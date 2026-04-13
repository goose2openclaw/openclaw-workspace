#!/usr/bin/env python3
"""
🎯 GO2SE 强化推荐引擎 V2
=========================
支持做多做空双向推荐
多因子置信度评分
分档位推送
"""

import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import statistics

# ─── 信号枚举 ───────────────────────────────────────────────

class SignalDirection(str, Enum):
    LONG = "LONG"      # 做多
    SHORT = "SHORT"    # 做空
    CLOSE_LONG = "CLOSE_LONG"
    CLOSE_SHORT = "CLOSE_SHORT"
    HOLD = "HOLD"      # 观望

class SignalStrength(str, Enum):
    STRONG_BUY = "STRONG_BUY"   # 强烈买入
    BUY = "BUY"                  # 买入
    HOLD = "HOLD"                # 观望
    SELL = "SELL"               # 卖出
    STRONG_SELL = "STRONG_SELL"  # 强烈卖出

# ─── 推荐档位配置 ───────────────────────────────────────────

LONG_TIERS = {
    "conservative": {
        "name": "保守做多",
        "leverage": 2,
        "max_position": 0.10,
        "min_confidence": 0.75,
        "stop_loss": 0.03,
        "take_profit": 0.08,
    },
    "moderate": {
        "name": "平衡做多",
        "leverage": 3,
        "max_position": 0.20,
        "min_confidence": 0.65,
        "stop_loss": 0.05,
        "take_profit": 0.15,
    },
    "aggressive": {
        "name": "激进做多",
        "leverage": 5,
        "max_position": 0.25,
        "min_confidence": 0.55,
        "stop_loss": 0.08,
        "take_profit": 0.25,
    },
}

SHORT_TIERS = {
    "conservative": {
        "name": "保守做空",
        "leverage": 2,
        "max_position": 0.08,  # 做空仓位更小
        "min_confidence": 0.78,  # 做空要求更高置信度
        "stop_loss": 0.04,  # 做空止损更紧
        "take_profit": 0.10,
    },
    "moderate": {
        "name": "平衡做空",
        "leverage": 3,
        "max_position": 0.15,
        "min_confidence": 0.68,
        "stop_loss": 0.06,
        "take_profit": 0.18,
    },
    "aggressive": {
        "name": "激进做空",
        "leverage": 5,
        "max_position": 0.20,
        "min_confidence": 0.58,
        "stop_loss": 0.10,
        "take_profit": 0.30,
    },
}

# ─── 做空触发条件 ───────────────────────────────────────────

SHORT_TRIGGERS = {
    "rsi_overbought": 70,        # RSI ≥ 70
    "rsi_extreme": 80,           # RSI ≥ 80 强烈做空
    "price_rejection": -3.0,     # 价格从高点回落 ≥ 3%
    "volume_surge_sell": 2.0,   # 卖出量激增 ≥ 2x
    "macd_death_cross": True,    # MACD 死叉
    "bollinger_upper_touch": True, # 触及布林带上轨
    "trend_reversal": -5.0,      # 趋势反转跌幅 ≥ 5%
    "whale_sell_ratio": 0.65,   # 大户卖出占比 ≥ 65%
}

LONG_TRIGGERS = {
    "rsi_oversold": 30,        # RSI ≤ 30
    "rsi_extreme": 20,          # RSI ≤ 20 强烈买入
    "price_bounce": 3.0,        # 从支撑位反弹 ≥ 3%
    "volume_surge_buy": 2.0,   # 买入量激增 ≥ 2x
    "macd_golden_cross": True,   # MACD 金叉
    "bollinger_lower_touch": True, # 触及布林带下轨
    "trend_reversal": 5.0,     # 趋势反转涨幅 ≥ 5%
    "whale_buy_ratio": 0.65,    # 大户买入占比 ≥ 65%
}

# ─── 数据类 ───────────────────────────────────────────────

@dataclass
class MarketIndicators:
    """市场指标"""
    symbol: str
    price: float
    change_24h: float
    volume_24h: float
    rsi: float
    macd: float
    macd_signal: float
    bollinger_upper: float
    bollinger_lower: float
    whale_buy_ratio: float
    whale_sell_ratio: float
    volume_surge: float


