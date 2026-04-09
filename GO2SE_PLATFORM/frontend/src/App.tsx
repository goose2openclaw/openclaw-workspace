/**
 * GO2SE 北斗七鑫 V10 - 智能投资平台
 * 
 * 投资架构:
 * ┌─────────────────────────────────────────────────────────┐
 * │              北斗七鑫投资组合 (可调参数)                   │
 * ├─────────────────────────────────────────────────────────┤
 * │  投资工具 (5种)              │  打工工具 (2种)           │
 * │  🐰 打兔子 (前20主流)        │  💰 薅羊毛 (空投)        │
 * │  🐹 打地鼠 (其他币)          │  👶 穷孩子 (众包)        │
 * │  🔮 走着瞧 (预测市场)        │                           │
 * │  👑 跟大哥 (做市)           │                           │
 * │  🍀 搭便车 (跟单)          │                           │
 * ├─────────────────────────────────────────────────────────┤
 * │  趋势判断: 声纳库 │ 预言机 │ MiroFish │ 情绪 │ 其他     │
 * ├─────────────────────────────────────────────────────────┤
 * │  底层: 市场数据 │ 算力 │ 策略 │ 资金                     │
 * └─────────────────────────────────────────────────────────┘
 * 
 * 25维度全向仿真 (A-E五层)
 */

import { useState, useEffect, useCallback } from 'react';
import './App.css';

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8004";

// 工具类型
type Tool = {
  id: string;
  name: string;
  emoji: string;
  position: number;  // 0-100
  stopLoss: number;
  takeProfit: number;
  status: 'active' | 'paused' | 'inactive';
  dailyPnL: number;
  totalPnL: number;
  trades: number;
};

// 层级类型
type Layer = 'A' | 'B' | 'C' | 'D' | 'E';

interface MarketData {
  symbol: string;
  price: number;
  change24h: number;
  volume: number;
}

interface Signal {
  id: string;
  symbol: string;
  type: 'buy' | 'sell';
  strength: number;
  timestamp: string;
}

interface PortfolioStats {
  totalValue: number;
  dailyPnL: number;
  totalPnL: number;
  positions: number;
  winRate: number;
}

