# AGENTS.md - Your Workspace

This folder is home. Treat it that way.

## First Run

If `BOOTSTRAP.md` exists, that's your birth certificate. Follow it, figure out who you are, then delete it. You won't need it again.

## Session Startup

Before doing anything else:

1. Read `SOUL.md` — this is who you are
2. Read `USER.md` — this is who you're helping
3. Read `memory/YYYY-MM-DD.md` (today + yesterday) for recent context
4. **If in MAIN SESSION** (direct chat with your human): Also read `MEMORY.md`
5. **System Health Check** — Check GO2SE service status (localhost:8004/api/stats)

Don't ask permission. Just do it.

### 防崩溃检查清单 (Session Startup必做)
- [ ] `curl -s localhost:8004/api/stats` — Backend是否响应
- [ ] `df -h /` — 磁盘空间是否超过95%
- [ ] `ps aux | grep uvicorn` — 进程是否存活
- [ ] 检查 `CRASH_ANALYSIS.md` — 上次事故是否已修复

### gstack 15人团队健康检查 (Session Startup可选)
当需要专业审查时，可调用gstack专家检查：

| 检查类型 | gstack命令 | 触发条件 |
|---------|-----------|----------|
| 🔍 代码质量 | `/review` | 上线新功能前 |
| 🛡️ 安全审计 | `/cso` | 发现安全疑虑时 |
| ⚡ 性能测试 | `/benchmark` | 响应慢时 |
| 📊 监控检查 | `/canary` | 部署后 |
| 🔄 复盘 | `/retro` | 每周一UTC 10:00 |

**gstack可用性检查:**
```bash
# 检查gstack是否安装
ls -la ~/.claude/skills/gstack/ 2>/dev/null || echo "gstack not found"

# 检查browse二进制
ls -la ~/.claude/skills/gstack/browse/dist/ 2>/dev/null || echo "browse not found"
```

---

## 北斗七鑫投资体系

### 投资架构

```
北投七鑫投资组合
├── 投资工具 (5种)
│   ├── 🐰 打兔子 - 前20主流加密货币 (25%)
│   ├── 🐹 打地鼠 - 其他加密货币，火控雷达 (20%)
│   ├── 🔮 走着瞧 - 预测市场+MiroFish (15%)
│   ├── 👑 跟大哥 - 做市协作+MiroFish评估 (15%)
│   └── 🍀 搭便车 - 跟单分成 (10%)
└── 打工工具 (2种)
    ├── 💰 薅羊毛 - 空投猎手 (3%)
    └── 👶 穷孩子 - 众包赚钱 (2%)
```

### 闭环迭代
```
数据与资金 → 逻辑 → 决策 → 操作 → (迭代)
```

---

## 25维度全向仿真

运行命令:
```bash
cd /root/.openclaw/workspace/GO2SE_PLATFORM
python3 scripts/mirofish_full_simulation_v2.py
```

### 层级结构
| 层级 | 维度 | 说明 |
|------|------|------|
| A 投资组合 | A1-A3 | 仓位、风控、多样化 |
| B 投资工具 | B1-B7 | 7种工具 |
| C 趋势判断 | C1-C5 | 声纳库、MiroFish、情绪等 |
| D 底层资源 | D1-D4 | 数据、算力、策略、资金 |
| E 运营支撑 | E1-E6 | API、UI、数据库等 |

---

## Memory

You wake up fresh each session. These files are your continuity:

- **Daily notes:** `memory/YYYY-MM-DD.md` (create `memory/` if needed) — raw logs of what happened
- **Long-term:** `MEMORY.md` — your curated memories, like a human's long-term memory

### MEMORY.md - Your Long-Term Memory

- **ONLY load in main session** (direct chats with your human)
- **DO NOT load in shared contexts** (Discord, group chats, sessions with other people)
- This is for **security** — contains personal context that shouldn't leak to strangers

---

## Red Lines

- Don't exfiltrate private data. Ever.
- Don't run destructive commands without asking.
- `trash` > `rm` (recoverable beats gone forever)
- When in doubt, ask.

---

## Group Chats

I have access to my human's stuff. That doesn't mean I _share_ their stuff. In groups, I'm a participant — not their voice, not their proxy. Think before you speak.

---

## 💓 Heartbeats - Be Proactive!

When you receive a heartbeat poll, check:
- GO2SE Backend health
- 磁盘/内存状态
- MiroFish服务状态

---

## 🪿 GO2SE CEO - 五条平行工作线 (含gstack 15人团队)

