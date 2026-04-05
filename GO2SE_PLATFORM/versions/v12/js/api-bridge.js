// GO2SE V12 API Bridge - 前后台打通 + 4级导航
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

// ========================================
// 4级导航系统 - Modal管理
// ========================================
const ModalManager = {
    activeModal: null,

    open(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) {
            console.warn(`Modal ${modalId} not found`);
            return;
        }
        
        // 关闭已打开的modal
        if (this.activeModal) {
            this.close(this.activeModal);
        }
        
        modal.classList.add('active');
        this.activeModal = modalId;
        document.body.style.overflow = 'hidden';
        
        // 触发打开事件
        modal.dispatchEvent(new CustomEvent('modal:open', { detail: { modalId } }));
    },

    close(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;
        
        modal.classList.remove('active');
        if (this.activeModal === modalId) {
            this.activeModal = null;
            document.body.style.overflow = '';
        }
        
        // 触发关闭事件
        modal.dispatchEvent(new CustomEvent('modal:close', { detail: { modalId } }));
    },

    closeAll() {
        document.querySelectorAll('.modal-overlay.active').forEach(modal => {
            modal.classList.remove('active');
        });
        this.activeModal = null;
        document.body.style.overflow = '';
    },

    isOpen(modalId) {
        const modal = document.getElementById(modalId);
        return modal && modal.classList.contains('active');
    }
};

// 初始化modal事件监听
document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    loadSignals();
    loadMarket();
    syncBrainState();
    
    // 点击overlay关闭modal
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                ModalManager.close(overlay.id);
            }
        });
    });
    
    // ESC键关闭modal
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && ModalManager.activeModal) {
            ModalManager.close(ModalManager.activeModal);
        }
    });
    
    // 定时刷新
    setInterval(loadStats, 30000);
    setInterval(loadSignals, 60000);
});

// ========================================
// 4级导航 - navigateTo函数
// ========================================
// 导航层级说明:
// 1级: 主模块 (attention/asset/beidou/engineer/security)
// 2级: 子模块 (content-section)
// 3级: 功能区 (sidebar-submenu)
// 4级: 详情弹窗 (modal)

function navigateTo(section, params) {
    // 处理字符串形式的params (兼容旧用法: navigateTo('section', 'subsection'))
    if (typeof params === 'string') {
        params = { subsection: params };
    }
    params = params || {};
    
    const { subsection, openModal = true } = params;
    
    const mainSections = ['attention', 'asset', 'beidou', 'engineer', 'ninja', 'security'];
    
    // 1级导航: 主模块切换
    if (mainSections.includes(section)) {
        // 高亮快捷键
        document.querySelectorAll('.shortcut-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.section === section);
        });
        
        // 滚动到主模块
        const target = document.getElementById(section);
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
        
        // 2级: 子模块 (content-section)
        if (subsection) {
            const subTarget = document.getElementById(`${section}-${subsection}`);
            if (subTarget) {
                setTimeout(() => subTarget.scrollIntoView({ behavior: 'smooth' }), 300);
            }
            
            // 4级: 如果指定了openModal且有对应modal，则打开
            if (openModal) {
                const modalId = `modal-${section}-${subsection}`;
                const modal = document.getElementById(modalId);
                if (modal) {
                    setTimeout(() => ModalManager.open(modalId), 500);
                }
            }
        }
        return;
    }
    
    // 直接modal导航 (用于快捷入口)
    if (section.startsWith('modal-')) {
        ModalManager.open(section);
        return;
    }
    
    // content-section直接导航
    const contentTarget = document.getElementById(section);
    if (contentTarget && contentTarget.classList.contains('content-section')) {
        contentTarget.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        // 提取section名称
        const sectionName = section;
        if (subsection && openModal) {
            const modalId = `modal-${sectionName}-${subsection}`;
            const modal = document.getElementById(modalId);
            if (modal) {
                setTimeout(() => ModalManager.open(modalId), 500);
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
    navigateTo,
    modal: ModalManager
};
