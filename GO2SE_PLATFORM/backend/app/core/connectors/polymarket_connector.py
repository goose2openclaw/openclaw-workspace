#!/usr/bin/env python3
"""
🪿 GO2SE Polymarket连接器 v11
预测市场数据接入
"""

import asyncio
import aiohttp
import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger("go2se")

POLYMARKET_BASE_URL = "https://clob.polymarket.com"
POLYMARKET_API_URL = "https://gamma-api.polymarket.com"
DEFAULT_TIMEOUT = aiohttp.ClientTimeout(total=10, connect=5)


class PolymarketConnector:
    """Polymarket预测市场连接器"""
    
    def __init__(self, api_key: str = ""):
        self.name = "polymarket"
        self.api_key = api_key
        self.base_url = POLYMARKET_BASE_URL
        self.api_url = POLYMARKET_API_URL
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
    
    async def _request(self, method: str, url: str, params: Dict = None) -> Optional[Any]:
        session = await self._get_session()
        headers = {"Content-Type": "application/json"}
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
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
                    logger.warning("Polymarket rate limited")
                    return None
                else:
                    logger.error(f"Polymarket API error {resp.status}: {url}")
                    return None
                    
        except asyncio.TimeoutError:
            logger.warning(f"Polymarket timeout: {url}")
            self.available = False
            return None
        except Exception as e:
            logger.error(f"Polymarket request error: {e}")
            self.available = False
            return None
    
    async def get_markets(self, limit: int = 100) -> Optional[List[Dict]]:
        """获取活跃市场列表"""
        data = await self._request(
            "GET",
            f"{self.api_url}/markets",
            {"limit": min(limit, 200), "closed": "false"}
        )
        
        if data:
            result = []
            for m in data:
                result.append({
                    "id": m.get("id"),
                    "question": m.get("question"),
                    "description": m.get("description"),
                    "outcome_prices": m.get("outcomePrices", {}),
                    "volume": float(m.get("volume", 0)),
                    "liquidity": float(m.get("liquidity", 0)),
                    "condition_id": m.get("conditionId"),
                    "created_at": m.get("createdAt"),
                    "end_date": m.get("endDate"),
                    "active": m.get("active", True),
                    "closed": m.get("closed", False),
                    "timestamp": datetime.utcnow().isoformat(),
                })
            return result
        return None
    
    async def get_market(self, market_id: str) -> Optional[Dict]:
        """获取单个市场详情"""
        data = await self._request(
            "GET",
            f"{self.api_url}/markets/{market_id}"
        )
        
        if data:
            return {
                "id": data.get("id"),
                "question": data.get("question"),
                "description": data.get("description"),
                "outcome_prices": data.get("outcomePrices", {}),
                "volume": float(data.get("volume", 0)),
                "liquidity": float(data.get("liquidity", 0)),
                "bids": data.get("bids", []),
                "asks": data.get("asks", []),
                "created_at": data.get("createdAt"),
                "end_date": data.get("endDate"),
                "resolved": data.get("resolved", False),
                "winner": data.get("winner"),
                "timestamp": datetime.utcnow().isoformat(),
            }
        return None
    
    async def get_prices(self, market_id: str) -> Optional[Dict]:
        """获取市场当前价格(概率)"""
        data = await self._request(
            "GET",
            f"{self.api_url}/prices",
            {"market_id": market_id}
        )
        
        if data:
            return {
                "market_id": market_id,
                "prices": data,
                "timestamp": datetime.utcnow().isoformat(),
                "latency_ms": round(self.latency_ms, 2),
            }
        return None
    
    async def get_orderbook(self, market_id: str) -> Optional[Dict]:
        """获取订单簿"""
        data = await self._request(
            "GET",
            f"{self.base_url}/orderbook",
            {"market": market_id}
        )
        
        if data:
            return {
                "market_id": market_id,
                "bids": data.get("bids", []),
                "asks": data.get("asks", []),
                "timestamp": datetime.utcnow().isoformat(),
                "latency_ms": round(self.latency_ms, 2),
            }
        return None
    
    async def get_trades(self, market_id: str, limit: int = 100) -> Optional[List[Dict]]:
        """获取最近成交"""
        data = await self._request(
            "GET",
            f"{self.base_url}/trades",
            {"market": market_id, "limit": min(limit, 500)}
        )
        
        if data:
            return [
                {
                    "id": t.get("id"),
                    "side": t.get("side"),
                    "price": float(t.get("price", 0)),
                    "size": float(t.get("size", 0)),
                    "timestamp": t.get("timestamp"),
                }
                for t in data
            ]
        return None
    
    async def get_market_stats(self) -> Optional[Dict]:
        """获取市场统计数据"""
        data = await self._request(
            "GET",
            f"{self.api_url}/stats"
        )
        
        if data:
            return {
                "total_volume": data.get("totalVolume", 0),
                "total_markets": data.get("totalMarkets", 0),
                "active_markets": data.get("activeMarkets", 0),
                "timestamp": datetime.utcnow().isoformat(),
            }
        return None
    
    async def get_events(self, limit: int = 50) -> Optional[List[Dict]]:
        """获取事件列表"""
        data = await self._request(
            "GET",
            f"{self.api_url}/events",
            {"limit": min(limit, 200)}
        )
        
        if data:
            result = []
            for e in data:
                result.append({
                    "id": e.get("id"),
                    "title": e.get("title"),
                    "description": e.get("description"),
                    "start_date": e.get("startDate"),
                    "end_date": e.get("endDate"),
                    "volume": float(e.get("volume", 0)),
                    "markets_count": e.get("marketsCount", 0),
                    "timestamp": datetime.utcnow().isoformat(),
                })
            return result
        return None
    
    async def search_markets(self, query: str, limit: int = 20) -> Optional[List[Dict]]:
        """搜索市场"""
        data = await self._request(
            "GET",
            f"{self.api_url}/markets",
            {"query": query, "limit": min(limit, 100)}
        )
        
        if data:
            return [
                {
                    "id": m.get("id"),
                    "question": m.get("question"),
                    "outcome_prices": m.get("outcomePrices", {}),
                    "volume": float(m.get("volume", 0)),
                }
                for m in data
            ]
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
                f"{self.api_url}/stats",
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
        """获取多个市场ticker"""
        markets = await self.get_markets(limit=50)
        
        results = []
        if markets:
            for m in markets:
                outcome_prices = m.get("outcome_prices", {})
                if isinstance(outcome_prices, dict):
                    for outcome, price in outcome_prices.items():
                        results.append({
                            "exchange": "polymarket",
                            "market_id": m.get("id"),
                            "question": m.get("question"),
                            "outcome": outcome,
                            "price": float(price),
                            "volume": m.get("volume"),
                            "timestamp": m.get("timestamp"),
                        })
                elif isinstance(outcome_prices, list) and len(outcome_prices) >= 2:
                    results.append({
                        "exchange": "polymarket",
                        "market_id": m.get("id"),
                        "question": m.get("question"),
                        "yes_price": float(outcome_prices[0]) if outcome_prices[0] else None,
                        "no_price": float(outcome_prices[1]) if len(outcome_prices) > 1 and outcome_prices[1] else None,
                        "volume": m.get("volume"),
                        "timestamp": m.get("timestamp"),
                    })
        
        return results


# ─── 全局实例 ───────────────────────────────────────────

polymarket_connector = PolymarketConnector()
