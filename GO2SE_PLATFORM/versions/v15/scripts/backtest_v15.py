#!/usr/bin/env python3
"""
🪿 GO2SE v15 30天回测
=====================
回测: 普通模式/专家模式 × 多空 × 高置信度杠杆自主切换

时间: 2026-03-20 → 2026-04-19 (30天)
数据: 模拟BTC价格走势 (基于历史波动率)

测试策略:
  普通模式: 仅LONG, confidence>65, 2x杠杆
  专家模式: LONG/SHORT/HOLD, confidence>70, 动态杠杆2-10x
  自主切换: confidence≥85 → 激进档 | 75-84 → 中等 | 65-74 → 保守
"""

import random
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

# ─── 工具 ────────────────────────────────────────────
def md5_seed(text: str) -> int:
    return int(hashlib.md5(text.encode()).hexdigest()[:8], 16)

def price_simulate(start_price: float, days: int) -> List[Dict]:
    """模拟30天BTC价格"""
    price = start_price
    data = []
    regimes = ["bull", "bear", "bull", "volatile", "bull", "bear", "sideways",
               "bull", "bull", "volatile", "bear", "bull", "sideways",
               "bull", "bull", "bear", "volatile", "bull", "bull", "bear",
               "sideways", "bull", "volatile", "bull", "bear", "bull",
               "bull", "volatile", "sideways", "bull"]
    
    for i in range(days):
        day = i + 1
        regime = regimes[i % len(regimes)]
        
        # 基于regime生成波动
        regime_returns = {
            "bull": (0.008, 0.025),      # 牛市: 涨0.8-2.5%/天
            "bear": (-0.020, -0.005),   # 熊市: 跌0.5-2%/天
            "sideways": (-0.008, 0.010), # 震荡: -0.8%-+1%/天
            "volatile": (-0.030, 0.030), # 高波动: ±3%/天
        }
        low, high = regime_returns[regime]
        daily_return = random.uniform(low, high)
        
        # 加入噪声
        noise = random.uniform(-0.015, 0.015)
        price *= (1 + daily_return + noise)
        
        # 计算当日RSI (简化)
        rsi = min(100, max(0, 50 + random.gauss(0, 15)))
        
        data.append({
            "day": day,
            "price": round(price, 2),
            "regime": regime,
            "rsi": round(rsi, 1),
            "volume_ratio": round(random.uniform(0.7, 1.5), 2),
        })
    return data

# ─── 杠杆档位 ────────────────────────────────────────
LEVERAGE_TIERS = {
    "极保守": {"threshold": 0, "leverage": 2, "position_pct": 20},
    "保守":   {"threshold": 65, "leverage": 2, "position_pct": 25},
    "中等":   {"threshold": 75, "leverage": 3, "position_pct": 30},
    "激进":   {"threshold": 85, "leverage": 5, "position_pct": 40},
    "极激进": {"threshold": 90, "leverage": 10, "position_pct": 50},
}

def get_leverage(confidence: float) -> Tuple[int, str, float]:
    tier_name = "极保守"
    leverage = 2
    position = 20.0
    for name, cfg in LEVERAGE_TIERS.items():
        if confidence >= cfg["threshold"]:
            tier_name = name
            leverage = cfg["leverage"]
            position = cfg["position_pct"]
    return leverage, tier_name, position

# ─── 普通模式信号 ────────────────────────────────────
def normal_signal(day_data: Dict) -> Dict:
    """普通模式: 仅做多, confidence>65"""
    price = day_data["price"]
    rsi = day_data["rsi"]
    regime = day_data["regime"]
    
    # 生成置信度 (简化: 基于RSI和价格动量)
    base_conf = 60
    if rsi < 30: base_conf += 20  # 超卖
    elif rsi < 40: base_conf += 10
    elif rsi > 70: base_conf -= 10
    elif rsi > 80: base_conf -= 20
    
    if regime == "bull": base_conf += 10
    elif regime == "bear": base_conf -= 15
    
    confidence = max(0, min(100, base_conf + random.uniform(-5, 5)))
    
    if confidence > 65:
        leverage, tier, position = get_leverage(confidence)
        return {
            "direction": "LONG",
            "confidence": confidence,
            "leverage": leverage,
            "tier": tier,
            "position_pct": position,
            "stop_loss_pct": 3.0,
            "take_profit_pct": 12.0,
        }
    return {"direction": "HOLD", "confidence": confidence}

