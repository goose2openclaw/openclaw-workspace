#!/usr/bin/env python3
"""
🪿 GO2SE 备选策略系统 - 本地实现
包含: RSI, MACD, Bollinger, ML信号, 统计套利
"""

import random
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict


@dataclass
class MarketData:
    """市场数据"""
    symbol: str
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float


class TechnicalIndicators:
    """技术指标计算"""
    
    @staticmethod
    def sma(prices: List[float], period: int) -> float:
        if len(prices) < period:
            return prices[-1] if prices else 0
        return sum(prices[-period:]) / period
    
    @staticmethod
    def ema(prices: List[float], period: int) -> float:
        if len(prices) < period:
            return prices[-1] if prices else 0
        multiplier = 2 / (period + 1)
        ema = sum(prices[:period]) / period
        for price in prices[period:]:
            ema = (price - ema) * multiplier + ema
        return ema
    
    @staticmethod
    def rsi(prices: List[float], period: int = 14) -> float:
        if len(prices) < period + 1:
            return 50.0
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas[-period:]]
        losses = [-d if d < 0 else 0 for d in deltas[-period:]]
        avg_gain = sum(gains) / period or 0.0001
        avg_loss = sum(losses) / period or 0.0001
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    def macd(prices: List[float]) -> Tuple[float, float, float]:
        ema12 = TechnicalIndicators.ema(prices, 12)
        ema26 = TechnicalIndicators.ema(prices, 26)
        macd_line = ema12 - ema26
        # 简化signal线
        signal = macd_line * 0.9
        return macd_line, signal, macd_line - signal
    
    @staticmethod
    def bollinger_bands(prices: List[float], period: int = 20) -> Tuple[float, float, float]:
        if len(prices) < period:
            return prices[-1], prices[-1], prices[-1]
        sma = sum(prices[-period:]) / period
        variance = sum((p - sma) ** 2 for p in prices[-period:]) / period
        std = variance ** 0.5
        return sma + 2 * std, sma, sma - 2 * std
    
    @staticmethod
    def atr(candles: List[MarketData], period: int = 14) -> float:
        if len(candles) < period:
            return 0
        ranges = []
        for c in candles[-period:]:
            tr = max(c.high - c.low, 
                    abs(c.high - c.close),
                    abs(c.low - c.close))
            ranges.append(tr)
        return sum(ranges) / period


class MLSignalGenerator:
    """机器学习信号生成器 (纯Python实现)"""
    
    def __init__(self):
        self.weights = {
            'rsi': 0.25,
            'macd': 0.25,
            'bollinger': 0.20,
            'volume': 0.15,
            'momentum': 0.15
        }
    
    def generate_signal(self, candles: List[MarketData]) -> Tuple[str, float, Dict]:
        """生成ML增强信号"""
        if len(candles) < 30:
            return "hold", 0.0, {}
        
        closes = [c.close for c in candles]
        volumes = [c.volume for c in candles]
        
        # 计算各项指标
        signals = {}
        
        # RSI
        rsi = TechnicalIndicators.rsi(closes, 14)
        if rsi < 30:
            signals['rsi'] = 1.0
        elif rsi > 70:
            signals['rsi'] = -1.0
        elif rsi < 40:
            signals['rsi'] = 0.5
        elif rsi > 60:
            signals['rsi'] = -0.5
        else:
            signals['rsi'] = 0
        
        # MACD
        macd, signal, hist = TechnicalIndicators.macd(closes)
        signals['macd'] = 1.0 if hist > 0 else -1.0
        
        # Bollinger
        bb_upper, bb_middle, bb_lower = TechnicalIndicators.bollinger_bands(closes)
        current = closes[-1]
        if current < bb_lower:
            signals['bollinger'] = 1.0
        elif current > bb_upper:
            signals['bollinger'] = -1.0
        else:
            signals['bollinger'] = 0
        
        # Volume
        avg_volume = sum(volumes[-10:]) / 10
        if volumes[-1] > avg_volume * 1.5:
            signals['volume'] = 1.0
        elif volumes[-1] < avg_volume * 0.5:
            signals['volume'] = -0.5
        else:
            signals['volume'] = 0
        
        # Momentum
        if len(closes) >= 10:
            momentum = (closes[-1] - closes[-10]) / closes[-10] * 100
            signals['momentum'] = min(max(momentum / 10, -1), 1)
        else:
            signals['momentum'] = 0
        
        # 加权计算总分
        total_score = sum(signals[k] * self.weights[k] for k in signals)
        
        # 置信度
        confidence = min(abs(total_score), 1.0)
        
        # 最终信号
        if total_score > 0.5:
            return "buy", confidence, signals
        elif total_score < -0.5:
            return "sell", confidence, signals
        else:
            return "hold", confidence, signals


