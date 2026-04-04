# GO2SE 权重引擎架构

> 核心原则文档 | 版本: v11.0.0 | 更新: 2026-04-04

---

## 一、终极输出等式

```
GO2SE终极决策 = Σ(技能/策略 × 动态权重) + MiroFish仿真验证

执行操作 = f(原生策略, 外部技能, ML新策略, MiroFish反馈)
```

### 权重组合等式

```
最终信号 = 
  (原生策略₁ × W₁) + (原生策略₂ × W₂) + ... +
  (外部技能₁ × W_ext₁) + (外部技能₂ × W_ext₂) + ... +
  (ML新策略₁ × W_ml₁) + ... +
  MiroFish共识 × W_mf

其中: ΣW = 1.0, W ∈ [0, 1]
```

---

## 二、全部技能和策略清单

### 2.1 量化交易技能 (已有)

| 技能 | 来源 | 功能 | 集成权重 |
|------|------|------|---------|
| **MoneyClaw** | GitHub | DCA定投/智能再平衡/价格告警/资金费率 | 0.0-0.3 |
| **AgentBrain** | npm | AI Agent记忆/RAG | 0.0-0.2 |
| **EvoMap** | API | 众包/社交信号 | 0.0-0.15 |
| **Binance Connector** | 内置 | 交易所连接 | 自动 |
| **OKX Connector** | 内置 | 交易所连接 | 自动 |
| **Polymarket Connector** | 内置 | 预测市场 | 自动 |

### 2.2 量化交易策略 (已有)

| 策略 | 工具 | 功能 | 基础权重 |
|------|------|------|---------|
| **声纳库123模型** | 全部 | 趋势/动量/波动/成交量检测 | 0.15 |
| **火控雷达** | 打地鼠 | 异动扫描 | 0.20 |
| **MiroFish共识** | 全部 | 450智能体×5轮仿真 | 0.25 |
| **信号融合引擎** | 全部 | 6源信号融合 | 0.20 |

### 2.3 GO2SE原生策略 (已有)

| 策略 | 工具 | 功能 | 基础权重 |
|------|------|------|---------|
| **Rabbit趋势策略** | 打兔子 | EMA/MA趋势追踪 | 0.60 |
| **Mole异动策略** | 打地鼠 | RSI/CCI扫描 | 0.50 |
| **Oracle预测策略** | 走着瞧 | Polymarket预测 | 0.40 |
| **Leader做市策略** | 跟大哥 | 订单簿/资金费率 | 0.50 |
| **Hitchhiker跟单策略** | 搭便车 | 跟Trader | 0.60 |

### 2.4 机器学习迭代策略 (自动生成)

| 来源 | 类型 | 生成方式 |
|------|------|---------|
| **因子挖掘** | 新因子 | 遗传算法/贝叶斯优化 |
| **策略融合** | 组合策略 | 策略交叉/变异 |
| **参数优化** | 调参 | 网格搜索/随机搜索 |
| **市场适应** | 自适应 | 强化学习 |

---

## 三、扩展通道 (为未来技能/策略预留)

### 3.1 技能注册表

```yaml
# skills_registry.yaml
skills:
  # 已有技能
  moneyclaw:
    path: /workspace/skills/moneyclaw/
    enabled: true
    weight_range: [0.0, 0.3]
    
  agentbrain:
    path: /workspace/skills/agentbrain/
    enabled: true
    weight_range: [0.0, 0.2]
    
  evomap:
    path: /workspace/skills/evomap/
    enabled: true
    weight_range: [0.0, 0.15]
    
  # 预留通道 (未来技能)
  future_skill_1:
    path: null  # 待接入
    enabled: false
    weight_range: [0.0, 0.2]
```

### 3.2 策略注册表

```yaml
# strategies_registry.yaml
strategies:
  # 已有策略
  sonar_123:
    enabled: true
    weight_range: [0.05, 0.30]
    auto_tune: true
    
  mirofish:
    enabled: true
    weight_range: [0.10, 0.50]
    auto_tune: true
    
  # 预留通道 (未来策略)
  future_strategy_1:
    enabled: false
    weight_range: [0.0, 0.2]
    auto_tune: false
```

---

## 四、权重组合引擎

### 4.1 引擎架构

