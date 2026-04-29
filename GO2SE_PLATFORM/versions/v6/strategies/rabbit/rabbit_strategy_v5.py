#!/usr/bin/env python3
"""
🐰 Rabbit V5 - CoinGecko真实市场数据版
========================================
突破网络封锁: 使用CoinGecko API获取真实数据
"""

import json
import requests
import random
from datetime import datetime
from typing import Dict, List, Optional

COINGECKO_API = "https://api.coingecko.com/api/v3"

def get_coingecko_data():
    """获取CoinGecko真实市场数据"""
    try:
        r = requests.get(
            f"{COINGECKO_API}/coins/markets",
            params={"vs_currency": "usd", "order": "market_cap_desc", "per_page": 20, "sparkline": False},
            timeout=10
        )
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return []

def get_ohlcv(symbol: str, days: int = 30):
    """获取OHLCV数据"""
    coin_id = symbol.lower()
    try:
        r = requests.get(
            f"{COINGECKO_API}/coins/{coin_id}/ohlc",
            params={"vs_currency": "usd", "days": days},
            timeout=10
        )
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return []

class RabbitStrategyV5:
    """打兔子 V5 - 真实市场数据"""

    TOP20 = ['bitcoin','ethereum','binancecoin','solana','ripple','cardano','dogecoin',
              'avalanche-2','polkadot','matic-network','chainlink','uniswap','cosmos',
              'litecoin','ethereum-classic','stellar','near','aptos','arbitrum','optimism']

    def __init__(self, config: dict = None):
        self.config = config or self._default_config()
        self._cache = {}
        self._cache_time = 0

    def _default_config(self) -> dict:
        return {'base_position': 0.15, 'max_position': 0.35, 'use_mi': True}

    def _get_cached_data(self) -> List[Dict]:
        now = datetime.now().timestamp()
        if now - self._cache_time < 60:  # 60秒缓存
            return self._cache.get('markets', [])
        data = get_coingecko_data()
        self._cache = {'markets': data}
        self._cache_time = now
        return data

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

    def analyze_all(self) -> List[Dict]:
        """分析所有币种"""
        markets = self._get_cached_data()
        results = []

        for coin in markets[:20]:
            try:
                symbol = coin['symbol'].upper()
                price = coin['current_price']
                change_24h = coin.get('price_change_percentage_24h', 0) or 0
                volume = coin.get('total_volume', 0)
                market_cap = coin.get('market_cap', 0)
                high_24h = coin.get('high_24h', price)
                low_24h = coin.get('low_24h', price)

                # 获取OHLCV历史计算RSI
                ohlcv = get_ohlcv(coin['id'], 30)
                closes = [o[4] for o in ohlcv] if ohlcv else [price]
                rsi = self._calc_rsi(closes)

                # 趋势评分
                change_score = max(0, min(1, (change_24h + 10) / 20))
                volume_score = min(1, volume / 1e9) if volume else 0.5

                # 综合评分
                score = 0.3 * change_score + 0.3 * (1 - abs(rsi - 50) / 50) + 0.4 * volume_score

                # 方向
                if score > 0.65 and change_24h > 1:
                    direction = 'LONG'
                    rec = 'STRONG_BUY' if score > 0.75 else 'BUY'
                elif score < 0.35 and change_24h < -1:
                    direction = 'SHORT'
                    rec = 'STRONG_SELL' if score < 0.25 else 'SELL'
                else:
                    direction = 'NEUTRAL'
                    rec = 'HOLD'

                # 止盈止损
                atr = price * 0.03
                if direction == 'LONG':
                    sl = round(price - atr * 2, 2)
                    tp = round(price + atr * 5, 2)
                elif direction == 'SHORT':
                    sl = round(price + atr * 2, 2)
                    tp = round(price - atr * 5, 2)
                else:
                    sl = round(price - atr * 3, 2)
                    tp = round(price + atr * 3, 2)

                results.append({
                    'symbol': symbol,
                    'name': coin.get('name', ''),
                    'price': price,
                    'change_24h': round(change_24h, 2),
                    'score': round(score, 3),
                    'direction': direction,
                    'recommendation': rec,
                    'rsi': round(rsi, 1),
                    'volume_24h': volume,
                    'market_cap': market_cap,
                    'high_24h': high_24h,
                    'low_24h': low_24h,
                    'stop_loss': sl,
                    'take_profit': tp,
                    'position_size': min(self.config['max_position'], self.config['base_position'] * score),
                    'source': 'coingecko_live',
                })
            except:
                continue

        return sorted(results, key=lambda x: x['score'], reverse=True)

_rabbit_v5 = None
def get_rabbit_v5_strategy():
    global _rabbit_v5
    if _rabbit_v5 is None:
        _rabbit_v5 = RabbitStrategyV5()
    return _rabbit_v5
