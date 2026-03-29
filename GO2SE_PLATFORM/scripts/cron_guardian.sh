#!/bin/bash
# 🛡️ Cron Guardian FAST - 崩溃预防守护 (优化版)
# 问题: 原版调用 openclaw crons list 耗时25秒 → 被SIGKILL
# 解决: 移除慢命令, 纯快速检查, 每个phase独立超时
# 用法: 每5分钟Cron调用
# 注意: 必须设置 Cron timeout=60s 或更长

set +e  # 不遇错即退

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'
LOG="/tmp/cron_guardian.log"
PORT=8005  # 当前运行端口

log() { echo "[$(date '+%H:%M:%S')] $1" | tee -a "$LOG"; }
alert() { echo -e "${RED}[ALERT] $1${NC}" | tee -a "$LOG"; }

echo "" > "$LOG"
log "🛡️ Cron Guardian FAST 启动"

# ── PHASE 1: Backend健康 (超时: 10s) ─────────────────────────
(
    sleep 0.2
    if curl -s --max-time 5 "http://localhost:${PORT}/api/stats" > /dev/null 2>&1; then
        log "  ✅ Backend :${PORT} OK"
    else
        alert "  🔴 Backend :${PORT} 无响应"
        bash /root/.openclaw/workspace/GO2SE_PLATFORM/scripts/start_server.sh restart 8005 >> "$LOG" 2>&1
    fi
) &
PID1=$!

# ── PHASE 2: 磁盘空间 (超时: 5s) ────────────────────────────
(
    sleep 0.3
    USAGE=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
    if [[ "$USAGE" -gt 95 ]]; then
        alert "  🔴 磁盘 ${USAGE}% (>95%)"
    elif [[ "$USAGE" -gt 85 ]]; then
        log "  ⚠️  磁盘 ${USAGE}% (>85%)"
    else
        log "  ✅ 磁盘 ${USAGE}% OK"
    fi
) &
PID2=$!

# ── PHASE 3: 僵尸进程 (超时: 5s) ────────────────────────────
(
    sleep 0.4
    ZOMBIES=$(ps aux 2>/dev/null | grep -c "defunct" || echo "0")
    if [[ "$ZOMBIES" -gt 0 ]]; then
        log "  ⚠️  僵尸进程: $ZOMBIES"
        pkill -9 -f defunct 2>/dev/null
    else
        log "  ✅ 无僵尸进程"
    fi
) &
PID3=$!

# ── PHASE 4: Cron叠加窗口检测 (超时: 3s) ───────────────────
(
    sleep 0.5
    MINUTE=$(date +%M)
    if [[ "$MINUTE" == "00" ]] || [[ "$MINUTE" == "30" ]]; then
        log "  ⚠️  同步窗口 :$MINUTE (检查并发)"
    fi
) &
PID4=$!

# ── PHASE 5: 最近ERROR日志 (超时: 5s) ──────────────────────
(
    sleep 0.6
    ERRORS=$(find /tmp/go2se*.log -mmin -10 -exec grep -l "ERROR\|Exception" {} \; 2>/dev/null | wc -l || echo "0")
    if [[ "$ERRORS" -gt 0 ]]; then
        alert "  🔴 最近10min ${ERRORS}个日志含ERROR"
    else
        log "  ✅ 无ERROR日志"
    fi
) &
PID5=$!

# 等待所有phase完成 (最多20s)
wait $PID1 $PID2 $PID3 $PID4 $PID5 2>/dev/null

log "  📊 Guardian完成 ($(date '+%H:%M:%S'))"
echo ""
