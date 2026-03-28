#!/usr/bin/env python3
"""
🪿 GO2SE 量化交易平台 - 核心配置
"""

import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用
    APP_NAME: str = "GO2SE量化交易平台"
    APP_VERSION: str = "v1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # 数据库
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./go2se.db"
    )
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # 交易配置
    TRADING_MODE: str = os.getenv("TRADING_MODE", "dry_run")  # dry_run 或 live
    MAX_POSITION: float = float(os.getenv("MAX_POSITION", "0.6"))
    STOP_LOSS: float = float(os.getenv("STOP_LOSS", "0.10"))
    TAKE_PROFIT: float = float(os.getenv("TAKE_PROFIT", "0.30"))
    
    # 交易对
    TRADING_PAIRS: List[str] = [
        "BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "BNB/USDT",
        "ADA/USDT", "DOGE/USDT", "DOT/USDT", "AVAX/USDT", "LINK/USDT"
    ]
    
    # 策略权重
    RABBIT_WEIGHT: float = 0.25      # 打兔子
    MOLE_WEIGHT: float = 0.20        # 打地鼠
    ORACLE_WEIGHT: float = 0.15      # 走着瞧
    LEADER_WEIGHT: float = 0.15      # 跟大哥
    HITCHHIKER_WEIGHT: float = 0.10 # 搭便车
    AIRDROP_WEIGHT: float = 0.03    # 薅羊毛
    CROWDSOURCE_WEIGHT: float = 0.02 # 穷孩子
    
    # 策略执行间隔 (秒)
    STRATEGY_INTERVAL_RABBIT: int = 300    # 5分钟
    STRATEGY_INTERVAL_MOLE: int = 60       # 1分钟
    STRATEGY_INTERVAL_ORACLE: int = 600   # 10分钟
    STRATEGY_INTERVAL_LEADER: int = 60     # 1分钟
    STRATEGY_INTERVAL_HITCHHIKER: int = 1800  # 30分钟
    
    # API配置
    BINANCE_API_KEY: str = os.getenv("BINANCE_API_KEY", "")
    BINANCE_SECRET_KEY: str = os.getenv("BINANCE_SECRET_KEY", "")
    API_RATE_LIMIT: int = int(os.getenv("API_RATE_LIMIT", "1200"))
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "5"))
    
    # 缓存配置
    CACHE_TTL_PRICE: int = int(os.getenv("CACHE_TTL_PRICE", "5"))
    CACHE_TTL_OHLCV: int = int(os.getenv("CACHE_TTL_OHLCV", "30"))
    CACHE_TTL_ORDERBOOK: int = int(os.getenv("CACHE_TTL_ORDERBOOK", "2"))
    
    # 日志
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # CORS - 支持本地和生产环境
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        # 生产环境 (根据环境变量添加)
    ] + ([os.getenv("CORS_ORIGIN", "")] if os.getenv("CORS_ORIGIN") else [])
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
