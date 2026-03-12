#!/bin/bash
# XIAMI 实盘交易配置脚本

echo "=========================================="
echo "🦐 XIAMI 实盘交易配置"
echo "=========================================="
echo ""
echo "请提供以下信息:"
echo ""

read -p "交易所 (binance/bybit/okx): " EXCHANGE
read -p "API Key: " API_KEY
read -p "Secret Key: " API_SECRET

echo ""
echo "配置中..."

# 更新配置文件
cd /root/.openclaw/workspace/freqtrade-config

# 创建临时配置
cat > config_live.json.tmp << EOF
{
    "exchange": {
        "name": "$EXCHANGE",
        "key": "$API_KEY",
        "secret": "$API_SECRET",
        "ccxt_config": {},
        "ccxt_async_config": {}
    }
}
EOF

# 合并配置
python3 << PYEOF
import json

with open('config.json', 'r') as f:
    config = json.load(f)

with open('config_live.json.tmp', 'r') as f:
    live = json.load(f)

config['exchange']['name'] = live['exchange']['name']
config['exchange']['key'] = live['exchange']['key']
config['exchange']['secret'] = live['exchange']['secret']
config['dry_run'] = False

with open('config.json', 'w') as f:
    json.dump(config, f, indent=4)

print("✅ 配置完成!")
PYEOF

rm -f config_live.json.tmp

echo ""
echo "=========================================="
echo "配置完成! 请重启 FreqTrade"
echo "=========================================="
