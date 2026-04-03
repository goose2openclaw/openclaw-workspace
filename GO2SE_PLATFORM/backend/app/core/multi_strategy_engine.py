"""
🚀 多策略并行引擎
=================
在不改变现有架构的情况下，为北斗七鑫添加多策略并行能力

功能:
- 同时运行多个策略实例
- 策略间资源共享
- 统一风控管理
- 并行信号生成
"""

import asyncio
import threading
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class StrategyInstance:
    """策略实例"""
    name: str
    strategy_func: Callable
    params: Dict = field(default_factory=dict)
    enabled: bool = True
    priority: int = 1  # 1-10, 越高越优先
    max_position_pct: float = 20.0
    status: str = "idle"  # idle, running, error


@dataclass
class ParallelSignal:
    """并行信号"""
    strategy_name: str
    symbol: str
    direction: str  # LONG, SHORT, HOLD
    confidence: float  # 0.0 - 1.0
    leverage: int = 1
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)


class MultiStrategyEngine:
    """
    多策略并行引擎
    =================
    支持多种策略并行运行，统一信号聚合
    """
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.strategies: Dict[str, StrategyInstance] = {}
        self.signal_cache: Dict[str, List[ParallelSignal]] = {}
        self.results_queue = asyncio.Queue()
        self.running = False
        self._lock = threading.Lock()
        
        # 信号聚合权重
        self.strategy_weights = {
            "mirofish": 0.3,    # MiroFish 30%
            "sonar": 0.25,       # 声纳库 25%
            "expert": 0.25,      # 专家模式 25%
            "momentum": 0.2      # 动量策略 20%
        }
    
    def register_strategy(self, name: str, strategy_func: Callable, 
                         params: Dict = None, priority: int = 5) -> None:
        """注册策略"""
        with self._lock:
            self.strategies[name] = StrategyInstance(
                name=name,
                strategy_func=strategy_func,
                params=params or {},
                priority=priority
            )
            logger.info(f"✅ 策略已注册: {name} (优先级: {priority})")
    
    def unregister_strategy(self, name: str) -> None:
        """注销策略"""
        with self._lock:
            if name in self.strategies:
                del self.strategies[name]
                logger.info(f"🗑️ 策略已注销: {name}")
    
    async def run_parallel(self, symbols: List[str], 
                          timeout: float = 30.0) -> Dict[str, List[ParallelSignal]]:
        """
        并行运行所有策略
        =================
        返回: {symbol: [signals]}
        """
        self.running = True
        results = {sym: [] for sym in symbols}
        
        # 创建任务
        tasks = []
        for symbol in symbols:
            for name, instance in self.strategies.items():
                if instance.enabled:
                    task = asyncio.create_task(
                        self._run_strategy(name, symbol, timeout)
                    )
                    tasks.append((symbol, name, task))
        
        # 并行执行
        if tasks:
            completed = await asyncio.gather(
                *[t[2] for t in tasks],
                return_exceptions=True
            )
            
            # 收集结果
            for i, (symbol, name, _) in enumerate(tasks):
                result = completed[i]
                if isinstance(result, ParallelSignal):
                    results[symbol].append(result)
        
        self.running = False
        return results
    
    async def _run_strategy(self, name: str, symbol: str, 
                           timeout: float) -> Optional[ParallelSignal]:
        """运行单个策略"""
        instance = self.strategies.get(name)
        if not instance:
            return None
        
        try:
            instance.status = "running"
            
            # 执行策略 (带超时)
            result = await asyncio.wait_for(
                asyncio.to_thread(instance.strategy_func, symbol, instance.params),
                timeout=timeout
            )
            
            if result:
                signal = ParallelSignal(
                    strategy_name=name,
                    symbol=symbol,
                    direction=result.get("direction", "HOLD"),
                    confidence=result.get("confidence", 0.5),
                    leverage=result.get("leverage", 1),
                    metadata=result
                )
                instance.status = "idle"
                return signal
            
        except asyncio.TimeoutError:
            logger.warning(f"⏱️ 策略超时: {name}@{symbol}")
        except Exception as e:
            logger.error(f"❌ 策略错误: {name}@{symbol}: {e}")
            instance.status = "error"
        
        instance.status = "idle"
        return None
    
    def aggregate_signals(self, signals: List[ParallelSignal]) -> Dict:
        """
        聚合多策略信号
        ==============
        使用加权投票决定最终信号
        """
        if not signals:
            return {"direction": "HOLD", "confidence": 0.0, "leverage": 1}
        
        # 统计投票
        votes = {"LONG": 0.0, "SHORT": 0.0, "HOLD": 0.0}
        total_weight = 0.0
        
        for signal in signals:
            weight = self.strategy_weights.get(signal.strategy_name, 0.2)
            conf_weight = weight * signal.confidence
            votes[signal.direction] += conf_weight
            total_weight += weight
        
        # 归一化
        if total_weight > 0:
            for dir in votes:
                votes[dir] /= total_weight
        
        # 决定最终方向
        max_dir = max(votes, key=votes.get)
        max_conf = votes[max_dir]
        
        # 计算加权平均置信度
        avg_confidence = sum(s.confidence * self.strategy_weights.get(s.strategy_name, 0.2) 
                           for s in signals) / total_weight if total_weight > 0 else 0
        
        return {
            "direction": max_dir,
            "confidence": avg_confidence,
            "votes": votes,
            "signal_count": len(signals),
            "strategies": list(set(s.strategy_name for s in signals))
        }
    
    def get_status(self) -> Dict:
        """获取引擎状态"""
        return {
            "running": self.running,
            "strategies": {
                name: {
                    "enabled": inst.enabled,
                    "status": inst.status,
                    "priority": inst.priority
                }
                for name, inst in self.strategies.items()
            },
            "registered_count": len(self.strategies),
            "active_count": sum(1 for i in self.strategies.values() if i.enabled)
        }


# 全局实例
multi_strategy_engine = MultiStrategyEngine(max_workers=4)


# 注册默认策略
def register_default_strategies():
    """注册北斗七鑫默认策略"""
    
    # MiroFish策略
    def mirofish_strategy(symbol: str, params: Dict) -> Dict:
        # 这里调用MiroFish预测
        return {
            "direction": "HOLD",
            "confidence": 0.5,
            "leverage": 1,
            "strategy": "mirofish"
        }
    
    # 声纳库策略
    def sonar_strategy(symbol: str, params: Dict) -> Dict:
        return {
            "direction": "HOLD", 
            "confidence": 0.5,
            "leverage": 1,
            "strategy": "sonar"
        }
    
    # 专家模式策略
    def expert_strategy(symbol: str, params: Dict) -> Dict:
        return {
            "direction": "HOLD",
            "confidence": 0.5, 
            "leverage": 2,
            "strategy": "expert"
        }
    
    # 注册
    multi_strategy_engine.register_strategy("mirofish", mirofish_strategy, priority=8)
    multi_strategy_engine.register_strategy("sonar", sonar_strategy, priority=7)
    multi_strategy_engine.register_strategy("expert", expert_strategy, priority=6)


if __name__ == "__main__":
    # 测试
    register_default_strategies()
    print("✅ 多策略引擎已初始化")
    print(f"状态: {multi_strategy_engine.get_status()}")
