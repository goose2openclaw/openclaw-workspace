"""
🧪 GO2SE API测试
================
基本API端点测试

运行: pytest tests/test_api.py -v
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealthEndpoint:
    """📊 SRE - Health端点测试"""
    
    def test_health_returns_200(self):
        """Health端点应返回200"""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_health_has_required_fields(self):
        """Health响应应包含必需字段"""
        response = client.get("/health")
        data = response.json()
        
        required_fields = ["status", "signals", "dependencies"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
    
    def test_health_shows_system_metrics(self):
        """Health应显示系统指标"""
        response = client.get("/health")
        data = response.json()
        
        signals = data.get("signals", {})
        assert "latency_ms" in signals
        assert "saturation_cpu" in signals


class TestStatsEndpoint:
    """📊 统计端点测试"""
    
    def test_stats_returns_200(self):
        """Stats端点应返回200"""
        response = client.get("/api/stats")
        assert response.status_code == 200
    
    def test_stats_has_signals(self):
        """Stats应包含信号数据"""
        response = client.get("/api/stats")
        data = response.json()
        
        assert "data" in data
        assert "total_signals" in data["data"]


class TestStrategiesEndpoint:
    """🎯 策略端点测试"""
    
    def test_strategies_returns_200(self):
        """Strategies端点应返回200"""
        response = client.get("/api/strategies")
        assert response.status_code == 200


class TestMarketEndpoint:
    """📈 市场数据端点测试"""
    
    def test_market_returns_200(self):
        """Market端点应返回200"""
        response = client.get("/api/market")
        assert response.status_code == 200
    
    def test_market_has_btc_price(self):
        """Market应包含BTC价格"""
        response = client.get("/api/market")
        data = response.json()
        
        if "data" in data and len(data["data"]) > 0:
            symbols = [item["symbol"] for item in data["data"]]
            assert any("BTC" in s for s in symbols)
