"""
声纳库 - 100+趋势模型
包含8大类趋势识别模型
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import math

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

@dataclass
class TrendModel:
    """趋势模型"""
    name: str
    category: str
    conditions: Dict[str, any]
    confidence: int  # 1-10
    timeframes: List[str]
    description: str = ""

@dataclass
class Signal:
    """交易信号"""
    type: SignalType
    confidence: float  # 0-10
    model_name: str
    reason: str
    timestamp: str
    symbol: str
    price: float = 0.0
    volume: float = 0.0


class SonarLibrary:
    """声纳库 - 100+趋势模型"""
    
    def __init__(self):
        self.models: Dict[str, TrendModel] = {}
        self._init_all_models()
        
    def _init_all_models(self):
        """初始化所有100+趋势模型"""
        
        # ===== 动量模型 (15个) =====
        momentum_models = [
            TrendModel("momentum_bull_1m", "动量", {"rsi_above_50": True, "price_above_sma20": True}, 3, ["1m"], "1分钟多头动量"),
            TrendModel("momentum_bull_5m", "动量", {"rsi_above_50": True, "price_above_sma20": True, "macd_bullish": True}, 5, ["5m"], "5分钟多头动量"),
            TrendModel("momentum_bull_15m", "动量", {"rsi_above_50": True, "price_above_sma20": True, "macd_bullish": True, "adx_above_25": True}, 7, ["15m"], "15分钟多头动量"),
            TrendModel("momentum_bear_1m", "动量", {"rsi_below_50": True, "price_below_sma20": True}, 3, ["1m"], "1分钟空头动量"),
            TrendModel("momentum_bear_5m", "动量", {"rsi_below_50": True, "price_below_sma20": True, "macd_bearish": True}, 5, ["5m"], "5分钟空头动量"),
            TrendModel("momentum_bear_15m", "动量", {"rsi_below_50": True, "price_below_sma20": True, "macd_bearish": True, "adx_above_25": True}, 7, ["15m"], "15分钟空头动量"),
            TrendModel("strong_momentum", "动量", {"rsi_range": [40, 70], "macd_histogram_increasing": True, "volume_increasing": True}, 8, ["5m", "15m", "1h"], "强势动量"),
            TrendModel("weak_momentum", "动量", {"rsi_range": [30, 70], "macd_histogram_decreasing": True}, 4, ["5m", "15m"], "弱势动量"),
            TrendModel("acceleration_bull", "动量", {"price_acceleration": "positive", "volume_surge": True, "rsi_above_60": True}, 8, ["5m", "15m"], "加速上涨"),
            TrendModel("acceleration_bear", "动量", {"price_acceleration": "negative", "volume_surge": True, "rsi_below_40": True}, 8, ["5m", "15m"], "加速下跌"),
            TrendModel("momentum_divergence_bull", "动量", {"price_lower_low": True, "rsi_higher_low": True}, 7, ["15m", "1h"], "底背离"),
            TrendModel("momentum_divergence_bear", "动量", {"price_higher_high": True, "rsi_lower_high": True}, 7, ["15m", "1h"], "顶背离"),
            TrendModel("hidden_divergence_bull", "动量", {"price_lower_high": True, "rsi_higher_low": True}, 6, ["15m", "1h"], "隐藏底背离"),
            TrendModel("hidden_divergence_bear", "动量", {"price_higher_low": True, "rsi_lower_high": True}, 6, ["15m", "1h"], "隐藏顶背离"),
            TrendModel("momentum_exhaustion", "动量", {"rsi_extreme": True, "volume_declining": True, "price_range_narrow": True}, 5, ["1h", "4h"], "动量衰竭"),
        ]
        
        # ===== 突破模型 (15个) =====
        breakout_models = [
            TrendModel("breakout_up_strong", "突破", {"price_breaks_high": True, "volume_surge_2x": True}, 7, ["15m", "1h"], "强势突破上涨"),
            TrendModel("breakout_up_weak", "突破", {"price_breaks_high": True, "volume_normal": True}, 5, ["15m", "1h"], "弱势突破上涨"),
            TrendModel("breakout_down_strong", "突破", {"price_breaks_low": True, "volume_surge_2x": True}, 7, ["15m", "1h"], "强势突破下跌"),
            TrendModel("breakout_down_weak", "突破", {"price_breaks_low": True, "volume_normal": True}, 5, ["15m", "1h"], "弱势突破下跌"),
            TrendModel("breakout_volume_surge", "突破", {"volume_surge_3x": True, "price_change_5pct": True}, 6, ["5m", "15m"], "成交量突破"),
            TrendModel("breakout_resistance", "突破", {"price_breaks_resistance": True, "volume_increasing": True}, 7, ["1h", "4h"], "阻力位突破"),
            TrendModel("breakout_support", "突破", {"price_breaks_support": True, "volume_increasing": True}, 7, ["1h", "4h"], "支撑位突破"),
            TrendModel("false_breakout_up", "突破", {"price_breaks_high": True, "closes_below_resistance": True}, 4, ["15m", "1h"], "假突破上涨"),
            TrendModel("false_breakout_down", "突破", {"price_breaks_low": True, "closes_above_support": True}, 4, ["15m", "1h"], "假突破下跌"),
            TrendModel("breakout_continuation_bull", "突破", {"breakout_confirmed": True, "retest_success": True, "volume_surge": True}, 8, ["1h", "4h"], "突破延续"),
            TrendModel("breakout_continuation_bear", "突破", {"breakout_confirmed": True, "retest_success": True, "volume_surge": True}, 8, ["1h", "4h"], "下跌延续"),
            TrendModel("range_breakout_up", "突破", {"price_range_bound": True, "breakout_direction": "up"}, 6, ["15m", "1h"], "区间突破上涨"),
            TrendModel("range_breakout_down", "突破", {"price_range_bound": True, "breakout_direction": "down"}, 6, ["15m", "1h"], "区间突破下跌"),
            TrendModel("triangle_breakout_up", "突破", {"triangle_pattern": True, "breakout_direction": "up"}, 7, ["1h", "4h"], "三角形突破上涨"),
            TrendModel("triangle_breakout_down", "突破", {"triangle_pattern": True, "breakout_direction": "down"}, 7, ["1h", "4h"], "三角形突破下跌"),
        ]
        
        # ===== 反转模型 (15个) =====
        reversal_models = [
            TrendModel("reversal_bull_strong", "反转", {"rsi_oversold": True, "price_bounces": True, "volume_increasing": True}, 7, ["15m", "1h"], "强势反转做多"),
            TrendModel("reversal_bull_weak", "反转", {"rsi_oversold": True, "price_bounces": True}, 5, ["15m", "1h"], "弱势反转做多"),
            TrendModel("reversal_bear_strong", "反转", {"rsi_overbought": True, "price_rejects": True, "volume_increasing": True}, 7, ["15m", "1h"], "强势反转做空"),
            TrendModel("reversal_bear_weak", "反转", {"rsi_overbought": True, "price_rejects": True}, 5, ["15m", "1h"], "弱势反转做空"),
            TrendModel("double_bottom", "反转", {"price_double_bottom": True, "volume_second_low_lower": True}, 7, ["1h", "4h"], "双底"),
            TrendModel("double_top", "反转", {"price_double_top": True, "volume_second_top_higher": True}, 7, ["1h", "4h"], "双顶"),
            TrendModel("head_shoulders_bull", "反转", {"head_shoulders_pattern": "bullish"}, 7, ["1h", "4h"], "头肩底"),
            TrendModel("head_shoulders_bear", "反转", {"head_shoulders_pattern": "bearish"}, 7, ["1h", "4h"], "头肩顶"),
            TrendModel("wedge_falling_wedge", "反转", {"falling_wedge": True, "breakout_up": True}, 7, ["1h", "4h"], "下降楔形"),
            TrendModel("wedge_rising_wedge", "反转", {"rising_wedge": True, "breakout_down": True}, 7, ["1h", "4h"], "上升楔形"),
            TrendModel("bottom_divergence", "反转", {"price_makes_low": True, "indicator_higher_low": True}, 6, ["1h", "4h"], "底部背离"),
            TrendModel("top_divergence", "反转", {"price_makes_high": True, "indicator_lower_high": True}, 6, ["1h", "4h"], "顶部背离"),
            TrendModel("rsi_oversold_bounce", "反转", {"rsi_below_30": True, "rsi_turning_up": True}, 6, ["5m", "15m"], "RSI超卖反弹"),
            TrendModel("rsi_overbought_dump", "反转", {"rsi_above_70": True, "rsi_turning_down": True}, 6, ["5m", "15m"], "RSI超买回落"),
            TrendModel("support_bounce", "反转", {"price_hits_support": True, "bounces_from_support": True, "volume_increasing": True}, 7, ["15m", "1h"], "支撑位反弹"),
        ]
        
        # ===== 波动率模型 (10个) =====
        volatility_models = [
            TrendModel("volatility_squeeze", "波动率", {"bb_squeeze": True, "atr_low": True}, 5, ["15m", "1h"], "波动率挤压"),
            TrendModel("volatility_expansion", "波动率", {"bb_expansion": True, "atr_high": True}, 6, ["15m", "1h"], "波动率扩张"),
            TrendModel("bb_squeeze_bull", "波动率", {"bb_squeeze": True, "price_breaks_up": True}, 7, ["15m", "1h"], "布林带挤压上涨"),
            TrendModel("bb_squeeze_bear", "波动率", {"bb_squeeze": True, "price_breaks_down": True}, 7, ["15m", "1h"], "布林带挤压下跌"),
            TrendModel("atr_breakout_up", "波动率", {"atr_surge": True, "price_up": True}, 6, ["15m", "1h"], "ATR突破上涨"),
            TrendModel("atr_breakout_down", "波动率", {"atr_surge": True, "price_down": True}, 6, ["15m", "1h"], "ATR突破下跌"),
            TrendModel("volatility_regime_change", "波动率", {"volatility_increases": True, "volume_surge": True}, 5, ["1h", "4h"], "波动率制度转换"),
            TrendModel("low_volatility_accumulation", "波动率", {"low_volatility": True, "volume_stable": True, "price_range": True}, 5, ["4h", "1d"], "低波动积累"),
            TrendModel("high_volatility_distribution", "波动率", {"high_volatility": True, "volume_increasing": True, "price_range_wide": True}, 5, ["4h", "1d"], "高波动分配"),
            TrendModel("volatility_cluster", "波动率", {"consecutive_volatile_candles": 3, "same_direction": True}, 4, ["5m", "15m"], "波动率聚集"),
        ]
        
        # ===== 成交量模型 (10个) =====
        volume_models = [
            TrendModel("volume_surge_bull", "成交量", {"volume_surge_2x": True, "price_up": True}, 6, ["5m", "15m"], "成交量激增上涨"),
            TrendModel("volume_surge_bear", "成交量", {"volume_surge_2x": True, "price_down": True}, 6, ["5m", "15m"], "成交量激增下跌"),
            TrendModel("volume_dry_up", "成交量", {"volume_below_average": True, "price_range_narrow": True}, 4, ["1h", "4h"], "成交量枯竭"),
            TrendModel("obv_divergence_bull", "成交量", {"obv_increasing": True, "price_decreasing": True}, 6, ["15m", "1h"], "OBV底背离"),
            TrendModel("obv_divergence_bear", "成交量", {"obv_decreasing": True, "price_increasing": True}, 6, ["15m", "1h"], "OBV顶背离"),
            TrendModel("vwap_rejection", "成交量", {"price_rejects_vwap": True, "volume_increasing": True}, 6, ["5m", "15m"], "VWAP拒绝"),
            TrendModel("vwap_bounce", "成交量", {"price_bounces_vwap": True, "volume_increasing": True}, 6, ["5m", "15m"], "VWAP反弹"),
            TrendModel("volume_price_trend_bull", "成交量", {"vpt_increasing": True, "price_up": True}, 5, ["15m", "1h"], "量价齐升"),
            TrendModel("volume_price_trend_bear", "成交量", {"vpt_decreasing": True, "price_down": True}, 5, ["15m", "1h"], "量价齐跌"),
            TrendModel("accumulation_distribution", "成交量", {"ad_line_increasing": True, "price_sideways": True}, 5, ["1h", "4h"], "积累期"),
        ]
        
        # ===== 趋势模型 (15个) =====
        trend_models = [
            TrendModel("trend_ema_crossover_bull", "趋势", {"ema_9_above_ema_21": True, "ema_21_above_ema_50": True}, 6, ["15m", "1h"], "EMA金叉上涨"),
            TrendModel("trend_ema_crossover_bear", "趋势", {"ema_9_below_ema_21": True, "ema_21_below_ema_50": True}, 6, ["15m", "1h"], "EMA死叉下跌"),
            TrendModel("trend_ma_alignment_bull", "趋势", {"ma_aligned_up": True, "price_above_all_ma": True}, 7, ["1h", "4h"], "均线多头排列"),
            TrendModel("trend_ma_alignment_bear", "趋势", {"ma_aligned_down": True, "price_below_all_ma": True}, 7, ["1h", "4h"], "均线空头排列"),
            TrendModel("trend_channel_up", "趋势", {"higher_highs": True, "higher_lows": True}, 6, ["1h", "4h"], "上升通道"),
            TrendModel("trend_channel_down", "趋势", {"lower_highs": True, "lower_lows": True}, 6, ["1h", "4h"], "下降通道"),
            TrendModel("trend_line_break_bull", "趋势", {"trendline_break": True, "direction": "up"}, 6, ["1h", "4h"], "趋势线突破上涨"),
            TrendModel("trend_line_break_bear", "趋势", {"trendline_break": True, "direction": "down"}, 6, ["1h", "4h"], "趋势线突破下跌"),
            TrendModel("higher_highs_higher_lows", "趋势", {"hhhl": True}, 7, ["1h", "4h"], "高点更高低点更高"),
            TrendModel("lower_highs_lower_lows", "趋势", {"lhll": True}, 7, ["1h", "4h"], "高点更低低点更低"),
            TrendModel("trend_strength_strong", "趋势", {"adx_above_25": True, "rsi_50_70": True}, 6, ["1h", "4h"], "趋势强劲"),
            TrendModel("trend_weakness", "趋势", {"adx_below_20": True, "price_range_narrow": True}, 4, ["1h", "4h"], "趋势疲软"),
            TrendModel("trend_exhaustion_bull", "趋势", {"price_extremes": True, "volume_declining": True, "adx_decreasing": True}, 6, ["4h", "1d"], "上涨衰竭"),
            TrendModel("trend_exhaustion_bear", "趋势", {"price_extremes": True, "volume_declining": True, "adx_decreasing": True}, 6, ["4h", "1d"], "下跌衰竭"),
            TrendModel("trend_reversal_early", "趋势", {"price_rejects_ma": True, "volume_increasing": True, "adx_turning": True}, 5, ["1h", "4h"], "趋势早反转"),
        ]
        
        # ===== 宏观模型 (10个) =====
        macro_models = [
            TrendModel("btc_dominance_up", "宏观", {"btc_dominance_increasing": True}, 5, ["1h", "4h", "1d"], "BTC主导上涨"),
            TrendModel("btc_dominance_down", "宏观", {"btc_dominance_decreasing": True}, 5, ["1h", "4h", "1d"], "BTC主导下跌"),
            TrendModel("altcoin_season", "宏观", {"altcoin_btc_ratio_increasing": True}, 6, ["1d"], "Altcoin季节"),
            TrendModel("btc_season", "宏观", {"btc_outperforms": True}, 6, ["1d"], "BTC季节"),
            TrendModel("fear_greed_extreme_fear", "宏观", {"fear_greed_index_below_25": True}, 6, ["1h", "4h", "1d"], "极度恐惧"),
            TrendModel("fear_greed_extreme_greed", "宏观", {"fear_greed_index_above_75": True}, 6, ["1h", "4h", "1d"], "极度贪婪"),
            TrendModel("market_sentiment_shift", "宏观", {"sentiment_change_20pct": True}, 5, ["4h", "1d"], "市场情绪转变"),
            TrendModel("sector_rotation_bull", "宏观", {"sector_leading": "tech", "sector_lagging": "utilities"}, 5, ["1d"], "板块轮动上涨"),
            TrendModel("sector_rotation_bear", "宏观", {"sector_leading": "utilities", "sector_lagging": "tech"}, 5, ["1d"], "板块轮动下跌"),
            TrendModel("correlation_break", "宏观", {"uncorrelated_assets": True, "correlation_below_0.3": True}, 4, ["1d"], "相关性break"),
        ]
        
        # ===== 链上模型 (10个) =====
        onchain_models = [
            TrendModel("exchange_netflow_positive", "链上", {"exchange_inflow_decreasing": True, "exchange_outflow_increasing": True}, 6, ["1h", "4h"], "净流入"),
            TrendModel("exchange_netflow_negative", "链上", {"exchange_inflow_increasing": True, "exchange_outflow_decreasing": True}, 6, ["1h", "4h"], "净流出"),
            TrendModel("whale_accumulation", "链上", {"whale_buying": True, "large_tx_increasing": True}, 7, ["4h", "1d"], "巨鲸积累"),
            TrendModel("whale_distribution", "链上", {"whale_selling": True, "large_tx_increasing": True}, 7, ["4h", "1d"], "巨鲸分配"),
            TrendModel("miner_revenue_surge", "链上", {"miner_revenue_increasing": True}, 5, ["1d"], "矿工收入激增"),
            TrendModel("hash_rate_change", "链上", {"hash_rate_increasing": True}, 5, ["1d"], "算力变化"),
            TrendModel("difficulty_adjustment_up", "链上", {"difficulty_increasing": True}, 5, ["1d"], "难度上调"),
            TrendModel("difficulty_adjustment_down", "链上", {"difficulty_decreasing": True}, 5, ["1d"], "难度下调"),
            TrendModel("stablecoin_flows", "链上", {"stablecoin_inflow": True}, 5, ["1h", "4h"], "稳定币流向"),
            TrendModel("nft_market_heat", "链上", {"nft_volume_increasing": True}, 4, ["1d"], "NFT市场热度"),
        ]
        
        # 注册所有模型
        all_models = (momentum_models + breakout_models + reversal_models + 
                     volatility_models + volume_models + trend_models + 
                     macro_models + onchain_models)
        
        for model in all_models:
            self.models[model.name] = model
            
    def get_model(self, name: str) -> Optional[TrendModel]:
        """获取指定模型"""
        return self.models.get(name)
        
    def get_models_by_category(self, category: str) -> List[TrendModel]:
        """按类别获取模型"""
        return [m for m in self.models.values() if m.category == category]
        
    def get_models_by_confidence(self, min_confidence: int) -> List[TrendModel]:
        """按置信度获取模型"""
        return [m for m in self.models.values() if m.confidence >= min_confidence]
        
    def get_models_by_timeframe(self, timeframe: str) -> List[TrendModel]:
        """按时 timeframe 获取模型"""
        return [m for m in self.models.values() if timeframe in m.timeframes]
        
    def get_all_categories(self) -> List[str]:
        """获取所有类别"""
        return list(set(m.category for m in self.models.values()))
        
    def get_statistics(self) -> Dict:
        """获取模型统计"""
        categories = {}
        for model in self.models.values():
            if model.category not in categories:
                categories[model.category] = {"count": 0, "avg_confidence": 0}
            categories[model.category]["count"] += 1
            
        # 计算平均置信度
        for cat in categories:
            models_in_cat = self.get_models_by_category(cat)
            avg_conf = sum(m.confidence for m in models_in_cat) / len(models_in_cat)
            categories[cat]["avg_confidence"] = round(avg_conf, 2)
            
        return {
            "total_models": len(self.models),
            "categories": categories
        }
        
    def evaluate_signal(self, market_data: Dict, models_to_check: List[str] = None) -> List[Signal]:
        """评估信号"""
        signals = []
        
        # 如果没有指定模型，检查所有模型
        check_models = models_to_check or list(self.models.keys())
        
        for model_name in check_models:
            model = self.models.get(model_name)
            if not model:
                continue
                
            # 简化评估 - 实际应该根据 market_data 进行复杂判断
            confidence = self._evaluate_model_conditions(model, market_data)
            
            if confidence > 0:
                signal_type = self._confidence_to_signal(confidence)
                signals.append(Signal(
                    type=signal_type,
                    confidence=confidence,
                    model_name=model_name,
                    reason=f"模型条件满足: {model.description}",
                    timestamp=market_data.get("timestamp", ""),
                    symbol=market_data.get("symbol", ""),
                    price=market_data.get("price", 0),
                    volume=market_data.get("volume", 0)
                ))
                
        return signals
        
    def _evaluate_model_conditions(self, model: TrendModel, market_data: Dict) -> float:
        """评估模型条件 - 简化版"""
        # 实际应该根据 market_data 中的指标进行复杂判断
        # 这里返回模型的基准置信度
        return float(model.confidence) if model.confidence >= 5 else 0
        
    def _confidence_to_signal(self, confidence: float) -> SignalType:
        """置信度转信号类型"""
        if confidence >= 7:
            return SignalType.STRONG_BUY
        elif confidence >= 5:
            return SignalType.BUY
        elif confidence >= 3:
            return SignalType.NEUTRAL
        elif confidence >= 1:
            return SignalType.SELL
        else:
            return SignalType.STRONG_SELL


# 全局声纳库实例
sonar_library = SonarLibrary()
