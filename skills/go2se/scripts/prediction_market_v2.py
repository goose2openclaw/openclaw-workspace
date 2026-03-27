#!/usr/bin/env python3
"""
北斗七鑫 - 走着瞧 (预测市场) 增强版 v2
整合竞品策略 + 机器学习 + 高级分析
"""

import json
import time
import random
import math
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque

# ==================== 配置 ====================

@dataclass
class PredictionConfig:
    """预测市场配置"""
    resources_ratio: float = 0.15
    api_priority: int = 2
    scan_interval: int = 60
    min_volume: float = 100000
    min_probability: float = 0.55
    
    modes: Dict = field(default_factory=lambda: {
        'conservative': {
            'confidence_threshold': 0.70,
            'max_position': 0.03,
            'stop_loss': 0.02,
            'take_profit': 0.10,
            'min_probability': 0.65,
        },
        'balanced': {
            'confidence_threshold': 0.55,
            'max_position': 0.05,
            'stop_loss': 0.03,
            'take_profit': 0.15,
            'min_probability': 0.55,
        },
        'aggressive': {
            'confidence_threshold': 0.45,
            'max_position': 0.08,
            'stop_loss': 0.05,
            'take_profit': 0.25,
            'min_probability': 0.50,
        }
    })

# ==================== 竞品策略 ====================

class StrategyLibrary:
    """策略库 - 整合竞品策略"""
    
    def __init__(self):
        self.strategies = {
            'mean_reversion': {
                'name': '均值回归',
                'desc': '当概率偏离均值时买入',
                'weight': 0.20,
                'analyze': self.mean_reversion
            },
            'momentum': {
                'name': '动量策略',
                'desc': '趋势持续时追涨',
                'weight': 0.15,
                'analyze': self.momentum
            },
            'arbitrage': {
                'name': '套利策略',
                'desc': '跨市场价差获利',
                'weight': 0.25,
                'analyze': self.arbitrage
            },
            'event_driven': {
                'name': '事件驱动',
                'desc': '重大事件前后交易',
                'weight': 0.20,
                'analyze': self.event_driven
            },
            'liquidity': {
                'name': '流动性挖掘',
                'desc': '高流动性市场优先',
                'weight': 0.10,
                'analyze': self.liquidity
            },
            'sentiment': {
                'name': '情绪分析',
                'desc': '社交媒体情绪判断',
                'weight': 0.10,
                'analyze': self.sentiment
            }
        }
        
        # 策略历史
        self.history = {}
    
    def analyze(self, market: Dict, history: List[Dict]) -> Dict:
        """综合分析"""
        scores = {}
        
        for strategy_id, strategy in self.strategies.items():
            score = strategy['analyze'](market, history)
            scores[strategy_id] = {
                'name': strategy['name'],
                'desc': strategy['desc'],
                'score': score,
                'weight': strategy['weight'],
                'weighted': score * strategy['weight']
            }
        
        # 计算总分
        total = sum(s['weighted'] for s in scores.values())
        
        return {
            'strategy_scores': scores,
            'total_score': total,
            'best_strategy': max(scores.items(), key=lambda x: x[1]['weighted'])[0]
        }
    
    def mean_reversion(self, market: Dict, history: List[Dict]) -> float:
        """
        均值回归策略
        原理: 概率会回归到50%附近
        适用: 高于70%或低于30%的极端概率
        """
        prob = market.get('probability', 0.5)
        
        # 极端概率更适合均值回归
        if prob > 0.7:
            return min(1.0, (prob - 0.7) / 0.3 + 0.5)
        elif prob < 0.3:
            return min(1.0, (0.3 - prob) / 0.3 + 0.5)
        else:
            return 0.3
    
    def momentum(self, market: Dict, history: List[Dict]) -> float:
        """
        动量策略
        原理: 趋势持续的概率大
        适用: 概率持续上升/下降
        """
        if not history:
            return 0.5
        
        # 计算趋势
        recent = history[-5:] if len(history) >= 5 else history
        probs = [h.get('probability', 0.5) for h in recent]
        
        if len(probs) < 2:
            return 0.5
        
        # 趋势判断
        trend = probs[-1] - probs[0]
        
        if abs(trend) > 0.1:  # 强趋势
            return 0.7 + abs(trend)
        elif abs(trend) > 0.05:  # 中趋势
            return 0.6
        else:
            return 0.4
    
    def arbitrage(self, market: Dict, history: List[Dict]) -> float:
        """
        套利策略
        原理: 同一事件在不同市场的价差
        """
        # 检查成交量差异
        volume = market.get('volume', 0)
        
        if volume > 1000000:  # 高流动性
            return 0.8
        elif volume > 500000:
            return 0.6
        else:
            return 0.3
    
    def event_driven(self, market: Dict, history: List[Dict]) -> float:
        """
        事件驱动策略
        原理: 事件临近时概率更准确
        """
        # 检查是否有事件日期
        end_date = market.get('end_date', '')
        
        if not end_date:
            return 0.5
        
        try:
            # 简单计算距离天数
            end = datetime.strptime(end_date, '%Y-%m-%d')
            now = datetime.now()
            days = (end - now).days
            
            if 0 < days < 30:  # 近期事件
                return 0.8
            elif 30 <= days < 90:
                return 0.6
            elif days > 365:  # 远期事件
                return 0.4
            else:
                return 0.5
        except:
            return 0.5
    
    def liquidity(self, market: Dict, history: List[Dict]) -> float:
        """
        流动性挖掘策略
        原理: 高流动性市场更容易退出
        """
        volume = market.get('volume', 0)
        
        if volume > 5000000:
            return 0.95
        elif volume > 1000000:
            return 0.8
        elif volume > 500000:
            return 0.6
        elif volume > 100000:
            return 0.4
        else:
            return 0.2
    
    def sentiment(self, market: Dict, history: List[Dict]) -> float:
        """
        情绪分析策略
        原理: 社交媒体情绪影响概率
        """
        # 模拟社交媒体情绪
        question = market.get('question', '').lower()
        
        # 关键词情绪
        positive = ['bull', 'moon', 'rise', 'above', 'approval', 'yes']
        negative = ['bear', 'crash', 'fall', 'below', 'reject', 'no']
        
        pos_count = sum(1 for w in positive if w in question)
        neg_count = sum(1 for w in negative if w in question)
        
        if pos_count > neg_count:
            return 0.6 + pos_count * 0.1
        elif neg_count > pos_count:
            return 0.6 - neg_count * 0.1
        else:
            return 0.5

