#!/usr/bin/env python3
"""
🎯 GO2SE Genius 北斗七鑫选品仿真系统 v2.0
=============================================
优化: 加权因子 | 便捷操作 | 成果展示
"""

import json
import random
import time
from datetime import datetime
from typing import Dict, List, Tuple

class CoinSelector:
    def __init__(self):
        self.version = "2.0"
        
        # 币种数据库 (评分因素: 波动率, 流动性, 机构持仓, 热度, 安全性)
        self.coins = {
            # 主流币
            "BTC":  {"vol": 0.03, "liq": 1.00, "inst": 1.0, "heat": 95, "safe": 1.0, "type": "主流"},
            "ETH":  {"vol": 0.05, "liq": 0.95, "inst": 0.9, "heat": 92, "safe": 0.95, "type": "主流"},
            "BNB":  {"vol": 0.06, "liq": 0.80, "inst": 0.8, "heat": 78, "safe": 0.85, "type": "主流"},
            # 高波动币
            "SOL":  {"vol": 0.12, "liq": 0.70, "inst": 0.5, "heat": 85, "safe": 0.65, "type": "高波动"},
            "DOGE": {"vol": 0.15, "liq": 0.65, "inst": 0.3, "heat": 80, "safe": 0.50, "type": "高波动"},
            "AVAX": {"vol": 0.11, "liq": 0.55, "inst": 0.4, "heat": 72, "safe": 0.60, "type": "高波动"},
            "FTM":  {"vol": 0.14, "liq": 0.35, "inst": 0.3, "heat": 60, "safe": 0.55, "type": "高波动"},
            # 中波动币
            "XRP":  {"vol": 0.08, "liq": 0.75, "inst": 0.6, "heat": 70, "safe": 0.75, "type": "中波动"},
            "ADA":  {"vol": 0.10, "liq": 0.60, "inst": 0.4, "heat": 68, "safe": 0.70, "type": "中波动"},
            "LINK": {"vol": 0.09, "liq": 0.60, "inst": 0.5, "heat": 72, "safe": 0.75, "type": "中波动"},
            "DOT":  {"vol": 0.08, "liq": 0.50, "inst": 0.5, "heat": 65, "safe": 0.70, "type": "中波动"},
            "MATIC":{"vol": 0.10, "liq": 0.55, "inst": 0.4, "heat": 68, "safe": 0.65, "type": "中波动"},
            "UNI":  {"vol": 0.09, "liq": 0.45, "inst": 0.5, "heat": 62, "safe": 0.70, "type": "中波动"},
            # DeFi币
            "AAVE": {"vol": 0.10, "liq": 0.35, "inst": 0.4, "heat": 55, "safe": 0.65, "type": "DeFi"},
            "MKR":  {"vol": 0.07, "liq": 0.30, "inst": 0.5, "heat": 58, "safe": 0.70, "type": "DeFi"},
            "CRV":  {"vol": 0.15, "liq": 0.30, "inst": 0.3, "heat": 50, "safe": 0.55, "type": "DeFi"},
            "LDO":  {"vol": 0.10, "liq": 0.35, "inst": 0.4, "heat": 58, "safe": 0.65, "type": "DeFi"},
            # 隐私币
            "ZEC":  {"vol": 0.12, "liq": 0.30, "inst": 0.3, "heat": 45, "safe": 0.60, "type": "隐私"},
            "XMR":  {"vol": 0.06, "liq": 0.35, "inst": 0.3, "heat": 50, "safe": 0.80, "type": "隐私"},
        }
        
        # 北斗七鑫 (优化加权因子)
        self.beidou = {
            "贪狼": {
                "strategy": "打兔子",
                "style": "激进",
                "desc": "高波动快进快出",
                # 加权因子: vol, liq, inst, heat, safe
                "weights": [0.35, 0.15, 0.10, 0.20, 0.20],
                "target_vol": 0.12,
                "target_liq": 0.50,
                "bonus_coin": ["SOL", "DOGE", "AVAX", "FTM"],
                "penalty_coin": ["XMR", "MKR"]
            },
            "巨门": {
                "strategy": "打地鼠",
                "style": "灵活",
                "desc": "区间震荡高抛低吸",
                "weights": [0.20, 0.25, 0.15, 0.15, 0.25],
                "target_vol": 0.08,
                "target_liq": 0.60,
                "bonus_coin": ["ETH", "XRP", "BNB", "LINK"],
                "penalty_coin": ["DOGE", "FTM"]
            },
            "禄存": {
                "strategy": "走着瞧",
                "style": "稳健",
                "desc": "趋势确认后持有",
                "weights": [0.10, 0.30, 0.25, 0.15, 0.20],
                "target_vol": 0.05,
                "target_liq": 0.85,
                "bonus_coin": ["BTC", "ETH", "BNB"],
                "penalty_coin": ["DOGE", "FTM", "CRV"]
            },
            "文曲": {
                "strategy": "跟大哥",
                "style": "跟庄",
                "desc": "跟随机构动向",
                "weights": [0.15, 0.25, 0.30, 0.10, 0.20],
                "target_vol": 0.08,
                "target_liq": 0.70,
                "bonus_coin": ["BTC", "ETH", "BNB", "AAVE", "MKR"],
                "penalty_coin": ["DOGE", "SHIB"]
            },
            "廉贞": {
                "strategy": "搭便车",
                "style": "保守",
                "desc": "稳定收益低风险",
                "weights": [0.05, 0.30, 0.15, 0.10, 0.40],
                "target_vol": 0.03,
                "target_liq": 0.90,
                "bonus_coin": ["BTC", "ETH"],
                "penalty_coin": ["SOL", "DOGE", "FTM", "CRV"]
            },
            "武曲": {
                "strategy": "打兔子+打地鼠",
                "style": "均衡",
                "desc": "混合策略攻防兼备",
                "weights": [0.25, 0.20, 0.15, 0.20, 0.20],
                "target_vol": 0.09,
                "target_liq": 0.55,
                "bonus_coin": ["ETH", "SOL", "XRP", "LINK"],
                "penalty_coin": ["DOGE"]
            },
            "破军": {
                "strategy": "走着瞧+跟大哥",
                "style": "突破",
                "desc": "趋势突破跟庄结合",
                "weights": [0.20, 0.20, 0.25, 0.20, 0.15],
                "target_vol": 0.10,
                "target_liq": 0.60,
                "bonus_coin": ["SOL", "ETH", "AVAX", "LINK"],
                "penalty_coin": ["XMR"]
            }
        }
        
    def calculate_coin_score(self, coin: str, star: str) -> Tuple[float, Dict]:
        """计算币种在某星宿下的评分"""
        if coin not in self.coins:
            return 0, {}
        
        c = self.coins[coin]
        s = self.beidou[star]
        w = s["weights"]
        
        # 各维度得分
        vol_score = 1.0 - abs(c["vol"] - s["target_vol"]) / s["target_vol"]
        vol_score = max(0, min(1, vol_score))
        
        liq_score = c["liq"] / s["target_liq"] if c["liq"] >= s["target_liq"] else c["liq"] / s["target_liq"]
        liq_score = max(0, min(1, liq_score))
        
        inst_score = c["inst"]
        heat_score = c["heat"] / 100
        safe_score = c["safe"]
        
        # 加权总分
        total = w[0]*vol_score + w[1]*liq_score + w[2]*inst_score + w[3]*heat_score + w[4]*safe_score
        
        # 加成/惩罚
        bonus = 1.0
        if coin in s["bonus_coin"]:
            bonus = 1.2
        elif coin in s["penalty_coin"]:
            bonus = 0.8
        
        final_score = total * bonus
        
        return final_score, {
            "vol_score": vol_score,
            "liq_score": liq_score,
            "inst_score": inst_score,
            "heat_score": heat_score,
            "safe_score": safe_score,
            "bonus": bonus,
            "total": total
        }
    
    def rank_coins_for_star(self, star: str) -> List[Dict]:
        """为星宿排名所有币种"""
        results = []
        
        for coin in self.coins:
            score, details = self.calculate_coin_score(coin, star)
            results.append({
                "coin": coin,
                "score": score,
                "type": self.coins[coin]["type"],
                "vol": self.coins[coin]["vol"],
                "liq": self.coins[coin]["liq"],
                "details": details
            })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def simulate_trading(self, star: str, coins: List[str], allocation: List[float], 
                         days: int = 30, initial: float = 10000) -> Dict:
        """模拟交易"""
        base_yields = {
            "打兔子": 0.15, "打地鼠": 0.12, "走着瞧": 0.08,
            "跟大哥": 0.20, "搭便车": 0.10,
            "打兔子+打地鼠": 0.14, "走着瞧+跟大哥": 0.15
        }
        
        strategy = self.beidou[star]["strategy"]
        base_yield = base_yields.get(strategy, 0.10)
        
        capital = initial
        daily_data = []
        wins, losses = 0, 0
        
        random.seed(42)
        
        for day in range(days):
            day_pnl = 0
            day_return = 0
            
            for i, coin in enumerate(coins):
                if i >= len(allocation):
                    break
                    
                alloc = allocation[i]
                coin_data = self.coins.get(coin, {})
                vol = coin_data.get("vol", 0.08)
                
                # 收益计算
                yield_exp = base_yield * (1 + (vol - 0.05) * 3)
                
                # 随机涨跌
                if random.random() < 0.65:  # 65%胜率
                    pnl = capital * alloc * yield_exp * random.uniform(0.7, 1.3)
                    capital += pnl
                    day_pnl += pnl
                    wins += 1
                else:
                    loss = capital * alloc * yield_exp * random.uniform(0.3, 0.6)
                    capital -= loss
                    day_pnl -= loss
                    losses += 1
                
                day_return += day_pnl
            
            daily_data.append({
                "day": day + 1,
                "capital": capital,
                "pnl": day_pnl,
                "total_return": (capital - initial) / initial
            })
        
        total_return = (capital - initial) / initial
        win_rate = wins / (wins + losses) if (wins + losses) > 0 else 0
        
        return {
            "star": star,
            "initial": initial,
            "final": capital,
            "total_return": total_return,
            "win_rate": win_rate,
            "wins": wins,
            "losses": losses,
            "daily_data": daily_data
        }
    
    def generate_report(self, stars: List[str] = None) -> str:
        """生成完整报告"""
        if stars is None:
            stars = list(self.beidou.keys())
        
        report = []
        report.append("=" * 80)
        report.append("🎯 GO2SE Genius 北斗七鑫选品仿真系统 v2.0")
        report.append("   加权因子优化 | 便捷模拟 | 成果展示")
        report.append("=" * 80)
        
        # 1. 币种评分矩阵
        report.append("\n📊 北斗七鑫 × 币种评分矩阵")
        report.append("-" * 80)
        
        # 表头
        coins_header = ["币种", "类型", "波动", "流动", "机构", "热度", "安全"]
        for star in stars:
            coins_header.append(star)
        
        report.append("| " + " | ".join(f"{h:<8}" for h in coins_header) + " |")
        report.append("|" + "|".join(["---" for _ in range(len(coins_header))]) + "|")
        
        # 币种行
        all_coins = sorted(self.coins.keys(), key=lambda x: self.coins[x]["heat"], reverse=True)
        for coin in all_coins:
            c = self.coins[coin]
            row = [
                f"{coin:<8}",
                f"{c['type']:<8}",
                f"{c['vol']:.0%}",
                f"{c['liq']:.0%}",
                f"{c['inst']:.0%}",
                f"{c['heat']}",
                f"{c['safe']:.0%}"
            ]
            for star in stars:
                score, _ = self.calculate_coin_score(coin, star)
                row.append(f"{score:.3f}")
            
            report.append("| " + " | ".join(row) + " |")
        
        # 2. 每星宿Top3推荐
        report.append("\n\n🌟 每星宿Top3推荐")
        report.append("-" * 80)
        
        for star in stars:
            rankings = self.rank_coins_for_star(star)[:3]
            s = self.beidou[star]
            report.append(f"\n✨ {star} ({s['style']}) - {s['strategy']}")
            report.append(f"   描述: {s['desc']}")
            report.append(f"   加权: vol={s['weights'][0]}, liq={s['weights'][1]}, inst={s['weights'][2]}, heat={s['weights'][3]}, safe={s['weights'][4]}")
            report.append(f"   推荐: " + " | ".join([f"{r['coin']}({r['score']:.3f})" for r in rankings]))
        
        # 3. 模拟交易结果
        report.append("\n\n📈 模拟交易结果 (30天, $10,000)")
        report.append("-" * 80)
        
        sim_results = []
        for star in stars:
            rankings = self.rank_coins_for_star(star)[:3]
            coins = [r["coin"] for r in rankings]
            alloc = [0.5, 0.3, 0.2]
            result = self.simulate_trading(star, coins, alloc)
            sim_results.append(result)
            
            report.append(f"\n💰 {star}:")
            report.append(f"   币种: {' | '.join(coins)}")
            report.append(f"   配置: 50% | 30% | 20%")
            report.append(f"   最终: ${result['final']:,.2f}")
            report.append(f"   收益: {result['total_return']:+.2%}")
            report.append(f"   胜率: {result['win_rate']:.0%} ({result['wins']}胜/{result['losses']}负)")
        
        # 4. 排名
        sim_results.sort(key=lambda x: x["total_return"], reverse=True)
        report.append("\n\n🏆 综合排名")
        report.append("-" * 80)
        
        medals = ["🥇", "🥈", "🥉", "4", "5", "6", "7"]
        for i, r in enumerate(sim_results):
            m = medals[i] if i < 3 else f"{i+1}."
            report.append(f"   {m} {r['star']}: {r['total_return']:+.2%} (${r['final']:,.2f})")
        
        # 5. 最优组合
        report.append("\n\n🎲 最优组合推荐")
        report.append("-" * 80)
        
        best = sim_results[0]
        best_rankings = self.rank_coins_for_star(best["star"])[:3]
        
        report.append(f"\n   推荐星宿: {best['star']}")
        report.append(f"   推荐币种: " + " | ".join([r['coin'] for r in best_rankings]))
        report.append(f"   预期收益: {best['total_return']:+.2%}")
        report.append(f"   风险等级: {self.beidou[best['star']]['style']}")
        
        report.append("\n" + "=" * 80)
        
        return "\n".join(report)

def main():
    selector = CoinSelector()
    report = selector.generate_report()
    print(report)
    
    # 保存报告
    with open("/tmp/beidou_selection_report.txt", "w") as f:
        f.write(report)
    
    print("\n✅ 报告已保存到 /tmp/beidou_selection_report.txt")

if __name__ == "__main__":
    main()
