#!/usr/bin/env python3
"""
🪿 GO2SE 实时行情 API
"""

from fastapi import APIRouter, Query
from typing import Optional
import json
import time

router = APIRouter(prefix="/api/market", tags=["实时行情"])

# 缓存
_cached_data = {"timestamp": 0, "data": None}
CACHE_TTL = 10  # 10秒缓存

@router.get("/ticker/{symbol}")
async def get_ticker(symbol: str = "BTC/USDT"):
    """获取单个币种实时行情"""
    from app.core.realtime_market import fetch_ticker
    return fetch_ticker(symbol.upper())

@router.get("/tickers")
async def get_all_tickers():
    """获取所有主流币实时行情"""
    global _cached_data
    
    # 简单缓存
    now = time.time()
    if _cached_data["data"] and (now - _cached_data["timestamp"]) < CACHE_TTL:
        return _cached_data["data"]
    
    from app.core.realtime_market import fetch_all_tickers
    data = {"markets": fetch_all_tickers()}
    
    _cached_data = {"timestamp": now, "data": data}
    return data

@router.get("/summary")
async def get_market_summary():
    """获取市场摘要"""
    from app.core.realtime_market import get_market_summary
    return get_market_summary()

@router.get("/orderbook/{symbol}")
async def get_orderbook(symbol: str = "BTC/USDT", limit: int = Query(10, ge=1, le=50)):
    """获取订单簿"""
    from app.core.realtime_market import fetch_order_book
    return fetch_order_book(symbol.upper(), limit)

@router.get("/trades/{symbol}")
async def get_trades(symbol: str = "BTC/USDT", limit: int = Query(20, ge=1, le=100)):
    """获取最近成交"""
    from app.core.realtime_market import fetch_trades
    return {"trades": fetch_trades(symbol.upper(), limit)}

@router.get("/prices")
async def get_prices(symbols: str = "BTC,ETH,SOL"):
    """批量获取价格"""
    from app.core.realtime_market import fetch_ticker
    
    symbol_list = [s.strip().upper() + "/USDT" for s in symbols.split(",")]
    prices = {}
    
    for sym in symbol_list:
        try:
            ticker = fetch_ticker(sym)
            if "error" not in ticker:
                prices[sym] = {
                    "price": ticker.get("price", 0),
                    "change_24h": ticker.get("change_24h", 0),
                    "rsi": ticker.get("rsi", 50)
                }
        except:
            pass
    
    return {"prices": prices, "timestamp": time.time()}

@router.get("/signals")
async def get_signals():
    """获取所有币种信号"""
    from app.core.realtime_market import fetch_all_tickers
    
    markets = fetch_all_tickers()
    signals = []
    
    for m in markets:
        rsi = m.get("rsi", 50)
        change = m.get("change_24h", 0)
        
        # 信号逻辑
        if rsi < 30:
            signal = "buy"
            reason = f"RSI超卖: {rsi}"
        elif rsi > 70:
            signal = "sell"
            reason = f"RSI超买: {rsi}"
        elif rsi < 40:
            signal = "buy"
            reason = f"RSI偏低: {rsi}"
        elif rsi > 60:
            signal = "sell"
            reason = f"RSI偏高: {rsi}"
        else:
            signal = "hold"
            reason = f"RSI中性: {rsi}"
        
        signals.append({
            "symbol": m["symbol"],
            "price": m.get("price", 0),
            "change_24h": change,
            "rsi": rsi,
            "signal": signal,
            "reason": reason
        })
    
    # 统计
    buy_signals = [s for s in signals if s["signal"] == "buy"]
    sell_signals = [s for s in signals if s["signal"] == "sell"]
    
    return {
        "signals": signals,
        "summary": {
            "total": len(signals),
            "buy": len(buy_signals),
            "sell": len(sell_signals),
            "hold": len(signals) - len(buy_signals) - len(sell_signals)
        }
    }
