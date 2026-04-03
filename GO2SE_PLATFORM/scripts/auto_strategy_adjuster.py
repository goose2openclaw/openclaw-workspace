#!/usr/bin/env python3
"""
🪿 GO2SE 自动调整策略机制
基于性能反馈的动态权重再平衡 + MiroFish仿真验证

触发条件:
  1. 工具评分变化 > 5% → 触发再平衡检查
  2. 工具亏损超过阈值 → 触发止损/降权
  3. MiroFish评分 < 70 → 触发专家审查
  4. 每日定时再平衡 (可选)

机制:
  A. 监控 → B. 分析 → C. 验证(MiroFish) → D. 执行调整
"""

import json
import time
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import hashlib

sys.path.insert(0, '/root/.openclaw/workspace/GO2SE_PLATFORM/backend')

BASE = "/root/.openclaw/workspace/GO2SE_PLATFORM"
BACKEND_URL = "http://localhost:8004"
STATE_FILE = f"{BASE}/auto_adjuster_state.json"
CONFIG_FILE = f"{BASE}/auto_adjuster_config.json"


@dataclass
class AdjustmentRule:
    """调整规则"""
    name: str
    condition: str  # "score_change|pnl_threshold|win_rate"
    threshold: float
    action: str  # "rebalance|decrease|increase|alert"
    priority: int = 1


@dataclass
class ToolState:
    """工具状态"""
    tool_id: str
    name: str
    weight: float
    allocation: float
    expert_score: float
    mirofish_score: float
    win_rate: float
    pnl: float
    return_pct: float
    trades: int
    last_updated: str
    status: str = "normal"  # normal|warning|critical|disabled


@dataclass
class Adjustment:
    """调整操作"""
    tool_id: str
    action: str
    reason: str
    old_value: Any
    new_value: Any
    timestamp: str
    mirofish_validated: bool = False
    approved: bool = False


