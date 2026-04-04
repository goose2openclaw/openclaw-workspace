"""
声纳库 V3 - 123趋势模型 + 7工具策略 + 置信度聚合
=================================================

北斗七鑫投资体系 - 策略工程核心模块

架构:
┌─────────────────────────────────────────────────────────────┐
│                    声纳库 (Sonar Library)                    │
├─────────────────────────────────────────────────────────────┤
│  123趋势模型 (分类整理)                                      │
│  ├── 趋势类 (EMA/MA/通道): ~30个                           │
│  ├── 动量类 (RSI/MACD/ADX): ~25个                          │
│  ├── 波动类 (Bollinger/ATR): ~20个                         │
│  ├── 成交量类 (OBV/VWAP): ~15个                            │
│  ├── 反转类 (CCI/Williams): ~15个                          │
│  ├── 通道类 (Channel/Breakout): ~10个                     │
│  └── 其他专用类: ~8个                                       │
├─────────────────────────────────────────────────────────────┤
│  信号聚合层                                                  │
│  ├── 置信度计算 (Confidence Scoring)                       │
│  ├── 多模型共识 (Multi-Model Consensus)                    │
│  └── 信号优先级 (Signal Priority)                          │
├─────────────────────────────────────────────────────────────┤
│  7大工具策略                                                │
│  ├── 🐰 打兔子 (前20主流) - 稳定收益                        │
│  ├── 🐹 打地鼠 (其他币) - 火控雷达                         │
│  ├── 🔮 走着瞧 (预测市场) - MiroFish仿真                   │
│  ├── 👑 跟大哥 (做市) - 综合判断                           │
│  ├── 🍀 搭便车 (跟单) - 二级分包                           │
│  ├── 💰 薅羊毛 (空投) - 只读安全                           │
│  └── 👶 穷孩子 (众包) - EvoMap隔离                         │
└─────────────────────────────────────────────────────────────┘
"""

import json
import math
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime
from collections import defaultdict, Counter

# ==================== 枚举定义 ====================

class SignalType(Enum):
    """信号类型"""
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    NEUTRAL = "NEUTRAL"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"
    
    def to_score(self) -> int:
        mapping = {
            SignalType.STRONG_BUY: 5,
            SignalType.BUY: 3,
            SignalType.NEUTRAL: 0,
            SignalType.SELL: -3,
            SignalType.STRONG_SELL: -5
        }
        return mapping.get(self, 0)

class TrendDirection(Enum):
    """趋势方向"""
    BULL = "BULL"
    BEAR = "BEAR"
    SIDEWAYS = "SIDEWAYS"
    
    def to_score(self) -> float:
        return {"BULL": 1.0, "BEAR": -1.0, "SIDEWAYS": 0.0}.get(self.value, 0.0)

class MarketRegime(Enum):
    """市场状态"""
    TRENDING_UP = "TRENDING_UP"
    TRENDING_DOWN = "TRENDING_DOWN"
    RANGE_BOUND = "RANGE_BOUND"
    VOLATILE = "VOLATILE"
    QUIET = "QUIET"
    BREAKOUT_IMMINENT = "BREAKOUT_IMMINENT"

class ModelCategory(Enum):
    """模型类别 - 123模型分类"""
    # 趋势类 (~30个)
    TREND_EMA = "TREND_EMA"
    TREND_MA = "TREND_MA"
    TREND_CHANNEL = "TREND_CHANNEL"
    TREND_ICHIMOKU = "TREND_ICHIMOKU"
    
    # 动量类 (~25个)
    MOMENTUM_RSI = "MOMENTUM_RSI"
    MOMENTUM_MACD = "MOMENTUM_MACD"
    MOMENTUM_ADX = "MOMENTUM_ADX"
    MOMENTUM_STOCHASTIC = "MOMENTUM_STOCHASTIC"
    
    # 波动类 (~20个)
    VOLATILITY_BOLLINGER = "VOLATILITY_BOLLINGER"
    VOLATILITY_ATR = "VOLATILITY_ATR"
    VOLATILITY_KELTNER = "VOLATILITY_KELTNER"
    
    # 成交量类 (~15个)
    VOLUME_OBV = "VOLUME_OBV"
    VOLUME_VWAP = "VOLUME_VWAP"
    VOLUME_VRM = "VOLUME_VRM"
    
    # 反转类 (~15个)
    REVERSAL_CCI = "REVERSAL_CCI"
    REVERSAL_WILLIAMS = "REVERSAL_WILLIAMS"
    REVERSAL_RVI = "REVERSAL_RVI"
    
    # 通道类 (~10个)
    CHANNEL_DONCHIAN = "CHANNEL_DONCHIAN"
    CHANNEL_PITCHFORK = "CHANNEL_PITCHFORK"
    CHANNEL_FIBONACCI = "CHANNEL_FIBONACCI"
    
    # 其他专用类 (~8个)
    SPECIAL_MELT = "SPECIAL_MELT"
    SPECIAL_RSI_DIV = "SPECIAL_RSI_DIV"
    SPECIAL_MA_CROSS = "SPECIAL_MA_CROSS"

class ToolType(Enum):
    """工具类型 - 7大工具"""
    RABBIT = "RABBIT"           # 🐰 打兔子 - 前20主流
    GOPHER = "GOPHER"           # 🐹 打地鼠 - 其他币
    LOOKER = "LOOKER"           # 🔮 走着瞧 - 预测市场
    FOLLOWER = "FOLLOWER"       # 👑 跟大哥 - 做市
    HITCHHIKE = "HITCHHIKE"     # 🍀 搭便车 - 跟单
    AIREDROP = "AIREDROP"       # 💰 薅羊毛 - 空投
    CROWDSOURCE = "CROWDSOURCE" # 👶 穷孩子 - 众包

# ==================== 数据结构 ====================

