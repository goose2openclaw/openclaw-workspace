#!/usr/bin/env python3
"""
🧠 北斗七鑫仓位自动优化器 V2
===========================
基于趋势 + MiroFish预测 + 矿工费 + 归一胜率 + 现金流再投资

核心改进:
1. 禁用工具 = 0权重
2. 打工工具(薅羊毛/穷孩子)产生现金流 → 及时投入高置信度投资
"""

import json
import math
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# ==================== 常量 ====================
MINING_FEE = 0.001  # Binance taker fee 0.1%
MAKER_FEE = 0.0005  # Binance maker fee 0.05%

# 北斗七鑫工具配置
TOOLS_CONFIG = {
    "rabbit": {
        "name": "🐰 打兔子",
        "symbols": ["BTC", "ETH", "SOL", "BNB", "XRP"],
        "base_weight": 0.25,
        "stop_loss": 0.05,
        "take_profit": 0.08,
        "status": "disabled",  # 禁用
        "type": "investment"
    },
    "mole": {
        "name": "🐹 打地鼠",
        "symbols": [],
        "base_weight": 0.30,
        "stop_loss": 0.08,
        "take_profit": 0.15,
        "status": "active",
        "type": "investment"
    },
    "oracle": {
        "name": "🔮 走着瞧",
        "symbols": ["POLYMARKET", "METACULUS"],
        "base_weight": 0.20,
        "stop_loss": 0.05,
        "take_profit": 0.10,
        "status": "active",
        "type": "investment"
    },
    "leader": {
        "name": "👑 跟大哥",
        "symbols": [],
        "base_weight": 0.15,
        "stop_loss": 0.03,
        "take_profit": 0.06,
        "status": "active",
        "type": "investment",
        "expert_mode": True
    },
    "hitchhiker": {
        "name": "🍀 搭便车",
        "symbols": [],
        "base_weight": 0.10,
        "stop_loss": 0.05,
        "take_profit": 0.08,
        "status": "active",
        "type": "investment"
    },
    "wool": {
        "name": "💰 薅羊毛",
        "symbols": [],
        "base_weight": 0.03,
        "stop_loss": 0.02,
        "take_profit": 0.20,
        "status": "active",
        "type": "work",  # 打工工具
        "cashflow_generation": 0.02,  # 2%现金流产生率
        "reinvest_threshold": 0.05  # 置信度>5%时再投资
    },
    "poor": {
        "name": "👶 穷孩子",
        "symbols": [],
        "base_weight": 0.02,
        "stop_loss": 0.01,
        "take_profit": 0.30,
        "status": "active",
        "type": "work",  # 打工工具
        "cashflow_generation": 0.03,  # 3%现金流产生率
        "reinvest_threshold": 0.05
    }
}


