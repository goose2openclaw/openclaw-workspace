#!/usr/bin/env python3
"""
👑 跟大哥 - 做市协作工具
版本: v1.0
日期: 2026-05-03

决策等式:
D_follow = α(Volume) + β(MA) + γ(Momentum)

参数:
α = 0.40 (量比权重)
β = 0.30 (均线权重)
γ = 0.30 (动量权重)
"""

class FollowTool:
    def __init__(self):
        self.name = "跟大哥"
        self.type = "follow"
        self.params = {
            "alpha": 0.40,
            "beta": 0.30,
            "gamma": 0.30
        }
        self.stop_loss = 0.03  # -3%
        self.take_profit = 0.08  # +8%
        
    def calculate(self, market_data):
        """
        计算跟大哥分数
        
        market_data = {
            "volume_ratio": 2.0,    # 量比
            "ma5": 50000,
            "ma20": 49000,
            "ma60": 48000,
            "momentum_4h": 0.03,    # 4h动量
            "breakout": True          # 突破
        }
        """
        # 量比分数
        vol_ratio = market_data.get("volume_ratio", 1)
        if vol_ratio > 2.0:
            vol_score = 1.0
        elif vol_ratio > 1.5:
            vol_score = 0.8
        elif vol_ratio > 1.2:
            vol_score = 0.5
        else:
            vol_score = 0.2
        
        # MA多头排列
        ma5 = market_data.get("ma5", 0)
        ma20 = market_data.get("ma20", 0)
        ma60 = market_data.get("ma60", 0)
        
        if ma5 > ma20 > ma60:
            ma_score = 1.0
        elif ma5 > ma20:
            ma_score = 0.6
        else:
            ma_score = 0.3
        
        # 动量分数
        momentum = market_data.get("momentum_4h", 0)
        if momentum > 0.05:
            mom_score = 1.0
        elif momentum > 0.02:
            mom_score = 0.7
        elif momentum > 0:
            mom_score = 0.5
        else:
            mom_score = 0.2
        
        D = (self.params["alpha"] * vol_score +
             self.params["beta"] * ma_score +
             self.params["gamma"] * mom_score)
        
        return {
            "score": D,
            "signal": self.get_signal(D),
            "action": self.get_action(D),
            "position": self.get_position(D)
        }
    
    def get_signal(self, D):
        if D > 0.7:
            return "🟢买入30%"
        elif D > 0.5:
            return "🟡买入20%"
        elif D > 0.3:
            return "🟠观望"
        else:
            return "🔴暂停"
    
    def get_action(self, D):
        if D > 0.7:
            return "买入30%"
        elif D > 0.5:
            return "买入20%"
        elif D > 0.3:
            return "观望"
        else:
            return "暂停"
    
    def get_position(self, D):
        if D > 0.7:
            return 0.30
        elif D > 0.5:
            return 0.20
        elif D > 0.3:
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
    tool = FollowTool()
    
    print("=" * 60)
    print("👑 跟大哥 - 做市协作工具")
    print("=" * 60)
    
    samples = [
        {"name": "BTC放量", "volume_ratio": 2.5, "ma5": 52000, "ma20": 51000, "ma60": 50000, "momentum_4h": 0.04},
        {"name": "ETH缩量", "volume_ratio": 0.8, "ma5": 2300, "ma20": 2350, "ma60": 2300, "momentum_4h": 0.01},
        {"name": "SOL突破", "volume_ratio": 1.8, "ma5": 85, "ma20": 80, "ma60": 75, "momentum_4h": 0.06},
    ]
    
    for s in samples:
        result = tool.calculate(s)
        print(f"\n{s['name']}:")
        print(f"  量比: {s['volume_ratio']:.1f}x")
        print(f"  4h动量: {s['momentum_4h']*100:+.1f}%")
        print(f"  分数: {result['score']:.3f}")
        print(f"  信号: {result['signal']}")
        print(f"  仓位: {result['position']*100:.0f}%")
