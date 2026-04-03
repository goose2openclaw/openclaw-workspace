#!/usr/bin/env python3
"""
🔬 北斗七鑫 1个月回测模拟器 (简化版)
===================================
使用模拟数据 + 真实价格获取
"""

import json
import math
import urllib.request
from datetime import datetime, timedelta
from typing import Dict, List

BINANCE_BASE = "https://api.binance.com/api/v3"

def fetch_recent_klines(symbol: str, days: int = 30) -> List[Dict]:
    """获取最近N天数据"""
    end_time = int(datetime.now().timestamp() * 1000)
    start_time = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
    
    url = f"{BINANCE_BASE}/klines?symbol={symbol.upper()}&interval=1h&startTime={start_time}&endTime={end_time}&limit=1000"
    
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            data = json.loads(resp.read())
            klines = []
            for d in data:
                klines.append({
                    "open_time": datetime.fromtimestamp(d[0]/1000),
                    "open": float(d[1]),
                    "high": float(d[2]),
                    "low": float(d[3]),
                    "close": float(d[4]),
                    "volume": float(d[5])
                })
            return klines
    except Exception as e:
        print(f"获取 {symbol} 失败: {e}")
        return []


def calculate_rsi(prices: List[float], period: int = 14) -> float:
    if len(prices) < period + 1:
        return 50
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0 for d in deltas[-period:]]
    losses = [-d if d < 0 else 0 for d in deltas[-period:]]
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        return 100
    return 100 - (100 / (1 + avg_gain / avg_loss))


def ma_strategy(prices: List[float]) -> str:
    """MA交叉策略"""
    if len(prices) < 26:
        return "HOLD"
    ma12 = sum(prices[-12:]) / 12
    ma26 = sum(prices[-26:]) / 26
    rsi = calculate_rsi(prices)
    
    if ma12 > ma26 and rsi < 70:
        return "LONG"
    elif ma12 < ma26 and rsi > 30:
        return "SHORT"
    return "HOLD"


def backtest_symbol(symbol: str, initial_capital: float, allocation: float) -> Dict:
    """回测单个标的"""
    klines = fetch_recent_klines(symbol, days=30)
    if not klines:
        return None
    
    capital = initial_capital * allocation
    position = 0
    entry_price = 0
    trades = []
    equity_history = []
    
    for i, kline in enumerate(klines[26:], 26):
        prices = [k["close"] for k in klines[:i+1]]
        price = kline["close"]
        equity = capital + position * price
        equity_history.append({"time": kline["open_time"].isoformat(), "equity": equity})
        
        # 止损止盈
        if position > 0:
            pnl = (price - entry_price) / entry_price
            if pnl <= -0.08 or pnl >= 0.15:
                capital = position * price * 0.999
                trades.append({"entry": entry_price, "exit": price, "pnl": pnl, "reason": "stop" if pnl < 0 else "profit"})
                position = 0
        
        # 信号
        signal = ma_strategy(prices)
        if signal == "LONG" and position == 0:
            position = capital / price * 0.999
            entry_price = price
            capital = 0
    
    # 平仓
    if position > 0:
        final_price = klines[-1]["close"]
        capital = position * final_price * 0.999
        trades.append({"entry": entry_price, "exit": final_price, "pnl": (final_price - entry_price) / entry_price, "reason": "end"})
    
    final_equity = capital
    total_return = (final_equity - initial_capital * allocation) / (initial_capital * allocation)
    wins = [t for t in trades if t["pnl"] > 0]
    
    return {
        "symbol": symbol,
        "initial": initial_capital * allocation,
        "final": final_equity,
        "return": total_return,
        "trades": len(trades),
        "wins": len(wins),
        "win_rate": len(wins) / len(trades) if trades else 0,
        "equity": equity_history
    }


def main():
    print("=" * 60)
    print("🔬 北斗七鑫 1个月回测")
    print("=" * 60)
    print(f"时间: 2026-02-28 ~ 2026-03-30")
    print(f"初始: $100,000")
    print()
    
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    initial = 100000
    
    # 仓位分配 (北斗七鑫)
    allocations = {
        "BTCUSDT": 0.30,   # 打地鼠
        "ETHUSDT": 0.20,   # 走着瞧
        "SOLUSDT": 0.15,   # 跟大哥
    }
    
    results = {}
    total_initial = 0
    total_final = 0
    
    for sym in symbols:
        print(f"📊 {sym}...", end=" ", flush=True)
        r = backtest_symbol(sym, initial, allocations[sym])
        if r:
            results[sym] = r
            total_initial += r["initial"]
            total_final += r["final"]
            ret = r["return"] * 100
            ret_str = f"+{ret:.2f}%" if ret >= 0 else f"{ret:.2f}%"
            print(f"{ret_str} | {r['trades']}笔 | 胜率{r['win_rate']*100:.0f}%")
        else:
            print("失败")
    
    total_return = (total_final - total_initial) / total_initial
    
    print()
    print("=" * 60)
    print("📈 汇总")
    print("=" * 60)
    print(f"总投入: ${total_initial:,.2f}")
    print(f"总收益: ${total_final:,.2f}")
    print(f"收益率: {total_return*100:+.2f}%")
    print(f"年化: {total_return*12*100:+.2f}%")
    print(f"夏普: {(total_return / 0.15) * math.sqrt(12):.2f}")
    print()
    
    # 保存
    report = {
        "period": "2026-02-28 to 2026-03-30",
        "initial_capital": initial,
        "total_initial": total_initial,
        "total_final": total_final,
        "total_return": total_return,
        "annualized": total_return * 12,
        "results": results,
        "timestamp": datetime.now().isoformat()
    }
    
    with open("backtest_1month_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    print("💾 已保存: backtest_1month_report.json")


if __name__ == "__main__":
    main()
