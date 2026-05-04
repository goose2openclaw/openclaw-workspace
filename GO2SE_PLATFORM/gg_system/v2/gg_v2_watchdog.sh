#!/bin/bash
# GG v2 看门狗 - 永不掉线
# 检测间隔: 600秒 (10分钟)

LOG_FILE="/home/goose/.openclaw/logs/gg/v2_watchdog.log"
PID_FILE="/tmp/gg_v2.pid"

echo "🐕 GG v2 看门狗启动 (600秒检测)..."

while true; do
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ! ps -p $PID > /dev/null 2>&1; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🔄 GG v2 进程已停止，重启中..." >> "$LOG_FILE"
            cd /home/goose/.openclaw/workspace/openclaw-workspace/GO2SE_PLATFORM/gg_system/v2
            nohup python3 gg_v2.py > /tmp/gg_v2.log 2>&1 &
            NEW_PID=$!
            echo $NEW_PID > "$PID_FILE"
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ GG v2 已重启，PID: $NEW_PID" >> "$LOG_FILE"
        fi
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🚀 首次启动 GG v2..." >> "$LOG_FILE"
        cd /home/goose/.openclaw/workspace/openclaw-workspace/GO2SE_PLATFORM/gg_system/v2
        nohup python3 gg_v2.py > /tmp/gg_v2.log 2>&1 &
        NEW_PID=$!
        echo $NEW_PID > "$PID_FILE"
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ GG v2 已启动，PID: $NEW_PID" >> "$LOG_FILE"
    fi
    sleep 600
done
