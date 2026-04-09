/**
 * 🪿 Strategies - 策略页
 * 7大投资工具管理
 */

import { useState } from 'react'

const strategies = [
  { id: 'rabbit', name: '打兔子', icon: '🐰', weight: 25, status: 'active', pnl: 125.50, trades: 12, desc: 'Top20趋势追踪', color: '#10B981' },
  { id: 'mole', name: '打地鼠', icon: '🐹', weight: 20, status: 'active', pnl: -32.80, trades: 8, desc: '高波动套利', color: '#F59E0B' },
  { id: 'oracle', name: '走着燋', icon: '🔮', weight: 15, status: 'active', pnl: 45.20, trades: 5, desc: '预测市场', color: '#7C3AED' },
  { id: 'leader', name: '跟大哥', icon: '👑', weight: 15, status: 'paused', pnl: 0, trades: 0, desc: '做市协作', color: '#3B82F6' },
  { id: 'hitchhiker', name: '搭便车', icon: '🍀', weight: 10, status: 'active', pnl: 28.90, trades: 15, desc: '跟单分成', color: '#EC4899' },
  { id: 'airdrop', name: '薅羊毛', icon: '💰', weight: 3, status: 'active', pnl: 156.00, trades: 23, desc: '新币空投', color: '#14B8A6' },
  { id: 'crowdsource', name: '穷孩子', icon: '👶', weight: 2, status: 'active', pnl: 12.50, trades: 6, desc: '众包任务', color: '#8B5CF6' },
]

export function Strategies() {
  const [selected, setSelected] = useState<string | null>(null)
  const totalPnl = strategies.reduce((a, s) => a + s.pnl, 0)
  const totalTrades = strategies.reduce((a, s) => a + s.trades, 0)
  const activeCount = strategies.filter(s => s.status === 'active').length

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', animation: 'fadeInUp 0.4s ease' }}>
      
      {/* 统计概览 */}
      <div className="stats-row">
        <div className="stat-card">
          <div className="stat-label">📈 今日盈亏</div>
          <div className={`stat-value ${totalPnl >= 0 ? 'positive' : 'negative'}`}>
            {totalPnl >= 0 ? '+' : ''}{totalPnl.toFixed(2)} USDT
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">🎯 交易次数</div>
          <div className="stat-value">{totalTrades}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">⚡ 活跃策略</div>
          <div className="stat-value">{activeCount}/7</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">💰 总会力</div>
          <div className="stat-value gradient-text">100%</div>
        </div>
      </div>

      {/* 算力分配 */}
      <div className="content-card">
        <div className="card-header">
          <h3 className="card-title">⚖️ 算力分配</h3>
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
            💾 保存配置
          </button>
        </div>
        <div className="card-body">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {strategies.map((s, i) => (
              <div key={s.id} style={{
                display: 'flex',
                alignItems: 'center',
                gap: '16px',
                padding: '16px 20px',
                background: selected === s.id ? `${s.color}15` : 'var(--bg-tertiary)',
                borderRadius: '14px',
                border: `1px solid ${selected === s.id ? s.color : 'var(--border)'}`,
                cursor: 'pointer',
                transition: 'all 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
                animation: `slideIn 0.3s ease ${i * 0.05}s`,
              }}
              onClick={() => setSelected(s.id)}
              onMouseOver={(e) => {
                e.currentTarget.style.transform = 'translateX(8px)'
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.transform = 'translateX(0)'
              }}
              >
                <span style={{ fontSize: '2rem', filter: 'drop-shadow(0 4px 8px rgba(0,0,0,0.2))' }}>{s.icon}</span>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                    <span style={{ fontWeight: 700, fontSize: '1rem' }}>{s.name}</span>
                    <span className={`tag ${s.status === 'active' ? 'tag-success' : 'tag-neutral'}`}>
                      {s.status === 'active' ? '运行中' : '暂停'}
                    </span>
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginBottom: '8px' }}>{s.desc}</div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{ flex: 1, height: '8px', background: 'var(--bg-secondary)', borderRadius: '4px', overflow: 'hidden' }}>
                      <div style={{ 
                        width: `${s.weight}%`, 
                        height: '100%', 
                        background: `linear-gradient(90deg, ${s.color}, ${s.color}80)`,
                        borderRadius: '4px',
                        transition: 'width 0.5s ease',
                      }} />
                    </div>
                    <span style={{ fontFamily: 'monospace', fontWeight: 700, color: s.color, minWidth: '45px' }}>{s.weight}%</span>
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontFamily: 'monospace', fontWeight: 700, fontSize: '1.125rem', color: s.pnl >= 0 ? '#10B981' : '#EF4444' }}>
                    {s.pnl >= 0 ? '+' : ''}{s.pnl.toFixed(2)}
                  </div>
                  <div style={{ fontSize: '0.6875rem', color: 'var(--text-tertiary)' }}>{s.trades}笔</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 策略详情 */}
      {selected && (
        <div className="content-card" style={{ animation: 'fadeInUp 0.3s ease' }}>
          <div className="card-header">
            <h3 className="card-title">
              {strategies.find(s => s.id === selected)?.icon} {strategies.find(s => s.id === selected)?.name} - 详情
            </h3>
            <button 
              onClick={() => setSelected(null)}
              style={{
                padding: '8px 16px',
                borderRadius: '8px',
                border: 'none',
                background: 'var(--bg-tertiary)',
                color: 'var(--text-secondary)',
                fontSize: '0.8125rem',
                cursor: 'pointer',
              }}
            >
              ✕ 关闭
            </button>
          </div>
          <div className="card-body">
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px' }}>
              {[
                { l: '今日盈亏', v: '+125.50 USDT', c: '#10B981' },
                { l: '交易次数', v: '12 次', c: 'var(--text-primary)' },
                { l: '胜率', v: '75%', c: 'var(--accent)' },
                { l: '平均持仓', v: '2.5h', c: 'var(--text-secondary)' },
              ].map((item, i) => (
                <div key={i} style={{ 
                  padding: '20px', 
                  background: 'var(--bg-tertiary)', 
                  borderRadius: '12px',
                  textAlign: 'center',
                }}>
                  <div style={{ fontSize: '0.8125rem', color: 'var(--text-tertiary)', marginBottom: '8px' }}>{item.l}</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 700, color: item.c }}>{item.v}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

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
