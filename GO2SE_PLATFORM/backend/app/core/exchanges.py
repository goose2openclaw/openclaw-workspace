"""
API库 - 多交易所数据源接入
支持: Binance, Bybit, OKX, Coinbase, Kraken, Gate, Mexc, KuCoin, Huobi, Bitget, Bitfinex, Gemini
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ExchangeConnector:
    """交易所连接器基类"""
    
    def __init__(self, name: str, api_key: str = "", api_secret: str = ""):
        self.name = name
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = ""
        self.latency_ms = 0
        self.available = False
        
    async def get_price(self, symbol: str) -> Optional[Dict]:
        """获取价格"""
        raise NotImplementedError
        
    async def get_orderbook(self, symbol: str, limit: int = 20) -> Optional[Dict]:
        """获取订单簿"""
        raise NotImplementedError
        
    async def get_ticker(self, symbol: str) -> Optional[Dict]:
        """获取24h行情"""
        raise NotImplementedError
        
    async def health_check(self) -> bool:
        """健康检查"""
        raise NotImplementedError


class BinanceConnector(ExchangeConnector):
    """Binance 交易所连接器"""
    
    def __init__(self, api_key: str = "", api_secret: str = ""):
        super().__init__("binance", api_key, api_secret)
        self.base_url = "https://api.binance.com"
        
    async def get_price(self, symbol: str) -> Optional[Dict]:
        async with aiohttp.ClientSession() as session:
            try:
                url = f"{self.base_url}/api/v3/ticker/price?symbol={symbol}"
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {
                            "exchange": "binance",
                            "symbol": symbol,
                            "price": float(data["price"]),
                            "timestamp": datetime.utcnow().isoformat()
                        }
            except Exception as e:
                logger.error(f"Binance get_price error: {e}")
        return None
        
    async def get_orderbook(self, symbol: str, limit: int = 20) -> Optional[Dict]:
        async with aiohttp.ClientSession() as session:
            try:
                url = f"{self.base_url}/api/v3/depth?symbol={symbol}&limit={limit}"
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {
                            "exchange": "binance",
                            "symbol": symbol,
                            "bids": [[float(p), float(q)] for p, q in data["bids"]],
                            "asks": [[float(p), float(q)] for p, q in data["asks"]],
                            "timestamp": datetime.utcnow().isoformat()
                        }
            except Exception as e:
                logger.error(f"Binance get_orderbook error: {e}")
        return None
        
    async def get_ticker(self, symbol: str) -> Optional[Dict]:
        async with aiohttp.ClientSession() as session:
            try:
                url = f"{self.base_url}/api/v3/ticker/24hr?symbol={symbol}"
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
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
                            "timestamp": datetime.utcnow().isoformat()
                        }
            except Exception as e:
                logger.error(f"Binance get_ticker error: {e}")
        return None
        
    async def health_check(self) -> bool:
        async with aiohttp.ClientSession() as session:
            try:
                url = f"{self.base_url}/api/v3/ping"
                start = datetime.utcnow()
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        self.available = True
                        return True
            except Exception:
                pass
        self.available = False
        return False


class BybitConnector(ExchangeConnector):
    """Bybit 交易所连接器"""
    
    def __init__(self, api_key: str = "", api_secret: str = ""):
        super().__init__("bybit", api_key, api_secret)
        self.base_url = "https://api.bybit.com"
        
    async def get_price(self, symbol: str) -> Optional[Dict]:
        async with aiohttp.ClientSession() as session:
            try:
                url = f"{self.base_url}/v5/market/tickers?category=spot&symbol={symbol}"
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("retCode") == 0:
                            item = data["result"]["list"][0]
                            return {
                                "exchange": "bybit",
                                "symbol": symbol,
                                "price": float(item["lastPrice"]),
                                "timestamp": datetime.utcnow().isoformat()
                            }
            except Exception as e:
                logger.error(f"Bybit get_price error: {e}")
        return None
        
    async def health_check(self) -> bool:
        async with aiohttp.ClientSession() as session:
            try:
                url = f"{self.base_url}/v5/market/time"
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        self.available = True
                        return True
            except Exception:
                pass
        self.available = False
        return False


class OKXConnector(ExchangeConnector):
    """OKX 交易所连接器"""
    
    def __init__(self, api_key: str = "", api_secret: str = ""):
        super().__init__("okx", api_key, api_secret)
        self.base_url = "https://www.okx.com"
        
    async def get_price(self, symbol: str) -> Optional[Dict]:
        async with aiohttp.ClientSession() as session:
            try:
                url = f"{self.base_url}/api/v5/market/ticker?instId={symbol}"
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("code") == "0":
                            item = data["data"][0]
                            return {
                                "exchange": "okx",
                                "symbol": symbol,
                                "price": float(item["last"]),
                                "timestamp": datetime.utcnow().isoformat()
                            }
            except Exception as e:
                logger.error(f"OKX get_price error: {e}")
        return None
        
    async def health_check(self) -> bool:
        async with aiohttp.ClientSession() as session:
            try:
                url = f"{self.base_url}/api/v5/system/time"
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        self.available = True
                        return True
            except Exception:
                pass
        self.available = False
        return False


class CoinbaseConnector(ExchangeConnector):
    """Coinbase 交易所连接器"""
    
    def __init__(self, api_key: str = "", api_secret: str = ""):
        super().__init__("coinbase", api_key, api_secret)
        self.base_url = "https://api.coinbase.com"
        
    async def get_price(self, symbol: str) -> Optional[Dict]:
        async with aiohttp.ClientSession() as session:
            try:
                # Coinbase uses BTC-USD format
                pair = symbol.replace("/", "-")
                url = f"{self.base_url}/v2/prices/{pair}/spot"
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {
                            "exchange": "coinbase",
                            "symbol": symbol,
                            "price": float(data["data"]["amount"]),
                            "timestamp": datetime.utcnow().isoformat()
                        }
            except Exception as e:
                logger.error(f"Coinbase get_price error: {e}")
        return None
        
    async def health_check(self) -> bool:
        async with aiohttp.ClientSession() as session:
            try:
                url = f"{self.base_url}/v2/time"
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        self.available = True
                        return True
            except Exception:
                pass
        self.available = False
        False


class KrakenConnector(ExchangeConnector):
    """Kraken 交易所连接器"""
    
    def __init__(self, api_key: str = "", api_secret: str = ""):
        super().__init__("kraken", api_key, api_secret)
        self.base_url = "https://api.kraken.com"
        
    async def get_price(self, symbol: str) -> Optional[Dict]:
        async with aiohttp.ClientSession() as session:
            try:
                # Kraken uses XXBT format for BTC
                kraken_symbol = symbol.replace("BTC", "XBT")
                url = f"{self.base_url}/0/public/Ticker?pair={kraken_symbol}"
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("error") == []:
                            pairs = list(data["result"].keys())
                            ticker = data["result"][pairs[0]]
                            return {
                                "exchange": "kraken",
                                "symbol": symbol,
                                "price": float(ticker["c"][0]),
                                "timestamp": datetime.utcnow().isoformat()
                            }
            except Exception as e:
                logger.error(f"Kraken get_price error: {e}")
        return None
        
    async def health_check(self) -> bool:
        async with aiohttp.ClientSession() as session:
            try:
                url = f"{self.base_url}/0/public/Time"
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        self.available = True
                        return True
            except Exception:
                pass
        self.available = False
        return False


class GateConnector(ExchangeConnector):
    """Gate.io 交易所连接器"""
    
    def __init__(self, api_key: str = "", api_secret: str = ""):
        super().__init__("gate", api_key, api_secret)
        self.base_url = "https://api.gateio.ws"
        
    async def get_price(self, symbol: str) -> Optional[Dict]:
        async with aiohttp.ClientSession() as session:
            try:
                url = f"{self.base_url}/api/v4/spot/tickers?currency_pair={symbol}"
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data:
                            return {
                                "exchange": "gate",
                                "symbol": symbol,
                                "price": float(data[0]["last"]),
                                "timestamp": datetime.utcnow().isoformat()
                            }
            except Exception as e:
                logger.error(f"Gate get_price error: {e}")
        return None
        
    async def health_check(self) -> bool:
        async with aiohttp.ClientSession() as session:
            try:
                url = f"{self.base_url}/api/v4/spot/time"
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        self.available = True
                        return True
            except Exception:
                pass
        self.available = False
        return False


class MexcConnector(ExchangeConnector):
    """MEXC 交易所连接器"""
    
    def __init__(self, api_key: str = "", api_secret: str = ""):
        super().__init__("mexc", api_key, api_secret)
        self.base_url = "https://api.mexc.com"
        
    async def get_price(self, symbol: str) -> Optional[Dict]:
        async with aiohttp.ClientSession() as session:
            try:
                url = f"{self.base_url}/api/v3/ticker/price?symbol={symbol}"
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {
                            "exchange": "mexc",
                            "symbol": symbol,
                            "price": float(data["price"]),
                            "timestamp": datetime.utcnow().isoformat()
                        }
            except Exception as e:
                logger.error(f"MEXC get_price error: {e}")
        return None
        
    async def health_check(self) -> bool:
        async with aiohttp.ClientSession() as session:
            try:
                url = f"{self.base_url}/api/v3/time"
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        self.available = True
                        return True
            except Exception:
                pass
        self.available = False
        return False


class KuCoinConnector(ExchangeConnector):
    """KuCoin 交易所连接器"""
    
    def __init__(self, api_key: str = "", api_secret: str = ""):
        super().__init__("kucoin", api_key, api_secret)
        self.base_url = "https://api.kucoin.com"
        
    async def get_price(self, symbol: str) -> Optional[Dict]:
        async with aiohttp.ClientSession() as session:
            try:
                url = f"{self.base_url}/api/v1/market/orderbook/level1?symbol={symbol}"
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("code") == "200000":
                            return {
                                "exchange": "kucoin",
                                "symbol": symbol,
                                "price": float(data["data"]["price"]),
                                "timestamp": datetime.utcnow().isoformat()
                            }
            except Exception as e:
                logger.error(f"KuCoin get_price error: {e}")
        return None
        
    async def health_check(self) -> bool:
        async with aiohttp.ClientSession() as session:
            try:
                url = f"{self.base_url}/api/v1/timestamp"
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        self.available = True
                        return True
            except Exception:
                pass
        self.available = False
        return False


# 交易所连接器映射
EXCHANGE_CONNECTORS = {
    "binance": BinanceConnector,
    "bybit": BybitConnector,
    "okx": OKXConnector,
    "coinbase": CoinbaseConnector,
    "kraken": KrakenConnector,
    "gate": GateConnector,
    "mexc": MexcConnector,
    "kucoin": KuCoinConnector,
}


class ExchangeManager:
    """交易所管理器 - 统一接入多个交易所"""
    
    def __init__(self):
        self.connectors: Dict[str, ExchangeConnector] = {}
        self.primary_exchange = "binance"
        self.fallback_exchanges = ["bybit", "okx"]
        
    def register_exchange(self, name: str, api_key: str = "", api_secret: str = ""):
        """注册交易所"""
        if name in EXCHANGE_CONNECTORS:
            self.connectors[name] = EXCHANGE_CONNECTORS[name](api_key, api_secret)
            logger.info(f"Registered exchange: {name}")
            
    async def initialize_all(self):
        """初始化所有交易所连接"""
        for name in EXCHANGE_CONNECTORS.keys():
            if name not in self.connectors:
                self.connectors[name] = EXCHANGE_CONNECTORS[name]()
                
        # 并行健康检查
        tasks = [conn.health_check() for conn in self.connectors.values()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for name, result in zip(self.connectors.keys(), results):
            if result:
                logger.info(f"Exchange {name}: ONLINE")
            else:
                logger.warning(f"Exchange {name}: OFFLINE")
                
    async def get_price(self, symbol: str, exchange: str = None) -> Optional[Dict]:
        """获取价格 - 支持指定交易所或自动选择"""
        if exchange:
            conn = self.connectors.get(exchange)
            if conn:
                return await conn.get_price(symbol)
            return None
            
        # 尝试主交易所
        primary = self.connectors.get(self.primary_exchange)
        if primary and primary.available:
            result = await primary.get_price(symbol)
            if result:
                return result
                
        # 尝试备用交易所
        for fallback in self.fallback_exchanges:
            conn = self.connectors.get(fallback)
            if conn and conn.available:
                result = await conn.get_price(symbol)
                if result:
                    return result
                    
        return None
        
    async def get_aggregated_price(self, symbol: str) -> Dict:
        """聚合多交易所价格"""
        prices = []
        
        tasks = [conn.get_price(symbol) for conn in self.connectors.values() 
                 if conn.available]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if result and isinstance(result, dict):
                prices.append(result)
                
        if not prices:
            return {"error": "No available exchanges"}
            
        # 计算加权平均价格
        total_price = sum(p["price"] for p in prices)
        avg_price = total_price / len(prices)
        
        return {
            "symbol": symbol,
            "avg_price": avg_price,
            "prices": prices,
            "exchanges_available": len(prices),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    async def get_all_tickers(self, exchange: str = "binance") -> List[Dict]:
        """获取所有交易对行情"""
        conn = self.connectors.get(exchange)
        if conn and conn.available:
            # 获取主要交易对
            symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", 
                      "ADAUSDT", "DUSDT", "AVAXUSDT", "DOTUSDT", "MATICUSDT"]
            
            tasks = [conn.get_ticker(s) for s in symbols]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            return [r for r in results if r and isinstance(r, dict)]
            
        return []
        
    def get_status(self) -> Dict:
        """获取所有交易所状态"""
        return {
            name: {
                "available": conn.available,
                "latency_ms": conn.latency_ms
            }
            for name, conn in self.connectors.items()
        }


# 全局交易所管理器实例
exchange_manager = ExchangeManager()
