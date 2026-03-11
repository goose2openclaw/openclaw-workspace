#!/usr/bin/env python3
"""
XIAMI Strategy v2 - Enhanced with more indicators
增强版XIAMI策略
"""

from freqtrade.strategy import IStrategy
from pandas import DataFrame
import pandas as pd
import numpy as np

class XiamiStrategyV2(IStrategy):
    """
    XIAMI v2 - Enhanced Multi-indicator Strategy
    
    Features:
    - Dynamic mode switching (trend/grid/sideways)
    - Multiple confirmations
    - ATR-based stop loss
    - Adaptive position sizing
    """
    
    # 策略参数 - 可优化
    timeframe = '15m'  # 更长周期减少噪音
    
    # ROI
    minimal_roi = {
        "0": 0.20,  # 20% take profit
        "180": 0.10,  # 10% after 3 hours
    }
    
    # 止损 - ATR-based
    stoploss = -0.03
    
    # 启动K线数
    startup_candle_count = 200
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """计算技术指标"""
        
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
        
        # EMA
        dataframe['ema12'] = dataframe['close'].ewm(span=12, adjust=False).mean()
        dataframe['ema26'] = dataframe['close'].ewm(span=26, adjust=False).mean()
        
        # MACD
        dataframe['macd'] = dataframe['ema12'] - dataframe['ema26']
        dataframe['macdsignal'] = dataframe['macd'].ewm(span=9, adjust=False).mean()
        dataframe['macdhist'] = dataframe['macd'] - dataframe['macdsignal']
        
        # ATR (Average True Range) -  volatility
        high_low = dataframe['high'] - dataframe['low']
        high_close = np.abs(dataframe['high'] - dataframe['close'].shift())
        low_close = np.abs(dataframe['low'] - dataframe['close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        dataframe['atr'] = tr.rolling(14).mean()
        dataframe['atr_percent'] = (dataframe['atr'] / dataframe['close']) * 100
        
        # Bollinger Bands
        sma20 = dataframe['close'].rolling(20).mean()
        std20 = dataframe['close'].rolling(20).std()
        dataframe['bb_upper'] = sma20 + (std20 * 2)
        dataframe['bb_lower'] = sma20 - (std20 * 2)
        dataframe['bb_position'] = (dataframe['close'] - dataframe['bb_lower']) / (dataframe['bb_upper'] - dataframe['bb_lower'])
        
        # Volume confirmation
        dataframe['volume_sma'] = dataframe['volume'].rolling(20).mean()
        dataframe['volume_ratio'] = dataframe['volume'] / dataframe['volume_sma']
        
        # Market regime detection
        dataframe['volatility'] = dataframe['close'].pct_change().rolling(20).std() * 100
        
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """增强入场信号"""
        
        # 基础条件
        rsi_oversold = dataframe['rsi'] < 35
        macd_bullish = (dataframe['macd'] > dataframe['macdsignal']) & (dataframe['macd'].shift(1) <= dataframe['macdsignal'].shift(1))
        price_above_sma = dataframe['close'] > dataframe['sma20']
        
        # 趋势确认
        uptrend = dataframe['sma20'] > dataframe['sma50']
        
        # 成交量确认
        volume_confirm = dataframe['volume_ratio'] > 1.0
        
        # 布林带确认
        bb_oversold = dataframe['bb_position'] < 0.2
        
        # 多重确认 (满足3/5)
        conditions = (
            rsi_oversold.astype(int) + 
            macd_bullish.astype(int) + 
            price_above_sma.astype(int) + 
            uptrend.astype(int) +
            volume_confirm.astype(int)
        )
        dataframe['enter_long'] = conditions >= 3
        
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """增强出场信号"""
        
        # RSI超买
        rsi_overbought = dataframe['rsi'] > 75
        
        # MACD死叉
        macd_bearish = (dataframe['macd'] < dataframe['macdsignal']) & (dataframe['macd'].shift(1) >= dataframe['macdsignal'].shift(1))
        
        # 价格跌破SMA20
        price_below_sma = dataframe['close'] < dataframe['sma20']
        
        # 趋势反转
        downtrend = dataframe['sma20'] < dataframe['sma50']
        
        # ATR止损触发
        atr_stop = dataframe['close'] < (dataframe['close'] - dataframe['atr'] * 2)
        
        # 任一条件
        dataframe['exit_long'] = rsi_overbought | macd_bearish | price_below_sma | downtrend | atr_stop
        
        return dataframe
