#!/usr/bin/env python3
"""
📈 Binance Futures 做空机制
===========================
支持做多/做空双向交易
杠杆率配置
条件单和止损止盈
"""

import hmac
import hashlib
import time
import json
import requests
from typing import Dict, Optional, Tuple, List
from datetime import datetime
from urllib.parse import urlencode

BINANCE_FUTURES_API = "https://fapi.binance.com"


class BinanceFuturesTrader:
    """Binance Futures 做空交易引擎"""

    def __init__(self, api_key: str = "", secret_key: str = ""):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = BINANCE_FUTURES_API
        self.test_mode = not api_key  # 无key时用模拟

        # 杠杆档位配置
        self.leverage_tiers = {
            "conservative": {"multiplier": 2, "max_position": 0.10},
            "moderate": {"multiplier": 3, "max_position": 0.20},
            "aggressive": {"multiplier": 5, "max_position": 0.25},
            "expert": {"multiplier": 10, "max_position": 0.30},
        }

    # ─── 签名生成 ───────────────────────────────────────────────
    def _sign(self, params: dict) -> str:
        query = urlencode(params)
        signature = hmac.new(
            self.secret_key.encode(), query.encode(), hashlib.sha256
        ).hexdigest()
        return signature

    def _headers(self) -> dict:
        return {
            "X-MBX-APIKEY": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded",
        }

    # ─── 市场数据 ───────────────────────────────────────────────
    def get_ticker(self, symbol: str) -> Dict:
        """获取合约行情"""
        if self.test_mode:
            return self._mock_ticker(symbol)
        try:
            url = f"{self.base_url}/fapi/v1/ticker/24hr"
            params = {"symbol": symbol.upper().replace("/", "")}
            r = requests.get(url, params=params, timeout=5)
            d = r.json()
            return {
                "symbol": d["symbol"],
                "price": float(d["lastPrice"]),
                "change_24h": float(d["priceChangePercent"]),
                "volume": float(d["quoteVolume"]),
                "high": float(d["highPrice"]),
                "low": float(d["lowPrice"]),
                "bid": float(d["bidPrice"]),
                "ask": float(d["askPrice"]),
            }
        except Exception:
            return self._mock_ticker(symbol)

    def _mock_ticker(self, symbol: str) -> Dict:
        """模拟行情（测试用）"""
        import random
        price = 75000 if "BTC" in symbol else 3500
        return {
            "symbol": symbol.upper().replace("/", "USDT"),
            "price": price,
            "change_24h": random.uniform(-5, 5),
            "volume": random.uniform(1e8, 5e8),
            "high": price * 1.02,
            "low": price * 0.98,
            "bid": price * 0.999,
            "ask": price * 1.001,
        }

    # ─── 订单操作 ───────────────────────────────────────────────
    def set_leverage(self, symbol: str, leverage: int) -> Dict:
        """设置杠杆倍数"""
        if self.test_mode:
            return {"symbol": symbol, "leverage": leverage, "success": True}
        try:
            url = f"{self.base_url}/fapi/v1/leverage"
            ts = int(time.time() * 1000)
            params = {"symbol": symbol.upper().replace("/", ""), "leverage": leverage, "timestamp": ts}
            params["signature"] = self._sign(params)
            r = requests.post(url, headers=self._headers(), params=params, timeout=5)
            return {"symbol": symbol, "leverage": leverage, "success": True}
        except Exception as e:
            return {"symbol": symbol, "leverage": leverage, "success": False, "error": str(e)}

    def place_order(
        self,
        symbol: str,
        side: str,  # BUY (做多) / SELL (做空)
        position_side: str,  # LONG / SHORT
        order_type: str = "MARKET",
        quantity: float = 0,
        price: float = 0,
        leverage: int = 3,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
    ) -> Dict:
        """
        下单（做多或做空）
        
        Args:
            symbol: 交易对如 BTCUSDT
            side: BUY(开多) / SELL(开空/平多)
            position_side: LONG / SHORT
            order_type: MARKET / LIMIT
            quantity: 数量（张）
            price: 限价价格
            leverage: 杠杆倍数
            stop_loss: 止损价
            take_profit: 止盈价
        """
        if self.test_mode:
            return self._mock_order(symbol, side, position_side, quantity, leverage)

        try:
            # 1. 设置杠杆
            self.set_leverage(symbol, leverage)

            # 2. 市价开仓
            url = f"{self.base_url}/fapi/v1/order"
            ts = int(time.time() * 1000)
            params = {
                "symbol": symbol.upper().replace("/", ""),
                "side": side,
                "positionSide": position_side,
                "type": order_type,
                "quantity": quantity,
                "timestamp": ts,
            }
            if order_type == "LIMIT":
                params["price"] = price
                params["timeInForce"] = "GTC"
            params["signature"] = self._sign(params)
            r = requests.post(url, headers=self._headers(), params=params, timeout=5)
            order = r.json()

            # 3. 设置止损止盈（条件单）
            if stop_loss or take_profit:
                self._set_sl_tp(symbol, side, position_side, stop_loss, take_profit, quantity)

            return {
                "success": True,
                "order_id": order.get("orderId", "SIM"),
                "symbol": symbol,
                "side": side,
                "position_side": position_side,
                "leverage": leverage,
                "price": float(order.get("avgPrice", 0)),
                "quantity": quantity,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _set_sl_tp(
        self, symbol: str, side: str, position_side: str,
        stop_loss: Optional[float], take_profit: Optional[float], quantity: float
    ):
        """设置止损止盈条件单"""
        try:
            url = f"{self.base_url}/fapi/v1/order"
            ts = int(time.time() * 1000)
            # 止损
            if stop_loss:
                sl_side = "SELL" if position_side == "LONG" else "BUY"
                params = {
                    "symbol": symbol.upper().replace("/", ""),
                    "side": sl_side,
                    "positionSide": position_side,
                    "type": "STOP_MARKET",
                    "stopPrice": stop_loss,
                    "closePosition": True,
                    "timestamp": ts,
                }
                params["signature"] = self._sign(params)
                requests.post(url, headers=self._headers(), params=params, timeout=5)
            # 止盈
            if take_profit:
                tp_side = "SELL" if position_side == "LONG" else "BUY"
                params = {
                    "symbol": symbol.upper().replace("/", ""),
                    "side": tp_side,
                    "positionSide": position_side,
                    "type": "TAKE_PROFIT_MARKET",
                    "stopPrice": take_profit,
                    "closePosition": True,
                    "timestamp": ts,
                }
                params["signature"] = self._sign(params)
                requests.post(url, headers=self._headers(), params=params, timeout=5)
        except Exception:
            pass

    def _mock_order(self, symbol: str, side: str, position_side: str, quantity: float, leverage: int) -> Dict:
        """模拟订单（dry_run模式）"""
        ticker = self.get_ticker(symbol)
        price = ticker["price"]
        return {
            "success": True,
            "order_id": f"DRY_{int(time.time())}",
            "symbol": symbol,
            "side": side,
            "position_side": position_side,
            "leverage": leverage,
            "price": price,
            "quantity": quantity,
            "mode": "dry_run",
            "timestamp": datetime.now().isoformat(),
        }

    # ─── 仓位查询 ───────────────────────────────────────────────
    def get_position(self, symbol: str) -> Dict:
        """查询当前仓位"""
        if self.test_mode:
            return {
                "symbol": symbol,
                "position_side": "NONE",
                "size": 0,
                "entry_price": 0,
                "unrealized_pnl": 0,
                "margin": 0,
            }
        try:
            url = f"{self.base_url}/fapi/v2/positionRisk"
            ts = int(time.time() * 1000)
            params = {"symbol": symbol.upper().replace("/", ""), "timestamp": ts}
            params["signature"] = self._sign(params)
            r = requests.get(url, headers=self._headers(), params=params, timeout=5)
            positions = r.json()
            for pos in positions:
                if pos["symbol"] == symbol.upper().replace("/", ""):
                    return {
                        "symbol": symbol,
                        "position_side": pos.get("positionSide", "BOTH"),
                        "size": float(pos.get("positionAmt", 0)),
                        "entry_price": float(pos.get("entryPrice", 0)),
                        "unrealized_pnl": float(pos.get("unRealizedProfit", 0)),
                        "margin": float(pos.get("isolatedMargin", 0)),
                    }
            return {"symbol": symbol, "position_side": "NONE", "size": 0}
        except Exception:
            return {"symbol": symbol, "position_side": "NONE", "size": 0}

    # ─── 平仓 ────────────────────────────────────────────────
    def close_position(self, symbol: str, position_side: str) -> Dict:
        """平仓"""
        pos = self.get_position(symbol)
        if pos["size"] == 0:
            return {"success": True, "message": "无持仓"}
        close_side = "BUY" if position_side == "SHORT" else "SELL"
        return self.place_order(symbol, close_side, position_side, quantity=abs(pos["size"]))


# ─── 快捷函数 ───────────────────────────────────────────────
_trader: Optional[BinanceFuturesTrader] = None


def get_trader(api_key: str = "", secret_key: str = "") -> BinanceFuturesTrader:
    global _trader
    if _trader is None:
        _trader = BinanceFuturesTrader(api_key, secret_key)
    return _trader


def open_short(symbol: str, quantity: float, leverage: int = 3, **kwargs) -> Dict:
    """快捷做空"""
    trader = get_trader()
    return trader.place_order(
        symbol=symbol,
        side="SELL",
        position_side="SHORT",
        quantity=quantity,
        leverage=leverage,
        **kwargs
    )


def open_long(symbol: str, quantity: float, leverage: int = 3, **kwargs) -> Dict:
    """快捷做多"""
    trader = get_trader()
    return trader.place_order(
        symbol=symbol,
        side="BUY",
        position_side="LONG",
        quantity=quantity,
        leverage=leverage,
        **kwargs
    )


def close_short(symbol: str) -> Dict:
    """平做空"""
    trader = get_trader()
    return trader.close_position(symbol, "SHORT")


def close_long(symbol: str) -> Dict:
    """平做多"""
    trader = get_trader()
    return trader.close_position(symbol, "LONG")
