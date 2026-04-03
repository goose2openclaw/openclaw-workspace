# OMX (Oh My Codex) 源码分析 & GO2SE 集成报告

**生成时间:** 2026-04-03
**来源:** https://github.com/Yeachan-Heo/oh-my-codex v0.11.12

---

## 一、项目结构概览

```
oh-my-codex/
├── src/                    # TypeScript 核心源码
│   ├── team/              # 多Agent团队编排 (22个文件)
│   │   ├── orchestrator.ts    # 状态机: plan→prd→exec→verify→fix
│   │   ├── role-router.ts     # 角色路由 (启发式分配)
│   │   ├── state.ts          # 团队状态管理
│   │   ├── tmux-session.ts   # tmux 会话管理
│   │   ├── worktree.ts       # git worktree 隔离
│   │   ├── allocation-policy.ts  # Worker 分配策略
│   │   ├── phase-controller.ts   # 阶段控制器
│   │   └── ...
│   ├── ralph/             # 持久完成循环 (Ralph = persistent loop owner)
│   │   ├── contract.ts        # 状态机: starting→executing→verifying→fixing→complete
│   │   └── persistence.ts     # 持久化状态到文件系统
│   ├── ralplan/           # 计划审批工作流
│   │   └── ...
│   ├── openclaw/          # OpenClaw 集成 (4个文件)
│   │   ├── dispatcher.ts      # HTTP/CLI 网关分发器
│   │   ├── config.ts         # 配置管理
│   │   ├── types.ts          # 类型定义
│   │   └── index.ts
│   ├── hooks/             # 事件钩子系统
│   ├── skills/            # 技能系统 (Markdown格式)
│   ├── notifications/     # 通知系统
│   ├── modes/             # 运行模式
│   ├── agents/            # Agent 定义
│   └── ...
├── crates/               # Rust 原生组件
│   ├── omx-runtime/      # 运行时核心
│   ├── omx-runtime-core/ # 运行时核心库
│   ├── omx-explore/      # 探索Agent
│   └── omx-sparkshell/   # 交互Shell
├── skills/               # 33个内置技能 (Markdown)
│   ├── deep-interview.md     # 深度访谈 (澄清需求)
│   ├── ralplan.md            # 计划审批
│   ├── ralph.md              # 持久执行
│   ├── team.md               # 团队协作
│   ├── code-review.md
│   ├── tdd.md
│   └── ...
└── prompts/              # 28个 Agent Role 提示词
    ├── executor.md
    ├── team-orchestrator.md
    ├── planner.md
    ├── qa-tester.md
    └── ...
```

---

## 二、核心架构分析

### 2.1 团队编排状态机 (Team Orchestrator)

**文件:** `src/team/orchestrator.ts`

```typescript
// 五阶段流水线
type TeamPhase = 'team-plan' | 'team-prd' | 'team-exec' | 'team-verify' | 'team-fix';
type TerminalPhase = 'complete' | 'failed' | 'cancelled';

// 转换规则
const TRANSITIONS: Record<TeamPhase, Array<TeamPhase | TerminalPhase>> = {
  'team-plan': ['team-prd'],
  'team-prd': ['team-exec'],
  'team-exec': ['team-verify'],
  'team-verify': ['team-fix', 'complete', 'failed'],
  'team-fix': ['team-exec', 'team-verify', 'complete', 'failed'],
};
```

**关键机制:**
- 状态持久化到 `.omx/team-state.json`
- 支持 `team-fix` 循环 (max 3次)
- 可恢复的团队状态 (`canResumeTeamState`)

### 2.2 角色路由 (Role Router)

**文件:** `src/team/role-router.ts`

```typescript
// Layer 1: 加载角色提示词
loadRolePrompt(role: string, promptsDir: string): Promise<string | null>
isKnownRole(role: string, promptsDir: string): boolean
listAvailableRoles(promptsDir: string): Promise<string[]>

// Layer 2: 启发式路由
routeTaskToRole(task: TeamTask): string
computeWorkerRoleAssignments(workers: Worker[], tasks: TeamTask[]): Map<Worker, TeamTask[]>
```

**内置角色 (28个):**
- `executor` / `team-executor` — 执行任务
- `team-orchestrator` — 协调团队
- `planner` — 规划任务
- `qa-tester` / `ultraqa` — 测试验证
- `code-reviewer` / `security-reviewer` — 代码审查
- `architect` / `information-architect` — 架构设计
- `researcher` / `product-analyst` — 研究分析

### 2.3 Ralph 持久循环 (Persistent Completion Loop)

**文件:** `src/ralph/contract.ts`

```typescript
// Ralph 状态机
type RalphPhase = 'starting' | 'executing' | 'verifying' | 'fixing' | 'complete' | 'failed' | 'cancelled';

// 持久化到 ~/.omx/ralph-state.json
// 每次状态变化写入磁盘，支持 resume
```

**Ralph vs Team:**
- Ralph: 单一Owner持久推进，类似 "Sisyphus"
- Team: 多Agent并行协作，阶段式流水线

### 2.4 OpenClaw 集成

**文件:** `src/openclaw/dispatcher.ts`

```typescript
// 支持两种网关
interface OpenClawHttpGatewayConfig {
  url: string;           // HTTPS 或 localhost HTTP
  token?: string;       // 可选认证
}

interface OpenClawCommandGatewayConfig {
  command: string;       // CLI 命令模板
  timeoutMs: number;     // 100ms - 300000ms 安全边界
}

// 事件类型
type HookEvent = 'session-start' | 'session-idle' | 'session-end' | 'ask-user-question' | 'stop';

// 指令格式
"[event|exec]\nproject={{projectName}} session={{sessionId}}\n요약: ...\n우선순위: ..."
```

