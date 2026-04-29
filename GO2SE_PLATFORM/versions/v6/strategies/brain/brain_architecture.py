#!/usr/bin/env python3
"""
🧠 左右脑 + OpenClaw/Hermes 自主切换系统 v2.0
================================================
左脑(逻辑) + 右脑(直觉) + OpenClaw(执行) + Hermes(反思)
互为备份 + 自主迭代
"""

import json
import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum

class BrainMode(str, Enum):
    LEFT = "left"      # 逻辑/分析
    RIGHT = "right"    # 直觉/创意
    HYBRID = "hybrid"  # 混合模式
    OPENCLAW = "openclaw"  # OpenClaw执行模式
    HERMES = "hermes"      # Hermes反思模式

class TrustLevel(float, Enum):
    VERY_LOW = 0.3
    LOW = 0.5
    MEDIUM = 0.7
    HIGH = 0.85
    VERY_HIGH = 0.95

# ═══════════════════════════════════════════════════════════════════════
# 🧠 左右脑核心
# ═══════════════════════════════════════════════════════════════════════

class BrainHemisphere:
    """脑半球"""
    
    def __init__(self, hemisphere_type: str):
        self.type = hemisphere_type  # "left" or "right"
        self.trust_score = 0.7
        self.decision_history = []
        self.success_count = 0
        self.fail_count = 0
        
        # 左右脑特质
        if hemisphere_type == "left":
            self.name = "左脑 (逻辑)"
            self.traits = {
                "style": "analytical",
                "risk_tolerance": 0.6,
                "time_horizon": "medium",
                "preferred_signals": ["momentum", "trend", "rsi"],
                "strengths": ["pattern_recognition", "statistics", "backtesting"],
                "weaknesses": ["emotion_reading", "black_swan"]
            }
        else:  # right
            self.name = "右脑 (直觉)"
            self.traits = {
                "style": "intuitive",
                "risk_tolerance": 0.8,
                "time_horizon": "short",
                "preferred_signals": ["contrarian", "sentiment", "anomaly"],
                "strengths": ["regime_detection", "mean_reversion", "event_driven"],
                "weaknesses": ["sustainable_trends", "fundamental"]
            }
    
    def calculate_trust(self, lookback: int = 20) -> float:
        """计算信任度"""
        recent = self.decision_history[-lookback:] if self.decision_history else []
        if not recent:
            return 0.7
        
        successes = sum(1 for d in recent if d.get("outcome") == "success")
        total = len(recent)
        
        # 基础成功率
        success_rate = successes / total
        
        # 考虑连续成功/失败
        consecutive = 0
        for d in reversed(recent):
            if d.get("outcome") == "success":
                consecutive += 1
            else:
                break
        
        # 信任度 = 成功率×0.7 + 连续性×0.3
        self.trust_score = success_rate * 0.7 + min(consecutive / 5, 1.0) * 0.3
        return self.trust_score
    
    def decide(self, market_data: Dict) -> Dict:
        """做出决策"""
        mi = market_data.get("mi", 0.65)
        price = market_data.get("price", 50000)
        change_24h = market_data.get("change_24h", 0)
        rsi = market_data.get("rsi", 50)
        volume_ratio = market_data.get("volume_ratio", 1.0)
        
        if self.type == "left":
            # 左脑: 趋势跟随, 等待确认
            decision = self._left_brain_decide(mi, price, change_24h, rsi, volume_ratio)
        else:
            # 右脑: 反向操作, 快速反应
            decision = self._right_brain_decide(mi, price, change_24h, rsi, volume_ratio)
        
        # 记录决策
        self.decision_history.append({
            "timestamp": datetime.now().isoformat(),
            "price": price,
            "mi": mi,
            "decision": decision,
            "trust": self.trust_score
        })
        
        return {
            "hemisphere": self.type,
            "name": self.name,
            "decision": decision,
            "trust_score": self.trust_score,
            "confidence": decision.get("confidence", 0.5)
        }
    
    def _left_brain_decide(self, mi, price, change_24h, rsi, volume_ratio) -> Dict:
        """左脑决策 - 逻辑分析"""
        # 趋势确认后才行动
        if change_24h > 2 and rsi < 70:
            return {"action": "LONG", "leverage": 2.0, "position": 0.6, "confidence": 0.75}
        elif change_24h < -2 and rsi > 30:
            return {"action": "SHORT", "leverage": 2.0, "position": 0.6, "confidence": 0.75}
        elif rsi < 30:
            return {"action": "BUY_DIP", "leverage": 1.5, "position": 0.4, "confidence": 0.65}
        elif rsi > 70:
            return {"action": "SELL_RALLY", "leverage": 1.5, "position": 0.4, "confidence": 0.65}
        else:
            return {"action": "HOLD", "leverage": 1.0, "position": 0.0, "confidence": 0.5}
    
    def _right_brain_decide(self, mi, price, change_24h, rsi, volume_ratio) -> Dict:
        """右脑决策 - 直觉反身"""
        # 越涨越卖, 越跌越买
        if change_24h > 3 and rsi > 65:
            return {"action": "SHORT", "leverage": 2.5, "position": 0.5, "confidence": 0.7}
        elif change_24h < -3 and rsi < 35:
            return {"action": "LONG", "leverage": 2.5, "position": 0.5, "confidence": 0.7}
        elif change_24h > 5:
            # 极端上涨, 短期反转
            return {"action": "SHORT", "leverage": 1.5, "position": 0.3, "confidence": 0.6}
        elif change_24h < -5:
            # 极端下跌, 抄底
            return {"action": "LONG", "leverage": 1.5, "position": 0.3, "confidence": 0.6}
        else:
            return {"action": "HOLD", "leverage": 1.0, "position": 0.0, "confidence": 0.5}
    
    def record_outcome(self, decision: Dict, outcome: str):
        """记录决策结果"""
        if self.decision_history:
            self.decision_history[-1]["outcome"] = outcome
            if outcome == "success":
                self.success_count += 1
            else:
                self.fail_count += 1
            self.calculate_trust()
    
    def to_dict(self):
        return {
            "type": self.type,
            "name": self.name,
            "trust_score": round(self.trust_score, 3),
            "total_decisions": len(self.decision_history),
            "success_rate": round(self.success_count / max(1, self.success_count + self.fail_count), 3),
            "traits": self.traits
        }


