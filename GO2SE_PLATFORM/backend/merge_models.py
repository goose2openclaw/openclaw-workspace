#!/usr/bin/env python3
"""合并v6模型到当前models.py"""

with open('/root/.openclaw/workspace/GO2SE_PLATFORM/backend/app/models/models.py', 'r') as f:
    current = f.read()

# 要添加的v6模型类（当前缺失的）
additions = '''
class UserAPIKey(Base):
    """用户API密钥"""
    __tablename__ = "user_api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(50))
    key = Column(String(64), unique=True, nullable=False, index=True)
    exchange = Column(String(20))
    permissions = Column(JSON)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime)


class UserWallet(Base):
    """用户钱包"""
    __tablename__ = "user_wallets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    wallet_type = Column(String(20))
    address = Column(String(100))
    balance = Column(Float, default=0)
    currency = Column(String(10), default="USDT")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class RiskRule(Base):
    """风控规则"""
    __tablename__ = "risk_rules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    rule_code = Column(String(20), nullable=False)
    name = Column(String(50), nullable=False)
    condition = Column(String(100))
    action = Column(String(100))
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
    type = Column(String(20))
    title = Column(String(100))
    content = Column(Text)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now(), index=True)
'''

# 在BacktestResult后添加
if 'class Notification(Base)' not in current:
    current = current.rstrip() + '\n' + additions
    with open('/root/.openclaw/workspace/GO2SE_PLATFORM/backend/app/models/models.py', 'w') as f:
        f.write(current)
    print("✅ Models merged successfully")
else:
    print("ℹ️  Notification already exists")
