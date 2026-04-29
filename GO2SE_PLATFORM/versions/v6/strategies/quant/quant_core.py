#!/usr/bin/env python3
"""
⚡ Quant Core - 高频量化决策引擎
==========================================
功能:
1. Rabbit + Mole 加权组合决策
2. 高频量化优化
3. 权重组合策略
4. 高置信度多空自主切换
5. 集成 vv6/v6i/v15
"""

import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

class Regime(Enum):
    BULL = "bull"
    BEAR = "bear"
    NEUTRAL = "neutral"

@dataclass
class Signal:
    symbol: str
    source: str           # rabbit/mole/brain
    direction: str       # LONG/SHORT/NEUTRAL
    confidence: float    # 0-1
    score: float         # 原始评分
    leverage: float = 1.0
    timestamp: str = ""
    
@dataclass  
class Position:
    symbol: str
    direction: str
    size: float
    entry_price: float
    leverage: float
    pnl: float = 0.0
    stop_loss: float = 0.0
    take_profit: float = 0.0

class WeightedDecisionEngine:
    """
    加权决策引擎
    =================
    决策等式: D = W_r * R + W_m * M + W_b * B
    其中:
    - R = Rabbit评分 (逻辑分析)
    - M = Mole评分 (直觉模式)
    - B = Brain评分 (市场环境)
    - W_* = 动态权重
    """
    
    def __init__(self):
        # 基础权重
        self.base_weights = {"rabbit": 0.40, "mole": 0.35, "brain": 0.25}
        
        # 动态权重调整
        self.adaptive_weights = dict(self.base_weights)
        
        # 置信度阈值
        self.confidence_threshold = 0.65
        self.high_confidence_threshold = 0.80
        
        # 历史表现追踪
        self.performance_history = {
            "rabbit": [], "mole": [], "brain": []
        }
        
    def calculate_composite_score(self, signals: Dict[str, Signal], regime: Regime) -> Tuple[float, Dict]:
        """计算综合评分"""
        
        # 获取各信号评分
        r_score = signals.get("rabbit", Signal("","rabbit","NEUTRAL",0,0)).score if signals.get("rabbit") else 0.5
        m_score = signals.get("mole", Signal("","mole","NEUTRAL",0,0)).score if signals.get("mole") else 0.5
        b_score = signals.get("brain", Signal("","brain","NEUTRAL",0,0)).confidence if signals.get("brain") else 0.5
        
        # 根据市场环境调整权重
        self._adjust_weights_for_regime(regime)
        
        # 综合评分
        composite = (
            self.adaptive_weights["rabbit"] * r_score +
            self.adaptive_weights["mole"] * m_score +
            self.adaptive_weights["brain"] * b_score
        )
        
        # 方向判断
        if composite > self.confidence_threshold:
            if r_score > 0.65 and m_score > 0.55:
                direction = "LONG"
            elif r_score < 0.40 and m_score < 0.45:
                direction = "SHORT"
            else:
                direction = "LONG" if composite > 0.6 else "NEUTRAL"
        elif composite < (1 - self.confidence_threshold):
            direction = "SHORT"
        else:
            direction = "NEUTRAL"
        
        return composite, {
            "rabbit_score": r_score,
            "mole_score": m_score, 
            "brain_score": b_score,
            "weights": self.adaptive_weights.copy(),
            "direction": direction
        }
    
    def _adjust_weights_for_regime(self, regime: Regime):
        """根据市场环境调整权重"""
        if regime == Regime.BULL:
            # 牛市: 增加Rabbit权重
            self.adaptive_weights = {"rabbit": 0.50, "mole": 0.30, "brain": 0.20}
        elif regime == Regime.BEAR:
            # 熊市: 增加Mole权重
            self.adaptive_weights = {"rabbit": 0.30, "mole": 0.45, "brain": 0.25}
        else:
            # 震荡: 平衡
            self.adaptive_weights = {"rabbit": 0.40, "mole": 0.35, "brain": 0.25}
    
    def update_weights_from_performance(self, outcomes: Dict[str, float]):
        """根据表现更新权重 (贝叶斯更新)"""
        learning_rate = 0.1
        
        for source, outcome in outcomes.items():
            if source in self.performance_history:
                self.performance_history[source].append(outcome)
                
                # 滚动平均
                recent = self.performance_history[source][-20:]
                avg_perf = sum(recent) / len(recent) if recent else 0
                
                # 调整权重
                if avg_perf > 0.02:  # 盈利
                    if source == "rabbit":
                        self.adaptive_weights["rabbit"] = min(0.55, self.adaptive_weights["rabbit"] + learning_rate * 0.05)
                    elif source == "mole":
                        self.adaptive_weights["mole"] = min(0.50, self.adaptive_weights["mole"] + learning_rate * 0.05)
                elif avg_perf < -0.01:  # 亏损
                    if source == "rabbit":
                        self.adaptive_weights["rabbit"] = max(0.25, self.adaptive_weights["rabbit"] - learning_rate * 0.05)
                    elif source == "mole":
                        self.adaptive_weights["mole"] = max(0.25, self.adaptive_weights["mole"] - learning_rate * 0.05)
                
                # 重新归一化
                total = sum(self.adaptive_weights.values())
                self.adaptive_weights = {k: v/total for k, v in self.adaptive_weights.items()}

