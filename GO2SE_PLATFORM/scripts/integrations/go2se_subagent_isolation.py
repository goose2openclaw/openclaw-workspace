"""
GO2SE SubAgent Isolation Manager - 基于 Nano Claude Code Multi-Agent 模块
=======================================================================
解决 subagent resume 401 问题:
- git worktree 隔离: 每个子agent独立工作目录
- 深度追踪: max_depth 防止无限递归
- 消息传递: inbox queue 跨agent通信
- typed agents: coder/reviewer/researcher/tester
"""
from __future__ import annotations

import os
import uuid
import queue
import subprocess
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor, Future
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional, Any


# ── Agent 类型定义 ─────────────────────────────────────────────────────────

@dataclass
class AgentDefinition:
    name: str
    description: str = ""
    system_prompt: str = ""
    model: str = ""
    tools: list = field(default_factory=list)  # empty = all tools
    source: str = "built-in"


# ── 内置 Agent 类型 ────────────────────────────────────────────────────────

BUILTIN_AGENTS = {
    "coder": AgentDefinition(
        name="coder",
        description="专业编码Agent: 编写、阅读、修改代码",
        system_prompt="""你是专业编程助手。专注于:
- 编写简洁、符合规范的代码
- 阅读理解现有代码后再修改
- 最小化定向修改
- 不添加不必要的功能、注释或错误处理
""",
        source="built-in",
    ),
    "reviewer": AgentDefinition(
        name="reviewer",
        description="代码审查Agent: 质量、安全、正确性分析",
        system_prompt="""你是代码审查助手。分析:
- 正确性和逻辑错误
- 安全漏洞 (注入、XSS、认证绕过等)
- 性能问题
- 代码质量和可维护性
简洁具体。按 Critical | Warning | Suggestion 分类。
工具限制: Read, Glob, Grep
""",
        tools=["Read", "Glob", "Grep"],
        source="built-in",
    ),
    "researcher": AgentDefinition(
        name="researcher",
        description="研究Agent: 探索代码库、回答问题",
        system_prompt="""你是研究助手。专注于:
- 充分阅读分析代码后再回答
- 提供基于事实、有证据的答案
- 引用具体文件路径和行号
- 简洁专注
工具: Read, Glob, Grep, WebFetch, WebSearch
""",
        tools=["Read", "Glob", "Grep", "WebFetch", "WebSearch"],
        source="built-in",
    ),
    "tester": AgentDefinition(
        name="tester",
        description="测试Agent: 编写和运行测试",
        system_prompt="""你是测试专家。职责:
- 为给定代码编写全面测试
- 运行现有测试并诊断失败
- 专注边界条件和错误条件
- 保持测试简单、快速、可读
""",
        source="built-in",
    ),
    "general-purpose": AgentDefinition(
        name="general-purpose",
        description="通用Agent: 研究复杂问题、搜索代码、执行多步任务",
        system_prompt="",
        source="built-in",
    ),
}


# ── 子任务定义 ─────────────────────────────────────────────────────────────

@dataclass
class SubAgentTask:
    id: str
    prompt: str
    status: str = "pending"  # pending | running | completed | failed | cancelled
    result: Optional[str] = None
    depth: int = 0
    name: str = ""
    worktree_path: str = ""
    worktree_branch: str = ""
    _cancel_flag: bool = field(default=False, repr=False)
    _future: Optional[Future] = field(default=None, repr=False)
    _inbox: Any = field(default_factory=queue.Queue, repr=False)


# ── Worktree 工具函数 ─────────────────────────────────────────────────────

def _git_root(cwd: str) -> Optional[str]:
    """返回git根目录，不在git仓库中则返回None"""
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=cwd, capture_output=True, text=True, check=True,
        )
        return r.stdout.strip()
    except Exception:
        return None


