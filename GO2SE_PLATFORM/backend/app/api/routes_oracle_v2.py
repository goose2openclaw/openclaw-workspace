"""
🔮 走着瞧V2 API路由
======================
2026-04-04
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import asyncio
import time

router = APIRouter(prefix="/api/oracle/v2", tags=["走着瞧V2"])

# 全局实例
_oracle_instance = None

async def get_oracle():
    global _oracle_instance
    if _oracle_instance is None:
        from app.core.oracle_v2_strategy import OracleV2Strategy
        _oracle_instance = OracleV2Strategy()
    return _oracle_instance


class PredictionRequest(BaseModel):
    symbol: str = "BTC"
    price_history: Optional[List[float]] = None


class BatchPredictionRequest(BaseModel):
    symbols: List[str] = ["BTC", "ETH", "SOL"]


@router.post("/predict")
async def predict(request: PredictionRequest):
    """获取单个币种预测"""
    oracle = await get_oracle()
    
    signal = await oracle.predict(request.symbol, request.price_history)
    
    return {
        "symbol": request.symbol,
        "action": signal.action.upper(),
        "confidence": f"{signal.confidence:.1%}",
        "price_target": f"${signal.price_target:,.2f}" if signal.price_target else 0,
        "reasoning": signal.reasoning,
        "sources": {
            k: f"{v:.1%}" for k, v in signal.sources.items()
        },
        "timestamp": signal.timestamp
    }


@router.post("/batch-predict")
async def batch_predict(request: BatchPredictionRequest):
    """批量预测"""
    oracle = await get_oracle()
    
    signals = await oracle.batch_predict(request.symbols)
    
    return {
        "predictions": [
            {
                "symbol": sig.action,
                "action": sig.action.upper(),
                "confidence": f"{sig.confidence:.1%}",
            }
            for sig in signals
        ],
        "total": len(signals),
        "timestamp": time.time()
    }


@router.get("/decision-equation")
async def get_decision_equation():
    """获取决策等式"""
    oracle = await get_oracle()
    
    return {
        "equation": oracle.get_decision_equation(),
        "weights": oracle.WEIGHTS,
        "version": oracle.version
    }


@router.post("/update-weights")
async def update_weights(new_weights: Dict[str, float]):
    """更新决策等式权重"""
    oracle = await get_oracle()
    
    oracle.update_weights(new_weights)
    
    return {
        "status": "updated",
        "weights": oracle.WEIGHTS,
        "equation": oracle.get_decision_equation()
    }


@router.get("/stats")
async def get_stats():
    """获取走着瞧统计"""
    oracle = await get_oracle()
    stats = oracle.get_stats()
    
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
    """获取gstack复盘结果"""
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


@router.get("/complete-report")
async def get_complete_report():
    """获取完整报告"""
    from app.core.oracle_v2_with_gstack_mirofish import create_oracle_v2_complete
    
    oracle = create_oracle_v2_complete()
    report = oracle.get_report()
    
    return report
