#!/usr/bin/env python3
"""
双轨趋势监控系统
轨道1: 持仓/指定币种轮换趋势判断
轨道2: 全市场异常监控 (4万+币种蛛网扫描)

与声纳趋势模型集成
"""

import json
import time
import threading
import numpy as np
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque
import ccxt
import random

# 导入趋势匹配器
import sys
sys.path.insert(0, 'skills/go2se/scripts')
from trend_pattern_matcher_v2 import TrendPatternMatcher, StrategyTrigger

# ==================== 数据结构 ====================

@dataclass
class Position:
    """持仓结构"""
    symbol: str
    entry_price: float
    quantity: float
    entry_time: int
    stop_loss: float = 0.03
    take_profit: float = 0.05
    strategy: str = ""

@dataclass
class AlertSignal:
    """异常警报"""
    symbol: str
    alert_type: str          # 'volume_spike', 'price_move', 'liquidity', 'social'
    severity: str            # 'low', 'medium', 'high', 'critical'
    metric_value: float
    threshold: float
    timestamp: int
    trend_analysis: Optional[Dict] = None

@dataclass
class MonitorTask:
    """监控任务"""
    task_id: str
    task_type: str           # 'position' | 'watchlist' | 'market_scan'
    symbols: List[str]
    interval: int           # 秒
    last_run: int = 0
    status: str = 'idle'

# ==================== 持仓管理器 ====================

class PositionManager:
    """持仓管理器"""
    
    def __init__(self):
        self.positions: Dict[str, Position] = {}
        self.watchlist: List[str] = []
        self.alerts: List[AlertSignal] = []
        
        # 默认监控列表
        self.default_symbols = [
            'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT',
            'XRP/USDT', 'ADA/USDT', 'AVAX/USDT', 'DOT/USDT',
            'MATIC/USDT', 'LINK/USDT', 'UNI/USDT', 'ATOM/USDT'
        ]
    
    def add_position(self, symbol: str, entry_price: float, 
                    quantity: float, strategy: str = ""):
        """添加持仓"""
        self.positions[symbol] = Position(
            symbol=symbol,
            entry_price=entry_price,
            quantity=quantity,
            entry_time=int(time.time()),
            strategy=strategy
        )
    
    def remove_position(self, symbol: str):
        """移除持仓"""
        if symbol in self.positions:
            del self.positions[symbol]
    
    def get_positions(self) -> List[str]:
        """获取所有持仓币种"""
        return list(self.positions.keys())
    
    def add_to_watchlist(self, symbol: str):
        """添加到观察列表"""
        if symbol not in self.watchlist:
            self.watchlist.append(symbol)
    
    def get_watchlist(self) -> List[str]:
        """获取观察列表"""
        return self.watchlist or self.default_symbols
    
    def add_alert(self, alert: AlertSignal):
        """添加警报"""
        self.alerts.append(alert)
        # 只保留最近100条
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
    
    def get_recent_alerts(self, hours: int = 24) -> List[AlertSignal]:
        """获取最近警报"""
        cutoff = int(time.time()) - hours * 3600
        return [a for a in self.alerts if a.timestamp > cutoff]

# ==================== 异常检测器 ====================