@dataclass
class TrendModel:
    """趋势模型 - 123模型基类"""
    id: str
    name: str
    name_cn: str
    category: ModelCategory
    description: str
    indicators: List[str]
    timeframes: List[str]  # 1m, 5m, 15m, 1h, 4h, 1d, 1w
    base_confidence: float  # 1-10 基础置信度
    success_rate: float     # 历史胜率
    conditions: Dict[str, Any]  # 信号生成条件
    tool_affinity: List[ToolType]  # 适用的工具
    
    # 统计
    match_count: int = 0
    success_count: int = 0
    last_matched: str = ""
    
    @property
    def current_confidence(self) -> float:
        """动态置信度 = 基础置信度 * 历史胜率调整"""
        if self.match_count == 0:
            return self.base_confidence
        # 贝叶斯更新: (成功次数 + alpha) / (总次数 + 2*alpha)
        alpha = 2
        observed_rate = (self.success_count + alpha) / (self.match_count + 2 * alpha)
        return self.base_confidence * observed_rate

@dataclass
class SignalCondition:
    """信号条件"""
    indicator: str
    operator: str  # >, <, >=, <=, ==, cross_above, cross_below
    value: Any
    weight: float = 1.0  # 条件权重

@dataclass
class GeneratedSignal:
    """生成的信号"""
    id: str
    timestamp: str
    symbol: str
    model_id: str
    model_name: str
    signal_type: SignalType
    direction: TrendDirection
    confidence: float
    price: float
    timeframe: str
    conditions_met: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "symbol": self.symbol,
            "model_id": self.model_id,
            "model_name": self.model_name,
            "signal_type": self.signal_type.value,
            "direction": self.direction.value,
            "confidence": round(self.confidence, 2),
            "price": self.price,
            "timeframe": self.timeframe,
            "conditions_met": self.conditions_met,
            "metadata": self.metadata
        }

@dataclass
class AggregatedSignal:
    """聚合信号 - 多模型共识"""
    symbol: str
    timestamp: str
    signals: List[GeneratedSignal]
    aggregated_direction: TrendDirection
    aggregated_confidence: float
    consensus_score: float  # 共识度 0-1
    primary_tool: ToolType
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "symbol": self.symbol,
            "timestamp": self.timestamp,
            "signal_count": len(self.signals),
            "aggregated_direction": self.aggregated_direction.value,
            "aggregated_confidence": round(self.aggregated_confidence, 2),
            "consensus_score": round(self.consensus_score, 2),
            "primary_tool": self.primary_tool.value,
            "metadata": self.metadata
        }

# ==================== 123趋势模型定义 ====================

class SonarLibrary:
    """声纳库 - 123趋势模型"""
    
    # 模型注册表
    MODELS: Dict[str, TrendModel] = {}
    
    # 类别分组
    CATEGORY_GROUPS: Dict[ModelCategory, List[str]] = defaultdict(list)
    
    @classmethod
    def register(cls, model: TrendModel):
        """注册模型"""
        cls.MODELS[model.id] = model
        cls.CATEGORY_GROUPS[model.category].append(model.id)
    
    @classmethod
    def get_by_category(cls, category: ModelCategory) -> List[TrendModel]:
        """按类别获取模型"""
        return [cls.MODELS[mid] for mid in cls.CATEGORY_GROUPS.get(category, [])]
    
    @classmethod
    def get_by_tool(cls, tool: ToolType) -> List[TrendModel]:
        """按工具获取适用模型"""
        return [m for m in cls.MODELS.values() if tool in m.tool_affinity]
    
    @classmethod
    def get_all_models(cls) -> List[TrendModel]:
        """获取所有模型"""
        return list(cls.MODELS.values())
    
    @classmethod
    def model_count(cls) -> Dict[str, int]:
        """各类型模型数量"""
        return {
            "total": len(cls.MODELS),
            "by_category": {cat.value: len(models) for cat, models in cls.CATEGORY_GROUPS.items()}
        }

# ==================== 模型定义宏 ====================

