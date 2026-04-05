// GO2SE V10 API Bridge - 前后台打通
const API_BASE = 'http://localhost:8004/api';

// 加载统计数据
async function loadStats() {
    try {
        const res = await fetch(`${API_BASE}/stats`);
        const data = await res.json();
        if (data.data) {
            document.querySelectorAll('.stat-value').forEach(el => {
                const key = el.dataset.stat;
                if (data.data[key] !== undefined) {
                    el.textContent = data.data[key];
                }
            });
        }
    } catch (e) { console.log('Stats API not available'); }
}

// 加载信号列表
async function loadSignals() {
    try {
        const res = await fetch(`${API_BASE}/signals`);
        const data = await res.json();
        if (data.data) {
            const signalList = document.getElementById('signal-list');
            if (signalList) {
                signalList.innerHTML = data.data.slice(0, 10).map(s => `
                    <div class="signal-item">
                        <span>${s.symbol}</span>
                        <span class="signal-${s.signal}">${s.signal}</span>
                        <span>${s.confidence}%</span>
                    </div>
                `).join('');
            }
        }
    } catch (e) { console.log('Signals API not available'); }
}

// 加载市场数据
async function loadMarket() {
    try {
        const res = await fetch(`${API_BASE}/market`);
        const data = await res.json();
        if (data.data) {
            document.querySelectorAll('[data-market]').forEach(el => {
                const key = el.dataset.market;
                if (data.data[key] !== undefined) {
                    el.textContent = data.data[key];
                }
            });
        }
    } catch (e) { console.log('Market API not available'); }
}

// 双脑状态同步
async function syncBrainState() {
    try {
        const res = await fetch(`${API_BASE}/dual-brain/status`);
        const data = await res.json();
        if (data.active_brain) {
            const switchEl = document.getElementById('brainSwitch');
            if (switchEl) {
                switchEl.checked = data.active_brain === 'right';
                switchEl.dispatchEvent(new Event('change'));
            }
        }
    } catch (e) { 
        // Dual brain API not implemented, use local state
    }
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    loadSignals();
    loadMarket();
    syncBrainState();
    
    // 定时刷新
    setInterval(loadStats, 30000);
    setInterval(loadSignals, 60000);
});

// 页面导航 - 4级结构
function navigateTo(section, subsection) {
    // 1级: 主模块
    // 2级: 子模块
    // 3级: 功能区
    // 4级: 详情页
    
    const mainSections = ['attention', 'asset', 'beidou', 'engineer', 'ninja'];
    
    if (mainSections.includes(section)) {
        // 高亮快捷键
        document.querySelectorAll('.shortcut-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.section === section);
        });
        
        // 滚动到目标
        const target = document.getElementById(section);
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
        
        // 子模块处理
        if (subsection) {
            const subTarget = document.getElementById(`${section}-${subsection}`);
            if (subTarget) {
                setTimeout(() => subTarget.scrollIntoView({ behavior: 'smooth' }), 300);
            }
        }
    }
}

// 暴露全局
window.go2se = {
    loadStats,
    loadSignals, 
    loadMarket,
    syncBrainState,
    navigateTo
};

// 4级弹窗函数
function openModal(title, contentId) {
  const overlay = document.getElementById('modal-overlay');
  const titleEl = document.getElementById('modal-title');
  const bodyEl = document.getElementById('modal-body');
  const content = document.getElementById(contentId);
  if (overlay && titleEl && bodyEl && content) {
    titleEl.textContent = title;
    bodyEl.innerHTML = content.innerHTML;
    overlay.classList.add('active');
  }
}
function closeModal() {
  const overlay = document.getElementById('modal-overlay');
  if (overlay) overlay.classList.remove('active');
}

// 为详情链接绑定弹窗
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-detail]').forEach(el => {
    el.style.cursor = 'pointer';
    el.addEventListener('click', () => {
      const detailId = el.dataset.detail;
      const title = el.dataset.title || '详情';
      openModal(title, detailId);
    });
  });
});

// ─── 双脑系统 ─────────────────────────────────────────────────────
let currentBrain = 'left';
let brainConfigs = null;

async function loadBrainConfigs() {
  try {
    const res = await fetch('/api/brain');
    const data = await res.json();
    brainConfigs = data.data;
    return data.data;
  } catch (e) {
    console.warn('Brain config load failed:', e);
    return null;
  }
}

async function switchBrain(brain) {
  try {
    const res = await fetch('/api/brain/switch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ brain })
    });
    const data = await res.json();
    if (data.status === 'ok') {
      currentBrain = brain;
      updateBrainUI(brain, brainConfigs?.[brain]);
      // 同步到localStorage
      localStorage.setItem('go2se_brain', brain);
    }
    return data;
  } catch (e) {
    console.error('Brain switch failed:', e);
    return null;
  }
}

function updateBrainUI(brain, config) {
  const label = document.getElementById('brainLabel');
  const mode = document.getElementById('brainMode');
  if (label) label.textContent = brain === 'left' ? '🧠左脑' : '🧠右脑';
  if (mode && config) {
    mode.textContent = config.mode === 'normal' ? '普通' : '专家';
  }
}

function initBrain() {
  // 恢复保存的脑配置
  const saved = localStorage.getItem('go2se_brain');
  if (saved) {
    currentBrain = saved;
    updateBrainUI(saved, null);
  }
  // 加载配置
  loadBrainConfigs();
}

// 双脑初始化
document.addEventListener('DOMContentLoaded', initBrain);

// 暴露全局
window.go2se = {
  ...window.go2se,
  loadBrainConfigs,
  switchBrain,
  getCurrentBrain: () => currentBrain
};
