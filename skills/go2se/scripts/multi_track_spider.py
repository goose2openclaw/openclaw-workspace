#!/usr/bin/env python3
"""
多轨道蛛网扫描系统 (4轨)
轨道1: 高速轨道 - 优先交易对
轨道2: 全量轨道 - Binance全量
轨道3: 多CEX轨道 - Bybit+OKX+Huobi
轨道4: DEX轨道 - DexScreener+DeFiLlama
"""

import requests
import time
import concurrent.futures
from typing import Dict, List
from dataclasses import dataclass, asdict

@dataclass
class TrackResult:
    name: str
    total: int
    alerts: List
    duration: float
    source: str

# ==================== 轨道1: 高速轨道 ====================

class HighSpeedTrack:
    """轨道1: 高速轨道 - 优先交易对 (<10秒)"""
    
    def __init__(self):
        self.threshold = 8.0
        self.name = "高速轨道"
    
    def scan(self) -> TrackResult:
        start = time.time()
        
        url = 'https://api.binance.com/api/v3/ticker/24hr'
        r = requests.get(url, timeout=30)
        data = r.json()
        
        # 优先: USDT, BTC, ETH
        priority = []
        for t in data:
            sym = t['symbol']
            if sym.endswith('USDT') or sym.endswith('BTC') or sym.endswith('ETH'):
                if len(priority) < 1000:
                    priority.append(t)
        
        alerts = []
        for t in priority:
            change = float(t.get('priceChangePercent', 0))
            vol = float(t.get('quoteVolume', 0))
            if abs(change) > self.threshold and vol > 10000:
                alerts.append({
                    'symbol': t['symbol'],
                    'change': round(change, 2),
                    'price': t['lastPrice']
                })
        
        alerts.sort(key=lambda x: abs(x['change']), reverse=True)
        
        return TrackResult(
            name=self.name,
            total=len(priority),
            alerts=alerts[:15],
            duration=time.time() - start,
            source='binance_priority'
        )

# ==================== 轨道2: 全量轨道 ====================

class FullTrack:
    """轨道2: 全量轨道 - Binance全部交易对"""
    
    def __init__(self):
        self.threshold = 10.0
        self.name = "全量轨道"
    
    def scan(self) -> TrackResult:
        start = time.time()
        
        url = 'https://api.binance.com/api/v3/ticker/24hr'
        r = requests.get(url, timeout=30)
        data = r.json()
        
        alerts = []
        for t in data:
            change = float(t.get('priceChangePercent', 0))
            vol = float(t.get('quoteVolume', 0))
            if abs(change) > self.threshold and vol > 5000:
                alerts.append({
                    'symbol': t['symbol'],
                    'change': round(change, 2),
                    'price': t['lastPrice']
                })
        
        alerts.sort(key=lambda x: abs(x['change']), reverse=True)
        
        return TrackResult(
            name=self.name,
            total=len(data),
            alerts=alerts[:20],
            duration=time.time() - start,
            source='binance_full'
        )

# ==================== 轨道3: 多CEX轨道 ====================

class MultiCEXTrack:
    """轨道3: 多CEX聚合轨道"""
    
    def __init__(self):
        self.threshold = 10.0
        self.name = "多CEX轨道"
    
    def scan(self) -> TrackResult:
        start = time.time()
        
        urls = {
            'bybit': 'https://api.bybit.com/v5/market/tickers?category=spot',
            'okx': 'https://www.okx.com/api/v5/market/tickers?instType=SPOT',
            'huobi': 'https://api.huobi.pro/market/tickers',
        }
        
        all_alerts = []
        total = 0
        
        for name, url in urls.items():
            try:
                r = requests.get(url, timeout=15)
                
                if name == 'bybit':
                    d = r.json()
                    if d.get('retCode') == 0:
                        pairs = d['result']['list']
                        total += len(pairs)
                        for p in pairs:
                            c = float(p.get('price24hPcnt', 0)) * 100
                            if abs(c) > self.threshold:
                                all_alerts.append({'symbol': p['symbol'], 'change': round(c, 2), 'src': 'bybit'})
                
                elif name == 'okx':
                    d = r.json()
                    if d.get('code') == '0':
                        pairs = d['data']
                        total += len(pairs)
                        for p in pairs:
                            c = float(p.get('sod_utc_0', 0))
                            if abs(c) > self.threshold:
                                all_alerts.append({'symbol': p['instId'], 'change': round(c, 2), 'src': 'okx'})
                
                elif name == 'huobi':
                    d = r.json()
                    if 'data' in d:
                        pairs = d['data']
                        total += len(pairs)
                        for p in pairs:
                            o = float(p.get('open', 1) or 1)
                            c = float(p.get('close', 1) or 1)
                            if o > 0:
                                c = ((c - o) / o) * 100
                                if abs(c) > self.threshold:
                                    all_alerts.append({'symbol': p['symbol'], 'change': round(c, 2), 'src': 'huobi'})
            except:
                pass
        
        all_alerts.sort(key=lambda x: abs(x['change']), reverse=True)
        
        return TrackResult(
            name=self.name,
            total=total,
            alerts=all_alerts[:15],
            duration=time.time() - start,
            source='multi_cex'
        )

