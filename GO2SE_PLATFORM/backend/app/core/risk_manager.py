"""
风控系统 - 8条风控规则
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    """风险等级"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class RiskRule(Enum):
    """风控规则"""
    R001_POSITION_LIMIT = "R001"      # 仓位限制
    R002_DAILY_STOP = "R002"          # 日内熔断
    R003_SINGLE_RISK = "R003"         # 单笔风险
    R004_VOLATILITY_STOP = "R004"    # 波动止损
    R005_LIQUIDITY_CHECK = "R005"     # 流动性检查
    R006_API_FAILURE = "R006"         # API故障
    R007_ANOMALY_DETECTION = "R007"   # 异常检测
    R008_SENTIMENT_OVERHEAT = "R008"  # 情绪过热

@dataclass
class RiskCheckResult:
    """风控检查结果"""
    rule: RiskRule
    passed: bool
    risk_level: RiskLevel
    message: str
    action_required: Optional[str] = None

@dataclass
class Position:
    """持仓"""
    symbol: str
    entry_price: float
    current_price: float
    quantity: float
    side: str  # LONG/SHORT
    entry_time: datetime
    
    @property
    def pnl_percent(self) -> float:
        """盈亏百分比"""
        if self.side == "LONG":
            return (self.current_price - self.entry_price) / self.entry_price * 100
        else:
            return (self.entry_price - self.current_price) / self.entry_price * 100
            
    @property
    def pnl_value(self) -> float:
        """盈亏金额"""
        return self.pnl_percent / 100 * self.entry_price * self.quantity
        
    @property
    def value(self) -> float:
        """持仓价值"""
        return self.current_price * self.quantity

@dataclass
class Trade:
    """交易记录"""
    symbol: str
    side: str
    price: float
    quantity: float
    fee: float
    timestamp: datetime
    pnl: float = 0.0

