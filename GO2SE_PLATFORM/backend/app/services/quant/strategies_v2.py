#!/usr/bin/env python3
"""
📊 十大量化交易策略 - 打工加密货币模块 V2
=========================================
支持权重调整 → 决策等式 → 回测 → 仿真
"""

import time
import random
import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import deque

# ─── 策略枚举 ──────────────────────────────────────────

class StrategyCategory(str, Enum):
    TREND = "trend_following"      # 趋势跟踪
    MEAN_REVERT = "mean_reversion" # 均值回归
    MARKET_NEUTRAL = "market_neutral" # 市场中性
    ML = "machine_learning"        # 机器学习

class SignalType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

# ─── 策略数据类 ───────────────────────────────────────

@dataclass
class StrategyParams:
    """策略参数"""
    name: str
    category: StrategyCategory
    description: str
    # 假设绩效指标
    assumed_win_rate: float       # 假设胜率 (0-1)
    assumed_return: float         # 假设收益率 (年化, 0-1)
    assumed_max_drawdown: float   # 假设最大回撤 (0-1)
    assumed_sharpe: float         # 假设夏普比率
    # 可调权重
    weight: float = 0.0          # 当前权重 (0-1)
    weight_default: float = 0.0   # 默认权重
    enabled: bool = True
    min_weight: float = 0.0
    max_weight: float = 0.5

@dataclass
class StrategySignal:
    """策略信号"""
    strategy_id: str
    strategy_name: str
    signal: SignalType
    confidence: float            # 0-1
    entry_price: float = 0
    target_price: float = 0
    stop_loss: float = 0
    timestamp: str = ""
    reason: str = ""

@dataclass
class BacktestResult:
    """回测结果"""
    strategy_id: str
    total_trades: int
    win_trades: int
    lose_trades: int
    win_rate: float
    total_return: float
    max_drawdown: float
    sharpe_ratio: float
    profit_factor: float
    avg_win: float
    avg_loss: float
    consecutive_wins: int
    consecutive_losses: int
    roi_annualized: float

@dataclass
class SimulationResult:
    """仿真结果"""
    strategy_id: str
    period_days: int
    start_balance: float
    end_balance: float
    total_return: float
    return_pct: float
    max_drawdown: float
    sharpe_ratio: float
    win_rate: float
    trade_count: int
    best_trade: float
    worst_trade: float


# ─── 十大量化策略 ────────────────────────────────────

