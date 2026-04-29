#!/bin/bash
cd /home/goose/.openclaw/workspace/openclaw-workspace/GO2SE_PLATFORM/versions/vv6/app
fuser -k 8016/tcp 2>/dev/null
sleep 2
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8016 > /tmp/vv6-supreme.log 2>&1 &
disown
sleep 3
curl -s --max-time 3 "http://localhost:8016/health" && echo "VV6 started on port 8016"
