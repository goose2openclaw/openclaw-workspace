#!/usr/bin/env python3
"""
🐹 打地鼠策略 V2 - 高波动套利 + 多空双向
==========================================
火控雷达系统，专注高波动山寨币
持仓周期: 1小时 - 3天

做空机制 (V2新增):
- 🐻 RSI过热(>75) + 布林带触顶 → 跟踪做空
- 📉 波动率仓位: 高波动 + 做空 → 仓位降低一半
- ⚡ 快速止损: 做空止损3%，快于做多5%

适用市场:
- 币安现货 (做多)
- 币安U本位期货 (多空皆可)
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import math

# 波动率阈值
VOLATILITY_THRESHOLDS = {
    'min_volatility_24h': 0.08,       # 8% 最小波动
    'min_volume_ratio': 2.0,           # 成交量放大2倍
    'vol_spike_ratio': 5.0,            # 成交量爆发5倍
}

# RSI/布林带阈值
SIGNAL_THRESHOLDS = {
    'rsi_oversold': 25,                # RSI超卖线 (做多)
    'rsi_overbought': 75,              # RSI超买线 (做空)
    'bb_std': 2,                       # 布林带标准差倍数
    'bb_lower_threshold': -0.8,        # 布林带下限阈值 (做多)
    'bb_upper_threshold': 0.8,         # 布林带上限阈值 (做空)
}

# 风险参数
RISK_PARAMS = {
    # ── 做多参数 ──
    'stop_loss_long': 0.05,            # 做多止损 5%
    'take_profit_long': 0.15,          # 做多止盈 15%
    # ── 做空参数 (V2新增) ──
    'stop_loss_short': 0.03,           # 做空止损 3% (更紧)
    'take_profit_short': 0.12,         # 做空止盈 12%
    # ── 通用参数 ──
    'base_position': 0.05,             # 5% 基础仓位
    'max_position_long': 0.15,         # 做多最大仓位 15%
    'max_position_short': 0.08,        # 做空最大仓位 8% (更保守)
    'max_total_position': 0.20,        # 总仓位上限 20%
    'min_confidence_long': 0.60,        # 做多最低置信度
    'min_confidence_short': 0.65,      # 做空最低置信度 (略严)
    'max_holding_hours': 72,           # 3天 最大持仓
}


class MoleStrategy:
    """
    🐹 打地鼠策略 V2 - 多空双向高波动套利
    ========================================

    核心理念:
    - 做多: RSI超卖(≤25) + 布林带触底 → 抄底反弹
    - 做空: RSI过热(≥75) + 布林带触顶 → 高位做空
    - 波动率仓位: 波动越大，仓位越精
    - 做空更保守: 仓位上限8% < 做多15%

    与V1区别:
    | 功能     | V1        | V2              |
    |----------|-----------|------------------|
    | 做空     | ❌ 仅平仓  | ✅ RSI过热触发   |
    | 做空仓位 | N/A       | 8% (<做多15%)   |
    | 做空止损 | N/A       | 3% (<做多5%)    |
    | 做空止盈 | N/A       | 12%             |
    | 平仓信号 | 仅卖出     | 多空皆可        |
    """

    def __init__(self, config: Optional[Dict] = None):
        self.name = "🐹 打地鼠 V2"
        self.version = "v2.0"
        self.vol_thresholds = VOLATILITY_THRESHOLDS.copy()
        self.signal_thresholds = SIGNAL_THRESHOLDS.copy()
        self.params = RISK_PARAMS.copy()

        if config:
            self.params.update(config)
            self.vol_thresholds.update(config.get('volatility', {}))
            self.signal_thresholds.update(config.get('signal', {}))

        # 状态: direction 字段区分多空
        # symbol -> {
        #   entry_price, quantity, entry_time,
        #   direction: 'long' | 'short',
        #   entry_rsi, entry_bb
        # }
        self.positions: Dict[str, Dict] = {}
        self.signals: Dict[str, Dict] = {}
        self.candidates: List[Dict] = []

    # ═══════════════════════════════════════════════════════════════════
    # 指标计算
    # ═══════════════════════════════════════════════════════════════════

    def calculate_rsi(self, closes: List[float], period: int = 14) -> float:
        if len(closes) < period + 1:
            return 50.0
        deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
        gains = [d if d > 0 else 0 for d in deltas[-period:]]
        losses = [-d if d < 0 else 0 for d in deltas[-period:]]
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return 100.0 - (100.0 / (1.0 + rs))

    def calculate_sma(self, values: List[float], period: int) -> float:
        if len(values) < period:
            return sum(values) / len(values) if values else 0
        return sum(values[-period:]) / period

    def calculate_std(self, values: List[float], period: int) -> float:
        if len(values) < period:
            return 0
        sma = self.calculate_sma(values, period)
        variance = sum((v - sma) ** 2 for v in values[-period:]) / period
        return math.sqrt(variance)

    def calculate_bb_position(self, closes: List[float], period: int = 20,
                              std_mult: float = 2.0) -> float:
        if len(closes) < period:
            return 0
        sma = self.calculate_sma(closes, period)
        std = self.calculate_std(closes, period)
        upper = sma + std_mult * std
        lower = sma - std_mult * std
        current = closes[-1]
        if upper == lower:
            return 0
        position = (current - sma) / (std_mult * std) if std > 0 else 0
        return max(-1, min(1, position))

    def calculate_volume_ratio(self, volumes: List[float], period: int = 20) -> float:
        if len(volumes) < period:
            return 1.0
        avg_vol = sum(volumes[-period:]) / period
        return volumes[-1] / avg_vol if avg_vol > 0 else 1.0

    def calculate_volatility(self, high: float, low: float,
                            entry: float = None) -> float:
        if entry is None:
            entry = (high + low) / 2
        return abs(high - low) / entry if entry > 0 else 0

    # ═══════════════════════════════════════════════════════════════════
    # 市场数据分析
    # ═══════════════════════════════════════════════════════════════════

    def analyze_market(self, symbol: str, data: Dict) -> Dict:
        """
        分析市场数据，生成指标 + 多空方向

        做空信号 (V2新增):
        - RSI ≥ 75 (超买)
        - 布林带 bb_pos ≥ 0.8 (触顶)
        - 成交量确认
        """
        price = data.get('price', 0)
        high_24h = data.get('high_24h', price)
        low_24h = data.get('low_24h', price)
        volume = data.get('volume', 0)
        avg_volume = data.get('avg_volume', volume)
        closes = data.get('closes', [price])
        volumes = data.get('volumes', [volume])

        # 计算指标
        rsi = self.calculate_rsi(closes)
        bb_pos = self.calculate_bb_position(closes)
        vol_ratio = self.calculate_volume_ratio(volumes)
        volatility = self.calculate_volatility(high_24h, low_24h, price)

        # 判断信号
        signal = 'neutral'  # buy / sell / neutral
        direction = 'neutral'  # long / short / neutral
        confidence = 0.5
        reason = ''

        # ══ 做多信号 (RSI超卖 + 布林带触底) ══
        if rsi <= self.signal_thresholds['rsi_oversold'] and bb_pos < self.signal_thresholds['bb_lower_threshold']:
            signal = 'buy'
            direction = 'long'
            confidence = 0.90
            reason = f'RSI超卖({rsi:.1f})+布林触底({bb_pos:.2f})'

        elif rsi <= self.signal_thresholds['rsi_oversold']:
            signal = 'buy'
            direction = 'long'
            confidence = 0.70
            reason = f'RSI超卖({rsi:.1f})'

        elif vol_ratio >= self.vol_thresholds['vol_spike_ratio'] and bb_pos < -0.5:
            signal = 'buy'
            direction = 'long'
            confidence = 0.65
            reason = f'成交量爆发({vol_ratio:.1f}x)+布林低位({bb_pos:.2f})'

        elif bb_pos < -0.8:
            signal = 'buy'
            direction = 'long'
            confidence = 0.60
            reason = f'布林带触底({bb_pos:.2f})'

        # ══ 做空信号 (V2新增: RSI过热 + 布林带触顶) ══
        elif rsi >= self.signal_thresholds['rsi_overbought'] and bb_pos > self.signal_thresholds['bb_upper_threshold']:
            signal = 'sell'
            direction = 'short'
            confidence = 0.88
            reason = f'RSI过热({rsi:.1f})+布林触顶({bb_pos:.2f})'

        elif rsi >= self.signal_thresholds['rsi_overbought']:
            signal = 'sell'
            direction = 'short'
            confidence = 0.70
            reason = f'RSI过热({rsi:.1f})'

        elif bb_pos > 0.8:
            signal = 'sell'
            direction = 'short'
            confidence = 0.62
            reason = f'布林带触顶({bb_pos:.2f})'

        # 做空需要成交量确认 (V2新增)
        if direction == 'short' and vol_ratio < 1.5:
            confidence *= 0.75

        confidence = min(0.95, confidence)

        return {
            'symbol': symbol,
            'price': price,
            'rsi': rsi,
            'bb_position': bb_pos,
            'vol_ratio': vol_ratio,
            'volatility': volatility,
            'signal': signal,      # buy / sell / neutral
            'direction': direction,  # long / short / neutral (V2)
            'confidence': confidence,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }

    # ═══════════════════════════════════════════════════════════════════
    # 交易决策
    # ═══════════════════════════════════════════════════════════════════

    def should_enter_long(self, symbol: str, analysis: Dict) -> Tuple[bool, str]:
        """判断是否应该做多"""
        if analysis['signal'] != 'buy' or analysis['direction'] != 'long':
            return False, f"信号{analysis['signal']}非做多"

        if analysis['confidence'] < self.params['min_confidence_long']:
            return False, f"置信度{analysis['confidence']:.0%}<阈值{self.params['min_confidence_long']:.0%}"

        if analysis['volatility'] < self.vol_thresholds['min_volatility_24h']:
            return False, f"波动率{analysis['volatility']:.1%}<阈值{self.vol_thresholds['min_volatility_24h']:.1%}"

        if analysis['vol_ratio'] < self.vol_thresholds['min_volume_ratio']:
            return False, f"成交量比{analysis['vol_ratio']:.1f}x<阈值{self.vol_thresholds['min_volume_ratio']:.1f}x"

        total_pos = sum(p['quantity'] * p['entry_price'] for p in self.positions.values())
        if total_pos >= self.params['max_total_position']:
            return False, f"总仓位已满({self.params['max_total_position']:.0%})"

        return True, f"做多: {analysis['reason']}"

    def should_enter_short(self, symbol: str, analysis: Dict) -> Tuple[bool, str]:
        """
        判断是否应该做空 (V2新增)

        做空条件:
        1. signal = 'sell' 且 direction = 'short'
        2. RSI ≥ 75 (超买)
        3. 成交量 ≥ 1.5x 确认
        4. 置信度 ≥ 65%
        5. 波动率 ≥ 8%
        """
        if analysis['signal'] != 'sell' or analysis['direction'] != 'short':
            return False, f"信号{analysis['signal']}非做空"

        if analysis['confidence'] < self.params['min_confidence_short']:
            return False, f"置信度{analysis['confidence']:.0%}<做空阈值{self.params['min_confidence_short']:.0%}"

        if analysis['volatility'] < self.vol_thresholds['min_volatility_24h']:
            return False, f"波动率{analysis['volatility']:.1%}<阈值{self.vol_thresholds['min_volatility_24h']:.1%}"

        if analysis['vol_ratio'] < 1.5:
            return False, f"做空成交量不足 {analysis['vol_ratio']:.1f}x < 1.5x"

        total_pos = sum(p['quantity'] * p['entry_price'] for p in self.positions.values())
        if total_pos >= self.params['max_total_position']:
            return False, f"总仓位已满({self.params['max_total_position']:.0%})"

        return True, f"做空: {analysis['reason']}"

    def should_exit(self, symbol: str, current_price: float,
                   analysis: Dict = None) -> Tuple[bool, str]:
        """判断是否应该平仓 (多空统一)"""
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

        # 时间止损
        holding_hours = (datetime.now() - pos['entry_time']).total_seconds() / 3600
        if holding_hours >= self.params['max_holding_hours']:
            return True, f"时间止损: 持有{int(holding_hours)}小时"

        # 逆向信号平仓 (V2: 多头在超买时平, 空头在超卖时平)
        if analysis:
            if direction == 'long' and analysis['signal'] == 'sell':
                return True, f"反向信号: {analysis['reason']}"
            if direction == 'short' and analysis['signal'] == 'buy':
                return True, f"反向信号: {analysis['reason']}"

        return False, "继续持有"

    def calculate_position_size(self, volatility: float, rsi: float,
                               price: float, direction: str = 'long',
                               total_capital: float = 1.0) -> float:
        """
        计算仓位大小 (多空分别计算)

        做空更保守:
        - 做空仓位上限: 8%
        - 做多仓位上限: 15%
        - 波动率加成: 波动越大仓位越小 (反比例)
        """
        if direction == 'short':
            # 做空: 波动越大越危险，仓位减半
            position = min(
                self.params['base_position'] * 0.8,  # 基础8%
                self.params['max_position_short']
            )
            # 高波动减半
            if volatility > 0.15:
                position *= 0.5
            elif volatility > 0.10:
                position *= 0.75
        else:
            # 做多: 波动越大机会越多
            position = self.params['base_position']
            volatility_bonus = volatility * 0.5
            position += volatility_bonus
            # 极端RSI加成
            if rsi < 20 or rsi > 80:
                position += 0.03
            position = max(0.02, min(position, self.params['max_position_long']))

        return position * total_capital

    def generate_signal(self, symbol: str, market_data: Dict) -> Dict:
        """
        生成交易信号 (多空双向)

        返回 action:
        - 'long'  : 开多仓
        - 'short' : 开空仓 (V2新增)
        - 'sell'  : 平仓
        - 'hold'  : 无操作
        """
        analysis = self.analyze_market(symbol, market_data)
        self.signals[symbol] = analysis

        action = 'hold'
        reason = ''
        quantity = 0
        position_size = 0
        direction = None

        # ── 检查是否应该平仓 ──
        if symbol in self.positions:
            should_exit, exit_reason = self.should_exit(symbol, analysis['price'], analysis)
            if should_exit:
                action = 'sell'
                reason = exit_reason
                direction = self.positions[symbol].get('direction', 'long')
                quantity = self.positions[symbol]['quantity']

        # ── 检查是否应该做多 ──
        if action == 'hold' and analysis['direction'] == 'long':
            should_enter, enter_reason = self.should_enter_long(symbol, analysis)
            if should_enter:
                action = 'buy'
                reason = enter_reason
                direction = 'long'
                position_size = self.calculate_position_size(
                    analysis['volatility'],
                    analysis['rsi'],
                    analysis['price'],
                    direction='long'
                )
                quantity = position_size / analysis['price']

        # ── 检查是否应该做空 (V2新增) ──
        if action == 'hold' and analysis['direction'] == 'short':
            should_enter, enter_reason = self.should_enter_short(symbol, analysis)
            if should_enter:
                action = 'sell'   # 注意: 开空仓action='sell', 平多仓也用'sell'
                              # 通过 position.direction 区分
                reason = enter_reason
                direction = 'short'
                position_size = self.calculate_position_size(
                    analysis['volatility'],
                    analysis['rsi'],
                    analysis['price'],
                    direction='short'
                )
                quantity = position_size / analysis['price']

        return {
            'symbol': symbol,
            'action': action,
            'direction': direction,
            'quantity': quantity,
            'position_size': position_size,
            'confidence': analysis['confidence'],
            'reason': reason,
            'signal': analysis['signal'],
            'rsi': analysis['rsi'],
            'bb_position': analysis['bb_position'],
            'vol_ratio': analysis['vol_ratio'],
            'volatility': analysis['volatility'],
            'timestamp': datetime.now().isoformat()
        }

    # ═══════════════════════════════════════════════════════════════════
    # 持仓管理
    # ═══════════════════════════════════════════════════════════════════

    def update_position(self, symbol: str, action: str, quantity: float,
                       price: float, direction: str = 'long',
                       analysis: Dict = None):
        """更新持仓"""
        if action == 'buy' or (action == 'sell' and direction == 'long'):
            self.positions[symbol] = {
                'entry_price': price,
                'quantity': quantity,
                'entry_time': datetime.now(),
                'direction': direction,
                'entry_rsi': analysis['rsi'] if analysis else 50,
                'entry_bb': analysis['bb_position'] if analysis else 0
            }
        elif action == 'sell' and direction == 'short':
            # 开空仓
            self.positions[symbol] = {
                'entry_price': price,
                'quantity': quantity,
                'entry_time': datetime.now(),
                'direction': 'short',
                'entry_rsi': analysis['rsi'] if analysis else 50,
                'entry_bb': analysis['bb_position'] if analysis else 0
            }
        elif action == 'sell' and symbol in self.positions:
            # 平仓
            del self.positions[symbol]

    def get_status(self) -> Dict:
        """获取策略状态"""
        total_pnl = 0.0
        total_value = 0.0
        long_count = sum(1 for p in self.positions.values() if p.get('direction') == 'long')
        short_count = sum(1 for p in self.positions.values() if p.get('direction') == 'short')

        for symbol, pos in self.positions.items():
            direction = pos.get('direction', 'long')
            if direction == 'long':
                current_value = pos['quantity'] * pos['entry_price'] * 1.02
            else:
                current_value = pos['quantity'] * pos['entry_price'] * 0.98
            pnl = current_value - pos['entry_price'] * pos['quantity']
            total_pnl += pnl
            total_value += current_value

        return {
            'name': self.name,
            'version': self.version,
            'long_positions': long_count,
            'short_positions': short_count,
            'total_positions': len(self.positions),
            'signals': len(self.signals),
            'total_pnl': total_pnl,
            'total_value': total_value,
            'params': {
                'stop_loss_long': self.params['stop_loss_long'],
                'take_profit_long': self.params['take_profit_long'],
                'stop_loss_short': self.params['stop_loss_short'],
                'take_profit_short': self.params['take_profit_short'],
                'max_position_long': self.params['max_position_long'],
                'max_position_short': self.params['max_position_short'],
            },
            'thresholds': {
                'volatility': self.vol_thresholds,
                'signal': self.signal_thresholds
            }
        }

    def get_candidates_from_scan(self, scan_results: List[Dict]) -> List[Dict]:
        """从火控雷达扫描结果中筛选候选币种"""
        candidates = []
        for item in scan_results:
            if item.get('volatility', 0) >= self.vol_thresholds['min_volatility_24h']:
                if item.get('volume_ratio', 0) >= self.vol_thresholds['min_volume_ratio']:
                    candidates.append(item)
        return sorted(candidates, key=lambda x: x.get('volatility', 0), reverse=True)


# 单例实例
_mole_strategy: Optional[MoleStrategy] = None


def get_mole_strategy(config: Optional[Dict] = None) -> MoleStrategy:
    """获取地鼠策略实例"""
    global _mole_strategy
    if _mole_strategy is None:
        _mole_strategy = MoleStrategy(config)
    return _mole_strategy


if __name__ == '__main__':
    strategy = get_mole_strategy()

    print("=" * 50)
    print("🐹 打地鼠 V2 - 多空双向测试")
    print("=" * 50)

    # ── 测试做多信号 (RSI超卖) ──
    bull_data = {
        'price': 0.00000850,
        'high_24h': 0.00000950,
        'low_24h': 0.00000800,
        'volume': 5000000000,
        'avg_volume': 2000000000,
        'closes': [0.0000092, 0.0000090, 0.0000088, 0.0000086, 0.0000084,
                   0.0000083, 0.0000082, 0.0000080, 0.0000082, 0.0000084,
                   0.0000085, 0.0000086, 0.0000088, 0.0000090, 0.0000092,
                   0.0000085, 0.0000083],
        'volumes': [100, 120, 150, 200, 300, 500, 400, 350, 300, 250,
                    200, 180, 200, 250, 300, 500, 800]
    }
    sig = strategy.generate_signal('SHIB', bull_data)
    print(f"\n📈 做多信号: action={sig['action']} direction={sig['direction']}")
    print(f"   置信度={sig['confidence']:.0%} RSI={sig['rsi']:.1f} vol={sig['volatility']:.1%}")
    print(f"   原因: {sig['reason']}")

    # ── 测试做空信号 (V2新增: RSI过热) ──
    bear_data = {
        'price': 0.00001200,
        'high_24h': 0.00001300,
        'low_24h': 0.00001000,
        'volume': 3000000000,   # 成交量1.5x
        'avg_volume': 2000000000,
        'closes': [0.00001000, 0.00001050, 0.00001100, 0.00001150, 0.00001200,
                   0.00001220, 0.00001230, 0.00001240, 0.00001230, 0.00001220,
                   0.00001210, 0.00001200, 0.00001180, 0.00001160, 0.00001140,
                   0.00001200, 0.00001210],
        'volumes': [100, 120, 200, 350, 500, 600, 700, 800, 750, 700,
                    600, 500, 400, 350, 300, 400, 450]
    }
    sig = strategy.generate_signal('SHIB', bear_data)
    print(f"\n📉 做空信号: action={sig['action']} direction={sig['direction']}")
    print(f"   置信度={sig['confidence']:.0%} RSI={sig['rsi']:.1f} vol={sig['volatility']:.1%}")
    print(f"   原因: {sig['reason']}")

    print(f"\n📊 策略状态: {strategy.get_status()}")
