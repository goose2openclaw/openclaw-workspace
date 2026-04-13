#!/usr/bin/env python3
"""
🪿 GO2SE 备选策略路由
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json

router = APIRouter(prefix="/api/alternatives", tags=["备选策略"])


class EnableStrategyRequest(BaseModel):
    strategy_id: str
    allocation: float = 0.1
    priority: int = 5
    capital_ratio: float = 0.1


@router.get("/strategies")
async def get_strategies():
    """获取所有备选策略"""
    try:
        with open("/root/.openclaw/workspace/GO2SE_PLATFORM/versions/v6/alternative_strategies.json", "r") as f:
            config = json.load(f)
    except:
        config = {"expert_mode": False, "strategies": {}}
    
    strategies = []
    for sid, sdata in config.get("strategies", {}).items():
        strategies.append({
            "id": sid,
            "name": sdata.get("name", sid),
            "type": sdata.get("type", "quant"),
            "description": sdata.get("description", ""),
            "source": sdata.get("source", "local"),
            "enabled": sdata.get("enabled", False),
            "allocation": sdata.get("allocation", 0.0),
            "priority": sdata.get("priority", 5),
            "capital_ratio": sdata.get("capital_ratio", 0.0)
        })
    
    return {
        "timestamp": datetime.now().isoformat(),
        "expert_mode": config.get("expert_mode", False),
        "strategies": strategies,
        "enabled_count": sum(1 for s in strategies if s["enabled"]),
        "total_allocation": sum(s["allocation"] for s in strategies if s["enabled"])
    }


@router.post("/enable")
async def enable_strategy(request: EnableStrategyRequest):
    """启用备选策略"""
    try:
        with open("/root/.openclaw/workspace/GO2SE_PLATFORM/versions/v6/alternative_strategies.json", "r") as f:
            config = json.load(f)
    except:
        return {"success": False, "message": "配置不存在"}
    
    if request.strategy_id not in config.get("strategies", {}):
        return {"success": False, "message": f"策略 {request.strategy_id} 不存在"}
    
    config["strategies"][request.strategy_id].update({
        "enabled": True,
        "allocation": request.allocation,
        "priority": request.priority,
        "capital_ratio": request.capital_ratio
    })
    
    with open("/root/.openclaw/workspace/GO2SE_PLATFORM/versions/v6/alternative_strategies.json", "w") as f:
        json.dump(config, f, indent=2)
    
    return {
        "success": True, 
        "message": f"已启用 {config['strategies'][request.strategy_id]['name']}",
        "strategy": config["strategies"][request.strategy_id]
    }


@router.post("/disable")
async def disable_strategy(strategy_id: str):
    """禁用策略"""
    try:
        with open("/root/.openclaw/workspace/GO2SE_PLATFORM/versions/v6/alternative_strategies.json", "r") as f:
            config = json.load(f)
    except:
        return {"success": False, "message": "配置不存在"}
    
    if config.get("strategies", {}).get(strategy_id):
        config["strategies"][strategy_id]["enabled"] = False
        with open("/root/.openclaw/workspace/GO2SE_PLATFORM/versions/v6/alternative_strategies.json", "w") as f:
            json.dump(config, f, indent=2)
        return {"success": True, "message": f"已禁用 {strategy_id}"}
    
    return {"success": False, "message": "策略不存在"}


@router.post("/expert-mode")
async def set_expert_mode(enabled: bool):
    """设置专家模式"""
    try:
        with open("/root/.openclaw/workspace/GO2SE_PLATFORM/versions/v6/alternative_strategies.json", "r") as f:
            config = json.load(f)
    except:
        config = {"expert_mode": False, "strategies": {}}
    
    config["expert_mode"] = enabled
    
    with open("/root/.openclaw/workspace/GO2SE_PLATFORM/versions/v6/alternative_strategies.json", "w") as f:
        json.dump(config, f, indent=2)
    
    return {"success": True, "expert_mode": enabled}


@router.get("/run/{strategy_id}")
async def run_strategy(strategy_id: str, symbol: str = "BTC/USDT"):
    """测试运行单个策略"""
    from app.core.local_strategies import AlternativeStrategyEngine, MarketData
    import random
    
    engine = AlternativeStrategyEngine()
    
    # 生成模拟数据
    base_price = 75000 if "BTC" in symbol else 2000
    candles = []
    for i in range(30 * 24):
        ts = datetime.now().timestamp() - (30 * 24 - i) * 3600
        price = base_price * (1 + random.gauss(0, 0.02))
        candles.append(MarketData(
            symbol=symbol,
            timestamp=datetime.fromtimestamp(ts).isoformat(),
            open=price * 0.99,
            high=price * 1.02,
            low=price * 0.98,
            close=price,
            volume=random.uniform(100, 1000)
        ))
    
    result = engine.run_strategy(strategy_id, candles)
    result["timestamp"] = datetime.now().isoformat()
    
    return result


@router.get("/backtest")
async def backtest_all(
    symbols: str = "BTC/USDT,ETH/USDT",
    days: int = 30,
    initial_cash: float = 100000
):
    """回测所有启用的策略"""
    from app.core.backtest_engine import BacktestEngine
    import random
    
    symbol_list = [s.strip() for s in symbols.split(",")]
    
    # 获取启用的策略
    try:
        with open("/root/.openclaw/workspace/GO2SE_PLATFORM/versions/v6/alternative_strategies.json", "r") as f:
            config = json.load(f)
    except:
        config = {"strategies": {}}
    
    enabled = [
        sid for sid, s in config.get("strategies", {}).items() 
        if s.get("enabled", False)
    ]
    
    if not enabled:
        # 如果没有启用的，默认测试所有
        enabled = ["lean_rsi", "lean_macd", "bollinger_bands", "ml_ensemble"]
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "config": {
            "symbols": symbol_list,
            "days": days,
            "initial_cash": initial_cash,
            "strategies": enabled
        },
        "results": {}
    }
    
    for strat_id in enabled:
        engine = BacktestEngine(initial_cash=initial_cash, fee_rate=0.001)
        try:
            result = engine.run_strategy(strat_id, symbol_list, days)
            results["results"][strat_id] = result
        except Exception as e:
            results["results"][strat_id] = {"error": str(e)}
    
    # 排序
    rankings = sorted(
        [(k, v.get("return_pct", 0), v.get("max_drawdown_pct", 0)) 
         for k, v in results["results"].items() if "error" not in v],
        key=lambda x: x[1],
        reverse=True
    )
    results["rankings"] = [
        {"strategy": r[0], "return_pct": r[1], "max_drawdown_pct": r[2]} 
        for r in rankings
    ]
    
    return results


@router.get("/compare")
async def compare_all():
    """对比所有策略 (平台+备选)"""
    from app.core.backtest_engine import BacktestEngine
    import random
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "strategies": {}
    }
    
    # 1. 平台策略 (理论预期)
    results["strategies"]["platform_beidou7xin"] = {
        "name": "北斗七鑫 (平台)",
        "source": "platform",
        "return_pct": 10.0,
        "max_drawdown_pct": 13.39,
        "note": "理论预期"
    }
    
    # 2. 备选策略 (实际回测)
    alt_strategies = ["lean_rsi", "lean_macd", "bollinger_bands", "ml_ensemble"]
    for strat in alt_strategies:
        engine = BacktestEngine(initial_cash=100000, fee_rate=0.001)
        try:
            r = engine.run_strategy(strat, ["BTC/USDT"], 30)
            results["strategies"][strat] = {
                "name": strat.replace("_", " ").title(),
                "source": "alternative",
                "return_pct": r.get("return_pct", 0),
                "max_drawdown_pct": r.get("max_drawdown_pct", 0),
                "win_rate": r.get("win_rate", 0),
                "total_trades": r.get("total_trades", 0)
            }
        except:
            pass
    
    # 排序
    ranked = sorted(
        results["strategies"].items(),
        key=lambda x: x[1].get("return_pct", 0),
        reverse=True
    )
    results["rankings"] = [
        {"id": k, **v} for k, v in ranked
    ]
    
    return results
