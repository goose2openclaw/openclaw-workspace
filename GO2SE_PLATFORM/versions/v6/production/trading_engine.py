#!/usr/bin/env python3
"""
🪿 GO2SE 交易引擎
高频量化交易核心 - 支持7×24小时运行
"""

import asyncio
import ccxt
import aiohttp
import asyncpg
import redis.asyncio as aioredis
import json
import logging
import signal
import sys
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum

# ═══════════════════════════════════════════════════════════════════════════════
# 配置
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Config:
    """交易配置"""
    # 数据库
    database_url: str = "postgresql+asyncpg://go2se:password@postgres:5432/go2se_trading"
    redis_url: str = "redis://redis:6379/0"
    
    # 交易参数
    trading_mode: str = "dry_run"  # dry_run 或 live
    max_position: float = 0.6      # 最大仓位60%
    stop_loss: float = 0.10       # 止损10%
    take_profit: float = 0.30    # 止盈30%
    
    # API
    binance_api_key: str = ""
    binance_secret_key: str = ""
    rate_limit: int = 1200        # 每分钟
    
    # 策略
    trading_pairs: List[str] = field(default_factory=lambda: [
        "BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "BNB/USDT",
        "ADA/USDT", "DOGE/USDT", "DOT/USDT", "AVAX/USDT", "LINK/USDT"
    ])
    
    # 缓存
    cache_ttl_price: int = 5
    cache_ttl_ohlcv: int = 30


# ═══════════════════════════════════════════════════════════════════════════════
# 核心交易引擎
# ═══════════════════════════════════════════════════════════════════════════════

