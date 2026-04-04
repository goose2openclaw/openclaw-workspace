#!/usr/bin/env python3
"""
🪿 GO2SE 主入口 V7
==================
北斗七鑫投资体系 + 25维度全向仿真
"""

import logging
import uuid
from datetime import datetime
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.core.database import init_db
from app.core.rate_limiter import rate_limiter
from app.core.risk_manager import risk_manager
from app.api import routes
from app.api.strategies_extra import router as strategies_extra_router
from app.api.oracle.mirofish import router as mirofish_router
from app.api.routes_v7 import router as routes_v7_router
from app.api.routes_sonar import router as sonar_router
from app.api.routes_expert import router as expert_router
from app.api.routes_market import router as market_router
from app.api.routes_ai_portfolio import router as ai_portfolio_router
from app.api.routes_mirofish_decision import router as mirofish_decision_router
from app.api.routes_backtest import router as backtest_router
from app.api.routes_paper_trading import router as paper_trading_router
from app.api.routes_expert_mode import router as expert_mode_router
from app.api.routes_factor_degradation import router as factor_degradation_router
from app.api.routes_optimizer import router as optimizer_router
from app.api.routes_mapping import router as mapping_router
from app.api.routes_public import router as public_router

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


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """⚡ API速率限制中间件"""
    # 跳过健康检查和根路径
    if request.url.path in ["/", "/health", "/docs", "/openapi.json", "/redoc"]:
        return await call_next(request)
    
    # 获取客户端标识 (优先X-Forwarded-For, 否则client_id)
    client_ip = request.headers.get("x-forwarded-for", "unknown")
    if client_ip == "unknown":
        client_ip = request.headers.get("x-real-ip", "unknown")
    client_id = f"{client_ip}:{request.url.path}"
    
    # 检查速率限制
    allowed, info = rate_limiter.check(request.url.path, client_id)
    
    # 添加速率限制头
    response = await call_next(request)
    response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
    response.headers["X-RateLimit-Limit"] = str(settings.API_RATE_LIMIT)
    response.headers["X-RateLimit-Reset"] = info["reset_at"]
    
    if not allowed:
        logger.warning(f"⚠️ 速率限制触发: {client_id} - {request.url.path}")
        return Response(
            content='{"error":"Rate limit exceeded","retry_after":"' + info["reset_at"] + '"}',
            status_code=429,
            media_type="application/json",
            headers={
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Limit": str(settings.API_RATE_LIMIT),
                "X-RateLimit-Reset": info["reset_at"],
                "Retry-After": str(int((datetime.fromisoformat(info["reset_at"]) - datetime.now()).total_seconds()))
            }
        )
    
    return response


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
app.include_router(sonar_router, tags=["声纳库"])
app.include_router(expert_router, tags=["专家模式"])
app.include_router(market_router, tags=["实时市场"])
app.include_router(ai_portfolio_router, tags=["AI策略组合"])
app.include_router(mirofish_decision_router, tags=["MiroFish决策"])
app.include_router(backtest_router, tags=["回测"])
app.include_router(paper_trading_router, tags=["模拟交易"])
app.include_router(expert_mode_router, tags=["专家模式配置"])
app.include_router(factor_degradation_router, tags=["因子退化检测"])
app.include_router(optimizer_router, tags=["优化器"])
app.include_router(public_router, tags=["公开数据"])
app.include_router(mapping_router, tags=["Mapping"])


@app.get("/")
async def root():
    """根路径 - 返回HTML仪表盘"""
    import os
    html_path = os.path.join(os.path.dirname(__file__), "frontend.html")
    with open(html_path, encoding="utf-8") as f:
        content = f.read()
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=content)


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
        db.execute(text("SELECT 1"))
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
            "error_rate": risk_manager.api_errors / max(risk_manager.api_total, 1),
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


# ─── 静态文件服务: React构建版本 ─────────────────────────────────────
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

dist_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
if os.path.exists(dist_path):
    # 挂载 /app 到 React构建目录
    app.mount("/app", StaticFiles(directory=dist_path, html=True), name="react-app")

    @app.get("/app")
    async def serve_react_index():
        """React单页应用入口"""
        return FileResponse(os.path.join(dist_path, "index.html"))

    @app.get("/app/{path:path}")
    async def serve_react_assets(path: str):
        """React静态资源"""
        file_path = os.path.join(dist_path, path)
        if os.path.exists(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(dist_path, "index.html"))

    logger.info(f"✅ React静态文件已挂载: /app")

