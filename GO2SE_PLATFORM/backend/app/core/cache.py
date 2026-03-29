"""
⚡ 性能工程师 - Redis缓存层
=======================
减少API调用，提升响应速度

缓存策略:
- 市场数据: TTL 30秒
- 策略列表: TTL 5分钟
- 信号列表: TTL 1分钟
"""

import time
from typing import Optional, Any
from functools import wraps

# 简单内存缓存 (生产环境建议用Redis)
class SimpleCache:
    def __init__(self):
        self._cache = {}
        self._ttl = {}
    
    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            if time.time() < self._ttl.get(key, 0):
                return self._cache[key]
            else:
                del self._cache[key]
                del self._ttl[key]
        return None
    
    def set(self, key: str, value: Any, ttl: int = 60):
        self._cache[key] = value
        self._ttl[key] = time.time() + ttl
    
    def delete(self, key: str):
        self._cache.pop(key, None)
        self._ttl.pop(key, None)
    
    def clear(self):
        self._cache.clear()
        self._ttl.clear()
    
    def stats(self):
        return {
            "keys": len(self._cache),
            "memory_kb": len(str(self._cache)) // 1024
        }


# 全局缓存实例
cache = SimpleCache()


def cached(ttl: int = 60, key_prefix: str = ""):
    """缓存装饰器"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            result = await func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
        
        # 根据函数类型返回对应包装器
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


# 预定义的缓存TTL常量
TTL = {
    "market_data": 30,      # 30秒 - 市场数据快速变化
    "signals": 60,          # 1分钟 - 信号相对稳定
    "strategies": 300,      # 5分钟 - 策略列表很少变化
    "portfolio": 60,        # 1分钟 - 持仓变动
    "stats": 10,            # 10秒 - 统计数据
}