def define_trend_models():
    """定义所有123个趋势模型"""
    
    # ===== 趋势类 (~30个) =====
    # EMA系列 (10个)
    for period in [9, 12, 20, 21, 26, 50, 100, 150, 200, 250]:
        model = TrendModel(
            id=f"TREND_EMA_{period}",
            name=f"EMA {period}",
            name_cn=f"指数移动平均线{period}",
            category=ModelCategory.TREND_EMA,
            description=f"EMA {period} 趋势判断",
            indicators=[f"EMA_{period}"],
            timeframes=["1h", "4h", "1d"],
            base_confidence=7.0,
            success_rate=0.55,
            conditions={
                "price_above": f"EMA_{period}",
                "description": f"价格位于EMA{period}上方看涨"
            },
            tool_affinity=[ToolType.RABBIT, ToolType.GOPHER, ToolType.LOOKER]
        )
        SonarLibrary.register(model)
    
    # MA系列 (10个)
    for period in [7, 10, 20, 30, 50, 100, 120, 150, 200, 250]:
        model = TrendModel(
            id=f"TREND_MA_{period}",
            name=f"MA {period}",
            name_cn=f"简单移动平均线{period}",
            category=ModelCategory.TREND_MA,
            description=f"MA {period} 趋势判断",
            indicators=[f"MA_{period}"],
            timeframes=["1h", "4h", "1d"],
            base_confidence=6.5,
            success_rate=0.53,
            conditions={
                "price_above": f"MA_{period}",
                "description": f"价格位于MA{period}上方看涨"
            },
            tool_affinity=[ToolType.RABBIT, ToolType.GOPHER]
        )
        SonarLibrary.register(model)
    
    # 通道类 (6个)
    for ch_type in ["ENVELOPE", "PRICE_CHANNEL", "RAFF_CHANNEL"]:
        for period in [20, 50]:
            model = TrendModel(
                id=f"TREND_CHANNEL_{ch_type}_{period}",
                name=f"{ch_type} {period}",
                name_cn=f"{ch_type}通道{period}",
                category=ModelCategory.TREND_CHANNEL,
                description=f"{ch_type} 通道趋势",
                indicators=[f"{ch_type}_{period}_UPPER", f"{ch_type}_{period}_LOWER"],
                timeframes=["4h", "1d"],
                base_confidence=6.0,
                success_rate=0.52,
                conditions={
                    "in_channel": True,
                    "description": f"价格在{ch_type}通道内"
                },
                tool_affinity=[ToolType.RABBIT, ToolType.FOLLOWER]
            )
            SonarLibrary.register(model)
    
    # 一目均衡表 (4个)
    for component in ["TENKAN", "KIJUN", "SENKOU_A", "SENKOU_B"]:
        model = TrendModel(
            id=f"TREND_ICHIMOKU_{component}",
            name=f"Ichimoku {component}",
            name_cn=f"一目均衡表{component}",
            category=ModelCategory.TREND_ICHIMOKU,
            description=f"Ichimoku {component} 趋势信号",
            indicators=["TENKAN", "KIJUN", "SENKOU_A", "SENKOU_B", "CHIKOU"],
            timeframes=["4h", "1d"],
            base_confidence=7.5,
            success_rate=0.58,
            conditions={
                "cloud_break": True,
                "description": "云层突破信号"
            },
            tool_affinity=[ToolType.LOOKER, ToolType.FOLLOWER]
        )
        SonarLibrary.register(model)
    
    # ===== 动量类 (~25个) =====
    # RSI系列 (8个)
    for period in [6, 7, 8, 9, 10, 12, 14, 21]:
        model = TrendModel(
            id=f"MOMENTUM_RSI_{period}",
            name=f"RSI {period}",
            name_cn=f"相对强弱指数{period}",
            category=ModelCategory.MOMENTUM_RSI,
            description=f"RSI {period} 动量判断",
            indicators=[f"RSI_{period}"],
            timeframes=["1h", "4h", "1d"],
            base_confidence=7.0,
            success_rate=0.56,
            conditions={
                "oversold": 30,
                "overbought": 70,
                "description": f"RSI{period} 超买超卖"
            },
            tool_affinity=[ToolType.RABBIT, ToolType.GOPHER, ToolType.LOOKER]
        )
        SonarLibrary.register(model)
    
    # MACD系列 (6个)
    for fast, slow, signal in [(12, 26, 9), (8, 17, 9), (5, 35, 5), (19, 39, 9), (12, 50, 18), (3, 10, 16)]:
        model = TrendModel(
            id=f"MOMENTUM_MACD_{fast}_{slow}_{signal}",
            name=f"MACD ({fast},{slow},{signal})",
            name_cn=f"MACD({fast},{slow},{signal})",
            category=ModelCategory.MOMENTUM_MACD,
            description=f"MACD 动量判断",
            indicators=["MACD", "MACD_SIGNAL", "MACD_HIST"],
            timeframes=["1h", "4h", "1d"],
            base_confidence=7.5,
            success_rate=0.58,
            conditions={
                "macd_cross": True,
                "histogram_sign": "positive" if fast < slow else "negative",
                "description": "MACD 金叉/死叉"
            },
            tool_affinity=[ToolType.RABBIT, ToolType.GOPHER]
        )
        SonarLibrary.register(model)
    
    # ADX系列 (6个)
    for period in [7, 10, 14, 20, 25, 30]:
        model = TrendModel(
            id=f"MOMENTUM_ADX_{period}",
            name=f"ADX {period}",
            name_cn=f"平均趋向指数{period}",
            category=ModelCategory.MOMENTUM_ADX,
            description=f"ADX {period} 趋势强度",
            indicators=[f"ADX_{period}", f"PLUS_DI_{period}", f"MINUS_DI_{period}"],
            timeframes=["4h", "1d"],
            base_confidence=6.5,
            success_rate=0.54,
            conditions={
                "strong_trend": 25,
                "very_strong": 50,
                "description": f"ADX{period} 趋势强度"
            },
            tool_affinity=[ToolType.RABBIT, ToolType.LOOKER]
        )
        SonarLibrary.register(model)
    
    # 随机指标 (5个)
    for period in [5, 8, 10, 14, 21]:
        model = TrendModel(
            id=f"MOMENTUM_STOCH_{period}",
            name=f"Stochastic {period}",
            name_cn=f"随机指标{period}",
            category=ModelCategory.MOMENTUM_STOCHASTIC,
            description=f"Stochastic {period} 动量",
            indicators=[f"STOCH_K_{period}", f"STOCH_D_{period}"],
            timeframes=["1h", "4h"],
            base_confidence=6.0,
            success_rate=0.52,
            conditions={
                "oversold": 20,
                "overbought": 80,
                "description": f"Stochastic{period} 超买超卖"
            },
            tool_affinity=[ToolType.GOPHER, ToolType.LOOKER]
        )
        SonarLibrary.register(model)
    
    # ===== 波动类 (~20个) =====
    # Bollinger Bands (6个)
    for period in [10, 14, 20, 21, 30, 50]:
        for std in [1.5, 2.0, 2.5]:
            model = TrendModel(
                id=f"VOL_BOLLINGER_{period}_{std}".replace(".", "_"),
                name=f"BB {period} std{std}",
                name_cn=f"布林带{period}标准差{std}",
                category=ModelCategory.VOLATILITY_BOLLINGER,
                description=f"Bollinger Bands 波动判断",
                indicators=[f"BB_UPPER_{period}", f"BB_MIDDLE_{period}", f"BB_LOWER_{period}"],
                timeframes=["1h", "4h", "1d"],
                base_confidence=6.5,
                success_rate=0.53,
                conditions={
                    "bandwidth": std,
                    "description": "布林带收口/开口"
                },
                tool_affinity=[ToolType.RABBIT, ToolType.GOPHER]
            )
            SonarLibrary.register(model)
    
    # ATR系列 (8个)
    for period in [5, 7, 10, 14, 20, 21, 30, 50]:
        model = TrendModel(
            id=f"VOL_ATR_{period}",
            name=f"ATR {period}",
            name_cn=f"平均真实波幅{period}",
            category=ModelCategory.VOLATILITY_ATR,
            description=f"ATR {period} 波动率",
            indicators=[f"ATR_{period}"],
            timeframes=["1h", "4h", "1d"],
            base_confidence=5.5,
            success_rate=0.50,
            conditions={
                "atr_spike": 2.0,
                "description": f"ATR{period} 波动异常"
            },
            tool_affinity=[ToolType.GOPHER, ToolType.LOOKER]
        )
        SonarLibrary.register(model)
    
    # Keltner通道 (6个)
    for period in [10, 14, 20, 30, 50, 100]:
        model = TrendModel(
            id=f"VOL_KELTNER_{period}",
            name=f"Keltner {period}",
            name_cn=f"肯特纳通道{period}",
            category=ModelCategory.VOLATILITY_KELTNER,
            description=f"Keltner Channel 波动",
            indicators=[f"KC_MIDDLE_{period}", f"KC_UPPER_{period}", f"KC_LOWER_{period}"],
            timeframes=["4h", "1d"],
            base_confidence=6.0,
            success_rate=0.52,
            conditions={
                "channel_break": True,
                "description": "Keltner通道突破"
            },
            tool_affinity=[ToolType.GOPHER, ToolType.FOLLOWER]
        )
        SonarLibrary.register(model)
    
    # ===== 成交量类 (~15个) =====
    # OBV系列 (5个)
    for period in [5, 10, 14, 20, 30]:
        model = TrendModel(
            id=f"VOLUME_OBV_{period}",
            name=f"OBV {period}",
            name_cn=f"能量潮{period}",
            category=ModelCategory.VOLUME_OBV,
            description=f"OBV {period} 成交量",
            indicators=[f"OBV_{period}_MA"],
            timeframes=["1h", "4h", "1d"],
            base_confidence=6.0,
            success_rate=0.52,
            conditions={
                "obv_trend": True,
                "description": f"OBV{period} 趋势确认"
            },
            tool_affinity=[ToolType.RABBIT, ToolType.GOPHER]
        )
        SonarLibrary.register(model)
    
    # VWAP系列 (5个)
    for timeframe in ["1h", "4h", "1d", "1w", "1M"]:
        model = TrendModel(
            id=f"VOLUME_VWAP_{timeframe}",
            name=f"VWAP {timeframe}",
            name_cn=f"成交量加权平均{timeframe}",
            category=ModelCategory.VOLUME_VWAP,
            description=f"VWAP 成交量加权",
            indicators=[f"VWAP_{timeframe}"],
            timeframes=[timeframe],
            base_confidence=7.0,
            success_rate=0.56,
            conditions={
                "price_above_vwap": True,
                "description": "价格与VWAP关系"
            },
            tool_affinity=[ToolType.RABBIT, ToolType.FOLLOWER]
        )
        SonarLibrary.register(model)
    
    # 成交量其他 (5个)
    for vol_type in ["VPT", "NVI", "PVI", "MFI", "CMF"]:
        model = TrendModel(
            id=f"VOLUME_{vol_type}",
            name=vol_type,
            name_cn=vol_type,
            category=ModelCategory.VOLUME_VRM,
            description=f"{vol_type} 成交量指标",
            indicators=[vol_type],
            timeframes=["4h", "1d"],
            base_confidence=6.0,
            success_rate=0.52,
            conditions={
                "volume_confirm": True,
                "description": f"{vol_type} 确认"
            },
            tool_affinity=[ToolType.RABBIT, ToolType.GOPHER]
        )
        SonarLibrary.register(model)
    
    # ===== 反转类 (~15个) =====
    # CCI系列 (5个)
    for period in [10, 14, 20, 30, 50]:
        model = TrendModel(
            id=f"REVERSAL_CCI_{period}",
            name=f"CCI {period}",
            name_cn=f"顺势指标{period}",
            category=ModelCategory.REVERSAL_CCI,
            description=f"CCI {period} 反转信号",
            indicators=[f"CCI_{period}"],
            timeframes=["1h", "4h"],
            base_confidence=6.5,
            success_rate=0.54,
            conditions={
                "extreme_above": 100,
                "extreme_below": -100,
                "description": f"CCI{period} 极端值反转"
            },
            tool_affinity=[ToolType.GOPHER, ToolType.LOOKER]
        )
        SonarLibrary.register(model)
    
    # Williams %R (5个)
    for period in [10, 14, 20, 28, 34]:
        model = TrendModel(
            id=f"REVERSAL_WILLIAMS_{period}",
            name=f"Williams %R {period}",
            name_cn=f"威廉指标{period}",
            category=ModelCategory.REVERSAL_WILLIAMS,
            description=f"Williams %R {period} 反转",
            indicators=[f"WILLIAMS_R_{period}"],
            timeframes=["1h", "4h"],
            base_confidence=6.0,
            success_rate=0.52,
            conditions={
                "oversold": -80,
                "overbought": -20,
                "description": f"Williams%R{period} 超买超卖"
            },
            tool_affinity=[ToolType.GOPHER]
        )
        SonarLibrary.register(model)
    
    # RVI (相对活力指数) (5个)
    for period in [5, 10, 14, 20, 30]:
        model = TrendModel(
            id=f"REVERSAL_RVI_{period}",
            name=f"RVI {period}",
            name_cn=f"相对活力指数{period}",
            category=ModelCategory.REVERSAL_RVI,
            description=f"RVI {period} 反转信号",
            indicators=[f"RVI_{period}", f"RVI_SIGNAL_{period}"],
            timeframes=["1h", "4h"],
            base_confidence=5.5,
            success_rate=0.50,
            conditions={
                "divergence": True,
                "description": f"RVI{period} 背离"
            },
            tool_affinity=[ToolType.LOOKER]
        )
        SonarLibrary.register(model)
    
    # ===== 通道类 (~10个) =====
    # Donchian通道 (4个)
    for period in [10, 20, 30, 50]:
        model = TrendModel(
            id=f"CHANNEL_DONCHIAN_{period}",
            name=f"Donchian {period}",
            name_cn=f"唐奇安通道{period}",
            category=ModelCategory.CHANNEL_DONCHIAN,
            description=f"Donchian {period} 通道突破",
            indicators=[f"DONCHIAN_UPPER_{period}", f"DONCHIAN_LOWER_{period}"],
            timeframes=["4h", "1d"],
            base_confidence=7.0,
            success_rate=0.56,
            conditions={
                "breakout": True,
                "description": f"Donchian{period} 突破"
            },
            tool_affinity=[ToolType.GOPHER, ToolType.FOLLOWER]
        )
        SonarLibrary.register(model)
    
    # Fibonacci通道 (3个)
    for channel_type in ["RET", "EXT", "PROJ"]:
        model = TrendModel(
            id=f"CHANNEL_FIBONACCI_{channel_type}",
            name=f"Fibonacci {channel_type}",
            name_cn=f"斐波那契通道{channel_type}",
            category=ModelCategory.CHANNEL_FIBONACCI,
            description=f"Fibonacci {channel_type} 通道",
            indicators=["FIB_236", "FIB_382", "FIB_500", "FIB_618", "FIB_786"],
            timeframes=["1d", "1w"],
            base_confidence=6.0,
            success_rate=0.52,
            conditions={
                "fib_level": True,
                "description": "斐波那契关键位"
            },
            tool_affinity=[ToolType.LOOKER]
        )
        SonarLibrary.register(model)
    
    # 修正通道/安德鲁叉 (3个)
    for variant in ["STANDARD", "SCHIFF", "MODIFIED"]:
        model = TrendModel(
            id=f"CHANNEL_PITCHFORK_{variant}",
            name=f"Pitchfork {variant}",
            name_cn=f"安德鲁叉{variant}",
            category=ModelCategory.CHANNEL_PITCHFORK,
            description=f"Pitchfork {variant} 通道",
            indicators=["PITCHFORK_MEDIAN", "PITCHFORK_UPPER", "PITCHFORK_LOWER"],
            timeframes=["1d", "1w"],
            base_confidence=5.5,
            success_rate=0.48,
            conditions={
                "price_near_median": True,
                "description": "价格靠近中线"
            },
            tool_affinity=[ToolType.LOOKER]
        )
        SonarLibrary.register(model)
    
    # ===== 其他专用类 (~8个) =====
    # Melt指标 (2个)
    for variant in ["STANDARD", "MODIFIED"]:
        model = TrendModel(
            id=f"SPECIAL_MELT_{variant}",
            name=f"Melt {variant}",
            name_cn=f"Melt指标{variant}",
            category=ModelCategory.SPECIAL_MELT,
            description=f"Melt {variant} 市场情绪",
            indicators=["MELT_SCORE", "MELT_TREND"],
            timeframes=["4h", "1d"],
            base_confidence=6.5,
            success_rate=0.55,
            conditions={
                "melt_extreme": True,
                "description": "市场情绪极端"
            },
            tool_affinity=[ToolType.LOOKER, ToolType.FOLLOWER]
        )
        SonarLibrary.register(model)
    
    # RSI背离 (3个)
    for div_type in ["BULL", "BEAR", "HIDDEN_BULL", "HIDDEN_BEAR"]:
        model = TrendModel(
            id=f"SPECIAL_RSI_DIV_{div_type}",
            name=f"RSI Divergence {div_type}",
            name_cn=f"RSI{div_type}背离",
            category=ModelCategory.SPECIAL_RSI_DIV,
            description=f"RSI {div_type} 背离",
            indicators=["RSI_14", "PRICE", "RSI_DIV_SIGNAL"],
            timeframes=["1h", "4h", "1d"],
            base_confidence=8.0,
            success_rate=0.65,
            conditions={
                "divergence_confirmed": True,
                "description": f"RSI {div_type} 背离确认"
            },
            tool_affinity=[ToolType.GOPHER, ToolType.LOOKER]
        )
        SonarLibrary.register(model)
    
    # MA交叉 (3个)
    for cross_type in ["GOLDEN", "DEATH", "TRIPLE"]:
        model = TrendModel(
            id=f"SPECIAL_MA_CROSS_{cross_type}",
            name=f"MA Cross {cross_type}",
            name_cn=f"均线{cross_type}交叉",
            category=ModelCategory.SPECIAL_MA_CROSS,
            description=f"MA {cross_type} 交叉",
            indicators=["MA_50", "MA_200", "MA_20", "MA_50", "MA_100"],
            timeframes=["1d", "1w"],
            base_confidence=7.5,
            success_rate=0.60,
            conditions={
                "cross_confirmed": True,
                "description": f"均线{cross_type}交叉确认"
            },
            tool_affinity=[ToolType.RABBIT, ToolType.LOOKER]
        )
        SonarLibrary.register(model)

