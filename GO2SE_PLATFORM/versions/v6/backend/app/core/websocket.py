#!/usr/bin/env python3
"""
🪿 GO2SE WebSocket 实时推送
"""

import json
import logging
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger("go2se")


class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # 活跃连接
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "market": set(),      # 行情数据
            "trade": set(),       # 交易信号
            "position": set(),    # 持仓更新
            "alert": set(),      # 告警通知
        }
    
    async def connect(self, websocket: WebSocket, channel: str = "market"):
        """连接"""
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = set()
        self.active_connections[channel].add(websocket)
        logger.info(f"🔌 WS连接: {channel} (总数: {len(self.active_connections[channel])})")
    
    def disconnect(self, websocket: WebSocket, channel: str = "market"):
        """断开连接"""
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)
            logger.info(f"🔌 WS断开: {channel} (剩余: {len(self.active_connections[channel])})")
    
    async def send_personal(self, message: dict, websocket: WebSocket):
        """发送个人消息"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"❌ 发送失败: {e}")
    
    async def broadcast(self, message: dict, channel: str = "market"):
        """广播消息"""
        if channel not in self.active_connections:
            return
        
        disconnected = set()
        for connection in self.active_connections[channel]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"❌ 广播失败: {e}")
                disconnected.add(connection)
        
        # 清理断开的连接
        for conn in disconnected:
            self.active_connections[channel].discard(conn)
    
    async def broadcast_market(self, data: dict):
        """广播行情数据"""
        await self.broadcast({
            "type": "market",
            "data": data,
            "timestamp": data.get("timestamp")
        }, "market")
    
    async def broadcast_signal(self, data: dict):
        """广播交易信号"""
        await self.broadcast({
            "type": "signal",
            "data": data
        }, "trade")
    
    async def broadcast_position(self, data: dict):
        """广播持仓更新"""
        await self.broadcast({
            "type": "position",
            "data": data
        }, "position")
    
    async def broadcast_alert(self, message: str, level: str = "info"):
        """广播告警"""
        await self.broadcast({
            "type": "alert",
            "message": message,
            "level": level
        }, "alert")


# 全局实例
manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, channel: str = "market"):
    """WebSocket端点"""
    await manager.connect(websocket, channel)
    try:
        while True:
            # 保持连接，可接收客户端消息
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 处理客户端消息
            if message.get("type") == "ping":
                await manager.send_personal({"type": "pong"}, websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)
        logger.info(f"🔌 客户端断开")
    except Exception as e:
        logger.error(f"❌ WebSocket错误: {e}")
        manager.disconnect(websocket, channel)
