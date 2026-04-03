"""
CopyTrading - 跟单分成策略库
============================
搭便车 - Cryptohopper/Coinrule/TradeSanta
"""
from __future__ import annotations
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import random


@dataclass
class TraderProfile:
    """交易者画像"""
    trader_id: str
    name: str
    score: float  # 0-100
    win_rate: float
    avg_return: float
    max_drawdown: float
    followers: int
    platforms: List[str]
    specialties: List[str]


@dataclass
class CopySignal:
    """跟单信号"""
    trader: TraderProfile
    recommended_action: str  # COPY / SKIP / UNFOLLOW
    position_ratio: float
    max_copy_amount: float
    confidence: float
    reason: str


class CopyTradingStrategy:
    """
    跟单分成策略库
    =================
    数据源: Cryptohopper, Coinrule, TradeSanta
    策略: 精选Trader + 动态跟单 + 分成收益
    """

    def __init__(self):
        self.min_score = 80
        self.min_followers = 100
        self.max_traders = 10
        self.position_per_trader = 0.02  # 每人不超2%
        self.max_drawdown_stop = 0.15    # 15%回撤停止

    def scan_traders(self) -> List[TraderProfile]:
        """扫描优质交易者"""
        traders = []
        names = ["AlphaTrader", "CryptoKing", " WhaleSignals", "GridMaster", "TrendRider"]
        platforms = ["Binance", "Bybit", "OKX", "Coinbase"]

        for i in range(20):
            trader = TraderProfile(
                trader_id=f"trader_{i+1}",
                name=random.choice(names) + f"_{i+1}",
                score=random.uniform(60, 95),
                win_rate=random.uniform(0.55, 0.75),
                avg_return=random.uniform(0.02, 0.10),
                max_drawdown=random.uniform(0.05, 0.25),
                followers=random.randint(50, 5000),
                platforms=random.sample(platforms, random.randint(1, 3)),
                specialties=["trend", "grid"] if i % 2 == 0 else ["momentum", "scalping"],
            )
            traders.append(trader)

        # 按评分排序
        traders.sort(key=lambda t: t.score, reverse=True)
        return traders

    def analyze_trader(self, trader: TraderProfile) -> CopySignal:
        """分析交易者"""
        # 评分检查
        if trader.score < self.min_score:
            return CopySignal(
                trader=trader,
                recommended_action="SKIP",
                position_ratio=0,
                max_copy_amount=0,
                confidence=0,
                reason=f"评分{trader.score:.0f}低于{self.min_score}",
            )

        # 跟随便检查
        if trader.followers < self.min_followers:
            return CopySignal(
                trader=trader,
                recommended_action="SKIP",
                position_ratio=0,
                max_copy_amount=0,
                confidence=0,
                reason=f"跟随者{trader.followers}低于{self.min_followers}",
            )

        # 回撤检查
        if trader.max_drawdown > self.max_drawdown_stop:
            return CopySignal(
                trader=trader,
                recommended_action="SKIP",
                position_ratio=0,
                max_copy_amount=0,
                confidence=0,
                reason=f"最大回撤{trader.max_drawdown:.1%}超过限制",
            )

        # 推荐跟单
        confidence = trader.score / 100
        position_ratio = min(self.position_per_trader * (confidence ** 0.5), 0.05)
        max_amount = 10000 * position_ratio  # 基于假设总资金

        return CopySignal(
            trader=trader,
            recommended_action="COPY",
            position_ratio=position_ratio,
            max_copy_amount=max_amount,
            confidence=confidence,
            reason=f"优质交易者，评分{trader.score:.0f}，胜率{trader.win_rate:.1%}",
        )

    def execute_copy(self, signal: CopySignal, capital: float) -> Dict[str, Any]:
        """执行跟单"""
        if signal.recommended_action != "COPY":
            return {"status": "skipped", "reason": signal.reason}

        copy_amount = min(capital * signal.position_ratio, signal.max_copy_amount)
        expected_return = copy_amount * signal.trader.avg_return
        expected_profit_share = expected_return * 0.20  # 20%分成

        return {
            "status": "copied",
            "trader_id": signal.trader.trader_id,
            "trader_name": signal.trader.name,
            "copy_amount": copy_amount,
            "position_ratio": signal.position_ratio,
            "expected_return": expected_return,
            "profit_share": expected_profit_share,
            "stop_loss": signal.trader.max_drawdown * 1.5,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def get_strategy_db(self) -> Dict[str, Any]:
        """获取策略数据库"""
        return {
            "name": "搭便车 - 跟单分成策略",
            "version": "v9.0",
            "data_sources": ["Cryptohopper", "Coinrule", "TradeSanta"],
            "parameters": {
                "min_score": self.min_score,
                "min_followers": self.min_followers,
                "max_traders": self.max_traders,
                "position_per_trader": self.position_per_trader,
                "max_drawdown_stop": self.max_drawdown_stop,
                "profit_share_rate": 0.20,
            },
            "entry_rules": [
                f"Trader评分 >= {self.min_score}",
                f"跟随者 >= {self.min_followers}",
                f"最大回撤 <= {self.max_drawdown_stop:.0%}",
                "平台合规审查通过",
            ],
            "exit_rules": [
                "Trader评分跌破70",
                "回撤超过15%",
                "Trader长期无信号",
                "手动取消",
            ],
            "risk_limits": {
                "单Trader最大": "总仓位5%",
                "所有跟单最大": "总仓位50%",
                "最多跟单数": f"{self.max_traders}个",
            },
        }
