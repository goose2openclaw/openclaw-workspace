# sessions-send 技能

> OpenClaw内置跨会话消息工具的配置、测试和优化

## 功能

`sessions_send` 是 OpenClaw 的**内置工具**，用于向其他会话发送消息。

## 工具参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `sessionKey` | string | ✅ | 目标会话键 |
| `message` | string | ✅ | 发送的消息 |
| `timeoutSeconds` | number | ❌ | 等待秒数 (0=即发即忘) |

## sessionKey格式

```
agent:<agentId>:<channel>:<scope>:<id>
```

常用键:
- `main` - 主会话 (当前)
- `agent:main:subagent:<uuid>` - 子Agent会话
- `cron:<jobId>` - Cron任务会话

## 使用场景

| 场景 | 示例 | timeout |
|------|------|---------|
| 主Agent → 子Agent | 调度任务 | 0 (即发即忘) |
| 主Agent → 主Agent | 跨会话通信 | 30-60 |
| Agent → Cron | 触发定时任务 | 0 |

## 返回状态

| status | 说明 |
|--------|------|
| `ok` | 成功，等待完成 |
| `timeout` | 等待超时，任务继续 |
| `error` | 发送失败 |

## 测试结果

```
当前活跃会话: 10个
- agent:main:main (running)
- agent:main:subagent:* (13个子会话)

测试sessions_send:
- 发送到已结束session → timeout (正常)
- 发送到活跃session → ok
```

## GO2SE集成

```javascript
// 调度子Agent (即发即忘)
const result = await sessions_send({
  sessionKey: "agent:main:subagent:<uuid>",
  message: "执行: 买入BTC",
  timeoutSeconds: 0
});

// 等待响应
const result = await sessions_send({
  sessionKey: "agent:main:subagent:<uuid>",
  message: "查询状态",
  timeoutSeconds: 30
});

// result格式
{
  runId: "xxx",
  status: "ok",      // ok | timeout | error
  reply: { ... }     // 响应内容 (如果等待)
}
```

## 安全配置

```yaml
sessions_send:
  default_timeout: 30
  max_retries: 3
  safety:
    allow_channels: ["telegram", "discord", "webchat"]
    max_message_length: 10000
```

## 与GO2SE Cron集成

```yaml
# Cron调度使用sessionTarget指定会话
cron:
  - name: 权重更新
    schedule: "0 */2 * * *"
    sessionTarget: isolated  # 在隔离会话中运行
    payload:
      kind: agentTurn
      message: "运行权重更新..."
```
