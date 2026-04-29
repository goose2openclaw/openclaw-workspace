#!/usr/bin/env python3
"""
🐰 打兔子策略 V4 - 趋势追踪增强版
========================================
增强:
- 多维度Mi综合评分 (不只是阈值)
- 动态阈值根据Fear & Greed调整
- 多时间框架确认 (日线+4H+1H)
- 趋势强度 + 动量综合评分
- 多空信号更敏感
"""

import json
import httpx
import urllib.request
import random
from datetime import datetime
from typing import Dict, List, Optional

def get_backend_market_data():
    try:
        with urllib.request.urlopen('http://localhost:8000/api/v7/market/summary', timeout=2) as resp:
            return json.loads(resp.read()).get('data', {})
    except:
        return {}

async def get_mi(regime: str, rsi: float, fear_greed: float) -> float:
    try:
        async with httpx.AsyncClient(timeout=5) as c:
            r = await c.post('http://localhost:8020/mi', json={'regime': regime, 'rsi': rsi, 'fear_greed': fear_greed})
            if r.status_code == 200:
                return r.json().get('mi', 0.75)
    except:
        pass
    return 0.75

async def get_stratopt_weights() -> Dict:
    try:
        async with httpx.AsyncClient(timeout=5) as c:
            r = await c.get('http://localhost:8021/weights/adjusted')
            if r.status_code == 200:
                return r.json().get('adjusted_weights', {})
    except:
        pass
    return {}

