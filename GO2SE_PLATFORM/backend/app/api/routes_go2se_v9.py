"""
🚀 GO2SE V9 API路由
====================

2026-04-04
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import asyncio
import time

router = APIRouter(prefix="/api/go2se/v9", tags=["GO2SE V9"])

_engine_normal = None
_engine_expert = None

async def get_engine(mode: str):
    global _engine_normal, _engine_expert
    if mode == "expert":
        if _engine_expert is None:
            from app.core.go2se_v9_core import GO2SEV9Engine
            _engine_expert = GO2SEV9Engine(mode="expert")
        return _engine_expert
    else:
        if _engine_normal is None:
            from app.core.go2se_v9_core import GO2SEV9Engine
            _engine_normal = GO2SEV9Engine(mode="normal")
        return _engine_normal


class ScanRequest(BaseModel):
    targets: List[str]
    tool_type: str = "general"


class SnipeRequest(BaseModel):
    opportunity: Dict
    urgency: str = "high"


class TradeRequest(BaseModel):
    signal: Dict


class ComputeScheduleRequest(BaseModel):
    tasks: List[Dict]
    budget: int = 1000


class ResourceMatchRequest(BaseModel):
    tasks: List[Dict]
    resources: Dict


class RetroRequest(BaseModel):
    sprint: str


# === 核心功能 ===

@router.post("/scan-and-select")
async def scan_and_select(request: ScanRequest, mode: str = "normal"):
    """扫描选品 - 全域扫描 + 深度扫描 + MiroFish共识"""
    engine = await get_engine(mode)
    results = await engine.scan_and_select(request.targets, request.tool_type)
    
    return {
        "mode": mode,
        "tool_type": request.tool_type,
        "results": results,
        "total": len(results),
        "timestamp": time.time()
    }


@router.post("/snipe")
async def snipe(request: SnipeRequest, mode: str = "normal"):
    """抢单 - 快速响应机会"""
    engine = await get_engine(mode)
    result = await engine.snipe_opportunity(request.opportunity, request.urgency)
    
    return {
        "mode": mode,
        "result": result,
        "timestamp": time.time()
    }


@router.post("/execute-trade")
async def execute_trade(request: TradeRequest, mode: str = "normal"):
    """执行交易"""
    engine = await get_engine(mode)
    result = await engine.execute_trade(request.signal)
    
    return {
        "mode": mode,
        "trade": result,
        "capital": engine.capital,
        "timestamp": time.time()
    }


@router.post("/compute-schedule")
async def compute_schedule(request: ComputeScheduleRequest, mode: str = "normal"):
    """算力调度"""
    engine = await get_engine(mode)
    scheduled = await engine.schedule_compute(request.tasks)
    
    return {
        "mode": mode,
        "scheduled": scheduled,
        "total": len(scheduled),
        "allocated": sum(1 for t in scheduled if t.get("allocated")),
        "timestamp": time.time()
    }


@router.post("/resource-match")
async def resource_match(request: ResourceMatchRequest, mode: str = "normal"):
    """资源匹配"""
    engine = await get_engine(mode)
    matches = await engine.match_resources(request.tasks, request.resources)
    
    return {
        "mode": mode,
        "matches": matches,
        "total": len(matches),
        "matched": sum(1 for m in matches if m.get("matched")),
        "timestamp": time.time()
    }


@router.post("/retro")
async def run_retro(request: RetroRequest, mode: str = "normal"):
    """gstack复盘"""
    engine = await get_engine(mode)
    retro = await engine.run_retro(request.sprint)
    
    return {
        "mode": mode,
        "retro": retro,
        "timestamp": time.time()
    }


# === 状态和统计 ===

@router.get("/stats")
async def get_stats(mode: str = "normal"):
    """获取统计"""
    engine = await get_engine(mode)
    stats = engine.get_stats()
    
    return {
        "mode": mode,
        "stats": stats,
        "config": engine.config,
        "timestamp": time.time()
    }


@router.get("/config")
async def get_config(mode: str = "normal"):
    """获取配置"""
    engine = await get_engine(mode)
    
    return {
        "mode": mode,
        "config": engine.config,
        "version": engine.VERSION,
        "timestamp": time.time()
    }


@router.post("/reset")
async def reset_engine(mode: str = "normal"):
    """重置引擎"""
    global _engine_normal, _engine_expert
    if mode == "expert":
        _engine_expert = None
    else:
        _engine_normal = None
    
    return {
        "status": "reset",
        "mode": mode,
        "timestamp": time.time()
    }


# === 批量操作 ===

@router.post("/batch-snipe")
async def batch_snipe(opportunities: List[Dict], mode: str = "normal", urgency: str = "high"):
    """批量抢单"""
    engine = await get_engine(mode)
    results = []
    
    for opp in opportunities:
        result = await engine.snipe_opportunity(opp, urgency)
        results.append(result)
    
    return {
        "mode": mode,
        "results": results,
        "total": len(results),
        "success_count": sum(1 for r in results if r.get("success")),
        "timestamp": time.time()
    }


@router.post("/batch-trade")
async def batch_trade(signals: List[Dict], mode: str = "normal"):
    """批量交易"""
    engine = await get_engine(mode)
    results = []
    
    for signal in signals:
        result = await engine.execute_trade(signal)
        results.append(result)
    
    return {
        "mode": mode,
        "results": results,
        "total": len(results),
        "win_count": sum(1 for r in results if r.get("win")),
        "final_capital": engine.capital,
        "timestamp": time.time()
    }
