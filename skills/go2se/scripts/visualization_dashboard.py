#!/usr/bin/env python3
"""
北斗七鑫 - 数据可视化面板 v1
实时数据 + 图表 + 统计面板
"""

import json
import time
import random
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime
from collections import deque

# ==================== 面板组件 ====================

@dataclass
class PanelData:
    title: str
    data: Dict
    chart_type: str = "text"

class Dashboard:
    """数据面板"""
    
    def __init__(self, name: str = "北斗七鑫"):
        self.name = name
        self.components = {}
        self.history = deque(maxlen=100)
    
    def add_component(self, name: str, data: PanelData):
        """添加组件"""
        self.components[name] = data
    
    def render(self) -> str:
        """渲染面板"""
        lines = []
        
        lines.append("\n" + "="*60)
        lines.append(f"📊 {self.name} - 数据面板")
        lines.append("="*60)
        lines.append(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        for name, comp in self.components.items():
            lines.append(self._render_component(comp))
        
        return "\n".join(lines)
    
    def _render_component(self, comp: PanelData) -> str:
        """渲染组件"""
        lines = [f"\n{comp.title}"]
        lines.append("-" * 40)
        
        if comp.chart_type == "text":
            for key, value in comp.data.items():
                lines.append(f"  {key}: {value}")
        elif comp.chart_type == "bar":
            lines.append(self._render_bar(comp.data))
        elif comp.chart_type == "status":
            lines.append(self._render_status(comp.data))
        
        return "\n".join(lines)
    
    def _render_bar(self, data: Dict) -> str:
        """渲染条形图"""
        lines = []
        
        max_val = max(data.values()) if data else 1
        
        for label, value in data.items():
            bar_len = int((value / max_val) * 20)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            lines.append(f"  {label:15} {bar} {value:.1f}")
        
        return "\n".join(lines)
    
    def _render_status(self, data: Dict) -> str:
        """渲染状态"""
        lines = []
        
        for label, status in data.items():
            icons = {
                'healthy': '✅',
                'warning': '⚠️',
                'error': '❌',
                'active': '🟢',
                'inactive': '🔴'
            }
            
            icon = icons.get(str(status).lower(), '⚪')
            lines.append(f"  {icon} {label}: {status}")
        
        return "\n".join(lines)

# ==================== 统计面板 ====================

class StatsPanel:
    """统计面板"""
    
    def __init__(self):
        self.stats = {
            'trades_today': 0,
            'wins_today': 0,
            'losses_today': 0,
            'pnl_today': 0,
            'win_rate': 0,
            'active_positions': 0
        }
    
    def update(self, new_stats: Dict):
        """更新统计"""
        self.stats.update(new_stats)
    
    def get_data(self) -> Dict:
        """获取数据"""
        return {
            '今日交易': self.stats['trades_today'],
            '盈利': self.stats['wins_today'],
            '亏损': self.stats['losses_today'],
            '胜率': f"{self.stats['win_rate']:.1f}%",
            '持仓': self.stats['active_positions'],
            'PnL': f"${self.stats['pnl_today']:.2f}"
        }

# ==================== 工具面板 ====================

class ToolPanel:
    """工具面板"""
    
    def __init__(self):
        self.tools = {
            'rabbit': {'name': '🐰 打兔子', 'status': 'active', 'signals': 0},
            'mole': {'name': '🐹 打地鼠', 'status': 'active', 'signals': 0},
            'prediction': {'name': '🔮 走着瞧', 'status': 'idle', 'signals': 0},
            'follow': {'name': '👑 跟大哥', 'status': 'active', 'signals': 0},
            'hitchhike': {'name': '🍀 搭便车', 'status': 'idle', 'signals': 0},
            'airdrop': {'name': '💰 薅羊毛', 'status': 'active', 'signals': 0},
            'crowdsource': {'name': '👶 穷孩子', 'status': 'idle', 'signals': 0},
        }
    
    def update(self):
        """更新工具状态"""
        for tool in self.tools:
            self.tools[tool]['signals'] = random.randint(0, 10)
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {t['name']: t['status'] for t in self.tools.values()}

# ==================== 市场面板 ====================

class MarketPanel:
    """市场面板"""
    
    def __init__(self):
        self.prices = {}
    
    def update(self):
        """更新价格"""
        self.prices = {
            'BTC': random.uniform(40000, 60000),
            'ETH': random.uniform(2000, 3000),
            'SOL': random.uniform(80, 150),
            'BNB': random.uniform(300, 400),
            'ADA': random.uniform(0.3, 0.5)
        }
    
    def get_data(self) -> Dict:
        """获取数据"""
        data = {}
        
        for coin, price in self.prices.items():
            change = random.uniform(-5, 5)
            data[f"{coin}/USDT"] = f"${price:.2f} ({change:+.2f}%)"
        
        return data

# ==================== 会员面板 ====================

class MembershipPanel:
    """会员面板"""
    
    def __init__(self):
        self.members = {
            'guest': 100,
            'subscriber': 30,
            'member': 15,
            'lp': 5,
            'expert': 3
        }
    
    def get_data(self) -> Dict:
        """获取数据"""
        total = sum(self.members.values())
        
        data = {}
        
        for level, count in self.members.items():
            pct = count / total * 100
            data[level] = count  # 使用数字用于图表
        
        return data

# ==================== 风控面板 ====================

class RiskPanel:
    """风控面板"""
    
    def __init__(self):
        self.alerts = []
    
    def add_alert(self, alert: Dict):
        """添加告警"""
        self.alerts.append(alert)
        
        if len(self.alerts) > 10:
            self.alerts.pop(0)
    
    def get_status(self) -> Dict:
        """获取状态"""
        critical = sum(1 for a in self.alerts if a.get('level') == 'critical')
        high = sum(1 for a in self.alerts if a.get('level') == 'high')
        
        if critical > 0:
            return 'critical'
        elif high > 0:
            return 'warning'
        else:
            return 'healthy'

# ==================== 可视化生成器 ====================

class Visualizer:
    """可视化生成器"""
    
    def __init__(self):
        self.dashboard = Dashboard()
        self.stats = StatsPanel()
        self.tools = ToolPanel()
        self.market = MarketPanel()
        self.membership = MembershipPanel()
        self.risk = RiskPanel()
    
    def update_all(self):
        """更新所有数据"""
        self.tools.update()
        self.market.update()
        
        # 模拟统计数据
        self.stats.update({
            'trades_today': random.randint(5, 20),
            'wins_today': random.randint(3, 15),
            'losses_today': random.randint(1, 10),
            'pnl_today': random.uniform(-100, 500),
            'win_rate': random.uniform(40, 80),
            'active_positions': random.randint(0, 5)
        })
    
    def render(self) -> str:
        """渲染完整面板"""
        # 更新组件
        self.dashboard.add_component("stats", PanelData(
            "📈 交易统计",
            self.stats.get_data(),
            "text"
        ))
        
        self.dashboard.add_component("tools", PanelData(
            "🛠️ 工具状态",
            self.tools.get_status(),
            "status"
        ))
        
        self.dashboard.add_component("market", PanelData(
            "🌐 市场行情",
            self.market.get_data(),
            "text"
        ))
        
        self.dashboard.add_component("membership", PanelData(
            "👥 会员分布",
            self.membership.get_data(),
            "bar"
        ))
        
        return self.dashboard.render()
    
    def generate_chart(self, data: Dict, title: str) -> str:
        """生成图表"""
        lines = [f"\n📊 {title}", "=" * 40]
        
        max_val = max(data.values()) if data else 1
        
        for label, value in data.items():
            bar_len = int((value / max_val) * 30)
            bar = "▓" * bar_len + "░" * (30 - bar_len)
            lines.append(f"{label:15} {bar} {value}")
        
        return "\n".join(lines)

# ==================== 主程序 ====================

def run_dashboard(cycles: int = 3):
    """运行面板"""
    visualizer = Visualizer()
    
    print("\n" + "="*60)
    print("🎨 数据可视化面板")
    print("="*60)
    
    for i in range(cycles):
        print(f"\n{'='*60}")
        print(f"📍 第 {i+1}/{cycles} 轮")
        print("="*60)
        
        visualizer.update_all()
        print(visualizer.render())
        
        if i < cycles - 1:
            time.sleep(2)
    
    # 示例图表
    print("\n" + "="*60)
    print("📈 趋势图表示例")
    print("="*60)
    
    # 收益曲线
    pnl_data = {
        '周一': random.randint(100, 500),
        '周二': random.randint(100, 500),
        '周三': random.randint(100, 500),
        '周四': random.randint(100, 500),
        '周五': random.randint(100, 500),
    }
    print(visualizer.generate_chart(pnl_data, "本周收益"))
    
    # 工具信号
    signal_data = {
        '打兔子': random.randint(5, 20),
        '打地鼠': random.randint(3, 15),
        '走着瞧': random.randint(1, 10),
        '跟大哥': random.randint(2, 12),
        '薅羊毛': random.randint(1, 8),
    }
    print(visualizer.generate_chart(signal_data, "工具信号统计"))

if __name__ == '__main__':
    run_dashboard(2)
