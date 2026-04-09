# 🪿 Go2Se 投资决策核心逻辑

## 完整决策链路图

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                          🪿 Go2Se 智能投资决策系统                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘

                              ┌──────────────────┐
                              │  声纳趋势检测    │
                              │  (Sonar)        │
                              └────────┬─────────┘
                                       │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
             ┌──────────┐      ┌──────────┐      ┌──────────┐
             │ bullish  │      │ neutral  │      │ bearish  │
             │  牛市   │      │  中性   │      │  熊市   │
             └────┬─────┘      └────┬─────┘      └────┬─────┘
                  │                 │                 │
                  ▼                 ▼                 ▼
         ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
         │ 策略组合A   │ │ 策略组合B   │ │ 策略组合C   │
         │ • trend    │ │ • grid     │ │ • grid     │
         │ • breakout │ │ • dca      │ │ • dca      │
         │ • ma_back │ │ • arbitrage│ │ • mm      │
         └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
               │               │               │
               ▼               ▼               ▼
        ┌─────────────────────────────────────────────────────┐
        │              投资组合配置                            │
        │  ┌─────────┬─────────┬─────────┬─────────┐         │
        │  │  BTC   │  ETH   │  SOL   │  USDT  │         │
        │  │  40%   │  30%   │  20%   │  10%   │         │
        │  └─────────┴─────────┴─────────┴─────────┘         │
        └─────────────────────┬───────────────────────────────┘
                              │
                              ▼
               ┌──────────────────────────────────┐
               │         工具组合执行              │
               │  ┌──────┐ ┌──────┐ ┌──────┐  │
               │  │🐰打兔│ │🐹打鼠│ │👀走着│  │
               │  │ 子  │ │ 子  │ │   瞧│  │
               │  └──────┘ └──────┘ └──────┘  │
               └────────────────────┬─────────────┘
                                     │
                                     ▼
                           ┌─────────────────┐
                           │   最终决策      │
                           │  BUY/HOLD/SELL │
                           └─────────────────┘
```

---

## 核心公式

```
决策 = f(声纳趋势, 策略组合, 投资组合, 工具组合)

其中:
- 声纳趋势 = Σ(模型信号 × 准确度权重)
- 策略组合 = top_k(趋势匹配策略)
- 投资组合 = 策略权重 × 风险偏好
- 工具组合 = 策略 → 工具映射
- 最终决策 = 加权投票(BUY/SELL/HOLD)
```

---

## 声纳 → 策略 映射表

| 声纳趋势 | 推荐策略 | 权重 | 风险 |
|---------|---------|------|------|
| bullish | trend, breakout, ma_pullback | 0.5-0.7 | 高 |
| neutral | grid, dca, arbitrage | 0.3-0.5 | 中 |
| bearish | grid, dca, market_maker | 0.1-0.3 | 低 |

---

## 策略 → 工具 映射

| 策略 | 工具 | 名称 | 图标 |
|------|------|------|------|
| trend | da_tu_zi | 打兔子 | 🐰 |
| breakout | da_di_shu | 打地鼠 | 🐹 |
| ma_pullback | da_tu_zi | 打兔子 | 🐰 |
| grid | da_di_shu | 打地鼠 | 🐹 |
| dca | da_tu_zi | 打兔子 | 🐰 |
| arbitrage | da_di_shu | 打地鼠 | 🐹 |
| copy | da_bian_che | 搭便车 | 🚗 |
| mm | gen_da_ge | 跟大哥 | 🤝 |

---

## 投资组合示例

### 牛市配置 (bullish)
```json
{
  "BTC": {"strategy": "trend", "allocation": 0.4},
  "ETH": {"strategy": "breakout", "allocation": 0.3},
  "SOL": {"strategy": "ma_pullback", "allocation": 0.2},
  "USDT": {"allocation": 0.1, "strategy": "cash"}
}
```

### 中性配置 (neutral)
```json
{
  "BTC": {"strategy": "grid", "allocation": 0.3},
  "ETH": {"strategy": "dca", "allocation": 0.3},
  "SOL": {"strategy": "arbitrage", "allocation": 0.2},
  "USDT": {"allocation": 0.2, "strategy": "cash"}
}
```

### 熊市配置 (bearish)
```json
{
  "BTC": {"strategy": "grid", "allocation": 0.2},
  "ETH": {"strategy": "dca", "allocation": 0.2},
  "USDT": {"allocation": 0.6, "strategy": "cash"}
}
```

---

## 回测指标

| 指标 | 目标值 | 实际值 |
|------|--------|---------|
| 总收益 | >20% | 55.93% |
| 胜率 | >60% | 76.7% |
| 夏普率 | >1.5 | 2.69 |
| 最大回撤 | <20% | 9.8% |

---

## 决策流程伪代码

```python
def decision_chain():
    # 1. 声纳趋势检测
    trend = detect_sonar_trend()
    
    # 2. 策略选择
    strategies = select_strategies(trend)
    
    # 3. 投资组合
    portfolio = build_portfolio(strategies)
    
    # 4. 工具匹配
    tools = map_tools(strategies)
    
    # 5. 最终决策
    decision = voting(strategies)
    
    return {
        'trend': trend,
        'strategies': strategies,
        'portfolio': portfolio,
        'tools': tools,
        'decision': decision
    }
```

---

_更新于: 2026.03.14_
