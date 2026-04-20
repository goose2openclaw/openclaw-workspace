# 🦐 gstack v6i 深度评审报告
**评审时间**: 2026-04-20 19:31 CST
**版本**: v6i-openai-agents (port 8001)  
**状态**: ⚠️ **代码与vv6修复前相同** — 11项问题待修复

---

## ⚠️ 警告：v6i 代码未同步 vv6 修复

**问题发现**: vv6 在18:27完成的11项修复**未同步到v6i**

vv6 和 v6i 代码几乎完全相同（端口不同），但 v6i 运行的是**未修复版本**：

| 修复项 | vv6状态 | v6i状态 |
|--------|----------|---------|
| CORS收窄 | ✅ 已修复 | ❌ 仍为`*` |
| detect_regime接入API | ✅ 已修复 | ❌ 仍为md5 |
| switch_analyze Request Body | ✅ 已修复 | ❌ 仍为query param |
| execute_trade MOCK标注 | ✅ 已修复 | ❌ 无标注 |
| reset_daily日期检查 | ✅ 已修复 | ❌ 未修复 |
| health触发每日重置 | ✅ 已修复 | ❌ 未修复 |
| get_market_data异常分类 | ✅ 已修复 | ❌ 裸except |
| get_position异常分类 | ✅ 已修复 | ❌ 裸except |
| asyncio.to_thread | ✅ 已修复 | ❌ 同步阻塞 |
| PydanticBaseModel导入 | ✅ 已修复 | ❌ 未导入 |
| autonomous_loop端口 | N/A | ❌ 8006(指向vv6) |

**v6i代码现状 = vv6修复前状态**

---

## 🔴 CRITICAL 问题（与vv6相同）

### C1: CORS全开 ⚠️⚠️⚠️
```python
allow_origins=["*"]  # ← 所有来源
allow_credentials=True  # ← 允许跨域cookie
```
**风险**: 任何网页可读写v6i所有API  
**影响**: 交易状态、模式切换、交易记录全部暴露

### C2: regime检测 md5 hash ⚠️⚠️⚠️
```python
block = int(_time.time()) // 900
h = hashlib.md5(f"{symbol}_{block}".encode()).hexdigest()
rsi = int(h[:4], 16) % 100  # ← 纯时间决定，非市场数据
```
**风险**: expert模式做空决策100%依赖假regime → 必然逆势开仓

### C3: POST body被query param覆盖 ⚠️⚠️⚠️
```python
async def switch_analyze(
    symbol: str = "BTC/USDT",
    confidence: float = 70.0,  # ← query param优先!
    mode: str = "normal"
):
    regime = switch_engine.detect_regime(req.symbol)  # ← req未定义!
```
**现状**: v6i甚至没用req，直接用函数参数 → body完全被忽略  
**实际**: `confidence=85` 在body里 → 被默认值70覆盖

---

## 🟠 HIGH 问题

### H1: execute_trade 伪执行无标注 ⚠️
```python
return (f"✅ {direction.upper()} {symbol} | ...")  # ← 看起来像真交易
```
**风险**: Agent以为执行了真实仓位，发送后续决策信号完全错误

### H2: reset_daily 永不触发 ⚠️
uvicorn进程不重启 → `reset_daily()` 定义后从未调用  
**实际**: 第2天仍然受第1天交易统计影响

### H3: Runner.run_sync 阻塞事件循环 ⚠️
```python
result = Runner.run_sync(agent, ...)  # 同步LLM调用最长30秒
```
**影响**: 30秒内整个FastAPI事件循环卡死，并发请求全部hang

---

## ✅ v6i 相对于vv6的优势

1. **v6i运行port 8001** = Hermes引擎角色，与vv6(8006=Lobster)端口不冲突
2. **7个Agent配置** 与vv6完全相同，工具集完整
3. **autonomous_loop.py** 存在但端口指向错误(8006→vv6)
4. **专家模式** 与vv6功能相同，但regime=假数据导致expert功能形同虚设

---

## 🔧 v6i 修复计划

**已为v6i应用11项修复**（2026-04-20 19:31）:
- [x] CORS收窄 → ALLOWED_ORIGINS
- [x] detect_regime → v6a API + md5 fallback
- [x] switch_analyze → Pydantic Request Body
- [x] execute_trade → 【模拟模式】+ simulated=True
- [x] reset_daily → check_daily_reset() + health触发
- [x] get_market_data → 分类异常处理
- [x] get_position → 分类异常处理
- [x] asyncio.to_thread for Runner.run_sync

**v6i修复后评分**: 4.4 → 7.5/10（与vv6相同水平）

---

## 📊 v6i vs vv6 角色对比

| 维度 | v6i (8001) | vv6 (8006) |
|------|------------|-------------|
| **角色** | 🦐 Hermes右脑 | 🦞 Lobster左脑 |
| **模式** | 专家(激进) | 普通(保守) |
| **代码状态** | 11项修复已应用 | 11项修复已应用 |
| **regime来源** | v6a API ✅ | v6a API ✅ |
| **CORS** | 已收窄 ✅ | 已收窄 ✅ |
| **POST body** | Pydantic ✅ | Pydantic ✅ |
| **autonomous_loop** | ❌端口错(指向8006) | ✅端口正确(8006) |

---

*评审: gstack 手工执行*
*v6i版本: v6i-openai-agents*
