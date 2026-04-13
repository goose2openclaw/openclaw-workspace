#!/usr/bin/env python3
"""
📈 模拟交易板块 V2 - 加强版
=======================
支持做多/做空
实时盈亏
7大工具信号
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

router = APIRouter(prefix="/api/sim", tags=["模拟交易V2"])

# ─── Request Models ─────────────────────────────────

class OpenPositionRequest(BaseModel):
    symbol: str = "BTCUSDT"
    side: str = "LONG"          # LONG / SHORT
    quantity: float = Field(..., gt=0)
    leverage: int = Field(default=1, ge=1, le=10)
    stop_loss_pct: Optional[float] = Field(default=0.05, description="止损百分比")
    take_profit_pct: Optional[float] = Field(default=0.15, description="止盈百分比")
    tool: str = "manual"

class ClosePositionRequest(BaseModel):
    symbol: str

class SetBalanceRequest(BaseModel):
    balance: float = Field(..., gt=0)

# ─── Routes ─────────────────────────────────────────

@router.get("/markets")
async def get_markets():
    """获取所有模拟市场行情"""
    from app.core.sim_engine import get_sim_engine
    engine = get_sim_engine()
    return {
        "success": True,
        "markets": engine.market.get_all_tickers(),
        "timestamp": datetime.now().isoformat()
    }


@router.get("/market/{symbol}")
async def get_market(symbol: str):
    """获取单个市场行情"""
    from app.core.sim_engine import get_sim_engine
    engine = get_sim_engine()
    ticker = engine.market.get_ticker(symbol)
    return {"success": True, "data": ticker}


@router.get("/portfolio")
async def get_portfolio():
    """获取模拟投资组合"""
    from app.core.sim_engine import get_sim_engine
    engine = get_sim_engine()
    # 先检查止损止盈
    closed = engine.check_positions()
    return {
        "success": True,
        "data": engine.get_portfolio(),
        "auto_closed": [
            {"symbol": c.symbol, "order_id": c.order_id, "price": c.price}
            for c in closed
        ] if closed else []
    }


@router.get("/stats")
async def get_stats():
    """获取交易统计"""
    from app.core.sim_engine import get_sim_engine
    engine = get_sim_engine()
    return {"success": True, "data": engine.get_stats()}


@router.post("/open")
async def open_position(req: OpenPositionRequest):
    """开仓（做多或做空）"""
    from app.core.sim_engine import get_sim_engine
    engine = get_sim_engine()

    try:
        # 计算止损止盈价格
        ticker = engine.market.get_ticker(req.symbol)
        price = ticker["price"]
        if req.side == "LONG":
            stop_loss = price * (1 - req.stop_loss_pct) if req.stop_loss_pct else 0
            take_profit = price * (1 + req.take_profit_pct) if req.take_profit_pct else 0
        else:  # SHORT
            stop_loss = price * (1 + req.stop_loss_pct) if req.stop_loss_pct else 0
            take_profit = price * (1 - req.take_profit_pct) if req.take_profit_pct else 0

        order = engine.open_position(
            symbol=req.symbol,
            side=req.side,
            quantity=req.quantity,
            leverage=req.leverage,
            stop_loss=stop_loss,
            take_profit=take_profit,
            tool=req.tool,
        )

        return {
            "success": True,
            "action": "OPEN",
            "direction": req.side,
            "symbol": req.symbol,
            "order_id": order.order_id,
            "price": order.price,
            "quantity": req.quantity,
            "leverage": req.leverage,
            "stop_loss": round(stop_loss, 4) if stop_loss else None,
            "take_profit": round(take_profit, 4) if take_profit else None,
            "fee": round(order.fee, 2),
            "balance": engine.balance,
            "timestamp": order.timestamp,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/close")
async def close_position(req: ClosePositionRequest):
    """平仓"""
    from app.core.sim_engine import get_sim_engine
    engine = get_sim_engine()

    try:
        order = engine.close_position(req.symbol)
        return {
            "success": True,
            "action": "CLOSE",
            "symbol": req.symbol,
            "order_id": order.order_id,
            "price": order.price,
            "quantity": order.quantity,
            "fee": round(order.fee, 2),
            "balance": engine.balance,
            "timestamp": order.timestamp,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/positions")
async def get_positions():
    """获取所有持仓"""
    from app.core.sim_engine import get_sim_engine
    engine = get_sim_engine()
    # 先触发止损止盈检查
    engine.check_positions()
    return {"success": True, "positions": engine.get_portfolio()["positions"]}


@router.post("/positions/close-all")
async def close_all_positions():
    """一键平所有持仓"""
    from app.core.sim_engine import get_sim_engine
    engine = get_sim_engine()
    closed = []
    for symbol in list(engine.positions.keys()):
        try:
            order = engine.close_position(symbol)
            closed.append({
                "symbol": symbol,
                "order_id": order.order_id,
                "price": order.price
            })
        except Exception:
            pass
    return {
        "success": True,
        "closed": closed,
        "balance": engine.balance
    }


@router.get("/trades")
async def get_trades(limit: int = Query(default=50, le=100)):
    """获取交易历史"""
    from app.core.sim_engine import get_sim_engine
    engine = get_sim_engine()
    return {"success": True, "trades": engine.get_trades(limit)}


@router.get("/orders")
async def get_orders(limit: int = Query(default=20, le=50)):
    """获取订单历史"""
    from app.core.sim_engine import get_sim_engine
    engine = get_sim_engine()
    return {"success": True, "orders": engine.get_orders(limit)}


@router.post("/reset")
async def reset_account(balance: Optional[float] = 100000):
    """重置账户"""
    from app.core.sim_engine import SimTradingEngine
    global _sim_engine
    _sim_engine = SimTradingEngine(initial_balance=balance)
    return {
        "success": True,
        "message": f"账户已重置，模拟资金: {balance}",
        "balance": balance
    }


@router.post("/balance")
async def set_balance(req: SetBalanceRequest):
    """设置模拟资金"""
    from app.core.sim_engine import get_sim_engine
    engine = get_sim_engine()
    engine.balance = req.balance
    engine.initial_balance = req.balance
    return {
        "success": True,
        "balance": req.balance
    }


# ─── 7工具快捷下单 ────────────────────────────────

@router.post("/tool/{tool_name}")
async def tool_trade(
    tool_name: str,
    symbol: str = "BTCUSDT",
    quantity: float = 0.01
):
    """7大工具快捷下单"""
    from app.core.sim_engine import get_sim_engine
    engine = get_sim_engine()

    # 7工具默认参数
    TOOL_PARAMS = {
        "rabbit": {
            "side": "LONG", "leverage": 3, "stop_loss_pct": 0.05, "take_profit_pct": 0.08
        },
        "mole": {
            "side": "SHORT", "leverage": 5, "stop_loss_pct": 0.03, "take_profit_pct": 0.12
        },
        "oracle": {
            "side": "LONG", "leverage": 3, "stop_loss_pct": 0.05, "take_profit_pct": 0.10
        },
        "leader": {
            "side": "LONG", "leverage": 3, "stop_loss_pct": 0.03, "take_profit_pct": 0.08
        },
        "hitchhiker": {
            "side": "LONG", "leverage": 2, "stop_loss_pct": 0.05, "take_profit_pct": 0.08
        },
        "airdrop": {
            "side": "LONG", "leverage": 1, "stop_loss_pct": 0.02, "take_profit_pct": 0.20
        },
        "crowdsource": {
            "side": "LONG", "leverage": 1, "stop_loss_pct": 0.01, "take_profit_pct": 0.30
        },
    }

    if tool_name not in TOOL_PARAMS:
        raise HTTPException(status_code=400, detail=f"未知工具: {tool_name}")

    params = TOOL_PARAMS[tool_name]

    try:
        ticker = engine.market.get_ticker(symbol)
        price = ticker["price"]
        if params["side"] == "LONG":
            stop_loss = price * (1 - params["stop_loss_pct"])
            take_profit = price * (1 + params["take_profit_pct"])
        else:
            stop_loss = price * (1 + params["stop_loss_pct"])
            take_profit = price * (1 - params["take_profit_pct"])

        order = engine.open_position(
            symbol=symbol,
            side=params["side"],
            quantity=quantity,
            leverage=params["leverage"],
            stop_loss=stop_loss,
            take_profit=take_profit,
            tool=tool_name,
        )

        return {
            "success": True,
            "tool": tool_name,
            "action": "OPEN",
            **params,
            "symbol": symbol,
            "order_id": order.order_id,
            "price": order.price,
            "quantity": quantity,
            "stop_loss": round(stop_loss, 4),
            "take_profit": round(take_profit, 4),
            "balance": round(engine.balance, 2),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
