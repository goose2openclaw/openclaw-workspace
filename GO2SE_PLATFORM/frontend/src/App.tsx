import { useState, useEffect, useCallback } from 'react'
import './App.css'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5000'

interface MarketData {
  symbol: string
  price: number
  change_24h: number
  volume_24h: number
  rsi: number
}

interface Signal {
  id: number
  strategy: string
  symbol: string
  signal: string
  confidence: number
  reason: string
  created_at: string
}

interface Portfolio {
  total_pnl: number
  total_trades: number
  win_rate: number
  performance: {
    portfolio: Record<string, {
      name: string
      icon: string
      weight: number
      pnl: number
      return_rate: number
      trades: number
      strategies: string[]
      desc: string
    }>
  }
}

function App() {
  const [markets, setMarkets] = useState<MarketData[]>([])
  const [signals, setSignals] = useState<Signal[]>([])
  const [stats, setStats] = useState<any>({})
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null)
  const [loading, setLoading] = useState(true)
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date())
  const [activeTab, setActiveTab] = useState<'market' | 'signals' | 'trades' | 'portfolio'>('market')
  const [apiErrors, setApiErrors] = useState<string[]>([])

  const fetchData = useCallback(async () => {
    const errors: string[] = []
    try {
      const [marketRes, signalsRes, statsRes, portfolioRes] = await Promise.all([
        fetch(`${API_BASE}/api/market`).catch(() => null),
        fetch(`${API_BASE}/api/signals?limit=20`).catch(() => null),
        fetch(`${API_BASE}/api/stats`).catch(() => null),
        fetch(`${API_BASE}/api/portfolio`).catch(() => null),
      ])
      
      if (marketRes?.ok) {
        const d = await marketRes.json()
        setMarkets(d.data || [])
      } else errors.push('market')
      
      if (signalsRes?.ok) {
        const d = await signalsRes.json()
        setSignals(d.data || [])
      } else errors.push('signals')
      
      if (statsRes?.ok) {
        const d = await statsRes.json()
        setStats(d.data || {})
      }
      
      if (portfolioRes?.ok) {
        const d = await portfolioRes.json()
        setPortfolio(d.data || d || null)
      }
    } catch (error) {
      console.error('Fetch error:', error)
    } finally {
      setApiErrors(errors)
      setLastUpdate(new Date())
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 15000) // 每15秒刷新
    return () => clearInterval(interval)
  }, [fetchData])

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case 'buy': return 'signal-buy'
      case 'sell': return 'signal-sell'
      default: return 'signal-hold'
    }
  }

  const getSignalIcon = (signal: string) => {
    switch (signal) {
      case 'buy': return '🟢'
      case 'sell': return '🔴'
      default: return '🟡'
    }
  }

  if (loading) {
    return <div className="loading">🪿 加载中...</div>
  }

  const portfolioList = portfolio?.performance?.portfolio ? Object.values(portfolio.performance.portfolio) : []

  return (
    <div className="app">
      <header className="header">
        <h1>🪿 GO2SE 量化交易平台</h1>
        <div className="status">
          <span className="mode">模式: {stats.trading_mode || 'dry_run'}</span>
          <span className="position">仓位: {(stats.max_position || 0) * 100}%</span>
          {apiErrors.length > 0 && (
            <span className="error-badge" title={`API错误: ${apiErrors.join(',')}`}>⚠️</span>
          )}
        </div>
      </header>

      <nav className="nav">
        {[
          { key: 'market', label: '📊 市场' },
          { key: 'signals', label: '🎯 信号' },
          { key: 'portfolio', label: '💼 组合' },
          { key: 'trades', label: '📈 统计' },
        ].map(tab => (
          <button
            key={tab.key}
            className={activeTab === tab.key ? 'active' : ''}
            onClick={() => setActiveTab(tab.key as any)}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      <main className="content">
        {activeTab === 'market' && (
          <div className="market-grid">
            {markets.length === 0 ? (
              <div className="empty">暂无市场数据</div>
            ) : markets.map(market => (
              <div key={market.symbol} className="market-card">
                <div className="symbol">{market.symbol.replace('/USDT', '')}</div>
                <div className="price">${market.price?.toLocaleString()}</div>
                <div className={`change ${market.change_24h >= 0 ? 'up' : 'down'}`}>
                  {market.change_24h >= 0 ? '▲' : '▼'} {market.change_24h?.toFixed(2)}%
                </div>
                <div className="rsi">
                  RSI: <span className={market.rsi > 70 ? 'overbought' : market.rsi < 30 ? 'oversold' : ''}>
                    {market.rsi?.toFixed(1)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'signals' && (
          <div className="signals-list">
            {signals.length === 0 ? (
              <div className="empty">暂无信号</div>
            ) : signals.map(signal => (
              <div key={signal.id} className={`signal-card ${getSignalColor(signal.signal)}`}>
                <div className="signal-header">
                  <span className="strategy">{signal.strategy}</span>
                  <span className="signal-type">{getSignalIcon(signal.signal)} {signal.signal.toUpperCase()}</span>
                </div>
                <div className="signal-body">
                  <span className="symbol">{signal.symbol}</span>
                  <span className="confidence">置信度: {signal.confidence?.toFixed(1)}</span>
                </div>
                <div className="signal-reason">{signal.reason}</div>
                <div className="signal-time">{new Date(signal.created_at).toLocaleString()}</div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'portfolio' && (
          <div className="portfolio-view">
            <div className="portfolio-summary">
              <div className="stat-card">
                <div className="stat-value">{portfolio?.total_pnl ?? '--'}</div>
                <div className="stat-label">总盈亏 (USDT)</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{portfolio?.total_trades ?? 0}</div>
                <div className="stat-label">总交易数</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{portfolio?.win_rate ?? '--'}%</div>
                <div className="stat-label">胜率</div>
              </div>
            </div>
            {portfolioList.length === 0 ? (
              <div className="empty">暂无组合数据</div>
            ) : (
              <div className="portfolio-grid">
                {portfolioList.map((p: any) => (
                  <div key={p.name} className="portfolio-card">
                    <div className="portfolio-icon">{p.icon}</div>
                    <div className="portfolio-info">
                      <div className="portfolio-name">{p.name}</div>
                      <div className="portfolio-desc">{p.desc}</div>
                    </div>
                    <div className="portfolio-pnl">
                      <div className={`pnl-value ${p.pnl >= 0 ? 'up' : 'down'}`}>
                        {p.pnl >= 0 ? '+' : ''}{p.pnl} USDT
                      </div>
                      <div className="pnl-rate">{p.return_rate}%</div>
                    </div>
                    <div className="portfolio-meta">
                      <span>仓位 {p.weight}%</span>
                      <span>交易 {p.trades}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'trades' && (
          <div className="stats-panel">
            <div className="stat-card">
              <div className="stat-value">{stats.total_trades || 0}</div>
              <div className="stat-label">总交易</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats.open_trades || 0}</div>
              <div className="stat-label">持仓中</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats.total_signals || 0}</div>
              <div className="stat-label">信号总数</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats.executed_signals || 0}</div>
              <div className="stat-label">已执行</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{(stats.stop_loss || 0) * 100}%</div>
              <div className="stat-label">止损线</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{(stats.take_profit || 0) * 100}%</div>
              <div className="stat-label">止盈线</div>
            </div>
          </div>
        )}
      </main>

      <footer className="footer">
        <span>🪿 GO2SE v2.5</span>
        <span>•</span>
        <span>更新: {lastUpdate.toLocaleTimeString()}</span>
        <span>•</span>
        <span className={stats.trading_mode === 'live' ? 'live-mode' : 'dry-mode'}>
          {stats.trading_mode === 'live' ? '🔴 实盘' : '🟡 模拟'}
        </span>
      </footer>
    </div>
  )
}

export default App
