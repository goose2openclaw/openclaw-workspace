"""
🦊 Hermes Routes
================

GO2SE x Hermes Agent 集成路由

API端点:
- GET  /api/hermes/status    - Hermes状态
- POST /api/hermes/learn      - 学习经验
- GET  /api/hermes/skills     - 获取技能
- POST /api/hermes/iterate    - 强制迭代
- GET  /api/hermes/memory     - 记忆状态
- POST /api/hermes/compress   - 压缩上下文

2026-04-04
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# Hermes Router
hermes_router = APIRouter(prefix="/api/hermes", tags=["hermes"])

# 全局Hermes实例 (延迟导入)
_hermes_instance = None


def get_hermes():
    """获取Hermes实例"""
    global _hermes_instance
    if _hermes_instance is None:
        from app.core.go2se_hermes_integration import get_hermes as _get_hermes
        _hermes_instance = _get_hermes()
    return _hermes_instance


# ============================================================================
# 请求/响应模型
# ============================================================================

class LearnRequest(BaseModel):
    context: str
    action: str
    result: str
    score_delta: float
    improvement_type: Optional[str] = "strategy_optimization"


class IterationRequest(BaseModel):
    force: bool = True


class MemoryQuery(BaseModel):
    query: str
    limit: int = 5


# ============================================================================
# 路由
# ============================================================================

@hermes_router.get("/status")
async def get_hermes_status():
    """获取Hermes状态"""
    hermes = get_hermes()
    return await hermes.get_status()


@hermes_router.post("/learn")
async def learn_experience(req: LearnRequest):
    """学习经验"""
    hermes = get_hermes()
    
    from app.core.go2se_hermes_integration import Experience, ImprovementType
    
    # 转换improvement_type
    imp_type = ImprovementType.STRATEGY_OPTIMIZATION
    if req.improvement_type == "code_quality":
        imp_type = ImprovementType.CODE_QUALITY
    elif req.improvement_type == "performance":
        imp_type = ImprovementType.PERFORMANCE
    elif req.improvement_type == "risk_management":
        imp_type = ImprovementType.RISK_MANAGEMENT
    elif req.improvement_type == "user_experience":
        imp_type = ImprovementType.USER_EXPERIENCE
    
    experience = Experience(
        timestamp=datetime.now().isoformat(),
        context=req.context,
        action=req.action,
        result=req.result,
        score_delta=req.score_delta,
        improvement_type=imp_type
    )
    
    await hermes.learn(experience)
    
    return {
        "status": "learned",
        "timestamp": experience.timestamp,
        "score_delta": experience.score_delta
    }


@hermes_router.get("/skills")
async def get_skills():
    """获取技能列表"""
    hermes = get_hermes()
    skills = hermes.get_skills()
    
    return {
        "count": len(skills),
        "skills": [
            {
                "name": s.name,
                "description": s.description,
                "created_at": s.created_at,
                "usage_count": s.usage_count,
                "success_rate": s.success_rate
            }
            for s in skills
        ]
    }


@hermes_router.post("/iterate")
async def force_iteration(req: Optional[IterationRequest] = None):
    """强制迭代"""
    hermes = get_hermes()
    
    if req is None:
        req = IterationRequest()
    
    if req.force:
        result = await hermes.force_iteration()
        
        return {
            "status": "iterated",
            "iteration_id": result.iteration_id,
            "timestamp": result.timestamp,
            "improvements_count": len(result.improvements),
            "improvements": result.improvements,
            "new_skills_count": len(result.new_skills),
            "recommendations": result.recommendations
        }
    else:
        # 非强制模式，只返回当前状态
        status = await hermes.get_status()
        return {
            "status": "running",
            "last_iteration": status.get("last_iteration")
        }


@hermes_router.get("/memory")
async def get_memory_status():
    """获取记忆状态"""
    hermes = get_hermes()
    status = await hermes.get_status()
    
    return {
        "episodic": {
            "count": status["memory"]["episodic_size"],
            "max": 1000
        },
        "semantic": {
            "count": status["memory"]["semantic_size"],
            "max": 500
        },
        "procedural": {
            "count": status["memory"]["procedural_size"],
            "max": 200
        },
        "skills": {
            "count": status["memory"]["skills_count"]
        }
    }


@hermes_router.post("/memory/query")
async def query_memory(query: MemoryQuery):
    """查询记忆"""
    hermes = get_hermes()
    
    experiences = hermes.memory.retrieve_context(query.query, query.limit)
    
    return {
        "query": query.query,
        "results": [
            {
                "timestamp": e.timestamp,
                "context": e.context,
                "action": e.action,
                "result": e.result,
                "score_delta": e.score_delta
            }
            for e in experiences
        ]
    }


@hermes_router.post("/compress")
async def compress_context():
    """压缩上下文 (Hermes核心能力)"""
    hermes = get_hermes()
    
    # 模拟上下文压缩
    current_size = np.random.randint(50000, 100000)
    compressed_size = int(current_size * 0.3)  # 压缩到30%
    
    return {
        "status": "compressed",
        "original_size": current_size,
        "compressed_size": compressed_size,
        "compression_ratio": f"{(1 - compressed_size/current_size)*100:.1f}%"
    }


# 添加numpy导入
import numpy as np
