#!/usr/bin/env python3
"""
🪿 GO2SE CEO 自主迭代管理器 V1
"""

import json
import time
import subprocess
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-8s | %(message)s')
logger = logging.getLogger("ceo_auto_iteration")


class CEOIterationConfig:
    """CEO迭代配置"""
    SIMULATION_MIN_SCORE = 80.0
    STRATEGY_MIN_SCORE = 70.0
    POSITION_MIN_SCORE = 60.0
    MIN_ITERATION_INTERVAL = 3600
    MAX_DAILY_ITERATIONS = 4
    PLATFORM_DIR = Path("/root/.openclaw/workspace/GO2SE_PLATFORM")
    REPORT_DIR = PLATFORM_DIR / "reports"
    ITERATION_HISTORY = PLATFORM_DIR / "ceo_iteration_history.json"
    THRESHOLDS = {
        "simulation_score": SIMULATION_MIN_SCORE,
        "strategy_score": STRATEGY_MIN_SCORE,
        "position_score": POSITION_MIN_SCORE,
        "layer_C_score": 70.0,
        "layer_A_score": 75.0,
    }


@dataclass
class IterationRecommendation:
    category: str
    dimension: str
    current_score: float
    threshold: float
    action: str
    priority: int
    reason: str


@dataclass
class IterationResult:
    iteration_id: str
    timestamp: str
    triggered_by: str
    actions_taken: List[str]
    scores_before: Dict[str, float]
    scores_after: Dict[str, float]
    improvement: float
    status: str


