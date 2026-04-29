"""
🚀 GO2SE Genius 深度优化模块 v2
=================================
2026-04-29 三项核心优化

优化内容:
1. Mirofish算法复杂度提升
2. 决策阈值动态调整
3. 反思频率优化
"""

OPTIMIZATION_CONFIG = {
    # Mirofish算法增强
    "mirofish": {
        "consensus_rounds": 5,      # 3 → 5
        "active_agents": 150,        # 100 → 150
        "voting_threshold": 0.6,    # 新增
        "score_target": 0.90          # 目标90%+
    },
    
    # 决策引擎优化
    "decision_engine": {
        "decision_threshold": 0.68,  # 0.65 → 0.68
        "confidence_boost": 0.12,    # 0.1 → 0.12
        "min_confidence": 0.7,      # 新增
        "dynamic_adjustment": True    # 新增: 动态调整
    },
    
    # 反思机制优化
    "reflection": {
        "cycle_minutes": 15,        # 30 → 15
        "learning_rate": 0.15,       # 新增
        "pattern_threshold": 0.8      # 新增
    },
    
    # 预期效果
    "expected": {
        "mirofish_score": "82% → 90%+",
        "decision_precision": "+5%",
        "reflection_speed": "2x"
    }
}
