#!/usr/bin/env python3
"""
趋势模型匹配器 - Trend Pattern Matcher
从市场数据流中提取形态，与声纳库趋势模型比对，生成概率输出并触发策略

功能:
1. 从API端口获取市场数据(指定或扫描)
2. 去噪音处理和数据清洗
3. 提取时间-价格形态特征
4. 与趋势模型库比对分析
5. 广泛匹配 -> 锁定目标 -> 概率输出
6. 阈值判断 -> 触发策略调用
"""

import json
import time
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from collections import deque
import ccxt
import requests
import socket
import threading

# ==================== 数据结构 ====================

@dataclass
class MarketData:
    """市场数据结构"""
    symbol: str
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    
@dataclass
class PatternFeatures:
    """形态特征"""
    trend_direction: float      # 趋势方向 (-1 to 1)
    volatility: float           # 波动率
    momentum: float             # 动量
    volume_profile: float       # 成交量特征
    price_acceleration: float   # 价格加速度
    support_resistance: float   # 支撑阻力强度
    consolidation: float        # 震荡程度
    
@dataclass
class TrendMatch:
    """趋势匹配结果"""
    model_name: str
    model_type: str
    probability: float          # 匹配概率 0-1
    confidence: float           # 置信度 0-10
    matched_indicators: List[str]
    timeframes: Dict[str, bool]
    direction: str              # 'long', 'short', 'neutral'
    features: PatternFeatures
    
@dataclass
class StrategyTrigger:
    """策略触发信号"""
    strategy_name: str
    models: List[str]           # 触发模型组合
    probability: float          # 总体概率
    direction: str
    position_size: float
    entry_price: float
    stop_loss: float
    take_profit: float
    timeframe: str
    metadata: Dict = field(default_factory=dict)

# ==================== 趋势模型库 ====================

