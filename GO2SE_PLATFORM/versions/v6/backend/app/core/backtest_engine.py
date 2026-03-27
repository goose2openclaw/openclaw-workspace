#!/usr/bin/env python3
"""
🪿 GO2SE 实际回测引擎
从理论预期转变为实际模拟回测
"""

import json
import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class Candle:
    """K线数据"""
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass
class Trade:
    """交易记录"""
    id: int
    timestamp: str
    symbol: str
    side: str  # buy/sell
    price: float
    quantity: float
    value: float
    fee: float
    pnl: float = 0.0
    strategy: str = ""


@dataclass
class Position:
    """持仓"""
    symbol: str
    quantity: float
    entry_price: float
    side: str = "long"
    
    
    def get_value(self, current_price: float = None) -> float:
        return self.quantity * (current_price or self.entry_price)
    
    
    def get_pnl(self, current_price: float = None) -> float:
        if self.side == "long":
            return (current_price - self.entry_price) * self.quantity
        else:
            return (self.entry_price - current_price) * self.quantity


class BacktestEngine:
    """实际回测引擎"""
    
    def __init__(self, initial_cash: float = 100000, fee_rate: float = 0.001):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.fee_rate = fee_rate
        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
        self.equity_curve: List[Dict] = []
        self.trade_id = 0
        self.closed_trades: List[Trade] = []
        
    def generate_market_data(self, symbol: str, days: int, 
                            trend: str = "random", volatility: float = 0.02) -> List[Candle]:
        """生成市场数据 - 模拟真实市场"""
        data = []
        
        # 基准价格
        base_prices = {
            "BTC/USDT": 75000, "ETH/USDT": 1850, "BNB/USDT": 580,
            "XRP/USDT": 2.45, "SOL/USDT": 145, "ADA/USDT": 0.85,
            "DOGE/USDT": 0.32, "DOT/USDT": 18.5, "AVAX/USDT": 42
        }
        base = base_prices.get(symbol, 1000)
        
        now = datetime.now()
        
        # 趋势参数
        trend_bias = 0.0002 if trend == "bull" else -0.0002 if trend == "bear" else 0
        
        for i in range(days * 24):  # 小时数据
            ts = now - timedelta(hours=days * 24 - i)
            
            # 价格随机游走 + 趋势偏置
            change = random.gauss(trend_bias, volatility)
            base *= (1 + change)
            
            # 生成OHLC
            spread = base * random.uniform(0.001, 0.005)
            open_p = base
            high = base + spread * random.uniform(0.5, 1.5)
            low = base - spread * random.uniform(0.5, 1.5)
            close = base
            volume = random.uniform(100, 1000)
            
            data.append(Candle(
                timestamp=ts.isoformat(),
                open=round(open_p, 2),
                high=round(high, 2),
                low=round(low, 2),
                close=round(close, 2),
                volume=round(volume, 2)
            ))
        
        return data
    
    def calculate_indicators(self, candles: List[Candle]) -> Dict:
        """计算技术指标"""
        closes = [c.close for c in candles]
        
        return {
            "rsi_14": self._rsi(closes, 14),
            "rsi_7": self._rsi(closes, 7),
            "ema_12": self._ema(closes, 12),
            "ema_26": self._ema(closes, 26),
            "macd": self._macd(closes),
            "bb_upper": self._bollinger(closes, 20)[0],
            "bb_middle": self._bollinger(closes, 20)[1],
            "bb_lower": self._bollinger(closes, 20)[2],
            "atr": self._atr(candles, 14),
            "stoch_k": self._stochastic(candles, 14)[0],
            "stoch_d": self._stochastic(candles, 14)[1],
        }
    
    def _rsi(self, closes: List[float], period: int = 14) -> float:
        if len(closes) < period + 1:
            return 50.0
        deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
        gains = [d if d > 0 else 0 for d in deltas[-period:]]
        losses = [-d if d < 0 else 0 for d in deltas[-period:]]
        avg_gain = sum(gains) / period or 0.0001
        avg_loss = sum(losses) / period or 0.0001
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    def _ema(self, closes: List[float], period: int) -> float:
        if len(closes) < period:
            return closes[-1] if closes else 0
        multiplier = 2 / (period + 1)
        ema = sum(closes[:period]) / period
        for price in closes[period:]:
            ema = (price - ema) * multiplier + ema
        return ema
    
    def _macd(self, closes: List[float]) -> Tuple[float, float, float]:
        ema12 = self._ema(closes, 12)
        ema26 = self._ema(closes, 26)
        macd_line = ema12 - ema26
        signal_line = macd_line  # 简化
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram
    
    def _bollinger(self, closes: List[float], period: int = 20) -> Tuple[float, float, float]:
        if len(closes) < period:
            return closes[-1], closes[-1], closes[-1]
        sma = sum(closes[-period:]) / period
        variance = sum((c - sma) ** 2 for c in closes[-period:]) / period
        std = variance ** 0.5
        return sma + 2 * std, sma, sma - 2 * std
    
    def _atr(self, candles: List[Candle], period: int = 14) -> float:
        if len(candles) < period:
            return 0
        ranges = []
        for c in candles[-period:]:
            tr = max(c.high - c.low, 
                    abs(c.high - c.close), 
                    abs(c.low - c.close))
            ranges.append(tr)
        return sum(ranges) / period
    
    def _stochastic(self, candles: List[Candle], period: int = 14) -> Tuple[float, float]:
        if len(candles) < period:
            return 50, 50
        recent = candles[-period:]
        high = max(c.high for c in recent)
        low = min(c.low for c in recent)
        close = recent[-1].close
        k = 100 * (close - low) / (high - low) if high != low else 50
        return k, k  # 简化
    
    # ==================== 策略实现 ====================
    
    def strategy_rsi(self, candles: List[Candle], oversold: int = 30, 
                    overbought: int = 70) -> str:
        """RSI均值回归策略"""
        ind = self.calculate_indicators(candles)
        rsi = ind["rsi_14"]
        
        if rsi < oversold:
            return "buy"
        elif rsi > overbought:
            return "sell"
        return "hold"
    
    def strategy_macd(self, candles: List[Candle]) -> str:
        """MACD趋势策略"""
        ind = self.calculate_indicators(candles)
        macd, signal, hist = ind["macd"]
        
        if hist > 0 and macd > signal:
            return "buy"
        elif hist < 0 and macd < signal:
            return "sell"
        return "hold"
    
    def strategy_bollinger(self, candles: List[Candle]) -> str:
        """布林带策略"""
        ind = self.calculate_indicators(candles)
        close = candles[-1].close
        
        if close < ind["bb_lower"]:
            return "buy"
        elif close > ind["bb_upper"]:
            return "sell"
        return "hold"
    
    def strategy_multi_indicator(self, candles: List[Candle]) -> Tuple[str, float]:
        """多指标综合策略"""
        ind = self.calculate_indicators(candles)
        
        score = 0
        # RSI
        if ind["rsi_14"] < 30:
            score += 2
        elif ind["rsi_14"] > 70:
            score -= 2
        elif ind["rsi_14"] < 40:
            score += 1
        elif ind["rsi_14"] > 60:
            score -= 1
        
        # MACD
        macd, signal, hist = ind["macd"]
        if hist > 0:
            score += 1
        else:
            score -= 1
        
        # 布林带
        if candles[-1].close < ind["bb_lower"]:
            score += 1
        elif candles[-1].close > ind["bb_upper"]:
            score -= 1
        
        confidence = min(abs(score) / 5, 1.0)
        
        if score >= 2:
            return "buy", confidence
        elif score <= -2:
            return "sell", confidence
        return "hold", confidence
    
    # ==================== 交易执行 ====================
    
    def execute_buy(self, symbol: str, quantity: float, price: float, 
                   strategy: str = "", timestamp: str = None) -> bool:
        """买入"""
        cost = quantity * price
        fee = cost * self.fee_rate
        
        if self.cash < cost + fee:
            return False
        
        self.cash -= (cost + fee)
        
        if symbol in self.positions:
            pos = self.positions[symbol]
            total_q = pos.quantity + quantity
            total_cost = pos.quantity * pos.entry_price + cost
            pos.quantity = total_q
            pos.entry_price = total_cost / total_q
        else:
            self.positions[symbol] = Position(
                symbol=symbol,
                quantity=quantity,
                entry_price=price,
                side="long"
            )
        
        self.trade_id += 1
        self.trades.append(Trade(
            id=self.trade_id,
            timestamp=timestamp or datetime.now().isoformat(),
            symbol=symbol,
            side="buy",
            price=price,
            quantity=quantity,
            value=cost,
            fee=fee,
            strategy=strategy
        ))
        
        return True
    
    def execute_sell(self, symbol: str, quantity: float, price: float,
                    strategy: str = "", timestamp: str = None) -> Tuple[bool, float]:
        """卖出 - 返回成功与否和盈亏"""
        if symbol not in self.positions:
            return False, 0
        
        pos = self.positions[symbol]
        if quantity > pos.quantity:
            quantity = pos.quantity
        
        revenue = quantity * price
        fee = revenue * self.fee_rate
        pnl = pos.get_pnl(price) * quantity / pos.quantity - fee
        
        self.cash += (revenue - fee)
        pos.quantity -= quantity
        
        if pos.quantity <= 0:
            del self.positions[symbol]
        
        self.trade_id += 1
        trade = Trade(
            id=self.trade_id,
            timestamp=timestamp or datetime.now().isoformat(),
            symbol=symbol,
            side="sell",
            price=price,
            quantity=quantity,
            value=revenue,
            fee=fee,
            pnl=pnl,
            strategy=strategy
        )
        self.trades.append(trade)
        self.closed_trades.append(trade)
        
        return True, pnl
    
    def liquidate(self, symbol: str, price: float, strategy: str = "") -> bool:
        """清仓"""
        if symbol in self.positions:
            qty = self.positions[symbol].quantity
            return self.execute_sell(symbol, qty, price, strategy)[0]
        return False
    
    def update_equity(self, prices: Dict[str, float], timestamp: str):
        """更新权益曲线"""
        pos_value = 0
        for sym, pos in self.positions.items():
            if sym in prices:
                pos_value += pos.get_value(prices[sym])
        
        self.equity_curve.append({
            "timestamp": timestamp,
            "equity": round(self.cash + pos_value, 2),
            "cash": round(self.cash, 2),
            "positions_value": round(pos_value, 2)
        })
    
    def get_total_equity(self, prices: Dict[str, float] = None) -> float:
        """获取总权益"""
        pos_value = 0
        for sym, pos in self.positions.items():
            price = prices.get(sym, pos.entry_price) if prices else pos.entry_price
            pos_value += pos.get_value(price)
        return self.cash + pos_value
    
    # ==================== 回测运行 ====================
    
    def run_strategy(self, strategy_name: str, symbols: List[str], 
                    days: int = 90, initial_cash: float = None) -> Dict:
        """运行单个策略回测"""
        if initial_cash:
            self.initial_cash = initial_cash
            self.cash = initial_cash
        
        # 生成市场数据
        market_data = {sym: self.generate_market_data(sym, days) for sym in symbols}
        
        # 策略函数映射
        strategy_funcs = {
            "rsi": self.strategy_rsi,
            "macd": self.strategy_macd,
            "bollinger": self.strategy_bollinger,
            "multi": self.strategy_multi_indicator,
        }
        
        func = strategy_funcs.get(strategy_name, self.strategy_rsi)
        
        self.trades = []
        self.closed_trades = []
        self.positions = {}
        self.equity_curve = []
        
        # 逐时间点执行
        reference = market_data[symbols[0]]
        
        for hour_idx in range(30, len(reference)):  # 跳过前面30小时
            # 更新价格
            prices = {}
            for sym in symbols:
                prices[sym] = market_data[sym][hour_idx].close
            
            self.update_equity(prices, reference[hour_idx].timestamp)
            
            # 策略信号
            for sym in symbols:
                candles = market_data[sym][:hour_idx+1]
                current_price = prices[sym]
                
                if strategy_name == "multi":
                    signal, confidence = func(candles)
                else:
                    signal = func(candles)
                    confidence = 0.7
                
                pos = self.positions.get(sym)
                invested = pos is not None and pos.quantity > 0
                
                # 交易执行
                if signal == "buy" and not invested:
                    if confidence > 0.5:
                        target_value = self.get_total_equity(prices) * 0.3
                        qty = target_value / current_price
                        self.execute_buy(sym, qty, current_price, strategy_name,
                                        reference[hour_idx].timestamp)
                
                elif signal == "sell" and invested:
                    self.liquidate(sym, current_price, strategy_name)
                
                # 止损
                elif invested:
                    pnl_pct = pos.get_pnl(current_price) / (pos.entry_price * pos.quantity) * 100
                    if pnl_pct < -5:
                        self.liquidate(sym, current_price, f"{strategy_name}_stop")
        
        return self.get_results()
    
    def get_results(self) -> Dict:
        """获取回测结果"""
        closed = self.closed_trades
        winning = [t for t in closed if t.pnl > 0]
        losing = [t for t in closed if t.pnl <= 0]
        
        total_pnl = sum(t.pnl for t in closed)
        final_equity = self.get_total_equity()
        return_pct = (final_equity - self.initial_cash) / self.initial_cash * 100
        
        # 最大回撤
        max_equity = self.initial_cash
        max_dd = 0
        for point in self.equity_curve:
            if point["equity"] > max_equity:
                max_equity = point["equity"]
            dd = (max_equity - point["equity"]) / max_equity * 100
            if dd > max_dd:
                max_dd = dd
        
        # 夏普比率 (简化)
        if len(closed) > 1:
            returns = [t.pnl / t.value for t in closed]
            avg_return = sum(returns) / len(returns)
            std_return = (sum((r - avg_return) ** 2 for r in returns) / len(returns)) ** 0.5
            sharpe = avg_return / std_return * math.sqrt(252) if std_return > 0 else 0
        else:
            sharpe = 0
        
        return {
            "initial_cash": self.initial_cash,
            "final_equity": round(final_equity, 2),
            "total_pnl": round(total_pnl, 2),
            "return_pct": round(return_pct, 2),
            "max_drawdown_pct": round(max_dd, 2),
            "sharpe_ratio": round(sharpe, 2),
            "total_trades": len(closed),
            "winning_trades": len(winning),
            "losing_trades": len(losing),
            "win_rate": round(len(winning) / len(closed), 3) if closed else 0,
            "avg_win": round(sum(t.pnl for t in winning) / len(winning), 2) if winning else 0,
            "avg_loss": round(sum(t.pnl for t in losing) / len(losing), 2) if losing else 0,
            "profit_factor": round(abs(sum(t.pnl for t in winning) / sum(t.pnl for t in losing)), 2) if losing and sum(t.pnl for t in losing) != 0 else 0,
        }


