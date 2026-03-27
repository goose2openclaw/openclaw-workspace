/**
 * 🪿 Dashboard - 北斗七鑫完整版
 */

import { useState, useEffect } from 'react'
import { useStore } from '../stores/appStore'

type PageId = 'overview' | 'beidou' | 'rabbit' | 'mole' | 'oracle' | 'leader' | 'hitchhiker' | 'airdrop' | 'crowd' | 'settings'

const pages: { id: PageId; icon: string; name: string }[] = [
  { id: 'overview', icon: '📊', name: '总览' },
  { id: 'beidou', icon: '🪿', name: '北斗' },
  { id: 'rabbit', icon: '🐰', name: '打兔子' },
  { id: 'mole', icon: '🐹', name: '打地鼠' },
  { id: 'oracle', icon: '🔮', name: '走着燋' },
  { id: 'leader', icon: '👑', name: '跟大哥' },
  { id: 'hitchhiker', icon: '🍀', name: '搭便车' },
  { id: 'airdrop', icon: '💰', name: '薅羊毛' },
  { id: 'crowd', icon: '👶', name: '穷孩子' },
  { id: 'settings', icon: '⚙️', name: '设置' },
]

// 工具详情数据
const toolDetails: Record<string, any> = {
  rabbit: {
    name: '打兔子',
    desc: '主动发现并捕捉市场机会',
    target: '市值前20主流币',
    risk: '中',
    expected: '+28%',
    params: [
      { k: 'max_position_pct', v: 20, min: 5, max: 50, label: '最大仓位%' },
      { k: 'stop_loss_pct', v: 5, min: 1, max: 15, label: '止损%' },
      { k: 'take_profit_pct', v: 15, min: 5, max: 50, label: '止盈%' },
      { k: 'strong_trend_threshold', v: 7.5, min: 5, max: 9, label: '强趋势阈值' },
    ]
  },
  mole: {
    name: '打地鼠',
    desc: '被动等待，敲一下动一下',
    target: '市值20名后所有币',
    risk: '高',
    expected: '+35%',
    params: [
      { k: 'max_position_pct', v: 15, min: 2, max: 30, label: '最大仓位%' },
      { k: 'stop_loss_pct', v: 8, min: 3, max: 20, label: '止损%' },
      { k: 'take_profit_pct', v: 20, min: 10, max: 50, label: '止盈%' },
      { k: 'rebound_threshold', v: -10, min: -30, max: -5, label: '反弹阈值%' },
    ]
  },
  oracle: {
    name: '走着燋',
    desc: '智能预测趋势方向',
    target: '预测市场 Polymarket',
    risk: '中',
    expected: '+22%',
    params: [
      { k: 'min_confidence', v: 6, min: 3, max: 9, label: '最低置信度' },
      { k: 'max_position_pct', v: 10, min: 2, max: 20, label: '最大仓位%' },
    ]
  },
  leader: {
    name: '跟大哥',
    desc: '跟随大资金操作',
    target: '主流币大单',
    risk: '中',
    expected: '+18%',
    params: [
      { k: 'min_whale_amount', v: 100000, min: 10000, max: 1000000, label: '最小大单USDT' },
      { k: 'position_pct', v: 15, min: 5, max: 30, label: '跟单仓位%' },
    ]
  },
  hitchhiker: {
    name: '搭便车',
    desc: '顺风车策略',
    target: '跟单平台',
    risk: '低',
    expected: '+15%',
    params: [
      { k: 'min_win_rate', v: 55, min: 40, max: 80, label: '最低胜率%' },
      { k: 'max_drawdown', v: 30, min: 10, max: 50, label: '最大回撤%' },
    ]
  },
  airdrop: {
    name: '薅羊毛',
    desc: '空投和糖果',
    target: '新币空投',
    risk: '中',
    expected: '50-500U',
    available: 12,
    tasks: [
      { n: 'LayerZero', r: 500, d: '中' },
      { n: 'zkSync', r: 300, d: '易' },
      { n: 'Starknet', r: 200, d: '易' },
    ]
  },
  crowd: {
    name: '穷孩子',
    desc: '社区众包智慧',
    target: '数据标注/问卷',
    risk: '低',
    expected: '10-50U',
    available: 8,
    tasks: [
      { n: 'AI标注', r: 15, d: 30 },
      { n: '问卷', r: 10, d: 15 },
      { n: '翻译', r: 25, d: 45 },
    ]
  }
}

