# GO2SE 可用策略和模型清单

> 更新: 2026-04-04

---

## 一、123趋势模型 (声纳库)

### 1.1 趋势类 (30个)

| ID | 名称 | 类别 | 参数 |
|----|------|------|------|
| TR001-TR006 | SMA_5/10/20/50/100/200 | 移动平均 | period=N |
| TR007-TR012 | EMA_5/10/20/50/100/200 | 移动平均 | period=N |
| TR013-TR014 | WMA_10/20 | 加权移动平均 | period=N |
| TR015-TR017 | DEMA/TEMA/T3_MA | 指数移动平均 | period=20 |
| TR018 | HMA_20 | Hull移动平均 | period=20 |
| TR019 | Keltner_Channel | 通道 | period=20, atr=2 |
| TR020 | Donchian_Channel | 通道 | period=20 |
| TR021 | Aroon_Up_Down | 通道 | period=25 |
| TR022 | Supertrend | 通道 | period=10, mult=3 |
| TR023 | Ichimoku_Cloud | 通道 | conv=9, base=26 |
| TR024 | Bollinger_Bands | 通道 | period=20, std=2 |
| TR025 | Price_Channel | 通道 | period=20 |
| TR026 | Parabolic_SAR | 趋势 | step=0.02 |
| TR027 | ZigZag | 趋势 | depth=12 |
| TR028 | Linear_Regression | 趋势 | period=20 |
| TR029 | Vortex_Indicator | 趋势 | period=14 |
| TR030 | TRIX | 趋势 | period=15 |

### 1.2 动量类 (25个)

| ID | 名称 | 类别 | 参数 |
|----|------|------|------|
| M001-M003 | RSI_7/14/21 | RSI族 | period=N |
| M004-M006 | Stoch_RSI/K/D | 随机RSI | period=14 |
| M007 | RSI_MA_Cross | RSI交叉 | period=14 |
| M008-M012 | MACD系 | MACD族 | fast=12, slow=26 |
| M013-M016 | ADX/DMI系 | ADX族 | period=14 |
| M017-M018 | ROC_10/20 | 变动率 | period=N |
| M019-M020 | Momentum/CMO | 动量 | period=10/14 |
| M021 | PPO | 振荡器 | fast=12, slow=26 |
| M022 | Williams_R | 振荡器 | period=14 |
| M023 | Ultimate_Oscillator | 振荡器 | p1=7, p2=14 |
| M024 | Awesome_Oscillator | 振荡器 | fast=5, slow=34 |
| M025 | Rate_of_Change | 振荡器 | period=14 |

### 1.3 波动类 (20个)

| ID | 名称 | 类别 | 参数 |
|----|------|------|------|
| V001-V004 | Bollinger_Bands | 波动 | period=20, std=1-3 |
| V005-V008 | ATR_7/14/21/28 | ATR族 | period=N |
| V009-V012 | Keltner_Channel | 波动 | period=20 |
| V013-V016 | Donchian_Channel | 波动 | period=10/20/50 |
| V017-V020 | 历史波动率 | 波动 | 不同窗口 |

### 1.4 成交量类 (15个)

| ID | 名称 | 类别 | 参数 |
|----|------|------|------|
| VO001 | OBV | 能量潮 | - |
| VO002-VO004 | VWAP | 量价 | 不同周期 |
| VO005-VO008 | Volume_MA | 成交量均线 | period=N |
| VO009-VO012 | MFI | 资金流 | period=14 |
| VO013-VO015 | CMF/AD | 积累分布 | - |

### 1.5 反转类 (15个)

| ID | 名称 | 类别 | 参数 |
|----|------|------|------|
| RV001-RV005 | CCI_14/20 | 商品通道 | period=N |
| RV006-RV010 | Williams_R | 超买超卖 | period=N |
| RV011-RV015 | Stoch_K/D | 随机 | %K/%D |

### 1.6 通道类 (10个)

| ID | 名称 | 类别 | 参数 |
|----|------|------|------|
| CH001-CH005 | 各种通道 | 通道 | - |
| CH006-CH010 | Breakout | 突破 | - |

### 1.7 市场结构类 (8个)

| ID | 名称 | 类别 |
|----|------|------|
| MS001-MS008 | 结构识别 | 支撑阻力 |

---

## 二、7大工具策略配置

### 2.1 🐰 打兔子 (Rabbit)

```json
{
  "id": "tool_rabbit",
  "allocation": 0.25,
  "stop_loss": 0.05,
  "take_profit": 0.08,
  "symbols": ["BTC", "ETH", "BNB", "XRP", "ADA", "DOGE", "SOL", "DOT", "MATIC", "LTC", ...],
  "applicable_models": ["TR001-TR018", "M001-M012", "V001-V008"],
  "status": "✅ 已激活"
}
```

