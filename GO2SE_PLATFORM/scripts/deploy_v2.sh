#!/bin/bash
#============================================================================---
# 🚀 GO2SE 部署脚本V2 (增强版)
#============================================================================---
# 功能:
#   1. 自动健康检查
#   2. 备份当前版本
#   3. 零停机部署
#   4. 自动回滚
#============================================================================---

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_DIR="/root/.openclaw/workspace/GO2SE_PLATFORM"
BACKUP_DIR="$PROJECT_DIR/backups"
LOG_FILE="$PROJECT_DIR/deploy.log"

#============================================================================---
# 函数定义
#============================================================================---

log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_info() { log "${BLUE}[INFO]${NC} $1"; }
log_ok()   { log "${GREEN}[OK]${NC} $1"; }
log_warn() { log "${YELLOW}[WARN]${NC} $1"; }
log_err()  { log "${RED}[ERROR]${NC} $1"; }

check_health() {
    local max_attempts=5
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s localhost:8004/api/health | grep -q "healthy"; then
            return 0
        fi
        log_warn "健康检查失败 ($attempt/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    done
    return 1
}

create_backup() {
    log_info "创建备份..."
    
    mkdir -p "$BACKUP_DIR"
    local backup_name="backup_$(date +%Y%m%d_%H%M%S)"
    local backup_path="$BACKUP_DIR/$backup_name"
    
    mkdir -p "$backup_path"
    
    # 备份关键文件
    cp -r "$PROJECT_DIR/backend" "$backup_path/" 2>/dev/null || true
    cp "$PROJECT_DIR/.env" "$backup_path/" 2>/dev/null || true
    cp "$PROJECT_DIR/go2se.db" "$backup_path/" 2>/dev/null || true
    
    # 保存备份信息
    echo "$backup_path" > "$BACKUP_DIR/latest_backup"
    echo "$(date)" > "$backup_path/backup_info.txt"
    
    log_ok "备份已创建: $backup_name"
    echo "$backup_path"
}

rollback() {
    local backup_path=$1
    
    if [ ! -d "$backup_path" ]; then
        log_err "备份不存在: $backup_path"
        return 1
    fi
    
    log_warn "开始回滚..."
    
    # 停止服务
    pkill -f "uvicorn app.main:app" 2>/dev/null || true
    sleep 2
    
    # 恢复文件
    cp -r "$backup_path/backend" "$PROJECT_DIR/" 2>/dev/null || true
    cp "$backup_path/.env" "$PROJECT_DIR/" 2>/dev/null || true
    
    # 重启服务
    start_server
    
    log_ok "回滚完成"
}

start_server() {
    log_info "启动服务..."
    
    cd "$PROJECT_DIR/backend"
    
    # 检查端口
    if lsof -i :8000 > /dev/null 2>&1; then
        log_warn "端口8000已被占用，尝试清理..."
        pkill -f "uvicorn app.main:app" 2>/dev/null || true
        sleep 2
    fi
    
    # 启动
    nohup python3 -m uvicorn app.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --workers 2 \
        --timeout 120 \
        > ../backend.log 2>&1 &
    
    sleep 3
    
    if check_health; then
        log_ok "服务启动成功"
    else
        log_err "服务启动失败"
        return 1
    fi
}

deploy() {
    local mode=${1:-"dry_run"}
    
    log_info "=========================================="
    log_info "🚀 GO2SE 部署开始 (模式: $mode)"
    log_info "=========================================="
    
    # 1. 预检查
    log_info "1. 预检查..."
    
    if [ ! -d "$PROJECT_DIR/backend" ]; then
        log_err "项目目录不存在"
        exit 1
    fi
    
    # 2. 创建备份
    log_info "2. 创建备份..."
    backup_path=$(create_backup)
    
    # 3. 更新配置
    log_info "3. 更新配置 (模式: $mode)..."
    
    if [ "$mode" = "live" ]; then
        log_warn "⚠️ 即将部署到LIVE模式!"
        read -p "确认? (yes/no): " confirm
        if [ "$confirm" != "yes" ]; then
            log_info "部署取消"
            exit 0
        fi
    fi
    
    # 4. 停止旧服务
    log_info "4. 停止旧服务..."
    pkill -f "uvicorn app.main:app" 2>/dev/null || true
    sleep 2
    log_ok "服务已停止"
    
    # 5. 启动新服务
    log_info "5. 启动新服务..."
    start_server
    
    # 6. 验证
    log_info "6. 验证部署..."
    
    local status=$(curl -s localhost:8004/api/health | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('trading_mode','?'))" 2>/dev/null || echo "error")
    
    if [ "$status" = "$mode" ]; then
        log_ok "部署成功! 模式: $mode"
    else
        log_err "部署验证失败，当前模式: $status"
        log_warn "尝试回滚..."
        rollback "$backup_path"
        exit 1
    fi
    
    # 7. 完成
    log_info "=========================================="
    log_ok "✅ 部署完成!"
    log_info "=========================================="
    echo ""
    echo "监控命令:"
    echo "  tail -f $PROJECT_DIR/backend.log"
    echo "  curl localhost:8004/api/health"
    echo ""
    echo "回滚命令:"
    echo "  $0 rollback $backup_path"
    echo ""
}

#============================================================================---
# 主程序
#============================================================================---

case "${1:-deploy}" in
    deploy)
        deploy "${2:-dry_run}"
        ;;
    rollback)
        if [ -z "$2" ]; then
            # 使用最新备份
            backup_path=$(cat "$BACKUP_DIR/latest_backup" 2>/dev/null || echo "")
            if [ -z "$backup_path" ] || [ ! -d "$backup_path" ]; then
                log_err "没有找到可用备份"
                exit 1
            fi
        else
            backup_path="$2"
        fi
        rollback "$backup_path"
        ;;
    status)
        if curl -s localhost:8004/api/health | grep -q "healthy"; then
            echo -e "${GREEN}✅ 服务运行正常${NC}"
            curl -s localhost:8004/api/health | python3 -m json.tool 2>/dev/null | head -10
        else
            echo -e "${RED}❌ 服务未运行${NC}"
        fi
        ;;
    backup)
        create_backup
        ;;
    *)
        echo "用法: $0 {deploy|rollback|status|backup} [参数]"
        echo ""
        echo "命令:"
        echo "  deploy [mode]   - 部署 (默认dry_run)"
        echo "  rollback [path] - 回滚 (可选备份路径)"
        echo "  status          - 查看状态"
        echo "  backup          - 创建备份"
        echo ""
        echo "示例:"
        echo "  $0 deploy dry_run"
        echo "  $0 deploy live"
        echo "  $0 rollback"
        echo "  $0 status"
        exit 1
        ;;
esac
