"""
🧠 GO2SE 左右脑架构 - 生产部署方案
======================================

左右脑并行架构:
- 左脑: 普通模式 (稳健)
- 右脑: 专家模式 (激进)
- 互为备份，自动切换
- UI一键切换

中转钱包架构:
- 智能合约隔离
- 主钱包 → 中转钱包 → 交易所
- 安全第一

龙虾模块:
- 复盘 (Retro)
- 仿真 (Simulation)
- 优化 (Optimization)

2026-04-04
"""

import asyncio
import json
import time
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
import random
import hashlib

# ============================================================================
# 左右脑状态机
# ============================================================================

class BrainState:
    """脑状态"""
    ACTIVE = "active"
    STANDBY = "standby"
    CRASHED = "crashed"
    SWITCHING = "switching"

@dataclass
class BrainStatus:
    """脑状态信息"""
    brain_id: str  # "left" or "right"
    mode: str  # "normal" or "expert"
    state: str
    health_score: float
    last_heartbeat: float
    crash_count: int
    switch_count: int

# ============================================================================
# 中转钱包架构
# ============================================================================

class WalletArchitecture:
    """
    中转钱包架构
    
    流程:
    主钱包 → 中转钱包(智能合约) → 交易所
         ↑                      ↓
         ←────── 收益回流 ←──────
    """
    
    def __init__(self):
        self.main_wallet = {
            "address": "0x_MAIN_WALLET_",
            "balance": 100000,
            "min_reserve": 20000  # 最低保留
        }
        
        self.transfer_wallet = {
            "address": "0x_TRANSFER_CONTRACT_",
            "balance": 50000,
            "max_transfer": 10000,  # 每次最大中转
            "min_transfer": 1000     # 每次最小中转
        }
        
        self.exchange_wallets = {
            "binance": {"address": "0x_BINANCE_", "balance": 30000},
            "bybit": {"address": "0x_BYBIT_", "balance": 20000},
            "okx": {"address": "0x_OKX_", "balance": 15000}
        }
        
        # 交易记录
        self.transfer_log = deque(maxlen=1000)
        
    def transfer_to_exchange(self, amount: float, target: str) -> Dict:
        """中转到交易所"""
        if target not in self.exchange_wallets:
            return {"success": False, "error": "Invalid exchange"}
        
        if amount < self.transfer_wallet["min_transfer"]:
            return {"success": False, "error": "Below minimum transfer"}
        
        if amount > self.transfer_wallet["max_transfer"]:
            return {"success": False, "error": "Exceeds maximum transfer"}
        
        if self.transfer_wallet["balance"] < amount:
            return {"success": False, "error": "Insufficient balance"}
        
        # 执行转账
        self.transfer_wallet["balance"] -= amount
        self.exchange_wallets[target]["balance"] += amount
        
        # 记录
        tx = {
            "tx_id": hashlib.md5(f"{time.time()}{amount}".encode()).hexdigest()[:16],
            "from": "transfer_wallet",
            "to": target,
            "amount": amount,
            "timestamp": datetime.now().isoformat()
        }
        self.transfer_log.append(tx)
        
        return {"success": True, "tx": tx}
    
    def return_to_main(self, amount: float) -> Dict:
        """收益回流主钱包"""
        if self.transfer_wallet["balance"] < amount:
            return {"success": False, "error": "Insufficient balance"}
        
        self.transfer_wallet["balance"] -= amount
        self.main_wallet["balance"] += amount
        
        return {
            "success": True,
            "amount": amount,
            "main_balance": self.main_wallet["balance"]
        }
    
    def get_status(self) -> Dict:
        """获取钱包状态"""
        return {
            "main_wallet": self.main_wallet,
            "transfer_wallet": self.transfer_wallet,
            "exchange_wallets": self.exchange_wallets,
            "total_assets": (
                self.main_wallet["balance"] +
                self.transfer_wallet["balance"] +
                sum(w["balance"] for w in self.exchange_wallets.values())
            )
        }

