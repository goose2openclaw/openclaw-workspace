#!/usr/bin/env python3
"""
🧠 北斗七鑫仓位自动优化器
========================
基于趋势 + MiroFish预测 + 矿工费 + 归一胜率 动态调整仓位

功能:
1. 实时趋势检测 (声纳库)
2. MiroFish预测信号
3. 矿工费计算 (Binance: 0.1% taker)
4. 归一胜率权重优化
5. 动态仓位调整
"""

import json
import math
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# ==================== 常量 ====================
MINING_FEE = 0.001  # Binance taker fee 0.1%
MAKER_FEE = 0.0005  # Binance maker fee 0.05%

# 北斗七鑫工具基础配置
TOOLS_BASE = {
    "rabbit": {
        "name": "🐰 打兔子",
        "symbols": ["BTC", "ETH", "SOL", "BNB", "XRP"],
        "base_weight": 0.25,
        "stop_loss": 0.05,
        "take_profit": 0.08,
        "fee_tier": "tier1"
    },
    "mole": {
        "name": "🐹 打地鼠",
        "symbols": [],  # 动态发现
        "base_weight": 0.20,
        "stop_loss": 0.08,
        "take_profit": 0.15,
        "fee_tier": "tier2"
    },
    "oracle": {
        "name": "🔮 走着瞧",
        "symbols": ["POLYMARKET", "METACULUS"],
        "base_weight": 0.15,
        "stop_loss": 0.05,
        "take_profit": 0.10,
        "fee_tier": "tier1"
    },
    "leader": {
        "name": "👑 跟大哥",
        "symbols": [],  # 动态跟随
        "base_weight": 0.15,
        "stop_loss": 0.03,
        "take_profit": 0.06,
        "fee_tier": "tier1",
        "expert_mode": True
    },
    "hitchhiker": {
        "name": "🍀 搭便车",
        "symbols": [],  # 动态跟单
        "base_weight": 0.10,
        "stop_loss": 0.05,
        "take_profit": 0.08,
        "fee_tier": "tier2"
    },
    "wool": {
        "name": "💰 薅羊毛",
        "symbols": [],  # 动态空投
        "base_weight": 0.03,
        "stop_loss": 0.02,
        "take_profit": 0.20,
        "fee_tier": "tier3"
    },
    "poor": {
        "name": "👶 穷孩子",
        "symbols": [],  # 动态众包
        "base_weight": 0.02,
        "stop_loss": 0.01,
        "take_profit": 0.30,
        "fee_tier": "tier3"
    }
}


class TrendSignal:
    """趋势信号"""
    BEARISH = -1
    NEUTRAL = 0
    BULLISH = 1


class MiroFishSignal:
    """MiroFish预测信号"""
    STRONG_SELL = 0.0
    SELL = 0.25
    HOLD = 0.50
    BUY = 0.75
    STRONG_BUY = 1.0


