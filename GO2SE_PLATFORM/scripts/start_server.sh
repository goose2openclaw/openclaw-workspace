#!/bin/bash
# 🪿 GO2SE 服务管理器 - 统一入口
# 用法: bash scripts/start_server.sh [start|stop|restart|status] [PORT]

set -e

ACTION=${1:-start}
PORT=${2:-8004}
BASE_DIR="/root/.openclaw/workspace/GO2SE_PLATFORM/backend"
VENV_DIR="$BASE_DIR/../venv"
PID_FILE="/tmp/go2se_${PORT}.pid"
LOG_FILE="/tmp/go2se${PORT}.log"

source "$VENV_DIR/bin/activate" 2>/dev/null || true

start_server() {
    echo "🪿 启动 GO2SE :${PORT}..."
    
    # 清理旧实例
    echo "  🔄 清理旧实例..."
    if [ -f "$PID_FILE" ]; then
        OLD_PID=$(cat "$PID_FILE")
        kill "$OLD_PID" 2>/dev/null || true
    fi
    pkill -f "uvicorn.*:${PORT}" 2>/dev/null || true
    sleep 1
    # 强制清理僵尸
    pkill -9 -f "uvicorn.*:${PORT}" 2>/dev/null || true
    
    # 启动新实例
    cd "$BASE_DIR"
    nohup uvicorn app.main:app --host 0.0.0.0 --port "$PORT" > "$LOG_FILE" 2>&1 &
    NEW_PID=$!
    echo "$NEW_PID" > "$PID_FILE"
    
    sleep 5
    
    # 验证启动
    if curl -s --max-time 5 "http://localhost:${PORT}/api/ping" > /dev/null 2>&1; then
        echo "  ✅ GO2SE :${PORT} 启动成功 (PID=$NEW_PID)"
    else
        echo "  ❌ GO2SE :${PORT} 启动失败，查看日志:"
        tail -10 "$LOG_FILE"
        exit 1
    fi
}

stop_server() {
    echo "🛑 停止 GO2SE :${PORT}..."
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        kill "$PID" 2>/dev/null || true
        rm -f "$PID_FILE"
    fi
    pkill -f "uvicorn.*:${PORT}" 2>/dev/null || true
    echo "  ✅ 已停止"
}

status_server() {
    echo "📊 GO2SE :${PORT} 状态:"
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo "  🟢 运行中 (PID=$PID)"
        else
            echo "  🔴 已停止 (PID文件残留)"
        fi
    else
        echo "  🔴 未运行"
    fi
    if curl -s --max-time 3 "http://localhost:${PORT}/api/ping" > /dev/null 2>&1; then
        echo "  🟢 HTTP正常响应"
    else
        echo "  🔴 HTTP无响应"
    fi
}

case "$ACTION" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        stop_server
        sleep 2
        start_server
        ;;
    status)
        status_server
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status} [PORT]"
        exit 1
        ;;
esac
