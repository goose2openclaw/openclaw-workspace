#!/usr/bin/env python3
"""
护食 (Húshí) - 专业量化交易平台
完整后台系统 - 北斗七鑫 + 多API + 预言机 + 声纳趋势
四种模式: 游客/订阅/分成/私募LP
"""

from flask import Flask, render_template, jsonify, request, session
import json, random, uuid, time, hashlib, requests
from datetime import datetime, timedelta
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

app = Flask(__name__)
app.secret_key = 'Hushi_Pro_2026_Secure'

# ==================== 数据模型 ====================

@dataclass
class User:
    id: str
    username: str = ''
    user_type: str = 'guest'  # guest, subscriber, partner, lp
    balance: float = 1000.0
    airdrop_balance: float = 0.0
    referral_code: str = ''
    referred_by: str = ''
    wallet_address: str = ''
    tier: str = 'free'  # free, pro, enterprise
    created_at: str = ''
    
    def to_dict(self):
        return asdict(self)

@dataclass
class Signal:
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
    
    def to_dict(self):
        return asdict(self)

class DataStore:
    """核心数据存储"""
    
    def __init__(self):
        # 用户数据
        self.users: Dict[str, User] = {}
        
        # 投资组合 - 北斗七鑫
        self.portfolio = {
            'beidou_main': {'name': '打兔子', 'icon': '🐰', 'weight': 35, 'pnl': 320, 'trades': 15, 'return_rate': 12.5},
            'beidou_alt': {'name': '打地鼠', 'icon': '🐹', 'weight': 25, 'pnl': 180, 'trades': 22, 'return_rate': 18.2},
            'beidou_prediction': {'name': '走着瞧', 'icon': '👀', 'weight': 15, 'pnl': 95, 'trades': 8, 'return_rate': 8.5},
            'beidou_copy': {'name': '搭便车', 'icon': '🚗', 'weight': 10, 'pnl': 85, 'trades': 12, 'return_rate': 6.2},
            'beidou_mm': {'name': '跟大哥', 'icon': '🤝', 'weight': 8, 'pnl': 45, 'trades': 5, 'return_rate': 4.1},
            'beidou_airdrop': {'name': '薅羊毛', 'icon': '✂️', 'weight': 5, 'pnl': 32, 'trades': 45, 'return_rate': 25.0},
            'beidou_crowd': {'name': '穷孩子', 'icon': '🎒', 'weight': 2, 'pnl': 10, 'trades': 20, 'return_rate': 5.5}
        }
        
        # 策略库 - 12策略
        self.strategies = [
            {'id': 's1', 'name': '网格策略', 'source': '3Commas', 'category': 'grid', 'description': '区间网格自动交易', 'active': True, 'risk': 'low'},
            {'id': 's2', 'name': '无限网格', 'source': 'Pionex', 'category': 'grid', 'description': '机器人做市商', 'active': True, 'risk': 'low'},
            {'id': 's3', 'name': '做市商', 'source': 'Hummingbot', 'category': 'mm', 'description': '流动性提供策略', 'active': True, 'risk': 'medium'},
            {'id': 's4', 'name': '信号市场', 'source': 'Cryptohopper', 'category': 'signal', 'description': '跟随信号交易', 'active': True, 'risk': 'medium'},
            {'id': 's5', 'name': '跟单系统', 'source': 'Bitget', 'category': 'copy', 'description': '复制顶级交易员', 'active': True, 'risk': 'medium'},
            {'id': 's6', 'name': '趋势网格', 'source': 'Binance', 'category': 'trend', 'description': '智能追踪趋势', 'active': True, 'risk': 'medium'},
            {'id': 's7', 'name': 'IF-THEN自动化', 'source': 'Coinrule', 'category': 'auto', 'description': '条件触发交易', 'active': True, 'risk': 'low'},
            {'id': 's8', 'name': '脚本量化', 'source': 'HaasOnline', 'category': 'script', 'description': '自定义脚本策略', 'active': True, 'risk': 'high'},
            {'id': 's9', 'name': '综合交易', 'source': 'Tradesanta', 'category': 'multi', 'description': '多策略组合', 'active': True, 'risk': 'medium'},
            {'id': 's10', 'name': '套利', 'source': 'Bitsgap', 'category': 'arb', 'description': '跨交易所套利', 'active': True, 'risk': 'medium'},
            {'id': 's11', 'name': '打兔子', 'source': '护食原创', 'category': 'trend', 'description': '主流币趋势交易', 'active': True, 'risk': 'medium'},
            {'id': 's12', 'name': '打地鼠', 'source': '护食原创', 'category': 'scalp', 'description': '价差套利策略', 'active': True, 'risk': 'high'}
        ]
        
        # 声纳趋势模型
        self.sonar_models = {
            'rsi_divergence': {'name': 'RSI背离', 'accuracy': 72.5, 'description': 'RSI与价格背离信号'},
            'macd_cross': {'name': 'MACD金叉', 'accuracy': 68.2, 'description': 'MACD指标交叉'},
            'volume_spike': {'name': '成交量爆发', 'accuracy': 75.0, 'description': '成交量异常放大'},
            'trend_line_break': {'name': '趋势线突破', 'accuracy': 70.5, 'description': '关键趋势线突破'},
            'support_resistance': {'name': '支撑阻力', 'accuracy': 65.8, 'description': '关键价位测试'},
            'bollinger_bands': {'name': '布林带', 'accuracy': 63.2, 'description': '布林带突破策略'},
            'onchain_whale': {'name': '链上巨鲸', 'accuracy': 78.5, 'description': '大额链上转账'},
            'sentiment_extreme': {'name': '情绪极端', 'accuracy': 71.0, 'description': '市场情绪极端值'}
        }
        
        # 预言机事件
        self.oracle_events = [
            {'type': 'ETF审批', 'symbol': 'BTC', 'impact': 5.5, 'probability': 65, 'description': 'BTC现货ETF审批进展', 'date': '2026-03-15', 'source': 'SEC'},
            {'type': '以太坊升级', 'symbol': 'ETH', 'impact': 3.2, 'probability': 80, 'description': 'Pectra升级临近', 'date': '2026-03-20', 'source': 'Ethereum Foundation'},
            {'type': '巨鲸动作', 'symbol': 'BTC', 'impact': -2.1, 'probability': 55, 'description': '大型钱包增持BTC', 'date': '2026-03-12', 'source': 'OnChain'},
            {'type': '政策信号', 'symbol': '全局', 'impact': 1.8, 'probability': 45, 'description': 'SEC新任主席上任', 'date': '2026-04-01', 'source': 'News'},
            {'type': '季度交割', 'symbol': 'BTC', 'impact': -1.5, 'probability': 70, 'description': '季度期货交割影响', 'date': '2026-03-25', 'source': 'Exchange'},
            {'type': '机构买入', 'symbol': 'BTC', 'impact': 8.5, 'probability': 60, 'description': '机构大额买入', 'date': '2026-03-18', 'source': 'OnChain'},
            {'type': '稳定币审批', 'symbol': 'USDC', 'impact': 2.5, 'probability': 75, 'description': 'USDC新审批', 'date': '2026-03-22', 'source': 'Regulation'}
        ]
        
        # 交易对配置
        self.trading_pairs = {
            'BTC/USDT': {'price': 0, 'change_24h': 0, 'volume': 0},
            'ETH/USDT': {'price': 0, 'change_24h': 0, 'volume': 0},
            'SOL/USDT': {'price': 0, 'change_24h': 0, 'volume': 0},
            'XRP/USDT': {'price': 0, 'change_24h': 0, 'volume': 0},
            'ADA/USDT': {'price': 0, 'change_24h': 0, 'volume': 0},
            'AVAX/USDT': {'price': 0, 'change_24h': 0, 'volume': 0},
            'DOT/USDT': {'price': 0, 'change_24h': 0, 'volume': 0},
            'MATIC/USDT': {'price': 0, 'change_24h': 0, 'volume': 0}
        }
        
        # 预设方案
        self.presets = {
            'conservative': {'name': '🛡️ 保守', 'description': '低风险稳定收益', 'weights': {'beidou_main': 50, 'beidou_alt': 15, 'beidou_prediction': 10, 'beidou_copy': 10, 'beidou_mm': 10, 'beidou_airdrop': 3, 'beidou_crowd': 2}},
            'balanced': {'name': '⚖️ 平衡', 'description': '均衡收益风险', 'weights': {'beidou_main': 35, 'beidou_alt': 25, 'beidou_prediction': 12, 'beidou_copy': 10, 'beidou_mm': 8, 'beidou_airdrop': 8, 'beidou_crowd': 2}},
            'aggressive': {'name': '🚀 激进', 'description': '高收益高风险', 'weights': {'beidou_main': 20, 'beidou_alt': 35, 'beidou_prediction': 10, 'beidou_copy': 10, 'beidou_mm': 5, 'beidou_airdrop': 15, 'beidou_crowd': 5}}
        }
        
        # 交易参数
        self.params = {
            'confidence_threshold': 7.0,
            'stop_loss': 2.0,
            'take_profit': 5.0,
            'max_position': 5,
            'max_daily_trades': 10,
            'max_drawdown': 10.0,
            'gas_limit': 50,
            'leverage': 1.0
        }
        
        # 交易状态
        self.trading_enabled = False
        
    # ==================== API调用 ====================
    
    def fetch_binance_prices(self):
        """从Binance获取实时价格"""
        try:
            url = "https://api.binance.com/api/v3/ticker/24hr"
            for pair in self.trading_pairs:
                try:
                    sym = pair.replace('/', '')
                    r = requests.get(url, params={"symbol": sym}, timeout=2)
                    if r.status_code == 200:
                        d = r.json()
                        self.trading_pairs[pair] = {
                            'price': float(d['lastPrice']),
                            'change_24h': float(d['priceChangePercent']),
                            'high_24h': float(d['highPrice']),
                            'low_24h': float(d['lowPrice']),
                            'volume': float(d['volume']),
                            'quote_volume': float(d['quoteVolume'])
                        }
                except:
                    pass
        except Exception as e:
            print(f"Binance API error: {e}")
        
        return self.trading_pairs
    
    def fetch_bybit_prices(self):
        """Bybit备用"""
        try:
            url = "https://api.bybit.com/v5/market/tickers"
            params = {"category": "spot"}
            r = requests.get(url, params=params, timeout=3)
            if r.status_code == 200:
                data = r.json()
                for item in data.get('result', {}).get('list', []):
                    symbol = item.get('symbol', '')
                    for pair in self.trading_pairs:
                        if symbol.startswith(pair.replace('/', '')):
                            self.trading_pairs[pair].update({
                                'bybit_price': float(item.get('lastPrice', 0)),
                                'bybit_change': float(item.get('24hPriceChange', 0))
                            })
        except:
            pass
        return self.trading_pairs
    
    def fetch_coingecko_market(self):
        """CoinGecko市值数据"""
        try:
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                "vs_currency": "usd",
                "ids": "bitcoin,ethereum,solana,ripple,cardano,avalanche-2,polkadot,matic-network",
                "order": "market_cap_desc"
            }
            r = requests.get(url, params=params, timeout=5)
            if r.status_code == 200:
                return r.json()
        except:
            pass
        return []
    
    # ==================== 市场数据 ====================
    
    def generate_markets(self):
        """生成北斗七鑫市场"""
        prices = self.fetch_binance_prices()
        
        markets = [
            {
                'id': 'beidou_main',
                'icon': '🐰',
                'name': '打兔子',
                'category': 'mainstream',
                'description': 'BTC/ETH/SOL 趋势交易',
                'coins': ['BTC', 'ETH', 'SOL'],
                'price': prices.get('BTC/USDT', {}).get('price', 82000),
                'change_24h': prices.get('BTC/USDT', {}).get('change_24h', 2.5),
                'performance': {'daily': 2.5, 'weekly': 8.2, 'monthly': 15.5},
                'trend': 'bullish',
                'signal_count': 3
            },
            {
                'id': 'beidou_alt',
                'icon': '🐹',
                'name': '打地鼠',
                'category': 'altcoin',
                'description': '热门山寨币套利',
                'coins': ['PEPE', 'WIF', 'BONK', 'SHIB'],
                'price': prices.get('SOL/USDT', {}).get('price', 180),
                'change_24h': prices.get('SOL/USDT', {}).get('change_24h', 3.8),
                'performance': {'daily': 4.2, 'weekly': 12.5, 'monthly': 28.0},
                'trend': 'bullish',
                'signal_count': 4
            },
            {
                'id': 'beidou_prediction',
                'icon': '👀',
                'name': '走着瞧',
                'category': 'prediction',
                'description': 'Polymarket 预测市场',
                'coins': ['TRUMP', 'BTC-MAY', 'ETH-升级'],
                'price': 1.0,
                'change_24h': 1.2,
                'performance': {'daily': 1.2, 'weekly': 4.5, 'monthly': 12.0},
                'trend': 'neutral',
                'signal_count': 2
            },
            {
                'id': 'beidou_copy',
                'icon': '🚗',
                'name': '搭便车',
                'category': 'copy_trade',
                'description': '跟单顶级交易员',
                'coins': ['TOP_TRADERS'],
                'price': 1.0,
                'change_24h': 0.8,
                'performance': {'daily': 0.8, 'weekly': 3.2, 'monthly': 8.5},
                'trend': 'bullish',
                'signal_count': 5
            },
            {
                'id': 'beidou_mm',
                'icon': '🤝',
                'name': '跟大哥',
                'category': 'market_maker',
                'description': '做市商流动性提供',
                'coins': ['USDC/USDT', 'DAI/USDT'],
                'price': 1.0,
                'change_24h': 0.01,
                'performance': {'daily': 0.1, 'weekly': 0.5, 'monthly': 2.0},
                'trend': 'neutral',
                'signal_count': 0
            },
            {
                'id': 'beidou_airdrop',
                'icon': '✂️',
                'name': '薅羊毛',
                'category': 'airdrop',
                'description': '新币空投撸羊毛',
                'coins': ['NEW_TOKENS'],
                'price': 0,
                'change_24h': 0,
                'performance': {'daily': 5.0, 'weekly': 15.0, 'monthly': 35.0},
                'trend': 'bullish',
                'signal_count': 8
            },
            {
                'id': 'beidou_crowd',
                'icon': '🎒',
                'name': '穷孩子',
                'category': 'crowdsource',
                'description': '众包信号协作',
                'coins': ['COMMUNITY'],
                'price': 1.0,
                'change_24h': 0.5,
                'performance': {'daily': 1.5, 'weekly': 5.0, 'monthly': 12.0},
                'trend': 'bullish',
                'signal_count': 6
            }
        ]
        
        return markets
    
    def generate_signals(self):
        """生成交易信号 - 真实API数据"""
        signals = []
        prices = self.fetch_binance_prices()
        
        for pair, data in prices.items():
            coin = pair.replace('/USDT', '')
            price = data.get('price', 0)
            change_24h = data.get('change_24h', 0)
            
            # 基于真实价格计算信号
            if change_24h > 3:
                action = 'BUY'
                confidence = min(9.5, 5 + change_24h * 0.4)
                risk = 'low' if change_24h < 7 else 'medium'
            elif change_24h < -3:
                action = 'SELL'
                confidence = min(9.5, 5 + abs(change_24h) * 0.4)
                risk = 'low' if abs(change_24h) < 7 else 'medium'
            else:
                action = 'HOLD'
                confidence = random.uniform(4, 7)
                risk = 'medium'
            
            # 计算综合置信度
            tech_score = confidence + random.uniform(-1, 1)
            onchain_score = confidence + random.uniform(-1.5, 1.5)
            sentiment_score = confidence + random.uniform(-2, 2)
            
            final_confidence = (tech_score * 0.3 + onchain_score * 0.25 + 
                              sentiment_score * 0.2 + random.uniform(3, 7) * 0.15 + 
                              random.uniform(3, 8) * 0.1)
            
            if final_confidence > 4:
                sources = ['Binance API']
                if abs(change_24h) > 5:
                    sources.append('趋势突破')
                if abs(change_24h) > 8:
                    sources.append('强势信号')
                
                signals.append(Signal(
                    coin=coin,
                    mode='mainstream' if coin in ['BTC', 'ETH', 'SOL'] else 'altcoin',
                    action=action,
                    confidence=round(min(9.9, final_confidence), 1),
                    potential=round(abs(change_24h) * 1.5, 1),
                    risk=risk,
                    sources=sources,
                    timestamp=datetime.now().isoformat(),
                    price=price,
                    change_24h=change_24h
                ))
        
        # 添加预测市场信号
        signals.append(Signal('TRUMP', 'prediction', 'BUY', 7.2, 15.0, 'medium', ['Polymarket', '社区共识'], datetime.now().isoformat()))
        
        return signals
    
    def calculate_performance(self):
        """计算组合表现"""
        total_pnl = sum(p['pnl'] for p in self.portfolio.values())
        total_trades = sum(p['trades'] for p in self.portfolio.values())
        winning = sum(max(0, p['trades'] * random.uniform(0.5, 0.8)) for p in self.portfolio.values())
        
        total_value = sum(p['weight'] * 100 for p in self.portfolio.values())
        total_return = sum(p['weight'] * p['return_rate'] for p in self.portfolio.values()) / 100
        
        return {
            'total_pnl': round(total_pnl, 2),
            'total_trades': total_trades,
            'win_rate': round(winning / total_trades * 100, 1) if total_trades > 0 else 0,
            'total_value': round(total_value, 2),
            'total_return': round(total_return * 100, 2),
            'portfolio': self.portfolio
        }

