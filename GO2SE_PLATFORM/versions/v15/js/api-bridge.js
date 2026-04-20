// v15 API Bridge - 四脑决策系统前后台打通
const V15_API = 'http://localhost:8015';
const V15_MF = 'http://localhost:8020';

const V15Bridge = {
  _autoRefresh: true,
  _interval: null,
  _listeners: [],
  _lastRSI: 60,

  addListener(cb) { this._listeners.push(cb); },

  _notify(data) { this._listeners.forEach(cb => { try { cb(data); } catch(e) {} }); },

  async fetchDecision(brainVotes, regime, rsi) {
    try {
      const res = await fetch(`${V15_API}/api/decision/eq`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          brain_votes: brainVotes,
          mirofish_scores: {},
          regime: regime,
          rsi: rsi
        })
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (e) {
      console.warn('Decision fetch failed:', e.message);
      return null;
    }
  },

  async fetchMirofish() {
    try {
      const [miRes, dimsRes] = await Promise.all([
        fetch(`${V15_MF}/mi/sync`),
        fetch(`${V15_MF}/dimensions/learning`)
      ]);
      const mi = miRes.ok ? (await miRes.json()).unified_mi : null;
      const dims = dimsRes.ok ? await dimsRes.json() : null;
      return { mi, dims };
    } catch (e) {
      console.warn('MiroFish fetch failed:', e.message);
      return { mi: null, dims: null };
    }
  },

  async fetchMarket() {
    try {
      const res = await fetch('http://localhost:8000/api/v7/market/summary');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return (await res.json()).data;
    } catch (e) { return null; }
  },

  startAutoRefresh(intervalMs = 30000) {
    this._autoRefresh = true;
    if (this._interval) clearInterval(this._interval);
    this._interval = setInterval(() => { if (this._autoRefresh) this.refreshAll(); }, intervalMs);
    this.refreshAll();
  },

  stopAutoRefresh() {
    this._autoRefresh = false;
    if (this._interval) { clearInterval(this._interval); this._interval = null; }
  },

  async refreshAll() {
    const rsi = this._lastRSI;
    const regime = this._lastRegime || 'bull';
    const brains = { alpha: 0.85, beta: 0.80, gamma: 0.70, delta: 0.60 };
    const [decision, mirofish, market] = await Promise.all([
      this.fetchDecision(brains, regime, rsi),
      this.fetchMirofish(),
      this.fetchMarket()
    ]);
    this._notify({ decision, mirofish, market });
    return { decision, mirofish, market };
  },

  updateUI({ decision, mirofish, market }) {
    if (!decision) return;

    const dir = (decision.direction || 'HOLD').toUpperCase();
    const score = decision.final_score || 0;
    const reasoning = decision.reasoning || '';
    const components = decision.components || {};
    const fusedMi = components.fused_mi || 0;
    const rsi = this._lastRSI;

    // Signal badge
    const sigEl = document.getElementById('finalSignal');
    if (sigEl) {
      const icons = { LONG: '📈', SHORT: '📉', HOLD: '⏸️' };
      const labels = { LONG: '做多', SHORT: '做空', HOLD: '观望' };
      sigEl.className = `signal-badge ${dir.toLowerCase()}`;
      sigEl.textContent = `${icons[dir] || '❓'} ${labels[dir] || dir}`;
    }

    // Final score
    const scoreEl = document.getElementById('finalScore');
    const barEl = document.getElementById('finalScoreBar');
    if (scoreEl) scoreEl.textContent = score.toFixed(4);
    if (barEl) barEl.style.width = `${Math.min(100, Math.abs(score) * 100)}%`;

    // RSI display
    const rsiEl = document.getElementById('rsiDisplay');
    const rsiLabel = document.getElementById('rsiLabel');
    const rsiCard = document.getElementById('rsiCard');
    if (rsiEl) rsiEl.textContent = rsi;
    if (rsi > 75 && rsiCard) {
      rsiCard.classList.add('rsi-extreme');
      if (rsiEl) rsiEl.style.color = '#f43f5e';
      if (rsiLabel) rsiLabel.textContent = '⚠️ 极度超买';
    } else if (rsi < 28 && rsiCard) {
      rsiCard.classList.add('rsi-extreme');
      if (rsiEl) rsiEl.style.color = '#22c55e';
      if (rsiLabel) rsiLabel.textContent = '⚠️ 极度超卖';
    } else {
      if (rsiCard) rsiCard.classList.remove('rsi-extreme');
      if (rsiEl) rsiEl.style.color = 'var(--text)';
      if (rsiLabel) rsiLabel.textContent = '正常区间';
    }

    // Mi display
    const miEl = document.getElementById('fusedMi');
    if (miEl) miEl.textContent = fusedMi.toFixed(4);

    // Reasoning
    const reasonEl = document.getElementById('reasoningText');
    if (reasonEl) reasonEl.textContent = reasoning;

    // MiroFish dimensions
    if (mirofish) {
      const { mi: pMi, dims } = mirofish;
      if (pMi) {
        const pmiEl = document.getElementById('platformMi');
        if (pmiEl) pmiEl.textContent = pMi.toFixed(4);
      }
      if (dims && dims.dimension_accuracy) {
        const grid = document.getElementById('dimensionGrid');
        if (grid) {
          const entries = Object.entries(dims.dimension_accuracy).slice(0, 20);
          grid.innerHTML = entries.map(([name, val]) => `
            <div class="dimension-item">
              <div class="dim-name">${name.replace(/_/g,' ')}</div>
              <div class="dim-val">${(val * 100).toFixed(1)}%</div>
            </div>
          `).join('');
        }
        const accEl = document.getElementById('agentAccuracy');
        if (accEl && dims.avg_accuracy) accEl.textContent = `${(dims.avg_accuracy * 100).toFixed(1)}%`;
      }
    }

    // Market data
    if (market) {
      this._lastRSI = Math.round(50 + (50 - (market.fear_greed_index || 50)) * 0.5);
      this._lastRegime = (market.fear_greed_index || 50) > 62 ? 'bull' : (market.fear_greed_index || 50) < 40 ? 'bear' : 'neutral';
    }

    // Backend status
    const statusEl = document.getElementById('backendStatus');
    if (statusEl) { statusEl.textContent = '● 已连接'; statusEl.style.color = 'var(--primary)'; }
  }
};
