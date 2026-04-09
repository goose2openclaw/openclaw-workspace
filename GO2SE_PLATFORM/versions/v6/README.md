# 🪿 GO2SE Platform v6 - 北斗七鑫

## 当前版本

### 目录结构
```
v6/
├── backend/         # Flask后端 (端口5000)
├── frontend/       # React前端 (端口3000)
├── strategies/     # 7大策略模块
├── production/     # 生产交易引擎
├── nginx/          # Nginx配置
├── docker-compose.yml
├── deploy.sh       # 一键部署脚本
└── .env            # 环境变量
```

### 7大策略
- 🐰 rabbit - Top20趋势
- 🐹 mole - 高波动套利
- 🔮 oracle - 预测市场
- 👑 leader - 跟大哥
- 🍀 hitchhiker - 搭便车
- 💰 airdrop - 薅羊毛
- 👶 crowdsource - 众包

### 启动方式
```bash
cd versions/v6
./deploy.sh
```

### 最佳回测策略
- 突破策略(15日高点): +3.94%
- 正收益概率: 78%
