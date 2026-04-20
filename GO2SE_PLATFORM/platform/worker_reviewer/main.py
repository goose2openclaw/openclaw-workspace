"""
GO2SE Worker/Reviewer 多Agent审查系统
Worker: 生成交易信号 / Reviewer: 审查信号质量
端口: 8031
"""
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import httpx, json, asyncio, random
from dataclasses import dataclass, field
from enum import Enum

app = FastAPI(title="GO2SE Worker/Reviewer System v1.0")

# ── 数据结构 ────────────────────────────────────────────────

class ReviewGrade(str):
    PASS = "PASS"       # 通过
    WARN = "WARN"       # 警告
    FAIL = "FAIL"       # 拒绝
    REVIEW = "REVIEW"   # 需人工复核

@dataclass
class ReviewResult:
    grade: str
    score: float          # 0-100
    issues: List[str]
    suggestions: List[str]
    risk_level: str      # LOW/MEDIUM/HIGH/CRITICAL
    iteration: int = 0
    worker_output: str = ""

@dataclass
class ReviewSession:
    session_id: str
    system: str           # vv6 / v15
    input_data: Dict
    worker_output: str = ""
    reviewer_result: Optional[ReviewResult] = None
    iterations: int = 0
    timestamp: str = ""
    approved: bool = False

sessions: Dict[str, ReviewSession] = {}
_session_counter = 0

def _new_id() -> str:
    global _session_counter
    _session_counter += 1
    return f"WR-{_session_counter:04d}"

# ── Worker: 交易信号生成 ──────────────────────────────────

class Worker:
    """Worker: 分析市场数据 + 生成交易信号"""

    async def generate(self, system: str, market_data: Dict, params: Dict) -> str:
        """生成交易信号建议"""
        if system == "vv6":
            return await self._vv6_worker(market_data, params)
        elif system == "v15":
            return await self._v15_worker(market_data, params)
        elif system == "v6i":
            return await self._v6i_worker(market_data, params)
        else:
            return await self._generic_worker(market_data, params)

    async def _vv6_worker(self, mkt: Dict, params: Dict) -> str:
        """vv6 Lobster Worker: 稳健做多"""
        fg = mkt.get("fear_greed_index", 50)
        trend = mkt.get("trend", "neutral")
        regime = "neutral"
        if fg < 40: regime = "bear"
        elif fg > 62: regime = "bull"

        sig = {
            "system": "vv6",
            "direction": "LONG" if regime != "bear" else "SHORT",
            "regime": regime,
            "confidence": params.get("confidence", 80),
            "mi": params.get("mi", 0.75),
            "reasoning": f"fear_greed={fg}, trend={trend}",
            "leverage": 3,
            "position_pct": 10,
        }

        if fg > params.get("fear_greed_short_threshold", 55):
            sig["direction"] = "SHORT"
            sig["reasoning"] = f"Greed Extreme SHORT: fear_greed={fg}>55"
        elif fg < params.get("fear_greed_long_threshold", 35):
            sig["direction"] = "LONG"
            sig["reasoning"] = f"Fear Extreme LONG: fear_greed={fg}<35"

        return json.dumps(sig, ensure_ascii=False)

    async def _v6i_worker(self, mkt: Dict, params: Dict) -> str:
        """v6i Expert Worker: 多空切换"""
        fg = mkt.get("fear_greed_index", 50)
        rsi = params.get("rsi", 60)
        regime = "neutral"
        if fg < 40: regime = "bear"
        elif fg > 62: regime = "bull"

        sig = {
            "system": "v6i",
            "direction": "HOLD",
            "regime": regime,
            "confidence": params.get("confidence", 80),
            "mi": params.get("mi", 0.75),
        }

        if rsi > params.get("rsi_short_threshold", 75):
            sig["direction"] = "SHORT"
            sig["reasoning"] = f"RSI Extreme SHORT: RSI={rsi}>75"
        elif rsi < params.get("rsi_long_threshold", 28):
            sig["direction"] = "LONG"
            sig["reasoning"] = f"RSI Extreme LONG: RSI={rsi}<28"
        elif regime == "bear" and fg > 55:
            sig["direction"] = "SHORT"
            sig["reasoning"] = f"Bear market + greed={fg}"
        elif regime == "bull":
            sig["direction"] = "LONG"
            sig["reasoning"] = f"Bull market, confidence={params.get('confidence', 80)}"

        return json.dumps(sig, ensure_ascii=False)

    async def _v15_worker(self, mkt: Dict, params: Dict) -> str:
        """v15 四脑Worker: 复杂信号"""
        fg = mkt.get("fear_greed_index", 50)
        rsi = params.get("rsi", 60)
        brains = params.get("brain_votes", {"alpha": 0.85, "beta": 0.80, "gamma": 0.70, "delta": 0.60})

        regime = "bull" if fg > 62 else ("bear" if fg < 40 else "neutral")
        avg_brain = sum(brains.values()) / len(brains)

        sig = {
            "system": "v15",
            "direction": "HOLD",
            "regime": regime,
            "rsi": rsi,
            "brain_avg": round(avg_brain, 3),
            "mi": params.get("mi", 0.75),
        }

        if rsi > 75:
            sig["direction"] = "SHORT"
            sig["reasoning"] = f"RSI Extreme SHORT: RSI={rsi}>75"
        elif rsi < 28:
            sig["direction"] = "LONG"
            sig["reasoning"] = f"RSI Extreme LONG: RSI={rsi}<28"
        elif avg_brain > params.get("threshold_long", 0.35):
            sig["direction"] = "LONG"
            sig["reasoning"] = f"Brain avg={avg_brain:.3f} > threshold"
        elif avg_brain < params.get("threshold_short", 0.30):
            sig["direction"] = "SHORT"
            sig["reasoning"] = f"Brain avg={avg_brain:.3f} < short threshold"

        return json.dumps(sig, ensure_ascii=False)

    async def _generic_worker(self, mkt: Dict, params: Dict) -> str:
        fg = mkt.get("fear_greed_index", 50)
        sig = {
            "system": "generic",
            "direction": "HOLD",
            "regime": "neutral" if 35 <= fg <= 65 else ("bear" if fg < 35 else "bull"),
            "confidence": params.get("confidence", 75),
            "mi": params.get("mi", 0.75),
            "reasoning": f"fear_greed={fg}",
        }
        if fg > 60: sig["direction"] = "SHORT"
        elif fg < 40: sig["direction"] = "LONG"
        return json.dumps(sig, ensure_ascii=False)


