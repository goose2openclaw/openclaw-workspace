"""
GO2SE E2E 测试配置
"""

import pytest
import asyncio
import sys
import os

# 添加backend到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def api_base_url():
    """API基础URL"""
    return os.environ.get("GO2SE_API_URL", "http://localhost:8004")


@pytest.fixture(scope="session")
def frontend_url():
    """前端URL"""
    return os.environ.get("GO2SE_FRONTEND_URL", "http://localhost:3000")


@pytest.fixture
def test_config():
    """测试配置"""
    return {
        "timeout": 30,
        "retry_count": 3,
        "screenshot_on_fail": True
    }


# 配置pytest-asyncio
def pytest_configure(config):
    """pytest配置"""
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )
