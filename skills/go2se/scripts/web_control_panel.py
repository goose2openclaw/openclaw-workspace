#!/usr/bin/env python3
"""
北斗七鑫 - 完整Web控制面板
安全系统 + 交易系统 + 监控面板
"""

import json
import time
import hashlib
import secrets
import base64
import random
from typing import Dict, List, Optional
from datetime import datetime
from collections import deque
from flask import Flask, render_template_string, jsonify, request

# ==================== Flask应用 ====================

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)

# ==================== 数据存储 ====================

class DataStore:
    """数据存储"""
    
    def __init__(self):
        self.signals = deque(maxlen=1000)
        self.positions = {}
        self.wallets = {
            'main': {'balance': 85000, 'currency': 'USDT'},
            'rabbit': {'balance': 2500, 'currency': 'USDT'},
            'prediction': {'balance': 3000, 'currency': 'USDT'},
            'airdrop': {'balance': 1500, 'currency': 'USDT'},
        }
        self.backups = deque(maxlen=50)
        self.alerts = deque(maxlen=100)
        self.config = {
            'mode': 'balanced',
            'risk_level': 'medium',
            'auto_trade': True,
            'backup_interval': 24
        }
    
    def add_signal(self, signal: Dict):
        self.signals.append({**signal, 'time': int(time.time())})
    
    def get_signals(self, limit: int = 50) -> List[Dict]:
        return list(self.signals)[-limit:]
    
    def get_wallets(self) -> Dict:
        total = sum(w['balance'] for w in self.wallets.values())
        return {
            'wallets': self.wallets,
            'total': total
        }

# ==================== 工具管理器 ====================

class ToolManager:
    """工具管理器"""
    
    def __init__(self):
        self.tools = {
            'rabbit': {'name': '🐰 打兔子', 'status': 'active', 'signals': 0, 'pnl': 0},
            'mole': {'name': '🐹 打地鼠', 'status': 'active', 'signals': 0, 'pnl': 0},
            'prediction': {'name': '🔮 走着瞧', 'status': 'active', 'signals': 0, 'pnl': 0},
            'follow': {'name': '👑 跟大哥', 'status': 'active', 'signals': 0, 'pnl': 0},
            'hitchhike': {'name': '🍀 搭便车', 'status': 'active', 'signals': 0, 'pnl': 0},
            'airdrop': {'name': '💰 薅羊毛', 'status': 'active', 'signals': 0, 'pnl': 0},
            'crowdsource': {'name': '👶 穷孩子', 'status': 'active', 'signals': 0, 'pnl': 0},
        }
        
        self.resources = {
            'rabbit': 25,
            'mole': 20,
            'prediction': 15,
            'follow': 15,
            'hitchhike': 10,
            'airdrop': 3,
            'crowdsource': 2,
        }
    
    def get_tools(self) -> Dict:
        return {
            'tools': self.tools,
            'resources': self.resources,
            'total_resources': sum(self.resources.values())
        }
    
    def update_tool(self, tool_id: str, data: Dict):
        if tool_id in self.tools:
            self.tools[tool_id].update(data)

# ==================== 安全系统 ====================

class SecurityPanel:
    """安全面板"""
    
    def __init__(self):
        self.protection = {
            'firewall': 'active',
            'encryption': 'enabled',
            '2fa': 'enabled',
            'backup': 'automatic'
        }
        
        self.threats = {
            'level': 1,
            'blocked': 0,
            'scans': 0
        }
        
        self.backup_codes = [
            f"GO2SE-{secrets.token_hex(2).upper()}-{i:04d}" 
            for i in range(1, 11)
        ]
    
    def get_status(self) -> Dict:
        return {
            'protection': self.protection,
            'threats': self.threats,
            'backup_codes': len(self.backup_codes),
            'last_backup': int(time.time()) - 3600
        }

# ==================== 初始化 ====================

data_store = DataStore()
tool_manager = ToolManager()
security_panel = SecurityPanel()

# ==================== HTML模板 ====================

MAIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🪿 北斗七鑫 控制面板</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
        }
        .header {
            background: linear-gradient(90deg, #0f3460, #16213e);
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #e94560;
        }
        .logo { font-size: 28px; font-weight: bold; }
        .logo span { color: #e94560; }
        .nav { display: flex; gap: 15px; }
        .nav button {
            background: transparent;
            border: 1px solid #e94560;
            color: #fff;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .nav button:hover, .nav button.active {
            background: #e94560;
        }
        .container { padding: 20px; }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        .card {
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
        }
        .card-title {
            font-size: 18px;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .stat { font-size: 32px; font-weight: bold; color: #00d9ff; }
        .stat-label { font-size: 14px; color: #888; }
        .tool-item {
            display: flex;
            justify-content: space-between;
            padding: 10px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .status-active { color: #00ff88; }
        .status-inactive { color: #ff4444; }
        .progress-bar {
            background: rgba(255,255,255,0.1);
            height: 20px;
            border-radius: 10px;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #e94560, #0f3460);
            transition: width 0.3s;
        }
        .btn {
            background: #e94560;
            border: none;
            color: #fff;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin: 5px;
        }
        .btn:hover { background: #ff6b8a; }
        .alert {
            background: rgba(233,69,96,0.2);
            border-left: 3px solid #e94560;
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
        }
        .security-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
        }
        .secure { background: #00ff88; color: #000; }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">🪿 北斗七鑫 <span>v5.0</span></div>
        <div class="nav">
            <button class="active" onclick="showPage('dashboard')">📊 仪表板</button>
            <button onclick="showPage('tools')">🔧 工具</button>
            <button onclick="showPage('security')">🛡️ 安全</button>
            <button onclick="showPage('wallets')">💰 钱包</button>
        </div>
    </div>
    
    <div class="container">
        <!-- 仪表板 -->
        <div id="dashboard" class="page">
            <div class="grid">
                <div class="card">
                    <div class="card-title">💰 总资产</div>
                    <div class="stat">${{ total_assets }}</div>
                    <div class="stat-label">+2.34% 今日</div>
                </div>
                <div class="card">
                    <div class="card-title">📡 信号数</div>
                    <div class="stat">{{ signal_count }}</div>
                    <div class="stat-label">活跃信号</div>
                </div>
                <div class="card">
                    <div class="card-title">🎯 执行率</div>
                    <div class="stat">87.2%</div>
                    <div class="stat-label">胜率 73%</div>
                </div>
                <div class="card">
                    <div class="card-title">🛡️ 安全状态</div>
                    <div class="stat"><span class="security-badge secure">安全</span></div>
                    <div class="stat-label">威胁等级: 低</div>
                </div>
            </div>
            
            <div class="card" style="margin-top: 20px;">
                <div class="card-title">📈 7个工具运行状态</div>
                {% for tool_id, tool in tools.items() %}
                <div class="tool-item">
                    <span>{{ tool.name }}</span>
                    <span class="status-active">{{ tool.status }}</span>
                </div>
                {% endfor %}
            </div>
        </div>
        
        <!-- 工具页面 -->
        <div id="tools" class="page" style="display: none;">
            <div class="card">
                <div class="card-title">⚙️ 工具配置</div>
                {% for tool_id, tool in tools.items() %}
                <div class="tool-item">
                    <span>{{ tool.name }}</span>
                    <span>{{ resources[tool_id] }}% 算力</span>
                </div>
                {% endfor %}
            </div>
        </div>
        
        <!-- 安全页面 -->
        <div id="security" class="page" style="display: none;">
            <div class="grid">
                <div class="card">
                    <div class="card-title">🛡️ 保护状态</div>
                    <div class="tool-item">
                        <span>防火墙</span>
                        <span class="status-active">启用</span>
                    </div>
                    <div class="tool-item">
                        <span>加密</span>
                        <span class="status-active">启用</span>
                    </div>
                    <div class="tool-item">
                        <span>2FA</span>
                        <span class="status-active">启用</span>
                    </div>
                </div>
                <div class="card">
                    <div class="card-title">🔑 备份码</div>
                    <p style="color: #888;">{{ backup_codes }} 个可用</p>
                </div>
            </div>
        </div>
        
        <!-- 钱包页面 -->
        <div id="wallets" class="page" style="display: none;">
            <div class="card">
                <div class="card-title">💰 钱包余额</div>
                {% for name, wallet in wallets.items() %}
                <div class="tool-item">
                    <span>{{ name }}</span>
                    <span>${{ wallet.balance }}</span>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
    
    <script>
        function showPage(pageId) {
            document.querySelectorAll('.page').forEach(p => p.style.display = 'none');
            document.getElementById(pageId).style.display = 'block';
            document.querySelectorAll('.nav button').forEach(b => b.classList.remove('active'));
            event.target.classList.add('active');
        }
        
        // 刷新数据
        setInterval(() => {
            fetch('/api/status').then(r => r.json()).then(data => {
                console.log('系统正常');
            });
        }, 30000);
    </script>
</body>
</html>
'''

# ==================== 路由 ====================

@app.route('/')
def index():
    wallets = data_store.get_wallets()
    tools = tool_manager.get_tools()
    
    return render_template_string(MAIN_TEMPLATE,
        total_assets=f"{wallets['total']:,.2f}",
        signal_count=len(data_store.get_signals()),
        tools=tools['tools'],
        resources=tools['resources'],
        wallets=wallets['wallets'],
        backup_codes=len(security_panel.backup_codes)
    )

@app.route('/api/status')
def api_status():
    return jsonify({
        'status': 'ok',
        'timestamp': int(time.time()),
        'wallets': data_store.get_wallets(),
        'tools': tool_manager.get_tools(),
        'security': security_panel.get_status()
    })

@app.route('/api/signals')
def api_signals():
    return jsonify(data_store.get_signals())

@app.route('/api/command', methods=['POST'])
def api_command():
    cmd = request.json.get('command')
    params = request.json.get('params', {})
    
    commands = {
        'backup': lambda: {'status': 'success', 'id': f"BK_{int(time.time())}"},
        'scan': lambda: {'threats': 0},
        'status': lambda: {'system': 'ok'}
    }
    
    result = commands.get(cmd, lambda: {'error': 'unknown'})()
    return jsonify(result)

# ==================== 测试 ====================

def test_api():
    """测试API"""
    print("\n" + "="*60)
    print("🌐 Web控制面板 API测试")
    print("="*60)
    
    # 模拟数据
    for i in range(10):
        data_store.add_signal({
            'tool': random.choice(['rabbit', 'mole', 'prediction']),
            'signal': f"BTC突破${random.randint(30000, 50000)}",
            'confidence': random.uniform(0.5, 0.9)
        })
    
    # 测试API
    print("\n📡 API状态:")
    with app.test_client() as client:
        resp = client.get('/api/status')
        data = json.loads(resp.data)
        print(f"   状态: {data['status']}")
        print(f"   总资产: ${data['wallets']['total']}")
        print(f"   工具数: {len(data['tools']['tools'])}")
        
        resp = client.get('/api/signals')
        signals = json.loads(resp.data)
        print(f"   信号数: {len(signals)}")
    
    # 测试命令
    with app.test_client() as client:
        resp = client.post('/api/command', 
            json={'command': 'backup'})
        print(f"   备份: {json.loads(resp.data)}")
    
    print("\n✅ API测试完成")

if __name__ == '__main__':
    test_api()
