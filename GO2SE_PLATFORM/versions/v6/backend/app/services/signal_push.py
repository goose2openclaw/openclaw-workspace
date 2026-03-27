#!/usr/bin/env python3
"""
🪿 GO2SE 信号推送模块
支持多渠道推送
"""

import asyncio
import logging
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Signal, User, Notification
import aiohttp

logger = logging.getLogger(__name__)


class SignalPushService:
    """信号推送服务"""
    
    def __init__(self):
        self.push_channels = {
            "telegram": self.push_to_telegram,
            "webhook": self.push_to_webhook,
            "email": self.push_to_email,
            "sms": self.push_to_sms,
        }
    
    async def push_signal(
        self,
        db: Session,
        signal: Signal,
        user_id: int,
        channels: List[str] = ["telegram"]
    ) -> Dict:
        """推送信号到各渠道"""
        results = {}
        
        # 获取用户信息
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"success": False, "reason": "用户不存在"}
        
        # 构建消息
        message = self.build_signal_message(signal)
        
        for channel in channels:
            if channel in self.push_channels:
                try:
                    result = await self.push_channels[channel](user, message)
                    results[channel] = result
                except Exception as e:
                    logger.error(f"推送失败 [{channel}]: {e}")
                    results[channel] = {"success": False, "error": str(e)}
        
        # 记录通知
        notification = Notification(
            user_id=user_id,
            type="signal",
            title=f"{signal.strategy} 信号",
            content=message["text"]
        )
        db.add(notification)
        db.commit()
        
        return results
    
    def build_signal_message(self, signal: Signal) -> Dict:
        """构建信号消息"""
        emoji = "🟢" if signal.signal == "buy" else "🔴" if signal.signal == "sell" else "⚪"
        
        text = f"""
{emoji} **{signal.strategy} 信号**

币种: {signal.symbol}
信号: {signal.signal.upper()}
置信度: {signal.signal}/10
价格: ${signal.price if signal.price else 'N/A'}
原因: {signal.reason or 'AI智能分析'}

时间: {signal.created_at.strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()
        
        return {
            "text": text,
            "html": self.build_html_message(signal),
            "emoji": emoji
        }
    
    def build_html_message(self, signal: Signal) -> str:
        """构建HTML消息"""
        emoji = "🟢" if signal.signal == "buy" else "🔴" if signal.signal == "sell" else "⚪"
        
        return f"""
<div style="font-family: Arial, sans-serif; padding: 16px;">
    <h3 style="margin: 0 0 12px;">{emoji} {signal.strategy} 信号</h3>
    <table style="width: 100%; border-collapse: collapse;">
        <tr><td><b>币种:</b></td><td>{signal.symbol}</td></tr>
        <tr><td><b>信号:</b></td><td>{signal.signal.upper()}</td></tr>
        <tr><td><b>置信度:</b></td><td>{signal.signal}/10</td></tr>
        <tr><td><b>价格:</b></td><td>${signal.price if signal.price else 'N/A'}</td></tr>
        <tr><td><b>原因:</b></td><td>{signal.reason or 'AI智能分析'}</td></tr>
    </table>
    <p style="color: #666; font-size: 12px; margin-top: 12px;">
        时间: {signal.created_at.strftime('%Y-%m-%d %H:%M:%S')}
    </p>
</div>
        """.strip()
    
    async def push_to_telegram(self, user: User, message: Dict) -> Dict:
        """推送到Telegram"""
        # 需要用户绑定Telegram Chat ID
        # 这里使用模拟实现
        telegram_webhook = getattr(user, 'telegram_webhook', None)
        
        if not telegram_webhook:
            return {"success": False, "reason": "未绑定Telegram"}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"https://api.telegram.org/bot{getattr(user, 'telegram_token', '')}/sendMessage",
                json={
                    "chat_id": user.telegram_chat_id,
                    "text": message["text"],
                    "parse_mode": "Markdown"
                }
            ) as resp:
                result = await resp.json()
                return {"success": result.get("ok", False)}
    
    async def push_to_webhook(self, user: User, message: Dict) -> Dict:
        """推送到WebHook"""
        webhook_url = getattr(user, 'webhook_url', None)
        
        if not webhook_url:
            return {"success": False, "reason": "未配置WebHook"}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=message) as resp:
                return {"success": resp.status == 200}
    
    async def push_to_email(self, user: User, message: Dict) -> Dict:
        """推送邮件"""
        # 需要配置SMTP
        # 这里使用模拟实现
        logger.info(f"发送邮件到 {user.email}: {message['text'][:50]}...")
        return {"success": True, "method": "email"}
    
    async def push_to_sms(self, user: User, message: Dict) -> Dict:
        """推送短信"""
        # 需要配置短信网关
        phone = getattr(user, 'phone', None)
        
        if not phone:
            return {"success": False, "reason": "未绑定手机号"}
        
        logger.info(f"发送短信到 {phone}: {message['text'][:50]}...")
        return {"success": True, "method": "sms"}
    
    async def batch_push(
        self,
        db: Session,
        signals: List[Signal]
    ) -> Dict:
        """批量推送信号"""
        results = {"total": len(signals), "success": 0, "failed": 0}
        
        for signal in signals:
            # 获取订阅该策略的用户
            users = db.query(User).filter(User.vip_level.in_(["vip", "partner", "expert"])).all()
            
            for user in users:
                result = await self.push_signal(db, signal, user.id)
                if result.get("telegram", {}).get("success"):
                    results["success"] += 1
                else:
                    results["failed"] += 1
        
        return results
    
    async def get_user_notifications(
        self,
        db: Session,
        user_id: int,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Notification]:
        """获取用户通知"""
        query = db.query(Notification).filter(Notification.user_id == user_id)
        
        if unread_only:
            query = query.filter(Notification.read == False)
        
        return query.order_by(Notification.created_at.desc()).limit(limit).all()
    
    async def mark_notification_read(
        self,
        db: Session,
        notification_id: int,
        user_id: int
    ) -> bool:
        """标记通知已读"""
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if notification:
            notification.read = True
            db.commit()
            return True
        
        return False
