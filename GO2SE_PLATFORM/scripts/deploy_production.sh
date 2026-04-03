#!/bin/bash
#============================================================================---
# 🚀 GO2SE 生产环境部署脚本
#============================================================================---
# Usage: ./deploy_production.sh <API_KEY> <SECRET_KEY> [DRY_RUN|LIVE]
#============================================================================---

set -e

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 参数
API_KEY=${1:-""}
SECRET_KEY=${2:-""}
MODE=${3:-"dry_run"}

echo "=============================================="
echo "🚀 GO2SE 生产环境部署"
echo "=============================================="
echo "交易模式: $MODE"
echo "时间: $(date)"
echo "=============================================="

# 检查参数
if [ "$MODE" = "live" ]; then
    if [ -z "$API_KEY" ] || [ -z "$SECRET_KEY" ]; then
        echo -e "${RED}❌ 错误: live模式需要API Key和Secret Key${NC}"
        exit 1
    fi
    echo -e "${YELLOW}⚠️  警告: 即将切换到LIVE实盘交易模式!${NC}"
    read -p "确认继续? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "取消部署"
        exit 0
    fi
fi

# 停止现有进程
echo -e "\n${YELLOW}1. 停止现有进程...${NC}"
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "gunicorn.*app.main:app" 2>/dev/null || true
sleep 2

# 备份配置
echo -e "\n${YELLOW}2. 备份配置...${NC}"
if [ -f backend/.env ]; then
    cp backend/.env backend/.env.backup.$(date +%Y%m%d_%H%M%S)
fi

# 更新配置
echo -e "\n${YELLOW}3. 更新环境配置...${NC}"
cat > backend/.env << ENVEOF
TRADING_MODE=$MODE
BINANCE_API_KEY=$API_KEY
BINANCE_SECRET_KEY=$SECRET_KEY
LOG_LEVEL=INFO
ENVEOF

# 验证
echo -e "\n${YELLOW}4. 验证配置...${NC}"
cd backend
python3 -c "
import sys
sys.path.insert(0, '.')
from app.core.config import settings
print(f'  交易模式: {settings.TRADING_MODE}')
print(f'  Backend: OK')
"

# 启动服务
echo -e "\n${YELLOW}5. 启动服务...${NC}"
cd /root/.openclaw/workspace/GO2SE_PLATFORM

# 使用gunicorn
nohup python3 -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 2 \
    --timeout 120 \
    > backend.log 2>&1 &

echo $! > backend.pid

sleep 3

# 健康检查
echo -e "\n${YELLOW}6. 健康检查...${NC}"
for i in {1..5}; do
    if curl -s localhost:8004/api/health | grep -q "healthy"; then
        echo -e "${GREEN}✅ Backend健康检查通过${NC}"
        break
    fi
    echo "等待服务启动... ($i/5)"
    sleep 2
done

# 获取API状态
echo -e "\n${YELLOW}7. 获取状态...${NC}"
curl -s localhost:8004/api/health | python3 -m json.tool 2>/dev/null | head -15

echo -e "\n${GREEN}=============================================="
echo -e "✅ 部署完成!"
echo -e "==============================================${NC}"
echo "模式: $MODE"
echo "日志: /root/.openclaw/workspace/GO2SE_PLATFORM/backend.log"
echo "PID: $(cat backend.pid 2>/dev/null || echo 'N/A')"
