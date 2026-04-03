#!/usr/bin/env python3
"""
🪿 GO2SE 北斗七鑫专家模式配置
声纳库趋势模型强烈信号后的止盈条件设置

恢复 2026.03.19 的配置
"""

# ==================== 声纳库配置 ====================

SONAR_CONFIG = {
    # 趋势模型配置
    "models": {
        "bullish": {
            "range": [70, 75],  # 70-75% 看涨
            "signal": "STRONG_BUY"
        },
        "bearish": {
            "range": [68, 75],  # 68-75% 看跌
            "signal": "STRONG_SELL"
        },
        "neutral": {
            "range": [67, 72],  # 67-72% 中性
            "signal": "NEUTRAL"
        }
    },
    
    # 强烈信号条件 (置信度阈值)
    "strong_signal_threshold": {
        "confidence_min": 7.0,  # 置信度 >= 7.0
        "model_consensus": 2,   # 至少2个模型共振
    },
    
    # 止盈条件 (已禁用)
    "take_profit": {
        "enabled": True,
        "remove_on_strong_signal": False,  # 强烈信号时移除止盈
        "conditions": [
            {
                "name": "strong_bull_exit",
                "trigger": "model_bullish_strong",
                "action": "take_profit",
                "targets": [
                    {"pct": 0.15, "exit_pct": 50},   # 15%收益, 卖出50%
                    {"pct": 0.25, "exit_pct": 80},   # 25%收益, 卖出80%
                    {"pct": 0.30, "exit_pct": 100},  # 30%收益, 全部卖出
                ]
            },
            {
                "name": "strong_bear_exit", 
                "trigger": "model_bearish_strong",
                "action": "stop_loss",
                "targets": [
                    {"pct": -0.05, "exit_pct": 100},  # -5%止损
                ]
            },
            {
                "name": "ma_exit",
                "trigger": "price_below_ma",
                "action": "exit_all",
                "targets": [
                    {"pct": 0, "exit_pct": 100},  # 跌破MA20, 全部卖出
                ]
            }
        ]
    }
}

# ==================== 策略止盈配置 ====================

STRATEGY_TAKE_PROFIT = {
    "rabbit": {
        "take_profit": 0.30,     # 30%止盈
        "stop_loss": -0.10,      # 10%止损
        "trailing_stop": 0.05,    # 5%追踪止损
        "exit_conditions": ["ma20_break", "rsi_overbought", "time_based"]
    },
    "mole": {
        "take_profit": 0.15,     # 15%止盈
        "stop_loss": -0.08,      # 8%止损
        "trailing_stop": 0.03,   # 3%追踪止损
        "exit_conditions": ["volatility_normalize", "rsi_extreme"]
    },
    "oracle": {
        "take_profit": 0.20,     # 20%止盈
        "stop_loss": -0.10,      # 10%止损
        "exit_conditions": ["event_resolved", "probability_shift"]
    },
    "leader": {
        "take_profit": 0.10,     # 10%止盈
        "stop_loss": -0.05,      # 5%止损
        "exit_conditions": ["spread_normalize"]
    }
}

# ==================== 专家模式执行规则 ====================

EXPERT_MODE_RULES = {
    # 双轨通道
    "dual_channel": {
        "fast_track": {
            "condition": "confidence >= 7.0",
            "action": "EXECUTE_IMMEDIATE",
            "priority": 1
        },
        "deep_track": {
            "condition": "confidence < 7.0", 
            "action": "DETAILED_ANALYSIS",
            "priority": 2
        }
    },
    
    # 最终决策
    "final_decision": {
        "EXECUTE": {
            "conditions": ["confidence >= 7.0", "model_consensus >= 2"],
            "output": "EXECUTE + 工具 + 仓位 + 止盈"
        },
        "WAIT": {
            "conditions": ["confidence < 7.0"],
            "output": "WAIT + 观察 + 等待时机"
        }
    },
    
    # 置信度评分 (5步法)
    "confidence_5_steps": {
        "step1": {"name": "市场状态分析", "weight": 0.40},
        "step2": {"name": "声纳模型匹配", "weight": 0.25},
        "step3": {"name": "策略组合", "weight": 0.20},
        "step4": {"name": "风险评估", "weight": 0.10},
        "step5": {"name": "综合评分", "weight": 0.05}
    }
}

# ==================== 风控规则 ====================

RISK_CONTROL_RULES = {
    "R001": {"name": "仓位限制", "condition": "position > 0.80", "action": "BLOCK"},
    "R002": {"name": "日内熔断", "condition": "daily_loss > 0.30", "action": "STOP_ALL"},
    "R003": {"name": "单笔风险", "condition": "risk > 0.05", "action": "REJECT"},
    "R004": {"name": "波动止损", "condition": "volatility > 0.08", "action": "REDUCE"},
    "R005": {"name": "流动性检查", "condition": "volume < 100000", "action": "WARN"},
    "R006": {"name": "API故障", "condition": "error_rate > 0.01", "action": "FALLBACK"},
    "R007": {"name": "异常检测", "condition": "deviation > 3σ", "action": "ALERT"},
    "R008": {"name": "情绪过热", "condition": "sentiment > 5σ", "action": "COOLDOWN"}
}


def get_take_profit_for_signal(signal_type: str, profit_pct: float) -> dict:
    """根据信号类型和当前收益获取止盈建议"""
    
    if signal_type not in SONAR_CONFIG["take_profit"]["conditions"]:
        return {"action": "hold", "exit_pct": 0}
    
    condition = SONAR_CONFIG["take_profit"]["conditions"][signal_type]
    
    for target in condition["targets"]:
        if profit_pct >= target["pct"] * 100:
            return {
                "action": "take_profit",
                "exit_pct": target["exit_pct"],
                "target_profit": target["pct"] * 100
            }
    
    return {"action": "hold", "exit_pct": 0}


def check_expert_mode_conditions(confidence: float, model_signals: list) -> dict:
    """检查专家模式执行条件"""
    
    rules = EXPERT_MODE_RULES["dual_channel"]
    
    # 快速通道
    if confidence >= 7.0:
        return {
            "channel": "fast_track",
            "action": "EXECUTE_IMMEDIATE",
            "priority": 1,
            "confidence": confidence
        }
    
    # 深度通道
    return {
        "channel": "deep_track",
        "action": "DETAILED_ANALYSIS", 
        "priority": 2,
        "confidence": confidence
    }


if __name__ == "__main__":
    import json
    
    print("=" * 60)
    print("🪿 北斗七鑫专家模式配置")
    print("=" * 60)
    
    print("\n📡 声纳库配置:")
    print(json.dumps(SONAR_CONFIG, indent=2, ensure_ascii=False)[:500] + "...")
    
    print("\n💰 策略止盈配置:")
    for strat, config in STRATEGY_TAKE_PROFIT.items():
        print(f"  {strat}: 止盈{config['take_profit']*100:.0f}%, 止损{abs(config['stop_loss'])*100:.0f}%")
    
    print("\n🛡️ 风控规则:")
    for rule_id, rule in RISK_CONTROL_RULES.items():
        print(f"  {rule_id}: {rule['name']} - {rule['condition']}")
    
    print("\n✅ 配置已恢复")
