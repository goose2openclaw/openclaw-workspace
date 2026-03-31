#!/bin/bash
#============================================================================---
# 🐳 GO2SE Docker 部署脚本
#============================================================================---

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

IMAGE_NAME="go2se/backend"
CONTAINER_NAME="go2se-backend"

log_info() { echo -e "${YELLOW}[INFO]${NC} $1"; }
log_ok()   { echo -e "${GREEN}[OK]${NC} $1"; }
log_err()  { echo -e "${RED}[ERROR]${NC} $1"; }

# 构建镜像
build() {
    log_info "构建Docker镜像..."
    
    cd /root/.openclaw/workspace/GO2SE_PLATFORM/backend
    
    docker build -t "$IMAGE_NAME:latest" .
    
    log_ok "镜像构建完成: $IMAGE_NAME:latest"
}

# 运行容器
run() {
    local mode=${1:-"dry_run"}
    
    log_info "启动容器 (模式: $mode)..."
    
    # 停止旧容器
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    docker rm "$CONTAINER_NAME" 2>/dev/null || true
    
    # 运行新容器
    docker run -d \
        --name "$CONTAINER_NAME" \
        --restart unless-stopped \
        -p 8000:8000 \
        -e TRADING_MODE="$mode" \
        -e BINANCE_API_KEY="${BINANCE_API_KEY:-}" \
        -e BINANCE_SECRET_KEY="${BINANCE_SECRET_KEY:-}" \
        -v /root/.openclaw/workspace/GO2SE_PLATFORM:/app \
        "$IMAGE_NAME:latest"
    
    sleep 3
    
    if curl -s localhost:8004/api/health | grep -q "healthy"; then
        log_ok "容器启动成功"
    else
        log_err "容器启动失败"
        docker logs "$CONTAINER_NAME"
        exit 1
    fi
}

# 停止
stop() {
    log_info "停止容器..."
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    docker rm "$CONTAINER_NAME" 2>/dev/null || true
    log_ok "容器已停止"
}

# 状态
status() {
    if docker ps | grep -q "$CONTAINER_NAME"; then
        echo -e "${GREEN}✅ 容器运行中${NC}"
        docker logs --tail 20 "$CONTAINER_NAME" 2>&1 | tail -10
    else
        echo -e "${RED}❌ 容器未运行${NC}"
    fi
}

# 主程序
case "${1:-help}" in
    build) build ;;
    run)   run "${2:-dry_run}" ;;
    stop)  stop ;;
    restart)
        stop
        run "${2:-dry_run}"
        ;;
    status) status ;;
    *)
        echo "用法: $0 {build|run|stop|restart|status} [模式]"
        echo ""
        echo "示例:"
        echo "  $0 build"
        echo "  $0 run dry_run"
        echo "  $0 run live"
        echo "  $0 restart"
        echo "  $0 status"
        ;;
esac
