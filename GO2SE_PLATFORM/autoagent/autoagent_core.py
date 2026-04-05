#!/usr/bin/env python3
"""
🪿 GO2SE AutoAgent - 自主运作智能体
===================================
实现系统自主运行、自我监控、自动修复、持续优化

职责:
1. 系统健康监控
2. MiroFish自动仿真
3. 双脑自主切换
4. 交易信号执行
5. 策略自动迭代
6. 异常自动修复
"""

import asyncio
import json
import time
import os
import subprocess
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

# API密钥
API_KEY = "GO2SE_e083a64d891b45089d6f37acb440435eba401313a1695711"
API_BASE = "http://localhost:8004"

class AgentState(Enum):
    IDLE = "idle"
    MONITORING = "monitoring"
    EXECUTING = "executing"
    RECOVERING = "recovering"
    ITERATING = "iterating"

@dataclass
class SystemHealth:
    backend: bool = False
    frontend: bool = False
    brain: str = "left"
    memory_usage: float = 0.0
    cpu_usage: float = 0.0
    last_simulation_score: float = 0.0
    active_positions: int = 0
    timestamp: str = ""

@dataclass
class AgentConfig:
    name: str = "GO2SE_AutoAgent"
    check_interval: int = 60  # 健康检查间隔(秒)
    simulation_interval: int = 7200  # MiroFish仿真间隔(2小时)
    brain_switch_threshold: float = 0.7  # 脑切换阈值
    max_recovery_attempts: int = 3
    auto_iterate: bool = True
    paper_mode: bool = True  # 默认Paper交易