# 初始化所有模型
define_trend_models()

# ==================== 信号生成器 ====================

class SignalGenerator:
    """信号生成器"""
    
    def __init__(self, indicators_data: Dict[str, float]):
        """
        初始化信号生成器
        
        Args:
            indicators_data: 指标数据字典
                {
                    "EMA_20": 50000,
                    "EMA_50": 49000,
                    "RSI_14": 65,
                    "MACD": 100,
                    "MACD_SIGNAL": 50,
                    ...
                }
        """
        self.data = indicators_data
        self.signals: List[GeneratedSignal] = []
    
    def evaluate_condition(self, condition: SignalCondition) -> Tuple[bool, float]:
        """
        评估单个条件
        
        Returns:
            (是否满足, 满足度 0-1)
        """
        indicator_value = self.data.get(condition.indicator)
        if indicator_value is None:
            return False, 0.0
        
        op = condition.operator
        target = condition.value
        
        try:
            if op == ">":
                met = indicator_value > target
                score = min(1.0, (indicator_value - target) / target * condition.weight) if met else 0.0
            elif op == "<":
                met = indicator_value < target
                score = min(1.0, (target - indicator_value) / target * condition.weight) if met else 0.0
            elif op == ">=":
                met = indicator_value >= target
                score = condition.weight if met else 0.0
            elif op == "<=":
                met = indicator_value <= target
                score = condition.weight if met else 0.0
            elif op == "==":
                met = abs(indicator_value - target) < 0.0001
                score = condition.weight if met else 0.0
            elif op == "cross_above":
                # 需要历史数据，这里简化处理
                met = False
                score = 0.0
            elif op == "cross_below":
                met = False
                score = 0.0
            else:
                met = False
                score = 0.0
            
            return met, score
        except:
            return False, 0.0
    
    def evaluate_model(self, model: TrendModel, symbol: str, price: float, timeframe: str) -> Optional[GeneratedSignal]:
        """
        评估单个模型
        
        Returns:
            如果触发则返回信号，否则None
        """
        conditions_met = []
        conditions_failed = []
        total_score = 0.0
        condition_count = 0
        
        for key, value in model.conditions.items():
            if key == "description":
                continue
            
            # 解析条件
            if key == "price_above":
                indicator = value
                indicator_value = self.data.get(indicator)
                if indicator_value and price > indicator_value:
                    conditions_met.append(f"{key}: {indicator}")
                    total_score += 1.0
                else:
                    conditions_failed.append(f"{key}: {indicator}")
                condition_count += 1
            
            elif key == "oversold":
                rsi_key = "RSI_14"
                rsi_value = self.data.get(rsi_key)
                if rsi_value and rsi_value < value:
                    conditions_met.append(f"{key}: RSI < {value}")
                    total_score += 1.5
                else:
                    conditions_failed.append(f"{key}: RSI >= {value}")
                condition_count += 1
            
            elif key == "overbought":
                rsi_key = "RSI_14"
                rsi_value = self.data.get(rsi_key)
                if rsi_value and rsi_value > value:
                    conditions_met.append(f"{key}: RSI > {value}")
                    total_score += 1.5
                else:
                    conditions_failed.append(f"{key}: RSI <= {value}")
                condition_count += 1
            
            elif key == "macd_cross":
                macd = self.data.get("MACD", 0)
                signal = self.data.get("MACD_SIGNAL", 0)
                if (macd > signal and conditions_met.count("macd_cross") == 0):
                    conditions_met.append("MACD Golden Cross")
                    total_score += 2.0
                    condition_count += 1
                elif macd < signal:
                    conditions_met.append("MACD Death Cross")
                    total_score += 2.0
                    condition_count += 1
                else:
                    conditions_failed.append("MACD No Cross")
            
            elif key == "in_channel":
                conditions_met.append("Price in channel")
                total_score += 1.0
                condition_count += 1
            
            elif key == "bandwidth":
                bb_upper = self.data.get("BB_UPPER_20", 0)
                bb_lower = self.data.get("BB_LOWER_20", 0)
                bb_mid = self.data.get("BB_MIDDLE_20", 0)
                if bb_mid > 0:
                    bandwidth = (bb_upper - bb_lower) / bb_mid
                    if bandwidth < 0.1:  # 收口
                        conditions_met.append("Bollinger Squeeze")
                        total_score += 1.5
                        condition_count += 1
                    else:
                        conditions_failed.append("Bollinger Wide")
            
            elif key == "strong_trend":
                adx = self.data.get("ADX_14", 0)
                if adx > value:
                    conditions_met.append(f"Strong trend ADX > {value}")
                    total_score += 1.5
                else:
                    conditions_failed.append(f"Weak trend ADX < {value}")
                condition_count += 1
            
            elif key == "divergence_confirmed":
                conditions_met.append("Divergence Confirmed")
                total_score += 2.0
                condition_count += 1
            
            elif key == "cross_confirmed":
                ma_50 = self.data.get("MA_50", 0)
                ma_200 = self.data.get("MA_200", 0)
                if cross_type == "GOLDEN" and ma_50 > ma_200:
                    conditions_met.append("Golden Cross")
                    total_score += 2.0
                    condition_count += 1
                elif cross_type == "DEATH" and ma_50 < ma_200:
                    conditions_met.append("Death Cross")
                    total_score += 2.0
                    condition_count += 1
                else:
                    conditions_failed.append("No MA Cross")
            
            else:
                # 未知条件类型，跳过
                pass
        
        # 判断信号类型
        if condition_count == 0:
            return None
        
        match_ratio = len(conditions_met) / condition_count if condition_count > 0 else 0
        
        if match_ratio < 0.5:
            return None
        
        # 计算置信度
        confidence = (total_score / condition_count) * model.current_confidence / 10.0
        confidence = min(1.0, confidence)
        
        # 判断方向
        if "Golden" in str(conditions_met) or "price_above" in str(conditions_met):
            direction = TrendDirection.BULL
            signal_type = SignalType.BUY
        elif "Death" in str(conditions_met) or price < self.data.get("EMA_200", price):
            direction = TrendDirection.BEAR
            signal_type = SignalType.SELL
        else:
            direction = TrendDirection.SIDEWAYS
            signal_type = SignalType.NEUTRAL
        
        # 更新模型统计
        model.match_count += 1
        
        return GeneratedSignal(
            id=f"SIG_{model.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            timestamp=datetime.now().isoformat(),
            symbol=symbol,
            model_id=model.id,
            model_name=model.name,
            signal_type=signal_type,
            direction=direction,
            confidence=confidence,
            price=price,
            timeframe=timeframe,
            conditions_met=conditions_met,
            metadata={"match_ratio": match_ratio, "total_score": total_score}
        )
    
    def scan_all_models(self, symbol: str, price: float, timeframe: str = "1h") -> List[GeneratedSignal]:
        """
        扫描所有模型，生成信号列表
        """
        signals = []
        
        for model in SonarLibrary.get_all_models():
            if timeframe not in model.timeframes:
                continue
            
            signal = self.evaluate_model(model, symbol, price, timeframe)
            if signal:
                signals.append(signal)
        
        self.signals = signals
        return signals