class StatisticalArbitrage:
    """统计套利策略"""
    
    def __init__(self):
        self.lookback = 50
        self.z_entry = 2.0
        self.z_exit = 0.5
        
        # 预设交易对
        self.pairs = [
            ("BTC/ETH", 0.02),
            ("ETH/BNB", 0.05),
            ("XRP/ADA", 0.1),
        ]
    
    def calculate_spread(self, price_a: List[float], price_b: List[float]) -> List[float]:
        """计算价差"""
        if len(price_a) != len(price_b):
            return []
        # 简化: 使用比率
        return [a / b for a, b in zip(price_a, price_b)]
    
    def calculate_zscore(self, spread: List[float]) -> float:
        """计算Z分数"""
        if len(spread) < self.lookback:
            return 0
        recent = spread[-self.lookback:]
        mean = sum(recent) / len(recent)
        variance = sum((s - mean) ** 2 for s in recent) / len(recent)
        std = variance ** 0.5
        if std == 0:
            return 0
        return (spread[-1] - mean) / std
    
    def generate_signal(self, pair_prices: Dict[str, List[float]]) -> Tuple[str, float]:
        """生成套利信号"""
        # 简化实现
        symbols = list(pair_prices.keys())
        if len(symbols) < 2:
            return "hold", 0
        
        spread = self.calculate_spread(
            pair_prices[symbols[0]],
            pair_prices[symbols[1]]
        )
        zscore = self.calculate_zscore(spread)
        
        if zscore > self.z_entry:
            return "sell", abs(zscore) / 4  # 价差过大，做空
        elif zscore < -self.z_entry:
            return "buy", abs(zscore) / 4
        elif abs(zscore) < self.z_exit:
            return "hold", 0
        
        return "hold", 0


