"""
PredictionMarket V2 - 预测市场策略库 (修复版)
============================================
走着瞧 v2 - Polymarket/Coinrule/Superalgos

修复:
- 原来胜率0%的问题
- 信号生成逻辑优化
- 期望值计算改进
"""
from __future__ import annotations
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import random


@dataclass
class Prediction:
    """预测项"""
    question: str
    yes_price: float  # 0-1, 相当于YES的概率
    volume: float
    market: str
    resolution_date: str
    sentiment: float  # 市场情绪 0-1


@dataclass
class PredictionSignal:
    """预测信号"""
    prediction: Prediction
    recommended_action: str  # YES / NO / HOLD
    position_size: float
    confidence: float
    expected_value: float
    edge: float  # 优势 = 概率 - 入场价格
    risk: str  # LOW / MEDIUM / HIGH


@dataclass
class TradeResult:
    """交易结果"""
    action: str
    entry_price: float
    exit_price: float
    pnl_pct: float
    win: bool


class PredictionMarketStrategyV2:
    """
    预测市场策略库 v2
    =================
    修复版:
    1. 期望值计算修正
    2. 边缘过滤改进
    3. 仓位管理优化
    """

    # 六大预测市场
    MARKETS = {
        "polymarket": {"name": "Polymarket", "volume_share": 0.6},
        "kalshi": {"name": "Kalshi", "volume_share": 0.15},
        "manifold": {"name": "Manifold", "volume_share": 0.10},
        "omen": {"name": "Omen", "volume_share": 0.08},
        "gnosis": {"name": "Gnosis", "volume_share": 0.05},
        "augur": {"name": "Augur", "volume_share": 0.02},
    }

    def __init__(self):
        # 降低门槛
        self.min_edge = 0.10  # 最小优势 10%
        self.min_volume = 5000  # 最低成交量 $5000
        self.max_position = 0.12  # 最大仓位 12%
        self.stop_loss = 0.08  # 止损 8%

    def scan_markets(self) -> List[Prediction]:
        """扫描所有市场"""
        predictions = []
        for market_id, market in self.MARKETS.items():
            count = random.randint(3, 8)
            for _ in range(count):
                pred = self._generate_prediction(market_id, market["name"])
                predictions.append(pred)
        return predictions

    def _generate_prediction(self, market_id: str, market_name: str) -> Prediction:
        """生成预测"""
        questions = [
            "BTC将突破$100000?",
            "ETH将上涨20%?",
            "Solana将进入前5?",
            "将出现新DeFi Summer?",
            "机构将入场?",
            "监管将明朗?",
            "山寨季将开始?",
            "Defi TVL将翻倍?",
        ]

        # 模拟真实市场分布
        # 大部分预测在40-60%之间(不确定)
        base_prob = random.betavariate(2, 2)  # Beta分布，偏中间

        return Prediction(
            question=random.choice(questions),
            yes_price=base_prob,
            volume=random.uniform(5000, 200000),
            market=market_name,
            resolution_date=datetime.utcnow().isoformat(),
            sentiment=random.uniform(0.4, 0.6),
        )

    def analyze_prediction(self, prediction: Prediction) -> PredictionSignal:
        """分析预测"""
        yes_prob = prediction.yes_price

        # 边缘计算
        edge = yes_prob - 0.5  # 相对于50%的优势

        # 风险评估
        if abs(edge) > 0.25:
            risk = "LOW"
        elif abs(edge) > 0.15:
            risk = "MEDIUM"
        else:
            risk = "HIGH"

        # 期望值 = 概率 × 赔付 - 成本
        # 假设YES盈利为1, NO盈利为1, 正确率=概率
        expected_value = yes_prob * 0.9 - (1 - yes_prob) * 0.5

        # 动作决策
        if prediction.volume < self.min_volume:
            action = "HOLD"
            position_size = 0
        elif edge > self.min_edge:
            action = "YES"
            # 仓位 = 优势 × 信心 × 基础仓位
            position_size = min(edge * prediction.volume / 50000 * 0.1, self.max_position)
        elif edge < -self.min_edge:
            action = "NO"
            position_size = min(abs(edge) * 0.08, self.max_position)
        else:
            action = "HOLD"
            position_size = 0

        return PredictionSignal(
            prediction=prediction,
            recommended_action=action,
            position_size=position_size,
            confidence=prediction.sentiment,
            expected_value=expected_value,
            edge=edge,
            risk=risk,
        )

    def execute_trade(self, signal: PredictionSignal) -> TradeResult:
        """执行交易并返回结果"""
        if signal.recommended_action == "HOLD":
            return TradeResult(
                action="HOLD",
                entry_price=0,
                exit_price=0,
                pnl_pct=0,
                win=False,
            )

        entry = signal.prediction.yes_price if signal.recommended_action == "YES" else (1 - signal.prediction.yes_price)

        # 模拟实际价格变动
        actual_prob = signal.prediction.yes_price + random.uniform(-0.1, 0.1)
        actual_prob = max(0.05, min(0.95, actual_prob))

        if signal.recommended_action == "YES":
            exit = actual_prob
            pnl_pct = (exit - entry) / entry if entry > 0 else 0
            win = exit > entry
        else:
            # NO action
            exit = 1 - actual_prob
            pnl_pct = (exit - entry) / entry if entry > 0 else 0
            win = exit > entry

        return TradeResult(
            action=signal.recommended_action,
            entry_price=entry,
            exit_price=exit,
            pnl_pct=pnl_pct,
            win=win,
        )

    def backtest(self, trades: int = 100) -> Dict[str, Any]:
        """回测"""
        results = []
        wins = 0
        losses = 0

        for _ in range(trades):
            predictions = self.scan_markets()
            for pred in predictions[:5]:  # 每次取5个预测
                signal = self.analyze_prediction(pred)
                result = self.execute_trade(signal)
                results.append(result)

                if result.action != "HOLD":
                    if result.win:
                        wins += 1
                    else:
                        losses += 1

        total = wins + losses
        return {
            "total_trades": total,
            "wins": wins,
            "losses": losses,
            "win_rate": wins / total if total > 0 else 0,
            "avg_pnl": sum(r.pnl_pct for r in results) / len(results) if results else 0,
        }


def run_demo():
    """演示"""
    print("=" * 80)
    print("🪿 走着瞧 v2 回测")
    print("=" * 80)

    strategy = PredictionMarketStrategyV2()

    # 回测
    result = strategy.backtest(100)

    print(f"\n📊 回测结果 (100次交易):")
    print(f"   总交易: {result['total_trades']}")
    print(f"   盈利: {result['wins']}")
    print(f"   亏损: {result['losses']}")
    print(f"   胜率: {result['win_rate']*100:.1f}%")
    print(f"   平均收益: {result['avg_pnl']*100:.2f}%")

    # 扫描演示
    print(f"\n📡 市场扫描:")
    predictions = strategy.scan_markets()[:5]
    for i, pred in enumerate(predictions, 1):
        signal = strategy.analyze_prediction(pred)
        print(f"   {i}. {pred.question[:30]}...")
        print(f"      价格: {pred.yes_price:.2f}, 成交量: ${pred.volume:.0f}")
        print(f"      动作: {signal.recommended_action}, 仓位: {signal.position_size*100:.1f}%")
        print(f"      边缘: {signal.edge:.2f}, 期望值: {signal.expected_value:.3f}")
        print()


if __name__ == "__main__":
    run_demo()
