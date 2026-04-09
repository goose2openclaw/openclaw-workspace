#!/bin/bash
# 🪿 GO2SE 启动脚本

set -e

echo "🪿 GO2SE 量化交易平台启动..."

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "📦 安装依赖..."
pip install -r backend/requirements.txt

# 复制环境变量
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️ 请编辑 .env 填入币安API密钥"
fi

# 启动
echo "🚀 启动服务..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
