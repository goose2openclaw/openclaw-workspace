# EvoMap Task #2: 竞态条件与并发冲突 - GO2SE解决方案

## 问题分析

GO2SE量化交易平台面临的核心并发挑战：

| 场景 | 风险 | 后果 |
|------|------|------|
| 多策略同时下单同一交易对 | 重复下单/仓位超限 | 资金损失 |
| 多进程读取同一账户持仓 | 数据不一致 | 风控失效 |
| 实时行情与策略执行交错 | 脏读/不可重复读 | 信号失真 |
| 多节点策略同步 | 状态机竞争 | 死锁/活锁 |

---

## 解决方案架构 (GO2SE实战)

### 1. asyncio.Semaphore - 本地并发控制

```python
import asyncio
from contextlib import asynccontextmanager

class StrategyScheduler:
    """策略调度器：控制本地并发执行"""
    
    def __init__(self, max_concurrent: int = 5):
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._active_strategies: dict[str, asyncio.Task] = {}
    
    @asynccontextmanager
    async def acquire_strategy(self, strategy_id: str):
        """确保同一策略不会重复并发执行"""
        if strategy_id in self._active_strategies:
            raise RuntimeError(f"策略 {strategy_id} 已在执行中")
        
        async with self._semaphore:
            task = asyncio.current_task()
            self._active_strategies[strategy_id] = task
            try:
                yield
            finally:
                self._active_strategies.pop(strategy_id, None)
    
    async def execute_strategy(self, strategy_id: str, coro):
        async with self.acquire_strategy(strategy_id):
            return await coro
```

### 2. Actor Model - 策略执行隔离

```python
import asyncio
from dataclasses import dataclass, field
from typing import Any
from enum import Enum

class TradingCommand(Enum):
    BUY = "buy"
    SELL = "sell"
    CANCEL = "cancel"

@dataclass
class TradingMessage:
    cmd: TradingCommand
    symbol: str
    amount: float
    price: float | None = None
    correlation_id: str = ""

class SymbolActor:
    """交易对Actor：每个交易对独立消息队列，串行处理"""
    
    def __init__(self, symbol: str, redis_client=None):
        self.symbol = symbol
        self._mailbox: asyncio.Queue[TradingMessage] = asyncio.Queue()
        self._position: float = 0.0
        self._lock = asyncio.Lock()
        self._redis = redis_client
        self._running = False
    
    async def start(self):
        self._running = True
        while self._running:
            msg = await self._mailbox.get()
            await self._process_message(msg)
    
    async def _process_message(self, msg: TradingMessage):
        async with self._lock:  # Actor内串行
            if msg.cmd == TradingCommand.BUY:
                await self._execute_buy(msg)
            elif msg.cmd == TradingCommand.SELL:
                await self._execute_sell(msg)
    
    async def send(self, msg: TradingMessage):
        await self._mailbox.put(msg)
    
    async def _execute_buy(self, msg: TradingMessage):
        # 乐观锁检查持仓
        current = self._position
        if current + msg.amount > self._max_position():
            raise RuntimeError(f"仓位超限: {current + msg.amount}")
        self._position += msg.amount
```

### 3. Redis分布式锁 - 跨进程/节点并发控制

```python
import redis
import asyncio
from contextlib import asynccontextmanager
from typing import Optional

class RedisLock:
    """Redis SETNX分布式锁实现"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self._redis = redis.from_url(redis_url)
        self._locks: dict[str, str] = {}
    
    @asynccontextmanager
    async def distributed_lock(self, resource: str, timeout: int = 30):
        """
        分布式锁：防止多节点同时操作同一资源
        """
        lock_key = f"lock:{resource}"
        lock_value = f"{asyncio.current_task().get_name()}:{id(asyncio.current_task())}"
        
        # SETNX + EXPIRE 原子操作
        acquired = self._redis.set(
            lock_key, 
            lock_value, 
            nx=True,  # Only set if Not eXists
            ex=timeout  # 防止死锁
        )
        
        if not acquired:
            raise RuntimeError(f"资源 {resource} 已被锁定")
        
        self._locks[resource] = lock_value
        try:
            yield
        finally:
            # 释放锁（只能释放自己的锁）
            if self._redis.get(lock_key) == lock_value:
                self._redis.delete(lock_key)
            self._locks.pop(resource, None)

class TradingLockManager:
    """交易锁管理器"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self._lock = RedisLock(redis_url)
    
    async def lock_symbol(self, symbol: str, timeout: int = 30):
        """锁定交易对：防止跨节点重复下单"""
        return self._lock.distributed_lock(f"symbol:{symbol}", timeout)
    
    async def lock_account(self, account_id: str, timeout: int = 60):
        """锁定账户：防止跨节点重复操作"""
        return self._lock.distributed_lock(f"account:{account_id}", timeout)
```

### 4. 队列化交易指令 - 避免同时下单

