#!/bin/bash
# 🕐 Cron Anchor重调度器 - 错开同步触发
# 解决30分钟周期同步触发问题
# 用法: bash scripts/cron_rescheduler.sh

set -e

echo ""
echo "============================================================"
echo "🕐 GO2SE Cron Anchor 重调度器"
echo "============================================================"

# 当前Anchor冲突分析
echo ""
echo "📋 当前Anchor冲突:"
echo "  - GO2SE-CEO-管理:      anchor = 1774711243282ms (03:00 UTC)"
echo "  - GO2SE平台迭代:       anchor = 1774711243170ms (03:00 UTC) ← 同步!"
echo "  - 市场情报收集:        anchor = 1774711243268ms (03:00 UTC) ← 同步!"
echo ""
echo "⚠️  每30分钟的 :00 和 :30 时，三个任务同时触发"

# 新的Anchor方案
echo ""
echo "🔄 推荐Anchor重分配方案:"
echo ""
echo "┌──────────────────────────────────────────────────────────┐"
echo "│ Cron Job                  │ 当前Anchor │ 新Anchor │ 效果  │"
echo "├──────────────────────────────────────────────────────────┤"
echo "│ GO2SE-CEO-管理           │ :00        │ :00      │ 保持  │"
echo "│ GO2SE平台迭代            │ :00        │ :15      │ 错开15min │"
echo "│ 市场情报收集              │ :00        │ :30      │ 错开30min │"
echo "│ Capability-Evolver        │ :28        │ :45      │ 错开17min │"
echo "│ OpenClaw每日备份         │ 03:00 UTC  │ 04:30 UTC│ 错开1.5h  │"
echo "└──────────────────────────────────────────────────────────┘"

echo ""
echo "⏰ 重调度后的时间线 (每30分钟周期):"
echo ""
echo "  :00  → GO2SE-CEO-管理 (main会话)"
echo "  :15  → GO2SE平台迭代 (isolated)  ← 原:00, 错开15min"
echo "  :30  → 市场情报收集 (isolated)   ← 原:00, 错开30min"
echo "  :45  → Capability-Evolver      ← 原:28, 错开17min"
echo "  04:30 UTC → OpenClaw每日备份     ← 原:03:00, 错开1.5h"

echo ""
echo "📊 改进效果:"
echo "  原: 3个任务同时 :00触发  → 资源竞争🔴"
echo "  新: 每15分钟1个任务      → 资源分散🟢"

echo ""
echo "⚠️  执行重调度需要以下openclaw CLI命令:"
echo ""
echo "  # 1. GO2SE平台迭代 - 错开15分钟"
echo "  openclaw crons update <GO2SE平台迭代-JOB-ID> \"
echo "    --anchor-offset 900000  # +15分钟"
echo ""
echo "  # 2. 市场情报收集 - 错开30分钟"
echo "  openclaw crons update <市场情报收集-JOB-ID> \"
echo "    --anchor-offset 1800000  # +30分钟"
echo ""
echo "  # 3. Capability-Evolver - 错开17分钟"
echo "  openclaw crons update <Capability-Evolver-JOB-ID> \"
echo "    --anchor-offset 1020000  # +17分钟"
echo ""
echo "  # 4. OpenClaw每日备份 - 改为04:30 UTC"
echo "  openclaw crons update <OpenClaw每日备份-JOB-ID> \"
echo "    --cron '30 4 * * *'"

echo ""
echo "============================================================"
echo "💡 Tip: 也可将GO2SE平台迭代频率从30min改为60min"
echo "        这样每天只运行12次而非24次，减少超时风险"
echo "============================================================"
echo ""
