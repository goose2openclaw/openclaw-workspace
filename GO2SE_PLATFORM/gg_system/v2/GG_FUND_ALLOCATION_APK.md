# GG v2 资金自主调配 APK - Hermes蒸馏版

## 版本
v2.2.0 - Hermes学习版 (2026-05-04)

## 核心功能

### 1. 1000 Mirofish智能体决策
```python
mirofish_fund_decision(fund_pressure_score, current_balance, target_balance, volatility)
```
- 1000个智能体同时投票
- 资金压力分数评估
- 波动率自适应

### 2. 加权决策方程
```
D = 0.2*(价格变化/100) + 0.15*成本差异 + 0.35*Miro + 0.15*波动率 + 0.15*Miro - 紧急惩罚
```

### 3. 强信号自主操作
```python
pre_fund_for_strong_signal(coin, required_amount, target_balance=15)
simulate_trade_result(coin, signal_d, miro_score, amount, leverage=2)
```

### 4. 自主调配类型
| 类型 | 条件 | 动作 |
|------|------|------|
| TRANSFER_IN | D>0.15, 现货充足 | 现货→逐仓 |
| TRANSFER_OUT | D<-0.1 | 逐仓→现货 |
| AGGREGATE | D>0.15, 现货不足 | 其他逐仓→目标 |

## 决策阈值
| D值范围 | 动作 |
|---------|------|
| D > 0.15 | 执行调配 |
| -0.1 ≤ D ≤ 0.15 | 观望 |
| D < -0.1 | 停止/转出 |

## Hermes蒸馏教训

### 核心教训
1. **资金集中**: 分散账户无法抓住强信号
2. **预配置**: 强信号前预先配置资金
3. **中转账户**: 保持$10+在现货作为中转
4. **摩擦成本**: 0.1%手续费可接受

### 改进策略
1. 强信号(D>0.85)时集中所有可用资金
2. 卖出弱势币换强信号币种
3. 账户最低保持$5-10余额
4. 仿真结果显示后再执行

## 今日成果
- LINK D=0.91买入成功: 0.71 LINK = $6.71
- XRP部分卖出: 5个 @ $1.39
- 资金归集效率提升

## 文件结构
```
gg_system/v2/
├── gg_v2.py              # 主程序(含Mirofish决策)
├── skills/
│   └── fund-allocation-skill.md  # 技能文档
├── GG_FUND_ALLOCATION_APK.md     # APK文档
└── README.md
```

## 使用方法
在GG主循环中自动调用:
```python
transfers = autonomous_fund_management(positions, prices, signals, spot_balance, isolated_balances)
sim = simulate_trade_result(coin, signal_d, miro_score, amount)
```

## 日志示例
```
🚨 强信号预警: LINK D=0.910
   📊 仿真: 仓位35% | 止盈12% | 胜率80%
   💰 预期收益: $0.91 | ROI: 17.2%
🧠 Mirofish资金调配决策...
📋 BNB: 🐂320 🐻280 ⚖️400 | D=0.234
✅ BNB转入5.0U成功
```
