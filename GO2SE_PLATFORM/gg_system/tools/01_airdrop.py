#!/usr/bin/env python3
"""
🛠️ 薅羊毛 - 空投工具
版本: v1.0
日期: 2026-05-03

决策等式:
D_airdrop = α(TVL) + β(Protocol) + γ(Innovation) - δ(Cost)

参数:
α = 0.35 (TVL权重)
β = 0.25 (协议安全性)
γ = 0.25 (创新性)
δ = 0.15 (成本风险)
"""

import requests
import json
from datetime import datetime

class AirdropTool:
    def __init__(self):
        self.name = "薅羊毛"
        self.type = "airdrop"
        self.params = {
            "alpha": 0.35,
            "beta": 0.25,
            "gamma": 0.25,
            "delta": 0.15
        }
        self.thresholds = {
            "strong": 0.7,
            "medium": 0.5,
            "weak": 0.3
        }
        
    def calculate(self, protocol_data):
        """
        计算空投分数
        
        protocol_data = {
            "name": "zkSync",
            "tvl": 500_000_000,  # TVL
            "audited": True,        # 审计
            "innovation": 0.8,      # 创新指数
            "cost": 5,             # 参与成本
            "potential": 100         # 潜在收益
        }
        """
        tvl_score = min(protocol_data.get("tvl", 0) / 1e9, 1.0)  # 归一化
        audit_score = 1.0 if protocol_data.get("audited") else 0.5
        innov_score = protocol_data.get("innovation", 0.5)
        cost_score = 1.0 - min(protocol_data.get("cost", 10) / 10, 1.0)
        
        D = (self.params["alpha"] * tvl_score +
             self.params["beta"] * audit_score +
             self.params["gamma"] * innov_score -
             self.params["delta"] * cost_score)
        
        return {
            "score": D,
            "signal": self.get_signal(D),
            "action": self.get_action(D),
            "position": self.get_position(D)
        }
    
    def get_signal(self, D):
        if D > self.thresholds["strong"]:
            return "🟢强烈参与"
        elif D > self.thresholds["medium"]:
            return "🟡重点参与"
        elif D > self.thresholds["weak"]:
            return "🟠普通参与"
        else:
            return "🔴避免"
    
    def get_action(self, D):
        if D > self.thresholds["strong"]:
            return "立即参与"
        elif D > self.thresholds["medium"]:
            return "重点参与"
        elif D > self.thresholds["weak"]:
            return "普通参与"
        else:
            return "跳过"
    
    def get_position(self, D):
        if D > self.thresholds["strong"]:
            return 0.30  # 30%仓位
        elif D > self.thresholds["medium"]:
            return 0.20
        elif D > self.thresholds["weak"]:
            return 0.10
        else:
            return 0.0
    
    def exit_strategy(self, status):
        """
        退出策略
        status = {
            "duration_days": 30,
            "profit_pct": 50,
            "airdrop_received": True
        }
        """
        if status.get("airdrop_received"):
            return {"action": "变现", "reason": "空投已到账"}
        elif status.get("duration_days", 0) > 90:
            return {"action": "评估", "reason": "超过90天，考虑退出"}
        else:
            return {"action": "持有", "reason": "等待空投"}

# 示例协议数据
sample_protocols = [
    {"name": "zkSync", "tvl": 500_000_000, "audited": True, "innovation": 0.9, "cost": 5, "potential": 100},
    {"name": "Linea", "tvl": 300_000_000, "audited": True, "innovation": 0.7, "cost": 5, "potential": 80},
    {"name": "StarkNet", "tvl": 200_000_000, "audited": True, "innovation": 0.8, "cost": 10, "potential": 120},
]

if __name__ == "__main__":
    tool = AirdropTool()
    
    print("=" * 60)
    print("🛠️ 薅羊毛 - 空投工具")
    print("=" * 60)
    
    for proto in sample_protocols:
        result = tool.calculate(proto)
        print(f"\n{proto['name']}:")
        print(f"  分数: {result['score']:.3f}")
        print(f"  信号: {result['signal']}")
        print(f"  动作: {result['action']}")
        print(f"  仓位: {result['position']*100:.0f}%")
