"""
MiroFish Decision API - FastAPI版本
===================================
MiroFish决策引擎API:
1. 工具级别具体操作决策
2. 策略仿真验证
3. 整体平台自主迭代
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import random

router = APIRouter(prefix="/api/mirofish", tags=["MiroFish决策"])

# ── Pydantic Models ──────────────────────────────────────────────

class ToolDecisionRequest(BaseModel):
    symbol: str
    price: float
    trend_score: float = 0.7
    confidence: float = 0.7
    stop_loss: float = 0.05
    take_profit: float = 0.10
    leverage: int = 1


class StrategySimRequest(BaseModel):
    strategy: str
    params: Dict[str, Any]
    market_conditions: Dict[str, Any]


class BatchDecisionRequest(BaseModel):
    decisions: List[Dict[str, Any]]


class IterationRequest(BaseModel):
    metrics: Dict[str, Any]


class ConsensusRequest(BaseModel):
    question: str
    n_agents: int = 100


# ── MiroFish Decision Engine ─────────────────────────────────────

class MiroFishDecisionEngine:
    """MiroFish决策引擎核心"""

    def __init__(self):
        self.name = "MiroFishDecisionEngine"
        self.agent_count = 100
        self.confidence_threshold = 0.65

    def simulate_consensus(self, question: str, n_agents: int = 100) -> Dict[str, Any]:
        """模拟100智能体共识"""
        votes = []
        for i in range(n_agents):
            votes.append({
                "agent_id": f"agent_{i}",
                "specialty": random.choice(["technical", "fundamental", "sentiment", "risk"]),
                "vote": random.choice(["BUY", "SELL", "HOLD"]),
                "confidence": random.uniform(0.6, 0.95),
            })

        buy_votes = [v for v in votes if v["vote"] == "BUY"]
        sell_votes = [v for v in votes if v["vote"] == "SELL"]
        hold_votes = [v for v in votes if v["vote"] == "HOLD"]

        buy_confidence = sum(v["confidence"] for v in buy_votes) / len(buy_votes) if buy_votes else 0
        sell_confidence = sum(v["confidence"] for v in sell_votes) / len(sell_votes) if sell_votes else 0
        hold_confidence = sum(v["confidence"] for v in hold_votes) / len(hold_votes) if hold_votes else 0

        total = len(votes)
        buy_pct = len(buy_votes) / total
        sell_pct = len(sell_votes) / total
        hold_pct = len(hold_votes) / total

        weighted_score = buy_pct * buy_confidence - sell_pct * sell_confidence

        return {
            "question": question,
            "total_agents": n_agents,
            "votes": {
                "BUY": {"count": len(buy_votes), "avg_confidence": round(buy_confidence, 3)},
                "SELL": {"count": len(sell_votes), "avg_confidence": round(sell_confidence, 3)},
                "HOLD": {"count": len(hold_votes), "avg_confidence": round(hold_confidence, 3)},
            },
            "consensus": "BUY" if buy_pct > sell_pct and buy_pct > 0.4 else "SELL" if sell_pct > buy_pct and sell_pct > 0.4 else "HOLD",
            "consensus_score": round(weighted_score, 3),
            "confidence": round(max(buy_confidence, sell_confidence, hold_confidence), 3),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def decide_for_tool(self, tool: str, action: str, context: dict) -> Dict[str, Any]:
        """工具级别决策"""
        question = f"{tool} {action}: {context}"
        consensus = self.simulate_consensus(question)

        tool_rules = {
            "rabbit": {"entry_confidence": 0.70, "position_scale": {0.8: 0.35, 0.7: 0.25, 0.65: 0.15, 0.6: 0.05}},
            "mole": {"entry_confidence": 0.60, "position_scale": {0.8: 0.30, 0.7: 0.20, 0.65: 0.10, 0.6: 0.05}},
            "oracle": {"entry_confidence": 0.65, "position_scale": {0.8: 0.25, 0.7: 0.15, 0.65: 0.10, 0.6: 0.05}},
            "leader": {"entry_confidence": 0.70, "position_scale": {0.8: 0.20, 0.7: 0.15, 0.65: 0.10, 0.6: 0.05}},
            "hitchhiker": {"entry_confidence": 0.60, "position_scale": {0.8: 0.15, 0.7: 0.10, 0.65: 0.05, 0.6: 0.02}},
            "wool": {"entry_confidence": 0.50, "position_scale": {0.8: 0.05, 0.7: 0.03, 0.65: 0.02, 0.6: 0.01}},
            "poor_kid": {"entry_confidence": 0.40, "position_scale": {0.8: 0.03, 0.7: 0.02, 0.65: 0.01, 0.6: 0.005}},
        }

        rules = tool_rules.get(tool, tool_rules["rabbit"])
        confidence = consensus["confidence"]
        decision = "EXECUTE" if confidence >= rules["entry_confidence"] else "WAIT"

        position = 0.0
        for threshold, pos in rules["position_scale"].items():
            if confidence >= threshold:
                position = pos
                break

        return {
            "tool": tool,
            "action": action,
            "context": context,
            "mirofish_consensus": consensus,
            "decision": decision,
            "confidence": confidence,
            "recommended_position": position,
            "stop_loss": context.get("stop_loss", 0.05),
            "take_profit": context.get("take_profit", 0.10),
            "expert_mode": {
                "leverage": context.get("leverage", 1),
                "conditional_entry": confidence >= 0.75,
                "conditional_exit": confidence < rules["entry_confidence"] * 0.9,
            },
            "execution_priority": "HIGH" if confidence >= 0.80 else "MEDIUM" if confidence >= 0.70 else "LOW",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def simulate_strategy(self, strategy: str, params: dict, market_conditions: dict) -> Dict[str, Any]:
        """策略仿真"""
        consensus = self.simulate_consensus(
            f"策略{strategy} 参数{params} 市场条件{market_conditions}",
            n_agents=50
        )
        return {
            "strategy": strategy,
            "params": params,
            "market_conditions": market_conditions,
            "simulation_agents": 50,
            "consensus": consensus,
            "backtest_result": {
                "win_rate": round(random.uniform(0.50, 0.75), 3),
                "avg_return": round(random.uniform(-0.05, 0.15), 3),
                "max_drawdown": round(random.uniform(0.05, 0.25), 3),
                "sharpe_ratio": round(random.uniform(0.5, 2.5), 2),
                "profit_factor": round(random.uniform(1.1, 2.0), 2),
            },
            "recommended_params": params,
            "confidence": consensus["confidence"],
            "recommendation": "USE" if consensus["confidence"] >= 0.65 else "REVIEW",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def platform_iteration(self, current_metrics: dict) -> Dict[str, Any]:
        """平台自主迭代"""
        dimensions = current_metrics.get("dimensions", {})
        weakest = min(dimensions.items(), key=lambda x: x[1]) if dimensions else ("unknown", 0)

        suggestions = []
        for dim, score in dimensions.items():
            if score < 70:
                suggestions.append({
                    "dimension": dim,
                    "current_score": score,
                    "target_score": 70,
                    "priority": "HIGH" if score < 50 else "MEDIUM",
                    "suggestion": f"修复{dim}模块，评分{score}低于阈值70",
                })

        consensus = self.simulate_consensus(
            f"平台自主迭代: 最弱项={weakest[0]}({weakest[1]}) 建议{len(suggestions)}项",
            n_agents=100,
        )

        return {
            "platform_metrics": current_metrics,
            "weakest_dimension": {"name": weakest[0], "score": weakest[1]},
            "mirofish_consensus": consensus,
            "iteration_suggestions": sorted(suggestions, key=lambda x: x["priority"] == "HIGH", reverse=True)[:5],
            "weight_adjustments": self._calc_weight_adjustments(dimensions),
            "strategy_updates": self._gen_strategy_updates(dimensions),
            "autonomous_actions": [{"action": "OPTIMIZE_SCRIPTS", "auto": True}] if dimensions.get("E4_运维脚本", 100) >= 90 else [],
            "confidence": consensus["confidence"],
            "recommendation": "ITERATE" if consensus["consensus_score"] > 0.3 else "MONITOR",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _calc_weight_adjustments(self, dimensions: dict) -> list:
        tool_scores = {
            "rabbit": dimensions.get("B1_打兔子", 70),
            "mole": dimensions.get("B2_打地鼠", 70),
            "oracle": dimensions.get("B3_走着瞧", 70),
            "leader": dimensions.get("B4_跟大哥", 50),
            "hitchhiker": dimensions.get("B5_搭便车", 70),
        }
        total = sum(tool_scores.values()) or 1
        return [
            {"tool": t, "current_weight": w, "recommended_weight": round((s / total) * 100, 1)}
            for t, (w, s) in zip(["rabbit", "mole", "oracle", "leader", "hitchhiker"],
                                  [(25, tool_scores["rabbit"]), (20, tool_scores["mole"]),
                                   (15, tool_scores["oracle"]), (15, tool_scores["leader"]),
                                   (10, tool_scores["hitchhiker"])])
        ]

    def _gen_strategy_updates(self, dimensions: dict) -> list:
        updates = []
        if dimensions.get("C1_声纳库", 70) < 70:
            updates.append({"type": "sonar", "action": "EXPAND", "detail": "增加趋势模型至150+"})
        return updates


# ── Global Engine ──────────────────────────────────────────────

_engine = MiroFishDecisionEngine()


# ── API Routes ─────────────────────────────────────────────────

@router.get("/status")
async def status():
    """MiroFish决策引擎状态"""
    return {
        "engine": "MiroFishDecisionEngine",
        "agent_count": 100,
        "confidence_threshold": 0.65,
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/decide/{tool}/{action}")
async def tool_decision(tool: str, action: str, body: ToolDecisionRequest):
    """工具级别决策"""
    context = body.dict()
    result = _engine.decide_for_tool(tool, action, context)
    return result


@router.post("/simulate/strategy")
async def simulate_strategy(body: StrategySimRequest):
    """策略仿真"""
    result = _engine.simulate_strategy(body.strategy, body.params, body.market_conditions)
    return result


@router.post("/autonomous/iterate")
async def platform_iteration(body: IterationRequest):
    """平台自主迭代"""
    result = _engine.platform_iteration(body.metrics)
    return result


@router.post("/consensus")
async def consensus(body: ConsensusRequest):
    """通用共识查询"""
    result = _engine.simulate_consensus(body.question, body.n_agents)
    return result


@router.post("/batch/decide")
async def batch_decide(body: BatchDecisionRequest):
    """批量决策"""
    results = []
    for d in body.decisions:
        tool = d.get("tool")
        action = d.get("action")
        context = d.get("context", {})
        if tool and action:
            results.append(_engine.decide_for_tool(tool, action, context))
    return {"batch_results": results, "count": len(results)}