class HighFrequencyQuantizer:
    """
    高频量化器
    =============
    - Tick级别数据处理
    - 微观趋势检测
    - 快速信号生成
    """
    
    def __init__(self):
        self.tick_buffer = {}  # 价格缓存
        self.price_history = {}  # 历史价格
        self.volume_profile = {}  # 成交量分布
        
        # 高频参数
        self.tick_window = 5      # 5秒窗口
        self.volume_threshold = 1.5  # 1.5倍均量
        self.price_change_threshold = 0.002  # 0.2%变化
        
    def process_tick(self, symbol: str, price: float, volume: float, timestamp: str):
        """处理单个tick"""
        if symbol not in self.tick_buffer:
            self.tick_buffer[symbol] = []
            self.price_history[symbol] = []
            self.volume_profile[symbol] = []
        
        # 缓存tick数据
        self.tick_buffer[symbol].append({
            "price": price,
            "volume": volume,
            "timestamp": timestamp
        })
        
        # 保持最近60秒数据
        cutoff = datetime.now() - timedelta(seconds=60)
        self.tick_buffer[symbol] = [
            t for t in self.tick_buffer[symbol]
            if datetime.fromisoformat(t["timestamp"]) > cutoff
        ]
        
        # 更新历史价格
        self.price_history[symbol].append(price)
        if len(self.price_history[symbol]) > 1000:
            self.price_history[symbol] = self.price_history[symbol][-1000:]
        
        # 更新成交量分布
        self.volume_profile[symbol].append(volume)
        if len(self.volume_profile[symbol]) > 100:
            self.volume_profile[symbol] = self.volume_profile[symbol][-100:]
    
    def detect_micro_trend(self, symbol: str) -> Dict:
        """检测微观趋势"""
        if symbol not in self.tick_buffer or len(self.tick_buffer[symbol]) < 5:
            return {"trend": "unknown", "strength": 0, "confidence": 0}
        
        ticks = self.tick_buffer[symbol][-self.tick_window:]
        prices = [t["price"] for t in ticks]
        volumes = [t["volume"] for t in ticks]
        
        # 计算价格变化
        price_change = (prices[-1] - prices[0]) / prices[0] if prices[0] > 0 else 0
        
        # 计算成交量比率
        avg_vol = sum(self.volume_profile.get(symbol, [1])) / max(1, len(self.volume_profile.get(symbol, [1])))
        cur_vol = sum(volumes) / len(volumes) if volumes else 1
        vol_ratio = cur_vol / avg_vol if avg_vol > 0 else 1
        
        # 微观趋势判断
        if price_change > self.price_change_threshold and vol_ratio > self.volume_threshold:
            trend = "up"
            strength = min(1.0, price_change * 10 + vol_ratio * 0.3)
        elif price_change < -self.price_change_threshold and vol_ratio > self.volume_threshold:
            trend = "down"
            strength = min(1.0, abs(price_change) * 10 + vol_ratio * 0.3)
        else:
            trend = "sideways"
            strength = 0.3
        
        return {
            "trend": trend,
            "strength": strength,
            "price_change": price_change,
            "volume_ratio": vol_ratio,
            "confidence": min(1.0, strength * 1.2)
        }
    
    def get_short_term_signal(self, symbol: str) -> Signal:
        """获取短期信号"""
        micro = self.detect_micro_trend(symbol)
        
        if micro["trend"] == "up" and micro["confidence"] > 0.7:
            return Signal(
                symbol=symbol,
                source="hfq",  # high frequency quant
                direction="LONG",
                confidence=micro["confidence"],
                score=0.5 + micro["strength"] * 0.3,
                leverage=1.5
            )
        elif micro["trend"] == "down" and micro["confidence"] > 0.7:
            return Signal(
                symbol=symbol,
                source="hfq",
                direction="SHORT", 
                confidence=micro["confidence"],
                score=0.5 - micro["strength"] * 0.2,
                leverage=1.5
            )
        
        return Signal(
            symbol=symbol,
            source="hfq",
            direction="NEUTRAL",
            confidence=0.3,
            score=0.5,
            leverage=1.0
        )

