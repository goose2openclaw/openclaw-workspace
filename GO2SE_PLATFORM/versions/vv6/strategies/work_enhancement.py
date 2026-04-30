"""
💼 打工能力增强配置
==================
增强抢单和落地交付能力
"""

WORK_ENHANCEMENT = {
    # 薅羊毛增强
    "wool": {
        "weight": 0.08,      # 3% → 8%
        "interval": 30,       # 更频繁扫描
        "min_profit": 0.5,   # 最小利润0.5%
        "max_gas": 10,        # 最大Gas费用
        "auto_claim": True,   # 自动领取
        "priority": ["new_listing", "airdrop", "testnet"]
    },
    
    # 众包打工增强
    "crowdsource": {
        "weight": 0.10,      # 2% → 10%
        "interval": 60,      # 每分钟扫描
        "task_types": ["translation", "data_entry", "testing", "review"],
        "min_reward": 5,     # 最小奖励5美元
        "auto_apply": True,   # 自动申请
        "delivery_speed": "fast"  # 快速交付
    },
    
    # 抢单能力
    "order_grabbing": {
        "enabled": True,
        "response_time_ms": 500,  # 500ms内响应
        "priority_queue": ["high_reward", "low_difficulty", "reputation"],
        "auto_bid": True,
        "max_bid_price": 2  # 最大竞价2美元
    },
    
    # 落地交付
    "delivery": {
        "quality": "high",
        "speed": "express",  # 快速交付
        "auto_review": True,
        "revision_rounds": 2,
        "on_time_rate": 0.95
    }
}
