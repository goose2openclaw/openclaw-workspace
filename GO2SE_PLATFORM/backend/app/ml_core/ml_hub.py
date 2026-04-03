"""
ML Hub - 机器学习能力中心
===========================
GO2SE ML能力统一入口
调度7大ML模块协同工作
"""
import logging
from typing import Dict, Any, Optional
from .quant_engine import QuantEngine
from .strategy_optimizer import StrategyOptimizer
from .predictor import Predictor
from .airdrop_hunter import AirdropHunter
from .compute_scheduler import ComputeScheduler
from .win_rate import WinRatePredictor
from .crowdsignal import CrowdSignal

logger = logging.getLogger(__name__)


class MLHub:
    """
    GO2SE ML能力中心
    =================
    统一调度7大ML模块:
    1. QuantEngine       - 量化引擎
    2. StrategyOptimizer - 策略优化
    3. Predictor        - 价格/趋势预测
    4. AirdropHunter    - 空投猎手
    5. ComputeScheduler  - 算力调度
    6. WinRatePredictor  - 胜率预测
    7. CrowdSignal      - 众包信号
    """

    def __init__(self):
        self.modules = {}
        self._init_modules()
        self.stats = {
            "queries_handled": 0,
            "predictions_made": 0,
            "cache_hits": 0,
        }

    def _init_modules(self):
        self.modules = {
            "quant": QuantEngine(),
            "optimizer": StrategyOptimizer(),
            "predictor": Predictor(),
            "airdrop": AirdropHunter(),
            "compute": ComputeScheduler(),
            "winrate": WinRatePredictor(),
            "crowdsignal": CrowdSignal(),
        }
        logger.info(f"ML Hub initialized with {len(self.modules)} modules")

    async def query(self, module: str, operation: str, **kwargs) -> Dict[str, Any]:
        """
        统一查询接口
        Usage: ml_hub.query("predictor", "price", symbol="BTC", horizon="1h")
        """
        self.stats["queries_handled"] += 1
        if module not in self.modules:
            return {"error": f"Unknown module: {module}"}

        mod = self.modules[module]
        op = getattr(mod, operation, None)
        if not op:
            return {"error": f"Unknown operation: {operation}"}

        try:
            result = op(**kwargs) if kwargs else op()
            self.stats["predictions_made"] += 1
            return {"success": True, "data": result}
        except Exception as e:
            logger.error(f"ML Hub query error: {e}")
            return {"success": False, "error": str(e)}

    def get_capabilities(self) -> Dict[str, Any]:
        """返回ML能力清单"""
        capabilities = {}
        for name, mod in self.modules.items():
            capabilities[name] = {
                "status": "active",
                "methods": [m for m in dir(mod) if not m.startswith("_")],
                "metrics": getattr(mod, "metrics", {}),
            }
        return {
            "hub_status": "operational",
            "modules": capabilities,
            "stats": self.stats,
        }
