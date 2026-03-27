#!/usr/bin/env python3
"""
异常监控模块 - 基于Binance排序API (无需造轮子)
利用交易所实时排序功能实现蛛网扫描
"""

import requests
import time
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class AnomalyAlert:
    """异常警报"""
    symbol: str
    alert_type: str      # 'volume_spike', 'price_surge', 'price_drop', 'new_high'
    severity: str        # 'low', 'medium', 'high', 'critical'
    value: float         # 实际值
    threshold: float     # 阈值
    metadata: Dict       # 附加信息

class BinanceSpiderScanner:
    """
    蛛网扫描器 - 基于Binance官方API
    
    原理: 利用交易所的排序API获取全量数据，本地计算筛选
    优势: 无需API Key，覆盖全市场，实时性强
    """
    
    def __init__(self):
        self.base_url = 'https://api.binance.com'
        self.cache = {
            'tickers': None,
            'timestamp': 0
        }
        self.cache_ttl = 60  # 缓存60秒
        
        # 异常阈值
        self.thresholds = {
            'volume_spike_ratio': 3.0,      # 成交量3倍
            'price_change_1h': 5.0,         # 1小时5%
            'price_change_24h': 10.0,        # 24小时10%
            'price_drop_1h': -5.0,           # 1小时-5%
            'price_drop_24h': -15.0,         # 24小时-15%
            'volume_min': 100000,            # 最小成交量
        }
        
        # 历史数据 (用于对比)
        self.history = {}
    
    def fetch_all_tickers(self) -> List[Dict]:
        """获取全部24h ticker数据"""
        # 使用缓存
        now = time.time()
        if self.cache['tickers'] and (now - self.cache['timestamp']) < self.cache_ttl:
            return self.cache['tickers']
        
        url = f'{self.base_url}/api/v3/ticker/24hr'
        response = requests.get(url, timeout=10)
        data = response.json()
        
        self.cache['tickers'] = data
        self.cache['timestamp'] = now
        
        return data
    
    def get_usdt_pairs(self) -> List[Dict]:
        """获取USDT交易对"""
        all_tickers = self.fetch_all_tickers()
        return [t for t in all_tickers if t['symbol'].endswith('USDT')]
    
    def sort_by(self, key: str, ascending: bool = False, pairs: List[Dict] = None) -> List[Dict]:
        """排序"""
        if pairs is None:
            pairs = self.get_usdt_pairs()
        
        return sorted(pairs, key=lambda x: float(x.get(key, 0)), reverse=not ascending)
    
    def scan_volume_anomalies(self, pairs: List[Dict] = None) -> List[AnomalyAlert]:
        """扫描成交量异常"""
        if pairs is None:
            pairs = self.get_usdt_pairs()
        
        alerts = []
        
        # 按成交量排序
        sorted_by_vol = self.sort_by('quoteVolume', pairs=pairs)
        
        # 对比历史
        for ticker in sorted_by_vol[:100]:  # 只看Top 100
            symbol = ticker['symbol']
            current_vol = float(ticker['quoteVolume'])
            
            # 初始化历史
            if symbol not in self.history:
                self.history[symbol] = {'volume': current_vol, 'time': time.time()}
                continue
            
            # 计算变化率
            prev_vol = self.history[symbol]['volume']
            if prev_vol > 0:
                vol_ratio = current_vol / prev_vol
                
                if vol_ratio > self.thresholds['volume_spike_ratio']:
                    alerts.append(AnomalyAlert(
                        symbol=symbol,
                        alert_type='volume_spike',
                        severity='high' if vol_ratio > 5 else 'medium',
                        value=vol_ratio,
                        threshold=self.thresholds['volume_spike_ratio'],
                        metadata={
                            'current_volume': current_vol,
                            'previous_volume': prev_vol,
                            'price': ticker['lastPrice']
                        }
                    ))
            
            # 更新历史
            self.history[symbol] = {'volume': current_vol, 'time': time.time()}
        
        return alerts
    
    def scan_price_anomalies(self, pairs: List[Dict] = None) -> List[AnomalyAlert]:
        """扫描价格异常"""
        if pairs is None:
            pairs = self.get_usdt_pairs()
        
        alerts = []
        
        for ticker in pairs:
            change_1h = float(ticker.get('priceChangePercent', 0))
            change_24h = float(ticker.get('priceChangePercent', 0))
            volume = float(ticker['quoteVolume'])
            
            # 过滤低成交量
            if volume < self.thresholds['volume_min']:
                continue
            
            # 暴涨
            if change_1h > self.thresholds['price_change_1h']:
                alerts.append(AnomalyAlert(
                    symbol=ticker['symbol'],
                    alert_type='price_surge',
                    severity='critical' if change_1h > 20 else 'high',
                    value=change_1h,
                    threshold=self.thresholds['price_change_1h'],
                    metadata={'price': ticker['lastPrice'], 'volume': volume}
                ))
            
            # 暴跌
            elif change_1h < self.thresholds['price_drop_1h']:
                alerts.append(AnomalyAlert(
                    symbol=ticker['symbol'],
                    alert_type='price_drop',
                    severity='critical' if change_1h < -20 else 'high',
                    value=change_1h,
                    threshold=self.thresholds['price_drop_1h'],
                    metadata={'price': ticker['lastPrice'], 'volume': volume}
                ))
            
            # 24小时极端
            elif abs(change_24h) > self.thresholds['price_change_24h']:
                alerts.append(AnomalyAlert(
                    symbol=ticker['symbol'],
                    alert_type='extreme_24h',
                    severity='medium',
                    value=change_24h,
                    threshold=self.thresholds['price_change_24h'],
                    metadata={'price': ticker['lastPrice']}
                ))
        
        return alerts
    
    def get_top_movers(self, limit: int = 10, trend: str = 'both') -> Dict:
        """获取Top波动币"""
        pairs = self.get_usdt_pairs()
        
        result = {'gainers': [], 'losers': [], 'volume': []}
        
        # 涨幅榜
        if trend in ['gainers', 'both']:
            sorted_gain = self.sort_by('priceChangePercent', pairs=pairs)
            result['gainers'] = [
                {
                    'symbol': t['symbol'],
                    'price': t['lastPrice'],
                    'change': t['priceChangePercent'],
                    'volume': t['quoteVolume']
                }
                for t in sorted_gain[:limit]
            ]
        
        # 跌幅榜
        if trend in ['losers', 'both']:
            sorted_lose = self.sort_by('priceChangePercent', ascending=True, pairs=pairs)
            result['losers'] = [
                {
                    'symbol': t['symbol'],
                    'price': t['lastPrice'],
                    'change': t['priceChangePercent'],
                    'volume': t['quoteVolume']
                }
                for t in sorted_lose[:limit]
            ]
        
        # 成交量榜
        if trend in ['volume', 'both']:
            sorted_vol = self.sort_by('quoteVolume', pairs=pairs)
            result['volume'] = [
                {
                    'symbol': t['symbol'],
                    'price': t['lastPrice'],
                    'change': t['priceChangePercent'],
                    'volume': t['quoteVolume']
                }
                for t in sorted_vol[:limit]
            ]
        
        return result
    
    def full_scan(self) -> Dict:
        """完整扫描"""
        pairs = self.get_usdt_pairs()
        
        print(f"\n🕸️ Binance蛛网扫描")
        print(f"   监控币种: {len(pairs)} USDT交易对")
        
        # 1. 成交量异常
        vol_alerts = self.scan_volume_anomalies(pairs)
        
        # 2. 价格异常
        price_alerts = self.scan_price_anomalies(pairs)
        
        # 3. 获取Top波动
        top_movers = self.get_top_movers(limit=5)
        
        # 汇总
        all_alerts = vol_alerts + price_alerts
        
        # 按严重程度排序
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        all_alerts.sort(key=lambda x: severity_order.get(x.severity, 3))
        
        result = {
            'timestamp': int(time.time()),
            'total_pairs': len(pairs),
            'anomalies': {
                'volume': len(vol_alerts),
                'price': len(price_alerts),
                'total': len(all_alerts)
            },
            'alerts': [
                {
                    'symbol': a.symbol,
                    'type': a.alert_type,
                    'severity': a.severity,
                    'value': round(a.value, 2),
                    'threshold': a.threshold,
                    'price': a.metadata.get('price')
                }
                for a in all_alerts[:20]  # 只返回Top 20
            ],
            'top_movers': top_movers
        }
        
        return result