# ============================================================================
# 左右脑引擎
# ============================================================================

class BrainEngine:
    """左右脑引擎"""
    
    def __init__(self, brain_id: str, mode: str):
        self.brain_id = brain_id  # "left" or "right"
        self.mode = mode  # "normal" or "expert"
        self.state = BrainState.STANDBY
        self.health_score = 1.0
        self.last_heartbeat = time.time()
        self.crash_count = 0
        self.switch_count = 0
        
        # 核心组件
        from app.core.go2se_v9_core import GO2SEV9Engine
        self.engine = GO2SEV9Engine(mode=mode)
        
        # 心跳统计
        self.heartbeats = deque(maxlen=100)
        
    def heartbeat(self) -> bool:
        """发送心跳"""
        now = time.time()
        elapsed = now - self.last_heartbeat
        
        # 检查是否存活 (5秒内有心跳)
        is_alive = elapsed < 5
        
        self.heartbeats.append({
            "timestamp": now,
            "elapsed": elapsed,
            "alive": is_alive
        })
        
        self.last_heartbeat = now
        
        if is_alive:
            self.health_score = min(1.0, self.health_score + 0.01)
        else:
            self.health_score = max(0.0, self.health_score - 0.1)
            if self.health_score < 0.3:
                self.state = BrainState.CRASHED
        
        return is_alive
    
    def activate(self):
        """激活脑"""
        self.state = BrainState.ACTIVE
        self.switch_count += 1
        
    def standby(self):
        """待机"""
        self.state = BrainState.STANDBY
        
    def crash(self):
        """崩溃"""
        self.state = BrainState.CRASHED
        self.crash_count += 1

# ============================================================================
# 左右脑管理器
# ============================================================================

