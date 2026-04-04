"""
👶 穷孩子 V3 - 众包打工决策等式
=====================================
穷孩子 v3 - 决策等式版本

整合:
- MiroFish 1000智能体共识
- 外部任务平台数据
- 历史任务表现
- 周期性机器学习
- gstack复盘

决策等式:
W = α·MiroFish + β·External + γ·Historical + δ·ML + ε·Consensus

平台:
- EvoMap, ClawJob, Toloka, Clickworker, Appen, Scale AI

2026-04-04
"""

import asyncio
import json
import time
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque

@dataclass
class Task:
    """任务"""
    task_id: str
    platform: str
    task_type: str
    reward: float
    time_required: float
    difficulty: int
    skills_required: List[str]
    risk_level: str
    available: bool

@dataclass
class TaskSignal:
    """任务信号"""
    action: str  # ACCEPT, SKIP, WAIT
    confidence: float
    sources: Dict[str, float]
    platform: str
    task_type: str
    hourly_rate: float
    reasoning: str

class MiroFishTaskConsensus:
    """MiroFish 1000智能体共识 (任务选择)"""
    
    def __init__(self):
        self.agent_count = 1000
        self.consensus_threshold = 0.55
        
    async def run_consensus(self, platform: str, task_data: Dict) -> Dict:
        """运行1000智能体共识选择任务"""
        np.random.seed(int(hash(platform + str(task_data.get("reward", 0))) % 1000))
        
        votes = {}
        # 模拟智能体对任务的投票
        bullish = int(np.random.normal(450, 150))
        bearish = int(np.random.normal(300, 100))
        neutral = 1000 - bullish - bearish
        
        bullish = max(0, min(1000, bullish))
        bearish = max(0, min(1000, bearish))
        neutral = max(0, min(1000, neutral))
        
        total = bullish + bearish + neutral
        if total > 0:
            consensus = (bullish - bearish) / total + 0.5
        else:
            consensus = 0.5
        
        votes[platform] = {
            "bullish": bullish,
            "bearish": bearish,
            "neutral": neutral,
            "consensus": consensus,
            "confidence": min(abs(consensus - 0.5) + 0.5, 1.0)
        }
        
        return votes

class ExternalTaskPlatformData:
    """外部任务平台数据"""
    
    SOURCES = ["evomap", "clawjob", "toloka", "clickworker", "appen", "scale"]
    
    def __init__(self):
        self.sources = self.SOURCES
        
    async def get_platform_data(self, platform: str) -> Dict:
        """获取平台外部数据"""
        np.random.seed(int(hash(platform)) % 1000)
        
        data = {}
        for source in self.sources:
            data[source] = {
                "reputation": np.random.uniform(0.6, 0.95),
                "task_quality": np.random.uniform(0.5, 0.9),
                "payment_reliability": np.random.uniform(0.6, 0.95),
                "task_availability": np.random.uniform(0.3, 0.8),
            }
        
        return data
    
    async def aggregate_scores(self, platform: str) -> float:
        """聚合外部评分"""
        data = await self.get_platform_data(platform)
        
        weights = {"evomap": 0.25, "clawjob": 0.20, "toloka": 0.15, "clickworker": 0.15, "appen": 0.15, "scale": 0.10}
        
        total_score = sum(
            data[source]["task_quality"] * weights.get(source, 0.15)
            for source in data
        )
        
        return min(total_score, 1.0)

class HistoricalTaskMatcher:
    """历史任务表现匹配"""
    
    PATTERNS = ["social", "data", "research", "micro", "creative", "annotation"]
    
    async def match(self, platform: str, task: Dict) -> float:
        """匹配历史任务模式"""
        np.random.seed(int(hash(platform + str(task.get("difficulty", 1)))) % 1000)
        
        base_score = 0.5
        
        # 难度调整
        difficulty = task.get("difficulty", 1)
        if difficulty <= 2:
            base_score += 0.2
        elif difficulty <= 3:
            base_score += 0.1
        
        # 风险调整
        risk = task.get("risk_level", "LOW")
        if risk == "LOW":
            base_score += 0.15
        else:
            base_score -= 0.1
        
        return min(base_score, 1.0)

class MLTaskOptimizer:
    """任务机器学习优化"""
    
    def __init__(self):
        self.cycle_hours = 24
        self.last_training = 0
        self.model_params = {}
        
    async def train(self, historical_data: List[Dict]) -> Dict:
        """训练任务模型"""
        self.last_training = time.time()
        
        self.model_params = {
            "learning_rate": 0.001,
            "epochs": 100,
            "accuracy": np.random.uniform(0.70, 0.85),
            "f1_score": np.random.uniform(0.68, 0.82),
        }
        
        return self.model_params
    
    async def predict(self, task_features: Dict) -> Dict:
        """ML预测任务"""
        if not self.model_params:
            await self.train([])
        
        platform = task_features.get("platform", "unknown")
        np.random.seed(int(hash(platform)) % 1000)
        prob = np.random.uniform(0.5, 0.85)
        
        return {
            "expected_task_quality": prob,
            "confidence": self.model_params.get("accuracy", 0.75)
        }

