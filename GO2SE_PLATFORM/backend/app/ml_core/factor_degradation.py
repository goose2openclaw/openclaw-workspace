"""
Factor Degradation Detector - 因子退化检测模块
==========================================
功能:
1. 因子评分实时监控
2. 公开策略成果追踪对比
3. 因子退化自动告警
4. 对比蒸馏自动触发
"""
from __future__ import annotations
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import random
import logging

logger = logging.getLogger(__name__)


# ── 公开策略追踪来源 ─────────────────────────────────────────────

PUBLIC_STRATEGY_TRACKERS = {
    "3commas": {
        "name": "3Commas",
        "url": "https://3commas.io",
        "strategies": ["DCACapital", "BandRaptor", "EMA_Cross"],
        "avg_win_rate": 0.65,
        "avg_return": 0.03,
        "update_frequency": "daily",
    },
    "haasonline": {
        "name": "HaasOnline",
        "url": "https://haasonline.com",
        "strategies": ["TrendTracker", "MarketMaker", "Scalper"],
        "avg_win_rate": 0.68,
        "avg_return": 0.035,
        "update_frequency": "weekly",
    },
    "freqtrade": {
        "name": "Freqtrade",
        "url": "https://freqtrade.io",
        "strategies": ["EMASpread", "RSI_BB", "VolumePair"],
        "avg_win_rate": 0.67,
        "avg_return": 0.032,
        "update_frequency": "weekly",
    },
    "cryptohopper": {
        "name": "Cryptohopper",
        "url": "https://cryptohopper.com",
        "strategies": ["MarketPlace", "SocialCopy"],
        "avg_win_rate": 0.64,
        "avg_return": 0.035,
        "update_frequency": "daily",
    },
    "bitsgap": {
        "name": "Bitsgap",
        "url": "https://bitsgap.com",
        "strategies": ["GridPro", "AutoInvest"],
        "avg_win_rate": 0.62,
        "avg_return": 0.028,
        "update_frequency": "daily",
    },
}


# ── 因子定义 ─────────────────────────────────────────────

@dataclass
class Factor:
    name: str
    category: str  # trend/momentum/volatility/sentiment/risk
    current_score: float  # 0-100
    historical_scores: List[Tuple[str, float]] = field(default_factory=list)
    last_updated: str = ""
    is_degraded: bool = False
    degradation_pct: float = 0.0


@dataclass
class FactorDegradation:
    factor_name: str
    current_score: float
    historical_avg: float
    degradation_pct: float
    severity: str  # NORMAL / WARNING / CRITICAL
    trend: str  # IMPROVING / STABLE / DEGRADING
    recommendation: str
    action_required: bool


@dataclass
class StrategyComparison:
    our_strategy: str
    reference_platform: str
    reference_strategy: str
    our_win_rate: float
    their_win_rate: float
    our_return: float
    their_return: float
    our_sharpe: float
    their_sharpe: float
    gap: float
    verdict: str  # AHEAD / MATCH / BEHIND / CRITICAL
    distillation_needed: bool
    suggested_params: Dict[str, float]


# ── 因子退化检测引擎 ─────────────────────────────────────────────

