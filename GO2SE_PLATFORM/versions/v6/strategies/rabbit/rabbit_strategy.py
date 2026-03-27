#!/usr/bin/env python3
"""
🐰 打兔子策略 - Top20趋势追踪
Version: 1.0
Author: GO2SE CEO
"""

import ccxt
import json
from datetime import datetime
from typing import Dict, List, Optional

class RabbitStrategy:
    """打兔子 - Top20趋势追踪策略"""
    
    def __init__(self, config: dict = None):
        self.exchange = ccxt.binance()
        self.config = config or self._default_config()
        self.top20_coins = [
            'BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'DOGE', 'AVAX', 
            'DOT', 'MATIC', 'LINK', 'UNI', 'ATOM', 'LTC', 'ETC', 'XLM',
            'NEAR', 'APT', 'ARB', 'OP'
        ]
        
    def _default_config(self) -> dict:
        return {
            'min_market_cap': 1_000_000_000,  # 10亿
            'min_volume_24h': 100_000_000,     # 1亿
            'ma_short': 20,
            'ma_long': 50,
            'min_momentum': 0.10,              # 10%
            'max_volatility': 0.05,            # 5%
            'base_position': 0.10,              # 10%
            'max_position': 0.20,               # 20%
            'stop_loss': -0.08,                 # -8%
            'take_profit': 0.30,               # 30%
        }
    
    def get_candidates(self) -> List[dict]:
        """获取符合条件的候选币种"""
        candidates = []
        
        for symbol in self.top20_coins:
            try:
                ticker = self.exchange.fetch_ticker(f'{symbol}/USDT')
                ohlcv = self.fetch_ohlcv(symbol, '1d', 60)
                
                if self._check_conditions(ticker, ohlcv):
                    candidates.append({
                        'symbol': symbol,
                        'price': ticker['last'],
                        'volume_24h': ticker['quoteVolume'],
                        'change_24h': ticker['percentage'],
                        'volatility': self._calculate_volatility(ohlcv),
                        'ma_trend': self._check_ma_trend(ohlcv),
                        'momentum': self._calculate_momentum(ohlcv),
                    })
            except Exception as e:
                continue
                
        return sorted(candidates, key=lambda x: x['momentum'], reverse=True)
    
    def fetch_ohlcv(self, symbol: str, timeframe: str = '1d', limit: int = 60):
        """获取K线数据"""
        try:
            return self.exchange.fetch_ohlcv(f'{symbol}/USDT', timeframe, limit=limit)
        except:
            return []
    
    def _check_conditions(self, ticker: dict, ohlcv: list) -> bool:
        """检查是否符合条件"""
        # 成交量检查
        if ticker.get('quoteVolume', 0) < self.config['min_volume_24h']:
            return False
        
        # 波动率检查
        volatility = self._calculate_volatility(ohlcv)
        if volatility > self.config['max_volatility']:
            return False
        
        # 动量检查
        momentum = self._calculate_momentum(ohlcv)
        if momentum < self.config['min_momentum']:
            return False
        
        return True
    
    def _calculate_volatility(self, ohlcv: list) -> float:
        """计算波动率 (标准差/均值)"""
        if len(ohlcv) < 20:
            return 0
        
        closes = [c[4] for c in ohlcv]
        mean = sum(closes) / len(closes)
        variance = sum((c - mean) ** 2 for c in closes) / len(closes)
        std = variance ** 0.5
        
        return std / mean if mean > 0 else 0
    
    def _calculate_momentum(self, ohlcv: list) -> float:
        """计算动量 (20日涨幅)"""
        if len(ohlcv) < 20:
            return 0
        
        closes = [c[4] for c in ohlcv]
        return (closes[-1] - closes[-20]) / closes[-20] if closes[-20] > 0 else 0
    
    def _check_ma_trend(self, ohlcv: list) -> str:
        """检查均线趋势"""
        if len(ohlcv) < 50:
            return 'unknown'
        
        closes = [c[4] for c in ohlcv]
        ma20 = sum(closes[-20:]) / 20
        ma50 = sum(closes[-50:]) / 50
        
        if ma20 > ma50:
            return 'bullish'
        elif ma20 < ma50:
            return 'bearish'
        return 'neutral'
    
    def calculate_position(self, confidence: float, volatility: float) -> float:
        """计算仓位"""
        # 基础仓位
        position = self.config['base_position']
        
        # 信心加成: (confidence-5) × 2%
        confidence_bonus = max(0, (confidence - 5)) * 0.02
        position += confidence_bonus
        
        # 波动减成: 5% - σ × 0.5%
        volatility_penalty = volatility * 0.5
        position -= volatility_penalty
        
        # 限制最大最小
        return max(0.05, min(position, self.config['max_position']))
    
    def generate_signal(self, symbol: str) -> dict:
        """生成交易信号"""
        ohlcv = self.fetch_ohlcv(symbol, '1d', 60)
        ticker = self.exchange.fetch_ticker(f'{symbol}/USDT')
        
        ma_trend = self._check_ma_trend(ohlcv)
        momentum = self._calculate_momentum(ohlcv)
        volatility = self._calculate_volatility(ohlcv)
        
        # 信号逻辑
        signal = 'neutral'
        confidence = 5
        
        if ma_trend == 'bullish' and momentum > 0.10:
            signal = 'buy'
            confidence = 5 + momentum * 10 + (0.05 - volatility) * 20
        elif ma_trend == 'bearish' or momentum < -0.05:
            signal = 'sell'
            confidence = 7
        
        position = self.calculate_position(confidence, volatility)
        
        return {
            'strategy': 'rabbit',
            'symbol': symbol,
            'signal': signal,
            'confidence': min(10, max(0, confidence)),
            'position_size': position,
            'stop_loss': self.config['stop_loss'],
            'take_profit': self.config['take_profit'],
            'ma_trend': ma_trend,
            'momentum': momentum,
            'volatility': volatility,
            'timestamp': datetime.now().isoformat()
        }


if __name__ == '__main__':
    strategy = RabbitStrategy()
    candidates = strategy.get_candidates()
    print(f"🐰 打兔子策略 - 候选币种: {len(candidates)}")
    for c in candidates[:5]:
        print(f"  {c['symbol']}: 动量 {c['momentum']*100:.1f}%, 趋势 {c['ma_trend']}")
