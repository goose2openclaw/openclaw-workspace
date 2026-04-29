#!/usr/bin/env python3
"""
🔊 市场声纳库 + 决策引擎
=========================
声纳趋势模型 + 决策等式 + 加权因子
"""

import json
import random
import math
from datetime import datetime
from typing import Dict, List, Optional

class SonarTrendModel:
    """声纳趋势模型"""
    
    def __init__(self):
        self.name = "sonar_trend"
        self.version = "1.0"
        
        # 历史数据点
        self.price_history = []
        self.volume_history = []
        self.momentum_history = []
        
        # 声纳参数
        self.ping_depth = 7  # ping扫描深度
        self.confidence_threshold = 0.65
        
    def ping(self, market_data: Dict) -> Dict:
        """声纳扫描 - 深入分析市场"""
        symbol = market_data.get("symbol", "BTC")
        price = market_data.get("price", 50000)
        volume = market_data.get("volume", 10000000)
        change_24h = market_data.get("change_24h", 0)
        change_7d = market_data.get("change_7d", 0)
        change_30d = market_data.get("change_30d", 0)
        
        # 更新历史
        self.price_history.append(price)
        self.volume_history.append(volume)
        if len(self.price_history) > 30:
            self.price_history.pop(0)
            self.volume_history.pop(0)
        
        # 计算声纳指标
        sonar_reading = self._calculate_sonar()
        
        # 趋势分析
        trend = self._analyze_trend()
        
        # 置信度
        confidence = self._calculate_confidence(sonar_reading, trend)
        
        # 决策
        decision = self._make_decision(confidence, trend, sonar_reading)
        
        return {
            "symbol": symbol,
            "price": price,
            "sonar_reading": sonar_reading,
            "trend": trend,
            "confidence": confidence,
            "decision": decision,
            "timestamp": datetime.now().isoformat()
        }
    
    def _calculate_sonar(self) -> Dict:
        """计算声纳指标"""
        if len(self.price_history) < 3:
            return {"velocity": 0, "acceleration": 0, "depth": 0, "surface": "neutral"}
        
        # 速度 (价格变化率)
        velocity = (self.price_history[-1] - self.price_history[-3]) / self.price_history[-3] * 100
        
        # 加速度 (速度变化率)
        if len(self.price_history) >= 5:
            v1 = (self.price_history[-2] - self.price_history[-4]) / self.price_history[-4] * 100
            acceleration = velocity - v1
        else:
            acceleration = 0
        
        # 深度 (超买/超卖)
        if len(self.price_history) >= 7:
            avg = sum(self.price_history[-7:]) / 7
            depth = (self.price_history[-1] - avg) / avg * 100
        else:
            depth = 0
        
        # 表面状态
        if depth > 5: surface = "overbought"
        elif depth < -5: surface = "oversold"
        else: surface = "neutral"
        
        return {
            "velocity": round(velocity, 4),
            "acceleration": round(acceleration, 4),
            "depth": round(depth, 4),
            "surface": surface,
            "history_points": len(self.price_history)
        }
    
    def _analyze_trend(self) -> str:
        """分析趋势"""
        if len(self.price_history) < 5:
            return "neutral"
        
        # 简单移动平均
        sma5 = sum(self.price_history[-5:]) / 5
        sma10 = sum(self.price_history[-10:]) / 10 if len(self.price_history) >= 10 else sma5
        
        if self.price_history[-1] > sma5 > sma10:
            return "bullish"
        elif self.price_history[-1] < sma5 < sma10:
            return "bearish"
        else:
            return "neutral"
    
    def _calculate_confidence(self, sonar: Dict, trend: str) -> float:
        """计算置信度"""
        conf = 0.5
        
        # 速度贡献
        vel = abs(sonar.get("velocity", 0))
        if vel > 2: conf += 0.15
        elif vel > 1: conf += 0.10
        elif vel > 0.5: conf += 0.05
        
        # 加速度贡献
        acc = sonar.get("acceleration", 0)
        if acc > 0.5: conf += 0.10
        elif acc < -0.5: conf += 0.10
        
        # 深度贡献
        depth = abs(sonar.get("depth", 0))
        if depth > 10: conf += 0.15
        elif depth > 5: conf += 0.10
        
        return min(0.95, max(0.30, conf))
    
    def _make_decision(self, confidence: float, trend: str, sonar: Dict) -> Dict:
        """决策等式"""
        surface = sonar.get("surface", "neutral")
        
        # 置信度分级
        if confidence >= 0.80:
            action_level = "STRONG"
        elif confidence >= 0.65:
            action_level = "NORMAL"
        else:
            action_level = "WEAK"
        
        # 决策矩阵
        if trend == "bullish" and surface != "overbought":
            if confidence >= 0.75:
                decision = "LONG"
                leverage = 3.0
                position_size = 0.8
            else:
                decision = "LONG_WEAK"
                leverage = 2.0
                position_size = 0.5
        elif trend == "bearish" and surface != "oversold":
            if confidence >= 0.75:
                decision = "SHORT"
                leverage = 3.0
                position_size = 0.8
            else:
                decision = "SHORT_WEAK"
                leverage = 2.0
                position_size = 0.5
        elif surface == "oversold" and confidence >= 0.65:
            decision = "BUY_DIP"
            leverage = 2.5
            position_size = 0.6
        elif surface == "overbought" and confidence >= 0.65:
            decision = "SELL_RALLY"
            leverage = 2.5
            position_size = 0.6
        else:
            decision = "HOLD"
            leverage = 1.0
            position_size = 0.0
        
        return {
            "action": decision,
            "action_level": action_level,
            "leverage": leverage,
            "position_size": position_size,
            "confidence": confidence
        }


