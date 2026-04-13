#!/usr/bin/env python3
"""
💰 薅羊毛 V3 - 智能找单·选品·抢单
================================
找单：多源实时扫描
选品：多因子评分排序
抢单：并发高速抢占
"""

import asyncio
import time
import random
import hashlib
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import re

# ─── 枚举 ──────────────────────────────────────────────

class TaskSource(str, Enum):
    DELEGATED = "delegated"           # 官方任务
    COMMUNITY = "community"           # 社区推荐
    TRENDING = "trending"            # 热门趋势
    NEW_LAUNCH = "new_launch"         # 新上线
    HIGH_PRIORITY = "high_priority"   # 高优先级

class Priority(str, Enum):
    P0 = "P0"   # 立即抢
    P1 = "P1"   # 优先
    P2 = "P2"   # 正常
    P3 = "P3"   # 观望

class TaskStatus(str, Enum):
    NEW = "new"
    SCANNING = "scanning"
    AVAILABLE = "available"
    GRABBED = "grabbed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EXPIRED = "expired"
    TAKEN = "taken"  # 被抢走

# ─── 评分因子 ────────────────────────────────────────

@dataclass
class TaskScore:
    """任务评分"""
    task_id: str
    total_score: float           # 综合评分 0-100
    return_score: float          # 收益得分 (0-30)
    speed_score: float           # 速度得分 (0-25)
    reliability_score: float      # 可靠性得分 (0-25)
    efficiency_score: float       # 效率得分 (0-20)
    priority: Priority
    factors: Dict[str, float]    # 各因子明细
    recommendation: str          # 推荐理由


