from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List
from datetime import datetime

class BrainType(str, Enum):
    ALPHA = "alpha"
    BETA  = "beta"
    GAMMA = "gamma"
    DELTA = "delta"

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

ALPHA_CONFIG = BrainConfig(
    name="左脑Alpha", brain_type=BrainType.ALPHA, mode=Mode.NORMAL,
    leverage=2.0, stop_loss_pct=4.0, take_profit_pct=12.0,
    min_confidence=65.0, max_position_pct=40.0, win_rate_estimate=72.0,
    description="v13左脑: 普通模式, 趋势追踪, 稳健收益"
)
BETA_CONFIG = BrainConfig(
    name="右脑Beta", brain_type=BrainType.BETA, mode=Mode.EXPERT,
    leverage=3.0, stop_loss_pct=2.5, take_profit_pct=18.0,
    min_confidence=60.0, max_position_pct=50.0, win_rate_estimate=78.0,
    description="v13右脑: 专家模式, 高频套利, 高胜率"
)
GAMMA_CONFIG = BrainConfig(
    name="上脑Gamma", brain_type=BrainType.GAMMA, mode=Mode.DYNAMIC,
    leverage=3.0, stop_loss_pct=3.0, take_profit_pct=15.0,
    min_confidence=70.0, max_position_pct=60.0, win_rate_estimate=82.0,
    description="v6i上脑: 动态杠杆, 自主多空切换引擎"
)
DELTA_CONFIG = BrainConfig(
    name="下脑Delta", brain_type=BrainType.DELTA, mode=Mode.SIM,
    leverage=2.5, stop_loss_pct=3.0, take_profit_pct=12.0,
    min_confidence=75.0, max_position_pct=45.0, win_rate_estimate=85.0,
    description="MiroFish下脑: 25维仿真, 风险熔断保护"
)
ALL_BRAINS = {b: c for b, c in zip(BrainType, [ALPHA_CONFIG, BETA_CONFIG, GAMMA_CONFIG, DELTA_CONFIG])}
BRAIN_WEIGHTS = {BrainType.ALPHA: 0.20, BrainType.BETA: 0.25, BrainType.GAMMA: 0.30, BrainType.DELTA: 0.25}

@dataclass
class BrainSignal:
    brain: BrainType
    direction: str
    confidence: float
    leverage: float
    position_pct: float
    stop_loss_pct: float
    take_profit_pct: float
    reason: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

class AdaptiveBrainWeights:
    """
    M3: 根据历史表现动态调整脑权重
    继承 v6i 自主迭代引擎模式: 连续改善→权重+, 连续恶化→权重-
    """
    def __init__(self):
        self.scores: Dict[BrainType, float] = {b: 70.0 for b in BrainType}
        self.streak_up: Dict[BrainType, int] = {b: 0 for b in BrainType}
        self.streak_dn: Dict[BrainType, int] = {b: 0 for b in BrainType}
        self.history: List[Dict] = []

    def record(self, brain: BrainType, outcome: str, confidence: float):
        prev = self.scores[brain]
        d = 0.0
        if outcome == "WIN":
            d = confidence * 0.05
            self.streak_up[brain] += 1
            self.streak_dn[brain] = 0
        elif outcome == "LOSS":
            d = -confidence * 0.05
            self.streak_dn[brain] += 1
            self.streak_up[brain] = 0
        if self.streak_up[brain] >= 3: d += 1.5
        if self.streak_dn[brain] >= 3: d -= 1.5
        self.scores[brain] = max(0.0, min(100.0, prev + d))
        self.history.append({"brain": brain.value, "prev": prev, "new": self.scores[brain], "delta": d, "outcome": outcome})

    def get(self) -> Dict[BrainType, float]:
        total = sum(self.scores.values())
        return {b: s / total for b, s in self.scores.items()}

    def status(self) -> Dict:
        return {
            "scores": {b.value: round(s, 2) for b, s in self.scores.items()},
            "weights": {b.value: round(w, 4) for b, w in self.get().items()},
            "streak_up": {b.value: c for b, c in self.streak_up.items()},
            "streak_dn": {b.value: c for b, c in self.streak_dn.items()},
            "records": len(self.history),
        }