# ==================== 信号聚合器 ====================

class SignalAggregator:
    """信号聚合器 - 多模型共识"""
    
    def __init__(self, signals: List[GeneratedSignal]):
        self.signals = signals
    
    def aggregate(self, tool: ToolType = None) -> AggregatedSignal:
        """
        聚合信号，生成共识信号
        
        Args:
            tool: 指定工具类型，如果不指定则根据信号自动判断
            
        Returns:
            AggregatedSignal - 聚合后的信号
        """
        if not self.signals:
            return None
        
        # 方向投票
        direction_votes = Counter([s.direction for s in self.signals])
        primary_direction = direction_votes.most_common(1)[0][0]
        
        # 信号类型投票
        type_votes = Counter([s.signal_type for s in self.signals])
        primary_type = type_votes.most_common(1)[0][0]
        
        # 置信度加权平均
        total_confidence = sum(s.confidence for s in self.signals) / len(self.signals)
        
        # 共识度计算
        top_direction_count = direction_votes.most_common(1)[0][1]
        consensus_score = top_direction_count / len(self.signals)
        
        # 判断工具
        if tool is None:
            # 根据信号模型判断适合的工具
            tool_affinity_count = Counter()
            for s in self.signals:
                model = SonarLibrary.MODELS.get(s.model_id)
                if model:
                    for t in model.tool_affinity:
                        tool_affinity_count[t] += 1
            if tool_affinity_count:
                tool = tool_affinity_count.most_common(1)[0][0]
            else:
                tool = ToolType.RABBIT  # 默认打兔子
        
        # 过滤同方向信号
        aligned_signals = [s for s in self.signals if s.direction == primary_direction]
        
        return AggregatedSignal(
            symbol=self.signals[0].symbol,
            timestamp=datetime.now().isoformat(),
            signals=self.signals,
            aggregated_direction=primary_direction,
            aggregated_confidence=total_confidence,
            consensus_score=consensus_score,
            primary_tool=tool,
            metadata={
                "signal_count": len(self.signals),
                "aligned_count": len(aligned_signals),
                "direction_votes": {k.value: v for k, v in direction_votes.items()},
                "type_votes": {k.value: v for k, v in type_votes.items()},
                "aligned_signals": [s.id for s in aligned_signals]
            }
        )
    
    def aggregate_by_category(self) -> Dict[ModelCategory, AggregatedSignal]:
        """
        按类别聚合信号
        """
        results = {}
        
        for signal in self.signals:
            model = SonarLibrary.MODELS.get(signal.model_id)
            if model:
                if model.category not in results:
                    results[model.category] = []
                results[model.category].append(signal)
        
        return {
            cat: SignalAggregator(sigs).aggregate()
            for cat, sigs in results.items() if sigs
        }

