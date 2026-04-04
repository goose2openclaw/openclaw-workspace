# MoneyClaw Skill

> 7x24 AI Agent that saves and makes money autonomously

## 来源
- **GitHub**: https://github.com/Qiyd81/moneyclaw-py
- **本地**: `/root/.openclaw/workspace/moneyclaw-py`

## 功能定位

MoneyClaw 是一个专注于**金融优化**的AI Agent，与GO2SE北斗七鑫投资体系高度互补：

| MoneyClaw | GO2SE |
|-----------|--------|
| DCA定投 | 打兔子趋势追踪 |
| 智能再平衡 | 跟大哥做市 |
| 价格告警 | 打地鼠异动 |
| 资金管理 | 搭便车跟单 |
| 加密货币 | 全市场覆盖 |

## 核心策略

### 1. DCA定投 (crypto_dca)
```python
# 位置: strategies/crypto_dca/
# 功能: 定期定额投资
```

### 2. 智能再平衡 (smart_rebalance)
```python
# 位置: strategies/smart_rebalance/
# 功能: 自动再平衡投资组合
```

### 3. 价格告警 (crypto_price_alert)
```python
# 位置: strategies/crypto_price_alert/
# 功能: 价格达到阈值时通知
```

### 4. 资金管理 (crypto_funding)
```python
# 位置: strategies/crypto_funding/
# 功能: 资金流管理
```

## 使用方法

```bash
cd /root/.openclaw/workspace/moneyclaw-py

# 查看策略
ls strategies/

# 运行DCA策略
python3 -m moneyclaw strategies/crypto_dca

# 查看状态
python3 -m moneyclaw status
```

## 与GO2SE集成原则

> ⚠️ **核心原则**: MoneyClaw策略是**补充集成**，不是替换映射。
> 所有外部策略按照权重参与GO2SE原生策略，形成组合决策。

### 集成权重示例

```
最终决策 = GO2SE原生策略 × 权重 + MoneyClaw策略 × 权重 + 趋势模型 × 权重

打兔子最终信号 = 
  原生打兔子(0.6) + DCA定投(0.2) + 趋势模型组合(0.2)

打地鼠最终信号 = 
  原生打地鼠(0.5) + 价格告警(0.25) + 资金费率(0.15) + 火控雷达(0.1)

走着瞧最终信号 = 
  原生走着瞧(0.4) + 预测市场(0.3) + MiroFish共识(0.3)

跟大哥最终信号 = 
  原生跟大哥(0.5) + 智能再平衡(0.3) + MiroFish评估(0.2)
```

### 打工工具独立

**注意**: 💰薅羊毛和👶穷孩子是**打工工具**，独立于MoneyClaw：

- 💰 薅羊毛 → 空投/任务平台 (用算力换钱)
- 👶 穷孩子 → EvoMap众包 (用技能换钱)

## 依赖
- Python 3.12+
- ccxt>=4.4
- httpx>=0.28
- fastapi>=0.115

## 文件结构
```
moneyclaw-py/
├── moneyclaw/          # 核心代码
│   ├── agent/          # Agent逻辑
│   ├── llm/            # LLM路由
│   └── plugins/        # 插件系统
├── strategies/         # 交易策略
│   ├── crypto_dca/     # DCA定投
│   ├── smart_rebalance/ # 智能再平衡
│   └── crypto_price_alert/ # 价格告警
└── tests/             # 测试
```
