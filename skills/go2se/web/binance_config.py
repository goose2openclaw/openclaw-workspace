#!/usr/bin/env python3
"""
Binance API 配置工具
"""

import json
from flask import Flask, jsonify, request

app = Flask(__name__)

# 存储配置 (实际应该存数据库或加密)
CONFIG_FILE = '/root/.openclaw/workspace/skills/go2se/web/binance_config.json'

def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except:
        return {'configured': False}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

@app.route('/')
def index():
    config = load_config()
    if config.get('configured'):
        return f"""
        <html>
        <head><title>Binance API 配置</title></head>
        <body style="font-family:sans-serif;padding:2rem;max-width:600px;margin:0 auto">
            <h1>✅ Binance API 已配置</h1>
            <p>API Key: <code>{config.get('api_key','')[:8]}...</code></p>
            <p>状态: {config.get('status','unknown')}</p>
            <p>功能: {', '.join(config.get('features',[]))}</p>
            <hr>
            <form method="POST" action="/configure">
                <h3>重新配置</h3>
                <input name="api_key" placeholder="API Key" style="width:100%;padding:8px;margin:8px 0">
                <input name="api_secret" placeholder="API Secret" style="width:100%;padding:8px;margin:8px 0">
                <button type="submit" style="padding:10px 20px;background:#f0b90b;color:#000;border:none;cursor:pointer">配置 Binance</button>
            </form>
        </body>
        </html>
        """
    return f"""
    <html>
    <head><title>Binance API 配置</title></head>
    <body style="font-family:sans-serif;padding:2rem;max-width:600px;margin:0 auto">
        <h1>🟡 配置 Binance API</h1>
        <form method="POST" action="/configure">
            <label>API Key:</label>
            <input name="api_key" placeholder="你的API Key" style="width:100%;padding:8px;margin:8px 0">
            <label>API Secret:</label>
            <input name="api_secret" placeholder="你的API Secret" style="width:100%;padding:8px;margin:8px 0">
            <button type="submit" style="padding:10px 20px;background:#f0b90b;color:#000;border:none;cursor:pointer;font-weight:bold">配置 Binance</button>
        </form>
        <hr>
        <h3>📌 配置步骤:</h3>
        <ol>
            <li>登录 <a href="https://www.binance.com" target="_blank">Binance.com</a></li>
            <li>右上角头像 → API Management</li>
            <li>创建新 API Key</li>
            <li>设置权限: 现货/合约交易 (不要提现)</li>
            <li>复制 API Key 和 Secret 填入上方</li>
        </ol>
    </body>
    </html>
    """

@app.route('/configure', methods=['POST'])
def configure():
    api_key = request.form.get('api_key', '').strip()
    api_secret = request.form.get('api_secret', '').strip()
    
    if not api_key or not api_secret:
        return "❌ 请填写完整的 API Key 和 Secret"
    
    config = {
        'configured': True,
        'api_key': api_key,
        'api_secret_masked': api_secret[:4] + '...' + api_secret[-4:] if len(api_secret) > 8 else '****',
        'features': ['spot_trading', 'futures', 'margin'],
        'status': 'active',
        'configured_at': '2026-03-13'
    }
    
    save_config(config)
    return f"""
    <html>
    <head><meta http-equiv="refresh" content="2;url=/"></head>
    <body style="font-family:sans-serif;padding:2rem;text-align:center">
        <h1>✅ 配置成功!</h1>
        <p>正在跳转...</p>
    </body>
    </html>
    """

@app.route('/api/status')
def status():
    config = load_config()
    if config.get('configured'):
        return jsonify({
            'configured': True,
            'api_key': config.get('api_key','')[:8] + '...',
            'features': config.get('features',[]),
            'status': config.get('status','active')
        })
    return jsonify({'configured': False})

if __name__ == '__main__':
    print("""
╔════════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║      🟡 Binance API 配置工具                                      ║
║                                                                    ║
║      🌐 http://localhost:5003                                     ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=5003, debug=False)
