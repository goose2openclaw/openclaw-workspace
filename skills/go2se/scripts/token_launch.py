#!/usr/bin/env python3
"""
GO2SE Token Launch Plan
平台代币发行计划
"""

import random
from datetime import datetime, timedelta

class GO2SEToken:
    """GO2SE 代币"""
    
    def __init__(self):
        self.name = "GO2SE"
        self.symbol = "GO2SE"
        self.decimals = 18
        self.total_supply = 100_000_000  # 1亿
        
        # 分配方案
        self.allocation = {
            "community": 40,        # 社区 40%
            "team": 20,            # 团队 20%
            "investors": 15,      # 早期投资者 15%
            "treasury": 15,       # 国库 15%
            "airdrop": 10,        # 空投 10%
        }
        
        # 价格参数
        self.initial_price = 0.01  # $0.01 初始价格
        self.tge_supply = 10      # TGE 释放 10%
        self.vesting_schedule = 24 # 24个月线性解锁
    
    def calculate_supply(self) -> dict:
        """计算供应量"""
        supply = {}
        for category, pct in self.allocation.items():
            supply[category] = {
                "percentage": pct,
                "tokens": self.total_supply * pct / 100,
                "tge": self.total_supply * pct / 100 * self.tge_supply / 100,
                "vested": self.total_supply * pct / 100 * (100 - self.tge_supple) / 100,
            }
        return supply
    
    def generate_tokenomics(self) -> dict:
        """生成代币经济学"""
        return {
            "name": self.name,
            "symbol": self.symbol,
            "decimals": self.decimals,
            "total_supply": self.total_supply,
            "initial_price": self.initial_price,
            "fdv": self.total_supply * self.initial_price,
            "allocation": self.allocation,
            "tge_unlock": f"{self.tge_supply}%",
            "vesting": f"{self.vesting_schedule} months linear"
        }
    
    def generate_roadmap(self) -> list:
        """生成路线图"""
        return [
            {
                "phase": "Phase 1",
                "timeline": "TGE",
                "description": "代币生成事件",
                "targets": [
                    "智能合约部署",
                    "初始流动性池",
                    "TGE 解锁 10%",
                    "CEX 上市准备"
                ]
            },
            {
                "phase": "Phase 2", 
                "timeline": "Month 1-3",
                "description": "早期增长",
                "targets": [
                    "CEX 上市 (Binance, Bybit)",
                    "DeFi 集成",
                    "治理模块上线",
                    "社区激励启动"
                ]
            },
            {
                "phase": "Phase 3",
                "timeline": "Month 4-12", 
                "description": "生态建设",
                "targets": [
                    "Staking 质押上线",
                    "Liquidity Program",
                    "DAO 治理启动",
                    "多链桥接"
                ]
            },
            {
                "phase": "Phase 4",
                "timeline": "Year 2+",
                "description": "大规模采用",
                "targets": [
                    "机构合作",
                    "支付集成",
                    "NFT 市场",
                    "元宇宙集成"
                ]
            }
        ]
    
    def generate_use_cases(self) -> list:
        """代币用例"""
        return [
            {
                "use_case": "Staking 质押",
                "percentage": 30,
                "description": "质押获得收益和治理权限"
            },
            {
                "use_case": "交易手续费折扣",
                "percentage": 25,
                "description": "持有GO2SE享受交易手续费折扣"
            },
            {
                "use_case": "治理投票",
                "percentage": 20,
                "description": "DAO治理，参与协议决策"
            },
            {
                "use_case": "生态激励",
                "percentage": 15,
                "description": "策略贡献者、流动性提供者激励"
            },
            {
                "use_case": "NFT铸造",
                "percentage": 10,
                "description": "限量版NFT铸造和交易"
            }
        ]
    
    def run(self):
        """运行"""
        print("\n" + "="*70)
        print("🪿 GO2SE 代币发行计划".center(70))
        print("="*70)
        
        # 代币信息
        tokenomics = self.generate_tokenomics()
        
        print(f"\n📊 代币经济学:")
        print(f"   名称: {tokenomics['name']}")
        print(f"   符号: {tokenomics['symbol']}")
        print(f"   总供应量: {tokenomics['total_supply']:,}")
        print(f"   初始价格: ${tokenomics['initial_price']}")
        print(f"   FDV: ${tokenomics['fdv']:,.0f}")
        
        # 分配
        print(f"\n📦 代币分配:")
        for category, pct in self.allocation.items():
            tokens = self.total_supply * pct / 100
            value = tokens * self.initial_price
            emoji = {
                "community": "👥",
                "team": "👨‍💻", 
                "investors": "💰",
                "treasury": "🏦",
                "airdrop": "🎁"
            }.get(category, "📦")
            
            print(f"   {emoji} {category:12} {pct:3}%  ({tokens:>12,.0f} GO2SE)")
        
        # 路线图
        roadmap = self.generate_roadmap()
        
        print(f"\n🗺️ 路线图:")
        for phase in roadmap:
            print(f"\n   📍 {phase['phase']} - {phase['timeline']}")
            print(f"      {phase['description']}")
            for target in phase['targets']:
                print(f"      ✅ {target}")
        
        # 用例
        use_cases = self.generate_use_cases()
        
        print(f"\n\n💎 代币用例:")
        for uc in use_cases:
            bar = "█" * int(uc['percentage']/5) + "░" * (20 - int(uc['percentage']/5))
            print(f"   [{bar}] {uc['percentage']}% {uc['use_case']}")
            print(f"      {uc['description']}")
        
        # 时间表
        print(f"\n⏰ 代币释放时间表:")
        print(f"   TGE (解锁): {self.tge_supply}%")
        print(f"   线性解锁: {self.vesting_schedule} 个月")
        
        # 估值预测
        print(f"\n💰 估值预测 (保守):")
        scenarios = [
            ("FOMO", 10, 1.0),
            ("Bull", 5, 0.5),
            ("Base", 2, 0.1),
            ("Bear", 0.5, 0.05)
        ]
        
        for name, price, mult in scenarios:
            fdv = self.total_supply * price * mult
            print(f"   {name:8} ${price*mult:.4f}/GO22SE | FDV: ${fdv:,.0f}")
        
        print("\n" + "="*70)


def main():
    import sys
    
    token = GO2SEToken()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "tokenomics":
            import json
            print(json.dumps(token.generate_tokenomics(), indent=2))
        elif sys.argv[1] == "roadmap":
            import json
            print(json.dumps(token.generate_roadmap(), indent=2))
        else:
            token.run()
    else:
        token.run()


if __name__ == "__main__":
    main()
