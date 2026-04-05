"""
声纳库 v2 - 基础模块
包含: 配置常量、工具函数、基础类
2026-04-04 重构版本
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import math

# ==================== 常量配置 ====================

BINANCE_BASE = "https://api.binance.com/api/v3"

TREND_CATEGORIES = {
    "ema": ["EMA5", "EMA10", "EMA20", "EMA50", "EMA200"],
    "ma": ["MA10", "MA20", "MA50", "MA200", "SMA10", "SMA20"],
    "macd": ["MACD", "MACD_Signal", "MACD_Hist"],
    "bollinger": ["BB_Upper", "BB_Middle", "BB_Lower"],
    "volume": ["OBV", "VWAP", "Volume_MA"],
    "momentum": ["RSI", "Stochastic", "CCI", "Williams_%R", "ADX"],
    "channel": ["Channel_High", "Channel_Low", "Channel_Middle"],
    "ichimoku": ["Ichimoku_Tenkan", "Ichimoku_Kijun", "Ichimoku_Span"]
}

TREND_THRESHOLDS = {
    "strong_bullish": 0.75,
    "bullish": 0.65,
    "neutral": 0.50,
    "bearish": 0.35,
    "strong_bearish": 0.25
}

SIGNAL_WEIGHTS = {
    "ema_cross": 1.5,
    "macd_cross": 1.3,
    "rsi_extreme": 1.2,
    "bollinger_break": 1.1,
    "volume_spike": 1.0
}

@dataclass
class TrendModel:
    name: str
    category: str
    weight: float
    enabled: bool = True

@dataclass  
class Signal:
    symbol: str
    model: str
    direction: str  # bullish, bearish, neutral
    confidence: float  # 0.0 - 1.0
    price: float
    timestamp: str

class TrendCategory(Enum):
    TREND = "trend"
    MOMENTUM = "momentum"
    VOLATILITY = "volatility"
    VOLUME = "volume"
    REVERSAL = "reversal"

# ==================== 工具函数 ====================

def calculate_ema(prices: List[float], period: int) -> float:
    """计算指数移动平均"""
    if len(prices) < period:
        return sum(prices) / len(prices) if prices else 0
    
    multiplier = 2 / (period + 1)
    ema = sum(prices[:period]) / period
    
    for price in prices[period:]:
        ema = (price - ema) * multiplier + ema
    
    return ema

def calculate_rsi(prices: List[float], period: int = 14) -> float:
    """计算RSI指标"""
    if len(prices) < period + 1:
        return 50.0
    
    gains = []
    losses = []
    
    for i in range(1, len(prices)):
        change = prices[i] - prices[i-1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

def calculate_macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[float, float, float]:
    """计算MACD (MACD线, Signal线, Histogram)"""
    if len(prices) < slow:
        return 0.0, 0.0, 0.0
    
    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)
    macd_line = ema_fast - ema_slow
    
    # Signal line is EMA of MACD line (simplified)
    signal_line = macd_line * 0.9  # approximation
    
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram

def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2.0) -> Tuple[float, float, float]:
    """计算布林带 (Upper, Middle, Lower)"""
    if len(prices) < period:
        return 0.0, 0.0, 0.0
    
    middle = sum(prices[-period:]) / period
    
    variance = sum((p - middle) ** 2 for p in prices[-period:]) / period
    std = math.sqrt(variance)
    
    upper = middle + (std_dev * std)
    lower = middle - (std_dev * std)
    
    return upper, middle, lower

def calculate_volatility(prices: List[float], period: int = 20) -> float:
    """计算历史波动率"""
    if len(prices) < period:
        return 0.0
    
    returns = []
    for i in range(1, len(prices)):
        ret = (prices[i] - prices[i-1]) / prices[i-1]
        returns.append(ret)
    
    if len(returns) < 2:
        return 0.0
    
    mean = sum(returns) / len(returns)
    variance = sum((r - mean) ** 2 for r in returns) / len(returns)
    
    return math.sqrt(variance * 252)  # 年化波动率

def normalize_confidence(raw: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """归一化置信度到0-1范围"""
    normalized = (raw - min_val) / (max_val - min_val) if max_val > min_val else 0.5
    return max(0.0, min(1.0, normalized))

def get_signal_direction(indicators: Dict[str, float], thresholds: Dict[str, float]) -> str:
    """根据指标判断信号方向"""
    bullish_count = 0
    bearish_count = 0
    
    for name, value in indicators.items():
        if "bullish" in name or value > thresholds.get("bullish", 0.6):
            bullish_count += 1
        elif "bearish" in name or value < thresholds.get("bearish", 0.4):
            bearish_count += 1
    
    if bullish_count > bearish_count * 1.5:
        return "bullish"
    elif bearish_count > bullish_count * 1.5:
        return "bearish"
    return "neutral"
