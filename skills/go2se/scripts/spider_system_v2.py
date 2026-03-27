#!/usr/bin/env python3
"""
全市场蛛网扫描系统 - 极限版
目标: 10000+ 交易对覆盖

轨道1: Binance全量 (3537)
轨道2: 多CEX聚合 (Bybit+OKX+KuCoin+Huobi+Bitfinex)
轨道3: DEX数据 (DexScreener+DeFiLlama)
"""

import requests
import time
import concurrent.futures
from typing import Dict, List
from dataclasses import dataclass, asdict

@dataclass
class ScanResult:
    source: str
    total: int
    alerts: List
    duration: float

# ==================== 轨道1: Binance ====================

class BinanceScanner:
    """Binance全量扫描"""
    def __init__(self):
        self.url = 'https://api.binance.com/api/v3/ticker/24hr'
        self.threshold = 10.0
    
    def scan(self) -> ScanResult:
        start = time.time()
        r = requests.get(self.url, timeout=30)
        data = r.json()
        
        alerts = []
        for t in data:
            change = float(t.get('priceChangePercent', 0))
            if abs(change) > self.threshold and float(t.get('quoteVolume', 0)) > 10000:
                alerts.append({
                    'symbol': t['symbol'],
                    'change': round(change, 2),
                    'price': t['lastPrice'],
                    'volume': round(float(t.get('quoteVolume', 0)), 0)
                })
        
        alerts.sort(key=lambda x: abs(x['change']), reverse=True)
        return ScanResult('binance', len(data), alerts[:20], time.time() - start)

# ==================== 轨道2: 多CEX ====================

class MultiCEXScanner:
    """多CEX聚合"""
    
    def scan_all(self) -> ScanResult:
        start = time.time()
        
        # 交易所配置
        self.exchanges = {
            'bybit': ('https://api.bybit.com/v5/market/tickers?category=spot', self.parse_bybit),
            'okx': ('https://www.okx.com/api/v5/market/tickers?instType=SPOT', self.parse_okx),
            'huobi': ('https://api.huobi.pro/market/tickers', self.parse_huobi),
            'bitfinex': ('https://api-pub.bitfinex.com/v2/tickers?symbols=ALL', self.parse_bitfinex),
        }
        
        all_alerts = []
        total = 0
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(self.scan_one, name, url, parser): name 
                      for name, (url, parser) in self.exchanges.items()}
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    total += result['total']
                    all_alerts.extend(result['alerts'])
                except:
                    pass
        
        all_alerts.sort(key=lambda x: abs(x.get('change', 0)), reverse=True)
        return ScanResult('multi_cex', total, all_alerts[:20], time.time() - start)
    
    def scan_one(self, name: str, url: str, parser) -> Dict:
        r = requests.get(url, timeout=15)
        return parser(r.json())
    
    def parse_bybit(self, data) -> Dict:
        if data.get('retCode') != 0:
            return {'total': 0, 'alerts': []}
        pairs = data['result']['list']
        alerts = []
        for p in pairs:
            change = float(p.get('price24hPcnt', 0)) * 100
            if abs(change) > 10:
                alerts.append({'symbol': p['symbol'], 'change': round(change, 2), 'source': 'bybit'})
        return {'total': len(pairs), 'alerts': alerts}
    
    def parse_okx(self, data) -> Dict:
        if data.get('code') != '0':
            return {'total': 0, 'alerts': []}
        pairs = data['data']
        alerts = []
        for p in pairs:
            change = float(p.get('sod_utc_0', 0))
            if abs(change) > 10:
                alerts.append({'symbol': p['instId'], 'change': round(change, 2), 'source': 'okx'})
        return {'total': len(pairs), 'alerts': alerts}
    
    def parse_huobi(self, data) -> Dict:
        if 'data' not in data:
            return {'total': 0, 'alerts': []}
        pairs = data['data']
        alerts = []
        for p in pairs:
            change = float(p.get('close') or 0) - float(p.get('open') or 0)
            if p.get('open'):
                change = (change / float(p['open'])) * 100
            if abs(change) > 10:
                alerts.append({'symbol': p['symbol'], 'change': round(change, 2), 'source': 'huobi'})
        return {'total': len(pairs), 'alerts': alerts}
    
    def parse_bitfinex(self, data) -> Dict:
        if not isinstance(data, list):
            return {'total': 0, 'alerts': []}
        alerts = []
        count = 0
        for p in data[1:]:  # skip header
            if len(p) > 11:
                symbol = p[0]
                change = p[11]  # CHANGE
                # 过滤异常值 (只保留合理范围)
                if change and -100 < float(change) < 1000:
                    if abs(float(change)) > 10:
                        alerts.append({'symbol': symbol, 'change': round(float(change), 2), 'source': 'bitfinex'})
                count += 1
        return {'total': count, 'alerts': alerts}

