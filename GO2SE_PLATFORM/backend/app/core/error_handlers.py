#!/usr/bin/env python3
"""
🪿 GO2SE 统一错误处理 v11
标准化API错误响应格式
"""

import logging
import traceback
import time
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, StarletteHTTPException
from pydantic import ValidationError
from typing import Union
from datetime import datetime
from enum import Enum

logger = logging.getLogger("go2se")


class ErrorCode(str, Enum):
    """错误码体系"""
    # 通用错误 (1000-1999)
    UNKNOWN_ERROR = "E1000"
    VALIDATION_ERROR = "E1001"
    INTERNAL_ERROR = "E1002"
    SERVICE_UNAVAILABLE = "E1003"
    TIMEOUT_ERROR = "E1004"
    
    # 认证错误 (2000-2999)
    UNAUTHORIZED = "E2001"
    FORBIDDEN = "E2002"
    INVALID_TOKEN = "E2003"
    API_KEY_INVALID = "E2004"
    
    # 资源错误 (3000-3999)
    NOT_FOUND = "E3001"
    RESOURCE_CONFLICT = "E3002"
    RESOURCE_LIMIT = "E3003"
    
    # 业务错误 (4000-4999)
    RATE_LIMIT_EXCEEDED = "E4001"
    TRADING_ERROR = "E4002"
    INSUFFICIENT_BALANCE = "E4003"
    INVALID_SYMBOL = "E4004"
    EXCHANGE_ERROR = "E4005"
    STRATEGY_ERROR = "E4006"
    
    # 数据错误 (5000-5999)
    DATA_NOT_FOUND = "E5001"
    DATA_INVALID = "E5002"
    CACHE_ERROR = "E5003"


class APIError(Exception):
    """标准API错误"""
    
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        details: dict = None,
        http_status: int = 400
    ):
        self.code = code
        self.message = message
        self.details = details or {}
        self.http_status = http_status
        super().__init__(message)
    
    def to_dict(self) -> dict:
        return {
            "error": {
                "code": self.code.value,
                "message": self.message,
                "details": self.details,
                "timestamp": datetime.utcnow().isoformat(),
            }
        }


class ErrorResponseBuilder:
    """错误响应构建器"""
    
    @staticmethod
    def build(
        code: ErrorCode,
        message: str,
        details: dict = None,
        http_status: int = 400,
        request_id: str = None
    ) -> dict:
        return {
            "error": {
                "code": code.value,
                "message": message,
                "details": details or {},
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": request_id,
            }
        }
    
    @staticmethod
    def from_exception(e: Exception, request_id: str = None) -> tuple[dict, int]:
        """从异常转换为错误响应"""
        if isinstance(e, APIError):
            resp = e.to_dict()
            if request_id:
                resp["error"]["request_id"] = request_id
            return resp, e.http_status
        
        if isinstance(e, RequestValidationError):
            errors = []
            for err in e.errors():
                errors.append({
                    "field": ".".join(str(loc) for loc in err["loc"]),
                    "message": err["msg"],
                    "type": err["type"],
                })
            return ErrorResponseBuilder.build(
                ErrorCode.VALIDATION_ERROR,
                "请求参数验证失败",
                {"validation_errors": errors},
                http_status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                request_id=request_id
            )
        
        if isinstance(e, ValidationError):
            return ErrorResponseBuilder.build(
                ErrorCode.VALIDATION_ERROR,
                "数据模型验证失败",
                {"detail": str(e)},
                http_status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                request_id=request_id
            )
        
        if isinstance(e, StarletteHTTPException):
            code_map = {
                401: ErrorCode.UNAUTHORIZED,
                403: ErrorCode.FORBIDDEN,
                404: ErrorCode.NOT_FOUND,
                429: ErrorCode.RATE_LIMIT_EXCEEDED,
            }
            return ErrorResponseBuilder.build(
                code_map.get(e.status_code, ErrorCode.UNKNOWN_ERROR),
                str(e.detail),
                http_status=e.status_code,
                request_id=request_id
            )
        
        if isinstance(e, TimeoutError):
            return ErrorResponseBuilder.build(
                ErrorCode.TIMEOUT_ERROR,
                "请求超时",
                {"timeout": str(e)},
                http_status=status.HTTP_504_GATEWAY_TIMEOUT,
                request_id=request_id
            )
        
        # 未知错误
        logger.error(f"Unhandled exception: {e}\n{traceback.format_exc()}")
        return ErrorResponseBuilder.build(
            ErrorCode.INTERNAL_ERROR,
            "服务器内部错误",
            {"internal_error": str(e) if logger.level <= logging.DEBUG else "See server logs"},
            http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            request_id=request_id
        )


def generate_request_id() -> str:
    """生成请求ID"""
    import uuid
    return str(uuid.uuid4())[:16]


async def error_handling_middleware(request: Request, call_next):
    """全局错误处理中间件"""
    request_id = request.headers.get("X-Request-ID", generate_request_id())
    start_time = time.time()
    
    try:
        response = await call_next(request)
        
        # 添加响应头
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{(time.time() - start_time)*1000:.2f}ms"
        
        return response
        
    except Exception as e:
        logger.error(f"Unhandled middleware exception: {e}")
        error_resp, http_status = ErrorResponseBuilder.from_exception(e, request_id)
        
        return JSONResponse(
            status_code=http_status,
            content=error_resp,
            headers={
                "X-Request-ID": request_id,
                "X-Response-Time": f"{(time.time() - start_time)*1000:.2f}ms",
            }
        )


def register_error_handlers(app):
    """注册全局错误处理器"""
    
    @app.exception_handler(APIError)
    async def api_error_handler(request: Request, exc: APIError):
        return JSONResponse(
            status_code=exc.http_status,
            content=exc.to_dict()
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        errors = []
        for err in exc.errors():
            errors.append({
                "field": ".".join(str(loc) for loc in err["loc"]),
                "message": err["msg"],
                "type": err["type"],
            })
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponseBuilder.build(
                ErrorCode.VALIDATION_ERROR,
                "请求参数验证失败",
                {"validation_errors": errors}
            )
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        code_map = {
            401: ErrorCode.UNAUTHORIZED,
            403: ErrorCode.FORBIDDEN,
            404: ErrorCode.NOT_FOUND,
            429: ErrorCode.RATE_LIMIT_EXCEEDED,
        }
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponseBuilder.build(
                code_map.get(exc.status_code, ErrorCode.UNKNOWN_ERROR),
                str(exc.detail)
            )
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponseBuilder.build(
                ErrorCode.INTERNAL_ERROR,
                "服务器内部错误"
            )
        )
