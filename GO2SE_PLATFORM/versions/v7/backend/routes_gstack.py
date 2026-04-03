"""
GO2SE v7 — gstack API Routes
把gstack命令集成到GO2SE后端API

Routes:
    GET  /api/gstack                    - 列出所有gstack命令
    GET  /api/gstack/commands          - 同上
    GET  /api/gstack/categories         - 获取命令分类
    GET  /api/gstack/help/<command>     - 获取命令帮助
    POST /api/gstack/run               - 运行gstack命令
    POST /api/gstack/strategy-flow     - 策略开发完整流水线
    POST /api/gstack/review-flow       - 代码审查流水线
    POST /api/gstack/monitor-flow      - 交易监控流水线
"""

from flask import Blueprint, jsonify, request
import asyncio
import sys
import os

# 添加gstack-integration到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'gstack-integration'))

try:
    from gstack_manager import GstackManager, GO2SEGstackBridge
    GSTACK_AVAILABLE = True
except ImportError:
    GSTACK_AVAILABLE = False
    GstackManager = None
    GO2SEGstackBridge = None

gstack_bp = Blueprint('gstack', __name__, url_prefix='/api/gstack')


def get_manager():
    """获取gstack管理器实例"""
    if not GSTACK_AVAILABLE:
        return None
    return GstackManager()


def get_bridge():
    """获取GO2SE-gstack桥接器实例"""
    if not GSTACK_AVAILABLE:
        return None
    return GO2SEGstackBridge()


@gstack_bp.route('', methods=['GET'])
@gstack_bp.route('/commands', methods=['GET'])
def list_commands():
    """
    列出所有gstack命令
    
    Returns:
        {
            "available": true,
            "commands": [
                {
                    "name": "/office-hours",
                    "description": "...",
                    "category": "startup"
                },
                ...
            ],
            "total": 29
        }
    """
    manager = get_manager()
    if not manager:
        return jsonify({
            "available": False,
            "error": "gstack not installed. Install from: https://github.com/garrytan/gstack"
        }), 503
    
    if not manager.is_available():
        return jsonify({
            "available": False,
            "error": "gstack not found at ~/.claude/skills/gstack"
        }), 503
    
    commands = []
    for cmd in manager.COMMANDS.values():
        commands.append({
            "name": cmd.name,
            "description": cmd.description,
            "category": cmd.category,
            "requires_browser": cmd.requires_browser,
            "requires_git": cmd.requires_git
        })
    
    return jsonify({
        "available": True,
        "commands": commands,
        "total": len(commands)
    })


@gstack_bp.route('/categories', methods=['GET'])
def get_categories():
    """获取所有命令分类"""
    manager = get_manager()
    if not manager:
        return jsonify({"error": "gstack not available"}), 503
    
    categories = manager.get_categories()
    category_info = {}
    
    for cat in categories:
        cmds = manager.list_commands(cat)
        category_info[cat] = {
            "count": len(cmds),
            "commands": [c.name for c in cmds]
        }
    
    return jsonify({
        "categories": categories,
        "details": category_info
    })


@gstack_bp.route('/help/<command>', methods=['GET'])
def get_help(command):
    """获取指定命令的详细帮助"""
    manager = get_manager()
    if not manager:
        return jsonify({"error": "gstack not available"}), 503
    
    # 确保命令格式正确
    if not command.startswith('/'):
        command = '/' + command
    
    cmd = manager.get_command(command)
    if not cmd:
        return jsonify({
            "error": f"Unknown command: {command}",
            "available": list(manager.COMMANDS.keys())[:10]
        }), 404
    
    skill_content = manager.get_skill_content(command)
    
    return jsonify({
        "command": command,
        "name": cmd.name,
        "description": cmd.description,
        "category": cmd.category,
        "requires_browser": cmd.requires_browser,
        "requires_git": cmd.requires_git,
        "skill_preview": skill_content[:1000] + "..." if skill_content and len(skill_content) > 1000 else skill_content
    })