# ═══════════════════════════════════════════════════════════════════════
# 🤖 OpenClaw/Hermes 双主体
# ═══════════════════════════════════════════════════════════════════════

class AgentCore:
    """OpenClaw/Hermes 核心"""
    
    def __init__(self, agent_type: str):
        self.type = agent_type  # "openclaw" or "hermes"
        self.status = "active"
        self.health = 1.0
        self.heartbeat = datetime.now()
        self.task_queue = []
        self.completed_tasks = []
        self.failed_tasks = []
        self.last_iteration = datetime.now()
        self.iteration_count = 0
        
        if agent_type == "openclaw":
            self.name = "OpenClaw (执行者)"
            self.role = "execution"
            self.capabilities = ["task_execution", "skill_management", "external_actions", "messaging", "file_operations"]
            self.focus = "immediate_action"
        else:  # hermes
            self.name = "Hermes (反思者)"
            self.role = "introspection"
            self.capabilities = ["memory_management", "learning", "pattern_recognition", "self_improvement", "strategy_refinement"]
            self.focus = "long_term_optimization"
    
    def is_alive(self) -> bool:
        """检查是否存活"""
        return self.status == "active" and (datetime.now() - self.heartbeat).seconds < 300
    
    def heartbeat_pulse(self):
        """心跳"""
        self.heartbeat = datetime.now()
        self.health = min(1.0, self.health + 0.01)
    
    def assign_task(self, task: Dict) -> bool:
        """分配任务"""
        if not self.is_alive():
            return False
        self.task_queue.append({**task, "assigned_at": datetime.now().isoformat()})
        return True
    
    def complete_task(self, task_id: str, result: Dict):
        """完成任务"""
        self.task_queue = [t for t in self.task_queue if t.get("id") != task_id]
        self.completed_tasks.append({**result, "completed_at": datetime.now().isoformat()})
        self.heartbeat_pulse()
    
    def fail_task(self, task_id: str, error: str):
        """任务失败"""
        self.task_queue = [t for t in self.task_queue if t.get("id") != task_id]
        self.failed_tasks.append({"task_id": task_id, "error": error, "failed_at": datetime.now().isoformat()})
        self.health = max(0.5, self.health - 0.1)
    
    def iterate(self, reflection_data: Dict = None):
        """自主迭代"""
        self.iteration_count += 1
        self.last_iteration = datetime.now()
        
        if self.type == "hermes" and reflection_data:
            # Hermes反思迭代
            return self._hermes_iterate(reflection_data)
        elif self.type == "openclaw":
            # OpenClaw执行迭代
            return self._openclaw_iterate()
        
        return {"iteration": self.iteration_count, "status": "ok"}
    
    def _hermes_iterate(self, reflection: Dict) -> Dict:
        """Hermes反思迭代"""
        improvements = []
        
        # 从失败中学习
        if self.failed_tasks:
            recent_failures = self.failed_tasks[-5:]
            for failure in recent_failures:
                improvements.append({
                    "type": "learned_from_failure",
                    "task": failure.get("task_id"),
                    "error": failure.get("error")
                })
        
        # 从成功中提炼模式
        if self.completed_tasks:
            recent_successes = self.completed_tasks[-10:]
            success_patterns = self._extract_patterns(recent_successes)
            if success_patterns:
                improvements.append({
                    "type": "pattern_learned",
                    "patterns": success_patterns
                })
        
        return {
            "iteration": self.iteration_count,
            "improvements": improvements,
            "health": self.health,
            "total_completed": len(self.completed_tasks),
            "total_failed": len(self.failed_tasks)
        }
    
    def _openclaw_iterate(self) -> Dict:
        """OpenClaw执行迭代"""
        # 优化任务队列
        optimized = []
        for task in self.task_queue:
            if task.get("priority", 5) > 3:
                optimized.append(task)
        
        self.task_queue = optimized
        
        return {
            "iteration": self.iteration_count,
            "queue_size": len(self.task_queue),
            "health": self.health
        }
    
    def _extract_patterns(self, tasks: List[Dict]) -> List[str]:
        """提取成功模式"""
        patterns = []
        if not tasks:
            return patterns
        
        # 简单模式检测
        fast_tasks = [t for t in tasks if t.get("duration", 999) < 10]
        if len(fast_tasks) / len(tasks) > 0.7:
            patterns.append("fast_execution")
        
        return patterns
    
    def to_dict(self):
        return {
            "type": self.type,
            "name": self.name,
            "role": self.role,
            "status": self.status,
            "health": round(self.health, 3),
            "is_alive": self.is_alive(),
            "queue_size": len(self.task_queue),
            "completed": len(self.completed_tasks),
            "failed": len(self.failed_tasks),
            "iteration": self.iteration_count,
            "last_iteration": self.last_iteration.isoformat(),
            "capabilities": self.capabilities,
            "focus": self.focus
        }


