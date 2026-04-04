"""
💰 薅羊毛V3 API路由
======================
2026-04-04
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional, Dict
import asyncio
import time

router = APIRouter(prefix="/api/airdrop/v3", tags=["薅羊毛V3"])

_airdrop_instance = None

async def get_airdrop():
    global _airdrop_instance
    if _airdrop_instance is None:
        from app.core.airdrop_v3_strategy import AirdropV3Strategy
        _airdrop_instance = AirdropV3Strategy()
    return _airdrop_instance


class ScanProtocolsRequest(BaseModel):
    min_potential: float = 100


@router.post("/scan-protocols")
async def scan_protocols(request: ScanProtocolsRequest):
    """扫描所有协议"""
    airdrop = await get_airdrop()
    
    signals = await airdrop.scan_protocols(min_potential=request.min_potential)
    
    return {
        "signals": [
            {
                "action": sig.action,
                "confidence": f"{sig.confidence:.1%}",
                "protocol": sig.protocol,
                "potential_value": f"${sig.potential_value:.2f}",
                "gas_estimate": f"${sig.gas_estimate:.2f}",
                "estimated_time": f"{sig.estimated_time:.1f}h",
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
    airdrop = await get_airdrop()
    
    return {
        "equation": airdrop.get_decision_equation(),
        "weights": airdrop.WEIGHTS,
        "version": airdrop.version
    }


@router.post("/update-weights")
async def update_weights(new_weights: Dict[str, float]):
    """更新权重"""
    airdrop = await get_airdrop()
    airdrop.WEIGHTS.update(new_weights)
    
    return {
        "status": "updated",
        "weights": airdrop.WEIGHTS,
        "equation": airdrop.get_decision_equation()
    }


@router.get("/stats")
async def get_stats():
    """获取统计"""
    airdrop = await get_airdrop()
    stats = airdrop.get_stats()
    
    return stats


@router.get("/protocols")
async def get_protocols():
    """获取协议列表"""
    airdrop = await get_airdrop()
    
    return {
        "protocols": airdrop.PROTOCOLS,
        "total": len(airdrop.PROTOCOLS)
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
