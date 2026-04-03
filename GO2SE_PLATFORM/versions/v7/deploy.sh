#!/bin/bash
# GO2SE v7 — gstack集成部署脚本
# 
# 用法: bash deploy.sh [选项]
#   --check      仅检查依赖
#   --install    安装gstack依赖
#   --backend    仅部署后端
#   --frontend   仅部署前端
#   --full       完整部署 (默认)

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GSTACK_ROOT="$HOME/.claude/skills/gstack"

# === 检查依赖 ===
check_dependencies() {
    log_info "检查依赖..."
    
    # 检查gstack
    if [ -d "$GSTACK_ROOT" ]; then
        log_info "✅ gstack已安装: $GSTACK_ROOT"
    else
        log_warn "⚠️ gstack未安装"
        log_info "安装: git clone https://github.com/garrytan/gstack.git $GSTACK_ROOT"
    fi
    
    # 检查Bun
    if command -v bun &> /dev/null; then
        BUN_VERSION=$(bun --version)
        log_info "✅ Bun已安装: v$BUN_VERSION"
    else
        log_error "❌ Bun未安装 (gstack需要)"
        log_info "安装: curl -fsSL https://bun.sh/install | bash"
        exit 1
    fi
    
    # 检查Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        log_info "✅ Python已安装: $PYTHON_VERSION"
    else
        log_error "❌ Python3未安装"
        exit 1
    fi
    
    # 检查Flask
    if python3 -c "import flask" 2>/dev/null; then
        log_info "✅ Flask已安装"
    else
        log_warn "⚠️ Flask未安装"
        log_info "安装: pip install flask gunicorn"
    fi
}

# === 安装gstack ===
install_gstack() {
    log_info "安装gstack..."
    
    if [ -d "$GSTACK_ROOT" ]; then
        log_info "gstack已存在，更新中..."
        cd "$GSTACK_ROOT" && git pull
    else
        git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git "$GSTACK_ROOT"
    fi
    
    # 安装Bun依赖
    if [ -f "$GSTACK_ROOT/package.json" ]; then
        cd "$GSTACK_ROOT" && bun install
    fi
    
    # 运行setup
    if [ -f "$GSTACK_ROOT/setup" ]; then
        cd "$GSTACK_ROOT" && chmod +x setup && ./setup
    fi
    
    log_info "✅ gstack安装完成"
}

# === 部署后端 ===
deploy_backend() {
    log_info "部署后端..."
    
    # 复制gstack集成模块
    cp "$SCRIPT_DIR/gstack-integration/gstack_manager.py" "$SCRIPT_DIR/backend/"
    cp "$SCRIPT_DIR/routes_gstack.py" "$SCRIPT_DIR/backend/"
    
    # 确保__init__.py存在
    touch "$SCRIPT_DIR/backend/__init__.py"
    
    # 注册blueprint (需要修改main app)
    log_info "请在backend/app.py中添加:"
    log_info "  from routes_gstack import gstack_bp"
    log_info "  app.register_blueprint(gstack_bp)"
    
    log_info "✅ 后端部署完成"
}

# === 部署前端 ===
deploy_frontend() {
    log_info "部署前端..."
    
    # 复制gstack面板组件
    cp "$SCRIPT_DIR/frontend/gstack-panel.html" "$SCRIPT_DIR/frontend/"
    
    # 添加到index.html引用 (需要手动)
    log_info "请在frontend/templates/index.html中添加:"
    log_info '  <div id="gstack-panel-container"></div>'
    log_info '  <script src="gstack-panel.html"></script>'
    
    log_info "✅ 前端部署完成"
}

# === 完整部署 ===
deploy_full() {
    log_info "🚀 开始完整部署 GO2SE v7..."
    
    check_dependencies
    deploy_backend
    deployfrontend
    
    log_info ""
    log_info "========================================"
    log_info "🎉 GO2SE v7 部署完成!"
    log_info "========================================"
    log_info ""
    log_info "新增功能:"
    log_info "  🪿 29个gstack专家命令"
    log_info "  📊 3大自动化流水线"
    log_info "  🔧 完整UI侧边栏"
    log_info ""
    log_info "API端点:"
    log_info "  GET  /api/gstack          - 列出所有命令"
    log_info "  POST /api/gstack/run      - 运行命令"
    log_info "  POST /api/gstack/strategy-flow - 策略开发流"
    log_info ""
    log_info "下一步:"
    log_info "  1. 重启backend服务"
    log_info "  2. 刷新前端页面"
    log_info "  3. 测试 /office-hours 命令"
}

# === 主逻辑 ===
MODE="${1:-full}"

case "$MODE" in
    --check)
        check_dependencies
        ;;
    --install)
        install_gstack
        ;;
    --backend)
        deploy_backend
        ;;
    --frontend)
        deploy_frontend
        ;;
    --full)
        deploy_full
        ;;
    *)
        echo "用法: $0 [--check|--install|--backend|--frontend|--full]"
        exit 1
        ;;
esac