class ToolOptimizer:
    """工具仓位优化器"""
    
    def __init__(self, tool_id: str, config: Dict):
        self.tool_id = tool_id
        self.config = config
        self.name = config["name"]
        
        # 实时数据
        self.trend_signal = TrendSignal.NEUTRAL
        self.trend_confidence = 0.5
        self.mirofish_signal = MiroFishSignal.HOLD
        self.mirofish_confidence = 0.5
        
        # 历史表现
        self.win_rate = 0.5
        self.avg_return = 0.0
        self.total_trades = 0
        
        # 计算属性
        self.fee = MINING_FEE if config["fee_tier"] == "tier1" else MINING_FEE * 1.2
        self.expected_return = 0.0
        self.normalized_win_rate = 0.0
        self.optimized_weight = 0.0
        
    def calculate_normalized_win_rate(self, all_tools: List['ToolOptimizer']) -> float:
        """计算归一化胜率 (相对于其他工具)"""
        if not all_tools or len(all_tools) < 2:
            return self.win_rate
            
        # 获取所有工具的胜率
        all_win_rates = [t.win_rate for t in all_tools if t.total_trades > 0]
        if not all_win_rates:
            return self.win_rate
            
        min_wr = min(all_win_rates)
        max_wr = max(all_win_rates)
        
        if max_wr == min_wr:
            return 0.5
            
        # 归一化到 0.3-0.9 范围
        normalized = (self.win_rate - min_wr) / (max_wr - min_wr) * 0.6 + 0.3
        self.normalized_win_rate = max(0.3, min(0.9, normalized))
        return self.normalized_win_rate
    
    def calculate_expected_return(self) -> float:
        """计算期望收益 (扣除矿工费)"""
        if self.win_rate == 0 or self.total_trades == 0:
            return 0.0
            
        # 基础期望收益 = 胜率 * 止盈 - (1-胜率) * 止损
        base_expected = (
            self.win_rate * self.config["take_profit"] -
            (1 - self.win_rate) * self.config["stop_loss"]
        )
        
        # 扣除双向矿工费 (入场 + 出场)
        total_fee = self.fee * 2
        
        # 趋势调整因子
        trend_factor = 1.0 + self.trend_signal * self.trend_confidence * 0.2
        
        # MiroFish预测调整因子
        mirofish_factor = 1.0 + (self.mirofish_signal - 0.5) * self.mirofish_confidence * 0.3
        
        # 最终期望收益
        self.expected_return = (base_expected - total_fee) * trend_factor * mirofish_factor
        return self.expected_return
    
    def calculate_optimized_weight(self, total_budget: float = 1.0, 
                                    all_tools: List['ToolOptimizer'] = None) -> float:
        """计算最优仓位权重"""
        # 基础权重
        base_weight = self.config["base_weight"]
        
        # 趋势调整
        if self.trend_signal == TrendSignal.BULLISH:
            trend_adjustment = 1.0 + self.trend_confidence * 0.5
        elif self.trend_signal == TrendSignal.BEARISH:
            trend_adjustment = 1.0 - self.trend_confidence * 0.7
        else:
            trend_adjustment = 1.0
            
        # MiroFish调整
        mirofish_adjustment = 0.5 + self.mirofish_signal * 0.5
        
        # 胜率调整 (归一化)
        wr_adjustment = self.calculate_normalized_win_rate(all_tools) if all_tools else self.win_rate
        
        # 期望收益调整
        if self.expected_return > 0:
            er_adjustment = 1.0 + min(self.expected_return * 5, 0.5)
        else:
            er_adjustment = 1.0 + max(self.expected_return * 5, -0.5)
        
        # 综合权重
        raw_weight = base_weight * trend_adjustment * mirofish_adjustment * wr_adjustment * er_adjustment
        
        # 如果趋势强烈看跌，权重趋近0
        if self.trend_signal == TrendSignal.BEARISH and self.trend_confidence > 0.7:
            raw_weight *= 0.1
            
        self.optimized_weight = max(0.0, min(raw_weight, self.config["base_weight"] * 2))
        return self.optimized_weight


class PortfolioOptimizer:
    """投资组合优化器"""
    
    def __init__(self):
        self.tools: Dict[str, ToolOptimizer] = {}
        self.total_weight = 0.0
        self.total_expected_return = 0.0
        self.mode = "normal"  # "normal" or "expert"
        
        # 初始化工具
        for tool_id, config in TOOLS_BASE.items():
            self.tools[tool_id] = ToolOptimizer(tool_id, config)
    
    def update_tool_data(self, tool_id: str, trend_signal: int, trend_confidence: float,
                         mirofish_signal: float, mirofish_confidence: float,
                         win_rate: float, avg_return: float, total_trades: int):
        """更新工具数据"""
        if tool_id not in self.tools:
            return
            
        tool = self.tools[tool_id]
        tool.trend_signal = trend_signal
        tool.trend_confidence = trend_confidence
        tool.mirofish_signal = mirofish_signal
        tool.mirofish_confidence = mirofish_confidence
        tool.win_rate = win_rate
        tool.avg_return = avg_return
        tool.total_trades = total_trades
    
    def optimize(self, mode: str = "normal") -> Dict:
        """优化投资组合"""
        self.mode = mode
        
        # 计算所有工具的期望收益
        for tool in self.tools.values():
            tool.calculate_expected_return()
        
        # 归一化胜率并优化权重
        tools_list = list(self.tools.values())
        for tool in tools_list:
            tool.calculate_normalized_win_rate(tools_list)
            tool.calculate_optimized_weight(all_tools=tools_list)
        
        # 归一化总权重
        total = sum(t.optimized_weight for t in tools_list)
        if total > 0:
            for tool in tools_list:
                tool.optimized_weight = tool.optimized_weight / total
        
        # 计算组合总期望收益
        self.total_expected_return = sum(
            t.optimized_weight * t.expected_return 
            for t in tools_list
        )
        
        # 考虑矿工费的总收益
        avg_fee = sum(t.fee * 2 * t.optimized_weight for t in tools_list)
        net_expected_return = self.total_expected_return - avg_fee
        
        return self.get_result()
    
    def get_result(self) -> Dict:
        """获取优化结果"""
        tool_weights = {}
        for tool_id, tool in self.tools.items():
            tool_weights[tool_id] = {
                "name": tool.name,
                "weight": round(tool.optimized_weight * 100, 2),
                "expected_return": round(tool.expected_return * 100, 3),
                "normalized_win_rate": round(tool.normalized_win_rate * 100, 1),
                "trend_signal": ["看跌", "中性", "看涨"][tool.trend_signal + 1],
                "mirofish_signal": ["强卖", "卖", "持有", "买", "强买"][int(tool.mirofish_signal * 4)],
                "expert_mode": tool.config.get("expert_mode", False)
            }
        
        return {
            "mode": self.mode,
            "total_expected_return": round(self.total_expected_return * 100, 3),
            "net_expected_return_after_fees": round((self.total_expected_return - sum(t.fee * 2 * t.optimized_weight for t in self.tools.values())) * 100, 3),
            "total_weight": round(sum(t.optimized_weight for t in self.tools.values()) * 100, 2),
            "tools": tool_weights,
            "timestamp": datetime.now().isoformat()
        }


