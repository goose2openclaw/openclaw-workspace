# BRAIN COORDINATOR - 左右脑 + Lobster/Hermes 综合架构

## 1. 系统架构图



## 2. API 汇总

### Brain Coordinator API (Port 8010)

| 端点 | 方法 | 描述 |
|------|------|------|
|  | GET | 协调器当前状态 |
|  | GET | 三脑实时信号 |
|  | POST | 触发一次决策分析 |
|  | POST | 手动切换引擎 |
|  | GET | 历史决策记录 |
|  | PUT | 更改协调模式 |
|  | GET | 健康检查 |

### 各引擎 API

| 引擎 | 端口 | 关键端点 |
|------|------|----------|
| Hermes (v6i) | 8001 |   |
| Lobster (vv6) | 8006 |   |
| QuadBrain (v15) | 8015 |   |
| Market (v6a) | 8000 |  |

## 3. 切换决策算法



## 4. 快速启动



## 5. 协调器 vs 独立引擎

| 场景 | 推荐 | 原因 |
|------|------|------|
| 日常运行 | Coordinator | 自动选择最优引擎 |
| 调试/测试 | 单独引擎 | 更细粒度控制 |
| 手动干预 | Coordinator SEMI | 提议+确认 |
| 高频交易 | v6i 专家模式 | 多空切换+高杠杆 |
| 保守定投 | vv6 普通模式 | 仅做多+低风险 |
| 四脑仲裁 | v15 QuadBrain | 多维度综合判断 |

## 6. 已知行为

- Hermes(v6i) 和 Lobster(vv6) 对同一请求可能返回不同的 confidence 值
- Quad(v15) direction 使用大写 (LONG/SHORT/HOLD)，其他使用小写
- 切换冷却时间: 5分钟 (min_switch_interval=300s)
- 置信度差异阈值: 10% (confidence_threshold=10.0)
- Coordinator 初始默认脑: hermes (v6i)