class AirdropScanner:
    """
    🔍 智能找单扫描器
    多源实时扫描 + 优先级排序
    """

    # 扩展任务库（增加来源和优先级）
    TASK_POOL = [
        # P0 高优先级
        {
            "id": "p0_001", "name": "LayerZero V2 主网",
            "project": "LayerZero", "chain": "Multi-chain",
            "actions": ["bridge", "swap", "stake"],
            "expected_return_usd": 800, "gas_usd": 25,
            "difficulty": "medium", "source": TaskSource.HIGH_PRIORITY,
            "priority": Priority.P0, "slots": 50, "taken": 23,
            "deadline": datetime.now() + timedelta(hours=2),
            "reliability": 95, "time_cost_min": 30,
        },
        {
            "id": "p0_002", "name": "zkSync Era 主网",
            "project": "zkSync", "chain": "zkSync",
            "actions": ["bridge", "mint", "swap"],
            "expected_return_usd": 500, "gas_usd": 18,
            "difficulty": "easy", "source": TaskSource.TRENDING,
            "priority": Priority.P0, "slots": 100, "taken": 67,
            "deadline": datetime.now() + timedelta(hours=4),
            "reliability": 92, "time_cost_min": 20,
        },
        # P1 优先
        {
            "id": "p1_001", "name": "Starknet 交互",
            "project": "Starknet", "chain": "Starknet",
            "actions": ["swap", "stake", "bridge"],
            "expected_return_usd": 300, "gas_usd": 12,
            "difficulty": "easy", "source": TaskSource.NEW_LAUNCH,
            "priority": Priority.P1, "slots": 200, "taken": 45,
            "deadline": datetime.now() + timedelta(days=1),
            "reliability": 88, "time_cost_min": 15,
        },
        {
            "id": "p1_002", "name": "Linea 交互",
            "project": "Linea", "chain": "Linea",
            "actions": ["bridge", "swap"],
            "expected_return_usd": 200, "gas_usd": 10,
            "difficulty": "easy", "source": TaskSource.TRENDING,
            "priority": Priority.P1, "slots": 150, "taken": 89,
            "deadline": datetime.now() + timedelta(hours=6),
            "reliability": 85, "time_cost_min": 12,
        },
        {
            "id": "p1_003", "name": "Berachain 测试网",
            "project": "Berachain", "chain": "Berachain",
            "actions": ["bridge", "swap", "farm"],
            "expected_return_usd": 600, "gas_usd": 20,
            "difficulty": "medium", "source": TaskSource.COMMUNITY,
            "priority": Priority.P1, "slots": 80, "taken": 12,
            "deadline": datetime.now() + timedelta(days=2),
            "reliability": 78, "time_cost_min": 35,
        },
        # P2 正常
        {
            "id": "p2_001", "name": "Monad 测试网",
            "project": "Monad", "chain": "Monad",
            "actions": ["swap", "transfer"],
            "expected_return_usd": 700, "gas_usd": 30,
            "difficulty": "medium", "source": TaskSource.TRENDING,
            "priority": Priority.P2, "slots": 300, "taken": 156,
            "deadline": datetime.now() + timedelta(days=3),
            "reliability": 82, "time_cost_min": 25,
        },
        {
            "id": "p2_002", "name": "Abstract 交互",
            "project": "Abstract", "chain": "Abstract",
            "actions": ["mint", "claim_nft"],
            "expected_return_usd": 150, "gas_usd": 8,
            "difficulty": "easy", "source": TaskSource.DELEGATED,
            "priority": Priority.P2, "slots": 500, "taken": 234,
            "deadline": datetime.now() + timedelta(days=7),
            "reliability": 90, "time_cost_min": 10,
        },
        {
            "id": "p2_003", "name": "Mode 交互",
            "project": "Mode", "chain": "Mode",
            "actions": ["bridge", "swap", "delegate"],
            "expected_return_usd": 250, "gas_usd": 15,
            "difficulty": "easy", "source": TaskSource.NEW_LAUNCH,
            "priority": Priority.P2, "slots": 200, "taken": 78,
            "deadline": datetime.now() + timedelta(days=5),
            "reliability": 80, "time_cost_min": 18,
        },
        # P3 观望
        {
            "id": "p3_001", "name": "AltLayer V2",
            "project": "AltLayer", "chain": "Multi-chain",
            "actions": ["bridge", "stake"],
            "expected_return_usd": 100, "gas_usd": 12,
            "difficulty": "easy", "source": TaskSource.COMMUNITY,
            "priority": Priority.P3, "slots": 1000, "taken": 450,
            "deadline": datetime.now() + timedelta(days=14),
            "reliability": 70, "time_cost_min": 15,
        },
        {
            "id": "p3_002", "name": "Nimble 交互",
            "project": "Nimble", "chain": "Nimble",
            "actions": ["swap", "provide_liquidity"],
            "expected_return_usd": 180, "gas_usd": 20,
            "difficulty": "medium", "source": TaskSource.COMMUNITY,
            "priority": Priority.P3, "slots": 150, "taken": 23,
            "deadline": datetime.now() + timedelta(days=10),
            "reliability": 65, "time_cost_min": 30,
        },
    ]

    def __init__(self):
        self.tasks: Dict[str, dict] = {}
        self._grabbed: Dict[str, datetime] = {}  # 已抢任务
        self._scan_history: deque = deque(maxlen=100)
        self._last_scan: Optional[datetime] = None

    async def scan_all(self) -> List[dict]:
        """全源扫描"""
        self._last_scan = datetime.now()
        tasks = []

        for template in self.TASK_POOL:
            # 检查是否过期
            if template["deadline"] < datetime.now():
                continue

            # 检查是否还有名额
            remaining = template["slots"] - template["taken"]
            if remaining <= 0:
                continue

            task_id = f"{template['id']}_{int(time.time())}"
            task = {
                **template,
                "task_id": task_id,
                "remaining_slots": remaining,
                "slot_occupancy": round(template["taken"] / template["slots"] * 100, 1),
                "scanned_at": datetime.now().isoformat(),
                "status": TaskStatus.AVAILABLE.value,
            }
            tasks.append(task)
            self.tasks[task_id] = task

        self._scan_history.append({
            "time": datetime.now(),
            "found": len(tasks),
            "p0": sum(1 for t in tasks if t["priority"] == Priority.P0.value),
            "p1": sum(1 for t in tasks if t["priority"] == Priority.P1.value),
        })

        return tasks

    def score_task(self, task: dict) -> TaskScore:
        """
        多因子评分
        收益(30) + 速度(25) + 可靠性(25) + 效率(20) = 100
        """
        factors = {}

        # ── 1. 收益得分 (0-30) ──────────────────────
        # 预期收益评分
        return_base = min(task["expected_return_usd"] / 30, 30)  # 上限30
        # Gas效率
        net_return = task["expected_return_usd"] - task["gas_usd"]
        gas_efficiency = min(net_return / task["gas_usd"] * 3, 15)  # 成本收益比
        return_score = round(return_base + gas_efficiency, 2)
        factors["return_raw"] = round(return_base, 2)
        factors["gas_efficiency"] = round(gas_efficiency, 2)

        # ── 2. 速度得分 (0-25) ─────────────────────
        # 名额紧迫度（越少越快抢）
        remaining = task["remaining_slots"]
        total = task["slots"]
        slot_score = 0
        occupancy = task["slot_occupancy"]
        if occupancy >= 90:
            slot_score = 25  # 快满了
        elif occupancy >= 70:
            slot_score = 20
        elif occupancy >= 50:
            slot_score = 15
        elif occupancy >= 30:
            slot_score = 10
        else:
            slot_score = 5

        # 时间窗口（越短越急）
        deadline = task["deadline"]
        hours_left = (deadline - datetime.now()).total_seconds() / 3600
        time_score = 0
        if hours_left <= 1:
            time_score = 25
        elif hours_left <= 4:
            time_score = 20
        elif hours_left <= 12:
            time_score = 15
        elif hours_left <= 48:
            time_score = 10
        else:
            time_score = 5

        speed_score = round(slot_score * 0.5 + time_score * 0.5, 2)
        factors["slot_urgency"] = slot_score
        factors["time_urgency"] = time_score

        # ── 3. 可靠性得分 (0-25) ────────────────────
        reliability = task.get("reliability", 75)
        reliability_score = reliability * 0.25  # 0-25
        factors["reliability"] = reliability

        # ── 4. 效率得分 (0-20) ──────────────────────
        # 时薪 = 收益/时间成本
        time_cost = task["time_cost_min"]
        hourly_rate = (task["expected_return_usd"] - task["gas_usd"]) / (time_cost / 60)
        efficiency_score = min(hourly_rate / 30 * 20, 20)  # 假设30/hr为满分
        factors["hourly_rate"] = round(hourly_rate, 2)
        factors["time_cost_min"] = time_cost

        total_score = round(return_score + speed_score + reliability_score + efficiency_score, 2)

        # 优先级
        priority = task["priority"]
        if total_score >= 80 and priority in [Priority.P0.value, Priority.P1.value]:
            final_priority = Priority.P0
        elif total_score >= 60:
            final_priority = Priority.P1
        elif total_score >= 40:
            final_priority = Priority.P2
        else:
            final_priority = Priority.P3

        # 推荐理由
        reasons = []
        if return_score >= 25: reasons.append("高收益")
        if speed_score >= 20: reasons.append("名额紧张")
        if reliability_score >= 20: reasons.append("高可靠")
        if efficiency_score >= 15: reasons.append("高效率")
        recommendation = " | ".join(reasons) if reasons else "普通任务"

        return TaskScore(
            task_id=task["task_id"],
            total_score=total_score,
            return_score=round(return_score, 2),
            speed_score=speed_score,
            reliability_score=round(reliability_score, 2),
            efficiency_score=round(efficiency_score, 2),
            priority=final_priority,
            factors=factors,
            recommendation=recommendation
        )

    def score_all(self) -> List[TaskScore]:
        """对所有任务评分排序"""
        scores = [self.score_task(t) for t in self.tasks.values()]
        scores.sort(key=lambda x: (
            -x.total_score,
            x.priority.value if isinstance(x.priority, Priority) else x.priority
        ))
        return scores

    async def grab_task(self, task_id: str, timeout_ms: int = 5000) -> tuple[bool, str]:
        """
        抢单（带并发锁）
        """
        if task_id not in self.tasks:
            return False, "任务不存在"

        task = self.tasks[task_id]

        # 检查是否已被抢
        if task["remaining_slots"] <= 0:
            return False, "名额已满"

        # 检查是否过期
        if task["deadline"] < datetime.now():
            task["status"] = TaskStatus.EXPIRED.value
            return False, "任务已过期"

        # 模拟抢单延迟
        await asyncio.sleep(random.uniform(0.1, 0.5))

        # 检查并发（简单锁）
        if task_id in self._grabbed:
            # 检查是否超时
            grab_time = self._grabbed[task_id]
            if (datetime.now() - grab_time).total_seconds() * 1000 > timeout_ms:
                del self._grabbed[task_id]
            else:
                return False, "任务正在被抢"

        # 抢占
        self._grabbed[task_id] = datetime.now()

        # 再次检查名额
        task = self.tasks[task_id]  # 重新获取（可能被更新）
        if task["remaining_slots"] <= 0:
            del self._grabbed[task_id]
            return False, "名额已满(并发)"

        # 扣减名额
        self.tasks[task_id]["remaining_slots"] -= 1
        self.tasks[task_id]["taken"] += 1
        self.tasks[task_id]["status"] = TaskStatus.GRABBED.value

        return True, task_id

    def get_top_tasks(self, limit: int = 5, min_score: float = 50) -> List[Dict]:
        """获取最优任务"""
        scores = self.score_all()
        result = []
        for score in scores:
            if score.total_score < min_score:
                break
            task = self.tasks.get(score.task_id, {})
            if task:
                result.append({
                    "task_id": score.task_id,
                    "name": task.get("name"),
                    "project": task.get("project"),
                    "chain": task.get("chain"),
                    "expected_return_usd": task.get("expected_return_usd"),
                    "gas_usd": task.get("gas_usd"),
                    "net_return": task.get("expected_return_usd") - task.get("gas_usd"),
                    "priority": score.priority.value if isinstance(score.priority, Priority) else score.priority,
                    "total_score": score.total_score,
                    "return_score": score.return_score,
                    "speed_score": score.speed_score,
                    "reliability_score": score.reliability_score,
                    "efficiency_score": score.efficiency_score,
                    "remaining_slots": task.get("remaining_slots"),
                    "hours_left": round((task["deadline"] - datetime.now()).total_seconds() / 3600, 1),
                    "recommendation": score.recommendation,
                    "factors": score.factors,
                })
            if len(result) >= limit:
                break
        return result

    def get_scanner_stats(self) -> Dict:
        """扫描统计"""
        tasks = list(self.tasks.values())
        p0 = [t for t in tasks if t.get("priority") == Priority.P0.value]
        p1 = [t for t in tasks if t.get("priority") == Priority.P1.value]
        p2 = [t for t in tasks if t.get("priority") == Priority.P2.value]
        p3 = [t for t in tasks if t.get("priority") == Priority.P3.value]

        total_expected = sum(t["expected_return_usd"] for t in tasks)
        total_gas = sum(t["gas_usd"] for t in tasks)

        return {
            "total_tasks": len(tasks),
            "p0_count": len(p0),
            "p1_count": len(p1),
            "p2_count": len(p2),
            "p3_count": len(p3),
            "total_expected_usd": round(total_expected, 2),
            "total_gas_usd": round(total_gas, 2),
            "net_potential_usd": round(total_expected - total_gas, 2),
            "last_scan": self._last_scan.isoformat() if self._last_scan else None,
            "scan_history_count": len(self._scan_history),
        }


# ─── 全局实例 ───────────────────────────────────────

scanner_v2 = AirdropScanner()