# ===== 多交易所聚合 =====

class MultiExchangeScanner:
    """多交易所聚合扫描"""
    
    def __init__(self):
        self.exchanges = {
            'binance': 'https://api.binance.com',
            'bybit': 'https://api.bybit.com/v2/public/tickers',
            # OKX需要更多处理
        }
    
    def scan_binance(self) -> Dict:
        scanner = BinanceSpiderScanner()
        return scanner.full_scan()
    
    def scan_all(self) -> Dict:
        """聚合扫描"""
        result = {
            'timestamp': int(time.time()),
            'sources': {}
        }
        
        # Binance
        try:
            result['sources']['binance'] = self.scan_binance()
        except Exception as e:
            result['sources']['binance'] = {'error': str(e)}
        
        return result

# ===== 测试 =====

def test():
    """测试"""
    print("="*60)
    print("🕸️ 蛛网扫描器测试")
    print("="*60)
    
    scanner = BinanceSpiderScanner()
    
    # 完整扫描
    result = scanner.full_scan()
    
    print(f"\n📊 扫描结果:")
    print(f"   总币种: {result['total_pairs']}")
    print(f"   异常数: {result['anomalies']['total']}")
    print(f"   - 成交量异常: {result['anomalies']['volume']}")
    print(f"   - 价格异常: {result['anomalies']['price']}")
    
    # Top波动
    print(f"\n📈 涨幅榜:")
    for m in result['top_movers']['gainers'][:5]:
        print(f"   {m['symbol']}: +{m['change']}% (${m['price']})")
    
    print(f"\n📉 跌幅榜:")
    for m in result['top_movers']['losers'][:5]:
        print(f"   {m['symbol']}: {m['change']}% (${m['price']})")
    
    # 警报
    if result['alerts']:
        print(f"\n🚨 警报 ({len(result['alerts'])}个):")
        for a in result['alerts'][:10]:
            print(f"   [{a['severity'].upper()}] {a['symbol']}: {a['type']} {a['value']}%")
    
    return result

if __name__ == '__main__':
    test()
