#!/usr/bin/env python3
"""
高性能全市场蛛网扫描系统 - 多轨道并行
目标: Binance全部 + CEX聚合 + DEX数据 = 10000+ 币种

轨道1: Binance全量 (3537交易对)
轨道2: 多CEX聚合 (Bybit+OKX+KuCoin+Gate)
轨道3: DEX数据 (DexScreener+DeFiLlama)
"""

import requests
import time
import asyncio
import aiohttp
import concurrent.futures
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from threading import Thread
import json

# ==================== 配置 ====================

THREADS = 8  # 并行线程数
BATCH_SIZE = 100  # 批处理大小

# ==================== 数据结构 ====================

@dataclass
class ScanResult:
    source: str
    total: int
    alerts: List
    duration: float

# ==================== 轨道1: Binance全量 ====================

class BinanceFullScanner:
    """Binance全量扫描 (3537交易对)"""
    
    def __init__(self):
        self.url = 'https://api.binance.com/api/v3/ticker/24hr'
        self.threshold = 10.0  # 10%涨跌
    
    def scan(self) -> ScanResult:
        start = time.time()
        
        # 获取全量
        r = requests.get(self.url, timeout=30)
        data = r.json()
        
        alerts = []
        
        # 筛选异常
        for t in data:
            change = float(t.get('priceChangePercent', 0))
            symbol = t['symbol']
            volume = float(t.get('quoteVolume', 0))
            
            if abs(change) > self.threshold and volume > 10000:
                alerts.append({
                    'symbol': symbol,
                    'change': round(change, 2),
                    'price': t['lastPrice'],
                    'volume': round(volume, 0)
                })
        
        # 排序
        alerts.sort(key=lambda x: abs(x['change']), reverse=True)
        
        return ScanResult(
            source='binance_full',
            total=len(data),
            alerts=alerts[:20],
            duration=time.time() - start
        )

# ==================== 轨道2: 多CEX聚合 ====================

class MultiCEXScanner:
    """多交易所并行扫描"""
    
    def __init__(self):
        self.exchanges = {
            'bybit': 'https://api.bybit.com/v5/market/tickers?category=spot',
            'okx': 'https://www.okx.com/api/v5/market/tickers?instType=SPOT',
            'kucoin': 'https://api.kucoin.com/api/v1/market/allTickers',
            'gate': 'https://api.gateio.ws/api4/spot/ticker',
        }
        self.threshold = 10.0
    
    def scan_all(self) -> ScanResult:
        start = time.time()
        
        all_alerts = []
        total = 0
        
        # 并行扫描
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(self.scan_exchange, name, url): name 
                      for name, url in self.exchanges.items()}
            
            for future in concurrent.futures.as_completed(futures):
                name = futures[future]
                try:
                    result = future.result()
                    total += result['total']
                    all_alerts.extend(result['alerts'])
                except Exception as e:
                    print(f"  {name}: error - {e}")
        
        # 排序
        all_alerts.sort(key=lambda x: abs(x.get('change', 0)), reverse=True)
        
        return ScanResult(
            source='multi_cex',
            total=total,
            alerts=all_alerts[:20],
            duration=time.time() - start
        )
    
    def scan_exchange(self, name: str, url: str) -> Dict:
        r = requests.get(url, timeout=15)
        
        alerts = []
        total = 0
        
        if name == 'bybit':
            data = r.json()
            if data.get('retCode') == 0:
                pairs = data['result']['list']
                total = len(pairs)
                for p in pairs:
                    change = float(p.get('price24hPcnt', 0)) * 100
                    if abs(change) > self.threshold:
                        alerts.append({
                            'symbol': p['symbol'],
                            'change': round(change, 2),
                            'source': 'bybit'
                        })
        
        elif name == 'okx':
            data = r.json()
            if data.get('code') == '0':
                pairs = data['data']
                total = len(pairs)
                for p in pairs:
                    change = float(p.get('sod_utc_0', 0))
                    if abs(change) > self.threshold:
                        alerts.append({
                            'symbol': p['instId'],
                            'change': round(change, 2),
                            'source': 'okx'
                        })
        
        elif name == 'kucoin':
            data = r.json()
            if data.get('code') == '200000':
                pairs = data['data']
                total = len(pairs)
                for p in pairs:
                    change = float(p.get('changeRate', 0)) * 100
                    if abs(change) > self.threshold:
                        alerts.append({
                            'symbol': p['symbol'],
                            'change': round(change, 2),
                            'source': 'kucoin'
                        })
        
        elif name == 'gate':
            data = r.json()
            if isinstance(data, list):
                total = len(data)
                for p in data:
                    change = float(p.get('change', 0))
                    if abs(change) > self.threshold:
                        alerts.append({
                            'symbol': p['currency_pair'],
                            'change': round(change, 2),
                            'source': 'gate'
                        })
        
        return {'total': total, 'alerts': alerts}

# ==================== 轨道3: DEX数据 ====================

