"""
🏛️ Gitcoin任务源
==================
连接Gitcoin获取开源资助和Quest任务
"""

import os
import requests
from typing import List, Dict, Optional

class GitcoinSource:
    """Gitcoin API集成"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GITCOIN_API_KEY")
        self.base_url = "https://gitcoin.co/grants/v1/api"
        self.headers = {"Content-Type": "application/json"}
        if self.api_key:
            self.headers["Authorization"] = f"Token {self.api_key}"
    
    def fetch_grants(self, limit: int = 20) -> List[Dict]:
        """获取资助项目"""
        try:
            response = requests.get(
                f"{self.base_url}/grants/",
                headers=self.headers,
                params={"limit": limit, "active": True},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                grants = []
                
                for g in data.get("results", data if isinstance(data, list) else []):
                    grants.append({
                        "id": g.get("id", ""),
                        "name": g.get("title", g.get("name", "Unknown")),
                        "title": g.get("title", ""),
                        "description": g.get("description", ""),
                        "reward": g.get("amount_goal", 0),
                        "token": g.get("token_symbol", "USDC"),
                        "chain": g.get("network", "Ethereum"),
                        "link": g.get("url", g.get("reference_url", "")),
                        "category": "grant_funding",
                        "platform": "Gitcoin",
                        "expires_in": 86400 * 30,
                    })
                
                return grants
                
        except Exception as e:
            print(f"❌ Gitcoin API错误: {e}")
        
        return []
    
    def fetch_quests(self, limit: int = 20) -> List[Dict]:
        """获取Quest任务"""
        try:
            # Gitcoin Quests API (Beta)
            response = requests.get(
                "https://gitcoin.co/alpha/quests/api/v1/quests/",
                headers=self.headers,
                params={"limit": limit},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                quests = []
                
                for q in data.get("results", data if isinstance(data, list) else []):
                    quests.append({
                        "id": q.get("id", ""),
                        "name": q.get("title", "Unknown"),
                        "title": q.get("title", ""),
                        "description": q.get("description", ""),
                        "reward": q.get("reward_amount", 0),
                        "token": q.get("reward_token", "GTC"),
                        "difficulty": q.get("difficulty_level", "medium"),
                        "link": q.get("url", ""),
                        "category": "gitcoin_quest",
                        "platform": "Gitcoin",
                        "expires_in": 86400 * 7,
                    })
                
                return quests
                
        except Exception as e:
            print(f"❌ Gitcoin Quests API错误: {e}")
        
        return []
    
    def get_config_help(self) -> str:
        """返回配置帮助"""
        return """
🔧 Gitcoin API配置:

1. 访问 https://gitcoin.co/
2. 登录 → Settings → API
3. 生成Personal API Token
4. 设置环境变量:
   export GITCOIN_API_KEY=your_api_key

注意: Gitcoin Grants部分数据公开可用
        """
