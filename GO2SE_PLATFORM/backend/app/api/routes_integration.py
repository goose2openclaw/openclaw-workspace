"""
权重更新API路由
"""

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import asyncio

router = APIRouter(prefix="/api/integration", tags=["integration"])

# 导入权重更新器
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from core.weight_updater import get_weight_updater, SkillInfo, StrategyInfo

class SkillAddRequest(BaseModel):
    name: str
    path: str
    type: str
    base_weight: float
    metrics: Dict = {}

class StrategyAddRequest(BaseModel):
    name: str
    path: str
    tool: str
    base_weight: float
    win_rate: float = 0.5
    sharpe_ratio: float = 1.0
    max_drawdown: float = 0.1
    total_trades: int = 0

class WeightUpdateRequest(BaseModel):
    skill_weights: Optional[Dict[str, float]] = None
    strategy_weights: Optional[Dict[str, float]] = None

@router.get("/summary")
async def get_summary():
    """获取集成摘要"""
    updater = get_weight_updater()
    return updater.get_registry_summary()

@router.get("/skills")
async def list_skills():
    """列出所有技能"""
    updater = get_weight_updater()
    return {
        "skills": {
            name: {
                "name": s.name,
                "type": s.type,
                "enabled": s.enabled,
                "base_weight": s.base_weight,
                "current_weight": s.current_weight,
                "last_updated": s.last_updated,
                "metrics": s.metrics
            }
            for name, s in updater.skills.items()
        }
    }

@router.get("/strategies")
async def list_strategies():
    """列出所有策略"""
    updater = get_weight_updater()
    return {
        "strategies": {
            name: {
                "name": s.name,
                "tool": s.tool,
                "enabled": s.enabled,
                "base_weight": s.base_weight,
                "current_weight": s.current_weight,
                "win_rate": s.win_rate,
                "sharpe_ratio": s.sharpe_ratio,
                "max_drawdown": s.max_drawdown,
                "total_trades": s.total_trades,
                "last_updated": s.last_updated
            }
            for name, s in updater.strategies.items()
        }
    }

@router.post("/skills")
async def add_skill(req: SkillAddRequest):
    """添加新技能"""
    updater = get_weight_updater()
    skill = SkillInfo(
        name=req.name,
        path=req.path,
        type=req.type,
        enabled=True,
        base_weight=req.base_weight,
        current_weight=req.base_weight,
        last_updated=datetime.now().isoformat(),
        metrics=req.metrics
    )
    updater.add_new_skill(req.name, skill)
    return {"status": "added", "skill": req.name}

@router.post("/strategies")
async def add_strategy(req: StrategyAddRequest):
    """添加新策略"""
    updater = get_weight_updater()
    strategy = StrategyInfo(
        name=req.name,
        path=req.path,
        tool=req.tool,
        enabled=True,
        base_weight=req.base_weight,
        current_weight=req.base_weight,
        last_updated=datetime.now().isoformat(),
        win_rate=req.win_rate,
        sharpe_ratio=req.sharpe_ratio,
        max_drawdown=req.max_drawdown,
        total_trades=req.total_trades
    )
    updater.add_new_strategy(req.name, strategy)
    return {"status": "added", "strategy": req.name}

@router.get("/weights")
async def get_current_weights():
    """获取当前权重"""
    updater = get_weight_updater()
    return updater._load_latest_weights()

@router.post("/weights/update")
async def trigger_weight_update(background_tasks: BackgroundTasks):
    """触发权重更新"""
    updater = get_weight_updater()
    
    async def run_update():
        await updater.run_update_cycle()
    
    background_tasks.add_task(run_update)
    return {"status": "update_started", "message": "权重更新已在后台运行"}

@router.get("/weights/status")
async def get_update_status():
    """获取更新状态"""
    updater = get_weight_updater()
    summary = updater.get_registry_summary()
    latest = updater._load_latest_weights()
    
    return {
        "registry": summary,
        "latest_update": latest.get("timestamp", "never"),
        "confidence": latest.get("total_confidence", 0),
        "mirofish_verification": latest.get("mirofish_verification", 0)
    }

@router.post("/weights/batch")
async def batch_update_weights(req: WeightUpdateRequest):
    """批量更新权重"""
    updater = get_weight_updater()
    
    if req.skill_weights:
        for name, weight in req.skill_weights.items():
            if name in updater.skills:
                updater.skills[name].current_weight = weight
                updater.skills[name].last_updated = datetime.now().isoformat()
    
    if req.strategy_weights:
        for name, weight in req.strategy_weights.items():
            if name in updater.strategies:
                updater.strategies[name].current_weight = weight
                updater.strategies[name].last_updated = datetime.now().isoformat()
    
    updater.save_skills()
    updater.save_strategies()
    
    return {"status": "updated"}

@router.post("/skills/{name}/enable")
async def enable_skill(name: str):
    """启用技能"""
    updater = get_weight_updater()
    if name in updater.skills:
        updater.skills[name].enabled = True
        updater.save_skills()
        return {"status": "enabled", "skill": name}
    return {"status": "error", "message": "skill not found"}

@router.post("/skills/{name}/disable")
async def disable_skill(name: str):
    """禁用技能"""
    updater = get_weight_updater()
    if name in updater.skills:
        updater.skills[name].enabled = False
        updater.save_skills()
        return {"status": "disabled", "skill": name}
    return {"status": "error", "message": "skill not found"}

@router.post("/strategies/{name}/enable")
async def enable_strategy(name: str):
    """启用策略"""
    updater = get_weight_updater()
    if name in updater.strategies:
        updater.strategies[name].enabled = True
        updater.save_strategies()
        return {"status": "enabled", "strategy": name}
    return {"status": "error", "message": "strategy not found"}

@router.post("/strategies/{name}/disable")
async def disable_strategy(name: str):
    """禁用策略"""
    updater = get_weight_updater()
    if name in updater.strategies:
        updater.strategies[name].enabled = False
        updater.save_strategies()
        return {"status": "disabled", "strategy": name}
    return {"status": "error", "message": "strategy not found"}

@router.get("/external-stats")
async def fetch_external_stats():
    """抓取外部统计数据"""
    updater = get_weight_updater()
    stats = await updater.fetch_external_win_rates()
    return {"external_stats": stats, "timestamp": datetime.now().isoformat()}