class DEXScanner:
    """DEX数据扫描"""
    
    def __init__(self):
        self.threshold = 10.0
    
    def scan(self) -> ScanResult:
        start = time.time()
        
        alerts = []
        total = 0
        
        # DexScreener热门
        try:
            r = requests.get('https://api.dexscreener.com/token-tracker/latest', timeout=15)
            if r.status_code == 200:
                data = r.json()
                tokens = data.get('tokens', []) or []
                total += len(tokens)
                
                for t in tokens[:200]:
                    change = t.get('priceChange', {})
                    h1 = float(change.get('h1', 0))
                    
                    if abs(h1) > self.threshold:
                        alerts.append({
                            'symbol': t.get('tokenAddress', '')[:12] + '...',
                            'chain': t.get('chain'),
                            'change': round(h1, 2),
                            'liquidity': t.get('liquidity', {}).get('usd'),
                            'source': 'dexscreener'
                        })
        except Exception as e:
            print(f"  dexscreener: {e}")
        
        # DeFiLlama
        try:
            r = requests.get('https://api.llama.fi/chains', timeout=10)
            chains = r.json()
            total += len(chains)
        except:
            pass
        
        alerts.sort(key=lambda x: abs(x.get('change', 0)), reverse=True)
        
        return ScanResult(
            source='dex',
            total=total,
            alerts=alerts[:20],
            duration=time.time() - start
        )

# ==================== 异步扫描器 ====================

class AsyncScanner:
    """异步高效扫描器"""
    
    def __init__(self):
        self.threshold = 10.0
    
    async def fetch(self, session, url, name):
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                return await resp.json(), name
        except Exception as e:
            return None, name
    
    async def scan_all(self) -> Dict:
        urls = {
            'binance': 'https://api.binance.com/api/v3/ticker/24hr',
            'bybit': 'https://api.bybit.com/v5/market/tickers?category=spot',
            'okx': 'https://www.okx.com/api/v5/market/tickers?instType=SPOT',
        }
        
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch(session, url, name) for name, url in urls.items()]
            results = await asyncio.gather(*tasks)
        
        return results

# ==================== 主系统 ====================

class SpiderSystem:
    """蛛网扫描系统 - 多轨道并行"""
    
    def __init__(self):
        # 轨道
        self.tracks = {
            'track1_binance': BinanceFullScanner(),
            'track2_cex': MultiCEXScanner(),
            'track3_dex': DEXScanner(),
        }
        
        # 缓存
        self.last_results = {}
        self.last_scan = 0
    
    def scan_single_track(self, track_name: str) -> ScanResult:
        """单轨道扫描"""
        scanner = self.tracks.get(track_name)
        if not scanner:
            return None
        
        # 选择正确的方法
        if track_name == 'track1_binance':
            return scanner.scan()
        elif track_name == 'track2_cex':
            return scanner.scan_all()
        elif track_name == 'track3_dex':
            return scanner.scan()
        
        return scanner.scan()
    
    def scan_parallel(self) -> Dict:
        """并行扫描所有轨道"""
        print("\n" + "="*60)
        print("🕸️ 全市场蛛网扫描系统")
        print("="*60)
        
        start = time.time()
        results = {}
        
        # 轨道1: Binance全量
        print("\n🚂 轨道1: Binance全量...")
        t1 = self.scan_single_track('track1_binance')
        results['track1'] = asdict(t1)
        print(f"   ✅ {t1.total} 交易对, {len(t1.alerts)} 异常, {t1.duration:.2f}s")
        
        # 轨道2: 多CEX
        print("\n🚂 轨道2: 多CEX聚合...")
        t2 = self.scan_single_track('track2_cex')
        results['track2'] = asdict(t2)
        print(f"   ✅ {t2.total} 交易对, {len(t2.alerts)} 异常, {t2.duration:.2f}s")
        
        # 轨道3: DEX
        print("\n🚂 轨道3: DEX数据...")
        t3 = self.scan_single_track('track3_dex')
        results['track3'] = asdict(t3)
        print(f"   ✅ {t3.total} 交易对/代币, {len(t3.alerts)} 异常, {t3.duration:.2f}s")
        
        # 汇总
        total_pairs = t1.total + t2.total + t3.total
        total_alerts = len(t1.alerts) + len(t2.alerts) + len(t3.alerts)
        
        # 合并所有警报
        all_alerts = t1.alerts + t2.alerts + t3.alerts
        all_alerts.sort(key=lambda x: abs(x.get('change', 0)), reverse=True)
        
        results['summary'] = {
            'total_pairs': total_pairs,
            'total_alerts': total_alerts,
            'duration': time.time() - start,
            'all_alerts': all_alerts[:30]
        }
        
        print("\n" + "="*60)
        print(f"📊 总计: {total_pairs:,} 交易对, {total_alerts} 异常")
        print(f"⏱️ 耗时: {time.time() - start:.2f}s")
        print("="*60)
        
        self.last_results = results
        self.last_scan = time.time()
        
        return results
    
    def quick_report(self) -> str:
        """快速报告"""
        if not self.last_results:
            self.scan_parallel()
        
        r = self.last_results
        s = r.get('summary', {})
        
        report = f"""
🕸️ 全市场蛛网扫描
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 总覆盖: {s.get('total_pairs', 0):,} 交易对
🚨 异常: {s.get('total_alerts', 0)}
⏱️ 耗时: {s.get('duration', 0):.2f}s

📈 Top异常:
"""
        
        for i, a in enumerate(s.get('all_alerts', [])[:10]):
            change = a.get('change', 0)
            symbol = a.get('symbol', '')
            report += f"   {'+' if change > 0 else ''}{change}% {symbol}\n"
        
        return report

# ===== 测试 =====

def test():
    system = SpiderSystem()
    results = system.scan_parallel()
    
    # 详细报告
    print("\n" + system.quick_report())
    
    return results

if __name__ == '__main__':
    test()