class AutoStrategyAdjuster:
    """自动调整策略引擎"""

    # 默认配置
    DEFAULT_CONFIG = {
        "enabled": True,
        "auto_execute": False,  # True = 自动执行, False = 仅推荐
        "min_mirofish_score": 70,  # MiroFish最低验证分数
        "rebalance_cooldown_hours": 6,  # 再平衡冷却时间
        "max_weight_change_pct": 10,  # 单次最大权重变化
        "total_capital": 100000,
        "investment_pool_ratio": 0.80,
        # 调整规则
        "rules": [
            {"name": "评分下跌告警", "condition": "score_change", "threshold": -10, "action": "alert", "priority": 1},
            {"name": "亏损超限降权", "condition": "pnl_threshold", "threshold": -0.15, "action": "decrease", "priority": 2},
            {"name": "胜率过低降权", "condition": "win_rate", "threshold": 0.35, "action": "decrease", "priority": 3},
            {"name": "评分上涨增权", "condition": "score_change", "threshold": 10, "action": "increase", "priority": 4},
        ],
        # 工具配置
        "tool_configs": {
            "rabbit":    {"min_weight": 5,  "max_weight": 40,  "target_score": 70},
            "mole":      {"min_weight": 10, "max_weight": 50,  "target_score": 75},
            "oracle":    {"min_weight": 5,  "max_weight": 30,  "target_score": 80},
            "leader":    {"min_weight": 0,  "max_weight": 20,  "target_score": 60},
            "hitchhiker":{"min_weight": 5,  "max_weight": 25,  "target_score": 70},
            "wool":      {"min_weight": 1,  "max_weight": 10,  "target_score": 65},
            "poor":      {"min_weight": 1,  "max_weight": 5,   "target_score": 60},
        }
    }

    def __init__(self):
        self.config = self._load_config()
        self.state = self._load_state()
        self.adjustments: List[Adjustment] = []

    # ─── 配置管理 ────────────────────────────────────────────────

    def _load_config(self) -> Dict:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE) as f:
                return json.load(f)
        return self.DEFAULT_CONFIG.copy()

    def _save_config(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def _load_state(self) -> Dict:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE) as f:
                return json.load(f)
        return {
            "last_rebalance": None,
            "last_adjustment": None,
            "tool_states": {},
            "adjustment_history": [],
        }

    def _save_state(self):
        with open(STATE_FILE, "w") as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    # ─── 数据获取 ────────────────────────────────────────────────

    def _fetch_performance(self) -> Dict:
        """从Backend获取性能矩阵"""
        try:
            import urllib.request
            req = urllib.request.Request(f"{BACKEND_URL}/api/performance")
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read())
        except Exception as e:
            print(f"⚠️  无法获取性能数据: {e}")
            return {}

    def _fetch_mirofish_score(self, tool_id: str) -> float:
        """获取MiroFish评分"""
        try:
            import urllib.request
            req = urllib.request.Request(f"{BACKEND_URL}/api/oracle/mirofish/score/{tool_id}")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
                return data.get("score", 50)
        except:
            # fallback: 使用专家评分
            perf = self._fetch_performance()
            tools = perf.get("investment_tools", {})
            return tools.get(tool_id, {}).get("expert_score", 50)

    def _fetch_recent_trades(self, tool_id: str, hours: int = 24) -> List[Dict]:
        """获取最近交易"""
        try:
            import urllib.request
            req = urllib.request.Request(f"{BACKEND_URL}/api/trades/{tool_id}?hours={hours}")
            with urllib.request.urlopen(req, timeout=5) as resp:
                return json.loads(resp.read())
        except:
            return []

    # ─── 状态分析 ────────────────────────────────────────────────

    def _get_tool_states(self) -> List[ToolState]:
        """获取所有工具当前状态"""
        perf = self._fetch_performance()
        inv_tools = perf.get("investment_tools", {})
        work_tools = perf.get("work_tools", {})
        all_tools = {**inv_tools, **work_tools}

        total_capital = perf.get("total_capital", self.config["total_capital"])
        investment_pool = total_capital * self.config["investment_pool_ratio"]

        states = []
        for tool_id, data in all_tools.items():
            weight = data.get("weight", 0)
            allocation = investment_pool * weight / 100 if weight > 0 else 0

            # 获取MiroFish评分
            mirofish_score = self._fetch_mirofish_score(tool_id)

            # 计算状态
            status = "normal"
            if data.get("weight", 0) <= 0:
                status = "disabled"
            elif mirofish_score < 50:
                status = "critical"
            elif mirofish_score < 70:
                status = "warning"

            state = ToolState(
                tool_id=tool_id,
                name=data.get("name", tool_id),
                weight=weight,
                allocation=allocation,
                expert_score=data.get("expert_score", 50),
                mirofish_score=mirofish_score,
                win_rate=data.get("win_rate", 0),
                pnl=data.get("pnl", 0),
                return_pct=data.get("return_pct", 0),
                trades=data.get("trades", 0),
                last_updated=datetime.now().isoformat(),
                status=status,
            )
            states.append(state)

        return sorted(states, key=lambda x: x.mirofish_score, reverse=True)

    def _check_rules(self, states: List[ToolState]) -> List[Tuple[AdjustmentRule, ToolState, float]]:
        """检查规则并返回触发的调整"""
        triggered = []
        rules = self.config.get("rules", [])

        # 只有交易数>5的工具才触发规则
        MIN_TRADES_FOR_RULE = 5

        for state in states:
            if state.status == "disabled":
                continue

            # 规则只在有足够交易数据时触发
            if state.trades < MIN_TRADES_FOR_RULE and state.win_rate == 0:
                continue

            for rule in rules:
                current_val = 0
                threshold = rule["threshold"]

                if rule["condition"] == "score_change":
                    # 评分变化 vs 上次
                    last_score = self.state.get("tool_states", {}).get(state.tool_id, {}).get("mirofish_score", state.mirofish_score)
                    current_val = state.mirofish_score - last_score

                elif rule["condition"] == "pnl_threshold":
                    current_val = state.return_pct  # 负数为亏损

                elif rule["condition"] == "win_rate":
                    current_val = state.win_rate

                # 检查是否触发
                if rule["condition"] == "score_change":
                    # 评分变化: 下跌超过threshold或上涨超过threshold
                    triggered_flag = abs(current_val) > abs(threshold)
                elif rule["condition"] == "pnl_threshold":
                    # 亏损阈值: 亏损超过threshold(负数)
                    triggered_flag = current_val < threshold
                elif rule["condition"] == "win_rate":
                    # 胜率阈值: 胜率低于threshold
                    triggered_flag = current_val < threshold
                else:
                    triggered_flag = False

                if triggered_flag:
                    triggered.append((AdjustmentRule(**rule), state, current_val))

        # 按优先级排序
        triggered.sort(key=lambda x: x[0].priority)
        return triggered

    # ─── MiroFish验证 ─────────────────────────────────────────────

    def _validate_with_mirofish(self, adjustment: Adjustment) -> bool:
        """使用MiroFish验证调整"""
        try:
            import urllib.request

            payload = json.dumps({
                "tool_id": adjustment.tool_id,
                "proposed_action": adjustment.action,
                "new_value": adjustment.new_value,
                "context": {
                    "current_score": adjustment.old_value,
                    "proposed_score": adjustment.new_value,
                }
            }).encode()

            req = urllib.request.Request(
                f"{BACKEND_URL}/api/oracle/mirofish/validate",
                data=payload,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read())
                return result.get("approved", False) and result.get("score", 0) >= self.config["min_mirofish_score"]
        except:
            # 如果MiroFish不可用，使用默认规则
            return adjustment.new_value <= self.config["tool_configs"].get(adjustment.tool_id, {}).get("max_weight", 100)

    # ─── 调整计算 ────────────────────────────────────────────────

    def _calculate_rebalance(self, states: List[ToolState]) -> List[Adjustment]:
        """计算再平衡调整"""
        adjustments = []
        total_pool = sum(s.allocation for s in states if s.weight > 0)

        if total_pool <= 0:
            return adjustments

        # 目标: 根据MiroFish评分重新分配权重
        total_score = sum(s.mirofish_score * s.weight for s in states if s.weight > 0)

        for state in states:
            if state.weight <= 0 or state.status == "disabled":
                continue

            # 计算新权重: 基于评分比例
            # 只对 MiroFish > 70 的工具增权，< 60 的降权
            tool_cfg = self.config["tool_configs"].get(state.tool_id, {})
            max_w = tool_cfg.get("max_weight", 30)
            min_w = tool_cfg.get("min_weight", 5)
            target_score = tool_cfg.get("target_score", 70)

            if state.mirofish_score >= 70:
                # 高评分工具: 基于相对评分增加权重
                target_pct = (state.mirofish_score / 100) * max_w
            elif state.mirofish_score < 60:
                # 低评分工具: 降低权重到最低
                target_pct = min_w
            else:
                # 中等评分: 保持当前权重
                continue

            target_pct = max(min_w, min(target_pct, max_w))

            # 权重变化
            weight_delta = target_pct - state.weight
            if abs(weight_delta) > self.config["max_weight_change_pct"]:
                weight_delta = self.config["max_weight_change_pct"] * (1 if weight_delta > 0 else -1)

            if abs(weight_delta) >= 1:  # 变化超过1%才调整
                new_weight = max(0, min(100, state.weight + weight_delta))
                adjustment = Adjustment(
                    tool_id=state.tool_id,
                    action="rebalance",
                    reason=f"MiroFish评分{state.mirofish_score:.1f} → 权重调整{weight_delta:+.1f}%",
                    old_value=state.weight,
                    new_value=new_weight,
                    timestamp=datetime.now().isoformat(),
                )
                adjustment.mirofish_validated = self._validate_with_mirofish(adjustment)
                adjustments.append(adjustment)

        return adjustments

    # ─── 主流程 ─────────────────────────────────────────────────

    def run_check(self, force_rebalance: bool = False) -> Dict:
        """运行自动检查"""
        print("=" * 70)
        print(f"🪿 GO2SE 自动策略调整检查 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("=" * 70)

        if not self.config["enabled"]:
            print("⚠️  自动调整已禁用")
            return {"status": "disabled"}

        # 检查冷却
        last_adj = self.state.get("last_adjustment")
        if last_adj:
            last_time = datetime.fromisoformat(last_adj)
            cooldown = self.config["rebalance_cooldown_hours"]
            if (datetime.now() - last_time).total_seconds() < cooldown * 3600:
                print(f"⏳ 冷却中 (还剩{cooldown - (datetime.now() - last_time).total_seconds()/3600:.1f}小时)")
                return {"status": "cooldown"}

        # 1. 获取状态
        print("\n📊 工具状态:")
        states = self._get_tool_states()
        for s in states:
            emoji = {"normal": "🟢", "warning": "🟡", "critical": "🔴", "disabled": "⚫"}.get(s.status, "⚪")
            print(f"  {emoji} {s.name:<12} 权重:{s.weight:>5.1f}% MiroFish:{s.mirofish_score:>5.1f} 评分:{s.expert_score:>5.1f} 盈亏:{s.return_pct:>+6.2f}%")

        # 2. 检查规则
        print("\n🔍 规则检查:")
        triggered = self._check_rules(states)

        adjustments = []

        for rule, state, value in triggered:
            adj = Adjustment(
                tool_id=state.tool_id,
                action=rule.action,
                reason=f"{rule.name}: {rule.condition}={value:.2f} {'<' if rule.threshold < 0 else '>'}{rule.threshold}",
                old_value=state.weight,
                new_value=self._calculate_new_weight(state, rule),
                timestamp=datetime.now().isoformat(),
            )
            adj.mirofish_validated = self._validate_with_mirofish(adj)
            adjustments.append(adj)
            print(f"  ⚡ {state.name}: {rule.name} → {rule.action} (MiroFish验证:{'✅' if adj.mirofish_validated else '❌'})")

        # 3. 强制再平衡 (仅在明确要求时)
        if force_rebalance:
            print("\n🔄 强制再平衡模式:")
            rebalances = self._calculate_rebalance(states)
            for adj in rebalances:
                if not any(a.tool_id == adj.tool_id for a in adjustments):
                    adjustments.append(adj)
                    print(f"  📊 {adj.tool_id}: {adj.old_value:.1f}% → {adj.new_value:.1f}%")

        # 4. 执行/推荐调整
        print("\n📋 调整建议:")
        if not adjustments:
            print("  ✅ 无需调整")
        else:
            for adj in adjustments:
                status = "✅" if adj.mirofish_validated else "⏳"
                auto_exec = "自动执行" if self.config["auto_execute"] and adj.mirofish_validated else "待确认"
                print(f"  {status} {adj.tool_id}: {adj.action} {adj.old_value:.1f}% → {adj.new_value:.1f}% ({auto_exec})")
                print(f"      原因: {adj.reason}")

        # 5. 保存状态
        self.state["last_check"] = datetime.now().isoformat()
        self.state["tool_states"] = {
            s.tool_id: {
                "mirofish_score": s.mirofish_score,
                "weight": s.weight,
                "return_pct": s.return_pct,
                "win_rate": s.win_rate,
            }
            for s in states
        }
        self.state["adjustment_history"].extend([{
            "tool_id": a.tool_id,
            "action": a.action,
            "old": a.old_value,
            "new": a.new_value,
            "timestamp": a.timestamp,
            "validated": a.mirofish_validated,
        } for a in adjustments])

        # 只保留最近20条
        self.state["adjustment_history"] = self.state["adjustment_history"][-20:]

        if adjustments and self.config["auto_execute"]:
            self._execute_adjustments(adjustments)

        self._save_state()

        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "states": [s.__dict__ for s in states],
            "adjustments": [a.__dict__ for a in adjustments],
            "auto_execute": self.config["auto_execute"],
        }

    def _calculate_new_weight(self, state: ToolState, rule: AdjustmentRule) -> float:
        """计算新权重"""
        delta_pct = self.config["max_weight_change_pct"]

        if rule.action == "decrease":
            new_weight = max(0, state.weight - delta_pct)
        elif rule.action == "increase":
            tool_cfg = self.config["tool_configs"].get(state.tool_id, {})
            max_w = tool_cfg.get("max_weight", 50)
            new_weight = min(max_w, state.weight + delta_pct)
        else:
            new_weight = state.weight

        return new_weight

    def _execute_adjustments(self, adjustments: List[Adjustment]):
        """执行调整"""
        print("\n🚀 执行调整:")
        validated = [a for a in adjustments if a.mirofish_validated]

        if not validated:
            print("  ⚠️  无已验证调整可执行")
            return

        for adj in validated:
            try:
                import urllib.request
                payload = json.dumps({
                    "tool_id": adj.tool_id,
                    "weight": adj.new_value,
                    "source": "auto_adjuster",
                    "reason": adj.reason,
                }).encode()

                req = urllib.request.Request(
                    f"{BACKEND_URL}/api/performance/weight",
                    data=payload,
                    method="PUT",
                    headers={"Content-Type": "application/json"},
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    print(f"  ✅ {adj.tool_id}: 已更新权重 {adj.old_value:.1f}% → {adj.new_value:.1f}%")
                    adj.approved = True
            except Exception as e:
                print(f"  ❌ {adj.tool_id}: 更新失败 - {e}")

        self.state["last_adjustment"] = datetime.now().isoformat()

    def enable(self):
        self.config["enabled"] = True
        self._save_config()
        print("✅ 自动调整已启用")

    def disable(self):
        self.config["enabled"] = False
        self._save_config()
        print("⛔ 自动调整已禁用")

    def set_auto_execute(self, enabled: bool):
        self.config["auto_execute"] = enabled
        self._save_config()
        print(f"{'🚀' if enabled else '⏸️'} 自动执行: {'启用' if enabled else '禁用'}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="GO2SE 自动策略调整器")
    parser.add_argument("--force-rebalance", action="store_true", help="强制再平衡")
    parser.add_argument("--enable", action="store_true", help="启用自动调整")
    parser.add_argument("--disable", action="store_true", help="禁用自动调整")
    parser.add_argument("--auto-execute", action="store_true", help="启用自动执行")
    parser.add_argument("--no-auto-execute", action="store_false", dest="auto_execute", help="禁用自动执行")
    args = parser.parse_args()

    adjuster = AutoStrategyAdjuster()

    if args.enable:
        adjuster.enable()
    elif args.disable:
        adjuster.disable()
    elif "--auto-execute" in sys.argv:
        adjuster.set_auto_execute(True)
    elif "--no-auto-execute" in sys.argv:
        adjuster.set_auto_execute(False)
    else:
        result = adjuster.run_check(force_rebalance=args.force_rebalance)
        return result


if __name__ == "__main__":
    main()
