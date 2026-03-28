# 📖 操作指南

## 快速开始

### 1. 启动服务
```bash
# 启动后台
cd /root/.openclaw/workspace/skills/go2se/web
python database_server.py --port 5001

# 启动前台
python server.py --port 5000
```

### 2. 访问界面
- 前台: http://localhost:5000
- 后台API: http://localhost:5001/api/

---

## 功能操作

### 查看信号
1. 打开首页
2. 查看"实时信号"表格
3. 置信度≥7.0显示🔥

### 执行交易
1. 点击"⚡买"按钮 或 信号行的"买"
2. 选择订单类型（市价/限价）
3. 输入数量
4. 点击确认

### 收藏币种
1. 点击币种卡片的⭐
2. 收藏的币种显示在"我的收藏"

---

## API接口

| 接口 | 方法 | 说明 |
|------|------|------|
| /api/signals | GET | 获取交易信号 |
| /api/market/prices | GET | 获取实时行情 |
| /api/trade/order | POST | 执行交易 |
| /api/account/balance | GET | 获取余额 |

---

## 常见问题

Q: 信号不刷新?
A: 页面每30秒自动刷新，或点击🔄

Q: 交易失败?
A: 检查API配置或使用模拟模式

---

*更新: 2026-03-13*
