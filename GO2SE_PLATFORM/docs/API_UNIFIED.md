# GO2SE API 统一文档 v1.0

## API Base
```
http://localhost:8004
```

## 认证
```javascript
Authorization: Bearer GO2SE_e083a64d891b45089d6f37acb440435eba401313a1695711
```

---

## 核心API

### 策略系统
| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/strategy` | 完整策略配置 |
| GET | `/api/strategy/tools` | 7大工具详情 |
| GET | `/api/strategy/styles` | 3种风格配置 |
| GET | `/api/strategy/recommend` | 当前推荐配置 |
| POST | `/api/strategy/style/{style}` | 切换风险风格 |

### 双脑系统
| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/brain` | 双脑配置 |
| POST | `/api/brain/switch?brain=left|right` | 切换脑 |

### 交易系统
| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/backtest` | 运行回测 |
| GET | `/api/backtest/history` | 回测历史 |
| POST | `/api/paper/account` | 创建模拟账户 |
| GET | `/api/paper/portfolio/{user_id}` | 获取持仓 |
| POST | `/api/paper/position/open` | 开仓 |
| POST | `/api/paper/position/close` | 平仓 |

### MiroFish
| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/mirofish/status` | 状态 |
| GET | `/api/mirofish/markets` | 市场数据 |
| POST | `/api/mirofish/predict` | 预测 |

### 系统
| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/stats` | 系统状态 |
| GET | `/health` | 健康检查 |

---

## 响应格式

### 成功
```json
{
  "status": "ok",
  "data": { ... }
}
```

### 错误
```json
{
  "detail": "错误信息"
}
```

---

## 状态码
- 200: 成功
- 401: 未授权
- 404: 未找到
- 500: 服务器错误
