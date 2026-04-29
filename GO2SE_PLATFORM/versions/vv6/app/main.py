#!/usr/bin/env python3
"""
⚡ VV6 会员体系 + 资产看板 v10
==================================
出金路径自动关联 + 支付API集成 + IM通知渠道
"""

import json
import random
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="GO2SE VV6", version="10.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# ═══════════════════════════════════════════════════════════════════════
# 🏆 会员等级
# ═══════════════════════════════════════════════════════════════════════

MEMBER_TIERS = {
    "bronze": {"name": "青铜会员", "level": 1, "deposit": ["bank"], "withdraw": ["bank"], "daily": 1000, "monthly": 10000, "discount": 0},
    "silver": {"name": "白银会员", "level": 2, "deposit": ["bank", "wise"], "withdraw": ["bank", "wise"], "daily": 5000, "monthly": 50000, "discount": 10},
    "gold": {"name": "黄金会员", "level": 3, "deposit": ["bank", "wise", "paypal"], "withdraw": ["bank", "wise", "paypal"], "daily": 20000, "monthly": 200000, "discount": 20},
    "diamond": {"name": "钻石会员", "level": 4, "deposit": ["bank", "wise", "paypal", "crypto"], "withdraw": ["bank", "wise", "paypal", "crypto"], "daily": 100000, "monthly": 1000000, "discount": 35},
}

# ═══════════════════════════════════════════════════════════════════════
# 💳 支付API连接器
# ═══════════════════════════════════════════════════════════════════════

class PaymentConnector:
    """支付渠道API连接器"""
    
    def __init__(self):
        self.connected = {
            "bank": False,
            "wise": False,
            "paypal": False,
            "crypto": True  # 默认已连接
        }
        self.credentials = {}
    
    def connect(self, channel: str, credentials: Dict) -> Dict:
        """连接支付API"""
        if channel == "bank":
            # 模拟银行API连接
            self.connected["bank"] = True
            self.credentials["bank"] = {"account_id": credentials.get("account_id", "****1234"), "bank_name": credentials.get("bank_name", "Demo Bank")}
            return {"success": True, "channel": "bank", "status": "connected", "account": "****1234"}
        
        elif channel == "wise":
            # Wise API连接
            self.connected["wise"] = True
            self.credentials["wise"] = {"api_key": "****" + credentials.get("api_key", ""), "account_id": credentials.get("account_id", "wise_****")}
            return {"success": True, "channel": "wise", "status": "connected", "account": "wise_****"}
        
        elif channel == "paypal":
            # PayPal API连接
            self.connected["paypal"] = True
            self.credentials["paypal"] = {"client_id": "****" + credentials.get("client_id", ""), "email": credentials.get("email", "demo@paypal.com")}
            return {"success": True, "channel": "paypal", "status": "connected", "email": "demo@paypal.com"}
        
        elif channel == "crypto":
            self.connected["crypto"] = True
            return {"success": True, "channel": "crypto", "status": "connected"}
        
        return {"success": False, "error": "Unknown channel"}
    
    def disconnect(self, channel: str) -> Dict:
        self.connected[channel] = False
        if channel in self.credentials:
            del self.credentials[channel]
        return {"success": True, "channel": channel, "status": "disconnected"}
    
    def get_status(self) -> Dict:
        return {
            "bank": {"connected": self.connected["bank"], "credentials": "****" if "bank" in self.credentials else None},
            "wise": {"connected": self.connected["wise"], "credentials": "****" if "wise" in self.credentials else None},
            "paypal": {"connected": self.connected["paypal"], "credentials": "****" if "paypal" in self.credentials else None},
            "crypto": {"connected": self.connected["crypto"], "credentials": None}
        }
    
    def deposit(self, channel: str, amount: float, metadata: Dict) -> Dict:
        """入金"""
        if not self.connected.get(channel, False):
            return {"success": False, "error": f"{channel} not connected"}
        
        if channel == "bank":
            return {"success": True, "tx_id": f"bank_dep_{random.randint(100000,999999)}", "amount": amount, "channel": "bank", "timestamp": datetime.now().isoformat()}
        elif channel == "wise":
            return {"success": True, "tx_id": f"wise_dep_{random.randint(100000,999999)}", "amount": amount, "channel": "wise", "timestamp": datetime.now().isoformat()}
        elif channel == "paypal":
            return {"success": True, "tx_id": f"paypal_dep_{random.randint(100000,999999)}", "amount": amount, "channel": "paypal", "timestamp": datetime.now().isoformat()}
        elif channel == "crypto":
            return {"success": True, "tx_id": f"crypto_dep_{random.randint(100000,999999)}", "amount": amount, "channel": "crypto", "timestamp": datetime.now().isoformat()}
        
        return {"success": False, "error": "Unknown channel"}
    
    def withdraw(self, channel: str, amount: float, destination: str, metadata: Dict) -> Dict:
        """出金"""
        if not self.connected.get(channel, False):
            return {"success": False, "error": f"{channel} not connected"}
        
        fee = amount * 0.001 * (1 - metadata.get("discount", 0) / 100)
        actual = amount - fee
        
        if channel == "bank":
            return {"success": True, "tx_id": f"bank_wd_{random.randint(100000,999999)}", "amount": amount, "fee": fee, "actual": actual, "destination": destination, "channel": "bank", "timestamp": datetime.now().isoformat()}
        elif channel == "wise":
            return {"success": True, "tx_id": f"wise_wd_{random.randint(100000,999999)}", "amount": amount, "fee": fee, "actual": actual, "destination": destination, "channel": "wise", "timestamp": datetime.now().isoformat()}
        elif channel == "paypal":
            return {"success": True, "tx_id": f"paypal_wd_{random.randint(100000,999999)}", "amount": amount, "fee": fee, "actual": actual, "destination": destination, "channel": "paypal", "timestamp": datetime.now().isoformat()}
        elif channel == "crypto":
            return {"success": True, "tx_id": f"crypto_wd_{random.randint(100000,999999)}", "amount": amount, "fee": fee, "actual": actual, "destination": destination, "channel": "crypto", "timestamp": datetime.now().isoformat()}
        
        return {"success": False, "error": "Unknown channel"}