```
┌─────────────────────────────────────────────────────────────┐
│                    权重组合引擎 (Weight Engine)              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │ 原生策略   │    │ 外部技能   │    │ ML新策略   │    │
│  │  W=0.4-0.7│    │ W=0.0-0.3 │    │ W=0.0-0.2 │    │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘    │
│         │                   │                   │            │
│         └───────────────────┼───────────────────┘            │
│                             ↓                              │
│                    ┌─────────────────┐                    │
│                    │  权重融合层    │                    │
│                    │  Σ(Wᵢ × Sᵢ)  │                    │
│                    └────────┬────────┘                    │
│                             ↓                              │
│                    ┌─────────────────┐                    │
│                    │ MiroFish验证   │                    │
│                    │ 450 Agent仿真  │                    │
│                    └────────┬────────┘                    │
│                             ↓                              │
│                    ┌─────────────────┐                    │
│                    │  最优权重输出  │                    │
│                    │  执行决策     │                    │
│                    └─────────────────┘                    │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 权重计算公式

```python
def calculate_final_signal(signals: dict, weights: dict, mirofish_score: float) -> dict:
    """
    最终信号 = Σ(策略信号 × 策略权重) + MiroFish验证
    
    Args:
        signals: 各策略信号 dict
        weights: 各策略权重 dict  
        mirofish_score: MiroFish仿真分数 [0-100]
    
    Returns:
        最终执行决策
    """
    # 1. 基础信号融合
    weighted_sum = 0
    weight_total = 0
    
    for strategy, signal in signals.items():
        w = weights.get(strategy, 0)
        if w > 0:
            weighted_sum += signal * w
            weight_total += w
    
    base_signal = weighted_sum / weight_total if weight_total > 0 else 0
    
    # 2. MiroFish验证
    mirofish_weight = weights.get('mirofish', 0.25)
    verified_signal = (
        base_signal * (1 - mirofish_weight) +
        (mirofish_score / 100) * mirofish_weight
    )
    
    # 3. 最终决策
    if verified_signal >= 0.7:
        decision = 'BUY'
    elif verified_signal <= 0.3:
        decision = 'SELL'
    else:
        decision = 'HOLD'
    
    return {
        'decision': decision,
        'signal': verified_signal,
        'confidence': abs(verified_signal - 0.5) * 2,
        'mirofish_score': mirofish_score,
        'base_signal': base_signal
    }
```

---

## 五、MiroFish周期性权重优化

### 5.1 优化流程

```
┌─────────────────────────────────────────────────────────────┐
│            MiroFish 周期性权重优化 (每2小时)                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  T+0:00  启动优化周期                                       │
│         ↓                                                  │
│  T+0:01  收集历史表现数据                                   │
│         - 过去2小时的交易结果                               │
│         - 各策略的胜率/收益率                               │
│         - 因子退化度                                       │
│         ↓                                                  │
│  T+0:05  蒙特卡洛仿真 (1000次)                             │
│         - 随机扰动权重                                      │
│         - 计算期望收益                                      │
│         - 记录最优组合                                      │
│         ↓                                                  │
│  T+0:30  遗传算法优化                                      │
│         - 选择: 保留top 20%权重组合                        │
│         - 交叉: 随机交换权重                                │
│         - 变异: 随机调整±5%                                │
│         ↓                                                  │
│  T+1:00  贝叶斯优化                                       │
│         - 建立代理模型                                      │
│         - 探索高收益区域                                    │
│         ↓                                                  │
│  T+1:30  候选权重验证                                      │
│         - MiroFish 450 Agent仿真                           │
│         - 验证新权重的稳定性                                │
│         ↓                                                  │
│  T+2:00  发布最优权重                                      │
│         - 更新权重配置                                      │
│         - 记录日志                                          │
│         - 通知监控系统                                      │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 优化目标函数

```python
def optimization_objective(weights: dict) -> float:
    """
    优化目标: 最大化夏普比率 + 最小化回撤 + 因子不退化
    
    Returns:
        综合得分 (越高越好)
    """
    # 1. 收益率 (40%)
    returns = calculate_returns(weights)
    
    # 2. 夏普比率 (30%)
    sharpe = calculate_sharpe_ratio(weights)
    
    # 3. 最大回撤 (20%)
    max_drawdown = calculate_max_drawdown(weights)
    
    # 4. 因子健康度 (10%)
    factor_health = calculate_factor_health(weights)
    
    score = (
        returns * 0.40 +
        sharpe * 0.30 +
        (1 - max_drawdown) * 0.20 +
        factor_health * 0.10
    )
    
    return score
```

### 5.3 因子不退化保障

