#!/usr/bin/env python3
"""
北斗七鑫 - 穷孩子 (众包数据) v1
众包任务+数据标注+其他赚钱机会
"""

import json
import time
import random
from typing import Dict, List
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque

# ==================== 配置 ====================

@dataclass
class CrowdsourceConfig:
    """众包配置"""
    resources_ratio: float = 0.02
    api_priority: int = 4
    scan_interval: int = 300
    
    modes: Dict = field(default_factory=lambda: {
        'conservative': {
            'min_payment': 20,
            'min_hourly': 15,
            'max_time': 30,
            'platforms': ['labelbox', 'scale', 'appen'],
            'auto_accept': False,
        },
        'balanced': {
            'min_payment': 10,
            'min_hourly': 10,
            'max_time': 60,
            'platforms': ['labelbox', 'scale', 'appen', 'mturk', 'prolific'],
            'auto_accept': True,
        },
        'aggressive': {
            'min_payment': 5,
            'min_hourly': 5,
            'max_time': 120,
            'platforms': ['labelbox', 'scale', 'appen', 'mturk', 'prolific', 'clickworker', 'remotasks'],
            'auto_accept': True,
        }
    })

# ==================== API ====================

class CrowdsourceAPI:
    """众包API"""
    
    def __init__(self):
        self.platforms = {
            'labelbox': {'name': 'Labelbox', 'url': 'https://api.labelbox.com', 'type': 'image'},
            'scale': {'name': 'Scale AI', 'url': 'https://api.scale.com', 'type': 'text'},
            'appen': {'name': 'Appen', 'url': 'https://api.appen.com', 'type': 'audio'},
            'mturk': {'name': 'Amazon MTurk', 'url': 'https://mturk.requester.amazon.com', 'type': 'mixed'},
            'prolific': {'name': 'Prolific', 'url': 'https://api.prolific.com', 'type': 'survey'},
            'clickworker': {'name': 'Clickworker', 'url': 'https://api.clickworker.com', 'type': 'mixed'},
            'remotasks': {'name': 'Remotasks', 'url': 'https://api.remotasks.com', 'type': 'annotation'},
        }
    
    def fetch_tasks(self) -> List[Dict]:
        return self._generate_tasks()
    
    def _generate_tasks(self) -> List[Dict]:
        tasks = [
            {'platform': 'Labelbox', 'type': 'image_bbox', 'payment': 25, 'duration': 20, 'difficulty': 'medium'},
            {'platform': 'Scale AI', 'type': 'text_classify', 'payment': 30, 'duration': 25, 'difficulty': 'easy'},
            {'platform': 'Appen', 'type': 'audio_transcribe', 'payment': 35, 'duration': 30, 'difficulty': 'medium'},
            {'platform': 'MTurk', 'type': 'survey', 'payment': 15, 'duration': 15, 'difficulty': 'easy'},
            {'platform': 'Prolific', 'type': 'survey', 'payment': 20, 'duration': 20, 'difficulty': 'easy'},
            {'platform': 'Clickworker', 'type': 'data_entry', 'payment': 10, 'duration': 15, 'difficulty': 'easy'},
            {'platform': 'Remotasks', 'type': 'image_segment', 'payment': 40, 'duration': 35, 'difficulty': 'hard'},
            {'platform': 'Labelbox', 'type': 'image_classify', 'payment': 18, 'duration': 12, 'difficulty': 'easy'},
            {'platform': 'Scale AI', 'type': 'ner_annotation', 'payment': 28, 'duration': 22, 'difficulty': 'medium'},
            {'platform': 'Appen', 'type': 'text_collection', 'payment': 22, 'duration': 18, 'difficulty': 'easy'},
        ]
        
        for t in tasks:
            t['hourly_rate'] = t['payment'] / (t['duration'] / 60)
            t['available'] = random.randint(10, 1000)
        
        return tasks
    
    def get_status(self) -> Dict:
        return {'platforms': len(self.platforms), 'active': len(self.platforms)}

# ==================== 策略 ====================

class StrategyLibrary:
    def __init__(self):
        self.strategies = {
            'max_payment': {'weight': 0.30, 'func': lambda t: t.get('payment', 0)},
            'max_efficiency': {'weight': 0.25, 'func': lambda t: t.get('hourly_rate', 0)},
            'easiest': {'weight': 0.20, 'func': lambda t: 1 if t.get('difficulty') == 'easy' else 0.5},
            'availability': {'weight': 0.15, 'func': lambda t: min(1.0, t.get('available', 0) / 100)},
            'speed': {'weight': 0.10, 'func': lambda t: 1 / max(t.get('duration', 1), 1)},
        }
    
    def analyze(self, task: Dict) -> Dict:
        scores = {}
        for sid, s in self.strategies.items():
            scores[sid] = s['func'](task) * s['weight']
        
        total = sum(scores.values())
        return {'total': min(1.0, total), 'scores': scores}

# ==================== 主系统 ====================

class CrowdsourceTool:
    def __init__(self, mode: str = 'balanced'):
        self.config = CrowdsourceConfig()
        self.mode = mode
        self.api = CrowdsourceAPI()
        self.strategy = StrategyLibrary()
        self.results = deque(maxlen=100)
    
    def scan(self) -> List[Dict]:
        tasks = self.api.fetch_tasks()
        params = self.config.modes[self.mode]
        
        opportunities = []
        for task in tasks:
            # 检查条件
            if task['payment'] < params['min_payment']:
                continue
            if task['hourly_rate'] < params['min_hourly']:
                continue
            if task['duration'] > params['max_time']:
                continue
            if task['platform'].lower() not in [p.lower() for p in params['platforms']]:
                continue
            
            # 策略分析
            strat = self.strategy.analyze(task)
            
            result = {
                'task': task,
                'strategy': strat,
                'action': 'ACCEPT' if params['auto_accept'] else 'REVIEW',
            }
            
            self.results.append(result)
            opportunities.append(result)
        
        return opportunities
    
    def get_status(self) -> Dict:
        return {
            'mode': self.mode,
            'total': len(self.results),
            'platforms': self.api.get_status()
        }

# ==================== 测试 ====================

def test():
    print("\n" + "="*60)
    print("👶 穷孩子 - 众包数据工具测试")
    print("="*60)
    
    for mode in ['conservative', 'balanced', 'aggressive']:
        print(f"\n📊 模式: {mode}")
        
        tool = CrowdsourceTool(mode=mode)
        opps = tool.scan()
        status = tool.get_status()
        
        print(f"   任务: {len(opps)}/{status['total']}")
        
        for o in opps[:3]:
            t = o['task']
            print(f"   - {t['platform']} {t['type']}: ${t['payment']} ({t['duration']}min)")
    
    print("\n✅ 测试完成")

if __name__ == '__main__':
    test()
