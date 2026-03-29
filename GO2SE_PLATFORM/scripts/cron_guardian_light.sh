#!/bin/bash
# 🛡️ Cron Guardian LIGHTWEIGHT - 轻量级崩溃预防
# 不调用openclaw CLI，避免SIGKILL
# 用法: bash scripts/cron_guardian_light.sh

# 轻量检查: Backend + 磁盘 + 进程 + 日志错误
# 耗时应 < 10秒

RESULT=""
LEVEL="🟢"

# 1. Backend
if curl -s --max-time 5 http://localhost:8004/api/stats > /dev/null 2>&1; then
    RESULT="${RESULT}✅ Backend OK | "
else
    RESULT="${RESULT}🔴 Backend DOWN | "
    LEVEL="🔴"
fi

# 2. 磁盘
DISK=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
if [[ "$DISK" -gt 95 ]]; then
    RESULT="${RESULT}🔴 Disk ${DISK}% | "
    LEVEL="🔴"
elif [[ "$DISK" -gt 85 ]]; then
    RESULT="${RESULT}⚠️ Disk ${DISK}% | "
    [[ "$LEVEL" == "🟢" ]] && LEVEL="⚠️"
else
    RESULT="${RESULT}✅ Disk ${DISK}% | "
fi

# 3. 僵尸进程
ZOMBIES=$(ps aux | grep -E "defunct|<defunct>" | grep -v grep | wc -l)
if [[ "$ZOMBIES" -gt 0 ]]; then
    RESULT="${RESULT}⚠️ Zombies $ZOMBIES | "
    [[ "$LEVEL" == "🟢" ]] && LEVEL="⚠️"
else
    RESULT="${RESULT}✅ No zombies | "
fi

# 4. 最近ERROR日志
ERRORS=$(find /tmp/go2se*.log -mmin -10 -exec grep -l "ERROR\|Exception\|Traceback" {} \; 2>/dev/null | wc -l)
if [[ "$ERRORS" -gt 0 ]]; then
    RESULT="${RESULT}🔴 $ERRORS error logs | "
    LEVEL="🔴"
else
    RESULT="${RESULT}✅ No recent errors | "
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] $LEVEL $RESULT"

# 如果🔴，重启Backend
if [[ "$LEVEL" == "🔴" ]]; then
    if [[ "$RESULT" == *"Backend DOWN"* ]]; then
        echo "🔄 重启Backend..."
        bash /root/.openclaw/workspace/GO2SE_PLATFORM/scripts/start_server.sh restart 8004
    fi
fi