@gstack_bp.route('/run', methods=['POST'])
def run_command():
    """
    运行gstack命令
    
    Body:
        {
            "command": "/review",
            "context": {"purpose": "code_review"},
            "cwd": "/optional/custom/working/directory"
        }
    
    Returns:
        {
            "success": true,
            "command": "/review",
            "description": "...",
            "skill_content": "..."
        }
    """
    data = request.get_json()
    
    if not data or 'command' not in data:
        return jsonify({"error": "Missing 'command' field"}), 400
    
    command = data['command']
    context = data.get('context', {})
    cwd = data.get('cwd')
    
    manager = get_manager()
    if not manager:
        return jsonify({"error": "gstack not available"}), 503
    
    if not command.startswith('/'):
        command = '/' + command
    
    if command not in manager.COMMANDS:
        return jsonify({
            "error": f"Unknown command: {command}",
            "available": list(manager.COMMANDS.keys())
        }), 404
    
    # 异步运行
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(manager.run_command_async(command, context, cwd))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        loop.close()


@gstack_bp.route('/strategy-flow', methods=['POST'])
def strategy_flow():
    """
    策略开发完整流水线 (gstack sprint)
    
    Body:
        {
            "idea": "我想做一个利用RSI背离的网格交易策略"
        }
    
    Returns:
        {
            "flow": "strategy_development",
            "idea": "...",
            "steps": [...],
            "ready_for_implementation": true
        }
    """
    data = request.get_json()
    
    if not data or 'idea' not in data:
        return jsonify({"error": "Missing 'idea' field"}), 400
    
    idea = data['idea']
    
    bridge = get_bridge()
    if not bridge:
        return jsonify({"error": "gstack not available"}), 503
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(bridge.strategy_development_flow(idea))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        loop.close()


@gstack_bp.route('/review-flow', methods=['POST'])
def review_flow():
    """
    策略代码审查流水线
    
    Body:
        {
            "code": "def my_strategy(): ..."
        }
    
    Returns:
        {
            "flow": "code_review",
            "steps": [...]
        }
    """
    data = request.get_json()
    
    if not data or 'code' not in data:
        return jsonify({"error": "Missing 'code' field"}), 400
    
    code = data['code']
    
    bridge = get_bridge()
    if not bridge:
        return jsonify({"error": "gstack not available"}), 503
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(bridge.code_review_flow(code))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        loop.close()


@gstack_bp.route('/monitor-flow', methods=['POST'])
def monitor_flow():
    """
    交易监控流水线
    
    Returns:
        {
            "flow": "trading_monitoring",
            "steps": [...]
        }
    """
    bridge = get_bridge()
    if not bridge:
        return jsonify({"error": "gstack not available"}), 503
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(bridge.trading_monitoring_flow())
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        loop.close()


@gstack_bp.route('/status', methods=['GET'])
def status():
    """检查gstack集成状态"""
    manager = get_manager()
    
    if not manager:
        return jsonify({
            "gstack_installed": False,
            "error": "gstack_manager import failed",
            "install_instructions": "git clone https://github.com/garrytan/gstack.git ~/.claude/skills/gstack"
        })
    
    is_avail = manager.is_available()
    
    return jsonify({
        "gstack_installed": is_avail,
        "gstack_root": manager.gstack_root if is_avail else None,
        "total_commands": len(manager.COMMANDS) if is_avail else 0,
        "categories": manager.get_categories() if is_avail else [],
        "status": "ready" if is_avail else "not_found"
    })


# === UI Helper: 获取侧边栏数据 ===

@gstack_bp.route('/sidebar', methods=['GET'])
def get_sidebar():
    """
    获取UI侧边栏的gstack命令列表
    
    Returns:
        按分类组织的命令列表，用于UI侧边栏渲染
    """
    manager = get_manager()
    if not manager or not manager.is_available():
        return jsonify({"error": "gstack not available"}), 503
    
    sidebar = {}
    for category in manager.get_categories():
        cmds = manager.list_commands(category)
        sidebar[category] = [
            {
                "name": cmd.name,
                "description": cmd.description,
                "icon": get_category_icon(category)
            }
            for cmd in cmds
        ]
    
    return jsonify({
        "sidebar": sidebar,
        "total_commands": len(manager.COMMANDS)
    })


def get_category_icon(category: str) -> str:
    """获取分类图标"""
    icons = {
        "startup": "🎯",
        "ceo": "👔",
        "eng": "⚙️",
        "design": "🎨",
        "code": "🔍",
        "security": "🛡️",
        "qa": "🧪",
        "deploy": "🚀",
        "monitor": "📊",
        "tools": "🔧",
        "safety": "⚠️"
    }
    return icons.get(category, "📦")
