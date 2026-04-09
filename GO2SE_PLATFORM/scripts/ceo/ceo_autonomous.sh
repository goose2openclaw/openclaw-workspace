#!/bin/bash
#===============================================================================
# 🪿 GO2SE CEO 自主迭代主脚本
#===============================================================================
# 功能:
#   1. CEO自动评估状态
#   2. 检查是否需要迭代
#   3. 运行基准评测
#   4. 自动触发迭代 (如需要)
#   5. 生成报告
#
# 使用:
#   ./ceo_autonomous.sh          # 评估状态
#   ./ceo_autonomous.sh --auto   # 自动迭代模式
#   ./ceo_autonomous.sh --benchmark  # 运行基准评测
#===============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CEO_DIR="$(dirname "$SCRIPT_DIR")"
PLATFORM_DIR="$(dirname "$CEO_DIR")"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# CEO配置文件
CEO_CONFIG="$PLATFORM_DIR/.ceo_config.json"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo "==============================================================================="
echo "🪿 GO2SE CEO 自主迭代系统"
echo "==============================================================================="

# 解析参数
MODE="${1:-status}"

cd "$PLATFORM_DIR"

# ─────────────────────────────────────────────────────────────────────────────
# 1. CEO状态评估
# ─────────────────────────────────────────────────────────────────────────────
ceo_status() {
    echo ""
    echo -e "${BLUE}[1/4] CEO状态评估${NC}"
    echo "─────────────────────────────────────"
    
    # 运行CEO自主迭代检查
    python3 "$SCRIPT_DIR/auto_iteration.py" --status 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    scores = data.get('scores', {})
    
    echo ''
    for key, info in scores.items():
        score = info.get('value', 0)
        threshold = info.get('threshold', 0)
        status = info.get('status', 'unknown')
        
        if status == 'ok':
            icon='✅'
        else:
            icon='⚠️'
        
        echo f'  {icon} {key}: {score:.1f} (阈值: {threshold})'
    
    echo ''
    echo '  迭代统计:'
    stats = data.get('iteration_stats', {})
    echo "    总迭代: ${stats.get('total', 0)}"
    echo "    今日迭代: ${stats.get('recent_5', 0)}"
    echo "    平均改进: ${stats.get('avg_improvement', 0):+.1f}"
    
    if stats.get('last_iteration'):
        echo "    上次迭代: ${stats.get('last_iteration')}"
except:
    echo '  无法获取状态'
"
}

# ─────────────────────────────────────────────────────────────────────────────
# 2. 基准评测
# ─────────────────────────────────────────────────────────────────────────────
ceo_benchmark() {
    echo ""
    echo -e "${BLUE}[2/4] 基准评测${NC}"
    echo "─────────────────────────────────────"
    
    python3 "$SCRIPT_DIR/benchmark.py" --run 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print('')
    print(f'  综合评分: {data.get(\"overall_score\", 0):.1f}')
    print(f'  百分位: {data.get(\"percentile\", 0)}%')
    
    print('')
    print('  行业对比:')
    comp = data.get('industry_comparison', {}).get('comparison', {})
    for key, info in comp.items():
        if isinstance(info, dict):
            go2se = info.get('go2se_estimate', info.get('go2se', 'N/A'))
            avg = info.get('industry_avg', 'N/A')
            verdict = info.get('verdict', 'unknown')
            print(f'    {key}: GO2SE={go2se}, 行业={avg} [{verdict}]')
    
    recs = data.get('recommendations', [])
    if recs:
        print('')
        print(f'  建议: {len(recs)}条')
        for r in recs[:3]:
            print(f'    - {r.get(\"action\", \"\")}')
except Exception as e:
    print(f'  评测失败: {e}')
"
}

# ─────────────────────────────────────────────────────────────────────────────
# 3. 生成建议
# ─────────────────────────────────────────────────────────────────────────────
ceo_recommend() {
    echo ""
    echo -e "${BLUE}[3/4] 迭代建议${NC}"
    echo "─────────────────────────────────────"
    
    python3 "$SCRIPT_DIR/auto_iteration.py" --recommend 2>/dev/null || echo "  无建议"
}

# ─────────────────────────────────────────────────────────────────────────────
# 4. 触发迭代
# ─────────────────────────────────────────────────────────────────────────────
ceo_trigger() {
    echo ""
    echo -e "${BLUE}[4/4] 迭代执行${NC}"
    echo "─────────────────────────────────────"
    
    # 检查是否应该触发
    should_trigger=$(python3 "$SCRIPT_DIR/auto_iteration.py" --auto 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data.get('should_trigger'):
        print('yes')
        print(f\"  原因: {data.get('trigger_reason', '')}\")
    else:
        print('no')
        print(f\"  原因: {data.get('trigger_reason', '')}\")
except:
    print('error')
" 2>&1)
    
    should=$(echo "$should_trigger" | head -1)
    reason=$(echo "$should_trigger" | tail -+2 | head -1)
    
    if [ "$should" = "yes" ]; then
        echo -e "  ${GREEN}触发迭代${NC}"
        echo "  原因: $reason"
        
        # 执行迭代
        bash scripts/go2se_v7_iteration.sh 2>&1 | tail -20
        
    elif [ "$should" = "no" ]; then
        echo -e "  ${YELLOW}暂不触发${NC}"
        echo "  原因: $reason"
    else
        echo -e "  ${RED}检查失败${NC}"
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
# 主流程
# ─────────────────────────────────────────────────────────────────────────────
case "$MODE" in
    --status|-s)
        ceo_status
        ;;
    --benchmark|-b)
        ceo_benchmark
        ;;
    --recommend|-r)
        ceo_recommend
        ;;
    --trigger|-t)
        ceo_trigger
        ;;
    --auto|-a)
        echo -e "${CYAN}自动迭代模式${NC}"
        echo ""
        ceo_status
        ceo_benchmark
        ceo_recommend
        ceo_trigger
        ;;
    --full|-f)
        echo -e "${CYAN}完整迭代+基准评测${NC}"
        echo ""
        # 运行完整迭代
        bash scripts/go2se_v7_iteration.sh
        # 运行基准评测
        ceo_benchmark
        ;;
    *)
        echo "用法: $0 [选项]"
        echo ""
        echo "选项:"
        echo "  --status, -s      CEO状态评估"
        echo "  --benchmark, -b   运行基准评测"
        echo "  --recommend, -r  生成迭代建议"
        echo "  --trigger, -t     触发迭代"
        echo "  --auto, -a        自动迭代模式 (完整流程)"
        echo "  --full, -f        完整迭代+基准"
        echo ""
        echo "示例:"
        echo "  $0 --status       # 查看状态"
        echo "  $0 --auto         # 自动迭代"
        ;;
esac

echo ""
echo "==============================================================================="
