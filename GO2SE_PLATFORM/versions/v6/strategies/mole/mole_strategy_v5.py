#!/usr/bin/env python3
"""
🐹 Mole V5 - CoinGecko真实异动扫描版
"""

import json
import requests
from datetime import datetime
from typing import Dict, List, Optional

COINGECKO_API = "https://api.coingecko.com/api/v3"

def get_coingecko_data():
    try:
        r = requests.get(
            f"{COINGECKO_API}/coins/markets",
            params={"vs_currency": "usd", "order": "market_cap_desc", "per_page": 50, "sparkline": False},
            timeout=10
        )
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return []

class MoleStrategyV5:
    """打地鼠 V5 - 真实异动扫描"""

    def __init__(self, config: dict = None):
        self.config = config or {'use_mi': True}
        self._cache = {}
        self._cache_time = 0

    def _get_cached_data(self) -> List[Dict]:
        now = datetime.now().timestamp()
        if now - self._cache_time < 60:
            return self._cache.get('markets', [])
        data = get_coingecko_data()
        self._cache = {'markets': data}
        self._cache_time = now
        return data

    def scan_all(self) -> List[Dict]:
        markets = self._get_cached_data()
        alerts = []

        for coin in markets[:30]:
            try:
                symbol = coin['symbol'].upper()
                price = coin['current_price']
                change_24h = coin.get('price_change_percentage_24h', 0) or 0
                volume = coin.get('total_volume', 0)
                market_cap = coin.get('market_cap', 0)
                high_24h = coin.get('high_24h', 0)
                low_24h = coin.get('low_24h', 0)

                # 异动评分
                alert_score = 0.0
                signals = []

                # 1. 价格变动
                if abs(change_24h) >= 5:
                    alert_score += 30
                    signals.append(f'big_move_{change_24h:+.1f}%')
                elif abs(change_24h) >= 3:
                    alert_score += 20
                    signals.append(f'moderate_move_{change_24h:+.1f}%')
                elif abs(change_24h) >= 1:
                    alert_score += 10
                    signals.append(f'small_move_{change_24h:+.1f}%')

                # 2. 成交量异动 (vs market cap)
                vol_ratio = volume / market_cap if market_cap else 0
                if vol_ratio > 0.1:
                    alert_score += 25
                    signals.append(f'vol_spike_{vol_ratio:.2f}')
                elif vol_ratio > 0.05:
                    alert_score += 15
                    signals.append(f'vol_up_{vol_ratio:.2f}')

                # 3. 波动范围
                if high_24h and low_24h and low_24h > 0:
                    range_pct = (high_24h - low_24h) / low_24h * 100
                    if range_pct >= 10:
                        alert_score += 20
                        signals.append(f'wide_range_{range_pct:.1f}%')
                    elif range_pct >= 5:
                        alert_score += 10
                        signals.append(f'moderate_range_{range_pct:.1f}%')

                # 4. 突破检测
                if price >= high_24h * 0.98:
                    alert_score += 25
                    signals.append('near_high')
                if price <= low_24h * 1.02:
                    alert_score += 20
                    signals.append('near_low')

                if alert_score < 20:
                    continue

                # 方向
                if change_24h > 3:
                    direction = 'long'
                    rec = 'STRONG_ALERT_LONG' if alert_score >= 50 else 'ALERT_LONG'
                elif change_24h < -3:
                    direction = 'short'
                    rec = 'STRONG_ALERT_SHORT' if alert_score >= 50 else 'ALERT_SHORT'
                else:
                    direction = 'neutral'
                    rec = 'WATCH'

                atr = price * 0.03
                sl = round(price - atr * 2.5 if direction == 'long' else price + atr * 2.5, 2)
                tp = round(price + atr * 5 if direction == 'long' else price - atr * 5, 2)

                alerts.append({
                    'symbol': symbol,
                    'name': coin.get('name', ''),
                    'price': price,
                    'change_24h': round(change_24h, 2),
                    'volume_24h': volume,
                    'alert_score': round(min(alert_score, 100), 1),
                    'direction': direction,
                    'recommendation': rec,
                    'signals': signals,
                    'high_24h': high_24h,
                    'low_24h': low_24h,
                    'stop_loss': sl,
                    'take_profit': tp,
                    'source': 'coingecko_live',
                })
            except:
                continue

        return sorted(alerts, key=lambda x: x['alert_score'], reverse=True)

_mole_v5 = None
def get_mole_v5_strategy():
    global _mole_v5
    if _mole_v5 is None:
        _mole_v5 = MoleStrategyV5()
    return _mole_v5
