"""
市场数据获取模块 - market_data_fetcher.py
=========================================

功能：
1. 使用ccxt连接Binance获取实时K线数据
2. 计算完整的技术指标（RSI, MACD, Bollinger Bands, ATR, ADX, Stochastic, CCI, Williams %R, OBV, VWAP等）
3. 提供与声纳库对接的接口
4. 支持多个时间框架的数据获取

使用示例:
    fetcher = MarketDataFetcher()
    indicators = fetcher.get_indicators("BTC/USDT", "15m")
    print(f"RSI: {indicators.rsi}")
    print(f"MACD: {indicators.macd}")
"""

import asyncio
import ccxt
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import math
import numpy as np
from collections import deque

# 导入声纳库的数据结构
try:
    from .sonar_v2 import MarketIndicators, MarketRegime
except ImportError:
    from sonar_v2 import MarketIndicators, MarketRegime


# ==================== 时间框架映射 ====================

TIMEFRAME_MAP = {
    "1m": "1m",
    "5m": "5m",
    "15m": "15m",
    "30m": "30m",
    "1h": "1h",
    "4h": "4h",
    "1d": "1d",
    "1w": "1w",
}

TIMEFRAME_SECONDS = {
    "1m": 60,
    "5m": 300,
    "15m": 900,
    "30m": 1800,
    "1h": 3600,
    "4h": 14400,
    "1d": 86400,
    "1w": 604800,
}


# ==================== K线数据结构 ====================

@dataclass
class OHLCV:
    """K线数据"""
    timestamp: int
    datetime: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    
    @classmethod
    def from_ohlcv(cls, ohlcv: list) -> 'OHLCV':
        """从ccxt的ohlcv列表创建"""
        return cls(
            timestamp=ohlcv[0],
            datetime=datetime.fromtimestamp(ohlcv[0] / 1000).isoformat(),
            open=float(ohlcv[1]),
            high=float(ohlcv[2]),
            low=float(ohlcv[3]),
            close=float(ohlcv[4]),
            volume=float(ohlcv[5])
        )


# ==================== 技术指标计算器 ====================

