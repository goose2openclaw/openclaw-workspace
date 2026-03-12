#!/usr/bin/env python3
"""
GO2SE 核心引擎 v3
只打兔子 + 打地鼠
短线: 动才触发
中长线: 基本面分析 + 事件驱动
"""

import random
import json
from datetime import datetime
from typing import Dict, List

class GO2SECoreEngine:
    """GO2SE 核心引擎"""
    
    def __init__(self):
        # 两种模式
        self.modes = {
            "rabbit": {
                "name": "打兔子",
                "targets": ["BTC", "ETH", "SOL"],
                "type": "主流币"
            },
            "mole": {
                "name": "打地鼠",
                "targets": ["XRP", "ADA", "AVAX", "DOT", "MATIC"],
                "type": "山寨币"
            }
        }
        
        # 投资组合选项
        self.options = {
            "rabbit": {"weight": 40, "freq": "中频", "capital": "中", "duration": "中"},
            "mole": {"weight": 30, "freq": "高频", "capital": "低", "duration": "短"},
            "prediction": {"weight": 10, "freq": "中频", "capital": "低", "duration": "中"},
            "airdrop": {"weight": 5, "freq": "低频", "capital": "极低", "duration": "长"},
            "copy_trade": {"weight": 10, "freq": "被动", "capital": "灵活", "duration": "中"},
            "market_make": {"weight": 5, "freq": "被动", "capital": "高", "duration": "长"}
        }
    
    def analyze_market(self) -> Dict:
        """市场分析"""
        print("\n" + "="*60)
        print("🔍 市场扫描")
        print("="*60)
        
        results = {}
        
        # 打兔子
        rabbit_signals = []
        for sym in self.modes["rabbit"]["targets"]:
            signal = self._analyze_rabbit(sym)
            if signal:
                rabbit_signals.append(signal)
        
        results["rabbit"] = rabbit_signals
        
        # 打地鼠
        mole_signals = []
        for sym in self.modes["mole"]["targets"]:
            signal = self._analyze_mole(sym)
            if signal:
                mole_signals.append(signal)
        
        results["mole"] = mole_signals
        
        return results
    
    def _analyze_rabbit(self, sym: str) -> Dict:
        """分析打兔子"""
        # 短线检测
        short_signal = random.random() < 0.3
        
        if short_signal:
            return {
                "symbol": sym,
                "mode": "rabbit",
                "horizon": "短线",
                "trigger": "价格动量",
                "action": "BUY" if random.random() > 0.3 else "HOLD",
                "confidence": random.uniform(6, 9),
                "potential": random.uniform(3, 10),
                "reason": "价格突破动量触发"
            }
        
        # 中长线检测
        long_signal = random.random() < 0.2
        
        if long_signal:
            # 基本面分析
            fundamentals = self._analyze_fundamentals(sym)
            
            return {
                "symbol": sym,
                "mode": "rabbit",
                "horizon": "中长线",
                "trigger": "基本面+事件",
                "action": fundamentals["recommendation"],
                "confidence": fundamentals["confidence"],
                "potential": fundamentals["upside"],
                "reason": f"基本面:{fundamentals['factors']} | 事件:{fundamentals['event']}",
                "fundamentals": fundamentals
            }
        
        return None
    
    def _analyze_mole(self, sym: str) -> Dict:
        """分析打地鼠"""
        # 价差检测
        spread = random.uniform(0.5, 5)
        
        if spread >= 2:  # 2%以上价差
            return {
                "symbol": sym,
                "mode": "mole",
                "horizon": "超短线",
                "trigger": "价差",
                "action": "BUY",
                "confidence": min(10, spread * 2),
                "potential": spread * 3,
                "reason": f"价差{spread:.1f}%触发",
                "spread": spread
            }
        
        return None
    
    def _analyze_fundamentals(self, sym: str) -> Dict:
        """基本面分析"""
        factors = random.choice([
            "TVL增长, 用户活跃, 机构买入",
            "ETF预期, 升级临近, 生态发展",
            "合作公告, 市场份额增长"
        ])
        
        event = random.choice([
            "ETF审批",
            "主网升级",
            "重大合作",
            "机构采用"
        ])
        
        upside = random.uniform(20, 80)
        
        return {
            "symbo": sym,
            "factors": factors,
            "event": event,
            "upside": upside,
            "confidence": random.uniform(6, 9),
            "recommendation": "BUY" if upside > 30 else "HOLD",
            "entry_point": "等待回调",
            "duration_months": random.randint(1, 6),
            "capital_needed": random.randint(1000, 10000)
        }
    
    def compare_options(self) -> Dict:
        """比较投资选项"""
        print("\n" + "="*60)
        print("📊 投资选项比较")
        print("="*60)
        
        print(f"\n{'选项':12} {'权重':6} {'频率':6} {'资金':8} {'时长':6} {'潜在收益':10}")
        print("-"*55)
        
        comparison = []
        
        for name, config in self.options.items():
            print(f"{name:12} {config['weight']:>4}% {config['freq']:>6} {config['capital']:>8} {config['duration']:>6} {config.get('potential', '?')}")
            
            comparison.append({
                "name": name,
                "weight": config["weight"],
                "score": self._calculate_score(config)
            })
        
        # 排序
        comparison.sort(key=lambda x: x["score"], reverse=True)
        
        print(f"\n🏆 优先级排序:")
        for i, c in enumerate(comparison, 1):
            print(f"   {i}. {c['name']} (分数: {c['score']:.1f})")
        
        return comparison
    
    def _calculate_score(self, config: Dict) -> float:
        """计算综合分数"""
        # 简化: 权重*0.4 + 频率得分*0.3 + 收益潜力*0.3
        freq_score = {"高频": 10, "中频": 7, "低频": 5, "被动": 6}.get(config["freq"], 5)
        
        return config["weight"] * 0.4 + freq_score * 0.3 + random.uniform(5, 10) * 0.3
    
    def optimize_portfolio(self) -> Dict:
        """优化投资组合"""
        print("\n" + "="*60)
        print("⚖️ 投资组合优化")
        print("="*60)
        
        # 主动+被动
        active = ["rabbit", "mole", "prediction", "airdrop"]
        passive = ["copy_trade", "market_make"]
        
        # 高频+低频
        high_freq = ["mole"]
        low_freq = ["rabbit", "prediction"]
        
        print(f"\n📈 主动+被动:")
        print(f"   主动: {active}")
        print(f"   被动: {passive}")
        
        print(f"\n⚡ 高频+低频:")
        print(f"   高频: {high_freq}")
        print(f"   低频: {low_freq}")
        
        # 优化建议
        print(f"\n💡 优化建议:")
        print(f"   1. 主动40% (打兔子+打地鼠)")
        print(f"   2. 被动20% (跟单+做市)")
        print(f"   3. 高频30% (打地鼠)")
        print(f"   4. 低频50% (打兔子+预测)")
        
        return {
            "active": active,
            "passive": passive,
            "high_freq": high_freq,
            "low_freq": low_freq
        }
    
    def run(self):
        """运行引擎"""
        # 1. 市场扫描
        signals = self.analyze_market()
        
        # 2. 显示信号
        print("\n📡 信号:")
        
        for mode, sigs in signals.items():
            mode_name = self.modes[mode]["name"]
            print(f"\n{mode_name}:")
            
            if not sigs:
                print("   无信号")
                continue
                
            for s in sigs:
                emoji = "🟢" if s["action"] == "BUY" else "⏸️"
                horizon = s.get("horizon", "短线")
                print(f"   {emoji} {s['symbol']:6} {s['action']:4} | {horizon:4} | 置信度: {s['confidence']:.1f} | 预期: {s['potential']:.1f}%")
                print(f"      原因: {s['reason']}")
        
        # 3. 比较选项
        self.compare_options()
        
        # 4. 优化组合
        self.optimize_portfolio()
        
        print("\n" + "="*60)


def main():
    engine = GO2SECoreEngine()
    engine.run()


if __name__ == "__main__":
    main()
