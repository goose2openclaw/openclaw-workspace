#!/bin/bash
# GO2SE Startup Validation Script
# 部署前验证脚本

set -e

WORKSPACE="/root/.openclaw/workspace/GO2SE_PLATFORM"
ERRORS=0

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ${RED}ERROR: $1${NC}" >&2
    ((ERRORS++))
}

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 1. 语法检查
log "检查Python语法..."
for file in $WORKSPACE/backend/app/*.py; do
    if [ -f "$file" ]; then
        python3 -m py_compile "$file" 2>/dev/null || error "语法错误: $file"
    fi
done

# 2. 导入检查
log "检查模块导入..."
cd $WORKSPACE/backend
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from app.main import app
    print('Main app imported successfully')
except Exception as e:
    print(f'Import error: {e}')
    sys.exit(1)
" || error "模块导入失败"

# 3. 端口检查
log "检查端口占用..."
for port in 8004 8005 8006; do
    if netstat -tuln 2>/dev/null | grep -q ":$port "; then
        echo "警告: 端口 $port 已被占用"
    fi
done

# 4. 磁盘检查
log "检查磁盘空间..."
usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$usage" -gt 95 ]; then
    error "磁盘空间不足: ${usage}%"
else
    log "磁盘空间: ${usage}%"
fi

# 5. 依赖检查
log "检查Python依赖..."
pip3 list 2>/dev/null | grep -E "fastapi|uvicorn|requests" > /dev/null || error "缺少必要依赖"

# 6. 配置检查
log "检查配置文件..."
if [ -f "$WORKSPACE/backend/config.py" ]; then
    python3 -c "
import config
print('Config loaded successfully')
" || error "配置文件加载失败"
fi

# 7. 数据库检查
log "检查数据库..."
if [ -f "$WORKSPACE/backend/app.db" ]; then
    python3 -c "
import sqlite3
conn = sqlite3.connect('app.db')
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\"')
tables = cursor.fetchall()
print(f'Database tables: {[t[0] for t in tables]}')
conn.close()
" 2>/dev/null || error "数据库检查失败"
fi

# 总结
log "========== 验证结果 =========="
if [ $ERRORS -eq 0 ]; then
    log "${GREEN}所有检查通过 ✓${NC}"
    exit 0
else
    log "${RED}发现 $ERRORS 个错误${NC}"
    exit 1
fi
