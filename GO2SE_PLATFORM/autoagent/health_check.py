#!/usr/bin/env python3
"""
🪿 GO2SE AutoAgent - Cron版
每分钟执行一次健康检查，自动恢复
"""

import os
import sys
import json
import time
import subprocess
import requests
from datetime import datetime

API_KEY = "GO2SE_e083a64d891b45089d6f37acb440435eba401313a1695711"
API_BASE = "http://localhost:8004"
STATUS_FILE = "/root/.openclaw/workspace/GO2SE_PLATFORM/autoagent/status.json"

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def check_backend():
    """检查Backend"""
    try:
        r = requests.get(f"{API_BASE}/api/stats", timeout=5)
        if r.status_code == 200:
            return True, r.json()
    except:
        pass
    return False, None

def check_frontend():
    """检查Frontend"""
    try:
        r = requests.get("http://localhost:8010/", timeout=5)
        return r.status_code == 200
    except:
        return False

def restart_backend():
    """重启Backend"""
    log("🔧 重启Backend...")
    os.system("pkill -f 'uvicorn app.main:app' 2>/dev/null")
    os.system("cd /root/.openclaw/workspace/GO2SE_PLATFORM/backend && "
              "nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8004 &>/dev/null &")
    time.sleep(3)

def restart_frontend():
    """重启Frontend"""
    log("🔧 重启Frontend...")
    os.system("pkill -f 'http.server 8010' 2>/dev/null")
    os.system("cd /root/.openclaw/workspace/GO2SE_PLATFORM/versions/v10 && "
              "nohup python3 -m http.server 8010 &>/dev/null &")
    time.sleep(2)

def run_mirofish():
    """运行MiroFish仿真"""
    log("🔬 运行MiroFish仿真...")
    try:
        result = subprocess.run(
            ["python3", "scripts/mirofish_full_simulation_v2.py"],
            cwd="/root/.openclaw/workspace/GO2SE_PLATFORM",
            capture_output=True,
            text=True,
            timeout=60
        )
        output = result.stdout + result.stderr
        score = 0.0
        for line in output.split('\n'):
            if '综合评分' in line:
                try:
                    parts = line.split(':')
                    score = float(''.join(filter(lambda x: x.isdigit() or x=='.', parts[-1])))
                except:
                    pass
        return score
    except Exception as e:
        log(f"❌ 仿真失败: {e}")
        return 0.0

def main():
    log("🪿 GO2SE AutoAgent 检查")
    
    # 检查Backend
    backend_ok, backend_data = check_backend()
    if not backend_ok:
        restart_backend()
        backend_ok, backend_data = check_backend()
    
    # 检查Frontend
    frontend_ok = check_frontend()
    if not frontend_ok:
        restart_frontend()
        frontend_ok = check_frontend()
    
    # 获取评分
    score = 0.0
    if backend_ok:
        score = run_mirofish()
    
    # 保存状态
    status = {
        "timestamp": datetime.now().isoformat(),
        "backend": backend_ok,
        "frontend": frontend_ok,
        "mirofish_score": score,
        "version": backend_data.get("data", {}).get("version", "unknown") if backend_data else "unknown",
        "signals": backend_data.get("data", {}).get("total_signals", 0) if backend_data else 0
    }
    
    with open(STATUS_FILE, 'w') as f:
        json.dump(status, f, indent=2)
    
    # 输出结果
    log(f"🏥 Backend: {'✅' if backend_ok else '❌'} | "
        f"Frontend: {'✅' if frontend_ok else '❌'} | "
        f"MiroFish: {score:.1f}")
    
    if score > 0:
        log(f"📊 系统评分: {score}/100 {'✅' if score >= 85 else '⚠️'}")

if __name__ == "__main__":
    main()