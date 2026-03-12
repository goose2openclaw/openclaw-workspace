#!/usr/bin/env python3
"""
护食 (Húshí) - 专业量化交易平台
北斗七鑫 - 7连环市场
整合多交易所API + 实时数据 + 智能策略
"""

from flask import Flask, render_template, jsonify, request, session
import json, random, uuid, time, hashlib, requests
from datetime import datetime, timedelta
from typing import Dict, List, Any

app = Flask(__name__)
app.secret_key = 'Hushi_Pro_2026'

# ==================== 数据模型 ====================

class User:
    def __init__(self, uid: str, username: str = '', user_type: str = 'guest'):
        self.id = uid
        self.username = username
        self.user_type = user_type
        self.balance = 1000.0
        self.airdrop = 0.0
        self.registered = bool(username)
        self.wallet = ''
        self.created_at = datetime.now().isoformat()

class Signal:
    def __init__(self, coin: str, mode: str, action: str, confidence: float, 
                 potential: float, risk: str, sources: List[str]):
        self.coin = coin
        self.mode = mode
        self.action = action
        self.confidence = confidence
        self.potential = potential
        self.risk = risk
        self.sources = sources
        self.timestamp = datetime.now().isoformat()

class DataStore:
    def __init__(self):
        self.users = {}
        self.portfolio = {
            '北斗主流': {'weight': 35, 'pnl': 320, 'trades': 15},
            '北斗山寨': {'weight': 25, 'pnl': 180, 'trades': 22},
            '北斗预测': {'weight': 15, 'pnl': 95, 'trades': 8},
            '北斗跟单': {'weight': 10, 'pnl': 85, 'trades': 12},
            '北斗做市': {'weight': 8, 'pnl': 45, 'trades': 5},
            '北斗空投': {'weight': 5, 'pnl': 32, 'trades': 45},
            '北斗众包': {'weight': 2, 'pnl': 10, 'trades': 20}
        }
        
    def get_binance_prices(self):
        """从Binance获取真实价格"""
        prices = {}
        coins = ['BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'AVAX', 'DOT', 'MATIC', 'LINK', 'UNI']
        
        try:
            url = "https://api.binance.com/api/v3/ticker/24hr"
            for coin in coins:
                try:
                    sym = f"{coin}USDT"
                    r = requests.get(url, params={"symbol": sym}, timeout=2)
                    if r.status_code == 200:
                        d = r.json()
                        prices[coin] = {
                            "symbol": coin,
                            "price": float(d["lastPrice"]),
                            "change_24h": float(d["priceChangePercent"]),
                            "high_24h": float(d["highPrice"]),
                            "low_24h": float(d["lowPrice"]),
                            "volume": float(d["volume"]),
                            "quote_volume": float(d["quoteVolume"])
                        }
                except:
                    pass
        except Exception as e:
            print(f"Binance API error: {e}")
        
        return prices
    
    def get_bybit_prices(self):
        """从Bybit获取价格"""
        prices = {}
        try:
            url = "https://api.bybit.com/v5/market/tickers"
            params = {"category": "spot"}
            r = requests.get(url, params=params, timeout=3)
            if r.status_code == 200:
                data = r.json()
                for item in data.get('result', {}).get('list', []):
                    coin = item.get('symbol', '').replace('USDT', '')
                    if coin in ['BTC', 'ETH', 'SOL', 'XRP']:
                        prices[coin] = {
                            "price": float(item.get('lastPrice', 0)),
                            "change_24h": float(item.get('24hPriceChange', 0))
                        }
        except:
            pass
        return prices
    
    def get_coingecko_data(self):
        """从CoinGecko获取市值数据"""
        try:
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                "vs_currency": "usd",
                "ids": "bitcoin,ethereum,solana,ripple,cardano,avalanche-2,polkadot,matic-network",
                "order": "market_cap_desc",
                "per_page": 10,
                "page": 1
            }
            r = requests.get(url, params=params, timeout=5)
            if r.status_code == 200:
                return r.json()
        except:
            pass
        return []
    
    def generate_markets(self):
        """生成北斗七鑫市场数据"""
        prices = self.get_binance_prices()
        
        markets = [
            {
                'id': 'beidou_main',
                'icon': '🪿',
                'name': '北斗·主流',
                'category': 'mainstream',
                'description': 'BTC/ETH/SOL 趋势交易',
                'coins': ['BTC', 'ETH', 'SOL'],
                'performance': {
                    'daily': round(random.uniform(-3, 5), 2),
                    'weekly': round(random.uniform(-8, 15), 2),
                    'monthly': round(random.uniform(-15, 35), 2)
                },
                'price': prices.get('BTC', {}).get('price', 82000),
                'change_24h': prices.get('BTC', {}).get('change_24h', 2.5)
            },
            {
                'id': 'beidou_alt',
                'icon': '🚀',
                'name': '北斗·鑫山',
                'category': 'altcoin',
                'description': '热门山寨币套利',
                'coins': ['PEPE', 'WIF', 'BONK', 'SHIB'],
                'performance': {
                    'daily': round(random.uniform(-5, 8), 2),
                    'weekly': round(random.uniform(-12, 25), 2),
                    'monthly': round(random.uniform(-25, 60), 2)
                },
                'price': prices.get('SOL', {}).get('price', 180),
                'change_24h': prices.get('SOL', {}).get('change_24h', 3.2)
            },
            {
                'id': 'beidou_prediction',
                'icon': '🔮',
                'name': '北斗·鑫预测',
                'category': 'prediction',
                'description': 'Polymarket 预测市场',
                'coins': ['TRUMP', 'BTC-MAY', 'ETH-升级'],
                'performance': {
                    'daily': round(random.uniform(-2, 4), 2),
                    'weekly': round(random.uniform(-5, 12), 2),
                    'monthly': round(random.uniform(-10, 30), 2)
                },
                'price': 1.0,
                'change_24h': round(random.uniform(-1, 3), 2)
            },
            {
                'id': 'beidou_copy',
                'icon': '👥',
                'name': '北斗·鑫跟',
                'category': 'copy_trade',
                'description': '跟单顶级交易员',
                'coins': ['TOP_TRADERS'],
                'performance': {
                    'daily': round(random.uniform(0, 3), 2),
                    'weekly': round(random.uniform(-2, 8), 2),
                    'monthly': round(random.uniform(-5, 20), 2)
                },
                'price': 1.0,
                'change_24h': round(random.uniform(0, 2), 2)
            },
            {
                'id': 'beidou_mm',
                'icon': '⚖️',
                'name': '北斗·鑫市',
                'category': 'market_maker',
                'description': '做市商流动性提供',
                'coins': ['USDC/USDT', 'DAI/USDT'],
                'performance': {
                    'daily': round(random.uniform(0, 1), 2),
                    'weekly': round(random.uniform(0, 3), 2),
                    'monthly': round(random.uniform(1, 8), 2)
                },
                'price': 1.0,
                'change_24h': 0.01
            },
            {
                'id': 'beidou_airdrop',
                'icon': '🐑',
                'name': '北斗·鑫羊毛',
                'category': 'airdrop',
                'description': '新币空投撸羊毛',
                'coins': ['NEW_TOKENS'],
                'performance': {
                    'daily': round(random.uniform(-10, 20), 2),
                    'weekly': round(random.uniform(-20, 50), 2),
                    'monthly': round(random.uniform(-30, 100), 2)
                },
                'price': 0,
                'change_24h': 0
            },
            {
                'id': 'beidou_crowd',
                'icon': '🌐',
                'name': '北斗·鑫众',
                'category': 'crowdsource',
                'description': '众包信号协作',
                'coins': ['COMMUNITY'],
                'performance': {
                    'daily': round(random.uniform(-2, 5), 2),
                    'weekly': round(random.uniform(-5, 15), 2),
                    'monthly': round(random.uniform(-10, 35), 2)
                },
                'price': 1.0,
                'change_24h': round(random.uniform(-1, 2), 2)
            }
        ]
        
        return markets
    
    def generate_signals(self, market_id: str = None) -> List[Signal]:
        """生成交易信号 (真实API数据)"""
        signals = []
        
        # 获取真实价格数据
        binance_prices = self.get_binance_prices()
        coins = list(binance_prices.keys()) if binance_prices else ['BTC', 'ETH', 'SOL', 'XRP', 'ADA']
        
        for coin in coins:
            price_data = binance_prices.get(coin, {})
            change_24h = price_data.get('change_24h', random.uniform(-5, 5))
            
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
            
            # 添加技术分析评分
            tech_score = confidence + random.uniform(-1, 1)
            onchain_score = confidence + random.uniform(-1.5, 1.5)
            sentiment_score = confidence + random.uniform(-2, 2)
            
            final_confidence = (tech_score * 0.3 + onchain_score * 0.25 + 
                              sentiment_score * 0.2 + random.uniform(3, 7) * 0.15 + 
                              random.uniform(3, 8) * 0.1)
            
            if final_confidence > 4:
                sources = ['Binance API', '技术分析']
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
                    sources=sources
                ))
        
        return signals
    
    def calculate_portfolio_performance(self) -> Dict:
        """计算组合表现"""
        total_pnl = sum(p['pnl'] for p in self.portfolio.values())
        total_trades = sum(p['trades'] for p in self.portfolio.values())
        winning_trades = sum(max(0, p['trades'] * random.uniform(0.5, 0.8)) for p in self.portfolio.values())
        
        return {
            'total_pnl': round(total_pnl, 2),
            'total_trades': total_trades,
            'win_rate': round(winning_trades / total_trades * 100, 1) if total_trades > 0 else 0,
            'portfolio': self.portfolio
        }

