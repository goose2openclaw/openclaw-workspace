// vv6 API Bridge - Lobster普通模式前后台打通
const API_BASE = 'http://localhost:8006';

const VV6Bridge = {
  _autoRefresh: true,
  _refreshInterval: null,
  _listeners: [],,

  addListener(cb) { this._listeners.push(cb); },

  _notify(data) {
    this._listeners.forEach(cb => { try { cb(data); } catch(e) {} });
  },

  async fetchSignal() {
    try {
      const res = await fetch(`${API_BASE}/api/switch/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol: 'BTCUSDT', confidence: 80, mode: 'normal' })
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (e) {
      console.warn('Signal fetch failed:', e.message);
      return null;
    }
  },

  async fetchMarket() {
    try {
      const res = await fetch('http://localhost:8000/api/v7/market/summary');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return (await res.json()).data;
    } catch (e) {
      console.warn('Market fetch failed:', e.message);
      return null;
    }
  },

  async setMode(mode) {
    try {
      const res = await fetch(`${API_BASE}/api/switch/mode`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode })
      });
      return await res.json();
    } catch (e) { return { error: e.message }; }
  },

  startAutoRefresh(intervalMs = 30000) {
    this._autoRefresh = true;
    if (this._refreshInterval) clearInterval(this._refreshInterval);
    this._refreshInterval = setInterval(() => {
      if (this._autoRefresh) this.refreshAll();
    }, intervalMs);
    this.refreshAll();
  },

  stopAutoRefresh() {
    this._autoRefresh = false;
    if (this._refreshInterval) {
      clearInterval(this._refreshInterval);
      this._refreshInterval = null;
    }
  },

  async refreshAll() {
    const [signalData, marketData] = await Promise.all([
      this.fetchSignal(),
      this.fetchMarket()
    ]);
    this._notify({ signal: signalData, market: marketData });
    return { signal: signalData, market: marketData };
  },

  updateUI({ signal, market }) {
    if (!signal) return;

    const sig = signal.signal || signal;
    const dir = (sig.direction || 'hold').toUpperCase();
    const mi = sig.mi || 0;
    const regime = sig.regime || 'neutral';
    const reason = sig.reasoning || sig.reason || '';

    // Signal badge
    const badge = document.getElementById('currentSignal');
    if (badge) {
      badge.className = `signal-badge ${dir.toLowerCase()}`;
      const icons = { LONG: '📈', SHORT: '📉', HOLD: '⏸️' };
      const labels = { LONG: '做多', SHORT: '做空', HOLD: '观望' };
      badge.textContent = `${icons[dir] || '❓'} ${labels[dir] || dir}`;
    }

    // Regime badge
    const regBadge = document.getElementById('regimeBadge');
    if (regBadge) {
      regBadge.className = `regime-badge ${regime.toLowerCase()}`;
      const regimeLabels = { bull: '🐂 牛市', bear: '🐻 熊市', neutral: '⚖️ 中性' };
      regBadge.textContent = regimeLabels[regime.toLowerCase()] || regime;
    }

    // Mi score
    const miEl = document.getElementById('miScore');
    if (miEl) miEl.textContent = mi.toFixed(4);

    // Position display
    if (dir === 'LONG' || dir === 'SHORT') {
      const posDir = document.getElementById('posDirection');
      const posPct = document.getElementById('posPct');
      const posSL = document.getElementById('posSL');
      if (posDir) posDir.textContent = dir === 'LONG' ? '📈 做多' : '📉 做空';
      if (posPct) posPct.textContent = `${sig.position_pct || 10}%`;
      if (posSL) posSL.textContent = `${sig.stop_loss_pct || 3.0}%`;
    }

    // Mode tag
    const modeTag = document.getElementById('modeTag');
    if (modeTag) modeTag.textContent = sig.mode === 'expert' ? '⚡ 专家模式' : '🦞 普通模式';

    // Signal feed
    this.appendToFeed({ dir, mi, regime, reason, ts: new Date() });

    // Backend status
    const statusEl = document.getElementById('backendStatus');
    if (statusEl) { statusEl.textContent = '● 已连接'; statusEl.style.color = 'var(--primary)'; }
  },

  _feedItems: [],
  appendToFeed(item) {
    this._feedItems.unshift(item);
    if (this._feedItems.length > 20) this._feedItems.pop();
    const feed = document.getElementById('signalFeed');
    if (!feed) return;
    feed.innerHTML = this._feedItems.map(it => `
      <div class="signal-feed-item ${it.dir.toLowerCase()}" style="padding:12px 16px;background:var(--card-bg);border-radius:8px;border-left:3px solid;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <div style="display:flex;align-items:center;gap:10px;">
            <span class="signal-badge ${it.dir.toLowerCase()}" style="font-size:12px;">${it.dir}</span>
            <span style="font-family:'JetBrains Mono',monospace;font-size:12px;color:var(--text-dim);">Mi=${it.mi?.toFixed(4)}</span>
            <span style="font-size:12px;color:var(--text-dim);">${it.regime}</span>
          </div>
          <span style="font-size:11px;color:var(--text-dim);">${it.ts.toLocaleTimeString()}</span>
        </div>
        ${it.reason ? `<div style="font-size:12px;color:var(--text-dim);margin-top:4px;">${it.reason}</div>` : ''}
      </div>
    `).join('');
  }
};
