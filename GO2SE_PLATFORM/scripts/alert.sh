#!/bin/bash
# GO2SE Telegram告警脚本

BOT_TOKEN="8405295378:AAG3bvttAQkwO0tjuTo1ypw02TLSKAFLT0o"
CHAT_ID="-1002381931352"

send_alert() {
    local level=$1
    local message=$2
    local emoji=""
    
    case $level in
        "critical") emoji="🚨" ;;
        "warning") emoji="⚠️" ;;
        "info") emoji="ℹ️" ;;
        "success") emoji="✅" ;;
        *) emoji="📢" ;;
    esac
    
    curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
        -d "chat_id=$CHAT_ID" \
        -d "text=$emoji $message" > /dev/null 2>&1
}

# 测试告警
send_alert "success" "🧪 GO2SE告警测试成功！

⏰ 时间: $(date -u '+%Y-%m-%d %H:%M UTC')
🔧 状态: 系统正常"

echo "告警脚本已创建"