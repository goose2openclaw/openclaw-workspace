#!/usr/bin/env python3
"""
GO2SE Genius 自动信号监控 + 执行系统
自动监控跟大哥、搭便车策略信号，激活后自动执行

版本: 1.0
日期: 2026-05-03
"""

import requests
import hmac
import hashlib
import time
import json
from datetime import datetime

API_KEY = "QPM55JoNnHSV7C7PllgNbTAxpzy9RaBjoKprgHuIE9GJUeQoVIGu69ICPnmBXp61"
API_SECRET = "BSOTWqsVsncRk13DMDJ2YDRQks8XvrajArQDPW2jY8sDwNtcgb5da8H3x6qF3hJk"
PROXIES = {"http": "http://172.29.144.1:7897", "https": "http://172.29.144.1:7897"}

# 币种列表
FOCUS_COINS = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'DOT', 'LINK', 'AVAX', 'MATIC']

def get_account():
    """获取账户"""
    ts = int(time.time() * 1000)
    params = f"timestamp={ts}&recvWindow=5000"
    sig = hmac.new(API_SECRET.encode(), params.encode(), hashlib.sha256).hexdigest()
    resp = requests.get(f"https://api.binance.com/api/v3/account?{params}&signature={sig}", headers={"X-MBX-APIKEY": API_KEY}, proxies=PROXIES, timeout=10)
    return {b["asset"]: float(b["free"]) for b in resp.json()["balances"]}

def get_prices(symbols):
    """获取价格"""
    sym = json.dumps([f"{s}USDT" for s in symbols])
    resp = requests.get("https://api.binance.com/api/v3/ticker/24hr", params={"symbols": sym}, proxies=PROXIES, timeout=10)
    return {p["symbol"].replace("USDT", ""): float(p["lastPrice"]) for p in resp.json()}

def get_klines(symbol, interval='1h', limit=720):
    """获取K线"""
    resp = requests.get("https://api.binance.com/api/v3/klines",
                       params={"symbol": symbol, "interval": interval, "limit": limit},
                       proxies=PROXIES, timeout=10)
    return resp.json() if resp.status_code == 200 else []

def check_follow_big_player(coin):
    """检查跟大哥信号"""
    klines = get_klines(f"{coin}USDT", '1h', 168)
    if not klines or len(klines) < 60:
        return None
    
    closes = [float(k[4]) for k in klines]
    volumes = [float(k[5]) for k in klines]
    
    current_price = closes[-1]
    
    # 量比
    avg_vol = sum(volumes[-24:]) / 24
    vol_ratio = volumes[-1] / avg_vol if avg_vol > 0 else 0
    
    # MA
    ma5 = sum(closes[-5:]) / 5
    ma20 = sum(closes[-20:]) / 20
    ma60 = sum(closes[-60:]) / 60 if len(closes) >= 60 else sum(closes) / len(closes)
    
    # 4h变化
    change_4h = (closes[-1] - closes[-5]) / closes[-5] * 100 if len(closes) >= 5 else 0
    
    # 信号
    signal1 = vol_ratio > 1.5  # 量比
    signal2 = ma5 > ma20 > ma60  # 多头
    signal3 = change_4h > 2  # 动量
    
    # 评分
    score = 0
    if vol_ratio > 2: score += 0.4
    elif vol_ratio > 1.5: score += 0.3
    elif vol_ratio > 1.2: score += 0.1
    
    if ma5 > ma20 > ma60: score += 0.3
    elif ma5 > ma20: score += 0.15
    
    if change_4h > 5: score += 0.3
    elif change_4h > 2: score += 0.2
    elif change_4h > 0: score += 0.1
    
    return {
        'coin': coin,
        'price': current_price,
        'vol_ratio': vol_ratio,
        'change_4h': change_4h,
        'ma5': ma5,
        'ma20': ma20,
        'ma60': ma60,
        'signal1': signal1,
        'signal2': signal2,
        'signal3': signal3,
        'score': score,
        'activated': signal1 and signal2 and signal3
    }

def check_hitchhike(coin):
    """检查搭便车信号"""
    klines = get_klines(f"{coin}USDT", '1h', 720)
    if not klines or len(klines) < 100:
        return None
    
    closes = [float(k[4]) for k in klines]
    
    # 胜率
    wins = 0
    total = 0
    profits = []
    
    for i in range(24, len(closes)):
        if closes[i] > closes[i-4]:
            wins += 1
            profits.append((closes[i] - closes[i-4]) / closes[i-4])
        total += 1
    
    win_rate = wins / total * 100 if total > 0 else 50
    
    # 夏普
    if profits:
        avg_ret = sum(profits) / len(profits)
        std_ret = (sum((p - avg_ret) ** 2 for p in profits) / len(profits)) ** 0.5
        sharpe = avg_ret / std_ret if std_ret > 0 else 0
    else:
        sharpe = 0
    
    # MA趋势
    ma5 = sum(closes[-5:]) / 5
    ma20 = sum(closes[-20:]) / 20
    ma_trend = ma5 > ma20
    
    # 信号
    signal1 = win_rate > 55
    signal2 = sharpe > 0.5
    signal3 = ma_trend
    
    # 评分
    score = 0
    if win_rate > 65: score += 0.4
    elif win_rate > 55: score += 0.3
    elif win_rate > 50: score += 0.15
    
    if sharpe > 1.0: score += 0.35
    elif sharpe > 0.5: score += 0.25
    elif sharpe > 0.3: score += 0.1
    
    if ma_trend: score += 0.25
    
    return {
        'coin': coin,
        'win_rate': win_rate,
        'sharpe': sharpe,
        'ma_trend': ma_trend,
        'signal1': signal1,
        'signal2': signal2,
        'signal3': signal3,
        'score': score,
        'activated': signal1 and signal2 and signal3
    }

