"""
🔗 跨市场套利模块
===================
跨交易所、跨币种、跨期的三角套利
2026-04-04
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque
import math

@dataclass
class ArbitrageOpportunity:
    """套利机会"""
    id: str
    type: str  # exchange, triangle, calendar
    symbol: str
    path: List[str]  # 交易路径
    prices: Dict[str, float]  # 各交易所/品种价格
    spread_pct: float
    volume: float
    confidence: float
    expected_profit_pct: float
    timestamp: float = field(default_factory=time.time)
    expires_at: float = 0  # 过期时间


class CrossMarketArbitrage:
    """
    跨市场套利引擎
    支持:
    1. 跨交易所套利 (Exchange Arbitrage)
    2. 三角套利 (Triangle Arbitrage)  
    3. 跨期套利 (Calendar Arbitrage)
    """
    
    VERSION = "v1.0-cross-market"
    
    def __init__(self, config: Optional[Dict] = None):
        self.name = "🔗 跨市场套利"
        self.version = self.VERSION
        
        # 配置
        self.config = config or {}
        self.min_spread = self.config.get("min_spread", 0.001)  # 0.1%
        self.min_volume = self.config.get("min_volume", 1000000)  # 100万
        self.max_position = self.config.get("max_position", 0.05)  # 5%
        self.confidence_threshold = self.config.get("confidence_threshold", 0.6)
        
        # 状态
        self.opportunities: deque = deque(maxlen=500)
        self.active_trades: Dict[str, dict] = {}
        self.stats = {
            "total_scans": 0,
            "opportunities_found": 0,
            "trades_executed": 0,
            "profitable_trades": 0,
            "avg_profit_pct": 0.0,
        }
        
        # 交易所配置
        self.exchanges = {
            "binance": {"priority": 1, "fee": 0.001},
            "bybit": {"priority": 2, "fee": 0.0015},
            "okx": {"priority": 3, "fee": 0.001},
            "huobi": {"priority": 4, "fee": 0.002},
        }
        
        # 三角套利路径 (示例)
        self.triangle_paths = [
            ["BTC", "ETH", "USDT"],   # BTC->ETH->USDT
            ["ETH", "BTC", "USDT"],   # ETH->BTC->USDT
            ["BTC", "SOL", "USDT"],   # BTC->SOL->USDT
            ["ETH", "SOL", "USDT"],   # ETH->SOL->USDT
        ]
        
        # 连接池
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            connector = aiohttp.TCPConnector(limit=20, keepalive_timeout=30)
            timeout = aiohttp.ClientTimeout(total=2.0)
            self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        return self.session
    
    async def _fetch_price(self, exchange: str, symbol: str) -> Optional[float]:
        """获取单个交易所价格"""
        try:
            session = await self._get_session()
            
            # 构造URL (简化)
            endpoints = {
                "binance": f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT",
                "bybit": f"https://api.bybit.com/v5/market/tickers?category=spot&symbol={symbol}USDT",
                "okx": f"https://www.okx.com/api/v5/market/ticker?instId={symbol}-USDT",
            }
            
            url = endpoints.get(exchange)
            if not url:
                return None
            
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=1.0)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if "price" in data:
                        return float(data["price"])
                    # 解析不同交易所格式
                    if "data" in data and data["data"]:
                        return float(data["data"][0].get("last", 0))
        except Exception:
            pass
        return None
    
    async def scan_exchange_arbitrage(self, symbols: List[str]) -> List[ArbitrageOpportunity]:
        """
        扫描跨交易所套利机会
        原理: 同一币种在不同交易所价格差异
        """
        opportunities = []
        
        for symbol in symbols:
            # 并行获取所有交易所价格
            tasks = {
                ex: self._fetch_price(ex, symbol)
                for ex in self.exchanges.keys()
            }
            
            results = await asyncio.gather(*tasks.values(), return_exceptions=True)
            
            prices = {}
            for ex, result in zip(tasks.keys(), results):
                if isinstance(result, (int, float)) and result > 0:
                    prices[ex] = result
            
            if len(prices) < 2:
                continue
            
            # 找最优买卖对
            sorted_prices = sorted(prices.items(), key=lambda x: x[1])
            best_buy_ex = sorted_prices[0][0]  # 最低价
            best_sell_ex = sorted_prices[-1][0]  # 最高价
            buy_price = sorted_prices[0][1]
            sell_price = sorted_prices[-1][1]
            
            spread = (sell_price - buy_price) / buy_price
            
            if spread >= self.min_spread:
                # 估算手续费影响
                buy_fee = self.exchanges[best_buy_ex]["fee"]
                sell_fee = self.exchanges[best_sell_ex]["fee"]
                net_spread = spread - buy_fee - sell_fee
                
                if net_spread > 0:
                    opp = ArbitrageOpportunity(
                        id=f"ex_{symbol}_{int(time.time())}",
                        type="exchange",
                        symbol=symbol,
                        path=[best_buy_ex, best_sell_ex],
                        prices=prices,
                        spread_pct=spread,
                        volume=1000000,  # 模拟
                        confidence=min(net_spread * 10, 1.0),
                        expected_profit_pct=net_spread,
                    )
                    opportunities.append(opp)
                    self.opportunities.append(opp)
        
        self.stats["total_scans"] += 1
        self.stats["opportunities_found"] += len(opportunities)
        
        return opportunities
    
    async def scan_triangle_arbitrage(self) -> List[ArbitrageOpportunity]:
        """
        扫描三角套利机会
        原理: BTC->ETH->USDT->BTC 循环交易
        """
        opportunities = []
        
        # 获取所有相关币种价格
        symbols = ["BTC", "ETH", "SOL", "BNB", "XRP"]
        
        prices = {}
        for symbol in symbols:
            tasks = {ex: self._fetch_price(ex, symbol) for ex in self.exchanges.keys()}
            results = await asyncio.gather(*tasks.values(), return_exceptions=True)
            
            for ex, result in zip(tasks.keys(), results):
                if isinstance(result, (int, float)) and result > 0:
                    if symbol not in prices:
                        prices[symbol] = {}
                    prices[symbol][ex] = result
        
        # 检查每个三角路径
        for path in self.triangle_paths:
            if not all(s in prices for s in path):
                continue
            
            # 使用binance作为基准
            if not all("binance" in prices[s] for s in path):
                continue
            
            try:
                # 路径: path[0] -> path[1] -> path[2] -> path[0]
                # 示例: BTC -> ETH -> USDT -> BTC
                
                # Step 1: 用BTC买ETH
                btc_eth = prices["ETH"]["binance"] / prices["BTC"]["binance"]
                
                # Step 2: 用ETH买USDT (反向)
                eth_usdt = prices["ETH"]["binance"]  # ETH/USDT
                
                # Step 3: USDT买回BTC
                usdt_btc = prices["BTC"]["binance"]  # BTC/USDT
                
                # 计算循环收益
                # 1 BTC -> ETH -> USDT -> BTC
                initial = 1.0
                step1 = initial / btc_eth  # 多少ETH
                step2 = step1 * eth_usdt  # 多少USDT
                step3 = step2 / usdt_btc  # 多少BTC
                
                profit_pct = (step3 - initial) / initial
                
                if profit_pct > self.min_spread:
                    opp = ArbitrageOpportunity(
                        id=f"tri_{path}_{int(time.time())}",
                        type="triangle",
                        symbol="/".join(path),
                        path=path,
                        prices={
                            "BTC/USDT": prices["BTC"]["binance"],
                            "ETH/USDT": prices["ETH"]["binance"],
                            "ETH/BTC": btc_eth,
                        },
                        spread_pct=profit_pct,
                        volume=1000000,
                        confidence=min(abs(profit_pct) * 20, 1.0),
                        expected_profit_pct=profit_pct,
                    )
                    opportunities.append(opp)
                    self.opportunities.append(opp)
                    
            except Exception:
                continue
        
        self.stats["opportunities_found"] += len(opportunities)
        return opportunities
    
    async def scan_all(self, symbols: List[str]) -> Dict[str, List[ArbitrageOpportunity]]:
        """扫描所有套利机会"""
        # 并行执行两种扫描
        exchange_opps, triangle_opps = await asyncio.gather(
            self.scan_exchange_arbitrage(symbols),
            self.scan_triangle_arbitrage(),
        )
        
        return {
            "exchange": exchange_opps,
            "triangle": triangle_opps,
            "total": len(exchange_opps) + len(triangle_opps),
        }
    
    async def execute_opportunity(self, opp: ArbitrageOpportunity) -> dict:
        """执行套利"""
        # 检查置信度
        if opp.confidence < self.confidence_threshold:
            return {"status": "rejected", "reason": "confidence_too_low"}
        
        # 检查资金
        position_size = opp.volume * 0.01  # 假设用1%成交量
        if position_size > self.max_position * 10000:  # 相对于1万本金
            return {"status": "rejected", "reason": "position_too_large"}
        
        # 模拟执行
        result = {
            "status": "executed",
            "opportunity_id": opp.id,
            "type": opp.type,
            "symbol": opp.symbol,
            "path": opp.path,
            "spread": f"{opp.spread_pct:.3%}",
            "expected_profit": f"{opp.expected_profit_pct:.3%}",
            "timestamp": datetime.now().isoformat(),
        }
        
        self.stats["trades_executed"] += 1
        if opp.expected_profit_pct > 0:
            self.stats["profitable_trades"] += 1
        
        return result
    
    def get_stats(self) -> dict:
        """获取统计"""
        stats = {**self.stats}
        if stats["trades_executed"] > 0:
            stats["avg_profit_pct"] = (
                stats["profitable_trades"] / stats["trades_executed"] * 100
            )
        return stats
    
    async def close(self):
        """关闭资源"""
        if self.session and not self.session.closed:
            await self.session.close()


# 导出
__all__ = [
    "CrossMarketArbitrage",
    "ArbitrageOpportunity",
]