class AnomalyDetector:
    """异常检测器 - 蛛网式扫描"""
    
    def __init__(self, position_manager: PositionManager):
        self.pm = position_manager
        self.exchanges = {}
        self._init_exchanges()
        
        # 统计缓存
        self.volume_history: Dict[str, deque] = {}
        self.price_history: Dict[str, deque] = {}
        
        # 异常阈值配置
        self.thresholds = {
            'volume_spike': 3.0,      # 成交量3倍
            'price_move': 0.05,        # 价格变动5%
            'price_drop': -0.10,       # 暴跌10%
            'volatility_spike': 2.0,   # 波动率2倍
        }
        
        # 已扫描的币种
        self.scanned_symbols = set()
        self.last_full_scan = 0
    
    def _init_exchanges(self):
        """初始化交易所"""
        for eid in ['binance', 'bybit', 'okx']:
            try:
                ec = getattr(ccxt, eid, None)
                if ec:
                    self.exchanges[eid] = ec({'enableRateLimit': True})
            except:
                pass
    
    def get_all_symbols(self, exchange: str = 'binance', force: bool = False) -> List[str]:
        """获取所有交易对 (支持缓存)"""
        cache_key = f'{exchange}_symbols'
        
        # 每小时刷新一次
        if force or time.time() - self.last_full_scan > 3600:
            try:
                ex = self.exchanges.get(exchange)
                if not ex:
                    return []
                
                markets = ex.load_markets()
                symbols = [s for s in markets.keys() 
                          if s.endswith('/USDT') or s.endswith('/BTC')]
                
                # 限制数量
                self.all_symbols = symbols[:50000]
                self.last_full_scan = time.time()
                
                return self.all_symbols
            except:
                return []
        
        return getattr(self, 'all_symbols', [])
    
    def scan_batch(self, symbols: List[str], batch_size: int = 100) -> List[AlertSignal]:
        """批量扫描 - 蛛网式"""
        alerts = []
        
        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i+batch_size]
            
            for symbol in batch:
                try:
                    alert = self.check_symbol(symbol)
                    if alert:
                        alerts.append(alert)
                        # 同时添加到管理器
                        self.pm.add_alert(alert)
                except:
                    pass
            
            # 避免API限制
            time.sleep(0.1)
        
        return alerts
    
    def check_symbol(self, symbol: str) -> Optional[AlertSignal]:
        """检查单个币种异常"""
        try:
            ex = self.exchanges.get('binance')
            if not ex:
                return None
            
            # 获取数据
            ohlcv = ex.fetch_ohlcv(symbol, '1m', limit=60)
            if len(ohlcv) < 30:
                return None
            
            closes = [c[4] for c in ohlcv]
            volumes = [c[5] for c in ohlcv]
            
            current_price = closes[-1]
            current_vol = volumes[-1]
            
            # 初始化历史
            if symbol not in self.volume_history:
                self.volume_history[symbol] = deque(maxlen=100)
                self.price_history[symbol] = deque(maxlen=100)
            
            # 添加到历史
            self.volume_history[symbol].append(current_vol)
            self.price_history[symbol].append(current_price)
            
            # 检查异常
            avg_vol = np.mean(list(self.volume_history[symbol])[:-1]) if len(self.volume_history[symbol]) > 1 else current_vol
            avg_price = np.mean(list(self.price_history[symbol])[:-1]) if len(self.price_history[symbol]) > 1 else current_price
            
            # 1. 成交量激增
            if avg_vol > 0:
                vol_ratio = current_vol / avg_vol
                if vol_ratio > self.thresholds['volume_spike']:
                    return AlertSignal(
                        symbol=symbol,
                        alert_type='volume_spike',
                        severity='high' if vol_ratio > 5 else 'medium',
                        metric_value=vol_ratio,
                        threshold=self.thresholds['volume_spike'],
                        timestamp=int(time.time())
                    )
            
            # 2. 价格变动
            if avg_price > 0:
                price_change = (current_price - avg_price) / avg_price
                
                if price_change < self.thresholds['price_drop']:
                    return AlertSignal(
                        symbol=symbol,
                        alert_type='price_drop',
                        severity='critical',
                        metric_value=price_change,
                        threshold=self.thresholds['price_drop'],
                        timestamp=int(time.time())
                    )
                elif abs(price_change) > self.thresholds['price_move']:
                    return AlertSignal(
                        symbol=symbol,
                        alert_type='price_move',
                        severity='medium',
                        metric_value=price_change,
                        threshold=self.thresholds['price_move'],
                        timestamp=int(time.time())
                    )
            
            return None
            
        except:
            return None
    
    def full_market_scan(self, max_symbols: int = 40000) -> List[AlertSignal]:
        """全市场扫描 - 蛛网模式"""
        print(f"\n🕸️ 开始全市场异常扫描 (最多 {max_symbols} 币种)...")
        
        symbols = self.get_all_symbols()
        if not symbols:
            print("❌ 无法获取币种列表")
            return []
        
        # 限制数量
        symbols = symbols[:max_symbols]
        
        print(f"📊 待扫描: {len(symbols)} 币种")
        
        all_alerts = []
        start_time = time.time()
        
        # 分批扫描
        batch_size = 500
        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i+batch_size]
            
            alerts = self.scan_batch(batch)
            all_alerts.extend(alerts)
            
            # 进度
            progress = (i + len(batch)) / len(symbols) * 100
            elapsed = time.time() - start_time
            print(f"   进度: {progress:.1f}% | 耗时: {elapsed:.1f}s | 发现异常: {len(all_alerts)}")
            
            # 避免API限制
            time.sleep(0.5)
        
        print(f"✅ 扫描完成! 发现 {len(all_alerts)} 个异常")
        
        return all_alerts

# ==================== 轨道1: 持仓趋势监控 ====================

