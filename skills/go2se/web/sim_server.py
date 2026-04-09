#!/usr/bin/env python3
"""
GO2SE 模拟交易系统 v5
- 模拟交易/回测
- 虚拟钱包分配
- 策略匹配执行
- 资产看板
"""

import json, random, uuid, time, requests
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)
app.secret_key = 'GO2SE_Sim_2026'

# ==================== 模拟交易引擎 ====================
class SimTradingEngine:
    """模拟交易引擎"""
    
    def __init__(self):
        # 虚拟钱包分配
        self.virtual_wallets = {}
        
        # 模拟交易记录
        self.sim_trades = []
        
        # 回测记录
        self.backtest_results = {}
        
        # 实时市场数据 (模拟)
        self.market_data = {
            'BTC': {'price': 82000, 'volatility': 0.03, 'trend': 'bullish'},
            'ETH': {'price': 3200, 'volatility': 0.04, 'trend': 'bullish'},
            'SOL': {'price': 180, 'volatility': 0.05, 'trend': 'bullish'},
            'XRP': {'price': 0.65, 'volatility': 0.035, 'trend': 'neutral'},
            'ADA': {'price': 0.58, 'volatility': 0.04, 'trend': 'bearish'},
            'AVAX': {'price': 42, 'volatility': 0.05, 'trend': 'bullish'},
            'PEPE': {'price': 0.0000012, 'volatility': 0.08, 'trend': 'bullish'},
            'WIF': {'price': 2.5, 'volatility': 0.06, 'trend': 'bullish'}
        }
        
        # 策略配置
        self.strategy_configs = {
            'trend_follow': {
                'name': '趋势跟踪',
                'entry': 'MA20>MA50 + RSI<70 + 放量突破',
                'stop_loss': 0.05,
                'take_profit': 0.10,
                'min_confidence': 7.0
            },
            'grid_trade': {
                'name': '网格交易',
                'entry': '价格区间±15%',
                'stop_loss': 0.02,
                'take_profit': 0.015,
                'grid_count': 10
            },
            'ma_pullback': {
                'name': '均线回踩',
                'entry': '回踩MA20 + 看涨K线',
                'stop_loss': 0.02,
                'take_profit': 0.08
            },
            'breakout': {
                'name': '突破策略',
                'entry': '缩量盘整后放量突破',
                'stop_loss': 0.03,
                'take_profit': 0.15
            }
        }
        
        # 组合配置
        self.portfolio_configs = {
            'conservative': {
                'name': '🛡️ 保守组合',
                'allocation': {'trend_follow': 40, 'ma_pullback': 30, 'grid_trade': 30},
                'initial_balance': 10000
            },
            'balanced': {
                'name': '⚖️ 平衡组合',
                'allocation': {'trend_follow': 35, 'breakout': 25, 'grid_trade': 25, 'ma_pullback': 15},
                'initial_balance': 10000
            },
            'aggressive': {
                'name': '🚀 激进组合',
                'allocation': {'breakout': 40, 'trend_follow': 30, 'grid_trade': 20, 'ma_pullback': 10},
                'initial_balance': 10000
            }
        }
    
    def create_virtual_wallet(self, user_id, user_type='guest'):
        """创建虚拟钱包"""
        wallet_id = f"wallet_{uuid.uuid4().hex[:12]}"
        wallet_address = "0x" + uuid.uuid4().hex[2:42]
        
        wallet = {
            'id': wallet_id,
            'address': wallet_address,
            'user_id': user_id,
            'user_type': user_type,
            'created_at': datetime.now().isoformat(),
            'balance': 100000 if user_type == 'subscriber' else 1000,  # 游客1000，会员100000
            'positions': {},
            'pnl': 0,
            'trade_count': 0
        }
        
        self.virtual_wallets[user_id] = wallet
        return wallet
    
    def get_wallet(self, user_id):
        """获取钱包"""
        if user_id not in self.virtual_wallets:
            return self.create_virtual_wallet(user_id)
        return self.virtual_wallets[user_id]
    
    def execute_trade(self, user_id, symbol, action, amount, strategy='manual'):
        """执行模拟交易"""
        wallet = self.get_wallet(user_id)
        
        if symbol not in self.market_data:
            return {'success': False, 'error': 'Symbol not found'}
        
        price = self.market_data[symbol]['price']
        total = amount * price
        fee = total * 0.001  # 0.1% 手续费
        
        trade = {
            'id': f"trade_{uuid.uuid4().hex[:8]}",
            'wallet_id': wallet['id'],
            'symbol': symbol,
            'action': action,  # BUY or SELL
            'amount': amount,
            'price': price,
            'total': total,
            'fee': fee,
            'strategy': strategy,
            'timestamp': datetime.now().isoformat(),
            'pnl': 0
        }
        
        if action == 'BUY':
            if wallet['balance'] >= total + fee:
                wallet['balance'] -= (total + fee)
                if symbol not in wallet['positions']:
                    wallet['positions'][symbol] = {'amount': 0, 'avg_price': 0}
                
                old_amt = wallet['positions'][symbol]['amount']
                old_avg = wallet['positions'][symbol]['avg_price']
                new_amt = old_amt + amount
                wallet['positions'][symbol]['avg_price'] = (old_amt * old_avg + amount * price) / new_amt
                wallet['positions'][symbol]['amount'] = new_amt
                
                trade['status'] = 'filled'
            else:
                trade['status'] = 'rejected'
                trade['reason'] = 'insufficient_balance'
                return {'success': False, 'trade': trade}
        else:
            # SELL
            if symbol in wallet['positions'] and wallet['positions'][symbol]['amount'] >= amount:
                wallet['positions'][symbol]['amount'] -= amount
                wallet['balance'] += (total - fee)
                
                # 计算盈亏
                entry_price = wallet['positions'][symbol].get('avg_price', price)
                trade['pnl'] = (price - entry_price) * amount - fee
                wallet['pnl'] += trade['pnl']
                
                trade['status'] = 'filled'
            else:
                trade['status'] = 'rejected'
                trade['reason'] = 'insufficient_position'
                return {'success': False, 'trade': trade}
        
        wallet['trade_count'] += 1
        self.sim_trades.append(trade)
        
        return {'success': True, 'trade': trade, 'wallet': wallet}
    
    def run_backtest(self, user_id, days=5, portfolio='balanced'):
        """运行回测"""
        config = self.portfolio_configs.get(portfolio, self.portfolio_configs['balanced'])
        wallet = self.get_wallet(user_id)
        
        # 重置钱包用于回测
        initial_balance = config['initial_balance']
        wallet['balance'] = initial_balance
        wallet['positions'] = {}
        wallet['pnl'] = 0
        wallet['trade_count'] = 0
        
        start_time = datetime.now() - timedelta(days=days)
        trades = []
        
        # 模拟每天的交易
        for day in range(days):
            # 每天随机选择1-3个策略执行
            for _ in range(random.randint(1, 3)):
                strategy_name = random.choice(list(config['allocation'].keys()))
                strategy = self.strategy_configs[strategy_name]
                
                # 随机选择币种
                symbol = random.choice(list(self.market_data.keys()))
                
                # 模拟价格变动
                market = self.market_data[symbol]
                price_change = random.uniform(-market['volatility'], market['volatility'])
                price = market['price'] * (1 + price_change)
                
                # 模拟执行
                amount = random.uniform(0.001, 0.1) * (config['allocation'][strategy_name] / 100)
                action = random.choice(['BUY', 'SELL'])
                
                trade = {
                    'id': f"bt_{day}_{uuid.uuid4().hex[:6]}",
                    'symbol': symbol,
                    'action': action,
                    'amount': round(amount, 6),
                    'price': round(price, 4),
                    'total': round(amount * price, 2),
                    'fee': round(amount * price * 0.001, 2),
                    'strategy': strategy_name,
                    'day': day + 1,
                    'timestamp': (start_time + timedelta(days=day)).isoformat()
                }
                
                # 模拟盈亏
                if action == 'SELL':
                    trade['pnl'] = round(random.uniform(-20, 50), 2)
                else:
                    trade['pnl'] = 0
                
                trades.append(trade)
                wallet['trade_count'] += 1
        
        # 计算最终结果
        final_balance = wallet['balance']
        total_pnl = final_balance - initial_balance + sum(t['pnl'] for t in trades)
        pnl_percent = (total_pnl / initial_balance) * 100
        win_trades = sum(1 for t in trades if t['pnl'] > 0)
        win_rate = (win_trades / len(trades) * 100) if trades else 0
        
        result = {
            'backtest_id': f"bt_{uuid.uuid4().hex[:8]}",
            'portfolio': portfolio,
            'days': days,
            'initial_balance': initial_balance,
            'final_balance': round(final_balance, 2),
            'total_pnl': round(total_pnl, 2),
            'pnl_percent': round(pnl_percent, 2),
            'total_trades': len(trades),
            'win_trades': win_trades,
            'win_rate': round(win_rate, 1),
            'trades': trades[:20],  # 返回前20笔
            'started_at': start_time.isoformat(),
            'completed_at': datetime.now().isoformat()
        }
        
        self.backtest_results[user_id] = result
        
        # 恢复当前余额
        wallet['balance'] = 1000
        
        return result
    
    def get_asset_summary(self, user_id):
        """获取资产看板摘要"""
        wallet = self.get_wallet(user_id)
        
        # 计算持仓市值
        positions_value = 0
        positions_detail = []
        
        for symbol, pos in wallet['positions'].items():
            if pos['amount'] > 0:
                price = self.market_data.get(symbol, {}).get('price', 0)
                value = pos['amount'] * price
                pnl = (price - pos['avg_price']) * pos['amount']
                positions_value += value
                positions_detail.append({
                    'symbol': symbol,
                    'amount': round(pos['amount'], 6),
                    'avg_price': round(pos['avg_price'], 4),
                    'current_price': price,
                    'value': round(value, 2),
                    'pnl': round(pnl, 2),
                    'pnl_percent': round((price - pos['avg_price']) / pos['avg_price'] * 100, 2) if pos['avg_price'] > 0 else 0
                })
        
        total_assets = wallet['balance'] + positions_value
        
        return {
            'wallet_address': wallet['address'],
            'total_assets': round(total_assets, 2),
            'available_balance': round(wallet['balance'], 2),
            'positions_value': round(positions_value, 2),
            'total_pnl': round(wallet['pnl'], 2),
            'pnl_percent': round(wallet['pnl'] / total_assets * 100, 2) if total_assets > 0 else 0,
            'trade_count': wallet['trade_count'],
            'positions': positions_detail,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_backtest_result(self, user_id):
        """获取回测结果"""
        return self.backtest_results.get(user_id, None)


# ==================== 初始化 ====================
sim_engine = SimTradingEngine()

# ==================== API路由 ====================

@app.route('/')
def index():
    return render_template('index.html')

# 模拟交易API
@app.route('/api/sim/wallet')
def sim_wallet():
    """获取虚拟钱包"""
    user_id = request.args.get('user_id', 'guest')
    wallet = sim_engine.get_wallet(user_id)
    return jsonify(wallet)

@app.route('/api/sim/wallet/create', methods=['POST'])
def sim_wallet_create():
    """创建虚拟钱包"""
    req = request.json
    user_id = req.get('user_id', 'guest')
    user_type = req.get('user_type', 'guest')
    wallet = sim_engine.create_virtual_wallet(user_id, user_type)
    return jsonify({'success': True, 'wallet': wallet})

@app.route('/api/sim/trade', methods=['POST'])
def sim_trade():
    """执行模拟交易"""
    req = request.json
    user_id = req.get('user_id', 'guest')
    symbol = req.get('symbol', 'BTC')
    action = req.get('action', 'BUY')
    amount = req.get('amount', 0.01)
    strategy = req.get('strategy', 'manual')
    
    result = sim_engine.execute_trade(user_id, symbol, action, amount, strategy)
    return jsonify(result)

@app.route('/api/sim/backtest', methods=['POST'])
def sim_backtest():
    """运行回测"""
    req = request.json
    user_id = req.get('user_id', 'guest')
    days = req.get('days', 5)
    portfolio = req.get('portfolio', 'balanced')
    
    result = sim_engine.run_backtest(user_id, days, portfolio)
    return jsonify({'success': True, 'result': result})

@app.route('/api/sim/assets')
def sim_assets():
    """获取资产看板"""
    user_id = request.args.get('user_id', 'guest')
    assets = sim_engine.get_asset_summary(user_id)
    return jsonify(assets)

@app.route('/api/sim/backtest/result')
def sim_backtest_result():
    """获取回测结果"""
    user_id = request.args.get('user_id', 'guest')
    result = sim_engine.get_backtest_result(user_id)
    if result:
        return jsonify(result)
    return jsonify({'error': 'No backtest result', 'status': 404})

# 组合配置API
@app.route('/api/sim/portfolios')
def sim_portfolios():
    """获取组合配置"""
    return jsonify(sim_engine.portfolio_configs)

@app.route('/api/sim/strategies')
def sim_strategies():
    """获取策略配置"""
    return jsonify(sim_engine.strategy_configs)

@app.route('/api/sim/market')
def sim_market():
    """获取市场数据"""
    return jsonify(sim_engine.market_data)


if __name__ == '__main__':
    print("""
╔════════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║      🪿 GO2SE 模拟交易系统 v5                                     ║
║                                                                    ║
║      🎮 模拟交易 | 📊 回测 | 💰 资产看板 | 💳 虚拟钱包           ║
║                                                                    ║
║      🌐 http://localhost:5002                                    ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=5002, debug=False)
