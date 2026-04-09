#!/usr/bin/env python3
"""
全市场蛛网扫描器 v2 - 整合多数据源
"""

import requests
import time
from typing import Dict, List
from dataclasses import dataclass, asdict

@dataclass
class AnomalyAlert:
    symbol: str
    source: str
    alert_type: str
    severity: str
    value: float
    metadata: Dict

class SpiderScanner:
    """全市场蛛网扫描器"""
    
    def __init__(self):
        self.thresholds = {
            'price_change_24h': 10.0,
            'price_change_1h': 5.0,
        }
    
    def scan_binance(self) -> Dict:
        """Binance: 655 USDT交易对"""
        url = 'https://api.binance.com/api/v3/ticker/24hr'
        r = requests.get(url, timeout=10)
        data = r.json()
        
        usdt_pairs = [t for t in data if t['symbol'].endswith('USDT')]
        
        alerts = []
        for t in usdt_pairs:
            change = float(t.get('priceChangePercent', 0))
            if abs(change) > self.thresholds['price_change_24h']:
                alerts.append(asdict(AnomalyAlert(
                    symbol=t['symbol'], source='binance',
                    alert_type='price_surge' if change > 0 else 'price_drop',
                    severity='critical' if abs(change) > 20 else 'high',
                    value=change,
                    metadata={'price': t['lastPrice'], 'volume': t['quoteVolume']}
                )))
        
        by_change = sorted(usdt_pairs, key=lambda x: float(x.get('priceChangePercent', 0)), reverse=True)
        
        return {
            'source': 'binance', 'total': len(usdt_pairs),
            'alerts': alerts, 'alert_count': len(alerts),
            'top_gainers': [{'s': t['symbol'], 'c': t['priceChangePercent'], 'p': t['lastPrice']} for t in by_change[:5]],
            'top_losers': [{'s': t['symbol'], 'c': t['priceChangePercent'], 'p': t['lastPrice']} for t in sorted(usdt_pairs, key=lambda x: float(x.get('priceChangePercent', 0)))[:5]]
        }
    
    def scan_bybit(self) -> Dict:
        """Bybit: 全交易对"""
        url = 'https://api.bybit.com/v5/market/tickers?category=spot'
        r = requests.get(url, timeout=10)
        data = r.json()
        
        if data.get('retCode') != 0:
            return {'error': 'API error'}
        
        pairs = data.get('result', {}).get('list', [])
        usdt_pairs = [p for p in pairs if p.get('symbol', '').endswith('USDT')]
        
        alerts = []
        for p in usdt_pairs:
            change = float(p.get('price24hPcnt', 0)) * 100
            if abs(change) > self.thresholds['price_change_24h']:
                alerts.append({
                    'symbol': p['symbol'], 'change': change,
                    'price': p.get('lastPrice')
                })
        
        return {
            'source': 'bybit', 'total': len(usdt_pairs),
            'alerts': alerts, 'alert_count': len(alerts)
        }
    
    def scan_okx(self) -> Dict:
        """OKX: 交易对"""
        url = 'https://www.okx.com/api/v5/market/tickers?instType=SPOT'
        r = requests.get(url, timeout=10)
        data = r.json()
        
        if data.get('code') != '0':
            return {'error': 'API error'}
        
        pairs = data.get('data', [])
        usdt_pairs = [p for p in pairs if p.get('instId', '').endswith('-USDT')]
        
        alerts = []
        for p in usdt_pairs:
            change = float(p.get('sod_utc_0', 0))
            if abs(change) > self.thresholds['price_change_24h']:
                alerts.append({
                    'symbol': p['instId'], 'change': change,
                    'price': p.get('last')
                })
        
        return {
            'source': 'okx', 'total': len(usdt_pairs),
            'alerts': alerts, 'alert_count': len(alerts)
        }
    
    def scan_dexscreener(self) -> Dict:
        """DexScreener: 获取热门代币"""
        # 热门代币
        url = 'https://api.dexscreener.com/token-tracker/latest'
        
        try:
            r = requests.get(url, timeout=10)
            if r.status_code != 200:
                return {'error': 'API error', 'total': 0}
            
            data = r.json()
            tokens = data.get('tokens', [])
            
            alerts = []
            for t in tokens[:100]:
                change = t.get('priceChange', {})
                h1 = float(change.get('h1', 0))
                
                if abs(h1) > self.thresholds['price_change_1h']:
                    alerts.append({
                        'symbol': t.get('tokenAddress', '')[:10] + '...',
                        'chain': t.get('chain'),
                        'change_1h': h1,
                        'price': t.get('price'),
                        'liquidity': t.get('liquidity', {}).get('usd')
                    })
            
            return {
                'source': 'dexscreener',
                'total': len(tokens),
                'alerts': alerts,
                'alert_count': len(alerts)
            }
        except Exception as e:
            return {'error': str(e), 'total': 0}
    
    def scan_defillama(self) -> Dict:
        """DeFiLlama: 449链TVL"""
        url = 'https://api.llama.fi/chains'
        r = requests.get(url, timeout=10)
        chains = r.json()
        
        sorted_chains = sorted(chains, key=lambda x: x.get('tvl', 0), reverse=True)
        
        alerts = []
        for c in sorted_chains[:20]:
            change = float(c.get('change_1d', 0))
            if abs(change) > 5:
                alerts.append({
                    'chain': c.get('name'),
                    'tvl': c.get('tvl'),
                    'change_1d': change
                })
        
        return {
            'source': 'defillama',
            'total_chains': len(chains),
            'top_chains': [{'n': c['name'], 'tvl': round(c['tvl']/1e9, 2), 'c': c.get('change_1d', 0)} for c in sorted_chains[:10]],
            'alerts': alerts,
            'alert_count': len(alerts)
        }
    
    def full_scan(self) -> Dict:
        """完整扫描"""
        print("\n🕸️ 全市场蛛网扫描")
        print("="*50)
        
        result = {'sources': {}, 'timestamp': int(time.time())}
        total_pairs = 0
        total_alerts = 0
        
        # 1. Binance
        print("📡 Binance...")
        b = self.scan_binance()
        result['sources']['binance'] = b
        total_pairs += b.get('total', 0)
        total_alerts += b.get('alert_count', 0)
        print(f"   ✅ {b.get('total', 0)} 对, {b.get('alert_count', 0)} 异常")
        
        # 2. Bybit
        print("📡 Bybit...")
        by = self.scan_bybit()
        result['sources']['bybit'] = by
        total_pairs += by.get('total', 0)
        total_alerts += by.get('alert_count', 0)
        print(f"   ✅ {by.get('total', 0)} 对, {by.get('alert_count', 0)} 异常")
        
        # 3. OKX
        print("📡 OKX...")
        okx = self.scan_okx()
        result['sources']['okx'] = okx
        total_pairs += okx.get('total', 0)
        total_alerts += okx.get('alert_count', 0)
        print(f"   ✅ {okx.get('total', 0)} 对, {okx.get('alert_count', 0)} 异常")
        
        # 4. DexScreener
        print("📡 DexScreener...")
        dex = self.scan_dexscreener()
        result['sources']['dexscreener'] = dex
        total_pairs += dex.get('total', 0)
        total_alerts += dex.get('alert_count', 0)
        print(f"   ✅ {dex.get('total', 0)} 代币, {dex.get('alert_count', 0)} 异常")
        
        # 5. DeFiLlama
        print("📡 DeFiLlama...")
        defi = self.scan_defillama()
        result['sources']['defillama'] = defi
        total_alerts += defi.get('alert_count', 0)
        print(f"   ✅ {defi.get('total_chains', 0)} 链, {defi.get('alert_count', 0)} 异常")
        
        result['summary'] = {'total_pairs': total_pairs, 'total_alerts': total_alerts}
        
        print("="*50)
        print(f"📊 总计: {total_pairs:,} 交易对, {total_alerts} 异常")
        
        return result

if __name__ == '__main__':
    scanner = SpiderScanner()
    result = scanner.full_scan()
