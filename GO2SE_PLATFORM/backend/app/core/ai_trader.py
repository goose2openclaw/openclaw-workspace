#!/usr/bin/env python3
"""
🎯 GO2SE AI 自主交易决策引擎
=============================
自动判断做多/做空/观望
基于多因子综合评分
"""

import time
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

# ─── 决策枚举 ─────────────────────────────────────────────

class TradeDirection(Enum):
    """交易方向"""
    LONG = "long"      # 做多
    SHORT = "short"     # 做空
    HOLD = "hold"       # 观望
    CLOSE_LONG = "close_long"   # 平多
    CLOSE_SHORT = "close_short"  # 平空

class MarketRegime(Enum):
    """市场状态"""
    BULL = "bull"       # 牛市
    BEAR = "bear"        # 熊市
    NEUTRAL = "neutral"  # 中性
    VOLATILE = "volatile" # 波动

# ─── 决策信号 ─────────────────────────────────────────────

@dataclass
class TradingSignal:
    """交易信号"""
    symbol: str
    direction: TradeDirection
    confidence: float        # 0-100
    reason: str
    factors: Dict[str, float]  # 各因子得分
    regime: MarketRegime
    timestamp: str
    urgency: str = "normal"  # low, normal, high

@dataclass
class AITraderConfig:
    """AI交易配置"""
    # 阈值
    long_threshold: float = 65.0   # >65分 做多
    short_threshold: float = 65.0  # >65分 做空
    hold_threshold: float = 50.0    # <50分 观望
    
    # 仓位
    default_position_pct: float = 10.0  # 默认仓位 10%
    max_position_pct: float = 60.0      # 最大仓位 60%
    min_confidence_for_full: float = 80.0  # 满仓置信度
    
    # 风控
    max_loss_per_trade: float = 5.0   # 单笔最大亏损 %
    stop_loss_pct: float = 3.0         # 止损 %
    take_profit_pct: float = 6.0       # 止盈 %
    
    # 切换冷却
    direction_switch_cooldown_minutes: int = 30  # 方向切换冷却时间

# ─── AI 交易引擎 ─────────────────────────────────────────

