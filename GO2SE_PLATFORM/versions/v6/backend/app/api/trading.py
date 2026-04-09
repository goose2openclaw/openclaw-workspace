#!/usr/bin/env python3
"""
🪿 GO2SE 交易API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.models.models import User, Trade, Position, Signal, RiskRule
from app.auth.auth import get_current_active_user
from app.services.trading import TradingService

router = APIRouter(prefix="/trade", tags=["交易"])
trading_service = TradingService()


class SignalExecuteRequest(BaseModel):
    signal_id: int


class TradeResponse(BaseModel):
    id: int
    order_id: str
    symbol: str
    side: str
    amount: float
    price: Optional[float]
    fee: float
    status: str
    pnl: float
    strategy: Optional[str]
    created_at: str


class PositionResponse(BaseModel):
    id: int
    symbol: str
    amount: float
    avg_price: float
    current_price: Optional[float]
    unrealized_pnl: float
    realized_pnl: float


class RiskRuleRequest(BaseModel):
    rule_code: str
    name: str
    condition: str
    action: str
    enabled: bool = True
    priority: int = 0


@router.get("/history", response_model=List[TradeResponse])
async def get_trade_history(
    limit: int = 50,
    symbol: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取交易历史"""
    query = db.query(Trade).filter(Trade.user_id == current_user.id)
    
    if symbol:
        query = query.filter(Trade.symbol == symbol)
    
    trades = query.order_by(Trade.created_at.desc()).limit(limit).all()
    
    return [
        TradeResponse(
            id=t.id,
            order_id=t.order_id,
            symbol=t.symbol,
            side=t.side,
            amount=t.amount,
            price=t.price,
            fee=t.fee,
            status=t.status,
            pnl=t.pnl,
            strategy=t.strategy,
            created_at=t.created_at.isoformat()
        )
        for t in trades
    ]


@router.get("/positions", response_model=List[PositionResponse])
async def get_positions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取当前持仓"""
    positions = db.query(Position).filter(Position.user_id == current_user.id).all()
    
    return [
        PositionResponse(
            id=p.id,
            symbol=p.symbol,
            amount=p.amount,
            avg_price=p.avg_price,
            current_price=p.current_price,
            unrealized_pnl=p.unrealized_pnl,
            realized_pnl=p.realized_pnl
        )
        for p in positions
    ]


@router.post("/execute")
async def execute_signal(
    request: SignalExecuteRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """执行信号"""
    # 获取信号
    signal = db.query(Signal).filter(Signal.id == request.signal_id).first()
    if not signal:
        raise HTTPException(status_code=404, detail="信号不存在")
    
    # 获取用户API Key
    # 这里简化处理，实际应该从用户配置中获取
    api_key = f"user_{current_user.id}_api_key"
    
    # 执行交易
    result = await trading_service.execute_signal(db, signal, current_user.id, api_key)
    
    return result


@router.post("/close-position/{position_id}")
async def close_position(
    position_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """平仓"""
    position = db.query(Position).filter(
        Position.id == position_id,
        Position.user_id == current_user.id
    ).first()
    
    if not position:
        raise HTTPException(status_code=404, detail="持仓不存在")
    
    result = await trading_service.close_position(db, position, current_user.id)
    return result


@router.get("/risk-rules")
async def get_risk_rules(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取风控规则"""
    rules = db.query(RiskRule).filter(RiskRule.user_id == current_user.id).all()
    return [
        {
            "id": r.id,
            "rule_code": r.rule_code,
            "name": r.name,
            "condition": r.condition,
            "action": r.action,
            "enabled": r.enabled,
            "priority": r.priority
        }
        for r in rules
    ]


@router.post("/risk-rules")
async def add_risk_rule(
    rule: RiskRuleRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """添加风控规则"""
    new_rule = RiskRule(
        user_id=current_user.id,
        rule_code=rule.rule_code,
        name=rule.name,
        condition=rule.condition,
        action=rule.action,
        enabled=rule.enabled,
        priority=rule.priority
    )
    db.add(new_rule)
    db.commit()
    db.refresh(new_rule)
    
    return {"id": new_rule.id, "message": "风控规则添加成功"}


@router.put("/risk-rules/{rule_id}")
async def update_risk_rule(
    rule_id: int,
    rule: RiskRuleRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新风控规则"""
    existing_rule = db.query(RiskRule).filter(
        RiskRule.id == rule_id,
        RiskRule.user_id == current_user.id
    ).first()
    
    if not existing_rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    
    existing_rule.name = rule.name
    existing_rule.condition = rule.condition
    existing_rule.action = rule.action
    existing_rule.enabled = rule.enabled
    existing_rule.priority = rule.priority
    
    db.commit()
    
    return {"message": "风控规则更新成功"}


@router.delete("/risk-rules/{rule_id}")
async def delete_risk_rule(
    rule_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """删除风控规则"""
    rule = db.query(RiskRule).filter(
        RiskRule.id == rule_id,
        RiskRule.user_id == current_user.id
    ).first()
    
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    
    db.delete(rule)
    db.commit()
    
    return {"message": "风控规则删除成功"}
