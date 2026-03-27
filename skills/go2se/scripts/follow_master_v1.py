#!/usr/bin/env python3
"""
北斗七鑫 - 跟大哥 (做市协作) v1
做市商协作/流动性做市工具
"""

import json
import time
import random
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque

# ==================== 配置 ====================

@dataclass
class FollowMasterConfig:
    """跟大哥配置"""
    # 资源分配
    resources_ratio: float = 0.15      # 算力15%
    api_priority: int = 2              # API优先级
    
    # 扫描设置
    scan_interval: int = 30            # 30秒
    min_liquidity: float = 100000     # 最小流动性
    min_spread: float = 0.001         # 最小价差0.1%
    
    # 资金配置
    total_funds: float = 10000
    reserve_ratio: float = 0.25        # 备用金25%
    max_position: float = 0.15         # 最大做市仓位
    
    # 三种模式
    modes: Dict = field(default_factory=lambda: {
        'conservative': {
            'min_spread': 0.003,      # 0.3%
            'max_position': 0.05,
            'rebalance_threshold': 0.02,
            'inventory_risk': 0.10,
            'min_order_size': 10,
            'max_slippage': 0.001,
        },
        'balanced': {
            'min_spread': 0.002,      # 0.2%
            'max_position': 0.10,
            'rebalance_threshold': 0.03,
            'inventory_risk': 0.15,
            'min_order_size': 5,
            'max_slippage': 0.002,
        },
        'aggressive': {
            'min_spread': 0.001,      # 0.1%
            'max_position': 0.15,
            'rebalance_threshold': 0.05,
            'inventory_risk': 0.20,
            'min_order_size': 1,
            'max_slippage': 0.005,
        }
    })

# ==================== API管理 ====================

class MarketMakingAPI:
    """做市API"""
    
    def __init__(self):
        self.apis = {
            'binance_mm': {'name': 'Binance做市', 'url': 'https://api.binance.com', 'priority': 1},
            'bybit_mm': {'name': 'Bybit做市', 'url': 'https://api.bybit.com', 'priority': 2},
            'okx_mm': {'name': 'OKX做市', 'url': 'https://www.okx.com', 'priority': 3},
            'kucoin_mm': {'name': 'KuCoin做市', 'url': 'https://api.kucoin.com', 'priority': 4},
        }
        
        self.primary = 'binance_mm'
        self.errors = deque(maxlen=30)
    
    def fetch_opportunities(self) -> List[Dict]:
        """获取做市机会"""
        return self._generate_opportunities()
    
    def _generate_opportunities(self) -> List[Dict]:
        """生成做市机会"""
        pairs = [
            'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 
            'XRP/USDT', 'ADA/USDT', 'AVAX/USDT', 'DOT/USDT',
            'MATIC/USDT', 'LINK/USDT', 'UNI/USDT', 'ATOM/USDT'
        ]
        
        opportunities = []
        
        for pair in pairs:
            opportunities.append({
                'pair': pair,
                'bid': random.uniform(0.001, 0.01),       # 买一价差
                'ask': random.uniform(0.001, 0.01),       # 卖一价差
                'spread': random.uniform(0.001, 0.02),    # 价差
                'volume_24h': random.uniform(100000, 10000000),
                'volatility': random.uniform(0.01, 0.10),
                'liquidity_score': random.uniform(0.3, 0.9),
                'maker_fee': 0.001,                       # 做市商手续费
                'platform': random.choice(['binance', 'bybit', 'okx']),
                'opportunity_score': random.uniform(0.3, 0.9),
            })
        
        return opportunities
    
    def get_status(self) -> Dict:
        return {
            'primary': self.primary,
            'apis': {k: v['priority'] for k, v in self.apis.items()},
        }

# ==================== 策略库 ====================