def run_all_strategies_comparison(symbols: List[str] = None, days: int = 90) -> Dict:
    """运行所有策略对比"""
    
    if symbols is None:
        symbols = ["BTC/USDT", "ETH/USDT"]
    
    strategies = ["rsi", "macd", "bollinger", "multi"]
    results = {}
    
    print("🔄 正在运行多策略回测对比...")
    
    for strat in strategies:
        engine = BacktestEngine(initial_cash=100000, fee_rate=0.001)
        result = engine.run_strategy(strat, symbols, days)
        results[strat] = result
        
        print(f"  ✅ {strat}: 收益 {result['return_pct']}%, 回撤 {result['max_drawdown_pct']}%, 胜率 {result['win_rate']}")
    
    # 排序
    ranked = sorted(results.items(), key=lambda x: x[1]["return_pct"], reverse=True)
    
    return {
        "timestamp": datetime.now().isoformat(),
        "symbols": symbols,
        "days": days,
        "strategies": results,
        "ranking": [{"strategy": r[0], **r[1]} for r in ranked],
        "best": ranked[0][0] if ranked else None
    }


if __name__ == "__main__":
    # 测试
    print("🪿 GO2SE 实际回测引擎测试")
    print("=" * 50)
    
    results = run_all_strategies_comparison(["BTC/USDT", "ETH/USDT"], 90)
    
    print("\n🏆 策略排名:")
    for i, r in enumerate(results["ranking"], 1):
        print(f"  {i}. {r['strategy']}: {r['return_pct']}% (回撤: {r['max_drawdown_pct']}%)")
    
    # 保存
    with open("/root/.openclaw/workspace/backtest_actual_results.json", "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("\n✅ 结果已保存")