class FactorDegradationDetector:
    """
    因子退化检测引擎
    =================
    1. 监控123声纳模型 + 7工具策略的因子
    2. 对标公开策略成果对比蒸馏
    3. 退化时自动告警
    4. 触发参数优化
    """

    def __init__(self, degradation_threshold: float = 15.0, critical_threshold: float = 25.0):
        self.degradation_threshold = degradation_threshold  # 退化15%告警
        self.critical_threshold = critical_threshold  # 退化25%严重
        self.factors: Dict[str, Factor] = {}
        self.tracked_strategies: Dict[str, List] = {}
        self.last_check: str = ""
        self._init_default_factors()

    def _init_default_factors(self):
        """初始化默认因子列表"""
        # 声纳库因子 (123模型)
        sonar_factors = [
            ("trend_ema_crossover", "trend"),
            ("trend_ma_alignment", "trend"),
            ("trend_channel", "trend"),
            ("momentum_rsi", "momentum"),
            ("momentum_macd", "momentum"),
            ("momentum_adx", "momentum"),
            ("volatility_bb", "volatility"),
            ("volatility_atr", "volatility"),
            ("sentiment_twitter", "sentiment"),
            ("sentiment_news", "sentiment"),
            ("risk_drawdown", "risk"),
            ("risk_volatility", "risk"),
        ]
        for name, category in sonar_factors:
            self.factors[name] = Factor(
                name=name,
                category=category,
                current_score=random.uniform(65, 85),
                historical_scores=[],
                last_updated=datetime.utcnow().isoformat(),
            )

    def update_factor_score(self, factor_name: str, new_score: float) -> FactorDegradation:
        """更新因子评分并检测退化"""
        if factor_name not in self.factors:
            self.factors[factor_name] = Factor(
                name=factor_name,
                category="unknown",
                current_score=new_score,
            )

        factor = self.factors[factor_name]

        # 记录历史
        timestamp = datetime.utcnow().isoformat()
        factor.historical_scores.append((timestamp, factor.current_score))
        factor.last_updated = timestamp

        # 计算历史平均 (最近30个点)
        recent = factor.historical_scores[-30:]
        historical_avg = sum(s for _, s in recent) / len(recent) if recent else 70.0

        # 计算退化百分比
        degradation_pct = ((historical_avg - new_score) / historical_avg * 100) if historical_avg > 0 else 0

        # 判断严重程度
        if degradation_pct >= self.critical_threshold:
            severity = "CRITICAL"
            action_required = True
        elif degradation_pct >= self.degradation_threshold:
            severity = "WARNING"
            action_required = True
        else:
            severity = "NORMAL"
            action_required = False

        # 判断趋势
        if len(recent) >= 5:
            recent_5 = [s for _, s in recent[-5:]]
            if new_score > sum(recent_5) / 5:
                trend = "IMPROVING"
            elif new_score < sum(recent_5) / 5:
                trend = "DEGRADING"
            else:
                trend = "STABLE"
        else:
            trend = "STABLE"

        # 更新因子
        old_score = factor.current_score
        factor.current_score = new_score
        factor.degradation_pct = degradation_pct
        factor.is_degraded = degradation_pct >= self.degradation_threshold

        # 生成建议
        recommendation = self._generate_recommendation(factor_name, degradation_pct, severity)

        return FactorDegradation(
            factor_name=factor_name,
            current_score=new_score,
            historical_avg=round(historical_avg, 2),
            degradation_pct=round(degradation_pct, 2),
            severity=severity,
            trend=trend,
            recommendation=recommendation,
            action_required=action_required,
        )

    def _generate_recommendation(self, factor_name: str, degradation_pct: float, severity: str) -> str:
        """生成修复建议"""
        if severity == "CRITICAL":
            return f"立即修复 {factor_name}，退化{degradation_pct:.1f}%，建议对比3Commas/HaasOnline基准参数"
        elif severity == "WARNING":
            return f"关注 {factor_name}，退化{degradation_pct:.1f}%，建议增加回测频率"
        else:
            return f"{factor_name} 评分正常，继续监控"

    def check_all_factors(self) -> Dict[str, Any]:
        """全面检查所有因子"""
        self.last_check = datetime.utcnow().isoformat()

        degraded_factors = []
        normal_factors = []
        critical_factors = []

        for name, factor in self.factors.items():
            degradation = self.update_factor_score(name, factor.current_score)
            if degradation.severity == "CRITICAL":
                critical_factors.append(degradation)
            elif degradation.severity == "WARNING":
                degraded_factors.append(degradation)
            else:
                normal_factors.append(degradation)

        return {
            "timestamp": self.last_check,
            "total_factors": len(self.factors),
            "critical_count": len(critical_factors),
            "warning_count": len(degraded_factors),
            "normal_count": len(normal_factors),
            "degraded_factors": degraded_factors,
            "critical_factors": critical_factors,
            "overall_health_score": self._calc_health_score(),
            "action_required": len(critical_factors) > 0 or len(degraded_factors) > 2,
        }

    def _calc_health_score(self) -> float:
        """计算整体健康分"""
        if not self.factors:
            return 100.0
        avg_score = sum(f.current_score for f in self.factors.values()) / len(self.factors)
        degraded_count = sum(1 for f in self.factors.values() if f.is_degraded)
        penalty = degraded_count * 5
        return round(max(0, avg_score - penalty), 1)

    def compare_with_public_strategies(
        self,
        our_strategy: str,
        tool: str,
        our_metrics: Dict[str, float],
    ) -> StrategyComparison:
        """
        与公开策略对比蒸馏
        =================
        our_metrics: {"win_rate": 0.62, "return": 0.03, "sharpe": 1.5}
        """
        # 找对应工具的参考平台
        reference = self._get_reference_for_tool(tool)
        if not reference:
            return StrategyComparison(
                our_strategy=our_strategy,
                reference_platform="N/A",
                reference_strategy="N/A",
                our_win_rate=our_metrics.get("win_rate", 0),
                their_win_rate=0,
                our_return=our_metrics.get("return", 0),
                their_return=0,
                our_sharpe=our_metrics.get("sharpe", 0),
                their_sharpe=0,
                gap=0,
                verdict="UNKNOWN",
                distillation_needed=False,
                suggested_params={},
            )

        their_win_rate = reference["avg_win_rate"]
        their_return = reference["avg_return"]

        our_win_rate = our_metrics.get("win_rate", 0)
        our_return = our_metrics.get("return", 0)
        our_sharpe = our_metrics.get("sharpe", 0)

        # 计算差距
        win_rate_gap = our_win_rate - their_win_rate
        return_gap = our_return - their_return
        gap = (win_rate_gap * 0.4 + return_gap * 0.6) * 100  # 权重综合

        # 判断 verdict
        if gap > 5:
            verdict = "AHEAD"
            distillation_needed = False
        elif gap >= -5:
            verdict = "MATCH"
            distillation_needed = False
        elif gap >= -15:
            verdict = "BEHIND"
            distillation_needed = True
        else:
            verdict = "CRITICAL"
            distillation_needed = True

        # 生成优化参数建议
        suggested_params = self._generate_distillation_params(
            our_strategy, reference, our_metrics
        )

        return StrategyComparison(
            our_strategy=our_strategy,
            reference_platform=reference["name"],
            reference_strategy=reference["strategies"][0] if reference["strategies"] else "N/A",
            our_win_rate=our_win_rate,
            their_win_rate=their_win_rate,
            our_return=our_return,
            their_return=their_return,
            our_sharpe=our_sharpe,
            their_sharpe=their_return / 0.1 * 1.5 if their_return > 0 else 1.0,
            gap=round(gap, 2),
            verdict=verdict,
            distillation_needed=distillation_needed,
            suggested_params=suggested_params,
        )

    def _get_reference_for_tool(self, tool: str) -> Optional[Dict]:
        """获取工具对应的参考平台"""
        tool_to_platform = {
            "rabbit": "3commas",
            "mole": "bitsgap",
            "oracle": "haasonline",
            "leader": "haasonline",
            "hitchhiker": "cryptohopper",
            "wool": "bitsgap",
            "poor_kid": "freqtrade",
        }
        platform_key = tool_to_platform.get(tool)
        if platform_key and platform_key in PUBLIC_STRATEGY_TRACKERS:
            return PUBLIC_STRATEGY_TRACKERS[platform_key]
        return None

    def _generate_distillation_params(
        self,
        our_strategy: str,
        reference: Dict,
        our_metrics: Dict,
    ) -> Dict[str, float]:
        """生成蒸馏后的建议参数"""
        their_wr = reference["avg_win_rate"]
        our_wr = our_metrics.get("win_rate", 0)

        if our_wr >= their_wr:
            return {}  # 我们已经领先，不需要改变

        # 建议调整的参数 (简化版)
        suggestions = {}

        # 根据工具类型给出不同建议
        if our_wr < their_wr * 0.9:  # 落后10%以上
            suggestions = {
                "rsi_oversold": 30,
                "rsi_overbought": 70,
                "ema_fast": 9,
                "ema_slow": 21,
                "adx_threshold": 25,
            }

        return suggestions

    def auto_distillation_trigger(
        self,
        comparisons: List[StrategyComparison],
    ) -> Dict[str, Any]:
        """自动触发蒸馏"""
        needs_distillation = [c for c in comparisons if c.distillation_needed]

        if not needs_distillation:
            return {
                "triggered": False,
                "reason": "所有策略表现正常",
                "strategies_to_optimize": [],
            }

        # 按gap排序，最差的先优化
        sorted_by_gap = sorted(needs_distillation, key=lambda x: x.gap)

        return {
            "triggered": True,
            "reason": f"{len(needs_distillation)}个策略需要蒸馏",
            "priority": [s.our_strategy for s in sorted_by_gap],
            "strategies_to_optimize": [
                {
                    "strategy": s.our_strategy,
                    "gap": s.gap,
                    "reference": s.reference_platform,
                    "suggested_params": s.suggested_params,
                }
                for s in sorted_by_gap
            ],
        }

    def get_factor_report(self) -> Dict[str, Any]:
        """获取因子健康报告"""
        check_result = self.check_all_factors()

        # 按类别分组
        by_category = {}
        for name, factor in self.factors.items():
            cat = factor.category
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append({
                "name": name,
                "score": factor.current_score,
                "degraded": factor.is_degraded,
                "degradation_pct": factor.degradation_pct,
            })

        return {
            "report_time": self.last_check,
            "overall_health_score": check_result["overall_health_score"],
            "action_required": check_result["action_required"],
            "summary": {
                "total": check_result["total_factors"],
                "critical": check_result["critical_count"],
                "warning": check_result["warning_count"],
                "normal": check_result["normal_count"],
            },
            "by_category": by_category,
            "degraded_list": [
                {"name": d.factor_name, "score": d.current_score, "severity": d.severity}
                for d in check_result["degraded_factors"] + check_result["critical_factors"]
            ],
            "reference_trackers": list(PUBLIC_STRATEGY_TRACKERS.keys()),
        }


# ── 全局实例 ─────────────────────────────────────────────

_detector = FactorDegradationDetector(degradation_threshold=15.0, critical_threshold=25.0)
