#!/usr/bin/env python3
"""
双轨趋势监控系统 - 集成多轨道蛛网扫描
轨道1: 持仓/指定币种轮换趋势判断
轨道2: 多轨道全市场异常监控 (7,000+ 币种)

与声纳趋势模型集成
"""

import json
import time
import threading
import numpy as np
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
import requests
import concurrent.futures

# 导入趋势匹配器
import sys
sys.path.insert(0, 'skills/go2se/scripts')
from trend_pattern_matcher_v2 import TrendPatternMatcher, StrategyTrigger

# ==================== 数据结构 ====================

@dataclass
class Position:
    symbol: str
    entry_price: float
    quantity: float
    entry_time: int
    stop_loss: float = 0.03
    take_profit: float = 0.05
    strategy: str = ""

@dataclass
class AlertSignal:
    symbol: str
    alert_type: str
    severity: str
    value: float
    source: str
    timestamp: int
    trend_analysis: Optional[Dict] = None

@dataclass
class TrackResult:
    name: str
    total: int
    alerts: List
    duration: float

# ==================== 持仓管理器 ====================

class PositionManager:
    def __init__(self):
        self.positions: Dict[str, Position] = {}
        self.watchlist: List[str] = []
        self.alerts: List[AlertSignal] = []
        self.default_symbols = [
            'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT',
            'XRP/USDT', 'ADA/USDT', 'AVAX/USDT', 'DOT/USDT'
        ]
    
    def add_position(self, symbol: str, entry_price: float, quantity: float, strategy: str = ""):
        self.positions[symbol] = Position(symbol, entry_price, quantity, int(time.time()), strategy=strategy)
    
    def remove_position(self, symbol: str):
        if symbol in self.positions:
            del self.positions[symbol]
    
    def get_positions(self) -> List[str]:
        return list(self.positions.keys())
    
    def add_to_watchlist(self, symbol: str):
        if symbol not in self.watchlist:
            self.watchlist.append(symbol)
    
    def get_watchlist(self) -> List[str]:
        return self.watchlist or self.default_symbols
    
    def add_alert(self, alert: AlertSignal):
        self.alerts.append(alert)
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
    
    def get_recent_alerts(self, hours: int = 24) -> List[AlertSignal]:
        cutoff = int(time.time()) - hours * 3600
        return [a for a in self.alerts if a.timestamp > cutoff]

# ==================== 轨道1: 持仓趋势监控 ====================

class PositionTrackMonitor:
    """轨道1: 持仓/指定币种轮换趋势判断"""
    
    def __init__(self, position_manager: PositionManager, matcher: TrendPatternMatcher):
        self.pm = position_manager
        self.matcher = matcher
        self.current_index = 0
        self.results_history = []
    
    def run_cycle(self) -> Dict:
        symbols = self.pm.get_positions() + self.pm.get_watchlist()
        if not symbols:
            return {'status': 'no_symbols'}
        
        symbol = symbols[self.current_index % len(symbols)]
        self.current_index += 1
        
        result = self.matcher.analyze_symbol(symbol)
        
        self.results_history.append({
            'symbol': symbol,
            'timestamp': int(time.time()),
            'result': result
        })
        
        return {
            'symbol': symbol,
            'result': result,
            'queue_position': self.current_index % len(symbols),
            'total_queue': len(symbols)
        }
    
    def run_full_cycle(self) -> List[Dict]:
        symbols = self.pm.get_positions() + self.pm.get_watchlist()
        results = []
        for symbol in symbols:
            result = self.matcher.analyze_symbol(symbol)
            results.append({'symbol': symbol, 'result': result})
            time.sleep(0.2)
        return results

# ==================== 轨道2: 多轨道蛛网扫描 ====================

