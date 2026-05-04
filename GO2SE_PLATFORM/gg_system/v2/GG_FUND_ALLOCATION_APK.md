# GG v2 资金自主调配 APK

## 版本
v2.1.0 - Mirofish增强版

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
D = 0.2*(价格变化/100) + 0.15*成本差异 + 0.35*Mirofish + 0.15*波动率 + 0.15*Mirofish - 紧急惩罚
```

### 3. 自主调配类型
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

## 文件结构
```
gg_system/v2/
├── gg_v2.py              # 主程序(含Mirofish决策)
├── skills/
│   └── fund-allocation-skill.md
├── GG_FUND_ALLOCATION_APK.md
└── README.md
```

## 使用方法
在GG主循环中自动调用:
```python
transfers = autonomous_fund_management(positions, prices, signals, spot_balance, isolated_balances)
```

## 日志示例
```
🧠 Mirofish资金调配决策...
📋 BNB: 🐂320 🐻280 ⚖️400 | D=0.234 强信号需要
✅ BNB转入5.0U成功
```
