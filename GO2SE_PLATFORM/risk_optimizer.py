#!/usr/bin/env python3
"""
🛡️ 风控参数优化器 V1
====================
基于6个月回测数据分析，优化风控参数
"""

import json
from dataclasses import dataclass
from typing import Dict

# 6个月回测结果
BACKTEST_DATA = {
    "ETHUSDT": {"trades": 432, "win_rate": 60.2, "pnl": -4.53, "max_dd": 5.96, "avg_win": 24.15, "avg_loss": 39.14},
    "BTCUSDT": {"trades": 298, "win_rate": 56.7, "pnl": -4.06, "max_dd": 7.50, "avg_win": 25.38, "avg_loss": 36.79},
    "SOLUSDT": {"trades": 513, "win_rate": 58.5, "pnl": -15.83, "max_dd": 18.50, "avg_win": 18.47, "avg_loss": 31.87},
}

@dataclass
class RiskParams:
    stop_loss_pct: float
    take_profit_pct: float
    trailing_stop_pct: float
    position_size: float
    leverage: int


def main():
    print("=" * 70)
    print("🛡️ 风控参数优化分析")
    print("=" * 70)
    
    print("\n📊 当前6个月回测问题诊断:")
    print("-" * 70)
    
    for sym, d in BACKTEST_DATA.items():
        pl_ratio = d["avg_win"] / d["avg_loss"] if d["avg_loss"] > 0 else 0
        print(f"  {sym}: 胜率{d['win_rate']:.1f}%, 盈亏比{pl_ratio:.2f} ← {'❌ 盈亏比<1' if pl_ratio < 1 else '✅'}")
        print(f"         平均盈利${d['avg_win']:.2f}, 平均亏损${d['avg_loss']:.2f}")
    
    print("\n💡 问题: 盈亏比 < 1.0，虽然胜率58%，但平均亏损 > 平均盈利")
    print("   原因: 止损2%太紧，止盈10%太大，单笔亏损超出盈利覆盖")
    
    # 计算期望值
    print("\n" + "=" * 70)
    print("🔧 优化方案测试")
    print("=" * 70)
    
    configs = [
        ("当前配置", RiskParams(2.0, 10.0, 3.0, 10.0, 3)),
        ("方案A-保守", RiskParams(3.0, 4.5, 2.5, 8.0, 2)),
        ("方案B-平衡", RiskParams(3.5, 5.25, 3.0, 10.0, 2)),
        ("方案C-进攻", RiskParams(4.0, 6.0, 3.0, 12.0, 2)),
    ]
    
    results = []
    for name, params in configs:
        total_pnl = 0
        total_trades = 0
        
        for sym, d in BACKTEST_DATA.items():
            wr = d["win_rate"] / 100
            trades = d["trades"]
            
            # 期望收益 = 胜率 * 止盈 - (1-胜率) * 止损
            pnl_per_trade = (wr * params.take_profit_pct) - ((1-wr) * params.stop_loss_pct)
            
            sym_pnl = pnl_per_trade * trades * (params.position_size / 100) * params.leverage
            total_pnl += sym_pnl
            total_trades += trades
        
        results.append({
            "name": name,
            "params": params,
            "total_trades": total_trades,
            "estimated_pnl": total_pnl,
            "pnl_per_trade": total_pnl / total_trades if total_trades > 0 else 0
        })
        
        ratio = params.take_profit_pct / params.stop_loss_pct
        print(f"\n📋 {name}:")
        print(f"   止损{params.stop_loss_pct:.1f}% : 止盈{params.take_profit_pct:.1f}% = 1:{ratio:.1f}")
        print(f"   杠杆{params.leverage}x, 仓位{params.position_size:.0f}%")
        print(f"   模拟期望收益: {total_pnl:+.2f}%")
    
    # 推荐
    best = max(results, key=lambda x: x["estimated_pnl"])
    
    print("\n" + "=" * 70)
    print("✅ 推荐配置")
    print("=" * 70)
    print(f"\n🏆 {best['name']}")
    print(f"   止损: {best['params'].stop_loss_pct:.1f}%")
    print(f"   止盈: {best['params'].take_profit_pct:.1f}%")
    print(f"   盈亏比: 1:{best['params'].take_profit_pct/best['params'].stop_loss_pct:.1f}")
    print(f"   杠杆: {best['params'].leverage}x")
    print(f"   仓位: {best['params'].position_size:.0f}%")
    print(f"   追踪止损: {best['params'].trailing_stop_pct:.1f}%")
    print(f"\n   预期6个月收益: {best['estimated_pnl']:+.2f}%")
    
    # 保存
    output = {
        "current_problem": {
            "win_rate": "58.6% (良好)",
            "profit_loss_ratio": "0.58-0.69 (不佳)",
            "issue": "止损太紧，止盈太大"
        },
        "recommended": {
            "name": best["name"],
            "params": {
                "stop_loss_pct": best["params"].stop_loss_pct,
                "take_profit_pct": best["params"].take_profit_pct,
                "trailing_stop_pct": best["params"].trailing_stop_pct,
                "position_size_pct": best["params"].position_size,
                "leverage": best["params"].leverage
            },
            "expected_pnl_6m": best["estimated_pnl"]
        }
    }
    
    with open("risk_optimization_result.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n💾 结果已保存: risk_optimization_result.json")
    print("=" * 70)
    
    return best


if __name__ == "__main__":
    main()
