#!/usr/bin/env python3
"""
趋势模型匹配器 - 优化版 (v2)
从市场数据流中提取形态，与声纳库趋势模型比对，生成概率输出并触发策略

优化点:
1. 增强形态识别算法 (多因子加权)
2. 多时间框架交叉验证
3. 自适应阈值调整
4. 动态权重分配
5. 策略组合优化
"""

import json
import time
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
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
    """形态特征 (扩展版)"""
    trend_direction: float
    volatility: float
    momentum: float
    volume_profile: float
    price_acceleration: float
    support_resistance: float
    consolidation: float
    trend_strength: float
    volume_concentration: float
    price_entropy: float
    fractal_dimension: float
    hurst_exponent: float
    
@dataclass
class TrendMatch:
    model_name: str
    model_type: str
    probability: float
    confidence: float
    matched_indicators: List[str]
    timeframes: Dict[str, bool]
    direction: str
    features: PatternFeatures
    cross_tf_score: float = 0
    
@dataclass
class StrategyTrigger:
    strategy_name: str
    models: List[str]
    probability: float
    direction: str
    position_size: float
    entry_price: float
    stop_loss: float
    take_profit: float
    timeframe: str
    risk_level: str = 'medium'
    metadata: Dict = field(default_factory=dict)

# ==================== 趋势模型库 ====================

