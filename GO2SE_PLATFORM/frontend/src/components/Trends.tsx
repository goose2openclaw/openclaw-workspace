export function Trends() {
  return (
    <div className="trends-section">
      <h2>🔮 趋势判断层</h2>
      <div className="trends-grid">
        <div className="card trend-card">
          <h4>📡 声纳库趋势模型</h4>
          <div className="trend-status active">运行中</div>
          <div className="trend-models">20+ 趋势模型</div>
        </div>
        <div className="card trend-card">
          <h4>🔮 预言机市场</h4>
          <div className="trend-status active">活跃</div>
          <div className="trend-markets">6 大预测市场</div>
        </div>
        <div className="card trend-card">
          <h4>🧠 MiroFish 共识</h4>
          <div className="trend-status active">1000 Agents</div>
          <div className="trend-rounds">95.1/100 评分</div>
        </div>
        <div className="card trend-card">
          <h4>💢 市场情绪</h4>
          <div className="trend-status neutral">中性</div>
          <div className="trend-sentiment">恐惧贪婪: 45</div>
        </div>
      </div>
    </div>
  );
}
