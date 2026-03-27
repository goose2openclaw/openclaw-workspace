#!/usr/bin/env python3
"""
北斗七鑫 - 智能止盈系统 v11
动态止盈 + 声纳学习 + 参数可调
"""

import json
import time
import secrets
import random
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import deque

# ==================== 声纳库 (增强版) ====================

class SonarLibrary:
    """声纳库 - 趋势模型"""
    
    def __init__(self):
        # 趋势模型配置
        self.models = {
            # 打兔子模型
            'rabbit': {
                'breakout': {'name': '突破', 'tp_removal_threshold': 0.25, 'duration': 4, 'confidence': 0.75},
                'momentum': {'name': '动量', 'tp_removal_threshold': 0.30, 'duration': 6, 'confidence': 0.70},
                'trend_following': {'name': '趋势跟随', 'tp_removal_threshold': 0.20, 'duration': 8, 'confidence': 0.72},
            },
            # 打地鼠模型
            'mole': {
                'volatility_surf': {'name': '波动surf', 'tp_removal_threshold': 0.35, 'duration': 2, 'confidence': 0.68},
                'mean_reversion': {'name': '均值回归', 'tp_removal_threshold': 0.40, 'duration': 3, 'confidence': 0.72},
                'grid_trading': {'name': '网格交易', 'tp_removal_threshold': 0.25, 'duration': 4, 'confidence': 0.65},
            },
            # 跟大哥模型
            'follow': {
                'market_making': {'name': '做市', 'tp_removal_threshold': None, 'duration': None, 'confidence': 0.80},  # 无限制
                'liquidity_provision': {'name': '流动性', 'tp_removal_threshold': None, 'duration': None, 'confidence': 0.75},
                'spread_capture': {'name': '价差捕获', 'tp_removal_threshold': 0.50, 'duration': 1, 'confidence': 0.70},
            },
            # 搭便车模型
            'hitchhike': {
                'copy_trading': {'name': '跟单', 'tp_removal_threshold': None, 'duration': None, 'confidence': 0.78},  # 无限制
                'signal_following': {'name': '信号跟随', 'tp_removal_threshold': 0.30, 'duration': 4, 'confidence': 0.72},
                'momentum_copy': {'name': '动量复制', 'tp_removal_threshold': 0.25, 'duration': 6, 'confidence': 0.70},
            },
            # 走着瞧模型
            'prediction': {
                'sentiment': {'name': '情绪', 'tp_removal_threshold': 0.35, 'duration': 4, 'confidence': 0.68},
                'event_based': {'name': '事件驱动', 'tp_removal_threshold': 0.30, 'duration': 8, 'confidence': 0.75},
                'arbitrage': {'name': '套利', 'tp_removal_threshold': 0.40, 'duration': 2, 'confidence': 0.80},
            },
            # 薅羊毛模型
            'airdrop': {
                'task_completion': {'name': '任务', 'tp_removal_threshold': None, 'duration': None, 'confidence': 0.85},
                'claim_tracking': {'name': '追踪', 'tp_removal_threshold': 0.50, 'duration': 12, 'confidence': 0.65},
            },
            # 穷孩子模型
            'crowdsource': {
                'micro_tasks': {'name': '微任务', 'tp_removal_threshold': None, 'duration': None, 'confidence': 0.90},
                'annotation': {'name': '标注', 'tp_removal_threshold': 0.60, 'duration': 4, 'confidence': 0.75},
            }
        }
        
        # 学习历史
        self.learning_history = deque(maxlen=500)
    
    def get_model(self, tool: str, model_name: str = None) -> Dict:
        """获取模型"""
        if tool not in self.models:
            return None
        
        if model_name and model_name in self.models[tool]:
            return self.models[tool][model_name]
        
        # 返回默认模型
        return list(self.models[tool].values())[0]
    
    def get_tool_models(self, tool: str) -> List[Dict]:
        """获取工具的所有模型"""
        return list(self.models.get(tool, {}).values())
    
    def update_model(self, tool: str, model_name: str, params: Dict):
        """更新模型参数 (学习)"""
        if tool in self.models and model_name in self.models[tool]:
            self.models[tool][model_name].update(params)
            
            self.learning_history.append({
                'tool': tool,
                'model': model_name,
                'params': params,
                'time': int(time.time())
            })

