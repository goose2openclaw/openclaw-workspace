#!/usr/bin/env python3
"""
GO2SE Unified Launcher
统一启动器 - 一键运行所有功能
"""

import os
import sys

class GO2SELauncher:
    """统一启动器"""
    
    def __init__(self):
        self.base_dir = "/root/.openclaw/workspace/skills/go2se/scripts"
        os.chdir(self.base_dir)
        
        self.categories = {
            "1": {"name": "🐰 赚钱工具", "scripts": [
                ("mainstream_strategy.py", "打兔子 - 主流币策略"),
                ("mole_strategy.py", "打地鼠 - 山寨币套利"),
                ("airdrop_hunter.py", "撸空投 - 新币监控"),
                ("polymarket_arb.py", "预测市场 - Polymarket套利"),
            ]},
            "2": {"name": "🤝 做市商联盟", "scripts": [
                ("market_maker_alliance.py", "做市商联盟"),
                ("strategy_deep_analyzer.py", "策略深度分析"),
                ("market_simulator.py", "多市场模拟"),
            ]},
            "3": {"name": "🏦 投资平台", "scripts": [
                ("micro_pe_v2.py", "微私募平台"),
                ("token_launch.py", "代币发行"),
                ("crowdsource_platform.py", "众包平台"),
            ]},
            "4": {"name": "🛠️ 工具箱", "scripts": [
                ("dashboard.py", "仪表板"),
                ("risk_manager.py", "风险管理"),
                ("portfolio_manager.py", "组合管理"),
                ("trading_journal.py", "交易日志"),
                ("backtest_engine.py", "回测引擎"),
                ("performance_optimizer.py", "性能优化"),
            ]},
            "5": {"name": "📡 信号系统", "scripts": [
                ("advanced_signals.py", "高级信号"),
                ("trend_updater.py", "趋势更新"),
                ("competitor_analyzer.py", "竞品分析"),
            ]},
            "6": {"name": "🌐 生态", "scripts": [
                ("yield_aggregator.py", "收益聚合"),
                ("community_system.py", "社区治理"),
                ("contract_generator.py", "合约生成"),
                ("miro_integration.py", "Miro协作"),
            ]},
        }
    
    def run_script(self, script):
        """运行脚本"""
        print(f"\n🚀 运行: {script}")
        os.system(f"python3 {script}")
    
    def main_menu(self):
        """主菜单"""
        while True:
            print("\n" + "="*60)
            print("🪿 GO2SE 量化交易系统 v2.0".center(60))
            print("="*60)
            
            print("\n📋 功能分类:")
            for key, cat in self.categories.items():
                print(f"  [{key}] {cat['name']}")
            
            print("\n  [A] 全部运行")
            print("  [Q] 退出")
            
            choice = input("\n👉 选择: ").strip().upper()
            
            if choice == "Q":
                print("\n👋 再见! 🪿\n")
                break
            elif choice == "A":
                self.run_all()
            elif choice in self.categories:
                self.category_menu(choice)
            else:
                print("❌ 无效选择")
    
    def category_menu(self, cat_key):
        """分类菜单"""
        cat = self.categories[cat_key]
        
        while True:
            print(f"\n📂 {cat['name']}")
            print("-"*40)
            
            scripts = cat['scripts']
            for i, (script, desc) in enumerate(scripts, 1):
                print(f"  [{i}] {desc}")
            
            print("\n  [B] 返回")
            print("  [A] 全部运行")
            
            choice = input("\n👉 选择: ").strip().upper()
            
            if choice == "B":
                break
            elif choice == "A":
                for script, _ in scripts:
                    self.run_script(script)
            else:
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(scripts):
                        self.run_script(scripts[idx][0])
                    else:
                        print("❌ 无效选择")
                except:
                    print("❌ 请输入数字")
    
    def run_all(self):
        """运行所有"""
        print("\n⚠️ 确认运行所有策略? (y/n): ", end="")
        if input().strip().lower() != "y":
            return
        
        print("\n" + "="*60)
        print("🚀 运行所有赚钱工具")
        print("="*60)
        
        # 赚钱工具
        for script, desc in self.categories["1"]["scripts"]:
            print(f"\n{'='*40}")
            print(f"▶ {desc}")
            print(f"{'='*40}")
            os.system(f"python3 {script}")
        
        print("\n✅ 全部完成!")


def main():
    launcher = GO2SELauncher()
    
    if len(sys.argv) > 1:
        # 命令行模式
        script = sys.argv[1]
        launcher.run_script(script)
    else:
        # 交互模式
        launcher.main_menu()


if __name__ == "__main__":
    main()
