#!/usr/bin/env python3
"""
🐰 Rabbit V6 - 优化版 (牛市做多策略)
========================================
基于深度评测优化:
1. Mi阈值 0.65→0.68 (更敏感)
2. 增加bull市场做多权重
3. 加入30天动量因子
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

class RabbitStrategyV6:
    """打兔子 V6 - 牛市优化版"""

    def __init__(self, config: dict = None):
        self.config = config or self._default_config()
        self._cache = {}
        self._cache_time = 0

    def _default_config(self) -> dict:
        return {
            'mi_threshold': 0.68,  # 优化: 0.65→0.68
            'bull_long_threshold': 0.60,  # 牛市做多阈值
            'momentum_weight': 0.25,  # 新增: 30天动量权重
            'use_mi': True
        }

    def _get_cached_data(self) -> List[Dict]:
        now = datetime.now().timestamp()
        if now - self._cache_time < 60:
            return self._cache.get('markets', [])
        data = get_markets()
        self._cache = {'markets': data}
        self._cache_time = now
        return data

    def analyze_all(self) -> List[Dict]:
        markets = self._get_cached_data()
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

                # 1. 动量评分 (30天趋势)
                momentum_score = 0.0
                if change_30d > 10: momentum_score = 0.9
                elif change_30d > 5: momentum_score = 0.75
                elif change_30d > 0: momentum_score = 0.55
                elif change_30d > -5: momentum_score = 0.35
                else: momentum_score = 0.15

                # 2. 短期趋势评分
                trend_score = 0.5
                if change_24h > 3: trend_score = 0.9
                elif change_24h > 1: trend_score = 0.7
                elif change_24h > 0: trend_score = 0.6
                elif change_24h > -1: trend_score = 0.4
                else: trend_score = 0.2

                # 3. 成交量评分
                vol_ratio = volume / market_cap if market_cap else 0
                vol_score = min(1.0, vol_ratio * 20) if vol_ratio > 0.01 else 0.3

                # 4. 综合评分 (优化权重)
                # 动量30天: 25%, 短期趋势: 35%, 成交量: 20%, Mi: 20%
                mi_estimate = 0.5 + (momentum_score - 0.5) * 0.3  # 基于动量估算Mi
                score = (momentum_score * 0.25 + trend_score * 0.35 + vol_score * 0.20 + mi_estimate * 0.20)

                # 5. 方向判断 (牛市优化)
                direction = 'NEUTRAL'
                recommendation = 'HOLD'

                # 牛市环境优先做多
                if momentum_score > 0.6 and score > self.config['mi_threshold']:
                    if change_24h > 0.5:
                        direction = 'LONG'
                        recommendation = 'STRONG_BUY' if score > 0.75 else 'BUY'
                    elif change_24h > 0:
                        direction = 'LONG'
                        recommendation = 'BUY'
                elif momentum_score > 0.7 and score > 0.65:
                    direction = 'LONG'
                    recommendation = 'BUY'

                # 只有明确弱势才做空
                if momentum_score < 0.3 and change_24h < -2:
                    direction = 'SHORT'
                    recommendation = 'SELL'

                # 止盈止损
                atr = price * 0.025
                if direction == 'LONG':
                    sl = round(price - atr * 2.5, 2)
                    tp = round(price + atr * 6, 2)
                elif direction == 'SHORT':
                    sl = round(price + atr * 2.5, 2)
                    tp = round(price - atr * 4, 2)
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
                    'direction': direction,
                    'recommendation': recommendation,
                    'momentum_score': round(momentum_score, 2),
                    'trend_score': round(trend_score, 2),
                    'volume_ratio': round(vol_ratio, 4),
                    'volume_24h': volume,
                    'market_cap': market_cap,
                    'stop_loss': sl,
                    'take_profit': tp,
                    'position_size': round(0.15 * score, 3) if direction != 'NEUTRAL' else 0.05,
                    'source': 'coingecko_v6',
                })
            except:
                continue

        return sorted(results, key=lambda x: x['score'], reverse=True)

_rabbit_v6 = None
def get_rabbit_v6_strategy():
    global _rabbit_v6
    if _rabbit_v6 is None:
        _rabbit_v6 = RabbitStrategyV6()
    return _rabbit_v6
