#!/usr/bin/env python3
"""
📈 GO2SE 模拟交易引擎 V2
=======================
支持做多做空双向模拟
实时盈亏计算
7大工具信号模拟
"""

import time
import random
import math
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque

# ─── 数据类 ───────────────────────────────────────────────

@dataclass
class SimPosition:
    """模拟持仓"""
    position_id: str
    symbol: str
    side: str          # LONG / SHORT
    entry_price: float
    quantity: float
    leverage: int = 1
    stop_loss: float = 0
    take_profit: float = 0
    timestamp: str = ""
    tool: str = ""       # rabbit/mole/oracle/etc
    pnl: float = 0
    pnl_pct: float = 0

@dataclass
class SimOrder:
    """模拟订单"""
    order_id: str
    symbol: str
    side: str           # BUY / SELL
    position_side: str    # LONG / SHORT
    quantity: float
    price: float
    leverage: int
    fee: float
    timestamp: str
    status: str          # pending/filled/cancelled

@dataclass
class SimTrade:
    """模拟交易记录"""
    trade_id: str
    symbol: str
    side: str            # OPEN / CLOSE
    direction: str        # LONG / SHORT
    entry_price: float
    exit_price: float
    quantity: float
    pnl: float
    pnl_pct: float
    tool: str
    timestamp: str
    hold_duration: int    # 秒

# ─── 模拟市场数据 ──────────────────────────────────────

class SimMarketData:
    """模拟实时行情"""

    PRICES = {
        "BTCUSDT": 75000,
        "ETHUSDT": 3500,
        "SOLUSDT": 180,
        "BNBUSDT": 620,
        "XRPUSDT": 0.62,
        "DOGEUSDT": 0.15,
        "ADAUSDT": 0.48,
        "AVAXUSDT": 38,
    }

    def __init__(self):
        self.prices = self.PRICES.copy()
        self._prices_history: Dict[str, deque] = {
            s: deque(maxlen=100) for s in self.prices
        }
        for s, p in self.prices.items():
            for i in range(100):
                self._prices_history[s].append(p * (1 + random.uniform(-0.001, 0.001)))

    def get_ticker(self, symbol: str) -> Dict:
        """获取实时行情"""
        if symbol not in self.prices:
            symbol = "BTCUSDT"

        price = self.prices[symbol]
        # 模拟小幅波动
        change_pct = random.uniform(-0.002, 0.002)
        self.prices[symbol] *= (1 + change_pct)
        price = self.prices[symbol]

        history = list(self._prices_history[symbol])
        history.append(price)
        self._prices_history[symbol].append(price)

        # 计算RSI
        rsi = self._calc_rsi(history)
        # 计算波动率
        volatility = self._calc_volatility(history)
        # 计算成交量
        volume = random.uniform(1e8, 5e8)

        return {
            "symbol": symbol,
            "price": round(price, 4),
            "change_24h": round(random.uniform(-5, 5), 2),
            "change_1h": round(random.uniform(-2, 2), 2),
            "volume_24h": round(volume, 0),
            "rsi": round(rsi, 1),
            "volatility": round(volatility, 4),
            "bid": round(price * 0.9998, 4),
            "ask": round(price * 1.0002, 4),
            "high_24h": round(price * 1.02, 4),
            "low_24h": round(price * 0.98, 4),
        }

    def _calc_rsi(self, prices: List[float], period: int = 14) -> float:
        if len(prices) < period + 1:
            return 50.0
        gains = []
        losses = []
        for i in range(1, min(len(prices), period + 1)):
            diff = prices[-i] - prices[-i-1]
            if diff > 0:
                gains.append(diff)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(diff))
        avg_gain = sum(gains) / period if gains else 0.01
        avg_loss = sum(losses) / period if losses else 0.01
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def _calc_volatility(self, prices: List[float], period: int = 20) -> float:
        if len(prices) < period:
            return 0.02
        recent = prices[-period:]
        returns = [math.log(recent[i]/recent[i-1]) for i in range(1, period)]
        mean = sum(returns) / len(returns)
        variance = sum((r - mean)**2 for r in returns) / len(returns)
        return math.sqrt(variance * 252)  # 年化波动率

    def get_all_tickers(self) -> List[Dict]:
        return [self.get_ticker(s) for s in self.PRICES]


# ─── 模拟交易引擎 ──────────────────────────────────────

