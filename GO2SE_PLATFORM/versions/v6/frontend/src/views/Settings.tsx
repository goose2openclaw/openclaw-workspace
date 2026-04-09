/**
 * 🪿 Settings - 设置页
 * 交易配置 + 风控规则 + API管理
 */

import { useState } from 'react'

const rules = [
  { id: 'R001', name: '仓位限制', condition: '>80%', action: '禁止开仓', status: true },
  { id: 'R002', name: '日内熔断', condition: '>30%', action: '全部平仓', status: true },
  { id: 'R003', name: '单笔风险', condition: '>5%', action: '降低仓位', status: true },
  { id: 'R004', name: '波动止损', condition: '>8%', action: '自动止损', status: true },
  { id: 'R005', name: '流动性检查', condition: '<100K', action: '禁止交易', status: true },
  { id: 'R006', name: 'API故障', condition: '>1%', action: '切换API', status: true },
  { id: 'R007', name: '异常检测', condition: '>3σ', action: '人工确认', status: false },
  { id: 'R008', name: '情绪过热', condition: '>5σ', action: '暂停交易', status: true },
]

const apis = [
  { name: 'Binance', status: 'online', latency: 45, icon: '🟡' },
  { name: 'Bybit', status: 'online', latency: 52, icon: '🟣' },
  { name: 'OKX', status: 'degraded', latency: 128, icon: '🔴' },
  { name: 'Gate', status: 'offline', latency: 0, icon: '⚫' },
]

