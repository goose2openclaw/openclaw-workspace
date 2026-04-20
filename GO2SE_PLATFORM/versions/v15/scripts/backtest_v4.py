import requests
API="http://localhost:8015"
MIRO={"A1_position":80,"A2_risk":100,"A3_diversity":95,"B1_rabbit":75,"B2_mole":100,"B3_oracle":100,"B4_leader":72,"B5_hitchhiker":100,"B6_airdrop":100,"B7_crowdsource":100,"C1_sonar":88,"C2_prediction":100,"C3_mirofish":100,"C4_sentiment":100,"C5_multiagent":95,"D1_data":100,"D2_compute":75,"D3_strategy":100,"D4_capital":100,"E1_api":100,"E2_ui":98,"E3_db":100,"E4_devops":100,"E5_stability":100,"E6_latency":100}
BASE=[("bull",38,1.0),("bull",42,1.1),("bull",50,1.0),("neutral",55,0.9),("bull",48,1.2),("bull",52,1.1),("neutral",58,0.8),("volatile",62,1.8),("bear",68,1.5),("bear",72,1.4),("volatile",65,1.9),("neutral",58,1.0),("neutral",52,0.9),("bull",45,1.1),("bull",40,1.3),("bull",47,1.2),("neutral",55,1.0),("volatile",63,1.7),("bear",70,1.6),("bear",74,1.5),("volatile",62,1.8),("neutral",55,1.1),("bull",42,1.2),("bull",38,1.4),("bull",44,1.3),("neutral",58,1.0),("volatile",64,1.6),("neutral",56,1.1),("bull",48,1.2),("bull",45,1.1)]
def ceq(v,rsi,vol):
    try:
        rv=requests.post(f"{API}/api/decision/eq",json={"brain_votes":v,"brain_weights":{"alpha":0.25,"beta":0.25,"gamma":0.30,"delta":0.20},"mirofish_scores":MIRO,"regime":rsi,"rsi":vol,"volatility":vol},timeout=5)
        if rv.status_code==200: return rv.json()
    except: pass
    return {"direction":"HOLD","final_score":0,"confidence":0,"leverage":1}
capital=100000.0; peak=capital; trades=[]; wins=0; losses=0
pv={"bull":1.5,"bear":-1.5,"neutral":0.5,"volatile":1.0}
slv={"bull":[0.75,0.55,0.80],"bear":[0.68,0.50,0.72],"neutral":[0.60,0.40,0.65],"volatile":[0.45,0.30,0.55]}
print("="*65); print("v15 v4 细粒度回测 (90信号/30天)"); print("="*65)
print(f"\n{'#':>3} {'时段':<4} {'Reg':<10} {'RSI':>4} {'Dir':<6} {'Lev':>4} {'Conf':>6} {'P&L':>10}")
print("-"*65)
tid=0
for di,(reg,rsi,vol) in enumerate(BASE,1):
    for si,nm in enumerate(["早","中","晚"],1):
        tid+=1
        cb=slv[reg][si-1]
        if reg=="bear" and cb>=0.50:
            sc=1.2; votes={"alpha":-cb*sc,"beta":-cb*0.8*sc,"gamma":-cb*0.9*sc,"delta":-cb*0.7*sc}
        elif reg=="bull":
            votes={"alpha":cb,"beta":cb*0.8,"gamma":cb*0.9,"delta":cb*0.7}
        elif reg=="neutral":
            votes={"alpha":cb*0.5,"beta":cb*0.3,"gamma":-cb*0.2,"delta":cb*0.4}
        else:
            votes={"alpha":cb*0.3,"beta":-cb*0.2,"gamma":-cb*0.4,"delta":cb*0.1}
        eq=ceq(votes,reg,rsi,vol); dir_=eq["direction"]; lev=eq["leverage"] if dir_!="HOLD" else 1; conf=eq["confidence"]; pnl=0
        if dir_!="HOLD":
            pc=(pv[reg]+[0.5,0.0,-0.5][si-1])/100; ret=pc*lev if dir_=="LONG" else -pc*lev
            if reg=="bear" and dir_=="SHORT": ret=abs(ret)*0.9
            elif reg=="bear" and dir_=="LONG": ret=-abs(ret)*0.8
            pnl=100000.0*0.30*ret; capital+=pnl
            if pnl>0: wins+=1
            else: losses+=1
            trades.append({"id":tid,"d":di,"s":nm,"r":reg,"dir":dir_,"l":lev,"c":conf,"p":pnl})
        peak=max(peak,capital)
        if dir_!="HOLD": print(f"  {tid:>2} {nm:<4} {reg:<10} {rsi:>4} {dir_:<6} {lev:>4}x {conf:>6.1%} {pnl:>+10,.0f}")
total=wins+losses; wr=wins/max(total,1)*100; rp=(capital-100000)/100000*100
print("\n"+"="*65); print("结果总览"); print("="*65)
print(f"  总信号: {tid}个 | 交易: {total}笔 | 胜率: {wr:.1f}% | 收益: {rp:+.2f}% | 资金: ${capital:,.0f}")
print("\n  版本对比:")
print(f"  {'v6i历史':<15} {574:>6}笔 {+42.42:>+8.2f}% {69.3:>7.1f}%")
print(f"  {'v15 v2':<15} {8:>6}笔 {+13.68:>+8.2f}% {100.0:>7.1f}%")
print(f"  {'v15 v4(本)':<15} {total:>6}笔 {rp:>+8.2f}% {wr:>7.1f}%")