class TrendModelLibrary:
    def __init__(self, db_path='skills/go2se/data/trend_database.json'):
        self.db_path = db_path
        self.models = self.load_models()
        self.model_implementations = self._init_implementations()
        self.model_weights = self._init_weights()
    
    def load_models(self) -> Dict:
        try:
            with open(self.db_path, 'r') as f:
                return json.load(f)
        except:
            return self._default_models()
    
    def _default_models(self) -> Dict:
        return {
            "crypto_trends": {
                "momentum": {"name": "动量趋势", "indicators": ["RSI", "MACD", "EMA", "BB"]},
                "breakout": {"name": "突破趋势", "indicators": ["Volume", "BB", "Price_Change"]},
                "reversal": {"name": "反转趋势", "indicators": ["RSI", "Divergence", "BB"]},
                "whale_accumulation": {"name": "巨鲸积累", "indicators": ["Volume", "OrderFlow"]},
                "volume_spike": {"name": "成交量激增", "indicators": ["Volume"]},
                "trend_exhaustion": {"name": "趋势衰竭", "indicators": ["RSI", "Momentum"]},
                "consolidation_break": {"name": "震荡突破", "indicators": ["BB", "Volume"]},
                "divergence": {"name": "背离", "indicators": ["RSI", "MACD", "Price"]}
            }
        }
    
    def _init_weights(self) -> Dict:
        return {
            "momentum": 1.0, "breakout": 1.0, "reversal": 0.9,
            "whale_accumulation": 0.8, "volume_spike": 0.7,
            "trend_exhaustion": 0.85, "consolidation_break": 0.9, "divergence": 0.95
        }
    
    def _init_implementations(self) -> Dict:
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
    
    def _momentum_pattern(self, f: PatternFeatures, ind: Dict) -> float:
        score = 0
        if abs(f.trend_direction) > 0.5: score += 0.25
        elif abs(f.trend_direction) > 0.3: score += 0.15
        
        rsi = ind.get('rsi', 50)
        if f.trend_direction > 0 and 40 < rsi < 70: score += 0.2
        elif f.trend_direction < 0 and 30 < rsi < 60: score += 0.2
        
        macd = ind.get('macd', 0)
        if f.trend_direction > 0 and macd > 0: score += 0.2
        elif f.trend_direction < 0 and macd < 0: score += 0.2
        
        if f.trend_strength > 0.7: score += 0.15
        if f.hurst_exponent > 0.6: score += 0.2 * f.hurst_exponent
        return min(1.0, score)
    
    def _breakout_pattern(self, f: PatternFeatures, ind: Dict) -> float:
        score = 0
        if f.volume_profile > 2.0: score += 0.35
        elif f.volume_profile > 1.5: score += 0.25
        elif f.volume_profile > 1.2: score += 0.15
        
        if f.volatility > 0.5: score += 0.2
        if f.support_resistance > 0.7: score += 0.25
        if f.price_acceleration > 0.3: score += 0.1
        if f.volume_concentration > 0.7: score += 0.1
        return min(1.0, score)
    
    def _reversal_pattern(self, f: PatternFeatures, ind: Dict) -> float:
        score = 0
        rsi = ind.get('rsi', 50)
        if rsi < 25 or rsi > 75: score += 0.25
        elif rsi < 30 or rsi > 70: score += 0.2
        
        if abs(f.momentum) < 0.15: score += 0.15
        if f.consolidation > 0.6: score += 0.15
        if f.trend_direction * f.momentum < 0: score += 0.25
        if f.price_entropy < 0.3: score += 0.2
        return min(1.0, score)
    
    def _whale_pattern(self, f: PatternFeatures, ind: Dict) -> float:
        score = 0
        if f.volume_profile > 2.0: score += 0.35
        elif f.volume_profile > 1.5: score += 0.25
        if f.trend_direction < 0 and f.momentum > -0.1: score += 0.25
        if f.volatility < 0.3: score += 0.2
        if f.volume_concentration > 0.6: score += 0.2
        return min(1.0, score)
    
    def _volume_pattern(self, f: PatternFeatures, ind: Dict) -> float:
        score = 0
        if f.volume_profile > 2.0: score += 0.5
        elif f.volume_profile > 1.5: score += 0.35
        elif f.volume_profile > 1.2: score += 0.2
        if f.volume_concentration > 0.7: score += 0.3
        elif f.volume_concentration > 0.5: score += 0.2
        return min(1.0, score)
    
    def _exhaustion_pattern(self, f: PatternFeatures, ind: Dict) -> float:
        score = 0
        if f.trend_direction * f.momentum < 0: score += 0.35
        if f.volatility > 0.7: score += 0.25
        rsi = ind.get('rsi', 50)
        if rsi < 20 or rsi > 80: score += 0.3
        elif rsi < 25 or rsi > 75: score += 0.2
        if f.trend_strength < 0.3: score += 0.1
        return min(1.0, score)
    
    def _consolidation_pattern(self, f: PatternFeatures, ind: Dict) -> float:
        score = 0
        if f.consolidation > 0.5: score += 0.3
        elif f.consolidation > 0.3: score += 0.2
        if 0.2 < f.volatility < 0.5: score += 0.25
        if f.price_entropy < 0.4: score += 0.2
        if f.volume_profile > 1.3: score += 0.25
        return min(1.0, score)
    
    def _divergence_pattern(self, f: PatternFeatures, ind: Dict) -> float:
        score = 0
        if f.trend_direction * f.momentum < 0: score += 0.5
        rsi = ind.get('rsi', 50)
        if f.trend_direction > 0 and rsi < 40: score += 0.25
        elif f.trend_direction < 0 and rsi > 60: score += 0.25
        return min(1.0, score)
    
    def get_all_models(self, market_type='crypto') -> Dict:
        return self.models.get(f'{market_type}_trends', {})
    
    def match_models(self, features: PatternFeatures, indicators: Dict, 
                    market_type='crypto', timeframes=['5m', '15m'],
                    cross_tf_matches: List = None) -> List[TrendMatch]:
        matches = []
        models = self.get_all_models(market_type)
        cross_tf = cross_tf_matches or []
        
        for model_name, model_data in models.items():
            model_tfs = model_data.get('timeframes', {})
            supported = any(tf in model_tfs for tf in timeframes)
            if not supported:
                continue
            
            pattern_fn = self.model_implementations.get(model_name)
            if not pattern_fn:
                pattern_fn = self.model_implementations.get('momentum')
            
            base_prob = pattern_fn(features, indicators)
            weight = self.model_weights.get(model_name, 1.0)
            probability = base_prob * weight
            
            # 交叉验证加分
            cross_tf_bonus = 0
            for tf_match in cross_tf:
                if tf_match.get('model') == model_name:
                    cross_tf_bonus += 0.1
            cross_tf_bonus = min(0.2, cross_tf_bonus)
            probability = min(1.0, probability + cross_tf_bonus)
            
            if probability > 0.2:
                direction = 'neutral'
                if features.trend_direction > 0.25:
                    direction = 'long'
                elif features.trend_direction < -0.25:
                    direction = 'short'
                
                matches.append(TrendMatch(
                    model_name=model_name,
                    model_type=model_data.get('name', model_name),
                    probability=probability,
                    confidence=probability * 10,
                    matched_indicators=model_data.get('indicators', []),
                    timeframes=model_tfs,
                    direction=direction,
                    features=features,
                    cross_tf_score=cross_tf_bonus
                ))
        
        matches.sort(key=lambda x: x.probability, reverse=True)
        return matches

