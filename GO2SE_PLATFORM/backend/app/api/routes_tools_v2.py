#!/usr/bin/env python3
"""
🛠️ 投资+打工工具 V2 API
===========================
5大投资工具 + 2大打工工具 完整API
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

router = APIRouter(prefix="/api/tools/v2", tags=["工具V2"])

# ═══════════════════════════════════════════════════════
# 🐰 打兔子 V2
# ═══════════════════════════════════════════════════════

@router.get("/rabbit/top")
async def rabbit_top(limit: int = Query(default=10, le=20)):
    """🐰 Top币种趋势分析"""
    try:
        import sys, os
        from rabbit.rabbit_strategy_v2 import get_rabbit_v2_strategy
        engine = get_rabbit_v2_strategy()
        results = engine.analyze_all()
        return {
            "success": True,
            "tool": "rabbit",
            "version": "v2",
            "count": len(results[:limit]),
            "results": results[:limit],
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# ═══════════════════════════════════════════════════════
# 🐹 打地鼠 V2
# ═══════════════════════════════════════════════════════

@router.get("/mole/alerts")
async def mole_alerts(limit: int = Query(default=10, le=30)):
    """🐹 异动扫描警报"""
    try:
        import sys
        from mole.mole_strategy_v2 import get_mole_v2_strategy
        engine = get_mole_v2_strategy()
        alerts = engine.scan_all()
        return {
            "success": True,
            "tool": "mole",
            "version": "v2",
            "count": len(alerts[:limit]),
            "alerts": alerts[:limit],
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# ═══════════════════════════════════════════════════════
# 🔮 走着瞧 V2
# ═══════════════════════════════════════════════════════

@router.get("/oracle/opportunities")
async def oracle_opportunities():
    """🔮 预测市场机会"""
    try:
        import sys
        from oracle.oracle_strategy_v2 import get_oracle_v2_strategy
        engine = get_oracle_v2_strategy()
        opps = engine.get_opportunities()
        return {"success": True, "tool": "oracle", "version": "v2", **opps}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/oracle/market/{market_id}")
async def oracle_market(market_id: str):
    """单个预测市场详情"""
    try:
        import sys
        from oracle.oracle_strategy_v2 import get_oracle_v2_strategy
        engine = get_oracle_v2_strategy()
        markets = engine.get_markets()
        for m in markets:
            if m.get('id') == market_id:
                return {"success": True, "analysis": engine.analyze_market(m)}
        raise HTTPException(status_code=404, detail="市场不存在")
    except Exception as e:
        return {"success": False, "error": str(e)}

# ═══════════════════════════════════════════════════════
# 👑 跟大歌 V2
# ═══════════════════════════════════════════════════════

@router.get("/leader/signals")
async def leader_signals(limit: int = Query(default=5, le=10)):
    """👑 做市协作信号"""
    try:
        import sys
        from leader.leader_strategy_v2 import get_leader_v2_strategy
        engine = get_leader_v2_strategy()
        results = engine.analyze_all()
        return {
            "success": True,
            "tool": "leader",
            "version": "v2",
            "count": len(results[:limit]),
            "signals": results[:limit],
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# ═══════════════════════════════════════════════════════
# 🌐 搭便车 V2
# ═══════════════════════════════════════════════════════

@router.get("/hitchhiker/traders")
async def hitchhiker_traders(min_score: float = Query(default=60, le=100)):
    """🌐 顶级交易员"""
    try:
        import sys
        from hitchhiker.hitchhiker_strategy_v2 import get_hitchhiker_v2_strategy
        engine = get_hitchhiker_v2_strategy()
        traders = engine.get_top_traders(min_score=min_score)
        return {
            "success": True,
            "tool": "hitchhiker",
            "version": "v2",
            "count": len(traders),
            "traders": traders,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/hitchhiker/allocation")
async def hitchhiker_allocation(capital: float = Query(default=10000, ge=100)):
    """💰 跟单分配"""
    try:
        import sys
        from hitchhiker.hitchhiker_strategy_v2 import get_hitchhiker_v2_strategy
        engine = get_hitchhiker_v2_strategy()
        traders = engine.get_top_traders(min_score=60)
        allocations = engine.get_allocation(traders, capital)
        perf = engine.simulate_performance(traders)
        return {
            "success": True,
            "tool": "hitchhiker",
            "version": "v2",
            "capital": capital,
            "allocations": allocations,
            "simulated_performance_30d": perf,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# ═══════════════════════════════════════════════════════
# 🐏 薅羊毛 V2
# ═══════════════════════════════════════════════════════

@router.get("/wool/tasks")
async def wool_tasks(
    chain: Optional[str] = None,
    risk: Optional[str] = None,
    min_return: Optional[float] = None,
):
    """🐏 打工任务 - 空投猎手"""
    try:
        import sys
        from airdrop.airdrop_engine_v2 import get_airdrop_v2_engine
        engine = get_airdrop_v2_engine()
        filters = {}
        if chain: filters['chain'] = chain
        if risk: filters['risk'] = risk
        if min_return: filters['min_return'] = min_return
        tasks = engine.get_tasks(filters if filters else None)
        portfolio = engine.get_portfolio_summary()
        return {
            "success": True,
            "tool": "wool",
            "version": "v2",
            "count": len(tasks),
            "tasks": tasks,
            "portfolio_summary": portfolio,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/wool/top")
async def wool_top(limit: int = Query(default=10, le=30)):
    """🏆 最优任务排序"""
    try:
        import sys
        from airdrop.airdrop_engine_v2 import get_airdrop_v2_engine
        engine = get_airdrop_v2_engine()
        tasks = engine.get_tasks()
        return {
            "success": True,
            "tool": "wool",
            "version": "v2",
            "top_tasks": tasks[:limit],
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# ═══════════════════════════════════════════════════════
# 👶 穷孩子 V2
# ═══════════════════════════════════════════════════════

@router.get("/poor/tasks")
async def poor_tasks(
    min_hourly: Optional[float] = None,
    platform: Optional[str] = None,
    language: Optional[str] = None,
):
    """👶 众包任务"""
    try:
        import sys
        from crowdsource.crowdsource_engine_v2 import get_crowdsource_v2_engine
        engine = get_crowdsource_v2_engine()
        filters = {}
        if min_hourly: filters['min_hourly'] = min_hourly
        if platform: filters['platform'] = platform
        if language: filters['language'] = language
        tasks = engine.get_tasks(filters if filters else None)
        summary = engine.get_summary()
        return {
            "success": True,
            "tool": "poor",
            "version": "v2",
            "count": len(tasks),
            "tasks": tasks,
            "summary": summary,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/poor/summary")
async def poor_summary():
    """📊 众包收益总览"""
    try:
        import sys
        from crowdsource.crowdsource_engine_v2 import get_crowdsource_v2_engine
        engine = get_crowdsource_v2_engine()
        return {"success": True, "tool": "poor", "version": "v2", **engine.get_summary()}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ═══════════════════════════════════════════════════════
# 📊 综合面板
# ═══════════════════════════════════════════════════════

@router.get("/dashboard")
async def tools_dashboard():
    """🖥️ 工具综合面板"""
    try:
        import sys
        
        results = {
            "investment_tools": {},
            "work_tools": {},
            "timestamp": datetime.now().isoformat(),
        }
        
        # 投资工具
        try:
            from rabbit.rabbit_strategy_v2 import get_rabbit_v2_strategy
            r = get_rabbit_v2_strategy()
            top = r.analyze_all()[:3]
            results["investment_tools"]["rabbit"] = {"status": "active", "top_picks": [t['symbol'] for t in top]}
        except: results["investment_tools"]["rabbit"] = {"status": "error"}
        
        try:
            from mole.mole_strategy_v2 import get_mole_v2_strategy
            m = get_mole_v2_strategy()
            alerts = m.scan_all()[:3]
            results["investment_tools"]["mole"] = {"status": "active", "alerts": len(alerts)}
        except: results["investment_tools"]["mole"] = {"status": "error"}
        
        try:
            from oracle.oracle_strategy_v2 import get_oracle_v2_strategy
            o = get_oracle_v2_strategy()
            opps = o.get_opportunities()
            results["investment_tools"]["oracle"] = {"status": "active", "opportunities": len(opps.get("opportunities",[]))}
        except: results["investment_tools"]["oracle"] = {"status": "error"}
        
        try:
            from leader.leader_strategy_v2 import get_leader_v2_strategy
            l = get_leader_v2_strategy()
            sigs = l.analyze_all()[:2]
            results["investment_tools"]["leader"] = {"status": "active", "signals": [s['symbol'] for s in sigs]}
        except: results["investment_tools"]["leader"] = {"status": "error"}
        
        try:
            from hitchhiker.hitchhiker_strategy_v2 import get_hitchhiker_v2_strategy
            h = get_hitchhiker_v2_strategy()
            traders = h.get_top_traders(min_score=60)
            results["investment_tools"]["hitchhiker"] = {"status": "active", "top_traders": len(traders)}
        except: results["investment_tools"]["hitchhiker"] = {"status": "error"}
        
        # 打工工具
        try:
            from airdrop.airdrop_engine_v2 import get_airdrop_v2_engine
            w = get_airdrop_v2_engine()
            port = w.get_portfolio_summary()
            results["work_tools"]["wool"] = {"status": "active", "net_potential": port.get("net_potential", 0), "available": port.get("available", 0)}
        except: results["work_tools"]["wool"] = {"status": "error"}
        
        try:
            from crowdsource.crowdsource_engine_v2 import get_crowdsource_v2_engine
            c = get_crowdsource_v2_engine()
            s = c.get_summary()
            results["work_tools"]["poor"] = {"status": "active", "total_reward": s.get("total_reward", 0), "avg_hourly": s.get("avg_hourly", 0)}
        except: results["work_tools"]["poor"] = {"status": "error"}
        
        return {"success": True, **results}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ─── Rabbit V3 Router ─────────────────────────────────────────────────
@router.get("/rabbit/v3/top")
async def rabbit_v3_top(limit: int = 10):
    """🐰 打兔子 V3 - Mi区间感知趋势追踪"""
    from rabbit.rabbit_strategy_v3 import get_rabbit_v3_strategy
    try:
        strat = get_rabbit_v3_strategy()
        results = await strat.analyze_all()
        return {
            "success": True,
            "tool": "rabbit",
            "version": "v3_mi_regime",
            "count": len(results),
            "results": results[:limit],
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ─── Mole V3 Router ──────────────────────────────────────────────────
@router.get("/mole/v3/alerts")
async def mole_v3_alerts(limit: int = 10):
    """🐹 打地鼠 V3 - Mi区间感知异动扫描"""
    from mole.mole_strategy_v3 import get_mole_v3_strategy
    try:
        strat = get_mole_v3_strategy()
        alerts = await strat.scan_all()
        return {
            "success": True,
            "tool": "mole",
            "version": "v3_mi_volatility",
            "count": len(alerts),
            "alerts": alerts[:limit],
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# ─── Rabbit V4 Router ─────────────────────────────────────────────────
@router.get("/rabbit/v4/top")
async def rabbit_v4_top(limit: int = 10):
    """🐰 打兔子 V4 - 多维度趋势增强版"""
    from rabbit.rabbit_strategy_v4 import get_rabbit_v4_strategy
    try:
        strat = get_rabbit_v4_strategy()
        results = await strat.analyze_all()
        return {
            "success": True,
            "tool": "rabbit",
            "version": "v4_multi_dim",
            "count": len(results),
            "results": results[:limit],
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# ─── Mole V4 Router ─────────────────────────────────────────────────
@router.get("/mole/v4/alerts")
async def mole_v4_alerts(limit: int = 10):
    """🐹 打地鼠 V4 - 多维异动增强版"""
    from mole.mole_strategy_v4 import get_mole_v4_strategy
    try:
        strat = get_mole_v4_strategy()
        alerts = await strat.scan_all()
        return {
            "success": True,
            "tool": "mole",
            "version": "v4_multi_alert",
            "count": len(alerts),
            "alerts": alerts[:limit],
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# ─── Decision Engine V2 ───────────────────────────────────────────────
@router.get("/decision/v2/analyze")
async def decision_v2_analyze(limit: int = 10):
    """🎯 多因子决策引擎 V2 - 综合Mi+RSI+FG+Trend+Momentum"""
    from decision_engine import get_decision_engine_v3
    try:
        engine = get_decision_engine_v3()
        
        TOP20 = ['BTC','ETH','BNB','SOL','XRP','ADA','DOGE','AVAX','DOT','MATIC',
                 'LINK','UNI','ATOM','LTC','ETC','XLM','NEAR','APT','ARB','OP']
        prices = {
            'BTC': 95000, 'ETH': 3200, 'BNB': 650, 'SOL': 180,
            'XRP': 2.5, 'ADA': 0.95, 'DOGE': 0.32, 'AVAX': 38,
            'DOT': 8.5, 'MATIC': 0.95, 'LINK': 18, 'UNI': 12,
            'ATOM': 9, 'LTC': 95, 'ETC': 28, 'XLM': 0.42,
            'NEAR': 8, 'APT': 12, 'ARB': 1.2, 'OP': 2.5
        }
        
        results = await engine.analyze_all(TOP20[:limit], prices)
        
        return {
            "success": True,
            "tool": "decision",
            "version": "v3_multi_factor_optimized",
            "count": len(results),
            "regime": results[0]['regime'] if results else 'NEUTRAL',
            "results": results,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# ─── Wool V3 Router ─────────────────────────────────────────────────
@router.get("/wool/v3/tasks")
async def wool_v3_tasks(limit: int = 50):
    """🐏 空投任务 V3 - 50+任务扩展版"""
    from wool.wool_engine_v3 import get_wool_v3
    try:
        data = get_wool_v3()
        tasks = data.get('tasks', [])[:limit]
        total = sum(t['reward_usd'] * t.get('volume', 1) for t in tasks)
        return {
            "success": True,
            "tool": "wool",
            "version": "v3_expanded",
            "count": len(tasks),
            "total_reward": total,
            "tasks": tasks,
            "by_chain": data.get('by_chain', {}),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# ─── Hitchhiker V3 Router ──────────────────────────────────────────
@router.get("/hitchhiker/v3/traders")
async def hitchhiker_v3_traders(min_score: float = 50):
    """🌐 跟单交易员 V3 - 15+交易员池"""
    from hitchhiker.hitchhiker_engine_v3 import get_hitchhiker_v3
    try:
        data = get_hitchhiker_v3()
        traders = [t for t in data.get('traders', []) if t['win_rate'] * 100 >= min_score]
        traders.sort(key=lambda x: x['win_rate'] * x['ratio'], reverse=True)
        return {
            "success": True,
            "tool": "hitchhiker",
            "version": "v3_expanded",
            "count": len(traders),
            "traders": traders,
            "top_5": traders[:5],
            "avg_win_rate": round(data.get('avg_win_rate', 0) * 100, 1),
            "avg_ratio": round(data.get('avg_ratio', 0), 2),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# ─── Crowdsource V3 Router ─────────────────────────────────────────
@router.get("/poor/v3/summary")
async def crowdsource_v3_summary():
    """👶 众包任务 V3 - 40+任务"""
    from crowdsource.crowdsource_engine_v3 import get_crowdsource_v3
    try:
        data = get_crowdsource_v3()
        return {
            "success": True,
            "tool": "poor",
            "version": "v3_expanded",
            "count": data.get('count', 0),
            "total_reward": data.get('total_reward', 0),
            "avg_hourly": data.get('avg_hourly', 0),
            "by_platform": data.get('by_platform', {}),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# ─── Rabbit V5 (CoinGecko Live) ────────────────────────────────────
@router.get("/rabbit/v5/top")
async def rabbit_v5_top(limit: int = 10):
    """🐰 打兔子 V5 - CoinGecko真实市场数据"""
    from rabbit.rabbit_strategy_v5 import get_rabbit_v5_strategy
    try:
        strat = get_rabbit_v5_strategy()
        results = strat.analyze_all()
        return {
            "success": True,
            "tool": "rabbit",
            "version": "v5_coingecko_live",
            "count": len(results),
            "results": results[:limit],
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# ─── Mole V5 (CoinGecko Live) ────────────────────────────────────
@router.get("/mole/v5/alerts")
async def mole_v5_alerts(limit: int = 10):
    """🐹 打地鼠 V5 - CoinGecko真实异动扫描"""
    from mole.mole_strategy_v5 import get_mole_v5_strategy
    try:
        strat = get_mole_v5_strategy()
        alerts = strat.scan_all()
        return {
            "success": True,
            "tool": "mole",
            "version": "v5_coingecko_live",
            "count": len(alerts),
            "alerts": alerts[:limit],
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# ─── Rabbit V6 (Optimized Bull Market) ────────────────────────────
@router.get("/rabbit/v6/top")
async def rabbit_v6_top(limit: int = 10):
    """🐰 打兔子 V6 - 牛市优化版"""
    from rabbit.rabbit_strategy_v6 import get_rabbit_v6_strategy
    try:
        strat = get_rabbit_v6_strategy()
        results = strat.analyze_all()
        return {
            "success": True,
            "tool": "rabbit",
            "version": "v6_bull_optimized",
            "count": len(results),
            "results": results[:limit],
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# ─── Mole V6 (Long Only) ──────────────────────────────────────────
@router.get("/mole/v6/alerts")
async def mole_v6_alerts(limit: int = 10):
    """🐹 打地鼠 V6 - 牛市只做多版"""
    from mole.mole_strategy_v6 import get_mole_v6_strategy
    try:
        strat = get_mole_v6_strategy()
        alerts = strat.scan_all()
        return {
            "success": True,
            "tool": "mole",
            "version": "v6_long_only",
            "count": len(alerts),
            "alerts": alerts[:limit],
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# ─── Rabbit V7 (多空切换 + 杠杆) ────────────────────────────────
@router.get("/rabbit/v7/top")
async def rabbit_v7_top(limit: int = 10):
    """🐰 打兔子 V7 - 多空自主切换 + 杠杆"""
    from rabbit.rabbit_strategy_v7 import get_rabbit_v7_strategy
    try:
        strat = get_rabbit_v7_strategy()
        results = strat.analyze_all()
        regime = results[0].get('regime', 'unknown') if results else 'unknown'
        return {
            "success": True,
            "tool": "rabbit",
            "version": "v7_long_short_leverage",
            "regime": regime,
            "count": len(results),
            "results": results[:limit],
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# ─── Mole V7 (多空切换 + 杠杆) ─────────────────────────────────
@router.get("/mole/v7/alerts")
async def mole_v7_alerts(limit: int = 10):
    """🐹 打地鼠 V7 - 多空自主切换 + 杠杆"""
    from mole.mole_strategy_v7 import get_mole_v7_strategy
    try:
        strat = get_mole_v7_strategy()
        alerts = strat.scan_all()
        regime = alerts[0].get('regime', 'unknown') if alerts else 'unknown'
        return {
            "success": True,
            "tool": "mole",
            "version": "v7_long_short_leverage",
            "regime": regime,
            "count": len(alerts),
            "alerts": alerts[:limit],
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# ─── Brain Architecture 脑系统 ────────────────────────────────
@router.get("/brain/status")
async def brain_status():
    """🧠 大脑系统状态"""
    from brain.brain_architecture import get_status
    try:
        return {"success": True, "data": get_status()}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/brain/decide")
async def brain_decide(btc_change_24h: float = 0, btc_change_7d: float = 0, change_24h: float = 0, volume_ratio: float = 0):
    """🧠 脑系统决策"""
    from brain.brain_architecture import get_brain_system
    try:
        brain = get_brain_system()
        market_data = {
            "btc_change_24h": btc_change_24h,
            "btc_change_7d": btc_change_7d,
            "change_24h": change_24h,
            "volume_ratio": volume_ratio,
        }
        decision = brain.decide(market_data)
        return {"success": True, "decision": decision}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/brain/feedback")
async def brain_feedback(subsystem: str, outcome: float, mode: str = None):
    """🧠 脑系统反馈"""
    from brain.brain_architecture import get_brain_system
    try:
        brain = get_brain_system()
        decision = {"subsystem": subsystem, "mode": mode}
        brain.feedback(decision, outcome)
        return {"success": True, "learning_cycles": brain.hermes.learning_cycle}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ─── Rabbit V8 (优化版) ────────────────────────────────────────
@router.get("/rabbit/v8/top")
async def rabbit_v8_top(limit: int = 10):
    """🐰 打兔子 V8 - GStack优化版 (阈值0.6, 杠杆3.0x)"""
    from rabbit.rabbit_strategy_v8 import get_rabbit_v8_strategy
    try:
        strat = get_rabbit_v8_strategy()
        results = strat.analyze_all()
        return {
            "success": True, "tool": "rabbit", "version": "v8_optimized",
            "regime": results[0].get('regime','?') if results else '?',
            "count": len(results), "results": results[:limit],
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# ─── Quant Core 高频量化路由 ─────────────────────────────────────
@router.get("/quant/status")
async def quant_status():
    """⚡ 量化系统状态"""
    from quant.quant_core import get_status
    try:
        return {"success": True, "data": get_status()}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/quant/execute")
async def quant_execute(btc_price: float = 75000, btc_change_7d: float = 3.0, btc_volume: float = 1000000):
    """⚡ 执行量化决策周期"""
    from quant.quant_core import get_quant_core
    try:
        core = get_quant_core()
        market_data = {
            "btc_price": btc_price,
            "btc_change_7d": btc_change_7d,
            "btc_volume": btc_volume
        }
        result = core.execute_cycle(market_data)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/quant/decision")
async def quant_decision():
    """⚡ 获取加权组合决策"""
    from quant.quant_core import get_quant_core
    try:
        core = get_quant_core()
        # 使用当前市场数据
        import urllib.request
        url = "http://localhost:8000/api/v7/market/summary"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
        market_data = data.get("data", {})
        
        # 估算BTC变化
        top_gainer = market_data.get("top_gainers", [{}])[0] if market_data.get("top_gainers") else {}
        btc_change = top_gainer.get("change", 0) if top_gainer else 0
        
        result = core.get_composite_signals({
            "btc_change_7d": btc_change * 7  # 估算
        })
        
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ─── VV6 高频版路由 ────────────────────────────────────────────
@router.get("/vv6/highfreq/status")
async def vv6_highfreq_status():
    """⚡ VV6 高频版状态"""
    from vv6_high_freq import get_vv6_high_freq
    try:
        obj = get_vv6_high_freq()
        return {"success": True, "data": obj.get_status()}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/vv6/highfreq/run")
async def vv6_highfreq_run():
    """⚡ VV6 高频版运行一个月"""
    from vv6_high_freq import get_vv6_high_freq
    try:
        obj = get_vv6_high_freq()
        result = obj.run_month()
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ─── V15 优化版路由 ────────────────────────────────────────────
@router.get("/v15/optimized/status")
async def v15_optimized_status():
    """🎯 V15 优化版状态"""
    from v15_wrapper import get_v15_optimized
    try:
        obj = get_v15_optimized()
        return {"success": True, "data": obj.get_status()}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/v15/optimized/run")
async def v15_optimized_run(mi: float = 0.75):
    """🎯 V15 优化版运行一个月"""
    from v15_wrapper import get_v15_optimized
    try:
        obj = get_v15_optimized()
        result = obj.run_month({"mi": mi})
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ─── 打工投资自主切换路由 ─────────────────────────────────

@router.get("/dual/status")
async def dual_status():
    """⚖️ 打工投资双模式状态"""
    import sys
    sys.path.insert(0, '/home/goose/.openclaw/workspace/openclaw-workspace/GO2SE_PLATFORM/versions/v6/strategies')
    from dual_mode.autonomous_switch import get_dual_mode_engine
    try:
        engine = get_dual_mode_engine()
        return {
            "success": True,
            "data": {
                "current_mode": engine.current_mode.value,
                "work_capital": engine.work_capital,
                "invest_capital": engine.invest_capital,
                "total_capital": engine.total_capital,
                "work_days": engine.work_days,
                "invest_days": engine.invest_days,
                "consecutive_losses": engine.consecutive_invest_losses
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/dual/run")
async def dual_run(days: int = 30):
    """⚖️ 运行打工投资自主切换"""
    import sys
    sys.path.insert(0, '/home/goose/.openclaw/workspace/openclaw-workspace/GO2SE_PLATFORM/versions/v6/strategies')
    from dual_mode.autonomous_switch import get_dual_mode_engine
    try:
        engine = get_dual_mode_engine()
        result = engine.run_month(days)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/dual/day")
async def dual_day():
    """⚖️ 执行一天"""
    import sys
    sys.path.insert(0, '/home/goose/.openclaw/workspace/openclaw-workspace/GO2SE_PLATFORM/versions/v6/strategies')
    from dual_mode.autonomous_switch import get_dual_mode_engine
    try:
        engine = get_dual_mode_engine()
        result = engine.run_day()
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/dual/switch")
async def dual_switch():
    """⚖️ 查看切换状态"""
    import sys
    sys.path.insert(0, '/home/goose/.openclaw/workspace/openclaw-workspace/GO2SE_PLATFORM/versions/v6/strategies')
    from dual_mode.autonomous_switch import get_dual_mode_engine
    try:
        engine = get_dual_mode_engine()
        decision = engine.should_switch()
        return {
            "success": True,
            "data": {
                "current_mode": engine.current_mode.value,
                "suggested_action": decision,
                "mi": engine.get_mi(),
                "market": engine.simulate_market()
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ─── Hitchhiker V4 套利路由 ─────────────────────────────────
@router.get("/hitchhiker/v4/status")
async def hitchhiker_v4_status():
    """🎒 Hitchhiker V4 状态"""
    import sys
    sys.path.insert(0, '/home/goose/.openclaw/workspace/openclaw-workspace/GO2SE_PLATFORM/versions/v6/strategies')
    from hitchhiker.hitchhiker_engine_v4 import get_hitchhiker_v4
    try:
        engine = get_hitchhiker_v4()
        return {"success": True, "data": engine.get_status()}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/hitchhiker/v4/day")
async def hitchhiker_v4_day():
    """🎒 执行一天套利"""
    import sys
    sys.path.insert(0, '/home/goose/.openclaw/workspace/openclaw-workspace/GO2SE_PLATFORM/versions/v6/strategies')
    from hitchhiker.hitchhiker_engine_v4 import get_hitchhiker_v4
    try:
        engine = get_hitchhiker_v4()
        result = engine.run_day()
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/hitchhiker/v4/run")
async def hitchhiker_v4_run(days: int = 30):
    """🎒 运行套利策略"""
    import sys
    sys.path.insert(0, '/home/goose/.openclaw/workspace/openclaw-workspace/GO2SE_PLATFORM/versions/v6/strategies')
    from hitchhiker.hitchhiker_engine_v4 import get_hitchhiker_v4
    try:
        engine = get_hitchhiker_v4()
        result = engine.run_month(days)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/hitchhiker/v4/scan")
async def hitchhiker_v4_scan():
    """🎒 扫描套利机会"""
    import sys
    sys.path.insert(0, '/home/goose/.openclaw/workspace/openclaw-workspace/GO2SE_PLATFORM/versions/v6/strategies')
    from hitchhiker.hitchhiker_engine_v4 import ExchangeArbitrage
    try:
        arb = ExchangeArbitrage()
        opportunities = arb.scan_opportunities()
        return {"success": True, "data": {"opportunities": opportunities}}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ─── 打工雷达 + 预测 + 抢单路由 ─────────────────────────────────
@router.get("/work/radar/scan")
async def work_radar_scan(category: str = "all"):
    """🔍 打工机会雷达扫描"""
    import sys
    sys.path.insert(0, '/home/goose/.openclaw/workspace/openclaw-workspace/GO2SE_PLATFORM/versions/v6/strategies')
    from work_radar import get_work_radar
    try:
        radar = get_work_radar()
        result = radar.radar_scan(category)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/work/radar/status")
async def work_radar_status():
    """📡 雷达状态"""
    import sys
    sys.path.insert(0, '/home/goose/.openclaw/workspace/openclaw-workspace/GO2SE_PLATFORM/versions/v6/strategies')
    from work_radar import get_work_radar
    try:
        radar = get_work_radar()
        return {"success": True, "data": radar.get_status()}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/work/radar/predict")
async def work_radar_predict(task_ids: str = ""):
    """📊 预测并比较任务"""
    import sys
    sys.path.insert(0, '/home/goose/.openclaw/workspace/openclaw-workspace/GO2SE_PLATFORM/versions/v6/strategies')
    from work_radar import get_work_radar
    try:
        radar = get_work_radar()
        ids = task_ids.split(",") if task_ids else []
        result = radar.predict_and_compare(ids)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/work/radar/snipe")
async def work_radar_snipe(task_id: str = ""):
    """⚡ 抢单"""
    import sys
    sys.path.insert(0, '/home/goose/.openclaw/workspace/openclaw-workspace/GO2SE_PLATFORM/versions/v6/strategies')
    from work_radar import get_work_radar
    try:
        radar = get_work_radar()
        result = radar.snipe(task_id)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/work/radar/snipe-batch")
async def work_radar_snipe_batch(task_ids: str = ""):
    """⚡ 批量抢单"""
    import sys
    sys.path.insert(0, '/home/goose/.openclaw/workspace/openclaw-workspace/GO2SE_PLATFORM/versions/v6/strategies')
    from work_radar import get_work_radar
    try:
        radar = get_work_radar()
        ids = task_ids.split(",") if task_ids else []
        result = radar.snipe_batch(ids)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ─── 声纳 + 增强策略路由 ─────────────────────────────────
@router.get("/sonar/ping")
async def sonar_ping(symbol: str = "BTC", price: float = 50000, volume: float = 10000000, change_24h: float = 0, change_7d: float = 0, change_30d: float = 0):
    """🔊 声纳扫描市场"""
    import sys
    sys.path.insert(0, '/home/goose/.openclaw/workspace/openclaw-workspace/GO2SE_PLATFORM/versions/v6/strategies')
    from market_sonar import get_sonar_model
    try:
        sonar = get_sonar_model()
        result = sonar.ping({
            "symbol": symbol, "price": price, "volume": volume,
            "change_24h": change_24h, "change_7d": change_7d, "change_30d": change_30d
        })
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/enhanced/rabbit/review")
async def enhanced_rabbit_review(symbol: str = "BTC", price: float = 50000, volume: float = 10000000, change_24h: float = 0, change_7d: float = 0, change_30d: float = 0):
    """🐰 增强打兔子 - 复盘+仿真"""
    import sys
    sys.path.insert(0, '/home/goose/.openclaw/workspace/openclaw-workspace/GO2SE_PLATFORM/versions/v6/strategies')
    from market_sonar import get_enhanced_rabbit
    try:
        strategy = get_enhanced_rabbit()
        result = strategy.review_and_simulate({
            "symbol": symbol, "price": price, "volume": volume,
            "change_24h": change_24h, "change_7d": change_7d, "change_30d": change_30d
        })
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/enhanced/mole/review")
async def enhanced_mole_review(symbol: str = "BTC", price: float = 50000, volume: float = 10000000, change_24h: float = 0, change_7d: float = 0, change_30d: float = 0):
    """🐹 增强打地鼠 - 复盘+仿真"""
    import sys
    sys.path.insert(0, '/home/goose/.openclaw/workspace/openclaw-workspace/GO2SE_PLATFORM/versions/v6/strategies')
    from market_sonar import get_enhanced_mole
    try:
        strategy = get_enhanced_mole()
        result = strategy.review_and_simulate({
            "symbol": symbol, "price": price, "volume": volume,
            "change_24h": change_24h, "change_7d": change_7d, "change_30d": change_30d
        })
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/enhanced/weights")
async def get_weights(type: str = "rabbit"):
    """⚙️ 获取加权因子"""
    import sys
    sys.path.insert(0, '/home/goose/.openclaw/workspace/openclaw-workspace/GO2SE_PLATFORM/versions/v6/strategies')
    from market_sonar import get_enhanced_rabbit, get_enhanced_mole
    try:
        if type == "mole":
            strategy = get_enhanced_mole()
        else:
            strategy = get_enhanced_rabbit()
        return {"success": True, "data": {"weights": strategy.weights}}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ─── 脑系统 v2.0 路由 ─────────────────────────────────────────
@router.get("/brain/v2/status")
async def brain_v2_status():
    """🧠 脑系统完整状态"""
    import sys
    sys.path.insert(0, '/home/goose/.openclaw/workspace/openclaw-workspace/GO2SE_PLATFORM/versions/v6/strategies')
    from brain_architecture import get_status
    try:
        return {"success": True, "data": get_status()}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/brain/v2/decide")
async def brain_v2_decide(mi: float = 0.65, price: float = 50000, change_24h: float = 0, rsi: float = 50, volume_ratio: float = 1.0):
    """🧠 左右脑决策"""
    import sys
    sys.path.insert(0, '/home/goose/.openclaw/workspace/openclaw-workspace/GO2SE_PLATFORM/versions/v6/strategies')
    from brain_architecture import decide_brain
    try:
        result = decide_brain({
            "mi": mi, "price": price, "change_24h": change_24h,
            "rsi": rsi, "volume_ratio": volume_ratio
        })
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/brain/v2/switch/brain")
async def brain_v2_switch_brain(mode: str = None):
    """🔄 切换脑半球"""
    import sys
    sys.path.insert(0, '/home/goose/.openclaw/workspace/openclaw-workspace/GO2SE_PLATFORM/versions/v6/strategies')
    from brain_architecture import switch_brain
    try:
        return {"success": True, "data": switch_brain(mode)}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/brain/v2/switch/agent")
async def brain_v2_switch_agent(agent: str = None):
    """🔄 切换Agent (OpenClaw/Hermes)"""
    import sys
    sys.path.insert(0, '/home/goose/.openclaw/workspace/openclaw-workspace/GO2SE_PLATFORM/versions/v6/strategies')
    from brain_architecture import switch_agent
    try:
        return {"success": True, "data": switch_agent(agent)}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/brain/v2/improve")
async def brain_v2_improve():
    """🔧 自主迭代"""
    import sys
    sys.path.insert(0, '/home/goose/.openclaw/workspace/openclaw-workspace/GO2SE_PLATFORM/versions/v6/strategies')
    from brain_architecture import self_improve
    try:
        return {"success": True, "data": self_improve()}
    except Exception as e:
        return {"success": False, "error": str(e)}
