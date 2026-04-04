#!/bin/bash
# GO2SE Health Check Script
# 健康检查 + 自动恢复

set -e

WORKSPACE="/root/.openclaw/workspace/GO2SE_PLATFORM"
LOG_FILE="$WORKSPACE/logs/health_check.log"
PORT=8004
MAX_RESTART=3

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

check_port() {
    nc -z localhost $PORT 2>/dev/null
    return $?
}

check_api() {
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$PORT/api/stats 2>/dev/null || echo "000")
    [ "$response" = "200" ]
    return $?
}

check_disk() {
    usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    [ "$usage" -lt 95 ]
    return $?
}

restart_backend() {
    log "${YELLOW}尝试重启后端服务...${NC}"
    
    # 杀掉旧进程
    pkill -f "uvicorn app.main:app.*port $PORT" || true
    sleep 2
    
    # 重启
    cd $WORKSPACE/backend
    nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port $PORT > $WORKSPACE/logs/backend.log 2>&1 &
    sleep 3
    
    if check_port; then
        log "${GREEN}后端服务重启成功${NC}"
        return 0
    else
        log "${RED}后端服务重启失败${NC}"
        return 1
    fi
}

main() {
    log "========== 健康检查开始 =========="
    
    # 1. 检查端口
    log "检查端口 $PORT..."
    if ! check_port; then
        log "${RED}端口 $PORT 未监听${NC}"
        restart_backend
    else
        log "${GREEN}端口 $PORT 正常${NC}"
    fi
    
    # 2. 检查API
    log "检查API响应..."
    if ! check_api; then
        log "${RED}API响应异常${NC}"
        restart_backend
    else
        log "${GREEN}API响应正常${NC}"
    fi
    
    # 3. 检查磁盘
    log "检查磁盘空间..."
    if ! check_disk; then
        log "${RED}磁盘空间不足 (>95%)${NC}"
    else
        usage=$(df / | tail -1 | awk '{print $5}')
        log "${GREEN}磁盘空间: $usage${NC}"
    fi
    
    # 4. 获取状态
    if check_api; then
        stats=$(curl -s http://localhost:$PORT/api/stats 2>/dev/null)
        signals=$(echo $stats | grep -o '"total_signals":[0-9]*' | cut -d: -f2)
        trades=$(echo $stats | grep -o '"total_trades":[0-9]*' | cut -d: -f2)
        mode=$(echo $stats | grep -o '"trading_mode":"[^"]*"' | cut -d'"' -f4)
        
        log "信号数: $signals | 交易数: $trades | 模式: $mode"
    fi
    
    log "========== 健康检查完成 =========="
}

# 执行
main

# 退出码
exit 0
