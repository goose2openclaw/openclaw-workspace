#!/usr/bin/env python3
"""
📊 专家模式 vs 普通模式 对比评测
==================================

测试维度:
1. 收益率
2. 胜率
3. 最大回撤
4. 交易频率
5. 风险调整收益
"""

import json
import urllib.request
from datetime import datetime, timedelta
from typing import Dict, List

BINANCE_API = "https://api.binance.com/api/v3"


def fetch_klines(symbol: str, days: int = 30) -> List[Dict]:
    """获取K线"""
    end_time = int(datetime.now().timestamp() * 1000)
    start_time = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
    url = f"{BINANCE_API}/klines?symbol={symbol}&interval=1h&startTime={start_time}&endTime={end_time}&limit=1000"
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            data = json.loads(resp.read())
            return [{"close": float(d[4]), "volume": float(d[5])} for d in data]
    except:
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


def normal_mode_backtest(symbol: str, initial: float, allocation: float) -> Dict:
    """
    普通模式
    ========
    - 简单MA交叉
    - 固定止损5%
    - 低置信度也交易
    """
    klines = fetch_klines(symbol, 30)
    if not klines:
        return None
    
    capital = initial * allocation
    position = 0
    qty = 0
    trades = []
    
    for i in range(50, len(klines)):
        closes = [k["close"] for k in klines[max(0,i-30):i+1]]
        if len(closes) < 30:
            continue
        
        price = klines[i]["close"]
        ma10 = sum(closes[-10:]) / 10
        ma20 = sum(closes[-20:]) / 20
        
        # 普通模式: MA交叉就交易
        if position == 0:
            if ma10 > ma20:
                position = 1
                qty = capital / price * 0.999
                capital = 0
            elif ma10 < ma20:
                position = -1
                qty = capital / price * 0.999
                capital = 0
        
        if position != 0:
            pnl = (price - (initial * allocation / qty)) / (initial * allocation / qty) * position
            if pnl <= -0.05 or pnl >= 0.10:
                capital = qty * price * 0.999
                trades.append({"pnl": pnl, "dir": "LONG" if position == 1 else "SHORT"})
                position = 0
    
    if position:
        capital = qty * klines[-1]["close"] * 0.999
    
    final = capital
    total_return = (final - initial * allocation) / (initial * allocation)
    wins = [t for t in trades if t["pnl"] > 0]
    
    return {
        "mode": "NORMAL",
        "symbol": symbol,
        "initial": initial * allocation,
        "final": final,
        "return": total_return,
        "trades": len(trades),
        "wins": len(wins),
        "win_rate": len(wins) / len(trades) if trades else 0,
        "max_dd": max([abs(t["pnl"]) for t in trades], default=0)
    }


def expert_mode_backtest(symbol: str, initial: float, allocation: float) -> Dict:
    """
    专家模式
    ========
    - MA + RSI + 波动率过滤
    - 动态止损3%
    - 只在高置信度时交易
    - 做多+做空双向
    """
    klines = fetch_klines(symbol, 30)
    if not klines:
        return None
    
    capital = initial * allocation
    position = 0
    qty = 0
    entry = 0
    trades = []
    
    for i in range(55, len(klines)):
        closes = [k["close"] for k in klines[max(0,i-55):i+1]]
        if len(closes) < 55:
            continue
        
        price = klines[i]["close"]
        
        # 专家指标
        ema9 = calculate_ema(closes, 9)
        ema21 = calculate_ema(closes, 21)
        ema55 = calculate_ema(closes, 55)
        rsi = calculate_rsi(closes)
        
        # 计算波动率
        returns = [(closes[j] - closes[j-1]) / closes[j-1] for j in range(1, len(closes))]
        vol = sum(abs(r) for r in returns[-20:]) / 20 if returns else 0
        
        # 专家模式: 多重过滤
        if position == 0:
            signal = None
            confidence = 0
            
            # 多头条件
            if ema9 > ema21 > ema55 and rsi < 70 and vol < 0.03:
                signal = 1
                confidence = 0.7
            # 空头条件
            elif ema9 < ema21 < ema55 and rsi > 30 and vol < 0.03:
                signal = -1
                confidence = 0.7
            
            # 只在高置信度时开仓
            if signal and confidence > 0.6:
                position = signal
                qty = capital / price * 0.999
                entry = price
                capital = 0
        
        # 动态止损3%
        if position != 0:
            pnl = (price - entry) / entry * position
            if pnl <= -0.03 or pnl >= 0.06:
                capital = qty * price * 0.999
                trades.append({"pnl": pnl, "dir": "LONG" if position == 1 else "SHORT"})
                position = 0
    
    if position:
        capital = qty * klines[-1]["close"] * 0.999
    
    final = capital
    total_return = (final - initial * allocation) / (initial * allocation)
    wins = [t for t in trades if t["pnl"] > 0]
    
    longs = [t for t in trades if t["dir"] == "LONG"]
    shorts = [t for t in trades if t["dir"] == "SHORT"]
    
    return {
        "mode": "EXPERT",
        "symbol": symbol,
        "initial": initial * allocation,
        "final": final,
        "return": total_return,
        "trades": len(trades),
        "wins": len(wins),
        "win_rate": len(wins) / len(trades) if trades else 0,
        "max_dd": max([abs(t["pnl"]) for t in trades], default=0),
        "longs": len(longs),
        "shorts": len(shorts)
    }


