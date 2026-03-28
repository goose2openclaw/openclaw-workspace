#!/usr/bin/env python3
"""
🐹 打地鼠策略 - 高波动套利
Version: 1.0
Author: GO2SE CEO
"""

import ccxt
import json
from datetime import datetime
from typing import Dict, List, Optional

class MoleStrategy:
    """打地鼠 - 高波动套利策略"""
    
    def __init__(self, config: dict = None):
        self.exchange = ccxt.binance()
        self.config = config or self._default_config()
        
    def _default_config(self) -> dict:
        return {
            'min_volatility_24h': 0.08,       # 8%
            'min_volume_ratio': 2.0,           # 成交量放大2倍
            'rsi_oversold': 25,
            'rsi_overbought': 75,
            'bb_std': 2,                       # 布林带标准差
            'vol_spike_ratio': 5.0,           # 成交量爆发5倍
            'base_position': 0.05,             # 5%
            'max_position': 0.15,              # 15%
            'stop_loss': -0.05,                # -5%
            'take_profit': 0.15,              # 15%
        }
    
    def get_candidates(self) -> List[dict]:
        """获取高波动候选币种"""
        # 主流币种列表
        symbols = ['BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'DOGE', 'DOT', 'AVAX', 
                   'LINK', 'UNI', 'ATOM', 'LTC', 'NEAR', 'APT', 'ARB', 'OP',
                   'MATIC', 'ETC', 'XLM', 'FIL']
        
        candidates = []
        
        for symbol in symbols:
            try:
                ticker = self.exchange.fetch_ticker(f'{symbol}/USDT')
                ohlcv_1h = self.fetch_ohlcv(symbol, '1h', 50)
                ohlcv_4h = self.fetch_ohlcv(symbol, '4h', 50)
                
                if self._check_conditions(ticker, ohlcv_1h, ohlcv_4h):
                    candidates.append({
                        'symbol': symbol,
                        'price': ticker['last'],
                        'volatility_24h': abs(ticker['percentage'] / 100) if ticker.get('percentage') else 0,
                        'volume_ratio': self._calculate_volume_ratio(ohlcv_1h),
                        'rsi': self._calculate_rsi(ohlcv_1h),
                        'bb_position': self._calculate_bb_position(ohlcv_1h),
                        'vol_spike': self._check_vol_spike(ohlcv_1h),
                    })
            except Exception as e:
                continue
        
        # 按波动率排序
        return sorted(candidates, key=lambda x: x['volatility_24h'], reverse=True)
    
    def fetch_ohlcv(self, symbol: str, timeframe: str = '1h', limit: int = 50):
        """获取K线数据"""
        try:
            return self.exchange.fetch_ohlcv(f'{symbol}/USDT', timeframe, limit=limit)
        except:
            return []
    
    def _check_conditions(self, ticker: dict, ohlcv_1h: list, ohlcv_4h: list) -> bool:
        """检查是否符合条件"""
        # 波动率检查
        change = abs(ticker.get('percentage', 0) / 100)
        if change < self.config['min_volatility_24h']:
            return False
        
        # 成交量爆发检查
        if len(ohlcv_1h) > 0:
            vol_ratio = self._calculate_volume_ratio(ohlcv_1h)
            if vol_ratio < self.config['min_volume_ratio']:
                return False
        
        return True
    
    def _calculate_rsi(self, ohlcv: list, period: int = 14) -> float:
        """计算RSI"""
        if len(ohlcv) < period + 1:
            return 50
        
        closes = [c[4] for c in ohlcv]
        deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
        
        gains = [d if d > 0 else 0 for d in deltas[-period:]]
        losses = [-d if d < 0 else 0 for d in deltas[-period:]]
        
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    def _calculate_volume_ratio(self, ohlcv: list) -> float:
        """计算成交量比率"""
        if len(ohlcv) < 20:
            return 1.0
        
        volumes = [c[5] for c in ohlcv]
        avg_vol = sum(volumes[-20:]) / 20
        current_vol = volumes[-1]
        
        return current_vol / avg_vol if avg_vol > 0 else 1.0
    
    def _calculate_bb_position(self, ohlcv: list) -> float:
        """计算布林带位置 (-1到1)"""
        if len(ohlcv) < 20:
            return 0
        
        closes = [c[4] for c in ohlcv]
        sma20 = sum(closes[-20:]) / 20
        std = (sum((c - sma20) ** 2 for c in closes[-20:]) / 20) ** 0.5
        
        upper = sma20 + self.config['bb_std'] * std
        lower = sma20 - self.config['bb_std'] * std
        
        current = closes[-1]
        
        if upper == lower:
            return 0
        
        return (current - sma20) / (upper - lower)
    
    def _check_vol_spike(self, ohlcv: list) -> bool:
        """检查成交量是否爆发"""
        return self._calculate_volume_ratio(ohlcv) > self.config['vol_spike_ratio']
    
    def calculate_position(self, volatility: float, rsi: float) -> float:
        """计算仓位"""
        # 基础仓位
        position = self.config['base_position']
        
        # 波动加成: 波动率 × 0.5%
        volatility_bonus = volatility * 0.5
        position += volatility_bonus
        
        # 极端加成: RSI<20 或 RSI>80 +3%
        if rsi < 20 or rsi > 80:
            position += 0.03
        
        return max(0.02, min(position, self.config['max_position']))
    
    def generate_signal(self, symbol: str) -> dict:
        """生成交易信号"""
        ohlcv = self.fetch_ohlcv(symbol, '1h', 50)
        ticker = self.exchange.fetch_ticker(f'{symbol}/USDT')
        
        rsi = self._calculate_rsi(ohlcv)
        bb_pos = self._calculate_bb_position(ohlcv)
        vol_spike = self._check_vol_spike(ohlcv)
        volatility = abs(ticker.get('percentage', 0) / 100)
        
        # 信号逻辑
        signal = 'neutral'
        confidence = 5
        
        # 买入信号: RSI超卖 且 触底反弹
        if rsi < self.config['rsi_oversold'] and bb_pos < -0.8:
            signal = 'buy'
            confidence = 7 + (25 - rsi) * 0.1
        # 卖出信号: RSI超买 且 触顶回落
        elif rsi > self.config['rsi_overbought'] and bb_pos > 0.8:
            signal = 'sell'
            confidence = 7 + (rsi - 75) * 0.1
        # 买入信号: 成交量爆发 + 触底
        elif vol_spike and bb_pos < -0.5:
            signal = 'buy'
            confidence = 6
        
        position = self.calculate_position(volatility, rsi)
        
        return {
            'strategy': 'mole',
            'symbol': symbol,
            'signal': signal,
            'confidence': min(10, max(0, confidence)),
            'position_size': position,
            'stop_loss': self.config['stop_loss'],
            'take_profit': self.config['take_profit'],
            'rsi': rsi,
            'bb_position': bb_pos,
            'vol_spike': vol_spike,
            'volatility': volatility,
            'timestamp': datetime.now().isoformat()
        }


if __name__ == '__main__':
    strategy = MoleStrategy()
    candidates = strategy.get_candidates()
    print(f"🐹 打地鼠策略 - 高波动候选: {len(candidates)}")
    for c in candidates[:5]:
        print(f"  {c['symbol']}: 波动 {c['volatility_24h']*100:.1f}%, RSI {c['rsi']:.1f}")
