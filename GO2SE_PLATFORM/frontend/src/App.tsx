/**
 * GO2SE V9 双脑架构前台
 * ====================
 * 四级页面 + 左右脑切换 + 龙虾模块
 */

import React, { useState, useEffect, useCallback } from 'react';

// ============================================================================
// 类型定义
// ============================================================================

interface BrainStatus {
  brain_id: string;
  mode: string;
  state: string;
  health: number;
  alive: boolean;
}

interface DualBrainStatus {
  active_brain: string;
  active_mode: string;
  left_brain: BrainStatus;
  right_brain: BrainStatus;
}

interface WalletStatus {
  main_wallet: { balance: number };
  transfer_wallet: { balance: number };
  exchange_walllets: Record<string, { balance: number }>;
  total_assets: number;
}

interface LobsterStatus {
  retro_count: number;
  simulation_count: number;
  optimization_count: number;
}

interface EngineStatus {
  version: string;
  running: boolean;
  uptime: number;
  brain_manager: DualBrainStatus;
  lobster: LobsterStatus;
}

// ============================================================================
// API 客户端
// ============================================================================

const API_BASE = '/api/dual-brain';

const api = {
  async getStatus(): Promise<EngineStatus> {
    const res = await fetch(`${API_BASE}/status`);
    return res.json();
  },

  async sendHeartbeat(): Promise<DualBrainStatus> {
    const res = await fetch(`${API_BASE}/heartbeat`, { method: 'POST' });
    return res.json();
  },

  async switchBrain(target: string): Promise<{ success: boolean; active_brain: string; mode: string }> {
    const res = await fetch(`${API_BASE}/switch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target })
    });
    return res.json();
  },

  async getWalletStatus(): Promise<WalletStatus> {
    const res = await fetch(`${API_BASE}/wallet-status`);
    return res.json();
  },

  async getLobsterStatus(): Promise<LobsterStatus> {
    const res = await fetch(`${API_BASE}/lobster/status`);
    return res.json();
  },

  async runRetro(): Promise<any> {
    const res = await fetch(`${API_BASE}/lobster/retro`, { method: 'POST' });
    return res.json();
  },

  async runSimulation(): Promise<any> {
    const res = await fetch(`${API_BASE}/lobster/simulation`, { method: 'POST' });
    return res.json();
  },

  async runOptimization(): Promise<any> {
    const res = await fetch(`${API_BASE}/lobster/optimization`, { method: 'POST' });
    return res.json();
  },

  async runFullCycle(): Promise<any> {
    const res = await fetch(`${API_BASE}/lobster/full-cycle`, { method: 'POST' });
    return res.json();
  }
};

// ============================================================================
// 左右脑切换组件
// ============================================================================

const BrainSwitcher: React.FC<{
  status: DualBrainStatus;
  onSwitch: (target: string) => void;
}> = ({ status, onSwitch }) => {
  const isLeftActive = status.active_brain === 'left';

  return (
    <div className="brain-switcher">
      <div className="brain-indicators">
        <div className={`brain-indicator left ${isLeftActive ? 'active' : ''}`}>
          <span className="brain-icon">🧠</span>
          <span className="brain-label">左脑</span>
          <span className="brain-mode">{status.left_brain.mode === 'normal' ? '普通' : '专家'}</span>
          <div className={`health-bar ${status.left_brain.health > 0.7 ? 'good' : status.left_brain.health > 0.4 ? 'warning' : 'bad'}`}>
            <div className="health-fill" style={{ width: `${status.left_brain.health * 100}%` }} />
          </div>
        </div>

        <div className="switch-arrows">
          <button onClick={() => onSwitch('left')} disabled={isLeftActive}>
            ◀
          </button>
          <button onClick={() => onSwitch('right')} disabled={!isLeftActive}>
            ▶
          </button>
        </div>

        <div className={`brain-indicator right ${!isLeftActive ? 'active' : ''}`}>
          <span className="brain-icon">🧠</span>
          <span className="brain-label">右脑</span>
          <span className="brain-mode">{status.right_brain.mode === 'normal' ? '普通' : '专家'}</span>
          <div className={`health-bar ${status.right_brain.health > 0.7 ? 'good' : status.right_brain.health > 0.4 ? 'warning' : 'bad'}`}>
            <div className="health-fill" style={{ width: `${status.right_brain.health * 100}%` }} />
          </div>
        </div>
      </div>

      <div className="active-info">
        当前活跃: <strong>{status.active_brain === 'left' ? '🧠 左脑' : '🧠 右脑'}</strong>
        ({status.active_mode === 'normal' ? '普通模式' : '专家模式'})
      </div>
    </div>
  );
};

// ============================================================================
// 钱包组件
// ============================================================================

const WalletPanel: React.FC<{ wallet: WalletStatus }> = ({ wallet }) => {
  return (
    <div className="wallet-panel">
      <h3>💰 钱包架构</h3>
      <div className="wallet-flow">
        <div className="wallet-item main">
          <span className="wallet-label">主钱包</span>
          <span className="wallet-balance">${wallet.main_wallet.balance.toLocaleString()}</span>
        </div>
        <div className="wallet-arrow">→</div>
        <div className="wallet-item transfer">
          <span className="wallet-label">中转钱包</span>
          <span className="wallet-balance">${wallet.transfer_wallet.balance.toLocaleString()}</span>
        </div>
        <div className="wallet-arrow">→</div>
        <div className="wallet-item exchanges">
          <span className="wallet-label">交易所</span>
          <span className="wallet-balance">
            ${Object.values(wallet.exchange_wallets || {}).reduce((s, w) => s + w.balance, 0).toLocaleString()}
          </span>
        </div>
      </div>
      <div className="total-assets">
        总资产: <strong>${wallet.total_assets.toLocaleString()}</strong>
      </div>
    </div>
  );
};

// ============================================================================
// 龙虾模块组件
// ============================================================================

const LobsterPanel: React.FC<{
  lobster: LobsterStatus;
  onRetro: () => void;
  onSimulation: () => void;
  onOptimization: () => void;
  onFullCycle: () => void;
}> = ({ lobster, onRetro, onSimulation, onOptimization, onFullCycle }) => {
  return (
    <div className="lobster-panel">
      <h3>🦞 龙虾模块</h3>
      <div className="lobster-stats">
        <div className="stat">
          <span className="stat-label">复盘</span>
          <span className="stat-value">{lobster.retro_count}</span>
        </div>
        <div className="stat">
          <span className="stat-label">仿真</span>
          <span className="stat-value">{lobster.simulation_count}</span>
        </div>
        <div className="stat">
          <span className="stat-label">优化</span>
          <span className="stat-value">{lobster.optimization_count}</span>
        </div>
      </div>
      <div className="lobster-actions">
        <button onClick={onRetro}>📊 复盘</button>
        <button onClick={onSimulation}>🧠 仿真</button>
        <button onClick={onOptimization}>⚙️ 优化</button>
        <button onClick={onFullCycle} className="primary">🚀 完整周期</button>
      </div>
    </div>
  );
};

// ============================================================================
// 一级页面: 总览
// ============================================================================

const OverviewPage: React.FC<{ status: EngineStatus }> = ({ status }) => {
  return (
    <div className="page page-overview">
      <h2>📊 总览</h2>

      <div className="overview-grid">
        <div className="card status-card">
          <h3>🧠 系统状态</h3>
          <div className="status-info">
            <div>版本: {status.version}</div>
            <div>运行时间: {Math.floor(status.uptime / 60)}分钟</div>
            <div>状态: <span className={status.running ? 'green' : 'red'}>
              {status.running ? '● 运行中' : '○ 已停止'}
            </span></div>
          </div>
        </div>

        <div className="card brain-card">
          <h3>🧠 左右脑状态</h3>
          <BrainSwitcher
            status={status.brain_manager}
            onSwitch={async (t) => { await api.switchBrain(t); }}
          />
        </div>

        <div className="card wallet-card">
          <WalletPanel wallet={{ ...status.brain_manager, main_wallet: { balance: 100000 }, transfer_wallet: { balance: 50000 }, exchange_wallets: { binance: { balance: 30000 }, bybit: { balance: 20000 }, okx: { balance: 15000 } }, total_assets: 215000 }} />
        </div>

        <div className="card lobster-card">
          <LobsterPanel
            lobster={status.lobster}
            onRetro={async () => { await api.runRetro(); }}
            onSimulation={async () => { await api.runSimulation(); }}
            onOptimization={async () => { await api.runOptimization(); }}
            onFullCycle={async () => { await api.runFullCycle(); }}
          />
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// 二级页面: 交易
// ============================================================================

const TradingPage: React.FC = () => {
  const [trades, setTrades] = useState<any[]>([]);

  return (
    <div className="page page-trading">
      <h2>📈 交易</h2>

      <div className="trading-grid">
        <div className="card">
          <h3>🐰 打兔子</h3>
          <div className="tool-status">30%仓位 | 2.0x杠杆</div>
          <button>查看详情</button>
        </div>

        <div className="card">
          <h3>🐹 打地鼠</h3>
          <div className="tool-status">25%仓位 | 2.5x杠杆</div>
          <button>查看详情</button>
        </div>

        <div className="card">
          <h3>🔮 走着瞧</h3>
          <div className="tool-status">20%仓位 | 1.5x杠杆</div>
          <button>查看详情</button>
        </div>

        <div className="card">
          <h3>👑 跟大哥</h3>
          <div className="tool-status">15%仓位 | 1.5x杠杆</div>
          <button>查看详情</button>
        </div>

        <div className="card">
          <h3>🍀 搭便车</h3>
          <div className="tool-status">5%仓位 | 1.0x杠杆</div>
          <button>查看详情</button>
        </div>

        <div className="card">
          <h3>💰 薅羊毛</h3>
          <div className="tool-status">3%仓位 | 1.0x杠杆</div>
          <button>查看详情</button>
        </div>

        <div className="card">
          <h3>👶 穷孩子</h3>
          <div className="tool-status">2%仓位 | 1.0x杠杆</div>
          <button>查看详情</button>
        </div>
      </div>

      <div className="card trades-history">
        <h3>📜 交易历史</h3>
        <table>
          <thead>
            <tr>
              <th>时间</th>
              <th>工具</th>
              <th>方向</th>
              <th>收益</th>
            </tr>
          </thead>
          <tbody>
            {trades.length === 0 ? (
              <tr><td colSpan={4}>暂无交易记录</td></tr>
            ) : trades.map((t, i) => (
              <tr key={i}>
                <td>{t.time}</td>
                <td>{t.tool}</td>
                <td>{t.direction}</td>
                <td className={t.profit > 0 ? 'green' : 'red'}>{t.profit > 0 ? '+' : ''}{t.profit}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// ============================================================================
// 三级页面: 工具详情
// ============================================================================

const ToolsPage: React.FC = () => {
  const tools = [
    { id: 'rabbit', name: '🐰 打兔子', desc: '前20主流加密货币趋势跟踪', version: 'v4.0', capability: 5 },
    { id: 'mole', name: '🐹 打地鼠', desc: 'HFT套利+跨市场套利', version: 'v5.0', capability: 5 },
    { id: 'oracle', name: '🔮 走着瞧', desc: '预测市场+决策等式', version: 'v4.0', capability: 5 },
    { id: 'leader', name: '👑 跟大哥', desc: '做市商跟单', version: 'v4.0', capability: 5 },
    { id: 'hitchhiker', name: '🍀 搭便车', desc: '跟单分成', version: 'v4.0', capability: 5 },
    { id: 'airdrop', name: '💰 薅羊毛', desc: '空投猎手', version: 'v4.0', capability: 5 },
    { id: 'crowdsourcing', name: '👶 穷孩子', desc: '众包打工', version: 'v4.0', capability: 5 },
  ];

  return (
    <div className="page page-tools">
      <h2>⚙️ 工具详情</h2>

      <div className="tools-list">
        {tools.map(tool => (
          <div className="tool-detail-card" key={tool.id}>
            <div className="tool-header">
              <h3>{tool.name}</h3>
              <span className="tool-version">{tool.version}</span>
            </div>
            <p className="tool-desc">{tool.desc}</p>
            <div className="tool-capabilities">
              <span>能力:</span>
              {[...Array(tool.capability)].map((_, i) => (
                <span key={i} className="capability-dot">●</span>
              ))}
            </div>
            <div className="tool-actions">
              <button>全域扫描</button>
              <button>深度扫描</button>
              <button>MiroFish选品</button>
              <button>抢单</button>
              <button>gstack复盘</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// ============================================================================
// 四级页面: 设置
// ============================================================================

const SettingsPage: React.FC = () => {
  return (
    <div className="page page-settings">
      <h2>⚙️ 设置</h2>

      <div className="settings-grid">
        <div className="card">
          <h3>🧠 左右脑配置</h3>
          <div className="setting-item">
            <label>左脑模式</label>
            <select defaultValue="normal">
              <option value="normal">普通模式</option>
              <option value="expert">专家模式</option>
            </select>
          </div>
          <div className="setting-item">
            <label>右脑模式</label>
            <select defaultValue="expert">
              <option value="normal">普通模式</option>
              <option value="expert">专家模式</option>
            </select>
          </div>
          <div className="setting-item">
            <label>自动切换</label>
            <input type="checkbox" defaultChecked />
          </div>
        </div>

        <div className="card">
          <h3>💰 钱包配置</h3>
          <div className="setting-item">
            <label>最大中转金额</label>
            <input type="number" defaultValue="10000" />
          </div>
          <div className="setting-item">
            <label>最小中转金额</label>
            <input type="number" defaultValue="1000" />
          </div>
          <div className="setting-item">
            <label>最低保留金额</label>
            <input type="number" defaultValue="20000" />
          </div>
        </div>

        <div className="card">
          <h3>🦞 龙虾模块</h3>
          <div className="setting-item">
            <label>自动复盘</label>
            <input type="checkbox" defaultChecked />
          </div>
          <div className="setting-item">
            <label>自动仿真</label>
            <input type="checkbox" defaultChecked />
          </div>
          <div className="setting-item">
            <label>优化周期(小时)</label>
            <input type="number" defaultValue="24" />
          </div>
        </div>

        <div className="card">
          <h3>📊 风控规则</h3>
          <div className="setting-item">
            <label>日亏损熔断</label>
            <input type="number" defaultValue="15" />%
          </div>
          <div className="setting-item">
            <label>单笔风险上限</label>
            <input type="number" defaultValue="5" />%
          </div>
          <div className="setting-item">
            <label>总仓位上限</label>
            <input type="number" defaultValue="80" />%
          </div>
        </div>
      </div>

      <div className="settings-actions">
        <button className="primary">保存设置</button>
        <button>重置默认</button>
      </div>
    </div>
  );
};

// ============================================================================
// 主应用
// ============================================================================

const App: React.FC = () => {
  const [currentPage, setCurrentPage] = useState<string>('overview');
  const [status, setStatus] = useState<EngineStatus | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchStatus = useCallback(async () => {
    try {
      const data = await api.getStatus();
      setStatus(data);
      setLoading(false);
    } catch (e) {
      console.error('Failed to fetch status:', e);
    }
  }, []);

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, [fetchStatus]);

  const handleSwitch = async (target: string) => {
    await api.switchBrain(target);
    await fetchStatus();
  };

  if (loading || !status) {
    return <div className="loading">加载中...</div>;
  }

  const renderPage = () => {
    switch (currentPage) {
      case 'overview': return <OverviewPage status={status} />;
      case 'trading': return <TradingPage />;
      case 'tools': return <ToolsPage />;
      case 'settings': return <SettingsPage />;
      default: return <OverviewPage status={status} />;
    }
  };

  return (
    <div className="go2se-app">
      <header className="app-header">
        <div className="header-left">
          <h1>🪿 GO2SE V9</h1>
          <span className="version">dual-brain</span>
        </div>
        <div className="header-right">
          <span className={`status-indicator ${status.brain_manager.active_brain === 'left' ? 'left' : 'right'}`}>
            🧠 {status.brain_manager.active_brain === 'left' ? '左脑' : '右脑'}
          </span>
        </div>
      </header>

      <nav className="app-nav">
        <button
          className={currentPage === 'overview' ? 'active' : ''}
          onClick={() => setCurrentPage('overview')}
        >
          📊 总览
        </button>
        <button
          className={currentPage === 'trading' ? 'active' : ''}
          onClick={() => setCurrentPage('trading')}
        >
          📈 交易
        </button>
        <button
          className={currentPage === 'tools' ? 'active' : ''}
          onClick={() => setCurrentPage('tools')}
        >
          ⚙️ 工具
        </button>
        <button
          className={currentPage === 'settings' ? 'active' : ''}
          onClick={() => setCurrentPage('settings')}
        >
          ⚙️ 设置
        </button>
      </nav>

      <main className="app-main">
        {renderPage()}
      </main>

      <footer className="app-footer">
        <span>GO2SE V9 Dual-Brain | {status.brain_manager.active_mode === 'normal' ? '普通模式' : '专家模式'}</span>
      </footer>
    </div>
  );
};

export default App;
