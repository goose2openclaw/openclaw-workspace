#!/usr/bin/env python3
"""
全市场蛛网扫描器 - 整合多数据源
1. Binance: 3537交易对
2. 多CEX聚合: 8000+
3. DexScreener: DEX实时
4. DeFiLlama: 449链TVL
"""

import requests
import time
import json
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class AnomalyAlert:
    """异常警报"""
    symbol: str
    source: str
    alert_type: str
    severity: str
    value: float
    threshold: float
    metadata: Dict

class MultiSourceSpiderScanner:
    """多数据源蛛网扫描器"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 60
        
        # 阈值配置
        self.thresholds = {
            'price_change_1h': 5.0,
            'price_change_24h': 10.0,
            'volume_spike': 3.0,
            'volume_min_usd': 10000,
        }
        
        # 历史数据
        self.history = {}
    
    # ==================== 数据源1: Binance ====================
    
    def scan_binance(self) -> Dict:
        """Binance全市场扫描 (3537交易对)"""
        url = 'https://api.binance.com/api/v3/ticker/24hr'
        
        try:
            r = requests.get(url, timeout=15)
            data = r.json()
        except Exception as e:
            return {'error': str(e), 'count': 0}
        
        alerts = []
        usdt_pairs = [t for t in data if t['symbol'].endswith('USDT')]
        
        for ticker in usdt_pairs:
            symbol = ticker['symbol']
            change = float(ticker.get('priceChangePercent', 0))
            volume = float(ticker.get('quoteVolume', 0))
            price = float(ticker.get('lastPrice', 0))
            
            # 暴涨
            if change > self.thresholds['price_change_24h']:
                alerts.append(AnomalyAlert(
                    symbol=symbol,
                    source='binance',
                    alert_type='price_surge',
                    severity='critical' if change > 20 else 'high',
                    value=change,
                    threshold=self.thresholds['price_change_24h'],
                    metadata={'price': price, 'volume': volume}
                ))
            # 暴跌
            elif change < -self.thresholds['price_change_24h']:
                alerts.append(AnomalyAlert(
                    symbol=symbol,
                    source='binance',
                    alert_type='price_drop',
                    severity='critical' if change < -20 else 'high',
                    value=change,
                    threshold=-self.thresholds['price_change_24h'],
                    metadata={'price': price, 'volume': volume}
                ))
        
        # Top排序
        by_change = sorted(usdt_pairs, key=lambda x: float(x.get('priceChangePercent', 0)), reverse=True)
        
        return {
            'source': 'binance',
            'total': len(usdt_pairs),
            'alerts': [asdict(a) for a in alerts],
            'alert_count': len(alerts),
            'top_gainers': [
                {'symbol': t['symbol'], 'change': t['priceChangePercent'], 'price': t['lastPrice']}
                for t in by_change[:10]
            ],
            'top_losers': [
                {'symbol': t['symbol'], 'change': t['priceChangePercent'], 'price': t['lastPrice']}
                for t in sorted(usdt_pairs, key=lambda x: float(x.get('priceChangePercent', 0)))[:10]
            ]
        }
    
    # ==================== 数据源2: 多CEX聚合 ====================
    
    def scan_multi_cex(self) -> Dict:
        """多交易所聚合扫描"""
        results = {
            'sources': {},
            'total_pairs': 0,
            'total_alerts': 0
        }
        
        # Binance (已有)
        results['sources']['binance'] = self.scan_binance()
        results['total_pairs'] += results['sources']['bininance'].get('total', 0)
        
        # Bybit
        try:
            bybit_data = self._scan_bybit()
            results['sources']['bybit'] = bybit_data
            results['total_pairs'] += bybit_data.get('total', 0)
        except Exception as e:
            results['sources']['bybit'] = {'error': str(e)}
        
        # OKX
        try:
            okx_data = self._scan_okx()
            results['sources']['okx'] = okx_data
            results['total_pairs'] += okx_data.get('total', 0)
        except Exception as e:
            results['sources']['okx'] = {'error': str(e)}
        
        return results
    
    def _scan_bybit(self) -> Dict:
        """Bybit扫描"""
        url = 'https://api.bybit.com/v2/public/tickers'
        
        r = requests.get(url, timeout=10)
        data = r.json()
        
        if data.get('ret_code') != 0:
            return {'error': 'API error'}
        
        pairs = data.get('result', [])
        usdt_pairs = [p for p in pairs if p.get('symbol', '').endswith('USDT')]
        
        alerts = []
        for p in usdt_pairs:
            change = float(p.get('price_1h_pcnt', 0))
            if abs(change) > self.thresholds['price_change_1h']:
                alerts.append({
                    'symbol': p['symbol'],
                    'change': change,
                    'price': p.get('last_price')
                })
        
        return {
            'source': 'bybit',
            'total': len(usdt_pairs),
            'alerts': alerts,
            'alert_count': len(alerts)
        }
    
    def _scan_okx(self) -> Dict:
        """OKX扫描"""
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
            if abs(change) > self.thresholds['price_change_1h']:
                alerts.append({
                    'symbol': p['instId'],
                    'change': change,
                    'price': p.get('last')
                })
        
        return {
            'source': 'okx',
            'total': len(usdt_pairs),
            'alerts': alerts,
            'alert_count': len(alerts)
        }
    
    # ==================== 数据源3: DexScreener ====================
    
    def scan_dexscreener(self, chains: List[str] = None) -> Dict:
        """DexScreener扫描 (DEX实时)"""
        if chains is None:
            chains = ['solana', 'ethereum', 'bsc', 'base', 'avalanche']
        
        results = {
            'source': 'dexscreener',
            'chains': {},
            'total_pairs': 0,
            'alerts': []
        }
        
        for chain in chains:
            try:
                url = f'https://api.dexscreener.com/latest/dex/tokens/{chain}'
                r = requests.get(url, timeout=10)
                
                if r.status_code != 200:
                    continue
                
                data = r.json()
                pairs = data.get('pairs', []) or []
                
                alerts = []
                for p in pairs[:50]:  # 取前50
                    price_change = p.get('priceChange', {})
                    h1 = price_change.get('h1', 0)
                    h6 = price_change.get('h6', 0)
                    
                    if abs(float(h1)) > self.thresholds['price_change_1h']:
                        alerts.append({
                            'pair': p.get('pairAddress'),
                            'token': p.get('baseToken', {}).get('symbol'),
                            'chain': chain,
                            'change_1h': h1,
                            'change_6h': h6,
                            'liquidity': p.get('liquidity', {}).get('usd'),
                            'volume': p.get('volume', {}).get('h24')
                        })
                    
                    results['total_pairs'] += 1
                
                results['chains'][chain] = {
                    'pairs': len(pairs),
                    'alerts': alerts,
                    'alert_count': len(alerts)
                }
                results['alerts'].extend(alerts)
                
            except Exception as e:
                results['chains'][chain] = {'error': str(e)}
        
        results['alert_count'] = len(results['alerts'])
        
        return results
    
    # ==================== 数据源4: DeFiLlama ====================
    
    def scan_defillama(self) -> Dict:
        """DeFiLlama扫描 (链上TVL)"""
        url = 'https://api.llama.fi/chains'
        
        try:
            r = requests.get(url, timeout=10)
            chains = r.json()
        except Exception as e:
            return {'error': str(e)}
        
        # 按TVL排序
        sorted_chains = sorted(chains, key=lambda x: x.get('tvl', 0), reverse=True)
        
        alerts = []
        for chain in sorted_chains[:20]:
            tvl = chain.get('tvl', 0)
            change_1d = chain.get('change_1d', 0)
            
            # TVL突变
            if abs(float(change_1d)) > 5:
                alerts.append({
                    'chain': chain.get('name'),
                    'tvl': tvl,
                    'change_1d': change_1d
                })
        
        return {
            'source': 'defillama',
            'total_chains': len(chains),
            'top_chains': [
                {'name': c['name'], 'tvl': c['tvl'], 'change_1d': c.get('change_1d', 0)}
                for c in sorted_chains[:10]
            ],
            'alerts': alerts,
            'alert_count': len(alerts)
        }
    
    # ==================== 完整扫描 ====================
    
    def full_scan(self, include_dex: bool = True, include_defi: bool = True) -> Dict:
        """完整扫描所有数据源"""
        print("\n" + "="*60)
        print("🕸️ 全市场蛛网扫描")
        print("="*60)
        
        result = {
            'timestamp': int(time.time()),
            'sources': {}
        }
        
        total_pairs = 0
        total_alerts = 0
        
        # 1. Binance (3537+)
        print("\n📡 扫描 Binance...")
        binance = self.scan_binance()
        result['sources']['binance'] = binance
        total_pairs += binance.get('total', 0)
        total_alerts += binance.get('alert_count', 0)
        print(f"   ✅ {binance.get('total', 0)} 交易对, {binance.get('alert_count', 0)} 异常")
        
        # 2. 多CEX
        print("\n📡 扫描 Bybit...")
        try:
            bybit = self._scan_bybit()
            result['sources']['bybit'] = bybit
            total_pairs += bybit.get('total', 0)
            total_alerts += bybit.get('alert_count', 0)
            print(f"   ✅ {bybit.get('total', 0)} 交易对, {bybit.get('alert_count', 0)} 异常")
        except Exception as e:
            print(f"   ❌ 错误: {e}")
        
        print("\n📡 扫描 OKX...")
        try:
            okx = self._scan_okx()
            result['sources']['okx'] = okx
            total_pairs += okx.get('total', 0)
            total_alerts += okx.get('alert_count', 0)
            print(f"   ✅ {okx.get('total', 0)} 交易对, {okx.get('alert_count', 0)} 异常")
        except Exception as e:
            print(f"   ❌ 错误: {e}")
        
        # 3. DexScreener
        if include_dex:
            print("\n📡 扫描 DexScreener...")
            try:
                dex = self.scan_dexscreener()
                result['sources']['dexscreener'] = dex
                total_pairs += dex.get('total_pairs', 0)
                total_alerts += dex.get('alert_count', 0)
                print(f"   ✅ {dex.get('total_pairs', 0)} 交易对, {dex.get('alert_count', 0)} 异常")
            except Exception as e:
                print(f"   ❌ 错误: {e}")
        
        # 4. DeFiLlama
        if include_defi:
            print("\n📡 扫描 DeFiLlama...")
            try:
                defi = self.scan_defillama()
                result['sources']['defillama'] = defi
                total_alerts += defi.get('alert_count', 0)
                print(f"   ✅ {defi.get('total_chains', 0)} 链, {defi.get('alert_count', 0)} 异常")
            except Exception as e:
                print(f"   ❌ 错误: {e}")
        
        # 汇总
        result['summary'] = {
            'total_pairs': total_pairs,
            'total_alerts': total_alerts
        }
        
        print("\n" + "="*60)
        print(f"📊 扫描完成: {total_pairs} 交易对, {total_alerts} 异常")
        print("="*60)
        
        return result
    
    def get_summary(self) -> str:
        """获取摘要"""
        result = self.full_scan()
        
        summary = f"""
