#!/usr/bin/env python3
"""
🪿 GO2SE 备选策略 API
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json
import random

from app.core.local_strategies import (
    AlternativeStrategyEngine,
    get_available_strategies,
    run_strategy_test,
    TechnicalIndicators,
    MLSignalGenerator
)

router = APIRouter(prefix="/api/alt-strategies", tags=["备选策略"])


class StrategyConfig(BaseModel):
    """策略配置"""
    id: str
    name: str
    type: str
    enabled: bool = False
    allocation: float = 0.0
    priority: int = 5
    capital_ratio: float = 0.0
    description: str = ""
    source: str = "local"


@router.get("/list")
async def list_strategies():
    """获取所有备选策略"""
    strategies = get_available_strategies()
    
    # 加载用户配置
    try:
        with open("/root/.openclaw/workspace/GO2SE_PLATFORM/versions/v6/alternative_strategies.json", "r") as f:
            config = json.load(f)
    except:
        config = {"strategies": {}}
    
    # 合并
    result = {
        "timestamp": datetime.now().isoformat(),
        "strategies": [],
        "enabled_count": 0,
        "expert_mode": config.get("expert_mode", False)
    }
    
    for sid, sdata in strategies["strategies"].items():
        user_config = config.get("strategies", {}).get(sid, {})
        result["strategies"].append({
            **sdata,
            "enabled": user_config.get("enabled", False),
            "allocation": user_config.get("allocation", 0.0),
            "priority": user_config.get("priority", 5),
            "capital_ratio": user_config.get("capital_ratio", 0.0),
            "user_config": user_config
        })
        if user_config.get("enabled"):
            result["enabled_count"] += 1
    
    return result


@router.post("/enable")
async def enable_strategy(
    strategy_id: str,
    allocation: float = 0.1,
    priority: int = 5,
    capital_ratio: float = 0.1
):
    """启用策略"""
    try:
        with open("/root/.openclaw/workspace/GO2SE_PLATFORM/versions/v6/alternative_strategies.json", "r") as f:
            config = json.load(f)
    except:
        config = {"expert_mode": False, "strategies": {}}
    
    if strategy_id not in config["strategies"]:
        config["strategies"][strategy_id] = {}
    
    config["strategies"][strategy_id].update({
        "enabled": True,
        "allocation": allocation,
        "priority": priority,
        "capital_ratio": capital_ratio
    })
    
    with open("/root/.openclaw/workspace/GO2SE_PLATFORM/versions/v6/alternative_strategies.json", "w") as f:
        json.dump(config, f, indent=2)
    
    return {"success": True, "message": f"已启用 {strategy_id}"}


@router.post("/disable")
async def disable_strategy(strategy_id: str):
    """禁用策略"""
    try:
        with open("/root/.openclaw/workspace/GO2SE_PLATFORM/versions/v6/alternative_strategies.json", "r") as f:
            config = json.load(f)
    except:
        return {"success": False, "message": "配置不存在"}
    
    if strategy_id in config.get("strategies", {}):
        config["strategies"][strategy_id]["enabled"] = False
        
        with open("/root/.openclaw/workspace/GO2SE_PLATFORM/versions/v6/alternative_strategies.json", "w") as f:
            json.dump(config, f, indent=2)
        
        return {"success": True, "message": f"已禁用 {strategy_id}"}
    
    return {"success": False, "message": "策略不存在"}


@router.get("/run/{strategy_id}")
async def run_strategy(strategy_id: str, symbol: str = "BTC/USDT", days: int = 30):
    """测试运行策略"""
    engine = AlternativeStrategyEngine()
    
    # 生成模拟数据
    base_price = 75000 if "BTC" in symbol else 2000
    from dataclasses import dataclass
    
    @dataclass
    class MockCandle:
        symbol: str
        timestamp: str
        open: float
        high: float
        low: float
        close: float
        volume: float
    
    candles = []
    for i in range(days * 24):
        ts = datetime.now().timestamp() - (days * 24 - i) * 3600
        price = base_price * (1 + random.gauss(0, 0.02))
        
        candles.append(MockCandle(
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
    result["symbol"] = symbol
    result["days"] = days
    
    return result


@router.post("/backtest")
async def backtest_strategies(
    strategy_ids: List[str],
    symbols: List[str] = ["BTC/USDT", "ETH/USDT"],
    days: int = 30,
    initial_cash: float = 100000
):
    """回测多个策略"""
    from app.core.backtest_engine import BacktestEngine
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "config": {
            "strategies": strategy_ids,
            "symbols": symbols,
            "days": days,
            "initial_cash": initial_cash
        },
        "results": {}
    }
    
    for strat_id in strategy_ids:
        engine = BacktestEngine(initial_cash=initial_cash, fee_rate=0.001)
        result = engine.run_strategy(strat_id, symbols, days)
        result["name"] = strat_id
        results["results"][strat_id] = result
    
    # 排序
    rankings = sorted(
        results["results"].items(),
        key=lambda x: x[1].get("return_pct", 0),
        reverse=True
    )
    results["rankings"] = [
        {"strategy": k, **v} for k, v in rankings
    ]
    
    return results


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
