#!/usr/bin/env python3
"""
🪿 GO2SE 深度仿真测试 + 自动优化引擎
自动参数搜索 + 策略对比 + 最优配置输出
"""

import asyncio
import json
import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import logging

# 添加backend路径
sys.path.insert(0, '/root/.openclaw/workspace/GO2SE_PLATFORM/backend')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("deep_sim")

# ─── 参数搜索空间 ────────────────────────────────────────────────
PARAM_GRID = {
    "strategy": ["rsi_macross", "rsi_extreme", "macd_cross", "bollinger breakout"],
    "stop_loss": [0.02, 0.03, 0.05, 0.08, 0.10],
    "take_profit": [0.05, 0.10, 0.15, 0.20, 0.25, 0.30],
    "position_size": [0.05, 0.10, 0.15, 0.20],
}

SYMBOLS = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
DATE_RANGE = {
    "start_date": "2025-01-01",
    "end_date": "2025-12-31",
}
INITIAL_CAPITAL = 10000.0


class DeepSimulator:
    """深度仿真引擎"""

    def __init__(self):
        self.results: List[Dict] = []
        self.best_result: Dict = {"total_return": -9999}

    async def run_single(
        self,
        exchange,
        strategy: str,
        stop_loss: float,
        take_profit: float,
        position_size: float,
        symbol: str
    ) -> Dict:
        """运行单次回测"""
        from app.core.backtest_engine import BacktestEngine, BacktestConfig

        config = BacktestConfig(
            symbol=symbol,
            start_date=DATE_RANGE["start_date"],
            end_date=DATE_RANGE["end_date"],
            initial_capital=INITIAL_CAPITAL,
            stop_loss=stop_loss,
            take_profit=take_profit,
            position_size=position_size,
            strategy=strategy
        )

        be = BacktestEngine(exchange=exchange)
        result = await be.run(config)

        return {
            **result,
            "strategy": strategy,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "position_size": position_size,
            "symbol": symbol,
            "params_hash": f"{strategy}_{stop_loss}_{take_profit}_{position_size}"
        }

    async def run_grid(self, exchange) -> List[Dict]:
        """网格搜索 (有限组合)"""
        all_results = []
        total = (
            len(PARAM_GRID["strategy"])
            * len(PARAM_GRID["stop_loss"])
            * len(PARAM_GRID["take_profit"])
            * len(PARAM_GRID["position_size"])
        )

        logger.info(f"🔬 开始网格搜索: {total} 种组合 × {len(SYMBOLS)} 币种")

        count = 0
        for strategy in PARAM_GRID["strategy"]:
            for sl in PARAM_GRID["stop_loss"]:
                for tp in PARAM_GRID["take_profit"]:
                    for ps in PARAM_GRID["position_size"]:
                        for symbol in SYMBOLS:
                            count += 1
                            try:
                                result = await self.run_single(
                                    exchange, strategy, sl, tp, ps, symbol
                                )
                                all_results.append(result)
                                logger.info(
                                    f"  [{count}/{total}] {symbol} {strategy} "
                                    f"SL={sl:.0%} TP={tp:.0%} PS={ps:.0%} "
                                    f"→ Return={result.get('total_return', 0):.2f}% "
                                    f"WinRate={result.get('win_rate', 0):.1f}% "
                                    f"MDD={result.get('max_drawdown', 0):.2f}%"
                                )
                            except Exception as e:
                                logger.error(f"  [{count}/{total}] ERROR: {e}")

        return all_results

    def analyze(self, results: List[Dict]) -> Dict:
        """分析结果，找出最优"""
        if not results:
            return {"error": "No results"}

        # 按总收益排序
        ranked = sorted(results, key=lambda x: x.get("total_return", 0), reverse=True)

        # 按夏普比率排序
        by_sharpe = sorted(results, key=lambda x: x.get("sharpe_ratio", 0), reverse=True)

        # 按最大回撤排序 (越小越好)
        by_mdd = sorted(results, key=lambda x: x.get("max_drawdown", 100))

        # 按胜率排序
        by_winrate = sorted(results, key=lambda x: x.get("win_rate", 0), reverse=True)

        # 筛选正收益组合
        profitable = [r for r in results if r.get("total_return", 0) > 0]

        # 综合评分 (收益*0.4 + 夏普*0.3 + 胜率*0.2 + 低回撤*0.1)
        for r in results:
            score = (
                max(0, r.get("total_return", 0)) * 0.4
                + r.get("sharpe_ratio", 0) * 0.3 * 10
                + r.get("win_rate", 0) * 0.2
                + max(0, 30 - r.get("max_drawdown", 0)) * 0.1
            )
            r["composite_score"] = score

        by_score = sorted(results, key=lambda x: x["composite_score"], reverse=True)

        analysis = {
            "total_simulations": len(results),
            "profitable_count": len(profitable),
            "profitable_rate": f"{len(profitable)/len(results)*100:.1f}%",
            "best_by_return": ranked[0] if ranked else None,
            "best_by_sharpe": by_sharpe[0] if by_sharpe else None,
            "best_by_mdd": by_mdd[0] if by_mdd else None,
            "best_by_winrate": by_winrate[0] if by_winrate else None,
            "best_composite": by_score[0] if by_score else None,
            "top10": ranked[:10],
            "worst5": ranked[-5:] if len(ranked) >= 5 else ranked,
            "avg_return": sum(r.get("total_return", 0) for r in results) / len(results),
            "avg_winrate": sum(r.get("win_rate", 0) for r in results) / len(results),
            "avg_mdd": sum(r.get("max_drawdown", 0) for r in results) / len(results),
            "timestamp": datetime.now().isoformat(),
        }

        self.results = results
        return analysis

    def save_results(self, analysis: Dict, output_path: str):
        """保存结果"""
        output = {
            "analysis": analysis,
            "all_results": self.results,
        }
        with open(output_path, "w") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        logger.info(f"💾 结果已保存: {output_path}")


