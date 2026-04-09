#!/usr/bin/env python3
"""
北斗七鑫 - 专家版 v3
深度推理 + 专家反馈 + 自适应优化
"""

import json
import time
import requests
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque

# ==================== 专家分析引擎 ====================

class ExpertAnalysisEngine:
    """专家分析引擎"""
    
    def __init__(self):
        self.market_regimes = {
            'bull_strong': {'name': '强势牛市', '特征': '上涨趋势', '建议': '积极追涨'},
            'bull_weak': {'name': '弱势牛市', '特征': '震荡上涨', '建议': '回调买入'},
            'bear_strong': {'name': '强势熊市', '特征': '下跌趋势', '建议': '空仓观望'},
            'bear_weak': {'name': '弱势熊市', '特征': '震荡下跌', '建议': '轻仓试空'},
            'sideways': {'name': '震荡市', '特征': '区间波动', '建议': '高抛低吸'}
        }
        
        self.current_regime = 'sideways'
        self.regime_history = deque(maxlen=30)
    
    def detect_market_regime(self, market_data: Dict) -> str:
        """检测市场状态"""
        # 简化版 - 实际需要更多指标
        btc_change = market_data.get('btc_change', 0)
        eth_change = market_data.get('eth_change', 0)
        avg_change = market_data.get('avg_change', 0)
        volatility = market_data.get('volatility', 0.02)
        
        if btc_change > 5 and volatility < 0.05:
            regime = 'bull_strong'
        elif btc_change > 0 and volatility < 0.03:
            regime = 'bull_weak'
        elif btc_change < -5 and volatility < 0.05:
            regime = 'bear_strong'
        elif btc_change < 0 and volatility < 0.03:
            regime = 'bear_weak'
        else:
            regime = 'sideways'
        
        self.current_regime = regime
        self.regime_history.append({
            'regime': regime,
            'timestamp': int(time.time())
        })
        
        return regime
    
    def get_expert_recommendation(self, tool: str, signals: List[Dict], market_data: Dict) -> Dict:
        """专家建议"""
        regime = self.detect_market_regime(market_data)
        regime_info = self.market_regimes.get(regime, {})
        
        # 基于市场状态调整建议
        recommendations = []
        
        for signal in signals:
            tool_name = signal.get('tool', '')
            confidence = signal.get('confidence', 0)
            action = signal.get('action', 'HOLD')
            
            # 根据工具和市场状态调整
            adjusted = self._adjust_for_regime(tool_name, action, confidence, regime)
            recommendations.append(adjusted)
        
        return {
            'market_regime': regime,
            'regime_name': regime_info.get('name', ''),
            'market_advice': regime_info.get('建议', ''),
            'recommendations': recommendations,
            'expert_analysis': self._generate_analysis(market_data, regime)
        }
    
    def _adjust_for_regime(self, tool: str, action: str, confidence: float, regime: str) -> Dict:
        """根据市场状态调整"""
        # 调整置信度
        regime_multipliers = {
            'bull_strong': 1.2,
            'bull_weak': 1.0,
            'bear_strong': 0.7,
            'bear_weak': 0.8,
            'sideways': 0.9
        }
        
        multiplier = regime_multipliers.get(regime, 1.0)
        adjusted_conf = min(1.0, confidence * multiplier)
        
        # 调整行动建议
        action_advice = action
        if regime in ['bear_strong', 'bear_weak'] and action == 'BUY':
            action_advice = 'WAIT'
        elif regime == 'bull_strong' and action == 'SELL':
            action_advice = 'HOLD'
        
        return {
            'tool': tool,
            'original_action': action,
            'adjusted_action': action_advice,
            'original_confidence': confidence,
            'adjusted_confidence': adjusted_conf,
            'reason': f'市场状态:{regime}'
        }
    
    def _generate_analysis(self, market_data: Dict, regime: str) -> str:
        """生成分析"""
        btc = market_data.get('btc_change', 0)
        eth = market_data.get('eth_change', 0)
        avg = market_data.get('avg_change', 0)
        
        analysis = f"""
        📊 市场分析:
        - BTC 24h: {btc:+.2f}%
        - ETH 24h: {eth:+.2f}%
        - 市场平均: {avg:+.2f}%
        
        🎯 当前状态: {self.market_regimes.get(regime, {}).get('name', '未知')}
        - 特征: {self.market_regimes.get(regime, {}).get('特征', '')}
        - 建议: {self.market_regimes.get(regime, {}).get('建议', '')}
        
        💡 专家观点:
        """
        
        if btc > 5:
            analysis += "BTC领涨，市场情绪高涨，建议关注强势币种。"
        elif btc < -5:
            analysis += "BTC领跌，风险厌恶情绪浓厚，建议减仓观望。"
        elif avg > 2:
            analysis += "市场整体上涨，但需注意短期回调风险。"
        elif avg < -2:
            analysis += "市场整体下跌，谨慎为主。"
        else:
            analysis += "市场震荡为主，建议高抛低吸。"
        
        return analysis

