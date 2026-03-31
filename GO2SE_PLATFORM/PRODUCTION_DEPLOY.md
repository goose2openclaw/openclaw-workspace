# 🏭 GO2SE 生产环境部署指南

## 2026-03-30

---

## 部署架构

```
                    ┌─────────────────┐
                    │   Nginx/Proxy   │
                    │   (SSL + WAF)   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Backend API    │
                    │  (Gunicorn)     │
                    │  localhost:8000 │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
     ┌────────▼────────┐     │     ┌────────▼────────┐
     │   GO2SE Core    │     │     │   MiroFish      │
     │   (Trading)     │     │     │   (Oracle)      │
     └─────────────────┘     │     └─────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │    Database       │
                    │   (SQLite/PG)     │
                    └───────────────────┘
```

---

## 部署检查清单

### 1. 环境准备
- [x] Python 3.11+
- [x] pip/venv
- [x] SQLite or PostgreSQL

### 2. 配置
```bash
# 生产环境变量
export TRADING_MODE=live
export BINANCE_API_KEY=your_api_key
export BINANCE_SECRET_KEY=your_secret_key
export LOG_LEVEL=INFO
export WORKERS=4
```

### 3. 启动命令
```bash
cd backend
gunicorn -w 4 -b 0.0.0.0:8000 app.main:app --timeout 120
```

### 4. Nginx配置
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 安全配置

### API Key权限
- 只读权限 (读取市场数据)
- 交易权限 (仅限现货)
- 禁止提现权限

### 风控规则
- 仓位限制: 60%
- 单笔风险: 5%
- 日内熔断: 15%

---

## 部署脚本
```bash
#!/bin/bash
# deploy_production.sh

export TRADING_MODE=production
export BINANCE_API_KEY=$1
export BINANCE_SECRET_KEY=$2

# 启动
cd /root/.openclaw/workspace/GO2SE_PLATFORM/backend
nohup gunicorn -w 4 -b 0.0.0.0:8000 app.main:app --timeout 120 > ../backend.log 2>&1 &

echo "GO2SE Backend started on port 8000"
```

