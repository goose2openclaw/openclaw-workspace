#!/usr/bin/env python3
"""
👶 穷孩子 V3 - 智能找单·选品·抢单
================================
找单：多平台实时聚合
选品：时薪+可靠性双排序
抢单：异步并发抢占
"""

import asyncio
import time
import random
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import deque

# ─── 枚举 ──────────────────────────────────────────────

class TaskType(str, Enum):
    LABEL = "label"
    SURVEY = "survey"
    TRANSLATE = "translate"
    VALIDATE = "validate"
    REVIEW = "review"
    TEST = "test"           # App测试
    DATA_ENTRY = "data_entry"  # 数据录入

class Platform(str, Enum):
    LABELBOX = "Labelbox"
    SCALE_AI = "Scale AI"
    MTURK = "Amazon MTurk"
    APPEN = "Appen"
    PROLIFIC = "Prolific"
    CLICKWORKER = "Clickworker"
    TOlOKA = "Toloka"
    USER_TESTING = "UserTesting"
    TESTFY = "Testfy"
    UBERU = "Uberu"

class TaskUrgency(str, Enum):
    HOT = "hot"       # 抢
    NORMAL = "normal"
    LOW = "low"

# ─── 评分 ──────────────────────────────────────────────

@dataclass
class CrowdTaskScore:
    """任务评分"""
    task_id: str
    total_score: float
    hourly_rate_score: float
    reliability_score: float
    speed_score: float
    availability_score: float
    priority: str
    factors: Dict[str, float]