class StrategyLibrary:
    """策略库 - 做市策略"""
    
    def __init__(self):
        self.strategies = {
            'spread_matching': {
                'name': '价差匹配',
                'weight': 0.25,
                'func': self._spread_matching
            },
            'inventory_balanced': {
                'name': '库存平衡',
                'weight': 0.25,
                'func': self._inventory_balanced
            },
            'liquidity_provision': {
                'name': '流动性提供',
                'weight': 0.20,
                'func': self._liquidity_provision
            },
            'volatility_capture': {
                'name': '波动捕获',
                'weight': 0.15,
                'func': self._volatility_capture
            },
            'fee_capture': {
                'name': '手续费捕获',
                'weight': 0.15,
                'func': self._fee_capture
            },
        }
    
    def analyze(self, opp: Dict, inventory: Dict = None) -> Dict:
        """分析做市机会"""
        scores = {}
        
        for sid, s in self.strategies.items():
            score = s['func'](opp, inventory or {})
            scores[sid] = {
                'name': s['name'],
                'score': score,
                'weight': s['weight'],
                'weighted': score * s['weight']
            }
        
        total = sum(s['weighted'] for s in scores.values())
        
        return {
            'scores': scores,
            'total': total,
            'best': max(scores.items(), key=lambda x: x[1]['weighted'])[0]
        }
    
    def _spread_matching(self, opp: Dict, inv: Dict) -> float:
        """价差匹配策略 - 价差越大越好"""
        spread = opp.get('spread', 0)
        
        if spread > 0.015: return 0.95
        elif spread > 0.010: return 0.80
        elif spread > 0.005: return 0.65
        elif spread > 0.002: return 0.50
        return 0.30
    
    def _inventory_balanced(self, opp: Dict, inv: Dict) -> float:
        """库存平衡 - 库存越平衡越好"""
        long_ratio = inv.get('long_ratio', 0.5)
        balanced = 1 - abs(long_ratio - 0.5) * 2
        
        return balanced
    
    def _liquidity_provision(self, opp: Dict, inv: Dict) -> float:
        """流动性提供 - 高流动性优先"""
        vol = opp.get('volume_24h', 0)
        liq = opp.get('liquidity_score', 0.5)
        
        score = liq * 0.7 + min(1.0, vol / 5000000) * 0.3
        
        return score
    
    def _volatility_capture(self, opp: Dict, inv: Dict) -> float:
        """波动捕获 - 波动适中最好"""
        vol = opp.get('volatility', 0.05)
        
        # 波动太低没收益，波动太高风险大
        if 0.02 <= vol <= 0.06:
            return 0.90
        elif 0.01 <= vol <= 0.08:
            return 0.70
        elif 0.005 <= vol <= 0.10:
            return 0.50
        return 0.30
    
    def _fee_capture(self, opp: Dict, inv: Dict) -> float:
        """手续费捕获 - 低手续费优先"""
        fee = opp.get('maker_fee', 0.001)
        
        # 手续费越低越好
        if fee < 0.0005: return 0.95
        elif fee < 0.001: return 0.80
        elif fee < 0.002: return 0.60
        return 0.40

# ==================== 风控 ====================

class RiskController:
    """风控"""
    
    def __init__(self, config: FollowMasterConfig):
        self.config = config
        self.inventory = {'long': 0, 'short': 0, 'long_ratio': 0.5}
        self.daily_pnl = 0
        self.positions = {}
    
    def check(self, opp: Dict, size: float, mode: str) -> Dict:
        """风控检查"""
        params = self.config.modes[mode]
        
        # 价差检查
        if opp.get('spread', 0) < params['min_spread']:
            return {'pass': False, 'reason': f"价差{opp['spread']:.2%}<{params['min_spread']:.2%}"}
        
        # 仓位检查
        total_position = abs(self.inventory['long']) + abs(self.inventory['short'])
        if total_position + size > self.config.total_funds * params['max_position']:
            return {'pass': False, 'reason': '仓位超限'}
        
        # 库存风险检查
        long_ratio = self.inventory['long_ratio']
        if abs(long_ratio - 0.5) > params['inventory_risk']:
            return {'pass': False, 'reason': f'库存偏置过大{long_ratio:.1%}'}
        
        return {'pass': True}
    
    def update_inventory(self, side: str, size: float):
        """更新库存"""
        if side == 'long':
            self.inventory['long'] += size
        else:
            self.inventory['short'] += size
        
        # 更新比率
        total = abs(self.inventory['long']) + abs(self.inventory['short'])
        if total > 0:
            self.inventory['long_ratio'] = abs(self.inventory['long']) / total
    
    def rebalance_if_needed(self, threshold: float) -> bool:
        """是否需要再平衡"""
        long_ratio = self.inventory['long_ratio']
        
        if abs(long_ratio - 0.5) > threshold:
            return True
        return False

# ==================== 决策引擎 ====================

