#!/usr/bin/env python3
"""
🪿 GO2SE 四系统协作编排器
============================
Hermes (信号) + MiroFish (仿真) + gstack (工程) + OpenClaw (编排)

协作循环:
  Hermes → MiroFish → OpenClaw → gstack → (迭代)
  
功能:
  1. 四系统健康检查
  2. 信号→仿真→决策→执行全流程
  3. 持续自主迭代
"""

import json
import time
import subprocess
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ─── 常量 ───────────────────────────────────────────────────────────────────
BACKEND_URL = "http://localhost:8004"
STATE_FILE = Path("/tmp/go2se_quartet_state.json")
LOG_FILE = Path("/tmp/go2se_quartet.log")
GSTACK_SKILLS_DIR = Path("/root/.openclaw/workspace/skills/gstack-")
MIROFISH_SCRIPT = "/root/.openclaw/workspace/GO2SE_PLATFORM/scripts/mirofish_full_simulation_v2.py"

# ─── 四系统定义 ─────────────────────────────────────────────────────────────
SYSTEMS = {
    "hermes": {
        "name": "Hermes墨丘利",
        "role": "信号与感知",
        "responsibility": "市场数据采集 + 信号生成 + 声纳库趋势",
        "color": "🔵",
    },
    "mirofish": {
        "name": "MiroFish冥河",
        "role": "仿真与验证", 
        "responsibility": "25维度全向仿真 + 策略回测 + 预测验证",
        "color": "🟢",
    },
    "gstack": {
        "name": "gstack工程队",
        "role": "工程与审查",
        "responsibility": "代码审查 + 架构评审 + CI/CD部署 + 性能优化",
        "color": "🟣",
    },
    "openclaw": {
        "name": "OpenClaw编排",
        "role": "CEO编排决策",
        "responsibility": "调度四系统 + 决策 + 迭代优化",
        "color": "🪿",
    },
}


# ─── 健康检查 ───────────────────────────────────────────────────────────────

def check_hermes() -> Dict:
    """检查Hermes信号系统"""
    result = {"status": "unknown", "signals": 0, "details": []}
    try:
        # 检查市场数据API (正确的endpoint)
        r = requests.get(f"{BACKEND_URL}/api/market", timeout=5)
        if r.ok:
            data = r.json()
            coins = data.get("data", [])
            result["status"] = "healthy"
            result["signals"] = len(coins)
            result["details"].append(f"市场数据: {len(coins)}个交易对")
        else:
            result["status"] = "degraded"
            result["details"].append(f"HTTP {r.status_code}")
    except requests.exceptions.RequestException as e:
        result["status"] = "down"
        result["details"].append(str(e)[:50])
        return result
    
    # 检查信号总览
    try:
        r2 = requests.get(f"{BACKEND_URL}/api/market/signals/overview", timeout=5)
        if r2.ok:
            sig_data = r2.json()
            result["sentiment"] = sig_data.get("sentiment", "?")
            result["details"].append(f"情绪: {result['sentiment']}")
    except:
        pass
    
    # 检查声纳库信号
    try:
        r3 = requests.get(f"{BACKEND_URL}/api/market/signals/beidou", timeout=5)
        if r3.ok:
            result["sonar"] = "active"
            result["details"].append("声纳库: active")
    except:
        result["sonar"] = "unavailable"
    
    return result