class BrainManager:
    """
    左右脑管理器
    
    功能:
    - 双脑并行运行
    - 心跳监控
    - 自动切换
    - 状态同步
    """
    
    def __init__(self):
        # 创建左右脑
        self.left_brain = BrainEngine("left", "normal")
        self.right_brain = BrainEngine("right", "expert")
        
        # 默认左脑活跃
        self.left_brain.activate()
        
        # 当前活跃脑
        self.active_brain = self.left_brain
        
        # 钱包架构
        self.wallet = WalletArchitecture()
        
        # 监控历史
        self.monitoring_history = deque(maxlen=1000)
        
        # 配置
        self.config = {
            "heartbeat_interval": 1.0,      # 心跳间隔(秒)
            "switch_threshold": 0.3,        # 切换阈值
            "crash_timeout": 5.0,            # 崩溃超时(秒)
            "sync_interval": 10.0,           # 同步间隔(秒)
            "auto_switch": True              # 自动切换
        }
        
    @property
    def current_mode(self) -> str:
        """当前模式"""
        return self.active_brain.mode
    
    @property
    def current_brain_id(self) -> str:
        """当前脑ID"""
        return self.active_brain.brain_id
    
    async def send_heartbeat(self) -> Dict:
        """发送心跳"""
        left_alive = self.left_brain.heartbeat()
        right_alive = self.right_brain.heartbeat()
        
        status = {
            "timestamp": datetime.now().isoformat(),
            "left": {
                "brain_id": self.left_brain.brain_id,
                "mode": self.left_brain.mode,
                "state": self.left_brain.state,
                "health": self.left_brain.health_score,
                "alive": left_alive
            },
            "right": {
                "brain_id": self.right_brain.brain_id,
                "mode": self.right_brain.mode,
                "state": self.right_brain.state,
                "health": self.right_brain.health_score,
                "alive": right_alive
            },
            "active_brain": self.active_brain.brain_id
        }
        
        self.monitoring_history.append(status)
        
        # 检查是否需要切换
        if self.config["auto_switch"]:
            await self._check_switch()
        
        return status
    
    async def _check_switch(self):
        """检查是否需要切换"""
        left = self.left_brain
        right = self.right_brain
        
        # 如果活跃脑崩溃，切换到备用脑
        if self.active_brain.state == BrainState.CRASHED:
            if self.active_brain == self.left_brain and right.state != BrainState.CRASHED:
                await self._switch_to(right)
            elif self.active_brain == self.right_brain and left.state != BrainState.CRASHED:
                await self._switch_to(left)
        
        # 如果备用脑更健康，询问是否切换
        standby = self.left_brain if self.active_brain == self.right_brain else self.right_brain
        if standby.health_score > self.active_brain.health_score + 0.3:
            # 健康度差距超过30%，可以考虑切换
            # 但目前只做被动切换
            pass
    
    async def _switch_to(self, new_brain: BrainEngine):
        """切换到新脑"""
        old_brain = self.active_brain
        
        new_brain.state = BrainState.SWITCHING
        
        # 等待状态同步
        await asyncio.sleep(0.5)
        
        # 切换
        old_brain.standby()
        new_brain.activate()
        self.active_brain = new_brain
        
        print(f"🧠 切换脑: {old_brain.brain_id} → {new_brain.brain_id}")
    
    async def switch_brain(self, target_brain_id: str) -> Dict:
        """手动切换脑"""
        if target_brain_id == self.active_brain.brain_id:
            return {"success": False, "error": "Already active"}
        
        if target_brain_id == "left":
            target = self.left_brain
        elif target_brain_id == "right":
            target = self.right_brain
        else:
            return {"success": False, "error": "Invalid brain ID"}
        
        await self._switch_to(target)
        
        return {
            "success": True,
            "active_brain": self.active_brain.brain_id,
            "mode": self.active_brain.mode
        }
    
    async def switch_mode(self, target_mode: str) -> Dict:
        """切换模式"""
        if target_mode == self.current_mode:
            return {"success": False, "error": "Already in this mode"}
        
        # 找到目标模式的脑
        if self.left_brain.mode == target_mode:
            target_brain = self.left_brain
        elif self.right_brain.mode == target_mode:
            target_brain = self.right_brain
        else:
            return {"success": False, "error": "Mode not available"}
        
        await self._switch_to(target_brain)
        
        return {
            "success": True,
            "active_brain": self.active_brain.brain_id,
            "mode": self.active_brain.mode
        }
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            "active_brain": self.active_brain.brain_id,
            "active_mode": self.active_brain.mode,
            "left_brain": {
                "brain_id": self.left_brain.brain_id,
                "mode": self.left_brain.mode,
                "state": self.left_brain.state,
                "health": self.left_brain.health_score,
                "crash_count": self.left_brain.crash_count,
                "switch_count": self.left_brain.switch_count
            },
            "right_brain": {
                "brain_id": self.right_brain.brain_id,
                "mode": self.right_brain.mode,
                "state": self.right_brain.state,
                "health": self.right_brain.health_score,
                "crash_count": self.right_brain.crash_count,
                "switch_count": self.right_brain.switch_count
            },
            "wallet": self.wallet.get_status(),
            "config": self.config
        }

# ============================================================================
# 龙虾模块 (复盘/仿真/优化)
# ============================================================================

