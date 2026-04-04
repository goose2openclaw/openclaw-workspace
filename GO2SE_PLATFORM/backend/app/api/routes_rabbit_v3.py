"""
🐰 打兔子V3 API路由
======================
2026-04-04
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional, Dict
import asyncio
import time

router = APIRouter(prefix="/api/rabbit/v3", tags=["打兔子V3"])

_rabbit_instance = None

async def get_rabbit():
    global _rabbit_instance
    if _rabbit_instance is None:
        from app.core.rabbit_v3_strategy import RabbitV3Strategy
        _rabbit_instance = RabbitV3Strategy()
    return _rabbit_instance


class ScanCoinsRequest(BaseModel):
    top_n: int = 10


@router.post("/scan-coins")
async def scan_coins(request: ScanCoinsRequest):
    """扫描前20主流币"""
    rabbit = await get_rabbit()
    
    signals = await rabbit.scan_coins(top_n=request.top_n)
    
    return {
        "signals": [
            {
                "action": sig.action,
                "confidence": f"{sig.confidence:.1%}",
                "coin": sig.coin,
                "entry_price": f"${sig.entry_price:.2f}",
                "target_price": f"${sig.target_price:.2f}",
                "stop_loss": f"${sig.stop_loss:.2f}",
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
    rabbit = await get_rabbit()
    
    return {
        "equation": rabbit.get_decision_equation(),
        "weights": rabbit.WEIGHTS,
        "version": rabbit.version
    }


@router.post("/update-weights")
async def update_weights(new_weights: Dict[str, float]):
    """更新权重"""
    rabbit = await get_rabbit()
    rabbit.WEIGHTS.update(new_weights)
    
    return {
        "status": "updated",
        "weights": rabbit.WEIGHTS,
        "equation": rabbit.get_decision_equation()
    }


@router.get("/stats")
async def get_stats():
    """获取统计"""
    rabbit = await get_rabbit()
    stats = rabbit.get_stats()
    
    return stats


@router.get("/coins")
async def get_coins():
    """获取前20主流币列表"""
    rabbit = await get_rabbit()
    
    return {
        "coins": rabbit.MAINSTREAM_COINS,
        "total": len(rabbit.MAINSTREAM_COINS)
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
