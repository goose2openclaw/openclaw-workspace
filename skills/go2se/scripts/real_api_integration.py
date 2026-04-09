#!/usr/bin/env python3
"""
北斗七鑫 - 真实API对接系统 v1
外部模拟API端口 + 信号输入 + 执行模块
"""

import json
import time
import socket
import threading
import requests
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

# ==================== API配置 ====================

class APIProvider(Enum):
    BINANCE = "binance"
    BYBIT = "bybit"
    OKX = "okx"
    POLYMARKET = "polymarket"
    MOCK = "mock"

@dataclass
class APIConfig:
    provider: APIProvider
    base_url: str
    timeout: int = 10
    rate_limit: int = 120  # 每分钟请求数
    is_primary: bool = True

API_CONFIGS = {
    'binance': APIConfig(
        provider=APIProvider.BINANCE,
        base_url='https://api.binance.com',
        timeout=10,
        rate_limit=1200,
        is_primary=True
    ),
    'bybit': APIConfig(
        provider=APIProvider.BYBIT,
        base_url='https://api.bybit.com',
        timeout=10,
        rate_limit=600,
        is_primary=False
    ),
    'okx': APIConfig(
        provider=APIProvider.OKX,
        base_url='https://www.okx.com',
        timeout=15,
        rate_limit=300,
        is_primary=False
    ),
    'mock': APIConfig(
        provider=APIProvider.MOCK,
        base_url='http://localhost:8888',
        timeout=5,
        rate_limit=10000,
        is_primary=True
    ),
}

# ==================== API客户端 ====================

