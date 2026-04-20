#!/usr/bin/env python3
"""
🪿 GO2SE v6i - OpenAI Agents 驱动版 + 自主多空切换
=====================================================
• 普通模式: 仅做多
• 专家模式: 做多/做空/观望 自动切换
• 严格风控: 杠杆档位 + 动态止损 + 仓位控制
"""

import os
import json
import logging
import urllib.request
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from fastapi import FastAPI
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings
from pydantic import BaseModel as PydanticBaseModel

# ─── MiroFish Platform Client ─────────────────────────────────────
from mirofish_client import MiroFishClient

_mf_client = None
def get_mf() -> MiroFishClient:
    global _mf_client
    if _mf_client is None:
        _mf_client = MiroFishClient(strategy_name="v6i")
    return _mf_client


# ─── 配置 ─────────────────────────────────────────────────
class Settings(BaseSettings):
    APP_NAME: str = "GO2SE v6i OpenAI Agents"
    APP_VERSION: str = "v6i-openai-agents"
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    PORT: int = 8001

settings = Settings()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s"
)
logger = logging.getLogger("go2se_v6i")

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)
ALLOWED_ORIGINS = [
    "http://localhost:8000", "http://localhost:8001",
    "http://localhost:8004", "http://localhost:8006",
    "http://localhost:8015",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ─── 多空方向枚举 ──────────────────────────────────────────
class TradeDirection(str, Enum):
    LONG = "long"       # 做多
    SHORT = "short"     # 做空
    HOLD = "hold"       # 观望
    CLOSE_LONG = "close_long"
    CLOSE_SHORT = "close_short"

class MarketRegime(str, Enum):
    BULL = "bull"        # 牛市
    BEAR = "bear"        # 熊市
    NEUTRAL = "neutral"  # 中性
    VOLATILE = "volatile" # 剧烈波动

# ─── 杠杆档位 ─────────────────────────────────────────────
LEVERAGE_TIERS = {
    "conservative": {"leverage": 2,  "max_position_pct": 30, "stop_loss_pct": 5.0, "take_profit_pct": 10.0, "desc": "保守"},
    "moderate":    {"leverage": 3,  "max_position_pct": 20, "stop_loss_pct": 4.0, "take_profit_pct": 12.0, "desc": "适度"},
    "aggressive":  {"leverage": 5,  "max_position_pct": 10, "stop_loss_pct": 3.0, "take_profit_pct": 15.0, "desc": "激进"},
    "expert":      {"leverage": 10, "max_position_pct": 5,  "stop_loss_pct": 2.0, "take_profit_pct": 20.0, "desc": "专家"},
}

# ─── 风控配置 ─────────────────────────────────────────────
RISK_CONFIG = {
    "max_position_pct": 60,      # 最大总仓位 60%
    "max_single_loss_pct": 5,    # 单笔最大亏损 5%
    "daily_loss_limit_pct": 15,  # 日内熔断 15%
    "max_drawdown_pct": 25,      # 最大回撤 25%
    "min_confidence_long": 65,    # 做多最低置信度
    "min_confidence_short": 75,   # 做空最低置信度（更严格）
    "min_confidence_expert_short": 80,  # 专家做空置信度
    "cooldown_minutes": 5,   # 专家模式冷却5分钟（适合日内交易）      # 方向切换冷却
    "max_trades_per_day": 50,    # 日内最大交易次数
}

@dataclass
class TradingSignal:
    """交易信号"""
    symbol: str
    direction: TradeDirection
    confidence: float        # 0-100
    reason: str
    regime: MarketRegime
    leverage_tier: str = "moderate"
    position_pct: float = 10.0
    stop_loss_pct: float = 4.0
    take_profit_pct: float = 8.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    mode: str = "normal"    # normal / expert

# ─── 多空自主切换引擎 ─────────────────────────────────────
class AutonomousSwitchEngine:
    """
    自主多空切换引擎
    ==================
    普通模式: 仅做多，置信度 > 65 分执行
    专家模式: 做多/做空/观望 自动判断
    """

    def __init__(self):
        self.last_direction: Optional[TradeDirection] = None
        self.last_switch_time: Optional[datetime] = None
        self.daily_trades: int = 0
        self.daily_pnl: float = 0.0
        self.daily_loss: float = 0.0
        self.current_regime: MarketRegime = MarketRegime.NEUTRAL
        self.mode: str = "normal"  # normal / expert
        self.trade_history: list = []

    def reset_daily(self):
        self.daily_trades = 0
        self.daily_pnl = 0.0
        self.daily_loss = 0.0
        self.last_reset_date = datetime.now().date()

    def check_daily_reset(self):
        today = datetime.now().date()
        if getattr(self, 'last_reset_date', None) != today:
            self.reset_daily()
            logger.info(f"🗓️ v6i日计数器已重置 ({today})")

    def detect_regime(self, symbol: str = "BTC/USDT") -> MarketRegime:
        """检测市场状态 - 优先/api/v7/market/summary，fallback md5哈希"""
        import hashlib, time as _time
        try:
            # 优先使用 /api/v7/market/summary（唯一可用的市场数据）
            url = "http://localhost:8000/api/v7/market/summary"
            with urllib.request.urlopen(url, timeout=3) as resp:
                data = json.loads(resp.read())
            fg = float(data.get("data", {}).get("fear_greed_index", 50))
            trend = data.get("data", {}).get("trend", "neutral")
            # fear_greed: <40=BEAR, >62=BULL (修复:原<25/>75太保守)
            if fg < 40:
                return MarketRegime.BEAR
            elif fg > 62:
                return MarketRegime.BULL
            elif fg < 35 or fg > 70:
                return MarketRegime.VOLATILE
            # 40-62: 用trend二次判断
            if trend in ("bearish", "down"):
                return MarketRegime.BEAR
            elif trend in ("bullish", "up"):
                return MarketRegime.BULL
            else:
                return MarketRegime.NEUTRAL
        except Exception:
            # Fallback: 本地确定性哈希（仅用于降级）
            block = int(_time.time()) // 900
            h = hashlib.md5(f"{symbol}_{block}".encode()).hexdigest()
            rsi = int(h[:4], 16) % 100
            if rsi > 75: return MarketRegime.BEAR
            elif rsi < 30: return MarketRegime.BULL
            elif rsi > 65: return MarketRegime.VOLATILE
            else: return MarketRegime.NEUTRAL

    def calculate_leverage(self, confidence: float, regime: MarketRegime) -> Dict:
        """计算杠杆档位"""
        if confidence >= 90:
            tier = "expert"
        elif confidence >= 80:
            tier = "aggressive"
        elif confidence >= 70:
            tier = "moderate"
        else:
            tier = "conservative"

        # 波动市场降低杠杆
        if regime in [MarketRegime.VOLATILE, MarketRegime.BEAR]:
            tier = "moderate" if tier == "expert" else "conservative"

        return {**LEVERAGE_TIERS[tier], "tier": tier}

    def analyze(self, symbol: str, confidence: float, regime: MarketRegime,
                mode: str = "normal") -> TradingSignal:
        """
        核心分析: 自主判断做多/做空/观望
        """
        self.current_regime = regime
        self.mode = mode

        # ── 风控检查 ──
        if self.daily_loss >= RISK_CONFIG["daily_loss_limit_pct"]:
            return TradingSignal(
                symbol=symbol, direction=TradeDirection.HOLD,
                confidence=0, reason="⚠️ 日内损失已达15%熔断线，停止交易",
                regime=regime, mode=mode
            )

        if self.daily_trades >= RISK_CONFIG["max_trades_per_day"]:
            return TradingSignal(
                symbol=symbol, direction=TradeDirection.HOLD,
                confidence=0, reason=f"⚠️ 今日交易次数已达{RISK_CONFIG['max_trades_per_day']}次上限",
                regime=regime, mode=mode
            )

        # ── 普通模式: 仅做多 ──
        if mode == "normal":
            if confidence >= RISK_CONFIG["min_confidence_long"]:
                lev = self.calculate_leverage(confidence, regime)
                return TradingSignal(
                    symbol=symbol, direction=TradeDirection.LONG,
                    confidence=confidence,
                    reason=f"✅ 普通模式做多，置信度 {confidence} 分",
                    regime=regime, leverage_tier=lev["tier"],
                    position_pct=lev["max_position_pct"],
                    stop_loss_pct=lev["stop_loss_pct"],
                    take_profit_pct=lev["take_profit_pct"],
                    mode="normal"
                )
            else:
                return TradingSignal(
                    symbol=symbol, direction=TradeDirection.HOLD,
                    confidence=confidence,
                    reason=f"⏸️ 置信度 {confidence} < {RISK_CONFIG['min_confidence_long']}，观望",
                    regime=regime, mode="normal"
                )

        # ── 专家模式: 做多/做空/观望 ──
        # 注意: cooldown改为基于时间戳，不再基于方向切换
        # (保留时间戳记录用于监控，但不阻止正常交易)
        # ── 多空判断 ──
        short_threshold = (RISK_CONFIG["min_confidence_expert_short"]
                          if mode == "expert" else RISK_CONFIG["min_confidence_short"])

        # 熊市/超买 → 做空优先
        if regime in [MarketRegime.BEAR, MarketRegime.VOLATILE]:
            if confidence >= short_threshold:
                lev = self.calculate_leverage(confidence, regime)
                lev["leverage"] = min(lev["leverage"], 3)  # 熊市最高3倍杠杆
                return TradingSignal(
                    symbol=symbol, direction=TradeDirection.SHORT,
                    confidence=confidence,
                    reason=f"🐻 专家模式做空，熊市+置信度 {confidence} 分",
                    regime=regime, leverage_tier=lev["tier"],
                    position_pct=lev["max_position_pct"],
                    stop_loss_pct=lev["stop_loss_pct"],
                    take_profit_pct=lev["take_profit_pct"],
                    mode="expert"
                )

        # 牛市/超卖 → 做多优先
        if regime in [MarketRegime.BULL, MarketRegime.NEUTRAL]:
            if confidence >= RISK_CONFIG["min_confidence_long"]:
                lev = self.calculate_leverage(confidence, regime)
                return TradingSignal(
                    symbol=symbol, direction=TradeDirection.LONG,
                    confidence=confidence,
                    reason=f"🐂 专家模式做多，牛市+置信度 {confidence} 分",
                    regime=regime, leverage_tier=lev["tier"],
                    position_pct=lev["max_position_pct"],
                    stop_loss_pct=lev["stop_loss_pct"],
                    take_profit_pct=lev["take_profit_pct"],
                    mode="expert"
                )

        # 默认观望
        return TradingSignal(
            symbol=symbol, direction=TradeDirection.HOLD,
            confidence=confidence,
            reason=f"⏸️ 置信度不足，观望（mode={mode}）",
            regime=regime, mode=mode
        )

    def record_trade(self, signal: TradingSignal, result_pnl: float = 0.0):
        """记录交易"""
        self.last_direction = signal.direction
        self.last_switch_time = datetime.now()
        self.daily_trades += 1
        self.daily_pnl += result_pnl
        if result_pnl < 0:
            self.daily_loss += abs(result_pnl)
        self.trade_history.append({
            "symbol": signal.symbol,
            "direction": signal.direction.value,
            "confidence": signal.confidence,
            "leverage": LEVERAGE_TIERS[signal.leverage_tier]["leverage"],
            "pnl": result_pnl,
            "timestamp": signal.timestamp
        })

# ─── 全局引擎实例 ─────────────────────────────────────────
switch_engine = AutonomousSwitchEngine()

# ─── OpenAI Agents ────────────────────────────────────────
from agents import Agent, Runner, function_tool

@function_tool
def get_market_data(symbol: str) -> str:
    """获取市场实时数据"""
    try:
        url = f"http://localhost:8000/api/market/{symbol.replace('/', '')}"
        with urllib.request.urlopen(url, timeout=2) as resp:
            data = json.loads(resp.read())
            return json.dumps(data)
    except urllib.error.HTTPError as e:
        logger.warning(f"[v6i get_market_data] HTTP {e.code}")
        return json.dumps({"error": "upstream_http_error", "code": e.code, "fallback": True})
    except urllib.error.URLError as e:
        logger.warning(f"[v6i get_market_data] Network: {e.reason}")
        return json.dumps({"error": "network_error", "fallback": True})
    except json.JSONDecodeError:
        logger.error(f"[v6i get_market_data] Invalid JSON")
        return json.dumps({"error": "parse_error", "fallback": True})
    except Exception as e:
        logger.exception(f"[v6i get_market_data] Unexpected: {e}")
        return json.dumps({"error": str(e), "fallback": True})

@function_tool
def get_position(symbol: str) -> str:
    """获取当前持仓"""
    try:
        url = "http://localhost:8000/api/positions"
        with urllib.request.urlopen(url, timeout=2) as resp:
            data = json.loads(resp.read())
            for p in data.get("positions", []):
                if p.get("symbol") == symbol:
                    return json.dumps(p)
            return f"{symbol} 无持仓"
    except urllib.error.HTTPError as e:
        logger.warning(f"[v6i get_position] HTTP {e.code}")
        return json.dumps({"symbol": symbol, "error": "upstream_error", "position": 0})
    except urllib.error.URLError:
        logger.warning(f"[v6i get_position] Network error")
        return json.dumps({"symbol": symbol, "error": "network_error", "position": 0})
    except Exception as e:
        logger.exception(f"[v6i get_position] Unexpected: {e}")
        return json.dumps({"symbol": symbol, "error": str(e), "position": 0})

@function_tool
def execute_trade(symbol: str, direction: str, position_pct: float, stop_loss_pct: float, leverage: int) -> str:
    """【模拟模式】仅记录信号，不执行真实订单"""
    result = {
        "simulated": True,
        "direction": direction.upper(),
        "symbol": symbol, "position_pct": position_pct,
        "leverage": leverage, "stop_loss_pct": stop_loss_pct,
        "timestamp": datetime.now().isoformat(),
        "note": "MOCK - 无真实订单执行"
    }
    logger.warning(f"[MOCK TRADE] {direction.upper()} {symbol} {position_pct}% {leverage}x")
    return json.dumps(result)

# ─── 7工具 Agent ─────────────────────────────────────────
def create_tool_agent(tool_name: str, tool_icon: str, description: str) -> Agent:
    return Agent(
        name=f"GO2SE_{tool_name}",
        instructions=f"""你是一个专业的加密货币交易Agent，负责【{tool_icon} {tool_name}】策略。

## 你的职责
{description}

## 交易规则
- 置信度 > 65 分才执行做多
- 做空需要 > 75 分（普通模式）或 > 80 分（专家模式）
- 最大仓位不超过 20%
- 止损 3-5%，止盈 8-15%
- 记录每笔交易的理由

## 输出格式
返回 JSON:
{{"decision": "long/short/hold", "confidence": 0-100, "reason": "理由", "symbol": "标的"}}
""",
        tools=[get_market_data, get_position, execute_trade],
        model=settings.OPENAI_MODEL if settings.OPENAI_API_KEY else "gpt-4o"
    )

RABBIT_AGENT    = create_tool_agent("打兔子",   "🐰", "追踪市值前20主流币趋势，发现强势信号时入场")
MOLE_AGENT      = create_tool_agent("打地鼠",   "🐹", "等待异动币突然反弹，敲一下动一下，高波动高收益")
ORACLE_AGENT    = create_tool_agent("走着瞧",   "🔮", "基于预测市场Polymarket分析，提前布局趋势")
LEADER_AGENT    = create_tool_agent("跟大哥",   "👑", "跟随大户地址操作，借势而为")
HITCHHIKER_AGENT= create_tool_agent("搭便车",   "🍀", "跟单专业交易员，分享利润")
WOOL_AGENT      = create_tool_agent("薅羊毛",   "💰", "寻找空投机会和新币质押收益")
CROWD_AGENT     = create_tool_agent("穷孩子",   "👶", "参与众包任务赚取加密报酬")

AGENTS = {
    "rabbit": RABBIT_AGENT, "mole": MOLE_AGENT,
    "oracle": ORACLE_AGENT, "leader": LEADER_AGENT,
    "hitchhiker": HITCHHIKER_AGENT, "wool": WOOL_AGENT, "crowd": CROWD_AGENT,
}

# ─── API 路由 ─────────────────────────────────────────────
@app.get("/")
async def root():
    return {"name": settings.APP_NAME, "version": settings.APP_VERSION, "status": "running"}

@app.get("/health")
async def health():
    switch_engine.check_daily_reset()
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "agents": list(AGENTS.keys()),
        "engine": "autonomous_switch_v1",
        "daily_reset_date": str(switch_engine.last_reset_date) if hasattr(switch_engine, 'last_reset_date') else "never"
    }

