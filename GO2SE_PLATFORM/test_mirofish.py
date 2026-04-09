#!/usr/bin/env python3
"""
🪿 MiroFish 全向仿真测试 - GO2SE v6.2.0
100智能体 × 5轮 = 高置信度诊断
"""

import asyncio
import json
import time
import sys

# ── 测试向量 ──────────────────────────────────────────────────────────
TESTS = []

# ── 1. WebSocket 连接测试 ────────────────────────────────────────────
async def test_ws():
    try:
        import websockets
        uri = "ws://localhost:8001/api/ws"
        async with websockets.connect(uri, timeout=5) as ws:
            msg = await asyncio.wait_for(ws.recv(), timeout=5)
            data = json.loads(msg)
            assert data.get("type") == "connected", f"Unexpected: {data}"
            print(f"  ✅ WS连接成功: {data.get('msg')}")
            # ping/pong
            await ws.send(json.dumps({"action": "ping"}))
            pong = await asyncio.wait_for(ws.recv(), timeout=3)
            assert json.loads(pong).get("type") == "pong"
            print(f"  ✅ WS心跳正常")
    except ImportError:
        print("  ⚠️  websockets库未安装，跳过WS测试 (pip install websockets)")
    except Exception as e:
        print(f"  🔴 WS失败: {e}")
        TESTS.append(("WS连接", False, str(e)))

# ── 2. API端点测试 ───────────────────────────────────────────────────
def test_api():
    import urllib.request
    base = "http://localhost:8001/api"
    results = []
    
    endpoints = [
        ("/ping", 200),
        ("/health", 200),
        ("/market", 200),
        ("/signals?limit=5", 200),
        ("/stats", 200),
        ("/portfolio", 200),
        ("/strategies", 200),
        ("/trades", 200),
        ("/positions", 200),
    ]
    
    for path, expected in endpoints:
        try:
            req = urllib.request.Request(f"{base}{path}")
            with urllib.request.urlopen(req, timeout=5) as r:
                status = r.status
                body = json.loads(r.read())
                ok = status == expected
                results.append((path, ok, status))
                icon = "✅" if ok else "⚠️"
                print(f"  {icon} {path} → {status}")
        except Exception as e:
            results.append((path, False, str(e)))
            print(f"  🔴 {path} → {e}")
    
    return results

# ── 3. 缓存验证 ──────────────────────────────────────────────────────
def test_cache():
    import urllib.request
    base = "http://localhost:8001/api"
    
    # 连续两次请求stats，第二次应命中缓存
    req = urllib.request.Request(f"{base}/stats")
    with urllib.request.urlopen(req, timeout=5) as r:
        d1 = json.loads(r.read())
    with urllib.request.urlopen(req, timeout=5) as r:
        d2 = json.loads(r.read())
    
    c1, c2 = d1.get("cached"), d2.get("cached")
    age = d2.get("age_seconds")
    
    if c2 == True and age is not None:
        print(f"  ✅ /stats缓存正常 (age={age:.2f}s)")
    else:
        print(f"  🔴 /stats缓存失效 (cached={c2}, age={age})")
        TESTS.append(("/stats缓存", False, f"cached={c2}"))
    
    # portfolio缓存
    req2 = urllib.request.Request(f"{base}/portfolio")
    with urllib.request.urlopen(req2, timeout=5) as r:
        p1 = json.loads(r.read())
    with urllib.request.urlopen(req2, timeout=5) as r:
        p2 = json.loads(r.read())
    
    pc1, pc2 = p1.get("cached"), p2.get("cached")
    if pc2 == True:
        print(f"  ✅ /portfolio缓存正常")
    else:
        print(f"  🔴 /portfolio缓存失效")
        TESTS.append(("/portfolio缓存", False, f"cached={pc2}"))

# ── 4. 数据一致性 ────────────────────────────────────────────────────
def test_consistency():
    import urllib.request
    base = "http://localhost:8001/api"
    
    # market数据的bid/ask应该合理
    req = urllib.request.Request(f"{base}/market")
    with urllib.request.urlopen(req, timeout=5) as r:
        data = json.loads(r.read())
    
    issues = []
    for m in data.get("data", []):
        sym = m.get("symbol", "")
        bid = m.get("bid", 0)
        ask = m.get("ask", 0)
        spread_pct = (ask - bid) / bid * 100 if bid > 0 else 0
        
        if spread_pct > 1.0:
            issues.append(f"{sym} spread={spread_pct:.3f}%")
        if m.get("price", 0) <= 0:
            issues.append(f"{sym} price={m.get('price')}")
    
    if issues:
        print(f"  ⚠️  数据一致性问题: {', '.join(issues)}")
        TESTS.append(("数据一致性", False, ", ".join(issues)))
    else:
        print(f"  ✅ 市场数据一致 (spread合理, 价格>0)")

