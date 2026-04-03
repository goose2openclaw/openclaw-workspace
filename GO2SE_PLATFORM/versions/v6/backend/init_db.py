#!/usr/bin/env python3
"""
🪿 GO2SE 数据库初始化脚本
创建所有表 + 基础数据
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.models import (
    User, UserAPIKey, UserWallet, Trade, Position, Signal,
    StrategyRun, MarketData, RiskRule, RiskLog, Config, APIRateLimit, Notification
)

def init_db():
    print("🛠️  初始化数据库...")
    
    # 创建引擎
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
    )
    
    # 检查已有表
    inspector = inspect(engine)
    existing = inspector.get_table_names()
    print(f"已有表: {existing}")
    
    # 导入所有模型以确保被注册
    from app.models.models import Base
    
    # 创建缺失的表
    Base.metadata.create_all(bind=engine)
    
    # 验证
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"✅ 当前表: {tables}")
    print(f"✅ 共 {len(tables)} 个表")
    
    # 插入基础数据
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # 检查是否已有用户
    if session.query(User).count() == 0:
        print("\n📝 创建默认用户...")
        default_user = User(
            username="admin",
            email="admin@go2se.local",
            password_hash="e10adc3949ba59abbe56e057f20f883e",  # 123456
            vip_level="expert",
            status="active",
            api_quota=999999
        )
        session.add(default_user)
        
        # 基础风控规则 (使用正确的列名)
        risk_rules = [
            RiskRule(rule_code="R001", name="仓位限制", condition="position>80%", action="禁止开仓"),
            RiskRule(rule_code="R002", name="日内熔断", condition="daily_loss>30%", action="全部平仓"),
            RiskRule(rule_code="R003", name="单笔风险", condition="risk>5%", action="警告"),
            RiskRule(rule_code="R004", name="波动止损", condition="volatility>8%", action="止损"),
            RiskRule(rule_code="R005", name="流动性检查", condition="volume<100K", action="警告"),
        ]
        for rule in risk_rules:
            session.add(rule)
        
        session.commit()
        print("✅ 基础数据已创建")
    else:
        print("\nℹ️  用户已存在，跳过初始化数据")
    
    session.close()
    print("\n🎉 数据库初始化完成!")

if __name__ == "__main__":
    init_db()
