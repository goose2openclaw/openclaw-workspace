"""
StrategyOptimizer - 策略优化器
===============================
贝叶斯优化、网格搜索、遗传算法
参数自动调优、A/B测试框架
"""
import logging
import random
from typing import Dict, Any, List, Callable, Optional

logger = logging.getLogger(__name__)


class StrategyOptimizer:
    """
    策略优化器
    =========
    功能:
    - 参数网格搜索
    - 贝叶斯优化
    - 遗传算法进化
    - 策略A/B测试
    """

    def __init__(self):
        self.name = "StrategyOptimizer"
        self.optimizers = {
            "grid_search": {"calls": 0, "best_score": 0.0},
            "bayesian": {"calls": 0, "best_score": 0.0},
            "genetic": {"generations": 0, "best_fitness": 0.0},
        }
        self.metrics = {"optimizations_run": 0, "improvements": []}

    def grid_search(
        self,
        param_space: Dict[str, List[Any]],
        objective_fn: Callable,
        max_trials: int = 100,
    ) -> Dict[str, Any]:
        """网格搜索优化"""
        results = []
        trial_count = 0
        for params in self._iter_param_space(param_space, max_trials):
            score = objective_fn(params)
            results.append({"params": params, "score": score})
            trial_count += 1
            if score > self.optimizers["grid_search"]["best_score"]:
                self.optimizers["grid_search"]["best_score"] = score

        self.optimizers["grid_search"]["calls"] += 1
        self.metrics["optimizations_run"] += 1
        best = max(results, key=lambda r: r["score"])
        return {
            "optimizer": "grid_search",
            "best_params": best["params"],
            "best_score": best["score"],
            "trials": trial_count,
            "all_results": results[:10],
        }

    def _iter_param_space(self, param_space: Dict, max_trials: int):
        """参数空间迭代"""
        keys = list(param_space.keys())
        values = list(param_space.values())
        for _ in range(min(max_trials, 1000)):
            yield dict(zip(keys, [random.choice(v) for v in values]))

    def bayesian_optimize(
        self,
        bounds: Dict[str, tuple],
        objective_fn: Callable,
        n_iterations: int = 20,
    ) -> Dict[str, Any]:
        """贝叶斯优化 (简化版)"""
        best_score = 0.0
        best_params = {}
        history = []

        for i in range(n_iterations):
            params = {k: random.uniform(v[0], v[1]) for k, v in bounds.items()}
            score = objective_fn(params)
            history.append({"iteration": i + 1, "params": params, "score": score})

            if score > best_score:
                best_score = score
                best_params = params

        self.optimizers["bayesian"]["calls"] += 1
        self.optimizers["bayesian"]["best_score"] = best_score
        self.metrics["optimizations_run"] += 1
        return {
            "optimizer": "bayesian",
            "best_params": best_params,
            "best_score": best_score,
            "iterations": n_iterations,
            "history": history[-10:],
        }

    def genetic_optimize(
        self,
        initial_population: List[Dict],
        fitness_fn: Callable,
        n_generations: int = 30,
        mutation_rate: float = 0.1,
    ) -> Dict[str, Any]:
        """遗传算法优化"""
        population = initial_population[:]
        best_fitness = 0.0
        best_individual = {}

        for gen in range(n_generations):
            fitness_scores = [(ind, fitness_fn(ind)) for ind in population]
            fitness_scores.sort(key=lambda x: x[1], reverse=True)

            if fitness_scores[0][1] > best_fitness:
                best_fitness = fitness_scores[0][1]
                best_individual = fitness_scores[0][0]

            parents = [ind for ind, _ in fitness_scores[:len(population) // 2]]
            new_population = parents[:]

            while len(new_population) < len(population):
                p1, p2 = random.sample(parents, 2)
                child = self._crossover(p1, p2)
                if random.random() < mutation_rate:
                    child = self._mutate(child)
                new_population.append(child)

            population = new_population

        self.optimizers["genetic"]["generations"] += n_generations
        self.optimizers["genetic"]["best_fitness"] = best_fitness
        self.metrics["optimizations_run"] += 1
        return {
            "optimizer": "genetic",
            "best_individual": best_individual,
            "best_fitness": best_fitness,
            "generations": n_generations,
        }

    def _crossover(self, p1: Dict, p2: Dict) -> Dict:
        return {k: p1[k] if random.random() > 0.5 else p2[k] for k in p1}

    def _mutate(self, individual: Dict) -> Dict:
        return {k: v + random.uniform(-0.1, 0.1) if isinstance(v, (int, float)) else v for k, v in individual.items()}