class CEOAutoIterationManager:
    def __init__(self, config: CEOIterationConfig = None):
        self.config = config or CEOIterationConfig()
        self.recommendations: List[IterationRecommendation] = []
        self.iteration_history = self._load_iteration_history()
    
    def _load_iteration_history(self) -> List[Dict]:
        if self.config.ITERATION_HISTORY.exists():
            try:
                with open(self.config.ITERATION_HISTORY) as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def _save_iteration_history(self):
        self.config.ITERATION_HISTORY.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config.ITERATION_HISTORY, 'w') as f:
            json.dump(self.iteration_history[-100:], f, indent=2)
    
    def check_simulation_score(self) -> Tuple[float, str]:
        try:
            report_path = self.config.PLATFORM_DIR / "beidou_simulation_report.json"
            if report_path.exists():
                with open(report_path) as f:
                    data = json.load(f)
                return data.get('overall_score', 0), data.get('timestamp', '')
        except Exception as e:
            logger.error(f"读取仿真报告失败: {e}")
        return 0.0, ""
    
    def check_strategy_distillation(self) -> Tuple[float, Dict]:
        try:
            report_path = self.config.PLATFORM_DIR / "strategy_distillation_results.json"
            if report_path.exists():
                with open(report_path) as f:
                    data = json.load(f)
                avg_score = data.get('summary', {}).get('average_score', 0)
                strategies = data.get('strategies', [])
                return avg_score, {"count": len(strategies)}
        except Exception as e:
            logger.error(f"读取策略蒸馏报告失败: {e}")
        return 0.0, {}
    
    def check_dynamic_weights(self) -> Tuple[float, Dict]:
        try:
            plan_path = self.config.PLATFORM_DIR / "dynamic_weights_plan.json"
            if plan_path.exists():
                with open(plan_path) as f:
                    data = json.load(f)
                pending_actions = len(data.get('proposed_actions', []))
                score = max(0, 100 - pending_actions * 10)
                return score, {"pending_actions": pending_actions}
        except Exception as e:
            logger.error(f"读取仓位计划失败: {e}")
        return 0.0, {}
    
    def check_layer_scores(self) -> Dict[str, float]:
        try:
            report_path = self.config.PLATFORM_DIR / "beidou_simulation_report.json"
            if report_path.exists():
                with open(report_path) as f:
                    data = json.load(f)
                layers = data.get('layers', {})
                return {k: v.get('score', 0) for k, v in layers.items()}
        except:
            pass
        return {}
    
    def generate_recommendations(self) -> List[IterationRecommendation]:
        recommendations = []
        
        sim_score, _ = self.check_simulation_score()
        if sim_score < self.config.SIMULATION_MIN_SCORE:
            recommendations.append(IterationRecommendation(
                category="simulation",
                dimension="overall",
                current_score=sim_score,
                threshold=self.config.SIMULATION_MIN_SCORE,
                action="run_full_simulation",
                priority=1 if sim_score < 70 else 3,
                reason=f"仿真评分 {sim_score:.1f} 低于阈值 {self.config.SIMULATION_MIN_SCORE}"
            ))
        
        strat_score, _ = self.check_strategy_distillation()
        if strat_score < self.config.STRATEGY_MIN_SCORE:
            recommendations.append(IterationRecommendation(
                category="strategy",
                dimension="distillation",
                current_score=strat_score,
                threshold=self.config.STRATEGY_MIN_SCORE,
                action="apply_optimal_params",
                priority=2,
                reason=f"策略评分 {strat_score:.1f} 低于阈值 {self.config.STRATEGY_MIN_SCORE}"
            ))
        
        pos_score, pos_info = self.check_dynamic_weights()
        if pos_score < self.config.POSITION_MIN_SCORE:
            recommendations.append(IterationRecommendation(
                category="position",
                dimension="allocation",
                current_score=pos_score,
                threshold=self.config.POSITION_MIN_SCORE,
                action="execute_rebalance",
                priority=2,
                reason=f"仓位需要调整，待执行动作: {pos_info.get('pending_actions', 0)}"
            ))
        
        layer_scores = self.check_layer_scores()
        for layer, score in layer_scores.items():
            threshold_key = f"layer_{layer}_score"
            if threshold_key in self.config.THRESHOLDS:
                threshold = self.config.THRESHOLDS[threshold_key]
                if score < threshold:
                    recommendations.append(IterationRecommendation(
                        category="layer",
                        dimension=f"layer_{layer}",
                        current_score=score,
                        threshold=threshold,
                        action=f"optimize_layer_{layer}",
                        priority=3 if score > 60 else 2,
                        reason=f"{layer}层评分 {score:.1f} 低于阈值 {threshold}"
                    ))
        
        recommendations.sort(key=lambda x: x.priority)
        self.recommendations = recommendations
        return recommendations
    
    def should_trigger_iteration(self) -> Tuple[bool, str]:
        if self.iteration_history:
            last_iteration = self.iteration_history[-1]
            last_time = datetime.fromisoformat(last_iteration['timestamp'])
            elapsed = (datetime.now() - last_time).total_seconds()
            if elapsed < self.config.MIN_ITERATION_INTERVAL:
                return False, f"距离上次迭代仅 {elapsed/60:.0f}分钟"
        
        today = datetime.now().date()
        today_iterations = [
            h for h in self.iteration_history
            if datetime.fromisoformat(h['timestamp']).date() == today
        ]
        if len(today_iterations) >= self.config.MAX_DAILY_ITERATIONS:
            return False, f"今日迭代次数已达上限 ({self.config.MAX_DAILY_ITERATIONS})"
        
        recs = self.generate_recommendations()
        if not recs:
            return False, "无迭代建议"
        
        top_rec = recs[0]
        if top_rec.priority <= 2:
            return True, f"高优先级建议: {top_rec.reason}"
        
        return False, f"建议优先级 {top_rec.priority}"
    
    def trigger_iteration(self, force: bool = False) -> Optional[IterationResult]:
        should_trigger, reason = self.should_trigger_iteration()
        
        if not should_trigger and not force:
            logger.info(f"不触发迭代: {reason}")
            return None
        
        logger.info(f"触发迭代: {reason}")
        
        scores_before = {
            "simulation": self.check_simulation_score()[0],
            "strategy": self.check_strategy_distillation()[0],
            "position": self.check_dynamic_weights()[0],
        }
        scores_before.update(self.check_layer_scores())
        
        iteration_id = f"iter_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        actions_taken = []
        
        try:
            logger.info("执行迭代脚本...")
            result = subprocess.run(
                ["bash", str(self.config.PLATFORM_DIR / "scripts" / "go2se_v7_iteration.sh")],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                actions_taken.append("v7_iteration_completed")
                logger.info("迭代脚本执行成功")
            else:
                actions_taken.append("v7_iteration_failed")
                logger.error(f"迭代脚本执行失败")
            
            time.sleep(2)
            scores_after = {
                "simulation": self.check_simulation_score()[0],
                "strategy": self.check_strategy_distillation()[0],
                "position": self.check_dynamic_weights()[0],
            }
            scores_after.update(self.check_layer_scores())
            
            improvement = scores_after.get("simulation", 0) - scores_before.get("simulation", 0)
            
            iter_result = IterationResult(
                iteration_id=iteration_id,
                timestamp=datetime.now().isoformat(),
                triggered_by=reason,
                actions_taken=actions_taken,
                scores_before=scores_before,
                scores_after=scores_after,
                improvement=improvement,
                status="success" if result.returncode == 0 else "partial"
            )
            
            self.iteration_history.append(asdict(iter_result))
            self._save_iteration_history()
            
            return iter_result
            
        except subprocess.TimeoutExpired:
            logger.error("迭代脚本执行超时")
            return IterationResult(
                iteration_id=iteration_id,
                timestamp=datetime.now().isoformat(),
                triggered_by=reason,
                actions_taken=["timeout"],
                scores_before=scores_before,
                scores_after={},
                improvement=0,
                status="failed"
            )
        except Exception as e:
            logger.error(f"迭代异常: {e}")
            return None
    
    def run_autonomous_cycle(self) -> Dict:
        sim_score, _ = self.check_simulation_score()
        strat_score, _ = self.check_strategy_distillation()
        pos_score, _ = self.check_dynamic_weights()
        layer_scores = self.check_layer_scores()
        
        recs = self.generate_recommendations()
        should_trigger, trigger_reason = self.should_trigger_iteration()
        
        result = None
        if should_trigger:
            result = self.trigger_iteration()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "current_scores": {
                "simulation": sim_score,
                "strategy": strat_score,
                "position": pos_score,
                "layers": layer_scores,
            },
            "recommendations": [asdict(r) for r in recs],
            "should_trigger": should_trigger,
            "trigger_reason": trigger_reason,
            "iteration_triggered": result is not None,
            "iteration_result": asdict(result) if result else None,
        }
    
    def get_status_dashboard(self) -> Dict:
        sim_score, _ = self.check_simulation_score()
        strat_score, _ = self.check_strategy_distillation()
        pos_score, _ = self.check_dynamic_weights()
        layer_scores = self.check_layer_scores()
        
        recent_iters = self.iteration_history[-5:] if self.iteration_history else []
        avg_improvement = sum(i.get('improvement', 0) for i in recent_iters) / max(1, len(recent_iters))
        
        return {
            "scores": {
                "simulation": {"value": sim_score, "threshold": self.config.SIMULATION_MIN_SCORE, "status": "ok" if sim_score >= self.config.SIMULATION_MIN_SCORE else "warn"},
                "strategy": {"value": strat_score, "threshold": self.config.STRATEGY_MIN_SCORE, "status": "ok" if strat_score >= self.config.STRATEGY_MIN_SCORE else "warn"},
                "position": {"value": pos_score, "threshold": self.config.POSITION_MIN_SCORE, "status": "ok" if pos_score >= self.config.POSITION_MIN_SCORE else "warn"},
            },
            "layers": {k: {"value": v, "threshold": self.config.THRESHOLDS.get(f"layer_{k}_score", 70)} for k, v in layer_scores.items()},
            "iteration_stats": {
                "total": len(self.iteration_history),
                "recent_5": len(recent_iters),
                "avg_improvement": avg_improvement,
                "last_iteration": self.iteration_history[-1]['timestamp'] if self.iteration_history else None,
            }
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="CEO自主迭代管理器")
    parser.add_argument("--status", action="store_true", help="显示状态")
    parser.add_argument("--recommend", action="store_true", help="生成建议")
    parser.add_argument("--trigger", action="store_true", help="触发迭代")
    parser.add_argument("--auto", action="store_true", help="运行自主周期")
    args = parser.parse_args()
    
    manager = CEOAutoIterationManager()
    
    if args.status:
        status = manager.get_status_dashboard()
        print(json.dumps(status, indent=2, ensure_ascii=False))
    elif args.recommend:
        recs = manager.generate_recommendations()
        print(f"发现 {len(recs)} 条建议:")
        for r in recs:
            print(f"  [{r.priority}] {r.category}: {r.reason}")
    elif args.trigger:
        result = manager.trigger_iteration(force=True)
        if result:
            print(f"迭代完成: {result.iteration_id}")
            print(f"改进: {result.improvement:+.1f}")
        else:
            print("迭代未触发")
    elif args.auto:
        result = manager.run_autonomous_cycle()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        status = manager.get_status_dashboard()
        print(json.dumps(status, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
