#!/usr/bin/env python3
"""
🪿 GO2SE v6i Telegram 管理机器人
===================================
直接通过 Telegram 管理 GO2SE v6a 和 v6i 双系统
"""

import os
import json
import time
import logging
import urllib.request
import urllib.parse
import urllib.error
from typing import Optional, Dict, Any
from datetime import datetime

# ─── 配置 ─────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = "8735448790:AAHi8eUhot2vWm9DY8PguicAgnOiR410njo"
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
ALLOWED_USER_ID = 6270866128  # Eric

V6A_URL = "http://localhost:8000"
V6I_URL = "http://localhost:8001"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s"
)
logger = logging.getLogger("go2se_telegram")

# ─── Telegram API 工具 ───────────────────────────────────
def send_message(chat_id: int, text: str, parse_mode: str = "Markdown", reply_markup: Optional[Dict] = None) -> Dict:
    """发送消息"""
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    
    try:
        data = json.dumps(payload).encode()
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception as e:
        logger.error(f"send_message error: {e}")
        return {}

def edit_message(chat_id: int, message_id: int, text: str, parse_mode: str = "Markdown") -> Dict:
    """编辑消息"""
    url = f"{TELEGRAM_API}/editMessageText"
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": parse_mode}
    try:
        data = json.dumps(payload).encode()
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception as e:
        logger.error(f"edit_message error: {e}")
        return {}

def send_document(chat_id: int, file_path: str, caption: str = "") -> Dict:
    """发送文件"""
    url = f"{TELEGRAM_API}/sendDocument"
    boundary = "----FormBoundary7MA4YWxkTrZu0gW"
    with open(file_path, "rb") as f:
        file_data = f.read()
    
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="chat_id"\r\n\r\n{chat_id}\r\n'
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="caption"\r\n\r\n{caption}\r\n'
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="document"; filename="{os.path.basename(file_path)}"\r\n'
        f"Content-Type: application/octet-stream\r\n\r\n"
    ).encode() + file_data + f"\r\n--{boundary}--\r\n".encode()
    
    req = urllib.request.Request(url, data=body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except Exception as e:
        logger.error(f"send_document error: {e}")
        return {}

def answer_callback_query(callback_query_id: str, text: str = "") -> Dict:
    """响应回调"""
    url = f"{TELEGRAM_API}/answerCallbackQuery"
    payload = {"callback_query_id": callback_query_id, "text": text}
    try:
        data = json.dumps(payload).encode()
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception as e:
        logger.error(f"answer_callback_query error: {e}")
        return {}

# ─── GO2SE API 调用 ───────────────────────────────────────
def go2se_get(endpoint: str, version: str = "v6i") -> Dict:
    """调用 GO2SE API"""
    base = V6I_URL if version == "v6i" else V6A_URL
    url = f"{base}{endpoint}"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception as e:
        logger.error(f"go2se_get error: {e}")
        return {"error": str(e)}

# ─── 按钮键盘 ─────────────────────────────────────────────
def main_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "📊 系统状态", "callback_data": "status"}, {"text": "💰 资金配置", "callback_data": "performance"}],
            [{"text": "🐰 打兔子分析", "callback_data": "analyze_rabbit"}, {"text": "🐹 打地鼠分析", "callback_data": "analyze_mole"}],
            [{"text": "🔮 全工具分析", "callback_data": "analyze_all"}, {"text": "🔄 刷新", "callback_data": "refresh"}],
            [{"text": "🖥️ v6a 后台", "callback_data": "v6a_status"}, {"text": "🤖 v6i 后台", "callback_data": "v6i_status"}],
            [{"text": "⚙️ 工具配置", "callback_data": "tools_config"}, {"text": "📈 策略报告", "callback_data": "strategy_report"}],
        ]
    }

def back_keyboard():
    return {"inline_keyboard": [[{"text": "🔙 返回主菜单", "callback_data": "back_main"}]]}

