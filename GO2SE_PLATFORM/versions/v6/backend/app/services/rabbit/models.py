#!/usr/bin/env python3
"""
🪿 打兔子数据库模型
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, Text
from sqlalchemy.sql import func
from app.core.database import Base


class RabbitSymbol(Base):
    """打兔子监控币种"""
    __tablename__ = "rabbit_symbols"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, nullable=False, index=True)
    
    # 币种信息
    name = Column(String(50))
    rank = Column(Integer)           # 市值排名
    market_cap = Column(Float)      # 市值
    volume_24h = Column(Float)      # 24h成交量
    
    # 监控状态
    is_active = Column(Boolean, default=True)
    last_price = Column(Float)
    last_update = Column(DateTime)
    
    # 配置
    scan_enabled = Column(Boolean, default=True)
    min_trade_amount = Column(Float, default=100)
    position_limit = Column(Float, default=0.20)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class RabbitSignal(Base):
    """打兔子信号记录"""
    __tablename__ = "rabbit_signals"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    
    # 信号类型
    signal_type = Column(String(20), nullable=False)  # strong_buy/buy/sell/strong_sell
    
    # 价格信息
    price = Column(Float, nullable=False)
    stop_loss = Column(Float)
    take_profit = Column(Float)
    
    # 评分
    confidence = Column(Float, nullable=False)  # 0-10
    trend_score = Column(Float)
    momentum_score = Column(Float)
    volume_score = Column(Float)
    
    # 指标
    rsi = Column(Float)
    change_24h = Column(Float)
    volume_ratio = Column(Float)
    
    # 原因
    reason = Column(Text)
    
    # 状态
    status = Column(String(20), default="pending")  # pending/executed/expired
    
    # 时间
    created_at = Column(DateTime, default=func.now(), index=True)
    executed_at = Column(DateTime)
    expired_at = Column(DateTime)


class RabbitPosition(Base):
    """打兔子持仓"""
    __tablename__ = "rabbit_positions"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    
    # 持仓信息
    amount = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    current_price = Column(Float)
    
    # 止损止盈
    stop_loss = Column(Float)
    take_profit = Column(Float)
    
    # PnL
    unrealized_pnl = Column(Float, default=0)
    realized_pnl = Column(Float, default=0)
    
    # 状态
    status = Column(String(20), default="open")  # open/closed
    
    # 时间
    entry_time = Column(DateTime, default=func.now())
    exit_time = Column(DateTime)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class RabbitTrade(Base):
    """打兔子交易记录"""
    __tablename__ = "rabbit_trades"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    
    # 交易信息
    side = Column(String(10), nullable=False)  # buy/sell
    amount = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    fee = Column(Float, default=0)
    
    # 信号信息
    signal_id = Column(Integer)
    confidence = Column(Float)
    reason = Column(Text)
    
    # PnL
    pnl = Column(Float, default=0)
    
    # 时间
    trade_time = Column(DateTime, default=func.now())


class RabbitConfig(Base):
    """打兔子策略配置"""
    __tablename__ = "rabbit_config"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 策略参数
    max_position_pct = Column(Float, default=0.20)
    stop_loss_pct = Column(Float, default=0.05)
    take_profit_pct = Column(Float, default=0.15)
    trailing_stop_pct = Column(Float, default=0.03)
    
    # 阈值
    strong_trend_threshold = Column(Float, default=7.5)
    volume_spike_ratio = Column(Float, default=2.0)
    rsi_oversold = Column(Float, default=30)
    rsi_overbought = Column(Float, default=70)
    
    # 交易参数
    min_trade_amount = Column(Float, default=100)
    scan_interval = Column(Integer, default=60)
    
    # 状态
    enabled = Column(Boolean, default=True)
    
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
