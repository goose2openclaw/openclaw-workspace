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
