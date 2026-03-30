#!/usr/bin/env python3
"""
🪿 GO2SE 动态仓位管理器 V1
==========================
根据工具表现动态调整仓位分配

功能:
1. 监控各工具表现
2. 自动减仓/加仓/切换
3. 趋势不好时转移到其他工具
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger("dynamic_allocator")

@dataclass
class ToolPerformance:
    tool_id: str
    name: str
    emoji: str
    current_weight: float  # 当前权重
    target_weight: float  # 目标权重
    recent_return: float  # 最近收益
    win_rate: float       # 胜率
    trend_score: float   # 趋势评分
    signal_strength: float  # 信号强度
    last_update: str

@dataclass
class RebalanceAction:
    tool_id: str
    action: str  # increase, decrease, maintain, close
    from_weight: float
    to_weight: float
    reason: str
    priority: int  # 1-5, 5最高

class DynamicPositionManager:
    """
    动态仓位管理器
    
    根据工具表现自动调整仓位:
    - 趋势好 -> 加仓
    - 趋势不好 -> 减仓/平仓
    - 资金转移到表现更好的工具
    """
    
    def __init__(self):
        # 基础配置 (默认权重)
        # B1打兔子(rabbit)已禁用 - 评分40.8，负收益
        self.base_weights = {
            "rabbit": {"weight": 0.00, "min": 0.00, "max": 0.00, "trend_lookback": 24, "enabled": False},
            "mole": {"weight": 0.30, "min": 0.05, "max": 0.40, "trend_lookback": 12, "enabled": True},
            "oracle": {"weight": 0.20, "min": 0.05, "max": 0.30, "trend_lookback": 48, "enabled": True},
            "leader": {"weight": 0.20, "min": 0.05, "max": 0.25, "trend_lookback": 24, "enabled": True},
            "hitchhiker": {"weight": 0.15, "min": 0.02, "max": 0.25, "trend_lookback": 48, "enabled": True},
            "wool": {"weight": 0.08, "min": 0.0, "max": 0.15, "trend_lookback": 72, "enabled": True},
            "poor": {"weight": 0.07, "min": 0.0, "max": 0.12, "trend_lookback": 72, "enabled": True},
        }
        
        # 趋势阈值
        self.trend_thresholds = {
            "bullish": 0.65,    # 趋势评分 > 0.65 -> 加仓
            "neutral": 0.45,    # 0.45 < 趋势 <= 0.65 -> 持有
            "bearish": 0.0,     # 趋势 <= 0.45 -> 减仓/平仓
        }
        
        # 最大调整幅度 (单次)
        self.max_adjustment = 0.05  # 5%
        
        # 当前实际权重 (只包含启用工具)
        self.current_weights = {k: v["weight"] for k, v in self.base_weights.items() if v.get("enabled", True)}
        
        # 工具名称映射
        self.tool_names = {
            "rabbit": "打兔子",
            "mole": "打地鼠",
            "oracle": "走着瞧",
            "leader": "跟大哥",
            "hitchhiker": "搭便车",
            "wool": "薅羊毛",
            "poor": "穷孩子",
        }
        
        self.tool_emojis = {
            "rabbit": "🐰",
            "mole": "🐹",
            "oracle": "🔮",
            "leader": "👑",
            "hitchhiker": "🍀",
            "wool": "💰",
            "poor": "👶",
        }
        
    def evaluate_tool_performance(self, tool_id: str, historical_data: Dict) -> ToolPerformance:
        """
        评估单个工具表现
        
        historical_data: {
            "recent_returns": [...],
            "win_rate": float,
            "trend_scores": [...],
            "signal_strength": float,
        }
        """
        base = self.base_weights.get(tool_id, {})
        
        # 计算最近收益
        returns = historical_data.get("recent_returns", [])
        recent_return = sum(returns[-base.get("trend_lookback", 24):]) / max(1, len(returns[-base.get("trend_lookback", 24):]))
        
        # 计算趋势评分 (0-1)
        trend_scores = historical_data.get("trend_scores", [])
        trend_score = sum(trend_scores[-base.get("trend_lookback", 24):]) / max(1, len(trend_scores)) if trend_scores else 0.5
        
        # 胜率
        win_rate = historical_data.get("win_rate", 0.5)
        
        # 信号强度
        signal_strength = historical_data.get("signal_strength", 0.5)
        
        return ToolPerformance(
            tool_id=tool_id,
            name=self.tool_names.get(tool_id, tool_id),
            emoji=self.tool_emojis.get(tool_id, "❓"),
            current_weight=self.current_weights.get(tool_id, 0.1),
            target_weight=self.current_weights.get(tool_id, 0.1),
            recent_return=recent_return,
            win_rate=win_rate,
            trend_score=trend_score,
            signal_strength=signal_strength,
            last_update=datetime.now().isoformat(),
        )
    
    def calculate_target_weights(self, performances: List[ToolPerformance]) -> Dict[str, float]:
        """
        根据表现计算机器目标权重
        
        原则:
        - 趋势好 -> 提高权重
        - 趋势不好 -> 降低权重
        - 总权重 = 100%
        """
        tool_scores = {}
        
        for perf in performances:
            base = self.base_weights.get(perf.tool_id, {})
            min_w = base.get("min", 0.0)
            max_w = base.get("max", 1.0)
            
            # 计算综合评分
            # 权重: 趋势40% + 胜率30% + 收益20% + 信号10%
            composite = (
                perf.trend_score * 0.40 +
                perf.win_rate * 0.30 +
                (perf.recent_return + 1) / 2 * 0.20 +  # 归一化收益
                perf.signal_strength * 0.10
            )
            
            # 根据趋势调整
            if perf.trend_score >= self.trend_thresholds["bullish"]:
                # 牛市 -> 权重上调
                adjustment = 1.2
            elif perf.trend_score >= self.trend_thresholds["neutral"]:
                # 中性 -> 保持
                adjustment = 1.0
            else:
                # 熊市 -> 权重下调
                adjustment = 0.6
            
            target = self.current_weights.get(perf.tool_id, 0.1) * adjustment
            target = max(min_w, min(max_w, target))  # 限制在min-max之间
            
            tool_scores[perf.tool_id] = {
                "target": target,
                "composite": composite,
                "trend": "bullish" if perf.trend_score >= self.trend_thresholds["bullish"] else 
                         "neutral" if perf.trend_score >= self.trend_thresholds["bearish"] else "bearish"
            }
        
        # 归一化到100%
        total = sum(s["target"] for s in tool_scores.values())
        if total > 0:
            for tool_id in tool_scores:
                tool_scores[tool_id]["target"] /= total
        
        return tool_scores
    
    def generate_rebalance_actions(self, tool_scores: Dict) -> List[RebalanceAction]:
        """
        生成调仓动作
        """
        actions = []
        
        for tool_id, scores in tool_scores.items():
            current = self.current_weights.get(tool_id, 0.1)
            target = scores["target"]
            diff = target - current
            
            if abs(diff) < 0.01:  # 变化太小，跳过
                continue
            
            # 确定动作类型
            if diff > 0:
                action = "increase" if diff > 0 else "decrease"
            else:
                action = "decrease"
            
            # 限制单次调整幅度
            actual_diff = max(-self.max_adjustment, min(self.max_adjustment, diff))
            actual_target = current + actual_diff
            
            # 优先级 (变化越大优先级越高)
            priority = min(5, int(abs(actual_diff) / 0.02) + 1)
            
            # 原因
            trend = scores["trend"]
            if trend == "bullish":
                reason = f"趋势向好 ({scores['composite']:.2f})"
            elif trend == "bearish":
                reason = f"趋势走弱 ({scores['composite']:.2f})"
            else:
                reason = f"趋势中性 ({scores['composite']:.2f})"
            
            actions.append(RebalanceAction(
                tool_id=tool_id,
                action=action,
                from_weight=current,
                to_weight=actual_target,
                reason=reason,
                priority=priority
            ))
        
        # 按优先级排序
        actions.sort(key=lambda x: x.priority, reverse=True)
        
        return actions
    
    def execute_rebalance(self, actions: List[RebalanceAction]) -> Dict:
        """
        执行调仓
        """
        total_change = 0
        
        for action in actions:
            old_weight = self.current_weights.get(action.tool_id, 0)
            self.current_weights[action.tool_id] = action.to_weight
            total_change += abs(action.to_weight - old_weight)
            
            logger.info(
                f"{self.tool_emojis.get(action.tool_id, '')} {action.tool_id}: "
                f"{action.from_weight:.1%} -> {action.to_weight:.1%} "
                f"[{action.action}] {action.reason}"
            )
        
        return {
            "executed": len(actions),
            "total_change": total_change,
            "new_weights": self.current_weights.copy(),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_rebalance_plan(self, performances: List[ToolPerformance]) -> Dict:
        """
        获取完整的调仓计划
        """
        # 过滤掉禁用的工具 (B1打兔子已禁用)
        enabled_performances = [
            p for p in performances
            if self.base_weights.get(p.tool_id, {}).get("enabled", True)
        ]
        
        # 计算目标权重
        tool_scores = self.calculate_target_weights(enabled_performances)
        
        # 生成调仓动作
        actions = self.generate_rebalance_actions(tool_scores)
        
        # 当前权重摘要
        current_summary = [
            {
                "tool_id": tool_id,
                "name": self.tool_names.get(tool_id, tool_id),
                "emoji": self.tool_emojis.get(tool_id, "❓"),
                "current_weight": weight,
                "min_weight": self.base_weights.get(tool_id, {}).get("min", 0),
                "max_weight": self.base_weights.get(tool_id, {}).get("max", 0),
            }
            for tool_id, weight in self.current_weights.items()
        ]
        
        # 目标权重摘要
        target_summary = [
            {
                "tool_id": tool_id,
                "target_weight": scores["target"],
                "composite": scores["composite"],
                "trend": scores["trend"],
            }
            for tool_id, scores in tool_scores.items()
        ]
        
        return {
            "current_weights": current_summary,
            "target_weights": target_summary,
            "proposed_actions": [asdict(a) for a in actions],
            "can_execute": len(actions) > 0 and any(a.priority >= 3 for a in actions),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_dashboard_data(self) -> Dict:
        """获取仪表盘数据"""
        return {
            "weights": [
                {
                    "tool_id": tool_id,
                    "name": self.tool_names.get(tool_id, tool_id),
                    "emoji": self.tool_emojis.get(tool_id, "❓"),
                    "current": weight,
                    "base": self.base_weights.get(tool_id, {}).get("weight", 0),
                    "min": self.base_weights.get(tool_id, {}).get("min", 0),
                    "max": self.base_weights.get(tool_id, {}).get("max", 0),
                }
                for tool_id, weight in self.current_weights.items()
            ],
            "total": sum(self.current_weights.values()),
            "rebalance_script": self.max_adjustment,
            "timestamp": datetime.now().isoformat()
        }


# 全局实例
position_manager = DynamicPositionManager()