class ToolNode:
    """工具节点"""
    def __init__(self, tool_id: str, config: Dict):
        self.tool_id = tool_id
        self.config = config
        self.name = config["name"]
        self.status = config.get("status", "active")
        self.tool_type = config.get("type", "investment")
        
        # 实时数据
        self.trend_signal = 0  # -1, 0, 1
        self.trend_confidence = 0.5
        self.mirofish_signal = 0.5  # 0-1
        self.mirofish_confidence = 0.5
        
        # 历史表现
        self.win_rate = 0.5
        self.total_trades = 0
        
        # 计算属性
        self.fee = MINING_FEE
        self.expected_return = 0.0
        self.normalized_win_rate = 0.5
        self.optimized_weight = 0.0
        
        # 打工工具现金流
        self.cashflow_rate = config.get("cashflow_generation", 0)
        self.cashflow_accumulated = 0.0
        self.reinvest_ready = False
    
    def calculate_normalized_win_rate(self, all_tools: List['ToolNode']) -> float:
        """计算归一化胜率"""
        if self.status == "disabled":
            self.normalized_win_rate = 0.0
            return 0.0
            
        active_tools = [t for t in all_tools if t.status == "active" and t.total_trades > 0]
        if not active_tools:
            return self.win_rate
            
        all_win_rates = [t.win_rate for t in active_tools]
        min_wr = min(all_win_rates)
        max_wr = max(all_win_rates)
        
        if max_wr == min_wr:
            return 0.5
            
        normalized = (self.win_rate - min_wr) / (max_wr - min_wr) * 0.6 + 0.3
        self.normalized_win_rate = max(0.0, min(0.9, normalized))
        return self.normalized_win_rate
    
    def calculate_expected_return(self) -> float:
        """计算期望收益"""
        if self.status == "disabled" or self.total_trades == 0:
            self.expected_return = 0.0
            return 0.0
            
        base_expected = (
            self.win_rate * self.config["take_profit"] -
            (1 - self.win_rate) * self.config["stop_loss"]
        )
        
        total_fee = self.fee * 2
        
        trend_factor = 1.0 + self.trend_signal * self.trend_confidence * 0.2
        mirofish_factor = 1.0 + (self.mirofish_signal - 0.5) * self.mirofish_confidence * 0.3
        
        self.expected_return = (base_expected - total_fee) * trend_factor * mirofish_factor
        return self.expected_return
    
    def calculate_optimized_weight(self, all_tools: List['ToolNode'] = None,
                                   max_total_weight: float = 1.0) -> float:
        """计算最优仓位权重"""
        # 禁用工具 = 0权重
        if self.status == "disabled":
            self.optimized_weight = 0.0
            return 0.0
        
        base_weight = self.config["base_weight"]
        
        # 打工工具特殊处理
        if self.tool_type == "work":
            # 打工工具: 累积现金流，不参与正常权重分配
            self.optimized_weight = base_weight
            return self.optimized_weight
        
        # 趋势调整
        if self.trend_signal == 1:  # BULLISH
            trend_adjustment = 1.0 + self.trend_confidence * 0.5
        elif self.trend_signal == -1:  # BEARISH
            trend_adjustment = 1.0 - self.trend_confidence * 0.7
        else:
            trend_adjustment = 1.0
            
        # MiroFish调整
        mirofish_adjustment = 0.5 + self.mirofish_signal * 0.5
        
        # 归一化胜率调整
        wr_adjustment = self.normalized_win_rate
        
        # 期望收益调整
        if self.expected_return > 0:
            er_adjustment = 1.0 + min(self.expected_return * 5, 0.5)
        else:
            er_adjustment = 1.0 + max(self.expected_return * 5, -0.5)
        
        # 综合权重
        raw_weight = base_weight * trend_adjustment * mirofish_adjustment * wr_adjustment * er_adjustment
        
        # 强看跌时几乎禁用
        if self.trend_signal == -1 and self.trend_confidence > 0.7:
            raw_weight *= 0.1
            
        self.optimized_weight = max(0.0, min(raw_weight, base_weight * 2))
        return self.optimized_weight
    
    def update_cashflow(self) -> float:
        """更新打工工具现金流"""
        if self.tool_type != "work" or self.status == "disabled":
            return 0.0
        
        # 累积现金流
        self.cashflow_accumulated += self.cashflow_rate
        
        # 检查是否达到再投资条件
        self.reinvest_ready = (
            self.cashflow_accumulated >= self.config.get("reinvest_threshold", 0.05)
        )
        
        return self.cashflow_accumulated


