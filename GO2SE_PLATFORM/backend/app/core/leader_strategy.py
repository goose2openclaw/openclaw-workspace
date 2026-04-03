"""
👑 跟大哥策略 (Leader Strategy)
================================
做多做空双向跟随策略

功能:
- 识别大户/机构方向
- 做多/做空双向跟随
- 动态止损止盈
- 仓位管理

适用市场:
- 加密货币 (币安/Bybit/OKX)
- 跟单做市协作
"""

import json
import time
import urllib.request
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import deque
import statistics
import logging

logger = logging.getLogger(__name__)

BINANCE_API = "https://api.binance.com/api/v3"


@dataclass
class OrderFlow:
    """订单流数据"""
    timestamp: datetime
    price: float
    volume: float
    side: str  # BUY / SELL
    is_whale: bool  # 是否大户


@dataclass
class LeaderSignal:
    """跟大哥信号"""
    symbol: str
    direction: str  # LONG / SHORT
    confidence: float  # 0.0 - 1.0
    entry_price: float
    stop_loss: float
    take_profit: float
    position_size: float
    reason: str
    whale_ratio: float = 0.0  # 大户买卖比率
    timestamp: datetime = field(default_factory=datetime.now)


class LeaderStrategy:
    """
    跟大哥策略
    ==========
    
    核心理念:
    1. 追踪大户订单流
    2. 跟随机构方向
    3. 做多做空双向
    4. 严格止损
    
    指标:
    - 订单簿失衡 (OBP)
    - 成交量加权价格 (VWAP)
    - 大户交易检测
    - 趋势确认
    """
    
    def __init__(self, 
                 symbol: str = "BTCUSDT",
                 interval: str = "1h",
                 whale_threshold: float = 100000.0,  # 大户门槛 USDT
                 position_size_pct: float = 0.15,     # 仓位15%
                 stop_loss_pct: float = 0.03,         # 止损3%
                 take_profit_pct: float = 0.06):       # 止盈6%
        
        self.symbol = symbol
        self.interval = interval
        self.whale_threshold = whale_threshold
        self.position_size_pct = position_size_pct
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        
        # 数据缓存
        self.order_flow: deque = deque(maxlen=1000)
        self.price_history: deque = deque(maxlen=100)
        self.volume_history: deque = deque(maxlen=100)
        
        # 状态
        self.position = 0  # 0 = 无仓位, 1 = 多, -1 = 空
        self.entry_price = 0
        self.signals: List[LeaderSignal] = []
    
    def fetch_recent_trades(self) -> List[Dict]:
        """获取最近成交"""
        url = f"{BINANCE_API}/trades?symbol={self.symbol}&limit=100"
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read())
                return [
                    {
                        "id": t["id"],
                        "price": float(t["price"]),
                        "qty": float(t["qty"]),
                        "time": datetime.fromtimestamp(t["time"] / 1000),
                        "is_buyer_maker": t["isBuyerMaker"]
                    }
                    for t in data
                ]
        except Exception as e:
            logger.error(f"获取成交失败: {e}")
            return []
    
    def fetch_klines(self, limit: int = 100) -> List[Dict]:
        """获取K线数据"""
        url = f"{BINANCE_API}/klines?symbol={self.symbol}&interval={self.interval}&limit={limit}"
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read())
                return [
                    {
                        "open_time": datetime.fromtimestamp(d[0] / 1000),
                        "open": float(d[1]),
                        "high": float(d[2]),
                        "low": float(d[3]),
                        "close": float(d[4]),
                        "volume": float(d[5]),
                    }
                    for d in data
                ]
        except Exception as e:
            logger.error(f"获取K线失败: {e}")
            return []
    
    def analyze_order_flow(self) -> Dict:
        """分析订单流"""
        trades = self.fetch_recent_trades()
        if not trades:
            return {"direction": "NEUTRAL", "confidence": 0.0}
        
        buy_volume = 0.0
        sell_volume = 0.0
        whale_buy = 0.0
        whale_sell = 0.0
        
        for t in trades:
            volume_usdt = t["price"] * t["qty"]
            is_whale = volume_usdt >= self.whale_threshold
            
            if t["is_buyer_maker"]:
                # 卖方主动 (价格下跌)
                sell_volume += volume_usdt
                if is_whale:
                    whale_sell += volume_usdt
            else:
                # 买方主动 (价格上涨)
                buy_volume += volume_usdt
                if is_whale:
                    whale_buy += volume_usdt
        
        total_volume = buy_volume + sell_volume
        if total_volume == 0:
            return {"direction": "NEUTRAL", "confidence": 0.0}
        
        # 计算大户比率
        total_whale = whale_buy + whale_sell
        whale_ratio = total_whale / total_volume if total_volume > 0 else 0
        
        # 方向判断
        buy_pct = buy_volume / total_volume
        sell_pct = sell_volume / total_volume
        
        imbalance = buy_pct - sell_pct  # -1 到 1
        
        if imbalance > 0.1:
            direction = "LONG"
            confidence = min(0.9, 0.5 + imbalance)
        elif imbalance < -0.1:
            direction = "SHORT"
            confidence = min(0.9, 0.5 + abs(imbalance))
        else:
            direction = "NEUTRAL"
            confidence = 0.5
        
        return {
            "direction": direction,
            "confidence": confidence,
            "buy_volume": buy_volume,
            "sell_volume": sell_volume,
            "buy_pct": buy_pct * 100,
            "sell_pct": sell_pct * 100,
            "whale_ratio": whale_ratio,
            "whale_buy": whale_buy,
            "whale_sell": whale_sell,
            "imbalance": imbalance
        }
    
    def calculate_vwap(self, klines: List[Dict]) -> float:
        """计算VWAP"""
        if not klines:
            return 0.0
        
        total_pv = sum(k["close"] * k["volume"] for k in klines)
        total_vol = sum(k["volume"] for k in klines)
        
        return total_pv / total_vol if total_vol > 0 else 0.0
    
    def calculate_ema(self, prices: List[float], period: int = 20) -> float:
        """计算EMA"""
        if len(prices) < period:
            return prices[-1] if prices else 0.0
        
        multiplier = 2 / (period + 1)
        ema = sum(prices[:period]) / period
        
        for price in prices[period:]:
            ema = (price - ema) * multiplier + ema
        
        return ema
    
    def detect_trend(self, klines: List[Dict]) -> Tuple[str, float]:
        """检测趋势"""
        if len(klines) < 50:
            return "NEUTRAL", 0.5
        
        closes = [k["close"] for k in klines]
        
        # 多周期EMA
        ema9 = self.calculate_ema(closes, 9)
        ema21 = self.calculate_ema(closes, 21)
        ema55 = self.calculate_ema(closes, 55)
        
        current = closes[-1]
        
        # 趋势判断
        if ema9 > ema21 > ema55 and current > ema9:
            return "LONG", min(0.9, 0.6 + (ema9 - ema55) / ema55)
        elif ema9 < ema21 < ema55 and current < ema9:
            return "SHORT", min(0.9, 0.6 + (ema55 - ema9) / ema55)
        else:
            return "NEUTRAL", 0.5
    
    def generate_signal(self) -> Optional[LeaderSignal]:
        """生成跟大哥信号"""
        # 获取数据
        order_flow = self.analyze_order_flow()
        klines = self.fetch_klines(limit=100)
        
        if not klines:
            return None
        
        current_price = klines[-1]["close"]
        
        # 趋势检测
        trend, trend_conf = self.detect_trend(klines)
        
        # 综合信号
        direction = order_flow["direction"]
        confidence = (order_flow["confidence"] * 0.6 + trend_conf * 0.4)
        
        # 如果趋势和订单流一致，增加置信度
        if (direction == "LONG" and trend == "LONG") or (direction == "SHORT" and trend == "SHORT"):
            confidence *= 1.2
        
        confidence = min(1.0, confidence)
        
        # 过滤低置信度信号
        if confidence < 0.6 or direction == "NEUTRAL":
            return None
        
        # 计算止损止盈
        if direction == "LONG":
            stop_loss = current_price * (1 - self.stop_loss_pct)
            take_profit = current_price * (1 + self.take_profit_pct)
        else:
            stop_loss = current_price * (1 + self.stop_loss_pct)
            take_profit = current_price * (1 - self.take_profit_pct)
        
        signal = LeaderSignal(
            symbol=self.symbol,
            direction=direction,
            confidence=confidence,
            entry_price=current_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            position_size=self.position_size_pct,
            reason=f"订单流:{order_flow['direction']} + 趋势:{trend}",
            whale_ratio=order_flow.get("whale_ratio", 0.0)
        )
        
        self.signals.append(signal)
        return signal
    
    def check_exit(self, current_price: float) -> Tuple[bool, str]:
        """检查是否需要平仓"""
        if self.position == 0:
            return False, ""
        
        if self.position == 1:  # 多头
            pnl_pct = (current_price - self.entry_price) / self.entry_price
            
            if current_price <= self.entry_price * (1 - self.stop_loss_pct):
                return True, "STOP_LOSS"
            elif current_price >= self.entry_price * (1 + self.take_profit_pct):
                return True, "TAKE_PROFIT"
        
        elif self.position == -1:  # 空头
            pnl_pct = (self.entry_price - current_price) / self.entry_price
            
            if current_price >= self.entry_price * (1 + self.stop_loss_pct):
                return True, "STOP_LOSS"
            elif current_price <= self.entry_price * (1 - self.take_profit_pct):
                return True, "TAKE_PROFIT"
        
        return False, ""
    
    def execute_signal(self, signal: LeaderSignal) -> Dict:
        """执行信号"""
        if signal.direction == "LONG":
            self.position = 1
        else:
            self.position = -1
        
        self.entry_price = signal.entry_price
        
        return {
            "action": "OPEN",
            "direction": signal.direction,
            "entry_price": signal.entry_price,
            "stop_loss": signal.stop_loss,
            "take_profit": signal.take_profit,
            "position_size": signal.position_size,
            "confidence": signal.confidence,
            "timestamp": datetime.now().isoformat()
        }
    
    def run_cycle(self) -> Dict:
        """运行一个交易周期"""
        result = {
            "symbol": self.symbol,
            "timestamp": datetime.now().isoformat(),
            "action": "HOLD",
            "position": self.position,
            "entry_price": self.entry_price,
            "signal": None
        }
        
        # 检查是否需要平仓
        klines = self.fetch_klines(limit=1)
        if klines and self.position != 0:
            current_price = klines[-1]["close"]
            should_exit, reason = self.check_exit(current_price)
            
            if should_exit:
                result["action"] = "CLOSE"
                result["exit_reason"] = reason
                result["exit_price"] = current_price
                result["pnl_pct"] = (
                    (current_price - self.entry_price) / self.entry_price * self.position
                    if self.position != 0 else 0
                )
                self.position = 0
                self.entry_price = 0
                return result
        
        # 生成新信号
        signal = self.generate_signal()
        if signal and self.position == 0:
            exec_result = self.execute_signal(signal)
            result["action"] = exec_result["action"]
            result["signal"] = exec_result
            result["entry_price"] = signal.entry_price
        
        return result
    
    def get_status(self) -> Dict:
        """获取策略状态"""
        return {
            "symbol": self.symbol,
            "position": self.position,
            "entry_price": self.entry_price,
            "position_size_pct": self.position_size_pct,
            "stop_loss_pct": self.stop_loss_pct,
            "take_profit_pct": self.take_profit_pct,
            "whale_threshold": self.whale_threshold,
            "signals_count": len(self.signals),
            "last_signal": self.signals[-1].__dict__ if self.signals else None
        }


