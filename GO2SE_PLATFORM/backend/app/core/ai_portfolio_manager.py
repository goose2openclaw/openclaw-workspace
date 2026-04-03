#!/usr/bin/env python3
"""
🪿 GO2SE AI智能投资组合管理器 V1
=================================
整合原创打兔子 + 打地鼠策略，AI动态调控权重

核心功能:
1. 集成原创打兔子策略 (rabbit_strategy.py)
2. 集成原创打地鼠策略 (mole_strategy.py)
3. AI动态权重调整 (根据表现自动加减仓)
4. MiroFish评分系统辅助决策

Author: GO2SE CEO
Date: 2026-03-31
"""

import json
import math
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from enum import Enum

from app.core.config import settings

logger = logging.getLogger("ai_portfolio")

# 导入原创策略
try:
    from app.core.rabbit_strategy import RabbitStrategy, get_rabbit_strategy
    from app.core.mole_strategy import MoleStrategy, get_mole_strategy
except ImportError as e:
    logger.warning(f"策略导入失败: {e}")
    RabbitStrategy = None
    MoleStrategy = None


class TrendDirection(Enum):
    """趋势方向"""
    BULLISH = "bullish"
    NEUTRAL = "neutral"
    BEARISH = "bearish"


@dataclass
class StrategyPerformance:
    """策略表现数据"""
    tool_id: str
    name: str
    emoji: str
    # 原始数据
    total_trades: int = 0
    win_trades: int = 0
    total_pnl: float = 0.0
    current_weight: float = 0.0
    # 计算指标
    win_rate: float = 0.5
    avg_profit: float = 0.0
    avg_loss: float = 0.0
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    trend_score: float = 0.5  # 0-1
    signal_strength: float = 0.5  # 0-1
    market_condition: str = "neutral"  # bullish/neutral/bearish
    # AI决策
    ai_score: float = 0.5  # 综合AI评分
    recommended_weight: float = 0.0  # AI推荐权重
    confidence: float = 0.5  # AI置信度
    last_update: str = ""


@dataclass
class WeightAdjustment:
    """权重调整建议"""
    tool_id: str
    from_weight: float
    to_weight: float
    change_pct: float
    reason: str
    priority: int  # 1-5
    trigger: str  # 触发原因


@dataclass
class PortfolioAllocation:
    """组合配置"""
    rabbit_weight: float = 0.25
    mole_weight: float = 0.20
    oracle_weight: float = 0.15
    leader_weight: float = 0.15
    hitchhiker_weight: float = 0.10
    wool_weight: float = 0.03
    poor_weight: float = 0.02
    # 总仓位限制
    total_exposure_limit: float = 0.80  # 最大80%仓位
    max_single_position: float = 0.15  # 单币最大15%


class MiroFishScorer:
    """
    MiroFish评分系统
    100智能体共识预测，辅助AI决策
    """
    
    def __init__(self):
        self.agent_count = 100
        self.confidence_threshold = 0.70
        
    def score_strategy(self, perf: StrategyPerformance, market_data: Dict) -> float:
        """
        MiroFish风格评分
        多维度综合评估策略
        """
        scores = []
        
        # 1. 胜率评分 (权重25%)
        if perf.total_trades >= 10:
            win_rate_score = perf.win_rate
            scores.append(("win_rate", win_rate_score, 0.25))
        
        # 2. 盈亏比评分 (权重20%)
        if perf.avg_loss > 0:
            profit_loss_ratio = abs(perf.avg_profit / perf.avg_loss)
            pl_score = min(1.0, profit_loss_ratio / 2.0)  # 2:1为满分
            scores.append(("profit_loss", pl_score, 0.20))
        
        # 3. 趋势评分 (权重25%)
        trend_score = perf.trend_score
        scores.append(("trend", trend_score, 0.25))
        
        # 4. 信号强度 (权重15%)
        signal_score = perf.signal_strength
        scores.append(("signal", signal_score, 0.15))
        
        # 5. 流动性/市场条件 (权重15%)
        market_score = 0.5
        if market_data.get("volume_spike", 1.0) > 1.5:
            market_score = 0.7
        if market_data.get("volatility", 0.05) > 0.10:
            market_score = min(1.0, market_score + 0.2)
        scores.append(("market", market_score, 0.15))
        
        # 归一化加权
        if not scores:
            return 0.5
            
        total_weight = sum(s[2] for s in scores)
        final_score = sum(s[1] * s[2] for s in scores) / total_weight
        
        return max(0.0, min(1.0, final_score))
    
    def get_consensus(self, perf: StrategyPerformance, market_data: Dict) -> Dict:
        """
        100智能体共识
        返回共识结果
        """
        score = self.score_strategy(perf, market_data)
        
        # 模拟100智能体投票
        bullish_votes = int(score * 100)
        neutral_votes = int((1 - abs(score - 0.5) * 2) * 100 * 0.3)
        bearish_votes = 100 - bullish_votes - neutral_votes
        
        direction = "bullish" if score > 0.6 else "bearish" if score < 0.4 else "neutral"
        
        return {
            "score": score,
            "direction": direction,
            "votes": {
                "bullish": bullish_votes,
                "neutral": neutral_votes,
                "bearish": bearish_votes
            },
            "consensus_strength": abs(score - 0.5) * 2,  # 0-1
            "confidence": perf.confidence
        }


