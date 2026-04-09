#!/usr/bin/env python3
"""
北斗七鑫 - 薅羊毛 (新币空投) v1
空投追踪+领取+任务工具
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
class AirdropConfig:
    """薅羊毛配置"""
    # 资源分配
    resources_ratio: float = 0.03      # 算力3%
    api_priority: int = 4              # API优先级
    
    # 扫描设置
    scan_interval: int = 300          # 5分钟
    min_value: float = 10            # 最小价值$10
    
    # 资金配置 (用于交互/Gas等)
    total_funds: float = 1000          # 预留资金
    reserve_ratio: float = 0.50      # 备用金50%
    
    # 三种模式
    modes: Dict = field(default_factory=lambda: {
        'conservative': {
            'min_difficulty': 0.3,       # 难度系数
            'min_value': 50,           # 最小价值$50
            'networks': ['ethereum', 'arbitrum', 'optimism'],
            'auto_claim': False,
            'risk_level': 0.1,
        },
        'balanced': {
            'min_difficulty': 0.2,
            'min_value': 20,
            'networks': ['ethereum', 'arbitrum', 'optimism', 'polygon', 'avalanche'],
            'auto_claim': True,
            'risk_level': 0.3,
        },
        'aggressive': {
            'min_difficulty': 0.1,
            'min_value': 10,
            'networks': ['ethereum', 'arbitrum', 'optimism', 'polygon', 'avalanche', 'bsc', 'zksync', 'starknet'],
            'auto_claim': True,
            'risk_level': 0.5,
        }
    })

# ==================== API管理 ====================

class AirdropAPI:
    """空投API"""
    
    def __init__(self):
        self.apis = {
            'layerzero': {'name': 'LayerZero', 'url': 'https://api.layerzero.network', 'priority': 1},
            'zksync': {'name': 'zkSync', 'url': 'https://api.zksync.io', 'priority': 2},
            'starknet': {'name': 'Starknet', 'url': 'https://api.starknet.io', 'priority': 3},
            'defillama': {'name': 'DeFiLlama', 'url': 'https://api.llama.fi', 'priority': 4},
            'airdrop_hunter': {'name': 'AirdropHunter', 'url': 'https://airdrop-hunter.io', 'priority': 5},
        }
        
        self.primary = 'layerzero'
        self.errors = deque(maxlen=30)
    
    def fetch_opportunities(self) -> List[Dict]:
        """获取空投机会"""
        return self._generate_opportunities()
    
    def _generate_opportunities(self) -> List[Dict]:
        """生成空投机会"""
        airdrops = [
            {'name': 'LayerZero', 'network': 'Multi-chain', 'difficulty': 'easy', 
             'est_value': 100, 'status': 'active', 'tasks': 3},
            {'name': 'zkSync', 'network': 'zkSync', 'difficulty': 'medium', 
             'est_value': 80, 'status': 'active', 'tasks': 5},
            {'name': 'Starknet', 'network': 'Starknet', 'difficulty': 'hard', 
             'est_value': 150, 'status': 'active', 'tasks': 8},
            {'name': 'MetaMask', 'network': 'ETH', 'difficulty': 'easy', 
             'est_value': 20, 'status': 'claimable', 'tasks': 1},
            {'name': 'Rabby', 'network': 'Multi-chain', 'difficulty': 'easy', 
             'est_value': 15, 'status': 'active', 'tasks': 2},
            {'name': 'Layer2', 'network': 'Arbitrum', 'difficulty': 'medium', 
             'est_value': 60, 'status': 'active', 'tasks': 4},
            {'name': 'Scroll', 'network': 'Scroll', 'difficulty': 'medium', 
             'est_value': 45, 'status': 'active', 'tasks': 3},
            {'name': 'Linea', 'network': 'Linea', 'difficulty': 'easy', 
             'est_value': 35, 'status': 'active', 'tasks': 2},
            {'name': 'Mode', 'network': 'Optimism', 'difficulty': 'easy', 
             'est_value': 25, 'status': 'claimable', 'tasks': 1},
            {'name': 'Polygon zkEVM', 'network': 'Polygon', 'difficulty': 'medium', 
             'est_value': 40, 'status': 'active', 'tasks': 4},
        ]
        
        # 添加随机属性
        for a in airdrops:
            a['difficulty_score'] = self._difficulty_to_score(a['difficulty'])
            a['tvl'] = random.uniform(10, 500)  # 百万美元
            a['holders'] = random.randint(10000, 500000)
        
        return airdrops
    
    def _difficulty_to_score(self, difficulty: str) -> float:
        mapping = {'easy': 0.9, 'medium': 0.5, 'hard': 0.2}
        return mapping.get(difficulty, 0.5)
    
    def get_status(self) -> Dict:
        return {
            'primary': self.primary,
            'apis': {k: v['priority'] for k, v in self.apis.items()},
        }

# ==================== 策略库 ====================

class StrategyLibrary:
    """策略库 - 空投策略"""
    
    def __init__(self):
        self.strategies = {
            'value_max': {
                'name': '价值最大化',
                'weight': 0.30,
                'func': self._value_max
            },
            'efficiency': {
                'name': '效率优先',
                'weight': 0.25,
                'func': self._efficiency
            },
            'difficulty_ratio': {
                'name': '难度收益比',
                'weight': 0.25,
                'func': self._difficulty_ratio
            },
            'network_coverage': {
                'name': '网络覆盖',
                'weight': 0.10,
                'func': self._network_coverage
            },
            'time_to_claim': {
                'name': '领取时机',
                'weight': 0.10,
                'func': self._time_to_claim
            },
        }
    
    def analyze(self, airdrop: Dict, history: List[Dict] = None) -> Dict:
        """分析空投机会"""
        scores = {}
        
        for sid, s in self.strategies.items():
            score = s['func'](airdrop, history or [])
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
    
    def _value_max(self, a: Dict, h: List) -> float:
        """价值最大化 - 预期价值"""
        value = a.get('est_value', 0)
        
        if value > 100: return 0.95
        elif value > 50: return 0.75
        elif value > 30: return 0.55
        elif value > 10: return 0.35
        return 0.15
    
    def _efficiency(self, a: Dict, h: List) -> float:
        """效率优先 - 任务少价值高"""
        tasks = a.get('tasks', 10)
        value = a.get('est_value', 0)
        
        efficiency = value / max(tasks, 1)
        
        if efficiency > 30: return 0.90
        elif efficiency > 15: return 0.70
        elif efficiency > 5: return 0.50
        return 0.30
    
    def _difficulty_ratio(self, a: Dict, h: List) -> float:
        """难度收益比"""
        diff = a.get('difficulty_score', 0.5)
        value = a.get('est_value', 0)
        
        ratio = value * diff
        
        if ratio > 30: return 0.90
        elif ratio > 15: return 0.70
        elif ratio > 5: return 0.50
        return 0.30
    
    def _network_coverage(self, a: Dict, h: List) -> float:
        """网络覆盖 - 热门网络优先"""
        network = a.get('network', '').lower()
        
        popular = ['ethereum', 'arbitrum', 'optimism']
        
        if network in popular: return 0.90
        elif 'poly' in network: return 0.70
        elif 'bsc' in network: return 0.60
        elif 'zk' in network or 'stark' in network: return 0.80
        return 0.40
    
    def _time_to_claim(self, a: Dict, h: List) -> float:
        """领取时机 - 可领取优先"""
        status = a.get('status', 'active')
        
        if status == 'claimable': return 0.95
        elif status == 'ending': return 0.80
        elif status == 'active': return 0.60
        elif status == 'upcoming': return 0.40
        return 0.30

# ==================== 风控 ====================

class RiskController:
    """风控"""
    
    def __init__(self, config: AirdropConfig):
        self.config = config
        self.claimed = []
        self.pending = []
    
    def check(self, airdrop: Dict, mode: str) -> Dict:
        """风控检查"""
        params = self.config.modes[mode]
        
        # 检查是否已领取
        if airdrop['name'] in self.claimed:
            return {'pass': False, 'reason': '已领取'}
        
        # 检查难度
        diff_score = airdrop.get('difficulty_score', 0.5)
        if diff_score < params['min_difficulty']:
            return {'pass': False, 'reason': f'难度过高'}
        
        # 检查价值
        value = airdrop.get('est_value', 0)
        if value < params['min_value']:
            return {'pass': False, 'reason': f'价值${value}<${params["min_value"]}'}
        
        # 检查网络
        network = airdrop.get('network', '').lower()
        if network not in [n.lower() for n in params['networks']]:
            return {'pass': False, 'reason': f'网络不支持'}
        
        # 检查风险
        if airdrop.get('risk_level', 0) > params['risk_level']:
            return {'pass': False, 'reason': '风险过高'}
        
        return {'pass': True}
    
    def mark_claimed(self, name: str):
        """标记已领取"""
        if name not in self.claimed:
            self.claimed.append(name)
    
    def mark_pending(self, name: str):
        """标记待领取"""
        if name not in self.pending:
            self.pending.append(name)

# ==================== 决策引擎 ====================

class DecisionEngine:
    """决策引擎"""
    
    def __init__(self, config: AirdropConfig):
        self.config = config
    
    def decide(self, airdrop: Dict, strategy: Dict, mode: str) -> Dict:
        """决策"""
        params = self.config.modes[mode]
        
        value = airdrop.get('est_value', 0)
        status = airdrop.get('status', 'active')
        
        # 价值检查
        if value < params['min_value']:
            return {'action': 'SKIP', 'reason': f'价值${value}<${params["min_value"]}'}
        
        # 策略评分
        if strategy['total'] < 0.4:
            return {'action': 'SKIP', 'reason': f'策略评分{strategy["total"]:.1%}<40%'}
        
        # 可领取优先
        if status == 'claimable':
            action = 'CLAIM_NOW'
        elif status == 'active':
            action = 'TRACK'
        else:
            action = 'WAIT'
        
        return {
            'action': action,
            'value': value,
            'tasks': airdrop.get('tasks', 0),
            'difficulty': airdrop.get('difficulty', 'medium'),
            'strategy': strategy['best'],
            'estimated_time': airdrop.get('tasks', 0) * 10  # 10分钟/任务
        }

# ==================== 资金管理 ====================

class FundManager:
    """资金管理"""
    
    def __init__(self, config: AirdropConfig):
        self.config = config
        self.available = config.total_funds * (1 - config.reserve_ratio)
        self.reserve = config.total_funds * config.reserve_ratio
    
    def get_status(self) -> Dict:
        return {
            'total': self.config.total_funds,
            'available': self.available,
            'reserve': self.reserve,
        }

# ==================== 主系统 ====================

class AirdropTool:
    """薅羊毛工具"""
    
    def __init__(self, mode: str = 'balanced'):
        self.config = AirdropConfig()
        self.mode = mode
        
        # 组件
        self.api = AirdropAPI()
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
        """扫描空投"""
        opportunities = self.api.fetch_opportunities()
        
        results = []
        
        for airdrop in opportunities:
            # 策略分析
            hist = self.history.get(airdrop['name'], [])
            strat = self.strategy.analyze(airdrop, hist)
            
            # 风控
            risk_check = self.risk.check(airdrop, self.mode)
            if not risk_check['pass']:
                continue
            
            # 决策
            decision = self.decision.decide(airdrop, strat, self.mode)
            
            # 保存
            result = {
                'airdrop': airdrop,
                'strategy': strat,
                'decision': decision,
                'timestamp': int(time.time())
            }
            
            self.results.append(result)
            self.history[airdrop['name']] = hist + [airdrop]
            
            if decision['action'] in ['CLAIM_NOW', 'TRACK']:
                results.append(result)
        
        return results
    
    def get_status(self) -> Dict:
        params = self.config.modes[self.mode]
        
        return {
            'mode': self.mode,
            'params': params,
            'api_status': self.api.get_status(),
            'funds': self.funds.get_status(),
            'claimed': len(self.risk.claimed),
            'pending': len(self.risk.pending),
            'results': {
                'total': len(self.results),
                'signals': sum(1 for r in self.results if r['decision']['action'] != 'SKIP')
            }
        }

# ==================== 测试 ====================

def test():
    print("\n" + "="*60)
    print("💰 薅羊毛 - 新币空投工具测试")
    print("="*60)
    
    for mode in ['conservative', 'balanced', 'aggressive']:
        print(f"\n📊 模式: {mode}")
        
        tool = AirdropTool(mode=mode)
        
        # 扫描
        opps = tool.scan()
        
        # 状态
        status = tool.get_status()
        
        print(f"   信号: {len(opps)}/{status['results']['total']}")
        print(f"   已领取: {status['claimed']} | 待领取: {status['pending']}")
        
        if opps:
            print(f"   Top机会:")
            for o in opps[:3]:
                a = o['airdrop']
                d = o['decision']
                print(f"   - {a['name']}")
                print(f"     价值: ${a['est_value']} | 任务: {a['tasks']}个 | 难度: {a['difficulty']}")
                print(f"     行动: {d['action']} | 策略: {o['strategy']['best']}")
    
    print("\n✅ 测试完成")

if __name__ == '__main__':
    test()
