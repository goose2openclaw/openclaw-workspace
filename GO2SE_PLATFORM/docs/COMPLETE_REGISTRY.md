# GO2SE 北斗七鑫 完整注册表

> 更新: 2026-04-04

## 权重系统总览

| 类型 | 数量 | 总权重占比 |
|------|------|-----------|
| 技能 | 28 | 40% |
| 策略 | 14 | 60% |

### 综合权重分布 (Top 15)

| 排名 | 名称 | 类型 | 综合权重 |
|------|------|------|----------|
| 1 | MiroFish共识 | strategy | 9.24% |
| 2 | Rabbit V2 | strategy | 8.01% |
| 3 | Rabbit | strategy | 5.40% |
| 4 | Oracle预测 | strategy | 4.73% |
| 5 | Mole | strategy | 4.43% |
| 6 | Mole V2 | strategy | 4.29% |
| 7 | 声纳库 | strategy | 4.08% |
| 8 | Leader V2 | strategy | 3.86% |
| 9 | MoneyClaw | skill | 3.47% |
| 10 | Trading Brain | skill | 3.31% |
| 11 | 信号优化器 | strategy | 3.25% |
| 12 | DCA定投 | strategy | 3.03% |
| 13 | 智能再平衡 | strategy | 2.81% |
| 14 | Polymarket | skill | 2.76% |
| 15 | Binance现货 | skill | 2.60% |

---

## 一、技能注册表 (28个)

### 1. 交易所连接 (4个) - 权重: 33%

| ID | 名称 | 路径 | 基准权重 |
|----|------|------|----------|
| binance_spot | Binance现货 | skills/binance-spot-trading | 0.12 |
| binance_grid | Binance网格 | skills/binance-grid-trading | 0.08 |
| okx_spot | OKX现货 | skills/okx-spot-trading | 0.08 |
| bybit_spot | Bybit现货 | skills/bybit-spot-trading | 0.05 |

### 2. 量化AI (8个) - 权重: 70%

| ID | 名称 | 路径 | 基准权重 |
|----|------|------|----------|
| trading_brain | Trading Brain | skills/trading-brain | 0.15 |
| quant_system | Quant系统 | skills/quant-trading-system | 0.12 |
| trading_agents | Trading Agents | skills/trading-agents | 0.10 |
| crypto_trading_bot | Crypto交易Bot | skills/crypto-trading-bot | 0.08 |
| rho_signals | Rho信号 | skills/rho-signals | 0.08 |
| trading_assistant | 交易助手 | skills/trading-assistant | 0.06 |
| openclaw_quant | OpenClaw Quant | skills/openclaw-quant-skill | 0.06 |
| trading_devbox | 交易开发箱 | skills/trading-devbox | 0.05 |

### 3. 预测市场 (2个) - 权重: 20%

| ID | 名称 | 路径 | 基准权重 |
|----|------|------|----------|
| polymarket | Polymarket | skills/polymarket-bot | 0.12 |
| polymarket_arbitrage | Polymarket套利 | skills/polymarket-arbitrage | 0.08 |

### 4. 外部金融 (1个) - 权重: 15%

| ID | 名称 | 路径 | 基准权重 |
|----|------|------|----------|
| moneyclaw | MoneyClaw | skills/moneyclaw | 0.15 |

### 5. Agent (1个) - 权重: 10%

| ID | 名称 | 路径 | 基准权重 |
|----|------|------|----------|
| hermes | Hermes Agent | hermes-agent | 0.10 |

### 6. 记忆/知识 (2个) - 权重: 16%

| ID | 名称 | 路径 | 基准权重 |
|----|------|------|----------|
| agentbrain | AgentBrain | skills/agentbrain | 0.08 |
| rag | RAG引擎 | backend/app/core/rag_engine.py | 0.08 |

### 7. 股票分析 (5个) - 权重: 20%

