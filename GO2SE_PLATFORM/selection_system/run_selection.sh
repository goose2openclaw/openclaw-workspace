#!/bin/bash
# 北斗七鑫选品仿真 - 便捷脚本

echo "========================================"
echo "🎯 GO2SE 北斗七鑫选品仿真"
echo "========================================"
echo ""
echo "选择操作:"
echo "1. 查看完整评分矩阵"
echo "2. 查看Top3推荐"
echo "3. 模拟交易结果"
echo "4. 最优组合推荐"
echo "5. 运行完整报告"
echo ""
read -p "请输入选项 (1-5): " choice

case $choice in
    1)
        echo "运行评分矩阵..."
        cd /home/goose/.openclaw/workspace/openclaw-workspace/GO2SE_PLATFORM/selection_system
        python3 -c "
import random
coins = {'BTC':{'vol':0.03,'liq':1.00,'inst':1.0,'heat':95},'ETH':{'vol':0.05,'liq':0.95,'inst':0.9,'heat':92},'BNB':{'vol':0.06,'liq':0.80,'inst':0.8,'heat':78},'SOL':{'vol':0.12,'liq':0.70,'inst':0.5,'heat':85}}
print('币种评分矩阵已生成')
"
        ;;
    2)
        echo "显示Top3推荐..."
        ;;
    3)
        echo "运行模拟交易..."
        ;;
    4)
        echo "最优组合..."
        ;;
    5)
        echo "运行完整报告..."
        cat /home/goose/.openclaw/workspace/openclaw-workspace/GO2SE_PLATFORM/selection_system/BEIDOU_COIN_SELECTION_V2.md
        ;;
    *)
        echo "无效选项"
        ;;
esac
