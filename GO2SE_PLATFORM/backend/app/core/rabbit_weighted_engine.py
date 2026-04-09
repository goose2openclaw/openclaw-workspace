#!/usr/bin/env python3
"""
🐰🐹 打兔子/打地鼠 加权引擎
=============================
双策略平行 + 权重组合
专家模式可调整权重
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

# 导入各策略 (假设在同一目录)
try:
    from rabbit_strategy import RabbitStrategy, get_rabbit_strategy
    from rabbit_v2_strategy import RabbitV2Strategy, get_rabbit_v2_strategy
    from mole_strategy import MoleStrategy, get_mole_strategy
    from mole_v2_strategy import MoleV2Strategy, get_mole_v2_strategy
except ImportError:
    # 尝试添加路径
    import sys, os
    _path = os.path.dirname(os.path.abspath(__file__))
    if _path not in sys.path:
        sys.path.insert(0, _path)
    from rabbit_strategy import RabbitStrategy, get_rabbit_strategy
    from rabbit_v2_strategy import RabbitV2Strategy, get_rabbit_v2_strategy
    from mole_strategy import MoleStrategy, get_mole_strategy
    from mole_v2_strategy import MoleV2Strategy, get_mole_v2_strategy


@dataclass
class WeightedSignal:
    """加权信号"""
    symbol: str
    action: str
    v1_signal: Dict = field(default_factory=dict)
    v2_signal: Dict = field(default_factory=dict)
    v1_confidence: float = 0
    v2_confidence: float = 0
    weighted_confidence: float = 0
    final_action: str = 'hold'
    reason: str = ''
    timestamp: str = ''
    
    def to_dict(self) -> Dict:
        return {
            'symbol': self.symbol,
            'action': self.final_action,
            'v1_signal': self.v1_signal,
            'v2_signal': self.v2_signal,
            'v1_confidence': self.v1_confidence,
            'v2_confidence': self.v2_confidence,
            'weighted_confidence': self.weighted_confidence,
            'reason': self.reason,
            'timestamp': self.timestamp
        }


class RabbitWeightedEngine:
    """
    🐰 打兔子加权引擎
    
    V1: 趋势跟踪 (MA + RSI + 成交量)
    V2: 突破型 (支撑阻力 + 成交量突破)
    """
    
    def __init__(self, v1_weight: float = 0.5, expert_mode: bool = False):
        self.name = "🐰 打兔子加权引擎"
        
        self.v1 = get_rabbit_strategy()
        self.v2 = get_rabbit_v2_strategy()
        
        self.v1_weight = max(0, min(1, v1_weight))
        self.v2_weight = 1 - self.v1_weight
        
        self.expert_mode = expert_mode
        if not expert_mode:
            self.v1_weight = max(0.3, min(0.7, self.v1_weight))
            self.v2_weight = 1 - self.v1_weight
        
        self.signals = {}
    
    def set_weights(self, v1_weight: float, expert_mode: bool = None):
        """调整权重"""
        if expert_mode is not None:
            self.expert_mode = expert_mode
        
        self.v1_weight = max(0, min(1, v1_weight))
        
        if not self.expert_mode:
            self.v1_weight = max(0.3, min(0.7, self.v1_weight))
        
        self.v2_weight = 1 - self.v1_weight
    
    def generate_signal(self, symbol: str, market_data: Dict) -> WeightedSignal:
        """生成加权信号"""
        v1_raw = self.v1.generate_signal(symbol, market_data)
        v1_conf = v1_raw.get('confidence', 0)
        
        v2_raw = self.v2.generate_signal(symbol, market_data)
        v2_conf = v2_raw.get('confidence', 0)
        
        weighted_conf = v1_conf * self.v1_weight + v2_conf * self.v2_weight
        
        v1_action = v1_raw.get('action', 'hold')
        v2_action = v2_raw.get('action', 'hold')
        
        final_action = 'hold'
        reason = ''
        
        # 双重买入
        if v1_action == 'buy' and v2_action == 'buy':
            final_action = 'buy'
            reason = f"双重买入 V1({v1_conf:.0%})×{self.v1_weight:.0%}+V2({v2_conf:.0%})×{self.v2_weight:.0%}"
        elif v1_action == 'buy' and v2_action == 'hold':
            if v1_conf >= 0.7:
                final_action = 'buy'
                reason = f"V1买入({v1_conf:.0%}) V2观望"
        elif v2_action == 'buy' and v1_action == 'hold':
            if v2_conf >= 0.75:
                final_action = 'buy'
                reason = f"V2买入({v2_conf:.0%}) V1观望"
        elif v1_action == 'sell' or v2_action == 'sell':
            final_action = 'sell'
            reason = "平仓信号"
        
        return WeightedSignal(
            symbol=symbol,
            action=final_action,
            v1_signal=v1_raw,
            v2_signal=v2_raw,
            v1_confidence=v1_conf,
            v2_confidence=v2_conf,
            weighted_confidence=weighted_conf,
            final_action=final_action,
            reason=reason,
            timestamp=datetime.now().isoformat()
        )
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'expert_mode': self.expert_mode,
            'weights': {
                'v1_trend': round(self.v1_weight, 2),
                'v2_breakout': round(self.v2_weight, 2)
            }
        }


class MoleWeightedEngine:
    """
    🐹 打地鼠加权引擎
    
    V1: RSI均值回归 + 布林带
    V2: 动量爆发策略
    """
    
    def __init__(self, v1_weight: float = 0.5, expert_mode: bool = False):
        self.name = "🐹 打地鼠加权引擎"
        
        self.v1 = get_mole_strategy()
        self.v2 = get_mole_v2_strategy()
        
        self.v1_weight = max(0, min(1, v1_weight))
        self.v2_weight = 1 - self.v1_weight
        
        self.expert_mode = expert_mode
        if not expert_mode:
            self.v1_weight = max(0.3, min(0.7, self.v1_weight))
            self.v2_weight = 1 - self.v1_weight
        
        self.signals = {}
    
    def set_weights(self, v1_weight: float, expert_mode: bool = None):
        """调整权重"""
        if expert_mode is not None:
            self.expert_mode = expert_mode
        
        self.v1_weight = max(0, min(1, v1_weight))
        
        if not self.expert_mode:
            self.v1_weight = max(0.3, min(0.7, self.v1_weight))
        
        self.v2_weight = 1 - self.v1_weight
    
    def generate_signal(self, symbol: str, market_data: Dict) -> WeightedSignal:
        """生成加权信号"""
        v1_raw = self.v1.generate_signal(symbol, market_data)
        v1_conf = v1_raw.get('confidence', 0)
        
        v2_raw = self.v2.generate_signal(symbol, market_data)
        v2_conf = v2_raw.get('confidence', 0)
        
        weighted_conf = v1_conf * self.v1_weight + v2_conf * self.v2_weight
        
        v1_action = v1_raw.get('action', 'hold')
        v2_action = v2_raw.get('action', 'hold')
        
        final_action = 'hold'
        reason = ''
        
        if v1_action == 'buy' and v2_action == 'buy':
            final_action = 'buy'
            reason = f"双重买入 V1({v1_conf:.0%})×{self.v1_weight:.0%}+V2({v2_conf:.0%})×{self.v2_weight:.0%}"
        elif v1_action == 'buy' and v2_action == 'hold':
            if v1_conf >= 0.7:
                final_action = 'buy'
                reason = f"V1买入({v1_conf:.0%})"
        elif v2_action == 'buy' and v1_action == 'hold':
            if v2_conf >= 0.75:
                final_action = 'buy'
                reason = f"V2买入({v2_conf:.0%})"
        elif v1_action == 'sell' or v2_action == 'sell':
            final_action = 'sell'
            reason = "平仓信号"
        
        return WeightedSignal(
            symbol=symbol,
            action=final_action,
            v1_signal=v1_raw,
            v2_signal=v2_raw,
            v1_confidence=v1_conf,
            v2_confidence=v2_conf,
            weighted_confidence=weighted_conf,
            final_action=final_action,
            reason=reason,
            timestamp=datetime.now().isoformat()
        )
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'expert_mode': self.expert_mode,
            'weights': {
                'v1_mean_reversion': round(self.v1_weight, 2),
                'v2_momentum': round(self.v2_weight, 2)
            }
        }


# 单例
_rabbit_engine = None
_mole_engine = None


def get_rabbit_weighted_engine(v1_weight: float = 0.5, expert_mode: bool = False) -> RabbitWeightedEngine:
    global _rabbit_engine
    if _rabbit_engine is None:
        _rabbit_engine = RabbitWeightedEngine(v1_weight, expert_mode)
    return _rabbit_engine


def get_mole_weighted_engine(v1_weight: float = 0.5, expert_mode: bool = False) -> MoleWeightedEngine:
    global _mole_engine
    if _mole_engine is None:
        _mole_engine = MoleWeightedEngine(v1_weight, expert_mode)
    return _mole_engine


if __name__ == '__main__':
    print("=" * 60)
    print("🐰🐹 加权引擎测试")
    print("=" * 60)
    
    # 兔子引擎
    engine = RabbitWeightedEngine(v1_weight=0.6, expert_mode=False)
    print(f"\n兔子引擎: V1={engine.v1_weight:.0%}, V2={engine.v2_weight:.0%}")
    print(f"专家模式: {engine.expert_mode}")
    
    # 地鼠引擎
    mole = MoleWeightedEngine(v1_weight=0.4, expert_mode=True)
    print(f"\n地鼠引擎: V1={mole.v1_weight:.0%}, V2={mole.v2_weight:.0%}")
    print(f"专家模式: {mole.expert_mode}")
    
    # 权重调整测试
    print("\n权重调整测试:")
    mole.set_weights(0.9, expert_mode=True)
    print(f"专家模式90%: V1={mole.v1_weight:.0%}, V2={mole.v2_weight:.0%}")
    
    mole.set_weights(0.9, expert_mode=False)
    print(f"普通模式90%: V1={mole.v1_weight:.0%}, V2={mole.v2_weight:.0%}")
    
    print("\n✅ 测试通过!")