# ==================== 策略配置 ====================

@dataclass
class ToolStrategy:
    """工具策略配置"""
    tool_type: ToolType
    name: str
    name_cn: str
    description: str
    position_limit: float  # 仓位上限 %
    stop_loss: float       # 止损 %
    take_profit: float     # 止盈 %
    max_positions: int      # 最大持仓数
    applicable_models: List[str]  # 适用的模型ID列表
    risk_level: str        # 风险等级: LOW, MEDIUM, HIGH
    conditions: Dict[str, Any]  # 其他条件
    
    def to_dict(self) -> Dict:
        return {
            "tool_type": self.tool_type.value,
            "name": self.name,
            "name_cn": self.name_cn,
            "description": self.description,
            "position_limit": self.position_limit,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "max_positions": self.max_positions,
            "applicable_models": self.applicable_models,
            "risk_level": self.risk_level,
            "conditions": self.conditions
        }

class StrategyConfig:
    """策略配置管理器"""
    
    TOOLS: Dict[ToolType, ToolStrategy] = {}
    
    @classmethod
    def register_tool(cls, strategy: ToolStrategy):
        cls.TOOLS[strategy.tool_type] = strategy
    
    @classmethod
    def get_tool(cls, tool: ToolType) -> Optional[ToolStrategy]:
        return cls.TOOLS.get(tool)
    
    @classmethod
    def get_all_tools(cls) -> List[ToolStrategy]:
        return list(cls.TOOLS.values())
    
    @classmethod
    def to_json(cls) -> str:
        return json.dumps(
            {"tools": [t.to_dict() for t in cls.TOOLS.values()]},
            ensure_ascii=False,
            indent=2
        )
    
    @classmethod
    def from_json(cls, json_str: str):
        data = json.loads(json_str)
        for tool_data in data.get("tools", []):
            strategy = ToolStrategy(
                tool_type=ToolType[tool_data["tool_type"]],
                name=tool_data["name"],
                name_cn=tool_data["name_cn"],
                description=tool_data["description"],
                position_limit=tool_data["position_limit"],
                stop_loss=tool_data["stop_loss"],
                take_profit=tool_data["take_profit"],
                max_positions=tool_data["max_positions"],
                applicable_models=tool_data["applicable_models"],
                risk_level=tool_data["risk_level"],
                conditions=tool_data["conditions"]
            )
            cls.register_tool(strategy)


