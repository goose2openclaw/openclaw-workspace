#!/usr/bin/env python3
"""
走着瞧策略 v2.0 - 增强版
Market Prediction with Mirofish 1000-Agent Simulation

决策等式:
D = α(Predict) + β(WinRate) + γ(Return) - δ(Risk)

版本: 2.0
更新: 2026-05-03
"""

import requests
import hmac
import hashlib
import time
import random
import json
from datetime import datetime

API_KEY = "QPM55JoNnHSV7C7PllgNbTAxpzy9RaBjoKprgHuIE9GJUeQoVIGu69ICPnmBXp61"
API_SECRET = "BSOTWqsVsncRk13DMDJ2YDRQks8XvrajArQDPW2jY8sDwNtcgb5da8H3x6qF3hJk"
PROXIES = {"http": "http://172.29.144.1:7897", "https": "http://172.29.144.1:7897"}

# 重点币种
FOCUS_COINS = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'LINK', 'DOGE', 
                'AVAX', 'DOT', 'MATIC', 'UNI', 'ATOM', 'FIL', 'APT', 'ARB', 'OP', 'INJ', 'SUI', 'SEI']

def get_klines(symbol, interval='1h', limit=48):
    """获取K线数据"""
    resp = requests.get(
        'https://api.binance.com/api/v3/klines',
        params={'symbol': symbol, 'interval': interval, 'limit': limit},
        proxies=PROXIES, timeout=10
    )
    return resp.json() if resp.status_code == 200 else []

def calculate_predict_score(coin):
    """计算预测分数"""
    klines = get_klines(f'{coin}USDT')
    if not klines:
        return None
    
    closes = [float(k[4]) for k in klines]
    current_price = closes[-1]
    
    # 变化率
    change_1h = (closes[-1] - closes[-2]) / closes[-2] * 100 if len(closes) >= 2 else 0
    change_24h = (closes[-1] - closes[-24]) / closes[-24] * 100 if len(closes) >= 24 else 0
    
    # 波动率
    returns = [(closes[i] - closes[i-1]) / closes[i-1] * 100 for i in range(1, len(closes))]
    volatility = sum(abs(r) for r in returns) / len(returns) if returns else 0
    
    # 移动平均
    ma12 = sum(closes[-12:]) / 12 if len(closes) >= 12 else sum(closes) / len(closes)
    ma24 = sum(closes[-24:]) / 24 if len(closes) >= 24 else sum(closes) / len(closes)
    ma48 = sum(closes) / 48 if len(closes) >= 48 else sum(closes) / len(closes)
    
    # 趋势
    if current_price > ma12 > ma24 > ma48:
        trend, trend_score = '强势上涨', 2
    elif current_price > ma12 > ma24:
        trend, trend_score = '上涨', 1.5
    elif current_price > ma12:
        trend, trend_score = '反弹', 1
    elif current_price < ma12 < ma24 < ma48:
        trend, trend_score = '强势下跌', -2
    elif current_price < ma12 < ma24:
        trend, trend_score = '下跌', -1.5
    elif current_price < ma12:
        trend, trend_score = '回调', -1
    else:
        trend, trend_score = '震荡', 0
    
    # 预测分数
    alpha, beta, gamma, delta = 0.35, 0.25, 0.25, 0.15
    predict_score = (
        alpha * trend_score +
        beta * (change_24h / 10) +
        gamma * (1 / (volatility + 1)) +
        delta * ((current_price - ma24) / ma24 * 10)
    )
    
    return {
        'price': current_price,
        'change_1h': change_1h,
        'change_24h': change_24h,
        'volatility': volatility,
        'ma12': ma12,
        'ma24': ma24,
        'trend': trend,
        'trend_score': trend_score,
        'predict_score': predict_score
    }

