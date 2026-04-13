#!/bin/bash
# GO2SE 自我修复脚本 - Capability Evolver风格 (集成Telegram告警)

BOT_TOKEN="8405295378:AAG3bvttAQkwO0tjuTo1ypw02TLSKAFLT0o"
CHAT_ID="-1002381931352"

send_alert() {
    local level=$1
    local message=$2
    local emoji=""
    
    case $level in
        "critical") emoji="🚨" ;;
        "warning") emoji="⚠️" ;;
        "success") emoji="✅" ;;
        "info") emoji="ℹ️" ;;
        *) emoji="📢" ;;
    esac
    
    curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
        -d "chat_id=$CHAT_ID" \
        -d "text=$emoji $message" > /dev/null 2>&1
}

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 检测函数
check_backend() {
    curl -s http://localhost:8004/api/stats > /dev/null 2>&1
}

check_frontend() {
    # 前端已集成到Backend (8004)，检查根路径
    curl -s http://localhost:8004/ | grep -q "GO2SE" > /dev/null 2>&1
}

# 修复函数
fix_backend() {
    echo -e "${YELLOW}⚠️ Backend停止，尝试重启...${NC}"
    pkill -f "uvicorn app.main:app --host 0.0.0.0 --port 8004" 2>/dev/null
    sleep 2
    cd /root/.openclaw/workspace/GO2SE_PLATFORM/backend
    nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8004 --log-level warning > /tmp/go2se.log 2>&1 &
    BACKEND_PID=$!
    # 等待最多15秒，每3秒检查一次
    for i in 1 2 3 4 5; do
        sleep 3
        if check_backend; then
            echo -e "${GREEN}✅ Backend重启成功 (PID: $BACKEND_PID)${NC}"
            send_alert "warning" "⚠️ GO2SE Backend自动重启成功
🕐 $(date -u '+%Y-%m-%d %H:%M UTC')"
            return 0
        fi
    done
    # 最后一次检查
    if check_backend; then
        echo -e "${GREEN}✅ Backend重启成功${NC}"
        send_alert "warning" "⚠️ GO2SE Backend自动重启成功
🕐 $(date -u '+%Y-%m-%d %H:%M UTC')"
        return 0
    else
        echo -e "${RED}❌ Backend重启失败${NC}"
        send_alert "critical" "🚨 GO2SE Backend重启失败！
🕐 $(date -u '+%Y-%m-%d %H:%M UTC')
⚠️ 需要人工介入"
        return 1
    fi
}

fix_frontend() {
    echo -e "${YELLOW}⚠️ 前端异常，尝试重启...${NC}"
    # 前端由Backend托管，尝试重启Backend
    fix_backend
    if check_frontend; then
        echo -e "${GREEN}✅ Frontend重启成功${NC}"
        send_alert "warning" "⚠️ GO2SE Frontend自动重启成功
🕐 $(date -u '+%Y-%m-%d %H:%M UTC')"
        return 0
    else
        echo -e "${RED}❌ Frontend重启失败${NC}"
        send_alert "critical" "🚨 GO2SE Frontend重启失败！
🕐 $(date -u '+%Y-%m-%d %H:%M UTC')
⚠️ 需要人工介入"
        return 1
    fi
}

# 主循环
echo "╔══════════════════════════════════════════════════════╗"
echo "║  🧬 GO2SE 自我修复循环                      ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

ISSUES_FOUND=0
ISSUES_FIXED=0

# 检查Backend
echo -n "检查 Backend (8004)... "
if check_backend; then
    echo -e "${GREEN}✅ 正常${NC}"
else
    echo -e "${RED}❌ 停止${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND+1))
    fix_backend && ISSUES_FIXED=$((ISSUES_FIXED+1))
fi

# 检查Frontend (集成在Backend 8004中)
echo -n "检查 Frontend (8004/)... "
if check_frontend; then
    echo -e "${GREEN}✅ 正常${NC}"
else
    echo -e "${RED}❌ 停止${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND+1))
    fix_frontend && ISSUES_FIXED=$((ISSUES_FIXED+1))
fi

# 检查磁盘空间
echo -n "检查 磁盘空间... "
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 90 ]; then
    echo -e "${GREEN}✅ ${DISK_USAGE}% (正常)${NC}"
else
    echo -e "${RED}⚠️ ${DISK_USAGE}% (过高)${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND+1))
    send_alert "critical" "🚨 磁盘空间告警！
🕐 $(date -u '+%Y-%m-%d %H:%M UTC')
💾 使用率: ${DISK_USAGE}%"
fi

# 检查内存
echo -n "检查 内存... "
MEM_USAGE=$(free | tail -1 | awk '{print int($3/$2 * 100)}')
if [ "$MEM_USAGE" -lt 85 ]; then
    echo -e "${GREEN}✅ ${MEM_USAGE}% (正常)${NC}"
else
    echo -e "${YELLOW}⚠️ ${MEM_USAGE}% (偏高)${NC}"
fi

# 总结
echo ""
echo "═══════════════════════════════════════════════════════"
echo -e "问题发现: ${ISSUES_FOUND}"
echo -e "问题修复: ${ISSUES_FIXED}"
echo "═══════════════════════════════════════════════════════"

if [ $ISSUES_FIXED -eq $ISSUES_FOUND ] && [ $ISSUES_FOUND -gt 0 ]; then
    echo -e "${GREEN}✅ 所有问题已修复${NC}"
    exit 0
elif [ $ISSUES_FOUND -gt 0 ]; then
    echo -e "${YELLOW}⚠️ 部分问题未修复${NC}"
    exit 1
else
    echo -e "${GREEN}✅ 系统健康${NC}"
    exit 0
fi