"""
声纳库 V2 - 核心模块
====================

包含:
- sonar/: 新模块化声纳库 (base, models, scanner)
- sonar_v2_legacy: 旧版 (已废弃，保留备查)
- market_data_fetcher: 市场数据获取器
"""

# 新模块化声纳库 (v2.0)
from .sonar import (
    SonarScanner,
    SonarLibrary,
    ScanResult,
    Signal,
    TrendModel,
    TrendCategory,
    calculate_ema,
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
    calculate_volatility,
    ModelFactory,
)

# 兼容旧接口 (指向旧版保留备查)
from .sonar_v2_legacy import (
    SonarLibraryV2,
    TrendModelLibrary,
    HierarchicalScanner,
    MarketIndicators,
    MatchResult,
    ScanResult as LegacyScanResult,
    SignalType,
    TrendDirection,
    MarketRegime,
    ModelCategory,
    create_sonar_library,
)

from .market_data_fetcher import (
    MarketDataFetcher,
    TechnicalIndicators,
    SonarMarketIntegration,
    OHLCV,
    create_market_fetcher,
    create_sonar_integration,
    get_binance_symbols,
)

# 打地鼠策略 V4 (双引擎)
from .mole_v4_strategy import (
    MoleV4Strategy,
    MoleV4Config,
    CombinedSignal,
)

# 跨市场套利
from .cross_market_arbitrage import (
    CrossMarketArbitrage,
    ArbitrageOpportunity,
)

__all__ = [
    # sonar_v2
    "SonarLibraryV2",
    "TrendModelLibrary",
    "HierarchicalScanner",
    "MarketIndicators",
    "TrendModel",
    "MatchResult",
    "ScanResult",
    "SignalType",
    "TrendDirection",
    "MarketRegime",
    "ModelCategory",
    "create_sonar_library",
    # market_data_fetcher
    "MarketDataFetcher",
    "TechnicalIndicators",
    "SonarMarketIntegration",
    "OHLCV",
    "create_market_fetcher",
    "create_sonar_integration",
    "get_binance_symbols",
]
