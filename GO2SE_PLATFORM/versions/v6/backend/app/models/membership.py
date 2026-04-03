#!/usr/bin/env python3
"""
🪿 GO2SE 会员体系
完整的会员等级和权益
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class Membership(Base):
    """会员等级"""
    __tablename__ = "memberships"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 会员等级
    level = Column(String(20), default="guest")  # guest/subscription/vip/partner/expert
    sub_level = Column(String(20))  # bronze/silver/gold/diamond
    
    # 订阅信息
    subscription_fee = Column(Float, default=0)  # 月费
    subscription_status = Column(String(20))  # active/cancelled/expired
    subscription_start = Column(DateTime)
    subscription_end = Column(DateTime)
    
    # 模拟交易
    simulated_balance = Column(Float, default=1000)  # 模拟金
    simulated_pnl = Column(Float, default=0)  # 模拟收益
    simulated_converted = Column(Boolean, default=False)  # 是否已转存
    
    # 中转钱包
    transit_wallet_enabled = Column(Boolean, default=False)
    transit_wallet_address = Column(String(100))
    transit_wallet_limit = Column(Float, default=0)  # 限额
    
    # 权益
    api_quota = Column(Integer, default=1000)
    compute_priority = Column(Integer, default=1)  # 1-10
    api_priority = Column(Integer, default=1)  # 1-10
    reserve_fund_limit = Column(Float, default=0)  # 备用金限额
    leverage_enabled = Column(Boolean, default=False)
    max_leverage = Column(Float, default=1.0)
    
    # 专家模式
    expert_mode = Column(Boolean, default=False)
    expert_model_level = Column(Integer, default=1)  # 1-5
    
    # 私募LP
    lp_tier = Column(String(20))  # none/silver/gold/platinum
    lp_deposit = Column(Float, default=0)  # 存入金额
    lp_monthly_volume = Column(Float, default=0)  # 月活跃量
    
    # 收益分成
    platform_share = Column(Float, default=0)  # 平台分成比例
    profit_sharing_tiers = Column(JSON)  # 分成阶梯
    
    # 时间
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


# 会员等级配置
MEMBERSHIP_TIERS = {
    "guest": {
        "name": "游客",
        "monthly_fee": 0,
        "simulated_balance": 1000,
        "api_quota": 1000,
        "tools": ["rabbit", "mole"],
        "features": ["模拟交易", "基础策略"],
        "withdraw_simulated": True,
    },
    "subscription": {
        "name": "订阅",
        "monthly_fee": 49,
        "simulated_balance": 4000,  # 3000 + 1000
        "api_quota": 5000,
        "tools": ["rabbit", "mole", "oracle", "leader", "hitchhiker"],
        "features": ["全部工具", "中转钱包", "优先信号"],
        "transit_wallet": True,
        "withdraw_simulated": True,
    },
    "vip": {
        "name": "会员",
        "monthly_fee": 99,
        "yearly_fee": 89,
        "min_months": 6,
        "simulated_balance": 6000,  # 5000 + 1000
        "api_quota": 20000,
        "compute_priority": 5,
        "api_priority": 5,
        "tools": ["rabbit", "mole", "oracle", "leader", "hitchhiker", "airdrop", "crowd"],
        "features": ["全部工具", "高级中转钱包", "算力优先", "API优先", "加强风控"],
        "transit_wallet": True,
        "transit_limit": 10000,
        "reserve_fund": 5000,
    },
    "partner": {
        "name": "私募LP",
        "monthly_fee": 0,
        "min_deposit": 100000,
        "lp_tiers": {
            "silver": {"deposit": 100000, "monthly_volume": 20000, "leverage": 2, "profit_share": 0.10},
            "gold": {"deposit": 500000, "monthly_volume": 50000, "leverage": 3, "profit_share": 0.15},
            "platinum": {"deposit": 1000000, "monthly_volume": 100000, "leverage": 5, "profit_share": 0.20},
        },
        "api_quota": 100000,
        "compute_priority": 8,
        "api_priority": 8,
        "tools": "all",
        "features": ["全部工具", "专家模式", "备用金", "杠杆", "1对1服务", "收益分红"],
        "expert_mode": True,
        "transit_wallet": True,
        "transit_limit": 100000,
        "reserve_fund": 50000,
        "max_leverage": 5.0,
    },
    "expert": {
        "name": "专家模式",
        "monthly_fee": 199,
        "yearly_discount": 30,  # 每月减30
        "api_quota": 50000,
        "compute_priority": 10,
        "api_priority": 10,
        "features": ["高级算力", "低成本备用金", "专业杠杆", "深度推理"],
        "expert_model_level": 3,
        "leverage_enabled": True,
        "max_leverage": 3.0,
    },
}

# 收益分成阶梯
PROFIT_SHARING_TIERS = [
    {"tier": 1, "profit_from": 0, "profit_to": 1000, "platform_share": 0.20, "user_share": 0.80},
    {"tier": 2, "profit_from": 1000, "profit_to": 5000, "platform_share": 0.15, "user_share": 0.85},
    {"tier": 3, "profit_from": 5000, "profit_to": 10000, "platform_share": 0.10, "user_share": 0.90},
    {"tier": 4, "profit_from": 10000, "profit_to": 50000, "platform_share": 0.08, "user_share": 0.92},
    {"tier": 5, "profit_from": 50000, "profit_to": 999999999, "platform_share": 0.05, "user_share": 0.95},
]


class InvestmentTool(Base):
    """投资工具配置"""
    __tablename__ = "investment_tools"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 工具标识
    tool_id = Column(String(20), unique=True, nullable=False)
    name = Column(String(50), nullable=False)
    icon = Column(String(10))
    category = Column(String(20))  # investment/work
    
    # 投资类型
    investment_type = Column(String(20))  # rabbit/mole/oracle/leader/hitchhiker
    
    # 算力配置
    compute_required = Column(Integer, default=1)  # 所需算力
    api_priority = Column(Integer, default=5)  # API优先级
    min_trade_amount = Column(Float, default=10)
    
    # 检测配置
    scan_interval = Column(Integer, default=60)  # 扫描间隔秒
    detection_threshold = Column(Float, default=0.7)  # 检测阈值
    
    # 策略参数
    default_stop_loss = Column(Float, default=0.05)
    default_take_profit = Column(Float, default=0.15)
    max_position = Column(Float, default=0.20)
    
    # 适用市场
    applicable_markets = Column(JSON)  # ["binance", "bybit", "polymarket"]
    
    # 会员等级要求
    required_level = Column(String(20), default="guest")
    
    # 状态
    enabled = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class MarketCondition(Base):
    """市场条件记录"""
    __tablename__ = "market_conditions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 市场标识
    symbol = Column(String(20), index=True)
    market_type = Column(String(20))  # crypto/stock/polymarket
    
    # 趋势指标
    trend_strength = Column(Float)  # 0-10
    volatility = Column(Float)      # 0-10
    rsi = Column(Float)
    momentum = Column(Float)
    sentiment = Column(Float)       # -10 to 10
    
    # 条件判断
    trend_direction = Column(String(10))  # bullish/bearish/neutral
    condition_type = Column(String(20))  # strong_trend/weak_trend/high_freq
    
    # 时间
    created_at = Column(DateTime, default=func.now(), index=True)


class TradeRecommendation(Base):
    """交易推荐"""
    __tablename__ = "trade_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 用户
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # 推荐信息
    symbol = Column(String(20), nullable=False, index=True)
    investment_type = Column(String(20), nullable=False)
    
    # 信号
    signal = Column(String(10), nullable=False)  # buy/sell/hold
    confidence = Column(Float, nullable=False)  # 0-10
    position_size = Column(Float)
    stop_loss = Column(Float)
    take_profit = Column(Float)
    
    # 原因
    reason = Column(Text)
    market_condition = Column(JSON)
    
    # 状态
    status = Column(String(20), default="pending")  # pending/executed/expired
    
    # 时间
    created_at = Column(DateTime, default=func.now())
    executed_at = Column(DateTime)
    expired_at = Column(DateTime)
