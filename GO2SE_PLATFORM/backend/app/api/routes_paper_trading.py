"""
Paper Trading API Routes - 模拟交易API
===================================
供游客和不同群体使用的模拟交易模块
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import random
import uuid

router = APIRouter(prefix="/api/paper", tags=["模拟交易"])


# ── 模拟交易者类型 ─────────────────────────────────────────────

USER_TYPES = {
    "visitor": {"name": "游客", "initial_capital": 1000.0, "features": ["basic"]},
    "beginner": {"name": "初学者", "initial_capital": 5000.0, "features": ["basic", "signals"]},
    "trader": {"name": "交易者", "initial_capital": 10000.0, "features": ["basic", "signals", "strategies"]},
    "pro": {"name": "专业", "initial_capital": 50000.0, "features": ["all"]},
    "institutional": {"name": "机构", "initial_capital": 100000.0, "features": ["all", "api"]},
}


# ── Pydantic Models ─────────────────────────────────────────────

class CreatePaperAccount(BaseModel):
    user_type: str = "visitor"
    username: Optional[str] = None


class PaperPosition(BaseModel):
    position_id: str
    symbol: str
    side: str  # LONG / SHORT
    entry_price: float
    current_price: float
    size: float
    pnl: float
    pnl_pct: float
    leverage: int
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    opened_at: str


class PaperOrder(BaseModel):
    order_id: str
    symbol: str
    side: str
    order_type: str  # MARKET / LIMIT
    price: Optional[float]
    size: float
    filled: bool
    filled_price: Optional[float]
    created_at: str


class PaperPortfolio(BaseModel):
    user_id: str
    user_type: str
    username: str
    initial_capital: float
    current_capital: float
    total_pnl: float
    total_pnl_pct: float
    positions: List[PaperPosition]
    available_capital: float
    margin_used: float


# ── 模拟账户管理器 ─────────────────────────────────────────────

class PaperTradingManager:
    """模拟交易管理器"""

    def __init__(self):
        self.accounts: Dict[str, Dict] = {}
        self.positions: Dict[str, List] = {}
        self.orders: Dict[str, List] = {}

    def create_account(self, user_type: str, username: str = None) -> Dict:
        user_id = str(uuid.uuid4())[:8]
        config = USER_TYPES.get(user_type, USER_TYPES["visitor"])

        self.accounts[user_id] = {
            "user_id": user_id,
            "user_type": user_type,
            "username": username or f"user_{user_id}",
            "initial_capital": config["initial_capital"],
            "current_capital": config["initial_capital"],
            "available_capital": config["initial_capital"],
            "margin_used": 0.0,
            "total_pnl": 0.0,
            "total_pnl_pct": 0.0,
            "features": config["features"],
            "created_at": datetime.utcnow().isoformat(),
        }
        self.positions[user_id] = []
        self.orders[user_id] = []
        return self.accounts[user_id]

    def get_portfolio(self, user_id: str) -> Optional[PaperPortfolio]:
        if user_id not in self.accounts:
            return None

        account = self.accounts[user_id]
        positions = self.positions.get(user_id, [])

        # 更新持仓市值
        for pos in positions:
            pos["current_price"] = pos["current_price"] * random.uniform(0.98, 1.02)
            pos["pnl"] = (pos["current_price"] - pos["entry_price"]) * pos["size"] * (1 if pos["side"] == "LONG" else -1)
            pos["pnl_pct"] = (pos["pnl"] / (pos["entry_price"] * pos["size"])) * 100

        # 更新账户
        total_pnl = sum(p["pnl"] for p in positions)
        account["total_pnl"] = total_pnl
        account["total_pnl_pct"] = (total_pnl / account["initial_capital"]) * 100
        account["current_capital"] = account["initial_capital"] + total_pnl
        account["margin_used"] = sum(p["entry_price"] * p["size"] * (1 / p["leverage"]) for p in positions)
        account["available_capital"] = account["current_capital"] - account["margin_used"]

        return PaperPortfolio(
            user_id=user_id,
            user_type=account["user_type"],
            username=account["username"],
            initial_capital=account["initial_capital"],
            current_capital=account["current_capital"],
            total_pnl=round(account["total_pnl"], 2),
            total_pnl_pct=round(account["total_pnl_pct"], 2),
            positions=positions,
            available_capital=round(account["available_capital"], 2),
            margin_used=round(account["margin_used"], 2),
        )

    def open_position(
        self,
        user_id: str,
        symbol: str,
        side: str,
        size: float,
        leverage: int = 1,
        entry_price: float = None,
        stop_loss: float = None,
        take_profit: float = None,
    ) -> Optional[PaperPosition]:
        if user_id not in self.accounts:
            return None

        account = self.accounts[user_id]

        # 估算开仓价格
        if entry_price is None:
            entry_price = random.uniform(30000, 70000)  # BTC价格

        margin_required = (entry_price * size) / leverage
        if margin_required > account["available_capital"]:
            raise HTTPException(status_code=400, detail="资金不足")

        position_id = str(uuid.uuid4())[:12]
        position = {
            "position_id": position_id,
            "symbol": symbol,
            "side": side,
            "entry_price": entry_price,
            "current_price": entry_price,
            "size": size,
            "pnl": 0.0,
            "pnl_pct": 0.0,
            "leverage": leverage,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "opened_at": datetime.utcnow().isoformat(),
        }

        self.positions[user_id].append(position)
        self._create_order(user_id, symbol, side, "MARKET", entry_price, size, True, entry_price)

        return PaperPosition(**position)

    def close_position(self, user_id: str, position_id: str) -> bool:
        if user_id not in self.accounts:
            return False

        positions = self.positions.get(user_id, [])
        for i, pos in enumerate(positions):
            if pos["position_id"] == position_id:
                # 更新最终价格
                pos["current_price"] = pos["current_price"] * random.uniform(0.95, 1.05)
                pos["pnl"] = (pos["current_price"] - pos["entry_price"]) * pos["size"] * (1 if pos["side"] == "LONG" else -1)
                self._create_order(user_id, pos["symbol"], "SHORT" if pos["side"] == "LONG" else "LONG", "MARKET", pos["current_price"], pos["size"], True, pos["current_price"])
                positions.pop(i)
                return True
        return False

    def _create_order(self, user_id: str, symbol: str, side: str, order_type: str, price: float, size: float, filled: bool, filled_price: float = None):
        order_id = str(uuid.uuid4())[:12]
        order = {
            "order_id": order_id,
            "symbol": symbol,
            "side": side,
            "order_type": order_type,
            "price": price,
            "size": size,
            "filled": filled,
            "filled_price": filled_price or price,
            "created_at": datetime.utcnow().isoformat(),
        }
        self.orders[user_id].append(order)


_manager = PaperTradingManager()


# ── API Routes ─────────────────────────────────────────────────

@router.get("/user_types")
async def get_user_types():
    """获取模拟交易者类型"""
    return {"user_types": USER_TYPES}


@router.post("/account")
async def create_account(body: CreatePaperAccount):
    """
    创建模拟账户
    POST /api/paper/account
    """
    if body.user_type not in USER_TYPES:
        raise HTTPException(status_code=400, detail="无效的用户类型")

    account = _manager.create_account(body.user_type, body.username)
    return account


@router.get("/portfolio/{user_id}")
async def get_portfolio(user_id: str):
    """
    获取模拟投资组合
    GET /api/paper/portfolio/{user_id}
    """
    portfolio = _manager.get_portfolio(user_id)
    if portfolio is None:
        raise HTTPException(status_code=404, detail="账户不存在")
    return portfolio


@router.post("/position/open")
async def open_position(
    user_id: str,
    symbol: str,
    side: str,
    size: float,
    leverage: int = 1,
    entry_price: float = None,
    stop_loss: float = None,
    take_profit: float = None,
):
    """
    开仓
    POST /api/paper/position/open
    """
    try:
        position = _manager.open_position(
            user_id=user_id,
            symbol=symbol,
            side=side,
            size=size,
            leverage=leverage,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
        )
        if position is None:
            raise HTTPException(status_code=404, detail="账户不存在")
        return position
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/position/close")
async def close_position(user_id: str, position_id: str):
    """
    平仓
    POST /api/paper/position/close
    """
    success = _manager.close_position(user_id, position_id)
    if not success:
        raise HTTPException(status_code=404, detail="持仓不存在")
    return {"status": "closed", "position_id": position_id}


@router.get("/orders/{user_id}")
async def get_orders(user_id: str, limit: int = 20):
    """获取订单历史"""
    if user_id not in _manager.orders:
        return {"orders": []}
    orders = _manager.orders[user_id][-limit:]
    return {"orders": orders, "total": len(_manager.orders[user_id])}


@router.post("/reset/{user_id}")
async def reset_account(user_id: str):
    """重置模拟账户"""
    if user_id in _manager.accounts:
        config = USER_TYPES.get(_manager.accounts[user_id]["user_type"], USER_TYPES["visitor"])
        _manager.accounts[user_id]["current_capital"] = config["initial_capital"]
        _manager.accounts[user_id]["available_capital"] = config["initial_capital"]
        _manager.accounts[user_id]["total_pnl"] = 0.0
        _manager.accounts[user_id]["total_pnl_pct"] = 0.0
        _manager.accounts[user_id]["margin_used"] = 0.0
        _manager.positions[user_id] = []
        _manager.orders[user_id] = []
        return {"status": "reset", "user_id": user_id}
    raise HTTPException(status_code=404, detail="账户不存在")
