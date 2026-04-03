"""
ML Routes - ML能力API端点
===========================
提供REST API访问所有ML模块
"""
from flask import Blueprint, jsonify, request
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ml_bp = Blueprint("ml", __name__, url_prefix="/api/ml")

try:
    from app.ml_core import MLHub
    _ml_hub = MLHub()
except ImportError:
    _ml_hub = None


@ml_bp.route("/capabilities", methods=["GET"])
def get_capabilities():
    """返回ML能力清单"""
    if _ml_hub is None:
        return jsonify({"error": "ML Hub not initialized"})
    return jsonify(_ml_hub.get_capabilities())


@ml_bp.route("/quant/factor_analysis", methods=["POST"])
def factor_analysis():
    """多因子分析"""
    if _ml_hub is None:
        return jsonify({"error": "ML Hub not initialized"})
    data = request.get_json()
    symbol = data.get("symbol", "BTC")
    result = _ml_hub.modules["quant"].factor_analysis(symbol)
    return jsonify(result)


@ml_bp.route("/quant/signals", methods=["POST"])
def generate_signals():
    """批量信号生成"""
    if _ml_hub is None:
        return jsonify({"error": "ML Hub not initialized"})
    data = request.get_json()
    symbols = data.get("symbols", ["BTC", "ETH", "SOL"])
    result = _ml_hub.modules["quant"].generate_signals(symbols)
    return jsonify({"signals": result})


@ml_bp.route("/predict/price", methods=["POST"])
def predict_price():
    """价格预测"""
    if _ml_hub is None:
        return jsonify({"error": "ML Hub not initialized"})
    data = request.get_json()
    symbol = data.get("symbol", "BTC")
    horizon = data.get("horizon", "1h")
    model = data.get("model", "Ensemble")
    result = _ml_hub.modules["predictor"].predict_price(symbol, horizon, model)
    return jsonify(result)


@ml_bp.route("/predict/trend", methods=["POST"])
def predict_trend():
    """趋势预测"""
    if _ml_hub is None:
        return jsonify({"error": "ML Hub not initialized"})
    data = request.get_json()
    symbol = data.get("symbol", "BTC")
    timeframe = data.get("timeframe", "1h")
    result = _ml_hub.modules["predictor"].predict_trend(symbol, timeframe)
    return jsonify(result)


@ml_bp.route("/predict/ensemble", methods=["POST"])
def ensemble_predict():
    """多模型集成预测"""
    if _ml_hub is None:
        return jsonify({"error": "ML Hub not initialized"})
    data = request.get_json()
    symbol = data.get("symbol", "BTC")
    horizon = data.get("horizon", "1h")
    result = _ml_hub.modules["predictor"].ensemble_predict(symbol, horizon)
    return jsonify(result)


@ml_bp.route("/optimizer/bayesian", methods=["POST"])
def bayesian_optimize():
    """贝叶斯优化"""
    if _ml_hub is None:
        return jsonify({"error": "ML Hub not initialized"})
    data = request.get_json()
    bounds = data.get("bounds", {"learning_rate": [0.001, 0.1], "depth": [3, 10]})
    n_iterations = data.get("n_iterations", 20)

    def objective_fn(params):
        return -sum(v**2 for v in params.values())

    result = _ml_hub.modules["optimizer"].bayesian_optimize(bounds, objective_fn, n_iterations)
    return jsonify(result)


@ml_bp.route("/optimizer/genetic", methods=["POST"])
def genetic_optimize():
    """遗传算法优化"""
    if _ml_hub is None:
        return jsonify({"error": "ML Hub not initialized"})
    data = request.get_json()
    population = data.get("population", [{"p1": 0.5, "p2": 0.3}] * 10)
    n_generations = data.get("n_generations", 30)

    def fitness_fn(individual):
        return sum(v for v in individual.values())

    result = _ml_hub.modules["optimizer"].genetic_optimize(population, fitness_fn, n_generations)
    return jsonify(result)


