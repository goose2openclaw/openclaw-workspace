#!/bin/bash
# GO2SE 系统启动脚本 v1.0
# ================================
# 确保端口不冲突，系统平滑启动

set -e

BACKEND_PORT=8004
BACKEND_DIR="/root/.openclaw/workspace/GO2SE_PLATFORM/backend"
LOG_DIR="/tmp/go2se"
PID_FILE="/tmp/go2se_backend.pid"

echo "=============================================="
echo "🪿 GO2SE 系统启动"
echo "=============================================="

# 创建日志目录
mkdir -p $LOG_DIR

# 检查端口是否被占用
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo "⚠️  端口 $port 已被占用"
        return 1
    else
        echo "✅ 端口 $port 可用"
        return 0
    fi
}

# 停止旧进程
stop_old() {
    if [ -f $PID_FILE ]; then
        local pid=$(cat $PID_FILE)
        if kill -0 $pid 2>/dev/null; then
            echo "🛑 停止旧进程 $pid..."
            kill $pid 2>/dev/null || true
            sleep 2
        fi
    fi
    
    # 也杀掉残留
    pkill -f "uvicorn.*$BACKEND_PORT" 2>/dev/null || true
    sleep 1
}

# 启动后端
start_backend() {
    echo "🚀 启动后端端口 $BACKEND_PORT..."
    
    cd $BACKEND_DIR
    
    # 后台运行
    nohup python3 -m uvicorn app.main:app \
        --host 0.0.0.0 \
        --port $BACKEND_PORT \
        --workers 2 \
        > $LOG_DIR/backend_$BACKEND_PORT.log 2>&1 &
    
    local pid=$!
    echo $pid > $PID_FILE
    echo "✅ 后端启动成功 (PID: $pid)"
    
    # 等待启动
    sleep 3
    
    # 检查健康
    local health=$(curl -s http://localhost:$BACKEND_PORT/api/stats 2>/dev/null || echo "")
    if echo "$health" | grep -q "version"; then
        echo "✅ 后端健康检查通过"
    else
        echo "❌ 后端健康检查失败"
        cat $LOG_DIR/backend_$BACKEND_PORT.log | tail -10
    fi
}

# 主流程
main() {
    echo ""
    echo "1️⃣ 检查端口..."
    if ! check_port $BACKEND_PORT; then
        echo "🔧 清理端口..."
        stop_old
        sleep 2
        check_port $BACKEND_PORT || exit 1
    fi
    
    echo ""
    echo "2️⃣ 启动服务..."
    start_backend
    
    echo ""
    echo "=============================================="
    echo "✅ GO2SE 系统启动完成！"
    echo "=============================================="
    echo "后端: http://localhost:$BACKEND_PORT"
    echo "API:  http://localhost:$BACKEND_PORT/api/stats"
    echo "日志: $LOG_DIR/backend_$BACKEND_PORT.log"
    echo "=============================================="
}

main "$@"
