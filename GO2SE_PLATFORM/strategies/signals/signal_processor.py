"""
信号处理模块 - 趋势识别/置信度计算/信号聚合
============================================

功能:
1. 趋势识别 - 从123模型中识别趋势
2. 置信度计算 - 多维度置信度评估
3. 信号聚合 - 多模型共识聚合
"""

import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
from collections import Counter, defaultdict
from enum import Enum

# ==================== 信号处理枚举 ====================

class SignalStrength(Enum):
    """信号强度"""
    VERY_WEAK = "VERY_WEAK"     # < 0.2
    WEAK = "WEAK"               # 0.2 - 0.4
    MODERATE = "MODERATE"       # 0.4 - 0.6
    STRONG = "STRONG"           # 0.6 - 0.8
    VERY_STRONG = "VERY_STRONG" # > 0.8

class TrendPhase(Enum):
    """趋势阶段"""
    EARLY = "EARLY"           # 早期
    CONFIRMED = "CONFIRMED"    # 确认
    MATURE = "MATURE"          # 成熟
    EXHAUSTED = "EXHAUSTED"   # 衰竭

@dataclass
class TrendAnalysis:
    """趋势分析结果"""
    symbol: str
    direction: str              # BULL, BEAR, SIDEWAYS
    phase: TrendPhase
    strength: SignalStrength
    confidence: float           # 0-1
    primary_indicators: List[str]
    supporting_indicators: List[str]
    conflicting_indicators: List[str]
    models_count: int
    models_breakdown: Dict[str, int]
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "symbol": self.symbol,
            "direction": self.direction,
            "phase": self.phase.value,
            "strength": self.strength.value,
            "confidence": round(self.confidence, 2),
            "primary_indicators": self.primary_indicators,
            "supporting_indicators": self.supporting_indicators,
            "conflicting_indicators": self.conflicting_indicators,
            "models_count": self.models_count,
            "models_breakdown": self.models_breakdown,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

@dataclass
class ConfidenceScore:
    """置信度评分"""
    overall: float
    directional: float          # 方向置信度
    magnitude: float           # 幅度置信度
    timing: float              # 时机置信度
    consensus: float           # 共识置信度
    factors: Dict[str, float]  # 各因素得分
    warnings: List[str]       # 警告信息
    
    @property
    def strength(self) -> SignalStrength:
        if self.overall < 0.2:
            return SignalStrength.VERY_WEAK
        elif self.overall < 0.4:
            return SignalStrength.WEAK
        elif self.overall < 0.6:
            return SignalStrength.MODERATE
        elif self.overall < 0.8:
            return SignalStrength.STRONG
        else:
            return SignalStrength.VERY_STRONG
    
    def to_dict(self) -> Dict:
        return {
            "overall": round(self.overall, 3),
            "directional": round(self.directional, 3),
            "magnitude": round(self.magnitude, 3),
            "timing": round(self.timing, 3),
            "consensus": round(self.consensus, 3),
            "strength": self.strength.value,
            "factors": {k: round(v, 3) for k, v in self.factors.items()},
            "warnings": self.warnings
        }

# ==================== 趋势识别器 ====================

