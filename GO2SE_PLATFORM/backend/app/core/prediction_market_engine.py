"""
🔮 预测市场引擎
================
扩展走着瞧工具，覆盖更多预测市场

支持的预测市场:
- Polymarket (https://polymarket.com)
- 其他预测市场

功能:
- 多市场聚合
- 概率聚合
- 趋势预测
- 信号生成
"""

import json
import urllib.request
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class PredictionMarket(Enum):
    """预测市场枚举"""
    POLYMARKET = "polymarket"
    GAS_GUZZLERS = "gas_guzzlers"
    ICT_INDEX = "ict_index"
    OTHER = "other"


@dataclass
class Prediction:
    """预测结果"""
    question: str
    outcome: str
    probability: float  # 0.0 - 1.0
    market: str
    volume: float
    end_date: str
    created_at: str = field(default_factory=datetime.now().isoformat)


@dataclass
class AggregatedPrediction:
    """聚合预测"""
    question: str
    direction: str  # YES/NO
    confidence: float
    avg_probability: float
    probability_change: float
    markets: List[str]
    volume: float
    metadata: Dict = field(default_factory=dict)


class PredictionMarketEngine:
    """
    预测市场引擎
    ===========
    
    核心理念:
    1. 多市场聚合预测
    2. 概率加权平均
    3. 趋势检测
    4. 信号生成
    """
    
    def __init__(self):
        self.markets = {
            PredictionMarket.POLYMARKET: {
                "name": "Polymarket",
                "enabled": True,
                "api_url": "https://clob.polymarket.com/markets",
                "weight": 0.60  # 权重60%
            },
            PredictionMarket.GAS_GUZZLERS: {
                "name": "Gas Guzzlers",
                "enabled": True,
                "api_url": "https://clob.polymarket.com/markets?tag=gas",
                "weight": 0.20  # 权重20%
            },
            PredictionMarket.ICT_INDEX: {
                "name": "ICT Index",
                "enabled": True,
                "api_url": "https://clob.polymarket.com/markets?tag=ict",
                "weight": 0.20  # 权重20%
            }
        }
        
        # 趋势关键词
        self.trend_keywords = {
            "bullish": ["will", "above", "higher", "increase", "bull", "yes"],
            "bearish": ["will not", "below", "lower", "decrease", "bear", "no"]
        }
        
        # 缓存
        self.predictions_cache: List[Prediction] = []
        self.last_update: datetime = None
    
    def fetch_polymarket_markets(self) -> List[Dict]:
        """获取Polymarket市场"""
        # 模拟数据 - 实际应调用API
        mock_markets = [
            {
                "question": "BTC above $100000 by end of 2026?",
                "outcome": "Yes",
                "probability": 0.35,
                "volume": 2500000,
                "end_date": "2026-12-31"
            },
            {
                "question": "ETH above $10000 by end of 2026?",
                "outcome": "Yes",
                "probability": 0.25,
                "volume": 1800000,
                "end_date": "2026-12-31"
            },
            {
                "question": "SOL above $500 by end of 2026?",
                "outcome": "Yes",
                "probability": 0.40,
                "volume": 1200000,
                "end_date": "2026-12-31"
            },
            {
                "question": "BTC above $70000 by April 2026?",
                "outcome": "Yes",
                "probability": 0.65,
                "volume": 3500000,
                "end_date": "2026-04-30"
            },
            {
                "question": "ETH above $4000 by April 2026?",
                "outcome": "Yes",
                "probability": 0.55,
                "volume": 2100000,
                "end_date": "2026-04-30"
            },
            {
                "question": "Altcoin season index above 75?",
                "outcome": "Yes",
                "probability": 0.30,
                "volume": 800000,
                "end_date": "2026-06-30"
            },
            {
                "question": "Bitcoin volatility above 80?",
                "outcome": "Yes",
                "probability": 0.45,
                "volume": 950000,
                "end_date": "2026-03-31"
            },
            {
                "question": "DeFi TVL above $200B?",
                "outcome": "Yes",
                "probability": 0.35,
                "volume": 650000,
                "end_date": "2026-06-30"
            }
        ]
        
        return mock_markets
    
    def parse_prediction(self, market_data: Dict, market_name: str) -> Optional[Prediction]:
        """解析预测"""
        try:
            question = market_data.get("question", "")
            outcome = market_data.get("outcome", "")
            probability = market_data.get("probability", 0.5)
            volume = market_data.get("volume", 0)
            end_date = market_data.get("end_date", "")
            
            return Prediction(
                question=question,
                outcome=outcome,
                probability=probability,
                market=market_name,
                volume=volume,
                end_date=end_date
            )
        except Exception as e:
            logger.error(f"解析预测失败: {e}")
            return None
    
    def aggregate_predictions(self, predictions: List[Prediction]) -> List[AggregatedPrediction]:
        """聚合预测"""
        # 按问题分组
        question_groups: Dict[str, List[Prediction]] = {}
        
        for pred in predictions:
            # 简化：用关键词分组
            key = self._extract_keyword(pred.question)
            if key not in question_groups:
                question_groups[key] = []
            question_groups[key].append(pred)
        
        # 聚合
        results = []
        for question, preds in question_groups.items():
            if not preds:
                continue
            
            # 加权平均概率
            total_weight = 0
            weighted_prob = 0
            total_volume = 0
            
            for pred in preds:
                market_config = self.markets.get(PredictionMarket(pred.market), {})
                weight = market_config.get("weight", 0.2)
                
                weighted_prob += pred.probability * weight
                total_weight += weight
                total_volume += pred.volume
            
            avg_prob = weighted_prob / total_weight if total_weight > 0 else 0.5
            
            # 方向判断
            direction = "YES" if avg_prob > 0.5 else "NO"
            
            # 置信度
            confidence = abs(avg_prob - 0.5) * 2  # 0.5时最低，0或1时最高
            
            results.append(AggregatedPrediction(
                question=question,
                direction=direction,
                confidence=confidence,
                avg_probability=avg_prob,
                probability_change=0.0,  # 需要历史数据
                markets=[p.market for p in preds],
                volume=total_volume,
                metadata={
                    "predictions_count": len(preds),
                    "min_prob": min(p.probability for p in preds),
                    "max_prob": max(p.probability for p in preds)
                }
            ))
        
        return results
    
    def _extract_keyword(self, question: str) -> str:
        """提取关键词"""
        keywords = ["BTC", "ETH", "SOL", "Bitcoin", "Ethereum", "altcoin", "DeFi", "volatility"]
        for kw in keywords:
            if kw.lower() in question.lower():
                return kw
        return "OTHER"
    
    def generate_signal(self, aggregated: AggregatedPrediction) -> Dict:
        """生成交易信号"""
        if aggregated.confidence < 0.3:
            return {"action": "HOLD", "confidence": aggregated.confidence}
        
        # 判断方向
        if "YES" in aggregated.direction:
            if "BTC" in aggregated.question or "Bitcoin" in aggregated.question:
                action = "LONG"
            else:
                action = "LONG"
        else:
            action = "HOLD"  # 预测NO时不轻易做空
        
        return {
            "action": action,
            "confidence": aggregated.confidence,
            "probability": aggregated.avg_probability,
            "volume": aggregated.volume,
            "question": aggregated.question
        }
    
    def scan_all_markets(self) -> Dict:
        """扫描所有预测市场"""
        all_predictions = []
        
        # 获取各市场数据
        for market, config in self.markets.items():
            if not config["enabled"]:
                continue
            
            markets_data = self.fetch_polymarket_markets()
            for data in markets_data:
                pred = self.parse_prediction(data, market.value)
                if pred:
                    all_predictions.append(pred)
        
        # 聚合
        aggregated = self.aggregate_predictions(all_predictions)
        
        # 生成信号
        signals = []
        for agg in aggregated:
            signal = self.generate_signal(agg)
            if signal["action"] != "HOLD":
                signals.append(signal)
        
        return {
            "total_predictions": len(all_predictions),
            "aggregated_predictions": [
                {
                    "question": a.question,
                    "direction": a.direction,
                    "confidence": a.confidence,
                    "probability": a.avg_probability,
                    "markets": a.markets,
                    "volume": a.volume
                }
                for a in aggregated
            ],
            "signals": signals,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_market_status(self) -> Dict:
        """获取市场状态"""
        enabled_markets = [
            {"name": config["name"], "weight": config["weight"]}
            for market, config in self.markets.items()
            if config["enabled"]
        ]
        
        return {
            "total_markets": len(self.markets),
            "enabled_markets": len(enabled_markets),
            "markets": enabled_markets,
            "predictions_count": len(self.predictions_cache),
            "last_update": self.last_update.isoformat() if self.last_update else None
        }


# 全局实例
prediction_market_engine = PredictionMarketEngine()


if __name__ == "__main__":
    print("=" * 60)
    print("🔮 预测市场扫描")
    print("=" * 60)
    
    results = prediction_market_engine.scan_all_markets()
    
    print(f"\n📊 聚合预测 ({results['total_predictions']}条)")
    print("-" * 60)
    
    for pred in results["aggregated_predictions"]:
        prob = pred["probability"] * 100
        conf = pred["confidence"] * 100
        markets = ", ".join(pred["markets"])
        print(f"  {pred['question'][:40]}...")
        print(f"    概率: {prob:.1f}% | 置信度: {conf:.1f}% | 市场: {markets}")
    
    print()
    print(f"📈 信号 ({len(results['signals'])}条)")
    print("-" * 60)
    
    for sig in results["signals"]:
        print(f"  {sig['action']}: {sig['question'][:40]}... (置信度: {sig['confidence']*100:.1f}%)")
    
    print()
    print("💾 市场状态:", prediction_market_engine.get_market_status())
