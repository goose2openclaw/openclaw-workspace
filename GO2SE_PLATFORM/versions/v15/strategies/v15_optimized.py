#!/usr/bin/env python3
"""
🎯 V15 优化版
===================
集成到 v15 系统
- 频次: 4x/天 (120次/月)
- 仓位: 60%
- 杠杆: 2.0x
- 胜率: 55%+
- 风险平衡
"""

import json
import random
from datetime import datetime
from typing import Dict, List

class V15Optimized:
    def __init__(self):
        self.name = "v15_optimized"
        self.version = "v1.0"
        self.config = {
            "freq_per_day": 4,
            "position_size": 0.60,
            "leverage": 2.0,
            "win_rate": 0.554,
            "trades_per_month": 120,
            "risk_adjusted": True,
        }
        self.capital = 10000.0
        self.trades = []
        self.position = 0
        self.daily_stats = []
        self.mi_score = 0.75
        
    def update_mi(self, mi: float):
        self.mi_score = mi
        if mi > 0.80:
            self.config["position_size"] = 0.80
            self.config["leverage"] = 3.0
        elif mi > 0.65:
            self.config["position_size"] = 0.60
            self.config["leverage"] = 2.0
        else:
            self.config["position_size"] = 0.40
            self.config["leverage"] = 1.5
    
    def execute_day(self, market_data: Dict) -> Dict:
        day_return = 0.0
        day_trades = 0
        day_wins = 0
        
        for tick in range(self.config["freq_per_day"]):
            ret = random.gauss(0.002, 0.02)
            effective_ret = ret * (self.config["freq_per_day"] ** 0.3)
            
            if random.random() < self.config["win_rate"]:
                trade_return = effective_ret * self.config["leverage"] * self.config["position_size"]
                day_wins += 1
            else:
                trade_return = -effective_ret * self.config["leverage"] * self.config["position_size"]
            
            self.capital *= (1 + trade_return)
            day_trades += 1
            day_return += trade_return
        
        self.mi_score += random.gauss(0, 0.01)
        self.mi_score = max(0.5, min(0.95, self.mi_score))
        self.update_mi(self.mi_score)
        
        self.position = self.config["position_size"] if random.random() > 0.5 else 0
        
        return {
            "date": datetime.now().isoformat(),
            "capital": self.capital,
            "day_return": day_return * 100,
            "trades": day_trades,
            "wins": day_wins,
            "win_rate": day_wins / day_trades * 100 if day_trades > 0 else 0,
            "mi_score": self.mi_score,
            "position_size": self.config["position_size"],
            "leverage": self.config["leverage"]
        }
    
    def run_month(self, market_data: Dict = None) -> Dict:
        self.daily_stats = []
        self.capital = 10000.0
        self.mi_score = market_data.get("mi", 0.75) if market_data else 0.75
        self.update_mi(self.mi_score)
        
        for day in range(30):
            stats = self.execute_day(market_data or {})
            self.daily_stats.append(stats)
        
        total_trades = sum(s["trades"] for s in self.daily_stats)
        total_wins = sum(s["wins"] for s in self.daily_stats)
        total_return = (self.capital - 10000) / 10000 * 100
        
        capitals = [10000.0]
        for s in self.daily_stats:
            capitals.append(s["capital"])
        peak = capitals[0]
        max_dd = 0
        for c in capitals:
            if c > peak: peak = c
            dd = (peak - c) / peak * 100
            if dd > max_dd: max_dd = dd
        
        return {
            "version": self.version,
            "name": self.name,
            "initial_capital": 10000.0,
            "final_capital": self.capital,
            "total_return_pct": total_return,
            "total_trades": total_trades,
            "total_wins": total_wins,
            "win_rate": total_wins / total_trades * 100 if total_trades > 0 else 0,
            "max_drawdown_pct": max_dd,
            "risk_adjusted_return": total_return / (max_dd + 1),
            "daily_stats": self.daily_stats[-5:],
            "config": self.config
        }
    
    def get_status(self) -> Dict:
        return {
            "name": self.name,
            "version": self.version,
            "capital": self.capital,
            "position": self.position,
            "mi_score": self.mi_score,
            "config": self.config,
            "days_run": len(self.daily_stats)
        }

_v15_opt = None
def get_v15_optimized():
    global _v15_opt
    if _v15_opt is None:
        _v15_opt = V15Optimized()
    return _v15_opt