class AutoSwitchEngine:
    """
    高置信度自主切换引擎
    =======================
    - 多空自主切换
    - 置信度门控
    - 快速止损
    """
    
    def __init__(self):
        self.position = None
        self.trade_history = []
        
        # 切换参数
        self.min_confidence_switch = 0.75
        self.min_confidence_entry = 0.70
        self.max_drawdown_exit = 0.03  # 3%回撤退出
        self.profit_target = 0.05       # 5%盈利目标
        self.time_based_exit = 300      # 5分钟超时
        
        # 状态
        self.current_direction = "NEUTRAL"
        self.entry_time = None
        self.entry_price = 0
        
    def should_switch(self, composite_score: float, direction: str, regime: Regime, 
                      current_price: float, high_freq_signal: Signal = None) -> Dict:
        """判断是否切换"""
        
        # 高置信度检查
        high_conf = composite_score > self.min_confidence_switch
        
        # 方向确认
        direction_confirmed = False
        if direction == "LONG" and composite_score > 0.60:
            direction_confirmed = True
        elif direction == "SHORT" and composite_score < 0.40:
            direction_confirmed = True
        
        # 高频信号确认
        hfq_confirmed = False
        if high_freq_signal:
            if high_freq_signal.direction == direction:
                hfq_confirmed = True
        
        # 综合判断
        should_enter = (
            high_conf and 
            direction_confirmed and 
            (hq_confirmed or regime != Regime.NEUTRAL)
        )
        
        # 退出判断
        should_exit = False
        exit_reason = ""
        
        if self.position:
            pnl_pct = (current_price - self.entry_price) / self.entry_price
            if self.position.direction == "SHORT":
                pnl_pct = -pnl_pct
            
            # 止盈
            if pnl_pct > self.profit_target:
                should_exit = True
                exit_reason = "profit_target"
            # 止损
            elif pnl_pct < -self.max_drawdown_exit:
                should_exit = True
                exit_reason = "stop_loss"
            # 超时
            elif self.entry_time and (datetime.now() - self.entry_time).seconds > self.time_based_exit:
                should_exit = True
                exit_reason = "time_out"
        
        return {
            "should_enter": should_enter,
            "should_exit": should_exit,
            "exit_reason": exit_reason,
            "direction": direction if should_enter else "NEUTRAL",
            "confidence": composite_score,
            "high_freq_confirmed": hfq_confirmed
        }
    
    def enter_position(self, symbol: str, direction: str, price: float, size: float, leverage: float):
        """开仓"""
        self.position = Position(
            symbol=symbol,
            direction=direction,
            size=size,
            entry_price=price,
            leverage=leverage
        )
        self.entry_time = datetime.now()
        self.current_direction = direction
        
        self.trade_history.append({
            "action": "enter",
            "symbol": symbol,
            "direction": direction,
            "price": price,
            "time": datetime.now().isoformat()
        })
    
    def exit_position(self, price: float, reason: str):
        """平仓"""
        if self.position:
            pnl = (price - self.position.entry_price) / self.position.entry_price
            if self.position.direction == "SHORT":
                pnl = -pnl
            
            self.trade_history.append({
                "action": "exit",
                "symbol": self.position.symbol,
                "direction": self.position.direction,
                "price": price,
                "pnl": pnl,
                "reason": reason,
                "time": datetime.now().isoformat()
            })
            
            self.position = None
            self.current_direction = "NEUTRAL"
            self.entry_time = None

