"""
P0修复: CCXT真实数据源 + 回测验证
"""

import asyncio
import ccxt
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json

class RealDataBacktest:
    """使用CCXT获取真实市场数据的回测引擎"""
    
    def __init__(self):
        self.exchange = None
        self.exchanges = {}
        self._init_exchanges()
    
    def _init_exchanges(self):
        """初始化交易所连接"""
        try:
            self.exchange = ccxt.binance({
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            })
            # 预加载市场数据
            self.exchange.load_markets()
            
            # 其他交易所
            self.exchanges['okx'] = ccxt.okx({'enableRateLimit': True})
            self.exchanges['bybit'] = ccxt.bybit({'enableRateLimit': True})
            
            print(f"✅ 已连接 Binance: {len(self.exchange.markets)} 个交易对")
        except Exception as e:
            print(f"❌ 交易所连接失败: {e}")
            self.exchange = None
    
    async def fetch_ohlcv(self, symbol: str, timeframe: str = '1h', 
                         since: int = None, limit: int = 500) -> List:
        """获取真实K线数据"""
        if not self.exchange:
            return []
        
        try:
            ohlcv = await asyncio.to_thread(
                self.exchange.fetch_ohlcv,
                symbol,
                timeframe,
                since=since,
                limit=limit
            )
            return ohlcv
        except Exception as e:
            print(f"获取K线失败 {symbol}: {e}")
            return []
    
    async def backtest_rabbit(self, symbols: List[str], days: int = 90) -> Dict:
        """
        回测Rabbit策略 (打兔子 - 前20主流币)
        使用真实市场数据验证胜率
        """
        results = {}
        strategy_configs = [
            {"id": "ema_cross", "name": "EMA交叉", "indicators": ["EMA20", "EMA50"]},
            {"id": "macd", "name": "MACD动量", "indicators": ["MACD", "Signal"]},
            {"id": "rsi_extreme", "name": "RSI极端", "indicators": ["RSI"]},
            {"id": "bb_meanreversion", "name": "布林带均值回归", "indicators": ["BB"]}
        ]
        
        since = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
        
        for symbol in symbols[:5]:  # 测试前5个币
            pair = f"{symbol}/USDT"
            print(f"回测 {pair}...")
            
            ohlcv = await self.fetch_ohlcv(pair, '1h', since)
            if len(ohlcv) < 100:
                continue
            
            symbol_results = []
            
            # 每个策略分别回测
            for config in strategy_configs:
                trades = self._run_strategy(ohlcv, config)
                if trades:
                    win_rate = sum(1 for t in trades if t['pnl'] > 0) / len(trades)
                    avg_pnl = sum(t['pnl'] for t in trades) / len(trades)
                    
                    symbol_results.append({
                        "strategy_id": config["id"],
                        "strategy_name": config["name"],
                        "total_trades": len(trades),
                        "win_rate": win_rate,
                        "avg_pnl": avg_pnl,
                        "total_pnl": sum(t['pnl'] for t in trades)
                    })
            
            if symbol_results:
                results[pair] = symbol_results
        
        return results
    
    def _run_strategy(self, ohlcv: List, config: Dict) -> List[Dict]:
        """运行策略并返回交易列表"""
        closes = [c[4] for c in ohlcv]
        trades = []
        
        if config["id"] == "ema_cross":
            trades = self._ema_cross_strategy(ohlcv, closes)
        elif config["id"] == "macd":
            trades = self._macd_strategy(ohlcv, closes)
        elif config["id"] == "rsi_extreme":
            trades = self._rsi_extreme_strategy(ohlcv, closes)
        elif config["id"] == "bb_meanreversion":
            trades = self._bb_strategy(ohlcv, closes)
        
        return trades
    
    def _ema_cross_strategy(self, ohlcv: List, closes: List) -> List[Dict]:
        """EMA交叉策略"""
        trades = []
        
        # 计算EMA
        ema20 = self._calc_ema(closes, 20)
        ema50 = self._calc_ema(closes, 50)
        
        position = None
        
        for i in range(50, len(closes)):
            if ema20[i] > ema50[i] and ema20[i-1] <= ema50[i-1] and position is None:
                # 买入信号
                position = {"entry_price": closes[i], "entry_idx": i}
            elif ema20[i] < ema50[i] and position is not None:
                # 卖出信号
                pnl = (closes[i] - position["entry_price"]) / position["entry_price"]
                trades.append({
                    "entry_price": position["entry_price"],
                    "exit_price": closes[i],
                    "pnl": pnl,
                    "side": "long"
                })
                position = None
        
        return trades
    
    def _macd_strategy(self, ohlcv: List, closes: List) -> List[Dict]:
        """MACD动量策略"""
        trades = []
        
        macd, signal = self._calc_macd(closes)
        position = None
        
        for i in range(26, len(closes)):
            if macd[i] > signal[i] and macd[i-1] <= signal[i-1] and position is None:
                position = {"entry_price": closes[i], "entry_idx": i}
            elif macd[i] < signal[i] and position is not None:
                pnl = (closes[i] - position["entry_price"]) / position["entry_price"]
                trades.append({
                    "entry_price": position["entry_price"],
                    "exit_price": closes[i],
                    "pnl": pnl,
                    "side": "long"
                })
                position = None
        
        return trades
    
    def _rsi_extreme_strategy(self, ohlcv: List, closes: List) -> List[Dict]:
        """RSI极端值策略"""
        trades = []
        rsi = self._calc_rsi(closes, 14)
        position = None
        
        for i in range(14, len(closes)):
            if rsi[i] < 30 and position is None:
                position = {"entry_price": closes[i], "entry_idx": i}
            elif rsi[i] > 70 and position is not None:
                pnl = (closes[i] - position["entry_price"]) / position["entry_price"]
                trades.append({
                    "entry_price": position["entry_price"],
                    "exit_price": closes[i],
                    "pnl": pnl,
                    "side": "long"
                })
                position = None
        
        return trades
    
    def _bb_strategy(self, ohlcv: List, closes: List) -> List[Dict]:
        """布林带均值回归策略"""
        trades = []
        bb_upper, bb_lower, bb_middle = self._calc_bollinger(closes, 20, 2)
        position = None
        
        for i in range(20, len(closes)):
            if closes[i] < bb_lower[i] and position is None:
                position = {"entry_price": closes[i], "entry_idx": i}
            elif closes[i] > bb_upper[i] and position is not None:
                pnl = (closes[i] - position["entry_price"]) / position["entry_price"]
                trades.append({
                    "entry_price": position["entry_price"],
                    "exit_price": closes[i],
                    "pnl": pnl,
                    "side": "long"
                })
                position = None
        
        return trades
    
    # ==================== 技术指标 ====================
    
    def _calc_ema(self, data: List, period: int) -> List:
        """计算EMA"""
        if len(data) < period:
            return [50] * len(data)
        
        k = 2 / (period + 1)
        ema = [data[0]]
        
        for i in range(1, len(data)):
            ema.append(data[i] * k + ema[-1] * (1 - k))
        
        return ema
    
    def _calc_macd(self, closes: List, fast: int = 12, slow: int = 26, signal: int = 9):
        """计算MACD"""
        ema_fast = self._calc_ema(closes, fast)
        ema_slow = self._calc_ema(closes, slow)
        
        macd = [ema_fast[i] - ema_slow[i] for i in range(len(closes))]
        signal_line = self._calc_ema(macd, signal)
        
        return macd, signal_line
    
    def _calc_rsi(self, closes: List, period: int = 14) -> List:
        """计算RSI"""
        if len(closes) < period + 1:
            return [50] * len(closes)
        
        deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        
        rsi = [50] * period
        
        for i in range(period, len(deltas)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            
            if avg_loss == 0:
                rsi.append(100)
            else:
                rs = avg_gain / avg_loss
                rsi.append(100 - 100 / (1 + rs))
        
        return rsi
    
    def _calc_bollinger(self, closes: List, period: int = 20, std_dev: int = 2):
        """计算布林带"""
        if len(closes) < period:
            return closes, closes, closes
        
        bb_upper = []
        bb_lower = []
        bb_middle = []
        
        for i in range(len(closes)):
            if i < period - 1:
                bb_upper.append(closes[i])
                bb_lower.append(closes[i])
                bb_middle.append(closes[i])
            else:
                window = closes[i - period + 1:i + 1]
                sma = sum(window) / period
                variance = sum((x - sma) ** 2 for x in window) / period
                std = variance ** 0.5
                
                bb_middle.append(sma)
                bb_upper.append(sma + std_dev * std)
                bb_lower.append(sma - std_dev * std)
        
        return bb_upper, bb_lower, bb_middle


# ==================== 修复后的策略配置 ====================

def fix_rabbit_config():
    """修复Rabbit仓位配置冲突"""
    
    # 原始配置: 30个币, max_position=0.6 (60%)
    # 问题: 如果同时持仓30个币, 总仓位 = 30 * 0.6 = 18 = 1800% ❌
    
    # 修复方案:
    # 1. 25%总仓位, 假设同时持有5个币
    # 2. 每个币的仓位 = 25% / 5 = 5%
    # 3. max_position 应该改为 0.05 (5%)
    
    fixed_config = {
        "name": "打兔子",
        "allocation": 25,  # 总仓位25%
        "position_pct": 25,
        "stop_loss": 5,
        "take_profit": 8,
        "max_position": 0.05,  # ✅ 修复: 每个币最多5%仓位 (25%/5币)
        "max_concurrent_positions": 5,  # ✅ 修复: 最多同时持有5个币
        "coins": [
            "BTC", "ETH", "BNB", "XRP", "ADA", "DOGE", "SOL", "DOT",
            "MATIC", "SHIB", "LTC", "AVAX", "LINK", "UNI", "ATOM", "XLM",
            "ALGO", "VET", "ICP", "FIL"
        ],
        "strategies": [
            {
                "id": "ema_cross",
                "name": "EMA交叉策略",
                "type": "trend",
                "weight": 0.35,
                "winrate": 0.745,  # ✅ 待回测验证
                "parameters": {
                    "ema_fast": 20,
                    "ema_slow": 50,
                    "rsi_threshold": 70
                }
            },
            {
                "id": "macd",
                "name": "MACD动量策略",
                "type": "momentum",
                "weight": 0.25,
                "winrate": 0.718,  # ✅ 待回测验证
                "parameters": {
                    "macd_fast": 12,
                    "macd_slow": 26,
                    "signal": 9
                }
            },
            {
                "id": "bb_meanreversion",
                "name": "布林带均值回归",
                "type": "volatility",
                "weight": 0.20,
                "winrate": 0.682,  # ✅ 待回测验证
                "parameters": {
                    "bb_period": 20,
                    "bb_std": 2
                }
            },
            {
                "id": "rsi_extreme",
                "name": "RSI极端值策略",
                "type": "mean_reversion",
                "weight": 0.20,
                "winrate": 0.721,  # ✅ 待回测验证
                "parameters": {
                    "rsi_period": 14,
                    "oversold": 30,
                    "overbought": 70
                }
            }
        ]
    }
    
    return fixed_config


# ==================== 跨工具信号融合 ====================

class CrossToolSignalFusion:
    """
    跨工具信号融合引擎
    
    7个工具各自独立 → 信号融合层统一协调
    """
    
    def __init__(self):
        self.tools_weights = {
            "rabbit": 0.25,      # 打兔子
            "mole": 0.20,        # 打地鼠
            "oracle": 0.15,      # 走着瞧
            "leader": 0.15,      # 跟大哥
            "hitchhiker": 0.10, # 搭便车
            "airdrop": 0.03,      # 薅羊毛
            "crowdsource": 0.02  # 穷孩子
        }
        self.confidence_threshold = 0.70  # 70%置信度阈值
    
    def fuse_signals(self, tool_signals: Dict[str, List[Dict]]) -> Dict:
        """
        融合来自各工具的信号
        
        Args:
            tool_signals: {
                "rabbit": [{"symbol": "BTC", "signal": "buy", "confidence": 0.85}, ...],
                "mole": [{"symbol": "ETH", "signal": "buy", "confidence": 0.75}, ...],
                ...
            }
        
        Returns:
            fused_signals: [{"symbol": "BTC", "signal": "buy", "confidence": 0.82, "tools": [...]}, ...]
        """
        # 1. 聚合所有信号
        all_signals = {}
        
        for tool, signals in tool_signals.items():
            tool_weight = self.tools_weights.get(tool, 0)
            
            for sig in signals:
                symbol = sig.get("symbol")
                if not symbol:
                    continue
                
                if symbol not in all_signals:
                    all_signals[symbol] = {
                        "symbol": symbol,
                        "signals": [],
                        "weighted_confidence": 0,
                        "total_weight": 0
                    }
                
                confidence = sig.get("confidence", 0.5)
                weighted_conf = confidence * tool_weight
                
                all_signals[symbol]["signals"].append({
                    "tool": tool,
                    "signal": sig.get("signal"),
                    "confidence": confidence,
                    "tool_weight": tool_weight,
                    "weighted_confidence": weighted_conf
                })
                
                all_signals[symbol]["weighted_confidence"] += weighted_conf
                all_signals[symbol]["total_weight"] += tool_weight
        
        # 2. 计算融合置信度
        fused = []
        
        for symbol, data in all_signals.items():
            if data["total_weight"] == 0:
                continue
            
            final_confidence = data["weighted_confidence"] / data["total_weight"]
            
            # 统计信号方向
            buy_votes = sum(1 for s in data["signals"] if s["signal"] == "buy")
            sell_votes = sum(1 for s in data["signals"] if s["signal"] == "sell")
            
            if buy_votes > sell_votes:
                final_signal = "buy"
            elif sell_votes > buy_votes:
                final_signal = "sell"
            else:
                final_signal = "hold"
            
            fused.append({
                "symbol": symbol,
                "signal": final_signal,
                "confidence": final_confidence,
                "buy_votes": buy_votes,
                "sell_votes": sell_votes,
                "tools": [s["tool"] for s in data["signals"]],
                "approved": final_confidence >= self.confidence_threshold
            })
        
        # 3. 按置信度排序
        fused.sort(key=lambda x: x["confidence"], reverse=True)
        
        return {
            "fused_signals": fused,
            "summary": {
                "total_symbols": len(fused),
                "approved_signals": sum(1 for f in fused if f["approved"]),
                "buy_signals": sum(1 for f in fused if f["signal"] == "buy"),
                "sell_signals": sum(1 for f in fused if f["signal"] == "sell")
            }
        }
    
    def add_mirofish_verification(self, fused_signals: List[Dict], 
                                   mirofish_results: Dict) -> List[Dict]:
        """
        添加MiroFish验证层
        
        MiroFish共识验证通过的信号, 置信度提升
        """
        verified = []
        
        for sig in fused_signals:
            symbol = sig["symbol"]
            
            # 检查MiroFish验证结果
            mf_result = mirofish_results.get(symbol, {})
            mf_confidence = mf_result.get("confidence", 0.5)
            
            if mf_confidence > 0.75:
                # MiroFish验证通过, 提升置信度
                sig["mirofish_verified"] = True
                sig["mirofish_confidence"] = mf_confidence
                sig["confidence"] = sig["confidence"] * 0.7 + mf_confidence * 0.3
                sig["approved"] = sig["confidence"] >= self.confidence_threshold
            else:
                sig["mirofish_verified"] = False
                sig["mirofish_confidence"] = mf_confidence
            
            verified.append(sig)
        
        return verified


# ==================== 验证和更新策略胜率 ====================

async def verify_strategy_winrates():
    """使用真实数据验证策略胜率"""
    
    backtest = RealDataBacktest()
    
    if not backtest.exchange:
        return {"error": "无法连接交易所"}
    
    # 回测币种
    symbols = ["BTC", "ETH", "BNB", "SOL", "XRP"]
    
    print("开始回测验证策略胜率...")
    results = await backtest.backtest_rabbit(symbols, days=90)
    
    # 计算加权平均胜率
    verified_winrates = {}
    
    for symbol, strategy_results in results.items():
        for sr in strategy_results:
            strategy_id = sr["strategy_id"]
            if strategy_id not in verified_winrates:
                verified_winrates[strategy_id] = {
                    "name": sr["strategy_name"],
                    "total_trades": 0,
                    "total_pnl": 0,
                    "win_count": 0
                }
            
            verified_winrates[strategy_id]["total_trades"] += sr["total_trades"]
            verified_winrates[strategy_id]["total_pnl"] += sr["total_pnl"]
            verified_winrates[strategy_id]["win_count"] += int(sr["win_rate"] * sr["total_trades"])
    
    # 计算最终胜率
    final_winrates = {}
    for sid, data in verified_winrates.items():
        if data["total_trades"] > 0:
            final_winrates[sid] = {
                "name": data["name"],
                "verified_winrate": data["win_count"] / data["total_trades"],
                "total_trades": data["total_trades"],
                "avg_pnl": data["total_pnl"] / data["total_trades"]
            }
    
    return {
        "verified_winrates": final_winrates,
        "backtest_period": "90 days",
        "symbols_tested": symbols
    }


if __name__ == "__main__":
    # 测试
    print("=== CCXT连接测试 ===")
    backtest = RealDataBacktest()
    
    print("\n=== Rabbit配置修复 ===")
    fixed = fix_rabbit_config()
    print(f"max_position: {fixed['max_position']} (修复前: 0.6)")
    print(f"max_concurrent_positions: {fixed['max_concurrent_positions']}")
    
    print("\n=== 跨工具信号融合测试 ===")
    fusion = CrossToolSignalFusion()
    
    test_signals = {
        "rabbit": [
            {"symbol": "BTC", "signal": "buy", "confidence": 0.85},
            {"symbol": "ETH", "signal": "buy", "confidence": 0.72}
        ],
        "mole": [
            {"symbol": "BTC", "signal": "buy", "confidence": 0.68},
            {"symbol": "SOL", "signal": "sell", "confidence": 0.75}
        ],
        "oracle": [
            {"symbol": "BTC", "signal": "buy", "confidence": 0.80}
        ]
    }
    
    result = fusion.fuse_signals(test_signals)
    print(f"融合信号数: {result['summary']['total_symbols']}")
    print(f"买入信号: {result['summary']['buy_signals']}")
    print(f"卖出信号: {result['summary']['sell_signals']}")