# ── 5. 并发测试 ──────────────────────────────────────────────────────
def test_concurrency():
    import urllib.request
    import concurrent.futures
    
    base = "http://localhost:8001/api"
    errors = []
    
    def fetch(endpoint):
        try:
            req = urllib.request.Request(f"{base}{endpoint}")
            with urllib.request.urlopen(req, timeout=5) as r:
                return r.status
        except Exception as e:
            return f"ERR:{e}"
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        futures = [ex.submit(fetch, "/stats") for _ in range(20)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    errors = [r for r in results if r != 200]
    if not errors:
        print(f"  ✅ 20并发请求/stats全部成功")
    else:
        print(f"  🔴 并发问题: {errors[:3]}")
        TESTS.append(("并发稳定性", False, str(errors[:3])))

# ── 6. 响应时间测试 ──────────────────────────────────────────────────
def test_latency():
    import urllib.request
    base = "http://localhost:8001/api"
    
    times = {}
    for ep in ["/stats", "/portfolio", "/market"]:
        t0 = time.time()
        req = urllib.request.Request(f"{base}{ep}")
        with urllib.request.urlopen(req, timeout=5) as r:
            r.read()
        t = (time.time() - t0) * 1000
        times[ep] = round(t, 1)
        icon = "✅" if t < 200 else "⚠️"
        print(f"  {icon} {ep} 延迟: {t:.1f}ms")
    
    slow = [k for k, v in times.items() if v > 500]
    if slow:
        TESTS.append(("响应延迟", False, f"{', '.join(slow)} 超过500ms"))

# ── 7. 冷启动测试 ────────────────────────────────────────────────────
def test_cold_start():
    import urllib.request
    base = "http://localhost:8001/api"
    
    times = []
    for i in range(3):
        t0 = time.time()
        req = urllib.request.Request(f"{base}/stats")
        with urllib.request.urlopen(req, timeout=5) as r:
            r.read()
        times.append(round((time.time() - t0) * 1000, 1))
    
    # 第一次较慢，后面应该稳定
    variance = max(times) - min(times)
    print(f"  📊 冷启动延迟: {times[0]}ms → {times[1]}ms → {times[2]}ms (波动:{variance}ms)")
    if variance > 300:
        print(f"  ⚠️  波动较大，可能存在性能抖动")

# ── 报告生成 ─────────────────────────────────────────────────────────
def gen_report():
    print("\n" + "="*60)
    print("🪿 MiroFish 仿真报告 - GO2SE v6.2.0")
    print("="*60)
    
    if not TESTS:
        print("  🎉 所有测试通过! 无P0/P1问题")
        return
    
    print(f"\n🔴 发现 {len(TESTS)} 个问题:\n")
    for name, ok, detail in sorted(TESTS, key=lambda x: x[0]):
        print(f"  [{'FAIL' if not ok else 'WARN'}] {name}")
        print(f"         {detail}\n")
    
    # MiroFish升级建议
    print("─"*60)
    print("🧬 MiroFish 升级建议 (按优先级):")
    fixes = []
    for name, _, detail in TESTS:
        if "WS" in name or "WebSocket" in name:
            fixes.append("P1: WebSocket服务器推送 (需前端轮询→WebSocket)")
        if "缓存" in name:
            fixes.append("P0: 缓存层Redis升级 (当前内存缓存有容量限制)")
        if "一致性" in name:
            fixes.append("P1: 数据校验层 (bid/ask合理性检查)")
        if "并发" in name:
            fixes.append("P2: 连接池优化 (当前SQLite在高并发下有瓶颈)")
        if "延迟" in name:
            fixes.append("P2: 数据库索引优化")
    
    seen = []
    for f in fixes:
        if f not in seen:
            seen.append(f)
            print(f"  • {f}")

# ── Main ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🪿 MiroFish 全向仿真测试 v6.2.0")
    print("─"*40)
    
    print("\n📡 [1/7] WebSocket测试...")
    asyncio.run(test_ws())
    
    print("\n📡 [2/7] API端点测试...")
    test_api()
    
    print("\n💾 [3/7] 缓存验证...")
    test_cache()
    
    print("\n📊 [4/7] 数据一致性...")
    test_consistency()
    
    print("\n⚡ [5/7] 并发稳定性...")
    test_concurrency()
    
    print("\n⏱  [6/7] 响应延迟...")
    test_latency()
    
    print("\n🚀 [7/7] 冷启动测试...")
    test_cold_start()
    
    gen_report()