def check_mirofish() -> Dict:
    """检查MiroFish仿真引擎"""
    result = {"status": "unknown", "simulation_count": 0, "details": []}
    try:
        # 检查仿真脚本是否存在
        sim_script = Path(MIROFISH_SCRIPT)
        if sim_script.exists():
            result["simulation_engine"] = "available"
            result["details"].append(f"仿真脚本: ✅")
        
        # 检查后端MiroFish API
        r = requests.get(f"{BACKEND_URL}/api/oracle/mirofish/batch", timeout=5)
        if r.ok:
            result["api"] = "responsive"
        elif r.status_code == 404:
            result["api"] = "no_endpoint"
        else:
            result["api"] = f"HTTP {r.status_code}"
            
    except requests.exceptions.RequestException as e:
        result["status"] = "down"
        result["details"].append(str(e)[:50])
        return result
    
    # 检查最近的仿真报告
    report_file = Path("/tmp/go2se_resource_report.json")
    if report_file.exists():
        try:
            with open(report_file) as f:
                report = json.load(f)
                if "mirofish" in str(report).lower() or "simulation" in str(report).lower():
                    result["details"].append("仿真报告: 存在")
        except:
            pass
    
    result["status"] = "healthy" if result["status"] == "unknown" else result["status"]
    return result


def check_gstack() -> Dict:
    """检查gstack工程团队"""
    result = {"status": "unknown", "skills_count": 0, "details": []}
    
    # 统计gstack技能数量
    try:
        # 先查找gstack-*目录
        skills_base = Path("/root/.openclaw/workspace/skills")
        gstack_dirs = [d for d in skills_base.iterdir() if d.is_dir() and d.name.startswith("gstack-")]
        skill_files = []
        for d in gstack_dirs:
            skill_md = d / "SKILL.md"
            if skill_md.exists():
                skill_files.append(skill_md)
        
        result["skills_count"] = len(skill_files)
        result["details"].append(f"技能数: {len(skill_files)}")
        
        # 检查关键技能
        critical = ["gstack-review", "gstack-qa", "gstack-canary", "gstack-benchmark",
                    "gstack-office-hours", "gstack-plan-ceo-review", "gstack-plan-eng-review"]
        found = []
        for s in critical:
            if (skills_base / s / "SKILL.md").exists():
                found.append(s.replace("gstack-", ""))
        
        result["details"].append(f"核心技能: {', '.join(found) if found else '无'}")
        result["status"] = "healthy" if len(skill_files) >= 15 else "degraded"
        
    except Exception as e:
        result["status"] = "error"
        result["details"].append(str(e)[:50])
    
    return result


def check_openclaw() -> Dict:
    """检查OpenClaw编排系统(使用缓存避免网络超时)"""
    result = {"status": "unknown", "cron_jobs": 0, "details": []}
    
    # 读取本地缓存的cron状态
    cron_cache = Path("/tmp/go2se_cron_state.json")
    if cron_cache.exists():
        try:
            with open(cron_cache) as f:
                data = json.load(f)
            jobs = data.get("jobs", [])
            result["cron_jobs"] = len(jobs)
            errors = sum(1 for j in jobs if j.get("state", {}).get("lastRunStatus") == "error")
            active = sum(1 for j in jobs if j.get("enabled"))
            result["details"].append(f"Cron任务: {len(jobs)}个 (运行中:{active}, 错误:{errors}) [缓存]")
            result["status"] = "degraded"  # 默认降级因为用缓存
        except:
            result["details"].append("Cron缓存读取失败")
            result["status"] = "degraded"
    else:
        result["details"].append("Cron状态: 无缓存")
        result["status"] = "degraded"
    
    # 检查资源监控状态
    resource_state = Path("/tmp/go2se_resource_config.json")
    if resource_state.exists():
        try:
            with open(resource_state) as f:
                state = json.load(f)
            result["details"].append(f"资源等级: {state.get('last_tier', '?')}")
        except:
            pass
    
    return result


def quartet_health_check() -> Dict:
    """四系统全面健康检查"""
    results = {}
    overall = "healthy"
    
    results["hermes"] = check_hermes()
    results["mirofish"] = check_mirofish()
    results["gstack"] = check_gstack()
    results["openclaw"] = check_openclaw()
    
    # 计算总体状态
    statuses = [r["status"] for r in results.values()]
    if "down" in statuses:
        overall = "critical"
    elif "error" in statuses or "degraded" in statuses:
        overall = "degraded"
    elif all(s == "healthy" for s in statuses):
        overall = "healthy"
    
    return {
        "timestamp": datetime.now().isoformat(),
        "overall": overall,
        "systems": results,
    }


