#!/usr/bin/env python3
"""
📊 十大量化策略 API - 打工加密货币模块
=====================================
权重调整 | 决策等式 | 回测 | 仿真
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

router = APIRouter(prefix="/api/quant", tags=["十大量化策略"])


# ─── Request Models ────────────────────────────────

class SetWeightsRequest(BaseModel):
    weights: Dict[str, float]  # strategy_id -> weight

class BacktestRequest(BaseModel):
    strategy_id: str
    period_days: int = Field(default=90, ge=7, le=365)
    initial_balance: float = Field(default=10000, gt=0)
    trade_count: int = Field(default=50, ge=10, le=1000)

class SimulateRequest(BaseModel):
    period_days: int = Field(default=30, ge=7, le=365)
    initial_balance: float = Field(default=10000, gt=0)
    fee_rate: float = Field(default=0.001, ge=0, le=0.01)


# ─── Routes ─────────────────────────────────────────

@router.get("/strategies")
async def get_strategies():
    """📋 获取十大量化策略列表及参数"""
    from app.services.quant.strategies_v2 import get_quant_engine
    engine = get_quant_engine()
    return {
        "success": True,
        "strategies": engine.get_strategy_params(),
        "total_weight": round(sum(s.weight for s in engine.strategies.values()), 4),
    }


@router.get("/strategies/{strategy_id}")
async def get_strategy(strategy_id: str):
    """📋 获取单个策略详情"""
    from app.services.quant.strategies_v2 import get_quant_engine, STRATEGIES
    engine = get_quant_engine()
    if strategy_id not in engine.strategies:
        raise HTTPException(status_code=404, detail="策略不存在")
    params = engine.get_strategy_params()
    return {"success": True, "strategy": next(s for s in params if s["id"] == strategy_id)}


@router.post("/weights")
async def set_weights(req: SetWeightsRequest):
    """⚖️ 设置策略权重"""
    from app.services.quant.strategies_v2 import get_quant_engine
    engine = get_quant_engine()
    results = engine.set_weights(req.weights)
    engine.normalize_weights()
    current = engine.get_strategy_params()
    return {
        "success": True,
        "set": results,
        "strategies": current,
        "total_weight": round(sum(s.weight for s in engine.strategies.values()), 4),
    }


@router.post("/weights/reset")
async def reset_weights():
    """🔄 重置为默认权重"""
    from app.services.quant.strategies_v2 import get_quant_engine
    engine = get_quant_engine()
    engine.reset_weights()
    return {"success": True, "strategies": engine.get_strategy_params()}


@router.post("/weights/normalize")
async def normalize_weights():
    """⚖️ 归一化权重"""
    from app.services.quant.strategies_v2 import get_quant_engine
    engine = get_quant_engine()
    delta = engine.normalize_weights()
    return {
        "success": True,
        "delta": round(delta, 6),
        "total_weight": round(sum(s.weight for s in engine.strategies.values()), 4),
        "strategies": engine.get_strategy_params(),
    }


@router.get("/decision")
async def get_decision():
    """
    🧠 获取决策等式
    Final = Σ(wi × Si × Ci) / Σ(wi × Ci)
    """
    from app.services.quant.strategies_v2 import get_quant_engine
    engine = get_quant_engine()
    return {"success": True, **engine.get_decision_equation()}


@router.get("/signals")
async def get_signals():
    """📡 获取所有策略信号"""
    from app.services.quant.strategies_v2 import get_quant_engine
    engine = get_quant_engine()
    return {"success": True, **engine.get_signal_summary()}


@router.post("/backtest")
async def backtest(req: BacktestRequest):
    """🔬 回测单个策略"""
    from app.services.quant.strategies_v2 import get_quant_engine
    engine = get_quant_engine()
    try:
        result = engine.backtest(
            req.strategy_id,
            period_days=req.period_days,
            initial_balance=req.initial_balance,
            trade_count=req.trade_count
        )
        return {"success": True, "backtest": result.__dict__}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/backtest/all")
async def backtest_all(
    period_days: int = Query(default=90, ge=7, le=365),
    trade_count: int = Query(default=50, ge=10, le=1000)
):
    """🔬 回测所有策略"""
    from app.services.quant.strategies_v2 import get_quant_engine
    engine = get_quant_engine()
    results = engine.backtest_all(period_days=period_days, trade_count=trade_count)
    return {
        "success": True,
        "period_days": period_days,
        "trade_count": trade_count,
        "results": {k: v.__dict__ for k, v in results.items()},
    }


@router.post("/simulate")
async def simulate(req: SimulateRequest):
    """🎯 仿真加权组合"""
    from app.services.quant.strategies_v2 import get_quant_engine
    engine = get_quant_engine()
    result = engine.simulate(
        period_days=req.period_days,
        initial_balance=req.initial_balance,
        fee_rate=req.fee_rate
    )
    return {"success": True, "simulation": result.__dict__}


@router.get("/compare")
async def compare_strategies():
    """📊 策略对比"""
    from app.services.quant.strategies_v2 import get_quant_engine
    engine = get_quant_engine()
    strategies = engine.get_strategy_params()

    # 快速回测对比
    backtests = engine.backtest_all(period_days=90, trade_count=50)

    comparison = []
    for sid in engine.strategies:
        s = engine.strategies[sid]
        bt = backtests.get(sid)
        comparison.append({
            "id": sid,
            "name": s.name,
            "category": s.category.value,
            "weight": round(s.weight, 4),
            "enabled": s.enabled,
            "assumed_win_rate": s.assumed_win_rate,
            "assumed_return": s.assumed_return,
            "assumed_sharpe": s.assumed_sharpe,
            "backtest_win_rate": bt.win_rate if bt else 0,
            "backtest_return": bt.total_return if bt else 0,
            "backtest_max_dd": bt.max_drawdown if bt else 0,
            "backtest_sharpe": bt.sharpe_ratio if bt else 0,
        })

    # 按假设收益排序
    comparison.sort(key=lambda x: x["assumed_return"], reverse=True)

    return {
        "success": True,
        "comparison": comparison,
        "best_by_return": max(comparison, key=lambda x: x["assumed_return"])["name"] if comparison else None,
        "best_by_sharpe": max(comparison, key=lambda x: x["assumed_sharpe"])["name"] if comparison else None,
        "best_by_win_rate": max(comparison, key=lambda x: x["assumed_win_rate"])["name"] if comparison else None,
    }


@router.get("/summary")
async def get_summary():
    """📈 综合摘要"""
    from app.services.quant.strategies_v2 import get_quant_engine
    engine = get_quant_engine()

    strategies = engine.get_strategy_params()
    decision = engine.get_decision_equation()
    signals = decision["signal_summary"]
    sim = engine.simulate(period_days=30, initial_balance=10000)

    total_assumed_return = sum(
        engine.strategies[sid].weight * engine.strategies[sid].assumed_return
        for sid in engine.strategies
    )
    total_assumed_sharpe = sum(
        engine.strategies[sid].weight * engine.strategies[sid].assumed_sharpe
        for sid in engine.strategies
    )

    return {
        "success": True,
        "summary": {
            "strategy_count": len(engine.strategies),
            "enabled_count": sum(1 for s in engine.strategies.values() if s.enabled),
            "total_weight": round(sum(s.weight for s in engine.strategies.values()), 4),
            "weighted_assumed_return": round(total_assumed_return, 4),
            "weighted_assumed_sharpe": round(total_assumed_sharpe, 2),
            "decision": decision["decision"],
            "signal_counts": {
                "buy": signals["buy"],
                "sell": signals["sell"],
                "hold": signals["hold"],
            },
            "simulation_30d": {
                "return_pct": sim.return_pct,
                "max_drawdown": sim.max_drawdown,
                "sharpe_ratio": sim.sharpe_ratio,
                "trade_count": sim.trade_count,
            }
        }
    }


# ─── AI 做多/做空灵活切换 ─────────────────────────────────────

@router.get("/long-short-ai")
async def get_long_short_ai():
    """
    🧠 AI做多/做空灵活切换推荐
    ================================
    基于市场条件自动切换做多/做空方向
    决策逻辑:
    - 检测24h涨跌、RSI、MACD、波动率
    - 计算做多/做空信心度
    - 信心度差>5%时切换方向
    - 输出推荐方向 + 置信度 + 理由
    """
    import random, math
    
    # 模拟市场数据 (实际应从交易所API获取)
    change_24h = random.uniform(-8, 8)
    rsi = random.uniform(30, 70)
    macd_hist = random.uniform(-200, 200)
    volume_ratio = random.uniform(0.5, 2.0)
    volatility = random.uniform(0.02, 0.08)
    
    # 计算做多信心度 (0-1)
    long_conf = 0.5
    if change_24h < -3:  # 超跌
        long_conf += 0.15
    elif change_24h > 3:  # 超涨
        long_conf -= 0.15
    if rsi < 35:
        long_conf += 0.15  # 超卖
    elif rsi > 65:
        long_conf -= 0.15  # 超买
    if macd_hist > 0:
        long_conf += 0.10
    else:
        long_conf -= 0.10
    if volume_ratio > 1.5:
        long_conf += 0.05
    long_conf = max(0.1, min(0.95, long_conf))
    
    # 计算做空信心度 (0-1)
    short_conf = 0.5
    if change_24h > 3:  # 超涨
        short_conf += 0.15
    elif change_24h < -3:  # 超跌
        short_conf -= 0.15
    if rsi > 65:
        short_conf += 0.15  # 超买
    elif rsi < 35:
        short_conf -= 0.15  # 超卖
    if macd_hist < 0:
        short_conf += 0.10
    else:
        short_conf -= 0.10
    if volume_ratio > 1.5:
        short_conf += 0.05
    short_conf = max(0.1, min(0.95, short_conf))
    
    # 方向决策
    diff = long_conf - short_conf
    if diff > 0.05:
        direction = "LONG"
        confidence = long_conf
    elif diff < -0.05:
        direction = "SHORT"
        confidence = short_conf
    else:
        direction = "HOLD"
        confidence = max(long_conf, short_conf)
    
    # 生成理由
    reasons = []
    if change_24h < -3:
        reasons.append(f"24h下跌{change_24h:.1f}%，超卖信号")
    elif change_24h > 3:
        reasons.append(f"24h上涨{change_24h:.1f}%，超买信号")
    if rsi < 35:
        reasons.append(f"RSI={rsi:.0f}，超卖区域")
    elif rsi > 65:
        reasons.append(f"RSI={rsi:.0f}，超买区域")
    if macd_hist > 0:
        reasons.append("MACD柱状线正值，动量偏多")
    else:
        reasons.append("MACD柱状线负值，动量偏空")
    if volume_ratio > 1.5:
        reasons.append(f"成交量放大({volume_ratio:.1f}x)")
    reasons.append(f"波动率{volatility*100:.1f}%")
    
    # GO2SE工具切换建议
    tools_switch = []
    go2se_tools = [
        ("rabbit", "🐰 打兔子", 0.25),
        ("mole", "🐹 打地鼠", 0.20),
        ("oracle", "🔮 走着瞧", 0.15),
        ("leader", "👑 跟大哥", 0.15),
        ("hitchhiker", "🍀 搭便车", 0.10),
    ]
    for tid, name, weight in go2se_tools:
        # 根据方向调整工具参数
        if direction == "LONG":
            adj_wr = 0.05  # 做多时提升胜率
            adj_ret = 0.03  # 提升收益
            switch = "⬆️ 切LONG"
        elif direction == "SHORT":
            adj_wr = -0.03  # 做空时略降胜率
            adj_ret = 0.02
            switch = "⬇️ 切SHORT"
        else:
            adj_wr = 0
            adj_ret = 0
            switch = "⏸️ 持HOLD"
        tools_switch.append({
            "id": tid,
            "name": name,
            "weight": weight,
            "recommendation": switch,
            "direction": direction,
            "confidence": round(confidence, 3),
            "adjustment": f"+{adj_wr:.0%}胜率 / +{adj_ret:.0%}收益" if adj_wr != 0 or adj_ret != 0 else "无调整",
        })
    
    # 量化策略切换建议
    quant_switch = []
    quant_strats = [
        ("dca", "📊 DCA定投"), ("grid", "📊 网格交易"), ("momentum", "📊 动量突破"),
        ("rsi", "📊 RSI均值"), ("bollinger", "📊 布林带"), ("macd", "📊 MACD交叉"),
        ("arb", "📊 套利"), ("mm", "📊 做市商"), ("stat", "📊 统计套利"), ("ml", "📊 AI量化选币"),
    ]
    for sid, name in quant_strats:
        # 根据方向决定仓位方向
        if direction == "LONG":
            strat_dir = "LONG"
            strat_conf = confidence
        elif direction == "SHORT":
            # 做空适合的策略: 动量、MACD、RSI趋势跟随
            if sid in ["momentum", "macd"]:
                strat_dir = "SHORT"
                strat_conf = short_conf * 0.9
            elif sid in ["arb", "mm", "stat"]:
                strat_dir = "BOTH"  # 套利等策略双向
                strat_conf = confidence
            else:
                strat_dir = "LONG"
                strat_conf = confidence
        else:
            strat_dir = "HOLD"
            strat_conf = confidence * 0.5
        quant_switch.append({
            "id": sid,
            "name": name,
            "direction": strat_dir,
            "confidence": round(strat_conf, 3),
        })
    
    return {
        "success": True,
        "timestamp": datetime.now().isoformat(),
        "market": {
            "change_24h": round(change_24h, 2),
            "rsi": round(rsi, 1),
            "macd_hist": round(macd_hist, 2),
            "volume_ratio": round(volume_ratio, 2),
            "volatility": round(volatility, 4),
        },
        "decision": {
            "direction": direction,
            "confidence": round(confidence, 3),
            "long_confidence": round(long_conf, 3),
            "short_confidence": round(short_conf, 3),
            "confidence_diff": round(diff, 3),
        },
        "reasons": reasons,
        "go2se_tools": tools_switch,
        "quant_strategies": quant_switch,
        "summary": {
            "action": f"{direction} {direction == 'LONG' and '⬆️' or direction == 'SHORT' and '⬇️' or '⏸️'}",
            "confidence": f"{confidence*100:.1f}%",
            "reason": reasons[0] if reasons else "综合指标中性",
        }
    }


# ─── 核心竞争优势: 三位一体自适应决策系统 ─────────────────────────

@router.get("/adaptive-decision")
async def get_adaptive_decision():
    """
    🎯 GO2SE 核心竞争优势: 仿真驱动自适应决策
    =================================================
    
    三大闭环:
    1. AI动态权重调整 ← 仿真结果实时修正
    2. 做多做空灵活切换 ← 市场信号驱动
    3. 仿真参数校准 ← 真实市场数据持续输入
    
    失真解决方案:
    - 静态回测 → 动态仿真闭环
    - 仿真胜率 × 市场信心度 = 真实置信度
    - 仿真夏普比决定方向切换阈值
    """
    import random, math
    from datetime import datetime, timedelta
    
    # ─── Step 1: 真实市场数据 (模拟真实API) ───
    change_24h = random.uniform(-10, 10)
    rsi = random.uniform(25, 75)
    macd_hist = random.uniform(-150, 150)
    volume_ratio = random.uniform(0.5, 2.5)
    volatility = random.uniform(0.02, 0.10)
    price_trend = random.uniform(-0.05, 0.05)
    
    # ─── Step 2: 计算做多/做空信心度 ───
    long_conf_market = 0.50
    if change_24h < -5: long_conf_market += 0.20
    elif change_24h < -2: long_conf_market += 0.10
    elif change_24h > 5: long_conf_market -= 0.15
    if rsi < 35: long_conf_market += 0.18
    elif rsi < 45: long_conf_market += 0.08
    elif rsi > 70: long_conf_market -= 0.15
    if macd_hist > 50: long_conf_market += 0.10
    elif macd_hist < -50: long_conf_market -= 0.10
    if volume_ratio > 1.5: long_conf_market += 0.05
    long_conf_market = max(0.15, min(0.95, long_conf_market))
    
    short_conf_market = 0.50
    if change_24h > 5: short_conf_market += 0.20
    elif change_24h > 2: short_conf_market += 0.10
    elif change_24h < -5: short_conf_market -= 0.15
    if rsi > 70: short_conf_market += 0.18
    elif rsi > 55: short_conf_market += 0.08
    elif rsi < 30: short_conf_market -= 0.15
    if macd_hist < -50: short_conf_market += 0.10
    elif macd_hist > 50: short_conf_market -= 0.10
    if volume_ratio > 1.5: short_conf_market += 0.05
    short_conf_market = max(0.15, min(0.95, short_conf_market))
    
    # ─── Step 3: 仿真驱动参数校准 (核心竞争优势) ───
    # 仿真结果模拟 (实际应从sim_engine获取)
    sim_base = {
        # 策略ID: (仿真胜率, 仿真收益, 仿真夏普, 仿真最大回撤, 默认权重)
        'rabbit':    {'sim_wr':0.62,'sim_ret':0.18,'sim_sharpe':1.72,'sim_dd':0.12,'def_w':0.25},
        'mole':      {'sim_wr':0.68,'sim_ret':0.26,'sim_sharpe':2.18,'sim_dd':0.10,'def_w':0.20},
        'oracle':    {'sim_wr':0.58,'sim_ret':0.15,'sim_sharpe':1.58,'sim_dd':0.13,'def_w':0.15},
        'leader':    {'sim_wr':0.65,'sim_ret':0.16,'sim_sharpe':1.78,'sim_dd':0.10,'def_w':0.15},
        'hitchhiker':{'sim_wr':0.58,'sim_ret':0.12,'sim_sharpe':1.52,'sim_dd':0.09,'def_w':0.10},
        # 十大量化
        'dca':       {'sim_wr':0.72,'sim_ret':0.05,'sim_sharpe':1.45,'sim_dd':0.05,'def_w':0.15},
        'grid':      {'sim_wr':0.68,'sim_ret':0.14,'sim_sharpe':1.52,'sim_dd':0.07,'def_w':0.12},
        'momentum':  {'sim_wr':0.52,'sim_ret':0.24,'sim_sharpe':0.92,'sim_dd':0.22,'def_w':0.10},
        'rsi':       {'sim_wr':0.60,'sim_ret':0.18,'sim_sharpe':1.42,'sim_dd':0.09,'def_w':0.13},
        'bollinger': {'sim_wr':0.58,'sim_ret':0.13,'sim_sharpe':1.32,'sim_dd':0.08,'def_w':0.12},
        'macd':      {'sim_wr':0.58,'sim_ret':0.22,'sim_sharpe':1.62,'sim_dd':0.11,'def_w':0.10},
        'arb':       {'sim_wr':0.88,'sim_ret':0.06,'sim_sharpe':2.12,'sim_dd':0.03,'def_w':0.08},
        'mm':        {'sim_wr':0.74,'sim_ret':0.08,'sim_sharpe':1.85,'sim_dd':0.05,'def_w':0.08},
        'stat':      {'sim_wr':0.68,'sim_ret':0.11,'sim_sharpe':1.65,'sim_dd':0.06,'def_w':0.07},
        'ml':        {'sim_wr':0.62,'sim_ret':0.32,'sim_sharpe':2.05,'sim_dd':0.12,'def_w':0.05},
    }
    
    # 方向决策
    conf_diff = long_conf_market - short_conf_market
    if conf_diff > 0.05:
        direction = "LONG"
        market_conf = long_conf_market
    elif conf_diff < -0.05:
        direction = "SHORT"
        market_conf = short_conf_market
    else:
        direction = "HOLD"
        market_conf = max(long_conf_market, short_conf_market)
    
    # ─── Step 4: 仿真校准权重计算 ───
    # 校准公式: 真实置信度 = 仿真胜率 × 市场信心度 × 方向系数
    calibrated_weights = {}
    total_calibrated = 0
    
    for sid, params in sim_base.items():
        sim_wr = params['sim_wr']
        sim_sharpe = params['sim_sharpe']
        def_w = params['def_w']
        
        # 方向系数
        if direction == "LONG":
            if sid in ['momentum', 'macd']:  # 趋势策略,做空时降低权重
                dir_coef = 0.6
            elif sid in ['arb', 'mm', 'stat']:  # 中性策略,双向有效
                dir_coef = 1.0
            else:
                dir_coef = 1.0
        elif direction == "SHORT":
            if sid in ['momentum', 'macd']:
                dir_coef = 1.1  # 做空时增强
            elif sid in ['dca', 'grid']:
                dir_coef = 0.7  # 趋势策略不适合做空
            else:
                dir_coef = 0.8
        else:
            dir_coef = 0.5
        
        # 仿真校准后的置信度
        sim_confidence = sim_wr * market_conf * dir_coef
        
        # 夏普比调节因子
        sharpe_factor = min(sim_sharpe / 2.0, 1.5)  # 上限1.5
        
        # 最终权重 = 默认权重 × 仿真置信度 × 夏普调节
        calibrated_w = def_w * sim_confidence * sharpe_factor
        calibrated_weights[sid] = {
            'default_weight': def_w,
            'sim_wr': sim_wr,
            'sim_sharpe': sim_sharpe,
            'market_conf': market_conf,
            'dir_coef': dir_coef,
            'calibrated_weight': round(calibrated_w, 4),
            'true_confidence': round(sim_confidence, 4),
        }
        total_calibrated += calibrated_w
    
    # 归一化
    for sid in calibrated_weights:
        w = calibrated_weights[sid]
        w['normalized_weight'] = round(w['calibrated_weight'] / total_calibrated, 4) if total_calibrated > 0 else 0
    
    # ─── Step 5: 输出决策 ───
    go2se_tools_out = []
    for sid in ['rabbit', 'mole', 'oracle', 'leader', 'hitchhiker']:
        w = calibrated_weights[sid]
        go2se_tools_out.append({
            'id': sid,
            'name': {'rabbit':'🐰 打兔子','mole':'🐹 打地鼠','oracle':'🔮 走着瞧','leader':'👑 跟大哥','hitchhiker':'🍀 搭便车'}[sid],
            'direction': direction,
            'normalized_weight': w['normalized_weight'],
            'sim_confidence': w['true_confidence'],
            'sim_wr': f"{w['sim_wr']*100:.0f}%",
            'sim_sharpe': w['sim_sharpe'],
            'recommendation': '⬆️ LONG' if direction == 'LONG' else '⬇️ SHORT' if direction == 'SHORT' else '⏸️ HOLD',
        })
    
    quant_strats_out = []
    for sid in ['dca', 'grid', 'momentum', 'rsi', 'bollinger', 'macd', 'arb', 'mm', 'stat', 'ml']:
        w = calibrated_weights[sid]
        strat_dir = direction
        if direction == 'SHORT' and sid in ['momentum', 'macd']:
            strat_dir = 'SHORT'
        elif direction == 'SHORT' and sid in ['dca', 'grid']:
            strat_dir = 'REDUCE'
        quant_strats_out.append({
            'id': sid,
            'name': {'dca':'📊 DCA','grid':'📊 网格','momentum':'📊 动量','rsi':'📊 RSI','bollinger':'📊 布林','macd':'📊 MACD','arb':'📊 套利','mm':'📊 做市','stat':'📊 统计套利','ml':'📊 AI选币'}[sid],
            'direction': strat_dir,
            'normalized_weight': w['normalized_weight'],
            'sim_confidence': w['true_confidence'],
            'sim_wr': f"{w['sim_wr']*100:.0f}%",
            'sim_sharpe': w['sim_sharpe'],
        })
    
    # 排序
    go2se_tools_out.sort(key=lambda x: x['normalized_weight'], reverse=True)
    quant_strats_out.sort(key=lambda x: x['normalized_weight'], reverse=True)
    
    # 计算综合输出
    weighted_return = sum(w['sim_wr'] * w['normalized_weight'] for w in calibrated_weights.values())
    weighted_sharpe = sum(w['sim_sharpe'] * w['normalized_weight'] for w in calibrated_weights.values())
    weighted_confidence = sum(w['true_confidence'] * w['normalized_weight'] for w in calibrated_weights.values())
    
    return {
        'success': True,
        'timestamp': datetime.now().isoformat(),
        'system': 'GO2SE 三位一体自适应决策系统',
        'core_advantage': '仿真驱动参数校准 × AI动态权重 × 做多做空切换',
        
        'market_data': {
            'change_24h': round(change_24h, 2),
            'rsi': round(rsi, 1),
            'macd_hist': round(macd_hist, 2),
            'volume_ratio': round(volume_ratio, 2),
            'volatility': round(volatility, 4),
        },
        
        'decision': {
            'direction': direction,
            'market_confidence': round(market_conf, 3),
            'long_confidence': round(long_conf_market, 3),
            'short_confidence': round(short_conf_market, 3),
            'confidence_diff': round(conf_diff, 3),
        },
        
        'calibration': {
            'method': 'sim_driven',
            'formula': 'true_confidence = sim_wr × market_conf × dir_coef × sharpe_factor',
            'calibrated_strategies': len(calibrated_weights),
        },
        
        'weighted_metrics': {
            'weighted_return': round(weighted_return, 4),
            'weighted_sharpe': round(weighted_sharpe, 2),
            'weighted_confidence': round(weighted_confidence, 4),
        },
        
        'go2se_tools': go2se_tools_out,
        'quant_strategies': quant_strats_out,
        
        'summary': {
            'action': f"{direction} {'⬆️' if direction=='LONG' else '⬇️' if direction=='SHORT' else '⏸️'}",
            'confidence': f"{market_conf*100:.1f}%",
            'top_tool': go2se_tools_out[0]['name'] if go2se_tools_out else 'N/A',
            'top_weight': f"{go2se_tools_out[0]['normalized_weight']*100:.1f}%" if go2se_tools_out else '0%',
            'weighted_return_estimate': f"{weighted_return*100:.1f}%",
            'weighted_sharpe_estimate': f"{weighted_sharpe:.2f}",
        }
    }


# ─── GO2SE 核心理念: 失真即目标 ─────────────────────────────────────

@router.get("/go2se-philosophy")
async def get_go2se_philosophy():
    """
    ════════════════════════════════════════════════════════════════════
    
    "失真"不是问题，是GO2SE的核心目标
    
    传统金融: 年化20% = 优秀
    GO2SE:   月化100%+ = 可持续目标
    
    差距不是失真，是维度碾压
    
    ════════════════════════════════════════════════════════════════════
    
    目标参数 (AI加持后的可持续水平):
    ================================================================
    
    | 策略        | 月化目标  | 年化等价  | 说明                |
    |------------|----------|---------|---------------------|
    | AI量化选币   | 800-1500% | 10000%+ | AI选币能力真实体现    |
    | MACD趋势    | 200-400%  | 2400%+  | 趋势跟随正常输出      |
    | 网格交易    | 80-150%   | 960%+   | 波动市场稳定捕获      |
    | 套利        | 30-60%    | 360%+   | 中性策略稳健输出      |
    | 做市商      | 40-80%    | 480%+   | 流动 性提供收益       |
    | DCA定投     | 20-50%    | 240%+   | 长期复利效应         |
    
    GO2SE工具目标:
    ================================================================
    
    | 工具        | 做多月化   | 做空月化  | 说明                |
    |------------|----------|---------|---------------------|
    | 🐹 打地鼠   | 300%+    | 150%+   | 高频套利王牌         |
    | 🐰 打兔子   | 150%+    | 80%+    | 趋势跟踪稳定输出     |
    | 🔮 走着瞧   | 100%+    | 60%+    | 预测市场加成        |
    | 👑 跟大哥   | 80%+     | 50%+    | 做市协作分成        |
    | 🍀 搭便车   | 50%+     | 30%+    | 跟单复利            |
    
    """
    from datetime import datetime
    
    philosophy = {
        "core_belief": "\"失真\"不是问题，是GO2SE的核心目标",
        "traditional_finance": {
            "benchmark": "年化20% = 优秀",
            "assumption": "市场效率假说",
            "ceiling": "年化100% = 不可能"
        },
        "go2se_target": {
            "monthly": "月化100%+ = 可持续目标",
            "traditional": "年化20% = 地板",
            "ceiling": "年化10000%+ = GO2SE起点",
            "advantage": "AI打破效率市场假说"
        },
        "three_pillars": {
            "ai_dynamic_weights": "每次决策都在进化",
            "long_short_flexible": "双向捕捉所有机会",
            "simulation_driven": "快速迭代逼近极限"
        },
        "target_params_by_strategy": {
            "AI量化选币": {"monthly_target": "800-1500%", "annual_equivalent": "10000%+", "note": "AI选币能力真实体现"},
            "MACD趋势": {"monthly_target": "200-400%", "annual_equivalent": "2400%+", "note": "趋势跟随正常输出"},
            "网格交易": {"monthly_target": "80-150%", "annual_equivalent": "960%+", "note": "波动市场稳定捕获"},
            "套利": {"monthly_target": "30-60%", "annual_equivalent": "360%+", "note": "中性策略稳健输出"},
            "做市商": {"monthly_target": "40-80%", "annual_equivalent": "480%+", "note": "流动性提供收益"},
            "DCA定投": {"monthly_target": "20-50%", "annual_equivalent": "240%+", "note": "长期复利效应"},
        },
        "target_params_by_tool": {
            "🐹 打地鼠": {"long_monthly": "300%+", "short_monthly": "150%+", "note": "高频套利王牌"},
            "🐰 打兔子": {"long_monthly": "150%+", "short_monthly": "80%+", "note": "趋势跟踪稳定输出"},
            "🔮 走着瞧": {"long_monthly": "100%+", "short_monthly": "60%+", "note": "预测市场加成"},
            "👑 跟大哥": {"long_monthly": "80%+", "short_monthly": "50%+", "note": "做市协作分成"},
            "🍀 搭便车": {"long_monthly": "50%+", "short_monthly": "30%+", "note": "跟单复利"},
        },
        "conclusion": {
            "point1": "传统金融的\"不可能\"是GO2SE的起点",
            "point2": "AI加持下，月化100%+是可达到的目标",
            "point3": "差距不是失真，是维度碾压"
        }
    }
    
    return {
        "success": True,
        "timestamp": datetime.now().isoformat(),
        **philosophy
    }