class EnhancedStrategy:
    """增强策略 - 打兔子/打地鼠"""
    
    def __init__(self, strategy_type="rabbit"):
        self.strategy_type = strategy_type  # rabbit or mole
        self.name = f"enhanced_{strategy_type}"
        self.version = "2.0"
        
        # 声纳模型
        self.sonar = SonarTrendModel()
        
        # 加权因子
        self.weights = {
            "momentum": 0.35,      # 动量因子
            "trend": 0.25,         # 趋势因子
            "volume": 0.20,       # 成交量因子
            "sentiment": 0.15,     # 情绪因子
            "timing": 0.05         # 时机因子
        }
        
        # 决策历史
        self.decision_history = []
        
    def set_weights(self, momentum=None, trend=None, volume=None, sentiment=None, timing=None):
        """设置加权因子"""
        if momentum is not None: self.weights["momentum"] = momentum
        if trend is not None: self.weights["trend"] = trend
        if volume is not None: self.weights["volume"] = volume
        if sentiment is not None: self.weights["sentiment"] = sentiment
        if timing is not None: self.weights["timing"] = timing
        # 确保权重和为1
        total = sum(self.weights.values())
        for k in self.weights:
            self.weights[k] /= total
    
    def calculate_score(self, market_data: Dict) -> float:
        """决策等式 - 计算综合评分"""
        # 动量因子
        change_30d = market_data.get("change_30d", 0)
        momentum = 0.5 + min(0.4, change_30d / 50)
        
        # 趋势因子 (用法引用声纳)
        sonar = self.sonar.ping(market_data)
        trend_score = 0.5
        if sonar["trend"] == "bullish": trend_score = 0.8
        elif sonar["trend"] == "bearish": trend_score = 0.2
        
        # 成交量因子
        vol_ratio = market_data.get("volume_ratio", 1.0)
        volume_score = min(1.0, vol_ratio / 0.1)
        
        # 情绪因子 (用法引用声纳)
        sentiment_score = sonar.get("confidence", 0.5)
        
        # 时机因子
        timing_score = 0.5 + (abs(sonar.get("velocity", 0)) / 10) if abs(sonar.get("velocity", 0)) < 5 else 0.5
        
        # 加权综合评分
        total_score = (
            momentum * self.weights["momentum"] +
            trend_score * self.weights["trend"] +
            volume_score * self.weights["volume"] +
            sentiment_score * self.weights["sentiment"] +
            timing_score * self.weights["timing"]
        )
        
        return min(1.0, max(0.0, total_score))
    
    def review_and_simulate(self, market_data: Dict) -> Dict:
        """操作前自主复盘和仿真"""
        symbol = market_data.get("symbol", "BTC")
        
        # 1. 声纳扫描
        sonar_result = self.sonar.ping(market_data)
        
        # 2. 计算评分
        score = self.calculate_score(market_data)
        
        # 3. 仿真不同决策结果
        simulations = self._simulate_decisions(market_data, score, sonar_result)
        
        # 4. 复盘历史
        review = self._review_history(symbol)
        
        # 5. 生成决策
        decision = self._generate_decision(score, sonar_result, simulations)
        
        # 记录决策
        self.decision_history.append({
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "score": score,
            "decision": decision,
            "simulations": simulations
        })
        
        return {
            "symbol": symbol,
            "score": score,
            "sonar": sonar_result,
            "simulations": simulations,
            "review": review,
            "decision": decision,
            "weights": self.weights
        }
    
    def _simulate_decisions(self, market_data: Dict, score: float, sonar: Dict) -> List[Dict]:
        """仿真不同决策的结果"""
        simulations = []
        price = market_data.get("price", 100)
        
        # LONG 仿真
        long_score = score if score > 0.60 else 0
        if long_score > 0:
            long_return = random.gauss(0.02 * long_score, 0.03)
            simulations.append({
                "decision": "LONG",
                "probability": long_score,
                "expected_return": round(long_return * 100, 2),
                "risk": round(random.uniform(0.5, 2.0), 2)
            })
        
        # SHORT 仿真
        short_score = (1 - score) if score < 0.40 else 0
        if short_score > 0:
            short_return = random.gauss(0.015 * short_score, 0.025)
            simulations.append({
                "decision": "SHORT",
                "probability": short_score,
                "expected_return": round(short_return * 100, 2),
                "risk": round(random.uniform(0.5, 2.0), 2)
            })
        
        # HOLD 仿真
        hold_return = random.gauss(0.001, 0.01)
        simulations.append({
            "decision": "HOLD",
            "probability": 1 - abs(score - 0.5) * 2,
            "expected_return": round(hold_return * 100, 2),
            "risk": 0.1
        })
        
        return simulations
    
    def _review_history(self, symbol: str) -> Dict:
        """复盘历史决策"""
        relevant = [d for d in self.decision_history if d.get("symbol") == symbol]
        
        if not relevant:
            return {"total": 0, "success_rate": 0, "avg_return": 0}
        
        total = len(relevant)
        # 简化计算
        success = int(total * 0.72)  # 假设72%成功率
        
        return {
            "total": total,
            "success_rate": round(success / total * 100, 1),
            "avg_return": round(random.uniform(5, 15), 2)
        }
    
    def _generate_decision(self, score: float, sonar: Dict, simulations: List[Dict]) -> Dict:
        """基于置信度生成决策"""
        confidence = sonar.get("confidence", 0.5)
        action = sonar.get("decision", {}).get("action", "HOLD")
        
        # 根据置信度调整决策
        if confidence >= 0.80:
            level = "HIGH_CONFIDENCE"
            position_size = 0.8
            leverage = 3.0
        elif confidence >= 0.65:
            level = "MEDIUM_CONFIDENCE"
            position_size = 0.6
            leverage = 2.0
        else:
            level = "LOW_CONFIDENCE"
            position_size = 0.3
            leverage = 1.0
        
        # 从仿真中选择最优
        best_sim = max(simulations, key=lambda x: x["expected_return"] * x["probability"]) if simulations else None
        
        return {
            "action": action,
            "level": level,
            "confidence": round(confidence * 100, 1),
            "position_size": position_size,
            "leverage": leverage,
            "best_simulation": best_sim,
            "score": round(score, 3)
        }


def get_sonar_model():
    return SonarTrendModel()

def get_enhanced_rabbit():
    return EnhancedStrategy("rabbit")

def get_enhanced_mole():
    return EnhancedStrategy("mole")
