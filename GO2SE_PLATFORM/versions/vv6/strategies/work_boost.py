"""
💪 打工算力增强配置
====================
加强打工算例，提升收益
"""

WORK_BOOST = {
    # 高频打工扫描
    "scan": {
        "interval_wool": 15,      # 羊毛扫描15秒
        "interval_crowd": 30,    # 众包扫描30秒
        "interval_hunter": 20,    # 打猎扫描20秒
        "parallel": True          # 并行扫描
    },
    
    # 算力分配
    "compute": {
        "wool_cpu": 0.3,       # 30% CPU
        "crowd_cpu": 0.25,      # 25% CPU
        "hunter_cpu": 0.2,      # 20% CPU
        "priority": ["wool", "crowd", "hunter"]
    },
    
    # 收益最大化
    "profit": {
        "min_daily": 10,        # 目标日收益$10
        "compounding": True,     # 复利
        " reinvest_rate": 0.8    # 80%再投资
    }
}
