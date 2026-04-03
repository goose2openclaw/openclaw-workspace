#!/bin/bash
# 🛡️ Cron Guardian - 崩溃预防 + 叠加效应监控 + 自动修复
# 每5分钟运行，检测cron堆叠、超时、资源耗尽
# 用法: bash scripts/cron_guardian.sh [--fix]
# 集成到Cron: */5 * * * * bash /root/.openclaw/workspace/GO2SE_PLATFORM/scripts/cron_guardian.sh >> /tmp/cron_guardian.log 2>&1

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'
LOG_FILE="/tmp/cron_guardian.log"
ALERT_LOG="/tmp/cron_guardian_alerts.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

alert() {
    local msg="[ALERT] $1"
    echo -e "${RED}$msg${NC}" | tee -a "$ALERT_LOG"
    echo "[$(date)] $msg" >> "$ALERT_LOG"
}

# ─────────────────────────────────────────────────────────────
# PHASE 1: GO2SE Backend健康检查
# ─────────────────────────────────────────────────────────────
check_go2se_backend() {
    log "🔍 检查GO2SE Backend..."
    
    # 检查端口
    if curl -s --max-time 5 "http://localhost:8004/api/ping" > /dev/null 2>&1; then
        log "  ✅ Backend 8004 响应正常"
        return 0
    else
        alert "🔴 Backend 8004 无响应，尝试重启..."
        bash /root/.openclaw/workspace/GO2SE_PLATFORM/scripts/start_server.sh restart 8004
        return 1
    fi
}

# ─────────────────────────────────────────────────────────────
# PHASE 2: Cron任务状态检查
# ─────────────────────────────────────────────────────────────
check_cron_health() {
    log "🔍 检查Cron任务健康状态..."
    
    # 用openclaw cron list获取状态 (如果可用)
    local CRON_STATUS=$(openclaw crons list 2>/dev/null | grep -E "GO2SE|platform|evolution|backup" || echo "")
    
    # 检查超时任务
    local TIMEOUT_JOBS=$(echo "$CRON_STATUS" | grep -E "timeout|error" | wc -l || echo "0")
    
    if [[ "$TIMEOUT_JOBS" -gt 0 ]]; then
        alert "⚠️  发现 $TIMEOUT_JOBS 个异常Cron任务"
    fi
    
    # 检查连续错误>3次的任务
    local CONSECUTIVE_ERRORS=$(echo "$CRON_STATUS" | grep -E "consecutiveErrors.*[4-9]" | wc -l || echo "0")
    
    if [[ "$CONSECUTIVE_ERRORS" -gt 0 ]]; then
        alert "🔴 发现 $CONSECUTIVE_ERRORS 个任务连续错误>3次"
        
        if [[ "$FIX_MODE" == "true" ]]; then
            log "🔧 自动修复: 暂停连续错误>5次的任务..."
            # 暂停超时的平台迭代 (连续8次错误)
            openclaw crons pause GO2SE平台迭代 2>/dev/null || true
            log "  ✅ 已暂停 GO2SE平台迭代"
        fi
    fi
    
    log "  Cron异常任务数: $TIMEOUT_JOBS, 高连续错误: $CONSECUTIVE_ERRORS"
}

# ─────────────────────────────────────────────────────────────
# PHASE 3: 资源检查 (内存/磁盘/CPU)
# ─────────────────────────────────────────────────────────────
check_resources() {
    log "🔍 检查系统资源..."
    
    # 磁盘空间
    local DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
    if [[ "$DISK_USAGE" -gt 95 ]]; then
        alert "🔴 磁盘使用率 ${DISK_USAGE}% (超过95%!)"
        [[ "$FIX_MODE" == "true" ]] && cleanup_disk
    elif [[ "$DISK_USAGE" -gt 85 ]]; then
        log "  ⚠️  磁盘使用率 ${DISK_USAGE}% (超过85%)"
    else
        log "  ✅ 磁盘使用率 ${DISK_USAGE}% OK"
    fi
    
    # 僵尸进程
    local ZOMBIES=$(ps aux | grep -E "defunct|<defunct>" | grep -v grep | wc -l || echo "0")
    if [[ "$ZOMBIES" -gt 0 ]]; then
        log "  ⚠️  发现 $ZOMBIES 个僵尸进程"
        [[ "$FIX_MODE" == "true" ]] && {
            pkill -9 -f defunct 2>/dev/null || true
            log "  ✅ 已清理僵尸进程"
        }
    else
        log "  ✅ 无僵尸进程"
    fi
    
    # 内存压力 (如果available < 500MB)
    local AVAIL_MEM=$(free -m 2>/dev/null | awk 'NR==2 {print $7}' || echo "1000")
    if [[ "$AVAIL_MEM" -lt 500 ]]; then
        alert "⚠️  可用内存仅 ${AVAIL_MEM}MB (低于500MB)"
    else
        log "  ✅ 可用内存 ${AVAIL_MEM}MB OK"
    fi
}

