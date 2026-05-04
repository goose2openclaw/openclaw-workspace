#!/bin/bash
# GO2SE Genius 完整自动启动脚本
# 添加到 crontab: @reboot /home/goose/.openclaw/workspace/openclaw-workspace/GO2SE_PLATFORM/scripts/auto_start_go2se.sh

LOG_DIR="/home/goose/.openclaw/logs/go2se"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/autostart_$(date +%Y%m%d_%H%M%S).log"

echo "🚀 GO2SE Genius 自动启动 - $(date)" | tee -a "$LOG_FILE"

# 1. Backend服务 (端口 8000)
echo "📦 启动 Backend (8000)..." | tee -a "$LOG_FILE"
cd /home/goose/.openclaw/workspace/openclaw-workspace/GO2SE_PLATFORM/backend
if pgrep -f "uvicorn.*8000" > /dev/null; then
    echo "  Backend已在运行" | tee -a "$LOG_FILE"
else
    nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 >> "$LOG_FILE" 2>&1 &
    sleep 3
    if curl -s --max-time 5 "http://localhost:8000/docs" > /dev/null; then
        echo "  ✅ Backend启动成功 (8000)" | tee -a "$LOG_FILE"
    else
        echo "  ⚠️ Backend启动中..." | tee -a "$LOG_FILE"
    fi
fi

# 2. VV6服务 (端口 8016)
echo "📦 启动 VV6 (8016)..." | tee -a "$LOG_FILE"
cd /home/goose/.openclaw/workspace/openclaw-workspace/GO2SE_PLATFORM/versions/vv6/app
if pgrep -f "uvicorn.*8016" > /dev/null; then
    echo "  VV6已在运行" | tee -a "$LOG_FILE"
else
    nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8016 >> "$LOG_FILE" 2>&1 &
    sleep 3
    if curl -s --max-time 5 "http://localhost:8016/health" > /dev/null; then
        echo "  ✅ VV6启动成功 (8016)" | tee -a "$LOG_FILE"
    else
        echo "  ⚠️ VV6启动中..." | tee -a "$LOG_FILE"
    fi
fi

# 3. 验证所有服务
echo "" | tee -a "$LOG_FILE"
echo "📊 服务状态检查:" | tee -a "$LOG_FILE"
for port in 8000 8016; do
    if curl -s --max-time 3 "http://localhost:$port/health" > /dev/null 2>&1 || curl -s --max-time 3 "http://localhost:$port/docs" > /dev/null 2>&1; then
        echo "  ✅ 端口 $port: 在线" | tee -a "$LOG_FILE"
    else
        echo "  ❌ 端口 $port: 离线" | tee -a "$LOG_FILE"
    fi
done

echo "" | tee -a "$LOG_FILE"
echo "✅ 自动启动完成 - $(date)" | tee -a "$LOG_FILE"