class GO2SEIntegrator:
    """
    GO2SE 集成器
    ==============
    集成 vv6, v6i, v15
    """
    
    def __init__(self):
        self.decision_engine = WeightedDecisionEngine()
        self.hfq = HighFrequencyQuantizer()
        self.auto_switch = AutoSwitchEngine()
        
        # 系统连接
        self.systems = {
            "vv6": {"port": 8006, "status": "unknown"},
            "v6i": {"port": 8001, "status": "unknown"},
            "v15": {"port": 8015, "status": "unknown"},
        }
        
        # 策略权重
        self.strategy_weights = {
            "rabbit_v8": 0.35,
            "mole_v7": 0.30,
            "hitchhiker_v3": 0.20,
            "wool_v3": 0.15
        }
        
    def check_systems(self) -> Dict:
        """检查各系统状态"""
        import urllib.request
        
        for name, info in self.systems.items():
            try:
                url = f"http://localhost:{info['port']}/health"
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=2) as resp:
                    if resp.status == 200:
                        info["status"] = "online"
                    else:
                        info["status"] = "error"
            except:
                info["status"] = "offline"
        
        return self.systems
    
    def get_composite_signals(self, market_data: Dict) -> Dict:
        """获取综合信号"""
        
        # 1. 获取各工具信号 (从API)
        signals = {}
        
        # Rabbit V8
        try:
            import urllib.request
            url = "http://localhost:8000/api/tools/v2/rabbit/v8/top?limit=1"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
                if data.get("success"):
                    results = data.get("results", [])
                    if results:
                        r = results[0]
                        signals["rabbit"] = Signal(
                            symbol=r.get("symbol",""),
                            source="rabbit_v8",
                            direction=r.get("direction","NEUTRAL"),
                            confidence=r.get("score", 0.5),
                            score=r.get("score", 0.5),
                            leverage=r.get("leverage", 1.0)
                        )
        except: pass
        
        # Mole V7 (类似)
        try:
            url = "http://localhost:8000/api/tools/v2/mole/v7/alerts?limit=1"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
                if data.get("success"):
                    alerts = data.get("alerts", [])
                    if alerts:
                        a = alerts[0]
                        signals["mole"] = Signal(
                            symbol=a.get("symbol",""),
                            source="mole_v7",
                            direction=a.get("direction","neutral").upper(),
                            confidence=a.get("alert_score", 50) / 100,
                            score=a.get("alert_score", 50) / 100,
                            leverage=a.get("leverage", 1.0)
                        )
        except: pass
        
        # Brain
        try:
            url = "http://localhost:8000/api/tools/v2/brain/status"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
                if data.get("success"):
                    brain_data = data.get("data", {})
                    mode = brain_data.get("mode", "balanced")
                    signals["brain"] = Signal(
                        symbol="BTC",
                        source="brain",
                        direction="LONG" if mode == "left" else "SHORT" if mode == "right" else "NEUTRAL",
                        confidence=brain_data.get("left_trust", 0.5) if mode == "left" else brain_data.get("right_trust", 0.5) if mode == "right" else 0.5,
                        score=brain_data.get("left_trust", 0.5)
                    )
        except: pass
        
        # 判断市场环境
        btc_7d = market_data.get("btc_change_7d", 0)
        if btc_7d > 5:
            regime = Regime.BULL
        elif btc_7d < -5:
            regime = Regime.BEAR
        else:
            regime = Regime.NEUTRAL
        
        # 计算综合评分
        composite, details = self.decision_engine.calculate_composite_score(signals, regime)
        
        return {
            "signals": {k: {"direction": v.direction, "confidence": v.confidence, "score": v.score} for k, v in signals.items()},
            "composite_score": composite,
            "regime": regime.value,
            "details": details,
            "weights": self.decision_engine.adaptive_weights
        }
    
    def execute_cycle(self, market_data: Dict) -> Dict:
        """执行一个交易周期"""
        
        # 1. 检查系统状态
        systems = self.check_systems()
        
        # 2. 获取综合信号
        signals = self.get_composite_signals(market_data)
        
        # 3. 高频处理
        btc_price = market_data.get("btc_price", 75000)
        btc_vol = market_data.get("btc_volume", 1000000)
        self.hfq.process_tick("BTC", btc_price, btc_vol, datetime.now().isoformat())
        hfq_signal = self.hfq.get_short_term_signal("BTC")
        
        # 4. 自主切换判断
        switch_decision = self.auto_switch.should_switch(
            composite_score=signals["composite_score"],
            direction=signals["details"]["direction"],
            regime=Regime(signals["regime"]) if signals["regime"] in ["bull","bear","neutral"] else Regime.NEUTRAL,
            current_price=btc_price,
            high_freq_signal=hfq_signal
        )
        
        # 5. 执行交易
        if switch_decision["should_enter"] and not self.auto_switch.position:
            size = 0.1 * switch_decision["confidence"]
            leverage = 2.0 if switch_decision["confidence"] > 0.8 else 1.5
            self.auto_switch.enter_position(
                symbol="BTC",
                direction=switch_decision["direction"],
                price=btc_price,
                size=size,
                leverage=leverage
            )
        elif switch_decision["should_exit"] and self.auto_switch.position:
            self.auto_switch.exit_position(btc_price, switch_decision["exit_reason"])
        
        # 6. 更新权重
        if self.auto_switch.trade_history:
            recent_trades = self.auto_switch.trade_history[-5:]
            outcomes = {}
            for t in recent_trades:
                if t["action"] == "exit":
                    outcomes[t.get("source", "rabbit")] = t.get("pnl", 0)
            if outcomes:
                self.decision_engine.update_weights_from_performance(outcomes)
        
        return {
            "systems": {k: v["status"] for k, v in systems.items()},
            "signals": signals,
            "high_frequency": {
                "trend": hfq_signal.direction,
                "confidence": hfq_signal.confidence
            },
            "switch_decision": switch_decision,
            "current_position": {
                "direction": self.auto_switch.current_direction,
                "entry_price": self.auto_switch.entry_price,
                "entry_time": self.auto_switch.entry_time.isoformat() if self.auto_switch.entry_time else None
            } if self.auto_switch.position else None,
            "weights": self.decision_engine.adaptive_weights
        }

# 全局实例
_quant_core = None
def get_quant_core():
    global _quant_core
    if _quant_core is None:
        _quant_core = GO2SEIntegrator()
    return _quant_core

def get_status() -> Dict:
    core = get_quant_core()
    return {
        "systems": {k: v["status"] for k, v in core.systems.items()},
        "weights": core.decision_engine.adaptive_weights,
        "position": core.auto_switch.current_direction,
        "trade_count": len(core.auto_switch.trade_history)
    }
