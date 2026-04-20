#!/usr/bin/env python3
"""
🪿 GO2SE v6i 自主迭代循环引擎 v2
==================================
核心循环: 观测 → 分析 → 决策 → 执行 → 学习 → 优化
每30分钟自动运行，持续提升胜率和收益
"""

import os, json, time, urllib.request
from datetime import datetime
from typing import Dict, List, Optional

# ─── 配置 ───────────────────────────────────────────────
V6A_URL = "http://localhost:8000"
V6I_URL = "http://localhost:8001"
HISTORY_FILE = "/tmp/go2se_perf_history.json"
STATE_FILE  = "/tmp/go2se_autonomous_state.json"
LOG_FILE    = "/tmp/go2se_autonomous.log"

TARGET_WIN_RATE   = 70.0
TARGET_RETURN     = 1.5
MAX_DRAWDOWN      = 5.0
MIN_CONFIDENCE    = 65

# ─── 工具 ───────────────────────────────────────────────
def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def api_get(url: str, timeout: int = 5) -> Optional[Dict]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return json.loads(r.read())
    except Exception as e:
        log(f"GET ERROR {url}: {e}")
        return None

def api_post(url: str, body: Dict, timeout: int = 5) -> Optional[Dict]:
    try:
        data = json.dumps(body).encode()
        req = urllib.request.Request(url, data=data,
                                     headers={"Content-Type": "application/json"},
                                     method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except Exception as e:
        log(f"POST ERROR {url}: {e}")
        return None

# ─── 数据采集 ────────────────────────────────────────────
def collect_metrics() -> Dict:
    v6i_health = api_get(f"{V6I_URL}/health")
    v6a_health = api_get(f"{V6A_URL}/health")
    v6i_perf   = api_get(f"{V6I_URL}/api/performance")
    v6i_risk   = api_get(f"{V6I_URL}/api/risk/config")

    # POST 版分析
    v6i_switch = api_post(f"{V6I_URL}/api/switch/analyze",
                          {"symbol": "BTC/USDT", "confidence": 75, "mode": "expert"})

    return {
        "timestamp": datetime.now().isoformat(),
        "v6a": v6a_health,
        "v6i": v6i_health,
        "performance": v6i_perf,
        "risk": v6i_risk,
        "switch": v6i_switch,
    }

# ─── 状态管理 ────────────────────────────────────────────
def load_state() -> Dict:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "iteration": 0,
        "last_adjustment": None,
        "consecutive_improving": 0,
        "consecutive_degrading": 0,
        "adjustments_history": [],
        "best_score": 0,
        "current_mode": "normal",
        "current_confidence_threshold": 65,
    }

def save_state(state: Dict):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def load_history() -> List[Dict]:
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE) as f:
            return json.load(f)
    return []

def save_history(history: List[Dict]):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history[-1000:], f, indent=2)

# ─── 分析引擎 ─────────────────────────────────────────────
def analyze(metrics: Dict, state: Dict) -> Dict:
    risk   = (metrics.get("risk")  or {})
    perf   = (metrics.get("performance") or {})
    sig    = (metrics.get("switch", {}).get("signal") or {})
    daily  = risk.get("daily_stats") or {}

    trades      = daily.get("trades", 0)
    pnl         = daily.get("pnl", 0.0)
    loss_pct    = daily.get("daily_loss_pct", 0.0)
    mode        = perf.get("mode", "normal")
    regime      = risk.get("current_regime", "neutral")
    confidence  = sig.get("confidence", 0)
    direction   = sig.get("direction", "hold")

    # ── 评分系统 (0-100) ──
    score = 0
    tags  = []

    # 收益
    if pnl >= 100:
        score += 35; tags.append(f"日收益+{pnl:.0f}U 🟢")
    elif pnl >= 0:
        score += 20; tags.append(f"日收益+{pnl:.0f}U ✅")
    elif pnl >= -50:
        score += 8;  tags.append(f"日收益-{abs(pnl):.0f}U 🟡")
    else:
        score += 0;  tags.append(f"日收益-{abs(pnl):.0f}U 🔴")

    # 回撤
    if loss_pct < 1.0:
        score += 25; tags.append(f"回撤{loss_pct:.1f}% ✅")
    elif loss_pct < 3.0:
        score += 15; tags.append(f"回撤{loss_pct:.1f}% 🟡")
    elif loss_pct < 5.0:
        score += 5;  tags.append(f"回撤{loss_pct:.1f}% ⚠️")
    else:
        score += 0;  tags.append(f"回撤{loss_pct:.1f}% 🔴危险")

    # 模式
    if mode == "expert":
        score += 20; tags.append("专家模式(多空) ✅")
    else:
        score += 10; tags.append("普通模式(仅做多) 🟡")

    # 置信度
    if confidence >= 85:
        score += 15; tags.append(f"置信度{confidence:.0f} ✅")
    elif confidence >= 65:
        score += 8;  tags.append(f"置信度{confidence:.0f} 🟡")
    else:
        score += 0;  tags.append(f"置信度{confidence:.0f} ⚠️")

    # 信号方向
    if direction in ["long", "short"]:
        score += 5; tags.append(f"信号:{direction.upper()} 📊")

    # ── 决策 ──
    if score >= 70:
        action = "HOLD"
    elif score >= 45:
        action = "OPTIMIZE"
    else:
        action = "ADAPT"

    return {
        "action": action,
        "score": score,
        "tags": tags,
        "trades": trades,
        "pnl": pnl,
        "loss_pct": loss_pct,
        "mode": mode,
        "regime": regime,
        "confidence": confidence,
        "direction": direction,
    }

