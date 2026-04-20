"""
====================================================================
  MIROFISH PLATFORM ENGINE - v1.0
  平台级25维仲裁引擎

角色:
  1. 集中式25维度评分引擎 (vv6 + v15 共享)
  2. Mi (市场调整系数) 计算中枢
  3. vv6 vs v15 信号仲裁器
  4. 策略权重优化引擎
  5. 历史表现追踪器

架构:
  vv6 + v15 ---> MiroFish Platform ---> Brain Coordinator
                    ^^^^^^^^^^^^^^
                    (仲裁 + 权重优化)

25维度结构:
  A层(投资组合):    A1_position, A2_risk, A3_diversity
  B层(投资工具):    B1-B7 (7个agent权重)
  C层(趋势判断):    C1_sonar, C2_prediction, C3_mirofish, C4_sentiment, C5_multiagent
  D层(底层资源):    D1_data, D2_compute, D3_strategy, D4_capital
  E层(运营支撑):    E1-E6 (6个运营维度)
====================================================================
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List, Literal
from datetime import datetime
from enum import Enum
import time as time_module
import asyncio
import random
from collections import defaultdict
from dataclasses import dataclass, field

app = FastAPI(title="MiroFish Platform Engine", version="1.0.0")

# ─── 25维配置 ────────────────────────────────────────────────────
class DimLayer(str, Enum):
    A = "portfolio"    # 投资组合层 (20%)
    B = "tools"       # 投资工具层 (30%)
    C = "trends"      # 趋势判断层 (25%)
    D = "resources"   # 底层资源层 (15%)
    E = "operations"  # 运营支撑层 (10%)

DIM_WEIGHTS = {
    # A层: 投资组合 (20%)
    "A1_position":   0.08,
    "A2_risk":       0.07,
    "A3_diversity":  0.05,
    # B层: 投资工具 (30%)
    "B1_rabbit":     0.06,
    "B2_mole":       0.05,
    "B3_oracle":     0.05,
    "B4_leader":     0.05,
    "B5_hitchhiker": 0.04,
    "B6_airdrop":    0.03,
    "B7_crowdsource":0.02,
    # C层: 趋势判断 (25%)
    "C1_sonar":      0.07,
    "C2_prediction": 0.06,
    "C3_mirofish":   0.05,
    "C4_sentiment":  0.04,
    "C5_multiagent": 0.03,
    # D层: 底层资源 (15%)
    "D1_data":       0.05,
    "D2_compute":    0.04,
    "D3_strategy":   0.03,
    "D4_capital":    0.03,
    # E层: 运营支撑 (10%)
    "E1_api":        0.02,
    "E2_ui":         0.02,
    "E3_db":         0.02,
    "E4_devops":     0.02,
    "E5_stability":  0.01,
    "E6_latency":    0.01,
}

LAYER_WEIGHTS = {
    DimLayer.A: 0.20,
    DimLayer.B: 0.30,
    DimLayer.C: 0.25,
    DimLayer.D: 0.15,
    DimLayer.E: 0.10,
}

LAYER_DIMS = {
    DimLayer.A: ["A1_position","A2_risk","A3_diversity"],
    DimLayer.B: ["B1_rabbit","B2_mole","B3_oracle","B4_leader","B5_hitchhiker","B6_airdrop","B7_crowdsource"],
    DimLayer.C: ["C1_sonar","C2_prediction","C3_mirofish","C4_sentiment","C5_multiagent"],
    DimLayer.D: ["D1_data","D2_compute","D3_strategy","D4_capital"],
    DimLayer.E: ["E1_api","E2_ui","E3_db","E4_devops","E5_stability","E6_latency"],
}

# ─── 状态存储 ────────────────────────────────────────────────────
class PlatformState:
    def __init__(self):
        # 25维当前分数 (0-100)
        self.dimensions: Dict[str, float] = {d: 75.0 for d in DIM_WEIGHTS}
        # Mi 历史
        self.mi_history: List[Dict] = []
        # 信号仲裁历史
        self.arbitration_history: List[Dict] = []
        # 策略表现追踪
        self.strategy_scores: Dict[str, Dict] = {
            "vv6": {"wins": 0, "losses": 0, "streak": 0, "last": "", "history": []},
            "v15": {"wins": 0, "losses": 0, "streak": 0, "last": "", "history": []},
            "coordinator": {"wins": 0, "losses": 0, "streak": 0, "last": "", "history": []},
        }
        # 策略权重 (Kelly优化用)
        self.strategy_weights: Dict[str, float] = {
            "vv6": 0.40,
            "v15": 0.40,
            "coordinator": 0.20,
        }
        # agent权重 (vv6/v15共享)
        self.agent_weights: Dict[str, float] = {
            "rabbit": 0.25,
            "mole": 0.20,
            "oracle": 0.15,
            "leader": 0.15,
            "hitchhiker": 0.10,
            "airdrop": 0.08,
            "crowdsource": 0.07,
        }
        # 启动时间
        self.start_time = datetime.now().isoformat()
        self.request_count = 0
        # 懒加载标志
        self._dimensions_loaded = False

    def refresh_dimensions_from_market(self) -> Dict[str, float]:
        """从v7 backend获取真实市场数据,初始化维度评分"""
        dims = {d: 75.0 for d in DIM_WEIGHTS}
        try:
            import urllib.request, json as _json
            req = urllib.request.Request(
                "http://localhost:8000/api/v7/market/summary",
                headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = _json.loads(resp.read()).get("data", {})
            fg = float(data.get("fear_greed_index", 50))
            trend = data.get("trend", "neutral")
            dims["A1_position"] = min(95, 60 + fg * 0.35)
            dims["A2_risk"] = max(40, 85 - fg * 0.3)
            if fg > 60:
                dims["B1_rabbit"] = min(95, 65 + (fg - 60) * 1.5)
            elif fg < 40:
                dims["B1_rabbit"] = max(50, 70 - (40 - fg) * 1.5)
            if trend in ("up", "down", "bullish", "bearish"):
                dims["C1_sonar"] = 80
                dims["C2_prediction"] = 78
            else:
                dims["C1_sonar"] = 70
                dims["C2_prediction"] = 72
            dims["C4_sentiment"] = fg * 0.8 + 20
            if fg < 35:
                dims["D1_data"] = min(90, 70 + (35 - fg) * 0.8)
            if trend in ("up", "bullish"):
                dims["E1_api"] = 80
                dims["E4_devops"] = 78
        except Exception:
            pass
        self.dimensions = dims
        return dims

state = PlatformState()

# ─── Pydantic模型 ────────────────────────────────────────────────
class ScoreUpdate(BaseModel):
    dimension: str
    score: float
    source: str = "manual"  # "vv6" | "v15" | "coordinator" | "manual"

class ArbitrationRequest(BaseModel):
    vv6_signal: dict
    v15_signal: dict
    regime: str = "neutral"
    rsi: float = 50.0
    fear_greed: float = 50.0

class StrategyWeightUpdate(BaseModel):
    strategy: str  # "vv6" | "v15" | "coordinator"
    outcome: str   # "WIN" | "LOSS"
    confidence: float
    direction: str

class PortfolioAllocationRequest(BaseModel):
    regime: str = "neutral"
    rsi: float = 50.0
    fear_greed: float = 50.0
    vv6_confidence: float = 0.0
    v15_confidence: float = 0.0
    coordinator_confidence: float = 0.0
    vv6_direction: str = "hold"
    v15_direction: str = "hold"
    coordinator_direction: str = "hold"

# ─── 核心计算函数 ────────────────────────────────────────────────
def compute_mi(dimensions: Dict[str, float], regime: str, rsi: float, fear_greed: float) -> float:
    """
    Mi = 市场调整系数 (Market adjustment multiplier)
    = 四脑信号一致性 × 市场情绪系数 × RSI系数 × 波动率调整
    范围: 0.5 ~ 1.35
    """
    # A层综合评分 (投资组合健康度)
    a_score = sum(dimensions.get(d, 75) * DIM_WEIGHTS.get(d, 0) for d in LAYER_DIMS[DimLayer.A])
    a_score /= sum(DIM_WEIGHTS.get(d, 0) for d in LAYER_DIMS[DimLayer.A])

    # C层综合评分 (趋势判断准确度)
    c_score = sum(dimensions.get(d, 75) * DIM_WEIGHTS.get(d, 0) for d in LAYER_DIMS[DimLayer.C])
    c_score /= sum(DIM_WEIGHTS.get(d, 0) for d in LAYER_DIMS[DimLayer.C])

    # 市场情绪系数 (fear_greed 0-100 → 0.5-1.5)
    fg_factor = 0.5 + (fear_greed / 100.0)

    # RSI系数 (RSI 0-100 → 0.5-1.5, RSI=50为中心)
    if rsi >= 50:
        rsi_factor = 0.5 + (rsi / 100.0)
    else:
        rsi_factor = 0.5 + (rsi / 100.0) - ((50 - rsi) / 100.0)

    # 波动率调整 (regime)
    vol_factor = {"bull": 1.10, "bear": 0.90, "neutral": 1.00, "volatile": 0.80}.get(regime, 1.00)

    # Mi = 加权组合评分 × 情绪 × RSI × 波动率
    composite = (a_score * 0.4 + c_score * 0.6) / 100.0
    mi = composite * fg_factor * rsi_factor * vol_factor
    mi = max(0.5, min(1.35, mi))
    return round(mi, 4)

def compute_layer_scores(dimensions: Dict[str, float]) -> Dict[str, float]:
    """计算各层综合评分"""
    result = {}
    for layer, dims in LAYER_DIMS.items():
        total_weight = sum(DIM_WEIGHTS.get(d, 0) for d in dims)
        if total_weight > 0:
            score = sum(dimensions.get(d, 75) * DIM_WEIGHTS.get(d, 0) for d in dims) / total_weight
            result[layer.value] = round(score, 2)
    return result

def compute_overall_score(dimensions: Dict[str, float]) -> float:
    """计算平台综合评分 (0-100)"""
    total = sum(dimensions.get(d, 75) * w for d, w in DIM_WEIGHTS.items())
    total_w = sum(DIM_WEIGHTS.values())
    return round(total / total_w, 2)

def update_strategy_weight(strategy: str, outcome: str, confidence: float):
    """
    Kelly Criterion 权重更新
    WIN  → 权重 += confidence * 0.05
    LOSS → 权重 -= confidence * 0.05
    然后归一化
    """
    s = state.strategy_scores[strategy]
    if outcome == "WIN":
        s["wins"] += 1
        s["streak"] = s["streak"] + 1 if s["last"] == "WIN" else 1
    else:
        s["losses"] += 1
        s["streak"] = s["streak"] - 1 if s["last"] == "LOSS" else -1
    s["last"] = outcome
    s["history"].append({"outcome": outcome, "confidence": confidence, "ts": datetime.now().isoformat()})

    # Kelly权重调整
    delta = confidence * 0.05 if outcome == "WIN" else -confidence * 0.05
    if state.strategy_scores[strategy]["streak"] >= 3:
        delta *= 1.5  # 连胜/连败加强
    elif state.strategy_scores[strategy]["streak"] <= -3:
        delta *= 1.5

    state.strategy_weights[strategy] = max(0.05, min(0.70, state.strategy_weights.get(strategy, 0.4) + delta))

    # 归一化
    total = sum(state.strategy_weights.values())
    for k in state.strategy_weights:
        state.strategy_weights[k] = round(state.strategy_weights[k] / total, 4)

def update_agent_weight(agent: str, outcome: str):
    """更新agent权重 (基于WIN/LOSS)"""
    delta = 0.02 if outcome == "WIN" else -0.02
    state.agent_weights[agent] = max(0.01, min(0.40, state.agent_weights.get(agent, 0.1) + delta))
    total = sum(state.agent_weights.values())
    for k in state.agent_weights:
        state.agent_weights[k] = round(state.agent_weights[k] / total, 4)

def kelly_allocation(request: PortfolioAllocationRequest) -> Dict:
    """
    Kelly Criterion 组合配置
    基于三个信号源的置信度和方向计算最优配置
    """
    strategies = [
        {"name": "vv6", "conf": request.vv6_confidence, "dir": request.vv6_direction},
        {"name": "v15", "conf": request.v15_confidence, "dir": request.v15_direction},
        {"name": "coordinator", "conf": request.coordinator_confidence, "dir": request.coordinator_direction},
    ]

    # Kelly fractions: f = W - (1-W)/R
    # W = win rate, R = win/loss ratio (假设1.5)
    total_kelly = {}
    for s in strategies:
        conf = s["conf"] / 100.0
        # Kelly fraction based on confidence
        k = max(0, min(0.20, conf * 0.25))
        total_kelly[s["name"]] = k

    # 方向一致性加成
    directions = [s["dir"] for s in strategies if s["dir"] != "hold"]
    if len(directions) >= 2 and len(set(directions)) == 1:
        for s in strategies:
            if s["dir"] == directions[0]:
                total_kelly[s["name"]] *= 1.5

    # 归一化
    total = sum(total_kelly.values())
    if total > 0:
        for k in total_kelly:
            total_kelly[k] = round(total_kelly[k] / total, 4)

    # 最终配置
    regime_factor = {"bull": 1.2, "bear": 0.8, "neutral": 1.0, "volatile": 0.6}.get(request.regime, 1.0)
    allocations = {}
    for name, kelly in total_kelly.items():
        alloc = kelly * regime_factor
        allocations[name] = {
            "kelly_fraction": kelly,
            "allocation": round(alloc * 100, 1),
            "position_pct": round(min(alloc * 100, 60.0), 1),
        }

    return allocations

# ─── API端点 ────────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "name": "MiroFish Platform Engine",
        "version": "1.0.0",
        "role": "Platform-level 25D arbitration + Portfolio optimization",
        "endpoints": [
            "GET  /health             - 健康检查",
            "GET  /dimensions         - 25维评分",
            "POST /dimensions/update  - 更新维度评分",
            "GET  /mi                 - 计算Mi",
            "POST /mi                 - 计算Mi (带参数)",
            "GET  /layer-scores       - 各层评分",
            "POST /arbitrate          - vv6 vs v15 仲裁",
            "GET  /strategy-weights   - 策略权重",
            "POST /strategy-weights   - 更新策略权重",
            "GET  /agent-weights      - Agent权重",
            "POST /agent-weights      - 更新Agent权重",
            "POST /portfolio/allocate - Kelly组合配置",
            "GET  /history            - 历史记录",
        ]
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "uptime": datetime.now().isoformat(),
        "request_count": state.request_count,
        "strategy_weights": state.strategy_weights,
        "overall_score": compute_overall_score(state.dimensions),
    }

def _ensure_dimensions_loaded():
    """首次访问时从v7懒加载维度数据"""
    if not state._dimensions_loaded:
        state.refresh_dimensions_from_market()
        state._dimensions_loaded = True

@app.get("/dimensions")
def get_dimensions():
    _ensure_dimensions_loaded()
    """获取所有25维当前评分"""
    return {
        "dimensions": state.dimensions,
        "weights": DIM_WEIGHTS,
        "overall_score": compute_overall_score(state.dimensions),
        "layer_scores": compute_layer_scores(state.dimensions),
    }

@app.post("/dimensions/update")
def update_dimension(update: ScoreUpdate):
    """更新指定维度评分"""
    if update.dimension not in DIM_WEIGHTS:
        raise HTTPException(status_code=400, detail=f"Unknown dimension: {update.dimension}")
    if not 0 <= update.score <= 100:
        raise HTTPException(status_code=400, detail="Score must be 0-100")
    old = state.dimensions.get(update.dimension, 75)
    state.dimensions[update.dimension] = update.score
    mi = compute_mi(state.dimensions, "neutral", 50, 50)
    state.mi_history.append({
        "dim": update.dimension,
        "old": old,
        "new": update.score,
        "mi": mi,
        "source": update.source,
        "ts": datetime.now().isoformat()
    })
    return {
        "dimension": update.dimension,
        "old": old,
        "new": update.score,
        "mi": mi,
        "overall_score": compute_overall_score(state.dimensions),
    }

@app.get("/mi")
def get_mi(regime: str = "neutral", rsi: float = 50.0, fear_greed: float = 50.0):
    """计算当前Mi值"""
    mi = compute_mi(state.dimensions, regime, rsi, fear_greed)
    return {
        "mi": mi,
        "regime": regime,
        "rsi": rsi,
        "fear_greed": fear_greed,
        "layer_scores": compute_layer_scores(state.dimensions),
        "dimensions": state.dimensions,
    }

@app.post("/mi")
def calc_mi(req: dict):
    """计算Mi (POST版本)"""
    regime = req.get("regime", "neutral")
    rsi = req.get("rsi", 50.0)
    fg = req.get("fear_greed", 50.0)
    overrides = req.get("dimension_overrides", {})
    dims = {**state.dimensions, **overrides}
    mi = compute_mi(dims, regime, rsi, fg)
    return {"mi": mi, "regime": regime, "rsi": rsi, "fear_greed": fg}

@app.get("/layer-scores")
def get_layer_scores():
    """获取各层评分"""
    layer_scores = compute_layer_scores(state.dimensions)
    result = {}
    for layer, score in layer_scores.items():
        dims = LAYER_DIMS[DimLayer(layer)]
        result[layer] = {
            "score": score,
            "weight": LAYER_WEIGHTS[DimLayer(layer)],
            "dimensions": {d: {"score": state.dimensions.get(d, 75), "weight": DIM_WEIGHTS.get(d, 0)} for d in dims}
        }
    return result

@app.post("/arbitrate")
def arbitrate(req: ArbitrationRequest):
    """
    vv6 vs v15 信号仲裁
    ========================
    输入: vv6_signal, v15_signal, regime, rsi, fear_greed
    输出: 仲裁决策 + Mi + 推荐策略权重
    """
    vv6 = req.vv6_signal
    v15 = req.v15_signal
    regime = req.regime
    rsi = req.rsi
    fg = req.fear_greed
    mi = compute_mi(state.dimensions, regime, rsi, fg)

    vv6_dir = vv6.get("direction", "hold")
    vv6_conf = vv6.get("confidence", 0)
    v15_dir = v15.get("direction", "hold")
    v15_conf = v15.get("confidence", 0)

    # 仲裁决策
    if vv6_dir == v15_dir and vv6_dir != "hold":
        winner = "vv6" if vv6_conf >= v15_conf else "v15"
        decision = "AGREE"
        final_dir = vv6_dir
        final_conf = max(vv6_conf, v15_conf)
        reasoning = f"双方一致({final_dir}), 置信度{final_conf:.1f}%"
    elif vv6_dir == v15_dir and vv6_dir == "hold":
        winner = "tie"
        decision = "HOLD"
        final_dir = "hold"
        final_conf = 0
        reasoning = "双方均观望"
    else:
        # 方向不一致
        diff = abs(vv6_conf - v15_conf)
        if diff >= 15:
            winner = "vv6" if vv6_conf > v15_conf else "v15"
            decision = "PREFER_HIGHER_CONF"
            final_dir = vv6_dir if vv6_conf > v15_conf else v15_dir
            final_conf = max(vv6_conf, v15_conf)
            reasoning = f"置信度差异{diff:.1f}%, 采纳{winner}({final_dir})"
        else:
            # 差异不够大 → 参考Mi和Kelly权重
            winner = "mi_kelly"
            decision = "USE_MI_KELLY"
            # 方向: 跟随vv6 (更保守) 除非v15极端信号
            if v15_conf >= 85:
                final_dir = v15_dir
                final_conf = v15_conf
            else:
                final_dir = vv6_dir
                final_conf = vv6_conf
            reasoning = f"分歧+Mi仲裁 → {final_dir}({final_conf:.1f}%)"

    result = {
        "decision": decision,
        "winner": winner,
        "final_direction": final_dir,
        "final_confidence": final_conf,
        "mi": mi,
        "reasoning": reasoning,
        "vv6": {"direction": vv6_dir, "confidence": vv6_conf},
        "v15": {"direction": v15_dir, "confidence": v15_conf},
        "regime": regime,
        "rsi": rsi,
        "fear_greed": fg,
        "strategy_weights": state.strategy_weights,
        "timestamp": datetime.now().isoformat(),
    }

    state.arbitration_history.append(result)
    state.request_count += 1
    return result

@app.get("/strategy-weights")
def get_strategy_weights():
    """获取当前策略权重"""
    scores = {}
    for name, s in state.strategy_scores.items():
        total = s["wins"] + s["losses"]
        wr = s["wins"] / total * 100 if total > 0 else 0
        scores[name] = {
            "wins": s["wins"],
            "losses": s["losses"],
            "win_rate": round(wr, 1),
            "streak": s["streak"],
            "last": s["last"],
            "weight": state.strategy_weights.get(name, 0.4),
        }
    return {
        "weights": state.strategy_weights,
        "scores": scores,
    }

@app.post("/strategy-weights")
def update_sw(update: StrategyWeightUpdate):
    """更新策略表现 (WIN/LOSS)"""
    if update.strategy not in state.strategy_weights:
        raise HTTPException(status_code=400, detail=f"Unknown strategy: {update.strategy}")
    old_w = state.strategy_weights.get(update.strategy, 0.4)
    update_strategy_weight(update.strategy, update.outcome, update.confidence)
    new_w = state.strategy_weights.get(update.strategy, 0.4)
    return {
        "strategy": update.strategy,
        "outcome": update.outcome,
        "weight_before": old_w,
        "weight_after": new_w,
        "all_weights": state.strategy_weights,
    }

@app.get("/agent-weights")
def get_agent_weights():
    """获取当前Agent权重"""
    return {
        "weights": state.agent_weights,
        "normalized": {k: round(v / sum(state.agent_weights.values()), 4) for k, v in state.agent_weights.items()},
    }

@app.post("/agent-weights")
def update_aw(req: dict):
    """更新Agent权重"""
    agent = req.get("agent")
    outcome = req.get("outcome")
    if not agent or agent not in state.agent_weights:
        raise HTTPException(status_code=400, detail=f"Unknown agent")
    old = state.agent_weights[agent]
    update_agent_weight(agent, outcome)
    return {
        "agent": agent,
        "outcome": outcome,
        "weight_before": old,
        "weight_after": state.agent_weights[agent],
        "all_weights": state.agent_weights,
    }

@app.post("/portfolio/allocate")
def portfolio_allocate(req: PortfolioAllocationRequest):
    """Kelly组合配置"""
    alloc = kelly_allocation(req)
    mi = compute_mi(state.dimensions, req.regime, req.rsi, req.fear_greed)
    return {
        "allocations": alloc,
        "mi": mi,
        "regime": req.regime,
        "total_allocation": round(sum(a["allocation"] for a in alloc.values()), 1),
        "strategy_weights": state.strategy_weights,
    }

@app.get("/history")
def get_history(limit: int = 20):
    """获取历史记录"""
    return {
        "mi_history": state.mi_history[-limit:],
        "arbitration_history": state.arbitration_history[-limit:],
    }

# ═══════════════════════════════════════════════════════════════════
# v15.2 核心: 1000-Agent群体智能 + 实时学习 + 三方仲裁自动化
# ═══════════════════════════════════════════════════════════════════

import asyncio
import random
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional
import time

# ─── 1000-Agent 虚拟群体智能 ────────────────────────────────────

@dataclass
class VirtualAgent:
    """单个虚拟交易Agent"""
    agent_id: int
    archetype: str           # trend_chaser | mean_reversion | breakout | event_driven | macro | onchain | sentiment
    personality: float       # 0.0-1.0 (保守-激进)
    accuracy_estimate: float # 该Agent历史预估准确率 0.5-0.9
    bias: str               # bullish | bearish | neutral
    vote_history: list = field(default_factory=list)  # [(timestamp, vote, outcome)]
    
    def vote(self, market_state: dict) -> float:
        """返回 -1.0 到 1.0 的信号"""
        fear = market_state.get("fear_greed", 50) / 100.0
        trend = market_state.get("trend_score", 0.5)
        rsi = market_state.get("rsi", 50) / 100.0
        
        base = {
            "trend_chaser":    0.3 * trend + 0.2 * rsi + 0.2 * (1 - fear) + 0.3 * self.personality,
            "mean_reversion":  0.4 * (1 - rsi) + 0.3 * (1 - fear) + 0.2 * trend + 0.1,
            "breakout":       0.5 * trend + 0.3 * rsi + 0.2 * self.personality,
            "event_driven":   0.4 * fear + 0.3 * trend + 0.2 * rsi + 0.1,
            "macro":          0.5 * trend + 0.3 * (1 - fear) + 0.2 * self.personality,
            "onchain":       0.4 * trend + 0.3 * rsi + 0.2 * fear + 0.1 * self.personality,
            "sentiment":      0.5 * fear + 0.3 * trend + 0.2 * self.personality,
        }.get(self.archetype, 0.5)
        
        # Bias adjustment
        if self.bias == "bullish": base = min(1.0, base + 0.1)
        elif self.bias == "bearish": base = max(0.0, base - 0.1)
        
        # Add personality-driven noise (±10%)
        noise = (random.random() - 0.5) * 0.1 * (1 - self.accuracy_estimate)
        return max(-1.0, min(1.0, base * 2 - 1 + noise))

class VirtualAgentPool:
    """1000个虚拟Agent的群体智能池"""
    
    ARCHETYPES = {
        "trend_chaser":   200,
        "mean_reversion": 200,
        "breakout":       150,
        "event_driven":   150,
        "macro":          100,
        "onchain":        100,
        "sentiment":      100,
    }
    
    def __init__(self, n_agents: int = 1000):
        self.n = n_agents
        self.agents: list[VirtualAgent] = []
        self.epoch_count = 0  # 群体学习轮次
        self._init_agents()
        self._seed_from_market()  # 从真实市场数据初始化

    def _seed_from_market(self):
        """从v6a API获取真实市场状态,提升初始准确率"""
        try:
            import urllib.request, json as _json
            req = urllib.request.Request(
                "http://localhost:8000/api/v7/market/summary",
                headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = _json.loads(resp.read()).get("data", {})
            fg = float(data.get("fear_greed_index", 50))
            trend = data.get("trend", "neutral")
            
            # 根据市场状态调整初始准确率
            market_bias = 1.0
            if fg > 65:  # 贪婪牛市
                for a in self.agents:
                    if a.archetype in ("trend_chaser", "breakout"):
                        a.accuracy_estimate = min(0.92, a.accuracy_estimate * 1.1)
                    elif a.archetype == "mean_reversion":
                        a.accuracy_estimate = min(0.85, a.accuracy_estimate * 0.95)
            elif fg < 35:  # 恐惧熊市
                for a in self.agents:
                    if a.archetype in ("mean_reversion", "sentiment"):
                        a.accuracy_estimate = min(0.92, a.accuracy_estimate * 1.1)
                    elif a.archetype == "trend_chaser":
                        a.accuracy_estimate = min(0.85, a.accuracy_estimate * 0.95)
            
            avg = sum(a.accuracy_estimate for a in self.agents) / self.n
            print(f"1000-Agent seeded with market data: fg={fg}, trend={trend}, avg_acc={avg:.4f}")
        except Exception as e:
            print(f"1000-Agent market seed failed: {e}")

    def self_improve(self, market_outcome: int) -> dict:
        """
        群体自我改进: 基于市场结果自动提升准确率
        market_outcome: 1=市场上涨, -1=市场下跌, 0=横盘
        """
        self.epoch_count += 1
        improvements = defaultdict(list)
        
        for a in self.agents:
            old_acc = a.accuracy_estimate
            
            # 检查该Agent的方向与市场是否一致
            bias_signal = {"bullish": 1, "bearish": -1, "neutral": 0}.get(a.bias, 0)
            correct_prediction = bias_signal == market_outcome or (bias_signal == 0 and market_outcome == 0)
            
            if correct_prediction:
                # 正确: +0.5%准确率
                a.accuracy_estimate = min(0.95, a.accuracy_estimate * (1 + 0.005))
            else:
                # 错误: -0.2%准确率  
                a.accuracy_estimate = max(0.50, a.accuracy_estimate * (1 - 0.002))
            
            improvements[a.archetype].append(a.accuracy_estimate - old_acc)
        
        avg_by_arch = {}
        for arch, deltas in improvements.items():
            avg_by_arch[arch] = round(sum(deltas)/len(deltas), 5)
        
        return {
            "epoch": self.epoch_count,
            "avg_accuracy": round(sum(a.accuracy_estimate for a in self.agents) / self.n, 4),
            "improvements_by_archetype": avg_by_arch,
        }
        
    def _init_agents(self):
        self.agents = []
        agent_id = 0
        for archetype, count in self.ARCHETYPES.items():
            for _ in range(count):
                self.agents.append(VirtualAgent(
                    agent_id=agent_id,
                    archetype=archetype,
                    personality=random.random(),  # 0.0-1.0
                    accuracy_estimate=0.55 + random.random() * 0.35,  # 0.55-0.90
                    bias=random.choice(["bullish", "bearish", "neutral"]),
                ))
                agent_id += 1
        random.shuffle(self.agents)
    
    def aggregate_vote(self, market_state: dict) -> dict:
        """1000个Agent投票 → 聚合信号 + 信心度"""
        votes = [a.vote(market_state) for a in self.agents]
        # Weighted by accuracy
        weighted_votes = [v * a.accuracy_estimate for v, a in zip(votes, self.agents)]
        raw_signal = sum(weighted_votes) / sum(a.accuracy_estimate for a in self.agents)
        
        # Confidence: how many agents agree
        signal = 1 if raw_signal > 0.1 else (-1 if raw_signal < -0.1 else 0)
        agreement = sum(1 for v in votes if (v > 0.1 and signal == 1) or (v < -0.1 and signal == -1) or (abs(v) <= 0.1 and signal == 0)) / self.n
        
        # σ异常值剔除
        mean_v = sum(votes) / len(votes)
        std_v = (sum((v - mean_v)**2 for v in votes) / len(votes)) ** 0.5
        filtered = [v for v in votes if abs(v - mean_v) <= 2 * std_v]
        filtered_signal = sum(filtered) / len(filtered) if filtered else 0
        
        return {
            "signal": 1 if filtered_signal > 0.05 else (-1 if filtered_signal < -0.05 else 0),
            "confidence": round(min(1.0, agreement * 1.2), 4),
            "raw_signal": round(filtered_signal, 4),
            "n_agents": self.n,
            "fear_greed_weighted": round(sum(v * a.accuracy_estimate for v, a in zip(votes, self.agents)) / sum(a.accuracy_estimate for a in self.agents), 4),
        }
    
    def update_dimension_scores(self, trade_outcome: dict, platform_state) -> dict:
        """根据交易结果更新各维度的预估准确率 → 驱动25维评分"""
        outcome_correct = getattr(trade_outcome, "correct", False)
        confidence = getattr(trade_outcome, "confidence", 0.5)
        regime = getattr(trade_outcome, "regime", "neutral")
        
        # Archetype → Dimension 映射
        arch_to_dims = {
            "trend_chaser":   ["C1_sonar", "A1_position"],
            "mean_reversion": ["C2_prediction", "D3_strategy"],
            "breakout":       ["C1_sonar"],
            "event_driven":   ["C4_sentiment"],
            "macro":          ["A1_position", "B1_rabbit"],
            "onchain":        ["D1_data"],
            "sentiment":      ["C4_sentiment"],
        }
        
        dim_adjustments = defaultdict(float)
        
        for agent in self.agents:
            correct = outcome_correct and random.random() < agent.accuracy_estimate
            delta = 0.02 if correct else -0.01
            agent.accuracy_estimate = max(0.50, min(0.95, agent.accuracy_estimate + delta))
            
            # Update relevant dimensions
            for dim in arch_to_dims.get(agent.archetype, []):
                dim_adjustments[dim] += delta * confidence
        
        # Apply adjustments to platform dimensions
        new_scores = {}
        for dim, adj in dim_adjustments.items():
            if dim in platform_state.dimensions:
                old = platform_state.dimensions[dim]
                platform_state.dimensions[dim] = max(50, min(100, old + adj * 10))
                new_scores[dim] = round(platform_state.dimensions[dim], 2)
        
        return new_scores

# ─── 全局1000-Agent池 ──────────────────────────────────────────
_agent_pool: Optional[VirtualAgentPool] = None

def get_agent_pool() -> VirtualAgentPool:
    global _agent_pool
    if _agent_pool is None:
        _agent_pool = VirtualAgentPool(n_agents=1000)
    return _agent_pool


# ─── 实时学习: 交易记录 → 维度更新 ─────────────────────────────

@dataclass
class TradeRecord:
    timestamp: str
    symbol: str
    direction: str      # LONG | SHORT | HOLD
    entry_price: float
    exit_price: Optional[float]
    outcome: str        # WIN | LOSS | PENDING
    pnl_pct: float
    regime: str
    confidence: float
    agents_voted: dict  # {"trend_chaser": 0.8, ...}
    dimensions_before: dict  # 交易前的维度评分
    correct: bool = False

_trade_history: list[TradeRecord] = []
_dim_learning_rates: dict[str, float] = {d: 0.01 for d in DIM_WEIGHTS}
_DIM_ACCURACY: dict[str, float] = {d: 0.5 for d in DIM_WEIGHTS}  # 维度预估准确率

def learn_from_trade(trade: TradeRecord) -> dict:
    """根据交易结果学习，更新维度评分和学习率"""
    global _DIM_ACCURACY, _dim_learning_rates
    
    corrections = {}
    for dim, score in trade.dimensions_before.items():
        if dim not in DIM_WEIGHTS:
            continue
        
        # 判断该维度对本次交易正确性的贡献
        dim_weight = DIM_WEIGHTS[dim]
        # 高分维度: 如果交易正确，略微增强；如果错误，略微减弱
        current_acc = _DIM_ACCURACY.get(dim, 0.5)
        
        if trade.outcome == "WIN":
            # 胜率提升 → 增强该维度权重
            improvement = dim_weight * 0.05 * trade.confidence
            _DIM_ACCURACY[dim] = min(0.95, current_acc + improvement)
            corrections[dim] = f"+{improvement:.4f}"
        elif trade.outcome == "LOSS":
            # 亏损 → 降低维度权重
            degradation = dim_weight * 0.03 * trade.confidence
            _DIM_ACCURACY[dim] = max(0.30, current_acc - degradation)
            corrections[dim] = f"-{degradation:.4f}"
        
        # 更新平台state的dimensions
        if dim in state.dimensions:
            old = state.dimensions[dim]
            acc_delta = (_DIM_ACCURACY[dim] - 0.5) * 2  # 0→-1, 0.5→0, 0.95→+0.9
            state.dimensions[dim] = max(50, min(100, 75 + acc_delta * 12.5))
    
    return corrections




@app.get("/agents/self-improve")
def agent_self_improve():
    """
    群体自我改进: 基于当前市场状态触发一次自我优化
    自动判断市场方向,让正确方向的Agent提升准确率
    """
    pool = get_agent_pool()
    
    # 从v6a判断市场方向
    try:
        import urllib.request, json as _json
        req = urllib.request.Request(
            "http://localhost:8000/api/v7/market/summary",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = _json.loads(resp.read()).get("data", {})
        fg = float(data.get("fear_greed_index", 50))
        trend = data.get("trend", "neutral")
        
        # 判断市场方向: fear>55+trend up → 上涨, fear<45+trend down → 下跌
        if fg > 55 or trend in ("up", "bullish"):
            market_outcome = 1
        elif fg < 45 or trend in ("down", "bearish"):
            market_outcome = -1
        else:
            market_outcome = 0
    except Exception:
        market_outcome = 0
    
    result = pool.self_improve(market_outcome)
    return result

# ─── v15.2 API Endpoints ───────────────────────────────────────

@app.get("/agents/pool")
def get_agent_pool_status():
    """1000-Agent池状态"""
    pool = get_agent_pool()
    by_archetype = defaultdict(int)
    for a in pool.agents:
        by_archetype[a.archetype] += 1
    return {
        "n_agents": pool.n,
        "by_archetype": dict(by_archetype),
        "avg_personality": round(sum(a.personality for a in pool.agents) / pool.n, 3),
        "avg_accuracy": round(sum(a.accuracy_estimate for a in pool.agents) / pool.n, 4),
    }

@app.post("/agents/vote")
def agent_pool_vote(market_state: dict = {}):
    """1000-Agent投票 → 聚合信号"""
    pool = get_agent_pool()
    state_defaults = {
        "fear_greed": 50,
        "trend_score": 0.5,
        "rsi": 50,
    }
    state_defaults.update(market_state)
    result = pool.aggregate_vote(state_defaults)
    return result

@app.post("/agents/learn")
def agent_learn_from_trade(trade: dict):
    """记录交易结果 → 1000-Agent学习 → 维度更新"""
    pool = get_agent_pool()
    
    # 构建TradeRecord
    trade_record = TradeRecord(
        timestamp=trade.get("timestamp", datetime.now().isoformat()),
        symbol=trade.get("symbol", "BTCUSDT"),
        direction=trade.get("direction", "LONG"),
        entry_price=trade.get("entry_price", 0),
        exit_price=trade.get("exit_price"),
        outcome=trade.get("outcome", "PENDING"),
        pnl_pct=trade.get("pnl_pct", 0.0),
        regime=trade.get("regime", "neutral"),
        confidence=trade.get("confidence", 0.5),
        agents_voted=trade.get("agents_voted", {}),
        dimensions_before=trade.get("dimensions_before", state.dimensions.copy()),
        correct=(trade.get("outcome") == "WIN"),
    )
    
    _trade_history.append(trade_record)
    
    # 学习更新
    corrections = learn_from_trade(trade_record)
    dim_updates = pool.update_dimension_scores(trade_record, state)
    
    return {
        "recorded": True,
        "trade_count": len(_trade_history),
        "dimension_corrections": corrections,
        "agent_pool_updates": dim_updates,
        "current_dimensions": {k: round(v, 2) for k, v in state.dimensions.items()},
    }

@app.get("/agents/history")
def get_trade_history(limit: int = 20):
    """最近的交易学习历史"""
    hist = _trade_history[-limit:]
    return {
        "count": len(hist),
        "recent": [
            {
                "timestamp": t.timestamp,
                "symbol": t.symbol,
                "direction": t.direction,
                "outcome": t.outcome,
                "pnl_pct": t.pnl_pct,
                "regime": t.regime,
                "confidence": t.confidence,
            } for t in hist
        ],
    }

@app.get("/dimensions/learning")
def get_learning_state():
    """维度学习状态 (准确率 + 学习率)"""
    return {
        "dimension_accuracy": {k: round(v, 4) for k, v in _DIM_ACCURACY.items()},
        "learning_rates": _dim_learning_rates,
        "total_trades_learned": len(_trade_history),
    }

# ─── 三方仲裁自动化 ─────────────────────────────────────────────

@dataclass
class ArbitrationSignal:
    source: str        # vv6 | v15 | coordinator
    direction: str     # LONG | SHORT | HOLD
    confidence: float # 0.0-1.0
    mi: float
    timestamp: str

_cross_platform_signals: dict[str, ArbitrationSignal] = {}
_auto_arbitration_enabled: bool = False

@app.post("/arbitration/push")
def push_arbitration_signal(signal: dict):
    """接收 vv6 或 v15 的信号推送到仲裁池"""
    source = signal.get("source", "unknown")
    sig = ArbitrationSignal(
        source=source,
        direction=signal.get("direction", "HOLD"),
        confidence=signal.get("confidence", 0.5),
        mi=signal.get("mi", 0.75),
        timestamp=datetime.now().isoformat(),
    )
    _cross_platform_signals[source] = sig
    return {"received": True, "source": source, "signals_count": len(_cross_platform_signals)}

@app.get("/arbitration/decide")
def arbitration_decide():
    """三方信号仲裁 → 最终决策"""
    if len(_cross_platform_signals) < 2:
        return {"status": "insufficient_signals", "signals": {k: {"direction": v.direction, "conf": v.confidence} for k, v in _cross_platform_signals.items()}}
    
    # 投票机制
    votes = {}
    for source, sig in _cross_platform_signals.items():
        dir_key = sig.direction.upper()
        if dir_key not in votes:
            votes[dir_key] = []
        # 置信度 × MI 作为权重
        weighted_conf = sig.confidence * sig.mi
        votes[dir_key].append((source, weighted_conf, sig.confidence))
    
    # 找最高权重方向
    best_dir = max(votes.keys(), key=lambda d: sum(w for _, w, _ in votes[d]))
    total_weight = sum(w for _, w, _ in votes[best_dir])
    avg_conf = sum(c for _, _, c in votes[best_dir]) / len(votes[best_dir])
    
    return {
        "decision": best_dir,
        "confidence": round(avg_conf, 4),
        "weighted_evidence": round(total_weight, 4),
        "signal_breakdown": {d: [(s, round(w, 4), round(c, 4)) for s, w, c in sources] for d, sources in votes.items()},
        "all_signals": {k: {"direction": v.direction, "conf": v.confidence, "mi": v.mi} for k, v in _cross_platform_signals.items()},
        "sources_agreeing": [s for s, w, _ in votes[best_dir]],
    }

@app.post("/arbitration/enable")
def enable_auto_arbitration(enabled: bool = True):
    """启用/禁用自动仲裁"""
    global _auto_arbitration_enabled
    _auto_arbitration_enabled = enabled
    return {"auto_arbitration": enabled}

@app.get("/arbitration/status")
def get_arbitration_status():
    return {
        "auto_enabled": _auto_arbitration_enabled,
        "signals": {k: {"direction": v.direction, "conf": round(v.confidence, 4), "mi": round(v.mi, 4), "age": v.timestamp} for k, v in _cross_platform_signals.items()},
        "all_signals_count": len(_cross_platform_signals),
    }


# ═══════════════════════════════════════════════════════════════════
# HERMES加强: MiroFish Platform v15.3 - 学习闭环 + Mi同步 + 交易闭环
# ═══════════════════════════════════════════════════════════════════

# ─── Pydantic模型 (补充) ───────────────────────────────────────

class TradeExecution(BaseModel):
    symbol: str = "BTCUSDT"
    direction: str  # LONG | SHORT
    entry_price: float
    quantity: float = 0.001
    confidence: float = 0.5
    regime: str = "neutral"

class MiSyncRequest(BaseModel):
    target_mi: float
    reason: str = ""

# ─── 全局状态 (补充) ───────────────────────────────────────────

_trade_journal: list = []  # 交易流水账
_persistence_file = "/tmp/mirofish_platform_state.json"

def _save_state():
    """持久化平台状态到磁盘"""
    try:
        import json
        state_data = {
            "dimensions": state.dimensions,
            "strategy_weights": state.strategy_weights,
            "agent_weights": state.agent_weights,
            "strategy_scores": state.strategy_scores,
            "trade_journal": _trade_journal[-100:],  # 只保留最近100条
            "epoch_count": getattr(state, 'epoch_count', 0),
        }
        with open(_persistence_file, 'w') as f:
            json.dump(state_data, f)
    except Exception:
        pass

def _load_state():
    """从磁盘加载平台状态"""
    try:
        import json
        with open(_persistence_file, 'r') as f:
            data = json.load(f)
        state.dimensions.update(data.get("dimensions", {}))
        state.strategy_weights.update(data.get("strategy_weights", {}))
        state.agent_weights.update(data.get("agent_weights", {}))
        state.strategy_scores.update(data.get("strategy_scores", {}))
        _trade_journal.extend(data.get("trade_journal", []))
        if hasattr(state, 'epoch_count') and 'epoch_count' in data:
            state.epoch_count = data['epoch_count']
    except Exception:
        pass

# 启动时加载状态
import threading
def _delayed_load():
    t = threading.Timer(2.0, _load_state)
    t.daemon = True
    t.start()

# ─── 改进的市场方向判断 ────────────────────────────────────────

def _detect_market_direction() -> int:
    """
    综合判断市场方向 (改进版)
    返回: 1=上涨, -1=下跌, 0=横盘
    """
    try:
        import urllib.request, json as _json
        req = urllib.request.Request(
            "http://localhost:8000/api/v7/market/summary",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = _json.loads(resp.read()).get("data", {})
        
        fg = float(data.get("fear_greed_index", 50))
        trend = data.get("trend", "neutral")
        top_gainers = data.get("top_gainers", [])
        
        # 多信号融合判断
        signals = 0
        
        # 信号1: fear_greed
        if fg > 58: signals += 1
        elif fg < 42: signals -= 1
        
        # 信号2: trend
        if trend in ("up", "bullish"): signals += 1
        elif trend in ("down", "bearish"): signals -= 1
        
        # 信号3: top gainers强度
        if top_gainers:
            avg_change = sum(g.get("change", 0) for g in top_gainers[:3]) / min(3, len(top_gainers))
            if avg_change > 3: signals += 1
            elif avg_change < -3: signals -= 1
        
        if signals >= 1: return 1
        elif signals <= -1: return -1
        else: return 0
    except Exception:
        return 0

# ─── Mi全局同步 ────────────────────────────────────────────────

@app.get("/mi/sync")
def sync_mi():
    """
    返回统一的Mi供所有系统使用 (解决Mi不一致问题)
    原理: v6i/v15/Platform应共享同一个Mi基准
    """
    try:
        import urllib.request, json as _json
        req = urllib.request.Request(
            "http://localhost:8000/api/v7/market/summary",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = _json.loads(resp.read()).get("data", {})
        fg = float(data.get("fear_greed_index", 50))
        trend = data.get("trend", "neutral")
    except Exception:
        fg, trend = 50, "neutral"
    
    # 统一用state.dimensions计算Mi
    _ensure_dimensions_loaded()
    unified_mi = compute_mi(state.dimensions, "neutral", 50.0, fg)
    
    return {
        "unified_mi": round(unified_mi, 4),
        "fear_greed": fg,
        "trend": trend,
        "dimensions_source": "state.dimensions",
        "note": "所有系统(v6i/v15/Platform)应使用此统一Mi",
    }

@app.post("/mi/feed")
def feed_mi_to_consumer(data: MiSyncRequest):
    """
    接收外部系统(如v15)的Mi进行校验和反馈
    """
    _ensure_dimensions_loaded()
    local_mi = compute_mi(state.dimensions, "neutral", 50.0, 50.0)
    
    return {
        "received_mi": data.target_mi,
        "local_mi": round(local_mi, 4),
        "delta": round(data.target_mi - local_mi, 4),
        "feedback": "mi_higher" if data.target_mi > local_mi else "mi_lower" if data.target_mi < local_mi else "aligned",
    }

# ─── 模拟交易执行 + 学习闭环 ───────────────────────────────────

@app.post("/trade/simulate")
def simulate_trade(trade: TradeExecution):
    """
    模拟交易执行 → 计算盈亏 → 更新1000-Agent + 维度评分
    
    这实现了Hermes学习闭环:
    signal → trade → outcome → learn → improved_signal
    """
    import random
    from datetime import datetime
    
    _ensure_dimensions_loaded()
    
    # 计算模拟盈亏 (基于市场方向 + 随机因素)
    market_outcome = _detect_market_direction()
    market_correct = (trade.direction == "LONG" and market_outcome == 1) or \
                     (trade.direction == "SHORT" and market_outcome == -1) or \
                     (market_outcome == 0)  # 横盘 = 中立赌注
    
    # 添加随机因素模拟真实交易 (70%市场相关, 30%随机)
    market_weight = 0.7
    luck = random.random()  # 0-1
    win_probability = market_weight * (1.0 if market_correct else 0.0) + (1 - market_weight) * luck
    outcome_win = random.random() < win_probability
    
    if trade.direction == "LONG":
        pnl_pct = round((random.uniform(0.5, 4.0) if outcome_win else -random.uniform(0.5, 3.0)), 3)
    else:
        pnl_pct = round((-random.uniform(0.5, 4.0) if outcome_win else random.uniform(0.5, 3.0)) * 0.8, 3)
    
    outcome = "WIN" if pnl_pct > 0 else "LOSS"
    
    # 记录交易
    trade_record = {
        "timestamp": datetime.now().isoformat(),
        "symbol": trade.symbol,
        "direction": trade.direction,
        "entry_price": trade.entry_price,
        "pnl_pct": pnl_pct,
        "outcome": outcome,
        "market_outcome": market_outcome,
        "confidence": trade.confidence,
        "regime": trade.regime,
        "mi_before": compute_mi(state.dimensions, trade.regime, 50, 50),
    }
    _trade_journal.append(trade_record)
    
    # 触发1000-Agent学习
    pool = get_agent_pool()
    agent_improvements = pool.self_improve(market_outcome)
    
    # 触发维度学习 (基于WIN/LOSS)
    from dataclasses import dataclass
    @dataclass
    class FakeTrade:
        timestamp: str = ""
        symbol: str = ""
        direction: str = "LONG"
        entry_price: float = 0
        exit_price: Optional[float] = None
        outcome: str = "WIN"
        pnl_pct: float = 0
        regime: str = "neutral"
        confidence: float = 0.5
        agents_voted: dict = None
        dimensions_before: dict = None
        correct: bool = False
    
    fake = FakeTrade(
        outcome=outcome, regime=trade.regime,
        confidence=trade.confidence,
        dimensions_before=state.dimensions.copy(),
        correct=(outcome == "WIN")
    )
    dim_corrections = learn_from_trade(fake)
    
    # 更新策略评分
    if outcome == "WIN":
        update_strategy_weight("mirofish", "WIN", trade.confidence)
    else:
        update_strategy_weight("mirofish", "LOSS", trade.confidence)
    
    # 持久化
    _save_state()
    
    return {
        "trade": trade_record,
        "market_outcome": market_outcome,
        "agent_improvements": agent_improvements,
        "dimension_corrections": dim_corrections,
        "total_trades": len(_trade_journal),
        "current_mi": round(compute_mi(state.dimensions, trade.regime, 50, 50), 4),
    }

@app.get("/trade/journal")
def get_trade_journal(limit: int = 20):
    """交易流水账"""
    return {
        "total": len(_trade_journal),
        "wins": sum(1 for t in _trade_journal if t["outcome"] == "WIN"),
        "losses": sum(1 for t in _trade_journal if t["outcome"] == "LOSS"),
        "recent": _trade_journal[-limit:],
    }

@app.get("/status/enhanced")
def get_enhanced_status():
    """增强状态面板 (Hermes诊断用)"""
    _ensure_dimensions_loaded()
    pool = get_agent_pool()
    
    # 当前Mi
    try:
        import urllib.request, json as _json
        req = urllib.request.Request(
            "http://localhost:8000/api/v7/market/summary",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = _json.loads(resp.read()).get("data", {})
        fg = float(data.get("fear_greed_index", 50))
        trend = data.get("trend", "neutral")
    except Exception:
        fg, trend = 50, "neutral"
    
    unified_mi = compute_mi(state.dimensions, "neutral", 50.0, fg)
    
    return {
        "unified_mi": round(unified_mi, 4),
        "fear_greed": fg,
        "trend": trend,
        "market_direction": _detect_market_direction(),
        "1000_agent": {
            "n": pool.n,
            "avg_accuracy": round(sum(a.accuracy_estimate for a in pool.agents) / pool.n, 4),
            "market_direction_votes": {k: len([a for a in pool.agents if a.bias == k]) for k in ("bullish", "bearish", "neutral")},
        },
        "dimensions": {
            k: round(v, 2) for k, v in state.dimensions.items()
        },
        "total_trades": len(_trade_journal),
        "win_rate": round(
            sum(1 for t in _trade_journal if t["outcome"] == "WIN") / max(1, len(_trade_journal)) * 100, 1
        ) if _trade_journal else 0,
        "state_loaded": state._dimensions_loaded,
    }
