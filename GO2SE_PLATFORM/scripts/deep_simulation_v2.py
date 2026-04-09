#!/usr/bin/env python3
"""
🪿 GO2SE 深度仿真 V2 - 修复数据获取 + 超卖反弹策略
自动获取完整历史数据 + 多轮迭代优化
"""

import asyncio
import json
import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict
import logging

sys.path.insert(0, '/root/.openclaw/workspace/GO2SE_PLATFORM/backend')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("deep_sim_v2")

# ─── 优化后的参数搜索空间 ────────────────────────────────────────
PARAM_GRID = {
    # 超卖反弹策略参数 (RSI极端值)
    "oversold_rsi": [20, 25, 30, 35],
    "overbought_rsi": [65, 70, 75, 80],
    # 仓位管理
    "position_size": [0.05, 0.10, 0.15],
    "stop_loss": [0.02, 0.03, 0.05],
    "take_profit": [0.03, 0.05, 0.08, 0.10],
}

SYMBOLS = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
INITIAL_CAPITAL = 10000.0


class FixedBacktestEngine:
    """修复版回测引擎 - 获取完整历史数据"""

    def __init__(self, exchange):
        self.exchange = exchange

    async def fetch_full_history(self, symbol: str, days: int = 90) -> List:
        """获取完整历史K线数据 (迭代获取)"""
        all_ohlcv = []
        timeframe = '1h'
        limit = 500  # 每次获取500根
        
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        since = int(start_time.timestamp() * 1000)
        
        try:
            while True:
                ohlcv = await asyncio.to_thread(
                    self.exchange.fetch_ohlcv,
                    symbol,
                    timeframe,
                    since=since,
                    limit=limit
                )
                if not ohlcv or len(ohlcv) == 0:
                    break
                    
                all_ohlcv.extend(ohlcv)
                since = ohlcv[-1][0] + 3600000  # 下一根K线
                
                if len(ohlcv) < limit:
                    break
                    
                if len(all_ohlcv) > 5000:  # 最多5000根 (约208天)
                    break
                    
        except Exception as e:
            logger.error(f"获取历史数据失败: {e}")
            
        logger.info(f"  📊 {symbol} 获取了 {len(all_ohlcv)} 根K线数据")
        return all_ohlcv

    def calc_rsi(self, closes: List[float], period: int = 14) -> List[float]:
        """计算RSI"""
        if len(closes) < period + 1:
            return [50.0] * len(closes)
        
        deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        
        rsi = [50.0] * period
        
        for i in range(period, len(closes)):
            avg_gain = (avg_gain * (period - 1) + gains[i-1]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i-1]) / period
            
            if avg_loss == 0:
                rsi.append(100.0)
            else:
                rs = avg_gain / avg_loss
                rsi.append(100 - (100 / (1 + rs)))
                
        return rsi

    def calc_ma(self, closes: List[float], period: int) -> List[float]:
        """计算移动均线"""
        ma = []
        for i in range(len(closes)):
            if i < period - 1:
                ma.append(sum(closes[:i+1]) / (i+1))
            else:
                ma.append(sum(closes[i-period+1:i+1]) / period)
        return ma

    def calc_bollinger(self, closes: List[float], period: int = 20, std_dev: float = 2.0):
        """计算布林带"""
        ma = self.calc_ma(closes, period)
        upper, lower = [], []
        for i in range(len(closes)):
            if i < period - 1:
                upper.append(ma[i])
                lower.append(ma[i])
            else:
                slice_data = closes[i-period+1:i+1]
                std = (sum((x - ma[i])**2 for x in slice_data) / period) ** 0.5
                upper.append(ma[i] + std_dev * std)
                lower.append(ma[i] - std_dev * std)
        return upper, lower

    def oversold_rebound_strategy(
        self, ohlcv: List, oversold: int, overbought: int,
        stop_loss: float, take_profit: float, position_size: float
    ) -> List[Dict]:
        """超卖反弹策略"""
        closes = [c[4] for c in ohlcv]
        timestamps = [c[0] / 1000 for c in ohlcv]
        rsi = self.calc_rsi(closes, 14)
        
        trades = []
        position = None
        entry_price = 0
        
        for i in range(30, len(closes)):
            current_price = closes[i]
            ts = datetime.fromtimestamp(timestamps[i]).strftime('%Y-%m-%d %H:%M')
            
            if position is None:
                # 买入信号: RSI超卖
                if rsi[i] < oversold:
                    position = {
                        "side": "buy",
                        "entry_price": current_price,
                        "entry_time": ts,
                        "stop_loss": current_price * (1 - stop_loss),
                        "take_profit": current_price * (1 + take_profit),
                        "amount": (INITIAL_CAPITAL * position_size) / current_price,
                    }
            else:
                # 检查止损
                if current_price <= position["stop_loss"]:
                    pnl = (position["stop_loss"] - position["entry_price"]) * position["amount"]
                    trades.append({
                        "timestamp": ts,
                        "side": "sell",
                        "price": position["stop_loss"],
                        "pnl": pnl,
                        "reason": "stop_loss"
                    })
                    position = None
                # 检查止盈
                elif current_price >= position["take_profit"]:
                    pnl = (position["take_profit"] - position["entry_price"]) * position["amount"]
                    trades.append({
                        "timestamp": ts,
                        "side": "sell",
                        "price": position["take_profit"],
                        "pnl": pnl,
                        "reason": "take_profit"
                    })
                    position = None
                # 检查RSI超买 (主动退出)
                elif rsi[i] > overbought:
                    pnl = (current_price - position["entry_price"]) * position["amount"]
                    trades.append({
                        "timestamp": ts,
                        "side": "sell",
                        "price": current_price,
                        "pnl": pnl,
                        "reason": "overbought_exit"
                    })
                    position = None
        
        return trades

    def calculate_stats(self, trades: List[Dict], initial_capital: float) -> Dict:
        """计算回测统计"""
        if not trades:
            return {
                "total_trades": 0,
                "win_rate": 0,
                "total_return": 0,
                "max_drawdown": 0,
                "sharpe_ratio": 0,
            }
        
        pnls = [t["pnl"] for t in trades]
        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p <= 0]
        
        total_pnl = sum(pnls)
        total_return = (total_pnl / initial_capital) * 100
        
        win_rate = (len(wins) / len(pnls)) * 100 if pnls else 0
        
        # 计算最大回撤
        cumulative = 0
        peak = 0
        max_drawdown = 0
        for pnl in pnls:
            cumulative += pnl
            if cumulative > peak:
                peak = cumulative
            drawdown = (peak - cumulative) / initial_capital * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        # 夏普比率 (简化版)
        if len(pnls) > 1:
            import statistics
            mean_pnl = statistics.mean(pnls)
            std_pnl = statistics.stdev(pnls) if len(pnls) > 1 else 0
            sharpe = (mean_pnl / std_pnl) * (252 ** 0.5) if std_pnl > 0 else 0
        else:
            sharpe = 0
            
        return {
            "total_trades": len(trades),
            "win_rate": win_rate,
            "total_return": total_return,
            "max_drawdown": max_drawdown,
            "sharpe_ratio": sharpe,
            "wins": len(wins),
            "losses": len(losses),
        }


