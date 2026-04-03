# GO2SE 完整平台架构文档 v8.1
**版本: v8.1 | 更新: 2026-04-03**

---

## 一、平台整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        GO2SE 平台 v8.1                        │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   前台 UI    │  │   后台 API   │  │  MiroFish   │          │
│  │  (React)     │  │  (Flask)    │  │ (决策引擎)  │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                  │
│         └──────────────────┼──────────────────┘                  │
│                            │                                   │
│         ┌─────────────────┼─────────────────┐                │
│         │         ML Hub (7大模块)           │                │
│         │  ┌─────────────────────────────┐   │                │
│         │  │ 量化│预测│优化│胜率│算力  │   │                │
│         │  │ 空投│众包                   │   │                │
│         │  └─────────────────────────────┘   │                │
│         │                                      │                │
│         │  ┌─────────────────────────────┐   │                │
│         │  │  北斗七鑫投资体系 (7工具)   │   │                │
│         │  │  5投资工具 + 2打工工具      │   │                │
│         │  └─────────────────────────────┘   │                │
│         │                                      │                │
│         │  ┌─────────────────────────────┐   │                │
│         │  │  声纳库 (123趋势模型)      │   │                │
│         │  │  预言机 │ MiroFish │ 情绪   │   │                │
│         │  └─────────────────────────────┘   │                │
│         └──────────────────────────────────────┘                │
│                            │                                   │
│         ┌─────────────────┼─────────────────┐                │
│         │     自主迭代引擎 (闭环)            │                │
│         │  回测→仿真→蒸馏→优化→验证→部署    │                │
│         └──────────────────────────────────────┘                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 二、前台 (Frontend) 结构

### 2.1 技术栈
```
React 18 + TypeScript + Vite
状态管理: Zustand / Redux Toolkit
UI组件: TailwindCSS + HeadlessUI
图表: Recharts / TradingView
实时: WebSocket / Socket.io
```

### 2.2 页面结构
```
frontend/
├── src/
│   ├── components/
│   │   ├── Dashboard/         # 总览页
│   │   ├── Market/           # 市场页
│   │   ├── Strategies/        # 策略页
│   │   ├── Signals/           # 信号页
│   │   ├── Trading/            # 交易页
│   │   ├── Wallet/            # 钱包页
│   │   ├── Settings/          # 设置页
│   │   ├── MiroFish/          # MiroFish决策面板 🆕
│   │   └── ML/                # ML能力中心 🆕
│   ├── hooks/
│   │   ├── useMiroFish.ts     # MiroFish决策Hook 🆕
│   │   ├── useML.ts          # ML能力Hook 🆕
│   │   └── useAutoIterate.ts  # 自主迭代Hook 🆕
│   ├── stores/
│   │   ├── strategyStore.ts   # 策略状态
│   │   ├── mlStore.ts        # ML状态 🆕
│   │   └── mirofishStore.ts  # MiroFish状态 🆕
│   └── App.tsx
```

### 2.3 前台核心组件

#### MiroFish决策面板
```
MiroFish/
├── DecisionPanel.tsx      # 决策面板主组件
├── ConsensusView.tsx      # 100智能体共识可视化
├── ToolDecision.tsx      # 工具级别决策卡片
├── StrategySimulator.tsx  # 策略仿真界面
└── AutonomousLoop.tsx    # 自主迭代状态展示
```

#### ML能力中心
```
ML/
├── CapabilityGrid.tsx     # 能力网格展示
├── QuantEngine.tsx       # 量化引擎UI
├── Predictor.tsx         # 预测引擎UI
├── AirdropHunter.tsx    # 空投猎手UI
└── ComputeScheduler.tsx  # 算力调度UI
```

---

## 三、后台 (Backend) 结构

### 3.1 技术栈
```
Python 3.12 + Flask
数据库: SQLite / PostgreSQL
缓存: Redis
任务队列: Celery
ML: scikit-learn, XGBoost, TA-Lib
```

