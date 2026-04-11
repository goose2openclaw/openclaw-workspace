#!/usr/bin/env python3
"""
🐰 打兔子策略 V2 - 主流币趋势跟踪 + 多空双向
==============================================
趋势跟踪策略，专注前20主流加密货币
持仓周期: 1-7天

做空机制 (V2新增):
- 🐻 看跌信号: RSI过热(>70) + MA死叉 → 跟踪做空
- 📉 止盈/止损: 做空止盈=做空方向利润，做空止损=上行突破
- ⚡ 杠杆: 默认1x，可配置最高3x

适用市场:
- 币安现货 (做多)
- 币安U本位期货 (多空皆可)
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# 主流币列表 (前20)
MAINSTREAM_COINS = [
    'BTC', 'ETH', 'BNB', 'XRP', 'SOL', 'ADA', 'DOGE',
    'AVAX', 'DOT', 'MATIC', 'LINK', 'UNI', 'ATOM', 'LTC',
    'ETC', 'XLM', 'ALGO', 'VET', 'ICP', 'FIL'
]

# 趋势信号阈值
TREND_THRESHOLDS = {
    'rsi_overbought': 70,
    'rsi_oversold': 30,
    'volume_spike': 1.5,   # 成交量异常倍数
    # ── 做空阈值 (V2新增) ──
    'bear_rsi_min': 60,    # 做空最低RSI
    'bear_volume_min': 1.3,  # 做空最低成交量倍率
}

# 风险参数
RISK_PARAMS = {
    # ── 做多参数 ──
    'stop_loss_long': 0.05,    # 做多止损 5%
    'take_profit_long': 0.08,  # 做多止盈 8%
    # ── 做空参数 (V2新增) ──
    'stop_loss_short': 0.05,   # 做空止损 5% (价格反向上涨5%)
    'take_profit_short': 0.10, # 做空止盈 10% (下跌10%)
    # ── 通用参数 ──
    'max_position': 0.10,      # 单币最大仓位 10%
    'max_total_position': 0.25, # 总仓位上限 25%
    'min_confidence_long': 0.65, # 做多最低置信度
    'min_confidence_short': 0.68, # 做空最低置信度 (略严)
    'max_leverage': 1,          # 最大杠杆
}


class RabbitStrategy:
    """
    🐰 打兔子策略 V2 - 多空双向趋势跟踪
    ======================================

    核心理念:
    - 顺势而为：多头趋势做多，空头趋势做空
    - 做空触发：RSI过热(≥60) + MA死叉 + 成交量确认
    - 严格止损：多空各5%硬止损
    - 波动止盈：做空止盈10% > 做多止盈8%

    与V1区别:
    | 功能     | V1        | V2              |
    |----------|-----------|------------------|
    | 做空     | ❌ 不支持  | ✅ RSI过热触发   |
    | 方向跟踪 | 仅做多     | 多空双向         |
    | 做空止盈 | N/A       | 10% (>做多8%)   |
    | 做空止损 | N/A       | 5%               |
    """

    def __init__(self, config: Optional[Dict] = None):
        self.name = "🐰 打兔子 V2"
        self.version = "v2.0"
        self.coins = MAINSTREAM_COINS
        self.params = RISK_PARAMS.copy()
        if config:
            self.params.update(config)

        # 状态: direction 字段区分多空
        # symbol -> {
        #   entry_price, quantity, entry_time,
        #   direction: 'long' | 'short'
        # }
        self.positions: Dict[str, Dict] = {}
        self.signals: Dict[str, Dict] = {}

    def analyze_trend(self, symbol: str, data: Dict) -> Dict:
        """
        分析币种趋势，返回多空方向 + 置信度

        做空信号识别 (V2):
        1. RSI ≥ 60 (过热但未极端)
        2. MA7 < MA25 (死叉确认)
        3. 价格 < MA7 (在均线下方)
        4. 成交量放大 ≥ 1.3x (确认)
        """
        price = data.get('price', 0)
        rsi = data.get('rsi', 50)
        ma_7 = data.get('ma7', price)
        ma_25 = data.get('ma25', price)
        volume = data.get('volume', 0)
        avg_volume = data.get('avg_volume', volume or 1)

        # ── 方向判断 ──
        direction = 'neutral'  # long / short / neutral
        confidence = 0.5

        # 多头: MA7 > MA25 且价格在MA7上方
        if ma_7 > ma_25 and price > ma_7:
            direction = 'long'
            confidence = 0.70
        # 空头 (V2新增): MA7 < MA25 且价格在MA7下方 且 RSI过热
        elif ma_7 < ma_25 and price < ma_7 and rsi >= TREND_THRESHOLDS['bear_rsi_min']:
            direction = 'short'
            confidence = 0.70
        else:
            direction = 'neutral'
            confidence = 0.50

        # ── 置信度调整 ──
        # 多头过热降权
        if rsi > TREND_THRESHOLDS['rsi_overbought'] and direction == 'long':
            confidence *= 0.75
        # 空头超卖降权 (可能反弹)
        if rsi < TREND_THRESHOLDS['rsi_oversold'] and direction == 'short':
            confidence *= 0.80

        # 成交量放大确认
        vol_ratio = volume / avg_volume if avg_volume > 0 else 1.0
        if vol_ratio >= TREND_THRESHOLDS['volume_spike']:
            confidence = min(0.95, confidence * 1.2)
        # 做空需要成交量确认 (V2新增)
        if direction == 'short' and vol_ratio < TREND_THRESHOLDS['bear_volume_min']:
            confidence *= 0.70

        confidence = min(0.95, confidence)

        return {
            'symbol': symbol,
            'direction': direction,
            'confidence': confidence,
            'price': price,
            'rsi': rsi,
            'ma7': ma_7,
            'ma25': ma_25,
            'vol_ratio': vol_ratio,
            'trend': 'up' if direction == 'long' else 'down' if direction == 'short' else 'sideways'
        }

    def should_enter_long(self, symbol: str, analysis: Dict) -> Tuple[bool, str]:
        """判断是否应该做多"""
        if analysis['direction'] != 'long':
            return False, f"方向{analysis['direction']}非做多"

        if analysis['confidence'] < self.params['min_confidence_long']:
            return False, f"置信度{analysis['confidence']:.0%}<阈值{self.params['min_confidence_long']:.0%}"

        # 总仓位检查 (多头 + 空头合计)
        total_pos = sum(
            p['quantity'] * p['entry_price']
            for p in self.positions.values()
        )
        if total_pos >= self.params['max_total_position']:
            return False, f"总仓位已满{self.params['max_total_position']:.0%}"

        return True, f"做多信号, RSI={analysis['rsi']:.1f}, vol={analysis['vol_ratio']:.1f}x"

    def should_enter_short(self, symbol: str, analysis: Dict) -> Tuple[bool, str]:
        """
        判断是否应该做空 (V2新增)

        做空条件:
        1. 方向 = short
        2. RSI ≥ 60 (过热)
        3. 成交量 ≥ 1.3x 确认
        4. 置信度 ≥ 68%
        """
        if analysis['direction'] != 'short':
            return False, f"方向{analysis['direction']}非做空"

        if analysis['confidence'] < self.params['min_confidence_short']:
            return False, f"置信度{analysis['confidence']:.0%}<做空阈值{self.params['min_confidence_short']:.0%}"

        if analysis['vol_ratio'] < TREND_THRESHOLDS['bear_volume_min']:
            return False, f"做空成交量不足 {analysis['vol_ratio']:.1f}x < {TREND_THRESHOLDS['bear_volume_min']}x"

        # 总仓位检查
        total_pos = sum(
            p['quantity'] * p['entry_price']
            for p in self.positions.values()
        )
        if total_pos >= self.params['max_total_position']:
            return False, f"总仓位已满{self.params['max_total_position']:.0%}"

        return True, f"做空信号, RSI={analysis['rsi']:.1f}, vol={analysis['vol_ratio']:.1f}x"

    def should_exit(self, symbol: str, current_price: float) -> Tuple[bool, str]:
        """
        判断是否应该平仓 (多空统一)

        多头: pnl = (current - entry) / entry
        空头: pnl = (entry - current) / entry
        """
        if symbol not in self.positions:
            return False, "无持仓"

        pos = self.positions[symbol]
        entry_price = pos['entry_price']
        direction = pos.get('direction', 'long')

        # 多头PnL
        if direction == 'long':
            pnl_pct = (current_price - entry_price) / entry_price
            stop_loss = -self.params['stop_loss_long']
            take_profit = self.params['take_profit_long']
        else:  # short
            pnl_pct = (entry_price - current_price) / entry_price
            stop_loss = -self.params['stop_loss_short']
            take_profit = self.params['take_profit_short']

        # 止损检查
        if pnl_pct <= stop_loss:
            return True, f"止损({direction}): {pnl_pct:.2%}"

        # 止盈检查
        if pnl_pct >= take_profit:
            return True, f"止盈({direction}): {pnl_pct:.2%}"

        # 时间止损 (持有超过7天)
        holding_days = (datetime.now() - pos['entry_time']).days
        if holding_days > 7:
            return True, f"时间止损: 持有{holding_days}天"

        return False, "继续持有"

    def generate_signal(self, symbol: str, market_data: Dict) -> Dict:
        """
        生成交易信号 (多空双向)

        返回 action:
        - 'long'  : 开多仓
        - 'short' : 开空仓 (V2新增)
        - 'sell'  : 平仓 (任意方向)
        - 'hold'  : 无操作
        """
        analysis = self.analyze_trend(symbol, market_data)
        self.signals[symbol] = analysis

        action = 'hold'
        reason = ''
        quantity = 0
        direction = None

        # ── 检查是否应该平仓 ──
        if symbol in self.positions:
            should_exit, exit_reason = self.should_exit(symbol, analysis['price'])
            if should_exit:
                action = 'sell'
                reason = exit_reason
                direction = self.positions[symbol].get('direction', 'long')

        # ── 检查是否应该做多 ──
        if action == 'hold' and analysis['direction'] == 'long':
            should_enter, enter_reason = self.should_enter_long(symbol, analysis)
            if should_enter:
                action = 'long'
                reason = enter_reason
                direction = 'long'
                # 仓位计算
                max_value = self.params['max_position']
                quantity = max_value / analysis['price']

        # ── 检查是否应该做空 (V2新增) ──
        if action == 'hold' and analysis['direction'] == 'short':
            should_enter, enter_reason = self.should_enter_short(symbol, analysis)
            if should_enter:
                action = 'short'
                reason = enter_reason
                direction = 'short'
                max_value = self.params['max_position']
                quantity = max_value / analysis['price']

        return {
            'symbol': symbol,
            'action': action,
            'direction': direction,
            'quantity': quantity,
            'confidence': analysis['confidence'],
            'reason': reason,
            'rsi': analysis['rsi'],
            'vol_ratio': analysis['vol_ratio'],
            'trend': analysis['trend'],
            'timestamp': datetime.now().isoformat()
        }

    def update_position(self, symbol: str, action: str, quantity: float,
                       price: float, direction: str = 'long'):
        """更新持仓"""
        if action == 'long':
            self.positions[symbol] = {
                'entry_price': price,
                'quantity': quantity,
                'entry_time': datetime.now(),
                'direction': 'long'
            }
        elif action == 'short':
            self.positions[symbol] = {
                'entry_price': price,
                'quantity': quantity,
                'entry_time': datetime.now(),
                'direction': 'short'
            }
        elif action == 'sell' and symbol in self.positions:
            del self.positions[symbol]

    def get_status(self) -> Dict:
        """获取策略状态"""
        total_pnl = 0.0
        long_count = sum(1 for p in self.positions.values() if p.get('direction') == 'long')
        short_count = sum(1 for p in self.positions.values() if p.get('direction') == 'short')

        for symbol, pos in self.positions.items():
            direction = pos.get('direction', 'long')
            if direction == 'long':
                pnl = (1.02 - 1.0) * pos['entry_price'] * pos['quantity']
            else:
                pnl = (1.0 - 0.98) * pos['entry_price'] * pos['quantity']
            total_pnl += pnl

        return {
            'name': self.name,
            'version': self.version,
            'long_positions': long_count,
            'short_positions': short_count,
            'total_positions': len(self.positions),
            'signals': len(self.signals),
            'total_pnl': total_pnl,
            'params': {
                'stop_loss_long': self.params['stop_loss_long'],
                'take_profit_long': self.params['take_profit_long'],
                'stop_loss_short': self.params['stop_loss_short'],
                'take_profit_short': self.params['take_profit_short'],
                'max_position': self.params['max_position'],
                'max_total_position': self.params['max_total_position'],
            }
        }


# 单例实例
_rabbit_strategy: Optional[RabbitStrategy] = None


def get_rabbit_strategy(config: Optional[Dict] = None) -> RabbitStrategy:
    """获取兔子策略实例"""
    global _rabbit_strategy
    if _rabbit_strategy is None:
        _rabbit_strategy = RabbitStrategy(config)
    return _rabbit_strategy


if __name__ == '__main__':
    strategy = get_rabbit_strategy()

    # ── 测试做多信号 ──
    print("=" * 50)
    print("🐰 打兔子 V2 - 多空双向测试")
    print("=" * 50)

    # 看涨数据
    bull_data = {
        'price': 50500,
        'rsi': 55,
        'ma7': 50000,
        'ma25': 49500,
        'volume': 1200000,
        'avg_volume': 800000
    }
    sig = strategy.generate_signal('BTC', bull_data)
    print(f"\n📈 看涨信号: {sig['action']} | {sig['direction']} | 置信度={sig['confidence']:.0%}")
    print(f"   原因: {sig['reason']}")

    # 看跌数据 (V2新测试)
    bear_data = {
        'price': 48000,
        'rsi': 68,       # 过热
        'ma7': 48500,
        'ma25': 49000,   # 死叉
        'volume': 1300000,
        'avg_volume': 800000
    }
    sig = strategy.generate_signal('BTC', bear_data)
    print(f"\n📉 看跌信号: {sig['action']} | {sig['direction']} | 置信度={sig['confidence']:.0%}")
    print(f"   原因: {sig['reason']}")

    # 中性数据
    neutral_data = {
        'price': 50000,
        'rsi': 50,
        'ma7': 50000,
        'ma25': 49900,
        'volume': 900000,
        'avg_volume': 800000
    }
    sig = strategy.generate_signal('BTC', neutral_data)
    print(f"\n➡️  中性信号: {sig['action']} | 置信度={sig['confidence']:.0%}")

    print(f"\n📊 策略状态: {strategy.get_status()}")