class CrowdScanner:
    """
    🔍 智能找单扫描器
    多平台聚合 + 实时评分
    """

    # 扩展任务池
    TASK_POOL = [
        # 高时薪任务
        {
            "id": "ct_001", "name": "AI视频内容审核", "platform": Platform.SCALE_AI.value,
            "task_type": TaskType.REVIEW.value,
            "description": "审核AI生成视频内容的合规性",
            "reward_usd": 45, "duration_min": 40,
            "difficulty": "medium", "requirements": ["英语好", "细心"],
            "slots": 20, "taken": 8,
            "reliability": 96, "payout_speed": "fast",
            "avg_hourly_rate": 67.5,
            "urgency": TaskUrgency.HOT.value,
            "expire_at": datetime.now() + timedelta(hours=3),
        },
        {
            "id": "ct_002", "name": "自动驾驶3D点云标注", "platform": Platform.LABELBOX.value,
            "task_type": TaskType.LABEL.value,
            "description": "为自动驾驶数据集标注3D点云中的目标",
            "reward_usd": 60, "duration_min": 60,
            "difficulty": "medium", "requirements": ["有标注经验", "懂交通标志"],
            "slots": 15, "taken": 3,
            "reliability": 95, "payout_speed": "fast",
            "avg_hourly_rate": 60.0,
            "urgency": TaskUrgency.HOT.value,
            "expire_at": datetime.now() + timedelta(hours=6),
        },
        # 快速任务
        {
            "id": "ct_003", "name": "产品体验问卷", "platform": Platform.PROLIFIC.value,
            "task_type": TaskType.SURVEY.value,
            "description": "关于新产品用户体验的15分钟问卷",
            "reward_usd": 12, "duration_min": 15,
            "difficulty": "easy", "requirements": ["认真填写"],
            "slots": 50, "taken": 12,
            "reliability": 93, "payout_speed": "fast",
            "avg_hourly_rate": 48.0,
            "urgency": TaskUrgency.NORMAL.value,
            "expire_at": datetime.now() + timedelta(hours=12),
        },
        {
            "id": "ct_004", "name": "搜索结果相关性评估", "platform": Platform.CLICKWORKER.value,
            "task_type": TaskType.REVIEW.value,
            "description": "评估搜索结果与查询关键词的相关程度",
            "reward_usd": 8, "duration_min": 20,
            "difficulty": "easy", "requirements": ["有互联网经验"],
            "slots": 100, "taken": 34,
            "reliability": 82, "payout_speed": "normal",
            "avg_hourly_rate": 24.0,
            "urgency": TaskUrgency.NORMAL.value,
            "expire_at": datetime.now() + timedelta(days=1),
        },
        # 高可靠性
        {
            "id": "ct_005", "name": "医学文献翻译", "platform": Platform.LABELBOX.value,
            "task_type": TaskType.TRANSLATE.value,
            "description": "将医学文献从英文翻译成中文",
            "reward_usd": 120, "duration_min": 120,
            "difficulty": "hard", "requirements": ["医学背景", "专业翻译"],
            "slots": 10, "taken": 2,
            "reliability": 98, "payout_speed": "fast",
            "avg_hourly_rate": 60.0,
            "urgency": TaskUrgency.LOW.value,
            "expire_at": datetime.now() + timedelta(days=7),
        },
        # 新任务
        {
            "id": "ct_006", "name": "AI对话质量评估", "platform": Platform.SCALE_AI.value,
            "task_type": TaskType.REVIEW.value,
            "description": "评估AI助手回复的质量和有用性",
            "reward_usd": 25, "duration_min": 30,
            "difficulty": "easy", "requirements": ["逻辑思维", "表达清晰"],
            "slots": 80, "taken": 5,
            "reliability": 94, "payout_speed": "fast",
            "avg_hourly_rate": 50.0,
            "urgency": TaskUrgency.HOT.value,
            "expire_at": datetime.now() + timedelta(hours=8),
        },
        {
            "id": "ct_007", "name": "电商图片标注", "platform": Platform.MTURK.value,
            "task_type": TaskType.LABEL.value,
            "description": "为电商产品图片标注品类和属性",
            "reward_usd": 15, "duration_min": 25,
            "difficulty": "easy", "requirements": ["有电商购物经验"],
            "slots": 200, "taken": 67,
            "reliability": 88, "payout_speed": "normal",
            "avg_hourly_rate": 36.0,
            "urgency": TaskUrgency.NORMAL.value,
            "expire_at": datetime.now() + timedelta(days=2),
        },
        {
            "id": "ct_008", "name": "App功能测试", "platform": Platform.USER_TESTING.value,
            "task_type": TaskType.TEST.value,
            "description": "测试新上线App的功能和用户体验",
            "reward_usd": 35, "duration_min": 30,
            "difficulty": "easy", "requirements": ["有手机", "认真反馈"],
            "slots": 30, "taken": 11,
            "reliability": 91, "payout_speed": "fast",
            "avg_hourly_rate": 70.0,
            "urgency": TaskUrgency.HOT.value,
            "expire_at": datetime.now() + timedelta(hours=4),
        },
        # 更多任务
        {
            "id": "ct_009", "name": "法律文档分类", "platform": Platform.APPEN.value,
            "task_type": TaskType.VALIDATE.value,
            "description": "将法律文档分类到指定类别",
            "reward_usd": 30, "duration_min": 45,
            "difficulty": "medium", "requirements": ["懂法律术语"],
            "slots": 40, "taken": 15,
            "reliability": 90, "payout_speed": "normal",
            "avg_hourly_rate": 40.0,
            "urgency": TaskUrgency.NORMAL.value,
            "expire_at": datetime.now() + timedelta(days=3),
        },
        {
            "id": "ct_010", "name": "语音转写标注", "platform": Platform.TOlOKA.value,
            "task_type": TaskType.LABEL.value,
            "description": "将音频转写为文字并标注说话人",
            "reward_usd": 10, "duration_min": 15,
            "difficulty": "easy", "requirements": ["英语听力", "打字快"],
            "slots": 150, "taken": 89,
            "reliability": 78, "payout_speed": "slow",
            "avg_hourly_rate": 40.0,
            "urgency": TaskUrgency.LOW.value,
            "expire_at": datetime.now() + timedelta(days=5),
        },
    ]

    def __init__(self):
        self.tasks: Dict[str, dict] = {}
        self._grabbed: Dict[str, datetime] = {}
        self._scan_history: deque = deque(maxlen=100)
        self._last_scan: Optional[datetime] = None
        self._completed_ids: set = set()

    async def scan_all(self) -> List[dict]:
        """全平台扫描"""
        self._last_scan = datetime.now()
        tasks = []

        for template in self.TASK_POOL:
            # 检查是否过期
            if template["expire_at"] < datetime.now():
                continue

            remaining = template["slots"] - template["taken"]
            if remaining <= 0:
                continue

            task_id = f"{template['id']}_{int(time.time())}"
            hourly_rate = (template["reward_usd"] / template["duration_min"]) * 60

            task = {
                **template,
                "task_id": task_id,
                "remaining_slots": remaining,
                "slot_occupancy": round(template["taken"] / template["slots"] * 100, 1),
                "hourly_rate": round(hourly_rate, 2),
                "scanned_at": datetime.now().isoformat(),
                "status": "available",
            }
            tasks.append(task)
            self.tasks[task_id] = task

        self._scan_history.append({
            "time": datetime.now(),
            "found": len(tasks),
            "hot": sum(1 for t in tasks if t["urgency"] == TaskUrgency.HOT.value),
        })

        return tasks

    def score_task(self, task: dict) -> CrowdTaskScore:
        """多因子评分"""
        factors = {}

        # ── 1. 时薪得分 (0-40) ──────────────────────
        hourly_rate = task["hourly_rate"]
        hourly_rate_score = min(hourly_rate / 50 * 40, 40)  # 50/hr为满分
        factors["hourly_rate"] = hourly_rate
        factors["hourly_rate_score_raw"] = round(hourly_rate_score, 2)

        # ── 2. 可靠性得分 (0-30) ────────────────────
        reliability = task.get("reliability", 80)
        reliability_score = reliability * 0.3
        factors["reliability"] = reliability

        # 付款速度加成
        payout_speed = task.get("payout_speed", "normal")
        payout_bonus = {"fast": 10, "normal": 5, "slow": 0}.get(payout_speed, 0)
        reliability_score = min(reliability_score + payout_bonus, 30)
        factors["payout_speed"] = payout_speed
        factors["payout_bonus"] = payout_bonus

        # ── 3. 速度得分 (0-15) ─────────────────────
        remaining = task["remaining_slots"]
        total = task["slots"]
        occupancy = task["slot_occupancy"]
        if occupancy >= 80:
            speed_score = 15  # 快满了
        elif occupancy >= 60:
            speed_score = 12
        elif occupancy >= 40:
            speed_score = 8
        else:
            speed_score = 5
        factors["slot_urgency"] = speed_score

        # ── 4. 可用性得分 (0-15) ────────────────────
        # 时间窗口
        hours_left = (task["expire_at"] - datetime.now()).total_seconds() / 3600
        if hours_left <= 2:
            avail_score = 15
        elif hours_left <= 8:
            avail_score = 12
        elif hours_left <= 24:
            avail_score = 8
        else:
            avail_score = 5
        factors["time_window"] = round(hours_left, 1)

        total_score = round(hourly_rate_score + reliability_score + speed_score + avail_score, 2)

        # 优先级
        if task["urgency"] == TaskUrgency.HOT.value or total_score >= 80:
            priority = "P1"
        elif total_score >= 60:
            priority = "P2"
        else:
            priority = "P3"

        return CrowdTaskScore(
            task_id=task["task_id"],
            total_score=total_score,
            hourly_rate_score=round(hourly_rate_score, 2),
            reliability_score=round(reliability_score, 2),
            speed_score=speed_score,
            availability_score=avail_score,
            priority=priority,
            factors=factors
        )

    def score_all(self) -> List[CrowdTaskScore]:
        """全部评分排序"""
        scores = [self.score_task(t) for t in self.tasks.values()]
        scores.sort(key=lambda x: -x.total_score)
        return scores

    async def grab_task(self, task_id: str, timeout_ms: int = 3000) -> tuple[bool, str]:
        """抢单"""
        if task_id not in self.tasks:
            return False, "任务不存在"

        task = self.tasks[task_id]

        if task["remaining_slots"] <= 0:
            return False, "名额已满"

        if task["expire_at"] < datetime.now():
            return False, "任务已过期"

        # 模拟网络延迟
        await asyncio.sleep(random.uniform(0.05, 0.3))

        # 检查是否已被抢
        if task_id in self._grabbed:
            grab_time = self._grabbed[task_id]
            if (datetime.now() - grab_time).total_seconds() * 1000 > timeout_ms:
                del self._grabbed[task_id]
            else:
                return False, "正在被抢"

        self._grabbed[task_id] = datetime.now()

        task = self.tasks[task_id]
        if task["remaining_slots"] <= 0:
            del self._grabbed[task_id]
            return False, "名额已满"

        self.tasks[task_id]["remaining_slots"] -= 1
        self.tasks[task_id]["taken"] += 1
        self.tasks[task_id]["status"] = "grabbed"

        return True, task_id

    async def batch_grab(self, task_ids: List[str], max_parallel: int = 3) -> List[Dict]:
        """批量抢单（并发）"""
        semaphore = asyncio.Semaphore(max_parallel)

        async def grab_one(tid):
            async with semaphore:
                ok, msg = await self.grab_task(tid)
                return {"task_id": tid, "success": ok, "message": msg}

        results = await asyncio.gather(*[grab_one(tid) for tid in task_ids])
        return list(results)

    def get_top_tasks(self, limit: int = 5, min_score: float = 50) -> List[Dict]:
        """获取最优任务"""
        scores = self.score_all()
        result = []
        for score in scores:
            if score.total_score < min_score:
                break
            task = self.tasks.get(score.task_id, {})
            if task and task["status"] == "available":
                result.append({
                    "task_id": score.task_id,
                    "name": task.get("name"),
                    "platform": task.get("platform"),
                    "task_type": task.get("task_type"),
                    "reward_usd": task.get("reward_usd"),
                    "duration_min": task.get("duration_min"),
                    "hourly_rate": task.get("hourly_rate"),
                    "difficulty": task.get("difficulty"),
                    "reliability": task.get("reliability"),
                    "payout_speed": task.get("payout_speed"),
                    "remaining_slots": task.get("remaining_slots"),
                    "hours_left": round((task["expire_at"] - datetime.now()).total_seconds() / 3600, 1),
                    "total_score": score.total_score,
                    "hourly_rate_score": score.hourly_rate_score,
                    "reliability_score": score.reliability_score,
                    "priority": score.priority,
                    "urgency": task.get("urgency"),
                })
            if len(result) >= limit:
                break
        return result

    def get_scanner_stats(self) -> Dict:
        """扫描统计"""
        tasks = list(self.tasks.values())
        hot = [t for t in tasks if t.get("urgency") == TaskUrgency.HOT.value]

        total_hourly = sum(t["hourly_rate"] for t in tasks) / len(tasks) if tasks else 0

        return {
            "total_tasks": len(tasks),
            "hot_count": len(hot),
            "total_reward_usd": sum(t["reward_usd"] for t in tasks),
            "avg_hourly_rate": round(total_hourly, 2),
            "last_scan": self._last_scan.isoformat() if self._last_scan else None,
            "scan_history_count": len(self._scan_history),
        }


# ─── 全局实例 ───────────────────────────────────────

crowd_scanner_v2 = CrowdScanner()