class TrendIdentifier:
    """趋势识别器"""
    
    # 指标分类
    TREND_INDICATORS = {
        "TREND_EMA", "TREND_MA", "TREND_CHANNEL", "TREND_ICHIMOKU",
        "MOMENTUM_ADX", "SPECIAL_MA_CROSS"
    }
    
    MOMENTUM_INDICATORS = {
        "MOMENTUM_RSI", "MOMENTUM_MACD", "MOMENTUM_STOCHASTIC"
    }
    
    VOLATILITY_INDICATORS = {
        "VOLATILITY_BOLLINGER", "VOLATILITY_ATR", "VOLATILITY_KELTNER"
    }
    
    VOLUME_INDICATORS = {
        "VOLUME_OBV", "VOLUME_VWAP", "VOLUME_VRM"
    }
    
    REVERSAL_INDICATORS = {
        "REVERSAL_CCI", "REVERSAL_WILLIAMS", "REVERSAL_RVI",
        "SPECIAL_RSI_DIV"
    }
    
    CHANNEL_INDICATORS = {
        "CHANNEL_DONCHIAN", "CHANNEL_FIBONACCI", "CHANNEL_PITCHFORK"
    }
    
    @classmethod
    def categorize_indicator(cls, indicator_id: str) -> str:
        """将指标ID分类到对应类别"""
        for category, indicators in [
            ("TREND", cls.TREND_INDICATORS),
            ("MOMENTUM", cls.MOMENTUM_INDICATORS),
            ("VOLATILITY", cls.VOLATILITY_INDICATORS),
            ("VOLUME", cls.VOLUME_INDICATORS),
            ("REVERSAL", cls.REVERSAL_INDICATORS),
            ("CHANNEL", cls.CHANNEL_INDICATORS)
        ]:
            if any(ind in indicator_id for ind in indicators):
                return category
        return "OTHER"
    
    @classmethod
    def identify_trend(cls, signals: List[Dict]) -> TrendAnalysis:
        """
        从信号列表识别趋势
        
        Args:
            signals: 信号列表，每个信号包含:
                - model_id: 模型ID
                - direction: 方向 (BULL/BEAR/SIDEWAYS)
                - confidence: 置信度
                - signal_type: 信号类型
                
        Returns:
            TrendAnalysis: 趋势分析结果
        """
        if not signals:
            return None
        
        symbol = signals[0].get("symbol", "UNKNOWN")
        
        # 统计各方向和类别的信号
        direction_counts = Counter()
        category_counts = Counter()
        indicator_signals = defaultdict(list)
        
        for sig in signals:
            direction = sig.get("direction", "SIDEWAYS")
            direction_counts[direction] += 1
            
            model_id = sig.get("model_id", "")
            category = cls.categorize_indicator(model_id)
            category_counts[category] += 1
            
            indicator_signals[category].append(sig)
        
        # 确定主方向
        primary_direction = direction_counts.most_common(1)[0][0]
        
        # 计算方向一致性
        total_signals = len(signals)
        direction_consistency = direction_counts[primary_direction] / total_signals
        
        # 判断趋势阶段
        if direction_consistency < 0.4:
            phase = TrendPhase.EARLY
        elif direction_consistency < 0.6:
            phase = TrendPhase.CONFIRMED
        elif direction_consistency < 0.8:
            phase = TrendPhase.MATURE
        else:
            phase = TrendPhase.EXHAUSTED
        
        # 区分主要指标和支持指标
        primary_indicators = []
        supporting_indicators = []
        conflicting_indicators = []
        
        for cat, count in category_counts.most_common(3):
            if count >= total_signals * 0.3:
                primary_indicators.append(cat)
            elif count >= total_signals * 0.1:
                supporting_indicators.append(cat)
        
        # 找出冲突指标
        for cat, signals_in_cat in indicator_signals.items():
            if cat not in primary_indicators:
                opposing = [s for s in signals_in_cat if s.get("direction") != primary_direction]
                if opposing:
                    conflicting_indicators.append(cat)
        
        # 计算整体置信度
        confidence = direction_consistency
        
        # 元数据
        metadata = {
            "total_signals": total_signals,
            "direction_distribution": dict(direction_counts),
            "category_distribution": dict(category_counts),
            "direction_consistency": round(direction_consistency, 3)
        }
        
        return TrendAnalysis(
            symbol=symbol,
            direction=primary_direction,
            phase=phase,
            strength=SignalStrength.MODERATE if confidence >= 0.5 else SignalStrength.WEAK,
            confidence=confidence,
            primary_indicators=primary_indicators,
            supporting_indicators=supporting_indicators,
            conflicting_indicators=conflicting_indicators,
            models_count=total_signals,
            models_breakdown=dict(category_counts),
            timestamp=datetime.now().isoformat(),
            metadata=metadata
        )

# ==================== 置信度计算器 ====================

