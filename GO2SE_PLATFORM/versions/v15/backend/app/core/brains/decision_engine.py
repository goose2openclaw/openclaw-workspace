"""
🧠 GO2SE v15 决策等式引擎
================================
MiroFish 25维 × gstack优化 × 四脑自适应加权

优化版决策等式:
  Final = Σ(wi × Si × Mi × Ri) / Σ(wi × Mi × Ri)

组成:
  wi  = 四脑自适应权重 (M3引擎)
  Si  = 脑信号强度 (LONG=+1, SHORT=-1, HOLD=0, UNCERTAIN=-0.5)
  Mi  = MiroFish 25维调整系数
  Ri  = 风险调整系数 (regime, RSI, 波动率)

决策规则:
  Final > 0.70 → LONG
  Final < 0.30 → SHORT
  Final ∈ [0.30, 0.70] → HOLD
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import random

# ─── MiroFish 25维权重配置 (gstack优化) ─────────────────────────────
MIROFISH_DIMENSION_WEIGHTS = {
    # A层: 投资组合 (20%)
    "A1_position":   0.08,   # 仓位分配
    "A2_risk":      0.07,   # 风控规则
    "A3_diversity": 0.05,   # 多样化
    # B层: 投资工具 (30%)
    "B1_rabbit":    0.06,   # 打兔子 (权重最高)
    "B2_mole":      0.05,   # 打地鼠
    "B3_oracle":    0.05,   # 走着瞧
    "B4_leader":    0.05,   # 跟大哥
    "B5_hitchhiker":0.04,   # 搭便车
    "B6_airdrop":   0.03,   # 薅羊毛
    "B7_crowdsource":0.02,  # 穷孩子
    # C层: 趋势判断 (25%)
    "C1_sonar":     0.07,   # 声纳库
    "C2_prediction": 0.06,  # 预测引擎
    "C3_mirofish":  0.05,  # MiroFish共识
    "C4_sentiment":  0.04,  # 市场情绪
    "C5_multiagent": 0.03,  # 多智能体
    # D层: 底层资源 (15%)
    "D1_data":      0.05,   # 市场数据
    "D2_compute":   0.04,   # 算力资源
    "D3_strategy":  0.03,  # 策略引擎
    "D4_capital":   0.03,  # 资金管理
    # E层: 运营支撑 (10%)
    "E1_api":       0.02,   # 后端API
    "E2_ui":        0.02,   # 前端UI
    "E3_db":        0.02,   # 数据库
    "E4_devops":   0.02,   # 运维脚本
    "E5_stability": 0.01,  # 系统稳定性
    "E6_latency":   0.01,   # API延迟
}

# ─── 脑信号强度映射 ────────────────────────────────────────────────
BRAIN_SIGNAL_MAP = {
    "LONG":      +1.0,
    "SHORT":     -1.0,
    "HOLD":       0.0,
    "UNCERTAIN": -0.5,
}

# ─── 风险调整系数 ─────────────────────────────────────────────────
RISK_REGIME_FACTORS = {
    "bull":      1.0,    # 牛市正常
    "bear":      0.85,   # 熊市打折(保护)
    "neutral":   0.95,   # 中性微调
    "volatile":  0.70,   # 高波动大幅打折
}

RSI_RISK = {
    (0, 30):    1.15,   # 超卖 → 放大做多信号
    (30, 40):   1.05,
    (40, 60):    1.00,
    (60, 70):   0.90,
    (70, 100):  0.75,   # 超买 → 抑制做多/放大做空
}

# ─── 决策阈值 ────────────────────────────────────────────────────
THRESHOLD_LONG  = 0.70   # Final > 0.70 → LONG
THRESHOLD_SHORT = 0.30   # Final < 0.30 → SHORT
THRESHOLD_ENGAGE = 0.60  # confidence < 0.60 → 降低仓位

@dataclass
class DecisionInput:
    """决策输入"""
    brain_votes: Dict[str, float]     # {"alpha": +1.0, "beta": +0.8, ...}
    brain_weights: Dict[str, float]    # {"alpha": 0.25, "beta": 0.25, ...}
    mirofish_scores: Dict[str, float]  # {"A1_position": 80.0, "B1_rabbit": 75.0, ...}
    regime: str                        # bull/bear/neutral/volatile
    rsi: float                       # 0-100
    volatility: float = 1.0         # 波动率倍数

@dataclass
class DecisionOutput:
    """决策输出"""
    final_score: float
    direction: str                    # LONG / SHORT / HOLD
    confidence: float                # 0-1
    leverage: int                   # 1-10
    position_pct: float             # 0-100
    stop_loss_pct: float
    take_profit_pct: float
    reasoning: str
    components: Dict = field(default_factory=dict)

class DecisionEngine:
    """
    v15 优化决策引擎
    Final = Σ(wi × Si × Mi × Ri) / Σ(wi × Mi × Ri)
    """

    def __init__(self):
        self.history: List[DecisionOutput] = []

    def decide(self, inp: DecisionInput) -> DecisionOutput:
        # 1. 计算 MiroFish 综合系数
        mi = self._compute_mirofish_multiplier(inp.mirofish_scores)

        # 2. 计算风险调整系数
        ri = self._compute_risk_factor(inp.regime, inp.rsi, inp.volatility)

        # 3. 计算加权决策分数
        weighted_num = 0.0
        weighted_den = 0.0

        for brain_name, signal in inp.brain_votes.items():
            w = inp.brain_weights.get(brain_name, 0.25)
            weighted_num += w * signal * mi * ri
            weighted_den += abs(w * mi * ri)

        final_score = weighted_num / weighted_den if weighted_den > 0 else 0.0
        final_score = max(-1.0, min(1.0, final_score))

        # 4. 确定方向
        if final_score > THRESHOLD_LONG:
            direction = "LONG"
            confidence = min(1.0, final_score)
        elif final_score < THRESHOLD_SHORT:
            direction = "SHORT"
            confidence = min(1.0, 1.0 - final_score)
        else:
            direction = "HOLD"
            confidence = 1.0 - abs(final_score - 0.5) * 2

        # 5. 计算杠杆和仓位
        leverage, position = self._compute_leverage_position(
            direction, confidence, inp.regime, inp.rsi
        )

        # 6. 止损止盈
        stop_loss, take_profit = self._compute_sl_tp(
            direction, inp.regime, confidence
        )

        # 7. 生成推理
        reasoning = self._generate_reasoning(
            final_score, direction, mi, ri,
            inp.brain_votes, inp.mirofish_scores
        )

        result = DecisionOutput(
            final_score=round(final_score, 4),
            direction=direction,
            confidence=round(confidence, 4),
            leverage=leverage,
            position_pct=round(position, 2),
            stop_loss_pct=round(stop_loss, 2),
            take_profit_pct=round(take_profit, 2),
            reasoning=reasoning,
            components={
                "mi": round(mi, 4),
                "ri": round(ri, 4),
                "brain_votes": inp.brain_votes,
                "mirofish_scores": inp.mirofish_scores,
            }
        )

        self.history.append(result)
        return result

    def _compute_mirofish_multiplier(self, scores: Dict[str, float]) -> float:
        """
        计算 MiroFish 25维调整系数 Mi
        Mi = Σ(wi × score_i/100) / Σ(wi)
        将25维评分加权平均,归一化到0.5-1.5范围
        """
        if not scores:
            return 1.0

        total_weight = 0.0
        weighted_sum = 0.0

        for dim, weight in MIROFISH_DIMENSION_WEIGHTS.items():
            score = scores.get(dim, 70.0) / 100.0  # 归一化到0-1
            weighted_sum += weight * score
            total_weight += weight

        if total_weight == 0:
            return 1.0

        mi = weighted_sum / total_weight
        # 映射到 0.5-1.5 范围
        mi = 0.5 + mi  # 0.5 + (0-1) = 0.5-1.5
        return mi

    def _compute_risk_factor(
        self, regime: str, rsi: float, volatility: float
    ) -> float:
        """计算风险调整系数 Ri"""
        reg_factor = RISK_REGIME_FACTORS.get(regime, 1.0)

        rsi_factor = 1.0
        for (low, high), factor in RSI_RISK.items():
            if low <= rsi < high:
                rsi_factor = factor
                break

        ri = reg_factor * rsi_factor / volatility
        return max(0.3, min(1.5, ri))

    def _compute_leverage_position(
        self, direction: str, confidence: float,
        regime: str, rsi: float
    ) -> Tuple[int, float]:
        """计算杠杆和仓位"""
        if direction == "HOLD":
            return 1, 0.0

        # 置信度 → 杠杆档位
        if confidence >= 0.90:
            leverage = 10
        elif confidence >= 0.85:
            leverage = 5
        elif confidence >= 0.75:
            leverage = 3
        elif confidence >= 0.60:
            leverage = 2
        else:
            leverage = 1

        # 熊市做多限制杠杆
        if regime == "bear" and direction == "LONG":
            leverage = min(leverage, 3)

        # 做空限制杠杆
        if direction == "SHORT":
            leverage = min(leverage, 3)

        # 仓位: 置信度 × 基础仓位
        base_position = min(60.0, confidence * 80.0)
        position = base_position

        return leverage, position

    def _compute_sl_tp(
        self, direction: str, regime: str, confidence: float
    ) -> Tuple[float, float]:
        """计算止损止盈"""
        base_sl = 3.0
        base_tp = 12.0

        # 高置信度 → 宽止损窄止盈(让利润奔跑)
        if confidence >= 0.85:
            base_sl = 4.0
            base_tp = 18.0
        elif confidence >= 0.75:
            base_sl = 3.5
            base_tp = 15.0

        # 震荡市 → 收紧
        if regime == "volatile":
            base_sl = min(base_sl, 2.0)
            base_tp = min(base_tp, 8.0)

        return base_sl, base_tp

    def _generate_reasoning(
        self, final_score: float, direction: str,
        mi: float, ri: float,
        brain_votes: Dict[str, float],
        mirofish_scores: Dict[str, float]
    ) -> str:
        """生成决策推理文本"""
        parts = []

        # 分数解读
        if direction == "LONG":
            parts.append(f"四脑加权{final_score:.2f}→LONG")
        elif direction == "SHORT":
            parts.append(f"四脑加权{final_score:.2f}→SHORT")
        else:
            parts.append(f"四脑加权{final_score:.2f}→HOLD")

        # MiroFish影响
        parts.append(f"MiroFish×{mi:.2f}")
        parts.append(f"风险系数×{ri:.2f}")

        # 各脑投票
        vote_strs = [f"{k[:1].upper()}:{v:+.1f}" for k, v in brain_votes.items()]
        parts.append(" ".join(vote_strs))

        return " | ".join(parts)

    def get_history(self, limit: int = 20) -> List[Dict]:
        return [
            {
                "final_score": h.final_score,
                "direction": h.direction,
                "confidence": h.confidence,
                "leverage": h.leverage,
                "position_pct": h.position_pct,
                "timestamp": getattr(h, "timestamp", None),
            }
            for h in self.history[-limit:]
        ]
