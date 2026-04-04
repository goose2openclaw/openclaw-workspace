#!/usr/bin/env python3
"""
🪿 GO2SE API路由
"""

import asyncio
import json
import logging
import time
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.core.websocket_manager import manager
from app.core.auth import get_current_user, get_current_user_optional, generate_api_key, hash_key
from app.core.backtest_engine import BacktestEngine, BacktestConfig
from functools import lru_cache

logger = logging.getLogger("go2se")
from app.core.config import settings
from app.core.trading_engine import engine
from app.models.models import Trade, Position, Signal, MarketData, User, BacktestResult

router = APIRouter()

# 简单内存缓存 (key: (endpoint, hash), value: (data, expire_ts))
_cache: dict = {}
_CACHE_TTL_STATS = 8   # /stats 缓存8秒

# 优化器路由
try:
    from app.api.routes_optimizer import router as optimizer_router
    router.include_router(optimizer_router)
    logger.info("✅ 优化器路由已注册")
except Exception as e:
    logger.warning(f"⚠️ 优化器路由注册失败: {e}")

# Mapping路由
try:
    from app.api.routes_mapping import router as mapping_router
    router.include_router(mapping_router)
    logger.info("✅ Mapping路由已注册")
except Exception as e:
    logger.warning(f"⚠️ Mapping路由注册失败: {e}")
_CACHE_TTL_PORTFOLIO = 10  # /portfolio 缓存10秒
_CACHE_TTL_MARKET = 15   # /market 新鲜缓存15秒
_CACHE_MAX_AGE_MARKET = 60  # /market 允许返回过期数据60秒 (stale-while-revalidate)

# Redis缓存层
try:
    from app.core.cache import cache_get, cache_set, cache_delete, cache_stats, namespaced_cache
    _use_redis = True
except ImportError:
    _use_redis = False

# 命名空间缓存实例
_market_cache = namespaced_cache("market", ttl=15) if _use_redis else None
_stats_cache = namespaced_cache("stats", ttl=8) if _use_redis else None

def _cache_get(key: str) -> Optional[dict]:
    """取缓存，未过期返回数据，否则返回None"""
    item = _cache.get(key)
    if item is None:
        return None
    data, expire_ts = item
    if time.time() > expire_ts:
        del _cache[key]
        return None
    return data

def _cache_set(key: str, data: dict, ttl: int):
    """设缓存"""
    _cache[key] = (data, time.time() + ttl)


@router.get("/cache/stats")
async def get_cache_stats():
    """获取缓存统计信息"""
    if not _use_redis:
        return {"error": "Redis缓存未启用"}
    
    try:
        stats = cache_stats()
        return {"data": stats}
    except Exception as e:
        return {"error": str(e)}


