#!/usr/bin/env python3
"""打地鼠实盘交易"""
import requests
import hmac
import hashlib
import time
from datetime import datetime

API_KEY = "QPM55JoNnHSV7C7PllgNbTAxpzy9RaBjoKprgHuIE9GJUeQoVIGu69ICPnmBXp61"
API_SECRET = "BSOTWqsVsncRk13DMDJ2YDRQks8XvrajArQDPW2jY8sDwNtcgb5da8H3x6qF3hJk"
PROXIES = {"http": "http://172.29.144.1:7897", "https": "http://172.29.144.1:7897"}

CAPITAL = 19.70
PER_POSITION = 3.94
MAX_POSITIONS = 3
STOP_LOSS = 0.02
TAKE_PROFIT = 0.03

positions = {}

def get_price(symbol):
    resp = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT", proxies=PROXIES, timeout=10)
    return float(resp.json()["price"])

def buy(symbol, usdt_amount):
    price = get_price(symbol)
    quantity = usdt_amount / price
    timestamp = int(time.time() * 1000)
    params = f"symbol={symbol}USDT&side=BUY&type=MARKET&quantity={quantity:.2f}&timestamp={timestamp}&recvWindow=5000"
    signature = hmac.new(API_SECRET.encode(), params.encode(), hashlib.sha256).hexdigest()
    resp = requests.post(f"https://api.binance.com/api/v3/order?{params}&signature={signature}", headers={"X-MBX-APIKEY": API_KEY}, proxies=PROXIES, timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        return {"success": True, "executed": float(data["executedQty"]), "cost": float(data["cummulativeQuoteQty"])}
    return {"success": False}

def scan():
    resp = requests.get("https://api.binance.com/api/v3/ticker/24hr", proxies=PROXIES, timeout=10)
    candidates = []
    for t in resp.json():
        if t["symbol"].endswith("USDT"):
            symbol = t["symbol"].replace("USDT", "")
            price = float(t["lastPrice"])
            change = float(t["priceChangePercent"])
            volume = float(t["quoteVolume"])
            if 2.0 <= abs(change) <= 10.0 and volume >= 10000000 and 0.0001 <= price <= 100:
                candidates.append({"symbol": symbol, "price": price, "change": change, "volume": volume})
    candidates.sort(key=lambda x: abs(x["change"]), reverse=True)
    return candidates[:5]

print("=" * 50)
print("🎯 打地鼠实盘启动")
print(f"资金: ${CAPITAL} | 每仓: ${PER_POSITION}")
print("-" * 50)

candidates = scan()
print(f"候选币种: {[c['symbol'] for c in candidates]}")

for c in candidates[:MAX_POSITIONS]:
    result = buy(c["symbol"], PER_POSITION)
    if result["success"]:
        positions[c["symbol"]] = result["executed"]
        print(f"✅ 买入 {c['symbol']}: {result['executed']:.2f} @ ${c['price']:.4f}")
    else:
        print(f"❌ 买入失败 {c['symbol']}")
    time.sleep(1)

print(f"\n持仓: {list(positions.keys())}")
print("=" * 50)
