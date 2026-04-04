# 123趋势模型分类文档

> GO2SE v11 声纳库 (Sonar Library)
> 总计: 123个技术指标模型

---

## 1. 趋势类 (Trend Indicators) - 30个

### 移动平均线族 (Moving Averages)
| ID | 名称 | 参数 | 描述 |
|----|------|------|------|
| TR001 | SMA_5 | period=5 | 简单移动平均5期 |
| TR002 | SMA_10 | period=10 | 简单移动平均10期 |
| TR003 | SMA_20 | period=20 | 简单移动平均20期 |
| TR004 | SMA_50 | period=50 | 简单移动平均50期 |
| TR005 | SMA_100 | period=100 | 简单移动平均100期 |
| TR006 | SMA_200 | period=200 | 简单移动平均200期 |
| TR007 | EMA_5 | period=5 | 指数移动平均5期 |
| TR008 | EMA_10 | period=10 | 指数移动平均10期 |
| TR009 | EMA_20 | period=20 | 指数移动平均20期 |
| TR010 | EMA_50 | period=50 | 指数移动平均50期 |
| TR011 | EMA_100 | period=100 | 指数移动平均100期 |
| TR012 | EMA_200 | period=200 | 指数移动平均200期 |
| TR013 | WMA_10 | period=10 | 加权移动平均10期 |
| TR014 | WMA_20 | period=20 | 加权移动平均20期 |
| TR015 | DEMA_20 | period=20 | 双指数移动平均 |
| TR016 | TEMA_20 | period=20 | 三重指数移动平均 |
| TR017 | T3_MA | period=20 | T3移动平均 |
| TR018 | HMA_20 | period=20 | Hull移动平均 |

### 通道类 (Channels)
| ID | 名称 | 参数 | 描述 |
|----|------|------|------|
| TR019 | Keltner_Channel | period=20, atr=2 | Keltner通道 |
| TR020 | Donchian_Channel | period=20 | 多空通道 |
| TR021 | Aroon_Up_Down | period=25 | Aroon指标 |
| TR022 | Supertrend | period=10, multiplier=3 | 超级趋势 |
| TR023 | Ichimoku_Cloud | conv=9, base=26, span=52 | 一目云 |
| TR024 | Bollinger_Bands | period=20, std=2 | 布林带 |
| TR025 | Price_Channel | period=20 | 价格通道 |

### 其他趋势
| ID | 名称 | 参数 | 描述 |
|----|------|------|------|
| TR026 | Parabolic_SAR | step=0.02, max=0.2 | 抛物线止损 |
| TR027 | ZigZag | depth=12, deviation=5 | 锯齿形 |
| TR028 | Linear_Regression | period=20 | 线性回归 |
| TR029 | Vortex_Indicator | period=14 | 漩涡指标 |
| TR030 | TRIX | period=15 | 三倍指数平滑 |

---

## 2. 动量类 (Momentum Indicators) - 25个

### RSI族 (Relative Strength)
| ID | 名称 | 参数 | 描述 |
|----|------|------|------|
| M001 | RSI_14 | period=14 | 相对强弱指数 |
| M002 | RSI_7 | period=7 | 快速RSI |
| M003 | RSI_21 | period=21 | 慢速RSI |
| M004 | Stoch_RSI | period=14 | 随机RSI |
| M005 | Stoch_RSI_K | period=14 | 随机RSI K线 |
| M006 | Stoch_RSI_D | period=14 | 随机RSI D线 |
| M007 | RSI_MA_Cross | period=14 | RSI移动平均交叉 |

### MACD族
| ID | 名称 | 参数 | 描述 |
|----|------|------|------|
| M008 | MACD | fast=12, slow=26, signal=9 | MACD主指标 |
| M009 | MACD_Histogram | fast=12, slow=26, signal=9 | MACD柱状图 |
| M010 | MACD_Signal | fast=12, slow=26, signal=9 | MACD信号线 |
| M011 | MACD_Crossover | fast=12, slow=26, signal=9 | MACD交叉 |
| M012 | MACD_Divergence | fast=12, slow=26, signal=9 | MACD背离 |

