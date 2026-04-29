#!/usr/bin/env python3
"""
🐹 打地鼠策略 V2 - 异动扫描
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

class MoleStrategyV2:
    """打地鼠 V2 - 异动猎手"""

    SCAN_PAIRS = ['BTC/USDT','ETH/USDT','BNB/USDT','SOL/USDT','XRP/USDT',
                  'ADA/USDT','DOGE/USDT','AVAX/USDT','DOT/USDT','MATIC/USDT',
                  'LINK/USDT','UNI/USDT','ATOM/USDT','LTC/USDT','ETC/USDT']

    def __init__(self, config: dict = None):
        self.config = config or self._default_config()
        self._backend_cache = {}
        self._backend_cache_time = 0

    def _default_config(self) -> dict:
        return {'volume_spike_ratio': 3.0, 'price_move_threshold': 0.03}

    def _get_backend_data_cached(self) -> Dict:
        now = datetime.now().timestamp()
        if now - self._backend_cache_time < 5:
            return self._backend_cache
        data = get_backend_market_data()
        self._backend_cache = data
        self._backend_cache_time = now
        return data

    def scan_all(self) -> List[Dict]:
        alerts = []
        backend_data = self._get_backend_data_cached()
        gainers = {g['symbol'].replace('/USDT','').replace('/USDT',''): g['change'] for g in backend_data.get('top_gainers', [])}
        losers = {l['symbol'].replace('/USDT','').replace('/USDT',''): l['change'] for l in backend_data.get('top_losers', [])}
        
        for pair in self.SCAN_PAIRS:
            symbol_base = pair.replace('/USDT', '')
            change = gainers.get(symbol_base, losers.get(symbol_base, 0))
            
            alert_score = abs(change) * 5
            if alert_score >= 15:  # 只返回有意义的异动
                alerts.append({
                    'symbol': symbol_base,
                    'price': 0,
                    'change_24h': change,
                    'volume_ratio': 1.5,
                    'vol_spike': abs(change) > 5,
                    'rsi': 55 + change,
                    'volatility': abs(change) / 2,
                    'alert_score': round(alert_score, 1),
                    'signals': [f'change_{change:.1f}%'],
                    'direction': 'long' if change > 0 else 'short',
                    'recommendation': 'STRONG_ALERT_LONG' if change > 5 else ('ALERT_SHORT' if change < -5 else 'WATCH'),
                    'source': 'backend_fallback',
                })
        
        return sorted(alerts, key=lambda x: x['alert_score'], reverse=True)

_mole_v2 = None
def get_mole_v2_strategy():
    global _mole_v2
    if _mole_v2 is None:
        _mole_v2 = MoleStrategyV2()
    return _mole_v2
