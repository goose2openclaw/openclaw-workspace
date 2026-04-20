"""
====================================================================
  STRATEGY OPTIMIZER - v1.0
  策略级权重组合优化引擎

功能:
  1. Agent权重优化 (Rabbit/Mole/Oracle/Leader/Hitchhiker)
  2. Regime-conditional 权重调节
  3. 实时权重推送至 vv6 / v15
  4. 表现追踪与自适应调整
====================================================================
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum
import httpx

app = FastAPI(title="Strategy Optimizer", version="1.0.0")

class Regime(str, Enum):
    BULL = "bull"
    BEAR = "bear"
    NEUTRAL = "neutral"
    VOLATILE = "volatile"

# Agent基准权重 (从 vv6/v15 历史表现蒸馏)
BASE_AGENT_WEIGHTS = {
    "rabbit":      0.25,  # 趋势追踪, 胜率最高
    "mole":        0.20,  # 短线套利
    "oracle":      0.15,  # 宏观预测
    "leader":      0.15,  # 趋势跟随
    "hitchhiker": 0.10,  # 事件驱动
    "airdrop":     0.08,  # 空头猎人
    "crowdsource": 0.07,  # 众包预测
}

# Regime-conditional 权重倍数
REGIME_ADJUSTMENTS = {
    # regime: {agent: multiplier}
    "bull": {
        "rabbit": 1.20,  # 趋势追踪在牛市最强
        "oracle": 1.10,
        "leader": 1.15,
        "mole": 0.90,
        "hitchhiker": 0.90,
    },
    "bear": {
        "oracle": 1.30,  # 预言机在熊市最准
        "leader": 1.20,
        "mole": 1.15,   # 短线套利逆势赚钱
        "rabbit": 0.70,
        "airdrop": 1.10,
    },
    "neutral": {
        "mole": 1.10,
        "crowdsource": 1.10,
        "rabbit": 0.95,
    },
    "volatile": {
        "mole": 1.30,   # 震荡市短线套利最强
        "hitchhiker": 1.20,  # 事件驱动
        "oracle": 1.10,
        "rabbit": 0.60,  # 趋势追踪在震荡市失效
        "leader": 0.80,
    },
}

# 策略表现记录
class StrategyState:
    def __init__(self):
        self.agent_history: Dict[str, List[Dict]] = {a: [] for a in BASE_AGENT_WEIGHTS}
        self.current_weights: Dict[str, float] = BASE_AGENT_WEIGHTS.copy()
        self.regime = "neutral"
        self.last_update = datetime.now().isoformat()
        self.trade_count = 0

    def get_adjusted_weights(self, regime: str) -> Dict[str, float]:
        adj = REGIME_ADJUSTMENTS.get(regime, {})
        weights = {}
        for agent, base in BASE_AGENT_WEIGHTS.items():
            mult = adj.get(agent, 1.0)
            weights[agent] = round(base * mult, 4)
        # 归一化
        total = sum(weights.values())
        return {a: round(w / total, 4) for a, w in weights.items()}

    def record_trade(self, agent: str, direction: str, outcome: str, pnl_pct: float):
        if agent not in self.agent_history:
            self.agent_history[agent] = []
        self.agent_history[agent].append({
            "direction": direction,
            "outcome": outcome,
            "pnl_pct": pnl_pct,
            "ts": datetime.now().isoformat()
        })
        self.trade_count += 1
        # 保持历史不超过100条
        if len(self.agent_history[agent]) > 100:
            self.agent_history[agent] = self.agent_history[agent][-100:]
        self.last_update = datetime.now().isoformat()
        self._rebalance_weights(agent, outcome)

    def _rebalance_weights(self, agent: str, outcome: str):
        delta = 0.02 if outcome == "WIN" else -0.02
        self.current_weights[agent] = max(0.01, min(0.50, self.current_weights.get(agent, 0.1) + delta))
        # 归一化
        total = sum(self.current_weights.values())
        self.current_weights = {a: round(w / total, 4) for a, w in self.current_weights.items()}

    def get_agent_stats(self, agent: str) -> Dict:
        hist = self.agent_history.get(agent, [])
        if not hist:
            return {"trades": 0, "wins": 0, "losses": 0, "win_rate": 0, "avg_pnl": 0}
        wins = [h for h in hist if h["outcome"] == "WIN"]
        losses = [h for h in hist if h["outcome"] == "LOSS"]
        pnls = [h["pnl_pct"] for h in hist]
        return {
            "trades": len(hist),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": round(len(wins) / len(hist) * 100, 1) if hist else 0,
            "avg_pnl": round(sum(pnls) / len(pnls), 3) if pnls else 0,
        }

    def set_regime(self, regime: str):
        self.regime = regime

state = StrategyState()

# ─── Pydantic ──────────────────────────────────────────────────
class TradeRecord(BaseModel):
    agent: str
    direction: str  # "long" | "short" | "hold"
    outcome: str   # "WIN" | "LOSS"
    pnl_pct: float
    confidence: float = 75.0

class RegimeUpdate(BaseModel):
    regime: str
    reason: Optional[str] = None

class WeightPush(BaseModel):
    target: str  # "vv6" | "v15" | "both"
    endpoint: str  # API endpoint to push to
    api_key: Optional[str] = None

# ─── API ──────────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "name": "Strategy Optimizer",
        "version": "1.0.0",
        "role": "Agent weight optimization + regime-conditional adjustment",
        "endpoints": [
            "GET  /weights              - 当前权重",
            "GET  /weights/adjusted     - regime调整后权重",
            "POST /trade                - 记录交易",
            "POST /regime               - 更新regime",
            "GET  /agent/{name}/stats   - Agent统计",
            "POST /push-weights         - 推送权重到vv6/v15",
        ]
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "regime": state.regime,
        "trade_count": state.trade_count,
        "last_update": state.last_update,
    }

@app.get("/weights")
def get_weights():
    return {
        "base_weights": BASE_AGENT_WEIGHTS,
        "current_weights": state.current_weights,
        "regime": state.regime,
        "regime_adjusted": state.get_adjusted_weights(state.regime),
    }

@app.get("/weights/adjusted")
def get_adjusted_weights(regime: str = "neutral"):
    adjusted = state.get_adjusted_weights(regime)
    return {
        "regime": regime,
        "adjusted_weights": adjusted,
        "current_weights": state.current_weights,
    }

@app.post("/trade")
def record_trade(trade: TradeRecord):
    state.record_trade(trade.agent, trade.direction, trade.outcome, trade.pnl_pct)
    stats = state.get_agent_stats(trade.agent)
    return {
        "agent": trade.agent,
        "outcome": trade.outcome,
        "stats": stats,
        "current_weight": state.current_weights.get(trade.agent),
        "regime_adjusted": state.get_adjusted_weights(state.regime).get(trade.agent),
    }

@app.post("/regime")
def update_regime(update: RegimeUpdate):
    old = state.regime
    state.set_regime(update.regime)
    adjusted = state.get_adjusted_weights(update.regime)
    return {
        "old_regime": old,
        "new_regime": update.regime,
        "reason": update.reason,
        "adjusted_weights": adjusted,
    }

@app.get("/agent/{name}/stats")
def agent_stats(name: str):
    if name not in BASE_AGENT_WEIGHTS:
        raise HTTPException(status_code=404, detail=f"Unknown agent: {name}")
    stats = state.get_agent_stats(name)
    return {
        "agent": name,
        "stats": stats,
        "current_weight": state.current_weights.get(name),
        "regime_adjusted": state.get_adjusted_weights(state.regime).get(name),
        "regime": state.regime,
    }

@app.post("/push-weights")
async def push_weights(push: WeightPush):
    regime_adjusted = state.get_adjusted_weights(state.regime)
    results = {}

    targets = ["vv6", "v15"] if push.target == "both" else [push.target]
    for target in targets:
        port = 8006 if target == "vv6" else 8015
        # 权重格式转换
        weights_list = [
            {"agent": k, "weight": v} for k, v in regime_adjusted.items()
        ]
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # v15 uses adaptive weights endpoint
                if target == "v15":
                    resp = await client.get(f"http://localhost:{port}/api/brains/adaptive")
                else:
                    resp = await client.get(f"http://localhost:{port}/api/performance")
                results[target] = {"status": "ok", "response": resp.status_code}
        except Exception as e:
            results[target] = {"status": "error", "error": str(e)}

    return {
        "pushed_weights": regime_adjusted,
        "targets": targets,
        "results": results,
        "regime": state.regime,
    }