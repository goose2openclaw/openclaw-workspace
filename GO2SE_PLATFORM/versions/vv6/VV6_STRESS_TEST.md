# 🦞 vv6 压力测试报告 & 优化迭代

**时间**: 2026-04-20 18:18
**系统**: vv6 (port 8006)
**状态**: Lobster引擎 (左脑·普通模式)

---

## 压测结果汇总

### 后端API测试 ✅

| 端点 | 次数 | 通过率 | 状态 |
|------|------|--------|------|
| `/health` | 50 sequential | 100% | ✅ |
| `/api/agents` | 20 sequential | 100% | ✅ |
| `/api/risk/config` | 10 sequential | 100% | ✅ |
| `/api/switch/mode` | normal↔expert | 100% | ✅ |
| `/api/switch/analyze` | 10 sequential | 100% | ✅ |

### 并发测试 ✅

| 并发数 | 总请求 | 成功 | 失败 |
|--------|--------|------|------|
| 10并发 | 10 | 10 | 0 |
| 20并发 | 20 | 20 | 0 |
| 30并发 | 30 | 30 | 0 |
| 50并发 | 50 | 50 | 0 |

### 性能基准

```
200次 /health ping:
  总耗时: 1464ms
  平均:   7.3ms/req
  评级:   ✅ 优秀 (<10ms/req)
```

---

## 发现问题 & 修复

### Issue #1: /api/analyze/all 路由冲突 ⚠️

**问题**: FastAPI优先匹配 `/api/analyze/{tool_id}` 路径参数
- 访问 `/api/analyze/all` → tool_id="all" → 不在AGENTS中 → 返回error
- 实际应该触发 `analyze_all()` 函数

**修复** (`main.py`):
```python
@app.post("/api/analyze/{tool_id}")
async def analyze(tool_id: str, symbol: str = "BTC/USDT"):
    # 路由修复: /api/analyze/all → 委托给 analyze_all
    if tool_id == "all":
        results = {}
        for tid, agent in AGENTS.items():
            try:
                result = Runner.run_sync(agent, f"分析 {symbol}，给出交易建议")
                results[tid] = {"result": result.final_output, "status": "ok"}
            except Exception as e:
                results[tid] = {"error": str(e), "status": "error"}
        return {"symbol": symbol, "tool_results": results}
```

**验证**:
```
/api/analyze/all → Keys: ['symbol', 'tool_results']
                   Tools: ['rabbit', 'mole', 'oracle', 'leader', 'hitchhiker', 'wool', 'crowd'] ✅
```

---

## vv6 vs v6i 对比

| 维度 | vv6 (8006) | v6i (8001) |
|------|------------|-------------|
| 角色 | Lobster左脑 | Hermes右脑 |
| 模式 | 普通(只做多) | 专家(多空切换) |
| 端口 | 8006 | 8001 |
| API修复 | ✅ 已修复 | N/A |
| 压测 | ✅ 100% | ✅ |
| 自主循环 | autonomous_loop.py | autonomous_loop.py |

---

## 优化建议 (v2迭代)

### P1: regime检测精度
- 当前: 本地md5 hash (确定性但不够精确)
- 建议: 接入v6a的行情API获取真实RSI

### P2: expert模式做空信号
- 当前: bear regime + conf 80 仍返回long
- 根因: regime检测的md5 hash不稳定

### P3: frontend独立化
- 当前: vv6无独立前端，共享v6a
- 建议: 创建vv6专属前端页面(粉色主题)
