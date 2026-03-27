#!/usr/bin/env python3
"""
北斗七鑫 - 完整版 v2
5个投资工具 + 2个打工工具

投资工具:
- 🐰 打兔子: Top20主流币
- 🐹 打地鼠: 高波动币
- 🔮 走着瞧: 预测市场
- 👑 跟大哥: 做市协作
- 🍀 搭便车: 跟单分成

打工工具:
- �羊毛 薅羊毛: 新币空投
- 👶 穷孩子: 众包数据
"""

import json
import time
import asyncio
import aiohttp
import requests
import threading
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from collections import deque

# ==================== 配置 ====================

@dataclass
class ToolConfig:
    """工具配置"""
    name: str
    enabled: bool
    scan_interval: int
    confidence_threshold: float
    max_position: float
    stop_loss: float
    take_profit: float
    api_priority: int  # 1-5, 1最高
    resources_ratio: float  # 算力占比

# 工具配置
TOOL_CONFIGS = {
    # 投资工具
    'rabbit': ToolConfig('打兔子', True, 60, 0.60, 0.15, 0.03, 0.08, 1, 0.30),
    'mole': ToolConfig('打地鼠', True, 30, 0.50, 0.05, 0.05, 0.15, 2, 0.25),
    'prediction': ToolConfig('走着瞧', True, 120, 0.55, 0.08, 0.05, 0.20, 3, 0.15),
    'follow': ToolConfig('跟大哥', True, 60, 0.60, 0.10, 0.04, 0.12, 2, 0.15),
    'hitchhike': ToolConfig('搭便车', True, 300, 0.70, 0.20, 0.02, 0.08, 4, 0.10),
    
    # 打工工具
    'airdrop': ToolConfig('薅羊毛', True, 600, 0.70, 0, 0, 0, 5, 0.03),
    'crowdsource': ToolConfig('穷孩子', True, 600, 0.60, 0, 0, 0, 5, 0.02),
}

# 模式配置
MODE_CONFIGS = {
    'conservative': {
        'name': '保守', 'reserved_funds': 0.20, 'max_positions': 3,
        'scan_interval_multiplier': 2.0, 'confidence_offset': 0.1
    },
    'balanced': {
        'name': '平衡', 'reserved_funds': 0.10, 'max_positions': 5,
        'scan_interval_multiplier': 1.0, 'confidence_offset': 0.0
    },
    'aggressive': {
        'name': '激进', 'reserved_funds': 0.05, 'max_positions': 10,
        'scan_interval_multiplier': 0.5, 'confidence_offset': -0.1
    },
}

# ==================== API管理 ====================

