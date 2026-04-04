#!/usr/bin/env python3
"""
🪿 GO2SE E2E 测试 - API调用
测试核心API端点和功能
"""

import sys
import os
import time
import requests
import json
from datetime import datetime

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8004")

class TestAPICalls:
    """API调用测试"""
    
    def __init__(self):
        self.session = requests.Session()
        self.results = []
        
    def log(self, msg, status="INFO"):
        ts = datetime.now().strftime("%H:%M:%S")
        icon = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️", "INFO": "📋"}.get(status, "📋")
        print(f"[{ts}] {icon} {msg}")
    
    def test_health_api(self):
        """测试健康检查API"""
        try:
            start = time.time()
            resp = self.session.get(f"{BACKEND_URL}/api/health", timeout=10)
            latency = (time.time() - start) * 1000
            
            if resp.status_code == 200:
                data = resp.json()
                status = data.get("status", "unknown")
                checks = data.get("checks", {})
                
                # 验证响应结构
                has_status = "status" in data
                has_checks = "checks" in data
                
                if has_status and has_checks:
                    self.log(f"健康API: status={status}, 延迟={latency:.0f}ms", "PASS")
                    return {"passed": True, "latency": latency, "data": data}
                else:
                    self.log("健康API响应结构不完整", "WARN")
                    return {"passed": False, "latency": latency, "data": data}
            else:
                self.log(f"健康API返回: {resp.status_code}", "FAIL")
                return {"passed": False, "latency": 0, "data": None}
        except Exception as e:
            self.log(f"健康API失败: {e}", "FAIL")
            return {"passed": False, "latency": 0, "data": None}
    
    def test_stats_api(self):
        """测试统计API"""
        try:
            start = time.time()
            resp = self.session.get(f"{BACKEND_URL}/api/stats", timeout=10)
            latency = (time.time() - start) * 1000
            
            if resp.status_code == 200:
                data = resp.json()
                stats = data.get("data", {})
                
                # 验证必要字段
                required_fields = ["trading_mode", "total_signals"]
                has_all = all(f in stats for f in required_fields)
                
                if has_all:
                    self.log(f"统计API: mode={stats.get('trading_mode')}, signals={stats.get('total_signals')}, 延迟={latency:.0f}ms", "PASS")
                    return {"passed": True, "latency": latency, "data": stats}
                else:
                    missing = [f for f in required_fields if f not in stats]
                    self.log(f"统计API缺少字段: {missing}", "WARN")
                    return {"passed": False, "latency": latency, "data": stats}
            else:
                self.log(f"统计API返回: {resp.status_code}", "FAIL")
                return {"passed": False, "latency": 0, "data": None}
        except Exception as e:
            self.log(f"统计API失败: {e}", "FAIL")
            return {"passed": False, "latency": 0, "data": None}
    
    def test_mirofish_markets_api(self):
        """测试MiroFish市场API"""
        try:
            start = time.time()
            resp = self.session.get(f"{BACKEND_URL}/api/oracle/mirofish/markets", timeout=10)
            latency = (time.time() - start) * 1000
            
            if resp.status_code == 200:
                data = resp.json()
                markets = data.get("data", [])
                
                # 验证市场结构
                if len(markets) > 0:
                    sample = markets[0]
                    has_fields = all(k in sample for k in ["id", "status", "agents"])
                    if has_fields:
                        active = len([m for m in markets if m.get("status") == "active"])
                        self.log(f"MiroFish API: {len(markets)}市场, {active}活跃, 延迟={latency:.0f}ms", "PASS")
                        return {"passed": True, "latency": latency, "markets": len(markets)}
                    else:
                        self.log("MiroFish市场结构不完整", "WARN")
                        return {"passed": False, "latency": latency, "markets": len(markets)}
                else:
                    self.log("MiroFish无市场数据", "WARN")
                    return {"passed": False, "latency": latency, "markets": 0}
            else:
                self.log(f"MiroFish API返回: {resp.status_code}", "WARN")
                return {"passed": False, "latency": 0, "markets": 0}
        except Exception as e:
            self.log(f"MiroFish API失败: {e}", "WARN")
            return {"passed": False, "latency": 0, "markets": 0}
    
    def test_mirofish_predict_api(self):
        """测试MiroFish预测API"""
        try:
            payload = {
                "symbol": "BTC",
                "direction": "long",
                "confidence": 0.7
            }
            start = time.time()
            resp = self.session.post(
                f"{BACKEND_URL}/api/oracle/mirofish/predict",
                json=payload,
                timeout=15
            )
            latency = (time.time() - start) * 1000
            
            if resp.status_code == 200:
                data = resp.json()
                has_result = "data" in data or "prediction" in data
                if has_result:
                    self.log(f"MiroFish预测API: 延迟={latency:.0f}ms", "PASS")
                    return {"passed": True, "latency": latency}
                else:
                    self.log("MiroFish预测响应异常", "WARN")
                    return {"passed": False, "latency": latency}
            else:
                self.log(f"MiroFish预测API返回: {resp.status_code}", "WARN")
                return {"passed": False, "latency": 0}
        except Exception as e:
            self.log(f"MiroFish预测API失败: {e}", "WARN")
            return {"passed": False, "latency": 0}
    
    def test_backtest_api(self):
        """测试回测API"""
        try:
            payload = {
                "symbol": "BTCUSDT",
                "start_time": "2024-01-01T00:00:00Z",
                "end_time": "2024-01-31T23:59:59Z",
                "strategy": "trend_following"
            }
            start = time.time()
            resp = self.session.post(
                f"{BACKEND_URL}/api/backtest",
                json=payload,
                timeout=30
            )
            latency = (time.time() - start) * 1000
            
            if resp.status_code in (200, 201):
                self.log(f"回测API: 延迟={latency:.0f}ms", "PASS")
                return {"passed": True, "latency": latency}
            elif resp.status_code == 404:
                self.log("回测API端点不存在 (可接受)", "WARN")
                return {"passed": False, "latency": 0}
            else:
                self.log(f"回测API返回: {resp.status_code}", "WARN")
                return {"passed": False, "latency": 0}
        except Exception as e:
            self.log(f"回测API失败: {e}", "WARN")
            return {"passed": False, "latency": 0}
    
    def test_concurrent_requests(self):
        """测试并发请求"""
        import concurrent.futures
        
        def make_request():
            try:
                start = time.time()
                resp = self.session.get(f"{BACKEND_URL}/api/health", timeout=10)
                return (time.time() - start) * 1000, resp.status_code == 200
            except:
                return 0, False
        
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(make_request) for _ in range(10)]
                results = [f.result() for f in concurrent.futures.as_completed(futures, timeout=15)]
            
            latencies = [r[0] for r in results]
            successes = sum(1 for r in results if r[1])
            
            avg_latency = sum(latencies) / len(latencies) if latencies else 0
            success_rate = successes / len(results) * 100
            
            if success_rate >= 80:
                self.log(f"并发测试: 10请求, {success_rate:.0f}%成功, 平均延迟={avg_latency:.0f}ms", "PASS")
                return {"passed": True, "success_rate": success_rate, "avg_latency": avg_latency}
            else:
                self.log(f"并发测试: {success_rate:.0f}%成功率较低", "WARN")
                return {"passed": False, "success_rate": success_rate, "avg_latency": avg_latency}
        except Exception as e:
            self.log(f"并发测试失败: {e}", "WARN")
            return {"passed": False, "success_rate": 0, "avg_latency": 0}
    
    def run_all(self):
        """运行所有API测试"""
        print("=" * 60)
        print("🪿 GO2SE API调用 E2E 测试")
        print("=" * 60)
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"后端: {BACKEND_URL}")
        print("-" * 60)
        
        tests = [
            ("健康API", self.test_health_api),
            ("统计API", self.test_stats_api),
            ("MiroFish市场", self.test_mirofish_markets_api),
            ("MiroFish预测", self.test_mirofish_predict_api),
            ("回测API", self.test_backtest_api),
            ("并发请求", self.test_concurrent_requests),
        ]
        
        results = []
        for name, test_func in tests:
            try:
                result = test_func()
                passed = result.get("passed", False)
                results.append((name, passed))
            except Exception as e:
                self.log(f"{name} 异常: {e}", "FAIL")
                results.append((name, False))
        
        print("-" * 60)
        passed = sum(1 for _, r in results if r)
        total = len(results)
        print(f"📊 结果: {passed}/{total} 通过")
        
        if passed >= total * 0.7:
            print("✅ API调用测试通过")
            return True
        else:
            print("❌ API调用测试未通过")
            return False


if __name__ == "__main__":
    tester = TestAPICalls()
    success = tester.run_all()
    sys.exit(0 if success else 1)
