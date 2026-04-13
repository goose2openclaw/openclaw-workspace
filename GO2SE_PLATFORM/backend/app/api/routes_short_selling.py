#!/usr/bin/env python3
"""
📉 做空机制 + 强化推荐 API路由
================================
支持做多/做空双向交易
强化推荐引擎 V2
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import time

router = APIRouter(prefix="/api/short", tags=["做空机制"])


# ─── Request/Response Models ────────────────────────────────────

class MarketIndicatorsRequest(BaseModel):
    """市场指标请求"""
    symbol: str = "BTCUSDT"
    price: float
    change_24h: float
    volume_24h: float
    rsi: float
    macd: float
    macd_signal: float
    bollinger_upper: float
    bollinger_lower: float
    whale_buy_ratio: float = 0.5
    whale_sell_ratio: float = 0.5
    volume_surge: float = 1.0


class RecommendationRequest(BaseModel):
    """推荐请求"""
    symbol: str = "BTCUSDT"
    indicators: MarketIndicatorsRequest
    prefer_direction: str = "auto"  # "long", "short", "auto"


class ShortPositionRequest(BaseModel):
    """做空仓位请求"""
    symbol: str = "BTCUSDT"
    quantity: float = Field(..., gt=0, description="合约张数")
    leverage: int = Field(default=3, ge=2, le=10, description="杠杆倍数")
    stop_loss_pct: Optional[float] = Field(default=0.05, description="止损百分比")
    take_profit_pct: Optional[float] = Field(default=0.15, description="止盈百分比")
    dry_run: bool = True


class LongPositionRequest(BaseModel):
    """做多仓位请求"""
    symbol: str = "BTCUSDT"
    quantity: float = Field(..., gt=0)
    leverage: int = Field(default=3, ge=2, le=10)
    stop_loss_pct: Optional[float] = 0.05
    take_profit_pct: Optional[float] = 0.15
    dry_run: bool = True


# ─── 辅助函数 ───────────────────────────────────────────────

def _sim_ticker(symbol: str) -> dict:
    """模拟行情数据"""
    import random
    price = 75000 if "BTC" in symbol else 3500
    return {
        "symbol": symbol,
        "price": price,
        "change_24h": random.uniform(-8, 8),
        "volume_24h": random.uniform(1e8, 5e8),
        "rsi": random.uniform(20, 80),
        "macd": random.uniform(-100, 100),
        "macd_signal": random.uniform(-100, 100),
        "bollinger_upper": price * 1.03,
        "bollinger_lower": price * 0.97,
        "whale_buy_ratio": random.uniform(0.3, 0.7),
        "whale_sell_ratio": random.uniform(0.3, 0.7),
        "volume_surge": random.uniform(0.5, 3.0),
    }


# ─── 推荐引擎 ───────────────────────────────────────────────

def _calc_long_confidence(m: dict) -> float:
    score = 0.0
    if m["rsi"] <= 30: score += 0.25
    elif m["rsi"] <= 40: score += 0.15
    if m["change_24h"] >= 3: score += 0.20
    elif m["change_24h"] >= 1: score += 0.10
    if m["macd"] > m["macd_signal"]: score += 0.20
    if m["price"] <= m["bollinger_lower"] * 1.02: score += 0.15
    if m["whale_buy_ratio"] >= 0.60: score += 0.15
    if m["volume_surge"] >= 2.0: score += 0.10
    return min(0.99, score / 1.05)


def _calc_short_confidence(m: dict) -> float:
    score = 0.0
    if m["rsi"] >= 70: score += 0.25
    elif m["rsi"] >= 60: score += 0.15
    if m["change_24h"] <= -3: score += 0.20
    elif m["change_24h"] <= -1: score += 0.10
    if m["macd"] < m["macd_signal"]: score += 0.20
    if m["price"] >= m["bollinger_upper"] * 0.98: score += 0.15
    if m["whale_sell_ratio"] >= 0.60: score += 0.15
    if m["volume_surge"] >= 2.0: score += 0.10
    return min(0.99, score / 1.05)


def _select_tier_long(confidence: float) -> dict:
    if confidence >= 0.75: return {"name": "保守做多", "leverage": 2, "max_position": 0.10, "stop_loss": 0.03, "take_profit": 0.08}
    elif confidence >= 0.60: return {"name": "平衡做多", "leverage": 3, "max_position": 0.20, "stop_loss": 0.05, "take_profit": 0.15}
    else: return {"name": "激进做多", "leverage": 5, "max_position": 0.25, "stop_loss": 0.08, "take_profit": 0.25}


def _select_tier_short(confidence: float) -> dict:
    if confidence >= 0.78: return {"name": "保守做空", "leverage": 2, "max_position": 0.08, "stop_loss": 0.04, "take_profit": 0.10}
    elif confidence >= 0.68: return {"name": "平衡做空", "leverage": 3, "max_position": 0.15, "stop_loss": 0.06, "take_profit": 0.18}
    else: return {"name": "激进做空", "leverage": 5, "max_position": 0.20, "stop_loss": 0.10, "take_profit": 0.30}


# ─── Routes ──────────────────────────────────────────────────

@router.get("/ticker/{symbol}")
async def get_ticker(symbol: str):
    """获取合约行情"""
    try:
        from app.core.binance_futures import get_trader
        trader = get_trader()
        ticker = trader.get_ticker(symbol)
        return {"success": True, "data": ticker}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/recommend")
async def get_recommendation(req: RecommendationRequest):
    """
    🎯 获取强化推荐（支持做多做空）
    """
    m = req.indicators
    long_conf = _calc_long_confidence(m.__dict__)
    short_conf = _calc_short_confidence(m.__dict__)

    prefer = req.prefer_direction
    if prefer == "long" and long_conf > 0.5:
        direction, confidence = "LONG", long_conf
    elif prefer == "short" and short_conf > 0.5:
        direction, confidence = "SHORT", short_conf
    elif long_conf > short_conf + 0.05:
        direction, confidence = "LONG", long_conf
    elif short_conf > long_conf + 0.05:
        direction, confidence = "SHORT", short_conf
    else:
        direction, confidence = "HOLD", max(long_conf, short_conf)

    # 平仓信号
    if direction == "LONG" and m.change_24h < -5:
        direction, confidence = "CLOSE_SHORT", min(1.0, abs(m.change_24h) / 5 * 0.8)
    elif direction == "SHORT" and m.change_24h > 5:
        direction, confidence = "CLOSE_LONG", min(1.0, m.change_24h / 5 * 0.8)

    if direction == "LONG":
        tier = _select_tier_long(confidence)
    elif direction == "SHORT":
        tier = _select_tier_short(confidence)
    else:
        tier = {"name": "观望", "leverage": 1, "max_position": 0, "stop_loss": 0, "take_profit": 0}

    reasons = []
    if direction == "LONG":
        if m.rsi <= 30: reasons.append(f"RSI超卖({m.rsi:.1f})")
        if m.change_24h >= 3: reasons.append(f"价格反弹({m.change_24h:+.1f}%)")
        if m.macd > m.macd_signal: reasons.append("MACD金叉")
    elif direction == "SHORT":
        if m.rsi >= 70: reasons.append(f"RSI过热({m.rsi:.1f})")
        if m.change_24h <= -3: reasons.append(f"价格回落({m.change_24h:+.1f}%)")
        if m.macd < m.macd_signal: reasons.append("MACD死叉")
    else:
        reasons.append("多空信号均衡")
    reasons.append(f"置信度{confidence:.0%}")

    strength = "STRONG" if confidence >= 0.80 else "NORMAL"

    return {
        "success": True,
        "symbol": req.symbol,
        "direction": direction,
        "strength": strength,
        "confidence": round(confidence, 3),
        "leverage": tier.get("leverage", 1),
        "position_size": tier.get("max_position", 0),
        "stop_loss": tier.get("stop_loss", 0),
        "take_profit": tier.get("take_profit", 0),
        "tier": tier.get("name", "观望"),
        "reasons": reasons,
        "long_confidence": round(long_conf, 3),
        "short_confidence": round(short_conf, 3),
        "timestamp": datetime.now().isoformat(),
    }


@router.post("/recommend/batch")
async def batch_recommend(symbols: List[str]):
    """批量推荐（返回所有币种评分）"""
    results = []
    for symbol in symbols:
        try:
            data = _sim_ticker(symbol)
            m = MarketIndicatorsRequest(**data)
            req = RecommendationRequest(symbol=symbol, indicators=m)
            rec = await get_recommendation(req)
            results.append(rec)
        except Exception as e:
            results.append({"symbol": symbol, "success": False, "error": str(e)})
    # 按置信度排序
    results.sort(key=lambda x: x.get("confidence", 0), reverse=True)
    return {"success": True, "results": results, "timestamp": datetime.now().isoformat()}


@router.post("/short/open")
async def open_short_position(req: ShortPositionRequest):
    """📉 开做空仓位"""
    try:
        from app.core.binance_futures import get_trader
        trader = get_trader()
        # 计算止损止盈价格
        ticker = trader.get_ticker(req.symbol)
        price = ticker["price"]
        sl = price * (1 + req.stop_loss_pct) if req.stop_loss_pct else None
        tp = price * (1 - req.take_profit_pct) if req.take_profit_pct else None
        result = trader.place_order(
            symbol=req.symbol,
            side="SELL",
            position_side="SHORT",
            quantity=req.quantity,
            leverage=req.leverage,
            stop_loss=sl,
            take_profit=tp,
        )
        result["mode"] = "DRY_RUN" if req.dry_run else "LIVE"
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/long/open")
async def open_long_position(req: LongPositionRequest):
    """📈 开做多仓位"""
    try:
        from app.core.binance_futures import get_trader
        trader = get_trader()
        ticker = trader.get_ticker(req.symbol)
        price = ticker["price"]
        sl = price * (1 - req.stop_loss_pct) if req.stop_loss_pct else None
        tp = price * (1 + req.take_profit_pct) if req.take_profit_pct else None
        result = trader.place_order(
            symbol=req.symbol,
            side="BUY",
            position_side="LONG",
            quantity=req.quantity,
            leverage=req.leverage,
            stop_loss=sl,
            take_profit=tp,
        )
        result["mode"] = "DRY_RUN" if req.dry_run else "LIVE"
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/position/close")
async def close_position(symbol: str, position_side: str = "SHORT"):
    """平仓"""
    try:
        from app.core.binance_futures import get_trader
        trader = get_trader()
        result = trader.close_position(symbol, position_side)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/position/{symbol}")
async def get_position(symbol: str):
    """查询仓位"""
    try:
        from app.core.binance_futures import get_trader
        trader = get_trader()
        return {"success": True, "data": trader.get_position(symbol)}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/leverage-tiers")
async def get_leverage_tiers():
    """获取杠杆档位"""
    return {
        "success": True,
        "long_tiers": {
            "conservative": {"leverage": 2, "max_position": "10%", "min_confidence": "75%"},
            "moderate": {"leverage": 3, "max_position": "20%", "min_confidence": "65%"},
            "aggressive": {"leverage": 5, "max_position": "25%", "min_confidence": "55%"},
        },
        "short_tiers": {
            "conservative": {"leverage": 2, "max_position": "8%", "min_confidence": "78%"},
            "moderate": {"leverage": 3, "max_position": "15%", "min_confidence": "68%"},
            "aggressive": {"leverage": 5, "max_position": "20%", "min_confidence": "58%"},
        },
        "note": "做空仓位上限为做多的80%，置信度要求更高"
    }
