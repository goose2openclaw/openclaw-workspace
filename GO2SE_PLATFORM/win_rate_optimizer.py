#!/usr/bin/env python3
"""
🪿 GO2SE 胜率优化引擎 V1
=========================
目标: 将胜率从 55% 提升到 65-70%

核心策略:
1. 多周期共振过滤
2. RSI背离确认
3. 成交量验证
4. 波动率过滤
5. 跨市场验证
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger("win_rate_optimizer")

# ============================================================================
# 配置
# ============================================================================

class WinRateConfig:
    """胜率优化配置"""
    
    # 多周期共振
    CONFLUENCE_PERIODS = ["1h", "4h", "1d"]  # 需要同时确认的周期
    MIN_CONFLUENCE_SCORE = 0.6  # 最低共振分数
    
    # RSI设置
    RSI_PERIOD = 14
    RSI_OVERSOLD = 35
    RSI_OVERBOUGHT = 65
    RSI_DIVERGENCE_LOOKBACK = 20
    
    # 成交量设置
    VOLUME_SURGE_MULTIPLIER = 1.5  # 放量倍数
    VOLUME_LOOKBACK = 20
    
    # 波动率过滤
    HIGH_VOLATILITY_THRESHOLD = 25  # VIX等效
    REDUCE_POSITION_ON_VOLATILITY = 0.5  # 高波动时减仓比例
    
    # 跨市场验证
    BTC_ETH_CORRELATION_MIN = 0.5  # 最低相关性
    
    # 止损止盈
    STOP_LOSS_ATR_MULTIPLIER = 2.0
    TAKE_PROFIT_RATIOS = [(1.5, 0.5), (3.0, 0.5)]  # (R倍数, 仓位比例)
    
    # 入场信号
    MIN_SIGNAL_CONFIDENCE = 0.65  # 最低信号置信度
    MIN_POSITIVE_CONFLUENCE = 2  # 最少正向共振周期数


@dataclass
class MarketData:
    """市场数据"""
    symbol: str
    price: float
    rsi: float
    volume: float
    volume_ma: float
    atr: float
    trend_score: Dict[str, float]  # per period
    
    
@dataclass
class Signal:
    """交易信号"""
    tool_id: str
    symbol: str
    direction: str  # long/short
    confidence: float
    entry_price: float
    stop_loss: float
    take_profit: float
    position_size: float
    reasons: List[str]
    confluence_score: float
    timestamp: str


@dataclass
class BacktestResult:
    """回测结果"""
    total_trades: int
    wins: int
    losses: int
    win_rate: float
    avg_win: float
    avg_loss: float
    profit_factor: float
    max_drawdown: float
    sharpe_ratio: float


class ConfluenceFilter:
    """多周期共振过滤器"""
    
    def __init__(self, config: WinRateConfig):
        self.config = config
        
    def check_confluence(self, market_data: Dict[str, MarketData]) -> Tuple[bool, float, List[str]]:
        """
        检查多周期共振
        
        Returns:
            (is_valid, score, reasons)
        """
        if not market_data:
            return False, 0.0, ["No market data"]
        
        positive_periods = 0
        total_score = 0.0
        reasons = []
        
        for period, data in market_data.items():
            if data.trend_score.get(period, 0) > self.config.MIN_CONFLUENCE_SCORE:
                positive_periods += 1
                total_score += data.trend_score[period]
                reasons.append(f"  {period}: {data.trend_score[period]:.2%} ✅")
            else:
                reasons.append(f"  {period}: {data.trend_score.get(period, 0):.2%} ❌")
        
        avg_score = total_score / len(market_data) if market_data else 0
        is_valid = positive_periods >= self.config.MIN_POSITIVE_CONFLUENCE
        
        return is_valid, avg_score, reasons


class RSIFilter:
    """RSI过滤器 - 识别背离"""
    
    def __init__(self, config: WinRateConfig):
        self.config = config
    
    def check_rsi_conditions(self, current_rsi: float, price_history: List[float], 
                             rsi_history: List[float]) -> Tuple[bool, str]:
        """
        检查RSI条件
        
        Returns:
            (is_valid, reason)
        """
        # 超卖反弹 (买入信号)
        if current_rsi < self.config.RSI_OVERSOLD:
            # 检查底背离
            if self._check_bullish_divergence(price_history, rsi_history):
                return True, f"RSI超卖 + 底背离 ({current_rsi:.1f})"
            return True, f"RSI超卖 ({current_rsi:.1f})"
        
        # 超买回落 (卖出信号)
        if current_rsi > self.config.RSI_OVERBOUGHT:
            # 检查顶背离
            if self._check_bearish_divergence(price_history, rsi_history):
                return True, f"RSI超买 + 顶背离 ({current_rsi:.1f})"
            return True, f"RSI超买 ({current_rsi:.1f})"
        
        return False, f"RSI中性 ({current_rsi:.1f})"
    
    def _check_bullish_divergence(self, prices: List[float], rsi_values: List[float]) -> bool:
        """检查看涨底背离: 价格新低但RSI未新低"""
        if len(prices) < self.config.RSI_DIVERGENCE_LOOKBACK or len(rsi_values) < self.config.RSI_DIVERGENCE_LOOKBACK:
            return False
        
        recent_prices = prices[-self.config.RSI_DIVERGENCE_LOOKBACK:]
        recent_rsi = rsi_values[-self.config.RSI_DIVERGENCE_LOOKBACK:]
        
        price_low_idx = recent_prices.index(min(recent_prices))
        rsi_low_idx = recent_rsi.index(min(recent_rsi))
        
        # 价格创新低但RSI没有创新低 = 底背离
        return price_low_idx > rsi_low_idx and min(recent_prices) < prices[0]
    
    def _check_bearish_divergence(self, prices: List[float], rsi_values: List[float]) -> bool:
        """检查看跌顶背离: 价格新高但RSI未新高"""
        if len(prices) < self.config.RSI_DIVERGENCE_LOOKBACK or len(rsi_values) < self.config.RSI_DIVERGENCE_LOOKBACK:
            return False
        
        recent_prices = prices[-self.config.RSI_DIVERGENCE_LOOKBACK:]
        recent_rsi = rsi_values[-self.config.RSI_DIVERGENCE_LOOKBACK:]
        
        price_high_idx = recent_prices.index(max(recent_prices))
        rsi_high_idx = recent_rsi.index(max(recent_rsi))
        
        # 价格创新高但RSI没有创新高 = 顶背离
        return price_high_idx > rsi_high_idx and max(recent_prices) > prices[0]


class VolumeFilter:
    """成交量过滤器"""
    
    def __init__(self, config: WinRateConfig):
        self.config = config
    
    def check_volume_confirmation(self, current_volume: float, 
                                  volume_ma: float) -> Tuple[bool, str]:
        """
        检查成交量确认
        
        Returns:
            (is_valid, reason)
        """
        if current_volume >= volume_ma * self.config.VOLUME_SURGE_MULTIPLIER:
            surge_ratio = current_volume / volume_ma if volume_ma > 0 else 0
            return True, f"放量确认 ({surge_ratio:.1f}x)"
        
        return False, f"量能不足 ({current_volume/volume_ma if volume_ma > 0 else 0:.1f}x)"


class VolatilityFilter:
    """波动率过滤器"""
    
    def __init__(self, config: WinRateConfig):
        self.config = config
    
    def get_position_adjustment(self, atr: float, current_price: float,
                                market_volatility: float) -> Tuple[float, str]:
        """
        根据波动率调整仓位
        
        Returns:
            (position_multiplier, reason)
        """
        if market_volatility > self.config.HIGH_VOLATILITY_THRESHOLD:
            return self.config.REDUCE_POSITION_ON_VOLATILITY, \
                   f"高波动减仓 ({market_volatility:.1f})"
        
        return 1.0, f"正常仓位 ({market_volatility:.1f})"


class CrossMarketValidator:
    """跨市场验证"""
    
    def __init__(self, config: WinRateConfig):
        self.config = config
    
    def validate_signal(self, primary_signal: Dict, 
                       correlation_assets: Dict) -> Tuple[bool, str]:
        """
        验证跨市场信号一致性
        
        Returns:
            (is_valid, reason)
        """
        primary_direction = primary_signal.get("direction")
        
        # 检查相关资产方向
        mismatches = 0
        for asset, data in correlation_assets.items():
            if data.get("direction") != primary_direction:
                mismatches += 1
        
        mismatch_ratio = mismatches / len(correlation_assets) if correlation_assets else 1
        
        if mismatch_ratio > 0.5:
            return False, f"跨市场背离 ({mismatch_ratio:.0%}不一致)"
        
        return True, f"跨市场一致 ✅"


class KellyCriterion:
    """凯利公式仓位计算"""
    
    def __init__(self):
        pass
    
    def calculate_position(self, win_rate: float, avg_win: float, 
                          avg_loss: float, max_position: float = 0.1) -> float:
        """
        凯利公式: f = (bp - q) / b
        
        其中:
        - b = 赔率 (avg_win / avg_loss)
        - p = 胜率
        - q = 1 - p
        
        Returns:
            建议仓位比例
        """
        if avg_loss == 0:
            return 0
        
        b = avg_win / avg_loss  # 赔率
        p = win_rate  # 胜率
        q = 1 - p  # 败率
        
        # 凯利公式
        f = (b * p - q) / b
        
        # 半凯利 (保守)
        f = f / 2
        
        # 限制最大仓位
        return min(f, max_position)


class WinRateOptimizer:
    """胜率优化引擎"""
    
    def __init__(self):
        self.config = WinRateConfig()
        self.confluence_filter = ConfluenceFilter(self.config)
        self.rsi_filter = RSIFilter(self.config)
        self.volume_filter = VolumeFilter(self.config)
        self.volatility_filter = VolatilityFilter(self.config)
        self.cross_market_validator = CrossMarketValidator(self.config)
        self.kelly = KellyCriterion()
        
    def generate_signal(self, market_data: Dict[str, MarketData],
                       btc_correlation: Optional[Dict] = None,
                       historical_prices: Optional[Dict] = None,
                       historical_rsi: Optional[Dict] = None) -> Optional[Signal]:
        """
        生成优化后的交易信号
        
        Args:
            market_data: 各周期市场数据
            btc_correlation: BTC相关资产数据
            historical_prices: 价格历史
            historical_rsi: RSI历史
        """
        signal_reasons = []
        
        # =====================================================================
        # 过滤器 1: 多周期共振
        # =====================================================================
        confluence_valid, confluence_score, confluence_reasons = \
            self.confluence_filter.check_confluence(market_data)
        signal_reasons.extend(confluence_reasons)
        
        if not confluence_valid:
            logger.info(f"信号被过滤: 多周期共振不足 (score={confluence_score:.2%})")
            return None
        
        # =====================================================================
        # 过滤器 2: RSI条件
        # =====================================================================
        primary_data = list(market_data.values())[0]
        rsi_valid, rsi_reason = self.rsi_filter.check_rsi_conditions(
            primary_data.rsi,
            historical_prices.get("prices", []) if historical_prices else [],
            historical_rsi.get("rsi", []) if historical_rsi else []
        )
        signal_reasons.append(f"  RSI: {rsi_reason}")
        
        # RSI条件可选，但会增加置信度
        # 暂不强制过滤
        
        # =====================================================================
        # 过滤器 3: 成交量确认
        # =====================================================================
        volume_valid, volume_reason = self.volume_filter.check_volume_confirmation(
            primary_data.volume,
            primary_data.volume_ma
        )
        signal_reasons.append(f"  Volume: {volume_reason}")
        
        if not volume_valid:
            logger.info(f"信号被过滤: 成交量不足")
            return None
        
        # =====================================================================
        # 过滤器 4: 波动率调整
        # =====================================================================
        volatility_mult, volatility_reason = self.volatility_filter.get_position_adjustment(
            primary_data.atr,
            primary_data.price,
            market_data.get("1h", MarketData("", 0, 0, 0, 0, 0, {})).atr / primary_data.price * 100
        )
        signal_reasons.append(f"  Volatility: {volatility_reason}")
        
        # =====================================================================
        # 过滤器 5: 跨市场验证
        # =====================================================================
        if btc_correlation:
            cross_valid, cross_reason = self.cross_market_validator.validate_signal(
                {"direction": "long" if confluence_score > 0.6 else "short"},
                btc_correlation
            )
            signal_reasons.append(f"  Cross-market: {cross_reason}")
            
            if not cross_valid:
                logger.info(f"信号被过滤: 跨市场背离")
                return None
        
        # =====================================================================
        # 计算信号置信度
        # =====================================================================
        confidence = confluence_score
        
        if volume_valid:
            confidence *= 1.1  # 成交量确认加成
        if rsi_valid:
            confidence *= 1.15  # RSI背离加成
        if volatility_mult == 1.0:
            confidence *= 1.05  # 正常波动加成
            
        confidence = min(confidence, 0.95)  # 最高95%
        
        if confidence < self.config.MIN_SIGNAL_CONFIDENCE:
            logger.info(f"信号被过滤: 置信度不足 ({confidence:.2%})")
            return None
        
        # =====================================================================
        # 计算止损止盈
        # =====================================================================
        atr = primary_data.atr
        entry = primary_data.price
        direction = "long"
        
        stop_loss = entry - atr * self.config.STOP_LOSS_ATR_MULTIPLIER
        take_profit_1 = entry + atr * self.config.TAKE_PROFIT_RATIOS[0][0]
        take_profit_2 = entry + atr * self.config.TAKE_PROFIT_RATIOS[1][0]
        
        # =====================================================================
        # 计算仓位
        # =====================================================================
        position_size = self.kelly.calculate_position(
            win_rate=0.55,  # 预期胜率
            avg_win=atr * self.config.TAKE_PROFIT_RATIOS[0][0],
            avg_loss=atr * self.config.STOP_LOSS_ATR_MULTIPLIER,
            max_position=0.1 * volatility_mult
        )
        
        # =====================================================================
        # 生成信号
        # =====================================================================
        return Signal(
            tool_id="mole",  # 默认使用打地鼠
            symbol="BTC",
            direction=direction,
            confidence=confidence,
            entry_price=entry,
            stop_loss=stop_loss,
            take_profit=take_profit_1,
            position_size=position_size,
            reasons=signal_reasons,
            confluence_score=confluence_score,
            timestamp=datetime.now().isoformat()
        )
    
    def backtest(self, signals: List[Signal], prices: List[float]) -> BacktestResult:
        """
        回测信号表现
        """
        if not signals or len(signals) < 2:
            return BacktestResult(0, 0, 0, 0, 0, 0, 0, 0, 0)
        
        wins = 0
        losses = 0
        total_win_amount = 0
        total_loss_amount = 0
        peak = 0
        max_dd = 0
        returns = []
        
        for i, signal in enumerate(signals[:-1]):
            next_price = prices[i + 1]
            
            if signal.direction == "long":
                pnl = (next_price - signal.entry_price) / signal.entry_price
            else:
                pnl = (signal.entry_price - next_price) / signal.entry_price
            
            returns.append(pnl)
            
            if pnl > 0:
                wins += 1
                total_win_amount += pnl
            else:
                losses += 1
                total_loss_amount += abs(pnl)
            
            # 跟踪净值和回撤
            if i == 0:
                peak = 1 + pnl
            else:
                peak = peak * (1 + pnl)
                dd = (peak - 1) / peak
                max_dd = max(max_dd, dd)
        
        total = wins + losses
        win_rate = wins / total if total > 0 else 0
        avg_win = total_win_amount / wins if wins > 0 else 0
        avg_loss = total_loss_amount / losses if losses > 0 else 0
        profit_factor = (total_win_amount / total_loss_amount) if total_loss_amount > 0 else 0
        
        # 夏普比率
        if len(returns) > 1:
            import statistics
            mean_ret = statistics.mean(returns)
            std_ret = statistics.stdev(returns) if len(returns) > 1 else 0
            sharpe = (mean_ret / std_ret * (252**0.5)) if std_ret > 0 else 0
        else:
            sharpe = 0
        
        return BacktestResult(
            total_trades=total,
            wins=wins,
            losses=losses,
            win_rate=win_rate,
            avg_win=avg_win,
            avg_loss=avg_loss,
            profit_factor=profit_factor,
            max_drawdown=max_dd,
            sharpe_ratio=sharpe
        )


# ============================================================================
# 全局实例
# ============================================================================
win_rate_optimizer = WinRateOptimizer()


# ============================================================================
# API端点
# ============================================================================
def get_optimizer_status() -> Dict:
    """获取优化器状态"""
    return {
        "status": "active",
        "target_win_rate": 0.65,
        "current_filters": [
            "confluence", "rsi", "volume", "volatility", "cross_market"
        ],
        "config": {
            "min_confidence": WinRateConfig.MIN_SIGNAL_CONFIDENCE,
            "min_confluence_periods": WinRateConfig.MIN_POSITIVE_CONFLUENCE,
            "rsi_oversold": WinRateConfig.RSI_OVERSOLD,
            "rsi_overbought": WinRateConfig.RSI_OVERBOUGHT,
            "volume_surge": WinRateConfig.VOLUME_SURGE_MULTIPLIER,
            "stop_loss_atr": WinRateConfig.STOP_LOSS_ATR_MULTIPLIER,
        },
        "timestamp": datetime.now().isoformat()
    }
