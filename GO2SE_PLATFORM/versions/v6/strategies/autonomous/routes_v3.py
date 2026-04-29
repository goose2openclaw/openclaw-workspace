#!/usr/bin/env python3
"""GO2SE 自主系统 API v4.0 + Hermes"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import APIRouter
from typing import Optional

router = APIRouter(prefix="/api/autonomous/v4", tags=["自主系统v4+Hermes"])

# Brain
try:
    from brain.autonomous_brain import get_brain, decide as brain_decide, switch_brain as brain_switch, switch_agent as agent_switch, self_improve as brain_improve, get_stats as brain_stats
    BRAIN_AVAILABLE = True
except:
    BRAIN_AVAILABLE = False
    def get_brain(): return {}
    def brain_decide(x): return {}
    def brain_switch(x): return {}
    def agent_switch(x): return {}
    def brain_improve(): return {}
    def brain_stats(): return {}

# Scheduler
try:
    from agents.scheduler import get_scheduler, schedule as do_schedule, get_stats as scheduler_stats, auto_optimize
    SCHEDULER_AVAILABLE = True
except:
    SCHEDULER_AVAILABLE = False
    def get_scheduler(): return {}
    def do_schedule(x,y): return {}
    def scheduler_stats(): return {}
    def auto_optimize(): return {}

# Learner
try:
    from learning.self_learner import get_learner, learn, predict, iterate as do_iterate, get_stats as learner_stats, export_knowledge
    LEARNER_AVAILABLE = True
except:
    LEARNER_AVAILABLE = False
    def get_learner(): return {}
    def learn(x): return {}
    def predict(x): return {}
    def do_iterate(): return {}
    def learner_stats(): return {}
    def export_knowledge(): return {}

# Self-Driving Engine v4.0
from upgrade_engine import run_self_driven_cycle, get_engine_status, enable_engine, disable_engine

# Hermes Integration
try:
    from hermes_go2se import activate as hermes_activate, enable as hermes_enable, learn as hermes_learn, get_status as hermes_status
    HERMES_AVAILABLE = True
except Exception as e:
    HERMES_AVAILABLE = False
    print(f"Hermes not available: {e}")

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

# ─── Self-Driving Engine v4.0 ─────────────────────────────────
@router.get("/self-driven/cycle")
def api_self_driven_cycle(mi: float=0.65, volatility: float=0.5):
    return run_self_driven_cycle({"mi": mi, "volatility": volatility})

@router.get("/self-driven/status")
def api_engine_status(): return get_engine_status()

@router.get("/self-driven/enable")
def api_enable(): return enable_engine()

@router.get("/self-driven/disable")
def api_disable(): return disable_engine()

# ─── Hermes Integration ───────────────────────────────────────
@router.get("/hermes/activate")
def api_hermes_activate():
    if not HERMES_AVAILABLE:
        return {"error": "Hermes not available", "available": False}
    result = hermes_activate()
    return {"status": "activated", "available": True, **result}

@router.get("/hermes/enable")
def api_hermes_enable():
    if not HERMES_AVAILABLE:
        return {"error": "Hermes not available", "available": False}
    return hermes_enable()

@router.post("/hermes/learn")
def api_hermes_learn():
    if not HERMES_AVAILABLE:
        return {"error": "Hermes not available"}
    return hermes_learn({"type": "manual", "timestamp": "now"})

@router.get("/hermes/status")
def api_hermes_status():
    if not HERMES_AVAILABLE:
        return {"available": False, "error": "not loaded"}
    status = hermes_status()
    return {"available": True, **status}

# ─── Work ─────────────────────────────────────────────────
@router.get("/work/scan")
def api_work_scan():
    from upgrade_engine import engine
    opps = engine.work.scan()
    return {"opportunities": len(opps), "status": engine.work.get_status()}

@router.get("/work/optimize")
def api_work_optimize(platform: str="wool"):
    from upgrade_engine import engine
    return engine.work.optimize_platform(platform)

# ─── Resource ──────────────────────────────────────────────
@router.get("/resource/optimize")
def api_resource_optimize(mi: float=0.65, volatility: float=0.5):
    from upgrade_engine import engine
    return engine.resource.optimize({"mi": mi, "volatility": volatility})

# ─── Status ─────────────────────────────────────────────────
@router.get("/status")
def api_status():
    return {
        "version": "4.0-Hermes",
        "brain": brain_stats(),
        "scheduler": scheduler_stats(),
        "learner": learner_stats(),
        "self_driving": get_engine_status(),
        "hermes": hermes_status() if HERMES_AVAILABLE else {"available": False}
    }
