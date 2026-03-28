#!/usr/bin/env python3
"""
👶 穷孩子策略 - 众包任务
Version: 1.0
Author: GO2SE CEO
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional

class CrowdsourceStrategy:
    """穷孩子 - 众包任务策略"""
    
    def __init__(self, config: dict = None):
        self.config = config or self._default_config()
        
    def _default_config(self) -> dict:
        return {
            'max_hours_per_week': 10,           # 每周10小时
            'min_hourly_rate': 10,             # 最低$10/小时
            'min_approval_rate': 0.95,        # 95%验收率
            'batch_size': 10,                  # 批量10个
            'target_weekly_earn': 100,        # 目标每周$100
            'platforms': [
                'labelbox',
                'scale_ai',
                'amazon_mturk',
                'appen',
            ]
        }
    
    def get_available_tasks(self, platform: str = None) -> List[dict]:
        """获取可用任务"""
        # 实际需要接入众包平台API
        tasks = [
            # 数据标注任务
            {
                'id': 'task_001',
                'platform': 'labelbox',
                'type': 'image_labeling',
                'description': '标注图片中的车辆',
                'rate': 15,                      # $/小时
                'duration': 2,                   # 小时
                'volume': 100,                   # 任务数
                'approval_rate': 0.98,
                'difficulty': 'easy'
            },
            {
                'id': 'task_002',
                'platform': 'scale_ai',
                'type': 'text_classification',
                'description': '分类新闻文本情感',
                'rate': 18,
                'duration': 3,
                'volume': 150,
                'approval_rate': 0.97,
                'difficulty': 'medium'
            },
            # 内容审核任务
            {
                'id': 'task_003',
                'platform': 'amazon_mturk',
                'type': 'content_moderation',
                'description': '审核社交媒体内容',
                'rate': 12,
                'duration': 1,
                'volume': 200,
                'approval_rate': 0.95,
                'difficulty': 'easy'
            },
            # 翻译任务
            {
                'id': 'task_004',
                'platform': 'appen',
                'type': 'audio_transcription',
                'description': '转录英语音频',
                'rate': 20,
                'duration': 2,
                'volume': 50,
                'approval_rate': 0.96,
                'difficulty': 'medium'
            },
        ]
        
        # 过滤
        filtered = [t for t in tasks if self._check_conditions(t)]
        
        if platform:
            filtered = [t for t in filtered if t['platform'] == platform]
        
        return filtered
    
    def _check_conditions(self, task: dict) -> bool:
        """检查任务是否符合条件"""
        if task['rate'] < self.config['min_hourly_rate']:
            return False
        if task['approval_rate'] < self.config['min_approval_rate']:
            return False
        return True
    
    def optimize_task_selection(self) -> dict:
        """优化任务选择"""
        tasks = self.get_available_tasks()
        
        if not tasks:
            return {'action': 'wait', 'reason': '无可用任务'}
        
        # 按时薪排序
        sorted_tasks = sorted(tasks, key=lambda x: x['rate'], reverse=True)
        
        # 选择最高时薪的任务
        best_task = sorted_tasks[0]
        
        # 计算可执行的任务数量
        available_hours = self.config['max_hours_per_week']
        task_duration = best_task['duration']
        
        max_batch = min(
            self.config['batch_size'],
            int(available_hours / task_duration),
            best_task['volume']
        )
        
        expected_earn = max_batch * (best_task['rate'] * best_task['duration'])
        
        return {
            'strategy': 'crowdsource',
            'selected_task': best_task,
            'batch_size': max_batch,
            'expected_earn': expected_earn,
            'time_required': max_batch * best_task['duration'],
            'action': 'execute',
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_plan(self) -> dict:
        """生成周计划"""
        tasks = self.get_available_tasks()
        
        if not tasks:
            return {
                'strategy': 'crowdsource',
                'status': 'no_tasks',
                'weekly_plan': []
            }
        
        # 选择最优任务组合
        weekly_plan = []
        remaining_hours = self.config['max_hours_per_week']
        remaining_budget = self.config['target_weekly_earn']
        
        # 按时薪排序
        sorted_tasks = sorted(tasks, key=lambda x: x['rate'], reverse=True)
        
        for task in sorted_tasks:
            if remaining_hours <= 0:
                break
            if remaining_budget <= 0:
                break
            
            # 计算可执行数量
            task_hours = task['duration']
            task_earn = task['rate'] * task['duration']
            
            batch = min(
                remaining_hours // task_hours,
                task['volume'],
                self.config['batch_size']
            )
            
            if batch > 0:
                weekly_plan.append({
                    'task_id': task['id'],
                    'platform': task['platform'],
                    'type': task['type'],
                    'batch': batch,
                    'hours': batch * task_hours,
                    'earn': batch * task_earn
                })
                
                remaining_hours -= batch * task_hours
                remaining_budget -= batch * task_earn
        
        total_hours = sum(p['hours'] for p in weekly_plan)
        total_earn = sum(p['earn'] for p in weekly_plan)
        
        return {
            'strategy': 'crowdsource',
            'status': 'planned',
            'weekly_plan': weekly_plan,
            'total_hours': total_hours,
            'total_earn': total_earn,
            'target': self.config['target_weekly_earn'],
            'completion': total_earn / self.config['target_weekly_earn'],
            'timestamp': datetime.now().isoformat()
        }
    
    def execute_task(self, task_id: str, batch: int = 1) -> dict:
        """执行任务"""
        tasks = self.get_available_tasks()
        task = next((t for t in tasks if t['id'] == task_id), None)
        
        if not task:
            return {'status': 'error', 'reason': '任务不存在'}
        
        # 模拟执行
        executed = {
            'task_id': task_id,
            'platform': task['platform'],
            'type': task['type'],
            'batch': batch,
            'status': 'completed',
            'earn': batch * task['rate'] * task['duration'],
            'timestamp': datetime.now().isoformat()
        }
        
        return executed


if __name__ == '__main__':
    strategy = CrowdsourceStrategy()
    plan = strategy.generate_plan()
    print(f"👶 穷孩子策略 - 周计划")
    print(f"  目标: ${plan.get('target', 0)}")
    print(f"  预计: ${plan.get('total_earn', 0)}")
    print(f"  完成度: {plan.get('completion', 0)*100:.0f}%")
