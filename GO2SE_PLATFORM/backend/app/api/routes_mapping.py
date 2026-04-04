"""
Mapping API路由 - 币种、策略、交易所映射管理
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import re

router = APIRouter(prefix="/api/mapping", tags=["mapping"])

# ==================== 币种Mapping ====================

SYMBOL_MAPPING = {
    # 主流币
    "BTC": {
        "name": "Bitcoin",
        "full_name": "Bitcoin",
        "category": "layer1",
        "exchanges": ["binance", "okx", "bybit", "coinbase"],
        "trading_pairs": ["BTC/USDT", "BTC/BUSD", "BTC/USD"],
        "risk_level": "low",
        "liquidity": "very_high"
    },
    "ETH": {
        "name": "Ethereum",
        "full_name": "Ethereum",
        "category": "layer1",
        "exchanges": ["binance", "okx", "bybit", "coinbase"],
        "trading_pairs": ["ETH/USDT", "ETH/BTC", "ETH/USD"],
        "risk_level": "low",
        "liquidity": "very_high"
    },
    "BNB": {
        "name": "BNB",
        "full_name": "Binance Coin",
        "category": "exchange",
        "exchanges": ["binance"],
        "trading_pairs": ["BNB/USDT", "BNB/BTC"],
        "risk_level": "medium",
        "liquidity": "high"
    },
    "SOL": {
        "name": "Solana",
        "full_name": "Solana",
        "category": "layer1",
        "exchanges": ["binance", "okx", "bybit"],
        "trading_pairs": ["SOL/USDT", "SOL/BTC"],
        "risk_level": "medium",
        "liquidity": "high"
    },
    "XRP": {
        "name": "Ripple",
        "full_name": "XRP",
        "category": "payment",
        "exchanges": ["binance", "okx", "bybit"],
        "trading_pairs": ["XRP/USDT", "XRP/BTC"],
        "risk_level": "medium",
        "liquidity": "high"
    },
    "ADA": {
        "name": "Cardano",
        "full_name": "Cardano",
        "category": "layer1",
        "exchanges": ["binance", "okx", "bybit"],
        "trading_pairs": ["ADA/USDT", "ADA/BTC"],
        "risk_level": "medium",
        "liquidity": "high"
    },
    "DOGE": {
        "name": "Dogecoin",
        "full_name": "Dogecoin",
        "category": "meme",
        "exchanges": ["binance", "okx", "bybit"],
        "trading_pairs": ["DOGE/USDT", "DOGE/BTC"],
        "risk_level": "high",
        "liquidity": "high"
    },
    "DOT": {
        "name": "Polkadot",
        "full_name": "Polkadot",
        "category": "layer1",
        "exchanges": ["binance", "okx", "bybit"],
        "trading_pairs": ["DOT/USDT", "DOT/BTC"],
        "risk_level": "medium",
        "liquidity": "medium"
    },
    # 预测市场
    "POLYMATIC": {
        "name": "Polymarket",
        "full_name": "Polymarket Token",
        "category": "prediction",
        "exchanges": ["polymarket"],
        "trading_pairs": ["POLY/USDC"],
        "risk_level": "high",
        "liquidity": "low"
    }
}

# ==================== 策略Mapping ====================

STRATEGY_MAPPING = {
    # 🐰 打兔子 - 主流币策略
    "rabbit_v2": {
        "name": "Rabbit V2",
        "tool": "🐰 打兔子",
        "tool_id": "rabbit",
        "category": "trend_following",
        "description": "趋势跟踪策略，交易前20主流加密货币",
        "symbols": ["BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOT"],
        "timeframe": "1h,4h,1d",
        "risk_level": "medium",
        "win_rate": 0.72,
        "sharpe_ratio": 1.85,
        "max_drawdown": 0.08,
        "indicators": ["EMA", "MACD", "RSI"],
        "parameters": {
            "ema_period": 20,
            "rsi_period": 14,
            "macd_fast": 12,
            "macd_slow": 26
        }
    },
    "rabbit": {
        "name": "Rabbit",
        "tool": "🐰 打兔子",
        "tool_id": "rabbit",
        "category": "trend_following",
        "description": "基础趋势策略",
        "symbols": ["BTC", "ETH", "BNB"],
        "timeframe": "4h,1d",
        "risk_level": "medium",
        "win_rate": 0.68,
        "sharpe_ratio": 1.65,
        "max_drawdown": 0.10
    },
    "crypto_dca": {
        "name": "DCA定投",
        "tool": "🐰 打兔子",
        "tool_id": "rabbit",
        "category": "dca",
        "description": "美元成本平均法定投",
        "symbols": ["BTC", "ETH", "SOL"],
        "timeframe": "1d,1w",
        "risk_level": "low",
        "win_rate": 0.75,
        "sharpe_ratio": 1.92,
        "max_drawdown": 0.03
    },
    
    # 🐹 打地鼠 - 异动扫描
    "mole_v2": {
        "name": "Mole V2",
        "tool": "🐹 打地鼠",
        "tool_id": "mole",
        "category": "momentum",
        "description": "动量策略，扫描异动币种",
        "symbols": [],  # 扫描所有
        "timeframe": "15m,1h",
        "risk_level": "high",
        "win_rate": 0.65,
        "sharpe_ratio": 1.45,
        "max_drawdown": 0.12,
        "indicators": ["RSI", "ATR", "Volume"]
    },
    "mole": {
        "name": "Mole",
        "tool": "🐹 打地鼠",
        "tool_id": "mole",
        "category": "momentum",
        "description": "基础动量策略",
        "symbols": [],
        "timeframe": "1h,4h",
        "risk_level": "high",
        "win_rate": 0.62,
        "sharpe_ratio": 1.32,
        "max_drawdown": 0.15
    },
    
    # 🔮 走着瞧 - 预测市场
    "oracle": {
        "name": "Oracle预测",
        "tool": "🔮 走着瞧",
        "tool_id": "oracle",
        "category": "prediction",
        "description": "预测市场策略",
        "symbols": ["POLYMATIC"],
        "timeframe": "1h,4h,1d",
        "risk_level": "medium",
        "win_rate": 0.70,
        "sharpe_ratio": 1.55,
        "max_drawdown": 0.07,
        "indicators": ["Sentiment", "Volume", "MiroFish"]
    },
    
    # 👑 跟大哥 - 做市协作
    "leader_v2": {
        "name": "Leader V2",
        "tool": "👑 跟大哥",
        "tool_id": "leader",
        "category": "copy_trading",
        "description": "跟单交易策略",
        "symbols": ["BTC", "ETH", "SOL", "XRP"],
        "timeframe": "1h,4h,1d",
        "risk_level": "medium",
        "win_rate": 0.68,
        "sharpe_ratio": 1.50,
        "max_drawdown": 0.06,
        "indicators": ["LeaderSignals", "Correlation"]
    },
    "smart_rebalance": {
        "name": "智能再平衡",
        "tool": "👑 跟大哥",
        "tool_id": "leader",
        "category": "rebalancing",
        "description": "动态资产再平衡",
        "symbols": ["BTC", "ETH", "USDT"],
        "timeframe": "1d,1w",
        "risk_level": "low",
        "win_rate": 0.72,
        "sharpe_ratio": 1.80,
        "max_drawdown": 0.04
    },
    
    # 🍀 搭便车 - 跟单分成
    "signal_optimizer": {
        "name": "信号优化器",
        "tool": "🍀 搭便车",
        "tool_id": "hitchhiker",
        "category": "signal",
        "description": "多信号聚合优化",
        "symbols": ["BTC", "ETH", "BNB", "SOL"],
        "timeframe": "1h,4h,1d",
        "risk_level": "medium",
        "win_rate": 0.75,
        "sharpe_ratio": 1.90,
        "max_drawdown": 0.05,
        "indicators": ["MultiSignal", "Confidence"]
    },
    
    # 🛡️ 声纳 - 风控
    "sonar": {
        "name": "声纳库123模型",
        "tool": "🛡️ 声纳",
        "tool_id": "sonar",
        "category": "risk_management",
        "description": "123趋势模型风控",
        "symbols": [],  # 全市场
        "timeframe": "all",
        "risk_level": "low",
        "win_rate": 0.70,
        "sharpe_ratio": 1.70,
        "max_drawdown": 0.06,
        "indicators": ["EMA", "RSI", "MACD", "Volume"]
    },
    
    # 🔮 MiroFish - 核心验证
    "mirofish": {
        "name": "MiroFish共识",
        "tool": "🔮 MiroFish",
        "tool_id": "mirofish",
        "category": "ai_consensus",
        "description": "100智能体AI共识验证",
        "symbols": ["BTC", "ETH", "SOL", "XRP", "ADA"],
        "timeframe": "1h,4h,1d",
        "risk_level": "medium",
        "win_rate": 0.78,
        "sharpe_ratio": 2.10,
        "max_drawdown": 0.05,
        "indicators": ["MiroFish", "Confidence"]
    }
}

# ==================== 交易所Mapping ====================

EXCHANGE_MAPPING = {
    "binance": {
        "name": "Binance",
        "type": "cex",
        "status": "active",
        "apis": {
            "spot": "https://api.binance.com",
            "futures": "https://fapi.binance.com"
        },
        "fees": {
            "maker": 0.001,
            "taker": 0.001
        },
        "features": ["spot", "futures", "margin", "staking"]
    },
    "okx": {
        "name": "OKX",
        "type": "cex",
        "status": "active",
        "apis": {
            "spot": "https://www.okx.com/api/v5"
        },
        "fees": {
            "maker": 0.0008,
            "taker": 0.001
        },
        "features": ["spot", "futures", "defi"]
    },
    "bybit": {
        "name": "Bybit",
        "type": "cex",
        "status": "active",
        "apis": {
            "spot": "https://api.bybit.com"
        },
        "fees": {
            "maker": 0.001,
            "taker": 0.001
        },
        "features": ["spot", "futures", "options"]
    },
    "polymarket": {
        "name": "Polymarket",
        "type": "prediction",
        "status": "active",
        "apis": {
            "market": "https://gamma-api.polymarket.com"
        },
        "fees": {
            "maker": 0.0,
            "taker": 0.02
        },
        "features": ["prediction", "markets"]
    }
}


# ==================== API路由 ====================

@router.get("/symbols")
async def get_symbol_mapping(
    category: Optional[str] = None,
    risk_level: Optional[str] = None,
    search: Optional[str] = None
):
    """获取币种Mapping"""
    results = SYMBOL_MAPPING
    
    if category:
        results = {k: v for k, v in results.items() if v.get("category") == category}
    
    if risk_level:
        results = {k: v for k, v in results.items() if v.get("risk_level") == risk_level}
    
    if search:
        search = search.lower()
        results = {
            k: v for k, v in results.items()
            if search in k.lower() or search in v.get("name", "").lower()
        }
    
    return {
        "symbols": results,
        "total": len(results)
    }

@router.get("/symbols/{symbol}")
async def get_symbol_detail(symbol: str):
    """获取单个币种详情"""
    symbol = symbol.upper()
    if symbol not in SYMBOL_MAPPING:
        return {"error": "symbol not found"}
    return SYMBOL_MAPPING[symbol]

@router.get("/strategies")
async def get_strategy_mapping(
    tool: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None
):
    """获取策略Mapping"""
    results = STRATEGY_MAPPING
    
    if tool:
        results = {k: v for k, v in results.items() if v.get("tool_id") == tool}
    
    if category:
        results = {k: v for k, v in results.items() if v.get("category") == category}
    
    if search:
        search = search.lower()
        results = {
            k: v for k, v in results.items()
            if search in k.lower() or search in v.get("name", "").lower()
        }
    
    return {
        "strategies": results,
        "total": len(results),
        "by_tool": {
            "rabbit": len([k for k, v in results.items() if v.get("tool_id") == "rabbit"]),
            "mole": len([k for k, v in results.items() if v.get("tool_id") == "mole"]),
            "oracle": len([k for k, v in results.items() if v.get("tool_id") == "oracle"]),
            "leader": len([k for k, v in results.items() if v.get("tool_id") == "leader"]),
            "hitchhiker": len([k for k, v in results.items() if v.get("tool_id") == "hitchhiker"]),
            "sonar": len([k for k, v in results.items() if v.get("tool_id") == "sonar"]),
            "mirofish": len([k for k, v in results.items() if v.get("tool_id") == "mirofish"])
        }
    }

@router.get("/strategies/{strategy_id}")
async def get_strategy_detail(strategy_id: str):
    """获取单个策略详情"""
    if strategy_id not in STRATEGY_MAPPING:
        return {"error": "strategy not found"}
    return STRATEGY_MAPPING[strategy_id]

@router.get("/exchanges")
async def get_exchange_mapping():
    """获取交易所Mapping"""
    return {
        "exchanges": EXCHANGE_MAPPING,
        "total": len(EXCHANGE_MAPPING)
    }

@router.get("/exchanges/{exchange}")
async def get_exchange_detail(exchange: str):
    """获取单个交易所详情"""
    exchange = exchange.lower()
    if exchange not in EXCHANGE_MAPPING:
        return {"error": "exchange not found"}
    return EXCHANGE_MAPPING[exchange]

@router.get("/search")
async def search_mapping(q: str = Query(..., min_length=1)):
    """全局搜索Mapping"""
    q = q.lower()
    results = {
        "symbols": [],
        "strategies": [],
        "exchanges": []
    }
    
    # 搜索币种
    for symbol, data in SYMBOL_MAPPING.items():
        if q in symbol.lower() or q in data.get("name", "").lower():
            results["symbols"].append({"id": symbol, **data})
    
    # 搜索策略
    for strategy_id, data in STRATEGY_MAPPING.items():
        if q in strategy_id.lower() or q in data.get("name", "").lower():
            results["strategies"].append({"id": strategy_id, **data})
    
    # 搜索交易所
    for exchange, data in EXCHANGE_MAPPING.items():
        if q in exchange.lower() or q in data.get("name", "").lower():
            results["exchanges"].append({"id": exchange, **data})
    
    return {
        "query": q,
        "results": results,
        "total": len(results["symbols"]) + len(results["strategies"]) + len(results["exchanges"])
    }

@router.post("/symbols/{symbol}")
async def update_symbol(symbol: str, data: dict):
    """更新币种Mapping"""
    symbol = symbol.upper()
    if symbol in SYMBOL_MAPPING:
        SYMBOL_MAPPING[symbol].update(data)
    else:
        SYMBOL_MAPPING[symbol] = data
    
    return {"status": "updated", "symbol": symbol}

@router.post("/strategies/{strategy_id}")
async def update_strategy(strategy_id: str, data: dict):
    """更新策略Mapping"""
    if strategy_id in STRATEGY_MAPPING:
        STRATEGY_MAPPING[strategy_id].update(data)
    else:
        STRATEGY_MAPPING[strategy_id] = data
    
    return {"status": "updated", "strategy_id": strategy_id}
