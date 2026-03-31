#!/bin/bash
# Enhanced Health Check Script v2
# Improved stability monitoring

LOG_FILE="/root/.openclaw/workspace/GO2SE_PLATFORM/backend/app.log"
PORT=8000
MAX_MEM_PERCENT=90
MAX_CPU_PERCENT=80

check_backend() {{
    curl -sf http://localhost:$PORT/api/stats >/dev/null 2>&1 && return 0 || return 1
}}

check_memory() {{
    MEM=$(free | awk '/Mem:/ {printf "%.0f", $3/$2 * 100}')
    [ "$MEM" -lt "$MAX_MEM_PERCENT" ] && return 0 || return 1
}}

check_disk() {{
    DISK=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    [ "$DISK" -lt 90 ] && return 0 || return 1
}}

check_process() {{
    pgrep -f "uvicorn" >/dev/null && return 0 || return 1
}}

# Main
if ! check_backend; then
    echo "[$(date)] Backend DOWN, restarting..."
    cd /root/.openclaw/workspace/GO2SE_PLATFORM
    pkill -f uvicorn || true
    sleep 2
    ./start.sh &
    exit 1
fi

if ! check_memory; then
    echo "[$(date)] High memory usage, triggering GC..."
    python3 -c "import gc; gc.collect()"
fi

if ! check_process; then
    echo "[$(date)] Process died, restarting..."
    cd /root/.openclaw/workspace/GO2SE_PLATFORM
    ./start.sh &
fi

echo "[$(date)] Health OK"