### 3.2 API结构
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Flask主入口
│   ├── routes/
│   │   ├── routes.py        # 核心路由
│   │   ├── routes_ml.py     # ML能力路由
│   │   ├── routes_mirofish_decision.py  # MiroFish决策路由 🆕
│   │   ├── routes_sonar.py  # 声纳库路由
│   │   └── routes_mirofish.py # MiroFish预测路由
│   ├── ml_core/             # ML能力中心 🆕
│   │   ├── __init__.py
│   │   ├── ml_hub.py
│   │   ├── quant_engine.py
│   │   ├── strategy_optimizer.py
│   │   ├── predictor.py
│   │   ├── airdrop_hunter.py
│   │   ├── compute_scheduler.py
│   │   ├── win_rate.py
│   │   └── crowdsignal.py
│   ├── core/                # 核心引擎
│   │   ├── sonar_v2.py      # 123个趋势模型
│   │   ├── risk_manager.py
│   │   ├── portfolio.py
│   │   └── ...
│   └── api/
│       └── ...
```

### 3.3 核心API端点

#### MiroFish决策API
```
GET  /api/mirofish/status                    # 引擎状态
POST /api/mirofish/decide/<tool>/<action>   # 工具决策
POST /api/mirofish/simulate/strategy        # 策略仿真
POST /api/mirofish/autonomous/iterate       # 自主迭代
POST /api/mirofish/consensus                # 通用共识
POST /api/mirofish/batch/decide             # 批量决策
```

#### ML API
```
GET  /api/ml/capabilities                   # 能力清单
POST /api/ml/quant/factor_analysis          # 多因子分析
POST /api/ml/quant/signals                  # 批量信号
POST /api/ml/predict/price                  # 价格预测
POST /api/ml/predict/trend                   # 趋势预测
POST /api/ml/optimizer/bayesian              # 贝叶斯优化
POST /api/ml/airdrop/scan                   # 空投资格扫描
POST /api/ml/compute/status                  # 算力状态
POST /api/ml/winrate/predict                # 胜率预测
POST /api/ml/crowd/aggregate                # 众包信号聚合
```

---

## 四、MiroFish决策引擎

### 4.1 架构
```
MiroFish决策引擎
├── 100智能体共识模块
│   ├── 技术分析Agent (30个)
│   ├── 基本面Agent (20个)
│   ├── 情绪Agent (20个)
│   ├── 风险管理Agent (15个)
│   └── 时机Agent (15个)
├── 决策生成器
│   ├── 工具级别决策
│   ├── 策略仿真
│   └── 自主迭代
└── 输出格式化
    ├── EXECUTE/WAIT
    ├── 置信度评分
    └── 建议参数
```

### 4.2 决策流程
```
用户/系统请求
     ↓
MiroFish决策引擎
     ↓
100智能体共识投票
     ↓
统计 + 加权
     ↓
决策输出 (EXECUTE/WAIT)
     ↓
置信度评分
     ↓
推荐参数 (仓位/止损/止盈/杠杆)
```

### 4.3 工具级别决策示例
```python
# 打兔子买入决策
POST /api/mirofish/decide/rabbit/buy
{
  "symbol": "BTC",
  "entry_price": 67000,
  "trend_score": 0.72,
  "confidence": 0.75,
  "stop_loss": 0.05,
  "take_profit": 0.08
}

