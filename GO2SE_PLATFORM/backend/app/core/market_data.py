#!/usr/bin/env python3
"""
📊 北斗七鑫实时市场数据模块
===========================
集成Binance实时行情 + 趋势计算 + MiroFish信号

功能:
1. 实时价格获取
2. 趋势信号计算 (RSI, MACD, Bollinger Bands)
3. 市场状态识别
4. 工具信号生成
"""

import json
import math
import urllib.request
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum

BINANCE_BASE = "https://api.binance.com/api/v3"


class MarketRegime(Enum):
    """市场状态"""
    TRENDING_UP = "TRENDING_UP"
    TRENDING_DOWN = "TRENDING_DOWN"
    RANGE_BOUND = "RANGE_BOUND"
    VOLATILE = "VOLATILE"
    QUIET = "QUIET"


class MarketDataProvider:
    """实时市场数据提供者"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 5  # 秒
    
    def get_ticker(self, symbol: str) -> Optional[Dict]:
        """获取币种Ticker数据"""
        url = f"{BINANCE_BASE}/ticker/24hr?symbol={symbol.upper()}"
        try:
            with urllib.request.urlopen(url, timeout=5) as resp:
                data = json.loads(resp.read())
                return {
                    "symbol": data["symbol"],
                    "price": float(data["lastPrice"]),
                    "change_24h": float(data["priceChangePercent"]),
                    "high_24h": float(data["highPrice"]),
                    "low_24h": float(data["lowPrice"]),
                    "volume": float(data["volume"]),
                    "quote_volume": float(data["quoteVolume"]),
                    "bid": float(data["bidPrice"]),
                    "ask": float(data["askPrice"]),
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {"error": str(e)}
    
    def get_klines(self, symbol: str, interval: str = "1h", limit: int = 100) -> List[Dict]:
        """获取K线数据"""
        url = f"{BINANCE_BASE}/klines?symbol={symbol.upper()}&interval={interval}&limit={limit}"
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read())
                return [
                    {
                        "open_time": datetime.fromtimestamp(d[0]/1000),
                        "open": float(d[1]),
                        "high": float(d[2]),
                        "low": float(d[3]),
                        "close": float(d[4]),
                        "volume": float(d[5]),
                        "close_time": datetime.fromtimestamp(d[6]/1000)
                    }
                    for d in data
                ]
        except Exception as e:
            return []
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """计算RSI"""
        if len(prices) < period + 1:
            return 50.0
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas[-period:]]
        losses = [-d if d < 0 else 0 for d in deltas[-period:]]
        
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return round(rsi, 2)
    
    def calculate_macd(self, prices: List[float]) -> Dict[str, float]:
        """计算MACD"""
        if len(prices) < 26:
            return {"macd": 0, "signal": 0, "histogram": 0}
        
        # EMA计算
        def ema(data, period):
            k = 2 / (period + 1)
            ema_val = data[0]
            for d in data[1:]:
                ema_val = d * k + ema_val * (1 - k)
            return ema_val
        
        ema12 = ema(prices, 12)
        ema26 = ema(prices, 26)
        macd_line = ema12 - ema26
        
        # Signal line (9-period EMA of MACD)
        macd_values = [macd_line]  # 简化，实际需要更多数据
        signal_line = ema(macd_values, 9)
        
        return {
            "macd": round(macd_line, 4),
            "signal": round(signal_line, 4),
            "histogram": round(macd_line - signal_line, 4)
        }
    
    def calculate_bollinger_bands(self, prices: List[float], period: int = 20, std_dev: int = 2) -> Dict[str, float]:
        """计算布林带"""
        if len(prices) < period:
            return {"upper": 0, "middle": 0, "lower": 0}
        
        recent = prices[-period:]
        sma = sum(recent) / period
        variance = sum((p - sma) ** 2 for p in recent) / period
        std = math.sqrt(variance)
        
        return {
            "upper": round(sma + std * std_dev, 2),
            "middle": round(sma, 2),
            "lower": round(sma - std * std_dev, 2)
        }
    
    def detect_trend(self, prices: List[float]) -> Tuple[str, float]:
        """检测趋势方向和强度"""
        if len(prices) < 50:
            return "NEUTRAL", 0.5
        
        # 简单趋势检测：比较50日均线和当前价格
        ma50 = sum(prices[-50:]) / 50
        ma20 = sum(prices[-20:]) / 20
        current = prices[-1]
        
        if current > ma50 and current > ma20:
            return "BULLISH", min((current - ma50) / ma50 * 2, 1.0)
        elif current < ma50 and current < ma20:
            return "BEARISH", min((ma50 - current) / ma50 * 2, 1.0)
        else:
            return "NEUTRAL", 0.5
    
    def detect_market_regime(self, prices: List[float], volumes: List[float]) -> Tuple[MarketRegime, float]:
        """识别市场状态"""
        if len(prices) < 20:
            return MarketRegime.RANGE_BOUND, 0.5
        
        # 计算波动率
        returns = [math.log(prices[i]/prices[i-1]) for i in range(1, len(prices))]
        volatility = sum(abs(r) for r in returns[-20:]) / 20
        
        # 计算成交量变化
        vol_change = (sum(volumes[-5:]) / 5) / (sum(volumes[-20:-5]) / 15) - 1 if sum(volumes[-20:-5]) > 0 else 0
        
        # 检测趋势
        trend, strength = self.detect_trend(prices)
        
        if volatility > 0.05:
            return MarketRegime.VOLATILE, strength
        elif vol_change > 0.5:
            return MarketRegime.VOLATILE, strength
        elif trend == "BULLISH" and strength > 0.7:
            return MarketRegime.TRENDING_UP, strength
        elif trend == "BEARISH" and strength > 0.7:
            return MarketRegime.TRENDING_DOWN, strength
        elif volatility < 0.02:
            return MarketRegime.QUIET, 0.5
        else:
            return MarketRegime.RANGE_BOUND, 0.5
    
    def calculate_atr(self, highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> float:
        """计算ATR (Average True Range)"""
        if len(highs) < period + 1:
            return 0.0
        
        true_ranges = []
        for i in range(1, len(highs)):
            tr = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i-1]),
                abs(lows[i] - closes[i-1])
            )
            true_ranges.append(tr)
        
        return round(sum(true_ranges[-period:]) / period, 4)
    
    def get_tool_signal(self, symbol: str) -> Dict:
        """获取工具信号 (打兔子/打地鼠/跟大哥)"""
        ticker = self.get_ticker(symbol)
        if "error" in ticker:
            return {"error": ticker["error"]}
        
        klines = self.get_klines(symbol, "1h", 100)
        if not klines:
            return {"error": "No kline data"}
        
        prices = [k["close"] for k in klines]
        highs = [k["high"] for k in klines]
        lows = [k["low"] for k in klines]
        volumes = [k["volume"] for k in klines]
        
        # 计算各项指标
        rsi = self.calculate_rsi(prices)
        macd = self.calculate_macd(prices)
        bb = self.calculate_bollinger_bands(prices)
        trend, trend_strength = self.detect_trend(prices)
        regime, regime_confidence = self.detect_market_regime(prices, volumes)
        atr = self.calculate_atr(highs, lows, prices)
        atr_pct = atr / prices[-1] if prices[-1] > 0 else 0
        
        # RSI信号
        rsi_signal = "OVERBOUGHT" if rsi > 70 else "OVERSOLD" if rsi < 30 else "NEUTRAL"
        
        # MACD信号
        macd_signal = "BULLISH" if macd["histogram"] > 0 else "BEARISH"
        
        # 综合信号
        bullish_signals = sum([
            trend == "BULLISH",
            rsi_signal == "OVERSOLD",
            macd_signal == "BULLISH",
            ticker["price"] > bb["middle"]
        ])
        
        if bullish_signals >= 3:
            overall_signal = "BUY"
        elif bullish_signals <= 1:
            overall_signal = "SELL"
        else:
            overall_signal = "HOLD"
        
        return {
            "symbol": symbol,
            "price": ticker["price"],
            "change_24h": ticker["change_24h"],
            "rsi": rsi,
            "rsi_signal": rsi_signal,
            "macd": macd,
            "macd_signal": macd_signal,
            "bollinger_bands": bb,
            "trend": trend,
            "trend_strength": round(trend_strength, 2),
            "market_regime": regime.value,
            "regime_confidence": round(regime_confidence, 2),
            "atr": atr,
            "atr_percent": round(atr_pct * 100, 2),
            "volume_24h": ticker["volume"],
            "overall_signal": overall_signal,
            "confidence": round(bullish_signals / 4, 2),
            "timestamp": datetime.now().isoformat()
        }


class BeidouSevenTools:
    """北斗七鑫工具信号生成器"""
    
    def __init__(self):
        self.provider = MarketDataProvider()
        
        # 北斗七鑫配置
        self.tools_config = {
            "rabbit": {
                "name": "🐰 打兔子",
                "symbols": ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"],
                "trend_threshold": 0.6,
                "rsi_oversold": 30,
                "rsi_overbought": 70
            },
            "mole": {
                "name": "🐹 打地鼠",
                "symbols": [],  # 动态发现
                "volume_threshold": 2.0,  # 成交量倍数
                "change_threshold": 5.0    # 波动阈值%
            },
            "oracle": {
                "name": "🔮 走着瞧",
                "symbols": ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
                "min_confidence": 0.7
            },
            "leader": {
                "name": "👑 跟大哥",
                "symbols": ["BTCUSDT", "ETHUSDT"],
                "trend_confidence": 0.7
            }
        }
    
    def get_rabbit_signals(self) -> List[Dict]:
        """打兔子信号 - 主流币趋势跟踪"""
        signals = []
        config = self.tools_config["rabbit"]
        
        for symbol in config["symbols"]:
            signal = self.provider.get_tool_signal(symbol)
            if "error" in signal:
                continue
            
            # 趋势跟踪逻辑
            if signal["trend"] == "BULLISH" and signal["trend_strength"] > config["trend_threshold"]:
                action = "LONG"
            elif signal["trend"] == "BEARISH" and signal["trend_strength"] > config["trend_threshold"]:
                action = "SHORT" if self.provider.get_ticker(symbol)["change_24h"] < -5 else "CLOSE"
            else:
                action = "HOLD"
            
            signals.append({
                "tool": "rabbit",
                "symbol": symbol,
                "action": action,
                "price": signal["price"],
                "trend": signal["trend"],
                "trend_strength": signal["trend_strength"],
                "rsi": signal["rsi"],
                "confidence": signal["confidence"],
                "market_regime": signal["market_regime"]
            })
        
        return signals
    
    def get_mole_signals(self) -> List[Dict]:
        """打地鼠信号 - 异动扫描"""
        signals = []
        config = self.tools_config["mole"]
        
        # 获取所有USDT交易对
        try:
            url = f"{BINANCE_BASE}/ticker/24hr"
            with urllib.request.urlopen(url, timeout=10) as resp:
                all_tickers = json.loads(resp.read())
            
            # 过滤高波动币种
            movers = [
                t for t in all_tickers 
                if t["symbol"].endswith("USDT")
                and abs(float(t["priceChangePercent"])) > config["change_threshold"]
                and float(t["quoteVolume"]) > 1e6
            ]
            movers.sort(key=lambda x: abs(float(x["priceChangePercent"])), reverse=True)
            
            for t in movers[:10]:  # Top 10异动
                symbol = t["symbol"]
                signal = self.provider.get_tool_signal(symbol)
                if "error" in signal:
                    continue
                
                signals.append({
                    "tool": "mole",
                    "symbol": symbol,
                    "action": "SCAN",
                    "price": float(t["lastPrice"]),
                    "change_24h": float(t["priceChangePercent"]),
                    "volume": float(t["quoteVolume"]),
                    "rsi": signal["rsi"],
                    "trend": signal["trend"],
                    "market_regime": signal["market_regime"]
                })
        except Exception as e:
            return [{"error": str(e)}]
        
        return signals
    
    def get_leader_signals(self) -> List[Dict]:
        """跟大哥信号 - 趋势确认 + 做市"""
        signals = []
        config = self.tools_config["leader"]
        
        for symbol in config["symbols"]:
            signal = self.provider.get_tool_signal(symbol)
            if "error" in signal:
                continue
            
            # 做市逻辑：趋势确认后跟随
            if signal["trend"] == "BULLISH" and signal["trend_strength"] > config["trend_confidence"]:
                action = "LONG"
                leverage = 3
            elif signal["trend"] == "BEARISH" and signal["trend_strength"] > config["trend_confidence"]:
                action = "SHORT"
                leverage = 2
            else:
                action = "HOLD"
                leverage = 1
            
            signals.append({
                "tool": "leader",
                "symbol": symbol,
                "action": action,
                "leverage": leverage,
                "price": signal["price"],
                "trend": signal["trend"],
                "trend_strength": signal["trend_strength"],
                "confidence": signal["confidence"],
                "atr_percent": signal["atr_percent"]
            })
        
        return signals
    
    def get_all_signals(self) -> Dict:
        """获取所有工具信号"""
        return {
            "rabbit": self.get_rabbit_signals(),
            "mole": self.get_mole_signals(),
            "oracle": [{"tool": "oracle", "status": "mirofish_dependent"}],  # MiroFish预测
            "leader": self.get_leader_signals(),
            "timestamp": datetime.now().isoformat()
        }


if __name__ == "__main__":
    # 测试
    provider = MarketDataProvider()
    tools = BeidouSevenTools()
    
    print("=== BTC Signal ===")
    btc = provider.get_tool_signal("BTCUSDT")
    print(f"Price: ${btc['price']:,.2f}")
    print(f"Trend: {btc['trend']} ({btc['trend_strength']})")
    print(f"RSI: {btc['rsi']} ({btc['rsi_signal']})")
    print(f"MACD: {btc['macd']}")
    print(f"Signal: {btc['overall_signal']} ({btc['confidence']})")
    print(f"Regime: {btc['market_regime']}")
    
    print("\n=== Tool Signals ===")
    all_signals = tools.get_all_signals()
    for tool, signals in all_signals.items():
        if tool == "timestamp":
            continue
        print(f"\n{tool}:")
        for s in signals[:3]:
            print(f"  {s.get('symbol', '')} {s.get('action', '')}")