class TechnicalIndicators:
    """技术指标计算器"""
    
    def __init__(self):
        self.lookback_periods = {
            'rsi': 14,
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            'bb': 20,
            'atr': 14,
            'adx': 14,
            'stoch': 14,
            'cci': 20,
            'obv': None,  # 不需要回溯
            'vwap': None,  # 不需要回溯
            'williams_r': 14,
            'sma': 20,
            'ema': 12,
        }
        
    def calculate_all(self, ohlcv_list: List[List[float]], 
                      timeframe: str = "15m") -> MarketIndicators:
        """计算所有指标"""
        ohlcv_array = np.array(ohlcv_list)
        
        # 提取各列
        closes = ohlcv_array[:, 4]
        highs = ohlcv_array[:, 2]
        lows = ohlcv_array[:, 3]
        volumes = ohlcv_array[:, 5]
        
        n = len(closes)
        
        # 基础价格信息
        close = float(closes[-1])
        open_price = float(ohlcv_array[-1, 1])
        high = float(highs[-1])
        low = float(lows[-1])
        
        # 价格变化
        price_change_pct = ((close - float(closes[-2])) / float(closes[-2]) * 100) if n > 1 else 0
        
        # K线特征
        candle_body = abs(close - open_price)
        candle_range = high - low
        candle_body_pct = (candle_body / candle_range * 100) if candle_range > 0 else 0
        upper_shadow = high - max(open_price, close)
        lower_shadow = min(open_price, close) - low
        upper_shadow_pct = (upper_shadow / candle_range * 100) if candle_range > 0 else 0
        lower_shadow_pct = (lower_shadow / candle_range * 100) if candle_range > 0 else 0
        is_doji = candle_body_pct < 20
        is_hammer = lower_shadow_pct > 60 and upper_shadow_pct < 10
        is_shooting_star = upper_shadow_pct > 60 and lower_shadow_pct < 10
        
        # RSI
        rsi = self.calculate_rsi(closes, 14)
        rsi_14 = rsi
        rsi_7 = self.calculate_rsi(closes, 7)
        rsi_3 = self.calculate_rsi(closes, 3)
        
        # MACD
        macd, macd_signal, macd_histogram = self.calculate_macd(closes)
        # macd_histogram可能是float或array
        if isinstance(macd_histogram, (list, np.ndarray)):
            macd_histogram_prev = float(macd_histogram[-2]) if len(macd_histogram) > 1 else 0
        else:
            macd_histogram_prev = 0
        
        # 均线
        sma5 = self.calculate_sma(closes, 5)
        sma10 = self.calculate_sma(closes, 10)
        sma20 = self.calculate_sma(closes, 20)
        sma50 = self.calculate_sma(closes, 50)
        sma100 = self.calculate_sma(closes, 100)
        sma200 = self.calculate_sma(closes, 200)
        
        ema4 = self.calculate_ema(closes, 4)
        ema9 = self.calculate_ema(closes, 9)
        ema12 = self.calculate_ema(closes, 12)
        ema21 = self.calculate_ema(closes, 21)
        ema26 = self.calculate_ema(closes, 26)
        ema50 = self.calculate_ema(closes, 50)
        ema55 = self.calculate_ema(closes, 55)
        ema200 = self.calculate_ema(closes, 200)
        
        # 布林带
        bb_upper, bb_middle, bb_lower, bb_width, bb_percent = self.calculate_bollinger_bands(closes, 20)
        
        # ATR
        atr, atr_14, atr_pct, true_range = self.calculate_atr(ohlcv_array)
        
        # ADX
        adx, plus_di, minus_di, adx_slope = self.calculate_adx(ohlcv_array)
        
        # 成交量
        volume = float(volumes[-1])
        volume_ma = self.calculate_sma(volumes, 20)
        volume_ma_20 = volume_ma
        volume_ratio = volume / volume_ma if volume_ma > 0 else 1
        volume_change_pct = ((volume - float(volumes[-2])) / float(volumes[-2]) * 100) if n > 1 else 0
        
        # OBV
        obv, obv_ma, obv_slope = self.calculate_obv(closes, volumes)
        
        # VWAP
        vwap, vwap_upper, vwap_lower, vwap_deviation = self.calculate_vwap(ohlcv_array)
        
        # Williams %R
        williams_r, williams_r_14 = self.calculate_williams_r(highs, lows, closes)
        
        # CCI
        cci, cci_14, cci_20 = self.calculate_cci(ohlcv_array)
        
        # Stochastic
        stoch_k, stoch_d, stoch_k_14, stoch_d_14, stoch_slow, stoch_fast = self.calculate_stochastic(highs, lows, closes)
        
        # 价格形态识别
        higher_highs, higher_lows, lower_highs, lower_lows = self.detect_price_patterns(closes, highs, lows)
        double_top, double_bottom = self.detect_double_patterns(closes)
        triple_top, triple_bottom = self.detect_triple_patterns(closes)
        
        # 趋势线角度
        trendline_angle = self.calculate_trendline_angle(closes)
        
        # 异常检测
        volume_anomaly = volume_ratio > 3 or volume_ratio < 0.3
        volatility_anomaly = bb_width > 0.05 or bb_width < 0.005
        price_anomaly = abs(price_change_pct) > 10
        
        # 市场状态
        market_regime = self.detect_market_regime(adx, bb_width, price_change_pct, plus_di, minus_di)
        regime_confidence = self.calculate_regime_confidence(adx, bb_width)
        
        # 综合评分
        momentum_score = self.calculate_momentum_score(rsi, macd_histogram, stoch_k)
        trend_score = self.calculate_trend_score(adx, plus_di, minus_di, sma20, sma50, close)
        volatility_score = self.calculate_volatility_score(bb_width, atr_pct)
        volume_score = self.calculate_volume_score(volume_ratio, obv_slope)
        
        # 支撑阻力
        support_level, resistance_level, pivot_point = self.calculate_support_resistance(highs, lows, closes)
        
        return MarketIndicators(
            close=close,
            open=open_price,
            high=high,
            low=low,
            price_change_pct=price_change_pct,
            rsi=rsi,
            rsi_14=rsi_14,
            rsi_7=rsi_7,
            rsi_3=rsi_3,
            macd=macd,
            macd_signal=macd_signal,
            macd_histogram=macd_histogram,
            macd_histogram_prev=macd_histogram_prev,
            sma5=sma5,
            sma10=sma10,
            sma20=sma20,
            sma50=sma50,
            sma100=sma100,
            sma200=sma200,
            ema4=ema4,
            ema9=ema9,
            ema12=ema12,
            ema21=ema21,
            ema26=ema26,
            ema50=ema50,
            ema55=ema55,
            ema200=ema200,
            bb_upper=bb_upper,
            bb_middle=bb_middle,
            bb_lower=bb_lower,
            bb_width=bb_width,
            bb_percent=bb_percent,
            atr=atr,
            atr_14=atr_14,
            atr_pct=atr_pct,
            true_range=true_range,
            adx=adx,
            plus_di=plus_di,
            minus_di=minus_di,
            adx_slope=adx_slope,
            volume=volume,
            volume_ma=volume_ma,
            volume_ma_20=volume_ma_20,
            volume_ratio=volume_ratio,
            volume_change_pct=volume_change_pct,
            obv=obv,
            obv_ma=obv_ma,
            obv_slope=obv_slope,
            vwap=vwap,
            vwap_upper=vwap_upper,
            vwap_lower=vwap_lower,
            vwap_deviation=vwap_deviation,
            williams_r=williams_r,
            williams_r_14=williams_r_14,
            cci=cci,
            cci_14=cci_14,
            cci_20=cci_20,
            stochastic_k=stoch_k,
            stochastic_d=stoch_d,
            stochastic_k_14=stoch_k_14,
            stochastic_d_14=stoch_d_14,
            stochastic_slow=stoch_slow,
            stochastic_fast=stoch_fast,
            higher_highs=higher_highs,
            higher_lows=higher_lows,
            lower_highs=lower_highs,
            lower_lows=lower_lows,
            double_top=double_top,
            double_bottom=double_bottom,
            triple_top=triple_top,
            triple_bottom=triple_bottom,
            trendline_angle=trendline_angle,
            volume_anomaly=volume_anomaly,
            volatility_anomaly=volatility_anomaly,
            price_anomaly=price_anomaly,
            market_regime=market_regime,
            regime_confidence=regime_confidence,
            momentum_score=momentum_score,
            trend_score=trend_score,
            volatility_score=volatility_score,
            volume_score=volume_score,
            candle_body_pct=candle_body_pct,
            upper_shadow_pct=upper_shadow_pct,
            lower_shadow_pct=lower_shadow_pct,
            is_doji=is_doji,
            is_hammer=is_hammer,
            is_shooting_star=is_shooting_star,
            support_level=support_level,
            resistance_level=resistance_level,
            pivot_point=pivot_point,
            highs=list(highs[-10:]) if len(highs) >= 10 else list(highs),
            lows=list(lows[-10:]) if len(lows) >= 10 else list(lows),
            closes=list(closes[-10:]) if len(closes) >= 10 else list(closes),
            volumes=list(volumes[-10:]) if len(volumes) >= 10 else list(volumes)
        )
    
    def calculate_rsi(self, closes: np.ndarray, period: int = 14) -> float:
        """计算RSI"""
        if len(closes) < period + 1:
            return 50.0
        
        deltas = np.diff(closes)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        # 使用指数移动平均
        avg_gain = self._ema(gains[-period:], period)
        avg_loss = self._ema(losses[-period:], period)
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return float(rsi)
    
    def _ema(self, data: np.ndarray, period: int) -> float:
        """计算EMA"""
        if len(data) == 0:
            return 0.0
        alpha = 2 / (period + 1)
        ema = data[0]
        for i in range(1, len(data)):
            ema = alpha * data[i] + (1 - alpha) * ema
        return ema
    
    def calculate_macd(self, closes: np.ndarray) -> Tuple[float, float, float]:
        """计算MACD"""
        if len(closes) < 26:
            return 0.0, 0.0, 0.0
        
        # EMA计算
        ema12 = self._ema(closes[-12:], 12) if len(closes) >= 12 else self._ema(closes, 12)
        ema26 = self._ema(closes[-26:], 26) if len(closes) >= 26 else self._ema(closes, 26)
        
        macd = ema12 - ema26
        
        # Signal线 (9日EMA of MACD)
        # 简化: 使用最近9个MACD值计算
        macd_values = []
        for i in range(26, min(len(closes), 35)):
            e12 = self._ema(closes[i-12:i], 12)
            e26 = self._ema(closes[i-26:i], 26)
            macd_values.append(e12 - e26)
        
        if len(macd_values) >= 9:
            signal = self._ema(np.array(macd_values[-9:]), 9)
        else:
            signal = self._ema(np.array(macd_values), len(macd_values)) if macd_values else 0
        
        histogram = macd - signal
        
        return float(macd), float(signal), float(histogram)
    
    def calculate_sma(self, data: np.ndarray, period: int) -> float:
        """计算SMA"""
        if len(data) < period:
            return float(data[-1]) if len(data) > 0 else 0.0
        return float(np.mean(data[-period:]))
    
    def calculate_ema(self, closes: np.ndarray, period: int) -> float:
        """计算EMA"""
        if len(closes) < period:
            return float(closes[-1]) if len(closes) > 0 else 0.0
        return self._ema(closes[-period:], period)
    
    def calculate_bollinger_bands(self, closes: np.ndarray, period: int = 20) -> Tuple[float, float, float, float, float]:
        """计算布林带"""
        if len(closes) < period:
            return 0.0, 0.0, 0.0, 0.0, 50.0
        
        sma = self.calculate_sma(closes, period)
        std = float(np.std(closes[-period:]))
        
        upper = sma + 2 * std
        lower = sma - 2 * std
        
        # 布林带宽度
        width = (upper - lower) / sma if sma > 0 else 0
        
        # %B指标
        current_close = float(closes[-1])
        if upper != lower:
            percent = (current_close - lower) / (upper - lower) * 100
        else:
            percent = 50
        
        return upper, sma, lower, width, percent
    
    def calculate_atr(self, ohlcv: np.ndarray) -> Tuple[float, float, float, float]:
        """计算ATR"""
        if len(ohlcv) < 14:
            return 0.0, 0.0, 0.0, 0.0
        
        highs = ohlcv[:, 2]
        lows = ohlcv[:, 3]
        closes = ohlcv[:, 4]
        
        # True Range
        tr_list = []
        for i in range(1, len(ohlcv)):
            high = highs[i]
            low = lows[i]
            prev_close = closes[i-1]
            
            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            tr_list.append(tr)
        
        tr_array = np.array(tr_list)
        atr = float(np.mean(tr_array[-14:])) if len(tr_array) >= 14 else float(np.mean(tr_array))
        atr_14 = atr
        atr_pct = atr / closes[-1] if closes[-1] > 0 else 0
        true_range = tr_list[-1] if tr_list else 0
        
        return atr, atr_14, atr_pct, true_range
    
    def calculate_adx(self, ohlcv: np.ndarray, period: int = 14) -> Tuple[float, float, float, float]:
        """计算ADX"""
        if len(ohlcv) < period + 1:
            return 0.0, 0.0, 0.0, 0.0
        
        highs = ohlcv[:, 2]
        lows = ohlcv[:, 3]
        closes = ohlcv[:, 4]
        
        # 计算 +DM 和 -DM
        plus_dm_list = []
        minus_dm_list = []
        tr_list = []
        
        for i in range(1, len(ohlcv)):
            high = highs[i]
            low = lows[i]
            prev_high = highs[i-1]
            prev_low = lows[i-1]
            prev_close = closes[i-1]
            
            # True Range
            tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
            tr_list.append(tr)
            
            # Directional Movement
            plus_dm = max(high - prev_high, 0) if (high - prev_high) > (prev_low - low) else 0
            minus_dm = max(prev_low - low, 0) if (prev_low - low) > (high - prev_high) else 0
            
            plus_dm_list.append(plus_dm)
            minus_dm_list.append(minus_dm)
        
        tr_array = np.array(tr_list)
        plus_dm_array = np.array(plus_dm_list)
        minus_dm_array = np.array(minus_dm_list)
        
        # 计算平滑值
        atr_smooth = np.mean(tr_array[-period:]) if len(tr_array) >= period else np.mean(tr_array)
        plus_dm_smooth = np.mean(plus_dm_array[-period:]) if len(plus_dm_array) >= period else np.mean(plus_dm_array)
        minus_dm_smooth = np.mean(minus_dm_array[-period:]) if len(minus_dm_array) >= period else np.mean(minus_dm_array)
        
        # 计算 DI
        plus_di = (plus_dm_smooth / atr_smooth * 100) if atr_smooth > 0 else 0
        minus_di = (minus_dm_smooth / atr_smooth * 100) if atr_smooth > 0 else 0
        
        # 计算 DX
        di_sum = plus_di + minus_di
        dx = (abs(plus_di - minus_di) / di_sum * 100) if di_sum > 0 else 0
        
        # 计算 ADX (简化)
        adx = dx  # 简化处理
        
        # ADX斜率 (简化)
        adx_slope = 0.0
        
        return float(adx), float(plus_di), float(minus_di), adx_slope
    
    def calculate_obv(self, closes: np.ndarray, volumes: np.ndarray) -> Tuple[float, float, float]:
        """计算OBV"""
        if len(closes) < 2:
            return 0.0, 0.0, 0.0
        
        obv = 0.0
        for i in range(1, len(closes)):
            if closes[i] > closes[i-1]:
                obv += volumes[i]
            elif closes[i] < closes[i-1]:
                obv -= volumes[i]
        
        # OBV的MA (20日)
        if len(closes) >= 20:
            obv_values = []
            temp_obv = 0.0
            for i in range(1, 20):
                if closes[i] > closes[i-1]:
                    temp_obv += volumes[i]
                elif closes[i] < closes[i-1]:
                    temp_obv -= volumes[i]
                obv_values.append(temp_obv)
            obv_ma = np.mean(obv_values) if obv_values else obv
        else:
            obv_ma = obv
        
        # OBV斜率
        if len(closes) >= 10:
            obv_values = []
            temp_obv = 0.0
            for i in range(1, min(10, len(closes))):
                if closes[i] > closes[i-1]:
                    temp_obv += volumes[i]
                elif closes[i] < closes[i-1]:
                    temp_obv -= volumes[i]
                obv_values.append(temp_obv)
            
            if len(obv_values) >= 2:
                slope = (obv_values[-1] - obv_values[0]) / obv_ma if obv_ma != 0 else 0
            else:
                slope = 0.0
        else:
            slope = 0.0
        
        return float(obv), float(obv_ma), float(slope)
    
    def calculate_vwap(self, ohlcv: np.ndarray) -> Tuple[float, float, float, float]:
        """计算VWAP"""
        if len(ohlcv) < 2:
            return 0.0, 0.0, 0.0, 0.0
        
        highs = ohlcv[:, 2]
        lows = ohlcv[:, 3]
        closes = ohlcv[:, 4]
        volumes = ohlcv[:, 5]
        
        # 典型价格
        typical_prices = (highs + lows + closes) / 3
        
        # VWAP = Σ(典型价格 × 成交量) / Σ成交量
        tp_vol_sum = np.sum(typical_prices * volumes)
        vol_sum = np.sum(volumes)
        
        vwap = tp_vol_sum / vol_sum if vol_sum > 0 else closes[-1]
        
        # VWAP上下轨 (基于标准差)
        tp_std = float(np.std(typical_prices))
        vwap_upper = vwap + tp_std
        vwap_lower = vwap - tp_std
        
        # 价格偏离VWAP
        vwap_deviation = (closes[-1] - vwap) / vwap if vwap > 0 else 0
        
        return float(vwap), float(vwap_upper), float(vwap_lower), float(vwap_deviation)
    
    def calculate_williams_r(self, highs: np.ndarray, lows: np.ndarray, 
                            closes: np.ndarray, period: int = 14) -> Tuple[float, float]:
        """计算Williams %R"""
        if len(closes) < period:
            return -50.0, -50.0
        
        highest_high = np.max(highs[-period:])
        lowest_low = np.min(lows[-period:])
        
        if highest_high == lowest_low:
            return -50.0, -50.0
        
        williams_r = -100 * (highest_high - closes[-1]) / (highest_high - lowest_low)
        
        # 14日Williams %R
        if len(closes) >= 28:
            highest_high_14 = np.max(highs[-14:])
            lowest_low_14 = np.min(lows[-14:])
            if highest_high_14 != lowest_low_14:
                williams_r_14 = -100 * (highest_high_14 - closes[-1]) / (highest_high_14 - lowest_low_14)
            else:
                williams_r_14 = williams_r
        else:
            williams_r_14 = williams_r
        
        return float(williams_r), float(williams_r_14)
    
    def calculate_cci(self, ohlcv: np.ndarray, period: int = 20) -> Tuple[float, float, float]:
        """计算CCI"""
        if len(ohlcv) < period:
            return 0.0, 0.0, 0.0
        
        highs = ohlcv[:, 2]
        lows = ohlcv[:, 3]
        closes = ohlcv[:, 4]
        
        # 典型价格
        typical_prices = (highs + lows + closes) / 3
        
        # CCI = (典型价格 - SMA(典型价格)) / (0.015 × 平均偏差)
        sma_tp = np.mean(typical_prices[-period:])
        mean_deviation = np.mean(np.abs(typical_prices[-period:] - sma_tp))
        
        if mean_deviation == 0:
            cci = 0
        else:
            cci = (typical_prices[-1] - sma_tp) / (0.015 * mean_deviation)
        
        # 14日CCI
        if len(ohlcv) >= 14:
            tp_14 = (highs + lows + closes) / 3
            sma_tp_14 = np.mean(tp_14[-14:])
            mean_dev_14 = np.mean(np.abs(tp_14[-14:] - sma_tp_14))
            if mean_dev_14 == 0:
                cci_14 = 0
            else:
                cci_14 = (tp_14[-1] - sma_tp_14) / (0.015 * mean_dev_14)
        else:
            cci_14 = cci
        
        # 20日CCI
        cci_20 = cci
        
        return float(cci), float(cci_14), float(cci_20)
    
    def calculate_stochastic(self, highs: np.ndarray, lows: np.ndarray,
                            closes: np.ndarray, period: int = 14) -> Tuple[float, float, float, float, float, float]:
        """计算随机指标"""
        if len(closes) < period:
            return 50.0, 50.0, 50.0, 50.0, 50.0, 50.0
        
        # %K (14日)
        highest_high = np.max(highs[-period:])
        lowest_low = np.min(lows[-period:])
        
        if highest_high == lowest_low:
            k = 50.0
        else:
            k = 100 * (closes[-1] - lowest_low) / (highest_high - lowest_low)
        
        # %D (3日简单移动平均 of %K)
        k_values = []
        for i in range(period, len(closes) + 1):
            hh = np.max(highs[i-period:i])
            ll = np.min(lows[i-period:i])
            if hh != ll:
                k_values.append(100 * (closes[i-1] - ll) / (hh - ll))
            else:
                k_values.append(50.0)
        
        if len(k_values) >= 3:
            d = np.mean(k_values[-3:])
        else:
            d = np.mean(k_values) if k_values else 50.0
        
        # 快慢随机指标
        stoch_fast = k
        stoch_slow = d
        
        return float(k), float(d), float(k), float(d), float(stoch_slow), float(stoch_fast)
    
    def detect_price_patterns(self, closes: np.ndarray, highs: np.ndarray, 
                             lows: np.ndarray) -> Tuple[bool, bool, bool, bool]:
        """检测价格形态"""
        if len(closes) < 5:
            return False, False, False, False
        
        # 最近5根K线
        recent_highs = list(highs[-5:])
        recent_lows = list(lows[-5:])
        recent_closes = list(closes[-5:])
        
        # 高点更高
        higher_highs = recent_highs[-1] > recent_highs[-2] > recent_highs[-3]
        # 低点更高
        higher_lows = recent_lows[-1] > recent_lows[-2] > recent_lows[-3]
        # 高点更低
        lower_highs = recent_highs[-1] < recent_highs[-2] < recent_highs[-3]
        # 低点更低
        lower_lows = recent_lows[-1] < recent_lows[-2] < recent_lows[-3]
        
        return higher_highs, higher_lows, lower_highs, lower_lows
    
    def detect_double_patterns(self, closes: np.ndarray) -> Tuple[bool, bool]:
        """检测双顶/双底形态"""
        if len(closes) < 10:
            return False, False
        
        # 简化检测：最近的价格峰值/谷值比较
        recent = closes[-10:]
        
        # 找局部最大最小
        double_top = False
        double_bottom = False
        
        # 简单的双顶/双底检测
        mid = len(recent) // 2
        left_part = recent[:mid]
        right_part = recent[mid:]
        
        if len(left_part) >= 2 and len(right_part) >= 2:
            # 检查双顶 (两个相近的高点)
            left_max = max(left_part)
            right_max = max(right_part)
            if abs(left_max - right_max) / left_max < 0.02:  # 2%以内
                double_top = True
            
            # 检查双底
            left_min = min(left_part)
            right_min = min(right_part)
            if abs(left_min - right_min) / left_min < 0.02:
                double_bottom = True
        
        return double_top, double_bottom
    
    def detect_triple_patterns(self, closes: np.ndarray) -> Tuple[bool, bool]:
        """检测三顶/三底形态"""
        if len(closes) < 15:
            return False, False
        
        # 简化：三顶/三底需要更复杂的检测，这里返回False
        return False, False
    
    def calculate_trendline_angle(self, closes: np.ndarray) -> float:
        """计算趋势线角度"""
        if len(closes) < 10:
            return 0.0
        
        # 简单线性回归
        n = 10
        x = np.arange(n)
        y = closes[-n:]
        
        x_mean = np.mean(x)
        y_mean = np.mean(y)
        
        numerator = np.sum((x - x_mean) * (y - y_mean))
        denominator = np.sum((x - x_mean) ** 2)
        
        if denominator == 0:
            return 0.0
        
        slope = numerator / denominator
        
        # 转换为角度 (度)
        angle = np.degrees(np.arctan(slope / closes[-1] * 100))
        
        return float(angle)
    
    def detect_market_regime(self, adx: float, bb_width: float, 
                           price_change_pct: float, plus_di: float, 
                           minus_di: float) -> MarketRegime:
        """检测市场状态"""
        # 强趋势
        if adx > 30:
            if plus_di > minus_di:
                return MarketRegime.TRENDING_UP
            else:
                return MarketRegime.TRENDING_DOWN
        
        # 突破前夕
        if bb_width < 0.015 and adx < 20:
            return MarketRegime.BREAKOUT_IMMINENT
        
        # 高波动
        if bb_width > 0.04 or abs(price_change_pct) > 5:
            return MarketRegime.VOLATILE
        
        # 低波动
        if bb_width < 0.01 and adx < 15:
            return MarketRegime.QUIET
        
        # 区间震荡
        return MarketRegime.RANGE_BOUND
    
    def calculate_regime_confidence(self, adx: float, bb_width: float) -> float:
        """计算市场状态置信度"""
        confidence = 0.5
        
        if adx > 30:
            confidence = min(0.95, adx / 30 + 0.2)
        elif bb_width < 0.012:
            confidence = 0.7
        elif bb_width > 0.05:
            confidence = 0.8
        
        return confidence
    
    def calculate_momentum_score(self, rsi: float, macd_hist: float, stoch_k: float) -> float:
        """计算动量评分"""
        score = 50.0
        
        # RSI贡献
        if rsi > 50:
            score += (rsi - 50) * 0.4
        else:
            score -= (50 - rsi) * 0.4
        
        # MACD贡献
        if macd_hist > 0:
            score += min(20, macd_hist / 5)
        else:
            score -= min(20, abs(macd_hist) / 5)
        
        # Stochastic贡献
        if stoch_k > 50:
            score += (stoch_k - 50) * 0.2
        else:
            score -= (50 - stoch_k) * 0.2
        
        return max(0, min(100, score))
    
    def calculate_trend_score(self, adx: float, plus_di: float, minus_di: float,
                             sma20: float, sma50: float, close: float) -> float:
        """计算趋势评分"""
        score = 50.0
        
        # ADX贡献
        if adx > 25:
            score += min(30, adx - 25 + 10)
        
        # 方向贡献
        if plus_di > minus_di and close > sma20 > sma50:
            score += 20
        elif minus_di > plus_di and close < sma20 < sma50:
            score += 20
        
        return max(0, min(100, score))
    
    def calculate_volatility_score(self, bb_width: float, atr_pct: float) -> float:
        """计算波动率评分"""
        # 波动率高分数低
        vol_score = 100 - (bb_width * 2000) if bb_width > 0 else 50
        vol_score = max(0, min(100, vol_score))
        
        return vol_score
    
    def calculate_volume_score(self, volume_ratio: float, obv_slope: float) -> float:
        """计算成交量评分"""
        score = 50.0
        
        if volume_ratio > 1.5:
            score += min(25, (volume_ratio - 1) * 20)
        elif volume_ratio < 0.7:
            score -= min(25, (0.7 - volume_ratio) * 30)
        
        if obv_slope > 0.1:
            score += 10
        elif obv_slope < -0.1:
            score -= 10
        
        return max(0, min(100, score))
    
    def calculate_support_resistance(self, highs: np.ndarray, lows: np.ndarray,
                                     closes: np.ndarray) -> Tuple[float, float, float]:
        """计算支撑阻力位"""
        if len(closes) < 2:
            return 0.0, 0.0, closes[-1] if len(closes) > 0 else 0.0
        
        # 枢轴点
        pivot = (highs[-1] + lows[-1] + closes[-1]) / 3
        
        # 支撑位
        support = lows[-1] if len(lows) > 0 else closes[-1]
        
        # 阻力位
        resistance = highs[-1] if len(highs) > 0 else closes[-1]
        
        return float(support), float(resistance), float(pivot)


