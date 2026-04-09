"""
预警系统 - Telegram/Discord 通知
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

class AlertType(Enum):
    """预警类型"""
    SIGNAL = "signal"              # 信号
    TRADE_EXECUTION = "trade"      # 交易执行
    STOP_LOSS = "stop_loss"        # 止损
    TAKE_PROFIT = "take_profit"    # 止盈
    RISK_WARNING = "risk"          # 风险警告
    SYSTEM_ERROR = "error"          # 系统错误
    POSITION_UPDATE = "position"   # 持仓更新
    DAILY_REPORT = "daily_report" # 日报

class AlertLevel(Enum):
    """预警级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class Alert:
    """预警消息"""
    type: AlertType
    level: AlertLevel
    title: str
    message: str
    data: Dict = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.data is None:
            self.data = {}
            
    def to_dict(self) -> Dict:
        return {
            "type": self.type.value,
            "level": self.level.value,
            "title": self.title,
            "message": self.message,
            "data": self.data,
            "timestamp": self.timestamp.isoformat()
        }


class TelegramNotifier:
    """Telegram 通知器"""
    
    def __init__(self, bot_token: str = "", chat_id: str = ""):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
        self.enabled = bool(bot_token and chat_id)
        
    async def send(self, alert: Alert) -> bool:
        """发送消息"""
        if not self.enabled:
            logger.warning("Telegram notifier not configured")
            return False
            
        try:
            # 构建消息
            emoji = self._get_level_emoji(alert.level)
            text = f"{emoji} *{alert.title}*\n\n"
            text += f"_{alert.message}_\n\n"
            
            # 添加数据字段
            if alert.data:
                text += "📊 *数据:*\n"
                for key, value in alert.data.items():
                    text += f"• {key}: `{value}`\n"
                    
            text += f"\n⏰ {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')} UTC"
            
            # 发送请求
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_url}/sendMessage"
                payload = {
                    "chat_id": self.chat_id,
                    "text": text,
                    "parse_mode": "Markdown",
                    "disable_web_page_preview": True
                }
                
                async with session.post(url, json=payload, timeout=10) as resp:
                    if resp.status == 200:
                        logger.info(f"Telegram alert sent: {alert.title}")
                        return True
                    else:
                        logger.error(f"Telegram API error: {resp.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Telegram send error: {e}")
            return False
            
    def _get_level_emoji(self, level: AlertLevel) -> str:
        """获取级别Emoji"""
        mapping = {
            AlertLevel.INFO: "ℹ️",
            AlertLevel.WARNING: "⚠️",
            AlertLevel.ERROR: "❌",
            AlertLevel.CRITICAL: "🔴"
        }
        return mapping.get(level, "ℹ️")


class DiscordNotifier:
    """Discord 通知器"""
    
    def __init__(self, webhook_url: str = ""):
        self.webhook_url = webhook_url
        self.enabled = bool(webhook_url)
        
    async def send(self, alert: Alert) -> bool:
        """发送消息"""
        if not self.enabled:
            logger.warning("Discord notifier not configured")
            return False
            
        try:
            # 构建嵌入消息
            color = self._get_level_color(alert.level)
            description = alert.message
            
            # 添加数据字段
            fields = []
            if alert.data:
                for key, value in alert.data.items():
                    fields.append({
                        "name": key,
                        "value": str(value),
                        "inline": True
                    })
                    
            # 构建请求
            async with aiohttp.ClientSession() as session:
                url = self.webhook_url
                payload = {
                    "embeds": [{
                        "title": alert.title,
                        "description": description,
                        "color": color,
                        "timestamp": alert.timestamp.isoformat(),
                        "footer": {
                            "text": f"GO2SE Alert - {alert.type.value}"
                        },
                        "fields": fields
                    }]
                }
                
                async with session.post(url, json=payload, timeout=10) as resp:
                    if resp.status in [200, 204]:
                        logger.info(f"Discord alert sent: {alert.title}")
                        return True
                    else:
                        logger.error(f"Discord API error: {resp.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Discord send error: {e}")
            return False
            
    def _get_level_color(self, level: AlertLevel) -> int:
        """获取级别颜色"""
        mapping = {
            AlertLevel.INFO: 3447003,      # 蓝色
            AlertLevel.WARNING: 16776960,  # 黄色
            AlertLevel.ERROR: 15158332,    # 红色
            AlertLevel.CRITICAL: 10038562  # 深红
        }
        return mapping.get(level, 3447003)


