# XIAMI DeFi Suite - 全流程 DeFi 解决方案

## 概述
XIAMI DeFi Suite 提供完整的去中心化金融服务，包含发币、智能合约、预言机、焚烧、资金池、做市、二级交易、社区工具、KOL 管理和 DApp 集成。

## 快速开始

```bash
cd skills/xiami/defi/scripts

# 发币
python defi_token.py create "MyToken" "MTK" 1000000

# 预言机价格
python defi_oracle.py price BTC/USDT

# 做市
python defi_liquidity.py mm BTC/USDT 10000

# KOL 跟单
python defi_community.py kol add vitalik 0x742d...
python defi_community.py kol signal vitalik ETH

# 收益率查询
python defi_community.py yield aave ETH
```

## 核心模块

### 1. 发币 (Token Creation) → `defi_token.py`
- ERC-20 / BEP-20 / SPL 代币
- 智能合约代码生成
- 代币配置管理

### 2. 预言机 (Oracle) → `defi_oracle.py`
- 多源价格聚合 (Binance/Bybit/OKX)
- TWAP 价格计算
- 价格异常监控

### 3. 流动性 & 做市 → `defi_liquidity.py`
- 资金池信息查询
- 添加/移除流动性
- 自动化做市策略

### 4. 社区 & KOL → `defi_community.py`
- 社区成员管理
- KOL 钱包追踪
- 跟单信号
- 收益率查询
- 跨链桥接
