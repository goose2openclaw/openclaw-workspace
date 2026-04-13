/**
 * GO2SE 北斗七鑫 V10 - 智能投资平台
 * 
 * 投资架构:
 * ┌─────────────────────────────────────────────────────────┐
 * │              北斗七鑫投资组合 (可调参数)                   │
 * ├─────────────────────────────────────────────────────────┤
 * │  投资工具 (5种)              │  打工工具 (2种)           │
 * │  🐰 打兔子 (前20主流)        │  💰 薅羊毛 (空投)        │
 * │  🐹 打地鼠 (其他币)          │  👶 穷孩子 (众包)        │
 * │  🔮 走着瞧 (预测市场)        │                           │
 * │  👑 跟大哥 (做市)           │                           │
 * │  🍀 搭便车 (跟单)          │                           │
 * ├─────────────────────────────────────────────────────────┤
 * │  趋势判断: 声纳库 │ 预言机 │ MiroFish │ 情绪 │ 其他     │
 * ├─────────────────────────────────────────────────────────┤
 * │  底层: 市场数据 │ 算力 │ 策略 │ 资金                     │
 * └─────────────────────────────────────────────────────────┘
 * 
 * 25维度全向仿真 (A-E五层)
 * 赚钱模块: V3智能找单·选品·抢单
 */

import { useState, useEffect, useCallback } from 'react';
import { BrowserRouter, Routes, Route, NavLink, useNavigate } from 'react-router-dom';
import './App.css';
import RecommendationHub from './components/RecommendationHub';

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8004";

// 工具类型
type Tool = {
  id: string;
  name: string;
  emoji: string;
  position: number;
  stopLoss: number;
  takeProfit: number;
  status: 'active' | 'paused' | 'inactive';
  dailyPnL: number;
  totalPnL: number;
  trades: number;
};

type Layer = 'A' | 'B' | 'C' | 'D' | 'E';

interface MarketData { symbol: string; price: number; change24h: number; volume: number; }
interface Signal { id: string; symbol: string; type: 'buy' | 'sell'; strength: number; timestamp: string; }
interface PortfolioStats { totalValue: number; dailyPnL: number; totalPnL: number; positions: number; winRate: number; }

// 赚钱任务类型
interface EarnTask {
  task_id: string;
  name: string;
  project?: string;
  platform?: string;
  chain?: string;
  expected_return_usd?: number;
  reward_usd?: number;
  net_return?: number;
  hourly_rate?: number;
  total_score: number;
  priority: string;
  remaining_slots?: number;
  hours_left?: number;
  reliability?: number;
  difficulty?: string;
  recommendation?: string;
}

// Page components import
import { Dashboard } from './components/Dashboard';
import { Trends } from './components/Trends';
import { Signals } from './components/Signals';
import { Tools } from './components/Tools';
import { Portfolio } from './components/Portfolio';
import { Settings } from './components/Settings';
import RecommendationHub from './components/RecommendationHub';

function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}

