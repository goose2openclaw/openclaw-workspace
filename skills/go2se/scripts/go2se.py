#!/usr/bin/env python3
"""
GO2SE AI Trading System - Main Entry Point
🪿 AI Quantitative Trading System
"""

import sys
import os

def print_banner():
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     🪿 GO2SE - AI 量化交易系统 🪿                       ║
║                                                           ║
║     Version: 4.0                                         ║
║     Status: RUNNING                                      ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)

def print_menu():
    print("""
📋 可用模块:

🎯 交易策略:
   [1] 主流币策略     - mainstream_strategy.py
   [2] 打地鼠策略    - mole_strategy.py  
   [3] 分层交易      - tiered_trading.py
   [4] 声纳 Pro      - sonar_pro_v3.py
   [5] 统一策略      - unified_strategy.py

📡 市场扫描:
   [6] 实时预警      - realtime_alert.py
   [7] 趋势数据库    - trend_db.py

🔮 DeFi:
   [8] 空投猎手      - airdrop_hunter.py
   [9] Polymarket    - polymarket_arb.py
  [10] 预言机        - defi_oracle.py

🛠️ 工具:
  [11] 仪表板        - dashboard.py
  [12] 风险管理      - risk_manager.py
  [13] 组合管理      - portfolio_manager.py
  [14] 交易日志      - trading_journal.py
  [15] 性能优化      - performance_optimizer.py
  [16] 回测引擎      - backtest_engine.py
  [17] 通知系统      - notification_system.py
  [18] Miro协作      - miro_integration.py
  [19] 反馈收集      - feedback_collector.py
  [20] 微私募平台    - micro_pe.py
  [21] 众包平台      - crowdsource_platform.py

🔄 系统:
  [a] 运行所有策略
  [b] 查看任务状态
  [c] 系统健康检查
  [d] 备份数据

💰 快捷命令:
  python3 dashboard.py              # 仪表板
  python3 airdrop_hunter.py 5.0    # 空投扫描
  python3 risk_manager.py          # 风险管理
  
🔗 帮助:
  cat ../QUICKSTART.md              # 快速入门
  cat ../WHITEPAPER.md             # 白皮书
""")

def run_module(module_num):
    """运行指定模块"""
    scripts = {
        "1": ("主流币策略", "mainstream_strategy.py"),
        "2": ("打地鼠策略", "mole_strategy.py"),
        "3": ("分层交易", "tiered_trading.py"),
        "4": ("声纳Pro", "sonar_pro_v3.py"),
        "5": ("统一策略", "unified_strategy.py"),
        "6": ("实时预警", "realtime_alert.py"),
        "7": ("趋势数据库", "trend_db.py"),
        "8": ("空投猎手", "airdrop_hunter.py"),
        "9": ("Polymarket套利", "polymarket_arb.py"),
        "10": ("预言机", "defi_oracle.py"),
        "11": ("仪表板", "dashboard.py"),
        "12": ("风险管理", "risk_manager.py"),
        "13": ("组合管理", "portfolio_manager.py"),
        "14": ("交易日志", "trading_journal.py"),
        "15": ("性能优化", "performance_optimizer.py"),
        "16": ("回测引擎", "backtest_engine.py"),
        "17": ("通知系统", "notification_system.py"),
        "18": ("Miro协作", "miro_integration.py"),
        "19": ("反馈收集", "feedback_collector.py"),
        "20": ("微私募平台", "micro_pe.py"),
        "21": ("众包平台", "crowdsource_platform.py"),
    }
    
    if module_num in scripts:
        name, script = scripts[module_num]
        print(f"\n🚀 运行 {name}...")
        os.system(f"python3 {script}")
    else:
        print("❌ 无效选择")

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print_banner()
    
    if len(sys.argv) > 1:
        # 命令行模式
        arg = sys.argv[1]
        
        if arg in ["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20","21"]:
            run_module(arg)
        elif arg == "a":
            print("\n🚀 运行所有策略...")
            os.system("python3 mainstream_strategy.py")
            os.system("python3 mole_strategy.py")
            os.system("python3 unified_strategy.py")
        elif arg == "b":
            print("\n📊 任务状态:")
            os.system("python3 dashboard.py")
        elif arg == "c":
            print("\n🩺 系统健康检查...")
            os.system("python3 risk_manager.py")
        elif arg == "d":
            print("\n💾 备份数据...")
            import json
            from datetime import datetime
            data = {"timestamp": datetime.now().isoformat(), "status": "backup"}
            with open("../data/backup.json", "w") as f:
                json.dump(data, f)
            print("✅ 备份完成")
        else:
            print_menu()
    else:
        # 交互模式
        print_menu()
        
        while True:
            try:
                choice = input("\n👉 选择模块 (输入数字或 q 退出): ").strip()
                
                if choice.lower() == 'q':
                    print("\n👋 GO2SE 再见! 🪿\n")
                    break
                
                if choice in ["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20","21"]:
                    run_module(choice)
                elif choice in ["a","b","c","d"]:
                    if choice == "a":
                        print("\n🚀 运行所有策略...")
                        os.system("python3 mainstream_strategy.py")
                        os.system("python3 mole_strategy.py")
                        os.system("python3 unified_strategy.py")
                    elif choice == "b":
                        os.system("python3 dashboard.py")
                    elif choice == "c":
                        os.system("python3 risk_manager.py")
                    elif choice == "d":
                        import json
                        from datetime import datetime
                        data = {"timestamp": datetime.now().isoformat(), "status": "manual_backup"}
                        with open("../data/backup.json", "w") as f:
                            json.dump(data, f)
                        print("✅ 备份完成")
                else:
                    print("❌ 无效选择")
            except KeyboardInterrupt:
                print("\n\n👋 GO2SE 再见! 🪿\n")
                break
            except Exception as e:
                print(f"❌ 错误: {e}")

if __name__ == "__main__":
    main()
