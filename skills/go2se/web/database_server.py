#!/usr/bin/env python3
"""
GO2SE 完整后台系统 v5
策略数据库 + 声纳库 + API配置 + 完整交易引擎
"""

import json, random, uuid, time, requests, hashlib, hmac
from datetime import datetime
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)
app.secret_key = 'GO2SE_2026_Secure'

# ==================== 完整策略数据库 ====================
class StrategyDatabase:
    """策略数据库 - 22个竞品策略 + 11个原生策略"""
    
    def __init__(self):
        # ============== 竞品策略库 (22个) ==============
        self.competitor_strategies = {
            # 3Commas (3个)
            '3commas_dca': {
                'name': 'DCA策略', 'source': '3Commas', 'category': 'dca',
                'description': '美元成本平均策略，定期买入降低均价',
                'entry': '定期买入', 'exit': '达到目标收益', 'risk': 'low', 'win_rate': 72,
                'parameters': {'interval': '1h', 'amount_pct': 10, 'profit_target': 2}
            },
            '3commas_grid': {
                'name': '智能网格', 'source': '3Commas', 'category': 'grid',
                'description': '区间网格自动交易',
                'entry': '价格进入区间', 'exit': '触及网格止盈', 'risk': 'low', 'win_rate': 70,
                'parameters': {'grid_count': 5, 'price_range': 10}
            },
            '3commas_智能交易': {
                'name': '智能交易机器人', 'source': '3Commas', 'category': 'smart',
                'description': 'AI驱动的自动交易',
                'entry': 'AI信号触发', 'exit': 'AI止盈止损', 'risk': 'medium', 'win_rate': 68,
                'parameters': {'ai_mode': 'auto', 'signals': ['RSI', 'MACD']}
            },
            
            # Pionex (3个)
            'pionex_infinite_grid': {
                'name': '无限网格', 'source': 'Pionex', 'category': 'grid',
                'description': '机器人做市商，单边行情持续套利',
                'entry': '趋势形成', 'exit': '趋势反转', 'risk': 'low', 'win_rate': 68,
                'parameters': {'leverage': 3, 'grid': 100}
            },
            'pionex_martingale': {
                'name': '马丁策略', 'source': 'Pionex', 'category': 'martingale',
                'description': '亏损加仓策略',
                'entry': '亏损后加仓', 'exit': '盈利出场', 'risk': 'high', 'win_rate': 65,
                'parameters': {'multiplier': 2, 'max_layers': 5}
            },
            'pionex_套利': {
                'name': '合约套利', 'source': 'Pionex', 'category': 'arbitrage',
                'description': '永续合约资金费套利',
                'entry': '资金费率>0.01%', 'exit': '资金结算', 'risk': 'medium', 'win_rate': 75,
                'parameters': {'funding_collect': True, 'hedge': True}
            },
            
            # Hummingbot (2个)
            'hummingbot_liquidity': {
                'name': '流动性做市', 'source': 'Hummingbot', 'category': 'mm',
                'description': '提供流动性赚取手续费',
                'entry': '价差优势', 'exit': '价差消失', 'risk': 'medium', 'win_rate': 65,
                'parameters': {'spread': 0.001, 'inventory_pct': 10}
            },
            'hummingbot_arb': {
                'name': '跨交易所做市', 'source': 'Hummingbot', 'category': 'arb',
                'description': '多交易所价差套利',
                'entry': '发现价差>0.5%', 'exit': '价差消失', 'risk': 'medium', 'win_rate': 72,
                'parameters': {'min_spread': 0.5}
            },
            
            # Cryptohopper (2个)
            'cryptohopper_signal': {
                'name': '信号交易', 'source': 'Cryptohopper', 'category': 'signal',
                'description': '跟随信号交易',
                'entry': '收到信号', 'exit': '信号消失', 'risk': 'medium', 'win_rate': 70,
                'parameters': {'signals': ['RSI', 'MACD', 'EMA']}
            },
            'cryptohopper_自动': {
                'name': '全自动交易', 'source': 'Cryptohopper', 'category': 'auto',
                'description': 'AI自动选择最佳策略',
                'entry': 'AI判断', 'exit': 'AI止盈', 'risk': 'medium', 'win_rate': 65,
                'parameters': {'ai_enabled': True}
            },
            
            # Bitget (2个)
            'bitget_copy': {
                'name': '跟单系统', 'source': 'Bitget', 'category': 'copy',
                'description': '复制顶级交易员',
                'entry': '跟随交易员', 'exit': '停止跟随', 'risk': 'medium', 'win_rate': 75,
                'parameters': {'copiers': 100, 'allocation': 1000}
            },
            'bitget_网格': {
                'name': '合约网格', 'source': 'Bitget', 'category': 'grid',
                'description': 'USDT合约网格交易',
                'entry': '区间震荡', 'exit': '突破区间', 'risk': 'medium', 'win_rate': 68,
                'parameters': {'leverage': 10, 'grids': 50}
            },
            
            # Binance (2个)
            'binance_spot_grid': {
                'name': '现货网格', 'source': 'Binance', 'category': 'grid',
                'description': '现货网格交易',
                'entry': '区间震荡', 'exit': '突破区间', 'risk': 'low', 'win_rate': 67,
                'parameters': {'grids': 20, 'price_range': 15}
            },
            'binance_趋势网格': {
                'name': '智能趋势追踪', 'source': 'Binance', 'category': 'trend',
                'description': '智能追踪趋势，突破买入',
                'entry': '趋势形成', 'exit': '趋势反转', 'risk': 'medium', 'win_rate': 70,
                'parameters': {'trend_ma': 50, 'breakout_threshold': 2}
            },
            
            # Coinrule (2个)
            'coinrule_ifthen': {
                'name': 'IF-THEN自动化', 'source': 'Coinrule', 'category': 'auto',
                'description': '条件触发交易',
                'entry': '条件满足', 'exit': '条件反转', 'risk': 'low', 'win_rate': 58,
                'parameters': {'conditions': 3}
            },
            'coinrule_止盈止损': {
                'name': '智能止盈止损', 'source': 'Coinrule', 'category': 'risk',
                'description': '自动止盈止损',
                'entry': '开仓后', 'exit': '触发条件', 'risk': 'low', 'win_rate': 80,
                'parameters': {'stop_loss': 2, 'take_profit': 5}
            },
            
            # HaasOnline (2个)
            'haas_script': {
                'name': '脚本量化', 'source': 'HaasOnline', 'category': 'script',
                'description': '自定义脚本策略',
                'entry': '脚本信号', 'exit': '脚本条件', 'risk': 'high', 'win_rate': 55,
                'parameters': {'script': 'custom'}
            },
            'haas_多指标': {
                'name': '多指标组合', 'source': 'HaasOnline', 'category': 'combo',
                'description': '多指标综合判断',
                'entry': '多指标共振', 'exit': '指标背离', 'risk': 'medium', 'win_rate': 68,
                'parameters': {'indicators': ['RSI', 'MACD', 'BB']}
            },
            
            # Bitsgap (2个)
            'bitsgap_arb': {
                'name': '跨交易所套利', 'source': 'Bitsgap', 'category': 'arb',
                'description': '跨交易所价差套利',
                'entry': '发现价差', 'exit': '价差消失', 'risk': 'medium', 'win_rate': 78,
                'parameters': {'exchanges': 3, 'min_diff': 0.5}
            },
            'bitsgap_triangle': {
                'name': '三角套利', 'source': 'Bitsgap', 'category': 'arb',
                'description': '同一交易所三角套利',
                'entry': '三角价差', 'exit': '收敛', 'risk': 'low', 'win_rate': 85,
                'parameters': {'min_profit': 0.1}
            }
        }
        
        # ============== 原生策略库 (11个) ==============
        self.native_strategies = {
            # 核心4个策略
            'trend_follow': {
                'name': '趋势跟踪', 'category': 'trend', 'type': 'core',
                'description': 'MA20>MA50 + RSI<70 + 放量突破',
                'entry': 'MA20>MA50 + RSI<70 + 放量突破',
                'exit': '跌破均线止盈/止损-5%',
                'risk': 'medium', 'win_rate': 72, 'expected_return': '12.5%/月',
                'parameters': {'ma_fast': 20, 'ma_slow': 50, 'rsi_oversold': 30}
            },
            'grid_trade': {
                'name': '网格交易', 'category': 'grid', 'type': 'core',
                'description': '当前价±15%区间',
                'entry': '当前价±15%区间',
                'exit': '每格+1.5%止盈',
                'risk': 'low', 'win_rate': 80, 'expected_return': '15%/月',
                'parameters': {'grid_pct': 15, 'profit_per_grid': 1.5}
            },
            'ma_pullback': {
                'name': '均线回踩', 'category': 'pullback', 'type': 'core',
                'description': '回踩MA20 + 看涨K线',
                'entry': '回踩MA20 + 看涨K线',
                'exit': '止损-2%',
                'risk': 'low', 'win_rate': 75, 'expected_return': '10%/月',
                'parameters': {'ma_period': 20, 'rsi_oversold': 35}
            },
            'breakout': {
                'name': '突破策略', 'category': 'breakout', 'type': 'core',
                'description': '缩量盘整后放量突破',
                'entry': '缩量盘整后放量突破',
                'exit': '止盈10-20%',
                'risk': 'medium', 'win_rate': 68, 'expected_return': '18%/月',
                'parameters': {'consolidation_bars': 20, 'volume_mult': 2}
            },
            
            # 扩展7个策略
            'airdrop': {
                'name': '空投猎手', 'category': 'airdrop', 'type': 'native',
                'description': 'DEX新币监控，空投潜力评估',
                'entry': '新币上线+社区热度高',
                'exit': '达到目标卖出',
                'risk': 'high', 'win_rate': 30, 'expected_return': '不确定',
                'parameters': {'dex': 'uniswap', 'min_liquidity': 10000}
            },
            'alt_arb': {
                'name': '跨链套利', 'category': 'arbitrage', 'type': 'native',
                'description': '跨交易所/跨链价差套利',
                'entry': '发现价差>1%',
                'exit': '价差消失',
                'risk': 'medium', 'win_rate': 75, 'expected_return': '8%/月',
                'parameters': {'min_spread': 1, 'execution_ms': 500}
            },
            'copy_trade': {
                'name': '智能跟单', 'category': 'copy', 'type': 'native',
                'description': '跟随盈利交易员，自动分配仓位',
                'entry': '跟单盈利信号',
                'exit': '交易员连续亏损',
                'risk': 'medium', 'win_rate': 70, 'expected_return': '15%/月',
                'parameters': {'max_traders': 5, 'allocation_pct': 20}
            },
            'crowdsource': {
                'name': '众包信号', 'category': 'crowdsource', 'type': 'native',
                'description': '聚合社区信号，权重分配',
                'entry': '多源信号共振',
                'exit': '信号消失',
                'risk': 'medium', 'win_rate': 65, 'expected_return': '10%/月',
                'parameters': {'sources': 5, 'threshold': 3}
            },
            'mainstream_trend': {
                'name': '主流趋势', 'category': 'trend', 'type': 'native',
                'description': 'BTC/ETH/SOL趋势跟踪',
                'entry': 'BTC>MA200 + 成交量放大',
                'exit': '跌破MA200',
                'risk': 'medium', 'win_rate': 68, 'expected_return': '12%/月',
                'parameters': {'coins': ['BTC', 'ETH', 'SOL'], 'ma': 200}
            },
            'market_maker': {
                'name': '做市商策略', 'category': 'mm', 'type': 'native',
                'description': '双边挂单赚取手续费+价差',
                'entry': '波动市场',
                'exit': '波动率<10%',
                'risk': 'medium', 'win_rate': 75, 'expected_return': '8%/月',
                'parameters': {'spread': 0.002, 'inventory': 50}
            },
            'prediction': {
                'name': '预测市场', 'category': 'prediction', 'type': 'native',
                'description': '基于Polymarket等预测市场',
                'entry': '概率变化>10%',
                'exit': '事件结束',
                'risk': 'medium', 'win_rate': 60, 'expected_return': '20%/月',
                'parameters': {'min_prob_change': 10, 'max_position': 100}
            }
        }
        
        # 投资组合
        self.strategy_portfolios = {
            'conservative': {
                'name': '保守组合', 'risk': 'low',
                'allocation': {'grid_trade': 50, 'dca': 30, 'market_maker': 20}
            },
            'balanced': {
                'name': '平衡组合', 'risk': 'medium',
                'allocation': {'trend_follow': 40, 'grid_trade': 30, 'copy_trade': 30}
            },
            'aggressive': {
                'name': '激进组合', 'risk': 'high',
                'allocation': {'breakout': 40, 'prediction': 30, 'alt_arb': 30}
            }
        }
    
    def get_all(self):
        return {
            'competitor': self.competitor_strategies,
            'native': self.native_strategies,
            'portfolios': self.strategy_portfolios,
            'count': len(self.competitor_strategies) + len(self.native_strategies)
        }
    
    def get_by_category(self, category):
        all_strats = {**self.competitor_strategies, **self.native_strategies}
        return {k: v for k, v in all_strats.items() if v.get('category') == category}
    
    def get_active(self):
        all_strats = {**self.competitor_strategies, **self.native_strategies}
        return {k: v for k, v in all_strats.items() if v.get('active', True)}

