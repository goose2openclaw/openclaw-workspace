"""
MiroFish Decision API - FastAPI版本
===================================
多信号源融合决策引擎:

信号源 (6个):
1. MiroFish    - 100智能体共识
2. 声纳库       - 123趋势模型
3. Oracle       - 预言机/数据源
4. 市场情绪     - Twitter/Telegram/News情绪
5. 外部API      - Binance/ByBit/专业信号
6. 其他专业信号  - 技术分析/量化信号

决策流程:
  多信号源 → 各自置信度 → 可调权重融合 → 最终决策
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import random

router = APIRouter(prefix="/api/mirofish", tags=["MiroFish决策"])

# ── 信号源权重配置 ─────────────────────────────────────────────

SIGNAL_SOURCES = [
    "mirofish",      # 100智能体共识
    "sonar",         # 123趋势模型
    "oracle",        # 预言机数据源
    "sentiment",     # 市场情绪
    "external_api",  # 外部API信号
    "professional",  # 其他专业信号
]

DEFAULT_WEIGHTS = {
    "mirofish": 0.25,      # MiroFish权重 (可调)
    "sonar": 0.20,         # 声纳库权重
    "oracle": 0.20,        # Oracle权重
    "sentiment": 0.15,     # 情绪权重
    "external_api": 0.10,  # 外部API权重
    "professional": 0.10,   # 专业信号权重
}

# 权重范围 (可调)
WEIGHT_BOUNDS = {
    "mirofish": [0.05, 0.50],
    "sonar": [0.05, 0.40],
    "oracle": [0.05, 0.40],
    "sentiment": [0.05, 0.30],
    "external_api": [0.00, 0.30],
    "professional": [0.00, 0.30],
}

# ── Pydantic Models ─────────────────────────────────────────────

class SignalInput(BaseModel):
    """单个信号源输入"""
    source: str  # mirofish/sonar/oracle/sentiment/external_api/professional
    signal: str   # BUY/SELL/HOLD
    confidence: float  # 0.0-1.0
    metadata: Dict[str, Any] = {}


class WeightedSignalsRequest(BaseModel):
    """多信号源融合请求"""
    symbol: str
    signals: List[SignalInput]
    weights: Optional[Dict[str, float]] = None  # 可选自定义权重


class ToolDecisionRequest(BaseModel):
    """工具决策请求"""
    symbol: str
    price: float
    # 各信号源输入
    mirofish_confidence: float = 0.7
    sonar_signals: List[Dict[str, Any]] = []
    oracle_data: Dict[str, Any] = {}
    sentiment_score: float = 0.5
    external_api_signals: List[Dict[str, Any]] = []
    professional_signals: List[Dict[str, Any]] = []
    # 可调权重
    weights: Optional[Dict[str, float]] = None
    # 工具参数
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


class WeightConfig(BaseModel):
    """权重配置"""
    weights: Dict[str, float]


# ── 信号融合引擎 ─────────────────────────────────────────────

class SignalFusionEngine:
    """
    多信号源融合引擎
    =================
    将6个信号源的输入，通过可调权重融合为最终决策

    信号源:
    1. MiroFish (100智能体共识)
    2. 声纳库 (123趋势模型)
    3. Oracle (预言机数据)
    4. 市场情绪 (Twitter/Telegram/News)
    5. 外部API (Binance/ByBit专业信号)
    6. 其他专业信号 (技术分析/量化)
    """

    def __init__(self):
        self.sources = SIGNAL_SOURCES
        self.default_weights = DEFAULT_WEIGHTS.copy()
        self.weight_bounds = WEIGHT_BOUNDS

    def normalize_weights(self, weights: Dict[str, float]) -> Dict[str, float]:
        """归一化权重，确保总和=1"""
        total = sum(weights.values())
        if total == 0:
            return self.default_weights.copy()
        return {k: v / total for k, v in weights.items()}

    def validate_weights(self, weights: Dict[str, float]) -> bool:
        """验证权重是否在有效范围内"""
        for source, weight in weights.items():
            if source in self.weight_bounds:
                lo, hi = self.weight_bounds[source]
                if not (lo <= weight <= hi):
                    return False
        return True

    def simulate_mirofish_consensus(self, question: str, n_agents: int = 100) -> Dict[str, Any]:
        """模拟MiroFish 100智能体共识"""
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

        total = len(votes)
        buy_pct = len(buy_votes) / total
        sell_pct = len(sell_votes) / total
        hold_pct = len(hold_votes) / total

        buy_conf = sum(v["confidence"] for v in buy_votes) / len(buy_votes) if buy_votes else 0
        sell_conf = sum(v["confidence"] for v in sell_votes) / len(sell_votes) if sell_votes else 0
        hold_conf = sum(v["confidence"] for v in hold_votes) / len(hold_votes) if hold_votes else 0

        # 转换为置信度分数 (-1到1)
        score = (buy_pct * buy_conf) - (sell_pct * sell_conf)

        return {
            "source": "mirofish",
            "signal": "BUY" if buy_pct > sell_pct else "SELL" if sell_pct > buy_pct else "HOLD",
            "confidence": max(buy_conf, sell_conf, hold_conf),
            "score": round(score, 3),
            "votes": {"BUY": len(buy_votes), "SELL": len(sell_votes), "HOLD": len(hold_votes)},
            "n_agents": n_agents,
        }

    def sonar_signal(self, symbol: str, models: List[Dict]) -> Dict[str, Any]:
        """声纳库123趋势模型信号"""
        if not models:
            # 模拟声纳扫描结果
            models_count = 123
            bullish_count = random.randint(40, 80)
            bearish_count = random.randint(10, 40)
            neutral_count = models_count - bullish_count - bearish_count

            bullish_conf = random.uniform(0.65, 0.85)
            bearish_conf = random.uniform(0.60, 0.80)

            score = (bullish_count * bullish_conf - bearish_count * bearish_conf) / models_count
        else:
            bullish_count = sum(1 for m in models if m.get("trend") == "bullish")
            bearish_count = sum(1 for m in models if m.get("trend") == "bearish")
            score = (bullish_count - bearish_count) / max(len(models), 1)

        return {
            "source": "sonar",
            "signal": "BUY" if score > 0.1 else "SELL" if score < -0.1 else "HOLD",
            "confidence": abs(score),
            "score": round(score, 3),
            "models_triggered": len(models) if models else 123,
            "bullish_models": bullish_count,
            "bearish_models": bearish_count,
        }

    def oracle_signal(self, data: Dict) -> Dict[str, Any]:
        """Oracle预言机信号"""
        if not data:
            # 模拟Oracle数据
            price_change = random.uniform(-0.05, 0.08)
            volume_ratio = random.uniform(0.8, 2.0)
            score = price_change * 2 + (volume_ratio - 1) * 0.3
        else:
            price_change = data.get("price_change", 0)
            volume_ratio = data.get("volume_ratio", 1)
            score = price_change * 2 + (volume_ratio - 1) * 0.3

        return {
            "source": "oracle",
            "signal": "BUY" if score > 0.1 else "SELL" if score < -0.1 else "HOLD",
            "confidence": min(abs(score) + 0.5, 1.0),
            "score": round(score, 3),
            "price_change": price_change if data else round(random.uniform(-0.05, 0.08), 4),
            "volume_ratio": volume_ratio if data else round(random.uniform(0.8, 2.0), 2),
        }

    def sentiment_signal(self, score: float = None) -> Dict[str, Any]:
        """市场情绪信号"""
        if score is None:
            score = random.uniform(-0.5, 0.6)

        return {
            "source": "sentiment",
            "signal": "BUY" if score > 0.2 else "SELL" if score < -0.2 else "HOLD",
            "confidence": abs(score),
            "score": round(score, 3),
        }

    def external_api_signal(self, signals: List[Dict]) -> Dict[str, Any]:
        """外部API信号"""
        if not signals:
            # 模拟外部API信号
            api_signals = [
                {"api": "binance", "signal": "BUY", "confidence": random.uniform(0.6, 0.85)},
                {"api": "bybit", "signal": "BUY", "confidence": random.uniform(0.55, 0.80)},
            ]
        else:
            api_signals = signals

        if not api_signals:
            return {"source": "external_api", "signal": "HOLD", "confidence": 0.5, "score": 0, "apis": []}

        buy_count = sum(1 for s in api_signals if s.get("signal") == "BUY")
        sell_count = sum(1 for s in api_signals if s.get("signal") == "SELL")
        total = len(api_signals)

        score = (buy_count - sell_count) / total
        avg_confidence = sum(s.get("confidence", 0.5) for s in api_signals) / total

        return {
            "source": "external_api",
            "signal": "BUY" if buy_count > sell_count else "SELL" if sell_count > buy_count else "HOLD",
            "confidence": avg_confidence,
            "score": round(score, 3),
            "apis": api_signals,
        }

    def professional_signal(self, signals: List[Dict]) -> Dict[str, Any]:
        """其他专业信号"""
        if not signals:
            signals = [
                {"type": "technical", "signal": "BUY", "confidence": random.uniform(0.60, 0.85)},
                {"type": "quant", "signal": "HOLD", "confidence": random.uniform(0.55, 0.75)},
            ]

        buy_count = sum(1 for s in signals if s.get("signal") == "BUY")
        sell_count = sum(1 for s in signals if s.get("signal") == "SELL")
        total = len(signals) or 1

        score = (buy_count - sell_count) / total
        avg_confidence = sum(s.get("confidence", 0.5) for s in signals) / total

        return {
            "source": "professional",
            "signal": "BUY" if buy_count > sell_count else "SELL" if sell_count > buy_count else "HOLD",
            "confidence": avg_confidence,
            "score": round(score, 3),
            "signals": signals,
        }

    def fuse_signals(
        self,
        symbol: str,
        mirofish_confidence: float = 0.7,
        sonar_models: List[Dict] = None,
        oracle_data: Dict = None,
        sentiment_score: float = 0.5,
        external_signals: List[Dict] = None,
        professional_signals: List[Dict] = None,
        weights: Dict[str, float] = None,
    ) -> Dict[str, Any]:
        """
        融合多信号源为最终决策
        =========================
        权重可调，默认:
        - MiroFish: 25%
        - 声纳库: 20%
        - Oracle: 20%
        - 情绪: 15%
        - 外部API: 10%
        - 专业信号: 10%
        """
        # 获取各信号源结果
        mirofish = self.simulate_mirofish_consensus(f"{symbol} trading decision")
        mirofish["confidence"] = mirofish_confidence
        mirofish["score"] = mirofish_confidence * (1 if mirofish["signal"] == "BUY" else -1 if mirofish["signal"] == "SELL" else 0)

        sonar = self.sonar_signal(symbol, sonar_models or [])
        oracle = self.oracle_signal(oracle_data or {})
        sentiment = self.sentiment_signal(sentiment_score)
        external_api = self.external_api_signal(external_signals or [])
        professional = self.professional_signal(professional_signals or [])

        all_signals = {
            "mirofish": mirofish,
            "sonar": sonar,
            "oracle": oracle,
            "sentiment": sentiment,
            "external_api": external_api,
            "professional": professional,
        }

        # 使用传入权重或默认权重
        if weights is None:
            weights = self.default_weights.copy()
        else:
            weights = self.normalize_weights(weights)

        # 验证权重
        if not self.validate_weights(weights):
            weights = self.default_weights.copy()

        # 加权融合
        total_score = 0.0
        total_confidence = 0.0
        source_results = {}

        for source, weight in weights.items():
            sig = all_signals.get(source, {})
            score = sig.get("score", 0)
            confidence = sig.get("confidence", 0.5)

            weighted_score = score * weight
            weighted_confidence = confidence * weight

            total_score += weighted_score
            total_confidence += weighted_confidence

            source_results[source] = {
                "signal": sig.get("signal", "HOLD"),
                "score": score,
                "confidence": confidence,
                "weight": weight,
                "weighted_score": round(weighted_score, 4),
            }

        # 最终决策
        final_score = total_score
        if final_score > 0.15:
            final_signal = "BUY"
        elif final_score < -0.15:
            final_signal = "SELL"
        else:
            final_signal = "HOLD"

        # 置信度
        final_confidence = abs(total_score) * total_confidence

        # 仓位计算
        position = self._calculate_position(final_signal, final_confidence)

        return {
            "symbol": symbol,
            "final_signal": final_signal,
            "final_score": round(final_score, 4),
            "final_confidence": round(final_confidence, 4),
            "recommended_position": position,
            "weights_used": weights,
            "source_results": source_results,
            "decision": "EXECUTE" if final_confidence >= 0.60 and final_signal != "HOLD" else "WAIT",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _calculate_position(self, signal: str, confidence: float) -> float:
        """根据信号和置信度计算仓位"""
        if signal == "HOLD":
            return 0.0

        base_positions = {
            "BUY": {0.8: 0.35, 0.7: 0.25, 0.6: 0.15, 0.5: 0.05},
            "SELL": {0.8: 0.30, 0.7: 0.20, 0.6: 0.10, 0.5: 0.05},
        }

        positions = base_positions.get(signal, {})
        for threshold, pos in sorted(positions.items(), reverse=True):
            if confidence >= threshold:
                return pos
        return 0.0


# ── 工具级别决策 (基于融合信号) ─────────────────────────────────────

class ToolDecisionEngine:
    """工具级别决策引擎"""

    def __init__(self):
        self.fusion_engine = SignalFusionEngine()
        self.tool_configs = {
            "rabbit": {
                "entry_confidence": 0.70,
                "position_scale": {0.8: 0.35, 0.7: 0.25, 0.65: 0.15, 0.6: 0.05},
                "base_weight_mirofish": 0.30,
            },
            "mole": {
                "entry_confidence": 0.60,
                "position_scale": {0.8: 0.30, 0.7: 0.20, 0.65: 0.10, 0.6: 0.05},
                "base_weight_mirofish": 0.20,
            },
            "oracle": {
                "entry_confidence": 0.65,
                "position_scale": {0.8: 0.25, 0.7: 0.15, 0.65: 0.10, 0.6: 0.05},
                "base_weight_mirofish": 0.25,
            },
            "leader": {
                "entry_confidence": 0.70,
                "position_scale": {0.8: 0.20, 0.7: 0.15, 0.65: 0.10, 0.6: 0.05},
                "base_weight_mirofish": 0.25,
            },
            "hitchhiker": {
                "entry_confidence": 0.60,
                "position_scale": {0.8: 0.15, 0.7: 0.10, 0.65: 0.05, 0.6: 0.02},
                "base_weight_mirofish": 0.15,
            },
            "wool": {
                "entry_confidence": 0.50,
                "position_scale": {0.8: 0.05, 0.7: 0.03, 0.65: 0.02, 0.6: 0.01},
                "base_weight_mirofish": 0.10,
            },
            "poor_kid": {
                "entry_confidence": 0.40,
                "position_scale": {0.8: 0.03, 0.7: 0.02, 0.65: 0.01, 0.6: 0.005},
                "base_weight_mirofish": 0.05,
            },
        }

    def decide_for_tool(
        self,
        tool: str,
        symbol: str,
        mirofish_confidence: float = 0.7,
        sonar_models: List[Dict] = None,
        oracle_data: Dict = None,
        sentiment_score: float = 0.5,
        external_signals: List[Dict] = None,
        professional_signals: List[Dict] = None,
        weights: Dict[str, float] = None,
        stop_loss: float = 0.05,
        take_profit: float = 0.10,
        leverage: int = 1,
    ) -> Dict[str, Any]:
        """工具级别决策"""
        # 工具特定权重调整
        if weights is None and tool in self.tool_configs:
            config = self.tool_configs[tool]
            weights = self.fusion_engine.default_weights.copy()
            # MiroFish在工具决策中权重可调整
            weights["mirofish"] = config.get("base_weight_mirofish", 0.25)

        # 融合信号
        fusion_result = self.fusion_engine.fuse_signals(
            symbol=symbol,
            mirofish_confidence=mirofish_confidence,
            sonar_models=sonar_models,
            oracle_data=oracle_data,
            sentiment_score=sentiment_score,
            external_signals=external_signals,
            professional_signals=professional_signals,
            weights=weights,
        )

        # 工具特定决策规则
        config = self.tool_configs.get(tool, self.tool_configs["rabbit"])
        entry_threshold = config["entry_confidence"]

        # 决策
        decision = "EXECUTE" if (
            fusion_result["final_confidence"] >= entry_threshold and
            fusion_result["final_signal"] != "HOLD"
        ) else "WAIT"

        # 工具特定仓位
        position = 0.0
        if fusion_result["final_signal"] != "HOLD":
            for threshold, pos in config["position_scale"].items():
                if fusion_result["final_confidence"] >= threshold:
                    position = pos
                    break

        return {
            "tool": tool,
            "symbol": symbol,
            "fusion_result": fusion_result,
            "decision": decision,
            "confidence": fusion_result["final_confidence"],
            "signal": fusion_result["final_signal"],
            "recommended_position": position,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "leverage": leverage,
            "expert_mode": {
                "conditional_entry": fusion_result["final_confidence"] >= entry_threshold + 0.10,
                "conditional_exit": fusion_result["final_confidence"] < entry_threshold * 0.8,
            },
            "execution_priority": "HIGH" if fusion_result["final_confidence"] >= 0.80 else "MEDIUM" if fusion_result["final_confidence"] >= 0.70 else "LOW",
            "timestamp": datetime.utcnow().isoformat(),
        }


# ── 自主迭代引擎 ─────────────────────────────────────────────

class AutonomousIterationEngine:
    """自主迭代引擎 - ML + MiroFish协同"""

    def __init__(self):
        self.fusion_engine = SignalFusionEngine()

    def generate_iteration(
        self,
        current_metrics: Dict[str, Any],
        market_conditions: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """生成迭代建议"""
        dimensions = current_metrics.get("dimensions", {})

        # 找出最弱项
        weakest = min(dimensions.items(), key=lambda x: x[1]) if dimensions else ("unknown", 0)

        # MiroFish共识
        mirofish = self.fusion_engine.simulate_mirofish_consensus(
            f"平台迭代: 最弱项={weakest[0]}({weakest[1]})"
        )

        # 生成建议
        suggestions = []
        for dim, score in dimensions.items():
            if score < 70:
                priority = "HIGH" if score < 50 else "MEDIUM"
                suggestions.append({
                    "dimension": dim,
                    "current_score": score,
                    "target_score": 70,
                    "priority": priority,
                    "action": f"优化{dim}模块，评分{score}低于阈值70",
                })

        # 权重调整
        weight_adjustments = []
        if "tool_scores" in current_metrics:
            for tool, score in current_metrics["tool_scores"].items():
                current_weight = self.fusion_engine.default_weights.get(tool, 0.15)
                if score > 75:
                    weight_adjustments.append({
                        "tool": tool,
                        "weight_change": +5,
                        "reason": f"评分{score}高于平均",
                    })
                elif score < 60:
                    weight_adjustments.append({
                        "tool": tool,
                        "weight_change": -5,
                        "reason": f"评分{score}低于阈值",
                    })

        return {
            "weakest_dimension": {"name": weakest[0], "score": weakest[1]},
            "mirofish_consensus": mirofish,
            "iteration_suggestions": sorted(suggestions, key=lambda x: x["priority"] == "HIGH", reverse=True)[:5],
            "weight_adjustments": weight_adjustments,
            "confidence": mirofish["confidence"],
            "recommendation": "ITERATE" if mirofish["confidence"] > 0.65 else "MONITOR",
            "timestamp": datetime.utcnow().isoformat(),
        }


# ── 全局引擎实例 ─────────────────────────────────────────────

_fusion_engine = SignalFusionEngine()
_tool_engine = ToolDecisionEngine()
_iteration_engine = AutonomousIterationEngine()


# ── API Routes ─────────────────────────────────────────────────

@router.get("/status")
async def status():
    """信号融合引擎状态"""
    return {
        "engine": "SignalFusionEngine",
        "sources": SIGNAL_SOURCES,
        "default_weights": DEFAULT_WEIGHTS,
        "weight_bounds": WEIGHT_BOUNDS,
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/fuse")
async def fuse_signals(body: WeightedSignalsRequest):
    """
    多信号源融合
    POST /api/mirofish/fuse
    """
    result = _fusion_engine.fuse_signals(
        symbol=body.symbol,
        mirofish_confidence=0.7,
        weights=body.weights,
    )
    return result


@router.post("/decide/{tool}")
async def tool_decision(tool: str, body: ToolDecisionRequest):
    """
    工具级别决策 (多信号源融合)
    POST /api/mirofish/decide/rabbit
    """
    result = _tool_engine.decide_for_tool(
        tool=tool,
        symbol=body.symbol,
        mirofish_confidence=body.mirofish_confidence,
        sonar_models=body.sonar_signals,
        oracle_data=body.oracle_data,
        sentiment_score=body.sentiment_score,
        external_signals=body.external_api_signals,
        professional_signals=body.professional_signals,
        weights=body.weights,
        stop_loss=body.stop_loss,
        take_profit=body.take_profit,
        leverage=body.leverage,
    )
    return result


@router.post("/weights")
async def update_weights(body: WeightConfig):
    """
    更新信号源权重
    POST /api/mirofish/weights
    """
    if not _fusion_engine.validate_weights(body.weights):
        raise HTTPException(status_code=400, detail="权重超出有效范围")
    normalized = _fusion_engine.normalize_weights(body.weights)
    return {
        "weights": normalized,
        "status": "updated",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/weights")
async def get_weights():
    """获取当前权重配置"""
    return {
        "weights": DEFAULT_WEIGHTS,
        "bounds": WEIGHT_BOUNDS,
    }


@router.post("/consensus")
async def consensus(body: ConsensusRequest):
    """MiroFish共识查询"""
    result = _fusion_engine.simulate_mirofish_consensus(body.question, body.n_agents)
    return result


@router.post("/autonomous/iterate")
async def autonomous_iterate(body: IterationRequest):
    """平台自主迭代"""
    result = _iteration_engine.generate_iteration(body.metrics)
    return result


@router.post("/batch/decide")
async def batch_decide(body: BatchDecisionRequest):
    """批量工具决策"""
    results = []
    for d in body.decisions:
        tool = d.get("tool", "rabbit")
        symbol = d.get("symbol", "BTC")
        result = _tool_engine.decide_for_tool(
            tool=tool,
            symbol=symbol,
            mirofish_confidence=d.get("mirofish_confidence", 0.7),
        )
        results.append(result)
    return {"batch_results": results, "count": len(results)}