# ==================== 智能止盈系统 ====================

class SmartTakeProfit:
    """智能止盈系统"""
    
    def __init__(self, sonar: SonarLibrary):
        self.sonar = sonar
        
        # 全局默认参数
        self.default_config = {
            'duration_hours': 6,  # 短期时长(小时)
            'drawdown_threshold': 0.30,  # 回撤30%
            'min_profit': 0.05,  # 最小盈利5%才启用
        }
        
        # 每个工具的配置
        self.tool_configs = {}
        
        # 盈利追踪
        self.profit_tracking = {}
    
    def configure_tool(self, tool: str, duration: int = None, 
                     drawdown: float = None, min_profit: float = None):
        """配置工具参数"""
        self.tool_configs[tool] = {
            'duration_hours': duration or self.default_config['duration_hours'],
            'drawdown_threshold': drawdown or self.default_config['drawdown_threshold'],
            'min_profit': min_profit or self.default_config['min_profit']
        }
    
    def get_config(self, tool: str) -> Dict:
        """获取配置"""
        return self.tool_configs.get(tool, self.default_config)
    
    def should_remove_tp(self, tool: str, profit_history: List[float], 
                        model_name: str = None) -> Dict:
        """判断是否移除止盈"""
        config = self.get_config(tool)
        model = self.sonar.get_model(tool, model_name)
        
        if not model:
            return {'remove': False, 'reason': 'no_model'}
        
        # 检查是否有止盈限制
        if model.get('tp_removal_threshold') is None:
            return {
                'remove': True,
                'reason': 'no_limit',
                'model': model['name']
            }
        
        if len(profit_history) < 2:
            return {'remove': False, 'reason': 'insufficient_data'}
        
        # 计算整体增长
        initial = profit_history[0]
        peak = max(profit_history)
        current = profit_history[-1]
        
        # 检查是否达到最小盈利
        if (peak - initial) / initial < config['min_profit']:
            return {'remove': False, 'reason': 'below_min_profit'}
        
        # 检查回撤
        drawdown = (peak - current) / peak
        
        # 检查时长
        duration_ok = len(profit_history) >= config['duration_hours']
        
        if drawdown >= config['drawdown_threshold'] and duration_ok:
            return {
                'remove': True,
                'reason': 'drawdown_triggered',
                'drawdown': drawdown,
                'threshold': model['tp_removal_threshold'],
                'model': model['name'],
                'duration_met': duration_ok
            }
        
        return {
            'remove': False,
            'reason': 'conditions_not_met',
            'drawdown': drawdown,
            'threshold': model['tp_removal_threshold'],
            'duration_hours': len(profit_history),
            'required_hours': config['duration_hours']
        }

# ==================== 趋势学习系统 ====================

class TrendLearning:
    """趋势学习系统"""
    
    def __init__(self, sonar: SonarLibrary):
        self.sonar = sonar
        self.strategies = {}
    
    def learn_from_trade(self, tool: str, model_name: str, 
                        trade_result: Dict):
        """从交易中学习"""
        # 分析交易结果
        profit = trade_result.get('profit', 0)
        duration = trade_result.get('duration', 0)
        drawdown = trade_result.get('max_drawdown', 0)
        
        # 调整模型参数
        if profit > 0:
            # 盈利：可以稍微放宽止盈阈值
            adjustment = 0.02
        else:
            # 亏损：需要收紧
            adjustment = -0.03
        
        current = self.sonar.get_model(tool, model_name)
        if current and current.get('tp_removal_threshold'):
            new_threshold = max(0.1, min(0.5, 
                current['tp_removal_threshold'] + adjustment))
            
            self.sonar.update_model(tool, model_name, {
                'tp_removal_threshold': new_threshold
            })
    
    def get_learned_params(self, tool: str) -> Dict:
        """获取学习后的参数"""
        models = self.sonar.get_tool_models(tool)
        
        return {
            'tool': tool,
            'models': models,
            'learning_count': len(self.sonar.learning_history)
        }

# ==================== 主系统 ====================