STRATEGIES: Dict[str, StrategyParams] = {
    "dca": StrategyParams(
        name="DCA定投策略",
        category=StrategyCategory.TREND,
        description="Dollar Cost Averaging - 定期定额投资，平滑成本，降低择时风险",
        assumed_win_rate=0.62,
        assumed_return=0.15,
        assumed_max_drawdown=0.25,
        assumed_sharpe=1.2,
        weight=0.15, weight_default=0.15,
        min_weight=0.0, max_weight=0.30
    ),
    "grid": StrategyParams(
        name="网格交易策略",
        category=StrategyCategory.MEAN_REVERT,
        description="Grid Trading - 在价格区间内低买高卖，自动化高抛低吸",
        assumed_win_rate=0.68,
        assumed_return=0.25,
        assumed_max_drawdown=0.30,
        assumed_sharpe=1.5,
        weight=0.12, weight_default=0.12,
        min_weight=0.0, max_weight=0.25
    ),
    "momentum": StrategyParams(
        name="动量突破策略",
        category=StrategyCategory.TREND,
        description="Momentum Breakout - 追涨杀跌，顺势而为，趋势跟踪核心",
        assumed_win_rate=0.45,
        assumed_return=0.40,
        assumed_max_drawdown=0.50,
        assumed_sharpe=1.8,
        weight=0.10, weight_default=0.10,
        min_weight=0.0, max_weight=0.30
    ),
    "rsi_revert": StrategyParams(
        name="RSI均值回归策略",
        category=StrategyCategory.MEAN_REVERT,
        description="RSI Mean Reversion - RSI超卖买入(30)，超买卖出(70)",
        assumed_win_rate=0.58,
        assumed_return=0.20,
        assumed_max_drawdown=0.22,
        assumed_sharpe=1.4,
        weight=0.13, weight_default=0.13,
        min_weight=0.0, max_weight=0.25
    ),
    "bollinger": StrategyParams(
        name="布林带策略",
        category=StrategyCategory.MEAN_REVERT,
        description="Bollinger Bands - 下轨买入，上轨卖出，中轨动态止损",
        assumed_win_rate=0.55,
        assumed_return=0.18,
        assumed_max_drawdown=0.28,
        assumed_sharpe=1.3,
        weight=0.12, weight_default=0.12,
        min_weight=0.0, max_weight=0.20
    ),
    "macd_cross": StrategyParams(
        name="MACD交叉策略",
        category=StrategyCategory.TREND,
        description="MACD Cross - 金叉买入，死叉卖出，趋势确认信号",
        assumed_win_rate=0.48,
        assumed_return=0.35,
        assumed_max_drawdown=0.45,
        assumed_sharpe=1.6,
        weight=0.10, weight_default=0.10,
        min_weight=0.0, max_weight=0.25
    ),
    "arbitrage": StrategyParams(
        name="套利策略",
        category=StrategyCategory.MARKET_NEUTRAL,
        description="Arbitrage - 跨交易所/跨品种价差套利，风险低收益稳",
        assumed_win_rate=0.78,
        assumed_return=0.12,
        assumed_max_drawdown=0.08,
        assumed_sharpe=2.5,
        weight=0.08, weight_default=0.08,
        min_weight=0.0, max_weight=0.15
    ),
    "market_maker": StrategyParams(
        name="做市商策略",
        category=StrategyCategory.MARKET_NEUTRAL,
        description="Market Making - 提供流动性，赚取买卖价差，胜率高",
        assumed_win_rate=0.72,
        assumed_return=0.15,
        assumed_max_drawdown=0.12,
        assumed_sharpe=2.2,
        weight=0.08, weight_default=0.08,
        min_weight=0.0, max_weight=0.15
    ),
    "stat_arb": StrategyParams(
        name="统计套利策略",
        category=StrategyCategory.MARKET_NEUTRAL,
        description="Statistical Arbitrage - 配对交易，均值回归概率高",
        assumed_win_rate=0.65,
        assumed_return=0.18,
        assumed_max_drawdown=0.15,
        assumed_sharpe=2.0,
        weight=0.07, weight_default=0.07,
        min_weight=0.0, max_weight=0.15
    ),
    "ml_selector": StrategyParams(
        name="AI量化选币策略",
        category=StrategyCategory.ML,
        description="ML Token Selection - AI多因子选币，动态调仓，收益潜力大",
        assumed_win_rate=0.55,
        assumed_return=0.50,
        assumed_max_drawdown=0.55,
        assumed_sharpe=1.9,
        weight=0.05, weight_default=0.05,
        min_weight=0.0, max_weight=0.20
    ),
}


# ─── 核心引擎 ────────────────────────────────────────

