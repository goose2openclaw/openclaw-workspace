#!/usr/bin/env python3
"""
GO2SE Community System
社区与治理系统
"""

import random
from datetime import datetime

class CommunitySystem:
    """社区系统"""
    
    def __init__(self):
        self.governance_token = "GO2SE"
        
        # 社区统计
        self.stats = {
            "total_members": 12580,
            "active_members": 3420,
            "discord_members": 8500,
            "telegram_members": 3200,
            "twitter_followers": 45000
        }
        
        # 治理提案
        self.proposals = [
            {
                "id": "GIP-001",
                "title": "增加流动性挖矿奖励",
                "description": "将流动性挖矿奖励从5%提高到8%",
                "status": "active",
                "votes_for": 125000,
                "votes_against": 35000,
                "ends_at": "2026-03-20"
            },
            {
                "id": "GIP-002", 
                "title": "新策略上线: 网格交易",
                "description": "新增网格交易策略到策略池",
                "status": "pending",
                "votes_for": 0,
                "votes_against": 0,
                "ends_at": "2026-03-25"
            }
        ]
        
        # 社区活动
        self.events = [
            {"name": "Trading Competition", "participants": 450, "prize": "$2,500"},
            {"name": "Strategy Contest", "participants": 120, "prize": "$1,000"},
            {"name": "Community AMA", "participants": 890, "prize": "$500"},
        ]
    
    def generate_proposal(self) -> dict:
        """生成提案模板"""
        templates = [
            ("增加质押奖励", "将质押年化提高X%"),
            ("新策略上线", "新增某种交易策略"),
            ("社区激励", "开展社区活动"),
            ("参数调整", "调整某策略参数"),
            ("合作伙伴", "与某项目合作"),
        ]
        
        title, desc = random.choice(templates)
        
        return {
            "id": f"GIP-{random.randint(100, 999)}",
            "title": title,
            "description": desc,
            "status": "draft",
            "votes_for": 0,
            "votes_against": 0,
            "created_at": datetime.now().isoformat(),
            "quorum_required": 100000,
            "duration_days": 7
        }
    
    def run_dashboard(self):
        """运行仪表板"""
        print("\n" + "="*70)
        print("👥 GO2SE 社区与治理系统".center(70))
        print("="*70)
        
        # 社区统计
        print(f"\n📊 社区总览:")
        print(f"   👥 总成员: {self.stats['total_members']:,}")
        print(f"   ✅ 活跃成员: {self.stats['active_members']:,}")
        print(f"   💬 Discord: {self.stats['discord_members']:,}")
        print(f"   📱 Telegram: {self.stats['telegram_members']:,}")
        print(f"   🐦 Twitter: {self.stats['twitter_followers']:,}")
        
        # 治理
        print(f"\n🗳️ 治理提案:")
        for prop in self.proposals:
            status_icon = "🟢" if prop["status"] == "active" else ("🟡" if prop["status"] == "pending" else "🔴")
            total = prop["votes_for"] + prop["votes_against"]
            for_pct = prop["votes_for"] / total * 100 if total > 0 else 0
            
            print(f"\n   {status_icon} {prop['id']}: {prop['title']}")
            print(f"      状态: {prop['status']}")
            print(f"      结束: {prop['ends_at']}")
            print(f"      投票: {for_pct:.1f}% 赞成 ({prop['votes_for']:,} / {total:,})")
        
        # 活动
        print(f"\n\n🎉 社区活动:")
        for event in self.events:
            print(f"   • {event['name']}")
            print(f"     参与: {event['participants']}人 | 奖金: {event['prize']}")
        
        # 奖励
        print(f"\n\n🎁 社区奖励:")
        rewards = [
            ("每日签到", "1 GO2SE"),
            ("交易分享", "5 GO2SE"),
            ("策略贡献", "50-500 GO2SE"),
            ("社区贡献", "100-1000 GO2SE"),
            ("Bug报告", "10-1000 GO2SE"),
        ]
        for reward, amount in rewards:
            print(f"   • {reward}: {amount}")
        
        print("\n" + "="*70)


def main():
    import sys
    CommunitySystem().run_dashboard()

if __name__ == "__main__":
    main()
