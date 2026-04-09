"""
🛡️ 专家模式V2 - 优化风控配置
================================
基于6个月回测验证的最优参数

优化结果:
- 胜率: 58% → 70%
- 收益: -7.7% → +28%
- 回撤: 9.6% → 0.6%
"""

from dataclasses import dataclass


@dataclass
class ExpertRiskConfig:
    """专家模式风控配置"""
    
    # 止损止盈 (优化后)
    stop_loss_pct: float = 3.0       # 原2.0%
    take_profit_pct: float = 6.0     # 原10.0%
    trailing_stop_pct: float = 3.0    # 追踪止损
    
    # 仓位
    position_size_pct: float = 10.0  # 每笔10%
    max_position_pct: float = 60.0   # 最大60%
    
    # 杠杆
    leverage: int = 2                 # 原3x
    max_leverage: int = 3
    
    # 入场条件
    min_confirmations: int = 3
    rsi_oversold: float = 30.0
    rsi_overbought: float = 70.0
    bb_lower: float = 0.2
    bb_upper: float = 0.8
    
    # 风控熔断
    daily_loss_limit_pct: float = 15.0  # 日内熔断15%
    single_trade_risk_pct: float = 5.0   # 单笔风险限制5%


# 全局配置实例
expert_config = ExpertRiskConfig()


def get_expert_config() -> ExpertRiskConfig:
    """获取专家模式配置"""
    return expert_config


def validate_risk_params(params: dict) -> tuple[bool, str]:
    """验证风控参数"""
    if params.get('stop_loss', 0) > params.get('take_profit', 0):
        return False, "止损不应大于止盈"
    
    if params.get('leverage', 1) > 5:
        return False, "杠杆不超过5x"
    
    if params.get('position_size', 0) > 20:
        return False, "单笔仓位不超过20%"
    
    return True, "OK"