class AlertManager:
    """预警管理器"""
    
    def __init__(self):
        self.telegram: Optional[TelegramNotifier] = None
        self.discord: Optional[DiscordNotifier] = None
        self.alert_history: List[Alert] = []
        self.max_history = 100
        
    def configure_telegram(self, bot_token: str, chat_id: str):
        """配置 Telegram"""
        self.telegram = TelegramNotifier(bot_token, chat_id)
        logger.info(f"Telegram notifier configured: chat_id={chat_id}")
        
    def configure_discord(self, webhook_url: str):
        """配置 Discord"""
        self.discord = DiscordNotifier(webhook_url)
        logger.info("Discord notifier configured")
        
    async def send_alert(self, alert: Alert) -> Dict[str, bool]:
        """发送预警到所有渠道"""
        results = {"telegram": False, "discord": False}
        
        # 记录历史
        self.alert_history.append(alert)
        if len(self.alert_history) > self.max_history:
            self.alert_history.pop(0)
            
        # 发送到 Telegram
        if self.telegram and self.telegram.enabled:
            results["telegram"] = await self.telegram.send(alert)
            
        # 发送到 Discord
        if self.discord and self.discord.enabled:
            results["discord"] = await self.discord.send(alert)
            
        return results
        
    # ===== 便捷方法 =====
    
    async def notify_signal(self, signal_type: str, symbol: str, price: float, confidence: float, reason: str):
        """通知信号"""
        level = AlertLevel.INFO if confidence < 7 else AlertLevel.WARNING
        
        alert = Alert(
            type=AlertType.SIGNAL,
            level=level,
            title=f"交易信号: {signal_type}",
            message=f"{symbol} @ ${price:,.2f}\n置信度: {confidence}/10\n原因: {reason}",
            data={
                "symbol": symbol,
                "price": f"${price:,.2f}",
                "confidence": f"{confidence}/10",
                "reason": reason
            }
        )
        return await self.send_alert(alert)
        
    async def notify_trade(self, side: str, symbol: str, price: float, quantity: float, pnl: float = 0):
        """通知交易"""
        emoji = "🟢" if side == "BUY" else "🔴"
        level = AlertLevel.INFO if pnl >= 0 else AlertLevel.WARNING
        
        alert = Alert(
            type=AlertType.TRADE_EXECUTION,
            level=level,
            title=f"{emoji} 交易执行: {side}",
            message=f"{side} {quantity} {symbol} @ ${price:,.2f}\n盈亏: ${pnl:,.2f}",
            data={
                "side": side,
                "symbol": symbol,
                "price": f"${price:,.2f}",
                "quantity": quantity,
                "pnl": f"${pnl:,.2f}"
            }
        )
        return await self.send_alert(alert)
        
    async def notify_stop_loss(self, symbol: str, entry_price: float, current_price: float, loss_percent: float):
        """通知止损"""
        alert = Alert(
            type=AlertType.STOP_LOSS,
            level=AlertLevel.ERROR,
            title=f"🛑 止损触发: {symbol}",
            message=f"止损平仓!\n入场: ${entry_price:,.2f}\n当前: ${current_price:,.2f}\n亏损: {loss_percent:.2f}%",
            data={
                "symbol": symbol,
                "entry_price": f"${entry_price:,.2f}",
                "current_price": f"${current_price:,.2f}",
                "loss_percent": f"{loss_percent:.2f}%"
            }
        )
        return await self.send_alert(alert)
        
    async def notify_take_profit(self, symbol: str, entry_price: float, current_price: float, profit_percent: float):
        """通知止盈"""
        alert = Alert(
            type=AlertType.TAKE_PROFIT,
            level=AlertLevel.INFO,
            title=f"💰 止盈触发: {symbol}",
            message=f"止盈平仓!\n入场: ${entry_price:,.2f}\n当前: ${current_price:,.2f}\n盈利: {profit_percent:.2f}%",
            data={
                "symbol": symbol,
                "entry_price": f"${entry_price:,.2f}",
                "current_price": f"${current_price:,.2f}",
                "profit_percent": f"{profit_percent:.2f}%"
            }
        )
        return await self.send_alert(alert)
        
    async def notify_risk_warning(self, rule: str, message: str, action: str = ""):
        """通知风险警告"""
        alert = Alert(
            type=AlertType.RISK_WARNING,
            level=AlertLevel.WARNING,
            title=f"⚠️ 风控警告: {rule}",
            message=f"{message}\n建议: {action}" if action else message,
            data={
                "rule": rule,
                "message": message,
                "action": action or "无"
            }
        )
        return await self.send_alert(alert)
        
    async def notify_error(self, source: str, error: str):
        """通知系统错误"""
        alert = Alert(
            type=AlertType.SYSTEM_ERROR,
            level=AlertLevel.ERROR,
            title=f"❌ 系统错误: {source}",
            message=f"错误详情: {error}",
            data={
                "source": source,
                "error": error
            }
        )
        return await self.send_alert(alert)
        
    async def notify_daily_report(self, stats: Dict):
        """通知日报"""
        pnl_emoji = "🟢" if stats.get("pnl", 0) >= 0 else "🔴"
        
        alert = Alert(
            type=AlertType.DAILY_REPORT,
            level=AlertLevel.INFO,
            title="📊 每日报告",
            message=f"{pnl_emoji} 今日盈亏: ${stats.get('pnl', 0):,.2f}\n"
                   f"交易次数: {stats.get('trades', 0)}\n"
                   f"胜率: {stats.get('win_rate', 0):.1f}%",
            data={
                "pnl": f"${stats.get('pnl', 0):,.2f}",
                "trades": stats.get('trades', 0),
                "win_rate": f"{stats.get('win_rate', 0):.1f}%",
                "best_trade": f"${stats.get('best_trade', 0):,.2f}",
                "worst_trade": f"${stats.get('worst_trade', 0):,.2f}"
            }
        )
        return await self.send_alert(alert)
        
    def get_history(self, limit: int = 10, alert_type: AlertType = None) -> List[Alert]:
        """获取历史预警"""
        history = self.alert_history[-limit:]
        if alert_type:
            history = [a for a in history if a.type == alert_type]
        return history
        
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            "telegram_enabled": self.telegram.enabled if self.telegram else False,
            "discord_enabled": self.discord.enabled if self.discord else False,
            "history_count": len(self.alert_history)
        }


# 全局预警管理器实例
alert_manager = AlertManager()