class SmartTakeProfitSystem:
    """智能止盈主系统"""
    
    def __init__(self):
        self.sonar = SonarLibrary()
        self.tp = SmartTakeProfit(self.sonar)
        self.learning = TrendLearning(self.sonar)
        
        # 默认配置
        self._init_default_configs()
    
    def _init_default_configs(self):
        """初始化默认配置"""
        # 打兔子: 4小时，回撤25%
        self.tp.configure_tool('rabbit', duration=4, drawdown=0.25, min_profit=0.05)
        
        # 打地鼠: 2小时，回撤35%
        self.tp.configure_tool('mole', duration=2, drawdown=0.35, min_profit=0.03)
        
        # 跟大哥: 无限制
        self.tp.configure_tool('follow', duration=None, drawdown=None)
        
        # 搭便车: 无限制
        self.tp.configure_tool('hitchhike', duration=None, drawdown=None)
        
        # 走着瞧: 4小时，回撤35%
        self.tp.configure_tool('prediction', duration=4, drawdown=0.35, min_profit=0.05)
        
        # 薅羊毛: 无限制
        self.tp.configure_tool('airdrop', duration=None, drawdown=None)
        
        # 穷孩子: 无限制
        self.tp.configure_tool('crowdsource', duration=None, drawdown=None)
    
    def analyze(self, tool: str, model_name: str, 
               profit_history: List[float]) -> Dict:
        """分析"""
        # 获取建议
        suggestion = self.tp.should_remove_tp(tool, profit_history, model_name)
        
        # 获取模型信息
        model = self.sonar.get_model(tool, model_name)
        
        return {
            'tool': tool,
            'model': model,
            'suggestion': suggestion,
            'config': self.tp.get_config(tool),
            'profit_history': profit_history[-5:]
        }

# ==================== 测试 ====================

def test():
    print("\n" + "="*80)
    print("🎯 北斗七鑫 - 智能止盈系统 v11 测试")
    print("="*80)
    
    system = SmartTakeProfitSystem()
    
    # 显示声纳库
    print("\n📊 声纳库 - 趋势模型:")
    for tool, models in system.sonar.models.items():
        print(f"\n🔧 {tool}:")
        for name, model in models.items():
            tp = model.get('tp_removal_threshold')
            tp_str = f"{tp*100:.0f}%" if tp else "无限制"
            print(f"   - {model['name']}: 止盈移除条件=回撤{tp_str}, 时长{model['duration']}h, 置信{model['confidence']:.0%}")
    
    # 显示配置
    print("\n\n⚙️ 工具配置:")
    for tool, config in system.tp.tool_configs.items():
        dur = config['duration_hours'] or '无'
        draw = f"{config['drawdown_threshold']*100:.0f}%" if config['drawdown_threshold'] else '无'
        minp = f"{config['min_profit']*100:.0f}%"
        print(f"   {tool}: 时长{dur}h, 回撤{draw}, 最低盈利{minp}")
    
    # 模拟盈利历史测试
    print("\n\n🧪 止盈测试:")
    
    test_cases = [
        ('mole', 'volatility_surf', [0.02, 0.05, 0.08, 0.10, 0.07]),  # 回撤30%
        ('rabbit', 'breakout', [0.03, 0.06, 0.10, 0.08]),  # 回撤20%
        ('follow', 'market_making', [0.01, 0.02, 0.03]),  # 无限制
        ('hitchhike', 'copy_trading', [0.05, 0.15, 0.20, 0.18]),  # 无限制
    ]
    
    for tool, model, history in test_cases:
        result = system.analyze(tool, model, history)
        
        suggestion = result['suggestion']
        status = "✅ 移除止盈" if suggestion['remove'] else "⏸️ 保持止盈"
        
        print(f"\n   {tool} | {result['model']['name']}:")
        print(f"   盈利历史: {[f'{p*100:.0f}%' for p in history]}")
        print(f"   结果: {status}")
        print(f"   原因: {suggestion['reason']}")
        
        if 'drawdown' in suggestion:
            print(f"   回撤: {suggestion['drawdown']*100:.1f}%")

if __name__ == '__main__':
    test()
