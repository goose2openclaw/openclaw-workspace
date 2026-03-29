# 外部API平滑升级方案 - GO2SE API抽象层设计

## 任务: 外部API平滑升级 (task_id: cmc0f914e47589adfb2823084)

---

## 1. 背景与目标

GO2SE交易平台需要支持多个交易所(Binance/OKX/Bybit)的API接口。关键挑战：
- API版本升级时不能中断交易
- 多交易所API差异需要统一抽象
- 需要降级策略和自动切换机制

---

## 2. API统一接口设计

### 2.1 抽象接口层 (TradingAPI)

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from enum import Enum
import asyncio

class APIStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"

class APIVersion(Enum):
    BINANCE_V3 = "binance_v3"
    BINANCE_V4 = "binance_v4"
    OKX_V5 = "okx_v5"
    BYBIT_V5 = "bybit_v5"

class TradingAPI(ABC):
    """统一交易API接口"""
    
    @abstractmethod
    async def get_balance(self) -> Dict[str, Any]:
        """获取账户余额"""
        pass
    
    @abstractmethod
    async def place_order(self, symbol: str, side: str, quantity: float, 
                          order_type: str = "MARKET") -> Dict[str, Any]:
        """下单"""
        pass
    
    @abstractmethod
    async def get_order(self, order_id: str) -> Dict[str, Any]:
        """查询订单状态"""
        pass
    
    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        """取消订单"""
        pass
    
    @abstractmethod
    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """获取行情"""
        pass
    
    @abstractmethod
    async def health_check(self) -> APIStatus:
        """健康检查"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> APIVersion:
        """API版本"""
        pass
```

### 2.2 具体实现适配器

```python
class BinanceAdapter(TradingAPI):
    """Binance API适配器"""
    
    def __init__(self, api_key: str, api_secret: str, version: APIVersion = APIVersion.BINANCE_V3):
        self.client = BinanceClient(api_key, api_secret)
        self._version = version
        self.endpoints = {
            APIVersion.BINANCE_V3: "https://api.binance.com",
            APIVersion.BINANCE_V4: "https://api.binance.com/v4"
        }
        self.base_url = self.endpoints[version]
    
    @property
    def version(self) -> APIVersion:
        return self._version
    
    async def health_check(self) -> APIStatus:
        try:
            resp = await self.client.get("/api/v3/ping")
            return APIStatus.HEALTHY if resp.status == 200 else APIStatus.DEGRADED
        except Exception:
            return APIStatus.FAILED
    
    async def get_balance(self) -> Dict[str, Any]:
        return await self.client.get("/api/v3/account")
```

---

## 3. API版本管理

### 3.1 版本映射表

```python
VERSION_MAP = {
    "binance": {
        "v3": {"status": "deprecated", "eol": "2025-12-31"},
        "v4": {"status": "stable", "eol": None},
        "v5": {"status": "beta", "eol": None}
    },
    "okx": {
        "v5": {"status": "stable", "eol": None}
    },
    "bybit": {
        "v5": {"status": "stable", "eol": None}
    }
}

def get_latest_stable(exchange: str) -> str:
    """获取最新稳定版本"""
    versions = VERSION_MAP.get(exchange, {})
    for v, info in sorted(versions.items(), reverse=True):
        if info["status"] == "stable":
            return v
    return list(versions.keys())[0]
```

### 3.2 版本自动升级策略

```python
class APIVersionManager:
    """API版本管理器"""
    
    def __init__(self):
        self.exchange_versions: Dict[str, Dict[str, Any]] = {}
        self.upgrade_policies: Dict[str, UpgradePolicy] = {}
    
    def register_exchange(self, exchange: str, adapter: TradingAPI):
        self.exchange_versions[exchange] = {
            "adapter": adapter,
            "current_version": adapter.version,
            "upgrade_candidates": []
        }
    
    async def auto_upgrade(self, exchange: str, target_version: str = None):
        """平滑自动升级"""
        current = self.exchange_versions[exchange]
        target = target_version or get_latest_stable(exchange)
        
        # 1. 并行部署新版本
        new_adapter = await self._deploy_parallel(exchange, target)
        
        # 2. 流量逐步切换 (5% -> 25% -> 50% -> 100%)
        for ratio in [0.05, 0.25, 0.50, 1.0]:
            await self._shift_traffic(exchange, new_adapter, ratio)
            await asyncio.sleep(60)  # 观察窗口
            if not await self._validate_health(exchange, new_adapter):
                await self._rollback(exchange)
                return False
        
        # 3. 关闭旧版本
        await self._deprecate_old(exchange)
        return True
```

---

## 4. 降级策略

### 4.1 降级触发条件

```python
class DegradationTrigger(Enum):
    LATENCY_HIGH = "latency_ms > 5000"
    ERROR_RATE_HIGH = "error_rate > 0.05"
    RATE_LIMIT_HIT = "rate_limit_count > 0"
    TIMEOUT_FREQUENT = "timeout_count > 10/min"
    VERSION_DEPRECATED = "version_eol_reached"

class DegradationPolicy:
    TRIGGERS = {
        DegradationTrigger.LATENCY_HIGH: {"threshold": 5000, "window": 60},
        DegradationTrigger.ERROR_RATE_HIGH: {"threshold": 0.05, "window": 300},
        DegradationTrigger.RATE_LIMIT_HIT: {"threshold": 1, "window": 60},
    }
    
    DEGRADATION_STEPS = [
        {"level": 1, "action": "降低请求频率 50%"},
        {"level": 2, "action": "切换到备用API版本"},
        {"level": 3, "action": "切换到备用交易所"},
        {"level": 4, "action": "只读模式(关闭开仓)"}
    ]
```

### 4.2 自动降级执行器

```python
class CircuitBreaker:
    """熔断器实现"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    async def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise CircuitOpenError("Circuit is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
            raise
