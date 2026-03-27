#!/bin/bash
# GO2SE 护食平台启动脚本
# 四种模式: 游客/订阅/分成/私募LP

echo "
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║      🪿 GO2SE 护食 - 量化投资平台                           ║
║      四种模式: 游客 | 订阅 | 分成 | 私募LP                  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"

# 激活虚拟环境
cd /root/.openclaw/workspace/skills/go2se/web
source ./venv/bin/activate

# 检查Flask
python -c "import flask" 2>/dev/null || pip install flask requests

# 启动服务
echo "🚀 启动 GO2SE 护食平台..."
echo "🌐 访问地址: http://localhost:5000"
echo "📱 功能: 模拟交易 | 私募LP | 薅羊毛 | 声纳趋势"
echo ""

python server.py
