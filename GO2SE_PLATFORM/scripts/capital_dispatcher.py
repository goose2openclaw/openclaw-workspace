#!/usr/bin/env python3
"""
🪿 GO2SE AI资金调配器 V1
独立的资金调度层，与胜率/评分解耦

原理:
  传统: 资金分配 = f(胜率, 评分) ← 耦合
  目标: 资金分配 = g(市场机会, 工具特性, 风控) ← 解耦

核心逻辑:
  1. 机会感知: 市场机会扫描 (波动率/趋势/流动性)
  2. 工具特性: 每种工具最适合什么市场
  3. 风控上限: 最大回撤/仓位限制
  4. 独立调度: 不受胜率影响

工具 ↔ 市场适配矩阵:
  工具        │  高波动 │  低波动 │  趋势   │  区间   │  预测市场
  ────────────┼────────┼────────┼────────┼────────┼─────────
  🐰 打兔子    │   1.0  │  1.5   │  1.2   │  1.5   │   0.5
  🐹 打地鼠    │  2.0   │  0.5   │  1.5   │  0.3   │   1.0
  🔮 走着瞧    │  0.8   │  1.0   │  1.0   │  1.0   │  3.0
  👑 跟大哥    │  1.5   │  1.2   │  2.0   │  1.0   │   0.8
  🍀 搭便车    │  1.2   │  1.0   │  1.5   │  1.2   │   1.0
  💰 薅羊毛    │  1.0   │  1.0   │  1.0   │  1.0   │   1.0
  👶 穷孩子    │  1.0   │  1.0   │  1.0   │  1.0   │   1.0
"""

import json
import time
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

sys.path.insert(0, '/root/.openclaw/workspace/GO2SE_PLATFORM/backend')

BASE = "/root/.openclaw/workspace/GO2SE_PLATFORM"
BACKEND_URL = "http://localhost:8004"
STATE_FILE = f"{BASE}/capital_dispatcher_state.json"


class MarketRegime(Enum):
    """市场状态枚举"""
    HIGH_VOL = "high_volatility"      # 高波动
    LOW_VOL = "low_volatility"        # 低波动
    TRENDING_UP = "trending_up"       # 上涨趋势
    TRENDING_DOWN = "trending_down"   # 下跌趋势
    RANGE_BOUND = "range_bound"       # 区间震荡
    UNKNOWN = "unknown"


@dataclass
class ToolCapitalConfig:
    """工具资金配置"""
    tool_id: str
    name: str
    base_weight: float       # 基础权重
    min_allocation: float    # 最小分配 ($)
    max_allocation: float   # 最大分配 ($)
    base_allocation: float  # 基础分配 ($)
    current_allocation: float  # 当前分配
    # 市场适配系数 (由AI动态调整)
    regime_multipliers: Dict[str, float] = field(default_factory=dict)
    # 状态
    is_active: bool = True
    last_dispatch: str = ""


@dataclass
class MarketOpportunity:
    """市场机会"""
    regime: MarketRegime
    volatility: float       # 波动率指数 0-100
    trend_strength: float  # 趋势强度 0-100
    volume: float          # 成交量因子 0-100
    confidence: float      # 判断置信度 0-100


@dataclass
class DispatchResult:
    """调度结果"""
    timestamp: str
    market_regime: MarketRegime
    total_pool: float
    dispatches: List[Dict]
    reason: str


