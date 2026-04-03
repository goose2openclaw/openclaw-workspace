#!/bin/bash
# GO2SE 健康检查脚本 v1.0
# ==========================
# 每5分钟运行，确保系统不崩溃

BACKEND_URL="http://localhost:8004"
LOG_FILE="/tmp/go2se_health.log"

check_backend() {
    local response=$(curl -s --max-time 5 "$BACKEND_URL/api/stats" 2>/dev/null || echo "FAILED")
    
    if echo "$response" | grep -q "version"; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Backend healthy" >> $LOG_FILE
        return 0
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ Backend unhealthy, restarting..." >> $LOG_FILE
        return 1
    fi
}

restart_backend() {
    cd /root/.openclaw/workspace/GO2SE_PLATFORM/backend
    pkill -f "uvicorn.*8004" 2>/dev/null || true
    sleep 2
    nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8004 > /tmp/go2se_8004.log 2>&1 &
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🔄 Backend restarted" >> $LOG_FILE
}

# 运行检查
if ! check_backend; then
    restart_backend
    sleep 3
    check_backend || echo "Restart failed"
fi