class APIManager:
    """API管理器"""
    
    def __init__(self):
        self.apis = {
            'binance': {
                'base_url': 'https://api.binance.com',
                'priority': 1, 'timeout': 10, 'weight': 1.0,
                'backup_url': 'https://api1.binance.com',
                'status': 'active', 'fail_count': 0
            },
            'bybit': {
                'base_url': 'https://api.bybit.com',
                'priority': 2, 'timeout': 10, 'weight': 0.8,
                'backup_url': 'https://api2.bybit.com',
                'status': 'active', 'fail_count': 0
            },
            'okx': {
                'base_url': 'https://www.okx.com',
                'priority': 3, 'timeout': 15, 'weight': 0.7,
                'backup_url': 'https://www.okx.com',
                'status': 'active', 'fail_count': 0
            },
            'polymarket': {
                'base_url': 'https://clob.polymarket.com',
                'priority': 4, 'timeout': 15, 'weight': 0.6,
                'backup_url': 'https://gamma.polymarket.com',
                'status': 'active', 'fail_count': 0
            },
            'coingecko': {
                'base_url': 'https://api.coingecko.com/api/v3',
                'priority': 5, 'timeout': 20, 'weight': 0.5,
                'backup_url': 'https://pro-api.coingecko.com',
                'status': 'active', 'fail_count': 0
            }
        }
        
        self.current_api = 'binance'
        self.fallback_chain = ['binance', 'bybit', 'okx']
    
    def get_api(self, tool_type: str) -> Dict:
        """获取API (带优先级和故障转移)"""
        # 根据工具类型选择API
        if tool_type in ['rabbit', 'mole']:
            priority_apis = ['binance', 'bybit', 'okx']
        elif tool_type == 'prediction':
            priority_apis = ['polymarket', 'binance']
        elif tool_type == 'follow':
            priority_apis = ['binance', 'bybit']
        else:
            priority_apis = self.fallback_chain
        
        # 选择可用API
        for api_name in priority_apis:
            api = self.apis.get(api_name)
            if api and api['status'] == 'active':
                return api
        
        # 全部故障，使用备份
        return self.apis.get('binance', {})
    
    def report_failure(self, api_name: str):
        """报告API故障"""
        if api_name in self.apis:
            self.apis[api_name]['fail_count'] += 1
            
            # 连续失败3次，标记为不可用
            if self.apis[api_name]['fail_count'] >= 3:
                self.apis[api_name]['status'] = 'degraded'
            
            # 连续失败5次，完全不可用
            if self.apis[api_name]['fail_count'] >= 5:
                self.apis[api_name]['status'] = 'inactive'
                print(f"⚠️ API {api_name} 已标记为不可用")
    
    def report_success(self, api_name: str):
        """报告API成功"""
        if api_name in self.apis:
            self.apis[api_name]['fail_count'] = max(0, self.apis[api_name]['fail_count'] - 1)
            if self.apis[api_name]['fail_count'] == 0:
                self.apis[api_name]['status'] = 'active'
    
    def get_status(self) -> Dict:
        """获取API状态"""
        return {k: v['status'] for k, v in self.apis.items()}

# ==================== 资源调度 ====================

class ResourceScheduler:
    """资源调度器"""
    
    def __init__(self):
        self.mode = 'balanced'
        self.total_resources = 100  # 百分比
        self.current_usage = 0
        
        # 工具当前资源使用
        self.tool_usage = {}
    
    def set_mode(self, mode: str):
        """设置模式"""
        self.mode = mode
        config = MODE_CONFIGS.get(mode, MODE_CONFIGS['balanced'])
        return config
    
    def allocate(self, tool_name: str) -> int:
        """分配资源"""
        tool_config = TOOL_CONFIGS.get(tool_name)
        if not tool_config:
            return 0
        
        # 根据模式调整
        mode_config = MODE_CONFIGS.get(self.mode, MODE_CONFIGS['balanced'])
        
        # 计算资源
        resources = int(tool_config.resources_ratio * 100 * 
                       (1 + mode_config.get('confidence_offset', 0)))
        
        resources = max(5, min(50, resources))  # 5-50%
        
        self.tool_usage[tool_name] = resources
        self.current_usage = sum(self.tool_usage.values())
        
        return resources
    
    def get_available(self) -> int:
        """获取可用资源"""
        return max(0, 100 - self.current_usage)

# ==================== 数据获取 ====================