export function Settings() {
  const [tab, setTab] = useState<'general' | 'risk' | 'api'>('general')

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', animation: 'fadeInUp 0.4s ease' }}>
      
      {/* 标签切换 */}
      <div style={{ display: 'flex', gap: '10px' }}>
        {[
          { key: 'general', icon: '⚙️', label: '交易配置' },
          { key: 'risk', icon: '🛡️', label: '风控规则' },
          { key: 'api', icon: '🔌', label: 'API管理' },
        ].map(t => (
          <button
            key={t.key}
            onClick={() => setTab(t.key as typeof tab)}
            style={{
              padding: '14px 28px',
              borderRadius: '12px',
              border: 'none',
              background: tab === t.key ? 'var(--accent)' : 'var(--bg-tertiary)',
              color: tab === t.key ? '#ffffff' : 'var(--text-secondary)',
              fontSize: '0.9375rem',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}
          >
            <span>{t.icon}</span>
            <span>{t.label}</span>
          </button>
        ))}
      </div>

      {/* 通用配置 */}
      {tab === 'general' && (
        <div className="content-card" style={{ animation: 'fadeIn 0.3s ease' }}>
          <div className="card-header">
            <h3 className="card-title">⚙️ 交易配置</h3>
          </div>
          <div className="card-body">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', maxWidth: '560px' }}>
              
              {/* 交易模式 */}
              <div>
                <div style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '12px' }}>交易模式</div>
                <div style={{ display: 'flex', gap: '16px' }}>
                  {['模拟交易', '实盘交易'].map((m, i) => (
                    <label key={m} style={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      gap: '10px',
                      padding: '14px 24px',
                      background: i === 0 ? 'rgba(0, 212, 170, 0.1)' : 'var(--bg-tertiary)',
                      border: `1px solid ${i === 0 ? '#00D4AA' : 'var(--border)'}`,
                      borderRadius: '12px',
                      cursor: 'pointer',
                      transition: 'all 0.2s ease',
                    }}>
                      <input type="radio" name="mode" defaultChecked={i === 0} />
                      <span style={{ fontWeight: 500 }}>{m}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* 滑块配置 */}
              {[
                { l: '最大仓位', v: '60%', min: 10, max: 100, val: 60 },
                { l: '止损线', v: '5%', min: 1, max: 20, val: 5 },
                { l: '止盈线', v: '15%', min: 5, max: 50, val: 15 },
                { l: '单笔上限', v: '1000U', min: 100, max: 10000, val: 1000 },
              ].map((s, i) => (
                <div key={i}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                    <span style={{ fontSize: '0.875rem', fontWeight: 500 }}>{s.l}</span>
                    <span style={{ fontFamily: 'monospace', fontWeight: 700, color: 'var(--accent)' }}>{s.v}</span>
                  </div>
                  <input 
                    type="range" 
                    min={s.min} 
                    max={s.max} 
                    defaultValue={s.val}
                    style={{
                      width: '100%',
                      height: '8px',
                      borderRadius: '4px',
                      appearance: 'none',
                      background: 'var(--bg-tertiary)',
                      cursor: 'pointer',
                    }}
                  />
                </div>
              ))}

              {/* 开关配置 */}
              {[
                { l: '自动复利', d: '盈利自动追加仓位', v: true },
                { l: '杠杆交易', d: '启用1-3倍杠杆', v: false },
                { l: '跟单模式', d: '跟随信号自动交易', v: true },
              ].map((sw, i) => (
                <div key={i} style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center',
                  padding: '16px',
                  background: 'var(--bg-tertiary)',
                  borderRadius: '12px',
                }}>
                  <div>
                    <div style={{ fontWeight: 600, marginBottom: '2px' }}>{sw.l}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>{sw.d}</div>
                  </div>
                  <div style={{
                    width: '52px',
                    height: '28px',
                    borderRadius: '14px',
                    background: sw.v ? 'var(--accent)' : 'var(--bg-secondary)',
                    position: 'relative',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                  }}>
                    <div style={{
                      position: 'absolute',
                      width: '22px',
                      height: '22px',
                      borderRadius: '50%',
                      background: '#ffffff',
                      top: '3px',
                      left: sw.v ? '27px' : '3px',
                      transition: 'all 0.3s ease',
                      boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
                    }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* 风控规则 */}
      {tab === 'risk' && (
        <div className="content-card" style={{ animation: 'fadeIn 0.3s ease' }}>
          <div className="card-header">
            <h3 className="card-title">🛡️ 风控规则</h3>
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
              + 添加规则
            </button>
          </div>
          <div className="card-body">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {rules.map((r, i) => (
                <div key={i} style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '16px',
                  padding: '16px 20px',
                  background: 'var(--bg-tertiary)',
                  borderRadius: '12px',
                  border: '1px solid var(--border)',
                  transition: 'all 0.3s ease',
                }}
                onMouseOver={(e) => e.currentTarget.style.borderColor = r.status ? '#10B981' : 'var(--border)'}
                onMouseOut={(e) => e.currentTarget.style.borderColor = 'var(--border)'}
                >
                  <div style={{
                    width: '40px',
                    height: '24px',
                    borderRadius: '12px',
                    background: r.status ? '#10B981' : 'var(--bg-secondary)',
                    position: 'relative',
                    cursor: 'pointer',
                  }}>
                    <div style={{
                      position: 'absolute',
                      width: '18px',
                      height: '18px',
                      borderRadius: '50%',
                      background: '#ffffff',
                      top: '3px',
                      left: r.status ? '19px' : '3px',
                      transition: 'all 0.3s ease',
                    }} />
                  </div>
                  <div style={{ flex: 1 }}>
                    <span style={{ fontWeight: 700, marginRight: '12px' }}>{r.id}</span>
                    <span style={{ fontWeight: 600 }}>{r.name}</span>
                  </div>
                  <div style={{ 
                    padding: '6px 14px', 
                    background: 'rgba(245, 158, 11, 0.15)', 
                    borderRadius: '8px',
                    fontSize: '0.8125rem',
                    fontFamily: 'monospace',
                    color: '#F59E0B',
                  }}>
                    {r.condition}
                  </div>
                  <div style={{ 
                    padding: '6px 14px', 
                    background: 'rgba(99, 102, 241, 0.15)', 
                    borderRadius: '8px',
                    fontSize: '0.8125rem',
                    color: '#6366F1',
                  }}>
                    {r.action}
                  </div>
                  <button style={{
                    padding: '8px 14px',
                    borderRadius: '8px',
                    border: '1px solid var(--border)',
                    background: 'transparent',
                    color: 'var(--text-tertiary)',
                    fontSize: '0.75rem',
                    cursor: 'pointer',
                  }}>
                    编辑
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* API管理 */}
      {tab === 'api' && (
        <div className="content-card" style={{ animation: 'fadeIn 0.3s ease' }}>
          <div className="card-header">
            <h3 className="card-title">🔌 API 连接</h3>
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
              + 添加API
            </button>
          </div>
          <div className="card-body">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              {apis.map((api, i) => (
                <div key={i} style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '16px',
                  padding: '20px',
                  background: 'var(--bg-tertiary)',
                  borderRadius: '14px',
                  border: '1px solid var(--border)',
                  transition: 'all 0.3s ease',
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.borderColor = api.status === 'online' ? '#10B981' : api.status === 'degraded' ? '#F59E0B' : '#EF4444'
                }}
                onMouseOut={(e) => e.currentTarget.style.borderColor = 'var(--border)'}
                >
                  <span style={{ fontSize: '1.75rem' }}>{api.icon}</span>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 700, fontSize: '1.0625rem' }}>{api.name}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>
                      {api.status === 'online' ? `延迟 ${api.latency}ms` : api.status === 'degraded' ? '连接降级' : '离线'}
                    </div>
                  </div>
                  <span className={`tag ${
                    api.status === 'online' ? 'tag-success' : api.status === 'degraded' ? 'tag-warning' : 'tag-danger'
                  }`}>
                    {api.status === 'online' ? '在线' : api.status === 'degraded' ? '降级' : '离线'}
                  </span>
                  <button style={{
                    padding: '10px 18px',
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
                    e.currentTarget.style.background = 'var(--accent)'
                    e.currentTarget.style.color = '#ffffff'
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.background = 'transparent'
                    e.currentTarget.style.color = 'var(--text-secondary)'
                  }}
                  >
                    测试
                  </button>
                  <button style={{
                    padding: '10px 18px',
                    borderRadius: '10px',
                    border: 'none',
                    background: 'rgba(239, 68, 68, 0.15)',
                    color: '#EF4444',
                    fontSize: '0.8125rem',
                    fontWeight: 500,
                    cursor: 'pointer',
                  }}>
                    删除
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* 保存按钮 */}
      <div style={{ display: 'flex', gap: '16px', marginTop: '8px' }}>
        <button className="cta-button" style={{ flex: 1 }}>
          💾 保存配置
        </button>
        <button style={{
          flex: 1,
          padding: '16px 24px',
          borderRadius: '14px',
          border: '1px solid var(--border)',
          background: 'var(--bg-tertiary)',
          color: 'var(--text-secondary)',
          fontSize: '1rem',
          fontWeight: 600,
          cursor: 'pointer',
        }}>
          重置默认
        </button>
      </div>

      <style>{`
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
      `}</style>
    </div>
  )
}