class LobsterModule:
    """
    龙虾模块
    
    - 复盘 (Retro): 周期性复盘
    - 仿真 (Simulation): MiroFish全向仿真
    - 优化 (Optimization): 参数优化
    """
    
    def __init__(self, brain_manager: BrainManager):
        self.brain_manager = brain_manager
        
        # 复盘
        self.retro_history = deque(maxlen=50)
        self.last_retro_time = 0
        
        # 仿真
        self.simulation_history = deque(maxlen=50)
        
        # 优化
        self.optimization_history = deque(maxlen=50)
        
    async def run_retro(self) -> Dict:
        """运行复盘"""
        from app.core.go2se_v9_optimizer import GstackTeamReview
        
        team = GstackTeamReview()
        result = team.run_review(f"GO2SE-{self.brain_manager.current_mode}")
        
        retro = {
            "timestamp": datetime.now().isoformat(),
            "mode": self.brain_manager.current_mode,
            "result": result
        }
        
        self.retro_history.append(retro)
        self.last_retro_time = time.time()
        
        return retro
    
    async def run_simulation(self) -> Dict:
        """运行仿真"""
        from app.core.go2se_v9_optimizer import MiroFishSimulation
        
        sim = MiroFishSimulation(agent_count=1000)
        result = sim.run_full_simulation()
        
        simulation = {
            "timestamp": datetime.now().isoformat(),
            "mode": self.brain_manager.current_mode,
            "result": result
        }
        
        self.simulation_history.append(simulation)
        
        return simulation
    
    async def run_optimization(self) -> Dict:
        """运行优化"""
        from app.core.go2se_v9_optimizer import StrategyOptimizer
        
        optimizer = StrategyOptimizer()
        
        current_weights = {
            "mirofish": 0.30,
            "external": 0.25,
            "historical": 0.20,
            "ml": 0.15,
            "consensus": 0.10
        }
        
        optimized = optimizer.optimize_weights(current_weights, {})
        
        optimization = {
            "timestamp": datetime.now().isoformat(),
            "mode": self.brain_manager.current_mode,
            "before": current_weights,
            "after": optimized
        }
        
        self.optimization_history.append(optimization)
        
        return optimization
    
    async def run_full_cycle(self) -> Dict:
        """运行完整龙虾周期"""
        retro = await self.run_retro()
        simulation = await self.run_simulation()
        optimization = await self.run_optimization()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "retro": retro,
            "simulation": simulation,
            "optimization": optimization,
            "mode": self.brain_manager.current_mode
        }
    
    def get_lobster_status(self) -> Dict:
        """获取龙虾状态"""
        return {
            "retro_count": len(self.retro_history),
            "simulation_count": len(self.simulation_history),
            "optimization_count": len(self.optimization_history),
            "last_retro": datetime.fromtimestamp(self.last_retro_time).isoformat() if self.last_retro_time else None
        }

# ============================================================================
# GO2SE 双脑主引擎
# ============================================================================

class GO2SEDualBrainEngine:
    """
    GO2SE 双脑主引擎
    
    整合:
    - 左右脑并行
    - 中转钱包
    - 龙虾模块
    """
    
    VERSION = "v9.0-dual-brain"
    
    def __init__(self):
        # 左右脑管理器
        self.brain_manager = BrainManager()
        
        # 龙虾模块
        self.lobster = LobsterModule(self.brain_manager)
        
        # 状态
        self.start_time = time.time()
        self.is_running = False
        
    async def start(self):
        """启动引擎"""
        self.is_running = True
        self.start_time = time.time()
        print("🧠 GO2SE 双脑引擎启动")
        
    async def stop(self):
        """停止引擎"""
        self.is_running = False
        print("🧠 GO2SE 双脑引擎停止")
    
    async def get_status(self) -> Dict:
        """获取状态"""
        return {
            "version": self.VERSION,
            "running": self.is_running,
            "uptime": time.time() - self.start_time,
            "brain_manager": self.brain_manager.get_status(),
            "lobster": self.lobster.get_lobster_status()
        }
    
    async def execute_trade(self, signal: Dict) -> Dict:
        """执行交易"""
        brain = self.brain_manager.active_brain
        result = await brain.engine.execute_trade(signal)
        
        # 中转钱包处理
        if result.get("win"):
            # 盈利时，部分回流
            profit = result["pnl_pct"] * brain.engine.capital
            if profit > 100:
                self.brain_manager.wallet.return_to_main(profit * 0.1)
        
        return result

# ============================================================================
# 导出
# ============================================================================

__all__ = [
    "BrainState",
    "BrainStatus",
    "WalletArchitecture",
    "BrainEngine",
    "BrainManager",
    "LobsterModule",
    "GO2SEDualBrainEngine",
]
