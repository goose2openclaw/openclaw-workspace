#!/usr/bin/env python3
"""
大白鹅CEO - 自动调度系统
每20分钟自动执行调度任务
"""

import time
import json
import os
import sys
from typing import Dict, List
sys.path.insert(0, '/root/.openclaw/workspace')

from datetime import datetime
from skills.go2se.scripts.goose_scheduler import GooseScheduler
from skills.go2se.scripts.risk_control_system import AlertSystem
from skills.go2se.scripts.visualization_dashboard import Visualizer

# ==================== 自动调度器 ====================

class AutoScheduler:
    """自动调度器"""
    
    def __init__(self, interval: int = 1200):  # 20分钟
        self.interval = interval
        self.is_running = False
        self.last_task = None
        self.task_queue = []
        self.stats = {
            'total_runs': 0,
            'total_tasks': 0,
            'last_run': None
        }
        
        # 加载任务配置
        self.tasks = self._load_tasks()
    
    def _load_tasks(self):
        """加载任务"""
        return [
            {'name': 'goose_scheduler', 'module': 'goose', 'interval': 1200, 'enabled': True},
            {'name': 'risk_monitor', 'module': 'risk', 'interval': 900, 'enabled': True},
            {'name': 'visualization', 'module': 'viz', 'interval': 1800, 'enabled': True},
        ]
    
    def add_task(self, task: Dict):
        """添加任务"""
        self.task_queue.append(task)
        self.stats['total_tasks'] += 1
    
    def clear_queue(self):
        """清空队列"""
        self.task_queue = []
    
    def run(self):
        """运行调度器"""
        self.is_running = True
        
        print("\n" + "="*60)
        print("🪿 大白鹅CEO - 自动调度系统启动")
        print("="*60)
        print(f"⏰ 间隔: {self.interval/60}分钟")
        print(f"📋 任务数: {len(self.tasks)}")
        
        cycle = 0
        
        while self.is_running:
            cycle += 1
            cycle_start = time.time()
            
            print(f"\n{'='*60}")
            print(f"🔄 第 {cycle} 轮 - {datetime.now().strftime('%H:%M:%S')}")
            print("="*60)
            
            # 1. 检查任务队列（优先级最高）
            if self.task_queue:
                print(f"\n📋 执行队列任务: {len(self.task_queue)}个")
                self._execute_queue()
            
            # 2. 执行计划任务
            self._execute_scheduled()
            
            # 3. 更新统计
            self.stats['total_runs'] += 1
            self.stats['last_run'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 4. 等待
            elapsed = time.time() - cycle_start
            wait_time = max(1, self.interval - elapsed)
            
            print(f"\n⏳ 等待下一轮 ({wait_time:.0f}秒)...")
            
            # 等待时检查新任务
            for _ in range(int(wait_time)):
                if not self.is_running:
                    break
                time.sleep(1)
        
        print("\n🛑 调度器已停止")
    
    def _execute_queue(self):
        """执行队列任务"""
        for task in self.task_queue:
            print(f"\n🎯 执行任务: {task.get('name', 'unknown')}")
            
            try:
                result = self._run_task(task)
                print(f"   ✅ 完成")
            except Exception as e:
                print(f"   ❌ 失败: {e}")
        
        # 清空队列
        self.clear_queue()
    
    def _execute_scheduled(self):
        """执行计划任务"""
        for task in self.tasks:
            if not task.get('enabled', True):
                continue
            
            print(f"\n🔧 执行计划任务: {task['name']}")
            
            try:
                result = self._run_task(task)
                
                # 输出简要结果
                if task['module'] == 'goose':
                    if 'insights' in result:
                        print(f"   🧠 洞察: {result['insights'].get('key_insight', 'N/A')[:50]}")
                        print(f"   ⚔️ 挑战: {len(result.get('challenges', []))}个")
                        print(f"   ❓ 问题: {len(result.get('questions', []))}个")
                
                elif task['module'] == 'risk':
                    print(f"   🛡️ 告警: {result.get('total_alerts', 0)}个")
                    print(f"   ⚡ 自动动作: {result.get('auto_actions', 0)}个")
                
                elif task['module'] == 'viz':
                    print(f"   📊 面板已更新")
                
            except Exception as e:
                print(f"   ❌ 失败: {e}")
    
    def _run_task(self, task: Dict) -> Dict:
        """运行单个任务"""
        module = task['module']
        
        if module == 'goose':
            scheduler = GooseScheduler()
            # 只运行1个周期
            result = scheduler.scheduler.run_cycle()
            return result
        
        elif module == 'risk':
            system = AlertSystem()
            result = system.run_cycle()
            return result
        
        elif module == 'viz':
            viz = Visualizer()
            viz.update_all()
            return {'status': 'ok'}
        
        return {}
    
    def stop(self):
        """停止调度器"""
        self.is_running = False
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            'running': self.is_running,
            'queue_size': len(self.task_queue),
            'stats': self.stats,
            'tasks': self.tasks
        }

# ==================== 交互接口 ====================

def status():
    """查看状态"""
    # 简单检查文件
    try:
        with open('/tmp/goose_scheduler_status.json', 'r') as f:
            data = json.load(f)
            return data
    except:
        return {'status': 'not_running'}

def add_task(task_name: str):
    """添加任务"""
    print(f"📝 添加任务: {task_name}")
    # 可以扩展为实际添加任务

# ==================== 主程序 ====================

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == 'start':
            scheduler = AutoScheduler(interval=1200)
            scheduler.run()
        
        elif cmd == 'status':
            print(json.dumps(status(), indent=2))
        
        elif cmd == 'stop':
            print("🛑 停止调度器")
        
        else:
            print(f"未知命令: {cmd}")
            print("用法: python auto_dispatch.py [start|status|stop]")
    else:
        # 默认运行
        scheduler = AutoScheduler(interval=1200)
        scheduler.run()
