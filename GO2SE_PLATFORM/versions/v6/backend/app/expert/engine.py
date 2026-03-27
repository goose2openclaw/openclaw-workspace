#!/usr/bin/env python3
"""
🪿 GO2SE 专家模式核心引擎
北斗七鑫量化交易系统 - 深度推理引擎
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """风险等级"""
    CONSERVATIVE = "conservative"  # 保守
    BALANCED = "balanced"          # 平衡
    AGGRESSIVE = "aggressive"      # 激进


class InvestmentType(Enum):
    """投资类型"""
    RABBIT = "rabbit"              # 打兔子 - 市值前20
    MOLE = "mole"                  # 打地鼠 - 其它币种
    ORACLE = "oracle"              # 走着燋 - 预测市场
    LEADER = "leader"              # 跟大哥 - 做市协调
    HITCHHIKER = "hitchhiker"     # 搭便车 - 跟单分成
    AIRDROP = "airdrop"            # 薅羊毛 - 新币空投
    CROWD = "crowd"                # 穷孩子 - 众包数据


@dataclass
class MarketCondition:
    """市场条件"""
    trend_strength: float          # 趋势强度 (0-10)
    volatility: float              # 波动率 (0-10)
    volume_ratio: float            # 成交量比
    rsi: float                    # RSI
    momentum: float                # 动量
    sentiment: float               # 情绪 (-10 to 10)


@dataclass
class PositionConfig:
    """持仓配置"""
    symbol: str
    amount: float
    entry_price: float
    stop_loss: float               # 止损
    take_profit: float             # 止盈
    trend_strength_at_entry: float  # 入场时趋势强度


@dataclass
class StrategyParams:
    """策略参数"""
    # 风险偏好
    risk_level: RiskLevel = RiskLevel.BALANCED
    
    # 仓位管理
    max_position_pct: float = 0.20    # 最大仓位 20%
    min_position_pct: float = 0.02    # 最小仓位 2%
    
    # 止损止盈
    default_stop_loss_pct: float = 0.05   # 默认止损 5%
    default_take_profit_pct: float = 0.15 # 默认止盈 15%
    trailing_stop_enabled: bool = True      # 追踪止损
    trailing_stop_pct: float = 0.03        # 追踪止损 3%
    
    # 趋势判断
    strong_trend_threshold: float = 7.0    # 强趋势阈值
    weak_trend_threshold: float = 4.0      # 弱趋势阈值
    
    # 高频量化
    high_freq_enabled: bool = False
    high_freq_threshold: float = 6.0        # 高频阈值
    
    # 专家模式
    expert_mode: bool = False
    remove_take_profit: bool = False       # 移除止盈点
    leverage_enabled: bool = False
    leverage_ratio: float = 1.0
    
    # 备用金
    reserve_fund_enabled: bool = False
    reserve_fund_limit: float = 0.0
    
    # 算力优先级
    api_priority: int = 5                  # API优先级 1-10
    compute_priority: int = 5               # 算力优先级 1-10


@dataclass
class BacktestResult:
    """回测结果"""
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    total_pnl: float = 0.0
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    avg_holding_time: float = 0.0
    profit_factor: float = 0.0


class ExpertEngine:
    """专家模式引擎"""
    
    # 风险参数配置
    RISK_PARAMS = {
        RiskLevel.CONSERVATIVE: {
            "max_position_pct": 0.10,
            "default_stop_loss_pct": 0.03,
            "default_take_profit_pct": 0.08,
            "strong_trend_threshold": 8.0,
            "high_freq_enabled": False,
            "leverage_ratio": 1.0,
        },
        RiskLevel.BALANCED: {
            "max_position_pct": 0.20,
            "default_stop_loss_pct": 0.05,
            "default_take_profit_pct": 0.15,
            "strong_trend_threshold": 7.0,
            "high_freq_enabled": True,
            "leverage_ratio": 1.0,
        },
        RiskLevel.AGGRESSIVE: {
            "max_position_pct": 0.30,
            "default_stop_loss_pct": 0.08,
            "default_take_profit_pct": 0.25,
            "strong_trend_threshold": 6.0,
            "high_freq_enabled": True,
            "leverage_ratio": 2.0,
        },
    }
    
    # 工具配置
    TOOL_CONFIGS = {
        InvestmentType.RABBIT: {
            "symbols": ["BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "AVAX", "DOT", "MATIC", "LINK",
                       "UNI", "ATOM", "LTC", "BCH", "XLM", "ALGO", "VET", "FIL", "THETA", "AAVE"],
            "api_priority": 10,
            "compute_priority": 10,
            "min_trade_amount": 100,
        },
        InvestmentType.MOLE: {
            "symbols": "all_except_top20",
            "api_priority": 7,
            "compute_priority": 7,
            "min_trade_amount": 10,
        },
        InvestmentType.ORACLE: {
            "symbols": "polymarket",
            "api_priority": 8,
            "compute_priority": 8,
            "min_trade_amount": 50,
        },
        InvestmentType.LEADER: {
            "symbols": "leader_whales",
            "api_priority": 9,
            "compute_priority": 9,
            "min_trade_amount": 100,
        },
        InvestmentType.HITCHHIKER: {
            "symbols": "copy_traders",
            "api_priority": 6,
            "compute_priority": 6,
            "min_trade_amount": 50,
        },
    }
    
    def __init__(self):
        self.positions: Dict[str, PositionConfig] = {}
        self.params = StrategyParams()
        self.market_history: List[MarketCondition] = []
    
    def set_risk_level(self, risk_level: RiskLevel):
        """设置风险等级"""
        self.params.risk_level = risk_level
        risk_params = self.RISK_PARAMS[risk_level]
        self.params.max_position_pct = risk_params["max_position_pct"]
        self.params.default_stop_loss_pct = risk_params["default_stop_loss_pct"]
        self.params.default_take_profit_pct = risk_params["default_take_profit_pct"]
        self.params.strong_trend_threshold = risk_params["strong_trend_threshold"]
        self.params.high_freq_enabled = risk_params["high_freq_enabled"]
        self.params.leverage_ratio = risk_params["leverage_ratio"]
    
    def enable_expert_mode(self, remove_tp: bool = False, leverage: float = 1.0):
        """启用专家模式"""
        self.params.expert_mode = True
        self.params.remove_take_profit = remove_tp
        self.params.leverage_enabled = leverage > 1.0
        self.params.leverage_ratio = leverage
    
    def analyze_market(self, price_data: List[float], volume_data: List[float]) -> MarketCondition:
        """分析市场条件"""
        if len(price_data) < 20:
            return MarketCondition(0, 0, 0, 50, 0, 0)
        
        # 计算趋势强度
        returns = np.diff(price_data) / price_data[:-1]
        trend_strength = abs(np.mean(returns)) / np.std(returns) * 10 if np.std(returns) > 0 else 0
        trend_strength = min(10, max(0, trend_strength))
        
        # 波动率
        volatility = min(10, np.std(returns) * 100)
        
        # 成交量比
        avg_volume = np.mean(volume_data[-20:-1])
        current_volume = volume_data[-1]
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        # RSI
        gains = np.where(returns > 0, returns, 0)
        losses = np.where(returns < 0, -returns, 0)
        avg_gain = np.mean(gains[-14:])
        avg_loss = np.mean(losses[-14:])
        rsi = 100 - (100 / (1 + avg_gain / avg_loss)) if avg_loss > 0 else 50
        
        # 动量
        momentum = (price_data[-1] / price_data[-20] - 1) * 100
        
        # 情绪 (简化)
        sentiment = (rsi - 50) / 5 + trend_strength - volatility
        
        condition = MarketCondition(
            trend_strength=trend_strength,
            volatility=volatility,
            volume_ratio=volume_ratio,
            rsi=rsi,
            momentum=momentum,
            sentiment=sentiment
        )
        
        self.market_history.append(condition)
        return condition
    
    def get_investment_recommendation(
        self,
        symbol: str,
        investment_type: InvestmentType,
        market_condition: MarketCondition
    ) -> Dict[str, Any]:
        """获取投资建议"""
        
        # 基础信号
        signal = "hold"
        confidence = 5.0
        reason = "趋势不明显"
        
        # 趋势强度判断
        if market_condition.trend_strength >= self.params.strong_trend_threshold:
            # 强趋势
            if market_condition.momentum > 0:
                signal = "buy"
                confidence = min(10, market_condition.trend_strength)
                reason = f"强上升趋势 (强度:{market_condition.trend_strength:.1f})"
            elif market_condition.momentum < 0:
                signal = "sell"
                confidence = min(10, market_condition.trend_strength)
                reason = f"强下降趋势 (强度:{market_condition.trend_strength:.1f})"
                
        elif market_condition.trend_strength <= self.params.weak_trend_threshold:
            # 弱趋势 - 检查高频量化
            if self.params.high_freq_enabled and market_condition.volatility > 5:
                signal = "high_freq"
                confidence = 7.0
                reason = f"高波动({market_condition.volatility:.1f})适合高频操作"
        
        # 专家模式特殊处理
        if self.params.expert_mode and investment_type in [
            InvestmentType.RABBIT,
            InvestmentType.LEADER,
            InvestmentType.HITCHHIKER
        ]:
            if self.params.remove_take_profit:
                reason += " | 专家模式: 无止盈限制"
        
        # RSI超买超卖
        if market_condition.rsi > 70:
            if signal == "buy":
                signal = "hold"
                reason += " | RSI超买"
        elif market_condition.rsi < 30:
            if signal == "sell":
                signal = "hold"
                reason += " | RSI超卖"
        
        # 计算仓位
        position_size = self.calculate_position_size(confidence, market_condition)
        
        # 计算止损止盈
        stop_loss, take_profit = self.calculate_stop_loss_take_profit(
            signal, market_condition
        )
        
        return {
            "symbol": symbol,
            "type": investment_type.value,
            "signal": signal,
            "confidence": confidence,
            "position_size": position_size,
            "stop_loss_pct": stop_loss,
            "take_profit_pct": take_profit if not self.params.remove_take_profit else None,
            "reason": reason,
            "market": {
                "trend_strength": market_condition.trend_strength,
                "volatility": market_condition.volatility,
                "rsi": market_condition.rsi,
                "sentiment": market_condition.sentiment,
            }
        }
    
    def calculate_position_size(
        self,
        confidence: float,
        market_condition: MarketCondition
    ) -> float:
        """计算仓位大小"""
        # 基础仓位 = 置信度 * 最大仓位
        base_size = (confidence / 10) * self.params.max_position_pct
        
        # 根据波动率调整
        if market_condition.volatility > 7:
            base_size *= 0.7  # 高波动减少仓位
        elif market_condition.volatility < 3:
            base_size *= 1.2  # 低波动增加仓位
        
        # 杠杆调整
        if self.params.leverage_enabled:
            base_size *= self.params.leverage_ratio
        
        return min(self.params.max_position_pct, max(self.params.min_position_pct, base_size))
    
    def calculate_stop_loss_take_profit(
        self,
        signal: str,
        market_condition: MarketCondition
    ) -> Tuple[float, float]:
        """计算止损止盈"""
        # 基础止损
        stop_loss = self.params.default_stop_loss_pct
        
        # 趋势越强，止损越宽
        if market_condition.trend_strength > 7:
            stop_loss = self.params.default_stop_loss_pct * 1.5
        
        # 止盈
        take_profit = self.params.default_take_profit_pct
        
        # 趋势越强，止盈目标越高
        if market_condition.trend_strength > 8:
            take_profit = self.params.default_take_profit_pct * 1.5
        
        # 专家模式
        if self.params.expert_mode and self.params.remove_take_profit:
            take_profit = None
        
        return stop_loss, take_profit or 0
    
    def rebalance_portfolio(
        self,
        current_positions: List[PositionConfig],
        total_value: float,
        new_recommendations: List[Dict]
    ) -> Dict[str, Any]:
        """组合再平衡"""
        
        # 分类持仓
        by_type = {}
        for pos in current_positions:
            inv_type = self.classify_position(pos.symbol)
            if inv_type not in by_type:
                by_type[inv_type] = []
            by_type[inv_type].append(pos)
        
        # 计算目标分配
        target_allocation = self.get_target_allocation()
        
        # 生成调整建议
        actions = []
        
        for inv_type, target_pct in target_allocation.items():
            current_holdings = by_type.get(inv_type, [])
            current_value = sum(p.amount * p.entry_price for p in current_holdings)
            current_pct = current_value / total_value if total_value > 0 else 0
            
            diff = target_pct - current_pct
            
            if abs(diff) > 0.05:  # 超过5%需要调整
                if diff > 0:
                    # 需要增持
                    recommendations = [r for r in new_recommendations if r["type"] == inv_type.value]
                    if recommendations:
                        actions.append({
                            "type": "buy",
                            "investment_type": inv_type.value,
                            "amount": diff * total_value,
                            "reason": f"增持{inv_type.value}"
                        })
                else:
                    # 需要减持
                    actions.append({
                        "type": "sell",
                        "investment_type": inv_type.value,
                        "amount": abs(diff) * total_value,
                        "reason": f"减持{inv_type.value}"
                    })
        
        return {
            "actions": actions,
            "current_allocation": {k: sum(p.amount * p.entry_price for p in v) / total_value 
                                   for k, v in by_type.items()},
            "target_allocation": target_allocation,
        }
    
    def get_target_allocation(self) -> Dict[InvestmentType, float]:
        """获取目标分配"""
        if self.params.risk_level == RiskLevel.CONSERVATIVE:
            return {
                InvestmentType.RABBIT: 0.50,
                InvestmentType.MOLE: 0.20,
                InvestmentType.ORACLE: 0.10,
                InvestmentType.LEADER: 0.10,
                InvestmentType.HITCHHIKER: 0.10,
            }
        elif self.params.risk_level == RiskLevel.BALANCED:
            return {
                InvestmentType.RABBIT: 0.35,
                InvestmentType.MOLE: 0.25,
                InvestmentType.ORACLE: 0.15,
                InvestmentType.LEADER: 0.15,
                InvestmentType.HITCHHIKER: 0.10,
            }
        else:  # AGGRESSIVE
            return {
                InvestmentType.RABBIT: 0.25,
                InvestmentType.MOLE: 0.30,
                InvestmentType.ORACLE: 0.15,
                InvestmentType.LEADER: 0.20,
                InvestmentType.HITCHHIKER: 0.10,
            }
    
    def classify_position(self, symbol: str) -> InvestmentType:
        """分类持仓"""
        if symbol in self.TOOL_CONFIGS[InvestmentType.RABBIT]["symbols"]:
            return InvestmentType.RABBIT
        return InvestmentType.MOLE
    
    def run_backtest(
        self,
        price_data: Dict[str, List[float]],
        investment_type: InvestmentType,
        periods: int = 100
    ) -> BacktestResult:
        """回测"""
        result = BacktestResult()
        
        if investment_type not in price_data:
            return result
        
        data = price_data[investment_type]
        if len(data) < periods:
            periods = len(data)
        
        # 模拟交易
        trades = []
        position = None
        
        for i in range(20, periods):
            window = data[:i]
            volume = [1.0] * len(window)  # 简化
            
            condition = self.analyze_market(window, volume)
            rec = self.get_investment_recommendation(
                "TEST",
                investment_type,
                condition
            )
            
            if rec["signal"] == "buy" and position is None:
                position = {
                    "entry_price": data[i-1],
                    "entry_index": i
                }
            elif rec["signal"] == "sell" and position is not None:
                pnl = (data[i-1] - position["entry_price"]) / position["entry_price"]
                trades.append(pnl)
                position = None
        
        # 计算统计
        if trades:
            result.total_trades = len(trades)
            result.winning_trades = sum(1 for t in trades if t > 0)
            result.losing_trades = sum(1 for t in trades if t <= 0)
            result.win_rate = result.winning_trades / result.total_trades
            result.total_pnl = sum(trades)
            result.profit_factor = abs(sum(t for t in trades if t > 0) / sum(t for t in trades if t < 0)) if sum(t for t in trades if t < 0) != 0 else 0
        
        return result
    
    def get_params_for_ui(self) -> Dict:
        """获取UI参数"""
        return {
            "risk_levels": [
                {"id": "conservative", "name": "保守", "description": "低风险,稳定收益"},
                {"id": "balanced", "name": "平衡", "description": "中等风险,均衡收益"},
                {"id": "aggressive", "name": "激进", "description": "高风险,高收益"},
            ],
            "current_risk_level": self.params.risk_level.value,
            "expert_mode": self.params.expert_mode,
            "parameters": {
                "max_position_pct": {
                    "value": self.params.max_position_pct,
                    "min": 0.02,
                    "max": 0.50,
                    "step": 0.01,
                    "label": "最大仓位"
                },
                "default_stop_loss_pct": {
                    "value": self.params.default_stop_loss_pct,
                    "min": 0.01,
                    "max": 0.15,
                    "step": 0.005,
                    "label": "默认止损"
                },
                "default_take_profit_pct": {
                    "value": self.params.default_take_profit_pct,
                    "min": 0.03,
                    "max": 0.50,
                    "step": 0.01,
                    "label": "默认止盈",
                    "hidden": self.params.remove_take_profit
                },
                "strong_trend_threshold": {
                    "value": self.params.strong_trend_threshold,
                    "min": 3.0,
                    "max": 9.0,
                    "step": 0.5,
                    "label": "强趋势阈值"
                },
                "leverage_ratio": {
                    "value": self.params.leverage_ratio,
                    "min": 1.0,
                    "max": 5.0,
                    "step": 0.5,
                    "label": "杠杆倍数",
                    "expert_only": True
                },
            },
            "tool_configs": {
                k.value: {
                    "api_priority": v["api_priority"],
                    "compute_priority": v["compute_priority"],
                    "min_trade_amount": v["min_trade_amount"],
                }
                for k, v in self.TOOL_CONFIGS.items()
            }
        }


# 全局实例
expert_engine = ExpertEngine()