# ═══════════════════════════════════════════════════════════════════════
# 📱 IM通知渠道
# ═══════════════════════════════════════════════════════════════════════

class IMChannel:
    """IM通知渠道"""
    
    def __init__(self, channel_type: str):
        self.channel_type = channel_type
        self.connected = False
        self.config = {}
    
    def connect(self, config: Dict) -> Dict:
        """连接IM渠道"""
        if self.channel_type == "telegram":
            self.connected = True
            self.config = {"bot_token": "****", "chat_id": config.get("chat_id", "****")}
            return {"success": True, "channel": "telegram", "status": "connected", "chat_id": config.get("chat_id", "****")}
        
        elif self.channel_type == "whatsapp":
            self.connected = True
            self.config = {"phone": config.get("phone", "+****"), "name": config.get("name", "Demo")}
            return {"success": True, "channel": "whatsapp", "status": "connected"}
        
        elif self.channel_type == "wechat":
            self.connected = True
            self.config = {"webhook": "****", "name": config.get("name", "Demo")}
            return {"success": True, "channel": "wechat", "status": "connected"}
        
        elif self.channel_type == "slack":
            self.connected = True
            self.config = {"webhook_url": "https://hooks.slack.com/****", "channel": config.get("channel", "#alerts")}
            return {"success": True, "channel": "slack", "status": "connected", "channel": config.get("channel", "#alerts")}
        
        return {"success": False, "error": "Unknown channel"}
    
    def disconnect(self) -> Dict:
        self.connected = False
        self.config = {}
        return {"success": True, "channel": self.channel_type, "status": "disconnected"}
    
    def send(self, message: str, priority: str = "normal") -> Dict:
        """发送消息"""
        if not self.connected:
            return {"success": False, "error": f"{self.channel_type} not connected"}
        
        # 模拟发送
        msg_id = f"{self.channel_type}_{random.randint(100000,999999)}"
        return {
            "success": True,
            "channel": self.channel_type,
            "msg_id": msg_id,
            "message": message[:50] + "..." if len(message) > 50 else message,
            "priority": priority,
            "timestamp": datetime.now().isoformat()
        }