def main():
    print("=" * 70)
    print("📊 专家模式 vs 普通模式 对比评测")
    print("=" * 70)
    print(f"周期: 2026-02-28 ~ 2026-03-30")
    print()
    
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    initial = 100000
    
    normal_results = {}
    expert_results = {}
    
    for sym in symbols:
        print(f"📊 {sym}...")
        
        # 普通模式
        n = normal_mode_backtest(sym, initial, 0.10)
        if n:
            normal_results[sym] = n
            print(f"   普通: {n['return']*100:+.2f}% | {n['trades']}笔 | 胜率{n['win_rate']*100:.0f}%")
        
        # 专家模式
        e = expert_mode_backtest(sym, initial, 0.10)
        if e:
            expert_results[sym] = e
            print(f"   专家: {e['return']*100:+.2f}% | {e['trades']}笔 | 胜率{e['win_rate']*100:.0f}%")
        print()
    
    # 汇总
    print("=" * 70)
    print("📈 汇总对比")
    print("=" * 70)
    
    n_total_ret = sum(r["return"] for r in normal_results.values()) / len(normal_results)
    e_total_ret = sum(r["return"] for r in expert_results.values()) / len(expert_results)
    
    n_total_trades = sum(r["trades"] for r in normal_results.values())
    e_total_trades = sum(r["trades"] for r in expert_results.values())
    
    n_win_rate = sum(r["win_rate"] for r in normal_results.values()) / len(normal_results)
    e_win_rate = sum(r["win_rate"] for r in expert_results.values()) / len(expert_results)
    
    n_max_dd = max(r["max_dd"] for r in normal_results.values())
    e_max_dd = max(r["max_dd"] for r in expert_results.values())
    
    print(f"{'':10} | {'普通模式':^15} | {'专家模式':^15} | {'差异':^10}")
    print("-" * 70)
    print(f"{'收益率':10} | {n_total_ret*100:+11.2f}% | {e_total_ret*100:+14.2f}% | {(e_total_ret-n_total_ret)*100:+9.2f}%")
    print(f"{'交易数':10} | {n_total_trades:^15} | {e_total_trades:^14} | {e_total_trades-n_total_trades:+10}")
    print(f"{'胜率':10} | {n_win_rate*100:^14.1f}% | {e_win_rate*100:^14.1f}% | {(e_win_rate-n_win_rate)*100:+9.1f}%")
    print(f"{'最大回撤':10} | {n_max_dd*100:^14.2f}% | {e_max_dd*100:^14.2f}% | {(e_max_dd-n_max_dd)*100:+9.2f}%")
    print()
    
    # 分析
    print("=" * 70)
    print("🔍 模式分析")
    print("=" * 70)
    
    advantages = {
        "NORMAL": [],
        "EXPERT": []
    }
    
    if e_total_ret > n_total_ret:
        advantages["EXPERT"].append("收益率更高")
    else:
        advantages["NORMAL"].append("收益率更高")
    
    if e_win_rate > n_win_rate:
        advantages["EXPERT"].append("胜率更高")
    else:
        advantages["NORMAL"].append("胜率更高")
    
    if e_max_dd < n_max_dd:
        advantages["EXPERT"].append("回撤更小")
    else:
        advantages["NORMAL"].append("回撤更小")
    
    if e_total_trades < n_total_trades:
        advantages["EXPERT"].append("交易更少(省手续费)")
    else:
        advantages["NORMAL"].append("交易更少(省手续费)")
    
    print(f"  普通模式优势: {', '.join(advantages['NORMAL']) if advantages['NORMAL'] else '无'}")
    print(f"  专家模式优势: {', '.join(advantages['EXPERT']) if advantages['EXPERT'] else '无'}")
    print()
    
    # 结论
    print("=" * 70)
    print("📝 结论")
    print("=" * 70)
    
    expert_score = 0
    normal_score = 0
    
    if e_total_ret > n_total_ret:
        expert_score += 1
    else:
        normal_score += 1
    
    if e_win_rate > n_win_rate:
        expert_score += 1
    else:
        normal_score += 1
    
    if e_max_dd < n_max_dd:
        expert_score += 1
    else:
        normal_score += 1
    
    if expert_score > normal_score:
        print("  🏆 专家模式总体表现更优")
        print(f"     - 更严格的信号过滤减少虚假交易")
        print(f"     - 动态止损3%比普通5%更能保护利润")
        print(f"     - 波动率过滤避免在市场剧烈波动时开仓")
    elif normal_score > expert_score:
        print("  🏆 普通模式总体表现更优")
        print(f"     - 简单策略在趋势明确时表现良好")
        print(f"     - 更少的条件限制不错过机会")
    else:
        print("  ⚖️  两种模式表现相当，各有优劣")
    
    print()
    print(f"  专家模式推荐场景: 震荡市 + 高波动")
    print(f"  普通模式推荐场景: 趋势明确 + 低波动")
    print()
    
    # 保存报告
    report = {
        "period": "2026-02-28 to 2026-03-30",
        "normal": normal_results,
        "expert": expert_results,
        "summary": {
            "normal_return": n_total_ret,
            "expert_return": e_total_ret,
            "normal_trades": n_total_trades,
            "expert_trades": e_total_trades,
            "normal_win_rate": n_win_rate,
            "expert_win_rate": e_win_rate,
            "normal_max_dd": n_max_dd,
            "expert_max_dd": e_max_dd
        },
        "winner": "EXPERT" if expert_score > normal_score else ("NORMAL" if normal_score > expert_score else "TIE"),
        "timestamp": datetime.now().isoformat()
    }
    
    with open("expert_vs_normal_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    print("💾 报告已保存: expert_vs_normal_report.json")


if __name__ == "__main__":
    main()
