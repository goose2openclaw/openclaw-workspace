#!/bin/bash
# Brain Coordinator 启动脚本

COOR_DIR="$HOME/.openclaw/workspace/openclaw-workspace/GO2SE_PLATFORM/versions/brain_coordinator"
LOG_DIR="/tmp"
PORT=8010

echo "========================================"
echo "  Brain Coordinator 启动脚本"
echo "========================================"

# 检查端口是否占用
if fuser -s $PORT/tcp 2>/dev/null; then
    echo "⚠️  Port $PORT 已被占用，停止旧进程..."
    fuser -k $PORT/tcp 2>/dev/null
    sleep 2
fi

# 启动协调器
cd "$COOR_DIR"
echo "🚀 启动 Brain Coordinator (port $PORT)..."
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port $PORT > $LOG_DIR/coordinator.log 2>&1 &
COORD_PID=$!
echo "    PID: $COORD_PID"

# 等待启动
sleep 4

# 验证
HEALTH=$(curl -s --max-time 5 http://localhost:$PORT/health 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get("status","fail"))" 2>/dev/null)
if [ "$HEALTH" = "healthy" ]; then
    echo "✅  Brain Coordinator 已启动 (PID: $COORD_PID)"
    echo ""
    echo "  API 端点:"
    echo "    http://localhost:$PORT/status    - 状态"
    echo "    http://localhost:$PORT/brains    - 三脑信号"
    echo "    http://localhost:$PORT/analyze   - 决策分析"
    echo "    http://localhost:$PORT/history   - 历史记录"
    echo "    http://localhost:$PORT/docs      - API文档"
    echo ""
    echo "  日志: tail -f $LOG_DIR/coordinator.log"
else
    echo "❌  启动失败，请检查日志: $LOG_DIR/coordinator.log"
fi