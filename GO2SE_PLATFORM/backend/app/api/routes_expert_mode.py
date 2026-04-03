"""
Expert Mode API Routes - 专家模式API
==================================
高度灵活的专家模式配置:
- 杠杆调整
- 条件止盈移除
- 参数自由调教
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

router = APIRouter(prefix="/api/expert", tags=["专家模式"])


# ── 专家模式配置 ─────────────────────────────────────────────

EXPERT_LEVERAGE_LEVELS = [1, 2, 3, 5, 10, 20]

EXPERT_CONFIGS = {
    "rabbit": {
        "leverage_range": [1, 3],
        "params": {
            "rsi_oversold": {"default": 30, "min": 20, "max": 40, "step": 1},
            "rsi_overbought": {"default": 70, "min": 60, "max": 80, "step": 1},
            "ema_fast": {"default": 9, "min": 5, "max": 21, "step": 1},
            "ema_slow": {"default": 21, "min": 10, "max": 50, "step": 1},
            "adx_threshold": {"default": 25, "min": 15, "max": 40, "step": 1},
            "macd_fast": {"default": 12, "min": 8, "max": 20, "step": 1},
            "macd_slow": {"default": 26, "min": 20, "max": 40, "step": 1},
        },
        "conditional_tp": {
            "enabled": True,
            "conditions": ["trend_score > 80", "volume_surge > 3x", "rsi_extreme > 4h"],
        },
    },
    "mole": {
        "leverage_range": [1, 5],
        "params": {
            "volume_threshold": {"default": 3.0, "min": 1.5, "max": 10.0, "step": 0.5},
            "rsi_extreme": {"default": 70, "min": 60, "max": 90, "step": 1},
            "bb_deviation": {"default": 2.0, "min": 1.5, "max": 3.0, "step": 0.1},
            "atr_multiplier": {"default": 1.5, "min": 1.0, "max": 3.0, "step": 0.1},
        },
        "conditional_tp": {
            "enabled": True,
            "conditions": ["trend_score > 80", "volume_surge > 3x", "whale_inflow > 1M"],
        },
    },
    "oracle": {
        "leverage_range": [1, 3],
        "params": {
            "min_winrate": {"default": 0.65, "min": 0.50, "max": 0.85, "step": 0.01},
            "min_volume": {"default": 10000, "min": 1000, "max": 100000, "step": 1000},
            "sentiment_threshold": {"default": 0.65, "min": 0.50, "max": 0.85, "step": 0.01},
        },
        "conditional_tp": {"enabled": False},
    },
    "leader": {
        "leverage_range": [1, 5],
        "params": {
            "max_copy_ratio": {"default": 0.3, "min": 0.1, "max": 0.5, "step": 0.05},
            "spread_threshold": {"default": 0.002, "min": 0.001, "max": 0.005, "step": 0.0001},
            "signal_confidence": {"default": 0.70, "min": 0.50, "max": 0.90, "step": 0.01},
        },
        "conditional_tp": {
            "enabled": True,
            "conditions": ["signal_confirmed > 2 sources", "drawdown < 5%"],
        },
    },
    "hitchhiker": {
        "leverage_range": [1, 3],
        "params": {
            "max_traders": {"default": 10, "min": 1, "max": 20, "step": 1},
            "position_per_trader": {"default": 0.02, "min": 0.01, "max": 0.05, "step": 0.005},
            "max_drawdown_stop": {"default": 0.15, "min": 0.05, "max": 0.25, "step": 0.01},
        },
        "conditional_tp": {"enabled": False},
    },
}


# ── Pydantic Models ─────────────────────────────────────────────

class ExpertConfig(BaseModel):
    """专家模式配置"""
    tool: str
    enabled: bool = True
    leverage: int = 1
    params: Dict[str, float] = {}
    conditional_tp_enabled: bool = True
    conditional_tp_conditions: List[str] = []
    auto_adjust: bool = False


class ExpertModeRequest(BaseModel):
    """专家模式请求"""
    tool: str
    action: str  # get / set / reset
    config: Optional[ExpertConfig] = None


class ExpertModeResponse(BaseModel):
    """专家模式响应"""
    tool: str
    enabled: bool
    leverage: int
    params: Dict[str, Any]
    conditional_tp_enabled: bool
    conditional_tp_conditions: List[str]
    auto_adjust: bool


# ── 专家模式管理器 ─────────────────────────────────────────────

class ExpertModeManager:
    """专家模式管理器"""

    def __init__(self):
        self.configs = {tool: self._default_config(tool) for tool in EXPERT_CONFIGS}

    def _default_config(self, tool: str) -> Dict:
        default = EXPERT_CONFIGS.get(tool, EXPERT_CONFIGS["rabbit"])
        return {
            "tool": tool,
            "enabled": True,
            "leverage": default["leverage_range"][0],
            "params": {
                k: v["default"] for k, v in default.get("params", {}).items()
            },
            "conditional_tp_enabled": default.get("conditional_tp", {}).get("enabled", False),
            "conditional_tp_conditions": default.get("conditional_tp", {}).get("conditions", []),
            "auto_adjust": False,
        }

    def get_config(self, tool: str) -> Optional[Dict]:
        return self.configs.get(tool)

    def set_config(self, tool: str, config: ExpertConfig) -> Dict:
        if tool not in EXPERT_CONFIGS:
            raise HTTPException(status_code=400, detail="不支持的工具")

        default = EXPERT_CONFIGS[tool]

        # 验证杠杆
        if config.leverage not in EXPERT_LEVERAGE_LEVELS:
            raise HTTPException(status_code=400, detail=f"杠杆必须为 {EXPERT_LEVERAGE_LEVELS}")
        if config.leverage > default["leverage_range"][1]:
            raise HTTPException(status_code=400, detail=f"杠杆最大 {default['leverage_range'][1]}")

        # 验证参数范围
        for param_name, value in config.params.items():
            if param_name in default.get("params", {}):
                param_config = default["params"][param_name]
                if not (param_config["min"] <= value <= param_config["max"]):
                    raise HTTPException(
                        status_code=400,
                        detail=f"{param_name} 范围 [{param_config['min']}, {param_config['max']}]"
                    )

        self.configs[tool] = {
            "tool": tool,
            "enabled": config.enabled,
            "leverage": config.leverage,
            "params": config.params,
            "conditional_tp_enabled": config.conditional_tp_enabled,
            "conditional_tp_conditions": config.conditional_tp_conditions,
            "auto_adjust": config.auto_adjust,
        }
        return self.configs[tool]

    def reset_config(self, tool: str) -> Dict:
        self.configs[tool] = self._default_config(tool)
        return self.configs[tool]

    def get_all_configs(self) -> Dict[str, Dict]:
        return self.configs

    def validate_position(self, tool: str, position: Dict) -> Dict:
        """验证专家模式下的持仓"""
        config = self.configs.get(tool, {})
        if not config.get("enabled"):
            return {"valid": True, "warnings": []}

        warnings = []

        # 杠杆检查
        leverage = position.get("leverage", 1)
        if leverage > config.get("leverage", 1):
            warnings.append(f"杠杆 {leverage} 超过配置 {config['leverage']}")

        # 止盈移除检查
        if config.get("conditional_tp_enabled"):
            conditions = config.get("conditional_tp_conditions", [])
            # 简化检查
            if position.get("pnl_pct", 0) > 15 and len(conditions) > 0:
                warnings.append("止盈可移除条件已满足")

        return {"valid": len(warnings) == 0, "warnings": warnings}


_manager = ExpertModeManager()


# ── API Routes ─────────────────────────────────────────────────

@router.get("/config/{tool}")
async def get_expert_config(tool: str):
    """
    获取专家模式配置
    GET /api/expert/config/{tool}
    """
    config = _manager.get_config(tool)
    if config is None:
        raise HTTPException(status_code=404, detail="工具不存在")
    return config


@router.get("/configs")
async def get_all_configs():
    """
    获取所有工具的专家配置
    GET /api/expert/configs
    """
    return {"tools": _manager.get_all_configs()}


@router.get("/params/{tool}")
async def get_expert_params(tool: str):
    """
    获取工具可调参数范围
    GET /api/expert/params/{tool}
    """
    if tool not in EXPERT_CONFIGS:
        raise HTTPException(status_code=404, detail="工具不存在")
    default = EXPERT_CONFIGS[tool]
    return {
        "tool": tool,
        "leverage_range": default["leverage_range"],
        "params": default.get("params", {}),
        "conditional_tp": default.get("conditional_tp", {}),
        "leverage_levels": EXPERT_LEVERAGE_LEVELS,
    }


@router.post("/config")
async def set_expert_config(body: ExpertConfig):
    """
    设置专家模式配置
    POST /api/expert/config
    """
    try:
        result = _manager.set_config(body.tool, body)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/reset/{tool}")
async def reset_expert_config(tool: str):
    """
    重置专家模式配置
    POST /api/expert/reset/{tool}
    """
    result = _manager.reset_config(tool)
    return result


@router.post("/validate/position")
async def validate_position(tool: str, position: Dict[str, Any]):
    """
    验证持仓是否符合专家模式配置
    POST /api/expert/validate/position
    """
    result = _manager.validate_position(tool, position)
    return result


@router.get("/leverage_levels")
async def get_leverage_levels():
    """获取可用杠杆等级"""
    return {"levels": EXPERT_LEVERAGE_LEVELS}