class AlternativeStrategyEngine:
    """备选策略引擎"""
    
    STRATEGIES = {
        "lean_rsi": {
            "name": "Lean RSI均值回归",
            "type": "quant",
            "description": "基于RSI的经典均值回归策略",
            "params": {"rsi_period": 14, "oversold": 30, "overbought": 70}
        },
        "lean_macd": {
            "name": "Lean MACD趋势",
            "type": "quant", 
            "description": "MACD金叉死叉趋势策略",
            "params": {"fast": 12, "slow": 26, "signal": 9}
        },
        "bollinger_bands": {
            "name": "布林带突破",
            "type": "quant",
            "description": "布林带上下轨突破策略",
            "params": {"period": 20, "std": 2}
        },
        "ml_ensemble": {
            "name": "ML多指标集成",
            "type": "ML",
            "description": "多指标加权机器学习信号",
            "params": {}
        },
        "stat_arb": {
            "name": "统计套利",
            "type": "arb",
            "description": "配对交易统计套利",
            "params": {"lookback": 50, "z_entry": 2.0}
        },
        "momentum": {
            "name": "动量策略",
            "type": "quant",
            "description": "价格动量跟踪策略",
            "params": {"lookback": 20}
        }
    }
    
    def __init__(self):
        self.ml_generator = MLSignalGenerator()
        self.stat_arb = StatisticalArbitrage()
        
    def run_strategy(self, strategy_id: str, candles: List[MarketData]) -> Dict:
        """运行策略"""
        if strategy_id not in self.STRATEGIES:
            return {"error": "策略不存在"}
        
        closes = [c.close for c in candles]
        
        if strategy_id == "lean_rsi":
            rsi = TechnicalIndicators.rsi(closes, 14)
            if rsi < 30:
                return {"signal": "buy", "confidence": (30-rsi)/30, "rsi": rsi}
            elif rsi > 70:
                return {"signal": "sell", "confidence": (rsi-70)/30, "rsi": rsi}
            return {"signal": "hold", "confidence": 0.5, "rsi": rsi}
        
        elif strategy_id == "lean_macd":
            macd, signal, hist = TechnicalIndicators.macd(closes)
            if hist > 0:
                return {"signal": "buy", "confidence": min(hist/10, 1), "macd": macd}
            elif hist < 0:
                return {"signal": "sell", "confidence": min(-hist/10, 1), "macd": macd}
            return {"signal": "hold", "confidence": 0.5, "macd": macd}
        
        elif strategy_id == "bollinger_bands":
            bb_upper, bb_middle, bb_lower = TechnicalIndicators.bollinger_bands(closes)
            current = closes[-1]
            if current < bb_lower:
                return {"signal": "buy", "confidence": 0.8, "bb": "lower"}
            elif current > bb_upper:
                return {"signal": "sell", "confidence": 0.8, "bb": "upper"}
            return {"signal": "hold", "confidence": 0.5, "bb": "middle"}
        
        elif strategy_id == "ml_ensemble":
            signal, confidence, details = self.ml_generator.generate_signal(candles)
            return {"signal": signal, "confidence": confidence, "details": details}
        
        elif strategy_id == "stat_arb":
            # 简化
            return {"signal": "hold", "confidence": 0, "note": "需要多币种数据"}
        
        elif strategy_id == "momentum":
            if len(closes) < 20:
                return {"signal": "hold", "confidence": 0}
            mom = (closes[-1] - closes[-20]) / closes[-20] * 100
            if mom > 5:
                return {"signal": "buy", "confidence": min(mom/20, 1), "momentum": mom}
            elif mom < -5:
                return {"signal": "sell", "confidence": min(-mom/20, 1), "momentum": mom}
            return {"signal": "hold", "confidence": 0.5, "momentum": mom}
        
        return {"error": "未知策略"}


# 全局引擎
engine = AlternativeStrategyEngine()


def get_available_strategies() -> Dict:
    """获取可用策略列表"""
    return {
        "strategies": AlternativeStrategyEngine.STRATEGIES,
        "count": len(AlternativeStrategyEngine.STRATEGIES)
    }


def run_strategy_test(strategy_id: str = "ml_ensemble", symbols: List[str] = None, days: int = 30) -> Dict:
    """测试策略"""
    import math
    
    if symbols is None:
        symbols = ["BTC/USDT"]
    
    results = {}
    
    for symbol in symbols:
        # 生成模拟数据
        base_price = 75000 if "BTC" in symbol else 2000
        candles = []
        
        for i in range(days * 24):
            ts = datetime.now().timestamp() - (days * 24 - i) * 3600
            price = base_price * (1 + random.gauss(0, 0.02))
            
            candles.append(MarketData(
                symbol=symbol,
                timestamp=datetime.fromtimestamp(ts).isoformat(),
                open=price * 0.99,
                high=price * 1.02,
                low=price * 0.98,
                close=price,
                volume=random.uniform(100, 1000)
            ))
        
        # 运行策略
        result = engine.run_strategy(strategy_id, candles)
        result["symbol"] = symbol
        results[symbol] = result
    
    return results


if __name__ == "__main__":
    print("🪿 备选策略系统测试")
    print("=" * 50)
    
    strategies = ["lean_rsi", "lean_macd", "bollinger_bands", "ml_ensemble", "momentum"]
    
    for strat in strategies:
        result = run_strategy_test(strat, ["BTC/USDT"], 30)
        r = result.get("BTC/USDT", {})
        print(f"{strat:20} -> {r.get('signal', 'error'):5} (置信度: {r.get('confidence', 0):.2f})")
    
    print("=" * 50)
    print("✅ 测试完成")