def simulate_normal_mode() -> Dict:
    """模拟普通模式"""
    optimizer = PortfolioOptimizer()
    
    # 模拟数据 (基于历史回测)
    # rabbit - 被禁用状态
    optimizer.update_tool_data(
        "rabbit", TrendSignal.BEARISH, 0.6, MiroFishSignal.HOLD, 0.5,
        0.12, -0.014, 1728
    )
    
    # mole - 活跃趋势
    optimizer.update_tool_data(
        "mole", TrendSignal.BULLISH, 0.7, MiroFishSignal.BUY, 0.65,
        0.55, 0.023, 500
    )
    
    # oracle - 预测市场
    optimizer.update_tool_data(
        "oracle", TrendSignal.NEUTRAL, 0.4, MiroFishSignal.BUY, 0.7,
        0.60, 0.035, 200
    )
    
    # leader - 跟大哥 (无专家模式)
    optimizer.update_tool_data(
        "leader", TrendSignal.NEUTRAL, 0.5, MiroFishSignal.HOLD, 0.5,
        0.50, 0.020, 300
    )
    
    # hitchhiker - 跟单
    optimizer.update_tool_data(
        "hitchhiker", TrendSignal.BULLISH, 0.6, MiroFishSignal.BUY, 0.6,
        0.52, 0.018, 150
    )
    
    # wool - 空投
    optimizer.update_tool_data(
        "wool", TrendSignal.NEUTRAL, 0.3, MiroFishSignal.HOLD, 0.4,
        0.45, 0.015, 80
    )
    
    # poor - 众包
    optimizer.update_tool_data(
        "poor", TrendSignal.NEUTRAL, 0.4, MiroFishSignal.HOLD, 0.3,
        0.40, 0.012, 50
    )
    
    return optimizer.optimize(mode="normal")


def simulate_expert_mode() -> Dict:
    """模拟专家模式"""
    optimizer = PortfolioOptimizer()
    
    # rabbit - 仍然禁用
    optimizer.update_tool_data(
        "rabbit", TrendSignal.BEARISH, 0.8, MiroFishSignal.SELL, 0.6,
        0.12, -0.014, 1728
    )
    
    # mole - 强势趋势，增强
    optimizer.update_tool_data(
        "mole", TrendSignal.BULLISH, 0.85, MiroFishSignal.STRONG_BUY, 0.8,
        0.65, 0.045, 500
    )
    
    # oracle - 预测市场增强
    optimizer.update_tool_data(
        "oracle", TrendSignal.BULLISH, 0.6, MiroFishSignal.STRONG_BUY, 0.85,
        0.70, 0.055, 200
    )
    
    # leader - 专家模式 (双向交易)
    optimizer.update_tool_data(
        "leader", TrendSignal.BULLISH, 0.7, MiroFishSignal.BUY, 0.75,
        0.65, 0.150, 300  # 高期望收益来自杠杆+条件止盈移除
    )
    
    # hitchhiker - 跟单
    optimizer.update_tool_data(
        "hitchhiker", TrendSignal.BULLISH, 0.7, MiroFishSignal.BUY, 0.7,
        0.58, 0.025, 150
    )
    
    # wool - 空投
    optimizer.update_tool_data(
        "wool", TrendSignal.NEUTRAL, 0.3, MiroFishSignal.HOLD, 0.4,
        0.45, 0.015, 80
    )
    
    # poor - 众包
    optimizer.update_tool_data(
        "poor", TrendSignal.NEUTRAL, 0.4, MiroFishSignal.HOLD, 0.3,
        0.40, 0.012, 50
    )
    
    return optimizer.optimize(mode="expert")


