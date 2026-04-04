# GO2SE v11 策略系统

## 目录结构

```
strategies/
├── config/           # 7大工具策略配置JSON
├── models/           # 123趋势模型分类
├── importers/        # 策略导入接口
├── docs/             # 接口说明文档
└── signals/          # 信号生成器
```

## 模块说明

### 1. 7大工具策略配置
- `config/rabbit.json` - 🐰 打兔子策略
- `config/mole.json` - 🐹 打地鼠策略
- `config/oracle.json` - 🔮 走着瞧策略
- `config/follow.json` - 👑 跟大哥策略
- `config/hitchhike.json` - 🍀 搭便车策略
- `config/airdrop.json` - 💰 薅羊毛策略
- `config/crowdsource.json` - 👶 穷孩子策略

### 2. 123趋势模型分类 (models/)
- 趋势类: EMA/MA/通道 (~30个)
- 动量类: RSI/MACD/ADX (~25个)
- 波动类: Bollinger/ATR (~20个)
- 成交量类: OBV/VWAP (~15个)
- 反转类: CCI/Williams %R (~15个)
- 通道类: Channel/Breakout (~10个)
- 其他专用类: (~8个)

### 3. 策略导入接口 (importers/)
- `strategy_importer.py` - 主导入器
- `config_importer.py` - 配置导入
- `model_loader.py` - 模型加载器

### 4. 接口说明文档 (docs/)
- `import_api.md` - 导入接口详细说明