class ConfidenceCalculator:
    """置信度计算器"""
    
    # 权重配置
    WEIGHTS = {
        "model_count": 0.15,        # 模型数量
        "direction_agreement": 0.20,  # 方向一致性
        "signal_strength": 0.15,    # 信号强度
        "timeframe_alignment": 0.15, # 时间框架对齐
        "historical_accuracy": 0.20, # 历史准确率
        "cross_indicator": 0.15     # 交叉验证
    }
    
    @classmethod
    def calculate(cls, signals: List[Dict], indicators_data: Dict = None) -> ConfidenceScore:
        """
        计算综合置信度
        
        Args:
            signals: 信号列表
            indicators_data: 指标数据（用于交叉验证）
            
        Returns:
            ConfidenceScore: 置信度评分
        """
        if not signals:
            return ConfidenceScore(
                overall=0.0,
                directional=0.0,
                magnitude=0.0,
                timing=0.0,
                consensus=0.0,
                factors={},
                warnings=["No signals available"]
            )
        
        factors = {}
        warnings = []
        
        # 1. 模型数量得分
        model_count = len(signals)
        model_count_score = min(1.0, model_count / 10)  # 10个模型以上满分
        factors["model_count"] = model_count_score
        
        # 2. 方向一致性得分
        directions = [s.get("direction", "SIDEWAYS") for s in signals]
        direction_counts = Counter(directions)
        primary_direction_count = direction_counts.most_common(1)[0][1]
        direction_agreement = primary_direction_count / len(directions)
        factors["direction_agreement"] = direction_agreement
        
        if direction_agreement < 0.5:
            warnings.append("Low direction agreement - conflicting signals")
        
        # 3. 信号强度得分
        confidences = [s.get("confidence", 0.5) for s in signals]
        avg_confidence = sum(confidences) / len(confidences)
        factors["signal_strength"] = avg_confidence
        
        if avg_confidence < 0.4:
            warnings.append("Low average signal confidence")
        
        # 4. 时间框架对齐得分
        timeframes = [s.get("timeframe", "1h") for s in signals]
        timeframe_counts = Counter(timeframes)
        primary_tf_count = timeframe_counts.most_common(1)[0][1]
        timeframe_alignment = primary_tf_count / len(timeframes)
        factors["timeframe_alignment"] = timeframe_alignment
        
        # 5. 历史准确率（从信号元数据获取）
        historical_scores = []
        for sig in signals:
            meta = sig.get("metadata", {})
            if "success_rate" in meta:
                historical_scores.append(meta["success_rate"])
        historical_accuracy = sum(historical_scores) / len(historical_scores) if historical_scores else 0.5
        factors["historical_accuracy"] = historical_accuracy
        
        # 6. 交叉验证得分（如果有指标数据）
        cross_indicator_score = 0.5  # 默认
        if indicators_data:
            cross_indicator_score = cls._cross_validate(signals, indicators_data)
        factors["cross_indicator"] = cross_indicator_score
        
        # 计算各维度得分
        directional = direction_agreement * 0.6 + avg_confidence * 0.4
        magnitude = avg_confidence * 0.7 + model_count_score * 0.3
        timing = timeframe_alignment * 0.5 + cross_indicator_score * 0.5
        consensus = direction_agreement
        
        # 综合得分
        overall = sum(factors[k] * v for k, v in cls.WEIGHTS.items())
        
        return ConfidenceScore(
            overall=min(1.0, max(0.0, overall)),
            directional=min(1.0, max(0.0, directional)),
            magnitude=min(1.0, max(0.0, magnitude)),
            timing=min(1.0, max(0.0, timing)),
            consensus=min(1.0, max(0.0, consensus)),
            factors=factors,
            warnings=warnings
        )
    
    @classmethod
    def _cross_validate(cls, signals: List[Dict], indicators_data: Dict) -> float:
        """
        交叉验证 - 检查信号与实际指标是否一致
        
        Returns:
            0-1 之间的验证分数
        """
        validations = []
        
        for sig in signals:
            model_id = sig.get("model_id", "")
            direction = sig.get("direction", "SIDEWAYS")
            
            # 检查EMA是否匹配方向
            if "EMA" in model_id:
                period = "".join(filter(str.isdigit, model_id.split("_")[-1]))
                ema_key = f"EMA_{period}" if period else None
                if ema_key and ema_key in indicators_data:
                    price = indicators_data.get("PRICE", 0)
                    ema_value = indicators_data.get(ema_key, 0)
                    if price > 0 and ema_value > 0:
                        if (direction == "BULL" and price > ema_value) or \
                           (direction == "BEAR" and price < ema_value):
                            validations.append(1.0)
                        else:
                            validations.append(0.5)
            
            # 检查RSI是否匹配
            elif "RSI" in model_id:
                rsi_value = indicators_data.get("RSI_14", 50)
                if (direction == "BULL" and 30 < rsi_value < 70) or \
                   (direction == "BEAR" and (rsi_value < 30 or rsi_value > 70)):
                    validations.append(1.0)
                else:
                    validations.append(0.5)
        
        return sum(validations) / len(validations) if validations else 0.5