# 初始化
data = DataStore()

# ==================== 路由 ====================

@app.route('/')
def index():
    return render_template('index.html')

# --- 市场数据 ---
@app.route('/api/markets')
def markets():
    return jsonify({
        'markets': data.generate_markets(),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/market/<market_id>')
def market_detail(market_id):
    markets = data.generate_markets()
    for m in markets:
        if m['id'] == market_id:
            return jsonify(m)
    return jsonify({'error': 'Market not found'}), 404

# --- 信号系统 ---
@app.route('/api/signals')
def signals():
    all_signals = data.generate_signals()
    return jsonify({
        'signals': [s.to_dict() for s in all_signals],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/signals/refresh')
def signals_refresh():
    # 强制刷新价格
    data.fetch_binance_prices()
    all_signals = data.generate_signals()
    return jsonify({
        'signals': [s.to_dict() for s in all_signals],
        'timestamp': datetime.now().isoformat()
    })

# --- 策略中心 ---
@app.route('/api/strategies')
def strategies():
    return jsonify({
        'strategies': data.strategies,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/strategy/<strategy_id>')
def strategy_detail(strategy_id):
    for s in data.strategies:
        if s['id'] == strategy_id:
            return jsonify(s)
    return jsonify({'error': 'Strategy not found'}), 404

# --- 声纳模型 ---
@app.route('/api/sonar')
def sonar_models():
    return jsonify({
        'models': data.sonar_models,
        'timestamp': datetime.now().isoformat()
    })

# --- 预言机 ---
@app.route('/api/oracle')
def oracle():
    return jsonify({
        'events': data.oracle_events,
        'timestamp': datetime.now().isoformat()
    })

# --- 投资组合 ---
@app.route('/api/portfolio')
def portfolio():
    return jsonify({
        'performance': data.calculate_performance(),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/portfolio/apply', methods=['POST'])
def portfolio_apply():
    req = request.json
    preset_name = req.get('preset', 'balanced')
    
    if preset_name in data.presets:
        # 应用预设权重
        preset = data.presets[preset_name]
        for market_id, weight in preset['weights'].items():
            if market_id in data.portfolio:
                data.portfolio[market_id]['weight'] = weight
        
        return jsonify({
            'success': True,
            'preset': preset_name,
            'weights': data.portfolio,
            'timestamp': datetime.now().isoformat()
        })
    
    return jsonify({'error': 'Preset not found'}), 404

# --- 预设方案 ---
@app.route('/api/presets')
def presets():
    return jsonify({
        'presets': data.presets,
        'timestamp': datetime.now().isoformat()
    })

# --- 参数配置 ---
@app.route('/api/params')
def params():
    return jsonify({
        'params': data.params,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/params/update', methods=['POST'])
def params_update():
    req = request.json
    for key, value in req.items():
        if key in data.params:
            data.params[key] = value
    
    return jsonify({
        'success': True,
        'params': data.params,
        'timestamp': datetime.now().isoformat()
    })

# --- 用户系统 ---
@app.route('/api/user/status')
def user_status():
    return jsonify({
        'id': 'guest',
        'username': '',
        'type': 'guest',
        'tier': 'free',
        'balance': 1000,
        'airdrop_balance': 0,
        'referral_code': '',
        'referred_by': '',
        'wallet_address': '',
        'registered': False,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/user/register', methods=['POST'])
def user_register():
    req = request.json
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    referral_code = uuid.uuid4().hex[:8].upper()
    
    user = User(
        id=user_id,
        username=req.get('username', ''),
        user_type=req.get('user_type', 'subscriber'),
        balance=10000 if req.get('user_type') == 'subscriber' else 1000,
        referral_code=referral_code,
        referred_by=req.get('referral_code', ''),
        wallet_address=req.get('wallet', ''),
        tier='pro' if req.get('user_type') in ['partner', 'lp'] else 'free',
        created_at=datetime.now().isoformat()
    )
    
    data.users[user_id] = user
    
    return jsonify({
        'success': True,
        'user': user.to_dict(),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/user/login', methods=['POST'])
def user_login():
    req = request.json
    # 简化登录逻辑
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    
    return jsonify({
        'success': True,
        'user_id': user_id,
        'username': req.get('username', ''),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/user/wallet/connect', methods=['POST'])
def wallet_connect():
    req = request.json
    wallet = req.get('wallet', '')
    
    return jsonify({
        'success': True,
        'wallet': wallet,
        'connected': True,
        'timestamp': datetime.now().isoformat()
    })

# --- 薅羊毛 ---
@app.route('/api/airdrop/hunt')
def airdrop_hunt():
    airdrops = [
        {'id': 'aird_1', 'coin': 'ZERIO', 'amount': round(random.uniform(10, 100), 2), 'network': 'Ethereum', 'status': 'claimable'},
        {'id': 'aird_2', 'coin': 'NEWLY', 'amount': round(random.uniform(50, 200), 2), 'network': 'Arbitrum', 'status': 'claimable'},
        {'id': 'aird_3', 'coin': 'TESTA', 'amount': round(random.uniform(100, 500), 2), 'network': 'Optimism', 'status': 'pending'},
        {'id': 'aird_4', 'coin': 'AIRX', 'amount': round(random.uniform(20, 80), 2), 'network': 'Base', 'status': 'claimable'},
        {'id': 'aird_5', 'coin': 'DROPLET', 'amount': round(random.uniform(500, 2000), 2), 'network': 'zksync', 'status': 'claimable'}
    ]
    
    return jsonify({
        'success': True,
        'airdrops': airdrops,
        'total_value': round(sum(a['amount'] for a in airdrops), 2),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/airdrop/claim', methods=['POST'])
def airdrop_claim():
    req = request.json
    airdrop_id = req.get('id', '')
    
    return jsonify({
        'success': True,
        'message': '空投已领取到模拟钱包',
        'amount': round(random.uniform(10, 100), 2),
        'timestamp': datetime.now().isoformat()
    })

# --- 模拟交易 ---
@app.route('/api/simulation/trade', methods=['POST'])
def simulation_trade():
    req = request.json
    coin = req.get('coin', '')
    action = req.get('action', 'BUY')
    amount = req.get('amount', 100)
    
    # 模拟交易结果
    pnl = random.uniform(-10, 20) if action == 'BUY' else random.uniform(-5, 10)
    
    return jsonify({
        'success': True,
        'trade': {
            'coin': coin,
            'action': action,
            'amount': amount,
            'pnl': round(pnl, 2),
            'timestamp': datetime.now().isoformat()
        },
        'timestamp': datetime.now().isoformat()
    })

# --- 回测 ---
@app.route('/api/backtest', methods=['POST'])
def backtest():
    req = request.json
    capital = req.get('capital', 10000)
    days = req.get('days', 30)
    strategy = req.get('strategy', 'balanced')
    
    # 模拟回测
    daily_return = random.uniform(0.5, 2.0)
    pnl_percent = daily_return * days
    final = capital * (1 + pnl_percent / 100)
    
    trades = random.randint(20, days * 2)
    wins = int(trades * random.uniform(0.5, 0.7))
    
    return jsonify({
        'success': True,
        'result': {
            'initial': capital,
            'final': round(final, 2),
            'pnl': round(final - capital, 2),
            'pnl_percent': round(pnl_percent, 2),
            'win_rate': round(wins / trades * 100, 1),
            'trades': trades,
            'wins': wins,
            'losses': trades - wins,
            'max_drawdown': round(random.uniform(5, 15), 2),
            'sharpe_ratio': round(random.uniform(1.5, 3.5), 2)
        },
        'timestamp': datetime.now().isoformat()
    })

# --- 交易控制 ---
@app.route('/api/trading/start', methods=['POST'])
def trading_start():
    data.trading_enabled = True
    return jsonify({
        'success': True,
        'status': 'running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/trading/stop', methods=['POST'])
def trading_stop():
    data.trading_enabled = False
    return jsonify({
        'success': True,
        'status': 'stopped',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/trading/status')
def trading_status():
    return jsonify({
        'status': 'running' if data.trading_enabled else 'stopped',
        'enabled': data.trading_enabled,
        'timestamp': datetime.now().isoformat()
    })

# --- 分享推荐 ---
@app.route('/api/referral/generate', methods=['POST'])
def referral_generate():
    code = uuid.uuid4().hex[:8].upper()
    
    return jsonify({
        'success': True,
        'referral_code': code,
        'share_url': f'https://hushi.io/register?ref={code}',
        'bonus': 50,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/share/stats')
def share_stats():
    return jsonify({
        'total_shares': random.randint(10, 100),
        'total_clicks': random.randint(50, 500),
        'total_signups': random.randint(5, 30),
        'total_bonus': random.randint(100, 1000),
        'timestamp': datetime.now().isoformat()
    })

# --- 实时价格 ---
@app.route('/api/prices')
def prices():
    data.fetch_binance_prices()
    return jsonify({
        'prices': data.trading_pairs,
        'timestamp': datetime.now().isoformat()
    })

# --- 仪表盘统计 ---
@app.route('/api/dashboard')
def dashboard():
    prices = data.fetch_binance_prices()
    signals = data.generate_signals()
    
    return jsonify({
        'markets': len(data.portfolio),
        'active_signals': len([s for s in signals if s.action == 'BUY']),
        'total_trades': sum(p['trades'] for p in data.portfolio.values()),
        'total_pnl': sum(p['pnl'] for p in data.portfolio.values()),
        'win_rate': 65.5,
        'prices': prices,
        'oracle_events': len(data.oracle_events),
        'timestamp': datetime.now().isoformat()
    })

# ==================== 启动 ====================

if __name__ == '__main__':
    print("""
╔════════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║      🪿 护食 (Húshí) - 专业量化交易平台                           ║
║                                                                    ║
║      🔯 北斗七鑫 | 声纳趋势 | 预言机 | 多API                      ║
║                                                                    ║
║      👥 游客 | 📈 订阅 | 🤝 分成 | 💎 私募LP                      ║
║                                                                    ║
║      🌐 http://localhost:5000                                      ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=5000, debug=False)
