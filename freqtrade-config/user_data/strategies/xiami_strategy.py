"""
XIAMI Strategy for FreqTrade
eXtensible AI-Driven Multi-source Intelligent trading
"""

from freqtrade.strategy import IStrategy
from pandas import DataFrame
import pandas as pd
import numpy as np

class XiamiStrategy(IStrategy):
    """
    XIAMI - Multi-strategy trading system
    
    Buy conditions (满足2/3):
    - RSI(4h) < 40 (oversold)
    - MACD bullish crossover
    - Price above SMA20
    
    Sell conditions:
    - RSI > 70 (overbought)
    - Price below SMA20
    - Take profit 15% or stop loss 5%
    """
    
    # 策略参数
    minimal_roi = {
        "0": 0.15,  # 15% take profit
        "60": 0.10,  # 10% after 1 hour
        "120": 0.05, # 5% after 2 hours
    }
    
    # 止损
    stoploss = -0.05
    
    #  timeframe
    timeframe = '5m'
    
    # 启动时需要的K线数
    startup_candle_count = 200
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """计算技术指标"""
        
        # RSI
        delta = dataframe['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        dataframe['rsi'] = 100 - (100 / (1 + rs))
        
        # SMA using pandas
        dataframe['sma20'] = dataframe['close'].rolling(window=20).mean()
        dataframe['sma50'] = dataframe['close'].rolling(window=50).mean()
        
        # EMA for MACD
        ema12 = dataframe['close'].ewm(span=12, adjust=False).mean()
        ema26 = dataframe['close'].ewm(span=26, adjust=False).mean()
        dataframe['macd'] = ema12 - ema26
        dataframe['macdsignal'] = dataframe['macd'].ewm(span=9, adjust=False).mean()
        dataframe['macdhist'] = dataframe['macd'] - dataframe['macdsignal']
        
        # 波动率
        dataframe['volatility'] = dataframe['close'].pct_change().rolling(20).std() * 100
        
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """入场信号"""
        
        # 条件1: RSI < 40 (超卖)
        rsi_oversold = dataframe['rsi'] < 40
        
        # 条件2: MACD 金叉
        macd_bullish = (dataframe['macd'] > dataframe['macdsignal']) & (dataframe['macd'].shift(1) <= dataframe['macdsignal'].shift(1))
        
        # 条件3: 价格站上 SMA20
        price_above_sma20 = dataframe['close'] > dataframe['sma20']
        
        # 满足2/3条件
        conditions = rsi_oversold.astype(int) + macd_bullish.astype(int) + price_above_sma20.astype(int)
        dataframe['enter_long'] = conditions >= 2
        
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """出场信号"""
        
        # 条件1: RSI > 70 (超买)
        rsi_overbought = dataframe['rsi'] > 70
        
        # 条件2: 价格跌破 SMA20
        price_below_sma20 = dataframe['close'] < dataframe['sma20']
        
        # 条件3: MACD 死叉
        macd_bearish = (dataframe['macd'] < dataframe['macdsignal']) & (dataframe['macd'].shift(1) >= dataframe['macdsignal'].shift(1))
        
        # 满足任一条件出场
        conditions = rsi_overbought | price_below_sma20 | macd_bearish
        dataframe['exit_long'] = conditions
        
        return dataframe
