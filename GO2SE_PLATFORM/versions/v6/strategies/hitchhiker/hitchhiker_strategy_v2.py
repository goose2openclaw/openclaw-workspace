#!/usr/bin/env python3
"""
🌐 搭便车策略 V2 - 跟单分成增强版
========================================
增强:
- 交易员排名算法优化 (Sharpe+胜率+盈亏比)
- 风险控制 (最大回撤限制)
- 自动再平衡
- 跨交易所跟单
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class HitchhikerStrategyV2:
    """搭便车 V2 - 跟单分成"""

    def __init__(self, config: dict = None):
        self.config = config or self._default_config()
        self._trader_cache = {}
        self._performance_cache = {}

    def _default_config(self) -> dict:
        return {
            'min_win_rate': 0.55,
            'min_profit_ratio': 1.8,
            'min_30d_return': 0.08,
            'max_drawdown': 0.20,
            'min_trades': 20,
            'min_followers': 50,
            'max_position_per_trader': 0.05,
            'total_max_position': 0.30,
            'rebalance_interval_hours': 6,
            'stop_loss_multiplier': 2.0,
        }

    def get_top_traders(self, min_score: float = 60) -> List[Dict]:
        """获取顶级交易员"""
        traders = self._fetch_traders()
        ranked = []
        for t in traders:
            score = self._score_trader(t)
            if score >= min_score:
                t['overall_score'] = round(score, 1)
                t['grade'] = self._grade(score)
                ranked.append(t)
        return sorted(ranked, key=lambda x: x['overall_score'], reverse=True)

    def _fetch_traders(self) -> List[Dict]:
        """获取交易员数据 (模拟)"""
        return [
            {'id': 't001', 'name': 'WhaleHunter', 'exchange': 'binance', 'win_rate': 0.72, 'profit_ratio': 3.2, 'return_30d': 0.18, 'max_drawdown': 0.12, 'total_trades': 245, 'followers': 890, 'specialty': ['BTC','ETH','SOL'], 'sharpe': 2.1},
            {'id': 't002', 'name': 'DeFiMaster', 'exchange': 'binance', 'win_rate': 0.68, 'profit_ratio': 2.8, 'return_30d': 0.15, 'max_drawdown': 0.18, 'total_trades': 156, 'followers': 520, 'specialty': ['SOL','ARB','OP'], 'sharpe': 1.8},
            {'id': 't003', 'name': 'TrendRider', 'exchange': 'bybit', 'win_rate': 0.65, 'profit_ratio': 2.5, 'return_30d': 0.12, 'max_drawdown': 0.15, 'total_trades': 312, 'followers': 1100, 'specialty': ['BTC','XRP'], 'sharpe': 1.6},
            {'id': 't004', 'name': 'MomentumKing', 'exchange': 'okx', 'win_rate': 0.70, 'profit_ratio': 2.2, 'return_30d': 0.20, 'max_drawdown': 0.22, 'total_trades': 89, 'followers': 340, 'specialty': ['ALT'], 'sharpe': 1.9},
            {'id': 't005', 'name': 'SwingTrader', 'exchange': 'binance', 'win_rate': 0.62, 'profit_ratio': 3.5, 'return_30d': 0.10, 'max_drawdown': 0.08, 'total_trades': 178, 'followers': 670, 'specialty': ['ETH','BNB'], 'sharpe': 1.7},
        ]

    def _score_trader(self, trader: Dict) -> float:
        """综合评分"""
        # 基本过滤
        if trader['win_rate'] < self.config['min_win_rate']:
            return 0
        if trader['profit_ratio'] < self.config['min_profit_ratio']:
            return 0
        if trader['return_30d'] < self.config['min_30d_return']:
            return 0
        if trader['max_drawdown'] > self.config['max_drawdown']:
            return 0
        if trader['total_trades'] < self.config['min_trades']:
            return 0

        # 加权评分
        wr_score = trader['win_rate'] * 30
        pr_score = min(trader['profit_ratio'] / 4, 1.0) * 25
        ret_score = min(trader['return_30d'] / 0.30, 1.0) * 20
        dd_score = max(0, (0.30 - trader['max_drawdown']) / 0.30) * 15
        sharpe_score = min(trader.get('sharpe', 1.0) / 3.0, 1.0) * 10

        return wr_score + pr_score + ret_score + dd_score + sharpe_score

    def _grade(self, score: float) -> str:
        if score >= 85: return 'S+'
        elif score >= 75: return 'S'
        elif score >= 65: return 'A'
        elif score >= 55: return 'B'
        else: return 'C'

    def get_allocation(self, traders: List[Dict], capital: float) -> List[Dict]:
        """计算跟单分配"""
        total_weight = 0
        weights = []

        for t in traders[:5]:  # 最多跟5个
            w = t['overall_score'] * (1 - t['max_drawdown'])
            weights.append(w)
            total_weight += w

        allocations = []
        for i, t in enumerate(traders[:5]):
            weight = weights[i] / total_weight if total_weight > 0 else 0
            position = min(capital * weight, capital * self.config['max_position_per_trader'])
            allocations.append({
                'trader_id': t['id'],
                'name': t['name'],
                'grade': t['grade'],
                'score': t['overall_score'],
                'allocation_usd': round(position, 2),
                'allocation_pct': round(weight * 100, 2),
                'stop_loss_pct': round(t['max_drawdown'] * self.config['stop_loss_multiplier'], 2),
                'specialty': t['specialty'],
            })

        return allocations

    def simulate_performance(self, traders: List[Dict], days: int = 30) -> Dict:
        """模拟跟单表现"""
        import random
        daily_returns = []
        capital = 10000.0

        for d in range(days):
            day_ret = 0
            for t in traders[:3]:
                prob = t['win_rate']
                ret = (random.random() < prob) * random.uniform(0.01, 0.05) * t['profit_ratio']
                ret -= (random.random() < (1 - prob)) * random.uniform(0.005, 0.02)
                day_ret += ret * 0.33  # 等权
            day_ret = max(-0.05, min(0.08, day_ret))
            capital *= (1 + day_ret)
            daily_returns.append(round(day_ret * 100, 3))

        total_return = (capital - 10000) / 10000 * 100
        wins = sum(1 for r in daily_returns if r > 0)
        wr = wins / len(daily_returns) * 100

        return {
            'total_return': round(total_return, 2),
            'final_capital': round(capital, 2),
            'win_rate': round(wr, 1),
            'best_day': max(daily_returns),
            'worst_day': min(daily_returns),
            'daily_returns': daily_returns,
            'sharpe_estimate': round(total_return / max(abs(min(daily_returns)), 1) * 0.5, 2),
        }


_hitchhiker_v2 = None
def get_hitchhiker_v2_strategy():
    global _hitchhiker_v2
    if _hitchhiker_v2 is None:
        _hitchhiker_v2 = HitchhikerStrategyV2()
    return _hitchhiker_v2
