#!/usr/bin/env python3
"""
🪿 GO2SE API路由
"""

import asyncio
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db

logger = logging.getLogger("go2se")
from app.core.config import settings
from app.core.trading_engine import engine
from app.models.models import Trade, Position, Signal, MarketData

router = APIRouter()


@router.get("/ping")
async def ping():
    """轻量级健康检查 (负载均衡器用)"""
    return {"pong": True, "ts": datetime.now().isoformat()}


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """健康检查 - 轻量级（不调用外部API）"""
    checks = {"database": "ok", "engine": "ok"}
    
    # 检查数据库
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        checks["database"] = f"error: {str(e)}"
    
    # 检查引擎状态（不调用外部API）
    try:
        if engine.exchange is None:
            checks["engine"] = "not_initialized"
        else:
            checks["engine"] = "ok"
    except Exception as e:
        checks["engine"] = f"error: {str(e)}"
    
    overall = "healthy" if all(v in ("ok", "not_initialized") for v in checks.values()) else "degraded"
    
    return {
        "status": overall,
        "checks": checks,
        "timestamp": datetime.now().isoformat(),
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "trading_mode": settings.TRADING_MODE
    }


@router.get("/market")
async def get_market_data():
    """获取市场数据 - 并发优化"""
    results = []
    errors = []
    
    async def fetch_one(symbol: str):
        try:
            tick = await engine.get_market_data(symbol)
            return {
                "symbol": tick.symbol,
                "price": tick.price,
                "change_24h": tick.change_24h,
                "volume_24h": tick.volume_24h,
                "rsi": tick.rsi,
                "bid": tick.bid,
                "ask": tick.ask
            }
        except Exception as e:
            logger.warning(f"获取 {symbol} 市场数据失败: {e}")
            return {"symbol": symbol, "error": str(e)}
    
    # 并发获取所有市场数据
    tasks = [fetch_one(s) for s in settings.TRADING_PAIRS[:10]]
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    for r in responses:
        if isinstance(r, Exception):
            errors.append({"error": str(r)})
        elif "error" in r:
            errors.append(r)
        else:
            results.append(r)
    
    return {
        "data": results,
        "errors": errors,
        "count": len(results),
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
        logger.warning(f"获取 {symbol} 数据失败: {e}")
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/signals")
async def get_signals(
    db: Session = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
    strategy: Optional[str] = None,
    signal: Optional[str] = None
):
    """获取信号列表 - 支持分页和过滤"""
    query = db.query(Signal)
    
    if strategy:
        query = query.filter(Signal.strategy == strategy)
    if signal:
        query = query.filter(Signal.signal == signal)
    
    total = query.count()
    signals = query.order_by(Signal.created_at.desc()).offset(offset).limit(limit).all()
    
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
        } for s in signals],
        "pagination": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total
        }
    }


@router.post("/signals/{strategy}/run")
async def run_strategy(strategy: str, db: Session = Depends(get_db)):
    """运行指定策略"""
    try:
        signals = await engine.run_strategy(strategy, settings.TRADING_PAIRS[:5])
        
        # 保存信号到数据库
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


@router.get("/portfolio")
async def get_portfolio(db: Session = Depends(get_db)):
    """获取组合数据 - 修复: 之前缺失此端点导致前端显示空白"""
    from app.models.models import Trade, Position
    
    # 计算总盈亏
    all_trades = db.query(Trade).all()
    total_pnl = sum(t.pnl or 0 for t in all_trades)
    total_trades = len(all_trades)
    winning_trades = len([t for t in all_trades if (t.pnl or 0) > 0])
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    # 获取当前持仓
    positions = db.query(Position).filter(Position.amount > 0).all()
    positions_data = [{
        "symbol": p.symbol,
        "amount": float(p.amount),
        "avg_price": float(p.avg_price) if p.avg_price else 0,
        "current_price": float(p.current_price) if p.current_price else 0,
        "pnl": float(p.pnl) if p.pnl else 0,
        "strategy": p.strategy or "unknown"
    } for p in positions]
    
    # 构建组合数据
    portfolio = {
        "total_pnl": round(total_pnl, 2),
        "total_trades": total_trades,
        "win_rate": round(win_rate, 1),
        "positions": positions_data,
        "performance": {
            "portfolio": {}
        }
    }
    
    # 按策略分组计算
    strategies_data = {}
    for t in all_trades:
        strat = t.strategy or "unknown"
        if strat not in strategies_data:
            strategies_data[strat] = {
                "name": f"策略-{strat}",
                "icon": "📊",
                "weight": getattr(settings, f"{strat.upper()}_WEIGHT", 0.1) * 100,
                "pnl": 0,
                "return_rate": 0,
                "trades": 0,
                "strategies": [strat],
                "desc": f"{strat} 策略表现"
            }
        strategies_data[strat]["pnl"] += t.pnl or 0
        strategies_data[strat]["trades"] += 1
    
    # 计算收益率
    for strat, data in strategies_data.items():
        data["return_rate"] = round((data["pnl"] / 1000) * 100, 2) if data["trades"] > 0 else 0
        data["pnl"] = round(data["pnl"], 2)
    
    portfolio["performance"]["portfolio"] = strategies_data
    
    return {"data": portfolio}
