#!/usr/bin/env python3
"""
🚗 搭便车 - 跟单分成工具
版本: v1.0
日期: 2026-05-03

决策等式:
D_hitch = α(WinRate) + β(Sharpe) + γ(Trend) - δ(Drawdown)

参数:
α = 0.40 (胜率权重)
β = 0.30 (夏普比率)
γ = 0.20 (趋势)
δ = 0.10 (回撤)
"""

class HitchTool:
    def __init__(self):
        self.name = "搭便车"
        self.type = "hitchhike"
        self.params = {
            "alpha": 0.40,
            "beta": 0.30,
            "gamma": 0.20,
            "delta": 0.10
        }
        self.stop_loss = 0.05  # -5%
        self.take_profit = 0.10  # +10%
        
    def calculate(self, market_data):
        """
        计算跟单分数
        
        market_data = {
            "win_rate": 65,        # 胜率 (%)
            "sharpe_ratio": 1.2,   # 夏普比率
            "ma_trend": True,      # MA趋势
            "max_drawdown": 0.03   # 最大回撤
        }
        """
        # 胜率分数
        win_rate = market_data.get("win_rate", 50)
        if win_rate > 65:
            win_score = 1.0
        elif win_rate > 55:
            win_score = 0.8
        elif win_rate > 50:
            win_score = 0.5
        else:
            win_score = 0.2
        
        # 夏普比率分数
        sharpe = market_data.get("sharpe_ratio", 0)
        if sharpe > 1.5:
            sharpe_score = 1.0
        elif sharpe > 1.0:
            sharpe_score = 0.8
        elif sharpe > 0.5:
            sharpe_score = 0.6
        else:
            sharpe_score = 0.3
        
        # 趋势分数
        trend_score = 1.0 if market_data.get("ma_trend") else 0.3
        
        # 回撤分数
        drawdown = market_data.get("max_drawdown", 0.1)
        draw_score = 1.0 - min(drawdown / 0.1, 1.0)
        
        D = (self.params["alpha"] * win_score +
             self.params["beta"] * sharpe_score +
             self.params["gamma"] * trend_score -
             self.params["delta"] * draw_score)
        
        return {
            "score": D,
            "signal": self.get_signal(D),
            "action": self.get_action(D),
            "position": self.get_position(D)
        }
    
    def get_signal(self, D):
        if D > 0.6:
            return "🟢跟单"
        elif D > 0.4:
            return "🟡轻仓"
        elif D > 0.2:
            return "🟠观望"
        else:
            return "🔴避免"
    
    def get_action(self, D):
        if D > 0.6:
            return "跟单30%"
        elif D > 0.4:
            return "轻仓20%"
        elif D > 0.2:
            return "观望"
        else:
            return "避免"
    
    def get_position(self, D):
        if D > 0.6:
            return 0.30
        elif D > 0.4:
            return 0.20
        elif D > 0.2:
            return 0.10
        else:
            return 0.0
    
    def exit_strategy(self, position_pnl):
        """
        退出策略
        """
        if position_pnl >= self.take_profit:
            return {"action": "止盈", "reason": f"+{self.take_profit*100}%"}
        elif position_pnl <= -self.stop_loss:
            return {"action": "止损", "reason": f"-{self.stop_loss*100}%"}
        else:
            return {"action": "持有", "reason": "未触发条件"}

if __name__ == "__main__":
    tool = HitchTool()
    
    print("=" * 60)
    print("🚗 搭便车 - 跟单分成工具")
    print("=" * 60)
    
    samples = [
        {"name": "BTC跟单", "win_rate": 68, "sharpe_ratio": 1.5, "ma_trend": True, "max_drawdown": 0.03},
        {"name": "ETH跟单", "win_rate": 58, "sharpe_ratio": 0.8, "ma_trend": True, "max_drawdown": 0.05},
        {"name": "SOL跟单", "win_rate": 48, "sharpe_ratio": 0.4, "ma_trend": False, "max_drawdown": 0.08},
    ]
    
    for s in samples:
        result = tool.calculate(s)
        print(f"\n{s['name']}:")
        print(f"  胜率: {s['win_rate']}%")
        print(f"  夏普: {s['sharpe_ratio']}")
        print(f"  分数: {result['score']:.3f}")
        print(f"  信号: {result['signal']}")
        print(f"  仓位: {result['position']*100:.0f}%")