```

---

## 5. 健康检查 + 自动切换

### 5.1 健康检查机制

```python
class HealthChecker:
    """多维度健康检查"""
    
    def __init__(self, check_interval: int = 30):
        self.check_interval = check_interval
        self.endpoints: Dict[str, TradingAPI] = {}
        self.results: Dict[str, HealthResult] = {}
    
    async def check_single(self, name: str, api: TradingAPI) -> HealthResult:
        start = time.time()
        try:
            status = await asyncio.wait_for(
                api.health_check(), 
                timeout=5.0
            )
            latency = time.time() - start
            
            return HealthResult(
                name=name,
                status=status,
                latency_ms=latency * 1000,
                timestamp=datetime.now(),
                details={}
            )
        except asyncio.TimeoutError:
            return HealthResult(name=name, status=APIStatus.FAILED, 
                              latency_ms=5000, error="timeout")
        except Exception as e:
            return HealthResult(name=name, status=APIStatus.FAILED,
                              latency_ms=0, error=str(e))
    
    async def check_all(self) -> Dict[str, HealthResult]:
        tasks = [
            self.check_single(name, api) 
            for name, api in self.endpoints.items()
        ]
        results = await asyncio.gather(*tasks)
        return {r.name: r for r in results}
    
    async def continuous_monitor(self):
        """持续监控"""
        while True:
            results = await self.check_all()
            self.results = results
            await self._evaluate_and_act(results)
            await asyncio.sleep(self.check_interval)
```

### 5.2 自动切换策略

```python
class APIFailoverManager:
    """API故障自动切换管理器"""
    
    def __init__(self):
        self.primary: str = None
        self.backups: List[str] = []
        self.current: str = None
        self.health_checker = HealthChecker()
        self.switch_history: List[SwitchEvent] = []
    
    def register(self, name: str, api: TradingAPI, priority: int = 0):
        """注册API端点"""
        self.health_checker.endpoints[name] = api
        if priority == 0:
            self.primary = name
        else:
            self.backups.append((priority, name))
        self.backups.sort()
        if not self.current:
            self.current = self.primary
    
    async def _should_switch(self, results: Dict[str, HealthResult]) -> bool:
        """判断是否需要切换"""
        current_result = results.get(self.current)
        if not current_result:
            return True
        if current_result.status == APIStatus.FAILED:
            return True
        if current_result.latency_ms > 5000:
            return True
        return False
    
    async def _do_switch(self, new_api: str):
        """执行切换"""
        old_api = self.current
        self.current = new_api
        
        self.switch_history.append(SwitchEvent(
            timestamp=datetime.now(),
            from_api=old_api,
            to_api=new_api,
            reason="health_check_failed"
        ))
        
        # 通知
        await self._notify_switch(old_api, new_api)
    
    async def _notify_switch(self, old: str, new: str):
        """切换通知"""
        logger.warning(f"API切换: {old} -> {new}")
        # 发送告警
```

---

## 6. 完整集成示例

```python
class GO2SETRadingEngine:
    """GO2SE交易引擎 - 完整API抽象层"""
    
    def __init__(self):
        # 初始化各交易所适配器
        self.binance = BinanceAdapter(...)
        self.okx = OKXAdapter(...)
        self.bybit = BybitAdapter(...)
        
        # 版本管理器
        self.version_manager = APIVersionManager()
        self.version_manager.register_exchange("binance", self.binance)
        self.version_manager.register_exchange("okx", self.okx)
        self.version_manager.register_exchange("bybit", self.bybit)
        
        # 熔断器
        self.breakers = {
            "binance": CircuitBreaker(),
            "okx": CircuitBreaker(),
            "bybit": CircuitBreaker()
        }
        
        # 健康检查
        self.health_monitor = HealthChecker()
        for name, api in [("binance", self.binance), ("okx", self.okx), 
                           ("bybit", self.bybit)]:
            self.health_monitor.endpoints[name] = api
        
        # 故障切换
        self.failover = APIFailoverManager()
        self.failover.register("binance", self.binance, priority=1)
        self.failover.register("okx", self.okx, priority=2)
        self.failover.register("bybit", self.bybit, priority=3)
    
    async def trade(self, symbol: str, side: str, quantity: float):
        """交易入口 - 自动故障切换"""
        api = self.failover.current
        breaker = self.breakers[api]
        
        try:
            async with breaker:
                result = await self._place_order(api, symbol, side, quantity)
                return result
        except CircuitOpenError:
            # 触发切换
            await self.failover.switch_to_backup(api)
            return await self.trade(symbol, side, quantity)
```

---

## 7. 升级检查清单

| 检查项 | 说明 | 阈值 |
|--------|------|------|
| 并行运行 | 新旧API同时运行，观察差异 | 24h |
| 流量切换 | 逐步放量 (5%→25%→50%→100%) | 无报错 |
| 错误率 | 新API错误率不应高于旧API | <1% |
| 延迟 | 新API延迟不应显著增加 | P99<2s |
| 日志审计 | 记录所有API调用差异 | 持续 |
| 回滚计划 | 确认切换开关可用 | 演练通过 |

---

## 8. 核心原则

1. **永不中断交易**: 任何升级都需要平行运行期
2. **可观测性**: 详细的日志、指标、追踪
3. **快速回滚**: 切换开关随时可用，30秒内回滚
4. **渐进式**: 5% → 25% → 50% → 100% 流量切换
5. **多层防护**: 熔断 + 降级 + 故障切换三重保障