class AITrader:
    """
    AI 自主交易决策引擎
    
    多因子评分:
    - 趋势因子 (30%): EMA, MA, 趋势线
    - 动量因子 (25%): RSI, MACD, Stochastic
    - 波动因子 (15%): ATR, Bollinger Bands
    - 结构因子 (15%): 支撑阻力, 斐波那契
    - 情绪因子 (15%): 资金流, 大户动向
    """
    
    def __init__(self, config: AITraderConfig = None):
        self.config = config or AITraderConfig()
        self.last_signals: Dict[str, TradingSignal] = {}
        self.last_switch_time: Dict[str, datetime] = {}
        
    def analyze_and_decide(self, symbol: str, market_data: Dict) -> TradingSignal:
        """
        分析市场数据并决策
        
        Args:
            symbol: 交易对如 BTCUSDT
            market_data: 市场数据 {
                price, rsi, macd, volume, ema_9, ema_21, ema_50,
                bb_upper, bb_lower, atr, adx,
                volume_ratio, price_change_24h,
                funding_rate, whale_ratio
            }
        """
        try:
            factors = self._calculate_factors(market_data)
            total_score = factors["total"]  # 使用归一化的总分，不是sum()
        except Exception as e:
            # 因子计算失败，返回观望信号
            return TradingSignal(
                symbol=symbol,
                direction=TradeDirection.HOLD,
                confidence=0,
                reason=f"因子计算失败: {str(e)}",
                factors={},
                regime=MarketRegime.NEUTRAL,
                timestamp=datetime.utcnow().isoformat(),
                urgency="low"
            )
        
        try:
            # 判断市场状态
            regime = self._detect_regime(market_data, factors)
            
            # 决策
            direction, confidence, reason = self._make_decision(
                symbol, factors, regime, total_score
            )
        except Exception as e:
            # 决策失败，返回观望信号
            return TradingSignal(
                symbol=symbol,
                direction=TradeDirection.HOLD,
                confidence=0,
                reason=f"决策失败: {str(e)}",
                factors=factors,
                regime=MarketRegime.NEUTRAL,
                timestamp=datetime.utcnow().isoformat(),
                urgency="low"
            )
        
        # 检查冷却时间
        if self._is_in_cooldown(symbol, direction):
            return TradingSignal(
                symbol=symbol,
                direction=TradeDirection.HOLD,
                confidence=confidence,
                reason=f"切换冷却中 ({self.config.direction_switch_cooldown_minutes}分钟内不重复切换)",
                factors=factors,
                regime=regime,
                timestamp=datetime.utcnow().isoformat(),
                urgency="low"
            )
        
        signal = TradingSignal(
            symbol=symbol,
            direction=direction,
            confidence=confidence,
            reason=reason,
            factors=factors,
            regime=regime,
            timestamp=datetime.utcnow().isoformat(),
            urgency=self._calculate_urgency(confidence, factors)
        )
        
        self.last_signals[symbol] = signal
        return signal
    
    def _calculate_factors(self, data: Dict) -> Dict[str, float]:
        """计算各因子得分"""
        scores = {}
        
        # 1. 趋势因子 (30%)
        trend_score = self._trend_factor(data)
        scores["trend"] = trend_score
        
        # 2. 动量因子 (25%)
        momentum_score = self._momentum_factor(data)
        scores["momentum"] = momentum_score
        
        # 3. 波动因子 (15%)
        volatility_score = self._volatility_factor(data)
        scores["volatility"] = volatility_score
        
        # 4. 结构因子 (15%)
        structure_score = self._structure_factor(data)
        scores["structure"] = structure_score
        
        # 5. 情绪因子 (15%)
        sentiment_score = self._sentiment_factor(data)
        scores["sentiment"] = sentiment_score
        
        # 加权总分
        total = (
            trend_score * 0.30 +
            momentum_score * 0.25 +
            volatility_score * 0.15 +
            structure_score * 0.15 +
            sentiment_score * 0.15
        )
        scores["total"] = total
        
        return scores
    
    def _trend_factor(self, data: Dict) -> float:
        """趋势因子"""
        score = 50.0  # 中性
        
        # EMA 趋势
        ema_9 = data.get("ema_9", 0)
        ema_21 = data.get("ema_21", 0)
        ema_50 = data.get("ema_50", 0)
        price = data.get("price", 0)
        
        if ema_9 > ema_21 > ema_50 and price > ema_9:
            score += 20  # 多头排列
        elif ema_9 < ema_21 < ema_50 and price < ema_9:
            score -= 20  # 空头排列
        
        # ADX 趋势强度
        adx = data.get("adx", 0)
        if adx > 25:
            if score > 50:
                score += 10  # 强势上涨
            elif score < 50:
                score -= 10  # 强势下跌
        
        return max(0, min(100, score))
    
    def _momentum_factor(self, data: Dict) -> float:
        """动量因子"""
        score = 50.0
        
        rsi = data.get("rsi", 50)
        macd = data.get("macd", 0)
        macd_signal = data.get("macd_signal", 0)
        
        # RSI
        if rsi < 30:
            score += 20  # 超卖
        elif rsi > 70:
            score -= 20  # 超买
        elif 40 <= rsi <= 60:
            score += 5   # 中性偏多
        
        # MACD
        if macd > macd_signal:
            score += 10
        else:
            score -= 10
        
        return max(0, min(100, score))
    
    def _volatility_factor(self, data: Dict) -> float:
        """波动因子"""
        score = 50.0
        
        bb_upper = data.get("bb_upper", 0)
        bb_lower = data.get("bb_lower", 0)
        price = data.get("price", 0)
        atr = data.get("atr", 0)
        
        # 布林带位置
        if bb_upper > bb_lower > 0:
            bb_position = (price - bb_lower) / (bb_upper - bb_lower) * 100
            
            if bb_position < 20:
                score += 15  # 接近下轨，超卖
            elif bb_position > 80:
                score -= 15  # 接近上轨，超买
        
        # ATR 波动率
        if atr > 0 and price > 0:
            atr_pct = atr / price * 100
            if atr_pct > 5:
                score -= 5  # 高波动，减少仓位
        
        return max(0, min(100, score))
    
    def _structure_factor(self, data: Dict) -> float:
        """结构因子"""
        score = 50.0
        
        price = data.get("price", 0)
        support = data.get("support", 0)
        resistance = data.get("resistance", 0)
        
        # 支撑阻力
        if support > 0 and price < support * 1.02:
            score += 15  # 接近支撑
        elif resistance > 0 and price > resistance * 0.98:
            score -= 15  # 接近阻力
        
        # 24h 价格变化
        change = data.get("price_change_24h", 0)
        if change > 3:
            score -= 5  # 24h涨幅过大
        elif change < -3:
            score += 5  # 24h跌幅过大
        
        return max(0, min(100, score))
    
    def _sentiment_factor(self, data: Dict) -> float:
        """情绪因子"""
        score = 50.0
        
        volume_ratio = data.get("volume_ratio", 1.0)
        whale_ratio = data.get("whale_ratio", 0.5)
        funding_rate = data.get("funding_rate", 0)
        
        # 成交量
        if volume_ratio > 1.5:
            score += 10  # 放量
        elif volume_ratio < 0.7:
            score -= 5   # 缩量
        
        # 资金费率 (期货)
        if funding_rate > 0.01:
            score -= 10  # 多头过度拥挤
        elif funding_rate < -0.01:
            score += 10  # 空头过度拥挤
        
        # 巨鲸比率
        if whale_ratio > 0.7:
            score += 5   # 主力看多
        elif whale_ratio < 0.3:
            score -= 5   # 主力看空
        
        return max(0, min(100, score))
    
    def _detect_regime(self, data: Dict, factors: Dict) -> MarketRegime:
        """检测市场状态"""
        adx = data.get("adx", 0)
        rsi = data.get("rsi", 50)
        price = data.get("price", 0)
        ema_50 = data.get("ema_50", 0)
        
        # ADX 判断趋势强度
        if adx < 20:
            return MarketRegime.NEUTRAL
        
        # 价格 vs EMA50 (放宽条件)
        if price > ema_50 and adx > 25:
            return MarketRegime.BULL
        
        if price < ema_50 and adx > 25:
            return MarketRegime.BEAR
        
        # 波动判断
        if factors.get("volatility", 50) < 35:
            return MarketRegime.VOLATILE
        
        return MarketRegime.NEUTRAL
    
    def _make_decision(
        self, symbol: str, factors: Dict[str, float], 
        regime: MarketRegime, total: float
    ) -> Tuple[TradeDirection, float, str]:
        """做出交易决策"""
        
        # 检查现有持仓方向
        existing_direction = self._get_existing_position_direction(symbol)
        
        # 决策逻辑 - 熊市优先做空，牛市优先做多
        if regime == MarketRegime.BEAR:
            # 熊市格局，强烈做空信号
            if existing_direction == "LONG":
                direction = TradeDirection.CLOSE_LONG
                reason = "熊市信号，平多仓"
            else:
                direction = TradeDirection.SHORT
                reason = self._build_short_reason(factors, regime) + " (熊市)"
            confidence = min(100, (50 - total) * 2 + 30)  # 熊市增强置信度
            
        elif regime == MarketRegime.BULL:
            # 牛市格局，强烈做多信号
            if existing_direction == "SHORT":
                direction = TradeDirection.CLOSE_SHORT
                reason = "牛市信号，平空仓"
            else:
                direction = TradeDirection.LONG
                reason = self._build_long_reason(factors, regime) + " (牛市)"
            confidence = min(100, (total - 50) * 2 + 30)  # 牛市增强置信度
            
        elif total >= self.config.long_threshold:
            # 中性市场，但总分偏高多
            direction = TradeDirection.LONG
            reason = self._build_long_reason(factors, regime)
            confidence = (total - 50) * 2
            
            if existing_direction == "SHORT":
                direction = TradeDirection.CLOSE_SHORT
                reason = "检测到做多信号，平空仓后做多"
                
        elif total <= (100 - self.config.short_threshold):
            # 中性市场，但总分偏低空
            direction = TradeDirection.SHORT
            reason = self._build_short_reason(factors, regime)
            confidence = (50 - total) * 2
            
            if existing_direction == "LONG":
                direction = TradeDirection.CLOSE_LONG
                reason = "检测到做空信号，平多仓后做空"
                
        else:
            direction = TradeDirection.HOLD
            if existing_direction:
                reason = f"信号中性，维持现有{existing_direction}持仓"
            else:
                reason = "信号中性，观望等待机会"
            confidence = 50 - abs(total - 50) * 2
        
        confidence = max(0, min(100, confidence))
        
        return direction, confidence, reason
    
    def _build_long_reason(self, factors: Dict, regime: MarketRegime) -> str:
        """构建做多原因"""
        reasons = []
        if factors.get("trend", 50) > 60:
            reasons.append("趋势向上")
        if factors.get("momentum", 50) > 60:
            reasons.append("动量增强")
        if regime == MarketRegime.BULL:
            reasons.append("牛市格局")
        if factors.get("structure", 50) > 60:
            reasons.append("结构支撑")
        return " + ".join(reasons) if reasons else "综合评分偏多"
    
    def _build_short_reason(self, factors: Dict, regime: MarketRegime) -> str:
        """构建做空原因"""
        reasons = []
        if factors.get("trend", 50) < 40:
            reasons.append("趋势向下")
        if factors.get("momentum", 50) < 40:
            reasons.append("动量减弱")
        if regime == MarketRegime.BEAR:
            reasons.append("熊市格局")
        if factors.get("structure", 50) < 40:
            reasons.append("结构压力")
        return " + ".join(reasons) if reasons else "综合评分偏空"
    
    def _calculate_urgency(self, confidence: float, factors: Dict[str, float]) -> str:
        """计算紧急程度"""
        if confidence >= 85:
            return "high"
        elif confidence >= 70:
            return "normal"
        return "low"
    
    def _is_in_cooldown(self, symbol: str, direction: TradeDirection) -> bool:
        """检查是否在冷却期"""
        if symbol not in self.last_switch_time:
            return False
        
        last = self.last_switch_time[symbol]
        elapsed = (datetime.utcnow() - last).total_seconds() / 60
        
        if elapsed < self.config.direction_switch_cooldown_minutes:
            return True
        
        # 记录切换时间
        self.last_switch_time[symbol] = datetime.utcnow()
        return False
    
    def _get_existing_position_direction(self, symbol: str) -> Optional[str]:
        """获取现有持仓方向"""
        try:
            from app.core.sim_engine import get_sim_engine
            engine = get_sim_engine()
            if symbol in engine.positions:
                pos = engine.positions[symbol]
                return pos.side.lower()  # "long" or "short"
        except Exception:
            pass
        return None
    
    def get_position_size(self, signal: TradingSignal, total_capital: float) -> float:
        """计算仓位大小"""
        base_size = total_capital * (self.config.default_position_pct / 100)
        
        # 根据置信度调整
        if signal.confidence >= self.config.min_confidence_for_full:
            size = base_size * 1.5
        elif signal.confidence >= 70:
            size = base_size * 1.0
        else:
            size = base_size * 0.5
        
        # 最大仓位限制
        max_size = total_capital * (self.config.max_position_pct / 100)
        return min(size, max_size)
    
    def get_stop_loss_take_profit(
        self, signal: TradingSignal, entry_price: float
    ) -> Tuple[float, float]:
        """计算止损止盈"""
        if signal.direction == TradeDirection.LONG:
            stop_loss = entry_price * (1 - self.config.stop_loss_pct / 100)
            take_profit = entry_price * (1 + self.config.take_profit_pct / 100)
        elif signal.direction == TradeDirection.SHORT:
            stop_loss = entry_price * (1 + self.config.stop_loss_pct / 100)
            take_profit = entry_price * (1 - self.config.take_profit_pct / 100)
        else:
            stop_loss = entry_price * 0.95
            take_profit = entry_price * 1.05
        
        return stop_loss, take_profit


# ─── 全局实例 ─────────────────────────────────────────────

_ai_trader: AITrader = None

def get_ai_trader() -> AITrader:
    """获取AI交易器单例"""
    global _ai_trader
    if _ai_trader is None:
        _ai_trader = AITrader()
    return _ai_trader
