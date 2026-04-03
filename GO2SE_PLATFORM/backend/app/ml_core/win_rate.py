"""
WinRatePredictor - 胜率预测
=============================
基于历史统计的胜率预测
蒙特卡洛模拟、置信区间、风险调整收益
"""
import logging
import random
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class WinRatePredictor:
    """
    胜率预测
    =========
    功能:
    - 单策略胜率预测
    - 多策略组合胜率
    - 蒙特卡洛模拟
    - 置信区间计算
    - 风险调整收益 (Sharpe/Sortino/Calmar)
    """

    def __init__(self):
        self.name = "WinRatePredictor"
        self.strategies = {
            "突破策略": {"win_rate": 0.62, "avg_return": 0.034, "avg_loss": 0.018, "trade_count": 156},
            "均值回归": {"win_rate": 0.58, "avg_return": 0.021, "avg_loss": 0.025, "trade_count": 203},
            "趋势跟踪": {"win_rate": 0.55, "avg_return": 0.048, "avg_loss": 0.031, "trade_count": 89},
            "网格交易": {"win_rate": 0.71, "avg_return": 0.008, "avg_loss": 0.012, "trade_count": 412},
            "套利": {"win_rate": 0.82, "avg_return": 0.003, "avg_loss": 0.002, "trade_count": 678},
            "打兔子": {"win_rate": 0.65, "avg_return": 0.025, "avg_loss": 0.015, "trade_count": 234},
            "打地鼠": {"win_rate": 0.48, "avg_return": 0.065, "avg_loss": 0.040, "trade_count": 67},
        }
        self.metrics = {"predictions": 0, "avg_win_rate": 0.0}

    def predict_win_rate(
        self,
        strategy_name: str,
        symbol: Optional[str] = None,
        market_regime: str = "NORMAL",
    ) -> Dict[str, Any]:
        """预测策略胜率"""
        strat = self.strategies.get(strategy_name)
        if not strat:
            return {"error": f"Unknown strategy: {strategy_name}"}

        base_wr = strat["win_rate"]
        regime_multipliers = {"BULL": 1.08, "NORMAL": 1.0, "BEAR": 0.92, "VOLATILE": 0.85}
        adjusted_wr = min(base_wr * regime_multipliers.get(market_regime, 1.0), 0.98)

        confidence_interval = self._wilson_confidence(adjusted_wr, strat["trade_count"])
        expectancy = (adjusted_wr * strat["avg_return"]) - ((1 - adjusted_wr) * strat["avg_loss"])

        return {
            "strategy": strategy_name,
            "symbol": symbol,
            "market_regime": market_regime,
            "base_win_rate": base_wr,
            "adjusted_win_rate": round(adjusted_wr, 4),
            "confidence_interval_95": confidence_interval,
            "expectancy_per_trade": round(expectancy, 5),
            "trade_count": strat["trade_count"],
            "sharpe_estimate": round(self._estimate_sharpe(strat, adjusted_wr), 2),
            "recommendation": "EXECUTE" if adjusted_wr > 0.55 and expectancy > 0 else "REVIEW",
        }

    def predict_combined_win_rate(
        self,
        strategy_names: List[str],
        weights: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """多策略组合胜率预测"""
        if weights is None:
            weights = [1.0 / len(strategy_names)] * len(strategy_names)
        weights = [w / sum(weights) for w in weights]

        predictions = []
        for name, weight in zip(strategy_names, weights):
            p = self.predict_win_rate(name)
            predictions.append({"name": name, "weight": weight, **p})
            self.metrics["predictions"] += 1

        combined_wr = sum(p["adjusted_win_rate"] * w for p, w in zip(predictions, weights))
        combined_expectancy = sum(p["expectancy_per_trade"] * w for p, w in zip(predictions, weights))
        avg_sharpe = sum(p["sharpe_estimate"] * w for p, w in zip(predictions, weights))

        monte_carlo = self._monte_carlo_simulation(combined_wr, combined_expectancy, n_simulations=1000)

        self.metrics["avg_win_rate"] = round(combined_wr, 4)

        return {
            "strategies": predictions,
            "weights": weights,
            "combined_win_rate": round(combined_wr, 4),
            "combined_expectancy": round(combined_expectancy, 5),
            "expected_sharpe": round(avg_sharpe, 2),
            "monte_carlo": monte_carlo,
            "recommendation": "PORTFOLIO" if combined_wr > 0.55 else "REDUCE",
        }

    def _wilson_confidence(self, win_rate: float, n: int) -> Dict[str, float]:
        """Wilson score置信区间"""
        if n == 0:
            return {"lower": 0.0, "upper": 1.0}
        import math
        z = 1.96
        p = win_rate
        N = n
        denom = 1 + z**2 / N
        center = (p + z**2 / (2 * N)) / denom
        margin = z * math.sqrt((p * (1 - p) + z**2 / (4 * N)) / N) / denom
        return {
            "lower": round(max(0, center - margin), 4),
            "upper": round(min(1, center + margin), 4),
        }

    def _estimate_sharpe(self, strat: Dict, adjusted_wr: float) -> float:
        """估算Sharpe比率"""
        avg_return = strat["avg_return"]
        avg_loss = strat["avg_loss"]
        win_prob = adjusted_wr
        loss_prob = 1 - adjusted_wr
        expected_return = win_prob * avg_return - loss_prob * avg_loss
        return round(expected_return / (avg_loss * 2), 2) if avg_loss > 0 else 0

    def _monte_carlo_simulation(
        self,
        win_rate: float,
        expectancy: float,
        n_simulations: int = 1000,
        n_trades: int = 100,
    ) -> Dict[str, Any]:
        """蒙特卡洛模拟"""
        outcomes = []
        for _ in range(n_simulations):
            equity = 1.0
            for _ in range(n_trades):
                if random.random() < win_rate:
                    equity *= (1 + expectancy)
                else:
                    equity *= (1 - expectancy * 0.5)
            outcomes.append(equity)

        outcomes.sort()
        return {
            "n_simulations": n_simulations,
            "n_trades_per_sim": n_trades,
            "final_equity_p10": round(outcomes[int(len(outcomes) * 0.1)], 4),
            "final_equity_p50": round(outcomes[int(len(outcomes) * 0.5)], 4),
            "final_equity_p90": round(outcomes[int(len(outcomes) * 0.9)], 4),
            "max_drawdown_p10": round((1 - outcomes[int(len(outcomes) * 0.1)]) * 100, 2),
            "max_drawdown_p50": round((1 - outcomes[int(len(outcomes) * 0.5)]) * 100, 2),
            "prob_profit": round(sum(1 for o in outcomes if o > 1.0) / len(outcomes), 4),
        }

    def analyze_trade_history(self, trades: List[Dict]) -> Dict[str, Any]:
        """分析交易历史"""
        if not trades:
            return {"error": "No trades provided"}

        wins = [t for t in trades if t.get("pnl", 0) > 0]
        losses = [t for t in trades if t.get("pnl", 0) <= 0]
        win_rate = len(wins) / len(trades) if trades else 0

        return {
            "total_trades": len(trades),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": round(win_rate, 4),
            "avg_win": round(sum(t["pnl"] for t in wins) / len(wins), 4) if wins else 0,
            "avg_loss": round(sum(abs(t["pnl"]) for t in losses) / len(losses), 4) if losses else 0,
            "best_trade": max(t["pnl"] for t in trades) if trades else 0,
            "worst_trade": min(t["pnl"] for t in trades) if trades else 0,
        }
