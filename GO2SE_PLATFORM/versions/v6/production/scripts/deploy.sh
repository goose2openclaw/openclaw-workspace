#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# 🪿 GO2SE 一键部署脚本
# 支持: Ubuntu 20.04+ / Debian 11+
# ═══════════════════════════════════════════════════════════════════════════════

set -e

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 检查root
if [[ "$EUID" -ne 0 ]]; then
    log_error "请使用 root 用户运行"
    exit 1
fi

log_info "🪿 GO2SE 部署脚本启动..."

# ═══════════════════════════════════════════════════════════════════════════════
# 1. 安装Docker
# ═══════════════════════════════════════════════════════════════════════════════
if ! command -v docker &> /dev/null; then
    log_info "安装Docker..."
    apt-get update
    apt-get install -y ca-certificates curl gnupg lsb-release
    
    mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/$(. /etc/os-release && echo $ID)/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/$(. /etc/os-release && echo $ID) $(lsb_release -cs) stable" | \
        tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    systemctl enable docker
    systemctl start docker
    log_info "Docker 安装完成"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# 2. 创建目录
# ═══════════════════════════════════════════════════════════════════════════════
log_info "创建目录..."
mkdir -p /opt/go2se/{logs,data,config,strategies}
cd /opt/go2se

# ═══════════════════════════════════════════════════════════════════════════════
# 3. 配置环境变量
# ═══════════════════════════════════════════════════════════════════════════════
if [ ! -f .env ]; then
    log_info "创建环境变量配置..."
    cp /root/.openclaw/workspace/go2se_production/.env.example .env
    
    # 生成随机密码
    POSTGRES_PASSWORD=$(openssl rand -base64 24)
    sed -i "s/^POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$POSTGRES_PASSWORD/" .env
    
    log_warn "请编辑 .env 填入币安API密钥!"
    log_warn "文件位置: /opt/go2se/.env"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# 4. 启动服务
# ═══════════════════════════════════════════════════════════════════════════════
log_info "启动Docker Compose..."

# 拉取代码(如果有)
if [ -d /root/.openclaw/workspace/go2se_production ]; then
    cp -r /root/.openclaw/workspace/go2se_production/* /opt/go2se/
fi

# 启动
docker compose up -d --build

# ═══════════════════════════════════════════════════════════════════════════════
# 5. 等待服务启动
# ═══════════════════════════════════════════════════════════════════════════════
log_info "等待服务启动..."
sleep 30

# 检查状态
docker compose ps

# ═══════════════════════════════════════════════════════════════════════════════
# 6. 健康检查
# ═══════════════════════════════════════════════════════════════════════════════
log_info "执行健康检查..."
docker exec go2se_trading_engine python /app/scripts/health_check.py || true

# ═══════════════════════════════════════════════════════════════════════════════
# 完成
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo "══════════════════════════════════════════════════════════════════════════════"
echo "🪿 GO2SE 部署完成!"
echo "══════════════════════════════════════════════════════════════════════════════"
echo ""
echo "📊 服务地址:"
echo "   - 交易引擎: http://localhost:8000"
echo "   - Grafana:   http://localhost:3000"
echo "   - Prometheus: http://localhost:9090"
echo ""
echo "📝 重要配置:"
echo "   - 配置文件: /opt/go2se/.env"
echo "   - 日志目录: /opt/go2se/logs"
echo "   - 数据目录: /opt/go2se/data"
echo ""
echo "🔧 常用命令:"
echo "   - 查看状态: docker compose ps"
echo "   - 查看日志: docker compose logs -f"
echo "   - 重启服务: docker compose restart"
echo "   - 停止服务: docker compose down"
echo ""
echo "⚠️  首次使用请务必:"
echo "   1. 编辑 /opt/go2se/.env 填入币安API密钥"
echo "   2. 设置 TRADING_MODE=dry_run (模拟) 或 live (实盘)"
echo "   3. 运行 docker compose restart"
echo ""
