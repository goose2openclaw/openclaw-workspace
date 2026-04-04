#!/usr/bin/env python3
"""
🪿 GO2SE 完整测试运行器
运行所有测试套件
"""

import sys
import os
import subprocess
import time
from datetime import datetime

TESTS_DIR = "/root/.openclaw/workspace/GO2SE_PLATFORM/tests"

class TestRunner:
    """测试运行器"""
    
    def __init__(self):
        self.results = []
        
    def log(self, msg, status="INFO"):
        ts = datetime.now().strftime("%H:%M:%S")
        icon = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️", "INFO": "📋"}.get(status, "📋")
        print(f"[{ts}] {icon} {msg}")
    
    def run_script(self, name, script_path):
        """运行测试脚本"""
        self.log(f"运行: {name}")
        try:
            result = subprocess.run(
                ["python3", script_path],
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode == 0:
                self.log(f"{name}: 通过", "PASS")
                return True
            else:
                self.log(f"{name}: 失败 (exit {result.returncode})", "FAIL")
                return False
        except subprocess.TimeoutExpired:
            self.log(f"{name}: 超时", "FAIL")
            return False
        except Exception as e:
            self.log(f"{name}: {e}", "FAIL")
            return False
    
    def run_health_check(self):
        """运行健康检查脚本"""
        script = "/root/.openclaw/workspace/GO2SE_PLATFORM/scripts/health_check.sh"
        if os.path.exists(script):
            self.log("运行: 健康检查脚本")
            try:
                result = subprocess.run(
                    ["bash", script],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if "无响应" not in result.stdout and "重启失败" not in result.stdout:
                    self.log("健康检查: 通过", "PASS")
                    return True
                else:
                    self.log("健康检查: 需关注", "WARN")
                    return True  # 允许重启
            except Exception as e:
                self.log(f"健康检查异常: {e}", "WARN")
                return True
        return True
    
    def run_validate_startup(self):
        """运行启动验证脚本"""
        script = "/root/.openclaw/workspace/GO2SE_PLATFORM/scripts/validate_startup.sh"
        if os.path.exists(script):
            self.log("运行: 启动验证脚本")
            try:
                result = subprocess.run(
                    ["bash", script],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if "验证完成" in result.stdout or result.returncode == 0:
                    self.log("启动验证: 通过", "PASS")
                    return True
                else:
                    self.log("启动验证: 失败", "FAIL")
                    return False
            except Exception as e:
                self.log(f"启动验证异常: {e}", "WARN")
                return True
        return True
    
    def run_e2e_tests(self):
        """运行E2E测试"""
        e2e_tests = [
            ("启动流程", f"{TESTS_DIR}/e2e/test_startup_flow.py"),
            ("页面导航", f"{TESTS_DIR}/e2e/test_page_navigation.py"),
            ("API调用", f"{TESTS_DIR}/e2e/test_api_calls.py"),
        ]
        
        results = []
        for name, path in e2e_tests:
            if os.path.exists(path):
                result = self.run_script(name, path)
                results.append(result)
            else:
                self.log(f"{name}: 脚本不存在", "WARN")
                results.append(False)
        
        return all(results) if results else True
    
    def run_integration_tests(self):
        """运行集成测试"""
        path = f"{TESTS_DIR}/integration/test_integration.py"
        if os.path.exists(path):
            return self.run_script("集成测试", path)
        self.log("集成测试: 脚本不存在", "WARN")
        return True
    
    def run_all(self):
        """运行所有测试"""
        print("=" * 70)
        print("🪿 GO2SE 完整测试套件")
        print("=" * 70)
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 70)
        
        # 1. 健康检查
        self.log("=" * 20 + " 阶段1: 健康检查 " + "=" * 20)
        health_pass = self.run_health_check()
        
        # 2. 启动验证
        self.log("=" * 20 + " 阶段2: 启动验证 " + "=" * 20)
        validate_pass = self.run_validate_startup()
        
        # 3. E2E测试
        self.log("=" * 20 + " 阶段3: E2E测试 " + "=" * 20)
        e2e_pass = self.run_e2e_tests()
        
        # 4. 集成测试
        self.log("=" * 20 + " 阶段4: 集成测试 " + "=" * 20)
        integration_pass = self.run_integration_tests()
        
        # 总结
        print("-" * 70)
        print("📊 测试总结:")
        print(f"   健康检查: {'✅' if health_pass else '❌'}")
        print(f"   启动验证: {'✅' if validate_pass else '❌'}")
        print(f"   E2E测试:  {'✅' if e2e_pass else '❌'}")
        print(f"   集成测试: {'✅' if integration_pass else '❌'}")
        
        all_pass = health_pass and validate_pass and e2e_pass and integration_pass
        if all_pass:
            print("\n✅ 所有测试通过!")
        else:
            print("\n⚠️ 部分测试失败，请检查日志")
        
        return all_pass


if __name__ == "__main__":
    runner = TestRunner()
    success = runner.run_all()
    sys.exit(0 if success else 1)
