"""
⚡ 疯狂抢单模式配置
====================
极致抢单速度，最大化机会捕捉
"""

CRAZY_GRAB_MODE = {
    # 疯狂模式开关
    "enabled": True,
    "mode": "insane",
    
    # 极速响应
    "response_time_ms": 100,    # 100ms内响应 (从500ms)
    "queue_priority": "FIRST",   # 第一优先级
    
    # 全力扫描
    "scan_interval_ms": 5000,   # 5秒扫描 (从15秒)
    "parallel_scan": True,
    "max_concurrent": 10,
    
    # 激进竞价
    "auto_bid": True,
    "bid_increase_rate": 0.5,  # 50%加价
    "max_bid_price": 10,        # 最高$10 (从$2)
    
    # 全面撒网
    "all_task_types": True,
    "min_reward": 1,            # $1就抢 (从$5)
    "accept_low_profit": True,
    
    # 极速交付
    "delivery_speed": "INSTANT",  # 即时交付
    "quality": "STANDARD",         # 标准质量
    
    # 资源全开
    "cpu_allocation": 0.8,     # 80% CPU
    "memory_limit": "2GB"
}

# 激活疯狂模式
ACTIVATED_AT = "2026-04-30 12:01"
