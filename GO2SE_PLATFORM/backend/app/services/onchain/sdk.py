#!/usr/bin/env python3
"""
🪿 On-chain 链上分析工具
区块链追踪与地址分析
"""

import json
import random
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class Transaction:
    """链上交易"""
    hash: str
    from_address: str
    to_address: str
    value: float
    token: str
    timestamp: str
    block: int
    gas_used: int
    status: str


@dataclass
class AddressProfile:
    """地址画像"""
    address: str
    balance: float
    total_received: float
    total_sent: float
    tx_count: int
    first_seen: str
    last_seen: str
    labels: List[str]
    risk_score: float


class OnChainScanner:
    """链上扫描器"""
    
    # 模拟主流代币信息
    TOKENS = {
        "BTC": {"name": "Bitcoin", "decimals": 8},
        "ETH": {"name": "Ethereum", "decimals": 18},
        "USDT": {"name": "Tether", "decimals": 6},
        "USDC": {"name": "USD Coin", "decimals": 6},
        "BNB": {"name": "BNB", "decimals": 18},
    }
    
    def __init__(self, rpc_url: str = None):
        self.rpc_url = rpc_url or "https://eth-mainnet.alchemyapi.io"
    
    def get_address_info(self, address: str) -> AddressProfile:
        """获取地址信息"""
        # 模拟数据
        return AddressProfile(
            address=address,
            balance=random.uniform(0.1, 100),
            total_received=random.uniform(1, 1000),
            total_sent=random.uniform(0.5, 500),
            tx_count=random.randint(10, 10000),
            first_seen="2021-01-01T00:00:00Z",
            last_seen=datetime.now().isoformat(),
            labels=random.sample(["whale", "defi_user", "nft_collector", "exchange", "miner"], 
                                k=random.randint(0, 3)),
            risk_score=random.uniform(0, 30)
        )
    
    def get_transactions(self, address: str, limit: int = 20) -> List[Transaction]:
        """获取地址交易历史"""
        txs = []
        for i in range(limit):
            token = random.choice(list(self.TOKENS.keys()))
            txs.append(Transaction(
                hash=f"0x{random.randint(10**62, 10**63-1):x}",
                from_address=address if random.random() > 0.5 else f"0x{random.randint(10**39, 10**40-1):x}",
                to_address=f"0x{random.randint(10**39, 10**40-1):x}" if random.random() > 0.5 else address,
                value=random.uniform(0.01, 10),
                token=token,
                timestamp=datetime.now().isoformat(),
                block=random.randint(17000000, 19000000),
                gas_used=random.randint(21000, 500000),
                status="success"
            ))
        return txs
    
    def get_token_holdings(self, address: str) -> List[Dict]:
        """获取代币持仓"""
        holdings = []
        for token, info in self.TOKENS.items():
            balance = random.uniform(0, 1000) if token != "BTC" else random.uniform(0, 10)
            if balance > 0:
                holdings.append({
                    "token": token,
                    "name": info["name"],
                    "balance": round(balance, info["decimals"] // 3),
                    "value_usd": round(balance * random.uniform(1000, 50000), 2)
                })
        return holdings
    
    def analyze_address_behavior(self, address: str) -> Dict:
        """分析地址行为模式"""
        info = self.get_address_info(address)
        txs = self.get_transactions(address, 50)
        
        # 计算行为特征
        incoming = sum(1 for t in txs if t.to_address == address)
        outgoing = sum(1 for t in txs if t.from_address == address)
        
        avg_value = sum(t.value for t in txs) / len(txs)
        
        # 交易频率
        days_active = (datetime.now() - datetime.fromisoformat(info.first_seen.replace("Z", "+00:00"))).days
        tx_per_day = info.tx_count / max(days_active, 1)
        
        # 行为分类
        behaviors = []
        if incoming > outgoing * 2:
            behaviors.append("collector")
        elif outgoing > incoming * 2:
            behaviors.append("distributor")
        if tx_per_day > 100:
            behaviors.append("high_frequency")
        if avg_value > 1:
            behaviors.append("whale")
        
        return {
            "address": address,
            "total_txs": info.tx_count,
            "incoming_txs": incoming,
            "outgoing_txs": outgoing,
            "avg_value": round(avg_value, 4),
            "tx_per_day": round(tx_per_day, 2),
            "behaviors": behaviors,
            "risk_score": info.risk_score,
            "labels": info.labels,
            "timestamp": datetime.now().isoformat()
        }
    
    def track_funds(self, address: str, depth: int = 2) -> Dict:
        """追踪资金流向"""
        # 简化实现
        tracking = {
            "origin": address,
            "depth": depth,
            "flows": []
        }
        
        current = address
        for d in range(depth):
            txs = self.get_transactions(current, 5)
            for t in txs:
                if t.from_address != current:
                    tracking["flows"].append({
                        "depth": d + 1,
                        "from": t.from_address[:10] + "...",
                        "to": t.to_address[:10] + "...",
                        "value": t.value,
                        "token": t.token,
                        "tx_hash": t.hash[:10] + "..."
                    })
                    current = t.to_address
                    break
        
        return tracking


class MistTrack:
    """MistTrack 风格分析"""
    
    def __init__(self):
        self.scanner = OnChainScanner()
        
    def risk_analysis(self, address: str) -> Dict:
        """风险分析"""
        info = self.scanner.get_address_info(address)
        behavior = self.scanner.analyze_address_behavior(address)
        
        # 风险评分
        risk_factors = []
        risk_score = 0
        
        if info.risk_score > 20:
            risk_factors.append("高风险标签")
            risk_score += 20
        
        if len(info.labels) == 0:
            risk_factors.append("无标签地址")
            risk_score += 10
        
        if behavior["tx_per_day"] > 1000:
            risk_factors.append("高频交易")
            risk_score += 15
        
        if "exchange" in info.labels or "miner" in info.labels:
            risk_factors.append("已确认来源")
            risk_score -= 20
        
        risk_score = max(0, min(100, risk_score))
        
        risk_level = "low" if risk_score < 30 else "medium" if risk_score < 60 else "high"
        
        return {
            "address": address,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "recommendation": "safe" if risk_score < 30 else "caution" if risk_score < 60 else "avoid",
            "details": {
                "balance": info.balance,
                "tx_count": info.tx_count,
                "labels": info.labels
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def address_screening(self, addresses: List[str]) -> List[Dict]:
        """批量地址筛查"""
        results = []
        for addr in addresses:
            results.append({
                "address": addr,
                **self.risk_analysis(addr)
            })
        return results


# 全局实例
onchain_scanner = OnChainScanner()
misttrack = MistTrack()


# API 接口
def get_address_info(address: str) -> Dict:
    info = onchain_scanner.get_address_info(address)
    return {
        "address": info.address,
        "balance": info.balance,
        "tx_count": info.tx_count,
        "labels": info.labels,
        "risk_score": info.risk_score
    }


def get_transactions(address: str, limit: int = 20) -> List[Dict]:
    txs = onchain_scanner.get_transactions(address, limit)
    return [{"hash": t.hash, "from": t.from_address, "to": t.to_address, 
             "value": t.value, "token": t.token, "timestamp": t.timestamp,
             "status": t.status} for t in txs]


def get_token_holdings(address: str) -> List[Dict]:
    return onchain_scanner.get_token_holdings(address)


def analyze_behavior(address: str) -> Dict:
    return onchain_scanner.analyze_address_behavior(address)


def risk_analysis(address: str) -> Dict:
    return misttrack.risk_analysis(address)


def address_screening(addresses: List[str]) -> List[Dict]:
    return misttrack.address_screening(addresses)


if __name__ == "__main__":
    print("🪿 On-chain 分析工具测试")
    print("=" * 50)
    
    test_addr = "0x742d35Cc6634C0532925a3b844Bc9e7595f0eB1E"
    
    print(f"\n📍 地址: {test_addr}")
    info = get_address_info(test_addr)
    print(f"  余额: {info['balance']:.4f} ETH")
    print(f"  交易: {info['tx_count']} 笔")
    print(f"  标签: {', '.join(info['labels']) or '无'}")
    print(f"  风险: {info['risk_score']:.1f}")
    
    print("\n⚠️ 风险分析:")
    risk = risk_analysis(test_addr)
    print(f"  风险等级: {risk['risk_level']}")
    print(f"  风险因素: {', '.join(risk['risk_factors']) or '无'}")
    print(f"  建议: {risk['recommendation']}")
    
    print("\n✅ On-chain 工具就绪")
