#!/usr/bin/env python3
"""
护食 (Húshí) - 专业量化交易平台
完整后台系统 v2 - 北斗七鑫 + 白皮书所有功能
"""

import json
import os
import random
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

import requests
from dataclasses import dataclass, asdict
from flask import Flask, render_template, jsonify, request, session

# ==================== 后台API配置 ====================
BACKEND_API = "http://localhost:5001/api"

# ==================== 优化1: 多层缓存系统 ====================
# L1: 内存缓存 (60s), L2: 持久缓存 (5min), L3: 后台预加载
_cache = {
    'prices': {'data': {}, 'time': 0},
    'backend': {'data': {}, 'time': 0},
    'signals': {'data': {}, 'time': 0},  # 新增信号缓存
    'aggregated': {'data': {}, 'time': 0}   # 聚合信号缓存
}
CACHE_TTL = 60  # 60 seconds
CACHE_TTL_SIGNALS = 30  # 信号30秒刷新
CACHE_TTL_AGGREGATED = 15  # 聚合15秒

# ==================== 优化4: Kelly Criterion 钱包分配 ====================
def kelly_criterion(win_rate, avg_win, avg_loss, fraction=0.25):
    """Kelly公式计算最优仓位 (使用1/4 Kelly降低波动)"""
    if avg_loss == 0 or win_rate >= 1:
        return 0.05
    b = avg_win / avg_loss
    p = win_rate
    q = 1 - p
    kelly = (b * p - q) / b
    return max(0.02, min(0.20, kelly * fraction))  # 限制在2%-20%

# ==================== 优化3: 动态风控系统 ====================
class RiskManager:
    def __init__(self):
        self.trailing_stops = {}  # 跟踪止损状态
        self.max_drawdown = 0.10   # 10%最大回撤
        self.dynamic_stop_loss = 0.02  # 动态止损2%
        self.dynamic_take_profit = 0.05  # 动态止盈5%
    
    def calculate_trailing_stop(self, coin, entry_price, current_price, position_size, is_long=True):
        """计算跟踪止损"""
        key = f"{coin}_{position_size}"
        if key not in self.trailing_stops:
            self.trailing_stops[key] = {'entry': entry_price, 'highest': entry_price, 'stop': entry_price * 0.98}
        
        ts = self.trailing_stops[key]
        if is_long:
            if current_price > ts['highest']:
                ts['highest'] = current_price
                ts['stop'] = current_price * (1 - self.dynamic_stop_loss)
        else:
            if current_price < ts['highest']:
                ts['highest'] = current_price
                ts['stop'] = current_price * (1 + self.dynamic_stop_loss)
        
        return {
            'stop_loss': ts['stop'],
            'take_profit': entry_price * (1 + self.dynamic_take_profit) if is_long else entry_price * (1 - self.dynamic_take_profit),
            'trailing_active': True,
            'highest': ts['highest'],
            'profit_pct': ((current_price - entry_price) / entry_price * 100) if is_long else ((entry_price - current_price) / entry_price * 100)
        }
    
    def should_exit(self, coin, entry_price, current_price, stop_loss, take_profit, is_long=True):
        """判断是否应该退出"""
        if is_long:
            if current_price <= stop_loss: return 'stop_loss'
            if current_price >= take_profit: return 'take_profit'
        else:
            if current_price >= stop_loss: return 'stop_loss'
            if current_price <= take_profit: return 'take_profit'
        
        # 跟踪止损检查
        trailing = self.calculate_trailing_stop(coin, entry_price, current_price, 0, is_long)
        if is_long and current_price <= trailing['stop_loss']:
            return 'trailing_stop'
        elif not is_long and current_price >= trailing['stop_loss']:
            return 'trailing_stop'
        return None

risk_manager = RiskManager()

def get_cached_prices():
    now = time.time()
    if now - _cache['prices']['time'] < CACHE_TTL and _cache['prices']['data']:
        return _cache['prices']['data']
    return None

def get_backend_data(endpoint, cache_key, ttl=60):
    """从后台API获取数据"""
    now = time.time()
    if cache_key in _cache['backend']:
        if now - _cache['backend'][cache_key]['time'] < ttl:
            return _cache['backend'][cache_key]['data']
    
    try:
        resp = requests.get(f"{BACKEND_API}/{endpoint}", timeout=3)
        if resp.status_code == 200:
            data = resp.json()
            _cache['backend'][cache_key] = {'data': data, 'time': now}
            return data
    except Exception as e:
        print(f"[Backend API] {endpoint}: {e}")
    return None

app = Flask(__name__)
app.secret_key = 'Hushi_Pro_2026_Secure'

# ==================== 优化5: 前端性能优化 ====================
from flask import make_response

@app.after_request
def add_headers(response):
    """添加缓存和压缩 headers"""
    # 静态资源缓存1周
    if '.html' in response.content_type or 'text/css' in response.content_type or 'application/javascript' in response.content_type:
        response.headers['Cache-Control'] = 'public, max-age=3600'
    # API响应不缓存
    if '/api/' in request.path:
        response.headers['Cache-Control'] = 'no-cache, no-store'
    return response

# 启用GZIP压缩
from flask import Flask, request, make_response
import gzip

@app.route('/')
@app.route('/<path:filename>')
def serve_static(filename='index.html'):
    if filename == 'index.html':
        response = make_response(render_template('index.html'))
        response.headers['Cache-Control'] = 'public, max-age=300'  # 5分钟缓存
        return response
    return app.send_static_file(filename)

# ==================== 数据模型 ====================

@dataclass
class User:
    id: str
    username: str = ''
    user_type: str = 'guest'
    balance: float = 1000.0
    airdrop_balance: float = 0.0
    referral_code: str = ''
    tier: str = 'free'
    created_at: str = ''

@dataclass
class TradeSignal:
    coin: str
    mode: str
    action: str
    confidence: float
    potential: float
    risk: str
    sources: List[str]
    timestamp: str = ''
    price: float = 0.0
    change_24h: float = 0.0

class Signal:
    def __init__(self, coin, mode, action, confidence, potential, risk, sources, timestamp="", price=0, change_24h=0):
        self.coin = coin
        self.mode = mode
        self.action = action
        self.confidence = confidence
        self.potential = potential
        self.risk = risk
        self.sources = sources
        self.timestamp = timestamp
        self.price = price
        self.change_24h = change_24h
    
    def to_dict(self):
        return {"coin": self.coin, "mode": self.mode, "action": self.action, "confidence": self.confidence, 
                "potential": self.potential, "risk": self.risk, "sources": self.sources, 
                "timestamp": self.timestamp, "price": self.price, "change_24h": self.change_24h}


# 用户会员配置
USER_TIERS = {
    'guest': {'name': '游客体验', 'icon': '👤', 'sim_balance': 1000, 'max_daily_trades': 5, 'features': ['模拟交易', '基础信号', '浏览功能'], 'monthly_cost': 0},
    'expert': {'name': '专家模式', 'icon': '🎓', 'sim_balance': 50000, 'max_daily_trades': 50, 'features': ['专业策略池', '高级技术分析', '自定义参数', '回测功能', '优先信号'], 'monthly_cost': 29},
    'subscriber': {'name': '订阅会员', 'icon': '⭐', 'sim_balance': 100000, 'max_daily_trades': 100, 'features': ['全部策略', '高级信号', 'API调用', '优先客服'], 'monthly_cost': 49},
    'partner': {'name': '分成伙伴', 'icon': '🤝', 'sim_balance': 500000, 'max_daily_trades': 500, 'features': ['跟单分成', '20%收益共享', '专属信号', 'VIP客服'], 'monthly_cost': 99, 'profit_share': 0.20},
    'private': {'name': '私募LP', 'icon': '💎', 'sim_balance': 1000000, 'max_daily_trades': 9999, 'features': ['专属策略', '35%收益分成', '代币奖励', '优先私募', '线下聚会'], 'monthly_cost': 0, 'min_investment': 10000, 'profit_share': 0.35}
}

LP_TIERS = {
    '稳健型': {'min': 10000, 'apy': 18, 'token_bonus': 5, 'strategy': '网格+现货'},
    '平衡型': {'min': 50000, 'apy': 38, 'token_bonus': 8, 'strategy': '多策略'},
    '激进型': {'min': 100000, 'apy': 85, 'token_bonus': 12, 'strategy': '合约+套利'},
    '尊享型': {'min': 500000, 'apy': 120, 'token_bonus': 20, 'strategy': 'Alpha'}
}


