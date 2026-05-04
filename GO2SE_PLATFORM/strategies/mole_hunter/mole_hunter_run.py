#!/usr/bin/env python3
"""打地鼠策略 - 市场扫描"""
import requests
import time
import sys

API_KEY = "QPM55JoNnHSV7C7PllgNbTAxpzy9RaBjoKprgHuIE9GJUeQoVIGu69ICPnmBXp61"
API_SECRET = "BSOTWqsVsncRk13DMDJ2YDRQks8XvrajArQDPW2jY8sDwNtcgb5da8H3x6qF3hJk"
PROXIES = {"http": "http://172.29.144.1:7897", "https": "http://172.29.144.1:7897"}

def scan():
    resp = requests.get("https://api.binance.com/api/v3/ticker/24hr", proxies=PROXIES, timeout=10)
    candidates = []
    for t in resp.json():
        if t["symbol"].endswith("USDT"):
            symbol = t["symbol"].replace("USDT", "")
            price = float(t["lastPrice"])
            change = float(t["priceChangePercent"])
            change_cont = abs(change)
            volume = float(t["quoteVolume"])
            if 2.0 <= change_cont <= 10.0 and volume >= 10000000 and 0.0001 <= price <= 100:
                mole_score = (change_cont / 10) * 0.5 + (volume / 1e8) * 0.5
                candidates.append({"symbol": symbol, "price": price, "change": change, "volume": volume, "mole_score": mole_score})
    candidates.sort(key=lambda x: x["mole_score"], reverse=True)
    return candidates[:10]

if __name__ == "__main__":
    print("🎯 打地鼠策略启动...")
    print("监控间隔: 60秒 | 止损: -2% | 止盈: +3%")
    print("-" * 50)
    
    mode = sys.argv[1] if len(sys.argv) > 1 else "scan"
    
    if mode == "scan":
        # 单次扫描
        candidates = scan()
        print(f"\n扫描到 {len(candidates)} 个候选币种:")
        for i, c in enumerate(candidates):
            vol = c["volume"] / 1e6
            print(f"  {i+1}. {c['symbol']}: {c['change']:+.2f}% | ${vol:.0f}M | 分数:{c['mole_score']:.3f}")
    else:
        # 持续监控
        while True:
            candidates = scan()
            print(f"[{time.strftime('%H:%M:%S')}] 候选: {len(candidates)} 个", end="")
            if candidates:
                c = candidates[0]
                print(f" | Top: {c['symbol']} {c['change']:+.2f}%")
            else:
                print(" | 无候选币种")
            time.sleep(60)
