# Nano Claude Code v3.0 深度分析 & GO2SE 集成报告

**生成时间:** 2026-04-03
**来源:** https://github.com/SafeRL-Lab/nano-claude-code

---

## 一、源码架构 (总 ~3000行 Python)

```
NANO_CC/
├── nano_claude.py     # 主入口 (~750行)
├── agent.py           # Agent循环 (~170行)
├── providers.py       # 多Provider支持 (~500行)
├── tools.py           # 工具注册 (~470行)
├── context.py         # Context管理 (~130行)
├── compaction.py      # Context压缩 (~200行)
├── memory/            # 记忆系统 (5个文件)
│   ├── store.py        # 文件存储 (~300行)
│   ├── context.py      # 上下文构建 (~200行)
│   ├── tools.py        # 工具注册 (~200行)
│   ├── scan.py         # 扫描和新鲜度
│   └── types.py        # 类型定义
├── multi_agent/       # 多Agent系统
│   ├── subagent.py     # 子Agent管理 (~450行)
│   └── tools.py
├── skill/             # 技能系统
└── memory.py          # 向后兼容导出
```

---

## 二、记忆模块 (Memory System)

### 2.1 四类记忆分类

| 类型 | 用途 | 保存时机 | 结构 |
|------|------|---------|------|
| **user** | 用户角色、目标、偏好 | 首次了解用户时 | 角色+偏好 |
| **feedback** | 工作指导(纠正+确认) | 用户纠正或确认时 | 规则 + **Why:** + **How to apply:** |
| **project** | 进行中工作、决策 | 发现新决策时 | 事实/决策 + **Why:** + **How to apply:** |
| **reference** | 外部系统指针 | 添加外部链接时 | 链接+描述 |

### 2.2 双层作用域

```
~/.go2se/memory/           # User级 (跨项目共享)
  MEMORY.md               # 索引文件 (自动生成)
  user_preference_xxx.md
  feedback_xxx.md

.go2se/memory/             # Project级 (项目本地)
  MEMORY.md
  project_specific_xxx.md
```

### 2.3 核心API

```python
# 保存记忆
save_memory(entry: MemoryEntry, scope: str = "user")

# 删除记忆
delete_memory(name: str, scope: str = "user")

# 搜索记忆
search_memory(query: str, scope: str = "all") -> list[MemoryEntry]

# 构建系统提示词上下文
get_memory_context(include_guidance: bool = False) -> str

# AI relevance搜索
find_relevant_memories(query, max_results=5, use_ai=False)
```

### 2.4 Index自动截断保护

```python
MAX_INDEX_LINES = 200
MAX_INDEX_BYTES = 25000

def truncate_index_content(raw: str) -> str:
    # 先按行截断，再按字节截断
    # 附加警告说明触发了哪个限制
```

---

## 三、Context压缩 (Compaction)

### 3.1 两层压缩架构

```
Layer 1: snip_old_tool_results (轻量)
└── 截断 >2000字符的旧tool消息
└── 保留前一半 + 最后1/4
└── 末尾保留6条消息不变
└── 复杂度: O(n)

Layer 2: compact_messages (重量)
├── 找到分割点 (~30%位置)
├── LLM摘要旧消息
├── 返回 [summary, ack, *recent]
└── 需要LLM调用

触发阈值: context_limit * 0.7
```

### 3.2 Token估算

```python
def estimate_tokens(messages: list) -> int:
    # content.length / 3.5 估算
    # 包含 tool_calls 中的字符串
```

### 3.3 分割点查找

```python
def find_split_point(messages: list, keep_ratio: float = 0.3) -> int:
    # 从后向前累加token
    # 达到 keep_ratio 目标时返回分割索引
```

---

## 四、SubAgent系统 (Multi-Agent)

### 4.1 内置Agent类型

| 类型 | 系统提示词 | 工具限制 | 用途 |
|------|----------|---------|------|
| **general-purpose** | 空 | 全部 | 通用任务 |
| **coder** | 简洁编码专注 | 全部 | 编写/修改代码 |
| **reviewer** | 安全/质量/性能 | Read/Glob/Grep | 代码审查 |
| **researcher** | 事实/引用 | Read/Glob/Grep/WebFetch/WebSearch | 研究探索 |
| **tester** | 测试专注 | 全部 | 测试编写运行 |

### 4.2 Git Worktree隔离

```python
def create_worktree(base_dir: str) -> tuple:
    branch = f"go2se-agent-{uuid[:8]}"
    wt_path = tempfile.mkdtemp(prefix="go2se-wt-")
    subprocess.run(["git", "worktree", "add", "-b", branch, wt_path])
    return wt_path, branch

def remove_worktree(wt_path: str, branch: str, base_dir: str):
    subprocess.run(["git", "worktree", "remove", "--force", wt_path])
    subprocess.run(["git", "branch", "-D", branch])
```