class AIWeightController:
    """
    AI权重控制器
    根据策略表现 + 市场条件动态调整权重
    """
    
    # 调整参数
    MAX_SINGLE_ADJUSTMENT = 0.05  # 单次最大调整5%
    MIN_WEIGHT_CHANGE = 0.01  # 最小调整幅度1%
    REBALANCE_HYSTERESIS = 0.02  # 滞后阈值
    
    # 趋势阈值
    TREND_BULLISH = 0.65
    TREND_NEUTRAL = 0.45
    TREND_BEARISH = 0.35
    
    # 市场条件权重因子
    BULL_MARKET_FACTOR = {
        "rabbit": 1.2,   # 牛市加分
        "mole": 0.8,     # 高波动更合适
    }
    BEAR_MARKET_FACTOR = {
        "rabbit": 0.7,   # 熊市减分
        "mole": 1.1,     # 波动反而有机会
    }
    
    def __init__(self):
        self.allocation = PortfolioAllocation()
        self.history: List[Dict] = []
        
    def calculate_ai_weights(
        self, 
        performances: List[StrategyPerformance],
        market_conditions: Dict
    ) -> Dict[str, float]:
        """
        计算AI推荐权重
        
        输入:
        - performances: 各策略表现
        - market_conditions: 市场条件 (volatility, volume_spike, trend)
        """
        
        # 确定市场状态
        market_state = self._determine_market_state(market_conditions)
        
        # 计算基础分数
        tool_scores = {}
        for perf in performances:
            # MiroFish评分
            mirofish = MiroFishScorer()
            consensus = mirofish.get_consensus(perf, market_conditions)
            
            # 综合评分 = MiroFish评分 * 市场适应因子
            market_factor = 1.0
            if market_state == "bullish":
                market_factor = self.BULL_MARKET_FACTOR.get(perf.tool_id, 1.0)
            elif market_state == "bearish":
                market_factor = self.BEAR_MARKET_FACTOR.get(perf.tool_id, 1.0)
            
            ai_score = consensus["score"] * market_factor
            ai_score = max(0.0, min(1.0, ai_score))
            
            perf.ai_score = ai_score
            perf.market_condition = market_state
            
            tool_scores[perf.tool_id] = {
                "ai_score": ai_score,
                "consensus": consensus,
                "market_factor": market_factor
            }
        
        # 转换为权重
        raw_weights = {p.tool_id: p.ai_score for p in performances}
        total = sum(raw_weights.values())
        
        if total == 0:
            return {p.tool_id: p.ai_score for p in performances}
        
        # 归一化
        normalized_weights = {k: v / total for k, v in raw_weights.items()}
        
        # 应用边界限制
        final_weights = self._apply_weight_limits(normalized_weights, performances)
        
        # 记录历史
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "market_state": market_state,
            "weights": final_weights,
            "scores": tool_scores
        })
        
        return final_weights
    
    def _determine_market_state(self, conditions: Dict) -> str:
        """判断市场状态"""
        trend = conditions.get("trend", "neutral")
        volatility = conditions.get("volatility", 0.05)
        volume = conditions.get("volume_spike", 1.0)
        
        # 基于多因素判断
        bullish_signals = 0
        
        if trend == "bullish":
            bullish_signals += 2
        elif trend == "bearish":
            bullish_signals -= 2
            
        if volatility > 0.10:
            bullish_signals += 1  # 高波动多空都有机会
            
        if volume > 1.5:
            bullish_signals += 1
            
        if bullish_signals >= 2:
            return "bullish"
        elif bullish_signals <= -1:
            return "bearish"
        else:
            return "neutral"
    
    def _apply_weight_limits(
        self, 
        weights: Dict[str, float],
        performances: List[StrategyPerformance]
    ) -> Dict[str, float]:
        """应用权重限制"""
        # 获取各工具的min/max限制
        limits = {
            "rabbit": (0.10, 0.40),
            "mole": (0.08, 0.35),
            "oracle": (0.05, 0.25),
            "leader": (0.05, 0.25),
            "hitchhiker": (0.03, 0.20),
            "wool": (0.01, 0.10),
            "poor": (0.01, 0.08)
        }
        
        final = {}
        
        # 第一遍：应用限制
        for tool_id, weight in weights.items():
            min_w, max_w = limits.get(tool_id, (0.0, 1.0))
            final[tool_id] = max(min_w, min(max_w, weight))
        
        # 第二遍：归一化确保=1.0
        total = sum(final.values())
        if total > 0:
            final = {k: v / total for k, v in final.items()}
        
        return final
    
    def generate_adjustment_plan(
        self,
        current_weights: Dict[str, float],
        target_weights: Dict[str, float],
        performances: List[StrategyPerformance]
    ) -> List[WeightAdjustment]:
        """
        生成调整计划
        限制单次调整幅度，避免频繁交易
        """
        adjustments = []
        
        for tool_id in current_weights:
            current = current_weights.get(tool_id, 0.0)
            target = target_weights.get(tool_id, current)
            diff = target - current
            
            # 检查是否需要调整
            if abs(diff) < self.MIN_WEIGHT_CHANGE:
                continue
            
            # 限制单次调整幅度
            actual_change = max(-self.MAX_SINGLE_ADJUSTMENT, 
                               min(self.MAX_SINGLE_ADJUSTMENT, diff))
            
            # 计算优先级 (变化越大优先级越高)
            priority = min(5, max(1, int(abs(diff) / 0.02) + 2))
            
            # 确定触发原因
            perf = next((p for p in performances if p.tool_id == tool_id), None)
            if perf:
                if perf.ai_score > 0.7:
                    trigger = "ai_score_high"
                    reason = f"AI评分{perf.ai_score:.1%}→推荐加仓"
                elif perf.ai_score < 0.4:
                    trigger = "ai_score_low"
                    reason = f"AI评分{perf.ai_score:.1%}→建议减仓"
                else:
                    trigger = "rebalance"
                    reason = f"权重再平衡 {current:.1%}→{target:.1%}"
            else:
                trigger = "init"
                reason = f"初始化权重"
            
            adjustments.append(WeightAdjustment(
                tool_id=tool_id,
                from_weight=current,
                to_weight=current + actual_change,
                change_pct=actual_change,
                reason=reason,
                priority=priority,
                trigger=trigger
            ))
        
        # 按优先级排序
        adjustments.sort(key=lambda x: x.priority, reverse=True)
        
        return adjustments