# ==================== 风险评估 ====================

class RiskAssessment:
    """风险评估系统"""
    
    def __init__(self):
        self.risk_metrics = {}
    
    def assess_risk(self, positions: List[Dict], market_data: Dict) -> Dict:
        """评估风险"""
        # 计算VaR (Value at Risk)
        var_95 = self._calculate_var(positions, 0.95)
        
        # 计算波动率
        portfolio_vol = self._calculate_volatility(positions)
        
        # 集中度风险
        concentration = self._calculate_concentration(positions)
        
        # 市场风险
        market_risk = self._assess_market_risk(market_data)
        
        # 综合风险评分
        risk_score = min(100, (
            var_95 * 30 +
            portfolio_vol * 20 +
            concentration * 25 +
            market_risk * 25
        ))
        
        return {
            'risk_score': risk_score,
            'risk_level': self._get_risk_level(risk_score),
            'var_95': var_95,
            'portfolio_volatility': portfolio_vol,
            'concentration_risk': concentration,
            'market_risk': market_risk,
            'warnings': self._generate_warnings(risk_score, var_95, concentration)
        }
    
    def _calculate_var(self, positions: List[Dict], confidence: float) -> float:
        """计算VaR"""
        if not positions:
            return 0
        
        # 简化版 - 实际需要更多数据
        return len(positions) * 0.02  # 假设每个头寸2%风险
    
    def _calculate_volatility(self, positions: List[Dict]) -> float:
        """计算组合波动率"""
        if not positions:
            return 0
        return min(1.0, len(positions) * 0.05)
    
    def _calculate_concentration(self, positions: List[Dict]) -> float:
        """计算集中度"""
        if not positions:
            return 0
        
        # 简化 - 越少越集中
        if len(positions) <= 1:
            return 0.9
        elif len(positions) <= 3:
            return 0.6
        elif len(positions) <= 5:
            return 0.3
        else:
            return 0.1
    
    def _assess_market_risk(self, market_data: Dict) -> float:
        """评估市场风险"""
        btc_change = abs(market_data.get('btc_change', 0))
        
        if btc_change > 10:
            return 0.9
        elif btc_change > 5:
            return 0.6
        elif btc_change > 2:
            return 0.3
        else:
            return 0.1
    
    def _get_risk_level(self, score: float) -> str:
        if score >= 70:
            return '极高'
        elif score >= 50:
            return '高'
        elif score >= 30:
            return '中'
        else:
            return '低'
    
    def _generate_warnings(self, risk_score: float, var: float, concentration: float) -> List[str]:
        """生成警告"""
        warnings = []
        
        if risk_score >= 70:
            warnings.append('⚠️ 风险极高，建议减仓')
        if var > 0.1:
            warnings.append('⚠️ VaR过高，单日可能损失超过10%')
        if concentration > 0.7:
            warnings.append('⚠️ 持仓过于集中')
        
        return warnings

