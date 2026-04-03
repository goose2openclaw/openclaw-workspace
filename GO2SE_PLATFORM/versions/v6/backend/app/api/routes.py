#!/usr/bin/env python3
"""
🪿 GO2SE API路由
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.core.config import settings
from app.core.trading_engine import engine
from app.models.models import Trade, Position, Signal, MarketData

router = APIRouter()


@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "trading_mode": settings.TRADING_MODE
    }


@router.get("/market")
async def get_market_data():
    """获取市场数据"""
    results = []
    
    for symbol in settings.TRADING_PAIRS[:10]:
        try:
            tick = await engine.get_market_data(symbol)
            results.append({
                "symbol": tick.symbol,
                "price": tick.price,
                "change_24h": tick.change_24h,
                "volume_24h": tick.volume_24h,
                "rsi": tick.rsi,
                "bid": tick.bid,
                "ask": tick.ask
            })
        except Exception as e:
            pass
    
    return {
        "data": results,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/market/{symbol}")
async def get_symbol_data(symbol: str):
    """获取单个交易对数据"""
    try:
        tick = await engine.get_market_data(f"{symbol}/USDT")
        return {
            "data": {
                "symbol": tick.symbol,
                "price": tick.price,
                "change_24h": tick.change_24h,
                "volume_24h": tick.volume_24h,
                "high_24h": tick.high_24h,
                "low_24h": tick.low_24h,
                "rsi": tick.rsi,
                "bid": tick.bid,
                "ask": tick.ask
            }
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/signals")
async def get_signals(db: Session = Depends(get_db), limit: int = 50):
    """获取信号列表"""
    signals = db.query(Signal).order_by(Signal.created_at.desc()).limit(limit).all()
    return {
        "data": [{
            "id": s.id,
            "strategy": s.strategy,
            "symbol": s.symbol,
            "signal": s.signal,
            "confidence": s.confidence,
            "reason": s.reason,
            "executed": s.executed,
            "created_at": s.created_at.isoformat()
        } for s in signals]
    }


@router.post("/signals/{strategy}/run")
async def run_strategy(strategy: str):
    """运行指定策略"""
    try:
        signals = await engine.run_strategy(strategy, settings.TRADING_PAIRS[:5])
        
        # 保存信号到数据库
        db = next(get_db())
        for sig in signals:
            db_signal = Signal(
                strategy=strategy,
                symbol=sig["symbol"],
                signal=sig["signal"],
                confidence=sig["confidence"],
                price=sig["price"],
                reason=sig.get("reason", "")
            )
            db.add(db_signal)
        db.commit()
        
        return {
            "status": "success",
            "strategy": strategy,
            "signals_count": len(signals),
            "signals": signals
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/strategies")
async def get_strategies_status():
    """获取所有策略状态"""
    return {
        "data": {
            "rabbit": {
                "name": "🐰 打兔子",
                "description": "Top20趋势追踪",
                "weight": settings.RABBIT_WEIGHT,
                "interval": settings.STRATEGY_INTERVAL_RABBIT,
                "status": "active"
            },
            "mole": {
                "name": "🐹 打地鼠",
                "description": "高波动套利",
                "weight": settings.MOLE_WEIGHT,
                "interval": settings.STRATEGY_INTERVAL_MOLE,
                "status": "active"
            },
            "oracle": {
                "name": "🔮 走着瞧",
                "description": "预测市场",
                "weight": settings.ORACLE_WEIGHT,
                "interval": settings.STRATEGY_INTERVAL_ORACLE,
                "status": "active"
            },
            "leader": {
                "name": "👑 跟大哥",
                "description": "做市协作",
                "weight": settings.LEADER_WEIGHT,
                "interval": settings.STRATEGY_INTERVAL_LEADER,
                "status": "active"
            },
            "hitchhiker": {
                "name": "🍀 搭便车",
                "description": "跟单分成",
                "weight": settings.HITCHHIKER_WEIGHT,
                "status": "active"
            }
        }
    }


@router.get("/trades")
async def get_trades(db: Session = Depends(get_db), limit: int = 50):
    """获取交易记录"""
    trades = db.query(Trade).order_by(Trade.created_at.desc()).limit(limit).all()
    return {
        "data": [{
            "id": t.id,
            "symbol": t.symbol,
            "side": t.side,
            "amount": t.amount,
            "price": t.price,
            "status": t.status,
            "pnl": t.pnl,
            "strategy": t.strategy,
            "created_at": t.created_at.isoformat()
        } for t in trades]
    }


@router.get("/positions")
async def get_positions(db: Session = Depends(get_db)):
    """获取当前持仓"""
    positions = db.query(Position).filter(Position.amount > 0).all()
    return {
        "data": [{
            "id": p.id,
            "symbol": p.symbol,
            "amount": p.amount,
            "avg_price": p.avg_price,
            "current_price": p.current_price,
            "unrealized_pnl": p.unrealized_pnl,
            "updated_at": p.updated_at.isoformat()
        } for p in positions]
    }


@router.post("/trade")
async def execute_trade(signal: dict):
    """执行交易"""
    result = await engine.execute_trade(signal)
    return result


@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """获取统计信息"""
    total_trades = db.query(Trade).count()
    open_trades = db.query(Trade).filter(Trade.status == "open").count()
    total_signals = db.query(Signal).count()
    executed_signals = db.query(Signal).filter(Signal.executed == True).count()
    
    return {
        "data": {
            "total_trades": total_trades,
            "open_trades": open_trades,
            "total_signals": total_signals,
            "executed_signals": executed_signals,
            "trading_mode": settings.TRADING_MODE,
            "max_position": settings.MAX_POSITION,
            "stop_loss": settings.STOP_LOSS,
            "take_profit": settings.TAKE_PROFIT
        }
    }
