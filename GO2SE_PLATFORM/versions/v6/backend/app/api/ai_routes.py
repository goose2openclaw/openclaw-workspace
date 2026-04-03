#!/usr/bin/env python3
"""
🪿 AI策略API路由
深度推理 + 信号评分 + 策略推荐
"""

import logging
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime

from app.core.config import settings
from app.core.trading_engine import engine
from app.core.ai_strategy import AIStrategyEngine
from app.core.database import get_db

logger = logging.getLogger("go2se")

router = APIRouter()

# AI策略引擎实例
ai_engine = AIStrategyEngine(engine)


@router.get("/ai/analyze/{symbol}")
async def analyze_symbol(symbol: str):
    """分析单个交易对"""
    try:
        state = await ai_engine.analyze_market(symbol)
        
        if not state:
            raise HTTPException(status_code=404, detail=f"无法获取 {symbol} 数据")
        
        return {
            "data": {
                "symbol": state.symbol,
                "price": state.price,
                "change_24h": state.change_24h,
                "rsi": state.rsi,
                "trend": state.trend,
                "volatility": state.volatility,
                "macd": state.macd,
                "analyzed_at": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"❌ 分析失败: {symbol} - {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai/reasoning")
async def deep_reasoning(symbols: Optional[List[str]] = None):
    """深度推理分析"""
    if symbols is None:
        symbols = settings.TRADING_PAIRS[:5]
    
    try:
        # 运行深度推理
        results = await ai_engine.run_deep_reasoning(symbols)
        
        # 获取策略推荐
        recommendation = ai_engine.get_strategy_recommendation(results)
        
        # 过滤买入信号
        buy_signals = [s for s in results if s.signal == "buy"]
        
        return {
            "data": {
                "analysis": [
                    {
                        "symbol": s.symbol,
                        "signal": s.signal,
                        "confidence": round(s.confidence, 1),
                        "strategy": s.strategy,
                        "reason": s.reason,
                        "factors": s.factors
                    }
                    for s in results
                ],
                "recommendation": recommendation,
                "summary": {
                    "total_analyzed": len(results),
                    "buy_signals": len(buy_signals),
                    "sell_signals": len([s for s in results if s.signal == "sell"]),
                    "hold_signals": len([s for s in results if s.signal == "hold"])
                },
                "reasoned_at": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"❌ 深度推理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai/signals")
async def get_ai_signals(limit: int = 10, min_confidence: float = 5.0):
    """获取AI信号 (置信度>=5)"""
    try:
        symbols = settings.TRADING_PAIRS[:10]
        
        # 运行推理
        results = await ai_engine.run_deep_reasoning(symbols)
        
        # 过滤高置信度信号
        filtered = [s for s in results if s.confidence >= min_confidence]
        
        # 排序
        sorted_signals = sorted(filtered, key=lambda x: x.confidence, reverse=True)
        
        return {
            "data": {
                "signals": [
                    {
                        "symbol": s.symbol,
                        "signal": s.signal,
                        "confidence": round(s.confidence, 1),
                        "strategy": s.strategy,
                        "reason": s.reason,
                        "factors": s.factors,
                        "action": "EXECUTE" if s.confidence >= 7.0 else "WATCH"
                    }
                    for s in sorted_signals[:limit]
                ],
                "count": len(sorted_signals),
                "threshold": min_confidence,
                "generated_at": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"❌ 获取信号失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai/strategies")
async def get_strategy_status():
    """获取所有策略状态和权重"""
    return {
        "data": {
            "strategies": [
                {
                    "name": name,
                    "weight": weight,
                    "description": get_strategy_description(name)
                }
                for name, weight in ai_engine.strategy_weights.items()
            ],
            "total_weight": sum(ai_engine.strategy_weights.values())
        }
    }


def get_strategy_description(name: str) -> str:
    """获取策略描述"""
    descriptions = {
        "rabbit": "🐰 趋势追踪 - 跟踪Top20币种趋势",
        "mole": "🐹 波动套利 - 高波动时低买高卖",
        "oracle": "🔮 预测市场 - 预测市场走向",
        "leader": "👑 做市协作 - 跟随大户流动性",
        "hitchhiker": "🍀 跟单分成 - 复制盈利策略",
        "airdrop": "💰 空投猎手 - 捕获新币空投",
        "crowdsource": "👶 众包任务 - 社区智慧协作"
    }
    return descriptions.get(name, name)


@router.post("/ai/trade")
async def execute_ai_trade(symbol: str, strategy: str = "rabbit"):
    """执行AI推荐交易"""
    try:
        # 获取信号
        state = await ai_engine.analyze_market(symbol)
        if not state:
            raise HTTPException(status_code=404, detail=f"无法获取 {symbol} 数据")
        
        score = ai_engine.calculate_confidence(state, strategy)
        
        # 检查置信度
        if score.confidence < 5.0:
            return {
                "status": "rejected",
                "reason": f"置信度不足 ({score.confidence:.1f} < 5.0)",
                "recommendation": "建议观望"
            }
        
        # 执行交易
        signal_data = {
            "symbol": symbol,
            "signal": score.signal,
            "confidence": score.confidence,
            "strategy": strategy,
            "reason": score.reason
        }
        
        result = await engine.execute_trade(signal_data)
        
        return {
            "status": "executed",
            "signal": signal_data,
            "result": result
        }
    except Exception as e:
        logger.error(f"❌ AI交易失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