async def main():
    logger.info("=" * 60)
    logger.info("🪿 GO2SE 深度仿真测试 + 自动优化引擎")
    logger.info("=" * 60)

    # 初始化交易所
    from app.core.trading_engine import engine
    engine.init_exchange()
    exchange = engine.exchange

    if exchange is None:
        logger.error("交易所未初始化，回测终止")
        return

    # 运行仿真
    sim = DeepSimulator()
    results = await sim.run_grid(exchange)

    # 分析结果
    analysis = sim.analyze(results)

    # 打印报告
    logger.info("\n" + "=" * 60)
    logger.info("📊 仿真分析报告")
    logger.info("=" * 60)
    logger.info(f"  总仿真次数: {analysis['total_simulations']}")
    logger.info(f"  正收益组合: {analysis['profitable_count']} ({analysis['profitable_rate']})")
    logger.info(f"  平均收益: {analysis['avg_return']:.2f}%")
    logger.info(f"  平均胜率: {analysis['avg_winrate']:.1f}%")
    logger.info(f"  平均最大回撤: {analysis['avg_mdd']:.2f}%")

    best = analysis["best_composite"]
    if best:
        logger.info(f"\n🏆 最优综合配置:")
        logger.info(f"  策略: {best['strategy']}")
        logger.info(f"  止损: {best['stop_loss']:.0%}")
        logger.info(f"  止盈: {best['take_profit']:.0%}")
        logger.info(f"  仓位: {best['position_size']:.0%}")
        logger.info(f"  币种: {best['symbol']}")
        logger.info(f"  收益: {best.get('total_return', 0):.2f}%")
        logger.info(f"  夏普: {best.get('sharpe_ratio', 0):.3f}")
        logger.info(f"  胜率: {best.get('win_rate', 0):.1f}%")
        logger.info(f"  回撤: {best.get('max_drawdown', 0):.2f}%")
        logger.info(f"  综合分: {best.get('composite_score', 0):.2f}")

    # 保存
    output = "/root/.openclaw/workspace/GO2SE_PLATFORM/deep_sim_results.json"
    sim.save_results(analysis, output)

    # 保存最优配置到专用文件
    if best:
        best_config = {
            "strategy": best["strategy"],
            "stop_loss": best["stop_loss"],
            "take_profit": best["take_profit"],
            "position_size": best["position_size"],
            "symbol": best["symbol"],
            "total_return": best.get("total_return", 0),
            "sharpe_ratio": best.get("sharpe_ratio", 0),
            "win_rate": best.get("win_rate", 0),
            "max_drawdown": best.get("max_drawdown", 0),
            "updated_at": datetime.now().isoformat(),
        }
        with open("/root/.openclaw/workspace/GO2SE_PLATFORM/optimal_config.json", "w") as f:
            json.dump(best_config, f, indent=2, ensure_ascii=False)
        logger.info("🏆 最优配置已保存: optimal_config.json")

    logger.info("\n✅ 深度仿真完成!")


if __name__ == "__main__":
    asyncio.run(main())
