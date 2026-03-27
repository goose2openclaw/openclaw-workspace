-- ═══════════════════════════════════════════════════════════════════════════════
-- 🪿 GO2SE 数据库初始化脚本
-- ═══════════════════════════════════════════════════════════════════════════════

-- 1. 交易记录表
CREATE TABLE IF NOT EXISTS trades (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(100) UNIQUE,
    symbol VARCHAR(20) NOT NULL,
    side VARCHAR(10) NOT NULL,  -- buy/sell
    amount DECIMAL(20, 8) NOT NULL,
    price DECIMAL(20, 8),
    fee DECIMAL(20, 8) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'open',  -- open/closed/cancelled
    pnl DECIMAL(20, 8) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP
);

CREATE INDEX idx_trades_symbol ON trades(symbol);
CREATE INDEX idx_trades_status ON trades(status);
CREATE INDEX idx_trades_created_at ON trades(created_at);

-- 2. 持仓表
CREATE TABLE IF NOT EXISTS positions (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL UNIQUE,
    amount DECIMAL(20, 8) NOT NULL,
    avg_price DECIMAL(20, 8) NOT NULL,
    current_price DECIMAL(20, 8),
    unrealized_pnl DECIMAL(20, 8) DEFAULT 0,
    realized_pnl DECIMAL(20, 8) DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. 信号记录表
CREATE TABLE IF NOT EXISTS signals (
    id SERIAL PRIMARY KEY,
    strategy VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    signal VARCHAR(10) NOT NULL,  -- buy/sell/hold
    confidence DECIMAL(5, 2) NOT NULL,
    price DECIMAL(20, 8),
    reason TEXT,
    executed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_signals_strategy ON signals(strategy);
CREATE INDEX idx_signals_symbol ON signals(symbol);
CREATE INDEX idx_signals_created_at ON signals(created_at);

-- 4. 策略执行记录
CREATE TABLE IF NOT EXISTS strategy_runs (
    id SERIAL PRIMARY KEY,
    strategy VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,  -- running/success/error
    duration_ms INTEGER,
    signals_count INTEGER,
    errors TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_strategy_runs_strategy ON strategy_runs(strategy);
CREATE INDEX idx_strategy_runs_created_at ON strategy_runs(created_at);

-- 5. 风控日志
CREATE TABLE IF NOT EXISTS risk_logs (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB,
    severity VARCHAR(20) DEFAULT 'info',  -- info/warning/error/critical
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_risk_logs_event_type ON risk_logs(event_type);
CREATE INDEX idx_risk_logs_severity ON risk_logs(severity);
CREATE INDEX idx_risk_logs_created_at ON risk_logs(created_at);

-- 6. API调用日志
CREATE TABLE IF NOT EXISTS api_logs (
    id SERIAL PRIMARY KEY,
    endpoint VARCHAR(100) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER,
    response_time_ms INTEGER,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_api_logs_endpoint ON api_logs(endpoint);
CREATE INDEX idx_api_logs_created_at ON api_logs(created_at);

-- 7. 账户余额快照
CREATE TABLE IF NOT EXISTS balance_snapshots (
    id SERIAL PRIMARY KEY,
    total_usdt DECIMAL(20, 8) NOT NULL,
    positions_value DECIMAL(20, 8),
    available_usdt DECIMAL(20, 8),
    unrealized_pnl DECIMAL(20, 8),
    snapshot_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_balance_snapshots_created_at ON balance_snapshots(created_at);

-- 8. 系统配置
CREATE TABLE IF NOT EXISTS config (
    key VARCHAR(100) PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入默认配置
INSERT INTO config (key, value) VALUES
    ('trading_mode', 'dry_run'),
    ('max_position', '0.6'),
    ('stop_loss', '0.10'),
    ('take_profit', '0.30'),
    ('api_rate_limit', '1200'),
    ('cache_ttl_price', '5')
ON CONFLICT (key) DO NOTHING;

-- 创建用户(可选)
-- CREATE USER go2se WITH PASSWORD 'your_password';
-- GRANT ALL PRIVILEGES ON DATABASE go2se_trading TO go2se;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO go2se;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO go2se;

-- ═══════════════════════════════════════════════════════════════════════════════
-- 初始化完成
-- ═══════════════════════════════════════════════════════════════════════════════
