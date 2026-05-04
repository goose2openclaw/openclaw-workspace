"""
🌐 Layer3任务源
================
连接Layer3.xyz获取Web3Quest任务
"""

import os
import requests
from typing import List, Dict, Optional

class Layer3Source:
    """Layer3 API集成"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("LAYER3_API_KEY")
        self.base_url = "https://layer3.xyz/api"
        self.headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
    
    def fetch_quests(self, limit: int = 20) -> List[Dict]:
        """获取Quest列表"""
        try:
            response = requests.get(
                f"{self.base_url}/quests",
                headers=self.headers,
                params={"limit": limit},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                quests = []
                
                for q in data if isinstance(data, list) else data.get("quests", []):
                    quests.append({
                        "id": q.get("id", ""),
                        "name": q.get("name", q.get("title", "Unknown")),
                        "title": q.get("name", q.get("title", "")),
                        "description": q.get("description", ""),
                        "reward": q.get("reward", q.get("reward_amount", 0)),
                        "reward_token": q.get("reward_token", "USDC"),
                        "chain": q.get("chain", q.get("network", "Ethereum")),
                        "difficulty": q.get("difficulty", "medium"),
                        "link": q.get("link", q.get("url", "")),
                        "category": "web3_quest",
                        "platform": "Layer3",
                        "expires_in": 86400 * 30,  # 默认30天
                    })
                
                return quests
                
        except Exception as e:
            print(f"❌ Layer3 API错误: {e}")
        
        return []
    
    def fetch_user_points(self, address: str) -> Dict:
        """获取用户积分"""
        try:
            response = requests.get(
                f"{self.base_url}/user/{address}/points",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"❌ Layer3用户数据错误: {e}")
        
        return {}
    
    def get_active_quests(self) -> List[Dict]:
        """获取活跃任务"""
        return self.fetch_quests(limit=50)
    
    def get_config_help(self) -> str:
        """返回配置帮助"""
        return """
🔧 Layer3 API配置:

1. 访问 https://layer3.xyz/
2. 申请API访问权限(或使用公共端点)
3. 设置环境变量:
   export LAYER3_API_KEY=your_api_key

注意: Layer3部分端点公开可用
        """
