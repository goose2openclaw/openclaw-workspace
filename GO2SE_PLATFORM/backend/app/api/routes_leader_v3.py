"""
👑 跟大哥V3 API路由
======================
2026-04-04
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import asyncio
import time

router = APIRouter(prefix="/api/leader/v3", tags=["跟大哥V3"])

_leader_instance = None

async def get_leader():
    global _leader_instance
    if _leader_instance is None:
        from app.core.leader_v3_strategy import LeaderV3Strategy
        _leader_instance = LeaderV3Strategy()
    return _leader_instance


class FollowRequest(BaseModel):
    top_n: int = 5
    pairs: List[str] = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]


@router.post("/scan-and-follow")
async def scan_and_follow(request: FollowRequest):
    """扫描并跟单"""
    leader = await get_leader()
    
    signals = await leader.scan_and_follow(top_n=request.top_n)
    
    return {
        "signals": [
            {
                "action": sig.action,
                "confidence": f"{sig.confidence:.1%}",
                "target_mm": sig.target_mm,
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
    leader = await get_leader()
    
    return {
        "equation": leader.get_decision_equation(),
        "weights": leader.WEIGHTS,
        "version": leader.version
    }


@router.post("/update-weights")
async def update_weights(new_weights: Dict[str, float]):
    """更新权重"""
    leader = await get_leader()
    leader.WEIGHTS.update(new_weights)
    
    return {
        "status": "updated",
        "weights": leader.WEIGHTS,
        "equation": leader.get_decision_equation()
    }


@router.get("/stats")
async def get_stats():
    """获取统计"""
    leader = await get_leader()
    stats = leader.get_stats()
    
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
