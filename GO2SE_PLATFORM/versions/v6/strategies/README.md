# 🪿 GO2SE 北斗七鑫策略模块

## 策略列表

| 策略 | 文件 | 功能 |
|------|------|------|
| 🐰 打兔子 | `rabbit/rabbit_strategy.py` | Top20趋势追踪 |
| 🐹 打地鼠 | `mole/mole_strategy.py` | 高波动套利 |
| 🔮 走着瞧 | `oracle/oracle_strategy.py` | 预测市场 |
| 👑 跟大哥 | `leader/leader_strategy.py` | 做市协作 |
| 🍀 搭便车 | `hitchhiker/hitchhiker_strategy.py` | 跟单分成 |
| 💰 薅羊毛 | `airdrop/airdrop_strategy.py` | 新币空投 |
| 👶 穷孩子 | `crowdsource/crowdsource_strategy.py` | 众包任务 |
| 🧠 核心引擎 | `core/expert_engine.py` | 专家模式 |

## 使用方法

```python
from core.expert_engine import ExpertEngine

# 初始化引擎
engine = ExpertEngine()

# 运行分析
analysis = engine.analyze_market()

# 获取建议
recommendation = analysis['final_recommendation']

# 执行交易
result = engine.execute_trade(recommendation)
```

## 策略算力分配

```
rabbit:      25%  (打兔子)
mole:       20%  (打地鼠)
oracle:     15%  (走着瞧)
leader:     15%  (跟大哥)
hitchhiker: 10%  (搭便车)
airdrop:     3%  (薅羊毛)
crowdsource: 2%  (穷孩子)
```

## 置信度评分

| 分数 | 级别 | 建议 |
|------|------|------|
| 0-3 | 🔴 高风险 | 禁止开仓 |
| 4-5 | 🟡 中风险 | 谨慎观望 |
| 6-7 | 🟢 正常 | 适度参与 |
| 8-10 | ⭐ 机会 | 积极做多 |

## 版本

v1.0 - 2026-03-17
