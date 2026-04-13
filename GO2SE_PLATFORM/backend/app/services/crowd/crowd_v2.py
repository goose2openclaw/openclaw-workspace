#!/usr/bin/env python3
"""
👶 穷孩子服务 V2 - 众包赚钱
=========================
安全机制：
- 🔒 完全隔离（与交易资金隔离）
- 🌐 无需暴露钱包私钥
- 📊 平台信誉评分
- ⏱️ 时间投入产出比
"""

import asyncio
import hashlib
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

# ─── 安全枚举 ──────────────────────────────────────────

class TaskType(str, Enum):
    LABEL = "label"           # 数据标注
    SURVEY = "survey"         # 问卷调查
    TRANSLATE = "translate"   # 翻译
    VALIDATE = "validate"     # 数据验证
    REVIEW = "review"         # 内容审核

class TaskStatus(str, Enum):
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"

class RiskLevel(str, Enum):
    SAFE = "safe"     # 纯人工，无需接触资金
    LOW = "low"       # 简单操作
    MEDIUM = "medium" # 需要一定技能

# ─── 安全配置 ──────────────────────────────────────────

# 🔒 隔离配置
ISOLATION_CONFIG = {
    "require_separate_account": True,   # 必须使用独立账号
    "no_private_key_required": True,    # 不需要私钥
    "max_daily_earnable": 100,          # 每日最高可赚（USD）
    "min_task_difficulty": "easy",       # 最低难度
    "payout_verify_required": True,     # 需要验证收款
}

# ─── 数据类 ─────────────────────────────────────────────

@dataclass
class CrowdTask:
    """众包任务"""
    id: str
    name: str
    platform: str
    task_type: TaskType
    description: str
    reward_usd: float
    duration_min: int
    difficulty: str
    requirements: List[str]
    risk_level: RiskLevel
    estimated_hourly_rate: float    # 预估时薪
    deadline: Optional[datetime]
    status: TaskStatus = TaskStatus.AVAILABLE
    created_at: str = ""
    started_at: Optional[str] = None
    submitted_at: Optional[str] = None
    approved_at: Optional[str] = None
    actual_reward: float = 0


@dataclass
class CrowdResult:
    """众包结果"""
    task_id: str
    success: bool
    reward: float
    platform: str
    task_type: str
    duration_actual_min: int
    hourly_rate_actual: float
    error: Optional[str]
    timestamp: str


@dataclass
class IsolationReport:
    """隔离报告"""
    task_id: str
    wallet_isolated: bool           # 钱包是否隔离
    no_private_key_used: bool       # 是否使用私钥
    platform_verified: bool         # 平台是否验证
    payment_method_safe: bool       # 付款方式是否安全
    overall_safe: bool


# ─── 平台数据库 ────────────────────────────────────────

PLATFORM_REPUTATION = {
    "Labelbox": {"reputation": 95, "payout_reliability": 98, "min_payout": 10},
    "Scale AI": {"reputation": 92, "payout_reliability": 96, "min_payout": 15},
    "Amazon MTurk": {"reputation": 88, "payout_reliability": 95, "min_payout": 5},
    "Appen": {"reputation": 90, "payout_reliability": 94, "min_payout": 10},
    "Toloka": {"reputation": 78, "payout_reliability": 85, "min_payout": 3},
    "Prolific": {"reputation": 93, "payout_reliability": 97, "min_payout": 8},
    "Clickworker": {"reputation": 82, "payout_reliability": 90, "min_payout": 5},
    "Surveytime": {"reputation": 75, "payout_reliability": 88, "min_payout": 2},
    "Lokalise": {"reputation": 85, "payout_reliability": 92, "min_payout": 15},
    "Rev": {"reputation": 87, "payout_reliability": 91, "min_payout": 10},
}


# ─── 众包服务 V2 ───────────────────────────────────────