# 返回
{
  "tool": "rabbit",
  "action": "buy",
  "mirofish_consensus": {
    "total_agents": 100,
    "votes": {"BUY": 65, "SELL": 15, "HOLD": 20},
    "consensus_score": 0.72
  },
  "decision": "EXECUTE",
  "confidence": 0.78,
  "recommended_position": 0.25,
  "expert_mode": {
    "leverage": 1,
    "conditional_entry": true
  }
}
```

---

## 五、ML Hub (7大模块)

### 5.1 模块清单
```
ML Hub
├── quant_engine           量化引擎 (因子分析/信号生成)
├── strategy_optimizer    策略优化 (Bayes/遗传/网格)
├── predictor           预测引擎 (价格/趋势/波动率)
├── airdrop_hunter     空投猎手 (只读安全)
├── compute_scheduler    算力调度 (GPU/CPU/内存)
├── win_rate           胜率预测 (MonteCarlo)
└── crowdsignal        众包信号 (Twitter/Polymarket/KOL)
```

### 5.2 自主迭代中的角色
```
自主迭代闭环:
┌──────────────────────────────────────┐
│           ML Hub                      │
│                                       │
│  quant_engine ──→ 因子评分            │
│  predictor ─────→ 趋势预测            │
│  strategy_optimizer ─→ 参数优化       │
│  win_rate ───────→ 胜率评估         │
│  compute_scheduler ─→ 算力分配        │
│                                       │
│  ↓ 所有模块输出                       │
│                                       │
│  MiroFish决策引擎                     │
│  ↓                                   │
│  自主迭代建议                         │
└──────────────────────────────────────┘
```

---

## 六、自主迭代闭环

### 6.1 迭代流程
```
┌─────────────────────────────────────────────────────────┐
│                    自主迭代闭环                          │
│                                                          │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐              │
│  │ 数据采集 │ → │ ML分析  │ → │ MiroFish│              │
│  └────┬────┘    └────┬────┘    │ 共识   │              │
│       │              │          └────┬────┘              │
│       │              │              │                   │
│       │         ┌────▼────┐        │                   │
│       │         │ 决策    │ ←──────┘                   │
│       │         └────┬────┘                            │
│       │              │                                 │
│  ┌────▼────────────▼────┐                            │
│  │      执行 → 记录 → 验证 → 优化    │                │
│  └────┬────────────────────┘                            │
│       │                                                 │
│       └───────────────────────────────────────────────┘
│                          ↓
│                    持续迭代
```

### 6.2 迭代触发条件
```python
ITERATION_TRIGGERS = {
    "定时触发": "每2小时自动执行",
    "因子退化": "评分下降>10%",
    "市场异常": "波动率>3σ",
    "策略失效": "胜率下降>15%",
    "手动触发": "用户请求"
}
```

### 6.3 迭代输出
```json
{
  "iteration_id": "iter_20260403_1500",
  "trigger": "scheduled",
  "mirofish_consensus": {...},
  "suggestions": [
    {
      "dimension": "B2_打地鼠",
      "current_score": 65,
      "target_score": 70,
      "action": "优化火控雷达灵敏度",
      "auto_execute": true
    }
  ],
  "weight_adjustments": [...],
  "strategy_updates": [...],
  "execution_results": null,
  "status": "pending_execution"
}
```

---

## 七、北斗七鑫投资体系

### 7.1 工具配置
```json
{
  "rabbit": {
    "weight": 25,
    "strategies": ["趋势跟踪", "突破", "网格"],
    "mirofish_decision": true,
    "ml_optimized": true
  },
  "mole": {
    "weight": 20,
    "strategies": ["火控雷达", "动量", "均值回归"],
    "mirofish_decision": true,
    "ml_optimized": true
  },
  "oracle": {
    "weight": 15,
    "strategies": ["预测市场", "情绪套利", "跨市场"],
    "mirofish_decision": true,
    "ml_optimized": true
  },
  "leader": {
    "weight": 15,
    "strategies": ["做市商", "多空", "信号跟随", "套利"],
    "mirofish_decision": true,
    "ml_optimized": true,
    "external_api": true
  },
  "hitchhiker": {
    "weight": 10,
    "strategies": ["跟单", "分包", "信号聚合"],
    "mirofish_decision": true,
    "ml_optimized": true
  },
  "wool": {
    "weight": 3,
    "strategies": ["空投猎手", "跨链桥", "DeFi农场", "Testnet"],
    "mirofish_decision": false,
    "ml_optimized": true
  },
  "poor_kid": {
    "weight": 2,
    "strategies": ["EvoMap社交", "众包", "技能套利", "推荐网络"],
    "mirofish_decision": false,
    "ml_optimized": true
  }
}
```

---

## 八、25维度全向仿真

### 8.1 维度定义
```
A. 投资组合层
├── A1: 仓位分配 (动态调整能力)
├── A2: 风控规则 (8大规则覆盖度)
└── A3: 多样化 (工具分布合理性)

B. 投资工具层
├── B1: 🐰 打兔子 (策略有效性)
├── B2: 🐹 打地鼠 (火控雷达灵敏度)
├── B3: 🔮 走着瞧 (预测胜率)
├── B4: 👑 跟大哥 (做市收益)
├── B5: 🍀 搭便车 (跟单效果)
├── B6: 💰 薅羊毛 (空投捕获)
└── B7: 👶 穷孩子 (众包收益)

C. 趋势判断层
├── C1: 声纳库 (123模型覆盖)
├── C2: 预言机 (数据源质量)
├── C3: MiroFish (预测准确度)
├── C4: 市场情绪 (情绪准确度)
└── C5: 多智能体共识 (投票质量)