# ==================== 完整声纳趋势库 (30+模型) ====================
class SonarDatabase:
    """声纳趋势库 - 30+多源AI信号"""
    
    def __init__(self):
        self.sonar_models = {
            # ===== 技术指标 (10个) =====
            'rsi_divergence': {
                'name': 'RSI背离', 'category': 'technical', 'type': 'indicator',
                'description': '价格与RSI指标背离，预示趋势反转',
                'entry': 'RSI<30且价格创新低 | RSI>70且价格创新高',
                'signal': 'reversal', 'accuracy': 72.5, 'sources': ['TradingView'], 'weight': 0.8
            },
            'macd_cross': {
                'name': 'MACD金叉/死叉', 'category': 'technical', 'type': 'indicator',
                'description': 'MACD指标交叉信号',
                'entry': 'DIF上穿DEA买入 | DIF下穿DEA卖出',
                'signal': 'bullish', 'accuracy': 68.2, 'sources': ['TradingView'], 'weight': 0.7
            },
            'volume_spike': {
                'name': '成交量爆发', 'category': 'technical', 'type': 'volume',
                'description': '成交量异常放大3倍以上',
                'entry': '成交量>均量3倍',
                'signal': 'bullish', 'accuracy': 75.0, 'sources': ['Binance'], 'weight': 0.8
            },
            'trend_line_break': {
                'name': '趋势线突破', 'category': 'technical', 'type': 'pattern',
                'description': '关键趋势线突破确认',
                'entry': '突破上升趋势线',
                'signal': 'bullish', 'accuracy': 70.5, 'sources': ['TradingView'], 'weight': 0.7
            },
            'support_resistance': {
                'name': '支撑阻力', 'category': 'technical', 'type': 'pattern',
                'description': '关键价位测试与突破',
                'entry': '触及支撑/阻力位',
                'signal': 'neutral', 'accuracy': 65.8, 'sources': ['TradingView'], 'weight': 0.6
            },
            'bollinger_bands': {
                'name': '布林带突破', 'category': 'technical', 'type': 'indicator',
                'description': '布林带收口后突破',
                'entry': '价格突破上轨买入 | 突破下轨卖出',
                'signal': 'neutral', 'accuracy': 63.2, 'sources': ['TradingView'], 'weight': 0.6
            },
            'ma_crossover': {
                'name': '均线金叉', 'category': 'technical', 'type': 'indicator',
                'description': '短期均线上穿长期均线',
                'entry': 'MA5上穿MA20 | MA20上穿MA50',
                'signal': 'bullish', 'accuracy': 71.5, 'sources': ['TradingView'], 'weight': 0.75
            },
            'keltner_breakout': {
                'name': '肯特纳突破', 'category': 'technical', 'type': 'pattern',
                'description': '肯特纳通道突破',
                'entry': '价格突破通道上轨',
                'signal': 'bullish', 'accuracy': 69.0, 'sources': ['TradingView'], 'weight': 0.7
            },
            'stoch_rsi': {
                'name': 'StochRSI', 'category': 'technical', 'type': 'indicator',
                'description': 'Stochastic RSI超买超卖',
                'entry': 'K<20超卖买入 | K>80超买卖出',
                'signal': 'reversal', 'accuracy': 70.0, 'sources': ['TradingView'], 'weight': 0.7
            },
            'atr_volatility': {
                'name': 'ATR波动率', 'category': 'technical', 'type': 'volatility',
                'description': 'ATR指标判断波动率',
                'entry': 'ATR突破均线',
                'signal': 'neutral', 'accuracy': 62.0, 'sources': ['TradingView'], 'weight': 0.55
            },
            
            # ===== 链上指标 (5个) =====
            'onchain_whale': {
                'name': '链上巨鲸', 'category': 'onchain', 'type': 'whale',
                'description': '大额链上转账检测',
                'entry': '单笔转账>1000BTC',
                'signal': 'bullish', 'accuracy': 78.5, 'sources': ['Glassnode'], 'weight': 0.85
            },
            'onchain_exchange_flow': {
                'name': '交易所流向', 'category': 'onchain', 'type': 'flow',
                'description': '交易所资金流入流出',
                'entry': '净流入增加',
                'signal': 'bullish', 'accuracy': 71.0, 'sources': ['Glassnode', 'CryptoQuant'], 'weight': 0.75
            },
            'onchain_nvt': {
                'name': 'NVT信号', 'category': 'onchain', 'type': 'valuation',
                'description': '网络价值比交易量',
                'entry': 'NVT低于历史均值',
                'signal': 'bullish', 'accuracy': 67.0, 'sources': ['Glassnode'], 'weight': 0.65
            },
            'onchain_holders': {
                'name': '长期持有者', 'category': 'onchain', 'type': 'holder',
                'description': '长期持有地址增加',
                'entry': 'HODLer数量增长',
                'signal': 'bullish', 'accuracy': 72.0, 'sources': ['Glassnode'], 'weight': 0.75
            },
            'onchain_stable': {
                'name': '稳定币流向', 'category': 'onchain', 'type': 'stablecoin',
                'description': 'USDT/USDC流入交易所',
                'entry': '稳定币净流入增加',
                'signal': 'bullish', 'accuracy': 69.0, 'sources': ['Glassnode'], 'weight': 0.7
            },
            
            # ===== 情绪指标 (5个) =====
            'sentiment_extreme': {
                'name': '情绪极端', 'category': 'sentiment', 'type': 'emotion',
                'description': '市场情绪极端值检测',
                'entry': '恐惧贪婪指数<20或>80',
                'signal': 'reversal', 'accuracy': 71.0, 'sources': ['Alternative.me'], 'weight': 0.75
            },
            'social_spike': {
                'name': '社交媒体爆发', 'category': 'sentiment', 'type': 'social',
                'description': 'Twitter/Reddit讨论量激增',
                'entry': '讨论量>均值5倍',
                'signal': 'bullish', 'accuracy': 65.0, 'sources': ['LunarCrush'], 'weight': 0.65
            },
            'google_trends': {
                'name': '谷歌趋势', 'category': 'sentiment', 'type': 'search',
                'description': '关键词搜索量激增',
                'entry': '搜索量增长>200%',
                'signal': 'bullish', 'accuracy': 63.0, 'sources': ['Google'], 'weight': 0.6
            },
            'news_sentiment': {
                'name': '新闻情绪', 'category': 'sentiment', 'type': 'nlp',
                'description': '新闻情感分析',
                'entry': '正面新闻>负面新闻',
                'signal': 'bullish', 'accuracy': 62.0, 'sources': ['CryptoPanic'], 'weight': 0.6
            },
            'influencer_flow': {
                'name': 'KOL资金流', 'category': 'sentiment', 'type': 'influencer',
                'description': '意见领袖地址动向',
                'entry': 'KOL地址转入',
                'signal': 'bullish', 'accuracy': 68.0, 'sources': ['Twitter'], 'weight': 0.7
            },
            
            # ===== 预测市场 (3个) =====
            'polymarket_odds': {
                'name': '预测概率变化', 'category': 'prediction', 'type': 'odds',
                'description': 'Polymarket赔率突变',
                'entry': '概率变化>10%',
                'signal': 'bullish', 'accuracy': 73.0, 'sources': ['Polymarket'], 'weight': 0.8
            },
            'prediction_sentiment': {
                'name': '预测市场情绪', 'category': 'prediction', 'type': 'sentiment',
                'description': '预测市场整体情绪',
                'entry': '多数事件概率>60%',
                'signal': 'bullish', 'accuracy': 68.0, 'sources': ['Polymarket'], 'weight': 0.7
            },
            'bet_volume': {
                'name': '投注量异动', 'category': 'prediction', 'type': 'volume',
                'description': '预测市场投注量激增',
                'entry': '投注量增长>100%',
                'signal': 'bullish', 'accuracy': 70.0, 'sources': ['Polymarket'], 'weight': 0.75
            },
            
            # ===== 资金流向 (3个) =====
            'fund_flow': {
                'name': '资金流向', 'category': 'flow', 'type': 'capital',
                'description': '大单资金流向',
                'entry': '主力资金净流入',
                'signal': 'bullish', 'accuracy': 72.0, 'sources': ['Binance'], 'weight': 0.8
            },
            'spot_etf_flow': {
                'name': 'ETF资金流', 'category': 'flow', 'type': 'etf',
                'description': '现货ETF净流入',
                'entry': 'ETF净流入增加',
                'signal': 'bullish', 'accuracy': 76.0, 'sources': ['Bloomberg'], 'weight': 0.85
            },
            'institutional_flow': {
                'name': '机构资金', 'category': 'flow', 'type': 'institutional',
                'description': '机构资金动向',
                'entry': '机构地址转入',
                'signal': 'bullish', 'accuracy': 75.0, 'sources': ['Glassnode'], 'weight': 0.8
            },
            
            # ===== 衍生品 (3个) =====
            'futures_funding': {
                'name': '资金费率', 'category': 'derivatives', 'type': 'funding',
                'description': '合约资金费率异常',
                'entry': '资金费率>0.01%或<-0.01%',
                'signal': 'neutral', 'accuracy': 65.0, 'sources': ['Binance'], 'weight': 0.65
            },
            'liquidations': {
                'name': '强平监控', 'category': 'derivatives', 'type': 'liquidation',
                'description': '大量合约强平',
                'entry': '24h强平金额>1亿',
                'signal': 'reversal', 'accuracy': 70.0, 'sources': ['Coinglass'], 'weight': 0.75
            },
            'options_gamma': {
                'name': '期权Gamma', 'category': 'derivatives', 'type': 'options',
                'description': '期权Gamma挤压',
                'entry': 'Gamma值异常高',
                'signal': 'reversal', 'accuracy': 68.0, 'sources': ['Paradigm'], 'weight': 0.7
            },
            
            # ===== 宏观 (3个) =====
            'dollar_index': {
                'name': '美元指数', 'category': 'macro', 'type': 'currency',
                'description': 'DXY走势与BTC负相关',
                'entry': 'DXY突破关键位',
                'signal': 'reversal', 'accuracy': 69.0, 'sources': ['TradingView'], 'weight': 0.7
            },
            'bitcoin_dom': {
                'name': 'BTC主导', 'category': 'macro', 'type': 'dominance',
                'description': 'BTC市值占比变化',
                'entry': 'Dominance变化>2%',
                'signal': 'neutral', 'accuracy': 66.0, 'sources': ['TradingView'], 'weight': 0.65
            },
            'fear_greed': {
                'name': '恐惧贪婪', 'category': 'macro', 'type': 'sentiment',
                'description': '综合市场情绪指标',
                'entry': 'FGI<25买入 | FGI>75卖出',
                'signal': 'reversal', 'accuracy': 73.0, 'sources': ['Alternative.me'], 'weight': 0.8
            }
        }
    
    def get_all(self):
        return self.sonar_models
    
    def get_by_signal(self, signal):
        return {k: v for k, v in self.sonar_models.items() if v.get('signal') == signal}
    
    def get_active(self):
        return self.sonar_models