@app.get("/api/agents")
async def list_agents():
    return {"agents": [{"id": k, "name": v.name} for k, v in AGENTS.items()]}

@app.get("/api/risk/config")
async def risk_config():
    """风控配置"""
    return {
        "risk_config": RISK_CONFIG,
        "leverage_tiers": LEVERAGE_TIERS,
        "daily_stats": {
            "trades": switch_engine.daily_trades,
            "pnl": round(switch_engine.daily_pnl, 2),
            "daily_loss_pct": round(switch_engine.daily_loss, 2)
        },
        "mode": switch_engine.mode,
        "current_regime": switch_engine.current_regime.value,
        "last_direction": switch_engine.last_direction.value if switch_engine.last_direction else None,
    }

class AnalyzeRequest(PydanticBaseModel):
    symbol: str = "BTC/USDT"
    confidence: float = 70.0
    mode: str = "normal"
    consecutive_wins: int = 0


def estimate_rsi_from_market(fear_greed: float, regime: str) -> float:
    """
    从市场数据估算RSI (Binance API被封时的降级方案)
    原理: fear_greed指数与RSI有强相关性
    """
    fg = fear_greed
    base_rsi = fg
    if regime == "BEAR":
        rsi = max(20, base_rsi - 15)
    elif regime == "BULL":
        rsi = min(80, base_rsi + 10)
    elif regime == "VOLATILE":
        rsi = max(20, base_rsi - 20) if fg < 40 else min(85, base_rsi + 15)
    else:
        rsi = base_rsi
    import random
    rsi = max(15, min(90, rsi + random.uniform(-3, 3)))
    return round(rsi, 1)



