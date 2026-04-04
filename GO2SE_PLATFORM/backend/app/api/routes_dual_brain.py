"""
🧠 GO2SE 左右脑架构 API路由
===========================

2026-04-04
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import asyncio
import time

router = APIRouter(prefix="/api/dual-brain", tags=["左右脑架构"])

# 全局引擎实例
_engine = None

async def get_engine():
    global _engine
    if _engine is None:
        from app.core.go2se_brain_architecture import GO2SEDualBrainEngine
        _engine = GO2SEDualBrainEngine()
        await _engine.start()
    return _engine


# === 状态和监控 ===

@router.get("/status")
async def get_status():
    """获取双脑状态"""
    engine = await get_engine()
    return await engine.get_status()


@router.get("/brain-status")
async def get_brain_status():
    """获取左右脑详细状态"""
    engine = await get_engine()
    status = engine.brain_manager.get_status()
    
    return {
        "active_brain": status["active_brain"],
        "active_mode": status["active_mode"],
        "left_brain": status["left_brain"],
        "right_brain": status["right_brain"],
        "timestamp": time.time()
    }


@router.post("/heartbeat")
async def send_heartbeat():
    """发送心跳"""
    engine = await get_engine()
    status = await engine.brain_manager.send_heartbeat()
    return status


# === 切换操作 ===

class SwitchRequest(BaseModel):
    target: str  # "left", "right", "normal", "expert"


@router.post("/switch")
async def switch(request: SwitchRequest):
    """切换脑或模式"""
    engine = await get_engine()
    bm = engine.brain_manager
    
    # 判断是切换脑还是切换模式
    if request.target in ["left", "right"]:
        result = await bm.switch_brain(request.target)
    elif request.target in ["normal", "expert"]:
        result = await bm.switch_mode(request.target)
    else:
        result = {"success": False, "error": "Invalid target"}
    
    return {
        **result,
        "timestamp": time.time()
    }


@router.post("/switch-brain")
async def switch_brain(target_brain_id: str):
    """切换到指定脑"""
    engine = await get_engine()
    result = await engine.brain_manager.switch_brain(target_brain_id)
    return {**result, "timestamp": time.time()}


@router.post("/switch-mode")
async def switch_mode(target_mode: str):
    """切换到指定模式"""
    engine = await get_engine()
    result = await engine.brain_manager.switch_mode(target_mode)
    return {**result, "timestamp": time.time()}


# === 钱包操作 ===

@router.get("/wallet-status")
async def get_wallet_status():
    """获取钱包状态"""
    engine = await get_engine()
    return engine.brain_manager.wallet.get_status()


class TransferRequest(BaseModel):
    amount: float
    target: str  # "binance", "bybit", "okx"


@router.post("/transfer-to-exchange")
async def transfer_to_exchange(request: TransferRequest):
    """中转资金到交易所"""
    engine = await get_engine()
    result = engine.brain_manager.wallet.transfer_to_exchange(
        request.amount, request.target
    )
    return {**result, "timestamp": time.time()}


@router.post("/return-to-main")
async def return_to_main(amount: float):
    """收益回流主钱包"""
    engine = await get_engine()
    result = engine.brain_manager.wallet.return_to_main(amount)
    return {**result, "timestamp": time.time()}


# === 龙虾模块 ===

@router.post("/lobster/retro")
async def run_retro():
    """运行复盘"""
    engine = await get_engine()
    result = await engine.lobster.run_retro()
    return {**result, "timestamp": time.time()}


@router.post("/lobster/simulation")
async def run_simulation():
    """运行仿真"""
    engine = await get_engine()
    result = await engine.lobster.run_simulation()
    return {**result, "timestamp": time.time()}


@router.post("/lobster/optimization")
async def run_optimization():
    """运行优化"""
    engine = await get_engine()
    result = await engine.lobster.run_optimization()
    return {**result, "timestamp": time.time()}


@router.post("/lobster/full-cycle")
async def run_full_cycle():
    """运行完整龙虾周期"""
    engine = await get_engine()
    result = await engine.lobster.run_full_cycle()
    return {**result, "timestamp": time.time()}


@router.get("/lobster/status")
async def get_lobster_status():
    """获取龙虾状态"""
    engine = await get_engine()
    return engine.lobster.get_lobster_status()


# === 交易操作 ===

class TradeRequest(BaseModel):
    signal: Dict


@router.post("/execute-trade")
async def execute_trade(request: TradeRequest):
    """执行交易"""
    engine = await get_engine()
    result = await engine.execute_trade(request.signal)
    return {
        **result,
        "active_brain": engine.brain_manager.active_brain.brain_id,
        "mode": engine.brain_manager.current_mode,
        "timestamp": time.time()
    }


# === 控制 ===

@router.post("/start")
async def start_engine():
    """启动引擎"""
    engine = await get_engine()
    await engine.start()
    return {"status": "started", "timestamp": time.time()}


@router.post("/stop")
async def stop_engine():
    """停止引擎"""
    engine = await get_engine()
    await engine.stop()
    return {"status": "stopped", "timestamp": time.time()}


@router.post("/reset")
async def reset_engine():
    """重置引擎"""
    global _engine
    _engine = None
    return {"status": "reset", "timestamp": time.time()}
