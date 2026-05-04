#!/usr/bin/env python3
"""
走着瞧策略 - 市场预测交易系统
Walk-and-See Strategy - Market Prediction Trading

版本: v1.0
更新: 2026-05-03
"""

import requests
import hmac
import hashlib
import time
import json
from datetime import datetime
from typing import List, Dict

class WalkAndSee:
    """走着瞧策略 - 预测市场走势"""
    
    def __init__(self, api_key: str, api_secret: str, proxies: dict):
        self.api_key = api_key
        self.api_secret = api_secret
        self.proxies = proxies
        
        # 策略参数
        self.params = {
            "min_predict_score": 0.5,     # 最小预测分数
            "min_win_rate": 55,            # 最小胜率
            "position_ratio": 0.7,         # 策略资金比例
            "reserve_ratio": 0.3,          # 观望资金比例
            "stop_loss": 0.03,             # 3%止损
            "take_profit": 0.05,           # 5%止盈
            "scan_interval": 300,           # 5分钟扫描
        }
        
        self.positions = {}
        self.trade_history = []
    
    def get_klines(self, symbol: str, interval: str = "1h", limit: int = 48) -> List:
        """获取K线数据"""
        resp = requests.get(
            "https://api.binance.com/api/v3/klines",
            params={"symbol": symbol, "interval": interval, "limit": limit},
            proxies=self.proxies, timeout=10
        )
        return resp.json() if resp.status_code == 200 else []
    
    def calculate_predict_score(self, symbol: str) -> Dict:
        """计算预测分数"""
        klines = self.get_klines(f"{symbol}USDT")
        if not klines:
            return {"score": 0, "trend": "unknown"}
        
        closes = [float(k[4]) for k in klines]
        current_price = closes[-1]
        
        # 计算指标
        change_24h = (closes[-1] - closes[-24]) / closes[-24] * 100 if len(closes) >= 24 else 0
        
        # 波动率
        returns = [(closes[i] - closes[i-1]) / closes[i-1] * 100 for i in range(1, len(closes))]
        volatility = sum(abs(r) for r in returns) / len(returns) if returns else 0
        
        # 移动平均
        ma12 = sum(closes[-12:]) / 12 if len(closes) >= 12 else sum(closes) / len(closes)
        ma24 = sum(closes[-24:]) / 24 if len(closes) >= 24 else sum(closes) / len(closes)
        
        # 趋势
        if current_price > ma12 > ma24:
            trend = "上涨"
            trend_score = 1
        elif current_price > ma12:
            trend = "强势上涨"
            trend_score = 2
        elif current_price < ma12 < ma24:
            trend = "下跌"
            trend_score = -1
        elif current_price < ma12:
            trend = "强势下跌"
            trend_score = -2
        else:
            trend = "震荡"
            trend_score = 0
        
        # 预测分数
        score = trend_score * 0.4 + (change_24h / 10) * 0.3 + (1 / (volatility + 1)) * 0.3
        
        return {
            "price": current_price,
            "change_24h": change_24h,
            "volatility": volatility,
            "trend": trend,
            "trend_score": trend_score,
            "score": score
        }
    
    def scan_market(self) -> List[Dict]:
        """扫描市场"""
        coins = ["BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "LINK", "DOGE"]
        results = []
        
        for coin in coins:
            try:
                data = self.calculate_predict_score(coin)
                data["coin"] = coin
                results.append(data)
            except:
                pass
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def execute_trade(self, symbol: str, side: str, quantity: float) -> Dict:
        """执行交易"""
        timestamp = int(time.time() * 1000)
        params = f"symbol={symbol}USDT&side={side}&type=MARKET&quantity={quantity:.6f}&timestamp={timestamp}&recvWindow=5000"
        signature = hmac.new(self.api_secret.encode(), params.encode(), hashlib.sha256).hexdigest()
        
        try:
            resp = requests.post(
                f"https://api.binance.com/api/v3/order?{params}&signature={signature}",
                headers={"X-MBX-APIKEY": self.api_key},
                proxies=self.proxies, timeout=10
            )
            
            if resp.status_code == 200:
                data = resp.json()
                return {"success": True, "executed": float(data["executedQty"])}
            return {"success": False, "error": resp.text}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def run(self):
        """运行策略"""
        print("🎯 走着瞧策略启动...")
        print(f"参数: {json.dumps(self.params, indent=2)}")
        
        while True:
            try:
                # 扫描市场
                candidates = self.scan_market()
                
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 扫描完成")
                
                # 打印结果
                for c in candidates[:5]:
                    print(f"  {c['coin']}: {c['score']:+.3f} ({c['trend']})")
                
                time.sleep(self.params["scan_interval"])
                
            except Exception as e:
                print(f"错误: {e}")
                time.sleep(60)


if __name__ == "__main__":
    API_KEY = "QPM55JoNnHSV7C7PllgNbTAxpzy9RaBjoKprgHuIE9GJUeQoVIGu69ICPnmBXp61"
    API_SECRET = "BSOTWqsVsncRk13DMDJ2YDRQks8XvrajArQDPW2jY8sDwNtcgb5da8H3x6qF3hJk"
    PROXIES = {"http": "http://172.29.144.1:7897", "https": "http://172.29.144.1:7897"}
    
    strategy = WalkAndSee(API_KEY, API_SECRET, PROXIES)
    strategy.run()
