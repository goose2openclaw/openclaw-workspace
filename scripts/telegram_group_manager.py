#!/usr/bin/env python3
"""
Telegram 群组管理 Bot
用于自动添加成员到群组
"""

import os
import json
from pathlib import Path
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 配置
BOT_TOKEN = "8393131247:AAGIfQLMtlrgOZx4ZFPriaUtL_opqXOCNDI"
DATA_FILE = "/root/.openclaw/workspace/telegram_groups.json"

# 群组配置
GROUPS = {
    "go2se": {"name": "Go2Se护食群", "chat_id": None, "invite_link": None},
    "drama_rwa": {"name": "短剧出海RWA群", "chat_id": None, "invite_link": None},
    "agam": {"name": "Agam群", "chat_id": None, "invite_link": None},
    "sg_oil": {"name": "新加坡油气群", "chat_id": None, "invite_link": None},
    "sg_job": {"name": "新加坡Jobstreet助手群", "chat_id": None, "invite_link": None},
    "rwa_token": {"name": "RWA和发币群", "chat_id": None, "invite_link": None},
    "bot_work": {"name": "Bot打工挣钱群", "chat_id": None, "invite_link": None}
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🦆 鹅王 Bot 已就绪！\n\n"
        "可用命令:\n"
        "/list - 查看所有群组\n"
        "/invite <群名> - 获取邀请链接\n"
        "/add <群名> <用户> - 添加用户"
    )

async def list_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "📋 群组列表:\n\n"
    for key, g in GROUPS.items():
        msg += f"• {g['name']}: `{key}`\n"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def get_invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("用法: /invite <群组代号>")
        return
    await update.message.reply_text("请先把 Bot 添加到群后再试")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("list", list_groups))
    app.add_handler(CommandHandler("invite", get_invite))
    print("🤖 Telegram 管理 Bot 启动中...")
    app.run_polling(pending_callback=True)

if __name__ == "__main__":
    main()
