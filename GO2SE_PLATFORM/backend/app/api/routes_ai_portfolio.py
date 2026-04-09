#!/usr/bin/env python3
"""
🪿 GO2SE AI策略组合API路由
===========================
整合原创打兔子 + 打地鼠策略，AI动态调控权重

API端点:
- GET  /api/ai/portfolio/status     - 获取组合状态
- GET  /api/ai/portfolio/weights   - 获取当前权重
- POST /api/ai/portfolio/rebalance - 执行AI再平衡
- GET  /api/ai/portfolio/decision  - 获取AI决策建议
- POST /api/ai/portfolio/signal    - 提交交易信号
- GET  /api/ai/portfolio/performances - 获取策略表现

Author: GO2SE CEO
Date: 2026-03-31
"""

import asyncio
import json
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional, Dict
from app.core.database import get_db
from app.core.config import settings

logger = logging.getLogger("ai_portfolio_api")
router = APIRouter(prefix="/api/ai/portfolio")

# 导入AI组合管理器
try:
    from app.core.ai_portfolio_manager import (
        get_ai_portfolio,
        AIStrategyPortfolio,
        MiroFishScorer,
        generate_demo_performances
    )
except ImportError as e:
    logger.error(f"AI Portfolio Manager导入失败: {e}")
    get_ai_portfolio = None


# ═══════════════════════════════════════════════════════════════════
# 辅助函数
# ═══════════════════════════════════════════════════════════════════

def get_portfolio() -> AIStrategyPortfolio:
    """获取AI组合实例"""
    if get_ai_portfolio is None:
        raise HTTPException(status_code=503, detail="AI组合管理器未初始化")
    return get_ai_portfolio()


def convert_binance_to_strategy_format(ticker: Dict) -> Dict:
    """将Binance数据转换为策略格式"""
    price = ticker.get('last', ticker.get('price', 0))
    high = ticker.get('high', price * 1.05)
    low = ticker.get('low', price * 0.95)
    
    return {
        "price": price,
        "high_24h": high,
        "low_24h": low,
        "volume": ticker.get('quoteVolume', 0),
        "avg_volume": ticker.get('quoteVolume', 0) * 0.9,  # 估算
        "change_24h": ticker.get('percentage', 0),
        "rsi": 50,  # 需要计算
        "closes": [price],  # 需要历史数据
        "volumes": [ticker.get('quoteVolume', 0)]
    }


# ═══════════════════════════════════════════════════════════════════
# API端点
# ═══════════════════════════════════════════════════════════════════

