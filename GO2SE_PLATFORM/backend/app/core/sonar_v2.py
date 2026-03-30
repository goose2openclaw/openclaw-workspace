"""
声纳库 V2 - 100+趋势模型 + 分层扫描
===================================

设计理念:
1. 定焦扫描: 当收到信号时，直接与对应的可能趋势模型组进行比对
2. 分层筛选: 广泛匹配 -> 锁定目标 -> 概率输出 -> 触发策略
3. 持续精进: 每次匹配后更新模型权重，不断优化判断精度

三层扫描架构:
┌─────────────────────────────────────────────────────────┐
│  Layer 1: 粗筛 (Coarse Scan)                            │
│  - 识别信号类型 (动量/突破/反转/波动率/成交量/趋势)      │
│  - 快速排除80%不匹配的模型                              │
├─────────────────────────────────────────────────────────┤
│  Layer 2: 精筛 (Fine Scan)                              │
│  - 在匹配的模型组内进行详细比对                         │
│  - 计算条件满足度和置信度                               │
├─────────────────────────────────────────────────────────┤
│  Layer 3: 决策 (Decision)                               │
│  - 多模型共识投票                                       │
│  - 高置信度触发策略                                     │
└─────────────────────────────────────────────────────────┘
"""

import json
import math
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from collections import defaultdict

# ==================== 数据结构 ====================

class SignalType(Enum):
    """信号类型"""
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    NEUTRAL = "NEUTRAL"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"

class TrendDirection(Enum):
    """趋势方向"""
    BULL = "BULL"
    BEAR = "BEAR"
    SIDEWAYS = "SIDEWAYS"

class ModelCategory(Enum):
    """模型类别"""
    MOMENTUM = "动量"      # 动量模型
    BREAKOUT = "突破"      # 突破模型
    REVERSAL = "反转"      # 反转模型
    VOLATILITY = "波动率"  # 波动率模型
    VOLUME = "成交量"      # 成交量模型
    TREND = "趋势"         # 趋势模型
    MACRO = "宏观"         # 宏观模型
    ONCHAIN = "链上"       # 链上模型

@dataclass
class TrendModel:
    """趋势模型"""
    name: str
    category: str
    conditions: Dict[str, Any]
    confidence: int  # 1-10 基础置信度
    timeframes: List[str]
    indicators: List[str]  # 需要的指标
    description: str = ""
    success_rate: float = 0.5  # 历史胜率
    match_count: int = 0        # 匹配次数
    last_matched: str = ""      # 上次匹配时间

@dataclass
class MatchResult:
    """匹配结果"""
    model_name: str
    model: TrendModel
    match_score: float          # 0-1 匹配度
    conditions_met: List[str]   # 满足的条件
    conditions_failed: List[str] # 未满足的条件
    direction: TrendDirection    # 趋势方向
    timeframe_scores: Dict[str, float]  # 各时间框架得分

@dataclass
class ScanResult:
    """扫描结果"""
    symbol: str
    timestamp: str
    layer1_candidates: List[str]     # Layer1 候选类别
    layer2_matches: List[MatchResult]  # Layer2 匹配结果
    final_signal: Optional[SignalType] = None
    final_confidence: float = 0.0
    direction: TrendDirection = TrendDirection.SIDEWAYS
    triggered_strategy: str = ""
    models_voted: List[str] = field(default_factory=list)
    multi_timeframe_confirmed: bool = False

@dataclass
class MarketIndicators:
    """市场指标"""
    # 价格指标
    close: float = 0.0
    open: float = 0.0
    high: float = 0.0
    low: float = 0.0
    price_change_pct: float = 0.0
    
    # RSI
    rsi: float = 50.0
    rsi_14: float = 50.0
    rsi_7: float = 50.0
    
    # MACD
    macd: float = 0.0
    macd_signal: float = 0.0
    macd_histogram: float = 0.0
    
    # 均线
    sma5: float = 0.0
    sma10: float = 0.0
    sma20: float = 0.0
    sma50: float = 0.0
    sma200: float = 0.0
    ema9: float = 0.0
    ema12: float = 0.0
    ema21: float = 0.0
    ema26: float = 0.0
    
    # 布林带
    bb_upper: float = 0.0
    bb_middle: float = 0.0
    bb_lower: float = 0.0
    bb_width: float = 0.0
    
    # ATR
    atr: float = 0.0
    atr_pct: float = 0.0
    
    # ADX
    adx: float = 0.0
    plus_di: float = 0.0
    minus_di: float = 0.0
    
    # 成交量
    volume: float = 0.0
    volume_ma: float = 0.0
    volume_ratio: float = 1.0
    
    # OBV
    obv: float = 0.0
    obv_ma: float = 0.0
    
    # VWAP
    vwap: float = 0.0
    
    # 威廉指标
    williams_r: float = -50.0
    
    # CCI
    cci: float = 0.0
    
    # 随机指标
    stochastic_k: float = 50.0
    stochastic_d: float = 50.0

# ==================== 趋势模型库 ====================

