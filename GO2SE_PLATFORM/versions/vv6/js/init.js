// vv6 Init - 启动动画 + 主题 + 导航
(function() {
  // Splash progress
  let progress = 0;
  const progressFill = document.getElementById('progressFill');
  const progressText = document.getElementById('progressText');
  const skipBtn = document.getElementById('skipBtn');

  function animateSplash() {
    if (progress < 100) {
      progress += 2;
      if (progressFill) progressFill.style.width = progress + '%';
      if (progressText) progressText.textContent = `稳健输出... ${progress}%`;
      if (progress >= 80) skipBtn.style.display = 'block';
      setTimeout(animateSplash, 80);
    } else {
      showApp();
    }
  }

  function showApp() {
    const splash = document.getElementById('splash');
    const app = document.getElementById('app');
    if (splash) { splash.style.opacity = '0'; setTimeout(() => splash.remove(), 400); }
    if (app) { app.classList.remove('hidden'); app.style.opacity = '0'; app.style.transition = 'opacity 0.5s'; setTimeout(() => app.style.opacity = '1', 50); }
    VV6Bridge.addListener(d => VV6Bridge.updateUI(d));
    VV6Bridge.startAutoRefresh(30000);
    if (typeof refreshMarket === 'function') refreshMarket();
  }

  if (skipBtn) skipBtn.addEventListener('click', () => { progress = 100; showApp(); });
  setTimeout(animateSplash, 300);

  // Theme switcher
  document.querySelectorAll('.theme-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.theme-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      document.documentElement.setAttribute('data-theme', btn.dataset.theme);
    });
  });

  // Sidebar navigation
  document.querySelectorAll('.sidebar-item, .shortcut-btn').forEach(item => {
    item.addEventListener('click', (e) => {
      const section = item.dataset.section;
      if (!section) return;
      document.querySelectorAll('.sidebar-item, .shortcut-btn').forEach(i => i.classList.remove('active'));
      document.querySelectorAll(`[data-section="${section}"]`).forEach(i => i.classList.add('active'));
      document.querySelectorAll('.content-section').forEach(s => s.style.display = 'none');
      const target = document.getElementById(section);
      if (target) target.style.display = 'block';
    });
  });

  // Pin functionality
  window.togglePin = function(btn) {
    btn.classList.toggle('active');
  };

  // Auto refresh toggle
  window.toggleAutoRefresh = function(btn) {
    btn.classList.toggle('active');
    if (btn.classList.contains('active')) {
      VV6Bridge.startAutoRefresh(30000);
    } else {
      VV6Bridge.stopAutoRefresh();
    }
  };

  // Refresh signal
  window.refreshSignal = function() { VV6Bridge.refreshAll(); };

  // Refresh market
  window.refreshMarket = async function() {
    const mkt = await VV6Bridge.fetchMarket();
    if (!mkt) return;
    const fg = mkt.fear_greed_index || 50;
    const trend = mkt.trend || 'neutral';
    const gainer = mkt.top_gainers?.[0]?.symbol || '--';
    const gainerChange = mkt.top_gainers?.[0]?.change || 0;

    const gaugeEl = document.getElementById('fearGauge');
    const labelEl = document.getElementById('fearLabel');
    const barEl = document.getElementById('fearBar');
    const fgVal = document.getElementById('fearGreedVal');
    const fgLabel = document.getElementById('fearGreedLabel');
    const trendEl = document.getElementById('trendDisplay');
    const topGainerEl = document.getElementById('topGainer');

    if (gaugeEl) gaugeEl.textContent = fg;
    if (fgVal) fgVal.textContent = fg;
    if (barEl) barEl.style.width = fg + '%';

    const labels = { 0: '极度恐惧', 25: '恐惧', 45: '中性', 55: '贪婪', 75: '极度贪婪', 100: '极端贪婪' };
    const nearest = Object.keys(labels).map(Number).reduce((a, b) => Math.abs(b - fg) < Math.abs(a - fg) ? b : a);
    const fgText = labels[nearest] || '中性';
    if (labelEl) labelEl.textContent = fgText;
    if (fgLabel) fgLabel.textContent = fgText;

    const trendLabels = { bullish: '📈 上涨', bearish: '📉 下跌', neutral: '⚖️ 中性' };
    if (trendEl) trendEl.textContent = trendLabels[trend] || trend;
    if (topGainerEl) topGainerEl.textContent = gainer ? `${gainer} +${gainerChange.toFixed(2)}%` : '--';
  };

  // Set mode
  window.setMode = async function(mode) {
    const result = await VV6Bridge.setMode(mode);
    const normalBtn = document.getElementById('modeNormalBtn');
    const expertBtn = document.getElementById('modeExpertBtn');
    if (mode === 'normal') {
      if (normalBtn) { normalBtn.classList.add('btn-primary'); normalBtn.style.background = 'var(--primary)'; normalBtn.style.color = '#000'; }
      if (expertBtn) { expertBtn.style.background = 'transparent'; expertBtn.style.color = 'var(--text-dim)'; }
    } else {
      if (expertBtn) { expertBtn.style.background = 'var(--primary)'; expertBtn.style.color = '#000'; }
      if (normalBtn) { normalBtn.style.background = 'transparent'; normalBtn.style.color = 'var(--text-dim)'; }
    }
    if (result.message) console.log(result.message);
    VV6Bridge.refreshAll();
  };
})();