D. 底层资源层
├── D1: 市场数据 (覆盖/延迟)
├── D2: 算力资源 (利用率)
├── D3: 策略引擎 (执行效率)
└── D4: 资金管理 (分配合理性)

E. 运营支撑层
├── E1: 后端API (响应/稳定性)
├── E2: 前端UI (体验/功能)
├── E3: 数据库 (性能/安全)
├── E4: 运维脚本 (覆盖率)
├── E5: 系统稳定性 (MTBF)
└── E6: API延迟 (p99)
```

### 8.2 仿真命令
```bash
cd GO2SE_PLATFORM
python3 scripts/mirofish_full_simulation_v2.py
```

---

## 九、关键文件清单

### 前台
```
frontend/
├── src/components/MiroFish/DecisionPanel.tsx
├── src/components/MiroFish/ConsensusView.tsx
├── src/components/ML/CapabilityGrid.tsx
├── src/hooks/useMiroFish.ts
├── src/hooks/useML.ts
├── src/hooks/useAutoIterate.ts
├── src/stores/mlStore.ts
└── src/stores/mirofishStore.ts
```

### 后台
```
backend/app/
├── routes_ml.py                     # ML能力路由
├── routes_mirofish_decision.py      # MiroFish决策路由 🆕
├── routes_sonar.py                 # 声纳库路由
├── routes_mirofish.py              # MiroFish预测路由
└── ml_core/                       # ML能力中心 🆕
    ├── __init__.py
    ├── ml_hub.py
    ├── quant_engine.py
    ├── strategy_optimizer.py
    ├── predictor.py
    ├── airdrop_hunter.py
    ├── compute_scheduler.py
    ├── win_rate.py
    └── crowdsignal.py
```

### 配置
```
GO2SE_PLATFORM/
├── active_strategy.json             # 策略配置 v8.1
├── BEIDOU_QIXIN_ARCHITECTURE.md   # 架构文档
└── scripts/
    ├── mirofish_full_simulation_v2.py  # 25维度仿真
    └── integrations/                 # 集成模块
        ├── go2se_memory.py
        ├── go2se_context_compression.py
        ├── go2se_subagent_isolation.py
        └── go2se_ralph_persistence.py
```

---

## 十、API完整清单

### MiroFish决策API
| 方法 | 端点 | 功能 |
|------|------|------|
| GET | `/api/mirofish/status` | 引擎状态 |
| POST | `/api/mirofish/decide/<tool>/<action>` | 工具决策 |
| POST | `/api/mirofish/simulate/strategy` | 策略仿真 |
| POST | `/api/mirofish/autonomous/iterate` | 自主迭代 |
| POST | `/api/mirofish/consensus` | 通用共识 |
| POST | `/api/mirofish/batch/decide` | 批量决策 |

### ML API
| 方法 | 端点 | 功能 |
|------|------|------|
| GET | `/api/ml/capabilities` | 能力清单 |
| POST | `/api/ml/quant/factor_analysis` | 多因子分析 |
| POST | `/api/ml/quant/signals` | 批量信号 |
| POST | `/api/ml/predict/price` | 价格预测 |
| POST | `/api/ml/predict/trend` | 趋势预测 |
| POST | `/api/ml/predict/ensemble` | 集成预测 |
| POST | `/api/ml/optimizer/bayesian` | 贝叶斯优化 |
| POST | `/api/ml/optimizer/genetic` | 遗传优化 |
| POST | `/api/ml/airdrop/scan` | 空投资格扫描 |
| POST | `/api/ml/airdrop/calendar` | 空投日历 |
| POST | `/api/ml/compute/status` | 算力状态 |
| POST | `/api/ml/compute/schedule` | 调度计划 |
| POST | `/api/ml/compute/optimize` | 优化建议 |
| POST | `/api/ml/winrate/predict` | 胜率预测 |
| POST | `/api/ml/winrate/combined` | 组合胜率 |
| POST | `/api/ml/crowd/aggregate` | 众包信号 |
| POST | `/api/ml/crowd/polymarket` | 预测市场信号 |

---

**版本: v8.1 | 更新: 2026-04-03 | CEO: GO2SE 🪿**