function AppContent() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'dashboard' | 'tools' | 'trends' | 'signals' | 'portfolio' | 'settings' | 'earn' | 'recommend'>('dashboard');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [signals, setSignals] = useState<Signal[]>([]);
  const [appVersion, setAppVersion] = useState<string>('v10.0');
  const [_portfolio, setPortfolio] = useState<PortfolioStats | null>(null);
  const [performance, setPerformance] = useState<any>(null);

  // 赚钱数据
  const [earnTab, setEarnTab] = useState<'airdrop' | 'crowd'>('airdrop');
  const [airdropTasks, setAirdropTasks] = useState<EarnTask[]>([]);
  const [crowdTasks, setCrowdTasks] = useState<EarnTask[]>([]);
  const [earnStats, setEarnStats] = useState<any>(null);
  const [scanLoading, setScanLoading] = useState(false);
  const [grabResults, setGrabResults] = useState<any[]>([]);

  // 仿真结果
  const [simulationScore] = useState<number>(95.1);
  const [layerScores] = useState<Record<Layer, number>>({ A: 90.3, B: 96.5, C: 96.1, D: 94.0, E: 95.6 });

  // 北斗七鑫工具配置
  const [tools, setTools] = useState<Tool[]>([
    { id: 'rabbit', name: '打兔子', emoji: '🐰', position: 25, stopLoss: 5, takeProfit: 8, status: 'active', dailyPnL: 0, totalPnL: 0, trades: 0 },
    { id: 'mole', name: '打地鼠', emoji: '🐹', position: 20, stopLoss: 8, takeProfit: 15, status: 'active', dailyPnL: 0, totalPnL: 0, trades: 0 },
    { id: 'oracle', name: '走着瞧', emoji: '🔮', position: 15, stopLoss: 5, takeProfit: 10, status: 'active', dailyPnL: 0, totalPnL: 0, trades: 0 },
    { id: 'leader', name: '跟大哥', emoji: '👑', position: 15, stopLoss: 3, takeProfit: 6, status: 'active', dailyPnL: 0, totalPnL: 0, trades: 0 },
    { id: 'hitchhiker', name: '搭便车', emoji: '🍀', position: 10, stopLoss: 5, takeProfit: 8, status: 'active', dailyPnL: 0, totalPnL: 0, trades: 0 },
    { id: 'wool', name: '薅羊毛', emoji: '💰', position: 3, stopLoss: 2, takeProfit: 20, status: 'active', dailyPnL: 0, totalPnL: 0, trades: 0 },
    { id: 'poor', name: '穷孩子', emoji: '👶', position: 2, stopLoss: 1, takeProfit: 30, status: 'active', dailyPnL: 0, totalPnL: 0, trades: 0 },
  ]);

  // ─── 数据获取 ────────────────────────────────

  const fetchData = useCallback(async () => {
    try {
      const [marketRes, signalsRes, statsRes, portfolioRes, perfRes] = await Promise.all([
        fetch(`${API_BASE}/api/market`).catch(() => null),
        fetch(`${API_BASE}/api/signals?limit=20`).catch(() => null),
        fetch(`${API_BASE}/api/stats`).catch(() => null),
        fetch(`${API_BASE}/api/portfolio`).catch(() => null),
        fetch(`${API_BASE}/api/performance`).catch(() => null),
      ]);
      const errors: string[] = [];
      if (marketRes?.ok) { const d = await marketRes.json(); setMarketData(d.data || []); } else errors.push('market');
      if (signalsRes?.ok) { const d = await signalsRes.json(); setSignals(d.signals || []); } else errors.push('signals');
      if (statsRes?.ok) { const d = await statsRes.json(); if (d.data?.version) setAppVersion(d.data.version); } else errors.push('stats');
      if (portfolioRes?.ok) { const d = await portfolioRes.json(); setPortfolio(d); }
      if (perfRes?.ok) {
        const d = await perfRes.json();
        setPerformance(d);
        if (d.investment_tools) {
          setTools(prev => prev.map(t => {
            const inv = d.investment_tools[t.id];
            const work = d.work_tools?.[t.id];
            if (inv) return { ...t, position: inv.weight || t.position, status: inv.status === 'disabled' ? 'inactive' : 'active' };
            if (work) return { ...t, position: work.weight || t.position };
            return t;
          }));
        }
      }
      if (errors.length > 0) setError(`API: ${errors.join(', ')}`);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch data');
      setLoading(false);
    }
  }, []);

  // ─── 赚钱扫描 ──────────────────────────────

  const scanEarnTasks = useCallback(async () => {
    setScanLoading(true);
    try {
      const [airdropRes, crowdRes, compareRes] = await Promise.all([
        fetch(`${API_BASE}/api/earn/v3/airdrop/top?limit=10`).catch(() => null),
        fetch(`${API_BASE}/api/earn/v3/crowd/top?limit=10`).catch(() => null),
        fetch(`${API_BASE}/api/earn/v3/compare`).catch(() => null),
      ]);
      if (airdropRes?.ok) {
        const d = await airdropRes.json();
        setAirdropTasks(d.tasks || []);
      }
      if (crowdRes?.ok) {
        const d = await crowdRes.json();
        setCrowdTasks(d.tasks || []);
      }
      if (compareRes?.ok) {
        const d = await compareRes.json();
        setEarnStats(d.compare || null);
      }
    } catch (err) {
      console.error('scan error:', err);
    }
    setScanLoading(false);
  }, []);

  const grabTask = useCallback(async (taskId: string, type: 'airdrop' | 'crowd') => {
    try {
      const endpoint = type === 'airdrop' ? 'grab' : 'grab';
      const res = await fetch(`${API_BASE}/api/earn/v3/${type}/${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task_id: taskId }),
      }).catch(() => null);
      if (res?.ok) {
        const d = await res.json();
        setGrabResults(prev => [{ ...d, time: new Date().toLocaleTimeString() }, ...prev.slice(0, 9)]);
        if (d.grabbed) {
          // 刷新列表
          scanEarnTasks();
        }
      }
    } catch (err) {
      console.error('grab error:', err);
    }
  }, [scanEarnTasks]);

  const batchGrab = useCallback(async (type: 'airdrop' | 'crowd', taskIds: string[]) => {
    try {
      const res = await fetch(`${API_BASE}/api/earn/v3/${type}/batch-grab?max_parallel=5`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(taskIds),
      }).catch(() => null);
      if (res?.ok) {
        const d = await res.json();
        setGrabResults(prev => [{ ...d, time: new Date().toLocaleTimeString() }, ...prev.slice(0, 9)]);
        scanEarnTasks();
      }
    } catch (err) {
      console.error('batch grab error:', err);
    }
  }, [scanEarnTasks]);

  useEffect(() => { fetchData(); }, [fetchData]);
  useEffect(() => { if (activeTab === 'earn') scanEarnTasks(); }, [activeTab, scanEarnTasks]);

  // ─── 渲染函数 ──────────────────────────────

  const renderDashboard = () => (
    <div className="dashboard">
      <div className="overview-cards">
        <div className="card stat-card">
          <div className="stat-label">平台评分</div>
          <div className="stat-value large">{simulationScore.toFixed(1)}</div>
          <div className="stat-change positive">↑ 0.3%</div>
        </div>
        <div className="card stat-card">
          <div className="stat-label">总资产</div>
          <div className="stat-value large">${_portfolio?.totalValue?.toLocaleString() || '—'}</div>
          <div className="stat-change positive">+$1,234</div>
        </div>
        <div className="card stat-card">
          <div className="stat-label">胜率</div>
          <div className="stat-value large">64.5%</div>
          <div className="stat-change negative">-2.1%</div>
        </div>
        <div className="card stat-card">
          <div className="stat-label">日收益</div>
          <div className="stat-value large">+2.23%</div>
          <div className="stat-change positive">ETH策略</div>
        </div>
      </div>
      <div className="card layer-scores">
        <h3>📊 25维度分层评分</h3>
        <div className="layer-grid">
          {(['A','B','C','D','E'] as Layer[]).map(l => (
            <div key={l} className="layer-item" onClick={() => l === 'B' ? setActiveTab('tools') : l === 'C' ? setActiveTab('trends') : null}>
              <span className={`layer-badge ${l}`}>{l}</span>
              <span className="layer-name">{{A:'投资组合',B:'投资工具',C:'趋势判断',D:'底层资源',E:'运营支撑'}[l]}</span>
              <span className="layer-score">{layerScores[l].toFixed(1)}</span>
            </div>
          ))}
        </div>
      </div>
      <div className="card market-section">
        <h3>📈 市场行情</h3>
        <div className="market-grid">
          {marketData.slice(0, 6).map(m => (
            <div key={m.symbol} className="market-item">
              <span className="symbol">{m.symbol}</span>
              <span className="price">${m.price?.toFixed(2) || '—'}</span>
              <span className={`change ${(m.change24h || 0) >= 0 ? 'positive' : 'negative'}`}>
                {(m.change24h || 0) >= 0 ? '↑' : '↓'} {Math.abs(m.change24h || 0).toFixed(2)}%
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderTools = () => (
    <div className="tools-section">
      <h2>🎛️ 北斗七鑫投资工具</h2>
      <div className="tools-grid">
        {tools.map(tool => (
          <div key={tool.id} className={`card tool-card ${tool.status}`}>
            <div className="tool-header">
              <span className="tool-emoji">{tool.emoji}</span>
              <span className="tool-name">{tool.name}</span>
              <span className={`status-badge ${tool.status}`}>{tool.status === 'active' ? '运行中' : tool.status === 'paused' ? '暂停' : '关闭'}</span>
            </div>
            <div className="tool-config">
              <div className="config-row"><span>仓位:</span><span className="value">{tool.position}%</span></div>
              <div className="config-row"><span>止损:</span><span className="value danger">{tool.stopLoss}%</span></div>
              <div className="config-row"><span>止盈:</span><span className="value success">{tool.takeProfit}%</span></div>
            </div>
            <div className="tool-stats">
              <div className="stat"><span className="label">日盈亏</span><span className={`value ${tool.dailyPnL >= 0 ? 'positive' : 'negative'}`}>{tool.dailyPnL >= 0 ? '+' : ''}{tool.dailyPnL.toFixed(2)}</span></div>
              <div className="stat"><span className="label">总盈亏</span><span className={`value ${tool.totalPnL >= 0 ? 'positive' : 'negative'}`}>{tool.totalPnL >= 0 ? '+' : ''}{tool.totalPnL.toFixed(2)}</span></div>
              <div className="stat"><span className="label">交易数</span><span className="value">{tool.trades}</span></div>
            </div>
            <div className="tool-actions">
              <button className="btn-small">配置</button>
              <button className={`btn-small ${tool.status === 'active' ? 'warning' : 'success'}`}>{tool.status === 'active' ? '暂停' : '启动'}</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderTrends = () => (
    <div className="trends-section">
      <h2>🔮 趋势判断层</h2>
      <div className="trends-grid">
        <div className="card trend-card"><h4>📡 声纳库趋势模型</h4><div className="trend-status active">运行中</div><div className="trend-models">20+ 趋势模型</div></div>
        <div className="card trend-card"><h4>🔮 预言机市场</h4><div className="trend-status active">活跃</div><div className="trend-markets">6 大预测市场</div></div>
        <div className="card trend-card"><h4>🧠 MiroFish 共识</h4><div className="trend-status active">1000 Agents</div><div className="trend-rounds">95.1/100 评分</div></div>
        <div className="card trend-card"><h4>💢 市场情绪</h4><div className="trend-status neutral">中性</div><div className="trend-sentiment">恐惧贪婪: 45</div></div>
      </div>
    </div>
  );

  const renderSignals = () => (
    <div className="signals-section">
      <h2>📡 交易信号</h2>
      <div className="signals-list">
        {signals.length > 0 ? signals.slice(0, 10).map(signal => (
          <div key={signal.id} className={`card signal-card ${signal.type}`}>
            <span className="signal-type">{signal.type === 'buy' ? '🟢 买入' : '🔴 卖出'}</span>
            <span className="signal-symbol">{signal.symbol}</span>
            <span className="signal-strength">强度: {signal.strength}%</span>
          </div>
        )) : <div className="card">暂无信号</div>}
      </div>
    </div>
  );

  const renderPortfolio = () => (
    <div className="portfolio-section">
      <h2>💼 投资组合 V10</h2>
      <div className="card portfolio-summary">
        <div className="summary-row"><span>总资金</span><span className="large">${performance?.total_capital?.toLocaleString() || '100,000'}</span></div>
        <div className="summary-row"><span>投资池 (80%)</span><span className="positive">${performance?.investment_pool?.toLocaleString() || '80,000'}</span></div>
        <div className="summary-row"><span>打工池 (20%)</span><span className="positive">${performance?.work_pool?.toLocaleString() || '20,000'}</span></div>
      </div>
      <div className="card allocation">
        <h4>📊 投资工具分配 (5个)</h4>
        <div className="allocation-bars">
          {Object.entries(performance?.investment_tools || {}).map(([id, tool]: [string, any]) => (
            <div key={id} className="allocation-row">
              <span>{tool.name}</span>
              <div className="bar-container"><div className="bar" style={{ width: `${tool.allocation / (performance?.investment_pool || 80000) * 100}%`, backgroundColor: tool.color, opacity: tool.status === 'disabled' ? 0.3 : 1 }}></div></div>
              <span className={tool.status === 'disabled' ? 'disabled' : ''}>${(tool.allocation || 0).toLocaleString()} ({tool.weight}%)</span>
            </div>
          ))}
        </div>
      </div>
      <div className="card allocation work-tools">
        <h4>💰 打工工具 (2个) - 现金流收集</h4>
        <div className="allocation-bars">
          {Object.entries(performance?.work_tools || {}).map(([id, tool]: [string, any]) => (
            <div key={id} className="allocation-row">
              <span>{tool.name}</span>
              <div className="bar-container"><div className="bar" style={{ width: `${tool.allocation / (performance?.work_pool || 20000) * 100}%`, backgroundColor: tool.color }}></div></div>
              <span>${(tool.allocation || 0).toLocaleString()} (现金流{tool.cashflow_rate * 100}%)</span>
            </div>
          ))}
        </div>
        <div className="cashflow-status"><span>💵 现金流池: ${(performance?.cashflow_pool || 0).toLocaleString()}</span></div>
      </div>
    </div>
  );

  // ─── 赚钱页面 (V3找单·选品·抢单) ─────────────────────────

  const renderEarn = () => (
    <div className="earn-section">
      <div className="earn-header">
        <h2>💰 赚钱中心 V3</h2>
        <div className="earn-tabs">
          <button className={earnTab === 'airdrop' ? 'active' : ''} onClick={() => setEarnTab('airdrop')}>💰 薅羊毛</button>
          <button className={earnTab === 'crowd' ? 'active' : ''} onClick={() => setEarnTab('crowd')}>👶 穷孩子</button>
        </div>
        <button className="btn-scan" onClick={scanEarnTasks} disabled={scanLoading}>
          {scanLoading ? '🔄 扫描中...' : '🔍 全源扫描'}
        </button>
      </div>

      {/* 统计概览 */}
      {earnStats && (
        <div className="earn-stats-bar">
          {earnTab === 'airdrop' ? (
            <>
              <div className="earn-stat"><span className="label">任务数</span><span className="value">{earnStats.airdrop?.total_tasks || 0}</span></div>
              <div className="earn-stat"><span className="label">P0优先</span><span className="value hot">{earnStats.airdrop?.p0_tasks || 0}</span></div>
              <div className="earn-stat"><span className="label">潜在收益</span><span className="value">${earnStats.airdrop?.net_potential_usd || 0}</span></div>
            </>
          ) : (
            <>
              <div className="earn-stat"><span className="label">任务数</span><span className="value">{earnStats.crowd?.total_tasks || 0}</span></div>
              <div className="earn-stat"><span className="label">热门</span><span className="value hot">{earnStats.crowd?.hot_tasks || 0}</span></div>
              <div className="earn-stat"><span className="label">平均时薪</span><span className="value">${earnStats.crowd?.avg_hourly_rate || 0}/hr</span></div>
            </>
          )}
        </div>
      )}

      <div className="earn-content">
        {/* 任务列表 */}
        <div className="earn-tasks-panel">
          <h4>{earnTab === 'airdrop' ? '💰 空投任务 (多因子评分)' : '👶 众包任务 (时薪排序)'}</h4>
          <div className="task-list">
            {(earnTab === 'airdrop' ? airdropTasks : crowdTasks).map((task, i) => (
              <div key={task.task_id} className={`task-card ${task.priority?.startsWith('P0') || task.priority === 'P1' ? 'priority-high' : ''}`}>
                <div className="task-rank">#{i + 1}</div>
                <div className="task-info">
                  <div className="task-name">{task.name}</div>
                  <div className="task-meta">
                    {task.project && <span className="tag">{task.project}</span>}
                    {task.platform && <span className="tag">{task.platform}</span>}
                    {task.chain && <span className="tag">{task.chain}</span>}
                    <span className="priority-badge">{task.priority}</span>
                  </div>
                  <div className="task-scores">
                    <span className="score-tag">评分: {task.total_score.toFixed(1)}</span>
                    {task.reliability && <span className="score-tag">可靠: {task.reliability}%</span>}
                    {task.difficulty && <span className="score-tag">{task.difficulty}</span>}
                  </div>
                </div>
                <div className="task-reward">
                  <div className="reward-main">
                    {task.expected_return_usd ? `$${task.expected_return_usd}` : task.reward_usd ? `$${task.reward_usd}` : '—'}
                  </div>
                  <div className="reward-sub">
                    {task.net_return && <span>净$:{task.net_return} </span>}
                    {task.hourly_rate && <span>{task.hourly_rate}/hr</span>}
                  </div>
                </div>
                <div className="task-slots">
                  <div className="slots-bar">
                    <div className="slots-fill" style={{ width: `${Math.min(100, (task.remaining_slots || 50) / 2)}%` }}></div>
                  </div>
                  <span>{task.remaining_slots}名额</span>
                </div>
                <button className="btn-grab" onClick={() => grabTask(task.task_id, earnTab)}>⚡抢</button>
              </div>
            ))}
            {(earnTab === 'airdrop' ? airdropTasks : crowdTasks).length === 0 && (
              <div className="empty-state">点击"全源扫描"获取任务</div>
            )}
          </div>
        </div>

        {/* 抢单结果 & 快捷操作 */}
        <div className="earn-actions-panel">
          <h4>⚡ 快捷操作</h4>
          <div className="quick-actions">
            <button className="btn-batch" onClick={() => {
              const top3 = (earnTab === 'airdrop' ? airdropTasks : crowdTasks).slice(0, 3).map(t => t.task_id);
              if (top3.length > 0) batchGrab(earnTab, top3);
            }}>
              ⚡⚡⚡ 抢TOP3
            </button>
            <button className="btn-batch" onClick={() => {
              const p0 = (earnTab === 'airdrop' ? airdropTasks : crowdTasks).filter(t => t.priority === 'P0' || t.priority === 'P1').map(t => t.task_id);
              if (p0.length > 0) batchGrab(earnTab, p0);
            }}>
              ⚡ 抢P0/P1
            </button>
          </div>

          <h4 style={{marginTop: '16px'}}>📋 抢单记录</h4>
          <div className="grab-results">
            {grabResults.length > 0 ? grabResults.map((r, i) => (
              <div key={i} className={`grab-result ${r.grabbed ? 'success' : 'failed'}`}>
                <span className="grab-icon">{r.grabbed ? '✅' : '❌'}</span>
                <span className="grab-msg">{r.message || (r.grabbed ? `成功 ${r.grabbed}/${r.total}` : r.error || '失败')}</span>
                <span className="grab-time">{r.time}</span>
              </div>
            )) : <div className="empty-state">暂无抢单记录</div>}
          </div>

          <h4 style={{marginTop: '16px'}}>📊 安全机制</h4>
          <div className="security-info">
            <div className="security-item">🚫 禁止授权链接</div>
            <div className="security-item">🔒 资金完全隔离</div>
            <div className="security-item">⛽ Gas费监控</div>
            <div className="security-item">🔍 任务安全审计</div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderSettings = () => (
    <div className="settings-section">
      <h2>⚙️ 系统设置</h2>
      <div className="settings-grid">
        <div className="card setting-card">
          <h4>🛡️ 风控规则</h4>
          <div className="setting-row"><span>总仓位上限</span><span>80%</span></div>
          <div className="setting-row"><span>单笔风险</span><span>5%</span></div>
          <div className="setting-row"><span>日亏损熔断</span><span>15%</span></div>
        </div>
        <div className="card setting-card">
          <h4>🔧 平台配置</h4>
          <div className="setting-row"><span>交易模式</span><span>Dry Run</span></div>
          <div className="setting-row"><span>API延迟</span><span>7ms</span></div>
          <div className="setting-row"><span>版本</span><span>{appVersion}</span></div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="app">
      <nav className="nav">
        <div className="nav-brand"><span className="logo">🪿</span><span className="title">GO2SE 北斗七鑫 {appVersion}</span></div>
        <div className="nav-tabs">
          <NavLink to="/" className={({isActive}) => isActive ? 'active' : ''} end>总览</NavLink>
          <NavLink to="/tools" className={({isActive}) => isActive ? 'active' : ''}>工具</NavLink>
          <NavLink to="/trends" className={({isActive}) => isActive ? 'active' : ''}>趋势</NavLink>
          <NavLink to="/signals" className={({isActive}) => isActive ? 'active' : ''}>信号</NavLink>
          <NavLink to="/portfolio" className={({isActive}) => isActive ? 'active' : ''}>组合</NavLink>
          <NavLink to="/earn" className={({isActive}) => isActive ? 'active' : ''}>💰赚钱</NavLink>
          <NavLink to="/recommend" className={({isActive}) => isActive ? 'active' : ''}>🎯推荐</NavLink>
          <NavLink to="/settings" className={({isActive}) => isActive ? 'active' : ''}>设置</NavLink>
        </div>
        <div className="nav-status"><span className="status-dot"></span><span>{appVersion}</span></div>
      </nav>
      <main className="main">
        {loading ? <div className="loading"><div className="spinner"></div><p>加载中...</p></div> : error ? <div className="error-banner">{error}</div> : (
          <Routes>
            <Route path="/" element={renderDashboard()} />
            <Route path="/tools" element={renderTools()} />
            <Route path="/trends" element={<Trends />} />
            <Route path="/signals" element={<Signals signals={signals} />} />
            <Route path="/portfolio" element={<Portfolio performance={performance} />} />
            <Route path="/earn" element={renderEarn()} />
            <Route path="/recommend" element={<RecommendationHub />} />
            <Route path="/settings" element={<Settings appVersion={appVersion} />} />
          </Routes>
        )}
      </main>
      <footer className="footer">
        <span>🪿 GO2SE 北斗七鑫 {appVersion}</span><span>|</span><span>评分: {simulationScore.toFixed(1)}</span><span>|</span><span>25维度全向仿真</span>
      </footer>
    </div>
  );
}

// Make Dashboard props compatible
function renderDashboard() {
  return <Dashboard simulationScore={simulationScore} layerScores={layerScores} marketData={marketData} portfolio={_portfolio} onNavigateToTools={() => navigate('/tools')} onNavigateToTrends={() => navigate('/trends')} />;
}

function renderTools() {
  return <Tools tools={tools} />;
}

export default App;
