/**
 * 🪿 Market - 市场页
 * 实时行情 + 趋势分析
 */

import { useStore } from '../stores/appStore'

export function Market() {
  const { markets } = useStore()

  const formatPrice = (price: number) => {
    if (!price) return '-'
    if (price > 1000) return price.toLocaleString('zh-CN', { maximumFractionDigits: 2 })
    return price.toFixed(2)
  }

  const formatVol = (vol: number) => {
    if (!vol) return '-'
    if (vol > 1e9) return (vol / 1e9).toFixed(2) + 'B'
    if (vol > 1e6) return (vol / 1e6).toFixed(2) + 'M'
    return vol.toLocaleString()
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', animation: 'fadeInUp 0.4s ease' }}>
      
      {/* 快捷筛选 */}
      <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
        {['全部', '涨幅榜', '跌幅榜', '成交量', 'DeFi', 'Layer2'].map((f, i) => (
          <button key={f} style={{
            padding: '10px 20px',
            borderRadius: '20px',
            border: i === 0 ? 'none' : '1px solid var(--border)',
            background: i === 0 ? 'var(--accent)' : 'var(--bg-tertiary)',
            color: i === 0 ? '#ffffff' : 'var(--text-secondary)',
            fontSize: '0.875rem',
            fontWeight: 500,
            cursor: 'pointer',
            transition: 'all 0.2s ease',
          }}>
            {f}
          </button>
        ))}
      </div>

      {/* 市场表格 */}
      <div className="content-card">
        <div className="card-header">
          <h3 className="card-title">📈 实时行情</h3>
          <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
            <input 
              type="text" 
              placeholder="搜索交易对..."
              style={{
                padding: '10px 16px',
                borderRadius: '10px',
                border: '1px solid var(--border)',
                background: 'var(--bg-tertiary)',
                color: 'var(--text-primary)',
                fontSize: '0.875rem',
                width: '180px',
                outline: 'none',
              }}
            />
            <button style={{
              padding: '10px 16px',
              borderRadius: '10px',
              border: 'none',
              background: 'var(--accent)',
              color: '#ffffff',
              fontSize: '0.875rem',
              fontWeight: 500,
              cursor: 'pointer',
            }}>
              🔄 刷新
            </button>
          </div>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>#</th>
                <th>交易对</th>
                <th>价格</th>
                <th>24h涨跌</th>
                <th>24h成交量</th>
                <th>RSI</th>
                <th>状态</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {markets.map((m, i) => (
                <tr key={m.symbol} style={{ animation: 'fadeInUp 0.3s ease', animationDelay: `${i * 0.05}s` }}>
                  <td style={{ color: 'var(--text-tertiary)', fontSize: '0.8125rem' }}>{i + 1}</td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span style={{ fontSize: '1.5rem' }}>🪙</span>
                      <div>
                        <div style={{ fontWeight: 700, fontFamily: 'monospace' }}>{m.symbol.replace('/USDT', '')}</div>
                        <div style={{ fontSize: '0.6875rem', color: 'var(--text-tertiary)' }}>USDT</div>
                      </div>
                    </div>
                  </td>
                  <td style={{ fontFamily: 'monospace', fontWeight: 600, fontSize: '1rem' }}>${formatPrice(m.price)}</td>
                  <td>
                    <span className={m.change_24h >= 0 ? 'price-up' : 'price-down'} style={{ 
                      fontFamily: 'monospace', 
                      fontWeight: 600,
                      padding: '4px 12px',
                      borderRadius: '6px',
                      background: m.change_24h >= 0 ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                    }}>
                      {m.change_24h >= 0 ? '▲' : '▼'} {Math.abs(m.change_24h || 0).toFixed(2)}%
                    </span>
                  </td>
                  <td style={{ color: 'var(--text-secondary)', fontFamily: 'monospace' }}>${formatVol(m.volume_24h)}</td>
                  <td>
                    <span style={{ 
                      fontFamily: 'monospace', 
                      fontWeight: 700,
                      color: (m.rsi || 0) > 70 ? '#EF4444' : (m.rsi || 0) < 30 ? '#10B981' : 'var(--text-secondary)'
                    }}>
                      {(m.rsi || 0).toFixed(1)}
                    </span>
                  </td>
                  <td>
                    <span className={`tag ${
                      (m.rsi || 0) > 70 ? 'tag-danger' : 
                      (m.rsi || 0) < 30 ? 'tag-success' : 'tag-neutral'
                    }`}>
                      {(m.rsi || 0) > 70 ? '超买' : (m.rsi || 0) < 30 ? '超卖' : '正常'}
                    </span>
                  </td>
                  <td>
                    <button style={{
                      padding: '8px 16px',
                      borderRadius: '8px',
                      border: '1px solid var(--border)',
                      background: 'transparent',
                      color: 'var(--text-secondary)',
                      fontSize: '0.8125rem',
                      cursor: 'pointer',
                      transition: 'all 0.2s ease',
                    }}
                    onMouseOver={(e) => {
                      e.currentTarget.style.background = 'var(--accent)'
                      e.currentTarget.style.color = '#ffffff'
                      e.currentTarget.style.borderColor = 'var(--accent)'
                    }}
                    onMouseOut={(e) => {
                      e.currentTarget.style.background = 'transparent'
                      e.currentTarget.style.color = 'var(--text-secondary)'
                      e.currentTarget.style.borderColor = 'var(--border)'
                    }}
                    >
                      交易
                    </button>
                  </td>
                </tr>
              ))}
              {markets.length === 0 && (
                <tr>
                  <td colSpan={8} style={{ textAlign: 'center', padding: '60px', color: 'var(--text-tertiary)' }}>
                    <div style={{ fontSize: '3rem', marginBottom: '16px' }}>📊</div>
                    <div>暂无市场数据</div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* 快速统计 */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px' }}>
        <div className="content-card" style={{ textAlign: 'center', padding: '24px' }}>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#EF4444', marginBottom: '8px' }}>
            {markets.filter(m => (m.rsi || 0) > 70).length}
          </div>
          <div style={{ fontSize: '0.875rem', color: 'var(--text-tertiary)' }}>超买 RSI&gt;70</div>
        </div>
        <div className="content-card" style={{ textAlign: 'center', padding: '24px' }}>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#10B981', marginBottom: '8px' }}>
            {markets.filter(m => (m.rsi || 0) < 30).length}
          </div>
          <div style={{ fontSize: '0.875rem', color: 'var(--text-tertiary)' }}>超卖 RSI&lt;30</div>
        </div>
        <div className="content-card" style={{ textAlign: 'center', padding: '24px' }}>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--accent)', marginBottom: '8px' }}>
            {markets.filter(m => m.rsi && m.rsi >= 30 && m.rsi <= 70).length}
          </div>
          <div style={{ fontSize: '0.875rem', color: 'var(--text-tertiary)' }}>正常 RSI 30-70</div>
        </div>
      </div>

      <style>{`
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  )
}
