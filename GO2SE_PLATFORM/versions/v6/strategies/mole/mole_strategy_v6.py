#!/usr/bin/env python3
"""
🐹 Mole V6 - 优化版 (牛市只做多)
========================================
基于深度评测优化:
1. 只做多方向 (牛市环境)
2. 触发阈值降低到score>15
3. 增加成交量权重
"""

import json
import requests
from datetime import datetime
from typing import Dict, List, Optional

COINGECKO_API = "https://api.coingecko.com/api/v3"

def get_markets():
    try:
        r = requests.get(
            f"{COINGECKO_API}/coins/markets",
            params={"vs_currency": "usd", "order": "market_cap_desc", "per_page": 30, "sparkline": False, "price_change_percentage": "24h,7d,30d"},
            timeout=10
        )
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return []

class MoleStrategyV6:
    """打地鼠 V6 - 牛市只做多版"""

    def __init__(self, config: dict = None):
        self.config = config or {'min_alert_score': 15}  # 降低阈值

    def scan_all(self) -> List[Dict]:
        markets = get_markets()
        alerts = []

        for coin in markets[:30]:
            try:
                symbol = coin['symbol'].upper()
                price = coin['current_price']
                change_24h = coin.get('price_change_percentage_24h', 0) or 0
                change_7d = coin.get('price_change_percentage_7d_in_currency', 0) or 0
                volume = coin.get('total_volume', 0)
                market_cap = coin.get('market_cap', 0)
                high_24h = coin.get('high_24h', price)
                low_24h = coin.get('low_24h', price)

                alert_score = 0.0
                signals = []

                # 1. 价格变动 (牛市只做多，正向变动)
                if change_24h >= 5:
                    alert_score += 35
                    signals.append(f'big_up_{change_24h:+.1f}%')
                elif change_24h >= 3:
                    alert_score += 25
                    signals.append(f'moderate_up_{change_24h:+.1f}%')
                elif change_24h >= 1.5:
                    alert_score += 15
                    signals.append(f'small_up_{change_24h:+.1f}%')

                # 2. 7天趋势 (牛市确认)
                if change_7d > 10:
                    alert_score += 25
                    signals.append(f'strong_week_{change_7d:+.1f}%')
                elif change_7d > 5:
                    alert_score += 15
                    signals.append(f'week_up_{change_7d:+.1f}%')

                # 3. 成交量异动 (提高权重)
                vol_ratio = volume / market_cap if market_cap else 0
                if vol_ratio > 0.15:
                    alert_score += 30
                    signals.append(f'vol_surge_{vol_ratio:.2f}')
                elif vol_ratio > 0.08:
                    alert_score += 20
                    signals.append(f'vol_up_{vol_ratio:.2f}')
                elif vol_ratio > 0.05:
                    alert_score += 10
                    signals.append(f'vol_active_{vol_ratio:.2f}')

                # 4. 波动范围 (上涨中突破)
                if high_24h and low_24h and low_24h > 0:
                    range_pct = (high_24h - low_24h) / low_24h * 100
                    if change_24h > 0 and range_pct >= 8:
                        alert_score += 20
                        signals.append(f'breakout_range_{range_pct:.1f}%')
                    elif range_pct >= 12:
                        alert_score += 15
                        signals.append(f'wide_range_{range_pct:.1f}%')

                # 5. 接近高点 (强势确认)
                if price >= high_24h * 0.98 and change_24h > 0:
                    alert_score += 25
                    signals.append('near_high_confirm')
                elif price >= high_24h * 0.95:
                    alert_score += 10
                    signals.append('near_high')

                # 低于阈值跳过
                if alert_score < 15:
                    continue

                # 方向判断 (牛市只做多!)
                direction = 'long'
                if change_24h >= 5:
                    recommendation = 'STRONG_ALERT_LONG'
                else:
                    recommendation = 'ALERT_LONG'

                atr = price * 0.03
                sl = round(price - atr * 2.5, 2)
                tp = round(price + atr * 5, 2)

                alerts.append({
                    'symbol': symbol,
                    'name': coin.get('name', ''),
                    'price': price,
                    'change_24h': round(change_24h, 2),
                    'change_7d': round(change_7d, 2),
                    'volume_24h': volume,
                    'alert_score': round(min(alert_score, 100), 1),
                    'direction': direction,
                    'recommendation': recommendation,
                    'signals': signals,
                    'high_24h': high_24h,
                    'low_24h': low_24h,
                    'stop_loss': sl,
                    'take_profit': tp,
                    'position_size': round(min(0.20, 0.10 + alert_score/500), 3),
                    'source': 'coingecko_v6',
                })
            except:
                continue

        return sorted(alerts, key=lambda x: x['alert_score'], reverse=True)

_mole_v6 = None
def get_mole_v6_strategy():
    global _mole_v6
    if _mole_v6 is None:
        _mole_v6 = MoleStrategyV6()
    return _mole_v6
