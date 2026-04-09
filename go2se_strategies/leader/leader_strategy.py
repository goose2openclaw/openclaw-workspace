#!/usr/bin/env python3
"""
👑 跟大哥策略 - 做市协作
Version: 1.0
Author: GO2SE CEO
"""

import ccxt
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class LeaderStrategy:
    """跟大哥 - 做市协作策略"""
    
    def __init__(self, config: dict = None):
        self.exchange = ccxt.binance()
        self.config = config or self._default_config()
        
    def _default_config(self) -> dict:
        return {
            'min_order_size': 10000,           # $10k
            'min_depth_imbalance': 3.0,        # 3:1
            'min_funding_rate': -0.001,       # 负费率
            'base_position': 0.08,            # 8%
            'max_position': 0.20,            # 20%
            'stop_loss': -0.05,              # -5%
            'take_profit': 0.10,            # 10%
            'order_book_depth': 20,           # 订单簿深度
        }
    
    def get_order_book(self, symbol: str) -> dict:
        """获取订单簿数据"""
        try:
            order_book = self.exchange.fetch_order_book(f'{symbol}/USDT', limit=self.config['order_book_depth'])
            return order_book
        except:
            return {'bids': [], 'asks': []}
    
    def calculate_depth_imbalance(self, order_book: dict) -> float:
        """计算订单簿深度失衡"""
        bids = order_book.get('bids', [])
        asks = order_book.get('asks', [])
        
        if not bids or not asks:
            return 1.0
        
        bid_volume = sum(b[1] for b in bids[:10])
        ask_volume = sum(a[1] for a in asks[:10])
        
        if ask_volume == 0:
            return 10.0
        
        return bid_volume / ask_volume
    
    def detect_whale_orders(self, symbol: str) -> List[dict]:
        """检测大单"""
        whales = []
        order_book = self.get_order_book(symbol)
        
        # 检查卖单大单 (可能在出货)
        for ask in order_book.get('asks', [])[:5]:
            size_usdt = ask[0] * ask[1]  # price * amount
            if size_usdt >= self.config['min_order_size']:
                whales.append({
                    'type': 'sell_wall',
                    'price': ask[0],
                    'size': size_usdt,
                    'side': 'ask'
                })
        
        # 检查买单大单 (可能在吸筹)
        for bid in order_book.get('bids', [])[:5]:
            size_usdt = bid[0] * bid[1]
            if size_usdt >= self.config['min_order_size']:
                whales.append({
                    'type': 'buy_wall',
                    'price': bid[0],
                    'size': size_usdt,
                    'side': 'bid'
                })
        
        return whales
    
    def check_funding_rate(self, symbol: str) -> Optional[float]:
        """检查资金费率"""
        try:
            # Binance 合约资金费率API
            # 这里简化处理
            return -0.0001  # 示例费率
        except:
            return None
    
    def get_candidates(self) -> List[dict]:
        """获取候选币种"""
        symbols = ['BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'DOGE', 'DOT', 'AVAX']
        
        candidates = []
        
        for symbol in symbols:
            order_book = self.get_order_book(symbol)
            whales = self.detect_whale_orders(symbol)
            imbalance = self.calculate_depth_imbalance(order_book)
            funding = self.check_funding_rate(symbol)
            
            # 检查是否有信号
            if whales or imbalance > self.config['min_depth_imbalance'] or \
               (funding and funding < self.config['min_funding_rate']):
                candidates.append({
                    'symbol': symbol,
                    'whales': whales,
                    'depth_imbalance': imbalance,
                    'funding_rate': funding,
                    'has_signal': True
                })
        
        return candidates
    
    def calculate_position(self, whales: list, imbalance: float) -> float:
        """计算仓位"""
        # 基础仓位
        position = self.config['base_position']
        
        # 大单加成: 大单数量 × 1%
        whale_bonus = len(whales) * 0.01
        position += whale_bonus
        
        # 深度加成: 失衡比例 × 2%
        imbalance_bonus = (imbalance - 1) * 0.02
        position += imbalance_bonus
        
        return max(0.05, min(position, self.config['max_position']))
    
    def generate_signal(self, symbol: str) -> dict:
        """生成交易信号"""
        order_book = self.get_order_book(symbol)
        whales = self.detect_whale_orders(symbol)
        imbalance = self.calculate_depth_imbalance(order_book)
        funding = self.check_funding_rate(symbol)
        
        # 信号逻辑
        signal = 'neutral'
        confidence = 5
        reason = ''
        
        # 买单大单 + 深度买入
        buy_walls = [w for w in whales if w['side'] == 'bid']
        if buy_walls and imbalance > self.config['min_depth_imbalance']:
            signal = 'buy'
            confidence = 6 + len(buy_walls) * 1 + (imbalance - 3) * 0.5
            reason = f'检测到{len(buy_walls)}个大单买入,深度失衡{imbalance:.1f}'
        
        # 负费率(多头补贴)
        elif funding and funding < self.config['min_funding_rate']:
            signal = 'buy'
            confidence = 6 + abs(funding) * 1000
            reason = f'资金费率{funding*100:.3f}%,多头补贴'
        
        # 卖单大单 (考虑卖出或减仓)
        sell_walls = [w for w in whales if w['side'] == 'ask']
        if sell_walls and imbalance < 1 / self.config['min_depth_imbalance']:
            signal = 'sell'
            confidence = 6 + len(sell_walls) * 1
            reason = f'检测到{len(sell_walls)}个大单卖出'
        
        position = self.calculate_position(whales, imbalance)
        
        return {
            'strategy': 'leader',
            'symbol': symbol,
            'signal': signal,
            'confidence': min(10, max(0, confidence)),
            'position_size': position,
            'stop_loss': self.config['stop_loss'],
            'take_profit': self.config['take_profit'],
            'whales': whales,
            'depth_imbalance': imbalance,
            'funding_rate': funding,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }


if __name__ == '__main__':
    strategy = LeaderStrategy()
    candidates = strategy.get_candidates()
    print(f"👑 跟大哥策略 - 候选信号: {len(candidates)}")
    for c in candidates[:3]:
        print(f"  {c['symbol']}: 大单{len(c['whales'])}, 失衡{c['depth_imbalance']:.2f}")
