"""
🌐 跨市场扩展引擎
================
为北斗七鑫添加跨市场交易能力

支持的市場:
- Crypto (币安、Bybit、OKX)
- Stock (美股、A股)
- Forex (外汇)
- Commodity (大宗商品)
"""

import asyncio
import urllib.request
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Market(Enum):
    """市场枚举"""
    CRYPTO = "crypto"
    STOCK_US = "stock_us"
    STOCK_CN = "stock_cn"
    FOREX = "forex"
    COMMODITY = "commodity"


@dataclass
class MarketConfig:
    """市场配置"""
    market: Market
    name: str
    enabled: bool = False
    api_endpoint: str = ""
    symbols: List[str] = field(default_factory=list)
    weight: float = 0.0  # 仓位权重


@dataclass
class CrossMarketSignal:
    """跨市场信号"""
    market: Market
    symbol: str
    price: float
    change_24h: float
    direction: str  # LONG, SHORT, HOLD
    confidence: float
    volume: float
    metadata: Dict = field(default_factory=dict)


class CrossMarketEngine:
    """
    跨市场扩展引擎
    ===============
    统一接口访问多个市场
    """
    
    def __init__(self):
        self.markets: Dict[Market, MarketConfig] = {}
        self._init_default_markets()
    
    def _init_default_markets(self):
        """初始化默认市场配置"""
        
        # 加密货币市场 (币安)
        self.markets[Market.CRYPTO] = MarketConfig(
            market=Market.CRYPTO,
            name="🪙 加密货币 (Binance)",
            enabled=True,
            api_endpoint="https://api.binance.com/api/v3",
            symbols=["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"],
            weight=0.40  # 40%仓位
        )
        
        # 美股市场 (Alpha Vantage / Yahoo Finance)
        self.markets[Market.STOCK_US] = MarketConfig(
            market=Market.STOCK_US,
            name="📈 美股 (NASDAQ/NYSE)",
            enabled=False,
            api_endpoint="https://query1.finance.yahoo.com/v8/finance",
            symbols=["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"],
            weight=0.20  # 20%仓位
        )
        
        # A股市场 (Tushare)
        self.markets[Market.STOCK_CN] = MarketConfig(
            market=Market.STOCK_CN,
            name="🏛️ A股 (沪深)",
            enabled=False,
            api_endpoint="http://api.tushare.pro",
            symbols=["600519", "000858", "601888"],  # 茅台、五粮液、中国中免
            weight=0.15  # 15%仓位
        )
        
        # 外汇市场
        self.markets[Market.FOREX] = MarketConfig(
            market=Market.FOREX,
            name="💱 外汇",
            enabled=False,
            api_endpoint="https://api.exchangerate-api.com/v4",
            symbols=["EUR/USD", "GBP/USD", "USD/JPY"],
            weight=0.15  # 15%仓位
        )
        
        # 大宗商品
        self.markets[Market.COMMODITY] = MarketConfig(
            market=Market.COMMODITY,
            name="🛢️ 大宗商品",
            enabled=False,
            api_endpoint="https://api.metals.live/v1",
            symbols=["GOLD", "SILVER", "OIL"],
            weight=0.10  # 10%仓位
        )
    
    def enable_market(self, market: Market, enabled: bool = True) -> None:
        """启用/禁用市场"""
        if market in self.markets:
            self.markets[market].enabled = enabled
            status = "启用" if enabled else "禁用"
            logger.info(f"✅ 市场{status}: {self.markets[market].name}")
    
    def get_enabled_markets(self) -> List[Market]:
        """获取已启用的市场列表"""
        return [m for m, cfg in self.markets.items() if cfg.enabled]
    
    async def fetch_market_data(self, market: Market, 
                                symbol: str) -> Optional[CrossMarketSignal]:
        """获取市场数据"""
        if market not in self.markets or not self.markets[market].enabled:
            return None
        
        config = self.markets[market]
        
        try:
            if market == Market.CRYPTO:
                return await self._fetch_crypto(symbol)
            elif market == Market.STOCK_US:
                return await self._fetch_us_stock(symbol)
            elif market == Market.FOREX:
                return await self._fetch_forex(symbol)
            else:
                logger.warning(f"市场暂不支持: {market}")
                return None
                
        except Exception as e:
            logger.error(f"获取市场数据失败: {market}/{symbol}: {e}")
            return None
    
    async def _fetch_crypto(self, symbol: str) -> Optional[CrossMarketSignal]:
        """获取加密货币数据"""
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol.upper()}"
        
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read())
                
                return CrossMarketSignal(
                    market=Market.CRYPTO,
                    symbol=symbol,
                    price=float(data.get("lastPrice", 0)),
                    change_24h=float(data.get("priceChangePercent", 0)),
                    direction="LONG" if float(data.get("priceChangePercent", 0)) > 0 else "SHORT",
                    confidence=0.7,
                    volume=float(data.get("quoteVolume", 0)),
                    metadata={"bidPrice": data.get("bidPrice"), "askPrice": data.get("askPrice")}
                )
        except Exception as e:
            logger.error(f"获取加密货币数据失败: {e}")
            return None
    
    async def _fetch_us_stock(self, symbol: str) -> Optional[CrossMarketSignal]:
        """获取美股数据"""
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d"
        
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read())
                meta = data["chart"]["result"][0]["meta"]
                
                return CrossMarketSignal(
                    market=Market.STOCK_US,
                    symbol=symbol,
                    price=meta.get("regularMarketPrice", 0),
                    change_24h=meta.get("regularMarketChangePercent", 0),
                    direction="LONG" if meta.get("regularMarketChangePercent", 0) > 0 else "SHORT",
                    confidence=0.6,
                    volume=meta.get("regularMarketVolume", 0)
                )
        except Exception as e:
            logger.error(f"获取美股数据失败: {e}")
            return None
    
    async def _fetch_forex(self, pair: str) -> Optional[CrossMarketSignal]:
        """获取外汇数据"""
        base, quote = pair.split("/")
        url = f"https://api.exchangerate-api.com/v4/latest/{base}"
        
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read())
                rate = data["rates"].get(quote, 0)
                
                return CrossMarketSignal(
                    market=Market.FOREX,
                    symbol=pair,
                    price=rate,
                    change_24h=0.0,  # 外汇24h变化需要历史数据
                    direction="HOLD",
                    confidence=0.5,
                    volume=0.0
                )
        except Exception as e:
            logger.error(f"获取外汇数据失败: {e}")
            return None
    
    async def scan_all_markets(self) -> Dict[Market, List[CrossMarketSignal]]:
        """扫描所有已启用市场"""
        results = {}
        
        for market in self.get_enabled_markets():
            config = self.markets[market]
            signals = []
            
            for symbol in config.symbols:
                signal = await self.fetch_market_data(market, symbol)
                if signal:
                    signals.append(signal)
            
            results[market] = signals
        
        return results
    
    def get_allocation(self) -> Dict[str, float]:
        """获取市场配置权重"""
        enabled = self.get_enabled_markets()
        total_weight = sum(self.markets[m].weight for m in enabled)
        
        if total_weight == 0:
            return {"CRYPTO": 1.0}
        
        return {
            m.value.upper(): self.markets[m].weight / total_weight 
            for m in enabled
        }
    
    def get_status(self) -> Dict:
        """获取引擎状态"""
        return {
            "total_markets": len(self.markets),
            "enabled_markets": len(self.get_enabled_markets()),
            "markets": {
                m.value: {
                    "name": cfg.name,
                    "enabled": cfg.enabled,
                    "symbols": cfg.symbols,
                    "weight": cfg.weight
                }
                for m, cfg in self.markets.items()
            },
            "allocation": self.get_allocation()
        }


# 全局实例
cross_market_engine = CrossMarketEngine()


if __name__ == "__main__":
    print("✅ 跨市场扩展引擎已初始化")
    print(f"状态: {cross_market_engine.get_status()}")
    
    # 测试获取加密货币数据
    import asyncio
    async def test():
        signal = await cross_market_engine.fetch_market_data(Market.CRYPTO, "BTCUSDT")
        if signal:
            print(f"\nBTC信号:")
            print(f"  价格: ${signal.price:,.2f}")
            print(f"  24h涨跌: {signal.change_24h:+.2f}%")
            print(f"  方向: {signal.direction}")
    
    asyncio.run(test())