# ==================== 信号聚合器 ====================

class SignalAggregator:
    """信号聚合器 - 多模型共识"""
    
    @classmethod
    def aggregate(cls, signals: List[Dict], min_confidence: float = 0.3) -> Dict:
        """
        聚合多个信号
        
        Args:
            signals: 信号列表
            min_confidence: 最低置信度阈值
            
        Returns:
            聚合后的信号
        """
        if not signals:
            return None
        
        # 过滤低置信度信号
        filtered_signals = [s for s in signals if s.get("confidence", 0) >= min_confidence]
        
        if not filtered_signals:
            return None
        
        # 方向投票
        directions = [s.get("direction", "SIDEWAYS") for s in filtered_signals]
        direction_counts = Counter(directions)
        primary_direction = direction_counts.most_common(1)[0][0]
        
        # 置信度加权
        total_confidence = sum(s.get("confidence", 0) for s in filtered_signals)
        avg_confidence = total_confidence / len(filtered_signals)
        
        # 信号类型
        signal_types = [s.get("signal_type", "NEUTRAL") for s in filtered_signals]
        type_counts = Counter(signal_types)
        primary_type = type_counts.most_common(1)[0][0]
        
        # 共识度
        consensus_score = direction_counts[primary_direction] / len(filtered_signals)
        
        # 涉及的模型
        model_ids = list(set(s.get("model_id", "") for s in filtered_signals))
        
        # 按工具分类
        tool_scores = defaultdict(lambda: {"count": 0, "confidence": 0})
        for sig in filtered_signals:
            tool = sig.get("tool_type", "RABBIT")
            tool_scores[tool]["count"] += 1
            tool_scores[tool]["confidence"] += sig.get("confidence", 0)
        
        # 找到最适合的工具
        best_tool = max(tool_scores.items(), key=lambda x: x[1]["count"])
        
        return {
            "symbol": filtered_signals[0].get("symbol", "UNKNOWN"),
            "timestamp": datetime.now().isoformat(),
            
            # 聚合结果
            "direction": primary_direction,
            "signal_type": primary_type,
            "confidence": round(avg_confidence, 3),
            "consensus_score": round(consensus_score, 3),
            
            # 统计
            "signal_count": len(filtered_signals),
            "model_count": len(model_ids),
            "direction_votes": dict(direction_counts),
            "type_votes": dict(type_counts),
            
            # 推荐
            "recommended_tool": best_tool[0],
            "tool_scores": {
                k: {"count": v["count"], "avg_confidence": round(v["confidence"]/v["count"], 3)}
                for k, v in tool_scores.items()
            },
            
            # 元数据
            "metadata": {
                "filtered_from": len(signals),
                "filtered_to": len(filtered_signals),
                "min_confidence_threshold": min_confidence,
                "models": model_ids[:10]  # 最多10个模型ID
            }
        }
    
    @classmethod
    def aggregate_by_timeframe(cls, signals: List[Dict]) -> Dict[str, Dict]:
        """
        按时间框架聚合信号
        
        Returns:
            {timeframe: aggregated_signal}
        """
        timeframe_groups = defaultdict(list)
        
        for sig in signals:
            tf = sig.get("timeframe", "1h")
            timeframe_groups[tf].append(sig)
        
        return {
            tf: cls.aggregate(sigs)
            for tf, sigs in timeframe_groups.items()
            if sigs
        }
    
    @classmethod
    def aggregate_by_category(cls, signals: List[Dict]) -> Dict[str, Dict]:
        """
        按模型类别聚合信号
        
        Returns:
            {category: aggregated_signal}
        """
        def get_category(model_id: str) -> str:
            if "TREND" in model_id:
                return "TREND"
            elif "MOMENTUM" in model_id:
                return "MOMENTUM"
            elif "VOLATILITY" in model_id:
                return "VOLATILITY"
            elif "VOLUME" in model_id:
                return "VOLUME"
            elif "REVERSAL" in model_id:
                return "REVERSAL"
            elif "CHANNEL" in model_id:
                return "CHANNEL"
            else:
                return "OTHER"
        
        category_groups = defaultdict(list)
        
        for sig in signals:
            cat = get_category(sig.get("model_id", ""))
            category_groups[cat].append(sig)
        
        return {
            cat: cls.aggregate(sigs)
            for cat, sigs in category_groups.items()
            if sigs
        }

