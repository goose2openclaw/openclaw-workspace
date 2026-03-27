import { useState, useEffect } from 'react'
import './App.css'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

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

function App() {
  const [markets, setMarkets] = useState<MarketData[]>([])
  const [signals, setSignals] = useState<Signal[]>([])
  const [stats, setStats] = useState<any>({})
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'market' | 'signals' | 'trades'>('market')

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 10000) // 每10秒刷新
    return () => clearInterval(interval)
  }, [])

  const fetchData = async () => {
    try {
      const [marketRes, signalsRes, statsRes] = await Promise.all([
        fetch(`${API_BASE}/api/market`),
        fetch(`${API_BASE}/api/signals?limit=20`),
        fetch(`${API_BASE}/api/stats`)
      ])
      
      const marketData = await marketRes.json()
      const signalsData = await signalsRes.json()
      const statsData = await statsRes.json()
      
      setMarkets(marketData.data || [])
      setSignals(signalsData.data || [])
      setStats(statsData.data || {})
      setLoading(false)
    } catch (error) {
      console.error('Fetch error:', error)
    }
  }

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

  return (
    <div className="app">
      <header className="header">
        <h1>🪿 GO2SE 量化交易平台</h1>
        <div className="status">
          <span className="mode">模式: {stats.trading_mode || 'dry_run'}</span>
          <span className="position">仓位: {(stats.max_position || 0) * 100}%</span>
        </div>
      </header>

      <nav className="nav">
        <button 
          className={activeTab === 'market' ? 'active' : ''} 
          onClick={() => setActiveTab('market')}
        >
          📊 市场
        </button>
        <button 
          className={activeTab === 'signals' ? 'active' : ''} 
          onClick={() => setActiveTab('signals')}
        >
          🎯 信号
        </button>
        <button 
          className={activeTab === 'trades' ? 'active' : ''} 
          onClick={() => setActiveTab('trades')}
        >
          📈 交易
        </button>
      </nav>

      <main className="content">
        {activeTab === 'market' && (
          <div className="market-grid">
            {markets.map(market => (
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
            ) : (
              signals.map(signal => (
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
              ))
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
          </div>
        )}
      </main>

      <footer className="footer">
        <span>🪿 GO2SE v1.0.0</span>
        <span>•</span>
        <span>数据更新: {new Date().toLocaleTimeString()}</span>
      </footer>
    </div>
  )
}

export default App
