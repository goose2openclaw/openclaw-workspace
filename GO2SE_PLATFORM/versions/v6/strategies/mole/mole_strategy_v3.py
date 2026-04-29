#!/usr/bin/env python3
"""
🐹 打地鼠策略 V3 - 异动扫描 + 区间感知
========================================
增强:
- MiroFish Mi 区间感知
- 多维度异动检测
- 动态警报评分
- 多空自主切换
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

class MoleStrategyV3:
    """打地鼠 V3 - 异动猎手增强版"""

    SCAN_PAIRS = ['BTC/USDT','ETH/USDT','BNB/USDT','SOL/USDT','XRP/USDT',
                  'ADA/USDT','DOGE/USDT','AVAX/USDT','DOT/USDT','MATIC/USDT',
                  'LINK/USDT','UNI/USDT','ATOM/USDT','LTC/USDT','ETC/USDT']

    REGIME_PARAMS = {
        'bull':  {'vol_spike': 1.5, 'price_move': 0.01, 'rsi_break': 60, 'score_mult': 1.2, 'min_alert': 15},
        'bear':  {'vol_spike': 1.3, 'price_move': 0.008, 'rsi_break': 55, 'score_mult': 1.5, 'min_alert': 15},
        'neutral': {'vol_spike': 1.6, 'price_move': 0.012, 'rsi_break': 58, 'score_mult': 1.0, 'min_alert': 12},
    }

    def __init__(self, config: dict = None):
        self.config = config or self._default_config()
        self._backend_cache = {}
        self._backend_cache_time = 0

    def _default_config(self) -> dict:
        return {'use_mi': True}

    def _get_backend_data_cached(self) -> Dict:
        now = datetime.now().timestamp()
        if now - self._backend_cache_time < 5:
            return self._backend_cache
        data = get_backend_market_data()
        self._backend_cache = data
        self._backend_cache_time = now
        return data

    def _detect_regime(self, change: float, fg: float) -> str:
        if fg >= 65 or change > 3:
            return 'bull'
        elif fg <= 35 or change < -2:
            return 'bear'
        return 'neutral'

    def _calc_volatility(self, prices: List[float]) -> float:
        if len(prices) < 5:
            return 0.03
        mean = sum(prices) / len(prices)
        variance = sum((p - mean) ** 2 for p in prices) / len(prices)
        return (variance ** 0.5) / mean if mean > 0 else 0.03

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

    def _simulate_ohlcv(self, symbol: str, base_price: float, change: float) -> Dict:
        random.seed(hash(symbol) % 1000)
        n = 30
        trend = change / 100 / n  # daily change distributed
        prices = [base_price * (1 + trend * i + random.uniform(-0.02, 0.02)) for i in range(n)]
        volumes = [random.uniform(5e7, 2e9) for _ in range(n)]
        spike_idx = random.randint(5, n-2)
        volumes[spike_idx] *= random.uniform(1.8, 3.0)
        prices[spike_idx] *= random.uniform(1.01, 1.05) if change > 0 else random.uniform(0.95, 0.99)
        return {'closes': prices, 'volumes': volumes, 'spike_idx': spike_idx}

    async def scan_all(self) -> List[Dict]:
        alerts = []
        backend_data = self._get_backend_data_cached()
        fg = backend_data.get('fear_greed_index', 50)
        top_change = backend_data.get('top_gainers', [{}])[0].get('change', 0) if backend_data.get('top_gainers') else 0
        regime = self._detect_regime(top_change, fg)
        params = self.REGIME_PARAMS[regime]

        gainers = {g['symbol'].replace('/USDT',''): g['change'] for g in backend_data.get('top_gainers', [])}
        losers = {l['symbol'].replace('/USDT',''): l['change'] for l in backend_data.get('top_losers', [])}

        for pair in self.SCAN_PAIRS:
            try:
                alert = await self._scan_pair(pair, gainers, losers, regime, params, fg)
                if alert and alert['alert_score'] >= params['min_alert']:
                    alerts.append(alert)
            except:
                continue

        return sorted(alerts, key=lambda x: x['alert_score'], reverse=True)

    async def _scan_pair(self, pair: str, gainers: Dict, losers: Dict, regime: str, params: Dict, fg: float) -> Optional[Dict]:
        symbol = pair.replace('/USDT', '')
        price_map = {
            'BTC': 95000, 'ETH': 3200, 'BNB': 650, 'SOL': 180,
            'XRP': 2.5, 'ADA': 0.95, 'DOGE': 0.32, 'AVAX': 38,
            'DOT': 8.5, 'MATIC': 0.95, 'LINK': 18, 'UNI': 12,
            'ATOM': 9, 'LTC': 95, 'ETC': 28, 'XLM': 0.42,
            'NEAR': 8, 'APT': 12, 'ARB': 1.2, 'OP': 2.5
        }
        base_price = price_map.get(symbol, 10)
        change = gainers.get(symbol, losers.get(symbol, 0))

        ohlcv_data = self._simulate_ohlcv(symbol, base_price, change)
        closes = ohlcv_data['closes']
        volumes = ohlcv_data['volumes']

        volatility = self._calc_volatility(closes)
        rsi = self._calc_rsi(closes)
        avg_vol = sum(volumes[:-3]) / max(1, len(volumes[:-3]))
        current_vol = volumes[-1]
        vol_ratio = current_vol / avg_vol if avg_vol > 0 else 1.0

        alert_score = 0.0
        signals = []
        direction = 'neutral'

        if vol_ratio >= params['vol_spike']:
            vol_score = min((vol_ratio / 5) * 40, 40)
            alert_score += vol_score
            signals.append(f'vol_x{vol_ratio:.1f}')

        price_move = abs(change) / 100
        if price_move >= params['price_move']:
            price_score = min(price_move * 15 * 100, 25)
            alert_score += price_score
            signals.append(f'price_{"+-"if change>0 else ""}{change:.1f}%')

        if rsi >= params['rsi_break'] or rsi <= (100 - params['rsi_break']):
            alert_score += 15
            signals.append(f'rsi_{rsi:.0f}')

        if volatility > 0.03:
            alert_score += 10
            signals.append(f'high_vol_{volatility*100:.1f}%')

        mi = await get_mi(regime, rsi, fg) if self.config.get('use_mi', True) else 0.75

        if regime == 'bull':
            if change > 2 and mi > 0.70:
                direction = 'long'
                alert_score *= params['score_mult']
            elif change < -2 and mi < 0.55:
                direction = 'short'
                alert_score *= params['score_mult']
        elif regime == 'bear':
            if change > 2.5 and mi > 0.75:
                direction = 'long'
                alert_score *= params['score_mult']
            elif change < -1.5 and mi < 0.60:
                direction = 'short'
                alert_score *= params['score_mult']
        else:
            if change > 2:
                direction = 'long'
            elif change < -2:
                direction = 'short'

        mi_boost = abs(mi - 0.5) * 15
        alert_score += mi_boost

        if alert_score < params['min_alert']:
            return None

        if direction == 'long':
            rec = 'STRONG_ALERT_LONG' if alert_score >= 40 else 'ALERT_LONG'
        elif direction == 'short':
            rec = 'STRONG_ALERT_SHORT' if alert_score >= 40 else 'ALERT_SHORT'
        else:
            rec = 'WATCH'

        atr = base_price * volatility
        sl = round(base_price - atr * 3 if direction == 'long' else base_price + atr * 3, 2)
        tp = round(base_price + atr * 5 if direction == 'long' else base_price - atr * 5, 2)

        return {
            'symbol': symbol,
            'price': base_price,
            'change_24h': round(change, 2),
            'volume_ratio': round(vol_ratio, 2),
            'vol_spike': vol_ratio >= params['vol_spike'],
            'rsi': round(rsi, 1),
            'volatility': round(volatility * 100, 2),
            'alert_score': round(min(alert_score, 100), 1),
            'mi': round(mi, 3),
            'regime': regime.upper(),
            'direction': direction,
            'recommendation': rec,
            'stop_loss': sl,
            'take_profit': tp,
            'position_size': min(0.20, 0.08 * (alert_score / 50)),
            'signals': signals,
            'source': 'v3_mi_volatility',
        }

_mole_v3 = None
def get_mole_v3_strategy():
    global _mole_v3
    if _mole_v3 is None:
        _mole_v3 = MoleStrategyV3()
    return _mole_v3
