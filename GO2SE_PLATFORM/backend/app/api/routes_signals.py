"""
信号路由 - 信号、策略相关API
2026-04-04 重构版本
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
import time

router = APIRouter(prefix="/api", tags=["信号"])

# ==================== 信号端点 ====================

@router.get("/signals")
async def get_signals(symbol: Optional[str] = None, limit: int = 50):
    """获取交易信号"""
    signals = [
        {
            "id": "sig1",
            "symbol": "BTC",
            "strategy": "ema_cross",
            "signal": "buy",
            "confidence": 85,
            "price": 68120.50,
            "timestamp": "2026-04-04T12:00:00Z"
        },
        {
            "id": "sig2",
            "symbol": "ETH",
            "strategy": "macd",
            "signal": "hold",
            "confidence": 62,
            "price": 3580.25,
            "timestamp": "2026-04-04T12:00:00Z"
        },
    ]
    
    if symbol:
        signals = [s for s in signals if s["symbol"] == symbol.upper()]
    
    return {"signals": signals[:limit], "total": len(signals)}


@router.post("/signals/{strategy}/run")
async def run_strategy(strategy: str, symbols: List[str] = ["BTC", "ETH"]):
    """运行指定策略"""
    results = []
    
    for symbol in symbols:
        results.append({
            "symbol": symbol,
            "strategy": strategy,
            "signal": "buy" if symbol == "BTC" else "hold",
            "confidence": 75 + hash(symbol) % 20,
            "indicators": {
                "RSI": 55,
                "MACD": 0.5,
                "EMA20": 68100
            }
        })
    
    return {
        "status": "success",
        "strategy": strategy,
        "results": results,
        "timestamp": time.time()
    }


@router.get("/strategies")
async def get_strategies():
    """获取可用策略列表"""
    strategies = [
        {"name": "ema_cross", "description": "EMA交叉策略", "enabled": True, "win_rate": 72.5},
        {"name": "macd", "description": "MACD策略", "enabled": True, "win_rate": 68.3},
        {"name": "bollinger", "description": "布林带策略", "enabled": True, "win_rate": 65.8},
        {"name": "rsi_extreme", "description": "RSI极端策略", "enabled": True, "win_rate": 70.2},
        {"name": "supertrend", "description": "超级趋势策略", "enabled": True, "win_rate": 71.5},
    ]
    
    return {"strategies": strategies, "total": len(strategies)}


@router.get("/sonar/stats")
async def get_sonar_stats():
    """获取声纳库统计"""
    return {
        "total_models": 60,
        "categories": 12,
        "trending": {
            "bullish": 8,
            "bearish": 3,
            "neutral": 5
        },
        "timestamp": time.time()
    }
