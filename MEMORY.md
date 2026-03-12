# MEMORY.md - 长期记忆

## 用户信息
- 使用 openclaw-control-ui 界面
- 对交易自动化 (FreqTrade) 感兴趣
- 使用中文沟通
- 倾向于使用 Docker 但愿意接受 pip 方案

## 已安装技能 (32+)
- agent-retro: 每日复盘技能
- vassili-clawhub-cli: ClawHub CLI 技能
- openclaw-tavily-search: Tavily 搜索
- xiucheng-self-improving-agent: 自我提升
- gog: Google Workspace CLI
- freqtrade: 交易机器人
- PDF, Scrapling, Trading, Crypto-trading-bot, Trading-brain
- Binance-grid-trading, Polymarket-bot, Polymarket-arbitrage
- Pair-trade-screener, Rho-signals, Video-to-text, Weather 等

## 交易系统 (XIAMI)

### 策略迭代
- **v1-v4**: 基础策略开发
- **主流币策略**: mainstream_strategy.py
- **打地鼠策略**: mole_strategy.py
- **高频量化**: quant_engine.py
- **声纳系统**: sonar_v3.py, sonar_pro.py
- **统一系统**: xiami_v4.py, auto_run.py

### Sonar Pro v2 特性
- 多数据源聚合 (Binance, Bybit, OKX)
- 10+ 趋势形态识别
- 多因子置信度评分 (0-10)
- 严格执行规则 (≥5分才执行)
- 仓位: 3%-20% 根据置信度
- 止损/止盈规则
- 风险管理制度

### 趋势数据库
- 100+ 趋势模型
- 市场覆盖: Crypto, Stock, ETF, DeFi, NFT, 预测市场, 社交媒体, 宏观

### Cron 任务
- xiami-tiered-trading: 每30分钟
- xiami-unified: 每15分钟
- xiami-market-scan: 每30分钟
- xiami-auto-trade: 每30分钟 (扫描→交易→复盘→优化→GitHub同步)

## 经验总结
- 容器环境优先考虑 pip 安装而非 Docker
- 后台进程需要更稳健的管理方式
- GitHub 仓库: https://github.com/goose2openclaw/openclaw-workspace
