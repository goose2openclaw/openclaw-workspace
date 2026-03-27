#!/usr/bin/env python3
"""
🪿 GO2SE 备选交易策略系统
支持多策略并行回测和对比
"""

import json
import random
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class StrategyConfig:
    """策略配置"""
    id: str
    name: str
    type: str  # quant/ML/arb/indicator
    enabled: bool = False
    allocation: float = 0.0  # 算力分配 0-1
    priority: int = 5  # 1-10 优先级
    capital_ratio: float = 0.0  # 资金比例 0-1
    description: str = ""
    source: str = ""  # 来源: lean/zipline/pybroker/custom


class AlternativeStrategies:
    """备选策略管理器"""
    
    # 内置策略模板
    BUILTIN_STRATEGIES = {
        "lean_rsi": {
            "id": "lean_rsi",
            "name": "Lean RSI均值回归",
            "type": "quant",
            "description": "基于QuantConnect Lean的RSI策略",
            "source": "lean",
            "default_params": {
                "rsi_period": 14,
                "oversold": 30,
                "overbought": 70,
                "position_size": 0.3
            }
        },
        "lean_macd": {
            "id": "lean_macd", 
            "name": "Lean MACD趋势",
            "type": "quant",
            "description": "基于Lean的MACD金叉死叉策略",
            "source": "lean",
            "default_params": {
                "fast": 12,
                "slow": 26,
                "signal": 9,
                "position_size": 0.5
            }
        },
        "zipline_momentum": {
            "id": "zipline_momentum",
            "name": "Zipline动量策略",
            "type": "quant",
            "description": "基于Zipline的动量跟踪策略",
            "source": "zipline",
            "default_params": {
                "lookback": 20,
                "top_n": 10,
                "position_size": 0.1
            }
        },
        "pybroker_ml": {
            "id": "pybroker_ml",
            "name": "PyBroker机器学习",
            "type": "ML",
            "description": "基于PyBroker的ML信号策略",
            "source": "pybroker",
            "default_params": {
                "model_type": "random_forest",
                "features": ["rsi", "macd", "volume"],
                "position_size": 0.25
            }
        },
        "stat_arb": {
            "id": "stat_arb",
            "name": "统计套利",
            "type": "arb",
            "description": "配对交易统计套利策略",
            "source": "custom",
            "default_params": {
                "pairs": ["BTC/ETH", "ETH/BNB"],
                "z_entry": 2.0,
                "z_exit": 0.5,
                "lookback": 50
            }
        },
        "ml_signals": {
            "id": "ml_signals",
            "name": "ML信号增强",
            "type": "ML",
            "description": "多模型集成的机器学习信号",
            "source": "custom",
            "default_params": {
                "models": ["xgboost", "lstm", "transformer"],
                "confidence_threshold": 0.7
            }
        }
    }
    
    def __init__(self):
        self.strategies: Dict[str, StrategyConfig] = {}
        self.expert_mode = False
        
        # 加载内置策略
        for sid, sdata in self.BUILTIN_STRATEGIES.items():
            self.strategies[sid] = StrategyConfig(
                id=sdata["id"],
                name=sdata["name"],
                type=sdata["type"],
                description=sdata.get("description", ""),
                source=sdata.get("source", "custom")
            )
    
    def enable_strategy(self, strategy_id: str, allocation: float = 0.1, 
                       priority: int = 5, capital_ratio: float = 0.1):
        """启用策略并设置参数"""
        if strategy_id not in self.strategies:
            return False, f"策略 {strategy_id} 不存在"
        
        self.strategies[strategy_id].enabled = True
        self.strategies[strategy_id].allocation = allocation
        self.strategies[strategy_id].priority = priority
        self.strategies[strategy_id].capital_ratio = capital_ratio
        
        return True, f"已启用 {self.strategies[strategy_id].name}"
    
    def disable_strategy(self, strategy_id: str):
        """禁用策略"""
        if strategy_id in self.strategies:
            self.strategies[strategy_id].enabled = False
            return True
        return False
    
    def get_enabled_strategies(self) -> List[StrategyConfig]:
        """获取已启用的策略"""
        return [s for s in self.strategies.values() if s.enabled]
    
    def get_total_allocation(self) -> float:
        """获取总算力分配"""
        return sum(s.allocation for s in self.strategies.values() if s.enabled)
    
    def set_expert_mode(self, enabled: bool):
        """设置专家模式"""
        self.expert_mode = enabled
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "expert_mode": self.expert_mode,
            "strategies": {k: asdict(v) for k, v in self.strategies.items()},
            "enabled_count": len(self.get_enabled_strategies()),
            "total_allocation": self.get_total_allocation()
        }
    
    def save(self, path: str):
        """保存配置"""
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
    
    def load(self, path: str):
        """加载配置"""
        with open(path, "r") as f:
            data = json.load(f)
        
        self.expert_mode = data.get("expert_mode", False)
        for sid, sdata in data.get("strategies", {}).items():
            if sid in self.strategies:
                for key, val in sdata.items():
                    setattr(self.strategies[sid], key, val)


# 全局实例
strategy_manager = AlternativeStrategies()


def get_strategy_manager() -> AlternativeStrategies:
    """获取策略管理器"""
    return strategy_manager


def init_strategies():
    """初始化策略系统"""
    config_path = "/root/.openclaw/workspace/GO2SE_PLATFORM/versions/v6/alternative_strategies.json"
    
    try:
        strategy_manager.load(config_path)
    except:
        strategy_manager.save(config_path)
    
    return strategy_manager


if __name__ == "__main__":
    # 测试
    mgr = init_strategies()
    print("🪿 备选策略系统")
    print("=" * 50)
    print(f"专家模式: {mgr.expert_mode}")
    print(f"策略数量: {len(mgr.strategies)}")
    
    # 启用Lean RSI
    mgr.enable_strategy("lean_rsi", allocation=0.15, priority=8, capital_ratio=0.1)
    mgr.enable_strategy("pybroker_ml", allocation=0.1, priority=6, capital_ratio=0.05)
    
    print(f"\n已启用策略:")
    for s in mgr.get_enabled_strategies():
        print(f"  - {s.name}: 算力{s.allocation}, 优先级{s.priority}, 资金{s.capital_ratio}")
    
    print(f"\n总算力分配: {mgr.get_total_allocation()}")
    
    # 保存
    mgr.save("/root/.openclaw/workspace/GO2SE_PLATFORM/versions/v6/alternative_strategies.json")
    print("\n✅ 配置已保存")
