#!/usr/bin/env python3
"""
🐹 打地鼠策略 - 高波动套利策略
===================================
火控雷达系统，专注高波动山寨币
持仓周期: 1小时 - 3天
止损: 5% | 止盈: 15%
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import math

# 波动率阈值
VOLATILITY_THRESHOLDS = {
    'min_volatility_24h': 0.08,      # 8% 最小波动
    'min_volume_ratio': 2.0,          # 成交量放大2倍
    'vol_spike_ratio': 5.0,          # 成交量爆发5倍
}

# RSI/布林带阈值
SIGNAL_THRESHOLDS = {
    'rsi_oversold': 25,               # RSI超卖线
    'rsi_overbought': 75,             # RSI超买线
    'bb_std': 2,                      # 布林带标准差倍数
    'bb_lower_threshold': -0.8,      # 布林带下限阈值
    'bb_upper_threshold': 0.8,       # 布林带上限阈值
}

# 风险参数
RISK_PARAMS = {
    'stop_loss': 0.05,               # 5% 止损
    'take_profit': 0.15,              # 15% 止盈
    'base_position': 0.05,           # 5% 基础仓位
    'max_position': 0.15,            # 15% 最大单币仓位
    'max_total_position': 0.20,     # 20% 总仓位上限
    'min_confidence': 0.60,           # 60% 最低置信度
    'max_holding_hours': 72,         # 3天 最大持仓
}


class MoleStrategy:
    """🐹 打地鼠策略 - 高波动套利"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.name = "🐹 打地鼠"
        self.vol_thresholds = VOLATILITY_THRESHOLDS.copy()
        self.signal_thresholds = SIGNAL_THRESHOLDS.copy()
        self.params = RISK_PARAMS.copy()
        
        if config:
            self.params.update(config)
            self.vol_thresholds.update(config.get('volatility', {}))
            self.signal_thresholds.update(config.get('signal', {}))
        
        # 状态
        self.positions = {}   # symbol -> {entry_price, quantity, entry_time, entry_rsi}
        self.signals = {}    # symbol -> {signal, confidence, indicators}
        self.candidates = [] # 候选币种列表
    
    # ═══════════════════════════════════════════════════════════════════
    # 指标计算
    # ═══════════════════════════════════════════════════════════════════
    
    def calculate_rsi(self, closes: List[float], period: int = 14) -> float:
        """计算RSI"""
        if len(closes) < period + 1:
            return 50.0
        
        deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
        gains = [d if d > 0 else 0 for d in deltas[-period:]]
        losses = [-d if d < 0 else 0 for d in deltas[-period:]]
        
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        return 100.0 - (100.0 / (1.0 + rs))
    
    def calculate_sma(self, values: List[float], period: int) -> float:
        """计算简单移动平均"""
        if len(values) < period:
            return sum(values) / len(values) if values else 0
        return sum(values[-period:]) / period
    
    def calculate_std(self, values: List[float], period: int) -> float:
        """计算标准差"""
        if len(values) < period:
            return 0
        sma = self.calculate_sma(values, period)
        variance = sum((v - sma) ** 2 for v in values[-period:]) / period
        return math.sqrt(variance)
    
    def calculate_bb_position(self, closes: List[float], period: int = 20, std_mult: float = 2.0) -> float:
        """计算布林带位置 (-1 到 1)"""
        if len(closes) < period:
            return 0
        
        sma = self.calculate_sma(closes, period)
        std = self.calculate_std(closes, period)
        
        upper = sma + std_mult * std
        lower = sma - std_mult * std
        
        current = closes[-1]
        
        if upper == lower:
            return 0
        
        # 返回 -1 到 1 之间的位置
        position = (current - sma) / (std_mult * std) if std > 0 else 0
        return max(-1, min(1, position))
    
    def calculate_volume_ratio(self, volumes: List[float], period: int = 20) -> float:
        """计算成交量比率"""
        if len(volumes) < period:
            return 1.0
        
        avg_vol = sum(volumes[-period:]) / period
        current_vol = volumes[-1]
        
        return current_vol / avg_vol if avg_vol > 0 else 1.0
    
    def calculate_volatility(self, high: float, low: float, entry: float = None) -> float:
        """计算波动率"""
        if entry is None:
            entry = (high + low) / 2
        return abs(high - low) / entry if entry > 0 else 0
    
    # ═══════════════════════════════════════════════════════════════════
    # 市场数据分析
    # ═══════════════════════════════════════════════════════════════════
    
    def analyze_market(self, symbol: str, data: Dict) -> Dict:
        """
        分析市场数据，生成指标
        data格式:
        {
            'price': float,
            'high_24h': float,
            'low_24h': float,
            'volume': float,
            'avg_volume': float,
            'closes': List[float],    # K线收盘价
            'volumes': List[float],    # K线成交量
        }
        """
        price = data.get('price', 0)
        high_24h = data.get('high_24h', price)
        low_24h = data.get('low_24h', price)
        volume = data.get('volume', 0)
        avg_volume = data.get('avg_volume', volume)
        closes = data.get('closes', [price])
        volumes = data.get('volumes', [volume])
        
        # 计算指标
        rsi = self.calculate_rsi(closes)
        bb_pos = self.calculate_bb_position(closes)
        vol_ratio = self.calculate_volume_ratio(volumes)
        volatility = self.calculate_volatility(high_24h, low_24h, price)
        
        # 判断信号
        signal = 'neutral'
        confidence = 0.5
        reason = ''
        
        # ===== 买入信号 =====
        # 信号1: RSI超卖 + 布林带触底 (最强)
        if rsi < self.signal_thresholds['rsi_oversold'] and bb_pos < self.signal_thresholds['bb_lower_threshold']:
            signal = 'buy'
            confidence = 0.90
            reason = f'RSI超卖({rsi:.1f})+布林触底({bb_pos:.2f})'
        
        # 信号2: RSI超卖
        elif rsi < self.signal_thresholds['rsi_oversold']:
            signal = 'buy'
            confidence = 0.70
            reason = f'RSI超卖({rsi:.1f})'
        
        # 信号3: 成交量爆发 + 布林带低位
        elif vol_ratio >= self.vol_thresholds['vol_spike_ratio'] and bb_pos < -0.5:
            signal = 'buy'
            confidence = 0.65
            reason = f'成交量爆发({vol_ratio:.1f}x)+布林低位({bb_pos:.2f})'
        
        # 信号4: 触底反弹形态
        elif bb_pos < -0.8:
            signal = 'buy'
            confidence = 0.60
            reason = f'布林带触底({bb_pos:.2f})'
        
        # ===== 卖出信号 =====
        # 信号5: RSI超买 + 布林带触顶
        elif rsi > self.signal_thresholds['rsi_overbought'] and bb_pos > self.signal_thresholds['bb_upper_threshold']:
            signal = 'sell'
            confidence = 0.85
            reason = f'RSI过热({rsi:.1f})+布林触顶({bb_pos:.2f})'
        
        # 信号6: RSI超买
        elif rsi > self.signal_thresholds['rsi_overbought']:
            signal = 'sell'
            confidence = 0.70
            reason = f'RSI过热({rsi:.1f})'
        
        # 信号7: 布林带触顶
        elif bb_pos > 0.8:
            signal = 'sell'
            confidence = 0.60
            reason = f'布林带触顶({bb_pos:.2f})'
        
        return {
            'symbol': symbol,
            'price': price,
            'rsi': rsi,
            'bb_position': bb_pos,
            'vol_ratio': vol_ratio,
            'volatility': volatility,
            'signal': signal,
            'confidence': confidence,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
    
    # ═══════════════════════════════════════════════════════════════════
    # 交易决策
    # ═══════════════════════════════════════════════════════════════════
    
    def should_enter(self, symbol: str, analysis: Dict) -> Tuple[bool, str]:
        """判断是否应该入场"""
        # 必须是买入信号
        if analysis['signal'] != 'buy':
            return False, f"信号{analysis['signal']}非买入"
        
        # 置信度检查
        if analysis['confidence'] < self.params['min_confidence']:
            return False, f"置信度{analysis['confidence']:.0%}低于阈值{self.params['min_confidence']:.0%}"
        
        # 波动率检查
        if analysis['volatility'] < self.vol_thresholds['min_volatility_24h']:
            return False, f"波动率{analysis['volatility']:.1%}低于阈值{self.vol_thresholds['min_volatility_24h']:.1%}"
        
        # 成交量检查
        if analysis['vol_ratio'] < self.vol_thresholds['min_volume_ratio']:
            return False, f"成交量比{analysis['vol_ratio']:.1f}x低于阈值{self.vol_thresholds['min_volume_ratio']:.1f}x"
        
        # 总仓位检查
        total_pos = sum(p['quantity'] * p['entry_price'] for p in self.positions.values())
        if total_pos >= self.params['max_total_position']:
            return False, f"总仓位已满({self.params['max_total_position']:.0%})"
        
        return True, f"买入信号: {analysis['reason']}"
    
    def should_exit(self, symbol: str, current_price: float, analysis: Dict = None) -> Tuple[bool, str]:
        """判断是否应该出场"""
        if symbol not in self.positions:
            return False, "无持仓"
        
        pos = self.positions[symbol]
        entry_price = pos['entry_price']
        pnl_pct = (current_price - entry_price) / entry_price
        
        # 止损检查
        if pnl_pct <= -self.params['stop_loss']:
            return True, f"止损: {pnl_pct:.2%}"
        
        # 止盈检查
        if pnl_pct >= self.params['take_profit']:
            return True, f"止盈: {pnl_pct:.2%}"
        
        # 时间止损检查
        holding_hours = (datetime.now() - pos['entry_time']).total_seconds() / 3600
        if holding_hours >= self.params['max_holding_hours']:
            return True, f"时间止损: 持有{int(holding_hours)}小时"
        
        # 卖出信号检查
        if analysis and analysis['signal'] == 'sell':
            return True, f"卖出信号: {analysis['reason']}"
        
        return False, "继续持有"
    
    def calculate_position_size(self, volatility: float, rsi: float, price: float, total_capital: float = 1.0) -> float:
        """
        计算仓位大小
        
        公式:
        仓位 = 基础仓位(5%) + 波动加成 + 极端加成
        - 波动加成: 波动率 × 0.5%
        - 极端加成: RSI<20 或 RSI>80 → +3%
        """
        # 基础仓位
        position = self.params['base_position']
        
        # 波动加成: 波动率 × 0.5%
        # 8%波动 → +4%
        # 15%波动 → +7.5%
        volatility_bonus = volatility * 0.5
        position += volatility_bonus
        
        # 极端加成: RSI<20 或 RSI>80
        if rsi < 20 or rsi > 80:
            position += 0.03
        
        # 限制在 [2%, 15%]
        position = max(0.02, min(position, self.params['max_position']))
        
        return position * total_capital
    
    def generate_signal(self, symbol: str, market_data: Dict) -> Dict:
        """生成交易信号"""
        analysis = self.analyze_market(symbol, market_data)
        self.signals[symbol] = analysis
        
        action = 'hold'
        reason = ''
        quantity = 0
        position_size = 0
        
        # 检查是否应该平仓
        if symbol in self.positions:
            should_exit, exit_reason = self.should_exit(symbol, analysis['price'], analysis)
            if should_exit:
                action = 'sell'
                reason = exit_reason
                quantity = self.positions[symbol]['quantity']
        
        # 检查是否应该开仓
        if action == 'hold' and analysis['signal'] == 'buy':
            should_enter, enter_reason = self.should_enter(symbol, analysis)
            if should_enter:
                action = 'buy'
                reason = enter_reason
                position_size = self.calculate_position_size(
                    analysis['volatility'],
                    analysis['rsi'],
                    analysis['price']
                )
                quantity = position_size / analysis['price']
        
        return {
            'symbol': symbol,
            'action': action,
            'quantity': quantity,
            'position_size': position_size,
            'confidence': analysis['confidence'],
            'reason': reason,
            'signal': analysis['signal'],
            'rsi': analysis['rsi'],
            'bb_position': analysis['bb_position'],
            'vol_ratio': analysis['vol_ratio'],
            'volatility': analysis['volatility'],
            'timestamp': datetime.now().isoformat()
        }
    
    # ═══════════════════════════════════════════════════════════════════
    # 持仓管理
    # ═══════════════════════════════════════════════════════════════════
    
    def update_position(self, symbol: str, action: str, quantity: float, price: float, analysis: Dict = None):
        """更新持仓"""
        if action == 'buy':
            self.positions[symbol] = {
                'entry_price': price,
                'quantity': quantity,
                'entry_time': datetime.now(),
                'entry_rsi': analysis['rsi'] if analysis else 50,
                'entry_bb': analysis['bb_position'] if analysis else 0
            }
        elif action == 'sell' and symbol in self.positions:
            del self.positions[symbol]
    
    def get_status(self) -> Dict:
        """获取策略状态"""
        total_pnl = 0
        total_value = 0
        
        for symbol, pos in self.positions.items():
            current_value = pos['quantity'] * pos['entry_price'] * 1.02  # 估算
            pnl = (current_value - pos['entry_price'] * pos['quantity'])
            total_pnl += pnl
            total_value += current_value
        
        return {
            'name': self.name,
            'positions': len(self.positions),
            'signals': len(self.signals),
            'total_pnl': total_pnl,
            'total_value': total_value,
            'params': self.params,
            'thresholds': {
                'volatility': self.vol_thresholds,
                'signal': self.signal_thresholds
            }
        }
    
    def get_candidates_from_scan(self, scan_results: List[Dict]) -> List[Dict]:
        """
        从火控雷达扫描结果中筛选候选币种
        scan_results: List[{symbol, price, volatility, volume_ratio, rsi, bb_position}]
        """
        candidates = []
        
        for item in scan_results:
            # 检查是否满足基本条件
            if item.get('volatility', 0) >= self.vol_thresholds['min_volatility_24h']:
                if item.get('volume_ratio', 0) >= self.vol_thresholds['min_volume_ratio']:
                    candidates.append(item)
        
        # 按波动率排序
        return sorted(candidates, key=lambda x: x.get('volatility', 0), reverse=True)


# 单例实例
_mole_strategy = None

def get_mole_strategy(config: Optional[Dict] = None) -> MoleStrategy:
    """获取地鼠策略实例"""
    global _mole_strategy
    if _mole_strategy is None:
        _mole_strategy = MoleStrategy(config)
    return _mole_strategy


if __name__ == '__main__':
    # 测试
    strategy = get_mole_strategy()
    
    # 模拟市场数据
    test_data = {
        'price': 0.00001000,
        'high_24h': 0.00001100,
        'low_24h': 0.00000900,
        'volume': 5000000000,
        'avg_volume': 2000000000,
        'closes': [0.0000098, 0.0000095, 0.0000092, 0.0000090, 0.0000088, 0.0000085,
                   0.0000083, 0.0000082, 0.0000084, 0.0000086, 0.0000088, 0.0000090,
                   0.0000092, 0.0000094, 0.0000096, 0.0000098, 0.00001000],
        'volumes': [100, 120, 150, 200, 300, 500, 400, 350, 300, 250, 200, 180,
                    200, 250, 300, 500, 800]
    }
    
    signal = strategy.generate_signal('SHIB', test_data)
    print(f"📊 信号: {json.dumps(signal, indent=2, ensure_ascii=False)}")
    print(f"📊 状态: {json.dumps(strategy.get_status(), indent=2, ensure_ascii=False)}")
