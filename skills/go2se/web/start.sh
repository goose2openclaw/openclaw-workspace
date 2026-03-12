#!/bin/bash
# GO2SE Web UI 启动脚本

echo "
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           🪿 GO2SE Web UI 量化交易系统                       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"

# 激活虚拟环境
cd /root/.openclaw/workspace/skills/go2se/web
source ./venv/bin/activate

# 启动服务
echo "🚀 启动 GO2SE Web UI..."
echo "🌐 访问地址: http://localhost:5000"
echo ""

python server.py