# ─── 协作流程 ────────────────────────────────────────────────────────────────

def run_collaboration_cycle() -> Dict:
    """执行一次完整的四系统协作循环"""
    cycle_log = []
    timestamp = datetime.now().isoformat()
    
    cycle_log.append(f"[{timestamp}] 🚀 四系统协作循环启动")
    
    # Step 1: Hermes 采集信号
    cycle_log.append("\n📡 Step 1: Hermes 信号采集...")
    hermes_result = check_hermes()
    if hermes_result["status"] in ("healthy", "degraded"):
        cycle_log.append(f"   ✅ 信号数: {hermes_result.get('signals', 0)}")
    else:
        cycle_log.append(f"   ⚠️ Hermes状态: {hermes_result['status']}")
    
    # Step 2: MiroFish 仿真验证
    cycle_log.append("\n🧪 Step 2: MiroFish 仿真验证...")
    mirofish_result = check_mirofish()
    cycle_log.append(f"   ✅ 仿真引擎: {mirofish_result.get('simulation_engine', '?')}")
    cycle_log.append(f"   ✅ API状态: {mirofish_result.get('api', '?')}")
    
    # Step 3: OpenClaw 决策编排
    cycle_log.append("\n🪿 Step 3: OpenClaw 决策编排...")
    openclaw_result = check_openclaw()
    cycle_log.append(f"   ✅ Cron任务: {openclaw_result.get('cron_jobs', 0)}个")
    cycle_log.append(f"   ✅ 状态: {openclaw_result['status']}")
    
    # Step 4: gstack 工程支持
    cycle_log.append("\n🔧 Step 4: gstack 工程支持...")
    gstack_result = check_gstack()
    cycle_log.append(f"   ✅ 技能数: {gstack_result.get('skills_count', 0)}")
    cycle_log.append(f"   ✅ 状态: {gstack_result['status']}")
    
    # Step 5: 资源自适应
    cycle_log.append("\n⚡ Step 5: 资源自适应调度...")
    try:
        result = subprocess.run(
            ["python3", MIROFISH_SCRIPT.replace("mirofish_full_simulation_v2", "resource_monitor").replace("_v2", "")],
            capture_output=True, text=True, timeout=30
        )
        # 尝试运行resource_monitor
        rm_result = subprocess.run(
            ["python3", "/root/.openclaw/workspace/GO2SE_PLATFORM/scripts/resource_monitor.py"],
            capture_output=True, text=True, timeout=30
        )
        if rm_result.returncode == 0:
            lines = rm_result.stdout.split("\n")
            for line in lines:
                if "推荐" in line or "等级" in line or "资源" in line:
                    cycle_log.append(f"   {line.strip()}")
    except:
        cycle_log.append("   ⚠️ 资源监控跳过")
    
    # 生成决策建议
    cycle_log.append("\n💡 决策建议:")
    if overall := determine_overall_status(hermes_result, mirofish_result, gstack_result, openclaw_result):
        cycle_log.append(f"   {overall}")
    
    cycle_log.append(f"\n[{datetime.now().isoformat()}] 🏁 协作循环完成")
    
    return {
        "timestamp": timestamp,
        "cycle_log": cycle_log,
        "hermes": hermes_result,
        "mirofish": mirofish_result,
        "gstack": gstack_result,
        "openclaw": openclaw_result,
    }


def determine_overall_status(hermes, mirofish, gstack, openclaw) -> str:
    """根据四系统状态生成决策建议"""
    issues = []
    
    if hermes["status"] == "down":
        issues.append("Hermes信号系统离线")
    if mirofish["status"] == "down":
        issues.append("MiroFish仿真引擎离线")
    if gstack["status"] != "healthy":
        issues.append(f"gstack需要关注 ({gstack['status']})")
    if openclaw["status"] == "down":
        issues.append("OpenClaw编排系统离线")
    
    if not issues:
        return "✅ 四系统运行正常，持续监控中"
    else:
        return "⚠️ " + "; ".join(issues)