adaptive_weights = AdaptiveBrainWeights()

class QuadBrainEngine:
    def __init__(self):
        self.active_brains: List[BrainType] = list(BrainType)
        self.vote_history: List[Dict] = []

    def get_brain_status(self) -> Dict:
        aw = adaptive_weights.get()
        return {
            "active_brains": [b.value for b in self.active_brains],
            "brains": {
                b.value: {
                    "name": ALL_BRAINS[b].name,
                    "mode": ALL_BRAINS[b].mode.value,
                    "leverage": ALL_BRAINS[b].leverage,
                    "win_rate_estimate": ALL_BRAINS[b].win_rate_estimate,
                    "adaptive_weight": round(aw.get(b, 0.25), 4),
                }
                for b in self.active_brains
            },
            "total_votes": len(self.vote_history),
        }

    def think(self, symbol: str, regime: str, confidence: float) -> BrainSignal:
        votes = [self._vote(b, symbol, regime, confidence) for b in self.active_brains]
        aw = adaptive_weights.get()
        weighted = sum(v.confidence * aw.get(v.brain, 0.25) for v in votes)
        total_w = sum(aw.get(b, 0.25) for b in self.active_brains)
        final_conf = weighted / total_w if total_w else 0
        dirs = [v.direction for v in votes]
        final_dir = max(set(dirs), key=dirs.count) if dirs else "HOLD"
        best = max(votes, key=lambda v: v.confidence)
        adaptive_weights.record(BrainType.GAMMA, "NEUTRAL", final_conf)
        self.vote_history.append({"ts": datetime.now().isoformat(), "symbol": symbol, "regime": regime, "votes": [(v.brain.value, v.direction, v.confidence) for v in votes], "final": final_dir, "conf": final_conf})
        return BrainSignal(brain=BrainType.GAMMA, direction=final_dir, confidence=final_conf, leverage=best.leverage, position_pct=best.position_pct, stop_loss_pct=best.stop_loss_pct, take_profit_pct=best.take_profit_pct, reason=f"四脑: {final_dir} ({final_conf:.0f}%) | {best.reason}")

    def _vote(self, bt: BrainType, symbol: str, regime: str, conf: float) -> BrainSignal:
        c = ALL_BRAINS[bt]
        if bt == BrainType.ALPHA:
            d = "LONG" if conf >= c.min_confidence and regime in ["bull","neutral"] else "HOLD"
            lev = c.leverage
        elif bt == BrainType.BETA:
            if regime == "bear" and conf >= 70: d = "SHORT"
            elif regime in ["bull","neutral"] and conf >= c.min_confidence: d = "LONG"
            else: d = "HOLD"
            lev = c.leverage
        elif bt == BrainType.GAMMA:
            lev = 10 if conf >= 90 else 5 if conf >= 85 else 3 if conf >= 75 else 2 if conf >= 65 else 1
            if regime == "bear" and conf >= 70: d = "SHORT"
            elif regime in ["bull","neutral"] and conf >= c.min_confidence: d = "LONG"
            else: d = "HOLD"
        else:
            lev = min(c.leverage, 3)
            d = "LONG" if conf >= 85 and regime in ["bull","neutral"] else ("SHORT" if conf >= 85 and regime == "bear" else "HOLD")
        pos = min(c.max_position_pct, conf * 0.6)
        return BrainSignal(brain=bt, direction=d, confidence=conf, leverage=lev, position_pct=pos, stop_loss_pct=c.stop_loss_pct, take_profit_pct=c.take_profit_pct, reason=f"{c.name}: {d} {lev}x")
