#!/usr/bin/env python3
"""
🪿 GO2SE 主入口
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.api import routes

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
    description="🪿 北斗七鑫量化交易平台 - 7大策略整合"
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


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
