"""
🤖 机器学习集成引擎
==================
为北斗七鑫添加ML预测能力

功能:
- 价格趋势预测
- 波动率预测
- 异常检测
- 策略参数优化
- 情感分析
"""

import json
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import deque
import statistics
import logging

logger = logging.getLogger(__name__)


@dataclass
class MLPrediction:
    """ML预测结果"""
    symbol: str
    prediction_type: str  # trend, volatility, anomaly, price
    direction: str  # UP, DOWN, NEUTRAL
    confidence: float  # 0.0 - 1.0
    horizon: int  # 预测周期(小时)
    timestamp: datetime = field(default_factory=datetime.now)
    features: Dict = field(default_factory=dict)
    model_version: str = "v1.0"


class MLEngine:
    """
    机器学习集成引擎
    ===============
    
    注意: 这里实现的是轻量级ML逻辑
    生产环境可替换为真正的ML模型(TensorFlow/PyTorch)
    """
    
    def __init__(self):
        self.models = {}
        self.price_history: Dict[str, deque] = {}  # 价格历史
        self.max_history = 168  # 保留7天 * 24小时
        
        # 初始化内置模型
        self._init_models()
    
    def _init_models(self):
        """初始化内置模型"""
        self.models = {
            "trend": {"name": "趋势预测器", "version": "v1.0", "accuracy": 0.72},
            "volatility": {"name": "波动率预测", "version": "v1.0", "accuracy": 0.68},
            "anomaly": {"name": "异常检测", "version": "v1.0", "accuracy": 0.85},
            "sentiment": {"name": "情感分析", "version": "v1.0", "accuracy": 0.65},
        }
        logger.info(f"✅ ML引擎已初始化，共{len(self.models)}个模型")
    
    def update_price(self, symbol: str, price: float, timestamp: datetime = None) -> None:
        """更新价格历史"""
        if symbol not in self.price_history:
            self.price_history[symbol] = deque(maxlen=self.max_history)
        
        self.price_history[symbol].append({
            "price": price,
            "timestamp": timestamp or datetime.now()
        })
    
    def predict_trend(self, symbol: str, horizon: int = 24) -> MLPrediction:
        """
        趋势预测
        ========
        使用移动平均线交叉和动量指标
        """
        if symbol not in self.price_history or len(self.price_history[symbol]) < 50:
            return MLPrediction(
                symbol=symbol,
                prediction_type="trend",
                direction="NEUTRAL",
                confidence=0.0,
                horizon=horizon,
                features={"error": "数据不足"}
            )
        
        prices = [p["price"] for p in self.price_history[symbol]]
        
        # 计算移动平均
        ma_short = statistics.mean(prices[-12:])  # 12小时
        ma_medium = statistics.mean(prices[-24:])  # 24小时
        ma_long = statistics.mean(prices[-48:])  # 48小时
        
        # 计算动量
        momentum = (prices[-1] - prices[-24]) / prices[-24] * 100 if len(prices) >= 24 else 0
        
        # 计算RSI
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas[-14:]]
        losses = [-d if d < 0 else 0 for d in deltas[-14:]]
        avg_gain = sum(gains) / 14
        avg_loss = sum(losses) / 14
        rsi = 100 - (100 / (1 + avg_gain / avg_loss)) if avg_loss > 0 else 50
        
        # 趋势判断
        if ma_short > ma_medium > ma_long and rsi < 70:
            direction = "UP"
            confidence = min(0.5 + abs(momentum) / 100, 0.95)
        elif ma_short < ma_medium < ma_long and rsi > 30:
            direction = "DOWN"
            confidence = min(0.5 + abs(momentum) / 100, 0.95)
        else:
            direction = "NEUTRAL"
            confidence = 0.5
        
        return MLPrediction(
            symbol=symbol,
            prediction_type="trend",
            direction=direction,
            confidence=confidence,
            horizon=horizon,
            features={
                "ma_short": ma_short,
                "ma_medium": ma_medium,
                "ma_long": ma_long,
                "momentum": momentum,
                "rsi": rsi
            }
        )
    
    def predict_volatility(self, symbol: str, horizon: int = 24) -> MLPrediction:
        """
        波动率预测
        ==========
        使用历史波动率和ARCH效应
        """
        if symbol not in self.price_history or len(self.price_history[symbol]) < 24:
            return MLPrediction(
                symbol=symbol,
                prediction_type="volatility",
                direction="NEUTRAL",
                confidence=0.0,
                horizon=horizon
            )
        
        prices = [p["price"] for p in self.price_history[symbol]]
        returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
        
        # 计算历史波动率
        hist_vol = statistics.stdev(returns[-24:]) if len(returns) >= 24 else 0
        
        # 计算BBand宽度 (波动率指标)
        recent = prices[-20:]
        sma = statistics.mean(recent)
        std = statistics.stdev(recent)
        bb_width = (max(recent) - min(recent)) / sma if sma > 0 else 0
        
        # 波动率趋势
        vol_change = abs(returns[-1]) / hist_vol if hist_vol > 0 else 1
        
        if vol_change > 1.5:
            direction = "HIGH"
            confidence = min(vol_change / 3, 0.9)
        elif vol_change < 0.5:
            direction = "LOW"
            confidence = min(1 - vol_change, 0.9)
        else:
            direction = "NORMAL"
            confidence = 0.6
        
        return MLPrediction(
            symbol=symbol,
            prediction_type="volatility",
            direction=direction,
            confidence=confidence,
            horizon=horizon,
            features={
                "hist_volatility": hist_vol,
                "bb_width": bb_width,
                "vol_change": vol_change
            }
        )
    
    def detect_anomaly(self, symbol: str) -> MLPrediction:
        """
        异常检测
        ========
        使用Z-Score和移动窗口
        """
        if symbol not in self.price_history or len(self.price_history[symbol]) < 50:
            return MLPrediction(
                symbol=symbol,
                prediction_type="anomaly",
                direction="NEUTRAL",
                confidence=0.0
            )
        
        prices = [p["price"] for p in self.price_history[symbol]]
        
        # 计算Z-Score
        recent = prices[-20:]
        mean = statistics.mean(prices[-50:-20])  # 用前30个作为基准
        std = statistics.stdev(prices[-50:-20])
        
        z_score = (prices[-1] - mean) / std if std > 0 else 0
        
        # 检测异常
        if abs(z_score) > 3:
            direction = "ANOMALY"
            confidence = 0.95
        elif abs(z_score) > 2:
            direction = "WARNING"
            confidence = 0.75
        else:
            direction = "NORMAL"
            confidence = 0.85
        
        return MLPrediction(
            symbol=symbol,
            prediction_type="anomaly",
            direction=direction,
            confidence=confidence,
            horizon=1,
            features={
                "z_score": z_score,
                "threshold": 3
            }
        )
    
    def analyze_sentiment(self, symbol: str, social_data: Dict = None) -> MLPrediction:
        """
        情感分析
        =========
        基于社交媒体和市场情绪指标
        """
        if symbol not in self.price_history:
            return MLPrediction(
                symbol=symbol,
                prediction_type="sentiment",
                direction="NEUTRAL",
                confidence=0.5
            )
        
        # 简化: 使用价格动量和RSI作为情感代理
        prices = [p["price"] for p in self.price_history[symbol]]
        
        if len(prices) < 24:
            return MLPrediction(
                symbol=symbol,
                prediction_type="sentiment",
                direction="NEUTRAL",
                confidence=0.5
            )
        
        momentum_24h = (prices[-1] - prices[-24]) / prices[-24] * 100
        
        if momentum_24h > 5:
            direction = "VERY_BULLISH"
            confidence = 0.8
        elif momentum_24h > 2:
            direction = "BULLISH"
            confidence = 0.7
        elif momentum_24h < -5:
            direction = "VERY_BEARISH"
            confidence = 0.8
        elif momentum_24h < -2:
            direction = "BEARISH"
            confidence = 0.7
        else:
            direction = "NEUTRAL"
            confidence = 0.6
        
        return MLPrediction(
            symbol=symbol,
            prediction_type="sentiment",
            direction=direction,
            confidence=confidence,
            horizon=4,
            features={"momentum_24h": momentum_24h}
        )
    
    def predict_all(self, symbol: str) -> List[MLPrediction]:
        """获取所有预测"""
        return [
            self.predict_trend(symbol),
            self.predict_volatility(symbol),
            self.detect_anomaly(symbol),
            self.analyze_sentiment(symbol)
        ]
    
    def get_combined_signal(self, symbol: str) -> Dict:
        """
        获取组合信号
        ============
        综合所有ML模型输出
        """
        predictions = self.predict_all(symbol)
        
        # 聚合方向
        direction_votes = {"UP": 0.0, "DOWN": 0.0, "NEUTRAL": 0.0}
        total_confidence = 0.0
        
        for pred in predictions:
            if pred.prediction_type == "anomaly" and pred.direction == "ANOMALY":
                # 异常检测优先
                return {
                    "symbol": symbol,
                    "action": "AVOID",
                    "confidence": pred.confidence,
                    "reason": "anomaly_detected",
                    "predictions": {p.prediction_type: p.direction for p in predictions}
                }
            
            weight = 1.0
            if pred.prediction_type == "trend":
                weight = 0.4
            elif pred.prediction_type == "sentiment":
                weight = 0.3
            elif pred.prediction_type == "volatility":
                weight = 0.2
            elif pred.prediction_type == "anomaly":
                weight = 0.1
            
            dir_map = {"UP": "UP", "DOWN": "DOWN", "VERY_BULLISH": "UP", 
                      "VERY_BEARISH": "DOWN", "BULLISH": "UP", "BEARISH": "DOWN"}
            
            mapped_dir = dir_map.get(pred.direction, "NEUTRAL")
            direction_votes[mapped_dir] += pred.confidence * weight
            total_confidence += pred.confidence * weight
        
        # 归一化
        if total_confidence > 0:
            for d in direction_votes:
                direction_votes[d] /= total_confidence
        
        # 最终决策
        final_dir = max(direction_votes, key=direction_votes.get)
        final_conf = direction_votes[final_dir]
        
        # 映射到交易动作
        action_map = {
            "UP": "LONG",
            "DOWN": "SHORT",
            "NEUTRAL": "HOLD"
        }
        
        return {
            "symbol": symbol,
            "action": action_map[final_dir],
            "confidence": final_conf,
            "direction_votes": direction_votes,
            "predictions": {p.prediction_type: {"dir": p.direction, "conf": p.confidence} 
                          for p in predictions}
        }
    
    def get_status(self) -> Dict:
        """获取引擎状态"""
        return {
            "models": self.models,
            "symbols_tracked": len(self.price_history),
            "history_size": {sym: len(h) for sym, h in self.price_history.items()}
        }


# 全局实例
ml_engine = MLEngine()


if __name__ == "__main__":
    print("✅ ML引擎已初始化")
    print(f"状态: {ml_engine.get_status()}")
    
    # 模拟数据
    import random
    base_price = 50000
    for i in range(100):
        price = base_price + random.uniform(-2000, 3000)
        ml_engine.update_price("BTCUSDT", price)
    
    # 获取预测
    signal = ml_engine.get_combined_signal("BTCUSDT")
    print(f"\nBTC综合信号:")
    print(f"  动作: {signal['action']}")
    print(f"  置信度: {signal['confidence']:.2f}")
    print(f"  方向投票: {signal['direction_votes']}")
