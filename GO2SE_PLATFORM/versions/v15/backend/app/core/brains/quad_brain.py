#!/usr/bin/env python3
"""
🧠 GO2SE v15 Quad Brain System
================================
四脑系统 = v13双脑 × v6i自主切换 × MiroFish仿真

架构:
  左脑 (Alpha)  → 普通模式, 趋势追踪, 稳健收益
  右脑 (Beta)   → 专家模式, 高频套利, 高胜率
  上脑 (Gamma)  → 动态杠杆, 自主多空切换
  下脑 (Delta)  → MiroFish仿真, 风险熔断

v13双脑 → v15四脑升级:
  - 左脑: 继承v13左脑配置 (胜率72%, 2x杠杆)
  - 右脑: 继承v13右脑配置 (胜率78%, 3x杠杆)
  - 新增Gamma: 动态杠杆大脑 (v6i自主切换引擎)
  - 新增Delta: MiroFish风险大脑 (25维仿真)
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Optional, List
from datetime import datetime
import random

class BrainType(str, Enum):
    ALPHA = "alpha"  # 左脑: 普通模式
    BETA  = "beta"   # 右脑: 专家模式
    GAMMA = "gamma"  # 上脑: 动态杠杆
    DELTA = "delta"  # 下脑: MiroFish仿真

class Mode(str, Enum):
    NORMAL  = "normal"
    EXPERT  = "expert"
    DYNAMIC = "dynamic"
    SIM     = "simulation"

@dataclass
class BrainConfig:
    name: str
    brain_type: BrainType
    mode: Mode
    leverage: float
    stop_loss_pct: float
    take_profit_pct: float
    min_confidence: float
    max_position_pct: float
    win_rate_estimate: float
    description: str

# ─── v13双脑配置继承 ───────────────────────────────
ALPHA_CONFIG = BrainConfig(
    name="左脑Alpha",
    brain_type=BrainType.ALPHA,
    mode=Mode.NORMAL,
    leverage=2.0,
    stop_loss_pct=4.0,
    take_profit_pct=12.0,
    min_confidence=65.0,
    max_position_pct=40.0,
    win_rate_estimate=72.0,
    description="v13左脑: 普通模式, 趋势追踪, 稳健收益"
)

BETA_CONFIG = BrainConfig(
    name="右脑Beta",
    brain_type=BrainType.BETA,
    mode=Mode.EXPERT,
    leverage=3.0,
    stop_loss_pct=2.5,
    take_profit_pct=18.0,
    min_confidence=60.0,
    max_position_pct=50.0,
    win_rate_estimate=78.0,
    description="v13右脑: 专家模式, 高频套利, 高胜率"
)

GAMMA_CONFIG = BrainConfig(
    name="上脑Gamma",
    brain_type=BrainType.GAMMA,
    mode=Mode.DYNAMIC,
    leverage=3.0,  # 动态调整 2x-10x
    stop_loss_pct=3.0,
    take_profit_pct=15.0,
    min_confidence=70.0,
    max_position_pct=60.0,
    win_rate_estimate=82.0,
    description="v6i上脑: 动态杠杆, 自主多空切换引擎"
)

DELTA_CONFIG = BrainConfig(
    name="下脑Delta",
    brain_type=BrainType.DELTA,
    mode=Mode.SIM,
    leverage=2.5,
    stop_loss_pct=3.0,
    take_profit_pct=12.0,
    min_confidence=75.0,
    max_position_pct=45.0,
    win_rate_estimate=85.0,
    description="MiroFish下脑: 25维仿真, 风险熔断保护"
)

ALL_BRAINS: Dict[BrainType, BrainConfig] = {
    BrainType.ALPHA: ALPHA_CONFIG,
    BrainType.BETA: BETA_CONFIG,
    BrainType.GAMMA: GAMMA_CONFIG,
    BrainType.DELTA: DELTA_CONFIG,
}

# ─── 四脑评分矩阵 ─────────────────────────────────
BRAIN_WEIGHTS = {
    BrainType.ALPHA: 0.20,  # 稳健
    BrainType.BETA:  0.25,  # 高胜率
    BrainType.GAMMA: 0.30,  # 动态杠杆
    BrainType.DELTA: 0.25,  # 仿真保护
}

@dataclass
class BrainSignal:
    brain: BrainType
    direction: str          # LONG / SHORT / HOLD
    confidence: float
    leverage: float
    position_pct: float
    stop_loss_pct: float
    take_profit_pct: float
    reason: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

class QuadBrainEngine:
    """
    四脑决策引擎
    每个脑独立评估 → 加权投票 → 最终决策
    """

    def __init__(self):
        self.active_brains: List[BrainType] = [
            BrainType.ALPHA, BrainType.BETA,
            BrainType.GAMMA, BrainType.DELTA
        ]
        self.vote_history: List[Dict] = []

    def think(self, symbol: str, regime: str, confidence: float) -> BrainSignal:
        """
        四脑同时思考 → 加权决策
        """
        votes: List[BrainSignal] = []

        for brain_type in self.active_brains:
            vote = self._brain_vote(brain_type, symbol, regime, confidence)
            votes.append(vote)

        # 加权评分
        weighted_score = 0.0
        total_weight = 0.0
        for vote, brain_type in zip(votes, self.active_brains):
            w = BRAIN_WEIGHTS[brain_type]
            score = vote.confidence * w
            weighted_score += score
            total_weight += w

        final_confidence = weighted_score / total_weight

        # 多数投票决定方向
        directions = [v.direction for v in votes]
        final_direction = max(set(directions), key=directions.count)

        # 取最高置信度的理由
        best_vote = max(votes, key=lambda v: v.confidence)

        self.vote_history.append({
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "regime": regime,
            "confidence": confidence,
            "votes": [(v.brain, v.direction, v.confidence) for v in votes],
            "final_direction": final_direction,
            "final_confidence": final_confidence,
        })

        return BrainSignal(
            brain=BrainType.GAMMA,  # 以Gamma为代表输出
            direction=final_direction,
            confidence=final_confidence,
            leverage=best_vote.leverage,
            position_pct=best_vote.position_pct,
            stop_loss_pct=best_vote.stop_loss_pct,
            take_profit_pct=best_vote.take_profit_pct,
            reason=f"四脑加权: {final_direction} ({final_confidence:.0f}%) | " + best_vote.reason,
        )

    def _brain_vote(self, brain_type: BrainType, symbol: str,
                     regime: str, confidence: float) -> BrainSignal:
        """单个脑的投票逻辑"""
        cfg = ALL_BRAINS[brain_type]

        if brain_type == BrainType.ALPHA:
            # 左脑: 普通模式趋势追踪
            if confidence >= cfg.min_confidence and regime in ["bull", "neutral"]:
                direction = "LONG"
            else:
                direction = "HOLD"
            leverage = cfg.leverage

        elif brain_type == BrainType.BETA:
            # 右脑: 专家模式多空
            if regime == "bear" and confidence >= 70:
                direction = "SHORT"
            elif regime in ["bull", "neutral"] and confidence >= cfg.min_confidence:
                direction = "LONG"
            else:
                direction = "HOLD"
            leverage = cfg.leverage

        elif brain_type == BrainType.GAMMA:
            # 上脑: v6i动态杠杆 (来自v6i_agents)
            leverage_tiers = [
                (90, 10, "极激进"),
                (85, 5, "激进"),
                (75, 3, "中等"),
                (65, 2, "保守"),
            ]
            for threshold, lev, desc in leverage_tiers:
                if confidence >= threshold:
                    leverage = lev
                    break
            if regime == "bear":
                direction = "SHORT" if confidence >= 70 else "HOLD"
            elif regime == "bull":
                direction = "LONG" if confidence >= cfg.min_confidence else "HOLD"
            else:
                direction = "HOLD" if confidence < 80 else "LONG"

        else:  # DELTA
            # 下脑: MiroFish仿真保护
            if confidence >= 85:
                direction = "LONG" if regime in ["bull", "neutral"] else "SHORT"
                leverage = min(cfg.leverage, 3)  # MiroFish限制杠杆
            elif confidence >= 70:
                direction = "HOLD"  # 置信度不足时保持
                leverage = cfg.leverage
            else:
                direction = "HOLD"
                leverage = 2.0

        # 计算仓位
        position_pct = min(cfg.max_position_pct, confidence * 0.6)

        return BrainSignal(
            brain=brain_type,
            direction=direction,
            confidence=confidence,
            leverage=leverage,
            position_pct=position_pct,
            stop_loss_pct=cfg.stop_loss_pct,
            take_profit_pct=cfg.take_profit_pct,
            reason=f"{cfg.name}: {direction} {leverage}x",
        )

    def get_brain_status(self) -> Dict:
        """返回四脑状态"""
        return {
            "active_brains": [b.value for b in self.active_brains],
            "brains": {
                b.value: {
                    "name": ALL_BRAINS[b].name,
                    "mode": ALL_BRAINS[b].mode.value,
                    "leverage": ALL_BRAINS[b].leverage,
                    "win_rate_estimate": ALL_BRAINS[b].win_rate_estimate,
                    "description": ALL_BRAINS[b].description,
                }
                for b in self.active_brains
            },
            "weights": {b.value: w for b, w in BRAIN_WEIGHTS.items()},
            "total_votes": len(self.vote_history),
        }
