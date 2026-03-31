#!/usr/bin/env python3
"""
🐹 打地鼠策略 V2 - 动量型高波动策略
===================================
基于动量指标的趋势跟随策略
专注高波动行情的动量爆发点
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import math

# 动量信号阈值
MOMENTUM_THRESHOLDS = {
    'min_volatility': 0.10,          # 最小波动率 10%
    'min_momentum': 0.03,            # 最小动量 3%
    'volume_surge': 2.5,             # 成交量激增 2.5x
    'rsi_overbought': 70,             # RSI过热
    'rsi_oversold': 30,              # RSI超卖
    'stoch_overbought': 80,          # 随机指标过热
    'stoch_oversold': 20,           # 随机指标超卖
}

# 风险参数
RISK_PARAMS = {
    'stop_loss': 0.06,               # 6% 止损 (更宽)
    'take_profit': 0.20,             # 20% 止盈 (更高)
    'max_position': 0.18,            # 最大仓位 18%
    'max_total_position': 0.20,     # 总仓位上限 20%
    'min_confidence': 0.55,         # 最低置信度
    'max_holding_days': 2,          # 最大持仓2天
}


class MoleV2Strategy:
    """🐹 打地鼠 V2 - 动量型高波动策略"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.name = "🐹 打地鼠V2"
        self.version = "v2.0-momentum"
        self.thresholds = MOMENTUM_THRESHOLDS.copy()
        self.params = RISK_PARAMS.copy()
        
        if config:
            self.params.update(config)
            self.thresholds.update(config.get('momentum', {}))
        
        # 状态
        self.positions = {}
        self.signals = {}
    
    # ═══════════════════════════════════════════════════════════════════
    # 指标计算
    # ═══════════════════════════════════════════════════════════════════
    
    def calculate_momentum(self, prices: List[float], period: int = 10) -> float:
        """计算动量指标 (Momentum)"""
        if len(prices) < period + 1:
            return 0
        return (prices[-1] - prices[-period]) / prices[-period]
    
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
    
    def calculate_stochastic(self, highs: List[float], lows: List[float], closes: List[float], k_period: int = 14, d_period: int = 3) -> Tuple[float, float]:
        """计算随机指标 %K 和 %D"""
        if len(closes) < k_period:
            return 50, 50
        
        recent_highs = highs[-k_period:]
        recent_lows = lows[-k_period:]
        
        highest_high = max(recent_highs)
        lowest_low = min(recent_lows)
        
        current_close = closes[-1]
        
        if highest_high == lowest_low:
            return 50, 50
        
        k_raw = (current_close - lowest_low) / (highest_high - lowest_low) * 100
        
        # %D 是 %K 的移动平均
        # 简化: 直接用当前 %K
        k = k_raw
        d = k_raw  # 简化处理
        
        return k, d
    
    def calculate_macd(self, closes: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[float, float, float]:
        """计算MACD"""
        if len(closes) < slow:
            return 0, 0, 0
        
        # 简化EMA计算
        def ema(data, period):
            if len(data) < period:
                return sum(data) / len(data)
            multiplier = 2 / (period + 1)
            ema_val = sum(data[:period]) / period
            for price in data[period:]:
                ema_val = (price - ema_val) * multiplier + ema_val
            return ema_val
        
        ema_fast = ema(closes, fast)
        ema_slow = ema(closes, slow)
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line * 0.9  # 简化signal
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    def calculate_volume_ratio(self, volumes: List[float], period: int = 20) -> float:
        """计算成交量比率"""
        if len(volumes) < period:
            return 1.0
        avg_vol = sum(volumes[-period:]) / period
        return volumes[-1] / avg_vol if avg_vol > 0 else 1.0
    
    def calculate_acceleration(self, prices: List[float], period: int = 5) -> float:
        """计算价格加速度"""
        if len(prices) < period * 2:
            return 0
        
        # 计算不同周期的动量
        mom_short = self.calculate_momentum(prices, period)
        mom_long = self.calculate_momentum(prices, period * 2)
        
        # 加速度 = 短期动量 - 长期动量
        return mom_short - mom_long
    
    # ═══════════════════════════════════════════════════════════════════
    # 市场分析
    # ═══════════════════════════════════════════════════════════════════
    
    def analyze_market(self, symbol: str, data: Dict) -> Dict:
        """
        分析市场数据
        data格式:
        {
            'price': float,
            'high_24h': float, 'low_24h': float,
            'opens': List[float], 'highs': List[float], 'lows': List[float],
            'closes': List[float], 'volumes': List[float],
            'volume': float, 'avg_volume': float
        }
        """
        price = data.get('price', 0)
        closes = data.get('closes', [price])
        volumes = data.get('volumes', [1])
        highs = data.get('highs', closes)
        lows = data.get('lows', closes)
        high_24h = data.get('high_24h', price)
        low_24h = data.get('low_24h', price)
        volume = data.get('volume', 1)
        avg_volume = data.get('avg_volume', volume)
        
        # 计算波动率
        volatility = (high_24h - low_24h) / price if price > 0 else 0
        
        # 计算指标
        rsi = self.calculate_rsi(closes)
        k, d = self.calculate_stochastic(highs, lows, closes)
        macd, signal, histogram = self.calculate_macd(closes)
        volume_ratio = self.calculate_volume_ratio(volumes)
        momentum = self.calculate_momentum(closes)
        acceleration = self.calculate_acceleration(closes)
        
        # 信号判断
        signal = 'neutral'
        confidence = 0.5
        reason = ''
        direction = 0
        
        # ===== 买入信号: 强势动量 =====
        # 条件: 动量 > 阈值 + 成交量爆发 + RSI未过热
        if momentum >= self.thresholds['min_momentum']:
            if volume_ratio >= self.thresholds['volume_surge']:
                if rsi < self.thresholds['rsi_overbought']:
                    # 检查随机指标
                    if k < self.thresholds['stoch_overbought']:
                        signal = 'buy'
                        direction = 1
                        confidence = 0.75
                        reason = f"动量({momentum:.1%})爆发({volume_ratio:.1f}x)"
                        
                        # 加速确认
                        if acceleration > 0:
                            confidence = 0.85
                            reason += f"+加速({acceleration:.3f})"
        
        # ===== 买入信号: 超卖反弹 =====
        if signal == 'neutral':
            if rsi < self.thresholds['rsi_oversold']:
                if k < self.thresholds['stoch_oversold']:
                    signal = 'buy'
                    direction = 1
                    confidence = 0.70
                    reason = f"RSI({rsi:.0f})随机({k:.0f})超卖"
        
        # ===== 卖出信号: 动量衰竭 =====
        if momentum < -self.thresholds['min_momentum']:
            if volume_ratio >= self.thresholds['volume_surge']:
                if rsi > self.thresholds['rsi_overbought']:
                    signal = 'sell'
                    direction = -1
                    confidence = 0.75
                    reason = f"动量({momentum:.1%})衰竭RSI({rsi:.0f})"
        
        # ===== MACD背离 =====
        if signal == 'neutral':
            if histogram > 0 and momentum > 0.05:
                signal = 'buy'
                direction = 1
                confidence = 0.65
                reason = f"MACD({histogram:.4f})金叉"
            elif histogram < 0 and momentum < -0.05:
                signal = 'sell'
                direction = -1
                confidence = 0.65
                reason = f"MACD({histogram:.4f})死叉"
        
        return {
            'symbol': symbol,
            'price': price,
            'rsi': rsi,
            'stoch_k': k,
            'stoch_d': d,
            'macd_histogram': histogram,
            'momentum': momentum,
            'acceleration': acceleration,
            'volume_ratio': volume_ratio,
            'volatility': volatility,
            'signal': signal,
            'direction': direction,
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
        
        if analysis['volatility'] < self.thresholds['min_volatility']:
            return False, f"波动率{analysis['volatility']:.1%}不足"
        
        if analysis['volume_ratio'] < self.thresholds['volume_surge']:
            return False, f"成交量比{analysis['volume_ratio']:.1f}x不足"
        
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
            return True, f"卖出: {analysis['reason']}"
        
        return False, "继续持有"
    
    def calculate_position(self, confidence: float, volatility: float, momentum: float) -> float:
        """计算仓位"""
        # 基础仓位 8%
        position = 0.08
        
        # 置信度加成
        position += (confidence - 0.5) * 0.15
        
        # 波动率加成: 波动越大，仓位越小
        volatility_penalty = (volatility - 0.10) * 0.2
        position -= max(0, volatility_penalty)
        
        # 动量加成
        if momentum > 0.05:
            position += 0.02
        
        return max(0.05, min(position, self.params['max_position']))
    
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
                position = self.calculate_position(
                    analysis['confidence'],
                    analysis['volatility'],
                    analysis['momentum']
                )
                quantity = position / analysis['price']
        
        return {
            'symbol': symbol,
            'action': action,
            'quantity': quantity,
            'confidence': analysis['confidence'],
            'reason': reason,
            'signal': analysis['signal'],
            'strategy': 'mole_v2',
            'rsi': analysis['rsi'],
            'momentum': analysis['momentum'],
            'volume_ratio': analysis['volume_ratio'],
            'volatility': analysis['volatility'],
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
_mole_v2 = None

def get_mole_v2_strategy(config: Optional[Dict] = None) -> MoleV2Strategy:
    global _mole_v2
    if _mole_v2 is None:
        _mole_v2 = MoleV2Strategy(config)
    return _mole_v2


if __name__ == '__main__':
    strategy = get_mole_v2_strategy()
    
    # 模拟动量爆发数据
    test_data = {
        'price': 0.00001000,
        'high_24h': 0.00001150,
        'low_24h': 0.00000850,
        'opens': [0.0000090 + i*0.0000001 for i in range(30)],
        'highs': [0.0000092 + i*0.0000001 for i in range(30)],
        'lows': [0.0000088 + i*0.0000001 for i in range(30)],
        'closes': [0.0000090 + i*0.00000012 for i in range(30)],
        'volumes': [100] * 25 + [400, 450, 500, 600, 700],
        'volume': 700,
        'avg_volume': 100
    }
    
    signal = strategy.generate_signal('SHIB', test_data)
    print(f"V2信号: {json.dumps(signal, indent=2, ensure_ascii=False)}")
