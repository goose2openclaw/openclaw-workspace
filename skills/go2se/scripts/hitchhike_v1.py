#!/usr/bin/env python3
"""
北斗七鑫 - 搭便车 (跟单分成) v1
复制交易/跟单分成工具
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
class HitchhikeConfig:
    """搭便车配置"""
    # 资源分配
    resources_ratio: float = 0.10      # 算力10%
    api_priority: int = 3              # API优先级
    
    # 扫描设置
    scan_interval: int = 120           # 120秒
    min_volume: float = 10000         # 最小跟单金额
    min_roi: float = 0.10            # 最小ROI
    
    # 资金配置
    total_funds: float = 10000
    reserve_ratio: float = 0.15        # 备用金15%
    max_position: float = 0.20         # 最大跟单仓位
    
    # 三种模式
    modes: Dict = field(default_factory=lambda: {
        'conservative': {
            'min_followers': 100,
            'min_roi': 0.05,
            'max_allocation': 0.10,
            'copier_ratio': 0.10,     # 跟单比例
            'commission': 0.20,       # 分成比例
            'max_traders': 3,
        },
        'balanced': {
            'min_followers': 50,
            'min_roi': 0.08,
            'max_allocation': 0.15,
            'copier_ratio': 0.15,
            'commission': 0.15,
            'max_traders': 5,
        },
        'aggressive': {
            'min_followers': 20,
            'min_roi': 0.05,
            'max_allocation': 0.20,
            'copier_ratio': 0.20,
            'commission': 0.10,
            'max_traders': 10,
        }
    })

# ==================== API管理 ====================

class CopyTradingAPI:
    """跟单交易API"""
    
    def __init__(self):
        self.apis = {
            'binance_ct': {'name': 'Binance跟单', 'url': 'https://api.binance.com', 'priority': 1, 'timeout': 10},
            'bybit_ct': {'name': 'Bybit跟单', 'url': 'https://api.bybit.com', 'priority': 2, 'timeout': 10},
            'okx_ct': {'name': 'OKX跟单', 'url': 'https://www.okx.com', 'priority': 3, 'timeout': 15},
            'bitget_ct': {'name': 'Bitget跟单', 'url': 'https://api.bitget.com', 'priority': 4, 'timeout': 15},
        }
        
        self.primary = 'binance_ct'
        self.errors = deque(maxlen=30)
    
    def fetch_traders(self) -> List[Dict]:
        """获取交易员列表"""
        # 模拟获取
        return self._generate_mock_traders()
    
    def _generate_mock_traders(self) -> List[Dict]:
        """生成模拟交易员"""
        traders = []
        names = [
            'CryptoWhale', 'AlphaTrader', 'QuantMaster', 'SniperPro',
            'MomentumKing', 'SwingTrader', 'TrendFollower', 'ScalpMaster',
            'BullRunner', 'BearHunter', 'VolatilityKing', ' arbitrageur'
        ]
        
        for i, name in enumerate(names):
            traders.append({
                'id': f'trader_{i+1}',
                'name': name,
                'roi_30d': random.uniform(0.05, 0.50),
                'win_rate': random.uniform(0.40, 0.80),
                'followers': random.randint(10, 5000),
                'aum': random.uniform(10000, 5000000),  # 管理资产
                'daily_trades': random.randint(1, 50),
                'avg_trade_size': random.uniform(100, 50000),
                'risk_score': random.uniform(0.2, 0.9),
                'platform': random.choice(['binance', 'bybit', 'okx']),
                'last_trade_time': int(time.time()) - random.randint(0, 3600),
            })
        
        return traders
    
    def get_status(self) -> Dict:
        return {
            'primary': self.primary,
            'apis': {k: v['priority'] for k, v in self.apis.items()},
            'errors': len(self.errors)
        }

# ==================== 策略库 ====================

class StrategyLibrary:
    """策略库 - 竞品策略"""
    
    def __init__(self):
        self.strategies = {
            'top_performer': {
                'name': '顶尖表现',
                'weight': 0.25,
                'func': self._top_performer
            },
            'consistency': {
                'name': '稳定性',
                'weight': 0.20,
                'func': self._consistency
            },
            'risk_adjusted': {
                'name': '风险调整',
                'weight': 0.25,
                'func': self._risk_adjusted
            },
            'momentum': {
                'name': '动量',
                'weight': 0.15,
                'func': self._momentum
            },
            'diversification': {
                'name': '分散化',
                'weight': 0.15,
                'func': self._diversification
            },
        }
    
    def analyze(self, trader: Dict, history: List[Dict] = None) -> Dict:
        """分析交易员"""
        scores = {}
        
        for sid, s in self.strategies.items():
            score = s['func'](trader, history or [])
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
    
    def _top_performer(self, t: Dict, h: List) -> float:
        """顶尖表现策略 - ROI最高"""
        roi = t.get('roi_30d', 0)
        
        if roi > 0.40: return 0.95
        elif roi > 0.30: return 0.80
        elif roi > 0.20: return 0.65
        elif roi > 0.10: return 0.50
        return 0.30
    
    def _consistency(self, t: Dict, h: List) -> float:
        """稳定性策略 - 胜率稳定"""
        win = t.get('win_rate', 0)
        
        if win > 0.70: return 0.90
        elif win > 0.60: return 0.75
        elif win > 0.50: return 0.60
        return 0.40
    
    def _risk_adjusted(self, t: Dict, h: List) -> float:
        """风险调整策略 - Sharpe-like"""
        roi = t.get('roi_30d', 0)
        risk = t.get('risk_score', 0.5)
        
        # 低风险高回报最好
        adjusted = roi / (risk + 0.1)
        
        if adjusted > 0.5: return 0.90
        elif adjusted > 0.3: return 0.70
        elif adjusted > 0.2: return 0.50
        return 0.30
    
    def _momentum(self, t: Dict, h: List) -> float:
        """动量策略 - 最近表现好"""
        last_time = t.get('last_trade_time', 0)
        now = time.time()
        
        # 最近有交易
        if now - last_time < 3600:  # 1小时内
            return 0.80
        elif now - last_time < 7200:  # 2小时内
            return 0.60
        elif now - last_time < 14400:  # 4小时内
            return 0.40
        return 0.20
    
    def _diversification(self, t: Dict, h: List) -> float:
        """分散化策略 - 多样性"""
        trades = t.get('daily_trades', 0)
        
        # 中等交易频率最好
        if 5 <= trades <= 20: return 0.85
        elif 1 <= trades <= 50: return 0.65
        return 0.40

# ==================== 风控 ====================

class RiskController:
    """风控"""
    
    def __init__(self, config: HitchhikeConfig):
        self.config = config
        self.daily_pnl = 0
        self.positions = {}
        self.last_reset = datetime.now().date()
    
    def check(self, trader: Dict, allocation: float, mode: str) -> Dict:
        """风控检查"""
        params = self.config.modes[mode]
        
        # 重置
        self._reset_daily()
        
        # 检查跟单人数
        if len(self.positions) >= params['max_traders']:
            return {'pass': False, 'reason': f"已达最大跟单数{params['max_traders']}"}
        
        # 检查仓位比例 (allocation / total_funds)
        allocation_ratio = allocation / self.config.total_funds
        if allocation_ratio > params['max_allocation']:
            return {'pass': False, 'reason': f"仓位比例{allocation_ratio:.1%}超过限制{params['max_allocation']:.1%}"}
        
        # 检查交易员风险
        if trader.get('risk_score', 0) > 0.9:
            return {'pass': False, 'reason': '交易员风险过高'}
        
        return {'pass': True}
    
    def record(self, trader_id: str, pnl: float = 0):
        """记录"""
        if trader_id not in self.positions:
            self.positions[trader_id] = 0
        self.positions[trader_id] += pnl
        self.daily_pnl += pnl
    
    def _reset_daily(self):
        today = datetime.now().date()
        if today != self.last_reset:
            self.daily_pnl = 0
            self.last_reset = today

# ==================== 决策引擎 ====================

class DecisionEngine:
    """决策引擎"""
    
    def __init__(self, config: HitchhikeConfig):
        self.config = config
    
    def decide(self, trader: Dict, strategy: Dict, allocation: float, mode: str) -> Dict:
        """决策"""
        params = self.config.modes[mode]
        
        roi = trader.get('roi_30d', 0)
        followers = trader.get('followers', 0)
        win_rate = trader.get('win_rate', 0)
        
        # 检查ROI
        if roi < params['min_roi']:
            return {'action': 'WAIT', 'reason': f"ROI {roi:.1%} < {params['min_roi']:.1%}"}
        
        # 检查粉丝
        if followers < params['min_followers']:
            return {'action': 'WAIT', 'reason': f"粉丝{followers} < {params['min_followers']}"}
        
        # 综合评分
        if strategy['total'] < 0.5:
            return {'action': 'WAIT', 'reason': f"策略评分{strategy['total']:.1%} < 50%"}
        
        # 执行
        return {
            'action': 'FOLLOW',
            'allocation': allocation,
            'copier_ratio': params['copier_ratio'],
            'commission': params['commission'],
            'strategy': strategy['best'],
            'expected_roi': roi * params['copier_ratio'],
        }

# ==================== 资金管理 ====================

class FundManager:
    """资金管理"""
    
    def __init__(self, config: HitchhikeConfig):
        self.config = config
        self.available = config.total_funds * (1 - config.reserve_ratio)
        self.reserve = config.total_funds * config.reserve_ratio
        self.allocations = {}
    
    def allocate(self, amount: float) -> bool:
        """分配资金"""
        if amount > self.available:
            return False
        self.available -= amount
        return True
    
    def get_status(self) -> Dict:
        return {
            'total': self.config.total_funds,
            'available': self.available,
            'reserve': self.reserve,
            'allocated': self.config.total_funds - self.available - self.reserve
        }

# ==================== 主系统 ====================

class HitchhikeTool:
    """搭便车工具"""
    
    def __init__(self, mode: str = 'balanced'):
        self.config = HitchhikeConfig()
        self.mode = mode
        
        # 组件
        self.api = CopyTradingAPI()
        self.strategy = StrategyLibrary()
        self.risk = RiskController(self.config)
        self.decision = DecisionEngine(self.config)
        self.funds = FundManager(self.config)
        
        # 历史
        self.history = {}
        self.results = deque(maxlen=100)
    
    def set_mode(self, mode: str):
        if mode in self.config.modes:
            self.mode = mode
    
    def scan(self) -> List[Dict]:
        """扫描交易员"""
        # 获取交易员
        traders = self.api.fetch_traders()
        
        opportunities = []
        
        for trader in traders:
            # 策略分析
            hist = self.history.get(trader['id'], [])
            strat = self.strategy.analyze(trader, hist)
            
            # 参数
            params = self.config.modes[self.mode]
            allocation = self.config.total_funds * params['max_allocation'] / params['max_traders']
            
            # 风控
            risk_check = self.risk.check(trader, allocation, self.mode)
            if not risk_check['pass']:
                continue
            
            # 决策
            decision = self.decision.decide(trader, strat, allocation, self.mode)
            
            # 保存
            result = {
                'trader': trader,
                'strategy': strat,
                'decision': decision,
                'timestamp': int(time.time())
            }
            
            self.results.append(result)
            self.history[trader['id']] = hist + [trader]
            
            if decision['action'] != 'WAIT':
                opportunities.append(result)
                self.funds.allocate(allocation)
                self.risk.record(trader['id'])
        
        return opportunities
    
    def get_status(self) -> Dict:
        params = self.config.modes[self.mode]
        
        return {
            'mode': self.mode,
            'params': params,
            'api_status': self.api.get_status(),
            'funds': self.funds.get_status(),
            'results': {
                'total': len(self.results),
                'signals': sum(1 for r in self.results if r['decision']['action'] != 'WAIT')
            }
        }

# ==================== 测试 ====================

def test():
    print("\n" + "="*60)
    print("🍀 搭便车 - 跟单分成工具测试")
    print("="*60)
    
    for mode in ['conservative', 'balanced', 'aggressive']:
        print(f"\n📊 模式: {mode}")
        
        tool = HitchhikeTool(mode=mode)
        
        # 扫描
        opps = tool.scan()
        
        # 状态
        status = tool.get_status()
        
        print(f"   信号: {len(opps)}/{status['results']['total']}")
        print(f"   资金: ${status['funds']['available']:.2f}")
        
        if opps:
            print(f"   Top交易员:")
            for o in opps[:3]:
                t = o['trader']
                d = o['decision']
                print(f"   - {t['name']}")
                print(f"     ROI: {t['roi_30d']:.1%} | 胜率: {t['win_rate']:.1%}")
                print(f"     策略: {o['strategy']['best']} | 跟单: {d.get('allocation',0):.0f}")
    
    print("\n✅ 测试完成")

if __name__ == '__main__':
    test()
