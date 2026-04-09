/**
 * 🪿 Wallet - 钱包页
 * 主/子钱包管理 + 资产分布
 */

export function Wallet() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', animation: 'fadeInUp 0.4s ease' }}>
      
      {/* 资产概览 */}
      <div className="stats-row">
        <div className="stat-card" style={{ gridColumn: 'span 2' }}>
          <div className="stat-label">💰 总资产 (USDT)</div>
          <div className="stat-value gradient-text" style={{ fontSize: '2.5rem' }}>$85,000.00</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">📈 今日收益</div>
          <div className="stat-value positive">+$328.50</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">📊 收益率</div>
          <div className="stat-value" style={{ color: 'var(--accent)' }}>+3.94%</div>
        </div>
      </div>

      {/* 主钱包 + 子钱包 */}
      <div className="two-col-grid">
        {/* 主钱包 */}
        <div className="content-card">
          <div className="card-header">
            <h3 className="card-title">🏦 主钱包</h3>
            <span className="tag tag-success">主账户</span>
          </div>
          <div className="card-body">
            <div style={{ 
              padding: '28px', 
              background: 'linear-gradient(135deg, rgba(0, 212, 170, 0.15) 0%, rgba(124, 58, 237, 0.15) 100%)',
              borderRadius: '16px',
              border: '1px solid rgba(0, 212, 170, 0.3)',
              marginBottom: '20px',
            }}>
              <div style={{ fontSize: '0.8125rem', color: 'var(--text-tertiary)', marginBottom: '8px' }}>可用余额</div>
              <div style={{ fontSize: '2rem', fontWeight: 800, fontFamily: 'monospace', color: 'var(--accent)' }}>$85,000.00</div>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              {[
                { l: '持仓市值', v: '$12,450' },
                { l: '可用', v: '$72,550' },
                { l: '冻结', v: '$0' },
                { l: '盈亏', v: '+$328.50', c: '#10B981' },
              ].map((item, i) => (
                <div key={i} style={{ 
                  padding: '14px', 
                  background: 'var(--bg-tertiary)', 
                  borderRadius: '10px',
                }}>
                  <div style={{ fontSize: '0.6875rem', color: 'var(--text-tertiary)', marginBottom: '4px' }}>{item.l}</div>
                  <div style={{ fontWeight: 600, color: item.c || 'var(--text-primary)' }}>{item.v}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 子钱包 */}
        <div className="content-card">
          <div className="card-header">
            <h3 className="card-title">🔖 子钱包分配</h3>
          </div>
          <div className="card-body">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {[
                { icon: '🐰', name: '打兔子', amount: 2500, pct: 2.9, color: '#10B981' },
                { icon: '🐹', name: '打地鼠', amount: 3000, pct: 3.5, color: '#F59E0B' },
                { icon: '🔮', name: '走着燋', amount: 3000, pct: 3.5, color: '#7C3AED' },
                { icon: '👑', name: '跟大哥', amount: 1500, pct: 1.8, color: '#3B82F6' },
                { icon: '🍀', name: '搭便车', amount: 1000, pct: 1.2, color: '#EC4899' },
                { icon: '💰', name: '薅羊毛', amount: 1500, pct: 1.8, color: '#14B8A6' },
                { icon: '👶', name: '穷孩子', amount: 500, pct: 0.6, color: '#8B5CF6' },
              ].map((w, i) => (
                <div key={i} style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '14px 16px',
                  background: 'var(--bg-tertiary)',
                  borderRadius: '12px',
                  border: '1px solid var(--border)',
                  transition: 'all 0.3s ease',
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.borderColor = w.color
                  e.currentTarget.style.transform = 'translateX(4px)'
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.borderColor = 'var(--border)'
                  e.currentTarget.style.transform = 'translateX(0)'
                }}
                >
                  <span style={{ fontSize: '1.5rem' }}>{w.icon}</span>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, fontSize: '0.9375rem' }}>{w.name}</div>
                    <div style={{ fontSize: '0.6875rem', color: 'var(--text-tertiary)' }}>{w.pct}% 分配</div>
                  </div>
                  <div style={{ fontFamily: 'monospace', fontWeight: 700, color: w.color }}>${w.amount}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* 资产分布 */}
      <div className="content-card">
        <div className="card-header">
          <h3 className="card-title">📊 资产分布</h3>
        </div>
        <div className="card-body">
          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '32px', alignItems: 'center' }}>
            {/* 饼图模拟 */}
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              padding: '32px',
            }}>
              <div style={{ 
                width: '200px', 
                height: '200px', 
                borderRadius: '50%', 
                background: 'conic-gradient(#10B981 0deg 72deg, #F59E0B 72deg 144deg, #7C3AED 144deg 216deg, #3B82F6 216deg 252deg, #EC4899 252deg 288deg, #14B8A6 288deg 324deg, #8B5CF6 324deg 360deg)',
                position: 'relative',
                boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)',
              }}>
                <div style={{
                  position: 'absolute',
                  inset: '40px',
                  background: 'var(--bg-secondary)',
                  borderRadius: '50%',
                }} />
              </div>
            </div>
            {/* 图例 */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              {[
                { c: '#10B981', n: 'BTC', v: '45%', a: '$38,250' },
                { c: '#F59E0B', n: 'ETH', v: '25%', a: '$21,250' },
                { c: '#7C3AED', n: 'SOL', v: '20%', a: '$17,000' },
                { c: '#3B82F6', n: '其他', v: '10%', a: '$8,500' },
              ].map((item, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <div style={{ 
                    width: '16px', 
                    height: '16px', 
                    borderRadius: '4px', 
                    background: item.c 
                  }} />
                  <span style={{ fontWeight: 600, flex: 1 }}>{item.n}</span>
                  <span style={{ fontFamily: 'monospace', color: 'var(--text-secondary)' }}>{item.v}</span>
                  <span style={{ fontFamily: 'monospace', fontWeight: 700 }}>{item.a}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* 操作按钮 */}
      <div style={{ display: 'flex', gap: '16px' }}>
        <button style={{
          flex: 1,
          padding: '16px 24px',
          borderRadius: '14px',
          border: 'none',
          background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
          color: '#ffffff',
          fontSize: '1rem',
          fontWeight: 700,
          cursor: 'pointer',
          boxShadow: '0 8px 24px rgba(16, 185, 129, 0.3)',
          transition: 'all 0.3s ease',
        }}
        onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-4px)'}
        onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0)'}
        >
          💵 充值
        </button>
        <button style={{
          flex: 1,
          padding: '16px 24px',
          borderRadius: '14px',
          border: '1px solid var(--border)',
          background: 'var(--bg-tertiary)',
          color: 'var(--text-primary)',
          fontSize: '1rem',
          fontWeight: 700,
          cursor: 'pointer',
          transition: 'all 0.3s ease',
        }}
        onMouseOver={(e) => {
          e.currentTarget.style.borderColor = 'var(--accent)'
          e.currentTarget.style.transform = 'translateY(-4px)'
        }}
        onMouseOut={(e) => {
          e.currentTarget.style.borderColor = 'var(--border)'
          e.currentTarget.style.transform = 'translateY(0)'
        }}
        >
          💳 提现
        </button>
        <button style={{
          flex: 1,
          padding: '16px 24px',
          borderRadius: '14px',
          border: '1px solid var(--border)',
          background: 'var(--bg-tertiary)',
          color: 'var(--text-primary)',
          fontSize: '1rem',
          fontWeight: 700,
          cursor: 'pointer',
          transition: 'all 0.3s ease',
        }}
        onMouseOver={(e) => {
          e.currentTarget.style.borderColor = 'var(--accent)'
          e.currentTarget.style.transform = 'translateY(-4px)'
        }}
        onMouseOut={(e) => {
          e.currentTarget.style.borderColor = 'var(--border)'
          e.currentTarget.style.transform = 'translateY(0)'
        }}
        >
          🔄 转账
        </button>
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
