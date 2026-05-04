#!/bin/bash
# 自动赚钱机会监控

export HTTP_PROXY=http://172.29.144.1:7897
export HTTPS_PROXY=http://172.29.144.1:7897

echo "📊 赚钱机会自动监控"
echo "时间: $(date)"

# 获取数据
python3 << 'PYTHON'
import requests

proxies = {"http": "http://172.29.144.1:7897", "https": "http://172.29.144.1:7897"}

print("\n📈 DeFi TVL监控:")
try:
    resp = requests.get("https://api.llama.fi/protocols", proxies=proxies, timeout=10)
    protocols = resp.json()
    
    targets = {"zkSync Bridge": 0, "Linea Bridge": 0, "Alchemix V3": 0, "Nerona": 0}
    for p in protocols:
        name = p.get("name", "")
        if "zksync" in name.lower() and "bridge" in name.lower():
            tvl = sum(p.get("tvl", {}).values()) if isinstance(p.get("tvl"), dict) else p.get("tvl") or 0
            targets["zkSync Bridge"] = tvl/1e6
        elif "linea" in name.lower() and "bridge" in name.lower():
            tvl = sum(p.get("tvl", {}).values()) if isinstance(p.get("tvl"), dict) else p.get("tvl") or 0
            targets["Linea Bridge"] = tvl/1e6
        elif "alchemix" in name.lower() and "v3" in name.lower():
            tvl = sum(p.get("tvl", {}).values()) if isinstance(p.get("tvl"), dict) else p.get("tvl") or 0
            targets["Alchemix V3"] = tvl/1e6
        elif "nerona" in name.lower():
            tvl = sum(p.get("tvl", {}).values()) if isinstance(p.get("tvl"), dict) else p.get("tvl") or 0
            targets["Nerona"] = tvl/1e6
    
    for k, v in targets.items():
        print(f"  {k}: ${v:.2f}M")
except Exception as e:
    print(f"  错误: {e}")

print("\n💰 币价:")
try:
    resp = requests.get(
        "https://api.coingecko.com/api/v3/simple/price",
        params={"ids": "bitcoin,ethereum", "vs_currencies": "usd"},
        proxies=proxies, timeout=10
    )
    data = resp.json()
    print(f"  BTC: ${data.get('bitcoin', {}).get('usd', 'N/A')}")
    print(f"  ETH: ${data.get('ethereum', {}).get('usd', 'N/A')}")
except:
    print("  获取失败")
PYTHON

echo "\n✅ 监控完成"
