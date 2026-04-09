# GO2SE + DeerFlow 集成指南

## 概述

DeerFlow (ByteDance开源SuperAgent框架) 与 GO2SE 平台的深度集成，实现多Agent协作执行五条平行工作线。

## 架构

```
┌─────────────────────────────────────────────────────────┐
│                     DeerFlow UI                          │
│                   (localhost:3000)                      │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│              DeerFlow Backend                            │
│    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐     │
│    │  Research   │ │   Coder     │ │   Analyst   │     │
│    │   Agent    │ │   Agent     │ │   Agent     │     │
│    └─────────────┘ └─────────────┘ └─────────────┘     │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                   GO2SE 平台                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │  交易    │ │  风控    │ │  信号    │ │  钱包    │   │
│  │  策略    │ │  系统    │ │  聚合    │ │  优化    │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
└─────────────────────────────────────────────────────────┘
```

## 五条平行工作线

### ① 系统健康
DeerFlow Agent → 检查GO2SE服务 → 自动告警

### ② 监控回复
DeerFlow Agent → OpenClaw → 实时响应

### ③ 调度准备
DeerFlow Agent → Cron调度 → 资源分配

### ④ 执行工作
DeerFlow Multi-Agent → GO2SE API → 交易/风控

### ⑤ 社交学习
DeerFlow Research Agent → 市场情报 → 知识积累

## 快速开始

### 1. 启动DeerFlow
```bash
cd /root/.openclaw/workspace/skills/deer-flow
docker compose up -d
```

### 2. 访问DeerFlow UI
```
http://localhost:3000
```

### 3. 创建GO2SE任务
在DeerFlow中输入:
```
执行GO2SE五条工作线:
1. 检查系统健康
2. 分析市场信号
3. 优化钱包分配
4. 生成交易报告
```

### 4. DeerFlow自动编排
- Research Agent 收集情报
- Coder Agent 调用API
- Analyst Agent 分析数据
- 汇总报告

## DeerFlow Skills

| 技能 | 用途 |
|------|------|
| go2se-ceo | CEO管理系统 |
| go2se-workflow | 五条工作线工作流 |
| deep-research | 深度研究 |
| data-analysis | 数据分析 |

## 配置

### DeerFlow config.yaml
```yaml
models:
  - name: doubao-seed
    model: doubao-seed-2-250615
    api_key: $VOLCENGINE_API_KEY

skills:
  - path: ../skills/public/go2se-ceo
  - path: ../skills/public/go2se-workflow
```

## API端点

| 服务 | 端点 | 功能 |
|------|------|------|
| GO2SE | /api/health | 健康检查 |
| GO2SE | /api/signals/aggregated | 聚合信号 |
| GO2SE | /api/wallet/optimize | 钱包优化 |
| GO2SE | /api/risk/trailing | 风控 |
| OpenClaw | localhost:18789 | Gateway |
