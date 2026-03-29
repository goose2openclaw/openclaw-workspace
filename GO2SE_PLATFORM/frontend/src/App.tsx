import React, { useState, useEffect, useCallback } from 'react'
import './App.css'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8004'

// ── Error Boundary ──────────────────────────────────────────────
class ErrorBoundary extends React.Component<
  { children: React.ReactNode; fallback?: React.ReactNode },
  { hasError: boolean; message: string }
> {
  constructor(props: any) {
    super(props)
    this.state = { hasError: false, message: '' }
  }
  static getDerivedStateFromError(e: Error) {
    return { hasError: true, message: e.message }
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <div className="error-icon">⚠️</div>
          <div className="error-msg">组件出错: {this.state.message}</div>
          <button onClick={() => window.location.reload()}>🔄 重新加载</button>
        </div>
      )
    }
    return this.props.children
  }
}

// ── Manual Refresh Button ────────────────────────────────────────
function RefreshButton({ onRefresh }: { onRefresh: () => void }) {
  return (
    <button className="refresh-btn" onClick={onRefresh} title="手动刷新数据">
      🔄
    </button>
  )
}

// ── Loading Skeleton ─────────────────────────────────────────────
function LoadingSkeleton({ tab }: { tab: string }) {
  return (
    <div className="skeleton">
      {[1, 2, 3].map(i => (
        <div key={i} className="skeleton-card">
          <div className="skeleton-line short" />
          <div className="skeleton-line" />
          <div className="skeleton-line medium" />
        </div>
      ))}
    </div>
  )
}

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
  const [activeTab, setActiveTab] = useState<'market' | 'signals' | 'trades' | 'portfolio' | 'backtest'>('market')
  type TabKey = typeof activeTab
  const [apiErrors, setApiErrors] = useState<string[]>([])
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [theme, setTheme] = useState<'dark' | 'light'>(() => {
    return (localStorage.getItem('go2se-theme') as 'dark' | 'light') || 'dark'
  })
  const [showTradePanel, setShowTradePanel] = useState(false)
  const [tradeSymbol, setTradeSymbol] = useState('BTC/USDT')
  const [tradeSide, setTradeSide] = useState<'buy' | 'sell'>('buy')
  const [tradeAmount, setTradeAmount] = useState('')
  const [tradeLoading, setTradeLoading] = useState(false)
  const [tradeResult, setTradeResult] = useState<string | null>(null)
  const [wsConnected, setWsConnected] = useState(false)
  const [apiKey, setApiKey] = useState<string | null>(localStorage.getItem('go2se_api_key'))
  const [authUser, setAuthUser] = useState<string | null>(localStorage.getItem('go2se_username'))
  const [showAuthPanel, setShowAuthPanel] = useState(false)
  const [authMode, setAuthMode] = useState<'login' | 'register'>('register')
  const [authUsername, setAuthUsername] = useState('')
  const [authResult, setAuthResult] = useState<string | null>(null)
  const [backtestLoading, setBacktestLoading] = useState(false)
  const [backtestResult, setBacktestResult] = useState<any>(null)
  const [backtestHistory, setBacktestHistory] = useState<any[]>([])
  const [backtestParams, setBacktestParams] = useState({
    symbol: 'BTC/USDT',
    start_date: '2025-01-01',
    end_date: '2025-12-31',
    initial_capital: 10000,
    stop_loss: 0.05,
    take_profit: 0.15,
    position_size: 0.1,
    strategy: 'rsi_macross'
  })

  const fetchData = useCallback(async (manual = false) => {
    if (manual) setIsRefreshing(true)
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
      if (manual) setIsRefreshing(false)
    }
  }, [])

  // ── Auth Handlers ─────────────────────────────────────────────
  const handleAuth = async () => {
    if (!authUsername.trim()) {
      setAuthResult('❌ 请输入用户名')
      return
    }
    setAuthResult(null)
    try {
      const endpoint = authMode === 'register' ? '/api/auth/register' : '/api/auth/login'
      const res = await fetch(`${API_BASE}${endpoint}?username=${encodeURIComponent(authUsername)}`)
      const data = await res.json()
      if (res.ok) {
        if (authMode === 'register' && data.api_key) {
          localStorage.setItem('go2se_api_key', data.api_key)
          localStorage.setItem('go2se_username', data.username)
          setApiKey(data.api_key)
          setAuthUser(data.username)
          setAuthResult(`✅ 注册成功! API密钥已保存`)
        } else if (authMode === 'login') {
          setAuthResult(`ℹ️ 用户: ${data.username} | 前缀: ${data.api_key_prefix} | 请使用完整密钥`)
        }
      } else {
        setAuthResult(`❌ ${data.detail}`)
      }
    } catch {
      setAuthResult('❌ 网络错误')
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('go2se_api_key')
    localStorage.removeItem('go2se_username')
    setApiKey(null)
    setAuthUser(null)
    setAuthResult(null)
  }

  // ── Backtest Handler ───────────────────────────────────────────
  const runBacktest = async () => {
    if (!apiKey) {
      setBacktestResult({ error: '请先在右上角登录获取API密钥' })
      return
    }
    setBacktestLoading(true)
    setBacktestResult(null)
    try {
      const params = new URLSearchParams({
        symbol: backtestParams.symbol,
        start_date: backtestParams.start_date,
        end_date: backtestParams.end_date,
        initial_capital: String(backtestParams.initial_capital),
        stop_loss: String(backtestParams.stop_loss),
        take_profit: String(backtestParams.take_profit),
        position_size: String(backtestParams.position_size),
        strategy: backtestParams.strategy
      })
      const res = await fetch(`${API_BASE}/api/backtest?${params}`, {
        headers: { 'Authorization': `Bearer ${apiKey}` }
      })
      const data = await res.json()
      if (res.ok) {
        setBacktestResult(data.data)
      } else {
        setBacktestResult({ error: data.detail || '回测失败' })
      }
    } catch {
      setBacktestResult({ error: '网络错误' })
    } finally {
      setBacktestLoading(false)
    }
  }

  const fetchBacktestHistory = async () => {
    if (!apiKey) return
    try {
      const res = await fetch(`${API_BASE}/api/backtest/history?limit=10`, {
        headers: { 'Authorization': `Bearer ${apiKey}` }
      })
      if (res.ok) {
        const data = await res.json()
        setBacktestHistory(data.data || [])
      }
    } catch {}
  }

  // ── Theme Effect ──────────────────────────────────────────────
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('go2se-theme', theme)
  }, [theme])

  // ── WebSocket Connection ────────────────────────────────────────
  useEffect(() => {
    let ws: WebSocket | null = null
    let reconnectTimer: ReturnType<typeof setTimeout>

    const connect = () => {
      const wsUrl = `ws://${API_BASE.replace('http://', '')}/api/ws`
      ws = new WebSocket(wsUrl)
      ws.onopen = () => {
        setWsConnected(true)
        console.log('🪿 WebSocket connected')
      }
      ws.onclose = () => {
        setWsConnected(false)
        reconnectTimer = setTimeout(connect, 5000)
      }
      ws.onerror = () => ws?.close()
      ws.onmessage = (e) => {
        try {
          const msg = JSON.parse(e.data)
          if (msg.type === 'pong') return
          console.log('WS msg:', msg.type)
        } catch {}
      }
    }

    connect()
    return () => {
      clearTimeout(reconnectTimer)
      ws?.close()
    }
  }, [])

  // ── Trade Handler ──────────────────────────────────────────────
  const handleTrade = async () => {
    if (!tradeAmount || isNaN(Number(tradeAmount)) || Number(tradeAmount) <= 0) {
      setTradeResult('❌ 请输入有效数量')
      return
    }
    setTradeLoading(true)
    setTradeResult(null)
    try {
      const res = await fetch(`${API_BASE}/api/trade`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol: tradeSymbol,
          side: tradeSide,
          amount: Number(tradeAmount),
          strategy: 'manual'
        })
      })
      const data = await res.json()
      setTradeResult(data.result?.pnl !== undefined
        ? `✅ ${tradeSide === 'buy' ? '买入' : '卖出'} ${tradeSymbol} × ${tradeAmount}`
        : `❌ ${data.error || '交易失败'}`
      )
      if (res.ok) {
        setTradeAmount('')
        fetchData(true)
      }
    } catch {
      setTradeResult('❌ 网络错误')
    } finally {
      setTradeLoading(false)
    }
  }

  // Page Visibility API - 标签页隐藏时暂停/降低刷新频率
  useEffect(() => {
    let interval: ReturnType<typeof setInterval>
    let hiddenInterval: ReturnType<typeof setInterval>

    const startPolling = () => {
      fetchData()
      interval = setInterval(fetchData, 15000) // 活跃标签页: 15秒
    }

    const startBackgroundPolling = () => {
      // 后台/隐藏: 60秒降频刷新（节省资源）
      hiddenInterval = setInterval(fetchData, 60000)
    }

    const handleVisibilityChange = () => {
      if (document.hidden) {
        // 标签页隐藏: 停止活跃轮询，切换到后台模式
        clearInterval(interval)
        clearInterval(hiddenInterval)
        startBackgroundPolling()
      } else {
        // 标签页恢复: 立即刷新一次，再恢复活跃轮询
        clearInterval(interval)
        clearInterval(hiddenInterval)
        fetchData()
        startPolling()
      }
    }

    document.addEventListener('visibilitychange', handleVisibilityChange)
    startPolling()

    return () => {
      clearInterval(interval)
      clearInterval(hiddenInterval)
      document.removeEventListener('visibilitychange', handleVisibilityChange)
    }
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
    return (
      <ErrorBoundary>
        <div className="loading">🪿 加载中...</div>
        <LoadingSkeleton tab={activeTab} />
      </ErrorBoundary>
    )
  }

  const portfolioList = portfolio?.performance?.portfolio ? Object.values(portfolio.performance.portfolio) : []

  return (
    <ErrorBoundary>
    <div className="app">
      <header className="header">
        <h1>🪿 GO2SE 量化交易平台</h1>
        <div className="status">
          <span className={`ws-status ${wsConnected ? 'ws-on' : 'ws-off'}`} title={wsConnected ? '实时推送已连接' : '实时推送未连接'}>
            {wsConnected ? '🟢' : '🔴'}
          </span>
          <span className="mode">模式: {stats.trading_mode || 'dry_run'}</span>
          <span className="position">仓位: {(stats.max_position || 0) * 100}%</span>
          {apiErrors.length > 0 && (
            <span className="error-badge" title={`API错误: ${apiErrors.join(',')}`}>⚠️</span>
          )}
          <button
            className="theme-btn"
            onClick={() => setTheme(t => t === 'dark' ? 'light' : 'dark')}
            title={theme === 'dark' ? '切换亮色模式' : '切换暗色模式'}
          >
            {theme === 'dark' ? '🌙' : '☀️'}
          </button>
          <button
            className="trade-btn"
            onClick={() => setShowTradePanel(p => !p)}
            title="交易面板"
          >
            💱
          </button>
          <button
            className="auth-btn"
            onClick={() => { setShowAuthPanel(a => !a); setAuthResult(null) }}
            title={apiKey ? `已登录: ${authUser}` : '登录/注册'}
          >
            {apiKey ? '🔑' : '⚪'}
          </button>
          <RefreshButton onRefresh={() => fetchData(true)} />
          {isRefreshing && <span className="refreshing">⟳</span>}
        </div>
      </header>

      {/* ── Auth Panel ───────────────────────────────────────────── */}
      {showAuthPanel && (
        <div className="trade-panel">
          <div className="trade-panel-header">
            <span>{apiKey ? `🔑 ${authUser}` : '登录 / 注册'}</span>
            <button className="close-btn" onClick={() => setShowAuthPanel(false)}>✕</button>
          </div>
          {apiKey ? (
            <div className="auth-logged-in">
              <div className="auth-info">已作为 <b>{authUser}</b> 登录</div>
              <div className="auth-key-display">密钥: <code>{apiKey.slice(0, 20)}...</code></div>
              <button className="logout-btn" onClick={handleLogout}>退出登录</button>
              <button className="history-btn" onClick={() => { fetchBacktestHistory(); setActiveTab('backtest') }}>
                📊 回测历史
              </button>
            </div>
          ) : (
            <div className="trade-form">
              <div className="trade-symbol-row">
                <label>用户名</label>
                <input
                  type="text"
                  className="trade-input"
                  value={authUsername}
                  onChange={e => setAuthUsername(e.target.value)}
                  placeholder="输入用户名"
                />
              </div>
              <div className="trade-side-row">
                <button
                  className={`side-btn ${authMode === 'register' ? 'buy-active' : ''}`}
                  onClick={() => { setAuthMode('register'); setAuthResult(null) }}
                >📝 注册</button>
                <button
                  className={`side-btn ${authMode === 'login' ? 'buy-active' : ''}`}
                  onClick={() => { setAuthMode('login'); setAuthResult(null) }}
                >🔐 登录</button>
              </div>
              <button className="trade-submit buy-submit" onClick={handleAuth}>
                {authMode === 'register' ? '注册并获取密钥' : '登录'}
              </button>
              {authResult && (
                <div className={`trade-result ${authResult.startsWith('✅') ? 'trade-success' : 'trade-error'}`}>
                  {authResult}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* ── Trade Panel ─────────────────────────────────────────── */}
      {showTradePanel && (
        <div className="trade-panel">
          <div className="trade-panel-header">
            <span>💱 交易面板</span>
            <button className="close-btn" onClick={() => setShowTradePanel(false)}>✕</button>
          </div>
          <div className="trade-form">
            <div className="trade-symbol-row">
              <label>交易对</label>
              <select
                value={tradeSymbol}
                onChange={e => setTradeSymbol(e.target.value)}
                className="trade-select"
              >
                {(markets.length ? markets : [
                  { symbol: 'BTC/USDT' }, { symbol: 'ETH/USDT' }, { symbol: 'SOL/USDT' }
                ]).map(m => (
                  <option key={m.symbol} value={m.symbol}>{m.symbol.replace('/USDT', '')}</option>
                ))}
              </select>
            </div>
            <div className="trade-side-row">
              <button
                className={`side-btn ${tradeSide === 'buy' ? 'buy-active' : ''}`}
                onClick={() => setTradeSide('buy')}
              >🟢 买入</button>
              <button
                className={`side-btn ${tradeSide === 'sell' ? 'sell-active' : ''}`}
                onClick={() => setTradeSide('sell')}
              >🔴 卖出</button>
            </div>
            <div className="trade-amount-row">
              <label>数量 (USDT)</label>
              <input
                type="number"
                className="trade-input"
                value={tradeAmount}
                onChange={e => setTradeAmount(e.target.value)}
                placeholder="输入数量"
                min="0"
              />
            </div>
            <button
              className={`trade-submit ${tradeSide === 'buy' ? 'buy-submit' : 'sell-submit'}`}
              onClick={handleTrade}
              disabled={tradeLoading || !tradeAmount}
            >
              {tradeLoading ? '⟳ 执行中...' : tradeSide === 'buy' ? '✅ 买入' : '✅ 卖出'}
            </button>
            {tradeResult && (
              <div className={`trade-result ${tradeResult.startsWith('✅') ? 'trade-success' : 'trade-error'}`}>
                {tradeResult}
              </div>
            )}
            <div className="trade-note">⚠️ 仅模拟交易，风险自担</div>
          </div>
        </div>
      )}

      <nav className="nav">
        {[
          { key: 'market', label: '📊 市场' },
          { key: 'signals', label: '🎯 信号' },
          { key: 'portfolio', label: '💼 组合' },
          { key: 'trades', label: '📈 统计' },
          { key: 'backtest', label: '🧪 回测' },
        ].map(tab => (
          <button
            key={tab.key}
            className={activeTab === tab.key ? 'active' : ''}
            onClick={() => setActiveTab(tab.key as TabKey)}
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
                <div className="spread">
                  差价: {((market as any).ask - (market as any).bid)?.toFixed(2) || '--'}
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

        {activeTab === 'backtest' && (
          <div className="backtest-panel">
            {!apiKey && (
              <div className="auth-required">
                <div className="auth-icon">🔑</div>
                <div className="auth-title">需要API密钥</div>
                <div className="auth-desc">请先在右上角登录/注册获取API密钥</div>
                <button className="trade-submit buy-submit" onClick={() => setShowAuthPanel(true)}>
                  去登录
                </button>
              </div>
            )}
            {apiKey && (
              <>
                <div className="backtest-form">
                  <div className="bf-row">
                    <div className="bf-field">
                      <label>交易对</label>
                      <select className="trade-select" value={backtestParams.symbol}
                        onChange={e => setBacktestParams(p => ({...p, symbol: e.target.value}))}>
                        <option>BTC/USDT</option>
                        <option>ETH/USDT</option>
                        <option>SOL/USDT</option>
                        <option>XRP/USDT</option>
                      </select>
                    </div>
                    <div className="bf-field">
                      <label>策略</label>
                      <select className="trade-select" value={backtestParams.strategy}
                        onChange={e => setBacktestParams(p => ({...p, strategy: e.target.value}))}>
                        <option value="rsi_macross">RSI+均线</option>
                        <option value="rsi_extreme">RSI极端值</option>
                        <option value="macd_cross">MACD交叉</option>
                      </select>
                    </div>
                    <div className="bf-field">
                      <label>初始资金 ($)</label>
                      <input type="number" className="trade-input" value={backtestParams.initial_capital}
                        onChange={e => setBacktestParams(p => ({...p, initial_capital: Number(e.target.value)}))} />
                    </div>
                  </div>
                  <div className="bf-row">
                    <div className="bf-field">
                      <label>开始日期</label>
                      <input type="date" className="trade-input" value={backtestParams.start_date}
                        onChange={e => setBacktestParams(p => ({...p, start_date: e.target.value}))} />
                    </div>
                    <div className="bf-field">
                      <label>结束日期</label>
                      <input type="date" className="trade-input" value={backtestParams.end_date}
                        onChange={e => setBacktestParams(p => ({...p, end_date: e.target.value}))} />
                    </div>
                    <div className="bf-field">
                      <label>止损 %</label>
                      <input type="number" step="0.01" className="trade-input" value={backtestParams.stop_loss}
                        onChange={e => setBacktestParams(p => ({...p, stop_loss: Number(e.target.value)}))} />
                    </div>
                    <div className="bf-field">
                      <label>止盈 %</label>
                      <input type="number" step="0.01" className="trade-input" value={backtestParams.take_profit}
                        onChange={e => setBacktestParams(p => ({...p, take_profit: Number(e.target.value)}))} />
                    </div>
                  </div>
                  <button className="trade-submit buy-submit" onClick={runBacktest} disabled={backtestLoading}>
                    {backtestLoading ? '⟳ 回测中...' : '▶ 运行回测'}
                  </button>
                </div>

                {backtestResult && (
                  <div className="backtest-result">
                    {backtestResult.error ? (
                      <div className="trade-error">{backtestResult.error}</div>
                    ) : (
                      <>
                        <div className="result-stats">
                          <div className="stat-card">
                            <div className="stat-value" style={{color: backtestResult.total_return >= 0 ? 'var(--success)' : 'var(--danger)'}}>
                              {backtestResult.total_return >= 0 ? '+' : ''}{backtestResult.total_return}%
                            </div>
                            <div className="stat-label">总收益</div>
                          </div>
                          <div className="stat-card">
                            <div className="stat-value">{backtestResult.win_rate}%</div>
                            <div className="stat-label">胜率</div>
                          </div>
                          <div className="stat-card">
                            <div className="stat-value">{backtestResult.total_trades}</div>
                            <div className="stat-label">交易次数</div>
                          </div>
                          <div className="stat-card">
                            <div className="stat-value">{backtestResult.max_drawdown}%</div>
                            <div className="stat-label">最大回撤</div>
                          </div>
                          <div className="stat-card">
                            <div className="stat-value">{backtestResult.sharpe_ratio}</div>
                            <div className="stat-label">夏普比率</div>
                          </div>
                          <div className="stat-card">
                            <div className="stat-value">${backtestResult.final_capital}</div>
                            <div className="stat-label">最终资金</div>
                          </div>
                        </div>
                        {backtestResult.trades?.length > 0 && (
                          <div className="bt-trades">
                            <h4>📋 最近交易</h4>
                            <table className="bt-table">
                              <thead><tr><th>#</th><th>时间</th><th>方向</th><th>价格</th><th>数量</th><th>盈亏</th><th>说明</th></tr></thead>
                              <tbody>
                                {backtestResult.trades.map((t: any) => (
                                  <tr key={t.index}>
                                    <td>{t.index}</td>
                                    <td>{new Date(t.t * 1000).toLocaleDateString()}</td>
                                    <td className={t.side === 'buy' ? 'up' : 'down'}>{t.side === 'buy' ? '🟢买入' : '🔴卖出'}</td>
                                    <td>${t.price?.toFixed(2)}</td>
                                    <td>{t.amount}</td>
                                    <td className={t.pnl >= 0 ? 'up' : 'down'}>{t.pnl >= 0 ? '+' : ''}{t.pnl}</td>
                                    <td>{t.reason}</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        )}
                      </>
                    )}
                  </div>
                )}

                {backtestHistory.length > 0 && (
                  <div className="bt-history">
                    <h4>📜 回测历史</h4>
                    <table className="bt-table">
                      <thead><tr><th>交易对</th><th>策略</th><th>收益</th><th>胜率</th><th>最大回撤</th><th>夏普</th><th>日期</th></tr></thead>
                      <tbody>
                        {backtestHistory.map((h: any) => (
                          <tr key={h.id}>
                            <td>{h.symbol}</td>
                            <td>{h.params?.strategy}</td>
                            <td className={h.total_return >= 0 ? 'up' : 'down'}>{h.total_return >= 0 ? '+' : ''}{h.total_return}%</td>
                            <td>{h.win_rate}%</td>
                            <td>{h.max_drawdown}%</td>
                            <td>{h.sharpe_ratio}</td>
                            <td>{new Date(h.created_at).toLocaleDateString()}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </main>

      <footer className="footer">
        <span>🪿 GO2SE v6.3.2</span>
        <span>•</span>
        <span>更新: {lastUpdate.toLocaleTimeString()}</span>
        <span>•</span>
        <span className={stats.trading_mode === 'live' ? 'live-mode' : 'dry-mode'}>
          {stats.trading_mode === 'live' ? '🔴 实盘' : '🟡 模拟'}
        </span>
      </footer>
    </div>
    </ErrorBoundary>
  )
}

export default App
