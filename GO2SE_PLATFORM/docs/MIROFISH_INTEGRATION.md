# MiroFish 集成方案

## 一、双层部署架构

```
┌─────────────────────────────────────────────────────────────┐
│                    MiroFish 双层部署                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  层级1: 工具级 MiroFish (投资决策仿真)               │   │
│  │                                                      │   │
│  │  🐰 打兔子 → MiroFish仿真 → 买入/卖出/持有           │   │
│  │  🐹 打地鼠 → MiroFish仿真 → 锁定/执行                 │   │
│  │  🔮 走着瞧 → MiroFish仿真 → 预测确认                 │   │
│  │  👑 跟大哥 → MiroFish仿真 → 跟单决策                 │   │
│  │  🍀 搭便车 → MiroFish仿真 → 跟单判断                 │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  层级2: 平台级 MiroFish (系统稳定+可持续提升)         │   │
│  │                                                      │   │
│  │  • 因子退化检测 → 自动触发优化                        │   │
│  │  • 策略评分排序 → 动态权重调整                        │   │
│  │  • 新机会发现 → 信号注入                              │   │
│  │  • 系统健康监控 → 异常告警                            │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 二、工具级集成 (MiroFish仿真参与决策)

### 2.1 🐰 打兔子 (Rabbit)

```json
{
  "mirofish_integration": {
    "enabled": true,
    "simulation_before_entry": true,
    "decision_weight": 0.35,
    "required_score": 70,
    "simulation_dimensions": ["A1", "A2", "B1", "C1", "D1"],
    "monte_carlo_runs": 1000,
    "confidence_threshold": 0.75
  }
}
```

**决策流程**:
1. 声纳库扫描 → 发现信号
2. MiroFish仿真 → 验证信号可信度
3. 分数≥70 → 执行
4. 分数<70 → 降低仓位或放弃

### 2.2 🐹 打地鼠 (Mole)

```json
{
  "mirofish_integration": {
    "enabled": true,
    "simulation_before_entry": true,
    "decision_weight": 0.40,
    "required_score": 75,
    "simulation_dimensions": ["A1", "A2", "B2", "C1", "D1", "D4"],
    "monte_carlo_runs": 1500,
    "confidence_threshold": 0.80,
    "radar_lock_override": true
  }
}
```

**决策流程**:
1. 火控雷达锁定 → 发现异动
2. MiroFish仿真 → 计算预期收益/风险
3. 分数≥75 → 锁定执行
4. 分数<75 → 降低仓位或放弃

### 2.3 🔮 走着瞧 (Oracle) - 核心集成

```json
{
  "mirofish_integration": {
    "enabled": true,
    "simulation_before_entry": true,
    "decision_weight": 0.50,
    "required_score": 70,
    "simulation_dimensions": ["A1", "A2", "A3", "B3", "C1", "C2", "C3", "D1", "D4"],
    "monte_carlo_runs": 2000,
    "confidence_threshold": 0.85,
    "prediction_market_boost": true
  }
}
```

**决策流程**:
1. 预测市场信号 → 来自Polymarket等
2. MiroFish仿真 → 多智能体共识验证
3. 分数≥70 → 执行预测
4. 分数<70 → 观望

### 2.4 👑 跟大哥 (Leader)

```json
{
  "mirofish_integration": {
    "enabled": true,
    "simulation_before_entry": true,
    "decision_weight": 0.30,
    "required_score": 70,
    "simulation_dimensions": ["A1", "A2", "B4", "C1", "D1"],
    "monte_carlo_runs": 1000,
    "confidence_threshold": 0.75,
    "provider_verification": true
  }
}
```

**决策流程**:
1. 选择Trader/策略
2. MiroFish仿真 → 验证Trader历史表现
3. 分数≥70 → 跟单
4. 分数<70 → 不跟

### 2.5 🍀 搭便车 (Hitchhiker)

```json
{
  "mirofish_integration": {
    "enabled": true,
    "simulation_before_entry": true,
    "decision_weight": 0.25,
    "required_score": 65,
    "simulation_dimensions": ["A1", "A2", "B5", "C1", "D1"],
    "monte_carlo_runs": 800,
    "confidence_threshold": 0.70,
    "sub_package_simulation": true
  }
}
```

## 三、平台级集成 (系统稳定+可持续提升)

### 3.1 因子退化检测

```yaml
factor_degradation:
  monitor_interval: 3600  # 1小时
  degradation_threshold: 0.15
  auto_optimize: true
  notify_on_degradation: true
  
  checked_factors:
    - momentum_rsi_14
    - trend_ema_20
    - volatility_bollinger_20
    - volume_obv
