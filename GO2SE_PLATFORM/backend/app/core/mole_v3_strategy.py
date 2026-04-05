#!/usr/bin/env python3
"""
🐹 打地鼠策略 V3 - 高频套利优化版
===================================
性能优化:
- 异步并行API调用
- 本地缓存减少延迟
- 连接池复用
- 优化指标计算
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque
import math

# ==================== 高频配置 ====================

@dataclass
class HFTConfig:
    """高频交易配置"""
    # API配置
    api_timeout: float = 1.0           # API超时(秒)
    max_concurrent_requests: int = 10   # 最大并发请求
    connection_pool_size: int = 20     # 连接池大小
    cache_ttl: float = 0.5            # 缓存TTL(秒)
    
    # 交易配置
    min_spread: float = 0.001         # 最小价差 0.1%
    min_volume: float = 1000000       # 最低成交量
    scan_interval: float = 0.5         # 扫描间隔(秒)
    
    # 风险配置
    max_position: float = 0.04         # 单笔最大仓位 4%
    max_total_position: float = 0.20   # 总仓位上限 20%
    stop_loss: float = 0.02           # 2% 止损
    take_profit: float = 0.05          # 5% 止盈


@dataclass
class ArbitrageOpportunity:
    """套利机会"""
    symbol: str
    buy_exchange: str
    sell_exchange: str
    buy_price: float
    sell_price: float
    spread_pct: float
    volume: float
    confidence: float
    timestamp: float = field(default_factory=time.time)


class RateLimiter:
    """令牌桶限流器"""
    def __init__(self, rate: float, burst: int):
        self.rate = rate
        self.burst = burst
        self.tokens = burst
        self.last_update = time.time()
    
    async def acquire(self) -> bool:
        now = time.time()
        elapsed = now - self.last_update
        self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
        self.last_update = now
        
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False


class PriceCache:
    """价格缓存 - 减少API调用"""
    def __init__(self, ttl: float = 0.5):
        self.ttl = ttl
        self.cache: Dict[str, Tuple[float, float]] = {}  # symbol -> (price, timestamp)
    
    def get(self, symbol: str) -> Optional[float]:
        if symbol in self.cache:
            price, ts = self.cache[symbol]
            if time.time() - ts < self.ttl:
                return price
            del self.cache[symbol]
        return None
    
    def set(self, symbol: str, price: float):
        self.cache[symbol] = (price, time.time())
    
    def invalidate(self, symbol: str):
        if symbol in self.cache:
            del self.cache[symbol]


class ConnectionPool:
    """连接池管理"""
    def __init__(self, max_size: int = 20):
        self.max_size = max_size
        self.semaphore = asyncio.Semaphore(max_size)
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(
                limit=self.max_size,
                keepalive_timeout=30,
                enable_cleanup_closed=True
            )
            timeout = aiohttp.ClientTimeout(total=1.0)
            self._session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        return self._session
    
    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()


class MoleV3Strategy:
    """🐹 打地鼠 V3 - 高频套利优化版"""
    
    VERSION = "v3.0-hft"
    
    def __init__(self, config: Optional[Dict] = None):
        self.name = "🐹 打地鼠V3"
        self.version = self.VERSION
        
        # 高频配置
        self.hft_config = HFTConfig()
        if config:
            self._apply_config(config)
        
        # 核心组件
        self.pool = ConnectionPool(max_size=self.hft_config.connection_pool_size)
        self.cache = PriceCache(ttl=self.hft_config.cache_ttl)
        self.rate_limiter = RateLimiter(rate=100, burst=20)
        
        # 状态
        self.positions: Dict[str, dict] = {}
        self.opportunities: deque = deque(maxlen=100)
        self.stats = {
            "total_scans": 0,
            "opportunities_found": 0,
            "trades_executed": 0,
            "avg_latency_ms": 0,
        }
        
        # 交易所端点
        self.exchanges = {
            "binance": "https://api.binance.com/api/v3",
            "bybit": "https://api.bybit.com/v5",
            "okx": "https://www.okx.com/api/v5",
        }
    
    def _apply_config(self, config: Dict):
        """应用配置"""
        if "hft" in config:
            hft = config["hft"]
            for key, value in hft.items():
                if hasattr(self.hft_config, key):
                    setattr(self.hft_config, key, value)
    
    # ═══════════════════════════════════════════════════════════════════
    # 高性能API调用
    # ═══════════════════════════════════════════════════════════════════
    
    async def _fetch_price_async(self, session: aiohttp.ClientSession, 
                                  exchange: str, symbol: str) -> Optional[float]:
        """异步获取单个交易所价格"""
        if not await self.rate_limiter.acquire():
            return None
        
        try:
            url = f"{self.exchanges[exchange]}/ticker/price?symbol={symbol}"
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    price = float(data.get("price", 0))
                    self.cache.set(f"{exchange}:{symbol}", price)
                    return price
        except Exception:
            pass
        return None
    
    async def _fetch_all_prices(self, symbol: str) -> Dict[str, float]:
        """并行获取所有交易所价格"""
        session = await self.pool.get_session()
        
        # 构造所有交易对
        tasks = []
        exchange_symbols = []
        
        for exchange in self.exchanges:
            sym = self._convert_symbol(symbol, exchange)
            tasks.append(self._fetch_price_async(session, exchange, sym))
            exchange_symbols.append(exchange)
        
        # 并行执行
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        prices = {}
        for exchange, result in zip(exchange_symbols, results):
            if isinstance(result, (int, float)) and result > 0:
                prices[exchange] = result
        
        return prices
    
    def _convert_symbol(self, symbol: str, exchange: str) -> str:
        """转换符号格式"""
        base = symbol.replace("/USDT", "USDT")
        return base
    
    # ═══════════════════════════════════════════════════════════════════
    # 套利机会检测
    # ═══════════════════════════════════════════════════════════════════
    
    async def scan_arbitrage(self, symbols: List[str]) -> List[ArbitrageOpportunity]:
        """扫描套利机会"""
        opportunities = []
        start_time = time.time()
        
        for symbol in symbols:
            prices = await self._fetch_all_prices(symbol)
            
            if len(prices) < 2:
                continue
            
            # 找最高价和最低价
            sorted_prices = sorted(prices.items(), key=lambda x: x[1], reverse=True)
            best_buy = sorted_prices[-1]   # 最低价交易所
            best_sell = sorted_prices[0]   # 最高价交易所
            
            buy_exchange, buy_price = best_buy
            sell_exchange, sell_price = best_sell
            
            spread_pct = (sell_price - buy_price) / buy_price
            
            # 检查是否满足条件
            if spread_pct >= self.hft_config.min_spread:
                # 获取成交量
                volume = await self._get_volume(symbol)
                
                if volume >= self.hft_config.min_volume:
                    opp = ArbitrageOpportunity(
                        symbol=symbol,
                        buy_exchange=buy_exchange,
                        sell_exchange=sell_exchange,
                        buy_price=buy_price,
                        sell_price=sell_price,
                        spread_pct=spread_pct,
                        volume=volume,
                        confidence=min(spread_pct * 10, 1.0),
                    )
                    opportunities.append(opp)
                    self.opportunities.append(opp)
        
        # 更新统计
        self.stats["total_scans"] += 1
        self.stats["opportunities_found"] += len(opportunities)
        
        latency = (time.time() - start_time) * 1000
        self.stats["avg_latency_ms"] = (
            (self.stats["avg_latency_ms"] * (self.stats["total_scans"] - 1) + latency)
            / self.stats["total_scans"]
        )
        
        return opportunities
    
    async def _get_volume(self, symbol: str) -> float:
        """获取成交量"""
        session = await self.pool.get_session()
        try:
            url = f"{self.exchanges['binance']}/ticker/24hr?symbol={self._convert_symbol(symbol, 'binance')}"
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return float(data.get("quoteVolume", 0))
        except Exception:
            pass
        return 0
    
    # ═══════════════════════════════════════════════════════════════════
    # 指标计算 (优化版)
    # ═══════════════════════════════════════════════════════════════════
    
    @staticmethod
    def calculate_rsi_fast(prices: List[float], period: int = 14) -> float:
        """快速RSI计算"""
        if len(prices) < period + 1:
            return 50.0
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas[-period:]]
        losses = [-d if d < 0 else 0 for d in deltas[-period:]]
        
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        return 100.0 - (100.0 / (1.0 + rs))
    
    @staticmethod
    def calculate_volatility_fast(prices: List[float], period: int = 20) -> float:
        """快速波动率计算"""
        if len(prices) < period:
            return 0.0
        
        returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))][-period:]
        mean = sum(returns) / len(returns)
        variance = sum((r - mean) ** 2 for r in returns) / len(returns)
        
        return math.sqrt(variance * 252)  # 年化
    
    @staticmethod
    def calculate_momentum_fast(prices: List[float], period: int = 10) -> float:
        """快速动量计算"""
        if len(prices) < period + 1:
            return 0.0
        return (prices[-1] - prices[-period]) / prices[-period]
    
    # ═══════════════════════════════════════════════════════════════════
    # 信号生成
    # ═══════════════════════════════════════════════════════════════════
    
    async def generate_signal(self, symbol: str, prices: List[float]) -> dict:
        """生成交易信号"""
        if len(prices) < 20:
            return {"action": "hold", "confidence": 0}
        
        # 快速计算指标
        rsi = self.calculate_rsi_fast(prices)
        volatility = self.calculate_volatility_fast(prices)
        momentum = self.calculate_momentum_fast(prices)
        
        # 信号逻辑
        action = "hold"
        confidence = 0.0
        
        # 高动量 + 高波动 = 买入信号
        if momentum > 0.03 and volatility > 0.05:
            action = "buy"
            confidence = min(momentum * 10 + volatility * 5, 0.95)
        
        # 负动量 + 高波动 = 卖出信号
        elif momentum < -0.03 and volatility > 0.05:
            action = "sell"
            confidence = min(abs(momentum) * 10 + volatility * 5, 0.95)
        
        # RSI超买超卖
        if rsi > 80:
            action = "sell"
            confidence = max(confidence, 0.75)
        elif rsi < 20:
            action = "buy"
            confidence = max(confidence, 0.75)
        
        return {
            "action": action,
            "confidence": confidence,
            "rsi": rsi,
            "volatility": volatility,
            "momentum": momentum,
            "timestamp": time.time(),
        }
    
    # ═══════════════════════════════════════════════════════════════════
    # 风险管理
    # ═══════════════════════════════════════════════════════════════════
    
    def check_position_limits(self, symbol: str, size: float) -> Tuple[bool, str]:
        """检查仓位限制"""
        current_pos = self.positions.get(symbol, {}).get("size", 0)
        
        if current_pos + size > self.hft_config.max_position:
            return False, f"单笔仓位超限: {current_pos + size} > {self.hft_config.max_position}"
        
        total_pos = sum(p.get("size", 0) for p in self.positions.values())
        if total_pos + size > self.hft_config.max_total_position:
            return False, f"总仓位超限: {total_pos + size} > {self.hft_config.max_total_position}"
        
        return True, "OK"
    
    def calculate_position_size(self, price: float, confidence: float) -> float:
        """根据置信度计算仓位"""
        base_size = self.hft_config.max_position * 0.5
        adjusted_size = base_size * confidence
        return min(adjusted_size, self.hft_config.max_position)
    
    # ═══════════════════════════════════════════════════════════════════
    # 执行交易
    # ═══════════════════════════════════════════════════════════════════
    
    async def execute_arbitrage(self, opp: ArbitrageOpportunity) -> dict:
        """执行套利"""
        size = self.calculate_position_size(opp.buy_price, opp.confidence)
        
        # 检查仓位限制
        ok, msg = self.check_position_limits(opp.symbol, size)
        if not ok:
            return {"status": "rejected", "reason": msg}
        
        # 模拟执行
        result = {
            "status": "executed",
            "symbol": opp.symbol,
            "buy_exchange": opp.buy_exchange,
            "sell_exchange": opp.sell_exchange,
            "buy_price": opp.buy_price,
            "sell_price": opp.sell_price,
            "spread": opp.spread_pct,
            "size": size,
            "expected_profit": opp.spread_pct * size * opp.buy_price,
            "timestamp": time.time(),
        }
        
        self.stats["trades_executed"] += 1
        return result
    
    # ═══════════════════════════════════════════════════════════════════
    # 状态管理
    # ═══════════════════════════════════════════════════════════════════
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            **self.stats,
            "positions": len(self.positions),
            "opportunities_in_queue": len(self.opportunities),
            "cache_size": len(self.cache.cache),
        }
    
    async def close(self):
        """关闭资源"""
        await self.pool.close()


# ==================== 工厂函数 ====================

def create_mole_v3(config: Optional[Dict] = None) -> MoleV3Strategy:
    """创建打地鼠V3策略"""
    return MoleV3Strategy(config)


# 导出
__all__ = [
    "MoleV3Strategy",
    "HFTConfig",
    "ArbitrageOpportunity",
    "RateLimiter",
    "PriceCache",
    "ConnectionPool",
    "create_mole_v3",
]
