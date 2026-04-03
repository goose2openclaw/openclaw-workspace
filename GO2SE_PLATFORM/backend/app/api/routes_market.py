#!/usr/bin/env python3
"""
📊 实时市场数据 API路由
=======================
提供实时价格、趋势信号、K线数据
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import urllib.request
import math

router = APIRouter(prefix="/api/market")

BINANCE_BASE = "https://api.binance.com/api/v3"


def fetch_binance(endpoint: str) -> Optional[dict]:
    """请求Binance API"""
    url = f"{BINANCE_BASE}{endpoint}"
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            return json.loads(resp.read())
    except Exception:
        return None


class TickerResponse(BaseModel):
    """Ticker响应"""
    symbol: str
    price: float
    change_24h: float
    high_24h: float
    low_24h: float
    volume: float
    timestamp: str


# ============ 使用子路径避免被 {symbol} 匹配 ============

@router.get("/list/top-coins")
async def get_top_coins(limit: int = Query(10, ge=1, le=50)) -> Dict[str, Any]:
    """获取Top主流币"""
    data = fetch_binance("/ticker/24hr")
    if not data:
        return {"error": "Failed to fetch data"}
    
    usdt_pairs = [
        d for d in data 
        if d["symbol"].endswith("USDT") 
        and float(d["quoteVolume"]) > 1e7
    ]
    usdt_pairs.sort(key=lambda x: float(x["quoteVolume"]), reverse=True)
    
    return {
        "data": [
            {
                "symbol": d["symbol"],
                "price": float(d["lastPrice"]),
                "change_24h": float(d["priceChangePercent"]),
                "volume_24h": float(d["quoteVolume"]),
            }
            for d in usdt_pairs[:limit]
        ],
        "timestamp": datetime.now().isoformat()
    }


@router.get("/signals/beidou")
async def get_beidou_signals() -> Dict[str, Any]:
    """获取北斗七鑫工具信号"""
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]
    signals = {}
    
    for symbol in symbols:
        ticker = fetch_binance(f"/ticker/24hr?symbol={symbol}")
        if not ticker:
            continue
        
        price = float(ticker["lastPrice"])
        change = float(ticker["priceChangePercent"])
        trend = "BULLISH" if change > 2 else "BEARISH" if change < -2 else "NEUTRAL"
        
        if trend == "BULLISH":
            signals[symbol] = {"rabbit": "LONG", "mole": "SCAN", "leader": {"action": "LONG", "leverage": 2}}
        elif trend == "BEARISH":
            signals[symbol] = {"rabbit": "CLOSE", "mole": "SCAN", "leader": {"action": "SHORT", "leverage": 2}}
        else:
            signals[symbol] = {"rabbit": "HOLD", "mole": "HOLD", "leader": {"action": "HOLD", "leverage": 1}}
    
    return {"signals": signals, "timestamp": datetime.now().isoformat()}


@router.get("/signals/overview")
async def get_market_overview() -> Dict[str, Any]:
    """获取市场概览"""
    data = fetch_binance("/ticker/24hr")
    if not data:
        return {"error": "Failed to fetch data"}
    
    usdt_pairs = [
        {"symbol": d["symbol"], "change": float(d["priceChangePercent"]), "volume": float(d["quoteVolume"])}
        for d in data 
        if d["symbol"].endswith("USDT") and float(d["quoteVolume"]) > 1e7
    ]
    usdt_pairs.sort(key=lambda x: x["volume"], reverse=True)
    top10 = usdt_pairs[:10]
    
    bullish = sum(1 for d in top10 if d["change"] > 0)
    bearish = len(top10) - bullish
    
    sentiment = "EXTREMELY_BULLISH" if bullish >= 7 else "BULLISH" if bullish >= 5 else "NEUTRAL" if bullish >= 3 else "BEARISH" if bullish >= 1 else "EXTREMELY_BEARISH"
    
    return {
        "sentiment": sentiment,
        "bullish_count": bullish,
        "bearish_count": bearish,
        "top_gainers": sorted(top10, key=lambda x: x["change"], reverse=True)[:3],
        "top_losers": sorted(top10, key=lambda x: x["change"])[:3],
        "timestamp": datetime.now().isoformat()
    }


@router.get("/signal/{symbol}")
async def get_signal(symbol: str) -> Dict[str, Any]:
    """获取币种交易信号"""
    ticker = fetch_binance(f"/ticker/24hr?symbol={symbol.upper()}")
    if not ticker:
        raise HTTPException(status_code=404, detail="Symbol not found")
    
    price = float(ticker["lastPrice"])
    change = float(ticker["priceChangePercent"])
    
    klines = fetch_binance(f"/klines?symbol={symbol.upper()}&interval=1h&limit=100")
    
    rsi = 50.0
    if klines and len(klines) > 14:
        closes = [float(k[4]) for k in klines]
        deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
        gains = [d if d > 0 else 0 for d in deltas[-14:]]
        losses = [-d if d < 0 else 0 for d in deltas[-14:]]
        avg_gain = sum(gains) / 14
        avg_loss = sum(losses) / 14
        if avg_loss > 0:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
    
    rsi_signal = "OVERBOUGHT" if rsi > 70 else "OVERSOLD" if rsi < 30 else "NEUTRAL"
    trend = "BULLISH" if change > 2 else "BEARISH" if change < -2 else "NEUTRAL"
    
    if trend == "BULLISH" and rsi_signal == "OVERSOLD":
        signal = "STRONG_BUY"
    elif trend == "BULLISH":
        signal = "BUY"
    elif trend == "BEARISH" and rsi_signal == "OVERBOUGHT":
        signal = "STRONG_SELL"
    elif trend == "BEARISH":
        signal = "SELL"
    else:
        signal = "HOLD"
    
    return {
        "symbol": symbol.upper(),
        "price": price,
        "change_24h": change,
        "rsi": round(rsi, 2),
        "rsi_signal": rsi_signal,
        "trend": trend,
        "signal": signal,
        "confidence": 0.7 if signal in ["STRONG_BUY", "STRONG_SELL"] else 0.5,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/detect-regime-info")
async def detect_market_regime():
    """检测市场状态 (由routes_v7暴露)"""
    pass  # Moved to routes_v7.py
    """
    检测市场状态，用于AI资金调配
    返回: regime, volatility, trend_strength, volume, confidence
    """
    import asyncio
    try:
        btc = await asyncio.to_thread(fetch_binance, "/ticker/24hr?symbol=BTCUSDT")
        eth = await asyncio.to_thread(fetch_binance, "/ticker/24hr?symbol=ETHUSDT")
    except:
        return {"regime": "unknown", "volatility": 50, "trend_strength": 50, "volume": 50, "confidence": 30}

    if not btc or not eth:
        return {"regime": "unknown", "volatility": 50, "trend_strength": 50, "volume": 50, "confidence": 30}

    btc_vol = abs(float(btc.get("priceChangePercent", 0)))
    eth_vol = abs(float(eth.get("priceChangePercent", 0)))
    avg_vol = (btc_vol + eth_vol) / 2
    volatility = min(100, avg_vol * 10)

    btc_change = float(btc.get("priceChangePercent", 0))
    eth_change = float(eth.get("priceChangePercent", 0))
    avg_change = (btc_change + eth_change) / 2

    if avg_change > 3:
        trend = "trending_up"
        trend_strength = min(100, avg_change * 15)
    elif avg_change < -3:
        trend = "trending_down"
        trend_strength = min(100, abs(avg_change) * 15)
    elif volatility > 60:
        trend = "high_volatility"
        trend_strength = 50
    elif volatility < 30:
        trend = "low_volatility"
        trend_strength = 50
    else:
        trend = "range_bound"
        trend_strength = 50

    btc_vol_amt = float(btc.get("quoteVolume", 0))
    volume = min(100, btc_vol_amt / 1e9) if btc_vol_amt else 50

    confidence = min(95, 40 + (volatility if volatility > 50 else 100 - volatility) * 0.3)

    return {
        "regime": trend,
        "volatility": round(volatility, 1),
        "trend_strength": round(trend_strength, 1),
        "volume": round(volume, 1),
        "confidence": round(confidence, 1),
        "btc_change_pct": round(btc_change, 2),
        "eth_change_pct": round(eth_change, 2),
        "timestamp": datetime.now().isoformat()
    }


@router.get("/{symbol}")
async def get_ticker(symbol: str) -> TickerResponse:
    """获取币种24hr ticker"""
    data = fetch_binance(f"/ticker/24hr?symbol={symbol.upper()}")
    if not data:
        raise HTTPException(status_code=404, detail="Symbol not found")
    
    return TickerResponse(
        symbol=data["symbol"],
        price=float(data["lastPrice"]),
        change_24h=float(data["priceChangePercent"]),
        high_24h=float(data["highPrice"]),
        low_24h=float(data["lowPrice"]),
        volume=float(data["volume"]),
        timestamp=datetime.now().isoformat()
    )