class PortfolioOptimizerV2:
    """投资组合优化器 V2"""
    
    def __init__(self):
        self.tools: Dict[str, ToolNode] = {}
        self.total_weight = 0.0
        self.total_expected_return = 0.0
        self.cashflow_pool = 0.0  # 可再投资的现金流
        self.mode = "normal"
        
        for tool_id, config in TOOLS_CONFIG.items():
            self.tools[tool_id] = ToolNode(tool_id, config)
    
    def update_tool_data(self, tool_id: str, trend_signal: int, trend_confidence: float,
                         mirofish_signal: float, mirofish_confidence: float,
                         win_rate: float, total_trades: int):
        """更新工具数据"""
        if tool_id not in self.tools:
            return
        tool = self.tools[tool_id]
        tool.trend_signal = trend_signal
        tool.trend_confidence = trend_confidence
        tool.mirofish_signal = mirofish_signal
        tool.mirofish_confidence = mirofish_confidence
        tool.win_rate = win_rate
        tool.total_trades = total_trades
    
    def collect_cashflow(self) -> float:
        """收集打工工具现金流"""
        cashflow = 0.0
        for tool in self.tools.values():
            if tool.tool_type == "work":
                cf = tool.update_cashflow()
                if tool.reinvest_ready:
                    # 达到阈值，可以再投资
                    cashflow += tool.cashflow_accumulated
                    tool.cashflow_accumulated = 0.0
                    tool.reinvest_ready = False
        self.cashflow_pool = cashflow
        return cashflow
    
    def deploy_cashflow(self, confidence_threshold: float = 0.05) -> Dict[str, float]:
        """部署现金流到高置信度投资"""
        deploys = {}
        
        if self.cashflow_pool <= 0:
            return deploys
        
        # 找出高置信度的投资工具
        investment_tools = [
            (tid, t) for tid, t in self.tools.items() 
            if t.tool_type == "investment" and t.status == "active"
        ]
        
        # 按置信度排序
        investment_tools.sort(
            key=lambda x: x[1].mirofish_confidence * x[1].mirofish_signal,
            reverse=True
        )
        
        # 部署到最高置信度
        for tid, tool in investment_tools[:2]:  # 最多2个
            if tool.mirofish_confidence >= confidence_threshold:
                deploys[tid] = {
                    "tool": tool.name,
                    "amount": self.cashflow_pool,
                    "confidence": tool.mirofish_confidence,
                    "signal": tool.mirofish_signal
                }
                break  # 只部署一个最高置信度的
        
        return deploys
    
    def optimize(self, mode: str = "normal") -> Dict:
        """优化投资组合"""
        self.mode = mode
        
        # 1. 计算所有工具的期望收益
        for tool in self.tools.values():
            tool.calculate_expected_return()
        
        # 2. 归一化胜率
        tools_list = list(self.tools.values())
        for tool in tools_list:
            tool.calculate_normalized_win_rate(tools_list)
        
        # 3. 计算投资工具的优化权重
        investment_tools = [t for t in tools_list if t.tool_type == "investment"]
        total_investment_base = sum(t.config["base_weight"] for t in investment_tools)
        
        for tool in investment_tools:
            tool.calculate_optimized_weight(tools_list)
        
        # 4. 归一化投资权重(禁用工具为0)
        total_raw = sum(t.optimized_weight for t in investment_tools)
        if total_raw > 0:
            for tool in investment_tools:
                tool.optimized_weight = tool.optimized_weight / total_raw
        
        # 5. 打工工具维持基础权重
        work_tools = [t for t in tools_list if t.tool_type == "work"]
        
        # 6. 收集现金流
        cashflow = self.collect_cashflow()
        cashflow_deploys = self.deploy_cashflow()
        
        # 7. 计算总期望收益
        self.total_expected_return = sum(
            t.optimized_weight * t.expected_return 
            for t in tools_list if t.status == "active"
        )
        
        return self.get_result(cashflow, cashflow_deploys)
    
    def get_result(self, cashflow: float, cashflow_deploys: Dict) -> Dict:
        """获取优化结果"""
        investment_weights = {}
        work_weights = {}
        
        for tool_id, tool in self.tools.items():
            data = {
                "name": tool.name,
                "weight": round(tool.optimized_weight * 100, 2),
                "expected_return": round(tool.expected_return * 100, 3),
                "normalized_win_rate": round(tool.normalized_win_rate * 100, 1),
                "trend": ["看跌", "中性", "看涨"][tool.trend_signal + 1],
                "mirofish": ["强卖", "卖", "持有", "买", "强买"][int(tool.mirofish_signal * 4)],
                "status": tool.status,
                "type": tool.tool_type
            }
            
            if tool.tool_type == "work":
                data["cashflow_accumulated"] = round(tool.cashflow_accumulated * 100, 3)
                data["cashflow_rate"] = round(tool.cashflow_rate * 100, 2)
                work_weights[tool_id] = data
            else:
                investment_weights[tool_id] = data
        
        return {
            "mode": self.mode,
            "total_expected_return": round(self.total_expected_return * 100, 3),
            "investment_tools": investment_weights,
            "work_tools": work_weights,
            "cashflow": {
                "pool": round(cashflow * 100, 3),
                "deploys": cashflow_deploys
            },
            "total_weight_check": sum(
                t.optimized_weight for t in self.tools.values()
            ),
            "timestamp": datetime.now().isoformat()
        }


