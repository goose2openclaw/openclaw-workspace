#!/usr/bin/env python3
"""
🔬 北斗七鑫回测模拟器 V2
======================
利用过去一个月历史数据对普通模式和专家模式进行自主模拟交易
"""

import json
import math
import urllib.request
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field

BINANCE_BASE = "https://api.binance.com/api/v3"

MINING_FEE = 0.001


@dataclass
class Trade:
    entry_time: str
    exit_time: str
    symbol: str
    direction: str
    entry_price: float
    exit_price: float
    position_size: float
    leverage: int
    pnl: float
    pnl_pct: float
    fees: float
    net_pnl: float
    exit_reason: str
    mode: str


@dataclass
class BacktestResult:
    mode: str
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    total_pnl: float = 0.0
    total_pnl_pct: float = 0.0
    max_drawdown: float = 0.0
    max_drawdown_pct: float = 0.0
    sharpe_ratio: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    profit_loss_ratio: float = 0.0
    trades: List = field(default_factory=list)


def fetch_klines(symbol: str, interval: str = "1h", limit: int = 720) -> List[Dict]:
    url = f"{BINANCE_BASE}/klines?symbol={symbol.upper()}&interval={interval}&limit={limit}"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = json.loads(resp.read())
            return [{
                "open_time": datetime.fromtimestamp(d[0]/1000),
                "open": float(d[1]), "high": float(d[2]),
                "low": float(d[3]), "close": float(d[4]),
                "volume": float(d[5]), "close_time": datetime.fromtimestamp(d[6]/1000)
            } for d in data]
    except Exception as e:
        print(f"Error: {e}")
        return []


def calculate_indicators(closes: List[float], highs: List[float], lows: List[float], i: int) -> Dict:
    """计算技术指标"""
    result = {"rsi": 50.0, "macd_hist": 0.0, "bb_position": 0.5, "trend": "NEUTRAL", "trend_strength": 0.5}
    
    if i < 20:
        return result
    
    # RSI (14)
    if i >= 15:
        deltas = [closes[i] - closes[i-1] for i in range(max(1, i-13), i+1)]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        avg_gain = sum(gains) / 14 if gains else 0
        avg_loss = sum(losses) / 14 if losses else 0
        if avg_loss > 0:
            rs = avg_gain / avg_loss
            result["rsi"] = 100 - (100 / (1 + rs))
    
    # MACD (12, 26, 9)
    if i >= 27:
        def ema(data, period):
            k = 2 / (period + 1)
            ema_val = sum(data[:period]) / period
            for d in data[period:]:
                ema_val = d * k + ema_val * (1 - k)
            return ema_val
        
        ema12 = ema(closes[:i+1], 12)
        ema26 = ema(closes[:i+1], 26)
        macd_line = ema12 - ema26
        signal = macd_line * 0.9
        result["macd_hist"] = macd_line - signal
    
    # Bollinger Bands (20, 2)
    if i >= 20:
        recent = closes[i-19:i+1]
        sma = sum(recent) / 20
        std = math.sqrt(sum((p - sma)**2 for p in recent) / 20)
        bb_upper = sma + 2 * std
        bb_lower = sma - 2 * std
        result["bb_position"] = (closes[i] - bb_lower) / (bb_upper - bb_lower) if bb_upper > bb_lower else 0.5
    
    # Trend (MA cross)
    if i >= 50:
        ma20 = sum(closes[i-19:i+1]) / 20
        ma50 = sum(closes[i-49:i+1]) / 50
        if closes[i] > ma20 and closes[i] > ma50:
            result["trend"] = "BULLISH"
            result["trend_strength"] = min((closes[i] - ma50) / ma50 * 2, 1.0)
        elif closes[i] < ma20 and closes[i] < ma50:
            result["trend"] = "BEARISH"
            result["trend_strength"] = min((ma50 - closes[i]) / ma50 * 2, 1.0)
    
    return result


