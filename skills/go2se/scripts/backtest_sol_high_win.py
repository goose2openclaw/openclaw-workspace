#!/usr/bin/env python3
"""
GO2SE Solana 90天 - 高胜率模式
"""

import requests
from datetime import datetime, timedelta
import statistics

BINANCE_URL = "https://api.binance.com/api/v3/klines"

def fetch_data(days=90):
    end_time = int(datetime.now().timestamp() * 1000)
    start_time = end_time - (days * 24 * 60 * 60 * 1000)
    params = {"symbol": "SOLUSDT", "interval": "1h", "startTime": start_time, "endTime": end_time, "limit": 1000}
    return [[float(k[1]), float(k[2]), float(k[3]), float(k[4]), float(k[5])] for k in requests.get(BINANCE_URL, params=params).json()]

def calc_ma(data, period):
    return [sum(data[i-period:i])/period if i>=period else None for i in range(len(data))]

def calc_rsi(data, period=14):
    rsi = [50] * period
    for i in range(period, len(data)):
        gains, losses = 0, 0
        for j in range(i-period, i):
            change = data[j+1] - data[j]
            gains += max(0, change)
            losses += max(0, -change)
        avg_gain, avg_loss = gains/period, losses/period
        rsi.append(100 - (100/(1+avg_gain/avg_loss)) if avg_loss else 100)
    return rsi

def calc_ema(data, period):
    ema = [data[0]]
    for price in data[1:]:
        ema.append(ema[-1] * (2/(period+1)) + price * (1 - 2/(period+1)))
    return ema

# 加载数据
print("📥 加载数据...")
raw = fetch_data(90)
opens, highs, lows, closes, vols = [x[0] for x in raw], [x[1] for x in raw], [x[2] for x in raw], [x[3] for x in raw], [x[4] for x in raw]

# 计算指标
ma20 = calc_ma(closes, 20)
ma50 = calc_ma(closes, 50)
ma200 = calc_ma(closes, 200) if len(closes) >= 200 else [None]*len(closes)
rsi = calc_rsi(closes)
ema12 = calc_ema(closes, 12)
ema26 = calc_ema(closes, 26)
macd = [ema12[i] - ema26[i] for i in range(len(closes))]
signal = [sum(macd[max(0,i-8):i+1])/min(9,i+1) for i in range(len(macd))]
hist = [macd[i] - signal[i] for i in range(len(macd))]

# 高胜率策略: 严格条件
capital = 10000
position = None
trades = []
stop_loss = 0.025  # 2.5% 止损
take_profit = 0.06  # 6% 止盈
max_pos = 0.20  # 20% 仓位

print("\n🎯 交易中...")

for i in range(200, len(closes)):
    price = closes[i]
    prev = closes[i-1]
    
    # 趋势判断 (MA200之上为上升趋势)
    uptrend = ma200[i] and price > ma200[i]
    
    # 买入信号 (多个条件同时满足)
    buy = False
    buy_reason = ""
    
    # 1. 均线金叉 + RSI超卖 + MACD向上
    if ma20[i] and ma50[i] and ma20[i-1] <= ma50[i-1] and ma20[i] > ma50[i]:
        if rsi[i] < 35 and hist[i] > hist[i-1]:
            buy, buy_reason = True, "MA金叉+RSI超卖+MACD向上"
    
    # 2. RSI极端超卖 + 趋势反弹
    if rsi[i] < 25 and uptrend:
        buy, buy_reason = True, "RSI极度超卖+趋势反弹"
    
    # 3. 布林带下轨支撑
    bb_lower = ma20[i] - 2 * statistics.stdev(closes[i-20:i]) if i >= 20 else price * 0.9
    if price < bb_lower * 1.03 and rsi[i] < 30 and uptrend:
        buy, buy_reason = True, "布林带支撑+RSI反弹"
    
    # 卖出信号
    sell = False
    sell_reason = ""
    
    # 1. 均线死叉
    if ma20[i] and ma50[i] and ma20[i-1] >= ma50[i-1] and ma20[i] < ma50[i]:
        sell, sell_reason = True, "MA死叉"
    
    # 2. RSI超买
    if rsi[i] > 75:
        sell, sell_reason = True, "RSI超买"
    
    # 3. MACD死叉
    if hist[i] < 0 and hist[i-1] >= 0:
        sell, sell_reason = True, "MACD死叉"
    
    # 止损检查
    if position:
        pnl_pct = (price - position['entry']) / position['entry']
        if pnl_pct <= -stop_loss:
            pnl = (price - position['entry']) * position['qty']
            capital += pnl + position['qty'] * price
            trades.append(('SELL', price, pnl, '止损'))
            position = None
            continue
        if pnl_pct >= take_profit:
            pnl = (price - position['entry']) * position['qty']
            capital += pnl + position['qty'] * price
            trades.append(('SELL', price, pnl, '止盈'))
            position = None
    
    # 执行交易
    if buy and not position and uptrend:  # 只在上升趋势做多
        qty = (capital * max_pos) / price
        position = {'qty': qty, 'entry': price}
        trades.append(('BUY', price, 0, buy_reason))
    
    elif sell and position:
        pnl = (price - position['entry']) * position['qty']
        capital += pnl + position['qty'] * price
        trades.append(('SELL', price, pnl, sell_reason))
        position = None

# 平仓
if position:
    final = closes[-1]
    pnl = (final - position['entry']) * position['qty']
    capital += pnl + position['qty'] * final
    trades.append(('SELL', final, pnl, '最终平仓'))

# 统计
sells = [t for t in trades if t[0] == 'SELL']
wins = len([t for t in sells if t[2] > 0])
win_rate = wins / len(sells) * 100 if sells else 0
total_return = (capital - 10000) / 10000 * 100

print("\n" + "="*55)
print("🏆 高胜率模式回测结果")
print("="*55)
print(f"💵 初始: \$10,000 → 最终: \${capital:,.2f}")
print(f"📈 收益: {total_return:+.2f}%")
print(f"📊 交易: {len(sells)} 笔")
print(f"✅ 胜率: {win_rate:.1f}%")
print(f"💰 PnL: \${capital-10000:+,.2f}")

print("\n📋 交易记录:")
for i, t in enumerate(trades[-12:], 1):
    if t[0] == 'BUY':
        print(f"   {i}. 🟢 买入 @ \${t[1]:.2f} | {t[3]}")
    else:
        pnl_str = f"\${t[2]:+.2f}" if t[2] else ""
        print(f"   {i}. 🔴 卖出 @ \${t[1]:.2f} | {pnl_str} | {t[3]}")

print("\n💡 胜率提升关键:")
print("""
1. 只在上升趋势做多 (MA200之上)
2. 多指标共振 (MA+RSI+MACD)
3. RSI极度超卖 (<25) 才买入
4. 严格止损 2.5% + 止盈 6%
5. 减少交易频率，质量 > 数量
""")