### ADX族
| ID | 名称 | 参数 | 描述 |
|----|------|------|------|
| M013 | ADX_14 | period=14 | 平均趋向指数 |
| M014 | DMI_Plus | period=14 | DMI正向 |
| M015 | DMI_Minus | period=14 | DMI负向 |
| M016 | ADX_Crossover | period=14 | ADX交叉 |

### 其他动量
| ID | 名称 | 参数 | 描述 |
|----|------|------|------|
| M017 | ROC_10 | period=10 | 变动率 |
| M018 | ROC_20 | period=20 | 变动率20期 |
| M019 | Momentum | period=10 | 动量指标 |
| M020 | CMO | period=14 | Chande动量指标 |
| M021 | PPO | fast=12, slow=26 | 价格百分比振荡器 |
| M022 | Williams_R | period=14 | Williams %R |
| M023 | Ultimate_Oscillator | p1=7, p2=14, p3=28 | 终极振荡器 |
| M024 | Awesome_Oscillator | fast=5, slow=34 | AO振荡器 |
| M025 | Rate_of_Change | period=14 | 变化率 |

---

## 3. 波动类 (Volatility Indicators) - 20个

| ID | 名称 | 参数 | 描述 |
|----|------|------|------|
| V001 | ATR_14 | period=14 | 平均真实波幅 |
| V002 | ATR_20 | period=20 | ATR长周期 |
| V003 | ATR_Ratio | period=14 | ATR相对比率 |
| V004 | Bollinger_Width | period=20, std=2 | 布林带宽度 |
| V005 | Bollinger_Pcnt | period=20, std=2 | 布林带百分比 |
| V006 | Keltner_Width | period=20, atr=2 | Keltner宽度 |
| V007 | Historical_Volatility | period=20 | 历史波动率 |
| V008 | Parkinson_Volatility | period=20 | Parkinson波动率 |
| V009 | Garman_Klass_Vol | period=20 | Garman-Klass波动率 |
| V010 | Rogers_Satchell_Vol | period=20 | Rogers-Satchell波动率 |
| V011 | Yang_Zhang_Vol | period=20 | Yang-Zhang波动率 |
| V012 | Chaikin_Volatility | period=10 | Chaikin波动率 |
| V013 | Standard_Dev | period=20 | 标准差 |
| V014 | Spread_Analysis | period=20 | 价差分析 |
| V015 | Nearest_Contract | - | 最近合约分析 |
| V016 | Term_Structure | - | 期限结构 |
| V017 | Basis_Mean_Rev | period=20 | 基差均值回归 |
| V018 | Basis_Trend | period=20 | 基差趋势 |
| V019 | Contango_Index | - | 期货升水指数 |
| V020 | Backwardation_Index | - | 期货贴水指数 |

---

## 4. 成交量类 (Volume Indicators) - 15个

| ID | 名称 | 参数 | 描述 |
|----|------|------|------|
| Vol01 | OBV | - | 能量潮 |
| Vol02 | OBV_MA | period=20 | OBV移动平均 |
| Vol03 | VWAP | - | 成交量加权平均价 |
| Vol04 | VWAP_MA | period=20 | VWAP移动平均 |
| Vol05 | Volume_RSI | period=14 | 成交量RSI |
| Vol06 | MFI | period=14 | 资金流量指数 |
| Vol07 | CMF | period=20 | Chaikin资金流量 |
| Vol08 | Accumulation_Dist | - | 累积分布线 |
| Vol09 | Volume_Profile | bins=24 | 成交量分布 |
| Vol10 | Volume_SMA_Ratio | period=20 | 成交量/均量比 |
| Vol11 | Bid_Ask_Pressure | - | 买卖压力 |
| Vol12 | Buy_Sell_Volume | - | 买卖成交量 |
| Vol13 | Large_Transaction | threshold=1000000 | 大单交易 |
| Vol14 | Volume_Weighted_Entry | - | 成交量加权入场 |
| Vol15 | Delta_Volume | period=10 | 成交量增量 |