class SimTradingEngine:
    """
    📈 模拟交易引擎
    支持做多/做空
    实时盈亏计算
    """

    def __init__(self, initial_balance: float = 100000):
        self.balance = initial_balance          # 模拟资金
        self.initial_balance = initial_balance
        self.positions: Dict[str, SimPosition] = {}  # symbol -> position
        self.orders: List[SimOrder] = []
        self.trades: List[SimTrade] = []
        self.market = SimMarketData()
        self._order_counter = 0
        self._trade_counter = 0

    # ─── 核心方法 ────────────────────────────────────

    def open_position(
        self,
        symbol: str,
        side: str,         # LONG / SHORT
        quantity: float,
        leverage: int = 1,
        stop_loss: float = 0,
        take_profit: float = 0,
        tool: str = "manual"
    ) -> SimOrder:
        """开仓"""
        ticker = self.market.get_ticker(symbol)
        price = ticker["price"]

        # 计算手续费
        fee = quantity * price * 0.001

        # 保证金检查
        required_margin = (quantity * price) / leverage
        if required_margin > self.balance:
            raise ValueError(f"余额不足: 需要 {required_margin:.2f}, 账户 {self.balance:.2f}")

        # 仓位限制（总仓位不超过80%）
        total_exposure = sum(
            p.quantity * p.entry_price / p.leverage
            for p in self.positions.values()
        )
        max_exposure = self.initial_balance * 0.8
        if total_exposure + required_margin > max_exposure:
            raise ValueError(f"仓位超限: 当前暴露 {total_exposure:.2f}, 上限 {max_exposure:.2f}")

        # 冻结保证金
        self.balance -= required_margin

        # 创建持仓
        position_id = f"POS_{int(time.time())}_{symbol}"
        self.positions[symbol] = SimPosition(
            position_id=position_id,
            symbol=symbol,
            side=side,
            entry_price=price,
            quantity=quantity,
            leverage=leverage,
            stop_loss=stop_loss,
            take_profit=take_profit,
            timestamp=datetime.now().isoformat(),
            tool=tool
        )

        # 创建订单
        self._order_counter += 1
        order = SimOrder(
            order_id=f"SIM_{self._order_counter:06d}",
            symbol=symbol,
            side="BUY" if side == "LONG" else "SELL",
            position_side=side,
            quantity=quantity,
            price=price,
            leverage=leverage,
            fee=fee,
            timestamp=datetime.now().isoformat(),
            status="filled"
        )
        self.orders.insert(0, order)
        self.trades.insert(0, SimTrade(
            trade_id=order.order_id,
            symbol=symbol,
            side="OPEN",
            direction=side,
            entry_price=price,
            exit_price=price,
            quantity=quantity,
            pnl=0,
            pnl_pct=0,
            tool=tool,
            timestamp=order.timestamp,
            hold_duration=0
        ))

        return order

    def close_position(self, symbol: str) -> SimOrder:
        """平仓"""
        if symbol not in self.positions:
            raise ValueError(f"无持仓: {symbol}")

        pos = self.positions[symbol]
        ticker = self.market.get_ticker(symbol)
        price = ticker["price"]
        fee = pos.quantity * price * 0.001

        # 计算盈亏
        if pos.side == "LONG":
            pnl = (price - pos.entry_price) * pos.quantity - fee
            pnl_pct = (price / pos.entry_price - 1) * 100 * pos.leverage
        else:  # SHORT
            pnl = (pos.entry_price - price) * pos.quantity - fee
            pnl_pct = (pos.entry_price / price - 1) * 100 * pos.leverage

        # 释放保证金 + 盈亏
        released_margin = (pos.quantity * pos.entry_price) / pos.leverage
        self.balance += released_margin + pnl

        # 更新订单
        self._order_counter += 1
        close_side = "SELL" if pos.side == "LONG" else "BUY"
        order = SimOrder(
            order_id=f"SIM_{self._order_counter:06d}",
            symbol=symbol,
            side=close_side,
            position_side=pos.side,
            quantity=pos.quantity,
            price=price,
            leverage=pos.leverage,
            fee=fee,
            timestamp=datetime.now().isoformat(),
            status="filled"
        )
        self.orders.insert(0, order)

        # 记录平仓交易
        entry_time = datetime.fromisoformat(pos.timestamp)
        hold_secs = int((datetime.now() - entry_time).total_seconds())
        self._trade_counter += 1
        self.trades.insert(0, SimTrade(
            trade_id=f"TRADE_{self._trade_counter:06d}",
            symbol=symbol,
            side="CLOSE",
            direction=pos.side,
            entry_price=pos.entry_price,
            exit_price=price,
            quantity=pos.quantity,
            pnl=round(pnl, 2),
            pnl_pct=round(pnl_pct, 2),
            tool=pos.tool,
            timestamp=order.timestamp,
            hold_duration=hold_secs
        ))

        # 清除持仓
        del self.positions[symbol]

        return order

    def check_positions(self) -> List[Dict]:
        """检查所有持仓，触发止损止盈"""
        closed = []
        for symbol in list(self.positions.keys()):
            pos = self.positions[symbol]
            ticker = self.market.get_ticker(symbol)
            price = ticker["price"]

            # 计算浮动盈亏
            if pos.side == "LONG":
                pos.pnl = (price - pos.entry_price) * pos.quantity
                pos.pnl_pct = (price / pos.entry_price - 1) * 100 * pos.leverage
            else:
                pos.pnl = (pos.entry_price - price) * pos.quantity
                pos.pnl_pct = (pos.entry_price / price - 1) * 100 * pos.leverage

            # 检查止损
            if pos.stop_loss > 0:
                if pos.side == "LONG" and price <= pos.stop_loss:
                    closed.append(self.close_position(symbol))
                elif pos.side == "SHORT" and price >= pos.stop_loss:
                    closed.append(self.close_position(symbol))

            # 检查止盈
            if pos.take_profit > 0:
                if pos.side == "LONG" and price >= pos.take_profit:
                    closed.append(self.close_position(symbol))
                elif pos.side == "SHORT" and price <= pos.take_profit:
                    closed.append(self.close_position(symbol))

        return closed

    # ─── 查询方法 ────────────────────────────────────

    def get_portfolio(self) -> Dict:
        """获取投资组合"""
        total_pnl = sum(p.pnl for p in self.positions.values())
        total_value = self.balance + sum(
            (p.quantity * p.entry_price / p.leverage) for p in self.positions.values()
        ) + total_pnl

        positions_data = []
        for pos in self.positions.values():
            ticker = self.market.get_ticker(pos.symbol)
            positions_data.append({
                "symbol": pos.symbol,
                "side": pos.side,
                "entry_price": pos.entry_price,
                "current_price": ticker["price"],
                "quantity": pos.quantity,
                "leverage": pos.leverage,
                "pnl": round(pos.pnl, 2),
                "pnl_pct": round(pos.pnl_pct, 2),
                "tool": pos.tool,
                "timestamp": pos.timestamp,
                "stop_loss": pos.stop_loss,
                "take_profit": pos.take_profit,
            })

        return {
            "balance": round(self.balance, 2),
            "total_pnl": round(total_pnl, 2),
            "total_value": round(total_value, 2),
            "total_pnl_pct": round((total_value / self.initial_balance - 1) * 100, 2),
            "positions": positions_data,
            "position_count": len(self.positions),
        }

    def get_trades(self, limit: int = 50) -> List[Dict]:
        """获取交易历史"""
        return [
            {
                "trade_id": t.trade_id,
                "symbol": t.symbol,
                "side": t.side,
                "direction": t.direction,
                "entry_price": t.entry_price,
                "exit_price": t.exit_price,
                "quantity": t.quantity,
                "pnl": t.pnl,
                "pnl_pct": t.pnl_pct,
                "tool": t.tool,
                "timestamp": t.timestamp,
                "hold_duration": f"{t.hold_duration // 60}分" if t.hold_duration > 60 else f"{t.hold_duration}秒"
            }
            for t in self.trades[:limit]
        ]

    def get_orders(self, limit: int = 20) -> List[Dict]:
        """获取订单历史"""
        return [
            {
                "order_id": o.order_id,
                "symbol": o.symbol,
                "side": o.side,
                "position_side": o.position_side,
                "quantity": o.quantity,
                "price": o.price,
                "leverage": o.leverage,
                "fee": round(o.fee, 2),
                "status": o.status,
                "timestamp": o.timestamp,
            }
            for o in self.orders[:limit]
        ]

    def get_stats(self) -> Dict:
        """统计摘要"""
        closed_trades = [t for t in self.trades if t.side == "CLOSE"]
        if closed_trades:
            total_pnl = sum(t.pnl for t in closed_trades)
            win_trades = [t for t in closed_trades if t.pnl > 0]
            win_rate = len(win_trades) / len(closed_trades) * 100
            avg_win = sum(t.pnl for t in win_trades) / len(win_trades) if win_trades else 0
            avg_loss = sum(t.pnl for t in closed_trades if t.pnl < 0) / (len(closed_trades) - len(win_trades)) if len(closed_trades) > len(win_trades) else 0
        else:
            total_pnl = 0
            win_rate = 0
            avg_win = 0
            avg_loss = 0

        return {
            "total_trades": len(closed_trades),
            "open_positions": len(self.positions),
            "total_pnl": round(total_pnl, 2),
            "win_rate": round(win_rate, 1),
            "avg_win": round(avg_win, 2),
            "avg_loss": round(avg_loss, 2),
            "profit_factor": round(abs(avg_win / avg_loss), 2) if avg_loss != 0 else 0,
            "balance": round(self.balance, 2),
            "total_value": round(self.balance + sum(p.pnl for p in self.positions.values()), 2),
        }


# ─── 全局实例 ──────────────────────────────────────

_sim_engine: Optional[SimTradingEngine] = None

def get_sim_engine() -> SimTradingEngine:
    global _sim_engine
    if _sim_engine is None:
        _sim_engine = SimTradingEngine(initial_balance=100000)
    return _sim_engine
