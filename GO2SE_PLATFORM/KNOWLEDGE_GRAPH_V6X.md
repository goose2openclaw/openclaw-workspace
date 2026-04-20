# 🪿 GO2SE v6* 系列知识图谱
## 时间范围: 2026-03-14 → 2026-04-20 | 覆盖4月1日-18日工作内容

---

## 📐 一、版本演进树

```
v6.0 (03-14)
  ├── v6a (04-09) ← 北斗七鑫+OpenAI Agents
  │     ├── v6i (04-20) ← 自主多空切换引擎
  │     └── 端口 8016/8001
  ├── v7.0 (03-29) ← MiroFish 25维集成
  │     ├── v7.5 (03-31)
  │     ├── v8 (03-31) ← 端口统一8004
  │     ├── v9 (03-31) ← 双端口优化
  │     └── v10 (03-31) ← MiroFish 90.6/100
  └── (当前) v6a + v6i 双引擎
```

---

## 📊 二、April 1-18 逐日工作图谱

### 4月9日 🟡 v6a 创建
```
【事件】创建 v6a (基于v13架构，拒绝v7的React)
【位置】GO2SE_PLATFORM/versions/v6a | 端口 8016
【修复】
  ✅ selectTab() 添加 renderPanel()
  ✅ selectTool() 添加 renderPanel()
  ✅ 语法错误修复
【提交】1e5031aa, fa69624f
【增强】API_BASE→8004, 7工具→真实信号, 实时流Tab
【提交】12c72bd4
```

### 4月11日 🔵 四系统集成
```
【四系统协作】
  🔵 Hermes墨丘利 → 市场数据 + 情绪分析 (EXTREMELY_BULLISH)
  🟢 MiroFish冥河 → 仿真验证 (94.7/100, 25/25通过)
  🟣 gstack工程队 → 29技能工程审查
  🪿 OpenClaw编排 → 任务编排

【做空引擎激活】
  ├── binance_futures.py — Binance期货做空
  ├── routes_short_selling.py — 8个做空API端点
  └── recommendation_engine.py — 强化推荐V2

【技能生态】
  194技能 | 145可用 | 49缺依赖
  新增: gstack-review, self-improving*, agent-team-orchestration

【Cron优化】
  资源监控 30m→60m | 健康检查 15m→30m | 协作 15m→30m
```

### 4月12日 🟢 推荐中心 + 十大策略
```
【推荐中心 V2】
  ├── RecommendationHub.tsx (3 Tab: 五大组合/十策略/对比分析)
  ├── 决策等式: Final = Σ(wi × Si × Ci) / Σ(wi × Ci)
  └── 权重调节滑块 + 回测+仿真按钮

【十大量化策略】
  ├── AI量化选币 (ML)       胜55% 收益50% 夏普1.9
  ├── 动量突破 (趋势)       胜45% 收益40% 夏普1.8
  ├── MACD交叉 (趋势)       胜48% 收益35% 夏普1.6
  ├── 网格交易 (均值回归)   胜68% 收益25% 夏普1.5
  ├── RSI均值回归           胜58% 收益20% 夏普1.4
  ├── 布林带               胜55% 收益18% 夏普1.3
  ├── 统计套利 (中性)      胜65% 收益18% 夏普2.0
  ├── DCA定投 (趋势)        胜62% 收益15% 夏普1.2
  ├── 做市商 (中性)         胜72% 收益15% 夏普2.2
  └── 套利 (中性)           胜78% 收益12% 夏普2.5

【第二记忆系统 GBrain】
  956 pages | 2506 chunks | Postgres+pgvector
  导入: workspace/* 859页 | GO2SE_PLATFORM/* 77页

【ClawPanel Pro v5.4.2】
  端口 19527 | Go+React | 20+通道 | PID 13964

【Harness配置】
  Codex CLI 0.118.0 | mode=auto | PI fallback
```

### 4月13日 🔴 v8 前端优化
```
【React Router架构】
  /tools /trends /signals /portfolio /earn /recommend /settings

【组件提取】
  Dashboard✅ Tools✅ Trends✅ Signals✅ Portfolio✅ Settings✅
  types.ts (共享类型)✅

【修复】
  $85,000硬编码 → 真实portfolio数据

【构建】211 KB (dist/assets/index-*.js)

【MiroFish评分】94.7/100 (25/25通过)
```

### 4月20日 ⚫ v6i 自主迭代引擎 (凌晨)
```
【新架构】OpenAI Agents SDK 0.14.2
【端口】8001 (独立于v6a的8000)
【7专家智能体】
  rabbit🐰 mole🐹 oracle🔮 leader👑
  hitchhiker🍀 wool🧵 crowd👶

【自主多空切换引擎】
  普通模式: 仅做多 confidence>65
  专家模式: long/short/hold 自动切换
  4档杠杆: 保守2x|中等3x|激进5x|专家10x

【风控熔断】
  日内损失≥15% → 自动停止交易
  每日益差≤5% → 仓位减半

【MiroFish 25维迭代计划】
  A1仓位 60→80 | B1打兔子 40.8→75 | D2算力 59.9→80
  目标: 97.2/100 (v6i.3周目标)

【自主循环引擎 v2】
  每30分钟: 观测→分析→决策→执行→学习→优化
  评分系统: 收益35+回撤25+模式20+置信度15+信号5
  迭代#1-18: 68→78分 | 连续17次HOLD
```

