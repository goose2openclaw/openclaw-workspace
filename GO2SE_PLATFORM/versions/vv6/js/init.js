// VV6 Init - Hermes Optimized
(function() {
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
    
    initNavigation();
    initThemeSwitcher();
    initAutoHandler();
    
    if (window.VV6Bridge) {
      VV6Bridge.addListener(d => VV6Bridge.updateUI(d));
      VV6Bridge.startAutoRefresh(30000);
    }
  }

  function initNavigation() {
    console.log('🧭 初始化导航...');
    
    // Navigation click handlers
    document.querySelectorAll('.sidebar-item, .shortcut-btn').forEach(item => {
      item.addEventListener('click', (e) => {
        e.preventDefault();
        const section = item.dataset.section;
        if (!section) return;
        
        console.log('🧭 导航:', section);
        
        // Update active states
        document.querySelectorAll('.sidebar-item, .shortcut-btn').forEach(i => i.classList.remove('active'));
        document.querySelectorAll(`[data-section="${section}"]`).forEach(i => i.classList.add('active'));
        
        // Show target section
        document.querySelectorAll('.content-section').forEach(s => s.style.display = 'none');
        const target = document.getElementById(section);
        if (target) target.style.display = 'block';
      });
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
      if (e.key === 'b' || e.key === 'B') toggleBrain();
    });
  }

  function initThemeSwitcher() {
    document.querySelectorAll('.theme-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.theme-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        document.documentElement.setAttribute('data-theme', btn.dataset.theme);
      });
    });
    
    document.querySelectorAll('.lang-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
      });
    });
  }

  function initAutoHandler() {
    if (window.autoHandlerVV6) {
      console.log('🤖 AutoHandler已启动');
    }
    if (window.paramsPanelVV6) {
      console.log('⚙️ ParamsPanel已启动');
    }
    if (window.hermesSoulVV6) {
      console.log('🧠 Hermes灵魂已激活');
    }
    if (window.deepIterationVV6) {
      console.log('🔍 深度迭代已激活');
    }
  }

  // Global functions
  window.navigateTo = function(section) {
    const item = document.querySelector(`[data-section="${section}"]`);
    if (item) item.click();
  };

  window.toggleBrain = function() {
    const modeText = document.getElementById('brainModeText');
    if (!modeText) return;
    const isNormal = modeText.textContent.includes('普通');
    const newMode = isNormal ? 'expert' : 'normal';
    modeText.textContent = isNormal ? '专家模式' : '普通模式';
    if (window.VV6Bridge) VV6Bridge.setMode(newMode);
  };

  window.toggleNotifications = function() {
    const badge = document.getElementById('notifBadge');
    if (badge) badge.textContent = '0';
  };

  // Skip button
  if (skipBtn) skipBtn.addEventListener('click', () => { progress = 100; showApp(); });
  
  // Start
  setTimeout(animateSplash, 300);
})();
