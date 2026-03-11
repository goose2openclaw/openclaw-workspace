#!/usr/bin/env python3
"""
XIAMI Sonar Pro v2
"""

import ccxt
import json
from datetime import datetime

class XiamiSonarPro:
    def __init__(self):
        with open('skills/xiami/data/sonar_pro.json', 'r') as f:
            self.config = json.load(f)
    
    def get_indicators(self, symbol):
        try:
            e = ccxt.binance()
            ohlcv = e.fetch_ohlcv(symbol, '5m', limit=100)
            
            closes = [c[4] for c in ohlcv]
            highs = [c[2] for c in ohlcv]
            lows = [c[3] for c in ohlcv]
            volumes = [c[5] for c in ohlcv]
            
            # RSI
            deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
            gains = [d if d > 0 else 0 for d in deltas]
            losses = [-d if d < 0 else 0 for d in deltas]
            avg_gain = sum(gains[-14:]) / 14
            avg_loss = sum(losses[-14:]) / 14
            rsi = 100 - (100 / (1 + avg_gain / (avg_loss + 0.0001)))
            
            # MACD
            ema12 = sum(closes[-12:]) / 12
            ema26 = sum(closes[-26:]) / 26
            macd = ema12 - ema26
            
            # SMA
            sma20 = sum(closes[-20:]) / 20
            sma50 = sum(closes[-50:]) / 50
            
            # Volume
            vol_ma = sum(volumes[-20:]) / 20
            vol_ratio = volumes[-1] / vol_ma
            
            return {
                'symbol': symbol,
                'price': closes[-1],
                'rsi': rsi,
                'macd': macd,
                'sma20': sma20,
                'sma50': sma50,
                'vol_ratio': vol_ratio,
                'change': (closes[-1] - closes[-10]) / closes[-10] * 100
            }
        except:
            return None
    
    def calculate_confidence(self, ind):
        score = 0
        
        if ind['rsi'] < 30: score += 3
        elif ind['rsi'] < 40: score += 2
        elif ind['rsi'] > 70: score -= 3
        elif ind['rsi'] > 60: score -= 2
        
        if ind['macd'] > 0: score += 2
        else: score -= 2
        
        if ind['price'] > ind['sma20']: score += 2
        else: score -= 2
        
        if ind['vol_ratio'] > 2: score += 2
        elif ind['vol_ratio'] > 1.5: score += 1
        
        return max(0, min(10, score))
    
    def detect_pattern(self, ind):
        patterns = []
        
        if ind['rsi'] > 50 and ind['price'] > ind['sma20'] and ind['macd'] > 0:
            patterns.append('动量上涨')
        if ind['rsi'] < 50 and ind['price'] < ind['sma20'] and ind['macd'] < 0:
            patterns.append('动量下跌')
        if ind['vol_ratio'] > 2 and ind['change'] > 3:
            patterns.append('放量突破')
        if ind['vol_ratio'] > 2 and ind['change'] < -3:
            patterns.append('放量下跌')
        if ind['rsi'] < 30:
            patterns.append('超卖')
        if ind['rsi'] > 70:
            patterns.append('超买')
        
        return patterns
    
    def should_trade(self, confidence, patterns):
        rules = self.config['execution_rules']
        
        if confidence < rules['min_confidence']:
            return False, f"置信度{confidence}<{rules['min_confidence']}"
        if not patterns:
            return False, "无形态"
        
        return True, f"置信度{confidence}"
    
    def run(self):
        print("="*60)
        print("XIAMI Sonar Pro v2")
        print(datetime.now().strftime('%H:%M:%S'))
        print("="*60)
        
        symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT', 'ADA/USDT', 'DOGE/USDT']
        
        results = []
        
        for symbol in symbols:
            ind = self.get_indicators(symbol)
            if not ind:
                continue
            
            confidence = self.calculate_confidence(ind)
            patterns = self.detect_pattern(ind)
            can_trade, reason = self.should_trade(confidence, patterns)
            
            results.append({
                'symbol': symbol,
                'price': ind['price'],
                'change': ind['change'],
                'rsi': ind['rsi'],
                'macd': ind['macd'],
                'vol_ratio': ind['vol_ratio'],
                'confidence': confidence,
                'patterns': patterns,
                'can_trade': can_trade
            })
        
        results.sort(key=lambda x: x['confidence'], reverse=True)
        
        print(f"\n观测 {len(results)} 个标的")
        
        trades = [r for r in results if r['can_trade']]
        
        if trades:
            print(f"\n可执行信号 ({len(trades)}个):")
            for t in trades[:3]:
                print(f"\n{t['symbol']}")
                print(f"  ${t['price']:.2f} | {t['change']:+.1f}%")
                print(f"  RSI:{t['rsi']:.0f} | MACD:{t['macd']:.2f}")
                print(f"  成交量:{t['vol_ratio']:.1f}x | 置信度:{t['confidence']}/10")
                print(f"  形态: {', '.join(t['patterns'])}")
        
        return results

if __name__ == "__main__":
    XiamiSonarPro().run()