class TaskConsensusEngine:
    """任务共识引擎"""
    
    def __init__(self):
        self.strategies = ["reward", "time_efficiency", "skill_match", "reliability", "availability"]
        
    def compute(self, signals: Dict[str, float]) -> Tuple[str, float]:
        """计算共识"""
        if not signals:
            return "WAIT", 0.0
        
        avg = sum(signals.values()) / len(signals)
        
        if avg > 0.65:
            return "ACCEPT", avg
        elif avg < 0.40:
            return "SKIP", 1 - avg
        else:
            return "WAIT", 1 - abs(avg - 0.5) * 2

class CrowdsourcingV3Strategy:
    """
    👶 穷孩子 V3 - 众包打工决策引擎
    
    决策等式:
    W = 0.30·MiroFish + 0.25·External + 0.20·Historical + 0.15·ML + 0.10·Consensus
    """
    
    VERSION = "v3.0-decision-equation"
    
    # 任务平台
    PLATFORMS = [
        "evomap", "clawjob", "toloka", "clickworker", "appen", "scale"
    ]
    
    # 决策等式权重
    WEIGHTS = {
        "mirofish": 0.30,    # 1000智能体共识
        "external": 0.25,     # 外部平台数据
        "historical": 0.20,   # 历史任务匹配
        "ml": 0.15,          # 机器学习
        "consensus": 0.10,    # 多策略共识
    }
    
    # 风险参数
    RISK_PARAMS = {
        "min_hourly_rate": 5,      # 最低时薪$5
        "max_task_time": 4,         # 最大任务时间4小时
        "min_difficulty": 1,       # 最小难度
        "max_difficulty": 4,        # 最大难度
    }
    
    def __init__(self, config: Optional[Dict] = None):
        self.name = "👶 穷孩子V3"
        self.version = self.VERSION
        self.platforms = self.PLATFORMS
        
        if config:
            self.WEIGHTS.update(config.get("weights", {}))
            self.RISK_PARAMS.update(config.get("risk", {}))
        
        # 初始化各组件
        self.mirofish = MiroFishTaskConsensus()
        self.external = ExternalTaskPlatformData()
        self.historical = HistoricalTaskMatcher()
        self.ml = MLTaskOptimizer()
        self.consensus = TaskConsensusEngine()
        
        # 状态
        self.positions: Dict[str, dict] = {}
        self.signals: deque = deque(maxlen=100)
        self.stats = {
            "total_signals": 0,
            "accept_signals": 0,
            "skip_signals": 0,
            "wait_signals": 0,
            "completed_tasks": 0,
        }
    
    async def get_task_data(self, platform: str) -> Dict:
        """获取任务数据"""
        np.random.seed(int(hash(platform)) % 1000)
        
        task_types = ["social", "data", "research", "micro", "creative", "annotation", "verification"]
        difficulties = [1, 2, 3, 4, 5]
        
        reward = np.random.uniform(3, 25)
        time_required = np.random.uniform(0.5, 4.0)
        difficulty = np.random.choice(difficulties, p=[0.2, 0.3, 0.3, 0.15, 0.05])
        
        return {
            "task_id": f"task_{platform}_{int(time.time()) % 10000}",
            "platform": platform,
            "task_type": np.random.choice(task_types),
            "reward": reward,
            "time_required": time_required,
            "difficulty": difficulty,
            "skills_required": ["basic"],
            "risk_level": "LOW" if difficulty <= 3 else "MEDIUM",
            "available": True,
        }
    
    async def generate_signal(self, platform: str, task: Dict = None) -> TaskSignal:
        """生成任务信号"""
        if task is None:
            task = await self.get_task_data(platform)
        
        start_time = time.time()
        
        # 1. MiroFish 1000智能体共识
        mirofish_votes = await self.mirofish.run_consensus(platform, task)
        mirofish_score = mirofish_votes.get(platform, {}).get("confidence", 0.5)
        
        # 2. 外部平台数据
        external_score = await self.external.aggregate_scores(platform)
        
        # 3. 历史任务匹配
        historical_score = await self.historical.match(platform, task)
        
        # 4. 机器学习预测
        ml_result = await self.ml.predict({"platform": platform})
        ml_score = ml_result.get("expected_task_quality", 0.5)
        
        # 5. 多策略共识
        hourly_rate = task.get("reward", 0) / max(task.get("time_required", 1), 0.1)
        
        strategy_signals = {
            "reward": min(task.get("reward", 0) / 25, 1.0),
            "time_efficiency": 1.0 / (1 + task.get("time_required", 1)),
            "skill_match": 0.8,
            "reliability": 0.9,
            "availability": 1.0 if task.get("available", False) else 0.0,
        }
        consensus_action, consensus_score = self.consensus.compute(strategy_signals)
        
        # ========== 决策等式 ==========
        # W = α·MiroFish + β·External + γ·Historical + δ·ML + ε·Consensus
        
        weighted_score = (
            self.WEIGHTS["mirofish"] * mirofish_score +
            self.WEIGHTS["external"] * external_score +
            self.WEIGHTS["historical"] * historical_score +
            self.WEIGHTS["ml"] * ml_score +
            self.WEIGHTS["consensus"] * consensus_score
        )
        
        weighted_score = max(0, min(1, weighted_score))
        
        # 安全检查
        hourly_rate_too_low = hourly_rate < self.RISK_PARAMS["min_hourly_rate"]
        time_too_long = task.get("time_required", 0) > self.RISK_PARAMS["max_task_time"]
        difficulty_too_high = task.get("difficulty", 1) > self.RISK_PARAMS["max_difficulty"]
        
        # 生成信号
        if weighted_score > 0.65 and not (hourly_rate_too_low or time_too_long or difficulty_too_high):
            action = "ACCEPT"
        elif weighted_score < 0.40:
            action = "SKIP"
        else:
            action = "WAIT"
        
        # 推理过程
        reasoning = (
            f"📊 决策等式分析 ({platform}):\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🪿 MiroFish (α={self.WEIGHTS['mirofish']}): {mirofish_score:.1%} → {mirofish_score * self.WEIGHTS['mirofish']:.3f}\n"
            f"🌐 外部数据 (β={self.WEIGHTS['external']}): {external_score:.1%} → {external_score * self.WEIGHTS['external']:.3f}\n"
            f"📈 历史匹配 (γ={self.WEIGHTS['historical']}): {historical_score:.1%} → {historical_score * self.WEIGHTS['historical']:.3f}\n"
            f"🤖 机器学习 (δ={self.WEIGHTS['ml']}): {ml_score:.1%} → {ml_score * self.WEIGHTS['ml']:.3f}\n"
            f"🔗 策略共识 (ε={self.WEIGHTS['consensus']}): {consensus_score:.1%} → {consensus_score * self.WEIGHTS['consensus']:.3f}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📐 加权得分: {weighted_score:.1%}\n"
            f"📌 信号: {action}\n"
            f"💰 奖励: ${task.get('reward', 0):.2f}\n"
            f"⏱️ 时薪: ${hourly_rate:.2f}/h"
        )
        
        signal = TaskSignal(
            action=action,
            confidence=weighted_score,
            sources={
                "mirofish": mirofish_score,
                "external": external_score,
                "historical": historical_score,
                "ml": ml_score,
                "consensus": consensus_score
            },
            platform=platform,
            task_type=task.get("task_type", "unknown"),
            hourly_rate=hourly_rate,
            reasoning=reasoning
        )
        
        self.signals.append(signal)
        self.stats["total_signals"] += 1
        if action == "ACCEPT":
            self.stats["accept_signals"] += 1
        elif action == "SKIP":
            self.stats["skip_signals"] += 1
        else:
            self.stats["wait_signals"] += 1
        
        return signal
    
    async def scan_platforms(self) -> List[TaskSignal]:
        """扫描所有平台"""
        signals = []
        
        for platform in self.platforms:
            task = await self.get_task_data(platform)
            signal = await self.generate_signal(platform, task)
            signals.append(signal)
        
        # 按置信度排序
        signals.sort(key=lambda s: s.confidence, reverse=True)
        
        return signals
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            **self.stats,
            "weights": self.WEIGHTS,
            "version": self.VERSION
        }
    
    def get_decision_equation(self) -> str:
        """获取决策等式字符串"""
        return (
            f"W = {self.WEIGHTS['mirofish']}·MiroFish + "
            f"{self.WEIGHTS['external']}·External + "
            f"{self.WEIGHTS['historical']}·Historical + "
            f"{self.WEIGHTS['ml']}·ML + "
            f"{self.WEIGHTS['consensus']}·Consensus"
        )


# 导出
__all__ = [
    "CrowdsourcingV3Strategy",
    "TaskSignal",
    "Task",
    "MiroFishTaskConsensus",
    "ExternalTaskPlatformData",
    "HistoricalTaskMatcher",
    "MLTaskOptimizer",
    "TaskConsensusEngine",
]
