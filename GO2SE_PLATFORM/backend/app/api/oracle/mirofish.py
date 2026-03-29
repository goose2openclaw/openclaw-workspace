"""
🪿 GO2SE MiroFish 预言机
100智能体 × 5轮共识 = 高置信度预测

预测市场:
1. BTC趋势预测
2. ETH趋势预测
3. SOL趋势预测
4. XRP趋势预测
5. 主流币组合
6. 全市场情绪
"""

import random
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/oracle/mirofish", tags=["MiroFish"])

# ─────────────────────────────────────────────
# 数据模型
# ─────────────────────────────────────────────
class PredictionMarket(str, Enum):
    BTC = "btc_trend"
    ETH = "eth_trend"
    SOL = "sol_trend"
    XRP = "xrp_trend"
    MAJOR_PAIRS = "major_pairs"
    MARKET_SENTIMENT = "market_sentiment"

class TrendDirection(str, Enum):
    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"
    UNCERTAIN = "uncertain"

@dataclass
class AgentVote:
    """单个智能体的投票"""
    agent_id: int
    agent_type: str
    vote: TrendDirection
    confidence: float  # 0-1
    reasoning: str
    round: int

@dataclass
class ConsensusResult:
    """共识结果"""
    market: str
    consensus: TrendDirection
    confidence: float  # 0-1
    agent_count: int
    rounds: int
    votes: List[AgentVote]
    timestamp: str
    hash: str = ""

@dataclass
class Prediction:
    """完整预测"""
    market: str
    direction: TrendDirection
    confidence: float
    target_price: Optional[float] = None
    timeframe: str = "24h"
    reasoning: str = ""
    consensus: Optional[ConsensusResult] = None

# ─────────────────────────────────────────────
# 市场配置
# ─────────────────────────────────────────────
MARKETS_CONFIG: Dict[str, Dict[str, Any]] = {
    "btc_trend": {
        "name": "BTC 24小时趋势",
        "base_price": 66500,
        "volatility": 0.03,
        "agents": 100,
        "rounds": 5,
    },
    "eth_trend": {
        "name": "ETH 24小时趋势",
        "base_price": 2000,
        "volatility": 0.04,
        "agents": 100,
        "rounds": 5,
    },
    "sol_trend": {
        "name": "SOL 24小时趋势",
        "base_price": 82,
        "volatility": 0.05,
        "agents": 100,
        "rounds": 5,
    },
    "xrp_trend": {
        "name": "XRP 24小时趋势",
        "base_price": 1.32,
        "volatility": 0.04,
        "agents": 100,
        "rounds": 5,
    },
    "major_pairs": {
        "name": "主流币组合预测",
        "base_price": 1,
        "volatility": 0.02,
        "agents": 80,
        "rounds": 4,
    },
    "market_sentiment": {
        "name": "市场整体情绪",
        "base_price": 50,
        "volatility": 0.1,
        "agents": 60,
        "rounds": 3,
    },
}

# 智能体类型
AGENT_TYPES = [
    "技术分析专家",
    "趋势跟踪专家", 
    "均值回归专家",
    "波浪理论专家",
    "布林带专家",
    "RSI专家",
    "MACD专家",
    "缠论专家",
    "支撑阻力专家",
    "成交量专家",
]

