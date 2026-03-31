#!/usr/bin/env python3
"""
⚡ API速率限制器
================
基于时间窗口的速率限制
"""

import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Optional
from dataclasses import dataclass
import threading


@dataclass
class RateLimitConfig:
    """速率限制配置"""
    requests_per_window: int = 100  # 窗口内最大请求数
    window_seconds: int = 60        # 窗口大小(秒)
    burst_limit: int = 10            # 突发限制


class RateLimiter:
    """令牌桶速率限制器"""
    
    def __init__(self, config: RateLimitConfig = None):
        self.config = config or RateLimitConfig()
        self.buckets: Dict[str, Dict] = defaultdict(self._create_bucket)
        self._lock = threading.Lock()
    
    def _create_bucket(self):
        return {
            "tokens": self.config.requests_per_window,
            "last_update": time.time(),
            "requests": []
        }
    
    def _refill_bucket(self, bucket: Dict) -> None:
        """补充令牌"""
        now = time.time()
        elapsed = now - bucket["last_update"]
        
        # 每秒补充 tokens / window 个令牌
        refill_rate = self.config.requests_per_window / self.config.window_seconds
        new_tokens = elapsed * refill_rate
        
        bucket["tokens"] = min(
            self.config.requests_per_window,
            bucket["tokens"] + new_tokens
        )
        bucket["last_update"] = now
    
    def check_limit(self, key: str) -> tuple[bool, Dict]:
        """
        检查速率限制
        返回: (allowed, info)
        """
        with self._lock:
            bucket = self.buckets[key]
            self._refill_bucket(bucket)
            
            # 清理超过窗口的请求记录
            now = datetime.now()
            bucket["requests"] = [
                t for t in bucket["requests"]
                if now - t < timedelta(seconds=self.config.window_seconds)
            ]
            
            allowed = bucket["tokens"] >= 1
            
            if allowed:
                bucket["tokens"] -= 1
                bucket["requests"].append(now)
            
            info = {
                "allowed": allowed,
                "remaining": int(bucket["tokens"]),
                "reset_at": datetime.fromtimestamp(
                    bucket["last_update"] + self.config.window_seconds
                ).isoformat(),
                "requests_in_window": len(bucket["requests"])
            }
            
            return allowed, info


# API特定限制配置
API_LIMITS = {
    "/api/market": RateLimitConfig(requests_per_window=120, window_seconds=60),      # 市场数据
    "/api/signals": RateLimitConfig(requests_per_window=60, window_seconds=60),       # 信号
    "/api/trade": RateLimitConfig(requests_per_window=30, window_seconds=60),        # 交易
    "/api/expert": RateLimitConfig(requests_per_window=30, window_seconds=60),       # 专家模式
    "default": RateLimitConfig(requests_per_window=100, window_seconds=60),           # 默认
}


class APIRateLimiter:
    """API速率限制管理器"""
    
    def __init__(self):
        self.limiters: Dict[str, RateLimiter] = {
            path: RateLimiter(config)
            for path, config in API_LIMITS.items()
        }
        self.default_limiter = RateLimiter(API_LIMITS["default"])
    
    def check(self, path: str, client_id: str = "default") -> tuple[bool, Dict]:
        """检查API请求是否允许"""
        # 找到匹配的limiter
        limiter = self.default_limiter
        for api_path, lim in self.limiters.items():
            if path.startswith(api_path):
                limiter = lim
                break
        
        key = f"{client_id}:{path}"
        return limiter.check_limit(key)


# 全局实例
rate_limiter = APIRateLimiter()


def rate_limit_middleware(endpoint: str = None):
    """装饰器用于速率限制"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            client_id = kwargs.get("client_id", "default")
            path = endpoint or func.__name__
            
            allowed, info = rate_limiter.check(path, client_id)
            
            if not allowed:
                return {
                    "error": "Rate limit exceeded",
                    "retry_after": info["reset_at"],
                    "limit": info["requests_in_window"]
                }, 429
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


if __name__ == "__main__":
    # 测试
    limiter = rate_limiter
    
    print("=== API速率限制测试 ===")
    
    for i in range(5):
        path = "/api/market/ticker"
        allowed, info = limiter.check(path, "test_client")
        print(f"请求 {i+1}: {'✅ 允许' if allowed else '❌ 拒绝'} | "
              f"剩余: {info['remaining']} | 窗口内请求: {info['requests_in_window']}")
    
    print("\n=== 限制说明 ===")
    print("  /api/market: 120请求/分钟")
    print("  /api/signals: 60请求/分钟")
    print("  /api/trade: 30请求/分钟")
    print("  /api/expert: 30请求/分钟")
    print("  default: 100请求/分钟")