class DecisionEngine:
    """决策引擎"""
    
    def __init__(self, config: FollowMasterConfig):
        self.config = config
    
    def decide(self, opp: Dict, strategy: Dict, size: float, mode: str) -> Dict:
        """决策"""
        params = self.config.modes[mode]
        
        spread = opp.get('spread', 0)
        liquidity = opp.get('liquidity_score', 0)
        
        # 综合检查
        if spread < params['min_spread']:
            return {'action': 'WAIT', 'reason': f'价差不足'}
        
        if strategy['total'] < 0.4:
            return {'action': 'WAIT', 'reason': f'策略评分{strategy["total"]:.1%}<40%'}
        
        if liquidity < 0.4:
            return {'action': 'WAIT', 'reason': '流动性不足'}
        
        # 执行
        return {
            'action': 'MAKE_MARKET',
            'spread': spread,
            'size': size,
            'expected_fee': spread * size * 2,  # 买卖都有
            'strategy': strategy['best'],
            'rebalance': params['rebalance_threshold']
        }

# ==================== 资金管理 ====================

class FundManager:
    """资金管理"""
    
    def __init__(self, config: FollowMasterConfig):
        self.config = config
        self.available = config.total_funds * (1 - config.reserve_ratio)
        self.reserve = config.total_funds * config.reserve_ratio
    
    def allocate(self, size: float) -> bool:
        if size > self.available:
            return False
        self.available -= size
        return True
    
    def get_status(self) -> Dict:
        return {
            'total': self.config.total_funds,
            'available': self.available,
            'reserve': self.reserve,
            'used': self.config.total_funds - self.available - self.reserve
        }

# ==================== 主系统 ====================

class FollowMasterTool:
    """跟大哥 - 做市协作工具"""
    
    def __init__(self, mode: str = 'balanced'):
        self.config = FollowMasterConfig()
        self.mode = mode
        
        # 组件
        self.api = MarketMakingAPI()
        self.strategy = StrategyLibrary()
        self.risk = RiskController(self.config)
        self.decision = DecisionEngine(self.config)
        self.funds = FundManager(self.config)
        
        # 历史
        self.results = deque(maxlen=100)
    
    def set_mode(self, mode: str):
        if mode in self.config.modes:
            self.mode = mode
    
    def scan(self) -> List[Dict]:
        """扫描做市机会"""
        opportunities = self.api.fetch_opportunities()
        
        results = []
        
        for opp in opportunities:
            # 策略分析
            strat = self.strategy.analyze(opp, self.risk.inventory)
            
            # 参数
            params = self.config.modes[self.mode]
            size = self.config.total_funds * params['max_position'] / 3
            
            # 风控
            risk_check = self.risk.check(opp, size, self.mode)
            if not risk_check['pass']:
                continue
            
            # 决策
            decision = self.decision.decide(opp, strat, size, self.mode)
            
            # 保存
            result = {
                'opportunity': opp,
                'strategy': strat,
                'decision': decision,
                'timestamp': int(time.time())
            }
            
            self.results.append(result)
            
            if decision['action'] != 'WAIT':
                results.append(result)
                self.funds.allocate(size)
                self.risk.update_inventory('long', size / 2)
                self.risk.update_inventory('short', size / 2)
        
        return results
    
    def get_status(self) -> Dict:
        params = self.config.modes[self.mode]
        
        return {
            'mode': self.mode,
            'params': params,
            'api_status': self.api.get_status(),
            'funds': self.funds.get_status(),
            'inventory': self.risk.inventory,
            'results': {
                'total': len(self.results),
                'signals': sum(1 for r in self.results if r['decision']['action'] != 'WAIT')
            }
        }

# ==================== 测试 ====================

def test():
    print("\n" + "="*60)
    print("👑 跟大哥 - 做市协作工具测试")
    print("="*60)
    
    for mode in ['conservative', 'balanced', 'aggressive']:
        print(f"\n📊 模式: {mode}")
        
        tool = FollowMasterTool(mode=mode)
        
        # 扫描
        opps = tool.scan()
        
        # 状态
        status = tool.get_status()
        
        print(f"   信号: {len(opps)}/{status['results']['total']}")
        print(f"   资金: ${status['funds']['available']:.2f}")
        print(f"   库存: 长{status['inventory']['long_ratio']:.1%}")
        
        if opps:
            print(f"   Top机会:")
            for o in opps[:3]:
                opp = o['opportunity']
                d = o['decision']
                print(f"   - {opp['pair']}")
                print(f"     价差:{opp['spread']:.2%} 策略:{o['strategy']['best']}")
                print(f"     预期手续费:${d.get('expected_fee',0):.2f}")
    
    print("\n✅ 测试完成")

if __name__ == '__main__':
    test()