class QuantStrategiesEngine:
    """
    📊 十大量化策略引擎
    权重配置 → 信号生成 → 决策等式 → 回测 → 仿真
    """

    def __init__(self):
        self.strategies = {k: StrategyParams(**v.__dict__) for k, v in STRATEGIES.items()}
        self._signal_history: Dict[str, deque] = {k: deque(maxlen=100) for k in STRATEGIES}
        self._price_history: deque = deque(maxlen=200)

    # ─── 权重管理 ─────────────────────────────────

    def set_weight(self, strategy_id: str, weight: float) -> bool:
        """设置策略权重"""
        if strategy_id not in self.strategies:
            return False
        s = self.strategies[strategy_id]
        weight = max(s.min_weight, min(s.max_weight, weight))
        s.weight = weight
        return True

    def set_weights(self, weights: Dict[str, float]) -> Dict[str, bool]:
        """批量设置权重"""
        return {k: self.set_weight(k, v) for k, v in weights.items()}

    def reset_weights(self):
        """重置为默认权重"""
        for s in self.strategies.values():
            s.weight = s.weight_default

    def normalize_weights(self) -> float:
        """
        归一化权重，确保总和=1
        返回调整量
        """
        total = sum(s.weight for s in self.strategies.values() if s.enabled)
        if total == 0:
            return 0.0
        for s in self.strategies.values():
            if s.enabled:
                s.weight = s.weight / total
        return 1.0 - abs(total - 1.0)

    def get_weighted_signal(self) -> Dict:
        """
        加权信号计算
        决策等式: S = Σ(wi × Si) / Σwi
        """
        total_weight = 0.0
        weighted_buy = 0.0
        weighted_sell = 0.0
        weighted_confidence = 0.0

        for sid, s in self.strategies.items():
            if not s.enabled or s.weight == 0:
                continue

            # 模拟当前信号
            signal = self._generate_mock_signal(sid)
            conf = signal.confidence

            if signal.signal == SignalType.BUY:
                weighted_buy += s.weight * conf
            elif signal.signal == SignalType.SELL:
                weighted_sell += s.weight * conf

            weighted_confidence += s.weight * conf
            total_weight += s.weight

        if total_weight == 0:
            return {"signal": SignalType.HOLD, "confidence": 0, "buy_pressure": 0, "sell_pressure": 0, "net_signal": 0}

        # 归一化
        buy_pressure = weighted_buy / total_weight
        sell_pressure = weighted_sell / total_weight
        net_signal = (buy_pressure - sell_pressure) / max(buy_pressure + sell_pressure, 0.01)

        if net_signal > 0.2:
            final_signal = SignalType.BUY
        elif net_signal < -0.2:
            final_signal = SignalType.SELL
        else:
            final_signal = SignalType.HOLD

        return {
            "signal": final_signal,
            "confidence": min(weighted_confidence / total_weight, 1.0),
            "buy_pressure": round(buy_pressure, 4),
            "sell_pressure": round(sell_pressure, 4),
            "net_signal": round(net_signal, 4),
            "total_weight": round(total_weight, 4),
        }

    # ─── 信号生成 ─────────────────────────────────

    def _generate_mock_signal(self, strategy_id: str) -> StrategySignal:
        """模拟生成策略信号"""
        s = self.strategies[strategy_id]
        r = random.random()

        # 基于假设胜率生成信号
        if r < s.assumed_win_rate:
            if r < s.assumed_win_rate * 0.5:
                signal = SignalType.BUY
                confidence = 0.6 + random.random() * 0.4
            else:
                signal = SignalType.SELL
                confidence = 0.6 + random.random() * 0.4
        else:
            signal = SignalType.HOLD
            confidence = 0.3 + random.random() * 0.3

        return StrategySignal(
            strategy_id=strategy_id,
            strategy_name=s.name,
            signal=signal,
            confidence=confidence,
            timestamp=datetime.now().isoformat(),
            reason=f"{s.category.value}信号"
        )

    def get_all_signals(self, symbol: str = "BTCUSDT") -> List[StrategySignal]:
        """获取所有策略信号"""
        signals = []
        for sid in self.strategies:
            signal = self._generate_mock_signal(sid)
            signals.append(signal)
        return signals

    def get_signal_summary(self) -> Dict:
        """获取信号汇总"""
        signals = self.get_all_signals()
        buy_count = sum(1 for s in signals if s.signal == SignalType.BUY)
        sell_count = sum(1 for s in signals if s.signal == SignalType.SELL)
        hold_count = sum(1 for s in signals if s.signal == SignalType.HOLD)
        avg_conf = sum(s.confidence for s in signals) / len(signals) if signals else 0

        return {
            "total": len(signals),
            "buy": buy_count,
            "sell": sell_count,
            "hold": hold_count,
            "avg_confidence": round(avg_conf, 3),
            "dominant_signal": "BUY" if buy_count > sell_count else "SELL" if sell_count > buy_count else "HOLD",
            "signals": [
                {
                    "strategy_id": s.strategy_id,
                    "strategy_name": s.strategy_name,
                    "signal": s.signal.value,
                    "confidence": round(s.confidence, 3),
                    "weight": round(self.strategies[s.strategy_id].weight, 4),
                    "reason": s.reason,
                }
                for s in signals
            ]
        }

    # ─── 回测模块 ─────────────────────────────────

    def backtest(
        self,
        strategy_id: str,
        period_days: int = 90,
        initial_balance: float = 10000,
        trade_count: int = 50
    ) -> BacktestResult:
        """回测单个策略"""
        if strategy_id not in self.strategies:
            raise ValueError(f"Unknown strategy: {strategy_id}")

        s = self.strategies[strategy_id]

        # 模拟交易序列
        trades = []
        balance = initial_balance
        peak = balance
        max_dd = 0
        wins = 0
        losses = 0
        total_win = 0
        total_loss = 0
        consec_wins = 0
        consec_losses = 0
        max_consec_wins = 0
        max_consec_losses = 0

        for i in range(trade_count):
            # 胜率决定交易结果
            is_win = random.random() < s.assumed_win_rate
            # 盈亏比
            win_size = random.uniform(0.02, 0.10) * s.assumed_return * 10
            loss_size = random.uniform(0.01, 0.05)

            if is_win:
                pnl = balance * win_size
                balance += pnl
                wins += 1
                total_win += pnl
                consec_wins += 1
                consec_losses = 0
                max_consec_wins = max(max_consec_wins, consec_wins)
            else:
                pnl = -balance * loss_size
                balance += pnl
                losses += 1
                total_loss += abs(pnl)
                consec_losses += 1
                consec_wins = 0
                max_consec_losses = max(max_consec_losses, consec_losses)

            trades.append({"trade": i+1, "win": is_win, "pnl": pnl, "balance": balance})

            # 更新最大回撤
            peak = max(peak, balance)
            dd = (peak - balance) / peak
            max_dd = max(max_dd, dd)

        win_rate = wins / trade_count if trade_count > 0 else 0
        avg_win = total_win / wins if wins > 0 else 0
        avg_loss = total_loss / losses if losses > 0 else 0
        profit_factor = total_win / total_loss if total_loss > 0 else float('inf')
        sharpe = (balance/initial_balance - 1) / (max_dd + 0.01) if max_dd > 0 else 0

        return BacktestResult(
            strategy_id=strategy_id,
            total_trades=trade_count,
            win_trades=wins,
            lose_trades=losses,
            win_rate=round(win_rate, 4),
            total_return=round(balance - initial_balance, 2),
            max_drawdown=round(max_dd, 4),
            sharpe_ratio=round(sharpe, 2),
            profit_factor=round(profit_factor, 2) if profit_factor != float('inf') else 99.99,
            avg_win=round(avg_win, 2),
            avg_loss=round(avg_loss, 2),
            consecutive_wins=max_consec_wins,
            consecutive_losses=max_consec_losses,
            roi_annualized=round((balance/initial_balance - 1) * 365 / period_days, 4)
        )

    def backtest_all(self, period_days: int = 90, trade_count: int = 50) -> Dict:
        """回测所有策略"""
        results = {}
        for sid in self.strategies:
            if self.strategies[sid].enabled:
                results[sid] = self.backtest(sid, period_days, trade_count=trade_count)
        return results

    # ─── 仿真模块 ─────────────────────────────────

    def simulate(
        self,
        period_days: int = 30,
        initial_balance: float = 10000,
        fee_rate: float = 0.001
    ) -> SimulationResult:
        """
        仿真所有策略的加权组合
        """
        balance = initial_balance
        peak = balance
        max_dd = 0
        trades = []
        wins = 0
        losses = 0
        best_trade = 0
        worst_trade = 0

        # 按权重分配每日收益
        daily_returns = []
        for day in range(period_days):
            day_return = 0.0
            active_trades = 0

            for sid, s in self.strategies.items():
                if not s.enabled or s.weight == 0:
                    continue

                # 每日策略收益模拟
                if random.random() < s.assumed_win_rate:
                    # 赢
                    ret = s.weight * random.uniform(0.01, 0.05) * s.assumed_return * 5
                    day_return += ret
                    wins += 1
                    best_trade = max(best_trade, ret * balance)
                    active_trades += 1
                else:
                    # 输
                    ret = -s.weight * random.uniform(0.005, 0.02)
                    day_return += ret
                    losses += 1
                    worst_trade = min(worst_trade, ret * balance)
                    active_trades += 1

            # 扣除手续费
            if active_trades > 0:
                day_return -= fee_rate * active_trades

            daily_returns.append(day_return)
            balance *= (1 + day_return)

            # 更新最大回撤
            peak = max(peak, balance)
            dd = (peak - balance) / peak
            max_dd = max(max_dd, dd)

        total_return = balance - initial_balance
        return_pct = total_return / initial_balance

        # 计算夏普比率
        if daily_returns:
            mean_ret = sum(daily_returns) / len(daily_returns)
            variance = sum((r - mean_ret)**2 for r in daily_returns) / len(daily_returns)
            std_ret = math.sqrt(variance) if variance > 0 else 0.001
            sharpe = (mean_ret / std_ret) * math.sqrt(252) if std_ret > 0 else 0
        else:
            sharpe = 0

        return SimulationResult(
            strategy_id="portfolio",
            period_days=period_days,
            start_balance=initial_balance,
            end_balance=round(balance, 2),
            total_return=round(total_return, 2),
            return_pct=round(return_pct, 4),
            max_drawdown=round(max_dd, 4),
            sharpe_ratio=round(sharpe, 2),
            win_rate=round(wins / (wins + losses), 4) if (wins + losses) > 0 else 0,
            trade_count=wins + losses,
            best_trade=round(best_trade, 2),
            worst_trade=round(worst_trade, 2),
        )

    # ─── 决策等式输出 ──────────────────────────────

    def get_decision_equation(self) -> Dict:
        """
        获取决策等式
        Final = Σ(wi × Si × Ci) / Σ(wi × Ci)
        """
        weighted = self.get_weighted_signal()
        signals = self.get_signal_summary()

        # 详细等式
        equation_terms = []
        total_contrib = 0.0

        for sig in signals["signals"]:
            s = self.strategies[sig["strategy_id"]]
            contrib = s.weight * sig["confidence"]
            total_contrib += contrib
            if contrib > 0:
                equation_terms.append({
                    "strategy": sig["strategy_name"],
                    "weight": round(s.weight, 4),
                    "confidence": sig["confidence"],
                    "contribution": round(contrib, 6),
                    "signal": sig["signal"],
                })

        return {
            "decision": {
                "signal": weighted["signal"].value,
                "confidence": weighted["confidence"],
                "buy_pressure": weighted["buy_pressure"],
                "sell_pressure": weighted["sell_pressure"],
                "net_signal": weighted["net_signal"],
            },
            "equation": {
                "formula": "Final = Σ(wi × Si × Ci) / Σ(wi × Ci)",
                "terms": equation_terms,
                "total_contribution": round(total_contrib, 6),
                "normalized_by": round(weighted["total_weight"], 4),
            },
            "signal_summary": signals,
        }

    def get_strategy_params(self) -> List[Dict]:
        """获取所有策略参数"""
        result = []
        for sid, s in self.strategies.items():
            result.append({
                "id": sid,
                "name": s.name,
                "category": s.category.value,
                "description": s.description,
                "weight": round(s.weight, 4),
                "weight_default": round(s.weight_default, 4),
                "weight_range": [s.min_weight, s.max_weight],
                "enabled": s.enabled,
                "assumed_win_rate": s.assumed_win_rate,
                "assumed_return": s.assumed_return,
                "assumed_max_drawdown": s.assumed_max_drawdown,
                "assumed_sharpe": s.assumed_sharpe,
            })
        return result


# ─── 全局实例 ───────────────────────────────────────

_engine: Optional[QuantStrategiesEngine] = None

def get_quant_engine() -> QuantStrategiesEngine:
    global _engine
    if _engine is None:
        _engine = QuantStrategiesEngine()
    return _engine