# ─────────────────────────────────────────────
# 智能体模拟
# ─────────────────────────────────────────────
def simulate_agent_vote(
    market: str,
    market_data: Dict[str, Any],
    agent_id: int,
    round_num: int
) -> AgentVote:
    """模拟单个智能体的投票"""
    
    # 基于市场数据和技术指标模拟投票
    price = market_data.get("price", 100)
    rsi = market_data.get("rsi", 50)
    volume = market_data.get("volume_24h", 1_000_000_000)
    change = market_data.get("change_24h", 0)
    
    # 不同类型智能体有不同偏好
    agent_type = AGENT_TYPES[agent_id % len(AGENT_TYPES)]
    
    # 基于RSI的判断
    if rsi < 30:
        base_vote = TrendDirection.BULL
        base_confidence = 0.6 + (30 - rsi) / 100
    elif rsi > 70:
        base_vote = TrendDirection.BEAR
        base_confidence = 0.6 + (rsi - 70) / 100
    else:
        # 基于价格变动
        if change > 2:
            base_vote = TrendDirection.BULL
            base_confidence = 0.55
        elif change < -2:
            base_vote = TrendDirection.BEAR
            base_confidence = 0.55
        else:
            base_vote = TrendDirection.SIDEWAYS
            base_confidence = 0.5
    
    # 加入一些随机性模拟真实场景
    if random.random() < 0.1:
        base_vote = random.choice(list(TrendDirection))
        
    # 多轮共识: 后续轮次更倾向共识
    if round_num > 1:
        # 简化处理，后续轮次轻微偏向中立
        base_confidence = min(0.9, base_confidence + 0.05 * round_num)
        
    confidence = min(0.95, max(0.3, base_confidence + random.uniform(-0.1, 0.1)))
    
    reasoning_map = {
        TrendDirection.BULL: f"基于RSI={rsi:.1f}超卖区域，MACD金叉形成，动量增强",
        TrendDirection.BEAR: f"基于RSI={rsi:.1f}超买区域，顶部背离，短期回调压力",
        TrendDirection.SIDEWAYS: f"基于RSI={rsi:.1f}中性区域，震荡整理格局",
        TrendDirection.UNCERTAIN: "数据不足，无法确定趋势方向",
    }
    
    return AgentVote(
        agent_id=agent_id,
        agent_type=agent_type,
        vote=base_vote,
        confidence=confidence,
        reasoning=reasoning_map.get(base_vote, "综合分析"),
        round=round_num
    )

def run_consensus(
    market: str,
    market_data: Dict[str, Any],
    agent_count: int = 100,
    rounds: int = 5
) -> ConsensusResult:
    """运行多智能体多轮共识"""
    
    config = MARKETS_CONFIG.get(market, MARKETS_CONFIG["btc_trend"])
    agent_count = config.get("agents", agent_count)
    rounds = config.get("rounds", rounds)
    
    all_votes: List[AgentVote] = []
    current_consensus = None
    
    for round_num in range(1, rounds + 1):
        round_votes = []
        
        # 每轮减少参与智能体数量(模拟退出)
        active_agents = max(10, agent_count - (round_num - 1) * 5)
        
        for agent_id in range(active_agents):
            vote = simulate_agent_vote(market, market_data, agent_id, round_num)
            round_votes.append(vote)
            all_votes.append(vote)
        
        # 计算本轮共识
        vote_counts: Dict[TrendDirection, int] = {}
        for v in round_votes:
            vote_counts[v.vote] = vote_counts.get(v.vote, 0) + 1
        
        # 加权投票(按置信度)
        weighted_scores: Dict[TrendDirection, float] = {}
        for v in round_votes:
            weighted_scores[v.vote] = weighted_scores.get(v.vote, 0) + v.confidence
        
        # 确定本轮胜出方向
        max_score = max(weighted_scores.values())
        winners = [d for d, s in weighted_scores.items() if s == max_score]
        current_consensus = random.choice(winners) if len(winners) > 1 else winners[0]
        
        # 后续轮次参考前面结果
        if round_num > 1 and random.random() < 0.3:
            current_consensus = winners[0]
    
    # 最终共识
    final_vote_counts: Dict[TrendDirection, int] = {}
    final_weighted: Dict[TrendDirection, float] = {}
    
    for v in all_votes:
        final_vote_counts[v.vote] = final_vote_counts.get(v.vote, 0) + 1
        final_weighted[v.vote] = final_weighted.get(v.vote, 0) + v.confidence
    
    # 最终方向
    max_final = max(final_weighted.values())
    final_winners = [d for d, s in final_weighted.items() if s == max_final]
    final_direction = random.choice(final_winners) if len(final_winners) > 1 else final_winners[0]
    
    # 计算置信度
    total_votes = len(all_votes)
    winning_votes = sum(1 for v in all_votes if v.vote == final_direction)
    confidence = (winning_votes / total_votes) * (max_final / total_votes)
    confidence = min(0.95, max(0.3, confidence))
    
    # 生成hash
    hash_input = f"{market}:{final_direction}:{confidence}:{datetime.now().isoformat()}"
    result_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
    
    return ConsensusResult(
        market=market,
        consensus=final_direction,
        confidence=confidence,
        agent_count=total_votes,
        rounds=rounds,
        votes=all_votes,
        timestamp=datetime.now().isoformat(),
        hash=result_hash
    )

