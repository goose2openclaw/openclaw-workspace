#!/bin/bash
# DOGE趋势监控脚本 v2.0

export HTTP_PROXY=http://172.29.144.1:7897
export HTTPS_PROXY=http://172.29.144.1:7897

echo "=========================================="
echo "🎯 DOGE 趋势监控 v2.0"
echo "=========================================="

# 获取价格
DATA=$(curl -s --proxy $HTTP_PROXY "https://api.binance.com/api/v3/ticker/price?symbols=[\"DOGEUSDT\"]")
PRICE=$(echo $DATA | python3 -c "import sys,json; print(json.load(sys.stdin)[0]['price'])")

echo "DOGE当前价格: $PRICE"

# 检查账户
echo ""
echo "=========================================="
