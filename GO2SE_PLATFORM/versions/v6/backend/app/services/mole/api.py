#!/usr/bin/env python3
"""
🪿 打地鼠 API
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.core.database import get_db

router = APIRouter(prefix="/mole", tags=["打地鼠"])

# 策略实例
from app.services.mole.strategy import MoleStrategy, MoleSignal
mole_strategy = MoleStrategy()


class MoleConfigRequest(BaseModel):
    max_position_pct: Optional[float] = None
    stop_loss_pct: Optional[float] = None
    take_profit_pct: Optional[float] = None
    rebound_threshold: Optional[float] = None


@router.get("/status")
async def get_status():
    """获取策略状态"""
    return mole_strategy.get_status()


@router.get("/active-holes")
async def get_active_holes():
    """获取活跃鼠洞"""
    return {
        "active_holes": mole_strategy.get_active_holes_summary(),
        "count": len(mole_strategy.active_holes)
    }


@router.post("/scan")
async def scan_market(db: Session = Depends(get_db)):
    """扫描市场找机会"""
    
    import random
    
    # 模拟市场数据 - 市值20名后
    market_data = {}
    test_symbols = [
        "DOGEUSDT", "SHIBUSDT", "PEPEUSDT", "WIFUSDT", "BONKUSDT",
        "APTUSDT", "OPUSDT", "ARBUSDT", "INJUSDT", "SUIUSDT"
    ]
    
    for symbol in test_symbols:
        market_data[symbol] = {
            'price': random.uniform(0.001, 100),
            'change_24h': random.uniform(-30, 10),
            'volume': random.uniform(50000, 50000000),
            'avg_volume': random.uniform(50000, 20000000),
            'rsi': random.uniform(20, 80),
        }
    
    result = await mole_strategy.scan_market(market_data)
    
    return {
        "scanned_count": result.scanned_count,
        "whacked_count": result.whacked_count,
        "active_holes": result.active_holes,
        "opportunities": [
            {
                "symbol": o.symbol,
                "signal": o.signal.value,
                "confidence": round(o.confidence, 2),
                "price": round(o.entry_price, 6),
                "reason": o.reason
            }
            for o in result.opportunities
        ],
        "timestamp": result.timestamp.isoformat()
    }


@router.get("/positions")
async def get_positions(db: Session = Depends(get_db)):
    """获取当前持仓"""
    return [
        {
            "symbol": s,
            "info": info
        }
        for s, info in mole_strategy.positions.items()
    ]


@router.get("/watch-list")
async def get_watch_list():
    """获取观察列表"""
    return {"watch_list": mole_strategy.watch_list}


@router.post("/add-watch")
async def add_to_watch(symbol: str):
    """添加到观察列表"""
    if symbol not in mole_strategy.watch_list:
        mole_strategy.watch_list.append(symbol)
    return {"message": f"{symbol} 已添加到观察列表"}


@router.post("/remove-hole/{symbol}")
async def remove_hole(symbol: str):
    """移除鼠洞"""
    if symbol in mole_strategy.active_holes:
        del mole_strategy.active_holes[symbol]
        return {"message": f"{symbol} 鼠洞已移除"}
    return {"message": f"{symbol} 无活跃鼠洞"}
