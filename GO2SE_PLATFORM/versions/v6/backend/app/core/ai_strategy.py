#!/usr/bin/env python3
"""
🪿 GO2SE AI 策略引擎
深度推理 + 信号评分 + 置信度计算
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json

logger = logging.getLogger("go2se")


@dataclass
class MarketState:
    """市场状态"""
    symbol: str
    price: float
    change_24h: float
    volume_24h: float
    rsi: float
    macd: str  # bull/bear/neutral
    trend: str  # up/down/sideways
    volatility: float  # 高/中/低


@dataclass
class SignalScore:
    """信号评分"""
    strategy: str
    symbol: str
    signal: str  # buy/sell/hold
    confidence: float  # 0-10
    factors: List[Dict]  # 评分因素
    reason: str  # 推荐理由


class AIStrategyEngine:
    """AI策略引擎"""
    
    def __init__(self, engine):
        self.engine = engine
        self.strategy_weights = {
            "rabbit": 0.25,      # 趋势追踪
            "mole": 0.20,        # 波动套利
            "oracle": 0.15,      # 预测市场
            "leader": 0.15,      # 做市协作
            "hitchhiker": 0.10,  # 跟单
            "airdrop": 0.03,     # 空投
            "crowdsource": 0.02  # 众包
        }
    
    async def analyze_market(self, symbol: str) -> MarketState:
        """分析市场状态"""
        try:
            tick = await self.engine.get_market_data(symbol)
            
            # 计算趋势
            trend = "sideways"
            if tick.change_24h > 2:
                trend = "up"
            elif tick.change_24h < -2:
                trend = "down"
            
            # 计算波动性
            volatility = "low"
            if tick.volume_24h > 1000000000:  # 10亿
                volatility = "high"
            elif tick.volume_24h > 500000000:  # 5亿
                volatility = "medium"
            
            # RSI判断
            macd = "neutral"
            if tick.rsi > 60:
                macd = "bull"
            elif tick.rsi < 40:
                macd = "bear"
            
            return MarketState(
                symbol=symbol,
                price=tick.price,
                change_24h=tick.change_24h,
                volume_24h=tick.volume_24h,
                rsi=tick.rsi,
                macd=macd,
                trend=trend,
                volatility=volatility
            )
        except Exception as e:
            logger.error(f"❌ 市场分析失败: {symbol} - {e}")
            return None
    
    def calculate_confidence(self, state: MarketState, strategy: str) -> SignalScore:
        """计算信号置信度"""
        factors = []
        confidence = 0.0
        
        # 策略1: 兔子 (趋势追踪)
        if strategy == "rabbit":
            if state.trend == "up":
                confidence += 3.0
                factors.append({"name": "上升趋势", "score": 3.0})
            if state.rsi < 70 and state.rsi > 30:
                confidence += 2.0
                factors.append({"name": "RSI健康区间", "score": 2.0})
            if state.volume_24h > 500000000:
                confidence += 2.0
                factors.append({"name": "成交量充足", "score": 2.0})
            signal = "buy" if state.trend == "up" else "hold"
        
        # 策略2: 地鼠 (波动套利)
        elif strategy == "mole":
            if state.volatility == "high":
                confidence += 4.0
                factors.append({"name": "高波动", "score": 4.0})
            if state.rsi < 30:
                confidence += 3.0
                factors.append({"name": "超卖", "score": 3.0})
            if abs(state.change_24h) > 5:
                confidence += 2.0
                factors.append({"name": "日内波动大", "score": 2.0})
            signal = "buy" if state.rsi < 30 else "hold"
        
        # 策略3: 预言家 (预测市场)
        elif strategy == "oracle":
            if state.trend == "sideways":
                confidence += 3.0
                factors.append({"name": "横盘整理", "score": 3.0})
            if state.macd == "neutral":
                confidence += 2.0
                factors.append({"name": "MACD收敛", "score": 2.0})
            signal = "hold"
        
        # 策略4: 跟大哥 (做市)
        elif strategy == "leader":
            if state.volume_24h > 1000000000:
                confidence += 3.0
                factors.append({"name": "深度流动性", "score": 3.0})
            if abs(state.change_24h) < 1:
                confidence += 2.0
                factors.append({"name": "价格稳定", "score": 2.0})
            signal = "hold"
        
        else:
            signal = "hold"
        
        # 限制置信度范围
        confidence = min(confidence, 10.0)
        
        return SignalScore(
            strategy=strategy,
            symbol=state.symbol,
            signal=signal,
            confidence=confidence,
            factors=factors,
            reason=self._generate_reason(factors, signal)
        )
    
    def _generate_reason(self, factors: List[Dict], signal: str) -> str:
        """生成推荐理由"""
        if not factors:
            return "市场状态不明确，建议观望"
        
        factor_names = [f["name"] for f in factors]
        reason = f"{'、'.join(factor_names)}，"
        
        if signal == "buy":
            reason += "建议买入"
        elif signal == "sell":
            reason += "建议卖出"
        else:
            reason += "建议观望"
        
        return reason
    
    async def run_deep_reasoning(self, symbols: List[str]) -> List[SignalScore]:
        """运行深度推理"""
        results = []
        
        logger.info(f"🧠 开始深度推理 ({len(symbols)} 个交易对)")
        
        for symbol in symbols:
            # 1. 市场状态分析
            state = await self.analyze_market(symbol)
            if not state:
                continue
            
            # 2. 多策略评分
            scores = []
            for strategy in self.strategy_weights.keys():
                score = self.calculate_confidence(state, strategy)
                score.confidence *= self.strategy_weights[strategy]
                scores.append(score)
            
            # 3. 综合评分
            best_score = max(scores, key=lambda x: x.confidence)
            
            # 4. 置信度阈值判断
            if best_score.confidence < 2.0:
                best_score.signal = "hold"
                best_score.confidence = 1.0
                best_score.reason = "未达到执行阈值，建议观望"
            
            results.append(best_score)
            
            logger.info(
                f"📊 {symbol}: {best_score.signal} "
                f"(置信度: {best_score.confidence:.1f}, 策略: {best_score.strategy})"
            )
        
        return results
    
    def get_strategy_recommendation(self, scores: List[SignalScore]) -> Dict:
        """获取策略组合推荐"""
        # 按置信度排序
        sorted_scores = sorted(scores, key=lambda x: x.confidence, reverse=True)
        
        # 选择Top 3
        top_strategies = sorted_scores[:3]
        
        # 计算仓位分配
        total_confidence = sum(s.confidence for s in top_strategies)
        allocations = {}
        
        for s in top_strategies:
            if s.signal == "buy":
                # 置信度越高，仓位越大
                weight = s.confidence / total_confidence if total_confidence > 0 else 0
                allocations[s.symbol] = {
                    "strategy": s.strategy,
                    "weight": round(weight, 2),
                    "signal": s.signal,
                    "confidence": round(s.confidence, 1)
                }
        
        return {
            "recommended_strategies": [
                {
                    "strategy": s.strategy,
                    "confidence": round(s.confidence, 1),
                    "signal": s.signal
                }
                for s in top_strategies
            ],
            "allocations": allocations,
            "total_confidence": round(total_confidence, 1)
        }
