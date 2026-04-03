#!/usr/bin/env python3
"""
🪿 WebSocket 连接管理器
"""
import asyncio
import json
import logging
from typing import Set
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger("go2se")


class ConnectionManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"🪿 WS连接建立 (总数: {len(self.active_connections)})")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"🔌 WS连接断开 (总数: {len(self.active_connections)})")

    async def broadcast(self, message: dict):
        """广播消息给所有连接的客户端"""
        if not self.active_connections:
            return
        dead = set()
        data = json.dumps(message, default=str)
        for conn in self.active_connections:
            try:
                await conn.send_text(data)
            except Exception:
                dead.add(conn)
        # 清理断开的连接
        self.active_connections -= dead


manager = ConnectionManager()
