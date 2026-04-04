# GO2SE 全部量化交易技能和策略集成

> 版本: v11.0.0 | 更新: 2026-04-04

---

## 一、全部量化交易技能 (等待权重集成)

### 1.1 技能清单

| # | 技能 | 路径/来源 | 功能 | 状态 | 权重范围 |
|---|------|----------|------|------|---------|
| **交易所连接** |
| 1 | binance-spot-trading | skills/binance-spot-trading/ | Binance现货交易 | ✅ | 自动 |
| 2 | binance-grid-trading | skills/binance-grid-trading/ | 网格交易 | ✅ | 0.05-0.20 |
| 3 | polymarket-bot | skills/polymarket-bot/ | Polymarket预测 | ✅ | 0.10-0.25 |
| 4 | polymarket-arbitrage | skills/polymarket-arbitrage/ | 预测市场套利 | ✅ | 0.10-0.20 |
| **量化分析** |
| 5 | quant-trading-system | skills/quant-trading-system/ | 量化交易系统 | ✅ | 0.15-0.30 |
| 6 | trading-brain | skills/trading-brain/ | 交易决策脑 | ✅ | 0.20-0.35 |
| 7 | trading-agents | skills/trading-agents/ | 多智能体交易 | ✅ | 0.15-0.30 |
| 8 | rho-signals | skills/rho-signals/ | 信号系统 | ✅ | 0.10-0.25 |
| 9 | agent-stock | skills/agent-stock/ | 股票Agent | ✅ | 0.05-0.15 |
| 10 | akshare-stock | skills/akshare-stock/ | A股数据 | ✅ | 0.05-0.15 |
| 11 | china-stock-analysis | skills/china-stock-analysis/ | A股分析 | ✅ | 0.05-0.15 |
| 12 | stock-analysis | skills/stock-analysis/ | 股票分析 | ✅ | 0.05-0.15 |
| 13 | stock-watcher | skills/stock-watcher/ | 股票监视 | ✅ | 0.05-0.15 |
| 14 | stock-monitor | skills/stock-monitor/ | 股票监控 | ✅ | 0.05-0.15 |
| **数据与分析** |
| 15 | data-analysis | skills/data-analysis/ | 数据分析 | ✅ | 0.10-0.20 |
| 16 | trading-assistant | skills/trading-assistant/ | 交易助手 | ✅ | 0.10-0.20 |
| 17 | trading-devbox | skills/trading-devbox/ | 交易开发箱 | ✅ | 0.10-0.20 |
| **外部集成** |
| 18 | **moneyclaw** | skills/moneyclaw/ | 7x24金融AI | ✅ | 0.10-0.30 |
| 19 | **agentbrain** | skills/agentbrain/ | AI记忆系统 | ✅ | 0.05-0.20 |
| 20 | evomap-tools | skills/evomap-tools/ | 众包/EvoMap | ✅ | 0.05-0.15 |
| **增强功能** |
| 21 | agent-reach | skills/agent-reach/ | Agent通信 | ✅ | 0.05-0.15 |
| 22 | agent-retro | skills/agent-retro/ | Agent复盘 | ✅ | 0.05-0.15 |
| 23 | proactive-agent-skill | skills/proactive-agent-skill/ | 主动Agent | ✅ | 0.10-0.20 |
| 24 | gstack-investigate | skills/gstack-investigate/ | 调查分析 | ✅ | 0.05-0.15 |
| **预留通道** |
| 25 | future-skill-1 | (待接入) | - | ⏳ | 0.0-0.20 |
| 26 | future-skill-2 | (待接入) | - | ⏳ | 0.0-0.20 |

### 1.2 技能调用/激活/配置

#### 1.2.1 Binance现货交易

```bash
# 调用
from binance.spot import Spot
client = Spot()

# 激活
curl -X POST localhost:8004/api/trade/enable \
  -d '{"exchange": "binance", "mode": "spot"}'

# 配置
# 路径: skills/binance-spot-trading/
# API Key: 在Settings页面配置
# 权限: 只读/交易
```

#### 1.2.2 Binance网格交易

```bash
# 调用
python3 -m binance_grid_trading --config config.yaml

# 激活
curl -X POST localhost:8004/api/strategies/grid/enable

# 配置
{
  "grid_count": 10,
  "price_range": 0.05,
  "quantity": 0.001,
  "stop_loss": 0.02
}
```

#### 1.2.3 Polymarket预测

