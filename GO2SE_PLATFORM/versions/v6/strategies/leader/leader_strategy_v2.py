#!/usr/bin/env python3
"""
👑 跟大歌策略 V2 - 做市协作
========================================
网络限制处理: Binance不可用时使用本地后端数据
"""

import json
import urllib.request
from datetime import datetime
from typing import Dict, List, Optional

def get_backend_market_data():
    try:
        with urllib.request.urlopen('http://localhost:8000/api/v7/market/summary', timeout=2) as resp:
            return json.loads(resp.read()).get('data', {})
    except:
        return {}

class LeaderStrategyV2:
    """跟大歌 V2 - 做市协作"""

    PAIRS = ['BTC/USDT','ETH/USDT','SOL/USDT','BNB/USDT','XRP/USDT']

    def __init__(self, config: dict = None):
        self.config = config or self._default_config()
        self._backend_cache = {}
        self._backend_cache_time = 0

    def _default_config(self) -> dict:
        return {'base_position': 0.08, 'max_position': 0.25}

    def _get_backend_data_cached(self) -> Dict:
        now = datetime.now().timestamp()
        if now - self._backend_cache_time < 5:
            return self._backend_cache
        data = get_backend_market_data()
        self._backend_cache = data
        self._backend_cache_time = now
        return data

    def analyze_all(self) -> List[Dict]:
        results = []
        backend_data = self._get_backend_data_cached()
        gainers = {g['symbol'].replace('/USDT',''): g['change'] for g in backend_data.get('top_gainers', [])}
        
        for pair in self.PAIRS:
            symbol = pair.replace('/USDT', '')
            change = gainers.get(symbol, 0)
            score = 50 + change * 5
            
            results.append({
                'symbol': symbol,
                'price': 0,
                'spread': 0.05,
                'depth_ratio': 1.0 + change / 10,
                'bid_depth_usd': 1e7,
                'ask_depth_usd': 1e7,
                'whales': {'buy_walls': 0, 'sell_walls': 0, 'net_whale_pressure': 0},
                'support': 0,
                'resistance': 0,
                'bid_flow': change / 100,
                'score': max(0, min(100, score)),
                'direction': 'LONG' if change > 0 else 'NEUTRAL',
                'signals': [f'change_{change:.1f}%'],
                'recommendation': 'LONG' if change > 2 else 'HOLD',
                'source': 'backend_fallback',
            })
        
        return sorted(results, key=lambda x: x['score'], reverse=True)

_leader_v2 = None
def get_leader_v2_strategy():
    global _leader_v2
    if _leader_v2 is None:
        _leader_v2 = LeaderStrategyV2()
    return _leader_v2
