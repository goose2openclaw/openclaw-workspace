
---

## v2.3 APK 更新 (2026-05-05)

### 新增规则

1. **保证金率触发器**
```
IF marginLevel < 2.5:
    FORCE_SELL 50% position
    REPAY 50% of proceeds
```

2. **分批止盈**
```
IF profit > 10%:
    SELL 30% position
IF profit > 15%:
    SELL 50% position  
IF profit > 20%:
    SELL 70% position
```

3. **RSI过滤**
```
IF RSI > 70 AND signal == BUY:
    REDUCE confidence by 20%
IF RSI < 30 AND signal == SELL:
    REDUCE confidence by 20%
```

### 迭代记录
- v2.2: 基础杠杆引擎 + Mirofish
- v2.3: 保证金率优先 + 分批止盈 + RSI确认
