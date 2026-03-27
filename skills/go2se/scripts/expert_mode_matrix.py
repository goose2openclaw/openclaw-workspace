#!/usr/bin/env python3
"""
北斗七鑫 - 专家模式资产表现矩阵
对比普通模式 vs 专家模式 (杠杆1x)
"""

import json
import time
import random
from typing import Dict, List
from datetime import datetime
from collections import deque

# ==================== 配置 ====================

class Config:
    """配置"""
    INITIAL_INVESTMENT = 1000
    
    HOURS_AGO = [24, 48, 72, 154]
    
    TRADING_FEE = 0.1
    
    # 专家模式配置
    EXPERT_CONFIG = {
        'leverage': 1.0,  # 杠杆1x
        'no_tp_tools': ['follow', 'hitchhike', 'rabbit'],  # 移除止盈的工具
        'higher_volatility': 1.3,  # 市场平均波动
    }
    
    # 模式参数
    MODES = {
        'conservative': {
            'name': '保守',
            'risk_level': 0.3,
            'avg_hourly_return': 0.0008,
            'volatility': 0.02,
            'max_daily_trades': 5,
            'win_rate': 0.68
        },
        'balanced': {
            'name': '平衡',
            'risk_level': 0.5,
            'avg_hourly_return': 0.0015,
            'volatility': 0.05,
            'max_daily_trades': 15,
            'win_rate': 0.73
        },
        'aggressive': {
            'name': '激进',
            'risk_level': 0.8,
            'avg_hourly_return': 0.0025,
            'volatility': 0.10,
            'max_daily_trades': 30,
            'win_rate': 0.58
        }
    }

# ==================== 普通模式引擎 ====================

class NormalEngine:
    """普通模式引擎"""
    
    def __init__(self, config: Config):
        self.config = config
    
    def simulate(self, initial: float, hours: int, mode: str, tool: str = None) -> Dict:
        """模拟"""
        mode_params = self.config.MODES[mode]
        
        balance = initial
        trades = 0
        wins = 0
        losses = 0
        
        days = hours / 24
        daily_trades = min(
            int(random.normalvariate(mode_params['max_daily_trades'], 3)),
            mode_params['max_daily_trades']
        )
        
        total_trades = int(daily_trades * days)
        
        for hour in range(hours):
            hourly_return = random.normalvariate(
                mode_params['avg_hourly_return'],
                mode_params['volatility']
            )
            
            balance *= (1 + hourly_return)
            
            if random.random() < 0.3:
                trades += 1
                
                if random.random() < mode_params['win_rate']:
                    win_amount = balance * random.uniform(0.01, 0.05)
                    balance += win_amount
                    wins += 1
                else:
                    loss_amount = balance * random.uniform(0.005, 0.03)
                    balance -= loss_amount
                    losses += 1
                
                balance *= (1 - self.config.TRADING_FEE / 100)
        
        total_return = (balance - initial) / initial
        
        return {
            'initial': initial,
            'final': balance,
            'profit': balance - initial,
            'return_pct': total_return * 100,
            'trades': trades,
            'wins': wins,
            'losses': losses,
            'win_rate': wins / trades if trades > 0 else 0,
            'fees_paid': initial * (trades * self.config.TRADING_FEE / 100)
        }

# ==================== 专家模式引擎 ====================