# ==================== 优化建议 ====================

class OptimizationAdvisor:
    """优化建议系统"""
    
    def __init__(self):
        self.history = deque(maxlen=100)
    
    def analyze_and_suggest(self, system_state: Dict) -> Dict:
        """分析并给出优化建议"""
        mode = system_state.get('mode', 'balanced')
        positions = system_state.get('positions', [])
        signals = system_state.get('signals', [])
        risk = system_state.get('risk', {})
        
        suggestions = []
        
        # 模式优化
        suggestions.extend(self._mode_suggestions(mode, positions, risk))
        
        # 工具优化
        suggestions.extend(self._tool_suggestions(positions, signals))
        
        # 风险优化
        if risk.get('risk_score', 0) > 50:
            suggestions.append({
                'type': 'risk',
                'priority': 'high',
                'suggestion': '建议切换到保守模式或减仓',
                'action': 'set_mode:conservative'
            })
        
        # 资源优化
        suggestions.extend(self._resource_suggestions(system_state))
        
        return {
            'suggestions': suggestions,
            'priority_actions': [s for s in suggestions if s.get('priority') == 'high'],
            'optimization_score': self._calculate_optimization_score(system_state)
        }
    
    def _mode_suggestions(self, mode: str, positions: List[Dict], risk: Dict) -> List[Dict]:
        """模式建议"""
        suggestions = []
        
        if len(positions) > 5 and mode == 'balanced':
            suggestions.append({
                'type': 'mode',
                'priority': 'medium',
                'suggestion': '持仓过多，建议切换到保守模式',
                'action': 'set_mode:conservative'
            })
        
        if risk.get('risk_score', 0) < 30 and mode == 'conservative':
            suggestions.append({
                'type': 'mode',
                'priority': 'low',
                'suggestion': '风险较低，可以考虑激进模式追求收益',
                'action': 'set_mode:aggressive'
            })
        
        return suggestions
    
    def _tool_suggestions(self, positions: List[Dict], signals: List[Dict]) -> List[Dict]:
        """工具建议"""
        suggestions = []
        
        # 统计各工具使用
        tool_usage = {}
        for p in positions:
            tool = p.get('tool', 'unknown')
            tool_usage[tool] = tool_usage.get(tool, 0) + 1
        
        # 找出使用最少的工具
        all_tools = ['rabbit', 'mole', 'prediction', 'follow', 'hitchhike']
        unused = [t for t in all_tools if t not in tool_usage]
        
        if len(positions) < 3 and unused:
            suggestions.append({
                'type': 'diversification',
                'priority': 'medium',
                'suggestion': f'投资组合过于单一，建议尝试: {", ".join(unused)}',
                'action': f'enable_tools:{",".join(unused[:2])}'
            })
        
        return suggestions
    
    def _resource_suggestions(self, system_state: Dict) -> List[Dict]:
        """资源建议"""
        return []
    
    def _calculate_optimization_score(self, system_state: Dict) -> float:
        """计算优化分数"""
        # 简化版
        positions = system_state.get('positions', [])
        risk = system_state.get('risk', {})
        
        score = 50
        
        if len(positions) >= 3:
            score += 10
        if len(positions) <= 8:
            score += 10
        if risk.get('risk_score', 100) < 50:
            score += 20
        
        return min(100, score)

# ==================== 专家版核心系统 ====================