```bash
# 调用
curl -X POST localhost:8004/api/oracle/markets \
  -d '{"market": "btc_trend", "question": "BTC > 70000?"}'

# 激活
curl -X POST localhost:8004/api/strategies/polymarket/enable

# 配置
{
  "api_endpoint": "https://gamma-api.polymarket.com",
  "min_probability": 0.65,
  "max_position": 0.05
}
```

#### 1.2.4 MoneyClaw (外部技能)

```bash
# 调用
cd /root/.openclaw/workspace/moneyclaw-py
python3 -m moneyclaw strategies/crypto_dca

# 激活
curl -X POST localhost:8004/api/strategies/moneyclaw/enable

# 配置
{
  "strategy": "dca",
  "coin": "BTC",
  "amount_usd": 10,
  "interval_hours": 24
}
```

#### 1.2.5 AgentBrain (外部技能)

```javascript
// 调用
const { AgentBrain } = require('agentbrain-sdk');
const brain = new AgentBrain('kc_live_xxx');

// 查询
const result = await brain.retrieve('BTC trading signal', {topK: 3});

// 激活 (npm已安装)
cd /root/.openclaw/workspace/agentbrain-sdk
npm install
```

#### 1.2.6 EvoMap众包

```bash
# 调用
curl -X POST https://evomap.ai/a2a/retrieve \
  -H "X-Node-ID: node_41349a7fe0f7c472" \
  -d '{"query": "crypto trends", "topK": 5}'

# 激活
curl -X POST localhost:8004/api/strategies/evomap/enable

# 配置
{
  "node_id": "node_41349a7fe0f7c472",
  "api_key": "xxx"
}
```

#### 1.2.7 Trading-Brain

```bash
# 调用
curl -X POST localhost:8004/api/ai/brain/decide \
  -d '{"market": "BTC/USDT", "action": "analyze"}'

# 激活
curl -X POST localhost:8004/api/ai/brain/enable

# 配置
{
  "model": "gpt-4",
  "temperature": 0.7,
  "max_tokens": 1000
}
```

#### 1.2.8 Quant-Trading-System

```bash
# 调用
python3 -m quant_trading_system --backtest

# 激活
curl -X POST localhost:8004/api/strategies/quant/enable

# 配置
{
  "strategies": ["momentum", "mean_reversion", "breakout"],
  "timeframe": "1h",
  "lookback": 100
}
```

### 1.3 技能权重配置API

```bash
# 设置技能权重
curl -X POST localhost:8004/api/weights/skills \
  -d '{
    "moneyclaw": 0.20,
    "trading_brain": 0.25,
    "binance_grid": 0.15,
    "polymarket": 0.10,
    "agentbrain": 0.10,
    "evomap": 0.10,
    "others": 0.10
  }'

# 获取当前权重
curl localhost:8004/api/weights/skills

# 重置为默认
curl -X POST localhost:8004/api/weights/skills/reset
```

---

## 二、全部量化交易策略 (等待权重集成)

### 2.1 策略清单

#### 2.1.1 GO2SE原生策略

| # | 策略 | 文件 | 功能 | 状态 | 基础权重 |
|---|------|------|------|------|---------|
| 1 | Rabbit策略 | rabbit_strategy.py | EMA/MA趋势追踪 | ✅ | 0.60 |
| 2 | Rabbit V2 | rabbit_v2_strategy.py | 增强趋势 | ✅ | 0.55 |
| 3 | Mole策略 | mole_strategy.py | RSI/CCI异动 | ✅ | 0.50 |
| 4 | Mole V2 | mole_v2_strategy.py | 增强异动 | ✅ | 0.45 |
| 5 | Oracle策略 | prediction_market_engine.py | Polymarket预测 | ✅ | 0.40 |
| 6 | Leader策略 | leader_strategy.py | 做市协作 | ✅ | 0.50 |
| 7 | Leader V2 | leader_strategy_v2.py | 增强做市 | ✅ | 0.45 |
| 8 | CopyTrading | copy_trading.py | 跟单策略 | ✅ | 0.50 |

#### 2.1.2 信号与优化策略

| # | 策略 | 文件 | 功能 | 状态 | 基础权重 |
|---|------|------|------|------|---------|
| 9 | SignalOptimizer | signal_optimizer.py | 多信号融合 | ✅ | 0.20 |
| 10 | ToolSignalIntegration | tool_signal_integration.py | 工具信号集成 | ✅ | 0.15 |
| 11 | SonarLibrary | sonar_v2.py | 123趋势模型 | ✅ | 0.15 |
| 12 | MiroFish共识 | ai_portfolio_manager.py | 450智能体 | ✅ | 0.25 |
| 13 | CrossMarket | cross_market_engine.py | 跨市场套利 | ✅ | 0.15 |

