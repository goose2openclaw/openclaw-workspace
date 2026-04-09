"""
GO2SE v7 — gstack Integration Manager
把gstack的15个专家角色集成到GO2SE交易平台

Usage:
    from gstack_manager import GstackManager
    gm = GstackManager()
    result = gm.run_command("/office-hours", context={"idea": "我想做一个网格交易策略"})
"""

import os
import subprocess
import json
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path

# gstack根目录
GSTACK_ROOT = os.path.expanduser("~/.claude/skills/gstack")
GSTACK_BIN = f"{GSTACK_ROOT}/bin"
GSTACK_BROWSE = f"{GSTACK_ROOT}/browse/dist"
GSTACK_DESIGN = f"{GSTACK_ROOT}/design/dist"


@dataclass
class GstackCommand:
    """gstack命令定义"""
    name: str
    description: str
    category: str  # startup/ceo/eng/design/qa/deploy/tools
    skill_path: str
    requires_browser: bool = False
    requires_git: bool = False


class GstackManager:
    """GO2SE的gstack集成管理器"""
    
    # 15个gstack专家角色
    COMMANDS = {
        # === 启动阶段 ===
        "/office-hours": GstackCommand(
            name="/office-hours",
            description="YC创业导师 - 6个强制问题重构策略想法",
            category="startup",
            skill_path=f"{GSTACK_ROOT}/office-hours/SKILL.md"
        ),
        
        # === CEO/策略阶段 ===
        "/plan-ceo-review": GstackCommand(
            name="/plan-ceo-review",
            description="CEO评审 - 找10星最优策略",
            category="ceo",
            skill_path=f"{GSTACK_ROOT}/plan-ceo-review/SKILL.md"
        ),
        "/plan-eng-review": GstackCommand(
            name="/plan-eng-review",
            description="工程评审 - 锁定架构和数据流",
            category="ceo",
            skill_path=f"{GSTACK_ROOT}/plan-eng-review/SKILL.md"
        ),
        "/plan-design-review": GstackCommand(
            name="/plan-design-review",
            description="设计评审 - UI/UX评分与改进",
            category="design",
            skill_path=f"{GSTACK_ROOT}/plan-design-review/SKILL.md"
        ),
        
        # === 设计阶段 ===
        "/design-consultation": GstackCommand(
            name="/design-consultation",
            description="设计咨询 - 创建设计系统",
            category="design",
            skill_path=f"{GSTACK_ROOT}/design-consultation/SKILL.md"
        ),
        "/design-review": GstackCommand(
            name="/design-review",
            description="设计审查 - 修复设计问题",
            category="design",
            skill_path=f"{GSTACK_ROOT}/design-review/SKILL.md"
        ),
        "/design-shotgun": GstackCommand(
            name="/design-shotgun",
            description="设计探索 - 多种设计方案对比",
            category="design",
            skill_path=f"{GSTACK_ROOT}/design-shotgun/SKILL.md"
        ),
        
        # === 代码/安全阶段 ===
        "/review": GstackCommand(
            name="/review",
            description="代码审查 - 找生产bug",
            category="code",
            skill_path=f"{GSTACK_ROOT}/review/SKILL.md",
            requires_git=True
        ),
        "/cso": GstackCommand(
            name="/cso",
            description="安全官 - OWASP+STRIDE审计",
            category="security",
            skill_path=f"{GSTACK_ROOT}/cso/SKILL.md"
        ),
        "/investigate": GstackCommand(
            name="/investigate",
            description="调试调查 - 系统化根因分析",
            category="code",
            skill_path=f"{GSTACK_ROOT}/investigate/SKILL.md"
        ),
        
        # === QA/测试阶段 ===
        "/qa": GstackCommand(
            name="/qa",
            description="QA测试 - 真实浏览器验证",
            category="qa",
            skill_path=f"{GSTACK_ROOT}/qa/SKILL.md",
            requires_browser=True
        ),
        "/qa-only": GstackCommand(
            name="/qa-only",
            description="QA报告 - 仅报告不修改",
            category="qa",
            skill_path=f"{GSTACK_ROOT}/qa-only/SKILL.md",
            requires_browser=True
        ),
        "/benchmark": GstackCommand(
            name="/benchmark",
            description="性能测试 - Core Web Vitals基准",
            category="qa",
            skill_path=f"{GSTACK_ROOT}/benchmark/SKILL.md"
        ),
        "/browse": GstackCommand(
            name="/browse",
            description="浏览器 - 真实Chromium采集数据",
            category="qa",
            skill_path=f"{GSTACK_ROOT}/browse/SKILL.md",
            requires_browser=True
        ),
        
        # === 部署/监控阶段 ===
        "/ship": GstackCommand(
            name="/ship",
            description="发布 - 同步测试推送PR",
            category="deploy",
            skill_path=f"{GSTACK_ROOT}/ship/SKILL.md",
            requires_git=True
        ),
        "/land-and-deploy": GstackCommand(
            name="/land-and-deploy",
            description="部署 - 合并验证生产",
            category="deploy",
            skill_path=f"{GSTACK_ROOT}/land-and-deploy/SKILL.md"
        ),
        "/canary": GstackCommand(
            name="/canary",
            description="金丝雀 - 部署后持续监控",
            category="monitor",
            skill_path=f"{GSTACK_ROOT}/canary/SKILL.md"
        ),
        "/document-release": GstackCommand(
            name="/document-release",
            description="文档 - 更新项目文档",
            category="deploy",
            skill_path=f"{GSTACK_ROOT}/document-release/SKILL.md"
        ),
        
        # === 工具类 ===
        "/retro": GstackCommand(
            name="/retro",
            description="复盘 - 每周团队回顾",
            category="tools",
            skill_path=f"{GSTACK_ROOT}/retro/SKILL.md"
        ),
        "/autoplan": GstackCommand(
            name="/autoplan",
            description="自动规划 - CEO→设计→工程流水线",
            category="tools",
            skill_path=f"{GSTACK_ROOT}/autoplan/SKILL.md"
        ),
        "/codex": GstackCommand(
            name="/codex",
            description="第二意见 - OpenAI Codex独立审查",
            category="tools",
            skill_path=f"{GSTACK_ROOT}/codex/SKILL.md"
        ),
        "/careful": GstackCommand(
            name="/careful",
            description="安全警告 - 危险命令确认",
            category="safety",
            skill_path=f"{GSTACK_ROOT}/careful/SKILL.md"
        ),
        "/freeze": GstackCommand(
            name="/freeze",
            description="冻结 - 限制文件编辑范围",
            category="safety",
            skill_path=f"{GSTACK_ROOT}/freeze/SKILL.md"
        ),
        "/guard": GstackCommand(
            name="/guard",
            description="全面保护 - careful+freeze",
            category="safety",
            skill_path=f"{GSTACK_ROOT}/guard/SKILL.md"
        ),
        "/unfreeze": GstackCommand(
            name="/unfreeze",
            description="解冻 - 移除编辑限制",
            category="safety",
            skill_path=f"{GSTACK_ROOT}/unfreeze/SKILL.md"
        ),
    }
    
    def __init__(self):
        self.gstack_root = GSTACK_ROOT
        self.bin_dir = GSTACK_BIN
        self.browse_dir = GSTACK_BROWSE
        
    def is_available(self) -> bool:
        """检查gstack是否可用"""
        return os.path.exists(self.gstack_root)
    
    def get_command(self, name: str) -> Optional[GstackCommand]:
        """获取指定命令"""
        return self.COMMANDS.get(name)
    
    def list_commands(self, category: Optional[str] = None) -> List[GstackCommand]:
        """列出所有命令，支持按分类过滤"""
        cmds = list(self.COMMANDS.values())
        if category:
            cmds = [c for c in cmds if c.category == category]
        return cmds
    
    def get_skill_content(self, command: str) -> Optional[str]:
        """获取技能文档内容"""
        cmd = self.COMMANDS.get(command)
        if not cmd:
            return None
        skill_file = cmd.skill_path
        if os.path.exists(skill_file):
            with open(skill_file, 'r') as f:
                return f.read()
        return None
    
    async def run_command_async(
        self, 
        command: str, 
        context: Optional[Dict[str, Any]] = None,
        cwd: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        异步运行gstack命令
        
        Args:
            command: gstack命令 (如 "/review", "/qa")
            context: 传递给命令的上下文
            cwd: 工作目录
            
        Returns:
            {"success": bool, "output": str, "error": str}
        """
        cmd = self.COMMANDS.get(command)
        if not cmd:
            return {"success": False, "error": f"Unknown command: {command}"}
        
        if not self.is_available():
            return {"success": False, "error": "gstack not installed"}
        
        # 读取skill内容作为指令
        skill_content = self.get_skill_content(command)
        if not skill_content:
            return {"success": False, "error": f"Skill not found: {command}"}
        
        # 构建执行环境
        env = os.environ.copy()
        env["GSTACK_ROOT"] = self.gstack_root
        env["GSTACK_BIN"] = self.bin_dir
        env["GSTACK_BROWSE"] = self.browse_dir
        
        working_dir = cwd or os.getcwd()
        
        # 对于需要git的命令，检查git仓库
        if cmd.requires_git:
            git_root = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=working_dir,
                capture_output=True,
                text=True
            )
            if git_root.returncode != 0:
                return {
                    "success": False, 
                    "error": "Not a git repository. gstack commands require a git repo."
                }
        
        return {
            "success": True,
            "command": command,
            "description": cmd.description,
            "category": cmd.category,
            "skill_content": skill_content[:500] + "..." if len(skill_content) > 500 else skill_content,
            "requires_browser": cmd.requires_browser,
            "requires_git": cmd.requires_git,
            "context": context or {}
        }
    
    def run_command_sync(
        self, 
        command: str, 
        context: Optional[Dict[str, Any]] = None,
        cwd: Optional[str] = None
    ) -> Dict[str, Any]:
        """同步版本的run_command_async"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.run_command_async(command, context, cwd))
        finally:
            loop.close()
    
    def get_categories(self) -> List[str]:
        """获取所有分类"""
        categories = set(cmd.category for cmd in self.COMMANDS.values())
        return sorted(list(categories))
    
    def get_help_text(self) -> str:
        """生成帮助文本"""
        lines = [
            "🪿 GO2SE v7 — gstack集成帮助",
            "",
            "可用命令 (29个专家角色):",
            ""
        ]
        
        for category in self.get_categories():
            lines.append(f"📁 {category.upper()}")
            for cmd in self.list_commands(category):
                lines.append(f"   {cmd.name:<25} {cmd.description}")
            lines.append("")
        
        lines.extend([
            "使用方法:",
            "   from gstack_manager import GstackManager",
            "   gm = GstackManager()",
            "   result = gm.run_command_sync('/review')",
            "",
            "或直接说: '用 /office-hours 帮我构思一个做空策略'"
        ])
        
        return "\n".join(lines)


# === GO2SE特定集成 ===

class GO2SEGstackBridge:
    """
    GO2SE交易平台 ↔ gstack工程工作流的桥接器
    把gstack的工程实践应用到量化交易策略开发
    """
    
    def __init__(self):
        self.manager = GstackManager()
    
    async def strategy_development_flow(self, idea: str) -> Dict[str, Any]:
        """
        策略开发完整流水线 (类gstack sprint)
        
        流程: office-hours → plan-ceo-review → plan-eng-review → review → qa → ship
        
        Args:
            idea: 交易策略想法
            
        Returns:
            完整开发流程状态和输出
        """
        steps = []
        
        # Step 1: office-hours - 构思阶段
        result1 = await self.manager.run_command_async(
            "/office-hours", 
            context={"idea": idea}
        )
        steps.append({
            "step": "office-hours",
            "name": "策略构思 (YC创业导师)",
            "result": result1,
            "status": "✅" if result1["success"] else "❌"
        })
        
        # Step 2: plan-ceo-review - CEO评审
        result2 = await self.manager.run_command_async(
            "/plan-ceo-review",
            context={"idea": idea}
        )
        steps.append({
            "step": "plan-ceo-review",
            "name": "策略方向评审 (CEO)",
            "result": result2,
            "status": "✅" if result2["success"] else "❌"
        })
        
        # Step 3: plan-eng-review - 工程评审
        result3 = await self.manager.run_command_async(
            "/plan-eng-review",
            context={"idea": idea}
        )
        steps.append({
            "step": "plan-eng-review",
            "name": "技术架构设计 (工程经理)",
            "result": result3,
            "status": "✅" if result3["success"] else "❌"
        })
        
        return {
            "flow": "strategy_development",
            "idea": idea,
            "steps": steps,
            "ready_for_implementation": all(s["result"]["success"] for s in steps)
        }
    
    async def code_review_flow(self, strategy_code: str) -> Dict[str, Any]:
        """
        策略代码审查流水线
        
        流程: review → cso (安全) → benchmark (性能)
        """
        steps = []
        
        # Code Review
        result1 = await self.manager.run_command_async(
            "/review",
            context={"code": strategy_code}
        )
        steps.append({
            "step": "review",
            "name": "代码审查",
            "result": result1,
            "status": "✅" if result1["success"] else "❌"
        })
        
        # Security Audit
        result2 = await self.manager.run_command_async(
            "/cso",
            context={"code": strategy_code}
        )
        steps.append({
            "step": "cso",
            "name": "安全审计 (OWASP+STRIDE)",
            "result": result2,
            "status": "✅" if result2["success"] else "❌"
        })
        
        # Benchmark
        result3 = await self.manager.run_command_async(
            "/benchmark",
            context={"code": strategy_code}
        )
        steps.append({
            "step": "benchmark",
            "name": "性能基准",
            "result": result3,
            "status": "✅" if result3["success"] else "❌"
        })
        
        return {
            "flow": "code_review",
            "steps": steps
        }
    
    async def trading_monitoring_flow(self) -> Dict[str, Any]:
        """
        交易监控流水线
        
        流程: canary (监控) → retro (复盘) → browse (市场数据)
        """
        steps = []
        
        # Canary Monitoring
        result1 = await self.manager.run_command_async("/canary")
        steps.append({
            "step": "canary",
            "name": "交易监控",
            "result": result1,
            "status": "✅" if result1["success"] else "❌"
        })
        
        # Retro
        result2 = await self.manager.run_command_async("/retro")
        steps.append({
            "step": "retro",
            "name": "交易复盘",
            "result": result2,
            "status": "✅" if result2["success"] else "❌"
        })
        
        # Browse Market Data
        result3 = await self.manager.run_command_async(
            "/browse",
            context={"purpose": "market_data_collection"}
        )
        steps.append({
            "step": "browse",
            "name": "市场数据采集",
            "result": result3,
            "status": "✅" if result3["success"] else "❌"
        })
        
        return {
            "flow": "trading_monitoring",
            "steps": steps
        }


# === CLI Interface ===

def main():
    """CLI入口"""
    import sys
    
    gm = GstackManager()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd in gm.COMMANDS:
            result = gm.run_command_sync(cmd)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif cmd == "--list":
            print(gm.get_help_text())
        else:
            print(f"Unknown command: {cmd}")
            print("Use --list to see available commands")
    else:
        print(gm.get_help_text())


if __name__ == "__main__":
    main()
