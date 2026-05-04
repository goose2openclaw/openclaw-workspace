# CHANGELOG - GO2SE 北斗七鑫量化交易平台

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.0.0] - 2026-03-29

### Added
- 🪿 GO2SE 北斗七鑫量化交易平台正式发布
- 7大投资策略整合
  - 🐰 打兔子 (Top20趋势追踪)
  - 🐹 打地鼠 (高波动套利)
  - 🔮 走着瞧 (预测市场)
  - 👑 跟大哥 (做市协作)
  - 🍀 搭便车 (跟单分成)
  - 💰 薅羊毛 (新币空投套利)
  - 👶 穷孩子 (众包任务套利)
- 100+趋势模型声纳库
- 8大风控规则
- 实时市场数据 (Binance)
- 回测引擎
- MiroFish 预言机系统 (100智能体×5轮共识)
- WebSocket实时推送
- API认证系统

### Features
- 7个页面: 总览/市场/策略/信号/交易/钱包/设置
- 键盘快捷键支持 (1-7切换页面)
- 页面切换动画效果
- 响应式设计
- Stale-While-Revalidate缓存策略
- 内存缓存 (stats 8s, portfolio 10s, market 15-60s)

### Security
- API Key认证
- CORS配置
- 参数化SQL查询
- 敏感信息安全存储

### Scripts
- `validate_startup.sh` - 部署前验证
- `start_server.sh` - 服务启动管理
- `health_check.sh` - 健康检查 (5分钟Cron)
- `deep_simulation.py` - 参数优化V1
- `deep_simulation_v2.py` - 参数优化V2
- `cron_guardian.sh` - Cron任务守护

---

## [0.9.0] - 2026-03-21

### Added
- 基础交易引擎
- 风控系统
- RSI策略
- 模拟交易模式

---

## [0.1.0] - 2026-03-14

### Added
- 项目初始化
- OpenClaw集成

## [2.1.0] - 2026-05-04

### Added
- 动态杠杆系统 (3x/5x/自适应)
- NOTIONAL 检查器 (订单金额验证)
- 保证金率实时监控 (marginLevel > 3.0 预警)
- 分批平仓优化
- 1000智能体 Mirofish 仿真
- 自主平仓优化

### Changed
- 杠杆配置: 2x → 3x/5x 可配置
- 动态仓位: 35%/25%/20%/15% 基于信号强度

### Fixed
- NOTIONAL 不足无法下单问题

### Performance
- 总资产: $208.62
- LINK 5x杠杆仓位: 7.46 LINK
- DOGE 减仓: 44→20 DOGE
- ORCA 止损失败 (NOTIONAL限制)

### Lessons Learned
- Binance LOT_SIZE 和 NOTIONAL 限制必须在下单前检查
- 逐仓保证金不足时无法开新仓
- 杠杆保证金率应保持在 3.0 以上

## [2.2.0] - 2026-05-04

### Added
- enhanced_leverage_engine.py: 增强杠杆引擎 v2.1
  - 动态杠杆: 1x~5x自适应
  - 资金复用: 止盈30%套现再投入
  - 保证金率 < 2.5 强制减仓
  - Mirofish 1000智能体仿真
- 三档Cron监控 (1min/5min/10min)
- FORCE_REDUCE 自动减仓机制
- LINK强平价实时计算

### Changed
- gg_crypto_monitor.sh: 集成增强杠杆引擎
- 决策方程: D = 0.35×趋势 + 0.30×(涨跌/10) + 0.25×(量比-1) - 0.10×波动率
- 杠杆阈值: 强(5x) >0.8 | 中(3x) >0.5 | 普(2x) >0.15

### Safety
- marginLevel < 2.5: 🔴 强制减仓
- marginLevel < 3.0: ⚠️ 预警

### GitHub Push
- enhanced_leverage_engine.py 已推送
