"""
💰 打工任务模拟器
==================
当外部API不可用时，生成模拟任务进行测试
"""

import random
import time
from datetime import datetime

WORK_SIMULATOR = {
    "enabled": True,
    "name": "打工任务模拟器",
    
    # 模拟任务池
    "task_pool": [
        # 🔴 第一优先级 - 高价值
        {"category": "airdrop", "title": "LayerZero空投认领", "reward": 150, "urgency": "high", "skills": ["web3", "defi"]},
        {"category": "airdrop", "title": "zkSync Era测试网交互", "reward": 200, "urgency": "high", "skills": ["web3", "nft"]},
        {"category": "testnet", "title": "Gitcoin Quest完成", "reward": 300, "urgency": "high", "skills": ["web3", "git"]},
        {"category": "new_listing", "title": "Binance新币打新", "reward": 500, "urgency": "high", "skills": ["trading"]},
        
        # 🟡 第二优先级 - 中等价值
        {"category": "translation", "title": "英文技术文档翻译", "reward": 80, "urgency": "medium", "skills": ["english", "tech"]},
        {"category": "coding", "title": "Python数据处理脚本", "reward": 200, "urgency": "medium", "skills": ["python", "data"]},
        {"category": "affiliate", "title": "推广链接分享", "reward": 50, "urgency": "medium", "skills": ["marketing"]},
        
        # 🟢 第三优先级 - 稳定收入
        {"category": "data_entry", "title": "Excel数据录入", "reward": 30, "urgency": "low", "skills": ["excel"]},
        {"category": "testing", "title": "App功能测试", "reward": 50, "urgency": "low", "skills": ["qa"]},
        {"category": "review", "title": "产品评测写作", "reward": 40, "urgency": "low", "skills": ["writing"]},
    ],
    
    # 生成设置
    "generate": {
        "interval_seconds": 60,  # 每60秒生成新任务
        "max_tasks": 20,         # 最多保留20个任务
        "success_rate": 0.8,     # 80%成功率
    },
    
    # 统计
    "stats": {
        "total_generated": 0,
        "total_sniped": 0,
        "total_completed": 0,
        "total_earned": 0,
    }
}

def generate_task():
    """生成随机任务"""
    task = random.choice(WORK_SIMULATOR["task_pool"])
    task["id"] = f"T{int(time.time())}_{random.randint(1000,9999)}"
    task["created_at"] = datetime.now().isoformat()
    task["expires_in"] = random.randint(300, 3600)  # 5分钟-1小时过期
    return task

def get_tasks_by_priority():
    """按优先级返回任务"""
    tasks = []
    for _ in range(random.randint(3, 8)):
        task = generate_task()
        # 高优先级任务概率更高
        if task["urgency"] == "high" and random.random() > 0.3:
            continue
        tasks.append(task)
    
    # 按奖励排序
    tasks.sort(key=lambda x: x["reward"], reverse=True)
    return tasks[:10]

# 初始化
print("✅ 打工任务模拟器已启动")
print(f"   任务池: {len(WORK_SIMULATOR['task_pool'])} 个任务")
print(f"   生成间隔: {WORK_SIMULATOR['generate']['interval_seconds']}秒")


# 抢单增强配置
SNIPE_ENHANCEMENT = {
    "name": "疯狂抢单模式",
    "enabled": True,
    
    # 抢单策略
    "snipe_strategy": {
        # 第一优先级 - 必抢
        "must_snipe": {
            "airdrop": {"min_reward": 50, "speed": "instant"},
            "testnet": {"min_reward": 100, "speed": "fast"},
            "new_listing": {"min_reward": 100, "speed": "instant"},
        },
        
        # 第二优先级 - 高价值
        "high_value": {
            "coding": {"min_reward": 50, "speed": "normal"},
            "translation": {"min_reward": 30, "speed": "normal"},
            "affiliate": {"min_reward": 20, "speed": "normal"},
        },
        
        # 第三优先级 - 稳定
        "steady": {
            "data_entry": {"min_reward": 10, "speed": "normal"},
            "testing": {"min_reward": 15, "speed": "normal"},
            "review": {"min_reward": 10, "speed": "normal"},
        }
    },
    
    # 执行设置
    "execution": {
        "scan_interval_ms": 5000,      # 5秒扫描一次
        "snipe_timeout_ms": 1000,       # 1秒内必须抢
        "max_concurrent": 3,           # 最多3个并发任务
        "retry_count": 3,              # 失败重试3次
        "retry_delay_ms": 500,         # 重试间隔500ms
    },
    
    # 过滤规则
    "filters": {
        "min_reward": 10,              # 最低$10
        "max_age_seconds": 3600,       # 1小时内
        "exclude_categories": [],
        "require_skills": [],          # 空=不限
    }
}

print("✅ 抢单增强配置已加载")
print("   扫描间隔: 5秒")
print("   抢单超时: 1秒")
print("   最大并发: 3个任务")
