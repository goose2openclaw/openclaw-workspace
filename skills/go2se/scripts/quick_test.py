#!/usr/bin/env python3
"""
北斗七鑫 - 快速模拟测试
"""

import json
import time
import requests

def scan_market() -> list:
    """扫描市场"""
    r = requests.get('https://api.binance.com/api/v3/ticker/24hr', timeout=10)
    data = r.json()
    
    alerts = []
    for t in data:
        change = float(t.get('priceChangePercent', 0))
        if abs(change) > 5:
            alerts.append({
                'symbol': t['symbol'],
                'change': change,
                'price': t['lastPrice']
            })
    
    alerts.sort(key=lambda x: abs(x['change']), reverse=True)
    return alerts[:30]

def run_test():
    """运行测试"""
    print("🧪 北斗七鑫 - 模拟测试")
    print("="*50)
    
    # 扫描
    print("\n📡 扫描市场...")
    alerts = scan_market()
    print(f"   发现 {len(alerts)} 个异常\n")
    
    # Top异常
    print("📈 Top异常:")
    for a in alerts[:10]:
        print(f"   {a['change']:+.1f}% {a['symbol']}")
    
    # 三种模式
    modes = {
        '保守': {'threshold': 0.7, 'stop_loss': 0.02, 'take_profit': 0.05, 'reserved': 0.20},
        '平衡': {'threshold': 0.6, 'stop_loss': 0.03, 'take_profit': 0.08, 'reserved': 0.10},
        '激进': {'threshold': 0.5, 'stop_loss': 0.05, 'take_profit': 0.15, 'reserved': 0.05}
    }
    
    results = []
    
    print("\n" + "="*50)
    print("📊 三种模式对比")
    print("="*50)
    
    for mode_name, params in modes.items():
        buys = 0
        sells = 0
        holds = 0
        
        for a in alerts:
            confidence = min(abs(a['change']) / 20, 1.0)
            
            if confidence >= params['threshold']:
                if a['change'] > 0:
                    buys += 1
                else:
                    sells += 1
            else:
                holds += 1
        
        print(f"\n{mode_name}模式:")
        print(f"  置信度阈值: {params['threshold']}")
        print(f"  买入信号: {buys}")
        print(f"  卖出信号: {sells}")
        print(f"  持有: {holds}")
        print(f"  止损: {params['stop_loss']:.0%}")
        print(f"  止盈: {params['take_profit']:.0%}")
        
        results.append({
            'mode': mode_name,
            'threshold': params['threshold'],
            'buys': buys,
            'sells': sells,
            'holds': holds,
            'stop_loss': params['stop_loss'],
            'take_profit': params['take_profit']
        })
    
    # 保存
    output = {
        'alerts': alerts,
        'results': results,
        'timestamp': int(time.time())
    }
    
    with open('skills/go2se/data/simulation_results.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("\n✅ 完成，结果已保存")
    
    return output

if __name__ == '__main__':
    run_test()
