#!/usr/bin/env python3
"""
🪿 GO2SE 模拟交易 API 路由
"""

from fastapi import APIRouter
from app.core.mock_data import (
    get_mock_market_data,
    get_mock_signals,
    get_mock_portfolio,
    get_mock_wallet,
    get_mock_trading_history
)

router = APIRouter(prefix="/api/sim", tags=["模拟交易"])


@router.get("/markets")
async def sim_markets(symbol: str = None):
    """获取模拟市场数据"""
    return get_mock_market_data(symbol)


@router.get("/signals")
async def sim_signals():
    """获取模拟交易信号"""
    return get_mock_signals()


@router.get("/portfolio")
async def sim_portfolio():
    """获取模拟持仓"""
    return get_mock_portfolio()


@router.get("/wallet")
async def sim_wallet():
    """获取模拟钱包"""
    return get_mock_wallet()


@router.get("/history")
async def sim_history(count: int = 20):
    """获取模拟交易历史"""
    return get_mock_trading_history(count)


@router.post("/trade")
async def sim_execute_trade(symbol: str, side: str, quantity: float):
    """模拟执行交易"""
    from datetime import datetime
    
    price = 75000  # 简化处理
    
    return {
        "status": "simulated",
        "order": {
            "id": f"SIM_{datetime.now().timestamp()}",
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": price,
            "total": quantity * price,
            "fee": quantity * price * 0.001,
            "status": "filled",
            "timestamp": datetime.now().isoformat()
        },
        "message": f"✅ 模拟交易成功: {side.upper()} {quantity} {symbol}"
    }
