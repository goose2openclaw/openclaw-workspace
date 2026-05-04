"""
⚡ 抢到手为强! 配置
=====================
落地交付为核心的赚钱策略
"""

GRAB_TO_WIN = {
    # 核心理念: 抢到手才是强
    "philosophy": "抢到手为强，落地交付为本",
    
    # 第一优先级 - 必抢
    "MUST_GRAB": {
        "airdrops": {
            "target": "$50-500/次",
            "speed": "24h内领取",
            "platforms": ["LayerZero", "zkSync", "StarkNet", "Arbitrum", "Linea"]
        },
        "testnets": {
            "target": "$100-1000/次", 
            "speed": "72h内完成",
            "platforms": ["Gitcoin", "QuestN", "Layer3", "Rabithole"]
        },
        "new_listings": {
            "target": "$100-1000/次",
            "speed": "上市前完成",
            "platforms": ["Binance", "OKX", "Bybit", "Coinbase"]
        }
    },
    
    # 第二优先级 - 高价值
    "HIGH_VALUE": {
        "affiliate": {
            "target": "5-50%佣金",
            "speed": "即时推广",
            "platforms": ["Amazon", "Binance", "OKX"]
        },
        "coding_gigs": {
            "target": "$50-500/单",
            "speed": "3-7天交付",
            "platforms": ["Upwork", "Fiverr", "Toptal"]
        }
    },
    
    # 第三优先级 - 稳定收入
    "STEADY": {
        "translation": {"target": "$0.05-0.2/字", "speed": "24h交付"},
        "data_entry": {"target": "$10-20/hr", "speed": "12h交付"},
        "testing": {"target": "$20-50/个", "speed": "48h交付"}
    },
    
    # 被动收入 - 躺赚
    "PASSIVE": {
        "staking": {"target": "5-20%年化", "platforms": ["Binance", "Kraken"]},
        "liquidity": {"target": "10-50%年化", "platforms": ["Uniswap", "Raydium"]}
    },
    
    # 执行原则
    "principles": [
        "1. 抢到手 > 想到手 > 观望",
        "2. 小钱也是钱，积少成多", 
        "3. 交付质量决定复购",
        "4. 速度就是竞争力"
    ]
}


# 落袋为安 - 第4原则
SECURE_PROFITS = {
    "principle": "落袋为安",
    "rules": [
        "1. 抢到的钱要及时变现",
        "2. 不要贪心，见好就收",
        "3. 及时提现，不要留太多在平台",
        "4. 定期将收益转入安全账户"
    ],
    "actions": {
        "withdrawal_threshold": 100,  # 满$100就提现
        "withdrawal_frequency": "weekly",  # 每周提现
        "emergency_fund": 0.2,  # 20%存入应急基金
        " reinvestment": 0.8  # 80%再投资
    }
}