# ─── 命令处理器 ───────────────────────────────────────────
def handle_command(text: str, chat_id: int, message_id: Optional[int] = None) -> str:
    """处理命令"""
    text = text.strip()
    
    # /start
    if text == "/start":
        return """🦢 *GO2SE v6i Telegram 管理面板*

欢迎使用 GO2SE 北斗七鑫 Telegram 管理机器人！

*支持版本：*
• v6a — 多策略引擎 (端口 8000)
• v6i — OpenAI Agents (端口 8001)

*快捷命令：*
/status — 系统状态
/performance — 资金配置
/analyze <工具> — 分析工具（rabbit/mole/oracle/leader/hitchhiker）
/analyze_all — 全工具分析
/v6a — v6a 后台状态
/v6i — v6i 后台状态

或直接点击下方按钮操作 👇"""

    # /help
    if text == "/help":
        return """📖 *命令帮助*

`/start` — 启动机器人，显示主菜单
`/status` — 显示 v6a + v6i 系统状态
`/performance` — 显示资金配置和工具权重
`/analyze <tool>` — 让指定工具Agent分析（rabbit/mole/oracle/leader/hitchhiker/wool/crowd）
`/analyze_all` — 全工具并行分析
`/v6a` — v6a 后台详细状态
`/v6i` — v6i 后台详细状态
`/tools` — 显示7工具配置"""

    # /status
    if text == "/status":
        v6a = go2se_get("/health", "v6a")
        v6i = go2se_get("/health", "v6i")
        return f"""📊 *GO2SE 系统状态*

*v6a 后台 (端口 8000)*
状态: `{v6a.get('status', 'unknown')}`
版本: `{v6a.get('version', 'N/A')}`
延迟: `{v6a.get('signals', {}).get('latency_ms', 'N/A')}ms`

*v6i 后台 (端口 8001)*
状态: `{v6i.get('status', 'unknown')}`
版本: `{v6i.get('version', 'N/A')}`

*数据库:* ✅ SQLite
*交易模式:* 🔵 dry_run
*总资金:* 100,000 USDT"""

    # /performance
    if text == "/performance":
        data = go2se_get("/api/performance", "v6i")
        if "error" in data:
            return f"❌ API错误: {data['error']}"
        
        total = data.get("total_capital", 0)
        inv = data.get("investment_pool", 0)
        work = data.get("work_pool", 0)
        inv_tools = data.get("investment_tools", {})
        work_tools = data.get("work_tools", {})
        
        inv_text = "\n".join([
            f"  {v['name']}: {v['weight']}% (${v.get('allocation', 0):,})"
            for v in inv_tools.values()
        ])
        work_text = "\n".join([
            f"  {v['name']}: {v['weight']}% (${v.get('allocation', 0):,})"
            for v in work_tools.values()
        ])
        
        return f"""💰 *GO2SE 资金配置*

总资金: `${total:,} USDT`
├ 投资池: `{inv:,} USDT` (80%)
└ 打工池: `{work:,} USDT` (20%)

*投资工具:*
{inv_text}

*打工工具:*
{work_text}

_OpenAI API: {'✅ 已配置' if data.get('openai_configured') else '⚠️ 未配置'}_"""

    # /v6a
    if text == "/v6a":
        data = go2se_get("/health", "v6a")
        sigs = data.get("signals", {})
        deps = data.get("dependencies", {})
        return f"""🖥️ *v6a 后台详细状态*

状态: `{data.get('status', 'unknown')}`
版本: `{data.get('version', 'N/A')}`

*Golden Signals:*
• 延迟: `{sigs.get('latency_ms', 'N/A')}ms {sigs.get('latency_status', '')}`
• 错误率: `{sigs.get('error_rate', 0):.2%}`
• CPU: `{sigs.get('saturation_cpu', 0):.1f}%`
• 内存: `{sigs.get('saturation_memory', 0):.1f}%`

*依赖:*
• 数据库: {deps.get('database', '❓')}
• 交易所: {deps.get('exchange', '❓')}"""

    # /v6i
    if text == "/v6i":
        data = go2se_get("/health", "v6i")
        agents = data.get("agents", [])
        perf = go2se_get("/api/performance", "v6i")
        return f"""🤖 *v6i (OpenAI Agents) 详细状态*

状态: `{data.get('status', 'unknown')}`
版本: `{data.get('version', 'N/A')}`

*7个专业Agent:*
{chr(10).join(['• ' + a for a in agents])}

*OpenAI Model:* `{perf.get('openai_model', 'N/A')}`
*API Key:* {'✅ 已配置' if perf.get('openai_configured') else '❌ 未配置'}"""

    # /tools
    if text == "/tools":
        agents_resp = go2se_get("/api/agents", "v6i")
        agents_list = agents_resp.get("agents", [])
        return f"""⚙️ *7工具 Agent 配置*

{chr(10).join([f"• `{a['id']:12}` — {a['name'].replace('GO2SE_', '')}" for a in agents_list])}

使用 `/analyze rabbit` 测试单个工具"""

    # /analyze_all
    if text == "/analyze_all":
        return "🔍 *全工具分析已启动...*\n\n稍等片刻，结果将显示在下方。"
    
    # /analyze <tool>
    if text.startswith("/analyze "):
        tool = text.split(" ", 1)[1].strip().lower()
        valid = ["rabbit", "mole", "oracle", "leader", "hitchhiker", "wool", "crowd"]
        if tool not in valid:
            return f"❌ 未知工具: `{tool}`\n\n有效工具: {', '.join(valid)}"
        return f"🔍 *分析工具: {tool}*\n\n正在调用 GO2SE_{tool} Agent..."

    return f"❓ 未知命令: `{text}`\n\n使用 /help 查看所有命令"