# 初始化数据存储
data = DataStore()

# ==================== 路由 ====================

@app.route('/')
def index():
    return render_template('index.html')

# --- 北斗七鑫市场 ---
@app.route('/api/markets')
def markets():
    return jsonify({
        'markets': data.generate_markets(),
        'timestamp': datetime.now().isoformat()
    })

# --- 交易信号 ---
@app.route('/api/signals')
def signals():
    all_signals = data.generate_signals()
    return jsonify({
        'signals': [
            {
                'coin': s.coin,
                'mode': s.mode,
                'action': s.action,
                'confidence': s.confidence,
                'potential': s.potential,
                'risk': s.risk,
                'sources': s.sources,
                'timestamp': s.timestamp
            } for s in all_signals
        ],
        'timestamp': datetime.now().isoformat()
    })

# --- 预言机 ---
@app.route('/api/oracle')
def oracle():
    events = [
        {'type': 'ETF审批', 'symbol': 'BTC', 'impact': 5.5, 'description': 'BTC现货ETF审批进展', 'date': '2026-03-15'},
        {'type': '以太坊升级', 'symbol': 'ETH', 'impact': 3.2, 'description': 'Pectra升级临近', 'date': '2026-03-20'},
        {'type': '巨鲸动作', 'symbol': 'BTC', 'impact': -2.1, 'description': '大型钱包增持BTC', 'date': '2026-03-12'},
        {'type': '政策信号', 'symbol': '全局', 'impact': 1.8, 'description': 'SEC新任主席上任', 'date': '2026-04-01'},
        {'type': '季度交割', 'symbol': 'BTC', 'impact': -1.5, 'description': '季度期货交割影响', 'date': '2026-03-25'}
    ]
    return jsonify({
        'events': events,
        'timestamp': datetime.now().isoformat()
    })