class LeaderMultiStrategy:
    """
    多标的跟大哥策略
    =================
    同时管理多个标的的跟大哥策略
    """
    
    def __init__(self):
        self.strategies: Dict[str, LeaderStrategy] = {}
        self.default_config = {
            "whale_threshold": 100000.0,
            "position_size_pct": 0.15,
            "stop_loss_pct": 0.03,
            "take_profit_pct": 0.06
        }
    
    def add_symbol(self, symbol: str, config: Dict = None) -> LeaderStrategy:
        """添加标的"""
        cfg = {**self.default_config, **(config or {})}
        strategy = LeaderStrategy(
            symbol=symbol,
            whale_threshold=cfg["whale_threshold"],
            position_size_pct=cfg["position_size_pct"],
            stop_loss_pct=cfg["stop_loss_pct"],
            take_profit_pct=cfg["take_profit_pct"]
        )
        self.strategies[symbol] = strategy
        logger.info(f"添加跟大哥策略: {symbol}")
        return strategy
    
    def remove_symbol(self, symbol: str) -> bool:
        """移除标的"""
        if symbol in self.strategies:
            del self.strategies[symbol]
            logger.info(f"移除跟大哥策略: {symbol}")
            return True
        return False
    
    def run_all(self) -> Dict:
        """运行所有策略"""
        results = {}
        for symbol, strategy in self.strategies.items():
            results[symbol] = strategy.run_cycle()
        return results
    
    def get_total_exposure(self) -> float:
        """获取总敞口"""
        total = 0.0
        for strategy in self.strategies.values():
            if strategy.position != 0:
                total += strategy.position_size_pct
        return total
    
    def get_status(self) -> Dict:
        """获取总状态"""
        return {
            "symbols_count": len(self.strategies),
            "total_exposure": self.get_total_exposure(),
            "strategies": {
                symbol: s.get_status() 
                for symbol, s in self.strategies.items()
            }
        }


# 全局实例
leader_multi_strategy = LeaderMultiStrategy()

# 默认添加主流币
leader_multi_strategy.add_symbol("BTCUSDT")
leader_multi_strategy.add_symbol("ETHUSDT")


if __name__ == "__main__":
    print("=" * 60)
    print("👑 跟大哥策略 - 多空双向跟随")
    print("=" * 60)
    
    # 单标的测试
    strategy = LeaderStrategy("BTCUSDT")
    
    # 获取信号
    signal = strategy.generate_signal()
    if signal:
        print(f"\n📊 信号:")
        print(f"   方向: {signal.direction}")
        print(f"   置信度: {signal.confidence:.2%}")
        print(f"   入场价: ${signal.entry_price:,.2f}")
        print(f"   止损: ${signal.stop_loss:,.2f}")
        print(f"   止盈: ${signal.take_profit:,.2f}")
        print(f"   大户比率: {signal.whale_ratio:.2%}")
    else:
        print("\n⚠️  当前无信号")
    
    # 多标的状态
    print(f"\n📈 多标的状态:")
    status = leader_multi_strategy.get_status()
    print(f"   标的数: {status['symbols_count']}")
    print(f"   总敞口: {status['total_exposure']:.1%}")