def run_simulation():
    """运行模拟"""
    optimizer = PortfolioOptimizerV2()
    
    # 模拟数据
    optimizer.update_tool_data("rabbit", -1, 0.7, 0.3, 0.5, 0.12, 1728)  # 禁用
    optimizer.update_tool_data("mole", 1, 0.75, 0.8, 0.7, 0.60, 500)
    optimizer.update_tool_data("oracle", 0, 0.5, 0.75, 0.7, 0.65, 200)
    optimizer.update_tool_data("leader", 1, 0.6, 0.65, 0.65, 0.55, 300)
    optimizer.update_tool_data("hitchhiker", 1, 0.65, 0.7, 0.6, 0.52, 150)
    optimizer.update_tool_data("wool", 0, 0.3, 0.5, 0.4, 0.45, 80)  # 打工工具
    optimizer.update_tool_data("poor", 0, 0.4, 0.5, 0.3, 0.40, 50)   # 打工工具
    
    return optimizer.optimize(mode="normal")


def print_result(result: Dict):
    """打印结果"""
    print()
    print("=" * 80)
    print("🧠 北斗七鑫仓位自动优化器 V2")
    print("   (禁用=0权重 + 打工工具现金流再投资)")
    print("=" * 80)
    print()
    
    print(f"📊 总期望收益: {result['total_expected_return']}%")
    print()
    
    print("【投资工具权重】")
    print("-" * 80)
    print(f"{'工具':<15} {'状态':<8} {'权重':<10} {'趋势':<8} {'MiroFish':<10} {'期望':<10}")
    print("-" * 80)
    
    for tid, t in result["investment_tools"].items():
        status_icon = "❌" if t["status"] == "disabled" else "✅"
        print(f"{t['name']:<12} {status_icon}{t['status']:<5} {t['weight']:>7.2f}% {t['trend']:<8} {t['mirofish']:<10} {t['expected_return']:>+8.3f}%")
    
    print()
    print("【打工工具现金流】")
    print("-" * 80)
    print(f"{'工具':<15} {'权重':<10} {'现金流率':<12} {'累积':<10} {'状态'}")
    print("-" * 80)
    
    for tid, t in result["work_tools"].items():
        reinvest_status = "📥 可再投资" if t["cashflow_accumulated"] >= 5 else "⏳ 累积中"
        print(f"{t['name']:<12} {t['weight']:>7.2f}% {t['cashflow_rate']:>9.2f}% {t['cashflow_accumulated']:>8.3f}% {reinvest_status}")
    
    print()
    cf = result["cashflow"]
    print(f"💰 现金流池: {cf['pool']}%")
    if cf['deploys']:
        print("📥 现金流部署:")
        for tid, info in cf['deploys'].items():
            print(f"   → {info['tool']}: {cf['pool']}% @ 置信度={info['confidence']}")
    else:
        print("📥 现金流部署: 待触发(置信度<5%)")
    
    print()
    print(f"✅ 权重总和验证: {result['total_weight_check']*100:.2f}%")
    print("=" * 80)


if __name__ == "__main__":
    result = run_simulation()
    print_result(result)
    
    with open('optimizer_v2_result.json', 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print("\n💾 结果已保存到 optimizer_v2_result.json")
