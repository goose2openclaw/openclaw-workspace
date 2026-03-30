#!/usr/bin/env python3
"""
🪿 GO2SE 主入口 V7
==================
北斗七鑫投资体系 + 25维度全向仿真
"""

import logging
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.api import routes
from app.api.strategies_extra import router as strategies_extra_router
from app.api.oracle.mirofish import router as mirofish_router
from app.api.routes_v7 import router as routes_v7_router

# 日志配置
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger("go2se")

# 创建应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="🪿 北斗七鑫量化交易平台 V7 - 7大策略 + 25维度全向仿真"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """启动事件"""
    logger.info(f"🚀 {settings.APP_NAME} {settings.APP_VERSION} 启动中...")
    
    # 初始化数据库
    init_db()
    logger.info("✅ 数据库初始化完成")
    
    # 初始化交易引擎
    from app.core.trading_engine import engine
    engine.init_exchange()
    logger.info("✅ 交易引擎初始化完成")
    
    logger.info(f"🪿 交易模式: {settings.TRADING_MODE}")
    logger.info(f"📊 最大仓位: {settings.MAX_POSITION * 100}%")


@app.on_event("shutdown")
async def shutdown_event():
    """关闭事件"""
    logger.info("🔴 应用关闭中...")


# 注册路由
app.include_router(routes.router, prefix="/api", tags=["API"])
app.include_router(strategies_extra_router, prefix="/api", tags=["额外策略"])
app.include_router(mirofish_router, tags=["MiroFish预言机"])
app.include_router(routes_v7_router, tags=["V7北斗七鑫"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """📊 SRE健康检查端点 - Golden Signals监控"""
    import time
    import psutil
    
    start = time.time()
    
    # 检查数据库
    try:
        from app.core.database import get_db
        db = next(get_db())
        db.execute("SELECT 1")
        db_ok = True
    except Exception:
        db_ok = False
    
    # 检查交易所连接
    try:
        from app.core.trading_engine import engine
        exchange_ok = engine.exchange is not None
    except Exception:
        exchange_ok = False
    
    # 系统指标
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    response_time = (time.time() - start) * 1000  # ms
    
    # 状态评估
    status = "healthy" if (db_ok and exchange_ok and response_time < 500) else "degraded"
    
    return {
        "status": status,
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.APP_VERSION,
        "signals": {
            "latency_ms": round(response_time, 2),
            "latency_status": "✅" if response_time < 500 else "⚠️",
            "error_rate": 0.0,  # TODO: 实现错误追踪
            "saturation_cpu": cpu_percent,
            "saturation_memory": memory.percent,
            "saturation_disk": disk.percent
        },
        "dependencies": {
            "database": "✅" if db_ok else "❌",
            "exchange": "✅" if exchange_ok else "❌"
        },
        "limits": {
            "cpu_alert": cpu_percent > 80,
            "memory_alert": memory.percent > 80,
            "disk_alert": disk.percent > 85
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
