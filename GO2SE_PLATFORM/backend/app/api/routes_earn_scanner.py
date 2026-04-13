#!/usr/bin/env python3
"""
💰 薅羊毛 & 👶 穷孩子 V3 - 找单·选品·抢单 API
============================================
增强版路由：多因子评分 + 智能排序 + 并发抢单
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List

router = APIRouter(prefix="/api/earn/v3", tags=["薅羊毛+穷孩子V3-找单抢单"])


# ─── Request Models ────────────────────────────────

class GrabRequest(BaseModel):
    task_id: str

class BatchGrabRequest(BaseModel):
    task_ids: List[str]
    max_parallel: int = Field(default=3, ge=1, le=10)


# ═══════════════════════════════════════════════════════
# 💰 薅羊毛 V3 - 空投找单抢单
# ═══════════════════════════════════════════════════════

@router.get("/airdrop/scan")
async def scan_airdrop():
    """🔍 全源扫描空投任务"""
    from app.services.airdrop.scanner_v2 import scanner_v2
    tasks = await scanner_v2.scan_all()
    stats = scanner_v2.get_scanner_stats()
    return {
        "success": True,
        "found": len(tasks),
        "stats": stats,
        "tasks": tasks,
    }


@router.get("/airdrop/top")
async def top_airdrop_tasks(limit: int = Query(default=5, le=20)):
    """🏆 获取最优空投任务（多因子评分）"""
    from app.services.airdrop.scanner_v2 import scanner_v2
    await scanner_v2.scan_all()
    top = scanner_v2.get_top_tasks(limit=limit, min_score=30)
    return {
        "success": True,
        "count": len(top),
        "tasks": top,
        "message": "按综合评分排序：收益+速度+可靠性+效率"
    }


@router.post("/airdrop/grab")
async def grab_airdrop(req: GrabRequest):
    """⚡ 抢空投任务"""
    from app.services.airdrop.scanner_v2 import scanner_v2
    await scanner_v2.scan_all()
    ok, msg = await scanner_v2.grab_task(req.task_id)
    if ok:
        task = scanner_v2.tasks.get(req.task_id, {})
        return {
            "success": True,
            "grabbed": True,
            "task_id": req.task_id,
            "name": task.get("name"),
            "remaining_slots": task.get("remaining_slots"),
            "message": f"✅ 抢单成功！剩余名额: {task.get('remaining_slots')}",
        }
    else:
        return {
            "success": False,
            "grabbed": False,
            "task_id": req.task_id,
            "message": f"❌ 抢单失败: {msg}",
        }


@router.post("/airdrop/batch-grab")
async def batch_grab_airdrop(task_ids: List[str], max_parallel: int = Query(default=5, le=10)):
    """⚡⚡⚡ 批量并发抢空投"""
    from app.services.airdrop.scanner_v2 import scanner_v2
    await scanner_v2.scan_all()

    semaphore = __import__("asyncio").Semaphore(max_parallel)
    import asyncio

    async def grab_one(tid):
        async with semaphore:
            ok, msg = await scanner_v2.grab_task(tid)
            return {"task_id": tid, "success": ok, "message": msg}

    results = await asyncio.gather(*[grab_one(tid) for tid in task_ids])

    success = sum(1 for r in results if r["success"])
    return {
        "success": True,
        "total": len(results),
        "grabbed": success,
        "failed": len(results) - success,
        "results": list(results),
        "message": f"⚡ 批量抢单完成: {success}/{len(results)} 成功",
    }


@router.get("/airdrop/scores")
async def score_all_airdrop():
    """📊 所有空投任务评分"""
    from app.services.airdrop.scanner_v2 import scanner_v2
    await scanner_v2.scan_all()
    scores = scanner_v2.score_all()
    return {
        "success": True,
        "count": len(scores),
        "scores": [
            {
                "task_id": s.task_id,
                "total_score": s.total_score,
                "return_score": s.return_score,
                "speed_score": s.speed_score,
                "reliability_score": s.reliability_score,
                "efficiency_score": s.efficiency_score,
                "priority": s.priority.value if hasattr(s.priority, 'value') else s.priority,
                "recommendation": s.recommendation,
            }
            for s in scores[:20]
        ],
    }


@router.get("/airdrop/stats-v3")
async def airdrop_stats_v3():
    """📈 空投扫描统计"""
    from app.services.airdrop.scanner_v2 import scanner_v2
    stats = scanner_v2.get_scanner_stats()
    return {"success": True, "stats": stats}


# ═══════════════════════════════════════════════════════
# 👶 穷孩子 V3 - 众包找单抢单
# ═══════════════════════════════════════════════════════

@router.get("/crowd/scan")
async def scan_crowd():
    """🔍 全平台扫描众包任务"""
    from app.services.crowd.scanner_v2 import crowd_scanner_v2
    tasks = await crowd_scanner_v2.scan_all()
    stats = crowd_scanner_v2.get_scanner_stats()
    return {
        "success": True,
        "found": len(tasks),
        "stats": stats,
        "tasks": tasks,
    }


@router.get("/crowd/top")
async def top_crowd_tasks(limit: int = Query(default=5, le=20)):
    """🏆 获取最优众包任务（时薪+可靠性双排序）"""
    from app.services.crowd.scanner_v2 import crowd_scanner_v2
    await crowd_scanner_v2.scan_all()
    top = crowd_scanner_v2.get_top_tasks(limit=limit, min_score=30)
    return {
        "success": True,
        "count": len(top),
        "tasks": top,
        "message": "按综合评分排序：时薪+可靠性+速度+可用性"
    }


@router.post("/crowd/grab")
async def grab_crowd(req: GrabRequest):
    """⚡ 抢众包任务"""
    from app.services.crowd.scanner_v2 import crowd_scanner_v2
    await crowd_scanner_v2.scan_all()
    ok, msg = await crowd_scanner_v2.grab_task(req.task_id)
    if ok:
        task = crowd_scanner_v2.tasks.get(req.task_id, {})
        return {
            "success": True,
            "grabbed": True,
            "task_id": req.task_id,
            "name": task.get("name"),
            "remaining_slots": task.get("remaining_slots"),
            "message": f"✅ 抢单成功！剩余名额: {task.get('remaining_slots')}",
        }
    else:
        return {
            "success": False,
            "grabbed": False,
            "task_id": req.task_id,
            "message": f"❌ 抢单失败: {msg}",
        }


@router.post("/crowd/batch-grab")
async def batch_grab_crowd(req: BatchGrabRequest):
    """⚡⚡⚡ 批量并发抢众包"""
    from app.services.crowd.scanner_v2 import crowd_scanner_v2
    await crowd_scanner_v2.scan_all()
    results = await crowd_scanner_v2.batch_grab(req.task_ids, req.max_parallel)
    success = sum(1 for r in results if r["success"])
    return {
        "success": True,
        "total": len(results),
        "grabbed": success,
        "failed": len(results) - success,
        "results": list(results),
        "message": f"⚡ 批量抢单完成: {success}/{len(results)} 成功",
    }


@router.get("/crowd/scores")
async def score_all_crowd():
    """📊 所有众包任务评分"""
    from app.services.crowd.scanner_v2 import crowd_scanner_v2
    await crowd_scanner_v2.scan_all()
    scores = crowd_scanner_v2.score_all()
    return {
        "success": True,
        "count": len(scores),
        "scores": [
            {
                "task_id": s.task_id,
                "total_score": s.total_score,
                "hourly_rate_score": s.hourly_rate_score,
                "reliability_score": s.reliability_score,
                "speed_score": s.speed_score,
                "availability_score": s.availability_score,
                "priority": s.priority,
            }
            for s in scores[:20]
        ],
    }


@router.get("/crowd/stats-v3")
async def crowd_stats_v3():
    """📈 众包扫描统计"""
    from app.services.crowd.scanner_v2 import crowd_scanner_v2
    stats = crowd_scanner_v2.get_scanner_stats()
    return {"success": True, "stats": stats}


# ═══════════════════════════════════════════════════════
# 📊 综合对比
# ═══════════════════════════════════════════════════════

@router.get("/compare")
async def compare_earn():
    """📊 薅羊毛 vs 穷孩子 综合对比"""
    from app.services.airdrop.scanner_v2 import scanner_v2
    from app.services.crowd.scanner_v2 import crowd_scanner_v2

    await scanner_v2.scan_all()
    await crowd_scanner_v2.scan_all()

    airdrop_stats = scanner_v2.get_scanner_stats()
    crowd_stats = crowd_scanner_v2.get_scanner_stats()
    airdrop_top = scanner_v2.get_top_tasks(limit=3, min_score=30)
    crowd_top = crowd_scanner_v2.get_top_tasks(limit=3, min_score=30)

    return {
        "success": True,
        "compare": {
            "airdrop": {
                "total_tasks": airdrop_stats["total_tasks"],
                "p0_tasks": airdrop_stats["p0_count"],
                "p1_tasks": airdrop_stats["p1_count"],
                "total_expected_usd": airdrop_stats["total_expected_usd"],
                "net_potential_usd": airdrop_stats["net_potential_usd"],
                "top_3": airdrop_top,
            },
            "crowd": {
                "total_tasks": crowd_stats["total_tasks"],
                "hot_tasks": crowd_stats["hot_count"],
                "total_reward_usd": crowd_stats["total_reward_usd"],
                "avg_hourly_rate": crowd_stats["avg_hourly_rate"],
                "top_3": crowd_top,
            },
            "recommendation": {
                "if_time_short": "优先做众包(快速结算)",
                "if_time_long": "优先做空投(高收益)",
                "optimal_mix": "空投70% + 众包30%",
            }
        }
    }
