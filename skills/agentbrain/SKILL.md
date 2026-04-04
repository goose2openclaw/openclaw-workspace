# AgentBrain Skill

> Official Knowcore SDK for AI agent memory. Retrieve context, learn new information, and preserve session history.

## 来源
- **npm**: `@knowcore/agentbrain`
- **GitHub**: https://github.com/TreyBros/agentbrain-sdk
- **本地**: `/root/.openclaw/workspace/agentbrain-sdk`

## 功能定位

AgentBrain 是一个**AI Agent记忆系统**，为AI Agent提供：
- 🚀 快速检索 (~1-2秒)
- 🧠 Agent原生RAG工作流
- 📦 零依赖
- 🔒 类型安全 (TypeScript)
- 🔄 智能重试 (指数退避)
- 🌐 通用 (Node.js/浏览器/Edge)

## 与GO2SE集成

AgentBrain可以作为GO2SE的记忆层：

| AgentBrain | GO2SE应用 |
|------------|-----------|
| 上下文检索 | MiroFish决策支持 |
| 记忆保存 | 交易历史持久化 |
| 知识学习 | 策略迭代学习 |

## 使用方法

### Node.js/TypeScript
```typescript
import { AgentBrain } from '@knowcore/agentbrain';

const brain = new AgentBrain('kc_live_your_api_key_here');

// 健康检查
const health = await brain.healthCheck();
console.log('Connected:', health.ok);

// 检索上下文
const result = await brain.retrieve('交易策略详情', {
  topK: 3,
  minScore: 0.4
});

// 使用上下文
const context = result.chunks
  .map(chunk => `[${chunk.metadata.title}]: ${chunk.text}`)
  .join('\n\n');
```

### JavaScript
```javascript
const { AgentBrain } = require('@knowcore/agentbrain');
```

## API

### AgentBrain Class

| 方法 | 说明 |
|------|------|
| `healthCheck()` | 检查连接状态 |
| `retrieve(query, options)` | 检索相关上下文 |
| `index(documents)` | 添加文档到索引 |
| `delete(id)` | 删除文档 |

### retrieve选项
```typescript
{
  topK: 3,        // 返回topK结果
  minScore: 0.4,  // 最小相似度分数
  filter: {}      // 元数据过滤
}
```

## 本地文件
```
/root/.openclaw/workspace/agentbrain-sdk/
├── src/              # TypeScript源码
├── examples/         # 示例代码
├── test/             # 测试
├── node_modules/     # 已安装依赖
└── package.json
```

## 依赖安装状态
```bash
cd /root/.openclaw/workspace/agentbrain-sdk
npm install  # 已完成
```

## 与现有技能互补

| 技能 | 功能 | AgentBrain增强 |
|------|------|----------------|
| memory-qdrant | Qdrant向量存储 | AgentBrain云端记忆 |
| memory-tiering | 记忆分层 | 上下文快速检索 |
| aoms | 持久记忆服务 | Agent原生RAG |

## 注意事项

- 需要API Key (kc_live_xxx)
- 免费版有速率限制
- 生产环境建议自托管Knowcore后端
