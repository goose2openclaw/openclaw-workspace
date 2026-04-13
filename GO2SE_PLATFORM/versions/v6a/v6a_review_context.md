# v6a 架构评审文档

## 系统概览
- 版本: v6a（基于v6后端 + v6a前端）
- 目标: 恢复v6a架构，激活全部功能模块

## 当前后端结构

### Models (14个)
APIRateLimit, BacktestResult, Config, MarketData, Notification, Position, RiskLog, RiskRule, Signal, StrategyRun, Trade, User, UserAPIKey, UserWallet

### Services (10个模块)
- airdrop/ - 空投猎手
- crowd/ - 众包
- hitchhiker/ - 搭便车跟单
- leader/ - 跟大哥做市
- mole/ - 打地鼠策略
- onchain/ - 链上数据
- oracle/ - 预言机
- polymarket/ - 预测市场
- rabbit/ - 打兔子策略
- signal_push.py - 信号推送
- trading.py - 交易执行

### Expert (2个)
- engine.py - 专家推理引擎
- work_service.py - 打工服务

### API Routes
- routes.py - 主路由
- routes_autonomous.py - 自主运营
- routes_expert.py - 专家模式
- routes_market.py - 市场数据
- routes_sonar.py - 声纳趋势
- routes_ai_portfolio.py - AI组合
- routes_history_analytics.py - 历史分析

### Core (20+引擎)
ai_portfolio_manager, alerts, auth, backtest_engine, beidou_integrator, cache, config, cross_market_engine, database, enhanced_data_sources, exchanges, expert_config, leader_strategy, market_data, market_data_fetcher, ml_engine, mole_strategy, mole_v2_strategy, multi_strategy_engine, prediction_market_engine, rabbit_strategy, rabbit_v2_strategy, rabbit_weighted_engine, rate_limiter, risk_manager, sonar, sonar_v2, trading_engine, websocket_manager

## 前端 v6a
静态HTML/CSS/JS架构，34个JS模块，6级页面

## 缺失项
- v6a后端SPEC.md文档不完整
- 前端尚未替换为v6a版本
