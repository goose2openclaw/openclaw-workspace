#!/usr/bin/env python3
"""
🐹 打地鼠 V4 - 高频套利 + 跨市场套利并行
============================================
双引擎并行:
1. 高频套利 (HFT) - 秒级响应
2. 跨市场套利 (Cross-Market) - 分钟级机会
2026-04-04
"""

import asyncio
import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque

from .mole_v3_strategy import (
    MoleV3Strategy,
    HFTConfig,
    ArbitrageOpportunity as HFTOpportunity,
)
from .cross_market_arbitrage import (
    CrossMarketArbitrage,
    ArbitrageOpportunity as CMAOpportunity,
)

@dataclass
class MoleV4Config:
    """V4配置"""
    # HFT配置
    hft_min_spread: float = 0.001
    hft_min_volume: float = 1000000
    hft_max_position: float = 0.04
    
    # 跨市场配置
    cross_min_spread: float = 0.0015
    cross_min_volume: float = 500000
    cross_max_position: float = 0.05
    
    # 并行配置
    parallel_enabled: bool = True
    hft_weight: float = 0.6  # HFT权重60%
    cross_weight: float = 0.4  # 跨市场权重40%


@dataclass
class CombinedSignal:
    """组合信号"""
    source: str  # "hft", "cross_market", "combined"
    action: str  # "buy", "sell", "hold"
    confidence: float
    spread_pct: float
    expected_profit_pct: float
    risk_level: str  # "low", "medium", "high"
    details: dict


