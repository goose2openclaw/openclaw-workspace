#!/usr/bin/env python3
"""
🔬 北斗七鑫 6个月回测模拟器 V2
"""

import json
import math
import urllib.request
from datetime import datetime, timedelta
from typing import Dict, List

BINANCE_BASE = "https://api.binance.com/api/v3"
MINING_FEE = 0.001


def fetch_klines_multi(symbol: str, interval: str = "1h", months: int = 6) -> List[Dict]:
    """获取多个月K线数据"""
    all_klines = []
    end_time = datetime.now()
    start_time = end_time - timedelta(days=30 * months)
    
    # Binance限制: 每次最多1000根
    chunk_size = timedelta(days=12)  # 约12天数据
    
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
                    # 避免重复
                    if not all_klines or kline["open_time"] > all_klines[-1]["open_time"]:
                        all_klines.append(kline)
                        
        except Exception as e:
            print(f"Error fetching {current_start}: {e}")
            break
        
        current_start = current_end
    
    return all_klines


def calculate_rsi(closes: List[float], period: int = 14) -> float:
    if len(closes) < period + 1:
        return 50.0
    deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
    gains = [d if d > 0 else 0 for d in deltas[-period:]]
    losses = [-d if d < 0 else 0 for d in deltas[-period:]]
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        return 100.0
    return 100 - (100 / (1 + avg_gain / avg_loss))


def get_indicators(closes: List[float], i: int) -> Dict:
    result = {"rsi": 50.0, "macd_hist": 0.0, "bb_pos": 0.5, "trend": "NEUTRAL", "trend_str": 0.5}
    
    if i < 20:
        return result
    
    # RSI
    if i >= 15:
        deltas = [closes[i] - closes[i-1] for i in range(max(1, i-13), i+1)]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        avg_g = sum(gains) / 14
        avg_l = sum(losses) / 14
        if avg_l > 0:
            result["rsi"] = 100 - (100 / (1 + avg_g / avg_l))
    
    # EMA
    def ema(data, period):
        k = 2 / (period + 1)
        val = sum(data[:period]) / period
        for d in data[period:]:
            val = d * k + val * (1 - k)
        return val
    
    # MACD
    if i >= 27:
        ema12 = ema(closes[:i+1], 12)
        ema26 = ema(closes[:i+1], 26)
        macd = ema12 - ema26
        signal = ema([macd] * 10, 9)
        result["macd_hist"] = macd - signal
    
    # BB
    if i >= 20:
        recent = closes[i-19:i+1]
        sma = sum(recent) / 20
        std = math.sqrt(sum((p - sma)**2 for p in recent) / 20)
        upper = sma + 2 * std
        lower = sma - 2 * std
        result["bb_pos"] = (closes[i] - lower) / (upper - lower) if upper > lower else 0.5
    
    # Trend
    if i >= 50:
        ma20 = sum(closes[i-19:i+1]) / 20
        ma50 = sum(closes[i-49:i+1]) / 50
        if closes[i] > ma20 and closes[i] > ma50:
            result["trend"] = "BULLISH"
            result["trend_str"] = min((closes[i] - ma50) / ma50 * 2, 1.0)
        elif closes[i] < ma20 and closes[i] < ma50:
            result["trend"] = "BEARISH"
            result["trend_str"] = min((ma50 - closes[i]) / ma50 * 2, 1.0)
    
    return result