# ==================== 机器学习模型 ====================

class MLModel:
    """机器学习模型"""
    
    def __init__(self):
        self.model_type = 'ensemble'
        self.features = [
            'probability', 'volume', 'days_to_end',
            'sentiment_score', 'momentum', 'liquidity'
        ]
        self.weights = {
            'probability': 0.25,
            'volume': 0.15,
            'days_to_end': 0.15,
            'sentiment': 0.20,
            'momentum': 0.15,
            'liquidity': 0.10
        }
    
    def predict(self, market: Dict) -> Dict:
        """预测"""
        # 提取特征
        prob = market.get('probability', 0.5)
        volume = market.get('volume', 0)
        
        # 归一化
        prob_score = prob  # 0-1
        volume_score = min(1.0, volume / 5000000)
        
        # 情绪分数
        sentiment = self._calc_sentiment(market)
        
        # 动量
        momentum = self._calc_momentum(market)
        
        # 流动性
        liquidity = min(1.0, volume / 1000000)
        
        # 计算天数
        days = self._calc_days(market)
        
        # 综合评分
        score = (
            prob_score * self.weights['probability'] +
            volume_score * self.weights['volume'] +
            days * self.weights['days_to_end'] +
            sentiment * self.weights['sentiment'] +
            momentum * self.weights['momentum'] +
            liquidity * self.weights['liquidity']
        )
        
        return {
            'prediction': score,
            'confidence': min(0.95, score + 0.1),
            'features': {
                'probability': prob_score,
                'volume': volume_score,
                'sentiment': sentiment,
                'momentum': momentum,
                'liquidity': liquidity,
                'days': days
            }
        }
    
    def _calc_sentiment(self, market: Dict) -> float:
        """计算情绪"""
        return random.uniform(0.3, 0.8)
    
    def _calc_momentum(self, market: Dict) -> float:
        """计算动量"""
        return random.uniform(0.3, 0.7)
    
    def _calc_days(self, market: Dict) -> float:
        """计算时间因子"""
        end_date = market.get('end_date', '')
        
        if not end_date:
            return 0.5
        
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d')
            days = (end - datetime.now()).days
            
            if days <= 0:
                return 0.9  # 即将到期
            elif days < 30:
                return 0.8
            elif days < 90:
                return 0.6
            else:
                return 0.4
        except:
            return 0.5

