# 策略开发进度

## 2026.03.14 已完成

### API数量: 16个策略

| # | 策略 | API | 状态 |
|---|------|-----|------|
| 1 | 网格交易 | /api/strategy/grid | ✅ |
| 2 | DCA定投 | /api/strategy/dca | ✅ |
| 3 | 趋势跟踪 | /api/strategy/trend | ✅ 新 |
| 4 | 套利 | /api/strategy/arbitrage | ✅ 新 |
| 5 | 做市商 | /api/strategy/market_maker | ✅ 新 |
| 6 | 跟单 | /api/strategy/copy_trade | ✅ 新 |
| 7 | 突破 | /api/strategy/breakout | ✅ 新 |
| 8 | 均线回踩 | /api/strategy/ma_pullback | ✅ 新 |
| 9 | IF-THEN自动化 | /api/strategy/if_then | ✅ 新 |
| 10 | 策略组合 | /api/strategy/portfolio | ✅ 新 |
| 11 | 参数回测 | /api/strategy/backtest_params | ✅ 新 |
| 12-16 | 更多 | 配置已就绪 | ⏳ |

### 策略参数

| 策略 | 关键参数 | 推荐值 |
|------|---------|-------|
| 趋势跟踪 | MA周期, RSI区间 | 20/50, 30-70 |
| 套利 | 交易所对, 最小价差 | 0.5% |
| 做市商 | 价差, 订单量 | 0.1%, 0.01 |
| 跟单 | 交易员, 仓位比 | 30% |
| 突破 | 盘整幅度, 量能 | 2%, 2x |

