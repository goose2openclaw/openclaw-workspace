#!/bin/bash
# GO2SE 手动日志轮转脚本 (替代logrotate)

LOG_DIR="/tmp"
KEEP_DAYS=7

# 轮转日志
for log in go2se.log v14_hermes.log self_heal.log; do
    if [ -f "$LOG_DIR/$log" ]; then
        # 如果日志存在且大于10MB，则轮转
        SIZE=$(stat -f%z "$LOG_DIR/$log" 2>/dev/null || stat -c%s "$LOG_DIR/$log" 2>/dev/null)
        if [ "$SIZE" -gt 10485760 ]; then
            mv "$LOG_DIR/$log" "$LOG_DIR/${log}.1"
            gzip -9 "$LOG_DIR/${log}.1"
            : > "$LOG_DIR/$log"
            echo "轮转: $log -> ${log}.1.gz"
        fi
    fi
done

# 删除旧日志
find $LOG_DIR -name "*.log.*.gz" -mtime +$KEEP_DAYS -delete 2>/dev/null

echo "日志轮转完成: $(date)"