@app.post("/api/switch/analyze")
async def switch_analyze(req: AnalyzeRequest):
    regime = switch_engine.detect_regime(req.symbol)
    signal = switch_engine.analyze(req.symbol, req.confidence, regime, req.mode)

    lev = LEVERAGE_TIERS[signal.leverage_tier]

    # MiroFish Mi
    mf = get_mf()
    try:
        fear_greed = 50.0
        try:
            import json as _json
            _req = urllib.request.Request("http://localhost:8000/api/v7/market/summary", headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(_req, timeout=4) as _resp:
                _data = _json.loads(_resp.read())
                fear_greed = float(_data.get("data", _data).get("fear_greed_index", 50))
        except Exception:
            pass
        rsi_val = estimate_rsi_from_market(fear_greed, signal.regime.value)
        # 使用统一Mi源确保全系统一致
        try:
            import json as _json
            _req = urllib.request.Request(
                "http://localhost:8020/mi/sync",
                headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(_req, timeout=5) as _resp:
                _data = _json.loads(_resp.read())
            mi = float(_data.get("unified_mi", 0.75))
        except Exception:
            mi = mf.get_mi_sync(signal.regime.value, rsi_val, fear_greed)
    except Exception:
        mi = 0.75

    return {
        "signal": {
            "symbol": signal.symbol,
            "direction": signal.direction.value,
            "confidence": signal.confidence,
            "mi": mi,
            "reason": signal.reason,
            "regime": signal.regime.value,
            "mode": signal.mode,
            "leverage_tier": signal.leverage_tier,
            "leverage": lev["leverage"],
            "position_pct": signal.position_pct,
            "stop_loss_pct": signal.stop_loss_pct,
            "take_profit_pct": signal.take_profit_pct,
            "timestamp": signal.timestamp,
        },
        "risk": {
            "daily_trades": switch_engine.daily_trades,
            "daily_pnl": round(switch_engine.daily_pnl, 2),
            "daily_loss_pct": round(switch_engine.daily_loss, 2),
            "daily_loss_limit": RISK_CONFIG["daily_loss_limit_pct"],
            "熔断触发": switch_engine.daily_loss >= RISK_CONFIG["daily_loss_limit_pct"],
        }
    }

@app.post("/api/switch/mode")
async def set_mode(mode: str):
    """切换普通/专家模式"""
    if mode not in ["normal", "expert"]:
        return {"error": "mode must be 'normal' or 'expert'"}
    switch_engine.mode = mode
    return {"mode": mode, "message": f"已切换至{'普通模式(仅做多)' if mode == 'normal' else '专家模式(多空切换)'}"}

@app.post("/api/switch/record")
async def record_trade(signal_json: Dict):
    """记录交易结果"""
    sig = TradingSignal(
        symbol=signal_json["symbol"],
        direction=TradeDirection(signal_json["direction"]),
        confidence=signal_json["confidence"],
        reason=signal_json["reason"],
        regime=MarketRegime(signal_json.get("regime", "neutral")),
        mode=signal_json.get("mode", "normal")
    )
    switch_engine.record_trade(sig, signal_json.get("pnl", 0.0))
    return {"recorded": True, "daily_trades": switch_engine.daily_trades}

@app.post("/api/analyze/{tool_id}")
async def analyze(tool_id: str, symbol: str = "BTC/USDT"):
    # ── RSI极端值独立信号 ─────────────────────────────────────────
    # RSI>75 → 强制SHORT | RSI<28 → 强制LONG (不依赖regime检测)
    rsi_estimate = max(25, min(85, int(50 + (int(confidence) - 70) * 0.8))) if confidence else 50
    if rsi_estimate > 75:
        return {
            "signal": {
                "direction": "short", "mode": mode, "regime": "bear",
                "leverage": 3, "position_pct": 25,
                "stop_loss_pct": 3.0, "take_profit_pct": 8.0,
                "mi": 0.75, "confidence": float(confidence),
                "reasoning": f"RSI Extreme SHORT: RSI={rsi_estimate}>75",
            },
            "switch_triggered": False,
        }
    elif rsi_estimate < 28:
        return {
            "signal": {
                "direction": "long", "mode": mode, "regime": "bull",
                "leverage": 3, "position_pct": 35,
                "stop_loss_pct": 5.0, "take_profit_pct": 12.0,
                "mi": 0.75, "confidence": float(confidence),
                "reasoning": f"RSI Extreme LONG: RSI={rsi_estimate}<28",
            },
            "switch_triggered": False,
        }

    if tool_id not in AGENTS:
        return {"error": f"Unknown agent: {tool_id}"}
    if not settings.OPENAI_API_KEY:
        return {"error": "OpenAI API key not configured", "tool_id": tool_id}
    agent = AGENTS[tool_id]
    try:
        result = await asyncio.to_thread(Runner.run_sync, agent, f"分析 {symbol} 的交易机会")
        return {"tool": tool_id, "symbol": symbol, "result": result.final_output}
    except Exception as e:
        logger.error(f"Agent error: {e}")
        return {"error": str(e), "tool": tool_id}

@app.post("/api/analyze/all")
async def analyze_all(symbol: str = "BTC/USDT"):
    results = {}
    for tool_id, agent in AGENTS.items():
        if not settings.OPENAI_API_KEY:
            results[tool_id] = {"error": "API key missing"}
            continue
        try:
            result = Runner.run_sync(agent, f"分析 {symbol}，给出交易建议")
            results[tool_id] = {"result": result.final_output, "status": "ok"}
        except Exception as e:
            results[tool_id] = {"error": str(e), "status": "error"}
    return {"symbol": symbol, "tool_results": results}

@app.get("/api/performance")
async def performance():
    return {
        "strategy": "v6i_openai_agents",
        "version": settings.APP_VERSION,
        "timestamp": datetime.now().isoformat(),
        "total_capital": 100000,
        "investment_pool": 80000,
        "work_pool": 20000,
        "mode": switch_engine.mode,
        "investment_tools": {
            "rabbit":    {"name": "🐰 打兔子",   "weight": 25, "allocation": 20000},
            "mole":      {"name": "🐹 打地鼠",   "weight": 20, "allocation": 16000},
            "oracle":    {"name": "🔮 走着瞧",   "weight": 15, "allocation": 12000},
            "leader":    {"name": "👑 跟大哥",   "weight": 15, "allocation": 12000},
            "hitchhiker":{"name": "🍀 搭便车",   "weight": 10, "allocation": 8000},
        },
        "work_tools": {
            "wool":  {"name": "💰 薅羊毛", "weight": 3, "allocation": 3000},
            "crowd": {"name": "👶 穷孩子", "weight": 5, "allocation": 5000},
        },
        "risk_config": RISK_CONFIG,
        "leverage_tiers": {k: {"leverage": v["leverage"], "max_position_pct": v["max_position_pct"], "desc": v["desc"]} for k, v in LEVERAGE_TIERS.items()},
    }

if __name__ == "__main__":
    import uvicorn
    logger.info(f"🚀 {settings.APP_NAME} 启动...")
    logger.info(f"📌 多空切换引擎: 自主切换 + 严格风控")
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
