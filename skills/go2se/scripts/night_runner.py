#!/usr/bin/env python3
"""
Go2Se 夜间持续迭代系统
- 整晚持续运行
- 每15分钟执行一次迭代
- 实时调整策略
- 学习改进
"""

import json
import time
import random
import requests
from datetime import datetime
from pathlib import Path
import sys

class NightRunner:
    def __init__(self):
        self.data_dir = Path("/root/.openclaw/workspace/skills/go2se/data")
        self.data_dir.mkdir(exist_ok=True)
        self.state_file = self.data_dir / "night_state.json"
        self.log_file = self.data_dir / "night_runner.log"
        self.load_state()
        
        # Trading parameters (sandbox mode by default)
        self.sandbox = True
        self.min_confidence = 6.0
        
    def load_state(self):
        if self.state_file.exists():
            with open(self.state_file) as f:
                self.state = json.load(f)
        else:
            self.state = {
                "start_time": datetime.now().isoformat(),
                "iterations": 0,
                "total_signals": 0,
                "trades_executed": 0,
                "pnl": 0,
                "weights": {
                    "mainstream": 0.35,
                    "mole": 0.30,
                    "airdrop": 0.15,
                    "oracle": 0.10,
                    "copy_trade": 0.10
                },
                "best_performers": [],
                "adjustments_log": []
            }
    
    def save_state(self):
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def log(self, msg):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {msg}"
        print(log_msg)
        with open(self.log_file, 'a') as f:
            f.write(log_msg + "\n")
    
    def fetch_real_prices(self):
        """获取实时价格"""
        try:
            # Fetch from Binance public API
            url = "https://api.binance.com/api/v3/ticker/24hr"
            params = {"symbol": "BTCUSDT"}
            r = requests.get(url, params=params, timeout=5)
            if r.status_code == 200:
                data = r.json()
                return {
                    "BTC": {
                        "price": float(data["lastPrice"]),
                        "change": float(data["priceChangePercent"]),
                        "volume": float(data["volume"])
                    }
                }
        except Exception as e:
            self.log(f"⚠️ 价格获取失败: {e}")
        
        # Fallback
        return {"BTC": {"price": 82000, "change": 2.5, "volume": 28000}}
    
    def fetch_signals(self):
        """获取交易信号"""
        signals = []
        
        # Real price data
        prices = self.fetch_real_prices()
        
        # Generate signals based on price action
        for coin, data in prices.items():
            change = data["change"]
            price = data["price"]
            
            # Simple signal logic
            if change > 3:
                action = "BUY"
                confidence = min(9, 5 + change)
                risk = "low" if change < 5 else "medium"
            elif change < -3:
                action = "SELL"
                confidence = min(9, 5 + abs(change))
                risk = "low" if abs(change) < 5 else "medium"
            else:
                action = "HOLD"
                confidence = random.uniform(4, 7)
                risk = "medium"
            
            signals.append({
                "coin": coin,
                "action": action,
                "confidence": round(confidence, 1),
                "potential": round(abs(change) * 1.5, 1),
                "risk": risk,
                "price": price,
                "timestamp": datetime.now().isoformat()
            })
        
        # Add simulated signals for other markets
        simulated = [
            {"coin": "ETH", "action": "BUY", "confidence": 7.5, "potential": 8.2, "risk": "low"},
            {"coin": "SOL", "action": "BUY", "confidence": 6.8, "potential": 12.5, "risk": "medium"},
            {"coin": "PEPE", "action": "HOLD", "confidence": 5.2, "potential": 15.0, "risk": "high"},
        ]
        signals.extend(simulated)
        
        return signals
    
    def analyze_and_adjust(self, signals):
        """分析信号并调整"""
        buy_signals = [s for s in signals if s["action"] == "BUY"]
        
        self.log(f"📊 分析: {len(buy_signals)}/{len(signals)} 买入信号")
        
        # Track best performers
        for signal in buy_signals:
            if signal["confidence"] >= self.min_confidence:
                self.state["best_performers"].append({
                    "coin": signal["coin"],
                    "confidence": signal["confidence"],
                    "potential": signal["potential"],
                    "timestamp": datetime.now().isoformat()
                })
        
        # Keep only recent
        self.state["best_performers"] = self.state["best_performers"][-20:]
        
        # Adjust weights based on confidence
        if len(buy_signals) > 3:
            self.state["weights"]["mainstream"] = min(0.45, 
                self.state["weights"]["mainstream"] + 0.02)
            self.state["weights"]["mole"] = max(0.15,
                self.state["weights"]["mole"] - 0.01)
        
        self.state["adjustments_log"].append({
            "time": datetime.now().isoformat(),
            "signals": len(signals),
            "buy": len(buy_signals),
            "weights": self.state["weights"].copy()
        })
        
        # Keep only recent adjustments
        self.state["adjustments_log"] = self.state["adjustments_log"][-50:]
        
        return buy_signals
    
    def execute_trade(self, signal):
        """执行交易（模拟）"""
        if self.sandbox:
            self.log(f"🔄 [模拟] {signal['coin']}: {signal['action']} @ ${signal.get('price', 'N/A')}")
            self.state["trades_executed"] += 1
            pnl = random.uniform(-5, 15)  # Simulated PnL
            self.state["pnl"] += pnl
            return {"status": "simulated", "pnl": pnl}
        else:
            # Real trading (not implemented in this version)
            return {"status": "disabled"}
    
    def run_iteration(self):
        """执行一次迭代"""
        self.state["iterations"] += 1
        iteration = self.state["iterations"]
        
        self.log(f"\n{'='*50}")
        self.log(f"🌙 迭代 #{iteration} | {datetime.now().strftime('%H:%M:%S')}")
        self.log(f"{'='*50}")
        
        # Step 1: Fetch signals
        signals = self.fetch_signals()
        self.state["total_signals"] += len(signals)
        
        # Step 2: Analyze and adjust
        buy_signals = self.analyze_and_adjust(signals)
        
        # Step 3: Execute trades for high confidence signals
        executed = 0
        for signal in buy_signals:
            if signal["confidence"] >= self.min_confidence:
                result = self.execute_trade(signal)
                executed += 1
                time.sleep(0.5)  # Rate limiting
        
        # Save state
        self.save_state()
        
        # Summary
        self.log(f"✅ 完成: {len(signals)} 信号, {executed} 交易执行")
        self.log(f"   总交易: {self.state['trades_executed']}")
        self.log(f"   PnL: ${self.state['pnl']:.2f}")
        self.log(f"   权重: {self.state['weights']}")
        
        return {
            "iteration": iteration,
            "signals": len(signals),
            "executed": executed,
            "total_trades": self.state["trades_executed"],
            "pnl": self.state["pnl"],
            "weights": self.state["weights"]
        }
    
    def run(self, iterations=None, interval=900):
        """
        持续运行
        
        Args:
            iterations: 运行次数 (None = 无限)
            interval: 每次迭代间隔(秒)
        """
        self.log("=" * 60)
        self.log("🪿 Go2Se 夜间持续迭代系统启动")
        self.log(f"   模式: {'模拟' if self.sandbox else '实盘'}")
        self.log(f"   间隔: {interval}秒")
        self.log("=" * 60)
        
        count = 0
        while True:
            try:
                result = self.run_iteration()
                count += 1
                
                # Check if done
                if iterations and count >= iterations:
                    self.log(f"\n✅ 完成 {iterations} 次迭代")
                    break
                
                # Wait for next iteration
                self.log(f"   💤 等待 {interval}秒...")
                time.sleep(interval)
                
            except KeyboardInterrupt:
                self.log("\n⚠️ 用户中断")
                break
            except Exception as e:
                self.log(f"❌ 错误: {e}")
                time.sleep(60)  # Wait longer on error
        
        self.log(f"\n📊 最终统计")
        self.log(f"   总迭代: {count}")
        self.log(f"   总交易: {self.state['trades_executed']}")
        self.log(f"   总PnL: ${self.state['pnl']:.2f}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Go2Se夜间迭代")
    parser.add_argument("-n", "--iterations", type=int, default=None, help="迭代次数")
    parser.add_argument("-i", "--interval", type=int, default=900, help="间隔秒数")
    parser.add_argument("--live", action="store_true", help="实盘模式")
    args = parser.parse_args()
    
    runner = NightRunner()
    runner.sandbox = not args.live
    runner.run(iterations=args.iterations, interval=args.interval)

if __name__ == "__main__":
    main()