# ─── /api/performance 端点 ──────────────────────────────────────────
@app.get("/api/performance")
async def get_performance():
    """📊 性能矩阵 + 资金分配端点 - 北斗七鑫V10"""
    import json as _json

    # 读取matrix文件
    matrix_path = os.path.join(os.path.dirname(__file__), "..", "..", "performance_matrix_v8.json")

    # 读取active_strategy配置
    strategy_path = "/root/.openclaw/workspace/GO2SE_PLATFORM/active_strategy.json"
    strategy_data = {}
    if os.path.exists(strategy_path):
        with open(strategy_path) as f:
            strategy_data = _json.load(f)

    tools_cfg = strategy_data.get("tools", {})
    work_cfg = strategy_data.get("work_tools", {})

    # 5个投资工具 + 2个打工工具 = 7工具资金分配
    # AI动态调度: 所有工具启用，权重由AI根据表现自动调整
    # weight=0表示AI已调至最低，但仍监控；AI可恢复任意工具权重
    investment_tools = {
        "rabbit":    {"name": "🐰 打兔子",   "weight": 25,  "status": "ai_managed", "expert_score": 75.0, "color": "#64748B"},   # 主流币，稳定
        "mole":      {"name": "🐹 打地鼠",   "weight": 20,  "status": "ai_managed", "expert_score": 89.0, "color": "#00D4AA"},   # 异动币，高收益
        "oracle":    {"name": "🔮 走着瞧",   "weight": 15,  "status": "ai_managed", "expert_score": 80.0, "color": "#7C3AED"},   # 预测市场
        "leader":    {"name": "👑 跟大哥",   "weight": 15,  "status": "ai_managed", "expert_score": 60.0, "color": "#F59E0B"},   # 做市协作
        "hitchhiker":{"name": "🍀 搭便车",   "weight": 10,  "status": "ai_managed", "expert_score": 85.0, "color": "#3B82F6"},   # 跟单分成
    }
    work_tools = {
        "wool":      {"name": "💰 薅羊毛",   "weight": 3,   "cashflow_rate": 0.02, "accumulated": 0.0, "color": "#EF4444"},
        "poor":      {"name": "👶 穷孩子",   "weight": 5,   "cashflow_rate": 0.03, "accumulated": 0.0, "color": "#EC4899"},
    }

    # 读取最新权重
    for tool_id in investment_tools:
        if tool_id in tools_cfg:
            investment_tools[tool_id]["weight"] = tools_cfg[tool_id].get("weight", investment_tools[tool_id]["weight"])
            investment_tools[tool_id]["status"] = tools_cfg[tool_id].get("status", investment_tools[tool_id]["status"])
    for tool_id in work_tools:
        if tool_id in work_cfg:
            work_tools[tool_id]["weight"] = work_cfg[tool_id].get("base_weight", work_tools[tool_id]["weight"]) * 100
            work_tools[tool_id]["cashflow_rate"] = work_cfg[tool_id].get("cashflow_rate", work_tools[tool_id]["cashflow_rate"])
            work_tools[tool_id]["accumulated"] = work_cfg[tool_id].get("cashflow_accumulated", 0)

    # 资金池 (从环境变量配置，支持 Docker/K8s 动态注入)
    total_capital = settings.TOTAL_CAPITAL
    investment_pool = total_capital * 0.80  # 80%投资
    work_pool = total_capital * 0.20        # 20%打工

    for tool in investment_tools.values():
        tool["allocation"] = round(investment_pool * tool["weight"] / 100, 2)
    for tool in work_tools.values():
        tool["allocation"] = round(work_pool * tool["weight"] / 100, 2)

    # 打工现金流收集状态
    cashflow_pool = sum(t["accumulated"] for t in work_tools.values())

    return {
        "strategy": "auto_optimizer_v10",
        "timestamp": datetime.now().isoformat(),
        "total_capital": total_capital,
        "investment_pool": investment_pool,
        "work_pool": work_pool,
        "cashflow_pool": cashflow_pool,
        "investment_tools": investment_tools,
        "work_tools": work_tools,
        "actions": {
            "replenish": {
                "description": "补仓 - 从现金池向亏损工具追加资金",
                "available": cashflow_pool > 100,
                "min_amount": 100,
                "targets": [t["name"] for t in investment_tools.values() if t["status"] == "active"]
            },
            "cashout": {
                "description": "套现 - 将盈利工具资金转出",
                "available": True,
                "min_amount": 50,
                "targets": [t["name"] for t in investment_tools.values() if t["status"] == "active"]
            },
            "work_to_invest": {
                "description": "打工收益补充投资 - 薅羊毛/穷孩子收益转入投资池",
                "available": cashflow_pool > 500,
                "threshold": 500,
                "sources": [t["name"] for t in work_tools.values()],
                "targets": ["🐹 打地鼠", "🔮 走着瞧", "🍀 搭便车"]
            }
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
