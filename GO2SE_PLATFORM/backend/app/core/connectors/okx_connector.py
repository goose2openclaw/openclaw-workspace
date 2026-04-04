#!/usr/bin/env python3
"""
🪿 GO2SE OKX连接器 v11
"""

import asyncio
import aiohttp
import logging
import time
import hmac
import hashlib
import base64
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger("go2se")

OKX_BASE_URL = "https://www.okx.com"
DEFAULT_TIMEOUT = aiohttp.ClientTimeout(total=10, connect=5)
MAX_RETRIES = 3


def symbol_to_okx(symbol: str) -> str:
    """转换为OKX格式: BTC/USDT -> BTC-USDT"""
    return symbol.replace("/", "-").upper()


def okx_to_symbol(okx_symbol: str) -> str:
    """转换为标准格式: BTC-USDT -> BTC/USDT"""
    return okx_symbol.replace("-", "/")


class OKXConnector:
    """OKX交易所连接器"""
    
    def __init__(
        self,
        api_key: str = "",
        api_secret: str = "",
        passphrase: str = "",
        testnet: bool = False
    ):
        self.name = "okx"
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
        self.base_url = OKX_BASE_URL if not testnet else "https://www.okx.com"
        self.available = False
        self.latency_ms = 0
        self._session: Optional[aiohttp.ClientSession] = None
        self._last_health_check = 0
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=DEFAULT_TIMEOUT)
        return self._session
    
    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
    
    def _sign(self, timestamp: str, method: str, path: str, body: str = "") -> str:
        """签名"""
        message = timestamp + method + path + body
        mac = hmac.new(
            self.api_secret.encode(),
            message.encode(),
            hashlib.sha256
        )
        return base64.b64encode(mac.digest()).decode()
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Dict = None,
        signed: bool = False
    ) -> Optional[Dict]:
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if signed and self.api_key:
            import json
            timestamp = datetime.utcnow().isoformat() + "Z"
            body = json.dumps(params) if params else ""
            
            headers["OK-Access-Key"] = self.api_key
            headers["OK-Access-Sign"] = self._sign(timestamp, method, endpoint, body)
            headers["OK-Access-Timestamp"] = timestamp
            headers["OK-Access-Passphrase"] = self.passphrase
        
        session = await self._get_session()
        start = time.time()
        
        try:
            async with session.request(
                method, url, json=params if signed else None,
                params=params if not signed else None,
                headers=headers
            ) as resp:
                self.latency_ms = (time.time() - start) * 1000
                
                if resp.status == 200:
                    data = await resp.json()
                    self.available = True
                    if data.get("code") == "0":
                        return data.get("data", {})
                    else:
                        logger.error(f"OKX API error: {data.get('msg')}")
                        return None
                else:
                    logger.error(f"OKX API error {resp.status}: {endpoint}")
                    return None
                    
        except asyncio.TimeoutError:
            logger.warning(f"OKX timeout: {endpoint}")
            self.available = False
            return None
        except Exception as e:
            logger.error(f"OKX request error: {e}")
            self.available = False
            return None
    
    async def get_price(self, symbol: str) -> Optional[Dict]:
        """获取实时价格"""
        okx_symbol = symbol_to_okx(symbol)
        data = await self._request("GET", "/api/v5/market/ticker", {
            "instId": okx_symbol
        })
        
        if data and len(data) > 0:
            item = data[0]
            return {
                "exchange": "okx",
                "symbol": symbol,
                "price": float(item.get("last", 0)),
                "timestamp": datetime.utcnow().isoformat(),
                "latency_ms": round(self.latency_ms, 2),
            }
        return None
    
    async def get_ticker(self, symbol: str) -> Optional[Dict]:
        """获取24h行情"""
        okx_symbol = symbol_to_okx(symbol)
        data = await self._request("GET", "/api/v5/market/ticker", {
            "instId": okx_symbol
        })
        
        if data and len(data) > 0:
            item = data[0]
            return {
                "exchange": "okx",
                "symbol": symbol,
                "lastPrice": float(item.get("last", 0)),
                "priceChange": float(item.get("last", 0)) - float(item.get("open24h", 0)),
                "priceChangePercent": (
                    (float(item.get("last", 0)) / float(item.get("open24h", 1)) - 1) * 100
                ),
                "highPrice": float(item.get("high24h", 0)),
                "lowPrice": float(item.get("low24h", 0)),
                "volume": float(item.get("vol24h", 0)),
                "quoteVolume": float(item.get("volCcy24h", 0)),
                "bidPrice": float(item.get("bidPx", 0)),
                "askPrice": float(item.get("askPx", 0)),
                "timestamp": datetime.utcnow().isoformat(),
                "latency_ms": round(self.latency_ms, 2),
            }
        return None
    
    async def get_orderbook(self, symbol: str, limit: int = 20) -> Optional[Dict]:
        """获取订单簿"""
        okx_symbol = symbol_to_okx(symbol)
        limit = min(limit, 400)
        
        data = await self._request("GET", "/api/v5/market/books", {
            "instId": okx_symbol,
            "sz": limit
        })
        
        if data and len(data) > 0:
            item = data[0]
            return {
                "exchange": "okx",
                "symbol": symbol,
                "bids": [[float(item[1]), float(item[2])]],  # OKX格式: [price, qty]
                "asks": [[float(item[3]), float(item[4])]],
                "timestamp": item[6] if len(item) > 6 else datetime.utcnow().isoformat(),
                "latency_ms": round(self.latency_ms, 2),
            }
        return None
    
    async def get_klines(
        self,
        symbol: str,
        interval: str = "1m",
        limit: int = 100
    ) -> Optional[List[Dict]]:
        """获取K线数据"""
        okx_symbol = symbol_to_okx(symbol)
        
        # 映射OKX周期
        interval_map = {
            "1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m",
            "1h": "1H", "2h": "2H", "4h": "4H", "6h": "6H",
            "12h": "12H", "1d": "1D", "3d": "3D", "1w": "1W"
        }
        okx_interval = interval_map.get(interval, "1m")
        
        limit = min(limit, 100)
        
        data = await self._request("GET", "/api/v5/market/candles", {
            "instId": okx_symbol,
            "bar": okx_interval,
            "limit": limit
        })
        
        if data:
            # OKX返回最新的在前
            result = []
            for k in data:
                result.append({
                    "timestamp": int(k[0]),
                    "open": float(k[1]),
                    "high": float(k[2]),
                    "low": float(k[3]),
                    "close": float(k[4]),
                    "volume": float(k[5]),
                    "quote_volume": float(k[7]) if len(k) > 7 else 0,
                })
            return list(reversed(result))  # 转换为时间正序
        return None
    
    async def health_check(self) -> bool:
        """健康检查"""
        now = time.time()
        if now - self._last_health_check < 60:
            return self.available
        
        self._last_health_check = now
        
        try:
            session = await self._get_session()
            start = time.time()
            
            async with session.get(
                f"{self.base_url}/api/v5/system/time",
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

okx_connector = OKXConnector()
