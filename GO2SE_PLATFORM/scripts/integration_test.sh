#!/bin/bash
# 🪿 GO2SE 整体集成测试 v2
# ============================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;36m'
NC='\033[0m'

PASS=0
FAIL=0

pass() { echo -e "${GREEN}✅ $1${NC}"; ((PASS++)); }
fail() { echo -e "${RED}❌ $1${NC}"; ((FAIL++)); }
info() { echo -e "${BLUE}ℹ️ $1${NC}"; }
warn() { echo -e "${YELLOW}⚠️ $1${NC}"; }

echo "============================================================"
echo "🪿 GO2SE 整体集成测试"
echo "============================================================"
echo ""

# 测试1: 后端健康检查
info "测试1: 后端服务健康检查"
RESULT=$(curl -s --max-time 5 http://localhost:8004/api/ping 2>/dev/null)
if echo "$RESULT" | grep -q "pong"; then
    pass "后端API响应正常"
else
    fail "后端API无响应"
fi

# 测试2: 市场数据API
info "测试2: 市场数据API"
RESULT=$(curl -s --max-time 5 http://localhost:8004/api/market 2>/dev/null)
MARKET_COUNT=$(echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('data',[])))" 2>/dev/null)
if [ -n "$MARKET_COUNT" ] && [ "$MARKET_COUNT" -gt 0 ]; then
    pass "市场数据: ${MARKET_COUNT}个交易对"
else
    fail "市场数据API失败"
fi

# 测试3: 历史API
info "测试3: 历史记录API"
RESULT=$(curl -s --max-time 5 "http://localhost:8004/api/history?page=1&page_size=5" 2>/dev/null)
HISTORY_COUNT=$(echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('total',0))" 2>/dev/null)
if [ -n "$HISTORY_COUNT" ] && [ "$HISTORY_COUNT" -gt 0 ]; then
    pass "历史记录: ${HISTORY_COUNT}条"
else
    fail "历史记录API失败"
fi

# 测试4: 分析API
info "测试4: 数据分析API"
RESULT=$(curl -s --max-time 5 http://localhost:8004/api/analytics/overview 2>/dev/null)
ANALYTICS=$(echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('total_profit',0))" 2>/dev/null)
if [ -n "$ANALYTICS" ] && [ "$ANALYTICS" != "0" ]; then
    pass "数据分析: profit=\$$ANALYTICS"
else
    fail "数据分析API失败"
fi

# 测试5: 性能API
info "测试5: 性能API"
RESULT=$(curl -s --max-time 5 http://localhost:8004/api/performance 2>/dev/null)
PERF=$(echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('strategy','?'))" 2>/dev/null)
if [ -n "$PERF" ] && [ "$PERF" != "?" ]; then
    pass "性能API: strategy=$PERF"
else
    fail "性能API失败"
fi

# 测试6: v6a UI文件检查
info "测试6: v6a UI L5/L6文件"
L56_FILES=0
for f in brain-dual seven-tools trading-modules engineer-module; do
    if [ -f "/root/.openclaw/workspace/GO2SE_PLATFORM/versions/v6a/js/${f}.js" ]; then
        L56_FILES=$((L56_FILES + 1))
    fi
done
if [ "$L56_FILES" -eq 4 ]; then
    pass "v6a L5/L6模块: 4/4文件存在"
else
    fail "v6a L5/L6模块: 仅${L56_FILES}/4文件存在"
fi

# 测试7: L5/L6代码检查
info "测试7: L5/L6渲染函数"
L56_FUNCS=0
for f in brain-dual seven-tools trading-modules engineer-module; do
    FILE="/root/.openclaw/workspace/GO2SE_PLATFORM/versions/v6a/js/${f}.js"
    if grep -qE "state\.level === 5|state\.level === 6|renderLevel5|renderLevel6|getLevel5|getLevel6" "$FILE" 2>/dev/null; then
        L56_FUNCS=$((L56_FUNCS + 1))
    fi
done
if [ "$L56_FUNCS" -eq 4 ]; then
    pass "L5/L6渲染函数: 4/4模块"
else
    fail "L5/L6渲染函数: 仅${L56_FUNCS}/4模块"
fi

# 测试8: 后端进程检查
info "测试8: 后端进程"
if pgrep -f "uvicorn.*8004" > /dev/null 2>&1; then
    pass "后端进程运行中"
else
    fail "后端进程未运行"
fi

# 测试9: 资源状态
info "测试9: 系统资源"
MEM_AVAIL=$(free -m | awk 'NR==2{print $7')
DISK_USE=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
if [ -n "$MEM_AVAIL" ] && [ "$MEM_AVAIL" -gt 1000 ]; then
    pass "内存: ${MEM_AVAIL}MB 可用"
else
    warn "内存: ${MEM_AVAIL}MB 可用 (偏低)"
fi
if [ -n "$DISK_USE" ] && [ "$DISK_USE" -lt 90 ]; then
    pass "磁盘: ${DISK_USE}% 使用"
else
    warn "磁盘: ${DISK_USE}% 使用 (偏高)"
fi

# 测试10: v6a index.html
info "测试10: v6a主页面"
if grep -q "l56_helper.js" /root/.openclaw/workspace/GO2SE_PLATFORM/versions/v6a/index.html 2>/dev/null; then
    pass "v6a主页面: L56 helper引入"
else
    fail "v6a主页面: 缺少L56 helper"
fi

# 测试11: L5/L6测试脚本
info "测试11: L5/L6测试脚本"
if [ -f "/root/.openclaw/workspace/GO2SE_PLATFORM/versions/v6a/test_l56_autonomous.js" ]; then
    pass "L5/L6测试脚本存在"
else
    fail "L5/L6测试脚本不存在"
fi

# 测试12: 四系统脚本
info "测试12: 四系统协作脚本"
if [ -f "/root/.openclaw/workspace/GO2SE_PLATFORM/scripts/quartet_orchestrator.py" ]; then
    pass "四系统脚本: quartet_orchestrator.py"
else
    fail "四系统脚本: quartet_orchestrator.py 不存在"
fi

if [ -f "/root/.openclaw/workspace/GO2SE_PLATFORM/scripts/resource_monitor.py" ]; then
    pass "资源监控脚本: resource_monitor.py"
else
    fail "资源监控脚本: resource_monitor.py 不存在"
fi

# 测试13: L56 Helper
info "测试13: L56 Helper"
if [ -f "/root/.openclaw/workspace/GO2SE_PLATFORM/versions/v6a/js/l56_helper.js" ]; then
    pass "L56 Helper JS存在"
else
    fail "L56 Helper JS不存在"
fi

# 测试14: 历史分析路由
info "测试14: 历史分析API路由"
if [ -f "/root/.openclaw/workspace/GO2SE_PLATFORM/backend/app/api/routes_history_analytics.py" ]; then
    pass "历史分析路由文件存在"
else
    fail "历史分析路由文件不存在"
fi

# 总结
echo ""
echo "============================================================"
echo "📊 测试总结"
echo "============================================================"
echo -e "通过: ${GREEN}${PASS}${NC}"
echo -e "失败: ${RED}${FAIL}${NC}"
TOTAL=$((PASS + FAIL))
if [ "$TOTAL" -gt 0 ]; then
    SCORE=$((PASS * 100 / TOTAL))
    echo -e "得分: ${SCORE}/100"
fi
echo ""

if [ "$FAIL" -eq 0 ]; then
    echo -e "${GREEN}🎉 所有测试通过!${NC}"
elif [ "$FAIL" -le 2 ]; then
    echo -e "${YELLOW}⚠️ 有少量失败项${NC}"
else
    echo -e "${RED}❌ 有较多失败项需要修复${NC}"
fi

exit $FAIL
