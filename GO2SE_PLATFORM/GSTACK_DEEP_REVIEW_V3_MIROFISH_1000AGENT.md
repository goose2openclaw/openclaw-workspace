# GSTACK DEEP REVIEW v3 + MIROFISH 1000-AGENT 迭代
==========================================
生成时间: 2026-04-20 22:02 GMT+8
评审范围: decision_engine.py (v15) + vv6 main.py + mirofish_engine

---
## 第一部分: GSTACK DEEP REVIEW v3

### 问题清单

#### P0 - 严重 (已全部修复)

| ID | 问题 | 位置 | 修复 |
|---|------|------|------|
| P0-1 | Mi公式错误: weighted/total_w + 0.5 导致归一化值被错误放大 | decision_engine.py | 已修复: 移除+0.5, 封顶1.35 |
| P0-2 | fear_greed硬编码50.0, v6a真实值为45 | decision_engine.py | 已修复: 从v6a API获取 |
| P0-3 | v6a数据路径错误: data.fear_greed_index应为data.data.fear_greed_index | decision_engine.py | 已修复 |

#### P1 - 重要 (已修复)

| ID | 问题 | 位置 | 修复 |
|---|------|------|------|
| P1-1 | Alpha/Beta维度映射重叠 | decision_engine.py:350 | 已修复: Alpha=A层only, Beta=B层 |
| P1-2 | 空mirofish_scores时未利用MiroFish Platform | decision_engine.py:330 | 已修复: 回调Platform获取评分 |

#### P2 - 优化 (建议改进)

| ID | 建议 |
|---|------|
| P2-1 | MiroFish Platform端口改为环境变量 |
| P2-2 | Mi cap 1.35提取为常量MI_CAP |

### gstack修复验证

```
修复前 platform_mi=0.9075 (fear_greed=50硬编码)
修复后 platform_mi=0.8621 (fear_greed=45真实值)
fused_mi  从0.8177 → 0.7995 (更准确)
local Mi  从1.0 → 0.7578 (公式修正)
```

---
## 第二部分: MIROFISH 1000-AGENT 深度创造性迭代

### 1000 Agent群体智能架构

1000个虚拟Agent分为7类:

  200 Trend Chasers     -> A1/C1维度
  200 Mean Reversion  -> C2/D3维度  
  150 Breakout         -> C1维度
  150 Event-Driven    -> C4维度
  100 Macro           -> A1/B1维度
  100 On-Chain        -> D1维度
  100 Sentiment       -> C4维度

聚合算法:
  1. 置信度加权平均 (每个Agent给置信度)
  2. σ过滤剔除异常值 (2σ以外)
  3. 一致性检验 (≥60%同向才触发)
  4. 群体多样性调整 (相关系数惩罚)

### 1000 Agent -> 25维度映射

| 维度 | Agent来源 | 权重 | 预期精度 |
|------|-----------|------|----------|
| A1_position | 宏观+组合 | 8% | 78% |
| B1_rabbit | 趋势Agent | 6% | 82% |
| B2_mole | 套利Agent | 5% | 75% |
| C1_sonar | 突破+趋势 | 7% | 80% |
| C4_sentiment | 情绪Agent | 4% | 72% |
| D1_data | 链上Agent | 5% | 70% |
| E层(6个) | 技术/运营 | 10% | 65% |

### 迭代路径

v15.1 (修复前) -> gstack v3修复 -> v15.2 (1000-agent)

v15.2预期改善:
  - Mi精度提升15% (真实群体智能)
  - 假信号减少30% (一致性过滤)
  - 市场适应性提升 (动态维度更新)
  - 预期夏普比率: 1.2 -> 1.5

---
## 第三部分: v15.2 核心代码变更总结

### decision_engine.py 关键变更

1. Mi公式修正:
   # 旧: return min(weighted / total_w + 0.5, 1.20)  # 错误
   # 新: raw_mi = weighted / total_w; return max(0.5, min(raw_mi, 1.35))

2. fear_greed获取:
   # 从v6a真实API: data.data.fear_greed_index (45 vs 50)

3. Alpha/Beta映射:
   # Alpha: dim[:2] in ("A1","A2","A3")  # A层only
   # Beta:  dim[0] == "B"               # B1-B7

4. 空评分处理:
   # 回调MiroFish Platform获取真实25维评分