```python
def ensure_factor_no_degradation(weights: dict) -> bool:
    """
    保障因子不退化反而提升
    
    条件:
    - 当前因子评分 >= 上周期评分
    - 或 收益改善 > 5%
    """
    current_score = evaluate_factor_health(weights)
    previous_score = get_previous_factor_score()
    returns_improvement = calculate_returns_improvement(weights)
    
    if current_score >= previous_score:
        return True  # 因子健康
    
    if returns_improvement > 0.05:
        return True  # 收益改善可接受
    
    return False  # 因子退化, 需要回滚
```

---

## 六、完整技能/策略列表

### 6.1 量化交易技能

| # | 技能 | 来源 | 状态 | 权重范围 |
|---|------|------|------|---------|
| 1 | MoneyClaw | Qiyd81/moneyclaw-py | ✅ 已安装 | 0.0-0.3 |
| 2 | AgentBrain | TreyBros/agentbrain-sdk | ✅ 已安装 | 0.0-0.2 |
| 3 | EvoMap | evomap.ai | ✅ 已集成 | 0.0-0.15 |
| 4 | Binance Connector | GO2SE内置 | ✅ 运行中 | 自动 |
| 5 | OKX Connector | GO2SE内置 | ✅ 运行中 | 自动 |
| 6 | Polymarket | GO2SE内置 | ✅ 运行中 | 自动 |

### 6.2 量化交易策略

| # | 策略 | 类型 | 状态 | 权重范围 |
|---|------|------|------|---------|
| 1 | 声纳库123模型 | 趋势/动量/波动 | ✅ 95激活 | 0.05-0.30 |
| 2 | 火控雷达 | 异动扫描 | ✅ 运行中 | 0.10-0.25 |
| 3 | MiroFish共识 | 智能体仿真 | ✅ 450×5轮 | 0.10-0.50 |
| 4 | 信号融合引擎 | 多源融合 | ✅ 运行中 | 0.15-0.30 |
| 5 | 预测市场引擎 | Polymarket | ✅ 6市场 | 0.10-0.25 |

### 6.3 GO2SE原生策略

| # | 策略 | 工具 | 基础权重 |
|---|------|------|---------|
| 1 | Rabbit趋势 | 🐰 打兔子 | 0.60 |
| 2 | Mole异动 | 🐹 打地鼠 | 0.50 |
| 3 | Oracle预测 | 🔮 走着瞧 | 0.40 |
| 4 | Leader做市 | 👑 跟大哥 | 0.50 |
| 5 | Hitchhiker跟单 | 🍀 搭便车 | 0.60 |

### 6.4 机器学习迭代策略

| # | 策略 | 生成方式 | 状态 |
|---|------|---------|------|
| 1 | 因子挖掘 | 遗传算法 | 🔄 开发中 |
| 2 | 策略融合 | 交叉变异 | 🔄 开发中 |
| 3 | 参数优化 | 贝叶斯 | 🔄 开发中 |
| 4 | 市场适应 | 强化学习 | 🔄 规划中 |

---

## 七、终极输出格式

```json
{
  "timestamp": "2026-04-04T07:58:00Z",
  "decision": {
    "action": "BUY",
    "symbol": "BTC/USDT",
    "signal": 0.78,
    "confidence": 0.85,
    "reason": "多策略共振+MiroFish验证通过"
  },
  "weight_breakdown": {
    "native_strategies": {
      "rabbit_trend": 0.25,
      "mole_radar": 0.15,
      "oracle_prediction": 0.10
    },
    "external_skills": {
      "mirofish": 0.25,
      "sonar_123": 0.12,
      "signal_fusion": 0.08
    },
    "ml_strategies": {
      "factor_mining": 0.05
    }
  },
  "mirofish_verification": {
    "score": 82,
    "agents": 450,
    "rounds": 5,
    "consensus": "BUY",
    "confidence": 0.88
  },
  "optimization": {
    "last_optimized": "2026-04-04T06:00:00Z",
    "next_optimization": "2026-04-04T08:00:00Z",
    "sharpe_ratio": 1.45,
    "max_drawdown": 0.08,
    "factor_health": 0.92
  },
  "execution": {
    "recommended_action": "BUY",
    "position_size": 0.08,
    "stop_loss": 0.05,
    "take_profit": 0.10,
    "risk_level": "MEDIUM"
  }
}
```

---

## 八、监控指标

| 指标 | 目标 | 告警阈值 |
|------|------|---------|
| 夏普比率 | ≥1.5 | <1.0 |
| 最大回撤 | ≤10% | >15% |
| 因子健康度 | ≥0.85 | <0.70 |
| 信号置信度 | ≥0.75 | <0.50 |
| MiroFish评分 | ≥70 | <60 |
