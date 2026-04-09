#!/usr/bin/env python3
"""
🪿 GO2SE 策略蒸馏模块 V1
========================
将平台策略与原出处/类似平台进行逐一比较蒸馏

功能:
1. 对比原版策略参数
2. 推导最优参数
3. 迭代更新数据库和脚本
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger("strategy_distiller")

@dataclass
class StrategyReference:
    """策略参考源"""
    platform: str
    url: str
    author: str
    description: str
    key_params: Dict  # 关键参数
    expected_return: float
    sharpe_ratio: float

@dataclass
class ParameterComparison:
    """参数对比"""
    param_name: str
    our_value: float
    reference_value: float
    diff_percent: float  # 差异百分比
    verdict: str  # "optimal", "needs_tuning", "reference_better", "our_better"

@dataclass
class DistillationResult:
    """蒸馏结果"""
    strategy_id: str
    strategy_name: str
    our_score: float
    reference_score: float
    params: List[ParameterComparison]
    optimal_params: Dict
    improvement: float  # 预期改进百分比
    confidence: float  # 置信度
    recommendations: List[str]
    sources_compared: int

class StrategyDistiller:
    """
    策略蒸馏器
    
    对比策略:
    1. 原版策略 (FreqTrade, TradingView, etc.)
    2. 类似平台 (3Commas, HaasOnline, etc.)
    3. 学术论文
    """
    
    def __init__(self):
        # 策略参考源
        self.strategy_references = {
            "oversold_rebound": StrategyReference(
                platform="FreqTrade",
                url="https://github.com/freqtrade/freqtrade-strategies",
                author="FreqTrade Community",
                description="RSI超卖反弹策略",
                key_params={
                    "rsi_oversold": (20, 35),
                    "rsi_overbought": (65, 75),
                    "stop_loss": (0.02, 0.05),
                    "take_profit": (0.03, 0.10),
                },
                expected_return=0.02,
                sharpe_ratio=1.2,
            ),
            "rsi_macd": StrategyReference(
                platform="TradingView",
                url="https://www.tradingview.com/script/",
                author="TradingView Community",
                description="RSI+MACD组合策略",
                key_params={
                    "rsi_period": 14,
                    "macd_fast": 12,
                    "macd_slow": 26,
                    "macd_signal": 9,
                },
                expected_return=0.015,
                sharpe_ratio=1.0,
            ),
            "bollinger_bands": StrategyReference(
                platform="3Commas",
                url="https://3commas.io/",
                author="3Commas Community",
                description="布林带均值回归策略",
                key_params={
                    "bb_period": 20,
                    "bb_std": 2.0,
                    "rsi_entry": 30,
                },
                expected_return=0.018,
                sharpe_ratio=1.1,
            ),
            "grid_trading": StrategyReference(
                platform="Binance",
                url="https://www.binance.com/en/support/articles/",
                author="Binance Academy",
                description="网格交易策略",
                key_params={
                    "grid_count": 10,
                    "grid_spacing": 1.0,
                    "investment_ratio": 0.5,
                },
                expected_return=0.025,
                sharpe_ratio=1.3,
            ),
            "dollar_cost_avg": StrategyReference(
                platform="Generic",
                url="https://en.wikipedia.org/wiki/Dollar_cost_averaging",
                author="Financial Research",
                description="定投策略",
                key_params={
                    "interval_hours": 168,
                    "investment_amount": 100,
                },
                expected_return=0.012,
                sharpe_ratio=0.9,
            ),
        }
        
        # 当前平台的策略参数
        self.our_strategies = {
            "oversold_rebound_v3_prime": {
                "name": "超卖反弹v3",
                "rsi_oversold": 20,
                "rsi_overbought": 65,
                "stop_loss": 0.03,
                "take_profit": 0.10,
                "position_size": 0.15,
                "backtest_return": 0.0223,
                "backtest_winrate": 0.50,
            },
            "rsi_macd_v2": {
                "name": "RSI+MACD v2",
                "rsi_period": 14,
                "macd_fast": 12,
                "macd_slow": 26,
                "macd_signal": 9,
                "backtest_return": 0.015,
                "backtest_winrate": 0.48,
            },
            "bollinger_v1": {
                "name": "布林带v1",
                "bb_period": 20,
                "bb_std": 2.0,
                "rsi_entry": 35,
                "backtest_return": 0.018,
                "backtest_winrate": 0.52,
            },
            "grid_v2": {
                "name": "网格v2",
                "grid_count": 15,
                "grid_spacing": 0.8,
                "investment_ratio": 0.4,
                "backtest_return": 0.028,
                "backtest_winrate": 0.55,
            },
            "dca_v3": {
                "name": "定投v3",
                "interval_hours": 168,
                "investment_amount": 100,
                "backtest_return": 0.014,
                "backtest_winrate": 0.60,
            },
        }
    
    def compare_parameters(
        self, 
        our_strategy: Dict, 
        reference: StrategyReference
    ) -> List[ParameterComparison]:
        """
        对比单个参数
        """
        comparisons = []
        
        for param_name, (ref_min, ref_max) in reference.key_params.items():
            if param_name in our_strategy:
                our_value = our_strategy[param_name]
                ref_value = (ref_min + ref_max) / 2  # 取中间值
                ref_range = ref_max - ref_min
                
                if ref_range > 0:
                    diff_pct = abs(our_value - ref_value) / ref_range * 100
                else:
                    diff_pct = 0
                
                # 判断最优
                if diff_pct < 10:
                    verdict = "optimal"
                elif our_value < ref_min or our_value > ref_max:
                    verdict = "needs_tuning"
                    if our_value < ref_min:
                        verdict = "our_better" if our_value > ref_min * 0.8 else "reference_better"
                    else:
                        verdict = "our_better" if our_value < ref_max * 1.2 else "reference_better"
                else:
                    verdict = "our_better" if our_value < ref_value else "reference_better"
                
                comparisons.append(ParameterComparison(
                    param_name=param_name,
                    our_value=our_value,
                    reference_value=ref_value,
                    diff_percent=diff_pct,
                    verdict=verdict,
                ))
        
        return comparisons
    
    def distill_strategy(self, strategy_id: str) -> Optional[DistillationResult]:
        """
        蒸馏单个策略
        """
        if strategy_id not in self.our_strategies:
            logger.warning(f"策略 {strategy_id} 不在已知列表中")
            return None
        
        our_strategy = self.our_strategies[strategy_id]
        
        # 找到对应的参考源 (改进的映射)
        strategy_prefix = strategy_id.split('_')[0].lower()
        
        # 映射策略前缀到参考key
        prefix_mapping = {
            "oversold": "oversold_rebound",
            "rsi": "rsi_macd",
            "bollinger": "bollinger_bands",
            "grid": "grid_trading",
            "dollar": "dollar_cost_avg",
            "dca": "dollar_cost_avg",
        }
        
        ref_key = prefix_mapping.get(strategy_prefix)
        if not ref_key or ref_key not in self.strategy_references:
            # 尝试模糊匹配
            for key in self.strategy_references:
                if strategy_prefix in key or key in strategy_prefix:
                    ref_key = key
                    break
            else:
                ref_key = "oversold_rebound"  # 默认
        
        reference = self.strategy_references[ref_key]
        
        # 确保key_params的值都是元组
        normalized_key_params = {}
        for k, v in reference.key_params.items():
            if isinstance(v, (int, float)):
                normalized_key_params[k] = (v * 0.9, v * 1.1)  # 假设±10%范围
            else:
                normalized_key_params[k] = v
        reference.key_params = normalized_key_params
        
        # 对比参数
        comparisons = self.compare_parameters(our_strategy, reference)
        
        # 计算评分
        optimal_count = sum(1 for c in comparisons if c.verdict == "optimal")
        our_better_count = sum(1 for c in comparisons if c.verdict == "our_better")
        needs_tuning_count = sum(1 for c in comparisons if c.verdict == "needs_tuning")
        
        # 我们的得分
        # optimal = 100分, our_better = 80分, needs_tuning = 50分
        our_score = (optimal_count * 100 + our_better_count * 80 + needs_tuning_count * 50) / max(1, len(comparisons))
        
        # 参考得分 (假设)
        reference_score = (reference.expected_return * 1000)  # 简化计算
        
        # 推导最优参数
        optimal_params = self._derive_optimal_params(our_strategy, comparisons)
        
        # 预期改进
        improvement = 0
        if needs_tuning_count > 0:
            improvement = needs_tuning_count * 0.05  # 每个需调参数预估5%改进
        
        # 置信度
        confidence = min(0.95, 0.5 + optimal_count * 0.1)
        
        # 建议
        recommendations = []
        for c in comparisons:
            if c.verdict == "needs_tuning":
                recommendations.append(
                    f"参数 {c.param_name}: 当前值 {c.our_value:.2f} vs 参考值 {c.reference_value:.2f}, "
                    f"建议调整到 {c.reference_value:.2f} 附近"
                )
        
        if improvement > 0:
            recommendations.append(f"预期收益改进: +{improvement*100:.1f}%")
        
        return DistillationResult(
            strategy_id=strategy_id,
            strategy_name=our_strategy.get("name", strategy_id),
            our_score=our_score,
            reference_score=reference_score,
            params=comparisons,
            optimal_params=optimal_params,
            improvement=improvement,
            confidence=confidence,
            recommendations=recommendations,
            sources_compared=1,
        )
    
    def _derive_optimal_params(
        self, 
        our_strategy: Dict, 
        comparisons: List[ParameterComparison]
    ) -> Dict:
        """
        推导最优参数
        
        规则:
        - optimal: 保持
        - reference_better: 采用参考值
        - our_better: 保持我们的值
        - needs_tuning: 采用参考值
        """
        optimal = our_strategy.copy()
        
        for c in comparisons:
            if c.param_name in optimal:
                if c.verdict in ["reference_better", "needs_tuning"]:
                    optimal[c.param_name] = c.reference_value
        
        return optimal
    
    def distill_all(self) -> Dict:
        """
        蒸馏所有策略
        """
        results = []
        result_objects = []
        total_improvement = 0
        
        for strategy_id in self.our_strategies:
            result = self.distill_strategy(strategy_id)
            if result:
                results.append(asdict(result))
                result_objects.append(result)
                total_improvement += result.improvement
        
        # 计算总体评分
        avg_score = sum(r.our_score for r in result_objects) / max(1, len(result_objects))
        avg_improvement = total_improvement / max(1, len(result_objects))
        
        return {
            "strategies": results,
            "summary": {
                "total_strategies": len(results),
                "average_score": avg_score,
                "total_improvement": total_improvement,
                "avg_improvement": avg_improvement,
                "ready_to_apply": any(r.improvement > 0.03 for r in result_objects if r),
            },
            "platform_references": {
                k: {
                    "platform": v.platform,
                    "url": v.url,
                    "expected_return": v.expected_return,
                }
                for k, v in self.strategy_references.items()
            },
            "timestamp": datetime.now().isoformat(),
        }
    
    def apply_optimal_params(self, strategy_id: str) -> Dict:
        """
        应用最优参数到策略
        """
        result = self.distill_strategy(strategy_id)
        if not result:
            return {"error": "Strategy not found"}
        
        # 更新我们的策略
        if strategy_id in self.our_strategies:
            old_params = self.our_strategies[strategy_id].copy()
            self.our_strategies[strategy_id].update(result.optimal_params)
            
            return {
                "strategy_id": strategy_id,
                "old_params": old_params,
                "new_params": result.optimal_params,
                "improvement": result.improvement,
                "applied": True,
                "timestamp": datetime.now().isoformat(),
            }
        
        return {"error": "Could not apply params"}
    
    def generate_optimization_script(self) -> str:
        """
        生成优化脚本
        """
        script = '''#!/bin/bash
#===============================================================================
# 🪿 GO2SE 策略参数优化脚本
#===============================================================================
# 根据蒸馏结果自动优化策略参数

STRATEGY_DIR="/root/.openclaw/workspace/GO2SE_PLATFORM/backend/app/core"
CONFIG_FILE="optimal_params.json"

echo "🪿 开始策略参数优化..."

# 读取蒸馏结果
DISTILL_RESULT=$(python3 -c "
import json
with open('strategy_distillation_results.json') as f:
    data = json.load(f)
    for s in data['strategies']:
        if s['improvement'] > 0.03:
            print(s['strategy_id'], s['improvement'])
")

echo "待优化策略: $DISTILL_RESULT"

# TODO: 自动应用最优参数到数据库和脚本
# 需要在得到确认后再执行

echo "✅ 策略优化建议已生成，请检查后手动应用"
'''
        return script
    
    def save_distillation_results(self, output_path: str = None):
        """
        保存蒸馏结果
        """
        results = self.distill_all()
        
        if output_path is None:
            output_path = "/root/.openclaw/workspace/GO2SE_PLATFORM/strategy_distillation_results.json"
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"蒸馏结果已保存: {output_path}")
        
        return output_path


# 全局实例
distiller = StrategyDistiller()