# ── Reviewer: 信号审查 ──────────────────────────────────

class Reviewer:
    """Reviewer: 多维度审查Worker输出"""

    async def review(self, worker_output: str, system: str, market_data: Dict) -> ReviewResult:
        """审查信号并返回审查结果"""
        try:
            sig = json.loads(worker_output)
        except:
            return ReviewResult(
                grade=ReviewGrade.FAIL,
                score=0,
                issues=["Worker输出格式无效"],
                suggestions=["返回有效的JSON格式"],
                risk_level="CRITICAL"
            )

        issues, suggestions, score_deductions = [], [], 0

        # 1. 信号完整性检查
        required = ["direction", "regime", "confidence"]
        for f in required:
            if f not in sig:
                issues.append(f"缺少字段: {f}")
                score_deductions += 15

        # 2. 方向合法性
        direction = sig.get("direction", "HOLD")
        if direction not in ["LONG", "SHORT", "HOLD"]:
            issues.append(f"非法方向: {direction}")
            score_deductions += 20

        # 3. 置信度合理性
        conf = sig.get("confidence", 0)
        if not (20 <= conf <= 100):
            issues.append(f"置信度异常: {conf}")
            score_deductions += 10
        elif conf > 95:
            suggestions.append("置信度>95%可能是过拟合信号")

        # 4. regime/direction一致性
        regime = sig.get("regime", "neutral")
        if regime == "bear" and direction == "LONG":
            issues.append(f"⚠️ 熊市做多风险: regime={regime}, direction={direction}")
            score_deductions += 15
        if regime == "bull" and direction == "SHORT":
            issues.append(f"⚠️ 牛市做空风险: regime={regime}, direction={direction}")
            score_deductions += 15

        # 5. RSI一致性（如果提供）
        rsi = sig.get("rsi", None) or market_data.get("rsi", None)
        if rsi:
            if rsi > 80 and direction == "LONG":
                issues.append(f"⚠️ RSI极度超买({rsi}>80)仍做多")
                score_deductions += 20
            if rsi < 25 and direction == "SHORT":
                issues.append(f"⚠️ RSI极度超卖({rsi}<25)仍做空")
                score_deductions += 20

        # 6. Mi合理性
        mi = sig.get("mi", 0)
        if not (0.3 <= mi <= 1.0):
            issues.append(f"Mi异常: {mi}")
            score_deductions += 10

        # 7. 理由充分性
        reason = sig.get("reasoning", "")
        if len(reason) < 5 and direction != "HOLD":
            suggestions.append("信号理由过于简单，建议补充分析依据")
            score_deductions += 5

        # 计算最终分数
        score = max(0, 100 - score_deductions)

        # 评级
        if score >= 85 and not any("⚠️" in i for i in issues):
            grade = ReviewGrade.PASS
            risk = "LOW"
        elif score >= 60:
            grade = ReviewGrade.WARN
            risk = "MEDIUM"
        elif score >= 30:
            grade = ReviewGrade.FAIL
            risk = "HIGH"
        else:
            grade = ReviewGrade.FAIL
            risk = "CRITICAL"

        return ReviewResult(
            grade=grade,
            score=score,
            issues=issues,
            suggestions=suggestions,
            risk_level=risk,
            worker_output=worker_output,
        )

    async def review_with_fix(self, worker_output: str, system: str, market_data: Dict) -> Tuple[ReviewResult, str]:
        """审查 + 自动修复WARN级别问题"""
        result = await self.review(worker_output, system, market_data)
        if result.grade == ReviewGrade.WARN:
            # 自动修复
            try:
                sig = json.loads(worker_output)
                for issue in result.issues:
                    if "⚠️ RSI极度超买" in issue and sig.get("direction") == "LONG":
                        sig["direction"] = "HOLD"
                        sig["reasoning"] = (sig.get("reasoning") or "") + " [Reviewer:auto HOLD]"
                    if "⚠️ 熊市做多" in issue and sig.get("direction") == "LONG":
                        sig["direction"] = "HOLD"
                        sig["reasoning"] = (sig.get("reasoning") or "") + " [Reviewer:auto HOLD]"
                fixed_output = json.dumps(sig, ensure_ascii=False)
                result.grade = ReviewGrade.PASS
                result.score = min(100, result.score + 15)
                result.suggestions.append("Reviewer已自动修复WARN")
                return result, fixed_output
            except:
                pass
        return result, worker_output


