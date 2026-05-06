# GG Fund Allocation & APK v2.7.1

更新: 2026-05-06

---

## 版本: v2.7.1

---

## 1. 做空做多灵活转换

### 市场判定
- 🟢 牛市: BTC日涨>0.5% → 优先做多
- 🔴 熊市: BTC日跌>0.5% → 优先做空
- 🟡 震荡: 其他 → RSI极端信号

### RSI Extreme
- RSI > 75 → SHORT (88.9%胜率)
- RSI < 28 → LONG (80%+胜率)

---

## 2. 北斗七鑫策略

| 星宿 | 策略 | 币种 | 杠杆 | 止盈 | 回测 |
|------|------|------|------|------|------|
| 文曲 | 跟大哥 | BTC/ETH/BNB | 5x | 5% | +142% |
| 贪狼 | 打兔子 | SOL/DOGE/ETH | 4x | 8% | +518% |
| 破军 | 走着瞧+跟大哥 | SOL/DOGE/ETH | 5x | 10% | +1802% |

---

## 3. 定时任务

```bash
*/1 * * * * $HOME/.openclaw/workspace/scripts/gg_cron_3layer.sh layer1
*/5 * * * * $HOME/.openclaw/workspace/scripts/gg_short_long_enhanced.sh
*/5 * * * * $HOME/.openclaw/workspace/scripts/gg_long_short_switch.sh
*/5 * * * * $HOME/.openclaw/workspace/scripts/gg_spike_system.sh
0 21 * * * $HOME/.openclaw/workspace/scripts/gg_cron_3layer.sh layer3
```

---

## 4. 30天回测

| 模式 | 月收益 | 胜率 | 正收益 |
|------|--------|------|--------|
| 普通模式 | +3.4% | 74.0% | 100% |
| 专家模式 | +272.2% | 49.9% | 100% |

---

## 5. 脚本清单

- gg_cron_3layer.sh - 三层监控
- gg_short_long_enhanced.sh - 做空做多增强
- gg_long_short_switch.sh - 灵活转换
- gg_spike_system.sh - 插针捕获

---

*GO2SE Genius v2.7.1 - 2026-05-06*
