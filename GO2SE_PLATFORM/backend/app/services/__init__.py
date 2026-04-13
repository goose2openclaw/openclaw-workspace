#!/usr/bin/env python3
"""
🪿 GO2SE Services 层
业务逻辑抽象 - 信号服务
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger("go2se")


class SignalService:
    """信号服务"""
    
    def __init__(self, db):
        self.db = db
    
    def create_signal(self, strategy: str, symbol: str, signal: str, 
                      confidence: float, price: float, reason: str = "") -> Dict:
        """创建信号"""
        from app.models.models import Signal
        
        db_signal = Signal(
            strategy=strategy,
            symbol=symbol,
            signal=signal,
            confidence=confidence,
            price=price,
            reason=reason,
            executed=False
        )
        self.db.add(db_signal)
        self.db.commit()
        self.db.refresh(db_signal)
        
        logger.info(f"📡 信号创建: {strategy} {symbol} {signal} ({confidence:.2f})")
        
        return {
            "id": db_signal.id,
            "strategy": db_signal.strategy,
            "symbol": db_signal.symbol,
            "signal": db_signal.signal,
            "confidence": db_signal.confidence
        }
    
    def get_signals(self, limit: int = 50, strategy: Optional[str] = None) -> List[Dict]:
        """获取信号列表"""
        from app.models.models import Signal
        
        query = self.db.query(Signal)
        if strategy:
            query = query.filter(Signal.strategy == strategy)
        
        signals = query.order_by(Signal.created_at.desc()).limit(limit).all()
        
        return [{
            "id": s.id,
            "strategy": s.strategy,
            "symbol": s.symbol,
            "signal": s.signal,
            "confidence": s.confidence,
            "reason": s.reason,
            "executed": s.executed,
            "created_at": s.created_at.isoformat()
        } for s in signals]
    
    def execute_signal(self, signal_id: int) -> Dict:
        """执行信号"""
        from app.models.models import Signal
        
        signal = self.db.query(Signal).filter(Signal.id == signal_id).first()
        if not signal:
            raise ValueError(f"信号不存在: {signal_id}")
        
        signal.executed = True
        self.db.commit()
        
        logger.info(f"✅ 信号已执行: {signal_id}")
        
        return {"status": "executed", "signal_id": signal_id}


class MarketService:
    """市场数据服务"""
    
    def __init__(self, engine):
        self.engine = engine
    
    async def get_market_overview(self, symbols: List[str]) -> List[Dict]:
        """获取市场概览"""
        results = []
        
        for symbol in symbols:
            try:
                tick = await self.engine.get_market_data(symbol)
                results.append({
                    "symbol": tick.symbol,
                    "price": tick.price,
                    "change_24h": tick.change_24h,
                    "volume_24h": tick.volume_24h,
                    "rsi": tick.rsi,
                    "bid": tick.bid,
                    "ask": tick.ask
                })
            except Exception as e:
                logger.error(f"❌ 获取市场数据失败: {symbol} - {e}")
        
        return results
    
    async def get_symbol_detail(self, symbol: str) -> Dict:
        """获取交易对详情"""
        try:
            tick = await self.engine.get_market_data(f"{symbol}/USDT")
            return {
                "symbol": tick.symbol,
                "price": tick.price,
                "change_24h": tick.change_24h,
                "volume_24h": tick.volume_24h,
                "high_24h": tick.high_24h,
                "low_24h": tick.low_24h,
                "rsi": tick.rsi,
                "bid": tick.bid,
                "ask": tick.ask
            }
        except Exception as e:
            logger.error(f"❌ 获取详情失败: {symbol} - {e}")
            raise


class TradeService:
    """交易服务"""
    
    def __init__(self, db, engine):
        self.db = db
        self.engine = engine
    
    async def execute_trade(self, signal: Dict) -> Dict:
        """执行交易"""
        result = await self.engine.execute_trade(signal)
        
        # 记录交易
        from app.models.models import Trade
        trade = Trade(
            symbol=signal.get("symbol"),
            side=signal.get("signal"),
            amount=signal.get("amount", 0),
            price=signal.get("price", 0),
            status="open",
            pnl=0,
            strategy=signal.get("strategy", "unknown")
        )
        self.db.add(trade)
        self.db.commit()
        
        logger.info(f"💰 交易执行: {signal.get('symbol')} {signal.get('signal')}")
        
        return result
    
    def get_trades(self, limit: int = 50, status: Optional[str] = None) -> List[Dict]:
        """获取交易记录"""
        from app.models.models import Trade
        
        query = self.db.query(Trade)
        if status:
            query = query.filter(Trade.status == status)
        
        trades = query.order_by(Trade.created_at.desc()).limit(limit).all()
        
        return [{
            "id": t.id,
            "symbol": t.symbol,
            "side": t.side,
            "amount": t.amount,
            "price": t.price,
            "status": t.status,
            "pnl": t.pnl,
            "strategy": t.strategy,
            "created_at": t.created_at.isoformat()
        } for t in trades]
    
    def get_positions(self) -> List[Dict]:
        """获取当前持仓"""
        from app.models.models import Position
        
        positions = self.db.query(Position).filter(Position.amount > 0).all()
        
        return [{
            "id": p.id,
            "symbol": p.symbol,
            "amount": p.amount,
            "avg_price": p.avg_price,
            "current_price": p.current_price,
            "unrealized_pnl": p.unrealized_pnl,
            "updated_at": p.updated_at.isoformat()
        } for p in positions]


class StatsService:
    """统计服务"""
    
    def __init__(self, db):
        self.db = db
    
    def get_overview(self) -> Dict:
        """获取统计概览"""
        from app.models.models import Trade, Signal
        from app.core.config import settings
        
        total_trades = self.db.query(Trade).count()
        open_trades = self.db.query(Trade).filter(Trade.status == "open").count()
        total_signals = self.db.query(Signal).count()
        executed_signals = self.db.query(Signal).filter(Signal.executed == True).count()
        
        # 计算胜率
        closed_trades = self.db.query(Trade).filter(Trade.status == "closed").all()
        wins = sum(1 for t in closed_trades if t.pnl > 0)
        win_rate = (wins / len(closed_trades) * 100) if closed_trades else 0
        
        # 计算总盈亏
        total_pnl = sum(t.pnl for t in closed_trades)
        
        return {
            "trading": {
                "total_trades": total_trades,
                "open_trades": open_trades,
                "closed_trades": len(closed_trades),
                "win_rate": round(win_rate, 2),
                "total_pnl": round(total_pnl, 2)
            },
            "signals": {
                "total": total_signals,
                "executed": executed_signals,
                "execution_rate": round(executed_signals / total_signals * 100, 2) if total_signals else 0
            },
            "config": {
                "mode": settings.TRADING_MODE,
                "max_position": settings.MAX_POSITION,
                "stop_loss": settings.STOP_LOSS,
                "take_profit": settings.TAKE_PROFIT
            }
        }
