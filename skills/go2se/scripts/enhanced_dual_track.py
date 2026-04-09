#!/usr/bin/env python3
"""
双轨趋势监控系统 - 回测与持续观测增强版
轨道1: 持仓/指定币种 - 高密度检测
轨道2: 异常监控 - 回测 + 持续观测机制
"""

import requests
import time
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from collections import deque

# ==================== 数据结构 ====================

@dataclass
class BacktestConfig:
    """回测配置"""
    lookback_period: int = 24      # 回看周期(小时)
    min_data_points: int = 100     # 最小数据点
    timeframes: List[str] = field(default_factory=lambda: ['1h', '4h', '1d'])
    confidence_threshold: float = 0.6  # 置信度阈值
    backtest_method: str = 'rolling'  # rolling/signal

@dataclass
class ObservationState:
    """观测状态"""
    symbol: str
    first_seen: int
    last_update: int
    observations: int
    trend_changes: int
    current_trend: str
    trend_history: List[Dict]
    alerts_history: List[Dict]

@dataclass
class BacktestResult:
    """回测结果"""
    symbol: str
    period_hours: int
    data_points: int
    signals: List[Dict]
    performance: Dict
    recommendation: str
    confidence: float

@dataclass
class Position:
    symbol: str
    entry_price: float
    quantity: float
    entry_time: int
    stop_loss: float = 0.03
    take_profit: float = 0.05
    strategy: str = ""

# ==================== 回测系统 ====================

