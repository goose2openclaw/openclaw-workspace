#!/usr/bin/env python3
"""
⚡ GO2SE 增强缓存层 v11
支持: 内存缓存 + Redis缓存 + 多级缓存 + stale-while-revalidate
"""

import time
import json
import logging
import hashlib
import threading
from typing import Optional, Any, Callable, Dict, Union
from functools import wraps
from datetime import datetime, timedelta
from collections import OrderedDict

logger = logging.getLogger("go2se")

# ─── 简单内存LRU缓存 ───────────────────────────────────────────

class LRUCache:
    """线程安全的LRU缓存"""
    
    def __init__(self, max_size: int = 1000, ttl: int = 60):
        self.max_size = max_size
        self.ttl = ttl
        self._cache: OrderedDict = OrderedDict()
        self._expiry: Dict[str, float] = {}
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None
            
            # 检查过期
            if time.time() > self._expiry.get(key, 0):
                del self._cache[key]
                del self._expiry[key]
                self._misses += 1
                return None
            
            # 移到末尾(LRU)
            self._cache.move_to_end(key)
            self._hits += 1
            return self._cache[key]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        with self._lock:
            # 淘汰最老的项(如果满)
            while len(self._cache) >= self.max_size:
                oldest = next(iter(self._cache))
                del self._cache[oldest]
                del self._expiry[oldest]
            
            self._cache[key] = value
            self._expiry[key] = time.time() + (ttl or self.ttl)
            self._cache.move_to_end(key)
    
    def delete(self, key: str):
        with self._lock:
            self._cache.pop(key, None)
            self._expiry.pop(key, None)
    
    def clear(self):
        with self._lock:
            self._cache.clear()
            self._expiry.clear()
            self._hits = 0
            self._misses = 0
    
    def stats(self) -> Dict:
        with self._lock:
            total = self._hits + self._misses
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": self._hits / total if total > 0 else 0,
            }


# ─── Redis缓存封装 ───────────────────────────────────────────

class RedisCache:
    """Redis缓存封装(当Redis不可用时自动降级)"""
    
    def __init__(self, redis_url: str = None, ttl: int = 60):
        self.redis_url = redis_url or "redis://localhost:6379/0"
        self.ttl = ttl
        self._client = None
        self._available = False
        self._connect()
    
    def _connect(self):
        try:
            import redis
            self._client = redis.from_url(self.redis_url, decode_responses=True)
            self._client.ping()
            self._available = True
            logger.info("  ✓ Redis缓存已连接")
        except Exception as e:
            logger.warning(f"  ⚠ Redis缓存不可用: {e}, 降级到内存缓存")
            self._available = False
    
    def get(self, key: str) -> Optional[Any]:
        if not self._available:
            return None
        try:
            data = self._client.get(key)
            if data:
                return json.loads(data)
        except Exception:
            pass
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        if not self._available:
            return
        try:
            self._client.setex(key, ttl or self.ttl, json.dumps(value))
        except Exception:
            pass
    
    def delete(self, key: str):
        if not self._available:
            return
        try:
            self._client.delete(key)
        except Exception:
            pass
    
    def clear(self):
        if not self._available:
            return
        try:
            self._client.flushdb()
        except Exception:
            pass
    
    def keys(self, pattern: str = "*") -> list:
        if not self._available:
            return []
        try:
            return self._client.keys(pattern)
        except Exception:
            return []
    
    def stats(self) -> Dict:
        if not self._available:
            return {"available": False}
        try:
            info = self._client.info("memory")
            return {
                "available": True,
                "used_memory_mb": info.get("used_memory", 0) / (1024 * 1024),
                "connected_clients": self._client.info("clients").get("connected_clients", 0),
            }
        except Exception:
            return {"available": False}


# ─── 多级缓存管理器 ───────────────────────────────────────────

class MultiLevelCache:
    """多级缓存: L1(内存) -> L2(Redis)"""
    
    def __init__(self, memory_size: int = 1000, redis_url: str = None, default_ttl: int = 60):
        self.l1 = LRUCache(max_size=memory_size, ttl=default_ttl)
        self.l2 = RedisCache(redis_url=redis_url, ttl=default_ttl)
        self.default_ttl = default_ttl
    
    def get(self, key: str, allow_stale: bool = False) -> Optional[Any]:
        """获取缓存值"""
        # L1优先
        value = self.l1.get(key)
        if value is not None:
            return value
        
        # L2次之
        value = self.l2.get(key)
        if value is not None:
            # 回填L1
            self.l1.set(key, value, ttl=self.default_ttl)
            return value
        
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """设置缓存"""
        ttl = ttl or self.default_ttl
        self.l1.set(key, value, ttl=ttl)
        self.l2.set(key, value, ttl=ttl)
    
    def delete(self, key: str):
        """删除缓存"""
        self.l1.delete(key)
        self.l2.delete(key)
    
    def clear(self):
        """清空所有缓存"""
        self.l1.clear()
        self.l2.clear()
    
    def stats(self) -> Dict:
        """获取缓存统计"""
        return {
            "l1_memory": self.l1.stats(),
            "l2_redis": self.l2.stats(),
        }