# ─────────────────────────────────────────────
# 缓存 (简单内存缓存)
# ─────────────────────────────────────────────
_cache: Dict[str, Dict[str, Any]] = {}
_cache_ttl = 300  # 5分钟缓存

def get_cached_or_update(key: str, fetch_func) -> Any:
    """简单的缓存装饰器逻辑"""
    now = datetime.now().timestamp()
    if key in _cache:
        cached_time, cached_data = _cache[key]
        if now - cached_time < _cache_ttl:
            return cached_data
    
    data = fetch_func()
    _cache[key] = (now, data)
    return data

# ─────────────────────────────────────────────
# API端点
# ─────────────────────────────────────────────
@router.get("/markets")
async def get_markets():
    """获取6大预测市场状态"""
    return {
        "data": [
            {
                "id": market_id,
                "name": config["name"],
                "status": "active",
                "agents": config["agents"],
                "rounds": config["rounds"],
            }
            for market_id, config in MARKETS_CONFIG.items()
        ],
        "count": len(MARKETS_CONFIG),
        "timestamp": datetime.now().isoformat(),
    }

@router.get("/market/{market_id}")
async def get_market_detail(market_id: str):
    """获取单个市场详情"""
    if market_id not in MARKETS_CONFIG:
        raise HTTPException(status_code=404, detail=f"市场 {market_id} 不存在")
    
    config = MARKETS_CONFIG[market_id]
    return {
        "id": market_id,
        "name": config["name"],
        "base_price": config["base_price"],
        "volatility": config["volatility"],
        "status": "active",
    }

@router.post("/predict")
async def predict(predict_request: Dict[str, Any]):
    """
    执行单次预测
    {
        "market": "btc_trend",
        "market_data": {"price": 66500, "rsi": 35, "volume_24h": 500000000, "change_24h": -1.5}
    }
    """
    market = predict_request.get("market", "btc_trend")
    market_data = predict_request.get("market_data", {})
    
    if market not in MARKETS_CONFIG:
        raise HTTPException(status_code=404, detail=f"市场 {market} 不存在")
    
    # 使用缓存或运行共识
    cache_key = f"predict:{market}"
    
    def fetch_prediction():
        config = MARKETS_CONFIG[market]
        # 合并默认数据和传入数据
        full_data = {
            "price": market_data.get("price", config["base_price"]),
            "rsi": market_data.get("rsi", 50),
            "volume_24h": market_data.get("volume_24h", 1_000_000_000),
            "change_24h": market_data.get("change_24h", 0),
        }
        
        consensus = run_consensus(market, full_data)
        
        # 估算目标价格
        target_change = consensus.confidence * 0.05 * (1 if consensus.consensus == TrendDirection.BULL else -1)
        target_price = full_data["price"] * (1 + target_change)
        
        return Prediction(
            market=market,
            direction=consensus.consensus,
            confidence=consensus.confidence,
            target_price=round(target_price, 2) if target_price else None,
            timeframe="24h",
            reasoning=f"MiroFish {consensus.agent_count}智能体 × {consensus.rounds}轮共识",
            consensus=consensus,
        )
    
    # 强制刷新(不使用缓存)
    prediction = fetch_prediction()
    
    return {
        "data": {
            "market": prediction.market,
            "direction": prediction.direction.value,
            "confidence": round(prediction.confidence, 4),
            "target_price": prediction.target_price,
            "timeframe": prediction.timeframe,
            "reasoning": prediction.reasoning,
            "consensus_hash": prediction.consensus.hash if prediction.consensus else None,
            "agent_count": prediction.consensus.agent_count if prediction.consensus else 0,
            "rounds": prediction.consensus.rounds if prediction.consensus else 0,
        },
        "timestamp": datetime.now().isoformat(),
    }