class TrendModelLibrary:
    """趋势模型库 - 本地化实现"""
    
    def __init__(self, db_path='skills/go2se/data/trend_database.json'):
        self.db_path = db_path
        self.models = self.load_models()
        self.model_implementations = self._init_implementations()
    
    def load_models(self) -> Dict:
        """加载趋势模型"""
        try:
            with open(self.db_path, 'r') as f:
                return json.load(f)
        except:
            return self._default_models()
    
    def _default_models(self) -> Dict:
        """默认趋势模型"""
        return {
            "crypto_trends": {
                "momentum": {
                    "name": "动量趋势",
                    "indicators": ["RSI", "MACD", "EMA", "BB"],
                    "pattern": "continuous_trend",
                    "timeframes": {"1m": True, "5m": True, "15m": True}
                },
                "breakout": {
                    "name": "突破趋势", 
                    "indicators": ["Volume", "BB", "Price_Change"],
                    "pattern": "breakout",
                    "timeframes": {"1m": True, "5m": True, "15m": True}
                },
                "reversal": {
                    "name": "反转趋势",
                    "indicators": ["RSI", "Divergence", "BB"],
                    "pattern": "reversal",
                    "timeframes": {"5m": True, "15m": True, "1h": True}
                }
            }
        }
    
    def _init_implementations(self) -> Dict:
        """初始化趋势模型实现"""
        return {
            "momentum": self._momentum_pattern,
            "breakout": self._breakout_pattern,
            "reversal": self._reversal_pattern,
            "whale_accumulation": self._whale_pattern,
            "volume_spike": self._volume_pattern,
            "trend_exhaustion": self._exhaustion_pattern,
            "consolidation_break": self._consolidation_pattern,
            "divergence": self._divergence_pattern,
        }
    
    # ==================== 形态识别函数 ====================
    
    def _momentum_pattern(self, features: PatternFeatures, indicators: Dict) -> float:
        """动量趋势识别"""
        score = 0
        
        # 趋势方向一致性
        if abs(features.trend_direction) > 0.5:
            score += 0.3
        
        # RSI 动量
        rsi = indicators.get('rsi', 50)
        if features.trend_direction > 0 and 40 < rsi < 70:
            score += 0.2
        elif features.trend_direction < 0 and 30 < rsi < 60:
            score += 0.2
        
        # MACD 方向
        macd = indicators.get('macd', 0)
        if features.trend_direction > 0 and macd > 0:
            score += 0.2
        elif features.trend_direction < 0 and macd < 0:
            score += 0.2
        
        # 动量强度
        if features.momentum > 0.3:
            score += 0.2
        elif features.momentum < -0.3:
            score += 0.2
            
        return min(1.0, score)
    
    def _breakout_pattern(self, features: PatternFeatures, indicators: Dict) -> float:
        """突破趋势识别"""
        score = 0
        
        # 成交量激增
        if features.volume_profile > 1.5:
            score += 0.4
        
        # 波动率上升
        if features.volatility > 0.5:
            score += 0.2
        
        # 突破支撑/阻力
        if features.support_resistance > 0.7:
            score += 0.3
        
        # 价格加速
        if features.price_acceleration > 0.3:
            score += 0.1
            
        return min(1.0, score)
    
    def _reversal_pattern(self, features: PatternFeatures, indicators: Dict) -> float:
        """反转趋势识别"""
        score = 0
        
        # RSI 超卖/超买
        rsi = indicators.get('rsi', 50)
        if rsi < 30 or rsi > 70:
            score += 0.3
        
        # 动量减弱
        if abs(features.momentum) < 0.2:
            score += 0.2
        
        # 震荡整理
        if features.consolidation > 0.6:
            score += 0.2
        
        # 背离信号 (价格vs动量)
        if features.trend_direction * features.momentum < 0:
            score += 0.3
            
        return min(1.0, score)
    
    def _whale_pattern(self, features: PatternFeatures, indicators: Dict) -> float:
        """巨鲸积累识别"""
        score = 0
        
        # 成交量异常
        if features.volume_profile > 2.0:
            score += 0.4
        
        # 低价位积累
        if features.trend_direction < 0 and features.momentum > -0.1:
            score += 0.3
        
        # 波动率降低
        if features.volatility < 0.3:
            score += 0.2
            
        return min(1.0, score)
    
    def _volume_pattern(self, features: PatternFeatures, indicators: Dict) -> float:
        """成交量模式识别"""
        if features.volume_profile > 1.8:
            return 0.9
        elif features.volume_profile > 1.3:
            return 0.6
        return 0.2
    
    def _exhaustion_pattern(self, features: PatternFeatures, indicators: Dict) -> float:
        """趋势衰竭识别"""
        score = 0
        
        # 动量背离
        if features.trend_direction * features.momentum < 0:
            score += 0.4
        
        # 波动率极端
        if features.volatility > 0.8:
            score += 0.3
        
        # RSI 极端
        rsi = indicators.get('rsi', 50)
        if rsi < 20 or rsi > 80:
            score += 0.3
            
        return min(1.0, score)
    
    def _consolidation_pattern(self, features: PatternFeatures, indicators: Dict) -> float:
        """震荡突破识别"""
        score = 0
        
        if features.consolidation > 0.5:
            score += 0.4
        
        if 0.3 < features.volatility < 0.6:
            score += 0.3
            
        return min(1.0, score)
    
    def _divergence_pattern(self, features: PatternFeatures, indicators: Dict) -> float:
        """背离识别"""
        if features.trend_direction * features.momentum < 0:
            return 0.8
        return 0.2
    
    def get_all_models(self, market_type='crypto') -> Dict:
        """获取所有趋势模型"""
        return self.models.get(f'{market_type}_trends', {})
    
    def match_models(self, features: PatternFeatures, indicators: Dict, 
                    market_type='crypto', timeframes=['5m', '15m']) -> List[TrendMatch]:
        """匹配所有趋势模型"""
        matches = []
        models = self.get_all_models(market_type)
        
        for model_name, model_data in models.items():
            # 获取模型的时间框架配置
            model_tfs = model_data.get('timeframes', {})
            
            # 检查是否在支持的时间框架内
            supported = any(tf in model_tfs for tf in timeframes)
            if not supported:
                continue
            
            # 获取形态识别函数
            pattern_fn = self.model_implementations.get(model_name)
            if not pattern_fn:
                pattern_fn = self.model_implementations.get('momentum')  # 默认
            
            # 计算匹配概率
            probability = pattern_fn(features, indicators)
            
            if probability > 0.2:  # 最低阈值
                # 确定方向
                direction = 'neutral'
                if features.trend_direction > 0.3:
                    direction = 'long'
                elif features.trend_direction < -0.3:
                    direction = 'short'
                
                # 计算置信度 (0-10)
                confidence = probability * 10
                
                matches.append(TrendMatch(
                    model_name=model_name,
                    model_type=model_data.get('name', model_name),
                    probability=probability,
                    confidence=confidence,
                    matched_indicators=model_data.get('indicators', []),
                    timeframes=model_tfs,
                    direction=direction,
                    features=features
                ))
        
        # 按概率排序
        matches.sort(key=lambda x: x.probability, reverse=True)
        return matches

