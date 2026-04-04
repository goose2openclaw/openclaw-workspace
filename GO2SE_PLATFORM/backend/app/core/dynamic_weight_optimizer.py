"""
策略动态权重优化器 + MiroFish信号融合层 + 交易成本模拟

实现:
1. 策略评分动态权重 (根据回测结果调整weight)
2. MiroFish与声纳库信号融合
3. 滑点/手续费模拟
"""

import asyncio
import ccxt
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
import json

# ==================== 交易成本模拟 ====================

@dataclass
class TradingCost:
    """交易成本"""
    slippage: float        # 滑点 (例如 0.001 = 0.1%)
    maker_fee: float      # Maker手续费
    taker_fee: float      # Taker手续费
    funding_rate: float    # 资金费率 (用于合约)
    
    def total_cost(self, side: str = "taker") -> float:
        """计算总交易成本"""
        fee = self.taker_fee if side == "taker" else self.maker_fee
        return self.slippage + fee

@dataclass
class BacktestTrade:
    """回测交易(含成本)"""
    entry_price: float
    exit_price: float
    side: str
    amount: float
    pnl_gross: float     # 毛利润
    pnl_net: float       # 净利润(含成本)
    slippage_cost: float
    fee_cost: float
    total_cost: float
    exit_reason: str      # stop_loss / take_profit / signal

# 默认成本配置 (Binance现货)
DEFAULT_TRADING_COST = TradingCost(
    slippage=0.001,    # 0.1% 滑点
    maker_fee=0.001,   # 0.1% Maker手续费
    taker_fee=0.001,   # 0.1% Taker手续费
    funding_rate=0.0     # 现货无资金费率
)

class TradingCostSimulator:
    """交易成本模拟器"""
    
    def __init__(self, cost: TradingCost = None):
        self.cost = cost or DEFAULT_TRADING_COST
    
    def simulate_trade(self, entry_price: float, exit_price: float, 
                     side: str, amount: float) -> BacktestTrade:
        """模拟单笔交易(含成本)"""
        # 计算毛利润
        if side == "long":
            pnl_gross = (exit_price - entry_price) * amount
        else:  # short
            pnl_gross = (entry_price - exit_price) * amount
        
        # 计算滑点成本
        avg_price = (entry_price + exit_price) / 2
        slippage_cost = avg_price * self.cost.slippage * amount
        
        # 计算手续费
        entry_value = entry_price * amount
        exit_value = exit_price * amount
        fee_cost = (entry_value + exit_value) * self.cost.taker_fee
        
        # 总成本
        total_cost = slippage_cost + fee_cost
        
        # 净利润
        pnl_net = pnl_gross - total_cost
        
        return BacktestTrade(
            entry_price=entry_price,
            exit_price=exit_price,
            side=side,
            amount=amount,
            pnl_gross=pnl_gross,
            pnl_net=pnl_net,
            slippage_cost=slippage_cost,
            fee_cost=fee_cost,
            total_cost=total_cost,
            exit_reason="unknown"
        )
    
    def get_cost_summary(self, trades: List[BacktestTrade]) -> Dict:
        """获取成本汇总"""
        total_slippage = sum(t.slippage_cost for t in trades)
        total_fees = sum(t.fee_cost for t in trades)
        total_costs = sum(t.total_cost for t in trades)
        gross_pnl = sum(t.pnl_gross for t in trades)
        net_pnl = sum(t.pnl_net for t in trades)
        
        return {
            "total_trades": len(trades),
            "total_slippage": total_slippage,
            "total_fees": total_fees,
            "total_costs": total_costs,
            "gross_pnl": gross_pnl,
            "net_pnl": net_pnl,
            "cost_ratio": total_costs / abs(gross_pnl) if gross_pnl != 0 else 0,
            "avg_cost_per_trade": total_costs / len(trades) if trades else 0
        }


# ==================== 策略动态权重 ====================

