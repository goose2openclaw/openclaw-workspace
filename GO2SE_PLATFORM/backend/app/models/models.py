#!/usr/bin/env python3
"""
🪿 GO2SE 数据模型
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.core.database import Base


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
    status = Column(String(20), nullable=False)  # running/success/error
    duration_ms = Column(Integer)
    signals_count = Column(Integer)
    errors = Column(Text)
    created_at = Column(DateTime, default=func.now())


class MarketData(Base):
    """市场数据快照"""
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    price = Column(Float, nullable=False)
    change_24h = Column(Float)
    volume_24h = Column(Float)
    high_24h = Column(Float)
    low_24h = Column(Float)
    rsi = Column(Float)
    data = Column(JSON)  # 完整数据
    created_at = Column(DateTime, default=func.now(), index=True)


class Config(Base):
    """系统配置"""
    __tablename__ = "config"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
