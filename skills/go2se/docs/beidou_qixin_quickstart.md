# 北斗七鑫系统 - 快速入门指南

## 一、系统架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         北斗七鑫 - 智能投资系统                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  🚀 五大投资行为                                                          │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │ 🐰 打兔子    │ 🐹 打地鼠    │ 🔮 走着瞧    │ 👑 跟大哥   │ 🍀 搭便车   │ │
│  │  (Top20)    │  (其他币)    │ (预测市场)    │ (做市协调)  │ (跟单分成)  │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  💰 二大赚钱活动                                                          │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │ �羊毛 薅羊毛     │ 📦 众包                                            │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  🧠 核心决策引擎                                                         │
│  • 趋势分析 → 信号生成 → 策略匹配 → 风险控制 → 执行                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 二、快速开始

### 1. 初始化系统

```python
from skills.go2se.scripts.beidou_qixin import BeidouQixinSystem

# 选择模式: conservative(保守) / balanced(平衡) / aggressive(激进)
system = BeidouQixinSystem(mode='balanced', total_capital=10000)
```

### 2. 运行决策周期

```python
result = system.run_cycle()
```

### 3. 查看结果

```python
# 组合状态
print(f"总资金: ${system.total_capital}")
print(f"备用金: ${system.reserved_capital}")
print(f"持仓数: {len(system.positions)}")
```

---

## 三、三种模式配置

### 保守模式 (conservative)
```python
{
    'scan_interval': 120,          # 扫描间隔
    'confidence_threshold': 0.7,   # 置信度
    'max_position': 0.08,          # 最大仓位
    'stop_loss': 0.02,            # 止损
    'take_profit': 0.05,          # 止盈
    'reserved_funds': 0.20,       # 备用金
    
    # 资金分配
    'rabbit': 0.70,               # 打兔子 70%
    'mole': 0.10,                 # 打地鼠 10%
    'prediction': 0.05,            # 走着瞧 5%
    'follow': 0.10,               # 跟大哥 10%
    'hitchhike': 0.05             # 搭便车 5%
}
```

### 平衡模式 (balanced) - 推荐
```python
{
    'scan_interval': 60,
    'confidence_threshold': 0.6,
    'max_position': 0.10,
    'stop_loss': 0.03,
    'take_profit': 0.08,
    'reserved_funds': 0.10,
    
    'rabbit': 0.50,
    'mole': 0.20,
    'prediction': 0.10,
    'follow': 0.10,
    'hitchhike': 0.10
}
```

### 激进模式 (aggressive)
```python
{
    'scan_interval': 30,
    'confidence_threshold': 0.5,
    'max_position': 0.15,
    'stop_loss': 0.05,
    'take_profit': 0.15,
    'reserved_funds': 0.05,
    
    'rabbit': 0.30,
    'mole': 0.35,
    'prediction': 0.15,
    'follow': 0.10,
    'hitchhike': 0.10
}
```

---

## 四、可调参数范围

| 参数 | 最小值 | 最大值 | 默认值 |
|------|--------|--------|--------|
| 扫描间隔 | 30秒 | 300秒 | 60秒 |
| 置信度阈值 | 0.3 | 0.9 | 0.6 |
| 最大仓位 | 1% | 30% | 10% |
| 止损 | 1% | 10% | 3% |
| 止盈 | 5% | 30% | 8% |
| 备用金 | 5% | 30% | 10% |

---

## 五、投资行为说明

| 行为 | 目标 | 风险 | 策略 |
|------|------|------|------|
| 🐰 打兔子 | 市值前20 | 低 | 动量 |
| 🐹 打地鼠 | 其他币种 | 高 | 突破 |
| 🔮 走着瞧 | 预测市场 | 中 | 情绪 |
| 👑 跟大哥 | 做市协调 | 中 | 跟单 |
| 🍀 搭便车 | 复制交易 | 低 | 复制 |

---

## 六、核心文件

```
skills/go2se/
├── scripts/
│   ├── beidou_qixin.py              # 核心系统
│   ├── ultimate_dual_track.py       # 增强版双轨
│   ├── enhanced_dual_track.py      # 回测观测版
│   └── multi_track_spider.py       # 多轨道扫描
│
├── docs/
│   ├── beidou_qixin_system.md      # 系统架构
│   ├── spider_expert_analysis.md   # 专家分析
│   └── enhanced_dual_track_analysis.md
│
└── data/
    └── config.json                  # 配置文件
```

---

## 七、决策流程

```
市场扫描 → 异常检测 → 趋势分析 → 投资分类
     ↓                              ↓
  置信度计算 ──────────────────→ 策略匹配
     ↓                              ↓
  风险检查 ← ────────────────── 仓位计算
     ↓
  执行买入/卖出/持有
```

---

## 八、运行示例

```python
# 初始化平衡模式
system = BeidouQixinSystem(mode='balanced', total_capital=10000)

# 运行决策周期
result = system.run_cycle()

# 输出示例:
# 📡 扫描市场...
#    发现 25 交易对异常
#    BTC/USDT: BUY (置信度: 85%)
#    ETH/USDT: HOLD (置信度: 45%)
# 📊 持仓检查:
# 📈 组合状态:
#    总资金: $10,000.00
#    备用金: $1,000.00
#    持仓数: 2
```

---

**版本**: v1.0
**更新时间**: 2026-03-15
