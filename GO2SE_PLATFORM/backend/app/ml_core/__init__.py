"""
GO2SE ML Core - 机器学习能力中心
===================================
量化交易、策略优化、预测、空投猎手、算力调度、胜率预测、众包信号

模块架构:
├── quant_engine.py          # 量化引擎
├── strategy_optimizer.py    # 策略优化器
├── predictor.py              # 预测引擎
├── airdrop_hunter.py      # 空投猎手
├── compute_scheduler.py    # 算力调度器
├── win_rate.py            # 胜率预测
├── crowdsignal.py         # 众包信号聚合
├── factor_degradation.py   # 因子退化检测
└── ml_hub.py             # ML能力中心 (统一入口)
"""
from .ml_hub import MLHub

__all__ = ["MLHub"]
