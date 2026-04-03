#!/bin/bash
# 🪿 GO2SE Platform v6 一键部署脚本

set -e

echo "=========================================="
echo "  🪿 GO2SE Platform v6 - 北斗七鑫"
echo "=========================================="

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker 未安装${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose 未安装${NC}"
    exit 1
fi

# 导航到v6目录
cd "$(dirname "$0")/versions/v6"

# 创建必要目录
mkdir -p logs data

# 检查.env
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env 文件不存在，复制示例配置...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠️  请编辑 .env 填入API密钥${NC}"
    exit 0
fi

echo -e "${GREEN}✅ 环境检查通过${NC}"

# 选择部署模式
echo ""
echo "请选择部署模式:"
echo "1) 开发模式 (后端5000 + 前端3000)"
echo "2) 生产模式 (完整Docker部署)"
echo "3) 仅后端"
echo "4) 仅前端"
read -p "请输入 (1-4): " mode

case $mode in
    1)
        echo -e "${GREEN}🚀 启动开发模式...${NC}"
        # 启动后端
        cd backend
        pip install -r requirements.txt -q
        python -m flask run --host=0.0.0.0 --port=5000 &
        cd ..
        # 启动前端
        cd frontend
        npm install 2>/dev/null || npm ci
        npm start &
        echo -e "${GREEN}✅ 开发服务已启动${NC}"
        echo "  后端: http://localhost:5000"
        echo "  前端: http://localhost:3000"
        ;;
    2)
        echo -e "${GREEN}🚀 启动生产模式...${NC}"
        docker-compose up -d
        echo -e "${GREEN}✅ 生产服务已启动${NC}"
        docker-compose ps
        ;;
    3)
        echo -e "${GREEN}🚀 启动后端服务...${NC}"
        cd backend
        pip install -r requirements.txt -q
        python -m flask run --host=0.0.0.0 --port=5000
        ;;
    4)
        echo -e "${GREEN}🚀 启动前端服务...${NC}"
        cd frontend
        npm install 2>/dev/null || npm ci
        npm start
        ;;
    *)
        echo -e "${RED}❌ 无效选择${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}=========================================="
echo "  🎉 部署完成!"
echo "==========================================${NC}"