class TrendModelLibrary:
    """趋势模型库 - 包含100+趋势模型"""
    
    def __init__(self, db_path: str = None):
        self.models: Dict[str, TrendModel] = {}
        self.models_by_category: Dict[str, List[TrendModel]] = defaultdict(list)
        self.models_by_timeframe: Dict[str, List[TrendModel]] = defaultdict(list)
        self.category_indicators: Dict[str, List[str]] = {}  # 各类别需要的指标
        
        # 加载模型
        if db_path:
            self._load_from_json(db_path)
        else:
            self._init_all_models()
        
        self._build_indexes()
        
    def _load_from_json(self, db_path: str):
        """从JSON文件加载趋势模型"""
        try:
            with open(db_path, 'r') as f:
                data = json.load(f)
            
            # 加载所有类别的趋势模型
            for category, models_data in data.items():
                if category.endswith('_trends') and isinstance(models_data, dict):
                    for model_name, model_info in models_data.items():
                        if isinstance(model_info, dict):
                            model = TrendModel(
                                name=model_name,
                                category=category.replace('_trends', ''),
                                conditions=model_info.get('conditions', {}),
                                confidence=model_info.get('confidence', 5),
                                timeframes=list(model_info.get('timeframes', {}).keys()),
                                indicators=model_info.get('indicators', []),
                                description=model_info.get('name', model_name),
                                success_rate=model_info.get('success_rate', 0.5),
                                match_count=model_info.get('match_count', 0),
                                last_matched=model_info.get('last_matched', '')
                            )
                            self.models[model_name] = model
        except Exception as e:
            print(f"Failed to load models from {db_path}: {e}")
            self._init_all_models()
    
    def _init_all_models(self):
        """初始化所有100+趋势模型"""
        
        # ===== 动量模型 (15个) =====
        momentum_models = [
            TrendModel("momentum_bull_1m", "动量", {"rsi_above_50": True, "price_above_sma20": True}, 3, ["1m"], ["rsi", "sma20"], "1分钟多头动量"),
            TrendModel("momentum_bull_5m", "动量", {"rsi_above_50": True, "price_above_sma20": True, "macd_bullish": True}, 5, ["5m"], ["rsi", "sma20", "macd"], "5分钟多头动量"),
            TrendModel("momentum_bull_15m", "动量", {"rsi_above_50": True, "price_above_sma20": True, "macd_bullish": True, "adx_above_25": True}, 7, ["15m"], ["rsi", "sma20", "macd", "adx"], "15分钟多头动量"),
            TrendModel("momentum_bear_1m", "动量", {"rsi_below_50": True, "price_below_sma20": True}, 3, ["1m"], ["rsi", "sma20"], "1分钟空头动量"),
            TrendModel("momentum_bear_5m", "动量", {"rsi_below_50": True, "price_below_sma20": True, "macd_bearish": True}, 5, ["5m"], ["rsi", "sma20", "macd"], "5分钟空头动量"),
            TrendModel("momentum_bear_15m", "动量", {"rsi_below_50": True, "price_below_sma20": True, "macd_bearish": True, "adx_above_25": True}, 7, ["15m"], ["rsi", "sma20", "macd", "adx"], "15分钟空头动量"),
            TrendModel("strong_momentum", "动量", {"rsi_range": [40, 70], "macd_histogram_increasing": True, "volume_increasing": True}, 8, ["5m", "15m", "1h"], ["rsi", "macd", "volume"], "强势动量"),
            TrendModel("weak_momentum", "动量", {"rsi_range": [30, 70], "macd_histogram_decreasing": True}, 4, ["5m", "15m"], ["rsi", "macd"], "弱势动量"),
            TrendModel("acceleration_bull", "动量", {"price_acceleration": "positive", "volume_surge": True, "rsi_above_60": True}, 8, ["5m", "15m"], ["rsi", "volume"], "加速上涨"),
            TrendModel("acceleration_bear", "动量", {"price_acceleration": "negative", "volume_surge": True, "rsi_below_40": True}, 8, ["5m", "15m"], ["rsi", "volume"], "加速下跌"),
            TrendModel("momentum_divergence_bull", "动量", {"price_lower_low": True, "rsi_higher_low": True}, 7, ["15m", "1h"], ["rsi", "price"], "底背离"),
            TrendModel("momentum_divergence_bear", "动量", {"price_higher_high": True, "rsi_lower_high": True}, 7, ["15m", "1h"], ["rsi", "price"], "顶背离"),
            TrendModel("hidden_divergence_bull", "动量", {"price_lower_high": True, "rsi_higher_low": True}, 6, ["15m", "1h"], ["rsi", "price"], "隐藏底背离"),
            TrendModel("hidden_divergence_bear", "动量", {"price_higher_low": True, "rsi_lower_high": True}, 6, ["15m", "1h"], ["rsi", "price"], "隐藏顶背离"),
            TrendModel("momentum_exhaustion", "动量", {"rsi_extreme": True, "volume_declining": True, "price_range_narrow": True}, 5, ["1h", "4h"], ["rsi", "volume"], "动量衰竭"),
        ]
        
        # ===== 突破模型 (15个) =====
        breakout_models = [
            TrendModel("breakout_up_strong", "突破", {"price_breaks_high": True, "volume_surge_2x": True}, 7, ["15m", "1h"], ["price", "volume"], "强势突破上涨"),
            TrendModel("breakout_up_weak", "突破", {"price_breaks_high": True, "volume_normal": True}, 5, ["15m", "1h"], ["price", "volume"], "弱势突破上涨"),
            TrendModel("breakout_down_strong", "突破", {"price_breaks_low": True, "volume_surge_2x": True}, 7, ["15m", "1h"], ["price", "volume"], "强势突破下跌"),
            TrendModel("breakout_down_weak", "突破", {"price_breaks_low": True, "volume_normal": True}, 5, ["15m", "1h"], ["price", "volume"], "弱势突破下跌"),
            TrendModel("breakout_volume_surge", "突破", {"volume_surge_3x": True, "price_change_5pct": True}, 6, ["5m", "15m"], ["volume", "price"], "成交量突破"),
            TrendModel("breakout_resistance", "突破", {"price_breaks_resistance": True, "volume_increasing": True}, 7, ["1h", "4h"], ["price", "volume"], "阻力位突破"),
            TrendModel("breakout_support", "突破", {"price_breaks_support": True, "volume_increasing": True}, 7, ["1h", "4h"], ["price", "volume"], "支撑位突破"),
            TrendModel("false_breakout_up", "突破", {"price_breaks_high": True, "closes_below_resistance": True}, 4, ["15m", "1h"], ["price"], "假突破上涨"),
            TrendModel("false_breakout_down", "突破", {"price_breaks_low": True, "closes_above_support": True}, 4, ["15m", "1h"], ["price"], "假突破下跌"),
            TrendModel("breakout_continuation_bull", "突破", {"breakout_confirmed": True, "retest_success": True, "volume_surge": True}, 8, ["1h", "4h"], ["price", "volume"], "突破延续"),
            TrendModel("breakout_continuation_bear", "突破", {"breakout_confirmed": True, "retest_success": True, "volume_surge": True}, 8, ["1h", "4h"], ["price", "volume"], "下跌延续"),
            TrendModel("range_breakout_up", "突破", {"price_range_bound": True, "breakout_direction": "up"}, 6, ["15m", "1h"], ["price"], "区间突破上涨"),
            TrendModel("range_breakout_down", "突破", {"price_range_bound": True, "breakout_direction": "down"}, 6, ["15m", "1h"], ["price"], "区间突破下跌"),
            TrendModel("triangle_breakout_up", "突破", {"triangle_pattern": True, "breakout_direction": "up"}, 7, ["1h", "4h"], ["price"], "三角形突破上涨"),
            TrendModel("triangle_breakout_down", "突破", {"triangle_pattern": True, "breakout_direction": "down"}, 7, ["1h", "4h"], ["price"], "三角形突破下跌"),
        ]
        
        # ===== 反转模型 (15个) =====
        reversal_models = [
            TrendModel("reversal_bull_strong", "反转", {"rsi_oversold": True, "price_bounces": True, "volume_increasing": True}, 7, ["15m", "1h"], ["rsi", "price", "volume"], "强势反转做多"),
            TrendModel("reversal_bull_weak", "反转", {"rsi_oversold": True, "price_bounces": True}, 5, ["15m", "1h"], ["rsi", "price"], "弱势反转做多"),
            TrendModel("reversal_bear_strong", "反转", {"rsi_overbought": True, "price_rejects": True, "volume_increasing": True}, 7, ["15m", "1h"], ["rsi", "price", "volume"], "强势反转做空"),
            TrendModel("reversal_bear_weak", "反转", {"rsi_overbought": True, "price_rejects": True}, 5, ["15m", "1h"], ["rsi", "price"], "弱势反转做空"),
            TrendModel("double_bottom", "反转", {"price_double_bottom": True, "volume_second_low_lower": True}, 7, ["1h", "4h"], ["price", "volume"], "双底"),
            TrendModel("double_top", "反转", {"price_double_top": True, "volume_second_top_higher": True}, 7, ["1h", "4h"], ["price", "volume"], "双顶"),
            TrendModel("head_shoulders_bull", "反转", {"head_shoulders_pattern": "bullish"}, 7, ["1h", "4h"], ["price"], "头肩底"),
            TrendModel("head_shoulders_bear", "反转", {"head_shoulders_pattern": "bearish"}, 7, ["1h", "4h"], ["price"], "头肩顶"),
            TrendModel("wedge_falling_wedge", "反转", {"falling_wedge": True, "breakout_up": True}, 7, ["1h", "4h"], ["price"], "下降楔形"),
            TrendModel("wedge_rising_wedge", "反转", {"rising_wedge": True, "breakout_down": True}, 7, ["1h", "4h"], ["price"], "上升楔形"),
            TrendModel("bottom_divergence", "反转", {"price_makes_low": True, "indicator_higher_low": True}, 6, ["1h", "4h"], ["rsi", "price"], "底部背离"),
            TrendModel("top_divergence", "反转", {"price_makes_high": True, "indicator_lower_high": True}, 6, ["1h", "4h"], ["rsi", "price"], "顶部背离"),
            TrendModel("rsi_oversold_bounce", "反转", {"rsi_below_30": True, "rsi_turning_up": True}, 6, ["5m", "15m"], ["rsi"], "RSI超卖反弹"),
            TrendModel("rsi_overbought_dump", "反转", {"rsi_above_70": True, "rsi_turning_down": True}, 6, ["5m", "15m"], ["rsi"], "RSI超买回落"),
            TrendModel("support_bounce", "反转", {"price_hits_support": True, "bounces_from_support": True, "volume_increasing": True}, 7, ["15m", "1h"], ["price", "volume"], "支撑位反弹"),
        ]
        
        # ===== 波动率模型 (10个) =====
        volatility_models = [
            TrendModel("volatility_squeeze", "波动率", {"bb_squeeze": True, "atr_low": True}, 5, ["15m", "1h"], ["bb_width", "atr"], "波动率挤压"),
            TrendModel("volatility_expansion", "波动率", {"bb_expansion": True, "atr_high": True}, 6, ["15m", "1h"], ["bb_width", "atr"], "波动率扩张"),
            TrendModel("bb_squeeze_bull", "波动率", {"bb_squeeze": True, "price_breaks_up": True}, 7, ["15m", "1h"], ["bb_width", "price"], "布林带挤压上涨"),
            TrendModel("bb_squeeze_bear", "波动率", {"bb_squeeze": True, "price_breaks_down": True}, 7, ["15m", "1h"], ["bb_width", "price"], "布林带挤压下跌"),
            TrendModel("atr_breakout_up", "波动率", {"atr_surge": True, "price_up": True}, 6, ["15m", "1h"], ["atr", "price"], "ATR突破上涨"),
            TrendModel("atr_breakout_down", "波动率", {"atr_surge": True, "price_down": True}, 6, ["15m", "1h"], ["atr", "price"], "ATR突破下跌"),
            TrendModel("volatility_regime_change", "波动率", {"volatility_increases": True, "volume_surge": True}, 5, ["1h", "4h"], ["bb_width", "volume"], "波动率制度转换"),
            TrendModel("low_volatility_accumulation", "波动率", {"low_volatility": True, "volume_stable": True, "price_range": True}, 5, ["4h", "1d"], ["bb_width", "volume"], "低波动积累"),
            TrendModel("high_volatility_distribution", "波动率", {"high_volatility": True, "volume_increasing": True, "price_range_wide": True}, 5, ["4h", "1d"], ["bb_width", "volume", "price"], "高波动分配"),
            TrendModel("volatility_cluster", "波动率", {"consecutive_volatile_candles": 3, "same_direction": True}, 4, ["5m", "15m"], ["atr"], "波动率聚集"),
        ]
        
        # ===== 成交量模型 (10个) =====
        volume_models = [
            TrendModel("volume_surge_bull", "成交量", {"volume_surge_2x": True, "price_up": True}, 6, ["5m", "15m"], ["volume_ratio", "price"], "成交量激增上涨"),
            TrendModel("volume_surge_bear", "成交量", {"volume_surge_2x": True, "price_down": True}, 6, ["5m", "15m"], ["volume_ratio", "price"], "成交量激增下跌"),
            TrendModel("volume_dry_up", "成交量", {"volume_below_average": True, "price_range_narrow": True}, 4, ["1h", "4h"], ["volume_ratio"], "成交量枯竭"),
            TrendModel("obv_divergence_bull", "成交量", {"obv_increasing": True, "price_decreasing": True}, 6, ["15m", "1h"], ["obv", "price"], "OBV底背离"),
            TrendModel("obv_divergence_bear", "成交量", {"obv_decreasing": True, "price_increasing": True}, 6, ["15m", "1h"], ["obv", "price"], "OBV顶背离"),
            TrendModel("vwap_rejection", "成交量", {"price_rejects_vwap": True, "volume_increasing": True}, 6, ["5m", "15m"], ["vwap", "volume"], "VWAP拒绝"),
            TrendModel("vwap_bounce", "成交量", {"price_bounces_vwap": True, "volume_increasing": True}, 6, ["5m", "15m"], ["vwap", "volume"], "VWAP反弹"),
            TrendModel("volume_price_trend_bull", "成交量", {"vpt_increasing": True, "price_up": True}, 5, ["15m", "1h"], ["volume", "price"], "量价齐升"),
            TrendModel("volume_price_trend_bear", "成交量", {"vpt_decreasing": True, "price_down": True}, 5, ["15m", "1h"], ["volume", "price"], "量价齐跌"),
            TrendModel("accumulation_distribution", "成交量", {"ad_line_increasing": True, "price_sideways": True}, 5, ["1h", "4h"], ["obv", "price"], "积累期"),
        ]
        
        # ===== 趋势模型 (15个) =====
        trend_models = [
            TrendModel("trend_ema_crossover_bull", "趋势", {"ema_9_above_ema_21": True, "ema_21_above_ema_50": True}, 6, ["15m", "1h"], ["ema9", "ema21", "ema50"], "EMA金叉上涨"),
            TrendModel("trend_ema_crossover_bear", "趋势", {"ema_9_below_ema_21": True, "ema_21_below_ema_50": True}, 6, ["15m", "1h"], ["ema9", "ema21", "ema50"], "EMA死叉下跌"),
            TrendModel("trend_ma_alignment_bull", "趋势", {"ma_aligned_up": True, "price_above_all_ma": True}, 7, ["1h", "4h"], ["sma20", "sma50", "sma200"], "均线多头排列"),
            TrendModel("trend_ma_alignment_bear", "趋势", {"ma_aligned_down": True, "price_below_all_ma": True}, 7, ["1h", "4h"], ["sma20", "sma50", "sma200"], "均线空头排列"),
            TrendModel("trend_channel_up", "趋势", {"higher_highs": True, "higher_lows": True}, 6, ["1h", "4h"], ["price"], "上升通道"),
            TrendModel("trend_channel_down", "趋势", {"lower_highs": True, "lower_lows": True}, 6, ["1h", "4h"], ["price"], "下降通道"),
            TrendModel("trend_line_break_bull", "趋势", {"trendline_break": True, "direction": "up"}, 6, ["1h", "4h"], ["price"], "趋势线突破上涨"),
            TrendModel("trend_line_break_bear", "趋势", {"trendline_break": True, "direction": "down"}, 6, ["1h", "4h"], ["price"], "趋势线突破下跌"),
            TrendModel("higher_highs_higher_lows", "趋势", {"hhhl": True}, 7, ["1h", "4h"], ["price"], "高点更高低点更高"),
            TrendModel("lower_highs_lower_lows", "趋势", {"lhll": True}, 7, ["1h", "4h"], ["price"], "高点更低低点更低"),
            TrendModel("trend_strength_strong", "趋势", {"adx_above_25": True, "rsi_50_70": True}, 6, ["1h", "4h"], ["adx", "rsi"], "趋势强劲"),
            TrendModel("trend_weakness", "趋势", {"adx_below_20": True, "price_range_narrow": True}, 4, ["1h", "4h"], ["adx"], "趋势疲软"),
            TrendModel("trend_exhaustion_bull", "趋势", {"price_extremes": True, "volume_declining": True, "adx_decreasing": True}, 6, ["4h", "1d"], ["price", "volume", "adx"], "上涨衰竭"),
            TrendModel("trend_exhaustion_bear", "趋势", {"price_extremes": True, "volume_declining": True, "adx_decreasing": True}, 6, ["4h", "1d"], ["price", "volume", "adx"], "下跌衰竭"),
            TrendModel("trend_reversal_early", "趋势", {"price_rejects_ma": True, "volume_increasing": True, "adx_turning": True}, 5, ["1h", "4h"], ["price", "volume", "adx"], "趋势早反转"),
        ]
        
        # ===== 宏观模型 (10个) =====
        macro_models = [
            TrendModel("btc_dominance_up", "宏观", {"btc_dominance_increasing": True}, 5, ["1h", "4h", "1d"], ["price"], "BTC主导上涨"),
            TrendModel("btc_dominance_down", "宏观", {"btc_dominance_decreasing": True}, 5, ["1h", "4h", "1d"], ["price"], "BTC主导下跌"),
            TrendModel("altcoin_season", "宏观", {"altcoin_btc_ratio_increasing": True}, 6, ["1d"], ["price"], "Altcoin季节"),
            TrendModel("btc_season", "宏观", {"btc_outperforms": True}, 6, ["1d"], ["price"], "BTC季节"),
            TrendModel("fear_greed_extreme_fear", "宏观", {"fear_greed_index_below_25": True}, 6, ["1h", "4h", "1d"], ["rsi"], "极度恐惧"),
            TrendModel("fear_greed_extreme_greed", "宏观", {"fear_greed_index_above_75": True}, 6, ["1h", "4h", "1d"], ["rsi"], "极度贪婪"),
            TrendModel("market_sentiment_shift", "宏观", {"sentiment_change_20pct": True}, 5, ["4h", "1d"], ["rsi"], "市场情绪转变"),
            TrendModel("sector_rotation_bull", "宏观", {"sector_leading": "tech", "sector_lagging": "utilities"}, 5, ["1d"], ["price"], "板块轮动上涨"),
            TrendModel("sector_rotation_bear", "宏观", {"sector_leading": "utilities", "sector_lagging": "tech"}, 5, ["1d"], ["price"], "板块轮动下跌"),
            TrendModel("correlation_break", "宏观", {"uncorrelated_assets": True, "correlation_below_0.3": True}, 4, ["1d"], ["price"], "相关性break"),
        ]
        
        # ===== 链上模型 (10个) =====
        onchain_models = [
            TrendModel("exchange_netflow_positive", "链上", {"exchange_inflow_decreasing": True, "exchange_outflow_increasing": True}, 6, ["1h", "4h"], ["volume"], "净流入"),
            TrendModel("exchange_netflow_negative", "链上", {"exchange_inflow_increasing": True, "exchange_outflow_decreasing": True}, 6, ["1h", "4h"], ["volume"], "净流出"),
            TrendModel("whale_accumulation", "链上", {"whale_buying": True, "large_tx_increasing": True}, 7, ["4h", "1d"], ["volume"], "巨鲸积累"),
            TrendModel("whale_distribution", "链上", {"whale_selling": True, "large_tx_increasing": True}, 7, ["4h", "1d"], ["volume"], "巨鲸分配"),
            TrendModel("miner_revenue_surge", "链上", {"miner_revenue_increasing": True}, 5, ["1d"], ["volume"], "矿工收入激增"),
            TrendModel("hash_rate_change", "链上", {"hash_rate_increasing": True}, 5, ["1d"], ["volume"], "算力变化"),
            TrendModel("difficulty_adjustment_up", "链上", {"difficulty_increasing": True}, 5, ["1d"], ["price"], "难度上调"),
            TrendModel("difficulty_adjustment_down", "链上", {"difficulty_decreasing": True}, 5, ["1d"], ["price"], "难度下调"),
            TrendModel("stablecoin_flows", "链上", {"stablecoin_inflow": True}, 5, ["1h", "4h"], ["volume"], "稳定币流向"),
            TrendModel("nft_market_heat", "链上", {"nft_volume_increasing": True}, 4, ["1d"], ["volume"], "NFT市场热度"),
        ]
        
        # 注册所有模型
        all_models = (momentum_models + breakout_models + reversal_models + 
                     volatility_models + volume_models + trend_models + 
                     macro_models + onchain_models)
        
        for model in all_models:
            self.models[model.name] = model
            
    def _build_indexes(self):
        """构建索引以加速查询"""
        for model in self.models.values():
            # 按类别索引
            self.models_by_category[model.category].append(model)
            # 按时 timeframe 索引
            for tf in model.timeframes:
                self.models_by_timeframe[tf].append(model)
            # 记录类别需要的指标
            if model.category not in self.category_indicators:
                self.category_indicators[model.category] = set()
            self.category_indicators[model.category].update(model.indicators)
    
    def get_model(self, name: str) -> Optional[TrendModel]:
        """获取指定模型"""
        return self.models.get(name)
        
    def get_models_by_category(self, category: str) -> List[TrendModel]:
        """按类别获取模型"""
        return self.models_by_category.get(category, [])
        
    def get_models_by_timeframe(self, timeframe: str) -> List[TrendModel]:
        """按时 timeframe 获取模型"""
        return self.models_by_timeframe.get(timeframe, [])
    
    def get_categories(self) -> List[str]:
        """获取所有类别"""
        return list(self.models_by_category.keys())
    
    def get_statistics(self) -> Dict:
        """获取模型统计"""
        categories = {}
        for cat, models in self.models_by_category.items():
            avg_conf = sum(m.confidence for m in models) / len(models) if models else 0
            categories[cat] = {
                "count": len(models),
                "avg_confidence": round(avg_conf, 2)
            }
        return {
            "total_models": len(self.models),
            "categories": categories
        }

