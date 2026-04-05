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
