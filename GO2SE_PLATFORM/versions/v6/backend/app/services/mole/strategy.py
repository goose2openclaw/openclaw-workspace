#!/usr/bin/env python3
"""
🪿 打地鼠策略 - 被动等待机会
专门做市值20名之后的所有币种
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)


class MoleSignal(Enum):
    """打地鼠信号"""
    WHACK = "whack"        # 敲打（买入机会）
    WAIT = "wait"          # 等待
    HIDDEN = "hidden"     # 躲藏（卖出）


@dataclass
class MoleConfig:
    """打地鼠配置"""
    # 目标币种 - 除前20外的所有币
    excluded_symbols: List[str] = None
    
    # 交易参数
    min_trade_amount: float = 10         # 较小交易额
    max_position_pct: float = 0.15       # 较小仓位15%
    
    # 机会检测
    min_volume: float = 100000           # 最小成交量
    price_change_threshold: float = 5.0   # 价格变动阈值%
    
    # 反弹检测
    rebound_threshold: float = -10.0      # 下跌多少后反弹
    rebound_confirm_bars: int = 2        # 确认K线数
    
    # 止损止盈
    stop_loss_pct: float = 0.08           # 宽止损8%
    take_profit_pct: float = 0.20         # 宽止盈20%
    
    # 扫描参数
    scan_interval: int = 120              # 扫描间隔(秒) - 较慢
    max_symbols: int = 100                # 最多监控数量
    
    def __post_init__(self):
        if self.excluded_symbols is None:
            self.excluded_symbols = [
                "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
                "ADAUSDT", "AVAXUSDT", "DOTUSDT", "MATICUSDT", "LINKUSDT",
                "UNIUSDT", "ATOMUSDT", "LTCUSDT", "BCHUSDT", "XLMUSDT",
                "ALGOUSDT", "VETUSDT", "FILUSDT", "THETAUSDT", "AAVEUSDT"
            ]


@dataclass
class MoleOpportunity:
    """打地鼠机会"""
    symbol: str
    signal: MoleSignal
    confidence: float
    entry_price: float
    stop_loss: float
    take_profit: float
    position_size: float
    reason: str
    indicators: Dict[str, float]
    timestamp: datetime
    reaction_time: Optional[datetime]  # 敲打时机


@dataclass  
class MoleResult:
    """打地鼠扫描结果"""
    opportunities: List[MoleOpportunity]
    scanned_count: int
    whacked_count: int
    timestamp: datetime
    active_holes: List[str]  # 活跃的"鼠洞"


class MoleStrategy:
    """打地鼠策略引擎"""
    
    def __init__(self, config: MoleConfig = None):
        self.config = config or MoleConfig()
        self.positions: Dict[str, Dict] = {}
        self.watch_list: List[str] = []  # 观察列表
        self.active_holes: Dict[str, Dict] = {}  # 活跃鼠洞（价格区间）
        self.history: List[MoleOpportunity] = []
    
    async def scan_market(
        self,
        market_data: Dict[str, Dict]
    ) -> MoleResult:
        """扫描市场找机会"""
        opportunities = []
        scanned = 0
        whacked = 0
        
        # 过滤掉前20币种
        valid_symbols = [
            s for s in market_data.keys()
            if s not in self.config.excluded_symbols
        ][:self.config.max_symbols]
        
        for symbol in valid_symbols:
            scanned += 1
            data = market_data[symbol]
            
            # 检查是否活跃鼠洞
            if symbol in self.active_holes:
                opp = self.check_hole(symbol, data)
                if opp:
                    opportunities.append(opp)
                    whacked += 1
            else:
                # 检查是否形成新鼠洞
                opp = self.detect_new_hole(symbol, data)
                if opp:
                    opportunities.append(opp)
        
        # 按置信度排序
        opportunities.sort(key=lambda x: x.confidence, reverse=True)
        
        return MoleResult(
            opportunities=opportunities,
            scanned_count=scanned,
            whacked_count=whacked,
            timestamp=datetime.now(),
            active_holes=list(self.active_holes.keys())
        )
    
    def detect_new_hole(
        self,
        symbol: str,
        data: Dict
    ) -> Optional[MoleOpportunity]:
        """检测新鼠洞（潜在机会）"""
        
        price = data.get('price', 0)
        change_24h = data.get('change_24h', 0)
        volume = data.get('volume', 0)
        
        # 检查成交量
        if volume < self.config.min_volume:
            return None
        
        # 检测大跌后反弹（鼠洞形成）
        if change_24h < self.config.rebound_threshold:
            # 可能形成鼠洞，加入观察
            self.active_holes[symbol] = {
                'high_price': price,
                'low_price': price * 0.9,
                'detected_at': datetime.now(),
                'change_24h': change_24h
            }
            
            return MoleOpportunity(
                symbol=symbol,
                signal=MoleSignal.WAIT,
                confidence=6.0,
                entry_price=price,
                stop_loss=price * (1 - self.config.stop_loss_pct),
                take_profit=price * (1 + self.config.take_profit_pct),
                position_size=0.10,
                reason=f"检测到鼠洞形成: 24h下跌{change_24h:.1f}%",
                indicators={
                    'change_24h': change_24h,
                    'volume': volume
                },
                timestamp=datetime.now(),
                reaction_time=None
            )
        
        return None
    
    def check_hole(
        self,
        symbol: str,
        data: Dict
    ) -> Optional[MoleOpportunity]:
        """检查活跃鼠洞（敲打时机）"""
        
        hole = self.active_holes[symbol]
        current_price = data.get('price', 0)
        
        if current_price == 0:
            return None
        
        # 检查是否到了鼠洞底部（反弹点）
        low_price = hole.get('low_price', current_price * 0.9)
        
        # 价格到达底部区域
        if current_price <= low_price * 1.05:  # 5%误差范围内
            
            # 计算反弹概率
            confidence = self.calculate_rebound_confidence(symbol, data, hole)
            
            if confidence >= 5:
                # 敲打！（买入）
                stop_loss = current_price * (1 - self.config.stop_loss_pct)
                take_profit = current_price * (1 + self.config.take_profit_pct)
                
                opp = MoleOpportunity(
                    symbol=symbol,
                    signal=MoleSignal.WHACK,
                    confidence=confidence,
                    entry_price=current_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    position_size=self.calculate_position_size(confidence),
                    reason=f"鼠洞敲打! 价格触底反弹区间",
                    indicators={
                        'entry_price': current_price,
                        'low_price': low_price,
                        'depth_pct': hole.get('change_24h', 0)
                    },
                    timestamp=datetime.now(),
                    reaction_time=datetime.now()
                )
                
                # 敲打后移除鼠洞（机会已捕捉）
                del self.active_holes[symbol]
                
                return opp
        
        # 检查鼠洞是否失效（太久没动静）
        detected_at = hole.get('detected_at')
        if detected_at:
            age = (datetime.now() - detected_at).total_seconds()
            if age > 3600:  # 1小时无动静
                del self.active_holes[symbol]
        
        return None
    
    def calculate_rebound_confidence(
        self,
        symbol: str,
        data: Dict,
        hole: Dict
    ) -> float:
        """计算反弹置信度"""
        score = 5.0
        
        # 深度调整
        depth = abs(hole.get('change_24h', 0))
        if depth >= 20:
            score += 2
        elif depth >= 15:
            score += 1.5
        elif depth >= 10:
            score += 1
        
        # RSI超卖
        rsi = data.get('rsi', 50)
        if rsi < 25:
            score += 2
        elif rsi < 30:
            score += 1
        
        # 成交量
        volume = data.get('volume', 0)
        avg_volume = data.get('avg_volume', volume)
        if avg_volume > 0 and volume > avg_volume * 1.5:
            score += 1
        
        return min(10, score)
    
    def calculate_position_size(self, confidence: float) -> float:
        """计算仓位大小 - 打地鼠仓位较小"""
        base_size = (confidence / 10) * self.config.max_position_pct
        return min(self.config.max_position_pct, max(0.02, base_size * 0.8))
    
    def should_exit(
        self,
        symbol: str,
        current_price: float
    ) -> Tuple[bool, str]:
        """判断是否出场"""
        
        if symbol not in self.positions:
            return False, "无持仓"
        
        pos = self.positions[symbol]
        entry_price = pos['entry_price']
        
        # 止损
        stop_loss = pos.get('stop_loss')
        if stop_loss and current_price <= stop_loss:
            return True, "止损"
        
        # 止盈
        take_profit = pos.get('take_profit')
        if take_profit and current_price >= take_profit:
            return True, "止盈"
        
        # 持仓时间过久
        entry_time = pos.get('entry_time')
        if entry_time:
            holding_hours = (datetime.now() - entry_time).total_seconds() / 3600
            if holding_hours > 24:  # 超过24小时
                return True, "超时退出"
        
        return False, ""
    
    def update_position(
        self,
        symbol: str,
        action: str,
        price: float,
        amount: float = 0
    ):
        """更新持仓"""
        
        if action == "entry":
            self.positions[symbol] = {
                'entry_price': price,
                'amount': amount,
                'stop_loss': price * (1 - self.config.stop_loss_pct),
                'take_profit': price * (1 + self.config.take_profit_pct),
                'entry_time': datetime.now()
            }
        elif action == "exit":
            if symbol in self.positions:
                del self.positions[symbol]
    
    def get_status(self) -> Dict:
        """获取策略状态"""
        return {
            "strategy": "mole",
            "name": "打地鼠",
            "description": "被动等待机会 - 市值20名后所有币",
            "watching_count": len(self.watch_list),
            "active_holes_count": len(self.active_holes),
            "current_positions": len(self.positions),
            "config": {
                "max_position_pct": self.config.max_position_pct,
                "stop_loss_pct": self.config.stop_loss_pct,
                "take_profit_pct": self.config.take_profit_pct,
                "rebound_threshold": self.config.rebound_threshold,
                "scan_interval": self.config.scan_interval,
            }
        }
    
    def get_active_holes_summary(self) -> List[Dict]:
        """获取活跃鼠洞摘要"""
        return [
            {
                "symbol": symbol,
                "detected_at": info.get('detected_at').isoformat() if info.get('detected_at') else None,
                "change_24h": info.get('change_24h'),
                "age_seconds": (datetime.now() - info.get('detected_at', datetime.now())).total_seconds()
            }
            for symbol, info in self.active_holes.items()
        ]


# 全局实例
mole_strategy = MoleStrategy()