class GO2SEAUTOAGENT:
    """GO2SE自主智能体"""
    
    def __init__(self, config: AgentConfig = None):
        self.config = config or AgentConfig()
        self.state = AgentState.IDLE
        self.health = SystemHealth()
        self.simulation_history: List[Dict] = []
        self.error_log: List[Dict] = []
        self.recovery_attempts = 0
        self.last_brain_switch = None
        self.iteration_count = 0
        
    async def start(self):
        """启动AutoAgent"""
        print(f"""
╔══════════════════════════════════════════════════════╗
║     🪿 GO2SE AutoAgent 启动                          ║
╠══════════════════════════════════════════════════════╣
║  名称: {self.config.name}
║  检查间隔: {self.config.check_interval}秒
║  仿真间隔: {self.config.simulation_interval}秒
║  交易模式: {'Paper' if self.config.paper_mode else 'Real'}
╚══════════════════════════════════════════════════════╝
        """)
        
        self.state = AgentState.MONITORING
        await self.main_loop()
    
    async def main_loop(self):
        """主循环"""
        iteration = 0
        last_simulation = time.time()
        
        while True:
            iteration += 1
            print(f"\n[#{iteration}] {datetime.now().isoformat()}")
            
            # 1. 系统健康检查
            await self.check_health()
            
            # 2. 执行必要的恢复
            if not self.health.backend or not self.health.frontend:
                await self.recover()
            
            # 3. MiroFish仿真 (定时)
            if time.time() - last_simulation > self.config.simulation_interval:
                await self.run_simulation()
                last_simulation = time.time()
            
            # 4. 脑状态检查
            await self.check_brain()
            
            # 5. 交易信号处理
            await self.process_signals()
            
            # 6. 迭代优化
            if self.config.auto_iterate and iteration % 10 == 0:
                await self.auto_iterate()
            
            await asyncio.sleep(self.config.check_interval)
    
    async def check_health(self):
        """检查系统健康状态"""
        import psutil
        
        # Backend检查
        try:
            import requests
            r = requests.get(f"{API_BASE}/api/stats", timeout=5)
            self.health.backend = r.status_code == 200
        except:
            self.health.backend = False
        
        # Frontend检查
        try:
            r = requests.get("http://localhost:8010/", timeout=5)
            self.health.frontend = r.status_code == 200
        except:
            self.health.frontend = False
        
        # 系统资源
        mem = psutil.virtual_memory()
        self.health.memory_usage = mem.percent
        self.health.cpu_usage = psutil.cpu_percent(interval=1)
        
        # Brain状态
        try:
            r = requests.get(f"{API_BASE}/api/brain", timeout=5)
            if r.status_code == 200:
                data = r.json()
                self.health.brain = data.get("data", {}).get("left", {}).get("status") == "active" and "left" or "right"
        except:
            pass
        
        print(f"  🏥 健康: Backend={'✅' if self.health.backend else '❌'} | "
              f"Frontend={'✅' if self.health.frontend else '❌'} | "
              f"Memory={self.health.memory_usage:.1f}% | "
              f"CPU={self.health.cpu_usage:.1f}% | "
              f"Brain={self.health.brain}")
    
    async def recover(self):
        """系统恢复"""
        self.state = AgentState.RECOVERING
        self.recovery_attempts += 1
        
        if self.recovery_attempts > self.config.max_recovery_attempts:
            print(f"  ⚠️ 超过最大恢复次数({self.config.max_recovery_attempts})，标记需要人工介入")
            self.error_log.append({
                "type": "recovery_failed",
                "attempts": self.recovery_attempts,
                "timestamp": datetime.now().isoformat()
            })
            return
        
        print(f"  🔧 尝试恢复 (尝试 {self.recovery_attempts}/{self.config.max_recovery_attempts})")
        
        if not self.health.backend:
            print("  → 重启Backend...")
            os.system("pkill -f 'uvicorn app.main:app' 2>/dev/null")
            os.system("cd /root/.openclaw/workspace/GO2SE_PLATFORM/backend && "
                     "nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8004 &>/dev/null &")
        
        if not self.health.frontend:
            print("  → 重启Frontend...")
            os.system("pkill -f 'http.server 8010' 2>/dev/null")
            os.system("cd /root/.openclaw/workspace/GO2SE_PLATFORM/versions/v10 && "
                     "nohup python3 -m http.server 8010 &>/dev/null &")
        
        await asyncio.sleep(5)
        await self.check_health()
        
        if self.health.backend and self.health.frontend:
            print("  ✅ 恢复成功")
            self.recovery_attempts = 0
    
    async def run_simulation(self):
        """运行MiroFish仿真"""
        self.state = AgentState.ITERATING
        print("  🔬 运行MiroFish全向仿真...")
        
        try:
            result = subprocess.run(
                ["python3", "scripts/mirofish_full_simulation_v2.py"],
                cwd="/root/.openclaw/workspace/GO2SE_PLATFORM",
                capture_output=True,
                text=True,
                timeout=60
            )
            
            output = result.stdout + result.stderr
            score = 0.0
            for line in output.split('\n'):
                if '综合评分' in line or '综合得分' in line:
                    try:
                        score = float(''.join(filter(lambda x: x.isdigit() or x=='.', line.split(':')[-1])))
                    except:
                        pass
            
            self.health.last_simulation_score = score
            self.simulation_history.append({
                "score": score,
                "timestamp": datetime.now().isoformat(),
                "state": "normal"
            })
            
            print(f"  📊 仿真评分: {score}/100")
            
            # 评分低于阈值时的处理
            if score < 85:
                print(f"  ⚠️ 评分低于85，启动优化...")
                await self.auto_optimize(score)
            
        except Exception as e:
            print(f"  ❌ 仿真失败: {e}")
            self.error_log.append({
                "type": "simulation_failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
        
        self.state = AgentState.MONITORING
    
    async def check_brain(self):
        """检查并切换脑状态"""
        if self.health.last_simulation_score > 0:
            # 根据评分和状态自动切换脑
            if self.health.last_simulation_score < 80 and self.health.brain == "left":
                print("  🧠 低评分，考虑切换到右脑(专家模式)...")
                # 可以在这里实现自动切换逻辑
            elif self.health.last_simulation_score > 95 and self.health.brain == "right":
                print("  🧠 高评分，考虑切换到左脑(稳健模式)...")
    
    async def process_signals(self):
        """处理交易信号"""
        if self.config.paper_mode:
            # Paper模式: 模拟信号处理
            pass
    
    async def auto_iterate(self):
        """自动迭代优化"""
        self.iteration_count += 1
        print(f"  🔄 自动迭代 #{self.iteration_count}")
        
        # 检查迭代趋势
        if len(self.simulation_history) >= 5:
            recent = self.simulation_history[-5:]
            avg = sum(h["score"] for h in recent) / len(recent)
            if recent[-1]["score"] < avg - 2:
                print(f"  ⚠️ 检测到评分下降趋势，启动优化...")
                await self.auto_optimize(recent[-1]["score"])
    
    async def auto_optimize(self, score: float):
        """自动优化"""
        print(f"  🛠️ 优化策略: 当前评分 {score}")
        # 根据评分和具体维度进行优化
        optimizations = []
        
        if score < 70:
            optimizations.append("D2-算力资源扩展")
        if score < 80:
            optimizations.append("B4-跟大哥策略优化")
        
        for opt in optimizations:
            print(f"  → {opt}")
    
    def get_status(self) -> Dict[str, Any]:
        """获取Agent状态"""
        return {
            "name": self.config.name,
            "state": self.state.value,
            "health": asdict(self.health),
            "iterations": self.iteration_count,
            "recovery_attempts": self.recovery_attempts,
            "simulation_history_count": len(self.simulation_history),
            "error_count": len(self.error_log),
            "uptime": datetime.now().isoformat()
        }


async def main():
    """主入口"""
    config = AgentConfig(
        name="GO2SE_CEO_AutoAgent",
        check_interval=60,
        simulation_interval=7200,  # 2小时
        brain_switch_threshold=0.7,
        max_recovery_attempts=3,
        auto_iterate=True,
        paper_mode=True
    )
    
    agent = GO2SEAUTOAGENT(config)
    await agent.start()


if __name__ == "__main__":
    asyncio.run(main())