# ==================== API配置数据库 ====================
class APIDatabase:
    """API配置数据库"""
    
    def __init__(self):
        self.exchanges = {
            'binance': {'name': 'Binance', 'api_key': '', 'api_secret': '', 'enabled': False},
            'bybit': {'name': 'Bybit', 'api_key': '', 'api_secret': '', 'enabled': False},
            'okx': {'name': 'OKX', 'api_key': '', 'api_secret': '', 'enabled': False},
            'coinbase': {'name': 'Coinbase', 'api_key': '', 'api_secret': '', 'enabled': False},
        }
        self.oracles = {
            'glassnode': {'name': 'Glassnode', 'api_key': '', 'enabled': False},
            'polymarket': {'name': 'Polymarket', 'api_key': '', 'enabled': False},
            'alternativeme': {'name': 'Alternative.me', 'api_key': '', 'enabled': False},
        }
    
    def get_all(self):
        return {'exchanges': self.exchanges, 'oracles': self.oracles}

# ==================== 初始化数据库 ====================
strategy_db = StrategyDatabase()
sonar_db = SonarDatabase()
api_db = APIDatabase()

# ==================== 交易引擎 ====================
class TradingEngine:
    def __init__(self):
        self.exchange = 'binance'
        self.base_url = 'https://api.binance.com'
        self.api_key = ''
        self.api_secret = ''
    
    def get_price(self, symbol):
        try:
            r = requests.get(f"{self.base_url}/api/v3/ticker/24hr", params={"symbol": symbol}, timeout=3)
            if r.status_code == 200:
                d = r.json()
                return {'symbol': d['symbol'], 'price': float(d['lastPrice']), 'change_24h': float(d['priceChangePercent'])}
        except: pass
        # 模拟数据
        mock = {'BTCUSDT':72000,'ETHUSDT':2150,'SOLUSDT':90,'XRPUSDT':1.42,'ADAUSDT':0.27,'AVAXUSDT':10}
        return {'symbol': symbol, 'price': mock.get(symbol, 100), 'change_24h': random.uniform(-5, 10)}
    
    def get_all_prices(self):
        prices = {}
        for sym in ['BTCUSDT','ETHUSDT','SOLUSDT','XRPUSDT','ADAUSDT','AVAXUSDT']:
            prices[sym] = self.get_price(sym)
        return prices
    
    def get_balance(self):
        return {'balances': [{'asset':'USDT','free':10000},{'asset':'BTC','free':0.1},{'asset':'ETH','free':1}], 'mock': True}
    
    def place_order(self, symbol, side, quantity, order_type='MARKET'):
        return {'success': True, 'mock': True, 'orderId': random.randint(100000, 999999), 'symbol': symbol, 'side': side, 'quantity': quantity}
    
    def generate_signals(self):
        signals = []
        pairs = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'XRPUSDT', 'ADAUSDT', 'AVAXUSDT']
        for symbol in pairs:
            data = self.get_price(symbol)
            change = data.get('change_24h', 0)
            coin = symbol.replace('USDT', '')
            action = 'BUY' if change > 3 else 'SELL' if change < -3 else 'HOLD'
            confidence = min(9.5, 5 + change * 0.4)
            signals.append({'coin': coin, 'symbol': symbol, 'action': action, 'confidence': round(confidence, 1), 'price': data.get('price'), 'change_24h': round(change, 2)})
        return signals

