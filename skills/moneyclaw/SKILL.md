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

## 与GO2SE集成

MoneyClaw策略是**投资/理财工具**，对应GO2SE投资工具层：

| MoneyClaw策略 | GO2SE投资工具 | 说明 |
|---------------|---------------|------|
| crypto_dca (DCA定投) | 🐰 打兔子 | 长期定投主流资产 |
| smart_rebalance (智能再平衡) | 👑 跟大哥 | 组合再平衡 |
| crypto_price_alert (价格告警) | 🐹 打地鼠 | 机会发现/告警 |
| crypto_funding (资金费率) | 🔮 走着瞧 | 预测市场辅助 |

### 打工工具独立

**注意**: 💰薅羊毛和👶穷孩子是**打工工具**，不与MoneyClaw集成：

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
