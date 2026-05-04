"""
💰 全网赚钱机会扫描器
=========================
不止于翻译、数据、测试、审核
寻找所有可能的变现机会
"""

OPPORTUNITIES = {
    # 现有机会
    "existing": {
        "translation": {"platforms": ["TranslatorsBase", "Gengo", "Rev", "Upwork", "Fiverr"], "rate": "$0.05-0.20/word"},
        "data_entry": {"platforms": ["Amazon MTurk", "Clickworker", "Appen", "Upwork"], "rate": "$5-15/hr"},
        "testing": {"platforms": ["UserTesting", "Testbirds", "Testlio", "uTest"], "rate": "$10-50/test"},
        "review": {"platforms": ["Trustpilot", "G2", "Capterra", "Sitejabber"], "rate": "$5-20/review"},
        "new_listing": {"platforms": ["Binance", "Coinbase", "Kraken", "OKX"], "rate": "$50-500/listing"},
        "airdrop": {"platforms": ["LayerZero", "StarkNet", "zkSync", "Arbitrum"], "rate": "$20-200/drop"},
        "testnet": {"platforms": ["Testnet Faucets", "Dev Guild", "Gitcoin"], "rate": "$100-1000/testnet"}
    },
    
    # 更多机会
    "expanding": {
        # 内容创作
        "content_creation": {
            "platforms": ["Medium", "Substack", "YouTube", "TikTok", "小红书"],
            "rate": "$100-10000/month",
            "skills": ["writing", "video", "design"]
        },
        
        # 联盟营销
        "affiliate_marketing": {
            "platforms": ["Amazon Associates", "ShareASale", "CJ Affiliate", "Awin"],
            "rate": "5-50% commission",
            "skills": ["marketing", "content"]
        },
        
        # 编程外包
        "coding_gigs": {
            "platforms": ["Upwork", "Freelancer", "Toptal", "Fiverr", "GitHub Jobs"],
            "rate": "$25-200/hr",
            "skills": ["python", "solidity", "web3", "ai"]
        },
        
        # AI提示词
        "prompt_engineering": {
            "platforms": ["PromptBase", "PromptHero", "Humanloop", "OpenAI"],
            "rate": "$10-500/prompt",
            "skills": ["ai", "prompts", "optimization"]
        },
        
        # 数据标注
        "data_annotation": {
            "platforms": ["Label Studio", "Scale AI", "Amazon Sagemaker", "Remotasks"],
            "rate": "$8-25/hr",
            "skills": ["labeling", "computer_vision", "nlp"]
        },
        
        # 虚拟助手
        "virtual_assistant": {
            "platforms": ["Zirtual", "Boldly", "Belay", "EA"],
            "rate": "$25-75/hr",
            "skills": ["admin", "research", "communication"]
        },
        
        # 社交媒体管理
        "social_media": {
            "platforms": ["Fiverr", "Upwork", "Agency", "Direct"],
            "rate": "$500-5000/month",
            "skills": ["social", "content", "analytics"]
        },
        
        # Web3机会
        "web3_hunter": {
            "platforms": ["Layer3", "RabbitHole", "QuestN", "Coindcx"],
            "rate": "$50-5000/quest",
            "skills": ["defi", "nft", "dao"]
        }
    },
    
    # 被动收入
    "passive": {
        "staking": {"platforms": ["Binance", "Coinbase", "Kraken"], "rate": "3-20% APY"},
        "liquidity": {"platforms": ["Uniswap", "PancakeSwap", "Raydium"], "rate": "10-100% APY"},
        "lending": {"platforms": ["Aave", "Compound", "Maker"], "rate": "3-15% APY"},
        "nft_rental": {"platforms": ["NFTFi", "OpenSea", "Blur"], "rate": "5-30% APY"}
    }
}

def scan_opportunities():
    """扫描所有赚钱机会"""
    return OPPORTUNITIES


# 落地交付能力
DELIVERY_CAPABILITY = {
    "templates": {
        "translation": {"delivery_time": "2-24h", "quality": "professional"},
        "data_entry": {"delivery_time": "1-12h", "quality": "99% accuracy"},
        "testing": {"delivery_time": "24-48h", "quality": "detailed report"},
        "coding": {"delivery_time": "1-7 days", "quality": "production-ready"}
    }
}
