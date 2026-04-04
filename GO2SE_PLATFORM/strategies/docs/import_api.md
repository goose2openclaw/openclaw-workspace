# 策略导入接口说明

> GO2SE v11 策略系统 API Documentation

---

## 目录

1. [概述](#概述)
2. [导入接口](#导入接口)
3. [配置格式](#配置格式)
4. [模型加载](#模型加载)
5. [示例代码](#示例代码)

---

## 概述

策略导入系统负责加载和管理7大工具策略配置及123趋势模型。

### 核心组件

```
strategies/
├── importers/
│   ├── __init__.py
│   ├── base_importer.py      # 基础导入器
│   ├── strategy_importer.py  # 策略导入器
│   ├── config_importer.py    # 配置导入器
│   └── model_loader.py       # 模型加载器
├── config/                   # 7大工具策略JSON
└── models/                  # 123趋势模型
```

---

## 导入接口

### 1. StrategyImporter

策略导入器 - 加载和管理工具策略配置

```python
from importers.strategy_importer import StrategyImporter

# 初始化
importer = StrategyImporter(base_path="strategies")

# 加载所有策略
strategies = importer.load_all()

# 加载单个策略
strategy = importer.load("rabbit")  # 加载打兔子策略

# 获取启用的策略
enabled = importer.get_enabled()

# 验证策略配置
valid = importer.validate(strategy)
```

### 2. ConfigImporter

配置导入器 - 解析和验证JSON配置

```python
from importers.config_importer import ConfigImporter

# 初始化
config_importer = ConfigImporter()

# 加载JSON配置
config = config_importer.load_json("config/rabbit.json")

# 解析配置
parsed = config_importer.parse(config)

# 验证配置
errors = config_importer.validate(config)
```

### 3. ModelLoader

模型加载器 - 加载123趋势模型

```python
from importers.model_loader import ModelLoader

# 初始化
loader = ModelLoader(model_path="models")

# 加载所有模型
models = loader.load_all()

# 按类别加载
trend_models = loader.load_category("trend")
momentum_models = loader.load_category("momentum")

# 获取单个模型
rsi = loader.get("RSI_14")
```

---

## 配置格式

### 策略配置JSON结构

```json
{
  "id": "tool_rabbit",
  "name": "🐰 打兔子",
  "description": "前20主流加密货币策略",
  "version": "11.0.0",
  "enabled": true,
  "priority": 1,
  "allocation": {
    "target": 0.25,
    "min": 0.15,
    "max": 0.30
  },
  "risk": {
    "stop_loss": 0.05,
    "take_profit": 0.08,
    "max_position_size": 0.08,
    "daily_loss_limit": 0.15
  },
  "symbols": {
    "include": ["BTC", "ETH", ...],
    "exclude": []
  },
  "indicators": {
    "primary": ["EMA_20", "EMA_50"],
    "secondary": ["RSI", "MACD"]
  },
  "entry_rules": {...},
  "exit_rules": {...},
  "position_management": {...}
}
```

### 模型配置JSON结构

```json
{
  "id": "TR001",
  "name": "SMA_5",
  "category": "trend",
  "parameters": {
    "period": 5
  },
  "description": "简单移动平均5期",
  "formula": "SMA(close, 5)"
}
```

---

## 模型加载

### 模型注册表

模型注册表文件: `strategies/models/model_registry.json`

```json
{
  "version": "11.0.0",
  "total_models": 123,
  "categories": {
    "trend": 30,
    "momentum": 25,
    "volatility": 20,
    "volume": 15,
    "reversal": 15,
    "breakout": 10,
    "specialized": 8
  },
  "models": [...]
}
```

### 模型计算器

```python
from app.core.sonar_v2 import SonarCalculator

# 初始化计算器
calculator = SonarCalculator()

# 计算单个指标
result = calculator.calculate("RSI_14", ohlcv_data)

# 批量计算
results = calculator.batch_calculate(
    ["RSI_14", "MACD", "EMA_20"],
    ohlcv_data
)

# 计算所有趋势模型
trend_signals = calculator.calculate_category("trend", ohlcv_data)
```

---

## 示例代码

### 完整导入流程

```python
from importers.strategy_importer import StrategyImporter
from importers.model_loader import ModelLoader

# 1. 初始化导入器
strategy_importer = StrategyImporter("strategies")
model_loader = ModelLoader("strategies/models")

# 2. 加载策略
strategies = strategy_importer.load_all()

# 3. 加载模型
models = model_loader.load_all()

# 4. 验证配置
for name, strategy in strategies.items():
    if not strategy_importer.validate(strategy):
        print(f"Invalid strategy: {name}")

# 5. 获取启用的策略
enabled_strategies = strategy_importer.get_enabled()

# 6. 为策略分配模型
for strategy in enabled_strategies:
    strategy["indicators"]["computed"] = [
        model_loader.get(indicator)
        for indicator in strategy["indicators"]["primary"]
    ]

# 7. 返回配置
return {
    "strategies": enabled_strategies,
    "models": models
}
```

### 异步导入

```python
import asyncio
from importers.strategy_importer import StrategyImporter

async def async_load_strategies():
    importer = StrategyImporter("strategies")
    
    # 并行加载
    tasks = [
        importer.load_async("rabbit"),
        importer.load_async("mole"),
        importer.load_async("oracle"),
    ]
    
    results = await asyncio.gather(*tasks)
    return results
```

### 导入事件钩子

```python
from importers.base_importer import BaseImporter

class CustomImporter(BaseImporter):
    def on_load(self, name, data):
        print(f"Loaded: {name}")
        
    def on_validate(self, name, errors):
        if errors:
            print(f"Validation errors for {name}: {errors}")
            
    def on_error(self, name, error):
        print(f"Error loading {name}: {error}")
```

---

## REST API 端点

### GET /api/strategies

获取所有策略

```bash
curl http://localhost:8004/api/strategies
```

响应:
```json
{
  "strategies": [...],
  "total": 7,
  "enabled": 7
}
```

### GET /api/strategies/{id}

获取单个策略

```bash
curl http://localhost:8004/api/strategies/rabbit
```

### POST /api/strategies/import

导入策略配置

```bash
curl -X POST http://localhost:8004/api/strategies/import \
  -H "Content-Type: application/json" \
  -d @config/rabbit.json
```

### GET /api/models

获取所有模型

```bash
curl http://localhost:8004/api/models
```

### GET /api/models/{category}

按类别获取模型

```bash
curl http://localhost:8004/api/models/trend
```

---

## 错误码

| 错误码 | 说明 |
|--------|------|
| E001 | 配置文件不存在 |
| E002 | JSON格式错误 |
| E003 | 缺少必需字段 |
| E004 | 字段类型错误 |
| E005 | 值范围超出限制 |
| E006 | 模型ID不存在 |
| E007 | 策略ID重复 |
| E008 | 循环依赖检测 |

---

## 文件位置

- 导入器源码: `strategies/importers/`
- 策略配置: `strategies/config/`
- 模型定义: `strategies/models/`
- API路由: `backend/app/api/strategies.py`
