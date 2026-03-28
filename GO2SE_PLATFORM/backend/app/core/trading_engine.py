#!/usr/bin/env python3
"""
🪿 GO2SE 交易引擎
整合7大策略 + 风控系统
"""

import ccxt
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

from app.core.config import settings


logger = logging.getLogger("go2se.engine")


@dataclass
class MarketTick:
    """市场数据"""
    symbol: str
    price: float
    bid: float
    ask: float
    volume_24h: float
    change_24h: float
    high_24h: float
    low_24h: float
    rsi: float = 50.0


class TradingEngine:
    """交易引擎"""
    
    def __init__(self):
        self.exchange: Optional[ccxt.binance] = None
        self.running = False
        
    def init_exchange(self):
        """初始化交易所连接"""
        self.exchange = ccxt.binance({
            'apiKey': settings.BINANCE_API_KEY,
            'secret': settings.BINANCE_SECRET_KEY,
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        logger.info("✅ 交易所连接初始化")
    
    async def get_market_data(self, symbol: str) -> MarketTick:
        """获取市场数据 - 使用线程池避免阻塞"""
        if not self.exchange:
            self.init_exchange()
        
        # 在线程池中执行同步的 ccxt 调用，避免阻塞事件循环
        ticker = await asyncio.to_thread(self.exchange.fetch_ticker, symbol)
        
        # 计算RSI
        ohlcv = await asyncio.to_thread(self.exchange.fetch_ohlcv, symbol, '1h', limit=50)
        rsi = self._calculate_rsi([c[4] for c in ohlcv])
        
        return MarketTick(
            symbol=symbol,
            price=ticker['last'],
            bid=ticker.get('bid', 0),
            ask=ticker.get('ask', 0),
            volume_24h=ticker.get('quoteVolume', 0),
            change_24h=ticker.get('percentage', 0),
            high_24h=ticker.get('high', 0),
            low_24h=ticker.get('low', 0),
            rsi=rsi
        )
    
    def _calculate_rsi(self, closes: List[float], period: int = 14) -> float:
        """计算RSI"""
        if len(closes) < period + 1:
            return 50.0
        
        deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
        gains = [d if d > 0 else 0 for d in deltas[-period:]]
        losses = [-d if d < 0 else 0 for d in deltas[-period:]]
        
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    def generate_signal(self, tick: MarketTick) -> Dict:
        """生成交易信号"""
        rsi = tick.rsi
        change = tick.change_24h
        
        # 简单RSI策略
        if rsi < 30:
            signal = "buy"
            confidence = min(10, (30 - rsi) / 30 * 10 + 5)
            reason = f"RSI超卖: {rsi:.1f}"
        elif rsi > 70:
            signal = "sell"
            confidence = min(10, (rsi - 70) / 30 * 10 + 5)
            reason = f"RSI超买: {rsi:.1f}"
        else:
            signal = "hold"
            confidence = 5
            reason = f"RSI中性: {rsi:.1f}"
        
        return {
            "symbol": tick.symbol,
            "signal": signal,
            "confidence": confidence,
            "price": tick.price,
            "rsi": rsi,
            "change_24h": change,
            "reason": reason
        }
    
    async def execute_trade(self, signal: Dict) -> Dict:
        """执行交易"""
        if settings.TRADING_MODE == "dry_run":
            logger.info(f"🔍 [模拟] {signal['signal'].upper()} {signal['symbol']}")
            return {
                "status": "simulated",
                "mode": "dry_run",
                "signal": signal
            }
        
        # 实盘交易
        try:
            order = self.exchange.create_order(
                symbol=signal['symbol'],
                type='market',
                side=signal['signal'],
                amount=0.001  # 小额测试
            )
            logger.info(f"✅ 实盘成交: {signal['signal']} {signal['symbol']}")
            return {
                "status": "success",
                "order": order
            }
        except Exception as e:
            logger.error(f"❌ 交易失败: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def run_strategy(self, strategy_name: str, symbols: List[str]) -> List[Dict]:
        """运行策略"""
        signals = []
        
        for symbol in symbols:
            try:
                tick = await self.get_market_data(symbol)
                signal = self.generate_signal(tick)
                signal["strategy"] = strategy_name
                signals.append(signal)
            except Exception as e:
                logger.error(f"⚠️ {symbol} 策略执行失败: {e}")
        
        return signals
    
    async def run_all_strategies(self) -> Dict:
        """运行所有策略"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "strategies": {},
            "all_signals": []
        }
        
        # 按权重运行策略
        strategy_weights = {
            "rabbit": settings.RABBIT_WEIGHT,
            "mole": settings.MOLE_WEIGHT,
            "oracle": settings.ORACLE_WEIGHT,
            "leader": settings.LEADER_WEIGHT,
        }
        
        for strategy, weight in strategy_weights.items():
            if weight > 0:
                signals = await self.run_strategy(
                    strategy, 
                    settings.TRADING_PAIRS[:5]  # 前5个交易对
                )
                results["strategies"][strategy] = {
                    "weight": weight,
                    "signals_count": len(signals),
                    "signals": signals
                }
                results["all_signals"].extend(signals)
        
        return results


# 全局引擎实例
engine = TradingEngine()