class MoleV4Strategy:
    """
    🐹 打地鼠 V4 - 双引擎并行
    
    两个套利引擎同时运转:
    1. HFT引擎: 捕捉秒级价格差异
    2. Cross-Market引擎: 捕捉跨交易所/三角套利
    """
    
    VERSION = "v4.0-dual-engine"
    
    def __init__(self, config: Optional[Dict] = None):
        self.name = "🐹 打地鼠V4"
        self.version = self.VERSION
        
        # V4配置
        self.v4_config = MoleV4Config()
        if config:
            self._apply_config(config)
        
        # 初始化HFT引擎
        hft_config = {
            "hft": {
                "api_timeout": 1.0,
                "max_concurrent_requests": 10,
                "connection_pool_size": 20,
                "cache_ttl": 0.5,
                "min_spread": self.v4_config.hft_min_spread,
                "min_volume": self.v4_config.hft_min_volume,
                "scan_interval": 0.5,
                "max_position": self.v4_config.hft_max_position,
                "max_total_position": 0.20,
                "stop_loss": 0.02,
                "take_profit": 0.05,
            }
        }
        self.hft_engine = MoleV3Strategy(hft_config)
        
        # 初始化跨市场引擎
        cross_config = {
            "min_spread": self.v4_config.cross_min_spread,
            "min_volume": self.v4_config.cross_min_volume,
            "max_position": self.v4_config.cross_max_position,
            "confidence_threshold": 0.6,
        }
        self.cross_engine = CrossMarketArbitrage(cross_config)
        
        # 状态
        self.positions: Dict[str, dict] = {}
        self.signals: deque = deque(maxlen=100)
        self.stats = {
            "hft_opportunities": 0,
            "cross_opportunities": 0,
            "combined_signals": 0,
            "total_trades": 0,
            "hft_trades": 0,
            "cross_trades": 0,
        }
    
    def _apply_config(self, config: Dict):
        """应用配置"""
        if "v4" in config:
            v4 = config["v4"]
            for key in ["hft_min_spread", "hft_min_volume", "cross_min_spread"]:
                if key in v4:
                    setattr(self.v4_config, key, v4[key])
    
    # ═══════════════════════════════════════════════════════════════════
    # 双引擎并行扫描
    # ═══════════════════════════════════════════════════════════════════
    
    async def scan_parallel(self, symbols: List[str]) -> Dict[str, any]:
        """并行扫描两种套利机会"""
        start_time = time.time()
        
        # 并行执行两个引擎
        hft_task = self.hft_engine.scan_arbitrage(symbols)
        cross_task = self.cross_engine.scan_all(symbols)
        
        hft_opps, cross_result = await asyncio.gather(
            hft_task,
            cross_task,
            return_exceptions=True
        )
        
        # 处理HFT结果
        if isinstance(hft_opps, Exception):
            hft_opps = []
        
        # 处理跨市场结果
        if isinstance(cross_result, Exception):
            cross_result = {"exchange": [], "triangle": [], "total": 0}
        
        scan_time_ms = (time.time() - start_time) * 1000
        
        return {
            "hft": hft_opps if not isinstance(hft_opps, Exception) else [],
            "cross_exchange": cross_result.get("exchange", []) if isinstance(cross_result, dict) else [],
            "cross_triangle": cross_result.get("triangle", []) if isinstance(cross_result, dict) else [],
            "scan_time_ms": scan_time_ms,
            "total_opportunities": len(hft_opps) + cross_result.get("total", 0) if isinstance(cross_result, dict) else 0,
        }
    
    async def generate_combined_signal(self, scan_result: Dict) -> CombinedSignal:
        """生成组合信号"""
        hft_opps = scan_result.get("hft", [])
        cross_exchange = scan_result.get("cross_exchange", [])
        cross_triangle = scan_result.get("cross_triangle", [])
        
        # 计算加权置信度
        total_opps = len(hft_opps) + len(cross_exchange) + len(cross_triangle)
        
        if total_opps == 0:
            return CombinedSignal(
                source="none",
                action="hold",
                confidence=0,
                spread_pct=0,
                expected_profit_pct=0,
                risk_level="low",
                details={"reason": "no_opportunities"}
            )
        
        # HFT贡献
        hft_confidence = 0
        hft_spread = 0
        if hft_opps:
            hft_confidence = max(opp.confidence for opp in hft_opps)
            hft_spread = max(opp.spread_pct for opp in hft_opps)
        
        # 跨市场贡献
        cross_confidence = 0
        cross_spread = 0
        cross_opps = cross_exchange + cross_triangle
        if cross_opps:
            cross_confidence = max(opp.confidence for opp in cross_opps)
            cross_spread = max(opp.spread_pct for opp in cross_opps)
        
        # 加权组合
        combined_confidence = (
            hft_confidence * self.v4_config.hft_weight +
            cross_confidence * self.v4_config.cross_weight
        )
        combined_spread = (
            hft_spread * self.v4_config.hft_weight +
            cross_spread * self.v4_config.cross_weight
        )
        
        # 确定动作
        if combined_spread >= self.v4_config.hft_min_spread * 1.5:
            action = "buy"
            source = "hft" if hft_spread > cross_spread else "cross_market"
        elif combined_confidence > 0.7:
            action = "buy"
            source = "combined"
        else:
            action = "hold"
            source = "none"
        
        # 风险等级
        if combined_spread > 0.01:  # >1%
            risk = "high"
        elif combined_spread > 0.005:  # >0.5%
            risk = "medium"
        else:
            risk = "low"
        
        signal = CombinedSignal(
            source=source,
            action=action,
            confidence=combined_confidence,
            spread_pct=combined_spread,
            expected_profit_pct=combined_spread - 0.002,  # 扣除手续费
            risk_level=risk,
            details={
                "hft_opps": len(hft_opps),
                "cross_opps": len(cross_opps),
                "hft_confidence": hft_confidence,
                "cross_confidence": cross_confidence,
            }
        )
        
        self.signals.append(signal)
        self.stats["combined_signals"] += 1
        
        return signal
    
    # ═══════════════════════════════════════════════════════════════════
    # 执行交易
    # ═══════════════════════════════════════════════════════════════════
    
    async def execute_combined(self, scan_result: Dict) -> List[dict]:
        """执行组合交易"""
        results = []
        
        # 执行HFT机会
        for opp in scan_result.get("hft", [])[:3]:  # 最多3个
            result = await self.hft_engine.execute_arbitrage(opp)
            if result["status"] == "executed":
                results.append({**result, "engine": "hft"})
                self.stats["hft_trades"] += 1
                self.stats["total_trades"] += 1
        
        # 执行跨市场机会
        for opp in scan_result.get("cross_exchange", [])[:2]:  # 最多2个
            result = await self.cross_engine.execute_opportunity(opp)
            if result["status"] == "executed":
                results.append({**result, "engine": "cross_market"})
                self.stats["cross_trades"] += 1
                self.stats["total_trades"] += 1
        
        return results
    
    # ═══════════════════════════════════════════════════════════════════
    # 状态管理
    # ═══════════════════════════════════════════════════════════════════
    
    def get_stats(self) -> dict:
        """获取统计"""
        return {
            **self.stats,
            "hft_engine": self.hft_engine.get_stats(),
            "cross_engine": self.cross_engine.get_stats(),
            "config": {
                "hft_weight": self.v4_config.hft_weight,
                "cross_weight": self.v4_config.cross_weight,
            }
        }
    
    async def close(self):
        """关闭所有引擎"""
        await self.hft_engine.close()
        await self.cross_engine.close()


# 导出
__all__ = [
    "MoleV4Strategy",
    "MoleV4Config",
    "CombinedSignal",
]
