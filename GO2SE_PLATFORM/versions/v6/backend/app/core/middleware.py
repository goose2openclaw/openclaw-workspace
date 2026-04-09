#!/usr/bin/env python3
"""
🪿 GO2SE 中间件层
统一请求/响应处理、日志、错误捕获
"""

import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger("go2se")


class LoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # 请求日志
        logger.info(f"📥 {request.method} {request.url.path}")
        
        # 处理请求
        response = await call_next(request)
        
        # 响应日志
        process_time = (time.time() - start_time) * 1000
        logger.info(
            f"📤 {request.method} {request.url.path} "
            f"- {response.status_code} ({process_time:.1f}ms)"
        )
        
        # 添加响应头
        response.headers["X-Process-Time"] = str(process_time)
        
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """统一错误处理中间件"""
    
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            logger.error(f"❌ 异常: {request.url.path} - {str(e)}")
            return Response(
                content=f'{{"error": "{str(e)}"}}',
                status_code=500,
                media_type="application/json"
            )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """简单限流中间件 (生产环境建议用Redis)"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.request_counts = {}
        self.window = 60  # 60秒窗口
        self.max_requests = 100  # 最大请求数
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # 清理过期记录
        self.request_counts = {
            k: v for k, v in self.request_counts.items()
            if current_time - v["time"] < self.window
        }
        
        # 检查限流
        if client_ip in self.request_counts:
            if current_time - self.request_counts[client_ip]["time"] < self.window:
                self.request_counts[client_ip]["count"] += 1
                if self.request_counts[client_ip]["count"] > self.max_requests:
                    logger.warning(f"🚫 限流: {client_ip}")
                    return Response(
                        content='{"error": "Rate limit exceeded"}',
                        status_code=429,
                        media_type="application/json"
                    )
            else:
                self.request_counts[client_ip] = {"time": current_time, "count": 1}
        else:
            self.request_counts[client_ip] = {"time": current_time, "count": 1}
        
        return await call_next(request)
