#!/usr/bin/env python3
"""
北斗七鑫 - 全自动智能投资交易系统
核心决策引擎 + 五类投资行为 + 二类赚钱活动
"""

import json
import time
import requests
import asyncio
import aiohttp
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from collections import deque

# ==================== 配置 ====================

@dataclass
class SystemMode:
    """系统模式"""
    name: str
    risk_tolerance: str
    scan_interval: int = 60
    confidence_threshold: float = 0.6
    max_position: float = 0.10
    stop_loss: float = 0.03
    take_profit: float = 0.08
    reserved_funds: float = 0.10
    leverage: float = 1.0
    
    # 分配
    rabbit: float = 0.50      # 打兔子
    mole: float = 0.20         # 打地鼠
    prediction: float = 0.10   # 走着瞧
    follow: float = 0.10      # 跟大哥
    hitchhike: float = 0.10   # 搭便车

# 预设模式
MODES = {
    'conservative': SystemMode(
        name='保守', risk_tolerance='low',
        scan_interval=120, confidence_threshold=0.7,
        max_position=0.08, stop_loss=0.02, take_profit=0.05,
        reserved_funds=0.20, leverage=1.0,
        rabbit=0.70, mole=0.10, prediction=0.05, follow=0.10, hitchhike=0.05
    ),
    'balanced': SystemMode(
        name='平衡', risk_tolerance='medium',
        scan_interval=60, confidence_threshold=0.6,
        max_position=0.10, stop_loss=0.03, take_profit=0.08,
        reserved_funds=0.10, leverage=1.5,
        rabbit=0.50, mole=0.20, prediction=0.10, follow=0.10, hitchhike=0.10
    ),
    'aggressive': SystemMode(
        name='激进', risk_tolerance='high',
        scan_interval=30, confidence_threshold=0.5,
        max_position=0.15, stop_loss=0.05, take_profit=0.15,
        reserved_funds=0.05, leverage=2.0,
        rabbit=0.30, mole=0.35, prediction=0.15, follow=0.10, hitchhike=0.10
    ),
}

# ==================== 投资行为配置 ====================

@dataclass
class InvestmentBehavior:
    """投资行为"""
    name: str
    symbols: List[str]
    strategy: str
    risk_level: str
    max_position: float
    stop_loss: float
    take_profit: float
    scan_interval: int
    confidence_threshold: float
    enabled: bool = True

# 打兔子 - Top20
RABBIT_COINS = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'AVAX', 'DOGE', 'DOT', 'MATIC',
                'LINK', 'UNI', 'ATOM', 'LTC', 'ETC', 'XLM', 'NEAR', 'APT', 'AR', 'FIL']

RABBIT_BEHAVIOR = InvestmentBehavior(
    name='打兔子',
    symbols=[f'{c}/USDT' for c in RABBIT_COINS[:10]],
    strategy='momentum',
    risk_level='low',
    max_position=0.15,
    stop_loss=0.03,
    take_profit=0.08,
    scan_interval=60,
    confidence_threshold=0.6
)

# 打地鼠 - 其他币
MOLE_BEHAVIOR = InvestmentBehavior(
    name='打地鼠',
    symbols=[],  # 动态获取
    strategy='breakout',
    risk_level='high',
    max_position=0.05,
    stop_loss=0.05,
    take_profit=0.15,
    scan_interval=30,
    confidence_threshold=0.5
)

# ==================== 核心系统 ====================

