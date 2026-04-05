"""
声纳库 v2 - 重构后的模块化结构
2026-04-04

模块结构:
- base.py: 基础配置、常量、工具函数
- models.py: 趋势模型定义 (60+模型)
- scanner.py: 信号扫描器和分析器
"""

from .base import (
    Signal,
    TrendModel,
    TrendCategory,
    TREND_THRESHOLDS,
    SIGNAL_WEIGHTS,
    calculate_ema,
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
    calculate_volatility,
    normalize_confidence,
)

from .models import (
    TrendModel,
    TREND_MODELS_ALL,
    MODEL_DICT,
    MODELS_BY_CATEGORY,
    ModelFactory,
)

from .scanner import (
    ScanResult,
    SonarScanner,
    SonarLibrary,
)

__version__ = "2.0.0"
__all__ = [
    # base
    "Signal",
    "TrendModel", 
    "TrendCategory",
    "TREND_THRESHOLDS",
    "SIGNAL_WEIGHTS",
    "calculate_ema",
    "calculate_rsi",
    "calculate_macd",
    "calculate_bollinger_bands",
    "calculate_volatility",
    "normalize_confidence",
    # models
    "TREND_MODELS_ALL",
    "MODEL_DICT",
    "MODELS_BY_CATEGORY",
    "ModelFactory",
    # scanner
    "ScanResult",
    "SonarScanner",
    "SonarLibrary",
]