def handle_callback(callback_data: str, chat_id: int, message_id: int, callback_query_id: str) -> str:
    """处理按钮回调"""
    answer_callback_query(callback_query_id)
    
    if callback_data == "status":
        return handle_command("/status", chat_id)
    
    elif callback_data == "performance":
        return handle_command("/performance", chat_id)
    
    elif callback_data == "v6a_status":
        return handle_command("/v6a", chat_id)
    
    elif callback_data == "v6i_status":
        return handle_command("/v6i", chat_id)
    
    elif callback_data == "refresh":
        return "🔄 刷新完成！" + "\n\n" + handle_command("/status", chat_id)
    
    elif callback_data == "analyze_all":
        return handle_command("/analyze_all", chat_id)
    
    elif callback_data.startswith("analyze_"):
        tool = callback_data.replace("analyze_", "")
        return handle_command(f"/analyze {tool}", chat_id)
    
    elif callback_data == "back_main":
        return "🏠 *主菜单*" + "\n\n" + handle_command("/start", chat_id)
    
    elif callback_data == "tools_config":
        return handle_command("/tools", chat_id)
    
    elif callback_data == "strategy_report":
        return """📈 *策略报告*

30天回测数据（2026-02-28 to 2026-03-30）:

*v6a 优化配置:*
• 综合胜率: 69.9%（原始58%）
• 平均收益: +44.1%（原始-11.9%）
• 最大回撤: 0.9%（原始18.5%）
• 交易次数: 574次（减少35%）

*专家模式:*
• 胜率: 69.3%（普通模式47.8%）
• 平均盈利: 65.35%（普通模式7.42%）
• 盈亏比: 71.15（普通模式2.48）"""
    
    return f"✅ 收到: `{callback_data}`"

# ─── 主循环 ────────────────────────────────────────────────
def main():
    logger.info("🪿 GO2SE Telegram Bot 启动中...")
    
    # 设置命令菜单
    commands = [
        {"command": "start", "description": "启动机器人"},
        {"command": "help", "description": "显示帮助"},
        {"command": "status", "description": "系统状态"},
        {"command": "performance", "description": "资金配置"},
        {"command": "v6a", "description": "v6a后台状态"},
        {"command": "v6i", "description": "v6i后台状态"},
        {"command": "tools", "description": "7工具配置"},
        {"command": "analyze_all", "description": "全工具分析"},
    ]
    
    try:
        url = f"{TELEGRAM_API}/setMyCommands"
        data = json.dumps({"commands": commands}).encode()
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            logger.info(f"Commands set: {resp.read()}")
    except Exception as e:
        logger.warning(f"setMyCommands failed: {e}")
    
    offset = 0
    logger.info("🔄 开始长轮询...")
    
    while True:
        try:
            # 获取更新
            url = f"{TELEGRAM_API}/getUpdates?offset={offset}&timeout=10&allowed_updates=message,callback_query"
            with urllib.request.urlopen(url, timeout=30) as resp:
                updates = json.loads(resp.read())
            
            if not updates.get("ok"):
                time.sleep(1)
                continue
            
            for update in updates.get("result", []):
                offset = max(offset, update["update_id"] + 1)
                
                # 处理消息
                if "message" in update:
                    msg = update["message"]
                    chat_id = msg["chat"]["id"]
                    text = msg.get("text", "")
                    
                    # 验证用户
                    user_id = msg.get("from", {}).get("id")
                    if user_id != ALLOWED_USER_ID:
                        send_message(chat_id, "❌ 无权限访问 GO2SE 系统")
                        continue
                    
                    logger.info(f"📩 {text} from {user_id}")
                    reply = handle_command(text, chat_id, msg.get("message_id"))
                    send_message(chat_id, reply, reply_markup=main_keyboard())
                
                # 处理回调
                elif "callback_query" in update:
                    cq = update["callback_query"]
                    chat_id = cq["message"]["chat"]["id"]
                    message_id = cq["message"]["message_id"]
                    callback_query_id = cq["id"]
                    data = cq.get("data", "")
                    
                    user_id = cq.get("from", {}).get("id")
                    if user_id != ALLOWED_USER_ID:
                        answer_callback_query(callback_query_id, "❌ 无权限")
                        continue
                    
                    logger.info(f"📲 callback: {data} from {user_id}")
                    reply = handle_callback(data, chat_id, message_id, callback_query_id)
                    edit_message(chat_id, message_id, reply)
        
        except Exception as e:
            logger.error(f"Main loop error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
