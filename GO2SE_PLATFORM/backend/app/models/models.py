#!/usr/bin/env python3
"""
🪿 GO2SE 数据模型
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    """用户"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=True, index=True)
    hashed_api_key = Column(String(128), unique=True, index=True)
    api_key_prefix = Column(String(8), index=True)  # 前8位可显示
    tier = Column(String(20), default="guest")  # guest/subscriber/partner/private
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())


class Trade(Base):
    """交易记录"""
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(100), unique=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    side = Column(String(10), nullable=False)  # buy/sell
    amount = Column(Float, nullable=False)
    price = Column(Float)
    fee = Column(Float, default=0)
    status = Column(String(20), default="open")  # open/closed/cancelled
    pnl = Column(Float, default=0)
    strategy = Column(String(50))  # rabbit/mole/oracle/etc
    created_at = Column(DateTime, default=func.now())
    closed_at = Column(DateTime)


class Position(Base):
    """持仓"""
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    avg_price = Column(Float, nullable=False)
    current_price = Column(Float)
    unrealized_pnl = Column(Float, default=0)
    realized_pnl = Column(Float, default=0)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Signal(Base):
    """策略信号"""
    __tablename__ = "signals"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy = Column(String(50), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    signal = Column(String(10), nullable=False)  # buy/sell/hold
    confidence = Column(Float, nullable=False)  # 0-10
    price = Column(Float)
    reason = Column(Text)
    executed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())


class StrategyRun(Base):
    """策略执行记录"""
    __tablename__ = "strategy_runs"

    id = Column(Integer, primary_key=True, index=True)
    strategy = Column(String(50), nullable=False, index=True)
    symbol = Column(String(20), nullable=False)
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)
    signals_generated = Column(Integer, default=0)
    trades_executed = Column(Integer, default=0)
    result = Column(JSON)  # {"pnl": x, "win_rate": y, ...}
    status = Column(String(20), default="running")  # running/completed/failed


class MarketData(Base):
    """市场数据快照"""
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    price = Column(Float)
    bid = Column(Float)
    ask = Column(Float)
    volume_24h = Column(Float)
    change_24h = Column(Float)
    rsi = Column(Float)
    fetched_at = Column(DateTime, default=func.now())


class BacktestResult(Base):
    """回测结果"""
    __tablename__ = "backtest_results"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    symbol = Column(String(20), nullable=False)
    start_date = Column(String(20), nullable=False)
    end_date = Column(String(20), nullable=False)
    initial_capital = Column(Float, nullable=False)
    final_capital = Column(Float, nullable=False)
    total_return = Column(Float, nullable=False)
    total_trades = Column(Integer, default=0)
    win_rate = Column(Float, default=0)
    max_drawdown = Column(Float, default=0)
    sharpe_ratio = Column(Float, default=0)
    params = Column(JSON)  # 策略参数
    equity_curve = Column(JSON)  # 资金曲线
    trades_detail = Column(JSON)  # 交易明细
    created_at = Column(DateTime, default=func.now())
