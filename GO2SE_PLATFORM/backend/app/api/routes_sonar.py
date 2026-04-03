"""
声纳库 API路由
=============
提供趋势模型扫描和信号生成接口
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import math

from app.core.sonar_v2 import (
    SonarLibraryV2, 
    MarketIndicators, 
    SignalType, 
    TrendDirection,
    TrendModelLibrary
)

router = APIRouter(prefix="/api/sonar")

# 全局声纳库实例
_sonar_instance: Optional[SonarLibraryV2] = None

def get_sonar() -> SonarLibraryV2:
    """获取声纳库实例"""
    global _sonar_instance
    if _sonar_instance is None:
        # 优先从JSON加载模型，否则使用内置模型
        db_path = '/root/.openclaw/workspace/skills/go2se/data/trend_database.json'
        try:
            _sonar_instance = SonarLibraryV2(db_path)
        except:
            _sonar_instance = SonarLibraryV2()
    return _sonar_instance


# ==================== 请求/响应模型 ====================

class MarketIndicatorsRequest(BaseModel):
    """市场指标请求"""
    symbol: str = "BTC/USDT"
    close: float = 0.0
    open: float = 0.0
    high: float = 0.0
    low: float = 0.0
    price_change_pct: float = 0.0
    
    # RSI
    rsi: float = 50.0
    rsi_14: float = 50.0
    rsi_7: float = 50.0
    
    # MACD
    macd: float = 0.0
    macd_signal: float = 0.0
    macd_histogram: float = 0.0
    
    # 均线
    sma5: float = 0.0
    sma10: float = 0.0
    sma20: float = 0.0
    sma50: float = 0.0
    sma200: float = 0.0
    ema9: float = 0.0
    ema12: float = 0.0
    ema21: float = 0.0
    ema26: float = 0.0
    
    # 布林带
    bb_upper: float = 0.0
    bb_middle: float = 0.0
    bb_lower: float = 0.0
    bb_width: float = 0.0
    
    # ATR
    atr: float = 0.0
    atr_pct: float = 0.0
    
    # ADX
    adx: float = 0.0
    plus_di: float = 0.0
    minus_di: float = 0.0
    
    # 成交量
    volume: float = 0.0
    volume_ma: float = 0.0
    volume_ratio: float = 1.0
    
    # OBV
    obv: float = 0.0
    obv_ma: float = 0.0
    
    # VWAP
    vwap: float = 0.0
    
    # 其他
    williams_r: float = -50.0
    cci: float = 0.0
    stochastic_k: float = 50.0
    stochastic_d: float = 50.0


class ScanRequest(BaseModel):
    """扫描请求"""
    symbol: str = "BTC/USDT"
    timeframe: str = "15m"
    indicators: Optional[MarketIndicatorsRequest] = None


class MatchResultResponse(BaseModel):
    """匹配结果"""
    model_name: str
    category: str
    match_score: float
    conditions_met: List[str]
    conditions_failed: List[str]
    direction: str
    description: str


class ScanResponse(BaseModel):
    """扫描响应"""
    symbol: str
    timestamp: str
    timeframe: str
    
    # Layer 1 结果
    layer1_candidates: List[str]
    category_signals: Dict[str, float]
    
    # Layer 2 结果
    layer2_matches: List[MatchResultResponse]
    
    # Layer 3 结果
    final_signal: Optional[str] = None
    final_confidence: float = 0.0
    direction: str = "SIDEWAYS"
    triggered_strategy: str = ""
    models_voted: List[str]
    multi_timeframe_confirmed: bool = False


# ==================== API 端点 ====================

@router.get("/status")
async def get_status():
    """获取声纳库状态"""
    sonar = get_sonar()
    stats = sonar.get_statistics()
    return {
        "status": "active",
        "total_models": stats["library"]["total_models"],
        "categories": stats["library"]["categories"],
        "total_scans": stats["total_scans"],
        "signal_distribution": stats["signal_distribution"]
    }


@router.get("/models")
async def get_models(
    category: Optional[str] = Query(None, description="按类别筛选"),
    timeframe: Optional[str] = Query(None, description="按时 timeframe 筛选"),
    min_confidence: Optional[int] = Query(None, description="最低置信度")
):
    """获取趋势模型列表"""
    sonar = get_sonar()
    
    models = []
    
    # 根据条件筛选
    if category:
        for model in sonar.library.get_models_by_category(category):
            if min_confidence and model.confidence < min_confidence:
                continue
            models.append({
                "name": model.name,
                "category": model.category,
                "confidence": model.confidence,
                "timeframes": model.timeframes,
                "indicators": model.indicators,
                "description": model.description,
                "success_rate": model.success_rate,
                "match_count": model.match_count,
                "last_matched": model.last_matched
            })
    elif timeframe:
        for model in sonar.library.get_models_by_timeframe(timeframe):
            if min_confidence and model.confidence < min_confidence:
                continue
            models.append({
                "name": model.name,
                "category": model.category,
                "confidence": model.confidence,
                "timeframes": model.timeframes,
                "indicators": model.indicators,
                "description": model.description,
                "success_rate": model.success_rate,
                "match_count": model.match_count,
                "last_matched": model.last_matched
            })
    else:
        for model in sonar.library.models.values():
            if min_confidence and model.confidence < min_confidence:
                continue
            models.append({
                "name": model.name,
                "category": model.category,
                "confidence": model.confidence,
                "timeframes": model.timeframes,
                "indicators": model.indicators,
                "description": model.description,
                "success_rate": model.success_rate,
                "match_count": model.match_count,
                "last_matched": model.last_matched
            })
    
    return {
        "count": len(models),
        "models": models
    }


@router.get("/models/categories")
async def get_categories():
    """获取所有模型类别"""
    sonar = get_sonar()
    categories = sonar.library.get_categories()
    
    result = []
    for cat in categories:
        models = sonar.library.get_models_by_category(cat)
        result.append({
            "name": cat,
            "count": len(models),
            "avg_confidence": sum(m.confidence for m in models) / len(models) if models else 0,
            "required_indicators": list(sonar.library.category_indicators.get(cat, set()))
        })
    
    return {
        "count": len(result),
        "categories": result
    }


@router.post("/scan", response_model=ScanResponse)
async def scan_market(request: ScanRequest):
    """执行市场扫描"""
    sonar = get_sonar()
    
    # 转换指标
    if request.indicators:
        indicators = MarketIndicators(
            close=request.indicators.close,
            open=request.indicators.open,
            high=request.indicators.high,
            low=request.indicators.low,
            price_change_pct=request.indicators.price_change_pct,
            rsi=request.indicators.rsi,
            rsi_14=request.indicators.rsi_14,
            rsi_7=request.indicators.rsi_7,
            macd=request.indicators.macd,
            macd_signal=request.indicators.macd_signal,
            macd_histogram=request.indicators.macd_histogram,
            sma5=request.indicators.sma5,
            sma10=request.indicators.sma10,
            sma20=request.indicators.sma20,
            sma50=request.indicators.sma50,
            sma200=request.indicators.sma200,
            ema9=request.indicators.ema9,
            ema12=request.indicators.ema12,
            ema21=request.indicators.ema21,
            ema26=request.indicators.ema26,
            bb_upper=request.indicators.bb_upper,
            bb_middle=request.indicators.bb_middle,
            bb_lower=request.indicators.bb_lower,
            bb_width=request.indicators.bb_width,
            atr=request.indicators.atr,
            atr_pct=request.indicators.atr_pct,
            adx=request.indicators.adx,
            plus_di=request.indicators.plus_di,
            minus_di=request.indicators.minus_di,
            volume=request.indicators.volume,
            volume_ma=request.indicators.volume_ma,
            volume_ratio=request.indicators.volume_ratio,
            obv=request.indicators.obv,
            obv_ma=request.indicators.obv_ma,
            vwap=request.indicators.vwap,
            williams_r=request.indicators.williams_r,
            cci=request.indicators.cci,
            stochastic_k=request.indicators.stochastic_k,
            stochastic_d=request.indicators.stochastic_d
        )
    else:
        indicators = None
    
    # 执行扫描
    result = sonar.scan(request.symbol, indicators, request.timeframe)
    
    # 转换响应
    layer2_matches = []
    for match in result.layer2_matches:
        layer2_matches.append(MatchResultResponse(
            model_name=match.model_name,
            category=match.model.category,
            match_score=match.match_score,
            conditions_met=match.conditions_met,
            conditions_failed=match.conditions_failed,
            direction=match.direction.value,
            description=match.model.description
        ))
    
    return ScanResponse(
        symbol=result.symbol,
        timestamp=result.timestamp,
        timeframe=request.timeframe,
        layer1_candidates=result.layer1_candidates,
        category_signals=sonar.scanner.category_signals,
        layer2_matches=layer2_matches,
        final_signal=result.final_signal.value if result.final_signal else None,
        final_confidence=result.final_confidence,
        direction=result.direction.value,
        triggered_strategy=result.triggered_strategy,
        models_voted=result.models_voted,
        multi_timeframe_confirmed=result.multi_timeframe_confirmed
    )


@router.post("/scan/batch")
async def scan_batch(symbols: List[str], timeframe: str = "15m"):
    """批量扫描多个交易对"""
    sonar = get_sonar()
    results = []
    
    for symbol in symbols:
        try:
            result = sonar.scan(symbol, timeframe=timeframe)
            results.append({
                "symbol": symbol,
                "signal": result.final_signal.value if result.final_signal else None,
                "confidence": result.final_confidence,
                "direction": result.direction.value,
                "triggered_strategy": result.triggered_strategy,
                "top_match": result.layer2_matches[0].model_name if result.layer2_matches else None,
                "status": "success"
            })
        except Exception as e:
            results.append({
                "symbol": symbol,
                "status": "error",
                "error": str(e)
            })
    
    return {
        "count": len(results),
        "results": results
    }


@router.get("/history")
async def get_scan_history(limit: int = 50):
    """获取扫描历史"""
    sonar = get_sonar()
    
    history = []
    for result in sonar.scan_history[-limit:]:
        history.append({
            "symbol": result.symbol,
            "timestamp": result.timestamp,
            "signal": result.final_signal.value if result.final_signal else None,
            "confidence": result.final_confidence,
            "direction": result.direction.value,
            "triggered_strategy": result.triggered_strategy,
            "candidates": result.layer1_candidates,
            "match_count": len(result.layer2_matches)
        })
    
    return {
        "count": len(history),
        "history": history
    }


@router.get("/statistics")
async def get_statistics():
    """获取声纳库统计"""
    sonar = get_sonar()
    stats = sonar.get_statistics()
    
    return {
        "library": {
            "total_models": stats["library"]["total_models"],
            "categories": stats["library"]["categories"]
        },
        "scanning": {
            "total_scans": stats["total_scans"],
            "signal_distribution": stats["signal_distribution"]
        }
    }