class BacktestEngine:
    """
    回测引擎
    从API获取历史数据进行回测分析
    """
    
    def __init__(self, config: BacktestConfig = None):
        self.config = config or BacktestConfig()
        self.exchanges = {}
        self._init_exchanges()
    
    def _init_exchanges(self):
        """初始化交易所"""
        try:
            import ccxt
            self.exchanges['binance'] = ccxt.binance({'enableRateLimit': True})
        except:
            pass
    
    def fetch_historical_data(self, symbol: str, timeframe: str = '1h', 
                             hours: int = None) -> List[Dict]:
        """获取历史数据用于回测"""
        hours = hours or self.config.lookback_period
        
        # 计算需要的K线数量
        timeframe_minutes = {'1m': 1, '5m': 5, '15m': 15, '1h': 60, '4h': 240, '1d': 1440}
        limit = (hours * 60 // timeframe_minutes.get(timeframe, 60)) + 10
        
        try:
            # 尝试ccxt
            ex = self.exchanges.get('binance')
            if ex:
                ohlcv = ex.fetch_ohlcv(symbol, timeframe, limit=min(limit, 500))
                return [
                    {
                        'timestamp': c[0],
                        'open': c[1],
                        'high': c[2],
                        'low': c[3],
                        'close': c[4],
                        'volume': c[5]
                    }
                    for c in ohlcv
                ]
        except:
            pass
        
        # 备用: 使用Binance REST API
        return self._fetch_from_rest(symbol, timeframe, hours)
    
    def _fetch_from_rest(self, symbol: str, timeframe: str, hours: int) -> List[Dict]:
        """从REST API获取历史数据"""
        # Binance klines API
        timeframe_map = {'1h': '1h', '4h': '4h', '1d': '1d'}
        tf = timeframe_map.get(timeframe, '1h')
        
        # 计算时间
        end_time = int(time.time() * 1000)
        start_time = end_time - (hours * 3600 * 1000)
        
        url = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={tf}&startTime={start_time}&endTime={end_time}&limit=500'
        
        try:
            r = requests.get(url, timeout=30)
            data = r.json()
            
            return [
                {
                    'timestamp': c[0],
                    'open': float(c[1]),
                    'high': float(c[2]),
                    'low': float(c[3]),
                    'close': float(c[4]),
                    'volume': float(c[5])
                }
                for c in data
            ]
        except:
            return []
    
    def run_backtest(self, symbol: str, trend_indicators: Dict = None) -> BacktestResult:
        """
        运行回测
        基于历史数据分析信号
        """
        # 获取历史数据
        historical_data = {}
        for tf in self.config.timeframes:
            data = self.fetch_historical_data(symbol, tf, self.config.lookback_period)
            historical_data[tf] = data
        
        # 合并数据点
        all_data = []
        for tf, data in historical_data.items():
            for d in data:
                d['timeframe'] = tf
            all_data.extend(data)
        
        # 按时间排序
        all_data.sort(key=lambda x: x['timestamp'])
        
        if len(all_data) < self.config.min_data_points:
            return BacktestResult(
                symbol=symbol,
                period_hours=self.config.lookback_period,
                data_points=len(all_data),
                signals=[],
                performance={'error': 'insufficient_data'},
                recommendation='HOLD',
                confidence=0
            )
        
        # 生成信号
        signals = self._generate_signals(all_data, trend_indicators)
        
        # 计算性能
        performance = self._calculate_performance(all_data, signals)
        
        # 生成建议
        recommendation, confidence = self._generate_recommendation(signals, performance)
        
        return BacktestResult(
            symbol=symbol,
            period_hours=self.config.lookback_period,
            data_points=len(all_data),
            signals=signals[-10:],  # 最近10个信号
            performance=performance,
            recommendation=recommendation,
            confidence=confidence
        )
    
    def _generate_signals(self, data: List[Dict], trend_indicators: Dict = None) -> List[Dict]:
        """生成交易信号"""
        signals = []
        
        if len(data) < 20:
            return signals
        
        closes = [d['close'] for d in data]
        volumes = [d['volume'] for d in data]
        
        # 简单移动平均
        sma_short = sum(closes[-10:]) / 10
        sma_long = sum(closes[-30:]) / 30
        
        # RSI
        deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        avg_gain = sum(gains[-14:]) / 14
        avg_loss = sum(losses[-14:]) / 14
        rsi = 100 - (100 / (1 + avg_gain / (avg_loss + 0.0001)))
        
        # 成交量变化
        vol_current = sum(volumes[-5:]) / 5
        vol_avg = sum(volumes[:-5]) / max(len(volumes) - 5, 1)
        vol_ratio = vol_current / (vol_avg + 1)
        
        # 生成信号
        timestamp = data[-1]['timestamp']
        
        # 买入信号
        if sma_short > sma_long and rsi < 70:
            signals.append({
                'timestamp': timestamp,
                'type': 'BUY',
                'price': closes[-1],
                'reason': f'SMA crossover, RSI={rsi:.1f}'
            })
        
        # 卖出信号
        elif sma_short < sma_long or rsi > 70:
            signals.append({
                'timestamp': timestamp,
                'type': 'SELL',
                'price': closes[-1],
                'reason': f'Reversal signal, RSI={rsi:.1f}'
            })
        
        # 成交量信号
        if vol_ratio > 2:
            signals.append({
                'timestamp': timestamp,
                'type': 'VOLUME_ALERT',
                'price': closes[-1],
                'reason': f'Volume spike {vol_ratio:.1f}x'
            })
        
        return signals
    
    def _calculate_performance(self, data: List[Dict], signals: List[Dict]) -> Dict:
        """计算性能指标"""
        if len(data) < 2:
            return {'error': 'insufficient_data'}
        
        closes = [d['close'] for d in data]
        
        # 收益率
        returns = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, len(closes))]
        
        return {
            'total_return': (closes[-1] - closes[0]) / closes[0],
            'volatility': float(np.std(returns)) if returns else 0,
            'max_drawdown': self._max_drawdown(closes),
            'signal_count': len(signals)
        }
    
    def _max_drawdown(self, prices: List[float]) -> float:
        """计算最大回撤"""
        peak = prices[0]
        max_dd = 0
        
        for p in prices:
            if p > peak:
                peak = p
            dd = (peak - p) / peak
            if dd > max_dd:
                max_dd = dd
        
        return max_dd
    
    def _generate_recommendation(self, signals: List[Dict], performance: Dict) -> tuple:
        """生成建议"""
        if not signals or performance.get('error'):
            return 'HOLD', 0.0
        
        last_signal = signals[-1]
        signal_type = last_signal['type']
        
        # 基于信号和性能计算置信度
        confidence = 0.5
        
        if signal_type == 'BUY':
            confidence = 0.6
            if performance.get('total_return', 0) > 0:
                confidence += 0.2
            if performance.get('max_drawdown', 1) < 0.1:
                confidence += 0.1
        
        elif signal_type == 'SELL':
            confidence = 0.7
        
        # 判断
        if confidence >= self.config.confidence_threshold:
            if signal_type == 'BUY':
                return 'BUY', confidence
            elif signal_type == 'SELL':
                return 'SELL', confidence
        
        return 'HOLD', confidence