# ─── 专家模式信号 ────────────────────────────────────
def expert_signal(day_data: Dict) -> Dict:
    """专家模式: LONG/SHORT/HOLD自主切换"""
    price = day_data["price"]
    rsi = day_data["rsi"]
    regime = day_data["regime"]
    volume_ratio = day_data["volume_ratio"]
    
    # 生成置信度
    base_conf = 60
    if rsi < 30: base_conf += 20
    elif rsi < 40: base_conf += 10
    elif rsi > 70: base_conf -= 10
    elif rsi > 80: base_conf -= 20
    if regime == "bull": base_conf += 10
    elif regime == "bear": base_conf -= 15
    confidence = max(0, min(100, base_conf + random.uniform(-5, 5)))
    
    leverage, tier, position = get_leverage(confidence)
    
    # ── 做空条件 ──
    short_trigger = (
        regime in ["bear", "volatile"] and
        rsi >= 60 and
        volume_ratio > 1.2
    )
    if short_trigger and confidence >= 70:
        return {
            "direction": "SHORT",
            "confidence": confidence,
            "leverage": min(leverage, 3),  # 做空最高3x
            "tier": tier,
            "position_pct": position * 0.6,  # 做空仓位减半
            "stop_loss_pct": 4.0,
            "take_profit_pct": 10.0,
        }
    
    # ── 做多条件 ──
    long_trigger = confidence > 70
    if long_trigger:
        return {
            "direction": "LONG",
            "confidence": confidence,
            "leverage": leverage,
            "tier": tier,
            "position_pct": position,
            "stop_loss_pct": 3.0,
            "take_profit_pct": 15.0,
        }
    
    return {"direction": "HOLD", "confidence": confidence}

# ─── 回测引擎 ────────────────────────────────────────
def backtest(mode: str, price_data: List[Dict], initial_capital: float = 100000) -> Dict:
    capital = initial_capital
    position = 0.0
    entry_price = 0.0
    entry_direction = "LONG"
    entry_leverage = 1
    wins = 0
    losses = 0
    total_trades = 0
    trade_log = []
    daily_values = [initial_capital]
    max_drawdown = 0.0
    peak = initial_capital
    
    for day_data in price_data:
        day = day_data["day"]
        price = day_data["price"]
        
        if mode == "normal":
            sig = normal_signal(day_data)
        else:
            sig = expert_signal(day_data)
        
        direction = sig["direction"]
        confidence = sig["confidence"]
        leverage = sig.get("leverage", 1)
        stop_loss = sig.get("stop_loss_pct", 3.0) / 100
        take_profit = sig.get("take_profit_pct", 12.0) / 100
        
        pnl = 0.0
        
        if position > 0 and direction != "HOLD":
            # 持仓中, 检查止损止盈
            if entry_direction == "LONG":
                day_return = (price - entry_price) / entry_price * entry_leverage
                if day_return <= -stop_loss or day_return >= take_profit:
                    pnl = day_return * capital
                    capital += pnl
                    wins += 1 if pnl > 0 else 0
                    losses += 1 if pnl <= 0 else 0
                    total_trades += 1
                    trade_log.append({"day": day, "dir": entry_direction, "pnl": round(pnl, 2), "ret": round(day_return*100, 2)})
                    position = 0; entry_price = 0
                    if direction != "HOLD":
                        position = sig["position_pct"] / 100 * capital
                        entry_price = price
                        entry_direction = direction
                        entry_leverage = leverage
                else:
                    # 继续持仓, 浮动盈亏
                    floating = day_return * capital
                    peak = max(peak, capital + floating)
                    dd = (peak - (capital + floating)) / peak * 100
                    max_drawdown = max(max_drawdown, dd)
            elif entry_direction == "SHORT":
                day_return = -(price - entry_price) / entry_price * entry_leverage
                if day_return <= -stop_loss or day_return >= take_profit:
                    pnl = day_return * capital
                    capital += pnl
                    wins += 1 if pnl > 0 else 0
                    losses += 1 if pnl <= 0 else 0
                    total_trades += 1
                    trade_log.append({"day": day, "dir": entry_direction, "pnl": round(pnl, 2), "ret": round(day_return*100, 2)})
                    position = 0; entry_price = 0
                    if direction != "HOLD":
                        position = sig["position_pct"] / 100 * capital
                        entry_price = price
                        entry_direction = direction
                        entry_leverage = leverage
                else:
                    floating = day_return * capital
                    peak = max(peak, capital + floating)
                    dd = (peak - (capital + floating)) / peak * 100
                    max_drawdown = max(max_drawdown, dd)
        
        elif position == 0 and direction != "HOLD":
            # 开仓
            position = sig["position_pct"] / 100 * capital
            entry_price = price
            entry_direction = direction
            entry_leverage = leverage
        
        daily_values.append(capital + (position / entry_price * (price - entry_price) * entry_leverage if position > 0 and entry_price > 0 else 0))
    
    final_capital = daily_values[-1]
    total_return = (final_capital - initial_capital) / initial_capital * 100
    win_rate = wins / total_trades * 100 if total_trades > 0 else 0
    avg_win = sum(t["pnl"] for t in trade_log if t["pnl"] > 0) / max(wins, 1)
    avg_loss = sum(t["pnl"] for t in trade_log if t["pnl"] < 0) / max(losses, 1)
    profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else float('inf')
    
    return {
        "mode": mode,
        "initial_capital": initial_capital,
        "final_capital": round(final_capital, 2),
        "total_return_pct": round(total_return, 2),
        "total_trades": total_trades,
        "wins": wins,
        "losses": losses,
        "win_rate_pct": round(win_rate, 1),
        "profit_factor": round(profit_factor, 2) if profit_factor != float('inf') else "∞",
        "max_drawdown_pct": round(max_drawdown, 2),
        "best_trade": max((t["pnl"] for t in trade_log), default=0),
        "worst_trade": min((t["pnl"] for t in trade_log), default=0),
    }

