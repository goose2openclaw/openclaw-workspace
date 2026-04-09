#!/usr/bin/env python3
"""
🐰 打兔子策略 - 主流币趋势跟踪策略
===================================
趋势跟踪策略，专注前20主流加密货币
持仓周期: 1-7天
止损: 5% | 止盈: 8%
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# 主流币列表 (前20)
MAINSTREAM_COINS = [
    'BTC', 'ETH', 'BNB', 'XRP', 'SOL', 'ADA', 'DOGE', 
    'AVAX', 'DOT', 'MATIC', 'LINK', 'UNI', 'ATOM', 'LTC',
    'ETC', 'XLM', 'ALGO', 'VET', 'ICP', 'FIL'
]

# 趋势信号阈值
TREND_THRESHOLDS = {
    'rsi_overbought': 70,
    'rsi_oversold': 30,
    'ma_cross_bull': 'golden_cross',
    'ma_cross_bear': 'death_cross',
    'volume_spike': 1.5,  # 成交量异常倍数
}

# 风险参数
RISK_PARAMS = {
    'stop_loss': 0.05,  # 5% 止损
    'take_profit': 0.08,  # 8% 止盈
    'max_position': 0.10,  # 单币最大仓位 10%
    'max_total_position': 0.25,  # 总仓位上限 25%
    'min_confidence': 0.65,  # 最低置信度
}

class RabbitStrategy:
    """🐰 打兔子策略 - 主流币趋势跟踪"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.name = "🐰 打兔子"
        self.coins = MAINSTREAM_COINS
        self.params = RISK_PARAMS.copy()
        if config:
            self.params.update(config)
        
        # 状态
        self.positions = {}  # symbol -> {entry_price, quantity, entry_time}
        self.signals = {}    # symbol -> {signal, confidence, timestamp}
        
    def analyze_trend(self, symbol: str, data: Dict) -> Dict:
        """分析币种趋势"""
        price = data.get('price', 0)
        rsi = data.get('rsi', 50)
        ma_7 = data.get('ma7', price)
        ma_25 = data.get('ma25', price)
        volume = data.get('volume', 0)
        avg_volume = data.get('avg_volume', volume)
        
        # 趋势判断
        signal = 'neutral'
        confidence = 0.5
        
        # MA金叉/死叉
        if ma_7 > ma_25 and price > ma_7:
            signal = 'bullish'
            confidence = 0.7
        elif ma_7 < ma_25 and price < ma_7:
            signal = 'bearish'
            confidence = 0.7
        else:
            signal = 'neutral'
            confidence = 0.5
        
        # RSI辅助
        if rsi > TREND_THRESHOLDS['rsi_overbought'] and signal == 'bullish':
            confidence *= 0.8  # 过热，降低置信度
        elif rsi < TREND_THRESHOLDS['rsi_oversold'] and signal == 'bearish':
            confidence *= 0.8
        
        # 成交量确认
        if volume > avg_volume * TREND_THRESHOLDS['volume_spike']:
            confidence = min(1.0, confidence * 1.2)
        
        return {
            'symbol': symbol,
            'signal': signal,
            'confidence': confidence,
            'price': price,
            'rsi': rsi,
            'trend': 'up' if signal == 'bullish' else 'down' if signal == 'bearish' else 'sideways'
        }
    
    def should_enter(self, symbol: str, analysis: Dict) -> Tuple[bool, str]:
        """判断是否应该入场"""
        if analysis['signal'] != 'bullish':
            return False, "趋势非看涨"
        
        if analysis['confidence'] < self.params['min_confidence']:
            return False, f"置信度{analysis['confidence']:.0%}低于阈值{self.params['min_confidence']:.0%}"
        
        # 检查当前仓位
        total_pos = sum(p['quantity'] * p['entry_price'] for p in self.positions.values())
        if total_pos >= self.params['max_total_position']:
            return False, f"总仓位已达{self.params['max_total_position']:.0%}"
        
        return True, "信号满足"
    
    def should_exit(self, symbol: str, current_price: float) -> Tuple[bool, str]:
        """判断是否应该止损/止盈"""
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
        
        # 时间止损 (持有超过7天)
        holding_days = (datetime.now() - pos['entry_time']).days
        if holding_days > 7:
            return True, f"时间止损: 持有{holding_days}天"
        
        return False, "继续持有"
    
    def generate_signal(self, symbol: str, market_data: Dict) -> Dict:
        """生成交易信号"""
        analysis = self.analyze_trend(symbol, market_data)
        self.signals[symbol] = analysis
        
        action = 'hold'
        reason = ''
        quantity = 0
        
        # 检查是否应该平仓
        if symbol in self.positions:
            should_exit, exit_reason = self.should_exit(symbol, analysis['price'])
            if should_exit:
                action = 'sell'
                reason = exit_reason
        
        # 检查是否应该开仓
        if action == 'hold' and analysis['signal'] == 'bullish':
            should_enter, enter_reason = self.should_enter(symbol, analysis)
            if should_enter:
                action = 'buy'
                reason = enter_reason
                max_qty = self.params['max_position'] * 1.0 / analysis['price']  # 假设1 USDT
                quantity = min(max_qty, 0.1)  # 最大10%仓位
        
        return {
            'symbol': symbol,
            'action': action,
            'quantity': quantity,
            'confidence': analysis['confidence'],
            'reason': reason,
            'signal': analysis['signal'],
            'timestamp': datetime.now().isoformat()
        }
    
    def update_position(self, symbol: str, action: str, quantity: float, price: float):
        """更新持仓"""
        if action == 'buy':
            self.positions[symbol] = {
                'entry_price': price,
                'quantity': quantity,
                'entry_time': datetime.now()
            }
        elif action == 'sell' and symbol in self.positions:
            del self.positions[symbol]
    
    def get_status(self) -> Dict:
        """获取策略状态"""
        total_pnl = 0
        for symbol, pos in self.positions.items():
            # 估算当前盈亏
            estimated_price = pos['entry_price'] * 1.02  # 假设2%利润
            pnl = (estimated_price - pos['entry_price']) * pos['quantity']
            total_pnl += pnl
        
        return {
            'name': self.name,
            'positions': len(self.positions),
            'signals': len(self.signals),
            'total_pnl': total_pnl,
            'params': self.params
        }


# 单例实例
_rabbit_strategy = None

def get_rabbit_strategy(config: Optional[Dict] = None) -> RabbitStrategy:
    """获取兔子策略实例"""
    global _rabbit_strategy
    if _rabbit_strategy is None:
        _rabbit_strategy = RabbitStrategy(config)
    return _rabbit_strategy


if __name__ == '__main__':
    # 测试
    strategy = get_rabbit_strategy()
    
    # 模拟市场数据
    test_data = {
        'price': 50000,
        'rsi': 55,
        'ma7': 49500,
        'ma25': 49000,
        'volume': 1000000,
        'avg_volume': 800000
    }
    
    signal = strategy.generate_signal('BTC', test_data)
    print(f"信号: {json.dumps(signal, indent=2, ensure_ascii=False)}")
    print(f"状态: {json.dumps(strategy.get_status(), indent=2, ensure_ascii=False)}")
