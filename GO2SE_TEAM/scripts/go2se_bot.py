#!/usr/bin/env python3
"""
🤖 GO2SE Telegram Bot
对接 GO2SE 量化交易平台
"""

import os
import json
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 配置
BOT_TOKEN = os.getenv("BOT_TOKEN", "8405295378:AAG3bvttAQkwO0tjuTo1ypw02TLSKAFLT0o")
GO2SE_API = os.getenv("GO2SE_API", "http://localhost:8000")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """启动命令"""
    await update.message.reply_text(
        "🪿 欢迎使用 GO2SE 量化交易机器人！\n\n"
        "可用命令:\n"
        "/status - 账户状态\n"
        "/signals - 交易信号\n"
        "/positions - 当前持仓\n"
        "/trades - 交易记录\n"
        "/stats - 统计数据\n"
        "/strategies - 策略列表"
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """账户状态"""
    try:
        resp = requests.get(f"{GO2SE_API}/api/stats", timeout=10)
        data = resp.json()
        
        text = f"📊 GO2SE 账户状态\n\n"
        text += f"交易模式: {data.get('data', {}).get('trading_mode', 'N/A')}\n"
        text += f"总交易: {data.get('data', {}).get('total_trades', 0)}\n"
        text += f"持仓中: {data.get('data', {}).get('open_trades', 0)}\n"
        text += f"信号总数: {data.get('data', {}).get('total_signals', 0)}\n"
        text += f"最大仓位: {data.get('data', {}).get('max_position', 0)*100}%"
        
        await update.message.reply_text(text)
    except Exception as e:
        await update.message.reply_text(f"❌ API错误: {str(e)}")

async def signals_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """交易信号"""
    try:
        resp = requests.get(f"{GO2SE_API}/api/signals", timeout=10)
        data = resp.json().get('data', [])
        
        if not data:
            await update.message.reply_text("暂无信号")
            return
            
        # 只显示最新的5个
        text = "📈 最新交易信号\n\n"
        for s in data[:5]:
            emoji = "🟢" if s['signal'] == 'buy' else "🔴" if s['signal'] == 'sell' else "⚪"
            text += f"{emoji} {s['symbol']} - {s['signal']}\n"
            text += f"   置信度: {s['confidence']} | {s['reason']}\n\n"
        
        await update.message.reply_text(text)
    except Exception as e:
        await update.message.reply_text(f"❌ API错误: {str(e)}")

async def positions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """当前持仓"""
    try:
        resp = requests.get(f"{GO2SE_API}/api/positions", timeout=10)
        data = resp.json().get('data', [])
        
        if not data:
            await update.message.reply_text("📭 当前无持仓")
            return
            
        text = "📦 当前持仓\n\n"
        for p in data:
            text += f"{p['symbol']}: {p['amount']} @ {p['entry_price']}\n"
        
        await update.message.reply_text(text)
    except Exception as e:
        await update.message.reply_text(f"❌ API错误: {str(e)}")

async def trades_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """交易记录"""
    try:
        resp = requests.get(f"{GO2SE_API}/api/trades", timeout=10)
        data = resp.json().get('data', [])
        
        if not data:
            await update.message.reply_text("📭 暂无交易记录")
            return
            
        text = "📜 交易记录\n\n"
        for t in data[:5]:
            emoji = "✅" if t.get('profit', 0) > 0 else "❌"
            text += f"{emoji} {t['symbol']} - {t['type']}\n"
        
        await update.message.reply_text(text)
    except Exception as e:
        await update.message.reply_text(f"❌ API错误: {str(e)}")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """统计数据"""
    try:
        resp = requests.get(f"{GO2SE_API}/api/stats", timeout=10)
        data = resp.json().get('data', {})
        
        text = "📊 统计概览\n\n"
        text += f"• 总交易: {data.get('total_trades', 0)}\n"
        text += f"• 执行信号: {data.get('executed_signals', 0)}\n"
        text += f"• 最大仓位: {data.get('max_position', 0)*100}%\n"
        text += f"• 止损线: {data.get('stop_loss', 0)*100}%\n"
        text += f"• 止盈线: {data.get('take_profit', 0)*100}%"
        
        await update.message.reply_text(text)
    except Exception as e:
        await update.message.reply_text(f"❌ API错误: {str(e)}")

async def strategies_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """策略列表"""
    try:
        resp = requests.get(f"{GO2SE_API}/api/strategies", timeout=10)
        data = resp.json().get('data', {})
        
        text = "🎯 活跃策略\n\n"
        for name, info in data.items():
            text += f"{info.get('name', name)}\n"
            text += f"   权重: {info.get('weight', 0)*100}% | 状态: {info.get('status')}\n\n"
        
        await update.message.reply_text(text)
    except Exception as e:
        await update.message.reply_text(f"❌ API错误: {str(e)}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """帮助"""
    text = "🪿 GO2SE 帮助\n\n"
    text += "/start - 启动机器人\n"
    text += "/status - 账户状态\n"
    text += "/signals - 交易信号\n"
    text += "/positions - 当前持仓\n"
    text += "/trades - 交易记录\n"
    text += "/stats - 统计数据\n"
    text += "/strategies - 策略列表\n"
    text += "/help - 帮助信息"
    
    await update.message.reply_text(text)

def main():
    """启动Bot"""
    app = Application.builder().token(BOT_TOKEN).build()
    
    # 注册命令
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("signals", signals_command))
    app.add_handler(CommandHandler("positions", positions_command))
    app.add_handler(CommandHandler("trades", trades_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("strategies", strategies_command))
    app.add_handler(CommandHandler("help", help_command))
    
    print("🤖 GO2SE Bot 启动中...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
