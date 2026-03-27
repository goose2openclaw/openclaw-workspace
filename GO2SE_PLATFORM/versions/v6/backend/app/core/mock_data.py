#!/usr/bin/env python3
"""
🪿 GO2SE 模拟交易测试数据生成器
生成虚拟市场数据用于测试
"""

import random
import time
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass, asdict


@dataclass
class MockMarketTick:
    """模拟市场数据"""
    symbol: str
    price: float
    bid: float
    ask: float
    volume_24h: float
    change_24h: float
    high_24h: float
    low_24h: float
    rsi: float
    timestamp: str


class MockDataGenerator:
    """模拟数据生成器"""
    
    # 主流币种基准价格
    BASE_PRICES = {
        "BTC/USDT": 75000,
        "ETH/USDT": 1850,
        "BNB/USDT": 580,
        "XRP/USDT": 2.45,
        "SOL/USDT": 145,
        "ADA/USDT": 0.85,
        "DOGE/USDT": 0.32,
        "DOT/USDT": 18.5,
        "AVAX/USDT": 42,
        "MATIC/USDT": 0.95,
    }
    
    def __init__(self, volatility: float = 0.02):
        """
        初始化模拟数据生成器
        volatility: 波动率 (0.02 = 2%)
        """
        self.volatility = volatility
        self.current_prices = self.BASE_PRICES.copy()
    
    def generate_tick(self, symbol: str) -> MockMarketTick:
        """生成单个交易对的模拟数据"""
        base_price = self.current_prices.get(symbol, 1000)
        
        # 随机波动
        change_pct = random.uniform(-self.volatility, self.volatility)
        new_price = base_price * (1 + change_pct)
        
        # 更新价格 (模拟连续波动)
        self.current_prices[symbol] = new_price
        
        # 计算其他指标
        spread = new_price * 0.001  # 0.1%买卖价差
        volume = random.uniform(100000, 10000000)
        
        # 随机RSI (30-70之间波动)
        rsi = random.uniform(25, 75)
        
        # 24小时涨跌
        change_24h = random.uniform(-8, 8)
        
        high_24h = new_price * (1 + abs(change_24h) / 100)
        low_24h = new_price * (1 - abs(change_24h) / 100)
        
        return MockMarketTick(
            symbol=symbol,
            price=round(new_price, 4),
            bid=round(new_price - spread, 4),
            ask=round(new_price + spread, 4),
            volume_24h=round(volume, 2),
            change_24h=round(change_24h, 2),
            high_24h=round(high_24h, 4),
            low_24h=round(low_24h, 4),
            rsi=round(rsi, 2),
            timestamp=datetime.now().isoformat()
        )
    
    def generate_all_ticks(self) -> List[MockMarketTick]:
        """生成所有交易对的模拟数据"""
        return [self.generate_tick(sym) for sym in self.BASE_PRICES.keys()]
    
    def generate_signals(self, ticks: List[MockMarketTick]) -> List[Dict]:
        """根据模拟数据生成交易信号"""
        signals = []
        
        for tick in ticks:
            rsi = tick.rsi
            change = tick.change_24h
            
            # RSI策略
            if rsi < 30:
                signal = "buy"
                confidence = round(min(10, (30 - rsi) / 30 * 10 + 5), 1)
                reason = f"RSI超卖: {rsi:.1f}"
            elif rsi > 70:
                signal = "sell"
                confidence = round(min(10, (rsi - 70) / 30 * 10 + 5), 1)
                reason = f"RSI超买: {rsi:.1f}"
            elif rsi < 40:
                signal = "buy"
                confidence = round((40 - rsi) / 40 * 7, 1)
                reason = f"RSI偏低: {rsi:.1f}"
            elif rsi > 60:
                signal = "sell"
                confidence = round((rsi - 60) / 40 * 7, 1)
                reason = f"RSI偏高: {rsi:.1f}"
            else:
                signal = "hold"
                confidence = round(5 + (50 - abs(rsi - 50)) / 10, 1)
                reason = f"RSI中性: {rsi:.1f}"
            
            signals.append({
                "symbol": tick.symbol,
                "signal": signal,
                "confidence": confidence,
                "price": tick.price,
                "rsi": tick.rsi,
                "change_24h": tick.change_24h,
                "reason": reason,
                "timestamp": tick.timestamp
            })
        
        return signals
    
    def generate_portfolio(self) -> Dict:
        """生成模拟持仓数据"""
        holdings = []
        
        for symbol, base_price in self.BASE_PRICES.items():
            # 随机决定是否有持仓
            if random.random() > 0.6:
                quantity = random.uniform(0.01, 1.0)
                entry_price = base_price * random.uniform(0.9, 1.1)
                current_price = base_price
                pnl_pct = (current_price - entry_price) / entry_price * 100
                
                holdings.append({
                    "symbol": symbol,
                    "quantity": round(quantity, 4),
                    "entry_price": round(entry_price, 2),
                    "current_price": round(current_price, 2),
                    "value": round(quantity * current_price, 2),
                    "pnl": round(quantity * (current_price - entry_price), 2),
                    "pnl_pct": round(pnl_pct, 2),
                    "side": random.choice(["long", "short"])
                })
        
        total_value = sum(h["value"] for h in holdings)
        total_pnl = sum(h["pnl"] for h in holdings)
        
        return {
            "holdings": holdings,
            "total_value": round(total_value, 2),
            "total_pnl": round(total_pnl, 2),
            "pnl_pct": round(total_pnl / total_value * 100, 2) if total_value > 0 else 0,
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_wallet_status(self) -> Dict:
        """生成模拟钱包状态"""
        return {
            "main_wallet": {
                "balance": round(random.uniform(80000, 90000), 2),
                "currency": "USDT"
            },
            "sub_wallets": {
                "rabbit": {"balance": round(random.uniform(2000, 3000), 2), "allocated": 2500},
                "mole": {"balance": round(random.uniform(2500, 3500), 2), "allocated": 3000},
                "oracle": {"balance": round(random.uniform(2500, 3500), 2), "allocated": 3000},
                "leader": {"balance": round(random.uniform(1200, 1800), 2), "allocated": 1500},
                "hitchhiker": {"balance": round(random.uniform(800, 1200), 2), "allocated": 1000},
                "airdrop": {"balance": round(random.uniform(1200, 1800), 2), "allocated": 1500},
                "crowd": {"balance": round(random.uniform(300, 700), 2), "allocated": 500},
            },
            "total_balance": round(random.uniform(90000, 100000), 2),
            "timestamp": datetime.now().isoformat()
        }


# 全局模拟数据生成器
mock_generator = MockDataGenerator(volatility=0.015)


def get_mock_market_data(symbol: str = None) -> Dict:
    """获取模拟市场数据API"""
    if symbol:
        tick = mock_generator.generate_tick(symbol)
        return asdict(tick)
    else:
        ticks = mock_generator.generate_all_ticks()
        return {"markets": [asdict(t) for t in ticks]}


def get_mock_signals() -> Dict:
    """获取模拟交易信号API"""
    ticks = mock_generator.generate_all_ticks()
    signals = mock_generator.generate_signals(ticks)
    
    # 分类信号
    buy_signals = [s for s in signals if s["signal"] == "buy"]
    sell_signals = [s for s in signals if s["signal"] == "sell"]
    hold_signals = [s for s in signals if s["signal"] == "hold"]
    
    return {
        "signals": signals,
        "summary": {
            "total": len(signals),
            "buy": len(buy_signals),
            "sell": len(sell_signals),
            "hold": len(hold_signals)
        },
        "timestamp": datetime.now().isoformat()
    }


def get_mock_portfolio() -> Dict:
    """获取模拟持仓API"""
    return mock_generator.generate_portfolio()


def get_mock_wallet() -> Dict:
    """获取模拟钱包API"""
    return mock_generator.generate_wallet_status()


def get_mock_trading_history(count: int = 20) -> Dict:
    """生成模拟交易历史"""
    history = []
    symbols = list(MockDataGenerator.BASE_PRICES.keys())
    
    for i in range(count):
        symbol = random.choice(symbols)
        side = random.choice(["buy", "sell"])
        quantity = round(random.uniform(0.01, 0.5), 4)
        price = round(MockDataGenerator.BASE_PRICES[symbol] * random.uniform(0.98, 1.02), 2)
        
        history.append({
            "id": i + 1,
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": price,
            "total": round(quantity * price, 2),
            "fee": round(quantity * price * 0.001, 2),
            "status": "filled",
            "timestamp": datetime.now().isoformat()
        })
    
    return {
        "trades": history,
        "total_trades": len(history),
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    # 测试
    print("🪿 GO2SE 模拟数据测试")
    print("=" * 50)
    
    print("\n📊 模拟市场数据:")
    data = get_mock_market_data()
    for market in data["markets"][:3]:
        print(f"  {market['symbol']}: ${market['price']} (RSI: {market['rsi']})")
    
    print("\n🎯 模拟交易信号:")
    signals = get_mock_signals()
    print(f"  买入: {signals['summary']['buy']} | 卖出: {signals['summary']['sell']} | 观望: {signals['summary']['hold']}")
    
    print("\n💼 模拟持仓:")
    portfolio = get_mock_portfolio()
    print(f"  总价值: ${portfolio['total_value']} | 总盈亏: ${portfolio['total_pnl']}")
    
    print("\n💰 模拟钱包:")
    wallet = get_mock_wallet()
    print(f"  主钱包: ${wallet['main_wallet']['balance']}")
    
    print("\n✅ 模拟数据生成完成!")