@router.get("/status")
async def get_portfolio_status():
    """
    获取AI策略组合状态
    """
    portfolio = get_portfolio()
    status = portfolio.get_portfolio_status()
    
    return {
        "status": "ok",
        "data": status,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/weights")
async def get_weights():
    """
    获取当前权重分配
    """
    portfolio = get_portfolio()
    
    weights = portfolio.current_weights
    
    # 计算总权重
    total = sum(weights.values())
    
    # 获取性能数据用于计算推荐权重
    performances = list(portfolio.performances.values())
    
    if not performances:
        return {
            "weights": weights,
            "total": total,
            "note": "无历史数据，使用默认权重",
            "timestamp": datetime.now().isoformat()
        }
    
    # 计算AI推荐权重
    controller = portfolio.controller
    target_weights = controller.calculate_ai_weights(
        performances,
        portfolio.market_conditions
    )
    
    return {
        "current_weights": weights,
        "target_weights": target_weights,
        "total": total,
        "weights_change": {
            k: {
                "from": weights.get(k, 0),
                "to": target_weights.get(k, 0),
                "change": target_weights.get(k, 0) - weights.get(k, 0)
            }
            for k in weights.keys()
        },
        "timestamp": datetime.now().isoformat()
    }


@router.post("/rebalance")
async def rebalance():
    """
    执行AI权重再平衡
    """
    portfolio = get_portfolio()
    
    result = portfolio.rebalance_weights()
    
    return {
        "status": result["status"],
        "data": result,
        "message": "AI再平衡完成" if result["status"] == "success" else result.get("message", ""),
        "timestamp": datetime.now().isoformat()
    }


@router.get("/decision")
async def get_ai_decision(context: Optional[Dict] = None):
    """
    获取AI决策建议
    MiroFish 100智能体共识
    """
    portfolio = get_portfolio()
    
    # 如果没有性能数据，加载演示数据
    if not portfolio.performances:
        logger.info("无历史性能数据，加载演示数据")
        performances = generate_demo_performances()
        for perf in performances:
            portfolio.performances[perf.tool_id] = perf
    
    decision = portfolio.get_ai_decision(context)
    
    return {
        "status": "ok",
        "data": decision,
        "timestamp": datetime.now().isoformat()
    }


@router.post("/signal")
async def submit_signal(
    tool_id: str,
    symbol: str,
    signal_type: str,  # buy/sell/hold
    pnl: float,
    confidence: float,
    trend_score: Optional[float] = 0.5,
    signal_strength: Optional[float] = 0.5,
    market_data: Optional[Dict] = None
):
    """
    提交交易信号，更新策略表现
    
    参数:
    - tool_id: 工具ID (rabbit/mole/oracle/leader/hitchhiker/wool/poor)
    - symbol: 交易对
    - signal_type: 信号类型 (buy/sell/hold)
    - pnl: 盈亏
    - confidence: 置信度
    - trend_score: 趋势评分 (0-1)
    - signal_strength: 信号强度 (0-1)
    """
    portfolio = get_portfolio()
    
    if tool_id not in ["rabbit", "mole", "oracle", "leader", "hitchhiker", "wool", "poor"]:
        raise HTTPException(status_code=400, detail="无效的tool_id")
    
    # 更新性能
    portfolio.update_performance(tool_id, {
        "pnl": pnl,
        "confidence": confidence,
        "trend_score": trend_score,
        "signal_strength": signal_strength
    })
    
    # 更新市场条件
    if market_data:
        portfolio.update_market_conditions(market_data)
    
    # 检查是否需要再平衡
    adjustment_needed = False
    if len(portfolio.performances) >= 2:
        performances = list(portfolio.performances.values())
        current_w = portfolio.current_weights
        
        # 计算新目标权重
        target_w = portfolio.controller.calculate_ai_weights(
            performances,
            portfolio.market_conditions
        )
        
        # 检查差异
        for k in current_w:
            if abs(current_w[k] - target_w.get(k, current_w[k])) > 0.03:
                adjustment_needed = True
                break
    
    return {
        "status": "ok",
        "message": f"信号已记录: {tool_id} {symbol} {signal_type}",
        "adjustment_needed": adjustment_needed,
        "current_performance": asdict(portfolio.performances.get(tool_id)) if portfolio.performances.get(tool_id) else None,
        "timestamp": datetime.now().isoformat()
    }


from dataclasses import asdict

@router.get("/performances")
async def get_performances():
    """
    获取所有策略表现
    """
    portfolio = get_portfolio()
    
    # 如果没有性能数据，返回空
    if not portfolio.performances:
        return {
            "performances": [],
            "summary": {
                "total_tools": 0,
                "avg_win_rate": 0,
                "avg_trend_score": 0,
                "total_pnl": 0
            },
            "timestamp": datetime.now().isoformat()
        }
    
    performances_list = []
    for perf in portfolio.performances.values():
        performances_list.append(asdict(perf))
    
    # 计算汇总
    total_tools = len(performances_list)
    avg_win_rate = sum(p.get("win_rate", 0) for p in performances_list) / max(1, total_tools)
    avg_trend_score = sum(p.get("trend_score", 0) for p in performances_list) / max(1, total_tools)
    total_pnl = sum(p.get("total_pnl", 0) for p in performances_list)
    
    return {
        "performances": performances_list,
        "summary": {
            "total_tools": total_tools,
            "avg_win_rate": avg_win_rate,
            "avg_trend_score": avg_trend_score,
            "total_pnl": total_pnl
        },
        "timestamp": datetime.now().isoformat()
    }


@router.post("/run/{tool_id}")
async def run_strategy(
    tool_id: str,
    symbol: str,
    market_data: Dict
):
    """
    运行指定策略
    
    参数:
    - tool_id: rabbit/mole
    - symbol: 交易对
    - market_data: 市场数据
    """
    portfolio = get_portfolio()
    
    if tool_id == "rabbit":
        result = portfolio.run_rabbit_strategy(symbol, market_data)
    elif tool_id == "mole":
        result = portfolio.run_mole_strategy(symbol, market_data)
    else:
        raise HTTPException(status_code=400, detail=f"不支持的策略: {tool_id}")
    
    return {
        "status": "ok",
        "data": result,
        "timestamp": datetime.now().isoformat()
    }


@router.post("/update-market")
async def update_market_conditions(conditions: Dict):
    """
    更新市场条件
    """
    portfolio = get_portfolio()
    portfolio.update_market_conditions(conditions)
    
    return {
        "status": "ok",
        "market_conditions": portfolio.market_conditions,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/mirofish-score/{tool_id}")
async def get_mirofish_score(tool_id: str):
    """
    获取单个策略的MiroFish评分
    """
    portfolio = get_portfolio()
    
    if tool_id not in portfolio.performances:
        raise HTTPException(status_code=404, detail=f"策略 {tool_id} 不存在")
    
    perf = portfolio.performances[tool_id]
    scorer = MiroFishScorer()
    consensus = scorer.get_consensus(perf, portfolio.market_conditions)
    
    return {
        "tool_id": tool_id,
        "tool_name": perf.name,
        "emoji": perf.emoji,
        "consensus": consensus,
        "performance": asdict(perf),
        "timestamp": datetime.now().isoformat()
    }


@router.get("/config")
async def get_tool_config():
    """
    获取工具配置
    """
    portfolio = get_portfolio()
    
    return {
        "config": portfolio.tool_config,
        "weights": portfolio.current_weights,
        "timestamp": datetime.now().isoformat()
    }


# ═══════════════════════════════════════════════════════════════════
# 演示/测试端点
# ═══════════════════════════════════════════════════════════════════

@router.post("/demo/load-performances")
async def load_demo_performances():
    """
    加载演示性能数据 (用于测试)
    """
    portfolio = get_portfolio()
    
    performances = generate_demo_performances()
    for perf in performances:
        portfolio.performances[perf.tool_id] = perf
    
    return {
        "status": "ok",
        "message": f"已加载 {len(performances)} 个演示性能数据",
        "performances": [asdict(p) for p in performances],
        "timestamp": datetime.now().isoformat()
    }


@router.post("/demo/simulate-trade")
async def simulate_trade(
    tool_id: str,
    symbol: str,
    action: str,  # buy/sell
    price: float,
    quantity: float
):
    """
    模拟一笔交易 (演示用)
    """
    portfolio = get_portfolio()
    
    # 模拟盈亏
    import random
    pnl = (random.random() - 0.45) * price * quantity * 0.1  # 55%胜率
    trend_score = random.random() * 0.4 + 0.3  # 0.3-0.7
    signal_strength = random.random() * 0.4 + 0.4  # 0.4-0.8
    
    portfolio.update_performance(tool_id, {
        "pnl": pnl,
        "confidence": random.random() * 0.3 + 0.6,
        "trend_score": trend_score,
        "signal_strength": signal_strength
    })
    
    return {
        "status": "ok",
        "trade": {
            "tool_id": tool_id,
            "symbol": symbol,
            "action": action,
            "price": price,
            "quantity": quantity,
            "value": price * quantity
        },
        "result": {
            "pnl": pnl,
            "trend_score": trend_score,
            "signal_strength": signal_strength
        },
        "timestamp": datetime.now().isoformat()
    }
