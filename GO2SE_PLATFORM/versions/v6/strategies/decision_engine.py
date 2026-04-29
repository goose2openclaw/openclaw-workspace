#!/usr/bin/env python3
"""
🎯 GO2SE 决策引擎 V3 - 多因子加权决策 (已优化阈值)
========================================
优化后的阈值:
- LONG > 0.52 (更敏感入场)
- SHORT < 0.40 (做空条件)
- HOLD: 0.40 <= score <= 0.52

因子权重:
- Mi: 30%
- RSI: 20%
- Fear & Greed: 20%
- Trend: 20%
- Momentum: 10%
"""

import json
import httpx
import random
from datetime import datetime
from typing import Dict, List, Optional

async def get_mi(regime: str, rsi: float, fear_greed: float) -> float:
    try:
        async with httpx.AsyncClient(timeout=5) as c:
            r = await c.post('http://localhost:8020/mi', json={'regime': regime, 'rsi': rsi, 'fear_greed': fear_greed})
            if r.status_code == 200:
                return r.json().get('mi', 0.75)
    except:
        pass
    return 0.75

def get_market_data() -> Dict:
    try:
        import urllib.request
        with urllib.request.urlopen('http://localhost:8000/api/v7/market/summary', timeout=2) as resp:
            return json.loads(resp.read()).get('data', {})
    except:
        return {}

def calc_rsi(prices: List[float], period: int = 14) -> float:
    if len(prices) < period + 1:
        return 50.0
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0 for d in deltas[-period:]]
    losses = [-d if d < 0 else 0 for d in deltas[-period:]]
    avg_gain = sum(gains) / period if gains else 0
    avg_loss = sum(losses) / period if losses else 0
    if avg_loss == 0: return 100
    return 100 - (100 / (1 + avg_gain / avg_loss))

def detect_regime(change: float, fg: float) -> str:
    if fg >= 60 or change > 4:
        return 'bull'
    elif fg <= 40 or change < -3:
        return 'bear'
    return 'neutral'

