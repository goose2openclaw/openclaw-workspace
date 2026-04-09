# 蛛网异常监控系统 - 专家架构分析

## 一、现状分析

### 1.1 可用数据源

| 数据源 | API能力 | 覆盖范围 | 权限要求 |
|--------|---------|----------|----------|
| **CEX (中心化交易所)** | | | |
| Binance | 3537交易对 | 现货全量 | 无需API Key |
| Bybit | 现货+合约 | 全量 | 无需API Key |
| OKX | 全市场 | 全量 | 无需API Key |
| **DEX (去中心化)** | | | |
| DexScreener | pairs数据 | Solana/多链 | 公开 |
| DeFiLlama | 449链TVL | 全DeFi | 公开 |
| CoinGecko | 18203币种 | 全市场 | 公开(限速) |

### 1.2 核心问题

```
用户问题: 如何通过API连接CEX/DEX，实现4万+币种蛛网监控？
```

**问题分解:**
1. 4万币种从哪来？
2. 如何高效获取全量数据？
3. 实时排序功能怎么用？
4. API限流怎么办？

---

## 二、架构方案

### 2.1 数据源整合方案

```
┌─────────────────────────────────────────────────────────────┐
│                    数据源金字塔                               │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: 高频排序API (核心)                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Binance: /api/v3/ticker/24hr (3537对)               │   │
│  │ → 成交量排序、涨跌幅排序、价格变动排序              │   │
│  │ → 返回: price, quoteVolume, percentChange           │   │
│  └─────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: DEX聚合API                                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ DexScreener: /latest/dex/tokens/{chain}           │   │
│  │ → 代币行情+流动性                                  │   │
│  │ DeFiLlama: /chains (449链TVL)                     │   │
│  │ → 链上总锁仓量                                     │   │
│  └─────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: 全量币种库 (离线)                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ CoinGecko: /coins/list (18203币种)                 │   │
│  │ → 代币基础信息映射                                  │   │
│  │ 缓存到本地数据库                                    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 蛛网工作模式

**核心思路**: 不是监控"所有币种"，而是监控"异常排序"

```
传统方式 (不可行):
❌ 获取40000个币种 → 逐个查询 → 10万次API调用 → 限流崩溃

蛛网方式 (可行):
✅ 获取排序列表 → 只监控Top异常 → 精准打击
```

**蛛网三层:**

```python
# Layer 1: 快速排序扫描 (每秒)
# 获取24h成交量排序，取Top 100
GET /api/v3/ticker/24hr?symbol=BTCUSDT
# 排序: ?sortBy=quoteVolume&ascending=false

# Layer 2: 涨跌幅异常 (每分钟)
# 获取涨幅榜+跌幅榜
# 筛选: percentChange > 5% 或 < -5%

# Layer 3: 趋势突变 (每小时)
# 对Top 500做深度分析
# 对比: 成交量变化率、价格加速度
```

---

## 三、技术实现方案

### 3.1 API权限矩阵

| 功能 | 无API Key | 仅Public Key | Full权限 |
|------|-----------|--------------|----------|
| 行情数据 | ✅ | ✅ | ✅ |
| 24h统计 | ✅ | ✅ | ✅ |
| 排序查询 | ✅ | ✅ | ✅ |
| 订单簿 | ✅(限频) | ✅ | ✅ |
| 账户信息 | ❌ | ❌ | ✅ |
| 交易下单 | ❌ | ❌ | ✅ |

**结论**: 异常监控只需**无需API Key**

### 3.2 核心API调用策略

```python
# ===== 方案A: Binance 官方API (推荐) =====

# 1. 获取全量24h统计 (每分钟调用1次即可)
response = requests.get('https://api.binance.com/api/v3/ticker/24hr')
all_tickers = response.json()  # 3537个交易对

# 2. 本地排序筛选 (不限速)
# 按成交量排序
sorted_by_volume = sorted(all_tickers, 
    key=lambda x: float(x['quoteVolume']), reverse=True)

# 按涨跌幅排序  
sorted_by_change = sorted(all_tickers,
    key=lambda x: float(x['percentChange']), reverse=True)

# 按价格变动排序
sorted_by_price = sorted(all_tickers,
    key=lambda x: abs(float(x['lastPrice'])), reverse=True)

# ===== 方案B: 多CEX聚合 =====

EXCHANGES = {
    'binance': 'https://api.binance.com',
    'bybit': 'https://api.bybit.com',
    'okx': 'https://www.okx.com',
    'kucoin': 'https://api.kucoin.com'
}

# ===== 方案C: DEX数据 =====

# DexScreener (Solana链)
url = 'https://api.dexscreener.com/latest/dex/tokens/solana'
response = requests.get(url)
pairs = response.json()['pairs']  # 实时流动性数据