#### 2.1.3 回测与仿真策略

| # | 策略 | 文件 | 功能 | 状态 | 基础权重 |
|---|------|------|------|------|---------|
| 14 | BacktestEngine | backtest_engine.py | 回测引擎 | ✅ | 0.10 |
| 15 | BacktestMatrix | backtest_matrix.py | 回测矩阵 | ✅ | 0.10 |
| 16 | E2ESimulation | e2e_simulation.py | 端到端仿真 | ✅ | 0.10 |
| 17 | PortfolioSimulator | portfolio_simulator.py | 组合模拟 | ✅ | 0.10 |
| 18 | LeaderBacktest | leader_backtest.py | Leader回测 | ✅ | 0.10 |

#### 2.1.4 ML增强策略

| # | 策略 | 文件 | 功能 | 状态 | 基础权重 |
|---|------|------|------|---------|
| 19 | MLEngine | ml_engine.py | 机器学习引擎 | ✅ | 0.15 |
| 20 | MLEngineEnhanced | ml_engine_enhanced.py | 增强ML | ✅ | 0.20 |
| 21 | AutonomousIteration | autonomous_iteration.py | 自动迭代 | ✅ | 0.10 |

#### 2.1.5 外部策略 (MoneyClaw等)

| # | 策略 | 来源 | 功能 | 状态 | 基础权重 |
|---|------|------|------|------|---------|
| 22 | CryptoDCA | MoneyClaw | DCA定投 | ✅ | 0.15 |
| 23 | SmartRebalance | MoneyClaw | 智能再平衡 | ✅ | 0.15 |
| 24 | CryptoPriceAlert | MoneyClaw | 价格告警 | ✅ | 0.10 |
| 25 | CryptoFunding | MoneyClaw | 资金费率 | ✅ | 0.10 |

#### 2.1.6 预留策略通道

| # | 策略 | 来源 | 功能 | 状态 |
|---|------|------|------|------|
| 26 | future-strategy-1 | (待克隆) | - | ⏳ |
| 27 | future-strategy-2 | (待蒸馏) | - | ⏳ |
| 28 | future-strategy-3 | (待优化) | - | ⏳ |

### 2.2 策略调用/激活/配置

#### 2.2.1 Rabbit策略

```bash
# 调用
curl -X POST localhost:8004/api/strategies/rabbit/run \
  -d '{"symbol": "BTC/USDT", "action": "analyze"}'

# 激活
curl -X POST localhost:8004/api/strategies/rabbit/enable

# 配置
{
  "symbols": ["BTC", "ETH", "SOL", "BNB", "XRP"],
  "indicators": ["EMA_20", "EMA_50", "RSI"],
  "stop_loss": 0.05,
  "take_profit": 0.08,
  "position_limit": 0.25
}
```

#### 2.2.2 Mole策略 (火控雷达)

```bash
# 调用
curl -X POST localhost:8004/api/strategies/mole/run \
  -d '{"symbol": "SOL/USDT", "action": "scan"}'

# 激活
curl -X POST localhost:8004/api/strategies/mole/enable

# 配置
{
  "radar": {
    "volume_spike": 3.0,
    "price_change_1h": 0.05,
    "funding_rate_anomaly": 0.02
  },
  "indicators": ["RSI", "CCI", "Williams_R"],
  "stop_loss": 0.08,
  "take_profit": 0.15
}
```

#### 2.2.3 Oracle策略 (预测市场)

```bash
# 调用
curl -X POST localhost:8004/api/strategies/oracle/run \
  -d '{"market": "btc_trend", "question": "BTC > 70000 in 24h?"}'

# 激活
curl -X POST localhost:8004/api/strategies/oracle/enable

# 配置
{
  "prediction_markets": ["polymarket", "azuro", "witch"],
  "min_probability": 0.65,
  "mirofish_verification": true,
  "required_score": 70
}
```

#### 2.2.4 Leader策略 (做市)

```bash
# 调用
curl -X POST localhost:8004/api/strategies/leader/run \
  -d '{"symbol": "BTC/USDT", "action": "market_make"}'

# 激活
curl -X POST localhost:8004/api/strategies/leader/enable

# 配置
{
  "spread_min": 0.001,
  "spread_max": 0.01,
  "inventory_target": 0.50,
  "rebalance_threshold": 0.10
}
```

