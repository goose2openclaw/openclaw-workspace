#!/usr/bin/env python3
"""
北斗七鑫 - 风控告警系统 v1
市场信号预警 + 投资组合偏离 + 止损 + 自动跳转 + 资源告警
"""

import json
import time
import random
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque
from enum import Enum

# ==================== 告警级别 ====================

class AlertLevel(Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertType(Enum):
    MARKET = "market"           # 市场信号
    PORTFOLIO = "portfolio"     # 投资组合
    RISK = "risk"              # 风险
    API = "api"                # API状态
    RESOURCE = "resource"       # 资源
    STOP_LOSS = "stop_loss"     # 止损

# ==================== 告警实体 ====================

@dataclass
class Alert:
    level: AlertLevel
    type: AlertType
    title: str
    description: str
    data: Dict = field(default_factory=dict)
    timestamp: int = field(default_factory=lambda: int(time.time()))

# ==================== 投资组合监控 ====================

class PortfolioMonitor:
    """投资组合监控"""
    
    def __init__(self):
        self.params = {
            'max_position': 0.15,      # 最大仓位15%
            'max_daily_loss': 0.05,    # 日内最大亏损5%
            'stop_loss_default': 0.03, # 默认止损3%
            'reserve_ratio': 0.20       # 备用金比例20%
        }
        
        self.current_positions = {}
        self.daily_pnl = 0
        self.total_pnl = 0
    
    def check_position_limit(self, symbol: str, new_size: float) -> bool:
        """检查仓位限制"""
        total_exposure = sum(self.current_positions.values()) + new_size
        
        if total_exposure > self.params['max_position']:
            return False
        
        return True
    
    def check_daily_loss(self, pnl: float) -> Alert:
        """检查日内亏损"""
        self.daily_pnl += pnl
        
        loss_ratio = abs(self.daily_pnl) / 10000  # 假设初始1万
        
        if loss_ratio > self.params['max_daily_loss']:
            return Alert(
                level=AlertLevel.HIGH,
                type=AlertType.RISK,
                title="日内亏损超标",
                description=f"亏损{loss_ratio:.1%}，超过{self.params['max_daily_loss']:.1%}",
                data={'loss': self.daily_pnl, 'ratio': loss_ratio}
            )
        
        return None
    
    def check_position_deviation(self, positions: Dict, strategy: str) -> Alert:
        """检查仓位偏离"""
        # 简单检查
        for symbol, size in positions.items():
            if size > self.params['max_position']:
                return Alert(
                    level=AlertLevel.MEDIUM,
                    type=AlertType.PORTFOLIO,
                    title=f"仓位偏离: {symbol}",
                    description=f"持仓{size:.1%}超过最大{self.params['max_position']:.1%}",
                    data={'symbol': symbol, 'size': size}
                )
        
        return None

# ==================== 市场信号监控 ====================

class MarketMonitor:
    """市场信号监控"""
    
    def __init__(self):
        self.last_prices = {}
        self.volatility_threshold = 0.05
        self.volume_spike_threshold = 2.0
    
    def check_price_alert(self, symbol: str, price: float) -> Optional[Alert]:
        """价格告警"""
        if symbol in self.last_prices:
            change = abs(price - self.last_prices[symbol]) / self.last_prices[symbol]
            
            if change > 0.1:  # 10%波动
                return Alert(
                    level=AlertLevel.CRITICAL,
                    type=AlertType.MARKET,
                    title=f"剧烈波动: {symbol}",
                    description=f"价格变动{change:.1%}",
                    data={'symbol': symbol, 'change': change, 'price': price}
                )
            
            if change > 0.05:  # 5%波动
                return Alert(
                    level=AlertLevel.HIGH,
                    type=AlertType.MARKET,
                    title=f"显著波动: {symbol}",
                    description=f"价格变动{change:.1%}",
                    data={'symbol': symbol, 'change': change}
                )
        
        self.last_prices[symbol] = price
        return None
    
    def check_volatility(self, symbol: str, volatility: float) -> Optional[Alert]:
        """波动率告警"""
        if volatility > self.volatility_threshold:
            return Alert(
                level=AlertLevel.MEDIUM,
                type=AlertType.MARKET,
                title=f"高波动: {symbol}",
                description=f"波动率{volatility:.1%}超过阈值{self.volatility_threshold:.1%}",
                data={'symbol': symbol, 'volatility': volatility}
            )
        
        return None

# ==================== API健康监控 ====================

class APIMonitor:
    """API健康监控"""
    
    def __init__(self):
        self.providers = {}
        self.error_counts = {}
        self.last_check = {}
    
    def check_provider(self, provider: str, healthy: bool) -> Optional[Alert]:
        """检查API状态"""
        if not healthy:
            count = self.error_counts.get(provider, 0) + 1
            self.error_counts[provider] = count
            
            if count >= 3:
                return Alert(
                    level=AlertLevel.CRITICAL,
                    type=AlertType.API,
                    title=f"API故障: {provider}",
                    description=f"连续{count}次失败",
                    data={'provider': provider, 'errors': count}
                )
            elif count >= 1:
                return Alert(
                    level=AlertLevel.LOW,
                    type=AlertType.API,
                    title=f"API异常: {provider}",
                    description=f"请求失败",
                    data={'provider': provider}
                )
        
        else:
            self.error_counts[provider] = 0
        
        return None

# ==================== 资源监控 ====================

class ResourceMonitor:
    """资源监控"""
    
    def __init__(self):
        self.limits = {
            'cpu_usage': 80,        # CPU使用率
            'memory_usage': 85,     # 内存使用率
            'api_rate_remaining': 100,  # 剩余API调用
            'queue_depth': 100      # 队列深度
        }
    
    def check_resources(self) -> List[Alert]:
        """检查资源"""
        alerts = []
        
        # 模拟检查
        cpu = random.uniform(20, 90)
        memory = random.uniform(30, 95)
        
        if cpu > self.limits['cpu_usage']:
            alerts.append(Alert(
                level=AlertLevel.MEDIUM,
                type=AlertType.RESOURCE,
                title="CPU负载高",
                description=f"使用率{cpu:.0f}%",
                data={'cpu': cpu}
            ))
        
        if memory > self.limits['memory_usage']:
            alerts.append(Alert(
                level=AlertLevel.HIGH,
                type=AlertType.RESOURCE,
                title="内存负载高",
                description=f"使用率{memory:.0f}%",
                data={'memory': memory}
            ))
        
        return alerts

# ==================== 风控引擎 ====================

class RiskControlEngine:
    """风控引擎"""
    
    def __init__(self):
        self.portfolio = PortfolioMonitor()
        self.market = MarketMonitor()
        self.api = APIMonitor()
        self.resource = ResourceMonitor()
        
        self.alerts = deque(maxlen=1000)
        self.auto_actions = []
    
    def check_all(self) -> List[Alert]:
        """全面检查"""
        alerts = []
        
        # 1. 市场检查
        alerts.extend(self._check_market())
        
        # 2. API检查
        alerts.extend(self._check_api())
        
        # 3. 资源检查
        alerts.extend(self._check_resources())
        
        # 4. 执行自动动作
        self._execute_auto_actions(alerts)
        
        # 保存告警
        for alert in alerts:
            self.alerts.append(alert)
        
        return alerts
    
    def _check_market(self) -> List[Alert]:
        """检查市场"""
        alerts = []
        
        # 模拟市场数据
        symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
        
        for symbol in symbols:
            price = random.uniform(100, 50000)
            volatility = random.uniform(0.01, 0.1)
            
            # 价格告警
            alert = self.market.check_price_alert(symbol, price)
            if alert:
                alerts.append(alert)
            
            # 波动告警
            alert = self.market.check_volatility(symbol, volatility)
            if alert:
                alerts.append(alert)
        
        return alerts
    
    def _check_api(self) -> List[Alert]:
        """检查API"""
        alerts = []
        
        providers = ['binance', 'bybit', 'okx']
        
        for provider in providers:
            healthy = random.random() > 0.1  # 90%健康
            
            alert = self.api.check_provider(provider, healthy)
            if alert:
                alerts.append(alert)
        
        return alerts
    
    def _check_resources(self) -> List[Alert]:
        """检查资源"""
        return self.resource.check_resources()
    
    def _execute_auto_actions(self, alerts: List[Alert]):
        """执行自动动作"""
        for alert in alerts:
            if alert.level in [AlertLevel.CRITICAL, AlertLevel.HIGH]:
                action = self._determine_action(alert)
                if action:
                    self.auto_actions.append({
                        'alert': alert.title,
                        'action': action,
                        'timestamp': int(time.time())
                    })
    
    def _determine_action(self, alert: Alert) -> str:
        """确定自动动作"""
        if alert.type == AlertType.API:
            return "switch_to_backup"
        elif alert.type == AlertType.RISK:
            return "reduce_position"
        elif alert.type == AlertType.MARKET:
            return "increase_stop_loss"
        
        return "monitor"

# ==================== 告警系统 ====================

class AlertSystem:
    """告警系统"""
    
    def __init__(self):
        self.risk_engine = RiskControlEngine()
        self.listeners = []
    
    def run_cycle(self) -> Dict:
        """运行检查周期"""
        alerts = self.risk_engine.check_all()
        
        # 格式化输出
        output = {
            'timestamp': int(time.time()),
            'total_alerts': len(alerts),
            'alerts': [],
            'auto_actions': len(self.risk_engine.auto_actions)
        }
        
        for alert in alerts:
            output['alerts'].append({
                'level': alert.level.value,
                'type': alert.type.value,
                'title': alert.title,
                'description': alert.description
            })
        
        # 通知监听器
        self._notify(alerts)
        
        return output
    
    def _notify(self, alerts: List[Alert]):
        """通知监听器"""
        for listener in self.listeners:
            for alert in alerts:
                if alert.level in [AlertLevel.HIGH, AlertLevel.CRITICAL]:
                    listener(alert)

# ==================== 测试 ====================

def test_risk_system():
    """测试风控系统"""
    print("\n🛡️ 风控告警系统测试")
    print("="*50)
    
    system = AlertSystem()
    
    # 运行3个周期
    for i in range(3):
        print(f"\n📍 第 {i+1} 轮检查")
        
        result = system.run_cycle()
        
        print(f"   告警数量: {result['total_alerts']}")
        print(f"   自动动作: {result['auto_actions']}")
        
        for alert in result['alerts'][:3]:
            icons = {
                'critical': '🔴',
                'high': '🟠',
                'medium': '🟡',
                'low': '🟢',
                'info': 'ℹ️'
            }
            icon = icons.get(alert['level'], '⚪')
            print(f"   {icon} [{alert['level'].upper()}] {alert['title']}")
        
        time.sleep(1)
    
    print(f"\n✅ 测试完成")

if __name__ == '__main__':
    test_risk_system()
