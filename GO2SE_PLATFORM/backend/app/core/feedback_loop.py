"""
回测 → 评估 → 迭代 闭环系统

P0修复核心: 建立持续优化的闭环
"""

import asyncio
import ccxt
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
import json

@dataclass
class BacktestResult:
    """回测结果"""
    strategy_id: str
    symbol: str
    period: str
    total_trades: int
    win_rate: float
    avg_pnl: float
    max_drawdown: float
    sharpe_ratio: float
    timestamp: str

@dataclass
class EvaluationResult:
    """评估结果"""
    strategy_id: str
    score: float  # 0-100
    grade: str    # A/B/C/D
    verdict: str   # keep/upgrade/deprecate
    reasons: List[str]
    suggestions: List[str]

class FeedbackLoop:
    """
    回测 → 评估 → 迭代 闭环
    
    流程:
    1. 回测: 使用CCXT真实数据验证策略
    2. 评估: 计算策略得分,决定保留/升级/淘汰
    3. 迭代: 自动更新策略参数或触发新策略
    """
    
    def __init__(self):
        self.exchange = None
        self.evaluation_thresholds = {
            "A": 80,  # score >= 80 → keep + promote
            "B": 60,  # score >= 60 → keep
            "C": 40,  # score >= 40 → upgrade
            "D": 0    # score < 40 → deprecate
        }
        self._init_exchange()
    
    def _init_exchange(self):
        """初始化交易所连接"""
        try:
            self.exchange = ccxt.binance({'enableRateLimit': True})
            self.exchange.load_markets()
            print(f"✅ 交易所已连接: Binance")
        except Exception as e:
            print(f"❌ 交易所连接失败: {e}")
    
    # ==================== 1. 回测 ====================
    
    async def run_backtest(self, strategy_id: str, symbol: str, 
                          days: int = 90) -> BacktestResult:
        """运行回测"""
        if not self.exchange:
            return None
        
        pair = f"{symbol}/USDT"
        since = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
        
        try:
            ohlcv = await asyncio.to_thread(
                self.exchange.fetch_ohlcv,
                pair, '1h', since=since, limit=500
            )
            
            if len(ohlcv) < 100:
                return None
            
            # 根据策略ID运行不同回测
            if strategy_id == "ema_cross":
                trades = self._backtest_ema_cross(ohlcv)
            elif strategy_id == "macd":
                trades = self._backtest_macd(ohlcv)
            elif strategy_id == "rsi_extreme":
                trades = self._backtest_rsi_extreme(ohlcv)
            elif strategy_id == "bb_meanreversion":
                trades = self._backtest_bb(ohlcv)
            else:
                trades = self._backtest_ema_cross(ohlcv)
            
            # 计算统计
            total_trades = len(trades)
            if total_trades == 0:
                return BacktestResult(
                    strategy_id=strategy_id,
                    symbol=symbol,
                    period=f"{days}d",
                    total_trades=0,
                    win_rate=0,
                    avg_pnl=0,
                    max_drawdown=0,
                    sharpe_ratio=0,
                    timestamp=datetime.now().isoformat()
                )
            
            wins = sum(1 for t in trades if t['pnl'] > 0)
            win_rate = wins / total_trades
            avg_pnl = sum(t['pnl'] for t in trades) / total_trades
            
            # 计算最大回撤
            cumulative = [1.0]
            for t in trades:
                cumulative.append(cumulative[-1] * (1 + t['pnl']))
            
            peak = cumulative[0]
            max_dd = 0
            for c in cumulative:
                if c > peak:
                    peak = c
                dd = (peak - c) / peak
                if dd > max_dd:
                    max_dd = dd
            
            # 简化夏普比率
            if avg_pnl > 0 and total_trades > 1:
                returns = [t['pnl'] for t in trades]
                avg_ret = sum(returns) / len(returns)
                std_ret = (sum((r - avg_ret)**2 for r in returns) / len(returns)) ** 0.5
                sharpe = avg_ret / std_ret * (252 ** 0.5) if std_ret > 0 else 0
            else:
                sharpe = 0
            
            return BacktestResult(
                strategy_id=strategy_id,
                symbol=symbol,
                period=f"{days}d",
                total_trades=total_trades,
                win_rate=win_rate,
                avg_pnl=avg_pnl,
                max_drawdown=max_dd,
                sharpe_ratio=sharpe,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            print(f"回测失败 {strategy_id} {symbol}: {e}")
            return None
    
    def _backtest_ema_cross(self, ohlcv: List) -> List[Dict]:
        """EMA交叉策略回测"""
        closes = [c[4] for c in ohlcv]
        ema20 = self._calc_ema(closes, 20)
        ema50 = self._calc_ema(closes, 50)
        
        trades = []
        position = None
        
        for i in range(50, len(closes)):
            if ema20[i] > ema50[i] and ema20[i-1] <= ema50[i-1] and position is None:
                position = {"entry_price": closes[i]}
            elif ema20[i] < ema50[i] and position is not None:
                pnl = (closes[i] - position["entry_price"]) / position["entry_price"]
                trades.append({"pnl": pnl})
                position = None
        
        return trades
    
    def _backtest_macd(self, ohlcv: List) -> List[Dict]:
        """MACD策略回测"""
        closes = [c[4] for c in ohlcv]
        macd, signal = self._calc_macd(closes)
        
        trades = []
        position = None
        
        for i in range(26, len(closes)):
            if macd[i] > signal[i] and macd[i-1] <= signal[i-1] and position is None:
                position = {"entry_price": closes[i]}
            elif macd[i] < signal[i] and position is not None:
                pnl = (closes[i] - position["entry_price"]) / position["entry_price"]
                trades.append({"pnl": pnl})
                position = None
        
        return trades
    
    def _backtest_rsi_extreme(self, ohlcv: List) -> List[Dict]:
        """RSI极端值策略回测"""
        closes = [c[4] for c in ohlcv]
        if len(closes) < 15:
            return []
        
        rsi = self._calc_rsi(closes, 14)
        if len(rsi) < 15:
            return []
        
        trades = []
        position = None
        
        for i in range(14, len(closes)):
            if i >= len(rsi):
                break
            try:
                if rsi[i] < 30 and position is None:
                    position = {"entry_price": closes[i]}
                elif rsi[i] > 70 and position is not None:
                    pnl = (closes[i] - position["entry_price"]) / position["entry_price"]
                    trades.append({"pnl": pnl})
                    position = None
            except (IndexError, KeyError):
                continue
        
        return trades
    
    def _backtest_bb(self, ohlcv: List) -> List[Dict]:
        """布林带策略回测"""
        closes = [c[4] for c in ohlcv]
        bb_upper, bb_lower, _ = self._calc_bollinger(closes, 20, 2)
        
        trades = []
        position = None
        
        for i in range(20, len(closes)):
            if closes[i] < bb_lower[i] and position is None:
                position = {"entry_price": closes[i]}
            elif closes[i] > bb_upper[i] and position is not None:
                pnl = (closes[i] - position["entry_price"]) / position["entry_price"]
                trades.append({"pnl": pnl})
                position = None
        
        return trades
    
    # ==================== 2. 评估 ====================
    
    def evaluate(self, result: BacktestResult) -> EvaluationResult:
        """评估回测结果"""
        if result is None or result.total_trades == 0:
            return EvaluationResult(
                strategy_id=strategy_id,
                score=0,
                grade="D",
                verdict="deprecate",
                reasons=["无交易数据"],
                suggestions=["检查策略逻辑"]
            )
        
        strategy_id = result.strategy_id
        
        # 计算综合得分 (0-100)
        score = 0
        reasons = []
        suggestions = []
        
        # 胜率得分 (40分)
        win_rate_score = result.win_rate * 40
        score += win_rate_score
        if result.win_rate >= 0.70:
            reasons.append(f"胜率优秀: {result.win_rate:.1%}")
        elif result.win_rate < 0.50:
            reasons.append(f"胜率不足: {result.win_rate:.1%}")
            suggestions.append("优化入场信号")
        
        # 平均收益得分 (30分)
        avg_pnl_score = min(30, result.avg_pnl * 1000)
        score += avg_pnl_score
        if result.avg_pnl > 0.02:
            reasons.append(f"平均收益良好: {result.avg_pnl:.2%}")
        
        # 夏普比率得分 (20分)
        sharpe_score = min(20, max(0, result.sharpe_ratio * 10))
        score += sharpe_score
        if result.sharpe_ratio >= 1.5:
            reasons.append(f"夏普优秀: {result.sharpe_ratio:.2f}")
        
        # 回撤得分 (10分)
        drawdown_score = max(0, 10 - result.max_drawdown * 100)
        score += drawdown_score
        if result.max_drawdown > 0.15:
            reasons.append(f"回撤过大: {result.max_drawdown:.1%}")
            suggestions.append("加强止损")
        elif result.max_drawdown < 0.05:
            reasons.append(f"回撤可控: {result.max_drawdown:.1%}")
        
        # 交易频率调整
        if result.total_trades < 10:
            suggestions.append("交易次数不足,统计可能不稳定")
        
        # 评分等级
        if score >= 80:
            grade = "A"
            verdict = "keep_promote"
        elif score >= 60:
            grade = "B"
            verdict = "keep"
        elif score >= 40:
            grade = "C"
            verdict = "upgrade"
        else:
            grade = "D"
            verdict = "deprecate"
        
        return EvaluationResult(
            strategy_id=strategy_id,
            score=score,
            grade=grade,
            verdict=verdict,
            reasons=reasons,
            suggestions=suggestions
        )
    
    # ==================== 3. 迭代 ====================
    
    async def iterate(self, evaluation: EvaluationResult, 
                     current_config: Dict) -> Dict:
        """根据评估结果迭代策略"""
        
        if evaluation.verdict == "keep_promote":
            # 增加仓位权重
            new_config = current_config.copy()
            new_config["allocation"] = min(30, current_config.get("allocation", 20) * 1.1)
            action = "promote"
            
        elif evaluation.verdict == "keep":
            # 保持不变
            new_config = current_config
            action = "keep"
            
        elif evaluation.verdict == "upgrade":
            # 调整参数
            new_config = current_config.copy()
            # 可以调整止损/止盈参数
            new_config["stop_loss"] = min(10, current_config.get("stop_loss", 5) * 1.1)
            new_config["take_profit"] = max(5, current_config.get("take_profit", 8) * 0.9)
            action = "upgrade"
            
        else:  # deprecate
            # 降低权重或禁用
            new_config = current_config.copy()
            new_config["allocation"] = current_config.get("allocation", 20) * 0.5
            new_config["enabled"] = False
            action = "deprecate"
        
        return {
            "action": action,
            "strategy_id": evaluation.strategy_id,
            "old_config": current_config,
            "new_config": new_config,
            "score_change": f"{evaluation.score:.1f} ({evaluation.grade})"
        }
    
    # ==================== 完整闭环 ====================
    
    async def run_full_loop(self, strategy_configs: Dict) -> Dict:
        """
        运行完整闭环: 回测 → 评估 → 迭代
        
        Args:
            strategy_configs: 策略配置 {
                "ema_cross": {"allocation": 25, "enabled": True, ...},
                ...
            }
        
        Returns:
            {
                "backtest_results": [...],
                "evaluations": [...],
                "iterations": [...],
                "updated_configs": {...}
            }
        """
        symbols = ["BTC", "ETH", "BNB", "SOL", "XRP"]
        results = {
            "backtest_results": [],
            "evaluations": [],
            "iterations": [],
            "updated_configs": strategy_configs.copy()
        }
        
        print("\n" + "="*60)
        print("🔄 回测 → 评估 → 迭代 闭环系统")
        print("="*60)
        
        for strategy_id in strategy_configs.keys():
            if not strategy_configs[strategy_id].get("enabled", True):
                continue
            
            print(f"\n📊 策略: {strategy_id}")
            
            # 1. 回测
            print(f"  🧪 回测中...")
            bt_result = await self.run_backtest(strategy_id, "BTC", days=90)
            
            if bt_result:
                results["backtest_results"].append({
                    "strategy_id": strategy_id,
                    **bt_result.__dict__
                })
                print(f"     交易次数: {bt_result.total_trades}")
                print(f"     胜率: {bt_result.win_rate:.1%}")
                print(f"     夏普: {bt_result.sharpe_ratio:.2f}")
                print(f"     回撤: {bt_result.max_drawdown:.1%}")
            else:
                print(f"     ❌ 回测失败")
                continue
            
            # 2. 评估
            print(f"  📈 评估中...")
            eval_result = self.evaluate(bt_result)
            results["evaluations"].append(eval_result.__dict__)
            print(f"     得分: {eval_result.score:.1f} ({eval_result.grade})")
            print(f"     结论: {eval_result.verdict}")
            
            # 3. 迭代
            print(f"  🔄 迭代中...")
            iteration = await self.iterate(eval_result, strategy_configs[strategy_id])
            results["iterations"].append(iteration)
            results["updated_configs"][strategy_id] = iteration["new_config"]
            print(f"     操作: {iteration['action']}")
        
        print("\n" + "="*60)
        print("✅ 闭环完成")
        print("="*60)
        
        return results
    
    # ==================== 工具函数 ====================
    
    def _calc_ema(self, data: List, period: int) -> List:
        if len(data) < period:
            return [50] * len(data)
        k = 2 / (period + 1)
        ema = [data[0]]
        for i in range(1, len(data)):
            ema.append(data[i] * k + ema[-1] * (1 - k))
        return ema
    
    def _calc_macd(self, closes: List, fast: int = 12, slow: int = 26, signal: int = 9):
        ema_fast = self._calc_ema(closes, fast)
        ema_slow = self._calc_ema(closes, slow)
        macd = [ema_fast[i] - ema_slow[i] for i in range(len(closes))]
        signal_line = self._calc_ema(macd, signal)
        return macd, signal_line
    
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
    
    def _calc_bollinger(self, closes: List, period: int = 20, std_dev: int = 2):
        if len(closes) < period:
            return closes, closes, closes
        bb_upper, bb_lower, bb_middle = [], [], []
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


# ==================== 独立运行 ====================

if __name__ == "__main__":
    async def main():
        loop = FeedbackLoop()
        
        # 测试策略配置
        test_configs = {
            "ema_cross": {"allocation": 25, "enabled": True, "stop_loss": 5, "take_profit": 8},
            "macd": {"allocation": 20, "enabled": True, "stop_loss": 5, "take_profit": 8},
            "rsi_extreme": {"allocation": 15, "enabled": True, "stop_loss": 5, "take_profit": 8},
            "bb_meanreversion": {"allocation": 10, "enabled": True, "stop_loss": 5, "take_profit": 8},
        }
        
        # 运行完整闭环
        results = await loop.run_full_loop(test_configs)
        
        print("\n📋 更新后的配置:")
        for sid, config in results["updated_configs"].items():
            alloc = config.get("allocation", "N/A")
            enabled = config.get("enabled", True)
            print(f"  {sid}: allocation={alloc}, enabled={enabled}")
    
    asyncio.run(main())