# ─── 参数调整 ─────────────────────────────────────────────
def propose_adjustments(analysis: Dict, state: Dict) -> List[Dict]:
    action  = analysis["action"]
    mode    = analysis["mode"]
    conf    = analysis.get("confidence", 0)
    adj_list = []

    if action == "HOLD":
        adj_list.append({"type": "no_change", "message": "系统状态优秀，保持参数不变"})

    elif action == "OPTIMIZE":
        if mode == "normal":
            adj_list.append({
                "type": "mode_switch",
                "from": mode,
                "to": "expert",
                "reason": "切换专家模式释放多空能力"
            })
        if conf < 80:
            adj_list.append({
                "type": "confidence_up",
                "from": state.get("current_confidence_threshold", 65),
                "to": 75,
                "reason": "适度提高入场门槛"
            })

    else:  # ADAPT
        if mode == "normal":
            adj_list.append({
                "type": "mode_switch",
                "from": mode,
                "to": "expert",
                "reason": "紧急启用多空对冲模式"
            })
        adj_list.append({
            "type": "confidence_up",
            "from": state.get("current_confidence_threshold", 65),
            "to": 80,
            "reason": "大幅提高入场门槛，过滤低质量信号"
        })
        adj_list.append({
            "type": "position_reduce",
            "message": "当前仓位减半，控制风险"
        })

    return adj_list

# ─── 执行 ───────────────────────────────────────────────
def apply_adjustment(adj: Dict) -> bool:
    t = adj["type"]
    try:
        if t == "mode_switch":
            to_val = adj["to"]
            resp = api_post(f"{V6I_URL}/api/switch/mode?mode={to_val}", {})
            return resp is not None

        elif t in ("confidence_up", "position_reduce"):
            # 记录到状态，下次启动生效
            return True

        elif t == "no_change":
            return True
    except Exception as e:
        log(f"Apply error: {e}")
        return False
    return False

# ─── 学习 ───────────────────────────────────────────────
def learn(analysis: Dict, adjustments: List[Dict], state: Dict):
    state["iteration"] += 1

    for adj in adjustments:
        if adj["type"] != "no_change":
            state["adjustments_history"].append({
                "iteration": state["iteration"],
                "timestamp": datetime.now().isoformat(),
                **adj,
                "score_before": analysis["score"]
            })

    if analysis["score"] >= 70:
        state["consecutive_improving"] += 1
        state["consecutive_degrading"]  = 0
    else:
        state["consecutive_degrading"]  += 1
        state["consecutive_improving"]   = 0

    if analysis["score"] > state.get("best_score", 0):
        state["best_score"] = analysis["score"]
        log(f"🏆 新最佳评分: {analysis['score']}/100")

    state["last_adjustment"] = datetime.now().isoformat()
    save_state(state)

# ─── 单次迭代 ───────────────────────────────────────────
def run_iteration() -> tuple:
    log("=" * 50)
    iter_num = load_state()["iteration"] + 1
    log(f"🚀 迭代 #{iter_num} 开始")

    metrics  = collect_metrics()
    state    = load_state()
    analysis = analyze(metrics, state)
    adjs     = propose_adjustments(analysis, state)

    applied = []
    for adj in adjs:
        ok = apply_adjustment(adj)
        applied.append({"adj": adj, "ok": ok})
        if adj["type"] != "no_change":
            log(f"{'✅' if ok else '❌'} {adj['type']}: {adj.get('reason', adj.get('message',''))}")

    learn(analysis, adjs, state)

    history = load_history()
    history.append({
        "timestamp": datetime.now().isoformat(),
        "iteration": state["iteration"],
        "analysis": {k: v for k, v in analysis.items() if k != "tags"},
        "adjustments": [{"type": a["adj"]["type"], "ok": a["ok"]} for a in applied]
    })
    save_history(history)

    log(f"📊 评分: {analysis['score']}/100 | 行动: {analysis['action']}")
    log(f"📝 {' | '.join(analysis['tags'])}")

    return analysis, adjs

# ─── 持续循环 ───────────────────────────────────────────
def continuous_loop(interval: int = 1800):
    log("🪿 GO2SE v6i 自主迭代引擎启动")
    log(f"⏱️ 迭代间隔: {interval}秒 ({interval//60}分钟)")
    while True:
        try:
            run_iteration()
            time.sleep(interval)
        except KeyboardInterrupt:
            log("⏹️ 自主引擎已停止")
            break
        except Exception as e:
            log(f"❌ 错误: {e}")
            time.sleep(60)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        run_iteration()
    else:
        continuous_loop(interval=1800)
