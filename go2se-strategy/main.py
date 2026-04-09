# region imports
from AlgorithmImports import *
# endregion

"""
🪿 GO2SE RSI趋势策略
基于RSI指标的均值回归交易策略
"""

class Go2seRSIStrategy(QCAlgorithm):

    def initialize(self):
        # 设置回测时间范围
        self.set_start_date(2024, 1, 1)
        self.set_end_date(2024, 12, 31)
        
        # 设置初始资金
        self.set_cash(100000)
        
        # 设置手续费模型
        self.set_fee_model(ConstantFeeModel(0.001))  # 0.1% 手续费
        
        # 添加加密货币 - 使用BTC和ETH
        self.symbols = [
            self.add_crypto("BTCUSD", Resolution.HOUR).symbol,
            self.add_crypto("ETHUSD", Resolution.HOUR).symbol,
        ]
        
        # RSI参数
        self.rsi_period = 14
        self.rsi_oversold = 30
        self.rsi_overbought = 70
        
        # 持仓追踪
        self.positions = {}
        
        # 初始化RSI指标
        for symbol in self.symbols:
            self.positions[str(symbol)] = {
                "rsi": self.rsi(symbol, self.rsi_period),
                "invested": False
            }
        
        self.log("🪿 GO2SE RSI策略初始化完成")

    def on_data(self, data: Slice):
        """每个新数据点都会调用此方法"""
        
        for symbol in self.symbols:
            symbol_str = str(symbol)
            pos = self.positions[symbol_str]
            
            # 检查RSI指标是否准备好
            if not pos["rsi"].is_ready:
                continue
            
            rsi_value = pos["rsi"].current.value
            current_price = data[symbol].close if data.contains_key(symbol) else None
            
            if current_price is None:
                continue
            
            # 买入信号: RSI超卖
            if rsi_value < self.rsi_oversold and not pos["invested"]:
                # 做多
                self.set_holdings(symbol, 0.3)  # 30%仓位
                pos["invested"] = True
                self.log(f"🟢 买入 {symbol_str} @ ${current_price:.2f} (RSI: {rsi_value:.1f})")
            
            # 卖出信号: RSI超买
            elif rsi_value > self.rsi_overbought and pos["invested"]:
                # 清仓
                self.liquidate(symbol)
                pos["invested"] = False
                self.log(f"🔴 卖出 {symbol_str} @ ${current_price:.2f} (RSI: {rsi_value:.1f})")
            
            # 止损: RSI进入中性区域且持仓亏损>5%
            elif pos["invested"]:
                holdings = self.portfolio[symbol]
                if holdings.quantity > 0:
                    pnl_pct = (current_price - holdings.average_price) / holdings.average_price * 100
                    if pnl_pct < -5:
                        self.liquidate(symbol)
                        pos["invested"] = False
                        self.log(f"🛡️ 止损 {symbol_str} @ ${current_price:.2f} (盈亏: {pnl_pct:.1f}%)")

    def on_end_of_algorithm(self):
        """策略结束时输出总结"""
        total_value = self.portfolio.total_value
        total_return = (total_value - 100000) / 100000 * 100
        
        self.log(f"=" * 40)
        self.log(f"🪿 策略结束总结")
        self.log(f"总资产: ${total_value:.2f}")
        self.log(f"总收益: {total_return:.2f}%")
        self.log(f"=" * 40)
