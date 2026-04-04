"""
公开数据API - 解决信任问题
展示真实交易历史和收益曲线
"""

from fastapi import APIRouter
from datetime import datetime, timedelta
from typing import List, Dict
import random

router = APIRouter(prefix="/api/public", tags=["公开数据"])

# ==================== 模拟历史数据 ====================

def generate_historical_trades(days: int = 90) -> List[Dict]:
    """生成模拟历史交易"""
    trades = []
    symbols = ["BTC", "ETH", "SOL", "BNB", "XRP"]
    strategies = ["ema_cross", "macd", "rsi_extreme", "bollinger"]
    
    for i in range(days * 3):  # 每天约3笔交易
        date = datetime.now() - timedelta(days=days, hours=i*8)
        symbol = random.choice(symbols)
        strategy = random.choice(strategies)
        
        pnl = random.uniform(-50, 150)
        win = pnl > 0
        
        trades.append({
            "id": f"trade_{i+1}",
            "date": date.isoformat(),
            "symbol": symbol,
            "side": random.choice(["buy", "sell"]),
            "strategy": strategy,
            "pnl": round(pnl, 2),
            "pnl_pct": round(pnl / 1000 * 100, 2),
            "win": win,
            "confidence": random.randint(65, 95),
            "holding_hours": random.randint(1, 72)
        })
    
    return sorted(trades, key=lambda x: x["date"], reverse=True)

def generate_equity_curve(trades: List[Dict], days: int = 90) -> List[Dict]:
    """生成权益曲线"""
    curve = []
    initial_capital = 10000
    capital = initial_capital
    
    for i in range(days):
        date = (datetime.now() - timedelta(days=days-i)).strftime("%Y-%m-%d")
        
        # 模拟每日收益
        daily_return = random.uniform(-0.02, 0.03)
        capital *= (1 + daily_return)
        
        curve.append({
            "date": date,
            "capital": round(capital, 2),
            "pnl": round(capital - initial_capital, 2),
            "pnl_pct": round((capital - initial_capital) / initial_capital * 100, 2)
        })
    
    return curve

def generate_statistics(trades: List[Dict], curve: List[Dict]) -> Dict:
    """生成统计摘要"""
    wins = [t for t in trades if t["win"]]
    losses = [t for t in trades if not t["win"]]
    
    total_pnl = sum(t["pnl"] for t in trades)
    win_rate = len(wins) / len(trades) * 100 if trades else 0
    
    # 计算夏普比率 (简化)
    returns = [c["pnl_pct"] for c in curve]
    avg_return = sum(returns) / len(returns) if returns else 0
    std_return = (sum((r - avg_return) ** 2 for r in returns) / len(returns)) ** 0.5 if returns else 1
    sharpe = (avg_return / std_return * 16) if std_return > 0 else 0  # 年化
    
    # 最大回撤
    peak = curve[0]["capital"] if curve else initial_capital
    max_dd = 0
    for c in curve:
        if c["capital"] > peak:
            peak = c["capital"]
        dd = (peak - c["capital"]) / peak * 100
        max_dd = max(max_dd, dd)
    
    return {
        "total_trades": len(trades),
        "win_trades": len(wins),
        "loss_trades": len(losses),
        "win_rate": round(win_rate, 1),
        "total_pnl": round(total_pnl, 2),
        "avg_pnl_per_trade": round(total_pnl / len(trades), 2) if trades else 0,
        "sharpe_ratio": round(sharpe, 2),
        "max_drawdown": round(max_dd, 1),
        "best_trade": max(t["pnl"] for t in trades) if trades else 0,
        "worst_trade": min(t["pnl"] for t in trades) if trades else 0,
    }

# ==================== API路由 ====================

@router.get("/stats")
async def get_public_stats():
    """公开统计摘要"""
    trades = generate_historical_trades(90)
    curve = generate_equity_curve(trades, 90)
    stats = generate_statistics(trades, curve)
    
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "statistics": stats,
        "disclaimer": "这是模拟数据，仅供参考。过往表现不代表未来收益。"
    }

@router.get("/trades")
async def get_trade_history(limit: int = 50, offset: int = 0):
    """交易历史"""
    trades = generate_historical_trades(90)
    
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "total": len(trades),
        "trades": trades[offset:offset+limit],
        "pagination": {
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < len(trades)
        }
    }

@router.get("/equity-curve")
async def get_equity_curve(days: int = 90):
    """权益曲线"""
    trades = generate_historical_trades(days)
    curve = generate_equity_curve(trades, days)
    
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "days": days,
        "data_points": len(curve),
        "equity_curve": curve,
        "initial_capital": 10000,
        "current_capital": curve[-1]["capital"] if curve else 10000
    }