# ==================== 分层扫描器 ====================

class HierarchicalScanner:
    """
    分层扫描器 - 实现三层扫描逻辑
    =================================
    
    Layer 1: 粗筛 (Coarse Scan)
    - 快速评估市场指标，确定可能的模型类别
    - 排除80%以上不匹配的模型
    - O(n) 复杂度 where n = 类别数
    
    Layer 2: 精筛 (Fine Scan)
    - 对候选类别中的模型进行详细比对
    - 计算每个条件的满足度
    - 输出匹配度和方向
    
    Layer 3: 决策 (Decision)
    - 多模型投票
    - 多时间框架确认
    - 触发对应策略
    """
    
    def __init__(self, library: TrendModelLibrary):
        self.library = library
        self.category_signals: Dict[str, float] = {}  # 各类别信号强度
        
    def scan(self, symbol: str, indicators: MarketIndicators, 
             timeframe: str = "15m") -> ScanResult:
        """
        执行三层扫描
        
        Args:
            symbol: 交易对
            indicators: 市场指标
            timeframe: 时间框架
            
        Returns:
            ScanResult: 包含最终信号和匹配详情
        """
        result = ScanResult(
            symbol=symbol,
            timestamp=datetime.now().isoformat(),
            layer1_candidates=[],
            layer2_matches=[]
        )
        
        # ===== Layer 1: 粗筛 =====
        layer1_start = datetime.now()
        candidates = self._layer1_coarse_scan(indicators)
        result.layer1_candidates = candidates
        layer1_time = (datetime.now() - layer1_start).total_seconds() * 1000
        
        if not candidates:
            return result
        
        # ===== Layer 2: 精筛 =====
        layer2_start = datetime.now()
        matches = self._layer2_fine_scan(candidates, indicators, timeframe)
        result.layer2_matches = matches
        layer2_time = (datetime.now() - layer2_start).total_seconds() * 1000
        
        if not matches:
            return result
        
        # ===== Layer 3: 决策 =====
        layer3_start = datetime.now()
        final_signal, final_confidence, direction, triggered_strategies = \
            self._layer3_decision(matches, indicators)
        result.final_signal = final_signal
        result.final_confidence = final_confidence
        result.direction = direction
        result.triggered_strategy = triggered_strategies
        result.models_voted = [m.model_name for m in matches[:5]]
        layer3_time = (datetime.now() - layer3_start).total_seconds() * 1000
        
        # 多时间框架确认
        result.multi_timeframe_confirmed = self._check_multi_timeframe(
            matches, symbol, indicators
        )
        
        # 更新模型统计
        for match in matches:
            match.model.match_count += 1
            match.model.last_matched = datetime.now().isoformat()
        
        return result
    
    def _layer1_coarse_scan(self, indicators: MarketIndicators) -> List[str]:
        """
        Layer 1: 粗筛 - 确定可能的模型类别
        
        快速评估市场状态，识别哪些模型类别可能匹配
        """
        candidates = []
        self.category_signals = {}
        
        # 评估各类别的信号强度
        categories = self.library.get_categories()
        
        for category in categories:
            signal_strength = self._evaluate_category_signal(category, indicators)
            self.category_signals[category] = signal_strength
            
            # 阈值: 信号强度 > 0.3 才纳入候选
            if signal_strength > 0.3:
                candidates.append(category)
        
        # 按信号强度排序
        candidates.sort(key=lambda c: self.category_signals[c], reverse=True)
        
        # 限制候选数量 (最多4个)
        return candidates[:4]
    
    def _evaluate_category_signal(self, category: str, 
                                  indicators: MarketIndicators) -> float:
        """评估某类别的信号强度"""
        signal = 0.0
        
        if category == "动量":
            # RSI 极端值信号
            if indicators.rsi < 30:
                signal += 0.4
            elif indicators.rsi > 70:
                signal += 0.4
            elif 40 <= indicators.rsi <= 60:
                signal += 0.2
            
            # MACD 信号
            if indicators.macd_histogram > 0:
                signal += 0.3
            else:
                signal += 0.1
                
        elif category == "突破":
            # 成交量信号
            if indicators.volume_ratio > 2.0:
                signal += 0.5
            elif indicators.volume_ratio > 1.5:
                signal += 0.3
            
            # 价格变化信号
            if abs(indicators.price_change_pct) > 3:
                signal += 0.4
            elif abs(indicators.price_change_pct) > 1:
                signal += 0.2
                
        elif category == "反转":
            # RSI 超卖/超买信号
            if indicators.rsi < 35:
                signal += 0.5
            elif indicators.rsi > 65:
                signal += 0.5
            elif indicators.rsi < 45:
                signal += 0.3
            elif indicators.rsi > 55:
                signal += 0.3
                
        elif category == "波动率":
            # 布林带宽度信号
            if indicators.bb_width > 0.03:
                signal += 0.4
            elif indicators.bb_width < 0.01:
                signal += 0.3
            
            # ATR 信号
            if indicators.atr_pct > 0.05:
                signal += 0.3
                
        elif category == "成交量":
            # 成交量比率信号
            if indicators.volume_ratio > 2.0:
                signal += 0.6
            elif indicators.volume_ratio > 1.5:
                signal += 0.4
            elif indicators.volume_ratio < 0.5:
                signal += 0.3
                
        elif category == "趋势":
            # ADX 信号
            if indicators.adx > 25:
                signal += 0.5
            elif indicators.adx > 20:
                signal += 0.3
            
            # 均线位置信号
            if indicators.price_change_pct > 2:
                signal += 0.3
            elif indicators.price_change_pct < -2:
                signal += 0.3
                
        elif category == "宏观":
            # 宏观信号 - 使用RSI作为代理
            if indicators.rsi < 40:
                signal += 0.3
            elif indicators.rsi > 60:
                signal += 0.3
                
        elif category == "链上":
            # 成交量信号作为代理
            if indicators.volume_ratio > 1.5:
                signal += 0.4
        
        return min(1.0, signal)
    
    def _layer2_fine_scan(self, categories: List[str], 
                          indicators: MarketIndicators,
                          timeframe: str) -> List[MatchResult]:
        """
        Layer 2: 精筛 - 在候选类别中进行详细比对
        """
        matches = []
        
        for category in categories:
            models = self.library.get_models_by_category(category)
            
            for model in models:
                # 检查时间框架是否匹配
                if timeframe not in model.timeframes:
                    continue
                
                # 评估模型条件
                result = self._evaluate_model(model, indicators)
                
                if result.match_score > 0.3:  # 阈值: 匹配度 > 0.3
                    matches.append(result)
        
        # 按匹配度排序
        matches.sort(key=lambda x: x.match_score, reverse=True)
        
        # 返回前10个匹配
        return matches[:10]
    
    def _evaluate_model(self, model: TrendModel, 
                        indicators: MarketIndicators) -> MatchResult:
        """评估单个模型的匹配度"""
        conditions_met = []
        conditions_failed = []
        total_conditions = len(model.conditions)
        matched_conditions = 0
        
        for condition, expected in model.conditions.items():
            if self._check_condition(condition, expected, indicators):
                conditions_met.append(condition)
                matched_conditions += 1
            else:
                conditions_failed.append(condition)
        
        # 计算匹配度
        match_score = matched_conditions / total_conditions if total_conditions > 0 else 0
        
        # 调整匹配度 (考虑置信度)
        adjusted_score = match_score * (model.confidence / 10.0)
        
        # 确定方向
        direction = self._determine_direction(model.name, indicators)
        
        # 各时间框架得分 (简化处理)
        timeframe_scores = {tf: adjusted_score for tf in model.timeframes}
        
        return MatchResult(
            model_name=model.name,
            model=model,
            match_score=adjusted_score,
            conditions_met=conditions_met,
            conditions_failed=conditions_failed,
            direction=direction,
            timeframe_scores=timeframe_scores
        )
    
    def _check_condition(self, condition: str, expected: Any, 
                        indicators: MarketIndicators) -> bool:
        """检查单个条件是否满足"""
        try:
            # 解析条件并检查
            if condition == "rsi_above_50":
                return indicators.rsi > 50
            elif condition == "rsi_below_50":
                return indicators.rsi < 50
            elif condition == "rsi_oversold" or condition == "rsi_below_30":
                return indicators.rsi < 30
            elif condition == "rsi_overbought" or condition == "rsi_above_70":
                return indicators.rsi > 70
            elif condition == "rsi_range":
                low, high = expected if isinstance(expected, list) else [30, 70]
                return low <= indicators.rsi <= high
            elif condition == "rsi_above_60":
                return indicators.rsi > 60
            elif condition == "rsi_below_40":
                return indicators.rsi < 40
            elif condition == "macd_bullish":
                return indicators.macd > 0 or indicators.macd_histogram > 0
            elif condition == "macd_bearish":
                return indicators.macd < 0 or indicators.macd_histogram < 0
            elif condition == "macd_histogram_increasing":
                return indicators.macd_histogram > 0
            elif condition == "macd_histogram_decreasing":
                return indicators.macd_histogram < 0
            elif condition == "price_above_sma20":
                return indicators.close > indicators.sma20
            elif condition == "price_below_sma20":
                return indicators.close < indicators.sma20
            elif condition == "volume_surge" or condition == "volume_surge_2x":
                return indicators.volume_ratio >= 2.0
            elif condition == "volume_surge_3x":
                return indicators.volume_ratio >= 3.0
            elif condition == "volume_increasing":
                return indicators.volume_ratio > 1.2
            elif condition == "volume_declining":
                return indicators.volume_ratio < 0.8
            elif condition == "volume_normal":
                return 0.8 <= indicators.volume_ratio <= 1.2
            elif condition == "volume_below_average":
                return indicators.volume_ratio < 0.7
            elif condition == "adx_above_25":
                return indicators.adx > 25
            elif condition == "adx_below_20":
                return indicators.adx < 20
            elif condition == "adx_decreasing":
                return indicators.adx < 20  # 简化
            elif condition == "price_up":
                return indicators.price_change_pct > 0
            elif condition == "price_down":
                return indicators.price_change_pct < 0
            elif condition == "bb_squeeze":
                return indicators.bb_width < 0.02
            elif condition == "bb_expansion":
                return indicators.bb_width > 0.03
            elif condition == "atr_high":
                return indicators.atr_pct > 0.04
            elif condition == "atr_low":
                return indicators.atr_pct < 0.02
            elif condition == "atr_surge":
                return indicators.atr_pct > 0.05
            elif condition == "rsi_extreme":
                return indicators.rsi < 25 or indicators.rsi > 75
            elif condition == "price_range_narrow":
                return indicators.bb_width < 0.015
            elif condition == "price_range":
                return indicators.bb_width < 0.02
            elif condition == "price_range_bound":
                return indicators.bb_width < 0.025
            elif condition == "price_bounces":
                return indicators.price_change_pct > 0
            elif condition == "price_rejects":
                return indicators.price_change_pct < 0
            elif condition == "price_breaks_high":
                return indicators.close > indicators.high * 0.998  # 接近最高点
            elif condition == "price_breaks_low":
                return indicators.close < indicators.low * 1.002  # 接近最低点
            elif condition == "price_breaks_resistance":
                return indicators.close > indicators.bb_upper * 0.99
            elif condition == "price_breaks_support":
                return indicators.close < indicators.bb_lower * 1.01
            elif condition == "rsi_turning_up":
                return indicators.rsi > 30 and indicators.rsi < 50
            elif condition == "rsi_turning_down":
                return indicators.rsi < 70 and indicators.rsi > 50
            elif condition == "volatility_increases":
                return indicators.bb_width > 0.025
            elif condition == "price_extremes":
                return indicators.rsi < 30 or indicators.rsi > 70
            elif condition == "price_bounces_vwap":
                return abs(indicators.close - indicators.vwap) / indicators.vwap < 0.005
            elif condition == "price_rejects_vwap":
                return abs(indicators.close - indicators.vwap) / indicators.vwap > 0.01
            elif condition == "volume_stable":
                return 0.7 <= indicators.volume_ratio <= 1.3
            elif condition == "low_volatility":
                return indicators.bb_width < 0.015
            elif condition == "high_volatility":
                return indicators.bb_width > 0.03
            elif condition == "high_volatility_distribution":
                return indicators.bb_width > 0.03 and indicators.volume_ratio > 1.3
            elif condition == "price_range_wide":
                return indicators.bb_width > 0.035
            elif condition == "ema_9_above_ema_21":
                return indicators.ema9 > indicators.ema21
            elif condition == "ema_9_below_ema_21":
                return indicators.ema9 < indicators.ema21
            elif condition == "ema_21_above_ema_50":
                return indicators.ema21 > indicators.ema50
            elif condition == "ema_21_below_ema_50":
                return indicators.ema21 < indicators.ema50
            elif condition == "ma_aligned_up":
                return indicators.sma20 > indicators.sma50 and indicators.sma50 > indicators.sma200
            elif condition == "ma_aligned_down":
                return indicators.sma20 < indicators.sma50 and indicators.sma50 < indicators.sma200
            elif condition == "price_above_all_ma":
                return indicators.close > indicators.sma20 and indicators.close > indicators.sma50
            elif condition == "price_below_all_ma":
                return indicators.close < indicators.sma20 and indicators.close < indicators.sma50
            elif condition == "price_change_5pct":
                return abs(indicators.price_change_pct) > 5
            elif condition == "closes_below_resistance":
                return indicators.close < indicators.bb_upper
            elif condition == "closes_above_support":
                return indicators.close > indicators.bb_lower
            elif condition == "obv_increasing":
                return indicators.obv > indicators.obv_ma
            elif condition == "obv_decreasing":
                return indicators.obv < indicators.obv_ma
            elif condition == "price_sideways":
                return abs(indicators.price_change_pct) < 1
            elif condition == "price_lower_low":
                return indicators.price_change_pct < -1
            elif condition == "price_higher_high":
                return indicators.price_change_pct > 1
            elif condition == "rsi_higher_low":
                return 40 <= indicators.rsi <= 50
            elif condition == "rsi_lower_high":
                return 50 <= indicators.rsi <= 60
            elif condition == "price_lower_high":
                return indicators.price_change_pct < 0 and indicators.price_change_pct > -2
            elif condition == "price_higher_low":
                return indicators.price_change_pct > 0 and indicators.price_change_pct < 2
            elif condition == "rsi_50_70":
                return 50 <= indicators.rsi <= 70
            elif condition == "price_hits_support":
                return indicators.close < indicators.bb_lower * 1.02
            elif condition == "bounces_from_support":
                return indicators.close > indicators.low * 1.005
            else:
                # 默认返回False
                return False
        except Exception as e:
            return False
    
    def _determine_direction(self, model_name: str, 
                           indicators: MarketIndicators) -> TrendDirection:
        """确定趋势方向"""
        name_lower = model_name.lower()
        
        if "bull" in name_lower or "up" in name_lower or "long" in name_lower:
            return TrendDirection.BULL
        elif "bear" in name_lower or "down" in name_lower or "short" in name_lower:
            return TrendDirection.BEAR
        elif "reversal" in name_lower or "bounce" in name_lower:
            # 根据当前价格位置判断
            if indicators.rsi < 40:
                return TrendDirection.BULL
            elif indicators.rsi > 60:
                return TrendDirection.BEAR
            else:
                return TrendDirection.SIDEWAYS
        else:
            return TrendDirection.SIDEWAYS
    
    def _layer3_decision(self, matches: List[MatchResult],
                        indicators: MarketIndicators) -> Tuple[SignalType, float, TrendDirection, str]:
        """
        Layer 3: 决策 - 多模型投票确定最终信号
        """
        if not matches:
            return SignalType.NEUTRAL, 0.0, TrendDirection.SIDEWAYS, ""
        
        # 多模型投票
        bull_votes = 0
        bear_votes = 0
        neutral_votes = 0
        total_confidence = 0.0
        
        for match in matches:
            weight = match.match_score
            if match.direction == TrendDirection.BULL:
                bull_votes += weight
            elif match.direction == TrendDirection.BEAR:
                bear_votes += weight
            else:
                neutral_votes += weight
            total_confidence += match.model.confidence * weight
        
        # 加权平均置信度
        avg_confidence = total_confidence / sum(m.match_score for m in matches) if matches else 0
        
        # 确定方向
        if bull_votes > bear_votes * 1.5:
            direction = TrendDirection.BULL
            if avg_confidence >= 7:
                signal = SignalType.STRONG_BUY
            elif avg_confidence >= 5:
                signal = SignalType.BUY
            else:
                signal = SignalType.NEUTRAL
        elif bear_votes > bull_votes * 1.5:
            direction = TrendDirection.BEAR
            if avg_confidence >= 7:
                signal = SignalType.STRONG_SELL
            elif avg_confidence >= 5:
                signal = SignalType.SELL
            else:
                signal = SignalType.NEUTRAL
        else:
            direction = TrendDirection.SIDEWAYS
            signal = SignalType.NEUTRAL
        
        # 确定触发的策略
        triggered_strategy = self._determine_strategy(matches[:3], direction)
        
        return signal, min(10.0, avg_confidence), direction, triggered_strategy
    
    def _determine_strategy(self, top_matches: List[MatchResult],
                           direction: TrendDirection) -> str:
        """根据匹配结果确定触发的策略"""
        if not top_matches:
            return ""
        
        # 根据模型类别确定策略
        categories = [m.model.category for m in top_matches]
        
        # 策略映射
        if "突破" in categories:
            return "🐹 打地鼠" if direction == TrendDirection.BULL else "🐹 打地鼠"
        elif "动量" in categories:
            return "🐰 打兔子"
        elif "反转" in categories:
            return "🔮 走着瞧"
        elif "宏观" in categories or "链上" in categories:
            return "👑 跟大哥"
        elif "成交量" in categories:
            return "🍀 搭便车"
        elif "趋势" in categories:
            return "🐰 打兔子"
        elif "波动率" in categories:
            return "🐹 打地鼠"
        else:
            return "🐰 打兔子"
    
    def _check_multi_timeframe(self, matches: List[MatchResult],
                               symbol: str,
                               indicators: MarketIndicators) -> bool:
        """检查多时间框架是否确认"""
        # 简化的多时间框架确认逻辑
        # 实际应该检查多个时间框架的数据
        
        if len(matches) < 3:
            return False
        
        # 检查前3个匹配是否来自不同时间框架
        timeframes = set()
        for match in matches[:3]:
            timeframes.update(match.model.timeframes)
        
        # 如果覆盖了多个时间框架，认为是确认的
        return len(timeframes) >= 2

