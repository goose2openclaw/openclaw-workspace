"""
🍀 搭便车V3 API路由
======================
2026-04-04
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional, Dict
import asyncio
import time

router = APIRouter(prefix="/api/hitchhiker/v3", tags=["搭便车V3"])

_hitchhiker_instance = None

async def get_hitchhiker():
    global _hitchhiker_instance
    if _hitchhiker_instance is None:
        from app.core.hitchhiker_v3_strategy import HitchhikerV3Strategy
        _hitchhiker_instance = HitchhikerV3Strategy()
    return _hitchhiker_instance


class ScanAndCopyRequest(BaseModel):
    top_n: int = 5


@router.post("/scan-and-copy")
async def scan_and_copy(request: ScanAndCopyRequest):
    """扫描并跟单"""
    hitchhiker = await get_hitchhiker()
    
    signals = await hitchhiker.scan_and_copy(top_n=request.top_n)
    
    return {
        "signals": [
            {
                "action": sig.action,
                "confidence": f"{sig.confidence:.1%}",
                "target_trader": sig.target_trader,
                "position_size": f"{sig.position_size:.2%}",
                "expected_profit": f"{sig.expected_profit:.2f}%",
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
    hitchhiker = await get_hitchhiker()
    
    return {
        "equation": hitchhiker.get_decision_equation(),
        "weights": hitchhiker.WEIGHTS,
        "version": hitchhiker.version
    }


@router.post("/update-weights")
async def update_weights(new_weights: Dict[str, float]):
    """更新权重"""
    hitchhiker = await get_hitchhiker()
    hitchhiker.WEIGHTS.update(new_weights)
    
    return {
        "status": "updated",
        "weights": hitchhiker.WEIGHTS,
        "equation": hitchhiker.get_decision_equation()
    }


@router.get("/stats")
async def get_stats():
    """获取统计"""
    hitchhiker = await get_hitchhiker()
    stats = hitchhiker.get_stats()
    
    return stats


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
