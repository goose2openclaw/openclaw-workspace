#!/usr/bin/env python3
"""
🪿 打兔子策略 - 主动发现并捕捉市场机会
专门做市值前20的主流币
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import numpy as np
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class RabbitSignal(Enum):
    """打兔子信号"""
    STRONG_BUY = "strong_buy"    # 强烈买入
    BUY = "buy"                   # 买入
    HOLD = "hold"                 # 持有
    SELL = "sell"                # 卖出
    STRONG_SELL = "strong_sell"  # 强烈卖出


@dataclass
class RabbitConfig:
    """打兔子配置"""
    # 目标币种 - 市值前20
    symbols: List[str] = None
    
    # 交易参数
    min_trade_amount: float = 100        # 最小交易额
    max_position_pct: float = 0.20       # 最大仓位20%
    
    # 趋势参数
    strong_trend_threshold: float = 7.5   # 强趋势阈值
    volume_spike_ratio: float = 2.0       # 成交量暴增比例
    
    # 止损止盈
    stop_loss_pct: float = 0.05          # 止损5%
    take_profit_pct: float = 0.15        # 止盈15%
    trailing_stop_pct: float = 0.03       # 追踪止损3%
    
    # 检测参数
    scan_interval: int = 60               # 扫描间隔(秒)
    rsi_oversold: float = 30             # RSI超卖
    rsi_overbought: float = 70            # RSI超买
    
    # 确认参数
    confirmation_bars: int = 3            # 确认K线数
    
    def __post_init__(self):
        if self.symbols is None:
            self.symbols = self.get_default_symbols()
    
    @staticmethod
    def get_default_symbols() -> List[str]:
        """默认市值前20币种"""
        return [
            "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
            "ADAUSDT", "AVAXUSDT", "DOTUSDT", "MATICUSDT", "LINKUSDT",
            "UNIUSDT", "ATOMUSDT", "LTCUSDT", "BCHUSDT", "XLMUSDT",
            "ALGOUSDT", "VETUSDT", "FILUSDT", "THETAUSDT", "AAVEUSDT"
        ]


@dataclass
class RabbitOpportunity:
    """打兔子机会"""
    symbol: str
    signal: RabbitSignal
    confidence: float          # 0-10
    entry_price: float
    stop_loss: float
    take_profit: float
    position_size: float      # 仓位比例
    reason: str
    indicators: Dict[str, float]  # 技术指标
    timestamp: datetime


@dataclass
class RabbitResult:
    """打兔子结果"""
    opportunities: List[RabbitOpportunity]
    scanned_count: int
    timestamp: datetime
    market_summary: Dict[str, Any]


class RabbitStrategy:
    """打兔子策略引擎"""
    
    # 默认配置
    DEFAULT_SYMBOLS = RabbitConfig.get_default_symbols()
    
    def __init__(self, config: RabbitConfig = None):
        self.config = config or RabbitConfig()
        self.positions: Dict[str, Dict] = {}  # symbol -> position info
        self.history: List[RabbitOpportunity] = []
    
    async def scan_market(
        self,
        market_data: Dict[str, Dict]
    ) -> RabbitResult:
        """扫描市场找机会"""
        opportunities = []
        scanned = 0
        
        for symbol in self.config.symbols:
            if symbol not in market_data:
                continue
            
            scanned += 1
            data = market_data[symbol]
            
            # 分析机会
            opp = self.analyze_opportunity(symbol, data)
            if opp and opp.signal in [RabbitSignal.STRONG_BUY, RabbitSignal.BUY]:
                opportunities.append(opp)
        
        # 按置信度排序
        opportunities.sort(key=lambda x: x.confidence, reverse=True)
        
        # 生成市场摘要
        summary = self.generate_summary(opportunities)
        
        return RabbitResult(
            opportunities=opportunities,
            scanned_count=scanned,
            timestamp=datetime.now(),
            market_summary=summary
        )
    
    def analyze_opportunity(
        self,
        symbol: str,
        data: Dict
    ) -> Optional[RabbitOpportunity]:
        """分析单个币种机会"""
        
        # 提取数据
        price = data.get('price', 0)
        change_24h = data.get('change_24h', 0)
        volume = data.get('volume', 0)
        avg_volume = data.get('avg_volume', volume)
        rsi = data.get('rsi', 50)
        macd = data.get('macd', 0)
        signal_line = data.get('signal_line', 0)
        ema_20 = data.get('ema_20', price)
        ema_50 = data.get('ema_50', price)
        
        # 计算趋势强度
        trend_score = self.calculate_trend_score(
            price, change_24h, ema_20, ema_50
        )
        
        # 计算动量
        momentum_score = self.calculate_momentum(
            rsi, macd, signal_line
        )
        
        # 计算成交量信号
        volume_signal = self.calculate_volume_signal(
            volume, avg_volume
        )
        
        # 综合评分
        confidence = (trend_score * 0.4 + momentum_score * 0.4 + volume_signal * 0.2)
        
        # 确定信号
        signal, reason = self.determine_signal(
            confidence, trend_score, rsi, volume_signal
        )
        
        if signal == RabbitSignal.HOLD:
            return None
        
        # 计算止损止盈
        stop_loss, take_profit = self.calculate_stop_loss_take_profit(
            price, signal
        )
        
        # 计算仓位
        position_size = self.calculate_position_size(confidence)
        
        return RabbitOpportunity(
            symbol=symbol,
            signal=signal,
            confidence=confidence,
            entry_price=price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            position_size=position_size,
            reason=reason,
            indicators={
                'trend_score': trend_score,
                'momentum_score': momentum_score,
                'volume_signal': volume_signal,
                'rsi': rsi,
                'change_24h': change_24h,
            },
            timestamp=datetime.now()
        )
    
    def calculate_trend_score(
        self,
        price: float,
        change_24h: float,
        ema_20: float,
        ema_50: float
    ) -> float:
        """计算趋势得分"""
        score = 5.0
        
        # 24h涨跌幅
        if change_24h > 5:
            score += 2
        elif change_24h > 2:
            score += 1
        elif change_24h < -5:
            score -= 2
        elif change_24h < -2:
            score -= 1
        
        # EMA均线
        if ema_20 > ema_50:  # 多头排列
            score += 1.5
        elif ema_20 < ema_50:  # 空头排列
            score -= 1.5
        
        # 价格位置
        if price > ema_20:
            score += 1
        
        return max(0, min(10, score))
    
    def calculate_momentum(
        self,
        rsi: float,
        macd: float,
        signal_line: float
    ) -> float:
        """计算动量得分"""
        score = 5.0
        
        # RSI
        if rsi < self.config.rsi_oversold:
            score += 2  # 超卖，可能反弹
        elif rsi > self.config.rsi_overbought:
            score -= 2  # 超买，可能回调
        elif rsi < 40:
            score += 1
        elif rsi > 60:
            score -= 1
        
        # MACD
        if macd > signal_line and macd > 0:
            score += 1.5
        elif macd < signal_line and macd < 0:
            score -= 1.5
        
        return max(0, min(10, score))
    
    def calculate_volume_signal(
        self,
        volume: float,
        avg_volume: float
    ) -> float:
        """计算成交量信号"""
        if avg_volume == 0:
            return 5.0
        
        ratio = volume / avg_volume
        
        if ratio >= self.config.volume_spike_ratio:
            return 8.0  # 成交量暴增
        elif ratio >= 1.5:
            return 6.0
        elif ratio >= 1.0:
            return 5.0
        else:
            return 4.0
    
    def determine_signal(
        self,
        confidence: float,
        trend_score: float,
        rsi: float,
        volume_signal: float
    ) -> Tuple[RabbitSignal, str]:
        """确定交易信号"""
        
        # 强买入条件
        if (confidence >= 8 and trend_score >= 7 and 
            volume_signal >= 6 and rsi < 65):
            return RabbitSignal.STRONG_BUY, f"强趋势+高动量+成交量确认 (置信度:{confidence:.1f})"
        
        # 买入条件
        if confidence >= 6 and trend_score >= 5:
            if rsi < 30:
                return RabbitSignal.BUY, f"RSI超卖反弹 (RSI:{rsi:.1f})"
            elif rsi > 70:
                return RabbitSignal.HOLD, "RSI超买，观望"
            return RabbitSignal.BUY, f"趋势向好 (置信度:{confidence:.1f})"
        
        # 强卖出条件
        if confidence <= 3 and trend_score <= 3 and rsi >= 70:
            return RabbitSignal.STRONG_SELL, "趋势转弱+RSI超买"
        
        # 卖出条件
        if confidence <= 4 and trend_score <= 4:
            return RabbitSignal.SELL, f"趋势向淡 (置信度:{confidence:.1f})"
        
        return RabbitSignal.HOLD, "趋势不明显"
    
    def calculate_stop_loss_take_profit(
        self,
        price: float,
        signal: RabbitSignal
    ) -> Tuple[float, float]:
        """计算止损止盈"""
        
        if signal in [RabbitSignal.STRONG_BUY, RabbitSignal.BUY]:
            # 买入方向
            stop_loss = price * (1 - self.config.stop_loss_pct)
            take_profit = price * (1 + self.config.take_profit_pct)
        else:
            # 卖出方向
            stop_loss = price * (1 + self.config.stop_loss_pct)
            take_profit = price * (1 - self.config.take_profit_pct)
        
        return stop_loss, take_profit
    
    def calculate_position_size(self, confidence: float) -> float:
        """计算仓位大小"""
        # 基础仓位
        base_size = (confidence / 10) * self.config.max_position_pct
        
        # 置信度调整
        if confidence >= 8:
            base_size *= 1.0   # 满仓
        elif confidence >= 7:
            base_size *= 0.8
        elif confidence >= 6:
            base_size *= 0.6
        else:
            base_size *= 0.4
        
        return min(self.config.max_position_pct, max(0.02, base_size))
    
    def generate_summary(
        self,
        opportunities: List[RabbitOpportunity]
    ) -> Dict[str, Any]:
        """生成市场摘要"""
        
        buy_signals = [o for o in opportunities if o.signal == RabbitSignal.BUY]
        strong_buy = [o for o in opportunities if o.signal == RabbitSignal.STRONG_BUY]
        
        return {
            "total_opportunities": len(opportunities),
            "strong_buy_count": len(strong_buy),
            "buy_count": len(buy_signals),
            "top_opportunities": [
                {
                    "symbol": o.symbol,
                    "signal": o.signal.value,
                    "confidence": o.confidence,
                    "reason": o.reason
                }
                for o in opportunities[:5]
            ]
        }
    
    def should_enter(
        self,
        symbol: str,
        opportunity: RabbitOpportunity
    ) -> bool:
        """判断是否入场"""
        
        # 已持仓不入场
        if symbol in self.positions:
            return False
        
        # 信号必须是买入
        if opportunity.signal not in [RabbitSignal.BUY, RabbitSignal.STRONG_BUY]:
            return False
        
        # 置信度必须足够
        if opportunity.confidence < 5:
            return False
        
        return True
    
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
        stop_loss = pos['stop_loss']
        take_profit = pos['take_profit']
        
        # 止损
        if current_price <= stop_loss:
            return True, "触发止损"
        
        # 止盈
        if current_price >= take_profit:
            return True, "触发止盈"
        
        # 追踪止损
        profit_pct = (current_price - entry_price) / entry_price
        if profit_pct >= 0.10:  # 已有10%利润
            # 检查是否回落
            trailing_stop = entry_price * (1 + self.config.trailing_stop_pct)
            if current_price < trailing_stop:
                return True, "追踪止损"
        
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
            "strategy": "rabbit",
            "name": "打兔子",
            "description": "主动发现并捕捉市场机会 - 市值前20主流币",
            "symbols_count": len(self.config.symbols),
            "current_positions": len(self.positions),
            "config": {
                "max_position_pct": self.config.max_position_pct,
                "stop_loss_pct": self.config.stop_loss_pct,
                "take_profit_pct": self.config.take_profit_pct,
                "strong_trend_threshold": self.config.strong_trend_threshold,
            }
        }


# 全局实例
rabbit_strategy = RabbitStrategy()
