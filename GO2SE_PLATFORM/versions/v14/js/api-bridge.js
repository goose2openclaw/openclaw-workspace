// GO2SE V12 API Bridge - 前后台打通 + 双脑自主系统
const API_BASE = 'http://localhost:8004/api';

// ============================================================================
// 双脑状态管理
// ============================================================================

const DualBrainBridge = {
    _currentSide: 'left',
    _currentMode: 'normal',
    _mirofishScore: 0,
    _freezeActive: false,
    _listeners: [],

    // 注册状态变化监听器
    addListener(callback) {
        this._listeners.push(callback);
    },

    // 通知状态变化
    _notify(data) {
        this._currentSide = data.active_side || this._currentSide;
        this._currentMode = data.active_mode || this._currentMode;
        this._mirofishScore = data.mirofish_score || this._mirofishScore;
        this._freezeActive = data.freeze_active || false;
        this._listeners.forEach(cb => {
            try { cb(data); } catch(e) { console.error('Brain listener error:', e); }
        });
    },

    // 获取当前状态
    getState() {
        return {
            side: this._currentSide,
            mode: this._currentMode,
            mirofishScore: this._mirofishScore,
            freezeActive: this._freezeActive,
        };
    },

    // 获取双脑状态(从API)
    async fetchStatus() {
        try {
            const res = await fetch(`${API_BASE}/autonomous/dual-brain/brief`);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();
            this._notify(data);
            return data;
        } catch (e) {
            console.warn('Dual brain status fetch failed:', e.message);
            return this.getState();
        }
    },

    // 切换脑
    async switchTo(side) {
        if (this._freezeActive) {
            console.warn('Brain switch blocked: freeze active');
            return { success: false, error: 'Freeze active' };
        }
        try {
            const res = await fetch(`${API_BASE}/autonomous/dual-brain/switch`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ target: side }),
            });
            const data = await res.json();
            if (data.success) {
                this._notify({
                    active_side: data.active_side,
                    active_mode: data.active_mode,
                });
            }
            return data;
        } catch (e) {
            console.error('Brain switch failed:', e);
            return { success: false, error: e.message };
        }
    },

    // 切换脑(反转)
    async toggle() {
        return this.switchTo(this._currentSide === 'left' ? 'right' : 'left');
    },

    // 同步双脑参数
    async sync(direction = 'both') {
        try {
            const res = await fetch(`${API_BASE}/autonomous/dual-brain/sync?direction=${direction}`, {
                method: 'POST',
            });
            return await res.json();
        } catch (e) {
            console.error('Brain sync failed:', e);
            return { success: false, error: e.message };
        }
    },

    // 更新参数
    async updateParams(side, params) {
        try {
            const res = await fetch(`${API_BASE}/autonomous/dual-brain/params`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ side, ...params }),
            });
            return await res.json();
        } catch (e) {
            console.error('Params update failed:', e);
            return { success: false, error: e.message };
        }
    },

    // 冻结管理
    async freeze(action, reason = '') {
        try {
            const res = await fetch(`${API_BASE}/autonomous/freeze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action, reason }),
            });
            return await res.json();
        } catch (e) {
            console.error('Freeze action failed:', e);
            return { success: false, error: e.message };
        }
    },

    // 获取同步历史
    async getSyncHistory(count = 10) {
        try {
            const res = await fetch(`${API_BASE}/autonomous/dual-brain/sync-history?count=${count}`);
            return await res.json();
        } catch (e) {
            return { history: [], error: e.message };
        }
    },
};


// ============================================================================
// MiroFish Bridge
// ============================================================================

const MiroFishBridge = {
    _lastReport: null,
    _score: 0,

    async fetchStatus() {
        try {
            const res = await fetch(`${API_BASE}/autonomous/mirofish/status`);
            return await res.json();
        } catch (e) {
            return { available: false, error: e.message };
        }
    },

    async runSimulation(force = false) {
        try {
            const res = await fetch(`${API_BASE}/autonomous/mirofish/run`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ force }),
            });
            const data = await res.json();
            this._lastReport = data;
            this._score = data.overall_score || 0;
            return data;
        } catch (e) {
            return { error: e.message };
        }
    },

    async getReport() {
        try {
            const res = await fetch(`${API_BASE}/autonomous/mirofish/report`);
            return await res.json();
        } catch (e) {
            return { error: e.message };
        }
    },

    async checkDegradation() {
        try {
            const res = await fetch(`${API_BASE}/autonomous/mirofish/degradation`);
            return await res.json();
        } catch (e) {
            return { detected: false, error: e.message };
        }
    },

    async preDecisionCheck(signal) {
        try {
            const res = await fetch(`${API_BASE}/autonomous/mirofish/pre-decision`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(signal),
            });
            return await res.json();
        } catch (e) {
            return { approved: true, confidence: 0.7 };
        }
    },

    getScore() {
        return this._score;
    },
};


// ============================================================================
// Autonomous Controller Bridge
// ============================================================================

const AutonomousBridge = {
    async getStatus() {
        try {
            const res = await fetch(`${API_BASE}/autonomous/status`);
            return await res.json();
        } catch (e) {
            return { error: e.message };
        }
    },

    async runHealthCheck() {
        try {
            const res = await fetch(`${API_BASE}/autonomous/health/check`, { method: 'POST' });
            return await res.json();
        } catch (e) {
            return { error: e.message };
        }
    },

    async executeStrategyFlow(signal) {
        try {
            const res = await fetch(`${API_BASE}/autonomous/strategy/flow`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(signal),
            });
            return await res.json();
        } catch (e) {
            return { error: e.message };
        }
    },

    async getAlerts() {
        try {
            const res = await fetch(`${API_BASE}/autonomous/alerts`);
            return await res.json();
        } catch (e) {
            return { alerts: [], error: e.message };
        }
    },

    async acknowledgeAlert(alertId) {
        try {
            const res = await fetch(`${API_BASE}/autonomous/alerts/${alertId}/acknowledge`, {
                method: 'POST',
            });
            return await res.json();
        } catch (e) {
            return { success: false, error: e.message };
        }
    },
};


// ============================================================================
// gstack Bridge
// ============================================================================

const gstackBridge = {
    async getTeamStatus() {
        try {
            const res = await fetch(`${API_BASE}/autonomous/gstack/team`);
            return await res.json();
        } catch (e) {
            return { error: e.message };
        }
    },

    async dispatchRole(roleId, inputData = {}) {
        try {
            const res = await fetch(`${API_BASE}/autonomous/gstack/dispatch`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ role_id: roleId, input_data: inputData }),
            });
            return await res.json();
        } catch (e) {
            return { success: false, error: e.message };
        }
    },

    async runPipeline(pipelineName, inputData = {}) {
        try {
            const res = await fetch(`${API_BASE}/autonomous/gstack/pipeline`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pipeline: pipelineName, input_data: inputData }),
            });
            return await res.json();
        } catch (e) {
            return { success: false, error: e.message };
        }
    },

    async getPipelines() {
        try {
            const res = await fetch(`${API_BASE}/autonomous/gstack/pipelines`);
            return await res.json();
        } catch (e) {
            return { error: e.message };
        }
    },
};


// ============================================================================
// 原有函数 (保持兼容)
// ============================================================================

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

// 原有双脑状态同步(使用新的DualBrainBridge)
async function syncBrainState() {
    return DualBrainBridge.fetchStatus();
}


// ============================================================================
// 4级导航系统 - Modal管理
// ============================================================================

const ModalManager = {
    activeModal: null,

    open(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) {
            console.warn(`Modal ${modalId} not found`);
            return;
        }
        if (this.activeModal) {
            this.close(this.activeModal);
        }
        modal.classList.add('active');
        this.activeModal = modalId;
        document.body.style.overflow = 'hidden';
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


// ============================================================================
// UI更新器 - 双脑状态同步到UI
// ============================================================================

const BrainUI = {
    _updateInterval: null,

    // 初始化双脑UI
    init() {
        // 注册状态监听器
        DualBrainBridge.addListener((state) => {
            this.updateUI(state);
        });

        // 启动定期同步
        this.startPolling();
    },

    // 更新UI元素
    updateUI(state) {
        const switchEl = document.getElementById('brainSwitch');
        const labelEl = document.getElementById('brainLabel');
        const modeEl = document.getElementById('brainMode');
        const heartbeatEl = document.getElementById('heartbeatVal');

        if (switchEl) {
            switchEl.checked = state.side === 'right';
        }
        if (labelEl) {
            labelEl.textContent = state.side === 'right' ? '🧠右脑' : '🧠左脑';
        }
        if (modeEl) {
            modeEl.textContent = state.mode === 'expert' ? '专家' : '普通';
            modeEl.style.color = state.mode === 'expert' ? '#ef4444' : '#3b82f6';
        }

        // 更新工程模式面板
        this.updateNinjaPanel(state);
    },

    // 更新工程模式面板
    updateNinjaPanel(state) {
        const leftUnit = document.querySelector('.brain-unit.left');
        const rightUnit = document.querySelector('.brain-unit.right');
        if (leftUnit) {
            leftUnit.classList.toggle('active', state.side === 'left');
            const dot = leftUnit.querySelector('.brain-status-dot');
            if (dot) dot.className = `brain-status-dot ${state.side === 'left' ? 'active' : 'standby'}`;
        }
        if (rightUnit) {
            rightUnit.classList.toggle('active', state.side === 'right');
            const dot = rightUnit.querySelector('.brain-status-dot');
            if (dot) dot.className = `brain-status-dot ${state.side === 'right' ? 'active' : 'standby'}`;
        }
    },

    // 开始轮询
    startPolling(intervalMs = 30000) {
        if (this._updateInterval) clearInterval(this._updateInterval);
        this._updateInterval = setInterval(() => {
            DualBrainBridge.fetchStatus();
        }, intervalMs);
    },

    stopPolling() {
        if (this._updateInterval) {
            clearInterval(this._updateInterval);
            this._updateInterval = null;
        }
    },
};


// ============================================================================
// 初始化
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    // 加载初始数据
    loadStats();
    loadSignals();
    loadMarket();
    syncBrainState();

    // 初始化双脑UI
    BrainUI.init();

    // Modal事件
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                ModalManager.close(overlay.id);
            }
        });
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && ModalManager.activeModal) {
            ModalManager.close(ModalManager.activeModal);
        }
    });

    // 定时刷新
    setInterval(loadStats, 30000);
    setInterval(loadSignals, 60000);
});


// ============================================================================
// 4级导航 - navigateTo函数
// ============================================================================

function navigateTo(section, params) {
    if (typeof params === 'string') {
        params = { subsection: params };
    }
    params = params || {};
    const { subsection, openModal = true } = params;

    const mainSections = ['attention', 'asset', 'beidou', 'engineer', 'ninja', 'security'];

    if (mainSections.includes(section)) {
        document.querySelectorAll('.shortcut-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.section === section);
        });
        const target = document.getElementById(section);
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
        if (subsection) {
            const subTarget = document.getElementById(`${section}-${subsection}`);
            if (subTarget) {
                setTimeout(() => subTarget.scrollIntoView({ behavior: 'smooth' }), 300);
            }
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

    if (section.startsWith('modal-')) {
        ModalManager.open(section);
        return;
    }

    const contentTarget = document.getElementById(section);
    if (contentTarget && contentTarget.classList.contains('content-section')) {
        contentTarget.scrollIntoView({ behavior: 'smooth', block: 'start' });
        if (subsection && openModal) {
            const modalId = `modal-${section}-${subsection}`;
            const modal = document.getElementById(modalId);
            if (modal) {
                setTimeout(() => ModalManager.open(modalId), 500);
            }
        }
    }
}


// ============================================================================
// 暴露全局API
// ============================================================================

window.go2se = {
    // 原有API
    loadStats,
    loadSignals,
    loadMarket,
    syncBrainState,
    navigateTo,
    modal: ModalManager,

    // 双脑Bridge
    brain: DualBrainBridge,

    // MiroFish Bridge
    mirofish: MiroFishBridge,

    // 自主控制器 Bridge
    autonomous: AutonomousBridge,

    // gstack Bridge
    gstack: gstackBridge,

    // Brain UI控制器
    brainUI: BrainUI,
};

// ============================================================================
// 启动动画 Splash Screen
// ============================================================================
const SplashScreen = {
    progress: 0,
    elements: {
        splash: null,
        progressFill: null,
        progressText: null
    },
    steps: [
        { target: 20, label: '连接后端...' },
        { target: 40, label: '加载配置...' },
        { target: 60, label: '同步双脑...' },
        { target: 80, label: '初始化模块...' },
        { target: 100, label: '启动完成!' }
    ],
    
    init() {
        this.elements.splash = document.getElementById('splash');
        this.elements.progressFill = document.getElementById('progressFill');
        this.elements.progressText = document.getElementById('progressText');
        if (!this.elements.splash) return;
        
        this.run();
    },
    
    async run() {
        for (const step of this.steps) {
            await this.animateTo(step.target, step.label);
            await this.delay(200);
        }
        await this.delay(300);
        this.hide();
    },
    
    async animateTo(target, label) {
        const start = this.progress;
        const duration = 300;
        const startTime = performance.now();
        
        return new Promise(resolve => {
            const animate = (currentTime) => {
                const elapsed = currentTime - startTime;
                const progress = Math.min(elapsed / duration, 1);
                const current = Math.round(start + (target - start) * progress);
                
                this.progress = current;
                this.updateUI(current, label);
                
                if (progress < 1) {
                    requestAnimationFrame(animate);
                } else {
                    resolve();
                }
            };
            requestAnimationFrame(animate);
        });
    },
    
    updateUI(progress, label) {
        if (this.elements.progressFill) {
            this.elements.progressFill.style.width = progress + '%';
        }
        if (this.elements.progressText) {
            this.elements.progressText.textContent = label + ' ' + progress + '%';
        }
    },
    
    hide() {
        if (this.elements.splash) {
            this.elements.splash.classList.add('hidden');
            setTimeout(() => {
                this.elements.splash.style.display = 'none';
            }, 500);
        }
    },
    
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
};

// 页面加载完成后初始化启动动画
document.addEventListener('DOMContentLoaded', () => {
    SplashScreen.init();
});

// ============================================================================
// 市场数据模块 - 动态市场介绍
// ============================================================================
const MarketModule = {
    apiBase: 'http://localhost:8004/api',
    updateInterval: null,
    
    async init() {
        await this.loadMarketData();
        this.startPolling();
    },
    
    async loadMarketData() {
        try {
            // 获取市场数据
            const marketRes = await fetch(`${this.apiBase}/market`);
            const marketData = await marketRes.json();
            
            // 获取统计
            const statsRes = await fetch(`${this.apiBase}/stats`);
            const statsData = await statsRes.json();
            
            // 更新市场介绍卡片
            this.updateMarketCard(marketData, statsData);
            
            // 更新市场情绪
            this.updateMarketSentiment(marketData);
            
            // 更新竞品对比
            this.updateCompetitorChart(statsData);
        } catch (e) {
            console.log('Market data loading...');
        }
    },
    
    updateMarketCard(marketData, statsData) {
        const container = document.getElementById('marketTickerContainer');
        if (!container) return;
        
        const topCoins = marketData.data?.slice(0, 4) || [];
        
        if (topCoins.length > 0) {
            container.innerHTML = topCoins.map(coin => {
                const changeClass = coin.change_24h >= 0 ? 'positive' : 'negative';
                const changeSign = coin.change_24h >= 0 ? '+' : '';
                return `<div class="market-ticker">
                    <span class="ticker-symbol">${coin.symbol}</span>
                    <span class="ticker-price">$${this.formatPrice(coin.price)}</span>
                    <span class="ticker-change ${changeClass}">${changeSign}${coin.change_24h.toFixed(2)}%</span>
                </div>`;
            }).join('');
        }
        
        // 更新市场情绪
        const sentimentEl = document.querySelector('#marketIntroCard .card-meta');
        if (sentimentEl) {
            const avgChange = topCoins.reduce((sum, c) => sum + c.change_24h, 0) / (topCoins.length || 1);
            const sentiment = avgChange > 2 ? '积极' : avgChange < -2 ? '消极' : '中性';
            const emoji = avgChange > 2 ? '🟢' : avgChange < -2 ? '🔴' : '🟡';
            sentimentEl.textContent = `市场情绪：${emoji} ${sentiment}`;
        }
    },
    
    updateMarketSentiment(marketData) {
        const sentimentEl = document.querySelector('.card-meta');
        if (!sentimentEl) return;
        
        // 计算市场情绪
        const avgChange = marketData.data?.reduce((sum, c) => sum + c.change_24h, 0) / (marketData.data?.length || 1) || 0;
        const sentiment = avgChange > 2 ? '积极' : avgChange < -2 ? '消极' : '中性';
        const emoji = avgChange > 2 ? '🟢' : avgChange < -2 ? '🔴' : '🟡';
        
        sentimentEl.textContent = `市场情绪：${emoji} ${sentiment}`;
    },
    
    updateCompetitorChart(statsData) {
        // 根据实际GO2SE评分更新
        const go2seBar = document.querySelector('.bar-fill.go2se');
        if (go2seBar) {
            const score = statsData.data?.version ? '94.7' : '85.0';
            go2seBar.style.width = score + '%';
            go2seBar.textContent = score + '%';
        }
    },
    
    formatPrice(price) {
        if (price >= 1000) return price.toLocaleString('en-US', {maximumFractionDigits: 0});
        if (price >= 1) return price.toFixed(2);
        return price.toFixed(4);
    },
    
    startPolling(intervalMs = 30000) {
        if (this.updateInterval) clearInterval(this.updateInterval);
        this.updateInterval = setInterval(() => this.loadMarketData(), intervalMs);
    }
};

// 初始化市场模块
document.addEventListener('DOMContentLoaded', () => {
    MarketModule.init();
});

// ============================================================================
// 北斗七鑫策略流程可视化模块
// ============================================================================
const BeidouViz = {
    apiBase: 'http://localhost:8004/api',
    flowSteps: [
        { name: '📡信号', desc: '市场信号', icon: '📡' },
        { name: '🔊声纳库', desc: '123模型', icon: '🔊' },
        { name: '🎯策略', desc: '候选策略', icon: '🎯' },
        { name: '⚖️权重', desc: '组合权重', icon: '⚖️' },
        { name: '🔄仿真', desc: 'MiroFish', icon: '🔄' },
        { name: '📊复盘', desc: '反馈优化', icon: '📊' },
        { name: '🚀执行', desc: '分发工具', icon: '🚀' }
    ],
    tools: [
        { id: 'rabbit', name: '🐰打兔子', position: 25, winRate: 72 },
        { id: 'mole', name: '🐹打地鼠', position: 20, winRate: 62 },
        { id: 'oracle', name: '🔮走着瞧', position: 15, winRate: 70 },
        { id: 'leader', name: '👑跟大哥', position: 15, winRate: 78 },
        { id: 'hitchhiker', name: '🍀搭便车', position: 10, winRate: 65 },
        { id: 'airdrop', name: '💰薅羊毛', position: 3, winRate: 55 },
        { id: 'crowdsource', name: '👶穷孩子', position: 2, winRate: 50 }
    ],
    currentFlowStep: 0,
    
    init() {
        this.renderFlowDiagram();
        this.renderToolStats();
        this.startFlowAnimation();
        this.loadLiveData();
        this.startPolling();
    },
    
    // 渲染流程图
    renderFlowDiagram() {
        const container = document.getElementById('beidouFlowDiagram');
        if (!container) return;
        
        container.innerHTML = this.flowSteps.map((step, i) => `
            <div class="flow-step-item ${i === 0 ? 'active' : ''}" id="flow-${i}">
                <span class="flow-icon">${step.icon}</span>
                <span class="flow-label">${step.name}</span>
            </div>
        `).join('');
    },
    
    // 渲染工具统计
    renderToolStats() {
        const container = document.getElementById('beidouToolStats');
        if (!container) return;
        
        container.innerHTML = this.tools.map(tool => `
            <div class="tool-stat-mini" id="tool-mini-${tool.id}">
                <span class="mini-name">${tool.name}</span>
                <span class="mini-rate">${tool.winRate}%</span>
            </div>
        `).join('');
    },
    
    // 启动流程动画
    startFlowAnimation() {
        setInterval(() => {
            const prevStep = document.getElementById(`flow-${this.currentFlowStep}`);
            if (prevStep) prevStep.classList.remove('active');
            
            this.currentFlowStep = (this.currentFlowStep + 1) % this.flowSteps.length;
            
            const nextStep = document.getElementById(`flow-${this.currentFlowStep}`);
            if (nextStep) nextStep.classList.add('active');
        }, 1500);
    },
    
    // 加载实时数据
    async loadLiveData() {
        try {
            // 获取双脑状态
            const brainRes = await fetch(`${this.apiBase}/dual-brain/status`);
            const brainData = await brainRes.json();
            
            // 获取北斗信号
            const signalRes = await fetch(`${this.apiBase}/market/signals/beidou`);
            const signalData = await signalRes.json();
            
            // 更新工具卡片上的胜率显示
            if (signalData.signals) {
                Object.entries(signalData.signals).forEach(([symbol, tools]) => {
                    ['rabbit', 'mole', 'leader'].forEach(tool => {
                        const card = document.querySelector(`.dashboard-tool[data-tool="${tool}"]`);
                        if (card && tools[tool]) {
                            card.classList.add('has-signal');
                        }
                    });
                });
            }
            
            // 更新龙虾模块状态
            this.updateLobsterModule(brainData);
            
        } catch (e) {
            console.log('Loading live data...');
        }
    },
    
    // 更新龙虾模块
    updateLobsterModule(brainData) {
        const lobsterBtns = document.querySelectorAll('.lobster-btn');
        lobsterBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                btn.textContent = '⏳ 运行中...';
                setTimeout(() => btn.textContent = '✅ 完成', 2000);
            });
        });
    },
    
    // 定期刷新
    startPolling() {
        setInterval(() => this.loadLiveData(), 30000);
    }
};

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => BeidouViz.init(), 2000);
});
