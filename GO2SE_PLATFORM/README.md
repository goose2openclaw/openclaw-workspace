# 🪿 GO2SE Platform - 北斗七鑫量化交易系统

<p align="center">
  <img src="https://img.shields.io/badge/Version-v6-blue" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.12-green" alt="Python">
  <img src="https://img.shields.io/badge/React-18-blue" alt="React">
  <img src="https://img.shields.io/badge/Docker-Ready-blue" alt="Docker">
</p>

---

## 📁 项目结构

```
GO2SE_PLATFORM/
├── versions/
│   ├── v1/          # 基础框架
│   ├── v2/          # 策略集成
│   ├── v3/          # 专家模式
│   ├── v4/          # 生产部署
│   ├── v5/          # 监控面板
│   └── v6/          # 🔥 当前版本 (北斗七鑫)
│       ├── backend/         # Flask API
│       ├── frontend/        # React UI
│       ├── strategies/      # 7大策略
│       ├── production/      # 交易引擎
│       ├── nginx/          # Nginx配置
│       ├── docker-compose.yml
│       └── deploy.sh       # 部署脚本
└── README.md
```

---

## 🚀 快速启动

### 方式1: Docker Compose (推荐)
```bash
cd GO2SE_PLATFORM/versions/v6
cp .env.example .env
# 编辑 .env 填入API密钥
docker-compose up -d
```

### 方式2: 开发模式
```bash
cd GO2SE_PLATFORM/versions/v6
./deploy.sh
# 选择开发模式 (选项1)
```

---

## 🎯 当前最佳策略 (v6)

| 策略 | 收益率 | 正收益概率 |
|------|--------|------------|
| 🥇 突破(15日) | +3.94% | 78% |
| 🥈 RSI(21周期) | +1.71% | - |
| 🥉 网格(3%/7%) | +0.47% | - |

---

## 📦 技术栈

- **后端**: Python Flask + SQLite
- **前端**: React 18 + TypeScript
- **交易**: Binance API
- **容器**: Docker + Docker Compose
- **策略**: Backtrader 回测框架

---

## 📞 端口映射

| 服务 | 端口 |
|------|------|
| 前端 | 3000 |
| 后端 | 5000 |
| Nginx | 80 |

---

_🪿 GO2SE - 智能量化交易平台_