def trade(symbol, side, quantity):
    """执行交易"""
    ts = int(time.time() * 1000)
    params = f"symbol={symbol}USDT&side={side}&type=MARKET&quantity={quantity:.6f}&timestamp={ts}&recvWindow=5000"
    sig = hmac.new(API_SECRET.encode(), params.encode(), hashlib.sha256).hexdigest()
    
    resp = requests.post(f"https://api.binance.com/api/v3/order?{params}&signature={sig}",
                       headers={"X-MBX-APIKEY": API_KEY}, proxies=PROXIES, timeout=10)
    
    if resp.status_code == 200:
        d = resp.json()
        return {"success": True, "qty": float(d["executedQty"]), "value": float(d["cummulativeQuoteQty"])}
    return {"success": False, "error": resp.json().get("msg", "Unknown")}

def execute_follow_big(coin, data, usdt):
    """执行跟大哥"""
    if usdt < 5:
        return None
    
    # 计算仓位
    position = 10  # 基础
    if data['vol_ratio'] > 2: position += 10
    if data['change_4h'] > 5: position += 10
    
    alloc = usdt * position / 100
    qty = alloc / data['price']
    
    result = trade(coin, "BUY", qty)
    if result["success"]:
        return f"跟大哥买入 {coin}: {result['qty']:.6f} @ ${data['price']:.2f} = ${result['value']:.2f}"
    return f"跟大哥买入失败 {coin}: {result['error']}"

def execute_hitchhike(coin, data, usdt):
    """执行搭便车"""
    if usdt < 5:
        return None
    
    # 计算仓位
    position = 10  # 基础
    if data['win_rate'] > 65: position += 10
    if data['sharpe'] > 1.0: position += 10
    
    alloc = usdt * position / 100
    qty = alloc / data['price']
    
    result = trade(coin, "BUY", qty)
    if result["success"]:
        return f"搭便车买入 {coin}: {result['qty']:.6f} @ ${data['price']:.2f} = ${result['value']:.2f}"
    return f"搭便车买入失败 {coin}: {result['error']}"

def run_monitor():
    """运行监控"""
    print("=" * 60)
    print("🔔 GO2SE Genius 自动信号监控系统")
    print("=" * 60)
    print("策略: 跟大哥 + 搭便车")
    print("信号: 激活后自动执行")
    print("-" * 60)
    
    last_alert = {"follow": None, "hitch": None}
    
    while True:
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n[{now}] 信号扫描...")
            
            # 检查跟大哥
            follow_activated = []
            for coin in FOCUS_COINS[:5]:  # 重点5个
                data = check_follow_big_player(coin)
                if data and data['activated']:
                    follow_activated.append(data)
            
            # 检查搭便车
            hitch_activated = []
            for coin in FOCUS_COINS:
                data = check_hitchhike(coin)
                if data and data['activated']:
                    hitch_activated.append(data)
            
            # 获取账户
            balances = get_account()
            usdt = balances.get("USDT", 0)
            
            # 执行
            executed = []
            
            # 跟大哥执行
            if follow_activated:
                print(f"\n📣 跟大哥信号激活!")
                for data in follow_activated[:1]:  # 最多1个
                    msg = execute_follow_big(data['coin'], data, usdt)
                    if msg:
                        executed.append(msg)
                        print(f"  ⚡ {msg}")
            
            # 搭便车执行
            if hitch_activated:
                print(f"\n📣 搭便车信号激活!")
                for data in hitch_activated[:1]:  # 最多1个
                    msg = execute_hitchhike(data['coin'], data, usdt)
                    if msg:
                        executed.append(msg)
                        print(f"  ⚡ {msg}")
            
            # 状态更新
            if not executed:
                # 显示接近信号
                for coin in FOCUS_COINS[:3]:
                    fb = check_follow_big_player(coin)
                    hh = check_hitchhike(coin)
                    
                    if fb and fb['score'] > 0.3:
                        print(f"  ⏳ {coin}: 跟大哥 {fb['score']:.2f}")
                    if hh and hh['score'] > 0.3:
                        print(f"  ⏳ {coin}: 搭便车 {hh['score']:.2f}")
            
            print(f"\n监控中... (每5分钟扫描)")
            time.sleep(300)  # 5分钟
            
        except Exception as e:
            print(f"错误: {e}")
            time.sleep(60)

if __name__ == "__main__":
    run_monitor()