class MultiTrackSpiderMonitor:
    """
    轨道2: 多轨道全市场异常监控
    - 轨道1: 高速轨道 (1,000 交易对)
    - 轨道2: 全量轨道 (3,537 交易对)
    - 轨道3: 多CEX轨道 (2,332 交易对)
    - 轨道4: DEX轨道 (449+ 代币)
    """
    
    def __init__(self, position_manager: PositionManager, matcher: TrendPatternMatcher):
        self.pm = position_manager
        self.matcher = matcher
        self.threshold = 10.0
        
        # 缓存
        self.last_results = {}
        self.last_scan = 0
    
    # 轨道1: 高速轨道
    def scan_track1(self) -> TrackResult:
        start = time.time()
        url = 'https://api.binance.com/api/v3/ticker/24hr'
        r = requests.get(url, timeout=30)
        data = r.json()
        
        # 优先交易对
        priority = [t for t in data if t['symbol'].endswith(('USDT', 'BTC', 'ETH'))][:1000]
        
        alerts = []
        for t in priority:
            change = float(t.get('priceChangePercent', 0))
            vol = float(t.get('quoteVolume', 0))
            if abs(change) > 8 and vol > 10000:
                alerts.append({
                    'symbol': t['symbol'],
                    'change': round(change, 2),
                    'type': 'price_surge' if change > 0 else 'price_drop',
                    'source': 'binance_priority'
                })
        
        alerts.sort(key=lambda x: abs(x['change']), reverse=True)
        return TrackResult('高速轨道', len(priority), alerts[:15], time.time() - start)
    
    # 轨道2: 全量轨道
    def scan_track2(self) -> TrackResult:
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
                    'type': 'price_surge' if change > 0 else 'price_drop',
                    'source': 'binance_full'
                })
        
        alerts.sort(key=lambda x: abs(x['change']), reverse=True)
        return TrackResult('全量轨道', len(data), alerts[:20], time.time() - start)
    
    # 轨道3: 多CEX轨道
    def scan_track3(self) -> TrackResult:
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
        return TrackResult('多CEX轨道', total, all_alerts[:15], time.time() - start)
    
    # 轨道4: DEX轨道
    def scan_track4(self) -> TrackResult:
        start = time.time()
        
        total = 449  # DeFiLlama chains
        alerts = []
        
        # DexScreener
        try:
            r = requests.get('https://api.dexscreener.com/token-tracker/latest', timeout=15)
            if r.status_code == 200:
                d = r.json()
                tokens = d.get('tokens', []) or []
                total += len(tokens)
                
                for t in tokens[:100]:
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
        
        alerts.sort(key=lambda x: abs(x['change']), reverse=True)
        return TrackResult('DEX轨道', total, alerts[:10], time.time() - start)
    
    def scan_all_tracks(self, track_mask: int = 0b1111) -> Dict:
        """扫描所有启用轨道"""
        # track_mask: 4位二进制, 每位代表一个轨道是否启用
        # 0b1111 = 全部启用, 0b0001 = 仅轨道1
        
        print("\n" + "="*60)
        print("🕸️ 轨道2: 多轨道蛛网扫描")
        print("="*60)
        
        results = []
        total_pairs = 0
        all_alerts = []
        
        # 轨道1
        if track_mask & 0b0001:
            print("\n🚂 轨道1: 高速轨道...")
            t1 = self.scan_track1()
            results.append(asdict(t1))
            total_pairs += t1.total
            all_alerts.extend(t1.alerts)
            print(f"   ✅ {t1.total:,} 交易对, {len(t1.alerts)} 异常, {t1.duration:.2f}s")
        
        # 轨道2
        if track_mask & 0b0010:
            print("\n🚂 轨道2: 全量轨道...")
            t2 = self.scan_track2()
            results.append(asdict(t2))
            total_pairs += t2.total
            all_alerts.extend(t2.alerts)
            print(f"   ✅ {t2.total:,} 交易对, {len(t2.alerts)} 异常, {t2.duration:.2f}s")
        
        # 轨道3
        if track_mask & 0b0100:
            print("\n🚂 轨道3: 多CEX轨道...")
            t3 = self.scan_track3()
            results.append(asdict(t3))
            total_pairs += t3.total
            all_alerts.extend(t3.alerts)
            print(f"   ✅ {t3.total:,} 交易对, {len(t3.alerts)} 异常, {t3.duration:.2f}s")
        
        # 轨道4
        if track_mask & 0b1000:
            print("\n🚂 轨道4: DEX轨道...")
            t4 = self.scan_track4()
            results.append(asdict(t4))
            total_pairs += t4.total
            all_alerts.extend(t4.alerts)
            print(f"   ✅ {t4.total:,} 代币/链, {len(t4.alerts)} 异常, {t4.duration:.2f}s")
        
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
        print(f"📊 轨道2总计: {total_pairs:,} 交易对, {len(unique_alerts)} 异常")
        print("="*60)
        
        # 存储结果
        self.last_results = {
            'tracks': results,
            'total_pairs': total_pairs,
            'alerts': unique_alerts,
            'timestamp': int(time.time())
        }
        
        return self.last_results
    
    def quick_scan(self) -> Dict:
        """快速扫描 (仅轨道1)"""
        return asdict(self.scan_track1())
    
    def analyze_top_alerts(self, limit: int = 5) -> List[Dict]:
        """对Top异常进行趋势分析"""
        if not self.last_results:
            self.scan_all_tracks()
        
        alerts = self.last_results.get('alerts', [])[:limit]
        
        analyzed = []
        for alert in alerts:
            symbol = alert.get('symbol', '')
            # 转换格式
            if '/' not in symbol:
                symbol = symbol.replace('USDT', '/USDT')
            
            try:
                result = self.matcher.analyze_symbol(symbol)
                
                analyzed.append({
                    'symbol': symbol,
                    'change': alert.get('change'),
                    'source': alert.get('source', alert.get('src', '')),
                    'trend_analysis': result
                })
            except:
                analyzed.append({
                    'symbol': symbol,
                    'change': alert.get('change'),
                    'source': alert.get('source', alert.get('src', '')),
                    'trend_analysis': None
                })
        
        return analyzed