# ==================== 数据获取器 ====================

class MarketDataFetcher:
    def __init__(self, api_config: Optional[Dict] = None):
        self.api_config = api_config or {}
        self.exchanges = {}
        self._init_exchanges()
    
    def _init_exchanges(self):
        for eid in ['binance', 'bybit', 'okx', 'kucoin']:
            try:
                ec = getattr(ccxt, eid, None)
                if ec:
                    self.exchanges[eid] = ec({'enableRateLimit': True, 'options': {'defaultType': 'spot'}})
            except:
                pass
    
    def fetch_ohlcv(self, symbol: str, timeframe: str = '5m', limit: int = 100, exchange: str = 'binance') -> List[MarketData]:
        try:
            ex = self.exchanges.get(exchange)
            if not ex:
                return []
            ohlcv = ex.fetch_ohlcv(symbol, timeframe, limit=limit)
            return [MarketData(symbol=symbol, timestamp=int(c[0]), open=float(c[1]), high=float(c[2]), low=float(c[3]), close=float(c[4]), volume=float(c[5])) for c in ohlcv]
        except:
            return []
    
    def fetch_multi_timeframe(self, symbol: str) -> Dict[str, List[MarketData]]:
        result = {}
        for tf in ['1m', '5m', '15m', '1h', '4h']:
            data = self.fetch_ohlcv(symbol, tf, limit=100)
            if data:
                result[tf] = data
        return result

# ==================== 数据去噪音 ====================

class NoiseReducer:
    def __init__(self, window_size: int = 5):
        self.window_size = window_size
    
    def denoise(self, data: List[float], method: str = 'ema') -> List[float]:
        if not data:
            return []
        
        if method == 'ema':
            result = [data[0]]
            for i in range(1, len(data)):
                result.append(0.3 * data[i] + 0.7 * result[-1])
            return result
        elif method == 'ma':
            w = self.window_size
            return [(sum(data[max(0,i-w):i+1])/min(i+1,w)) for i in range(len(data))]
        elif method == 'hybrid':
            ema = self.denoise(data, 'ema')
            return self.denoise(ema, 'ma')
        return data

# ==================== 特征提取器 (优化版) ====================