# ==================== 数据获取器 ====================

class MarketDataFetcher:
    """市场数据获取器"""
    
    def __init__(self, api_config: Optional[Dict] = None):
        self.api_config = api_config or self._default_apis()
        self.exchanges = {}
        self._init_exchanges()
    
    def _default_apis(self) -> Dict:
        """默认API配置"""
        return {
            'binance': {'enabled': True, 'priority': 1},
            'bybit': {'enabled': True, 'priority': 2},
            'okx': {'enabled': True, 'priority': 3}
        }
    
    def _init_exchanges(self):
        """初始化交易所连接"""
        exchange_ids = ['binance', 'bybit', 'okx', 'kucoin']
        
        for eid in exchange_ids:
            try:
                exchange_class = getattr(ccxt, eid, None)
                if exchange_class:
                    self.exchanges[eid] = exchange_class({
                        'enableRateLimit': True,
                        'options': {'defaultType': 'spot'}
                    })
            except Exception as e:
                print(f"Failed to init {eid}: {e}")
    
    def scan_api_ports(self, port_range=(5000, 5010)) -> List[Dict]:
        """扫描本地API端口"""
        available_apis = []
        
        for port in range(port_range[0], port_range[1]):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                
                if result == 0:
                    # 尝试获取端口信息
                    available_apis.append({
                        'port': port,
                        'type': 'local',
                        'status': 'available'
                    })
            except:
                pass
        
        return available_apis
    
    def fetch_ohlcv(self, symbol: str, timeframe: str = '5m', 
                   limit: int = 100, exchange: str = 'binance') -> List[MarketData]:
        """获取K线数据"""
        try:
            ex = self.exchanges.get(exchange)
            if not ex:
                return []
            
            ohlcv = ex.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            return [
                MarketData(
                    symbol=symbol,
                    timestamp=int(c[0]),
                    open=float(c[1]),
                    high=float(c[2]),
                    low=float(c[3]),
                    close=float(c[4]),
                    volume=float(c[5])
                )
                for c in ohlcv
            ]
        except Exception as e:
            print(f"Fetch error: {e}")
            return []
    
    def fetch_multi_timeframe(self, symbol: str) -> Dict[str, List[MarketData]]:
        """获取多时间框架数据"""
        timeframes = ['1m', '5m', '15m', '1h', '4h']
        result = {}
        
        for tf in timeframes:
            data = self.fetch_ohlcv(symbol, tf, limit=100)
            if data:
                result[tf] = data
        
        return result

# ==================== 数据去噪音 ====================

