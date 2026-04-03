#!/usr/bin/env python3
"""
🪿 打兔子 API
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.services.rabbit.strategy import RabbitStrategy, RabbitConfig, RabbitSignal as RSignal
from app.services.rabbit.models import RabbitSymbol, RabbitSignal, RabbitPosition, RabbitTrade, RabbitConfig as DBConfig

router = APIRouter(prefix="/rabbit", tags=["打兔子"])

# 策略实例
rabbit_strategy = RabbitStrategy()


class RabbitScanRequest(BaseModel):
    """扫描请求"""
    symbols: Optional[List[str]] = None


class RabbitSignalResponse(BaseModel):
    """信号响应"""
    symbol: str
    signal: str
    confidence: float
    price: float
    stop_loss: float
    take_profit: float
    position_size: float
    reason: str
    rsi: Optional[float] = None
    change_24h: Optional[float] = None


class RabbitConfigRequest(BaseModel):
    """配置请求"""
    max_position_pct: Optional[float] = None
    stop_loss_pct: Optional[float] = None
    take_profit_pct: Optional[float] = None
    strong_trend_threshold: Optional[float] = None


@router.get("/status")
async def get_status():
    """获取策略状态"""
    return rabbit_strategy.get_status()


@router.get("/symbols")
async def get_symbols(db: Session = Depends(get_db)):
    """获取监控的币种"""
    symbols = db.query(RabbitSymbol).filter(RabbitSymbol.is_active == True).all()
    return [
        {
            "symbol": s.symbol,
            "name": s.name,
            "rank": s.rank,
            "last_price": s.last_price,
            "scan_enabled": s.scan_enabled
        }
        for s in symbols
    ]


@router.post("/scan")
async def scan_market(
    request: RabbitScanRequest = None,
    db: Session = Depends(get_db)
):
    """扫描市场找机会"""
    
    # 模拟市场数据 - 实际应该从交易所API获取
    market_data = {}
    
    symbols = request.symbols if request and request.symbols else rabbit_strategy.config.symbols
    
    for symbol in symbols[:10]:  # 限制扫描数量
        # 模拟数据
        import random
        market_data[symbol] = {
            'price': random.uniform(100, 50000),
            'change_24h': random.uniform(-10, 10),
            'volume': random.uniform(1000000, 100000000),
            'avg_volume': random.uniform(1000000, 50000000),
            'rsi': random.uniform(20, 80),
            'macd': random.uniform(-100, 100),
            'signal_line': random.uniform(-100, 100),
            'ema_20': random.uniform(100, 50000),
            'ema_50': random.uniform(100, 50000),
        }
    
    # 执行扫描
    result = await rabbit_strategy.scan_market(market_data)
    
    return {"data": result}


@router.get("/signals")
async def get_signals(
    limit: int = Query(10, le=50),
    status: Optional[str] = None
):
    """获取信号列表"""
    # 返回模拟数据
    return [
        {"symbol": "BTCUSDT", "signal": "buy", "confidence": 7.5, "price": 75000, "stop_loss": 71250, "take_profit": 82500, "position_size": 0.1, "reason": "强趋势"},
        {"symbol": "ETHUSDT", "signal": "hold", "confidence": 5.2, "price": 3200, "stop_loss": 3040, "take_profit": 3520, "position_size": 0, "reason": "观望"},
    ]


@router.get("/positions")
async def get_positions():
    """获取当前持仓"""
    return []


@router.get("/trades")
async def get_trades(limit: int = Query(20, le=100)):
    """获取交易历史"""
    return []


@router.get("/config")
async def get_config():
    """获取策略配置"""
    return rabbit_strategy.config.__dict__


@router.post("/config")
async def update_config(config: RabbitConfigRequest):
    """更新策略配置"""
    if config.max_position_pct is not None:
        rabbit_strategy.config.max_position_pct = config.max_position_pct
    if config.stop_loss_pct is not None:
        rabbit_strategy.config.stop_loss_pct = config.stop_loss_pct
    if config.take_profit_pct is not None:
        rabbit_strategy.config.take_profit_pct = config.take_profit_pct
    if config.strong_trend_threshold is not None:
        rabbit_strategy.config.strong_trend_threshold = config.strong_trend_threshold
    
    return {"message": "配置已更新", "config": rabbit_strategy.config.__dict__}


@router.post("/toggle/{symbol}")
async def toggle_symbol(symbol: str, enabled: bool = True):
    """开关币种监控"""
    return {"message": f"{symbol} 已{'启用' if enabled else '禁用'}"}


@router.get("/symbols")
async def get_symbols():
    """获取监控的币种"""
    return {"symbols": rabbit_strategy.config.symbols}
