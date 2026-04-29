#!/usr/bin/env python3
"""
⚖️ 打工投资自主切换系统 v2
=========================
打工模式: Wool空投 + Crowdsource众包 + Hitchhiker
投资模式: Rabbit + Mole + VV6

自主切换:
- Mi > 0.75 → 投资模式
- Mi < 0.60 → 打工模式  
- Mi 0.60-0.75 → 混合模式
"""

import json
import random
from datetime import datetime
from enum import Enum

class Mode(Enum):
    WORK = "work"
    INVEST = "invest"
    HYBRID = "hybrid"

class DualModeEngine:
    def __init__(self):
        self.name = "dual_mode_engine"
        self.version = "v2.0"
        
        self.current_mode = Mode.HYBRID
        self.work_capital = 10000.0
        self.invest_capital = 10000.0
        self.total_capital = 20000.0
        
        self.work_days = 0
        self.invest_days = 0
        self.hybrid_days = 0
        self.consecutive_invest_losses = 0
        self.total_work_income = 0
        self.total_invest_pnl = 0
        
        self.mode_history = []
        self.daily_results = []
        
    def get_mi(self) -> float:
        return random.uniform(0.50, 0.95)
    
    def determine_mode(self) -> Mode:
        mi = self.get_mi()
        if mi > 0.75:
            return Mode.INVEST
        elif mi < 0.60:
            return Mode.WORK
        else:
            return Mode.HYBRID
    
    def execute_work_day(self) -> float:
        """打工日收入: Wool + Crowdsource + Hitchhiker"""
        # Wool空投
        wool_income = 0
        if random.random() < 0.85:  # 85% 成功率
            wool_income = 8 * 75  # 8小时 x $75/小时
        
        # Crowdsource众包
        crowd_income = 0
        if random.random() < 0.80:
            crowd_income = 6 * 55  # 6小时 x $55/小时
        
        # Hitchhiker
        hitch_income = 0
        if random.random() < 0.75:
            hitch_income = 4 * 120  # 4小时 x $120/小时
        
        total = wool_income + crowd_income + hitch_income
        self.work_capital += total
        self.total_work_income += total
        return total
    
    def execute_invest_day(self) -> float:
        """投资日盈亏"""
        mi = self.get_mi()
        
        # 根据Mi确定市场
        if mi > 0.80:
            regime = "bull"
            daily_ret = random.gauss(0.02, 0.03)  # 牛市 2% 日均
        elif mi < 0.60:
            regime = "bear"
            daily_ret = random.gauss(-0.01, 0.025)  # 熊市 -1%
        else:
            regime = "neutral"
            daily_ret = random.gauss(0.005, 0.02)  # 中性 0.5%
        
        leverage = 3.0
        
        # 执行3-5笔交易
        trades = random.randint(3, 5)
        wins = 0
        for _ in range(trades):
            win_prob = 0.55 + (mi - 0.5) * 0.3  # 55-70% 胜率
            is_win = random.random() < win_prob
            if is_win:
                wins += 1
        
        win_rate = wins / trades if trades > 0 else 0
        
        # 盈亏
        if win_rate > 0.5:
            pnl = self.invest_capital * daily_ret * leverage * win_rate * 1.5
        else:
            pnl = self.invest_capital * daily_ret * leverage * win_rate * -0.5
        
        self.invest_capital += pnl
        self.total_invest_pnl += pnl
        
        if pnl < 0:
            self.consecutive_invest_losses += 1
        else:
            self.consecutive_invest_losses = 0
        
        return pnl
    
    def execute_hybrid_day(self) -> tuple:
        """混合模式: 60%打工 + 40%投资"""
        work_part = self.execute_work_day() * 0.6  # 打工收入60%
        invest_part = self.execute_invest_day() * 0.4  # 投资盈亏40%
        return work_part, invest_part
    
    def run_day(self) -> dict:
        mi = self.get_mi()
        new_mode = self.determine_mode()
        
        # 切换
        if new_mode != self.current_mode:
            self.mode_history.append({
                "timestamp": datetime.now().isoformat(),
                "from": self.current_mode.value,
                "to": new_mode.value,
                "mi": mi
            })
            self.current_mode = new_mode
        
        # 执行
        if self.current_mode == Mode.WORK:
            income = self.execute_work_day()
            result = {"mode": "work", "income": income, "invest_pnl": 0}
            self.work_days += 1
        elif self.current_mode == Mode.INVEST:
            pnl = self.execute_invest_day()
            result = {"mode": "invest", "income": 0, "invest_pnl": pnl}
            self.invest_days += 1
        else:
            work_part, invest_part = self.execute_hybrid_day()
            result = {"mode": "hybrid", "income": work_part, "invest_pnl": invest_part}
            self.hybrid_days += 1
        
        self.total_capital = self.work_capital + self.invest_capital
        
        return {
            "day": len(self.daily_results) + 1,
            "mi": mi,
            "mode": self.current_mode.value,
            **result,
            "work_capital": self.work_capital,
            "invest_capital": self.invest_capital,
            "total_capital": self.total_capital
        }
    
    def run_month(self, days: int = 30) -> dict:
        self.daily_results = []
        for _ in range(days):
            self.daily_results.append(self.run_day())
        
        mode_counts = {"work": 0, "invest": 0, "hybrid": 0}
        for r in self.daily_results:
            mode_counts[r["mode"]] = mode_counts.get(r["mode"], 0) + 1
        
        return {
            "version": self.version,
            "initial_capital": 20000.0,
            "final_capital": self.total_capital,
            "total_return_pct": (self.total_capital - 20000.0) / 20000.0 * 100,
            "work_income": self.total_work_income,
            "invest_pnl": self.total_invest_pnl,
            "mode_distribution": mode_counts,
            "work_days": self.work_days,
            "invest_days": self.invest_days,
            "hybrid_days": self.hybrid_days,
            "daily_results": self.daily_results[-5:]
        }
    
    def get_status(self) -> dict:
        return {
            "current_mode": self.current_mode.value,
            "work_capital": self.work_capital,
            "invest_capital": self.invest_capital,
            "total_capital": self.total_capital,
            "work_days": self.work_days,
            "invest_days": self.invest_days,
            "consecutive_losses": self.consecutive_invest_losses
        }

_dual_engine = None

def get_dual_mode_engine():
    global _dual_engine
    if _dual_engine is None:
        _dual_engine = DualModeEngine()
    return _dual_engine
