/**
 * 🪿 Signals - 信号页
 * AI智能信号分析
 */

import { useStore } from '../stores/appStore'

export function Signals() {
  const { signals } = useStore()
  
  const buySignals = signals.filter(s => s.signal === 'buy')
  const sellSignals = signals.filter(s => s.signal === 'sell')
  const holdSignals = signals.filter(s => s.signal === 'hold')

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', animation: 'fadeInUp 0.4s ease' }}>
      
      {/* 信号统计 */}
      <div className="stats-row">
        <div className="stat-card" style={{ borderColor: '#10B981' }}>
          <div className="stat-label">🟢 买入信号</div>
          <div className="stat-value" style={{ color: '#10B981' }}>{buySignals.length}</div>
        </div>
        <div className="stat-card" style={{ borderColor: '#F59E0B' }}>
          <div className="stat-label">🟡 观望信号</div>
          <div className="stat-value" style={{ color: '#F59E0B' }}>{holdSignals.length}</div>
        </div>
        <div className="stat-card" style={{ borderColor: '#EF4444' }}>
          <div className="stat-label">🔴 卖出信号</div>
          <div className="stat-value" style={{ color: '#EF4444' }}>{sellSignals.length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">📡 总信号数</div>
          <div className="stat-value">{signals.length}</div>
        </div>
      </div>

      {/* AI分析面板 */}
      <div className="content-card">
        <div className="card-header">
          <h3 className="card-title">🤖 AI深度分析</h3>
          <button style={{
            padding: '8px 16px',
            borderRadius: '8px',
            border: 'none',
            background: 'var(--accent)',
            color: '#ffffff',
            fontSize: '0.8125rem',
            fontWeight: 500,
            cursor: 'pointer',
          }}>
            🔄 重新分析
          </button>
        </div>
        <div className="card-body">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
            {[
              { icon: '📊', title: '市场情绪', value: '偏多', color: '#10B981', desc: '多头趋势明显' },
              { icon: '🎯', title: '置信度', value: '7.5', color: 'var(--accent)', desc: '建议执行' },
              { icon: '⏰', title: '建议操作', value: '买入', color: '#10B981', desc: '最佳入场点' },
            ].map((item, i) => (
              <div key={i} style={{
                padding: '20px',
                background: 'var(--bg-tertiary)',
                borderRadius: '14px',
                border: '1px solid var(--border)',
                textAlign: 'center',
                transition: 'all 0.3s ease',
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.borderColor = item.color
                e.currentTarget.style.transform = 'translateY(-4px)'
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.borderColor = 'var(--border)'
                e.currentTarget.style.transform = 'translateY(0)'
              }}
              >
                <div style={{ fontSize: '1.75rem', marginBottom: '10px' }}>{item.icon}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginBottom: '4px' }}>{item.title}</div>
                <div style={{ fontSize: '1.375rem', fontWeight: 800, color: item.color, marginBottom: '4px' }}>{item.value}</div>
                <div style={{ fontSize: '0.6875rem', color: 'var(--text-tertiary)' }}>{item.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 信号列表 */}
      <div className="content-card">
        <div className="card-header">
          <h3 className="card-title">🎯 实时信号</h3>
          <div style={{ display: 'flex', gap: '8px' }}>
            {['全部', '买入', '观望', '卖出'].map((f, i) => (
              <button key={f} style={{
                padding: '6px 14px',
                borderRadius: '16px',
                border: 'none',
                background: i === 0 ? 'var(--accent)' : 'var(--bg-tertiary)',
                color: i === 0 ? '#ffffff' : 'var(--text-secondary)',
                fontSize: '0.75rem',
                fontWeight: 500,
                cursor: 'pointer',
              }}>
                {f}
              </button>
            ))}
          </div>
        </div>
        <div className="card-body" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {signals.map((s, i) => (
            <div key={i} style={{
              display: 'flex',
              alignItems: 'center',
              gap: '16px',
              padding: '18px 20px',
              background: 'var(--bg-tertiary)',
              borderRadius: '14px',
              border: '1px solid var(--border)',
              transition: 'all 0.3s ease',
              animation: `slideIn 0.3s ease ${i * 0.05}s`,
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.borderColor = s.signal === 'buy' ? '#10B981' : s.signal === 'sell' ? '#EF4444' : '#F59E0B'
              e.currentTarget.style.transform = 'translateX(8px)'
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.borderColor = 'var(--border)'
              e.currentTarget.style.transform = 'translateX(0)'
            }}
            >
              <div style={{
                width: '48px',
                height: '48px',
                borderRadius: '12px',
                background: s.signal === 'buy' ? 'rgba(16, 185, 129, 0.15)' : s.signal === 'sell' ? 'rgba(239, 68, 68, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '1.5rem',
              }}>
                {s.signal === 'buy' ? '🟢' : s.signal === 'sell' ? '🔴' : '🟡'}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                  <span style={{ fontWeight: 700, fontSize: '1.125rem', fontFamily: 'monospace' }}>{s.symbol}</span>
                  <span className={`tag ${
                    s.signal === 'buy' ? 'tag-success' : s.signal === 'sell' ? 'tag-danger' : 'tag-warning'
                  }`}>
                    {s.signal === 'buy' ? '买入' : s.signal === 'sell' ? '卖出' : '观望'}
                  </span>
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>{s.strategy}</div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ 
                  fontFamily: 'monospace', 
                  fontWeight: 700, 
                  fontSize: '1.25rem',
                  color: s.confidence && s.confidence >= 7 ? 'var(--accent)' : 'var(--text-secondary)'
                }}>
                  {s.confidence?.toFixed(1) || '-'}
                </div>
                <div style={{ fontSize: '0.6875rem', color: 'var(--text-tertiary)' }}>置信度</div>
              </div>
              <button style={{
                padding: '10px 20px',
                borderRadius: '10px',
                border: 'none',
                background: s.signal === 'buy' ? '#10B981' : s.signal === 'sell' ? '#EF4444' : '#F59E0B',
                color: '#ffffff',
                fontSize: '0.8125rem',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.2s ease',
              }}
              onMouseOver={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
              onMouseOut={(e) => e.currentTarget.style.transform = 'scale(1)'}
              >
                执行
              </button>
            </div>
          ))}
          {signals.length === 0 && (
            <div style={{ textAlign: 'center', padding: '60px', color: 'var(--text-tertiary)' }}>
              <div style={{ fontSize: '3rem', marginBottom: '16px' }}>🎯</div>
              <div>暂无信号</div>
            </div>
          )}
        </div>
      </div>

      <style>{`
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes slideIn {
          from { opacity: 0; transform: translateX(-20px); }
          to { opacity: 1; transform: translateX(0); }
        }
      `}</style>
    </div>
  )
}
