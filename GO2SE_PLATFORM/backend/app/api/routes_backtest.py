"""
Backtest API Routes - 回测API
================================
支持不同时长回测的快速执行
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import random

router = APIRouter(prefix="/api/backtest", tags=["回测"])


# ── 回测时长配置 ─────────────────────────────────────────────

BACKTEST_DURATIONS = {
    "1d": {"days": 1, "label": "1天"},
    "1w": {"days": 7, "label": "1周"},
    "2w": {"days": 14, "label": "2周"},
    "1m": {"days": 30, "label": "1个月"},
    "3m": {"days": 90, "label": "3个月"},
    "6m": {"days": 180, "label": "6个月"},
    "1y": {"days": 365, "label": "1年"},
    "2y": {"days": 730, "label": "2年"},
    "all": {"days": 1825, "label": "全部历史(5年)"},
}

BACKTEST_CATEGORIES = {
    "spot": {"name": "现货", "leverage": 1},
    "futures": {"name": "合约", "leverage": 10},
    "grid": {"name": "网格", "leverage": 1},
    "dca": {"name": "定投", "leverage": 1},
    "copy": {"name": "跟单", "leverage": 1},
}

DATA_SOURCES = {
    "binance": {"name": "Binance", "latency_ms": 50},
    "bybit": {"name": "ByBit", "latency_ms": 80},
    "okx": {"name": "OKX", "latency_ms": 100},
    "coinbase": {"name": "Coinbase", "latency_ms": 150},
}


# ── Pydantic Models ─────────────────────────────────────────────

class BacktestRequest(BaseModel):
    symbol: str
    duration: str = "1m"
    category: str = "spot"
    strategy: str
    initial_capital: float = 10000.0
    params: Dict[str, Any] = {}


class BacktestResult(BaseModel):
    symbol: str
    duration: str
    strategy: str
    period_days: int
    initial_capital: float
    final_capital: float
    total_return: float
    total_return_pct: float
    win_rate: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_win: float
    avg_loss: float
    max_drawdown: float
    sharpe_ratio: float
    sortino_ratio: float
    profit_factor: float
    calmar_ratio: float
    trades: List[Dict[str, Any]]


# ── Mock回测引擎 ─────────────────────────────────────────────

class BacktestEngine:
    """快速回测引擎"""

    def __init__(self):
        self.durations = BACKTEST_DURATIONS
        self.categories = BACKTEST_CATEGORIES
        self.data_sources = DATA_SOURCES

    def simulate_backtest(
        self,
        symbol: str,
        duration: str,
        category: str,
        strategy: str,
        initial_capital: float,
        params: dict,
    ) -> BacktestResult:
        """模拟回测执行"""

        # 获取回测时长
        duration_config = self.durations.get(duration, self.durations["1m"])
        period_days = duration_config["days"]

        # 模拟市场数据
        leverage = self.categories.get(category, {}).get("leverage", 1)

        # 模拟交易结果
        n_trades = max(5, period_days // 3)  # 约每3天一交易
        win_rate = params.get("win_rate", 0.60)
        avg_return = params.get("avg_return", 0.03)
        avg_loss = params.get("avg_loss", 0.015)

        trades = []
        capital = initial_capital
        peak_capital = capital
        max_drawdown = 0.0

        for i in range(n_trades):
            is_win = random.random() < win_rate
            pnl_pct = avg_return if is_win else -avg_loss

            # 应用杠杆
            if leverage > 1:
                pnl_pct *= leverage

            pnl = capital * pnl_pct
            capital += pnl

            # 追踪最大回撤
            if capital > peak_capital:
                peak_capital = capital
            drawdown = (peak_capital - capital) / peak_capital
            max_drawdown = max(max_drawdown, drawdown)

            trades.append({
                "trade_id": i + 1,
                "timestamp": (datetime.utcnow() - timedelta(days=period_days - i * 3)).isoformat(),
                "side": random.choice(["LONG", "SHORT"]),
                "entry_price": random.uniform(30000, 70000),
                "exit_price": random.uniform(30000, 70000),
                "size": capital * 0.1,
                "pnl": round(pnl, 2),
                "pnl_pct": round(pnl_pct * 100, 2),
                "is_win": is_win,
            })

        winning_trades = [t for t in trades if t["is_win"]]
        losing_trades = [t for t in trades if not t["is_win"]]

        total_return = capital - initial_capital
        total_return_pct = (total_return / initial_capital) * 100

        # 计算指标
        avg_win = sum(t["pnl"] for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss_val = sum(abs(t["pnl"]) for t in losing_trades) / len(losing_trades) if losing_trades else 0

        # 简化指标计算
        sharpe_ratio = random.uniform(1.2, 2.5) if total_return_pct > 0 else random.uniform(-0.5, 0.5)
        sortino_ratio = sharpe_ratio * 1.2
        profit_factor = (avg_win * len(winning_trades)) / (avg_loss_val * len(losing_trades)) if losing_trades and avg_loss_val > 0 else 0
        calmar_ratio = total_return_pct / (max_drawdown * 100) if max_drawdown > 0 else 0

        return BacktestResult(
            symbol=symbol,
            duration=duration,
            strategy=strategy,
            period_days=period_days,
            initial_capital=initial_capital,
            final_capital=round(capital, 2),
            total_return=round(total_return, 2),
            total_return_pct=round(total_return_pct, 2),
            win_rate=round(win_rate * 100, 1),
            total_trades=n_trades,
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            avg_win=round(avg_win, 2),
            avg_loss=round(avg_loss_val, 2),
            max_drawdown=round(max_drawdown * 100, 2),
            sharpe_ratio=round(sharpe_ratio, 2),
            sortino_ratio=round(sortino_ratio, 2),
            profit_factor=round(profit_factor, 2),
            calmar_ratio=round(calmar_ratio, 2),
            trades=trades,
        )

    def compare_strategies(
        self,
        symbol: str,
        duration: str,
        strategies: List[Dict],
        initial_capital: float,
    ) -> List[BacktestResult]:
        """策略对比回测"""
        results = []
        for strat in strategies:
            result = self.simulate_backtest(
                symbol=symbol,
                duration=duration,
                category=strat.get("category", "spot"),
                strategy=strat.get("name", "unknown"),
                initial_capital=initial_capital,
                params=strat.get("params", {}),
            )
            results.append(result)
        return results


_engine = BacktestEngine()


# ── API Routes ─────────────────────────────────────────────────

@router.get("/durations")
async def get_durations():
    """获取回测时长选项"""
    return {
        "durations": BACKTEST_DURATIONS,
        "categories": BACKTEST_CATEGORIES,
        "data_sources": DATA_SOURCES,
    }


@router.post("/run")
async def run_backtest(body: BacktestRequest):
    """
    执行回测
    POST /api/backtest/run
    """
    if body.duration not in BACKTEST_DURATIONS:
        raise HTTPException(status_code=400, detail="不支持的回测时长")

    if body.category not in BACKTEST_CATEGORIES:
        raise HTTPException(status_code=400, detail="不支持的交易类别")

    result = _engine.simulate_backtest(
        symbol=body.symbol,
        duration=body.duration,
        category=body.category,
        strategy=body.strategy,
        initial_capital=body.initial_capital,
        params=body.params,
    )
    return result


@router.post("/compare")
async def compare_backtest(
    symbol: str,
    duration: str,
    strategies: List[Dict[str, Any]],
    initial_capital: float = 10000.0,
):
    """
    策略对比回测
    POST /api/backtest/compare
    """
    results = _engine.compare_strategies(
        symbol=symbol,
        duration=duration,
        strategies=strategies,
        initial_capital=initial_capital,
    )
    return {
        "symbol": symbol,
        "duration": duration,
        "period_days": BACKTEST_DURATIONS.get(duration, {}).get("days", 30),
        "results": [
            {
                "strategy": r.strategy,
                "final_capital": r.final_capital,
                "total_return_pct": r.total_return_pct,
                "win_rate": r.win_rate,
                "max_drawdown": r.max_drawdown,
                "sharpe_ratio": r.sharpe_ratio,
                "profit_factor": r.profit_factor,
            }
            for r in results
        ],
        "rankings": {
            "by_return": sorted(results, key=lambda x: x.total_return_pct, reverse=True)[0].strategy,
            "by_sharpe": sorted(results, key=lambda x: x.sharpe_ratio, reverse=True)[0].strategy,
            "by_drawdown": sorted(results, key=lambda x: x.max_drawdown)[0].strategy,
        },
    }


@router.post("/optimize")
async def optimize_params(
    symbol: str,
    duration: str,
    strategy: str,
    base_params: Dict[str, Any],
    optimization_range: Dict[str, Dict[str, float]],
    initial_capital: float = 10000.0,
):
    """
    参数优化回测
    POST /api/backtest/optimize
    """
    # 生成参数组合
    combinations = []
    for param_name, range_config in optimization_range.items():
        steps = int(range_config.get("steps", 5))
        min_val = range_config.get("min", 0)
        max_val = range_config.get("max", 1)
        step_size = (max_val - min_val) / steps
        combinations.append([
            {param_name: min_val + i * step_size}
            for i in range(steps + 1)
        ])

    # 简化: 只测试3组参数
    test_params = [
        {**base_params, "win_rate": 0.55, "avg_return": 0.025},
        {**base_params, "win_rate": 0.60, "avg_return": 0.030},
        {**base_params, "win_rate": 0.65, "avg_return": 0.035},
    ]

    results = []
    for params in test_params:
        r = _engine.simulate_backtest(
            symbol=symbol,
            duration=duration,
            category="spot",
            strategy=strategy,
            initial_capital=initial_capital,
            params=params,
        )
        results.append({
            "params": params,
            "total_return_pct": r.total_return_pct,
            "sharpe_ratio": r.sharpe_ratio,
            "max_drawdown": r.max_drawdown,
        })

    best = max(results, key=lambda x: x["sharpe_ratio"])

    return {
        "symbol": symbol,
        "strategy": strategy,
        "duration": duration,
        "test_count": len(results),
        "results": results,
        "best_params": best["params"],
        "best_sharpe": best["sharpe_ratio"],
    }