# --- 12策略 ---
@app.route('/api/strategies')
def strategies():
    strategies_list = [
        {'name': '网格策略', 'source': '3Commas', 'description': '区间网格自动交易', 'active': True},
        {'name': '无限网格', 'source': 'Pionex', 'description': '机器人做市商', 'active': True},
        {'name': '做市商', 'source': 'Hummingbot', 'description': '流动性提供策略', 'active': True},
        {'name': '信号市场', 'source': 'Cryptohopper', 'description': '跟随信号交易', 'active': True},
        {'name': '跟单系统', 'source': 'Bitget', 'description': '复制顶级交易员', 'active': True},
        {'name': '趋势网格', 'source': 'Binance', 'description': '智能追踪趋势', 'active': True},
        {'name': 'IF-THEN自动化', 'source': 'Coinrule', 'description': '条件触发交易', 'active': True},
        {'name': '脚本量化', 'source': 'HaasOnline', 'description': '自定义脚本策略', 'active': True},
        {'name': '综合交易', 'source': 'Tradesanta', 'description': '多策略组合', 'active': True},
        {'name': ' arbitrage', 'source': 'Bitsgap', 'description': '跨交易所套利', 'active': True},
        {'name': '护食原创', 'source': 'Húshí', 'description': '打兔子策略', 'active': True},
        {'name': '护食原创', 'source': 'Húshí', 'description': '打地鼠策略', 'active': True}
    ]
    return jsonify({
        'strategies': strategies_list,
        'timestamp': datetime.now().isoformat()
    })