class TradingEngine:
    """高频交易引擎"""
    
    def __init__(self, config: Config):
        self.config = config
        self.exchange: Optional[ccxt.binance] = None
        self.db: Optional[asyncpg.Pool] = None
        self.redis: Optional[aioredis.Redis] = None
        self.running = False
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        """设置日志"""
        logger = logging.getLogger("go2se")
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    async def initialize(self):
        """初始化"""
        self.logger.info("🪿 GO2SE 交易引擎启动中...")
        
        # 1. 连接数据库
        self.db = await asyncpg.create_pool(
            self.config.database_url,
            min_size=2,
            max_size=10
        )
        self.logger.info("✅ 数据库连接成功")
        
        # 2. 连接Redis
        self.redis = await aioredis.from_url(
            self.config.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
        self.logger.info("✅ Redis连接成功")
        
        # 3. 初始化交易所
        self.exchange = ccxt.binance({
            'apiKey': self.config.binance_api_key,
            'secret': self.config.binance_secret_key,
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        
        # 测试API
        try:
            await self.exchange.fetch_balance()
            self.logger.info("✅ 币安API连接成功")
        except Exception as e:
            self.logger.warning(f⚠️ 币安API测试失败: {e} (dry_run模式)")
        
        self.logger.info("🪿 GO2SE 初始化完成!")
    
    async def close(self):
        """关闭连接"""
        if self.db:
            await self.db.close()
        if self.redis:
            await self.redis.close()
        self.logger.info("🔴 交易引擎已关闭")
    
    async def health_check(self) -> Dict:
        """健康检查"""
        health = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {}
        }
        
        # 检查数据库
        try:
            async with self.db.acquire() as conn:
                await conn.fetchval("SELECT 1")
            health["components"]["database"] = "ok"
        except Exception as e:
            health["components"]["database"] = f"error: {e}"
            health["status"] = "degraded"
        
        # 检查Redis
        try:
            await self.redis.ping()
            health["components"]["redis"] = "ok"
        except Exception as e:
            health["components"]["redis"] = f"error: {e}"
            health["status"] = "degraded"
        
        # 检查交易所API
        try:
            await self.exchange.fetch_time()
            health["components"]["exchange"] = "ok"
        except Exception as e:
            health["components"]["exchange"] = f"error: {e}"
        
        return health
    
    async def get_market_data(self, symbol: str) -> Dict:
        """获取市场数据 (带缓存)"""
        cache_key = f"market:{symbol}"
        
        # 尝试从缓存获取
        cached = await self.redis.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # 获取实时数据
        ticker = await self.exchange.fetch_ticker(symbol)
        order_book = await self.exchange.fetch_order_book(symbol, limit=20)
        
        data = {
            "symbol": symbol,
            "price": ticker['last'],
            "bid": ticker.get('bid', 0),
            "ask": ticker.get('ask', 0),
            "volume_24h": ticker.get('quoteVolume', 0),
            "change_24h": ticker.get('percentage', 0),
            "high": ticker.get('high', 0),
            "low": ticker.get('low', 0),
            "order_book_bids": order_book['bids'][:10],
            "order_book_asks": order_book['asks'][:10],
            "timestamp": datetime.now().isoformat()
        }
        
        # 缓存
        await self.redis.setex(
            cache_key,
            self.config.cache_ttl_price,
            json.dumps(data)
        )
        
        return data
    
    async def execute_trade(self, symbol: str, side: str, amount: float) -> Dict:
        """执行交易"""
        if self.config.trading_mode == "dry_run":
            self.logger.info(f"🔍 [模拟] {side.upper()} {amount} {symbol}")
            return {
                "status": "simulated",
                "side": side,
                "symbol": symbol,
                "amount": amount,
                "mode": "dry_run"
            }
        
        # 实盘交易
        try:
            if side == "buy":
                order = await self.exchange.create_order(
                    symbol, 'market', 'buy', amount
                )
            else:
                order = await self.exchange.create_order(
                    symbol, 'market', 'sell', amount
                )
            
            self.logger.info(f"✅ 实盘成交: {side.upper()} {amount} {symbol}")
            
            # 记录到数据库
            await self.record_trade(order)
            
            return {
                "status": "success",
                "order": order
            }
        except Exception as e:
            self.logger.error(f"❌ 交易失败: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def record_trade(self, order: Dict):
        """记录交易到数据库"""
        async with self.db.acquire() as conn:
            await conn.execute("""
                INSERT INTO trades (order_id, symbol, side, amount, price, status, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """, 
                order.get('id'),
                order.get('symbol'),
                order.get('side'),
                order.get('amount'),
                order.get('price'),
                order.get('status'),
                datetime.now()
            )
    
    async def check_positions(self) -> List[Dict]:
        """检查当前持仓"""
        if self.config.trading_mode == "dry_run":
            # 模拟持仓
            return []
        
        try:
            balance = await self.exchange.fetch_balance()
            positions = []
            
            for symbol in self.config.trading_pairs:
                base = symbol.split('/')[0]
                if balance['free'].get(base, 0) > 0:
                    positions.append({
                        "symbol": symbol,
                        "amount": balance['free'][base],
                        "value": balance['free'][base] * balance['total'][base + '/USDT']
                    })
            
            return positions
        except Exception as e:
            self.logger.error(f"❌ 获取持仓失败: {e}")
            return []
    
    async def run_strategy(self, strategy_name: str, symbols: List[str]):
        """运行策略"""
        self.logger.info(f"📊 运行策略: {strategy_name}")
        
        signals = []
        
        for symbol in symbols:
            try:
                data = await self.get_market_data(symbol)
                
                # 简单策略: RSI超卖买入
                rsi = await self.calculate_rsi(symbol)
                
                if rsi < 30:
                    signals.append({
                        "symbol": symbol,
                        "action": "buy",
                        "confidence": (30 - rsi) / 30,
                        "reason": f"RSI超卖: {rsi:.2f}"
                    })
                elif rsi > 70:
                    signals.append({
                        "symbol": symbol,
                        "action": "sell",
                        "confidence": (rsi - 70) / 30,
                        "reason": f"RSI超买: {rsi:.2f}"
                    })
                    
            except Exception as e:
                self.logger.error(f"⚠️ {symbol} 分析失败: {e}")
        
        # 执行信号
        for signal in signals:
            if signal['confidence'] > 0.5:
                self.logger.info(f"🎯 信号: {signal}")
                # 这里调用 execute_trade
    
    async def calculate_rsi(self, symbol: str, period: int = 14) -> float:
        """计算RSI"""
        ohlcv = await self.exchange.fetch_ohlcv(
            symbol, '1h', limit=period + 1
        )
        
        closes = [c[4] for c in ohlcv]
        deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
        
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    async def start(self):
        """启动引擎"""
        self.running = True
        self.logger.info("🚀 GO2SE 交易引擎运行中...")
        
        while self.running:
            try:
                # 运行策略
                await self.run_strategy("mole", self.config.trading_pairs[:5])
                
                # 检查持仓和风控
                positions = await self.check_positions()
                
                # 每60秒运行一次
                await asyncio.sleep(60)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ 引擎错误: {e}")
                await asyncio.sleep(10)
        
    def stop(self):
        """停止引擎"""
        self.running = False
        self.logger.info("🛑 交易引擎停止中...")


# ═══════════════════════════════════════════════════════════════════════════════
# 主程序
# ═══════════════════════════════════════════════════════════════════════════════

async def main():
    # 加载配置
    config = Config(
        database_url="postgresql+asyncpg://go2se:change_me_in_production@postgres:5432/go2se_trading",
        redis_url="redis://redis:6379/0",
        trading_mode="dry_run",
        binance_api_key="",
        binance_secret_key=""
    )
    
    # 创建引擎
    engine = TradingEngine(config)
    
    # 信号处理
    def signal_handler(sig, frame):
        engine.stop()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 初始化
    await engine.initialize()
    
    # 启动
    try:
        await engine.start()
    finally:
        await engine.close()


if __name__ == "__main__":
    asyncio.run(main())
