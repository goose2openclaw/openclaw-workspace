

# 自动优化迭代配置
AUTO_ITERATION = {
    "name": "持续优化循环",
    "enabled": True,
    
    # 迭代周期 (秒)
    "cycle": 300,  # 5分钟
    
    # 优化步骤
    "steps": [
        {"name": "scan", "desc": "扫描机会", "interval": 60},
        {"name": "analyze", "desc": "分析数据", "interval": 30},
        {"name": "execute", "desc": "执行任务", "interval": 60},
        {"name": "learn", "desc": "学习反馈", "interval": 30},
        {"name": "optimize", "desc": "优化参数", "interval": 60},
    ],
    
    # 学习参数
    "learning": {
        "mode": "adaptive",
        "rate": 0.01,
        "memory": True,
        "pattern": True
    },
    
    # 循环状态
    "status": "running",
    "iterations": 0,
    "uptime": "持续运行中"
}