```

### 3.2 策略评分排序

```yaml
strategy_scoring:
  enabled: true
  update_interval: 1800  # 30分钟
  scoring_criteria:
    - recent_return (30%)
    - sharpe_ratio (25%)
    - max_drawdown (20%)
    - win_rate (15%)
    - mirofish_score (10%)
```

### 3.3 系统健康监控

```yaml
system_health:
  enabled: true
  check_interval: 300  # 5分钟
  
  metrics:
    - api_latency: <100ms
    - error_rate: <1%
    - memory_usage: <85%
    - cpu_usage: <90%
    - disk_usage: <90%
  
  alerts:
    - on_degradation: notify
    - on_critical: auto_restart
```

## 四、MiroFish API 端点

### 工具级调用

```
POST /api/oracle/mirofish/predict
POST /api/mirofish/decide/{tool}
POST /api/mirofish/fuse
```

### 平台级调用

```
POST /api/mirofish/autonomous/iterate
GET /api/mirofish/status
GET /api/mirofish/weights
POST /api/mirofish/weights
```

## 五、信号融合权重

```yaml
signal_weights:
  mirofish: 0.25      # MiroFish共识
  sonar: 0.20         # 声纳库
  oracle: 0.20        # 预言机
  sentiment: 0.15      # 情绪
  external_api: 0.10  # 外部API
  professional: 0.10   # 专业判断

weight_bounds:
  mirofish: [0.05, 0.50]
  sonar: [0.05, 0.40]
  oracle: [0.05, 0.40]
  sentiment: [0.05, 0.30]
  external_api: [0.00, 0.30]
  professional: [0.00, 0.30]
```

## 六、25维度全向仿真

### 工具级维度 (参与决策)

| 工具 | MiroFish维度 | 仿真权重 |
|------|-------------|---------|
| 🐰 打兔子 | A1, A2, B1, C1, D1 | 35% |
| 🐹 打地鼠 | A1, A2, B2, C1, D1, D4 | 40% |
| 🔮 走着瞧 | A1-A3, B3, C1-C3, D1, D4 | 50% |
| 👑 跟大哥 | A1, A2, B4, C1, D1 | 30% |
| 🍀 搭便车 | A1, A2, B5, C1, D1 | 25% |

### 平台级维度 (系统稳定)

| 维度 | 说明 | 触发条件 |
|------|------|---------|
| E5-系统稳定性 | 进程监控 | 崩溃时 |
| E6-API延迟 | 响应时间 | >100ms |
| D2-算力资源 | CPU/内存 | >85% |
| F1-UI响应性 | 前端延迟 | >500ms |

---

## 七、集成状态

| 工具 | MiroFish集成 | 状态 |
|------|-------------|------|
| 🐰 打兔子 | ✅ | 已配置 |
| 🐹 打地鼠 | ✅ | 已配置 |
| 🔮 走着瞧 | ✅ | 已配置 |
| 👑 跟大哥 | ✅ | 已配置 |
| 🍀 搭便车 | ✅ | 已配置 |
| 💰 薅羊毛 | ❌ | 打工工具不需要 |
| 👶 穷孩子 | ❌ | 打工工具不需要 |

| 功能 | 状态 |
|------|------|
| 因子退化检测 | ✅ 已配置 |
| 策略评分排序 | ✅ 已配置 |
| 系统健康监控 | ✅ 已配置 |
| 6个预测市场 | ✅ 运行中 |
| 450智能体×5轮 | ✅ 运行中 |
