"""
交易路由 - 交易、持仓、统计相关API
2026-04-04 重构版本
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/api", tags=["交易"])

# ==================== 内存缓存 ====================

_cache: dict = {}
_CACHE_TTL_STATS = 8
_CACHE_TTL_PORTFOLIO = 10

def _cache_get(key: str, ttl: int) -> Optional[dict]:
    import time
    item = _cache.get(key)
    if item is None:
        return None
    data, expire_ts = item
    if time.time() > expire_ts:
        del _cache[key]
        return None
    return data

def _cache_set(key: str, data: dict, ttl: int):
    import time
    _cache[key] = (data, time.time() + ttl)


# ==================== 交易端点 ====================

@router.get("/trades")
async def get_trades(limit: int = 50):
    """获取交易历史"""
    # 模拟数据
    trades = [
        {"id": "t1", "symbol": "BTC", "side": "buy", "pnl": 125.50, "date": "2026-04-04"},
        {"id": "t2", "symbol": "ETH", "side": "sell", "pnl": -45.20, "date": "2026-04-03"},
    ]
    return {"trades": trades[:limit], "total": len(trades)}


@router.get("/positions")
async def get_positions():
    """获取当前持仓"""
    positions = [
        {"symbol": "BTC", "side": "long", "size": 0.15, "entry": 67450, "current": 68120, "pnl": 100.50},
        {"symbol": "ETH", "side": "long", "size": 1.2, "entry": 3520, "current": 3580, "pnl": 72.00},
    ]
    return {"positions": positions}


@router.post("/trade")
async def execute_trade(trade: dict):
    """执行交易"""
    return {
        "status": "success",
        "message": "交易执行成功 (dry_run模式)",
        "trade_id": f"trade_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    }


@router.get("/stats")
async def get_stats():
    """获取统计信息"""
    cached = _cache_get("stats", _CACHE_TTL_STATS)
    if cached:
        return cached
    
    stats = {
        "total_trades": 247,
        "win_trades": 178,
        "loss_trades": 69,
        "win_rate": 72.1,
        "total_pnl": 1847.32,
        "sharpe_ratio": 2.34,
        "max_drawdown": -6.2,
    }
    
    _cache_set("stats", stats, _CACHE_TTL_STATS)
    return stats


@router.get("/portfolio")
async def get_portfolio():
    """获取投资组合"""
    cached = _cache_get("portfolio", _CACHE_TTL_PORTFOLIO)
    if cached:
        return cached
    
    portfolio = {
        "total_value": 11847.32,
        "positions_value": 6847.32,
        "cash": 5000.00,
        "daily_pnl": 423.50,
        "daily_return": 3.71,
    }
    
    _cache_set("portfolio", portfolio, _CACHE_TTL_PORTFOLIO)
    return portfolio
