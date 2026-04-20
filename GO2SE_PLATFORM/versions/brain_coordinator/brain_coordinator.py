"""
BRAIN COORDINATOR - 综合左右脑 + Lobster/Hermes 自主切换架构

架构层级:
┌─────────────────────────────────────────────────────────┐
│            LAYER 3: Brain Coordinator (协调层)            │
│   监控 v6i + vv6 + v15 四脑，决定激活哪个脑               │
├─────────────────────────────────────────────────────────┤
│          LAYER 2: v6i / vv6 自主引擎 (执行层)            │
│   v6i=专家模式(Hermes) | vv6=普通模式(Lobster)          │
├─────────────────────────────────────────────────────────┤
│           LAYER 1: v15 Quad-Brain (决策层)              │
│     Alpha(左脑/保守) | Beta(右脑/激进)                   │
│     Gamma(动态) | Delta(模拟)                            │
└─────────────────────────────────────────────────────────┘

切换逻辑:
1. Coordinator 轮询 v6i + vv6 的市场分析
2. 对比 Herms(v6i) vs Lobster(vv6) 的信号差异
3. 根据差异强度决定: 激活哪个引擎 或 启用v15四脑仲裁
4. v15四脑投票权重由 adaptive-weights 动态调整

工作模式:
- AUTO_MODE: Coordinator 完全自主决策
- SEMI_MODE: 提议切换，等待人类确认
- MANUAL_MODE: 人类完全控制
"""

import asyncio
import httpx
import time
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

class BrainMode(Enum):
    NORMAL = "normal"       # 左脑/Lobster/vv6
    EXPERT = "expert"       # 右脑/Hermes/v6i
    QUAD = "quad"           # v15四脑仲裁
    HYBRID = "hybrid"       # v6i + vv6 联合

class SwitchDecision(Enum):
    ACTIVATE_HERMES = "hermes"    # 激活 v6i 专家模式
    ACTIVATE_LOBSTER = "lobster"  # 激活 vv6 普通模式
    ACTIVATE_QUAD = "quad"        # 启用 v15 四脑仲裁
    HOLD = "hold"                 # 保持当前

@dataclass
class BrainSignal:
    brain: str
    direction: str
    confidence: float
    regime: str
    leverage: int
    position_pct: float
    reasoning: str
    timestamp: str = ""

@dataclass
class SwitchResult:
    decision: SwitchDecision
    hermes_signal: Optional[BrainSignal] = None
    lobster_signal: Optional[BrainSignal] = None
    quad_signal: Optional[BrainSignal] = None
    confidence_diff: float = 0.0
    recommended_brain: str = ""
    reasoning: str = ""
    timestamp: str = ""
    active_engine: str = ""

