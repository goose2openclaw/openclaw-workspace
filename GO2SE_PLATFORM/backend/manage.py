#!/usr/bin/env python3
"""
GO2SE 后台管理脚本
==================
启动、停止、重启、状态检查
"""
import os
import sys
import signal
import time
import requests
import subprocess
from datetime import datetime


# 配置
BACKEND_DIR = "/root/.openclaw/workspace/GO2SE_PLATFORM/backend"
PORT = 8004
HOST = "0.0.0.0"
PID_FILE = "/tmp/go2se_backend.pid"
LOG_FILE = "/tmp/go2se_backend.log"


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'


def log(msg, color=Colors.RESET):
    print(f"{color}[{datetime.now().strftime('%H:%M:%S')}] {msg}{Colors.RESET}")


def get_pid():
    """获取PID"""
    if os.path.exists(PID_FILE):
        with open(PID_FILE) as f:
            return int(f.read().strip())
    return None


def is_running(pid):
    """检查进程是否运行"""
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def check_health():
    """检查健康状态"""
    try:
        resp = requests.get(f"http://localhost:{PORT}/api/stats", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            log(f"✅ Backend健康: v{data.get('version')} | 信号:{data.get('total_signals')} | 模式:{data.get('trading_mode')}", Colors.GREEN)
            return True
    except Exception as e:
        log(f"❌ Backend无响应: {e}", Colors.RED)
    return False


def start():
    """启动后端"""
    pid = get_pid()
    if pid and is_running(pid):
        log(f"⚠️  Backend已运行 (PID: {pid})", Colors.YELLOW)
        check_health()
        return

    log("🚀 启动Backend...", Colors.BLUE)
    
    # 切换到后端目录
    os.chdir(BACKEND_DIR)
    
    # 后台启动
    cmd = [
        sys.executable, "-m", "uvicorn",
        "app.main:app",
        "--host", HOST,
        "--port", str(PORT),
        "--workers", "2"
    ]
    
    with open(LOG_FILE, "w") as f:
        proc = subprocess.Popen(cmd, stdout=f, stderr=f)
    
    # 保存PID
    with open(PID_FILE, "w") as f:
        f.write(str(proc.pid))
    
    # 等待启动
    time.sleep(3)
    
    if check_health():
        log(f"✅ Backend启动成功 (PID: {proc.pid})", Colors.GREEN)
    else:
        log("❌ Backend启动失败 - 查看日志:", Colors.RED)
        log(f"   tail -f {LOG_FILE}", Colors.YELLOW)


def stop():
    """停止后端"""
    pid = get_pid()
    if not pid or not is_running(pid):
        log("⚠️  Backend未运行", Colors.YELLOW)
        return
    
    log(f"🛑 停止Backend (PID: {pid})...", Colors.BLUE)
    
    try:
        os.kill(pid, signal.SIGTERM)
        time.sleep(2)
        
        if not is_running(pid):
            log("✅ Backend已停止", Colors.GREEN)
        else:
            os.kill(pid, signal.SIGKILL)
            log("✅ Backend强制终止", Colors.GREEN)
    except Exception as e:
        log(f"❌ 停止失败: {e}", Colors.RED)
    
    # 删除PID文件
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)


def restart():
    """重启后端"""
    log("🔄 重启Backend...", Colors.BLUE)
    stop()
    time.sleep(1)
    start()


def status():
    """状态检查"""
    pid = get_pid()
    if not pid or not is_running(pid):
        log("⚠️  Backend未运行", Colors.YELLOW)
        return
    
    log(f"Backend运行中 (PID: {pid})", Colors.BLUE)
    check_health()


def logs(lines=20):
    """查看日志"""
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            content = f.readlines()
            for line in content[-lines:]:
                print(line.rstrip())
    else:
        log(f"日志文件不存在: {LOG_FILE}", Colors.YELLOW)


def main():
    if len(sys.argv) < 2:
        print(f"""
🪿 GO2SE 后台管理脚本
====================

用法: python manage.py <命令>

命令:
  start     启动Backend
  stop      停止Backend
  restart   重启Backend
  status    检查状态
  health    健康检查
  logs      查看日志 (默认20行)
  logs N    查看最近N行日志

示例:
  python manage.py start
  python manage.py restart
  python manage.py logs 50
""")
        return

    cmd = sys.argv[1].lower()
    
    if cmd == "start":
        start()
    elif cmd == "stop":
        stop()
    elif cmd == "restart":
        restart()
    elif cmd == "status":
        status()
    elif cmd == "health":
        check_health()
    elif cmd == "logs":
        lines = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        logs(lines)
    else:
        log(f"未知命令: {cmd}", Colors.RED)


if __name__ == "__main__":
    main()
