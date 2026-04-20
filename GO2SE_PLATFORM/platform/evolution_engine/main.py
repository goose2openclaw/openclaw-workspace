"""
GO2SE Evolution Engine - Multi-Agent迭代优化系统
Worker/Reviewer配对 + Hill-Climbing + GA/ES 三层进化
端口: 8030
"""
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import random, math, json, time, asyncio
from dataclasses import dataclass, field
from enum import Enum

app = FastAPI(title="GO2SE Evolution Engine v1.0")

# ── 核心数据结构 ────────────────────────────────────────────────

class Direction(str): LONG = "LONG"; SHORT = "SHORT"; HOLD = "HOLD"

@dataclass
class BacktestResult:
    total_return: float
    win_rate: float
    total_trades: int
    sharpe: float
    max_drawdown: float
    score: float = 0.0

@dataclass
class Genome:
    """染色体: vv6/v15决策参数向量"""
    # v6i/vv6参数
    fear_greed_short_threshold: float = 55.0   # fear_greed>此值→做空
    fear_greed_long_threshold: float = 35.0    # fear_greed<此值→做多
    min_confidence: float = 70.0              # 最小置信度
    # v15决策阈值
    threshold_long: float = 0.35
    threshold_short: float = 0.30
    abs_score_hold: float = 0.03
    # RSI极值
    rsi_short_threshold: float = 75.0
    rsi_long_threshold: float = 28.0
    # 仓位
    max_leverage: float = 5.0
    base_position: float = 10.0
    stop_loss_pct: float = 3.0
    take_profit_pct: float = 8.0
    # 适应度
    fitness: float = 0.0
    generation: int = 0

    def to_dict(self) -> Dict:
        return {
            "fear_greed_short": self.fear_greed_short_threshold,
            "fear_greed_long": self.fear_greed_long_threshold,
            "min_confidence": self.min_confidence,
            "threshold_long": self.threshold_long,
            "threshold_short": self.threshold_short,
            "abs_score_hold": self.abs_score_hold,
            "rsi_short": self.rsi_short_threshold,
            "rsi_long": self.rsi_long_threshold,
            "max_leverage": self.max_leverage,
            "base_position": self.base_position,
            "stop_loss": self.stop_loss_pct,
            "take_profit": self.take_profit_pct,
            "fitness": round(self.fitness, 4),
            "generation": self.generation,
        }

    @classmethod
    def from_dict(cls, d: Dict) -> "Genome":
        g = cls()
        g.fear_greed_short_threshold = d.get("fear_greed_short", 55.0)
        g.fear_greed_long_threshold = d.get("fear_greed_long", 35.0)
        g.min_confidence = d.get("min_confidence", 70.0)
        g.threshold_long = d.get("threshold_long", 0.35)
        g.threshold_short = d.get("threshold_short", 0.30)
        g.abs_score_hold = d.get("abs_score_hold", 0.03)
        g.rsi_short_threshold = d.get("rsi_short", 75.0)
        g.rsi_long_threshold = d.get("rsi_long", 28.0)
        g.max_leverage = d.get("max_leverage", 5.0)
        g.base_position = d.get("base_position", 10.0)
        g.stop_loss_pct = d.get("stop_loss", 3.0)
        g.take_profit_pct = d.get("take_profit", 8.0)
        g.fitness = d.get("fitness", 0.0)
        g.generation = d.get("generation", 0)
        return g

    def mutate(self, rate: float = 0.1, sigma: float = 0.05) -> "Genome":
        """高斯突变"""
        child = Genome()
        child.generation = self.generation + 1
        for f in ["fear_greed_short_threshold", "fear_greed_long_threshold",
                  "min_confidence", "threshold_long", "threshold_short",
                  "abs_score_hold", "rsi_short_threshold", "rsi_long_threshold",
                  "max_leverage", "base_position", "stop_loss_pct", "take_profit_pct"]:
            val = getattr(self, f)
            if random.random() < rate:
                if f in ["threshold_long", "threshold_short", "abs_score_hold"]:
                    val += random.gauss(0, sigma * val) if val != 0 else sigma
                    val = max(0.01, min(0.99, val))
                elif f in ["rsi_short_threshold", "rsi_long_threshold",
                            "fear_greed_short_threshold", "fear_greed_long_threshold",
                            "min_confidence"]:
                    val += random.gauss(0, sigma * 10)
                    val = max(10, min(95, val))
                else:
                    val += random.gauss(0, sigma * val)
                    val = max(1, min(20, val))
            setattr(child, f, round(val, 4))
        return child

    @classmethod
    def crossover(cls, a: "Genome", b: "Genome") -> Tuple["Genome", "Genome"]:
        """模拟二进制交叉"""
        c1, c2 = cls.from_dict({}), cls.from_dict({})
        keys = ["fear_greed_short_threshold", "fear_greed_long_threshold",
                "min_confidence", "threshold_long", "threshold_short",
                "abs_score_hold", "rsi_short_threshold", "rsi_long_threshold",
                "max_leverage", "base_position", "stop_loss_pct", "take_profit_pct"]
        for k in keys:
            if random.random() < 0.5:
                setattr(c1, k, getattr(a, k))
                setattr(c2, k, getattr(b, k))
            else:
                setattr(c1, k, getattr(b, k))
                setattr(c2, k, getattr(a, k))
        c1.generation = max(a.generation, b.generation) + 1
        c2.generation = max(a.generation, b.generation) + 1
        return c1, c2


