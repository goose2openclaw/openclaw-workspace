# 崩溃复盘报告 — 2026.03.29

## 事故概述

| 项目 | 内容 |
|------|------|
| **时间** | 2026-03-29 15:38 UTC |
| **类型** | Sub-agent exec SIGKILL (非服务崩溃) |
| **影响范围** | evomap-publish / xiami-dataloader 子进程 |
| **实际服务** | ✅ 无影响 (8004/8005 正常) |

---

## 事件经过

1. **13:29 UTC** — 用户启动3个EvoMap任务并行执行
2. **13:29-15:38 UTC** — 子Agent持续运行:
   - `evomap-task1/2/3`: 持续调用EvoMap API，受rate limit制约
   - `evomap-publish`: 长轮询等待API限流恢复 (52秒等待)
   - `xiami-dataloader`: 扫描代码库分析N+1问题
3. **15:38 UTC** — "lucky-ke" exec进程收到SIGKILL (进程超时)
4. **15:45 UTC** — Cron Guardian检查: Backend正常，仅磁盘95%警告

---

## 根因分析

### 直接原因
- **Sub-agent exec进程超时**: 长运行任务(134分钟)的poll循环导致session超时被SIGKILL
- **EvoMap API限流**: rate_limit窗口60秒，频繁触发 `retry_after_ms`

### 深层原因
| 问题 | 描述 |
|------|------|
| **同步等待模式** | 使用 `process.poll(timeout=1200000ms)` 同步等待，无法异步处理 |
| **超时预算失控** | 单次poll 20分钟，但rate limit需要频繁重试 |
| **子Agent生命周期** | 没有为长时间运行任务设置正确的超时机制 |
| **EvoMap API认知不足** | 未预判rate limit策略，高频调用导致被限流 |

---

## 做对的事情 ✅

1. **真实服务零中断** — GO2SE Backend :8004/:8005全程健康
2. **Cron Guardian有效** — 15:45检查确认服务正常
3. **任务设计合理** — 3任务并行执行，充分利用算力
4. **失败隔离** — 子Agent失败不影响主会话

---

## 做错的事情 ❌

1. **同步poll超时失控** — 单次poll 20分钟，共运行134分钟
2. **未处理rate limit** — EvoMap API限流策略未提前规避
3. **长任务无checkpoint** — 未设计中间状态保存，断点无法续传
4. **未设置exec超时上限** — 进程可以无限期运行直到被kill

---

## 改进点

| 改进 | 具体措施 | 优先级 |
|------|---------|--------|
| **修复poll超时** | poll timeout设上限≤5分钟，超时后切换策略 | P0 |
| **增加退避重试** | 指数退避: 1s→2s→4s→8s→max 60s | P0 |
| **添加checkpoint** | 每轮迭代保存状态，支持断点续传 | P1 |
| **预判API限制** | 调用前检查 rate limit 窗口，避免触发 | P1 |
| **子Agent超时** | 设置合理的 runTimeoutSeconds，避免无限运行 | P1 |

---

## 纳入防崩溃机制

将以下检查项加入 `validate_startup.sh`:
```bash
# 检查子Agent超时配置
if grep -q "poll.*1200000" $WORKSPACE/**/*.py 2>/dev/null; then
    echo "⚠️ 发现过长poll timeout配置"
fi
```

---

## 教训总结

> **长任务必须设计退避策略和断点机制，不能依赖无限轮询等待。**

EvoMap API的rate limit是已知的，但代码中未做退避处理。这是human error，代码没有按设计运行。

---

*复盘时间: 2026-03-29 16:00 UTC*

---

## 补充：子Agent超时问题 (2026-03-30)

### 新发现
- 子Agent session `8e750feb` 和 `b8a4e079` 状态显示 aborted 和 401 auth error
- 根本原因：子Agent运行时遇到401认证错误，导致任务无法完成

### 根因
1. 子Agent运行时API认证失败
2. 长任务未设置正确超时机制
3. EvoMap API rate limit导致频繁重试

### 修复建议
1. **P0**: 为所有sessions_spawn添加runTimeoutSeconds参数（≤300s）
2. **P0**: 实现指数退避策略处理API限流
3. **P1**: 添加API认证重试机制
4. **P1**: 实现checkpoint支持断点续传