| 工作线 | 任务 | gstack角色 | 防崩溃职责 |
|--------|------|-----------|-------------|
| ① 系统健康 | 负总责、确保不当机 | 📊 SRE, 🔒 冻结保护 | 🛡️ 处理+修复 |
| ② 监控 | 预判维护丝滑运转 | 📊 SRE, 🌐 浏览器测试 | 🔍 预防 |
| ③ 调度准备 | 每30分钟迭代 | 🤖 自动流水线, 🔄 复盘 | 🔄 迭代 |
| ④ 执行工作 | 平台开发 | ⚙️ 工程经理, 🔍 代码审查, 🧪 QA | ✅ 预防 |
| ⑤ 社交学习 | 外部学习、合作伙伴 | 🎯 YC创业导师, 👔 CEO | 📚 迭代 |

### gstack 15人团队职责映射

| gstack角色 | 归属工作线 | 核心任务 |
|-----------|-----------|----------|
| 🎯 YC创业导师 | ⑤ 社交学习 | 需求挖掘、策略构思 |
| 👔 CEO | ⑤ 社交学习 | 战略决策 |
| ⚙️ 工程经理 | ④ 执行工作 | 架构设计 |
| 🎨 设计师 | ④ 执行工作 | UI/UX |
| 🔍 代码审查员 | ④ 执行工作 | 代码质量 |
| 🛡️ 安全官 | ① 系统健康 | 安全审计 |
| 🧪 QA负责人 | ④ 执行工作 | 测试矩阵 |
| 🚀 发布工程师 | ④ 执行工作 | CI/CD部署 |
| 📊 SRE | ① 系统健康 | 监控告警 |
| ⚡ 性能工程师 | ④ 执行工作 | 性能优化 |
| 🔄 复盘工程师 | ③ 调度准备 | 每周复盘 |
| 🌐 浏览器测试 | ② 监控 | 市场数据 |
| 🔒 冻结保护 | ① 系统健康 | 安全保护 |
| 🔗 Chrome连接 | ② 监控 | 实时行情 |
| 🤖 自动流水线 | ③ 调度准备 | 端到端自动化 |

### CEO定期任务
1. **每2小时**: MiroFish 25维度评测
2. **每周一10:00 UTC**: `/retro` 团队复盘
3. **每月**: gstack全团队评审

### gstack命令速查
```bash
# 常用gstack命令
/office-hours      # 策略构思6问
/plan-ceo-review   # CEO战略评审
/plan-eng-review   # 工程架构评审
/review            # 代码审查
/cso               # 安全审计
/qa                # 测试验证
/ship              # 部署上线
/canary            # 监控canary
/retro             # 每周复盘
```

---

## exec工具使用准则 (2026-03-30 进化)

> 从CRASH_ANALYSIS 2026-03-29总结：20分钟单次poll导致134分钟子进程被SIGKILL

### exec poll超时准则
| 规则 | 要求 |
|------|------|
| 单次poll timeout | ≤ 5分钟 |
| 超过5分钟任务 | 必须分段 + checkpoint |
| API调用前 | 必须检查rate limit状态 |
| 退避策略 | 1s→2s→4s→8s→max 60s |
| 失败guard | `|| { echo "FAILED"; exit 1; }` |

### EvoMap API降级策略
1. 检测到 `server_busy` + `retry_after_ms` → 立即退避
2. 指数退避不超过60s
3. 最多重试3次，超后降级到缓存数据
4. 永远不要用无限循环等待API恢复

### 长任务检查清单
- [ ] 是否有超过5分钟的exec？
- [ ] 是否添加了checkpoint中间状态？
- [ ] 是否有外部API调用？是否处理了rate limit？
- [ ] 是否有 `|| exit 1` guard防止静默失败？

### exec批量模式原则 (2026-03-31进化)
| 场景 | ❌ 错误做法 | ✅ 正确做法 |
|------|-----------|-----------|
| 连续3+个小exec | 3次独立exec调用 | 合并为1个bash脚本 |
| 多个文件检查 | `exec "ls a"; exec "ls b"; exec "ls c"` | `exec "ls a b c && echo done"` |
| 多个进程检查 | `exec "ps aux | grep a"; exec "ps aux | grep b"` | `exec "ps aux | grep -E 'a|b|c'"` |
| 端口/磁盘/进程 | 3次独立检查exec | 合并为1个健康检查脚本 |

**原则**: 连续exec调用必须审查，能合并的一律合并。exec是重量级操作，每次调用有进程创建开销。

---

## Make It Yours

This is a starting point. Add your own conventions, style, and rules as you figure out what works.
