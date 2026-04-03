"""
TradingEvolutionLearner - 交易进化学习器
======================================
基于历史表现自动学习和优化交易策略
"""
from __future__ import annotations
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import random


@dataclass
class StrategyRecord:
    """策略记录"""
    strategy_id: str
    strategy_name: str
    tool: str
    win_rate: float
    return_pct: float
    sharpe_ratio: float
    max_drawdown: float
    trade_count: int
    timestamp: str


@dataclass
class EvolutionResult:
    """进化结果"""
    generation: int
    best_strategy_id: str
    best_score: float
    improvements: List[str]
    mutations: List[str]
    dropped_strategies: List[str]
    new_strategies: List[str]


class TradingEvolutionLearner:
    """
    交易进化学习器
    =================
    基于遗传算法的策略自动进化

    流程:
    1. 记录策略表现
    2. 选择优秀策略
    3. 交叉变异
    4. 生成新策略
    5. 淘汰差策略
    """

    def __init__(self, population_size: int = 20, mutation_rate: float = 0.1):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.strategies: List[StrategyRecord] = []
        self.generation = 0
        self.history: List[EvolutionResult] = []

    def record_performance(self, strategy: StrategyRecord) -> None:
        """记录策略表现"""
        self.strategies.append(strategy)

    def evolve(self) -> EvolutionResult:
        """执行一代进化"""
        self.generation += 1

        if len(self.strategies) < 3:
            return EvolutionResult(
                generation=self.generation,
                best_strategy_id="",
                best_score=0.0,
                improvements=[],
                mutations=[],
                dropped_strategies=[],
                new_strategies=[],
            )

        # 计算适应度
        fitness = self._calculate_fitness()

        # 选择优秀策略
        selected = self._selection(fitness)

        # 交叉变异
        new_strategies = self._crossover_mutate(selected)

        # 淘汰差策略
        dropped = self._淘汰(fitness)

        # 生成结果
        best_idx = max(range(len(fitness)), key=lambda i: fitness[i])
        best_score = fitness[best_idx]
        best_id = self.strategies[best_idx].strategy_id if best_idx < len(self.strategies) else ""

        result = EvolutionResult(
            generation=self.generation,
            best_strategy_id=best_id,
            best_score=best_score,
            improvements=self._generate_improvements(selected),
            mutations=self._generate_mutations(),
            dropped_strategies=dropped,
            new_strategies=new_strategies,
        )

        self.history.append(result)
        return result

    def _calculate_fitness(self) -> List[float]:
        """计算适应度"""
        fitness = []
        for s in self.strategies:
            # 综合评分 = 胜率*0.3 + 收益*0.3 + Sharpe*0.2 - 回撤*0.2
            score = (
                s.win_rate * 0.30 +
                s.return_pct * 0.30 +
                s.sharpe_ratio * 0.20 -
                s.max_drawdown * 0.20
            )
            fitness.append(max(0, score))
        return fitness

    def _selection(self, fitness: List[float]) -> List[StrategyRecord]:
        """轮盘赌选择"""
        total = sum(fitness)
        if total == 0:
            return self.strategies[:self.population_size // 2]

        probabilities = [f / total for f in fitness]
        selected = []
        for _ in range(min(len(self.strategies), self.population_size // 2)):
            r = random.random()
            cumsum = 0
            for i, p in enumerate(probabilities):
                cumsum += p
                if r <= cumsum:
                    selected.append(self.strategies[i])
                    break
        return selected

    def _crossover_mutate(self, selected: List[StrategyRecord]) -> List[str]:
        """交叉变异生成新策略"""
        new_strategy_names = []

        for _ in range(len(selected), self.population_size):
            if len(selected) >= 2:
                p1, p2 = random.sample(selected, 2)
                # 生成新策略名称
                new_name = f"{p1.strategy_name}+{p2.strategy_name}"
                new_strategy_names.append(new_name)

        return new_strategy_names

    def _淘汰(self, fitness: List[float]) -> List[str]:
        """淘汰最差策略"""
        if len(self.strategies) <= self.population_size:
            return []

        # 找出最差的20%
        n_drop = max(1, len(self.strategies) // 5)
        indices = sorted(range(len(fitness)), key=lambda i: fitness[i])[:n_drop]
        dropped = [self.strategies[i].strategy_id for i in indices]
        self.strategies = [s for i, s in enumerate(self.strategies) if i not in indices]
        return dropped

    def _generate_improvements(self, selected: List[StrategyRecord]) -> List[str]:
        """生成改进建议"""
        improvements = []
        if selected:
            best = max(selected, key=lambda s: s.win_rate)
            improvements.append(f"胜率最高策略: {best.strategy_name} ({best.win_rate*100:.1f}%)")
            best_ret = max(selected, key=lambda s: s.return_pct)
            improvements.append(f"收益最高策略: {best_ret.strategy_name} ({best_ret.return_pct*100:.1f}%)")
        return improvements

    def _generate_mutations(self) -> List[str]:
        """生成变异描述"""
        mutations = []
        if random.random() < self.mutation_rate:
            mutations.append("参数随机扰动")
        if random.random() < self.mutation_rate:
            mutations.append("止损阈值调整")
        if random.random() < self.mutation_rate * 0.5:
            mutations.append("仓位比例微调")
        return mutations

    def get_best_strategies(self, top_n: int = 5) -> List[Dict[str, Any]]:
        """获取最佳策略"""
        fitness = self._calculate_fitness()
        scored = list(zip(self.strategies, fitness))
        scored.sort(key=lambda x: x[1], reverse=True)
        return [
            {
                "strategy_id": s.strategy_id,
                "strategy_name": s.strategy_name,
                "tool": s.tool,
                "score": score,
                "win_rate": s.win_rate,
                "return_pct": s.return_pct,
                "sharpe_ratio": s.sharpe_ratio,
                "max_drawdown": s.max_drawdown,
            }
            for s, score in scored[:top_n]
        ]

    def get_evolution_summary(self) -> Dict[str, Any]:
        """获取进化摘要"""
        return {
            "generation": self.generation,
            "total_strategies": len(self.strategies),
            "history_count": len(self.history),
            "avg_score": sum(self._calculate_fitness()) / max(len(self.strategies), 1),
            "best_ever": self.get_best_strategies(1)[0] if self.strategies else None,
        }