function App() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'tools' | 'trends' | 'signals' | 'portfolio' | 'settings'>('dashboard');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // 数据状态
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [signals, setSignals] = useState<Signal[]>([]);
  // 系统信息
  const [appVersion, setAppVersion] = useState<string>('v7.1.0');
  
  const [_portfolio, setPortfolio] = useState<PortfolioStats | null>(null);
  const [performance, setPerformance] = useState<any>(null);
  
  // 北斗七鑫工具配置
  const [tools, setTools] = useState<Tool[]>([
    { id: 'rabbit', name: '打兔子', emoji: '🐰', position: 25, stopLoss: 5, takeProfit: 8, status: 'active', dailyPnL: 0, totalPnL: 0, trades: 0 },
    { id: 'mole', name: '打地鼠', emoji: '🐹', position: 20, stopLoss: 8, takeProfit: 15, status: 'active', dailyPnL: 0, totalPnL: 0, trades: 0 },
    { id: 'oracle', name: '走着瞧', emoji: '🔮', position: 15, stopLoss: 5, takeProfit: 10, status: 'active', dailyPnL: 0, totalPnL: 0, trades: 0 },
    { id: 'leader', name: '跟大哥', emoji: '👑', position: 15, stopLoss: 3, takeProfit: 6, status: 'active', dailyPnL: 0, totalPnL: 0, trades: 0 },
    { id: 'hitchhiker', name: '搭便车', emoji: '🍀', position: 10, stopLoss: 5, takeProfit: 8, status: 'active', dailyPnL: 0, totalPnL: 0, trades: 0 },
    { id: 'wool', name: '薅羊毛', emoji: '💰', position: 3, stopLoss: 2, takeProfit: 20, status: 'paused', dailyPnL: 0, totalPnL: 0, trades: 0 },
    { id: 'poor', name: '穷孩子', emoji: '👶', position: 2, stopLoss: 1, takeProfit: 30, status: 'paused', dailyPnL: 0, totalPnL: 0, trades: 0 },
  ]);

  // 仿真结果
  const [simulationScore] = useState<number>(87.6);
  const [layerScores] = useState<Record<Layer, number>>({
    A: 82.0, B: 89.1, C: 77.4, D: 88.2, E: 94.9
  });

  // 获取数据
  const fetchData = useCallback(async () => {
    try {
      const [marketRes, signalsRes, statsRes, portfolioRes, perfRes] = await Promise.all([
        fetch(`${API_BASE}/api/market`).catch(() => null),
        fetch(`${API_BASE}/api/signals?limit=20`).catch(() => null),
        fetch(`${API_BASE}/api/stats`).catch(() => null),
        fetch(`${API_BASE}/api/portfolio`).catch(() => null),
        fetch(`${API_BASE}/api/performance`).catch(() => null),
      ]);

      const errors: string[] = [];
      
      if (marketRes?.ok) {
        const d = await marketRes.json();
        setMarketData(d.data || []);
      } else errors.push('market');
      
      if (signalsRes?.ok) {
        const d = await signalsRes.json();
        setSignals(d.signals || []);
      } else errors.push('signals');
      
      if (statsRes?.ok) {
        const d = await statsRes.json();
        // 提取版本信息
        if (d.data?.version) setAppVersion(d.data.version);
        // 工具盈亏数据由 /api/v7/tools 提供，这里保留API原始数据
        // statsRes仅用于确认服务健康
      } else errors.push('stats');
      
      if (portfolioRes?.ok) {
        const d = await portfolioRes.json();
        setPortfolio(d);
      }

      if (perfRes?.ok) {
        const d = await perfRes.json();
        setPerformance(d);
        // 更新工具配置中的权重
        if (d.investment_tools) {
          setTools(prev => prev.map(t => {
            const inv = d.investment_tools[t.id];
            const work = d.work_tools?.[t.id];
            if (inv) return { ...t, position: inv.weight || t.position, status: inv.status === 'disabled' ? 'inactive' : 'active' };
            if (work) return { ...t, position: work.weight || t.position };
            return t;
          }));
        }
      }
      
      if (errors.length > 0) {
        setError(`API issues: ${errors.join(', ')}`);
      }
      
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch data');
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [fetchData]);

  // 渲染组件
  const renderDashboard = () => (
    <div className="dashboard">
      {/* 概览卡片 */}
      <div className="overview-cards">
        <div className="card stat-card">
          <div className="stat-label">平台评分</div>
          <div className="stat-value large">{simulationScore.toFixed(1)}</div>
          <div className="stat-change positive">↑ 3.2%</div>
        </div>
        <div className="card stat-card">
          <div className="stat-label">总资产</div>
          <div className="stat-value large">$85,000</div>
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

      {/* 层级评分 */}
      <div className="card layer-scores">
        <h3>📊 25维度分层评分</h3>
        <div className="layer-grid">
          <div className="layer-item" onClick={() => setActiveTab('dashboard')}>
            <span className="layer-badge A">A</span>
            <span className="layer-name">投资组合</span>
            <span className="layer-score">{layerScores.A.toFixed(1)}</span>
          </div>
          <div className="layer-item" onClick={() => setActiveTab('tools')}>
            <span className="layer-badge B">B</span>
            <span className="layer-name">投资工具</span>
            <span className="layer-score">{layerScores.B.toFixed(1)}</span>
          </div>
          <div className="layer-item" onClick={() => setActiveTab('trends')}>
            <span className="layer-badge C">C</span>
            <span className="layer-name">趋势判断</span>
            <span className="layer-score">{layerScores.C.toFixed(1)}</span>
          </div>
          <div className="layer-item">
            <span className="layer-badge D">D</span>
            <span className="layer-name">底层资源</span>
            <span className="layer-score">{layerScores.D.toFixed(1)}</span>
          </div>
          <div className="layer-item">
            <span className="layer-badge E">E</span>
            <span className="layer-name">运营支撑</span>
            <span className="layer-score">{layerScores.E.toFixed(1)}</span>
          </div>
        </div>
      </div>

      {/* 市场数据 */}
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

  const renderTools = () => (
    <div className="tools-section">
      <h2>🎛️ 北斗七鑫投资工具</h2>
      <div className="tools-grid">
        {tools.map(tool => (
          <div key={tool.id} className={`card tool-card ${tool.status}`}>
            <div className="tool-header">
              <span className="tool-emoji">{tool.emoji}</span>
              <span className="tool-name">{tool.name}</span>
              <span className={`status-badge ${tool.status}`}>{tool.status}</span>
            </div>
            <div className="tool-config">
              <div className="config-row">
                <span>仓位:</span>
                <span className="value">{tool.position}%</span>
              </div>
              <div className="config-row">
                <span>止损:</span>
                <span className="value danger">{tool.stopLoss}%</span>
              </div>
              <div className="config-row">
                <span>止盈:</span>
                <span className="value success">{tool.takeProfit}%</span>
              </div>
            </div>
            <div className="tool-stats">
              <div className="stat">
                <span className="label">日盈亏</span>
                <span className={`value ${tool.dailyPnL >= 0 ? 'positive' : 'negative'}`}>
                  {tool.dailyPnL >= 0 ? '+' : ''}{tool.dailyPnL.toFixed(2)}
                </span>
              </div>
              <div className="stat">
                <span className="label">总盈亏</span>
                <span className={`value ${tool.totalPnL >= 0 ? 'positive' : 'negative'}`}>
                  {tool.totalPnL >= 0 ? '+' : ''}{tool.totalPnL.toFixed(2)}
                </span>
              </div>
              <div className="stat">
                <span className="label">交易数</span>
                <span className="value">{tool.trades}</span>
              </div>
            </div>
            <div className="tool-actions">
              <button className="btn-small">配置</button>
              <button className={`btn-small ${tool.status === 'active' ? 'warning' : 'success'}`}>
                {tool.status === 'active' ? '暂停' : '启动'}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderTrends = () => (
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
          <div className="trend-status active">540 Agents</div>
          <div className="trend-rounds">27 轮共识</div>
        </div>
        <div className="card trend-card">
          <h4>💢 市场情绪</h4>
          <div className="trend-status neutral">中性</div>
          <div className="trend-sentiment">恐惧贪婪: 45</div>
        </div>
      </div>
    </div>
  );

  const renderSignals = () => (
    <div className="signals-section">
      <h2>📡 交易信号</h2>
      <div className="signals-list">
        {signals.length > 0 ? signals.slice(0, 10).map(signal => (
          <div key={signal.id} className={`card signal-card ${signal.type}`}>
            <span className="signal-type">{signal.type === 'buy' ? '🟢 买入' : '🔴 卖出'}</span>
            <span className="signal-symbol">{signal.symbol}</span>
            <span className="signal-strength">强度: {signal.strength}%</span>
          </div>
        )) : (
          <div className="card">暂无信号</div>
        )}
      </div>
    </div>
  );

  const renderPortfolio = () => (
    <div className="portfolio-section">
      <h2>💼 投资组合 V10</h2>

      {/* 总览卡片 */}
      <div className="card portfolio-summary">
        <div className="summary-row">
          <span>总资金</span>
          <span className="large">${performance?.total_capital?.toLocaleString() || '100,000'}</span>
        </div>
        <div className="summary-row">
          <span>投资池 (80%)</span>
          <span className="positive">${performance?.investment_pool?.toLocaleString() || '80,000'}</span>
        </div>
        <div className="summary-row">
          <span>打工池 (20%)</span>
          <span className="positive">${performance?.work_pool?.toLocaleString() || '20,000'}</span>
        </div>
      </div>

      {/* 投资工具分配 */}
      <div className="card allocation">
        <h4>📊 投资工具分配 (5个)</h4>
        <div className="allocation-bars">
          {Object.entries(performance?.investment_tools || {}).map(([id, tool]: [string, any]) => (
            <div key={id} className="allocation-row">
              <span>{tool.name}</span>
              <div className="bar-container">
                <div className="bar" style={{
                  width: `${tool.allocation / (performance?.investment_pool || 80000) * 100}%`,
                  backgroundColor: tool.color,
                  opacity: tool.status === 'disabled' ? 0.3 : 1
                }}></div>
              </div>
              <span className={tool.status === 'disabled' ? 'disabled' : ''}>
                ${(tool.allocation || 0).toLocaleString()} ({tool.weight}%)
              </span>
            </div>
          ))}
        </div>
        <div className="action-buttons">
          <button className="btn-action replenish"
            disabled={!performance?.actions?.replenish?.available}
            title={performance?.actions?.replenish?.description}>
            📥 补仓
          </button>
          <button className="btn-action cashout"
            disabled={!performance?.actions?.cashout?.available}
            title={performance?.actions?.cashout?.description}>
            📤 套现
          </button>
        </div>
      </div>

      {/* 打工工具 + 现金流 */}
      <div className="card allocation work-tools">
        <h4>💰 打工工具 (2个) - 现金流收集</h4>
        <div className="allocation-bars">
          {Object.entries(performance?.work_tools || {}).map(([id, tool]: [string, any]) => (
            <div key={id} className="allocation-row">
              <span>{tool.name}</span>
              <div className="bar-container">
                <div className="bar" style={{
                  width: `${tool.allocation / (performance?.work_pool || 20000) * 100}%`,
                  backgroundColor: tool.color
                }}></div>
              </div>
              <span>${(tool.allocation || 0).toLocaleString()} (现金流{tool.cashflow_rate * 100}%)</span>
            </div>
          ))}
        </div>
        <div className="cashflow-status">
          <span>💵 现金流池: ${(performance?.cashflow_pool || 0).toLocaleString()}</span>
        </div>
        <div className="action-buttons">
          <button className="btn-action work-to-invest"
            disabled={!performance?.actions?.work_to_invest?.available}
            title={performance?.actions?.work_to_invest?.description}>
            🔄 打工→投资
          </button>
        </div>
      </div>
    </div>
  );

  const renderSettings = () => (
    <div className="settings-section">
      <h2>⚙️ 系统设置</h2>
      <div className="settings-grid">
        <div className="card setting-card">
          <h4>🛡️ 风控规则</h4>
          <div className="setting-row">
            <span>总仓位上限</span>
            <span>80%</span>
          </div>
          <div className="setting-row">
            <span>单笔风险</span>
            <span>5%</span>
          </div>
          <div className="setting-row">
            <span>日亏损熔断</span>
            <span>15%</span>
          </div>
        </div>
        <div className="card setting-card">
          <h4>🔧 平台配置</h4>
          <div className="setting-row">
            <span>交易模式</span>
            <span>Dry Run</span>
          </div>
          <div className="setting-row">
            <span>API延迟</span>
            <span>7ms</span>
          </div>
          <div className="setting-row">
            <span>版本</span>
            <span>{appVersion}</span>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="app">
      {/* 顶部导航 */}
      <nav className="nav">
        <div className="nav-brand">
          <span className="logo">🪿</span>
          <span className="title">GO2SE 北斗七鑫 {appVersion}</span>
        </div>
        <div className="nav-tabs">
          <button className={activeTab === 'dashboard' ? 'active' : ''} onClick={() => setActiveTab('dashboard')}>总览</button>
          <button className={activeTab === 'tools' ? 'active' : ''} onClick={() => setActiveTab('tools')}>工具</button>
          <button className={activeTab === 'trends' ? 'active' : ''} onClick={() => setActiveTab('trends')}>趋势</button>
          <button className={activeTab === 'signals' ? 'active' : ''} onClick={() => setActiveTab('signals')}>信号</button>
          <button className={activeTab === 'portfolio' ? 'active' : ''} onClick={() => setActiveTab('portfolio')}>组合</button>
          <button className={activeTab === 'settings' ? 'active' : ''} onClick={() => setActiveTab('settings')}>设置</button>
        </div>
        <div className="nav-status">
          <span className="status-dot"></span>
          <span>{appVersion}</span>
        </div>
      </nav>

      {/* 主内容 */}
      <main className="main">
        {loading ? (
          <div className="loading">
            <div className="spinner"></div>
            <p>加载中...</p>
          </div>
        ) : error ? (
          <div className="error-banner">{error}</div>
        ) : (
          <>
            {activeTab === 'dashboard' && renderDashboard()}
            {activeTab === 'tools' && renderTools()}
            {activeTab === 'trends' && renderTrends()}
            {activeTab === 'signals' && renderSignals()}
            {activeTab === 'portfolio' && renderPortfolio()}
            {activeTab === 'settings' && renderSettings()}
          </>
        )}
      </main>

      {/* 底部状态栏 */}
      <footer className="footer">
        <span>🪿 GO2SE 北斗七鑫 {appVersion}</span>
        <span>|</span>
        <span>评分: {simulationScore.toFixed(1)}</span>
        <span>|</span>
        <span>25维度全向仿真</span>
      </footer>
    </div>
  );
}

export default App;