import numpy as np

# ==================== 持续观测系统 ====================

class ContinuousObservation:
    """
    持续观测系统
    对异常信号进行持续跟踪观察
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {
            'min_observation_hours': 4,      # 最小观测时长(小时)
            'max_observation_hours': 24,     # 最大观测时长(小时)
            'trend_change_threshold': 2,     # 趋势变化阈值
            'strong_signal_threshold': 0.7,   # 强烈信号阈值
            'check_interval_minutes': 30,    # 检查间隔(分钟)
        }
        
        # 观测状态
        self.observations: Dict[str, ObservationState] = {}
        
        # 观测历史
        self.history = deque(maxlen=1000)
    
    def start_observation(self, symbol: str, initial_alert: Dict = None) -> ObservationState:
        """开始观测"""
        now = int(time.time())
        
        state = ObservationState(
            symbol=symbol,
            first_seen=now,
            last_update=now,
            observations=1,
            trend_changes=0,
            current_trend=initial_alert.get('trend', 'unknown') if initial_alert else 'unknown',
            trend_history=[{
                'timestamp': now,
                'trend': initial_alert.get('trend', 'unknown') if initial_alert else 'unknown',
                'change': initial_alert.get('change', 0)
            }],
            alerts_history=[initial_alert] if initial_alert else []
        )
        
        self.observations[symbol] = state
        self.history.append({
            'symbol': symbol,
            'action': 'START',
            'timestamp': now,
            'alert': initial_alert
        })
        
        return state
    
    def update_observation(self, symbol: str, update: Dict) -> ObservationState:
        """更新观测状态"""
        now = int(time.time())
        
        if symbol not in self.observations:
            return self.start_observation(symbol, update)
        
        state = self.observations[symbol]
        state.last_update = now
        state.observations += 1
        
        # 检测趋势变化
        new_trend = update.get('trend', state.current_trend)
        if new_trend != state.current_trend:
            state.trend_changes += 1
            state.current_trend = new_trend
            state.trend_history.append({
                'timestamp': now,
                'trend': new_trend,
                'change': update.get('change', 0)
            })
        
        # 添加警报历史
        state.alerts_history.append(update)
        
        return state
    
    def should_trigger(self, symbol: str) -> tuple:
        """
        判断是否触发
        返回: (should_trigger, reason, confidence)
        """
        if symbol not in self.observations:
            return False, 'No observation', 0
        
        state = self.observations[symbol]
        now = int(time.time())
        
        # 计算观测时长
        hours_elapsed = (now - state.first_seen) / 3600
        
        # 检查是否达到最小观测时长
        if hours_elapsed < self.config['min_observation_hours']:
            return False, f'Too early ({hours_elapsed:.1f}h)', 0
        
        # 检查是否超过最大观测时长
        if hours_elapsed > self.config['max_observation_hours']:
            return True, 'Max observation time reached', 0.8
        
        # 检查趋势变化次数
        if state.trend_changes >= self.config['trend_change_threshold']:
            return True, f'Trend changed {state.trend_changes} times', 0.7
        
        # 检查当前趋势强度
        if state.alerts_history:
            latest = state.alerts_history[-1]
            change = abs(latest.get('change', 0))
            
            if change > 20:  # 剧烈波动
                return True, f'Strong signal ({change}%)', 0.8
            elif change > 10 and hours_elapsed > self.config['min_observation_hours'] / 2:
                return True, f'Moderate signal ({change}%)', 0.6
        
        return False, 'Observation continuing', 0
    
    def get_observation_summary(self, symbol: str) -> Dict:
        """获取观测摘要"""
        if symbol not in self.observations:
            return {'status': 'not_observed'}
        
        state = self.observations[symbol]
        
        now = int(time.time())
        hours_elapsed = (now - state.first_seen) / 3600
        
        should_trigger, reason, confidence = self.should_trigger(symbol)
        
        return {
            'symbol': symbol,
            'status': 'TRIGGER' if should_trigger else 'OBSERVING',
            'hours_elapsed': round(hours_elapsed, 1),
            'observations': state.observations,
            'trend_changes': state.trend_changes,
            'current_trend': state.current_trend,
            'trigger_reason': reason,
            'confidence': confidence,
            'trend_history': state.trend_history[-5:]
        }
    
    def stop_observation(self, symbol: str, reason: str = 'manual'):
        """停止观测"""
        if symbol in self.observations:
            del self.observations[symbol]
            
            self.history.append({
                'symbol': symbol,
                'action': 'STOP',
                'reason': reason,
                'timestamp': int(time.time())
            })

# ==================== 增强版双轨系统 ====================

class EnhancedDualTrackSystem:
    """
    增强版双轨系统
    - 轨道1: 高密度持仓检测
    - 轨道2: 回测 + 持续观测
    """
    
    def __init__(self, config: Dict = None):
        # 回测配置
        self.backtest_config = BacktestConfig(
            lookback_period=config.get('lookback_hours', 24) if config else 24,
            confidence_threshold=config.get('confidence_threshold', 0.6) if config else 0.6
        )
        
        # 观测配置
        self.observation_config = config.get('observation', {}) if config else {}
        
        # 初始化系统
        self.backtest_engine = BacktestEngine(self.backtest_config)
        self.observation_system = ContinuousObservation(self.observation_config)
        
        # 持仓管理
        self.positions: Dict[str, Position] = {}
        self.watchlist: List[str] = []
        
        # 高密度检测配置
        self.position_check_interval = 60  # 60秒检测一次持仓
        
        # 缓存
        self.last_position_check = 0
        self.last_observation_check = 0
    
    # ===== 轨道1: 持仓高密度检测 =====
    
    def check_positions_high_frequency(self) -> List[Dict]:
        """高频率检测持仓"""
        now = int(time.time())
        
        # 检查间隔
        if now - self.last_position_check < self.position_check_interval:
            return []
        
        self.last_position_check = now
        
        results = []
        
        for symbol, pos in self.positions.items():
            # 获取当前价格
            current_price = self._get_current_price(symbol)
            
            if not current_price:
                continue
            
            # 计算盈亏
            pnl = (current_price - pos.entry_price) / pos.entry_price
            
            # 检查止损/止盈
            action = None
            
            if pnl <= -pos.stop_loss:
                action = 'STOP_LOSS'
            elif pnl >= pos.take_profit:
                action = 'TAKE_PROFIT'
            
            results.append({
                'symbol': symbol,
                'entry_price': pos.entry_price,
                'current_price': current_price,
                'pnl': pnl,
                'action': action,
                'timestamp': now
            })
            
            # 执行操作
            if action:
                print(f"\n⚠️ {action}: {symbol} @ {current_price} (PnL: {pnl:.2%})")
        
        return results
    
    def _get_current_price(self, symbol: str) -> Optional[float]:
        """获取当前价格"""
        # 移除斜杠
        sym = symbol.replace('/', '')
        
        try:
            url = f'https://api.binance.com/api/v3/ticker/price?symbol={sym}'
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                return float(r.json()['price'])
        except:
            pass
        
        return None
    
    # ===== 轨道2: 回测 + 持续观测 =====
    
    def analyze_with_backtest(self, symbol: str, alert_data: Dict = None) -> Dict:
        """
        回测分析
        获取历史数据，进行回测，生成建议
        """
        print(f"\n🔄 回测分析: {symbol}")
        
        # 运行回测
        trend_indicators = alert_data.get('indicators', {}) if alert_data else None
        result = self.backtest_engine.run_backtest(symbol, trend_indicators)
        
        print(f"   数据点: {result.data_points}")
        print(f"   信号数: {len(result.signals)}")
        print(f"   建议: {result.recommendation} (置信度: {result.confidence:.1%})")
        
        if result.performance and 'error' not in result.performance:
            print(f"   收益率: {result.performance.get('total_return', 0):.2%}")
            print(f"   最大回撤: {result.performance.get('max_drawdown', 0):.2%}")
        
        return asdict(result)
    
    def start_observation_for_alert(self, symbol: str, alert: Dict) -> Dict:
        """为警报启动持续观测"""
        state = self.observation_system.start_observation(symbol, alert)
        
        # 获取初始回测
        backtest = self.analyze_with_backtest(symbol, alert)
        
        return {
            'observation': self.observation_system.get_observation_summary(symbol),
            'backtest': backtest
        }
    
    def update_observation(self, symbol: str, update: Dict) -> Dict:
        """更新观测"""
        self.observation_system.update_observation(symbol, update)
        
        # 定期重新回测
        state = self.observation_system.observations.get(symbol)
        if state and state.observations % 4 == 0:  # 每4次更新回测一次
            backtest = self.analyze_with_backtest(symbol, update)
            return {'observation': self.observation_system.get_observation_summary(symbol), 'backtest': backtest}
        
        return {'observation': self.observation_system.get_observation_summary(symbol)}
    
    def check_observations(self) -> List[Dict]:
        """检查所有观测是否触发"""
        triggered = []
        
        for symbol in list(self.observation_system.observations.keys()):
            should_trigger, reason, confidence = self.observation_system.should_trigger(symbol)
            
            if should_trigger:
                # 获取完整分析
                backtest = self.analyze_with_backtest(symbol)
                
                triggered.append({
                    'symbol': symbol,
                    'reason': reason,
                    'confidence': confidence,
                    'backtest': backtest,
                    'observation': self.observation_system.get_observation_summary(symbol)
                })
        
        return triggered
    
    # ===== 主流程 =====
    
    def run_full_cycle(self, alert_symbols: List[str] = None) -> Dict:
        """运行完整周期"""
        results = {
            'timestamp': int(time.time()),
            'position_checks': [],
            'observations': {},
            'triggered': []
        }
        
        # 轨道1: 持仓检测
        print("\n" + "="*50)
        print("🚂 轨道1: 持仓高密度检测")
        print("="*50)
        
        position_results = self.check_positions_high_frequency()
        results['position_checks'] = position_results
        
        for r in position_results:
            print(f"   {r['symbol']}: {r['pnl']:.2%} - {r.get('action', 'HOLDING')}")
        
        # 轨道2: 异常监控 + 回测 + 观测
        print("\n" + "="*50)
        print("🕸️ 轨道2: 回测 + 持续观测")
        print("="*50)
        
        # 检查观测是否触发
        triggered = self.check_observations()
        
        if triggered:
            print(f"\n⚠️ 触发信号: {len(triggered)}")
            for t in triggered:
                print(f"   {t['symbol']}: {t['reason']} (置信度: {t['confidence']:.1%})")
                results['triggered'].append(t)
        
        results['observations'] = {
            'count': len(self.observation_system.observations),
            'list': [
                self.observation_system.get_observation_summary(s)
                for s in list(self.observation_system.observations.keys())[:5]
            ]
        }
        
        return results
    
    # ===== 持仓管理 =====
    
    def add_position(self, symbol: str, entry_price: float, quantity: float,
                   strategy: str = 'momentum', stop_loss: float = 0.03, take_profit: float = 0.05):
        """添加持仓"""
        self.positions[symbol] = Position(
            symbol=symbol,
            entry_price=entry_price,
            quantity=quantity,
            entry_time=int(time.time()),
            stop_loss=stop_loss,
            take_profit=take_profit,
            strategy=strategy
        )
    
    def close_position(self, symbol: str):
        """平仓"""
        if symbol in self.positions:
            del self.positions[symbol]
    
    def add_to_watchlist(self, symbol: str):
        """添加到观察列表"""
        if symbol not in self.watchlist:
            self.watchlist.append(symbol)

# ===== 测试 =====

def test():
    print("="*60)
    print("🧪 测试增强版双轨系统")
    print("="*60)
    
    # 初始化
    config = {
        'lookback_hours': 24,
        'confidence_threshold': 0.6,
        'observation': {
            'min_observation_hours': 2,
            'max_observation_hours': 12,
            'trend_change_threshold': 2,
            'strong_signal_threshold': 0.7
        }
    }
    
    system = EnhancedDualTrackSystem(config)
    
    # 添加持仓
    system.add_position('BTC/USDT', 50000, 0.1, 'momentum', 0.03, 0.08)
    system.add_position('ETH/USDT', 3000, 1.0, 'breakout', 0.05, 0.10)
    
    print(f"\n📊 持仓: {list(system.positions.keys())}")
    
    # 添加观测
    system.start_observation_for_alert('HYPERFDUSD', {
        'change': 242,
        'trend': 'reversal',
        'source': 'binance'
    })
    
    # 运行周期
    results = system.run_full_cycle()
    
    # 显示观测状态
    print("\n📊 观测状态:")
    for sym, obs in system.observation_system.observations.items():
        summary = system.observation_system.get_observation_summary(sym)
        print(f"   {sym}: {summary['status']} ({summary.get('hours_elapsed', 0)}h)")
    
    print("\n✅ 测试完成")
    
    return system

if __name__ == '__main__':
    test()