def print_comparison(normal_result: Dict, expert_result: Dict):
    """打印对比报告"""
    print()
    print("=" * 80)
    print("🧠 北斗七鑫仓位自动优化器 - 普通模式 vs 专家模式")
    print("=" * 80)
    print()
    
    # 汇总对比
    print("📊 【汇总对比】")
    print("-" * 80)
    对比表 = [
        ["指标", "普通模式", "专家模式", "差异"],
        ["模式", "仅做多", "做多+做空", "双向获利"],
        ["总期望收益", f"{normal_result['total_expected_return']}%", 
         f"{expert_result['total_expected_return']}%", 
         f"{expert_result['total_expected_return'] - normal_result['total_expected_return']:+.3f}%"],
        ["扣除矿工费后", f"{normal_result['net_expected_return_after_fees']}%",
         f"{expert_result['net_expected_return_after_fees']}%",
         f"{expert_result['net_expected_return_after_fees'] - normal_result['net_expected_return_after_fees']:+.3f}%"],
        ["总仓位", f"{normal_result['total_weight']}%",
         f"{expert_result['total_weight']}%", "-"],
    ]
    
    for row in 对比表:
        print(f"  {row[0]:<20} {row[1]:<20} {row[2]:<20} {row[3]}")
    
    print()
    print("📋 【工具权重分配】")
    print("-" * 80)
    print(f"{'工具':<15} {'普通模式':<15} {'专家模式':<15} {'差异':<10} {'备注'}")
    print("-" * 80)
    
    normal_tools = normal_result['tools']
    expert_tools = expert_result['tools']
    
    for tool_id in ["mole", "oracle", "leader", "hitchhiker", "wool", "poor", "rabbit"]:
        if tool_id not in normal_tools:
            continue
        nt = normal_tools[tool_id]
        et = expert_tools.get(tool_id, nt)
        
        diff = float(et['weight']) - float(nt['weight'])
        note = ""
        if tool_id == "rabbit":
            note = "(禁用)"
        elif tool_id == "leader":
            note = "杠杆+双向"
        elif float(nt['weight']) < 1 and float(et['weight']) > float(nt['weight']):
            note = "↑增配"
        elif float(nt['weight']) > 1 and float(et['weight']) < float(nt['weight']):
            note = "↓减配"
            
        print(f"  {nt['name']:<12} {nt['weight']:>8}% {et['weight']:>8}% {diff:>+7.2f}%  {note}")
    
    print()
    print("🎯 【趋势与信号】")
    print("-" * 80)
    print(f"{'工具':<15} {'趋势':<8} {'MiroFish':<10} {'普通胜率':<10} {'归一胜率':<10}")
    print("-" * 80)
    
    for tool_id in ["mole", "oracle", "leader", "hitchhiker"]:
        nt = normal_tools[tool_id]
        print(f"  {nt['name']:<12} {nt['trend_signal']:<8} {nt['mirofish_signal']:<10} "
              f"{nt['normalized_win_rate']:>8}% {nt['normalized_win_rate']:>8}%")
    
    print()
    print("💰 【矿工费影响】")
    print("-" * 80)
    print(f"  Binance Taker Fee: {MINING_FEE*100:.2f}% (单笔,双向{ MINING_FEE*2*100:.2f}%)")
    print(f"  归一胜率计算: (win_rate - min) / (max - min) * 0.6 + 0.3")
    print(f"  趋势调整: 趋势信号 * 置信度 * 20%")
    print(f"  MiroFish调整: (信号 - 0.5) * 置信度 * 30%")
    print()
    print("=" * 80)


if __name__ == "__main__":
    print("🧠 北斗七鑫仓位自动优化器")
    print(f"执行时间: {datetime.now().isoformat()}")
    
    # 执行模拟
    normal_result = simulate_normal_mode()
    expert_result = simulate_expert_mode()
    
    # 打印对比
    print_comparison(normal_result, expert_result)
    
    # 保存结果
    with open('optimizer_result.json', 'w') as f:
        json.dump({
            "normal_mode": normal_result,
            "expert_mode": expert_result,
            "timestamp": datetime.now().isoformat()
        }, f, indent=2, ensure_ascii=False)
    
    print()
    print("💾 结果已保存到 optimizer_result.json")
