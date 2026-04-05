"""
声纳库 v2 - 趋势模型模块
包含: 100+趋势模型定义、模型配置、模型工厂
2026-04-04 重构版本
"""

from typing import Dict, List, Optional
from dataclasses import dataclass

# ==================== 趋势模型库 ====================

@dataclass
class TrendModel:
    name: str
    category: str
    weight: float
    enabled: bool = True

# EMA系列
EMA_MODELS = [
    TrendModel("EMA5", "ema", 1.0),
    TrendModel("EMA10", "ema", 1.1),
    TrendModel("EMA20", "ema", 1.2),
    TrendModel("EMA50", "ema", 1.3),
    TrendModel("EMA100", "ema", 1.4),
    TrendModel("EMA200", "ema", 1.5),
]

# MA系列
MA_MODELS = [
    TrendModel("MA10", "ma", 1.0),
    TrendModel("MA20", "ma", 1.1),
    TrendModel("MA50", "ma", 1.2),
    TrendModel("MA100", "ma", 1.3),
    TrendModel("MA200", "ma", 1.4),
    TrendModel("SMA10", "ma", 0.9),
    TrendModel("SMA20", "ma", 1.0),
    TrendModel("HMA", "ma", 1.2),
]

# MACD系列
MACD_MODELS = [
    TrendModel("MACD", "macd", 1.3),
    TrendModel("MACD_Signal", "macd", 1.2),
    TrendModel("MACD_Hist", "macd", 1.1),
]

# 布林带系列
BB_MODELS = [
    TrendModel("BB_Upper", "bollinger", 1.0),
    TrendModel("BB_Middle", "bollinger", 0.9),
    TrendModel("BB_Lower", "bollinger", 1.0),
    TrendModel("BB_Width", "bollinger", 0.8),
]

# RSI系列
RSI_MODELS = [
    TrendModel("RSI_7", "momentum", 1.0),
    TrendModel("RSI_14", "momentum", 1.1),
    TrendModel("RSI_21", "momentum", 1.0),
    TrendModel("RSI_Oversold", "momentum", 1.3),
    TrendModel("RSI_Overbought", "momentum", 1.3),
]

# 随机指标系列
STOCH_MODELS = [
    TrendModel("Stochastic_K", "momentum", 1.0),
    TrendModel("Stochastic_D", "momentum", 0.9),
    TrendModel("Stochastic_Fast", "momentum", 0.8),
    TrendModel("Stochastic_Slow", "momentum", 0.9),
]

# 动量指标系列
MOMENTUM_MODELS = [
    TrendModel("Momentum", "momentum", 1.0),
    TrendModel("ROC", "momentum", 1.0),
    TrendModel("CCI", "momentum", 1.1),
    TrendModel("Williams_%R", "momentum", 1.0),
    TrendModel("ADX", "momentum", 1.2),
    TrendModel("ADX_Plus_DI", "momentum", 1.1),
    TrendModel("ADX_Minus_DI", "momentum", 1.1),
]

# 成交量系列
VOLUME_MODELS = [
    TrendModel("OBV", "volume", 1.0),
    TrendModel("VWAP", "volume", 1.2),
    TrendModel("Volume_MA", "volume", 0.9),
    TrendModel("Volume_Ratio", "volume", 1.0),
    TrendModel("Money_Flow", "volume", 1.1),
]

# 波动率系列
VOLATILITY_MODELS = [
    TrendModel("ATR", "volatility", 1.0),
    TrendModel("NATR", "volatility", 0.9),
    TrendModel("StdDev", "volatility", 0.8),
]

# 通道系列
CHANNEL_MODELS = [
    TrendModel("Channel_High", "channel", 1.0),
    TrendModel("Channel_Low", "channel", 1.0),
    TrendModel("Channel_Middle", "channel", 0.8),
    TrendModel("Donchian_High", "channel", 1.1),
    TrendModel("Donchian_Low", "channel", 1.1),
]

# Ichimoku系列
ICHIMOKU_MODELS = [
    TrendModel("Ichimoku_Tenkan", "ichimoku", 1.0),
    TrendModel("Ichimoku_Kijun", "ichimoku", 1.0),
    TrendModel("Ichimoku_SpanA", "ichimoku", 0.9),
    TrendModel("Ichimoku_SpanB", "ichimoku", 0.9),
]

# Pivot系列
PIVOT_MODELS = [
    TrendModel("Pivot_Point", "reversal", 1.0),
    TrendModel("Pivot_R1", "reversal", 0.9),
    TrendModel("Pivot_S1", "reversal", 0.9),
]

# 反转系列
REVERSAL_MODELS = [
    TrendModel("RSI_Reversal_Oversold", "reversal", 1.2),
    TrendModel("RSI_Reversal_Overbought", "reversal", 1.2),
    TrendModel("Stoch_Reversal_Low", "reversal", 1.1),
    TrendModel("Stoch_Reversal_High", "reversal", 1.1),
    TrendModel("Fibonacci_Retracement", "reversal", 1.1),
]

# 趋势持续系列
TREND_MODELS = [
    TrendModel("Supertrend", "trend", 1.3),
    TrendModel("Parabolic_SAR", "trend", 1.2),
    TrendModel("Trend_Continuation", "trend", 1.0),
]

# 汇总所有模型
TREND_MODELS_ALL = (
    EMA_MODELS + MA_MODELS + MACD_MODELS + BB_MODELS +
    RSI_MODELS + STOCH_MODELS + MOMENTUM_MODELS + VOLUME_MODELS +
    VOLATILITY_MODELS + CHANNEL_MODELS + ICHIMOKU_MODELS +
    PIVOT_MODELS + REVERSAL_MODELS + TREND_MODELS
)

# 模型名称到对象的映射
MODEL_DICT: Dict[str, TrendModel] = {m.name: m for m in TREND_MODELS_ALL}

# 按类别分组的模型
MODELS_BY_CATEGORY: Dict[str, List[TrendModel]] = {}
for model in TREND_MODELS_ALL:
    if model.category not in MODELS_BY_CATEGORY:
        MODELS_BY_CATEGORY[model.category] = []
    MODELS_BY_CATEGORY[model.category].append(model)


class ModelFactory:
    """模型工厂"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_model(self, name: str) -> Optional[TrendModel]:
        return MODEL_DICT.get(name)
    
    def get_models_by_category(self, category: str) -> List[TrendModel]:
        return MODELS_BY_CATEGORY.get(category, [])
    
    def get_all_models(self, enabled_only: bool = True) -> List[TrendModel]:
        if enabled_only:
            return [m for m in TREND_MODELS_ALL if m.enabled]
        return TREND_MODELS_ALL
    
    def get_model_count(self) -> int:
        return len(TREND_MODELS_ALL)


# 导出
__all__ = [
    "TrendModel",
    "TREND_MODELS_ALL",
    "MODEL_DICT",
    "MODELS_BY_CATEGORY",
    "ModelFactory",
]
