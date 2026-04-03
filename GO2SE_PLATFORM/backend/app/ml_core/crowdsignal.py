"""
CrowdSignal - 众包信号聚合
============================
聚合多来源市场信号: 社交媒体、KOL、社区、预测市场
加权评分、信号质量评估、实时排行
"""
import logging
import random
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class Signal:
    source: str
    content: str
    sentiment: float  # -1 to 1
    confidence: float  # 0 to 1
    timestamp: str
    engagement: int = 0


class CrowdSignal:
    """
    众包信号聚合
    =============
    功能:
    - 多源信号采集
    - 情感分析
    - 加权评分
    - 信号质量过滤
    - KOL影响力权重

    数据源:
    - Twitter/X
    - Telegram
    - Discord
    - 预测市场 (Polymarket)
    - News
    """

    def __init__(self):
        self.name = "CrowdSignal"
        self.sources = {
            "twitter": {"weight": 0.20, "reliability": 0.65},
            "telegram": {"weight": 0.15, "reliability": 0.60},
            "discord": {"weight": 0.10, "reliability": 0.55},
            "polymarket": {"weight": 0.25, "reliability": 0.78},
            "news": {"weight": 0.15, "reliability": 0.72},
            "onchain": {"weight": 0.15, "reliability": 0.70},
        }
        self.kols = {
            "CZ": {"influence": 0.95, "accuracy": 0.72},
            "Vitalik": {"influence": 0.92, "accuracy": 0.75},
            "SBF": {"influence": 0.85, "accuracy": 0.45},  # 准确率较低
            "Arthur": {"influence": 0.80, "accuracy": 0.68},
            "Josh": {"influence": 0.78, "accuracy": 0.71},
        }
        self.metrics = {"signals_processed": 0, "sources_queried": 0}

    def aggregate_signals(
        self,
        symbol: str,
        sources: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        聚合多源信号
        """
        sources = sources or list(self.sources.keys())
        self.metrics["sources_queried"] += len(sources)

        source_signals = {}
        for source in sources:
            source_signals[source] = self._fetch_source_signals(symbol, source)
            self.metrics["signals_processed"] += 1

        aggregated = self._weighted_aggregate(source_signals)
        sentiment_score = aggregated["weighted_sentiment"]
        confidence = aggregated["confidence"]

        trend_signal = "BULLISH" if sentiment_score > 0.2 else "BEARISH" if sentiment_score < -0.2 else "NEUTRAL"

        return {
            "symbol": symbol,
            "aggregated_sentiment": round(sentiment_score, 3),
            "confidence": round(confidence, 3),
            "trend_signal": trend_signal,
            "sources": source_signals,
            "top_signals": self._get_top_signals(source_signals),
            "kol_consensus": self._kol_consensus(symbol),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _fetch_source_signals(self, symbol: str, source: str) -> Dict[str, Any]:
        """模拟从各来源获取信号"""
        sentiment = random.uniform(-0.5, 0.6)
        engagement = random.randint(100, 10000) if source in ["twitter", "telegram"] else random.randint(50, 1000)

        return {
            "source": source,
            "sentiment": round(sentiment, 3),
            "confidence": round(self.sources.get(source, {}).get("reliability", 0.6), 3),
            "weight": self.sources.get(source, {}).get("weight", 0.1),
            "signals": [
                {"text": f"{symbol} showing {'bullish' if sentiment > 0 else 'bearish'} signals", "sentiment": sentiment, "engagement": engagement},
            ],
            "volume": random.randint(50, 500),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _weighted_aggregate(self, source_signals: Dict[str, Dict]) -> Dict[str, Any]:
        """加权聚合信号"""
        total_weight = 0.0
        weighted_sentiment = 0.0
        weighted_confidence = 0.0

        for source, data in source_signals.items():
            weight = data["weight"]
            total_weight += weight
            weighted_sentiment += data["sentiment"] * weight
            weighted_confidence += data["confidence"] * weight * data["sentiment"] if data["sentiment"] > 0 else 0

        if total_weight > 0:
            weighted_sentiment /= total_weight
            weighted_confidence /= total_weight

        return {
            "weighted_sentiment": weighted_sentiment,
            "confidence": weighted_confidence,
        }

    def _get_top_signals(self, source_signals: Dict[str, Dict]) -> List[Dict]:
        """获取最强烈的信号"""
        all_signals = []
        for source, data in source_signals.items():
            for signal in data.get("signals", []):
                score = abs(signal["sentiment"]) * data["weight"] * signal["engagement"]
                all_signals.append({
                    "source": source,
                    "text": signal["text"],
                    "sentiment": signal["sentiment"],
                    "score": round(score, 3),
                })
        return sorted(all_signals, key=lambda x: x["score"], reverse=True)[:5]

    def _kol_consensus(self, symbol: str) -> Dict[str, Any]:
        """KOL共识分析"""
        kol_votes = []
        for kol, info in self.kols.items():
            sentiment = random.uniform(-0.3, 0.5) * info["accuracy"]
            weighted_sentiment = sentiment * info["influence"]
            kol_votes.append({
                "kol": kol,
                "influence": info["influence"],
                "sentiment": round(weighted_sentiment, 3),
                "reliability_score": round(info["influence"] * info["accuracy"], 3),
            })

        bullish_count = sum(1 for v in kol_votes if v["sentiment"] > 0.1)
        bearish_count = sum(1 for v in kol_votes if v["sentiment"] < -0.1)

        return {
            "votes": sorted(kol_votes, key=lambda x: x["reliability_score"], reverse=True),
            "consensus": "BULLISH" if bullish_count > bearish_count else "BEARISH" if bearish_count > bullish_count else "SPLIT",
            "agreement_pct": round(max(bullish_count, bearish_count) / len(kol_votes) * 100, 1),
            "avg_sentiment": round(sum(v["sentiment"] for v in kol_votes) / len(kol_votes), 3),
        }

    def get_polymarket_signals(self, question: str) -> Dict[str, Any]:
        """预测市场信号"""
        return {
            "question": question,
            "yes_price": round(random.uniform(0.40, 0.85), 3),
            "no_price": round(random.uniform(0.15, 0.60), 3),
            "volume_24h": random.randint(10000, 500000),
            "sentiment": round(random.uniform(-0.3, 0.5), 3),
            "confidence": round(random.uniform(0.5, 0.8), 3),
            "recommendation": "YES" if random.random() > 0.5 else "NO",
            "source": "Polymarket",
        }

    def sentiment_timeline(
        self,
        symbol: str,
        hours: int = 24,
    ) -> Dict[str, Any]:
        """情感时间线"""
        now = datetime.utcnow()
        points = []
        for i in range(hours):
            t = now - timedelta(hours=hours - i - 1)
            sentiment = random.uniform(-0.4, 0.5) + (0.1 if i > hours // 2 else -0.1)
            points.append({
                "timestamp": t.isoformat(),
                "sentiment": round(sentiment, 3),
                "volume": random.randint(100, 5000),
            })

        return {
            "symbol": symbol,
            "hours": hours,
            "timeline": points,
            "trend": "IMPROVING" if points[-1]["sentiment"] > points[0]["sentiment"] else "DETERIORATING",
            "avg_sentiment": round(sum(p["sentiment"] for p in points) / len(points), 3),
        }
