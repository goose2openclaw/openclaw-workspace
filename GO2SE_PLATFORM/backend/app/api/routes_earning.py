"""
打工赚钱API路由
"""

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime

router = APIRouter(prefix="/api/earning", tags=["earning"])

class EarningSkillResponse(BaseModel):
    name: str
    skill_name: str
    income_potential: float
    compute_required: float
    current_weight: float
    enabled: bool

class IncomeStats(BaseModel):
    total_earnings: float
    this_month: float
    last_month: float
    by_skill: Dict[str, float]
    by_channel: Dict[str, float]

class EarningActivateRequest(BaseModel):
    skill_id: str
    config: Optional[Dict] = {}

# 打工技能数据
EARNING_SKILLS = {
    "automation_scripts": {
        "name": "自动化脚本",
        "path": "skills/automation-pack",
        "income_potential": 0.85,
        "compute_required": 0.60,
        "base_weight": 0.12,
        "enabled": True,
        "platforms": ["fiverr", "upwork", "直接客户"]
    },
    "website_cloner": {
        "name": "网站克隆开发",
        "path": "skills/ai-website-cloner",
        "income_potential": 0.90,
        "compute_required": 0.50,
        "base_weight": 0.10,
        "enabled": True,
        "platforms": ["fiverr", "99designs", "直接客户"]
    },
    "article_writing": {
        "name": "文章写作",
        "path": "skills/article-writing",
        "income_potential": 0.70,
        "compute_required": 0.20,
        "base_weight": 0.10,
        "enabled": True,
        "platforms": ["medium", "公众号", "直接客户"]
    },
    "content_writer": {
        "name": "内容创作",
        "path": "skills/content-writer",
        "income_potential": 0.70,
        "compute_required": 0.25,
        "base_weight": 0.10,
        "enabled": True,
        "platforms": ["抖音", "小红书", "直接客户"]
    },
    "api_integration": {
        "name": "API集成服务",
        "path": "skills/public-apis-skill-creator",
        "income_potential": 0.65,
        "compute_required": 0.40,
        "base_weight": 0.08,
        "enabled": True,
        "platforms": ["fiverr", "upwork", "直接客户"]
    },
    "video_to_text": {
        "name": "视频转文字",
        "path": "skills/video-to-text",
        "income_potential": 0.60,
        "compute_required": 0.70,
        "base_weight": 0.08,
        "enabled": True,
        "platforms": ["youtube", "viki", "直接客户"]
    },
    "whisper_tts": {
        "name": "Whisper语音转文字",
        "path": "skills/openai-whisper",
        "income_potential": 0.55,
        "compute_required": 0.65,
        "base_weight": 0.08,
        "enabled": True,
        "platforms": ["会议平台", "播客", "直接客户"]
    },
    "canvas_design": {
        "name": "设计服务",
        "path": "skills/pls-canvas-design",
        "income_potential": 0.55,
        "compute_required": 0.30,
        "base_weight": 0.06,
        "enabled": True,
        "platforms": ["fiverr", "99designs", "直接客户"]
    },
}

@router.get("/skills")
async def list_earning_skills():
    """列出所有打工技能"""
    return {
        "skills": EARNING_SKILLS,
        "total": len(EARNING_SKILLS),
        "total_income_potential": sum(s["income_potential"] for s in EARNING_SKILLS.values())
    }

@router.get("/skills/{skill_id}")
async def get_earning_skill(skill_id: str):
    """获取单个打工技能详情"""
    if skill_id not in EARNING_SKILLS:
        return {"error": "skill not found"}
    return EARNING_SKILLS[skill_id]

@router.post("/skills/{skill_id}/activate")
async def activate_earning_skill(skill_id: str, background_tasks: BackgroundTasks):
    """激活打工技能"""
    if skill_id not in EARNING_SKILLS:
        return {"error": "skill not found"}
    
    skill = EARNING_SKILLS[skill_id]
    
    # 后台激活
    async def activate():
        # TODO: 实现实际的技能激活逻辑
        pass
    
    background_tasks.add_task(activate)
    
    return {
        "status": "activating",
        "skill_id": skill_id,
        "skill_name": skill["name"],
        "message": f"正在激活 {skill['name']}..."
    }

@router.post("/skills/{skill_id}/deactivate")
async def deactivate_earning_skill(skill_id: str):
    """停用打工技能"""
    if skill_id not in EARNING_SKILLS:
        return {"error": "skill not found"}
    
    EARNING_SKILLS[skill_id]["enabled"] = False
    
    return {
        "status": "deactivated",
        "skill_id": skill_id
    }

@router.get("/stats")
async def get_earning_stats():
    """获取打工收入统计"""
    # TODO: 集成实际收入数据
    return {
        "total_earnings": 0.0,
        "this_month": 0.0,
        "last_month": 0.0,
        "by_skill": {},
        "by_channel": {},
        "active_jobs": 0,
        "pending_invoices": 0
    }

@router.get("/opportunities")
async def get_earning_opportunities():
    """获取赚钱机会"""
    # 基于市场需求的动态机会
    opportunities = [
        {
            "id": "auto_script_001",
            "skill": "automation_scripts",
            "title": "Python自动化脚本开发",
            "budget": "$50-200",
            "platform": "fiverr",
            "deadline": "3天",
            "match_score": 0.92
        },
        {
            "id": "website_001",
            "skill": "website_cloner",
            "title": "WordPress网站克隆",
            "budget": "$100-300",
            "platform": "直接客户",
            "deadline": "5天",
            "match_score": 0.88
        },
        {
            "id": "content_001",
            "skill": "content_writer",
            "title": "加密货币内容创作",
            "budget": "$30-100",
            "platform": "medium",
            "deadline": "2天",
            "match_score": 0.85
        }
    ]
    
    return {
        "opportunities": opportunities,
        "total": len(opportunities),
        "best_match": opportunities[0] if opportunities else None
    }

@router.post("/submit-work")
async def submit_earning_work(
    skill_id: str,
    title: str,
    description: str,
    platform: str
):
    """提交工作成果"""
    if skill_id not in EARNING_SKILLS:
        return {"error": "skill not found"}
    
    return {
        "status": "submitted",
        "submission_id": f"SUB_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "skill_id": skill_id,
        "title": title,
        "platform": platform,
        "submitted_at": datetime.now().isoformat()
    }

@router.get("/compute-usage")
async def get_compute_usage():
    """获取算力使用情况"""
    # TODO: 集成实际算力监控
    return {
        "total_compute": 100.0,
        "used_compute": 45.0,
        "idle_compute": 55.0,
        "by_skill": {
            "automation_scripts": 20.0,
            "video_to_text": 15.0,
            "whisper_tts": 10.0
        },
        "recommendation": "可激活更多打工技能，利用闲置算力"
    }
