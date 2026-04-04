# Sidebar 子菜单重构方案

## v10.1 Sidebar 架构

### 当前结构 (7个主入口)
```
Sidebar
├── 📌 注意力
├── 💰 资产看板
├── 🎯 北斗七鑫
├── ⚙️ 工善其事
├── 🔧 可迭代定制
├── 🛡️ 安全
└── ⚙️ 设置
```

### 重构后 (5个主入口 + 子菜单)

```
Sidebar
├── 🏠 首页/总览
│   └── 快捷仪表盘
├── 💰 资产中心
│   ├── 📊 资产总览
│   ├── 📈 投资组合
│   ├── 💼 打工收益
│   └── 🎮 模拟器
├── 🎯 交易引擎
│   ├── 🐰 打兔子
│   ├── 🐹 打地鼠
│   ├── 🔮 走着瞧
│   ├── 👑 跟大哥
│   ├── 🍀 搭便车
│   ├── 💰 薅羊毛
│   └── 👶 穷孩子
├── 📡 信号策略
│   ├── 📊 市场信号
│   ├── 🏆 策略中心
│   ├── 🔄 仿真引擎
│   └── 📉 声纳库
└── ⚙️ 平台
    ├── 🔧 可迭代定制
    ├── 🛡️ 安全中心
    └── ⚙️ 设置/系统
```

## 交互设计

### 1. 主菜单项
- 点击主菜单项 → 展开/收起子菜单
- 再次点击 → 折叠子菜单

### 2. 子菜单
- 点击子菜单项 → 滚动到对应section
- 当前section高亮显示

### 3. 视觉设计
- 子菜单缩进16px
- 小箭头指示展开/折叠状态
- 动画过渡 200ms

## 技术实现

```javascript
// Sidebar Toggle
document.querySelectorAll('.sidebar-item[data-has-children]').forEach(item => {
  item.addEventListener('click', (e) => {
    e.preventDefault();
    const submenu = item.nextElementSibling;
    if (submenu.classList.contains('sidebar-submenu')) {
      submenu.classList.toggle('expanded');
      item.classList.toggle('expanded');
    }
  });
});
```

## CSS

```css
.sidebar-item[data-has-children]::after {
  content: '▶';
  font-size: 10px;
  transition: transform 0.2s;
}

.sidebar-item.expanded::after {
  transform: rotate(90deg);
}

.sidebar-submenu {
  display: none;
  padding-left: 16px;
}

.sidebar-submenu.expanded {
  display: block;
}
```

## 用户体验优化

### 优点
1. 信息架构更清晰
2. 减少一级入口到5个
3. 功能分组合理
4. 可扩展性强

### 缺点
1. 需要额外点击展开
2. 层级变深

### 解决方案
- 默认展开当前活跃模块的子菜单
- 记住用户展开状态
- 提供快捷键支持 (数字键直接跳转)