class ExpertEngine:
    """专家模式引擎"""
    
    def __init__(self, config: Config):
        self.config = config
        self.exp_config = config.EXPERT_CONFIG
    
    def simulate(self, initial: float, hours: int, mode: str, tool: str = None) -> Dict:
        """模拟 - 专家模式"""
        mode_params = self.config.MODES[mode]
        
        # 检查是否移除止盈
        no_tp = tool in self.exp_config['no_tp_tools']
        
        balance = initial
        trades = 0
        wins = 0
        losses = 0
        
        days = hours / 24
        
        # 专家模式：更多交易机会，更高波动
        if no_tp:
            # 移除止盈：持仓更久，收益更高但风险也更大
            daily_trades = min(
                int(random.normalvariate(mode_params['max_daily_trades'] * 0.7, 2)),
                mode_params['max_daily_trades']
            )
            volatility = mode_params['volatility'] * self.exp_config['higher_volatility']
            hourly_return = mode_params['avg_hourly_return'] * 1.2  # 更高收益
        else:
            daily_trades = min(
                int(random.normalvariate(mode_params['max_daily_trades'], 3)),
                mode_params['max_daily_trades']
            )
            volatility = mode_params['volatility']
            hourly_return = mode_params['avg_hourly_return']
        
        total_trades = int(daily_trades * days)
        
        for hour in range(hours):
            # 专家模式：按市场平均波动
            hr = random.normalvariate(hourly_return, volatility)
            
            balance *= (1 + hr)
            
            if random.random() < 0.25:  # 稍微减少交易频率
                trades += 1
                
                # 专家模式更高胜率
                exp_win_rate = min(mode_params['win_rate'] + 0.05, 0.85)
                
                if random.random() < exp_win_rate:
                    win_amount = balance * random.uniform(0.015, 0.08)  # 更高单笔收益
                    balance += win_amount
                    wins += 1
                else:
                    loss_amount = balance * random.uniform(0.003, 0.025)
                    balance -= loss_amount
                    losses += 1
                
                balance *= (1 - self.config.TRADING_FEE / 100)
        
        total_return = (balance - initial) / initial
        
        return {
            'initial': initial,
            'final': balance,
            'profit': balance - initial,
            'return_pct': total_return * 100,
            'trades': trades,
            'wins': wins,
            'losses': losses,
            'win_rate': wins / trades if trades > 0 else 0,
            'fees_paid': initial * (trades * self.config.TRADING_FEE / 100),
            'no_take_profit': no_tp,
            'expert_mode': True
        }

# ==================== 矩阵计算 ====================

class MatrixCalculator:
    """矩阵计算器"""
    
    def __init__(self):
        self.config = Config()
        self.normal_engine = NormalEngine(self.config)
        self.expert_engine = ExpertEngine(self.config)
        self.runs = 10
    
    def calculate_cell(self, engine, hours: int, mode: str, tool: str = None) -> Dict:
        """计算单元格"""
        results = []
        
        for _ in range(self.runs):
            result = engine.simulate(
                self.config.INITIAL_INVESTMENT,
                hours,
                mode,
                tool
            )
            results.append(result)
        
        avg_result = {
            'initial': self.config.INITIAL_INVESTMENT,
            'final': sum(r['final'] for r in results) / len(results),
            'profit': sum(r['profit'] for r in results) / len(results),
            'return_pct': sum(r['return_pct'] for r in results) / len(results),
            'trades': sum(r['trades'] for r in results) / len(results),
            'win_rate': sum(r['win_rate'] for r in results) / len(results),
            'fees_paid': sum(r['fees_paid'] for r in results) / len(results)
        }
        
        return avg_result
    
    def generate_normal_matrix(self) -> Dict:
        """普通模式矩阵"""
        modes = ['conservative', 'balanced', 'aggressive']
        matrix = {}
        
        for mode in modes:
            matrix[mode] = {}
            for hour in self.config.HOURS_AGO:
                matrix[mode][hour] = self.calculate_cell(
                    self.normal_engine, hour, mode
                )
        
        return matrix
    
    def generate_expert_matrix(self) -> Dict:
        """专家模式矩阵"""
        modes = ['conservative', 'balanced', 'aggressive']
        tools = ['rabbit', 'follow', 'hitchhike']  # 移除止盈的工具
        matrix = {}
        
        for mode in modes:
            matrix[mode] = {}
            for hour in self.config.HOURS_AGO:
                # 使用移除止盈的工具计算
                matrix[mode][hour] = self.calculate_cell(
                    self.expert_engine, hour, mode, random.choice(tools)
                )
        
        return matrix

# ==================== 格式化输出 ====================

