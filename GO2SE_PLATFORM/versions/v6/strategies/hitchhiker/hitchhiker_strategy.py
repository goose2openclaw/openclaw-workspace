#!/usr/bin/env python3
"""
🍀 搭便车策略 - 跟单分成
Version: 1.0
Author: GO2SE CEO
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional

class HitchhikerStrategy:
    """搭便车 - 跟单分成策略"""
    
    def __init__(self, config: dict = None):
        self.config = config or self._default_config()
        # 交易员数据 (示例)
        self.traders = {}
        
    def _default_config(self) -> dict:
        return {
            'min_win_rate': 0.60,             # 60%
            'min_profit_ratio': 2.0,          # 盈亏比2
            'min_30d_profit': 0.10,          # 30天盈利10%
            'min_followers': 100,              # 100人跟单
            'max_follow_ratio': 0.20,         # 跟单仓位最多20%
            'base_position': 0.05,            # 5%
            'max_position': 0.10,           # 10%
            'copy_ratio': 0.20,              # 跟单比例
        }
    
    def get_top_traders(self) -> List[dict]:
        """获取顶级交易员"""
        # 实际需要接入交易平台API
        traders = [
            {
                'id': 'trader_001',
                'name': ' whale_hunter',
                'win_rate': 0.72,
                'profit_ratio': 3.2,
                'profit_30d': 0.15,
                'followers': 520,
                'total_trades': 156,
                'specialty': ['BTC', 'ETH'],
            },
            {
                'id': 'trader_002',
                'name': 'defi_master',
                'win_rate': 0.68,
                'profit_ratio': 2.8,
                'profit_30d': 0.12,
                'followers': 320,
                'total_trades': 89,
                'specialty': ['SOL', 'ARB'],
            },
            {
                'id': 'trader_003',
                'name': 'trend_rider',
                'win_rate': 0.65,
                'profit_ratio': 2.5,
                'profit_30d': 0.08,
                'followers': 210,
                'total_trades': 234,
                'specialty': ['BTC', 'SOL'],
            },
        ]
        
        return [t for t in traders if self._check_conditions(t)]
    
    def _check_conditions(self, trader: dict) -> bool:
        """检查交易员是否符合条件"""
        if trader['win_rate'] < self.config['min_win_rate']:
            return False
        if trader['profit_ratio'] < self.config['min_profit_ratio']:
            return False
        if trader['profit_30d'] < self.config['min_30d_profit']:
            return False
        if trader['followers'] < self.config['min_followers']:
            return False
        return True
    
    def get_trader_positions(self, trader_id: str) -> List[dict]:
        """获取交易员当前仓位"""
        # 实际需要接入跟单平台API
        # 示例数据
        positions = [
            {
                'trader_id': trader_id,
                'symbol': 'BTC/USDT',
                'side': 'long',
                'position_size': 0.5,  # BTC数量
                'entry_price': 72000,
                'current_price': 73500,
                'pnl_percent': 2.08,
                'confidence': 8,
                'opened_at': '2026-03-15T10:00:00Z'
            },
            {
                'trader_id': trader_id,
                'symbol': 'ETH/USDT',
                'side': 'long',
                'position_size': 2.0,
                'entry_price': 2200,
                'current_price': 2350,
                'pnl_percent': 6.82,
                'confidence': 7,
                'opened_at': '2026-03-14T15:00:00Z'
            }
        ]
        
        return positions
    
    def calculate_copy_position(self, trader_position: dict) -> float:
        """计算跟单仓位"""
        # 基础仓位
        position = self.config['base_position']
        
        # 交易员盈利加成
        if trader_position.get('pnl_percent', 0) > 0:
            profit_bonus = trader_position['pnl_percent'] * 0.01
            position += profit_bonus
        
        # 置信度加成
        confidence = trader_position.get('confidence', 5)
        confidence_bonus = (confidence - 5) * 0.005
        position += confidence_bonus
        
        # 限制最大仓位
        max_copy = trader_position.get('position_size', 0) * self.config['copy_ratio']
        
        return min(position, max_copy, self.config['max_position'])
    
    def generate_signals(self) -> List[dict]:
        """生成跟单信号"""
        signals = []
        traders = self.get_top_traders()
        
        for trader in traders:
            positions = self.get_trader_positions(trader['id'])
            
            for pos in positions:
                # 检查是否应该跟单
                if pos['pnl_percent'] > -2:  # 没有大幅亏损
                    copy_size = self.calculate_copy_position(pos)
                    
                    signals.append({
                        'strategy': 'hitchhiker',
                        'trader_id': trader['id'],
                        'trader_name': trader['name'],
                        'symbol': pos['symbol'],
                        'signal': 'copy_buy' if pos['side'] == 'long' else 'copy_sell',
                        'confidence': pos['confidence'],
                        'position_size': copy_size,
                        'entry_price': pos['entry_price'],
                        'stop_loss': -0.05,  # -5%
                        'take_profit': 0.10,  # +10%
                        'reason': f'跟单{trader["name"]}',
                        'timestamp': datetime.now().isoformat()
                    })
        
        # 按置信度排序
        return sorted(signals, key=lambda x: x['confidence'], reverse=True)


# 示例执行
if __name__ == '__main__':
    strategy = HitchhikerStrategy()
    traders = strategy.get_top_traders()
    print(f"🍀 搭便车策略 - 优质交易员: {len(traders)}")
    for t in traders:
        print(f"  {t['name']}: 胜率{t['win_rate']*100:.0f}%, 盈亏比{t['profit_ratio']:.1f}")
    
    signals = strategy.generate_signals()
    print(f"  待跟单信号: {len(signals)}")
