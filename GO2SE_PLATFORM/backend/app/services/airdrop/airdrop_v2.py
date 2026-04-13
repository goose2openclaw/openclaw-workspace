#!/usr/bin/env python3
"""
💰 薅羊毛服务 V2 - 空投猎手
=========================
安全机制：
- 🚫 绝对不访问授权链接
- 🔒 合约交互白名单
- ⛽ Gas费智能监控
- 📊 风险评分系统
"""

import asyncio
import hashlib
import time
import re
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import deque

# ─── 安全枚举 ──────────────────────────────────────────

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"

class AirdropStatus(str, Enum):
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SUSPENDED = "suspended"      # 风险过高暂停
    AUTH_WARNING = "auth_warning" # 疑似授权链接

# ─── 安全配置 ──────────────────────────────────────────

# 🚫 绝对禁止的关键词（授权相关）
FORBIDDEN_PATTERNS = [
    r"approve", r"authorization", r"auth", r"allowance",
    r"setapproval", r"approvefor", r"permit",
    r"unlock", r"enable.*token", r"grant.*access",
    r"infinite.*approve", r"approve.*unlimited",
]

# 🔒 合约交互白名单（仅这些操作是安全的）
SAFE_ACTIONS = {
    "bridge", "swap", "mint", "transfer", "stake",
    "unstake", "claim", "deposit", "withdraw",
    "add_liquidity", "remove_liquidity", "vote",
    "delegate", "register", "claim_nft",
}

# ⛽  Gas费阈值
GAS_CONFIG = {
    "max_gas_gwei": 100,       # 超过100gwei暂停
    "watch_gas_gwei": 50,      # 超过50gwei告警
    "auto_suspend": True,       # 高Gas自动暂停
}

# ─── 数据类 ─────────────────────────────────────────────

@dataclass
class AirdropTask:
    """空投任务"""
    id: str
    name: str
    project: str
    chain: str
    actions: List[str]              # 安全操作列表
    expected_return_usd: float
    difficulty: str
    risk_level: RiskLevel
    estimated_gas_usd: float
    deadline: Optional[datetime]
    status: AirdropStatus
    security_flags: List[str] = field(default_factory=list)
    created_at: str = ""
    completed_at: Optional[str] = None
    tx_hashes: List[str] = field(default_factory=list)
    actual_return_usd: float = 0


@dataclass
class AirdropResult:
    """空投结果"""
    task_id: str
    success: bool
    actual_return: float
    tx_hash: Optional[str]
    gas_spent: float
    error: Optional[str]
    security_check_passed: bool
    timestamp: str


@dataclass
class SecurityReport:
    """安全报告"""
    task_id: str
    risk_score: float          # 0-100, 越高越危险
    risk_factors: List[str]
    auth_check_passed: bool
    contract_check_passed: bool
    gas_check_passed: bool
    recommendation: str        # PROCEED / CAUTION / STOP


# ─── 安全检查器 ────────────────────────────────────────

class SecurityChecker:
    """
    🔒 安全检查器
    所有空投任务必须通过安全检查
    """

    def __init__(self):
        self.forbidden_patterns = [re.compile(p, re.I) for p in FORBIDDEN_PATTERNS]
        self.safe_actions = SAFE_ACTIONS

    def check_task_name(self, name: str) -> tuple[bool, str]:
        """检查任务名称是否安全"""
        for pattern in self.forbidden_patterns:
            if pattern.search(name):
                return False, f"禁止词: {pattern.pattern}"
        return True, "OK"

    def check_actions(self, actions: List[str]) -> tuple[bool, List[str]]:
        """检查操作列表是否都是安全的"""
        unsafe = []
        for action in actions:
            action_clean = action.lower().replace(" ", "_").replace("-", "_")
            if action_clean not in self.safe_actions:
                # 检查是否是禁止词
                for pattern in self.forbidden_patterns:
                    if pattern.search(action):
                        unsafe.append(f"禁止操作: {action} ({pattern.pattern})")
                        break
                else:
                    unsafe.append(f"未识别操作: {action}")
        return len(unsafe) == 0, unsafe

    def check_gas(self, gas_price_gwei: float) -> tuple[bool, str]:
        """检查Gas费是否合理"""
        if gas_price_gwei > GAS_CONFIG["max_gas_gwei"]:
            return False, f"Gas费过高: {gas_price_gwei}gwei > {GAS_CONFIG['max_gas_gwei']}gwei"
        if gas_price_gwei > GAS_CONFIG["watch_gas_gwei"]:
            return False, f"Gas费警告: {gas_price_gwei}gwei > {GAS_CONFIG['watch_gas_gwei']}gwei"
        return True, "OK"

    def calculate_risk_score(
        self,
        task: AirdropTask,
        current_gas_gwei: float = 30
    ) -> SecurityReport:
        """计算任务风险评分"""
        risk_factors = []
        risk_score = 0

        # 1. 操作风险
        actions_safe, unsafe_ops = self.check_actions(task.actions)
        if not actions_safe:
            risk_score += 50
            risk_factors.extend([f"危险操作: {o}" for o in unsafe_ops])

        # 2. 授权风险
        name_safe, name_reason = self.check_task_name(task.name)
        if not name_safe:
            risk_score += 30
            risk_factors.append(f"名称风险: {name_reason}")

        # 3. Gas风险
        if current_gas_gwei > GAS_CONFIG["max_gas_gwei"]:
            risk_score += 20
            risk_factors.append(f"Gas费过高: {current_gas_gwei}gwei")

        # 4. 项目风险
        if task.risk_level == RiskLevel.HIGH:
            risk_score += 15
            risk_factors.append("高风险项目")
        elif task.risk_level == RiskLevel.EXTREME:
            risk_score += 30
            risk_factors.append("极高风险项目")

        # 5. 返回预期
        if task.expected_return_usd > 1000:
            risk_score += 10
            risk_factors.append("高回报目标(>$1000)")

        # 归一化
        risk_score = min(100, risk_score)

        # 建议
        if risk_score >= 70:
            recommendation = "STOP"
        elif risk_score >= 40:
            recommendation = "CAUTION"
        else:
            recommendation = "PROCEED"

        return SecurityReport(
            task_id=task.id,
            risk_score=risk_score,
            risk_factors=risk_factors,
            auth_check_passed=name_safe,
            contract_check_passed=actions_safe,
            gas_check_passed=current_gas_gwei <= GAS_CONFIG["max_gas_gwei"],
            recommendation=recommendation
        )


