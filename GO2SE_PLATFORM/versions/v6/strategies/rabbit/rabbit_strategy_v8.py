#!/usr/bin/env python3
"""
🐰 Rabbit V8 - 优化版 (阈值0.6, 杠杆3.0x)
==========================================
基于GStack+MiroFish深度评测优化:
1. 信号阈值: 0.55→0.60
2. 杠杆: 2.0→3.0x
3. 多空自主切换
"""

import json
import requests
from datetime import datetime
from typing import Dict, List

BACKEND_API = "http://localhost:8000"

def get_markets():
    try:
        r = requests.get(f"{COINGECKO_API}/coins/markets",
            params={"vs_currency": "usd", "order": "market_cap_desc", "per_page": 30, "sparkline": False, "price_change_percentage": "24h,7d,30d"},
            timeout=10)
        if r.status_code == 200: return r.json()
    except: pass
    return []

class RabbitStrategyV8:
    """打兔子 V8 - 优化版"""

    def __init__(self):
        self.config = {
            'threshold': 0.60,  # 优化: 0.55→0.60
            'leverage': 3.0,      # 优化: 2.0→3.0x
            'auto_switch': True,
        }

    def _get_regime(self, markets):
        btc = next((m for m in markets if m['symbol']=='bitcoin'), None)
        if not btc: return 'neutral', 2.0
        btc_7d = btc.get('price_change_percentage_7d_in_currency', 0) or 0
        if btc_7d > 5: return 'bull', 3.0
        elif btc_7d < -5: return 'bear', 3.0
        return 'neutral', 2.0

    def analyze_all(self) -> List[Dict]:
        markets = get_markets()
        regime, leverage = self._get_regime(markets)
        results = []
        
        for coin in markets[:20]:
            try:
                symbol = coin['symbol'].upper()
                price = coin['current_price']
                ch24 = coin.get('price_change_percentage_24h', 0) or 0
                ch7 = coin.get('price_change_percentage_7d_in_currency', 0) or 0
                ch30 = coin.get('price_change_percentage_30d_in_currency', 0) or 0
                vol = coin.get('total_volume', 0)
                mc = coin.get('market_cap', 0)
                
                # 评分
                momentum = 0.5 + min(0.4, ch30/50)
                trend = 0.5 + min(0.4, ch24/15)
                vol_score = min(1.0, vol/mc/0.05) if mc else 0.3
                score = momentum*0.5 + trend*0.3 + vol_score*0.2
                
                # 方向
                direction = 'NEUTRAL'
                recommendation = 'HOLD'
                eff_lev = 1.0
                
                if regime == 'bull':
                    if score > self.config['threshold'] and ch24 > 0:
                        direction = 'LONG'
                        recommendation = 'STRONG_BUY' if score > 0.75 else 'BUY'
                        eff_lev = leverage
                elif regime == 'bear':
                    if score < 0.40 and ch24 < 0:
                        direction = 'SHORT'
                        recommendation = 'STRONG_SELL'
                        eff_lev = leverage
                    elif score > 0.75:
                        direction = 'LONG'
                        recommendation = 'BEAR_BOUNCE'
                        eff_lev = 1.5
                else:
                    if score > 0.75: direction = 'LONG'; recommendation = 'BUY'; eff_lev = 2.0
                    elif score < 0.35: direction = 'SHORT'; recommendation = 'SELL'; eff_lev = 1.5
                
                atr = price * 0.025
                if direction == 'LONG':
                    sl = round(price - atr*2/eff_lev, 2)
                    tp = round(price + atr*6*eff_lev, 2)
                elif direction == 'SHORT':
                    sl = round(price + atr*2/eff_lev, 2)
                    tp = round(price - atr*5*eff_lev, 2)
                else:
                    sl = round(price - atr*3, 2); tp = round(price + atr*3, 2)
                
                results.append({
                    'symbol': symbol, 'price': price,
                    'change_24h': round(ch24, 2), 'change_7d': round(ch7, 2), 'change_30d': round(ch30, 2),
                    'score': round(score, 3), 'direction': direction,
                    'recommendation': recommendation, 'leverage': eff_lev,
                    'regime': regime, 'stop_loss': sl, 'take_profit': tp,
                    'position_size': round(min(0.25, 0.15*score*eff_lev/3), 3) if direction != 'NEUTRAL' else 0.05,
                    'source': 'coingecko_v8',
                })
            except: continue
        
        return sorted(results, key=lambda x: x['score'], reverse=True)

_rabbit_v8 = None
def get_rabbit_v8_strategy():
    global _rabbit_v8
    if _rabbit_v8 is None: _rabbit_v8 = RabbitStrategyV8()
    return _rabbit_v8