---

## 🧠 三、v6* 版本核心对比矩阵

| 维度 | v6.0 | v6a | v7.0 | v8-v10 | v6i (最新) |
|------|------|-----|------|--------|-----------|
| **时间** | 03-14 | 04-09 | 03-29 | 03-31 | 04-20 |
| **前端** | 10页 | 静态34JS | React | React Router | FastAPI |
| **后端** | Flask | FastAPI | FastAPI | FastAPI | OpenAI Agents |
| **端口** | 3002/5000 | 8016 | 8004 | 8004 | 8001 |
| **做空** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **MiroFish** | ❌ | ❌ | 87.7/100 | 90.6/100 | 91.8/100 |
| **自主切换** | ❌ | ❌ | ❌ | ❌ | ✅ |
| **多智能体** | 7工具 | 14Models | 20+Core | 20+Core | 7 Agents |
| **十大策略** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **推荐中心** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **GBrain** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **ClawPanel** | ❌ | ❌ | ❌ | ✅ | ✅ |

---

## 🔗 四、关键依赖关系图 (API调用链)

```
用户请求
  ↓
v6i (端口8001) ← OpenAI Agents SDK
  ├── rabbit🐰 → 趋势发现
  ├── mole🐹 → 波动套利
  ├── oracle🔮 → 预测市场
  ├── leader👑 → 做市协调
  ├── hitchhiker🍀 → 跟单
  └── crowd👶 → 众包
  ↓ 自主多空切换引擎
  ├── confidence≥85 → LONG 5x
  ├── confidence 65-84 → HOLD
  └── bear regime → SHORT 3x
  ↓
v6a (端口8000) ← FastAPI多策略
  ├── signal_push.py → Telegram告警
  ├── trading.py → Binance执行
  ├── backtest_engine → 30天回测
  └── risk_manager → 熔断控制
  ↓
Binance API ←→ 真实市场
  ↓
v6a 前端 (端口5173) ← React实时展示
```

---

## 📈 四、April 1-18 核心指标变化

| 指标 | 4月1日 | 4月9日 | 4月11日 | 4月12日 | 4月13日 | 4月20日 |
|------|--------|--------|---------|---------|---------|---------|
| 技能数 | ~145 | ~145 | 194 | 194 | 194 | 225 |
| MiroFish | — | — | 94.7 | 94.7 | 94.7 | 91.8 |
| 版本 | v7? | v6a | v6a | v6a | v8 | v6i |
| 策略数 | 7工具 | 7工具 | 7+做空 | 10量化 | 10量化 | 10+AI |
| 记忆层 | MEMORY.md | MEMORY.md | GBrain | GBrain | GBrain | GBrain+分层 |
| 面板 | — | — | — | ClawPanel | ClawPanel | ClawPanel |

---

## 🎯 五、v6i vs v6a 功能差异

| 功能 | v6a (8000) | v6i (8001) |
|------|------------|------------|
| **架构** | FastAPI多策略 | OpenAI Agents SDK |
| **多空切换** | 手动AI判断 | 全自动+专家模式 |
| **杠杆** | 固定档位 | 4档动态(2x-10x) |
| **风控** | 规则熔断 | 动态仓位+熔断 |
| **自主循环** | 外部调度 | 内置30min迭代 |
| **学习能力** | 无 | 历史评分+参数优化 |
| **信号来源** | 20+Core引擎 | 7专业Agent协作 |
| **适用场景** | 批量回测/分析 | 实时自主交易 |

---

## 🗺️ 六、April核心成就地图

```
4月1-8日
  ⚪ 无记录 (工作空白期)

4月9日 🟡
  └→ v6a复活 + Tab修复 + 提交Git

4月11日 🔵
  ├→ 四系统协作激活 (Hermes+MiroFish+gstack+OpenClaw)
  ├→ 做空引擎上线 (Binance Futures)
  ├→ 技能库194个
  └→ Cron间隔优化

4月12日 🟢
  ├→ 推荐中心V2 + 决策等式
  ├→ 十大量化策略集成
  ├→ GBrain 956页语义记忆
  ├→ ClawPanel Pro v5.4.2
  └→ Harness Codex配置

4月13日 🔴
  ├→ v8 React Router重构
  ├→ 7组件提取
  └→ $85,000硬编码修复

4月14-19日
  ⚪ 无记录

4月20日 ⚫
  ├→ v6i OpenAI Agents全新架构
  ├→ 自主多空切换引擎
  ├→ MiroFish 25维迭代计划
  ├→ 技能库→225个
  └→ 持续自主迭代#1-18 (68→78分)
```

---

*生成时间: 2026-04-20 04:39 UTC*
*数据来源: memory/2026-04-*.md + v*_iteration_*.md + versions/v6*/
