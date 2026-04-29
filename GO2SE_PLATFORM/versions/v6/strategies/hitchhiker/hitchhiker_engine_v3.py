#!/usr/bin/env python3
"""
🌐 Hitchhiker V3 - 扩展交易员池
========================================
新增到15个顶级交易员，覆盖更多策略类型
"""

TRADERS_V3 = [
    # 高胜率型 (WR > 70%)
    {"id": "hh_whalehunter", "name": "WhaleHunter", "grade": "A", "win_rate": 0.72, "ratio": 3.2, "alloc": 0.12, "trades": 245, "followers": 1820, "strategies": ["trend", "breakout"], "chains": ["Ethereum", "Arbitrum"], "fee": 0.015},
    {"id": "hh_steadyprofit", "name": "SteadyProfit", "grade": "A", "win_rate": 0.71, "ratio": 2.9, "alloc": 0.10, "trades": 312, "followers": 1540, "strategies": ["grid", "dca"], "chains": ["Solana", "Ethereum"], "fee": 0.012},
    {"id": "hh_smartmoney", "name": "SmartMoney", "grade": "A", "win_rate": 0.70, "ratio": 3.5, "alloc": 0.08, "trades": 189, "followers": 2100, "strategies": ["whale", "momentum"], "chains": ["Ethereum", "BSC"], "fee": 0.018},
    {"id": "hh_cryptoelite", "name": "CryptoElite", "grade": "A", "win_rate": 0.73, "ratio": 2.8, "alloc": 0.10, "trades": 276, "followers": 1650, "strategies": ["swing", "trend"], "chains": ["Ethereum", "Polygon"], "fee": 0.014},
    {"id": "hh_alphatrader", "name": "AlphaTrader", "grade": "A", "win_rate": 0.71, "ratio": 3.1, "alloc": 0.10, "trades": 234, "followers": 1890, "strategies": ["mean_reversion", "momentum"], "chains": ["Ethereum", "Optimism"], "fee": 0.016},
    
    # 中等胜率型 (WR 60-70%)
    {"id": "hh_swingking", "name": "SwingKing", "grade": "B", "win_rate": 0.68, "ratio": 3.4, "alloc": 0.08, "trades": 421, "followers": 980, "strategies": ["swing", "support_resistance"], "chains": ["Solana", "Ethereum", "Arbitrum"], "fee": 0.010},
    {"id": "hh_momentumboss", "name": "MomentumBoss", "grade": "B", "win_rate": 0.67, "ratio": 3.0, "alloc": 0.08, "trades": 356, "followers": 1120, "strategies": ["momentum", "breakout"], "chains": ["Ethereum", "BSC"], "fee": 0.012},
    {"id": "hh_trendmaster", "name": "TrendMaster", "grade": "B", "win_rate": 0.65, "ratio": 3.3, "alloc": 0.07, "trades": 289, "followers": 890, "strategies": ["trend_following", "ma_cross"], "chains": ["Ethereum", "Avalanche"], "fee": 0.011},
    {"id": "hh_cryptoquant", "name": "CryptoQuant", "grade": "B", "win_rate": 0.66, "ratio": 2.7, "alloc": 0.08, "trades": 398, "followers": 760, "strategies": ["quant", "stat_arb"], "chains": ["Ethereum", "Solana"], "fee": 0.015},
    {"id": "hh_defibull", "name": "DeFiBull", "grade": "B", "win_rate": 0.64, "ratio": 3.2, "alloc": 0.06, "trades": 267, "followers": 650, "strategies": ["defi", "yield_hunt"], "chains": ["Ethereum", "Arbitrum", "Polygon"], "fee": 0.013},
    
    # 新兴交易员 (高潜力)
    {"id": "hh_gempicks", "name": "GemPicks", "grade": "B+", "win_rate": 0.62, "ratio": 4.2, "alloc": 0.05, "trades": 145, "followers": 420, "strategies": ["micro_cap", "gem_hunt"], "chains": ["Solana", "Ethereum"], "fee": 0.018},
    {"id": "hh_airdropsnipe", "name": "AirdropSnipe", "grade": "B", "win_rate": 0.60, "ratio": 5.0, "alloc": 0.04, "trades": 89, "followers": 380, "strategies": ["airdrop", "testnet"], "chains": ["Multi"], "fee": 0.020},
    {"id": "hh_nftflipping", "name": "NFTFlipping", "grade": "C", "win_rate": 0.58, "ratio": 4.5, "alloc": 0.04, "trades": 523, "followers": 290, "strategies": ["nft", "flipping"], "chains": ["Solana", "Ethereum"], "fee": 0.025},
    
    # 保守型 (低风险)
    {"id": "hh_safefarmer", "name": "SafeFarmer", "grade": "A-", "win_rate": 0.75, "ratio": 2.2, "alloc": 0.12, "trades": 567, "followers": 2340, "strategies": ["yield_farm", "lending"], "chains": ["Ethereum", "Polygon", "Arbitrum"], "fee": 0.008},
    {"id": "hh_stableyield", "name": "StableYield", "grade": "A", "win_rate": 0.78, "ratio": 1.8, "alloc": 0.15, "trades": 890, "followers": 3100, "strategies": ["stablecoin", "arbitrage"], "chains": ["Ethereum", "Arbitrum", "Optimism"], "fee": 0.005},
]

def get_hitchhiker_v3():
    traders = sorted(TRADERS_V3, key=lambda x: x["win_rate"] * x["ratio"], reverse=True)
    top = traders[:5]
    portfolio = sum(t["alloc"] for t in traders)
    
    return {
        "count": len(TRADERS_V3),
        "traders": traders,
        "top_5": top,
        "portfolio_alloc": round(portfolio, 2),
        "avg_win_rate": sum(t["win_rate"] for t in traders) / len(traders),
        "avg_ratio": sum(t["ratio"] for t in traders) / len(traders),
    }
