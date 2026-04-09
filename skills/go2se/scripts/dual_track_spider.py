#!/usr/bin/env python3
"""
双轨蛛网扫描系统
轨道1: 高效率稳定快捷 (USDT主交易对)
轨道2: 更广泛覆盖 (全量交易对)

目标: Binance 2000+ 交易对全覆盖
"""

import requests
import time
import concurrent.futures
from typing import Dict, List
from dataclasses import dataclass, asdict
from threading import Lock

@dataclass
class ScanResult:
    source: str
    total: int
    alerts: List
    duration: float
    timestamp: int

# ==================== 轨道1: 高效率轨道 ====================

class HighSpeedTrack:
    """
    轨道1: 高效率稳定快捷
    - USDT主交易对 (654)
    - BTC交易对 (487)
    - 核心主流币种
    - 5秒内完成
    """
    
    def __init__(self):
        self.threshold = 8.0  # 8%涨跌
        self.priority_pairs = None
    
    def get_priority_symbols(self) -> List[str]:
        """获取优先扫描的交易对"""
        if self.priority_pairs:
            return self.priority_pairs
        
        # 从API获取
        url = 'https://api.binance.com/api/v3/exchangeInfo'
        r = requests.get(url, timeout=30)
        data = r.json()
        
        symbols = [s['symbol'] for s in data['symbols']]
        
        # 优先: USDT > BTC > ETH > BUSD > USDC
        usdt = [s for s in symbols if s.endswith('USDT') and s != 'USDCUSDT']
        btc = [s for s in symbols if s.endswith('BTC')]
        eth = [s for s in symbols if s.endswith('ETH')]
        busd = [s for s in symbols if s.endswith('BUSD')]
        
        # 取前1000个优先对
        self.priority_pairs = (usdt + btc + eth + busd)[:1000]
        return self.priority_pairs
    
    def scan(self) -> ScanResult:
        """快速扫描优先交易对"""
        start = time.time()
        
        symbols = self.get_priority_symbols()
        
        # 构建批量请求
        url = 'https://api.binance.com/api/v3/ticker/24hr'
        
        # 分批获取 (每批100)
        alerts = []
        total = 0
        
        # 直接获取全量，然后筛选
        r = requests.get(url, timeout=30)
        all_data = r.json()
        
        # 筛选优先对
        symbol_set = set(symbols)
        priority_data = [t for t in all_data if t['symbol'] in symbol_set]
        total = len(priority_data)
        
        # 检测异常
        for t in priority_data:
            change = float(t.get('priceChangePercent', 0))
            volume = float(t.get('quoteVolume', 0))
            
            if abs(change) > self.threshold and volume > 10000:
                alerts.append({
                    'symbol': t['symbol'],
                    'change': round(change, 2),
                    'price': t['lastPrice'],
                    'volume': round(volume, 0)
                })
        
        # 排序
        alerts.sort(key=lambda x: abs(x['change']), reverse=True)
        
        return ScanResult(
            source='track1_highspeed',
            total=total,
            alerts=alerts[:20],
            duration=time.time() - start,
            timestamp=int(time.time())
        )

# ==================== 轨道2: 广泛轨道 ====================

class BroadTrack:
    """
    轨道2: 广泛覆盖
    - 全部交易对 (2000+)
    - 包括所有币种
    - 30秒内完成
    """
    
    def __init__(self):
        self.threshold = 10.0
        self.cache = {}
        self.cache_time = 0
    
    def scan(self) -> ScanResult:
        """全量扫描"""
        start = time.time()
        
        # 直接获取全量
        url = 'https://api.binance.com/api/v3/ticker/24hr'
        r = requests.get(url, timeout=30)
        all_data = r.json()
        
        total = len(all_data)
        alerts = []
        
        for t in all_data:
            change = float(t.get('priceChangePercent', 0))
            volume = float(t.get('quoteVolume', 0))
            
            # 更宽松的阈值，覆盖更多
            if abs(change) > self.threshold and volume > 5000:
                alerts.append({
                    'symbol': t['symbol'],
                    'change': round(change, 2),
                    'price': t['lastPrice'],
                    'volume': round(volume, 0)
                })
        
        # 排序
        alerts.sort(key=lambda x: abs(x['change']), reverse=True)
        
        # 缓存
        self.cache = {'alerts': alerts, 'total': total}
        self.cache_time = time.time()
        
        return ScanResult(
            source='track2_broad',
            total=total,
            alerts=alerts[:30],
            duration=time.time() - start,
            timestamp=int(time.time())
        )
    
    def scan_multi_exchange(self) -> ScanResult:
        """多交易所全量扫描"""
        start = time.time()
        
        all_alerts = []
        total = 0
        
        # 并行获取多交易所
        urls = {
            'binance': 'https://api.binance.com/api/v3/ticker/24hr',
            'bybit': 'https://api.bybit.com/v5/market/tickers?category=spot',
            'okx': 'https://www.okx.com/api/v5/market/tickers?instType=SPOT',
        }
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = {executor.submit(self.fetch_and_parse, name, url): name 
                      for name, url in urls.items()}
            
            for future in concurrent.futures.as_completed(futures):
                name = futures[future]
                try:
                    result = future.result()
                    total += result['total']
                    all_alerts.extend(result['alerts'])
                except:
                    pass
        
        # 排序
        all_alerts.sort(key=lambda x: abs(x.get('change', 0)), reverse=True)
        
        return ScanResult(
            source='track2_multi_cex',
            total=total,
            alerts=all_alerts[:30],
            duration=time.time() - start,
            timestamp=int(time.time())
        )
    
    def fetch_and_parse(self, name: str, url: str) -> Dict:
        """获取并解析"""
        r = requests.get(url, timeout=15)
        
        alerts = []
        total = 0
        
        if name == 'binance':
            data = r.json()
            total = len(data)
            for t in data:
                change = float(t.get('priceChangePercent', 0))
                if abs(change) > self.threshold:
                    alerts.append({
                        'symbol': t['symbol'],
                        'change': change,
                        'source': 'binance'
                    })
        
        elif name == 'bybit':
            data = r.json()
            if data.get('retCode') == 0:
                pairs = data['result']['list']
                total = len(pairs)
                for p in pairs:
                    change = float(p.get('price24hPcnt', 0)) * 100
                    if abs(change) > self.threshold:
                        alerts.append({
                            'symbol': p['symbol'],
                            'change': change,
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
                            'change': change,
                            'source': 'okx'
                        })
        
        return {'total': total, 'alerts': alerts}

