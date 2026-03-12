#!/usr/bin/env python3
"""
GO2SE Web UI 后台服务 v2
支持: 游客/注册用户/钱包/VPN/模拟交易/薅羊毛
"""

from flask import Flask, render_template, jsonify, request, session
import json
import random
import threading
import time
import uuid
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'go2se_secret_key_2026'

# ==================== 用户系统 ====================

class UserSystem:
    """用户系统"""
    
    def __init__(self):
        # 用户数据库
        self.users = {
            "guest": {
                "id": "guest",
                "type": "guest",
                "balance": 1000.0,  # 游客1000USDT
                "airdrop_earned": 0.0,  # 薅羊毛收益
                "registered": False,
                "wallet": None,
                "created_at": datetime.now().isoformat()
            }
        }
        
        # 注册用户
        self.registered_users = {}
        
        # 当前会话
        self.sessions = {}
    
    def create_guest(self):
        """创建游客"""
        guest_id = f"guest_{uuid.uuid4().hex[:8]}"
        self.users[guest_id] = {
            "id": guest_id,
            "type": "guest",
            "balance": 1000.0,
            "airdrop_earned": 0.0,
            "registered": False,
            "wallet": None,
            "created_at": datetime.now().isoformat()
        }
        return guest_id
    
    def register_user(self, guest_id, username, password, wallet_address=None):
        """注册用户"""
        user = self.users.get(guest_id)
        if not user:
            return {"success": False, "error": "User not found"}
        
        # 创建注册用户
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        self.registered_users[user_id] = {
            "id": user_id,
            "username": username,
            "password": password,  # 实际应加密
            "type": "registered",
            "balance": user["balance"],  # 继承余额
            "airdrop_earned": user["airdrop_earned"],  # 继承羊毛收益
            "wallet": wallet_address,
            "registered": True,
            "created_at": datetime.now().isoformat()
        }
        
        user["registered"] = True
        
        return {"success": True, "user_id": user_id, "user": self.registered_users[user_id]}
    
    def get_user(self, user_id):
        """获取用户"""
        if user_id in self.registered_users:
            return self.registered_users[user_id]
        return self.users.get(user_id)
    
    def update_balance(self, user_id, amount):
        """更新余额"""
        user = self.get_user(user_id)
        if user:
            user["balance"] = max(0, user["balance"] + amount)
            return True
        return False
    
    def add_airdrop(self, user_id, amount):
        """添加羊毛收益"""
        user = self.get_user(user_id)
        if user:
            user["airdrop_earned"] = user.get("airdrop_earned", 0) + amount
            return True
        return False
    
    def transfer_to_wallet(self, user_id, amount):
        """转到钱包"""
        user = self.get_user(user_id)
        if user and user.get("airdrop_earned", 0) >= amount:
            user["airdrop_earned"] -= amount
            return {"success": True, "amount": amount}
        return {"success": False, "error": "Insufficient airdrop balance"}

user_system = UserSystem()

# ==================== 配置 ====================

class Config:
    """全局配置"""
    
    portfolio = {
        "rabbit_weight": 35,
        "mole_weight": 35,
        "prediction_weight": 10,
        "copy_trade_weight": 10,
        "market_make_weight": 10
    }
    
    hft_config = {
        "scan_interval": 15,
        "quick_scan_count": 5,
        "quick_scan_interval": 0.5,
        "confidence_threshold": 8.0
    }
    
    position_config = {
        "check_interval": 60,
        "stop_loss": 2.0,
        "take_profit": 5.0,
        "max_positions": 5,
        "max_daily_trades": 10
    }
    
    risk_config = {
        "max_drawdown": 10.0,
        "max_position_size": 20,
        "min_trade_amount": 10,
        "gas_limit": 50
    }
    
    wallet = {"address": "", "connected": False, "network": "ethereum"}
    
    vpn = {"enabled": False, "provider": "", "status": "disconnected"}
    
    presets = {
        "conservative": {"name": "保守型", "rabbit_weight": 50, "mole_weight": 20, "prediction_weight": 15, "copy_trade_weight": 10, "market_make_weight": 5, "confidence_threshold": 9.0, "stop_loss": 1.5, "take_profit": 4.0},
        "balanced": {"name": "平衡型", "rabbit_weight": 35, "mole_weight": 35, "prediction_weight": 10, "copy_trade_weight": 10, "market_make_weight": 10, "confidence_threshold": 8.0, "stop_loss": 2.0, "take_profit": 5.0},
        "aggressive": {"name": "激进型", "rabbit_weight": 25, "mole_weight": 45, "prediction_weight": 10, "copy_trade_weight": 10, "market_make_weight": 10, "confidence_threshold": 7.0, "stop_loss": 3.0, "take_profit": 8.0}
    }
    
    status = {
        "running": False,
        "total_pnl": 0.0,
        "today_pnl": 0.0,
        "win_rate": 0.0,
        "positions": [],
        "signals": [],
        "last_update": ""
    }