trading = TradingEngine()

# ==================== API路由 ====================

@app.route('/')
def index(): return render_template('index.html')

@app.route('/api/db/strategies')
def db_strategies(): return jsonify(strategy_db.get_all())

@app.route('/api/db/sonar')
def db_sonar(): return jsonify(sonar_db.get_all())

@app.route('/api/db/apis')
def db_apis(): return jsonify(api_db.get_all())

@app.route('/api/db/overview')
def db_overview():
    return jsonify({
        'strategies': {'competitor': len(strategy_db.competitor_strategies), 'native': len(strategy_db.native_strategies), 'total': len(strategy_db.competitor_strategies) + len(strategy_db.native_strategies)},
        'sonar': {'total': len(sonar_db.sonar_models)},
        'apis': {'exchanges': len(api_db.exchanges), 'oracles': len(api_db.oracles)},
        'scripts': {'total': 8, 'ready': 6}
    })

@app.route('/api/market/prices')
def market_prices():
    prices = {}
    for sym in ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'XRPUSDT', 'ADAUSDT', 'AVAXUSDT']:
        prices[sym] = trading.get_price(sym)
    return jsonify({'prices': prices, 'timestamp': datetime.now().isoformat()})

@app.route('/api/signals')
def signals(): return jsonify({'signals': trading.generate_signals(), 'timestamp': datetime.now().isoformat()})

@app.route('/api/account/balance')
def account_balance(): return jsonify(trading.get_balance())

@app.route('/api/portfolio')
def portfolio():
    # 模拟持仓数据
    prices = trading.get_all_prices()
    holdings = [
        {'coin': 'BTC', 'amount': 0.01, 'avgPrice': 71000, 'now': prices.get('BTCUSDT',{}).get('price',72000)},
        {'coin': 'ETH', 'amount': 0.5, 'avgPrice': 2100, 'now': prices.get('ETHUSDT',{}).get('price',2150)},
        {'coin': 'SOL', 'amount': 5, 'avgPrice': 88, 'now': prices.get('SOLUSDT',{}).get('price',90)}
    ]
    return jsonify({'holdings': holdings, 'totalValue': sum(h['amount']*h['now'] for h in holdings)})

@app.route('/api/trade/order', methods=['POST'])
def trade_order():
    req = request.json
    return jsonify(trading.place_order(req.get('symbol','BTCUSDT'), req.get('side','BUY'), req.get('quantity',0.01)))

if __name__ == '__main__':
    print("🚀 GO2SE v5 Running on :5001")
    app.run(host='0.0.0.0', port=5001, debug=False)
