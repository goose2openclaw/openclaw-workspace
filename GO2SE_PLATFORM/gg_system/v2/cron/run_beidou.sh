#!/bin/bash
INTERVAL=${1:-30}
while true; do
    echo "[$(date)] 北斗七鑫扫描..."
    cd /home/goose/.openclaw/workspace/openclaw-workspace/GO2SE_PLATFORM/gg_system/v2/cron
    python3 beidou_scan.py >> /home/goose/.openclaw/logs/gg/beidou_scan.log 2>&1
    sleep $((INTERVAL * 60))
done
