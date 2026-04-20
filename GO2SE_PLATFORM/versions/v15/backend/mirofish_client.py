"""
====================================================================
  MiroFish Platform Client
  vv6 和 v15 共享的 MiroFish 集成客户端

功能:
  1. 查询 MiroFish Mi 值
  2. 报告交易结果到 MiroFish (用于权重优化)
  3. 查询仲裁结果
  4. 组合配置查询
====================================================================
"""

import httpx
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime

MIROFISH_URL = "http://localhost:8020"
SROPTIMIZER_URL = "http://localhost:8021"

class MiroFishClient:
    """MiroFish Platform Engine 客户端"""

    def __init__(self, strategy_name: str = "vv6"):
        self.strategy_name = strategy_name
        self.base_url = MIROFISH_URL
        self.timeout = 10.0
        self._mi_cache: Optional[float] = None
        self._mi_cache_time: float = 0

    async def get_mi(
        self,
        regime: str,
        rsi: float,
        fear_greed: float,
        dimension_overrides: Optional[Dict[str, float]] = None,
        use_cache: bool = True,
    ) -> float:
        """
        获取 Mi (市场调整系数)
        缓存 30 秒，避免重复请求
        """
        import time
        now = time.time()
        if use_cache and self._mi_cache is not None and (now - self._mi_cache_time) < 30:
            return self._mi_cache

        payload = {
            "regime": regime,
            "rsi": rsi,
            "fear_greed": fear_greed,
        }
        if dimension_overrides:
            payload["dimension_overrides"] = dimension_overrides

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(f"{self.base_url}/mi", json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    mi = data.get("mi", 1.0)
                    self._mi_cache = mi
                    self._mi_cache_time = now
                    return mi
        except Exception as e:
            print(f"[MiroFishClient] get_mi error: {e}")
        return 1.0  # fallback

    async def report_outcome(
        self,
        strategy: str,
        outcome: str,  # "WIN" | "LOSS"
        confidence: float,
        direction: str,
    ) -> Dict[str, Any]:
        """
        报告交易结果到 MiroFish (更新 Kelly 权重)
        """
        payload = {
            "strategy": strategy,
            "outcome": outcome,
            "confidence": confidence,
            "direction": direction,
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(f"{self.base_url}/strategy-weights", json=payload)
                if resp.status_code == 200:
                    return resp.json()
        except Exception as e:
            print(f"[MiroFishClient] report_outcome error: {e}")
        return {}

    async def get_strategy_weights(self) -> Dict[str, float]:
        """获取当前策略权重"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(f"{self.base_url}/strategy-weights")
                if resp.status_code == 200:
                    return resp.json().get("weights", {})
        except Exception as e:
            print(f"[MiroFishClient] get_strategy_weights error: {e}")
        return {"vv6": 0.4, "v15": 0.4, "coordinator": 0.2}

    async def update_dimension(
        self,
        dimension: str,
        score: float,
        source: Optional[str] = None,
    ) -> Dict[str, Any]:
        """更新指定维度评分"""
        payload = {
            "dimension": dimension,
            "score": score,
            "source": source or self.strategy_name,
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(f"{self.base_url}/dimensions/update", json=payload)
                if resp.status_code == 200:
                    return resp.json()
        except Exception as e:
            print(f"[MiroFishClient] update_dimension error: {e}")
        return {}

    async def arbitrate(
        self,
        vv6_signal: Dict,
        v15_signal: Dict,
        regime: str,
        rsi: float,
        fear_greed: float,
    ) -> Dict[str, Any]:
        """
        请求 MiroFish 仲裁 vv6 vs v15 信号
        """
        payload = {
            "vv6_signal": vv6_signal,
            "v15_signal": v15_signal,
            "regime": regime,
            "rsi": rsi,
            "fear_greed": fear_greed,
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(f"{self.base_url}/arbitrate", json=payload)
                if resp.status_code == 200:
                    return resp.json()
        except Exception as e:
            print(f"[MiroFishClient] arbitrate error: {e}")
        return {"decision": "error", "error": str(e)}

    async def get_portfolio_allocation(
        self,
        regime: str,
        rsi: float,
        fear_greed: float,
        vv6_confidence: float,
        v15_confidence: float,
        coordinator_confidence: float,
        vv6_direction: str,
        v15_direction: str,
        coordinator_direction: str,
    ) -> Dict[str, Any]:
        """Kelly 组合配置"""
        payload = {
            "regime": regime,
            "rsi": rsi,
            "fear_greed": fear_greed,
            "vv6_confidence": vv6_confidence,
            "v15_confidence": v15_confidence,
            "coordinator_confidence": coordinator_confidence,
            "vv6_direction": vv6_direction,
            "v15_direction": v15_direction,
            "coordinator_direction": coordinator_direction,
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(f"{self.base_url}/portfolio/allocate", json=payload)
                if resp.status_code == 200:
                    return resp.json()
        except Exception as e:
            print(f"[MiroFishClient] get_portfolio_allocation error: {e}")
        return {}

    def get_mi_sync(self, regime: str, rsi: float, fear_greed: float) -> float:
        """同步版本: 获取 Mi (用于非async上下文)"""
        import urllib.request
        import json
        url = f"{self.base_url}/mi?regime={regime}&rsi={rsi}&fear_greed={fear_greed}"
        try:
            with urllib.request.urlopen(url, timeout=5) as resp:
                data = json.loads(resp.read())
                return data.get("mi", 1.0)
        except Exception:
            return 1.0

# ─── 全局客户端实例 ────────────────────────────────────────────
_client: Optional[MiroFishClient] = None

def get_mirofish_client(strategy: str = "vv6") -> MiroFishClient:
    global _client
    if _client is None:
        _client = MiroFishClient(strategy_name=strategy)
    return _client