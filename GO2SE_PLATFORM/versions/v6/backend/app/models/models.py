#!/usr/bin/env python3
"""
🪿 GO2SE 数据模型 - 完整版
包含：用户、认证、交易、风控
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import hashlib


class User(Base):
    """用户"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)
    vip_level = Column(String(20), default="guest")  # guest/member/vip/partner/expert
    status = Column(String(20), default="active")  # active/banned/suspended
    api_quota = Column(Integer, default=1000)  # 每日API配额
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime)
    
    def set_password(self, password: str):
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password: str) -> bool:
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()


class UserAPIKey(Base):
    """用户API密钥"""
    __tablename__ = "user_api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(50))
    key = Column(String(64), unique=True, nullable=False, index=True)
    exchange = Column(String(20))  # binance/bybit/okx
    permissions = Column(JSON)  # {"read": true, "trade": true}
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime)


class UserWallet(Base):
    """用户钱包"""
    __tablename__ = "user_wallets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    wallet_type = Column(String(20))  # main/sub
    address = Column(String(100))
    balance = Column(Float, default=0)
    currency = Column(String(10), default="USDT")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Trade(Base):
    """交易记录"""
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    order_id = Column(String(100), unique=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    side = Column(String(10), nullable=False)  # buy/sell
    amount = Column(Float, nullable=False)
    price = Column(Float)
    fee = Column(Float, default=0)
    status = Column(String(20), default="open")
    pnl = Column(Float, default=0)
    strategy = Column(String(50))
    created_at = Column(DateTime, default=func.now(), index=True)
    closed_at = Column(DateTime)


class Position(Base):
    """持仓"""
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    symbol = Column(String(20), nullable=False, index=True)
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
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    strategy = Column(String(50), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    signal = Column(String(10), nullable=False)  # buy/sell/hold
    confidence = Column(Float, nullable=False)
    price = Column(Float)
    reason = Column(Text)
    executed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now(), index=True)


class StrategyRun(Base):
    """策略执行记录"""
    __tablename__ = "strategy_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy = Column(String(50), nullable=False, index=True)
    status = Column(String(20), nullable=False)
    duration_ms = Column(Integer)
    signals_count = Column(Integer)
    errors = Column(Text)
    created_at = Column(DateTime, default=func.now())


class MarketData(Base):
    """市场数据"""
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    price = Column(Float, nullable=False)
    change_24h = Column(Float)
    volume_24h = Column(Float)
    high_24h = Column(Float)
    low_24h = Column(Float)
    rsi = Column(Float)
    data = Column(JSON)
    created_at = Column(DateTime, default=func.now(), index=True)


class RiskRule(Base):
    """风控规则"""
    __tablename__ = "risk_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    rule_code = Column(String(20), nullable=False)  # R001/R002/etc
    name = Column(String(50), nullable=False)
    condition = Column(String(100))  # >80%/ >30% /etc
    action = Column(String(100))  # 禁止开仓/全部平仓
    enabled = Column(Boolean, default=True)
    priority = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())


class RiskLog(Base):
    """风控日志"""
    __tablename__ = "risk_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    rule_code = Column(String(20))
    triggered = Column(Boolean)
    action_taken = Column(String(100))
    details = Column(JSON)
    created_at = Column(DateTime, default=func.now(), index=True)


class Config(Base):
    """系统配置"""
    __tablename__ = "config"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class APIRateLimit(Base):
    """API速率限制"""
    __tablename__ = "api_rate_limits"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    endpoint = Column(String(50))
    requests_count = Column(Integer, default=0)
    reset_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())


class Notification(Base):
    """通知记录"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    type = Column(String(20))  # signal/trade/risk/system
    title = Column(String(100))
    content = Column(Text)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now(), index=True)