# ==================== 工具策略定义 ====================

def define_tool_strategies():
    """定义7大工具策略"""
    
    # 🐰 打兔子 - 前20主流加密货币
    rabbit_models = [
        m.id for m in SonarLibrary.MODELS.values() 
        if ToolType.RABBIT in m.tool_affinity
    ]
    
    StrategyConfig.register_tool(ToolStrategy(
        tool_type=ToolType.RABBIT,
        name="Rabbit Strategy",
        name_cn="打兔子策略",
        description="前20主流加密货币，稳定收益策略",
        position_limit=25.0,
        stop_loss=5.0,
        take_profit=8.0,
        max_positions=10,
        applicable_models=rabbit_models[:20],  # 限制20个模型
        risk_level="LOW",
        conditions={
            "trend恶化_减仓": True,
            "RSI大于75": {"action": "reduce_position", "target": 15},
            "ADX下降": {"action": "switch_tool", "target": "GOPHER"},
            "主要标的": "BTC,ETH,BNB,SOL,XRP,ADA,DOT,AVAX,DOGE,MATIC,LINK,UNI,LTC,ATOM,XLM,ETC,XMR,ALGO,FIL,VET"
        }
    ))
    
    # 🐹 打地鼠 - 其他加密货币
    gopher_models = [
        m.id for m in SonarLibrary.MODELS.values() 
        if ToolType.GOPHER in m.tool_affinity
    ]
    
    StrategyConfig.register_tool(ToolStrategy(
        tool_type=ToolType.GOPHER,
        name="Gopher Strategy",
        name_cn="打地鼠策略",
        description="其他加密货币，火控雷达锁定异动",
        position_limit=20.0,
        stop_loss=8.0,
        take_profit=15.0,
        max_positions=20,
        applicable_models=gopher_models[:25],
        risk_level="MEDIUM",
        conditions={
            "火控雷达_锁定": True,
            "波动异常检测": {"threshold": 2.0, "indicator": "ATR"},
            "专家模式_止盈可移除": True,
            "适用场景": "非主流币、异动币、小市值币"
        }
    ))
    
    # 🔮 走着瞧 - 预测市场
    looker_models = [
        m.id for m in SonarLibrary.MODELS.values() 
        if ToolType.LOOKER in m.tool_affinity
    ]
    
    StrategyConfig.register_tool(ToolStrategy(
        tool_type=ToolType.LOOKER,
        name="Looker Strategy",
        name_cn="走着瞧策略",
        description="预测市场 + MiroFish仿真",
        position_limit=15.0,
        stop_loss=5.0,
        take_profit=10.0,
        max_positions=5,
        applicable_models=looker_models[:15],
        risk_level="MEDIUM",
        conditions={
            "MiroFish_仿真": True,
            "胜率门槛": 0.65,
            "预测市场集成": ["Polymarket", "Betfair", "Augur"],
            "策略对比": True,
            "适用场景": "预测事件、选举、赛事结果"
        }
    ))
    
    # 👑 跟大哥 - 做市协作
    follower_models = [
        m.id for m in SonarLibrary.MODELS.values() 
        if ToolType.FOLLOWER in m.tool_affinity
    ]
    
    StrategyConfig.register_tool(ToolStrategy(
        tool_type=ToolType.FOLLOWER,
        name="Follower Strategy",
        name_cn="跟大哥策略",
        description="做市协作 + MiroFish评估",
        position_limit=15.0,
        stop_loss=3.0,
        take_profit=6.0,
        max_positions=8,
        applicable_models=follower_models[:15],
        risk_level="MEDIUM",
        conditions={
            "MiroFish_评估": True,
            "最大跟单比例": 0.30,
            "综合判断": True,
            "主要标的": "主流交易所做市商信号",
            "适用场景": "跟单做市、大户信号"
        }
    ))
    
    # 🍀 搭便车 - 跟单分成
    hitchhike_models = [
        m.id for m in SonarLibrary.MODELS.values() 
        if ToolType.HITCHHIKE in m.tool_affinity
    ]
    
    StrategyConfig.register_tool(ToolStrategy(
        tool_type=ToolType.HITCHHIKE,
        name="Hitchhike Strategy",
        name_cn="搭便车策略",
        description="跟单分成 + 二级分包",
        position_limit=10.0,
        stop_loss=5.0,
        take_profit=8.0,
        max_positions=10,
        applicable_models=hitchhike_models[:10],
        risk_level="MEDIUM",
        conditions={
            "二级分包": True,
            "加强风控": True,
            "策略仿真": True,
            "分成比例": "70/30",
            "适用场景": "专业跟单平台、信号订阅"
        }
    ))
    
    # 💰 薅羊毛 - 空投猎手
    airdrop_models = [
        m.id for m in SonarLibrary.MODELS.values() 
        if ToolType.AIREDROP in m.tool_affinity
    ]
    
    StrategyConfig.register_tool(ToolStrategy(
        tool_type=ToolType.AIREDROP,
        name="Airdrop Strategy",
        name_cn="薅羊毛策略",
        description="空投猎手，只读安全",
        position_limit=3.0,
        stop_loss=2.0,
        take_profit=20.0,
        max_positions=30,
        applicable_models=airdrop_models[:5],
        risk_level="HIGH",
        conditions={
            "杜绝授权链接": True,
            "中转钱包隔离": True,
            "只读API": True,
            "安全第一": "永远不授权资产",
            "适用场景": "新项目空投、测试网交互"
        }
    ))
    
    # 👶 穷孩子 - 众包赚钱
    crowdsource_models = [
        m.id for m in SonarLibrary.MODELS.values() 
        if ToolType.CROWDSOURCE in m.tool_affinity
    ]
    
    StrategyConfig.register_tool(ToolStrategy(
        tool_type=ToolType.CROWDSOURCE,
        name="Crowdsource Strategy",
        name_cn="穷孩子策略",
        description="众包赚钱 + EvoMap隔离",
        position_limit=2.0,
        stop_loss=1.0,
        take_profit=30.0,
        max_positions=5,
        applicable_models=crowdsource_models[:5],
        risk_level="HIGH",
        conditions={
            "EvoMap_社交圈": True,
            "人设收益": True,
            "隔离保护": True,
            "适用场景": "众包任务、微任务平台"
        }
    ))