def format_comparison(normal: Dict, expert: Dict, config: Config):
    """格式比较输出"""
    
    mode_names = {'conservative': '保守', 'balanced': '平衡', 'aggressive': '激进'}
    
    print("\n" + "="*120)
    print("🪿 北斗七鑫 - 普通模式 vs 专家模式 资产表现矩阵对比")
    print("="*120)
    
    print("\n📊 【普通模式】收益矩阵 (初始投资: $1,000)")
    print("-"*120)
    print(f"{'模式':<10} {'24小时':<22} {'48小时':<22} {'72小时':<22} {'154小时':<22}")
    print("-"*120)
    
    for mode in ['conservative', 'balanced', 'aggressive']:
        name = mode_names[mode]
        row = f"{name:<10}"
        
        for hour in [24, 48, 72, 154]:
            result = normal[mode][hour]
            final = result['final']
            pct = result['return_pct']
            
            if pct > 5:
                indicator = "🟢"
            elif pct > 0:
                indicator = "🟡"
            else:
                indicator = "🔴"
            
            row += f"${final:>7.2f} {indicator}{pct:>5.1f}%{'':<8}"
        
        print(row)
    
    print("-"*120)
    
    print("\n📊 【专家模式】收益矩阵 (初始投资: $1,000, 杠杆1x, 无止盈)")
    print("-"*120)
    print(f"{'模式':<10} {'24小时':<22} {'48小时':<22} {'72小时':<22} {'154小时':<22}")
    print("-"*120)
    
    for mode in ['conservative', 'balanced', 'aggressive']:
        name = mode_names[mode]
        row = f"{name:<10}"
        
        for hour in [24, 48, 72, 154]:
            result = expert[mode][hour]
            final = result['final']
            pct = result['return_pct']
            
            if pct > 5:
                indicator = "🟢"
            elif pct > 0:
                indicator = "🟡"
            else:
                indicator = "🔴"
            
            row += f"${final:>7.2f} {indicator}{pct:>5.1f}%{'':<8}"
        
        print(row)
    
    print("-"*120)
    
    # 对比
    print("\n📈 【对比分析】专家模式 vs 普通模式 (154小时)")
    print("-"*100)
    print(f"{'模式':<10} {'普通模式':<18} {'专家模式':<18} {'差异':<18} {'提升':<15}")
    print("-"*100)
    
    for mode in ['conservative', 'balanced', 'aggressive']:
        name = mode_names[mode]
        normal_final = normal[mode][154]['final']
        expert_final = expert[mode][154]['final']
        diff = expert_final - normal_final
        improvement = (expert_final - normal_final) / normal_final * 100
        
        imp_indicator = "📈" if improvement > 0 else "📉"
        
        print(f"{name:<10} ${normal_final:>8,.2f}    ${expert_final:>8,.2f}    ${diff:>+8,.2f}    {imp_indicator}{improvement:>+5.1f}%")
    
    print("-"*100)
    
    # 统计对比
    print("\n📊 【详细统计】(154小时)")
    print("-"*100)
    print(f"{'模式':<10} {'类型':<12} {'交易次数':<12} {'胜率':<12} {'平均收益':<15} {'手续费':<12}")
    print("-"*100)
    
    for mode in ['conservative', 'balanced', 'aggressive']:
        name = mode_names[mode]
        
        n = normal[mode][154]
        e = expert[mode][154]
        
        print(f"{name:<10} {'普通':<12} {int(n['trades']):<12} {n['win_rate']*100:.1f}%{'':<7} ${n['profit']:>8,.2f}{'':<3} ${n['fees_paid']:>8,.2f}")
        print(f"{'':<10} {'专家':<12} {int(e['trades']):<12} {e['win_rate']*100:.1f}%{'':<7} ${e['profit']:>8,.2f}{'':<3} ${e['fees_paid']:>8,.2f}")
        print("-"*100)

# ==================== 主程序 ====================

def main():
    """主程序"""
    calc = MatrixCalculator()
    
    print("\n🔄 计算普通模式矩阵...")
    normal_matrix = calc.generate_normal_matrix()
    
    print("🔄 计算专家模式矩阵...")
    expert_matrix = calc.generate_expert_matrix()
    
    # 输出
    format_comparison(normal_matrix, expert_matrix, calc.config)
    
    # 保存结果
    result = {
        'generated': datetime.now().isoformat(),
        'initial_investment': 1000,
        'normal_mode': {},
        'expert_mode': {}
    }
    
    for mode in ['conservative', 'balanced', 'aggressive']:
        result['normal_mode'][mode] = {}
        result['expert_mode'][mode] = {}
        
        for hour in [24, 48, 72, 154]:
            for key in ['final', 'profit', 'return_pct', 'trades', 'win_rate', 'fees_paid']:
                result['normal_mode'][mode][hour] = result['normal_mode'].get(hour, {})
                result['normal_mode'][mode][hour][key] = round(normal_matrix[mode][hour][key], 2)
                
                result['expert_mode'][mode][hour] = result['expert_mode'].get(hour, {})
                result['expert_mode'][mode][hour][key] = round(expert_matrix[mode][hour][key], 2)
    
    with open('/root/.openclaw/workspace/skills/go2se/data/expert_mode_matrix.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("\n✅ 矩阵已保存至 expert_mode_matrix.json")

if __name__ == '__main__':
    main()