def backtest(symbol: str, klines: List[Dict], mode: str = "EXPERT") -> Dict:
    """回测"""
    if len(klines) < 50:
        return {"error": "数据不足"}
    
    closes = [k["close"] for k in klines]
    
    equity = 10000.0
    peak = equity
    trades = []
    position = None
    
    for i in range(50, len(klines)):
        price = closes[i]
        ind = get_indicators(closes, i)
        
        # 入场
        if position is None:
            confirm = sum([
                ind["rsi"] < 30 or ind["rsi"] > 70,
                ind["bb_pos"] < 0.2 or ind["bb_pos"] > 0.8,
                ind["macd_hist"] > 0,
                ind["trend"] != "NEUTRAL"
            ])
            
            if confirm >= 2:
                direction = "LONG" if ind["rsi"] < 40 or ind["bb_pos"] < 0.3 else "SHORT"
                leverage = 3 if ind["trend"] == "BULLISH" else 2
                
                position = {
                    "entry": price,
                    "dir": direction,
                    "lev": leverage,
                    "size": 0.10,
                    "sl": price * (1 - 0.02 / leverage),
                    "tp": price * (1 + 0.10 / leverage),
                    "high": price if direction == "LONG" else 0,
                    "low": price if direction == "SHORT" else float('inf'),
                    "ts": None
                }
        
        # 持仓
        elif position:
            if position["dir"] == "LONG":
                position["high"] = max(position["high"], price)
            else:
                position["low"] = min(position["low"], price)
            
            exit_reason = None
            exit_price = price
            
            # 止损
            if position["dir"] == "LONG" and price <= position["sl"]:
                exit_reason = "SL"
                exit_price = position["sl"]
            elif position["dir"] == "SHORT" and price >= position["sl"]:
                exit_reason = "SL"
                exit_price = position["sl"]
            
            # 止盈
            if exit_reason is None and position["tp"]:
                if position["dir"] == "LONG" and price >= position["tp"]:
                    exit_reason = "TP"
                    exit_price = position["tp"]
                elif position["dir"] == "SHORT" and price <= position["tp"]:
                    exit_reason = "TP"
                    exit_price = position["tp"]
            
            # 追踪止损
            if exit_reason is None:
                ts = position["high"] * 0.97 if position["dir"] == "LONG" else position["low"] * 1.03
                if position["ts"] is None or (position["dir"] == "LONG" and ts > position["ts"]) or (position["dir"] == "SHORT" and ts < position["ts"]):
                    position["ts"] = ts
                if position["dir"] == "LONG" and price < position["ts"]:
                    exit_reason = "TS"
                elif position["dir"] == "SHORT" and price > position["ts"]:
                    exit_reason = "TS"
            
            # 出场
            if exit_reason:
                if position["dir"] == "LONG":
                    pnl_pct = (exit_price - position["entry"]) / position["entry"] * position["lev"]
                else:
                    pnl_pct = (position["entry"] - exit_price) / position["entry"] * position["lev"]
                
                pnl = equity * position["size"] * pnl_pct
                fees = equity * position["size"] * MINING_FEE * 2 * position["lev"]
                net = pnl - fees
                
                trades.append({
                    "entry": position["entry"],
                    "exit": exit_price,
                    "pnl": net,
                    "reason": exit_reason,
                    "dir": position["dir"]
                })
                
                equity += net
                if equity > peak:
                    peak = equity
                
                position = None
    
    # 统计
    wins = [t for t in trades if t["pnl"] > 0]
    losses = [t for t in trades if t["pnl"] <= 0]
    
    return {
        "symbol": symbol,
        "mode": mode,
        "trades": len(trades),
        "wins": len(wins),
        "losses": len(losses),
        "win_rate": len(wins) / len(trades) * 100 if trades else 0,
        "pnl_pct": (equity - 10000) / 10000 * 100,
        "max_dd": (peak - equity) / peak * 100 if peak > 0 else 0,
        "sharpe": 0.0,
        "avg_win": sum(t["pnl"] for t in wins) / len(wins) if wins else 0,
        "avg_loss": abs(sum(t["pnl"] for t in losses) / len(losses)) if losses else 0
    }


def run():
    symbols = ["ETHUSDT", "BTCUSDT", "SOLUSDT"]
    all_results = {}
    
    for sym in symbols:
        print(f"\n🔬 {sym} 6个月回测...")
        klines = fetch_klines_multi(sym, "1h", 6)
        
        if not klines:
            print(f"  ❌ 获取失败")
            continue
        
        print(f"  ✅ {len(klines)} 根K线 ({klines[0]['open_time'].strftime('%Y-%m-%d')} ~ {klines[-1]['open_time'].strftime('%Y-%m-%d')})")
        
        result = backtest(sym, klines)
        all_results[sym] = result
        
        print(f"  📊 交易:{result['trades']:3}笔 | 胜率:{result['win_rate']:5.1f}% | 收益:{result['pnl_pct']:+6.2f}% | 回撤:{result['max_dd']:5.2f}%")
    
    # 汇总
    print("\n" + "=" * 70)
    print("🔬 6个月专家模式回测汇总")
    print("=" * 70)
    
    total_trades = sum(r["trades"] for r in all_results.values())
    total_wins = sum(r["wins"] for r in all_results.values())
    
    print(f"\n{'标的':<10} {'交易':<6} {'胜率':<8} {'收益':<10} {'最大回撤':<10} {'盈亏比':<8}")
    print("-" * 70)
    for sym, r in all_results.items():
        pl_ratio = r["avg_win"] / r["avg_loss"] if r["avg_loss"] > 0 else 0
        print(f"{sym:<10} {r['trades']:<6} {r['win_rate']:<7.1f}% {r['pnl_pct']:<+9.2f}% {r['max_dd']:<9.2f}% {pl_ratio:<8.2f}")
    
    print("-" * 70)
    avg_wr = total_wins / total_trades * 100 if total_trades > 0 else 0
    avg_pnl = sum(r["pnl_pct"] for r in all_results.values()) / len(all_results)
    avg_dd = sum(r["max_dd"] for r in all_results.values()) / len(all_results)
    print(f"{'汇总':<10} {total_trades:<6} {avg_wr:<7.1f}% {avg_pnl:<+9.2f}% {avg_dd:<9.2f}%")
    print("=" * 70)
    
    with open('backtest_6months_result.json', 'w') as f:
        json.dump({"results": all_results, "timestamp": datetime.now().isoformat()}, f, indent=2)
    print("\n💾 已保存 backtest_6months_result.json")


if __name__ == "__main__":
    run()
