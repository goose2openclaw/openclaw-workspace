# CONTRIBUTING - GO2SE 贡献指南

欢迎贡献 GO2SE 北斗七鑫量化交易平台！

## 开发环境设置

### 前置要求
- Python 3.9+
- Node.js 18+
- npm 或 yarn

### 安装

```bash
# 克隆仓库
git clone https://github.com/goose2openclaw/openclaw-workspace.git
cd openclaw-workspace/GO2SE_PLATFORM

# 安装后端依赖
cd backend
pip install -r requirements.txt

# 安装前端依赖
cd ../versions/v6/frontend
npm install
```

### 运行

```bash
# 后端
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8004

# 前端 (开发模式)
cd versions/v6/frontend
npm run dev
```

## 代码规范

### Python
- 使用类型注解
- 遵循PEP 8
- 使用docstring文档化

```python
from typing import List, Optional

def calculate_rsi(prices: List[float], period: int = 14) -> Optional[float]:
    """
    计算RSI指标
    
    Args:
        prices: 价格列表
        period: 计算周期
        
    Returns:
        RSI值 (0-100) 或 None
    """
    pass
```

### TypeScript/React
- 使用TypeScript严格模式
- 组件使用函数式写法
- hooks放在 `src/hooks/` 目录

## 测试

### 后端测试
```bash
cd backend
python -m pytest tests/
```

### 前端测试
```bash
cd versions/v6/frontend
npm run test
```

## 提交规范

### Commit格式
```
<type>: <subject>

<body>
```

### Type
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建/工具

### 示例
```
feat: 添加MiroFish预言机路由

- 实现100智能体×5轮共识
- 添加6大预测市场
- 支持批量预测API
```

## 分支管理

- `main`: 主分支 (稳定版)
- `develop`: 开发分支
- `feature/*`: 功能分支
- `fix/*`: 修复分支

## 问题反馈

请通过 GitHub Issues 反馈问题，包含:
- 问题描述
- 复现步骤
- 环境信息
- 期望行为

## 许可证

本项目采用 MIT 许可证。