#### 2.2.5 SignalOptimizer (多信号融合)

```bash
# 调用
curl -X POST localhost:8004/api/signals/fuse \
  -d '{"symbol": "BTC/USDT", "sources": ["rabbit", "mole", "sonar"]}'

# 激活 (默认开启)
curl -X POST localhost:8004/api/signals/optimizer/enable

# 配置
{
  "weights": {
    "rabbit": 0.30,
    "mole": 0.25,
    "sonar": 0.20,
    "mirofish": 0.25
  },
  "fusion_method": "weighted_average"
}
```

#### 2.2.6 SonarLibrary (123趋势模型)

```bash
# 调用
curl -X POST localhost:8004/api/sonar/scan \
  -d '{"symbol": "BTC/USDT", "models": ["EMA_20", "RSI_14", "MACD"]}'

# 查看模型列表
curl localhost:8004/api/sonar/models

# 配置
{
  "enabled_models": 95,
  "categories": ["trend", "momentum", "volatility"],
  "confidence_threshold": 0.70
}
```

#### 2.2.7 MiroFish共识

```bash
# 调用
curl -X POST localhost:8004/api/oracle/mirofish/predict \
  -d '{"symbol": "BTC/USDT"}'

# 批量预测
curl -X POST localhost:8004/api/oracle/mirofish/batch \
  -d '{"symbols": ["BTC", "ETH", "SOL"]}'

# 获取状态
curl localhost:8004/api/mirofish/status

# 配置
{
  "agents": 450,
  "rounds": 5,
  "markets": ["btc_trend", "eth_trend", "sol_trend", "xrp_trend"]
}
```

#### 2.2.8 MoneyClaw策略

```bash
# DCA定投
cd /root/.openclaw/workspace/moneyclaw-py
python3 -m moneyclaw strategies/crypto_dca --config '{"coin": "BTC", "amount_usd": 10}'

# 智能再平衡
python3 -m moneyclaw strategies/smart_rebalance

# 价格告警
python3 -m moneyclaw strategies/crypto_price_alert --price 70000

# 资金费率
python3 -m moneyclaw strategies/crypto_funding
```

### 2.3 策略权重配置API

```bash
# 设置策略权重
curl -X POST localhost:8004/api/weights/strategies \
  -d '{
    "rabbit": 0.25,
    "mole": 0.20,
    "oracle": 0.15,
    "leader": 0.15,
    "hitchhiker": 0.10,
    "signal_optimizer": 0.10,
    "sonar": 0.05
  }'

# 获取当前权重
curl localhost:8004/api/weights/strategies

# 重置为默认
curl -X POST localhost:8004/api/weights/strategies/reset
```

---

## 三、克隆策略和蒸馏比较

### 3.1 克隆策略流程

```
原始策略 → 克隆 → 适应GO2SE → 权重配置 → 参与组合
```

#### 3.1.1 克隆示例

```bash
# 克隆外部策略
curl -X POST localhost:8004/api/strategies/clone \
  -d '{
    "source": "external_strategy_xyz",
    "target": "cloned_strategy_1",
    "adaptations": ["api_format", "data_source"]
  }'

# 激活克隆策略
curl -X POST localhost:8004/api/strategies/cloned_strategy_1/enable
```

### 3.2 蒸馏比较流程

```
策略A ↔ 策略B ↔ ... → MiroFish仿真 → 最优策略 → 权重调整
```

#### 3.2.1 蒸馏比较API

```bash
# 运行蒸馏比较
curl -X POST localhost:8004/api/backtest/compare \
  -d '{
    "strategies": ["rabbit", "rabbit_v2", "mole", "mole_v2"],
    "symbol": "BTC/USDT",
    "period": "90d"
  }'

# 返回结果
{
  "rankings": [
    {"strategy": "rabbit_v2", "sharpe": 1.85, "win_rate": 0.72},
    {"strategy": "rabbit", "sharpe": 1.65, "win_rate": 0.68},
    {"strategy": "mole_v2", "sharpe": 1.45, "win_rate": 0.65},
    {"strategy": "mole", "sharpe": 1.32, "win_rate": 0.62}
  ],
  "recommended": "rabbit_v2"
}
```

### 3.3 蒸馏后的策略权重调整

