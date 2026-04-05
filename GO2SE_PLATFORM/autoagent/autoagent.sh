#!/bin/bash
# GO2SE AutoAgent 启动脚本

cd /root/.openclaw/workspace/GO2SE_PLATFORM

echo "🪿 GO2SE AutoAgent 启动中..."

# 检查后端
if ! curl -s http://localhost:8004/api/stats > /dev/null 2>&1; then
    echo "→ 启动 Backend..."
    cd backend
    nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8004 &>/dev/null &
    cd ..
    sleep 3
fi

# 检查前端
if ! curl -s http://localhost:8010/ > /dev/null 2>&1; then
    echo "→ 启动 Frontend..."
    cd versions/v10
    nohup python3 -m http.server 8010 &>/dev/null &
    cd ../..
    sleep 2
fi

# 启动AutoAgent
echo "→ 启动 AutoAgent..."
nohup python3 autoagent/autoagent_core.py &>/dev/null &

echo "✅ GO2SE AutoAgent 已启动"
echo "状态: $(curl -s http://localhost:8004/api/stats | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get(\"data\",{}).get(\"version\",\"unknown\"))')"
echo "前端: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:8010/)"