# ==================== 轨道4: DEX轨道 ====================

class DEXTrack:
    """轨道4: DEX数据轨道"""
    
    def __init__(self):
        self.threshold = 10.0
        self.name = "DEX轨道"
    
    def scan(self) -> TrackResult:
        start = time.time()
        
        total = 0
        alerts = []
        
        # DexScreener
        try:
            r = requests.get('https://api.dexscreener.com/token-tracker/latest', timeout=15)
            if r.status_code == 200:
                d = r.json()
                tokens = d.get('tokens', []) or []
                total += len(tokens)
                
                for t in tokens[:200]:
                    c = t.get('priceChange', {}).get('h1', 0)
                    if abs(float(c)) > self.threshold:
                        alerts.append({
                            'symbol': t.get('tokenAddress', '')[:12] + '...',
                            'chain': t.get('chain'),
                            'change': round(float(c), 2),
                            'src': 'dexscreener'
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
        
        return TrackResult(
            name=self.name,
            total=total,
            alerts=alerts[:10],
            duration=time.time() - start,
            source='dex'
        )

# ==================== 多轨道控制器 ====================

class MultiTrackSpider:
    """多轨道蛛网扫描系统"""
    
    def __init__(self, num_tracks: int = 4):
        self.num_tracks = num_tracks
        
        # 初始化轨道
        self.tracks = [
            HighSpeedTrack(),    # 轨道1
            FullTrack(),         # 轨道2
            MultiCEXTrack(),     # 轨道3
            DEXTrack(),          # 轨道4
        ][:num_tracks]
    
    def scan_all(self) -> Dict:
        """扫描所有轨道"""
        print("\n" + "="*60)
        print("🕸️ 多轨道蛛网扫描系统")
        print("="*60)
        
        results = []
        total_pairs = 0
        all_alerts = []
        
        for i, track in enumerate(self.tracks):
            print(f"\n🚂 轨道{i+1}: {track.name}...")
            result = track.scan()
            results.append(asdict(result))
            
            total_pairs += result.total
            all_alerts.extend(result.alerts)
            
            print(f"   ✅ {result.total:,} 交易对, {len(result.alerts)} 异常, {result.duration:.2f}s")
        
        # 去重合并
        seen = set()
        unique_alerts = []
        for a in all_alerts:
            sym = a.get('symbol', '')
            if sym not in seen:
                seen.add(sym)
                unique_alerts.append(a)
        
        unique_alerts.sort(key=lambda x: abs(x.get('change', 0)), reverse=True)
        
        total_time = sum(r['duration'] for r in results)
        
        print("\n" + "="*60)
        print(f"📊 多轨道总计:")
        print(f"   - 轨道数: {len(self.tracks)}")
        print(f"   - 交易对: {total_pairs:,}")
        print(f"   - 异常: {len(unique_alerts)}")
        print(f"   - 总耗时: {total_time:.2f}s")
        print("="*60)
        
        # Top异常
        print("\n📈 Top异常:")
        for a in unique_alerts[:15]:
            c = a.get('change', 0)
            s = a.get('symbol', '')
            src = a.get('src', a.get('source', ''))
            print(f"   {'+' if c > 0 else ''}{c}% {s} [{src}]")
        
        return {
            'tracks': results,
            'summary': {
                'total_pairs': total_pairs,
                'total_alerts': len(unique_alerts),
                'duration': total_time,
                'alerts': unique_alerts[:30]
            }
        }
    
    def quick_scan(self) -> Dict:
        """快速扫描 (仅轨道1)"""
        print("\n🔍 快速扫描 (轨道1)...")
        result = self.tracks[0].scan()
        print(f"   ✅ {result.total} 交易对, {len(result.alerts)} 异常, {result.duration:.2f}s")
        return asdict(result)

# ===== 测试 =====

def test():
    # 4轨道系统
    print("🎯 测试 4轨道系统:")
    spider = MultiTrackSpider(num_tracks=4)
    result = spider.scan_all()
    
    return result

if __name__ == '__main__':
    test()