class NoiseReducer:
    """数据去噪音处理"""
    
    def __init__(self, window_size: int = 5):
        self.window_size = window_size
    
    def moving_average(self, data: List[float], window: int = None) -> List[float]:
        """移动平均去噪音"""
        w = window or self.window_size
        if len(data) < w:
            return data
        
        result = []
        for i in range(len(data)):
            start = max(0, i - w + 1)
            result.append(sum(data[start:i+1]) / (i - start + 1))
        
        return result
    
    def exponential_moving_average(self, data: List[float], 
                                   alpha: float = 0.3) -> List[float]:
        """指数移动平均"""
        if not data:
            return []
        
        result = [data[0]]
        for i in range(1, len(data)):
            ema = alpha * data[i] + (1 - alpha) * result[-1]
            result.append(ema)
        
        return result
    
    def kalman_filter(self, measurements: List[float], 
                     process_variance: float = 1e-5,
                     measurement_variance: float = 1e-3) -> List[float]:
        """卡尔曼滤波去噪音"""
        if not measurements:
            return []
        
        # 卡尔曼滤波
        posteriors = []
        posterior_cov = 1.0
        
        for measurement in measurements:
            # 预测步骤
            prior = posterior_cov + process_variance
            
            # 更新步骤
            kalman_gain = prior / (prior + measurement_variance)
            posterior = measurement * kalman_gain + posteriors[-1] * (1 - kalman_gain) if posteriors else measurement
            posterior_cov = (1 - kalman_gain) * prior
            
            posteriors.append(posterior)
        
        return posteriors
    
    def outliers_removal(self, data: List[float], threshold: float = 2.0) -> List[float]:
        """异常值移除"""
        if len(data) < 3:
            return data
        
        # 计算标准差
        mean = np.mean(data)
        std = np.std(data)
        
        # 过滤异常值
        return [d for d in data if abs(d - mean) < threshold * std]
    
    def denoise(self, data: List[float], method: str = 'ema') -> List[float]:
        """综合去噪音"""
        if method == 'ma':
            return self.moving_average(data)
        elif method == 'ema':
            return self.exponential_moving_average(data)
        elif method == 'kalman':
            return self.kalman_filter(data)
        else:
            return data

# ==================== 特征提取器 ====================