| ID | 名称 | 路径 | 基准权重 |
|----|------|------|----------|
| agent_stock | 股票Agent | skills/agent-stock | 0.05 |
| akshare_stock | AKShare A股 | skills/akshare-stock | 0.04 |
| china_stock_analysis | A股分析 | skills/china-stock-analysis | 0.04 |
| stock_analysis | 股票分析 | skills/stock-analysis | 0.04 |
| stock_watcher | 股票监视 | skills/stock-watcher | 0.03 |

### 8. 众包/数据 (2个) - 权重: 11%

| ID | 名称 | 路径 | 基准权重 |
|----|------|------|----------|
| evomap | EvoMap众包 | skills/evomap-tools | 0.06 |
| data_analysis | 数据分析 | skills/data-analysis | 0.05 |

### 9. 工具类 (3个) - 权重: 13%

| ID | 名称 | 路径 | 基准权重 |
|----|------|------|----------|
| gstack_browse | gstack浏览 | skills/gstack-browse | 0.05 |
| gstack_investigate | gstack调查 | skills/gstack-investigate | 0.04 |
| gstack_retro | gstack复盘 | skills/gstack-retro | 0.04 |

---

## 二、策略注册表 (14个)

### 北斗七鑫工具映射

| 工具 | 策略 | 胜率 | 夏普 | 权重 |
|------|------|------|------|------|
| 🐰 打兔子 | Rabbit V2 | 72% | 1.85 | 8.01% |
| 🐰 打兔子 | Rabbit | 68% | 1.65 | 5.40% |
| 🐰 打兔子 | DCA定投 | 75% | 1.92 | 3.03% |
| 🐹 打地鼠 | Mole V2 | 65% | 1.45 | 4.29% |
| 🐹 打地鼠 | Mole | 62% | 1.32 | 4.43% |
| 🐹 打地鼠 | 价格告警 | 65% | 1.40 | - |
| 🔮 走着瞧 | Oracle预测 | 70% | 1.55 | 4.73% |
| 🔮 走着瞧 | 资金费率套利 | 68% | 1.55 | - |
| 👑 跟大哥 | Leader V2 | 68% | 1.50 | 3.86% |
| 👑 跟大哥 | Leader | 60% | 1.28 | - |
| 👑 跟大哥 | 智能再平衡 | 72% | 1.80 | 2.81% |
| 🍀 搭便车 | 信号优化器 | 75% | 1.90 | 3.25% |
| 🛡️ 风控 | 声纳库 | 70% | 1.70 | 4.08% |
| 🔮 MiroFish | MiroFish共识 | 78% | 2.10 | 9.24% |

### 策略详情

| 策略 | 工具 | 胜率 | 夏普 | 最大回撤 | 总交易数 |
|------|------|------|------|----------|----------|
| MiroFish共识 | all | 78% | 2.10 | 5% | 1000+ |
| Rabbit V2 | rabbit | 72% | 1.85 | 8% | 500+ |
| Rabbit | rabbit | 68% | 1.65 | 10% | 300+ |
| DCA定投 | rabbit | 75% | 1.92 | 3% | 200+ |
| Oracle预测 | oracle | 70% | 1.55 | 7% | 150+ |
| Mole V2 | mole | 65% | 1.45 | 12% | 200+ |
| Mole | mole | 62% | 1.32 | 15% | 100+ |
| Leader V2 | leader | 68% | 1.50 | 6% | 180+ |
| Leader | leader | 60% | 1.28 | 10% | 80+ |
| 信号优化器 | all | 75% | 1.90 | 5% | 300+ |
| 声纳库 | all | 70% | 1.70 | 6% | 500+ |
| 智能再平衡 | leader | 72% | 1.80 | 4% | 120+ |
| 价格告警 | mole | 65% | 1.40 | 8% | 50+ |
| 资金费率套利 | oracle | 68% | 1.55 | 5% | 60+ |

---

## 三、声纳库 123趋势模型

### 趋势分类

