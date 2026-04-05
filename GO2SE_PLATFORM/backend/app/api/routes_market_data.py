"""
市场数据路由 - 行情、K线、实时数据
2026-04-04 重构版本
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
import time

router = APIRouter(prefix="/api", tags=["市场数据"])

# ==================== 缓存配置 ====================

_cache: dict = {}
_CACHE_TTL_MARKET = 15
_CACHE_MAX_AGE_MARKET = 60

def _cache_get_market(key: str) -> Optional[dict]:
    item = _cache.get(key)
    if item is None:
        return None
    data, expire_ts = item
    if time.time() > expire_ts:
        del _cache[key]
        return None
    return data

def _cache_set_market(key: str, data: dict, ttl: int = _CACHE_TTL_MARKET):
    _cache[key] = (data, time.time() + ttl)


# ==================== 市场数据端点 ====================

@router.get("/market")
async def get_market_data(limit: int = 20):
    """获取市场行情"""
    cached = _cache_get_market("market_list")
    if cached:
        return cached
    
    market_data = [
        {"symbol": "BTC", "price": 68120.50, "change_24h": 2.34, "volume": 28500000000},
        {"symbol": "ETH", "price": 3580.25, "change_24h": 1.87, "volume": 15200000000},
        {"symbol": "BNB", "price": 412.30, "change_24h": 0.95, "volume": 1850000000},
        {"symbol": "SOL", "price": 145.80, "change_24h": 3.21, "volume": 3200000000},
        {"symbol": "XRP", "price": 0.5234, "change_24h": -0.45, "volume": 1200000000},
    ]
    
    result = {"market": market_data[:limit], "timestamp": time.time()}
    _cache_set_market("market_list", result)
    
    return result


@router.get("/market/{symbol}")
async def get_market_symbol(symbol: str):
    """获取指定币种行情"""
    symbol = symbol.upper()
    cached = _cache_get_market(f"market_{symbol}")
    if cached:
        return cached
    
    # 模拟数据
    prices = {
        "BTC": 68120.50, "ETH": 3580.25, "BNB": 412.30,
        "SOL": 145.80, "XRP": 0.5234, "ADA": 0.4521,
        "DOGE": 0.1234, "DOT": 7.89
    }
    
    if symbol not in prices:
        raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
    
    data = {
        "symbol": symbol,
        "price": prices[symbol],
        "change_24h": 2.34,
        "high_24h": prices[symbol] * 1.03,
        "low_24h": prices[symbol] * 0.97,
        "volume_24h": 1000000000,
        "timestamp": time.time()
    }
    
    _cache_set_market(f"market_{symbol}", data)
    return data


@router.get("/klines/{symbol}")
async def get_klines(symbol: str, interval: str = "1h", limit: int = 100):
    """获取K线数据"""
    symbol = symbol.upper()
    
    # 模拟K线数据
    klines = []
    base_price = 68000 if symbol == "BTC" else 3500
    
    for i in range(limit):
        import random
        klines.append({
            "timestamp": int(time.time()) - (limit - i) * 3600,
            "open": base_price * (1 + random.uniform(-0.02, 0.02)),
            "high": base_price * (1 + random.uniform(0, 0.03)),
            "low": base_price * (1 + random.uniform(-0.03, 0)),
            "close": base_price * (1 + random.uniform(-0.02, 0.02)),
            "volume": random.uniform(100, 1000)
        })
    
    return {"symbol": symbol, "interval": interval, "klines": klines}