class IMNotifier:
    """IM通知管理器"""
    
    def __init__(self):
        self.channels = {
            "telegram": IMChannel("telegram"),
            "whatsapp": IMChannel("whatsapp"),
            "wechat": IMChannel("wechat"),
            "slack": IMChannel("slack")
        }
        self.notification_history = []
    
    def connect(self, channel: str, config: Dict) -> Dict:
        return self.channels[channel].connect(config) if channel in self.channels else {"success": False, "error": "Unknown channel"}
    
    def disconnect(self, channel: str) -> Dict:
        return self.channels[channel].disconnect() if channel in self.channels else {"success": False, "error": "Unknown channel"}
    
    def send(self, channel: str, message: str, priority: str = "normal") -> Dict:
        result = self.channels[channel].send(message, priority) if channel in self.channels else {"success": False, "error": "Unknown channel"}
        if result.get("success"):
            self.notification_history.append({**result, "message": message})
        return result
    
    def broadcast(self, message: str, priority: str = "normal") -> Dict:
        results = {}
        for ch in self.channels:
            if self.channels[ch].connected:
                results[ch] = self.send(ch, message, priority)
        return {"success": True, "results": results}
    
    def get_status(self) -> Dict:
        return {ch: {"connected": self.channels[ch].connected, "config": self.channels[ch].config} for ch in self.channels}
    
    def get_history(self, limit: int = 20) -> List[Dict]:
        return self.notification_history[-limit:]


# ═══════════════════════════════════════════════════════════════════════
# 👤 会员 + 账户
# ═══════════════════════════════════════════════════════════════════════

class Account:
    """账户"""
    
    WITHDRAWAL_ROUTES = {
        # 账户类型 → 默认出金路径
        "main": "cold",           # 主账户 → 冷钱包
        "trading": "backup",     # 交易账户 → 备用
        "work": "bank",           # 打工收入 → 银行
        "backup": "bank",         # 备用 → 银行
        "cold": "crypto"          # 冷钱包 → 加密
    }
    
    def __init__(self, acc_id: str, name: str, acc_type: str):
        self.id = acc_id
        self.name = name
        self.type = acc_type
        self.balance = 0.0
        self.currency = "USDT"
        self.status = "active"
        self.withdrawal_route = self.WITHDRAWAL_ROUTES.get(acc_type, "bank")
        self.transaction_history = []
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "balance": self.balance,
            "currency": self.currency,
            "status": self.status,
            "withdrawal_route": self.withdrawal_route
        }


class Member:
    """会员"""
    
    def __init__(self, mid: str, name: str, tier: str):
        self.member_id = mid
        self.name = name
        self.tier = tier
        self.accounts = {}
        self.im_channels = {}  # member_id → {telegram, whatsapp, wechat, slack}
        self.created = datetime.now().isoformat()
        self._init_accounts()
    
    def _init_accounts(self):
        self.accounts["main"] = Account(f"{self.member_id}_main", "主账户", "main")
        self.accounts["trading"] = Account(f"{self.member_id}_trading", "交易账户", "trading")
        self.accounts["work"] = Account(f"{self.member_id}_work", "打工收入", "work")
        self.accounts["backup"] = Account(f"{self.member_id}_backup", "备用账户", "backup")
        self.accounts["cold"] = Account(f"{self.member_id}_cold", "冷钱包", "cold")
    
    def total_balance(self):
        return sum(a.balance for a in self.accounts.values())
    
    def info(self):
        t = MEMBER_TIERS[self.tier]
        return {
            "member_id": self.member_id,
            "name": self.name,
            "tier": self.tier,
            "tier_name": t["name"],
            "level": t["level"],
            "total": self.total_balance(),
            "accounts": {k: v.to_dict() for k, v in self.accounts.items()},
            "im_channels": list(self.im_channels.keys()),
            "deposit_channels": t["deposit"],
            "withdraw_channels": t["withdraw"],
            "daily_limit": t["daily"],
            "discount": t["discount"]
        }
    
    def add_im_channel(self, channel: str, config: Dict):
        self.im_channels[channel] = config
    
    def get_im_channels(self):
        return self.im_channels


# ═══════════════════════════════════════════════════════════════════════
# 💰 资产看板
# ═══════════════════════════════════════════════════════════════════════

