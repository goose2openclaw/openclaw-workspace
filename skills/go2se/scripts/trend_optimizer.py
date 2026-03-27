#!/usr/bin/env python3
"""
趋势模型匹配器 - 参数优化循环
自动调整参数，多次运行找到最佳配置
"""

import json
import time
import numpy as np
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import random

# 导入原脚本
import sys
sys.path.insert(0, 'skills/go2se/scripts')
from trend_pattern_matcher_v2 import (
    TrendPatternMatcher, StrategyTriggerSystem, StrategyTrigger,
    MarketDataFetcher, FeatureExtractor
)

@dataclass
class RunResult:
    """单次运行结果"""
    run_id: int
    params: Dict
    results: List[Dict]
    triggers_count: int
    avg_probability: float
    best_model: str
    features_summary: Dict

class ParameterOptimizer:
    """参数优化器"""
    
    def __init__(self, symbols: List[str] = None):
        self.symbols = symbols or ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']
        self.history = []
        self.best_result = None
        self.best_score = 0
        
        # 参数空间
        self.param_space = {
            'min_probability': [0.25, 0.30, 0.35, 0.40, 0.45],
            'min_confidence': [3, 4, 5, 6],
            'max_models': [3, 5, 7],
            # 特征权重
            'trend_weight': [0.8, 1.0, 1.2, 1.5],
            'momentum_weight': [0.8, 1.0, 1.2],
            'volume_weight': [0.7, 1.0, 1.3],
            # 阈值
            'volatility_threshold': [0.01, 0.015, 0.02, 0.025],
            'trend_direction_threshold': [0.2, 0.25, 0.3, 0.35],
        }
    
    def generate_params(self, iteration: int) -> Dict:
        """生成参数配置"""
        if iteration == 0:
            # 初始默认参数
            return {
                'min_probability': 0.35,
                'min_confidence': 4,
                'max_models': 5,
                'trend_weight': 1.0,
                'momentum_weight': 1.0,
                'volume_weight': 1.0,
                'volatility_threshold': 0.02,
                'trend_direction_threshold': 0.25,
            }
        elif iteration == 1:
            # 尝试更宽松的阈值
            return {
                'min_probability': 0.30,
                'min_confidence': 3,
                'max_models': 5,
                'trend_weight': 1.2,
                'momentum_weight': 1.2,
                'volume_weight': 1.3,
                'volatility_threshold': 0.015,
                'trend_direction_threshold': 0.2,
            }
        elif iteration == 2:
            # 尝试更严格的阈值
            return {
                'min_probability': 0.40,
                'min_confidence': 5,
                'max_models': 3,
                'trend_weight': 1.5,
                'momentum_weight': 0.8,
                'volume_weight': 0.7,
                'volatility_threshold': 0.025,
                'trend_direction_threshold': 0.35,
            }
        elif iteration == 3:
            # 平衡配置
            return {
                'min_probability': 0.32,
                'min_confidence': 4,
                'max_models': 5,
                'trend_weight': 1.1,
                'momentum_weight': 1.1,
                'volume_weight': 1.0,
                'volatility_threshold': 0.018,
                'trend_direction_threshold': 0.28,
            }
        elif iteration == 4:
            # 动量优先
            return {
                'min_probability': 0.28,
                'min_confidence': 3,
                'max_models': 7,
                'trend_weight': 0.9,
                'momentum_weight': 1.5,
                'volume_weight': 1.0,
                'volatility_threshold': 0.015,
                'trend_direction_threshold': 0.22,
            }
        elif iteration == 5:
            # 成交量优先
            return {
                'min_probability': 0.30,
                'min_confidence': 4,
                'max_models': 5,
                'trend_weight': 0.8,
                'momentum_weight': 1.0,
                'volume_weight': 1.5,
                'volatility_threshold': 0.012,
                'trend_direction_threshold': 0.25,
            }
        elif iteration == 6:
            # 保守配置
            return {
                'min_probability': 0.45,
                'min_confidence': 5,
                'max_models': 3,
                'trend_weight': 1.3,
                'momentum_weight': 1.2,
                'volume_weight': 0.8,
                'volatility_threshold': 0.028,
                'trend_direction_threshold': 0.32,
            }
        elif iteration == 7:
            # 激进配置
            return {
                'min_probability': 0.25,
                'min_confidence': 3,
                'max_models': 7,
                'trend_weight': 0.8,
                'momentum_weight': 0.9,
                'volume_weight': 1.2,
                'volatility_threshold': 0.01,
                'trend_direction_threshold': 0.2,
            }
        elif iteration == 8:
            # 趋势优先
            return {
                'min_probability': 0.33,
                'min_confidence': 4,
                'max_models': 5,
                'trend_weight': 1.5,
                'momentum_weight': 0.9,
                'volume_weight': 0.9,
                'volatility_threshold': 0.02,
                'trend_direction_threshold': 0.3,
            }
        else:
            # 随机探索
            return {
                'min_probability': random.choice([0.28, 0.32, 0.35, 0.38]),
                'min_confidence': random.choice([3, 4, 5]),
                'max_models': random.choice([3, 5, 7]),
                'trend_weight': random.choice([0.8, 1.0, 1.2, 1.4]),
                'momentum_weight': random.choice([0.8, 1.0, 1.2, 1.4]),
                'volume_weight': random.choice([0.7, 1.0, 1.3]),
                'volatility_threshold': random.choice([0.012, 0.015, 0.018, 0.02, 0.022]),
                'trend_direction_threshold': random.choice([0.2, 0.25, 0.28, 0.32]),
            }
    
    def apply_params(self, params: Dict) -> Dict:
        """应用参数到配置"""
        config = {
            'min_probability': params['min_probability'],
            'min_confidence': params['min_confidence'],
            'max_models': params['max_models'],
        }
        
        # 特征权重和阈值作为元数据
        config['_meta'] = {
            'trend_weight': params['trend_weight'],
            'momentum_weight': params['momentum_weight'],
            'volume_weight': params['volume_weight'],
            'volatility_threshold': params['volatility_threshold'],
            'trend_direction_threshold': params['trend_direction_threshold'],
        }
        
        return config
    
    def run_single(self, params: Dict, run_id: int) -> RunResult:
        """运行单次测试"""
        config = self.apply_params(params)
        
        print(f"\n{'='*60}")
        print(f"🔄 第 {run_id+1} 次运行")
        print(f"{'='*60}")
        print(f"📋 参数: min_prob={params['min_probability']}, min_conf={params['min_confidence']}")
        print(f"   权重: trend={params['trend_weight']}, momentum={params['momentum_weight']}, volume={params['volume_weight']}")
        
        # 初始化匹配器
        matcher = TrendPatternMatcher(config)
        
        all_results = []
        triggers_count = 0
        probabilities = []
        best_model = ""
        features_sum = {}
        
        for symbol in self.symbols:
            try:
                result = matcher.analyze_symbol(symbol)
                
                if result.get('best_models'):
                    best = result['best_models'][0]
                    probabilities.append(best['probability'])
                    if not best_model:
                        best_model = best['model']
                    elif best['probability'] > probabilities[0]:
                        best_model = best['model']
                
                if result.get('trigger'):
                    triggers_count += 1
                
                all_results.append(result)
                
                # 累计特征
                if result.get('features'):
                    for k, v in result['features'].items():
                        if k not in features_sum:
                            features_sum[k] = []
                        features_sum[k].append(v)
                
                print(f"   {symbol}: {result.get('best_models', [{}])[0].get('model', 'N/A')} "
                      f"({result.get('best_models', [{}])[0].get('probability', 0)*100:.1f}%)")
                
            except Exception as e:
                print(f"   {symbol}: ❌ 错误 - {e}")
        
        # 计算平均
        avg_prob = sum(probabilities) / len(probabilities) if probabilities else 0
        
        # 计算特征平均值
        features_avg = {k: sum(v)/len(v) for k, v in features_sum.items()}
        
        # 计算评分
        score = self._calculate_score(triggers_count, avg_prob, params)
        
        print(f"\n📊 结果: 触发次数={triggers_count}, 平均概率={avg_prob:.2%}, 评分={score:.2f}")
        
        result = RunResult(
            run_id=run_id,
            params=params.copy(),
            results=all_results,
            triggers_count=triggers_count,
            avg_probability=avg_prob,
            best_model=best_model,
            features_summary=features_avg
        )
        
        return result, score
    
    def _calculate_score(self, triggers: int, avg_prob: float, params: Dict) -> float:
        """计算评分"""
        # 评分标准:
        # 1. 触发次数 (1-3次为佳)
        trigger_score = 1.0 if 1 <= triggers <= 3 else 0.5
        
        # 2. 平均概率 (越高越好)
        prob_score = avg_prob
        
        # 3. 参数合理性
        param_score = 1.0
        if params['min_probability'] > 0.4:
            param_score = 0.8
        if params['min_probability'] < 0.28:
            param_score = 0.7
        
        # 综合评分
        score = trigger_score * 0.3 + prob_score * 0.5 + param_score * 0.2
        
        return score
    
    def optimize(self, iterations: int = 10) -> Dict:
        """运行优化循环"""
        print("🚀 趋势模型参数优化循环")
        print("="*60)
        
        results = []
        
        for i in range(iterations):
            # 生成参数
            params = self.generate_params(i)
            
            # 运行测试
            result, score = self.run_single(params, i)
            
            results.append({
                'run_id': i + 1,
                'params': params,
                'score': score,
                'triggers': result.triggers_count,
                'avg_prob': result.avg_probability,
                'best_model': result.best_model
            })
            
            # 更新最佳
            if score > self.best_score:
                self.best_score = score
                self.best_result = result
                print(f"   ⭐ 新最佳配置!")
            
            # 等待一下
            time.sleep(1)
        
        return self._summarize(results)
    
    def _summarize(self, results: List[Dict]) -> Dict:
        """汇总结果"""
        print("\n" + "="*60)
        print("📊 优化结果汇总")
        print("="*60)
        
        # 按评分排序
        sorted_results = sorted(results, key=lambda x: x['score'], reverse=True)
        
        print("\n🏆 Top 3 配置:")
        for i, r in enumerate(sorted_results[:3]):
            print(f"\n   #{i+1} 评分: {r['score']:.3f}")
            print(f"       参数: min_prob={r['params']['min_probability']}, "
                  f"min_conf={r['params']['min_confidence']}")
            print(f"       权重: trend={r['params']['trend_weight']}, "
                  f"momentum={r['params']['momentum_weight']}, "
                  f"volume={r['params']['volume_weight']}")
            print(f"       结果: 触发={r['triggers']}, 平均概率={r['avg_prob']:.2%}")
        
        # 最佳配置
        best = sorted_results[0]
        
        print("\n" + "="*60)
        print("✅ 推荐最佳配置")
        print("="*60)
        print(f"""
# 最佳参数配置:
config = {{
    'min_probability': {best['params']['min_probability']},
    'min_confidence': {best['params']['min_confidence']},
    'max_models': {best['params']['max_models']},
    'trend_weight': {best['params']['trend_weight']},
    'momentum_weight': {best['params']['momentum_weight']},
    'volume_weight': {best['params']['volume_weight']},
    'volatility_threshold': {best['params']['volatility_threshold']},
    'trend_direction_threshold': {best['params']['trend_direction_threshold']},
}}

# 预期效果:
# - 触发次数: {best['triggers']}
# - 平均概率: {best['avg_prob']:.2%}
# - 评分: {best['score']:.3f}
# - 最佳模型: {best['best_model']}
""")
        
        # 保存结果
        with open('skills/go2se/scripts/optimization_results.json', 'w') as f:
            json.dump({
                'results': results,
                'best': best,
                'timestamp': int(time.time())
            }, f, indent=2, default=str)
        
        print("📁 结果已保存到 optimization_results.json")
        
        return best

def main():
    optimizer = ParameterOptimizer()
    best = optimizer.optimize(iterations=10)
    return best

if __name__ == '__main__':
    main()
