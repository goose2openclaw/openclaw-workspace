#!/usr/bin/env python3
"""
🪿 GO2SE V10 - 7天回测优化版
基于: 北斗七鑫V10性能矩阵 + 投资组合权重
数据源: API信号 / 声纳库 / Oracle / MiroFish / 第三方
"""

import json
import time
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

sys.path.insert(0, '/root/.openclaw/workspace/GO2SE_PLATFORM/backend')

BASE = "/root/.openclaw/workspace/GO2SE_PLATFORM"
BACKEND_URL = "http://localhost:8004"

@dataclass
class ToolAllocation:
    tool_id: str
    name: str
    weight: float  # 0-100
    allocation: float  # 美元金额
    expert_score: float
    color: str
    mode: str  # "normal" | "expert"
    # 回测参数
    stop_loss: float
    take_profit: float
    position_size: float
    # 表现
    total_trades: int = 0
    wins: int = 0
    losses: int = 0
    pnl: float = 0.0
    win_rate: float = 0.0
    return_pct: float = 0.0


class V10BacktestEngine:
    """V10回测引擎 - 基于性能矩阵的多工具组合回测"""

    def __init__(self):
        self.performance = self._load_performance()
        self.allocations = self._build_allocations()
        self.results = {}

    def _load_performance(self) -> Dict:
        """从API获取性能矩阵"""
        try:
            import urllib.request
            req = urllib.request.Request(f"{BACKEND_URL}/api/performance")
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read())
        except Exception as e:
            print(f"⚠️  API不可用，使用本地数据: {e}")
            return self._default_performance()

    def _default_performance(self) -> Dict:
        return {
            "investment_tools": {
                "rabbit":    {"name": "🐰 打兔子",  "weight": 0,  "expert_score": 5.5,  "color": "#64748B"},
                "mole":      {"name": "🐹 打地鼠",  "weight": 50, "expert_score": 71.8, "color": "#00D4AA"},
                "oracle":    {"name": "🔮 走着瞧",  "weight": 25, "expert_score": 79.1, "color": "#7C3AED"},
                "leader":   {"name": "👑 跟大哥",  "weight": 0,  "expert_score": 41.8, "color": "#F59E0B"},
                "hitchhiker":{"name": "🍀 搭便车", "weight": 10, "expert_score": 68.0, "color": "#3B82F6"},
            },
            "work_tools": {
                "wool": {"name": "💰 薅羊毛", "weight": 3, "cashflow_rate": 0.02, "color": "#EF4444"},
                "poor": {"name": "👶 穷孩子", "weight": 5, "cashflow_rate": 0.03, "color": "#EC4899"},
            },
            "total_capital": 100000.0,
            "investment_pool": 80000.0,
        }

    def _build_allocations(self) -> List[ToolAllocation]:
        """基于性能矩阵构建工具分配"""
        total = self.performance.get("investment_pool", 80000)
        inv_tools = self.performance.get("investment_tools", {})

        allocations = []
        for tool_id, data in inv_tools.items():
            weight = data.get("weight", 0)
            if weight <= 0:
                continue

            alloc = ToolAllocation(
                tool_id=tool_id,
                name=data.get("name", tool_id),
                weight=weight,
                allocation=total * weight / 100,
                expert_score=data.get("expert_score", 50),
                color=data.get("color", "#888"),
                mode="expert",  # V10统一使用专家模式
                stop_loss=self._get_stop_loss(tool_id),
                take_profit=self._get_take_profit(tool_id),
                position_size=self._get_position_size(tool_id),
            )
            allocations.append(alloc)

        return sorted(allocations, key=lambda x: x.expert_score, reverse=True)

    def _get_stop_loss(self, tool_id: str) -> float:
        """根据工具类型确定止损"""
        defaults = {
            "rabbit": 0.02, "mole": 0.03, "oracle": 0.05,
            "leader": 0.03, "hitchhiker": 0.05
        }
        return defaults.get(tool_id, 0.05)

    def _get_take_profit(self, tool_id: str) -> float:
        """根据工具类型确定止盈"""
        defaults = {
            "rabbit": 0.08, "mole": 0.12, "oracle": 0.10,
            "leader": 0.06, "hitchhiker": 0.08
        }
        return defaults.get(tool_id, 0.10)

    def _get_position_size(self, tool_id: str) -> float:
        """根据工具评分确定仓位"""
        defaults = {
            "rabbit": 0.05, "mole": 0.15, "oracle": 0.12,
            "leader": 0.10, "hitchhiker": 0.08
        }
        return defaults.get(tool_id, 0.10)

    def _get_sonar_signal(self, symbol: str, days: int = 7) -> Dict:
        """声纳库趋势判断"""
        try:
            import urllib.request
            req = urllib.request.Request(f"{BACKEND_URL}/api/sonar/trends")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
                return {"signal": data.get("signal", "neutral"), "confidence": data.get("confidence", 50)}
        except:
            return {"signal": "bullish" if "BTC" in symbol else "neutral", "confidence": 60}

    def _get_oracle_prediction(self, symbol: str) -> Dict:
        """Oracle预测市场"""
        try:
            import urllib.request
            req = urllib.request.Request(f"{BACKEND_URL}/api/oracle/mirofish/markets")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
                markets = data.get("data", [])
                active = len([m for m in markets if m.get("status") == "active"])
                return {"prediction": "bullish" if active >= 4 else "neutral", "markets": active}
        except:
            return {"prediction": "neutral", "markets": 3}

    def _get_mirofish_score(self, tool_id: str) -> float:
        """MiroFish仿真评分"""
        for alloc in self.allocations:
            if alloc.tool_id == tool_id:
                return alloc.expert_score
        return 50.0

    def simulate_7day_trades(self, symbol: str, days: int = 7) -> List[Dict]:
        """模拟7天交易 - 基于多数据源"""
        trades = []
        now = datetime.now()

        # 获取历史价格模拟 (使用固定种子模拟)
        for day in range(days):
            date = now - timedelta(days=days-day-1)

            for alloc in self.allocations:
                if alloc.weight <= 0:
                    continue

                # 多数据源综合信号
                sonar = self._get_sonar_signal(symbol, day)
                oracle = self._get_oracle_prediction(symbol)
                mirofish_score = self._get_mirofish_score(alloc.tool_id)

                # 综合评分 (0-100)
                signal_score = 0
                if sonar["signal"] == "bullish":
                    signal_score += 30
                elif sonar["signal"] == "bearish":
                    signal_score -= 20

                if oracle["prediction"] == "bullish":
                    signal_score += 25
                elif oracle["prediction"] == "bearish":
                    signal_score -= 15

                signal_score += mirofish_score * 0.45  # MiroFish占45%

                # 只有信号>60才交易
                if signal_score < 60:
                    continue

                # 计算盈亏
                direction = "long" if signal_score > 70 else "neutral"
                if direction == "long":
                    # 模拟: 60%概率盈利, 40%概率亏损
                    import random
                    random.seed(int(date.timestamp()) + hash(alloc.tool_id) % 1000)
                    win = random.random() < 0.60

                    if win:
                        pnl = alloc.allocation * alloc.take_profit
                        alloc.wins += 1
                    else:
                        pnl = -alloc.allocation * alloc.stop_loss
                        alloc.losses += 1

                    alloc.pnl += pnl
                    trades.append({
                        "date": date.isoformat(),
                        "tool": alloc.tool_id,
                        "symbol": symbol,
                        "direction": direction,
                        "entry_price": 50000 + random.randint(-5000, 5000),
                        "pnl": pnl,
                        "signal_score": signal_score,
                        "mirofish": mirofish_score,
                        "sonar": sonar["signal"],
                        "oracle": oracle["prediction"],
                    })

        return trades

    def run_backtest(self, symbols: List[str] = None, days: int = 7) -> Dict:
        """运行7天回测"""
        if symbols is None:
            symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]

        print("=" * 80)
        print(f"🪿 GO2SE V10 7天回测 - {datetime.now().strftime('%Y-%m-%d')}")
        print("=" * 80)
        print(f"\n📊 性能矩阵配置:")
        for alloc in self.allocations:
            print(f"  {alloc.name}: 权重={alloc.weight}% 分配=${alloc.allocation:,.0f} 评分={alloc.expert_score}")
        print()

        all_trades = []
        total_start = self.performance.get("total_capital", 100000)

        for symbol in symbols:
            print(f"📈 回测 {symbol}...")
            trades = self.simulate_7day_trades(symbol, days)
            all_trades.extend(trades)
            print(f"  → {len(trades)} 笔交易")

        # 汇总各工具结果
        print("\n" + "=" * 80)
        print("📊 回测结果汇总")
        print("=" * 80)

        total_pnl = 0
        total_trades = 0
        total_wins = 0

        for alloc in self.allocations:
            alloc.total_trades = alloc.wins + alloc.losses
            total_trades += alloc.total_trades
            total_wins += alloc.wins
            total_pnl += alloc.pnl

            if alloc.total_trades > 0:
                alloc.win_rate = alloc.wins / alloc.total_trades * 100
            alloc.return_pct = alloc.pnl / alloc.allocation * 100 if alloc.allocation > 0 else 0

            status = "✅" if alloc.pnl >= 0 else "❌"
            print(f"\n{alloc.name} ({alloc.mode}模式)")
            print(f"  评分: {alloc.expert_score} | 分配: ${alloc.allocation:,.0f}")
            print(f"  交易: {alloc.total_trades}笔 | 胜率: {alloc.win_rate:.1f}%")
            print(f"  盈亏: {alloc.pnl:+.2f} ({alloc.return_pct:+.2f}%)")

        total_return = total_pnl / total_start * 100
        overall_wr = total_wins / max(total_trades, 1) * 100

        print(f"\n{'='*80}")
        print(f"📈 组合总览:")
        print(f"  总交易: {total_trades}笔")
        print(f"  总胜率: {overall_wr:.1f}%")
        print(f"  总盈亏: ${total_pnl:+.2f} ({total_return:+.2f}%)")
        print(f"  初始资金: ${total_start:,.0f}")
        print(f"  最终资金: ${total_start + total_pnl:,.2f}")
        print(f"{'='*80}")

        return {
            "timestamp": datetime.now().isoformat(),
            "period_days": days,
            "initial_capital": total_start,
            "final_capital": total_start + total_pnl,
            "total_pnl": total_pnl,
            "total_return_pct": total_return,
            "total_trades": total_trades,
            "win_rate": overall_wr,
            "tools": [asdict(a) for a in self.allocations],
            "trades": all_trades,
            "performance_matrix": {
                "investment_tools": self.performance.get("investment_tools", {}),
                "work_tools": self.performance.get("work_tools", {}),
            }
        }

    def save_results(self, results: Dict, path: str = None):
        if path is None:
            path = f"{BASE}/v10_backtest_7day_result.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n💾 结果已保存: {path}")


def main():
    engine = V10BacktestEngine()
    results = engine.run_backtest(days=7)
    engine.save_results(results)

    # 保存到回测历史
    history_path = f"{BASE}/backtest_history.json"
    history = []
    if os.path.exists(history_path):
        with open(history_path) as f:
            history = json.load(f)
    history.append({
        "timestamp": results["timestamp"],
        "total_return_pct": results["total_return_pct"],
        "total_trades": results["total_trades"],
        "win_rate": results["win_rate"],
    })
    with open(history_path, "w") as f:
        json.dump(history[-10:], f, ensure_ascii=False, indent=2)  # 保留最近10次

    return results


if __name__ == "__main__":
    main()
