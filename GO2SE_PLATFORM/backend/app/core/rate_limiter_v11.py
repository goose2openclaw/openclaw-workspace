#!/usr/bin/env python3
"""
⚡ API速率限制器 v11
支持: 时间窗口 + 令牌桶 + 突发限制 + 路径限流
"""

import time
import threading
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger("go2se")


class RateLimitTier(str, Enum):
    """限流层级"""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


@dataclass
class RateLimitConfig:
    """速率限制配置"""
    requests_per_window: int = 100
    window_seconds: int = 60
    burst_limit: int = 10
    tier: RateLimitTier = RateLimitTier.FREE


# API特定限制配置 - v11增强
API_RATE_LIMITS: Dict[str, RateLimitConfig] = {
    # 公共端点 - 宽松限制
    "/api/ping": RateLimitConfig(requests_per_window=300, window_seconds=60, tier=RateLimitTier.FREE),
    "/api/health": RateLimitConfig(requests_per_window=120, window_seconds=60, tier=RateLimitTier.FREE),
    "/api/stats": RateLimitConfig(requests_per_window=60, window_seconds=60, tier=RateLimitTier.BASIC),
    
    # 市场数据 - 中等限制
    "/api/market": RateLimitConfig(requests_per_window=300, window_seconds=60, tier=RateLimitTier.BASIC),
    "/api/oracle": RateLimitConfig(requests_per_window=120, window_seconds=60, tier=RateLimitTier.BASIC),
    
    # 信号 - 严格限制
    "/api/signals": RateLimitConfig(requests_per_window=60, window_seconds=60, tier=RateLimitTier.PREMIUM),
    "/api/backtest": RateLimitConfig(requests_per_window=30, window_seconds=60, tier=RateLimitTier.PREMIUM),
    
    # 交易 - 最严格
    "/api/trade": RateLimitConfig(requests_per_window=30, window_seconds=60, tier=RateLimitTier.ENTERPRISE),
    "/api/order": RateLimitConfig(requests_per_window=30, window_seconds=60, tier=RateLimitTier.ENTERPRISE),
    "/api/strategy": RateLimitConfig(requests_per_window=60, window_seconds=60, tier=RateLimitTier.PREMIUM),
    
    # 默认
    "default": RateLimitConfig(requests_per_window=100, window_seconds=60, tier=RateLimitTier.FREE),
}


class TokenBucket:
    """令牌桶实现"""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.tokens = float(config.requests_per_window)
        self.last_refill = time.time()
        self.requests: list = []  # 时间窗口内的请求记录
        self.lock = threading.Lock()
    
    def _refill(self):
        """补充令牌"""
        now = time.time()
        elapsed = now - self.last_refill
        
        # 根据时间流逝补充令牌
        refill_rate = self.config.requests_per_window / self.config.window_seconds
        new_tokens = elapsed * refill_rate
        
        self.tokens = min(
            float(self.config.requests_per_window),
            self.tokens + new_tokens
        )
        self.last_refill = now
    
    def consume(self, tokens: int = 1) -> Tuple[bool, Dict]:
        """尝试消费令牌"""
        with self.lock:
            self._refill()
            
            now = datetime.now()
            
            # 清理超过窗口的请求记录
            self.requests = [
                t for t in self.requests
                if now - t < timedelta(seconds=self.config.window_seconds)
            ]
            
            # 检查是否允许
            allowed = self.tokens >= tokens
            request_count = len(self.requests) + 1
            
            # 额外检查: 突发限制
            burst_ok = request_count <= self.config.burst_limit * (self.config.window_seconds / 60)
            
            if allowed and burst_ok:
                self.tokens -= tokens
                self.requests.append(now)
            
            remaining = max(0, int(self.tokens))
            reset_at = datetime.fromtimestamp(
                self.last_refill + self.config.window_seconds
            )
            
            return allowed and burst_ok, {
                "allowed": allowed and burst_ok,
                "remaining": remaining,
                "reset_at": reset_at.isoformat(),
                "limit": self.config.requests_per_window,
                "requests_in_window": request_count,
                "burst_limit": self.config.burst_limit,
                "tier": self.config.tier.value,
            }


