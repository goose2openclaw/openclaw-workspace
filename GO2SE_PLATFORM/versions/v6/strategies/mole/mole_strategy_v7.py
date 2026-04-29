#!/usr/bin/env python3
"""
🐹 Mole V7 - 多空自主切换 + 杠杆版
========================================
功能:
1. 熊市做空机制
2. 多空自主切换
3. 杠杆功能 (1x-5x)
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

class MoleStrategyV7:
    """打地鼠 V7 - 多空切换 + 杠杆版"""

    def __init__(self, config: dict = None):
        self.config = config or {
            'leverage': 2.0,
            'alert_threshold_long': 20,
            'alert_threshold_short': 25,
        }

    def _get_market_regime(self, markets: List[Dict]) -> Dict:
        """判断市场环境"""
        btc = next((m for m in markets if m['symbol'] == 'bitcoin'), None)
        if not btc:
            return {'regime': 'neutral', 'leverage': 1.5}
        
        btc_7d = btc.get('price_change_percentage_7d_in_currency', 0) or 0
        
        if btc_7d > 5:
            return {'regime': 'bull', 'leverage': 2.5}
        elif btc_7d > 2:
            return {'regime': 'bull', 'leverage': 2.0}
        elif btc_7d < -5:
            return {'regime': 'bear', 'leverage': 3.0}
        elif btc_7d < -2:
            return {'regime': 'bear', 'leverage': 2.0}
        else:
            return {'regime': 'neutral', 'leverage': 1.5}

    def scan_all(self) -> List[Dict]:
        markets = get_markets()
        regime_info = self._get_market_regime(markets)
        regime = regime_info['regime']
        leverage = regime_info['leverage']
        
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

                # 上涨异动 (做多信号)
                if change_24h >= 5:
                    alert_score += 35
                    signals.append(f'big_up_{change_24h:+.1f}%')
                elif change_24h >= 3:
                    alert_score += 25
                    signals.append(f'mod_up_{change_24h:+.1f}%')
                elif change_24h >= 1.5:
                    alert_score += 15
                    signals.append(f'small_up_{change_24h:+.1f}%')

                # 下跌异动 (做空信号) - V7新增
                if change_24h <= -5:
                    alert_score += 40
                    signals.append(f'big_down_{change_24h:+.1f}%')
                elif change_24h <= -3:
                    alert_score += 30
                    signals.append(f'mod_down_{change_24h:+.1f}%')
                elif change_24h <= -1.5:
                    alert_score += 15
                    signals.append(f'small_down_{change_24h:+.1f}%')

                # 7天趋势确认
                if change_7d > 10:
                    alert_score += 20
                    signals.append(f'strong_week_up_{change_7d:+.1f}%')
                elif change_7d > 5:
                    alert_score += 10
                    signals.append(f'week_up_{change_7d:+.1f}%')
                elif change_7d < -10:
                    alert_score += 25
                    signals.append(f'strong_week_down_{change_7d:+.1f}%')
                elif change_7d < -5:
                    alert_score += 15
                    signals.append(f'week_down_{change_7d:+.1f}%')

                # 成交量异动
                vol_ratio = volume / market_cap if market_cap else 0.02
                if vol_ratio > 0.12:
                    alert_score += 25
                    signals.append(f'vol_surge_{vol_ratio:.2f}')
                elif vol_ratio > 0.06:
                    alert_score += 15
                    signals.append(f'vol_active_{vol_ratio:.2f}')

                # 波动范围
                if high_24h and low_24h and low_24h > 0:
                    range_pct = (high_24h - low_24h) / low_24h * 100
                    if range_pct >= 8:
                        alert_score += 15
                        signals.append(f'wide_range_{range_pct:.1f}%')

                # 位置确认
                if price >= high_24h * 0.98 and change_24h > 0:
                    alert_score += 20
                    signals.append('near_high_confirm')
                elif price <= low_24h * 1.02 and change_24h < 0:
                    alert_score += 20
                    signals.append('near_low_confirm')

                # 方向判断 (多空自主切换!)
                direction = 'neutral'
                recommendation = 'WATCH'
                position_type = 'none'
                effective_leverage = 1.0

                if regime == 'bull':
                    # 牛市环境: 优先做多
                    if change_24h >= 1.5 and alert_score >= self.config['alert_threshold_long']:
                        direction = 'long'
                        position_type = 'long'
                        effective_leverage = leverage
                        recommendation = 'STRONG_ALERT_LONG' if alert_score >= 50 else 'ALERT_LONG'
                elif regime == 'bear':
                    # 熊市环境: 优先做空
                    if change_24h <= -1.5 and alert_score >= self.config['alert_threshold_short']:
                        direction = 'short'
                        position_type = 'short'
                        effective_leverage = leverage
                        recommendation = 'STRONG_ALERT_SHORT' if alert_score >= 55 else 'ALERT_SHORT'
                    elif change_24h >= 3 and alert_score >= 60:
                        # 反弹信号也可以做多，但要小心
                        direction = 'long'
                        position_type = 'long'
                        effective_leverage = 1.5
                        recommendation = 'BEAR_BOUNTCE_LONG'
                else:
                    # 震荡市: 两边都做，轻仓
                    if change_24h >= 2 and alert_score >= 30:
                        direction = 'long'
                        position_type = 'long'
                        effective_leverage = 1.5
                        recommendation = 'RANGE_LONG'
                    elif change_24h <= -2 and alert_score >= 30:
                        direction = 'short'
                        position_type = 'short'
                        effective_leverage = 1.5
                        recommendation = 'RANGE_SHORT'

                if position_type == 'none':
                    continue

                atr = price * 0.03
                if direction == 'long':
                    sl = round(price - atr * 2.5 / effective_leverage, 2)
                    tp = round(price + atr * 5 * effective_leverage, 2)
                else:
                    sl = round(price + atr * 2.5 / effective_leverage, 2)
                    tp = round(price - atr * 5 * effective_leverage, 2)

                alerts.append({
                    'symbol': symbol,
                    'name': coin.get('name', ''),
                    'price': price,
                    'change_24h': round(change_24h, 2),
                    'change_7d': round(change_7d, 2),
                    'volume_24h': volume,
                    'alert_score': round(min(alert_score, 100), 1),
                    'direction': direction,
                    'position_type': position_type,
                    'recommendation': recommendation,
                    'leverage': effective_leverage,
                    'regime': regime,
                    'signals': signals,
                    'high_24h': high_24h,
                    'low_24h': low_24h,
                    'stop_loss': sl,
                    'take_profit': tp,
                    'position_size': round(min(0.25, 0.12 * alert_score / 30 * effective_leverage), 3),
                    'source': 'coingecko_v7',
                })
            except:
                continue

        return sorted(alerts, key=lambda x: x['alert_score'], reverse=True)

_mole_v7 = None
def get_mole_v7_strategy():
    global _mole_v7
    if _mole_v7 is None:
        _mole_v7 = MoleStrategyV7()
    return _mole_v7
