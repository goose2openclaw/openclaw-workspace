#!/usr/bin/env python3
"""
🪿 GO2SE Binance连接器 v11
增强版: 请求重试、超时控制、错误处理、缓存支持
"""

import asyncio
import aiohttp
import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from functools import wraps

logger = logging.getLogger("go2se")

# ─── 配置 ───────────────────────────────────────────

BINANCE_BASE_URL = "https://api.binance.com"
BINANCE_API_VERSION = "v3"

DEFAULT_TIMEOUT = aiohttp.ClientTimeout(total=10, connect=5)
MAX_RETRIES = 3
RETRY_DELAY = 1.0  # 秒


# ─── 工具函数 ───────────────────────────────────────────

def retry_on_error(max_retries: int = MAX_RETRIES, delay: float = RETRY_DELAY):
    """重试装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay * (attempt + 1))
            raise last_error
        return wrapper
    return decorator


def symbol_to_binance(symbol: str) -> str:
    """转换为Binance格式: BTC/USDT -> BTCUSDT"""
    return symbol.replace("/", "").upper()


def binance_to_symbol(binance_symbol: str) -> str:
    """转换为标准格式: BTCUSDT -> BTC/USDT"""
    for quote in ["USDT", "BUSD", "BTC", "ETH", "BNB"]:
        if binance_symbol.endswith(quote):
            base = binance_symbol[:-len(quote)]
            return f"{base}/{quote}"
    return binance_symbol


# ─── Binance连接器 ───────────────────────────────────────────

class BinanceConnector:
    """Binance交易所连接器"""
    
    def __init__(
        self,
        api_key: str = "",
        api_secret: str = "",
        base_url: str = BINANCE_BASE_URL,
        testnet: bool = False
    ):
        self.name = "binance"
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url if not testnet else "https://testnet.binance.vision"
        self.available = False
        self.latency_ms = 0
        self._session: Optional[aiohttp.ClientSession] = None
        self._last_health_check = 0
        self._health_check_ttl = 60  # 秒
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """获取或创建会话"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=DEFAULT_TIMEOUT)
        return self._session
    
    async def close(self):
        """关闭会话"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Dict = None,
        signed: bool = False
    ) -> Optional[Dict]:
        """发送请求"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if self.api_key:
            headers["X-MBX-APIKEY"] = self.api_key
        
        session = await self._get_session()
        start = time.time()
        
        try:
            async with session.request(
                method, url, params=params, headers=headers
            ) as resp:
                self.latency_ms = (time.time() - start) * 1000
                
                if resp.status == 200:
                    self.available = True
                    return await resp.json()
                elif resp.status == 429:
                    logger.warning(f"Binance rate limited: {endpoint}")
                    return None
                elif resp.status == 418:
                    logger.error(f"Binance IP banned: {endpoint}")
                    return None
                else:
                    logger.error(f"Binance API error {resp.status}: {endpoint}")
                    return None
                    
        except asyncio.TimeoutError:
            logger.warning(f"Binance timeout: {endpoint}")
            self.available = False
            return None
        except Exception as e:
            logger.error(f"Binance request error: {e}")
            self.available = False
            return None
    
    @retry_on_error(max_retries=3, delay=1.0)
    async def get_price(self, symbol: str) -> Optional[Dict]:
        """获取实时价格"""
        binance_symbol = symbol_to_binance(symbol)
        data = await self._request("GET", "/api/v3/ticker/price", {"symbol": binance_symbol})
        
        if data:
            return {
                "exchange": "binance",
                "symbol": symbol,
                "price": float(data["price"]),
                "timestamp": datetime.utcnow().isoformat(),
                "latency_ms": round(self.latency_ms, 2),
            }
        return None
    
    @retry_on_error(max_retries=3, delay=1.0)
    async def get_ticker(self, symbol: str) -> Optional[Dict]:
        """获取24h行情"""
        binance_symbol = symbol_to_binance(symbol)
        data = await self._request("GET", "/api/v3/ticker/24hr", {"symbol": binance_symbol})
        
        if data:
            return {
                "exchange": "binance",
                "symbol": symbol,
                "lastPrice": float(data["lastPrice"]),
                "priceChange": float(data["priceChange"]),
                "priceChangePercent": float(data["priceChangePercent"]),
                "volume": float(data["volume"]),
                "quoteVolume": float(data["quoteVolume"]),
                "highPrice": float(data["highPrice"]),
                "lowPrice": float(data["lowPrice"]),
                "bidPrice": float(data["bidPrice"]) if "bidPrice" in data else None,
                "askPrice": float(data["askPrice"]) if "askPrice" in data else None,
                "count": int(data["count"]) if "count" in data else None,
                "timestamp": datetime.utcnow().isoformat(),
                "latency_ms": round(self.latency_ms, 2),
            }
        return None
    
    @retry_on_error(max_retries=3, delay=1.0)
    async def get_orderbook(self, symbol: str, limit: int = 20) -> Optional[Dict]:
        """获取订单簿"""
        binance_symbol = symbol_to_binance(symbol)
        limit = min(limit, 100)  # Binance最大100
        data = await self._request("GET", "/api/v3/depth", {
            "symbol": binance_symbol,
            "limit": limit
        })
        
        if data:
            return {
                "exchange": "binance",
                "symbol": symbol,
                "bids": [[float(p), float(q)] for p, q in data.get("bids", [])],
                "asks": [[float(p), float(q)] for p, q in data.get("asks", [])],
                "lastUpdateId": data.get("lastUpdateId"),
                "timestamp": datetime.utcnow().isoformat(),
                "latency_ms": round(self.latency_ms, 2),
            }
        return None
    
    @retry_on_error(max_retries=3, delay=1.0)
    async def get_klines(
        self,
        symbol: str,
        interval: str = "1m",
        limit: int = 100
    ) -> Optional[List[Dict]]:
        """获取K线数据"""
        binance_symbol = symbol_to_binance(symbol)
        limit = min(limit, 1000)  # Binance最大1000
        
        data = await self._request("GET", "/api/v3/klines", {
            "symbol": binance_symbol,
            "interval": interval,
            "limit": limit
        })
        
        if data:
            result = []
            for k in data:
                result.append({
                    "open_time": k[0],
                    "open": float(k[1]),
                    "high": float(k[2]),
                    "low": float(k[3]),
                    "close": float(k[4]),
                    "volume": float(k[5]),
                    "close_time": k[6],
                    "quote_volume": float(k[7]),
                    "trades": int(k[8]),
                    "taker_buy_volume": float(k[9]),
                    "taker_buy_quote_volume": float(k[10]),
                })
            return result
        return None
    
    @retry_on_error(max_retries=3, delay=1.0)
    async def get_recent_trades(self, symbol: str, limit: int = 100) -> Optional[List[Dict]]:
        """获取最近成交"""
        binance_symbol = symbol_to_binance(symbol)
        limit = min(limit, 1000)
        
        data = await self._request("GET", "/api/v3/trades", {
            "symbol": binance_symbol,
            "limit": limit
        })
        
        if data:
            return [
                {
                    "id": t["id"],
                    "price": float(t["price"]),
                    "qty": float(t["qty"]),
                    "time": t["time"],
                    "is_buyer_maker": t["isBuyerMaker"],
                }
                for t in data
            ]
        return None
    
    @retry_on_error(max_retries=2, delay=0.5)
    async def get_exchange_info(self) -> Optional[Dict]:
        """获取交易所信息"""
        return await self._request("GET", "/api/v3/exchangeInfo")
    
    async def health_check(self) -> bool:
        """健康检查"""
        now = time.time()
        
        # 缓存健康检查结果
        if now - self._last_health_check < self._health_check_ttl:
            return self.available
        
        self._last_health_check = now
        
        try:
            session = await self._get_session()
            start = time.time()
            
            async with session.get(
                f"{self.base_url}/api/v3/ping",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                self.latency_ms = (time.time() - start) * 1000
                
                if resp.status == 200:
                    self.available = True
                    return True
                    
        except Exception:
            pass
        
        self.available = False
        return False
    
    async def get_all_tickers(self, symbols: List[str] = None) -> List[Dict]:
        """批量获取ticker"""
        results = []
        
        if symbols:
            tasks = [self.get_ticker(s) for s in symbols]
            tickers = await asyncio.gather(*tasks, return_exceptions=True)
            
            for t in tickers:
                if isinstance(t, dict):
                    results.append(t)
        
        return results


# ─── 全局实例 ───────────────────────────────────────────

binance_connector = BinanceConnector()
