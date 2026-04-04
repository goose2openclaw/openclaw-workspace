# 🪿 GO2SE UI 三级页面体系设计规范

**版本: v9.1** | **日期: 2026-04-04** | **CEO: GO2SE 🪿**

---

## 一、页面层级架构

### 🏠 零级: 入口页 (Landing)
| 页面 | 路径 | 功能 |
|------|------|------|
| 启动页 | `/` | Logo动画 + 加载进度 |
| 登录页 | `/login` | 认证入口 |
| 注册页 | `/register` | 新用户注册 |

### 📊 一级: 主导航页 (Primary)
| 页面 | 路径 | 功能 |
|------|------|------|
| **总览** | `/dashboard` | 仪表盘 + 核心指标 |
| **市场** | `/market` | 行情 + 交易所数据 |
| **策略** | `/strategies` | 策略管理 + 工具配置 |
| **信号** | `/signals` | 信号中心 + AI分析 |
| **交易** | `/trading` | 持仓 + 订单管理 |
| **钱包** | `/wallet` | 资产管理 + 钱包 |
| **设置** | `/settings` | 系统配置 |

### 📂 二级: 功能模块页 (Secondary)
| 父级 | 二级页面 | 路径 | 功能 |
|------|----------|------|------|
| **市场** | 主流币 | `/market/top20` | 前20主流币行情 |
| | 异动币 | `/market/movers` | 涨幅榜/跌幅榜 |
| | K线详情 | `/market/kline/:symbol` | 单币K线+分析 |
| | 交易所 | `/market/exchanges` | 多交易所对比 |
| **策略** | 打兔子 | `/strategies/rabbit` | 主流币策略配置 |
| | 打地鼠 | `/strategies/mole` | 异动币策略配置 |
| | 走着瞧 | `/strategies/oracle` | 预测市场策略 |
| | 跟大哥 | `/strategies/leader` | 做市协作配置 |
| | 搭便车 | `/strategies/hitchhiker` | 跟单配置 |
| | 薅羊毛 | `/strategies/airdrop` | 空投猎手配置 |
| | 穷孩子 | `/strategies/crowdsource` | 众包赚钱配置 |
| **信号** | 信号列表 | `/signals/list` | 历史信号 |
| | 信号详情 | `/signals/:id` | 单信号分析 |
| | MiroFish | `/signals/mirofish` | 100智能体决策 |
| | 声纳库 | `/signals/sonar` | 趋势模型库 |
| **交易** | 持仓 | `/trading/positions` | 当前持仓 |
| | 历史 | `/trading/history` | 历史订单 |
| | 模拟交易 | `/trading/paper` | 模拟交易 |
| | 实盘 | `/trading/live` | 实盘交易 |
| **钱包** | 资产管理 | `/wallet/assets` | 资产总览 |
| | 充值 | `/wallet/deposit` | 充值入口 |
| | 提现 | `/wallet/withdraw` | 提现入口 |
| | 记录 | `/wallet/history` | 资金流水 |
| **设置** | 交易配置 | `/settings/trading` | 交易参数 |
| | 风控规则 | `/settings/risk` | 8大风控规则 |
| | API管理 | `/settings/api` | API Key配置 |
| | 通知 | `/settings/notifications` | 通知设置 |
| | 团队 | `/settings/team` | 团队管理 |

### 📄 三级: 详情/弹窗页 (Detail)
| 父级 | 三级页面 | 类型 | 功能 |
|------|----------|------|------|
| 信号 | 信号详情弹窗 | Modal | 信号详细分析 |
| 交易 | 订单详情 | Modal | 订单完整信息 |
| 钱包 | 转账弹窗 | Modal | 钱包转账 |
| 设置 | API编辑 | Modal | 编辑API配置 |
| K线 | 策略下单 | Modal | 从K线页面直接下单 |
| 持仓 | 止损止盈 | Modal | 修改持仓风控 |

---

## 二、导航结构

### 侧边栏设计 (Sidebar)
```
┌─────────────────────────┐
│  🪿 GO2SE (Logo)        │  ← 收起: 68px, 展开: 220px
├─────────────────────────┤
│  📊 总览                │  ← 一级入口
│  📈 市场                │  ← 展开子菜单
│  ⚙️ 策略                │  ← 展开子菜单
│  📡 信号                │  ← 展开子菜单
│  💹 交易                │  ← 展开子菜单
│  💰 钱包                │  ← 展开子菜单
│  ⚡ 设置                │  ← 展开子菜单
├─────────────────────────┤
│  🏆 会员等级            │  ← 底部状态
└─────────────────────────┘
```

### 二级导航 (Sub-nav)
```
📈 市场 > [ 主流币 | 异动币 | 交易所 ]
```

---

## 三、页面组件规范

### 3.1 卡片组件 (Card)
```html
<!-- 标准卡片 -->
<div class="card">
  <div class="card-header">
    <span class="card-title">标题</span>
    <span class="card-action">操作</span>
  </div>
  <div class="card-body">
    <!-- 内容 -->
  </div>
</div>

<!-- 卡片尺寸 -->
.card-sm   { padding: 0.75rem }   /* 小卡片 */
.card-md   { padding: 1rem }       /* 中卡片 (默认) */
.card-lg   { padding: 1.5rem }    /* 大卡片 */
```

