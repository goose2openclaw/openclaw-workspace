"""
GO2SE 核心模块测试
2026-04-04
"""

import pytest
import sys
sys.path.insert(0, '.')

from app.core.sonar import (
    SonarScanner,
    SonarLibrary,
    ScanResult,
    Signal,
    TrendModel,
    calculate_ema,
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
    ModelFactory,
)


class TestSonarBase:
    """基础工具函数测试"""
    
    def test_calculate_ema(self):
        """测试EMA计算"""
        prices = [100, 102, 101, 103, 105, 104, 106, 108, 107, 110]
        ema = calculate_ema(prices, 5)
        assert ema > 0
        assert isinstance(ema, float)
    
    def test_calculate_rsi(self):
        """测试RSI计算"""
        prices = [100, 102, 101, 103, 105, 104, 106, 108, 107, 110]
        rsi = calculate_rsi(prices, 14)
        assert 0 <= rsi <= 100
    
    def test_calculate_macd(self):
        """测试MACD计算"""
        prices = [100, 102, 101, 103, 105, 104, 106, 108, 107, 110] * 5
        macd, signal, hist = calculate_macd(prices)
        assert isinstance(macd, float)
        assert isinstance(signal, float)
        assert isinstance(hist, float)
    
    def test_calculate_bollinger_bands(self):
        """测试布林带计算"""
        prices = [100, 102, 101, 103, 105, 104, 106, 108, 107, 110] * 3
        upper, middle, lower = calculate_bollinger_bands(prices, 20)
        assert upper > middle > lower


class TestSonarModels:
    """模型测试"""
    
    def test_model_factory(self):
        """测试模型工厂"""
        factory = ModelFactory()
        assert factory.get_model_count() > 0
        
        # 测试获取单个模型
        model = factory.get_model("EMA5")
        assert model is not None
        assert model.name == "EMA5"
    
    def test_get_models_by_category(self):
        """测试按类别获取模型"""
        factory = ModelFactory()
        ema_models = factory.get_models_by_category("ema")
        assert len(ema_models) > 0
    
    def test_trend_model(self):
        """测试趋势模型"""
        model = TrendModel("Test", "test", 1.0)
        assert model.name == "Test"
        assert model.enabled is True


class TestSonarScanner:
    """扫描器测试"""
    
    def test_scanner_init(self):
        """测试扫描器初始化"""
        scanner = SonarScanner()
        assert scanner.factory.get_model_count() > 0
    
    def test_scan_basic(self):
        """测试基本扫描"""
        scanner = SonarScanner()
        
        indicators = {
            "RSI_14": 65,
            "MACD": 0.5,
            "EMA20": 68000,
        }
        
        result = scanner.scan("BTC", 68120.50, indicators)
        
        assert isinstance(result, ScanResult)
        assert result.symbol == "BTC"
        assert result.price == 68120.50
        assert result.recommendation in ["buy", "sell", "hold"]
    
    def test_direction_classification(self):
        """测试方向分类"""
        scanner = SonarScanner()
        
        # 测试RSI超卖
        result = scanner.scan("BTC", 100, {"RSI_14": 25})
        assert result.bullish_count > 0
        
        # 测试RSI超买
        result = scanner.scan("BTC", 100, {"RSI_14": 85})
        assert result.bearish_count > 0


class TestSonarLibrary:
    """声纳库测试"""
    
    def test_library_init(self):
        """测试库初始化"""
        library = SonarLibrary()
        assert library.model_count > 0
    
    def test_analyze(self):
        """测试综合分析"""
        library = SonarLibrary()
        
        indicators = {
            "RSI_14": 55,
            "MACD": 0.3,
            "EMA20": 68000,
            "EMA50": 67500,
        }
        
        result = library.analyze("BTC", 68120.50, indicators)
        
        assert result["status"] == "success"
        assert "analysis" in result
        assert "recommendation" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