# ==================== 信号处理器 ====================

class SignalProcessor:
    """信号处理器 - 整合以上功能"""
    
    def __init__(self):
        self.trend_identifier = TrendIdentifier()
        self.confidence_calculator = ConfidenceCalculator()
        self.signal_aggregator = SignalAggregator()
        
        self.processed_signals: List[Dict] = []
        self.history: List[Dict] = []
    
    def process(self, signals: List[Dict], indicators_data: Dict = None) -> Dict:
        """
        完整处理信号
        
        Args:
            signals: 信号列表
            indicators_data: 指标数据（可选）
            
        Returns:
            完整处理结果
        """
        if not signals:
            return {
                "status": "no_signals",
                "timestamp": datetime.now().isoformat()
            }
        
        # 1. 趋势识别
        trend_analysis = self.trend_identifier.identify_trend(signals)
        
        # 2. 置信度计算
        confidence = self.confidence_calculator.calculate(signals, indicators_data)
        
        # 3. 信号聚合
        aggregated = self.signal_aggregator.aggregate(signals)
        
        # 4. 时间框架聚合
        by_timeframe = self.signal_aggregator.aggregate_by_timeframe(signals)
        
        # 5. 类别聚合
        by_category = self.signal_aggregator.aggregate_by_category(signals)
        
        # 组合结果
        result = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            
            # 原始信号统计
            "signal_count": len(signals),
            
            # 趋势分析
            "trend_analysis": trend_analysis.to_dict() if trend_analysis else None,
            
            # 置信度
            "confidence": confidence.to_dict(),
            
            # 聚合结果
            "aggregated": aggregated,
            
            # 分类聚合
            "by_timeframe": by_timeframe,
            "by_category": by_category,
            
            # 建议
            "recommendations": self._generate_recommendations(
                trend_analysis, confidence, aggregated
            )
        }
        
        # 存储历史
        self.processed_signals.append(result)
        self.history.append({
            "timestamp": result["timestamp"],
            "signal_count": len(signals),
            "confidence": confidence.overall,
            "direction": aggregated.get("direction") if aggregated else None
        })
        
        return result
    
    def _generate_recommendations(
        self,
        trend: TrendAnalysis,
        confidence: ConfidenceScore,
        aggregated: Dict
    ) -> Dict:
        """生成建议"""
        recommendations = {
            "action": "HOLD",
            "tool": "RABBIT",
            "position_size": 0,
            "stop_loss": 0,
            "take_profit": 0,
            "reasons": [],
            "warnings": confidence.warnings
        }
        
        if not aggregated:
            return recommendations
        
        direction = aggregated.get("direction", "SIDEWAYS")
        conf = confidence.overall
        
        # 根据置信度和方向生成建议
        if conf >= 0.6:
            if direction == "BULL":
                recommendations["action"] = "BUY"
                recommendations["reasons"].append("High confidence bull signal")
            elif direction == "BEAR":
                recommendations["action"] = "SELL"
                recommendations["reasons"].append("High confidence bear signal")
        elif conf >= 0.4:
            recommendations["action"] = "WATCH"
            recommendations["reasons"].append("Moderate confidence - wait for confirmation")
        else:
            recommendations["action"] = "HOLD"
            recommendations["reasons"].append("Low confidence - no action")
        
        # 推荐工具
        if "recommended_tool" in aggregated:
            recommendations["tool"] = aggregated["recommended_tool"]
        
        # 仓位建议
        if conf >= 0.7:
            recommendations["position_size"] = 25.0
        elif conf >= 0.5:
            recommendations["position_size"] = 15.0
        elif conf >= 0.3:
            recommendations["position_size"] = 10.0
        
        # 风控建议
        if recommendations["tool"] == "RABBIT":
            recommendations["stop_loss"] = 5.0
            recommendations["take_profit"] = 8.0
        elif recommendations["tool"] == "GOPHER":
            recommendations["stop_loss"] = 8.0
            recommendations["take_profit"] = 15.0
        
        return recommendations
    
    def get_history(self, limit: int = 100) -> List[Dict]:
        """获取处理历史"""
        return self.history[-limit:]

