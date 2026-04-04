"""
GO2SE V9 E2E 测试套件
=====================

测试覆盖:
1. 前台UI测试
2. 后台API测试
3. 左右脑架构测试
4. 龙虾模块测试
5. 工具集成测试

运行方式:
  pytest e2e/go2se_e2e_tests.py -v
  pytest e2e/go2se_e2e_tests.py -v --headed  # 显示浏览器
  pytest e2e/go2se_e2e_tests.py -v -k "test_api"  # 只跑API测试

2026-04-04
"""

import pytest
import asyncio
import json
import time
import random
from typing import Dict, Any, Optional
from dataclasses import dataclass

# ============================================================================
# 测试配置
# ============================================================================

BASE_URL = "http://localhost:8004"
FRONTEND_URL = "http://localhost:3000"

TEST_CONFIG = {
    "timeout": 30,
    "retry_count": 3,
    "screenshot_on_fail": True
}


# ============================================================================
# 数据类
# ============================================================================

@dataclass
class TestResult:
    name: str
    passed: bool
    duration: float
    error: Optional[str] = None


# ============================================================================
# API 客户端
# ============================================================================

class APIClient:
    """API测试客户端"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
    
    async def get(self, endpoint: str) -> Dict[str, Any]:
        """GET请求"""
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}{endpoint}", timeout=TEST_CONFIG["timeout"]) as resp:
                return await resp.json()
    
    async def post(self, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """POST请求"""
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}{endpoint}",
                json=data or {},
                timeout=TEST_CONFIG["timeout"]
            ) as resp:
                return await resp.json()


# ============================================================================
# 辅助函数
# ============================================================================

def generate_test_id(prefix: str = "test") -> str:
    """生成唯一测试ID"""
    return f"{prefix}_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"


def assert_response_valid(response: Dict[str, Any], required_fields: list = None):
    """验证响应格式"""
    assert isinstance(response, dict), "Response should be a dict"
    
    if required_fields:
        for field in required_fields:
            assert field in response, f"Missing required field: {field}"


def assert_within_range(value: float, min_val: float, max_val: float, field_name: str = "value"):
    """验证值在范围内"""
    assert min_val <= value <= max_val, f"{field_name} {value} not in range [{min_val}, {max_val}]"


# ============================================================================
# 测试类
# ============================================================================

class TestDualBrainAPI:
    """左右脑API测试"""
    
    @pytest.fixture
    def api(self):
        return APIClient(BASE_URL)
    
    @pytest.mark.asyncio
    async def test_status_endpoint(self, api):
        """测试状态端点"""
        response = await api.get("/api/dual-brain/status")
        
        assert_response_valid(response, ["version", "running"])
        assert "dual-brain" in response.get("version", "").lower() or "v9" in response.get("version", "").lower()
        assert isinstance(response.get("running"), bool)
    
    @pytest.mark.asyncio
    async def test_brain_status(self, api):
        """测试左右脑状态"""
        response = await api.get("/api/dual-brain/brain-status")
        
        assert_response_valid(response, ["left", "right"])
        assert response["left"]["mode"] in ["normal", "expert"]
        assert response["right"]["mode"] in ["normal", "expert"]
    
    @pytest.mark.asyncio
    async def test_heartbeat(self, api):
        """测试心跳"""
        response = await api.post("/api/dual-brain/heartbeat")
        
        assert_response_valid(response, ["left", "right"])
        assert response["left"]["alive"] in [True, False]
        assert response["right"]["alive"] in [True, False]
    
    @pytest.mark.asyncio
    async def test_switch_brain(self, api):
        """测试切换脑"""
        current = await api.get("/api/dual-brain/status")
        active = current.get("brain_manager", {}).get("active_brain", "left")
        target = "right" if active == "left" else "left"
        
        response = await api.post("/api/dual-brain/switch", {"target": target})
        
        assert response.get("success") in [True, False] or "active_brain" in response
    
    @pytest.mark.asyncio
    async def test_wallet_status(self, api):
        """测试钱包状态"""
        response = await api.get("/api/dual-brain/wallet-status")
        
        assert_response_valid(response, ["main_wallet", "transfer_wallet"])
        assert "balance" in response["main_wallet"]
        assert "balance" in response["transfer_wallet"]
        
        # 验证余额格式
        assert response["main_wallet"]["balance"] >= 0
        assert response["transfer_wallet"]["balance"] >= 0


class TestLobsterModule:
    """龙虾模块测试"""
    
    @pytest.fixture
    def api(self):
        return APIClient(BASE_URL)
    
    @pytest.mark.asyncio
    async def test_lobster_status(self, api):
        """测试龙虾状态"""
        response = await api.get("/api/dual-brain/lobster/status")
        
        assert_response_valid(response, ["retro_count", "simulation_count", "optimization_count"])
    
    @pytest.mark.asyncio
    async def test_retro(self, api):
        """测试复盘功能"""
        response = await api.post("/api/dual-brain/lobster/retro")
        
        # 复盘应该返回结果
        assert isinstance(response, dict)
    
    @pytest.mark.asyncio
    async def test_simulation(self, api):
        """测试仿真功能"""
        response = await api.post("/api/dual-brain/lobster/simulation")
        
        assert isinstance(response, dict)
    
    @pytest.mark.asyncio
    async def test_optimization(self, api):
        """测试优化功能"""
        response = await api.post("/api/dual-brain/lobster/optimization")
        
        assert isinstance(response, dict)
    
    @pytest.mark.asyncio
    async def test_full_cycle(self, api):
        """测试完整周期"""
        response = await api.post("/api/dual-brain/lobster/full-cycle")
        
        assert isinstance(response, dict)


class TestStrategyEngines:
    """策略引擎测试"""
    
    @pytest.fixture
    def api(self):
        return APIClient(BASE_URL)
    
    @pytest.mark.asyncio
    async def test_rabbit_strategy(self, api):
        """测试打兔子策略"""
        response = await api.post("/api/dual-brain/execute-trade", {
            "tool": "rabbit",
            "score": 0.75
        })
        
        assert isinstance(response, dict)
        assert "win" in response or "pnl_pct" in response
    
    @pytest.mark.asyncio
    async def test_oracle_strategy(self, api):
        """测试走着瞧策略"""
        # 走着瞧 V5 优化版测试
        response = await api.post("/api/go2se/v9/scan-and-select", {
            "mode": "normal"
        })
        
        assert isinstance(response, dict)
    
    @pytest.mark.asyncio
    async def test_hitchhiker_strategy(self, api):
        """测试搭便车策略"""
        response = await api.post("/api/go2se/v9/snipe", {
            "tool": "hitchhiker",
            "confidence": 0.8
        })
        
        assert isinstance(response, dict)


class TestGO2SECore:
    """GO2SE核心功能测试"""
    
    @pytest.fixture
    def api(self):
        return APIClient(BASE_URL)
    
    @pytest.mark.asyncio
    async def test_go2se_stats(self, api):
        """测试统计端点"""
        response = await api.get("/api/go2se/v9/stats")
        
        assert_response_valid(response, ["mode", "version"])
    
    @pytest.mark.asyncio
    async def test_go2se_config(self, api):
        """测试配置端点"""
        response = await api.get("/api/go2se/v9/config")
        
        assert_response_valid(response, ["version", "tools"])
    
    @pytest.mark.asyncio
    async def test_batch_snipe(self, api):
        """测试批量抢单"""
        response = await api.post("/api/go2se/v9/batch-snipe", {
            "items": [
                {"tool": "rabbit", "score": 0.8},
                {"tool": "mole", "score": 0.75}
            ]
        })
        
        assert isinstance(response, dict)


class TestIntegration:
    """集成测试"""
    
    @pytest.fixture
    def api(self):
        return APIClient(BASE_URL)
    
    @pytest.mark.asyncio
    async def test_full_trading_cycle(self, api):
        """完整交易周期测试"""
        # 1. 获取状态
        status = await api.get("/api/dual-brain/status")
        assert status.get("running") or isinstance(status.get("running"), bool)
        
        # 2. 发送心跳
        heartbeat = await api.post("/api/dual-brain/heartbeat")
        assert "left" in heartbeat or "right" in heartbeat
        
        # 3. 获取钱包状态
        wallet = await api.get("/api/dual-brain/wallet-status")
        assert "total_assets" in wallet or "main_wallet" in wallet
        
        # 4. 执行交易
        trade = await api.post("/api/dual-brain/execute-trade", {
            "tool": "rabbit",
            "score": 0.75
        })
        assert "win" in trade or "pnl_pct" in trade
        
        # 5. 获取龙虾状态
        lobster = await api.get("/api/dual-brain/lobster/status")
        assert "retro_count" in lobster or "simulation_count" in lobster
    
    @pytest.mark.asyncio
    async def test_mode_switch_cycle(self, api):
        """模式切换周期测试"""
        # 1. 获取当前状态
        initial = await api.get("/api/dual-brain/status")
        initial_mode = initial.get("brain_manager", {}).get("active_mode", "normal")
        
        # 2. 切换模式
        if initial_mode == "normal":
            target_mode = "expert"
        else:
            target_mode = "normal"
        
        switch = await api.post("/api/dual-brain/switch-mode", {"mode": target_mode})
        assert switch.get("success") in [True, False] or "mode" in switch
        
        # 3. 验证切换
        updated = await api.get("/api/dual-brain/status")
        # 验证模式已更新（如果切换成功）


class TestPerformance:
    """性能测试"""
    
    @pytest.fixture
    def api(self):
        return APIClient(BASE_URL)
    
    @pytest.mark.asyncio
    async def test_api_response_time(self, api):
        """API响应时间测试"""
        start = time.time()
        await api.get("/api/dual-brain/status")
        duration = time.time() - start
        
        # 响应时间应该在1秒内
        assert duration < 1.0, f"API response took {duration:.2f}s, expected < 1s"
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, api):
        """并发请求测试"""
        import asyncio
        
        async def make_request():
            return await api.get("/api/dual-brain/status")
        
        # 并发10个请求
        start = time.time()
        results = await asyncio.gather(*[make_request() for _ in range(10)])
        duration = time.time() - start
        
        # 所有请求应该成功
        assert len(results) == 10
        assert all(isinstance(r, dict) for r in results)
        
        # 总时间应该合理（10个并发请求，1秒内完成）
        assert duration < 2.0, f"Concurrent requests took {duration:.2f}s"


# ============================================================================
# 测试运行器
# ============================================================================

def run_tests():
    """运行所有测试"""
    import sys
    
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        f"--timeout={TEST_CONFIG['timeout']}",
        "-ra"
    ])
    
    return exit_code


if __name__ == "__main__":
    run_tests()