class FeatureExtractor:
    """从市场数据中提取形态特征"""
    
    def __init__(self):
        self.noise_reducer = NoiseReducer()
    
    def extract(self, data: List[MarketData], indicators: Dict = None) -> PatternFeatures:
        """提取形态特征"""
        if len(data) < 10:
            return PatternFeatures(0, 0, 0, 0, 0, 0, 0)
        
        closes = np.array([d.close for d in data])
        highs = np.array([d.high for d in data])
        lows = np.array([d.low for d in data])
        volumes = np.array([d.volume for d in data])
        times = np.array([d.timestamp for d in data])
        
        # 去噪音
        closes_clean = self.noise_reducer.denoise(closes.tolist(), 'ema')
        closes_clean = np.array(closes_clean)
        
        # 1. 趋势方向 (-1 to 1)
        trend_direction = self._calc_trend_direction(closes_clean)
        
        # 2. 波动率
        volatility = self._calc_volatility(closes_clean)
        
        # 3. 动量
        momentum = self._calc_momentum(closes_clean)
        
        # 4. 成交量特征
        volume_profile = self._calc_volume_profile(volumes)
        
        # 5. 价格加速度
        price_acceleration = self._calc_acceleration(closes_clean, times)
        
        # 6. 支撑/阻力强度
        support_resistance = self._calc_sr_strength(highs, lows, closes_clean)
        
        # 7. 震荡程度
        consolidation = self._calc_consolidation(highs, lows, closes_clean)
        
        return PatternFeatures(
            trend_direction=trend_direction,
            volatility=volatility,
            momentum=momentum,
            volume_profile=volume_profile,
            price_acceleration=price_acceleration,
            support_resistance=support_resistance,
            consolidation=consolidation
        )
    
    def _calc_trend_direction(self, prices: np.ndarray) -> float:
        """计算趋势方向"""
        if len(prices) < 2:
            return 0
        
        # 使用线性回归
        x = np.arange(len(prices))
        slope, _ = np.polyfit(x, prices, 1)
        
        # 归一化到 -1 到 1
        mean_price = np.mean(prices)
        if mean_price == 0:
            return 0
        
        normalized_slope = slope / mean_price
        return np.clip(normalized_slope * 100, -1, 1)
    
    def _calc_volatility(self, prices: np.ndarray) -> float:
        """计算波动率"""
        if len(prices) < 2:
            return 0
        
        returns = np.diff(prices) / prices[:-1]
        return float(np.std(returns)) if len(returns) > 0 else 0
    
    def _calc_momentum(self, prices: np.ndarray) -> float:
        """计算动量"""
        if len(prices) < 10:
            return 0
        
        # RSI 动量
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-14:]) if len(gains) >= 14 else np.mean(gains)
        avg_loss = np.mean(losses[-14:]) if len(losses) >= 14 else np.mean(losses)
        
        if avg_loss == 0:
            return 1
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        # 归一化到 -1 到 1
        return (rsi - 50) / 50
    
    def _calc_volume_profile(self, volumes: np.ndarray) -> float:
        """计算成交量特征"""
        if len(volumes) < 2:
            return 1
        
        current_vol = np.mean(volumes[-5:])
        avg_vol = np.mean(volumes[:-5])
        
        if avg_vol == 0:
            return 1
        
        return current_vol / avg_vol
    
    def _calc_acceleration(self, prices: np.ndarray, times: np.ndarray) -> float:
        """计算价格加速度"""
        if len(prices) < 3:
            return 0
        
        # 二阶导数近似
        returns = np.diff(prices) / prices[:-1]
        acceleration = np.diff(returns)
        
        return float(np.mean(acceleration)) if len(acceleration) > 0 else 0
    
    def _calc_sr_strength(self, highs: np.ndarray, lows: np.ndarray, 
                          closes: np.ndarray) -> float:
        """计算支撑阻力强度"""
        if len(highs) < 2:
            return 0
        
        # 计算价格触及高点和低点的次数
        current_price = closes[-1]
        
        resistance_touches = np.sum(highs > current_price * 1.01)
        support_touches = np.sum(lows < current_price * 0.99)
        
        total = resistance_touches + support_touches
        if total == 0:
            return 0.5
        
        return min(1.0, total / 10)
    
    def _calc_consolidation(self, highs: np.ndarray, lows: np.ndarray,
                           closes: np.ndarray) -> float:
        """计算震荡程度"""
        if len(highs) < 2:
            return 0
        
        # 价格的窄幅震荡
        price_range = highs[-20:] - lows[-20:]
        avg_range = np.mean(price_range)
        
        if avg_range == 0:
            return 0
        
        # 相对于价格的震荡
        avg_price = np.mean(closes[-20:])
        consolidation = avg_range / avg_price
        
        return min(1.0, consolidation * 10)
    
    def calculate_indicators(self, data: List[MarketData]) -> Dict:
        """计算技术指标"""
        if len(data) < 30:
            return {}
        
        closes = np.array([d.close for d in data])
        volumes = np.array([d.volume for d in data])
        
        # RSI
        deltas = np.diff(closes)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        avg_gain = np.mean(gains[-14:])
        avg_loss = np.mean(losses[-14:])
        rsi = 100 - (100 / (1 + avg_gain / (avg_loss + 0.0001))) if avg_loss > 0 else 50
        
        # MACD
        ema12 = self._ema(closes, 12)
        ema26 = self._ema(closes, 26)
        macd = ema12 - ema26
        signal = self._ema([macd] * 26, 9)
        macd_hist = macd - signal
        
        # EMA
        ema20 = self._ema(closes, 20)
        ema50 = self._ema(closes, 50)
        
        # Bollinger Bands
        sma20 = np.mean(closes[-20:])
        std20 = np.std(closes[-20:])
        bb_upper = sma20 + 2 * std20
        bb_lower = sma20 - 2 * std20
        
        # Volume MA
        vol_ma = np.mean(volumes[-20:])
        
        return {
            'rsi': rsi,
            'macd': macd,
            'macd_hist': macd_hist,
            'ema20': ema20,
            'ema50': ema50,
            'bb_upper': bb_upper,
            'bb_lower': bb_lower,
            'bb_middle': sma20,
            'vol_ma': vol_ma,
            'vol_ratio': volumes[-1] / vol_ma if vol_ma > 0 else 1,
            'price': closes[-1],
            'sma20': sma20
        }
    
    def _ema(self, prices: List[float], period: int) -> float:
        """计算EMA"""
        prices = np.array(prices)
        if len(prices) < period:
            return np.mean(prices)
        
        alpha = 2 / (period + 1)
        ema = prices[0]
        for p in prices[1:]:
            ema = alpha * p + (1 - alpha) * ema
        return ema

# ==================== 趋势匹配器核心 ====================

