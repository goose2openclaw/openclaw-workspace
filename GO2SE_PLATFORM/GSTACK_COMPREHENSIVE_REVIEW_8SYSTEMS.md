# GSTACK COMPREHENSIVE DEEP REVIEW - 8系统全面评测
===============================================
时间: 2026-04-20 23:05 GMT+8
评测方法: 代码路径分析 + API测试 + 逻辑验证 + 市场模拟

═══════════════════════════════════════════════
第一部分: 修复验证 (gstack review v3 findings)
═══════════════════════════════════════════════

修复前问题:
  ❌ v6i: mi=None (MiroFish未集成)
  ❌ vv6: regime=bear误判 (fear_greed=45应=neutral)
  ❌ v15: platform_mi=1.0688超上限(未cap)

修复后验证:
  ✅ v6i: mi=0.7125 (MiroFish Platform真实值)
  ✅ vv6: regime=neutral (fear_greed=45,trend=neutral)
  ✅ v15: platform_mi=0.8621 (<1.35 cap applied)

═══════════════════════════════════════════════
第二部分: 各系统深度评测
═══════════════════════════════════════════════

───────────────────────────────────────────────
系统1: v7 Backend (port 8000)
───────────────────────────────────────────────
状态: ✅ 运行中
功能: GO2SE主后端, v7 API, 市场数据源
关键端点:
  GET /api/v7/market/summary → fear_greed=45, trend=neutral
  GET /api/v7/portfolio/v7
  GET /api/v7/status
  GET /api/v7/strategies

评测结果:
  • 市场数据API: ✅ 正常 (fear_greed=45, trend=neutral)
  • v6i/vv6依赖此端点进行regime检测
  • 建议: 添加实时fear_greed抓取(当前固定45)

───────────────────────────────────────────────
系统2: v6i - Hermes引擎 (port 8001)
───────────────────────────────────────────────
状态: ✅ 运行中 (expert模式)
版本: v6i-openai-agents
模式: expert (空头+多头自动切换)

关键发现:
  ✅ MiroFish集成: mi=0.7125 (修复后,修复前=None)
  ✅ regime检测: neutral (fear_greed=45,trend=neutral)
  ✅ 专家模式: direction=long, leverage=2, position_pct=30
  ⚠️  cooldow机制: 5分钟(已修复)
  ⚠️  RSI固定50.0 (未从市场获取真实RSI)

评测结果:
  • 健康状态: ✅
  • MiroFish: ✅ 已集成(修复完成)
  • regime检测: ✅ 正常(修复完成)
  • 风险控制: ✅ 熔断机制,日损失限制15%
  • 改进空间: RSI应从交易所获取实时值

───────────────────────────────────────────────
系统3: vv6 - Lobster引擎 (port 8006)
───────────────────────────────────────────────
状态: ✅ 运行中 (normal模式)
版本: vv6-openai-agents
模式: normal (仅做多)

关键发现:
  ✅ MiroFish集成: mi=0.7125, source=vv6
  ✅ regime检测: neutral (修复后,修复前=bear误判)
  ✅ fear_greed获取: 从v7 backend真实API (修复完成)
  ✅ MiroFish Platform回调: 集成完整

评测结果:
  • 健康状态: ✅
  • MiroFish: ✅ 完全集成(含fear_greed真实值)
  • regime检测: ✅ 正确(修复完成)
  • 改进空间: 考虑添加expert模式支持

───────────────────────────────────────────────
系统4: Brain Coordinator (port 8010)
───────────────────────────────────────────────
状态: ✅ 运行中
版本: v15.2 (含auto-poll)
模式: AUTO

关键发现:
  ✅ Auto-poll: 已配置vv6+v15自动轮询
  ✅ 三方仲裁: /arbitration/decide端点正常
  ✅ 手动触发: /auto-poll/trigger 测试成功
  ⚠️  Auto-poll enabled: false (未启动后台轮询)
  ⚠️  信号池陈旧: vv6=22:45, v15=22:45 (20分钟前)

评测结果:
  • 仲裁逻辑: ✅ 置信度×Mi加权
  • Auto-poll架构: ✅ 就绪(可启动)
  • 改进空间: 启动auto-poll后台任务