### 3.2 表格组件 (Table)
```html
<table class="data-table">
  <thead>
    <tr>
      <th>币种</th>
      <th>价格</th>
      <th>24h涨跌</th>
      <th>信号</th>
      <th>操作</th>
    </tr>
  </thead>
  <tbody>
    <tr class="row-clickable" onclick="navigateTo('/market/kline/BTC')">
      <!-- 行数据 -->
    </tr>
  </tbody>
</table>
```

### 3.3 表单组件 (Form)
```html
<div class="form-group">
  <label class="form-label">标签</label>
  <input class="input" type="text" placeholder="请输入">
  <span class="form-hint">提示文字</span>
</div>

<!-- 按钮 -->
<button class="btn btn-primary">确定</button>
<button class="btn btn-outline">取消</button>
<button class="btn btn-buy">买入</button>
<button class="btn btn-sell">卖出</button>
```

### 3.4 图表组件 (Chart)
```html
<!-- K线图 -->
<div class="chart-container" id="kline-chart">
  <!-- ECharts 图表区 -->
</div>

<!-- 时间周期选择 -->
<div class="chart-controls">
  <button class="chart-tf" data-tf="1m">1m</button>
  <button class="chart-tf active" data-tf="5m">5m</button>
  <button class="chart-tf" data-tf="1h">1h</button>
  <button class="chart-tf" data-tf="4h">4h</button>
  <button class="chart-tf" data-tf="1d">1D</button>
</div>
```

### 3.5 状态徽章 (Badge)
```html
<span class="status-dot status-running"></span> 运行中
<span class="badge badge-success">盈利</span>
<span class="badge badge-danger">亏损</span>
<span class="badge badge-warning">待确认</span>
```

---

## 四、页面模板

### 4.1 一级页面模板
```html
<!-- 一级页面结构 -->
<div class="page">
  <div class="page-header">
    <h1 class="page-title">{页面标题}</h1>
    <div class="page-actions">
      <!-- 操作按钮 -->
    </div>
  </div>

  <div class="page-content">
    <!-- 核心内容区 -->
  </div>
</div>
```

### 4.2 二级页面模板
```html
<!-- 二级页面结构 -->
<div class="page">
  <div class="page-header">
    <div class="breadcrumb">
      <a href="/{父级路径}">{父级}</a>
      <span class="separator">/</span>
      <span class="current">{当前}</span>
    </div>
    <h1 class="page-title">{页面标题}</h1>
  </div>

  <!-- 标签切换 (如有) -->
  <div class="tab-nav">
    <button class="tab active">Tab1</button>
    <button class="tab">Tab2</button>
  </div>

  <div class="page-content">
    <!-- 内容 -->
  </div>
</div>
```

---

## 五、响应式断点

| 断点 | 宽度 | 侧边栏 | 网格 |
|------|------|--------|------|
| Mobile | <768px | 隐藏 | 1列 |
| Tablet | 768-1024px | 折叠 | 2列 |
| Desktop | 1024-1400px | 展开 | 3-4列 |
| Wide | >1400px | 展开 | 4-6列 |

---

## 六、页面清单 (完整)

### 一级页面 (7个)
1. `/dashboard` - 总览
2. `/market` - 市场
3. `/strategies` - 策略
4. `/signals` - 信号
5. `/trading` - 交易
6. `/wallet` - 钱包
7. `/settings` - 设置

### 二级页面 (28个)
| 父级 | 页面 | 路径 |
|------|------|------|
| 市场 | 主流币 | `/market/top20` |
| | 异动币 | `/market/movers` |
| | K线详情 | `/market/kline/:symbol` |
| | 交易所 | `/market/exchanges` |
| 策略 | 打兔子 | `/strategies/rabbit` |
| | 打地鼠 | `/strategies/mole` |
| | 走着瞧 | `/strategies/oracle` |
| | 跟大哥 | `/strategies/leader` |
| | 搭便车 | `/strategies/hitchhiker` |
| | 薅羊毛 | `/strategies/airdrop` |
| | 穷孩子 | `/strategies/crowdsource` |
| 信号 | 信号列表 | `/signals/list` |
| | 信号详情 | `/signals/:id` |
| | MiroFish | `/signals/mirofish` |
| | 声纳库 | `/signals/sonar` |
| 交易 | 持仓 | `/trading/positions` |
| | 历史 | `/trading/history` |
| | 模拟交易 | `/trading/paper` |
| | 实盘交易 | `/trading/live` |
| 钱包 | 资产管理 | `/wallet/assets` |
| | 充值 | `/wallet/deposit` |
| | 提现 | `/wallet/withdraw` |
| | 记录 | `/wallet/history` |
| 设置 | 交易配置 | `/settings/trading` |
| | 风控规则 | `/settings/risk` |
| | API管理 | `/settings/api` |
| | 通知 | `/settings/notifications` |
| | 团队 | `/settings/team` |

### 三级弹窗 (6个)
1. 信号详情弹窗
2. 订单详情弹窗
3. 转账弹窗
4. API编辑弹窗
5. 策略下单弹窗
6. 止损止盈弹窗

---

**总计: 1入口 + 7一级 + 28二级 + 6三级 = 42个页面/弹窗**

---

**CEO: GO2SE 🪿 | UI三级页面设计 | 2026-04-04**
