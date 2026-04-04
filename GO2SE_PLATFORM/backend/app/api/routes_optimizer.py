"""
优化器API路由 - 动态权重+信号融合+回测
"""

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import asyncio

router = APIRouter(prefix="/api/optimizer", tags=["optimizer"])

# ==================== 数据模型 ====================

class BacktestRequest(BaseModel):
    symbols: List[str] = ["BTC", "ETH", "SOL"]
    strategies: List[str] = ["ema_cross", "macd", "rsi_extreme"]
    days: int = 30

class SignalFusionRequest(BaseModel):
    sonar_signals: Dict
    mirofish_predictions: Dict

class WeightUpdateRequest(BaseModel):
    scores: Dict[str, float]  # {strategy_id: score}

# ==================== 路由 ====================

@router.get("/status")
async def get_optimizer_status():
    """获取优化器状态"""
    from backend.app.core.dynamic_weight_optimizer import DynamicWeightOptimizer, MiroFishSignalFusion
    
    optimizer = DynamicWeightOptimizer()
    fusion = MiroFishSignalFusion()
    
    return {
        "status": "active",
        "timestamp": datetime.now().isoformat(),
        "optimizer": {
            "strategies": list(optimizer.current_weights.keys()),
            "weights": optimizer.get_weights(),
            "score_history_count": len(optimizer.scores_history)
        },
        "fusion": {
            "sonar_weight": fusion.sonar_weight,
            "mirofish_weight": fusion.mirofish_weight,
            "threshold": fusion.mirofish_threshold
        }
    }

@router.post("/backtest/run")
async def run_backtest(req: BacktestRequest, background_tasks: BackgroundTasks):
    """运行完整回测"""
    
    async def run():
        from backend.app.core.dynamic_weight_optimizer import CompleteBacktestEngine
        engine = CompleteBacktestEngine()
        result = await engine.run_complete_backtest(req.symbols, req.strategies)
        return result
    
    background_tasks.add_task(run)
    
    return {
        "status": "started",
        "message": f"回测 {req.symbols} × {req.strategies}",
        "estimated_time": f"{len(req.symbols) * len(req.strategies) * 10}s"
    }

@router.get("/backtest/results")
async def get_backtest_results():
    """获取回测结果"""
    # TODO: 从缓存/数据库读取
    return {
        "status": "completed",
        "strategies": {
            "ema_cross": {"score": 75, "grade": "B", "trades": 20},
            "macd": {"score": 55, "grade": "C", "trades": 18},
            "rsi_extreme": {"score": 65, "grade": "B", "trades": 15}
        }
    }

@router.post("/fusion")
async def fuse_signals(req: SignalFusionRequest):
    """融合声纳库和MiroFish信号"""
    from backend.app.core.dynamic_weight_optimizer import MiroFishSignalFusion
    
    fusion = MiroFishSignalFusion()
    fused = fusion.fuse(req.sonar_signals, req.mirofish_predictions)
    signals = fusion.get_trade_signals(fused)
    
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "fused_signals": fused,
        "approved_signals": signals
    }

@router.get("/fusion/signals")
async def get_approved_signals():
    """获取批准的交易信号"""
    from backend.app.core.dynamic_weight_optimizer import MiroFishSignalFusion
    
    fusion = MiroFishSignalFusion()
    
    # 模拟数据
    sonar = {
        "BTC": {"signal": "buy", "confidence": 0.75, "indicators": ["EMA"]},
        "ETH": {"signal": "buy", "confidence": 0.72, "indicators": ["MACD"]},
        "SOL": {"signal": "sell", "confidence": 0.65, "indicators": ["RSI"]}
    }
    miro = {
        "BTC": {"signal": "buy", "confidence": 0.82, "agents": 85},
        "ETH": {"signal": "buy", "confidence": 0.78, "agents": 80},
        "SOL": {"signal": "hold", "confidence": 0.60, "agents": 70}
    }
    
    fused = fusion.fuse(sonar, miro)
    signals = fusion.get_trade_signals(fused)
    
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "approved_signals": signals,
        "total": len(signals)
    }

@router.get("/weights")
async def get_current_weights():
    """获取当前策略权重"""
    from backend.app.core.dynamic_weight_optimizer import DynamicWeightOptimizer
    
    optimizer = DynamicWeightOptimizer()
    
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "weights": optimizer.get_weights(),
        "recommendations": optimizer.get_recommendations()
    }

@router.post("/weights/update")
async def update_weights(req: WeightUpdateRequest):
    """根据评分更新权重"""
    from backend.app.core.dynamic_weight_optimizer import DynamicWeightOptimizer
    
    optimizer = DynamicWeightOptimizer()
    new_weights = optimizer.update_weights(req.scores)
    
    return {
        "status": "updated",
        "timestamp": datetime.now().isoformat(),
        "old_weights": optimizer.base_weights,
        "new_weights": new_weights
    }

@router.get("/weights/recommendations")
async def get_weight_recommendations():
    """获取优化建议"""
    from backend.app.core.dynamic_weight_optimizer import DynamicWeightOptimizer
    
    optimizer = DynamicWeightOptimizer()
    recommendations = optimizer.get_recommendations()
    
    return {
        "status": "success",
        "recommendations": recommendations
    }

@router.get("/costs/summary")
async def get_cost_summary():
    """获取交易成本汇总"""
    from backend.app.core.dynamic_weight_optimizer import TradingCostSimulator, BacktestTrade
    
    simulator = TradingCostSimulator()
    
    # 模拟历史交易
    trades = [
        simulator.simulate_trade(100, 105, "long", 1.0),
        simulator.simulate_trade(50, 48, "long", 2.0),
        simulator.simulate_trade(200, 210, "long", 0.5)
    ]
    
    summary = simulator.get_cost_summary(trades)
    
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        **summary
    }

@router.get("/loop/status")
async def get_feedback_loop_status():
    """获取回测→评估→迭代闭环状态"""
    return {
        "status": "active",
        "timestamp": datetime.now().isoformat(),
        "loop_enabled": True,
        "steps": [
            {"step": 1, "name": "回测", "status": "active", "description": "CCXT真实数据回测"},
            {"step": 2, "name": "评估", "status": "pending", "description": "得分计算A/B/C/D"},
            {"step": 3, "name": "迭代", "status": "pending", "description": "权重调整"}
        ],
        "last_run": datetime.now().isoformat(),
        "next_run": "2小时"
    }