───────────────────────────────────────────────
系统5: v15 Quad-Brain (port 8015)
───────────────────────────────────────────────
状态: ✅ 运行中
版本: v15.0.0
引擎: quad-brain × v6i-switch × MiroFish

关键发现:
  ✅ Decision Engine v3: 四脑自适应加权
  ✅ MiroFish融合: fused_mi=0.7948 (0.4×platform+0.6×local)
  ✅ platform_mi cap: 0.8621<1.35 (修复后,修复前=1.0688)
  ✅ local Mi: 0.75 (正确计算)
  ✅ gstack v3修复: 全部5项完成
  ✅ 1000-Agent: 聚合信号已集成

评测结果:
  • Mi计算: ✅ 正确(含cap)
  • 四脑权重: ✅ 自适应
  • 决策输出: ✅ direction=LONG, leverage=2
  • 改进空间: 四脑信号未见明显分歧

───────────────────────────────────────────────
系统6: MiroFish Platform Engine (port 8020)
───────────────────────────────────────────────
状态: ✅ 运行中
版本: v15.2 (1000-Agent)
功能: 25维仲裁 + 群体智能

关键发现:
  ✅ 1000-Agent池: 1000个虚拟Agent, avg_accuracy=0.7381
  ✅ 7类Agent: trend_chaser(200), mean_reversion(200), breakout(150),
              event_driven(150), macro(100), onchain(100), sentiment(100)
  ✅ 仲裁API: /arbitration/push + /arbitration/decide 正常
  ✅ 学习API: /agents/learn 交易记录→维度更新
  ✅ Mi计算: fear_greed=45→Mi=0.8621
  ⚠️  Auto-arbitration: enabled=false (未启动)
  ⚠️  维度评分: 多为默认值75.0 (学习未触发)

评测结果:
  • 1000-Agent: ✅ 池健康,投票正常
  • 仲裁机制: ✅ 双方信号加权
  • 学习系统: ✅ 架构完整,等待交易触发
  • 改进空间: 启动auto-arbitration,积累真实交易

───────────────────────────────────────────────
系统7: Strategy Optimizer (port 8021)
───────────────────────────────────────────────
状态: ✅ 运行中
版本: v1.0.0
功能: regime-conditional权重 + Kelly Criterion

关键发现:
  ✅ regime权重: bear→mole↑22.16%, rabbit↓16.86%
  ✅ 权重调整: 7个agent动态调整
  ✅ Kelly分配: 组合权重计算正常
  ✅ API响应: /weights/adjusted 正常

评测结果:
  • 权重逻辑: ✅ bear regime正确调整
  • Kelly: ✅ 组合再分配正确
  • 改进空间: bull regime权重(待验证)

───────────────────────────────────────────────
系统8: v13 (port 8004)
───────────────────────────────────────────────
状态: ✅ 运行中
备注: 7鑫系统,非标准health端点

═══════════════════════════════════════════════
第三部分: 问题汇总与优先级
═══════════════════════════════════════════════

P0 - 严重 (已全部修复):
  ✅ v6i mi=None → MiroFish集成
  ✅ vv6 regime=bear误判 → v7 API获取
  ✅ v15 platform_mi超1.35 → 添加cap

P1 - 重要:
  🔄 Auto-poll未启动 (Brain Coordinator)
  🔄 Auto-arbitration未启动 (MiroFish Platform)
  📋 v6i RSI固定50.0 (应从交易所获取)
  📋 vv6 normal模式 (Hermes应支持expert)
  📋 维度评分多为75.0 (缺少真实市场数据)

P2 - 优化:
  📋 v7 fear_greed固定45 (应实时抓取)
  📋 1000-Agent avg_accuracy=0.7381 (可提升)
  📋 四脑adaptive_weights为空(未触发)

═══════════════════════════════════════════════
第四部分: 迭代建议
═══════════════════════════════════════════════

v15.3 目标:
  1. 启动Brain Coordinator auto-poll后台任务
  2. 启动MiroFish auto-arbitration
  3. v6i添加实时RSI获取(Binance API)
  4. v7 backend添加实时fear_greed抓取
  5. 维度评分从75.0默认值→真实市场数据驱动

v15.4 目标:
  1. 1000-Agent真实市场数据输入
  2. 交易学习闭环: WIN/LOSS → 维度评分更新
  3. Kelly Criterion组合再平衡自动化