class RiskManager:
    """风控管理器"""
    
    def __init__(self):
        # 风控规则配置
        self.config = {
            RiskRule.R001_POSITION_LIMIT: {
                "max_position_ratio": 0.80,  # 最大仓位80%
                "enabled": True
            },
            RiskRule.R002_DAILY_STOP: {
                "max_daily_loss": 0.30,  # 日内最大亏损30%
                "enabled": True
            },
            RiskRule.R003_SINGLE_RISK: {
                "max_single_risk": 0.05,  # 单笔最大风险5%
                "enabled": True
            },
            RiskRule.R004_VOLATILITY_STOP: {
                "volatility_threshold": 0.08,  # 波动超过8%触发
                "enabled": True
            },
            RiskRule.R005_LIQUIDITY_CHECK: {
                "min_volume_24h": 100000,  # 最小成交量10万
                "enabled": True
            },
            RiskRule.R006_API_FAILURE: {
                "max_error_rate": 0.01,  # 错误率超过1%触发
                "enabled": True
            },
            RiskRule.R007_ANOMALY_DETECTION: {
                "std_deviation_threshold": 3,  # 偏离3倍标准差
                "enabled": True
            },
            RiskRule.R008_SENTIMENT_OVERHEAT: {
                "volatility_threshold": 5,  # 波动超过5倍
                "enabled": True
            }
        }
        
        # 状态跟踪
        self.positions: List[Position] = []
        self.daily_trades: List[Trade] = []
        self.daily_pnl = 0.0
        self.api_errors = 0
        self.api_total = 0
        self.last_reset = datetime.utcnow()
        
    def reset_daily(self):
        """重置每日状态"""
        self.daily_trades = []
        self.daily_pnl = 0.0
        self.last_reset = datetime.utcnow()
        
    def add_position(self, position: Position):
        """添加持仓"""
        self.positions.append(position)
        
    def close_position(self, symbol: str, current_price: float):
        """平仓"""
        for i, pos in enumerate(self.positions):
            if pos.symbol == symbol:
                pos.current_price = current_price
                self.positions.pop(i)
                break
                
    def update_position_price(self, symbol: str, current_price: float):
        """更新持仓价格"""
        for pos in self.positions:
            if pos.symbol == symbol:
                pos.current_price = current_price
                
    def add_trade(self, trade: Trade):
        """添加交易记录"""
        self.daily_trades.append(trade)
        self.daily_pnl += trade.pnl
        
    def record_api_call(self, success: bool):
        """记录API调用"""
        self.api_total += 1
        if not success:
            self.api_errors += 1
            
    # ===== 风控规则检查 =====
    
    def check_r001_position_limit(self, new_position_ratio: float) -> RiskCheckResult:
        """R001: 仓位限制"""
        config = self.config[RiskRule.R001_POSITION_LIMIT]
        max_ratio = config["max_position_ratio"]
        
        # 计算当前总仓位
        total_ratio = sum(p.value for p in self.positions) / 10000  # 假设总资金10万
        new_total = total_ratio + new_position_ratio
        
        if new_total > max_ratio:
            return RiskCheckResult(
                rule=RiskRule.R001_POSITION_LIMIT,
                passed=False,
                risk_level=RiskLevel.HIGH,
                message=f"仓位超限: 当前{total_ratio*100:.1f}% + 新增{new_position_ratio*100:.1f}% > 最大{max_ratio*100:.1f}%",
                action_required="减少仓位或平仓部分"
            )
            
        return RiskCheckResult(
            rule=RiskRule.R001_POSITION_LIMIT,
            passed=True,
            risk_level=RiskLevel.LOW,
            message=f"仓位检查通过: {total_ratio*100:.1f}% + {new_position_ratio*100:.1f}%"
        )
        
    def check_r002_daily_stop(self, capital: float) -> RiskCheckResult:
        """R002: 日内熔断"""
        config = self.config[RiskRule.R002_DAILY_STOP]
        max_loss = config["max_daily_loss"]
        
        loss_ratio = abs(self.daily_pnl) / capital if self.daily_pnl < 0 else 0
        
        if loss_ratio > max_loss:
            return RiskCheckResult(
                rule=RiskRule.R002_DAILY_STOP,
                passed=False,
                risk_level=RiskLevel.CRITICAL,
                message=f"日内熔断触发: 亏损{loss_ratio*100:.1f}% > 最大{max_loss*100:.1f}%",
                action_required="停止所有交易，等待明日"
            )
            
        return RiskCheckResult(
            rule=RiskRule.R002_DAILY_STOP,
            passed=True,
            risk_level=RiskLevel.LOW,
            message=f"日内熔断检查通过: 亏损{loss_ratio*100:.1f}%"
        )
        
    def check_r003_single_risk(self, position_value: float, stop_loss_percent: float, capital: float) -> RiskCheckResult:
        """R003: 单笔风险"""
        config = self.config[RiskRule.R003_SINGLE_RISK]
        max_risk = config["max_single_risk"]
        
        risk_amount = position_value * stop_loss_percent
        risk_ratio = risk_amount / capital
        
        if risk_ratio > max_risk:
            return RiskCheckResult(
                rule=RiskRule.R003_SINGLE_RISK,
                passed=False,
                risk_level=RiskLevel.HIGH,
                message=f"单笔风险超限: {risk_ratio*100:.1f}% > 最大{max_risk*100:.1f}%",
                action_required="降低仓位或扩大止损"
            )
            
        return RiskCheckResult(
            rule=RiskRule.R003_SINGLE_RISK,
            passed=True,
            risk_level=RiskLevel.LOW,
            message=f"单笔风险检查通过: {risk_ratio*100:.1f}%"
        )
        
    def check_r004_volatility_stop(self, symbol: str, volatility_percent: float) -> RiskCheckResult:
        """R004: 波动止损"""
        config = self.config[RiskRule.R004_VOLATILITY_STOP]
        threshold = config["volatility_threshold"]
        
        if volatility_percent > threshold:
            return RiskCheckResult(
                rule=RiskRule.R004_VOLATILITY_STOP,
                passed=False,
                risk_level=RiskLevel.HIGH,
                message=f"波动止损触发: {symbol}波动{volatility_percent*100:.1f}% > 阈值{threshold*100:.1f}%",
                action_required="立即平仓"
            )
            
        return RiskCheckResult(
            rule=RiskRule.R004_VOLATILITY_STOP,
            passed=True,
            risk_level=RiskLevel.LOW,
            message=f"波动止损检查通过: {volatility_percent*100:.1f}%"
        )
        
    def check_r005_liquidity_check(self, volume_24h: float) -> RiskCheckResult:
        """R005: 流动性检查"""
        config = self.config[RiskRule.R005_LIQUIDITY_CHECK]
        min_volume = config["min_volume_24h"]
        
        if volume_24h < min_volume:
            return RiskCheckResult(
                rule=RiskRule.R005_LIQUIDITY_CHECK,
                passed=False,
                risk_level=RiskLevel.MEDIUM,
                message=f"流动性不足: 24h成交量${volume_24h:,.0f} < 最小${min_volume:,.0f}",
                action_required="建议不交易或等待流动性改善"
            )
            
        return RiskCheckResult(
            rule=RiskRule.R005_LIQUIDITY_CHECK,
            passed=True,
            risk_level=RiskLevel.LOW,
            message=f"流动性检查通过: ${volume_24h:,.0f}"
        )
        
    def check_r006_api_failure(self) -> RiskCheckResult:
        """R006: API故障"""
        config = self.config[RiskRule.R006_API_FAILURE]
        max_error_rate = config["max_error_rate"]
        
        if self.api_total == 0:
            return RiskCheckResult(
                rule=RiskRule.R006_API_FAILURE,
                passed=True,
                risk_level=RiskLevel.LOW,
                message="API调用无记录"
            )
            
        error_rate = self.api_errors / self.api_total
        
        if error_rate > max_error_rate:
            return RiskCheckResult(
                rule=RiskRule.R006_API_FAILURE,
                passed=False,
                risk_level=RiskLevel.CRITICAL,
                message=f"API错误率过高: {error_rate*100:.1f}% > 最大{max_error_rate*100:.1f}%",
                action_required="切换备用API或暂停交易"
            )
            
        return RiskCheckResult(
            rule=RiskRule.R006_API_FAILURE,
            passed=True,
            risk_level=RiskLevel.LOW,
            message=f"API错误率: {error_rate*100:.2f}%"
        )
        
    def check_r007_anomaly_detection(self, price: float, historical_prices: List[float]) -> RiskCheckResult:
        """R007: 异常检测"""
        import statistics
        
        config = self.config[RiskRule.R007_ANOMALY_DETECTION]
        threshold = config["std_deviation_threshold"]
        
        if len(historical_prices) < 20:
            return RiskCheckResult(
                rule=RiskRule.R007_ANOMALY_DETECTION,
                passed=True,
                risk_level=RiskLevel.LOW,
                message="历史数据不足，跳过异常检测"
            )
            
        mean = statistics.mean(historical_prices)
        std = statistics.stdev(historical_prices)
        
        if std == 0:
            return RiskCheckResult(
                rule=RiskRule.R007_ANOMALY_DETECTION,
                passed=True,
                risk_level=RiskLevel.LOW,
                message="标准差为0，跳过异常检测"
            )
            
        z_score = abs(price - mean) / std
        
        if z_score > threshold:
            return RiskCheckResult(
                rule=RiskRule.R007_ANOMALY_DETECTION,
                passed=False,
                risk_level=RiskLevel.HIGH,
                message=f"价格异常: Z-score={z_score:.1f} > 阈值{threshold}",
                action_required="等待价格回归或手动确认"
            )
            
        return RiskCheckResult(
            rule=RiskRule.R007_ANOMALY_DETECTION,
            passed=True,
            risk_level=RiskLevel.LOW,
            message=f"异常检测通过: Z-score={z_score:.2f}"
        )
        
    def check_r008_sentiment_overheat(self, volatility: float, fear_greed_index: int = 50) -> RiskCheckResult:
        """R008: 情绪过热"""
        config = self.config[RiskRule.R008_SENTIMENT_OVERHEAT]
        vol_threshold = config["volatility_threshold"]
        
        # 波动率超过5倍或恐惧贪婪指数极端
        if volatility > vol_threshold:
            return RiskCheckResult(
                rule=RiskRule.R008_SENTIMENT_OVERHEAT,
                passed=False,
                risk_level=RiskLevel.HIGH,
                message=f"情绪过热: 波动率指数{volatility:.1f} > 阈值{vol_threshold}",
                action_required="减少仓位或退出观望"
            )
            
        if fear_greed_index >= 80:
            return RiskCheckResult(
                rule=RiskRule.R008_SENTIMENT_OVERHEAT,
                passed=False,
                risk_level=RiskLevel.MEDIUM,
                message=f"极度贪婪: 恐惧贪婪指数{fear_greed_index} >= 80",
                action_required="注意回调风险"
            )
            
        if fear_greed_index <= 20:
            return RiskCheckResult(
                rule=RiskRule.R008_SENTIMENT_OVERHEAT,
                passed=False,
                risk_level=RiskLevel.MEDIUM,
                message=f"极度恐惧: 恐惧贪婪指数{fear_greed_index} <= 20",
                action_required="注意反弹机会"
            )
            
        return RiskCheckResult(
            rule=RiskRule.R008_SENTIMENT_OVERHEAT,
            passed=True,
            risk_level=RiskLevel.LOW,
            message=f"情绪检查通过: 波动{volatility:.1f}, 恐惧贪婪={fear_greed_index}"
        )
        
    # ===== 综合风控检查 =====
    
    def check_all(self, trade_params: Dict, market_data: Dict, capital: float) -> Dict[str, RiskCheckResult]:
        """执行所有风控检查"""
        results = {}
        
        # R001: 仓位限制
        results["R001"] = self.check_r001_position_limit(
            trade_params.get("position_ratio", 0.1)
        )
        
        # R002: 日内熔断
        results["R002"] = self.check_r002_daily_stop(capital)
        
        # R003: 单笔风险
        results["R003"] = self.check_r003_single_risk(
            trade_params.get("position_value", 1000),
            trade_params.get("stop_loss", 0.05),
            capital
        )
        
        # R004: 波动止损
        if "volatility" in market_data:
            results["R004"] = self.check_r004_volatility_stop(
                trade_params.get("symbol", ""),
                market_data["volatility"]
            )
            
        # R005: 流动性检查
        if "volume_24h" in market_data:
            results["R005"] = self.check_r005_liquidity_check(
                market_data["volume_24h"]
            )
            
        # R006: API故障
        results["R006"] = self.check_r006_api_failure()
        
        # R007: 异常检测
        if "price" in market_data and "historical_prices" in market_data:
            results["R007"] = self.check_r007_anomaly_detection(
                market_data["price"],
                market_data["historical_prices"]
            )
            
        # R008: 情绪过热
        if "volatility_index" in market_data or "fear_greed" in market_data:
            results["R008"] = self.check_r008_sentiment_overheat(
                market_data.get("volatility_index", 1.0),
                market_data.get("fear_greed", 50)
            )
            
        return results
        
    def can_trade(self, trade_params: Dict, market_data: Dict, capital: float) -> Tuple[bool, str]:
        """综合判断是否可以交易"""
        results = self.check_all(trade_params, market_data, capital)
        
        failed_rules = [r for r in results.values() if not r.passed]
        
        if not failed_rules:
            return True, "所有风控检查通过"
            
        # 严重程度排序
        critical = [r for r in failed_rules if r.risk_level == RiskLevel.CRITICAL]
        high = [r for r in failed_rules if r.risk_level == RiskLevel.HIGH]
        
        if critical:
            return False, f"严重: {critical[0].message}"
        elif high:
            return False, f"警告: {high[0].message}"
        else:
            return False, failed_rules[0].message
            
    def get_risk_status(self) -> Dict:
        """获取风控状态"""
        return {
            "open_positions": len(self.positions),
            "daily_pnl": self.daily_pnl,
            "daily_trades": len(self.daily_trades),
            "api_error_rate": self.api_errors / max(self.api_total, 1),
            "rules_enabled": {
                r.value: self.config[r]["enabled"] 
                for r in RiskRule
            }
        }


# 全局风控管理器实例
risk_manager = RiskManager()