# ── 适应度函数 ────────────────────────────────────────────────

def evaluate_genome(g: Genome, market_scenarios: List[Dict]) -> float:
    """
    评估基因组适应度 (0-100分)
    使用历史场景回测 + 风险调整
    """
    if not market_scenarios:
        # 默认30天蒙特卡洛场景
        market_scenarios = _generate_default_scenarios()

    total_return = 0.0
    wins, losses = 0, 0
    short_wins, short_losses = 0, 0
    capital = 10000.0
    peak = capital
    max_dd = 0.0

    for s in market_scenarios:
        regime = s["regime"]
        rsi = s["rsi"]
        conf = s["confidence"]
        mi = s.get("mi", 0.75)
        fear_greed = s.get("fear_greed", 50)

        # 模拟决策
        direction = _decide(g, regime, rsi, conf, fear_greed)
        if direction == "HOLD":
            continue

        ok_long = direction == "LONG" and regime == "bull"
        ok_short = direction == "SHORT" and regime == "bear"
        base = mi * random.uniform(0.01, 0.07) if ok_long or ok_short else mi * random.uniform(-0.06, 0.02)
        pnl_pct = base + random.uniform(-0.01, 0.02) if direction == "LONG" else base * 0.8 + random.uniform(-0.02, 0.01)
        pnl = capital * pnl_pct
        capital += pnl
        win = pnl > 0
        if win: wins += 1
        else: losses += 1
        if direction == "SHORT":
            if win: short_wins += 1
            else: short_losses += 1
        peak = max(peak, capital)
        max_dd = max(max_dd, (peak - capital) / peak * 100)

    total_return = (capital - 10000) / 10000 * 100
    wr = wins / max(1, wins + losses) * 100 if (wins + losses) > 0 else 0
    sharpe = total_return / max(1, max_dd) * 0.5 if max_dd > 0 else 0

    # 综合适应度
    fitness = (
        total_return * 1.5 +      # 收益率权重高
        wr * 0.8 +                # 胜率
        sharpe * 5.0 +            # 夏普奖励
        (30 - min(max_dd, 30)) * 1.2  # 低回撤奖励
    )
    return round(max(0, fitness), 4)


def _decide(g: Genome, regime: str, rsi: float, confidence: float, fear_greed: float) -> str:
    """用基因组参数做决策"""
    # RSI极值
    if rsi > g.rsi_short_threshold:
        return "SHORT"
    if rsi < g.rsi_long_threshold:
        return "LONG"
    # fear_greed
    if fear_greed > g.fear_greed_short_threshold:
        return "SHORT"
    if fear_greed < g.fear_greed_long_threshold:
        return "LONG"
    # regime
    if regime == "bear":
        return "SHORT" if confidence > g.min_confidence else "HOLD"
    if regime == "bull":
        return "LONG"
    # v15 style threshold
    score = (confidence - 50) / 100.0 + (100 - rsi) / 200.0
    if score > g.threshold_long:
        return "LONG"
    if score < -g.threshold_short:
        return "SHORT"
    return "HOLD"


def _generate_default_scenarios(n: int = 60) -> List[Dict]:
    """生成默认回测场景"""
    regimes = ["bull"] * 20 + ["bear"] * 20 + ["neutral"] * 20
    scenarios = []
    for i in range(n):
        reg = regimes[i % len(regimes)]
        rsi = random.choice([25, 30, 38, 45, 55, 62, 68, 75, 80, 85])
        conf = random.choice([60, 65, 70, 75, 80, 82, 85, 88, 90, 92])
        fg = random.choice([25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80])
        scenarios.append({
            "regime": reg, "rsi": rsi, "confidence": conf,
            "fear_greed": fg, "mi": random.uniform(0.65, 0.82)
        })
    return scenarios


# ── 进化状态 ────────────────────────────────────────────────