class AssetDashboard:
    def __init__(self):
        self.version = "10.0"
        self.members: Dict[str, Member] = {}
        self.payment = PaymentConnector()
        self.im = IMNotifier()
        self.txs = []
        self._init_demo()
    
    def _init_demo(self):
        # Eric - 黄金会员
        e = Member("eric_001", "Eric", "gold")
        e.accounts["main"].balance = 50000
        e.accounts["trading"].balance = 25000
        e.accounts["work"].balance = 15800
        e.accounts["backup"].balance = 5000
        e.accounts["cold"].balance = 100000
        e.add_im_channel("telegram", {"chat_id": "6270866128"})
        e.add_im_channel("whatsapp", {"phone": "+6597319708"})
        self.members["eric_001"] = e
        
        # Alice - 白银会员
        a = Member("alice_002", "Alice", "silver")
        a.accounts["main"].balance = 8000
        a.accounts["trading"].balance = 3000
        self.members["alice_002"] = a
        
        # Bob - 青铜会员
        b = Member("bob_003", "Bob", "bronze")
        b.accounts["main"].balance = 1500
        self.members["bob_003"] = b
    
    # ─── 入金 ───
    def deposit(self, mid: str, acc: str, amount: float, channel: str, notify: bool = True) -> Dict:
        if mid not in self.members: return {"success": False, "error": "Member not found"}
        m = self.members[mid]
        t = MEMBER_TIERS[m.tier]
        
        if channel not in t["deposit"]:
            return {"success": False, "error": f"{channel} not available for {t['name']}"}
        
        if amount > t["daily"]:
            return {"success": False, "error": f"Exceeds daily limit ${t['daily']}"}
        
        # 通过支付API入金
        pay_result = self.payment.deposit(channel, amount, {"member_id": mid, "account": acc, "discount": t["discount"]})
        if not pay_result["success"]:
            return pay_result
        
        fee = pay_result.get("fee", amount * 0.001 * (1 - t["discount"]/100))
        actual = amount - fee
        
        m.accounts[acc].balance += actual
        tx = {"id": f"dep_{len(self.txs)}", "type": "deposit", "mid": mid, "acc": acc, "amount": amount, "fee": fee, "actual": actual, "channel": channel, "tx_id": pay_result.get("tx_id"), "time": datetime.now().isoformat()}
        self.txs.append(tx)
        
        # IM通知
        if notify:
            for im_ch in m.im_channels:
                self.im.send(im_ch, f"💰 入金成功! ${amount} 到 {acc}", "normal")
        
        return {"success": True, "tx": tx, "account_balance": m.accounts[acc].balance, "total": m.total_balance()}
    
    # ─── 出金 ───
    def withdraw(self, mid: str, acc: str, amount: float, channel: str = None, auto_route: bool = True, notify: bool = True) -> Dict:
        if mid not in self.members: return {"success": False, "error": "Member not found"}
        m = self.members[mid]
        t = MEMBER_TIERS[m.tier]
        
        # 自动出金路径
        if auto_route and channel is None:
            route = m.accounts[acc].withdrawal_route
            channel = route if route in t["withdraw"] else t["withdraw"][0]
            channel = channel if channel in t["withdraw"] else t["withdraw"][0]
        elif channel is None:
            channel = t["withdraw"][0]
        
        if channel not in t["withdraw"]:
            return {"success": False, "error": f"{channel} not available for {t['name']}"}
        
        if m.accounts[acc].balance < amount:
            return {"success": False, "error": "Insufficient balance"}
        
        # 通过支付API出金
        pay_result = self.payment.withdraw(channel, amount, f"{acc}@{mid}", {"member_id": mid, "account": acc, "discount": t["discount"]})
        if not pay_result["success"]:
            return pay_result
        
        fee = pay_result.get("fee", amount * 0.01 * (1 - t["discount"]/100))
        m.accounts[acc].balance -= amount
        tx = {"id": f"wd_{len(self.txs)}", "type": "withdraw", "mid": mid, "acc": acc, "amount": amount, "fee": fee, "actual": pay_result.get("actual", amount - fee), "channel": channel, "route": m.accounts[acc].withdrawal_route, "tx_id": pay_result.get("tx_id"), "time": datetime.now().isoformat()}
        self.txs.append(tx)
        
        # IM通知
        if notify:
            for im_ch in m.im_channels:
                self.im.send(im_ch, f"💸 出金成功! ${amount} 从 {acc} → {channel}", "high")
        
        return {"success": True, "tx": tx, "account_balance": m.accounts[acc].balance, "total": m.total_balance()}
    
    # ─── 账户转账 ───
    def transfer(self, mid: str, frm: str, to: str, amount: float, notify: bool = True) -> Dict:
        if mid not in self.members: return {"success": False, "error": "Member not found"}
        m = self.members[mid]
        
        if m.accounts[frm].balance < amount:
            return {"success": False, "error": "Insufficient balance"}
        
        m.accounts[frm].balance -= amount
        m.accounts[to].balance += amount
        tx = {"id": f"tx_{len(self.txs)}", "type": "transfer", "mid": mid, "from": frm, "to": to, "amount": amount, "time": datetime.now().isoformat()}
        self.txs.append(tx)
        
        if notify:
            for im_ch in m.im_channels:
                self.im.send(im_ch, f"🔄 转账 ${amount} {frm} → {to}", "normal")
        
        return {"success": True, "tx": tx, "balances": {k: v.balance for k, v in m.accounts.items()}}
    
    # ─── 看板 ───
    def member_dashboard(self, mid: str) -> Dict:
        if mid not in self.members: return {"success": False, "error": "Member not found"}
        m = self.members[mid]
        return {"success": True, "member": m.info(), "recent_txs": self.txs[-10:]}
    
    def all_dashboard(self) -> Dict:
        members = [m.info() for m in self.members.values()]
        members.sort(key=lambda x: x["total"], reverse=True)
        tiers = {t: {"name": MEMBER_TIERS[t]["name"], "count": sum(1 for m in self.members.values() if m.tier == t)} for t in MEMBER_TIERS}
        return {"success": True, "members": members, "total_assets": sum(m.total_balance() for m in self.members.values()), "tiers": tiers}