```bash
# 基于蒸馏结果调整权重
curl -X POST localhost:8004/api/weights/distill \
  -d '{
    "distill_results": {
      "rabbit_v2": {"sharpe": 1.85, "weight": 0.30},
      "rabbit": {"sharpe": 1.65, "weight": 0.20},
      "mole_v2": {"sharpe": 1.45, "weight": 0.15},
      "mole": {"sharpe": 1.32, "weight": 0.10}
    },
    "adjustment_method": "sharpe_proportional"
  }'
```

---

## 四、外部技能/策略集 (等待权重集成)

### 4.1 外部技能集

```yaml
# external_skills_pool.yaml
external_skills:
  # 量化交易技能
  binance_spot:
    path: skills/binance-spot-trading/
    enabled: true
    call_method: api
    weight: 0.15
    
  binance_grid:
    path: skills/binance-grid-trading/
    enabled: true
    call_method: process
    weight: 0.10
    
  polymarket:
    path: skills/polymarket-bot/
    enabled: true
    call_method: api
    weight: 0.15
    
  # 外部AI技能
  moneyclaw:
    path: skills/moneyclaw/
    enabled: true
    call_method: subprocess
    weight: 0.20
    
  agentbrain:
    path: skills/agentbrain/
    enabled: true
    call_method: npm
    weight: 0.10
    
  evomap:
    path: skills/evomap-tools/
    enabled: true
    call_method: api
    weight: 0.10
    
  # 预留通道
  future_1:
    enabled: false
    weight: 0.0
```

### 4.2 外部策略集

```yaml
# external_strategies_pool.yaml
external_strategies:
  # MoneyClaw策略
  crypto_dca:
    source: moneyclaw
    enabled: true
    weight: 0.15
    
  smart_rebalance:
    source: moneyclaw
    enabled: true
    weight: 0.15
    
  crypto_price_alert:
    source: moneyclaw
    enabled: true
    weight: 0.10
    
  crypto_funding:
    source: moneyclaw
    enabled: true
    weight: 0.10
    
  # 克隆策略
  cloned_1:
    source: external
    enabled: false
    weight: 0.0
    
  # 蒸馏策略
  distilled_1:
    source: distillation
    enabled: false
    weight: 0.0
```

---

## 五、完整权重集成API

### 5.1 获取全部技能和策略

```bash
# 获取全部技能
curl localhost:8004/api/integration/skills

# 获取全部策略
curl localhost:8004/api/integration/strategies

# 获取外部技能池
curl localhost:8004/api/integration/external-skills

# 获取外部策略池
curl localhost:8004/api/integration/external-strategies
```

### 5.2 批量权重设置

```bash
curl -X POST localhost:8004/api/weights/batch \
  -d '{
    "skills": {
      "moneyclaw": 0.20,
      "binance_grid": 0.15,
      "trading_brain": 0.25,
      "agentbrain": 0.10,
      "evomap": 0.10,
      "polymarket": 0.10,
      "others": 0.10
    },
    "strategies": {
      "rabbit": 0.25,
      "rabbit_v2": 0.15,
      "mole": 0.15,
      "mole_v2": 0.10,
      "oracle": 0.10,
      "leader": 0.10,
      "sonar": 0.05,
      "signal_optimizer": 0.05,
      "crypto_dca": 0.05
    }
  }'
```

### 5.3 权重优化触发

```bash
# 触发MiroFish权重优化
curl -X POST localhost:8004/api/weights/optimize

# 获取优化状态
curl localhost:8004/api/weights/optimize/status

# 回滚到上一组权重
curl -X POST localhost:8004/api/weights/rollback
```

---

## 六、监控面板

### 6.1 技能状态

| 技能 | 状态 | 最后调用 | 响应时间 |
|------|------|---------|---------|
| binance-spot | ✅ | 2026-04-04T08:00 | 45ms |
| binance-grid | ✅ | 2026-04-04T08:00 | 52ms |
| polymarket | ✅ | 2026-04-04T08:00 | 120ms |
| moneyclaw | ✅ | 2026-04-04T08:00 | 200ms |
| agentbrain | ✅ | 2026-04-04T08:00 | 80ms |
| evomap | ✅ | 2026-04-04T08:00 | 150ms |

### 6.2 策略状态

| 策略 | 状态 | 胜率 | 夏普比率 |
|------|------|------|---------|
| rabbit | ✅ | 68% | 1.65 |
| rabbit_v2 | ✅ | 72% | 1.85 |
| mole | ✅ | 62% | 1.32 |
| mole_v2 | ✅ | 65% | 1.45 |
| oracle | ✅ | 70% | 1.55 |
| leader | ✅ | 60% | 1.28 |
| crypto_dca | ✅ | 75% | 1.92 |
