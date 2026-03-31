#!/bin/bash
# Enhanced Health Check Script v2
# Improved stability monitoring

LOG_FILE="/root/.openclaw/workspace/GO2SE_PLATFORM/backend/app.log"
PORT=8004
MAX_MEM_PERCENT=90
MAX_CPU_PERCENT=80

check_backend() {
    curl -sf http://localhost:$PORT/api/stats >/dev/null 2>&1 && return 0 || return 1
}

check_memory() {
    MEM=$(free | awk '/Mem:/ {printf "%.0f", $3/$2 * 100}')
    [ "$MEM" -lt "$MAX_MEM_PERCENT" ] && return 0 || return 1
}

check_disk() {
    DISK=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    [ "$DISK" -lt 90 ] && return 0 || return 1
}

check_process() {
    pgrep -f "uvicorn" >/dev/null && return 0 || return 1
}

# Main
if ! check_backend; then
    echo "[$(date)] Backend DOWN, restarting..."
    cd /root/.openclaw/workspace/GO2SE_PLATFORM
    pkill -f uvicorn || true
    sleep 2
    ./scripts/start_server.sh
    exit 1
fi

if ! check_memory; then
    echo "[$(date)] ⚠️ Memory high, triggering GC..."
    python3 /root/.openclaw/workspace/GO2SE_PLATFORM/scripts/memory_optimizer.py 2>/dev/null
fi

if ! check_disk; then
    echo "[$(date)] 🚨 Disk critical!"
fi

echo "[$(date)] ✅ GO2SE Health OK"
