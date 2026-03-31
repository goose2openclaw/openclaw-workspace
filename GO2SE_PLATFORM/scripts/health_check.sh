#!/bin/bash
# 🪿 GO2SE 健康检查 + 自动重启
# 用法: bash scripts/health_check.sh [PORT]

PORT=${1:-8004}
PID_FILE="/tmp/go2se_${PORT}.pid"
LOG_FILE="/tmp/go2se${PORT}.log"
ALERT_THRESHOLD=90  # 磁盘告警阈值

# 检查进程是否存活 + API响应有效性
check_alive() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            return 0
        fi
    fi
    # 备用: ping检查
    if curl -s --max-time 3 "http://localhost:${PORT}/api/ping" > /dev/null 2>&1; then
        return 0
    fi
    return 1
}

# 检查API stats响应完整性
check_stats_api() {
    STATS=$(curl -s --max-time 5 "http://localhost:${PORT}/api/stats" 2>/dev/null)
    if [ -z "$STATS" ]; then
        echo "⚠️  [WARN] /api/stats 返回空"
        return 1
    fi
    # 验证必要字段
    if echo "$STATS" | grep -q "\"trading_mode\"" && echo "$STATS" | grep -q "\"total_signals\""; then
        return 0
    else
        echo "⚠️  [WARN] /api/stats 响应字段不完整: $STATS"
        return 1
    fi
}

# 检查磁盘空间
check_disk() {
    USAGE=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
    if [ "$USAGE" -gt $ALERT_THRESHOLD ]; then
        echo "⚠️  [ALERT] 磁盘使用率 ${USAGE}% (超过${ALERT_THRESHOLD}%阈值!)"
        echo "[$(date)] ⚠️  磁盘告警: ${USAGE}% > ${ALERT_THRESHOLD}%" >> "$LOG_FILE"
        return 1
    fi
    return 0
}

# 检查内存
check_memory() {
    MEM_PCT=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100}')
    if [ "$MEM_PCT" -gt 90 ]; then
        echo "⚠️  [ALERT] 内存使用率 ${MEM_PCT}% (超过90%阈值!)"
        echo "[$(date)] ⚠️  内存告警: ${MEM_PCT}%" >> "$LOG_FILE"
        return 1
    fi
    return 0
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
echo "[$(date)] 🔍 健康检查..."

# 先检查资源告警
check_disk
DISK_STATUS=$?
check_memory
MEM_STATUS=$?

if check_alive; then
    echo "✅ GO2SE :${PORT} 进程正常"
    # 深度检查: 验证API响应
    if check_stats_api; then
        echo "✅ /api/stats 响应有效"
    else
        echo "⚠️  /api/stats 异常"
    fi
    if [ $DISK_STATUS -ne 0 ] || [ $MEM_STATUS -ne 0 ]; then
        echo "   ⚠️  但存在资源告警 (见上方)"
    fi
    exit 0
else
    echo "🔴 GO2SE :${PORT} 无响应，尝试重启..." >> "$LOG_FILE"
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
