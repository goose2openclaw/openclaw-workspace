#!/usr/bin/env python3
"""
🪿 GO2SE 量化交易平台 - 核心配置 v11
"""

import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用
    APP_NAME: str = "GO2SE北斗七鑫量化交易平台"
    APP_VERSION: str = "v11.0.0"
    APP_BUILD: str = "backend-v11"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # 数据库
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./go2se.db"
    )
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "10"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_ENABLED: bool = os.getenv("REDIS_ENABLED", "false").lower() == "true"
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "60"))
    
    # 交易配置
    TRADING_MODE: str = os.getenv("TRADING_MODE", "dry_run")
    MAX_POSITION: float = float(os.getenv("MAX_POSITION", "0.6"))
    STOP_LOSS: float = float(os.getenv("STOP_LOSS", "0.10"))
    TAKE_PROFIT: float = float(os.getenv("TAKE_PROFIT", "0.30"))
    
    # 交易对
    TRADING_PAIRS: List[str] = [
        "BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "BNB/USDT",
        "ADA/USDT", "DOGE/USDT", "DOT/USDT", "AVAX/USDT", "LINK/USDT"
    ]
    
    # 资金配置
    TOTAL_CAPITAL: float = float(os.getenv("TOTAL_CAPITAL", "100000.0"))
    
    # 策略权重
    RABBIT_WEIGHT: float = 0.25
    MOLE_WEIGHT: float = 0.20
    ORACLE_WEIGHT: float = 0.15
    LEADER_WEIGHT: float = 0.15
    HITCHHIKER_WEIGHT: float = 0.10
    AIRDROP_WEIGHT: float = 0.03
    CROWDSOURCE_WEIGHT: float = 0.02
    
    # 策略执行间隔 (秒)
    STRATEGY_INTERVAL_RABBIT: int = 300
    STRATEGY_INTERVAL_MOLE: int = 60
    STRATEGY_INTERVAL_ORACLE: int = 600
    STRATEGY_INTERVAL_LEADER: int = 60
    STRATEGY_INTERVAL_HITCHHIKER: int = 1800
    
    # API配置 - v11 增强
    API_RATE_LIMIT: int = int(os.getenv("API_RATE_LIMIT", "1200"))
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "10"))
    API_READ_TIMEOUT: int = int(os.getenv("API_READ_TIMEOUT", "30"))
    API_CONNECT_TIMEOUT: int = int(os.getenv("API_CONNECT_TIMEOUT", "10"))
    API_MAX_RETRIES: int = int(os.getenv("API_MAX_RETRIES", "3"))
    
    # 请求验证
    REQUEST_MAX_SIZE: int = int(os.getenv("REQUEST_MAX_SIZE", "1048576"))  # 1MB
    
    # 缓存配置
    CACHE_TTL_PRICE: int = int(os.getenv("CACHE_TTL_PRICE", "5"))
    CACHE_TTL_OHLCV: int = int(os.getenv("CACHE_TTL_OHLCV", "30"))
    CACHE_TTL_ORDERBOOK: int = int(os.getenv("CACHE_TTL_ORDERBOOK", "2"))
    CACHE_TTL_SIGNALS: int = int(os.getenv("CACHE_TTL_SIGNALS", "60"))
    CACHE_TTL_STATS: int = int(os.getenv("CACHE_TTL_STATS", "10"))
    
    # 日志
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "%(asctime)s | %(levelname)-8s | %(message)s")
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ] + ([os.getenv("CORS_ORIGIN")] if os.getenv("CORS_ORIGIN") else [])
    
    # 备份配置
    DB_BACKUP_DIR: str = os.getenv("DB_BACKUP_DIR", "/root/.openclaw/workspace/GO2SE_PLATFORM/backups")
    DB_BACKUP_RETENTION: int = int(os.getenv("DB_BACKUP_RETENTION", "7"))
    
    # 健康检查
    HEALTH_CHECK_INTERVAL: int = int(os.getenv("HEALTH_CHECK_INTERVAL", "300"))
    HEALTH_CHECK_TIMEOUT: int = int(os.getenv("HEALTH_CHECK_TIMEOUT", "10"))
    
    # 策略热更新
    STRATEGY_CONFIG_PATH: str = os.getenv("STRATEGY_CONFIG_PATH", "/root/.openclaw/workspace/GO2SE_PLATFORM/config/strategies.yaml")
    STRATEGY_WATCH_ENABLED: bool = os.getenv("STRATEGY_WATCH_ENABLED", "true").lower() == "true"
    
    # Polymarket
    POLYMARKET_API_URL: str = os.getenv("POLYMARKET_API_URL", "https://clob.polymarket.com")
    POLYMARKET_API_KEY: str = os.getenv("POLYMARKET_API_KEY", "")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
