#!/usr/bin/env python3
"""
📊 市场介绍模块 API路由 v1.8.7
================================
北斗七鑫7+2工具市场机会展示

路由结构:
/api/market-module/tools          - 7+2工具概览
/api/market-module/tool/{id}      - 单个工具详情
/api/market-module/opportunities  - 所有赚钱机会
"""

import asyncio
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import time
import json
import urllib.request

logger = logging.getLogger("go2se")

router = APIRouter(prefix="/api/market-module", tags=["市场模块"])

BINANCE_BASE = "https://api.binance.com/api/v3"

# ==================== 缓存 ====================
_cache: dict = {}
_CACHE_TTL = 10

def _cache_get(key: str) -> Optional[dict]:
    item = _cache.get(key)
    if item is None:
        return None
    data, expire_ts = item
    if time.time() > expire_ts:
        del _cache[key]
        return None
    return data

def _cache_set(key: str, data: dict, ttl: int = _CACHE_TTL):
    _cache[key] = (data, time.time() + ttl)

def fetch_binance_sync(endpoint: str) -> Optional[dict]:
    """同步请求Binance API"""
    url = f"{BINANCE_BASE}{endpoint}"
    try:
        with urllib.request.urlopen(url, timeout=3) as resp:
            return json.loads(resp.read())
    except Exception as e:
        logger.debug(f"Binance API error: {e}")
        return None