class RateLimiter:
    """多层级速率限制器"""
    
    def __init__(self):
        self.buckets: Dict[str, TokenBucket] = {}
        self._lock = threading.Lock()
        self.default_config = API_RATE_LIMITS["default"]
    
    def _get_config(self, path: str) -> RateLimitConfig:
        """获取路径对应的限流配置"""
        # 精确匹配优先
        if path in API_RATE_LIMITS:
            return API_RATE_LIMITS[path]
        
        # 前缀匹配
        for api_path, config in API_RATE_LIMITS.items():
            if api_path != "default" and path.startswith(api_path):
                return config
        
        return self.default_config
    
    def _get_bucket(self, key: str, config: RateLimitConfig) -> TokenBucket:
        """获取或创建bucket"""
        with self._lock:
            if key not in self.buckets:
                self.buckets[key] = TokenBucket(config)
            return self.buckets[key]
    
    def check(self, path: str, client_id: str = "anonymous") -> Tuple[bool, Dict]:
        """
        检查速率限制
        返回: (allowed, info_dict)
        """
        config = self._get_config(path)
        key = f"{client_id}:{path}"
        
        bucket = self._get_bucket(key, config)
        return bucket.consume()


class RateLimitMiddleware:
    """速率限制中间件封装"""
    
    def __init__(self, limiter: RateLimiter):
        self.limiter = limiter
        self._client_cache: Dict[str, str] = {}  # 请求IP -> 客户端ID
    
    def get_client_id(self, request) -> str:
        """从请求中提取客户端标识"""
        # 优先使用API Key
        api_key = request.headers.get("X-API-Key", "")
        if api_key:
            return f"api_key:{api_key[:16]}"
        
        # 然后使用用户ID
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"
        
        # 最后使用IP
        ip = request.headers.get("x-forwarded-for", "")
        if not ip:
            ip = request.headers.get("x-real-ip", "unknown")
        # 取第一个IP (多级代理)
        if "," in ip:
            ip = ip.split(",")[0].strip()
        
        return f"ip:{ip}"
    
    def get_tier(self, client_id: str) -> RateLimitTier:
        """根据客户端ID确定限流层级"""
        if client_id.startswith("api_key:"):
            return RateLimitTier.PREMIUM
        if client_id.startswith("user:"):
            return RateLimitTier.BASIC
        return RateLimitTier.FREE
    
    async def check_request(self, request) -> Tuple[bool, Dict]:
        """检查请求是否允许"""
        path = request.url.path
        client_id = self.get_client_id(request)
        
        return self.limiter.check(path, client_id)


# 全局限流器实例
rate_limiter = RateLimiter()
rate_limit_middleware = RateLimitMiddleware(rate_limiter)


def rate_limit(
    requests_per_window: int = 100,
    window_seconds: int = 60,
    burst_limit: int = 10
):
    """速率限制装饰器"""
    config = RateLimitConfig(
        requests_per_window=requests_per_window,
        window_seconds=window_seconds,
        burst_limit=burst_limit
    )
    
    def decorator(func):
        async def wrapper(*args, **kwargs):
            from fastapi import HTTPException
            key = f"decorator:{func.__name__}"
            bucket = rate_limiter._get_bucket(key, config)
            allowed, info = bucket.consume()
            
            if not allowed:
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "Rate limit exceeded",
                        "retry_after": info["reset_at"],
                        "limit": info["limit"],
                        "remaining": info["remaining"],
                    },
                    headers={
                        "X-RateLimit-Remaining": str(info["remaining"]),
                        "X-RateLimit-Limit": str(info["limit"]),
                        "X-RateLimit-Reset": info["reset_at"],
                        "Retry-After": str(window_seconds),
                    }
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# ─── 全局状态统计 ───────────────────────────────────────────

class RateLimitStats:
    """速率限制统计"""
    
    def __init__(self):
        self.total_requests = 0
        self.blocked_requests = 0
        self.by_path: Dict[str, Dict] = defaultdict(lambda: {"total": 0, "blocked": 0})
        self._lock = threading.Lock()
    
    def record(self, path: str, allowed: bool):
        with self._lock:
            self.total_requests += 1
            if not allowed:
                self.blocked_requests += 1
            self.by_path[path]["total"] += 1
            if not allowed:
                self.by_path[path]["blocked"] += 1
    
    def get_stats(self) -> Dict:
        with self._lock:
            return {
                "total_requests": self.total_requests,
                "blocked_requests": self.blocked_requests,
                "block_rate": self.blocked_requests / max(self.total_requests, 1),
                "by_path": dict(self.by_path),
            }


rate_limit_stats = RateLimitStats()