config = Config()

# ==================== 路由 ====================

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

# --- 用户相关 ---
@app.route('/api/user/status')
def get_user_status():
    """获取当前用户状态"""
    user_id = session.get('user_id', 'guest')
    user = user_system.get_user(user_id)
    
    if user:
        return jsonify({
            "user": {
                "id": user["id"],
                "type": user["type"],
                "balance": user["balance"],
                "airdrop_earned": user.get("airdrop_earned", 0),
                "registered": user.get("registered", False),
                "wallet": user.get("wallet")
            }
        })
    return jsonify({"user": None})

@app.route('/api/user/register', methods=['POST'])
def register():
    """注册用户"""
    data = request.json
    guest_id = session.get('user_id', 'guest')
    username = data.get('username')
    password = data.get('password')
    wallet = data.get('wallet', '')
    
    if not username or not password:
        return jsonify({"success": False, "error": "Missing fields"})
    
    result = user_system.register_user(guest_id, username, password, wallet)
    
    if result["success"]:
        session['user_id'] = result["user_id"]
        session['username'] = username
    
    return jsonify(result)

@app.route('/api/user/login', methods=['POST'])
def login():
    """登录"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    # 简单验证
    for user_id, user in user_system.registered_users.items():
        if user["username"] == username and user["password"] == password:
            session['user_id'] = user_id
            session['username'] = username
            return jsonify({"success": True, "user": user})
    
    return jsonify({"success": False, "error": "Invalid credentials"})

@app.route('/api/user/wallet/transfer', methods=['POST'])
def transfer_to_wallet():
    """羊毛收益转到钱包"""
    data = request.json
    user_id = session.get('user_id', 'guest')
    amount = float(data.get('amount', 0))
    
    result = user_system.transfer_to_wallet(user_id, amount)
    return jsonify(result)

@app.route('/api/user/wallet/connect', methods=['POST'])
def connect_user_wallet():
    """连接钱包"""
    data = request.json
    user_id = session.get('user_id', 'guest')
    
    user = user_system.get_user(user_id)
    if user:
        user["wallet"] = data.get('address', '')
        user["network"] = data.get('network', 'ethereum')
        return jsonify({"success": True, "wallet": user["wallet"]})
    
    return jsonify({"success": False})

# --- 系统状态 ---
@app.route('/api/status')
def get_status():
    user_id = session.get('user_id', 'guest')
    user = user_system.get_user(user_id)
    
    return jsonify({
        "status": config.status,
        "wallet": user.get("wallet", {"address": "", "connected": False}) if user else config.wallet,
        "vpn": config.vpn,
        "user_balance": user["balance"] if user else 0,
        "airdrop_earned": user.get("airdrop_earned", 0) if user else 0
    })

@app.route('/api/config')
def get_config():
    return jsonify({
        "portfolio": config.portfolio,
        "hft_config": config.hft_config,
        "position_config": config.position_config,
        "risk_config": config.risk_config,
        "presets": config.presets
    })

@app.route('/api/config', methods=['POST'])
def update_config():
    data = request.json
    if "portfolio" in data: config.portfolio.update(data["portfolio"])
    if "hft_config" in data: config.hft_config.update(data["hft_config"])
    if "position_config" in data: config.position_config.update(data["position_config"])
    if "risk_config" in data: config.risk_config.update(data["risk_config"])
    return jsonify({"success": True})

@app.route('/api/preset/<name>')
def apply_preset(name):
    if name in config.presets:
        preset = config.presets[name]
        config.portfolio["rabbit_weight"] = preset["rabbit_weight"]
        config.portfolio["mole_weight"] = preset["mole_weight"]
        config.portfolio["prediction_weight"] = preset["prediction_weight"]
        config.portfolio["copy_trade_weight"] = preset["copy_trade_weight"]
        config.portfolio["market_make_weight"] = preset["market_make_weight"]
        config.hft_config["confidence_threshold"] = preset["confidence_threshold"]
        config.position_config["stop_loss"] = preset["stop_loss"]
        config.position_config["take_profit"] = preset["take_profit"]
        return jsonify({"success": True, "preset": preset})
    return jsonify({"success": False})

# --- 交易控制 ---
@app.route('/api/trading/start')
def start_trading():
    config.status["running"] = True
    config.status["last_update"] = datetime.now().isoformat()
    return jsonify({"success": True})

@app.route('/api/trading/stop')
def stop_trading():
    config.status["running"] = False
    config.status["last_update"] = datetime.now().isoformat()
    return jsonify({"success": True})

# --- 信号与交易 ---
@app.route('/api/signals')
def get_signals():
    signals = []
    coins = ["BTC", "ETH", "SOL", "XRP", "ADA", "AVAX", "DOT", "MATIC"]
    
    for coin in coins:
        if random.random() > 0.4:
            mode = random.choice(["rabbit", "mole"])
            action = "BUY" if random.random() > 0.3 else "HOLD"
            confidence = round(random.uniform(5, 10), 1)
            
            signals.append({
                "coin": coin,
                "mode": mode,
                "action": action,
                "confidence": confidence,
                "potential": round(random.uniform(3, 15), 1),
                "timestamp": datetime.now().isoformat()
            })
    
    config.status["signals"] = signals
    return jsonify({"signals": signals})

# --- 薅羊毛 ---
@app.route('/api/airdrop/hunt')
def hunt_airdrop():
    """薅羊毛"""
    user_id = session.get('user_id', 'guest')
    
    # 模拟空投
    airdrops = []
    coins = ["NEW", "AIRDROP", "FREE", "TOKEN", "COIN"]
    
    for coin in coins:
        if random.random() > 0.6:
            amount = random.uniform(1, 50)
            airdrops.append({
                "coin": coin,
                "amount": round(amount, 2),
                "timestamp": datetime.now().isoformat()
            })
            user_system.add_airdrop(user_id, amount)
    
    return jsonify({"success": True, "airdrops": airdrops})

@app.route('/api/airdrop/claim', methods=['POST'])
def claim_airdrop():
    """领取空投"""
    data = request.json
    user_id = session.get('user_id', 'guest')
    amount = float(data.get('amount', 0))
    
    if amount > 0:
        user_system.add_airdrop(user_id, amount)
        return jsonify({"success": True, "amount": amount})
    
    return jsonify({"success": False})

# --- 回测与模拟 ---
@app.route('/api/backtest', methods=['POST'])
def backtest():
    data = request.json
    days = data.get("days", 30)
    capital = data.get("capital", 10000)
    
    trades = random.randint(20, 100)
    wins = int(trades * random.uniform(0.5, 0.8))
    pnl = random.uniform(-500, 2000)
    
    return jsonify({
        "success": True,
        "results": {
            "period_days": days,
            "initial_capital": capital,
            "final_capital": round(capital + pnl, 2),
            "total_pnl": round(pnl, 2),
            "pnl_percent": round(pnl / capital * 100, 2),
            "total_trades": trades,
            "winning_trades": wins,
            "win_rate": round(wins / trades * 100, 1),
            "max_drawdown": round(random.uniform(5, 20), 1)
        }
    })

@app.route('/api/simulation', methods=['POST'])
def simulation():
    data = request.json
    user_id = session.get('user_id', 'guest')
    user = user_system.get_user(user_id)
    
    capital = data.get("capital", user["balance"] if user else 10000)
    days = data.get("days", 7)
    
    daily_data = []
    balance = capital
    
    for i in range(days):
        change = random.uniform(-5, 8)
        balance *= (1 + change / 100)
        
        daily_data.append({
            "day": i + 1,
            "date": f"2026-03-{12-i:02d}",
            "pnl": round(change * capital / 100, 2),
            "pnl_percent": round(change, 2),
            "balance": round(balance, 2)
        })
        
        # 更新用户余额
        if user:
            user["balance"] = balance
    
    return jsonify({
        "success": True,
        "simulation": {
            "initial_capital": capital,
            "final_capital": round(balance, 2),
            "total_pnl": round(balance - capital, 2),
            "pnl_percent": round((balance - capital) / capital * 100, 2),
            "daily_data": daily_data
        }
    })

# ==================== 主程序 ====================

def run_server(host='0.0.0.0', port=5000):
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           🪿 Go2Se Web UI 服务                            ║
║                                                              ║
║   🌐 http://localhost:{port}                                 ║
║   🪿 Go2Se - 量化交易系统                                  ║
║   💰 游客送1000USDT模拟交易                                ║
║   🎁 薅羊毛可转钱包                                        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    app.run(host=host, port=port, debug=False, threaded=True)

if __name__ == '__main__':
    run_server()