# ═══════════════════════════════════════════════════════════════════════
# 🔄 自主切换引擎
# ═══════════════════════════════════════════════════════════════════════

class AutonomousSwitchEngine:
    """自主切换引擎"""
    
    def __init__(self):
        # 左右脑
        self.left_brain = BrainHemisphere("left")
        self.right_brain = BrainHemisphere("right")
        
        # OpenClaw/Hermes
        self.openclaw = AgentCore("openclaw")
        self.hermes = AgentCore("hermes")
        
        # 当前状态
        self.current_brain_mode = BrainMode.HYBRID
        self.current_agent_mode = "openclaw"
        self.last_switch = datetime.now()
        self.switch_count = {"brain": 0, "agent": 0}
        
        # 切换阈值
        self.brain_switch_thresholds = {
            "trust_diff": 0.2,      # 信任度差异触发切换
            "performance_window": 20,
            "cooldown_seconds": 300
        }
        
        self.agent_switch_thresholds = {
            "health_diff": 0.3,     # 健康度差异
            "task_complexity": 7,   # 任务复杂度阈值
            "cooldown_seconds": 180
        }
        
        # 互为备份状态
        self.backup_state = {
            "openclaw_backup_hermes": False,
            "hermes_backup_openclaw": False,
            "last_backup_check": datetime.now()
        }
    
    # ─── 左右脑切换 ───
    
    def switch_brain(self, force: str = None) -> Dict:
        """切换脑半球"""
        now = datetime.now()
        
        # 冷却期检查
        if (now - self.last_switch).seconds < self.brain_switch_thresholds["cooldown_seconds"]:
            return {"switched": False, "reason": "cooldown", "current": self.current_brain_mode.value}
        
        left_trust = self.left_brain.calculate_trust(self.brain_switch_thresholds["performance_window"])
        right_trust = self.right_brain.calculate_trust(self.brain_switch_thresholds["performance_window"])
        
        # 强制切换
        if force == "left":
            self.current_brain_mode = BrainMode.LEFT
        elif force == "right":
            self.current_brain_mode = BrainMode.RIGHT
        else:
            # 自主切换逻辑
            diff = abs(left_trust - right_trust)
            
            if diff > self.brain_switch_thresholds["trust_diff"]:
                # 信任度差异大, 切换到高信任度
                if left_trust > right_trust:
                    self.current_brain_mode = BrainMode.LEFT
                else:
                    self.current_brain_mode = BrainMode.RIGHT
            else:
                # 信任度接近, 使用混合模式
                self.current_brain_mode = BrainMode.HYBRID
        
        self.last_switch = now
        self.switch_count["brain"] += 1
        
        return {
            "switched": True,
            "from": self.current_brain_mode.value,
            "to": self.current_brain_mode.value,
            "left_trust": round(left_trust, 3),
            "right_trust": round(right_trust, 3),
            "switch_count": self.switch_count["brain"]
        }
    
    def decide_with_brain(self, market_data: Dict) -> Dict:
        """用当前脑半球决策"""
        left_result = self.left_brain.decide(market_data)
        right_result = self.right_brain.decide(market_data)
        
        if self.current_brain_mode == BrainMode.LEFT:
            primary = left_result
            secondary = right_result
        elif self.current_brain_mode == BrainMode.RIGHT:
            primary = right_result
            secondary = left_result
        else:  # HYBRID
            primary = self._hybrid_decide(left_result, right_result)
            primary["hemisphere"] = "hybrid"
        
        return {
            "mode": self.current_brain_mode.value,
            "left_brain": left_result,
            "right_brain": right_result,
            "decision": primary,
            "left_trust": round(self.left_brain.trust_score, 3),
            "right_trust": round(self.right_brain.trust_score, 3),
            "switch_count": self.switch_count["brain"]
        }
    
    def _hybrid_decide(self, left: Dict, right: Dict) -> Dict:
        """混合决策"""
        # 置信度加权平均
        left_weight = self.left_brain.trust_score
        right_weight = self.right_brain.trust_score
        total = left_weight + right_weight
        
        left_action = left.get("decision", {})
        right_action = right.get("decision", {})
        
        # 仓位融合
        position = (left_action.get("position", 0) * left_weight + right_action.get("position", 0) * right_weight) / total
        
        # 杠杆融合
        leverage = (left_action.get("leverage", 1) * left_weight + right_action.get("leverage", 1) * right_weight) / total
        
        # 行动融合 (优先高置信度)
        if left.get("confidence", 0) > right.get("confidence", 0):
            action = left_action.get("action", "HOLD")
        else:
            action = right_action.get("action", "HOLD")
        
        return {
            "action": action,
            "leverage": round(leverage, 2),
            "position": round(position, 2),
            "confidence": round((left.get("confidence", 0) + right.get("confidence", 0)) / 2, 3)
        }
    
    # ─── Agent切换 (OpenClaw/Hermes) ───
    
    def switch_agent(self, force: str = None) -> Dict:
        """切换Agent"""
        now = datetime.now()
        
        # 冷却期检查
        if (now - self.last_switch).seconds < self.agent_switch_thresholds["cooldown_seconds"]:
            return {"switched": False, "reason": "cooldown"}
        
        old_agent = self.current_agent_mode
        
        # 强制切换
        if force in ["openclaw", "hermes"]:
            self.current_agent_mode = force
        else:
            # 健康度检查
            if not self.openclaw.is_alive() and not self.hermes.is_alive():
                # 都挂了, 尝试恢复Hermes作为备份
                self.current_agent_mode = "hermes"
                self.backup_state["hermes_backup_openclaw"] = True
            elif not self.hermes.is_alive():
                self.current_agent_mode = "openclaw"
                self.backup_state["openclaw_backup_hermes"] = True
            elif self.openclaw.health < self.agent_switch_thresholds["health_diff"]:
                # OpenClaw不健康, Hermes接管
                self.current_agent_mode = "hermes"
            elif self.hermes.health < self.agent_switch_thresholds["health_diff"]:
                # Hermes不健康, OpenClaw接管
                self.current_agent_mode = "openclaw"
            else:
                # 正常状态, 保持当前
                pass
        
        self.last_switch = now
        self.switch_count["agent"] += 1
        
        return {
            "switched": old_agent != self.current_agent_mode,
            "from": old_agent,
            "to": self.current_agent_mode,
            "openclaw_health": round(self.openclaw.health, 3),
            "hermes_health": round(self.hermes.health, 3),
            "switch_count": self.switch_count["agent"]
        }
    
    def execute_task(self, task: Dict) -> Dict:
        """执行任务 (带备份)"""
        task_id = task.get("id", "task_" + str(random.randint(1000, 9999)))
        task["id"] = task_id
        
        # 确定执行Agent
        if self.current_agent_mode == "openclaw":
            executor = self.openclaw
            backup = self.hermes
        else:
            executor = self.hermes
            backup = self.openclaw
        
        # 尝试执行
        if executor.assign_task(task):
            try:
                # 模拟任务执行
                result = self._execute_task_internal(task)
                executor.complete_task(task_id, result)
                
                # 通知Hermes反思
                if self.hermes.is_alive():
                    self.hermes.assign_task({
                        "id": f"reflect_{task_id}",
                        "type": "reflection",
                        "source_task": task,
                        "result": result
                    })
                
                return {"success": True, "executor": executor.type, "result": result}
            except Exception as e:
                executor.fail_task(task_id, str(e))
                # 备份接管
                if backup.is_alive():
                    return self._execute_with_backup(task, backup)
                return {"success": False, "error": str(e)}
        else:
            # 执行器不健康, 备份接管
            return self._execute_with_backup(task, backup)
    
    def _execute_task_internal(self, task: Dict) -> Dict:
        """内部任务执行"""
        # 模拟执行
        import time
        time.sleep(0.1)
        return {"status": "completed", "output": f"Task {task.get('id')} done"}
    
    def _execute_with_backup(self, task: Dict, backup: AgentCore) -> Dict:
        """备份执行"""
        if backup.assign_task(task):
            try:
                result = self._execute_task_internal(task)
                backup.complete_task(task.get("id"), result)
                return {"success": True, "executor": backup.type, "result": result, "backup_used": True}
            except Exception as e:
                backup.fail_task(task.get("id"), str(e))
                return {"success": False, "error": str(e), "backup_failed": True}
        return {"success": False, "error": "No available executor"}
    
    # ─── 自主迭代 ───
    
    def self_improve(self) -> Dict:
        """自主迭代"""
        # 1. Hermes反思
        reflection = {
            "left_brain_performance": self.left_brain.decision_history[-20:],
            "right_brain_performance": self.right_brain.decision_history[-20:],
            "openclaw_tasks": self.openclaw.completed_tasks[-10:],
            "hermes_tasks": self.hermes.completed_tasks[-10:],
            "switch_count": self.switch_count
        }
        
        hermes_result = self.hermes.iterate(reflection)
        
        # 2. 调整策略
        adjustments = []
        
        # 如果左脑成功率下降, 降低权重
        left_trust = self.left_brain.calculate_trust()
        if left_trust < 0.5:
            adjustments.append({"type": "left_brain_degraded", "trust": left_trust})
        
        # 如果右脑表现好, 增加使用
        right_trust = self.right_brain.calculate_trust()
        if right_trust > 0.7:
            adjustments.append({"type": "right_brain_promoted", "trust": right_trust})
        
        # 3. 检查备份状态
        backup_check = self._check_backup_status()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "hermes_iteration": hermes_result,
            "adjustments": adjustments,
            "backup_status": backup_check,
            "recommendations": self._generate_recommendations()
        }
    
    def _check_backup_status(self) -> Dict:
        """检查备份状态"""
        return {
            "openclaw_alive": self.openclaw.is_alive(),
            "hermes_alive": self.hermes.is_alive(),
            "mutual_backup": self.backup_state,
            "total_switches": self.switch_count
        }
    
    def _generate_recommendations(self) -> List[str]:
        """生成建议"""
        recs = []
        
        left_trust = self.left_brain.trust_score
        right_trust = self.right_brain.trust_score
        
        if left_trust < 0.4:
            recs.append("左脑信任度过低, 建议切换到右脑模式")
        if right_trust < 0.4:
            recs.append("右脑信任度过低, 建议切换到左脑模式")
        if abs(left_trust - right_trust) < 0.1:
            recs.append("左右脑信任度接近, 建议使用混合模式")
        
        if self.openclaw.health < 0.6:
            recs.append("OpenClaw健康度低, 建议Hermes接管")
        if self.hermes.health < 0.6:
            recs.append("Hermes健康度低, 建议OpenClaw接管")
        
        return recs
    
    # ─── 状态导出 ───
    
    def get_status(self) -> Dict:
        """获取完整状态"""
        return {
            "brain_mode": self.current_brain_mode.value,
            "agent_mode": self.current_agent_mode,
            "left_brain": self.left_brain.to_dict(),
            "right_brain": self.right_brain.to_dict(),
            "openclaw": self.openclaw.to_dict(),
            "hermes": self.hermes.to_dict(),
            "switch_count": self.switch_count,
            "backup_status": self.backup_state,
            "last_switch": self.last_switch.isoformat()
        }


# ═══════════════════════════════════════════════════════════════════════
# 全局实例
# ═══════════════════════════════════════════════════════════════════════

brain_engine = AutonomousSwitchEngine()


# ═══════════════════════════════════════════════════════════════════════
# API 端点
# ═══════════════════════════════════════════════════════════════════════

def get_brain_engine():
    return brain_engine

def decide_brain(market_data: Dict) -> Dict:
    """脑半球决策"""
    return brain_engine.decide_with_brain(market_data)

def switch_brain(mode: str = None) -> Dict:
    """切换脑半球"""
    return brain_engine.switch_brain(mode)

def switch_agent(agent: str = None) -> Dict:
    """切换Agent"""
    return brain_engine.switch_agent(agent)

def get_status() -> Dict:
    """获取状态"""
    return brain_engine.get_status()

def self_improve() -> Dict:
    """自主迭代"""
    return brain_engine.self_improve()