class DataFetcher:
    """数据获取器"""
    
    def __init__(self, api_manager: APIManager):
        self.api_manager = api_manager
        self.cache = {}
        self.cache_ttl = 60
    
    def fetch(self, endpoint: str, params: Dict = None, tool_type: str = 'rabbit') -> Optional[Dict]:
        """获取数据 (带重试和故障转移)"""
        api = self.api_manager.get_api(tool_type)
        url = f"{api['base_url']}{endpoint}"
        
        for attempt in range(3):  # 最多重试3次
            try:
                response = requests.get(
                    url, params=params, 
                    timeout=api.get('timeout', 10)
                )
                
                if response.status_code == 200:
                    self.api_manager.report_success(api.get('name', ''))
                    return response.json()
                elif response.status_code == 429:  # 限流
                    print(f"⚠️ 限流，等待重试...")
                    time.sleep(2 ** attempt)
                else:
                    self.api_manager.report_failure(api.get('name', ''))
                    
            except requests.exceptions.Timeout:
                print(f"⚠️ 超时: {url}")
                self.api_manager.report_failure(api.get('name', ''))
            except Exception as e:
                print(f"⚠️ 错误: {e}")
                self.api_manager.report_failure(api.get('name', ''))
        
        # 尝试备用API
        for backup_name in ['bybit', 'okx']:
            if backup_name != api.get('name', ''):
                backup_api = self.api_manager.apis.get(backup_name, {})
                if backup_api.get('status') != 'inactive':
                    print(f"🔄 切换到备用API: {backup_name}")
                    try:
                        url = f"{backup_api['base_url']}{endpoint}"
                        response = requests.get(url, params=params, timeout=10)
                        if response.status_code == 200:
                            return response.json()
                    except:
                        pass
        
        return None
    
    def get_market_data(self, tool_type: str = 'rabbit') -> List[Dict]:
        """获取市场数据"""
        # 优先从缓存获取
        cache_key = f'market_{tool_type}'
        if cache_key in self.cache:
            cached_time, cached_data = self.cache[cache_key]
            if time.time() - cached_time < self.cache_ttl:
                return cached_data
        
        # 获取新数据
        endpoints = {
            'rabbit': '/api/v3/ticker/24hr',
            'mole': '/api/v3/ticker/24hr',
            'prediction': '/markets',
            'follow': '/v3/ticker/24hr',
        }
        
        endpoint = endpoints.get(tool_type, '/api/v3/ticker/24hr')
        data = self.fetch(endpoint, tool_type=tool_type)
        
        if data:
            self.cache[cache_key] = (time.time(), data)
            return data if isinstance(data, list) else []
        
        return []

# ==================== 投资工具 ====================

class InvestmentTool:
    """投资工具基类"""
    
    def __init__(self, name: str, config: ToolConfig):
        self.name = name
        self.config = config
        self.positions = {}
        self.signals = deque(maxlen=100)
    
    def scan(self, data: List[Dict]) -> List[Dict]:
        """扫描信号"""
        return []
    
    def analyze(self, symbol: str, data: Dict) -> Dict:
        """分析"""
        return {'signal': 'HOLD', 'confidence': 0}
    
    def execute(self, signal: Dict) -> bool:
        """执行"""
        return True


class RabbitTool(InvestmentTool):
    """打兔子 - Top20主流币"""
    
    TOP20 = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'AVAX', 'DOGE', 'DOT', 'MATIC',
             'LINK', 'UNI', 'ATOM', 'LTC', 'ETC', 'XLM', 'NEAR', 'APT', 'AR', 'FIL']
    
    def __init__(self):
        super().__init__('打兔子', TOOL_CONFIGS['rabbit'])
    
    def scan(self, data: List[Dict]) -> List[Dict]:
        signals = []
        
        for item in data:
            symbol = item.get('symbol', '')
            base = symbol.replace('USDT', '').replace('BTC', '').replace('ETH', '')
            
            # 只关注Top20
            if base not in self.TOP20:
                continue
            
            change = float(item.get('priceChangePercent', 0))
            confidence = min(abs(change) / 20, 1.0)
            
            if confidence >= self.config.confidence_threshold:
                signals.append({
                    'symbol': symbol,
                    'change': change,
                    'confidence': confidence,
                    'tool': 'rabbit',
                    'action': 'BUY' if change > 0 else 'SELL'
                })
        
        return signals


class MoleTool(InvestmentTool):
    """打地鼠 - 高波动币"""
    
    def __init__(self):
        super().__init__('打地鼠', TOOL_CONFIGS['mole'])
    
    def scan(self, data: List[Dict]) -> List[Dict]:
        signals = []
        
        # 按变化率排序
        sorted_data = sorted(data, 
                           key=lambda x: abs(float(x.get('priceChangePercent', 0))), 
                           reverse=True)[:100]
        
        for item in sorted_data:
            symbol = item.get('symbol', '')
            change = float(item.get('priceChangePercent', 0))
            volume = float(item.get('quoteVolume', 0))
            
            # 高波动但不是Top20
            if volume < 1000000:  # $1M
                continue
            
            confidence = min(abs(change) / 15, 1.0)
            
            if confidence >= self.config.confidence_threshold:
                signals.append({
                    'symbol': symbol,
                    'change': change,
                    'confidence': confidence,
                    'tool': 'mole',
                    'action': 'BUY' if change > 0 else 'SELL'
                })
        
        return signals


