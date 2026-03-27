#!/usr/bin/env python3
"""
🪿 GO2SE 健康检查脚本
"""

import asyncio
import aiohttp
import asyncpg
import redis.asyncio as aioredis
import json
from datetime import datetime


async def check_database():
    """检查数据库"""
    try:
        db = await asyncpg.create_pool(
            "postgresql://go2se:change_me_in_production@localhost:5432/go2se_trading",
            min_size=1,
            max_size=1
        )
        async with db.acquire() as conn:
            await conn.fetchval("SELECT 1")
        await db.close()
        return {"status": "ok", "message": "PostgreSQL connected"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def check_redis():
    """检查Redis"""
    try:
        redis = await aioredis.from_url("redis://localhost:6379/0")
        await redis.ping()
        await redis.close()
        return {"status": "ok", "message": "Redis connected"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def check_exchange():
    """检查交易所API"""
    try:
        import ccxt
        exchange = ccxt.binance()
        time = await exchange.fetch_time()
        return {"status": "ok", "message": f"Binance API OK (time: {time})"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def check_api():
    """检查API服务"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/health") as resp:
                data = await resp.json()
                return {"status": "ok", "data": data}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def main():
    print("🪿 GO2SE 健康检查")
    print("=" * 50)
    
    checks = {
        "数据库": await check_database(),
        "Redis": await check_redis(),
        "交易所API": await check_exchange(),
        "API服务": await check_api()
    }
    
    all_ok = True
    for name, result in checks.items():
        status = "✅" if result["status"] == "ok" else "❌"
        print(f"{status} {name}: {result.get('message', result.get('data', 'N/A'))}")
        
        if result["status"] != "ok":
            all_ok = False
    
    print("=" * 50)
    if all_ok:
        print("✅ 所有服务正常")
    else:
        print("❌ 部分服务异常")
    
    return 0 if all_ok else 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
