#!/usr/bin/env python3
"""
🪿 GO2SE WebSocket 路由
"""

import json
import logging
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websocket import manager

logger = logging.getLogger("go2se")
router = APIRouter()

CHANNELS = ["market", "trade", "position", "alert"]

@router.websocket("")
async def websocket_endpoint(websocket: WebSocket, channel: str = "market"):
    """WebSocket 实时推送"""
    # 安全校验channel
    if channel not in CHANNELS:
        channel = "market"
    await manager.connect(websocket, channel)
    try:
        await websocket.send_json({
            "type": "connected",
            "msg": "🪿 GO2SE WebSocket已连接",
            "channel": channel,
            "ts": datetime.now().isoformat()
        })
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                action = msg.get("action")
                if action == "ping":
                    await websocket.send_json({"type": "pong", "ts": datetime.now().isoformat()})
                elif action == "subscribe":
                    topic = msg.get("topic", "market")
                    if topic in CHANNELS:
                        # 将连接迁移到新channel
                        manager.disconnect(websocket, channel)
                        channel = topic
                        await manager.connect(websocket, channel)
                    await websocket.send_json({"type": "subscribed", "topic": topic, "channel": channel})
                elif action == "broadcast":
                    # 允许客户端触发广播到同channel
                    await manager.broadcast({"type": "broadcast", "data": msg.get("data")}, channel)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "msg": "Invalid JSON"})
            except Exception as e:
                logger.error(f"❌ WS消息处理错误: {e}")
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel)
    except Exception as e:
        logger.error(f"❌ WebSocket错误: {e}")
        manager.disconnect(websocket, channel)
