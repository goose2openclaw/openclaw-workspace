#!/usr/bin/env python3
"""
🪿 GO2SE 请求验证器 v11
Pydantic模型 + 自定义验证器
"""

from pydantic import BaseModel, Field, field_validator, validator
from typing import Optional, List, Literal
from datetime import datetime
from enum import Enum
import re


class TradingMode(str, Enum):
    DRY_RUN = "dry_run"
    LIVE = "live"
    PAPER = "paper"


class Symbol(str, Enum):
    """支持的交易对"""
    BTC_USDT = "BTC/USDT"
    ETH_USDT = "ETH/USDT"
    SOL_USDT = "SOL/USDT"
    XRP_USDT = "XRP/USDT"
    BNB_USDT = "BNB/USDT"
    ADA_USDT = "ADA/USDT"
    DOGE_USDT = "DOGE/USDT"
    DOT_USDT = "DOT/USDT"
    AVAX_USDT = "AVAX/USDT"
    LINK_USDT = "LINK/USDT"


class StrategyType(str, Enum):
    RABBIT = "rabbit"
    MOLE = "mole"
    ORACLE = "oracle"
    LEADER = "leader"
    HITCHHIKER = "hitchhiker"
    AIRDROP = "airdrop"
    CROWDSOURCE = "crowdsource"


# ─── 交易请求模型 ───────────────────────────────────────────

class TradeRequest(BaseModel):
    """交易请求"""
    symbol: str = Field(..., min_length=3, max_length=20, description="交易对")
    side: Literal["buy", "sell"] = Field(..., description="买卖方向")
    amount: float = Field(..., gt=0, le=1000000, description="数量")
    price: Optional[float] = Field(None, gt=0, description="价格(市价单可不填)")
    strategy_type: Optional[StrategyType] = Field(None, description="策略类型")
    client_order_id: Optional[str] = Field(None, max_length=64, description="客户端订单ID")
    
    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v):
        # 标准化格式
        v = v.upper().strip()
        if "/" not in v:
            # 尝试自动转换 BTCUSDT -> BTC/USDT
            for sep in ["USDT", "BTC", "ETH", "BNB"]:
                if v.endswith(sep) and len(v) > len(sep) + 3:
                    base = v[: -len(sep)]
                    if base:
                        v = f"{base}/{sep}"
                        break
        return v
    
    @field_validator("side")
    @classmethod
    def validate_side(cls, v):
        return v.lower()
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "BTC/USDT",
                "side": "buy",
                "amount": 0.01,
                "price": 50000.0,
                "strategy_type": "rabbit"
            }
        }


class BatchTradeRequest(BaseModel):
    """批量交易请求"""
    trades: List[TradeRequest] = Field(..., min_length=1, max_length=10)
    group_id: Optional[str] = Field(None, max_length=64)
    
    class Config:
        json_schema_extra = {
            "example": {
                "trades": [
                    {"symbol": "BTC/USDT", "side": "buy", "amount": 0.01, "price": 50000}
                ],
                "group_id": "batch_001"
            }
        }


# ─── 策略配置模型 ───────────────────────────────────────────

class StrategyConfig(BaseModel):
    """策略配置"""
    name: str = Field(..., min_length=1, max_length=100)
    strategy_type: StrategyType
    enabled: bool = True
    weight: float = Field(0.0, ge=0.0, le=1.0)
    
    # 风控参数
    max_position: float = Field(0.6, ge=0.0, le=1.0)
    stop_loss: float = Field(0.10, ge=0.0, le=1.0)
    take_profit: float = Field(0.30, ge=0.0, le=10.0)
    
    # 执行参数
    interval_seconds: int = Field(60, ge=10, le=3600)
    min_trade_amount: float = Field(0.001, ge=0)
    
    # 策略特定参数
    params: dict = Field(default_factory=dict)
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not re.match(r'^[\w\-\.]+$', v):
            raise ValueError("名称只能包含字母、数字、下划线和连字符")
        return v


class StrategyUpdateRequest(BaseModel):
    """策略更新请求"""
    enabled: Optional[bool] = None
    weight: Optional[float] = Field(None, ge=0.0, le=1.0)
    max_position: Optional[float] = Field(None, ge=0.0, le=1.0)
    stop_loss: Optional[float] = Field(None, ge=0.0, le=1.0)
    take_profit: Optional[float] = Field(None, ge=0.0, le=10.0)
    interval_seconds: Optional[int] = Field(None, ge=10, le=3600)
    params: Optional[dict] = None


class StrategyReloadRequest(BaseModel):
    """策略热更新请求"""
    strategy_names: Optional[List[str]] = Field(None, description="指定策略名(空=全部)")
    force: bool = Field(False, description="强制重载")


# ─── 回测请求模型 ───────────────────────────────────────────

class BacktestRequest(BaseModel):
    """回测请求"""
    strategy_type: StrategyType
    symbols: List[str] = Field(..., min_length=1, max_length=20)
    
    start_date: datetime
    end_date: datetime
    
    initial_capital: float = Field(10000.0, gt=0)
    commission: float = Field(0.001, ge=0.0, le=0.1)
    slippage: float = Field(0.0005, ge=0.0, le=0.1)
    
    # 策略参数
    params: dict = Field(default_factory=dict)
    
    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, v, info):
        if "start_date" in info.data and v <= info.data["start_date"]:
            raise ValueError("结束日期必须晚于开始日期")
        return v
    
    @field_validator("symbols")
    @classmethod
    def validate_symbols(cls, v):
        seen = set()
        for s in v:
            s_clean = s.upper().strip()
            if s_clean in seen:
                continue  # 去重
            seen.add(s_clean)
        return list(seen)


class BacktestResultQuery(BaseModel):
    """回测结果查询"""
    strategy_type: Optional[StrategyType] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_sharpe: Optional[float] = Field(None, ge=-10, le=10)
    limit: int = Field(50, ge=1, le=500)
    offset: int = Field(0, ge=0)


# ─── 市场数据请求 ───────────────────────────────────────────

class MarketDataRequest(BaseModel):
    """市场数据请求"""
    symbol: str = Field(..., min_length=3, max_length=20)
    exchange: Optional[str] = Field("binance", max_length=20)
    interval: Optional[str] = Field("1m", max_length=10)
    limit: int = Field(100, ge=1, le=1000)
    
    @field_validator("interval")
    @classmethod
    def validate_interval(cls, v):
        valid = ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w"]
        if v not in valid:
            raise ValueError(f"无效周期: {v}, 支持: {valid}")
        return v


class PriceAlertRequest(BaseModel):
    """价格告警请求"""
    symbol: str
    condition: Literal["above", "below", "cross"]
    price: float = Field(..., gt=0)
    callback_url: Optional[str] = Field(None, max_length=500)
    
    @field_validator("callback_url")
    @classmethod
    def validate_url(cls, v):
        if v and not v.startswith(("http://", "https://")):
            raise ValueError("回调URL必须以http://或https://开头")
        return v


# ─── 通用分页模型 ───────────────────────────────────────────

class PaginationParams(BaseModel):
    """分页参数"""
    limit: int = Field(50, ge=1, le=500)
    offset: int = Field(0, ge=0)
    sort_by: Optional[str] = Field(None, max_length=50)
    sort_order: Literal["asc", "desc"] = "desc"
    
    @property
    def page(self) -> int:
        return (self.offset // self.limit) + 1


class HealthCheckResponse(BaseModel):
    """健康检查响应"""
    status: Literal["healthy", "degraded", "unhealthy"]
    version: str
    timestamp: datetime
    signals: dict
    dependencies: dict
    limits: dict