class PositionTrackMonitor:
    """持仓轨道 - 轮换趋势判断"""
    
    def __init__(self, position_manager: PositionManager, matcher: TrendPatternMatcher):
        self.pm = position_manager
        self.matcher = matcher
        self.current_index = 0
        self.results_history = deque(maxlen=100)
    
    def run_cycle(self) -> Dict:
        """运行一轮监控"""
        # 获取监控列表 (持仓 + 观察)
        symbols = self.pm.get_positions() + self.pm.get_watchlist()
        
        if not symbols:
            return {'status': 'no_symbols'}
        
        # 轮换到下一个
        symbol = symbols[self.current_index % len(symbols)]
        self.current_index += 1
        
        # 趋势分析
        result = self.matcher.analyze_symbol(symbol)
        
        # 保存结果
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
        """运行完整一轮"""
        symbols = self.pm.get_positions() + self.pm.get_watchlist()
        
        results = []
        for symbol in symbols:
            result = self.matcher.analyze_symbol(symbol)
            results.append({
                'symbol': symbol,
                'result': result
            })
            time.sleep(0.2)  # 避免API限制
        
        return results

# ==================== 轨道2: 异常监控 ====================

class AnomalyTrackMonitor:
    """异常轨道 - 全市场监控"""
    
    def __init__(self, position_manager: PositionManager, matcher: TrendPatternMatcher):
        self.pm = position_manager
        self.matcher = matcher
        self.detector = AnomalyDetector(position_manager)
        self.alert_history = deque(maxlen=500)
        self.is_scanning = False
    
    def quick_scan(self, sample_size: int = 100) -> List[AlertSignal]:
        """快速扫描 - 随机采样"""
        all_symbols = self.detector.get_all_symbols()
        
        if not all_symbols:
            return []
        
        # 随机采样
        if len(all_symbols) > sample_size:
            sample = random.sample(all_symbols, sample_size)
        else:
            sample = all_symbols
        
        print(f"🔍 快速扫描: {len(sample)} 币种")
        
        alerts = []
        for symbol in sample:
            try:
                alert = self.detector.check_symbol(symbol)
                if alert:
                    alerts.append(alert)
                    self.pm.add_alert(alert)
            except:
                pass
        
        return alerts
    
    def full_scan(self, max_symbols: int = 40000) -> Dict:
        """全量扫描"""
        if self.is_scanning:
            return {'status': 'already_scanning'}
        
        self.is_scanning = True
        
        try:
            # 全市场扫描
            alerts = self.detector.full_market_scan(max_symbols)
            
            # 对高危异常进行趋势分析
            critical_alerts = [a for a in alerts if a.severity in ['high', 'critical']]
            
            for alert in critical_alerts[:10]:  # 限制分析数量
                result = self.matcher.analyze_symbol(alert.symbol)
                alert.trend_analysis = result
            
            self.alert_history.extend(alerts)
            
            return {
                'status': 'completed',
                'total_alerts': len(alerts),
                'critical_count': len(critical_alerts),
                'alerts': alerts
            }
        finally:
            self.is_scanning = False
    
    def get_recent_alerts(self, hours: int = 1) -> List[AlertSignal]:
        """获取最近警报"""
        return self.pm.get_recent_alerts(hours)

# ==================== 双轨控制器 ====================

