#!/usr/bin/env python3
"""
权重自动更新Cron脚本
每2小时运行一次，周期性抓取外部胜率并更新权重
"""

import sys
import os
import asyncio
import json
from datetime import datetime

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.weight_updater import get_weight_updater

async def main():
    print(f"[{datetime.now().isoformat()}] 开始权重更新周期...")
    
    updater = get_weight_updater()
    
    # 1. 显示注册表状态
    summary = updater.get_registry_summary()
    print(f"技能数量: {summary['skills_count']}")
    print(f"策略数量: {summary['strategies_count']}")
    
    # 2. 抓取外部胜率
    print("抓取外部胜率...")
    external_stats = await updater.fetch_external_win_rates()
    for name, rate in external_stats.items():
        print(f"  {name}: {rate:.2%}")
    
    # 3. 运行完整更新
    print("计算综合权重...")
    result = await updater.run_update_cycle()
    
    print(f"更新完成: {result.timestamp}")
    print(f"MiroFish验证分数: {result.mirofish_verification:.2%}")
    print(f"总置信度: {result.total_confidence:.2%}")
    
    # 4. 显示Top权重
    sorted_weights = sorted(
        result.combined_weights.items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]
    
    print("\nTop 10 权重:")
    for name, weight in sorted_weights:
        print(f"  {name}: {weight:.2%}")
    
    # 5. 保存日志
    log_path = os.path.join(updater.config_path, "update_log.json")
    logs = []
    if os.path.exists(log_path):
        with open(log_path) as f:
            logs = json.load(f)
    
    logs.append({
        "timestamp": result.timestamp,
        "skills_count": summary['skills_count'],
        "strategies_count": summary['strategies_count'],
        "confidence": result.total_confidence,
        "top_weights": dict(sorted_weights[:5])
    })
    
    # 只保留最近100条
    logs = logs[-100:]
    
    with open(log_path, "w") as f:
        json.dump(logs, f, indent=2)
    
    print(f"\n日志已保存到: {log_path}")
    print(f"[{datetime.now().isoformat()}] 权重更新完成!")

if __name__ == "__main__":
    asyncio.run(main())
