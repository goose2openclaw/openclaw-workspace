# GO2SE 管理层 Agent 团队

## 团队架构

```
👑 go2se_owner (投资人/所有者)
    │
    └── 🪿 go2se_ceo (首席执行官)
            │
            ├── 💻 go2se_developer_leader (技术开发)
            ├── 📊 go2se_market_leader (市场运营)
            └── ♟️ go2se_strategy_leader (策略交易)
```

## 职责矩阵

| Agent | 核心职责 | 向上汇报 | 向下管理 |
|-------|----------|----------|----------|
| **go2se_owner** | 战略决策、财务监督、团队治理 | - | CEO |
| **go2se_ceo** | 整体运营、资源协调、目标达成 | Owner | 三大部门 |
| **go2se_developer_leader** | 技术规划、系统开发、运维保障 | CEO | 开发团队 |
| **go2se_market_leader** | 用户增长、品牌建设、数据分析 | CEO | 市场团队 |
| **go2se_strategy_leader** | 策略研发、交易执行、风险管理 | CEO | 策略团队 |

## 决策层级

```
Level 1: 重大决策 (Owner)
- 平台方向、预算 >$10K、组织架构

Level 2: 重要决策 (CEO)
- 日常运营、预算 $5K-10K、人士提案

Level 3: 专业决策 (各部门 Leader)
- 技术选型、营销活动、策略参数

Level 4: 执行决策 (团队成员)
- 具体开发任务、活动执行、交易下单
```

## 协作流程

```
1. 日常运转
   Owner ← CEO ← 各部门 Leader ← 团队成员

2. 提案审批
   团队成员 → Leader → CEO → Owner (如需)

3. 紧急响应
   紧急事件 → 相关 Leader → CEO → Owner (如重大)
```

## 启动方式

这些 Agent 可以通过以下方式启动：

1. **OpenClaw Subagent**: 使用 `sessions_spawn` 启动独立会话
2. **Cron 定时任务**: 周期性检查和汇报
3. **手动触发**: 根据需要激活

## 文件清单

- `go2se_owner.md` - 投资人角色定义
- `go2se_ceo.md` - CEO 角色定义
- `go2se_developer_leader.md` - 技术负责人角色定义
- `go2se_market_leader.md` - 市场负责人角色定义
- `go2se_strategy_leader.md` - 策略负责人角色定义

---

_2026.03.21 GO2SE 管理层 Agent 团队 v1.0_