class DualTrackController:
    """双轨趋势监控系统"""
    
    def __init__(self):
        # 初始化组件
        self.position_manager = PositionManager()
        self.matcher = TrendPatternMatcher({'min_probability': 0.32})
        
        # 轨道1: 持仓监控
        self.position_track = PositionTrackMonitor(self.position_manager, self.matcher)
        
        # 轨道2: 异常监控
        self.anomaly_track = AnomalyTrackMonitor(self.position_manager, self.matcher)
        
        # 配置
        self.config = {
            'position_scan_interval': 60,      # 持仓扫描间隔(秒)
            'quick_scan_interval': 300,        # 快速扫描间隔(秒)
            'full_scan_interval': 3600,        # 全量扫描间隔(秒)
            'max_symbols_scan': 40000,        # 最大扫描币种数
        }
        
        self.last_position_scan = 0
        self.last_quick_scan = 0
        self.last_full_scan = 0
    
    def run_position_track(self) -> Dict:
        """运行持仓轨道"""
        result = self.position_track.run_cycle()
        
        # 检查是否需要完整扫描
        now = int(time.time())
        if now - self.last_position_scan > self.config['position_scan_interval'] * 5:
            # 每5个周期运行一次完整扫描
            results = self.position_track.run_full_cycle()
            self.last_position_scan = now
            return {
                'type': 'full_cycle',
                'results': results
            }
        
        return {'type': 'single', 'data': result}
    
    def run_anomaly_track(self, mode: str = 'quick') -> Dict:
        """运行异常轨道"""
        if mode == 'quick':
            alerts = self.anomaly_track.quick_scan()
            return {
                'type': 'quick_scan',
                'alerts_count': len(alerts),
                'alerts': [
                    {'symbol': a.symbol, 'type': a.alert_type, 'severity': a.severity}
                    for a in alerts[:10]
                ]
            }
        elif mode == 'full':
            result = self.anomaly_track.full_scan(self.config['max_symbols_scan'])
            return result
        else:
            return {'error': 'unknown_mode'}
    
    def analyze_alert(self, symbol: str) -> Dict:
        """分析警报"""
        result = self.matcher.analyze_symbol(symbol)
        
        # 获取该币种最近的警报
        alerts = [a for a in self.position_manager.alerts if a.symbol == symbol]
        
        return {
            'symbol': symbol,
            'trend_analysis': result,
            'recent_alerts': [
                {'type': a.alert_type, 'severity': a.severity, 'timestamp': a.timestamp}
                for a in alerts[-5:]
            ]
        }
    
    def run_dual_track(self, cycles: int = 1) -> Dict:
        """运行双轨一轮"""
        results = {
            'timestamp': int(time.time()),
            'position_track': None,
            'anomaly_track': None
        }
        
        # 轨道1: 持仓趋势
        pos_result = self.run_position_track()
        results['position_track'] = pos_result
        
        # 轨道2: 异常监控
        anomaly_result = self.run_anomaly_track('quick')
        results['anomaly_track'] = anomaly_result
        
        return results
    
    def status(self) -> Dict:
        """系统状态"""
        return {
            'positions': self.position_manager.get_positions(),
            'watchlist_size': len(self.position_manager.get_watchlist()),
            'recent_alerts': len(self.position_manager.get_recent_alerts()),
            'config': self.config
        }

# ==================== 测试运行 ====================

def test_dual_track():
    """测试双轨系统"""
    print("="*60)
    print("� 双轨趋势监控系统测试")
    print("="*60)
    
    # 初始化
    controller = DualTrackController()
    
    # 添加测试持仓
    controller.position_manager.add_position('BTC/USDT', 50000, 0.1, 'momentum')
    controller.position_manager.add_position('ETH/USDT', 3000, 1.0, 'breakout')
    
    # 添加观察列表
    for sym in ['SOL/USDT', 'BNB/USDT', 'XRP/USDT']:
        controller.position_manager.add_to_watchlist(sym)
    
    print(f"\n📊 持仓: {controller.position_manager.get_positions()}")
    print(f"👀 观察: {controller.position_manager.get_watchlist()}")
    
    # 测试轨道1: 持仓趋势
    print("\n" + "="*60)
    print("🚂 轨道1: 持仓趋势监控")
    print("="*60)
    
    for i in range(3):
        result = controller.position_track.run_cycle()
        print(f"\n轮换 {i+1}: {result.get('symbol', 'N/A')}")
        if result.get('result', {}).get('best_models'):
            bm = result['result']['best_models'][0]
            print(f"   最佳模型: {bm['model']} | 概率: {bm['probability']:.2%}")
    
    # 完整持仓扫描
    print("\n📋 完整持仓扫描:")
    full_results = controller.position_track.run_full_cycle()
    for r in full_results:
        symbol = r['symbol']
        result = r['result']
        if result.get('best_models'):
            bm = result['best_models'][0]
            print(f"   {symbol}: {bm['model']} ({bm['probability']:.2%})")
    
    # 测试轨道2: 异常监控
    print("\n" + "="*60)
    print("🕸️ 轨道2: 异常监控")
    print("="*60)
    
    # 快速扫描
    print("\n🔍 快速扫描 (100个币种):")
    quick_result = controller.run_anomaly_track('quick')
    print(f"   发现异常: {quick_result.get('alerts_count', 0)}")
    
    # 显示系统状态
    print("\n" + "="*60)
    print("📊 系统状态")
    print("="*60)
    status = controller.status()
    print(f"   持仓数: {len(status['positions'])}")
    print(f"   观察数: {status['watchlist_size']}")
    print(f"   最近警报: {status['recent_alerts']}")
    
    print("\n✅ 双轨系统测试完成")
    
    return controller

def main():
    return test_dual_track()

if __name__ == '__main__':
    main()