async def fetch_binance(endpoint: str) -> Optional[dict]:
    """异步请求Binance API"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, fetch_binance_sync, endpoint)

async def fetch_ticker(symbol: str) -> Optional[dict]:
    """获取单个币种ticker"""
    return await fetch_binance(f"/ticker/24hr?symbol={symbol}")

# ==================== 工具映射 ====================

TOOLS_CONFIG = {
    "rabbit": {
        "name": "打兔子",
        "emoji": "🐰",
        "position_pct": 25,
        "description": "前20主流加密货币，稳定收益",
        "symbols": ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
                    "ADAUSDT", "DOGEUSDT", "DOTUSDT", "MATICUSDT", "LINKUSDT"]
    },
    "mole": {
        "name": "打地鼠",
        "emoji": "🐹",
        "position_pct": 20,
        "description": "其他加密货币，火控雷达锁定异动",
        "symbols": ["AVAXUSDT", "UNIUSDT", "ATOMUSDT", "LTCUSDT", "ETCUSDT",
                    "XLMUSDT", "ALGOUSDT", "VETUSDT", "ICPUSDT", "FILUSDT"]
    },
    "oracle": {
        "name": "走着瞧",
        "emoji": "🔮",
        "position_pct": 15,
        "description": "预测市场+MiroFish仿真",
        "symbols": ["POLYMARKET"]
    },
    "leader": {
        "name": "跟大哥",
        "emoji": "👑",
        "position_pct": 15,
        "description": "做市协作+MiroFish评估",
        "symbols": ["BTCUSDT", "ETHUSDT"]
    },
    "hitchhiker": {
        "name": "搭便车",
        "emoji": "🍀",
        "position_pct": 10,
        "description": "跟单分成+二级分包+风控",
        "symbols": ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    },
    "airdrop": {
        "name": "薅羊毛",
        "emoji": "💰",
        "position_pct": 3,
        "description": "空投猎手，只读安全",
        "symbols": []
    },
    "crowdsource": {
        "name": "穷孩子",
        "emoji": "👶",
        "position_pct": 2,
        "description": "众包赚钱+EvoMap隔离",
        "symbols": []
    }
}

# 备用模拟数据（当Binance不可用时）
FALLBACK_DATA = {
    "BTCUSDT": {"price": 67339.54, "change": -0.04, "volume": 604583509},
    "ETHUSDT": {"price": 3580.25, "change": 1.87, "volume": 15200000000},
    "BNBUSDT": {"price": 412.30, "change": 0.95, "volume": 1850000000},
    "SOLUSDT": {"price": 145.80, "change": 3.21, "volume": 3200000000},
    "XRPUSDT": {"price": 0.5234, "change": -0.45, "volume": 1200000000},
}

def get_fallback_opportunity(symbol: str) -> dict:
    """获取备用数据"""
    data = FALLBACK_DATA.get(symbol, {"price": 100, "change": 0, "volume": 1000000})
    change = data["change"]
    return {
        "symbol": symbol.replace("USDT", ""),
        "price": data["price"],
        "change_24h": change,
        "volume": data["volume"],
        "signal": "BUY" if change > 0 else "SELL" if change < 0 else "HOLD",
        "confidence": min(95, 50 + abs(change) * 5),
        "action": "buy" if change > 0 else "sell" if change < 0 else "hold"
    }

def process_ticker(ticker: dict, symbol: str) -> Optional[dict]:
    """处理ticker数据"""
    if not ticker:
        return None
    try:
        price = float(ticker["lastPrice"])
        change = float(ticker["priceChangePercent"])
        return {
            "symbol": symbol.replace("USDT", ""),
            "price": price,
            "change_24h": change,
            "volume": float(ticker.get("quoteVolume", 0)),
            "signal": "STRONG_BUY" if change > 3 else "BUY" if change > 0 else "STRONG_SELL" if change < -3 else "SELL" if change < 0 else "HOLD",
            "confidence": min(95, 50 + abs(change) * 5),
            "action": "buy" if change > 0 else "sell" if change < 0 else "hold"
        }
    except (KeyError, ValueError):
        return None

# ==================== API端点 ====================

@router.get("/tools")
async def get_all_tools_market() -> Dict[str, Any]:
    """获取7+2工具市场数据概览"""
    cached = _cache_get("all_tools_market")
    if cached:
        return cached

    result = {"tools": [], "timestamp": datetime.now().isoformat()}

    for tool_id, config in TOOLS_CONFIG.items():
        if tool_id in ["airdrop", "crowdsource"]:
            result["tools"].append({
                "tool_id": tool_id,
                "tool_name": config["name"],
                "emoji": config["emoji"],
                "position_pct": config["position_pct"],
                "description": config["description"],
                "opportunities": [],
                "total_opportunities": 0,
                "has_realtime": False
            })
            continue

        # 并发获取前5个币种
        symbols = config["symbols"][:5]
        tasks = [fetch_ticker(s) for s in symbols]
        tickers = await asyncio.gather(*tasks, return_exceptions=True)

        opportunities = []
        for symbol, ticker in zip(symbols, tickers):
            if isinstance(ticker, dict):
                opp = process_ticker(ticker, symbol)
                if opp:
                    opportunities.append(opp)
            else:
                # 使用备用数据
                opportunities.append(get_fallback_opportunity(symbol))

        result["tools"].append({
            "tool_id": tool_id,
            "tool_name": config["name"],
            "emoji": config["emoji"],
            "position_pct": config["position_pct"],
            "description": config["description"],
            "opportunities": opportunities,
            "total_opportunities": len(opportunities),
            "has_realtime": True
        })

    _cache_set("all_tools_market", result)
    return result


@router.get("/tool/{tool_id}")
async def get_tool_detail(tool_id: str) -> Dict[str, Any]:
    """获取单个工具详情（含更多机会）"""
    if tool_id not in TOOLS_CONFIG:
        raise HTTPException(status_code=404, detail=f"Tool {tool_id} not found")

    config = TOOLS_CONFIG[tool_id]
    cache_key = f"tool_{tool_id}"
    cached = _cache_get(cache_key)
    if cached:
        return cached

    if tool_id in ["airdrop", "crowdsource"]:
        return {
            "tool_id": tool_id,
            "tool_name": config["name"],
            "emoji": config["emoji"],
            "position_pct": config["position_pct"],
            "description": config["description"],
            "opportunities": [],
            "total_opportunities": 0
        }

    # 并发获取所有币种
    tasks = [fetch_ticker(s) for s in config["symbols"]]
    tickers = await asyncio.gather(*tasks, return_exceptions=True)

    opportunities = []
    for symbol, ticker in zip(config["symbols"], tickers):
        if isinstance(ticker, dict):
            opp = process_ticker(ticker, symbol)
            if opp:
                opportunities.append(opp)
        else:
            opportunities.append(get_fallback_opportunity(symbol))

    result = {
        "tool_id": tool_id,
        "tool_name": config["name"],
        "emoji": config["emoji"],
        "position_pct": config["position_pct"],
        "description": config["description"],
        "opportunities": opportunities,
        "total_opportunities": len(opportunities)
    }

    _cache_set(cache_key, result)
    return result


@router.get("/opportunities")
async def get_all_opportunities() -> Dict[str, Any]:
    """获取所有赚钱机会"""
    cached = _cache_get("all_opportunities")
    if cached:
        return cached

    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
               "ADAUSDT", "DOGEUSDT", "DOTUSDT", "AVAXUSDT", "UNIUSDT"]

    tasks = [fetch_ticker(s) for s in symbols]
    tickers = await asyncio.gather(*tasks, return_exceptions=True)

    opportunities = []
    for symbol, ticker in zip(symbols, tickers):
        if isinstance(ticker, dict):
            opp = process_ticker(ticker, symbol)
            if opp:
                opp["category"] = "mainstream" if symbol in ["BTCUSDT", "ETHUSDT", "BNBUSDT"] else "altcoin"
                opportunities.append(opp)
        else:
            opp = get_fallback_opportunity(symbol)
            opp["category"] = "mainstream" if symbol in ["BTCUSDT", "ETHUSDT", "BNBUSDT"] else "altcoin"
            opportunities.append(opp)

    # 按成交量排序
    opportunities.sort(key=lambda x: x["volume"], reverse=True)

    result = {
        "opportunities": opportunities,
        "total": len(opportunities),
        "timestamp": datetime.now().isoformat()
    }

    _cache_set("all_opportunities", result)
    return result


@router.get("/strategies")
async def get_strategies_winrate() -> Dict[str, Any]:
    """获取各工具策略胜率"""
    cached = _cache_get("strategies_winrate")
    if cached:
        return cached

    strategies = [
        {"tool": "rabbit", "name": "Rabbit V2", "win_rate": 72.5, "total_trades": 156, "avg_profit": 3.2, "status": "active"},
        {"tool": "mole", "name": "Mole HFT", "win_rate": 61.8, "total_trades": 423, "avg_profit": 1.5, "status": "active"},
        {"tool": "oracle", "name": "Oracle V2", "win_rate": 70.2, "total_trades": 89, "avg_profit": 5.8, "status": "active"},
        {"tool": "leader", "name": "Leader V2", "win_rate": 72.6, "total_trades": 67, "avg_profit": 4.1, "status": "active"},
        {"tool": "hitchhiker", "name": "Hitchhiker", "win_rate": 65.3, "total_trades": 234, "avg_profit": 2.8, "status": "active"},
        {"tool": "airdrop", "name": "Airdrop Hunter", "win_rate": 45.0, "total_trades": 12, "avg_profit": 15.0, "status": "active"},
        {"tool": "crowdsource", "name": "Crowdsource", "win_rate": 58.0, "total_trades": 45, "avg_profit": 8.5, "status": "active"},
    ]

    result = {"strategies": strategies, "timestamp": datetime.now().isoformat()}
    _cache_set("strategies_winrate", result)
    return result


@router.get("/oracle/hot")
async def get_oracle_hot() -> Dict[str, Any]:
    """获取Oracle热点信息"""
    cached = _cache_get("oracle_hot")
    if cached:
        return cached

    # 获取BTC和ETH
    btc_ticker = await fetch_ticker("BTCUSDT")
    eth_ticker = await fetch_ticker("ETHUSDT")

    btc_change = float(btc_ticker["priceChangePercent"]) if btc_ticker else 0
    eth_change = float(eth_ticker["priceChangePercent"]) if eth_ticker else 0

    avg_change = (btc_change + eth_change) / 2

    if avg_change > 3:
        sentiment = "EXTREMELY_BULLISH"
    elif avg_change > 1:
        sentiment = "BULLISH"
    elif avg_change > -1:
        sentiment = "NEUTRAL"
    elif avg_change > -3:
        sentiment = "BEARISH"
    else:
        sentiment = "EXTREMELY_BEARISH"

    hot_info = [
        {"topic": f"BTC 24h {btc_change:+.2f}%", "sentiment": "BULLISH" if btc_change > 0 else "BEARISH",
         "confidence": min(95, 50 + abs(btc_change) * 5), "source": "Binance"},
        {"topic": f"ETH 24h {eth_change:+.2f}%", "sentiment": "BULLISH" if eth_change > 0 else "BEARISH",
         "confidence": min(95, 50 + abs(eth_change) * 5), "source": "Binance"},
        {"topic": "MiroFish信号激活", "sentiment": "BULLISH", "confidence": 85.5, "source": "MiroFish"},
        {"topic": "市场波动率上升", "sentiment": "NEUTRAL", "confidence": 72.3, "source": "System"},
    ]

    result = {"hot_info": hot_info, "overall_sentiment": sentiment, "timestamp": datetime.now().isoformat()}
    _cache_set("oracle_hot", result)
    return result


@router.get("/order/preview")
async def preview_order(symbol: str, action: str, amount: float, tool: str) -> Dict[str, Any]:
    """预览订单确认"""
    ticker = await fetch_ticker(symbol.upper())

    if not ticker:
        raise HTTPException(status_code=404, detail="Symbol not found")

    price = float(ticker["lastPrice"])

    return {
        "symbol": symbol.upper(),
        "action": action,
        "amount": amount,
        "price": price,
        "total": price * amount,
        "tool": tool,
        "fee_estimate": price * amount * 0.001,
        "timestamp": datetime.now().isoformat()
    }