class BrainCoordinator:
    """
    左右脑协调器 - 综合架构核心
    
    职责:
    1. 并行查询 v6i(Hermes) + vv6(Lobster) + v15(QuadBrain)
    2. 对比三方信号，计算置信度差异
    3. 自主决定激活哪个引擎
    4. 记录所有切换决策到历史
    """

    PORTS = {
        "hermes": 8001,   # v6i - Hermes/专家
        "lobster": 8006,  # vv6 - Lobster/普通
        "quad": 8015,     # v15 - 四脑系统
    }

    def __init__(self, mode: str = "AUTO"):
        self.mode = mode
        self.history: List[SwitchResult] = []
        self.current_brain = "hermes"
        self.current_mode = "normal"
        self.hold_count = 0
        self.switch_count = 0
        self.last_switch_time = 0
        self.min_switch_interval = 300  # 5分钟最小切换间隔
        self.confidence_threshold = 10.0  # 置信度差异阈值
        self.adaptive_weights = {
            "alpha": 0.25,
            "beta": 0.25,
            "gamma": 0.25,
            "delta": 0.25,
        }

    async def fetch_signal(self, brain: str, symbol: str = "BTCUSDT") -> Optional[BrainSignal]:
        """从指定脑获取信号"""
        port = self.PORTS[brain]
        url = f"http://localhost:{port}/api/switch/analyze"
        headers = {"Content-Type": "application/json"}
        payload = {
            "symbol": symbol,
            "confidence": 75,
            "regime": "bull",
            "rsi": 55,
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, json=payload, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    sig = data.get("signal", {})
                    return BrainSignal(
                        brain=brain,
                        direction=sig.get("direction", "hold"),
                        confidence=sig.get("confidence", 0),
                        regime=sig.get("regime", "neutral"),
                        leverage=sig.get("leverage", 1),
                        position_pct=sig.get("position_pct", 0),
                        reasoning=sig.get("reason", ""),
                        timestamp=sig.get("timestamp", ""),
                    )
        except Exception as e:
            print(f"[{brain}] fetch failed: {e}")
        return None

    async def fetch_quad_signal(self, symbol: str = "BTCUSDT") -> Optional[BrainSignal]:
        """从v15四脑系统获取综合信号"""
        qport = self.PORTS["quad"]
        url = f"http://localhost:{qport}/api/brains/think"
        headers = {"Content-Type": "application/json"}
        payload = {"symbol": symbol, "regime": "bull", "rsi": 55}
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(url, json=payload, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    sig = data.get("signal", {})
                    return BrainSignal(
                        brain="quad",
                        direction=sig.get("direction", "hold"),
                        confidence=sig.get("confidence", 0),
                        regime=sig.get("regime", "neutral"),
                        leverage=sig.get("leverage", 1),
                        position_pct=sig.get("position_pct", 0),
                        reasoning=sig.get("reason", ""),
                        timestamp=sig.get("timestamp", ""),
                    )
        except Exception as e:
            print(f"[quad] fetch failed: {e}")
        return None

    def decide(self, hermes: Optional[BrainSignal], lobster: Optional[BrainSignal],
               quad: Optional[BrainSignal]) -> SwitchResult:
        """基于三方信号做出切换决策"""
        now = time.time()
        ts = datetime.now().isoformat()

        if not hermes and not lobster:
            return SwitchResult(
                decision=SwitchDecision.HOLD,
                recommended_brain="hermes",
                reasoning="no signals available, default to hermes",
                timestamp=ts,
                active_engine=self.current_brain,
            )

        # 计算置信度差异
        h_conf = hermes.confidence if hermes else 0
        l_conf = lobster.confidence if lobster else 0
        q_conf = quad.confidence if quad else 0
        diff = abs(h_conf - l_conf)
        avg_conf = (h_conf + l_conf + q_conf) / 3 if all([hermes, lobster, quad]) else (h_conf + l_conf) / 2

        # 方向一致性分析
        directions = [s.direction.upper() for s in [hermes, lobster, quad] if s]
        all_same = len(set(directions)) == 1 if directions else False
        h_l_agree = hermes and lobster and hermes.direction.upper() == lobster.direction.upper()

        # 切换冷却检查
        cooldown_ok = (now - self.last_switch_time) > self.min_switch_interval
        self.hold_count += 1

        # 决策树
        decision = SwitchDecision.HOLD
        recommended = self.current_brain
        reasoning = ""

        if not cooldown_ok:
            reasoning = f"cooldown active ({self.min_switch_interval}s min), hold"
            decision = SwitchDecision.HOLD
        elif all_same and avg_conf > 70:
            # 三方一致，看好方向
            if hermes.direction.upper() == "LONG":
                decision = SwitchDecision.ACTIVATE_HERMES
                recommended = "hermes"
                reasoning = f"三方一致做多(avg_conf={avg_conf:.1f}%), 激活Hermes专家模式"
            elif hermes.direction.upper() == "SHORT":
                decision = SwitchDecision.ACTIVATE_LOBSTER
                recommended = "lobster"
                reasoning = f"三方一致做空(avg_conf={avg_conf:.1f}%), 激活Lobster普通模式"
            else:
                decision = SwitchDecision.HOLD
                recommended = self.current_brain
                reasoning = "三方一致观望"
        elif diff >= self.confidence_threshold:
            # 差异足够大，选择置信度更高的
            if h_conf > l_conf:
                decision = SwitchDecision.ACTIVATE_HERMES
                recommended = "hermes"
                reasoning = f"Hermes置信度更高({h_conf:.1f}% vs {l_conf:.1f}%), 切换至专家模式"
            else:
                decision = SwitchDecision.ACTIVATE_LOBSTER
                recommended = "lobster"
                reasoning = f"Lobster置信度更高({l_conf:.1f}% vs {h_conf:.1f}%), 保持普通模式"
        elif quad and q_conf > max(h_conf, l_conf) + 5:
            # v15四脑信号最强，启用仲裁
            decision = SwitchDecision.ACTIVATE_QUAD
            recommended = "quad"
            reasoning = f"Quad四脑信号最强({q_conf:.1f}%), 启用v15仲裁"
        else:
            # 差异不够大，保持当前
            reasoning = f"置信度差异不足(diff={diff:.1f}% < {self.confidence_threshold}%), 保持{self.current_brain}"
            decision = SwitchDecision.HOLD
            recommended = self.current_brain

        result = SwitchResult(
            decision=decision,
            hermes_signal=hermes,
            lobster_signal=lobster,
            quad_signal=quad,
            confidence_diff=diff,
            recommended_brain=recommended,
            reasoning=reasoning,
            timestamp=ts,
            active_engine=self.current_brain,
        )

        # 执行切换
        if decision != SwitchDecision.HOLD and recommended != self.current_brain and cooldown_ok:
            self.current_brain = recommended
            self.switch_count += 1
            self.last_switch_time = now
            self.hold_count = 0
            result.active_engine = recommended
        else:
            result.active_engine = self.current_brain

        self.history.append(result)
        return result

    async def switch_engine(self, target: str) -> dict:
        """实际执行引擎切换"""
        if target == "hermes":
            port = self.PORTS["hermes"]
            url = f"http://localhost:{port}/api/switch/mode?mode=expert"
        elif target == "lobster":
            port = self.PORTS["lobster"]
            url = f"http://localhost:{port}/api/switch/mode?mode=normal"
        else:
            return {"status": "no_switch_needed", "target": target}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url)
                if resp.status_code == 200:
                    return {"status": "switched", "target": target, "response": resp.json()}
        except Exception as e:
            return {"status": "error", "target": target, "error": str(e)}
        return {"status": "failed", "target": target}

    async def run_cycle(self, symbol: str = "BTCUSDT") -> SwitchResult:
        """运行一个完整的协调周期"""
        # 并行获取三方信号
        hermes, lobster, quad = await asyncio.gather(
            self.fetch_signal("hermes", symbol),
            self.fetch_signal("lobster", symbol),
            self.fetch_quad_signal(symbol),
        )

        # 做出决策
        result = self.decide(hermes, lobster, quad)

        # 如果需要切换，执行切换
        if result.decision != SwitchDecision.HOLD and result.recommended_brain != self.current_brain:
            switch_result = await self.switch_engine(result.recommended_brain)
            result.reasoning += f" | 切换结果: {switch_result.get('status')}"

        return result

    def get_status(self) -> dict:
        """获取协调器当前状态"""
        return {
            "mode": self.mode,
            "current_brain": self.current_brain,
            "switch_count": self.switch_count,
            "hold_count": self.hold_count,
            "last_switch_time": self.last_switch_time,
            "confidence_threshold": self.confidence_threshold,
            "adaptive_weights": self.adaptive_weights,
            "history_len": len(self.history),
            "ports": self.PORTS,
        }

    def print_result(self, r: SwitchResult):
        """打印决策结果"""
        emoji = {
            "hermes": "🦐",
            "lobster": "🦞",
            "quad": "🧠",
            "hold": "⏸️",
        }.get(r.decision.value, "❓")
        print(f"{emoji} [{r.timestamp[:19]}] Decision: {r.decision.value}")
        print(f"   Reasoning: {r.reasoning}")
        if r.hermes_signal:
            print(f"   🦐 Hermes: {r.hermes_signal.direction} conf={r.hermes_signal.confidence:.1f}% lev={r.hermes_signal.leverage}x")
        if r.lobster_signal:
            print(f"   🦞 Lobster: {r.lobster_signal.direction} conf={r.lobster_signal.confidence:.1f}% lev={r.lobster_signal.leverage}x")
        if r.quad_signal:
            print(f"   🧠 Quad: {r.quad_signal.direction} conf={r.quad_signal.confidence:.1f}% lev={r.quad_signal.leverage}x")
        print(f"   → Active Engine: {r.active_engine} (confidence_diff={r.confidence_diff:.1f}%)")

async def main():
    coordinator = BrainCoordinator(mode="AUTO")
    print("=" * 72)
    print("  BRAIN COORDINATOR - 左右脑 + Lobster/Hermes 综合架构测试")
    print("=" * 72)
    print()
    print("状态:", coordinator.get_status())
    print()
    print("Running 3 decision cycles...")
    print()
    for i in range(3):
        print(f"--- Cycle {i+1} ---")
        result = await coordinator.run_cycle("BTCUSDT")
        coordinator.print_result(result)
        print()
        if i < 2:
            await asyncio.sleep(2)

    print("=" * 72)
    print("  FINAL STATUS")
    print("=" * 72)
    status = coordinator.get_status()
    for k, v in status.items():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    asyncio.run(main())