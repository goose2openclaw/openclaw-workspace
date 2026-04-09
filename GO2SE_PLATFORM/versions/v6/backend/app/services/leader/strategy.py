#!/usr/bin/env python3
"""
🪿 跟大哥策略 - 做市协调
跟随大资金/做市商操作
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)


class LeaderSignal(Enum):
    """跟大哥信号"""
    FOLLOW = "follow"      # 跟随
    LEAD = "lead"          # 领先
    EXIT = "exit"          # 退出
    WAIT = "wait"          # 等待


@dataclass
class WhaleData:
    """大资金数据"""
    address: str
    direction: str          # inflow/outflow
    amount: float
    transaction_type: str   # buy/sell/transfer
    token: str
    timestamp: datetime


@dataclass
class LeaderOpportunity:
    """跟大哥机会"""
    symbol: str
    signal: LeaderSignal
    confidence: float
    entry_price: float
    position_size: float
    reason: str
    whale_address: Optional[str]
    timestamp: datetime


class LeaderStrategy:
    """跟大哥策略引擎 - 做市协调"""
    
    def __init__(self):
        self.positions: Dict[str, Dict] = {}
        self.whale_wallets: Dict[str, Dict] = {}  # 监控的大哥钱包
        self.order_book_cache: Dict[str, Dict] = {}
        
        # 配置
        self.min_whale_amount = 100000  # 最少10万USDT
        self.follow_delay = 60  # 跟随延迟秒
        self.position_size_pct = 0.15  # 仓位15%
    
    async def scan_market(
        self,
        whale_data: List[Dict],
        order_book: Dict[str, Dict]
    ) -> List[LeaderOpportunity]:
        """扫描大资金动向"""
        opportunities = []
        
        # 处理大资金数据
        for whale in whale_data:
            opp = self.analyze_whale_movement(whale)
            if opp:
                opportunities.append(opp)
        
        # 分析订单簿
        for symbol, book in order_book.items():
            opp = self.analyze_order_book(symbol, book)
            if opp:
                opportunities.append(opp)
        
        # 按置信度排序
        opportunities.sort(key=lambda x: x.confidence, reverse=True)
        
        return opportunities
    
    def analyze_whale_movement(self, whale: Dict) -> Optional[LeaderOpportunity]:
        """分析大资金动向"""
        
        amount = whale.get('amount_usd', 0)
        if amount < self.min_whale_amount:
            return None
        
        direction = whale.get('direction', '')
        token = whale.get('token', '')
        transaction_type = whale.get('type', '')
        
        # 转换为交易对
        symbol = f"{token}USDT" if token else None
        if not symbol:
            return None
        
        # 判断信号
        if direction == 'inflow' and transaction_type == 'buy':
            # 大资金买入
            confidence = min(10, 5 + (amount / 100000))
            
            return LeaderOpportunity(
                symbol=symbol,
                signal=LeaderSignal.FOLLOW,
                confidence=confidence,
                entry_price=0,  # 市价
                position_size=self.position_size_pct,
                reason=f"大哥买入 ${amount:,.0f}",
                whale_address=whale.get('address'),
                timestamp=datetime.now()
            )
        
        elif direction == 'outflow' and transaction_type == 'sell':
            # 大资金卖出
            confidence = min(10, 5 + (amount / 100000))
            
            return LeaderOpportunity(
                symbol=symbol,
                signal=LeaderSignal.EXIT,
                confidence=confidence,
                entry_price=0,
                position_size=0,
                reason=f"大哥卖出 $${amount:,.0f}, 跟随退出",
                whale_address=whale.get('address'),
                timestamp=datetime.now()
            )
        
        return None
    
    def analyze_order_book(self, symbol: str, book: Dict) -> Optional[LeaderOpportunity]:
        """分析订单簿 - 检测大单"""
        
        bids = book.get('bids', [])
        asks = book.get('asks', [])
        
        if not bids or not asks:
            return None
        
        # 检查大单
        large_bid = self.find_large_order(bids, 50000)  # 5万以上
        large_ask = self.find_large_order(asks, 50000)
        
        if large_bid and not large_ask:
            # 大量买单没人卖，可能上涨
            return LeaderOpportunity(
                symbol=symbol,
                signal=LeaderSignal.LEAD,
                confidence=7.0,
                entry_price=0,
                position_size=self.position_size_pct * 0.5,
                reason=f"订单簿大单: 买单密集",
                whale_address=None,
                timestamp=datetime.now()
            )
        
        elif large_ask and not large_bid:
            # 大量卖单没人买，可能下跌
            return LeaderOpportunity(
                symbol=symbol,
                signal=LeaderSignal.EXIT,
                confidence=7.0,
                entry_price=0,
                position_size=0,
                reason=f"订单簿大单: 卖单密集",
                whale_address=None,
                timestamp=datetime.now()
            )
        
        return None
    
    def find_large_order(self, orders: List[Dict], threshold: float) -> Optional[Dict]:
        """找大单"""
        for order in orders:
            if order.get('amount_usd', 0) >= threshold:
                return order
        return None
    
    def add_whale_wallet(self, address: str, name: str = ""):
        """添加监控的大哥钱包"""
        self.whale_wallets[address] = {
            'name': name,
            'added_at': datetime.now(),
            'total_trades': 0,
            'success_rate': 0
        }
    
    def get_status(self) -> Dict:
        return {
            "strategy": "leader",
            "name": "跟大哥",
            "description": "做市协调 - 跟随大资金",
            "whales_tracking": len(self.whale_wallets),
            "positions": len(self.positions),
            "config": {
                "min_whale_amount": self.min_whale_amount,
                "position_size_pct": self.position_size_pct * 100
            }
        }


leader_strategy = LeaderStrategy()