class PredictionTool(InvestmentTool):
    """走着瞧 - 预测市场"""
    
    def __init__(self):
        super().__init__('走着瞧', TOOL_CONFIGS['prediction'])
    
    def scan(self, data: List[Dict]) -> List[Dict]:
        # 简化版 - 实际需要调用Polymarket API
        signals = []
        
        # 示例信号
        signals.append({
            'symbol': 'BTC>50000',
            'change': 5.0,
            'confidence': 0.65,
            'tool': 'prediction',
            'action': 'BUY'
        })
        
        return signals


class FollowTool(InvestmentTool):
    """跟大哥 - 做市协作"""
    
    def __init__(self):
        super().__init__('跟大哥', TOOL_CONFIGS['follow'])
    
    def scan(self, data: List[Dict]) -> List[Dict]:
        # 示例信号
        return [{
            'symbol': 'BTCUSDT',
            'change': 3.0,
            'confidence': 0.70,
            'tool': 'follow',
            'action': 'BUY',
            'source': 'whale_alert'
        }]


class HitchhikeTool(InvestmentTool):
    """搭便车 - 跟单分成"""
    
    def __init__(self):
        super().__init__('搭便车', TOOL_CONFIGS['hitchhike'])
    
    def scan(self, data: List[Dict]) -> List[Dict]:
        # 示例信号
        return [{
            'symbol': 'BTCUSDT',
            'change': 2.0,
            'confidence': 0.75,
            'tool': 'hitchhike',
            'action': 'FOLLOW'
        }]

# ==================== 打工工具 ====================

class WorkTool:
    """打工工具基类"""
    
    def __init__(self, name: str, config: ToolConfig):
        self.name = name
        self.config = config
        self.tasks = []
        self.earnings = 0
    
    def scan_opportunities(self) -> List[Dict]:
        """扫描机会"""
        return []
    
    def execute_task(self, task: Dict) -> bool:
        """执行任务"""
        return False


class AirdropTool(WorkTool):
    """薅羊毛 - 空投"""
    
    def __init__(self):
        super().__init__('薅羊毛', TOOL_CONFIGS['airdrop'])
    
    def scan_opportunities(self) -> List[Dict]:
        """扫描空投机会"""
        # 示例
        return [
            {
                'type': 'airdrop',
                'name': 'LayerZero空投',
                'estimated_value': 100,
                'difficulty': 'medium',
                'steps': 5,
                'confidence': 0.80
            }
        ]


class CrowdsourceTool(WorkTool):
    """穷孩子 - 众包数据"""
    
    def __init__(self):
        super().__init__('穷孩子', TOOL_CONFIGS['crowdsource'])
    
    def scan_opportunities(self) -> List[Dict]:
        """扫描众包任务"""
        # 示例
        return [
            {
                'type': 'crowdsource',
                'name': 'AI数据标注',
                'payment': 50,
                'duration': 30,
                'difficulty': 'easy',
                'confidence': 0.90
            }
        ]

# ==================== 北斗七鑫核心 ====================