### 2.5 技能系统 (Skills)

**格式:** Markdown 文件 + 参数替换

```markdown
# $skill-name
## Purpose
...

## Usage
$skill-name arg1 "arg with spaces" --flag value

## Examples
...
```

**内置技能 (33个):**
| 技能 | 用途 |
|------|------|
| `$deep-interview` | 澄清需求、边界、排除项 |
| `$ralplan` | 批准方案 + 权衡分析 |
| `$ralph` | 持久完成循环 |
| `$team` | 团队并行执行 |
| `$code-review` | 代码审查 |
| `$tdd` | 测试驱动开发 |
| `$build-fix` | 自动修复构建错误 |
| `$security-review` | 安全审计 |

---

## 三、GO2SE 集成方案

### 3.1 当前痛点 & OMX 解决方案

| GO2SE 痛点 | OMX 解决方案 | 集成难度 |
|-----------|-------------|---------|
| 子Agent resume 401 错误 | git worktree 隔离 + 状态持久化 | 🟡 中等 |
| Context 溢出 (>50K) | 启发式路由 + 角色分离 | 🟢 简单 |
| 多任务协调混乱 | Team 状态机 (plan→exec→verify) | 🟡 中等 |
| 任务中途放弃 | Ralph 持久循环 | 🟢 简单 |
| 技能复用性差 | Markdown 技能 + 参数替换 | 🟢 简单 |
| OpenClaw 事件感知弱 | OpenClaw Hooks 集成 | 🟡 中等 |

### 3.2 推荐的 GO2SE 集成架构

```
GO2SE + OMX 融合架构
├── GO2SE CEO (主控)
│   ├── MiroFish 决策引擎
│   ├── 北斗七鑫投资体系
│   └── 调度命令 → OMX 执行器
│
├── OMX 任务执行层
│   ├── $team 3:researcher    # 研究Agent × 3
│   ├── $team 2:code-reviewer # 代码审查 × 2
│   ├── $ralph                # 持久执行循环
│   └── $deep-interview        # 需求澄清
│
└── OpenClaw Hooks 事件驱动
    ├── session-start  → 初始化任务队列
    ├── session-idle   → 自动恢复 + nudge
    └── session-end    → 状态存档
```

### 3.3 优先集成的 3 个模块

#### 优先级 1: Ralph 持久循环 (最快见效)
```
文件: src/ralph/
价值: 解决"任务执行到一半被中断"问题
集成: 复用 persistence.ts 逻辑，适配 GO2SE 任务
```

#### 优先级 2: Team 状态机 (核心编排)
```
文件: src/team/orchestrator.ts + role-router.ts
价值: 多任务并行协调，阶段式流水线
集成: 用于 GO2SE 回测任务、扫描任务的阶段管理
```

#### 优先级 3: OpenClaw Hooks (事件驱动)
```
文件: src/openclaw/
价值: session-start/idle/end 事件通知
集成: GO2SE 健康检查触发、任务完成通知
```

---

## 四、关键文件清单

| 文件 | 行数 | 用途 | GO2SE 可用性 |
|------|------|------|-------------|
| `src/team/orchestrator.ts` | ~200 | 状态机 | 🟡 需适配 |
| `src/team/role-router.ts` | ~270 | 角色路由 | 🟢 直接用 |
| `src/team/state.ts` | ~300 | 状态管理 | 🟡 需适配 |
| `src/team/tmux-session.ts` | ~250 | tmux隔离 | ⚪ Linux only |
| `src/team/worktree.ts` | ~200 | git隔离 | 🟢 直接用 |
| `src/ralph/contract.ts` | ~200 | 状态机 | 🟢 直接用 |
| `src/ralph/persistence.ts` | ~150 | 持久化 | 🟢 直接用 |
| `src/openclaw/dispatcher.ts` | ~350 | 网关分发 | 🟢 直接用 |
| `src/openclaw/types.ts` | ~100 | 类型定义 | 🟢 直接用 |
| `skills/deep-interview.md` | ~150 | 访谈技能 | 🟢 参考 |
| `skills/ralph.md` | ~100 | 持久技能 | 🟢 参考 |
| `skills/team.md` | ~120 | 团队技能 | 🟢 参考 |

---

## 五、安装验证

```bash
✅ npm install -g @openai/codex
✅ npm install -g oh-my-codex
✅ omx setup (完成)
✅ omx --version  # v0.11.12
✅ 源码已克隆: /root/.openclaw/workspace/OMX_SOURCE (35MB)
```

---

## 六、下一步行动

- [ ] 1. 分析 `src/ralph/persistence.ts` → 集成到 GO2SE 任务持久化
- [ ] 2. 提取 `src/team/role-router.ts` 启发式分配逻辑 → 增强 GO2SE 任务调度
- [ ] 3. 研究 `src/openclaw/dispatcher.ts` → 实现 GO2SE Hooks 通知
- [ ] 4. 克隆 33个技能文件 → 转化为 GO2SE 技能库
- [ ] 5. 创建 GO2SE × OMX 融合 Agent 原型

---

**结论:** OMX 的核心价值在于 **状态机 + 角色路由 + 持久化** 三合一，这是当前 GO2SE 最薄弱但也最容易快速提升的模块。建议优先集成 Ralph 的持久化逻辑，其次是 Team 的状态机。
