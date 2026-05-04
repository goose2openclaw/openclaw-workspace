#!/usr/bin/env python3
"""
GG v2 - 北斗七鑫全域扫描Cron
版本: v2.0 | 日期: 2026-05-04
周期: 每30分钟 | 可降至10分钟/5分钟
"""

import requests, hmac, hashlib, time, json, random
from datetime import datetime

API_KEY = "QPM55JoNnHSV7C7PllgNbTAxpzy9RaBjoKprgHuIE9GJUeQoVIGu69ICPnmBXp61"
API_SECRET = "BSOTWqsVsncRk13DMDJ2YDRQks8XvrajArQDPW2jY8sDwNtcgb5da8H3x6qF3hJk"
PROXIES = {"http": "http://172.29.144.1:7897", "https": "http://172.29.144.1:7897"}

ALL_COINS = ['BTC','ETH','BNB','SOL','XRP','ADA','DOT','LINK','AVAX','MATIC','DOGE','ORDI','ORCA','NEAR','AAVE','UNI','ATOM','FIL','APT','SUI']
FOCUS_SECTORS = {'Layer2':['ARB','OP','MATIC'],'DeFi':['UNI','AAVE','COMP'],'GameFi':['IMX','GALA','MANA'],'AI':['AGIX','FET'],'RWA':['PRO']}

def log(m):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {m}", flush=True)

def get_prices(symbols):
    sym = json.dumps([f"{s}USDT" for s in symbols])
    resp = requests.get("https://api.binance.com/api/v3/ticker/24hr", params={"symbols": sym}, proxies=PROXIES, timeout=10)
    return {p["symbol"].replace("USDT",""): float(p["lastPrice"]) for p in resp.json()}

def get_klines(symbol, interval='1h', limit=168):
    resp = requests.get("https://api.binance.com/api/v3/klines", params={"symbol": symbol, "interval": interval, "limit": limit}, proxies=PROXIES, timeout=10)
    return resp.json() if resp.status_code == 200 else []

def sonar_trend(coin):
    klines = get_klines(f"{coin}USDT")
    if not klines: return None
    closes = [float(k[4]) for k in klines]
    volumes = [float(k[5]) for k in klines]
    ma5 = sum(closes[-5:])/5
    ma20 = sum(closes[-20:])/20
    ma60 = sum(closes[-60:])/60 if len(closes)>=60 else sum(closes)/len(closes)
    change = (closes[-1]-closes[-24])/closes[-24]*100 if len(closes)>=24 else 0
    returns = [(closes[i]-closes[i-1])/closes[i-1] for i in range(1,len(closes))]
    volatility = sum(abs(r) for r in returns)/len(returns)*100 if returns else 0
    avg_vol = sum(volumes[-24:])/24
    vol_ratio = volumes[-1]/avg_vol if avg_vol>0 else 1
    gains = [max(0,returns[i]) for i in range(len(returns))]
    losses = [max(0,-returns[i]) for i in range(len(returns))]
    avg_gain = sum(gains[-14:])/14 if len(gains)>=14 else sum(gains)/max(1,len(gains))
    avg_loss = sum(losses[-14:])/14 if len(losses)>=14 else sum(losses)/max(1,len(losses))
    rs = avg_gain/avg_loss if avg_loss>0 else 100
    rsi = 100-(100/(1+rs))
    trend = 1 if ma5>ma20>ma60 else 0.5 if ma5>ma20 else 0
    momentum = 1 if change>5 else 0.7 if change>2 else 0.5 if change>0 else 0.2
    volume = 1 if vol_ratio>1.5 else 0.7 if vol_ratio>1.2 else 0.5
    vol_score = 1 if 2<=volatility<=10 else 0.6 if volatility<15 else 0.3
    return {'trend':trend,'momentum':momentum,'volume':volume,'volatility':vol_score,'rsi':rsi,'change':change,'vol_ratio':vol_ratio}

def calc_rabbit(s): return 0.35*s['trend']+0.30*s['momentum']+0.25*s['volume']-0.10*(1-s['volatility']) if s else 0
def calc_mole(s): return 0.40*s['volatility']+0.35*s['volume']-0.25*0.5 if s else 0
def calc_predict(s): return 0.30*s.get('rsi',50)/100+0.25*s.get('rsi',50)/100+0.25*s['momentum']-0.20*(1-s['volatility']) if s else 0
def calc_follow(s): return 0.40*s['volume']+0.30*s['trend']+0.30*s['momentum'] if s else 0
def calc_hitch(s): return 0.40*0.65+0.30*1.2+0.20*s['trend']-0.10*(1-s['volatility']) if s else 0

def mirofish(score, n=1000):
    random.seed(int(time.time()))
    v={'buy':0,'hold':0,'sell':0}
    for _ in range(n):
        f=score+random.gauss(0,0.2)
        if f>0.6: v['buy']+=1
        elif f>0.3: v['hold']+=1
        else: v['sell']+=1
    t=sum(v.values())
    return {k:v/t*100 for k,v in v.items()}

def run_scan():
    log("="*60)
    log(" 北斗七鑫 全域扫描")
    log("="*60)
    start=time.time()
    prices=get_prices(ALL_COINS)
    results=[]
    for coin in ALL_COINS:
        if coin not in prices: continue
        s=sonar_trend(coin)
        if not s: continue
        r=calc_rabbit(s); m=calc_mole(s); p=calc_predict(s); f=calc_follow(s); h=calc_hitch(s)
        best=max(r,m,p,f,h)
        miro=mirofish(best)
        results.append({'coin':coin,'price':prices[coin],'rabbit':r,'mole':m,'predict':p,'follow':f,'hitch':h,'best':best,'miro':miro,'sonar':s})
    results.sort(key=lambda x:x['best'],reverse=True)
    log("\n声纳库趋势:")
    for r in results[:5]:
        s=r['sonar']
        log(f"  {r['coin']}: RSI={s['rsi']:.0f} 变化={s['change']:+.1f}% 量比={s['vol_ratio']:.2f}x")
    log("\n决策等式:")
    for r in results[:5]:
        log(f"  {r['coin']}: D={r['best']:.2f} (兔{r['rabbit']:.2f} 鼠{r['mole']:.2f} 预{r['predict']:.2f} 哥{r['follow']:.2f} 车{r['hitch']:.2f})")
        log(f"         Miro: 买{r['miro']['buy']:.0f}% 持{r['miro']['hold']:.0f}% 卖{r['miro']['sell']:.0f}%")
    top=results[0]
    log(f"\n最佳: {top['coin']} D={top['best']:.3f}")
    if top['best']>0.75: log(f"  强烈买入")
    elif top['best']>0.6: log(f"  买入")
    elif top['best']>0.4: log(f"  观望")
    else: log(f"  回避")
    log(f"\n扫描完成: {time.time()-start:.1f}秒")
    log("="*60)
    return results

if __name__=="__main__":
    run_scan()
