#!/bin/bash
# 🤖 GO2SE Bot 创建脚本

# 需要先从 @BotFather 获取主 Bot Token
MAIN_BOT_TOKEN="YOUR_BOTFATHER_TOKEN"
CHAT_ID="YOUR_CHAT_ID"

# 成员配置
MEMBERS=(
  "rabbit:🐰 Rabbit:趋势信号"
  "mole:🐹 Mole:波动信号"
  "oracle:🔮 Oracle:预测分析"
  "leader:👑 Leader:做市信号"
  "hitchhiker:🍀 Hitchhiker:跟单信号"
  "airdrop:💰 Airdrop:空投提醒"
  "baby:👶 Baby:小额信号"
  "datahub:📊 DataHub:数据推送"
  "expert:🧠 Expert:决策通知"
  "turbo:⚡ Turbo:快速信号"
  "guardian:🛡️ Guardian:风控告警"
  "wallet:💰 Wallet:资金变动"
)

echo "🤖 GO2SE Bot 创建工具"
echo "========================"
echo ""
echo "请先从 @BotFather 获取 Token 并填入脚本"
echo ""
echo "配置预览:"
for m in "${MEMBERS[@]}"; do
  echo "  - ${m#*:}"
done