# ==================== 声纳库主类 ====================

class SonarLibraryV2:
    """
    声纳库 V2 - 分层扫描版本
    ========================
    
    使用示例:
    
    # 初始化
    sonar = SonarLibraryV2()
    
    # 获取市场指标
    indicators = sonar.fetch_indicators("BTC/USDT", "15m")
    
    # 执行扫描
    result = sonar.scan("BTC/USDT", indicators, "15m")
    
    # 输出结果
    print(f"信号: {result.final_signal}")
    print(f"置信度: {result.final_confidence}")
    print(f"方向: {result.direction}")
    print(f"触发策略: {result.triggered_strategy}")
    print(f"Layer1候选: {result.layer1_candidates}")
    print(f"Layer2匹配: {[m.model_name for m in result.layer2_matches]}")
    """
    
    def __init__(self, db_path: str = None):
        self.library = TrendModelLibrary(db_path)
        self.scanner = HierarchicalScanner(self.library)
        self.scan_history: List[ScanResult] = []
        
    def scan(self, symbol: str, indicators: MarketIndicators = None,
             timeframe: str = "15m") -> ScanResult:
        """执行完整扫描"""
        if indicators is None:
            indicators = self._default_indicators()
        
        result = self.scanner.scan(symbol, indicators, timeframe)
        self.scan_history.append(result)
        
        return result
    
    def _default_indicators(self) -> MarketIndicators:
        """返回默认指标"""
        return MarketIndicators(
            rsi=50.0,
            rsi_14=50.0,
            rsi_7=50.0,
            macd=0.0,
            macd_signal=0.0,
            macd_histogram=0.0,
            volume_ratio=1.0,
            bb_width=0.02,
            atr_pct=0.02,
            adx=20.0,
            price_change_pct=0.0,
            sma20=0.0,
            sma50=0.0,
            sma200=0.0,
            ema9=0.0,
            ema21=0.0,
            ema50=0.0,
            close=0.0
        )
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        return {
            "library": self.library.get_statistics(),
            "total_scans": len(self.scan_history),
            "signal_distribution": self._get_signal_distribution()
        }
    
    def _get_signal_distribution(self) -> Dict:
        """获取信号分布"""
        distribution = {
            "STRONG_BUY": 0,
            "BUY": 0,
            "NEUTRAL": 0,
            "SELL": 0,
            "STRONG_SELL": 0
        }
        
        for result in self.scan_history:
            if result.final_signal:
                distribution[result.final_signal.value] += 1
        
        return distribution
    
    def analyze_batch(self, symbols: List[str], 
                     timeframe: str = "15m") -> List[ScanResult]:
        """批量分析多个交易对"""
        results = []
        for symbol in symbols:
            try:
                result = self.scan(symbol, timeframe=timeframe)
                results.append(result)
            except Exception as e:
                print(f"Error scanning {symbol}: {e}")
        return results