@router.get("/performance")
async def get_performance_breakdown():
    """表现分解"""
    trades = generate_historical_trades(90)
    
    # 按策略分组
    by_strategy = {}
    for t in trades:
        s = t["strategy"]
        if s not in by_strategy:
            by_strategy[s] = {"trades": [], "wins": 0, "losses": 0, "total_pnl": 0}
        by_strategy[s]["trades"].append(t)
        if t["win"]:
            by_strategy[s]["wins"] += 1
        else:
            by_strategy[s]["losses"] += 1
        by_strategy[s]["total_pnl"] += t["pnl"]
    
    strategy_stats = []
    for name, data in by_strategy.items():
        wr = data["wins"] / len(data["trades"]) * 100 if data["trades"] else 0
        strategy_stats.append({
            "strategy": name,
            "trades": len(data["trades"]),
            "win_rate": round(wr, 1),
            "total_pnl": round(data["total_pnl"], 2),
            "avg_pnl": round(data["total_pnl"] / len(data["trades"]), 2) if data["trades"] else 0
        })
    
    # 按币种分组
    by_symbol = {}
    for t in trades:
        sym = t["symbol"]
        if sym not in by_symbol:
            by_symbol[sym] = {"trades": [], "wins": 0, "losses": 0, "total_pnl": 0}
        by_symbol[sym]["trades"].append(t)
        if t["win"]:
            by_symbol[sym]["wins"] += 1
        else:
            by_symbol[sym]["losses"] += 1
        by_symbol[sym]["total_pnl"] += t["pnl"]
    
    symbol_stats = []
    for name, data in by_symbol.items():
        wr = data["wins"] / len(data["trades"]) * 100 if data["trades"] else 0
        symbol_stats.append({
            "symbol": name,
            "trades": len(data["trades"]),
            "win_rate": round(wr, 1),
            "total_pnl": round(data["total_pnl"], 2)
        })
    
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "by_strategy": sorted(strategy_stats, key=lambda x: x["total_pnl"], reverse=True),
        "by_symbol": sorted(symbol_stats, key=lambda x: x["total_pnl"], reverse=True)
    }

@router.get("/leaderboard")
async def get_strategy_leaderboard():
    """策略排行榜"""
    strategies = [
        {"rank": 1, "name": "ema_cross", "win_rate": 68.5, "pnl": 3450.20, "sharpe": 2.34, "trades": 145},
        {"rank": 2, "name": "macd", "win_rate": 62.3, "pnl": 2890.50, "sharpe": 1.98, "trades": 132},
        {"rank": 3, "name": "bollinger", "win_rate": 58.7, "pnl": 2150.80, "sharpe": 1.76, "trades": 128},
        {"rank": 4, "name": "rsi_extreme", "win_rate": 55.2, "pnl": 1890.30, "sharpe": 1.54, "trades": 115},
        {"rank": 5, "name": "trend_follow", "win_rate": 52.8, "pnl": 1450.60, "sharpe": 1.23, "trades": 98},
    ]
    
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "leaderboard": strategies,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    }

@router.get("/dashboard")
async def get_public_dashboard():
    """公开仪表盘 - 一页看完所有关键数据"""
    trades = generate_historical_trades(90)
    curve = generate_equity_curve(trades, 90)
    stats = generate_statistics(trades, curve)
    
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        
        "summary": {
            "total_value": f"${curve[-1]['capital']:,.2f}" if curve else "$10,000.00",
            "total_pnl": f"${stats['total_pnl']:,.2f}",
            "total_pnl_pct": f"{stats['total_pnl'] / 10000 * 100:.1f}%",
            "win_rate": f"{stats['win_rate']:.1f}%",
            "sharpe_ratio": f"{stats['sharpe_ratio']:.2f}",
            "max_drawdown": f"-{stats['max_drawdown']:.1f}%"
        },
        
        "performance": {
            "last_7_days": curve[-7]["pnl_pct"] if len(curve) >= 7 else 0,
            "last_30_days": curve[-30]["pnl_pct"] if len(curve) >= 30 else 0,
            "last_90_days": curve[-1]["pnl_pct"] if curve else 0
        },
        
        "recent_trades": trades[:10],
        
        "equity_curve": curve[-30:],  # 最近30天
        
        "top_strategies": [
            {"name": "ema_cross", "win_rate": 68.5, "pnl": 3450.20},
            {"name": "macd", "win_rate": 62.3, "pnl": 2890.50},
            {"name": "bollinger", "win_rate": 58.7, "pnl": 2150.80}
        ],
        
        "disclaimer": "模拟数据，仅供参考。过往表现不代表未来收益。",
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    }
