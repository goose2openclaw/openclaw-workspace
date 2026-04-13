#!/bin/bash
# 🪿 GO2SE 轻量级健康检查 - 每5分钟 Cron
# 职责: 快速探活 + 崩溃重启 + Telegram 告警
# 不依赖 Python，纯 bash

PORT=8004
BOT_TOKEN="8405295378:AAG3bvttAQkwO0tjuTo1ypw02TLSKAFLT0o"
CHAT_ID="-1002381931352"

send_telegram() {
    local emoji=$1
    local message=$2
    curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
        -d "chat_id=${CHAT_ID}" \
        -d "text=${emoji} ${message}" > /dev/null 2>&1
}

# 1. 检查 API 是否响应
if curl -s --max-time 5 "http://localhost:${PORT}/api/ping" > /dev/null 2>&1; then
    # API 正常，检查响应速度
    RESPONSE_TIME=$(curl -s --max-time 5 -w "%{time_total}" -o /dev/null "http://localhost:${PORT}/api/ping")
    TIME_MS=$(echo "$RESPONSE_TIME * 1000" | bc 2>/dev/null | cut -d. -f1)
    
    if [ -n "$TIME_MS" ] && [ "$TIME_MS" -gt 5000 ]; then
        send_telegram "⚠️" "🪿 GO2SE响应慢: ${TIME_MS}ms"
    fi
    exit 0
fi

# 2. API 无响应 → 尝试重启
send_telegram "🚨" "🪿 GO2SE Backend停止，尝试重启中..."

# Kill 旧进程
pkill -f "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}" 2>/dev/null
sleep 2

# Restart
cd /root/.openclaw/workspace/GO2SE_PLATFORM/backend
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --log-level warning \
    > /tmp/go2se_${PORT}.log 2>&1 &

# Wait up to 30s
for i in $(seq 1 10); do
    sleep 3
    if curl -s --max-time 3 "http://localhost:${PORT}/api/ping" > /dev/null 2>&1; then
        send_telegram "✅" "🪿 GO2SE Backend 自动重启成功
🕐 $(date -u '+%H:%M UTC')
📊 Port: ${PORT}"
        exit 0
    fi
done

# 重启失败
send_telegram "🚨" "🪿 GO2SE 重启失败，请检查！
🕐 $(date -u '+%H:%M UTC')"
exit 1
