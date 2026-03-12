#!/bin/bash
# GO2SE Web UI 启动脚本

echo "
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           🪿 GO2SE Web UI 量化交易系统                       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"

# 检查依赖
echo "📦 检查依赖..."
pip install flask requests -q 2>/dev/null

# 启动服务
echo "🚀 启动 GO2SE Web UI..."
echo "🌐 访问地址: http://localhost:5000"
echo ""

cd /root/.openclaw/workspace/skills/go2se/web
python3 server.py
