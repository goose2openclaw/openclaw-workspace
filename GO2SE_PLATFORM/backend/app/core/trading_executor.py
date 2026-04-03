"""
TradingExecutor - 核心交易执行引擎
=================================
趋势判断 → 策略选择 → 工具分配 → 操作执行 → 退出评估
"""
from __future__ import annotations
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import random


class TrendStrength(Enum):
    """趋势强度"""
    EXTREME = "EXTREME"      # >80% 极强
    STRONG = "STRONG"        # 60-80% 强
    NEUTRAL = "NEUTRAL"      # 40-60% 中性
    WEAK = "WEAK"            # 20-40% 弱
    NONE = "NONE"            # <20% 无趋势


class OperationType(Enum):
    """操作类型"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    CLOSE = "CLOSE"
    REDUCE = "REDUCE"
    ADD = "ADD"


@dataclass
class TradingSignal:
    """交易信号"""
    symbol: str
    tool: str  # rabbit/mole/oracle/leader/hitchhiker
    trend_score: float
    trend_strength: TrendStrength
    recommended_action: OperationType
    position_size: float
    leverage: int
    stop_loss: float
    take_profit: float
    remove_tp: bool  # 专家模式
    confidence: float
    fees: float = 0.001  # 0.1% 交易费
    timestamp: str = ""


@dataclass
class PortfolioAllocation:
    """投资组合分配"""
    total_value: float
    allocations: Dict[str, float]  # tool -> percentage
    positions: Dict[str, Dict]  # symbol -> position details
    backup_fund: float = 0.0
    mode: str = "balanced"  # conservative/balanced/aggressive


@dataclass
class ExecutionResult:
    """执行结果"""
    operation: OperationType
    symbol: str
    tool: str
    success: bool
    executed_price: float
    executed_size: float
    fees_paid: float
    pnl: float = 0.0
    message: str = ""


class TradingExecutor:
    """
    核心交易执行引擎
    =================
    1. 趋势判断 → 信号融合
    2. 策略选择 → 工具分配
    3. 操作执行 → 止损止盈
    4. 退出评估 → 组合调整
    """

    def __init__(self, mode: str = "balanced"):
        self.mode = mode
        self.params = self._get_mode_params(mode)
        self.fees = 0.001  # 0.1% Binance手续费
        self._init_tools()

    def _get_mode_params(self, mode: str) -> Dict:
        """获取模式参数"""
        modes = {
            "conservative": {
                "max_position": 0.20,
                "stop_loss": 0.03,
                "take_profit": 0.05,
                "leverage": 1,
                "max_tools": 3,
                "frequency": "low",
                "min_confidence": 0.7,
            },
            "balanced": {
                "max_position": 0.30,
                "stop_loss": 0.05,
                "take_profit": 0.08,
                "leverage": 2,
                "max_tools": 5,
                "frequency": "medium",
                "min_confidence": 0.6,
            },
            "aggressive": {
                "max_position": 0.40,
                "stop_loss": 0.08,
                "take_profit": 0.15,
                "leverage": 5,
                "max_tools": 7,
                "frequency": "high",
                "min_confidence": 0.5,
            },
        }
        return modes.get(mode, modes["balanced"])

    def _init_tools(self):
        """初始化工具配置"""
        self.tools = {
            "rabbit": {
                "name": "打兔子",
                "target": "top20_crypto",
                "weight": 0.25,
                "max_leverage": self.params["leverage"],
                "remove_tp": False,
                "default_stop_loss": self.params["stop_loss"],
                "default_take_profit": self.params["take_profit"],
            },
            "mole": {
                "name": "打地鼠",
                "target": "other_crypto",
                "weight": 0.20,
                "max_leverage": self.params["leverage"],
                "dynamic_tp": True,
                "default_stop_loss": self.params["stop_loss"] * 1.2,
                "default_take_profit": self.params["take_profit"] * 1.5,
            },
            "oracle": {
                "name": "走着瞧",
                "target": "prediction_market",
                "weight": 0.15,
                "max_leverage": self.params["leverage"],
                "default_stop_loss": self.params["stop_loss"],
                "default_take_profit": self.params["take_profit"],
            },
            "leader": {
                "name": "跟大哥",
                "target": "market_making",
                "weight": 0.15,
                "max_leverage": self.params["leverage"],
                "remove_tp": False,
                "default_stop_loss": self.params["stop_loss"] * 0.6,
                "default_take_profit": self.params["take_profit"] * 0.8,
            },
            "hitchhiker": {
                "name": "搭便车",
                "target": "copy_trading",
                "weight": 0.10,
                "max_leverage": self.params["leverage"],
                "remove_tp": False,
                "default_stop_loss": self.params["stop_loss"],
                "default_take_profit": self.params["take_profit"],
            },
        }

    def analyze_trend(self, symbol: str, signals: Dict[str, float]) -> Tuple[TrendStrength, float]:
        """分析趋势强度"""
        # 加权评分
        weights = {
            "mirofish": 0.25,
            "sonar": 0.20,
            "oracle": 0.15,
            "sentiment": 0.15,
            "external_api": 0.13,
            "professional": 0.12,
        }
        total_score = sum(signals.get(k, 0) * v for k, v in weights.items())

        if total_score > 80:
            return TrendStrength.EXTREME, total_score
        elif total_score > 60:
            return TrendStrength.STRONG, total_score
        elif total_score > 40:
            return TrendStrength.NEUTRAL, total_score
        elif total_score > 20:
            return TrendStrength.WEAK, total_score
        else:
            return TrendStrength.NONE, total_score

    def select_tool(self, symbol: str, trend: TrendStrength, is_top20: bool) -> str:
        """选择工具"""
        if is_top20:
            return "rabbit"
        return "mole"

    def calculate_position(
        self,
        trend: TrendStrength,
        total_value: float,
        tool: str,
        confidence: float,
    ) -> Tuple[float, int, float, float, bool]:
        """
        计算仓位
        返回: (position_size, leverage, stop_loss, take_profit, remove_tp)
        """
        tool_config = self.tools[tool]
        base_position = self.params["max_position"]

        # 根据趋势调整仓位
        if trend == TrendStrength.EXTREME:
            position = base_position * 1.5
            leverage = tool_config["max_leverage"]
        elif trend == TrendStrength.STRONG:
            position = base_position * 1.2
            leverage = min(tool_config["max_leverage"], 2)
        elif trend == TrendStrength.NEUTRAL:
            position = base_position * 0.5
            leverage = 1
        elif trend == TrendStrength.WEAK:
            position = base_position * 0.3
            leverage = 1
        else:
            position = 0
            leverage = 1

        # 专家模式特殊规则
        remove_tp = False
        if tool == "rabbit" and hasattr(self, 'expert_mode') and self.expert_mode:
            remove_tp = True
        elif tool == "leader" and hasattr(self, 'expert_mode') and self.expert_mode:
            remove_tp = True
        elif tool == "hitchhiker" and hasattr(self, 'expert_mode') and self.expert_mode:
            remove_tp = True
        elif tool == "mole" and hasattr(self, 'expert_mode') and self.expert_mode:
            # 打地鼠动态止盈
            if trend == TrendStrength.EXTREME:
                remove_tp = True

        # 计算止损止盈
        stop_loss = tool_config["default_stop_loss"]
        take_profit = tool_config["default_take_profit"] if not remove_tp else float('inf')

        # 根据置信度微调
        if confidence > 0.8:
            position *= 1.2
        elif confidence < 0.5:
            position *= 0.7

        position_value = total_value * min(position, self.params["max_position"])

        return position_value, leverage, stop_loss, take_profit, remove_tp

    def generate_signal(
        self,
        symbol: str,
        signals: Dict[str, float],
        total_value: float,
        is_top20: bool = True,
        expert_mode: bool = False,
    ) -> TradingSignal:
        """生成交易信号"""
        self.expert_mode = expert_mode

        trend, score = self.analyze_trend(symbol, signals)
        tool = self.select_tool(symbol, trend, is_top20)
        position_size, leverage, stop_loss, take_profit, remove_tp = self.calculate_position(
            trend, total_value, tool, signals.get("confidence", 0.6)
        )

        # 确定操作
        if trend == TrendStrength.EXTREME:
            action = OperationType.BUY
        elif trend == TrendStrength.STRONG:
            action = OperationType.HOLD
        elif trend == TrendStrength.NEUTRAL:
            action = OperationType.HOLD
        elif trend == TrendStrength.WEAK:
            action = OperationType.REDUCE
        else:
            action = OperationType.CLOSE

        return TradingSignal(
            symbol=symbol,
            tool=tool,
            trend_score=score,
            trend_strength=trend,
            recommended_action=action,
            position_size=position_size,
            leverage=leverage,
            stop_loss=stop_loss,
            take_profit=take_profit,
            remove_tp=remove_tp,
            confidence=signals.get("confidence", 0.6),
            fees=self.fees,
            timestamp=datetime.utcnow().isoformat(),
        )

    def execute_signal(self, signal: TradingSignal) -> ExecutionResult:
        """执行信号"""
        if signal.recommended_action == OperationType.HOLD:
            return ExecutionResult(
                operation=OperationType.HOLD,
                symbol=signal.symbol,
                tool=signal.tool,
                success=True,
                executed_price=0,
                executed_size=0,
                fees_paid=0,
                message="趋势中性，观望",
            )

        # 模拟执行
        executed_price = random.uniform(30000, 70000)
        fees = signal.position_size * signal.fees

        return ExecutionResult(
            operation=signal.recommended_action,
            symbol=signal.symbol,
            tool=signal.tool,
            success=True,
            executed_price=executed_price,
            executed_size=signal.position_size,
            fees_paid=fees,
            message=f"执行{operation_to_chinese(signal.recommended_action)}",
        )

    def adjust_portfolio(
        self,
        portfolio: PortfolioAllocation,
        signals: Dict[str, Dict],
        backup_threshold: float = 0.1,
        expert_mode: bool = False,
    ) -> PortfolioAllocation:
        """调整投资组合"""
        new_allocations = portfolio.allocations.copy()
        new_positions = portfolio.positions.copy()

        for symbol, sig_dict in signals.items():
            signal = self.generate_signal(
                symbol,
                sig_dict,
                portfolio.total_value,
                is_top20=(symbol in self._get_top20()),
                expert_mode=expert_mode,
            )

            # 检查备用金触发
            if signal.trend_strength == TrendStrength.EXTREME and portfolio.backup_fund > 0:
                if signal.confidence > 0.8:
                    # 使用备用金
                    backup_used = min(portfolio.backup_fund * backup_threshold, portfolio.total_value * 0.1)
                    signal.position_size += backup_used
                    portfolio.backup_fund -= backup_used

            # 更新仓位
            new_positions[symbol] = {
                "tool": signal.tool,
                "size": signal.position_size,
                "action": signal.recommended_action.value,
                "leverage": signal.leverage,
                "stop_loss": signal.stop_loss,
                "take_profit": signal.take_profit,
                "remove_tp": signal.remove_tp,
            }

        return PortfolioAllocation(
            total_value=portfolio.total_value,
            allocations=new_allocations,
            positions=new_positions,
            backup_fund=portfolio.backup_fund,
            mode=self.mode,
        )

    def _get_top20(self) -> List[str]:
        """获取前20主流币"""
        return ["BTC", "ETH", "BNB", "XRP", "ADA", "SOL", "DOGE", "DOT", "MATIC", "SHIB",
                "LTC", "TRX", "AVAX", "LINK", "ATOM", "UNI", "XMR", "ETC", "XLM", "BCH"]

    def get_mode_params(self) -> Dict:
        """获取当前模式参数"""
        return self.params

    def set_mode(self, mode: str) -> None:
        """设置模式"""
        self.mode = mode
        self.params = self._get_mode_params(mode)
        self._init_tools()


def operation_to_chinese(op: OperationType) -> str:
    """操作转中文"""
    mapping = {
        OperationType.BUY: "买入",
        OperationType.SELL: "卖出",
        OperationType.HOLD: "持有",
        OperationType.CLOSE: "平仓",
        OperationType.REDUCE: "减仓",
        OperationType.ADD: "加仓",
    }
    return mapping.get(op, "未知")
