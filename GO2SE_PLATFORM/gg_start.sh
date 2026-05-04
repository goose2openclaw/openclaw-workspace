#!/bin/bash
# GG (GO2SE Genius) 自动启动脚本
# 版本: v1.0
# 日期: 2026-05-03

echo "=============================================="
echo "🧠 GG 自动启动系统"
echo "=============================================="

LOG_DIR="/home/goose/.openclaw/logs/gg"
mkdir -p "$LOG_DIR"

# 1. 启动GG主循环
echo "[1/4] 启动GG主循环..."
cd /home/goose/.openclaw/workspace/skills/go2se-genius-gg
nohup python3 gg_autonomous.py >> "$LOG_DIR/gg_main.log" 2>&1 &
GG_PID=$!
echo "   GG主循环 PID: $GG_PID"

# 2. 启动信号监控
echo "[2/4] 启动信号监控..."
cd /home/goose/.openclaw/workspace/openclaw-workspace/GO2SE_PLATFORM/strategies/signal_monitor
nohup python3 auto_monitor.py >> "$LOG_DIR/signal_monitor.log" 2>&1 &
MONITOR_PID=$!
echo "   信号监控 PID: $MONITOR_PID"

# 3. 启动AI自主系统
echo "[3/4] 启动AI自主系统..."
cd /home/goose/.openclaw/workspace/openclaw-workspace/GO2SE_PLATFORM/strategies/ai_autonomous
nohup python3 ai_loop.py >> "$LOG_DIR/ai_loop.log" 2>&1 &
AI_PID=$!
echo "   AI自主 PID: $AI_PID"

# 4. 验证服务
echo "[4/4] 验证服务..."
sleep 3

echo ""
echo "=============================================="
echo "📊 GG 服务状态"
echo "=============================================="

# 检查进程
for name in "gg_autonomous" "auto_monitor" "ai_loop"; do
    if pgrep -f "$name" > /dev/null; then
        echo "   ✅ $name: 运行中"
    else
        echo "   ❌ $name: 未运行"
    fi
done

# 检查端口
for port in 8000 8016; do
    if curl -s --max-time 2 "http://localhost:$port/health" > /dev/null 2>&1; then
        echo "   ✅ 端口 $port: 在线"
    else
        echo "   ❌ 端口 $port: 离线"
    fi
done

echo ""
echo "=============================================="
echo "🧠 GG 系统已全面上线!"
echo "=============================================="
echo ""
echo "日志位置: $LOG_DIR"
echo ""