# ── Worker/Reviewer 循环 ──────────────────────────────────

async def worker_reviewer_loop(
    system: str,
    market_data: Dict,
    params: Dict,
    max_iterations: int = 3
) -> Tuple[str, ReviewResult, int]:
    """
    执行Worker→Reviewer循环
    直到Reviewer通过或达到最大迭代次数
    """
    worker = Worker()
    reviewer = Reviewer()
    output = ""
    result = None

    for i in range(max_iterations):
        # Worker生成
        output = await worker.generate(system, market_data, params)

        # Reviewer审查
        result, fixed_output = await reviewer.review_with_fix(output, system, market_data)
        output = fixed_output

        if result.grade in [ReviewGrade.PASS, ReviewGrade.REVIEW]:
            break

    return output, result, i + 1


# ── API端点 ────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    system: str          # vv6 / v15 / v6i / generic
    market_data: Dict    # fear_greed_index, trend, rsi等
    params: Dict = {}    # 决策参数

class QuickReviewRequest(BaseModel):
    worker_output: str
    system: str
    market_data: Dict = {}

@app.get("/health")
def health(): return {"status": "worker_reviewer", "sessions": len(sessions)}

@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    """
    Worker/Reviewer配对分析
    自动迭代直到信号通过审查
    """
    session_id = _new_id()
    market = req.market_data or await _fetch_market()

    output, result, iters = await worker_reviewer_loop(
        req.system, market, req.params
    )

    session = ReviewSession(
        session_id=session_id,
        system=req.system,
        input_data={"market": market, "params": req.params},
        worker_output=output,
        reviewer_result=result,
        iterations=iters,
        timestamp=datetime.now().isoformat(),
        approved=result.grade == ReviewGrade.PASS if result else False,
    )
    sessions[session_id] = session

    return {
        "session_id": session_id,
        "system": req.system,
        "direction": json.loads(output).get("direction", "HOLD") if output else "HOLD",
        "grade": result.grade if result else "UNKNOWN",
        "score": result.score if result else 0,
        "issues": result.issues if result else [],
        "iterations": iters,
        "approved": result.grade == ReviewGrade.PASS if result else False,
        "signal": json.loads(output) if output else {},
    }

@app.post("/review")
async def quick_review(req: QuickReviewRequest):
    """快速审查已生成的信号"""
    reviewer = Reviewer()
    result, fixed = await reviewer.review_with_fix(
        req.worker_output, req.system, req.market_data
    )
    return {
        "grade": result.grade,
        "score": result.score,
        "issues": result.issues,
        "suggestions": result.suggestions,
        "risk_level": result.risk_level,
        "fixed_signal": json.loads(fixed) if fixed != req.worker_output else None,
        "auto_fixed": fixed != req.worker_output,
    }

@app.get("/sessions")
def list_sessions(limit: int = 20):
    """最近的审查会话"""
    return list(sessions.values())[-limit:]

@app.get("/sessions/{session_id}")
def get_session(session_id: str):
    if session_id not in sessions:
        raise HTTPException(404, "Session not found")
    s = sessions[session_id]
    return {
        "session_id": s.session_id,
        "system": s.system,
        "iterations": s.iterations,
        "approved": s.approved,
        "grade": s.reviewer_result.grade if s.reviewer_result else "UNKNOWN",
        "score": s.reviewer_result.score if s.reviewer_result else 0,
        "worker_output": s.worker_output,
        "timestamp": s.timestamp,
    }

async def _fetch_market() -> Dict:
    try:
        async with httpx.AsyncClient(timeout=5) as c:
            r = await c.get("http://localhost:8000/api/v7/market/summary")
            return r.json().get("data", {}) if r.status_code == 200 else {}
    except:
        return {}

