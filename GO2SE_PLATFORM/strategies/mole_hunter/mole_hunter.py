#!/usr/bin/env python3
"""
打地鼠策略 - 高频量化交易系统
Hit-the-Mole High-Frequency Trading Strategy

版本: v2.0
更新: 2026-05-03
"""

import requests
import hmac
import hashlib
import time
import json
from datetime import datetime
from typing import List, Dict, Optional

class MoleHunter:
    """打地鼠高频量化策略"""
    
    def __init__(self, api_key: str, api_secret: str, proxies: dict):
        self.api_key = api_key
        self.api_secret = api_secret
        self.proxies = proxies
        
        # 策略参数
        self.params = {
            "position_size": 0.1,        # 10%仓位
            "max_positions": 5,          # 最多5个仓位
            "stop_loss": 0.02,           # 2%止损
            "take_profit": 0.03,         # 3%止盈
            "scan_interval": 60,          # 扫描间隔60秒
            "min_volatility": 2.0,       # 最小波动2%
            "max_volatility": 8.0,       # 最大波动8%
            "min_volume_24h": 10_000_000,  # 最小日成交量
        }
        
        self.positions = {}  # 当前持仓
        self.trade_history = []  # 交易历史
        
    def scan_market(self) -> List[Dict]:
        """扫描市场，筛选打地鼠候选币种"""
        
        # 获取24h行情
        resp = requests.get(
            "https://api.binance.com/api/v3/ticker/24hr",
            proxies=self.proxies,
            timeout=10
        )
        
        candidates = []
        for t in resp.json():
            if not t["symbol"].endswith("USDT"):
                continue
                
            symbol = t["symbol"].replace("USDT", "")
            price = float(t["lastPrice"])
            change = float(t["priceChangePercent"])
            change_cont = abs(change)
            volume = float(t["quoteVolume"])
            
            # 筛选条件
            if (self.params["min_volatility"] <= change_cont <= self.params["max_volatility"] and
                volume >= self.params["min_volume_24h"] and
                0.0001 <= price <= 100):
                
                # 计算地鼠分数
                mole_score = (change_cont / 10) * 0.5 + (volume / 1e8) * 0.5
                
                candidates.append({
                    "symbol": symbol,
                    "price": price,
                    "change": change,
                    "change_cont": change_cont,
                    "volume": volume,
                    "mole_score": mole_score
                })
        
        # 排序
        candidates.sort(key=lambda x: x["mole_score"], reverse=True)
        return candidates[:10]
    
    def execute_trade(self, symbol: str, side: str, quantity: float) -> Dict:
        """执行交易"""
        
        timestamp = int(time.time() * 1000)
        params = f"symbol={symbol}USDT&side={side}&type=MARKET&quantity={quantity}&timestamp={timestamp}&recvWindow=5000"
        signature = hmac.new(self.api_secret.encode(), params.encode(), hashlib.sha256).hexdigest()
        
        try:
            resp = requests.post(
                f"https://api.binance.com/api/v3/order?{params}&signature={signature}",
                headers={"X-MBX-APIKEY": self.api_key},
                proxies=self.proxies,
                timeout=10
            )
            
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "success": True,
                    "symbol": symbol,
                    "side": side,
                    "quantity": float(data["executedQty"]),
                    "price": float(data.get("cummulativeQuoteQty", 0)) / float(data["executedQty"])
                }
            else:
                return {"success": False, "error": resp.text}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def run(self):
        """运行打地鼠策略"""
        
        print(f"🎯 打地鼠策略启动...")
        print(f"参数: {json.dumps(self.params, indent=2)}")
        
        while True:
            try:
                # 扫描市场
                candidates = self.scan_market()
                
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 扫描到 {len(candidates)} 个候选币种")
                
                # 打印Top5
                for i, c in enumerate(candidates[:5]):
                    print(f"  {i+1}. {c['symbol']}: {c['change']:+.2f}% (分数: {c['mole_score']:.3f})")
                
                # 检查持仓
                for symbol, pos in list(self.positions.items()):
                    # 检查止盈止损
                    current_price = None
                    for c in candidates:
                        if c["symbol"] == symbol:
                            current_price = c["price"]
                            break
                    
                    if current_price:
                        pnl_pct = (current_price - pos["buy_price"]) / pos["buy_price"]
                        
                        if pnl_pct <= -self.params["stop_loss"]:
                            print(f"  🛑 止损 {symbol}: {pnl_pct*100:.2f}%")
                            self.execute_trade(symbol, "SELL", pos["quantity"])
                            del self.positions[symbol]
                            
                        elif pnl_pct >= self.params["take_profit"]:
                            print(f"  🎯 止盈 {symbol}: {pnl_pct*100:.2f}%")
                            self.execute_trade(symbol, "SELL", pos["quantity"])
                            del self.positions[symbol]
                
                time.sleep(self.params["scan_interval"])
                
            except Exception as e:
                print(f"错误: {e}")
                time.sleep(10)


if __name__ == "__main__":
    # 配置
    API_KEY = "YOUR_API_KEY"
    API_SECRET = "YOUR_API_SECRET"
    PROXIES = {"http": "http://172.29.144.1:7897", "https": "http://172.29.144.1:7897"}
    
    # 启动
    hunter = MoleHunter(API_KEY, API_SECRET, PROXIES)
    hunter.run()