class APIClient:
    """API客户端"""
    
    def __init__(self, name: str, config: APIConfig):
        self.name = name
        self.config = config
        self.session = requests.Session()
        self.available = True
        self.last_request_time = 0
        self.request_count = 0
        self.errors = []
    
    def get(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """GET请求"""
        if not self.available:
            return None
        
        url = f"{self.config.base_url}{endpoint}"
        
        try:
            # 限流检查
            now = time.time()
            if now - self.last_request_time < 60:
                self.request_count += 1
                if self.request_count > self.config.rate_limit:
                    self._log_error("Rate limit exceeded")
                    return None
            else:
                self.request_count = 0
            
            response = self.session.get(url, params=params, 
                                        timeout=self.config.timeout)
            
            if response.status_code == 200:
                self.last_request_time = now
                return response.json()
            elif response.status_code == 429:
                self._log_error("Rate limited")
                return None
            else:
                self._log_error(f"HTTP {response.status_code}")
                return None
        
        except requests.exceptions.Timeout:
            self._log_error("Timeout")
            return None
        except Exception as e:
            self._log_error(str(e))
            return None
    
    def post(self, endpoint: str, data: Dict = None) -> Optional[Dict]:
        """POST请求"""
        if not self.available:
            return None
        
        url = f"{self.config.base_url}{endpoint}"
        
        try:
            response = self.session.post(url, json=data, 
                                        timeout=self.config.timeout)
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                self._log_error(f"HTTP {response.status_code}")
                return None
        
        except Exception as e:
            self._log_error(str(e))
            return None
    
    def _log_error(self, error: str):
        """记录错误"""
        self.errors.append({
            'time': int(time.time()),
            'error': error
        })
        
        if len(self.errors) > 10:
            self.errors.pop(0)
    
    def health_check(self) -> bool:
        """健康检查"""
        try:
            # 简化的健康检查
            if self.config.provider == APIProvider.MOCK:
                return self._mock_health_check()
            
            # 实际API检查
            endpoint = '/api/v3/ping' if self.name == 'binance' else '/v5/market/time'
            result = self.get(endpoint)
            
            return result is not None
        except:
            return False
    
    def _mock_health_check(self) -> bool:
        """模拟健康检查"""
        return True

# ==================== API管理器 ====================

class APIManager:
    """API管理器"""
    
    def __init__(self):
        self.clients: Dict[str, APIClient] = {}
        self.primary = None
        self.fallbacks = []
        self._init_clients()
    
    def _init_clients(self):
        """初始化客户端"""
        for name, config in API_CONFIGS.items():
            client = APIClient(name, config)
            self.clients[name] = client
            
            if config.is_primary:
                self.primary = name
    
    def get(self, provider: str = None) -> Optional[APIClient]:
        """获取API客户端"""
        if provider and provider in self.clients:
            return self.clients[provider]
        
        # 返回主API
        if self.primary and self.clients[self.primary].available:
            return self.clients[self.primary]
        
        # 查找可用的备用API
        for name in ['bybit', 'okx', 'binance']:
            if name in self.clients and self.clients[name].available:
                return self.clients[name]
        
        return None
    
    def switch_primary(self, new_primary: str):
        """切换主API"""
        if new_primary in self.clients:
            old = self.primary
            self.primary = new_primary
            
            # 更新配置
            for name in self.clients:
                self.clients[name].config.is_primary = (name == new_primary)
            
            print(f"   🔄 切换主API: {old} → {new_primary}")
    
    def check_all_health(self) -> Dict:
        """检查所有API健康状态"""
        results = {}
        
        for name, client in self.clients.items():
            healthy = client.health_check()
            client.available = healthy
            
            results[name] = {
                'available': healthy,
                'errors': len(client.errors)
            }
        
        return results

# ==================== 交易执行器 ====================

class TradingExecutor:
    """交易执行器"""
    
    def __init__(self):
        self.api_manager = APIManager()
        self.order_history = []
        self.pending_orders = []
    
    def execute_signal(self, signal: Dict) -> Dict:
        """执行信号"""
        provider = signal.get('provider', 'binance')
        client = self.api_manager.get(provider)
        
        if not client:
            return {
                'success': False,
                'error': 'No available API'
            }
        
        # 构建订单
        order = self._build_order(signal)
        
        # 执行订单
        result = self._submit_order(client, order)
        
        # 记录
        self.order_history.append({
            'signal': signal,
            'order': order,
            'result': result,
            'timestamp': int(time.time())
        })
        
        return result
    
    def _build_order(self, signal: Dict) -> Dict:
        """构建订单"""
        return {
            'symbol': signal['symbol'],
            'side': signal.get('side', 'BUY'),
            'type': signal.get('type', 'MARKET'),
            'quantity': signal.get('quantity', 0),
            'price': signal.get('price', 0),
            'stopLoss': signal.get('stop_loss'),
            'takeProfit': signal.get('take_profit')
        }
    
    def _submit_order(self, client: APIClient, order: Dict) -> Dict:
        """提交订单"""
        # 根据不同API调整
        if client.name == 'binance':
            return self._submit_binance(client, order)
        elif client.name == 'bybit':
            return self._submit_bybit(client, order)
        elif client.name == 'mock':
            return self._submit_mock(client, order)
        else:
            return {'success': False, 'error': 'Unknown provider'}
    
    def _submit_binance(self, client: APIClient, order: Dict) -> Dict:
        """提交Binance订单"""
        endpoint = '/api/v3/order'
        
        params = {
            'symbol': order['symbol'],
            'side': order['side'],
            'type': order['type'],
            'quantity': order['quantity']
        }
        
        if order.get('stopLoss'):
            params['stopLoss'] = order['stopLoss']
        if order.get('takeProfit'):
            params['takeProfit'] = order['takeProfit']
        
        result = client.post(endpoint, params)
        
        if result:
            return {
                'success': True,
                'order_id': result.get('orderId'),
                'symbol': result.get('symbol'),
                'side': result.get('side'),
                'price': result.get('price'),
                'executed_qty': result.get('executedQty')
            }
        
        return {'success': False, 'error': 'Order failed'}
    
    def _submit_bybit(self, client: APIClient, order: Dict) -> Dict:
        """提交Bybit订单"""
        endpoint = '/v5/order/create'
        
        params = {
            'category': 'spot',
            'symbol': order['symbol'],
            'side': order['side'],
            'orderType': order['type'],
            'qty': str(order['quantity'])
        }
        
        result = client.post(endpoint, params)
        
        if result:
            return {
                'success': True,
                'order_id': result.get('orderId'),
                'result': result
            }
        
        return {'success': False, 'error': 'Order failed'}
    
    def _submit_mock(self, client: APIClient, order: Dict) -> Dict:
        """模拟订单提交"""
        # 本地模拟执行
        return {
            'success': True,
            'order_id': f"MOCK_{int(time.time())}",
            'symbol': order['symbol'],
            'side': order['side'],
            'quantity': order['quantity'],
            'mock': True,
            'timestamp': int(time.time())
        }
    
    def get_status(self) -> Dict:
        """获取状态"""
        api_status = self.api_manager.check_all_health()
        
        return {
            'api_status': api_status,
            'primary': self.api_manager.primary,
            'total_orders': len(self.order_history),
            'pending': len(self.pending_orders)
        }

# ==================== 信号路由器 ====================

class SignalRouter:
    """信号路由器"""
    
    def __init__(self):
        self.executor = TradingExecutor()
        self.filters = []
    
    def route_signal(self, signal: Dict) -> Dict:
        """路由信号"""
        # 1. 验证信号
        if not self._validate_signal(signal):
            return {
                'success': False,
                'reason': 'Invalid signal'
            }
        
        # 2. 应用过滤器
        for filter_func in self.filters:
            if not filter_func(signal):
                return {
                    'success': False,
                    'reason': 'Filtered'
                }
        
        # 3. 执行
        result = self.executor.execute_signal(signal)
        
        return result
    
    def _validate_signal(self, signal: Dict) -> bool:
        """验证信号"""
        required = ['symbol', 'side', 'quantity']
        
        for field in required:
            if field not in signal:
                return False
        
        return True
    
    def add_filter(self, filter_func):
        """添加过滤器"""
        self.filters.append(filter_func)

# ==================== Mock API服务器 ====================

class MockAPIServer:
    """模拟API服务器（用于测试）"""
    
    def __init__(self, host='127.0.0.1', port=8888):
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
    
    def start(self):
        """启动服务器"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        
        self.running = True
        
        print(f"\n🎭 Mock API Server 启动: {self.host}:{self.port}")
        
        while self.running:
            try:
                client, addr = self.socket.accept()
                threading.Thread(target=self._handle, 
                                args=(client, addr)).start()
            except:
                break
    
    def _handle(self, client, addr):
        """处理请求"""
        data = client.recv(4096)
        
        # 简单响应
        response = json.dumps({
            'status': 'ok',
            'mock': True,
            'timestamp': int(time.time())
        })
        
        client.sendall(response.encode())
        client.close()
    
    def stop(self):
        """停止服务器"""
        self.running = False
        if self.socket:
            self.socket.close()

# ==================== 测试 ====================

def test_api_manager():
    """测试API管理"""
    print("\n🔧 API管理器测试")
    print("="*50)
    
    manager = APIManager()
    
    # 健康检查
    status = manager.check_all_health()
    
    print("\n📡 API状态:")
    for name, info in status.items():
        icon = "✅" if info['available'] else "❌"
        print(f"   {icon} {name}: {'可用' if info['available'] else '不可用'}")
    
    return manager

def test_executor():
    """测试执行器"""
    print("\n🎯 交易执行测试")
    print("="*50)
    
    executor = TradingExecutor()
    
    # 模拟信号
    signal = {
        'symbol': 'BTCUSDT',
        'side': 'BUY',
        'quantity': 0.001,
        'type': 'MARKET',
        'provider': 'mock'
    }
    
    # 执行
    result = executor.execute_signal(signal)
    
    print(f"\n📝 执行结果:")
    print(f"   成功: {result.get('success')}")
    print(f"   订单ID: {result.get('order_id')}")
    
    return executor

def test_signal_router():
    """测试信号路由"""
    print("\n🔀 信号路由测试")
    print("="*50)
    
    router = SignalRouter()
    
    # 测试信号
    signals = [
        {'symbol': 'BTCUSDT', 'side': 'BUY', 'quantity': 0.001},
        {'symbol': 'ETHUSDT', 'side': 'SELL', 'quantity': 0.01},
        {'symbol': 'SOLUSDT', 'side': 'BUY', 'quantity': 1},  # 无效
    ]
    
    for sig in signals:
        result = router.route_signal(sig)
        status = "✅" if result.get('success') else "❌"
        print(f"   {status} {sig['symbol']}: {result.get('reason', 'OK')}")

if __name__ == '__main__':
    print("="*60)
    print("🔌 真实API对接系统测试")
    print("="*60)
    
    # API管理
    test_api_manager()
    
    # 执行器
    test_executor()
    
    # 信号路由
    test_signal_router()
    
    print("\n✅ 测试完成")
