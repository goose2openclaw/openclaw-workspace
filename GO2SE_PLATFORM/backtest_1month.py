#!/usr/bin/env python3
"""
🔬 北斗七鑫 1个月回测模拟器
============================
测试周期: 2026-02-28 ~ 2026-03-30
周期: 1小时K线
"""

import json
import math
import urllib.request
from datetime import datetime, timedelta
from typing import Dict, List

BINANCE_BASE = "https://api.binance.com/api/v3"
MINING_FEE = 0.001

def fetch_klines(symbol: str, interval: str = "1h", days: int = 30) -> List[Dict]:
    """获取K线数据"""
    all_klines = []
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    
    chunk_size = timedelta(days=12)
    current_start = start_time
    
    while current_start < end_time:
        current_end = min(current_start + chunk_size, end_time)
        url = f"{BINANCE_BASE}/klines?symbol={symbol.upper()}&interval={interval}&startTime={int(current_start.timestamp()*1000)}&endTime={int(current_end.timestamp()*1000)}&limit=1000"
        
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                data = json.loads(resp.read())
                if not data:
                    break
                for d in data:
                    kline = {
                        "open_time": datetime.fromtimestamp(d[0]/1000),
                        "open": float(d[1]),
                        "high": float(d[2]),
                        "low": float(d[3]),
                        "close": float(d[4]),
                        "volume": float(d[5])
                    }
                    if not all_klines or kline["open_time"] > all_klines[-1]["open_time"]:
                        all_klines.append(kline)
        except Exception as e:
            print(f"获取数据失败: {e}")
            break
        current_start = current_end
    
    return all_klines


class BeidouBacktester:
    """北斗七鑫回测器"""
    
    def __init__(self, initial_capital: float = 100000):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.position = 0
        self.trades = []
        self.equity_curve = []
        
        # 7大工具配置
        self.tools = {
            "rabbit": {"weight": 0, "stop_loss": 0.05, "take_profit": 0.08},  # 禁用
            "mole": {"weight": 0.30, "stop_loss": 0.08, "take_profit": 0.15},  # 打地鼠
            "oracle": {"weight": 0.20, "stop_loss": 0.05, "take_profit": 0.10},  # 走着瞧
            "leader": {"weight": 0.15, "stop_loss": 0.03, "take_profit": 0.06},  # 跟大哥
            "hitchhiker": {"weight": 0.15, "stop_loss": 0.05, "take_profit": 0.08},  # 搭便车
            "airdrop": {"weight": 0.03, "stop_loss": 0.02, "take_profit": 0.20},  # 薅羊毛
            "crowdsource": {"weight": 0.02, "stop_loss": 0.01, "take_profit": 0.30},  # 穷孩子
        }
        
        # 当前启用的工具
        self.active_tools = ["mole", "oracle", "leader", "hitchhiker", "airdrop", "crowdsource"]
    
    def calculate_signal(self, kline: Dict, history: List[Dict]) -> str:
        """基于历史数据生成信号"""
        if len(history) < 50:
            return "HOLD"
        
        closes = [h["close"] for h in history[-50:]]
        
        # 简单MA策略
        ma_short = sum(closes[-12:]) / 12
        ma_long = sum(closes[-24:]) / 24
        
        rsi = self.calculate_rsi(closes)
        
        if ma_short > ma_long and rsi < 70:
            return "LONG"
        elif ma_short < ma_long and rsi > 30:
            return "SHORT"
        return "HOLD"
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """计算RSI"""
        if len(prices) < period + 1:
            return 50
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas[-period:]]
        losses = [-d if d < 0 else 0 for d in deltas[-period:]]
        
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        
        if avg_loss == 0:
            return 100
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    def backtest_symbol(self, symbol: str, klines: List[Dict]) -> Dict:
        """回测单个标的"""
        self.capital = self.initial_capital * self.tools["mole"]["weight"]  # 按仓位分配
        self.position = 0
        self.trades = []
        self.equity_curve = []
        
        entry_price = 0
        entry_time = None
        
        for i, kline in enumerate(klines):
            price = kline["close"]
            
            # 计算权益
            equity = self.capital + self.position * price
            self.equity_curve.append({"time": kline["open_time"], "equity": equity})
            
            signal = self.calculate_signal(kline, klines[:i])
            
            # 止损止盈检查
            if self.position > 0:
                pnl_pct = (price - entry_price) / entry_price
                stop_loss = -self.tools["mole"]["stop_loss"]
                take_profit = self.tools["mole"]["take_profit"]
                
                if pnl_pct <= stop_loss or pnl_pct >= take_profit:
                    # 平仓
                    self.capital = self.position * price * (1 - MINING_FEE)
                    self.trades.append({
                        "symbol": symbol,
                        "entry": entry_price,
                        "exit": price,
                        "pnl_pct": pnl_pct,
                        "exit_reason": "stop_loss" if pnl_pct <= stop_loss else "take_profit",
                        "duration": (kline["open_time"] - entry_time).total_seconds() / 3600
                    })
                    self.position = 0
                    entry_price = 0
            
            # 开仓
            if signal == "LONG" and self.position == 0:
                allocate = self.capital
                self.position = allocate / price * (1 - MINING_FEE)
                entry_price = price
                entry_time = kline["open_time"]
                self.capital = 0
        
        # 最终平仓
        if self.position > 0:
            final_price = klines[-1]["close"]
            self.capital = self.position * final_price * (1 - MINING_FEE)
            self.trades.append({
                "symbol": symbol,
                "entry": entry_price,
                "exit": final_price,
                "pnl_pct": (final_price - entry_price) / entry_price,
                "exit_reason": "end",
                "duration": (klines[-1]["open_time"] - entry_time).total_seconds() / 3600
            })
            self.position = 0
        
        final_equity = self.capital + self.position * klines[-1]["close"]
        
        return {
            "symbol": symbol,
            "initial_capital": self.initial_capital * self.tools["mole"]["weight"],
            "final_equity": final_equity,
            "total_return": (final_equity - self.initial_capital * self.tools["mole"]["weight"]) / (self.initial_capital * self.tools["mole"]["weight"]),
            "num_trades": len(self.trades),
            "win_rate": sum(1 for t in self.trades if t["pnl_pct"] > 0) / len(self.trades) if self.trades else 0,
            "avg_win": sum(t["pnl_pct"] for t in self.trades if t["pnl_pct"] > 0) / sum(1 for t in self.trades if t["pnl_pct"] > 0) if self.trades else 0,
            "avg_loss": sum(t["pnl_pct"] for t in self.trades if t["pnl_pct"] < 0) / sum(1 for t in self.trades if t["pnl_pct"] < 0) if self.trades else 0,
            "trades": self.trades
        }
    
    def run_backtest(self, symbols: List[str]) -> Dict:
        """运行完整回测"""
        print("=" * 60)
        print("🔬 北斗七鑫 1个月回测")
        print("=" * 60)
        print(f"测试周期: {(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')} ~ {datetime.now().strftime('%Y-%m-%d')}")
        print(f"初始资金: ${self.initial_capital:,.2f}")
        print(f"工具配置: {self.active_tools}")
        print("=" * 60)
        
        results = {}
        total_equity = self.initial_capital
        
        for symbol in symbols:
            print(f"\n📊 回测 {symbol}...")
            
            # 获取数据
            klines = fetch_klines(symbol, "1h", days=30)
            if not klines:
                print(f"  ⚠️ 无法获取数据")
                continue
            
            print(f"  获取到 {len(klines)} 根K线")
            
            # 回测
            result = self.backtest_symbol(symbol, klines)
            results[symbol] = result
            
            # 累计资金 (按权重)
            tool_weight = self.tools["mole"]["weight"]
            position_capital = self.initial_capital * tool_weight
            position_equity = position_capital * (1 + result["total_return"])
            total_equity += position_equity - position_capital
            
            # 输出结果
            ret_pct = result["total_return"] * 100
            ret_str = f"+{ret_pct:.2f}%" if ret_pct >= 0 else f"{ret_pct:.2f}%"
            print(f"  收益: {ret_str} | 交易: {result['num_trades']} | 胜率: {result['win_rate']*100:.1f}%")
        
        # 汇总
        total_return = (total_equity - self.initial_capital) / self.initial_capital
        
        print("\n" + "=" * 60)
        print("📈 汇总报告")
        print("=" * 60)
        print(f"总资金: ${total_equity:,.2f}")
        print(f"总收益: {total_return*100:+.2f}%")
        print(f"年化收益: {total_return*12*100:+.2f}%")
        
        return {
            "period": "1个月",
            "start_date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
            "end_date": datetime.now().strftime("%Y-%m-%d"),
            "initial_capital": self.initial_capital,
            "final_capital": total_equity,
            "total_return": total_return,
            "annualized_return": total_return * 12,
            "symbols": symbols,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }


if __name__ == "__main__":
    # 测试标的
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]
    
    backtester = BeidouBacktester(initial_capital=100000)
    report = backtester.run_backtest(symbols)
    
    # 保存报告
    with open("backtest_1month_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n💾 报告已保存: backtest_1month_report.json")