class BeidouQixinCore:
    """北斗七鑫核心系统"""
    
    def __init__(self, mode: str = 'balanced'):
        self.mode = mode
        self.total_capital = 10000
        self.reserved_funds = 0
        self.positions = {}
        
        # 初始化组件
        self.api_manager = APIManager()
        self.scheduler = ResourceScheduler()
        self.scheduler.set_mode(mode)
        self.data_fetcher = DataFetcher(self.api_manager)
        
        # 初始化工具
        self.investment_tools = {
            'rabbit': RabbitTool(),
            'mole': MoleTool(),
            'prediction': PredictionTool(),
            'follow': FollowTool(),
            'hitchhike': HitchhikeTool()
        }
        
        self.work_tools = {
            'airdrop': AirdropTool(),
            'crowdsource': CrowdsourceTool()
        }
        
        # 配置
        mode_config = MODE_CONFIGS.get(mode, MODE_CONFIGS['balanced'])
        self.reserved_funds = self.total_capital * mode_config['reserved_funds']
        self.max_positions = mode_config['max_positions']
        
        # 状态
        self.status = 'idle'
        self.last_run = 0
    
    def run_cycle(self) -> Dict:
        """运行一个周期"""
        print(f"\n{'='*60}")
        print(f"🌀 北斗七鑫 - {MODE_CONFIGS[self.mode]['name']}模式")
        print(f"{'='*60}")
        
        results = {
            'mode': self.mode,
            'timestamp': int(time.time()),
            'investment_signals': [],
            'work_opportunities': [],
            'positions': len(self.positions),
            'reserved_funds': self.reserved_funds
        }
        
        # 1. 投资工具扫描
        print("\n📡 投资工具扫描:")
        
        for tool_name, tool in self.investment_tools.items():
            if not TOOL_CONFIGS[tool_name].enabled:
                continue
            
            # 分配资源
            resources = self.scheduler.allocate(tool_name)
            print(f"  {tool.name}: 分配{resources}%算力")
            
            # 获取数据
            data = self.data_fetcher.get_market_data(tool_name)
            
            # 扫描信号
            signals = tool.scan(data)
            results['investment_signals'].extend(signals[:3])
            
            if signals:
                print(f"    发现 {len(signals)} 个信号")
        
        # 2. 打工工具扫描
        print("\n💰 打工工具扫描:")
        
        idle_resources = self.scheduler.get_available()
        
        if idle_resources > 10:  # 算力富余
            for tool_name, tool in self.work_tools.items():
                if not TOOL_CONFIGS[tool_name].enabled:
                    continue
                
                opportunities = tool.scan_opportunities()
                results['work_opportunities'].extend(opportunities)
                
                if opportunities:
                    print(f"  {tool.name}: {len(opportunities)} 个机会")
        
        # 3. 汇总
        print(f"\n📊 汇总:")
        print(f"  投资信号: {len(results['investment_signals'])}")
        print(f"  打工机会: {len(results['work_opportunities'])}")
        print(f"  当前持仓: {len(self.positions)}")
        print(f"  备用金: ${self.reserved_funds:,.2f}")
        
        # API状态
        api_status = self.api_manager.get_status()
        print(f"\n🌐 API状态:")
        for api, status in api_status.items():
            print(f"  {api}: {status}")
        
        self.last_run = time.time()
        
        return results
    
    def set_mode(self, mode: str):
        """切换模式"""
        self.mode = mode
        self.scheduler.set_mode(mode)
        mode_config = MODE_CONFIGS.get(mode, MODE_CONFIGS['balanced'])
        self.reserved_funds = self.total_capital * mode_config['reserved_funds']
        self.max_positions = mode_config['max_positions']
        print(f"✅ 切换到{mode}模式")
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            'mode': self.mode,
            'status': self.status,
            'positions': len(self.positions),
            'reserved_funds': self.reserved_funds,
            'api_status': self.api_manager.get_status()
        }

# ==================== 测试 ====================

def test():
    """测试"""
    print("🧪 北斗七鑫完整版测试")
    print("="*50)
    
    # 初始化
    system = BeidouQixinCore('balanced')
    
    # 运行周期
    result = system.run_cycle()
    
    # 测试模式切换
    print("\n\n🔄 测试模式切换:")
    for mode in ['conservative', 'balanced', 'aggressive']:
        system.set_mode(mode)
        status = system.get_status()
        print(f"  {mode}: 备用金 ${status['reserved_funds']:,.0f}")
    
    print("\n✅ 测试完成")
    
    return system

if __name__ == '__main__':
    test()