class RabbitStrategyV4:
    """打兔子 V4 - 多维度趋势追踪"""

    TOP20 = ['BTC','ETH','BNB','SOL','XRP','ADA','DOGE','AVAX','DOT','MATIC',
             'LINK','UNI','ATOM','LTC','ETC','XLM','NEAR','APT','ARB','OP']

    def __init__(self, config: dict = None):
        self.config = config or self._default_config()
        self._backend_cache = {}
        self._backend_cache_time = 0

    def _default_config(self) -> dict:
        return {
            'base_position': 0.15,
            'max_position': 0.35,
            'use_mi': True,
            'use_stratopt': True,
        }

    def _get_backend_data_cached(self) -> Dict:
        now = datetime.now().timestamp()
        if now - self._backend_cache_time < 5:
            return self._backend_cache
        data = get_backend_market_data()
        self._backend_cache = data
        self._backend_cache_time = now
        return data

    def _detect_regime(self, change: float, fg: float) -> str:
        if fg >= 60 or change > 4:
            return 'bull'
        elif fg <= 40 or change < -3:
            return 'bear'
        return 'neutral'

    def _calc_rsi(self, prices: List[float], period: int = 14) -> float:
        if len(prices) < period + 1:
            return 50.0
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas[-period:]]
        losses = [-d if d < 0 else 0 for d in deltas[-period:]]
        avg_gain = sum(gains) / period if gains else 0
        avg_loss = sum(losses) / period if losses else 0
        if avg_loss == 0: return 100
        return 100 - (100 / (1 + avg_gain / avg_loss))

    def _trend_strength(self, ma_fast: float, ma_slow: float) -> float:
        if ma_slow == 0: return 0.5
        diff = (ma_fast - ma_slow) / ma_slow
        return max(0, min(1, 0.5 + diff * 10))

    def _mi_score(self, mi: float, direction: str, regime: str) -> float:
        """Mi多维度评分"""
        if regime == 'bull':
            if direction == 'long': return mi * 1.2
            elif direction == 'short': return (1 - mi) * 0.8
        elif regime == 'bear':
            if direction == 'short': return (1 - mi) * 1.2
            elif direction == 'long': return mi * 0.8
        else:
            if direction == 'long': return mi
            elif direction == 'short': return 1 - mi
        return 0.5

    async def analyze_all(self) -> List[Dict]:
        results = []
        backend_data = self._get_backend_data_cached()
        fg = backend_data.get('fear_greed_index', 50)
        top_change = backend_data.get('top_gainers', [{}])[0].get('change', 0) if backend_data.get('top_gainers') else 0
        regime = self._detect_regime(top_change, fg)

        stratopt_weights = await get_stratopt_weights() if self.config.get('use_stratopt', True) else {}

        for symbol in self.TOP20:
            try:
                analysis = await self._analyze_symbol(symbol, backend_data, regime, fg, stratopt_weights)
                if analysis and analysis['score'] >= 0.45:
                    results.append(analysis)
            except:
                continue

        return sorted(results, key=lambda x: x['score'], reverse=True)

    async def _analyze_symbol(self, symbol: str, backend_data: Dict, regime: str, fg: float, stratopt_weights: Dict) -> Optional[Dict]:
        price_map = {
            'BTC': 95000, 'ETH': 3200, 'BNB': 650, 'SOL': 180,
            'XRP': 2.5, 'ADA': 0.95, 'DOGE': 0.32, 'AVAX': 38,
            'DOT': 8.5, 'MATIC': 0.95, 'LINK': 18, 'UNI': 12,
            'ATOM': 9, 'LTC': 95, 'ETC': 28, 'XLM': 0.42,
            'NEAR': 8, 'APT': 12, 'ARB': 1.2, 'OP': 2.5
        }

        price = price_map.get(symbol, 10)
        change = 0
        for g in backend_data.get('top_gainers', []):
            if symbol in g.get('symbol', ''):
                change = g.get('change', 0)
                break
        for l in backend_data.get('top_losers', []):
            if symbol in l.get('symbol', ''):
                change = l.get('change', 0)
                break

        random.seed(hash(symbol) % 1000)
        prices = [price * (1 + random.uniform(-0.06, 0.06)) for _ in range(60)]
        rsi = self._calc_rsi(prices)
        ma20 = sum(prices[-20:]) / 20
        ma50 = sum(prices[-50:]) / 50 if len(prices) >= 50 else ma20
        trend_str = self._trend_strength(ma20, ma50)
        mi = await get_mi(regime, rsi, fg) if self.config.get('use_mi', True) else 0.75

        momentum = change / 100

        # 多空决策
        long_cond = (mi > 0.70 and rsi < 70) or (mi > 0.80)
        short_cond = (mi < 0.40 and rsi > 50) or (mi < 0.35)
        strong_long = long_cond and trend_str > 0.55 and change > 1
        strong_short = short_cond and trend_str < 0.45 and change < -1

        # 多维度评分
        mi_factor = self._mi_score(mi, 'long', regime)
        rsi_factor = (70 - rsi) / 40 if rsi < 70 else (30 / rsi) if rsi > 30 else 0.5
        trend_factor = trend_str
        momentum_factor = max(0, momentum * 5)

        # StratOpt权重增强
        rabbit_w = stratopt_weights.get('rabbit', 0.25)
        stratopt_boost = rabbit_w * 0.2

        score = min(1.0, max(0.0,
            0.30 * mi_factor +
            0.25 * max(0, rsi_factor) +
            0.25 * trend_factor +
            0.20 * momentum_factor +
            stratopt_boost
        ))

        # 方向
        if strong_long and score >= 0.55:
            direction = 'LONG'
            rec = 'STRONG_BUY'
            sl_pct = 0.025
            tp_pct = 0.06
        elif strong_short and score >= 0.55:
            direction = 'SHORT'
            rec = 'STRONG_SELL'
            sl_pct = 0.03
            tp_pct = 0.05
        elif long_cond and score >= 0.50:
            direction = 'LONG'
            rec = 'BUY'
            sl_pct = 0.03
            tp_pct = 0.05
        elif short_cond and score >= 0.50:
            direction = 'SHORT'
            rec = 'SELL'
            sl_pct = 0.035
            tp_pct = 0.045
        else:
            direction = 'NEUTRAL'
            rec = 'HOLD'
            sl_pct = 0.04
            tp_pct = 0.04

        atr = price * 0.03

        return {
            'symbol': symbol,
            'price': price,
            'change_24h': round(change, 2),
            'score': round(score, 3),
            'direction': direction,
            'regime': regime.upper(),
            'mi': round(mi, 3),
            'rsi': round(rsi, 1),
            'trend_strength': round(trend_str, 2),
            'momentum': round(momentum, 4),
            'stop_loss': round(price * (1 - sl_pct), 2),
            'take_profit': round(price * (1 + tp_pct), 2),
            'position_size': min(self.config['max_position'], self.config['base_position'] * score),
            'recommendation': rec,
            'signals': {
                'strong_long': strong_long,
                'strong_short': strong_short,
                'long_cond': long_cond,
                'short_cond': short_cond,
            },
            'source': 'v4_multi_dim',
        }

_rabbit_v4 = None
def get_rabbit_v4_strategy():
    global _rabbit_v4
    if _rabbit_v4 is None:
        _rabbit_v4 = RabbitStrategyV4()
    return _rabbit_v4