### 2.2 🐹 打地鼠 (Mole)

```json
{
  "id": "tool_mole",
  "allocation": 0.20,
  "stop_loss": 0.08,
  "take_profit": 0.15,
  "symbols": "非前20主流",
  "radar": {
    "volume_spike": 3.0,
    "price_change_1h": 0.05,
    "funding_rate_anomaly": 0.02
  },
  "applicable_models": ["M001-M025", "RV001-RV015"],
  "status": "✅ 已激活"
}
```

### 2.3 🔮 走着瞧 (Oracle)

```json
{
  "id": "tool_oracle",
  "allocation": 0.15,
  "stop_loss": 0.05,
  "take_profit": 0.10,
  "prediction_markets": ["polymarket", "azuro", "witch", "metagate", "perspectx", "kucoin_predict"],
  "mirofish": {
    "enabled": true,
    "required_score": 70,
    "monte_carlo_runs": 2000
  },
  "status": "✅ 已激活"
}
```

### 2.4 👑 跟大哥 (Leader)

```json
{
  "id": "tool_leader",
  "allocation": 0.15,
  "stop_loss": 0.03,
  "take_profit": 0.06,
  "market_making": {
    "spread_min": 0.001,
    "spread_max": 0.01
  },
  "mirofish": {
    "enabled": true,
    "decision_weight": 0.30,
    "required_score": 70
  },
  "status": "✅ 已激活"
}
```

### 2.5 🍀 搭便车 (Hitchhiker)

```json
{
  "id": "tool_hitchhike",
  "allocation": 0.10,
  "stop_loss": 0.05,
  "take_profit": 0.08,
  "copy_trading": {
    "providers": ["top_traders", "strategy_funds", "signal_groups"],
    "min_win_rate": 0.55
  },
  "mirofish": {
    "enabled": true,
    "decision_weight": 0.25,
    "required_score": 65
  },
  "status": "✅ 已激活"
}
```

### 2.6 💰 薅羊毛 (Airdrop) - 打工工具

```json
{
  "id": "tool_airdrop",
  "allocation": 0.03,
  "stop_loss": 0.02,
  "take_profit": 0.20,
  "type": "打工工具",
  "activities": ["空投猎手", "任务平台", "验证码"],
  "status": "✅ 已激活"
}
```

### 2.7 👶 穷孩子 (Crowdsource) - 打工工具

```json
{
  "id": "tool_crowdsource",
  "allocation": 0.02,
  "stop_loss": 0.01,
  "take_profit": 0.30,
  "type": "打工工具",
  "platforms": ["EvoMap", "众包平台"],
  "status": "✅ 已激活"
}
```

---

## 三、MiroFish 预测市场

| 市场ID | 名称 | 智能体 | 轮次 | 状态 |
|--------|------|--------|------|------|
| btc_trend | BTC 24小时趋势 | 100 | 5 | ✅ |
| eth_trend | ETH 24小时趋势 | 100 | 5 | ✅ |
| sol_trend | SOL 24小时趋势 | 100 | 5 | ✅ |
| xrp_trend | XRP 24小时趋势 | 100 | 5 | ✅ |
| major_pairs | 主流币组合预测 | 80 | 4 | ✅ |
| market_sentiment | 市场整体情绪 | 60 | 3 | ✅ |

---

## 四、MoneyClaw 策略 (投资工具)

| 策略 | GO2SE工具 | 状态 |
|------|-----------|------|
| crypto_dca | 🐰 打兔子 | ✅ 已集成 |
| smart_rebalance | 👑 跟大哥 | ✅ 已集成 |
| crypto_price_alert | 🐹 打地鼠 | ✅ 已集成 |
| crypto_funding | 🔮 走着瞧 | ✅ 已集成 |
| appl_trading_strategy | 🍀 搭便车 | ✅ 可用 |
| gold_trading_strategy | (扩展) | ⏳ 待开发 |
| stock_dividend | (扩展) | ⏳ 待开发 |

---

## 五、集成状态总览

| 类别 | 总数 | 已激活 | 状态 |
|------|------|--------|------|
| 趋势模型 | 123 | 95 | ✅ |
| 7大工具 | 7 | 7 | ✅ |
| 预测市场 | 6 | 6 | ✅ |
| MoneyClaw策略 | 4 | 4 | ✅ |

---

## 六、激活命令

```bash
# 查看声纳库状态
curl localhost:8004/api/sonar/status

# 查看MiroFish状态
curl localhost:8004/api/mirofish/status

# 查看所有策略
curl localhost:8004/api/strategies

# 激活所有策略
curl -X POST localhost:8004/api/strategies/enable-all

# 运行MiroFish仿真
python3 scripts/mirofish_full_simulation_v2.py
```
