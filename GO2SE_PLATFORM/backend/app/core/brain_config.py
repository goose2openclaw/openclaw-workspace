"""
双脑配置 - 左脑/右脑平行配置
"""
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class BrainConfig:
    name: str
    mode: str  # "normal" | "expert"
    leverage: float
    take_profit: float
    stop_loss: float
    win_rate: float
    max_position: float
    description: str

LEFT_BRAIN = BrainConfig(
    name="左脑",
    mode="normal",
    leverage=2.0,
    take_profit=0.12,
    stop_loss=0.04,
    win_rate=0.72,
    max_position=0.25,
    description="普通模式 - 稳健投资"
)

RIGHT_BRAIN = BrainConfig(
    name="右脑",
    mode="expert", 
    leverage=3.0,
    take_profit=0.18,
    stop_loss=0.025,
    win_rate=0.78,
    max_position=0.30,
    description="专家模式 - 高收益高风险"
)

def get_brain_config(brain: str) -> BrainConfig:
    """获取脑配置"""
    if brain == "right":
        return RIGHT_BRAIN
    return LEFT_BRAIN

def sync_brains():
    """同步双脑配置"""
    return {
        "left": {
            **LEFT_BRAIN.__dict__,
            "status": "active"
        },
        "right": {
            **RIGHT_BRAIN.__dict__,
            "status": "standby"
        },
        "last_sync": "2026-04-05T13:45:00Z"
    }
