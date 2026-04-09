#!/usr/bin/env python3
"""
GO2SE Solana 回测 - 90天真实历史数据
使用Binance API获取真实SOL/USDT数据
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict

# Binance API
BINANCE_URL = "https://api.binance.com/api/v3/klines"

def fetch_sol_data(days: int = 90) -> List[Dict]:
    """获取SOL/USDT历史K线数据"""
    end_time = int(datetime.now().timestamp() * 1000)
    start_time = end_time - (days * 24 * 60 * 60 * 1000)
    
    params = {
        "symbol": "SOLUSDT",
        "interval": "1h",
        "startTime": start_time,
        "endTime": end_time,
        "limit": 1000
    }
    
    try:
        resp = requests.get(BINANCE_URL, params=params, timeout=30)
        data = resp.json()
        
        result = []
        for k in data:
            result.append({
                "timestamp": k[0],
                "open": float(k[1]),
                "high": float(k[2]),
                "low": float(k[3]),
                "close": float(k[4]),
                "volume": float(k[5])
            })
        return result
    except Exception as e:
        print(f"获取数据失败: {e}")
        return []

def calculate_indicators(data: List[Dict]) -> List[Dict]:
    """计算技术指标"""
    # 计算SMA
    for i in range(len(data)):
        if i >= 20:
            sma20 = sum(d['close'] for d in data[i-20:i]) / 20
            data[i]['sma20'] = sma20
        if i >= 50:
            sma50 = sum(d['close'] for d in data[i-50:i]) / 50
            data[i]['sma50'] = sma50
    
    # 计算RSI (14周期)
    for i in range(len(data)):
        if i >= 14:
            gains = []
            losses = []
            for j in range(i-14, i):
                change = data[j+1]['close'] - data[j]['close']
                if change > 0:
                    gains.append(change)
                    losses.append(0)
                else:
                    gains.append(0)
                    losses.append(abs(change))
            
            avg_gain = sum(gains) / 14
            avg_loss = sum(losses) / 14
            
            if avg_loss == 0:
                data[i]['rsi'] = 100
            else:
                rs = avg_gain / avg_loss
                data[i]['rsi'] = 100 - (100 / (1 + rs))
    
    return data

def generate_signals(data: List[Dict]) -> List[Dict]:
    """生成交易信号"""
    signals = []
    
    for i in range(50, len(data)):
        curr = data[i]
        prev = data[i-1]
        
        if 'sma20' not in curr or 'sma50' not in curr:
            continue
            
        action, reason, confidence = "HOLD", "", 0
        
        # 金叉买入
        if prev.get('sma20', 0) <= prev.get('sma50', 0) and curr['sma20'] > curr['sma50']:
            action, reason, confidence = "BUY", "MA黄金交叉", min(95, 70 + (curr['rsi'] - 50) / 2)
        # 死叉卖出
        elif prev.get('sma20', 0) >= prev.get('sma50', 0) and curr['sma20'] < curr['sma50']:
            action, reason, confidence = "SELL", "MA死亡交叉", min(95, 70 + (50 - curr['rsi']) / 2)
        # RSI超卖买入
        elif curr.get('rsi', 50) < 35 and action == "HOLD":
            action, reason, confidence = "BUY", "RSI超卖", min(90, 60 + (35 - curr['rsi']))
        # RSI超买卖出
        elif curr.get('rsi', 50) > 70 and action == "HOLD":
            action, reason, confidence = "SELL", "RSI超买", min(90, 60 + (curr['rsi'] - 70))
        
        if action != "HOLD":
            signals.append({
                "timestamp": curr['timestamp'],
                "action": action,
                "reason": reason,
                "confidence": round(confidence, 1),
                "price": curr['close'],
                "rsi": round(curr.get('rsi', 50), 1),
                "sma20": round(curr.get('sma20', 0), 2),
                "sma50": round(curr.get('sma50', 0), 2)
            })
    
    return signals

def run_backtest(data: List[Dict], signals: List[Dict], initial_capital: float = 10000) -> Dict:
    """执行回测"""
    capital = initial_capital
    position = None
    trades = []
    
    for sig in signals:
        price = sig['price']
        size_pct = min(0.3, sig['confidence'] / 100 * 0.3)  # 仓位根据置信度
        
        if sig['action'] == "BUY" and position is None:
            qty = (capital * size_pct) / price
            position = {"qty": qty, "entry": price, "size_pct": size_pct}
            trades.append({
                "type": "BUY",
                "price": price,
                "qty": qty,
                "confidence": sig['confidence'],
                "reason": sig['reason']
            })
        
        elif sig['action'] == "SELL" and position is None:
            continue  # 无持仓不卖出
            
        elif sig['action'] == "SELL" and position is not None:
            # 平仓
            pnl = (price - position['entry']) * position['qty']
            capital += pnl + (position['qty'] * price)
            trades.append({
                "type": "SELL",
                "price": price,
                "pnl": pnl,
                "roi": (price - position['entry']) / position['entry'] * 100,
                "reason": sig['reason']
            })
            position = None
        
        elif sig['action'] == "BUY" and position is not None:
            continue  # 持仓中不买入
    
    # 最后平仓
    if position:
        final_price = data[-1]['close']
        pnl = (final_price - position['entry']) * position['qty']
        capital += pnl + (position['qty'] * final_price)
        trades.append({
            "type": "SELL",
            "price": final_price,
            "pnl": pnl,
            "roi": (final_price - position['entry']) / position['entry'] * 100,
            "reason": "最终平仓"
        })
    
    # 统计
    sell_trades = [t for t in trades if t['type'] == "SELL"]
    wins = [t for t in sell_trades if t.get('pnl', 0) > 0]
    win_rate = len(wins) / len(sell_trades) * 100 if sell_trades else 0
    
    total_return = (capital - initial_capital) / initial_capital * 100
    
    return {
        "symbol": "SOL/USDT",
        "period": f"最近90天",
        "initial_capital": initial_capital,
        "final_capital": round(capital, 2),
        "total_return": round(total_return, 2),
        "total_trades": len(trades),
        "completed_trades": len(sell_trades),
        "win_rate": round(win_rate, 1),
        "total_pnl": round(capital - initial_capital, 2),
        "trades": trades[-10:]  # 最近10笔
    }

def main():
    print("=" * 60)
    print("🪿 GO2SE Solana 90天回测")
    print("=" * 60)
    
    # 获取数据
    print("\n📥 获取SOL/USDT历史数据...")
    data = fetch_sol_data(90)
    
    if not data:
        print("❌ 获取数据失败")
        return
    
    print(f"✅ 获取到 {len(data)} 条小时K线数据")
    print(f"📅 数据范围: {datetime.fromtimestamp(data[0]['timestamp']/1000).strftime('%Y-%m-%d')} ~ {datetime.fromtimestamp(data[-1]['timestamp']/1000).strftime('%Y-%m-%d')}")
    
    # 计算指标
    print("\n📊 计算技术指标...")
    data = calculate_indicators(data)
    
    # 生成信号
    print("🎯 生成交易信号...")
    signals = generate_signals(data)
    print(f"✅ 生成 {len(signals)} 个信号")
    
    # 回测
    print("\n💰 执行回测...")
    result = run_backtest(data, signals, 10000)
    
    # 输出结果
    print("\n" + "=" * 60)
    print("📈 回测结果")
    print("=" * 60)
    print(f"🪙 交易对: {result['symbol']}")
    print(f"📅 回测周期: {result['period']}")
    print(f"💵 初始资金: ${result['initial_capital']:,.2f}")
    print(f"💵 最终资金: ${result['final_capital']:,.2f}")
    print(f"📈 总收益: {result['total_return']:+.2f}%")
    print(f"📊 总交易: {result['total_trades']} 笔")
    print(f"✅ 胜率: {result['win_rate']}%")
    print(f"💰 PnL: ${result['total_pnl']:+,.2f}")
    
    print("\n📋 最近交易:")
    for i, t in enumerate(result['trades'], 1):
        if t['type'] == "BUY":
            print(f"   {i}. 🟢 买入 @ ${t['price']:.2f} | 置信度: {t['confidence']:.0f}% | {t['reason']}")
        else:
            pnl_str = f"${t['pnl']:+.2f}" if 'pnl' in t else ""
            roi_str = f"({t.get('roi', 0):+.2f}%)" if 'roi' in t else ""
            print(f"   {i}. 🔴 卖出 @ ${t['price']:.2f} | {pnl_str} {roi_str} | {t['reason']}")
    
    # 价格变化
    start_price = data[0]['close']
    end_price = data[-1]['close']
    price_change = (end_price - start_price) / start_price * 100
    
    print(f"\n📌 基准对比 (买入持有):")
    print(f"   SOL价格: ${start_price:.2f} → ${end_price:.2f} ({price_change:+.2f}%)")
    print(f"   策略超额收益: {result['total_return'] - price_change:+.2f}%")

if __name__ == '__main__':
    main()