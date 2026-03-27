#!/usr/bin/env python3
"""
🪿 搭便车策略 - 跟单分成
跟随盈利交易员操作
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict

logger = logging.getLogger(__name__)


class HitchhikerSignal(Enum):
    """搭便车信号"""
    COPY = "copy"      # 复制跟单
    INCREASE = "increase"  # 增加跟单
    STOP = "stop"      # 停止跟单
    WAIT = "wait"      # 等待


@dataclass
class Trader:
    """交易员数据"""
    id: str
    name: str
    win_rate: float          # 胜率
    avg_profit: float        # 平均盈利
    max_drawdown: float      # 最大回撤
    total_trades: int        # 总交易数
    recent_pnl: float        # 最近盈利
    followers: int           # 跟随人数
    aum: float               # 管理资产


@dataclass
class HitchhikerOpportunity:
    """搭便车机会"""
    trader_id: str
    trader_name: str
    signal: HitchhikerSignal
    confidence: float
    action: str
    amount: float
    reason: str
    expected_return: float
    timestamp: datetime


class HitchhikerStrategy:
    """搭便车策略 - 跟单分成"""
    
    def __init__(self):
        self.traders: Dict[str, Trader] = {}
        self.following: Dict[str, Dict] = {}  # trader_id -> follow_info
        self.copy_trades: Dict[str, List] = defaultdict(list)
        
        # 配置
        self.min_traders = 5
        self.min_win_rate = 0.55
        self.max_drawdown_threshold = 0.30
        self.allocation_per_trader = 0.03  # 每个交易员3%
    
    async def scan_traders(
        self,
        trader_data: List[Dict]
    ) -> List[HitchhikerOpportunity]:
        """扫描交易员找机会"""
        opportunities = []
        
        for data in trader_data:
            trader = Trader(
                id=data.get('id'),
                name=data.get('name', 'Unknown'),
                win_rate=data.get('win_rate', 0),
                avg_profit=data.get('avg_profit', 0),
                max_drawdown=data.get('max_drawdown', 0),
                total_trades=data.get('total_trades', 0),
                recent_pnl=data.get('recent_pnl', 0),
                followers=data.get('followers', 0),
                aum=data.get('aum', 0)
            )
            
            self.traders[trader.id] = trader
            
            # 分析是否值得跟单
            opp = self.analyze_trader(trader)
            if opp:
                opportunities.append(opp)
        
        # 按预期收益排序
        opportunities.sort(key=lambda x: x.expected_return, reverse=True)
        
        return opportunities
    
    def analyze_trader(self, trader: Trader) -> Optional[HitchhikerOpportunity]:
        """分析交易员是否值得跟单"""
        
        # 基础筛选
        if trader.total_trades < 100:
            return None
        
        if trader.win_rate < self.min_win_rate:
            return None
        
        if trader.max_drawdown > self.max_drawdown_threshold:
            # 回撤太大，减少跟单
            return HitchhikerOpportunity(
                trader_id=trader.id,
                trader_name=trader.name,
                signal=HitchhikerSignal.STOP,
                confidence=8.0,
                action="reduce",
                amount=self.allocation_per_trader * 0.5,
                reason=f"回撤过大: {trader.max_drawdown*100:.1f}%",
                expected_return=-0.1,
                timestamp=datetime.now()
            )
        
        # 计算预期收益
        expected_return = (trader.win_rate * trader.avg_profit * trader.total_trades) / 10000
        
        # 判断信号
        if trader.recent_pnl > 0 and trader.win_rate > 0.65:
            # 胜率高+最近盈利
            confidence = min(10, 5 + trader.win_rate * 5 + trader.recent_pnl / 1000)
            
            # 检查是否已在跟单
            if trader.id in self.following:
                return HitchhikerOpportunity(
                    trader_id=trader.id,
                    trader_name=trader.name,
                    signal=HitchhikerSignal.INCREASE,
                    confidence=confidence,
                    action="increase",
                    amount=self.allocation_per_trader,
                    reason=f"盈利强劲, 增加跟单",
                    expected_return=expected_return,
                    timestamp=datetime.now()
                )
            else:
                return HitchhikerOpportunity(
                    trader_id=trader.id,
                    trader_name=trader.name,
                    signal=HitchhikerSignal.COPY,
                    confidence=confidence,
                    action="start",
                    amount=self.allocation_per_trader,
                    reason=f"胜率{trader.win_rate*100:.0f}%, 跟单",
                    expected_return=expected_return,
                    timestamp=datetime.now()
                )
        
        elif trader.recent_pnl < -500:
            # 最近亏损
            if trader.id in self.following:
                return HitchhikerOpportunity(
                    trader_id=trader.id,
                    trader_name=trader.name,
                    signal=HitchhikerSignal.STOP,
                    confidence=7.0,
                    action="stop",
                    amount=0,
                    reason=f"近期亏损${abs(trader.recent_pnl):.0f}",
                    expected_return=-0.2,
                    timestamp=datetime.now()
                )
        
        return None
    
    def start_following(self, trader_id: str, amount: float) -> bool:
        """开始跟单"""
        if trader_id not in self.traders:
            return False
        
        self.following[trader_id] = {
            'amount': amount,
            'entry_pnl': 0,
            'start_time': datetime.now(),
            'trades_copied': 0
        }
        
        logger.info(f"开始跟单交易员: {self.traders[trader_id].name}, 金额: ${amount}")
        return True
    
    def stop_following(self, trader_id: str) -> bool:
        """停止跟单"""
        if trader_id in self.following:
            del self.following[trader_id]
            logger.info(f"停止跟单交易员: {trader_id}")
            return True
        return False
    
    def record_copy_trade(self, trader_id: str, trade: Dict):
        """记录跟单交易"""
        self.copy_trades[trader_id].append({
            **trade,
            'copied_at': datetime.now()
        })
        
        # 更新跟单信息
        if trader_id in self.following:
            self.following[trader_id]['trades_copied'] += 1
    
    def calculate_total_allocation(self) -> float:
        """计算总跟单金额"""
        return sum(f['amount'] for f in self.following.values())
    
    def get_best_traders(self, limit: int = 10) -> List[Dict]:
        """获取最佳交易员"""
        sorted_traders = sorted(
            self.traders.values(),
            key=lambda t: (t.win_rate, t.recent_pnl),
            reverse=True
        )
        
        return [
            {
                "id": t.id,
                "name": t.name,
                "win_rate": f"{t.win_rate*100:.1f}%",
                "recent_pnl": f"${t.recent_pnl:.0f}",
                "max_drawdown": f"{t.max_drawdown*100:.1f}%",
                "following": t.id in self.following
            }
            for t in sorted_traders[:limit]
        ]
    
    def get_status(self) -> Dict:
        return {
            "strategy": "hitchhiker",
            "name": "搭便车",
            "description": "跟单分成 - 跟随盈利交易员",
            "traders_tracking": len(self.traders),
            "following": len(self.following),
            "total_allocation": self.calculate_total_allocation(),
            "config": {
                "min_win_rate": self.min_win_rate * 100,
                "max_drawdown": self.max_drawdown_threshold * 100,
                "allocation_per_trader": self.allocation_per_trader * 100
            }
        }


hitchhiker_strategy = HitchhikerStrategy()