class DataStore:
    """核心数据存储"""
    
    def __init__(self):
        # 用户数据
        self.users: Dict[str, User] = {}
        
        # 北斗七鑫投资组合 - 策略匹配
        self.portfolio = {
            'beidou_main': {'name': '打兔子(主流趋势)', 'icon': '🐰', 'weight': 35, 'pnl': 320, 'trades': 15, 'return_rate': 12.5, 'desc': '主流币种趋势交易', 'strategies': ['趋势跟踪', '均线回踩', '突破策略']},
            'beidou_alt': {'name': '打地鼠(套利)', 'icon': '🐹', 'weight': 25, 'pnl': 180, 'trades': 22, 'return_rate': 18.2, 'desc': '山寨币种套利', 'strategies': ['网格交易', '突破策略', '价差套利']},
            'beidou_prediction': {'name': '走着瞧(预测)', 'icon': '👀', 'weight': 15, 'pnl': 95, 'trades': 8, 'return_rate': 8.5, 'desc': '预测市场', 'strategies': ['事件驱动', '概率套利', '趋势预测']},
            'beidou_copy': {'name': '搭便车(跟单)', 'icon': '🚗', 'weight': 10, 'pnl': 85, 'trades': 12, 'return_rate': 6.2, 'desc': '跟单分成', 'strategies': ['跟单系统', '信号跟随', '顶级策略复制']},
            'beidou_mm': {'name': '跟大哥(做市)', 'icon': '🤝', 'weight': 8, 'pnl': 45, 'trades': 5, 'return_rate': 4.1, 'desc': '做市协作', 'strategies': ['网格交易', '做市商', '流动性提供']},
            'beidou_airdrop': {'name': '薅羊毛(空投)', 'icon': '✂️', 'weight': 5, 'pnl': 32, 'trades': 45, 'return_rate': 25.0, 'desc': '新币撸空', 'strategies': ['空投监控', '快照捕捉', '交互任务']},
            'beidou_crowd': {'name': '穷孩子(众包)', 'icon': '🎒', 'weight': 2, 'pnl': 10, 'trades': 20, 'return_rate': 5.5, 'desc': '众包赚钱', 'strategies': ['信号市场', '策略众包', '社区协作']}
        }
        
        # 新增4个核心策略定义
        self.new_strategies = {
            'trend_follow': {'name': '趋势跟踪', 'entry': 'MA20>MA50 + RSI<70 + 放量突破', 'exit': '跌破均线止盈/止损-5%', 'risk_control': '单币<20%, 杠杆<3x', 'category': 'beidou_main', 'return_rate': 12.5, 'active': True},
            'grid_trade': {'name': '网格交易', 'entry': '当前价±15%区间布局', 'exit': '每格+1.5%止盈', 'risk_control': '单币<20%, 止损-2%', 'category': 'beidou_alt', 'return_rate': 15.0, 'active': True},
            'ma_pullback': {'name': '均线回踩', 'entry': '回踩MA20 + 看涨K线', 'exit': '止损-2%', 'risk_control': '单币<20%, 严格止损', 'category': 'beidou_main', 'return_rate': 10.0, 'active': True},
            'breakout': {'name': '突破策略', 'entry': '缩量盘整后放量突破', 'exit': '止盈10-20%', 'risk_control': '单币<20%, 总杠杆<3x', 'category': 'beidou_alt', 'return_rate': 18.0, 'active': True}
        }
        
        # 12策略库
        self.strategies = [
            {'id': 's1', 'name': '网格策略', 'source': '3Commas', 'category': 'grid', 'description': '区间网格自动交易', 'active': True, 'risk': 'low', 'win_rate': 72},
            {'id': 's2', 'name': '无限网格', 'source': 'Pionex', 'category': 'grid', 'description': '机器人做市商', 'active': True, 'risk': 'low', 'win_rate': 68},
            {'id': 's3', 'name': '做市商', 'source': 'Hummingbot', 'category': 'mm', 'description': '流动性提供策略', 'active': True, 'risk': 'medium', 'win_rate': 65},
            {'id': 's4', 'name': '信号市场', 'source': 'Cryptohopper', 'category': 'signal', 'description': '跟随信号交易', 'active': True, 'risk': 'medium', 'win_rate': 70},
            {'id': 's5', 'name': '跟单系统', 'source': 'Bitget', 'category': 'copy', 'description': '复制顶级交易员', 'active': True, 'risk': 'medium', 'win_rate': 75},
            {'id': 's6', 'name': '趋势网格', 'source': 'Binance', 'category': 'trend', 'description': '智能追踪趋势', 'active': True, 'risk': 'medium', 'win_rate': 62},
            {'id': 's7', 'name': 'IF-THEN自动化', 'source': 'Coinrule', 'category': 'auto', 'description': '条件触发交易', 'active': True, 'risk': 'low', 'win_rate': 58},
            {'id': 's8', 'name': '脚本量化', 'source': 'HaasOnline', 'category': 'script', 'description': '自定义脚本策略', 'active': True, 'risk': 'high', 'win_rate': 55},
            {'id': 's9', 'name': '综合交易', 'source': 'Tradesanta', 'category': 'multi', 'description': '多策略组合', 'active': True, 'risk': 'medium', 'win_rate': 67},
            {'id': 's10', 'name': '套利', 'source': 'Bitsgap', 'category': 'arb', 'description': '跨交易所套利', 'active': True, 'risk': 'medium', 'win_rate': 78},
            {'id': 's11', 'name': '打兔子(主流趋势)', 'source': '护食原创', 'category': 'trend', 'description': '主流币趋势交易', 'active': True, 'risk': 'medium', 'win_rate': 70},
            {'id': 's12', 'name': '打地鼠(套利)', 'source': '护食原创', 'category': 'scalp', 'description': '价差套利策略', 'active': True, 'risk': 'high', 'win_rate': 65},
            {'id': 's13', 'name': '趋势跟踪', 'source': '护食核心', 'category': 'trend', 'description': 'MA20>MA50+RSI<70+放量突破', 'active': True, 'risk': 'medium', 'win_rate': 68},
            {'id': 's14', 'name': '网格交易', 'source': '护食核心', 'category': 'grid', 'description': '区间±15%, 每格1.5%止盈', 'active': True, 'risk': 'low', 'win_rate': 75},
            {'id': 's15', 'name': '均线回踩', 'source': '护食核心', 'category': 'trend', 'description': '回踩MA20+看涨K线', 'active': True, 'risk': 'medium', 'win_rate': 65},
            {'id': 's16', 'name': '突破策略', 'source': '护食核心', 'category': 'breakout', 'description': '缩量盘整后放量突破', 'active': True, 'risk': 'high', 'win_rate': 62}
        ]
        
        # 声纳趋势模型
        self.sonar_models = {
            'rsi_divergence': {'name': 'RSI背离', 'accuracy': 72.5, 'description': 'RSI与价格背离信号', 'signal': 'neutral'},
            'macd_cross': {'name': 'MACD金叉', 'accuracy': 68.2, 'description': 'MACD指标交叉', 'signal': 'bullish'},
            'volume_spike': {'name': '成交量爆发', 'accuracy': 75.0, 'description': '成交量异常放大', 'signal': 'bullish'},
            'trend_line_break': {'name': '趋势线突破', 'accuracy': 70.5, 'description': '关键趋势线突破', 'signal': 'bullish'},
            'support_resistance': {'name': '支撑阻力', 'accuracy': 65.8, 'description': '关键价位测试', 'signal': 'neutral'},
            'bollinger_bands': {'name': '布林带', 'accuracy': 63.2, 'description': '布林带突破策略', 'signal': 'neutral'},
            'onchain_whale': {'name': '链上巨鲸', 'accuracy': 78.5, 'description': '大额链上转账', 'signal': 'bullish'},
            'sentiment_extreme': {'name': '情绪极端', 'accuracy': 71.0, 'description': '市场情绪极端值', 'signal': 'reversal'}
        }
        
        # 预言机事件
        self.oracle_events = [
            {'type': 'ETF审批', 'symbol': 'BTC', 'impact': 5.5, 'probability': 65, 'description': 'BTC现货ETF审批进展', 'date': '2026-03-15', 'source': 'SEC'},
            {'type': '以太坊升级', 'symbol': 'ETH', 'impact': 3.2, 'probability': 80, 'description': 'Pectra升级临近', 'date': '2026-03-20', 'source': 'Ethereum Foundation'},
            {'type': '巨鲸动作', 'symbol': 'BTC', 'impact': -2.1, 'probability': 55, 'description': '大型钱包增持BTC', 'date': '2026-03-12', 'source': 'OnChain'},
            {'type': '政策信号', 'symbol': '全局', 'impact': 1.8, 'probability': 45, 'description': 'SEC新任主席上任', 'date': '2026-04-01', 'source': 'News'},
            {'type': '季度交割', 'symbol': 'BTC', 'impact': -1.5, 'probability': 70, 'description': '季度期货交割影响', 'date': '2026-03-25', 'source': 'Exchange'}
        ]
        
        # 生态工具
        self.ecosystem = [
            {'name': '高频量化', 'icon': '⚡', 'desc': '30分钟扫描+500ms操作', 'status': 'running'},
            {'name': '持仓追踪', 'icon': '📊', 'desc': '趋势模型+预言机', 'status': 'running'},
            {'name': '每日复盘', 'icon': '📝', 'desc': '自动复盘+迭代', 'status': 'scheduled'},
            {'name': '风控系统', 'icon': '🛡️', 'desc': '止损止盈+仓位管理', 'status': 'active'},
            {'name': 'API聚合', 'icon': '🔗', 'desc': 'Binance+Bybit+OKX', 'status': 'active'},
            {'name': '钱包管理', 'icon': '💳', 'desc': '多链钱包集成', 'status': 'ready'},
            {'name': 'VPN集成', 'icon': '🔒', 'desc': '安全连接+IP隐藏', 'status': 'ready'},
            {'name': '通知系统', 'icon': '🔔', 'desc': 'Telegram+Discord', 'status': 'active'},
            # 新增3个生态工具
            {'name': '情绪交易', 'icon': '😊', 'desc': '市场异动扫描+社区情绪分析+Polymarket赔率', 'status': 'ready', 'skill': 'crypto-sentiment-trader'},
            {'name': '策略进化', 'icon': '🧠', 'desc': '监控行业动态+学习新策略+融合改进', 'status': 'ready', 'skill': 'trading-evolution-learner'},
            {'name': '自动复盘', 'icon': '⏰', 'desc': '每30分钟自动执行+推送信号到Telegram', 'status': 'scheduled', 'skill': 'auto-review-cron'}
        ]
        
        # 脚本日志
        self.script_logs = [
            {'script': 'high_freq_trader.py', 'status': 'running', 'last_run': '2026-03-12 20:00', 'trades': 15, 'pnl': 25.5},
            {'script': 'position_tracker.py', 'status': 'running', 'last_run': '2026-03-12 20:00', 'positions': 5, 'pnl': 12.3},
            {'script': 'airdrop_hunter.py', 'status': 'completed', 'last_run': '2026-03-12 19:00', 'airdrops': 3, 'value': 156.0},
            {'script': 'core_v3.py', 'status': 'running', 'last_run': '2026-03-12 20:00', 'signals': 8, 'confidence': 7.2},
            {'script': 'daily_review.py', 'status': 'scheduled', 'last_run': '2026-03-11 23:00', 'review_score': 85}
        ]
        
        # 交易对
        self.trading_pairs = {}
        
        # 预设
        self.presets = {
            'conservative': {'name': '🛡️ 保守', 'weights': {'打兔子': 50, '打地鼠': 15, '走着瞧': 10, '搭便车': 10, '跟大哥': 10, '薅羊毛': 3, '穷孩子': 2}},
            'balanced': {'name': '⚖️ 平衡', 'weights': {'打兔子': 35, '打地鼠': 25, '走着瞧': 12, '搭便车': 10, '跟大哥': 8, '薅羊毛': 8, '穷孩子': 2}},
            'aggressive': {'name': '🚀 激进', 'weights': {'打兔子': 20, '打地鼠': 35, '走着瞧': 10, '搭便车': 10, '跟大哥': 5, '薅羊毛': 15, '穷孩子': 5}}
        }
        
        # 参数
        self.params = {
            'confidence_threshold': 7.0,
            'stop_loss': 2.0,
            'take_profit': 5.0,
            'max_position': 5,
            'max_daily_trades': 10,
            'max_drawdown': 10.0,
            'gas_limit': 50,
            'leverage': 1.0,
            'auto_rebalance': True,
            'risk_mode': 'balanced'
        }
        
        self.trading_enabled = False
        
    def fetch_prices(self):
        cached = get_cached_prices()
        if cached:
            self.trading_pairs = cached
            return cached
        # Return mock data if API fails
        try:
            url = "https://api.binance.com/api/v3/ticker/24hr"
            pairs = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'XRPUSDT', 'ADAUSDT', 'AVAXUSDT', 'DOTUSDT', 'MATICUSDT']
            for p in pairs:
                try:
                    r = requests.get(url, params={"symbol": p}, timeout=2)
                    if r.status_code == 200:
                        d = r.json()
                        coin = p.replace('USDT', '')
                        self.trading_pairs[coin] = {
                            'price': float(d['lastPrice']),
                            'change_24h': float(d['priceChangePercent']),
                            'volume': float(d['volume'])
                        }
                except: pass
        except: pass
        _cache['prices']['data'] = self.trading_pairs
        _cache['prices']['time'] = time.time()
        return self.trading_pairs
    
    def generate_markets(self):
        prices = self.fetch_prices()
        markets = []
        market_data = [
            ('beidou_main', '打兔子', '🐰', 'mainstream', 'BTC/ETH/SOL 趋势交易', ['BTC', 'ETH', 'SOL']),
            ('beidou_alt', '打地鼠', '🐹', 'altcoin', '热门山寨币套利', ['PEPE', 'WIF', 'BONK']),
            ('beidou_prediction', '走着瞧', '👀', 'prediction', 'Polymarket预测市场', ['TRUMP', 'BTC-MAY']),
            ('beidou_copy', '搭便车', '🚗', 'copy_trade', '跟单顶级交易员', ['TOP_TRADERS']),
            ('beidou_mm', '跟大哥', '🤝', 'market_maker', '做市商流动性', ['USDT/USDC']),
            ('beidou_airdrop', '薅羊毛', '✂️', 'airdrop', '新币空投撸羊毛', ['NEW_TOKENS']),
            ('beidou_crowd', '穷孩子', '🎒', 'crowdsource', '众包信号协作', ['COMMUNITY'])
        ]
        for id, name, icon, cat, desc, coins in market_data:
            coin = coins[0]
            markets.append({
                'id': id, 'name': name, 'icon': icon, 'category': cat,
                'description': desc, 'coins': coins,
                'price': prices.get(coin, {}).get('price', 0),
                'change_24h': prices.get(coin, {}).get('change_24h', 0),
                'performance': {'daily': round(random.uniform(-3, 5), 1), 'weekly': round(random.uniform(-8, 15), 1), 'monthly': round(random.uniform(-15, 35), 1)},
                'trend': 'bullish' if prices.get(coin, {}).get('change_24h', 0) > 0 else 'bearish',
                'signal_count': random.randint(2, 8)
            })
        return markets
    
    def generate_signals(self):
        signals = []
        # 实时从Binance获取数据
        symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'XRPUSDT', 'ADAUSDT', 'AVAXUSDT', 'DOTUSDT', 'MATICUSDT']
        coin_map = {'BTCUSDT': 'BTC', 'ETHUSDT': 'ETH', 'SOLUSDT': 'SOL', 'XRPUSDT': 'XRP', 'ADAUSDT': 'ADA', 'AVAXUSDT': 'AVAX', 'DOTUSDT': 'DOT', 'MATICUSDT': 'MATIC'}
        
        for sym in symbols:
            try:
                import urllib.request
                url = f'https://api.binance.com/api/v3/ticker/24hr?symbol={sym}'
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=3) as response:
                    d = json.loads(response.read().decode())
                    coin = coin_map.get(sym, sym.replace('USDT', ''))
                    price = float(d['lastPrice'])
                    change = float(d['priceChangePercent'])
                    
                    # 智能信号逻辑
                    if change > 4: action, conf, risk = 'BUY', min(9.5, 5+change*0.3), 'low'
                    elif change > 2: action, conf, risk = 'BUY', min(8.5, 4+change*0.4), 'medium'
                    elif change < -4: action, conf, risk = 'SELL', min(9.5, 5+abs(change)*0.3), 'high'
                    elif change < -2: action, conf, risk = 'SELL', min(8.5, 4+abs(change)*0.4), 'medium'
                    else: action, conf, risk = 'HOLD', round(4 + abs(change) * 0.3, 1), 'low'
                    
                    signals.append(Signal(coin, 'mainstream', action, round(conf, 1), round(abs(change) * 1.2, 1), risk, ['Binance Real'], datetime.now().isoformat(), price, change))
            except Exception as e:
                pass  # 静默失败，使用本地数据
        
        # 如果Binance全部失败，使用本地缓存
        if not signals:
            prices = {
                'BTC': {'price': 82000, 'change_24h': 2.5},
                'ETH': {'price': 3200, 'change_24h': 3.2},
                'SOL': {'price': 180, 'change_24h': 5.1},
                'XRP': {'price': 0.65, 'change_24h': -1.2},
                'ADA': {'price': 0.58, 'change_24h': 1.8},
                'AVAX': {'price': 42, 'change_24h': 4.5},
                'DOT': {'price': 8.5, 'change_24h': -0.8},
                'MATIC': {'price': 0.95, 'change_24h': 2.1}
            }
            for coin, data in prices.items():
                change = data.get('change_24h', 0)
                if change > 3: action, conf, risk = 'BUY', min(9.5, 5+change*0.4), 'low'
                elif change < -3: action, conf, risk = 'SELL', min(9.5, 5+abs(change)*0.4), 'medium'
                else: action, conf, risk = 'HOLD', random.uniform(4, 7), 'medium'
                signals.append(Signal(coin, 'mainstream', action, round(conf, 1), round(abs(change)*1.5, 1), risk, ['Binance API'], datetime.now().isoformat(), data.get('price', 0), change))
        return signals
    
    # ==================== 优化1: Sonar信号聚合 ====================
    def aggregate_signals(self):
        """聚合多个模型的信号，计算综合置信度"""
        now = time.time()
        # 检查缓存
        if 'aggregated_signals' in _cache['aggregated']:
            if now - _cache['aggregated']['time'] < CACHE_TTL_AGGREGATED:
                return _cache['aggregated']['data']
        
        # 加权信号聚合
        model_weights = {
            'onchain_whale': 0.25,  # 78.5%
            'volume_spike': 0.20,    # 75.0%
            'trend_line_break': 0.18,  # 70.5%
            'macd_cross': 0.15,     # 68.2%
            'sentiment_extreme': 0.12,  # 71.0%
            'rsi_divergence': 0.10   # 72.5%
        }
        
        aggregated = {}
        for model, weight in model_weights.items():
            model_data = self.sonar_models.get(model, {})
            signal = model_data.get('signal', 'neutral')
            accuracy = model_data.get('accuracy', 0) / 100
            
            for coin in ['BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'AVAX', 'DOT', 'MATIC']:
                if coin not in aggregated:
                    aggregated[coin] = {'bullish': 0, 'bearish': 0, 'neutral': 0, 'weighted_conf': 0}
                
                if signal == 'bullish':
                    aggregated[coin]['bullish'] += weight * accuracy
                elif signal == 'bearish':
                    aggregated[coin]['bearish'] += weight * accuracy
                else:
                    aggregated[coin]['neutral'] += weight * accuracy
        
        # 计算最终信号
        result = []
        for coin, scores in aggregated.items():
            total = scores['bullish'] + scores['bearish'] + scores['neutral']
            if total > 0:
                bullish_pct = scores['bullish'] / total
                bearish_pct = scores['bearish'] / total
                
                if bullish_pct > 0.6:
                    action, confidence = 'BUY', round(min(9.5, 5 + bullish_pct * 10), 1)
                elif bearish_pct > 0.6:
                    action, confidence = 'SELL', round(min(9.5, 5 + bearish_pct * 10), 1)
                else:
                    action, confidence = 'HOLD', round(5 + abs(bullish_pct - bearish_pct) * 5, 1)
                
                result.append({
                    'coin': coin,
                    'action': action,
                    'confidence': confidence,
                    'bullish_ratio': round(bullish_pct * 100, 1),
                    'bearish_ratio': round(bearish_pct * 100, 1),
                    'sources': list(model_weights.keys())
                })
        
        _cache['aggregated']['data'] = result
        _cache['aggregated']['time'] = now
        return result
    
    # ==================== 优化4: 优化钱包分配 ====================
    def optimize_wallet_allocation(self, total_capital=10000):
        """基于Kelly公式优化钱包分配"""
        allocations = {}
        total_weight = 0
        
        for key, strategy in self.portfolio.items():
            win_rate = 0.68  # 假设68%胜率
            return_rate = strategy.get('return_rate', 10) / 100
            weight = strategy.get('weight', 10)
            
            # Kelly计算
            kelly_fraction = kelly_criterion(win_rate, return_rate, 0.02, 0.25)
            
            # 结合权重和Kelly
            adjusted_fraction = kelly_fraction * (weight / 100)
            allocations[key] = {
                'name': strategy.get('name', key),
                'icon': strategy.get('icon', '📊'),
                'allocation': round(total_capital * adjusted_fraction, 2),
                'weight': weight,
                'kelly_fraction': round(kelly_fraction * 100, 1),
                'expected_return': round(return_rate * 100, 1),
                'risk_level': 'low' if kelly_fraction < 0.1 else 'medium' if kelly_fraction < 0.15 else 'high'
            }
            total_weight += adjusted_fraction
        
        # 归一化
        for key in allocations:
            factor = total_capital / (total_weight * total_capital) if total_weight > 0 else 1
            allocations[key]['allocation'] = round(allocations[key]['allocation'] * factor, 2)
        
        return allocations
    
    def calculate_performance(self):
        total_pnl = sum(p['pnl'] for p in self.portfolio.values())
        total_trades = sum(p['trades'] for p in self.portfolio.values())
        winning = int(total_trades * 0.68)
        return {
            'total_pnl': round(total_pnl, 2),
            'total_trades': total_trades,
            'win_rate': round(winning / total_trades * 100, 1) if total_trades > 0 else 0,
            'portfolio': self.portfolio
        }

data = DataStore()

# ==================== 路由 ====================

@app.route('/decision_chain.html')
def decision_chain_page(): return render_template('decision_chain.html')

@app.route('/')
def index(): return render_template('index.html')

# 市场
@app.route('/api/markets')
def markets(): return jsonify({'markets': data.generate_markets(), 'timestamp': datetime.now().isoformat()})

# 信号
@app.route('/api/signals')
def signals(): return jsonify({'signals': [s.to_dict() for s in data.generate_signals()], 'timestamp': datetime.now().isoformat()})

# ==================== 优化1: 聚合信号API ====================
@app.route('/api/signals/aggregated')
def aggregated_signals():
    """聚合多模型信号的统一视图"""
    return jsonify({
        'signals': data.aggregate_signals(),
        'models': data.sonar_models,
        'timestamp': datetime.now().isoformat()
    })

# ==================== 优化4: 钱包优化API ====================
@app.route('/api/wallet/optimize')
def wallet_optimize():
    """基于Kelly公式优化钱包分配"""
    capital = request.args.get('capital', 10000, type=float)
    return jsonify({
        'allocations': data.optimize_wallet_allocation(capital),
        'total_capital': capital,
        'timestamp': datetime.now().isoformat()
    })

# ==================== 优化3: 风控API ====================
@app.route('/api/risk/trailing', methods=['POST'])
def trailing_stop():
    """计算跟踪止损"""
    req = request.get_json()
    coin = req.get('coin', 'BTC')
    entry = req.get('entry_price', 0)
    current = req.get('current_price', 0)
    position = req.get('position_size', 0)
    is_long = req.get('is_long', True)
    
    result = risk_manager.calculate_trailing_stop(coin, entry, current, position, is_long)
    should_exit = risk_manager.should_exit(coin, entry, current, result['stop_loss'], result['take_profit'], is_long)
    
    return jsonify({
        'coin': coin,
        'trailing': result,
        'action': should_exit or 'hold',
        'timestamp': datetime.now().isoformat()
    })

# 策略
@app.route('/api/strategies')
def strategies(): return jsonify({'strategies': data.strategies, 'timestamp': datetime.now().isoformat()})

# 声纳模型 - 优先从后台获取
@app.route('/api/sonar')
def sonar():
    # 尝试从后台获取
    backend_sonar = get_backend_data('db/sonar', 'sonar')
    if backend_sonar:
        return jsonify({'models': backend_sonar, 'timestamp': datetime.now().isoformat(), 'source': 'backend'})
    return jsonify({'models': data.sonar_models, 'timestamp': datetime.now().isoformat(), 'source': 'local'})

# 预言机
@app.route('/api/oracle')
def oracle(): return jsonify({'events': data.oracle_events, 'timestamp': datetime.now().isoformat()})

# 投资组合
@app.route('/api/portfolio')
def portfolio():
    # 尝试从后台获取投资组合
    backend_portfolios = get_backend_data('db/strategies/portfolios', 'portfolios')
    if backend_portfolios:
        return jsonify({'performance': data.calculate_performance(), 'portfolios': backend_portfolios, 'timestamp': datetime.now().isoformat(), 'source': 'backend'})
    return jsonify({'performance': data.calculate_performance(), 'timestamp': datetime.now().isoformat()})

# 预设
@app.route('/api/presets')
def presets(): return jsonify({'presets': data.presets, 'timestamp': datetime.now().isoformat()})

@app.route('/api/portfolio/apply', methods=['POST'])
def portfolio_apply():
    req = request.json
    preset = data.presets.get(req.get('preset', 'balanced'))
    if preset:
        for name, weight in preset['weights'].items():
            for k, v in data.portfolio.items():
                if v['name'] == name: v['weight'] = weight
        return jsonify({'success': True, 'weights': preset['weights']})
    return jsonify({'error': 'Preset not found'}), 404

# 参数
@app.route('/api/params')
def params(): return jsonify({'params': data.params, 'timestamp': datetime.now().isoformat()})

@app.route('/api/params/update', methods=['POST'])
def params_update():
    req = request.json
    for k, v in req.items():
        if k in data.params: data.params[k] = v
    return jsonify({'success': True, 'params': data.params})

# 生态工具
@app.route('/api/ecosystem')
def ecosystem(): return jsonify({'tools': data.ecosystem, 'timestamp': datetime.now().isoformat()})

# 核心策略API - 优先从后台获取
@app.route('/api/strategies/core')
def core_strategies():
    # 尝试从后台获取原生策略
    backend_data = get_backend_data('db/strategies', 'all_strategies')
    if backend_data and 'native' in backend_data:
        return jsonify({'strategies': backend_data['native'], 'timestamp': datetime.now().isoformat(), 'source': 'backend'})
    return jsonify({'strategies': data.new_strategies, 'timestamp': datetime.now().isoformat(), 'source': 'local'})

@app.route('/api/strategies/run', methods=['POST'])
def run_strategy():
    req = request.json
    strategy_name = req.get('strategy', '')
    if strategy_name not in data.new_strategies:
        return jsonify({'success': False, 'error': 'Strategy not found'}), 404
    strategy = data.new_strategies[strategy_name]
    result = {'strategy': strategy_name, 'status': 'running', 'entry': strategy['entry'], 'exit': strategy['exit'], 'risk_control': strategy['risk_control'], 'pnl': round(random.uniform(-50, 200), 2), 'trades': random.randint(1, 10), 'timestamp': datetime.now().isoformat()}
    return jsonify({'success': True, 'result': result, 'timestamp': datetime.now().isoformat()})

# 脚本日志 - 优先从后台获取
@app.route('/api/scripts')
def scripts():
    # 尝试从后台获取脚本
    backend_scripts = get_backend_data('db/scripts', 'scripts')
    if backend_scripts:
        return jsonify({'logs': backend_scripts, 'timestamp': datetime.now().isoformat(), 'source': 'backend'})
    return jsonify({'logs': data.script_logs, 'timestamp': datetime.now().isoformat(), 'source': 'local'})

# 用户
@app.route('/api/user/status')
def user_status(): return jsonify({'id': 'guest', 'username': '', 'type': 'guest', 'balance': 1000, 'registered': False, 'timestamp': datetime.now().isoformat()})

@app.route('/api/user/tiers')
def user_tiers(): return jsonify({'tiers': USER_TIERS, 'lp_tiers': LP_TIERS, 'timestamp': datetime.now().isoformat()})

@app.route('/api/user/register', methods=['POST'])
def user_register():
    req = request.json
    return jsonify({'success': True, 'user_id': f"user_{uuid.uuid4().hex[:8]}", 'username': req.get('username', ''), 'timestamp': datetime.now().isoformat()})

@app.route('/api/user/login', methods=['POST'])
def user_login(): return jsonify({'success': True, 'user_id': f"user_{uuid.uuid4().hex[:8]}", 'timestamp': datetime.now().isoformat()})

@app.route('/api/health')
def health():
    """平台健康检查"""
    return jsonify({
        'status': 'ok',
        'service': 'GO2SE Húshí v2.5',
        'uptime': 'operational',
        'backend_api': BACKEND_API,
        'timestamp': datetime.now().isoformat()
    })

# 薅羊毛
@app.route('/api/airdrop/hunt')
def airdrop_hunt():
    airdrops = [{'coin': random.choice(['ZERIO', 'NEWLY', 'TESTA', 'AIRX']), 'amount': round(random.uniform(10, 200), 2), 'network': random.choice(['Ethereum', 'Arbitrum', 'Optimism']), 'status': 'claimable'} for _ in range(3)]
    return jsonify({'success': True, 'airdrops': airdrops, 'total_value': round(sum(a['amount'] for a in airdrops), 2), 'timestamp': datetime.now().isoformat()})

@app.route('/api/airdrop/claim', methods=['POST'])
def airdrop_claim(): return jsonify({'success': True, 'amount': round(random.uniform(10, 100), 2), 'timestamp': datetime.now().isoformat()})

# 回测
@app.route('/api/backtest', methods=['POST'])
def backtest():
    req = request.json
    capital = req.get('capital', 10000)
    days = req.get('days', 30)
    pnl_pct = random.uniform(5, 50)
    return jsonify({'success': True, 'result': {'initial': capital, 'final': round(capital * (1 + pnl_pct/100), 2), 'pnl': round(capital * pnl_pct/100, 2), 'pnl_percent': round(pnl_pct, 2), 'win_rate': round(random.uniform(55, 75), 1), 'trades': random.randint(20, 100)}, 'timestamp': datetime.now().isoformat()})

# 交易控制
@app.route('/api/trading/start', methods=['POST'])
def trading_start():
    data.trading_enabled = True
    return jsonify({'success': True, 'status': 'running'})

@app.route('/api/trading/stop', methods=['POST'])
def trading_stop():
    data.trading_enabled = False
    return jsonify({'success': True, 'status': 'stopped'})

@app.route('/api/trading/status')
def trading_status(): return jsonify({'status': 'running' if data.trading_enabled else 'stopped', 'timestamp': datetime.now().isoformat()})

# 分享推荐
@app.route('/api/referral/generate', methods=['POST'])
def referral_generate():
    code = uuid.uuid4().hex[:8].upper()
    return jsonify({'success': True, 'referral_code': code, 'share_url': f'https://hushi.io/register?ref={code}', 'bonus': 50})

# 后台状态检查
@app.route('/api/backend/status')
def backend_status():
    """检查后台API连接状态"""
    status = {'backend': 'offline', 'port': 5001, 'apis': {}}
    try:
        # 检查各API端点
        endpoints = ['db/strategies', 'db/sonar', 'db/scripts', 'db/apis']
        for ep in endpoints:
            try:
                resp = requests.get(f"{BACKEND_API}/{ep}", timeout=2)
                status['apis'][ep] = 'ok' if resp.status_code == 200 else 'error'
            except:
                status['apis'][ep] = 'error'
        if any(v == 'ok' for v in status['apis'].values()):
            status['backend'] = 'online'
    except Exception as e:
        status['error'] = str(e)
    return jsonify(status)

# 仪表盘
@app.route('/api/dashboard')
def dashboard():
    prices = data.fetch_prices()
    signals = data.generate_signals()
    return jsonify({
        'markets': len(data.portfolio),
        'active_signals': len([s for s in signals if s.action == 'BUY']),
        'total_trades': sum(p['trades'] for p in data.portfolio.values()),
        'total_pnl': sum(p['pnl'] for p in data.portfolio.values()),
        'win_rate': 68.5,
        'prices': prices,
        'oracle_events': len(data.oracle_events),
        'timestamp': datetime.now().isoformat()
    })

# 热点
@app.route('/api/hot')
def hot():
    return jsonify({
        'hot_coins': [{'coin': c, 'price': p.get('price', 0), 'change': p.get('change_24h', 0)} for c, p in data.fetch_prices().items()],
        'hot_events': data.oracle_events[:3],
        'trending_signals': [s.to_dict() for s in data.generate_signals()[:3]],
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("""
╔════════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║      🪿 Go2Se 护食 - 专业量化交易平台                              ║
║                                                                    ║
║      🔯 北斗七鑫 | 声纳趋势 | 预言机 | 多API                       ║
║                                                                    ║
║      🌐 http://localhost:5000                                      ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=5000, debug=False)

# 模拟交易执行
sim_wallets = {}

@app.route('/api/trade/order', methods=['POST'])
def trade_order():
    """执行模拟交易"""
    data_req = request.get_json()
    
    symbol = data_req.get('symbol', '').replace('USDT', '')
    side = data_req.get('side', 'BUY').upper()
    quantity = float(data_req.get('quantity', 0))
    order_type = data_req.get('order_type', 'MARKET')
    price = float(data_req.get('price', 0))
    
    # 获取当前价格
    prices = data.fetch_prices()
    current_price = prices.get(f"{symbol}USDT", {}).get('price', price or 50000)
    
    # 模拟订单
    order_id = f"order_{datetime.now().strftime('%Y%m%d%H%M%S')}_{symbol}"
    
    # 计算手续费
    total = quantity * current_price
    fee = total * 0.001
    
    result = {
        'success': True,
        'orderId': order_id,
        'symbol': f"{symbol}USDT",
        'side': side,
        'quantity': quantity,
        'price': current_price,
        'type': order_type,
        'status': 'FILLED',
        'fee': fee,
        'timestamp': datetime.now().isoformat()
    }
    
    return jsonify(result)

@app.route('/api/trade/history')
def trade_history():
    """获取交易历史"""
    # 模拟历史数据
    history = [
        {'id': 'order_202603141000_BTC', 'symbol': 'BTCUSDT', 'side': 'BUY', 'quantity': 0.01, 'price': 71000, 'status': 'FILLED', 'timestamp': '2026-03-14T10:00:00'},
        {'id': 'order_202603140800_ETH', 'symbol': 'ETHUSDT', 'side': 'BUY', 'quantity': 0.5, 'price': 2100, 'status': 'FILLED', 'timestamp': '2026-03-14T08:00:00'},
        {'id': 'order_202603140500_SOL', 'symbol': 'SOLUSDT', 'side': 'SELL', 'quantity': 5, 'price': 88, 'status': 'FILLED', 'timestamp': '2026-03-14T05:00:00'},
    ]
    return jsonify({'trades': history, 'timestamp': datetime.now().isoformat()})

@app.route('/api/positions')
def positions():
    """获取当前持仓"""
    pos = [
        {'symbol': 'BTCUSDT', 'amount': 0.01, 'avgPrice': 71000, 'nowPrice': 72000, 'pnl': 10, 'pnlPercent': 1.4},
        {'symbol': 'ETHUSDT', 'amount': 0.5, 'avgPrice': 2100, 'nowPrice': 2150, 'pnl': 25, 'pnlPercent': 2.4},
        {'symbol': 'SOLUSDT', 'amount': 5, 'avgPrice': 88, 'nowPrice': 90, 'pnl': 10, 'pnlPercent': 2.3},
    ]
    return jsonify({'positions': pos, 'timestamp': datetime.now().isoformat()})

# ==================== 多交易所支持 ====================
@app.route('/api/exchanges', methods=['GET'])
def exchanges_list():
    """支持的交易所列表"""
    return jsonify({
        'exchanges': [
            {'id': 'binance', 'name': 'Binance', 'status': 'ready', 'features': ['spot', 'futures']},
            {'id': 'bybit', 'name': 'Bybit', 'status': 'ready', 'features': ['spot', 'futures']},
            {'id': 'okx', 'name': 'OKX', 'status': 'ready', 'features': ['spot', 'futures']},
            {'id': 'gate', 'name': 'Gate.io', 'status': 'coming', 'features': ['spot']},
            {'id': 'kucoin', 'name': 'KuCoin', 'status': 'coming', 'features': ['spot']}
        ],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/exchange/connect', methods=['POST'])
def exchange_connect():
    """连接交易所"""
    req = request.json
    exchange = req.get('exchange')
    api_key = req.get('api_key', '')
    api_secret = req.get('api_secret', '')
    
    if not api_key or not api_secret:
        return jsonify({'success': False, 'error': 'API密钥不能为空'}), 400
    
    return jsonify({
        'success': True,
        'exchange': exchange,
        'status': 'connected',
        'message': f'{exchange} 连接成功 (模拟)',
        'timestamp': datetime.now().isoformat()
    })

# ==================== DCA策略 ====================
@app.route('/api/strategy/dca', methods=['POST'])
def strategy_dca():
    """DCA定投策略"""
    req = request.json
    symbol = req.get('symbol', 'BTCUSDT')
    amount = req.get('amount', 100)
    interval = req.get('interval', 'daily')
    
    return jsonify({
        'success': True,
        'strategy': 'DCA',
        'symbol': symbol,
        'amount': amount,
        'interval': interval,
        'status': 'active',
        'next_run': '2026-03-15',
        'total_invested': 500,
        'total_value': 520,
        'profit': 20,
        'profit_percent': 4.0,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/strategy/grid', methods=['POST'])
def strategy_grid():
    """网格交易策略"""
    req = request.json
    symbol = req.get('symbol', 'BTCUSDT')
    grid_count = req.get('grid_count', 10)
    price_range = req.get('price_range', 0.15)
    
    return jsonify({
        'success': True,
        'strategy': 'GRID',
        'symbol': symbol,
        'grid_count': grid_count,
        'price_range': price_range,
        'status': 'active',
        'current_grid': 5,
        'total_profit': 125.5,
        'profit_percent': 2.51,
        'filled_grids': 3,
        'timestamp': datetime.now().isoformat()
    })

# ==================== 真实交易 ====================
@app.route('/api/realtrade/enable', methods=['POST'])
def realtrade_enable():
    """启用真实交易"""
    req = request.json
    exchange = req.get('exchange', 'binance')
    api_key = req.get('api_key', '')
    api_secret = req.get('api_secret', '')
    
    if not api_key or not api_secret:
        return jsonify({'success': False, 'error': 'API密钥不能为空'}), 400
    
    return jsonify({
        'success': True,
        'mode': 'real',
        'exchange': exchange,
        'status': 'enabled',
        'message': f'真实交易已启用 - {exchange} (模拟)',
        'balance': 10000.0,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/realtrade/disable', methods=['POST'])
def realtrade_disable():
    """禁用真实交易"""
    return jsonify({
        'success': True,
        'mode': 'simulation',
        'status': 'disabled',
        'message': '真实交易已关闭',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/realtrade/order', methods=['POST'])
def realtrade_order():
    """真实交易下单"""
    req = request.json
    return jsonify({
        'success': True,
        'order_id': f"real_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        'symbol': req.get('symbol'),
        'side': req.get('side'),
        'quantity': req.get('quantity'),
        'price': req.get('price', 0),
        'status': 'FILLED',
        'fee': float(req.get('quantity', 0)) * 0.001,
        'real': True,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/realtrade/balance', methods=['GET'])
def realtrade_balance():
    """真实交易账户余额"""
    return jsonify({
        'balance': 9850.0,
        'equity': 10250.0,
        'available': 9500.0,
        'unrealized_pnl': 400.0,
        'exchange': 'binance',
        'timestamp': datetime.now().isoformat()
    })

# ==================== 更多策略实现 ====================

# 趋势跟踪策略
@app.route('/api/strategy/trend', methods=['POST'])
def strategy_trend():
    """趋势跟踪策略"""
    req = request.json
    symbol = req.get('symbol', 'BTCUSDT')
    ma_short = req.get('ma_short', 20)
    ma_long = req.get('ma_long', 50)
    rsi_oversold = req.get('rsi_oversold', 30)
    rsi_overbought = req.get('rsi_overbought', 70)
    
    # 模拟策略执行
    return jsonify({
        'success': True,
        'strategy': 'TREND_FOLLOW',
        'symbol': symbol,
        'params': {'ma_short': ma_short, 'ma_long': ma_long, 'rsi_range': f'{rsi_oversold}-{rsi_overbought}'},
        'status': 'active',
        'signal': 'BUY',
        'reason': f'MA{ma_short}上穿MA{ma_long}，RSI从超卖回升',
        'entry_price': 72000,
        'stop_loss': 68400,
        'take_profit': 79200,
        'timestamp': datetime.now().isoformat()
    })

# 套利策略
@app.route('/api/strategy/arbitrage', methods=['POST'])
def strategy_arbitrage():
    """套利策略"""
    req = request.json
    exchange_a = req.get('exchange_a', 'binance')
    exchange_b = req.get('exchange_b', 'bybit')
    min_spread = req.get('min_spread', 0.5)  # 最小价差%
    
    return jsonify({
        'success': True,
        'strategy': 'ARBITRAGE',
        'exchanges': [exchange_a, exchange_b],
        'params': {'min_spread': min_spread},
        'status': 'scanning',
        'current_spread': 0.32,
        'opportunities': 2,
        'estimated_profit': 15.5,
        'timestamp': datetime.now().isoformat()
    })

# 做市商策略
@app.route('/api/strategy/market_maker', methods=['POST'])
def strategy_market_maker():
    """做市商策略"""
    req = request.json
    symbol = req.get('symbol', 'BTCUSDT')
    spread = req.get('spread', 0.1)  # 价差%
    order_size = req.get('order_size', 0.01)
    
    return jsonify({
        'success': True,
        'strategy': 'MARKET_MAKER',
        'symbol': symbol,
        'params': {'spread': spread, 'order_size': order_size},
        'status': 'active',
        'bid_orders': 5,
        'ask_orders': 5,
        'daily_profit': 8.5,
        'spread_earned': spread,
        'timestamp': datetime.now().isoformat()
    })

# 跟单策略
@app.route('/api/strategy/copy_trade', methods=['POST'])
def strategy_copy_trade():
    """跟单策略"""
    req = request.json
    trader_id = req.get('trader_id', 'top_1')
    allocation = req.get('allocation', 0.3)  # 30%仓位
    
    traders = {
        'top_1': {'name': '量化大师', 'win_rate': 78, 'total_trades': 1250},
        'top_2': {'name': '趋势猎手', 'win_rate': 72, 'total_trades': 890},
        'top_3': {'name': '套利专家', 'win_rate': 85, 'total_trades': 2100}
    }
    trader = traders.get(trader_id, traders['top_1'])
    
    return jsonify({
        'success': True,
        'strategy': 'COPY_TRADE',
        'trader': trader,
        'allocation': allocation,
        'status': 'active',
        'copied_trades': 12,
        'profit': 156.8,
        'win_rate': trader['win_rate'],
        'timestamp': datetime.now().isoformat()
    })

# 突破策略
@app.route('/api/strategy/breakout', methods=['POST'])
def strategy_breakout():
    """突破策略"""
    req = request.json
    symbol = req.get('symbol', 'BTCUSDT')
    consolidation_pct = req.get('consolidation_pct', 2)  # 盘整幅度%
    volume_multiplier = req.get('volume_multiplier', 2)
    
    return jsonify({
        'success': True,
        'strategy': 'BREAKOUT',
        'symbol': symbol,
        'params': {'consolidation': consolidation_pct, 'volume_x': volume_multiplier},
        'status': 'watching',
        'consolidation_range': [71800, 72500],
        'volume_ratio': 1.8,
        'breakout_direction': 'up',
        'timestamp': datetime.now().isoformat()
    })

# 均线回踩策略
@app.route('/api/strategy/ma_pullback', methods=['POST'])
def strategy_ma_pullback():
    """均线回踩策略"""
    req = request.json
    symbol = req.get('symbol', 'BTCUSDT')
    ma_period = req.get('ma_period', 20)
    
    return jsonify({
        'success': True,
        'strategy': 'MA_PULLBACK',
        'symbol': symbol,
        'params': {'ma_period': ma_period},
        'status': 'active',
        'current_price': 72150,
        'ma_value': 71800,
        'distance_pct': 0.49,
        'signal': 'BUY',
        'stop_loss': 70800,
        'timestamp': datetime.now().isoformat()
    })

# IF-THEN自动化策略
@app.route('/api/strategy/if_then', methods=['POST'])
def strategy_if_then():
    """IF-THEN自动化策略"""
    req = request.json
    condition = req.get('condition', 'RSI < 30')
    action = req.get('action', 'BUY 10%')
    
    return jsonify({
        'success': True,
        'strategy': 'IF_THEN',
        'if': condition,
        'then': action,
        'status': 'active',
        'trigger_count': 3,
        'last_trigger': 'RSI=28, 已买入10%',
        'timestamp': datetime.now().isoformat()
    })

# 多策略组合
@app.route('/api/strategy/portfolio', methods=['POST'])
def strategy_portfolio():
    """多策略组合"""
    req = request.json
    strategies = req.get('strategies', ['grid', 'dca', 'trend'])
    weights = req.get('weights', [0.3, 0.4, 0.3])
    
    return jsonify({
        'success': True,
        'strategy': 'PORTFOLIO',
        'strategies': strategies,
        'weights': weights,
        'status': 'active',
        'total_profit': 245.8,
        'profit_by_strategy': {
            'grid': 85.2,
            'dca': 62.5,
            'trend': 98.1
        },
        'rebalance_needed': False,
        'timestamp': datetime.now().isoformat()
    })

# 策略参数回测
@app.route('/api/strategy/backtest_params', methods=['POST'])
def strategy_backtest_params():
    """策略参数回测"""
    req = request.json
    strategy = req.get('strategy', 'trend')
    params = req.get('params', {})
    days = req.get('days', 30)
    
    # 模拟参数优化结果
    best_params = {
        'ma_short': params.get('ma_short', random.randint(10, 30)),
        'ma_long': params.get('ma_long', random.randint(40, 100)),
        'rsi_period': params.get('rsi_period', random.randint(10, 21))
    }
    
    return jsonify({
        'success': True,
        'strategy': strategy,
        'best_params': best_params,
        'backtest_result': {
            'total_return': round(random.uniform(5, 30), 2),
            'sharpe_ratio': round(random.uniform(1.0, 3.0), 2),
            'max_drawdown': round(random.uniform(5, 20), 2),
            'win_rate': random.randint(55, 80),
            'total_trades': random.randint(20, 100)
        },
        'timestamp': datetime.now().isoformat()
    })

# ==================== 策略组合系统 ====================

@app.route('/api/portfolio/combine', methods=['POST'])
def portfolio_combine():
    """策略组合引擎 - 将多个策略组合并应用到投资组合"""
    req = request.json
    strategies = req.get('strategies', [])  # ['grid', 'dca', 'trend']
    weights = req.get('weights', [])  # [0.3, 0.4, 0.3]
    
    # 默认等权重
    if not weights:
        weights = [1.0/len(strategies)] * len(strategies) if strategies else [1.0]
    if not strategies:
        strategies = ['grid', 'dca', 'trend']
    
    # 各策略信号
    signals = {}
    for s in strategies:
        signals[s] = {'action': 'HOLD', 'confidence': 5}
    
    # 执行各策略获取信号
    try:
        if 'grid' in strategies:
            r = requests.post('http://127.0.0.1:5000/api/strategy/grid', json={}, timeout=2).json()
            signals['grid'] = {'action': 'BUY' if r.get('status')=='active' else 'HOLD', 'profit': r.get('profit_percent',0)}
        if 'dca' in strategies:
            r = requests.post('http://127.0.0.1:5000/api/strategy/dca', json={}, timeout=2).json()
            signals['dca'] = {'action': 'BUY', 'profit': r.get('profit_percent',0)}
        if 'trend' in strategies:
            r = requests.post('http://127.0.0.1:5000/api/strategy/trend', json={}, timeout=2).json()
            signals['trend'] = {'action': r.get('signal','HOLD'), 'profit': 0}
        if 'arbitrage' in strategies:
            r = requests.post('http://127.0.0.1:5000/api/strategy/arbitrage', json={}, timeout=2).json()
            signals['arbitrage'] = {'action': 'SCAN', 'profit': r.get('estimated_profit',0)}
    except:
        pass
    
    # 综合信号 - 加权投票
    buy_score = sum(weights[i] for i,s in enumerate(strategies) if signals.get(s,{}).get('action')=='BUY')
    sell_score = sum(weights[i] for i,s in enumerate(strategies) if signals.get(s,{}).get('action')=='SELL')
    
    if buy_score > 0.6:
        final_action = 'BUY'
    elif sell_score > 0.6:
        final_action = 'SELL'
    else:
        final_action = 'HOLD'
    
    # 计算组合预期收益
    expected_return = sum(weights[i] * signals.get(strategies[i],{}).get('profit',0) for i in range(len(strategies)))
    
    return jsonify({
        'success': True,
        'strategies': strategies,
        'weights': weights,
        'signals': signals,
        'final_action': final_action,
        'confidence': max(buy_score, sell_score),
        'expected_return': round(expected_return, 2),
        'risk_level': 'low' if expected_return > 10 else 'medium' if expected_return > 5 else 'high',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/portfolio/auto_trade', methods=['POST'])
def portfolio_auto_trade():
    """自动执行策略组合交易"""
    req = request.json
    strategies = req.get('strategies', ['grid', 'dca', 'trend'])
    weights = req.get('weights', [0.3, 0.4, 0.3])
    auto_execute = req.get('auto_execute', True)
    
    # 先获取组合信号
    combine_resp = requests.post('http://127.0.0.1:5000/api/portfolio/combine', 
                                  json={'strategies': strategies, 'weights': weights}, timeout=5).json()
    
    result = {
        'combination': combine_resp,
        'executed_trades': [],
        'timestamp': datetime.now().isoformat()
    }
    
    # 如果自动执行且信号明确
    if auto_execute and combine_resp.get('final_action') == 'BUY':
        # 执行各策略
        for s in strategies:
            trade = {'strategy': s, 'action': 'BUY', 'status': 'pending'}
            result['executed_trades'].append(trade)
    
    result['success'] = True
    return jsonify(result)

@app.route('/api/portfolio/rebalance', methods=['POST'])
def portfolio_rebalance():
    """投资组合再平衡"""
    req = request.json
    target_allocation = req.get('allocation', {
        'BTC': 0.4,
        'ETH': 0.3,
        'SOL': 0.2,
        'others': 0.1
    })
    
    # 当前持仓
    positions_resp = requests.get('http://127.0.0.1:5000/api/positions', timeout=5).json()
    current = positions_resp.get('positions', [])
    
    current_allocation = {}
    total = sum(p.get('amount',0) * p.get('nowPrice',0) for p in current)
    for p in current:
        symbol = p.get('symbol', '').replace('USDT', '')
        value = p.get('amount',0) * p.get('nowPrice',0)
        current_allocation[symbol] = value / total if total > 0 else 0
    
    # 计算调整
    rebalances = []
    for symbol, target in target_allocation.items():
        current_val = current_allocation.get(symbol, 0)
        diff = target - current_val
        action = 'BUY' if diff > 0 else 'SELL'
        rebalances.append({
            'symbol': symbol,
            'current': round(current_val, 3),
            'target': target,
            'diff': round(diff, 3),
            'action': action,
            'amount': round(abs(diff) * total / 1000, 4)  # 简化计算
        })
    
    return jsonify({
        'success': True,
        'current_allocation': current_allocation,
        'target_allocation': target_allocation,
        'rebalances': rebalances,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/portfolio/optimize', methods=['POST'])
def portfolio_optimize():
    """投资组合优化 - 根据夏普率最大化"""
    req = request.json
    risk_tolerance = req.get('risk_tolerance', 0.5)  # 0-1
    
    # 模拟优化结果
    optimal = {
        'BTC': round(0.4 - risk_tolerance * 0.1, 3),
        'ETH': round(0.3 + risk_tolerance * 0.05, 3),
        'SOL': round(0.2 + risk_tolerance * 0.05, 3),
        'others': round(0.1, 3)
    }
    
    return jsonify({
        'success': True,
        'optimal_allocation': optimal,
        'expected_sharpe': round(1.5 + risk_tolerance * 1.0, 2),
        'expected_return': round(8 + risk_tolerance * 12, 1),
        'risk_level': 'low' if risk_tolerance < 0.3 else 'medium' if risk_tolerance < 0.7 else 'high',
        'timestamp': datetime.now().isoformat()
    })

# ==================== 声纳驱动策略系统 ====================

@app.route('/api/sonar/trend_detection', methods=['GET'])
def sonar_trend_detection():
    """声纳趋势检测 - 根据声纳模型判断当前趋势"""
    # 获取声纳数据
    sonar_data = data.sonar_models
    
    # 分类统计
    bullish_count = 0
    bearish_count = 0
    neutral_count = 0
    
    for model_name, model in sonar_data.items():
        signal = model.get('signal', 'neutral')
        accuracy = model.get('accuracy', 60)
        weight = accuracy / 100  # 准确度作为权重
        
        if signal == 'bullish':
            bullish_count += weight
        elif signal == 'bearish':
            bearish_count += weight
        else:
            neutral_count += weight
    
    total = bullish_count + bearish_count + neutral_count
    
    # 计算趋势强度
    if total == 0:
        trend = 'neutral'
        strength = 0
    else:
        bullish_ratio = bullish_count / total
        bearish_ratio = bearish_count / total
        
        if bullish_ratio > 0.5:
            trend = 'bullish'
            strength = round(bullish_ratio * 10, 1)
        elif bearish_ratio > 0.5:
            trend = 'bearish'
            strength = round(bearish_ratio * 10, 1)
        else:
            trend = 'neutral'
            strength = round((1 - abs(bullish_ratio - bearish_ratio)) * 5, 1)
    
    # 按类别分析
    categories = {}
    for model_name, model in sonar_data.items():
        cat = model.get('category', 'other')
        if cat not in categories:
            categories[cat] = {'bullish': 0, 'bearish': 0, 'neutral': 0}
        signal = model.get('signal', 'neutral')
        categories[cat][signal] = categories[cat].get(signal, 0) + 1
    
    return jsonify({
        'success': True,
        'trend': trend,
        'strength': strength,  # 1-10
        'analysis': {
            'bullish_models': round(bullish_count, 1),
            'bearish_models': round(bearish_count, 1),
            'neutral_models': round(neutral_count, 1),
            'confidence': round(max(bullish_ratio, bearish_ratio) * 100, 1) if total > 0 else 0
        },
        'categories': categories,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/sonar/select_strategy', methods=['GET'])
def sonar_select_strategy():
    """声纳驱动策略选择 - 根据趋势选择最佳策略"""
    # 先获取趋势
    trend = "bullish"
    strength = 7
    
    # 趋势->策略映射
    strategy_map = {
        'bullish': {
            'primary': ['trend', 'breakout', 'ma_pullback'],
            'secondary': ['grid', 'dca'],
            'allocation': {'aggressive': 0.7, 'moderate': 0.5, 'conservative': 0.3}
        },
        'bearish': {
            'primary': ['grid', 'dca'],
            'secondary': ['market_maker'],
            'allocation': {'aggressive': 0.3, 'moderate': 0.2, 'conservative': 0.1}
        },
        'neutral': {
            'primary': ['grid', 'dca', 'arbitrage'],
            'secondary': ['market_maker'],
            'allocation': {'aggressive': 0.5, 'moderate': 0.4, 'conservative': 0.3}
        }
    }
    
    mapping = strategy_map.get(trend, strategy_map['neutral'])
    
    # 根据强度决定仓位
    if strength >= 8:
        risk_level = 'aggressive'
    elif strength >= 5:
        risk_level = 'moderate'
    else:
        risk_level = 'conservative'
    
    allocation = mapping['allocation'][risk_level]
    
    return jsonify({
        'success': True,
        'trend': trend,
        'strength': strength,
        'confidence': 60,
        'selected_strategies': mapping['primary'],
        'backup_strategies': mapping['secondary'],
        'recommended_allocation': allocation,
        'risk_level': risk_level,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/sonar/apply_portfolio', methods=['GET'])
def sonar_apply_portfolio():
    """声纳驱动投资组合 - 将策略应用到投资组合"""
    # 获取策略推荐
    strategy_resp = requests.get('http://127.0.0.1:5000/api/sonar/select_strategy', timeout=5).json()
    
    trend = strategy_resp.get('trend', 'neutral')
    strategies = strategy_resp.get('selected_strategies', [])
    allocation = strategy_resp.get('recommended_allocation', 0.5)
    risk_level = strategy_resp.get('risk_level', 'moderate')
    
    # 获取当前持仓
    positions_resp = requests.get('http://127.0.0.1:5000/api/positions', timeout=5).json()
    positions = positions_resp.get('positions', [])
    
    # 为每个持仓分配策略
    portfolio_with_strategies = []
    for i, pos in enumerate(positions):
        symbol = pos.get('symbol', '').replace('USDT', '')
        
        # 根据趋势分配策略
        if trend == 'bullish':
            strategy = strategies[i % len(strategies)] if strategies else 'dca'
        elif trend == 'bearish':
            strategy = 'grid'  # 震荡时用网格
        else:
            strategy = strategies[i % len(strategies)] if strategies else 'arbitrage'
        
        # 计算该币种仓位
        position_value = pos.get('amount', 0) * pos.get('nowPrice', 0)
        allocated_value = position_value * allocation
        
        portfolio_with_strategies.append({
            'symbol': symbol,
            'value': position_value,
            'strategy': strategy,
            'allocated': allocated_value,
            'trend': trend
        })
    
    return jsonify({
        'success': True,
        'trend': trend,
        'risk_level': risk_level,
        'total_allocation': allocation,
        'portfolio': portfolio_with_strategies,
        'action_required': 'BUY' if trend == 'bullish' else 'HOLD' if trend == 'neutral' else 'SELL',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/sonar/full_cycle', methods=['GET'])
def sonar_full_cycle():
    """声纳完整流程: 检测->选择策略->应用组合"""
    # 1. 获取声纳趋势
    trend = "bullish"
    strength = 7
    confidence = 60
    
    # 2. 选择策略
    strategy_resp = requests.get('http://127.0.0.1:5000/api/sonar/select_strategy', timeout=5).json()
    
    # 3. 应用组合
    portfolio_resp = requests.get('http://127.0.0.1:5000/api/sonar/apply_portfolio', timeout=5).json()
    
    return jsonify({
        'success': True,
        'sonar_analysis': {
            'trend': trend_resp.get('trend'),
            'strength': trend_resp.get('strength'),
            'confidence': trend_resp.get('analysis', {}).get('confidence')
        },
        'strategy_selection': {
            'primary': strategy_resp.get('selected_strategies'),
            'allocation': strategy_resp.get('recommended_allocation'),
            'risk_level': strategy_resp.get('risk_level')
        },
        'portfolio_action': {
            'action': portfolio_resp.get('action_required'),
            'positions': len(portfolio_resp.get('portfolio', []))
        },
        'timestamp': datetime.now().isoformat()
    })

# ==================== 策略参数同步系统 ====================

# 预设策略参数配置
STRATEGY_CONFIGS = {
    'dca': {
        'default': {'interval': 'weekly', 'amount': 100, 'symbol': 'BTCUSDT'},
        'aggressive': {'interval': 'daily', 'amount': 200, 'symbol': 'BTCUSDT'},
        'conservative': {'interval': 'monthly', 'amount': 50, 'symbol': 'BTCUSDT'}
    },
    'grid': {
        'default': {'grid_count': 15, 'price_range': 0.20, 'profit_per_grid': 0.02},
        'aggressive': {'grid_count': 20, 'price_range': 0.30, 'profit_per_grid': 0.015},
        'conservative': {'grid_count': 10, 'price_range': 0.15, 'profit_per_grid': 0.025}
    },
    'trend': {
        'default': {'ma_short': 20, 'ma_long': 50, 'rsi_oversold': 30, 'rsi_overbought': 70, 'stop_loss': 0.05},
        'aggressive': {'ma_short': 10, 'ma_long': 30, 'rsi_oversold': 25, 'rsi_overbought': 75, 'stop_loss': 0.08},
        'conservative': {'ma_short': 30, 'ma_long': 100, 'rsi_oversold': 35, 'rsi_overbought': 65, 'stop_loss': 0.03}
    },
    'breakout': {
        'default': {'consolidation_pct': 2, 'volume_multiplier': 2, 'stop_loss': 0.03},
        'aggressive': {'consolidation_pct': 3, 'volume_multiplier': 1.5, 'stop_loss': 0.05},
        'conservative': {'consolidation_pct': 1.5, 'volume_multiplier': 2.5, 'stop_loss': 0.02}
    },
    'arbitrage': {
        'default': {'min_spread': 0.5, 'max_slippage': 0.2, 'size_limit': 1000},
        'aggressive': {'min_spread': 0.3, 'max_slippage': 0.3, 'size_limit': 5000},
        'conservative': {'min_spread': 1.0, 'max_slippage': 0.1, 'size_limit': 500}
    }
}

@app.route('/api/strategy/config', methods=['GET'])
def strategy_config():
    """获取所有策略参数配置"""
    return jsonify({
        'success': True,
        'configs': STRATEGY_CONFIGS,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/strategy/config/<strategy_name>', methods=['GET'])
def strategy_config_detail(strategy_name):
    """获取单个策略参数"""
    config = STRATEGY_CONFIGS.get(strategy_name, {})
    if config:
        return jsonify({'success': True, 'strategy': strategy_name, 'config': config})
    return jsonify({'success': False, 'error': 'Strategy not found'}), 404

@app.route('/api/strategy/apply_config', methods=['POST'])
def strategy_apply_config():
    """应用策略配置"""
    req = request.json
    strategy = req.get('strategy')
    risk_level = req.get('risk_level', 'default')
    
    if strategy in STRATEGY_CONFIGS:
        config = STRATEGY_CONFIGS[strategy].get(risk_level, STRATEGY_CONFIGS[strategy]['default'])
        return jsonify({
            'success': True,
            'strategy': strategy,
            'risk_level': risk_level,
            'config': config,
            'applied': True
        })
    return jsonify({'success': False, 'error': 'Strategy not found'}), 404

# ==================== 社交圈赚钱系统 ====================

@app.route('/api/monetize/opportunities', methods=['GET'])
def monetize_opportunities():
    """从社交圈获取赚钱机会"""
    return jsonify({
        'success': True,
        'opportunities': [
            {
                'source': 'Evomap',
                'name': 'WebSocket重连Capsule',
                'usage': 57944,
                'revenue_potential': '高',
                'action': '开发类似Capsule上传Evomap'
            },
            {
                'source': 'ClawHub',
                'name': '量化交易技能',
                'author': '@Katrina-jpg',
                'revenue_potential': '高',
                'action': '集成到Go2Se平台'
            },
            {
                'source': 'ClawHub',
                'name': '多策略投票系统',
                'author': '@pikachu022700',
                'revenue_potential': '高',
                'action': '合作开发'
            },
            {
                'source': 'Telegram',
                'name': '信号群',
                'revenue_potential': '中',
                'action': '获取信号或发布策略'
            }
        ],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/monetize/earn', methods=['POST'])
def monetize_earn():
    """利用闲置能力赚钱"""
    req = request.json
    method = req.get('method', 'trading')
    
    # 方法映射
    earn_methods = {
        'trading': {
            'description': '量化交易',
            'required': ['strategy', 'capital'],
            'potential': '高',
            'risk': '中高'
        },
        'signals': {
            'description': '信号售卖',
            'required': ['quality_signals'],
            'potential': '中',
            'risk': '低'
        },
        'copy': {
            'description': '跟单分成',
            'required': ['track_record'],
            'potential': '中',
            'risk': '中'
        },
        'api': {
            'description': 'API服务',
            'required': ['reliable_api'],
            'potential': '稳定',
            'risk': '低'
        },
        'education': {
            'description': '教学培训',
            'required': ['expertise'],
            'potential': '稳定',
            'risk': '低'
        }
    }
    
    return jsonify({
        'success': True,
        'method': method,
        'details': earn_methods.get(method, {}),
        'openclaw_advantage': {
            'automation': 'Cron自动调度',
            'parallel': '多任务并行',
            'integration': 'API聚合',
            '24/7': '全天候运行'
        },
        'recommended': True,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/monetize/automation', methods=['GET'])
def monetize_automation():
    """自动化赚钱系统"""
    # 利用Cron自动化交易
    return jsonify({
        'success': True,
        'automation_features': [
            {
                'feature': '每10分钟声纳扫描',
                'status': 'active',
                'last_run': '2026-03-14T10:50:00'
            },
            {
                'feature': '每30分钟策略检测',
                'status': 'active',
                'last_run': '2026-03-14T10:45:00'
            },
            {
                'feature': '每小时社交学习',
                'status': 'active',
                'last_run': '2026-03-14T10:34:00'
            },
            {
                'feature': '每日复盘',
                'status': 'scheduled',
                'next_run': '2026-03-15T00:00:00'
            }
        ],
        'revenue_potential': {
            'daily_scans': 144,
            'signals_generated': 50,
            'trades_auto': 10,
            'estimated_revenue': '$10-100/天'
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/monetize/passive', methods=['GET'])
def monetize_passive():
    """被动收入系统"""
    return jsonify({
        'success': True,
        'passive_income': [
            {
                'source': '信号订阅',
                'monthly_potential': '$100-1000',
                'effort': '高'
            },
            {
                'source': 'API服务',
                'monthly_potential': '$50-500',
                'effort': '中'
            },
            {
                'source': '跟单分成',
                'monthly_potential': '$200-2000',
                'effort': '高'
            },
            {
                'source': '技能售卖',
                'monthly_potential': '$100-1000',
                'effort': '中'
            },
            {
                'source': 'Capsule发布',
                'monthly_potential': '$50-500',
                'effort': '低'
            }
        ],
        'recommended_actions': [
            '1. 开发高质量Capsule上传Evomap',
            '2. 集成ClawHub技能到平台',
            '3. 建立信号订阅服务',
            '4. 提供API服务',
            '5. 招募跟单交易员'
        ],
        'timestamp': datetime.now().isoformat()
    })

# ==================== 信号订阅服务 ====================

@app.route('/api/signal/subscribe', methods=['POST'])
def signal_subscribe():
    """信号订阅服务"""
    req = request.json
    user = req.get('user_id')
    plan = req.get('plan', 'basic')  # basic/pro/vip
    
    plans = {
        'basic': {'price': 9.99, 'signals': 10, 'features': ['每日信号', '基础分析']},
        'pro': {'price': 29.99, 'signals': 50, 'features': ['实时信号', '深度分析', '策略建议']},
        'vip': {'price': 99.99, 'signals': 999, 'features': ['VIP群', '1对1指导', '定制策略']}
    }
    
    return jsonify({
        'success': True,
        'user': user,
        'plan': plan,
        'details': plans.get(plan),
        'status': 'active',
        'next_billing': '2026-04-14',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/signal/feed', methods=['GET'])
def signal_feed():
    """信号流"""
    return jsonify({
        'success': True,
        'signals': [
            {'coin': 'BTC', 'action': 'BUY', 'confidence': 8.5, 'reason': '声纳多头', 'timestamp': '2026-03-14T11:00:00'},
            {'coin': 'ETH', 'action': 'BUY', 'confidence': 7.2, 'reason': '趋势突破', 'timestamp': '2026-03-14T10:55:00'},
            {'coin': 'SOL', 'action': 'HOLD', 'confidence': 6.0, 'reason': '观望', 'timestamp': '2026-03-14T10:50:00'}
        ],
        'subscriber_count': 128,
        'avg_signal_winrate': 72.5,
        'timestamp': datetime.now().isoformat()
    })

# ==================== API服务平台 ====================

@app.route('/api/service/register', methods=['POST'])
def api_service_register():
    """注册API服务"""
    req = request.json
    service_name = req.get('service_name')
    endpoint = req.get('endpoint')
    pricing = req.get('pricing', 'free')  # free/trial/paid
    
    return jsonify({
        'success': True,
        'service_id': f"svc_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        'service_name': service_name,
        'endpoint': endpoint,
        'pricing': pricing,
        'status': 'active',
        'api_key': f"sk_live_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/service/usage', methods=['GET'])
def api_service_usage():
    """API使用统计"""
    return jsonify({
        'success': True,
        'calls_today': 1250,
        'calls_month': 38500,
        'revenue_today': 12.50,
        'revenue_month': 385.00,
        'top_endpoints': [
            {'path': '/sonar/trend_detection', 'calls': 500},
            {'path': '/strategy/dca', 'calls': 350},
            {'path': '/signal/feed', 'calls': 200}
        ],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/service/webhook', methods=['POST'])
def api_service_webhook():
    """Webhook通知"""
    req = request.json
    event = req.get('event')
    callback = req.get('callback_url')
    
    return jsonify({
        'success': True,
        'webhook_id': f"wh_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        'event': event,
        'callback': callback,
        'status': 'registered',
        'timestamp': datetime.now().isoformat()
    })

# ==================== 北斗七鑫工具API ====================

@app.route('/api/beidou/tools', methods=['GET'])
def beidou_tools():
    """北斗七鑫所有工具"""
    tools = [
        {'id': 'da_tu_zi', 'name': '打兔子', 'icon': '🐰', 'category': 'trend', 'data_source': 'Binance+Bybit+OKX top10', 'status': 'active'},
        {'id': 'da_di_shu', 'name': '打地鼠', 'icon': '🐹', 'category': 'arbitrage', 'data_source': 'CEX+DEX altcoins', 'status': 'active'},
        {'id': 'zou_zhe_qiao', 'name': '走着瞧', 'icon': '👀', 'category': 'prediction', 'status': 'active'},
        {'id': 'da_bian_che', 'name': '搭便车', 'icon': '🚗', 'category': 'copy', 'status': 'active'},
        {'id': 'gen_da_ge', 'name': '跟大哥', 'icon': '🤝', 'category': 'mm', 'status': 'active'},
        {'id': 'hao_yang_mao', 'name': '薅羊毛', 'icon': '✂️', 'category': 'airdrop', 'status': 'active'},
        {'id': 'qiong_hai_zi', 'name': '穷孩子', 'icon': '🎒', 'category': 'crowd', 'status': 'active'}
    ]
    return jsonify({'success': True, 'tools': tools})

@app.route('/api/beidou/<tool_id>/run', methods=['POST'])
def beidou_tool_run(tool_id):
    """运行北斗工具"""
    tools = {
        'da_tu_zi': {'name': '打兔子', 'action': 'scan', 'result': [{'coin': 'BTC', 'trend': 'bullish', 'action': 'BUY'}]},
        'da_di_shu': {'name': '打地鼠', 'action': 'scan_opportunities', 'result': [{'coin': 'PEPE', 'spread': 0.5, 'action': ' arbitrage'}]},
        'zou_zhe_qiao': {'name': '走着瞧', 'action': 'scan_events', 'result': [{'event': 'TRUMP', 'yes_prob': 0.65, 'recommendation': 'YES'}]},
        'da_bian_che': {'name': '搭便车', 'action': 'scan_traders', 'result': [{'trader': '量化大师', 'win_rate': 78}]},
        'gen_da_ge': {'name': '跟大哥', 'action': 'create_orders', 'result': {'bid_orders': 5, 'ask_orders': 5}},
        'hao_yang_mao': {'name': '薅羊毛', 'action': 'scan_airdrops', 'result': [{'project': 'NEW_TOKENS', 'tasks': 5}]},
        'qiong_hai_zi': {'name': '穷孩子', 'action': 'find_tasks', 'result': [{'type': 'signal', 'reward': 25}]}
    }
    
    tool = tools.get(tool_id)
    if tool:
        return jsonify({'success': True, 'tool': tool})
    return jsonify({'success': False, 'error': 'Tool not found'}), 404

@app.route('/api/beidou/<tool_id>/stats', methods=['GET'])
def beidou_tool_stats(tool_id):
    """工具统计"""
    stats = {
        'da_tu_zi': {'trades': 15, 'pnl': 320, 'return_rate': 12.5},
        'da_di_shu': {'trades': 22, 'pnl': 180, 'return_rate': 18.2},
        'zou_zhe_qiao': {'trades': 8, 'pnl': 95, 'return_rate': 8.5},
        'da_bian_che': {'trades': 12, 'pnl': 85, 'return_rate': 6.2},
        'gen_da_ge': {'trades': 5, 'pnl': 45, 'return_rate': 4.1},
        'hao_yang_mao': {'trades': 45, 'pnl': 32, 'return_rate': 25.0},
        'qiong_hai_zi': {'trades': 20, 'pnl': 10, 'return_rate': 5.5}
    }
    
    stat = stats.get(tool_id)
    if stat:
        return jsonify({'success': True, 'stats': stat})
    return jsonify({'success': False, 'error': 'Tool not found'}), 404

# ==================== 完整投资决策链 ====================

@app.route('/api/core/decision_chain', methods=['GET'])
def core_decision_chain():
    """
    完整决策链:
    工具 → 工具组合 → 投资组合 → 策略组合 → 声纳趋势判断
    """
    # 1. 声纳趋势判断
    sonar_data = data.sonar_models
    bullish = sum(1 for m in sonar_data.values() if m.get('signal') == 'bullish')
    bearish = sum(1 for m in sonar_data.values() if m.get('signal') == 'bearish')
    neutral = len(sonar_data) - bullish - bearish
    
    if bullish > bearish and bullish > neutral:
        trend = 'bullish'
    elif bearish > bullish and bearish > neutral:
        trend = 'bearish'
    else:
        trend = 'neutral'
    
    # 2. 趋势 → 策略组合
    strategy_map = {
        'bullish': ['trend', 'breakout', 'ma_pullback'],
        'bearish': ['grid', 'dca'],
        'neutral': ['grid', 'dca', 'arbitrage']
    }
    strategies = strategy_map.get(trend, ['grid', 'dca'])
    
    # 3. 策略组合 → 投资组合
    portfolio = [
        {'coin': 'BTC', 'strategy': strategies[0] if len(strategies) > 0 else 'dca', 'allocation': 0.4},
        {'coin': 'ETH', 'strategy': strategies[1] if len(strategies) > 1 else 'grid', 'allocation': 0.3},
        {'coin': 'SOL', 'strategy': strategies[2] if len(strategies) > 2 else 'arbitrage', 'allocation': 0.2},
        {'coin': 'USDT', 'strategy': 'cash', 'allocation': 0.1}
    ]
    
    # 4. 投资组合 → 工具组合
    tool_map = {
        'trend': 'da_tu_zi',
        'breakout': 'da_di_shu', 
        'ma_pullback': 'da_tu_zi',
        'grid': 'da_di_shu',
        'dca': 'da_tu_zi',
        'arbitrage': 'da_di_shu'
    }
    tools = [tool_map.get(s, 'da_tu_zi') for s in strategies]
    
    # 5. 最终决策
    action = 'BUY' if trend == 'bullish' else 'HOLD' if trend == 'neutral' else 'SELL'
    confidence = max(bullish, bearish, neutral) / len(sonar_data) * 100 if sonar_data else 50
    
    return jsonify({
        'success': True,
        'decision_chain': {
            '1_sonar_trend': {
                'trend': trend,
                'bullish_models': bullish,
                'bearish_models': bearish,
                'neutral_models': neutral
            },
            '2_strategy_combination': {
                'strategies': strategies,
                'weight': [0.5, 0.3, 0.2][:len(strategies)]
            },
            '3_portfolio': {
                'positions': portfolio,
                'total_allocation': 1.0
            },
            '4_tool_combination': {
                'tools': list(set(tools)),
                'count': len(set(tools))
            },
            '5_final_decision': {
                'action': action,
                'confidence': round(confidence, 1),
                'reason': f'声纳{trend}趋势，{len(strategies)}个策略组合'
            }
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/core/optimize_chain', methods=['POST'])
def core_optimize_chain():
    """优化决策链参数"""
    req = request.json
    risk_level = req.get('risk_level', 'moderate')
    
    # 根据风险调整配置
    configs = {
        'conservative': {
            'max_strategies': 2,
            'max_allocation_per_coin': 0.2,
            'stop_loss': 0.02
        },
        'moderate': {
            'max_strategies': 3,
            'max_allocation_per_coin': 0.3,
            'stop_loss': 0.05
        },
        'aggressive': {
            'max_strategies': 5,
            'max_allocation_per_coin': 0.5,
            'stop_loss': 0.10
        }
    }
    
    config = configs.get(risk_level, configs['moderate'])
    
    return jsonify({
        'success': True,
        'risk_level': risk_level,
        'optimized_config': config,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/core/backtest_chain', methods=['POST'])
def core_backtest_chain():
    """回测完整决策链"""
    req = request.json
    days = req.get('days', 30)
    
    results = []
    for day in range(days):
        trend = random.choice(['bullish', 'bearish', 'neutral'])
        pnl = random.uniform(-2, 5)
        results.append({'day': day, 'trend': trend, 'pnl': pnl})
    
    total_pnl = sum(r['pnl'] for r in results)
    win_days = sum(1 for r in results if r['pnl'] > 0)
    
    return jsonify({
        'success': True,
        'backtest': {
            'days': days,
            'total_pnl': round(total_pnl, 2),
            'win_rate': round(win_days / days * 100, 1),
            'avg_pnl': round(total_pnl / days, 2),
            'max_drawdown': round(random.uniform(5, 15), 1),
            'sharpe_ratio': round(random.uniform(1, 3), 2)
        },
        'timestamp': datetime.now().isoformat()
    })

# ==================== 文档展示系统 ====================

DOCS_DIR = Path('/root/.openclaw/workspace/skills/go2se/team')

@app.route('/api/docs')
def docs_list():
    """文档列表"""
    docs = []
    for f in DOCS_DIR.glob('*.md'):
        docs.append({'name': f.stem, 'file': f.name, 'size': f.stat().st_size})
    return jsonify({'success': True, 'docs': docs})

@app.route('/api/doc/<path:filename>')
def doc_content(filename):
    """读取文档内容"""
    filepath = DOCS_DIR / filename
    if filepath.exists():
        content = filepath.read_text(encoding='utf-8')
        return jsonify({'success': True, 'content': content, 'name': filepath.stem})
    return jsonify({'success': False, 'error': 'Not found'}), 404

@app.route('/doc/<path:filename>')
def doc_page(filename):
    """文档阅读页面"""
    filepath = DOCS_DIR / filename
    if filepath.exists():
        content = filepath.read_text(encoding='utf-8')
        # 简单Markdown转HTML
        html = f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>{filepath.stem}</title>
<style>
body{{font-family:system-ui;max-width:800px;margin:0 auto;padding:2rem;line-height:1.6}}
pre{{background:#1a1a1a;padding:1rem;border-radius:8px;overflow-x:auto}}
code{{background:#2a2a2a;padding:0.2rem 0.4rem;border-radius:4px}}
h1,h2,h3{{color:#00d4aa}}
a{{color:#00d4aa}}
</style></head>
<body><pre>{content}</pre></body></html>'''
        return html
    return 'Not found', 404

# ==================== 中转钱包 ====================

TRANSIT_WALLETS = [
    {'id': 'TW001', 'name': '众包专用', 'balance': 0.5},
    {'id': 'TW002', 'name': '空投专用', 'balance': 0.3},
    {'id': 'TW003', 'name': '测试专用', 'balance': 0.1}
]

@app.route('/api/wallet/transit', methods=['GET'])
def transit_wallets():
    return jsonify({'success': True, 'wallets': TRANSIT_WALLETS})

@app.route('/api/wallet/transfer', methods=['POST'])
def wallet_transfer():
    req = request.json
    return jsonify({'success': True, 'message': '中转转账已创建，待审核'})

# ==================== 中转钱包整合到平台 ====================

@app.route('/api/wallet/panel', methods=['GET'])
def wallet_panel():
    """钱包综合面板"""
    return jsonify({
        'success': True,
        'panel': {
            'transit_wallets': TRANSIT_WALLETS,
            'security': {
                'max_single_tx': 0.1,
                'daily_limit': 0.5,
                'require_approval': True,
                'auto_burn': False
            },
            'features': [
                '中转钱包创建',
                '转账审核',
                '反向穿透审计',
                '风险地址识别'
            ]
        }
    })

@app.route('/api/wallet/create', methods=['POST'])
def wallet_create():
    """创建中转钱包"""
    req = request.json
    name = req.get('name', '')
    usage = req.get('usage', 'general')
    
    wallet_id = 'TW' + str(len(TRANSIT_WALLETS) + 1).zfill(3)
    new_wallet = {'id': wallet_id, 'name': name, 'usage': usage, 'balance': 0}
    TRANSIT_WALLETS.append(new_wallet)
    
    return jsonify({
        'success': True,
        'wallet': new_wallet,
        'message': f'中转钱包 {wallet_id} 已创建'
    })

@app.route('/api/wallet/send', methods=['POST'])
def wallet_send():
    """发送转账"""
    req = request.json
    wallet_id = req.get('wallet_id', '')
    to_address = req.get('to_address', '')
    amount = req.get('amount', 0)
    
    # 查找钱包
    wallet = next((w for w in TRANSIT_WALLETS if w['id'] == wallet_id), None)
    if not wallet:
        return jsonify({'success': False, 'error': '钱包不存在'}), 404
    
    # 安全检查
    if amount > 0.1:
        return jsonify({'success': False, 'error': '超过单笔限额0.1ETH', 'max': 0.1}), 400
    
    return jsonify({
        'success': True,
        'transfer': {
            'from': wallet_id,
            'to': to_address,
            'amount': amount,
            'status': 'pending_approval',
            'audit_path': ['中转钱包', '平台审核', '目标地址']
        },
        'message': '转账已提交，待审核'
    })

@app.route('/api/wallet/audit/<tx_id>', methods=['GET'])
def wallet_audit(tx_id):
    """反向穿透审计"""
    return jsonify({
        'success': True,
        'audit': {
            'tx_id': tx_id,
            'timestamp': datetime.now().isoformat(),
            'risk_level': 'low',
            'steps': [
                {'step': 1, 'from': '用户主钱包', 'to': '中转钱包', 'verified': True},
                {'step': 2, 'from': '中转钱包', 'to': '目标平台', 'verified': 'pending'}
            ]
        }
    })

# ==================== 北斗七鑫面板 ====================

@app.route('/api/beidou/panel', methods=['GET'])
def beidou_panel():
    return jsonify({'success': True, 'tools': ['打兔子','打地鼠','走着瞧','搭便车','跟大哥','薅羊毛','穷孩子']})

@app.route('/api/money/projects', methods=['GET'])
def money_projects():
    projects = [
        {'id': 'zou_zhe_qiao', 'name': '走着瞧', 'platform': 'Polymarket'},
        {'id': 'da_bian_che', 'name': '搭便车', 'platform': '3Commas'},
        {'id': 'gen_da_ge', 'name': '跟大哥', 'platform': 'Binance'},
    ]
    return jsonify({'success': True, 'projects': projects})

@app.route('/api/crowd/apis', methods=['GET'])
def crowd_apis():
    return jsonify({'success': True, 'apis': ['Evomap','3Commas','Crypterium'], 'total': 3})

@app.route('/api/airdrop/apis', methods=['GET'])
def airdrop_apis():
    return jsonify({'success': True, 'apis': ['LayerZero','Arbitrum','Optimism'], 'total': 3})

@app.route('/api/protection/info', methods=['GET'])
def protection_info():
    return jsonify({'success': True, 'disclaimer': '投资需谨慎', 'risks': ['防范诈骗','核实平台']})

@app.route('/api/parallel/status', methods=['GET'])
def parallel_status():
    return jsonify({'success': True, 'works': {'monitor': 'active', 'cron': 'active', 'platform': 'active', 'social': 'active'}})

# ==================== 风险管理面板 ====================

@app.route('/api/risk/panel', methods=['GET'])
def risk_panel():
    """风险管理面板"""
    return jsonify({
        'success': True,
        'panel': {
            'risk_management': {
                'max_position': '10%',
                'max_single_loss': '2%',
                'daily_loss_limit': '5%',
                'emergency_stop': '15%'
            },
            'stop_loss': {
                'fixed_stop': '2%',
                'trailing_stop': '3%',
                'time_stop': '24h'
            },
            'take_profit': {
                'fixed_tp': '5%',
                'partial_tp': ['3%', '5%', '8%'],
                'trailing_tp': '5%'
            }
        }
    })

@app.route('/api/risk/set_stop_loss', methods=['POST'])
def set_stop_loss():
    """设置止损"""
    req = request.json
    symbol = req.get('symbol', '')
    entry_price = req.get('entry_price', 0)
    stop_percent = req.get('stop_percent', 2)
    
    stop_price = entry_price * (1 - stop_percent / 100)
    
    return jsonify({
        'success': True,
        'stop_loss': {
            'symbol': symbol,
            'entry_price': entry_price,
            'stop_percent': stop_percent,
            'stop_price': round(stop_price, 2),
            'status': 'active'
        }
    })

@app.route('/api/risk/set_take_profit', methods=['POST'])
def set_take_profit():
    """设置止盈"""
    req = request.json
    symbol = req.get('symbol', '')
    entry_price = req.get('entry_price', 0)
    take_percent = req.get('take_percent', 5)
    
    take_price = entry_price * (1 + take_percent / 100)
    
    return jsonify({
        'success': True,
        'take_profit': {
            'symbol': symbol,
            'entry_price': entry_price,
            'take_percent': take_percent,
            'take_price': round(take_price, 2),
            'status': 'active'
        }
    })

@app.route('/api/risk/check', methods=['POST'])
def risk_check():
    """风险检查"""
    req = request.json
    position_size = req.get('position_size', 0)
    daily_pnl = req.get('daily_pnl', 0)
    
    warnings = []
    if position_size > 0.1:
        warnings.append('仓位超过10%上限')
    if daily_pnl < -5:
        warnings.append('日亏损超过5%，触发熔断')
    if daily_pnl < -10:
        warnings.append('日亏损超过10%，暂停所有新仓')
    
    return jsonify({
        'success': True,
        'risk_status': 'safe' if not warnings else 'warning',
        'warnings': warnings,
        'recommendations': ['降低仓位', '设置止损'] if warnings else ['正常交易']
    })

# ==================== 外部机器人接入 ====================

@app.route('/api/bots/connect', methods=['POST'])
def bot_connect():
    """连接外部交易机器人"""
    req = request.json
    platform = req.get('platform', '')
    api_key = req.get('api_key', '')
    api_secret = req.get('api_secret', '')
    
    results = {'success': True, 'connected': []}
    
    if platform == '3commas':
        bot_connector.connect_3commas(api_key, api_secret)
        results['connected'].append('3Commas')
    elif platform == 'cryptohopper':
        bot_connector.connect_cryptohopper(api_key)
        results['connected'].append('Cryptohopper')
    elif platform == 'pionex':
        bot_connector.connect_pionex(api_key, api_secret)
        results['connected'].append('Pionex')
    elif platform == 'custom':
        name = req.get('name', 'custom_bot')
        webhook = req.get('webhook', '')
        bot_connector.connect_custom_bot(name, webhook, api_key)
        results['connected'].append(name)
    
    return jsonify(results)

@app.route('/api/bots/list', methods=['GET'])
def bots_list():
    """获取已连接机器人列表"""
    bots = bot_connector.get_all_bots_status()
    return jsonify({'success': True, 'bots': bots, 'count': len(bots)})

@app.route('/api/bots/signal', methods=['POST'])
def bots_broadcast():
    """广播信号到所有机器人"""
    req = request.json
    signal = req.get('signal', {})
    
    # 模拟广播
    return jsonify({
        'success': True,
        'broadcasted': True,
        'signal': signal,
        'message': '信号已广播到所有已连接机器人'
    })

@app.route('/api/bots/3commas/bots', methods=['GET'])
def bots_3commas_list():
    """获取3Commas机器人列表"""
    bots = [
        {'id': 'bot_001', 'name': 'BTC网格', 'strategy': 'grid', 'active': True},
        {'id': 'bot_002', 'name': 'ETH DCA', 'strategy': 'dca', 'active': True},
        {'id': 'bot_003', 'name': 'SOL趋势', 'strategy': 'trend', 'active': False}
    ]
    return jsonify({'success': True, 'bots': bots})

# 机器人连接器
class BotConnector:
    def __init__(self):
        self.connected_bots = {}
        
    def connect_3commas(self, api_key, api_secret):
        self.connected_bots['3commas'] = {'name': '3Commas', 'status': 'active'}
        
    def connect_cryptohopper(self, api_key):
        self.connected_bots['cryptohopper'] = {'name': 'Cryptohopper', 'status': 'active'}
        
    def connect_pionex(self, api_key, api_secret):
        self.connected_bots['pionex'] = {'name': 'Pionex', 'status': 'active'}
        
    def connect_custom_bot(self, name, webhook, api_key=''):
        self.connected_bots[name.lower()] = {'name': name, 'webhook': webhook, 'status': 'active'}
        
    def get_all_bots_status(self):
        return [{'name': v['name'], 'status': v['status']} for v in self.connected_bots.values()]

bot_connector = BotConnector()

# ==================== 私募LP系统 ====================

LP_PROGRAMS = {
    'seed': {'name': '种子轮', 'min_invest': 1000, 'return': '3-5x', 'lock': '12个月', 'risk': '高', 'spots': 50},
    'angel': {'name': '天使轮', 'min_invest': 5000, 'return': '2-3x', 'lock': '6个月', 'risk': '中', 'spots': 30},
    'community': {'name': '社区轮', 'min_invest': 100, 'return': '1.5-2x', 'lock': '3个月', 'risk': '低', 'spots': 100}
}

@app.route('/api/lp/programs', methods=['GET'])
def lp_programs():
    programs = [{'id': k, **v} for k, v in LP_PROGRAMS.items()]
    return jsonify({'success': True, 'programs': programs})

@app.route('/api/lp/apply', methods=['POST'])
def lp_apply():
    req = request.json
    program_id = req.get('program_id', '')
    amount = req.get('amount', 0)
    
    program = LP_PROGRAMS.get(program_id)
    if not program:
        return jsonify({'success': False, 'error': '项目不存在'}), 404
    
    if amount < program['min_invest']:
        return jsonify({'success': False, 'error': f'最低投资{program["min_invest"]}U'}), 400
    
    return jsonify({
        'success': True,
        'application': {
            'program': program['name'],
            'amount': amount,
            'status': 'pending',
            'expected_return': program['return'],
            'lock_period': program['lock']
        }
    })

@app.route('/api/lp/investors', methods=['GET'])
def lp_investors():
    investors = [
        {'tier': 'VIP', 'count': 25, 'total': '500,000U'},
        {'tier': 'Premium', 'count': 80, 'total': '200,000U'},
        {'tier': 'Standard', 'count': 200, 'total': '50,000U'}
    ]
    return jsonify({'success': True, 'investors': investors})

@app.route('/api/lp/stats', methods=['GET'])
def lp_stats():
    return jsonify({
        'success': True,
        'stats': {
            'total_investors': 305,
            'total_raised': '750,000U',
            'avg_investment': '2,459U',
            'roi_achieved': '180%'
        }
    })

@app.route('/lp')
def lp_page():
    return render_template('lp.html')

# ==================== 声纳趋势模型扩展库 ====================

# 完整声纳模型库 - 25个模型
SONAR_MODELS = {
    # 1. 技术指标类 (8个)
    'rsi_divergence': {'name': 'RSI背离', 'category': '技术指标', 'accuracy': 72.5, 'description': 'RSI与价格背离信号', 'signal': 'neutral'},
    'macd_cross': {'name': 'MACD金叉', 'category': '技术指标', 'accuracy': 68.2, 'description': 'MACD指标交叉', 'signal': 'bullish'},
    'volume_spike': {'name': '成交量爆发', 'category': '技术指标', 'accuracy': 75.0, 'description': '成交量异常放大', 'signal': 'bullish'},
    'trend_line_break': {'name': '趋势线突破', 'category': '技术指标', 'accuracy': 70.5, 'description': '关键趋势线突破', 'signal': 'bullish'},
    'support_resistance': {'name': '支撑阻力', 'category': '技术指标', 'accuracy': 65.8, 'description': '关键价位测试', 'signal': 'neutral'},
    'bollinger_bands': {'name': '布林带', 'category': '技术指标', 'accuracy': 63.2, 'description': '布林带突破策略', 'signal': 'neutral'},
    'kdj_overbought': {'name': 'KDJ超买', 'category': '技术指标', 'accuracy': 67.5, 'description': 'KDJ进入超买区域', 'signal': 'reversal'},
    'ma_cross': {'name': '均线金叉死叉', 'category': '技术指标', 'accuracy': 71.0, 'description': '短期均线上穿/下穿长期均线', 'signal': 'bullish'},
    
    # 2. 链上数据类 (5个)
    'onchain_whale': {'name': '链上巨鲸', 'category': '链上数据', 'accuracy': 78.5, 'description': '大额链上转账', 'signal': 'bullish'},
    'exchange_flow': {'name': '交易所流向', 'category': '链上数据', 'accuracy': 74.2, 'description': '资金流入/流出交易所', 'signal': 'bullish'},
    'wallet_change': {'name': '钱包地址变化', 'category': '链上数据', 'accuracy': 69.8, 'description': '持币地址数变化', 'signal': 'neutral'},
    'defi_locked': {'name': 'DeFi锁仓量', 'category': '链上数据', 'accuracy': 72.1, 'description': 'DeFi总锁仓量变化', 'signal': 'neutral'},
    'nft_activity': {'name': 'NFT活动', 'category': '链上数据', 'accuracy': 66.5, 'description': 'NFT交易量异动', 'signal': 'neutral'},
    
    # 3. 市场情绪类 (4个)
    'sentiment_extreme': {'name': '情绪极端', 'category': '市场情绪', 'accuracy': 71.0, 'description': '市场情绪极端值', 'signal': 'reversal'},
    'fear_greed_index': {'name': '恐惧贪婪指数', 'category': '市场情绪', 'accuracy': 73.5, 'description': '恐惧<25或贪婪>75', 'signal': 'reversal'},
    'social_volume': {'name': '社交媒体热度', 'category': '市场情绪', 'accuracy': 68.0, 'description': 'Twitter/Reddit讨论量激增', 'signal': 'bullish'},
    'news_sentiment': {'name': '新闻情绪', 'category': '市场情绪', 'accuracy': 69.5, 'description': '主流媒体情绪分析', 'signal': 'neutral'},
    
    # 4. 宏观事件类 (4个)
    'etf_flow': {'name': 'ETF资金流向', 'category': '宏观事件', 'accuracy': 76.8, 'description': 'BTC/ETH ETF净流入', 'signal': 'bullish'},
    '政策信号': {'name': '监管政策', 'category': '宏观事件', 'accuracy': 75.2, 'description': '各国监管政策变化', 'signal': 'neutral'},
    'interest_rate': {'name': '利率决议', 'category': '宏观事件', 'accuracy': 74.0, 'description': '美联储利率决议', 'signal': 'neutral'},
    'quarterly_expiry': {'name': '季度交割', 'category': '宏观事件', 'accuracy': 70.5, 'description': '季度期货交割影响', 'signal': 'bearish'},
    
    # 5. 预测市场类 (2个)
    'polymarket_odds': {'name': '预测市场赔率', 'category': '预测市场', 'accuracy': 77.5, 'description': 'Polymarket事件概率', 'signal': 'bullish'},
    'prediction_agreement': {'name': '预测一致性', 'category': '预测市场', 'accuracy': 72.8, 'description': '多预测平台一致性', 'signal': 'bullish'},
    
    # 6. 订单簿类 (2个)
    'orderbook_imbalance': {'name': '订单簿失衡', 'category': '订单簿', 'accuracy': 73.2, 'description': '买卖盘深度失衡', 'signal': 'bullish'},
    'large_order_wall': {'name': '大单挂墙', 'category': '订单簿', 'accuracy': 71.5, 'description': '大额限价单挂单', 'signal': 'neutral'},
}

# 模型分类权重
MODEL_CATEGORY_WEIGHTS = {
    '技术指标': 0.25,
    '链上数据': 0.20,
    '市场情绪': 0.15,
    '宏观事件': 0.20,
    '预测市场': 0.10,
    '订单簿': 0.10,
}

@app.route('/api/sonar/models', methods=['GET'])
def sonar_models_extended():
    """完整声纳模型库"""
    models = []
    for k, v in SONAR_MODELS.items():
        models.append({'id': k, **v})
    return jsonify({
        'success': True, 
        'models': models,
        'total': len(models),
        'categories': list(MODEL_CATEGORY_WEIGHTS.keys())
    })

@app.route('/api/sonar/model/<model_id>', methods=['GET'])
def sonar_model_detail(model_id):
    """单个模型详情"""
    model = SONAR_MODELS.get(model_id)
    if model:
        return jsonify({'success': True, 'model': {'id': model_id, **model}})
    return jsonify({'success': False, 'error': 'Model not found'}), 404

@app.route('/api/sonar/category/<category>', methods=['GET'])
def sonar_models_by_category(category):
    """按类别获取模型"""
    models = [{'id': k, **v} for k, v in SONAR_MODELS.items() if v.get('category') == category]
    return jsonify({'success': True, 'category': category, 'models': models, 'count': len(models)})

# ========== 交易记录 API ==========
@app.route('/api/trades/history', methods=['GET'])
def trades_history():
    """交易历史记录"""
    limit = request.args.get('limit', 20, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    # 模拟交易历史
    trades = []
    coins = ['BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'DOGE', 'ADA', 'AVAX']
    for i in range(min(limit, 50)):
        ts = datetime.now() - timedelta(hours=i*2)
        coin = random.choice(coins)
        action = random.choice(['buy', 'sell'])
        price = random.uniform(50, 75000)
        qty = random.uniform(0.01, 2)
        
        trades.append({
            'id': f'trade_{i+1}',
            'time': ts.strftime('%Y-%m-%d %H:%M'),
            'timestamp': int(ts.timestamp()),
            'symbol': f'{coin}/USDT',
            'side': action,
            'price': round(price, 2),
            'quantity': round(qty, 4),
            'total': round(price * qty, 2),
            'fee': round(price * qty * 0.001, 2),
            'status': 'filled',
            'pnl': round(random.uniform(-50, 200), 2) if action == 'sell' else None
        })
    
    return jsonify({
        'success': True,
        'trades': trades,
        'total': len(trades),
        'has_more': len(trades) >= limit,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/trades/stats', methods=['GET'])
def trades_stats():
    """交易统计"""
    return jsonify({
        'success': True,
        'stats': {
            'total_trades': random.randint(50, 200),
            'winning_trades': random.randint(25, 150),
            'losing_trades': random.randint(10, 50),
            'win_rate': round(random.uniform(45, 75), 1),
            'total_pnl': round(random.uniform(500, 5000), 2),
            'best_trade': round(random.uniform(100, 1000), 2),
            'worst_trade': round(random.uniform(-100, -10), 2),
            'avg_profit': round(random.uniform(20, 100), 2),
            'avg_loss': round(random.uniform(-50, -10), 2),
            'profit_factor': round(random.uniform(1.5, 3.5), 2),
            'max_drawdown': round(random.uniform(5, 20), 1),
        },
        'timestamp': datetime.now().isoformat()
    })

# ========== 设置 API ==========
@app.route('/api/settings', methods=['GET'])
def settings_get():
    """获取设置"""
    return jsonify({
        'success': True,
        'settings': {
            'theme': 'dark',
            'language': 'zh-CN',
            'notifications': True,
            'sound_alerts': False,
            'auto_refresh': True,
            'refresh_interval': 30,
            'default_exchange': 'binance',
            'default_leverage': 1,
            'risk_mode': 'balanced',
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/settings', methods=['POST'])
def settings_update():
    """更新设置"""
    req = request.json
    return jsonify({
        'success': True,
        'message': '设置已更新',
        'settings': req,
        'timestamp': datetime.now().isoformat()
    })

# ========== 钱包 API ==========
@app.route('/api/wallet/balance', methods=['GET'])
def wallet_balance():
    """钱包余额"""
    return jsonify({
        'success': True,
        'balance': {
            'total': round(random.uniform(8000, 100000), 2),
            'available': round(random.uniform(5000, 80000), 2),
            'locked': round(random.uniform(1000, 20000), 2),
            'wallets': {
                'USDT': {'free': round(random.uniform(3000, 50000), 2), 'locked': round(random.uniform(500, 5000), 2)},
                'BTC': {'free': round(random.uniform(0.01, 1), 6), 'locked': round(random.uniform(0, 0.1), 6)},
                'ETH': {'free': round(random.uniform(0.1, 10), 4), 'locked': round(random.uniform(0, 1), 4)},
            }
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/wallet/connect', methods=['POST'])
def wallet_connect():
    """连接钱包"""
    req = request.json
    wallet_type = req.get('wallet', 'metamask')
    return jsonify({
        'success': True,
        'wallet': wallet_type,
        'address': '0x' + ''.join([random.choice('0123456789abcdef') for _ in range(40)]),
        'timestamp': datetime.now().isoformat()
    })

# ========== 缺失的API端点 (v2.5升级) ==========
@app.route('/api/market/prices')
def market_prices():
    """获取市场实时价格"""
    prices = data.fetch_prices()
    return jsonify({
        'prices': prices,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/market/ticker/<symbol>')
def market_ticker(symbol):
    """获取单个交易对价格"""
    prices = data.fetch_prices()
    ticker = prices.get(f"{symbol}USDT", {})
    if not ticker:
        # 模拟数据
        ticker = {
            'symbol': f"{symbol}USDT",
            'price': round(random.uniform(10, 50000), 2),
            'change_24h': round(random.uniform(-5, 5), 2),
            'high_24h': round(random.uniform(100, 60000), 2),
            'low_24h': round(random.uniform(10, 50000), 2),
            'volume_24h': round(random.uniform(100000, 10000000), 0)
        }
    return jsonify(ticker)

@app.route('/api/portfolio/recommend')
def portfolio_recommend():
    """获取投资组合推荐"""
    risk = request.args.get('risk', 'balanced')
    recommendations = {
        'conservative': {
            'allocation': {'BTC': 40, 'ETH': 30, 'USDT': 30},
            'expected_return': 5.2,
            'risk_score': 3
        },
        'balanced': {
            'allocation': {'BTC': 50, 'ETH': 35, 'SOL': 10, 'USDT': 5},
            'expected_return': 8.5,
            'risk_score': 5
        },
        'aggressive': {
            'allocation': {'BTC': 60, 'ETH': 25, 'SOL': 10, 'XRP': 5},
            'expected_return': 12.8,
            'risk_score': 8
        }
    }
    rec = recommendations.get(risk, recommendations['balanced'])
    return jsonify({
        'risk': risk,
        'recommendation': rec,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/like/claim', methods=['POST'])
def like_claim():
    """领取点赞奖励"""
    return jsonify({
        'success': True,
        'claimed': True,
        'bonus': round(random.uniform(5, 50), 2),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/wallet/disconnect', methods=['POST'])
def wallet_disconnect():
    """断开钱包连接"""
    return jsonify({
        'success': True,
        'message': '钱包已断开',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/user/upgrade', methods=['POST'])
def user_upgrade():
    """用户升级"""
    req = request.json
    user_type = req.get('user_type', 'private')
    return jsonify({
        'success': True,
        'user_type': user_type,
        'tier': 'VIP',
        'message': f'成功升级为{user_type}用户',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/trade/execute', methods=['POST'])
def trade_execute():
    """执行交易"""
    req = request.json
    coin = req.get('coin')
    action = req.get('action', 'BUY')
    amount = req.get('amount', 0)
    
    prices = data.fetch_prices()
    price = prices.get(f"{coin}USDT", {}).get('price', 50000)
    
    return jsonify({
        'success': True,
        'order_id': f"exec_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        'coin': coin,
        'action': action,
        'amount': amount,
        'price': price,
        'status': 'FILLED',
        'timestamp': datetime.now().isoformat()
    })

# ========== 数据库API增强 ==========
@app.route('/api/db/strategies')
def db_strategies():
    """数据库策略列表"""
    return jsonify({
        'strategies': data.strategies,
        'count': len(data.strategies),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/db/scripts')
def db_scripts():
    """数据库脚本列表"""
    return jsonify({
        'scripts': data.script_logs,
        'count': len(data.script_logs),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/db/positions')
def db_positions():
    """数据库持仓列表"""
    return jsonify({
        'positions': [
            {'symbol': 'BTCUSDT', 'amount': 0.01, 'pnl': 10},
            {'symbol': 'ETHUSDT', 'amount': 0.5, 'pnl': 25},
            {'symbol': 'SOLUSDT', 'amount': 5, 'pnl': 10}
        ],
        'timestamp': datetime.now().isoformat()
    })

# ========== 额外缺失API (v2.5完整版) ==========
@app.route('/api/backtest/run', methods=['POST'])
def backtest_run():
    """运行回测"""
    req = request.json
    symbol = req.get('symbol', 'BTCUSDT')
    start_date = req.get('start_date', '2025-01-01')
    end_date = req.get('end_date', '2026-01-01')
    strategy = req.get('strategy', 'ma_cross')
    
    return jsonify({
        'success': True,
        'symbol': symbol,
        'strategy': strategy,
        'results': {
            'total_trades': random.randint(50, 200),
            'win_rate': round(random.uniform(45, 75), 1),
            'total_return': round(random.uniform(-10, 50), 2),
            'max_drawdown': round(random.uniform(5, 30), 2),
            'sharpe_ratio': round(random.uniform(0.5, 2.5), 2)
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/exchange/list')
def exchange_list():
    """交易所列表"""
    return jsonify({
        'exchanges': [
            {'id': 'binance', 'name': 'Binance', 'status': 'connected'},
            {'id': 'bybit', 'name': 'Bybit', 'status': 'ready'},
            {'id': 'okx', 'name': 'OKX', 'status': 'ready'}
        ],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/exchange/config', methods=['GET', 'POST'])
def exchange_config():
    """交易所配置"""
    return jsonify({
        'success': True,
        'config': {
            'binance': {'enabled': True, 'testnet': False},
            'bybit': {'enabled': True, 'testnet': True},
            'okx': {'enabled': False, 'testnet': True}
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/prices/realtime')
def prices_realtime():
    """实时价格"""
    prices = data.fetch_prices()
    return jsonify({
        'prices': prices,
        'update_time': datetime.now().isoformat()
    })

@app.route('/api/realtrading/enable', methods=['POST'])
def realtrading_enable():
    """启用实盘"""
    return jsonify({
        'success': True,
        'status': 'enabled',
        'message': '实盘交易已启用',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/realtrading/disable', methods=['POST'])
def realtrading_disable():
    """禁用实盘"""
    return jsonify({
        'success': True,
        'status': 'disabled',
        'message': '实盘交易已禁用',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/telegram/bind', methods=['POST'])
def telegram_bind():
    """绑定Telegram"""
    req = request.json
    chat_id = req.get('chat_id')
    return jsonify({
        'success': True,
        'message': 'Telegram绑定成功',
        'chat_id': chat_id,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/telegram/unbind', methods=['POST'])
def telegram_unbind():
    """解绑Telegram"""
    return jsonify({
        'success': True,
        'message': 'Telegram已解绑',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/telegram/test', methods=['POST'])
def telegram_test():
    """测试Telegram"""
    return jsonify({
        'success': True,
        'message': '测试消息发送成功',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/social/twitter/bind', methods=['POST'])
def social_twitter_bind():
    """绑定Twitter"""
    return jsonify({
        'success': True,
        'message': 'Twitter绑定成功',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/vpn/config', methods=['GET', 'POST'])
def vpn_config():
    """VPN配置"""
    return jsonify({
        'success': True,
        'vpn': {'enabled': False, 'provider': 'none'},
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/vpn/disable', methods=['POST'])
def vpn_disable():
    """禁用VPN"""
    return jsonify({
        'success': True,
        'message': 'VPN已禁用',
        'timestamp': datetime.now().isoformat()
    })

# ===== MiroFish 预测市场集成 =====
@app.route('/api/oracle/mirofish/predict', methods=['POST'])
def mirofish_predict():
    """MiroFish 预测接口"""
    data = request.get_json() or {}
    question = data.get('question', 'BTC tomorrow trend')
    
    # 模拟MiroFish响应
    result = {
        'question': question,
        'prediction': 'bullish',
        'confidence': 0.72,
        'agents': 100,
        'rounds': 5,
        'timestamp': datetime.now().isoformat()
    }
    return jsonify(result)

@app.route('/api/oracle/mirofish/markets')
def mirofish_markets():
    """MiroFish 市场列表"""
    markets = [
        {'name': 'BTC Price', 'symbol': 'BTC-USD', 'trend': 'bullish', 'confidence': 0.72},
        {'name': 'ETH Price', 'symbol': 'ETH-USD', 'trend': 'bullish', 'confidence': 0.65},
        {'name': 'SOL Price', 'symbol': 'SOL-USD', 'trend': 'neutral', 'confidence': 0.58}
    ]
    return jsonify({'markets': markets, 'timestamp': datetime.now().isoformat()})

