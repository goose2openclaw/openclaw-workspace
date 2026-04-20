"""
BRAIN COORDINATOR API SERVER
FastAPI 服务 - 提供 REST API 访问协调器
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import asyncio
from brain_coordinator import BrainCoordinator, BrainSignal, SwitchResult, SwitchDecision

app = FastAPI(title="Brain Coordinator API", version="1.0.0")

coordinator = BrainCoordinator(mode="AUTO")

coord_state: Dict = {
    "mode": "AUTO",
    "history": [],
    "auto_polls": [],
    "last_switch": None,
}

class AnalyzeRequest(BaseModel):
    symbol: str = "BTCUSDT"
    regime: str = "bull"
    rsi: float = 55.0
    confidence_override: Optional[float] = None

class SwitchRequest(BaseModel):
    target: str  # "hermes" | "lobster" | "quad"
    reason: Optional[str] = None

class ModeRequest(BaseModel):
    mode: str  # "AUTO" | "SEMI" | "MANUAL"

@app.get("/")
def root():
    return {
        "name": "Brain Coordinator API",
        "version": "1.0.0",
        "description": "左右脑 + Lobster/Hermes 自主切换协调器",
        "endpoints": [
            "GET  /status          - 协调器状态",
            "POST /analyze         - 触发一次决策分析",
            "POST /switch          - 手动切换引擎",
            "GET  /history         - 历史决策记录",
            "GET  /brains          - 三脑实时信号",
            "PUT  /mode            - 更改协调模式",
        ]
    }

@app.get("/status")
def get_status():
    """获取协调器当前状态"""
    s = coordinator.get_status()
    s["decision_labels"] = {
        "hermes": "🦐 Hermes专家 (v6i)",
        "lobster": "🦞 Lobster普通 (vv6)",
        "quad": "🧠 Quad四脑仲裁 (v15)",
        "hold": "⏸️ 保持当前",
    }
    return s

@app.get("/brains")
async def get_brains():
    """并行获取三脑实时信号"""
    hermes, lobster, quad = await asyncio.gather(
        coordinator.fetch_signal("hermes", "BTCUSDT"),
        coordinator.fetch_signal("lobster", "BTCUSDT"),
        coordinator.fetch_quad_signal("BTCUSDT"),
    )
    return {
        "hermes": hermes.__dict__ if hermes else None,
        "lobster": lobster.__dict__ if lobster else None,
        "quad": quad.__dict__ if quad else None,
        "timestamp": coordinator.get_status()["current_brain"],
    }

@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    """触发一次完整决策分析"""
    result = await coordinator.run_cycle(req.symbol)
    return {
        "decision": result.decision.value,
        "recommended_brain": result.recommended_brain,
        "active_engine": result.active_engine,
        "confidence_diff": result.confidence_diff,
        "reasoning": result.reasoning,
        "hermes": result.hermes_signal.__dict__ if result.hermes_signal else None,
        "lobster": result.lobster_signal.__dict__ if result.lobster_signal else None,
        "quad": result.quad_signal.__dict__ if result.quad_signal else None,
        "timestamp": result.timestamp,
    }

@app.post("/switch")
async def switch(req: SwitchRequest):
    """手动切换指定引擎"""
    allowed = ["hermes", "lobster", "quad"]
    if req.target not in allowed:
        raise HTTPException(status_code=400, detail=f"target must be one of {allowed}")
    result = await coordinator.switch_engine(req.target)
    if result.get("status") == "switched":
        coordinator.current_brain = req.target
    return {
        "requested": req.target,
        "current": coordinator.current_brain,
        "result": result,
        "reason": req.reason or "manual switch",
    }

@app.get("/history")
def get_history(limit: int = 10):
    """获取历史决策记录"""
    hist = coordinator.history[-limit:]
    return [
        {
            "decision": r.decision.value,
            "recommended_brain": r.recommended_brain,
            "active_engine": r.active_engine,
            "confidence_diff": r.confidence_diff,
            "reasoning": r.reasoning,
            "timestamp": r.timestamp,
            "hermes_conf": r.hermes_signal.confidence if r.hermes_signal else None,
            "lobster_conf": r.lobster_signal.confidence if r.lobster_signal else None,
            "quad_conf": r.quad_signal.confidence if r.quad_signal else None,
        }
        for r in hist
    ]

@app.put("/mode")
def set_mode(req: ModeRequest):
    """更改协调器工作模式"""
    allowed = ["AUTO", "SEMI", "MANUAL"]
    if req.mode not in allowed:
        raise HTTPException(status_code=400, detail=f"mode must be one of {allowed}")
    coordinator.mode = req.mode
    return {"mode": coordinator.mode, "message": f"模式已切换为 {req.mode}"}

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "coordinator": coordinator.get_status()["mode"],
        "current_brain": coordinator.current_brain,
    }

# ═══════════════════════════════════════════════════════════════════
# v15.2 三方仲裁自动化: 自动轮询 vv6 + v15 → MiroFish仲裁
# ═══════════════════════════════════════════════════════════════════

import asyncio
import httpx
from datetime import datetime

COORDINATOR_VERSION = "v15.2"

# ─── 自动轮询配置 ──────────────────────────────────────────────
auto_poll_enabled = False
poll_interval_seconds = 60  # 每60秒轮询一次

BRAIN_ENDPOINTS = {
    "vv6": "http://localhost:8006/api/switch/analyze",
    "v15": "http://localhost:8015/api/decision/eq",
}

async def poll_brain_signal(brain: str, endpoint: str) -> dict:
    """从vv6或v15获取信号"""
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            if brain == "vv6":
                resp = await client.post(endpoint, json={"symbol": "BTCUSDT", "confidence": 80, "mode": "normal"})
            else:
                resp = await client.post(endpoint, json={
                    "brain_votes": {"alpha": 0.85, "beta": 0.80, "gamma": 0.70, "delta": 0.60},
                    "mirofish_scores": {},
                    "regime": "bull",
                    "rsi": 60,
                })
            data = resp.json()
            
            if brain == "vv6":
                sig = data.get("signal", {})
                return {
                    "direction": sig.get("direction", "HOLD").upper(),
                    "confidence": sig.get("confidence", 0.75),
                    "mi": sig.get("mi", 0.75),
                    "regime": sig.get("regime", "neutral"),
                    "source": "vv6",
                    "ok": True,
                }
            else:
                return {
                    "direction": data.get("direction", "HOLD").upper(),
                    "confidence": data.get("final_score", 0.6),
                    "mi": data.get("components", {}).get("fused_mi", 0.8),
                    "regime": "bull",
                    "source": "v15",
                    "ok": True,
                }
    except Exception as e:
        return {"source": brain, "ok": False, "error": str(e)}

async def poll_all_brains():
    """轮询所有大脑并推送信号到MiroFish仲裁"""
    global auto_poll_enabled
    
    while auto_poll_enabled:
        results = {}
        for brain, endpoint in BRAIN_ENDPOINTS.items():
            result = await poll_brain_signal(brain, endpoint)
            results[brain] = result
            
            if result.get("ok"):
                # 推送到MiroFish仲裁池
                try:
                    async with httpx.AsyncClient(timeout=5.0) as client:
                        await client.post("http://localhost:8020/arbitration/push", json={
                            "source": brain,
                            "direction": result["direction"],
                            "confidence": result["confidence"],
                            "mi": result["mi"],
                        })
                except:
                    pass
        
        # 同时记录到Coordinator历史
        now = datetime.now().isoformat()
        coord_state["auto_polls"].append({
            "timestamp": now,
            "results": {k: {"direction": v.get("direction","?"), "conf": v.get("confidence",0), "ok": v.get("ok")} for k, v in results.items()},
        })
        if len(coord_state["auto_polls"]) > 100:
            coord_state["auto_polls"] = coord_state["auto_polls"][-100:]
        
        await asyncio.sleep(poll_interval_seconds)

_auto_poll_task: asyncio.Task | None = None

@app.post("/auto-poll/start")
async def start_auto_poll(interval_seconds: int = 60):
    """启动自动轮询vv6+v15信号"""
    global auto_poll_enabled, poll_interval_seconds, _auto_poll_task
    auto_poll_enabled = True
    poll_interval_seconds = interval_seconds
    
    if _auto_poll_task is None or _auto_poll_task.done():
        _auto_poll_task = asyncio.create_task(poll_all_brains())
    
    return {"auto_poll": True, "interval_sec": interval_seconds, "brains": list(BRAIN_ENDPOINTS.keys())}

@app.post("/auto-poll/stop")
async def stop_auto_poll():
    global auto_poll_enabled, _auto_poll_task
    auto_poll_enabled = False
    if _auto_poll_task and not _auto_poll_task.done():
        _auto_poll_task.cancel()
    return {"auto_poll": False}

@app.get("/auto-poll/status")
def get_auto_poll_status():
    return {
        "enabled": auto_poll_enabled,
        "interval_sec": poll_interval_seconds,
        "brains": list(BRAIN_ENDPOINTS.keys()),
        "recent_polls": [
            {**p, "timestamp": p["timestamp"][-8:]}
            for p in coord_state.get("auto_polls", [])[-5:]
        ],
    }

@app.get("/auto-poll/trigger")
async def trigger_manual_poll():
    """手动触发一次轮询 (测试用)"""
    results = {}
    for brain, endpoint in BRAIN_ENDPOINTS.items():
        results[brain] = await poll_brain_signal(brain, endpoint)
    
    # 推送到MiroFish
    for brain, result in results.items():
        if result.get("ok"):
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    await client.post("http://localhost:8020/arbitration/push", json={
                        "source": brain,
                        "direction": result["direction"],
                        "confidence": result["confidence"],
                        "mi": result["mi"],
                    })
            except:
                pass
    
    return {"triggered": True, "results": results}
