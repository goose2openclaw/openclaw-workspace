"""
🚀 收益优化配置 v3
====================
2026-04-29 收益提升方案

目标: 30天收益 50%+
"""

PROFIT_OPTIMIZATION = {
    # 策略1: 持仓优化
    "position": {
        "normal": 0.65,    # 60% → 65%
        "expert": 0.85,     # 80% → 85%
        "dynamic": True       # 动态调整
    },
    
    # 策略2: 止盈止损优化
    "stop_loss": {
        "normal": 0.08,    # 10% → 8%
        "expert": 0.06     # 8% → 6%
    },
    "take_profit": {
        "normal": 0.35,    # 30% → 35%
        "expert": 0.30     # 25% → 30%
    },
    
    # 策略3: 交易频率优化
    "frequency": {
        "normal_interval": 180,  # 300秒 → 180秒
        "expert_interval": 120,   # 更频繁
        "min_signal_strength": 0.6
    },
    
    # 策略4: 动态仓位
    "dynamic_position": {
        "strong_trend": 0.20,   # 趋势强时20%
        "weak_trend": 0.08,     # 趋势弱时8%
        "neutral": 0.12         # 中性12%
    },
    
    # 预期收益
    "expected": {
        "normal_monthly": 0.25,   # 25%
        "expert_monthly": 0.50,   # 50%+
        "improvement": "+35%"
    }
}