# 初始化工具策略
define_tool_strategies()

# ==================== 工具函数 ====================

def get_sonar_stats() -> Dict:
    """获取声纳库统计"""
    return {
        "model_count": SonarLibrary.model_count(),
        "tool_count": len(StrategyConfig.TOOLS),
        "tools": {
            t.value: {
                "name_cn": s.name_cn,
                "position_limit": s.position_limit,
                "model_count": len(s.applicable_models)
            }
            for t, s in StrategyConfig.TOOLS.items()
        }
    }

def create_test_signal() -> GeneratedSignal:
    """创建测试信号"""
    indicators = {
        "EMA_20": 50000,
        "EMA_50": 49000,
        "EMA_200": 48000,
        "RSI_14": 65,
        "MACD": 100,
        "MACD_SIGNAL": 50,
        "ADX_14": 30,
        "BB_UPPER_20": 52000,
        "BB_LOWER_20": 48000,
        "BB_MIDDLE_20": 50000,
    }
    
    generator = SignalGenerator(indicators)
    signals = generator.scan_all_models("BTCUSDT", 50500, "1h")
    
    if signals:
        return signals[0]
    return None

# ==================== 主入口 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("声纳库 V3 - 123趋势模型 + 7工具策略")
    print("=" * 60)
    
    stats = get_sonar_stats()
    print(f"\n📊 模型统计:")
    print(f"   总模型数: {stats['model_count']['total']}")
    print(f"   工具数: {stats['tool_count']}")
    
    print(f"\n📈 各类模型数量:")
    for cat, count in stats['model_count']['by_category'].items():
        print(f"   {cat}: {count}")
    
    print(f"\n🛠️ 工具配置:")
    for tool_id, tool_info in stats['tools'].items():
        print(f"   {tool_id}: {tool_info['name_cn']} - {tool_info['model_count']}个模型")
    
    print("\n✅ 声纳库初始化完成")
