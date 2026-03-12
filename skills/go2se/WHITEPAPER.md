# 🪿 GO2SE 赚钱工具白皮书

**版本**: 1.0  
**更新**: 2026-03-12  
**状态**: 可用

---

## 一句话

GO2SE 是一款通过 **AI 量化工具** 帮你赚钱的系统：打兔子、打地鼠、撸空投、预测市场、跟单分钱。

---

## 赚钱方式

### 🐰 1. 打兔子 (主流币)

```
策略: 主流币策略 (mainstream_strategy.py)

盈利方式:
- BTC/ETH/SOL 趋势交易
- RSI/MACD/均线 信号
- 稳健止损止盈

预期收益: 5-15%/月
风险: ⭐⭐ (低)
```

### 🐹 2. 打地鼠 (山寨币)

```
策略: 打地鼠策略 (mole_strategy.py)

盈利方式:
- 跨交易所价差套利
- 成交量异常检测
- 快速买卖信号

预期收益: 10-30%/月
风险: ⭐⭐⭐ (中)
```

### 🎯 3. 撸空投 (新币)

```
策略: 空投猎手 (airdrop_hunter.py)

盈利方式:
- DEX 新币监控
- 空投潜力评分 (0-10分)
- 蜜罐检测 + 零Approval

预期收益: 不确定 (高风险高回报)
风险: ⭐⭐⭐⭐ (高)
```

### 🔮 4. 预测市场

```
策略: Polymarket 套利 (polymarket_arb.py)

盈利方式:
- 数学套利检测
- 概率不匹配机会
- 事件预测交易

预期收益: 5-20%/月
风险: ⭐⭐ (中低)
```

### 👥 5. 跟单分成

```
策略: 做市商联盟 (market_maker_alliance.py)

盈利方式:
- 跟随顶级交易员
- 自动分成收益
- 无需自己分析

预期收益: 20-50%/月
风险: ⭐⭐⭐ (中)
```

---

## 工具列表

### 🎯 赚钱工具

| 工具 | 脚本 | 收益预期 | 风险 |
|------|------|----------|------|
| 打兔子 | mainstream_strategy.py | 5-15%/月 | 低 |
| 打地鼠 | mole_strategy.py | 10-30%/月 | 中 |
| 撸空投 | airdrop_hunter.py | 不确定 | 高 |
| 预测套利 | polymarket_arb.py | 5-20%/月 | 中低 |
| 跟单分成 | market_maker_alliance.py | 20-50%/月 | 中 |

### 🛠️ 辅助工具

| 工具 | 功能 |
|------|------|
| dashboard.py | 仪表板总览 |
| risk_manager.py | 风险管理 |
| portfolio_manager.py | 组合管理 |
| trading_journal.py | 交易记录 |
| performance_optimizer.py | 性能优化 |
| backtest_engine.py | 回测 |
| advanced_signals.py | 多源信号 |

---

## 使用方法

### 快速开始

```bash
cd /root/.openclaw/workspace/skills/go2se/scripts

# 1. 查看仪表板
python3 dashboard.py

# 2. 运行打兔子
python3 mainstream_strategy.py

# 3. 运行打地鼠
python3 mole_strategy.py

# 4. 扫描空投
python3 airdrop_hunter.py 5.0

# 5. Polymarket套利
python3 polymarket_arb.py 2.0

# 6. 跟单分成
python3 market_maker_alliance.py on
python3 market_maker_alliance.py
```

---

## 策略详解

### 🐰 打兔子 (主流币)

```python
# 运行
python3 mainstream_strategy.py

# 逻辑
- 监控 BTC/ETH/SOL/BNB
- 技术指标: RSI, MACD, 均线
- 趋势确认后买入
- 止损 3%, 止盈 8%
```

### 🐹 打地鼠 (山寨币)

```python
# 运行
python3 mole_strategy.py

# 逻辑
- 扫描多个交易所
- 发现价差 > 2%
- 快速买入/卖出
- 止盈 5-20%
```

### 🎯 撸空投

```python
# 运行
python3 airdrop_hunter.py 5.0

# 分数 > 7: 强烈建议
# 分数 5-7: 建议关注
# 分数 < 5: 观望

# 风险控制
- ❌ 严禁 Approval
- ✅ 零授权
- ⛽ Gas < 50 gwei
- 💰 单笔 < $50
```

### 🔮 预测市场

```python
# 运行
python3 polymarket_arb.py 2.0

# 逻辑
- 抓取 Polymarket 数据
- 检测概率不匹配
- 套利机会 > 2%
```

---

## 风险控制

### 通用规则

| 规则 | 限制 |
|------|------|
| 最大持仓 | 5个 |
| 单日交易 | 10笔 |
| 最大回撤 | 10% |

### 空投专用

```
- ❌ 严禁 Approval (零授权)
- ✅ 使用 Safe Wallet
- ⛽ Gas 限制: 50 gwei
- 💰 单笔限额: $50
```

---

## Cron 自动任务

| 任务 | 间隔 | 功能 |
|------|------|------|
| mainstream | 30分钟 | 打兔子 |
| mole | 15分钟 | 打地鼠 |
| airdrop | 30分钟 | 撸空投 |
| pm-arbitrage | 30分钟 | 预测套利 |

---

## 预期收益

### 保守估计

| 策略 | 资金 | 月收益 |
|------|------|----------|
| 打兔子 | $10K | $500-1500 |
| 打地鼠 | $10K | $1000-3000 |
| 撸空投 | $1K | 不确定 |
| 预测市场 | $10K | $500-2000 |
| 跟单分成 | $10K | $2000-5000 |

---

## 快速命令汇总

```bash
# 核心赚钱
python3 mainstream_strategy.py   # 打兔子
python3 mole_strategy.py        # 打地鼠
python3 airdrop_hunter.py 5.0  # 撸空投
python3 polymarket_arb.py 2.0  # 预测套利

# 跟单
python3 market_maker_alliance.py on  # 开启跟单

# 工具
python3 dashboard.py             # 仪表板
python3 risk_manager.py          # 风控
python3 backtest_engine.py 10000 30 BTC  # 回测
```

---

## ⚠️ 风险提示

1. 加密货币高风险
2. 过去收益不代表未来
3. 空投风险极高
4. 跟单有亏损可能
5. 请用闲散资金

---

## 文件结构

```
skills/go2se/
├── scripts/
│   ├── mainstream_strategy.py   # 打兔子
│   ├── mole_strategy.py        # 打地鼠
│   ├── airdrop_hunter.py     # 撸空投
│   ├── polymarket_arb.py      # 预测套利
│   ├── market_maker_alliance.py # 跟单
│   └── ... (40+ 脚本)
├── data/
└── *.md
```

---

**🪿 GO2SE - 帮你赚钱的 AI 工具**

© 2026 GO2SE