# DeFiLlama (全链TVL)
url = 'https://api.llama.fi/chains'
chains = requests.get(url).json()  # 449条链的TVL排名
```

### 3.3 蛛网扫描算法

```python
class SpiderScan:
    """蛛网扫描器"""
    
    def __init__(self):
        self.thresholds = {
            'volume_spike': 3.0,     # 成交量3倍
            'price_change': 5.0,    # 涨跌5%
            'new_listing': 0,        # 新上线检测
            'liquidity_drop': 0.5,   # 流动性下降50%
        }
    
    def scan_cex(self) -> List[Alert]:
        """CEX蛛网扫描"""
        # Step 1: 获取全量数据
        all_tickers = self.fetch_all_tickers()
        
        alerts = []
        
        # Step 2: 成交量异常检测
        for ticker in all_tickers:
            vol = float(ticker['quoteVolume'])
            if vol > self.thresholds['volume_spike'] * self.get_avg_volume(ticker['symbol']):
                alerts.append(Alert(
                    symbol=ticker['symbol'],
                    type='volume_spike',
                    severity='high'
                ))
        
        # Step 3: 涨跌幅异常
        change = float(ticker['percentChange'])
        if abs(change) > self.thresholds['price_change']:
            alerts.append(Alert(...))
        
        # Step 4: 排序突变检测
        # 对比上次排序位置
        ...
        
        return alerts
    
    def scan_dex(self) -> List[Alert]:
        """DEX蛛网扫描"""
        alerts = []
        
        # DexScreener - 获取流动性变化
        for chain in ['solana', 'ethereum', 'bsc']:
            url = f'https://api.dexscreener.com/latest/dex/tokens/{chain}'
            pairs = requests.get(url).json()['pairs']
            
            # 检测: 新对、流动性激增、价格突变
            ...
        
        return alerts
```

---

## 四、完整实现架构

```
┌──────────────────────────────────────────────────────────────┐
│                    蛛网异常监控系统                             │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │  排序API   │    │  深度分析   │    │  异常检测   │     │
│  │  (每秒)    │───▶│  (每分)    │───▶│  (实时)    │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│        │                   │                   │            │
│        ▼                   ▼                   ▼            │
│  ┌─────────────────────────────────────────────────────┐     │
│  │              异常事件队列                             │     │
│  │  - volume_spike    - price_surge    - liquidity    │     │
│  └─────────────────────────────────────────────────────┘     │
│                           │                                  │
│                           ▼                                  │
│  ┌─────────────────────────────────────────────────────┐     │
│  │         触发趋势分析 (声纳模型)                      │     │
│  └─────────────────────────────────────────────────────┘     │
│                           │                                  │
│                           ▼                                  │
│  ┌─────────────────────────────────────────────────────┐     │
│  │              信号输出 → 策略触发                      │     │
│  └─────────────────────────────────────────────────────┘     │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

---

## 五、关键技术参数

### 5.1 API调用频率

| 数据类型 | 推荐频率 | API端点 |
|----------|----------|---------|
| 全量24h | 60秒/次 | /api/v3/ticker/24hr |
| 实时价格 | 5秒/次 | /api/v3/ticker/price |
| 订单簿 | 10秒/次 | /api/v3/depth |
| 成交记录 | 30秒/次 | /api/v3/trades |

### 5.2 阈值配置

```python
ANOMALY_THRESHOLDS = {
    # 成交量类
    'volume_spike_ratio': 3.0,      # 成交量3倍
    'volume_rank_change': 50,         # 排名变动50位
    
    # 价格类
    'price_change_1m': 0.03,          # 1分钟3%
    'price_change_5m': 0.05,          # 5分钟5%
    'price_change_1h': 0.10,          # 1小时10%
    'price_drop_alert': -0.15,        # 暴跌15%
    
    # 流动性类
    'liquidity_drop': 0.50,          # 流动性下降50%
    'spread_widening': 0.05,         # 价差扩大5%
    
    # 新上线路
    'new_listing': True,              # 新币上市
    'trending_rank': 100,             # 进入热搜前100
}
```

---

## 六、推荐实现方案

### 方案优先级

| 优先级 | 方案 | 覆盖范围 | 实施难度 |
|--------|------|----------|----------|
| ⭐⭐⭐ | Binance排序API | 3500+币种 | 简单 |
| ⭐⭐⭐ | 多CEX聚合 | 8000+币种 | 中等 |
| ⭐⭐ | DexScreener | DEX热门对 | 简单 |
| ⭐ | DeFiLlama | 链上数据 | 简单 |

### 下一步行动

1. **立即可用**: Binance 24h API (3537币种)
2. **扩展范围**: 聚合 Bybit+OKx+KuCoin (8000+)
3. **深度监控**: DexScreener (DEX实时数据)
4. **预警增强**: DeFiLlama (链上异动)

---

## 结论

**蛛网模式的本质**:
- 不是"监控所有"，而是"监控异常"
- 利用交易所的**排序API**作为入口
- 异常判定后调用**声纳模型**深度分析
- 最后**触发策略**执行

这个方案完全可行，技术上没有问题。关键在于：
1. 使用排序API而非逐个查询
2. 本地计算筛选而非API端筛选
3. 分层扫描(快→准→深)

需要我基于这个架构重写异常监控模块吗？
