"""
SignalOptimizer - 信号融合优化器
================================
统一信号融合算法，自动优化权重
"""
from __future__ import annotations
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import random


@dataclass
class SignalSource:
    """信号源"""
    name: str
    score: float
    confidence: float
    weight: float  # 动态权重
    history: List[float]  # 历史准确率


@dataclass
class OptimizedSignal:
    """优化后的信号"""
    final_score: float
    direction: str  # BUY/SELL/HOLD
    confidence: float
    source_weights: Dict[str, float]
    adjustments: List[str]


class SignalOptimizer:
    """
    信号融合优化器
    ===============
    1. 多源信号融合
    2. 动态权重调整
    3. 历史准确率反馈
    4. 异常信号过滤
    """

    # 默认权重
    DEFAULT_WEIGHTS = {
        "mirofish": 0.20,
        "sonar": 0.25,
        "oracle": 0.15,
        "sentiment": 0.18,
        "external_api": 0.12,
        "professional": 0.10,
    }

    # 异常阈值
    ANOMALY_THRESHOLD = 0.3  # 低于30%准确率的信号源视为异常

    def __init__(self):
        self.signals: Dict[str, SignalSource] = {}
        self.history: List[Dict] = []
        self.adjustment_count = 0

    def add_signal(
        self,
        name: str,
        score: float,
        confidence: float = 0.5,
        weight: Optional[float] = None,
    ) -> None:
        """添加信号源"""
        self.signals[name] = SignalSource(
            name=name,
            score=score,
            confidence=confidence,
            weight=weight or self.DEFAULT_WEIGHTS.get(name, 0.1),
            history=[],
        )

    def update_history(self, name: str, correct: bool) -> None:
        """更新历史准确率"""
        if name in self.signals:
            self.signals[name].history.append(1.0 if correct else 0.0)
            # 保留最近20条
            self.signals[name].history = self.signals[name].history[-20:]

    def get_accuracy(self, name: str) -> float:
        """获取信号源准确率"""
        if name not in self.signals or not self.signals[name].history:
            return 0.5  # 默认50%
        return sum(self.signals[name].history) / len(self.signals[name].history)

    def optimize_weights(self) -> Dict[str, float]:
        """优化信号权重"""
        adjustments = []

        for name, source in self.signals.items():
            accuracy = self.get_accuracy(name)

            # 异常检测
            if accuracy < self.ANOMALY_THRESHOLD:
                # 降低权重
                source.weight *= 0.5
                adjustments.append(f"{name}: 准确率{accuracy:.1%}低于阈值，降低权重×0.5")
            elif accuracy > 0.7:
                # 提高权重
                source.weight *= 1.2
                adjustments.append(f"{name}: 准确率{accuracy:.1%}优秀，提高权重×1.2")

            # 确保权重在合理范围
            source.weight = max(0.05, min(0.4, source.weight))

        # 归一化权重
        total = sum(s.weight for s in self.signals.values())
        for name in self.signals:
            self.signals[name].weight /= total

        self.adjustment_count += 1
        return {name: s.weight for name, s in self.signals.items()}, adjustments

    def fuse_signals(self) -> OptimizedSignal:
        """融合信号"""
        if not self.signals:
            return OptimizedSignal(
                final_score=0.5,
                direction="HOLD",
                confidence=0,
                source_weights={},
                adjustments=["无信号源"],
            )

        # 加权平均
        total_score = 0.0
        total_weight = 0.0

        for name, source in self.signals.items():
            # 考虑置信度的综合权重
            effective_weight = source.weight * source.confidence
            total_score += source.score * effective_weight
            total_weight += effective_weight

        final_score = total_score / total_weight if total_weight > 0 else 0.5

        # 方向判断
        if final_score > 0.65:
            direction = "BUY"
        elif final_score < 0.35:
            direction = "SELL"
        else:
            direction = "HOLD"

        # 置信度
        confidence = abs(final_score - 0.5) * 2  # 0-1范围

        return OptimizedSignal(
            final_score=final_score,
            direction=direction,
            confidence=confidence,
            source_weights={name: s.weight for name, s in self.signals.items()},
            adjustments=[],
        )

    def run_optimization_cycle(self) -> Dict[str, Any]:
        """运行完整优化周期"""
        # 1. 优化权重
        weights, adjustments = self.optimize_weights()

        # 2. 融合信号
        result = self.fuse_signals()
        result.adjustments = adjustments

        # 3. 记录历史
        self.history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "weights": weights,
            "final_score": result.final_score,
            "direction": result.direction,
            "confidence": result.confidence,
        })

        return {
            "weights": weights,
            "final_score": result.final_score,
            "direction": result.direction,
            "confidence": result.confidence,
            "adjustments": adjustments,
            "signals": {
                name: {
                    "score": s.score,
                    "confidence": s.confidence,
                    "weight": s.weight,
                    "accuracy": self.get_accuracy(name),
                }
                for name, s in self.signals.items()
            },
        }


def demo():
    """演示"""
    print("=" * 80)
    print("🪿 信号融合优化器演示")
    print("=" * 80)

    optimizer = SignalOptimizer()

    # 添加各工具信号
    signals = {
        "mirofish": (0.72, 0.85),
        "sonar": (0.68, 0.78),
        "oracle": (0.45, 0.55),  # 走着瞧 - 低分
        "sentiment": (0.70, 0.75),
        "external_api": (0.62, 0.65),
        "professional": (0.58, 0.60),
    }

    print("\n📊 原始信号:")
    for name, (score, conf) in signals.items():
        optimizer.add_signal(name, score, conf)
        print(f"   {name}: score={score:.2f}, confidence={conf:.2f}")

    # 运行优化
    result = optimizer.run_optimization_cycle()

    print("\n📊 优化后权重:")
    for name, weight in result["weights"].items():
        print(f"   {name}: {weight:.2%}")

    print(f"\n📊 融合结果:")
    print(f"   最终评分: {result['final_score']:.3f}")
    print(f"   方向: {result['direction']}")
    print(f"   置信度: {result['confidence']:.2%}")

    if result["adjustments"]:
        print(f"\n⚙️ 调整:")
        for adj in result["adjustments"]:
            print(f"   - {adj}")

    # 模拟历史准确率更新
    print("\n📊 模拟历史准确率反馈:")
    optimizer.update_history("oracle", True)
    optimizer.update_history("oracle", False)
    optimizer.update_history("oracle", True)

    result2 = optimizer.run_optimization_cycle()
    print(f"   走着瞧准确率: {optimizer.get_accuracy('oracle'):.1%}")
    print(f"   新权重: {result2['weights']['oracle']:.2%}")

    return result


if __name__ == "__main__":
    demo()