# ==================== 市场数据获取器 ====================

class MarketDataFetcher:
    """
    市场数据获取器
    
    使用ccxt连接Binance获取实时数据
    """
    
    def __init__(self, api_key: str = None, api_secret: str = None):
        """初始化"""
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'},
        })
        
        self.indicators = TechnicalIndicators()
        self.cache: Dict[str, Tuple[List[List[float]], datetime]] = {}
        self.cache_ttl = 60  # 缓存有效期(秒)
        
    def get_ohlcv(self, symbol: str, timeframe: str = "15m", 
                 limit: int = 200) -> List[List[float]]:
        """
        获取K线数据
        
        Args:
            symbol: 交易对，如 "BTC/USDT"
            timeframe: 时间框架，如 "15m", "1h", "4h", "1d"
            limit: 获取数量
            
        Returns:
            List of OHLCV data
        """
        # 检查缓存
        cache_key = f"{symbol}_{timeframe}"
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if (datetime.now() - cached_time).seconds < self.cache_ttl:
                return cached_data
        
        try:
            # 转换时间框架
            tf = TIMEFRAME_MAP.get(timeframe, timeframe)
            
            # 获取K线数据
            ohlcv = self.exchange.fetch_ohlcv(symbol, tf, limit=limit)
            
            # 缓存
            self.cache[cache_key] = (ohlcv, datetime.now())
            
            return ohlcv
            
        except Exception as e:
            print(f"Error fetching OHLCV for {symbol}: {e}")
            return []
    
    def get_indicators(self, symbol: str, timeframe: str = "15m") -> Optional[MarketIndicators]:
        """
        获取技术指标
        
        Args:
            symbol: 交易对，如 "BTC/USDT"
            timeframe: 时间框架
            
        Returns:
            MarketIndicators对象
        """
        ohlcv = self.get_ohlcv(symbol, timeframe)
        
        if len(ohlcv) < 50:
            print(f"Insufficient data for {symbol}, got {len(ohlcv)} candles")
            return None
        
        return self.indicators.calculate_all(ohlcv, timeframe)
    
    def get_multi_timeframe_indicators(self, symbol: str, 
                                      timeframes: List[str] = None) -> Dict[str, MarketIndicators]:
        """
        获取多个时间框架的指标
        
        Args:
            symbol: 交易对
            timeframes: 时间框架列表
            
        Returns:
            Dict[str, MarketIndicators]
        """
        if timeframes is None:
            timeframes = ["5m", "15m", "1h", "4h"]
        
        result = {}
        
        for tf in timeframes:
            try:
                indicators = self.get_indicators(symbol, tf)
                if indicators:
                    result[tf] = indicators
            except Exception as e:
                print(f"Error getting {tf} indicators for {symbol}: {e}")
        
        return result
    
    def get_batch_indicators(self, symbols: List[str], 
                            timeframe: str = "15m") -> Dict[str, Optional[MarketIndicators]]:
        """
        批量获取多个交易对的指标
        
        Args:
            symbols: 交易对列表
            timeframe: 时间框架
            
        Returns:
            Dict[str, MarketIndicators]
        """
        result = {}
        
        for symbol in symbols:
            try:
                indicators = self.get_indicators(symbol, timeframe)
                result[symbol] = indicators
            except Exception as e:
                print(f"Error getting indicators for {symbol}: {e}")
                result[symbol] = None
        
        return result
    
    def scan_symbols(self, symbols: List[str], timeframe: str = "15m") -> List[Dict]:
        """
        扫描多个交易对，收集市场状态信息
        
        Returns:
            List of dicts with symbol and indicators summary
        """
        results = []
        
        for symbol in symbols:
            try:
                indicators = self.get_indicators(symbol, timeframe)
                if indicators:
                    results.append({
                        'symbol': symbol,
                        'indicators': indicators,
                        'summary': {
                            'price': indicators.close,
                            'price_change_pct': indicators.price_change_pct,
                            'rsi': indicators.rsi,
                            'trend': 'BULL' if indicators.price_change_pct > 0 else 'BEAR',
                            'volume_ratio': indicators.volume_ratio,
                            'market_regime': indicators.market_regime.value
                        }
                    })
            except Exception as e:
                print(f"Error scanning {symbol}: {e}")
        
        return results
    
    def get_ticker(self, symbol: str) -> Optional[Dict]:
        """获取Ticker信息"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return {
                'symbol': symbol,
                'last': ticker.get('last'),
                'bid': ticker.get('bid'),
                'ask': ticker.get('ask'),
                'volume': ticker.get('baseVolume'),
                'price_change': ticker.get('change'),
                'price_change_pct': ticker.get('percentage'),
                'high': ticker.get('high'),
                'low': ticker.get('low'),
            }
        except Exception as e:
            print(f"Error fetching ticker for {symbol}: {e}")
            return None
    
    def get_top_volumes(self, limit: int = 20) -> List[Dict]:
        """获取成交量排名"""
        try:
            # 获取所有交易对
            markets = self.exchange.load_markets()
            
            volumes = []
            for symbol in list(markets.keys())[:100]:  # 限制检查数量
                try:
                    ticker = self.get_ticker(symbol)
                    if ticker and ticker.get('volume'):
                        volumes.append(ticker)
                except:
                    continue
            
            # 按成交量排序
            volumes.sort(key=lambda x: x.get('volume', 0), reverse=True)
            
            return volumes[:limit]
        except Exception as e:
            print(f"Error getting top volumes: {e}")
            return []


# ==================== 声纳库集成 ====================

class SonarMarketIntegration:
    """
    声纳库与市场数据集成
    
    提供完整的市场数据获取 -> 指标计算 -> 声纳扫描流程
    """
    
    def __init__(self, api_key: str = None, api_secret: str = None):
        self.fetcher = MarketDataFetcher(api_key, api_secret)
        
    def scan(self, symbol: str, timeframe: str = "15m", 
             use_cache: bool = True) -> Optional[Dict]:
        """
        完整扫描流程
        
        Args:
            symbol: 交易对
            timeframe: 时间框架
            use_cache: 是否使用缓存
            
        Returns:
            Dict with scan results
        """
        if use_cache:
            indicators = self.fetcher.get_indicators(symbol, timeframe)
        else:
            # 清除缓存
            self.fetcher.cache.clear()
            indicators = self.fetcher.get_indicators(symbol, timeframe)
        
        if not indicators:
            return None
        
        return {
            'symbol': symbol,
            'timeframe': timeframe,
            'indicators': indicators,
            'timestamp': datetime.now().isoformat()
        }
    
    def multi_scan(self, symbols: List[str], timeframe: str = "15m") -> List[Dict]:
        """多交易对扫描"""
        results = []
        
        for symbol in symbols:
            try:
                result = self.scan(symbol, timeframe)
                if result:
                    results.append(result)
            except Exception as e:
                print(f"Error in multi_scan for {symbol}: {e}")
        
        return results


# ==================== 便捷函数 ====================

def create_market_fetcher(api_key: str = None, api_secret: str = None) -> MarketDataFetcher:
    """创建市场数据获取器"""
    return MarketDataFetcher(api_key, api_secret)


def create_sonar_integration(api_key: str = None, api_secret: str = None) -> SonarMarketIntegration:
    """创建声纳库集成"""
    return SonarMarketIntegration(api_key, api_secret)


def get_binance_symbols(quote: str = "USDT") -> List[str]:
    """获取Binance交易对列表"""
    try:
        exchange = ccxt.binance({'enableRateLimit': True})
        markets = exchange.load_markets()
        
        symbols = []
        for symbol in markets.keys():
            if symbol.endswith(f"/{quote}"):
                symbols.append(symbol)
        
        return symbols
    except Exception as e:
        print(f"Error loading Binance markets: {e}")
        return ["BTC/USDT", "ETH/USDT", "BNB/USDT"]


# ==================== 主函数 ====================

def main():
    """主函数 - 测试"""
    print("=" * 60)
    print("📊 市场数据获取器测试")
    print("=" * 60)
    
    # 创建市场数据获取器
    fetcher = MarketDataFetcher()
    
    # 测试获取数据
    print("\n📈 获取 BTC/USDT 15分钟K线数据...")
    ohlcv = fetcher.get_ohlcv("BTC/USDT", "15m", limit=100)
    print(f"   获取到 {len(ohlcv)} 根K线")
    
    if len(ohlcv) > 0:
        print(f"   最新K线: {ohlcv[-1]}")
    
    # 计算技术指标
    print("\n📊 计算技术指标...")
    indicators = fetcher.get_indicators("BTC/USDT", "15m")
    
    if indicators:
        print(f"""
   价格信息:
     当前价格: {indicators.close}
     开盘价: {indicators.open}
     最高价: {indicators.high}
     最低价: {indicators.low}
     涨跌幅: {indicators.price_change_pct:.2f}%
   
   RSI指标:
     RSI(14): {indicators.rsi_14:.2f}
     RSI(7): {indicators.rsi_7:.2f}
     RSI(3): {indicators.rsi_3:.2f}
   
   MACD指标:
     MACD: {indicators.macd:.2f}
     Signal: {indicators.macd_signal:.2f}
     Histogram: {indicators.macd_histogram:.2f}
   
   均线:
     SMA20: {indicators.sma20:.2f}
     SMA50: {indicators.sma50:.2f}
     SMA200: {indicators.sma200:.2f}
     EMA9: {indicators.ema9:.2f}
     EMA21: {indicators.ema21:.2f}
   
   布林带:
     上轨: {indicators.bb_upper:.2f}
     中轨: {indicators.bb_middle:.2f}
     下轨: {indicators.bb_lower:.2f}
     带宽: {indicators.bb_width:.4f}
     %B: {indicators.bb_percent:.2f}
   
   ATR:
     ATR: {indicators.atr:.2f}
     ATR%: {indicators.atr_pct:.4f}
   
   ADX:
     ADX: {indicators.adx:.2f}
     +DI: {indicators.plus_di:.2f}
     -DI: {indicators.minus_di:.2f}
   
   成交量:
     当前成交量: {indicators.volume:.2f}
     成交量MA: {indicators.volume_ma:.2f}
     成交量比: {indicators.volume_ratio:.2f}
   
   OBV:
     OBV: {indicators.obv:.2f}
     OBV MA: {indicators.obv_ma:.2f}
   
   VWAP:
     VWAP: {indicators.vwap:.2f}
     偏离: {indicators.vwap_deviation:.4f}
   
   Williams %R:
     WR: {indicators.williams_r:.2f}
   
   CCI:
     CCI: {indicators.cci:.2f}
   
   Stochastic:
     K: {indicators.stochastic_k:.2f}
     D: {indicators.stochastic_d:.2f}
   
   市场状态: {indicators.market_regime.value}
   状态置信度: {indicators.regime_confidence:.2f}
   
   综合评分:
     动量: {indicators.momentum_score:.1f}
     趋势: {indicators.trend_score:.1f}
     波动率: {indicators.volatility_score:.1f}
     成交量: {indicators.volume_score:.1f}
""")
    
    # 测试多时间框架
    print("\n⏱️ 多时间框架指标...")
    mt_indicators = fetcher.get_multi_timeframe_indicators("BTC/USDT", ["5m", "15m", "1h", "4h"])
    for tf, ind in mt_indicators.items():
        print(f"   {tf}: RSI={ind.rsi:.1f}, MACD={ind.macd:.1f}, 趋势={ind.market_regime.value}")
    
    # 批量获取
    print("\n📦 批量获取多个交易对...")
    symbols = ["BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT"]
    batch_results = fetcher.get_batch_indicators(symbols, "15m")
    for symbol, ind in batch_results.items():
        if ind:
            print(f"   {symbol}: 价格={ind.close:.2f}, RSI={ind.rsi:.1f}, 涨跌幅={ind.price_change_pct:.2f}%")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
