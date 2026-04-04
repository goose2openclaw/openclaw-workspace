# 🪿 GO2SE API 路由索引
# ========================
# 
# 本文件汇总所有路由模块
#
# 路由文件结构:
# ├── routes.py              # 主路由 (核心API)
# ├── routes_v7.py           # V7扩展
# ├── routes_expert.py       # 专家模式
# ├── routes_expert_mode.py  # 专家模式扩展
# ├── routes_market.py        # 市场数据
# ├── routes_sonar.py        # 声纳库
# ├── routes_backtest.py      # 回测系统
# ├── routes_paper_trading.py # 模拟交易
# ├── routes_mirofish_decision.py # MiroFish决策
# ├── routes_factor_degradation.py # 因子退化
# ├── routes_ai_portfolio.py  # AI组合管理
# ├── strategies_extra.py     # 额外策略
# └── oracle/
#     └── mirofish.py         # MiroFish预言机

from .routes import router as main_router
from .routes_v7 import router as v7_router
from .routes_expert import router as expert_router
from .routes_expert_mode import router as expert_mode_router
from .routes_market import router as market_router
from .routes_sonar import router as sonar_router
from .routes_backtest import router as backtest_router
from .routes_paper_trading import router as paper_trading_router
from .routes_mirofish_decision import router as mirofish_decision_router
from .routes_factor_degradation import router as factor_degradation_router
from .routes_ai_portfolio import router as ai_portfolio_router
from .strategies_extra import router as strategies_extra_router
from .oracle.mirofish import router as mirofish_router

__all__ = [
    "main_router",
    "v7_router",
    "expert_router",
    "expert_mode_router",
    "market_router",
    "sonar_router",
    "backtest_router",
    "paper_trading_router",
    "mirofish_decision_router",
    "factor_degradation_router",
    "ai_portfolio_router",
    "strategies_extra_router",
    "mirofish_router",
]
