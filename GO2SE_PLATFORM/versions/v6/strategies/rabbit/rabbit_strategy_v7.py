#!/usr/bin/env python3
"""
🐰 Rabbit V7 - 多空自主切换 + 杠杆版
========================================
功能:
1. 熊市做空机制
2. 多空自主切换 (基于市场环境)
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

class RabbitStrategyV7:
    """打兔子 V7 - 多空切换 + 杠杆版"""

    def __init__(self, config: dict = None):
        self.config = config or {
            'leverage': 2.0,  # 默认2倍杠杆
            'max_leverage': 5.0,
            'auto_switch': True,
            'mi_threshold_long': 0.65,
            'mi_threshold_short': 0.45,
        }

    def _get_cached_data(self) -> List[Dict]:
        now = datetime.now().timestamp()
        if now - getattr(self, '_cache_time', 0) < 60:
            return self._cache.get('markets', [])
        data = get_markets()
        self._cache = {'markets': data}
        self._cache_time = now
        return data

    def _get_market_regime(self, markets: List[Dict]) -> Dict:
        """判断市场环境"""
        btc = next((m for m in markets if m['symbol'] == 'bitcoin'), None)
        eth = next((m for m in markets if m['symbol'] == 'ethereum'), None)
        
        if not btc or not eth:
            return {'regime': 'neutral', 'leverage': 1.5}
        
        btc_7d = btc.get('price_change_percentage_7d_in_currency', 0) or 0
        eth_7d = eth.get('price_change_percentage_7d_in_currency', 0) or 0
        avg_change = (btc_7d + eth_7d) / 2
        
        if avg_change > 5:
            return {'regime': 'bull', 'leverage': 2.5, 'reason': '强势上涨'}
        elif avg_change > 2:
            return {'regime': 'bull', 'leverage': 2.0, 'reason': '温和上涨'}
        elif avg_change < -5:
            return {'regime': 'bear', 'leverage': 3.0, 'reason': '强势下跌'}
        elif avg_change < -2:
            return {'regime': 'bear', 'leverage': 2.0, 'reason': '温和下跌'}
        else:
            return {'regime': 'neutral', 'leverage': 1.5, 'reason': '震荡市'}

    def analyze_all(self) -> List[Dict]:
        markets = self._get_cached_data()
        regime_info = self._get_market_regime(markets)
        regime = regime_info['regime']
        leverage = regime_info['leverage']
        
        results = []
        for coin in markets[:20]:
            try:
                symbol = coin['symbol'].upper()
                price = coin['current_price']
                change_24h = coin.get('price_change_percentage_24h', 0) or 0
                change_7d = coin.get('price_change_percentage_7d_in_currency', 0) or 0
                change_30d = coin.get('price_change_percentage_30d_in_currency', 0) or 0
                volume = coin.get('total_volume', 0)
                market_cap = coin.get('market_cap', 0)

                # 动量评分
                momentum = 0.5
                if change_30d > 15: momentum = 0.9
                elif change_30d > 8: momentum = 0.75
                elif change_30d > 3: momentum = 0.6
                elif change_30d > 0: momentum = 0.5
                elif change_30d > -5: momentum = 0.35
                else: momentum = 0.15

                # 短期趋势
                trend = 0.5
                if change_24h > 3: trend = 0.85
                elif change_24h > 1: trend = 0.65
                elif change_24h > 0: trend = 0.55
                elif change_24h > -2: trend = 0.40
                else: trend = 0.20

                vol_ratio = volume / market_cap if market_cap else 0.02
                vol_score = min(1.0, vol_ratio * 15)

                # Mi估算
                mi = momentum * 0.6 + trend * 0.4

                # 综合评分
                score = mi * 0.7 + vol_score * 0.3

                # 多空方向判断 (自主切换!)
                direction = 'NEUTRAL'
                recommendation = 'HOLD'
                position_type = 'spot'
                effective_leverage = 1.0

                if regime == 'bull':
                    # 牛市做多
                    if score > self.config['mi_threshold_long'] and change_24h > 0:
                        direction = 'LONG'
                        position_type = 'long'
                        effective_leverage = leverage
                        recommendation = 'STRONG_BUY' if score > 0.75 else 'BUY'
                elif regime == 'bear':
                    # 熊市做空
                    if score < self.config['mi_threshold_short'] and change_24h < 0:
                        direction = 'SHORT'
                        position_type = 'short'
                        effective_leverage = leverage
                        recommendation = 'STRONG_SELL' if score < 0.30 else 'SELL'
                    elif mi < 0.40 and change_30d < -5:
                        # 强势下跌市，做空
                        direction = 'SHORT'
                        position_type = 'short'
                        effective_leverage = leverage
                        recommendation = 'STRONG_SELL'
                else:
                    # 震荡市，轻仓
                    if score > 0.72:
                        direction = 'LONG'
                        position_type = 'long'
                        effective_leverage = 1.0
                        recommendation = 'BUY'
                    elif score < 0.35:
                        direction = 'SHORT'
                        position_type = 'short'
                        effective_leverage = 1.5
                        recommendation = 'SELL'

                # 止盈止损 (杠杆调整)
                atr = price * 0.025
                if direction == 'LONG':
                    sl = round(price - atr * 2 / effective_leverage, 2)
                    tp = round(price + atr * 6 * effective_leverage, 2)
                elif direction == 'SHORT':
                    sl = round(price + atr * 2 / effective_leverage, 2)
                    tp = round(price - atr * 5 * effective_leverage, 2)
                else:
                    sl = round(price - atr * 3, 2)
                    tp = round(price + atr * 3, 2)

                results.append({
                    'symbol': symbol,
                    'name': coin.get('name', ''),
                    'price': price,
                    'change_24h': round(change_24h, 2),
                    'change_7d': round(change_7d, 2),
                    'change_30d': round(change_30d, 2),
                    'score': round(score, 3),
                    'mi': round(mi, 3),
                    'direction': direction,
                    'position_type': position_type,
                    'recommendation': recommendation,
                    'leverage': effective_leverage,
                    'regime': regime,
                    'regime_reason': regime_info.get('reason', ''),
                    'stop_loss': sl,
                    'take_profit': tp,
                    'position_size': round(min(0.25, 0.15 * score * effective_leverage), 3) if direction != 'NEUTRAL' else 0.05,
                    'source': 'coingecko_v7',
                })
            except:
                continue

        return sorted(results, key=lambda x: x['score'], reverse=True)

_rabbit_v7 = None
def get_rabbit_v7_strategy():
    global _rabbit_v7
    if _rabbit_v7 is None:
        _rabbit_v7 = RabbitStrategyV7()
    return _rabbit_v7