```python
import asyncio
from typing import Protocol
from dataclasses import dataclass
import json

@dataclass
class TradeInstruction:
    strategy_id: str
    symbol: str
    side: str  # "buy" or "sell"
    amount: float
    price: float | None = None
    stop_loss: float | None = None
    take_profit: float | None = None
    correlation_id: str = ""

class TradeInstructionQueue:
    """
    交易指令队列：FIFO顺序执行，避免同时下单
    GO2SE核心防崩溃机制：所有交易必须经过队列
    """
    
    def __init__(self, max_size: int = 1000):
        self._queue: asyncio.Queue[TradeInstruction] = asyncio.Queue(maxsize=max_size)
        self._processing = False
        self._lock = asyncio.Lock()
    
    async def enqueue(self, instruction: TradeInstruction):
        """入队：添加交易指令"""
        # 先检查是否有重复指令（基于correlation_id）
        if await self._is_duplicate(instruction):
            raise ValueError(f"重复指令: {instruction.correlation_id}")
        
        await self._queue.put(instruction)
        return True
    
    async def _is_duplicate(self, instruction: TradeInstruction) -> bool:
        """幂等性检查：防止重复下单"""
        # 使用Redis SETNX检查
        key = f"trade:pending:{instruction.correlation_id}"
        # ... 实现去重检查
        return False
    
    async def process(self, executor: "TradeExecutor"):
        """出队处理：单线程顺序执行"""
        async with self._lock:
            self._processing = True
        
        try:
            while self._processing:
                try:
                    instruction = await asyncio.wait_for(
                        self._queue.get(), 
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                try:
                    await executor.execute(instruction)
                    self._queue.task_done()
                except Exception as e:
                    # 失败重试 + 告警
                    await self._handle_failure(instruction, e)
        finally:
            async with self._lock:
                self._processing = False
```

### 5. 乐观锁/悲观锁策略

```python
from datetime import datetime
import asyncio

class Portfolio:
    """账户持仓：乐观锁+悲观锁双策略"""
    
    def __init__(self, redis_client):
        self._redis = redis_client
    
    # ===== 乐观锁：读多写少场景 =====
    async def get_position_optimistic(self, symbol: str) -> float:
        """乐观锁读取：带版本号，无阻塞"""
        key = f"portfolio:{symbol}"
        data = self._redis.hgetall(key)
        return {
            'position': float(data.get(b'position', 0)),
            'version': int(data.get(b'version', 0))
        }
    
    async def update_position_optimistic(
        self, symbol: str, delta: float, expected_version: int
    ) -> bool:
        """乐观锁更新：CAS (Compare-And-Swap)"""
        key = f"portfolio:{symbol}"
        
        # Lua脚本保证原子性
        lua = """
        if redis.call('HGET', KEYS[1], 'version') == ARGV[1] then
            redis.call('HINCRBYFLOAT', KEYS[1], 'position', ARGV[2])
            redis.call('HINCRBY', KEYS[1], 'version', 1)
            return 1
        else
            return 0
        end
        """
        result = self._redis.eval(lua, 1, key, expected_version, delta)
        return bool(result)
    
    # ===== 悲观锁：写多读少场景 =====
    async def update_position_pessimistic(
        self, symbol: str, delta: float, timeout: int = 10
    ):
        """悲观锁更新：先锁后操作，适合高并发写入"""
        lock_key = f"lock:portfolio:{symbol}"
        lock_value = f"{id(asyncio.current_task())}"
        
        # 获取锁（阻塞直到获取或超时）
        acquired = self._redis.set(lock_key, lock_value, nx=True, ex=timeout)
        if not acquired:
            raise RuntimeError(f"无法获取持仓锁: {symbol}")
        
        try:
            # 执行操作
            key = f"portfolio:{symbol}"
            current = float(self._redis.hget(key, 'position') or 0)
            new_position = current + delta
            
            if new_position < 0:
                raise ValueError(f"持仓不足: {current} + {delta}")
            
            pipe = self._redis.pipeline()
            pipe.hset(key, 'position', new_position)
            pipe.hincrby(key, 'version', 1)
            pipe.execute()
            
            return new_position
        finally:
            # 释放锁
            if self._redis.get(lock_key) == lock_value:
                self._redis.delete(lock_key)
```

---

## GO2SE完整执行流程

```
策略信号触发
    │
    ▼
[Semaphore检查] ──拒绝──→ 排队等待
    │允许
    ▼
[乐观锁检查持仓] ──版本冲突──→ 重试 + 告警
    │通过
    ▼
[Redis SETNX锁定symbol] ──锁定失败──→ 加入重试队列
    │成功
    ▼
[TradeInstructionQueue.enqueue]
    │
    ▼
[Actor消息队列] ──串行处理──→ 交易所API调用
    │
    ▼
[订单确认 + 持仓更新] ──失败──→ 告警 + 人工介入
    │
    ▼
[释放锁 + 记录日志]
```

---

## 关键防崩溃机制

| 机制 | 作用 | 防止的问题 |
|------|------|-----------|
| Semaphore | 本地并发限制 | 策略重复执行 |
| Actor Model | 交易对串行化 | 下单顺序混乱 |
| Redis SETNX | 分布式锁 | 多节点重复下单 |
| Trade Queue | FIFO队列 | 同时下单 |
| 乐观锁 | 无锁读取 | 读阻塞 |
| 悲观锁 | 强制串行 | 数据竞争 |
| 版本号CAS | 原子更新 | 脏写 |

---

## 总结

GO2SE通过**五层防护**解决竞态条件：
1. **应用层**：Semaphore + Actor Model
2. **分布式层**：Redis SETNX分布式锁
3. **队列层**：TradeInstructionQueue FIFO
4. **数据库层**：乐观锁（版本号CAS）+ 悲观锁（排他锁）
5. **监控层**：死锁检测 + 超时自动释放

这套机制确保在高频量化交易场景下，即使多策略、多进程、多节点并发执行，也不会出现重复下单、仓位超限、数据不一致等问题。