export function Dashboard() {
  const { stats, signals } = useStore()
  const [theme, setTheme] = useState('dark')
  const [activePage, setActivePage] = useState<PageId>('overview')
  const [expertMode, setExpertMode] = useState(false)
  
  const pnl = stats?.total_pnl || 0

  useEffect(() => {
    const hour = new Date().getHours()
    setTheme(hour < 6 || hour >= 18 ? 'dark' : 'light')
  }, [])

  const isDark = theme === 'dark'
  const bg = isDark ? '#0c1520' : '#e8f4fc'
  const cardBg = isDark ? 'rgba(20,35,50,0.85)' : 'rgba(255,255,255,0.85)'
  const border = isDark ? 'rgba(0,150,200,0.12)' : 'rgba(100,180,220,0.2)'
  const textPrimary = isDark ? '#f0f5f8' : '#1a3a5a'
  const textSecondary = isDark ? '#7a9aaa' : '#6a8a9a'

  return (
    <div style={{ background: bg, minHeight: '100vh' }}>
      {/* 顶部 */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 16px', background: isDark ? 'rgba(12,21,32,0.95)' : 'rgba(232,244,252,0.95)', borderBottom: '1px solid ' + border, position: 'sticky', top: 0, zIndex: 100, flexWrap: 'wrap', gap: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ width: 32, height: 32, borderRadius: '50%', background: isDark ? '#e8eef2' : '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>🪿</div>
          <div style={{ fontSize: '0.9375rem', fontWeight: 700, color: textPrimary }}>Go2Se 护食</div>
        </div>
        <button onClick={() => setExpertMode(!expertMode)} style={{ padding: '4px 10px', borderRadius: 10, border: 'none', background: expertMode ? '#7c3aed' : (isDark ? '#1a3040' : '#fff'), color: expertMode ? '#fff' : textSecondary, fontSize: '0.5625rem', fontWeight: 600, cursor: 'pointer' }}>
          🎛️ {expertMode ? '专家模式' : '普通模式'}
        </button>
      </div>

      {/* 横向快捷 */}
      <div style={{ display: 'flex', justifyContent: 'center', gap: 4, padding: '8px', background: isDark ? 'rgba(20,35,50,0.6)' : 'rgba(200,225,240,0.6)', overflowX: 'auto', flexWrap: 'wrap' }}>
        {pages.map(p => (
          <button key={p.id} onClick={() => setActivePage(p.id)} style={{ minWidth: 45, height: 45, background: activePage === p.id ? (isDark ? '#00b5d6' : '#0891b2') : 'transparent', borderRadius: '50%', border: 'none', cursor: 'pointer', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
            <span style={{ fontSize: '0.875rem' }}>{p.icon}</span>
            <span style={{ fontSize: '0.375rem', fontWeight: 600, color: activePage === p.id ? '#fff' : textSecondary }}>{p.name}</span>
          </button>
        ))}
      </div>

      {/* 标语 */}
      <div style={{ textAlign: 'center', padding: '10px' }}>
        <h2 style={{ fontSize: '1.125rem', fontWeight: 800, background: isDark ? 'linear-gradient(90deg, #00b5d6, #00d4aa, #7c3aed)' : 'linear-gradient(90deg, #0891b2, #2563eb, #7c3aed)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>薅羊毛众包AI, 量化投资加密</h2>
      </div>

      {/* 内容 */}
      <div style={{ padding: '0 12px 20px', maxWidth: 700, margin: '0 auto' }}>
        {activePage === 'overview' && <OverviewPage isDark={isDark} cardBg={cardBg} border={border} textPrimary={textPrimary} textSecondary={textSecondary} pnl={pnl} />}
        {activePage === 'beidou' && <BeidouPage isDark={isDark} cardBg={cardBg} border={border} textPrimary={textPrimary} textSecondary={textSecondary} setActivePage={setActivePage} />}
        {activePage === 'rabbit' && <ToolPage isDark={isDark} cardBg={cardBg} border={border} textPrimary={textPrimary} textSecondary={textSecondary} toolKey="rabbit" />}
        {activePage === 'mole' && <ToolPage isDark={isDark} cardBg={cardBg} border={border} textPrimary={textPrimary} textSecondary={textSecondary} toolKey="mole" />}
        {activePage === 'oracle' && <ToolPage isDark={isDark} cardBg={cardBg} border={border} textPrimary={textPrimary} textSecondary={textSecondary} toolKey="oracle" />}
        {activePage === 'leader' && <ToolPage isDark={isDark} cardBg={cardBg} border={border} textPrimary={textPrimary} textSecondary={textSecondary} toolKey="leader" />}
        {activePage === 'hitchhiker' && <ToolPage isDark={isDark} cardBg={cardBg} border={border} textPrimary={textPrimary} textSecondary={textSecondary} toolKey="hitchhiker" />}
        {activePage === 'airdrop' && <WorkPage isDark={isDark} cardBg={cardBg} border={border} textPrimary={textPrimary} textSecondary={textSecondary} toolKey="airdrop" />}
        {activePage === 'crowd' && <WorkPage isDark={isDark} cardBg={cardBg} border={border} textPrimary={textPrimary} textSecondary={textSecondary} toolKey="crowd" />}
        {activePage === 'settings' && <SettingsPage isDark={isDark} cardBg={cardBg} border={border} textPrimary={textPrimary} textSecondary={textSecondary} />}
      </div>
    </div>
  )
}

function OverviewPage({ isDark, cardBg, border, textPrimary, textSecondary, pnl }: any) {
  return (
    <div style={{ display: 'grid', gap: 12 }}>
      <div style={{ background: cardBg, borderRadius: 12, padding: 14, border: '1px solid ' + border }}>
        <h3 style={{ fontSize: '0.8125rem', fontWeight: 700, marginBottom: 10, color: textPrimary }}>📊 核心指标</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 8 }}>
          <div style={{ padding: 8, background: isDark ? '#152535' : '#f0f8ff', borderRadius: 6, textAlign: 'center' }}><div style={{ fontSize: '0.5rem', color: textSecondary }}>总盈亏</div><div style={{ fontSize: '0.875rem', fontWeight: 800, color: pnl >= 0 ? '#10b981' : '#ef4444' }}>{pnl >= 0 ? '+' : ''}{pnl.toFixed(2)}</div></div>
          <div style={{ padding: 8, background: isDark ? '#152535' : '#f0f8ff', borderRadius: 6, textAlign: 'center' }}><div style={{ fontSize: '0.5rem', color: textSecondary }}>工具</div><div style={{ fontSize: '0.875rem', fontWeight: 800, color: '#00b5d6' }}>7</div></div>
          <div style={{ padding: 8, background: isDark ? '#152535' : '#f0f8ff', borderRadius: 6, textAlign: 'center' }}><div style={{ fontSize: '0.5rem', color: textSecondary }}>信号</div><div style={{ fontSize: '0.875rem', fontWeight: 800, color: '#7c3aed' }}>0</div></div>
          <div style={{ padding: 8, background: isDark ? '#152535' : '#f0f8ff', borderRadius: 6, textAlign: 'center' }}><div style={{ fontSize: '0.5rem', color: textSecondary }}>胜率</div><div style={{ fontSize: '0.875rem', fontWeight: 800, color: '#10b981' }}>78%</div></div>
        </div>
      </div>
    </div>
  )
}

function BeidouPage({ isDark, cardBg, border, textPrimary, textSecondary, setActivePage }: any) {
  const tools = [
    { id: 'rabbit', icon: '🐰', name: '打兔子', desc: '主动发现机会', color: '#10B981' },
    { id: 'mole', icon: '🐹', name: '打地鼠', desc: '被动等机会', color: '#F59E0B' },
    { id: 'oracle', icon: '🔮', name: '走着燋', desc: '预测市场', color: '#7C3AED' },
    { id: 'leader', icon: '👑', name: '跟大哥', desc: '做市协调', color: '#3B82F6' },
    { id: 'hitchhiker', icon: '🍀', name: '搭便车', desc: '跟单分成', color: '#EC4899' },
    { id: 'airdrop', icon: '💰', name: '薅羊毛', desc: '新币空投', color: '#14B8A6' },
    { id: 'crowd', icon: '👶', name: '穷孩子', desc: '众包数据', color: '#8B5CF6' },
  ]
  return (
    <div style={{ background: cardBg, borderRadius: 12, padding: 14, border: '1px solid ' + border }}>
      <h3 style={{ fontSize: '0.875rem', fontWeight: 700, marginBottom: 12, color: textPrimary }}>🪿 北斗七鑫 - 投资与打工</h3>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 8 }}>
        {tools.map((t: any) => (
          <div key={t.id} onClick={() => setActivePage(t.id)} style={{ padding: 12, background: t.color + '15', borderRadius: 10, border: '1px solid ' + t.color + '40', cursor: 'pointer' }}>
            <div style={{ fontSize: '1.5rem' }}>{t.icon}</div>
            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: t.color }}>{t.name}</div>
            <div style={{ fontSize: '0.5625rem', color: textSecondary }}>{t.desc}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

function ToolPage({ isDark, cardBg, border, textPrimary, textSecondary, toolKey }: any) {
  const tool = toolDetails[toolKey as keyof typeof toolDetails]
  const colors: any = { rabbit: '#10B981', mole: '#F59E0B', oracle: '#7C3AED', leader: '#3B82F6', hitchhiker: '#EC4899' }
  const color = colors[toolKey] || '#00b5d6'
  
  return (
    <div style={{ display: 'grid', gap: 12 }}>
      <div style={{ background: cardBg, borderRadius: 12, padding: 14, border: '1px solid ' + border }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
          <span style={{ fontSize: '2rem' }}>{toolKey === 'rabbit' ? '🐰' : toolKey === 'mole' ? '🐹' : toolKey === 'oracle' ? '🔮' : toolKey === 'leader' ? '👑' : '🍀'}</span>
          <div>
            <div style={{ fontSize: '1rem', fontWeight: 700, color }}>{tool.name}</div>
            <div style={{ fontSize: '0.625rem', color: textSecondary }}>{tool.desc}</div>
          </div>
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 8, marginBottom: 12 }}>
          <div style={{ padding: 8, background: isDark ? '#152535' : '#f0f8ff', borderRadius: 6, textAlign: 'center' }}><div style={{ fontSize: '0.5rem', color: textSecondary }}>目标</div><div style={{ fontSize: '0.625rem', fontWeight: 600 }}>{tool.target}</div></div>
          <div style={{ padding: 8, background: isDark ? '#152535' : '#f0f8ff', borderRadius: 6, textAlign: 'center' }}><div style={{ fontSize: '0.5rem', color: textSecondary }}>风险</div><div style={{ fontSize: '0.625rem', fontWeight: 600, color: tool.risk === '高' ? '#ef4444' : tool.risk === '中' ? '#f59e0b' : '#10b981' }}>{tool.risk}</div></div>
          <div style={{ padding: 8, background: isDark ? '#152535' : '#f0f8ff', borderRadius: 6, textAlign: 'center' }}><div style={{ fontSize: '0.5rem', color: textSecondary }}>预期</div><div style={{ fontSize: '0.625rem', fontWeight: 600, color: '#10b981' }}>{tool.expected}</div></div>
        </div>
        
        <h4 style={{ fontSize: '0.75rem', fontWeight: 600, color: textPrimary, marginBottom: 8 }}>参数配置</h4>
        {tool.params?.map((p: any, i: number) => (
          <div key={i} style={{ marginBottom: 8 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
              <span style={{ fontSize: '0.625rem', color: textSecondary }}>{p.label}</span>
              <span style={{ fontSize: '0.625rem', fontWeight: 600, color }}>{p.v}</span>
            </div>
            <input type="range" min={p.min} max={p.max} defaultValue={p.v} style={{ width: '100%', accentColor: color }} />
          </div>
        ))}
      </div>
    </div>
  )
}

function WorkPage({ isDark, cardBg, border, textPrimary, textSecondary, toolKey }: any) {
  const tool = toolDetails[toolKey as keyof typeof toolDetails]
  const isAirdrop = toolKey === 'airdrop'
  
  return (
    <div style={{ background: cardBg, borderRadius: 12, padding: 14, border: '1px solid ' + border }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
        <span style={{ fontSize: '2rem' }}>{isAirdrop ? '💰' : '👶'}</span>
        <div>
          <div style={{ fontSize: '1rem', fontWeight: 700, color: '#f59e0b' }}>{tool.name}</div>
          <div style={{ fontSize: '0.625rem', color: textSecondary }}>{tool.desc}</div>
        </div>
      </div>
      
      <div style={{ fontSize: '0.6875rem', color: textSecondary, marginBottom: 8 }}>可抢任务: {tool.available}个</div>
      
      {tool.tasks?.map((t: any, i: number) => (
        <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: 10, background: isDark ? '#152535' : '#f0f8ff', borderRadius: 8, marginBottom: 6 }}>
          <div>
            <div style={{ fontWeight: 600, fontSize: '0.75rem' }}>{t.n}</div>
            <div style={{ fontSize: '0.5625rem', color: textSecondary }}>{isAirdrop ? `难度:${t.d}` : `${t.d}分钟`}</div>
          </div>
          <div style={{ fontWeight: 700, color: '#10b981' }}>${t.r}</div>
        </div>
      ))}
    </div>
  )
}

function SettingsPage({ isDark, cardBg, border, textPrimary, textSecondary }: any) {
  return (
    <div style={{ background: cardBg, borderRadius: 12, padding: 14, border: '1px solid ' + border }}>
      <h3 style={{ fontSize: '0.8125rem', fontWeight: 700, marginBottom: 10, color: textPrimary }}>⚙️ 设置</h3>
      {[
        { n: '交易设置', d: '滑点/手续费/仓位' },
        { n: '风控设置', d: '止损/熔断/限流' },
        { n: 'API管理', d: '交易所API配置' },
        { n: '通知设置', d: '推送/邮件/短信' },
      ].map((x: any, i: number) => (
        <div key={i} style={{ padding: 10, background: isDark ? '#152535' : '#f0f8ff', borderRadius: 8, marginBottom: 6, cursor: 'pointer' }}>
          <div style={{ fontWeight: 600, fontSize: '0.75rem' }}>{x.n}</div>
          <div style={{ fontSize: '0.5625rem', color: textSecondary }}>{x.d}</div>
        </div>
      ))}
    </div>
  )
}
