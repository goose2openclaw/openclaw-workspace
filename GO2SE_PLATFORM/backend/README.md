# 🪿 GO2SE 后台系统

**版本: v9.0** | **状态: ✅ 可交付** | **CEO: GO2SE 🪿**

---

## 一、快速开始

### 1. 本地运行

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动服务
python manage.py start

# 或直接运行
python -m uvicorn app.main:app --host 0.0.0.0 --port 8004
```

### 2. Docker运行

```bash
# 构建镜像
docker build -t go2se-backend .

# 启动容器
docker-compose up -d

# 查看日志
docker-compose logs -f backend
```

---

## 二、管理命令

```bash
python manage.py <命令>

命令:
  start     启动Backend
  stop      停止Backend
  restart   重启Backend
  status    检查状态
  health    健康检查
  logs      查看日志 (默认20行)
  logs N    查看最近N行日志
```

---

## 三、API端点

### 健康检查
```bash
curl http://localhost:8004/api/stats
```

### 市场数据
```bash
curl http://localhost:8004/api/market
```

### 回测参数
```bash
curl http://localhost:8004/api/backtest/params
```

### 模拟交易用户类型
```bash
curl http://localhost:8004/api/paper/user_types
```

### 专家模式杠杆等级
```bash
curl http://localhost:8004/api/expert/leverage_levels
```

### 因子状态
```bash
curl http://localhost:8004/api/factor/status
```

---

## 四、核心模块

### 4.1 路由模块 (app/api/)
| 文件 | 说明 |
|------|------|
| routes.py | 主路由 (核心API) |
| routes_v7.py | V7扩展 |
| routes_expert.py | 专家模式 |
| routes_market.py | 市场数据 |
| routes_sonar.py | 声纳库 |
| routes_backtest.py | 回测系统 |
| routes_paper_trading.py | 模拟交易 |
| routes_mirofish_decision.py | MiroFish决策 |
| routes_factor_degradation.py | 因子退化 |
| routes_ai_portfolio.py | AI组合管理 |

### 4.2 核心模块 (app/core/)
| 文件 | 说明 |
|------|------|
| config.py | 配置管理 |
| database.py | 数据库 |
| auth.py | 认证 |
| trading_engine.py | 交易引擎 |
| backtest_engine.py | 回测引擎 |
| risk_manager.py | 风控管理 |
| market_data_fetcher.py | 市场数据 |
| sonar_v2.py | 声纳库 |
| tool_signal_integration.py | 信号接入 |
| signal_optimizer.py | 信号优化 |
| autonomous_iteration.py | 自主迭代 |

### 4.3 策略模块 (app/core/)
| 文件 | 工具 |
|------|------|
| rabbit_strategy.py | 🐰 打兔子 |
| mole_strategy.py | 🐹 打地鼠 |
| prediction_market.py | 🔮 走着瞧 |
| leader_strategy.py | 👑 跟大哥 |
| copy_trading.py | 🍀 搭便车 |
| airdrop_hunter_v2.py | 💰 薅羊毛 |
| crowdsourcing.py | 👶 穷孩子 |

---

## 五、数据库

### SQLite (开发环境)
```python
from app.core.database import get_db
```

### PostgreSQL (生产环境)
```bash
# 设置环境变量
export DATABASE_URL=postgresql://user:pass@localhost/go2se
```

---

## 六、缓存

### Redis (可选)
```bash
# 启动Redis
docker-compose up -d redis

# 缓存配置
REDIS_URL=redis://localhost:6379
```

---

## 七、日志

```bash
# 查看日志
tail -f /tmp/go2se_backend.log

# 使用管理脚本
python manage.py logs 50
```

---

## 八、部署

### 8.1 Docker Compose (推荐)
```bash
docker-compose up -d
docker-compose ps
```

### 8.2 Systemd
```bash
# 创建服务文件
sudo tee /etc/systemd/system/go2se.service << EOF
[Unit]
Description=GO2SE Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/.openclaw/workspace/GO2SE_PLATFORM/backend
ExecStart=/usr/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8004
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 启用服务
sudo systemctl enable go2se
sudo systemctl start go2se
```

---

## 九、监控

### 健康检查
```bash
curl http://localhost:8004/health
```

### 性能指标
```bash
curl http://localhost:8004/api/performance
```

### 缓存统计
```bash
curl http://localhost:8004/api/cache/stats
```

---

## 十、配置

### 环境变量
| 变量 | 默认值 | 说明 |
|------|--------|------|
| PORT | 8004 | 端口 |
| HOST | 0.0.0.0 | 主机 |
| LOG_LEVEL | INFO | 日志级别 |
| CORS_ORIGINS | * | CORS源 |
| API_RATE_LIMIT | 100 | API速率限制 |
| TOTAL_CAPITAL | 100000 | 总资金 |

---

## 十一、版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v9.0 | 2026-04-04 | 可交付版本 |
| v8.0 | 2026-04-03 | 架构升级 |
| v7.0 | 2026-03-29 | gstack集成 |

---

**CEO: GO2SE 🪿 | 后台系统 | 2026-04-04**