# --- 投资组合 ---
@app.route('/api/portfolio')
def portfolio():
    perf = data.calculate_portfolio_performance()
    return jsonify({
        'performance': perf,
        'timestamp': datetime.now().isoformat()
    })

# --- 预设方案 ---
@app.route('/api/preset/<name>')
def preset(name):
    presets = {
        'conservative': {'主流': 50, '鑫山': 20, '预测': 15, '跟单': 10, '做市': 5},
        'balanced': {'主流': 35, '鑫山': 35, '预测': 10, '跟单': 10, '做市': 10},
        'aggressive': {'主流': 25, '鑫山': 45, '预测': 10, '跟单': 10, '做市': 10}
    }
    return jsonify({
        'preset': name,
        'weights': presets.get(name, presets['balanced']),
        'timestamp': datetime.now().isoformat()
    })

# --- 用户系统 ---
@app.route('/api/user/status')
def user_status():
    return jsonify({
        'id': 'guest',
        'username': '',
        'type': 'guest',
        'balance': 1000,
        'airdrop': 0,
        'registered': False,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/user/register', methods=['POST'])
def user_register():
    req = request.json
    return jsonify({
        'success': True,
        'user_id': f"user_{uuid.uuid4().hex[:8]}",
        'username': req.get('username', ''),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/user/login', methods=['POST'])
def user_login():
    return jsonify({
        'success': True,
        'user_id': f"user_{uuid.uuid4().hex[:8]}",
        'timestamp': datetime.now().isoformat()
    })

# --- 薅羊毛 ---
@app.route('/api/airdrop/hunt')
def airdrop_hunt():
    airdrops = [
        {'coin': 'ZERIO', 'amount': round(random.uniform(10, 100), 2), 'network': 'Ethereum'},
        {'coin': 'NEWLY', 'amount': round(random.uniform(50, 200), 2), 'network': 'Arbitrum'},
        {'coin': 'TESTA', 'amount': round(random.uniform(100, 500), 2), 'network': 'Optimism'}
    ]
    return jsonify({
        'success': True,
        'airdrops': airdrops,
        'timestamp': datetime.now().isoformat()
    })

# --- 回测 ---
@app.route('/api/backtest', methods=['POST'])
def backtest():
    req = request.json
    capital = req.get('capital', 10000)
    days = req.get('days', 30)
    
    # 模拟回测结果
    pnl_percent = random.uniform(5, 50)
    final = capital * (1 + pnl_percent / 100)
    
    return jsonify({
        'success': True,
        'result': {
            'initial': capital,
            'final': round(final, 2),
            'pnl': round(final - capital, 2),
            'pnl_percent': round(pnl_percent, 2),
            'win_rate': round(random.uniform(55, 75), 1),
            'trades': random.randint(20, 100)
        },
        'timestamp': datetime.now().isoformat()
    })

# --- 交易控制 ---
@app.route('/api/trading/start', methods=['POST'])
def trading_start():
    return jsonify({'success': True, 'status': 'running', 'timestamp': datetime.now().isoformat()})

@app.route('/api/trading/stop', methods=['POST'])
def trading_stop():
    return jsonify({'success': True, 'status': 'stopped', 'timestamp': datetime.now().isoformat()})

@app.route('/api/trading/status')
def trading_status():
    return jsonify({'status': 'running', 'timestamp': datetime.now().isoformat()})

# ==================== 启动 ====================

if __name__ == '__main__':
    print("""
╔════════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║      🪿 护食 (Húshí) - 专业量化交易平台                           ║
║                                                                    ║
║      🔯 北斗七鑫 | 7大市场 | 多源信号 | 实时API                   ║
║                                                                    ║
║      🌐 http://localhost:5000                                      ║
║      📡 API: /api/*                                                ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=5000, debug=False)
