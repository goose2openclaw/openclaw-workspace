#!/usr/bin/env python3
"""
北斗七鑫 - 模拟测试与参数优化
50轮 x 3种模式 = 默认参数生成
"""

import json
import time
import asyncio
import aiohttp
import numpy as np
from typing import Dict, List
from dataclasses import dataclass, asdict

# ==================== 配置 ====================

@dataclass
class ModeConfig:
    name: str
    scan_interval: int
    confidence_threshold: float
    max_position: float
    stop_loss: float
    take_profit: float
    reserved_funds: float

MODES = {
    'conservative': ModeConfig('保守', 120, 0.7, 0.08, 0.02, 0.05, 0.20),
    'balanced': ModeConfig('平衡', 60, 0.6, 0.10, 0.03, 0.08, 0.10),
    'aggressive': ModeConfig('激进', 30, 0.5, 0.15, 0.05, 0.15, 0.05),
}

# ==================== 市场模拟器 ====================

class MarketSimulator:
    """市场模拟器"""
    
    def __init__(self):
        self.data = None
    
    async def fetch_async(self) -> List[Dict]:
        urls = {
            'binance': 'https://api.binance.com/api/v3/ticker/24hr',
            'bybit': 'https://api.bybit.com/v5/market/tickers?category=spot',
        }
        
        async with aiohttp.ClientSession() as session:
            tasks = [session.get(url) for url in urls.values()]
            responses = await asyncio.gather(*tasks)
        
        alerts = []
        
        for name, resp in zip(urls.keys(), responses):
            try:
                data = await resp.json()
                
                if name == 'binance':
                    for t in data:
                        change = float(t.get('priceChangePercent', 0))
                        alerts.append({
                            'symbol': t['symbol'],
                            'change': change,
                            'source': 'binance',
                            'price': float(t['lastPrice']),
                            'volume': float(t.get('quoteVolume', 0))
                        })
                
                elif name == 'bybit':
                    if data.get('retCode') == 0:
                        for t in data['result']['list']:
                            change = float(t.get('price24hPcnt', 0)) * 100
                            alerts.append({
                                'symbol': t['symbol'],
                                'change': change,
                                'source': 'bybit',
                                'price': float(t.get('lastPrice', 0)),
                                'volume': float(t.get('turnover24h', 0))
                            })
            except:
                pass
        
        return alerts
    
    def fetch(self) -> List[Dict]:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self.fetch_async())
        loop.close()
        return result

# ==================== 模拟系统 ====================

class SimulationSystem:
    """模拟系统"""
    
    def __init__(self, mode: str, capital: float = 10000):
        self.mode = MODES[mode]
        self.mode_name = mode
        self.capital = capital
        self.initial_capital = capital
        self.reserved = capital * self.mode.reserved_funds
        self.positions = {}
        self.market = MarketSimulator()
        
        # 统计
        self.stats = {
            'buy_signals': 0,
            'sell_signals': 0,
            'hold_signals': 0,
            'wins': 0,
            'losses': 0,
            'total_pnl': 0,
            'cycles': 0
        }
    
    def run_cycle(self) -> Dict:
        self.stats['cycles'] += 1
        
        # 获取市场数据
        alerts = self.market.fetch()
        
        # 按变化排序
        alerts.sort(key=lambda x: abs(x.get('change', 0)), reverse=True)
        
        decisions = []
        
        # 分析Top信号
        for alert in alerts[:10]:
            symbol = alert['symbol']
            change = alert.get('change', 0)
            price = alert.get('price', 0)
            
            # 简单信号判断
            confidence = min(abs(change) / 20, 1.0)
            
            if confidence >= self.mode.confidence_threshold:
                if change > 0:
                    # 买入信号
                    if self.reserved > 0 and len(self.positions) < 5:
                        size = self.mode.max_position * self.capital
                        
                        self.positions[symbol] = {
                            'entry': price,
                            'size': size,
                            'entry_pnl': 0
                        }
                        self.reserved -= size
                        
                        self.stats['buy_signals'] += 1
                        decisions.append({'action': 'BUY', 'symbol': symbol, 'change': change})
                else:
                    self.stats['sell_signals'] += 1
            else:
                self.stats['hold_signals'] += 1
        
        # 更新持仓盈亏
        for symbol, pos in list(self.positions.items()):
            # 模拟当前价格
            for a in alerts:
                if a['symbol'] == symbol:
                    current_price = a.get('price', pos['entry'])
                    pnl = (current_price - pos['entry']) / pos['entry']
                    pos['current_pnl'] = pnl
                    
                    # 止损/止盈检查
                    if pnl <= -self.mode.stop_loss or pnl >= self.mode.take_profit:
                        # 平仓
                        self.reserved += pos['size'] * (1 + pnl)
                        
                        if pnl > 0:
                            self.stats['wins'] += 1
                        else:
                            self.stats['losses'] += 1
                        
                        del self.positions[symbol]
                        self.stats['sell_signals'] += 1
                        decisions.append({'action': 'SELL', 'symbol': symbol, 'pnl': pnl})
                    break
        
        # 计算总资产
        position_value = sum(p['size'] * (1 + p.get('current_pnl', 0)) for p in self.positions.values())
        total_assets = self.reserved + position_value
        
        self.stats['total_pnl'] = (total_assets - self.initial_capital) / self.initial_capital
        
        return {
            'cycle': self.stats['cycles'],
            'decisions': decisions,
            'positions': len(self.positions),
            'total_assets': total_assets,
            'reserved': self.reserved,
            'pnl': self.stats['total_pnl']
        }