# ==================== 主入口 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("信号处理模块测试")
    print("=" * 60)
    
    # 模拟信号数据
    test_signals = [
        {
            "symbol": "BTCUSDT",
            "model_id": "TREND_EMA_20",
            "direction": "BULL",
            "confidence": 0.7,
            "signal_type": "BUY",
            "timeframe": "1h"
        },
        {
            "symbol": "BTCUSDT",
            "model_id": "MOMENTUM_RSI_14",
            "direction": "BULL",
            "confidence": 0.6,
            "signal_type": "BUY",
            "timeframe": "1h"
        },
        {
            "symbol": "BTCUSDT",
            "model_id": "MOMENTUM_MACD_12_26_9",
            "direction": "BULL",
            "confidence": 0.65,
            "signal_type": "BUY",
            "timeframe": "1h"
        },
        {
            "symbol": "BTCUSDT",
            "model_id": "VOLATILITY_BOLLINGER_20_2_0",
            "direction": "SIDEWAYS",
            "confidence": 0.4,
            "signal_type": "NEUTRAL",
            "timeframe": "1h"
        }
    ]
    
    indicators_data = {
        "PRICE": 50500,
        "EMA_20": 50000,
        "RSI_14": 55
    }
    
    # 处理信号
    processor = SignalProcessor()
    result = processor.process(test_signals, indicators_data)
    
    print(f"\n处理状态: {result['status']}")
    print(f"信号数量: {result['signal_count']}")
    
    print(f"\n趋势分析:")
    if result['trend_analysis']:
        ta = result['trend_analysis']
        print(f"  方向: {ta['direction']}")
        print(f"  阶段: {ta['phase']}")
        print(f"  强度: {ta['strength']}")
        print(f"  置信度: {ta['confidence']}")
        print(f"  主要指标: {ta['primary_indicators']}")
    
    print(f"\n置信度评分:")
    conf = result['confidence']
    print(f"  综合: {conf['overall']}")
    print(f"  方向: {conf['directional']}")
    print(f"  强度: {conf['strength']}")
    
    print(f"\n聚合结果:")
    agg = result['aggregated']
    if agg:
        print(f"  方向: {agg['direction']}")
        print(f"  推荐工具: {agg['recommended_tool']}")
        print(f"  共识度: {agg['consensus_score']}")
    
    print(f"\n建议:")
    rec = result['recommendations']
    print(f"  操作: {rec['action']}")
    print(f"  工具: {rec['tool']}")
    print(f"  仓位: {rec['position_size']}%")
    print(f"  止损: {rec['stop_loss']}%")
    print(f"  止盈: {rec['take_profit']}%")
    
    print("\n✅ 信号处理测试完成")
