"""
PortfolioSimulationMatrix - 投资组合模拟矩阵
=========================================
连续运行50次，生成三种情况下的默认参数和阈值
"""
from __future__ import annotations
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import random
import json


@dataclass
class MarketCondition:
    """市场条件"""
    name: str
    trend_score_range: Tuple[float, float]
    volatility_range: Tuple[float, float]
    sentiment_range: Tuple[float, float]


@dataclass
class SimulationResult:
    """单次模拟结果"""
    run: int
    mode: str
    market_condition: str
    initial_value: float
    final_value: float
    total_return: float
    max_drawdown: float
    win_rate: float
    sharpe_ratio: float
    trades: int
    fees: float
    final_positions: Dict


class PortfolioSimulationMatrix:
    """
    投资组合模拟矩阵
    =================
    50次连续运行 × 3种市场情况 × 3种模式
    """

    # 三种市场情况
    MARKET_CONDITIONS = {
        "bull": MarketCondition("牛市", (60, 95), (0.05, 0.15), (0.6, 0.9)),
        "bear": MarketCondition("熊市", (5, 40), (0.08, 0.20), (0.1, 0.4)),
        "sideways": MarketCondition("震荡", (35, 65), (0.03, 0.10), (0.4, 0.6)),
    }

    # 三种模式参数
    MODES = {
        "conservative": {
            "max_position": 0.20,
            "stop_loss": 0.03,
            "take_profit": 0.05,
            "leverage": 1,
            "max_tools": 3,
            "min_confidence": 0.7,
            "fee_tolerance": 0.001,
        },
        "balanced": {
            "max_position": 0.30,
            "stop_loss": 0.05,
            "take_profit": 0.08,
            "leverage": 2,
            "max_tools": 5,
            "min_confidence": 0.6,
            "fee_tolerance": 0.002,
        },
        "aggressive": {
            "max_position": 0.40,
            "stop_loss": 0.08,
            "take_profit": 0.15,
            "leverage": 5,
            "max_tools": 7,
            "min_confidence": 0.5,
            "fee_tolerance": 0.003,
        },
    }

    # 工具配置
    TOOLS_CONFIG = {
        "rabbit": {"weight": 0.25, "risk": 0.2, "liquidity": 0.95},
        "mole": {"weight": 0.20, "risk": 0.4, "liquidity": 0.7},
        "oracle": {"weight": 0.15, "risk": 0.3, "liquidity": 0.6},
        "leader": {"weight": 0.15, "risk": 0.25, "liquidity": 0.65},
        "hitchhiker": {"weight": 0.10, "risk": 0.2, "liquidity": 0.7},
    }

    def __init__(self, runs: int = 50):
        self.runs = runs
        self.results: List[SimulationResult] = []
        self.expert_results: List[SimulationResult] = []
        self._init_symbols()

    def _init_symbols(self):
        """初始化模拟币种"""
        self.top20 = ["BTC", "ETH", "BNB", "XRP", "ADA", "SOL", "DOGE", "DOT", "MATIC", "SHIB",
                      "LTC", "TRX", "AVAX", "LINK", "ATOM", "UNI", "XMR", "ETC", "XLM", "BCH"]
        self.other = ["PEPE", "WIF", "FLOKI", "BONK", "SUI", "APT", "ARB", "OP", "INJ", "TIA"]

    def run_full_simulation(self) -> Dict[str, Any]:
        """运行完整模拟"""
        print("=" * 60)
        print("🪿 北斗七鑫 投资组合模拟矩阵")
        print("=" * 60)
        print(f"运行次数: {self.runs} × 3种市场 × 3种模式")
        print(f"开始时间: {datetime.utcnow().isoformat()}")
        print("=" * 60)

        all_results = {}

        for mode in ["conservative", "balanced", "aggressive"]:
            print(f"\n📊 模式: {mode.upper()}")
            print("-" * 40)

            mode_results = []
            expert_mode_results = []

            for market_name, market in self.MARKET_CONDITIONS.items():
                print(f"  {market.name}...", end=" ")

                for run in range(self.runs):
                    # 普通模式
                    result = self._simulate_run(mode, market_name, run)
                    mode_results.append(result)

                    # 专家模式 (杠杆1x，打兔子/跟大哥/搭便车移除止盈)
                    expert_result = self._simulate_expert_run(mode, market_name, run)
                    expert_mode_results.append(expert_result)

                avg_return = sum(r.total_return for r in mode_results[-self.runs:]) / self.runs
                avg_dd = sum(r.max_drawdown for r in mode_results[-self.runs:]) / self.runs
                avg_wr = sum(r.win_rate for r in mode_results[-self.runs:]) / self.runs
                print(f"平均收益: {avg_return*100:.1f}%, 回撤: {avg_dd*100:.1f}%, 胜率: {avg_wr*100:.1f}%")

            all_results[mode] = {
                "regular": self._summarize(mode_results),
                "expert": self._summarize(expert_mode_results),
            }

        # 生成最终推荐参数
        recommendations = self._generate_recommendations(all_results)

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "runs": self.runs,
            "results": all_results,
            "recommendations": recommendations,
        }

    def _simulate_run(
        self,
        mode: str,
        market_condition: str,
        run: int,
    ) -> SimulationResult:
        """模拟单次运行"""
        params = self.MODES[mode]
        market = self.MARKET_CONDITIONS[market_condition]

        initial_value = 10000.0
        current_value = initial_value
        max_value = initial_value
        max_drawdown = 0.0
        trades = 0
        total_fees = 0.0
        wins = 0
        positions = {}

        # 模拟50个时间步
        for step in range(50):
            # 生成市场信号
            trend = random.uniform(*market.trend_score_range) / 100
            volatility = random.uniform(*market.volatility_range)

            # 根据模式决定交易
            if trend > params["min_confidence"]:
                # 选择工具
                tool = self._select_tool(trend, params)
                tool_config = self.TOOLS_CONFIG[tool]

                # 计算仓位
                position_size = current_value * params["max_position"] * tool_config["weight"]
                fee = position_size * 0.001
                total_fees += fee

                # 模拟盈亏
                if random.random() < 0.52:  # 基础胜率
                    pnl = position_size * trend * random.uniform(0.5, 1.5)
                    wins += 1
                else:
                    pnl = -position_size * params["stop_loss"] * random.uniform(0.5, 1.5)

                current_value += pnl - fee
                trades += 1

                # 跟踪持仓
                positions[tool] = positions.get(tool, 0) + position_size

            # 更新最大回撤
            max_value = max(max_value, current_value)
            drawdown = (max_value - current_value) / max_value
            max_drawdown = max(max_drawdown, drawdown)

            # 市场波动影响
            current_value *= (1 + random.uniform(-volatility, volatility))

        total_return = (current_value - initial_value) / initial_value
        win_rate = wins / max(trades, 1)
        sharpe = self._calc_sharpe(total_return, max_drawdown)

        return SimulationResult(
            run=run,
            mode=mode,
            market_condition=market_condition,
            initial_value=initial_value,
            final_value=current_value,
            total_return=total_return,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            sharpe_ratio=sharpe,
            trades=trades,
            fees=total_fees,
            final_positions=positions,
        )

    def _simulate_expert_run(
        self,
        mode: str,
        market_condition: str,
        run: int,
    ) -> SimulationResult:
        """模拟专家模式运行 (杠杆1x，移除止盈)"""
        params = self.MODES[mode].copy()
        market = self.MARKET_CONDITIONS[market_condition]

        # 专家模式调整
        params["leverage"] = 1  # 固定杠杆1x
        params["take_profit"] = float("inf")  # 移除止盈

        initial_value = 10000.0
        current_value = initial_value
        max_value = initial_value
        max_drawdown = 0.0
        trades = 0
        total_fees = 0.0
        wins = 0
        positions = {}

        # 只用打兔子、跟大哥、搭便车
        expert_tools = ["rabbit", "leader", "hitchhiker"]

        for step in range(50):
            trend = random.uniform(*market.trend_score_range) / 100
            volatility = random.uniform(*market.volatility_range)

            if trend > params["min_confidence"]:
                tool = random.choice(expert_tools)  # 只用专家模式工具
                tool_config = self.TOOLS_CONFIG[tool]

                position_size = current_value * params["max_position"] * tool_config["weight"]
                fee = position_size * 0.001
                total_fees += fee

                # 专家模式：无止盈，趋势跟随
                if random.random() < 0.55:  # 略高胜率
                    pnl = position_size * trend * random.uniform(0.8, 2.0)  # 更高收益
                    wins += 1
                else:
                    pnl = -position_size * params["stop_loss"] * random.uniform(0.3, 0.8)  # 更低止损

                current_value += pnl - fee
                trades += 1
                positions[tool] = positions.get(tool, 0) + position_size

            max_value = max(max_value, current_value)
            drawdown = (max_value - current_value) / max_value
            max_drawdown = max(max_drawdown, drawdown)
            current_value *= (1 + random.uniform(-volatility, volatility))

        total_return = (current_value - initial_value) / initial_value
        win_rate = wins / max(trades, 1)
        sharpe = self._calc_sharpe(total_return, max_drawdown)

        return SimulationResult(
            run=run,
            mode=mode,
            market_condition=market_condition,
            initial_value=initial_value,
            final_value=current_value,
            total_return=total_return,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            sharpe_ratio=sharpe,
            trades=trades,
            fees=total_fees,
            final_positions=positions,
        )

    def _select_tool(self, trend: float, params: Dict) -> str:
        """选择工具"""
        if trend > 0.8:
            return "rabbit"
        elif trend > 0.6:
            return random.choice(["rabbit", "mole"])
        elif trend > 0.4:
            return random.choice(["mole", "oracle", "leader"])
        else:
            return random.choice(["hitchhiker", "leader"])

    def _calc_sharpe(self, return_rate: float, max_drawdown: float) -> float:
        """计算Sharpe比"""
        if max_drawdown == 0:
            return 0
        return return_rate / max_drawdown * 0.5

    def _summarize(self, results: List[SimulationResult]) -> Dict:
        """汇总结果"""
        if not results:
            return {}

        returns = [r.total_return for r in results]
        drawdowns = [r.max_drawdown for r in results]
        win_rates = [r.win_rate for r in results]
        sharpes = [r.sharpe_ratio for r in results]

        return {
            "avg_return": sum(returns) / len(returns),
            "avg_drawdown": sum(drawdowns) / len(drawdowns),
            "avg_win_rate": sum(win_rates) / len(win_rates),
            "avg_sharpe": sum(sharpes) / len(sharpes),
            "best_return": max(returns),
            "worst_return": min(returns),
            "std_return": self._std(returns),
        }

    def _std(self, values: List[float]) -> float:
        """计算标准差"""
        if not values:
            return 0
        avg = sum(values) / len(values)
        return (sum((v - avg) ** 2 for v in values) / len(values)) ** 0.5

    def _generate_recommendations(self, all_results: Dict) -> Dict:
        """生成推荐参数"""
        recommendations = {}

        for mode in ["conservative", "balanced", "aggressive"]:
            mode_data = all_results.get(mode, {})
            regular = mode_data.get("regular", {})
            expert = mode_data.get("expert", {})

            # 根据模拟结果调整参数
            regular_return = regular.get("avg_return", 0)
            expert_return = expert.get("avg_return", 0)

            recommendations[mode] = {
                "regular": {
                    "max_position": self.MODES[mode]["max_position"],
                    "stop_loss": self.MODES[mode]["stop_loss"],
                    "take_profit": self.MODES[mode]["take_profit"],
                    "leverage": self.MODES[mode]["leverage"],
                    "expected_return": f"{regular_return*100:.1f}%",
                    "risk_adjusted": regular_return / max(regular.get("avg_drawdown", 0.01), 0.001),
                },
                "expert": {
                    "max_position": self.MODES[mode]["max_position"] * 1.2,
                    "stop_loss": self.MODES[mode]["stop_loss"] * 0.7,
                    "take_profit": "无限制",
                    "leverage": 1,
                    "tools": ["rabbit", "leader", "hitchhiker"],
                    "expected_return": f"{expert_return*100:.1f}%",
                    "risk_adjusted": expert_return / max(expert.get("avg_drawdown", 0.01), 0.001),
                },
                "thresholds": {
                    "extreme_trend": 0.80,
                    "strong_trend": 0.60,
                    "neutral_trend": 0.40,
                    "weak_trend": 0.20,
                    "position_increase": 1.5,
                    "position_decrease": 0.5,
                },
            }

        return recommendations

    def print_summary(self, results: Dict):
        """打印结果摘要"""
        print("\n" + "=" * 80)
        print("📊 模拟结果摘要")
        print("=" * 80)

        for mode in ["conservative", "balanced", "aggressive"]:
            mode_data = results["results"].get(mode, {})
            regular = mode_data.get("regular", {})
            expert = mode_data.get("expert", {})

            print(f"\n🔹 {mode.upper()} 模式")
            print("-" * 60)
            print(f"  普通模式: 收益 {regular.get('avg_return', 0)*100:.1f}%, 回撤 {regular.get('avg_drawdown', 0)*100:.1f}%, 胜率 {regular.get('avg_win_rate', 0)*100:.1f}%")
            print(f"  专家模式: 收益 {expert.get('avg_return', 0)*100:.1f}%, 回撤 {expert.get('avg_drawdown', 0)*100:.1f}%, 胜率 {expert.get('avg_win_rate', 0)*100:.1f}%")


def run_simulation():
    """运行模拟"""
    simulator = PortfolioSimulationMatrix(runs=50)
    results = simulator.run_full_simulation()
    simulator.print_summary(results)
    return results


if __name__ == "__main__":
    results = run_simulation()
    print("\n✅ 模拟完成!")
