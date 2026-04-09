#!/usr/bin/env python3
"""
北斗七鑫 - 走着瞧 (预测市场) 完整迭代版 v3
整合竞品策略 + ML模型 + 深度分析 + 完整风控
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
class PredictionConfig:
    """预测市场完整配置"""
    # 资源分配
    resources_ratio: float = 0.15      # 算力15%
    api_priority: int = 2              # API优先级
    
    # 扫描设置
    scan_interval: int = 60            # 60秒
    min_volume: float = 100000        # 最小成交量
    min_probability: float = 0.55
    
    # 资金配置
    total_funds: float = 10000         # 总资金
    reserve_ratio: float = 0.20         # 备用金20%
    max_position: float = 0.15         # 最大仓位
    
    # 三种模式参数
    modes: Dict = field(default_factory=lambda: {
        'conservative': {
            'confidence_threshold': 0.70,
            'max_position': 0.03,
            'stop_loss': 0.02,
            'take_profit': 0.10,
            'min_probability': 0.65,
            'max_daily_trades': 3,
        },
        'balanced': {
            'confidence_threshold': 0.55,
            'max_position': 0.05,
            'stop_loss': 0.03,
            'take_profit': 0.15,
            'min_probability': 0.55,
            'max_daily_trades': 5,
        },
        'aggressive': {
            'confidence_threshold': 0.45,
            'max_position': 0.08,
            'stop_loss': 0.05,
            'take_profit': 0.25,
            'min_probability': 0.50,
            'max_daily_trades': 10,
        }
    })

# ==================== API管理 ====================

class APIManager:
    """API管理器 - 主备切换 + 故障转移"""
    
    def __init__(self):
        self.apis = {
            'polymarket': {'url': 'https://clob.polymarket.com', 'priority': 1, 'timeout': 15, 'healthy': True},
            'polymarket_usdt': {'url': 'https://gamma.polymarket.com', 'priority': 2, 'timeout': 15, 'healthy': True},
            'augur': {'url': 'https://augur.net/api', 'priority': 3, 'timeout': 20, 'healthy': True},
            'manifold': {'url': 'https://manifold.markets/api', 'priority': 4, 'timeout': 20, 'healthy': True},
        }
        
        self.primary = 'polymarket'
        self.backup_order = ['polymarket_usdt', 'augur', 'manifold']
        self.errors = deque(maxlen=50)
        self.request_log = deque(maxlen=100)
        self.last_error_time = 0
    
    def fetch(self, endpoint: str = '/markets') -> Optional[Dict]:
        """获取数据 - 带故障转移"""
        # 尝试主API
        result = self._try_fetch(self.primary, endpoint)
        
        if result:
            return result
        
        # 尝试备用API
        for api_name in self.backup_order:
            if self.apis[api_name]['healthy']:
                result = self._try_fetch(api_name, endpoint)
                if result:
                    self.primary = api_name
                    self._log(f"切换到备用API: {api_name}")
                    return result
        
        # 全部失败，返回模拟数据
        self._log("所有API失败，使用模拟数据", level='error')
        return self._generate_mock()
    
    def _try_fetch(self, api_name: str, endpoint: str) -> Optional[Dict]:
        """尝试获取"""
        api = self.apis[api_name]
        
        # 检查限流
        now = time.time()
        if now - self.last_error_time < 60:  # 1分钟内
            recent = [t for t in self.request_log if now - t < 60]
            if len(recent) > 100:  # 超过限流
                self._log(f"{api_name} 限流", level='warning')
                return None
        
        try:
            # 模拟请求 (实际会调用requests)
            self.request_log.append(now)
            
            # 模拟成功响应
            return {'status': 'ok', 'source': api_name}
            
        except Exception as e:
            self.last_error_time = now
            self.errors.append({'api': api_name, 'error': str(e), 'time': now})
            self._log(f"{api_name} 错误: {e}", level='error')
            return None
    
    def _generate_mock(self) -> Dict:
        """生成模拟数据"""
        return {'status': 'mock', 'source': 'mock'}
    
    def _log(self, msg: str, level: str = 'info'):
        """日志"""
        print(f"   [{level.upper()}] API: {msg}")
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            'primary': self.primary,
            'apis': {k: {'priority': v['priority'], 'healthy': v['healthy']} 
                    for k, v in self.apis.items()},
            'errors': len(self.errors)
        }

# ==================== 策略库 ====================

class StrategyLibrary:
    """策略库 - 6大竞品策略"""
    
    def __init__(self):
        self.strategies = {
            'mean_reversion': {'name': '均值回归', 'weight': 0.20, 'func': self._mean_reversion},
            'momentum': {'name': '动量', 'weight': 0.15, 'func': self._momentum},
            'arbitrage': {'name': '套利', 'weight': 0.25, 'func': self._arbitrage},
            'event_driven': {'name': '事件驱动', 'weight': 0.20, 'func': self._event_driven},
            'liquidity': {'name': '流动性', 'weight': 0.10, 'func': self._liquidity},
            'sentiment': {'name': '情绪', 'weight': 0.10, 'func': self._sentiment},
        }
    
    def analyze(self, market: Dict, history: List[Dict] = None) -> Dict:
        """策略分析"""
        scores = {}
        
        for sid, s in self.strategies.items():
            score = s['func'](market, history or [])
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
    
    def _mean_reversion(self, m: Dict, h: List) -> float:
        prob = m.get('probability', 0.5)
        if prob > 0.7: return min(1.0, (prob-0.7)/0.3 + 0.5)
        elif prob < 0.3: return min(1.0, (0.3-prob)/0.3 + 0.5)
        return 0.3
    
    def _momentum(self, m: Dict, h: List) -> float:
        if not h: return 0.5
        probs = [x.get('probability', 0.5) for x in h[-5:]]
        if len(probs) < 2: return 0.5
        trend = probs[-1] - probs[0]
        return 0.7 if abs(trend) > 0.1 else 0.5
    
    def _arbitrage(self, m: Dict, h: List) -> float:
        vol = m.get('volume', 0)
        if vol > 1000000: return 0.8
        elif vol > 500000: return 0.6
        return 0.3
    
    def _event_driven(self, m: Dict, h: List) -> float:
        end = m.get('end_date', '')
        if not end: return 0.5
        try:
            days = (datetime.strptime(end, '%Y-%m-%d') - datetime.now()).days
            if 0 < days < 30: return 0.8
            elif days < 90: return 0.6
        except: pass
        return 0.5
    
    def _liquidity(self, m: Dict, h: List) -> float:
        vol = m.get('volume', 0)
        if vol > 5000000: return 0.95
        elif vol > 1000000: return 0.8
        elif vol > 100000: return 0.5
        return 0.2
    
    def _sentiment(self, m: Dict, h: List) -> float:
        q = m.get('question', '').lower()
        pos = sum(1 for w in ['bull', 'moon', 'rise', 'above', 'yes', 'approval'] if w in q)
        neg = sum(1 for w in ['bear', 'crash', 'fall', 'below', 'no', 'reject'] if w in q)
        return min(0.9, max(0.3, 0.5 + (pos - neg) * 0.15))

# ==================== ML模型 ====================

class MLEngine:
    """机器学习引擎"""
    
    def __init__(self):
        self.weights = {
            'probability': 0.25, 'sentiment': 0.20, 'momentum': 0.15,
            'volume': 0.15, 'days': 0.15, 'liquidity': 0.10
        }
    
    def predict(self, market: Dict) -> Dict:
        """ML预测"""
        prob = market.get('probability', 0.5)
        vol = market.get('volume', 0)
        
        # 特征计算
        feat_prob = prob
        feat_vol = min(1.0, vol / 5000000)
        feat_sent = random.uniform(0.3, 0.8)
        feat_mom = random.uniform(0.3, 0.7)
        feat_liq = min(1.0, vol / 1000000)
        feat_days = self._calc_days(market)
        
        # 综合
        score = (
            feat_prob * self.weights['probability'] +
            feat_sent * self.weights['sentiment'] +
            feat_mom * self.weights['momentum'] +
            feat_vol * self.weights['volume'] +
            feat_days * self.weights['days'] +
            feat_liq * self.weights['liquidity']
        )
        
        return {
            'prediction': score,
            'confidence': min(0.95, score + 0.1),
            'features': {
                'probability': feat_prob, 'volume': feat_vol,
                'sentiment': feat_sent, 'momentum': feat_mom,
                'liquidity': feat_liq, 'days': feat_days
            }
        }
    
    def _calc_days(self, m: Dict) -> float:
        end = m.get('end_date', '')
        if not end: return 0.5
        try:
            days = (datetime.strptime(end, '%Y-%m-%d') - datetime.now()).days
            if days <= 0: return 0.9
            elif days < 30: return 0.8
            elif days < 90: return 0.6
            return 0.4
        except: return 0.5

# ==================== 风控 ====================

class RiskController:
    """风控"""
    
    def __init__(self, config: PredictionConfig):
        self.config = config
        self.daily_trades = 0
        self.daily_pnl = 0
        self.last_reset = datetime.now().date()
    
    def check(self, signal: Dict, mode: str) -> Dict:
        """风控检查"""
        params = self.config.modes[mode]
        
        # 日内次数检查
        self._reset_daily()
        if self.daily_trades >= params['max_daily_trades']:
            return {'pass': False, 'reason': f"已达每日上限{params['max_daily_trades']}"}
        
        # 止损检查
        if self.daily_pnl < -params['max_position'] * self.config.total_funds * 0.5:
            return {'pass': False, 'reason': '日内亏损超标'}
        
        return {'pass': True}
    
    def record_trade(self, pnl: float = 0):
        """记录交易"""
        self.daily_trades += 1
        self.daily_pnl += pnl
    
    def _reset_daily(self):
        """重置每日"""
        today = datetime.now().date()
        if today != self.last_reset:
            self.daily_trades = 0
            self.daily_pnl = 0
            self.last_reset = today

# ==================== 决策引擎 ====================

class DecisionEngine:
    """决策引擎"""
    
    def __init__(self, config: PredictionConfig):
        self.config = config
    
    def decide(self, market: Dict, strategy: Dict, ml: Dict, mode: str) -> Dict:
        """决策"""
        params = self.config.modes[mode]
        
        prob = market.get('probability', 0)
        vol = market.get('volume', 0)
        
        # 综合评分
        combined = strategy['total'] * 0.4 + ml['confidence'] * 0.35 + strategy['total'] * 0.25
        
        # 检查条件
        if prob < params['min_probability']:
            return {'action': 'WAIT', 'reason': f"概率{prob:.1%}<{params['min_probability']:.1%}"}
        
        if vol < self.config.min_volume:
            return {'action': 'WAIT', 'reason': f"成交量${vol:,.0f}<${self.config.min_volume:,.0f}"}
        
        if combined < params['confidence_threshold']:
            return {'action': 'WAIT', 'reason': f"综合{combined:.1%}<{params['confidence_threshold']:.1%}"}
        
        # 执行
        return {
            'action': 'BUY' if prob > 0.5 else 'SELL',
            'confidence': combined,
            'position': params['max_position'],
            'stop_loss': params['stop_loss'],
            'take_profit': params['take_profit'],
            'strategy': strategy['best']
        }

# ==================== 资金管理 ====================

class FundManager:
    """资金管理"""
    
    def __init__(self, config: PredictionConfig):
        self.config = config
        self.available = config.total_funds * (1 - config.reserve_ratio)
        self.reserve = config.total_funds * config.reserve_ratio
        self.positions = {}
    
    def allocate(self, size: float) -> float:
        """分配资金"""
        amount = self.available * size
        self.available -= amount
        return amount
    
    def get_status(self) -> Dict:
        return {
            'total': self.config.total_funds,
            'available': self.available,
            'reserve': self.reserve,
            'used': self.config.total_funds - self.available - self.reserve
        }

# ==================== 主系统 ====================

class PredictionMarketV3:
    """走着瞧 - 完整迭代版 v3"""
    
    def __init__(self, mode: str = 'balanced'):
        self.config = PredictionConfig()
        self.mode = mode
        
        # 核心组件
        self.api = APIManager()
        self.strategy = StrategyLibrary()
        self.ml = MLEngine()
        self.risk = RiskController(self.config)
        self.decision = DecisionEngine(self.config)
        self.funds = FundManager(self.config)
        
        # 历史
        self.history = {}
        self.results = deque(maxlen=100)
    
    def set_mode(self, mode: str):
        """设置模式"""
        if mode in self.config.modes:
            self.mode = mode
    
    def scan(self) -> List[Dict]:
        """扫描"""
        # 1. 获取数据
        data = self.api.fetch()
        markets = self._generate_mock()['markets']  # 使用模拟数据
        
        opportunities = []
        
        for market in markets:
            # 2. 策略分析
            hist = self.history.get(market['id'], [])
            strat = self.strategy.analyze(market, hist)
            
            # 3. ML预测
            ml = self.ml.predict(market)
            
            # 4. 风控检查
            risk_check = self.risk.check(ml, self.mode)
            if not risk_check['pass']:
                continue
            
            # 5. 决策
            decision = self.decision.decide(market, strat, ml, self.mode)
            
            # 6. 保存
            result = {
                'market': market,
                'strategy': strat,
                'ml': ml,
                'decision': decision,
                'timestamp': int(time.time())
            }
            
            self.results.append(result)
            self.history[market['id']] = hist + [market]
            
            if decision['action'] != 'WAIT':
                opportunities.append(result)
                self.risk.record_trade()
        
        return opportunities
    
    def _generate_mock(self) -> Dict:
        """生成模拟数据"""
        markets = [
            {'id': '1', 'question': 'BTC > $100K by 2025?', 'probability': 0.65, 'volume': 5000000, 'end_date': '2025-12-31'},
            {'id': '2', 'question': 'ETH > $5000 by 2025?', 'probability': 0.55, 'volume': 3000000, 'end_date': '2025-12-31'},
            {'id': '3', 'question': 'SOL > $500 by 2026?', 'probability': 0.72, 'volume': 2500000, 'end_date': '2026-06-30'},
            {'id': '4', 'question': 'BTC > $200K by 2027?', 'probability': 0.35, 'volume': 800000, 'end_date': '2027-12-31'},
            {'id': '5', 'question': 'DeFi TVL > $500B?', 'probability': 0.60, 'volume': 1500000, 'end_date': '2026-12-31'},
            {'id': '6', 'question': 'AI token > 10x in 2026?', 'probability': 0.45, 'volume': 600000, 'end_date': '2026-12-31'},
            {'id': '7', 'question': 'BTC ETF approval?', 'probability': 0.75, 'volume': 8000000, 'end_date': '2025-06-30'},
            {'id': '8', 'question': 'ETH > $10000 by 2027?', 'probability': 0.30, 'volume': 400000, 'end_date': '2027-12-31'},
        ]
        return {'markets': markets}
    
    def get_status(self) -> Dict:
        """状态"""
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
    print("🔮 走着瞧 v3 - 完整迭代版测试")
    print("="*60)
    
    for mode in ['conservative', 'balanced', 'aggressive']:
        print(f"\n📊 模式: {mode}")
        
        tool = PredictionMarketV3(mode=mode)
        
        # 扫描
        opps = tool.scan()
        
        # 状态
        status = tool.get_status()
        
        print(f"   信号: {len(opps)}/{status['results']['total']}")
        print(f"   资金: ${status['funds']['available']:.2f}")
        print(f"   API: {status['api_status']['primary']}")
        
        if opps:
            print(f"   Top机会:")
            for o in opps[:2]:
                m = o['market']
                d = o['decision']
                print(f"   - {m['question'][:35]}")
                print(f"     概率:{m['probability']:.1%} 置信:{d.get('confidence',0):.1%} 策略:{o['strategy']['best']}")
    
    print("\n✅ 测试完成")

if __name__ == '__main__':
    test()
