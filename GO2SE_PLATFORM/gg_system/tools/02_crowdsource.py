#!/usr/bin/env python3
"""
💼 穷孩子 - 众包打工工具
版本: v1.0
日期: 2026-05-03

决策等式:
D_crowd = α(Reward) + β(Speed) + γ(Skill) - δ(Complexity)

参数:
α = 0.40 (报酬权重)
β = 0.30 (速度权重)
γ = 0.20 (技能匹配)
δ = 0.10 (复杂程度)
"""

class CrowdsourceTool:
    def __init__(self):
        self.name = "穷孩子"
        self.type = "crowdsource"
        self.params = {
            "alpha": 0.40,
            "beta": 0.30,
            "gamma": 0.20,
            "delta": 0.10
        }
        self.thresholds = {
            "strong": 0.6,
            "medium": 0.4,
            "weak": 0.2
        }
        
    def calculate(self, task_data):
        """
        计算任务分数
        
        task_data = {
            "reward": 50,          # 报酬 ($)
            "time_hours": 2,        # 完成时间
            "skill_match": 0.8,    # 技能匹配 (0-1)
            "complexity": 0.3,     # 复杂程度 (0-1)
            "client_rating": 4.8     # 客户评分
        }
        """
        # 报酬分数
        reward_score = min(task_data.get("reward", 0) / 100, 1.0)
        
        # 速度分数
        time_hours = task_data.get("time_hours", 10)
        speed_score = 1.0 - min(time_hours / 10, 1.0)
        
        # 技能匹配
        skill_score = task_data.get("skill_match", 0.5)
        
        # 复杂度
        complexity_score = 1.0 - task_data.get("complexity", 0.5)
        
        D = (self.params["alpha"] * reward_score +
             self.params["beta"] * speed_score +
             self.params["gamma"] * skill_score -
             self.params["delta"] * complexity_score)
        
        return {
            "score": D,
            "signal": self.get_signal(D),
            "action": self.get_action(D),
            "priority": self.get_priority(D)
        }
    
    def get_signal(self, D):
        if D > self.thresholds["strong"]:
            return "🟢立即接单"
        elif D > self.thresholds["medium"]:
            return "🟡优先接单"
        elif D > self.thresholds["weak"]:
            return "🟠普通接单"
        else:
            return "🔴放弃"
    
    def get_action(self, D):
        if D > self.thresholds["strong"]:
            return "立即接单"
        elif D > self.thresholds["medium"]:
            return "优先接单"
        elif D > self.thresholds["weak"]:
            return "普通接单"
        else:
            return "放弃"
    
    def get_priority(self, D):
        if D > self.thresholds["strong"]:
            return 1
        elif D > self.thresholds["medium"]:
            return 2
        elif D > self.thresholds["weak"]:
            return 3
        else:
            return 99
    
    def exit_strategy(self, task_status):
        """
        退出策略
        """
        if task_status.get("completed"):
            return {"action": "收款", "reason": "任务完成"}
        elif task_status.get("rejected"):
            return {"action": "申诉", "reason": "被拒绝"}
        elif task_status.get("time_spent", 0) > task_status.get("time_estimate", 1) * 2:
            return {"action": "放弃", "reason": "超时"}
        else:
            return {"action": "继续", "reason": "正常进行"}

# 示例任务数据
sample_tasks = [
    {"name": "翻译文章", "reward": 30, "time_hours": 1, "skill_match": 0.9, "complexity": 0.2},
    {"name": "数据标注", "reward": 50, "time_hours": 3, "skill_match": 0.7, "complexity": 0.3},
    {"name": "代码测试", "reward": 100, "time_hours": 5, "skill_match": 0.6, "complexity": 0.6},
]

if __name__ == "__main__":
    tool = CrowdsourceTool()
    
    print("=" * 60)
    print("💼 穷孩子 - 众包打工工具")
    print("=" * 60)
    
    for task in sample_tasks:
        result = tool.calculate(task)
        print(f"\n{task['name']}:")
        print(f"  报酬: ${task['reward']}")
        print(f"  时间: {task['time_hours']}h")
        print(f"  分数: {result['score']:.3f}")
        print(f"  信号: {result['signal']}")
        print(f"  优先级: {result['priority']}")
