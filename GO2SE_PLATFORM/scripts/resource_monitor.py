#!/usr/bin/env python3
"""
🪿 GO2SE 资源监控 + 自适应调度模块
功能:
  1. 监控 CPU/内存/磁盘/网络
  2. 根据资源紧张程度自动调整Cron间隔
  3. 5分钟 → 15分钟 → 30分钟 → 60分钟 (阶梯式降频)
  4. 资源恢复时自动回升频次
"""

import psutil
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

CONFIG_FILE = Path("/tmp/go2se_resource_config.json")
DEFAULT_INTERVAL = 5   # 默认5分钟
MAX_INTERVAL = 60     # 最长60分钟

# 资源阈值配置
THRESHOLDS = {
    "memory_percent": 85,      # 内存85% → 降频
    "memory_available_mb": 2048,  # 可用内存<2GB → 降频
    "cpu_percent": 80,          # CPU 80% → 降频
    "disk_percent": 90,         # 磁盘90% → 降频
    "swap_percent": 80,         # Swap 80% → 警告
}

# 降频阶梯
FREQUENCY_TIERS = [
    {"name": "normal",   "interval": 5,  "memory_threshold": 70,  "available_mb": 4096},
    {"name": "light",    "interval": 15, "memory_threshold": 85,  "available_mb": 2048},
    {"name": "moderate", "interval": 30, "memory_threshold": 90,  "available_mb": 1024},
    {"name": "severe",   "interval": 60, "memory_threshold": 95,  "available_mb": 512},
]

def get_resource_status():
    """获取当前资源状态"""
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    disk = psutil.disk_usage('/')
    cpu = psutil.cpu_percent(interval=1)
    
    return {
        "timestamp": datetime.now().isoformat(),
        "memory_percent": mem.percent,
        "memory_available_mb": mem.available / (1024 * 1024),
        "memory_total_gb": mem.total / (1024 * 1024 * 1024),
        "swap_percent": swap.percent,
        "cpu_percent": cpu,
        "disk_percent": disk.percent,
        "disk_free_gb": disk.free / (1024 * 1024 * 1024),
    }

def calculate_tier(status):
    """根据资源状态计算当前频次等级"""
    for tier in FREQUENCY_TIERS:
        # 检查所有指标
        if (status["memory_percent"] < tier["memory_threshold"] and 
            status["memory_available_mb"] >= tier["available_mb"] and
            status["cpu_percent"] < 80):
            return tier
    return FREQUENCY_TIERS[-1]  # 最高等级

def get_recommended_interval(status):
    """获取推荐的Cron间隔(分钟)"""
    tier = calculate_tier(status)
    return tier["interval"]

