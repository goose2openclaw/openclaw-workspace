#!/usr/bin/env python3
"""
🪿 GO2SE E2E 测试 - 页面导航
测试前端页面导航和组件渲染
"""

import sys
import os
import time
import requests
from datetime import datetime

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8004")

class TestPageNavigation:
    """页面导航测试"""
    
    def __init__(self):
        self.results = []
        self.session = requests.Session()
        
    def log(self, msg, status="INFO"):
        ts = datetime.now().strftime("%H:%M:%S")
        icon = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️", "INFO": "📋"}.get(status, "📋")
        print(f"[{ts}] {icon} {msg}")
    
    def test_root_page(self):
        """测试根页面"""
        try:
            resp = self.session.get(BACKEND_URL, timeout=10)
            if resp.status_code == 200:
                content = resp.text
                checks = {
                    "HTML根": 'id="root"' in content or 'id="app"' in content,
                    "Vite": "vite" in content.lower() or "/@vite" in content,
                    "Goose": "GO2SE" in content or "go2se" in content.lower(),
                }
                passed = sum(checks.values())
                if passed >= 2:
                    self.log(f"根页面正常 (检查: {passed}/3)", "PASS")
                    return True
                else:
                    self.log(f"根页面部分通过 (检查: {passed}/3)", "WARN")
                    return False
            else:
                self.log(f"根页面返回: {resp.status_code}", "FAIL")
                return False
        except Exception as e:
            self.log(f"根页面失败: {e}", "FAIL")
            return False
    
    def test_api_docs(self):
        """测试API文档页面"""
        try:
            resp = self.session.get(f"{BACKEND_URL}/docs", timeout=10)
            if resp.status_code == 200:
                content = resp.text
                if "swagger" in content.lower() or "openapi" in content.lower():
                    self.log("API文档可访问", "PASS")
                    return True
            self.log("API文档返回异常", "WARN")
            return False
        except Exception as e:
            self.log(f"API文档失败: {e}", "WARN")
            return False
    
    def test_health_endpoint(self):
        """测试健康端点"""
        try:
            resp = self.session.get(f"{BACKEND_URL}/api/health", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                status = data.get("status", "unknown")
                self.log(f"健康端点: {status}", "PASS")
                return True
            else:
                self.log(f"健康端点返回: {resp.status_code}", "FAIL")
                return False
        except Exception as e:
            self.log(f"健康端点失败: {e}", "FAIL")
            return False
    
    def test_stats_endpoint(self):
        """测试统计端点"""
        try:
            resp = self.session.get(f"{BACKEND_URL}/api/stats", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                stats = data.get("data", {})
                has_trading_mode = "trading_mode" in stats
                has_signals = "total_signals" in stats
                if has_trading_mode and has_signals:
                    self.log(f"统计端点正常 (mode={stats.get('trading_mode')}, signals={stats.get('total_signals')})", "PASS")
                    return True
                else:
                    self.log("统计端点字段不完整", "WARN")
                    return False
            else:
                self.log(f"统计端点返回: {resp.status_code}", "FAIL")
                return False
        except Exception as e:
            self.log(f"统计端点失败: {e}", "FAIL")
            return False
    
    def test_mirofish_endpoint(self):
        """测试MiroFish端点"""
        try:
            resp = self.session.get(f"{BACKEND_URL}/api/oracle/mirofish/markets", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                markets = data.get("data", [])
                self.log(f"MiroFish端点: {len(markets)} 市场", "PASS")
                return True
            else:
                self.log(f"MiroFish端点返回: {resp.status_code}", "WARN")
                return False
        except Exception as e:
            self.log(f"MiroFish端点失败: {e}", "WARN")
            return False
    
    def test_websocket_manager(self):
        """测试WebSocket管理器"""
        try:
            resp = self.session.get(f"{BACKEND_URL}/api/ws/status", timeout=5)
            # WebSocket状态端点可能不存在
            if resp.status_code == 200:
                self.log("WebSocket状态端点正常", "PASS")
                return True
            else:
                self.log("WebSocket状态端点不可用 (非必需)", "WARN")
                return False
        except:
            self.log("WebSocket检查跳过", "WARN")
            return False
    
    def run_all(self):
        """运行所有页面导航测试"""
        print("=" * 60)
        print("🪿 GO2SE 页面导航 E2E 测试")
        print("=" * 60)
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)
        
        tests = [
            ("根页面", self.test_root_page),
            ("API文档", self.test_api_docs),
            ("健康端点", self.test_health_endpoint),
            ("统计端点", self.test_stats_endpoint),
            ("MiroFish端点", self.test_mirofish_endpoint),
            ("WebSocket", self.test_websocket_manager),
        ]
        
        results = []
        for name, test_func in tests:
            try:
                result = test_func()
                results.append((name, result))
            except Exception as e:
                self.log(f"{name} 异常: {e}", "FAIL")
                results.append((name, False))
        
        print("-" * 60)
        passed = sum(1 for _, r in results if r)
        total = len(results)
        print(f"📊 结果: {passed}/{total} 通过")
        
        if passed >= total * 0.6:
            print("✅ 页面导航测试通过")
            return True
        else:
            print("❌ 页面导航测试未通过")
            return False


if __name__ == "__main__":
    tester = TestPageNavigation()
    success = tester.run_all()
    sys.exit(0 if success else 1)
