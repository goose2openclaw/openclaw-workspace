"""
🔗 北斗七鑫统一集成层
======================
整合多策略、跨市场、机器学习到现有架构

在不改变原有策略架构的情况下，提供:
- 多策略并行
- 跨市场扩展
- ML增强预测
"""

from typing import Dict, List
from .multi_strategy_engine import multi_strategy_engine, MultiStrategyEngine
from .cross_market_engine import cross_market_engine, CrossMarketEngine, Market
from .ml_engine import ml_engine, MLEngine


class BeidouIntegrator:
    """
    北斗七鑫统一集成器
    =================
    
    对外提供统一的接口，不改变原有架构
    """
    
    def __init__(self):
        self.multi_strategy = multi_strategy_engine
        self.cross_market = cross_market_engine
        self.ml = ml_engine
    
    async def get_enhanced_signal(self, symbol: str, market: Market = Market.CRYPTO) -> Dict:
        """
        获取增强信号
        ============
        整合多策略 + ML预测
        """
        # 1. 获取ML预测
        ml_signal = self.ml.get_combined_signal(symbol)
        
        # 2. 获取多策略信号
        strategy_signals = await self.multi_strategy.run_parallel([symbol])
        aggregated = self.multi_strategy.aggregate_signals(
            strategy_signals.get(symbol, [])
        )
        
        # 3. 组合信号
        # ML权重30%，策略权重70%
        final_confidence = ml_signal["confidence"] * 0.3 + aggregated["confidence"] * 0.7
        
        # 方向一致性检查
        if ml_signal["action"] != aggregated["direction"]:
            # 不一致，降低置信度
            final_confidence *= 0.8
        
        return {
            "symbol": symbol,
            "market": market.value,
            "direction": aggregated["direction"],
            "confidence": final_confidence,
            "leverage": aggregated.get("leverage", 2),
            "ml_signal": ml_signal,
            "strategy_signals": {
                "votes": aggregated.get("votes", {}),
                "count": aggregated.get("signal_count", 0)
            },
            "sources": {
                "multi_strategy": True,
                "cross_market": True,
                "ml_enhanced": True
            }
        }
    
    async def scan_all(self) -> Dict:
        """
        全市场扫描
        =========
        返回所有市场的增强信号
        """
        results = {}
        
        # 获取所有启用的市场
        enabled_markets = self.cross_market.get_enabled_markets()
        
        for market in enabled_markets:
            config = self.cross_market.markets[market]
            market_signals = []
            
            for symbol in config.symbols:
                signal = await self.get_enhanced_signal(symbol, market)
                market_signals.append(signal)
            
            results[market.value] = {
                "name": config.name,
                "weight": config.weight,
                "signals": market_signals
            }
        
        return results
    
    def get_portfolio_allocation(self) -> Dict:
        """
        获取组合配置
        ===========
        基于跨市场配置分配资金
        """
        allocation = self.cross_market.get_allocation()
        
        # 添加策略权重
        strategy_weights = {
            "mirofish": 0.30,
            "sonar": 0.25,
            "expert": 0.25,
            "ml_enhanced": 0.20
        }
        
        return {
            "market_allocation": allocation,
            "strategy_weights": strategy_weights,
            "total_markets": len(self.cross_market.get_enabled_markets())
        }
    
    def get_status(self) -> Dict:
        """获取集成状态"""
        return {
            "multi_strategy": self.multi_strategy.get_status(),
            "cross_market": self.cross_market.get_status(),
            "ml": self.ml.get_status()
        }


# 全局实例
beidou_integrator = BeidouIntegrator()


if __name__ == "__main__":
    print("✅ 北斗七鑫集成层已初始化")
    status = beidou_integrator.get_status()
    print(f"\n多策略引擎: {status['multi_strategy']['registered_count']}个策略")
    print(f"跨市场: {status['cross_market']['enabled_markets']}个市场启用")
    print(f"ML模型: {len(status['ml']['models'])}个模型")
