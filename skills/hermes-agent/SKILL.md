# Hermes Agent Skill

> Self-improving AI agent built by Nous Research

## 来源
- **GitHub**: https://github.com/NousResearch/hermes-agent
- **文档**: https://hermes-agent.nousresearch.com/docs/
- **本地**: `/root/.openclaw/workspace/hermes-agent/`

## 核心功能

Hermes Agent 是一个**自改进AI Agent**，具有内置学习循环：

| 功能 | 说明 |
|------|------|
| **持久记忆** | 跨会话记忆，保持上下文 |
| **技能创建** | 从经验中创建可复用技能 |
| **自我改进** | 使用过程中自动改进技能 |
| **多平台** | Telegram, Discord, Slack, CLI |
| **模型灵活** | 支持OpenRouter/OpenAI/自有端点 |

## 与GO2SE集成

Hermes Agent 可以作为GO2SE的**增强Agent层**：

| Hermes功能 | GO2SE应用 |
|------------|-----------|
| 自改进学习 | 策略迭代优化 |
| 跨会话记忆 | 交易历史学习 |
| 技能创建 | 自定义策略生成 |
| 多平台通信 | 通知和报警 |

## 安装状态

```bash
# Hermes Agent 已克隆到:
/root/.openclaw/workspace/hermes-agent/

# 查看技能
ls /root/.openclaw/workspace/hermes-agent/skills/

# 可用技能目录 (部分):
apple, autonomous-ai-agents, creative, data-science
devops, diagramming, github, mlops
```

## 使用方法

### 快速安装
```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

### 启动Hermes
```bash
hermes
```

### 配置模型
```bash
hermes model set openrouter <API_KEY>
hermes model set openai <API_KEY>
```

### 创建技能
```bash
hermes skill create <skill_name>
```

### 调度任务
```bash
hermes cron "每2小时检查市场" --interval=2h
```

## 架构特点

```
Hermes Agent
├── 持久记忆层 (Session + User Model)
├── 技能系统 (Skills)
├── 调度系统 (Cron)
├── 通信网关 (Telegram/Discord/Slack)
└── 模型路由 (OpenRouter/OpenAI/自有)
```

## 与现有技能互补

| 技能 | 功能 | Hermes增强 |
|------|------|-----------|
| agentbrain | 云端记忆 | 本地+云端双记忆 |
| memory-qdrant | 向量存储 | 语义检索+记忆 |
| capability-evolver | 自我改进 | 自改进Agent |

## 文件结构
```
hermes-agent/
├── agent/              # Agent核心
├── skills/            # 技能库
├── hermes_cli/       # CLI工具
├── acp_adapter/      # ACP协议
├── docs/             # 文档
└── requirements.txt
```

## 状态
- **克隆**: ✅ 完成
- **安装**: ⏳ 待网络恢复后安装
- **集成**: 🔄 开发中
