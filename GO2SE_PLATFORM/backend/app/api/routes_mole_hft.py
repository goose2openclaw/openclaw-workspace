"""
🐹 打地鼠高频套利 API
2026-04-04
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import asyncio
import time

router = APIRouter(prefix="/api/mole", tags=["打地鼠高频"])

# 全局策略实例
_mole_v3_instance = None

async def get_mole_v3():
    global _mole_v3_instance
    if _mole_v3_instance is None:
        from app.core.mole_v3_strategy import MoleV3Strategy
        _mole_v3_instance = MoleV3Strategy()
    return _mole_v3_instance


class HFTScanRequest(BaseModel):
    symbols: List[str] = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]


class HFTScanResponse(BaseModel):
    opportunities: List[Dict]
    stats: Dict
    scan_time_ms: float


@router.post("/scan")
async def scan_arbitrage(req: HFTScanRequest):
    """扫描套利机会"""
    start = time.time()
    
    mole = await get_mole_v3()
    symbols = [s.replace("/USDT", "") for s in req.symbols]
    
    opportunities = await mole.scan_arbitrage(symbols)
    
    return HFTScanResponse(
        opportunities=[
            {
                "symbol": opp.symbol,
                "buy_exchange": opp.buy_exchange,
                "sell_exchange": opp.sell_exchange,
                "buy_price": opp.buy_price,
                "sell_price": opp.sell_price,
                "spread_pct": f"{opp.spread_pct:.2%}",
                "volume": f"${opp.volume:,.0f}",
                "confidence": f"{opp.confidence:.1%}",
            }
            for opp in opportunities
        ],
        stats=mole.get_stats(),
        scan_time_ms=round((time.time() - start) * 1000, 2)
    )


@router.get("/stats")
async def get_hft_stats():
    """获取高频统计"""
    mole = await get_mole_v3()
    return mole.get_stats()


@router.get("/config")
async def get_hft_config():
    """获取高频配置"""
    mole = await get_mole_v3()
    return {
        "api_timeout": mole.hft_config.api_timeout,
        "max_concurrent_requests": mole.hft_config.max_concurrent_requests,
        "connection_pool_size": mole.hft_config.connection_pool_size,
        "cache_ttl": mole.hft_config.cache_ttl,
        "min_spread": f"{mole.hft_config.min_spread:.2%}",
        "scan_interval": f"{mole.hft_config.scan_interval}s",
    }


class HFTConfigUpdate(BaseModel):
    api_timeout: Optional[float] = None
    max_concurrent_requests: Optional[int] = None
    min_spread: Optional[float] = None
    scan_interval: Optional[float] = None


@router.post("/config")
async def update_hft_config(config: HFTConfigUpdate):
    """更新高频配置"""
    mole = await get_mole_v3()
    
    if config.api_timeout is not None:
        mole.hft_config.api_timeout = config.api_timeout
    if config.max_concurrent_requests is not None:
        mole.hft_config.max_concurrent_requests = config.max_concurrent_requests
    if config.min_spread is not None:
        mole.hft_config.min_spread = config.min_spread
    if config.scan_interval is not None:
        mole.hft_config.scan_interval = config.scan_interval
    
    return {"status": "updated", "config": await get_hft_config()}


@router.post("/signal/{symbol}")
async def get_signal(symbol: str):
    """获取单个币种信号"""
    mole = await get_mole_v3()
    symbol = symbol.upper().replace("/USDT", "")
    
    # 模拟价格数据
    import random
    prices = [100 + random.uniform(-5, 5) for _ in range(30)]
    
    signal = await mole.generate_signal(symbol, prices)
    
    return {
        "symbol": symbol,
        **signal,
        "recommendation": "BUY" if signal["action"] == "buy" else "SELL" if signal["action"] == "sell" else "HOLD"
    }


@router.get("/opportunities/recent")
async def get_recent_opportunities(limit: int = 20):
    """获取最近的套利机会"""
    mole = await get_mole_v3()
    
    recent = list(mole.opportunities)[-limit:]
    
    return {
        "count": len(recent),
        "opportunities": [
            {
                "symbol": opp.symbol,
                "spread_pct": f"{opp.spread_pct:.2%}",
                "confidence": f"{opp.confidence:.1%}",
                "timestamp": time.strftime("%H:%M:%S", time.localtime(opp.timestamp)),
            }
            for opp in reversed(recent)
        ]
    }
