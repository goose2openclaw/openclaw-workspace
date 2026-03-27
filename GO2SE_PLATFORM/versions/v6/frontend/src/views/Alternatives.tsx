/**
 * 🪿 Alternatives - 备选策略页
 * 支持多策略对比与选择
 */

import { useState, useEffect } from 'react'

interface Strategy {
  id: string
  name: string
  type: string
  description: string
  source: string
  enabled: boolean
  allocation: number
  priority: number
  capital_ratio: number
}

interface BacktestResult {
  id: string
  name: string
  return_pct: number
  max_drawdown_pct: number
  win_rate?: number
  total_trades?: number
  source: string
}

export function Alternatives() {
  const [strategies, setStrategies] = useState<Strategy[]>([])
  const [expertMode, setExpertMode] = useState(false)
  const [loading, setLoading] = useState(true)
  const [results, setResults] = useState<BacktestResult[]>([])
  const [comparing, setComparing] = useState(false)

  useEffect(() => {
    fetchStrategies()
  }, [])

  const fetchStrategies = async () => {
    try {
      const res = await fetch('http://localhost:5000/api/alternatives/strategies')
      const data = await res.json()
      setStrategies(data.strategies || [])
      setExpertMode(data.expert_mode || false)
    } catch (e) {
      console.error('Failed to fetch strategies:', e)
    } finally {
      setLoading(false)
    }
  }

  const enableStrategy = async (id: string) => {
    try {
      await fetch('http://localhost:5000/api/alternatives/enable', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          strategy_id: id, 
          allocation: 0.1, 
          priority: 5, 
          capital_ratio: 0.1 
        })
      })
      fetchStrategies()
    } catch (e) {
      console.error('Failed to enable strategy:', e)
    }
  }

  const disableStrategy = async (id: string) => {
    try {
      await fetch(`http://localhost:5000/api/alternatives/disable?strategy_id=${id}`, {
        method: 'POST'
      })
      fetchStrategies()
    } catch (e) {
      console.error('Failed to disable strategy:', e)
    }
  }

  const runComparison = async () => {
    setComparing(true)
    try {
      const res = await fetch('http://localhost:5000/api/alternatives/compare')
      const data = await res.json()
      setResults(data.rankings || [])
    } catch (e) {
      console.error('Failed to compare:', e)
    } finally {
      setComparing(false)
    }
  }

  const toggleExpertMode = async () => {
    try {
      await fetch('http://localhost:5000/api/alternatives/expert-mode', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled: !expertMode })
      })
      setExpertMode(!expertMode)
    } catch (e) {
      console.error('Failed to toggle expert mode:', e)
    }
  }

  const enabledCount = strategies.filter(s => s.enabled).length
  const totalAllocation = strategies.filter(s => s.enabled).reduce((a, s) => a + s.allocation, 0)

  const typeColors: Record<string, string> = {
    quant: '#10B981',
    ML: '#7C3AED',
    arb: '#F59E0B',
    indicator: '#3B82F6',
    prediction: '#EC4899',
    analytics: '#14B8A6'
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', animation: 'fadeInUp 0.4s ease' }}>
      
      {/* 头部控制 */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ margin: 0, fontSize: '24px' }}>🧩 备选策略</h2>
          <p style={{ margin: '4px 0 0', color: '#888' }}>接入第三方策略作为北斗七鑫的补充</p>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button 
            onClick={toggleExpertMode}
            style={{
              padding: '8px 16px',
              borderRadius: '8px',
              border: expertMode ? '2px solid #10B981' : '2px solid #333',
              background: expertMode ? 'rgba(16,185,129,0.1)' : 'transparent',
              color: expertMode ? '#10B981' : '#888',
              cursor: 'pointer',
              fontWeight: 500
            }}
          >
            {expertMode ? '🎓 专家模式' : '📖 普通模式'}
          </button>
          <button 
            onClick={runComparison}
            disabled={comparing}
            style={{
              padding: '8px 16px',
              borderRadius: '8px',
              border: 'none',
              background: comparing ? '#666' : 'linear-gradient(135deg, #7C3AED, #3B82F6)',
              color: 'white',
              cursor: comparing ? 'not-allowed' : 'pointer',
              fontWeight: 500
            }}
          >
            {comparing ? '🔄 对比中...' : '⚡ 对比回测'}
          </button>
        </div>
      </div>

      {/* 统计概览 */}
      <div className="stats-row">
        <div className="stat-card">
          <div className="stat-label">📦 策略总数</div>
          <div className="stat-value">{strategies.length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">✅ 已启用</div>
          <div className="stat-value gradient-text">{enabledCount}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">💾 总算力</div>
          <div className="stat-value">{totalAllocation > 0 ? `${(totalAllocation * 100).toFixed(0)}%` : '-'}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">🏆 最佳策略</div>
          <div className="stat-value">{results[0]?.name || '-'}</div>
        </div>
      </div>

      {/* 对比结果 */}
      {results.length > 0 && (
        <div className="content-card" style={{ animation: 'fadeIn 0.3s ease' }}>
          <h3 style={{ margin: '0 0 16px' }}>📊 回测对比结果</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px' }}>
            {results.map((r, i) => (
              <div 
                key={r.id}
                style={{
                  padding: '16px',
                  borderRadius: '12px',
                  background: i === 0 ? 'rgba(16,185,129,0.1)' : 'rgba(255,255,255,0.03)',
                  border: i === 0 ? '2px solid #10B981' : '1px solid #333',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                  <span style={{ fontSize: '20px' }}>{i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : '  '}</span>
                  <span style={{ fontWeight: 600 }}>{r.name}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px', color: '#888' }}>
                  <span>收益:</span>
                  <span style={{ color: r.return_pct >= 0 ? '#10B981' : '#EF4444' }}>
                    {r.return_pct >= 0 ? '+' : ''}{r.return_pct.toFixed(2)}%
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px', color: '#888' }}>
                  <span>回撤:</span>
                  <span style={{ color: '#F59E0B' }}>{r.max_drawdown_pct.toFixed(2)}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 策略列表 */}
      <div className="content-card">
        <h3 style={{ margin: '0 0 16px' }}>🧩 备选策略列表</h3>
        
        {loading ? (
          <div style={{ textAlign: 'center', padding: '40px', color: '#888' }}>加载中...</div>
        ) : (
          <div style={{ display: 'grid', gap: '12px' }}>
            {strategies.map((strategy) => (
              <div 
                key={strategy.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '16px 20px',
                  borderRadius: '12px',
                  background: strategy.enabled ? 'rgba(16,185,129,0.05)' : 'rgba(255,255,255,0.02)',
                  border: strategy.enabled ? '1px solid rgba(16,185,129,0.3)' : '1px solid #333',
                  transition: 'all 0.2s ease'
                }}
              >
                {/* 左侧: 策略信息 */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                  <div 
                    style={{
                      width: '48px',
                      height: '48px',
                      borderRadius: '12px',
                      background: typeColors[strategy.type] || '#666',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '24px'
                    }}
                  >
                    {strategy.type === 'quant' ? '📊' : 
                     strategy.type === 'ML' ? '🤖' : 
                     strategy.type === 'arb' ? '⚖️' :
                     strategy.type === 'prediction' ? '🔮' :
                     strategy.type === 'analytics' ? '🔗' : '📈'}
                  </div>
                  
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontWeight: 600, fontSize: '16px' }}>{strategy.name}</span>
                      <span style={{ 
                        fontSize: '12px', 
                        padding: '2px 8px', 
                        borderRadius: '4px',
                        background: strategy.source === 'local' ? 'rgba(59,130,246,0.2)' : 'rgba(139,92,246,0.2)',
                        color: strategy.source === 'local' ? '#3B82F6' : '#8B5CF6'
                      }}>
                        {strategy.source === 'local' ? '本地' : 'GitHub'}
                      </span>
                    </div>
                    <div style={{ fontSize: '13px', color: '#888', marginTop: '2px' }}>
                      {strategy.description}
                    </div>
                  </div>
                </div>

                {/* 中间: 专家模式参数 */}
                {expertMode && strategy.enabled && (
                  <div style={{ display: 'flex', gap: '24px', fontSize: '13px', color: '#888' }}>
                    <div>
                      <span>算力: </span>
                      <span style={{ color: '#10B981' }}>{(strategy.allocation * 100).toFixed(0)}%</span>
                    </div>
                    <div>
                      <span>优先级: </span>
                      <span style={{ color: '#F59E0B' }}>{strategy.priority}</span>
                    </div>
                    <div>
                      <span>资金: </span>
                      <span style={{ color: '#7C3AED' }}>{(strategy.capital_ratio * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                )}

                {/* 右侧: 操作 */}
                <div>
                  <button
                    onClick={() => strategy.enabled ? disableStrategy(strategy.id) : enableStrategy(strategy.id)}
                    style={{
                      padding: '8px 20px',
                      borderRadius: '8px',
                      border: 'none',
                      background: strategy.enabled 
                        ? 'linear-gradient(135deg, #EF4444, #DC2626)' 
                        : 'linear-gradient(135deg, #10B981, #059669)',
                      color: 'white',
                      cursor: 'pointer',
                      fontWeight: 500,
                      transition: 'transform 0.1s ease'
                    }}
                  >
                    {strategy.enabled ? '禁用' : '启用'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 策略类型说明 */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '12px' }}>
        {Object.entries(typeColors).map(([type, color]) => (
          <div key={type} style={{ 
            padding: '12px', 
            borderRadius: '8px', 
            background: 'rgba(255,255,255,0.03)',
            border: '1px solid #333',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <div style={{ width: '12px', height: '12px', borderRadius: '3px', background: color }} />
            <span style={{ fontSize: '13px', color: '#888' }}>
              {type === 'quant' ? '量化' : 
               type === 'ML' ? '机器学习' : 
               type === 'arb' ? '套利' :
               type === 'prediction' ? '预测' :
               type === 'analytics' ? '分析' : type}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