# ==================== 双轨控制器 ====================

class DualTrackSpiderSystem:
    """
    双轨蛛网扫描系统
    
    轨道1: 高效率轨道
    - 优先交易对 (~1000)
    - 扫描时间 < 5秒
    - 适合实时监控
    
    轨道2: 广泛轨道
    - 全量交易对 (2000+)
    - 扫描时间 < 30秒
    - 适合全面扫描
    """
    
    def __init__(self):
        self.track1 = HighSpeedTrack()
        self.track2 = BroadTrack()
        self.last_track1 = None
        self.last_track2 = None
    
    def scan_track1(self) -> ScanResult:
        """扫描轨道1"""
        result = self.track1.scan()
        self.last_track1 = result
        return result
    
    def scan_track2(self) -> ScanResult:
        """扫描轨道2"""
        result = self.track2.scan()
        self.last_track2 = result
        return result
    
    def scan_both(self) -> Dict:
        """双轨并行扫描"""
        print("\n" + "="*60)
        print("🕸️ 双轨蛛网扫描系统")
        print("="*60)
        
        # 轨道1
        print("\n🚀 轨道1: 高效率轨道 (优先交易对)...")
        t1 = self.scan_track1()
        print(f"   ✅ {t1.total} 交易对, {len(t1.alerts)} 异常, {t1.duration:.2f}s")
        
        # 轨道2: 广泛轨道 (多CEX聚合)
        print("\n🌐 轨道2: 广泛轨道 (多交易所聚合)...")
        t2 = self.track2.scan_multi_exchange()
        print(f"   ✅ {t2.total} 交易对, {len(t2.alerts)} 异常, {t2.duration:.2f}s")
        
        # 汇总
        total_pairs = t1.total + t2.total
        all_alerts = t1.alerts + t2.alerts
        
        # 去重合并
        seen = set()
        unique_alerts = []
        for a in all_alerts:
            if a['symbol'] not in seen:
                seen.add(a['symbol'])
                unique_alerts.append(a)
        
        unique_alerts.sort(key=lambda x: abs(x['change']), reverse=True)
        
        print("\n" + "="*60)
        print(f"📊 双轨总计:")
        print(f"   - 交易对: {t1.total} (高速) + {t2.total} (全量) = {total_pairs}")
        print(f"   - 异常: {len(unique_alerts)}")
        print(f"   - 总耗时: {t1.duration + t2.duration:.2f}s")
        print("="*60)
        
        return {
            'track1': asdict(t1),
            'track2': asdict(t2),
            'summary': {
                'total_pairs': total_pairs,
                'total_alerts': len(unique_alerts),
                'duration': t1.duration + t2.duration,
                'alerts': unique_alerts[:20]
            }
        }
    
    def quick_scan(self) -> Dict:
        """快速扫描 (仅轨道1)"""
        return asdict(self.scan_track1())
    
    def full_scan(self) -> Dict:
        """完整扫描 (轨道1 + 轨道2)"""
        return self.scan_both()

# ===== 测试 =====

def test():
    system = DualTrackSpiderSystem()
    
    # 快速扫描
    print("\n🔍 快速扫描 (轨道1):")
    quick = system.quick_scan()
    print(f"   {quick['total']} 交易对, {len(quick['alerts'])} 异常, {quick['duration']:.2f}s")
    
    # 完整扫描
    result = system.full_scan()
    
    # 显示Top异常
    print("\n📈 Top异常:")
    for a in result['summary']['alerts'][:10]:
        c = a['change']
        print(f"   {'+' if c > 0 else ''}{c}% {a['symbol']}")
    
    return result

if __name__ == '__main__':
    test()
