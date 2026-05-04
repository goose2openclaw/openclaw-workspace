"""
💼 Upwork任务源
===============
连接Upwork API获取真实Freelance任务
"""

import os
import requests
from typing import List, Dict, Optional

class UpworkSource:
    """Upwork API集成"""
    
    def __init__(self, consumer_key: str = None, consumer_secret: str = None):
        self.consumer_key = consumer_key or os.getenv("UPWORK_CONSUMER_KEY")
        self.consumer_secret = consumer_secret or os.getenv("UPWORK_CONSUMER_SECRET")
        self.base_url = "https://api.upwork.com/api/v1"
        self.auth_url = "https://api.upwork.com/graphql"
        self.token = None
        
        # 任务类别配置
        self.categories = {
            "data_entry": {"skill": "Data Entry", "rate": 15},
            "translation": {"skill": "Translation", "rate": 50},
            "writing": {"skill": "Content Writing", "rate": 40},
            "web_dev": {"skill": "Web Development", "rate": 75},
            "python": {"skill": "Python", "rate": 85},
            "web3": {"skill": "Blockchain", "rate": 120},
        }
    
    def authenticate(self) -> bool:
        """OAuth认证"""
        if not self.consumer_key or not self.consumer_secret:
            print("⚠️ Upwork API凭证未配置")
            return False
        
        # TODO: 实现OAuth流程
        # 1. 获取request token
        # 2. 用户授权
        # 3. 获取access token
        self.token = os.getenv("UPWORK_ACCESS_TOKEN")
        return self.token is not None
    
    def fetch_jobs(self, category: str = "all", limit: int = 10) -> List[Dict]:
        """获取任务列表"""
        if not self.authenticate():
            return []
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # GraphQL查询
        query = """
        query GetJobs($category: String, $limit: Int) {
            jobSearch(category: $category, limit: $limit) {
                jobs {
                    id
                    title
                    description
                    budget
                    hourlyRate
                    skills
                    postedTime
                }
            }
        }
        """
        
        try:
            response = requests.post(
                self.auth_url,
                json={"query": query, "variables": {"category": category, "limit": limit}},
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("data", {}).get("jobSearch", {}).get("jobs", [])
        except Exception as e:
            print(f"❌ Upwork API错误: {e}")
        
        return []
    
    def search_by_skill(self, skill: str, limit: int = 10) -> List[Dict]:
        """按技能搜索任务"""
        return self.fetch_jobs(category=skill, limit=limit)
    
    def get_config_help(self) -> str:
        """返回配置帮助"""
        return """
🔧 Upwork API配置:

1. 访问 https://developers.upwork.com/
2. 注册开发者账号
3. 创建应用获取:
   - Consumer Key
   - Consumer Secret
4. 设置环境变量:
   export UPWORK_CONSUMER_KEY=your_key
   export UPWORK_CONSUMER_SECRET=your_secret
   export UPWORK_ACCESS_TOKEN=your_token
        """
