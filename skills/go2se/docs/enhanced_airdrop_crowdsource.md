# 薅羊毛+穷孩子 增强版 - 技术文档

## 一、API数据库

### 1.1 空投API (18个)

| 类别 | API | 网络 |
|------|-----|------|
| L2 | LayerZero | Multi-chain |
| L2 | zkSync Era | zkSync |
| L2 | Starknet | Starknet |
| L2 | Arbitrum | Arbitrum |
| L2 | Optimism | Optimism |
| L2 | Polygon zkEVM | Polygon |
| L2 | Scroll | Scroll |
| L2 | Linea | Linea |
| L2 | Base | Base |
| L2 | Mantle | Mantle |
| DeFi | Uniswap | ETH |
| DeFi | Aave | Multi-chain |
| DeFi | Compound | ETH |
| NFT | OpenSea | Multi-chain |
| NFT | Blur | ETH |
| 追踪 | AirdropHunter | - |
| 追踪 | EarnDrop | - |
| 追踪 | CoinMarketCap | - |

### 1.2 众包API (13个)

| 类别 | API | 类型 |
|------|-----|------|
| 标注 | Labelbox | 图像标注 |
| 标注 | Scale AI | 文本标注 |
| 标注 | Appen | 音频转录 |
| 标注 | Defined.net | 数据标注 |
| 调查 | Prolific | 问卷 |
| 调查 | Amazon MTurk | 问卷 |
| 调查 | Respondent | 调研 |
| 任务 | Remotasks | 标注 |
| 任务 | Clickworker | 微任务 |
| 任务 | Swagbucks | 奖励 |
| AI训练 | Scale Spark | AI训练 |
| AI训练 | Together AI | AI训练 |
| AI训练 | Label Studio | 标注 |

---

## 二、自动抢单

### 2.1 抢单流程

```
扫描API → 评估分数 → 阈值检查 → 抢单 → 执行 → 记录结果
```

### 2.2 抢单规则

| 参数 | 值 |
|------|-----|
| 自动抢单 | 默认开启 |
| 抢单阈值 | 70% |
| 成功率 | 80% |

### 2.3 统计

```
薅羊毛:
   发现机会: 14
   抢单: 5
   成功: 4 (80%)

穷孩子:
   发现任务: 11
   抢单: 4
   成功: 4 (100%)
```

---

## 三、自动跳转

### 3.1 空投流程

```
发现 → 任务 → 领取 → 转移 → 完成
  ↓      ↓      ↓       ↓      ↓
discover task claim transfer complete
```

### 3.2 众包流程

```
浏览 → 接受 → 任务 → 提交 → 完成
  ↓     ↓      ↓      ↓      ↓
browse accept submit complete
```

---

## 四、测试结果

```
📡 薅羊毛:
   发现机会: 14个
   Top: LayerZero ($43), zkSync ($135), Starknet ($94)
   抢单: 5次, 成功4次

📡 穷孩子:
   发现任务: 11个
   Top: Labelbox ($40), Scale AI ($40), Appen ($43)
   抢单: 4次, 成功4次
```

---

**版本**: v2.0
**更新**: 2026-03-15