# ─── 缓存装饰器工厂 ───────────────────────────────────────────

def cached(
    ttl: int = 60,
    key_prefix: str = "",
    allow_stale: bool = False,
    cache_instance: MultiLevelCache = None
):
    """
    缓存装饰器
    
    用法:
        @cached(ttl=30, key_prefix="market")
        async def get_market_data(symbol):
            ...
    """
    def decorator(func: Callable):
        # 判断是否是异步函数
        import asyncio
        is_async = asyncio.iscoroutinefunction(func)
        
        if is_async:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # 构建缓存key
                cache_key = _build_cache_key(key_prefix, func.__name__, args, kwargs)
                
                # 尝试获取缓存
                cache = cache_instance or _global_cache
                cached_value = cache.get(cache_key, allow_stale=allow_stale)
                if cached_value is not None:
                    return cached_value
                
                # 执行函数
                result = await func(*args, **kwargs)
                
                # 缓存结果
                if result is not None:
                    cache.set(cache_key, result, ttl=ttl)
                
                return result
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                cache_key = _build_cache_key(key_prefix, func.__name__, args, kwargs)
                
                cache = cache_instance or _global_cache
                cached_value = cache.get(cache_key, allow_stale=allow_stale)
                if cached_value is not None:
                    return cached_value
                
                result = func(*args, **kwargs)
                
                if result is not None:
                    cache.set(cache_key, result, ttl=ttl)
                
                return result
            return sync_wrapper
    
    return decorator


def _build_cache_key(prefix: str, func_name: str, args: tuple, kwargs: dict) -> str:
    """构建缓存key"""
    parts = []
    if prefix:
        parts.append(prefix)
    parts.append(func_name)
    
    # 序列化参数
    try:
        args_str = json.dumps(args, sort_keys=True, default=str)
        kwargs_str = json.dumps(kwargs, sort_keys=True, default=str)
        key_content = hashlib.md5(f"{args_str}{kwargs_str}".encode()).hexdigest()[:12]
        parts.append(key_content)
    except Exception:
        parts.append(str(args))
    
    return ":".join(parts)


# ─── 预定义缓存实例 ───────────────────────────────────────────

# 全局缓存实例
_global_cache: Optional[MultiLevelCache] = None


def init_cache(redis_url: str = None, memory_size: int = 1000) -> MultiLevelCache:
    """初始化全局缓存"""
    global _global_cache
    _global_cache = MultiLevelCache(
        memory_size=memory_size,
        redis_url=redis_url,
        default_ttl=60
    )
    return _global_cache


def get_cache() -> MultiLevelCache:
    """获取全局缓存实例"""
    global _global_cache
    if _global_cache is None:
        _global_cache = init_cache()
    return _global_cache


# ─── 命名空间缓存工厂 ───────────────────────────────────────────

class NamespacedCache:
    """命名空间缓存"""
    
    def __init__(self, namespace: str, ttl: int = 60):
        self.namespace = f"go2se:{namespace}"
        self.ttl = ttl
        self._local = LRUCache(max_size=500, ttl=ttl)
    
    def _key(self, key: str) -> str:
        return f"{self.namespace}:{key}"
    
    def get(self, key: str) -> Optional[Any]:
        return _global_cache.get(self._key(key)) if _global_cache else self._local.get(key)
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        ttl = ttl or self.ttl
        if _global_cache:
            _global_cache.set(self._key(key), value, ttl=ttl)
        else:
            self._local.set(key, value, ttl=ttl)
    
    def delete(self, key: str):
        if _global_cache:
            _global_cache.delete(self._key(key))
        else:
            self._local.delete(key)
    
    def clear(self):
        if _global_cache:
            for key in _global_cache.l2.keys(f"{self.namespace}:*"):
                _global_cache.l2.delete(key)


# ─── 预定义TTL常量 ───────────────────────────────────────────

class CacheTTL:
    """缓存TTL常量(秒)"""
    # 市场数据 - 快速变化
    PRICE = 5
    TICKER = 10
    ORDERBOOK = 2
    OHLCV = 30
    TRADES = 10
    
    # 策略数据 - 中等变化
    SIGNALS = 60
    POSITIONS = 30
    PORTFOLIO = 60
    
    # 统计数据 - 相对稳定
    STATS = 10
    PERFORMANCE = 60
    BACKTEST = 300
    
    # 配置数据 - 很少变化
    STRATEGIES = 300
    CONFIG = 600
    EXCHANGE_STATUS = 60


# ─── 缓存统计API ───────────────────────────────────────────

def cache_stats() -> Dict:
    """获取缓存统计"""
    cache = get_cache()
    stats = cache.stats()
    
    return {
        "memory_l1": stats["l1_memory"],
        "redis_l2": stats["l2_redis"],
        "total_memory_items": stats["l1_memory"]["size"],
        "hit_rate": stats["l1_memory"]["hit_rate"],
    }


def cache_clear():
    """清空所有缓存"""
    cache = get_cache()
    cache.clear()
    return cache.l1.stats()["size"] + 1
