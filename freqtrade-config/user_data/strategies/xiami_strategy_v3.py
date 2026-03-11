#!/usr/bin/env python3
"""
🦐 XIAMI Strategy v3 - 高胜率优化版
- 趋势过滤
- 多重确认
- 严格止损
"""

from freqtrade.strategy import IStrategy
from pandas import DataFrame
import pandas as pd
import numpy as np

class XiamiStrategyV3(IStrategy):
    """
    XIAMI v3 - 高胜率优化策略
    
    核心:
    - 只做上涨趋势
    - 多指标确认
    - 严格止损
    """
    
    timeframe = '1h'  # 更长周期，更稳
    
    # 止盈止损
    minimal_roi = {
        "0": 0.05,  # 5% 止盈
        "240": 0.03,  # 4小时后3%
    }
    
    stoploss = -0.02  # 2% 严格止损
    
    startup_candle_count = 200
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """技术指标"""
        
        # RSI
        delta = dataframe['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        dataframe['rsi'] = 100 - (100 / (1 + rs))
        
        # EMA
        dataframe['ema9'] = dataframe['close'].ewm(span=9, adjust=False).mean()
        dataframe['ema21'] = dataframe['close'].ewm(span=21, adjust=False).mean()
        
        # SMA
        dataframe['sma50'] = dataframe['close'].rolling(window=50).mean()
        dataframe['sma200'] = dataframe['close'].rolling(window=200).mean()
        
        # MACD
        ema12 = dataframe['close'].ewm(span=12, adjust=False).mean()
        ema26 = dataframe['close'].ewm(span=26, adjust=False).mean()
        dataframe['macd'] = ema12 - ema26
        dataframe['macdsignal'] = dataframe['macd'].ewm(span=9, adjust=False).mean()
        
        # ATR 止损
        high_low = dataframe['high'] - dataframe['low']
        high_close = np.abs(dataframe['high'] - dataframe['close'].shift())
        low_close = np.abs(dataframe['low'] - dataframe['close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        dataframe['atr'] = tr.rolling(14).mean()
        
        # 成交量
        dataframe['volume_ma'] = dataframe['volume'].rolling(20).mean()
        
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """高胜率入场"""
        
        # 1. 趋势确认 (必须)
        uptrend = dataframe['ema21'] > dataframe['ema50']
        strong_uptrend = dataframe['close'] > dataframe['sma200']
        
        # 2. 回调入场 (RSI超卖)
        rsi_oversold = dataframe['rsi'] < 35
        
        # 3. MACD 金叉
        macd_cross = (dataframe['macd'] > dataframe['macdsignal']) & (dataframe['macd'].shift(1) <= dataframe['macdsignal'].shift(1))
        
        # 4. 成交量确认
        volume_confirm = dataframe['volume'] > dataframe['volume_ma'] * 1.2
        
        # 5. 均线支撑
        near_ema = np.abs(dataframe['close'] - dataframe['ema21']) / dataframe['ema21'] < 0.02
        
        # 满足条件:
        # 趋势 + (RSI超卖 + MACD金叉 + 成交量)
        conditions = (
            uptrend.astype(int) + 
            strong_uptrend.astype(int) +
            rsi_oversold.astype(int) +
            macd_cross.astype(int) +
            volume_confirm.astype(int)
        )
        
        # 只在趋势向上时入场
        dataframe['enter_long'] = (uptrend) & (conditions >= 3)
        
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """严格出场"""
        
        # 1. RSI 超买
        rsi_overbought = dataframe['rsi'] > 75
        
        # 2. 趋势反转
        trend_reversal = dataframe['ema21'] < dataframe['ema50']
        
        # 3. MACD 死叉
        macd_death = (dataframe['macd'] < dataframe['macdsignal']) & (dataframe['macd'].shift(1) >= dataframe['macdsignal'].shift(1))
        
        # 4. ATR 止损
        atr_stop = dataframe['close'] < (dataframe['close'] - dataframe['atr'] * 1.5)
        
        # 5. 跌破200日均线
        below_sma200 = dataframe['close'] < dataframe['sma200']
        
        # 任一条件出场
        dataframe['exit_long'] = rsi_overbought | trend_reversal | macd_death | atr_stop | below_sma200
        
        return dataframe
