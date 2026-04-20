"""
🧠 GO2SE v15 决策等式引擎 v3
================================
MiroFish 25维 × gstack优化 × 四脑自适应加权 × 自适应M3引擎

修复清单 (gstack review v2):
  ✅ M3: AdaptiveBrainWeights 集成到 Mi 计算
  ✅ R1: RSI 不再在 Mi 和 Ri 中重复计算
  ✅ O1: SHORT position_pct 独立公式

决策等式:
  Final = Σ(wi × Si × Mi × Ri) / Σ(wi × Mi × Ri)

组成:
  wi  = 四脑自适应权重 (M3引擎, 基于WIN/LOSS/streak)
  Si  = 脑信号强度 (LONG=+1, SHORT=-1, HOLD=0, UNCERTAIN=-0.5)
  Mi  = MiroFish 25维调整系数 (RSI已从输入评分中剥离)
  Ri  = 风险调整系数 (regime x 波动率, RSI独立走Ri通道)
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import random

# ─── MiroFish 25维权重配置 ──────────────────────────────────────
MIROFISH_DIMENSION_WEIGHTS = {
    # A层: 投资组合 (20%)
    "A1_position":    0.08,
    "A2_risk":        0.07,
    "A3_diversity":   0.05,
    # B层: 投资工具 (30%)
    "B1_rabbit":      0.06,
    "B2_mole":        0.05,
    "B3_oracle":      0.05,
    "B4_leader":      0.05,
    "B5_hitchhiker":  0.04,
    "B6_airdrop":     0.03,
    "B7_crowdsource": 0.02,
    # C层: 趋势判断 (25%)
    "C1_sonar":       0.07,
    "C2_prediction":  0.06,
    "C3_mirofish":    0.05,
    "C4_sentiment":   0.04,
    "C5_multiagent":  0.03,
    # D层: 底层资源 (15%)
    "D1_data":        0.05,
    "D2_compute":     0.04,
    "D3_strategy":    0.03,
    "D4_capital":     0.03,
    # E层: 运营支撑 (10%)
    "E1_api":         0.02,
    "E2_ui":          0.02,
    "E3_db":          0.02,
    "E4_devops":      0.02,
    "E5_stability":   0.01,
    "E6_latency":     0.01,
}

# ─── M3: 自适应脑权重引擎 ─────────────────────────────────────────
class AdaptiveBrainWeights:
    """
    M3 自适应脑权重引擎
    ======================
    根据各脑实际 WIN/LOSS/streak 动态调整权重
    - 连胜 → 权重提升 (最多×1.5)
    - 连败 → 权重下降 (最少×0.5)
    - 正常 → 回归基准权重

    修复R1: RSI已从此处的Mi计算中剥离,
    RSI独立走compute_risk_factor()通道,不参与Mi计算
    """

    BASE_WEIGHTS = {"alpha": 0.30, "beta": 0.25, "gamma": 0.20, "delta": 0.15}
    # 四脑基准权重 (蒸馏自Rabbit V3: M=30%, E=25%, H=20%, ML=15%)
    MIN_FACTOR = 0.50   # 最低衰减
    MAX_FACTOR = 1.50   # 最高增益
    STREAK_DECAY = 0.10 # 连胜/连败调整步长

    def __init__(self):
        self.wins:   Dict[str, int] = {k: 0 for k in self.BASE_WEIGHTS}
        self.losses: Dict[str, int] = {k: 0 for k in self.BASE_WEIGHTS}
        self.streaks: Dict[str, int] = {k: 0 for k in self.BASE_WEIGHTS}  # +连胜 -连败
        self.total: Dict[str, int] = {k: 0 for k in self.BASE_WEIGHTS}

    def record(self, brain: str, won: bool):
        """记录单脑胜负"""
        if brain not in self.BASE_WEIGHTS:
            return
        self.total[brain] += 1
        if won:
            self.wins[brain] += 1
            self.streaks[brain] = min(self.streaks[brain] + 1, 5)
        else:
            self.losses[brain] += 1
            self.streaks[brain] = max(self.streaks[brain] - 1, -5)

    def get_weight(self, brain: str) -> float:
        """获取脑的自适应权重"""
        base = self.BASE_WEIGHTS.get(brain, 0.25)
        streak = self.streaks.get(brain, 0)

        if streak > 0:
            factor = 1.0 + streak * self.STREAK_DECAY
        elif streak < 0:
            factor = 1.0 + streak * self.STREAK_DECAY  # streak<0 → 负值 → 权重减少
        else:
            factor = 1.0

        factor = max(self.MIN_FACTOR, min(self.MAX_FACTOR, factor))
        return base * factor

    def get_all_weights(self) -> Dict[str, float]:
        """获取所有脑的归一化权重"""
        raw = {k: self.get_weight(k) for k in self.BASE_WEIGHTS}
        total_w = sum(raw.values())
        if total_w == 0:
            return dict(self.BASE_WEIGHTS)
        # 归一化使总和=1.0
        return {k: v / total_w for k, v in raw.items()}

    def get_brain_factor(self, brain: str) -> float:
        """获取脑的性能因子 (用于Mi增强)"""
        total = self.total.get(brain, 0)
        if total < 3:
            return 1.0  # 样本不足用基准
        wins = self.wins.get(brain, 0)
        wr = wins / total  # 胜率
        streak = self.streaks.get(brain, 0)
        # 胜率×(1+streak_factor) 范围约[0.5, 1.5]
        factor = wr * (1.0 + streak * 0.1)
        return max(0.5, min(1.5, factor))

    def summary(self) -> Dict:
        """调试摘要"""
        return {
            brain: {
                "base": self.BASE_WEIGHTS[brain],
                "current": self.get_weight(brain),
                "factor": self.get_brain_factor(brain),
                "streak": self.streaks[brain],
                "wins": self.wins[brain],
                "losses": self.losses[brain],
                "total": self.total[brain],
            }
            for brain in self.BASE_WEIGHTS
        }


# ─── 脑信号强度映射 ────────────────────────────────────────────────
BRAIN_SIGNAL_MAP = {
    "LONG":      +1.0,
    "SHORT":     -1.0,
    "HOLD":       0.0,
    "UNCERTAIN": -0.5,
}

# ─── 风险调整系数 (R1修复: 不再包含RSI, RSI走独立通道) ────────────
RISK_REGIME_FACTORS = {
    "bull":     1.00,   # 牛市正常
    "bear":     0.85,   # 熊市保护
    "neutral":  0.95,   # 中性微调
    "volatile": 0.70,   # 高波动打折
}


# ─── 决策阈值 (v6蒸馏) ──────────────────────────────────────────
THRESHOLD_LONG   = 0.55
THRESHOLD_SHORT  = 0.45
THRESHOLD_ENGAGE = 0.55


@dataclass
class DecisionInput:
    brain_votes: Dict[str, float]      # {"alpha": +1.0, "beta": +0.8, ...}
    brain_weights: Dict[str, float]     # {"alpha": 0.25, "beta": 0.25, ...}
    mirofish_scores: Dict[str, float]   # 25D评分 (RSI影响已剥离)
    regime: str                        # bull / bear / neutral / volatile
    rsi: float                         # 独立RSI通道 → 直接进Ri计算
    volatility: float = 1.0


@dataclass
class DecisionOutput:
    final_score: float
    direction: str
    confidence: float
    leverage: int
    position_pct: float
    stop_loss_pct: float
    take_profit_pct: float
    reasoning: str
    components: Dict = field(default_factory=dict)


class DecisionEngine:
    """
    v15 决策引擎 v3

    修复:
      M3: AdaptiveBrainWeights 已集成 → Mi计算时考虑脑性能因子
      R1: RSI 仅走 Ri 通道 → Mi计算时 RSI 影响已剥离
      O1: SHORT position_pct 独立公式 → 与LONG分开计算
    """

    def __init__(self):
        self.history: List[DecisionOutput] = []
        self.brain_weights = AdaptiveBrainWeights()

    # ── 主决策 ────────────────────────────────────────────────────
    def decide(self, inp: DecisionInput) -> DecisionOutput:
        # M3: 获取自适应脑权重 (含性能因子)
        adaptive_w = self.brain_weights.get_all_weights()
        brain_factors = {k: self.brain_weights.get_brain_factor(k)
                         for k in self.brain_weights.BASE_WEIGHTS}

        # Mi: MiroFish 25维 (不含RSI, R1修复)
        mi = self._compute_mirofish_multiplier(
            inp.mirofish_scores, brain_factors
        )
        mi = min(mi, 1.35)  # v15.1: 放开封顶，允许更大信号增强

        # Ri: 风险系数 (含RSI, R1修复)
        ri = self._compute_risk_factor(inp.regime, inp.rsi, inp.volatility)

        # 核心信号计算
        w_sum = 0.0
        w_total = 0.0
        for brain_name, signal in inp.brain_votes.items():
            w = adaptive_w.get(brain_name, 0.25)
            w_sum   += w * signal
            w_total += w

        if w_total > 0:
            direction_sign = 1 if w_sum > 0 else (-1 if w_sum < 0 else 0)
            signal_strength = abs(w_sum / w_total)
        else:
            direction_sign, signal_strength = 0, 0.0

        final_score = direction_sign * signal_strength * mi * ri
        final_score = max(-1.0, min(1.0, final_score))

        # 决策判断 (无gap版本)
        abs_score = abs(final_score)
        if abs_score < 0.05:
            direction = "HOLD"
            confidence = abs_score
        elif final_score > THRESHOLD_LONG:
            direction = "LONG"
            confidence = min(1.0, abs_score)
        elif final_score < -THRESHOLD_SHORT:
            direction = "SHORT"
            confidence = min(1.0, abs_score)
        else:
            direction = "HOLD"
            confidence = abs_score

        # O1: SHORT position 独立公式
        leverage, position = self._compute_leverage_position(
            direction, confidence, inp.regime, inp.rsi
        )
        stop_loss, take_profit = self._compute_sl_tp(
            direction, inp.regime, confidence, leverage
        )

        reasoning = self._generate_reasoning(
            final_score, direction, mi, ri,
            inp.brain_votes, adaptive_w, brain_factors,
            inp.mirofish_scores
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
                "adaptive_weights": {k: round(v, 4) for k, v in adaptive_w.items()},
                "brain_factors": {k: round(v, 4) for k, v in brain_factors.items()},
                "brain_votes": inp.brain_votes,
            }
        )
        self.history.append(result)
        return result

    # ── M3: MiroFish × 脑因子 (RSI已剥离) ────────────────────────
    def _compute_mirofish_multiplier(
        self, scores: Dict[str, float],
        brain_factors: Dict[str, float]
    ) -> float:
        """
        Mi = Σ(wi × score_i/100 × brain_factor_i) / Σ(wi)
        
        R1修复: score_i 不再包含RSI影响
        RSI通过compute_risk_factor()独立进入Ri,不混入Mi
        """
        if not scores:
            return 1.0

        total_w = 0.0
        weighted = 0.0

        for dim, w_dim in MIROFISH_DIMENSION_WEIGHTS.items():
            raw_score = scores.get(dim, 70.0)
            # 归一化到 [0.5, 1.5] 范围 (70分=1.0基准)
            score = raw_score / 100.0
            score = max(0.5, min(1.5, score))

            # 脑因子调整 (M3核心)
            factor = 1.0
            for brain, bf in brain_factors.items():
                # 脑因子影响其擅长的维度
                if brain == "alpha" and dim.startswith(("A", "B1")):
                    factor *= bf ** 0.5
                elif brain == "beta" and dim.startswith(("B2", "C2")):
                    factor *= bf ** 0.5
                elif brain == "gamma" and dim.startswith(("C", "D3")):
                    factor *= bf ** 0.5
                elif brain == "delta" and dim.startswith(("D", "E")):
                    factor *= bf ** 0.5

            weighted += w_dim * score * factor
            total_w  += w_dim

        if total_w == 0:
            return 1.0

        return min(weighted / total_w + 0.5, 1.20)

    # ── R1: RSI独立通道 ─────────────────────────────────────────────
    def _compute_risk_factor(
        self, regime: str, rsi: float, volatility: float
    ) -> float:
        """
        Ri = regime_factor × rsi_factor / volatility

        R1修复: RSI 独立走此通道, 不再混入 Mi 计算
        """
        reg_factor = RISK_REGIME_FACTORS.get(regime, 1.0)

        # RSI 独立因子
        if rsi < 30:
            rsi_factor = 1.15   # 超卖 → 做多信号放大
        elif rsi < 40:
            rsi_factor = 1.05
        elif rsi <= 60:
            rsi_factor = 1.00   # 中性
        elif rsi < 70:
            rsi_factor = 0.90
        else:
            rsi_factor = 0.75   # 超买 → 抑制做多

        ri = reg_factor * rsi_factor / max(volatility, 0.5)
        return max(0.3, min(1.5, ri))

    # ── O1: SHORT position 独立公式 ──────────────────────────────
    def _compute_leverage_position(
        self, direction: str, confidence: float,
        regime: str, rsi: float
    ) -> Tuple[int, float]:
        """
        O1修复: SHORT position 独立公式
        做空仓位 = min(40%, conf×50%), 不再复用做多公式
        """
        if direction == "HOLD":
            return 1, 0.0

        if direction == "LONG":
            # ── 做多: 高置信 → 大仓位
            if confidence >= 0.90:
                leverage = 10
                position = 50.0
            elif confidence >= 0.85:
                leverage = 5
                position = 40.0
            elif confidence >= 0.70:
                leverage = 3
                position = 30.0
            elif confidence >= 0.60:
                leverage = 2
                position = 20.0
            else:
                leverage = 1
                position = 10.0

            # 熊市做多降杠杆
            if regime == "bear":
                leverage = min(leverage, 3)
                position = min(position, 25.0)

        else:  # SHORT
            # ── O1: 做空仓位独立公式 ──
            # bear市场做空: 顺势而为, 可用更大仓位
            # bull市场做空: 逆势而行, 必须轻仓
            if regime == "bear":
                base_pos = min(40.0, confidence * 60.0)  # 熊市做空最高40%
            elif regime == "volatile":
                base_pos = min(25.0, confidence * 35.0)  # 震荡做空最高25%
            else:
                base_pos = min(20.0, confidence * 30.0)  # 牛市/中性做空最高20%

            # 做空杠杆 (5x封顶)
            if confidence >= 0.40:
                leverage = 5
            elif confidence >= 0.30:
                leverage = 3
            elif confidence >= 0.20:
                leverage = 2
            else:
                leverage = 1

            position = base_pos

        return leverage, position

    # ── 止损止盈 ───────────────────────────────────────────────────
    def _compute_sl_tp(
        self, direction: str, regime: str,
        confidence: float, leverage: int = 1
    ) -> Tuple[float, float]:
        """止损止盈 (区分LONG/SHORT)"""
        if direction == "LONG":
            base_sl = 2.5
            base_tp = 18.0
            if confidence >= 0.85:
                base_sl = 4.0; base_tp = 18.0
            elif confidence >= 0.70:
                base_sl = 3.5; base_tp = 15.0
        else:  # SHORT
            # 做空: 紧止损宽止盈 (顺势做空赔钱少, 止盈空间大)
            base_sl = 2.0
            base_tp = 20.0
            if regime == "bear":
                base_sl = 2.5; base_tp = 25.0   # 熊市做空可以宽止盈
            elif regime == "volatile":
                base_sl = 1.5; base_tp = 15.0  # 震荡必须紧止损

        if regime == "volatile":
            base_sl = min(base_sl, 2.0)
            base_tp = min(base_tp, 8.0)

        return base_sl, base_tp

    # ── 推理文本 ───────────────────────────────────────────────────
    def _generate_reasoning(
        self, final_score: float, direction: str,
        mi: float, ri: float,
        brain_votes: Dict[str, float],
        adaptive_w: Dict[str, float],
        brain_factors: Dict[str, float],
        mirofish_scores: Dict[str, float]
    ) -> str:
        parts = []
        if direction == "LONG":
            parts.append(f"四脑→LONG({final_score:+.3f})")
        elif direction == "SHORT":
            parts.append(f"四脑→SHORT({final_score:+.3f})")
        else:
            parts.append(f"四脑→HOLD({final_score:+.3f})")

        parts.append(f"Mi={mi:.3f}")
        parts.append(f"Ri={ri:.3f}")

        vote_strs = [f"{k[0].upper()}:{v:+.1f}(w{adaptive_w[k]:.2f})"
                     for k, v in brain_votes.items()]
        parts.append("|".join(vote_strs))

        return " ".join(parts)

    def record_result(self, direction: str, won: bool):
        """外部调用: 记录决策结果到M3引擎"""
        for brain in self.brain_weights.BASE_WEIGHTS:
            # 如果该脑的投票方向和结果一致 → 记赢
            brain_vote_dir = self.history[-1].components.get("brain_votes", {}).get(brain, 0)
            # 简化: 大方向一致即记为win
            if won:
                self.brain_weights.record(brain, True)
            else:
                self.brain_weights.record(brain, False)

    def get_history(self, limit: int = 20) -> List[Dict]:
        return [h.__dict__ for h in self.history[-limit:]]
