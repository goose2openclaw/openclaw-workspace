"""
声纳库 v2 - 扫描器模块
包含: 信号扫描、趋势分析、综合评分
2026-04-04 重构版本
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from .base import Signal, TREND_THRESHOLDS, calculate_rsi, calculate_macd, calculate_bollinger_bands
from .models import ModelFactory, TREND_MODELS_ALL

@dataclass
class ScanResult:
    symbol: str
    price: float
    timestamp: str
    signals: List[Signal]
    bullish_count: int
    bearish_count: int
    neutral_count: int
    confidence: float
    recommendation: str  # buy, sell, hold

class SonarScanner:
    """声纳扫描器 - 扫描市场信号"""
    
    def __init__(self):
        self.factory = ModelFactory()
        self.models = self.factory.get_all_models()
    
    def scan(self, symbol: str, price: float, indicators: Dict[str, float], 
             timestamp: str = None) -> ScanResult:
        """扫描并生成信号"""
        if timestamp is None:
            from datetime import datetime
            timestamp = datetime.now().isoformat()
        
        signals = []
        bullish_count = 0
        bearish_count = 0
        neutral_count = 0
        
        # 遍历指标生成信号
        for name, value in indicators.items():
            direction = self._get_direction(name, value)
            
            if direction == "bullish":
                bullish_count += 1
            elif direction == "bearish":
                bearish_count += 1
            else:
                neutral_count += 1
            
            # 查找对应模型获取权重
            model = self.factory.get_model(name)
            weight = model.weight if model else 1.0
            
            confidence = self._calculate_confidence(value, direction, weight)
            
            signals.append(Signal(
                symbol=symbol,
                model=name,
                direction=direction,
                confidence=confidence,
                price=price,
                timestamp=timestamp
            ))
        
        # 计算综合置信度
        total = bullish_count + bearish_count + neutral_count
        if total > 0:
            confidence = (bullish_count - bearish_count) / total
            confidence = (confidence + 1) / 2  # 归一化到0-1
        else:
            confidence = 0.5
        
        # 生成推荐
        recommendation = self._get_recommendation(bullish_count, bearish_count, neutral_count)
        
        return ScanResult(
            symbol=symbol,
            price=price,
            timestamp=timestamp,
            signals=signals,
            bullish_count=bullish_count,
            bearish_count=bearish_count,
            neutral_count=neutral_count,
            confidence=confidence,
            recommendation=recommendation
        )
    
    def _get_direction(self, name: str, value: float) -> str:
        """根据指标名称和值判断方向"""
        name_lower = name.lower()
        
        # RSI类
        if "rsi" in name_lower:
            if value < 30:
                return "bullish"  # 超卖=看涨
            elif value > 70:
                return "bearish"  # 超买=看跌
            return "neutral"
        
        # 随机指标类
        if "stoch" in name_lower or "stochastic" in name_lower:
            if value < 20:
                return "bullish"
            elif value > 80:
                return "bearish"
            return "neutral"
        
        # ADX类
        if "adx" in name_lower:
            if value > 25:
                return "bullish" if "plus" in name_lower or "tenkan" in name_lower else "bearish"
            return "neutral"
        
        # 布林带类
        if "bb_" in name_lower or "bollinger" in name_lower:
            if "upper" in name_lower:
                return "bearish"  # 价格接近上轨=阻力
            if "lower" in name_lower:
                return "bullish"  # 价格接近下轨=支撑
            return "neutral"
        
        # MACD类
        if "macd" in name_lower:
            if value > 0:
                return "bullish"
            elif value < 0:
                return "bearish"
            return "neutral"
        
        # EMA/MA交叉类
        if "cross" in name_lower:
            return "bullish" if value > 0 else "bearish"
        
        # 动量类
        if value > 50:
            return "bullish"
        elif value < 50:
            return "bearish"
        return "neutral"
    
    def _calculate_confidence(self, value: float, direction: str, weight: float) -> float:
        """计算置信度"""
        base = abs(value - 50) / 50  # 0-1 based on distance from 50
        return min(1.0, base * weight)
    
    def _get_recommendation(self, bullish: int, bearish: int, neutral: int) -> str:
        """生成推荐"""
        if bullish > bearish * 1.5 and bullish > neutral:
            return "buy"
        elif bearish > bullish * 1.5 and bearish > neutral:
            return "sell"
        return "hold"
    
    def get_trend_summary(self, result: ScanResult) -> Dict:
        """获取趋势摘要"""
        return {
            "symbol": result.symbol,
            "price": result.price,
            "confidence": f"{result.confidence:.1%}",
            "recommendation": result.recommendation.upper(),
            "bullish_signals": result.bullish_count,
            "bearish_signals": result.bearish_count,
            "neutral_signals": result.neutral_count,
            "bullish_ratio": f"{result.bullish_count / max(1, result.bullish_count + result.bearish_count):.1%}",
        }


class SonarLibrary:
    """声纳库 - 管理所有扫描器"""
    
    def __init__(self):
        self.scanner = SonarScanner()
        self.model_count = self.scanner.factory.get_model_count()
        self.category_count = len(set(m.category for m in self.scanner.factory.get_all_models()))
    
    def analyze(self, symbol: str, price: float, indicators: Dict[str, float]) -> Dict:
        """综合分析"""
        result = self.scanner.scan(symbol, price, indicators)
        summary = self.scanner.get_trend_summary(result)
        
        return {
            "status": "success",
            "model_count": self.model_count,
            "analysis": summary,
            "recommendation": result.recommendation,
            "confidence": result.confidence,
        }
    
    def get_stats(self) -> Dict:
        """获取声纳库统计"""
        return {
            "total_models": self.model_count,
            "categories": self.category_count,
            "models_by_category": {
                cat: len(models) 
                for cat, models in self.scanner.factory.get_all_models().__class__.items()
            } if hasattr(self.scanner.factory.get_all_models(), '__class__') else {}
        }


# 导出
__all__ = [
    "SonarScanner",
    "SonarLibrary",
    "ScanResult",
    "Signal",
]
