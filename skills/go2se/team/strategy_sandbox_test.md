# 📊 策略沙盒测试报告

## 2026.03.14

### 测试结果汇总

| 策略 | API状态 | 收益 | 信号 | 状态 |
|------|---------|------|------|------|
| DCA | ✅ | 4.0% | BUY | active |
| 网格 | ✅ | 2.51% | HOLD | active |
| 趋势跟踪 | ✅ | - | BUY | active |
| 套利 | ✅ | 15.5 | SCAN | scanning |
| 做市商 | ✅ | 8.5 | - | active |
| 跟单 | ✅ | 156.8 | - | active |
| 突破 | ✅ | - | WATCH | watching |
| 均线回踩 | ✅ | - | BUY | active |

---

### 参数蒸馏对比

#### 1. DCA策略
| 参数 | 默认值 | 优化范围 | 推荐值 |
|------|--------|---------|--------|
| 间隔 | daily | daily/weekly/monthly | weekly |
| 金额 | 100 | 50-500 | 100 |
| 周期 | - | 4周-52周 | 12周 |

#### 2. 网格策略
| 参数 | 默认值 | 优化范围 | 推荐值 |
|------|--------|---------|--------|
| 网格数 | 10 | 5-50 | 15 |
| 价格区间 | 15% | 10-30% | 20% |
| 止盈 | 1.5% | 1-3% | 2% |

#### 3. 趋势跟踪策略
| 参数 | 默认值 | 优化范围 | 推荐值 |
|------|--------|---------|--------|
| MA短期 | 20 | 10-30 | 20 |
| MA长期 | 50 | 30-100 | 50 |
| RSI区间 | 30-70 | 20-80 | 25-75 |
| 止损 | 5% | 2-10% | 5% |

#### 4. 突破策略
| 参数 | 默认值 | 优化范围 | 推荐值 |
|------|--------|---------|--------|
| 盘整幅度 | 2% | 1-5% | 2% |
| 量能倍数 | 2x | 1.5-3x | 2x |
| 止损 | 3% | 2-5% | 3% |

---

### 声纳驱动匹配

| 趋势 | 推荐策略 | 仓位 |
|------|---------|------|
| bullish | trend, breakout, ma_pullback | 50-70% |
| neutral | grid, dca, arbitrage | 30-50% |
| bearish | grid, market_maker | 10-30% |

---

### 沙盒测试命令

```bash
# DCA测试
curl -X POST http://localhost:5000/api/strategy/dca -d '{"symbol":"BTCUSDT","amount":100}'

# 网格测试
curl -X POST http://localhost:5000/api/strategy/grid -d '{"grid_count":10}'

# 趋势测试
curl -X POST http://localhost:5000/api/strategy/trend -d '{"ma_short":20,"ma_long":50}'

# 声纳趋势
curl http://localhost:5000/api/sonar/trend_detection

# 策略选择
curl http://localhost:5000/api/sonar/select_strategy
```

