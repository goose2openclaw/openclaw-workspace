"""
Crowdsourcing - 众包赚钱策略库
==============================
穷孩子 - EvoMap/ClawJob/数据众包
"""
from __future__ import annotations
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import random


@dataclass
class Task:
    """任务"""
    task_id: str
    platform: str
    task_type: str  # social/data/creative/feedback
    reward: float
    time_required: float  # 小时
    difficulty: int  # 1-5
    skills_required: List[str]
    risk_level: str  # LOW / MEDIUM
    available: bool


@dataclass
class TaskSignal:
    """任务信号"""
    task: Task
    recommended_action: str  # ACCEPT / SKIP
    priority: int  # 1-5
    hourly_rate: float
    match_score: float


class CrowdsourcingStrategy:
    """
    众包赚钱策略库
    =================
    赚钱API不断扩展 + 动态任务组合
    """

    # 任务平台
    PLATFORMS = {
        "evomap": {
            "name": "EvoMap",
            "types": ["social", "data", "research"],
            "base_reward": 10,
            "time_estimate": 2,
        },
        "clawjob": {
            "name": "ClawJob",
            "types": ["micro", "creative", "data"],
            "base_reward": 5,
            "time_estimate": 1,
        },
        "toloka": {
            "name": "Toloka",
            "types": ["annotation", "verification", "classification"],
            "base_reward": 3,
            "time_estimate": 0.5,
        },
        "clickworker": {
            "name": "Clickworker",
            "types": ["surveys", "data", "testing"],
            "base_reward": 8,
            "time_estimate": 1,
        },
        "appen": {
            "name": "Appen",
            "types": ["AI_training", "annotation", "transcription"],
            "base_reward": 15,
            "time_estimate": 3,
        },
        "scale": {
            "name": "Scale AI",
            "types": ["annotation", "evaluation", "data"],
            "base_reward": 20,
            "time_estimate": 2,
        },
    }

    def __init__(self):
        self.min_hourly_rate = 5  # 最低时薪$5
        self.max_difficulty = 4   # 最难4星
        self.active_tasks: Dict[str, Task] = {}

    def scan_tasks(self) -> List[Task]:
        """扫描任务"""
        tasks = []

        for platform_id, platform in self.PLATFORMS.items():
            for task_type in platform["types"]:
                for i in range(random.randint(2, 6)):
                    task = Task(
                        task_id=f"{platform_id}_{task_type}_{i}",
                        platform=platform["name"],
                        task_type=task_type,
                        reward=platform["base_reward"] * random.uniform(0.5, 2.0),
                        time_required=platform["time_estimate"] * random.uniform(0.5, 1.5),
                        difficulty=random.randint(1, 5),
                        skills_required=self._get_skills_for_type(task_type),
                        risk_level="LOW",
                        available=True,
                    )
                    tasks.append(task)

        tasks.sort(key=lambda t: t.reward / max(t.time_required, 0.1), reverse=True)
        return tasks

    def _get_skills_for_type(self, task_type: str) -> List[str]:
        """获取任务类型所需技能"""
        skill_map = {
            "social": ["writing", "engagement", "analysis"],
            "data": ["python", "excel", "analysis"],
            "creative": ["design", "writing", "video"],
            "annotation": ["detail", "labeling", "AI"],
            "verification": ["critical", "attention", "detail"],
            "micro": ["quick", "simple", "repeat"],
            "surveys": ["opinion", "feedback", "survey"],
            "testing": ["usability", "bug", "feedback"],
            "transcription": ["typing", "listening", "accuracy"],
            "AI_training": ["prompting", "evaluation", "annotation"],
        }
        return skill_map.get(task_type, ["general"])

    def analyze_task(self, task: Task, available_skills: List[str] = None) -> TaskSignal:
        """分析任务"""
        if available_skills is None:
            available_skills = ["python", "writing", "analysis", "detail", "critical"]

        # 计算匹配度
        skill_match = len(set(task.skills_required) & set(available_skills)) / max(len(task.skills_required), 1)

        # 计算时薪
        hourly_rate = task.reward / max(task.time_required, 0.1)

        # 过滤
        if hourly_rate < self.min_hourly_rate:
            return TaskSignal(
                task=task,
                recommended_action="SKIP",
                priority=0,
                hourly_rate=hourly_rate,
                match_score=skill_match,
            )

        if task.difficulty > self.max_difficulty:
            return TaskSignal(
                task=task,
                recommended_action="SKIP",
                priority=0,
                hourly_rate=hourly_rate,
                match_score=skill_match,
            )

        # 优先级
        if hourly_rate > 20 and skill_match > 0.7:
            priority = 1
        elif hourly_rate > 10:
            priority = 2
        else:
            priority = 4

        return TaskSignal(
            task=task,
            recommended_action="ACCEPT",
            priority=priority,
            hourly_rate=hourly_rate,
            match_score=skill_match,
        )

    def execute_task(self, signal: TaskSignal) -> Dict[str, Any]:
        """执行任务"""
        if signal.recommended_action != "ACCEPT":
            return {"status": "skipped", "reason": "不满足条件"}

        net_profit = signal.task.reward * 0.9  # 10%平台费

        return {
            "status": "accepted",
            "task_id": signal.task.task_id,
            "platform": signal.task.platform,
            "task_type": signal.task.task_type,
            "reward": signal.task.reward,
            "hourly_rate": signal.hourly_rate,
            "time_required": signal.task.time_required,
            "net_profit": net_profit,
            "wallet": "中转钱包",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def optimize_task_portfolio(self, tasks: List[Task], target_weekly: float = 500) -> Dict[str, Any]:
        """优化任务组合"""
        signals = [self.analyze_task(t) for t in tasks]
        accepting = [s for s in signals if s.recommended_action == "ACCEPT"]

        # 按优先级和时薪排序
        accepting.sort(key=lambda s: (s.priority, -s.hourly_rate))

        # 选择能达标的任务
        selected = []
        total_earning = 0
        total_time = 0

        for signal in accepting:
            if total_earning >= target_weekly:
                break
            selected.append(signal)
            total_earning += signal.task.reward
            total_time += signal.task.time_required

        return {
            "target_weekly": target_weekly,
            "selected_count": len(selected),
            "estimated_earning": total_earning,
            "estimated_time": total_time,
            "average_hourly_rate": total_earning / max(total_time, 1),
            "tasks": [
                {
                    "task_id": s.task.task_id,
                    "platform": s.task.platform,
                    "reward": s.task.reward,
                    "hourly_rate": s.hourly_rate,
                }
                for s in selected
            ],
        }

    def get_strategy_db(self) -> Dict[str, Any]:
        """获取策略数据库"""
        return {
            "name": "穷孩子 - 众包赚钱策略",
            "version": "v9.0",
            "platforms": list(self.PLATFORMS.keys()),
            "parameters": {
                "min_hourly_rate": self.min_hourly_rate,
                "max_difficulty": self.max_difficulty,
            },
            "task_types": {
                "social": ["EvoMap社交任务", "内容创作"],
                "data": ["数据分析", "标注", "验证"],
                "creative": ["设计", "视频", "写作"],
                "micro": ["小任务", "问卷", "测试"],
            },
            "entry_rules": [
                "时薪 >= $5",
                "难度 <= 4星",
                "风险 == LOW",
                "技能匹配 > 0.5",
            ],
            "optimization": {
                "target_weekly": "$500",
                "max_daily_hours": 4,
                "skill_development": ["python", "AI", "design"],
            },
            "platform_fees": {
                "EvoMap": "5%",
                "ClawJob": "10%",
                "Toloka": "15%",
                "Clickworker": "10%",
                "Appen": "15%",
                "Scale AI": "10%",
            },
        }