# ==================== 双轨控制器 ====================

class DualTrackController:
    """双轨趋势监控系统 - 集成版"""
    
    def __init__(self):
        self.position_manager = PositionManager()
        self.matcher = TrendPatternMatcher({'min_probability': 0.32})
        
        # 轨道1: 持仓监控
        self.position_track = PositionTrackMonitor(self.position_manager, self.matcher)
        
        # 轨道2: 多轨道蛛网扫描
        self.anomaly_track = MultiTrackSpiderMonitor(self.position_manager, self.matcher)
        
        self.last_position_scan = 0
        self.last_anomaly_scan = 0
    
    # ===== 轨道1操作 =====
    
    def run_position_track(self) -> Dict:
        """运行持仓轨道"""
        return self.position_track.run_cycle()
    
    def run_position_full_cycle(self) -> List[Dict]:
        """运行持仓完整扫描"""
        return self.position_track.run_full_cycle()
    
    # ===== 轨道2操作 =====
    
    def run_anomaly_track(self, mode: str = 'full') -> Dict:
        """运行异常轨道"""
        if mode == 'quick':
            return self.anomaly_track.quick_scan()
        elif mode == 'full':
            return self.anomaly_track.scan_all_tracks()
        else:
            # 指定轨道
            track_map = {'track1': 0b0001, 'track2': 0b0010, 'track3': 0b0100, 'track4': 0b1000}
            mask = track_map.get(mode, 0b1111)
            return self.anomaly_track.scan_all_tracks(mask)
    
    def analyze_alerts(self, limit: int = 5) -> List[Dict]:
        """分析Top异常"""
        return self.anomaly_track.analyze_top_alerts(limit)
    
    # ===== 双轨操作 =====
    
    def run_dual_track(self) -> Dict:
        """运行双轨"""
        results = {
            'timestamp': int(time.time()),
            'position_track': None,
            'anomaly_track': None
        }
        
        # 轨道1: 持仓
        pos_result = self.run_position_track()
        results['position_track'] = pos_result
        
        # 轨道2: 异常
        anomaly_result = self.run_anomaly_track('full')
        results['anomaly_track'] = anomaly_result
        
        return results
    
    def status(self) -> Dict:
        return {
            'positions': self.position_manager.get_positions(),
            'watchlist_size': len(self.position_manager.get_watchlist()),
            'recent_alerts': len(self.position_manager.get_recent_alerts())
        }

# ===== 测试 =====

def test():
    print("="*60)
    print("🕸️ 双轨趋势监控系统 - 集成测试")
    print("="*60)
    
    # 初始化
    controller = DualTrackController()
    
    # 添加持仓
    controller.position_manager.add_position('BTC/USDT', 50000, 0.1, 'momentum')
    controller.position_manager.add_position('ETH/USDT', 3000, 1.0, 'breakout')
    
    # 添加观察列表
    for sym in ['SOL/USDT', 'BNB/USDT', 'XRP/USDT']:
        controller.position_manager.add_to_watchlist(sym)
    
    print(f"\n📊 持仓: {controller.position_manager.get_positions()}")
    print(f"👀 观察: {controller.position_manager.get_watchlist()}")
    
    # ===== 轨道1: 持仓趋势 =====
    print("\n" + "="*60)
    print("🚂 轨道1: 持仓趋势监控")
    print("="*60)
    
    pos_results = controller.run_position_full_cycle()
    for r in pos_results:
        if r['result'].get('best_models'):
            bm = r['result']['best_models'][0]
            print(f"   {r['symbol']}: {bm['model']} ({bm['probability']:.1%})")
    
    # ===== 轨道2: 多轨道异常 =====
    print("\n" + "="*60)
    print("🕸️ 轨道2: 多轨道蛛网扫描")
    print("="*60)
    
    anomaly = controller.run_anomaly_track('full')
    
    # 分析Top异常
    print("\n📈 分析Top异常:")
    analyzed = controller.analyze_alerts(3)
    for a in analyzed:
        print(f"\n   {a['symbol']}: {a['change']}% [{a['source']}]")
        if a.get('trend_analysis') and a['trend_analysis'].get('best_models'):
            bm = a['trend_analysis']['best_models'][0]
            print(f"      趋势: {bm['model']} ({bm['probability']:.1%})")
    
    # 状态
    print("\n" + "="*60)
    print("📊 系统状态")
    print("="*60)
    status = controller.status()
    print(f"   持仓数: {len(status['positions'])}")
    print(f"   观察数: {status['watchlist_size']}")
    print(f"   警报数: {status['recent_alerts']}")
    
    print("\n✅ 集成测试完成")
    
    return controller

def main():
    return test()

if __name__ == '__main__':
    main()
