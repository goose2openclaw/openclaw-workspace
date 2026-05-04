"""
🌐 Web3公开数据任务
====================
利用公开API创建真实打工任务
"""

import requests
from typing import List, Dict
from datetime import datetime
import time

class Web3PublicTasks:
    """Web3公开数据任务生成器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0"})
        
        # 公开API
        self.apis = {
            "llama": "https://api.llama.fi",
            "coingecko": "https://api.coingecko.com/api/v3",
            "defillama": "https://api.llama.fi",
            "crypto": "https://api.cryptoapis.io/v1",
        }
        
        # 任务模板
        self.task_templates = {
            "yield_hunt": {
                "name": "Yield Hunter",
                "description": "寻找最高收益DeFi协议",
                "reward_range": [50, 500],
                "difficulty": "medium",
                "source": "DeFiLlama"
            },
            "arb_finder": {
                "name": "Arbitrage Finder", 
                "description": "发现跨交易所套利机会",
                "reward_range": [100, 1000],
                "difficulty": "hard",
                "source": "CoinGecko"
            },
            "airdrop_tracker": {
                "name": "Airdrop Tracker",
                "description": "追踪潜在空投项目",
                "reward_range": [20, 200],
                "difficulty": "easy",
                "source": "多源"
            },
            "rug_check": {
                "name": "Rug Check",
                "description": "审计合约安全性",
                "reward_range": [30, 300],
                "difficulty": "medium",
                "source": "链上数据"
            }
        }
    
    def generate_tasks(self) -> List[Dict]:
        """生成真实Web3任务"""
        tasks = []
        
        # 1. Yield Hunter - 寻找高收益
        yield_tasks = self._fetch_yield_opportunities()
        tasks.extend(yield_tasks)
        
        # 2. Airdrop Tracker - 追踪空投
        airdrop_tasks = self._fetch_airdrop_opportunities()
        tasks.extend(airdrop_tasks)
        
        # 3. DEX Volume Tracker - 交易所数据
        dex_tasks = self._fetch_dex_opportunities()
        tasks.extend(dex_tasks)
        
        return tasks
    
    def _fetch_yield_opportunities(self) -> List[Dict]:
        """获取Yield任务"""
        tasks = []
        try:
            response = self.session.get(f"{self.apis['llama']}/protocols", timeout=10)
            if response.status_code == 200:
                protocols = response.json()[:20]  # 取前20个
                
                for i, p in enumerate(protocols):
                    if p.get("tvlUsd", 0) > 10000000:  # TVL > $10M
                        tasks.append({
                            "id": f"yield_{int(time.time())}_{i}",
                            "name": f"Yield: {p.get('name', 'Unknown')} Analysis",
                            "title": f"分析 {p.get('name')} 的Yield机会",
                            "description": f"TVL: ${p.get('tvlUsd', 0)/1e9:.1f}B, Chain: {p.get('chain', 'Multi')}",
                            "category": "yield_hunt",
                            "reward": min(500, max(50, int(p.get('tvlUsd', 0) / 1e8))),
                            "chain": p.get("chain", "Multi"),
                            "tvl": p.get("tvlUsd", 0),
                            "source": "DeFiLlama",
                            "difficulty": "medium",
                            "url": f"https://defillama.com/protocol/{p.get('name', '').lower().replace(' ', '-')}",
                            "expires_in": 3600,
                            "found_at": datetime.now().isoformat()
                        })
        except Exception as e:
            print(f"⚠️ Yield任务获取失败: {e}")
        return tasks[:10]  # 最多10个
    
    def _fetch_airdrop_opportunities(self) -> List[Dict]:
        """获取空投任务"""
        tasks = []
        
        # 潜在空投项目 (基于公开信息)
        potential_airdrops = [
            {"name": "LayerZero", "chain": "Multi", "status": "Active"},
            {"name": "Zettablock", "chain": "Ethereum", "status": "Early"},
            {"name": "Scroll", "chain": "Ethereum", "status": "Testnet"},
            {"name": "Linea", "chain": "Ethereum", "status": "Active"},
            {"name": "Polygon zkEVM", "chain": "Polygon", "status": "Active"},
            {"name": "StarkNet", "chain": "StarkNet", "status": "Active"},
            {"name": "zkSync", "chain": "zkSync", "status": "Active"},
            {"name": "Arbitrum", "chain": "Arbitrum", "status": "Active"},
        ]
        
        for i, airdrop in enumerate(potential_airdrops):
            tasks.append({
                "id": f"airdrop_{int(time.time())}_{i}",
                "name": f"Airdrop: {airdrop['name']}",
                "title": f"完成 {airdrop['name']} 测试网任务",
                "description": f"Chain: {airdrop['chain']}, Status: {airdrop['status']}",
                "category": "airdrop_tracker",
                "reward": 50 if airdrop["status"] == "Testnet" else 150,
                "chain": airdrop["chain"],
                "source": "公开信息整理",
                "difficulty": "easy",
                "url": f"https://{airdrop['name'].lower()}.xyz",
                "expires_in": 86400 * 30,
                "found_at": datetime.now().isoformat()
            })
        
        return tasks
    
    def _fetch_dex_opportunities(self) -> List[Dict]:
        """获取DEX套利任务"""
        tasks = []
        
        # 从DeFiLlama获取DEX数据
        try:
            response = self.session.get(f"{self.apis['llama']}/protocols", timeout=10)
            if response.status_code == 200:
                protocols = response.json()
                
                dexes = [p for p in protocols if p.get("category") == "DEX"][:5]
                
                for i, dex in enumerate(dexes):
                    tasks.append({
                        "id": f"dex_{int(time.time())}_{i}",
                        "name": f"DEX Analysis: {dex.get('name')}",
                        "title": f"分析 {dex.get('name')} 交易量与机会",
                        "description": f"24h Volume: ${dex.get('volume24h', 0)/1e6:.1f}M, TVL: ${dex.get('tvlUsd', 0)/1e6:.1f}M",
                        "category": "arb_finder",
                        "reward": min(300, max(50, int(dex.get("volume24h", 0) / 1e7))),
                        "chain": dex.get("chain", "Multi"),
                        "volume24h": dex.get("volume24h", 0),
                        "source": "DeFiLlama",
                        "difficulty": "hard",
                        "url": f"https://defillama.com/protocol/{dex.get('name', '').lower().replace(' ', '-')}",
                        "expires_in": 1800,
                        "found_at": datetime.now().isoformat()
                    })
        except Exception as e:
            print(f"⚠️ DEX任务获取失败: {e}")
        
        return tasks[:5]


def generate_web3_tasks() -> List[Dict]:
    """便捷函数"""
    generator = Web3PublicTasks()
    return generator.generate_tasks()
