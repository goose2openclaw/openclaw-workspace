#!/bin/bash
# GO2SE v15 启动脚本
PORT=8015
PID_FILE="/tmp/go2se_v15.pid"
LOG_FILE="/tmp/go2se_v15.log"

if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat $PID_FILE)
    if kill -0 $OLD_PID 2>/dev/null; then
        echo "v15已运行 PID=$OLD_PID"
        exit 0
    fi
fi

echo "启动 GO2SE v15 (端口 $PORT)..."
cd "$(dirname "$0")/backend"

nohup python3 -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port $PORT \
    --log-level info > $LOG_FILE 2>&1 &

NEW_PID=$!
echo $NEW_PID > $PID_FILE
echo "v15 PID=$NEW_PID"

sleep 3
if curl -s http://localhost:$PORT/health > /dev/null 2>&1; then
    echo "✅ v15 启动成功 http://localhost:$PORT"
    echo "📊 四脑状态: http://localhost:$PORT/api/brains"
    echo "🔮 MiroFish评分: http://localhost:$PORT/api/mirofish/score"
else
    echo "❌ v15 启动失败，查看日志: tail -f $LOG_FILE"
fi
