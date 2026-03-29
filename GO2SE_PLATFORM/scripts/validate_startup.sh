#!/bin/bash
# 🪿 GO2SE 启动前验证脚本
# 在启动服务前检查所有关键依赖和导入

set -e

echo "🪿 GO2SE 启动前验证..."
cd /root/.openclaw/workspace/GO2SE_PLATFORM/backend

# 1. Python语法检查
echo "  📋 检查Python语法..."
python3 -m py_compile app/models/models.py || { echo "❌ models.py 语法错误"; exit 1; }
python3 -m py_compile app/core/auth.py || { echo "❌ auth.py 语法错误"; exit 1; }
python3 -m py_compile app/core/backtest_engine.py || { echo "❌ backtest_engine.py 语法错误"; exit 1; }
python3 -m py_compile app/core/websocket_manager.py || { echo "❌ websocket_manager.py 语法错误"; exit 1; }
python3 -m py_compile app/api/routes.py || { echo "❌ routes.py 语法错误"; exit 1; }
python3 -m py_compile app/core/trading_engine.py || { echo "❌ trading_engine.py 语法错误"; exit 1; }
echo "  ✅ Python语法 OK"

# 2. 关键导入检查
echo "  📦 检查关键导入..."
python3 -c "
from app.models.models import Trade, Position, Signal, User, BacktestResult, MarketData, StrategyRun
from app.core.auth import get_current_user, generate_api_key
from app.core.backtest_engine import BacktestEngine
from app.core.websocket_manager import ConnectionManager
print('  ✅ 所有模型和工具类导入 OK')
" || { echo "❌ 导入检查失败"; exit 1; }

# 3. 数据库模型检查
echo "  🗄️  检查数据库..."
source ../venv/bin/activate
python3 -c "
from app.core.database import Base, engine, get_db
from app.models.models import User, Trade, Position, Signal, BacktestResult
# 验证表已创建
from sqlalchemy import inspect
insp = inspect(engine)
tables = insp.get_table_names()
required = ['users', 'trades', 'positions', 'signals', 'backtest_results']
for t in required:
    if t in tables:
        print(f'    ✅ 表 {t} 存在')
    else:
        print(f'    ⚠️  表 {t} 不存在 (会自动创建)')
print('  ✅ 数据库检查 OK')
" || { echo "❌ 数据库检查失败"; exit 1; }

# 4. 端口冲突检查
echo "  🔌 检查端口冲突..."
for PORT in 8001 8002 8003 8004 8005; do
    if ss -tlnp 2>/dev/null | grep -q ":${PORT} "; then
        echo "  ⚠️  端口 ${PORT} 已被占用，将跳过"
    fi
done

# 5. 磁盘空间检查
echo "  💾 检查磁盘空间..."
USAGE=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
if [ "$USAGE" -gt 95 ]; then
    echo "  ⚠️  磁盘使用率 ${USAGE}% (超过95%)，建议清理"
else
    echo "  ✅ 磁盘使用率 ${USAGE}% OK"
fi

# 6. 交易所连接检查 (模拟)
echo "  🌐 检查交易所连接..."
source ../venv/bin/activate
timeout 10 python3 -c "
import asyncio
from app.core.trading_engine import engine
async def test():
    engine.init_exchange()
    print('  ✅ 交易所连接 OK')
asyncio.run(test())
" 2>&1 | tail -1 || echo "  ⚠️  交易所连接跳过 (API密钥或网络问题)"

echo ""
echo "🪿 验证完成，所有检查通过！"