# ==================== 主测试 ====================

def run_simulation(mode: str, cycles: int = 50) -> Dict:
    """运行模拟"""
    print(f"\n{'='*60}")
    print(f"🧪 模拟测试: {MODES[mode].name}模式")
    print(f"{'='*60}")
    
    system = SimulationSystem(mode)
    
    results = []
    
    for i in range(cycles):
        result = system.run_cycle()
        results.append(result)
        
        if (i + 1) % 10 == 0:
            print(f"  第{i+1}轮: 持仓={result['positions']}, "
                  f"资产=${result['total_assets']:,.0f}, "
                  f"PnL={result['pnl']:.2%}")
        
        time.sleep(0.5)  # 避免请求过快
    
    # 汇总
    final = results[-1]
    
    print(f"\n{'='*60}")
    print(f"📊 {MODES[mode].name}模式 - 最终结果")
    print(f"{'='*60}")
    print(f"  初始资金: ${system.initial_capital:,.2f}")
    print(f"  最终资产: ${final['total_assets']:,.2f}")
    print(f"  总收益: {final['pnl']:.2%}")
    print(f"  买入信号: {system.stats['buy_signals']}")
    print(f"  卖出信号: {system.stats['sell_signals']}")
    print(f"  持仓数: {final['positions']}")
    print(f"  胜率: {system.stats['wins']/(system.stats['wins']+system.stats['losses']+1):.1%}")
    
    return {
        'mode': mode,
        'initial_capital': system.initial_capital,
        'final_assets': final['total_assets'],
        'total_pnl': final['pnl'],
        'buy_signals': system.stats['buy_signals'],
        'sell_signals': system.stats['sell_signals'],
        'win_rate': system.stats['wins']/(system.stats['wins']+system.stats['losses']+1)
    }

def main():
    print("\n" + "="*60)
    print("🚀 北斗七鑫 - 50轮模拟测试")
    print("="*60)
    
    all_results = []
    
    # 三种模式
    for mode in ['conservative', 'balanced', 'aggressive']:
        result = run_simulation(mode, cycles=50)
        all_results.append(result)
    
    # 对比
    print("\n" + "="*60)
    print("📊 三种模式对比")
    print("="*60)
    
    for r in all_results:
        print(f"\n{r['mode']}:")
        print(f"  收益: {r['total_pnl']:.2%}")
        print(f"  买入: {r['buy_signals']}, 卖出: {r['sell_signals']}")
        print(f"  胜率: {r['win_rate']:.1%}")
    
    # 保存结果
    with open('skills/go2se/data/simulation_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print("\n✅ 模拟完成，结果已保存")
    
    return all_results

if __name__ == '__main__':
    main()
