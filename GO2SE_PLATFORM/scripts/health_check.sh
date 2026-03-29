#!/bin/bash
# 🪿 GO2SE 健康检查 + 自动重启
# 用法: bash scripts/health_check.sh [PORT]

PORT=${1:-8004}
PID_FILE="/tmp/go2se_${PORT}.pid"
LOG_FILE="/tmp/go2se${PORT}.log"

# 检查进程是否存活
check_alive() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            return 0
        fi
    fi
    # 备用: 检查端口
    if curl -s --max-time 3 "http://localhost:${PORT}/api/ping" > /dev/null 2>&1; then
        return 0
    fi
    return 1
}

# 启动服务
start_server() {
    echo "[$(date)] 🚀 启动 GO2SE :${PORT}..." >> "$LOG_FILE"
    cd /root/.openclaw/workspace/GO2SE_PLATFORM/backend
    source ../venv/bin/activate >> "$LOG_FILE" 2>&1
    nohup uvicorn app.main:app --host 0.0.0.0 --port "$PORT" >> "$LOG_FILE" 2>&1 &
    NEW_PID=$!
    echo "$NEW_PID" > "$PID_FILE"
    echo "[$(date)] ✅ PID=$NEW_PID 已启动" >> "$LOG_FILE"
}

# 主逻辑
if check_alive; then
    echo "[$(date)] ✅ GO2SE :${PORT} 运行正常"
    exit 0
else
    echo "[$(date)] 🔴 GO2SE :${PORT} 无响应，尝试重启..." >> "$LOG_FILE"
    # 杀掉残留进程
    pkill -f "uvicorn.*:${PORT}" 2>/dev/null
    sleep 2
    # 清理僵尸
    pkill -9 -f "uvicorn.*:${PORT}" 2>/dev/null
    rm -f "$PID_FILE"
    start_server
    sleep 5
    if check_alive; then
        echo "[$(date)] ✅ 重启成功" >> "$LOG_FILE"
        echo "🔄 GO2SE :${PORT} 已重启"
    else
        echo "[$(date)] ❌ 重启失败" >> "$LOG_FILE"
        echo "❌ GO2SE :${PORT} 重启失败"
        exit 1
    fi
fi