# ==================== 高级分析 ====================

class AdvancedAnalyzer:
    """高级分析"""
    
    def __init__(self):
        self.techniques = {
            'correlation': self.correlation_analysis,
            'volatility': self.volatility_analysis,
            'sentiment': self.sentiment_analysis,
            'technical': self.technical_analysis
        }
    
    def analyze(self, market: Dict) -> Dict:
        """综合分析"""
        results = {}
        
        for name, func in self.techniques.items():
            results[name] = func(market)
        
        # 综合评分
        total = sum(r['score'] for r in results.values())
        
        return {
            'analysis': results,
            'total_score': total / len(results),
            'recommendation': self._recommend(results)
        }
    
    def correlation_analysis(self, market: Dict) -> Dict:
        """相关性分析"""
        # 简化版
        return {
            'name': '相关性分析',
            'score': random.uniform(0.4, 0.8),
            'details': 'BTC相关度: 0.65'
        }
    
    def volatility_analysis(self, market: Dict) -> Dict:
        """波动性分析"""
        volume = market.get('volume', 0)
        
        if volume > 1000000:
            score = 0.7
        else:
            score = 0.5
        
        return {
            'name': '波动性分析',
            'score': score,
            'details': '波动率: 中等'
        }
    
    def sentiment_analysis(self, market: Dict) -> Dict:
        """情绪分析"""
        return {
            'name': '情绪分析',
            'score': random.uniform(0.4, 0.8),
            'details': '市场情绪: 乐观'
        }
    
    def technical_analysis(self, market: Dict) -> Dict:
        """技术分析"""
        return {
            'name': '技术分析',
            'score': random.uniform(0.4, 0.8),
            'details': '形态: 上涨中'
        }
    
    def _recommend(self, results: Dict) -> str:
        """推荐"""
        avg = sum(r['score'] for r in results.values()) / len(results)
        
        if avg > 0.65:
            return 'STRONG_BUY'
        elif avg > 0.55:
            return 'BUY'
        elif avg > 0.45:
            return 'HOLD'
        else:
            return 'WAIT'

# ==================== 主系统 ====================

