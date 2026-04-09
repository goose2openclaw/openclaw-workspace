#!/usr/bin/env python3
"""
北斗七鑫 - 快速Dry-Run测试版
减少网络调用，加速测试
"""

import random
import time
from collections import deque

# 工具配置
TOOLS = {
    'rabbit': {'name': '打兔子', 'base_win': 0.65, 'base_return': 0.08},
    'mole': {'name': '打地鼠', 'base_win': 0.45, 'base_return': 0.15},
    'prediction': {'name': '走着瞧', 'base_win': 0.55, 'base_return': 0.20},
    'follow': {'name': '跟大哥', 'base_win': 0.60, 'base_return': 0.12},
    'hitchhike': {'name': '搭便车', 'base_win': 0.70, 'base_return': 0.08},
    'airdrop': {'name': '薅羊毛', 'base_win': 0.80, 'base_return': 0.30},
    'crowdsource': {'name': '穷孩子', 'base_win': 0.85, 'base_return': 0.20},
}

def generate_signals():
    """生成模拟信号"""
    signals = []
    
    for tool, config in TOOLS.items():
        # 每个工具生成1-3个信号
        count = random.randint(1, 3)
        
        for _ in range(count):
            confidence = random.uniform(0.4, 0.9)
            
            # 基础胜率 + 置信度影响
            win_rate = config['base_win'] * (0.5 + confidence * 0.5)
            
            signals.append({
                'tool': tool,
                'name': f"{config['name']}_{random.randint(1,100)}",
                'confidence': confidence,
                'win_rate': win_rate,
                'expected_return': config['base_return'] * confidence
            })
    
    return signals

def backtest(signals):
    """回测"""
    results = []
    
    for signal in signals:
        # 模拟100次
        wins = 0
        pnl = 0
        
        for _ in range(100):
            if random.random() < signal['win_rate']:
                wins += 1
                pnl += signal['expected_return'] * random.uniform(0.5, 1.5)
            else:
                pnl -= random.uniform(0.01, 0.05)
        
        results.append({
            'signal': signal,
            'win_rate': wins / 100,
            'avg_pnl': pnl / 100,
            'expected_value': (wins / 100) * (pnl / 100)
        })
    
    # 按期望值排序
    results.sort(key=lambda x: x['expected_value'], reverse=True)
    return results

def make_decision(backtest_result):
    """决策"""
    signal = backtest_result['signal']
    ev = backtest_result['expected_value']
    win_rate = backtest_result['win_rate']
    
    if ev > 0.01 and win_rate > 0.5:
        return 'EXECUTE'
    elif ev > 0:
        return 'MONITOR'
    return 'WAIT'

def execute(decision, dry_run=True):
    """执行"""
    if decision == 'WAIT':
        return {'status': 'skipped', 'pnl': 0}
    
    # 模拟执行
    success = random.random() > 0.1
    pnl = random.uniform(-0.02, 0.08) if success else random.uniform(-0.05, -0.01)
    
    return {
        'status': 'success' if success else 'failed',
        'pnl': pnl
    }

def run_cycle(stats):
    """单轮"""
    # 1. 生成信号
    signals = generate_signals()
    
    # 2. 回测
    results = backtest(signals)
    
    # 3. 决策
    decisions = []
    for r in results[:5]:
        decision = make_decision(r)
        decisions.append((r, decision))
    
    # 4. 执行
    for r, decision in decisions:
        result = execute(decision)
        
        if result['status'] != 'skipped':
            stats['executions'] += 1
            
            if result['pnl'] > 0:
                stats['wins'] += 1
            else:
                stats['losses'] += 1
            
            stats['total_pnl'] += result['pnl']

def run_dry_run(cycles=100):
    """Dry Run"""
    print(f"\n🧪 Dry Run - {cycles}次测试")
    print("="*50)
    
    stats = {
        'executions': 0,
        'wins': 0,
        'losses': 0,
        'total_pnl': 0
    }
    
    # 按工具统计
    tool_stats = {t: {'wins': 0, 'losses': 0, 'pnl': 0} for t in TOOLS}
    
    for i in range(cycles):
        run_cycle(stats)
        
        if (i + 1) % 20 == 0:
            print(f"  进度: {i+1}/{cycles} | 胜:{stats['wins']} 负:{stats['losses']} PnL:{stats['total_pnl']:.2%}")
    
    # 汇总
    print(f"\n{'='*50}")
    print(f"📊 结果汇总")
    print(f"{'='*50}")
    print(f"总执行: {stats['executions']}")
    print(f"胜利: {stats['wins']}")
    print(f"失败: {stats['losses']}")
    print(f"胜率: {stats['wins']/max(1,stats['executions']):.1%}")
    print(f"总PnL: {stats['total_pnl']:.2%}")
    
    return stats

# 测试
if __name__ == '__main__':
    run_dry_run(100)
