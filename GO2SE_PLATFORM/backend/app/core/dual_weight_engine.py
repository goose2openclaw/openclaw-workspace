"""
双轨权重引擎 - 投资与打工分离

投资赚钱: 资金驱动 → 策略权重
打工赚钱: 算力驱动 → 技能权重
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
import json
import os

# 数据目录
DATA_DIR = os.path.join(os.path.dirname(__file__), "../../data/weights")
os.makedirs(DATA_DIR, exist_ok=True)

@dataclass
class InvestmentWeight:
    """投资权重"""
    # 策略相关
    strategy_name: str
    strategy_type: str  # rabbit/mole/oracle/leader/hitchhiker/airdrop/crowdsource
    tool: str           # 属于哪个工具
    
    # 核心指标
    win_rate: float     # 胜率 0-1
    sharpe_ratio: float # 夏普比率
    max_drawdown: float # 最大回撤
    
    # 资金相关
    position_size: float  # 仓位占比
    capital_weight: float # 资金权重因子
    
    # 动态权重
    current_weight: float
    mirofish_score: float = 0.8
    
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass  
class EarningSkill:
    """打工技能"""
    skill_name: str
    skill_path: str
    
    # 变现能力
    income_potential: float   # 收入潜力 0-1
    skill_efficiency: float   # 技能效率 0-1
    market_demand: float      # 市场需求 0-1
    
    # 算力相关
    compute_required: float   # 所需算力 0-1
    idle_compute_bonus: float # 闲置算力加成 0-1
    
    # 动态权重
    current_weight: float
    
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())

class DualWeightEngine:
    """
    双轨权重引擎
    
    投资轨 (Investment Track):
    - 核心资源: 资金
    - 权重 = f(策略胜率, 夏普比率, 资金配置, MiroFish验证)
    
    打工轨 (Earning Track):
    - 核心资源: 算力  
    - 权重 = f(收入潜力, 技能效率, 闲置算力, 市场需求的集成)
    """
    
    def __init__(self):
        self.investment_weights: Dict[str, InvestmentWeight] = {}
        self.earning_skills: Dict[str, EarningSkill] = {}
        
        self._init_investment_strategies()
        self._init_earning_skills()
    
    # ==================== 投资轨 (资金驱动) ====================
    
    def _init_investment_strategies(self):
        """初始化投资策略权重"""
        strategies = {
            # 🐰 打兔子 - 前20主流加密货币
            "rabbit_v2": InvestmentWeight(
                strategy_name="Rabbit V2",
                strategy_type="rabbit",
                tool="🐰 打兔子",
                win_rate=0.72,
                sharpe_ratio=1.85,
                max_drawdown=0.08,
                position_size=0.25,
                capital_weight=0.25,
                current_weight=0.0
            ),
            "rabbit": InvestmentWeight(
                strategy_name="Rabbit",
                strategy_type="rabbit", 
                tool="🐰 打兔子",
                win_rate=0.68,
                sharpe_ratio=1.65,
                max_drawdown=0.10,
                position_size=0.20,
                capital_weight=0.20,
                current_weight=0.0
            ),
            "crypto_dca": InvestmentWeight(
                strategy_name="DCA定投",
                strategy_type="rabbit",
                tool="🐰 打兔子",
                win_rate=0.75,
                sharpe_ratio=1.92,
                max_drawdown=0.03,
                position_size=0.15,
                capital_weight=0.15,
                current_weight=0.0
            ),
            
            # 🐹 打地鼠 - 其他加密货币
            "mole_v2": InvestmentWeight(
                strategy_name="Mole V2",
                strategy_type="mole",
                tool="🐹 打地鼠",
                win_rate=0.65,
                sharpe_ratio=1.45,
                max_drawdown=0.12,
                position_size=0.20,
                capital_weight=0.20,
                current_weight=0.0
            ),
            "mole": InvestmentWeight(
                strategy_name="Mole",
                strategy_type="mole",
                tool="🐹 打地鼠",
                win_rate=0.62,
                sharpe_ratio=1.32,
                max_drawdown=0.15,
                position_size=0.15,
                capital_weight=0.15,
                current_weight=0.0
            ),
            
            # 🔮 走着瞧 - 预测市场
            "oracle": InvestmentWeight(
                strategy_name="Oracle预测",
                strategy_type="oracle",
                tool="🔮 走着瞧",
                win_rate=0.70,
                sharpe_ratio=1.55,
                max_drawdown=0.07,
                position_size=0.15,
                capital_weight=0.15,
                current_weight=0.0
            ),
            
            # 👑 跟大哥 - 做市协作
            "leader_v2": InvestmentWeight(
                strategy_name="Leader V2",
                strategy_type="leader",
                tool="👑 跟大哥",
                win_rate=0.68,
                sharpe_ratio=1.50,
                max_drawdown=0.06,
                position_size=0.15,
                capital_weight=0.15,
                current_weight=0.0
            ),
            "smart_rebalance": InvestmentWeight(
                strategy_name="智能再平衡",
                strategy_type="leader",
                tool="👑 跟大哥",
                win_rate=0.72,
                sharpe_ratio=1.80,
                max_drawdown=0.04,
                position_size=0.10,
                capital_weight=0.10,
                current_weight=0.0
            ),
            
            # 🍀 搭便车 - 跟单分成
            "signal_optimizer": InvestmentWeight(
                strategy_name="信号优化器",
                strategy_type="hitchhiker",
                tool="🍀 搭便车",
                win_rate=0.75,
                sharpe_ratio=1.90,
                max_drawdown=0.05,
                position_size=0.10,
                capital_weight=0.10,
                current_weight=0.0
            ),
            
            # 🛡️ 声纳 - 风控
            "sonar": InvestmentWeight(
                strategy_name="声纳库123模型",
                strategy_type="sonar",
                tool="🛡️ 声纳",
                win_rate=0.70,
                sharpe_ratio=1.70,
                max_drawdown=0.06,
                position_size=0.0,  # 风控不占仓位
                capital_weight=0.0,
                current_weight=0.0
            ),
            
            # 🔮 MiroFish - 核心验证
            "mirofish": InvestmentWeight(
                strategy_name="MiroFish共识",
                strategy_type="mirofish",
                tool="🔮 MiroFish",
                win_rate=0.78,
                sharpe_ratio=2.10,
                max_drawdown=0.05,
                position_size=0.0,
                capital_weight=0.0,
                current_weight=0.0,
                mirofish_score=1.0
            ),
        }
        self.investment_weights = strategies
    
    def calculate_investment_weights(self, mirofish_verification: float = 0.85) -> Dict[str, float]:
        """
        计算投资权重 - 资金驱动
        
        公式:
        权重 = 基础权重 × 胜率因子 × 夏普因子 × MiroFish验证 × 资金配置因子
        
        基础权重 = 策略仓位占比
        胜率因子 = win_rate / 0.7 (基准70%)
        夏普因子 = sharpe_ratio / 1.5 (基准1.5)
        """
        weights = {}
        
        # 计算总仓位
        total_position = sum(s.position_size for s in self.investment_weights.values())
        
        for name, strategy in self.investment_weights.items():
            # 基础权重 = 仓位占比
            base_weight = strategy.position_size / total_position if total_position > 0 else 0
            
            # 胜率因子 (0.5 - 1.5)
            win_factor = max(0.5, min(1.5, strategy.win_rate / 0.7))
            
            # 夏普因子 (0.5 - 1.5)
            sharpe_factor = max(0.5, min(1.5, strategy.sharpe_ratio / 1.5))
            
            # MiroFish验证
            mirofish_factor = strategy.mirofish_score * mirofish_verification
            
            # 资金配置因子
            capital_factor = 1.0 + (strategy.capital_weight * 0.2)
            
            # 最终权重
            weight = base_weight * win_factor * sharpe_factor * mirofish_factor * capital_factor
            weights[f"invest_{name}"] = weight
        
        # 归一化
        total = sum(weights.values())
        if total > 0:
            weights = {k: v / total for k, v in weights.items()}
        
        return weights
    
    # ==================== 打工轨 (算力驱动) ====================
    
    def _init_earning_skills(self):
        """初始化打工技能权重"""
        skills = {
            # 高优先级 - 高收入技能
            "automation_scripts": EarningSkill(
                skill_name="自动化脚本",
                skill_path="skills/automation-pack",
                income_potential=0.85,
                skill_efficiency=0.80,
                market_demand=0.75,
                compute_required=0.60,
                idle_compute_bonus=0.90,  # 大量闲置算力可用
                current_weight=0.0
            ),
            "website_cloner": EarningSkill(
                skill_name="网站克隆开发",
                skill_path="skills/ai-website-cloner",
                income_potential=0.90,
                skill_efficiency=0.75,
                market_demand=0.80,
                compute_required=0.50,
                idle_compute_bonus=0.85,
                current_weight=0.0
            ),
            
            # 中高优先级
            "article_writing": EarningSkill(
                skill_name="文章写作",
                skill_path="skills/article-writing",
                income_potential=0.70,
                skill_efficiency=0.85,
                market_demand=0.70,
                compute_required=0.20,  # 低算力需求
                idle_compute_bonus=0.95,
                current_weight=0.0
            ),
            "content_writer": EarningSkill(
                skill_name="内容创作",
                skill_path="skills/content-writer",
                income_potential=0.70,
                skill_efficiency=0.80,
                market_demand=0.75,
                compute_required=0.25,
                idle_compute_bonus=0.90,
                current_weight=0.0
            ),
            
            # 中等优先级
            "api_integration": EarningSkill(
                skill_name="API集成服务",
                skill_path="skills/public-apis-skill-creator",
                income_potential=0.65,
                skill_efficiency=0.70,
                market_demand=0.60,
                compute_required=0.40,
                idle_compute_bonus=0.75,
                current_weight=0.0
            ),
            "video_to_text": EarningSkill(
                skill_name="视频转文字",
                skill_path="skills/video-to-text",
                income_potential=0.60,
                skill_efficiency=0.75,
                market_demand=0.65,
                compute_required=0.70,  # 视频处理需要较高算力
                idle_compute_bonus=0.70,
                current_weight=0.0
            ),
            "whisper_tts": EarningSkill(
                skill_name="Whisper语音转文字",
                skill_path="skills/openai-whisper",
                income_potential=0.55,
                skill_efficiency=0.80,
                market_demand=0.60,
                compute_required=0.65,
                idle_compute_bonus=0.70,
                current_weight=0.0
            ),
            
            # 设计类
            "canvas_design": EarningSkill(
                skill_name="设计服务",
                skill_path="skills/pls-canvas-design",
                income_potential=0.55,
                skill_efficiency=0.70,
                market_demand=0.65,
                compute_required=0.30,
                idle_compute_bonus=0.80,
                current_weight=0.0
            ),
        }
        self.earning_skills = skills
    
    def calculate_earning_weights(self, idle_compute_factor: float = 0.8) -> Dict[str, float]:
        """
        计算打工权重 - 算力驱动
        
        公式:
        权重 = 基础分数 × 收入因子 × 需求因子 × 闲置算力加成
        
        基础分数 = (收入潜力 + 技能效率) / 2
        收入因子 = income_potential / 0.7
        需求因子 = 市场需求
        闲置算力加成 = idle_compute_bonus × idle_compute_factor
        
        核心原则: 闲置算力越多，高算力需求技能权重越高
        """
        weights = {}
        
        for name, skill in self.earning_skills.items():
            # 基础分数
            base_score = (skill.income_potential + skill.skill_efficiency) / 2
            
            # 收入因子
            income_factor = skill.income_potential / 0.7
            
            # 市场需求因子
            demand_factor = skill.market_demand
            
            # 闲置算力加成 (核心!)
            # 如果闲置算力多，高算力技能权重上升
            compute_bonus = skill.idle_compute_bonus * idle_compute_factor
            
            # 综合权重
            weight = base_score * income_factor * demand_factor * (1 + compute_bonus)
            weights[f"earn_{name}"] = weight
        
        # 归一化
        total = sum(weights.values())
        if total > 0:
            weights = {k: v / total for k, v in weights.items()}
        
        return weights
    
    # ==================== 双轨融合 ====================
    
    def get_dual_track_weights(self, 
                               investment_ratio: float = 0.8,
                               mirofish_verification: float = 0.85,
                               idle_compute_factor: float = 0.8) -> Dict[str, float]:
        """
        获取双轨权重
        
        Args:
            investment_ratio: 投资占比 (0-1), 打工占比 = 1 - investment_ratio
            mirofish_verification: MiroFish验证分数
            idle_compute_factor: 闲置算力因子 (0-1)
        
        Returns:
            Dict: 所有权重 (invest_* 和 earn_*)
        """
        # 计算投资权重
        invest_weights = self.calculate_investment_weights(mirofish_verification)
        
        # 计算打工权重
        earn_weights = self.calculate_earning_weights(idle_compute_factor)
        
        # 按比例融合
        combined = {}
        
        # 投资轨
        for k, v in invest_weights.items():
            combined[k] = v * investment_ratio
        
        # 打工轨
        for k, v in earn_weights.items():
            combined[k] = v * (1 - investment_ratio)
        
        return combined
    
    def get_summary(self) -> dict:
        """获取双轨摘要"""
        return {
            "investment_track": {
                "strategies_count": len(self.investment_weights),
                "strategies": [
                    {
                        "name": s.strategy_name,
                        "tool": s.tool,
                        "win_rate": s.win_rate,
                        "sharpe": s.sharpe_ratio
                    }
                    for s in self.investment_weights.values()
                ]
            },
            "earning_track": {
                "skills_count": len(self.earning_skills),
                "skills": [
                    {
                        "name": s.skill_name,
                        "income_potential": s.income_potential,
                        "compute_required": s.compute_required
                    }
                    for s in self.earning_skills.values()
                ]
            }
        }


# 全局实例
_dual_engine = None

def get_dual_weight_engine() -> DualWeightEngine:
    global _dual_engine
    if _dual_engine is None:
        _dual_engine = DualWeightEngine()
    return _dual_engine