class AIStrategyPortfolio:
    """
    AI策略组合管理器
    整合打兔子 + 打地鼠 + 其他工具
    """
    
    def __init__(self):
        # 策略实例
        self.rabbit = get_rabbit_strategy() if RabbitStrategy else None
        self.mole = get_mole_strategy() if MoleStrategy else None
        
        # 权重控制器
        self.controller = AIWeightController()
        
        # 当前权重
        self.current_weights = {
            "rabbit": 0.25,
            "mole": 0.20,
            "oracle": 0.15,
            "leader": 0.15,
            "hitchhiker": 0.10,
            "wool": 0.03,
            "poor": 0.02
        }
        
        # 策略表现记录
        self.performances: Dict[str, StrategyPerformance] = {}
        
        # 市场条件缓存
        self.market_conditions = {
            "trend": "neutral",
            "volatility": 0.05,
            "volume_spike": 1.0
        }
        
        # 工具配置
        self.tool_config = {
            "rabbit": {
                "name": "🐰 打兔子",
                "emoji": "🐰",
                "description": "前20主流加密货币趋势跟踪",
                "stop_loss": 0.05,
                "take_profit": 0.08,
                "holding_period": "1-7天",
                "symbols": ["BTC", "ETH", "BNB", "XRP", "SOL", "ADA", "DOGE", "AVAX", "DOT", "MATIC"]
            },
            "mole": {
                "name": "🐹 打地鼠",
                "emoji": "🐹",
                "description": "高波动山寨币火控雷达",
                "stop_loss": 0.05,
                "take_profit": 0.15,
                "holding_period": "1小时-3天",
                "symbols": []  # 动态扫描
            }
        }
    
    def update_performance(self, tool_id: str, trade_result: Dict):
        """更新策略表现"""
        if tool_id not in self.performances:
            self.performances[tool_id] = StrategyPerformance(
                tool_id=tool_id,
                name=self.tool_config.get(tool_id, {}).get("name", tool_id),
                emoji=self.tool_config.get(tool_id, {}).get("emoji", "❓")
            )
        
        perf = self.performances[tool_id]
        
        # 更新统计
        perf.total_trades += 1
        if trade_result.get("pnl", 0) > 0:
            perf.win_trades += 1
        
        perf.total_pnl += trade_result.get("pnl", 0)
        perf.win_rate = perf.win_trades / perf.total_trades
        
        # 更新趋势评分 (使用移动平均)
        new_trend = trade_result.get("trend_score", 0.5)
        old_trend = perf.trend_score
        perf.trend_score = 0.7 * old_trend + 0.3 * new_trend
        
        # 更新信号强度
        new_signal = trade_result.get("signal_strength", 0.5)
        old_signal = perf.signal_strength
        perf.signal_strength = 0.8 * old_signal + 0.2 * new_signal
        
        perf.last_update = datetime.now().isoformat()
    
    def update_market_conditions(self, conditions: Dict):
        """更新市场条件"""
        self.market_conditions.update(conditions)
    
    def run_rabbit_strategy(self, symbol: str, market_data: Dict) -> Dict:
        """运行打兔子策略"""
        if not self.rabbit:
            return {"error": "打兔子策略未初始化"}
        
        # 转换数据格式
        converted_data = {
            "price": market_data.get("price", 0),
            "rsi": market_data.get("rsi", 50),
            "ma7": market_data.get("ma7", market_data.get("price", 0)),
            "ma25": market_data.get("ma25", market_data.get("price", 0)),
            "volume": market_data.get("volume", 0),
            "avg_volume": market_data.get("avg_volume", market_data.get("volume", 0))
        }
        
        signal = self.rabbit.generate_signal(symbol, converted_data)
        
        return {
            "tool_id": "rabbit",
            "tool_name": "🐰 打兔子",
            "symbol": symbol,
            **signal
        }
    
    def run_mole_strategy(self, symbol: str, market_data: Dict) -> Dict:
        """运行打地鼠策略"""
        if not self.mole:
            return {"error": "打地鼠策略未初始化"}
        
        # 转换数据格式
        converted_data = {
            "price": market_data.get("price", 0),
            "high_24h": market_data.get("high_24h", market_data.get("price", 0) * 1.05),
            "low_24h": market_data.get("low_24h", market_data.get("price", 0) * 0.95),
            "volume": market_data.get("volume", 0),
            "avg_volume": market_data.get("avg_volume", market_data.get("volume", 0)),
            "closes": market_data.get("closes", [market_data.get("price", 0)]),
            "volumes": market_data.get("volumes", [market_data.get("volume", 0)])
        }
        
        signal = self.mole.generate_signal(symbol, converted_data)
        
        return {
            "tool_id": "mole",
            "tool_name": "🐹 打地鼠",
            "symbol": symbol,
            **signal
        }
    
    def run_all_strategies(self, market_data: Dict) -> List[Dict]:
        """运行所有策略"""
        results = []
        
        # 打兔子 - 前20主流币
        rabbit_symbols = self.tool_config["rabbit"]["symbols"]
        for symbol in rabbit_symbols[:5]:  # 限制数量
            result = self.run_rabbit_strategy(symbol, market_data.get(symbol, {}))
            results.append(result)
        
        # 打地鼠 - 动态扫描高波动币
        # 从市场数据中获取高波动币
        mole_symbols = market_data.get("high_volatility_symbols", [])
        for symbol in mole_symbols[:3]:
            result = self.run_mole_strategy(symbol, market_data.get(symbol, {}))
            results.append(result)
        
        return results
    
    def rebalance_weights(self) -> Dict:
        """
        执行AI权重再平衡
        """
        # 准备性能数据
        performances = list(self.performances.values())
        
        # 如果没有历史数据，使用默认权重
        if not performances:
            return {
                "status": "no_history",
                "weights": self.current_weights,
                "adjustments": [],
                "message": "无历史数据，使用默认权重"
            }
        
        # 计算目标权重
        target_weights = self.controller.calculate_ai_weights(
            performances,
            self.market_conditions
        )
        
        # 生成调整计划
        adjustments = self.controller.generate_adjustment_plan(
            self.current_weights,
            target_weights,
            performances
        )
        
        # 执行调整
        for adj in adjustments:
            self.current_weights[adj.tool_id] = adj.to_weight
            adj.from_weight = adj.from_weight  # 已在generate时计算
        
        return {
            "status": "success",
            "previous_weights": {k: v for k, v in self.current_weights.items()},
            "target_weights": target_weights,
            "adjustments": [asdict(a) for a in adjustments],
            "timestamp": datetime.now().isoformat()
        }
    
    def get_portfolio_status(self) -> Dict:
        """获取组合状态"""
        performances_list = [asdict(p) for p in self.performances.values()]
        
        return {
            "current_weights": self.current_weights,
            "performances": performances_list,
            "market_conditions": self.market_conditions,
            "tool_config": self.tool_config,
            "rabbit_active": self.rabbit is not None,
            "mole_active": self.mole is not None,
            "total_allocation": sum(self.current_weights.values()),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_ai_decision(self, context: Dict = None) -> Dict:
        """
        获取AI决策建议
        MiroFish 100智能体共识
        """
        context = context or {}
        
        # 更新市场条件
        if "market_conditions" in context:
            self.update_market_conditions(context["market_conditions"])
        
        # 获取当前状态
        status = self.get_portfolio_status()
        
        # 生成MiroFish评分
        mirofish_scores = {}
        for perf in self.performances.values():
            scorer = MiroFishScorer()
            consensus = scorer.get_consensus(perf, self.market_conditions)
            mirofish_scores[perf.tool_id] = consensus
        
        # AI综合建议
        overall_score = sum(s["score"] for s in mirofish_scores.values()) / max(1, len(mirofish_scores))
        
        # 决策建议
        if overall_score > 0.65:
            decision = "BULLISH"
            action = "加仓"
            confidence = overall_score
        elif overall_score < 0.40:
            decision = "BEARISH"
            action = "减仓"
            confidence = 1 - overall_score
        else:
            decision = "NEUTRAL"
            action = "持有"
            confidence = 1 - abs(overall_score - 0.5) * 2
        
        return {
            "decision": decision,
            "action": action,
            "confidence": confidence,
            "overall_score": overall_score,
            "mirofish_scores": mirofish_scores,
            "market_conditions": self.market_conditions,
            "weights": self.current_weights,
            "reasoning": self._generate_reasoning(decision, overall_score, mirofish_scores),
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_reasoning(
        self, 
        decision: str, 
        score: float, 
        mirofish_scores: Dict
    ) -> str:
        """生成决策推理文本"""
        reasons = []
        
        if decision == "BULLISH":
            reasons.append(f"综合得分{score:.1%}高于阈值，市场向好")
            for tool_id, consensus in mirofish_scores.items():
                if consensus["score"] > 0.6:
                    perf = self.performances.get(tool_id)
                    emoji = perf.emoji if perf else "❓"
                    reasons.append(f"{emoji}{tool_id}评分{consensus['score']:.1%}，看涨")
        
        elif decision == "BEARISH":
            reasons.append(f"综合得分{score:.1%}低于阈值，控制风险")
            for tool_id, consensus in mirofish_scores.items():
                if consensus["score"] < 0.4:
                    perf = self.performances.get(tool_id)
                    emoji = perf.emoji if perf else "❓"
                    reasons.append(f"{emoji}{tool_id}评分{consensus['score']:.1%}，谨慎")
        
        else:
            reasons.append(f"综合得分{score:.1%}处于中性区间，观望")
        
        return "; ".join(reasons)


# ═══════════════════════════════════════════════════════════════════
# 全局单例
# ═══════════════════════════════════════════════════════════════════

_ai_portfolio: Optional[AIStrategyPortfolio] = None


def get_ai_portfolio() -> AIStrategyPortfolio:
    """获取AI策略组合实例"""
    global _ai_portfolio
    if _ai_portfolio is None:
        _ai_portfolio = AIStrategyPortfolio()
    return _ai_portfolio


# ═══════════════════════════════════════════════════════════════════
# 模拟数据用于演示
# ═══════════════════════════════════════════════════════════════════

def generate_demo_performances() -> List[StrategyPerformance]:
    """生成演示用性能数据"""
    return [
        StrategyPerformance(
            tool_id="rabbit",
            name="🐰 打兔子",
            emoji="🐰",
            total_trades=45,
            win_trades=32,
            total_pnl=1250.50,
            current_weight=0.25,
            win_rate=0.71,
            avg_profit=55.0,
            avg_loss=28.0,
            max_drawdown=0.08,
            sharpe_ratio=1.65,
            trend_score=0.72,
            signal_strength=0.68,
            market_condition="bullish",
            ai_score=0.0,
            recommended_weight=0.0,
            confidence=0.75,
            last_update=datetime.now().isoformat()
        ),
        StrategyPerformance(
            tool_id="mole",
            name="🐹 打地鼠",
            emoji="🐹",
            total_trades=78,
            win_trades=42,
            total_pnl=890.25,
            current_weight=0.20,
            win_rate=0.54,
            avg_profit=85.0,
            avg_loss=35.0,
            max_drawdown=0.12,
            sharpe_ratio=1.42,
            trend_score=0.58,
            signal_strength=0.72,
            market_condition="neutral",
            ai_score=0.0,
            recommended_weight=0.0,
            confidence=0.68,
            last_update=datetime.now().isoformat()
        ),
        StrategyPerformance(
            tool_id="oracle",
            name="🔮 走着瞧",
            emoji="🔮",
            total_trades=23,
            win_trades=15,
            total_pnl=420.80,
            current_weight=0.15,
            win_rate=0.65,
            avg_profit=45.0,
            avg_loss=22.0,
            max_drawdown=0.06,
            sharpe_ratio=1.88,
            trend_score=0.65,
            signal_strength=0.55,
            market_condition="bullish",
            ai_score=0.0,
            recommended_weight=0.0,
            confidence=0.62,
            last_update=datetime.now().isoformat()
        ),
        StrategyPerformance(
            tool_id="leader",
            name="👑 跟大哥",
            emoji="👑",
            total_trades=34,
            win_trades=22,
            total_pnl=380.40,
            current_weight=0.15,
            win_rate=0.65,
            avg_profit=35.0,
            avg_loss=20.0,
            max_drawdown=0.05,
            sharpe_ratio=1.75,
            trend_score=0.60,
            signal_strength=0.52,
            market_condition="neutral",
            ai_score=0.0,
            recommended_weight=0.0,
            confidence=0.58,
            last_update=datetime.now().isoformat()
        )
    ]


# ═══════════════════════════════════════════════════════════════════
# 主程序测试
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # 测试AI组合管理器
    portfolio = AIStrategyPortfolio()
    
    # 加载模拟数据
    performances = generate_demo_performances()
    for perf in performances:
        portfolio.performances[perf.tool_id] = perf
    
    # 更新市场条件
    portfolio.update_market_conditions({
        "trend": "bullish",
        "volatility": 0.08,
        "volume_spike": 1.5
    })
    
    print("=" * 60)
    print("🪿 AI智能投资组合管理器 - 测试")
    print("=" * 60)
    
    # 获取AI决策
    decision = portfolio.get_ai_decision()
    print(f"\n📊 AI决策: {decision['decision']}")
    print(f"📊 建议动作: {decision['action']}")
    print(f"📊 置信度: {decision['confidence']:.1%}")
    print(f"📊 推理: {decision['reasoning']}")
    
    print("\n📊 MiroFish评分:")
    for tool_id, score in decision["mirofish_scores"].items():
        perf = portfolio.performances.get(tool_id)
        emoji = perf.emoji if perf else "❓"
        print(f"  {emoji} {tool_id}: {score['score']:.1%} ({score['direction']})")
    
    print("\n📊 当前权重:")
    for tool_id, weight in portfolio.current_weights.items():
        print(f"  {tool_id}: {weight:.1%}")
    
    # 执行再平衡
    print("\n🔄 执行权重再平衡...")
    result = portfolio.rebalance_weights()
    
    if result["status"] == "success":
        print("\n📊 调整计划:")
        for adj in result["adjustments"]:
            emoji = portfolio.performances.get(adj["tool_id"], {}).get("emoji", "❓")
            print(f"  {emoji} {adj['tool_id']}: {adj['from_weight']:.1%} → {adj['to_weight']:.1%}")
            print(f"     原因: {adj['reason']}")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)