---

## 5. 反转类 (Reversal Indicators) - 15个

| ID | 名称 | 参数 | 描述 |
|----|------|------|------|
| R001 | CCI_14 | period=14 | 商品通道指标 |
| R002 | CCI_20 | period=20 | CCI长周期 |
| R003 | CCI_Histogram | period=14 | CCI柱状图 |
| R004 | CCI_Divergence | period=14 | CCI背离 |
| R005 | Stoch_K | period=14 | 随机K线 |
| R006 | Stoch_D | period=14 | 随机D线 |
| R007 | Stoch_Full | k=14, d=3, smooth=3 | 完整随机指标 |
| R008 | Williams_R | period=14 | Williams %R |
| R009 | Williams_R_Div | period=14 | Williams背离 |
| R010 | ROC_Reversal | period=5 | ROC反转信号 |
| R011 | RSI_Divergence | period=14 | RSI背离 |
| R012 | MACD_Divergence | period=14 | MACD背离 |
| R013 | Overbought_Oversold | period=14 | 超买超卖 |
| R014 | Stochastic_Div | period=14 | 随机背离 |
| R015 | Price_Divergence | period=20 | 价格背离 |

---

## 6. 通道突破类 (Channel & Breakout) - 10个

| ID | 名称 | 参数 | 描述 |
|----|------|------|------|
| B001 | Breakout_20 | period=20 | 20日突破 |
| B002 | Breakout_50 | period=50 | 50日突破 |
| B003 | Support_Resistance | lookback=20 | 支撑阻力 |
| B004 | Pivot_Points | type=standard | 枢轴点 |
| B005 | Fibonacci_Retrace | - | 斐波那契回撤 |
| B006 | Volume_Confirmation | period=20 | 成交量确认 |
| B007 | Price_Amplitude | period=20 | 价格振幅 |
| B008 | Consolidation_Break | lookback=20 | 盘整突破 |
| B009 | Range_Breakout | period=20 | 区间突破 |
| B010 | Trendline_Break | - | 趋势线突破 |

---

## 7. 专用类 (Specialized) - 8个

| ID | 名称 | 参数 | 描述 |
|----|------|------|------|
| S001 | On_Balance_Volume | - | 平衡成交量 |
| S002 | Volume_Weighted_Price | - | 成交量加权价格 |
| S003 | Money_Flow | period=14 | 资金流量 |
| S004 | Ease_of_Movement | period=14 | 简易波动指标 |
| S005 | Force_Index | period=13 | 强力指数 |
| S006 | Elder_Ray | period=13 |  Elder射线 |
| S007 | Market_Facilitation | - | 市场促进指数 |
| S008 | Candlestick_Pattern | - | K线形态识别 |

---

## 模型使用指南

### 策略工具适配

| 工具 | 推荐模型 | 权重 |
|------|----------|------|
| 🐰 打兔子 | TR009, TR011, M001, M008, M013 | 趋势+动量 |
| 🐹 打地鼠 | M001, M002, R001, R004, V001 | 动量+反转 |
| 🔮 走着瞧 | Vol01, Vol03, S003, S005 | 成交量+专用 |
| 👑 跟大哥 | Vol04, B001, B006 | 通道+成交量 |
| 🍀 搭便车 | TR024, M014, M015, B002 | 布林+突破 |

### 模型组合建议

1. **趋势确认**: SMA + EMA + ADX
2. **动量信号**: RSI + MACD + Stochastic
3. **波动率警戒**: ATR + Bollinger Width
4. **成交量确认**: OBV + VWAP + Volume Profile
5. **反转预警**: CCI + Williams %R + RSI Divergence

---

## 文件位置

- 模型定义: `backend/app/core/sonar_v2.py`
- 模型配置: `strategies/models/model_registry.json`
- 策略映射: `strategies/config/*.json`
