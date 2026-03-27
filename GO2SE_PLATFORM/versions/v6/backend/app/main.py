#!/usr/bin/env python3
"""
🪿 GO2SE 主入口
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 简化配置
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="GO2SE", version="6.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"name": "GO2SE", "version": "6.0.0", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# 北斗七鑫路由
from app.services.rabbit import api as rabbit_api
from app.services.mole import api as mole_api
from app.services.oracle import strategy as oracle_api

app.include_router(rabbit_api.router, prefix="/api/rabbit", tags=["打兔子"])
app.include_router(mole_api.router, prefix="/api/mole", tags=["打地鼠"])
# app.include_router(oracle_api.router, prefix="/api/oracle", tags=["走着燋"])

# 模拟交易路由
from app.routes import sim_trading
app.include_router(sim_trading.router)

# 回测系统路由
from app.routes import backtest_api
app.include_router(backtest_api.router)

# 备选策略路由
from app.routes import alt_strategies_api
app.include_router(alt_strategies_api.router)

# 备选策略V2路由
from app.routes import alternatives
app.include_router(alternatives.router)

# MiroFish路由
from app.services.oracle import mirofish_api
app.include_router(mirofish_api.router)

# 实时行情路由
from app.routes import market_api
app.include_router(market_api.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
