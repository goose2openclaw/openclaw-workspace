import { useState, useEffect, useCallback } from 'react';

interface LayerScore { A: number; B: number; C: number; D: number; E: number }
interface MarketData { symbol: string; price: number; change24h: number }
interface PortfolioStats { totalValue: number; dailyPnL: number; totalPnL: number; positions: number; winRate: number }
type Layer = 'A' | 'B' | 'C' | 'D' | 'E';

interface DashboardProps {
  simulationScore: number;
  layerScores: LayerScore;
  marketData: MarketData[];
  portfolio: PortfolioStats | null;
  onNavigateToTools: () => void;
  onNavigateToTrends: () => void;
}

const LAYER_NAMES: Record<Layer, string> = {
  A: '投资组合', B: '投资工具', C: '趋势判断', D: '底层资源', E: '运营支撑'
};

export function Dashboard({
  simulationScore,
  layerScores,
  marketData,
  portfolio,
  onNavigateToTools,
  onNavigateToTrends
}: DashboardProps) {
  return (
    <div className="dashboard">
      <div className="overview-cards">
        <div className="card stat-card">
          <div className="stat-label">平台评分</div>
          <div className="stat-value large">{simulationScore.toFixed(1)}</div>
          <div className="stat-change positive">↑ 0.3%</div>
        </div>
        <div className="card stat-card">
          <div className="stat-label">总资产</div>
          <div className="stat-value large">${portfolio?.totalValue?.toLocaleString() || '—'}</div>
          <div className="stat-change positive">+$1,234</div>
        </div>
        <div className="card stat-card">
          <div className="stat-label">胜率</div>
          <div className="stat-value large">64.5%</div>
          <div className="stat-change negative">-2.1%</div>
        </div>
        <div className="card stat-card">
          <div className="stat-label">日收益</div>
          <div className="stat-value large">+2.23%</div>
          <div className="stat-change positive">ETH策略</div>
        </div>
      </div>
      <div className="card layer-scores">
        <h3>📊 25维度分层评分</h3>
        <div className="layer-grid">
          {(['A', 'B', 'C', 'D', 'E'] as Layer[]).map(l => (
            <div
              key={l}
              className="layer-item"
              onClick={() => l === 'B' ? onNavigateToTools() : l === 'C' ? onNavigateToTrends() : null}
            >
              <span className={`layer-badge ${l}`}>{l}</span>
              <span className="layer-name">{LAYER_NAMES[l]}</span>
              <span className="layer-score">{layerScores[l].toFixed(1)}</span>
            </div>
          ))}
        </div>
      </div>
      <div className="card market-section">
        <h3>📈 市场行情</h3>
        <div className="market-grid">
          {marketData.slice(0, 6).map(m => (
            <div key={m.symbol} className="market-item">
              <span className="symbol">{m.symbol}</span>
              <span className="price">${m.price?.toFixed(2) || '—'}</span>
              <span className={`change ${(m.change24h || 0) >= 0 ? 'positive' : 'negative'}`}>
                {(m.change24h || 0) >= 0 ? '↑' : '↓'} {Math.abs(m.change24h || 0).toFixed(2)}%
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export function useDashboardData() {
  const [portfolio, setPortfolio] = useState<PortfolioStats | null>(null);
  const [marketData, setMarketData] = useState<MarketData[]>([]);

  const fetchData = useCallback(async () => {
    try {
      const res = await fetch('http://localhost:8004/api/portfolio');
      if (res.ok) {
        const d = await res.json();
        setPortfolio(d);
      }
    } catch {}
    try {
      const res = await fetch('http://localhost:8004/api/market');
      if (res.ok) {
        const d = await res.json();
        setMarketData(d.slice || d);
      }
    } catch {}
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  return { portfolio, marketData };
}
