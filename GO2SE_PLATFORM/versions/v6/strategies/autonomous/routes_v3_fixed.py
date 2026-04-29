#!/usr/bin/env python3
"""GO2SE 自主系统 API v3.0"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import APIRouter
from typing import Optional
from dataclasses import asdict

router = APIRouter(prefix="/api/autonomous/v3", tags=["自主系统v3"])

# Brain
from brain.autonomous_brain import get_brain, decide as brain_decide, switch_brain as brain_switch, switch_agent as agent_switch, self_improve as brain_improve, get_stats as brain_stats

# Scheduler
from agents.scheduler import get_scheduler, schedule as do_schedule, get_stats as scheduler_stats, auto_optimize

# Learner
from learning.self_learner import get_learner, learn, predict, iterate as do_iterate, get_stats as learner_stats, export_knowledge

# Upgrade Engine
try:
    from upgrade_engine import run_full_upgrade, get_status as get_upgrade_status, add_upgrade_task
except:
    def run_full_upgrade(): return {"status": "unavailable"}
    def get_upgrade_status(): return {"status": "unavailable"}
    def add_upgrade_task(c, s, p): return {"task_id": "none"}

# ─── Brain ───────────────────────────────────────────────────
@router.get("/brain/decide")
def api_brain_decide(mi: float=0.65, change_24h: float=0, rsi: float=50, velocity: float=0, depth: float=0, sentiment: float=0.5):
    return brain_decide({"mi": mi, "change_24h": change_24h, "rsi": rsi, "velocity": velocity, "depth": depth, "sentiment": sentiment})

@router.get("/brain/switch")
def api_brain_switch(mode: Optional[str]=None): return brain_switch(mode)

@router.get("/brain/switch/agent")
def api_agent_switch(agent: Optional[str]=None): return agent_switch(agent)

@router.get("/brain/improve")
def api_brain_improve(): return brain_improve()

@router.get("/brain/stats")
def api_brain_stats(): return brain_stats()

# ─── Scheduler ────────────────────────────────────────────────
@router.get("/schedule")
def api_schedule(mi: float=0.65, change_24h: float=0, rsi: float=50):
    return do_schedule(mi, {"mi": mi, "change_24h": change_24h, "rsi": rsi})

@router.get("/schedule/stats")
def api_scheduler_stats(): return scheduler_stats()

@router.get("/schedule/optimize")
def api_schedule_optimize(): return auto_optimize()

# ─── Learner ─────────────────────────────────────────────────
@router.get("/learn")
def api_learn(mi: float=0.65, change_24h: float=0, prediction: str="HOLD", actual: str="HOLD"):
    return learn({"mi": mi, "change_24h": change_24h}, prediction, actual)

@router.get("/predict")
def api_predict(mi: float=0.65, change_24h: float=0, rsi: float=50):
    return predict({"mi": mi, "change_24h": change_24h, "rsi": rsi})

@router.get("/iterate")
def api_iterate(): return do_iterate()

@router.get("/learn/stats")
def api_learner_stats(): return learner_stats()

@router.get("/knowledge/export")
def api_export_knowledge(): return export_knowledge()

# ─── Upgrade Engine ─────────────────────────────────────────
@router.get("/upgrade/full/cycle")
def api_upgrade_full_cycle(): return run_full_upgrade()

@router.get("/upgrade/status")
def api_upgrade_status(): return get_upgrade_status()

@router.get("/upgrade/task")
def api_add_task(component: str="", skill: str="", priority: str="medium"):
    return {"success": True, "task": asdict(add_upgrade_task(component, skill, priority))}

# ─── Status ─────────────────────────────────────────────────
@router.get("/status")
def api_status():
    return {"version": "3.0.0", "brain": brain_stats(), "scheduler": scheduler_stats(), "learner": learner_stats(), "upgrade": get_upgrade_status()}

@router.get("/full/cycle")
def api_full_cycle(mi: float=0.65, change_24h: float=0, rsi: float=50):
    m = {"mi": mi, "change_24h": change_24h, "rsi": rsi}
    return {"input": m, "prediction": predict(m), "brain_decision": brain_decide(m), "schedule": do_schedule(mi, m), "recommendations": brain_improve().get("recommendations", [])}