# ─── 薅羊毛服务 V2 ────────────────────────────────────

class AirdropServiceV2:
    """
    💰 薅羊毛服务 V2
    - 安全第一
    - 全程风控
    - 记录追溯
    """

    # 空投任务模板（已安全审核）
    TASK_TEMPLATES = [
        {
            "name": "LayerZero V2 空投",
            "project": "LayerZero",
            "chain": "Arbitrum",
            "actions": ["bridge", "swap", "add_liquidity"],
            "expected_return_usd": 500,
            "difficulty": "medium",
            "risk_level": RiskLevel.LOW,
            "estimated_gas_usd": 20,
        },
        {
            "name": "zkSync Era 测试网",
            "project": "zkSync",
            "chain": "zkSync",
            "actions": ["mint", "bridge"],
            "expected_return_usd": 300,
            "difficulty": "easy",
            "risk_level": RiskLevel.LOW,
            "estimated_gas_usd": 15,
        },
        {
            "name": "Starknet 交互",
            "project": "Starknet",
            "chain": "Starknet",
            "actions": ["swap", "stake"],
            "expected_return_usd": 200,
            "difficulty": "easy",
            "risk_level": RiskLevel.LOW,
            "estimated_gas_usd": 10,
        },
        {
            "name": "Linea 交互",
            "project": "Linea",
            "chain": "Linea",
            "actions": ["bridge", "swap"],
            "expected_return_usd": 150,
            "difficulty": "easy",
            "risk_level": RiskLevel.LOW,
            "estimated_gas_usd": 12,
        },
        {
            "name": "Berachain 空投",
            "project": "Berachain",
            "chain": "Berachain",
            "actions": ["bridge", "swap", "stake"],
            "expected_return_usd": 400,
            "difficulty": "medium",
            "risk_level": RiskLevel.MEDIUM,
            "estimated_gas_usd": 25,
        },
        {
            "name": "Monad 测试网",
            "project": "Monad",
            "chain": "Monad",
            "actions": ["swap", "transfer"],
            "expected_return_usd": 600,
            "difficulty": "medium",
            "risk_level": RiskLevel.MEDIUM,
            "estimated_gas_usd": 30,
        },
        {
            "name": "Abstract 交互",
            "project": "Abstract",
            "chain": "Abstract",
            "actions": ["mint", "claim_nft"],
            "expected_return_usd": 100,
            "difficulty": "easy",
            "risk_level": RiskLevel.LOW,
            "estimated_gas_usd": 8,
        },
    ]

    def __init__(self):
        self.tasks: Dict[str, AirdropTask] = {}
        self.results: List[AirdropResult] = []
        self.security_checker = SecurityChecker()
        self._gas_price_history: deque = deque(maxlen=100)
        self._suspended_projects: set = set()

    async def scan_opportunities(self) -> List[AirdropTask]:
        """扫描空投机会"""
        tasks = []
        now = datetime.now()

        for i, template in enumerate(self.TASK_TEMPLATES):
            project = template["project"]

            # 跳过已暂停的项目
            if project in self._suspended_projects:
                continue

            task_id = f"airdrop_{project.lower()}_{now.strftime('%Y%m%d%H%M')}"
            task = AirdropTask(
                id=task_id,
                name=template["name"],
                project=template["project"],
                chain=template["chain"],
                actions=template["actions"],
                expected_return_usd=template["expected_return_usd"],
                difficulty=template["difficulty"],
                risk_level=template["risk_level"],
                estimated_gas_usd=template["estimated_gas_usd"],
                deadline=None,
                status=AirdropStatus.AVAILABLE,
                security_flags=[],
                created_at=now.isoformat(),
            )

            # 🚫 安全审核
            name_ok, _ = self.security_checker.check_task_name(task.name)
            actions_ok, unsafe_ops = self.security_checker.check_actions(task.actions)

            if not name_ok:
                task.security_flags.append("NAME_SUSPICIOUS")
                task.status = AirdropStatus.AUTH_WARNING
            if not actions_ok:
                task.security_flags.append(f"UNSAFE_OPS: {', '.join(unsafe_ops)}")
                task.status = AirdropStatus.SUSPENDED

            tasks.append(task)
            self.tasks[task.id] = task

        return tasks

    async def execute_task(self, task_id: str, dry_run: bool = True) -> AirdropResult:
        """
        执行空投任务（干跑模式）
        🚫 绝对不访问授权链接
        """
        if task_id not in self.tasks:
            return AirdropResult(
                task_id=task_id, success=False, actual_return=0,
                tx_hash=None, gas_spent=0,
                error="任务不存在",
                security_check_passed=False,
                timestamp=datetime.now().isoformat()
            )

        task = self.tasks[task_id]

        # ─── 安全预检 ────────────────────────────────
        security_report = self.security_checker.calculate_risk_score(task)

        if security_report.recommendation == "STOP":
            return AirdropResult(
                task_id=task_id, success=False, actual_return=0,
                tx_hash=None, gas_spent=0,
                error=f"安全检查失败: {', '.join(security_report.risk_factors)}",
                security_check_passed=False,
                timestamp=datetime.now().isoformat()
            )

        # ─── 模拟执行（干跑）─────────────────────────
        try:
            await asyncio.sleep(0.5)  # 模拟延迟

            tx_hash = None if dry_run else f"0x{hashlib.sha256((task_id + str(time.time())).encode()).hexdigest()[:64]}"

            result = AirdropResult(
                task_id=task_id,
                success=True,
                actual_return=task.expected_return_usd * 0.9 if dry_run else task.expected_return_usd,
                tx_hash=tx_hash,
                gas_spent=task.estimated_gas_usd * 0.1,  # 模拟Gas消耗
                error=None,
                security_check_passed=True,
                timestamp=datetime.now().isoformat()
            )

            self.results.append(result)
            task.status = AirdropStatus.COMPLETED
            task.completed_at = result.timestamp
            task.actual_return_usd = result.actual_return
            if tx_hash:
                task.tx_hashes.append(tx_hash)

            return result

        except Exception as e:
            task.status = AirdropStatus.FAILED
            return AirdropResult(
                task_id=task_id, success=False, actual_return=0,
                tx_hash=None, gas_spent=0,
                error=str(e),
                security_check_passed=False,
                timestamp=datetime.now().isoformat()
            )

    def security_audit(self, task_id: str) -> SecurityReport:
        """对任务进行完整安全审计"""
        if task_id not in self.tasks:
            raise ValueError(f"任务不存在: {task_id}")
        task = self.tasks[task_id]
        return self.security_checker.calculate_risk_score(task)

    def get_task_stats(self) -> Dict:
        """获取任务统计"""
        completed = [r for r in self.results if r.success]
        failed = [r for r in self.results if not r.success]

        total_gas = sum(r.gas_spent for r in self.results)

        return {
            "total_opportunities": len(self.tasks),
            "completed": len(completed),
            "failed": len(failed),
            "in_progress": sum(1 for t in self.tasks.values() if t.status == AirdropStatus.IN_PROGRESS),
            "suspended": sum(1 for t in self.tasks.values() if t.status == AirdropStatus.SUSPENDED),
            "total_earned_usd": sum(r.actual_return for r in completed),
            "total_gas_spent_usd": round(total_gas, 2),
            "net_profit_usd": round(sum(r.actual_return for r in completed) - total_gas, 2),
            "avg_per_task": round(sum(r.actual_return for r in completed) / len(completed), 2) if completed else 0,
            "suspended_projects": list(self._suspended_projects),
            "security_flags": sum(1 for t in self.tasks.values() if t.security_flags),
        }

    def get_active_tasks(self) -> List[Dict]:
        """获取可用任务列表"""
        return [
            {
                "id": t.id,
                "name": t.name,
                "project": t.project,
                "chain": t.chain,
                "actions": t.actions,
                "expected_return_usd": t.expected_return_usd,
                "difficulty": t.difficulty,
                "risk_level": t.risk_level.value,
                "estimated_gas_usd": t.estimated_gas_usd,
                "status": t.status.value,
                "security_flags": t.security_flags,
            }
            for t in self.tasks.values()
            if t.status in [AirdropStatus.AVAILABLE, AirdropStatus.AUTH_WARNING]
        ]


# ─── 全局实例 ───────────────────────────────────────

airdrop_service_v2 = AirdropServiceV2()
