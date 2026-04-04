#!/bin/bash
# sessions-send 测试脚本
# 测试跨会话消息功能

set -e

GATEWAY_URL="${GATEWAY_URL:-http://localhost:18789}"
SESSION_KEY="${SESSION_KEY:-main}"

echo "=== sessions-send 测试脚本 ==="
echo "Gateway: $GATEWAY_URL"
echo "Session: $SESSION_KEY"
echo ""

# 1. 列出会话
echo "1. 列出活跃会话..."
curl -s "$GATEWAY_URL/api/sessions" | python3 -c "
import json, sys
data = json.load(sys.stdin)
sessions = data.get('sessions', data.get('data', []))
print(f'找到 {len(sessions)} 个会话:')
for s in sessions[:5]:
    key = s.get('key', s.get('sessionKey', 'unknown'))
    kind = s.get('kind', 'unknown')
    print(f'  - {key[:50]} [{kind}]')
"

echo ""

# 2. 发送即发即忘消息
echo "2. 发送即发即忘消息 (timeout=0)..."
RESPONSE=$(curl -s -X POST "$GATEWAY_URL/api/sessions/$SESSION_KEY/messages?timeout=0" \
  -H "Content-Type: application/json" \
  -d '{"content": "test message from sessions-send"}')
echo "响应: $RESPONSE"

echo ""

# 3. 获取主会话历史
echo "3. 获取主会话历史..."
curl -s "$GATEWAY_URL/api/sessions/$SESSION_KEY/history?limit=5" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    messages = data.get('messages', data.get('data', []))
    print(f'最近 {len(messages)} 条消息:')
    for m in messages[-5:]:
        role = m.get('role', 'unknown')
        content = str(m.get('content', ''))[:50]
        print(f'  [{role}] {content}...')
except Exception as e:
    print(f'Error: {e}')
"

echo ""
echo "=== 测试完成 ==="
