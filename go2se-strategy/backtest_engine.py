#!/usr/bin/env python3
"""
🪿 GO2SE 简易回测引擎
纯Python实现，无需Docker
"""

import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class Trade:
    """交易记录"""
    timestamp: str
    symbol: str
    side: str  # buy/sell
    price: float
    quantity: float
    value: float
    fee: float
    pnl: float = 0.0


@dataclass
class Position:
    """持仓"""
    symbol: str
    quantity: float
    entry_price: float
    current_price: float = 0.0
    
    @property
    def value(self) -> float:
        return self.quantity * self.current_price
    
    @property
    def pnl(self) -> float:
        return (self.current_price - self.entry_price) * self.quantity


class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, initial_cash: float = 100000, fee_rate: float = 0.001):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.fee_rate = fee_rate
        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
        self.equity_curve: List[Dict] = []
        self.running = True
        
    def generate_mock_data(self, symbol: str, days: int = 30) -> List[Dict]:
        """生成模拟K线数据"""
        import math
        
        data = []
        base_price = 45000 if "BTC" in symbol else 2500
        now = datetime.now()
        
        for i in range(days * 24):  # 小时数据
            timestamp = now - timedelta(hours=days * 24 - i)
            
            # 随机游走
            change = random.gauss(0, 0.02)  # 2%标准差
            base_price *= (1 + change)
            
            # 生成OHLC
            open_price = base_price
            high = base_price * random.uniform(1.0, 1.03)
            low = base_price * random.uniform(0.97, 1.0)
            close = base_price
            volume = random.uniform(100, 1000)
            
            data.append({
                "timestamp": timestamp.isoformat(),
                "symbol": symbol,
                "open": round(open_price, 2),
                "high": round(high, 2),
                "low": round(low, 2),
                "close": round(close, 2),
                "volume": round(volume, 2)
            })
        
        return data
    
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
            return 100
        
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    def buy(self, symbol: str, quantity: float, price: float) -> bool:
        """买入"""
        cost = quantity * price
        fee = cost * self.fee_rate
        
        if self.cash < cost + fee:
            return False
        
        self.cash -= (cost + fee)
        
        if symbol in self.positions:
            # 加仓
            pos = self.positions[symbol]
            total_quantity = pos.quantity + quantity
            total_cost = pos.quantity * pos.entry_price + cost
            pos.quantity = total_quantity
            pos.entry_price = total_cost / total_quantity
        else:
            self.positions[symbol] = Position(
                symbol=symbol,
                quantity=quantity,
                entry_price=price
            )
        
        self.trades.append(Trade(
            timestamp=datetime.now().isoformat(),
            symbol=symbol,
            side="buy",
            price=price,
            quantity=quantity,
            value=cost,
            fee=fee
        ))
        
        return True
    
    def sell(self, symbol: str, quantity: float, price: float) -> bool:
        """卖出"""
        if symbol not in self.positions:
            return False
        
        pos = self.positions[symbol]
        if pos.quantity < quantity:
            quantity = pos.quantity
        
        revenue = quantity * price
        fee = revenue * self.fee_rate
        pnl = (price - pos.entry_price) * quantity - fee
        
        self.cash += (revenue - fee)
        pos.quantity -= quantity
        
        if pos.quantity <= 0:
            del self.positions[symbol]
        
        self.trades.append(Trade(
            timestamp=datetime.now().isoformat(),
            symbol=symbol,
            side="sell",
            price=price,
            quantity=quantity,
            value=revenue,
            fee=fee,
            pnl=pnl
        ))
        
        return True
    
    def liquidate(self, symbol: str, price: float) -> bool:
        """清仓"""
        if symbol in self.positions:
            quantity = self.positions[symbol].quantity
            return self.sell(symbol, quantity, price)
        return False
    
    def update_prices(self, prices: Dict[str, float]):
        """更新所有持仓的当前价格"""
        for symbol, pos in self.positions.items():
            if symbol in prices:
                pos.current_price = prices[symbol]
    
    def get_total_equity(self) -> float:
        """获取总权益"""
        positions_value = sum(p.value for p in self.positions.values())
        return self.cash + positions_value
    
    def log(self, message: str):
        """日志"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def run_backtest(self, symbols: List[str], days: int = 30) -> Dict:
        """运行回测"""
        self.log(f"🪿 GO2SE 回测引擎启动")
        self.log(f"初始资金: ${self.initial_cash:,.2f}")
        self.log(f"交易对: {', '.join(symbols)}")
        self.log(f"回测周期: {days} 天")
        self.log("=" * 50)
        
        # 生成数据
        market_data = {}
        for symbol in symbols:
            market_data[symbol] = self.generate_mock_data(symbol, days)
        
        # RSI参数
        rsi_period = 14
        oversold = 30
        overbought = 70
        
        # 逐时间点执行
        for hour_idx in range(rsi_period, len(market_data[symbols[0]])):
            # 更新所有持仓价格
            prices = {}
            for symbol in symbols:
                candles = market_data[symbol]
                current_price = candles[hour_idx]["close"]
                prices[symbol] = current_price
            
            self.update_prices(prices)
            
            # 记录权益曲线
            self.equity_curve.append({
                "timestamp": market_data[symbols[0]][hour_idx]["timestamp"],
                "equity": self.get_total_equity(),
                "cash": self.cash,
                "positions_value": sum(p.value for p in self.positions.values())
            })
            
            # 策略逻辑
            for symbol in symbols:
                candles = market_data[symbol]
                close_prices = [c["close"] for c in candles[:hour_idx+1]]
                rsi = self.calculate_rsi(close_prices, rsi_period)
                current_price = prices[symbol]
                
                pos = self.positions.get(symbol)
                invested = pos is not None and pos.quantity > 0
                
                # 买入信号
                if rsi < oversold and not invested:
                    # 使用30%仓位
                    target_value = self.get_total_equity() * 0.3
                    quantity = target_value / current_price
                    if self.buy(symbol, quantity, current_price):
                        self.log(f"🟢 买入 {symbol} @ ${current_price:.2f} x {quantity:.4f} (RSI: {rsi:.1f})")
                
                # 卖出信号
                elif rsi > overbought and invested:
                    if self.liquidate(symbol, current_price):
                        self.log(f"🔴 卖出 {symbol} @ ${current_price:.2f} (RSI: {rsi:.1f})")
                
                # 止损
                elif invested:
                    pnl_pct = (current_price - pos.entry_price) / pos.entry_price * 100
                    if pnl_pct < -5:
                        if self.liquidate(symbol, current_price):
                            self.log(f"🛡️ 止损 {symbol} @ ${current_price:.2f} ({pnl_pct:.1f}%)")
        
        # 回测结束
        return self.get_results()
    
    def get_results(self) -> Dict:
        """获取回测结果"""
        total_pnl = sum(t.pnl for t in self.trades if t.side == "sell")
        final_equity = self.get_total_equity()
        return_pct = (final_equity - self.initial_cash) / self.initial_cash * 100
        
        # 计算最大回撤
        max_equity = self.initial_cash
        max_drawdown = 0
        for point in self.equity_curve:
            if point["equity"] > max_equity:
                max_equity = point["equity"]
            drawdown = (max_equity - point["equity"]) / max_equity * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        results = {
            "initial_cash": self.initial_cash,
            "final_equity": round(final_equity, 2),
            "total_pnl": round(total_pnl, 2),
            "return_pct": round(return_pct, 2),
            "max_drawdown_pct": round(max_drawdown, 2),
            "total_trades": len(self.trades),
            "winning_trades": len([t for t in self.trades if t.side == "sell" and t.pnl > 0]),
            "losing_trades": len([t for t in self.trades if t.side == "sell" and t.pnl <= 0]),
            "trades": [t.__dict__ for t in self.trades[-10:]],  # 最近10笔
            "equity_curve": self.equity_curve
        }
        
        self.log("=" * 50)
        self.log(f"🪿 回测结果")
        self.log(f"初始资金: ${results['initial_cash']:,.2f}")
        self.log(f"最终权益: ${results['final_equity']:,.2f}")
        self.log(f"总盈亏: ${results['total_pnl']:,.2f}")
        self.log(f"收益率: {results['return_pct']:.2f}%")
        self.log(f"最大回撤: {results['max_drawdown_pct']:.2f}%")
        self.log(f"交易次数: {results['total_trades']}")
        self.log(f"盈利交易: {results['winning_trades']}")
        self.log(f"亏损交易: {results['losing_trades']}")
        
        return results


def run():
    """运行示例回测"""
    engine = BacktestEngine(initial_cash=100000, fee_rate=0.001)
    results = engine.run_backtest(
        symbols=["BTCUSDT", "ETHUSDT"],
        days=90
    )
    
    # 保存结果
    with open("/root/.openclaw/workspace/go2se-strategy/backtest_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n✅ 回测结果已保存到 backtest_results.json")
    
    return results


if __name__ == "__main__":
    run()
