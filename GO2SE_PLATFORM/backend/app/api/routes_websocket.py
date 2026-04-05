"""
WebSocket 实时推送端点
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import asyncio
import json

router = APIRouter()

# 连接管理器
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket实时推送端点"""
    await manager.connect(websocket)
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 处理订阅请求
            if message.get("action") == "subscribe":
                channel = message.get("channel")
                await websocket.send_json({
                    "type": "subscribed",
                    "channel": channel
                })
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@router.get("/ws/status")
async def websocket_status():
    """WebSocket连接状态"""
    return {
        "status": "ok",
        "active_connections": len(manager.active_connections)
    }