| 类别 | 数量 | 代表模型 |
|------|------|----------|
| 趋势类 (EMA/MA/通道) | ~30 | EMA, MA, MACD Channel |
| 动量类 (RSI/MACD/ADX) | ~25 | RSI, MACD, ADX, Stochastic |
| 波动类 (Bollinger/ATR) | ~20 | Bollinger Bands, ATR |
| 成交量类 (OBV/VWAP) | ~15 | OBV, VWAP, Volume Profile |
| 反转类 (CCI/Williams %R) | ~15 | CCI, Williams %R |
| 通道类 (Channel/Breakout) | ~10 | Donchian Channel, Breakout |
| 其他专用类 | ~8 | Ichimoku, Parabolic SAR |

### 声纳库文件

```
strategies/sonar_v3.py      # 声纳库主文件
strategies/sonar_pro.py      # Pro版本
strategies/signal_processor.py # 信号处理器
```

---

## 四、外部技能导入路径

### ClawHub技能 (已有)

```
skills/
├── binance-spot-trading/      ✅
├── binance-grid-trading/      ✅
├── polymarket-bot/            ✅
├── polymarket-arbitrage/       ✅
├── moneyclaw/                  ✅
├── trading-brain/              ✅
├── trading-agents/            ✅
├── trading-assistant/          ✅
├── trading-devbox/            ✅
├── quant-trading-system/       ✅
├── crypto-trading-bot/        ✅
├── rho-signals/               ✅
├── agent-stock/               ✅
├── akshare-stock/            ✅
├── china-stock-analysis/      ✅
├── stock-analysis/           ✅
├── stock-watcher/            ✅
├── evomap-tools/             ✅
├── agentbrain/               ✅
├── gstack-browse/            ✅
├── gstack-investigate/       ✅
└── gstack-retro/            ✅
```

### 克隆自GitHub

```
hermes-agent/                 ✅ NousResearch/hermes-agent
rag/                          ✅ TF-IDF轻量级RAG
```

---

## 五、权重更新机制

### Cron调度

| 任务 | 频率 | 功能 |
|------|------|------|
| 权重自动更新 | 每2小时 | 抓取胜率+计算权重 |

### 权重计算公式

```
综合权重 = 技能贡献(40%) + 策略贡献(60%)

技能权重 = 基准权重 × 外部胜率因子 × MiroFish分数
策略权重 = 基准权重 × (胜率/0.7) × (夏普/1.5) × MiroFish分数

MiroFish分数范围: 0.7 - 1.0
外部胜率因子范围: 0.5 - 1.5
```

### 验证指标

| 指标 | 当前值 | 目标 |
|------|--------|------|
| MiroFish验证分数 | 84.38% | >80% |
| 总置信度 | 78.58% | >75% |
| 因子退化评分 | - | <70%告警 |

---

## 六、北斗七鑫工具权重分配

| 工具 | 策略数 | 最高权重策略 | 累计权重 |
|------|--------|-------------|----------|
| 🐰 打兔子 | 3 | Rabbit V2 (8.01%) | 16.44% |
| 🐹 打地鼠 | 2 | Mole (4.43%) | 8.72% |
| 🔮 走着瞧 | 2 | Oracle预测 (4.73%) | 4.73% |
| 👑 跟大哥 | 3 | Leader V2 (3.86%) | 6.67% |
| 🍀 搭便车 | 1 | 信号优化器 (3.25%) | 3.25% |
| 🛡️ 风控/声纳 | 1 | 声纳库 (4.08%) | 4.08% |
| 🔮 MiroFish | 1 | MiroFish共识 (9.24%) | 9.24% |

---

## 七、Git提交历史

| Commit | 说明 |
|--------|------|
| 04e89df | feat: 全部量化技能导入权重系统 (28技能+14策略) |
| 8d150f7 | feat: sessions-send技能 |
| e59a37e | feat: 权重自动更新系统 |
| a97b168 | feat: Hermes Agent和RAG技能部署 |
| e4d7839 | feat: 全部量化交易技能和策略集成文档 |
| 597ac3e | feat: 权重引擎架构文档 |

---

*最后更新: 2026-04-04 08:57 UTC*
