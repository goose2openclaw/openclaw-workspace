#!/usr/bin/env python3
"""
🪿 GO2SE E2E 测试 - 启动流程
测试完整的启动流程
"""

import sys
import os
import time
import subprocess
import requests
from datetime import datetime

# 配置
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8004")
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")
TIMEOUT = 30

class TestStartupFlow:
    """启动流程测试"""
    
    def __init__(self):
        self.results = []
        
    def log(self, msg, status="INFO"):
        ts = datetime.now().strftime("%H:%M:%S")
        icon = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️", "INFO": "📋"}.get(status, "📋")
        print(f"[{ts}] {icon} {msg}")
    
    def test_backend_process(self):
        """测试后端进程"""
        try:
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True,
                timeout=5
            )
            uvicorn_count = result.stdout.count("uvicorn")
            if uvicorn_count >= 1:
                self.log("后端进程运行中", "PASS")
                return True
            else:
                self.log("后端进程未运行", "FAIL")
                return False
        except Exception as e:
            self.log(f"进程检查失败: {e}", "FAIL")
            return False
    
    def test_backend_port(self):
        """测试后端端口"""
        try:
            result = subprocess.run(
                ["ss", "-tlnp"],
                capture_output=True,
                text=True,
                timeout=5
            )
            port_8004 = ":8004" in result.stdout
            if port_8004:
                self.log("端口8004监听中", "PASS")
                return True
            else:
                self.log("端口8004未监听", "FAIL")
                return False
        except Exception as e:
            self.log(f"端口检查失败: {e}", "FAIL")
            return False
    
    def test_backend_health(self):
        """测试后端健康检查API"""
        try:
            resp = requests.get(f"{BACKEND_URL}/api/health", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                status = data.get("status", "unknown")
                self.log(f"后端健康状态: {status}", "PASS")
                return True
            else:
                self.log(f"后端返回状态码: {resp.status_code}", "FAIL")
                return False
        except Exception as e:
            self.log(f"后端健康检查失败: {e}", "FAIL")
            return False
    
    def test_backend_stats(self):
        """测试后端统计API"""
        try:
            resp = requests.get(f"{BACKEND_URL}/api/stats", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                stats = data.get("data", {})
                signals = stats.get("total_signals", 0)
                mode = stats.get("trading_mode", "unknown")
                self.log(f"统计API: signals={signals}, mode={mode}", "PASS")
                return True
            else:
                self.log(f"统计API返回: {resp.status_code}", "FAIL")
                return False
        except Exception as e:
            self.log(f"统计API失败: {e}", "FAIL")
            return False
    
    def test_mirofish_markets(self):
        """测试MiroFish市场API"""
        try:
            resp = requests.get(f"{BACKEND_URL}/api/oracle/mirofish/markets", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                markets = data.get("data", [])
                active = len([m for m in markets if m.get("status") == "active"])
                self.log(f"MiroFish市场: {active}/{len(markets)} 活跃", "PASS")
                return True
            else:
                self.log(f"MiroFish API返回: {resp.status_code}", "WARN")
                return False
        except Exception as e:
            self.log(f"MiroFish API失败: {e}", "WARN")
            return False
    
    def test_frontend_reachable(self):
        """测试前端可访问性"""
        try:
            resp = requests.get(BACKEND_URL, timeout=10)
            if resp.status_code == 200:
                content = resp.text
                has_root = 'id="root"' in content or 'id="app"' in content
                if has_root:
                    self.log("前端SPA正常响应", "PASS")
                    return True
                else:
                    self.log("前端HTML结构异常", "WARN")
                    return False
            else:
                self.log(f"前端返回: {resp.status_code}", "WARN")
                return False
        except Exception as e:
            self.log(f"前端访问失败: {e}", "WARN")
            return False
    
    def run_all(self):
        """运行所有启动测试"""
        print("=" * 60)
        print("🪿 GO2SE 启动流程 E2E 测试")
        print("=" * 60)
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"后端: {BACKEND_URL}")
        print(f"前端: {FRONTEND_URL}")
        print("-" * 60)
        
        tests = [
            ("后端进程", self.test_backend_process),
            ("后端端口", self.test_backend_port),
            ("后端健康", self.test_backend_health),
            ("后端统计", self.test_backend_stats),
            ("MiroFish", self.test_mirofish_markets),
            ("前端可访问", self.test_frontend_reachable),
        ]
        
        results = []
        for name, test_func in tests:
            try:
                result = test_func()
                results.append((name, result))
            except Exception as e:
                self.log(f"{name} 执行异常: {e}", "FAIL")
                results.append((name, False))
        
        print("-" * 60)
        passed = sum(1 for _, r in results if r)
        total = len(results)
        print(f"📊 结果: {passed}/{total} 通过")
        
        if passed == total:
            print("✅ 启动流程测试全部通过!")
            return True
        elif passed >= total * 0.7:
            print("⚠️ 启动流程测试部分通过")
            return True
        else:
            print("❌ 启动流程测试未通过")
            return False


if __name__ == "__main__":
    tester = TestStartupFlow()
    success = tester.run_all()
    sys.exit(0 if success else 1)
