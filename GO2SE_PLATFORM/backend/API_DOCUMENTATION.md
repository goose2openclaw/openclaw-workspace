# 🪿 GO2SE 后台API文档

**版本: v9.0** | **日期: 2026-04-04** | **CEO: GO2SE 🪿**

---

## 一、API概览

### 基础信息
| 项目 | 值 |
|------|------|
| Base URL | `http://localhost:8004` |
| 版本 | v7.1.0 |
| 协议 | REST |
| 格式 | JSON |

### 认证
| 方式 | 说明 |
|------|------|
| API Key | Header: `X-API-Key: your-key` |
| Bearer Token | Header: `Authorization: Bearer token` |

---

## 二、核心端点

### 2.1 系统状态

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/` | 首页 |
| GET | `/health` | 健康检查 |
| GET | `/api/stats` | 系统统计 |

**GET /api/stats**
```json
{
  "total_trades": 0,
  "open_trades": 0,
  "total_signals": 25,
  "executed_signals": 0,
  "trading_mode": "dry_run",
  "max_position": 0.6,
  "stop_loss": 0.1,
  "take_profit": 0.3,
  "version": "v7.1.0",
  "strategy_mode": "manual"
}
```

---

### 2.2 市场数据

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/market` | 市场概览 |
| GET | `/api/market/{symbol}` | 单币数据 |
| GET | `/api/market/summary` | 市场摘要 |
| GET | `/api/markets` | 多市场 |
| GET | `/api/history/{market}` | 历史数据 |
| GET | `/api/consensus/{market}` | 市场共识 |

---

### 2.3 回测系统

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/backtest/params` | 回测参数 |
| GET | `/api/backtest/sources` | 数据源 |
| GET | `/api/backtest/history` | 回测历史 |
| POST | `/api/backtest/run` | 运行回测 |

**GET /api/backtest/params**
```json
{
  "modes": ["conservative", "balanced", "aggressive"],
  "timeframes": ["1m", "5m", "15m", "1h", "4h", "1d"],
  "strategies": ["rabbit", "mole", "oracle", "leader", "hitchhiker"],
  "indicators": ["RSI", "MACD", "BB", "KDJ", "OBV"]
}
```

---

### 2.4 模拟交易

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/paper/user_types` | 用户类型 |
| GET | `/api/paper/positions` | 持仓 |
| POST | `/api/paper/order` | 下单 |
| DELETE | `/api/paper/position/{id}` | 平仓 |

**GET /api/paper/user_types**
```json
{
  "types": [
    {"id": "guest", "name": "游客", "balance": 1000, "features": ["basic_signals"]},
    {"id": "subscriber", "name": "订阅者", "balance": 3000, "features": ["all_signals"]},
    {"id": "member", "name": "会员", "balance": 5000, "features": ["all_signals", "auto_trade"]},
    {"id": "lp", "name": "私募LP", "balance": "定制", "features": ["full_access"]},
    {"id": "expert", "name": "专家", "balance": "-", "features": ["expert_mode"]}
  ]
}
```

---

### 2.5 专家模式

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/expert/leverage_levels` | 杠杆等级 |
| GET | `/api/expert/config` | 专家配置 |
| POST | `/api/expert/enable` | 启用专家 |
| POST | `/api/expert/disable` | 禁用专家 |

**GET /api/expert/leverage_levels**
```json
{
  "levels": [
    {"tier": 1, "leverage": "2x", "min_capital": 1000},
    {"tier": 2, "leverage": "3x", "min_capital": 5000},
    {"tier": 3, "leverage": "5x", "min_capital": 10000},
    {"tier": 4, "leverage": "10x", "min_capital": 50000}
  ]
}
```

---

### 2.6 因子退化

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/factor/status` | 因子状态 |
| GET | `/api/factor/degraded` | 退化因子 |
| GET | `/api/factor/report` | 分析报告 |

**GET /api/factor/status**
```json
{
  "factors": [
    {"id": "momentum", "health": 0.85, "degradation": 0.12},
    {"id": "volume", "health": 0.92, "degradation": 0.05},
    {"id": "sentiment", "health": 0.78, "degradation": 0.18}
  ],
  "overall_health": 0.85,
  "recommendations": ["rebalance_momentum", "refresh_sentiment"]
}
```

---

### 2.7 MiroFish决策

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/mirofish/decision` | MiroFish决策 |
| GET | `/api/mirofish/markets` | 市场数据 |
| GET | `/api/mirofish/score/{tool_id}` | 评分 |

**GET /api/mirofish/decision**
```json
{
  "consensus": "BUY",
  "confidence": 0.72,
  "agents": 100,
  "votes": {"buy": 36, "sell": 27, "hold": 37},
  "timestamp": "2026-04-04T01:00:00Z",
  "recommendations": {
    "action": "EXECUTE",
    "tool": "mole",
    "position_size": 0.20,
    "stop_loss": 0.08,
    "take_profit": 0.15
  }
}
```

---

### 2.8 策略管理

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/strategies` | 所有策略 |
| GET | `/api/strategies/{id}` | 策略详情 |
| POST | `/api/strategies` | 创建策略 |
| PUT | `/api/strategies/{id}` | 更新策略 |
| DELETE | `/api/strategies/{id}` | 删除策略 |

---

### 2.9 信号系统

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/signals` | 信号列表 |
| GET | `/api/signals/{id}` | 信号详情 |
| POST | `/api/signals/generate` | 生成信号 |

---

### 2.10 声纳库

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/sonar/models` | 趋势模型 |
| GET | `/api/sonar/models/categories` | 模型分类 |
| POST | `/api/sonar/detect` | 趋势检测 |

---

### 2.11 性能数据

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/performance` | 性能矩阵 |
| GET | `/api/compare` | 对比分析 |
| GET | `/api/portfolio` | 组合数据 |

---

## 三、策略API

### 3.1 打兔子 (Rabbit)
```
GET  /api/strategies/rabbit/config
POST /api/strategies/rabbit/enable
POST /api/strategies/rabbit/disable
```

### 3.2 打地鼠 (Mole)
```
GET  /api/strategies/mole/config
POST /api/strategies/mole/enable
POST /api/strategies/mole/disable
```

### 3.3 走着瞧 (Oracle)
```
GET  /api/strategies/oracle/config
POST /api/strategies/oracle/enable
POST /api/strategies/oracle/disable
```

### 3.4 跟大哥 (Leader)
```
GET  /api/strategies/leader/config
POST /api/strategies/leader/enable
POST /api/strategies/leader/disable
```

### 3.5 搭便车 (Hitchhiker)
```
GET  /api/strategies/hitchhiker/config
POST /api/strategies/hitchhiker/enable
POST /api/strategies/hitchhiker/disable
```

---

## 四、错误码

| 码 | 说明 |
|----|------|
| 200 | 成功 |
| 400 | 请求错误 |
| 401 | 未认证 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 429 | 请求过于频繁 |
| 500 | 服务器错误 |

---

## 五、速率限制

| 端点 | 限制 |
|------|------|
| `/api/*` | 100次/分钟 |
| `/api/backtest/*` | 10次/分钟 |
| `/api/paper/*` | 60次/分钟 |

---

**CEO: GO2SE 🪿 | 后台API文档 | 2026-04-04**