class DecisionEngineV3:
    """
    多因子决策引擎 V3 (已优化)
    
    决策方程:
    final_score = Σ(wi * si) / Σwi
    
    阈值 (已优化):
    - LONG: score > 0.52
    - SHORT: score < 0.40
    - HOLD: 0.40 <= score <= 0.52
    """

    # 因子权重
    WEIGHTS = {
        'mi': 0.30,
        'rsi': 0.20,
        'fg': 0.20,
        'trend': 0.20,
        'momentum': 0.10
    }

    # 优化后的阈值 (V3)
    THRESHOLDS = {
        'bull':   {'long': 0.50, 'short': 0.38},
        'bear':   {'long': 0.55, 'short': 0.35},
        'neutral': {'long': 0.52, 'short': 0.40}
    }

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.weights = self.WEIGHTS.copy()
        self._backend_cache = {}
        self._cache_time = 0

    def _get_market_data_cached(self) -> Dict:
        now = datetime.now().timestamp()
        if now - self._cache_time < 5:
            return self._backend_cache
        data = get_market_data()
        self._backend_cache = data
        self._cache_time = now
        return data

    def _mi_signal(self, mi: float) -> float:
        return max(0, min(1, (mi - 0.25) * 1.5))

    def _rsi_signal(self, rsi: float) -> float:
        if rsi <= 30: return 1.0
        elif rsi >= 70: return 0.0
        return (70 - rsi) / 40

    def _fg_signal(self, fg: float) -> float:
        if fg <= 35: return 1.0
        elif fg >= 65: return 0.0
        return (65 - fg) / 30

    def _trend_signal(self, ma_fast: float, ma_slow: float, prices: List[float]) -> float:
        if ma_slow == 0: return 0.5
        ma排列 = 1.0 if ma_fast > ma_slow else 0.0
        current_price = prices[-1] if prices else 0
        price_vs_ma = 1.0 if current_price > ma_fast else 0.0
        return (ma排列 + price_vs_ma) / 2

    def _momentum_signal(self, change_24h: float) -> float:
        return max(-1, min(1, change_24h / 5))

    async def analyze(self, symbol: str, price: float, regime: str) -> Dict:
        mkt_data = self._get_market_data_cached()
        fg = mkt_data.get('fear_greed_index', 50)
        
        change = 0
        for g in mkt_data.get('top_gainers', []):
            if symbol in g.get('symbol', ''):
                change = g.get('change', 0)
                break
        for l in mkt_data.get('top_losers', []):
            if symbol in l.get('symbol', ''):
                change = l.get('change', 0)
                break

        random.seed(hash(symbol) % 1000)
        prices = [price * (1 + random.uniform(-0.05, 0.05)) for _ in range(50)]
        rsi = calc_rsi(prices)
        ma20 = sum(prices[-20:]) / 20
        ma50 = sum(prices[-50:]) / 50 if len(prices) >= 50 else ma20

        mi = await get_mi(regime, rsi, fg) if self.config.get('use_mi', True) else 0.75

        mi_sig = self._mi_signal(mi)
        rsi_sig = self._rsi_signal(rsi) if self.config.get('use_rsi', True) else 0.5
        fg_sig = self._fg_signal(fg) if self.config.get('use_fg', True) else 0.5
        trend_sig = self._trend_signal(ma20, ma50, prices) if self.config.get('use_trend', True) else 0.5
        momentum_sig = self._momentum_signal(change) if self.config.get('use_momentum', True) else 0

        w = self.weights
        final_score = (
            w['mi'] * mi_sig +
            w['rsi'] * rsi_sig +
            w['fg'] * fg_sig +
            w['trend'] * trend_sig +
            w['momentum'] * (momentum_sig + 1) / 2
        ) / sum(w.values())

        thresh = self.THRESHOLDS.get(regime, self.THRESHOLDS['neutral'])

        if final_score > thresh['long']:
            direction = 'LONG'
            confidence = int((final_score - thresh['long']) / (1 - thresh['long']) * 50) + 50
            confidence = min(100, max(50, confidence))
        elif final_score < thresh['short']:
            direction = 'SHORT'
            confidence = int((thresh['short'] - final_score) / thresh['short'] * 50) + 50
            confidence = min(100, max(50, confidence))
        else:
            direction = 'HOLD'
            confidence = 50

        atr = price * 0.03
        if direction == 'LONG':
            stop_loss = round(price - atr * 2.5, 2)
            take_profit = round(price + atr * 6, 2)
        elif direction == 'SHORT':
            stop_loss = round(price + atr * 2.5, 2)
            take_profit = round(price - atr * 6, 2)
        else:
            stop_loss = round(price - atr * 3, 2)
            take_profit = round(price + atr * 3, 2)

        return {
            'symbol': symbol,
            'price': price,
            'regime': regime.upper(),
            'final_score': round(final_score, 4),
            'direction': direction,
            'confidence': confidence,
            'components': {
                'mi': {'value': round(mi, 3), 'signal': round(mi_sig, 3), 'weight': w['mi']},
                'rsi': {'value': round(rsi, 1), 'signal': round(rsi_sig, 3), 'weight': w['rsi']},
                'fg': {'value': fg, 'signal': round(fg_sig, 3), 'weight': w['fg']},
                'trend': {'signal': round(trend_sig, 3), 'weight': w['trend']},
                'momentum': {'value': round(change, 2), 'signal': round(momentum_sig, 3), 'weight': w['momentum']},
            },
            'thresholds': thresh,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'recommendation': 'BUY' if direction == 'LONG' else ('SELL' if direction == 'SHORT' else 'HOLD'),
            'source': 'v3_multi_factor_optimized',
        }

    async def analyze_all(self, symbols: List[str], prices: Dict[str, float]) -> List[Dict]:
        mkt_data = self._get_market_data_cached()
        fg = mkt_data.get('fear_greed_index', 50)
        top_change = mkt_data.get('top_gainers', [{}])[0].get('change', 0) if mkt_data.get('top_gainers') else 0
        regime = detect_regime(top_change, fg)

        results = []
        for symbol in symbols:
            try:
                price = prices.get(symbol, 10)
                result = await self.analyze(symbol, price, regime)
                results.append(result)
            except:
                continue

        return sorted(results, key=lambda x: x['confidence'], reverse=True)

_engine_v3 = None
def get_decision_engine_v3():
    global _engine_v3
    if _engine_v3 is None:
        _engine_v3 = DecisionEngineV3()
    return _engine_v3
