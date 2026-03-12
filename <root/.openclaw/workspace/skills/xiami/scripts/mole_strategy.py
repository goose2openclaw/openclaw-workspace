#!/usr/bin/env python3
"""
🦐 XIAMI 山寨币 - 打地鼠策略
快速发现异动币种，搭便车
"""

import ccxt
import time
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

class XiamiMole:
    """打地鼠策略 - 快速发现异动"""
    
    def __init__(self):
        # 打地鼠配置
        self.config = {
            'min_change': 5,      # 最小波动5%
            'max_position': 50,   # 最大仓位50 USDT
            'stop_loss': 0.05,    # 5% 止损
            'take_profit': 0.12,   # 12% 止盈
            'scan_limit': 100,     # 扫描前100个
            'max_coins': 3,       # 最多同时3个
            'fee': 0.001,         # 交易手续费
        }
        
    def scan_exchange(self, exchange_name):
        """扫描交易所"""
        alerts = []
        
        try:
            exchange = getattr(ccxt, exchange_name)()
            exchange.load_markets()
            
            # 获取所有USDT交易对
            markets = [m for m in exchange.markets.keys() if 'USDT' in m]
            tickers = exchange.fetch_tickers(markets[:self.config['scan_limit']])
            
            for symbol, ticker in tickers.items():
                change = ticker.get('percentage') or 0
                volume = ticker.get('quoteVolume', 0)
                price = ticker.get('last', 0)
                
                # 过滤条件
                if abs(change) >= self.config['min_change'] and volume > 50000 and price > 0.001:
                    # 计算潜在收益
                    potential_profit = abs(change) - (self.config['fee'] * 200)  # 扣除手续费
                    
                    if potential_profit > 3:  # 扣除手续费后还有3%以上
                        score = potential_profit * (volume / 1e6)
                        
                        alerts.append({
                            'symbol': symbol,
                            'exchange': exchange_name,
                            'price': price,
                            'change': change,
                            'volume': volume,
                            'potential_profit': potential_profit,
                            'score': score,
                            'direction': 'LONG' if change > 0 else 'SHORT'
                        })
                        
        except Exception as e:
            print(f"❌ {exchange_name}: {e}")
        
        return alerts
    
    def run(self):
        """运行打地鼠"""
        print("="*60)
        print("🎯 XIAMI 打地鼠 - 山寨币快速套利")
        print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
        print("="*60)
        
        # 并行扫描
        exchanges = ['binance', 'bybit', 'okx', 'gate', 'mexc']
        
        all_alerts = []
        
        with ThreadPoolExecutor(max_workers=5) as ex:
            futures = [ex.submit(self.scan_exchange, ex) for ex in exchanges]
            
            for future in futures:
                all_alerts.extend(future.result())
        
        # 按收益排序
        all_alerts.sort(key=lambda x: x['potential_profit'], reverse=True)
        
        print(f"\n📊 发现 {len(all_alerts)} 个机会")
        
        # 取最佳
        opportunities = all_alerts[:self.config['max_coins']]
        
        print("\n" + "="*60)
        print("🎯 打地鼠信号")
        print("="*60)
        
        for i, opp in enumerate(opportunities, 1):
            emoji = "📈" if opp['change'] > 0 else "📉"
            
            print(f"\n{i}. {emoji} {opp['symbol']} @ {opp['exchange']}")
            print(f"   价格: ${opp['price']:.6f}")
            print(f"   涨跌: {opp['change']:+.1f}%")
            print(f"   成交量: ${opp['volume']/1e6:.1f}M")
            print(f"   潜在收益: {opp['potential_profit']:+.1f}%")
            print(f"   方向: {opp['direction']}")
            
            # 交易决策
            if opp['direction'] == 'LONG':
                action = "🟢 买入"
                stop_loss = opp['price'] * (1 - self.config['stop_loss'])
                take_profit = opp['price'] * (1 + self.config['take_profit'])
            else:
                action = "🔴 做空"
                stop_loss = opp['price'] * (1 + self.config['stop_loss'])
                take_profit = opp['price'] * (1 - self.config['take_profit'])
            
            print(f"   决策: {action}")
            print(f"   止损: ${stop_loss:.6f}")
            print(f"   止盈: ${take_profit:.6f}")
            
            # 资金使用
            usdt = self.config['max_position']
            amount = usdt / opp['price']
            
            print(f"   仓位: {usdt} USDT ≈ {amount:.0f} {opp['symbol'].split('/')[0]}")
            
            # 扣除手续费后净收益
            gross = abs(opp['change'])
            fees = self.config['fee'] * 200  # 买卖手续费
            net = gross - fees
            print(f"   手续费扣除: {fees:.2f}%")
            print(f"   净收益: {net:.1f}%")
        
        if not opportunities:
            print("\n⚪ 无打地鼠机会")
        
        return opportunities

if __name__ == "__main__":
    XiamiMole().run()
