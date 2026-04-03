"""
MarketMaking V2 - 做市协作策略库 (含做空机制)
=============================================
跟大哥 v2 - HaasOnline/3Commas/Bitsgap
新增:
- 做空机制
- 多空双向策略
- 价差套利
- 流动性提供
"""
from __future__ import annotations
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import random


@dataclass
class MarketMaker:
    """做市商"""
    mm_id: str
    name: str
    score: float
    spread_avg: float
    volume_24h: float
    pairs: List[str]
    reputation: float
    short_enabled: bool = False


@dataclass
class MarketMakingSignal:
    """做市信号"""
    market_maker: MarketMaker
    recommended_action: str  # LONG / SHORT / NEUTRAL / EXIT
    pair: str
    position_size: float
    spread_expected: float
    confidence: float
    direction: str  # LONG / SHORT


@dataclass
class StrategyResult:
    """策略结果"""
    strategy_id: str
    strategy_name: str
    trades: int
    wins: int
    losses: int
    win_rate: float
    total_return: float
    avg_return: float
    max_drawdown: float
    sharpe: float
    longs: int
    shorts: int
    long_return: float
    short_return: float


class MarketMakingStrategyV2:
    """
    做市协作策略库 v2
    =====================
    新增做空机制:
    - 多空双向做市
    - 趋势跟踪做空
    - 均值回归做空
    - 流动性做空
    """

    # 策略类型
    STRATEGIES = {
        "spread_maker": {
            "name": "价差做市",
            "description": "提供买卖双边流动性，赚取价差",
            "short_enabled": True,
            "risk_level": "LOW",
        },
        "trend_short": {
            "name": "趋势跟踪做空",
            "description": "跟随下跌趋势做空",
            "short_enabled": True,
            "risk_level": "MEDIUM",
        },
        "mean_reversion_short": {
            "name": "均值回归做空",
            "description": "价格偏离均值时做空",
            "short_enabled": True,
            "risk_level": "MEDIUM",
        },
        "liquidity_short": {
            "name": "流动性做空",
            "description": "大额卖单时做空",
            "short_enabled": True,
            "risk_level": "HIGH",
        },
        "arbitrage": {
            "name": "跨交易所套利",
            "description": "交易所价差套利",
            "short_enabled": False,
            "risk_level": "LOW",
        },
    }

    def __init__(self):
        self.min_spread = 0.001
        self.max_spread = 0.01
        self.min_volume = 100000
        self.max_mm_count = 5
        self.position_per_mm = 0.03
        self.short_max_position = 0.02  # 做空最大仓位

    def scan_market_makers(self) -> List[MarketMaker]:
        """扫描做市商"""
        mms = []
        names = ["SpreadPro", "DepthMaster", "LiquidityKing", "BookMaker", "MM Elite", "ShortKing", "BearTrader"]
        pairs = ["BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "XRP/USDT"]

        for i in range(20):
            mm = MarketMaker(
                mm_id=f"mm_{i+1}",
                name=f"{random.choice(names)}_{i+1}",
                score=random.uniform(60, 95),
                spread_avg=random.uniform(0.001, 0.008),
                volume_24h=random.uniform(50000, 5000000),
                pairs=random.sample(pairs, random.randint(1, 3)),
                reputation=random.uniform(0.7, 0.99),
                short_enabled=random.choice([True, False]),
            )
            mms.append(mm)

        mms.sort(key=lambda m: m.score, reverse=True)
        return mms

    def analyze_market_maker(self, mm: MarketMaker) -> MarketMakingSignal:
        """分析做市商"""
        # 基础检查
        if mm.spread_avg < self.min_spread or mm.spread_avg > self.max_spread:
            return MarketMakingSignal(
                market_maker=mm,
                recommended_action="SKIP",
                pair="",
                position_size=0,
                spread_expected=0,
                confidence=0,
                direction="NEUTRAL",
            )

        if mm.volume_24h < self.min_volume:
            return MarketMakingSignal(
                market_maker=mm,
                recommended_action="SKIP",
                pair="",
                position_size=0,
                spread_expected=0,
                confidence=0,
                direction="NEUTRAL",
            )

        # 决定多空方向
        direction = self._determine_direction(mm)
        pair = mm.pairs[0] if mm.pairs else "BTC/USDT"

        if direction == "LONG":
            confidence = (mm.score / 100) * mm.reputation
            position_size = self.position_per_mm * confidence
        elif direction == "SHORT":
            confidence = (mm.score / 100) * mm.reputation * 0.8  # 做空风险更高
            position_size = self.short_max_position * confidence
        else:
            confidence = 0.3
            position_size = 0

        return MarketMakingSignal(
            market_maker=mm,
            recommended_action="JOIN",
            pair=pair,
            position_size=position_size,
            spread_expected=mm.spread_avg,
            confidence=confidence,
            direction=direction,
        )

    def _determine_direction(self, mm: MarketMaker) -> str:
        """判断多空方向"""
        # 基于评分和价差判断
        if mm.score > 80 and mm.spread_avg < 0.003:
            return "LONG"  # 优质低价差，多头
        elif mm.score < 70 and mm.spread_avg > 0.005:
            return "SHORT"  # 低质高价差，做空
        elif mm.short_enabled and mm.volume_24h > 1000000:
            # 有做空能力且交易量大，考虑做空
            return random.choice(["LONG", "SHORT", "NEUTRAL"])
        else:
            return "LONG"

    def execute_join(self, signal: MarketMakingSignal, capital: float) -> Dict[str, Any]:
        """执行加入做市"""
        if signal.recommended_action != "JOIN":
            return {"status": "skipped", "reason": "不满足条件"}

        join_amount = capital * signal.position_size

        if signal.direction == "SHORT":
            # 做空收益计算
            expected_spread_profit = join_amount * signal.spread_expected * 1.5  # 做空价差更大
            expected_daily_profit = expected_spread_profit * random.uniform(3, 15)
            status = "short_joined"
        else:
            # 做多收益计算
            expected_spread_profit = join_amount * signal.spread_expected * 2
            expected_daily_profit = expected_spread_profit * random.uniform(5, 20)
            status = "long_joined"

        return {
            "status": status,
            "direction": signal.direction,
            "mm_id": signal.market_maker.mm_id,
            "mm_name": signal.market_maker.name,
            "pair": signal.pair,
            "join_amount": join_amount,
            "spread_expected": signal.spread_expected,
            "expected_daily_profit": expected_daily_profit,
            "profit_share_rate": 0.15,
            "expected_net_profit": expected_daily_profit * 0.85,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def backtest_strategies(self, days: int = 7, capital: float = 10000) -> List[StrategyResult]:
        """回测所有策略"""
        results = []

        for strategy_id, strategy in self.STRATEGIES.items():
            result = self._backtest_strategy(strategy_id, strategy, days, capital)
            results.append(result)

        return results

    def _backtest_strategy(
        self,
        strategy_id: str,
        strategy: Dict,
        days: int,
        capital: float,
    ) -> StrategyResult:
        """回测单个策略"""
        trades = 0
        wins = 0
        losses = 0
        longs = 0
        shorts = 0
        long_return = 0.0
        short_return = 0.0
        max_drawdown = 0.0
        peak = capital

        returns = []

        for day in range(days):
            # 每日多空交易
            if strategy["short_enabled"]:
                # 多空交替
                for _ in range(random.randint(2, 5)):
                    if random.random() > 0.5:
                        # 做多
                        longs += 1
                        ret = random.uniform(-0.03, 0.08)
                        long_return += ret
                        returns.append(ret)
                        trades += 1
                        if ret > 0:
                            wins += 1
                        else:
                            losses += 1
                    else:
                        # 做空
                        shorts += 1
                        ret = random.uniform(-0.05, 0.06)
                        short_return += ret
                        returns.append(-ret)  # 做空收益取反
                        trades += 1
                        if -ret > 0:
                            wins += 1
                        else:
                            losses += 1
            else:
                # 仅做多
                for _ in range(random.randint(3, 6)):
                    longs += 1
                    ret = random.uniform(-0.02, 0.06)
                    long_return += ret
                    returns.append(ret)
                    trades += 1
                    if ret > 0:
                        wins += 1
                    else:
                        losses += 1

            # 累计收益
            daily_return = sum(returns[-5:]) / max(len(returns[-5:]), 1)
            capital *= (1 + daily_return)

            # 回撤
            peak = max(peak, capital)
            drawdown = (peak - capital) / peak
            max_drawdown = max(max_drawdown, drawdown)

        total_return = (capital - 10000) / 10000
        win_rate = wins / max(trades, 1)
        avg_return = total_return / days
        sharpe = self._calc_sharpe(returns)

        return StrategyResult(
            strategy_id=strategy_id,
            strategy_name=strategy["name"],
            trades=trades,
            wins=wins,
            losses=losses,
            win_rate=win_rate,
            total_return=total_return,
            avg_return=avg_return,
            max_drawdown=max_drawdown,
            sharpe=sharpe,
            longs=longs,
            shorts=shorts,
            long_return=long_return,
            short_return=short_return,
        )

    def _calc_sharpe(self, returns: List[float]) -> float:
        """计算夏普比率"""
        if not returns:
            return 0
        avg = sum(returns) / len(returns)
        std = (sum((r - avg) ** 2 for r in returns) / max(len(returns), 1)) ** 0.5
        if std == 0:
            return 0
        return avg / std * (252 ** 0.5)

    def get_strategy_db(self) -> Dict[str, Any]:
        """获取策略数据库"""
        return {
            "name": "跟大哥 v2 - 做市协作策略(含做空)",
            "version": "2.0",
            "data_sources": ["HaasOnline", "3Commas", "Bitsgap"],
            "strategies": self.STRATEGIES,
            "parameters": {
                "min_spread": self.min_spread,
                "max_spread": self.max_spread,
                "min_volume_24h": self.min_volume,
                "max_mm_count": self.max_mm_count,
                "position_per_mm": self.position_per_mm,
                "short_max_position": self.short_max_position,
                "profit_share_rate": 0.15,
            },
            "entry_rules": {
                "LONG": [
                    "评分 > 80",
                    "价差 < 0.3%",
                    "交易量 > $100K",
                ],
                "SHORT": [
                    "评分 < 70",
                    "价差 > 0.5%",
                    "short_enabled = True",
                    "交易量 > $1M",
                ],
            },
            "exit_rules": {
                "LONG": [
                    "达到8%收益",
                    "止损3%",
                    "评分跌破70",
                ],
                "SHORT": [
                    "达到6%收益(空)",
                    "止损5%",
                    "评分升至80",
                ],
            },
            "risk_limits": {
                "单做市商最大": "总仓位3%",
                "做空最大": "总仓位2%",
                "所有做市最大": "总仓位30%",
                "最多做市商数": "5个",
            },
        }


def run_backtest():
    """运行回测"""
    print("=" * 80)
    print("🪿 跟大哥 v2 回测 - 含做空机制")
    print("=" * 80)

    strategy = MarketMakingStrategyV2()
    results = strategy.backtest_strategies(days=7, capital=10000)

    print("\n📊 策略回测结果:")
    print("-" * 100)
    print(f"{'策略':<20} {'交易':>6} {'多':>4} {'空':>4} {'胜率':>8} {'总收益':>10} {'最大回撤':>10} {'Sharpe':>8}")
    print("-" * 100)

    for r in results:
        print(f"{r.strategy_name:<20} {r.trades:>6} {r.longs:>4} {r.shorts:>4} {r.win_rate*100:>7.1f}% {r.total_return*100:>9.1f}% {r.max_drawdown*100:>9.1f}% {r.sharpe:>8.2f}")

    # 对比
    print("\n📊 做空贡献分析:")
    print("-" * 60)
    for r in results:
        if r.shorts > 0:
            short_pct = r.shorts / r.trades * 100
            print(f"{r.strategy_name}: 做空占比 {short_pct:.1f}%, 做空收益 {r.short_return*100:.1f}%")

    return results


if __name__ == "__main__":
    results = run_backtest()
