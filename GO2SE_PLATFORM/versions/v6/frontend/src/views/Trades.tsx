/**
 * 🪿 Trades - 交易页
 * 持仓管理 + 历史记录
 */

import { useStore } from '../stores/appStore'

export function Trades() {
  const { trades } = useStore()

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', animation: 'fadeInUp 0.4s ease' }}>
      
      {/* 统计概览 */}
      <div className="stats-row">
        <div className="stat-card">
          <div className="stat-label">📊 持仓数量</div>
          <div className="stat-value">3</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">💵 总持仓</div>
          <div className="stat-value">$12,450</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">📈 今日盈亏</div>
          <div className="stat-value positive">+$328.50</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">🎯 历史胜率</div>
          <div className="stat-value gradient-text">78%</div>
        </div>
      </div>

      {/* 当前持仓 */}
      <div className="content-card">
        <div className="card-header">
          <h3 className="card-title">💰 当前持仓</h3>
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
            + 新建仓位
          </button>
        </div>
        <div className="card-body">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {[
              { sym: 'BTC', name: 'Bitcoin', side: 'long', qty: 0.15, price: 75234, pnl: 1250.50, pnlPct: 12.5 },
              { sym: 'ETH', name: 'Ethereum', side: 'long', qty: 2.5, price: 3456, pnl: -125.30, pnlPct: -2.1 },
              { sym: 'SOL', name: 'Solana', side: 'long', qty: 25, price: 178, pnl: 320.80, pnlPct: 7.8 },
            ].map((t, i) => (
              <div key={i} style={{
                display: 'flex',
                alignItems: 'center',
                gap: '16px',
                padding: '20px',
                background: 'var(--bg-tertiary)',
                borderRadius: '14px',
                border: '1px solid var(--border)',
                transition: 'all 0.3s ease',
                animation: `slideIn 0.3s ease ${i * 0.05}s`,
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.borderColor = t.pnl >= 0 ? '#10B981' : '#EF4444'
                e.currentTarget.style.transform = 'translateY(-2px)'
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.borderColor = 'var(--border)'
                e.currentTarget.style.transform = 'translateY(0)'
              }}
              >
                <div style={{
                  width: '52px',
                  height: '52px',
                  borderRadius: '14px',
                  background: 'linear-gradient(135deg, #F7931A 0%, #F5A623 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '1.5rem',
                  fontWeight: 700,
                  color: '#ffffff',
                }}>
                  {t.sym[0]}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <span style={{ fontWeight: 700, fontSize: '1.125rem' }}>{t.sym}/USDT</span>
                    <span className={`tag ${t.side === 'long' ? 'tag-success' : 'tag-danger'}`}>
                      {t.side === 'long' ? '做多' : '做空'}
                    </span>
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>
                    数量: {t.qty} | 均价: ${t.price}
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontFamily: 'monospace', fontWeight: 700, fontSize: '1.25rem', color: t.pnl >= 0 ? '#10B981' : '#EF4444' }}>
                    {t.pnl >= 0 ? '+' : ''}{t.pnl.toFixed(2)} USDT
                  </div>
                  <div style={{ fontSize: '0.75rem', color: t.pnl >= 0 ? '#10B981' : '#EF4444' }}>
                    {t.pnlPct >= 0 ? '+' : ''}{t.pnlPct}%
                  </div>
                </div>
                <button style={{
                  padding: '10px 20px',
                  borderRadius: '10px',
                  border: '1px solid var(--border)',
                  background: 'transparent',
                  color: 'var(--text-secondary)',
                  fontSize: '0.8125rem',
                  fontWeight: 500,
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.background = '#EF4444'
                  e.currentTarget.style.color = '#ffffff'
                  e.currentTarget.style.borderColor = '#EF4444'
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.background = 'transparent'
                  e.currentTarget.style.color = 'var(--text-secondary)'
                  e.currentTarget.style.borderColor = 'var(--border)'
                }}
                >
                  平仓
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 历史记录 */}
      <div className="content-card">
        <div className="card-header">
          <h3 className="card-title">📜 历史记录</h3>
          <div style={{ display: 'flex', gap: '8px' }}>
            <input 
              type="text" 
              placeholder="搜索..."
              style={{
                padding: '8px 14px',
                borderRadius: '8px',
                border: '1px solid var(--border)',
                background: 'var(--bg-tertiary)',
                color: 'var(--text-primary)',
                fontSize: '0.8125rem',
                width: '140px',
              }}
            />
          </div>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>时间</th>
                <th>交易对</th>
                <th>方向</th>
                <th>数量</th>
                <th>价格</th>
                <th>盈亏</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              {trades.length > 0 ? trades.map((t, i) => (
                <tr key={i}>
                  <td style={{ fontSize: '0.8125rem', color: 'var(--text-tertiary)' }}>2026-03-19 10:30</td>
                  <td style={{ fontWeight: 600 }}>{t.symbol}</td>
                  <td><span className="tag tag-success">买入</span></td>
                  <td style={{ fontFamily: 'monospace' }}>0.1</td>
                  <td style={{ fontFamily: 'monospace' }}>$75,234</td>
                  <td style={{ color: '#10B981', fontFamily: 'monospace', fontWeight: 600 }}>+125.50</td>
                  <td><span className="tag tag-success">已完成</span></td>
                </tr>
              )) : [
                { t: '10:30', p: 'BTC', s: '买入', q: '0.1', pr: '75,234', pl: '+125.50', st: '完成' },
                { t: '09:15', p: 'ETH', s: '卖出', q: '1.5', pr: '3,456', pl: '-32.80', st: '完成' },
                { t: '08:45', p: 'SOL', s: '买入', q: '10', pr: '165', pl: '+68.50', st: '完成' },
              ].map((t, i) => (
                <tr key={i}>
                  <td style={{ fontSize: '0.8125rem', color: 'var(--text-tertiary)' }}>{t.t}</td>
                  <td style={{ fontWeight: 600 }}>{t.p}</td>
                  <td><span className={`tag ${t.s === '买入' ? 'tag-success' : 'tag-danger'}`}>{t.s}</span></td>
                  <td style={{ fontFamily: 'monospace' }}>{t.q}</td>
                  <td style={{ fontFamily: 'monospace' }}>${t.pr}</td>
                  <td style={{ 
                    color: t.pl.startsWith('+') ? '#10B981' : '#EF4444', 
                    fontFamily: 'monospace', 
                    fontWeight: 600 
                  }}>{t.pl}</td>
                  <td><span className="tag tag-success">{t.st}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
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
