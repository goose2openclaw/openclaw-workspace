"""
Factor Degradation API Routes
==============================
因子退化检测 + 公开策略对比蒸馏
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from datetime import datetime

router = APIRouter(prefix="/api/factor", tags=["因子退化检测"])


# ── Pydantic Models ─────────────────────────────────────────────

class FactorScoreUpdate(BaseModel):
    factor_name: str
    score: float
    category: str = "unknown"


class StrategyMetrics(BaseModel):
    strategy_name: str
    tool: str
    win_rate: float
    return_pct: float
    sharpe_ratio: float


# ── 导入检测器 ─────────────────────────────────────────────

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.ml_core.factor_degradation import FactorDegradationDetector, _detector
except ImportError:
    _detector = None


# ── API Routes ─────────────────────────────────────────────────

@router.get("/status")
async def get_status():
    """获取因子退化检测状态"""
    if _detector is None:
        return {"status": "unavailable", "message": "Factor detector not initialized"}
    return {
        "status": "operational",
        "degradation_threshold": _detector.degradation_threshold,
        "critical_threshold": _detector.critical_threshold,
        "total_factors": len(_detector.factors),
        "last_check": _detector.last_check,
    }


@router.post("/update")
async def update_factor_score(body: FactorScoreUpdate):
    """
    更新因子评分
    POST /api/factor/update
    """
    if _detector is None:
        raise HTTPException(status_code=503, detail="检测器未初始化")

    result = _detector.update_factor_score(body.factor_name, body.score)
    return {
        "factor_name": result.factor_name,
        "current_score": result.current_score,
        "historical_avg": result.historical_avg,
        "degradation_pct": result.degradation_pct,
        "severity": result.severity,
        "trend": result.trend,
        "recommendation": result.recommendation,
        "action_required": result.action_required,
    }


@router.get("/check/all")
async def check_all_factors():
    """
    检查所有因子
    GET /api/factor/check/all
    """
    if _detector is None:
        raise HTTPException(status_code=503, detail="检测器未初始化")

    result = _detector.check_all_factors()
    return result


@router.get("/report")
async def get_factor_report():
    """
    获取因子健康报告
    GET /api/factor/report
    """
    if _detector is None:
        raise HTTPException(status_code=503, detail="检测器未初始化")

    report = _detector.get_factor_report()
    return report


@router.get("/degraded")
async def get_degraded_factors():
    """
    获取退化的因子列表
    GET /api/factor/degraded
    """
    if _detector is None:
        raise HTTPException(status_code=503, detail="检测器未初始化")

    degraded = [
        {
            "name": name,
            "score": f.current_score,
            "degradation_pct": f.degradation_pct,
            "category": f.category,
        }
        for name, f in _detector.factors.items()
        if f.is_degraded
    ]
    return {"degraded_factors": degraded, "count": len(degraded)}


@router.post("/compare")
async def compare_with_public(
    our_strategy: str,
    tool: str,
    win_rate: float,
    return_pct: float,
    sharpe_ratio: float,
):
    """
    与公开策略对比
    POST /api/factor/compare
    """
    if _detector is None:
        raise HTTPException(status_code=503, detail="检测器未初始化")

    metrics = {
        "win_rate": win_rate,
        "return": return_pct,
        "sharpe": sharpe_ratio,
    }
    result = _detector.compare_with_public_strategies(our_strategy, tool, metrics)
    return {
        "our_strategy": result.our_strategy,
        "reference_platform": result.reference_platform,
        "reference_strategy": result.reference_strategy,
        "our_win_rate": result.our_win_rate,
        "their_win_rate": result.their_win_rate,
        "our_return": result.our_return,
        "their_return": result.their_return,
        "our_sharpe": result.our_sharpe,
        "their_sharpe": result.their_sharpe,
        "gap_pct": result.gap,
        "verdict": result.verdict,
        "distillation_needed": result.distillation_needed,
        "suggested_params": result.suggested_params,
    }


@router.post("/distill")
async def trigger_distillation(
    strategy_metrics: List[StrategyMetrics],
):
    """
    批量对比并触发蒸馏
    POST /api/factor/distill
    """
    if _detector is None:
        raise HTTPException(status_code=503, detail="检测器未初始化")

    comparisons = []
    for sm in strategy_metrics:
        metrics = {
            "win_rate": sm.win_rate,
            "return": sm.return_pct,
            "sharpe": sm.sharpe_ratio,
        }
        comp = _detector.compare_with_public_strategies(
            sm.strategy_name, sm.tool, metrics
        )
        comparisons.append(comp)

    trigger_result = _detector.auto_distillation_trigger(comparisons)

    return {
        "comparisons": [
            {
                "strategy": c.our_strategy,
                "verdict": c.verdict,
                "gap_pct": c.gap,
                "distillation_needed": c.distillation_needed,
            }
            for c in comparisons
        ],
        "distillation_trigger": trigger_result,
    }


@router.get("/trackers")
async def get_public_trackers():
    """
    获取公开策略追踪来源
    GET /api/factor/trackers
    """
    from app.ml_core.factor_degradation import PUBLIC_STRATEGY_TRACKERS
    return {
        "trackers": PUBLIC_STRATEGY_TRACKERS,
        "count": len(PUBLIC_STRATEGY_TRACKERS),
    }