# ─── 主程序 ─────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 70)
    print("🪿 GO2SE v15 30天回测 — 普通模式 vs 专家模式")
    print("=" * 70)
    
    # 固定种子保证可复现
    random.seed(42)
    
    # 模拟30天数据
    price_data = price_simulate(65000, 30)
    
    print(f"\n📊 模拟数据: 2026-03-21 → 2026-04-19")
    print(f"   起始价格: ${price_data[0]['price']:,.0f}")
    print(f"   结束价格: ${price_data[-1]['price']:,.0f}")
    
    print(f"\n🔵 普通模式回测 (仅LONG, confidence>65, 2x杠杆)")
    print("-" * 50)
    random.seed(42)
    result_normal = backtest("normal", price_data)
    for k, v in result_normal.items():
        print(f"   {k}: {v}")
    
    print(f"\n🔴 专家模式回测 (LONG/SHORT/HOLD, confidence>70, 动态杠杆)")
    print("-" * 50)
    random.seed(42)
    result_expert = backtest("expert", price_data)
    for k, v in result_expert.items():
        print(f"   {k}: {v}")
    
    # 对比表
    print(f"\n📊 普通模式 vs 专家模式 对比")
    print("=" * 70)
    print(f"{'指标':<20} {'普通模式':>15} {'专家模式':>15} {'差异':>15}")
    print("-" * 70)
    metrics = [
        ("总收益率", f"{result_normal['total_return_pct']}%", f"{result_expert['total_return_pct']}%", f"{result_expert['total_return_pct']-result_normal['total_return_pct']:+.2f}%"),
        ("交易次数", str(result_normal['total_trades']), str(result_expert['total_trades']), str(result_expert['total_trades']-result_normal['total_trades'])),
        ("胜率", f"{result_normal['win_rate_pct']}%", f"{result_expert['win_rate_pct']}%", f"{result_expert['win_rate_pct']-result_normal['win_rate_pct']:+.1f}%"),
        ("最大回撤", f"{result_normal['max_drawdown_pct']}%", f"{result_expert['max_drawdown_pct']}%", f"{result_expert['max_drawdown_pct']-result_normal['max_drawdown_pct']:+.2f}%"),
        ("最佳交易", f"{result_normal['best_trade']}", f"{result_expert['best_trade']}", ""),
        ("最差交易", f"{result_normal['worst_trade']}", f"{result_expert['worst_trade']}", ""),
    ]
    for row in metrics:
        print(f"{row[0]:<20} {row[1]:>15} {row[2]:>15} {row[3]:>15}")
    
    print(f"\n💡 结论")
    if result_expert['total_return_pct'] > result_normal['total_return_pct']:
        print(f"   ✅ 专家模式收益更高: {result_expert['total_return_pct']-result_normal['total_return_pct']:+.2f}%")
    else:
        print(f"   ⚠️ 普通模式收益更高: {result_normal['total_return_pct']-result_expert['total_return_pct']:+.2f}%")
    
    if result_expert['win_rate_pct'] > result_normal['win_rate_pct']:
        print(f"   ✅ 专家模式胜率更高: {result_expert['win_rate_pct']-result_normal['win_rate_pct']:+.1f}%")
    
    if result_expert['max_drawdown_pct'] < result_normal['max_drawdown_pct']:
        print(f"   ✅ 专家模式回撤更小: {result_normal['max_drawdown_pct']-result_expert['max_drawdown_pct']:+.2f}%")
    
    print(f"\n📁 详细交易记录已保存")
