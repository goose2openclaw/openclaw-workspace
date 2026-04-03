#!/usr/bin/env python3
"""
🪿 回测引擎 - 历史行情模拟交易
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger("go2se")


@dataclass
class BacktestTrade:
    """回测交易"""
    index: int
    timestamp: str
    symbol: str
    side: str  # buy/sell
    price: float
    amount: float
    pnl: float = 0
    cumulative_capital: float = 0


@dataclass
class BacktestConfig:
    """回测配置"""
    symbol: str = "BTC/USDT"
    start_date: str = ""  # YYYY-MM-DD
    end_date: str = ""    # YYYY-MM-DD
    initial_capital: float = 10000.0
    stop_loss: float = 0.05   # 5%
    take_profit: float = 0.15  # 15%
    position_size: float = 0.1  # 每次用10%仓位
    strategy: str = "rsi_macross"  # 策略名称


class BacktestEngine:
    """回测引擎"""

    def __init__(self, exchange):
        self.exchange = exchange

    async def run(self, config: BacktestConfig) -> Dict:
        """执行回测"""
        logger.info(f"🧪 回测开始: {config.symbol} {config.start_date} → {config.end_date}")
        
        # 获取历史数据
        ohlcv_data = await self._fetch_historical(config)
        if not ohlcv_data:
            return {"error": "无法获取历史数据"}

        # 运行策略
        signals = self._generate_signals(ohlcv_data, config.strategy)
        
        # 模拟交易
        trades, equity = self._simulate_trades(ohlcv_data, signals, config)
        
        # 计算统计
        stats = self._calculate_stats(trades, equity, config.initial_capital)
        
        logger.info(f"🧪 回测完成: 总交易={stats['total_trades']}, 胜率={stats['win_rate']:.1f}%, 收益={stats['total_return']:.2f}%")
        
        return {
            **stats,
            "symbol": config.symbol,
            "start_date": config.start_date,
            "end_date": config.end_date,
            "initial_capital": config.initial_capital,
            "trades": trades[-20:],  # 最近20笔
            "equity_curve": equity[-30:],  # 最近30个时间点
        }

    async def _fetch_historical(self, config: BacktestConfig) -> List:
        """获取历史K线数据"""
        try:
            since = int(datetime.strptime(config.start_date, "%Y-%m-%d").timestamp() * 1000)
            limit = 200
            ohlcv = await asyncio.to_thread(
                self.exchange.fetch_ohlcv,
                config.symbol,
                '1h',
                since=since,
                limit=limit
            )
            return ohlcv
        except Exception as e:
            logger.error(f"获取历史数据失败: {e}")
            return []

    def _generate_signals(self, ohlcv: List, strategy: str) -> List[Dict]:
        """生成交易信号"""
        if strategy == "rsi_macross":
            return self._rsi_macross(ohlcv)
        elif strategy == "rsi_extreme":
            return self._rsi_extreme(ohlcv)
        elif strategy == "macd_cross":
            return self._macd_cross(ohlcv)
        else:
            return self._rsi_macross(ohlcv)

    def _rsi_macross(self, ohlcv: List) -> List[Dict]:
        """RSI + 移动均线的简单策略"""
        closes = [c[4] for c in ohlcv]
        signals = []
        
        # 计算RSI
        rsi = self._calc_rsi(closes, 14)
        
        # 计算短期/长期均线
        ma_fast = self._calc_ma(closes, 10)
        ma_slow = self._calc_ma(closes, 30)
        
        for i in range(30, len(closes)):
            signal = "hold"
            reason = ""
            
            # 金叉买入，死叉卖出
            if i > 0 and ma_fast[i] > ma_slow[i] and ma_fast[i-1] <= ma_slow[i-1] and rsi[i] < 70:
                signal = "buy"
                reason = f"MA金叉 RSI={rsi[i]:.1f}"
            elif i > 0 and ma_fast[i] < ma_slow[i] and ma_fast[i-1] >= ma_slow[i-1]:
                signal = "sell"
                reason = f"MA死叉 RSI={rsi[i]:.1f}"
            
            signals.append({
                "index": i,
                "timestamp": ohlcv[i][0] // 1000,
                "price": closes[i],
                "signal": signal,
                "reason": reason,
                "rsi": rsi[i] if i < len(rsi) else 50
            })
        return signals

    def _rsi_extreme(self, ohlcv: List) -> List[Dict]:
        """RSI极端值策略"""
        closes = [c[4] for c in ohlcv]
        rsi = self._calc_rsi(closes, 14)
        signals = []
        
        for i in range(14, len(closes)):
            signal = "hold"
            reason = ""
            
            if rsi[i] < 30:
                signal = "buy"
                reason = f"RSI超卖={rsi[i]:.1f}"
            elif rsi[i] > 70:
                signal = "sell"
                reason = f"RSI超买={rsi[i]:.1f}"
            
            signals.append({
                "index": i,
                "timestamp": ohlcv[i][0] // 1000,
                "price": closes[i],
                "signal": signal,
                "reason": reason,
                "rsi": rsi[i]
            })
        return signals

    def _macd_cross(self, ohlcv: List) -> List[Dict]:
        """MACD金叉死叉策略"""
        closes = [c[4] for c in ohlcv]
        macd, signal = self._calc_macd(closes)
        signals = []
        
        for i in range(30, len(closes)):
            signal_type = "hold"
            reason = ""
            
            if i > 0 and macd[i] > signal[i] and macd[i-1] <= signal[i-1]:
                signal_type = "buy"
                reason = "MACD金叉"
            elif i > 0 and macd[i] < signal[i] and macd[i-1] >= signal[i-1]:
                signal_type = "sell"
                reason = "MACD死叉"
            
            signals.append({
                "index": i,
                "timestamp": ohlcv[i][0] // 1000,
                "price": closes[i],
                "signal": signal_type,
                "reason": reason,
            })
        return signals

    def _simulate_trades(self, ohlcv: List, signals: List, config: BacktestConfig) -> tuple[List[BacktestTrade], List[Dict]]:
        """模拟交易"""
        closes = [c[4] for c in ohlcv]
        capital = config.initial_capital
        position = 0.0  # 持仓数量
        entry_price = 0.0
        trades = []
        equity = []
        trade_count = 0

        # 索引映射: signal.index → ohlcv index
        signal_map = {s["index"]: s for s in signals}
        
        for i in range(len(ohlcv)):
            price = closes[i]
            ts = ohlcv[i][0] // 1000
            
            # 记录资金曲线
            position_value = position * price
            total = capital + position_value
            equity.append({"t": ts, "v": round(total, 2)})
            
            if i not in signal_map:
                continue
            
            sig = signal_map[i]
            
            if sig["signal"] == "buy" and position == 0:
                # 买入
                amount = (capital * config.position_size) / price
                fee = amount * price * 0.001
                position = amount
                capital -= (amount * price + fee)
                entry_price = price
                trade_count += 1
                trades.append({
                    "index": trade_count,
                    "t": ts,
                    "side": "buy",
                    "price": price,
                    "amount": round(amount, 6),
                    "pnl": 0,
                    "reason": sig["reason"],
                    "equity": round(capital + position * price, 2)
                })
                
            elif sig["signal"] == "sell" and position > 0:
                # 卖出 (止损/止盈/跟踪)
                pnl_pct = (price - entry_price) / entry_price
                should_sell = False
                
                if pnl_pct <= -config.stop_loss:
                    should_sell = True
                    sig["reason"] += " [SL]"
                elif pnl_pct >= config.take_profit:
                    should_sell = True
                    sig["reason"] += " [TP]"
                elif sig["reason"] == "MA死叉":
                    should_sell = True
                
                if should_sell:
                    proceeds = position * price
                    fee = proceeds * 0.001
                    pnl = proceeds - (position * entry_price) - fee
                    capital += proceeds - fee
                    trades.append({
                        "index": trade_count,
                        "t": ts,
                        "side": "sell",
                        "price": price,
                        "amount": round(position, 6),
                        "pnl": round(pnl, 2),
                        "reason": sig["reason"],
                        "equity": round(capital, 2)
                    })
                    position = 0
                    entry_price = 0

        # 平仓
        if position > 0:
            price = closes[-1]
            proceeds = position * price
            fee = proceeds * 0.001
            pnl = proceeds - (position * entry_price) - fee
            capital += proceeds - fee
            trade_count += 1
            trades.append({
                "index": trade_count,
                "t": ohlcv[-1][0] // 1000,
                "side": "sell",
                "price": price,
                "amount": round(position, 6),
                "pnl": round(pnl, 2),
                "reason": "回测结束平仓",
                "equity": round(capital, 2)
            })

        return trades, equity

    def _calculate_stats(self, trades: List[Dict], equity: List[Dict], initial: float) -> Dict:
        """计算回测统计"""
        if not trades:
            return {
                "total_trades": 0, "win_trades": 0, "lose_trades": 0,
                "win_rate": 0, "total_return": 0, "max_drawdown": 0,
                "sharpe_ratio": 0, "final_capital": initial
            }
        
        sells = [t for t in trades if t["side"] == "sell"]
        wins = [t for t in sells if t["pnl"] > 0]
        losses = [t for t in sells if t["pnl"] <= 0]
        
        final_capital = equity[-1]["v"] if equity else initial
        total_return = (final_capital - initial) / initial * 100
        
        # 最大回撤
        peak = initial
        max_dd = 0
        for e in equity:
            if e["v"] > peak:
                peak = e["v"]
            dd = (peak - e["v"]) / peak * 100
            if dd > max_dd:
                max_dd = dd
        
        # 夏普比率简化版 (用日收益标准差)
        returns = []
        for i in range(1, len(equity)):
            r = (equity[i]["v"] - equity[i-1]["v"]) / equity[i-1]["v"]
            returns.append(r)
        if returns:
            import statistics
            mean_r = statistics.mean(returns) * 24  # 日化
            std_r = statistics.stdev(returns) * (24 ** 0.5) if len(returns) > 1 else 0
            sharpe = (mean_r / std_r) if std_r > 0 else 0
        else:
            sharpe = 0

        return {
            "total_trades": len(sells),
            "win_trades": len(wins),
            "lose_trades": len(losses),
            "win_rate": round(len(wins) / len(sells) * 100, 1) if sells else 0,
            "total_return": round(total_return, 2),
            "final_capital": round(final_capital, 2),
            "max_drawdown": round(max_dd, 2),
            "sharpe_ratio": round(sharpe, 2),
        }

    @staticmethod
    def _calc_rsi(closes: List[float], period: int = 14) -> List[float]:
        if len(closes) < period + 1:
            return [50.0] * len(closes)
        deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        rsi = [50.0] * period
        for i in range(period, len(deltas)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            rs = avg_gain / avg_loss if avg_loss > 0 else 0
            rsi.append(100 - 100 / (1 + rs))
        return rsi

    @staticmethod
    def _calc_ma(closes: List[float], period: int) -> List[float]:
        result = []
        for i in range(len(closes)):
            if i < period - 1:
                result.append(sum(closes[:i+1]) / (i+1))
            else:
                result.append(sum(closes[i-period+1:i+1]) / period)
        return result

    @staticmethod
    def _calc_macd(closes: List[float], fast: int = 12, slow: int = 26, signal: int = 9):
        ema_fast = BacktestEngine._calc_ema(closes, fast)
        ema_slow = BacktestEngine._calc_ema(closes, slow)
        macd = [f - s for f, s in zip(ema_fast, ema_slow)]
        signal_line = BacktestEngine._calc_ema(macd, signal)
        return macd, signal_line

    @staticmethod
    def _calc_ema(closes: List[float], period: int) -> List[float]:
        k = 2 / (period + 1)
        ema = [closes[0]]
        for i in range(1, len(closes)):
            ema.append(closes[i] * k + ema[-1] * (1 - k))
        return ema
