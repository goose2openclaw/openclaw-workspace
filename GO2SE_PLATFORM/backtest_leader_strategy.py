#!/usr/bin/env python3
"""
👑 跟大哥策略 - 一个月回测
===========================
测试周期: 2026-02-28 ~ 2026-03-30
支持: 做多 + 做空 双向
"""

import json
import urllib.request
from datetime import datetime, timedelta
from typing import Dict, List

BINANCE_API = "https://api.binance.com/api/v3"


def fetch_klines(symbol: str, interval: str = "1h", days: int = 30) -> List[Dict]:
    """获取K线"""
    end_time = int(datetime.now().timestamp() * 1000)
    start_time = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
    
    url = f"{BINANCE_API}/klines?symbol={symbol}&interval={interval}&startTime={start_time}&endTime={end_time}&limit=1000"
    
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            data = json.loads(resp.read())
            return [
                {
                    "open_time": datetime.fromtimestamp(d[0] / 1000),
                    "open": float(d[1]),
                    "high": float(d[2]),
                    "low": float(d[3]),
                    "close": float(d[4]),
                    "volume": float(d[5])
                }
                for d in data
            ]
    except Exception as e:
        print(f"获取 {symbol} 失败: {e}")
        return []


def calculate_ema(prices: List[float], period: int) -> float:
    if len(prices) < period:
        return prices[-1] if prices else 0.0
    multiplier = 2 / (period + 1)
    ema = sum(prices[:period]) / period
    for price in prices[period:]:
        ema = (price - ema) * multiplier + ema
    return ema


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


def leader_backtest(symbol: str, initial_capital: float, allocation: float) -> Dict:
    """
    跟大哥策略回测
    ==============
    做空+做多双向跟随
    """
    klines = fetch_klines(symbol, "1h", days=30)
    if not klines:
        return None
    
    capital = initial_capital * allocation
    position = 0  # 0=无, 1=多, -1=空
    position_qty = 0
    entry_price = 0
    trades = []
    equity_curve = []
    
    stop_loss_pct = 0.03  # 3%
    take_profit_pct = 0.06  # 6%
    
    for i in range(50, len(klines)):
        window = klines[max(0, i-55):i+1]
        closes = [k["close"] for k in window]
        
        current_price = klines[i]["close"]
        equity = capital + position_qty * current_price if position == 0 else capital
        equity_curve.append({"time": klines[i]["open_time"].isoformat(), "equity": equity})
        
        # 趋势判断
        ema9 = calculate_ema(closes, 9)
        ema21 = calculate_ema(closes, 21)
        ema55 = calculate_ema(closes, 55)
        rsi = calculate_rsi(closes)
        
        # 信号
        signal = None
        if position == 0:
            if ema9 > ema21 > ema55 and rsi < 70:
                signal = "LONG"
            elif ema9 < ema21 < ema55 and rsi > 30:
                signal = "SHORT"
        
        # 开仓
        if signal and position == 0:
            if signal == "LONG":
                position = 1
                position_qty = capital / current_price * 0.999
                capital = 0
            else:  # SHORT
                position = -1
                position_qty = capital / current_price * 0.999
                capital = 0
            entry_price = current_price
        
        # 平仓检查
        if position != 0:
            pnl_pct = (current_price - entry_price) / entry_price * position
            
            should_close = False
            reason = ""
            
            if position == 1:  # 多头
                if pnl_pct <= -stop_loss_pct:
                    should_close = True
                    reason = "STOP_LOSS"
                elif pnl_pct >= take_profit_pct:
                    should_close = True
                    reason = "TAKE_PROFIT"
            else:  # 空头
                if pnl_pct <= -stop_loss_pct:
                    should_close = True
                    reason = "STOP_LOSS"
                elif pnl_pct >= take_profit_pct:
                    should_close = True
                    reason = "TAKE_PROFIT"
            
            if should_close:
                capital = position_qty * current_price * 0.999
                trades.append({
                    "direction": "LONG" if position == 1 else "SHORT",
                    "entry": entry_price,
                    "exit": current_price,
                    "pnl_pct": pnl_pct,
                    "reason": reason,
                    "duration_hours": (klines[i]["open_time"] - klines[max(0,i-10)]["open_time"]).total_seconds() / 3600
                })
                position = 0
                position_qty = 0
    
    # 平仓
    if position != 0:
        final_price = klines[-1]["close"]
        capital = position_qty * final_price * 0.999
        trades.append({
            "direction": "LONG" if position == 1 else "SHORT",
            "entry": entry_price,
            "exit": final_price,
            "pnl_pct": (final_price - entry_price) / entry_price * position,
            "reason": "END",
            "duration_hours": 0
        })
        position = 0
    
    final_equity = capital
    total_return = (final_equity - initial_capital * allocation) / (initial_capital * allocation)
    
    wins = [t for t in trades if t["pnl_pct"] > 0]
    longs = [t for t in trades if t["direction"] == "LONG"]
    shorts = [t for t in trades if t["direction"] == "SHORT"]
    
    return {
        "symbol": symbol,
        "initial": initial_capital * allocation,
        "final": final_equity,
        "return": total_return,
        "trades": len(trades),
        "wins": len(wins),
        "longs": len(longs),
        "shorts": len(shorts),
        "win_rate": len(wins) / len(trades) if trades else 0,
        "longs_pnl": sum(t["pnl_pct"] for t in longs) / len(longs) if longs else 0,
        "shorts_pnl": sum(t["pnl_pct"] for t in shorts) / len(shorts) if shorts else 0,
        "equity": equity_curve
    }