class CapitalDispatcher:
    """AI资金调配器"""

    # 工具 ↔ 市场适配矩阵 (市场最适合的工具)
    REGIME_MATRIX = {
        "rabbit":    {"high_volatility": 1.0, "low_volatility": 1.5, "trending_up": 1.2, "trending_down": 1.0, "range_bound": 1.5, "unknown": 1.0},
        "mole":      {"high_volatility": 2.0, "low_volatility": 0.5, "trending_up": 1.5, "trending_down": 1.8, "range_bound": 0.3, "unknown": 1.0},
        "oracle":    {"high_volatility": 0.8, "low_volatility": 1.0, "trending_up": 1.0, "trending_down": 1.0, "range_bound": 1.0, "unknown": 1.0, "prediction_market": 3.0},
        "leader":    {"high_volatility": 1.5, "low_volatility": 1.2, "trending_up": 2.0, "trending_down": 1.5, "range_bound": 1.0, "unknown": 1.0},
        "hitchhiker":{"high_volatility": 1.2, "low_volatility": 1.0, "trending_up": 1.5, "trending_down": 0.8, "range_bound": 1.2, "unknown": 1.0},
        "wool":      {"high_volatility": 1.0, "low_volatility": 1.0, "trending_up": 1.0, "trending_down": 1.0, "range_bound": 1.0, "unknown": 1.0},
        "poor":      {"high_volatility": 1.0, "low_volatility": 1.0, "trending_up": 1.0, "trending_down": 1.0, "range_bound": 1.0, "unknown": 1.0},
    }

    def __init__(self):
        self.state = self._load_state()
        self.tool_configs = self._init_tool_configs()

    # ─── 状态管理 ────────────────────────────────────────────────

    def _load_state(self) -> Dict:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE) as f:
                return json.load(f)
        return {
            "last_dispatch": None,
            "dispatch_history": [],
            "total_pool": 100000,
            "investment_pool": 80000,
        }

    def _save_state(self):
        with open(STATE_FILE, "w") as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    def _init_tool_configs(self) -> List[ToolCapitalConfig]:
        """初始化工具配置"""
        total_pool = self.state.get("investment_pool", 80000)

        # 工具基础配置 (% of investment pool)
        # 注意: 总和必须 = 100 (当前工具) + 5 (预留) = 100%
        tool_defs = [
            # tool_id, name, base_weight%, min%, max%
            ("rabbit",    "🐰 打兔子",    20,  5, 40),   # 默认20%
            ("mole",      "🐹 打地鼠",    40, 10, 50),   # 默认40%
            ("oracle",    "🔮 走着瞧",    15,  5, 30),   # 默认15%
            ("leader",    "👑 跟大哥",     0,  0, 20),   # 默认0%
            ("hitchhiker","🍀 搭便车",    10,  5, 25),   # 默认10%
            ("wool",      "💰 薅羊毛",     5,  1, 10),   # 默认5%
            ("poor",      "👶 穷孩子",    10,  1, 10),   # 默认10%
            # 预留 0% (其他工具)
        ]
        # 验证总和 = 100%
        total_weight = sum(d[2] for d in tool_defs)
        assert total_weight == 100, f"基础权重总和={total_weight}%, 必须=100%"

        configs = []
        for tool_id, name, base_w, min_w, max_w in tool_defs:
            base_alloc = total_pool * base_w / 100
            cfg = ToolCapitalConfig(
                tool_id=tool_id, name=name,
                base_weight=base_w,
                min_allocation=total_pool * min_w / 100,
                max_allocation=total_pool * max_w / 100,
                base_allocation=base_alloc,
                current_allocation=base_alloc,  # 默认使用基础分配
            )
            configs.append(cfg)

        # 从状态恢复当前分配
        saved = self.state.get("tool_allocations", {})
        if saved:
            for cfg in configs:
                if cfg.tool_id in saved:
                    cfg.current_allocation = saved[cfg.tool_id]

        return configs

    # ─── 市场机会感知 ────────────────────────────────────────────

    def _detect_market_regime(self) -> MarketOpportunity:
        """检测市场状态"""
        # 默认使用中性市场
        regime = MarketRegime.UNKNOWN
        volatility = 50
        trend_strength = 50
        volume = 50
        confidence = 30

        try:
            import urllib.request

            # 1. 获取市场数据
            req = urllib.request.Request(f"{BACKEND_URL}/api/v7/market-regime")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
                regime_str = data.get("regime", "unknown")
                volatility = data.get("volatility", 50)
                trend_strength = data.get("trend_strength", 50)
                volume = data.get("volume", 50)
                confidence = data.get("confidence", 50)

                regime_map = {
                    "high_volatility": MarketRegime.HIGH_VOL,
                    "low_volatility": MarketRegime.LOW_VOL,
                    "trending_up": MarketRegime.TRENDING_UP,
                    "trending_down": MarketRegime.TRENDING_DOWN,
                    "range_bound": MarketRegime.RANGE_BOUND,
                }
                regime = regime_map.get(regime_str, MarketRegime.UNKNOWN)

        except Exception as e:
            # 尝试从声纳库获取
            try:
                req = urllib.request.Request(f"{BACKEND_URL}/api/sonar/trends")
                with urllib.request.urlopen(req, timeout=5) as resp:
                    data = json.loads(resp.read())
                    signal = data.get("signal", "neutral")

                    if signal == "bullish":
                        regime = MarketRegime.TRENDING_UP
                        trend_strength = 70
                    elif signal == "bearish":
                        regime = MarketRegime.TRENDING_DOWN
                        trend_strength = 70
                    else:
                        regime = MarketRegime.RANGE_BOUND
                        trend_strength = 40

                    confidence = data.get("confidence", 50)
            except:
                # 使用默认
                pass

        return MarketOpportunity(
            regime=regime,
            volatility=volatility,
            trend_strength=trend_strength,
            volume=volume,
            confidence=confidence,
        )

    def _calculate_opportunity_score(self, cfg: ToolCapitalConfig, opportunity: MarketOpportunity) -> float:
        """计算单个工具的机会评分"""
        regime_key = opportunity.regime.value
        base_multiplier = self.REGIME_MATRIX.get(cfg.tool_id, {}).get(regime_key, 1.0)

        # 市场机会因子
        vol_factor = opportunity.volatility / 100  # 0-1
        trend_factor = opportunity.trend_strength / 100  # 0-1
        conf_factor = opportunity.confidence / 100  # 0-1

        # 工具对不同市场因子的敏感度
        tool_sensitivities = {
            "rabbit":    {"vol": 0.3, "trend": 0.5, "conf": 0.2},
            "mole":      {"vol": 0.7, "trend": 0.3, "conf": 0.0},
            "oracle":    {"vol": 0.1, "trend": 0.3, "conf": 0.6},
            "leader":    {"vol": 0.3, "trend": 0.7, "conf": 0.0},
            "hitchhiker":{"vol": 0.4, "trend": 0.5, "conf": 0.1},
            "wool":      {"vol": 0.0, "trend": 0.0, "conf": 0.0},
            "poor":      {"vol": 0.0, "trend": 0.0, "conf": 0.0},
        }

        sens = tool_sensitivities.get(cfg.tool_id, {"vol": 0.3, "trend": 0.3, "conf": 0.3})

        # 综合评分 = 基础系数 × 市场机会加权
        market_score = (
            base_multiplier *
            (1 + sens["vol"] * (vol_factor - 0.5) + sens["trend"] * (trend_factor - 0.5) + sens["conf"] * (conf_factor - 0.5))
        )

        # 归一化到 0.5 - 2.0 范围
        return max(0.5, min(2.0, market_score))

    # ─── 资金调度 ────────────────────────────────────────────────

    def dispatch(self, force: bool = False) -> DispatchResult:
        """执行资金调度"""
        print("=" * 70)
        print(f"🪿 AI资金调配器 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("=" * 70)

        # 1. 检测市场机会
        print("\n🔍 市场机会感知:")
        opportunity = self._detect_market_regime()
        regime_emoji = {
            MarketRegime.HIGH_VOL: "📊",
            MarketRegime.LOW_VOL: "📉",
            MarketRegime.TRENDING_UP: "🚀",
            MarketRegime.TRENDING_DOWN: "🔻",
            MarketRegime.RANGE_BOUND: "➡️",
            MarketRegime.UNKNOWN: "❓",
        }.get(opportunity.regime, "❓")

        print(f"  市场状态: {regime_emoji} {opportunity.regime.value}")
        print(f"  波动率: {opportunity.volatility}/100")
        print(f"  趋势强度: {opportunity.trend_strength}/100")
        print(f"  置信度: {opportunity.confidence}/100")

        # 2. 计算各工具机会评分
        print("\n📊 工具机会评分:")
        total_pool = self.state.get("investment_pool", 80000)

        opportunity_scores = {}
        for cfg in self.tool_configs:
            if not cfg.is_active:
                continue
            score = self._calculate_opportunity_score(cfg, opportunity)
            opportunity_scores[cfg.tool_id] = score
            print(f"  {cfg.name}: {score:.2f}x ({cfg.tool_id})")

        # 3. 计算目标分配
        print("\n💰 资金调度计算:")

        # 归一化机会评分
        total_score = sum(opportunity_scores.values())
        if total_score == 0:
            total_score = 1

        # 计算目标分配
        target_allocations = {}
        for tool_id, score in opportunity_scores.items():
            cfg = next((c for c in self.tool_configs if c.tool_id == tool_id), None)
            if cfg is None:
                continue

            # 目标分配 = 基础分配 × 机会评分
            # 但要在 min/max 范围内
            raw_target = cfg.base_allocation * score
            target = max(cfg.min_allocation, min(cfg.max_allocation, raw_target))
            target_allocations[tool_id] = target

        # 归一化确保总和等于总池
        total_target = sum(target_allocations.values())
        if total_target > 0:
            scale = total_pool / total_target
            for tool_id in target_allocations:
                target_allocations[tool_id] *= scale

        # 4. 展示调度结果
        print(f"\n{'工具':<12} {'当前分配':>12} {'目标分配':>12} {'调整':>10} {'原因'}")
        print("-" * 70)

        dispatches = []
        for cfg in self.tool_configs:
            current = cfg.current_allocation
            target = target_allocations.get(cfg.tool_id, cfg.min_allocation)
            delta = target - current
            delta_pct = (delta / current * 100) if current > 0 else 0

            emoji = "➖" if abs(delta) < total_pool * 0.01 else ("📈" if delta > 0 else "📉")
            reason = self._get_dispatch_reason(cfg, opportunity, delta_pct)

            print(f"{cfg.name:<12} ${current:>10,.0f} ${target:>10,.0f} {emoji}{delta_pct:>+8.1f}% {reason}")

            dispatches.append({
                "tool_id": cfg.tool_id,
                "name": cfg.name,
                "current": current,
                "target": target,
                "delta": delta,
                "delta_pct": delta_pct,
                "opportunity_score": opportunity_scores.get(cfg.tool_id, 1.0),
                "reason": reason,
            })

        # 5. 保存调度结果
        result = DispatchResult(
            timestamp=datetime.now().isoformat(),
            market_regime=opportunity.regime,
            total_pool=total_pool,
            dispatches=dispatches,
            reason=f"市场{opportunity.regime.value}, 置信度{opportunity.confidence}%",
        )

        # 更新状态
        self.state["last_dispatch"] = result.timestamp
        self.state["market_regime"] = opportunity.regime.value
        self.state["tool_allocations"] = {d["tool_id"]: d["target"] for d in dispatches}
        self.state["dispatch_history"].append({
            "timestamp": result.timestamp,
            "regime": result.market_regime.value,
            "dispatches": [{"tool_id": d["tool_id"], "delta_pct": d["delta_pct"]} for d in dispatches],
        })
        self.state["dispatch_history"] = self.state["dispatch_history"][-20:]  # 保留最近20次

        for cfg in self.tool_configs:
            if cfg.tool_id in target_allocations:
                cfg.current_allocation = target_allocations[cfg.tool_id]
                cfg.last_dispatch = result.timestamp

        self._save_state()

        # 6. 输出汇总
        total_current = sum(d["current"] for d in dispatches)
        total_target = sum(d["target"] for d in dispatches)
        total_delta = total_target - total_current

        print(f"\n{'='*70}")
        print(f"📈 调度汇总:")
        print(f"  总资金池: ${total_pool:,.0f}")
        print(f"  当前配置: ${total_current:,.0f}")
        print(f"  目标配置: ${total_target:,.0f}")
        print(f"  调整幅度: ${total_delta:>+10,.0f}")
        print(f"  市场状态: {regime_emoji} {opportunity.regime.value}")
        print(f"{'='*70}")

        return result

    def _get_dispatch_reason(self, cfg: ToolCapitalConfig, opportunity: MarketOpportunity, delta_pct: float) -> str:
        """获取调度原因"""
        regime = opportunity.regime.value
        matrix = self.REGIME_MATRIX.get(cfg.tool_id, {})

        if abs(delta_pct) < 1:
            return "无需调整"

        base_mult = matrix.get(regime, 1.0)
        if base_mult >= 1.5:
            return f"适合{regime}"
        elif base_mult >= 1.2:
            return f"偏好{regime}"
        elif base_mult <= 0.5:
            return f"规避{regime}"
        else:
            return f"中性{regime}"

    # ─── API接口 ────────────────────────────────────────────────

    def get_allocations(self) -> Dict:
        """获取当前分配"""
        return {
            "timestamp": self.state.get("last_dispatch", ""),
            "market_regime": self.state.get("market_regime", "unknown"),
            "total_pool": self.state.get("investment_pool", 80000),
            "tools": [
                {
                    "tool_id": cfg.tool_id,
                    "name": cfg.name,
                    "allocation": cfg.current_allocation,
                    "base_allocation": cfg.base_allocation,
                    "weight": cfg.current_allocation / self.state.get("investment_pool", 80000) * 100,
                    "is_active": cfg.is_active,
                }
                for cfg in self.tool_configs
            ],
        }

    def apply_dispatch(self) -> bool:
        """应用调度结果到Backend"""
        try:
            import urllib.request

            payload = json.dumps({
                "source": "capital_dispatcher",
                "allocations": {cfg.tool_id: cfg.current_allocation for cfg in self.tool_configs},
                "timestamp": datetime.now().isoformat(),
            }).encode()

            req = urllib.request.Request(
                f"{BACKEND_URL}/api/performance/allocations",
                data=payload,
                method="PUT",
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                print(f"✅ 资金分配已同步到Backend")
                return True

        except Exception as e:
            print(f"⚠️  同步失败: {e}")
            return False


def main():
    import argparse
    parser = argparse.ArgumentParser(description="GO2SE AI资金调配器")
    parser.add_argument("--apply", action="store_true", help="应用调度结果")
    parser.add_argument("--show", action="store_true", help="显示当前分配")
    args = parser.parse_args()

    dispatcher = CapitalDispatcher()

    if args.show:
        alloc = dispatcher.get_allocations()
        print(json.dumps(alloc, indent=2, ensure_ascii=False))
    else:
        result = dispatcher.dispatch()
        if args.apply:
            dispatcher.apply_dispatch()
        return result


if __name__ == "__main__":
    main()