class DynamicWeightOptimizer:
    """
    策略动态权重优化器
    
    根据回测结果自动调整策略权重:
    - 回测得分高 -> 增加权重
    - 回测得分低 -> 降低权重
    - 持续低迷 -> 淘汰
    """
    
    def __init__(self):
        # 基础配置
        self.base_weights = {
            "rabbit_ema_cross": 0.35,
            "rabbit_macd": 0.25,
            "rabbit_rsi": 0.20,
            "rabbit_bb": 0.20,
        }
        
        # 当前动态权重
        self.current_weights = self.base_weights.copy()
        
        # 历史得分
        self.scores_history = {}
        
        # 权重边界
        self.min_weight = 0.05
        self.max_weight = 0.50
        self.promote_factor = 1.2  # 升级因子
        self.demote_factor = 0.8    # 降级因子
    
    def update_weights(self, backtest_results: Dict[str, float]):
        """
        根据回测得分更新权重
        
        Args:
            backtest_results: {strategy_id: score}
        """
        total_score = sum(backtest_results.values())
        if total_score == 0:
            return
        
        new_weights = {}
        
        for strategy_id, score in backtest_results.items():
            base = self.base_weights.get(strategy_id, 0.1)
            
            # 根据得分调整
            if score >= 80:  # A级 - 提升
                adjusted = base * self.promote_factor
            elif score >= 60:  # B级 - 保持
                adjusted = base
            elif score >= 40:  # C级 - 降低
                adjusted = base * self.demote_factor
            else:  # D级 - 显著降低
                adjusted = base * self.demote_factor * 0.5
            
            # 边界限制
            adjusted = max(self.min_weight, min(self.max_weight, adjusted))
            new_weights[strategy_id] = adjusted
        
        # 归一化
        total = sum(new_weights.values())
        if total > 0:
            self.current_weights = {k: v / total for k, v in new_weights.items()}
        
        # 记录历史
        for strategy_id, score in backtest_results.items():
            if strategy_id not in self.scores_history:
                self.scores_history[strategy_id] = []
            self.scores_history[strategy_id].append({
                "timestamp": datetime.now().isoformat(),
                "score": score,
                "weight": self.current_weights.get(strategy_id, 0)
            })
        
        return self.current_weights
    
    def get_weights(self) -> Dict[str, float]:
        """获取当前权重"""
        return self.current_weights.copy()
    
    def get_recommendations(self) -> List[Dict]:
        """获取优化建议"""
        recommendations = []
        
        for strategy_id, weight in self.current_weights.items():
            history = self.scores_history.get(strategy_id, [])
            if not history:
                continue
            
            recent_scores = [h["score"] for h in history[-5:]]
            avg_score = sum(recent_scores) / len(recent_scores)
            
            if avg_score >= 80:
                action = "增加仓位"
            elif avg_score >= 60:
                action = "保持"
            elif avg_score >= 40:
                action = "减少仓位"
            else:
                action = "考虑淘汰"
            
            recommendations.append({
                "strategy": strategy_id,
                "current_weight": weight,
                "avg_score": avg_score,
                "action": action
            })
        
        return sorted(recommendations, key=lambda x: x["avg_score"], reverse=True)


# ==================== MiroFish信号融合 ====================

class MiroFishSignalFusion:
    """
    MiroFish与声纳库信号融合层
    
    融合流程:
    1. 收集声纳库123模型的信号
    2. 获取MiroFish预测结果
    3. 计算综合置信度
    4. 输出融合信号
    """
    
    def __init__(self):
        self.mirofish_threshold = 0.70  # MiroFish验证阈值
        self.sonar_weight = 0.4         # 声纳库权重
        self.mirofish_weight = 0.6      # MiroFish权重
    
    def fuse(self, sonar_signals: Dict, mirofish_predictions: Dict) -> Dict:
        """
        融合信号
        
        Args:
            sonar_signals: {
                "BTC": {"signal": "buy", "confidence": 0.75, "indicators": ["EMA", "RSI"]},
                ...
            }
            mirofish_predictions: {
                "BTC": {"signal": "buy", "confidence": 0.82, "agents": 85},
                ...
            }
        
        Returns:
            fused_signals: {
                "BTC": {
                    "signal": "buy",
                    "confidence": 0.79,
                    "sonar_confidence": 0.75,
                    "mirofish_confidence": 0.82,
                    "approved": True
                },
                ...
            }
        """
        fused = {}
        
        # 获取所有币种
        all_symbols = set(sonar_signals.keys()) | set(mirofish_predictions.keys())
        
        for symbol in all_symbols:
            sonar = sonar_signals.get(symbol, {})
            miro = mirofish_predictions.get(symbol, {})
            
            if not sonar and not miro:
                continue
            
            # 声纳信号
            sonar_signal = sonar.get("signal", "hold")
            sonar_conf = sonar.get("confidence", 0.5)
            
            # MiroFish信号
            miro_signal = miro.get("signal", "hold")
            miro_conf = miro.get("confidence", 0.5)
            
            # 方向一致性检查
            if sonar_signal == miro_signal or sonar_signal == "hold":
                final_signal = miro_signal
            elif miro_signal == "hold":
                final_signal = sonar_signal
            else:
                # 冲突时, 置信度加权
                final_signal = miro_signal if miro_conf > sonar_conf else sonar_signal
            
            # 综合置信度
            if sonar_conf > 0 and miro_conf > 0:
                final_conf = sonar_conf * self.sonar_weight + miro_conf * self.mirofish_weight
            elif miro_conf > 0:
                final_conf = miro_conf
            else:
                final_conf = sonar_conf
            
            # MiroFish验证
            mirofish_verified = miro_conf >= self.mirofish_threshold
            
            fused[symbol] = {
                "symbol": symbol,
                "signal": final_signal,
                "confidence": final_conf,
                "sonar_confidence": sonar_conf,
                "mirofish_confidence": miro_conf,
                "sonar_signal": sonar_signal,
                "mirofish_signal": miro_signal,
                "mirofish_verified": mirofish_verified,
                "approved": final_conf >= 0.70 and mirofish_verified,
                "indicators": sonar.get("indicators", []),
                "agent_count": miro.get("agents", 0)
            }
        
        return fused
    
    def get_trade_signals(self, fused_signals: Dict, min_confidence: float = 0.70) -> List[Dict]:
        """获取可执行的交易信号"""
        signals = []
        
        for symbol, data in fused_signals.items():
            if data["approved"] and data["confidence"] >= min_confidence:
                signals.append({
                    "symbol": symbol,
                    "signal": data["signal"],
                    "confidence": data["confidence"],
                    "reason": f"MiroFish验证({data['mirofish_confidence']:.0%}) + 声纳库({data['sonar_confidence']:.0%})"
                })
        
        # 按置信度排序
        return sorted(signals, key=lambda x: x["confidence"], reverse=True)