@ml_bp.route("/airdrop/scan", methods=["POST"])
def scan_airdrop():
    """空投资格扫描"""
    if _ml_hub is None:
        return jsonify({"error": "ML Hub not initialized"})
    data = request.get_json()
    wallet = data.get("wallet", "0x...")
    chains = data.get("chains", None)
    result = _ml_hub.modules["airdrop"].scan_eligibility(wallet, chains)
    return jsonify(result)


@ml_bp.route("/airdrop/calendar", methods=["GET"])
def airdrop_calendar():
    """空投日历"""
    if _ml_hub is None:
        return jsonify({"error": "ML Hub not initialized"})
    result = _ml_hub.modules["airdrop"].get_airdrop_calendar()
    return jsonify(result)


@ml_bp.route("/airdrop/strategies", methods=["POST"])
def rank_airdrop_strategies():
    """空投策略排序"""
    if _ml_hub is None:
        return jsonify({"error": "ML Hub not initialized"})
    data = request.get_json()
    capital = data.get("available_capital", 1000)
    risk = data.get("risk_tolerance", "MEDIUM")
    result = _ml_hub.modules["airdrop"].rank_strategies(capital, risk)
    return jsonify(result)


@ml_bp.route("/compute/status", methods=["GET"])
def compute_status():
    """算力状态"""
    if _ml_hub is None:
        return jsonify({"error": "ML Hub not initialized"})
    result = _ml_hub.modules["compute"].get_system_status()
    return jsonify(result)


@ml_bp.route("/compute/schedule", methods=["GET"])
def compute_schedule():
    """调度计划"""
    if _ml_hub is None:
        return jsonify({"error": "ML Hub not initialized"})
    result = _ml_hub.modules["compute"].get_schedule()
    return jsonify(result)


@ml_bp.route("/compute/optimize", methods=["GET"])
def compute_optimize():
    """优化建议"""
    if _ml_hub is None:
        return jsonify({"error": "ML Hub not initialized"})
    result = _ml_hub.modules["compute"].optimize_allocation()
    return jsonify(result)


@ml_bp.route("/winrate/predict", methods=["POST"])
def predict_winrate():
    """胜率预测"""
    if _ml_hub is None:
        return jsonify({"error": "ML Hub not initialized"})
    data = request.get_json()
    strategy = data.get("strategy", "突破策略")
    regime = data.get("market_regime", "NORMAL")
    result = _ml_hub.modules["winrate"].predict_win_rate(strategy, market_regime=regime)
    return jsonify(result)


@ml_bp.route("/winrate/combined", methods=["POST"])
def combined_winrate():
    """组合胜率"""
    if _ml_hub is None:
        return jsonify({"error": "ML Hub not initialized"})
    data = request.get_json()
    strategies = data.get("strategies", ["突破策略", "网格交易"])
    weights = data.get("weights", None)
    result = _ml_hub.modules["winrate"].predict_combined_win_rate(strategies, weights)
    return jsonify(result)


@ml_bp.route("/crowd/aggregate", methods=["POST"])
def aggregate_signals():
    """众包信号聚合"""
    if _ml_hub is None:
        return jsonify({"error": "ML Hub not initialized"})
    data = request.get_json()
    symbol = data.get("symbol", "BTC")
    sources = data.get("sources", None)
    result = _ml_hub.modules["crowdsignal"].aggregate_signals(symbol, sources)
    return jsonify(result)


@ml_bp.route("/crowd/polymarket", methods=["POST"])
def polymarket_signals():
    """预测市场信号"""
    if _ml_hub is None:
        return jsonify({"error": "ML Hub not initialized"})
    data = request.get_json()
    question = data.get("question", "BTC > $70000 by EOD?")
    result = _ml_hub.modules["crowdsignal"].get_polymarket_signals(question)
    return jsonify(result)


@ml_bp.route("/crowd/timeline", methods=["POST"])
def sentiment_timeline():
    """情感时间线"""
    if _ml_hub is None:
        return jsonify({"error": "ML Hub not initialized"})
    data = request.get_json()
    symbol = data.get("symbol", "BTC")
    hours = data.get("hours", 24)
    result = _ml_hub.modules["crowdsignal"].sentiment_timeline(symbol, hours)
    return jsonify(result)