class BeidouQixinExpert:
    """专家版北斗七鑫"""
    
    def __init__(self, mode: str = 'balanced'):
        self.mode = mode
        self.expert_engine = ExpertAnalysisEngine()
        self.risk_assessor = RiskAssessment()
        self.optimizer = OptimizationAdvisor()
        
        # 状态
        self.positions = {}
        self.signals_history = deque(maxlen=100)
        self.market_data = {}
    
    def run_expert_analysis(self, signals: List[Dict]) -> Dict:
        """运行专家分析"""
        # 1. 获取市场数据
        market_data = self._get_market_data()
        
        # 2. 专家建议
        expert = self.expert_engine.get_expert_recommendation(
            'multi', signals, market_data
        )
        
        # 3. 风险评估
        risk = self.risk_assessor.assess_risk(
            list(self.positions.values()), market_data
        )
        
        # 4. 优化建议
        system_state = {
            'mode': self.mode,
            'positions': list(self.positions.values()),
            'signals': signals,
            'risk': risk
        }
        optimization = self.optimizer.analyze_and_suggest(system_state)
        
        return {
            'expert_recommendation': expert,
            'risk_assessment': risk,
            'optimization': optimization,
            'market_data': market_data
        }
    
    def _get_market_data(self) -> Dict:
        """获取市场数据"""
        try:
            r = requests.get('https://api.binance.com/api/v3/ticker/24hr', timeout=10)
            data = r.json()
            
            btc = eth = avg = 0
            count = 0
            
            for t in data:
                symbol = t['symbol']
                change = float(t.get('priceChangePercent', 0))
                
                if symbol == 'BTCUSDT':
                    btc = change
                elif symbol == 'ETHUSDT':
                    eth = change
                
                if symbol.endswith('USDT'):
                    avg += change
                    count += 1
            
            avg = avg / count if count > 0 else 0
            
            # 计算波动率
            changes = [float(t.get('priceChangePercent', 0)) for t in data[:100]]
            volatility = np.std(changes) if changes else 0.02
            
            return {
                'btc_change': btc,
                'eth_change': eth,
                'avg_change': avg,
                'volatility': volatility,
                'timestamp': int(time.time())
            }
        except:
            return {'btc_change': 0, 'eth_change': 0, 'avg_change': 0, 'volatility': 0.02}
    
    def generate_report(self) -> str:
        """生成专家报告"""
        # 模拟数据
        signals = [
            {'tool': 'rabbit', 'confidence': 0.7, 'action': 'BUY', 'symbol': 'BTC'},
            {'tool': 'mole', 'confidence': 0.6, 'action': 'BUY', 'symbol': 'PEPE'},
        ]
        
        result = self.run_expert_analysis(signals)
        
        expert = result['expert_recommendation']
        risk = result['risk_assessment']
        optimization = result['optimization']
        
        report = f"""
╔════════════════════════════════════════════════════════════════╗
║                    🧠 北斗七鑫专家分析报告                    ║
╠════════════════════════════════════════════════════════════════╣
║
║  📊 市场状态
║  ─────────────────────────────────────────────────────────
║  当前状态: {expert['market_regime']}
║  状态名称: {expert['regime_name']}
║  市场建议: {expert['market_advice']}
║
║  💡 专家观点
{expert['expert_analysis']}
║
║  🛡️ 风险评估
║  ─────────────────────────────────────────────────────────
║  风险评分: {risk['risk_score']}/100 ({risk['risk_level']})
║  VaR(95%): {risk['var_95']:.1%}
║  组合波动: {risk['portfolio_volatility']:.1%}
║  集中度: {risk['concentration_risk']:.1%}
║  市场风险: {risk['market_risk']:.1%}
"""
        
        if risk['warnings']:
            for w in risk['warnings']:
                report += f"║  {w}\n"
        
        report += f"""║
║  🎯 优化建议
║  ─────────────────────────────────────────────────────────
║  优化分数: {optimization['optimization_score']}/100
"""
        
        for i, s in enumerate(optimization['suggestions'][:3], 1):
            report += f"║  {i}. {s['suggestion']}\n"
        
        report += """║
╚════════════════════════════════════════════════════════════════╝
"""
        
        return report

# ==================== 测试 ====================

def test_expert():
    """测试专家系统"""
    print("🧠 北斗七鑫专家系统测试")
    print("="*50)
    
    expert = BeidouQixinExpert('balanced')
    report = expert.generate_report()
    
    print(report)
    
    return expert

if __name__ == '__main__':
    test_expert()