def simulate_trades(klines: List[Dict], symbol: str, mode: str) -> BacktestResult:
    """模拟交易"""
    result = BacktestResult(mode=mode)
    
    if len(klines) < 50:
        return result
    
    closes = [k["close"] for k in klines]
    highs = [k["high"] for k in klines]
    lows = [k["low"] for k in klines]
    
    # 策略参数
    if mode == "NORMAL":
        params = {
            "rsi_oversold": 35,  # 放宽条件
            "rsi_overbought": 65,
            "stop_loss": 0.03,
            "take_profit": 0.08,
            "position_size": 0.15,
            "leverage": 1
        }
    else:  # EXPERT
        params = {
            "rsi_oversold": 30,
            "rsi_overbought": 70,
            "stop_loss": 0.02,
            "take_profit": 0.12,
            "position_size": 0.10,
            "leverage": 3,
            "trailing_distance": 0.03
        }
    
    equity = 10000.0
    peak_equity = equity
    trade_pnls = []
    position = None
    
    for i in range(50, len(klines)):
        current = klines[i]
        price = current["close"]
        ind = calculate_indicators(closes, highs, lows, i)
        
        # 入场信号
        if position is None:
            signal = None
            
            # 普通模式: RSI超卖 + 趋势确认
            if mode == "NORMAL":
                if ind["rsi"] < params["rsi_oversold"] and ind["bb_position"] < 0.2:
                    signal = ("LONG", price)
                elif ind["rsi"] > params["rsi_overbought"] and ind["bb_position"] > 0.8:
                    signal = ("LONG", price)  # 只做多
            
            # 专家模式: 多重确认 + 双向
            else:
                confirmations = 0
                if ind["rsi"] < params["rsi_oversold"]:
                    confirmations += 1
                if ind["rsi"] > params["rsi_overbought"]:
                    confirmations += 1
                if ind["macd_hist"] > 0:
                    confirmations += 1
                if ind["bb_position"] < 0.2:
                    confirmations += 1
                
                if confirmations >= 3:
                    if ind["rsi"] < params["rsi_oversold"] or ind["bb_position"] < 0.2:
                        signal = ("LONG", price)
                    elif ind["rsi"] > params["rsi_overbought"] or ind["bb_position"] > 0.8:
                        signal = ("SHORT", price) if ind["trend"] == "BEARISH" else ("LONG", price)
                
                # 趋势跟踪
                if ind["trend"] == "BULLISH" and ind["trend_strength"] > 0.6:
                    if ind["macd_hist"] > 0:
                        signal = ("LONG", price)
                elif ind["trend"] == "BEARISH" and ind["trend_strength"] > 0.6:
                    if mode == "EXPERT" and ind["macd_hist"] < 0:
                        signal = ("SHORT", price)
            
            if signal:
                direction, entry_price = signal
                position = {
                    "entry_time": current["open_time"],
                    "entry_price": entry_price,
                    "direction": direction,
                    "position_size": params["position_size"],
                    "leverage": params["leverage"],
                    "stop_loss": entry_price * (1 - params["stop_loss"] / params["leverage"]),
                    "take_profit": entry_price * (1 + params["take_profit"] / params["leverage"]),
                    "highest": entry_price if direction == "LONG" else 0,
                    "lowest": entry_price if direction == "SHORT" else float('inf'),
                    "trailing_stop": None
                }
        
        # 持仓管理
        elif position:
            direction = position["direction"]
            leverage = position["leverage"]
            entry_price = position["entry_price"]
            
            # 更新高低
            if direction == "LONG":
                position["highest"] = max(position["highest"], price)
            else:
                position["lowest"] = min(position["lowest"], price)
            
            exit_price = None
            exit_reason = None
            
            # 止损
            if direction == "LONG" and price <= position["stop_loss"]:
                exit_reason = "STOP_LOSS"
                exit_price = position["stop_loss"]
            elif direction == "SHORT" and price >= position["stop_loss"]:
                exit_reason = "STOP_LOSS"
                exit_price = position["stop_loss"]
            
            # 止盈 (专家模式可移除)
            if exit_reason is None and position["take_profit"]:
                if direction == "LONG" and price >= position["take_profit"]:
                    exit_reason = "TAKE_PROFIT"
                    exit_price = position["take_profit"]
                elif direction == "SHORT" and price <= position["take_profit"]:
                    exit_reason = "TAKE_PROFIT"
                    exit_price = position["take_profit"]
            
            # 追踪止损 (专家模式)
            if mode == "EXPERT" and exit_reason is None:
                if direction == "LONG":
                    ts = position["highest"] * (1 - params["trailing_distance"])
                    if ts > (position.get("trailing_stop") or 0):
                        position["trailing_stop"] = ts
                    if price < position["trailing_stop"]:
                        exit_reason = "TRAILING_STOP"
                        exit_price = price
                elif direction == "SHORT":
                    ts = position["lowest"] * (1 + params["trailing_distance"])
                    if ts < (position.get("trailing_stop") or float('inf')):
                        position["trailing_stop"] = ts
                    if price > position["trailing_stop"]:
                        exit_reason = "TRAILING_STOP"
                        exit_price = price
            
            # 出场
            if exit_reason:
                if direction == "LONG":
                    pnl_pct = (exit_price - entry_price) / entry_price * leverage
                else:
                    pnl_pct = (entry_price - exit_price) / entry_price * leverage
                
                pnl = equity * position["position_size"] * pnl_pct
                fees = equity * position["position_size"] * MINING_FEE * 2 * leverage
                net_pnl = pnl - fees
                
                result.total_trades += 1
                equity += net_pnl
                
                if net_pnl > 0:
                    result.winning_trades += 1
                else:
                    result.losing_trades += 1
                
                trade_pnls.append(net_pnl)
                result.total_pnl += net_pnl
                
                if equity > peak_equity:
                    peak_equity = equity
                dd = peak_equity - equity
                if dd > result.max_drawdown:
                    result.max_drawdown = dd
                    result.max_drawdown_pct = dd / peak_equity * 100
                
                position = None
    
    # 统计
    if result.total_trades > 0:
        result.win_rate = result.winning_trades / result.total_trades * 100
        result.total_pnl_pct = (equity - 10000) / 10000 * 100
        wins = [p for p in trade_pnls if p > 0]
        losses = [p for p in trade_pnls if p < 0]
        result.avg_win = sum(wins) / len(wins) if wins else 0
        result.avg_loss = abs(sum(losses) / len(losses)) if losses else 0
        result.profit_loss_ratio = result.avg_win / result.avg_loss if result.avg_loss > 0 else 0
        
        if len(trade_pnls) > 1:
            avg_r = sum(trade_pnls) / len(trade_pnls)
            std_r = math.sqrt(sum((r - avg_r)**2 for r in trade_pnls) / len(trade_pnls))
            result.sharpe_ratio = avg_r / std_r * math.sqrt(252) if std_r > 0 else 0
    
    return result


