#!/usr/bin/env python3
"""
🔍 打工机会雷达 + 预测 + 抢单系统 V2
======================================
增强抢单成功率
"""

import json
import random
from datetime import datetime
from typing import Dict, List, Optional

class WorkRadarSystem:
    def __init__(self):
        self.name = "work_radar"
        self.version = "2.0"
        self.scanned_count = 0
        self.sniped_count = 0
        self.success_count = 0
        self.retry_enabled = True
        self.max_retries = 3
        
        self.task_pool = {
            "wool": [
                {"id": "w001", "name": "Solana Saga手机任务", "chain": "Solana", "reward": 150, "duration": 4, "difficulty": "medium", "reliability": 85, "hot_score": 85, "expires_in": 7200},
                {"id": "w002", "name": "Aptos激励测试网", "chain": "Aptos", "reward": 300, "duration": 8, "difficulty": "hard", "reliability": 80, "hot_score": 90, "expires_in": 14400},
                {"id": "w003", "name": "Sui测试网任务", "chain": "Sui", "reward": 200, "duration": 5, "difficulty": "medium", "reliability": 85, "hot_score": 88, "expires_in": 10800},
                {"id": "w004", "name": "Celestia节点", "chain": "Celestia", "reward": 400, "duration": 10, "difficulty": "hard", "reliability": 85, "hot_score": 95, "expires_in": 28800},
                {"id": "w005", "name": "EigenLayer再质押", "chain": "Ethereum", "reward": 200, "duration": 4, "difficulty": "medium", "reliability": 85, "hot_score": 82, "expires_in": 8640},
                {"id": "w006", "name": "Sei Network任务", "chain": "Sei", "reward": 180, "duration": 4, "difficulty": "medium", "reliability": 80, "hot_score": 78, "expires_in": 7200},
                {"id": "w007", "name": "Injective协议", "chain": "Injective", "reward": 160, "duration": 4, "difficulty": "medium", "reliability": 82, "hot_score": 76, "expires_in": 6480},
                {"id": "w008", "name": "dYdX做市任务", "chain": "dYdX", "reward": 280, "duration": 6, "difficulty": "hard", "reliability": 85, "hot_score": 88, "expires_in": 12960},
            ],
            "crowdsource": [
                {"id": "c001", "name": "自动驾驶3D点云标注", "platform": "Scale AI", "reward": 45, "duration": 40, "hourly_rate": 67.5, "reliability": 90, "hot_score": 88, "expires_in": 3600},
                {"id": "c002", "name": "中文语音录制", "platform": "Appen", "reward": 50, "duration": 40, "hourly_rate": 75, "reliability": 88, "hot_score": 85, "expires_in": 3000},
                {"id": "c003", "name": "医学影像标注", "platform": "Labelbox", "reward": 80, "duration": 90, "hourly_rate": 53.3, "reliability": 95, "hot_score": 92, "expires_in": 5400},
                {"id": "c004", "name": "英语语音转写", "platform": "Appen", "reward": 30, "duration": 35, "hourly_rate": 51.4, "reliability": 88, "hot_score": 80, "expires_in": 2100},
                {"id": "c005", "name": "NLP文本标注", "platform": "Scale AI", "reward": 35, "duration": 35, "hourly_rate": 60, "reliability": 88, "hot_score": 82, "expires_in": 2100},
                {"id": "c006", "name": "商品图片分类", "platform": "Toloka", "reward": 15, "duration": 20, "hourly_rate": 45, "reliability": 80, "hot_score": 70, "expires_in": 1200},
            ],
            "hitchhiker": [
                {"id": "h001", "type": "cross_exchange", "name": "BTC跨交易所套利", "pair": "BTC", "exchanges": "Binance→OKX", "spread": 1.46, "confidence": 0.84, "profit": 1.17, "expires_in": 300},
                {"id": "h002", "type": "cross_exchange", "name": "ETH跨交易所套利", "pair": "ETH", "exchanges": "OKX→Bybit", "spread": 1.29, "confidence": 0.80, "profit": 1.03, "expires_in": 300},
                {"id": "h003", "type": "cross_exchange", "name": "SOL跨交易所套利", "pair": "SOL", "exchanges": "Binance→HTX", "spread": 0.91, "confidence": 0.86, "profit": 0.78, "expires_in": 300},
                {"id": "h004", "type": "triangular", "name": "BTC三角套利", "pair": "BTC→ETH→USDT", "spread": 0.65, "confidence": 0.72, "profit": 0.47, "expires_in": 180},
                {"id": "h005", "type": "funding_rate", "name": "SOL资金费率套利", "pair": "SOL-PERP", "rate": 0.15, "annualized": 54.75, "profit": 0.15, "expires_in": 3600},
            ]
        }
    
    def radar_scan(self, category: str = "all") -> Dict:
        self.scanned_count += 1
        opportunities = []
        cats = list(self.task_pool.keys()) if category == "all" else [category]
        
        for cat in cats:
            for task in self.task_pool.get(cat, []):
                priority = self._calc_priority(task)
                task["expires_in"] = max(0, task.get("expires_in", 0) - 300)
                
                opp = {
                    "id": task["id"],
                    "name": task.get("name", task.get("pair", "Unknown")),
                    "category": cat,
                    "priority": priority,
                    "hot_score": task.get("hot_score", 50),
                    "reward": task.get("reward", task.get("profit", 0)),
                    "expires_in": task.get("expires_in", 0),
                    "scanned_at": datetime.now().isoformat(),
                    "predicted_success": self._predict_success(task, cat)
                }
                opportunities.append(opp)
        
        opportunities.sort(key=lambda x: (x["priority"] != "urgent", x["hot_score"]), reverse=True)
        
        return {
            "scan_id": f"scan_{self.scanned_count}",
            "scanned_at": datetime.now().isoformat(),
            "total_found": len(opportunities),
            "opportunities": opportunities[:20],
            "by_category": {cat: len([o for o in opportunities if o["category"] == cat]) for cat in cats}
        }
    
    def _calc_priority(self, task: Dict) -> str:
        hot = task.get("hot_score", 50)
        exp = task.get("expires_in", 99999)
        if exp < 300: return "urgent"
        if hot >= 90: return "high"
        if hot >= 75: return "medium"
        return "low"
    
    def _predict_success(self, task: Dict, cat: str) -> float:
        base = 0.75
        if cat == "wool": return base * task.get("reliability", 80) / 100
        elif cat == "crowdsource": return base * task.get("reliability", 80) / 100 * 1.1
        elif cat == "hitchhiker": return base * task.get("confidence", 0.8)
        return base
    
    def _find_task(self, task_id: str) -> Optional[Dict]:
        for tasks in self.task_pool.values():
            for task in tasks:
                if task["id"] == task_id:
                    return task
        return None
    
    def _get_category(self, task_id: str) -> str:
        return {"w": "wool", "c": "crowdsource", "h": "hitchhiker"}.get(task_id[:1], "unknown")
    
    def predict_and_compare(self, task_ids: List[str]) -> Dict:
        tasks = [self._find_task(tid) for tid in task_ids]
        tasks = [t for t in tasks if t]
        
        predictions = []
        for task in tasks:
            reward = task.get("reward", task.get("profit", 0))
            reliability = task.get("reliability", 80) / 100
            duration = max(task.get("duration", 1), 0.5)
            expected_value = reward * reliability
            hourly_rate = expected_value / duration
            time_value = hourly_rate * (1 + task.get("hot_score", 50) / 100)
            urgency = 1.0 / max(task.get("expires_in", 99999) / 3600, 0.5)
            
            predictions.append({
                "id": task["id"],
                "name": task.get("name", task.get("pair", "Unknown")),
                "category": self._get_category(task["id"]),
                "expected_value": round(expected_value, 2),
                "hourly_rate": round(hourly_rate, 2),
                "time_value": round(time_value, 2),
                "urgency": round(urgency, 4),
                "score": round(expected_value * (1 + urgency), 2),
                "recommendation": "⭐⭐⭐ 强烈推荐" if expected_value >= 200 and hourly_rate >= 50 else "⭐⭐ 推荐" if expected_value >= 100 else "⭐ 可选"
            })
        
        predictions.sort(key=lambda x: x["score"], reverse=True)
        return {"predicted_at": datetime.now().isoformat(), "predictions": predictions, "best_choice": predictions[0] if predictions else None}
    
    def snipe(self, task_id: str, auto_retry: bool = True) -> Dict:
        task = self._find_task(task_id)
        if not task:
            return {"success": False, "error": "Task not found"}
        
        self.sniped_count += 1
        attempts = []
        
        # 尝试抢单 (最多3次)
        for attempt in range(self.max_retries if auto_retry else 1):
            success, result = self._execute_snipe(task, attempt + 1)
            attempts.append({"attempt": attempt + 1, "success": success, "result": result})
            
            if success:
                self.success_count += 1
                return {
                    "success": True,
                    "task_id": task_id,
                    "task_name": task.get("name", task.get("pair", "Unknown")),
                    "reward": task.get("reward", task.get("profit", 0)),
                    "attempts": attempts,
                    "message": f"抢单成功! 获得 ${task.get('reward', task.get('profit', 0))}",
                    "stats": self._get_stats()
                }
            
            # 失败后短暂等待再重试
            if auto_retry and attempt < self.max_retries - 1:
                pass  # 模拟短暂延迟
        
        # 所有尝试都失败
        return {
            "success": False,
            "task_id": task_id,
            "task_name": task.get("name", task.get("pair", "Unknown")),
            "attempts": attempts,
            "error": "抢单失败，已尝试%d次" % len(attempts),
            "alternative": self._find_alternative(task),
            "stats": self._get_stats()
        }
    
    def _execute_snipe(self, task: Dict, attempt: int) -> tuple:
        """执行抢单 - 增强版"""
        hot_score = task.get("hot_score", 80) / 100
        reliability = task.get("reliability", 85) / 100
        confidence = task.get("confidence", 0.8)
        
        # 紧急任务难度增加
        expires = task.get("expires_in", 99999)
        urgency_factor = 1.0
        if expires < 300:
            urgency_factor = 0.6  # 紧急任务成功率降低
        elif expires < 1800:  # 30分钟内
            urgency_factor = 0.8
        elif expires > 3600:  # 1小时以上
            urgency_factor = 1.2  # 更充裕时间，成功率更高
        
        # 尝试次数加成 (越尝试越容易成功)
        attempt_factor = 1.0 + (attempt - 1) * 0.15
        
        # 综合成功率
        if "confidence" in task:  # hitchhiker
            success_prob = confidence * hot_score * attempt_factor
        else:
            success_prob = reliability * hot_score * urgency_factor * attempt_factor
        
        success_prob = min(0.95, success_prob)  # 最高95%
        
        success = random.random() < success_prob
        
        result = {
            "attempt": attempt,
            "success_prob": round(success_prob, 3),
            "success": success
        }
        
        return success, result
    
    def _find_alternative(self, failed_task: Dict) -> Dict:
        cat = self._get_category(failed_task["id"])
        tasks = self.task_pool.get(cat, [])
        alternatives = [t for t in tasks if t["id"] != failed_task["id"]]
        alternatives.sort(key=lambda x: x.get("hot_score", 50), reverse=True)
        
        if alternatives:
            alt = alternatives[0]
            return {
                "id": alt["id"],
                "name": alt.get("name", alt.get("pair", "Unknown")),
                "reward": alt.get("reward", alt.get("profit", 0)),
                "hot_score": alt.get("hot_score", 50),
                "snipe_recommendation": "推荐抢这个替代任务"
            }
        return {"message": "暂无替代任务"}
    
    def snipe_batch(self, task_ids: List[str], priority_order: bool = True) -> Dict:
        """批量抢单 - 智能排序"""
        if priority_order:
            # 按优先级排序
            tasks = []
            for tid in task_ids:
                t = self._find_task(tid)
                if t:
                    t["_sort_key"] = t.get("hot_score", 50) * (1 + t.get("expires_in", 99999) / 10000)
                    tasks.append(t)
            tasks.sort(key=lambda x: x["_sort_key"], reverse=True)
            task_ids = [t["id"] for t in tasks]
        
        results = []
        success_count = 0
        
        for task_id in task_ids:
            result = self.snipe(task_id)
            results.append({
                "task_id": task_id,
                "success": result["success"],
                "message": result.get("message", result.get("error", ""))
            })
            if result["success"]:
                success_count += 1
                break  # 成功后停止
        
        return {
            "total": len(task_ids),
            "success": success_count,
            "failed": len(task_ids) - success_count,
            "results": results,
            "stats": self._get_stats()
        }
    
    def _get_stats(self) -> Dict:
        rate = self.success_count / max(self.sniped_count, 1) * 100
        return {
            "total_sniped": self.sniped_count,
            "success_count": self.success_count,
            "failed_count": self.sniped_count - self.success_count,
            "success_rate": round(rate, 1)
        }
    
    def get_status(self) -> Dict:
        return {
            "name": self.name,
            "version": self.version,
            "scanned_count": self.scanned_count,
            "stats": self._get_stats()
        }

_radar = None
def get_work_radar():
    global _radar
    if _radar is None:
        _radar = WorkRadarSystem()
    return _radar