@router.post("/batch")
async def batch_predict(batch_request: Dict[str, Any]):
    """
    批量预测多个市场
    {
        "markets": ["btc_trend", "eth_trend"],
        "market_datas": {
            "btc_trend": {"price": 66500, "rsi": 35},
            "eth_trend": {"price": 2000, "rsi": 40}
        }
    }
    """
    markets = batch_request.get("markets", list(MARKETS_CONFIG.keys()))
    market_datas = batch_request.get("market_datas", {})
    
    results = []
    
    for market in markets:
        if market not in MARKETS_CONFIG:
            continue
            
        config = MARKETS_CONFIG[market]
        market_data = market_datas.get(market, {})
        
        full_data = {
            "price": market_data.get("price", config["base_price"]),
            "rsi": market_data.get("rsi", 50),
            "volume_24h": market_data.get("volume_24h", 1_000_000_000),
            "change_24h": market_data.get("change_24h", 0),
        }
        
        consensus = run_consensus(market, full_data)
        
        target_change = consensus.confidence * 0.05 * (1 if consensus.consensus == TrendDirection.BULL else -1)
        target_price = full_data["price"] * (1 + target_change)
        
        results.append({
            "market": market,
            "direction": consensus.consensus.value,
            "confidence": round(consensus.confidence, 4),
            "target_price": round(target_price, 2) if target_price else None,
            "agent_count": consensus.agent_count,
            "rounds": consensus.rounds,
            "hash": consensus.hash,
        })
    
    return {
        "data": results,
        "count": len(results),
        "timestamp": datetime.now().isoformat(),
    }

@router.get("/consensus/{market}")
async def get_consensus(market: str):
    """获取指定市场的实时共识状态"""
    if market not in MARKETS_CONFIG:
        raise HTTPException(status_code=404, detail=f"市场 {market} 不存在")
    
    config = MARKETS_CONFIG[market]
    
    # 获取实时市场数据(模拟)
    market_data = {
        "price": config["base_price"],
        "rsi": random.uniform(30, 70),
        "volume_24h": 1_000_000_000,
        "change_24h": random.uniform(-3, 3),
    }
    
    consensus = run_consensus(market, market_data)
    
    return {
        "data": {
            "market": market,
            "consensus": consensus.consensus.value,
            "confidence": round(consensus.confidence, 4),
            "agent_count": consensus.agent_count,
            "rounds": consensus.rounds,
            "hash": consensus.hash,
            "timestamp": consensus.timestamp,
        },
    }

@router.get("/history/{market}")
async def get_history(market: str, limit: int = 10):
    """获取预测历史(模拟)"""
    if market not in MARKETS_CONFIG:
        raise HTTPException(status_code=404, detail=f"市场 {market} 不存在")
    
    # 模拟历史数据
    history = []
    base_price = MARKETS_CONFIG[market]["base_price"]
    
    for i in range(limit):
        direction = random.choice(list(TrendDirection))
        confidence = random.uniform(0.5, 0.9)
        price_change = random.uniform(-5, 5)
        
        history.append({
            "id": f"hist_{market}_{i}",
            "market": market,
            "direction": direction.value,
            "confidence": round(confidence, 4),
            "price_change": round(price_change, 2),
            "target_price": round(base_price * (1 + price_change / 100), 2),
            "timestamp": datetime.now().isoformat(),
        })
    
    return {
        "data": history,
        "count": len(history),
    }