def run_backtest(symbol: str = "ETHUSDT"):
    print(f"🔬 获取 {symbol} 历史数据 (过去30天)...")
    klines = fetch_klines(symbol, "1h", 720)
    
    if not klines:
        print("❌ 获取数据失败")
        return
    
    print(f"✅ {len(klines)} 根K线: {klines[0]['open_time'].strftime('%Y-%m-%d')} ~ {klines[-1]['open_time'].strftime('%Y-%m-%d')}")
    print()
    
    print("🔄 普通模式回测...")
    normal = simulate_trades(klines, symbol, "NORMAL")
    print(f"   完成: {normal.total_trades} 笔交易, 胜率 {normal.win_rate:.1f}%")
    
    print("🔄 专家模式回测...")
    expert = simulate_trades(klines, symbol, "EXPERT")
    print(f"   完成: {expert.total_trades} 笔交易, 胜率 {expert.win_rate:.1f}%")
    
    print()
    print("=" * 90)
    print(f"🔬 北斗七鑫 回测报告 | {symbol} | 30天")
    print("=" * 90)
    print()
    
    print(f"{'指标':<22} {'普通模式':<30} {'专家模式':<30}")
    print("-" * 90)
    print(f"{'交易次数':<22} {normal.total_trades:<30} {expert.total_trades:<30}")
    print(f"{'胜率':<22} {normal.win_rate:<30.1f}% {expert.win_rate:<30.1f}%")
    print(f"{'总收益率':<22} {normal.total_pnl_pct:<29.2f}% {expert.total_pnl_pct:<29.2f}%")
    print(f"{'最大回撤率':<22} {normal.max_drawdown_pct:<29.2f}% {expert.max_drawdown_pct:<29.2f}%")
    print(f"{'夏普比率':<22} {normal.sharpe_ratio:<30.2f} {expert.sharpe_ratio:<30.2f}")
    print(f"{'盈亏比':<22} {normal.profit_loss_ratio:<30.2f} {expert.profit_loss_ratio:<30.2f}")
    print(f"{'平均盈利':<22} {normal.avg_win:<30.2f} {expert.avg_win:<30.2f}")
    print(f"{'平均亏损':<22} {normal.avg_loss:<30.2f} {expert.avg_loss:<30.2f}")
    print("-" * 90)
    
    wr_diff = expert.win_rate - normal.win_rate
    pnl_diff = expert.total_pnl_pct - normal.total_pnl_pct
    
    print()
    print(f"【差异】胜率 {wr_diff:+.1f}% | 收益 {pnl_diff:+.2f}%")
    
    if expert.total_pnl_pct > normal.total_pnl_pct and expert.sharpe_ratio > normal.sharpe_ratio:
        print("✅ 专家模式更优")
    elif normal.total_pnl_pct > 0 and normal.max_drawdown_pct < expert.max_drawdown_pct:
        print("✅ 普通模式更稳健")
    elif expert.total_pnl_pct > 0:
        print("✅ 专家模式收益更佳")
    else:
        print("⚠️ 两种模式均需优化")
    
    print("=" * 90)
    
    # 保存
    result_data = {
        "symbol": symbol,
        "period": {
            "start": klines[0]["open_time"].isoformat(),
            "end": klines[-1]["open_time"].isoformat()
        },
        "normal_mode": vars(normal),
        "expert_mode": vars(expert),
        "timestamp": datetime.now().isoformat()
    }
    
    with open('backtest_result.json', 'w') as f:
        json.dump(result_data, f, indent=2, ensure_ascii=False)
    
    print("\n💾 结果已保存到 backtest_result.json")


if __name__ == "__main__":
    import sys
    symbol = sys.argv[1] if len(sys.argv) > 1 else "ETHUSDT"
    run_backtest(symbol)
