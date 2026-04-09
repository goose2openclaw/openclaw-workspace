"""
🪿 Go2Se 赚钱API库
各平台API接口配置和数据
"""

MONEY_APIS = {
    # 走着瞧 - 预测市场
    'zou_zhe_qiao': {
        'name': '走着瞧',
        'platform': 'Polymarket',
        'api_url': 'https://clamp.polymarket.com/markets',
        'websocket': 'wss://endpoint.polymarket.com/ws',
        'docs': 'https://docs.polymarket.com',
        'historical_data': [],
        'stats': {'total_trades': 8, 'pnl': 95, 'win_rate': 62.5}
    },
    
    # 搭便车 - 跟单交易
    'da_bian_che': {
        'name': '搭便车',
        'platform': '3Commas',
        'api_url': 'https://api.3commas.io/v2',
        'docs': 'https://docs.3commas.io',
        'traders': [
            {'id': 'top_1', 'name': '量化大师', 'win_rate': 78, 'pnl_30d': 125.5},
            {'id': 'top_2', 'name': '趋势猎手', 'win_rate': 72, 'pnl_30d': 98.2},
            {'id': 'top_3', 'name': '套利专家', 'win_rate': 85, 'pnl_30d': 156.8}
        ],
        'stats': {'total_trades': 12, 'pnl': 85, 'return_rate': 6.2}
    },
    
    # 跟大哥 - 做市商
    'gen_da_ge': {
        'name': '跟大哥',
        'platform': 'Binance Market Making',
        'api_url': 'https://api.binance.com/api/v3',
        'docs': 'https://developers.binance.com',
        'requirements': '需要API密钥和做市商申请',
        'stats': {'daily_profit': 8.5, 'spread_earned': 0.1}
    },
    
    # 薅羊毛 - 空投
    'hao_yang_mao': {
        'name': '薅羊毛',
        'platform': 'LayerZero/Aptos/Solana',
        'api_url': 'https://app.layerzero.network',
        'interaction_apis': [
            {'project': 'Stargate', 'est_value': 500, 'status': 'claimed'},
            {'project': 'Aptos', 'est_value': 200, 'status': 'pending'},
            {'project': 'Sui', 'est_value': 150, 'status': 'pending'}
        ],
        'stats': {'total_airdrops': 45, 'total_value': 3200}
    },
    
    # 穷孩子 - 众包
    'qiong_hai_zi': {
        'name': '穷孩子',
        'platform': 'Evomap/Moltbot',
        'api_url': 'https://evomap.ai/api',
        'tasks': [
            {'type': 'signal', 'reward': 25, 'completed': 15},
            {'type': 'strategy', 'reward': 50, 'completed': 8},
            {'type': 'data', 'reward': 10, 'completed': 45}
        ],
        'stats': {'total_tasks': 68, 'total_earnings': 1450}
    }
}

def get_money_api(api_id):
    return MONEY_APIS.get(api_id)

def get_all_money_apis():
    return MONEY_APIS

def refresh_api_data(api_id):
    """定期刷新API数据"""
    api = MONEY_APIS.get(api_id)
    if api:
        # 模拟数据刷新
        api['last_update'] = '2026-03-14T17:46:00Z'
    return api