def mirofish_simulate(data, iterations=1000):
    """Mirofish 1000智能体仿真"""
    decisions = {'强烈买入': 0, '买入': 0, '观望': 0, '卖出': 0, '强烈卖出': 0}
    
    for _ in range(iterations):
        score = data['predict_score']
        noise = random.gauss(0, 0.3)
        final_score = score + noise
        
        if final_score > 1.5:
            decisions['强烈买入'] += 1
        elif final_score > 0.5:
            decisions['买入'] += 1
        elif final_score > -0.5:
            decisions['观望'] += 1
        elif final_score > -1.5:
            decisions['卖出'] += 1
        else:
            decisions['强烈卖出'] += 1
    
    total = sum(decisions.values())
    buy_votes = decisions['强烈买入'] + decisions['买入']
    win_rate = buy_votes / total * 100
    
    if data['trend_score'] > 0:
        expected_return = data['volatility'] * 0.5 * (data['predict_score'] + 1)
    else:
        expected_return = -data['volatility'] * 0.3 * (data['predict_score'] - 1)
    
    return decisions, win_rate, expected_return

def calculate_decision(coin, data, win_rate, expected_return):
    """计算综合决策分数"""
    alpha, beta, gamma, delta = 0.30, 0.25, 0.25, 0.20
    
    predict_norm = max(0, data['predict_score']) / 2
    win_rate_norm = win_rate / 100
    return_norm = (expected_return + 5) / 10
    risk_norm = data.get('volatility', 0) / 5
    
    D = alpha * predict_norm + beta * win_rate_norm + gamma * return_norm - delta * risk_norm
    
    if D > 0.7:
        return '强烈买入', D, 30, -5, 10
    elif D > 0.5:
        return '买入', D, 20, -3, 8
    elif D > 0.3:
        return '观望', D, 10, -2, 5
    else:
        return '避免', D, 0, 0, 0

def get_account():
    """获取账户"""
    ts = int(time.time() * 1000)
    params = f'timestamp={ts}&recvWindow=5000'
    sig = hmac.new(API_SECRET.encode(), params.encode(), hashlib.sha256).hexdigest()
    resp = requests.get(f'https://api.binance.com/api/v3/account?{params}&signature={sig}', headers={'X-MBX-APIKEY': API_KEY}, proxies=PROXIES, timeout=10)
    return {b['asset']: float(b['free']) for b in resp.json()['balances']}

def trade(symbol, side, quantity):
    """执行交易"""
    ts = int(time.time() * 1000)
    params = f'symbol={symbol}USDT&side={side}&type=MARKET&quantity={quantity:.6f}&timestamp={ts}&recvWindow=5000'
    sig = hmac.new(API_SECRET.encode(), params.encode(), hashlib.sha256).hexdigest()
    resp = requests.post(f'https://api.binance.com/api/v3/order?{params}&signature={sig}', headers={'X-MBX-APIKEY': API_KEY}, proxies=PROXIES, timeout=10)
    if resp.status_code == 200:
        d = resp.json()
        return True, float(d['executedQty']), float(d['cummulativeQuoteQty'])
    return False, 0, 0

def run_cycle():
    """运行一个决策周期"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 走着瞧扫描...")
    
    results = []
    
    # 1. 计算预测分数
    for coin in FOCUS_COINS:
        data = calculate_predict_score(coin)
        if data:
            decisions, win_rate, expected_return = mirofish_simulate(data)
            action, D, position, stop_loss, take_profit = calculate_decision(coin, data, win_rate, expected_return)
            results.append({
                'coin': coin,
                'data': data,
                'decisions': decisions,
                'win_rate': win_rate,
                'expected_return': expected_return,
                'action': action,
                'D': D,
                'position': position,
                'stop_loss': stop_loss,
                'take_profit': take_profit
            })
    
    # 排序
    results.sort(key=lambda x: x['D'], reverse=True)
    
    # 打印结果
    print(f"\n  {'币种':<8} {'D值':<8} {'决策':<12} {'胜率':<8} {'预期收益'}")
    print(f"  {'-'*60}")
    for r in results[:8]:
        print(f"  {r['coin']:<8} {r['D']:>6.3f}   {r['action']:<12} {r['win_rate']:>5.1f}%   {r['expected_return']:>+.2f}%")
    
    return results

if __name__ == "__main__":
    print("=" * 60)
    print("🔮 走着瞧策略 v2.0 启动")
    print("=" * 60)
    run_cycle()