@router.post("/cache/clear")
async def clear_cache():
    """清空所有缓存 (谨慎使用)"""
    if not _use_redis:
        return {"error": "Redis缓存未启用"}
    
    try:
        count = cache_clear()
        return {"message": f"已清空 {count} 个缓存键"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ping")
async def ping():
    """轻量级健康检查 (负载均衡器用)"""
    from fastapi import Response
    return Response(
        content='{"pong":true,"ts":"' + datetime.now().isoformat() + '"}',
        media_type="application/json",
        headers={"Cache-Control": "no-cache, no-store, must-revalidate", "X-Content-Type-Options": "nosniff"}
    )


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """健康检查 - 轻量级（不调用外部API）"""
    checks = {"database": "ok", "engine": "ok", "cache": "ok"}
    
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
    
    # 检查缓存
    if _use_redis:
        try:
            cache_stats_data = cache_stats()
            checks["cache"] = f"redis:{cache_stats_data.get('backend','unknown')}"
        except Exception as e:
            checks["cache"] = f"warn:{str(e)[:20]}"
    
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
    """
    获取市场数据 - Stale-While-Revalidate缓存策略
    支持Redis缓存层 (高性能)
    
    缓存层级:
    1. 新鲜缓存(<15s): 直接返回
    2. 过期但可用缓存(15-60s): 立即返回 + 后台刷新
    3. 无缓存或超期(>60s): 等待Binance API
    """
    # 优先使用Redis缓存
    if _use_redis and _market_cache:
        cached_data = _market_cache.get("/market")
        if cached_data is not None:
            return {"data": cached_data["data"], "cached": True, "age_seconds": 0}
    
    cached_raw = _cache.get("/market")
    now = time.time()
    
    async def fetch_all():
        """从Binance获取所有市场数据"""
        results, errors = [], []
        
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
    
    # Case 1: 新鲜缓存 → 直接返回
    if cached_raw is not None:
        cached_data, expire_ts = cached_raw
        age = now - (expire_ts - _CACHE_TTL_MARKET)  # 数据年龄
        
        if age < _CACHE_TTL_MARKET:
            return {"data": cached_data["data"], "cached": True, "age_seconds": round(age, 1)}
        
        # Case 2: 过期但可用(15-60s) → 立即返回 + 后台刷新
        if age < _CACHE_MAX_AGE_MARKET:
            logger.info(f"📦 /market stale返回 (age={age:.0f}s), 后台刷新...")
            # 触发后台刷新(不等待)
            asyncio.create_task(_do_market_refresh())
            return {"data": cached_data["data"], "cached": True, "stale": True, "age_seconds": round(age, 1)}
    
    # Case 3: 无缓存或超期(>60s) → 等待API
    payload = await fetch_all()
    _cache_set("/market", payload, _CACHE_TTL_MARKET)
    return {"data": payload["data"], "cached": False, "count": payload["count"]}


async def _do_market_refresh():
    """后台刷新市场数据(不阻塞响应)"""
    try:
        results, errors = [], []
        
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
                return {"symbol": symbol, "error": str(e)}
        
        tasks = [fetch_one(s) for s in settings.TRADING_PAIRS[:10]]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        for r in responses:
            if isinstance(r, Exception):
                errors.append({"error": str(r)})
            elif "error" in r:
                errors.append(r)
            else:
                results.append(r)
        
        payload = {
            "data": results,
            "errors": errors,
            "count": len(results),
            "timestamp": datetime.now().isoformat()
        }
        _cache_set("/market", payload, _CACHE_TTL_MARKET)
        logger.info(f"✅ /market 后台刷新完成 ({len(results)}个交易对)")
    except Exception as e:
        logger.error(f"❌ /market 后台刷新失败: {e}")


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
            },
            "airdrop": {
                "name": "💰 薅羊毛",
                "description": "新币空投套利",
                "weight": 0.03,
                "status": "active"
            },
            "crowdsource": {
                "name": "👶 穷孩子",
                "description": "众包任务套利",
                "weight": 0.02,
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
    """获取统计信息 (8秒Redis/内存缓存)"""
    # 优先使用Redis缓存
    if _use_redis and _stats_cache:
        cached = _stats_cache.get("/stats")
        if cached is not None:
            return {"data": cached, "cached": True}
    
    cached = _cache_get("/stats")
    if cached is not None:
        return {"data": cached, "cached": True, "age_seconds": time.time() - (_cache.get("/stats")[1] - _CACHE_TTL_STATS)}
    
    total_trades = db.query(Trade).count()
    open_trades = db.query(Trade).filter(Trade.status == "open").count()
    total_signals = db.query(Signal).count()
    executed_signals = db.query(Signal).filter(Signal.executed == True).count()
    
    data = {
        "total_trades": total_trades,
        "open_trades": open_trades,
        "total_signals": total_signals,
        "executed_signals": executed_signals,
        "trading_mode": settings.TRADING_MODE,
        "max_position": settings.MAX_POSITION,
        "stop_loss": settings.STOP_LOSS,
        "take_profit": settings.TAKE_PROFIT,
        "version": settings.APP_VERSION,
        "strategy_mode": "ai_dynamic" if hasattr(settings, 'AI_DYNAMIC_ALLOCATION') and settings.AI_DYNAMIC_ALLOCATION else "manual",
    }
    _cache_set("/stats", data, _CACHE_TTL_STATS)
    
    # 同时写入Redis
    if _use_redis and _stats_cache:
        _stats_cache.set("/stats", data)
    
    return {"data": data, "cached": False}


@router.get("/portfolio")
async def get_portfolio(db: Session = Depends(get_db)):
    """获取组合数据 (10秒内存缓存)"""
    cached = _cache_get("/portfolio")
    if cached is not None:
        return {"data": cached, "cached": True}
    
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
    _cache_set("/portfolio", portfolio, _CACHE_TTL_PORTFOLIO)
    return {"data": portfolio, "cached": False}


# ── 认证端点 (公开) ───────────────────────────────────────────────

@router.post("/auth/register")
async def register(username: str = Query(...), db: Session = Depends(get_db)):
    """注册用户并生成API密钥"""
    # 检查是否已存在
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    api_key, prefix, hashed = generate_api_key()
    user = User(
        username=username,
        api_key_prefix=prefix,
        hashed_api_key=hashed,
        tier="guest"
    )
    db.add(user)
    db.commit()
    
    return {
        "username": username,
        "api_key": api_key,  # 仅在此返回，服务器不存储明文
        "api_key_prefix": prefix,
        "tier": user.tier,
        "msg": "请妥善保存API密钥，仅显示一次"
    }


@router.post("/auth/login")
async def login(username: str = Query(...), db: Session = Depends(get_db)):
    """通过用户名登录，返回已有API密钥前缀"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {
        "username": user.username,
        "api_key_prefix": user.api_key_prefix,
        "tier": user.tier,
        "msg": "使用完整的API密钥访问受保护端点"
    }


# ── 用户信息 (需认证) ─────────────────────────────────────────────

@router.get("/auth/me")
async def get_me(user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return {
        "username": user.username,
        "tier": user.tier,
        "api_key_prefix": user.api_key_prefix,
        "created_at": user.created_at.isoformat()
    }


# ── 回测端点 (需认证) ─────────────────────────────────────────────

@router.post("/backtest")
async def run_backtest(
    symbol: str = Query("BTC/USDT"),
    start_date: str = Query("2025-01-01"),
    end_date: str = Query("2025-12-31"),
    initial_capital: float = Query(10000.0),
    stop_loss: float = Query(0.05),
    take_profit: float = Query(0.15),
    position_size: float = Query(0.1),
    strategy: str = Query("rsi_macross"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """运行回测 (需API认证)"""
    config = BacktestConfig(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        initial_capital=initial_capital,
        stop_loss=stop_loss,
        take_profit=take_profit,
        position_size=position_size,
        strategy=strategy
    )
    
    be = BacktestEngine(exchange=engine.exchange)
    result = await be.run(config)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    # 保存结果
    bt = BacktestResult(
        name=f"{symbol}_{strategy}_{start_date}_{end_date}",
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        initial_capital=initial_capital,
        final_capital=result["final_capital"],
        total_return=result["total_return"],
        total_trades=result["total_trades"],
        win_rate=result["win_rate"],
        max_drawdown=result["max_drawdown"],
        sharpe_ratio=result["sharpe_ratio"],
        params={"strategy": strategy, "stop_loss": stop_loss, "take_profit": take_profit},
        equity_curve=result.get("equity_curve", []),
        trades_detail=result.get("trades", [])
    )
    db.add(bt)
    db.commit()
    
    return {"data": result}


@router.get("/backtest/history")
async def get_backtest_history(
    limit: int = Query(20),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取回测历史"""
    results = db.query(BacktestResult).order_by(BacktestResult.created_at.desc()).limit(limit).all()
    return {
        "data": [{
            "id": r.id,
            "name": r.name,
            "symbol": r.symbol,
            "start_date": r.start_date,
            "end_date": r.end_date,
            "initial_capital": r.initial_capital,
            "final_capital": r.final_capital,
            "total_return": r.total_return,
            "total_trades": r.total_trades,
            "win_rate": r.win_rate,
            "max_drawdown": r.max_drawdown,
            "sharpe_ratio": r.sharpe_ratio,
            "params": r.params,
            "created_at": r.created_at.isoformat()
        } for r in results]
    }


# ── WebSocket 端点 ──────────────────────────────────────────────────
from fastapi import WebSocket

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 实时推送 - 客户端连接后接收实时行情/信号/持仓更新"""
    await manager.connect(websocket)
    try:
        # 发送欢迎消息
        await websocket.send_json({
            "type": "connected",
            "msg": "🪿 GO2SE WebSocket已连接",
            "ts": datetime.now().isoformat()
        })
        # 保持连接，监听客户端消息
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                # 客户端可以发送 {"action": "ping"} 维持心跳
                if msg.get("action") == "ping":
                    await websocket.send_json({"type": "pong", "ts": datetime.now().isoformat()})
                elif msg.get("action") == "subscribe":
                    # 客户端订阅特定主题 (future)
                    await websocket.send_json({"type": "subscribed", "topic": msg.get("topic")})
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "msg": "Invalid JSON"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)