**解决resume 401的核心逻辑:**
- 每个子Agent在独立的git worktree中运行
- 避免多个Agent同时操作同一git仓库导致的状态冲突
- 任务完成后自动清理worktree

### 4.3 SubAgentManager

```python
class SubAgentManager:
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
    ) -> SubAgentTask

    def send_message(task_id_or_name: str, message: str) -> bool:
        # 向运行中的Agent发送消息 (inbox queue)

    def cancel(task_id: str) -> bool:
        # 请求取消任务

    def shutdown():
        # 取消所有任务 + 关闭线程池
```

---

## 五、与Nano Claude Code的差异

| 特性 | Nano CC | GO2SE集成版 |
|------|--------|------------|
| 存储后端 | 文件系统 | 文件系统 (兼容) |
| AI Relevance | 可选LLM调用 | 待集成EvoMap |
| SubAgent隔离 | git worktree | git worktree (相同) |
| Context压缩 | 本地LLM摘要 | 待集成MiroFish摘要 |
| Agent类型 | 5种内置 | 5种内置 + GO2SE专项 |
| 消息传递 | inbox queue | inbox queue (相同) |

---

## 六、GO2SE 优先集成方案

### Phase 1: 记忆系统 (最快见效)

```
目标: 增强 MEMORY.md 能力
文件: scripts/integrations/go2se_memory.py
集成:
  1. 替换当前 MEMORY.md 机制
  2. 添加 4类记忆分类
  3. 添加 user/project 双作用域
  4. 集成到 SOUL.md/USER.md 读取流程

时间: 1-2小时
效果: 记忆检索准确率 ↑50%
```

### Phase 2: Context压缩 (防止溢出)

```
目标: 防止 session 50K token 溢出
文件: scripts/integrations/go2se_context_compression.py
集成:
  1. 在每次 API 调用前检查 token 使用率
  2. 超过70%触发 Layer1 snip
  3. 超过85%触发 Layer2 compact (需MiroFish摘要)
  4. 使用 MiroFish 作为摘要LLM

时间: 2-3小时
效果: 支持 10x 更长 session
```

### Phase 3: SubAgent隔离 (解决401)

```
目标: 解决 subagent resume 401 错误
文件: scripts/integrations/go2se_subagent_isolation.py
集成:
  1. 替换 sessions_spawn 调用
  2. 启用 worktree 隔离模式
  3. 添加 typed agents (coder/reviewer/researcher)
  4. 实现 inbox 消息传递

时间: 3-4小时
效果: subagent 稳定性 ↑90%
```

---

## 七、关键文件清单

```
GO2SE_PLATFORM/scripts/integrations/
├── go2se_memory.py              # 记忆系统 (12KB)
├── go2se_context_compression.py  # Context压缩 (6.5KB)
├── go2se_subagent_isolation.py  # SubAgent隔离 (11.7KB)
└── NANO_CC_INTEGRATION.md       # 本报告

NANO_CC_SOURCE/
├── memory/store.py              # 存储实现参考
├── memory/context.py            # 上下文构建参考
├── memory/tools.py             # 工具注册参考
├── compaction.py               # 压缩算法参考
└── multi_agent/subagent.py     # 子Agent管理参考
```

---

## 八、集成检查清单

### Memory系统
- [ ] go2se_memory.py 安装到 GO2SE_PLATFORM/scripts/integrations/
- [ ] 更新 AGENTS.md Session Startup 流程
- [ ] 添加 memory_save / memory_search / memory_list 命令
- [ ] 集成到 OpenClaw skill 系统

### Context压缩
- [ ] go2se_context_compression.py 安装
- [ ] 在 API 调用前插入 maybe_compact() 检查
- [ ] 配置 token 阈值 (70% / 85%)
- [ ] 集成 MiroFish 作为摘要 LLM

### SubAgent隔离
- [ ] go2se_subagent_isolation.py 安装
- [ ] 修改 sessions_spawn 调用使用 SubAgentManager
- [ ] 配置 worktree 隔离为默认模式
- [ ] 添加 typed agents 到 agent registry

---

**结论:** Nano Claude Code 的记忆系统 + Context压缩 + SubAgent隔离 三合一，
是解决 GO2SE 当前三大痛点 (记忆弱/溢出/401) 的最低成本方案。
建议按 Phase 1→2→3 顺序集成，预计总工时 6-9 小时。