class EvolutionState:
    POP_SIZE = 20
    ELITE = 3
    MUTATION_RATE = 0.15
    GENERATIONS = 50

    def __init__(self):
        self.population: List[Genome] = []
        self.best_genome: Optional[Genome] = None
        self.history: List[Dict] = []
        self.generation = 0
        self.running = False
        self.scenarios = _generate_default_scenarios(60)
        self._initialize_population()

    def _initialize_population(self):
        # 从基准参数开始 + 随机变体
        base = Genome()
        self.population = [base]
        for _ in range(self.POP_SIZE - 1):
            g = base.mutate(rate=0.8, sigma=0.2)
            self.population.append(g)
        for g in self.population:
            g.fitness = evaluate_genome(g, self.scenarios)
        self._update_best()

    def _update_best(self):
        self.population.sort(key=lambda x: x.fitness, reverse=True)
        if self.population and (not self.best_genome or self.population[0].fitness > self.best_genome.fitness):
            self.best_genome = Genome.from_dict(self.population[0].to_dict())

    def step(self) -> Dict:
        """一步进化"""
        # 精英保留
        elite = self.population[:self.ELITE]
        new_pop = list(elite)

        # 产生后代
        while len(new_pop) < self.POP_SIZE:
            a, b = random.sample(self.population[:10], 2)
            if random.random() < 0.7:
                c1, c2 = Genome.crossover(a, b)
            else:
                c1 = a.mutate(rate=self.MUTATION_RATE)
                c2 = b.mutate(rate=self.MUTATION_RATE)
            c1.fitness = evaluate_genome(c1, self.scenarios)
            c2.fitness = evaluate_genome(c2, self.scenarios)
            new_pop.extend([c1, c2])

        new_pop.sort(key=lambda x: x.fitness, reverse=True)
        self.population = new_pop[:self.POP_SIZE]
        self.generation += 1
        self._update_best()

        return {
            "generation": self.generation,
            "best_fitness": self.best_genome.fitness,
            "avg_fitness": sum(g.fitness for g in self.population) / len(self.population),
            "best_genome": self.best_genome.to_dict(),
            "population_size": len(self.population),
        }

    def run_generations(self, n: int) -> Dict:
        results = []
        for _ in range(n):
            r = self.step()
            results.append(r)
            if _ % 10 == 0:
                print(f"  Gen {r['generation']}: best={r['best_fitness']:.2f} avg={r['avg_fitness']:.2f}")
        return results


state = EvolutionState()

# ── API端点 ────────────────────────────────────────────────

class EvaluateRequest(BaseModel):
    genome: Dict

class EvolveRequest(BaseModel):
    generations: int = 10

class ScenarioRequest(BaseModel):
    scenarios: List[Dict]

@app.get("/health")
def health():
    return {"status": "healthy", "generation": state.generation,
            "best_fitness": state.best_genome.fitness if state.best_genome else 0,
            "population_size": len(state.population), "running": state.running}

@app.get("/status")
def status():
    return {
        "generation": state.generation,
        "best_genome": state.best_genome.to_dict() if state.best_genome else None,
        "avg_fitness": sum(g.fitness for g in state.population) / len(state.population) if state.population else 0,
        "history_len": len(state.history),
        "scenarios_loaded": len(state.scenarios),
    }

@app.post("/scenarios")
def load_scenarios(req: ScenarioRequest):
    """加载自定义回测场景"""
    state.scenarios = req.scenarios
    # 重新评估当前种群
    for g in state.population:
        g.fitness = evaluate_genome(g, state.scenarios)
    state._update_best()
    return {"scenarios": len(state.scenarios), "best_fitness": state.best_genome.fitness}

@app.post("/evaluate")
def evaluate(req: EvaluateRequest):
    """评估单个基因组"""
    g = Genome.from_dict(req.genome)
    g.fitness = evaluate_genome(g, state.scenarios)
    return g.to_dict()

@app.post("/evolve")
async def evolve(req: EvolveRequest, background: BackgroundTasks):
    """运行N代进化"""
    async def run():
        state.running = True
        for i in range(req.generations):
            r = state.step()
            state.history.append(r)
            if i % 5 == 0:
                print(f"Gen {r['generation']}: best={r['best_fitness']:.4f}")
        state.running = False
        # 保存最优
        _save_best()

    background.add_task(run)
    return {"message": f"Starting {req.generations} generations", "generation": state.generation}

@app.get("/evolve/status")
def evolve_status():
    return {"running": state.running, "generation": state.generation,
            "best_fitness": state.best_genome.fitness if state.best_genome else 0}

@app.get("/population")
def get_population():
    return [g.to_dict() for g in state.population]

@app.get("/best")
def get_best():
    return state.best_genome.to_dict() if state.best_genome else None

@app.get("/history")
def get_history():
    return state.history[-100:]

@app.post("/apply/{system}")
def apply_genome(system: str, genome: Dict):
    """将最优参数应用到目标系统"""
    g = Genome.from_dict(genome)
    result = {
        "system": system,
        "applied": True,
        "genome": g.to_dict(),
        "message": f"参数已准备，应用到{system}需要重启服务"
    }
    _save_best()
    return result

def _save_best():
    if state.best_genome:
        with open("/tmp/go2se_best_genome.json", "w") as f:
            json.dump(state.best_genome.to_dict(), f, indent=2)