async def run_optimization():
    """运行优化"""
    logger.info("=" * 60)
    logger.info("🪿 GO2SE 深度仿真 V2 - 超卖反弹策略优化")
    logger.info("=" * 60)
    
    from app.core.trading_engine import engine
    engine.init_exchange()
    exchange = engine.exchange
    
    if exchange is None:
        logger.error("交易所未初始化")
        return
    
    bt = FixedBacktestEngine(exchange)
    
    # 先获取历史数据
    logger.info("📊 获取市场历史数据...")
    ohlcv_data = {}
    for symbol in SYMBOLS:
        data = await bt.fetch_full_history(symbol, days=90)
        if data:
            ohlcv_data[symbol] = data
    
    if not ohlcv_data:
        logger.error("无法获取市场数据")
        return
    
    # 网格搜索
    all_results = []
    total = (
        len(PARAM_GRID["oversold_rsi"])
        * len(PARAM_GRID["overbought_rsi"])
        * len(PARAM_GRID["stop_loss"])
        * len(PARAM_GRID["take_profit"])
        * len(PARAM_GRID["position_size"])
    )
    
    count = 0
    logger.info(f"🔬 开始网格搜索: {total} 种组合 × {len(ohlcv_data)} 币种")
    
    for oversold in PARAM_GRID["oversold_rsi"]:
        for overbought in PARAM_GRID["overbought_rsi"]:
            for sl in PARAM_GRID["stop_loss"]:
                for tp in PARAM_GRID["take_profit"]:
                    for ps in PARAM_GRID["position_size"]:
                        for symbol, ohlcv in ohlcv_data.items():
                            count += 1
                            try:
                                trades = bt.oversold_rebound_strategy(
                                    ohlcv, oversold, overbought, sl, tp, ps
                                )
                                stats = bt.calculate_stats(trades, INITIAL_CAPITAL)
                                
                                result = {
                                    **stats,
                                    "oversold_rsi": oversold,
                                    "overbought_rsi": overbought,
                                    "stop_loss": sl,
                                    "take_profit": tp,
                                    "position_size": ps,
                                    "symbol": symbol,
                                    "params_hash": f"{oversold}_{overbought}_{sl}_{tp}_{ps}_{symbol}",
                                }
                                all_results.append(result)
                                
                                if stats["total_trades"] > 0:
                                    logger.info(
                                        f"  [{count}/{total*3:.0f}] {symbol} "
                                        f"OS={oversold} OB={overbought} "
                                        f"SL={sl:.0%} TP={tp:.0%} PS={ps:.0%} "
                                        f"→ Trades={stats['total_trades']} "
                                        f"WinRate={stats['win_rate']:.0f}% "
                                        f"Return={stats['total_return']:.2f}% "
                                        f"MDD={stats['max_drawdown']:.2f}%"
                                    )
                            except Exception as e:
                                logger.error(f"  [{count}] ERROR: {e}")
    
    # 分析结果
    if not all_results:
        logger.error("无有效结果")
        return
    
    # 按综合评分排序
    for r in all_results:
        score = (
            max(0, r["total_return"]) * 0.4
            + r["win_rate"] * 0.2
            + max(0, 20 - r["max_drawdown"]) * 0.2
            + r["total_trades"] * 0.2
        )
        r["composite_score"] = score
    
    ranked = sorted(all_results, key=lambda x: x["composite_score"], reverse=True)
    
    # 打印报告
    logger.info("\n" + "=" * 60)
    logger.info("📊 仿真分析报告")
    logger.info("=" * 60)
    
    trades_count = sum(1 for r in all_results if r["total_trades"] > 0)
    logger.info(f"  总仿真次数: {len(all_results)}")
    logger.info(f"  有交易组合: {trades_count} ({trades_count/len(all_results)*100:.1f}%)")
    
    profitable = [r for r in all_results if r["total_return"] > 0]
    logger.info(f"  正收益组合: {len(profitable)} ({len(profitable)/len(all_results)*100:.1f}%)")
    
    if all_results:
        avg_return = sum(r["total_return"] for r in all_results) / len(all_results)
        avg_winrate = sum(r["win_rate"] for r in all_results if r["total_trades"] > 0) / max(1, trades_count)
        avg_mdd = sum(r["max_drawdown"] for r in all_results) / len(all_results)
        logger.info(f"  平均收益: {avg_return:.2f}%")
        logger.info(f"  平均胜率: {avg_winrate:.1f}%")
        logger.info(f"  平均最大回撤: {avg_mdd:.2f}%")
    
    # Top 5
    logger.info(f"\n🏆 Top 5 最优配置:")
    for i, r in enumerate(ranked[:5]):
        logger.info(f"  #{i+1} {r['symbol']} OS={r['oversold_rsi']} OB={r['overbought_rsi']} "
                   f"SL={r['stop_loss']:.0%} TP={r['take_profit']:.0%} PS={r['position_size']:.0%}")
        logger.info(f"      收益={r['total_return']:.2f}% 胜率={r['win_rate']:.0f}% "
                   f"交易={r['total_trades']} MDD={r['max_drawdown']:.2f}% 分={r['composite_score']:.2f}")
    
    # 保存结果
    output = {
        "total_simulations": len(all_results),
        "profitable_count": len(profitable),
        "results": all_results,
        "ranked": ranked[:20],
        "timestamp": datetime.now().isoformat(),
    }
    
    output_path = "/root/.openclaw/workspace/GO2SE_PLATFORM/deep_sim_v2_results.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    logger.info(f"💾 结果已保存: {output_path}")
    
    # 保存最优配置
    if ranked:
        best = ranked[0]
        best_config = {
            "strategy": "oversold_rebound",
            "oversold_rsi": best["oversold_rsi"],
            "overbought_rsi": best["overbought_rsi"],
            "stop_loss": best["stop_loss"],
            "take_profit": best["take_profit"],
            "position_size": best["position_size"],
            "symbol": best["symbol"],
            "total_return": best["total_return"],
            "win_rate": best["win_rate"],
            "total_trades": best["total_trades"],
            "max_drawdown": best["max_drawdown"],
            "sharpe_ratio": best["sharpe_ratio"],
            "composite_score": best["composite_score"],
            "updated_at": datetime.now().isoformat(),
        }
        config_path = "/root/.openclaw/workspace/GO2SE_PLATFORM/optimal_config_v2.json"
        with open(config_path, "w") as f:
            json.dump(best_config, f, indent=2, ensure_ascii=False)
        logger.info(f"🏆 最优配置已保存: {config_path}")
    
    logger.info("\n✅ 深度仿真V2完成!")


if __name__ == "__main__":
    asyncio.run(run_optimization())