db = AssetDashboard()

# ═══════════════════════════════════════════════════════════════════════
# API端点
# ═══════════════════════════════════════════════════════════════════════

@app.get("/health")
def health(): return {"status": "VV6 OK", "version": "10.0", "time": datetime.now().isoformat()}

# ─── 看板 ───
@app.get("/api/dashboard/{mid}")
def member_dash(mid): return db.member_dashboard(mid)

@app.get("/api/dashboard")
def all_dash(): return db.all_dashboard()

# ─── 支付API ───
@app.get("/api/payment/connect")
def connect_payment(channel: str, account_id: str = None, api_key: str = None, client_id: str = None, email: str = None):
    creds = {"account_id": account_id, "api_key": api_key, "client_id": client_id, "email": email}
    return db.payment.connect(channel, creds)

@app.get("/api/payment/disconnect")
def disconnect_payment(channel: str): return db.payment.disconnect(channel)

@app.get("/api/payment/status")
def payment_status(): return db.payment.get_status()

# ─── IM渠道 ───
@app.get("/api/im/connect")
def connect_im(channel: str, chat_id: str = None, phone: str = None, name: str = None, webhook_url: str = None):
    config = {"chat_id": chat_id, "phone": phone, "name": name, "webhook_url": webhook_url}
    return db.im.connect(channel, config)

@app.get("/api/im/disconnect")
def disconnect_im(channel: str): return db.im.disconnect(channel)

@app.get("/api/im/status")
def im_status(): return db.im.get_status()

@app.get("/api/im/send")
def send_im(channel: str, message: str, priority: str = "normal"): return db.im.send(channel, message, priority)

@app.get("/api/im/broadcast")
def broadcast_im(message: str, priority: str = "normal"): return db.im.broadcast(message, priority)

# ─── 交易 ───
@app.get("/api/deposit")
def deposit(mid: str, acc: str, amount: float, channel: str, notify: bool = True): return db.deposit(mid, acc, amount, channel, notify)

@app.get("/api/withdraw")
def withdraw(mid: str, acc: str, amount: float, channel: str = None, auto_route: bool = True, notify: bool = True): return db.withdraw(mid, acc, amount, channel, auto_route, notify)

@app.get("/api/transfer")
def transfer(mid: str, frm: str, to: str, amount: float, notify: bool = True): return db.transfer(mid, frm, to, amount, notify)

# ─── 会员IM配置 ───
@app.get("/api/member/{mid}/im/connect")
def member_im_connect(mid: str, channel: str, chat_id: str = None, phone: str = None, name: str = None):
    if mid not in db.members: return {"success": False, "error": "Member not found"}
    result = db.im.connect(channel, {"chat_id": chat_id, "phone": phone, "name": name})
    if result.get("success"):
        db.members[mid].add_im_channel(channel, result)
    return result

@app.get("/api/member/{mid}/im/status")
def member_im_status(mid: str):
    if mid not in db.members: return {"success": False, "error": "Member not found"}
    return {"success": True, "channels": db.members[mid].get_im_channels()}

@app.get("/api/tiers")
def tiers(): return {"success": True, "data": MEMBER_TIERS}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8016)