def check_cron_jobs(current_interval):
    """检查并更新Cron任务的间隔"""
    try:
        result = subprocess.run(
            ["openclaw", "cron", "list", "--json"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            return {"error": "无法获取Cron列表", "details": result.stderr}
        
        try:
            data = json.loads(result.stdout)
            crons = data.get("jobs", [])
        except json.JSONDecodeError:
            return {"error": "Cron JSON解析失败", "raw": result.stdout[:500]}
        
        updated = []
        for cron in crons:
            cron_id = cron.get("id")
            name = cron.get("name", "unknown")
            schedule = cron.get("schedule", {})
            
            # 找出5分钟周期的任务 (300000ms)
            if schedule.get("kind") == "every":
                interval_ms = schedule.get("everyMs", 0)
                if interval_ms == 300000:  # 5分钟 = 300000ms
                    new_interval = current_interval * 60 * 1000  # 转换为ms
                    # 更新Cron
                    update_result = subprocess.run(
                        ["openclaw", "cron", "edit", cron_id,
                         "--every", f"{current_interval}m"],
                        capture_output=True, text=True, timeout=15
                    )
                    if update_result.returncode == 0:
                        updated.append({
                            "name": name,
                            "from": "5m",
                            "to": f"{current_interval}m"
                        })
                    else:
                        updated.append({
                            "name": name,
                            "from": "5m",
                            "to": f"{current_interval}m (失败: {update_result.stderr[:100]})"
                        })
        
        return {"updated": updated}
    
    except subprocess.TimeoutExpired:
        return {"error": "Cron命令超时"}
    except Exception as e:
        return {"error": str(e)}

def load_state():
    """加载上次状态"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                return json.load(f)
        except:
            pass
    return {"last_interval": DEFAULT_INTERVAL, "last_tier": "normal"}

def save_state(interval, tier):
    """保存当前状态"""
    with open(CONFIG_FILE, "w") as f:
        json.dump({"last_interval": interval, "last_tier": tier, "updated": datetime.now().isoformat()}, f)

def restore_default_intervals():
    """恢复所有Cron到默认5分钟"""
    try:
        result = subprocess.run(
            ["openclaw", "cron", "list", "--json"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode != 0:
            return {"error": "无法获取Cron列表"}
        
        data = json.loads(result.stdout)
        crons = data.get("jobs", [])
        restored = []
        
        for cron in crons:
            cron_id = cron.get("id")
            name = cron.get("name", "unknown")
            schedule = cron.get("schedule", {})
            
            if schedule.get("kind") == "every":
                interval_ms = schedule.get("everyMs", 0)
                # 恢复任何非5分钟的间隔
                if interval_ms != 300000:
                    update_result = subprocess.run(
                        ["openclaw", "cron", "edit", cron_id, "--every", "5m"],
                        capture_output=True, text=True, timeout=15
                    )
                    if update_result.returncode == 0:
                        restored.append({"name": name, "to": "5m"})
        
        return {"restored": restored}
    except Exception as e:
        return {"error": str(e)}

def analyze_and_adjust():
    """主分析 + 调整逻辑"""
    status = get_resource_status()
    recommended = get_recommended_interval(status)
    tier = calculate_tier(status)
    state = load_state()
    
    result = {
        "status": status,
        "tier": tier["name"],
        "recommended_interval_minutes": recommended,
        "current_default": DEFAULT_INTERVAL,
        "needs_adjustment": recommended != state["last_interval"],
        "cron_updates": [],
        "was_adjusted": state["last_interval"] != DEFAULT_INTERVAL,
        "timestamp": datetime.now().isoformat()
    }
    
    # 如果当前推荐间隔不同于上次记录的间隔，需要调整
    if result["needs_adjustment"]:
        if recommended > state["last_interval"]:
            # 资源更紧张 → 降低频次
            cron_result = check_cron_jobs(recommended)
            if "updated" in cron_result:
                result["cron_updates"] = cron_result["updated"]
            else:
                result["cron_error"] = cron_result.get("error", "未知错误")
            save_state(recommended, tier["name"])
        elif recommended < state["last_interval"]:
            # 资源恢复 → 回升频次
            restore_result = restore_default_intervals()
            if "restored" in restore_result:
                result["cron_restored"] = restore_result["restored"]
            else:
                result["cron_error"] = restore_result.get("error", "未知错误")
            save_state(DEFAULT_INTERVAL, tier["name"])
    
    return result

def format_report(result):
    """格式化输出报告"""
    s = result["status"]
    tier_emojis = {
        "normal": "🟢",
        "light": "🟡", 
        "moderate": "🟠",
        "severe": "🔴"
    }
    emoji = tier_emojis.get(result["tier"], "⚪")
    
    lines = [
        f"{'='*50}",
        f"🪿 GO2SE 资源监控报告",
        f"{'='*50}",
        f"⏰ 生成时间: {result['timestamp']}",
        f"",
        f"{emoji} 资源等级: {result['tier'].upper()}",
        f"",
        f"📊 资源使用:",
        f"  内存: {s['memory_percent']:.1f}% (可用: {s['memory_available_mb']:.0f}MB / {s['memory_total_gb']:.1f}GB)",
        f"  CPU:  {s['cpu_percent']:.1f}%",
        f"  磁盘: {s['disk_percent']:.1f}% (剩余: {s['disk_free_gb']:.1f}GB)",
        f"  Swap: {s['swap_percent']:.1f}%",
        f"",
        f"⚙️  调度建议:",
        f"  当前默认: {result['current_default']}分钟",
        f"  推荐间隔: {result['recommended_interval_minutes']}分钟",
        f"  调整需求: {'✅ 需要调整' if result['needs_adjustment'] else '❌ 无需调整'}",
    ]
    
    if result.get("cron_updates"):
        lines.append(f"")
        lines.append(f"🔄 Cron任务已更新:")
        for u in result["cron_updates"]:
            lines.append(f"  • {u['name']}: {u['from']} → {u['to']}")
    
    if result.get("cron_error"):
        lines.append(f"")
        lines.append(f"⚠️ Cron更新失败: {result['cron_error']}")
    
    lines.append(f"{'='*50}")
    return "\n".join(lines)

def main():
    result = analyze_and_adjust()
    print(format_report(result))
    
    # 保存结果到文件
    with open("/tmp/go2se_resource_report.json", "w") as f:
        json.dump(result, f, indent=2, default=str)
    
    return result

if __name__ == "__main__":
    main()
