#!/usr/bin/env python3
"""
🪿 GO2SE History & Analytics API - L5/L6 支持
=============================================
为6级导航提供历史记录和数据分析API

L5: 历史记录 - /api/history/*
L6: 数据分析 - /api/analytics/*
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import random

router = APIRouter(prefix="/api", tags=["History & Analytics"])

# ─── 内存存储 (生产环境用数据库) ────────────────────────────────────────────
_history_store = []
_analytics_cache = {}
_last_update = datetime.now()


def _generate_sample_history():
    """生成示例历史数据"""
    global _history_store
    if not _history_store:
        actions = ['资金转账', '策略切换', '风控触发', '仓位调整', '止盈执行', '止损执行', '工具启用', '工具停用']
        statuses = ['成功', '失败', '部分成功']
        for i in range(50):
            _history_store.append({
                'id': i + 1,
                'action': random.choice(actions),
                'status': random.choice(statuses),
                'success': random.random() > 0.15,
                'time': (datetime.now() - timedelta(hours=i*2, minutes=random.randint(0,59))).strftime('%Y-%m-%d %H:%M:%S'),
                'amount': round(random.uniform(100, 10000), 2),
                'tool': random.choice(['打兔子', '打地鼠', '走着瞧', '跟大哥', '搭便车', None]),
                'detail': f'操作详情 #{i+1}'
            })
    return _history_store


def _generate_analytics():
    """生成分析数据"""
    return {
        'total_profit': 30900.0,
        'return_rate': 38.6,
        'max_drawdown': 12.4,
        'sharpe_ratio': 2.1,
        'win_rate': 67.5,
        'trade_count': 156,
        'avg_profit_per_trade': 198.0,
        'profit_by_tool': {
            '打兔子': {'profit': 12500, 'trades': 45, 'win_rate': 72},
            '打地鼠': {'profit': 8300, 'trades': 38, 'win_rate': 65},
            '走着瞧': {'profit': 5200, 'trades': 28, 'win_rate': 70},
            '跟大哥': {'profit': 3100, 'trades': 25, 'win_rate': 68},
            '搭便车': {'profit': 1800, 'trades': 20, 'win_rate': 60}
        },
        'monthly_profit': [
            {'month': '2026-01', 'profit': 4200},
            {'month': '2026-02', 'profit': 5800},
            {'month': '2026-03', 'profit': 8900},
            {'month': '2026-04', 'profit': 12000}
        ],
        'risk_metrics': {
            'var_95': 2500,
            'volatility': 15.2,
            'beta': 1.1,
            'sortino_ratio': 2.4
        },
        'updated_at': datetime.now().isoformat()
    }


# ─── L5: 历史记录 API ───────────────────────────────────────────────────────

class HistoryItem(BaseModel):
    id: int
    action: str
    status: str
    success: bool
    time: str
    amount: Optional[float] = None
    tool: Optional[str] = None
    detail: Optional[str] = None


class HistoryResponse(BaseModel):
    history: List[HistoryItem]
    total: int
    page: int
    page_size: int


@router.get("/history", response_model=HistoryResponse)
async def get_history(
    page: int = 1,
    page_size: int = 20,
    tool: Optional[str] = None,
    action: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    获取操作历史记录
    
    - page: 页码 (默认1)
    - page_size: 每页条数 (默认20)
    - tool: 按工具筛选
    - action: 按操作类型筛选
    """
    _generate_sample_history()
    
    filtered = _history_store.copy()
    
    if tool:
        filtered = [h for h in filtered if h.get('tool') == tool]
    if action:
        filtered = [h for h in filtered if action in h.get('action', '')]
    
    total = len(filtered)
    start = (page - 1) * page_size
    end = start + page_size
    items = filtered[start:end]
    
    return HistoryResponse(
        history=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/history/stats")
async def get_history_stats():
    """获取历史统计"""
    _generate_sample_history()
    
    total = len(_history_store)
    success = sum(1 for h in _history_store if h.get('success'))
    
    # 按操作类型统计
    by_action = {}
    for h in _history_store:
        a = h.get('action', 'unknown')
        if a not in by_action:
            by_action[a] = {'total': 0, 'success': 0}
        by_action[a]['total'] += 1
        if h.get('success'):
            by_action[a]['success'] += 1
    
    # 按工具统计
    by_tool = {}
    for h in _history_store:
        t = h.get('tool') or '其他'
        if t not in by_tool:
            by_tool[t] = {'total': 0, 'success': 0}
        by_tool[t]['total'] += 1
        if h.get('success'):
            by_tool[t]['success'] += 1
    
    return {
        'total': total,
        'success': success,
        'failed': total - success,
        'success_rate': round(success / total * 100, 1) if total > 0 else 0,
        'by_action': by_action,
        'by_tool': by_tool,
        'today_ops': sum(1 for h in _history_store if h['time'].startswith(datetime.now().strftime('%Y-%m-%d'))),
        'week_ops': sum(1 for h in _history_store if (datetime.now() - datetime.strptime(h['time'], '%Y-%m-%d %H:%M:%S')).days < 7)
    }


@router.post("/history")
async def add_history_item(item: HistoryItem):
    """添加历史记录"""
    global _history_store
    _history_store.insert(0, item.dict())
    return {'success': True, 'id': item.id}


# ─── L6: 数据分析 API ───────────────────────────────────────────────────────

class AnalyticsResponse(BaseModel):
    total_profit: float
    return_rate: float
    max_drawdown: float
    sharpe_ratio: float
    win_rate: float
    trade_count: int
    avg_profit_per_trade: float
    profit_by_tool: Dict[str, Any]
    monthly_profit: List[Dict[str, Any]]
    risk_metrics: Dict[str, Any]
    updated_at: str


@router.get("/analytics/overview", response_model=AnalyticsResponse)
async def get_analytics_overview():
    """
    获取分析总览
    
    返回完整的分析数据，包含:
    - 收益指标 (总收益, 收益率, 回撤)
    - 风险指标 (VaR,波动率, Beta, Sortino)
    - 工具收益分布
    - 月度收益趋势
    """
    global _analytics_cache, _last_update
    
    # 缓存5分钟
    if not _analytics_cache or (datetime.now() - _last_update).seconds > 300:
        _analytics_cache = _generate_analytics()
        _last_update = datetime.now()
    
    return AnalyticsResponse(**_analytics_cache)


@router.get("/analytics/profit-chart")
async def get_profit_chart(period: str = "monthly"):
    """
    获取收益图表数据
    
    - period: monthly | weekly | daily
    """
    _generate_analytics()
    
    if period == "monthly":
        data = _analytics_cache.get('monthly_profit', [])
    elif period == "weekly":
        # 模拟周数据
        data = [
            {'week': 'W1', 'profit': 2100},
            {'week': 'W2', 'profit': 2800},
            {'week': 'W3', 'profit': 3200},
            {'week': 'W4', 'profit': 3800}
        ]
    else:
        # 模拟日数据
        data = [{'day': f'D{i}', 'profit': random.uniform(100, 500)} for i in range(1, 32)]
    
    return {'period': period, 'data': data}


@router.get("/analytics/tool-breakdown")
async def get_tool_breakdown():
    """获取各工具收益分解"""
    _generate_analytics()
    return _analytics_cache.get('profit_by_tool', {})


@router.get("/analytics/risk-metrics")
async def get_risk_metrics():
    """获取风险指标"""
    _generate_analytics()
    return _analytics_cache.get('risk_metrics', {})


@router.get("/analytics/comparison")
async def get_comparison(period: str = "30d"):
    """
    获取对比分析
    
    - period: 7d | 30d | 90d | 1y
    """
    return {
        'period': period,
        'go2se_return': round(random.uniform(20, 50), 1),
        'market_return': round(random.uniform(10, 25), 1),
        'alpha': round(random.uniform(5, 20), 1),
        'benchmark': 'BTC',
        'outperformance': round(random.uniform(5, 15), 1)
    }