# ==================== 便捷函数 ====================

def create_sonar_library(db_path: str = None) -> SonarLibraryV2:
    """创建声纳库实例"""
    return SonarLibraryV2(db_path)


# ==================== 主函数 ====================

def main():
    """主函数 - 用于测试"""
    print("=" * 60)
    print("🚀 声纳库 V2 - 100+趋势模型 + 分层扫描")
    print("=" * 60)
    
    # 创建声纳库
    sonar = SonarLibraryV2()
    
    # 打印统计
    stats = sonar.library.get_statistics()
    print(f"\n📊 模型统计:")
    print(f"   总模型数: {stats['total_models']}")
    for cat, info in stats['categories'].items():
        print(f"   {cat}: {info['count']}个模型, 平均置信度: {info['avg_confidence']}")
    
    # 创建模拟市场指标
    indicators = MarketIndicators(
        close=67500,
        open=67000,
        high=67800,
        low=66800,
        price_change_pct=0.75,
        rsi=58,
        rsi_14=58,
        macd=120,
        macd_signal=100,
        macd_histogram=20,
        sma20=67000,
        sma50=66500,
        sma200=64000,
        ema9=67200,
        ema21=66800,
        ema50=66500,
        bb_upper=68000,
        bb_middle=67200,
        bb_lower=66400,
        bb_width=0.024,
        atr=350,
        atr_pct=0.0052,
        adx=28,
        plus_di=30,
        minus_di=20,
        volume=15000,
        volume_ma=12000,
        volume_ratio=1.25,
        obv=5000000,
        obv_ma=4800000,
        vwap=67100,
        williams_r=-35,
        cci=45,
        stochastic_k=62,
        stochastic_d=58
    )
    
    # 执行扫描
    print("\n" + "=" * 60)
    print("📊 扫描 BTC/USDT")
    print("=" * 60)
    
    result = sonar.scan("BTC/USDT", indicators, "15m")
    
    print(f"\n📊 Layer 1 粗筛结果:")
    print(f"   候选类别: {result.layer1_candidates}")
    print(f"   类别信号: {sonar.scanner.category_signals}")
    
    print(f"\n📊 Layer 2 精筛结果 (Top 5):")
    for i, match in enumerate(result.layer2_matches[:5]):
        print(f"   {i+1}. {match.model_name}")
        print(f"      匹配度: {match.match_score:.2f}")
        print(f"      方向: {match.direction.value}")
        print(f"      满足条件: {match.conditions_met}")
        print(f"      未满足: {match.conditions_failed}")
    
    print(f"\n📊 Layer 3 决策结果:")
    print(f"   最终信号: {result.final_signal.value if result.final_signal else 'N/A'}")
    print(f"   置信度: {result.final_confidence:.1f}")
    print(f"   方向: {result.direction.value}")
    print(f"   触发策略: {result.triggered_strategy}")
    print(f"   多时间框架确认: {result.multi_timeframe_confirmed}")
    print(f"   投票模型: {result.models_voted}")
    
    print("\n" + "=" * 60)
    print("✅ 扫描完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