class FeatureExtractor:
    def __init__(self):
        self.noise_reducer = NoiseReducer()
    
    def extract(self, data: List[MarketData], indicators: Dict = None) -> PatternFeatures:
        if len(data) < 20:
            return PatternFeatures(0,0,0,1,0,0,0,0,0,1.5,1.5,0.5)
        
        closes = np.array([d.close for d in data])
        highs = np.array([d.high for d in data])
        lows = np.array([d.low for d in data])
        volumes = np.array([d.volume for d in data])
        
        closes_clean = np.array(self.noise_reducer.denoise(closes.tolist(), 'hybrid'))
        
        return PatternFeatures(
            trend_direction=self._calc_trend(closes_clean),
            volatility=self._calc_vol(closes_clean),
            momentum=self._calc_mom(closes_clean),
            volume_profile=self._calc_vol_prof(volumes),
            price_acceleration=self._calc_accel(closes_clean),
            support_resistance=self._calc_sr(highs, lows, closes_clean),
            consolidation=self._calc_cons(highs, lows, closes_clean),
            trend_strength=self._calc_trend_str(closes_clean),
            volume_concentration=self._calc_vol_conc(volumes),
            price_entropy=self._calc_entropy(closes_clean),
            fractal_dimension=1.5,
            hurst_exponent=self._calc_hurst(closes_clean)
        )
    
    def _calc_trend(self, p): return np.clip(np.polyfit(range(len(p)), p, 1)[0]/np.mean(p)*100, -1, 1) if len(p)>1 else 0
    def _calc_vol(self, p): return float(np.std(np.diff(p)/p[:-1])) if len(p)>1 else 0
    def _calc_mom(self, p):
        if len(p) < 14: return 0
        d = np.diff(p)
        g = np.where(d > 0, d, 0)
        l = np.where(d < 0, -d, 0)
        rs = np.mean(g[-14:]) / (np.mean(l[-14:]) + 1e-10)
        return (100 - (100/(1+rs)) - 50) / 50
    def _calc_vol_prof(self, v): return np.mean(v[-5:])/(np.mean(v[:-5])+1e-10) if len(v)>5 else 1
    def _calc_accel(self, p): return float(np.mean(np.diff(np.diff(p)/p[:-1]))) if len(p)>2 else 0
    def _calc_sr(self, h, l, c):
        if len(h) < 2: return 0
        cp = c[-1]
        return min(1.0, (np.sum(h > cp*1.01) + np.sum(l < cp*0.99)) / 10)
    def _calc_cons(self, h, l, c):
        if len(h) < 2: return 0
        r = h[-20:] - l[-20:]
        return min(1.0, np.mean(r)/np.mean(c[-20:])*10)
    def _calc_trend_str(self, p):
        if len(p) < 14: return 0
        ch = np.diff(p)
        return abs(np.sum(ch > 0) - np.sum(ch < 0)) / (np.sum(ch > 0) + np.sum(ch < 0) + 1)
    def _calc_vol_conc(self, v):
        if len(v) < 5: return 0.5
        sv = np.sort(v[-20:])
        n = len(sv)
        cs = np.cumsum(sv)
        gini = (2*np.sum((np.arange(1,n+1)*sv)) - (n+1)*cs[-1]) / (n*cs[-1]+1e-10)
        return max(0, min(1, 1-gini))
    def _calc_entropy(self, p):
        if len(p) < 10: return 1.0
        r = np.diff(p)/p[:-1]
        hist, _ = np.histogram(r, bins=10)
        hist = hist/(np.sum(hist)+1e-10)
        return -np.sum(hist*np.log2(hist+1e-10))/np.log2(10)
    def _calc_hurst(self, p):
        if len(p) < 20: return 0.5
        st = np.std(p[-10:] - p[-20:-10]) if len(p) >= 20 else 0
        lt = np.std(p[-20:])
        return np.clip(0.5 + (st/(lt+1e-10) - 0.5) * 0.5, 0, 1)
    
    def calculate_indicators(self, data: List[MarketData]) -> Dict:
        if len(data) < 30: return {}
        closes = np.array([d.close for d in data])
        volumes = np.array([d.volume for d in data])
        
        d = np.diff(closes)
        g = np.where(d > 0, d, 0)
        l = np.where(d < 0, -d, 0)
        rsi = 100 - (100/(1+np.mean(g[-14:])/(np.mean(l[-14:])+1e-10)))
        
        ema12 = self._ema(closes, 12)
        ema26 = self._ema(closes, 26)
        macd = ema12 - ema26
        
        sma20 = np.mean(closes[-20:])
        std20 = np.std(closes[-20:])
        
        return {'rsi': rsi, 'macd': macd, 'price': closes[-1], 'sma20': sma20,
                'bb_upper': sma20+2*std20, 'bb_lower': sma20-2*std20,
                'vol_ratio': volumes[-1]/(np.mean(volumes[-20:])+1e-10)}
    
    def _ema(self, p, per):
        if len(p) < per: return np.mean(p)
        a = 2/(per+1)
        e = float(p[0])
        for x in p[1:]: e = a*float(x) + (1-a)*e
        return e

# ==================== 趋势匹配器核心 ====================

