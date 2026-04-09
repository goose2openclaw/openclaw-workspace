#!/usr/bin/env python3
"""
GO2SE Strategy Auto-Importer
策略自动导入模块 - 从外部源自动导入策略
"""

import os
import json
import random
from datetime import datetime
from typing import Dict, List

class StrategyImporter:
    """策略导入器"""
    
    def __init__(self):
        self.data_dir = "/root/.openclaw/workspace/skills/go2se/data"
        self.strategies_dir = "/root/.openclaw/workspace/skills/go2se/scripts"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 内置策略模板
        self.templates = {
            "grid": {
                "name": "网格交易策略",
                "type": "grid",
                "parameters": {
                    "grid_count": 10,
                    "grid_spacing": 1.5,
                    "order_size": 100,
                    "stop_loss": 5.0
                },
                "risk_level": "low"
            },
            "trend_following": {
                "name": "趋势跟随策略",
                "type": "trend",
                "parameters": {
                    "ma_periods": [20, 50, 200],
                    "rsi_period": 14,
                    "rsi_oversold": 30,
                    "rsi_overbought": 70
                },
                "risk_level": "medium"
            },
            "mean_reversion": {
                "name": "均值回归策略",
                "type": "mean_reversion",
                "parameters": {
                    "lookback_period": 20,
                    "std_dev_multiplier": 2.0,
                    "entry_threshold": 0.02
                },
                "risk_level": "medium"
            },
            "momentum": {
                "name": "动量策略",
                "type": "momentum",
                "parameters": {
                    "lookback": 12,
                    "threshold": 0.05,
                    "volume_filter": 1.5
                },
                "risk_level": "high"
            },
            "arbitrage": {
                "name": "跨交易所套利",
                "type": "arbitrage",
                "parameters": {
                    "min_spread": 0.5,
                    "max_position": 1000,
                    "exchanges": ["binance", "bybit", "okx"]
                },
                "risk_level": "medium"
            }
        }
    
    def import_from_template(self, template_name: str, config: Dict = None) -> Dict:
        """从模板导入策略"""
        if template_name not in self.templates:
            return {"error": f"Template {template_name} not found"}
        
        template = self.templates[template_name].copy()
        if config:
            template["parameters"].update(config)
        
        # 添加元数据
        template["imported_at"] = datetime.now().isoformat()
        template["status"] = "active"
        
        return template
    
    def generate_strategy_code(self, template: Dict) -> str:
        """生成策略代码"""
        strategy_type = template["type"]
        params = template["parameters"]
        
        code = f'''#!/usr/bin/env python3
"""
GO2SE Strategy - {template['name']}
Type: {template['type']}
Risk: {template['risk_level']}
Imported: {template['imported_at']}
"""

import random

class {strategy_type.title().replace('_', '')}Strategy:
    """Auto-generated strategy"""
    
    def __init__(self):
        self.name = "{template['name']}"
        self.type = "{strategy_type}"
        self.params = {params}
        self.risk_level = "{template['risk_level']}"
    
    def analyze(self, data: dict) -> dict:
        """分析市场数据"""
        # Strategy logic here
        return {{"action": "HOLD", "confidence": 0}}
    
    def run(self):
        """运行策略"""
        print(f"Running {{self.name}}...")
        return self.analyze({{}})

if __name__ == "__main__":
    strategy = {strategy_type.title().replace('_', '')}Strategy()
    strategy.run()
'''
        return code
    
    def save_strategy(self, template: Dict) -> str:
        """保存策略"""
        # 生成文件名
        strategy_type = template["type"]
        filename = f"strategy_{strategy_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}.py"
        filepath = os.path.join(self.strategies_dir, filename)
        
        # 生成代码
        code = self.generate_strategy_code(template)
        
        # 保存
        with open(filepath, 'w') as f:
            f.write(code)
        
        # 更新索引
        index_file = os.path.join(self.data_dir, "strategies_index.json")
        if os.path.exists(index_file):
            with open(index_file, 'r') as f:
                index = json.load(f)
        else:
            index = {"strategies": []}
        
        index["strategies"].append({
            "name": template["name"],
            "type": template["type"],
            "filename": filename,
            "imported_at": template["imported_at"],
            "status": "active"
        })
        
        with open(index_file, 'w') as f:
            json.dump(index, f, indent=2)
        
        return filepath
    
    def list_templates(self) -> List[Dict]:
        """列出可用模板"""
        return [
            {"name": name, **template}
            for name, template in self.templates.items()
        ]
    
    def run_import(self, template_name: str = None, config: Dict = None):
        """运行导入"""
        print("\n" + "="*50)
        print("📥 GO2SE 策略导入器")
        print("="*50)
        
        # 列出模板
        templates = self.list_templates()
        print(f"\n📋 可用模板 ({len(templates)}):")
        for i, t in enumerate(templates, 1):
            risk_icon = "🟢" if t["risk_level"] == "low" else ("🟡" if t["risk_level"] == "medium" else "🔴")
            print(f"   {i}. {t['name']} [{risk_icon} {t['risk_level']}]")
        
        # 如果指定了模板
        if template_name:
            result = self.import_from_template(template_name, config)
            if "error" in result:
                print(f"\n❌ 错误: {result['error']}")
                return
            
            filepath = self.save_strategy(result)
            print(f"\n✅ 策略已导入: {filepath}")
            print(f"   名称: {result['name']}")
            print(f"   类型: {result['type']}")
            print(f"   风险: {result['risk_level']}")
        else:
            # 演示：导入所有模板
            print(f"\n📥 导入所有模板...")
            for t in templates:
                result = self.import_from_template(t["name"])
                filepath = self.save_strategy(result)
                print(f"   ✅ {result['name']}")
        
        print("\n" + "="*50)


def main():
    import sys
    
    importer = StrategyImporter()
    
    template = sys.argv[1] if len(sys.argv) > 1 else None
    config = None
    
    if len(sys.argv) > 2:
        try:
            config = json.loads(sys.argv[2])
        except:
            pass
    
    importer.run_import(template, config)


if __name__ == "__main__":
    main()
