"""
👶 穷孩子V3 API路由
======================
2026-04-04
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional, Dict
import asyncio
import time

router = APIRouter(prefix="/api/crowdsourcing/v3", tags=["穷孩子V3"])

_crowdsourcing_instance = None

async def get_crowdsourcing():
    global _crowdsourcing_instance
    if _crowdsourcing_instance is None:
        from app.core.crowdsourcing_v3_strategy import CrowdsourcingV3Strategy
        _crowdsourcing_instance = CrowdsourcingV3Strategy()
    return _crowdsourcing_instance


class ScanPlatformsRequest(BaseModel):
    pass


@router.post("/scan-platforms")
async def scan_platforms(request: ScanPlatformsRequest):
    """扫描所有平台"""
    crowdsourcing = await get_crowdsourcing()
    
    signals = await crowdsourcing.scan_platforms()
    
    return {
        "signals": [
            {
                "action": sig.action,
                "confidence": f"{sig.confidence:.1%}",
                "platform": sig.platform,
                "task_type": sig.task_type,
                "hourly_rate": f"${sig.hourly_rate:.2f}/h",
                "reasoning": sig.reasoning,
            }
            for sig in signals
        ],
        "total": len(signals),
        "timestamp": time.time()
    }


@router.get("/decision-equation")
async def get_decision_equation():
    """获取决策等式"""
    crowdsourcing = await get_crowdsourcing()
    
    return {
        "equation": crowdsourcing.get_decision_equation(),
        "weights": crowdsourcing.WEIGHTS,
        "version": crowdsourcing.version
    }


@router.post("/update-weights")
async def update_weights(new_weights: Dict[str, float]):
    """更新权重"""
    crowdsourcing = await get_crowdsourcing()
    crowdsourcing.WEIGHTS.update(new_weights)
    
    return {
        "status": "updated",
        "weights": crowdsourcing.WEIGHTS,
        "equation": crowdsourcing.get_decision_equation()
    }


@router.get("/stats")
async def get_stats():
    """获取统计"""
    crowdsourcing = await get_crowdsourcing()
    stats = crowdsourcing.get_stats()
    
    return stats


@router.get("/platforms")
async def get_platforms():
    """获取平台列表"""
    crowdsourcing = await get_crowdsourcing()
    
    return {
        "platforms": crowdsourcing.PLATFORMS,
        "total": len(crowdsourcing.PLATFORMS)
    }


@router.get("/mirofish-simulation")
async def get_mirofish_simulation():
    """运行MiroFish全向仿真"""
    from app.core.oracle_v2_with_gstack_mirofish import MirofishSimulation
    
    sim = MirofishSimulation()
    result = sim.run_full_simulation()
    
    return {
        "status": "success",
        "simulation": result,
        "recommendations": result.get("recommendations", [])
    }


@router.get("/gstack-retro")
async def get_gstack_retro():
    """获取gstack复盘"""
    from app.core.oracle_v2_with_gstack_mirofish import run_gstack_retro
    
    retro = run_gstack_retro()
    
    return {
        "sprint": retro.sprint,
        "velocity": retro.velocity,
        "bugs_fixed": retro.bugs_fixed,
        "improvements": retro.improvements,
        "next_sprint_goals": retro.next_sprint_goals,
        "team_health": f"{retro.team_health:.0%}"
    }