class TrendPatternMatcher:
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.library = TrendModelLibrary()
        self.fetcher = MarketDataFetcher()
        self.extractor = FeatureExtractor()
        
        self.min_probability = self.config.get('min_probability', 0.35)
        self.min_confidence = self.config.get('min_confidence', 4)
        self.max_models = self.config.get('max_models', 5)
        
        self.tf_weights = {'1m': 0.1, '5m': 0.25, '15m': 0.35, '1h': 0.2, '4h': 0.1}
    
    def analyze_symbol(self, symbol: str, timeframes: List[str] = None) -> Dict:
        if timeframes is None:
            timeframes = ['5m', '15m', '1h']
        
        results = {
            'symbol': symbol,
            'timestamp': int(time.time()),
            'matches': [],
            'best_models': [],
            'trigger': None,
            'features': {}
        }
        
        multi_tf_data = self.fetcher.fetch_multi_timeframe(symbol)
        
        if not multi_tf_data:
            return results
        
        # 第一阶段: 各时间框架独立分析
        tf_results = {}
        all_matches = []
        
        for tf, data in multi_tf_data.items():
            if len(data) < 30:
                continue
            
            indicators = self.extractor.calculate_indicators(data)
            features = self.extractor.extract(data, indicators)
            
            matches = self.library.match_models(features, indicators, timeframes=[tf])
            
            for m in matches:
                m.timeframe = tf
            
            tf_results[tf] = {'matches': matches, 'features': features, 'indicators': indicators}
            all_matches.extend(matches)
        
        # 第二阶段: 多时间框架交叉验证
        cross_tf_matches = self._cross_timeframe_validation(tf_results)
        
        # 第三阶段: 重新匹配(带交叉验证)
        final_matches = []
        for tf, res in tf_results.items():
            features = res['features']
            indicators = res['indicators']
            
            matches = self.library.match_models(features, indicators, 
                                               timeframes=[tf], cross_tf_matches=cross_tf_matches)
            for m in matches:
                m.timeframe = tf
            final_matches.extend(matches)
        
        # 聚合结果
        final_matches.sort(key=lambda x: x.probability, reverse=True)
        
        results['matches'] = [
            {'model': m.model_name, 'type': m.model_type, 'probability': m.probability,
             'confidence': m.confidence, 'direction': m.direction, 'timeframe': m.timeframe}
            for m in final_matches[:self.max_models]
        ]
        
        # 特征信息
        if tf_results:
            best_tf = max(tf_results.keys(), key=lambda k: len(tf_results[k]['matches']))
            f = tf_results[best_tf]['features']
            results['features'] = {
                'trend_direction': round(f.trend_direction, 3),
                'momentum': round(f.momentum, 3),
                'volatility': round(f.volatility, 3),
                'volume_profile': round(f.volume_profile, 3),
                'trend_strength': round(f.trend_strength, 3),
                'hurst_exponent': round(f.hurst_exponent, 3)
            }
        
        results['best_models'] = self._select_best_models(final_matches)
        
        # 检查触发
        trigger = self._check_trigger(results['best_models'], tf_results)
        if trigger:
            results['trigger'] = trigger
        
        return results
    
    def _cross_timeframe_validation(self, tf_results: Dict) -> List[Dict]:
        """多时间框架交叉验证"""
        model_counts = {}
        
        for tf, res in tf_results.items():
            weight = self.tf_weights.get(tf, 0.1)
            for m in res['matches']:
                if m.model_name not in model_counts:
                    model_counts[m.model_name] = 0
                model_counts[m.model_name] += weight
        
        return [{'model': k, 'weight': v} for k, v in model_counts.items() if v >= 0.3]
    
    def _select_best_models(self, matches: List[TrendMatch]) -> List[Dict]:
        model_probs = {}
        for m in matches:
            if m.model_name not in model_probs:
                model_probs[m.model_name] = []
            model_probs[m.model_name].append(m.probability)
        
        best = []
        for name, probs in model_probs.items():
            avg_prob = sum(probs) / len(probs)
            best.append({'model': name, 'probability': avg_prob, 'occurrences': len(probs)})
        
        best.sort(key=lambda x: x['probability'], reverse=True)
        return best[:3]
    
    def _check_trigger(self, best_models: List[Dict], tf_results: Dict) -> Optional[StrategyTrigger]:
        if not best_models or best_models[0]['probability'] < self.min_probability:
            return None
        
        best = best_models[0]
        
        # 动态调整阈值
        model_data = self.library.get_all_models().get(best['model'], {})
        min_conf = 4
        
        for tf, config in model_data.get('timeframes', {}).items():
            if config.get('execute', False):
                min_conf = config.get('min_confidence', min_conf)
                break
        
        if best['probability'] * 10 < min_conf:
            return None
        
        # 确定风险等级
        risk_level = 'low'
        if best['probability'] > 0.7:
            risk_level = 'high'
        elif best['probability'] > 0.5:
            risk_level = 'medium'
        
        return StrategyTrigger(
            strategy_name=f"trend_{best['model']}",
            models=[b['model'] for b in best_models],
            probability=best['probability'],
            direction='long' if best_models[0].get('probability', 0) > 0.5 else 'neutral',
            position_size=self._calc_position_size(best['probability'], risk_level),
            entry_price=0,
            stop_loss=0.02 if risk_level == 'high' else 0.03,
            take_profit=0.05 if risk_level == 'high' else 0.04,
            timeframe='5m',
            risk_level=risk_level
        )
    
    def _calc_position_size(self, probability: float, risk_level: str) -> float:
        base = {'low': 0.03, 'medium': 0.05, 'high': 0.08}
        return min(0.25, base.get(risk_level, 0.05) + probability * 0.15)

