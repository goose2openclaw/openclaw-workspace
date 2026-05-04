#!/usr/bin/env python3
"""
🐹 打地鼠 - 高频量化工具
版本: v1.0
日期: 2026-05-03

决策等式:
D_mole = α(Volatility) + β(Volume) - γ(StopLoss)

参数:
α = 0.40 (波动率)
β = 0.35 (成交量)
γ = 0.25 (止损风险)
"""

class MoleTool:
    def __init__(self):
        self.name = "打地鼠"
        self.type = "highfreq"
        self.params = {
            "alpha": 0.40,
            "beta": 0.35,
            "gamma": 0.25
        }
        self.stop_loss = 0.02  # -2%
        self.take_profit = 0.03  # +3%
        
    def calculate(self, market_data):
        """
        计算波动分数
        
        market_data = {
            "volatility": 0.05,      # 波动率
            "volume_ratio": 2.0,       # 量比
            "price": 0.05,            # 当前价格
            "position_size": 0.1        # 仓位
        }
        """
        # 波动率分数 (2-10%最佳)
        vol = market_data.get("volatility", 0)
        if 0.02 <= vol <= 0.10:
            vol_score = 1.0
        elif vol > 0.10:
            vol_score = 0.7
        elif vol > 0.05:
            vol_score = 0.8
        else:
            vol_score = 0.3
        
        # 成交量分数
        vol_ratio = market_data.get("volume_ratio", 1)
        vol_score = min(vol_ratio / 2, 1.0)
        
        # 止损风险
        stop_pct = self.stop_loss
        risk_score = 1.0 - stop_pct * 10
        
        D = (self.params["alpha"] * vol_score +
             self.params["beta"] * vol_score -
             self.params["gamma"] * risk_score)
        
        return {
            "score": D,
            "signal": self.get_signal(D),
            "action": self.get_action(D),
            "position": self.get_position(D)
        }
    
    def get_signal(self, D):
        if D > 0.7:
            return "🟢买入"
        elif D > 0.5:
            return "🟡轻仓"
        elif D > 0.3:
            return "🟠观望"
        else:
            return "🔴避免"
    
    def get_action(self, D):
        if D > 0.7:
            return "买入"
        elif D > 0.5:
            return "轻仓买入"
        elif D > 0.3:
            return "观望"
        else:
            return "避免"
    
    def get_position(self, D):
        if D > 0.7:
            return 0.10
        elif D > 0.5:
            return 0.05
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
    tool = MoleTool()
    
    print("=" * 60)
    print("🐹 打地鼠 - 高频量化工具")
    print("=" * 60)
    
    samples = [
        {"name": "ORDI", "volatility": 0.08, "volume_ratio": 2.5, "price": 5.0},
        {"name": "DOGE", "volatility": 0.12, "volume_ratio": 1.5, "price": 0.1},
        {"name": "LINK", "volatility": 0.03, "volume_ratio": 1.2, "price": 9.0},
    ]
    
    for s in samples:
        result = tool.calculate(s)
        print(f"\n{s['name']}:")
        print(f"  波动率: {s['volatility']*100:.1f}%")
        print(f"  量比: {s['volume_ratio']:.1f}x")
        print(f"  分数: {result['score']:.3f}")
        print(f"  信号: {result['signal']}")
        print(f"  仓位: {result['position']*100:.0f}%")
