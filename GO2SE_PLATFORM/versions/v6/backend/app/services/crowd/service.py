#!/usr/bin/env python3
"""
🪿 穷孩子服务 - 众包数据
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CrowdTask:
    """众包任务"""
    id: str
    name: str
    platform: str
    task_type: str  # label/survey/translate/validate
    reward: float    # USD
    duration_min: int
    difficulty: str
    requirements: List[str]


@dataclass
class CrowdResult:
    """众包结果"""
    task_id: str
    success: bool
    reward: float
    error: Optional[str]


class CrowdService:
    """穷孩子 - 众包数据服务"""
    
    TASK_TEMPLATES = [
        {
            "name": "AI图片标注",
            "platform": "Labelbox",
            "task_type": "label",
            "reward": 15,
            "duration_min": 30,
            "difficulty": "easy",
            "requirements": ["会基本英语", "细心"]
        },
        {
            "name": "加密货币问卷",
            "platform": "SurveySphere",
            "task_type": "survey",
            "reward": 10,
            "duration_min": 15,
            "difficulty": "easy",
            "requirements": ["了解加密货币"]
        },
        {
            "name": "文档翻译",
            "platform": "Lokalise",
            "task_type": "translate",
            "reward": 25,
            "duration_min": 45,
            "difficulty": "medium",
            "requirements": ["中英双语"]
        },
        {
            "name": "数据验证",
            "platform": "Appen",
            "task_type": "validate",
            "reward": 12,
            "duration_min": 20,
            "difficulty": "easy",
            "requirements": ["仔细认真"]
        }
    ]
    
    def __init__(self):
        self.tasks: Dict[str, CrowdTask] = {}
        self.results: List[CrowdResult] = []
        self.completed = 0
    
    async def scan_opportunities(self) -> List[CrowdTask]:
        """扫描众包机会"""
        tasks = []
        
        for i, template in enumerate(self.TASK_TEMPLATES):
            task = CrowdTask(
                id=f"crowd_{i}_{datetime.now().strftime('%Y%m%d%H%M')}",
                name=template['name'],
                platform=template['platform'],
                task_type=template['task_type'],
                reward=template['reward'],
                duration_min=template['duration_min'],
                difficulty=template['difficulty'],
                requirements=template['requirements']
            )
            tasks.append(task)
            self.tasks[task.id] = task
        
        return tasks
    
    async def execute_task(self, task_id: str) -> CrowdResult:
        """执行众包任务"""
        if task_id not in self.tasks:
            return CrowdResult(task_id, False, 0, "任务不存在")
        
        task = self.tasks[task_id]
        
        try:
            await asyncio.sleep(0.5)  # 模拟
            
            result = CrowdResult(
                task_id=task_id,
                success=True,
                reward=task.reward * 0.95,
                error=None
            )
            
            self.results.append(result)
            self.completed += 1
            
            return result
            
        except Exception as e:
            return CrowdResult(task_id, False, 0, str(e))
    
    def get_stats(self) -> Dict:
        completed = [r for r in self.results if r.success]
        
        return {
            "available_tasks": len(self.tasks),
            "completed": self.completed,
            "total_earned": sum(r.reward for r in completed),
            "avg_reward": sum(r.reward for r in completed) / len(completed) if completed else 0
        }


crowd_service = CrowdService()
