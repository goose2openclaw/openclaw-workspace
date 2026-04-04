# 🪿 GO2SE UI v2.6 完整UX规范

**版本: v9.3** | **日期: 2026-04-04** | **CEO: GO2SE 🪿**

---

## 一、Header状态呼吸灯 (Alert Aggregation)

### 1.1 多级提醒汇总
```javascript
ALERT_LEVELS = {
  critical: { color: 'red', priority: 1, icon: '🚨', description: '系统崩溃/资金安全' },
  warning: { color: 'yellow', priority: 2, icon: '⚠️', description: '风控警告/性能下降' },
  info: { color: 'blue', priority: 3, icon: '💬', description: '新消息/客服回复' },
  success: { color: 'green', priority: 4, icon: '✅', description: '任务完成/收益到账' },
}
```

### 1.2 快捷路由菜单
```html
<!-- 状态灯下拉 -->
<div class="status-dropdown">
  <div class="alert-item critical" @click="routeTo('/security')">
    🚨 系统崩溃 - 立即处理
  </div>
  <div class="alert-item warning" @click="routeTo('/risk')">
    ⚠️ 风控警告 - 2个待处理
  </div>
  <div class="alert-item info" @click="routeTo('/im')">
    💬 新消息 - 3条未读
  </div>
  <div class="alert-item success" @click="routeTo('/收益')">
    ✅ 空投到账 - $23.5
  </div>
</div>
```

---

## 二、14模块导航架构

| 索引 | 模块 | 路径 | 子项 |
|------|------|------|------|
| A | 注意力板块 | `/focus` | 热点/DIY/收藏/历史 |
| B | 宏观微观 | `/macro-micro` | 市场/个人/打工/关注 |
| C | 资产看板 | `/assets` | c1-c5 |
| D | 投资配置 | `/invest` | 打兔子/打地鼠/走着瞧/跟大哥/搭便车 |
| E | 打工配置 | `/work` | 薅羊毛/穷孩子 |
| F | 算力资源 | `/compute` | 节点/响应/延时/自检 |
| G | 信号输入 | `/signals` | Oracle/API/情绪/仿真 |
| H | 策略为王 | `/strategies` | h1-h4 |
| I | 安全机制 | `/security` | i1-i7 |
| J | 机器学习 | `/ml` | j1-j2 |
| K | 私募LP | `/private` | k1-k2 |
| L | 设置 | `/settings` | l1-l4 |
| M | 脚本日志 | `/scripts` | m1-m3 |
| N | 工程模式 | `/engineering` | n1-n3 |

---

## 三、模块详情

### C. 资产看板 (c1-c5)
```
C1: 财产总额 + 增长率
C2: 收益详情 (投资 + 打工)
C3: 钱包架构 (连接状态 + 金额)
C4: 资产分配
  - 投资部分: 各工具仓位
  - 打工部分: 薅羊毛/穷孩子
  - 保证金: 跟大哥/搭便车
  - 暂存平台: 无风险套利/保本套利
  - 内部调配: AI自动调度
C5: 模拟器
  - 回测交易
  - 模拟交易
  - 全向仿真 (推荐配置)
```

### D. 投资配置
```
打兔子: 主流趋势策略
打地鼠: 高频套利策略
走着瞧: 预测市场策略
跟大哥: 做市协作策略
搭便车: 跟单分成策略

仪表盘参数:
- 整体风格: 保守/平衡/积极
- 模式: 普通/专家
- AI推荐可调比例
- 各工具策略权重
```

### H. 策略为王 (h1-h4)
```
H1: 当前策略组合 + 构成
H2: 仿真模拟 (胜率 vs 预期)
H3: 克隆策略 (第三方平台)
H4: 策略介绍
```

### I. 安全机制 (i1-i7)
```
I1: 资金安全
I2: 后门管控
I3: 左右脑防崩溃
I4: 数据/算力安全
I5: 全向仿真 (每日/优化前)
I6: 客户端适应性
I7: 审计日志
```

### J. 机器学习 (j1-j2)
```
J1: 竞品监控 + 自主迭代
J2: 私募LP/专家定制
  - 交易习惯
  - 配置风格
  - 策略倾向
  - 保密机制
```

### K. 私募LP (k1-k2)
```
K1: 私募部落
  - 招募基金/管理人
  - Host加密货币量化群组
K2: 平台私募LP
  - 加入平台
```

### L. 设置 (l1-l4)
```
L1: 钱包架构
  - 链接/状态/金额
L2: 交易所/机构
  - CEX (Binance/Bybit/OKX)
  - DEX (Uniswap/PancakeSwap)
L3: 信息同步
  - IM同步
  - 智能办公架构
L4: OPC (一人公司)
  - 业务需求/供给
  - OPC托管
```

### M. 脚本日志 (m1-m3)
```
M1: 左右双脑备份
  - 配置自动备份
  - 数据自动备份
M2: 最佳状态点
  - 收益/胜率/抗压/记忆点
  - 两个可逆时间点
M3: 脚本日志输出
```

### N. 工程模式 (n1-n3)
```
N1: AI Debug
  - MiroFish仿真
  - 自我诊断
  - 自主迭代
N2: 终端 Termux
N3: 数据指令通道
```

---

## 四、会员权限架构

| 会员 | K私募 | L设置 | M脚本 | N工程 |
|------|-------|-------|-------|-------|
| 游客 | ❌ | ❌ | ❌ | ❌ |
| 订阅 | ❌ | l1-l2 | ❌ | ❌ |
| 会员 | ❌ | l1-l3 | m3 | ❌ |
| LP | ✅ | l1-l4 | m1-m3 | j2 |
| 专家 | ❌ | l1-l4 | m1-m3 | n1-n3 |

---

**CEO: GO2SE 🪿 | v2.6 UX完整规范 | 2026-04-04**
