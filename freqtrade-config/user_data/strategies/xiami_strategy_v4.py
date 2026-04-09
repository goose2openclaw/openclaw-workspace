#!/usr/bin/env python3
"""
🦐 XIAMI Strategy v4 - 精选高胜率策略
- 只做高确定性信号
- 趋势确认 + 突破
- 严格风控
"""

from freqtrade.strategy import IStrategy
from pandas import DataFrame
import pandas as pd
import numpy as np

class XiamiStrategyV4(IStrategy):
    """
    XIAMI v4 - 精选高胜率策略
    
    只做趋势确认 + 突破的高确定性信号
    """
    
    timeframe = '4h'  # 4小时周期
    
    # 止盈止损
    minimal_roi = {
        "0": 0.08,  # 8% 止盈
        "72": 0.04,  # 4% 保本
    }
    
    stoploss = -0.03  # 3% 止损
    
    startup_candle_count = 200
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """技术指标"""
        
        # RSI
        delta = dataframe['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        dataframe['rsi'] = 100 - (100 / (1 + rs))
        
        # SMA
        dataframe['sma20'] = dataframe['close'].rolling(window=20).mean()
        dataframe['sma50'] = dataframe['close'].rolling(window=50).mean()
        dataframe['sma200'] = dataframe['close'].rolling(window=200).mean()
        
        # 20日最高价 (突破用)
        dataframe['highest_20'] = dataframe['high'].rolling(20).max()
        
        # ATR
        high_low = dataframe['high'] - dataframe['low']
        high_close = np.abs(dataframe['high'] - dataframe['close'].shift())
        low_close = np.abs(dataframe['low'] - dataframe['close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        dataframe['atr'] = tr.rolling(14).mean()
        
        # 成交量
        dataframe['volume_ma'] = dataframe['volume'].rolling(20).mean()
        
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """高确定性入场"""
        
        # 1. 长期趋势向上 (200日均线)
        long_trend = dataframe['close'] > dataframe['sma200']
        
        # 2. 中期趋势向上 (50日均线)
        mid_trend = dataframe['sma20'] > dataframe['sma50']
        
        # 3. 突破20日高点
        breakout = dataframe['close'] > dataframe['highest_20'].shift(1)
        
        # 4. 成交量确认
        volume_confirm = dataframe['volume'] > dataframe['volume_ma'] * 1.3
        
        # 5. RSI 在合理区间 (40-70)
        rsi_good = (dataframe['rsi'] > 40) & (dataframe['rsi'] < 70)
        
        # 入场: 趋势确认 + 突破 + 成交量
        dataframe['enter_long'] = (
            long_trend & 
            mid_trend & 
            breakout & 
            volume_confirm &
            rsi_good
        )
        
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """严格出场"""
        
        # 1. 跌破50日均线
        below_ma50 = dataframe['close'] < dataframe['sma50']
        
        # 2. RSI 超买
        rsi_overbought = dataframe['rsi'] > 75
        
        # 3. ATR 止损
        atr_stop = dataframe['close'] < (dataframe['close'] - dataframe['atr'] * 2)
        
        # 4. 止盈
        # (由 minimal_roi 处理)
        
        dataframe['exit_long'] = below_ma50 | rsi_overbought | atr_stop
        
        return dataframe