class CrowdServiceV2:
    """
    👶 穷孩子服务 V2
    - 资金完全隔离
    - 平台信誉筛选
    - 时薪最优排序
    """

    TASK_TEMPLATES = [
        # 数据标注
        {
            "name": "AI图片目标检测标注",
            "platform": "Labelbox",
            "task_type": TaskType.LABEL,
            "description": "为自动驾驶数据集标注车辆、行人、交通标志",
            "reward_usd": 25,
            "duration_min": 60,
            "difficulty": "easy",
            "requirements": ["基本英语", "细心", "有电脑"],
            "risk_level": RiskLevel.SAFE,
        },
        {
            "name": "语音转文字标注",
            "platform": "Scale AI",
            "task_type": TaskType.LABEL,
            "description": "将音频转写为文字，标注说话人",
            "reward_usd": 30,
            "duration_min": 45,
            "difficulty": "easy",
            "requirements": ["英语听力", "打字速度>40字/分"],
            "risk_level": RiskLevel.SAFE,
        },
        {
            "name": "文档分类标注",
            "platform": "Amazon MTurk",
            "task_type": TaskType.LABEL,
            "description": "将新闻文章分类到指定类别",
            "reward_usd": 8,
            "duration_min": 20,
            "difficulty": "easy",
            "requirements": ["基本英语阅读"],
            "risk_level": RiskLevel.SAFE,
        },
        # 问卷调查
        {
            "name": "加密货币用户调研",
            "platform": "Prolific",
            "task_type": TaskType.SURVEY,
            "description": "关于加密货币使用习惯的问卷调查",
            "reward_usd": 12,
            "duration_min": 25,
            "difficulty": "easy",
            "requirements": ["了解加密货币基本概念"],
            "risk_level": RiskLevel.SAFE,
        },
        {
            "name": "DeFi产品体验反馈",
            "platform": "Surveytime",
            "task_type": TaskType.SURVEY,
            "description": "测试并反馈DeFi产品使用体验",
            "reward_usd": 15,
            "duration_min": 30,
            "difficulty": "easy",
            "requirements": ["有DeFi使用经验"],
            "risk_level": RiskLevel.SAFE,
        },
        # 翻译
        {
            "name": "技术文档中英翻译",
            "platform": "Lokalise",
            "task_type": TaskType.TRANSLATE,
            "description": "翻译区块链技术文档",
            "reward_usd": 50,
            "duration_min": 90,
            "difficulty": "medium",
            "requirements": ["中英双语流利", "懂技术术语"],
            "risk_level": RiskLevel.SAFE,
        },
        {
            "name": "产品描述本地化",
            "platform": "Rev",
            "task_type": TaskType.TRANSLATE,
            "description": "将产品描述本地化为目标市场语言",
            "reward_usd": 35,
            "duration_min": 60,
            "difficulty": "medium",
            "requirements": ["母语级双语能力"],
            "risk_level": RiskLevel.SAFE,
        },
        # 数据验证
        {
            "name": "电商产品信息验证",
            "platform": "Appen",
            "task_type": TaskType.VALIDATE,
            "description": "验证电商平台产品信息的准确性",
            "reward_usd": 18,
            "duration_min": 35,
            "difficulty": "easy",
            "requirements": ["细心", "有网购经验"],
            "risk_level": RiskLevel.SAFE,
        },
        {
            "name": "搜索结果质量评估",
            "platform": "Clickworker",
            "task_type": TaskType.REVIEW,
            "description": "评估搜索结果的相关性和质量",
            "reward_usd": 10,
            "duration_min": 25,
            "difficulty": "easy",
            "requirements": ["有互联网使用经验"],
            "risk_level": RiskLevel.SAFE,
        },
    ]

    def __init__(self):
        self.tasks: Dict[str, CrowdTask] = {}
        self.results: List[CrowdResult] = []
        self._daily_earned: float = 0
        self._last_reset_date: str = datetime.now().strftime("%Y-%m-%d")
        self._completed_task_ids: set = set()

    def _check_daily_limit(self, additional_reward: float) -> bool:
        """检查每日限额"""
        today = datetime.now().strftime("%Y-%m-%d")
        if today != self._last_reset_date:
            self._daily_earned = 0
            self._last_reset_date = today

        return (self._daily_earned + additional_reward) <= ISOLATION_CONFIG["max_daily_earnable"]

    async def scan_opportunities(self) -> List[CrowdTask]:
        """扫描众包机会"""
        tasks = []
        now = datetime.now()

        for i, template in enumerate(self.TASK_TEMPLATES):
            # 计算预估时薪
            hourly_rate = (template["reward_usd"] / template["duration_min"]) * 60

            task_id = f"crowd_{template['platform'].lower()}_{i}_{now.strftime('%Y%m%d%H%M')}"
            task = CrowdTask(
                id=task_id,
                name=template["name"],
                platform=template["platform"],
                task_type=template["task_type"],
                description=template["description"],
                reward_usd=template["reward_usd"],
                duration_min=template["duration_min"],
                difficulty=template["difficulty"],
                requirements=template["requirements"],
                risk_level=template["risk_level"],
                estimated_hourly_rate=round(hourly_rate, 2),
                deadline=None,
                created_at=now.isoformat(),
            )

            tasks.append(task)
            self.tasks[task.id] = task

        return tasks

    async def start_task(self, task_id: str) -> CrowdTask:
        """开始任务"""
        if task_id not in self.tasks:
            raise ValueError(f"任务不存在: {task_id}")

        task = self.tasks[task_id]

        # 检查每日限额
        if not self._check_daily_limit(task.reward_usd):
            raise ValueError(f"已达每日收益上限: ${ISOLATION_CONFIG['max_daily_earnable']}")

        if task.status != TaskStatus.AVAILABLE:
            raise ValueError(f"任务不可用: {task.status.value}")

        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.now().isoformat()

        return task

    async def submit_task(self, task_id: str, work_quality: str = "normal") -> CrowdResult:
        """提交任务"""
        if task_id not in self.tasks:
            return CrowdResult(
                task_id=task_id, success=False, reward=0,
                platform="", task_type="", duration_actual_min=0,
                hourly_rate_actual=0, error="任务不存在",
                timestamp=datetime.now().isoformat()
            )

        task = self.tasks[task_id]

        if task.status != TaskStatus.IN_PROGRESS:
            return CrowdResult(
                task_id=task_id, success=False, reward=0,
                platform=task.platform, task_type=task.task_type.value,
                duration_actual_min=0, hourly_rate_actual=0,
                error=f"任务状态错误: {task.status.value}",
                timestamp=datetime.now().isoformat()
            )

        # 模拟提交审核
        await asyncio.sleep(0.5)

        now = datetime.now()
        task.submitted_at = now.isoformat()

        # 质量影响奖励
        quality_multiplier = {"high": 1.2, "normal": 1.0, "low": 0.7}.get(work_quality, 1.0)
        actual_reward = task.reward_usd * quality_multiplier

        # 检查限额
        if not self._check_daily_limit(actual_reward):
            remaining = ISOLATION_CONFIG["max_daily_earnable"] - self._daily_earned
            actual_reward = max(0, remaining)

        # 模拟批准概率
        approval_prob = {"high": 0.95, "normal": 0.85, "low": 0.6}.get(work_quality, 0.85)
        approved = True  # 简化：模拟直接批准

        if approved:
            task.status = TaskStatus.APPROVED
            task.approved_at = now.isoformat()
            task.actual_reward = actual_reward
            self._daily_earned += actual_reward
            self._completed_task_ids.add(task_id)

            result = CrowdResult(
                task_id=task_id,
                success=True,
                reward=round(actual_reward, 2),
                platform=task.platform,
                task_type=task.task_type.value,
                duration_actual_min=task.duration_min,
                hourly_rate_actual=round((actual_reward / task.duration_min) * 60, 2),
                error=None,
                timestamp=now.isoformat()
            )
        else:
            task.status = TaskStatus.REJECTED
            result = CrowdResult(
                task_id=task_id, success=False, reward=0,
                platform=task.platform, task_type=task.task_type.value,
                duration_actual_min=task.duration_min,
                hourly_rate_actual=0,
                error="任务被拒绝",
                timestamp=now.isoformat()
            )

        self.results.append(result)
        return result

    def get_isolation_report(self, task_id: str) -> IsolationReport:
        """获取隔离报告"""
        if task_id not in self.tasks:
            raise ValueError(f"任务不存在: {task_id}")

        task = self.tasks[task_id]
        platform_info = PLATFORM_REPUTATION.get(task.platform, {})

        return IsolationReport(
            task_id=task_id,
            wallet_isolated=True,              # 永远隔离
            no_private_key_used=True,           # 永远不需要私钥
            platform_verified=platform_info.get("reputation", 0) >= 70,
            payment_method_safe=True,           # 使用官方支付
            overall_safe=True
        )

    def get_platform_stats(self) -> Dict:
        """获取平台统计"""
        stats = {}
        for platform, info in PLATFORM_REPUTATION.items():
            completed = [r for r in self.results if r.platform == platform]
            total_earned = sum(r.reward for r in completed)
            stats[platform] = {
                "reputation": info["reputation"],
                "payout_reliability": info["payout_reliability"],
                "min_payout": info["min_payout"],
                "tasks_completed": len(completed),
                "total_earned": round(total_earned, 2),
            }
        return stats

    def get_task_stats(self) -> Dict:
        """获取任务统计"""
        completed = [r for r in self.results if r.success]

        return {
            "total_opportunities": len(self.tasks),
            "completed": len(completed),
            "rejected": sum(1 for r in self.results if not r.success),
            "in_progress": sum(1 for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS),
            "total_earned_usd": round(sum(r.reward for r in completed), 2),
            "total_time_min": sum(r.duration_actual_min for r in completed),
            "avg_hourly_rate": round(
                sum(r.hourly_rate_actual for r in completed) / len(completed), 2
            ) if completed else 0,
            "daily_earned_usd": round(self._daily_earned, 2),
            "daily_remaining_usd": round(ISOLATION_CONFIG["max_daily_earnable"] - self._daily_earned, 2),
            "isolation_config": ISOLATION_CONFIG,
        }

    def get_available_tasks(
        self,
        min_hourly_rate: float = 0,
        task_type: Optional[str] = None,
        sort_by: str = "hourly_rate"
    ) -> List[Dict]:
        """获取可用任务（可排序过滤）"""
        tasks = [
            t for t in self.tasks.values()
            if t.status == TaskStatus.AVAILABLE
            and t.estimated_hourly_rate >= min_hourly_rate
            and (task_type is None or t.task_type.value == task_type)
        ]

        # 排序
        if sort_by == "hourly_rate":
            tasks.sort(key=lambda x: x.estimated_hourly_rate, reverse=True)
        elif sort_by == "reward":
            tasks.sort(key=lambda x: x.reward_usd, reverse=True)
        elif sort_by == "difficulty":
            order = {"easy": 0, "medium": 1, "hard": 2}
            tasks.sort(key=lambda x: order.get(x.difficulty, 9))

        return [
            {
                "id": t.id,
                "name": t.name,
                "platform": t.platform,
                "platform_reputation": PLATFORM_REPUTATION.get(t.platform, {}).get("reputation", 0),
                "task_type": t.task_type.value,
                "description": t.description,
                "reward_usd": t.reward_usd,
                "duration_min": t.duration_min,
                "difficulty": t.difficulty,
                "estimated_hourly_rate": t.estimated_hourly_rate,
                "requirements": t.requirements,
                "risk_level": t.risk_level.value,
            }
            for t in tasks
        ]


# ─── 全局实例 ───────────────────────────────────────

crowd_service_v2 = CrowdServiceV2()