🕸️ 全市场蛛网扫描报告
========================

📊 总计:
   - 交易对: {result['summary']['total_pairs']:,}
   - 异常数: {result['summary']['total_alerts']}
"""
        
        # Binance
        b = result['sources'].get('binance', {})
        if b and 'error' not in b:
            gainers = b.get('top_gainers', [])[:5]
            losers = b.get('top_losers', [])[:5]
            
            summary += f"""
📈 Binance (USDT):
   - 交易对: {b.get('total', 0)}
   - 异常: {b.get('alert_count', 0)}
   - 涨幅Top: {', '.join([f"{g['symbol']}(+{g['change']}%)" for g in gainers])}
   - 跌幅Top: {', '.join([f"{l['symbol']}({l['change']}%)" for l in losers])}
"""
        
        # DeFiLlama
        d = result['sources'].get('defillama', {})
        if d and 'error' not in d:
            chains = d.get('top_chains', [])[:5]
            summary += f"""
🌐 DeFi TVL:
   - 链数: {d.get('total_chains', 0)}
   - TVL Top: {', '.join([c['name'] for c in chains])}
"""
        
        return summary

# ===== 测试 =====

def test():
    scanner = MultiSourceSpiderScanner()
    result = scanner.full_scan(include_dex=True, include_defi=True)
    
    print("\n" + scanner.get_summary())
    
    return result

if __name__ == '__main__':
    test()
