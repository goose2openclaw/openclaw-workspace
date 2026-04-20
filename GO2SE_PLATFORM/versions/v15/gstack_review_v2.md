# v15 gstack Code Review v2
## 时间: 2026-04-20 16:23 GMT+8

---

## gstack Issues (v15 Decision Engine)

| ID | 问题 | 严重度 | 状态 |
|----|------|--------|------|
| M3 | AdaptiveBrainWeights未集成到Mi计算 | HIGH | 待修复 |
| R1 | RSI风险在Mi归一化和Ri中重复计算 | MED | 待修复 |
| O1 | SHORT position_pct缺乏独立公式 | MED | 待修复 |

## Strengths

- 无注入风险 - 所有参数白名单
- 数学严谨: 有界、有单位
- Mi归一化: 25D加权到[0.5, 1.5]
- Ri动态: regime x RSI x 波动率
- B1_rabbit最高权重(0.06) - 反映真实缺陷

## MiroFish 25D 迭代结果

| 维度 | 当前 | 改进后 | 提升 |
|------|------|--------|------|
| Overall | 93.50 | ~94.5 | +1.0 |
| Mi乘数 | 1.2000 | 1.2000 | 0 |

## 待实施修复

1. 将AdaptiveBrainWeights (WIN/LOSS/streak) 集成到Mi计算
2. 重构Ri避免RSI重复计算
3. SHORT position_pct独立公式