# ==================== 轨道3: DEX ====================

class DEXScanner:
    """DEX数据"""
    def scan(self) -> ScanResult:
        start = time.time()
        total = 0
        alerts = []
        
        # DexScreener
        try:
            r = requests.get('https://api.dexscreener.com/token-tracker/latest', timeout=15)
            if r.status_code == 200:
                data = r.json()
                tokens = data.get('tokens', []) or []
                total += len(tokens)
                for t in tokens[:200]:
                    change = t.get('priceChange', {}).get('h1', 0)
                    if abs(float(change)) > 10:
                        alerts.append({
                            'symbol': t.get('tokenAddress', '')[:10],
                            'chain': t.get('chain'),
                            'change': round(float(change), 2),
                            'source': 'dexscreener'
                        })
        except:
            pass
        
        # DeFiLlama
        try:
            r = requests.get('https://api.llama.fi/chains', timeout=10)
            chains = r.json()
            total += len(chains)
        except:
            pass
        
        alerts.sort(key=lambda x: abs(x.get('change', 0)), reverse=True)
        return ScanResult('dex', total, alerts[:20], time.time() - start)

# ==================== 主系统 ====================

class SpiderSystem:
    def __init__(self):
        self.tracks = {
            'binance': BinanceScanner(),
            'cex': MultiCEXScanner(),
            'dex': DEXScanner()
        }
    
    def scan(self) -> Dict:
        print("\n" + "="*60)
        print("🕸️ 全市场蛛网扫描系统 (极限版)")
        print("="*60)
        
        start = time.time()
        results = {}
        
        # 轨道1
        print("\n🚂 轨道1: Binance...")
        r1 = self.tracks['binance'].scan()
        results['binance'] = asdict(r1)
        print(f"   ✅ {r1.total:,} 交易对, {len(r1.alerts)} 异常, {r1.duration:.1f}s")
        
        # 轨道2
        print("\n🚂 轨道2: 多CEX聚合...")
        r2 = self.tracks['cex'].scan_all()
        results['cex'] = asdict(r2)
        print(f"   ✅ {r2.total:,} 交易对, {len(r2.alerts)} 异常, {r2.duration:.1f}s")
        
        # 轨道3
        print("\n🚂 轨道3: DEX数据...")
        r3 = self.tracks['dex'].scan()
        results['dex'] = asdict(r3)
        print(f"   ✅ {r3.total:,} 代币/链, {len(r3.alerts)} 异常, {r3.duration:.1f}s")
        
        # 汇总
        total_pairs = r1.total + r2.total + r3.total
        all_alerts = r1.alerts + r2.alerts + r3.alerts
        all_alerts.sort(key=lambda x: abs(x.get('change', 0)), reverse=True)
        
        results['summary'] = {
            'total_pairs': total_pairs,
            'total_alerts': len(all_alerts),
            'duration': time.time() - start,
            'alerts': all_alerts[:30]
        }
        
        print("\n" + "="*60)
        print(f"📊 总覆盖: {total_pairs:,} 交易对/代币")
        print(f"🚨 异常: {len(all_alerts)}")
        print(f"⏱️ 耗时: {time.time() - start:.1f}s")
        print("="*60)
        
        # Top异常
        print("\n📈 Top异常:")
        for a in all_alerts[:10]:
            c = a.get('change', 0)
            print(f"   {'+' if c > 0 else ''}{c}% {a.get('symbol', '')} [{a.get('source', '')}]")
        
        return results

if __name__ == '__main__':
    SpiderSystem().scan()