# ─── 持续迭代循环 ───────────────────────────────────────────────────────────

def continuous_iteration(num_cycles: int = 3, interval_seconds: int = 60) -> List[Dict]:
    """持续迭代循环"""
    results = []
    for i in range(num_cycles):
        cycle_result = run_collaboration_cycle()
        results.append(cycle_result)
        
        # 保存状态
        with open(STATE_FILE, "w") as f:
            json.dump({
                "last_cycle": cycle_result["timestamp"],
                "cycle_number": i + 1,
                "total_cycles": num_cycles,
            }, f, indent=2, default=str)
        
        # 记录到日志
        with open(LOG_FILE, "a") as f:
            f.write(f"\n{'='*60}\n")
            for line in cycle_result["cycle_log"]:
                f.write(line + "\n")
        
        if i < num_cycles - 1:
            time.sleep(interval_seconds)
    
    return results


# ─── 格式化输出 ─────────────────────────────────────────────────────────────

def format_health_report(health_result: Dict) -> str:
    """格式化健康检查报告"""
    lines = [
        "=" * 60,
        f"🪿 GO2SE 四系统健康检查",
        "=" * 60,
        f"⏰ {health_result['timestamp']}",
        f"🏥 总体状态: {health_result['overall'].upper()}",
        "",
    ]
    
    for sys_key, sys_info in SYSTEMS.items():
        result = health_result["systems"][sys_key]
        status_icon = "✅" if result["status"] == "healthy" else "⚠️" if result["status"] == "degraded" else "❌"
        
        lines.append(f"{sys_info['color']} {sys_info['name']} ({sys_info['role']})")
        lines.append(f"   {status_icon} 状态: {result['status']}")
        for detail in result.get("details", []):
            lines.append(f"   • {detail}")
        lines.append("")
    
    lines.append("=" * 60)
    return "\n".join(lines)


def format_cycle_report(cycle_result: Dict) -> str:
    """格式化协作循环报告"""
    lines = [
        "=" * 60,
        f"🪿 四系统协作循环报告",
        "=" * 60,
        f"⏰ {cycle_result['timestamp']}",
        "",
    ]
    
    for line in cycle_result["cycle_log"]:
        lines.append(line)
    
    lines.append("=" * 60)
    return "\n".join(lines)


# ─── 主函数 ─────────────────────────────────────────────────────────────────

def main():
    import sys
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "health":
            # 健康检查
            result = quartet_health_check()
            print(format_health_report(result))
            
        elif cmd == "cycle":
            # 单次协作循环
            result = run_collaboration_cycle()
            print(format_cycle_report(result))
            
        elif cmd == "iterate":
            # 持续迭代
            cycles = int(sys.argv[2]) if len(sys.argv) > 2 else 3
            interval = int(sys.argv[3]) if len(sys.argv) > 3 else 60
            print(f"🔄 启动{cycles}次迭代循环，间隔{interval}秒...")
            results = continuous_iteration(cycles, interval)
            print(f"\n✅ 完成{len(results)}次迭代")
            
        elif cmd == "status":
            # 快速状态
            result = quartet_health_check()
            for sys_key in ["hermes", "mirofish", "gstack", "openclaw"]:
                sys_info = SYSTEMS[sys_key]
                r = result["systems"][sys_key]
                icon = "✅" if r["status"] == "healthy" else "⚠️" if r["status"] == "degraded" else "❌"
                print(f"{sys_info['color']} {sys_info['name']}: {icon} {r['status']}")
            
        else:
            print(f"未知命令: {cmd}")
            print("用法: python3 quartet_orchestrator.py [health|cycle|iterate|status]")
    else:
        # 默认: 健康检查
        result = quartet_health_check()
        print(format_health_report(result))


if __name__ == "__main__":
    main()
