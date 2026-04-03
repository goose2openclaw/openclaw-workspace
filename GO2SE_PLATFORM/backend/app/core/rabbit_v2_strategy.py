#!/usr/bin/env python3
"""
🐰 打兔子策略 V2 - 突破型趋势跟踪
===================================
基于声纳库的突破型策略
识别关键阻力位/支撑位突破
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import math

# 目标币种 (前20主流)
MAINSTREAM_COINS = [
    'BTC', 'ETH', 'BNB', 'XRP', 'SOL', 'ADA', 'DOGE', 
    'AVAX', 'DOT', 'MATIC', 'LINK', 'UNI', 'ATOM', 'LTC',
    'ETC', 'XLM', 'ALGO', 'VET', 'ICP', 'FIL'
]

# 突破信号阈值
BREAKOUT_THRESHOLDS = {
    'min_breakout_pct': 0.02,        # 突破幅度 >= 2%
    'min_volume_ratio': 1.8,          # 成交量放大 1.8x
    'rsi_optimal_low': 45,            # RSI最佳区间下限
    'rsi_optimal_high': 65,          # RSI最佳区间上限
    'adx_min': 20,                   # ADX最小值
}

# 风险参数
RISK_PARAMS = {
    'stop_loss': 0.04,               # 4% 止损 (更紧)
    'take_profit': 0.10,              # 10% 止盈 (更高)
    'max_position': 0.12,            # 最大仓位 12%
    'max_total_position': 0.25,     # 总仓位上限 25%
    'min_confidence': 0.60,          # 最低置信度
    'max_holding_days': 5,           # 最大持仓5天
}


class RabbitV2Strategy:
    """🐰 打兔子 V2 - 突破型趋势跟踪"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.name = "🐰 打兔子V2"
        self.version = "v2.0-breakout"
        self.coins = MAINSTREAM_COINS
        self.thresholds = BREAKOUT_THRESHOLDS.copy()
        self.params = RISK_PARAMS.copy()
        
        if config:
            self.params.update(config)
            self.thresholds.update(config.get('breakout', {}))
        
        # 状态
        self.positions = {}
        self.signals = {}
    
    # ═══════════════════════════════════════════════════════════════════
    # 指标计算
    # ═══════════════════════════════════════════════════════════════════
    
    def calculate_atr(self, highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> float:
        """计算ATR (Average True Range)"""
        if len(highs) < period + 1:
            return 0
        
        trs = []
        for i in range(1, len(closes)):
            high = highs[i]
            low = lows[i]
            prev_close = closes[i-1]
            tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
            trs.append(tr)
        
        return sum(trs[-period:]) / period if trs else 0
    
    def calculate_adx(self, highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> float:
        """计算ADX (趋势强度)"""
        if len(highs) < period * 2:
            return 0
        
        # 计算 +DM 和 -DM
        plus_dm = []
        minus_dm = []
        
        for i in range(1, len(closes)):
            high_diff = highs[i] - highs[i-1]
            low_diff = lows[i-1] - lows[i]
            
            if high_diff > low_diff and high_diff > 0:
                plus_dm.append(high_diff)
                minus_dm.append(0)
            elif low_diff > high_diff and low_diff > 0:
                plus_dm.append(0)
                minus_dm.append(low_diff)
            else:
                plus_dm.append(0)
                minus_dm.append(0)
        
        # 计算 True Range
        atr = self.calculate_atr(highs, lows, closes, period)
        if atr == 0:
            return 0
        
        plus_di = (sum(plus_dm[-period:]) / period) / atr * 100
        minus_di = (sum(minus_dm[-period:]) / period) / atr * 100
        
        dx = abs(plus_di - minus_di) / (plus_di + minus_di) * 100 if (plus_di + minus_di) > 0 else 0
        
        return dx  # 简化版ADX
    
    def calculate_volume_ratio(self, volumes: List[float], period: int = 20) -> float:
        """计算成交量比率"""
        if len(volumes) < period:
            return 1.0
        avg_vol = sum(volumes[-period:]) / period
        return volumes[-1] / avg_vol if avg_vol > 0 else 1.0
    
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
    
    def detect_support_resistance(self, highs: List[float], lows: List[float], closes: List[float], lookback: int = 50) -> Dict:
        """检测支撑位和阻力位"""
        if len(closes) < lookback:
            lookback = len(closes)
        
        # 近20日高低点
        recent_closes = closes[-lookback:]
        resistance = max(recent_closes)
        support = min(recent_closes)
        
        # 当前价格位置
        current = closes[-1]
        position = (current - support) / (resistance - support) if resistance != support else 0.5
        
        return {
            'resistance': resistance,
            'support': support,
            'position': position,  # 0=支撑, 1=阻力
            'range': resistance - support
        }
    
    def detect_breakout(self, prices: List[float], volumes: List[float], thresholds: Dict) -> Dict:
        """检测突破信号"""
        if len(prices) < 20:
            return {'type': 'none', 'confidence': 0}
        
        # 检测近期高低点
        lookback = 20
        recent = prices[-lookback:]
        current = prices[-1]
        
        # 计算高低点
        high_20 = max(recent[:-1])  # 前19个的最高
        low_20 = min(recent[:-1])   # 前19个的最低
        
        # 突破检测
        breakout_type = 'none'
        breakout_pct = 0
        confidence = 0
        
        # 向上突破
        if current > high_20:
            breakout_type = 'up'
            breakout_pct = (current - high_20) / high_20
            confidence = min(1.0, breakout_pct * 10)  # 2%突破=0.2, 5%=0.5
        
        # 向下突破
        elif current < low_20:
            breakout_type = 'down'
            breakout_pct = (low_20 - current) / low_20
            confidence = min(1.0, breakout_pct * 10)
        
        return {
            'type': breakout_type,
            'pct': breakout_pct,
            'confidence': confidence,
            'high_20': high_20,
            'low_20': low_20
        }
    
    # ═══════════════════════════════════════════════════════════════════
    # 市场分析
    # ═══════════════════════════════════════════════════════════════════
    
    def analyze_market(self, symbol: str, data: Dict) -> Dict:
        """
        分析市场数据
        data格式:
        {
            'price': float,
            'high': float, 'low': float,
            'opens': List[float], 'highs': List[float], 'lows': List[float],
            'closes': List[float], 'volumes': List[float]
        }
        """
        price = data.get('price', 0)
        closes = data.get('closes', [price])
        volumes = data.get('volumes', [1])
        highs = data.get('highs', closes)
        lows = data.get('lows', closes)
        
        # 计算指标
        rsi = self.calculate_rsi(closes)
        volume_ratio = self.calculate_volume_ratio(volumes)
        breakout = self.detect_breakout(closes, volumes, self.thresholds)
        sr_levels = self.detect_support_resistance(highs, lows, closes)
        
        # 信号判断
        signal = 'neutral'
        confidence = 0.5
        reason = ''
        
        # ===== 买入信号: 向上突破 =====
        if breakout['type'] == 'up':
            # 检查突破幅度
            if breakout['pct'] >= self.thresholds['min_breakout_pct']:
                # 检查RSI是否在最佳区间
                if self.thresholds['rsi_optimal_low'] <= rsi <= self.thresholds['rsi_optimal_high']:
                    # 检查成交量
                    if volume_ratio >= self.thresholds['min_volume_ratio']:
                        signal = 'buy'
                        confidence = 0.80
                        reason = f"突破({breakout['pct']:.1%})RSI({rsi:.0f})量({volume_ratio:.1f}x)"
                    else:
                        signal = 'buy'
                        confidence = 0.65
                        reason = f"突破({breakout['pct']:.1%})RSI({rsi:.0f})量不足"
                elif rsi < self.thresholds['rsi_optimal_low']:
                    # RSI偏低，可能是假突破
                    confidence = 0.40
                    reason = f"RSI偏低({rsi:.0f})，突破待确认"
        
        # ===== 卖出信号: 向下突破 =====
        elif breakout['type'] == 'down':
            if breakout['pct'] >= self.thresholds['min_breakout_pct']:
                signal = 'sell'
                confidence = 0.75
                reason = f"下破({breakout['pct']:.1%})"
        
        # ===== 支撑位附近买入 =====
        elif sr_levels['position'] < 0.2 and rsi < 40:
            signal = 'buy'
            confidence = 0.60
            reason = f"支撑位RSI{rsi:.0f}"
        
        return {
            'symbol': symbol,
            'price': price,
            'rsi': rsi,
            'volume_ratio': volume_ratio,
            'breakout': breakout,
            'sr_levels': sr_levels,
            'signal': signal,
            'confidence': confidence,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
    
    # ═══════════════════════════════════════════════════════════════════
    # 交易决策
    # ═══════════════════════════════════════════════════════════════════
    
    def should_enter(self, analysis: Dict) -> Tuple[bool, str]:
        """判断是否入场"""
        if analysis['signal'] != 'buy':
            return False, f"信号{analysis['signal']}"
        
        if analysis['confidence'] < self.params['min_confidence']:
            return False, f"置信度{analysis['confidence']:.0%}"
        
        if analysis['breakout']['pct'] < self.thresholds['min_breakout_pct']:
            return False, f"突破幅度不足{analysis['breakout']['pct']:.1%}"
        
        return True, analysis['reason']
    
    def should_exit(self, symbol: str, current_price: float, analysis: Dict = None) -> Tuple[bool, str]:
        """判断是否出场"""
        if symbol not in self.positions:
            return False, "无持仓"
        
        pos = self.positions[symbol]
        entry_price = pos['entry_price']
        pnl_pct = (current_price - entry_price) / entry_price
        
        # 止损
        if pnl_pct <= -self.params['stop_loss']:
            return True, f"止损{pnl_pct:.2%}"
        
        # 止盈
        if pnl_pct >= self.params['take_profit']:
            return True, f"止盈{pnl_pct:.2%}"
        
        # 时间止损
        holding_days = (datetime.now() - pos['entry_time']).days
        if holding_days >= self.params['max_holding_days']:
            return True, f"时间止损{holding_days}天"
        
        # 卖出信号
        if analysis and analysis['signal'] == 'sell':
            return True, f"卖出信号: {analysis['reason']}"
        
        return False, "继续持有"
    
    def calculate_position(self, confidence: float, volatility: float = 0.03) -> float:
        """计算仓位"""
        # 基础仓位 6%
        position = 0.06
        
        # 置信度加成: 0.6→+0%, 0.8→+2%, 0.9→+4%
        confidence_bonus = (confidence - 0.5) * 0.1
        position += confidence_bonus
        
        # 波动加成
        volatility_bonus = volatility * 0.3
        position += volatility_bonus
        
        return max(0.03, min(position, self.params['max_position']))
    
    def generate_signal(self, symbol: str, market_data: Dict) -> Dict:
        """生成交易信号"""
        analysis = self.analyze_market(symbol, market_data)
        self.signals[symbol] = analysis
        
        action = 'hold'
        reason = ''
        quantity = 0
        
        if symbol in self.positions:
            should_exit, exit_reason = self.should_exit(symbol, analysis['price'], analysis)
            if should_exit:
                action = 'sell'
                reason = exit_reason
                quantity = self.positions[symbol]['quantity']
        
        if action == 'hold' and analysis['signal'] == 'buy':
            should_enter, enter_reason = self.should_enter(analysis)
            if should_enter:
                action = 'buy'
                reason = enter_reason
                volatility = abs(market_data.get('high', 0) - market_data.get('low', 0)) / market_data.get('price', 1)
                position = self.calculate_position(analysis['confidence'], volatility)
                quantity = position / analysis['price']
        
        return {
            'symbol': symbol,
            'action': action,
            'quantity': quantity,
            'confidence': analysis['confidence'],
            'reason': reason,
            'signal': analysis['signal'],
            'strategy': 'rabbit_v2',
            'rsi': analysis['rsi'],
            'volume_ratio': analysis['volume_ratio'],
            'breakout': analysis['breakout'],
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
        """获取状态"""
        return {
            'name': self.name,
            'version': self.version,
            'positions': len(self.positions),
            'params': self.params
        }


# 单例
_rabbit_v2 = None

def get_rabbit_v2_strategy(config: Optional[Dict] = None) -> RabbitV2Strategy:
    global _rabbit_v2
    if _rabbit_v2 is None:
        _rabbit_v2 = RabbitV2Strategy(config)
    return _rabbit_v2


if __name__ == '__main__':
    strategy = get_rabbit_v2_strategy()
    
    # 模拟突破数据
    test_data = {
        'price': 50500,
        'opens': [49500 + i*100 for i in range(20)],
        'highs': [49600 + i*150 for i in range(20)],
        'lows': [49400 + i*50 for i in range(20)],
        'closes': [49500 + i*120 for i in range(20)],
        'volumes': [1000] * 19 + [2500]  # 最后一天放量
    }
    test_data['high'] = test_data['closes'][-1] * 1.01
    test_data['low'] = test_data['closes'][-1] * 0.99
    
    signal = strategy.generate_signal('BTC', test_data)
    print(f"V2信号: {json.dumps(signal, indent=2, ensure_ascii=False)}")