@dataclass
class Recommendation:
    """推荐结果"""
    symbol: str
    direction: SignalDirection
    strength: SignalStrength
    confidence: float  # 0.0 - 1.0
    leverage: int
    position_size: float
    stop_loss: float
    take_profit: float
    reason: List[str]
    tier: str
    timestamp: str


# ─── 推荐引擎 ───────────────────────────────────────────────

class RecommendationEngine:
    """
    🎯 GO2SE 强化推荐引擎 V2
    支持做多/做空双向推荐
    """

    def __init__(self):
        self.long_tiers = LONG_TIERS
        self.short_tiers = SHORT_TIERS

    def analyze(self, indicators: MarketIndicators, prefer_direction: str = "auto") -> Recommendation:
        """
        分析市场指标，生成推荐

        Args:
            indicators: 市场指标数据
            prefer_direction: 偏好方向 ("long", "short", "auto")
        """
        ts = time.strftime("%Y-%m-%d %H:%M:%S")

        # ─── Step 1: 计算各方向置信度 ──────────────────────────
        long_conf = self._calc_long_confidence(indicators)
        short_conf = self._calc_short_confidence(indicators)

        # ─── Step 2: 确定方向 ────────────────────────────────
        if prefer_direction == "long" and long_conf > 0.5:
            direction = SignalDirection.LONG
            confidence = long_conf
        elif prefer_direction == "short" and short_conf > 0.5:
            direction = SignalDirection.SHORT
            confidence = short_conf
        elif long_conf > short_conf + 0.05:
            direction = SignalDirection.LONG
            confidence = long_conf
        elif short_conf > long_conf + 0.05:
            direction = SignalDirection.SHORT
            confidence = short_conf
        else:
            direction = SignalDirection.HOLD
            confidence = max(long_conf, short_conf)

        # ─── Step 3: 平仓信号 ──────────────────────────────
        if direction == SignalDirection.LONG and indicators.change_24h < -5:
            direction = SignalDirection.CLOSE_SHORT
            confidence = min(1.0, abs(indicators.change_24h) / 5 * 0.8)
        if direction == SignalDirection.SHORT and indicators.change_24h > 5:
            direction = SignalDirection.CLOSE_LONG
            confidence = min(1.0, indicators.change_24h / 5 * 0.8)

        # ─── Step 4: 选择档位 ─────────────────────────────
        if direction == SignalDirection.LONG:
            tier = self._select_tier(confidence, self.long_tiers)
            stop_loss = tier["stop_loss"]
            take_profit = tier["take_profit"]
        elif direction == SignalDirection.SHORT:
            tier = self._select_tier(confidence, self.short_tiers)
            stop_loss = tier["stop_loss"]
            take_profit = tier["take_profit"]
        else:
            tier = {"name": "观望", "leverage": 1, "max_position": 0}
            stop_loss = 0
            take_profit = 0

        # ─── Step 5: 计算信号强度 ─────────────────────────
        if confidence >= 0.80:
            strength = SignalStrength.STRONG_BUY if direction == SignalDirection.LONG else SignalStrength.STRONG_SELL
        elif confidence >= 0.65:
            strength = SignalStrength.BUY if direction == SignalDirection.LONG else SignalStrength.SELL
        else:
            strength = SignalStrength.HOLD

        # ─── Step 6: 生成原因列表 ─────────────────────────
        reasons = self._generate_reasons(indicators, direction, confidence)

        return Recommendation(
            symbol=indicators.symbol,
            direction=direction,
            strength=strength,
            confidence=round(confidence, 3),
            leverage=tier.get("leverage", 1),
            position_size=tier.get("max_position", 0),
            stop_loss=stop_loss,
            take_profit=take_profit,
            reason=reasons,
            tier=tier.get("name", "观望"),
            timestamp=ts,
        )

    def _calc_long_confidence(self, m: MarketIndicators) -> float:
        """计算做多置信度 0-1"""
        score = 0.0
        reasons = 0

        # RSI 超卖
        if m.rsi <= 30:
            score += 0.25
            reasons += 1
        elif m.rsi <= 40:
            score += 0.15
            reasons += 1

        # 价格从支撑反弹
        if m.change_24h >= 3:
            score += 0.20
            reasons += 1
        elif m.change_24h >= 1:
            score += 0.10
            reasons += 1

        # MACD 金叉
        if m.macd > m.macd_signal:
            score += 0.20
            reasons += 1

        # 布林带下轨
        if m.price <= m.bollinger_lower * 1.02:
            score += 0.15
            reasons += 1

        # 大户买入
        if m.whale_buy_ratio >= 0.60:
            score += 0.15
            reasons += 1

        # 成交量激增
        if m.volume_surge >= 2.0:
            score += 0.10
            reasons += 1

        # 归一化
        max_possible = 1.05  # 略大于1.0用于平滑
        return min(0.99, score / max_possible)

    def _calc_short_confidence(self, m: MarketIndicators) -> float:
        """计算做空置信度 0-1"""
        score = 0.0

        # RSI 超买
        if m.rsi >= 70:
            score += 0.25
        elif m.rsi >= 60:
            score += 0.15

        # 价格从高点回落
        if m.change_24h <= -3:
            score += 0.20
        elif m.change_24h <= -1:
            score += 0.10

        # MACD 死叉
        if m.macd < m.macd_signal:
            score += 0.20

        # 布林带上轨
        if m.price >= m.bollinger_upper * 0.98:
            score += 0.15

        # 大户卖出
        if m.whale_sell_ratio >= 0.60:
            score += 0.15

        # 成交量激增卖出
        if m.volume_surge >= 2.0:
            score += 0.10

        max_possible = 1.05
        return min(0.99, score / max_possible)

    def _select_tier(self, confidence: float, tiers: dict) -> dict:
        """根据置信度选择档位"""
        if confidence >= 0.75:
            return tiers.get("conservative", tiers["moderate"])
        elif confidence >= 0.60:
            return tiers.get("moderate", tiers["aggressive"])
        else:
            return tiers.get("aggressive", tiers["moderate"])

    def _generate_reasons(self, m: MarketIndicators, direction: SignalDirection, confidence: float) -> List[str]:
        """生成推荐原因"""
        reasons = []
        if direction == SignalDirection.LONG:
            if m.rsi <= 30:
                reasons.append(f"RSI超卖({m.rsi:.1f})")
            if m.change_24h >= 3:
                reasons.append(f"价格反弹({m.change_24h:+.1f}%)")
            if m.macd > m.macd_signal:
                reasons.append("MACD金叉")
            if m.whale_buy_ratio >= 0.60:
                reasons.append(f"大户买入占比{m.whale_buy_ratio:.0%}")
        elif direction == SignalDirection.SHORT:
            if m.rsi >= 70:
                reasons.append(f"RSI过热({m.rsi:.1f})")
            if m.change_24h <= -3:
                reasons.append(f"价格回落({m.change_24h:+.1f}%)")
            if m.macd < m.macd_signal:
                reasons.append("MACD死叉")
            if m.whale_sell_ratio >= 0.60:
                reasons.append(f"大户卖出占比{m.whale_sell_ratio:.0%}")
        else:
            reasons.append("多空信号均衡，观望")
        reasons.append(f"置信度{confidence:.0%}")
        return reasons

    def batch_analyze(self, symbols: List[str], market_data_fn) -> List[Recommendation]:
        """批量分析多个币种"""
        results = []
        for symbol in symbols:
            try:
                data = market_data_fn(symbol)
                indicators = MarketIndicators(**data)
                rec = self.analyze(indicators)
                results.append(rec)
            except Exception:
                pass
        # 按置信度排序
        results.sort(key=lambda x: x.confidence, reverse=True)
        return results


# ─── 快捷函数 ───────────────────────────────────────────────
_engine: Optional[RecommendationEngine] = None

def get_engine() -> RecommendationEngine:
    global _engine
    if _engine is None:
        _engine = RecommendationEngine()
    return _engine

def get_recommendation(symbol: str, indicators: dict, prefer: str = "auto") -> Recommendation:
    """快捷获取推荐"""
    m = MarketIndicators(**indicators)
    return get_engine().analyze(m, prefer)
