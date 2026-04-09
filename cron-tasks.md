# 🕐 24小时运转任务

## Heartbeat 任务 (每5分钟)

```
- 检查市场信号
- 更新交易信号
- 检查持仓状态
- 推送高置信度信号
```

## Cron 任务

### 每15分钟 - 市场扫描
```json
{
  "name": "xiami-market-scan",
  "schedule": {"kind": "every", "everyMs": 900000},
  "payload": {"kind": "systemEvent", "text": "执行市场扫描"}
}
```

### 每30分钟 - 交易执行
```json
{
  "name": "xiami-tiered-trading",
  "schedule": {"kind": "every", "everyMs": 1800000},
  "payload": {"kind": "systemEvent", "text": "执行交易策略"}
}
```

### 每小时 - 复盘总结
```json
{
  "name": "daily-review",
  "schedule": {"kind": "every", "everyMs": 3600000},
  "payload": {"kind": "systemEvent", "text": "每日复盘"}
}
```

---

## 🚀 加速方案

### 1. 本地多线程
- 使用Python threading
- 同时运行多个任务

### 2. 外部算力
- Parallel AI (安装中)
- 云函数 (待配置)

### 3. 缓存优化
- 减少重复计算
- 本地缓存热点数据

---

*更新时间: 2026-03-13*
