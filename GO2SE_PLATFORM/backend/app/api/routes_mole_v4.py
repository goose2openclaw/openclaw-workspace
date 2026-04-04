"""
🐹 打地鼠V4 双引擎 API
=======================
高频套利 + 跨市场套利 并行运转
2026-04-04
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import asyncio
import time

router = APIRouter(prefix="/api/mole/v4", tags=["打地鼠V4"])

# 全局V4实例
_mole_v4_instance = None

async def get_mole_v4():
    global _mole_v4_instance
    if _mole_v4_instance is None:
        from app.core.mole_v4_strategy import MoleV4Strategy
        _mole_v4_instance = MoleV4Strategy()
    return _mole_v4_instance


class V4ScanRequest(BaseModel):
    symbols: List[str] = ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "DOGE", "DOT"]


class V4ScanResponse(BaseModel):
    hft_opportunities: List[Dict]
    cross_opportunities: List[Dict]
    combined_signal: Dict
    scan_time_ms: float
    stats: Dict


@router.post("/scan")
async def scan_v4(req: V4ScanRequest):
    """
    并行扫描双引擎套利机会
    - HFT引擎: 秒级价格差异
    - 跨市场引擎: 跨交易所/三角套利
    """
    start = time.time()
    
    mole = await get_mole_v4()
    
    # 并行扫描
    scan_result = await mole.scan_parallel(req.symbols)
    
    # 生成组合信号
    combined_signal = await mole.generate_combined_signal(scan_result)
    
    scan_time_ms = (time.time() - start) * 1000
    
    return V4ScanResponse(
        hft_opportunities=[
            {
                "symbol": opp.symbol,
                "spread_pct": f"{opp.spread_pct:.3%}",
                "volume": f"${opp.volume:,.0f}",
                "confidence": f"{opp.confidence:.1%}",
            }
            for opp in scan_result.get("hft", [])[:5]
        ],
        cross_opportunities=[
            {
                "type": opp.type,
                "symbol": opp.symbol,
                "path": " → ".join(opp.path) if isinstance(opp.path, list) else opp.path,
                "spread_pct": f"{opp.spread_pct:.3%}",
                "confidence": f"{opp.confidence:.1%}",
            }
            for opp in scan_result.get("cross_exchange", [])[:3]
        ],
        combined_signal={
            "source": combined_signal.source,
            "action": combined_signal.action,
            "confidence": f"{combined_signal.confidence:.1%}",
            "spread_pct": f"{combined_signal.spread_pct:.3%}",
            "expected_profit": f"{combined_signal.expected_profit_pct:.3%}",
            "risk_level": combined_signal.risk_level,
        },
        scan_time_ms=round(scan_time_ms, 2),
        stats=mole.get_stats()
    )


@router.post("/execute")
async def execute_v4(req: V4ScanRequest):
    """
    执行双引擎交易
    自动分配权重: HFT 60%, 跨市场 40%
    """
    mole = await get_mole_v4()
    
    # 扫描机会
    scan_result = await mole.scan_parallel(req.symbols)
    
    # 执行交易
    results = await mole.execute_combined(scan_result)
    
    return {
        "status": "executed",
        "trades": results,
        "total_trades": len(results),
        "timestamp": time.time()
    }


@router.get("/stats")
async def get_v4_stats():
    """获取V4双引擎统计"""
    mole = await get_mole_v4()
    stats = mole.get_stats()
    
    return {
        "version": "v4.0-dual-engine",
        "engines": {
            "hft": {
                "weight": "60%",
                "opportunities": stats.get("hft_opportunities", 0),
                "trades": stats.get("hft_trades", 0),
                "stats": stats.get("hft_engine", {}),
            },
            "cross_market": {
                "weight": "40%",
                "opportunities": stats.get("cross_opportunities", 0),
                "trades": stats.get("cross_trades", 0),
                "stats": stats.get("cross_engine", {}),
            }
        },
        "combined": {
            "signals": stats.get("combined_signals", 0),
            "total_trades": stats.get("total_trades", 0),
        }
    }


@router.get("/config")
async def get_v4_config():
    """获取V4配置"""
    mole = await get_mole_v4()
    
    return {
        "version": "v4.0-dual-engine",
        "engines": {
            "hft": {
                "min_spread": f"{mole.v4_config.hft_min_spread:.2%}",
                "min_volume": f"${mole.v4_config.hft_min_volume:,.0f}",
                "max_position": f"{mole.v4_config.hft_max_position:.1%}",
                "weight": f"{mole.v4_config.hft_weight:.0%}",
            },
            "cross_market": {
                "min_spread": f"{mole.v4_config.cross_min_spread:.2%}",
                "min_volume": f"${mole.v4_config.cross_min_volume:,.0f}",
                "max_position": f"{mole.v4_config.cross_max_position:.1%}",
                "weight": f"{mole.v4_config.cross_weight:.0%}",
            }
        },
        "parallel_enabled": mole.v4_config.parallel_enabled,
    }


class V4ConfigUpdate(BaseModel):
    hft_min_spread: Optional[float] = None
    cross_min_spread: Optional[float] = None
    hft_weight: Optional[float] = None
    cross_weight: Optional[float] = None


@router.post("/config")
async def update_v4_config(config: V4ConfigUpdate):
    """更新V4配置"""
    mole = await get_mole_v4()
    
    if config.hft_min_spread is not None:
        mole.v4_config.hft_min_spread = config.hft_min_spread
    if config.cross_min_spread is not None:
        mole.v4_config.cross_min_spread = config.cross_min_spread
    if config.hft_weight is not None:
        mole.v4_config.hft_weight = config.hft_weight
        mole.v4_config.cross_weight = 1.0 - config.hft_weight
    if config.cross_weight is not None:
        mole.v4_config.cross_weight = config.cross_weight
        mole.v4_config.hft_weight = 1.0 - config.cross_weight
    
    return {"status": "updated", "config": await get_v4_config()}


@router.get("/signal")
async def get_combined_signal():
    """获取当前组合信号"""
    mole = await get_mole_v4()
    
    symbols = ["BTC", "ETH", "SOL", "BNB", "XRP"]
    scan_result = await mole.scan_parallel(symbols)
    combined = await mole.generate_combined_signal(scan_result)
    
    return {
        "signal": {
            "action": combined.action.upper(),
            "confidence": f"{combined.confidence:.1%}",
            "source": combined.source,
            "spread": f"{combined.spread_pct:.3%}",
            "expected_profit": f"{combined.expected_profit_pct:.3%}",
            "risk": combined.risk_level,
        },
        "recommendation": "BUY" if combined.action == "buy" else "SELL" if combined.action == "sell" else "HOLD",
        "details": combined.details,
    }