# ==================== 完整回测引擎 ====================

class CompleteBacktestEngine:
    """
    完整回测引擎
    - CCXT真实数据
    - 交易成本模拟
    - 信号融合
    - 动态权重
    """
    
    def __init__(self):
        self.exchange = None
        self.cost_simulator = TradingCostSimulator()
        self.weight_optimizer = DynamicWeightOptimizer()
        self.signal_fusion = MiroFishSignalFusion()
        self._init_exchange()
    
    def _init_exchange(self):
        try:
            self.exchange = ccxt.binance({'enableRateLimit': True})
            self.exchange.load_markets()
            print("✅ 交易所已连接")
        except Exception as e:
            print(f"❌ 交易所连接失败: {e}")
    
    async def run_complete_backtest(self, symbols: List[str], 
                                   strategies: List[str]) -> Dict:
        """运行完整回测"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "symbols": symbols,
            "strategies": strategies,
            "trades": [],
            "cost_summary": {},
            "weights": {},
            "fused_signals": {}
        }
        
        # 1. 获取市场数据
        market_data = await self._fetch_market_data(symbols)
        
        # 2. 生成声纳库信号
        sonar_signals = self._generate_sonar_signals(market_data)
        
        # 3. 模拟MiroFish预测
        mirofish_predictions = self._simulate_mirofish(symbols)
        
        # 4. 信号融合
        fused = self.signal_fusion.fuse(sonar_signals, mirofish_predictions)
        results["fused_signals"] = fused
        
        # 5. 执行回测(含成本)
        backtest_results = {}
        for strategy in strategies:
            trades = self._run_strategy_backtest(strategy, market_data)
            results["trades"].extend(trades)
            
            # 计算策略得分
            if trades:
                wins = sum(1 for t in trades if t.pnl_net > 0)
                win_rate = wins / len(trades)
                avg_pnl = sum(t.pnl_net for t in trades) / len(trades)
                score = win_rate * 40 + min(avg_pnl * 1000, 30) + (10 if avg_pnl > 0 else 0)
                backtest_results[strategy] = score
        
        # 6. 更新动态权重
        if backtest_results:
            new_weights = self.weight_optimizer.update_weights(backtest_results)
            results["weights"] = new_weights
        
        # 7. 成本汇总
        if results["trades"]:
            results["cost_summary"] = self.cost_simulator.get_cost_summary(results["trades"])
        
        # 8. 获取交易信号
        trade_signals = self.signal_fusion.get_trade_signals(fused)
        results["trade_signals"] = trade_signals
        
        return results
    
    async def _fetch_market_data(self, symbols: List[str]) -> Dict:
        """获取市场数据"""
        data = {}
        since = int((datetime.now() - timedelta(days=30)).timestamp() * 1000)
        
        for symbol in symbols[:5]:  # 限制数量
            pair = f"{symbol}/USDT"
            try:
                ohlcv = await asyncio.to_thread(
                    self.exchange.fetch_ohlcv, pair, '1h', since=since, limit=500
                )
                data[symbol] = ohlcv
            except Exception as e:
                print(f"获取{symbol}数据失败: {e}")
        
        return data
    
    def _generate_sonar_signals(self, market_data: Dict) -> Dict:
        """生成声纳库信号"""
        signals = {}
        
        for symbol, ohlcv in market_data.items():
            if len(ohlcv) < 50:
                continue
            
            closes = [c[4] for c in ohlcv]
            
            # 简化信号计算
            ema_fast = self._calc_ema(closes, 20)
            ema_slow = self._calc_ema(closes, 50)
            rsi = self._calc_rsi(closes, 14)
            
            # 信号判断
            recent = len(closes) - 1
            signal = "hold"
            confidence = 0.5
            indicators = []
            
            if ema_fast[recent] > ema_slow[recent] and rsi[recent] < 70:
                signal = "buy"
                confidence = 0.75
                indicators = ["EMA金叉", "RSI未超买"]
            elif ema_fast[recent] < ema_slow[recent]:
                signal = "sell"
                confidence = 0.70
                indicators = ["EMA死叉"]
            
            signals[symbol] = {
                "signal": signal,
                "confidence": confidence,
                "indicators": indicators
            }
        
        return signals
    
    def _simulate_mirofish(self, symbols: List[str]) -> Dict:
        """模拟MiroFish预测"""
        predictions = {}
        
        for symbol in symbols[:5]:
            # 简化模拟
            import random
            confidence = 0.70 + random.random() * 0.20
            signals = ["buy", "sell", "hold"]
            signal = random.choice(signals)
            
            predictions[symbol] = {
                "signal": signal,
                "confidence": confidence,
                "agents": random.randint(70, 100)
            }
        
        return predictions
    
    def _run_strategy_backtest(self, strategy: str, market_data: Dict) -> List[BacktestTrade]:
        """运行策略回测(含成本)"""
        trades = []
        
        for symbol, ohlcv in market_data.items():
            if len(ohlcv) < 50:
                continue
            
            closes = [c[4] for c in ohlcv]
            position = None
            
            for i in range(50, len(closes)):
                price = closes[i]
                
                if position is None:
                    # 买入信号
                    if strategy == "ema_cross" and i > 0:
                        ema_f = self._calc_ema(closes[:i+1], 20)[-1]
                        ema_s = self._calc_ema(closes[:i+1], 50)[-1]
                        if ema_f > ema_s:
                            position = {"entry_price": price, "entry_idx": i}
                else:
                    # 卖出条件
                    pnl_pct = (price - position["entry_price"]) / position["entry_price"]
                    
                    if pnl_pct > 0.08 or pnl_pct < -0.05:
                        # 止盈/止损
                        trade = self.cost_simulator.simulate_trade(
                            position["entry_price"], price, "long", 1.0
                        )
                        trade.exit_reason = "take_profit" if pnl_pct > 0 else "stop_loss"
                        trades.append(trade)
                        position = None
        
        return trades
    
    def _calc_ema(self, data: List, period: int) -> List:
        if len(data) < period:
            return [data[0]] * len(data)
        k = 2 / (period + 1)
        ema = [data[0]]
        for i in range(1, len(data)):
            ema.append(data[i] * k + ema[-1] * (1 - k))
        return ema
    
    def _calc_rsi(self, closes: List, period: int = 14) -> List:
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


# ==================== 测试 ====================

if __name__ == "__main__":
    print("=== 完整回测引擎测试 ===")
    
    engine = CompleteBacktestEngine()
    
    # 测试交易成本
    print("\n1. 交易成本模拟:")
    cost_sim = TradingCostSimulator()
    trade = cost_sim.simulate_trade(100, 105, "long", 1.0)
    print(f"   买入100, 卖出105, 数量1.0")
    print(f"   毛利润: {trade.pnl_gross:.2f}")
    print(f"   滑点成本: {trade.slippage_cost:.4f}")
    print(f"   手续费: {trade.fee_cost:.4f}")
    print(f"   总成本: {trade.total_cost:.4f}")
    print(f"   净利润: {trade.pnl_net:.2f}")
    
    # 测试动态权重
    print("\n2. 动态权重:")
    optimizer = DynamicWeightOptimizer()
    results = {"ema_cross": 75, "macd": 55, "rsi": 35}
    new_weights = optimizer.update_weights(results)
    for k, v in new_weights.items():
        print(f"   {k}: {v:.2%}")
    
    # 测试信号融合
    print("\n3. MiroFish信号融合:")
    fusion = MiroFishSignalFusion()
    sonar = {"BTC": {"signal": "buy", "confidence": 0.75, "indicators": ["EMA"]}}
    miro = {"BTC": {"signal": "buy", "confidence": 0.82, "agents": 85}}
    fused = fusion.fuse(sonar, miro)
    print(f"   BTC融合信号: {fused['BTC']['signal']}")
    print(f"   置信度: {fused['BTC']['confidence']:.0%}")
    print(f"   MiroFish验证: {fused['BTC']['mirofish_verified']}")
    print(f"   批准执行: {fused['BTC']['approved']}")
