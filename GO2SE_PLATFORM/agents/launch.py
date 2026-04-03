#!/usr/bin/env python3
"""
GO2SE 管理层 Agent 启动器

用法:
    python launch.py all         # 启动所有 Agent
    python launch.py ceo        # 启动 CEO
    python launch.py developer  # 启动技术负责人
    python launch.py market     # 启动市场负责人
    python launch.py strategy    # 启动策略负责人
"""

import os
import sys

AGENTS_DIR = os.path.dirname(os.path.abspath(__file__))

AGENT_CONFIGS = {
    "owner": {
        "name": "GO2SE Owner",
        "file": "go2se_owner.md",
        "description": "平台投资人/所有者"
    },
    "ceo": {
        "name": "GO2SE CEO",
        "file": "go2se_ceo.md",
        "description": "首席执行官"
    },
    "developer": {
        "name": "GO2SE Developer Leader",
        "file": "go2se_developer_leader.md",
        "description": "技术开发负责人"
    },
    "market": {
        "name": "GO2SE Market Leader",
        "file": "go2se_market_leader.md",
        "description": "市场负责人"
    },
    "strategy": {
        "name": "GO2SE Strategy Leader",
        "file": "go2se_strategy_leader.md",
        "description": "策略负责人"
    }
}

def load_prompt(agent_key):
    """加载 Agent 提示词"""
    config = AGENT_CONFIGS[agent_key]
    filepath = os.path.join(AGENTS_DIR, config["file"])
    with open(filepath, "r") as f:
        return f.read()

def list_agents():
    """列出所有可用 Agent"""
    print("\n📋 GO2SE 管理团队:")
    print("=" * 50)
    for key, config in AGENT_CONFIGS.items():
        print(f"  {key:12} - {config['name']}")
        print(f"             {config['description']}")
    print("=" * 50)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python launch.py <agent>")
        list_agents()
        sys.exit(1)
    
    agent = sys.argv[1].lower()
    
    if agent == "list":
        list_agents()
    elif agent == "all":
        print("🚀 启动所有 GO2SE 管理 Agent...")
        for key in AGENT_CONFIGS:
            print(f"  ✓ {AGENT_CONFIGS[key]['name']}")
        print("\n💡 使用 sessions_spawn 启动各个 Agent 会话")
    elif agent in AGENT_CONFIGS:
        config = AGENT_CONFIGS[agent]
        print(f"🚀 启动 {config['name']}...")
        prompt = load_prompt(agent)
        print(f"\n📝 提示词预览 (前500字符):")
        print("-" * 50)
        print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
        print("-" * 50)
    else:
        print(f"❌ 未知 Agent: {agent}")
        list_agents()
        sys.exit(1)