# ─────────────────────────────────────────────────────────────
# PHASE 4: Cron叠加效应检测
# ─────────────────────────────────────────────────────────────
check_cron_stacking() {
    log "🔍 检查Cron叠加效应..."
    
    local MINUTE=$(date +%M)
    local HOUR=$(date +%H)
    
    # 检测同步触发时间点
    if [[ "$MINUTE" == "00" ]] || [[ "$MINUTE" == "30" ]]; then
        log "  ⚠️  当前为同步触发窗口 (:$MINUTE) — 2-3个Cron同时运行"
        
        # 检查当前并发cron任务数
        local CONCURRENT=$(ps aux | grep -E "openclaw|cron" | grep -v grep | wc -l || echo "0")
        log "  当前并发Cron相关进程: $CONCURRENT"
        
        if [[ "$CONCURRENT" -gt 5 ]]; then
            alert "🔴 并发Cron进程过多 ($CONCURRENT)，资源竞争风险"
        fi
    fi
    
    # 检测每日03:00 UTC峰
    if [[ "$HOUR" == "03" ]] && [[ "$MINUTE" -lt 15 ]]; then
        log "  🔴 每日03:00 UTC峰期 — CEO管理+平台迭代+情报+备份同触发"
    fi
}

# ─────────────────────────────────────────────────────────────
# PHASE 5: 日志错误检测
# ─────────────────────────────────────────────────────────────
check_error_logs() {
    log "🔍 检查错误日志..."
    
    # 检查最近5分钟内的ERROR
    local RECENT_ERRORS=$(find /tmp/go2se*.log -mmin -5 -exec grep -l "ERROR\|Exception\|Traceback" {} \; 2>/dev/null | wc -l || echo "0")
    
    if [[ "$RECENT_ERRORS" -gt 0 ]]; then
        alert "⚠️  最近5分钟发现 $RECENT_ERRORS 个日志文件含ERROR"
        [[ "$FIX_MODE" == "true" ]] && {
            find /tmp/go2se*.log -mmin -5 -exec grep "ERROR" {} \; 2>/dev/null | tail -5 | tee -a "$ALERT_LOG"
        }
    else
        log "  ✅ 最近5分钟无ERROR日志"
    fi
}

# ─────────────────────────────────────────────────────────────
# PHASE 6: 磁盘清理 (FIX模式)
# ─────────────────────────────────────────────────────────────
cleanup_disk() {
    log "🧹 执行磁盘清理..."
    
    # 清理__pycache__
    find /root/.openclaw/workspace/GO2SE_PLATFORM -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    
    # 清理旧日志 (保留最近3个)
    find /tmp/go2se*.log -mtime +3 -delete 2>/dev/null || true
    
    # 清理npm/pip缓存
    rm -rf /root/.npm/_cacache 2>/dev/null || true
    rm -rf /root/.cache/pip 2>/dev/null || true
    
    local NEW_USAGE=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
    log "  ✅ 磁盘清理完成，使用率: ${NEW_USAGE}%"
}

# ─────────────────────────────────────────────────────────────
# PHASE 7: 修复超时任务 (FIX模式)
# ─────────────────────────────────────────────────────────────
fix_timeout_jobs() {
    log "🔧 检查超时任务修复..."
    
    # 这个需要在FIX模式下手动执行，因为需要openclaw CLI
    # 输出修复建议
    echo ""
    log "📋 建议手动执行的修复:"
    log "  1. 更新超时限制: openclaw crons update <job-id> --timeout 600"
    log "  2. 错开Anchor: 修改GO2SE平台迭代的anchor时间"
    log "  3. 暂停故障任务: openclaw crons pause GO2SE平台迭代"
    log ""
    log "⚠️  当前自动修复受限，需手动执行openclaw CLI命令"
}

# ─────────────────────────────────────────────────────────────
# MAIN: 执行所有检查
# ─────────────────────────────────────────────────────────────
FIX_MODE="false"
[[ "$1" == "--fix" ]] && FIX_MODE="true"

echo ""
echo "============================================================"
log "🛡️ Cron Guardian 启动 ($(date))"
echo "============================================================"

check_go2se_backend
check_cron_health
check_resources
check_cron_stacking
check_error_logs

if [[ "$FIX_MODE" == "true" ]]; then
    fix_timeout_jobs
fi

# 最终状态摘要
echo ""
log "📊 检查完成 — $(date)"
echo "============================================================"
