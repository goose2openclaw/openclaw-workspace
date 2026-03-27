#!/usr/bin/env python3
"""
🧠 专家模式核心引擎
Version: 1.0
Author: GO2SE CEO

整合7大策略，统一决策
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

# 导入7大策略
from rabbit.rabbit_strategy import RabbitStrategy
from mole.mole_strategy import MoleStrategy
from oracle.oracle_strategy import OracleStrategy
from leader.leader_strategy import LeaderStrategy
from hitchhiker.hitchhiker_strategy import HitchhikerStrategy
from airdrop.airdrop_strategy import AirdropStrategy
from crowdsource.crowdsource_strategy import CrowdsourceStrategy


@dataclass
class TradeSignal:
    """交易信号"""
    strategy: str
    symbol: str
    signal: str  # buy, sell, neutral
    confidence: float
    position_size: float
    stop_loss: float
    take_profit: float
    reason: str
    timestamp: str


class ExpertEngine:
    """专家模式核心引擎"""
    
    def __init__(self):
        # 初始化7大策略
        self.strategies = {
            'rabbit': RabbitStrategy(),
            'mole': MoleStrategy(),
            'oracle': OracleStrategy(),
            'leader': LeaderStrategy(),
            'hitchhiker': HitchhikerStrategy(),
            'airdrop': AirdropStrategy(),
            'crowdsource': CrowdsourceStrategy(),
        }
        
        # 策略权重 (算力分配)
        self.weights = {
            'rabbit': 0.25,      # 25%
            'mole': 0.20,        # 20%
            'oracle': 0.15,      # 15%
            'leader': 0.15,     # 15%
            'hitchhiker': 0.10, # 10%
            'airdrop': 0.03,    # 3%
            'crowdsource': 0.02, # 2%
        }
        
    def analyze_market(self) -> dict:
        """全面市场分析"""
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'strategies': {},
            'aggregated_signals': [],
            'final_recommendation': None
        }
        
        # 1. 运行7大策略
        for name, strategy in self.strategies.items():
            try:
                if name in ['rabbit', 'mole', 'oracle', 'leader', 'hitchhiker']:
                    # 这些返回信号
                    signals = self._get_signals(name, strategy)
                    analysis['strategies'][name] = {
                        'status': 'active',
                        'signals': signals,
                        'weight': self.weights[name]
                    }
                elif name == 'airdrop':
                    # 空投策略
                    plan = strategy.generate_plan(strategy.get_upcoming_airdrops()[0])
                    analysis['strategies'][name] = {
                        'status': 'active',
                        'plan': plan,
                        'weight': self.weights[name]
                    }
                elif name == 'crowdsource':
                    # 众包策略
                    plan = strategy.generate_plan()
                    analysis['strategies'][name] = {
                        'status': 'active',
                        'plan': plan,
                        'weight': self.weights[name]
                    }
            except Exception as e:
                analysis['strategies'][name] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        # 2. 聚合信号
        analysis['aggregated_signals'] = self._aggregate_signals(analysis)
        
        # 3. 生成最终建议
        analysis['final_recommendation'] = self._generate_recommendation(analysis)
        
        return analysis
    
    def _get_signals(self, name: str, strategy) -> List[dict]:
        """获取策略信号"""
        signals = []
        
        if name == 'rabbit':
            candidates = strategy.get_candidates()
            for c in candidates[:3]:
                sig = strategy.generate_signal(c['symbol'])
                signals.append(sig)
        
        elif name == 'mole':
            candidates = strategy.get_candidates()
            for c in candidates[:3]:
                sig = strategy.generate_signal(c['symbol'])
                signals.append(sig)
        
        elif name == 'oracle':
            sig = strategy.generate_signal()
            if sig['confidence'] > 0:
                signals.append(sig)
        
        elif name == 'leader':
            candidates = strategy.get_candidates()
            for c in candidates[:2]:
                sig = strategy.generate_signal(c['symbol'])
                signals.append(sig)
        
        elif name == 'hitchhiker':
            signals = strategy.generate_signals()
        
        return signals
    
    def _aggregate_signals(self, analysis: dict) -> List[dict]:
        """聚合所有信号"""
        all_signals = []
        
        for name, data in analysis['strategies'].items():
            if 'signals' in data:
                for sig in data['signals']:
                    sig['strategy_weight'] = data['weight']
                    sig['weighted_confidence'] = sig['confidence'] * data['weight']
                    all_signals.append(sig)
        
        # 按加权置信度排序
        return sorted(all_signals, key=lambda x: x.get('weighted_confidence', 0), reverse=True)
    
    def _generate_recommendation(self, analysis: dict) -> dict:
        """生成最终建议"""
        signals = analysis['aggregated_signals']
        
        if not signals:
            return {
                'action': 'wait',
                'confidence': 0,
                'reason': '无可用信号'
            }
        
        # 选取最佳信号
        best = signals[0]
        
        # 检查置信度阈值
        if best['weighted_confidence'] < 2.5:  # 低于2.5分
            return {
                'action': 'wait',
                'confidence': best['weighted_confidence'],
                'reason': '置信度不足'
            }
        
        # 生成执行计划
        action = 'buy' if best['signal'] in ['buy', 'yes', 'copy_buy'] else \
                 'sell' if best['signal'] in ['sell', 'no', 'copy_sell'] else 'wait'
        
        # 汇总多策略信号
        buy_signals = [s for s in signals if s['signal'] in ['buy', 'yes', 'copy_buy']]
        sell_signals = [s for s in signals if s['signal'] in ['sell', 'no', 'copy_sell']]
        
        return {
            'action': action,
            'primary_signal': best,
            'confidence': best['weighted_confidence'],
            'buy_count': len(buy_signals),
            'sell_count': len(sell_signals),
            'recommended_symbol': best.get('symbol', best.get('market_id')),
            'position_size': best.get('position_size', 0),
            'stop_loss': best.get('stop_loss', -0.10),
            'take_profit': best.get('take_profit', 0.30),
            'timestamp': datetime.now().isoformat()
        }
    
    def calculate_confidence(self, market_data: dict) -> float:
        """计算置信度 (5步法)"""
        confidence = 0
        
        # 第1步: 市场状态分析 (权重40%)
        tech_score = self._evaluate_technical(market_data)
        confidence += tech_score * 0.40
        
        # 第2步: 声纳模型匹配 (权重已包含在信号中)
        # 直接使用策略输出
        
        # 第3步: 策略组合 (权重已分配)
        # 已通过加权计算
        
        # 第4步: 风险评估 (已包含在仓位计算中)
        risk_score = self._evaluate_risk(market_data)
        
        # 第5步: 综合评分
        final_confidence = min(10, confidence)
        
        return final_confidence
    
    def _evaluate_technical(self, data: dict) -> float:
        """技术面评估"""
        # 简化的技术指标评分
        score = 5.0
        
        # RSI
        rsi = data.get('rsi', 50)
        if 30 < rsi < 70:
            score += 1
        elif rsi < 30 or rsi > 70:
            score -= 1
        
        return score
    
    def _evaluate_risk(self, data: dict) -> float:
        """风险评估"""
        score = 5.0
        
        # 波动率
        volatility = data.get('volatility', 0)
        if volatility > 0.10:
            score -= 2
        elif volatility > 0.05:
            score -= 1
        
        return score
    
    def execute_trade(self, recommendation: dict) -> dict:
        """执行交易"""
        if recommendation['action'] == 'wait':
            return {'status': 'skipped', 'reason': recommendation['reason']}
        
        # 实际执行交易
        # 这里需要接入交易所API
        return {
            'status': 'executed',
            'action': recommendation['action'],
            'symbol': recommendation['recommended_symbol'],
            'size': recommendation['position_size'],
            'stop_loss': recommendation['stop_loss'],
            'take_profit': recommendation['take_profit'],
            'confidence': recommendation['confidence'],
            'timestamp': datetime.now().isoformat()
        }


# 主程序
if __name__ == '__main__':
    engine = ExpertEngine()
    
    print("🧠 专家模式引擎 - 启动分析")
    print("=" * 50)
    
    # 1. 全面市场分析
    analysis = engine.analyze_market()
    
    print(f"\n📊 策略信号汇总:")
    for sig in analysis['aggregated_signals'][:5]:
        print(f"  {sig['strategy']}: {sig.get('symbol', 'N/A')} | {sig['signal']} | 置信度 {sig.get('weighted_confidence', 0):.2f}")
    
    # 2. 最终建议
    rec = analysis['final_recommendation']
    print(f"\n🎯 最终建议:")
    print(f"  操作: {rec['action']}")
    print(f"  标的: {rec.get('recommended_symbol', 'N/A')}")
    print(f"  置信度: {rec.get('confidence', 0):.2f}")
    print(f"  仓位: {rec.get('position_size', 0)*100:.1f}%")
    print(f"  止损: {rec.get('stop_loss', 0)*100:.1f}%")
    print(f"  止盈: {rec.get('take_profit', 0)*100:.1f}%")
