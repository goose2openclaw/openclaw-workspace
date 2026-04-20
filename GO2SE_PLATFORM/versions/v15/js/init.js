// v15 Init - 启动动画 + 主题 + 导航
(function() {
  let progress = 0;
  const progressFill = document.getElementById('progressFill');
  const progressText = document.getElementById('progressText');
  const skipBtn = document.getElementById('skipBtn');

  function animateSplash() {
    if (progress < 100) {
      progress += 1.5;
      if (progressFill) progressFill.style.width = progress + '%';
      if (progressText) progressText.textContent = `四脑同步中... ${Math.round(progress)}%`;
      if (progress >= 80) skipBtn.style.display = 'block';
      setTimeout(animateSplash, 60);
    } else {
      showApp();
    }
  }

  function showApp() {
    const splash = document.getElementById('splash');
    const app = document.getElementById('app');
    if (splash) { splash.style.opacity = '0'; setTimeout(() => splash.remove(), 400); }
    if (app) {
      app.classList.remove('hidden');
      app.style.opacity = '0';
      app.style.transition = 'opacity 0.5s';
      setTimeout(() => app.style.opacity = '1', 50);
    }
    V15Bridge.addListener(d => V15Bridge.updateUI(d));
    V15Bridge.startAutoRefresh(30000);
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
  window.togglePin = function(btn) { btn.classList.toggle('active'); };

  // Auto refresh toggle
  window.toggleAutoRefresh = function(btn) {
    btn.classList.toggle('active');
    if (btn.classList.contains('active')) V15Bridge.startAutoRefresh(30000);
    else V15Bridge.stopAutoRefresh();
  };

  // Global ref
  window.v15Bridge = V15Bridge;
})();
