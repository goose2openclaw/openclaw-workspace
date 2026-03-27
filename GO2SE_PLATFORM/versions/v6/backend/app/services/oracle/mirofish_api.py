#!/usr/bin/env python3
"""
🔮 Oracle MiroFish API
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api/oracle/mirofish", tags=["走着燋-MiroFish"])


class PredictionRequest(BaseModel):
    question: str
    topic: Optional[str] = None


@router.get("/predict")
async def predict(question: str):
    """MiroFish预测"""
    import sys
    sys.path.insert(0, "/root/.openclaw/workspace/GO2SE_PLATFORM/versions/v6")
    from strategies.oracle.mirofish_oracle import get_prediction
    return get_prediction(question)


@router.post("/predict")
async def predict_post(request: PredictionRequest):
    """MiroFish预测 (POST)"""
    import sys
    sys.path.insert(0, "/root/.openclaw/workspace/GO2SE_PLATFORM/versions/v6")
    from strategies.oracle.mirofish_oracle import get_prediction
    return get_prediction(request.question)


@router.get("/consensus")
async def get_consensus(question: str):
    """获取共识分析"""
    import sys
    sys.path.insert(0, "/root/.openclaw/workspace/GO2SE_PLATFORM/versions/v6")
    from strategies.oracle.mirofish_oracle import get_consensus
    return get_consensus(question)


@router.get("/batch")
async def batch_predict(questions: str):
    """批量预测 (逗号分隔)"""
    import sys
    sys.path.insert(0, "/root/.openclaw/workspace/GO2SE_PLATFORM/versions/v6")
    from strategies.oracle.mirofish_oracle import mirofish_oracle
    
    q_list = [q.strip() for q in questions.split(",")]
    return {
        "predictions": mirofish_oracle.batch_predict(q_list),
        "count": len(q_list)
    }


@router.get("/markets")
async def get_prediction_markets():
    """获取预设预测市场"""
    import sys
    sys.path.insert(0, "/root/.openclaw/workspace/GO2SE_PLATFORM/versions/v6")
    from strategies.oracle.mirofish_oracle import mirofish_oracle
    
    markets = [
        "Will BTC reach $100k by end of 2024?",
        "Will ETH exceed $5000 in 2024?",
        "Will there be a Fed rate cut in Q2?",
        "Who will win 2024 US Presidential Election?",
        "Will Solana flip Ethereum by market cap?",
        "Will Bitcoin ETF be approved in 2024?"
    ]
    
    results = []
    for q in markets:
        pred = mirofish_oracle.generate_market_signal(q)
        results.append({
            "question": q,
            "signal": pred["signal"],
            "yes_prob": pred["prediction"]["yes_probability"],
            "confidence": pred["confidence"]
        })
    
    return {"markets": results}


@router.get("/config")
async def get_config():
    """获取MiroFish配置"""
    import sys
    sys.path.insert(0, "/root/.openclaw/workspace/GO2SE_PLATFORM/versions/v6")
    from strategies.oracle.mirofish_oracle import mirofish_oracle
    return mirofish_oracle.config


@router.post("/config")
async def update_config(agent_count: int = 100, consensus_threshold: float = 0.6, simulation_rounds: int = 5):
    """更新配置"""
    import sys
    sys.path.insert(0, "/root/.openclaw/workspace/GO2SE_PLATFORM/versions/v6")
    from strategies.oracle.mirofish_oracle import mirofish_oracle
    
    mirofish_oracle.config.update({
        "agent_count": agent_count,
        "consensus_threshold": consensus_threshold,
        "simulation_rounds": simulation_rounds
    })
    
    return {"success": True, "config": mirofish_oracle.config}
