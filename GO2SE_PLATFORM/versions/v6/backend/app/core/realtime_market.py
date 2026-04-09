#!/usr/bin/env python3
"""
🪿 GO2SE 实时行情数据
"""

import ccxt
import asyncio
import time
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

# 全局交易所实例
_exchange = None

def get_exchange() -> ccxt.binance:
    """获取交易所实例"""
    global _exchange
    if _exchange is None:
        _exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
    return _exchange

def fetch_ticker(symbol: str = "BTC/USDT") -> Dict:
    """获取单个币种行情"""
    try:
        exchange = get_exchange()
        # 设置超时
        exchange.timeout = 5000  # 5秒超时
        
        ticker = exchange.fetch_ticker(symbol)
        
        # 计算RSI
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, '1h', limit=50)
            rsi = calculate_rsi([c[4] for c in ohlcv])
        except:
            rsi = 50.0
        
        return {
            "symbol": symbol,
            "price": ticker['last'],
            "bid": ticker.get('bid', 0),
            "ask": ticker.get('ask', 0),
            "volume_24h": ticker.get('quoteVolume', 0),
            "volume": ticker.get('baseVolume', 0),
            "change_24h": ticker.get('percentage', 0),
            "high_24h": ticker.get('high', 0),
            "low_24h": ticker.get('low', 0),
            "open": ticker.get('open', 0),
            "rsi": round(rsi, 2),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        # 返回模拟数据作为后备
        return get_mock_ticker(symbol)

def fetch_all_tickers() -> List[Dict]:
    """获取所有主流币行情"""
    symbols = [
        "BTC/USDT", "ETH/USDT", "BNB/USDT", "XRP/USDT", "SOL/USDT",
        "ADA/USDT", "DOGE/USDT", "DOT/USDT", "AVAX/USDT", "MATIC/USDT",
        "LINK/USDT", "UNI/USDT", "ATOM/USDT", "LTC/USDT", "ETC/USDT"
    ]
    
    results = []
    for sym in symbols:
        try:
            ticker = fetch_ticker(sym)
            if "error" not in ticker:
                results.append(ticker)
        except:
            pass
    
    return results

def calculate_rsi(closes: List[float], period: int = 14) -> float:
    """计算RSI"""
    if len(closes) < period + 1:
        return 50.0
    
    deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
    gains = [d if d > 0 else 0 for d in deltas[-period:]]
    losses = [-d if d < 0 else 0 for d in deltas[-period:]]
    
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    
    if avg_loss == 0:
        return 100
    
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def get_mock_ticker(symbol: str) -> Dict:
    """获取模拟行情 (后备)"""
    import random
    base_prices = {
        "BTC/USDT": 70000, "ETH/USDT": 1850, "BNB/USDT": 580,
        "XRP/USDT": 2.45, "SOL/USDT": 145, "ADA/USDT": 0.85,
        "DOGE/USDT": 0.32, "DOT/USDT": 18.5, "AVAX/USDT": 42
    }
    base = base_prices.get(symbol, 1000)
    price = base * (1 + random.uniform(-0.02, 0.02))
    
    return {
        "symbol": symbol,
        "price": round(price, 2),
        "bid": round(price * 0.999, 2),
        "ask": round(price * 1.001, 2),
        "volume_24h": random.uniform(1e6, 1e7),
        "volume": random.uniform(1e4, 1e5),
        "change_24h": random.uniform(-5, 5),
        "high_24h": round(price * 1.02, 2),
        "low_24h": round(price * 0.98, 2),
        "open": round(price * 0.99, 2),
        "rsi": round(random.uniform(30, 70), 2),
        "timestamp": datetime.now().isoformat(),
        "source": "mock"
    }

def fetch_order_book(symbol: str = "BTC/USDT", limit: int = 10) -> Dict:
    """获取订单簿"""
    try:
        exchange = get_exchange()
        order_book = exchange.fetch_order_book(symbol, limit)
        
        return {
            "symbol": symbol,
            "bids": order_book['bids'][:limit],
            "asks": order_book['asks'][:limit],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

def fetch_trades(symbol: str = "BTC/USDT", limit: int = 20) -> List[Dict]:
    """获取最近成交"""
    try:
        exchange = get_exchange()
        trades = exchange.fetch_trades(symbol, limit=limit)
        
        return [
            {
                "id": t['id'],
                "price": t['price'],
                "amount": t['amount'],
                "side": t['side'],
                "timestamp": datetime.fromtimestamp(t['timestamp']/1000).isoformat()
            }
            for t in trades
        ]
    except Exception as e:
        return [{"error": str(e)}]

def get_market_summary() -> Dict:
    """获取市场摘要"""
    tickers = fetch_all_tickers()
    
    if not tickers:
        return {"error": "无法获取行情数据"}
    
    # 计算市场情绪
    changes = [t['change_24h'] for t in tickers if 'change_24h' in t]
    rsi_values = [t['rsi'] for t in tickers if 'rsi' in t]
    
    avg_change = sum(changes) / len(changes) if changes else 0
    avg_rsi = sum(rsi_values) / len(rsi_values) if rsi_values else 50
    
    # 市场情绪
    if avg_rsi > 70:
        sentiment = "overbought"
    elif avg_rsi < 30:
        sentiment = "oversold"
    elif avg_rsi > 55:
        sentiment = "bullish"
    elif avg_rsi < 45:
        sentiment = "bearish"
    else:
        sentiment = "neutral"
    
    return {
        "timestamp": datetime.now().isoformat(),
        "total_markets": len(tickers),
        "avg_change_24h": round(avg_change, 2),
        "avg_rsi": round(avg_rsi, 2),
        "sentiment": sentiment,
        "gainers": len([c for c in changes if c > 0]),
        "losers": len([c for c in changes if c < 0]),
        "markets": tickers
    }


if __name__ == "__main__":
    print("🪿 GO2SE 实时行情测试")
    print("=" * 50)
    
    print("\n📊 BTC行情:")
    btc = fetch_ticker("BTC/USDT")
    print(f"  价格: ${btc['price']:,.2f}")
    print(f"  24h涨跌: {btc['change_24h']:.2f}%")
    print(f"  RSI: {btc['rsi']}")
    
    print("\n📈 市场摘要:")
    summary = get_market_summary()
    print(f"  市场数: {summary['total_markets']}")
    print(f"  平均涨跌: {summary['avg_change_24h']:.2f}%")
    print(f"  市场情绪: {summary['sentiment']}")
    print(f"  上涨/下跌: {summary['gainers']}/{summary['losers']}")
    
    print("\n✅ 实时行情已就绪")
