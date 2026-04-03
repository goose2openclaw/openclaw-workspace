#!/usr/bin/env python3
"""
🪿 GO2SE 交易执行模块
支持多交易所、多策略
"""

import asyncio
import logging
from typing import Optional, List, Dict
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Trade, Position, Signal, RiskRule, RiskLog
from app.services.exchange import ExchangeService

logger = logging.getLogger(__name__)


class TradingService:
    """交易执行服务"""
    
    def __init__(self):
        self.exchange = ExchangeService()
    
    async def execute_signal(
        self,
        db: Session,
        signal: Signal,
        user_id: int,
        api_key: str
    ) -> Dict:
        """执行信号"""
        # 检查风控
        risk_check = await self.check_risk(db, user_id, signal)
        if not risk_check["passed"]:
            # 记录风控日志
            log = RiskLog(
                user_id=user_id,
                rule_code=risk_check.get("rule_code"),
                triggered=True,
                action_taken=risk_check.get("action"),
                details={"signal_id": signal.id, "reason": risk_check["reason"]}
            )
            db.add(log)
            db.commit()
            return {"success": False, "reason": risk_check["reason"]}
        
        try:
            # 获取当前价格
            price = await self.exchange.get_price(signal.symbol)
            
            # 计算订单参数
            amount = self.calculate_position_size(signal)
            
            # 执行交易
            if signal.signal == "buy":
                result = await self.exchange.place_order(
                    api_key=api_key,
                    symbol=signal.symbol,
                    side="buy",
                    amount=amount,
                    price=price
                )
            elif signal.signal == "sell":
                result = await self.exchange.place_order(
                    api_key=api_key,
                    symbol=signal.symbol,
                    side="sell",
                    amount=amount,
                    price=price
                )
            else:
                return {"success": False, "reason": "无效信号"}
            
            # 创建交易记录
            trade = Trade(
                user_id=user_id,
                order_id=result.get("order_id"),
                symbol=signal.symbol,
                side=signal.signal,
                amount=amount,
                price=price,
                fee=result.get("fee", 0),
                strategy=signal.strategy,
                status="open"
            )
            db.add(trade)
            
            # 更新信号状态
            signal.executed = True
            db.commit()
            
            return {"success": True, "trade_id": trade.id, "order_id": result.get("order_id")}
            
        except Exception as e:
            logger.error(f"交易执行失败: {e}")
            return {"success": False, "reason": str(e)}
    
    async def check_risk(self, db: Session, user_id: int, signal: Signal) -> Dict:
        """风控检查"""
        rules = db.query(RiskRule).filter(
            RiskRule.user_id == user_id,
            RiskRule.enabled == True
        ).order_by(RiskRule.priority).all()
        
        for rule in rules:
            if rule.rule_code == "R001":  # 仓位限制
                positions = db.query(Position).filter(Position.user_id == user_id).all()
                total_exposure = sum(p.amount * p.current_price for p in positions)
                # 假设总资产100万
                if total_exposure > 800000:
                    return {"passed": False, "rule_code": "R001", "action": rule.action, "reason": "仓位超过80%"}
            
            elif rule.rule_code == "R002":  # 日内熔断
                today_trades = db.query(Trade).filter(
                    Trade.user_id == user_id,
                    Trade.created_at >= datetime.utcnow().replace(hour=0, minute=0)
                ).all()
                daily_pnl = sum(t.pnl for t in today_trades)
                if daily_pnl < -30000:
                    return {"passed": False, "rule_code": "R002", "action": rule.action, "reason": "日内亏损超过30%"}
            
            elif rule.rule_code == "R003":  # 单笔风险
                if signal.confidence < 5:
                    return {"passed": False, "rule_code": "R003", "action": rule.action, "reason": "置信度过低"}
            
            elif rule.rule_code == "R004":  # 波动止损
                pass  # 需要实时价格监控
        
        return {"passed": True}
    
    def calculate_position_size(self, signal: Signal) -> float:
        """计算仓位大小"""
        # 基于置信度计算仓位
        confidence = signal.confidence
        
        if confidence >= 8:
            return 0.20  # 20%仓位
        elif confidence >= 7:
            return 0.15  # 15%仓位
        elif confidence >= 6:
            return 0.10  # 10%仓位
        elif confidence >= 5:
            return 0.05  # 5%仓位
        else:
            return 0.02  # 2%仓位
    
    async def close_position(
        self,
        db: Session,
        position: Position,
        user_id: int,
        reason: str = "manual"
    ) -> Dict:
        """平仓"""
        try:
            current_price = await self.exchange.get_price(position.symbol)
            
            # 计算盈亏
            pnl = (current_price - position.avg_price) * position.amount
            
            # 执行平仓订单
            result = await self.exchange.place_order(
                symbol=position.symbol,
                side="sell",
                amount=position.amount,
                price=current_price
            )
            
            # 更新持仓
            position.status = "closed"
            position.realized_pnl += pnl
            db.commit()
            
            return {"success": True, "pnl": pnl}
            
        except Exception as e:
            logger.error(f"平仓失败: {e}")
            return {"success": False, "reason": str(e)}
    
    async def sync_positions(self, db: Session, user_id: int, api_key: str) -> List[Position]:
        """同步持仓"""
        try:
            exchange_positions = await self.exchange.get_positions(api_key)
            
            for ep in exchange_positions:
                position = db.query(Position).filter(
                    Position.user_id == user_id,
                    Position.symbol == ep["symbol"]
                ).first()
                
                if position:
                    position.amount = ep["amount"]
                    position.current_price = ep["price"]
                    position.unrealized_pnl = (ep["price"] - position.avg_price) * ep["amount"]
                else:
                    position = Position(
                        user_id=user_id,
                        symbol=ep["symbol"],
                        amount=ep["amount"],
                        avg_price=ep["avg_price"],
                        current_price=ep["price"]
                    )
                    db.add(position)
            
            db.commit()
            return db.query(Position).filter(Position.user_id == user_id).all()
            
        except Exception as e:
            logger.error(f"同步持仓失败: {e}")
            return []
