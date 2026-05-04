"""
🔗 任务源聚合器
================
统一管理所有真实任务源
"""

import os
from typing import List, Dict, Optional
from .upwork_source import UpworkSource
from .layer3_source import Layer3Source
from .gitcoin_source import GitcoinSource

class TaskAggregator:
    """任务源聚合器"""
    
    def __init__(self):
        self.sources = {
            "upwork": UpworkSource(),
            "layer3": Layer3Source(),
            "gitcoin": GitcoinSource(),
        }
        
        # 任务池
        self.task_pool = []
        self.last_fetch = None
        
        # 配置状态
        self.config_status = {
            "upwork": bool(os.getenv("UPWORK_CONSUMER_KEY")),
            "layer3": bool(os.getenv("LAYER3_API_KEY")),
            "gitcoin": bool(os.getenv("GITCOIN_API_KEY")),
        }
    
    def fetch_all(self) -> List[Dict]:
        """从所有已配置源获取任务"""
        all_tasks = []
        
        for name, source in self.sources.items():
            if self.config_status.get(name):
                try:
                    if name == "upwork":
                        tasks = source.fetch_jobs(limit=20)
                    elif name == "layer3":
                        tasks = source.fetch_quests(limit=20)
                    elif name == "gitcoin":
                        tasks = source.fetch_quests(limit=20)
                    
                    for task in tasks:
                        task["source"] = name
                        all_tasks.append(task)
                        
                except Exception as e:
                    print(f"⚠️ {name}获取失败: {e}")
        
        self.task_pool = all_tasks
        self.last_fetch = __import__("datetime").datetime.now()
        
        return all_tasks
    
    def fetch_by_category(self, category: str) -> List[Dict]:
        """按类别获取任务"""
        all_tasks = self.fetch_all()
        return [t for t in all_tasks if t.get("category") == category]
    
    def get_status(self) -> Dict:
        """获取配置状态"""
        return {
            "sources_configured": sum(self.config_status.values()),
            "total_sources": len(self.sources),
            "tasks_in_pool": len(self.task_pool),
            "last_fetch": self.last_fetch.isoformat() if self.last_fetch else None,
            "configured": [k for k, v in self.config_status.items() if v],
            "unconfigured": [k for k, v in self.config_status.items() if not v],
        }
    
    def get_setup_help(self) -> str:
        """获取配置帮助"""
        helps = []
        for name, source in self.sources.items():
            if not self.config_status.get(name):
                helps.append(f"\n### {name.upper()}")
                helps.append(source.get_config_help())
        
        return "\n".join(helps) if helps else "所有源已配置！"


# 全局实例
_aggregator = None

def get_aggregator() -> TaskAggregator:
    global _aggregator
    if _aggregator is None:
        _aggregator = TaskAggregator()
    return _aggregator


def get_web3_tasks():
    """获取Web3真实任务"""
    from .web3_tasks import generate_web3_tasks
    return generate_web3_tasks()
