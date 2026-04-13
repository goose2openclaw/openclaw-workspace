#!/usr/bin/env python3
"""
💰 薅羊毛 & 👶 穷孩子 API路由
================================
加强版V2 - 安全机制完善
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List

router = APIRouter(prefix="/api/earn", tags=["薅羊毛+穷孩子V2"])

# ─── Request Models ─────────────────────────────────

class ExecuteAirdropRequest(BaseModel):
    task_id: str
    dry_run: bool = True

class StartCrowdTaskRequest(BaseModel):
    task_id: str

class SubmitCrowdTaskRequest(BaseModel):
    task_id: str
    work_quality: str = "normal"  # high/normal/low

# ─── 薅羊毛 Routes ──────────────────────────────────

@router.get("/airdrop/tasks")
async def list_airdrop_tasks():
    """列出可用空投任务"""
    from app.services.airdrop.airdrop_v2 import airdrop_service_v2
    await airdrop_service_v2.scan_opportunities()
    tasks = airdrop_service_v2.get_active_tasks()
    return {
        "success": True,
        "count": len(tasks),
        "tasks": tasks,
    }


@router.get("/airdrop/tasks/{task_id}")
async def get_airdrop_task(task_id: str):
    """获取单个任务详情"""
    from app.services.airdrop.airdrop_v2 import airdrop_service_v2
    await airdrop_service_v2.scan_opportunities()
    if task_id not in airdrop_service_v2.tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    t = airdrop_service_v2.tasks[task_id]
    return {
        "success": True,
        "task": {
            "id": t.id,
            "name": t.name,
            "project": t.project,
            "chain": t.chain,
            "actions": t.actions,
            "expected_return_usd": t.expected_return_usd,
            "difficulty": t.difficulty,
            "risk_level": t.risk_level.value,
            "estimated_gas_usd": t.estimated_gas_usd,
            "status": t.status.value,
            "security_flags": t.security_flags,
            "created_at": t.created_at,
        }
    }


@router.post("/airdrop/execute")
async def execute_airdrop(req: ExecuteAirdropRequest):
    """执行空投任务（默认干跑）"""
    from app.services.airdrop.airdrop_v2 import airdrop_service_v2
    await airdrop_service_v2.scan_opportunities()
    result = await airdrop_service_v2.execute_task(req.task_id, dry_run=req.dry_run)
    return {
        "success": result.success,
        "task_id": result.task_id,
        "actual_return_usd": result.actual_return,
        "tx_hash": result.tx_hash,
        "gas_spent_usd": result.gas_spent,
        "error": result.error,
        "security_check_passed": result.security_check_passed,
        "dry_run": req.dry_run,
        "timestamp": result.timestamp,
        "warning": "🚫 禁止访问授权链接！仅执行安全操作。" if req.dry_run else "⚠️ 实盘模式未启用",
    }


@router.get("/airdrop/audit/{task_id}")
async def audit_airdrop_task(task_id: str):
    """安全审计"""
    from app.services.airdrop.airdrop_v2 import airdrop_service_v2
    await airdrop_service_v2.scan_opportunities()
    report = airdrop_service_v2.security_audit(task_id)
    return {
        "success": True,
        "task_id": report.task_id,
        "risk_score": report.risk_score,
        "risk_factors": report.risk_factors,
        "auth_check_passed": report.auth_check_passed,
        "contract_check_passed": report.contract_check_passed,
        "gas_check_passed": report.gas_check_passed,
        "recommendation": report.recommendation,
        "recommendation_label": {
            "PROCEED": "✅ 可执行",
            "CAUTION": "⚠️ 谨慎执行",
            "STOP": "🚫 停止执行",
        }.get(report.recommendation, "未知"),
    }


@router.get("/airdrop/stats")
async def airdrop_stats():
    """获取空投统计"""
    from app.services.airdrop.airdrop_v2 import airdrop_service_v2
    return {
        "success": True,
        "stats": airdrop_service_v2.get_task_stats(),
    }


# ─── 穷孩子 Routes ──────────────────────────────────

@router.get("/crowd/tasks")
async def list_crowd_tasks(
    min_hourly_rate: float = Query(default=0, description="最低时薪"),
    task_type: Optional[str] = Query(default=None, description="任务类型"),
    sort_by: str = Query(default="hourly_rate", description="排序方式"),
):
    """列出可用众包任务"""
    from app.services.crowd.crowd_v2 import crowd_service_v2
    await crowd_service_v2.scan_opportunities()
    tasks = crowd_service_v2.get_available_tasks(
        min_hourly_rate=min_hourly_rate,
        task_type=task_type,
        sort_by=sort_by
    )
    return {
        "success": True,
        "count": len(tasks),
        "tasks": tasks,
    }


@router.get("/crowd/tasks/{task_id}")
async def get_crowd_task(task_id: str):
    """获取众包任务详情"""
    from app.services.crowd.crowd_v2 import crowd_service_v2
    await crowd_service_v2.scan_opportunities()
    if task_id not in crowd_service_v2.tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    t = crowd_service_v2.tasks[task_id]
    return {
        "success": True,
        "task": {
            "id": t.id,
            "name": t.name,
            "platform": t.platform,
            "task_type": t.task_type.value,
            "description": t.description,
            "reward_usd": t.reward_usd,
            "duration_min": t.duration_min,
            "difficulty": t.difficulty,
            "estimated_hourly_rate": t.estimated_hourly_rate,
            "requirements": t.requirements,
            "risk_level": t.risk_level.value,
            "status": t.status.value,
        }
    }


@router.post("/crowd/start")
async def start_crowd_task(req: StartCrowdTaskRequest):
    """开始众包任务"""
    from app.services.crowd.crowd_v2 import crowd_service_v2
    try:
        task = await crowd_service_v2.start_task(req.task_id)
        return {
            "success": True,
            "task_id": task.id,
            "name": task.name,
            "status": task.status.value,
            "started_at": task.started_at,
            "message": "🔒 资金已隔离，放心操作",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/crowd/submit")
async def submit_crowd_task(req: SubmitCrowdTaskRequest):
    """提交众包任务"""
    from app.services.crowd.crowd_v2 import crowd_service_v2
    result = await crowd_service_v2.submit_task(req.task_id, req.work_quality)
    return {
        "success": result.success,
        "task_id": result.task_id,
        "reward_usd": result.reward,
        "platform": result.platform,
        "task_type": result.task_type,
        "duration_actual_min": result.duration_actual_min,
        "hourly_rate_actual": result.hourly_rate_actual,
        "error": result.error,
        "timestamp": result.timestamp,
        "isolation_report": crowd_service_v2.get_isolation_report(req.task_id).__dict__ if result.success else None,
    }


@router.get("/crowd/isolation/{task_id}")
async def get_isolation_report(task_id: str):
    """获取隔离报告"""
    from app.services.crowd.crowd_v2 import crowd_service_v2
    try:
        report = crowd_service_v2.get_isolation_report(task_id)
        return {
            "success": True,
            "task_id": report.task_id,
            "wallet_isolated": report.wallet_isolated,
            "no_private_key_used": report.no_private_key_used,
            "platform_verified": report.platform_verified,
            "payment_method_safe": report.payment_method_safe,
            "overall_safe": report.overall_safe,
            "message": "✅ 全程隔离，安全有保障" if report.overall_safe else "⚠️ 存在风险",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/crowd/platforms")
async def crowd_platforms():
    """获取平台信誉统计"""
    from app.services.crowd.crowd_v2 import crowd_service_v2
    return {
        "success": True,
        "platforms": crowd_service_v2.get_platform_stats(),
    }


@router.get("/crowd/stats")
async def crowd_stats():
    """获取众包统计"""
    from app.services.crowd.crowd_v2 import crowd_service_v2
    return {
        "success": True,
        "stats": crowd_service_v2.get_task_stats(),
    }


# ─── 综合 Routes ──────────────────────────────────

@router.get("/summary")
async def earn_summary():
    """获取薅羊毛+穷孩子综合概览"""
    from app.services.airdrop.airdrop_v2 import airdrop_service_v2
    from app.services.crowd.crowd_v2 import crowd_service_v2

    airdrop_stats = airdrop_service_v2.get_task_stats()
    crowd_stats = crowd_service_v2.get_task_stats()

    total_earned = airdrop_stats["total_earned_usd"] + crowd_stats["total_earned_usd"]
    total_gas = airdrop_stats["total_gas_spent_usd"]
    net_profit = total_earned - total_gas

    return {
        "success": True,
        "summary": {
            "total_earned_usd": round(total_earned, 2),
            "total_gas_spent_usd": round(total_gas, 2),
            "net_profit_usd": round(net_profit, 2),
            "airdrop": {
                "completed": airdrop_stats["completed"],
                "suspended": airdrop_stats["suspended"],
                "security_flags": airdrop_stats["security_flags"],
            },
            "crowd": {
                "completed": crowd_stats["completed"],
                "in_progress": crowd_stats["in_progress"],
                "daily_earned": crowd_stats["daily_earned_usd"],
                "daily_remaining": crowd_stats["daily_remaining_usd"],
            },
            "isolation_active": True,
            "message": "🔒 所有操作完全隔离，保障本金安全",
        }
    }


@router.get("/security-rules")
async def security_rules():
    """获取安全规则说明"""
    from app.services.airdrop.airdrop_v2 import FORBIDDEN_PATTERNS, SAFE_ACTIONS, GAS_CONFIG
    from app.services.crowd.crowd_v2 import ISOLATION_CONFIG, PLATFORM_REPUTATION

    return {
        "success": True,
        "airdrop_rules": {
            "🚫_forbidden_patterns": FORBIDDEN_PATTERNS,
            "✅_safe_actions": list(SAFE_ACTIONS),
            "⛽_gas_config": GAS_CONFIG,
            "description": "空投猎手安全规则：禁止授权操作，仅执行白名单操作",
        },
        "crowd_rules": {
            "🔒_isolation_config": ISOLATION_CONFIG,
            "📊_min_platform_reputation": 70,
            "description": "众包赚钱隔离规则：完全隔离，无需私钥，平台信誉验证",
        },
    }