# ==================== 策略触发系统 ====================

class StrategyTriggerSystem:
    def __init__(self, matcher: TrendPatternMatcher):
        self.matcher = matcher
        self.strategies = {
            'trend_momentum': {'min_probability': 0.4, 'min_models': 1},
            'trend_breakout': {'min_probability': 0.5, 'min_models': 1},
            'trend_reversal': {'min_probability': 0.45, 'min_models': 1}
        }
    
    def evaluate(self, analysis_result: Dict) -> Optional[StrategyTrigger]:
        if not analysis_result.get('trigger'):
            return None
        
        trigger = analysis_result['trigger']
        models = analysis_result.get('best_models', [])
        
        for strat_name, strat_config in self.strategies.items():
            if len(models) < strat_config['min_models']:
                continue
            
            max_prob = max(m['probability'] for m in models)
            if max_prob < strat_config['min_probability']:
                continue
            
            trigger.strategy_name = strat_name
            return trigger
        
        return None

# ==================== 主脚本入口 ====================

def run_analysis(symbols: List[str] = None, config: Dict = None, trigger_callback: Optional[callable] = None):
    print("=" * 60)
    print("🚀 趋势模型匹配器 v2 (优化版)")
    print("=" * 60)
    
    if symbols is None:
        symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT']
    
    matcher = TrendPatternMatcher(config or {})
    trigger_system = StrategyTriggerSystem(matcher)
    
    results = []
    
    for symbol in symbols:
        print(f"\n📊 分析: {symbol}")
        
        try:
            result = matcher.analyze_symbol(symbol)
            
            if result['best_models']:
                best = result['best_models'][0]
                print(f"   最佳模型: {best['model']}")
                print(f"   匹配概率: {best['probability']:.2%}")
                
                # 显示特征
                if result.get('features'):
                    f = result['features']
                    print(f"   趋势方向: {f.get('trend_direction', 0):.2f}, 动量: {f.get('momentum', 0):.2f}")
                    print(f"   波动率: {f.get('volatility', 0):.3f}, 趋势强度: {f.get('trend_strength', 0):.2f}")
                
                if result.get('trigger'):
                    t = result['trigger']
                    print(f"   ⚡ 触发: {t.strategy_name} | 方向: {t.direction} | 仓位: {t.position_size:.2%} | 风险: {t.risk_level}")
                    
                    if trigger_callback:
                        trigger_callback(t)
            
            results.append(result)
            
        except Exception as e:
            print(f"   ❌ 错误: {e}")
    
    return results

def main():
    config = {'min_probability': 0.35, 'min_confidence': 4, 'max_models': 5}
    
    def on_trigger(trigger: StrategyTrigger):
        print(f"\n🎯 策略触发:")
        print(f"   策略: {trigger.strategy_name}")
        print(f"   模型: {trigger.models}")
        print(f"   概率: {trigger.probability:.2%}")
        print(f"   方向: {trigger.direction}")
        print(f"   仓位: {trigger.position_size:.2%}")
        print(f"   风险: {trigger.risk_level}")
        print(f"   止损: {trigger.stop_loss:.1%}, 止盈: {trigger.take_profit:.1%}")
    
    results = run_analysis(symbols=['BTC/USDT', 'ETH/USDT', 'SOL/USDT'], config=config, trigger_callback=on_trigger)
    
    print("\n" + "=" * 60)
    print("✅ 优化版分析完成")
    print("=" * 60)
    
    return results

if __name__ == '__main__':
    main()