class BeidouQixinSystem:
    """北斗七鑫智能投资系统"""
    
    def __init__(self, mode: str = 'balanced', total_capital: float = 10000):
        # 模式
        self.mode = MODES.get(mode, MODES['balanced'])
        self.mode_name = mode
        
        # 资金
        self.total_capital = total_capital
        self.reserved_capital = total_capital * self.mode.reserved_funds
        
        # 持仓
        self.positions: Dict[str, Dict] = {}
        
        # 投资组合目标
        self.portfolio_targets = {
            '打兔子': self.mode.rabbit,
            '打地鼠': self.mode.mole,
            '走着瞧': self.mode.prediction,
            '跟大哥': self.mode.follow,
            '搭便车': self.mode.hitchhike
        }
        
        # 缓存
        self.cache = {}
        
        # 信号
        self.signals = deque(maxlen=100)
        
        # 赚钱活动
        self.earning_activities = []
    
    # ===== 市场扫描 =====
    
    async def scan_market_async(self) -> Dict:
        """异步扫描市场"""
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
                        if abs(change) > 10 * (1 - self.mode.confidence_threshold):
                            alerts.append({
                                'symbol': t['symbol'],
                                'change': change,
                                'source': 'binance',
                                'price': t['lastPrice'],
                                'volume': t['quoteVolume']
                            })
                
                elif name == 'bybit':
                    if data.get('retCode') == 0:
                        for t in data['result']['list']:
                            change = float(t.get('price24hPcnt', 0)) * 100
                            if abs(change) > 10 * (1 - self.mode.confidence_threshold):
                                alerts.append({
                                    'symbol': t['symbol'],
                                    'change': change,
                                    'source': 'bybit',
                                    'price': t.get('lastPrice'),
                                    'volume': t.get('turnover24h')
                                })
            except:
                pass
        
        # 排序
        alerts.sort(key=lambda x: abs(x['change']), reverse=True)
        
        return {
            'total': len(alerts),
            'alerts': alerts[:50],
            'timestamp': int(time.time())
        }
    
    def scan_market(self) -> Dict:
        """同步扫描"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self.scan_market_async())
        loop.close()
        return result
    
    # ===== 趋势分析 =====
    
    def analyze_symbol(self, symbol: str) -> Dict:
        """分析单个符号"""
        # 获取价格
        sym = symbol.replace('/', '')
        try:
            r = requests.get(f'https://api.binance.com/api/v3/ticker/24hr?symbol={sym}', timeout=5)
            data = r.json()
        except:
            return {'error': 'failed to fetch'}
        
        change = float(data.get('priceChangePercent', 0))
        price = float(data.get('lastPrice', 0))
        volume = float(data.get('quoteVolume', 0))
        
        # 简单趋势判断
        if change > 5 * (1 - self.mode.confidence_threshold):
            trend = 'bullish'
            signal = 'BUY'
        elif change < -5 * (1 - self.mode.confidence_threshold):
            trend = 'bearish'
            signal = 'SELL'
        else:
            trend = 'neutral'
            signal = 'HOLD'
        
        # 计算置信度
        confidence = min(abs(change) / 20, 1.0)
        
        return {
            'symbol': symbol,
            'price': price,
            'change': change,
            'volume': volume,
            'trend': trend,
            'signal': signal,
            'confidence': confidence,
            'timestamp': int(time.time())
        }
    
    # ===== 投资行为分类 =====
    
    def classify_behavior(self, symbol: str, analysis: Dict) -> str:
        """分类投资行为"""
        # 检查是否是兔子 (Top10)
        base = symbol.replace('/USDT', '').replace('USDT', '')
        if base in RABBIT_COINS[:10]:
            return '打兔子'
        
        # 打地鼠
        if abs(analysis.get('change', 0)) > 10:
            return '打地鼠'
        
        # 走着瞧 - 预测市场
        if 'POL' in symbol or 'PRED' in symbol:
            return '走着瞧'
        
        # 跟大哥 - 大户
        if analysis.get('volume', 0) > 100000000:  # $100M+
            return '跟大哥'
        
        # 搭便车
        if 'COPY' in symbol or 'LEADER' in symbol:
            return '搭便车'
        
        return '打地鼠'  # 默认打地鼠
    
    # ===== 组合管理 =====
    
    def calculate_position_size(self, behavior: str, confidence: float) -> float:
        """计算仓位"""
        base_size = self.portfolio_targets.get(behavior, 0.10)
        
        # 调整
        size = base_size * confidence
        
        # 限制
        return min(size, self.mode.max_position)
    
    def check_portfolio_limits(self, behavior: str) -> bool:
        """检查组合限制"""
        # 计算当前仓位
        current = sum(p.get('size', 0) for p in self.positions.values() 
                     if p.get('behavior') == behavior)
        
        target = self.portfolio_targets.get(behavior, 0.10) * self.total_capital
        
        return current < target
    
    # ===== 风险管理 =====
    
    def check_risk(self, symbol: str, analysis: Dict) -> Dict:
        """风险检查"""
        pnl = 0
        action = 'HOLD'
        
        if symbol in self.positions:
            pos = self.positions[symbol]
            entry = pos.get('entry', 0)
            current = analysis.get('price', 0)
            
            if entry > 0:
                pnl = (current - entry) / entry
                
                # 止损
                if pnl <= -self.mode.stop_loss:
                    action = 'STOP_LOSS'
                # 止盈
                elif pnl >= self.mode.take_profit:
                    action = 'TAKE_PROFIT'
        
        return {
            'action': action,
            'pnl': pnl,
            'stop_loss': -self.mode.stop_loss,
            'take_profit': self.mode.take_profit
        }
    
    # ===== 决策引擎 =====
    
    def make_decision(self, symbol: str) -> Dict:
        """决策"""
        # 分析
        analysis = self.analyze_symbol(symbol)
        
        if 'error' in analysis:
            return {'action': 'ERROR', 'reason': analysis.get('error')}
        
        # 风险检查
        risk = self.check_risk(symbol, analysis)
        
        if risk['action'] != 'HOLD':
            return risk
        
        # 分类
        behavior = self.classify_behavior(symbol, analysis)
        
        # 检查组合限制
        if not self.check_portfolio_limits(behavior):
            return {'action': 'HOLD', 'reason': 'portfolio_limit'}
        
        # 信号判断
        signal = analysis.get('signal', 'HOLD')
        confidence = analysis.get('confidence', 0)
        
        # 决策
        if confidence >= self.mode.confidence_threshold:
            if signal == 'BUY':
                # 检查备用金
                if self.reserved_capital <= 0:
                    return {'action': 'HOLD', 'reason': 'no_reserved_funds'}
                
                size = self.calculate_position_size(behavior, confidence)
                
                return {
                    'action': 'BUY',
                    'behavior': behavior,
                    'size': size,
                    'confidence': confidence,
                    'price': analysis.get('price')
                }
        
        return {
            'action': 'HOLD',
            'reason': 'low_confidence',
            'confidence': confidence
        }
    
    # ===== 核心流程 =====
    
    def run_cycle(self) -> Dict:
        """运行决策周期"""
        print(f"\n{'='*60}")
        print(f"🌀 北斗七鑫 - {self.mode.name}模式")
        print(f"{'='*60}")
        
        results = {
            'timestamp': int(time.time()),
            'mode': self.mode_name,
            'positions': len(self.positions),
            'decisions': []
        }
        
        # 1. 市场扫描
        print("\n📡 扫描市场...")
        market = self.scan_market()
        print(f"   发现 {market['total']} 交易对异常")
        
        # 2. 分析Top信号
        top_alerts = market['alerts'][:10]
        
        for alert in top_alerts:
            symbol = alert['symbol']
            
            # 确保格式正确
            if not '/' in symbol:
                symbol = symbol.replace('USDT', '/USDT')
            
            # 决策
            decision = self.make_decision(symbol)
            
            print(f"\n   {symbol}: {decision.get('action', 'HOLD')} "
                  f"(置信度: {decision.get('confidence', 0):.1%})")
            
            results['decisions'].append({
                'symbol': symbol,
                'change': alert.get('change'),
                **decision
            })
            
            # 执行
            if decision.get('action') in ['BUY', 'STOP_LOSS', 'TAKE_PROFIT']:
                self._execute(decision, symbol, alert)
        
        # 3. 检查现有持仓
        print("\n📊 持仓检查:")
        for symbol, pos in list(self.positions.items()):
            analysis = self.analyze_symbol(symbol)
            risk = self.check_risk(symbol, analysis)
            
            if risk['action'] != 'HOLD':
                print(f"   ⚠️ {symbol}: {risk['action']} (PnL: {risk['pnl']:.2%})")
                self._execute(risk, symbol, {'price': analysis.get('price')})
        
        # 4. 组合状态
        print(f"\n📈 组合状态:")
        print(f"   总资金: ${self.total_capital:,.2f}")
        print(f"   备用金: ${self.reserved_capital:,.2f}")
        print(f"   持仓数: {len(self.positions)}")
        
        return results
    
    def _execute(self, decision: Dict, symbol: str, data: Dict):
        """执行决策"""
        action = decision.get('action')
        
        if action == 'BUY':
            # 建仓
            self.positions[symbol] = {
                'entry': data.get('price'),
                'size': decision.get('size', 0),
                'behavior': decision.get('behavior', '打地鼠'),
                'entry_time': int(time.time())
            }
            self.reserved_capital -= decision.get('size', 0) * self.total_capital
            print(f"   ✅ 买入: {symbol} @ {data.get('price')}")
        
        elif action in ['STOP_LOSS', 'TAKE_PROFIT']:
            # 平仓
            if symbol in self.positions:
                pos = self.positions.pop(symbol)
                self.reserved_capital += pos.get('size', 0) * self.total_capital
                print(f"   ❌ 平仓: {symbol} ({action})")
    
    # ===== 赚钱活动 =====
    
    def check_earning_opportunities(self) -> List[Dict]:
        """检查赚钱机会"""
        opportunities = []
        
        # 简单检查
        if self.reserved_capital > 100:  # 有备用金
            opportunities.append({
                'type': 'airdrops',
                'expected_return': 0.05,
                'risk': 'low'
            })
        
        return opportunities

# ==================== 主程序 ====================

def run_simulation(mode: str = 'balanced', cycles: int = 50):
    """运行模拟"""
    print(f"\n{'#'*60}")
    print(f"北斗七鑫 - 模拟测试 ({mode}模式)")
    print(f"{'#'*60}\n")
    
    system = BeidouQixinSystem(mode=mode, total_capital=10000)
    
    results = []
    
    for i in range(cycles):
        print(f"\n{'='*40}")
        print(f"第 {i+1}/{cycles} 轮")
        print(f"{'='*40}")
        
        result = system.run_cycle()
        results.append(result)
        
        time.sleep(1)
    
    # 汇总
    print(f"\n{'#'*60}")
    print("模拟结果汇总")
    print(f"{'#'*60}")
    
    buy_count = sum(1 for r in results for d in r.get('decisions', []) if d.get('action') == 'BUY')
    sell_count = sum(1 for r in results for d in r.get('decisions', []) if d.get('action') in ['STOP_LOSS', 'TAKE_PROFIT'])
    
    print(f"   总轮次: {cycles}")
    print(f"   买入次数: {buy_count}")
    print(f"   卖出次数: {sell_count}")
    print(f"   最终持仓: {len(system.positions)}")
    
    return system, results

if __name__ == '__main__':
    # 测试
    system = BeidouQixinSystem(mode='balanced')
    system.run_cycle()
