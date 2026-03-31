#!/bin/bash
#============================================================================---
# 🔴 切换到LIVE实盘交易模式
#============================================================================---
# ⚠️ 警告: 这将开始真实交易!
#============================================================================---

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

API_KEY=$1
SECRET_KEY=$2

echo -e "${RED}=============================================="
echo -e "🔴 警告: 即将切换到LIVE实盘交易模式!"
echo -e "==============================================${NC}"

if [ -z "$API_KEY" ] || [ -z "$SECRET_KEY" ]; then
    echo -e "${RED}❌ 错误: 需要提供API Key和Secret Key${NC}"
    echo "Usage: $0 <API_KEY> <SECRET_KEY>"
    exit 1
fi

# 确认
echo ""
echo -e "${YELLOW}请确认以下事项:${NC}"
echo "  1. API Key已设置权限(仅现货交易,禁用提现)"
echo "  2. 账户有足够的USDT/USDC"
echo "  3. 风控参数已验证"
echo ""
read -p "输入 'yes' 确认切换到live模式: " confirm

if [ "$confirm" != "yes" ]; then
    echo "取消操作"
    exit 0
fi

# 备份当前配置
echo -e "\n${YELLOW}1. 备份当前配置...${NC}"
cp backend/.env backend/.env.dry_run_backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true

# 创建新配置
echo -e "\n${YELLOW}2. 创建live模式配置...${NC}"
cat > backend/.env << ENVEOF
TRADING_MODE=live
BINANCE_API_KEY=$API_KEY
BINANCE_SECRET_KEY=$SECRET_KEY
STOP_LOSS=0.03
TAKE_PROFIT=0.06
TRAILING_STOP=0.03
POSITION_SIZE=0.10
LEVERAGE=2
MAX_POSITION=0.6
ENVEOF

# 重启服务
echo -e "\n${YELLOW}3. 重启服务...${NC}"
pkill -f "uvicorn app.main:app" 2>/dev/null || true
sleep 2

cd /root/.openclaw/workspace/GO2SE_PLATFORM/backend
nohup python3 -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 2 \
    > ../backend.log 2>&1 &

sleep 3

# 验证
echo -e "\n${YELLOW}4. 验证状态...${NC}"
STATUS=$(curl -s localhost:8000/api/health 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('trading_mode', 'unknown'))" 2>/dev/null || echo "error")

if [ "$STATUS" = "live" ]; then
    echo -e "${GREEN}✅ 已切换到LIVE实盘交易模式!${NC}"
else
    echo -e "${RED}❌ 切换失败,当前模式: $STATUS${NC}"
    echo "请检查日志: tail -f backend.log"
fi

echo ""
echo -e "${GREEN}=============================================="
echo -e "🔴 GO2SE 已切换到LIVE实盘交易模式"
echo -e "==============================================${NC}"
echo ""
echo "监控命令:"
echo "  tail -f /root/.openclaw/workspace/GO2SE_PLATFORM/backend.log"
echo "  curl localhost:8000/api/health"
echo ""
echo "切换回dry_run:"
echo "  cp backend/.env.dry_run_backup.* backend/.env"
echo "  $0 \$1 \$2 dry_run"