def create_worktree(base_dir: str) -> tuple:
    """
    创建临时git worktree。
    返回: (worktree_path, branch_name)
    """
    branch = f"go2se-agent-{uuid.uuid4().hex[:8]}"
    wt_path = tempfile.mkdtemp(prefix="go2se-wt-")
    os.rmdir(wt_path)
    subprocess.run(
        ["git", "worktree", "add", "-b", branch, wt_path],
        cwd=base_dir, check=True, capture_output=True, text=True,
    )
    return wt_path, branch


def remove_worktree(wt_path: str, branch: str, base_dir: str) -> None:
    """删除git worktree和对应分支 (best-effort)"""
    try:
        subprocess.run(
            ["git", "worktree", "remove", "--force", wt_path],
            cwd=base_dir, capture_output=True,
        )
    except Exception:
        pass
    try:
        subprocess.run(
            ["git", "branch", "-D", branch],
            cwd=base_dir, capture_output=True,
        )
    except Exception:
        pass


# ── SubAgentManager ────────────────────────────────────────────────────────

class SubAgentManager:
    """
    子Agent管理器，使用线程池并发执行。
    
    关键特性:
    - worktree隔离: 每个子agent独立git分支
    - 深度限制: max_depth防止无限递归
    - typed agents: coder/reviewer/researcher/tester
    - 消息传递: inbox queue支持agent间通信
    - cancel支持: 可中断正在运行的agent
    """

    def __init__(self, max_concurrent: int = 5, max_depth: int = 5):
        self.tasks: dict = {}
        self._by_name: dict = {}
        self.max_concurrent = max_concurrent
        self.max_depth = max_depth
        self._pool = ThreadPoolExecutor(max_workers=max_concurrent)

    def spawn(
        self,
        prompt: str,
        config: dict,
        system_prompt: str,
        agent_executor: Callable,
        depth: int = 0,
        agent_type: str = "general-purpose",
        isolation: str = "worktree",  # "" | "worktree"
        name: str = "",
    ) -> SubAgentTask:
        """
        启动新的子agent任务。

        Args:
            prompt: 用户消息
            config: agent配置字典
            system_prompt: 基础系统提示词
            agent_executor: 执行agent的函数 (prompt, state, config, system_prompt) -> generator
            depth: 当前嵌套深度
            agent_type: "general-purpose" | "coder" | "reviewer" | "researcher" | "tester"
            isolation: "" 正常模式, "worktree" git隔离模式
            name: 可选的人类可读名称 (可通过SendMessage寻址)

        Returns:
            SubAgentTask 跟踪任务
        """
        task_id = uuid.uuid4().hex[:12]
        short_name = name or task_id[:8]
        task = SubAgentTask(id=task_id, prompt=prompt, depth=depth, name=short_name)
        self.tasks[task_id] = task
        if name:
            self._by_name[name] = task_id

        if depth >= self.max_depth:
            task.status = "failed"
            task.result = f"超出最大深度 ({self.max_depth})"
            return task

        # 获取agent定义
        agent_def = BUILTIN_AGENTS.get(agent_type, BUILTIN_AGENTS["general-purpose"])

        # 构建effective config和system prompt
        eff_config = dict(config)
        eff_system = system_prompt

        if agent_def.model:
            eff_config["model"] = agent_def.model
        if agent_def.system_prompt:
            eff_system = agent_def.system_prompt.rstrip() + "\n\n" + system_prompt

        # 处理worktree隔离
        worktree_path = ""
        worktree_branch = ""
        base_dir = os.getcwd()

        if isolation == "worktree":
            git_root = _git_root(base_dir)
            if not git_root:
                task.status = "failed"
                task.result = "isolation='worktree' 需要 git 仓库"
                return task
            try:
                worktree_path, worktree_branch = create_worktree(git_root)
                task.worktree_path = worktree_path
                task.worktree_branch = worktree_branch
                notice = (
                    f"\n\n[注意: 你在隔离的git worktree中: {worktree_path} "
                    f"(分支: {worktree_branch})。"
                    f"你的更改与主工作区 {git_root} 隔离。"
                    f"提交更改以便审核/合并。]"
                )
                prompt = prompt + notice
            except Exception as e:
                task.status = "failed"
                task.result = f"创建worktree失败: {e}"
                return task

        def _run():
            task.status = "running"
            old_cwd = os.getcwd()
            try:
                if worktree_path:
                    os.chdir(worktree_path)

                state = _AgentState()
                gen = agent_executor(
                    prompt, state, eff_config, eff_system,
                    depth=depth + 1,
                    cancel_check=lambda: task._cancel_flag,
                )
                for _event in gen:
                    if task._cancel_flag:
                        break

                if task._cancel_flag:
                    task.status = "cancelled"
                    task.result = None
                else:
                    task.result = _extract_final_text(state.messages)
                    task.status = "completed"

                # 处理通过SendMessage发送的消息
                while not task._inbox.empty() and not task._cancel_flag:
                    inbox_msg = task._inbox.get_nowait()
                    task.status = "running"
                    gen2 = agent_executor(
                        inbox_msg, state, eff_config, eff_system,
                        depth=depth + 1,
                        cancel_check=lambda: task._cancel_flag,
                    )
                    for _ev in gen2:
                        if task._cancel_flag:
                            break
                    if not task._cancel_flag:
                        task.result = _extract_final_text(state.messages)
                        task.status = "completed"

            except Exception as e:
                task.status = "failed"
                task.result = f"Error: {e}"
            finally:
                if worktree_path:
                    os.chdir(old_cwd)
                    remove_worktree(worktree_path, worktree_branch, old_cwd)

        task._future = self._pool.submit(_run)
        return task

    def wait(self, task_id: str, timeout: float = None) -> Optional[SubAgentTask]:
        """阻塞直到任务完成或超时"""
        task = self.tasks.get(task_id)
        if task is None:
            return None
        if task._future is not None:
            try:
                task._future.result(timeout=timeout)
            except Exception:
                pass
        return task

    def get_result(self, task_id: str) -> Optional[str]:
        """返回已完成任务的结果字符串"""
        task = self.tasks.get(task_id)
        return task.result if task else None

    def list_tasks(self) -> list:
        """返回所有跟踪的任务"""
        return list(self.tasks.values())

    def send_message(self, task_id_or_name: str, message: str) -> bool:
        """
        向运行中的后台agent发送消息。
        消息进入队列，agent完成当前工作后处理。
        """
        task_id = self._by_name.get(task_id_or_name, task_id_or_name)
        task = self.tasks.get(task_id)
        if task is None:
            return False
        if task.status not in ("running", "pending"):
            return False
        task._inbox.put(message)
        return True

    def cancel(self, task_id: str) -> bool:
        """请求取消正在运行的任务"""
        task = self.tasks.get(task_id)
        if task is None:
            return False
        if task.status == "running":
            task._cancel_flag = True
            return True
        return False

    def shutdown(self) -> None:
        """取消所有运行中的任务并关闭线程池"""
        for task in self.tasks.values():
            if task.status == "running":
                task._cancel_flag = True
        self._pool.shutdown(wait=True)


# ── 最小AgentState ────────────────────────────────────────────────────────

class _AgentState:
    """最小化的AgentState，用于subagent追踪"""
    def __init__(self):
        self.messages = []


def _extract_final_text(messages) -> str:
    """从消息列表中提取最后的assistant content"""
    for msg in reversed(messages):
        if msg.get("role") == "assistant" and msg.get("content"):
            return msg["content"]
    return ""


# ── 使用示例 ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("GO2SE SubAgent Isolation Manager")
    print("=" * 40)
    print(f"内置Agent类型: {list(BUILTIN_AGENTS.keys())}")
    print(f"最大并发: 5, 最大深度: 5")
    print(f"隔离模式: worktree (git)")
    print("\n解决的问题:")
    print("  1. subagent resume 401 → worktree隔离避免session冲突")
    print("  2. Context溢出 → 深度限制 + 消息截断")
    print("  3. Agent通信 → inbox queue消息传递")