def main():
    print("=" * 65)
    print("👑 跟大哥策略 1个月回测 (做多+做空)")
    print("=" * 65)
    print(f"周期: 2026-02-28 ~ 2026-03-30")
    print(f"初始资金: $100,000")
    print()
    
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    initial = 100000
    
    # 跟大哥仓位
    allocations = {
        "BTCUSDT": 0.15,  # 跟大哥 15%
        "ETHUSDT": 0.10,  # 跟大哥 10%
        "SOLUSDT": 0.05,  # 跟大哥 5%
    }
    
    results = {}
    total_initial = 0
    total_final = 0
    
    for sym in symbols:
        print(f"📊 {sym}...", end=" ", flush=True)
        r = leader_backtest(sym, initial, allocations[sym])
        if r:
            results[sym] = r
            total_initial += r["initial"]
            total_final += r["final"]
            ret = r["return"] * 100
            ret_str = f"+{ret:.2f}%" if ret >= 0 else f"{ret:.2f}%"
            
            longs_pnl = r["longs_pnl"] * 100
            shorts_pnl = r["shorts_pnl"] * 100
            
            print(f"{ret_str} | 多:{r['longs']}笔({longs_pnl:+.1f}%) 空:{r['shorts']}笔({shorts_pnl:+.1f}%) | 胜率{r['win_rate']*100:.0f}%")
        else:
            print("失败")
    
    total_return = (total_final - total_initial) / total_initial
    
    print()
    print("=" * 65)
    print("📈 汇总")
    print("=" * 65)
    print(f"总投入: ${total_initial:,.2f}")
    print(f"总收益: ${total_final:,.2f}")
    print(f"收益率: {total_return*100:+.2f}%")
    print(f"年化: {total_return*12*100:+.2f}%")
    print()
    
    # 对比原策略
    print("-" * 65)
    print("📊 做空 vs 做多 对比")
    print("-" * 65)
    total_longs_pnl = sum(r["longs_pnl"] * r["longs"] for r in results.values()) / max(1, sum(r["longs"] for r in results.values()))
    total_shorts_pnl = sum(r["shorts_pnl"] * r["shorts"] for r in results.values()) / max(1, sum(r["shorts"] for r in results.values()))
    
    print(f"  做多平均收益: {total_longs_pnl*100:+.2f}%")
    print(f"  做空平均收益: {total_shorts_pnl*100:+.2f}%")
    
    if abs(total_shorts_pnl) > abs(total_longs_pnl):
        print("  → 熊市环境，做空策略更有效")
    else:
        print("  → 牛市环境，做多策略更有效")
    print()
    
    # 保存报告
    report = {
        "strategy": "leader_multi_short",
        "period": "2026-02-28 to 2026-03-30",
        "initial_capital": initial,
        "total_initial": total_initial,
        "total_final": total_final,
        "total_return": total_return,
        "annualized": total_return * 12,
        "results": results,
        "timestamp": datetime.now().isoformat()
    }
    
    with open("backtest_leader_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    print("💾 报告已保存: backtest_leader_report.json")


if __name__ == "__main__":
    main()
