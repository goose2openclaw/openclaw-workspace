#!/usr/bin/env python3
"""
🪿 GO2SE 投资组合API路由
========================
动态仓位管理 + 策略蒸馏
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import json

from app.core.portfolio.dynamic_allocator import position_manager, DynamicPositionManager
from app.core.portfolio.strategy_distiller import distiller, StrategyDistiller

router = APIRouter(prefix="/api/v7/portfolio", tags=["V7投资组合"])

# ─────────────────────────────────────────────────────────────────────────────
# 动态仓位管理 API
# ─────────────────────────────────────────────────────────────────────────────

class PerformanceData(BaseModel):
    """工具表现数据"""
    recent_returns: List[float] = []
    win_rate: float = 0.5
    trend_scores: List[float] = []
    signal_strength: float = 0.5


class ToolPerformanceRequest(BaseModel):
    """工具表现请求"""
    rabbit: Optional[PerformanceData] = None
    mole: Optional[PerformanceData] = None
    oracle: Optional[PerformanceData] = None
    leader: Optional[PerformanceData] = None
    hitchhiker: Optional[PerformanceData] = None
    wool: Optional[PerformanceData] = None
    poor: Optional[PerformanceData] = None


@router.get("/weights")
async def get_weights():
    """获取当前仓位权重"""
    return {
        "data": position_manager.get_dashboard_data(),
        "timestamp": datetime.now().isoformat()
    }


@router.get("/weights/{tool_id}")
async def get_tool_weight(tool_id: str):
    """获取单个工具权重"""
    if tool_id not in position_manager.current_weights:
        raise HTTPException(status_code=404, detail="工具不存在")
    
    return {
        "data": {
            "tool_id": tool_id,
            "name": position_manager.tool_names.get(tool_id, tool_id),
            "emoji": position_manager.tool_emojis.get(tool_id, "❓"),
            "current_weight": position_manager.current_weights.get(tool_id, 0),
            "base_weight": position_manager.base_weights.get(tool_id, {}).get("weight", 0),
            "min_weight": position_manager.base_weights.get(tool_id, {}).get("min", 0),
            "max_weight": position_manager.base_weights.get(tool_id, {}).get("max", 0),
        },
        "timestamp": datetime.now().isoformat()
    }


@router.put("/weights/{tool_id}")
async def update_tool_weight(tool_id: str, weight: float):
    """手动调整工具权重"""
    if tool_id not in position_manager.current_weights:
        raise HTTPException(status_code=404, detail="工具不存在")
    
    base = position_manager.base_weights.get(tool_id, {})
    min_w = base.get("min", 0)
    max_w = base.get("max", 1)
    
    if weight < min_w or weight > max_w:
        raise HTTPException(
            status_code=400, 
            detail=f"权重必须在 {min_w:.0%} - {max_w:.0%} 之间"
        )
    
    old_weight = position_manager.current_weights[tool_id]
    position_manager.current_weights[tool_id] = weight
    
    return {
        "message": "权重已更新",
        "tool_id": tool_id,
        "old_weight": old_weight,
        "new_weight": weight,
        "timestamp": datetime.now().isoformat()
    }


@router.post("/rebalance/evaluate")
async def evaluate_rebalance(data: ToolPerformanceRequest):
    """
    评估是否需要调仓
    
    根据各工具表现，自动计算目标权重并生成调仓建议
    """
    # 构建表现数据
    performances = []
    
    tool_data_map = {
        "rabbit": data.rabbit,
        "mole": data.mole,
        "oracle": data.oracle,
        "leader": data.leader,
        "hitchhiker": data.hitchhiker,
        "wool": data.wool,
        "poor": data.poor,
    }
    
    for tool_id, perf_data in tool_data_map.items():
        if perf_data:
            perf = position_manager.evaluate_tool_performance(
                tool_id,
                {
                    "recent_returns": perf_data.recent_returns,
                    "win_rate": perf_data.win_rate,
                    "trend_scores": perf_data.trend_scores,
                    "signal_strength": perf_data.signal_strength,
                }
            )
            performances.append(perf)
    
    # 获取调仓计划
    plan = position_manager.get_rebalance_plan(performances)
    
    return {
        "data": plan,
        "can_auto_execute": plan["can_execute"],
        "timestamp": datetime.now().isoformat()
    }


@router.post("/rebalance/execute")
async def execute_rebalance(data: ToolPerformanceRequest):
    """
    执行自动调仓
    
    根据表现自动调整仓位
    """
    # 构建表现数据
    performances = []
    
    tool_data_map = {
        "rabbit": data.rabbit,
        "mole": data.mole,
        "oracle": data.oracle,
        "leader": data.leader,
        "hitchhiker": data.hitchhiker,
        "wool": data.wool,
        "poor": data.poor,
    }
    
    for tool_id, perf_data in tool_data_map.items():
        if perf_data:
            perf = position_manager.evaluate_tool_performance(
                tool_id,
                {
                    "recent_returns": perf_data.recent_returns,
                    "win_rate": perf_data.win_rate,
                    "trend_scores": perf_data.trend_scores,
                    "signal_strength": perf_data.signal_strength,
                }
            )
            performances.append(perf)
    
    # 计算目标权重
    tool_scores = position_manager.calculate_target_weights(performances)
    
    # 生成调仓动作
    actions = position_manager.generate_rebalance_actions(tool_scores)
    
    # 执行
    result = position_manager.execute_rebalance(actions)
    
    return {
        "data": result,
        "executed": result["executed"],
        "total_change": f"{result['total_change']:.1%}",
        "timestamp": datetime.now().isoformat()
    }


@router.post("/rebalance/reset")
async def reset_weights():
    """
    重置为默认权重
    """
    for tool_id in position_manager.base_weights:
        position_manager.current_weights[tool_id] = position_manager.base_weights[tool_id]["weight"]
    
    return {
        "message": "权重已重置为默认值",
        "weights": position_manager.current_weights,
        "timestamp": datetime.now().isoformat()
    }


# ─────────────────────────────────────────────────────────────────────────────
# 策略蒸馏 API
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/distillation")
async def get_distillation_results():
    """
    获取所有策略蒸馏结果
    """
    results = distiller.distill_all()
    
    return {
        "data": results,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/distillation/{strategy_id}")
async def get_strategy_distillation(strategy_id: str):
    """
    获取单个策略蒸馏结果
    """
    result = distiller.distill_strategy(strategy_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="策略不存在")
    
    return {
        "data": result,
        "timestamp": datetime.now().isoformat()
    }


@router.post("/distillation/{strategy_id}/apply")
async def apply_optimal_params(strategy_id: str):
    """
    应用最优参数到策略
    """
    result = distiller.apply_optimal_params(strategy_id)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {
        "message": "最优参数已应用",
        "data": result,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/distillation/references")
async def get_strategy_references():
    """
    获取策略参考源列表
    """
    references = {
        k: {
            "platform": v.platform,
            "url": v.url,
            "author": v.author,
            "description": v.description,
            "key_params": v.key_params,
            "expected_return": v.expected_return,
            "sharpe_ratio": v.sharpe_ratio,
        }
        for k, v in distiller.strategy_references.items()
    }
    
    return {
        "data": references,
        "timestamp": datetime.now().isoformat()
    }


@router.post("/distillation/save")
async def save_distillation_results():
    """
    保存蒸馏结果到文件
    """
    output_path = distiller.save_distillation_results()
    
    return {
        "message": "蒸馏结果已保存",
        "path": output_path,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/distillation/script")
async def get_optimization_script():
    """
    获取策略优化脚本
    """
    script = distiller.generate_optimization_script()
    
    return {
        "data": {
            "script": script,
            "path": "/root/.openclaw/workspace/GO2SE_PLATFORM/scripts/strategy_optimization.sh"
        },
        "timestamp": datetime.now().isoformat()
    }
