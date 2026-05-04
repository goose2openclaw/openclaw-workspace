#!/usr/bin/env python3
"""
🐰 打兔子 - 主流趋势工具
版本: v1.0
日期: 2026-05-03

决策等式:
D_trend = α(MA_cross) + β(Momentum) + γ(Volume) - δ(Volatility)

参数:
α = 0.35 (均线交叉)
β = 0.30 (动量)
γ = 0.25 (成交量)
δ = 0.10 (波动率)
"""

class RabbitTool:
    def __init__(self):
        self.name = "打兔子"
        self.type = "trend"
        self.params = {
            "alpha": 0.35,
            "beta": 0.30,
            "gamma": 0.25,
            "delta": 0.10
        }
        self.stop_loss = 0.05  # -5%
        self.take_profit = 0.15  # +15%
        
    def calculate(self, market_data):
        """
        计算趋势分数
        
        market_data = {
            "ma5": 50000,
            "ma20": 49000,
            "ma60": 48000,
            "momentum": 0.03,      # 动量
            "volume_ratio": 1.5,    # 量比
            "volatility": 0.02      # 波动率
        }
        """
        # MA交叉信号
        ma5 = market_data.get("ma5", 0)
        ma20 = market_data.get("ma20", 0)
        ma60 = market_data.get("ma60", 0)
        
        if ma5 > ma20 > ma60:
            ma_score = 1.0
        elif ma5 > ma20:
            ma_score = 0.7
        elif ma5 > ma60:
            ma_score = 0.5
        else:
            ma_score = 0.2
        
        # 动量分数
        momentum = market_data.get("momentum", 0)
        if momentum > 0.05:
            mom_score = 1.0
        elif momentum > 0.02:
            mom_score = 0.7
        elif momentum > 0:
            mom_score = 0.5
        else:
            mom_score = 0.2
        
        # 成交量分数
        vol_ratio = market_data.get("volume_ratio", 1)
        vol_score = min(vol_ratio / 2, 1.0)
        
        # 波动率分数
        volatility = market_data.get("volatility", 0)
        vola_score = 1.0 - min(volatility / 0.1, 1.0)
        
        D = (self.params["alpha"] * ma_score +
             self.params["beta"] * mom_score +
             self.params["gamma"] * vol_score -
             self.params["delta"] * vola_score)
        
        return {
            "score": D,
            "signal": self.get_signal(D),
            "action": self.get_action(D),
            "position": self.get_position(D)
        }
    
    def get_signal(self, D):
        if D > 0.8:
            return "🟢强烈买入"
        elif D > 0.6:
            return "🟡买入"
        elif D > 0.4:
            return "🟠观望"
        else:
            return "🔴回避"
    
    def get_action(self, D):
        if D > 0.8:
            return "买入30%"
        elif D > 0.6:
            return "买入20%"
        elif D > 0.4:
            return "买入10%"
        else:
            return "观望"
    
    def get_position(self, D):
        if D > 0.8:
            return 0.30
        elif D > 0.6:
            return 0.20
        elif D > 0.4:
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
    tool = RabbitTool()
    
    print("=" * 60)
    print("🐰 打兔子 - 主流趋势工具")
    print("=" * 60)
    
    # 示例数据
    samples = [
        {"name": "BTC强势", "ma5": 52000, "ma20": 51000, "ma60": 50000, "momentum": 0.04, "volume_ratio": 1.8, "volatility": 0.02},
        {"name": "ETH盘整", "ma5": 2300, "ma20": 2350, "ma60": 2300, "momentum": 0.01, "volume_ratio": 1.0, "volatility": 0.03},
        {"name": "SOL下跌", "ma5": 80, "ma20": 85, "ma60": 90, "momentum": -0.02, "volume_ratio": 0.8, "volatility": 0.05},
    ]
    
    for s in samples:
        result = tool.calculate(s)
        print(f"\n{s['name']}:")
        print(f"  MA: {s['ma5']}/{s['ma20']}/{s['ma60']}")
        print(f"  动量: {s['momentum']*100:+.1f}%")
        print(f"  分数: {result['score']:.3f}")
        print(f"  信号: {result['signal']}")
        print(f"  仓位: {result['position']*100:.0f}%")