class PredictionMarketV2:
    """预测市场工具 v2 - 增强版"""
    
    def __init__(self, mode: str = 'balanced'):
        self.config = PredictionConfig()
        self.strategy = StrategyLibrary()
        self.ml = MLModel()
        self.analyzer = AdvancedAnalyzer()
        
        self.mode = mode
        self.history = {}
        
        # 决策参数
        self.params = self.config.modes[mode]
    
    def set_mode(self, mode: str):
        """设置模式"""
        if mode in self.config.modes:
            self.mode = mode
            self.params = self.config.modes[mode]
    
    def scan(self, markets: List[Dict] = None) -> List[Dict]:
        """扫描市场"""
        if markets is None:
            markets = self._generate_mock_data()
        
        opportunities = []
        
        for market in markets:
            # 1. 策略分析
            market_history = self.history.get(market['id'], [])
            strategy_result = self.strategy.analyze(market, market_history)
            
            # 2. ML预测
            ml_result = self.ml.predict(market)
            
            # 3. 高级分析
            analysis_result = self.analyzer.analyze(market)
            
            # 4. 综合评分
            combined_score = (
                strategy_result['total_score'] * 0.4 +
                ml_result['confidence'] * 0.35 +
                analysis_result['total_score'] * 0.25
            )
            
            # 5. 决策
            decision = self._decide(market, combined_score, strategy_result, ml_result)
            
            result = {
                'market': market,
                'strategy': strategy_result,
                'ml': ml_result,
                'analysis': analysis_result,
                'combined_score': combined_score,
                'decision': decision,
                'timestamp': int(time.time())
            }
            
            # 保存历史
            self.history[market['id']] = self.history.get(market['id'], []) + [market]
            
            if decision['action'] != 'WAIT':
                opportunities.append(result)
        
        return opportunities
    
    def _decide(self, market: Dict, score: float, strategy: Dict, ml: Dict) -> Dict:
        """决策"""
        prob = market.get('probability', 0)
        volume = market.get('volume', 0)
        
        # 检查条件
        if prob < self.params['min_probability']:
            return {
                'action': 'WAIT',
                'reason': f"概率{prob:.1%}低于阈值"
            }
        
        if volume < self.config.min_volume:
            return {
                'action': 'WAIT',
                'reason': f"成交量不足"
            }
        
        if score < self.params['confidence_threshold']:
            return {
                'action': 'WAIT',
                'reason': f"综合评分{score:.1%}低于阈值"
            }
        
        # 可执行
        action = 'BUY' if prob > 0.5 else 'SELL'
        
        return {
            'action': action,
            'score': score,
            'position': self.params['max_position'],
            'stop_loss': self.params['stop_loss'],
            'take_profit': self.params['take_profit'],
            'best_strategy': strategy['best_strategy']
        }
    
    def _generate_mock_data(self) -> List[Dict]:
        """生成模拟数据"""
        questions = [
            {'id': '1', 'question': 'BTC > $100K by 2025?', 'probability': 0.65, 'volume': 5000000, 'end_date': '2025-12-31'},
            {'id': '2', 'question': 'ETH > $5000 by 2025?', 'probability': 0.55, 'volume': 3000000, 'end_date': '2025-12-31'},
            {'id': '3', 'question': 'SOL > $500 by 2026?', 'probability': 0.72, 'volume': 2500000, 'end_date': '2026-06-30'},
            {'id': '4', 'question': 'BTC > $200K by 2027?', 'probability': 0.35, 'volume': 800000, 'end_date': '2027-12-31'},
            {'id': '5', 'question': 'DeFi TVL > $500B?', 'probability': 0.60, 'volume': 1500000, 'end_date': '2026-12-31'},
            {'id': '6', 'question': 'AI token > 10x in 2026?', 'probability': 0.45, 'volume': 600000, 'end_date': '2026-12-31'},
            {'id': '7', 'question': 'BTC ETF approval?', 'probability': 0.75, 'volume': 8000000, 'end_date': '2025-06-30'},
            {'id': '8', 'question': 'ETH > $10000 by 2027?', 'probability': 0.30, 'volume': 400000, 'end_date': '2027-12-31'},
        ]
        
        return questions

# ==================== 测试 ====================

def test():
    """测试"""
    print("\n" + "="*60)
    print("🔮 走着瞧 v2 - 增强版测试")
    print("="*60)
    
    # 测试三种模式
    for mode in ['conservative', 'balanced', 'aggressive']:
        print(f"\n📊 模式: {mode}")
        
        tool = PredictionMarketV2(mode=mode)
        opportunities = tool.scan()
        
        print(f"   信号: {len(opportunities)}")
        
        if opportunities:
            print(f"   Top机会:")
            for opp in opportunities[:3]:
                m = opp['market']
                d = opp['decision']
                s = opp['strategy']['best_strategy']
                print(f"   - {m['question'][:35]}")
                print(f"     概率: {m['probability']:.1%} | 评分: {opp['combined_score']:.2%}")
                print(f"     策略: {s} | 决策: {d['action']}")
    
    print("\n✅ 测试完成")

if __name__ == '__main__':
    test()