class TrendPatternMatcher:
    """趋势形态匹配器 - 主类"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.library = TrendModelLibrary()
        self.fetcher = MarketDataFetcher()
        self.extractor = FeatureExtractor()
        
        # 配置参数
        self.min_probability = self.config.get('min_probability', 0.3)
        self.min_confidence = self.config.get('min_confidence', 4)
        self.max_models = self.config.get('max_models', 5)
        
    def analyze_symbol(self, symbol: str, timeframes: List[str] = None) -> Dict:
        """分析单个交易对"""
        if timeframes is None:
            timeframes = ['5m', '15m', '1h']
        
        results = {
            'symbol': symbol,
            'timestamp': int(time.time()),
            'matches': [],
            'best_models': [],
            'trigger': None
        }
        
        # 获取多时间框架数据
        multi_tf_data = self.fetcher.fetch_multi_timeframe(symbol)
        
        if not multi_tf_data:
            return results
        
        # 分析每个时间框架
        all_matches = []
        
        for tf, data in multi_tf_data.items():
            if len(data) < 30:
                continue
            
            # 计算指标
            indicators = self.extractor.calculate_indicators(data)
            
            # 提取特征
            features = self.extractor.extract(data, indicators)
            
            # 匹配趋势模型
            matches = self.library.match_models(
                features, indicators, 
                market_type='crypto', 
                timeframes=[tf]
            )
            
            for m in matches:
                m.timeframe = tf
            
            all_matches.extend(matches)
        
        # 按概率排序
        all_matches.sort(key=lambda x: x.probability, reverse=True)
        results['matches'] = [
            {
                'model': m.model_name,
                'type': m.model_type,
                'probability': m.probability,
                'confidence': m.confidence,
                'direction': m.direction,
                'timeframe': getattr(m, 'timeframe', 'unknown')
            }
            for m in all_matches[:self.max_models]
        ]
        
        # 锁定最佳模型
        if all_matches:
            results['best_models'] = self._select_best_models(all_matches)
            
            # 检查是否触发策略
            trigger = self._check_trigger(results['best_models'])
            if trigger:
                results['trigger'] = trigger
        
        return results
    
    def _select_best_models(self, matches: List[TrendMatch]) -> List[Dict]:
        """选择最佳模型组合"""
        # 聚合相同模型
        model_probs = {}
        for m in matches:
            if m.model_name not in model_probs:
                model_probs[m.model_name] = []
            model_probs[m.model_name].append(m.probability)
        
        # 取平均概率
        best = []
        for name, probs in model_probs.items():
            avg_prob = sum(probs) / len(probs)
            best.append({
                'model': name,
                'probability': avg_prob,
                'occurrences': len(probs)
            })
        
        best.sort(key=lambda x: x['probability'], reverse=True)
        return best[:3]
    
    def _check_trigger(self, best_models: List[Dict]) -> Optional[StrategyTrigger]:
        """检查是否触发策略"""
        if not best_models or best_models[0]['probability'] < self.min_probability:
            return None
        
        # 获取最佳模型
        best = best_models[0]
        
        # 检查置信度
        model_data = self.library.get_all_models().get(best['model'], {})
        min_conf = 4  # 默认
        
        for tf, config in model_data.get('timeframes', {}).items():
            if config.get('execute', False):
                min_conf = config.get('min_confidence', min_conf)
                break
        
        if best['probability'] * 10 < min_conf:
            return None
        
        # 触发策略
        return StrategyTrigger(
            strategy_name=f"trend_{best['model']}",
            models=[b['model'] for b in best_models],
            probability=best['probability'],
            direction='long' if best_models[0].get('probability', 0) > 0.5 else 'neutral',
            position_size=self._calc_position_size(best['probability']),
            entry_price=0,  # 实时获取
            stop_loss=0.02,
            take_profit=0.05,
            timeframe='5m'
        )
    
    def _calc_position_size(self, probability: float) -> float:
        """根据概率计算仓位大小"""
        # 概率越高，仓位越大
        base_size = 0.05
        return min(0.25, base_size + probability * 0.2)

# ==================== 策略触发器 ====================

class StrategyTriggerSystem:
    """策略触发系统"""
    
    def __init__(self, matcher: TrendPatternMatcher):
        self.matcher = matcher
        self.strategies = self._load_strategies()
    
    def _load_strategies(self) -> Dict:
        """加载可用策略"""
        return {
            'trend_momentum': {
                'min_models': 1,
                'min_probability': 0.4,
                'required_indicators': ['RSI', 'MACD']
            },
            'trend_breakout': {
                'min_models': 1,
                'min_probability': 0.5,
                'required_indicators': ['Volume', 'BB']
            },
            'trend_reversal': {
                'min_models': 1,
                'min_probability': 0.45,
                'required_indicators': ['RSI', 'Divergence']
            }
        }
    
    def evaluate(self, analysis_result: Dict) -> Optional[StrategyTrigger]:
        """评估是否触发策略"""
        if not analysis_result.get('trigger'):
            return None
        
        trigger = analysis_result['trigger']
        models = analysis_result.get('best_models', [])
        
        # 遍历策略
        for strat_name, strat_config in self.strategies.items():
            # 检查模型数量
            if len(models) < strat_config['min_models']:
                continue
            
            # 检查概率
            max_prob = max(m['probability'] for m in models)
            if max_prob < strat_config['min_probability']:
                continue
            
            # 匹配成功
            trigger.strategy_name = strat_name
            return trigger
        
        return None
    
    def execute_trigger(self, trigger: StrategyTrigger, 
                       current_price: float) -> Dict:
        """执行策略触发"""
        trigger.entry_price = current_price
        
        # 计算止损止盈
        if trigger.direction == 'long':
            trigger.stop_loss = current_price * (1 - trigger.stop_loss)
            trigger.take_profit = current_price * (1 + trigger.take_profit)
        else:
            trigger.stop_loss = current_price * (1 + trigger.stop_loss)
            trigger.take_profit = current_price * (1 - trigger.take_profit)
        
        return {
            'status': 'ready',
            'trigger': trigger,
            'message': f"策略触发: {trigger.strategy_name}, 方向: {trigger.direction}, 概率: {trigger.probability:.2%}"
        }

# ==================== 主脚本入口 ====================

def run_analysis(symbols: List[str] = None, 
                config: Dict = None,
                trigger_callback: Optional[callable] = None):
    """
    运行趋势模型分析
    
    Args:
        symbols: 要分析的交易对列表
        config: 配置参数
        trigger_callback: 触发策略时的回调函数
    """
    print("=" * 60)
    print("🚀 趋势模型匹配器启动")
    print("=" * 60)
    
    # 默认交易对
    if symbols is None:
        symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT']
    
    # 初始化
    matcher = TrendPatternMatcher(config or {})
    trigger_system = StrategyTriggerSystem(matcher)
    
    results = []
    
    for symbol in symbols:
        print(f"\n📊 分析: {symbol}")
        
        try:
            result = matcher.analyze_symbol(symbol)
            
            if result['best_models']:
                print(f"   最佳模型: {result['best_models'][0]['model']}")
                print(f"   匹配概率: {result['best_models'][0]['probability']:.2%}")
                
                if result.get('trigger'):
                    print(f"   ⚡ 策略触发: {result['trigger'].strategy_name}")
                    
                    # 评估并执行
                    trigger = trigger_system.evaluate(result)
                    if trigger and trigger_callback:
                        trigger_callback(trigger)
            
            results.append(result)
            
        except Exception as e:
            print(f"   ❌ 错误: {e}")
    
    return results

def main():
    """主函数 - 用于测试"""
    # 配置
    config = {
        'min_probability': 0.35,
        'min_confidence': 4,
        'max_models': 5
    }
    
    # 回调函数示例
    def on_trigger(trigger: StrategyTrigger):
        print(f"\n🎯 策略触发信号:")
        print(f"   策略: {trigger.strategy_name}")
        print(f"   模型: {trigger.models}")
        print(f"   概率: {trigger.probability:.2%}")
        print(f"   方向: {trigger.direction}")
        print(f"   仓位: {trigger.position_size:.2%}")
    
    # 运行分析
    results = run_analysis(
        symbols=['BTC/USDT', 'ETH/USDT', 'SOL/USDT'],
        config=config,
        trigger_callback=on_trigger
    )
    
    print("\n" + "=" * 60)
    print("✅ 分析完成")
    print("=" * 60)
    
    return results

if __name__ == '__main__':
    main()
