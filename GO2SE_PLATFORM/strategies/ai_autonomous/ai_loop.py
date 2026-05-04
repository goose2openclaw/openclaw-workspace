#!/usr/bin/env python3
"""GO2SE AI Autonomous System"""
import requests, hmac, hashlib, time, json
API_KEY = "QPM55JoNnHSV7C7PllgNbTAxpzy9RaBjoKprgHuIE9GJUeQoVIGu69ICPnmBXp61"
API_SECRET = "BSOTWqsVsncRk13DMDJ2YDRQks8XvrajArQDPW2jY8sDwNtcgb5da8H3x6qF3hJk"
PROXIES = {"http": "http://172.29.144.1:7897", "https": "http://172.29.144.1:7897"}
def get_account():
    ts = int(time.time() * 1000)
    p = f"timestamp={ts}&recvWindow=5000"
    sig = hmac.new(API_SECRET.encode(), p.encode(), hashlib.sha256).hexdigest()
    resp = requests.get(f"https://api.binance.com/api/v3/account?{p}&signature={sig}", headers={"X-MBX-APIKEY": API_KEY}, proxies=PROXIES, timeout=10)
    return {b["asset"]: float(b["free"]) for b in resp.json()["balances"]}
balances = get_account()
print("AI系统就绪")
print("DOGE:", balances.get("DOGE", 0))
print("USDT:", balances.get("USDT", 0))
