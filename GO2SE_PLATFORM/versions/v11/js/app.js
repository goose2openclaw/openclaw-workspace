/* GO2SE Platform v11 - Main Application */

const GO2SE = {
    version: '11.0.0',
    config: {
        apiBase: 'http://localhost:8004/api',
        refreshInterval: 30000,
        toastDuration: 4000,
        theme: 'dark'
    },
    state: {
        currentPage: 'dashboard',
        isLoading: false,
        user: null,
        connection: 'offline'
    }
};

// ========== Splash Screen Controller ==========
const SplashScreen = {
    stages: [
        { progress: 15, text: '正在连接服务器...', duration: 400 },
        { progress: 35, text: '加载配置文件...', duration: 500 },
        { progress: 55, text: '初始化交易引擎...', duration: 600 },
        { progress: 75, text: '同步市场数据...', duration: 500 },
        { progress: 90, text: '准备完成...', duration: 300 },
        { progress: 100, text: '欢迎回来!', duration: 200 }
    ],
    
    init() {
        this.createParticles();
        this.bindEvents();
        this.startAnimation();
    },
    
    createParticles() {
        const container = document.getElementById('particles');
        for (let i = 0; i < 30; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.animationDelay = Math.random() * 8 + 's';
            particle.style.animationDuration = (6 + Math.random() * 4) + 's';
            const colors = ['#00d4ff', '#7c3aed', '#10b981', '#f59e0b'];
            particle.style.background = colors[Math.floor(Math.random() * colors.length)];
            particle.style.width = (2 + Math.random() * 4) + 'px';
            particle.style.height = particle.style.width;
            container.appendChild(particle);
        }
    },
    
    bindEvents() {
        document.getElementById('btn-skip').addEventListener('click', () => this.hide());
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !document.getElementById('splash-screen').classList.contains('hidden')) {
                this.hide();
            }
        });
        
        document.querySelectorAll('.quick-options button').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const page = e.target.dataset.page;
                this.hide(() => {
                    Router.navigate(page);
                });
            });
        });
    },
    
    async startAnimation() {
        const progressBar = document.getElementById('progress-bar');
        const progressText = document.getElementById('progress-text');
        
        for (const stage of this.stages) {
            await this.animateStage(progressBar, progressText, stage);
            await this.sleep(stage.duration);
        }
        
        await this.sleep(500);
        this.hide();
    },
    
    animateStage(bar, text, stage) {
        return new Promise(resolve => {
            bar.style.width = stage.progress + '%';
            text.textContent = stage.text;
            setTimeout(resolve, 300);
        });
    },
    
    hide(callback) {
        const splash = document.getElementById('splash-screen');
        const app = document.getElementById('app');
        
        splash.classList.add('hidden');
        app.style.display = 'flex';
        
        setTimeout(() => {
            app.classList.add('fade-in');
            if (callback) callback();
        }, 500);
    },
    
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
};

// ========== Router ==========
const Router = {
    routes: {
        'dashboard': { template: 'dashboard', title: '仪表盘', parent: null },
        'signals': { template: 'signals', title: '信号列表', parent: null },
        'signals-detail': { template: 'signals-detail', title: '信号详情', parent: 'signals' },
        'portfolio': { template: 'portfolio', title: '投资组合', parent: null },
        'portfolio-history': { template: 'portfolio-history', title: '历史记录', parent: 'portfolio' },
        'assets': { template: 'assets', title: '资产看板', parent: null },
        'assets-detail': { template: 'assets-detail', title: '资产详情', parent: 'assets' },
        'wallet': { template: 'wallet', title: '钱包架构', parent: null },
        'wallet-transfer': { template: 'wallet-transfer', title: '转账', parent: 'wallet' },
        'settings': { template: 'settings', title: '系统设置', parent: null },
        'settings-api': { template: 'settings-api', title: 'API设置', parent: 'settings' },
        'help': { template: 'help', title: '帮助中心', parent: null }
    },
    
    init() {
        window.addEventListener('hashchange', () => this.handleRoute());
        this.handleRoute();
    },
    
    handleRoute() {
        const hash = window.location.hash.slice(1) || 'dashboard';
        const route = this.routes[hash] || this.routes['dashboard'];
        this.navigate(route.template, false);
    },
    
    navigate(page, updateHash = true) {
        if (updateHash) {
            window.location.hash = page;
        }
        
        const route = this.routes[page] || this.routes['dashboard'];
        GO2SE.state.currentPage = page;
        
        // Update breadcrumb
        Breadcrumb.update(route);
        
        // Update sidebar active state
        Sidebar.setActive(page);
        
        // Page transition
        PageTransition.out(() => {
            this.loadPage(route.template);
        });
    },
    
    loadPage(template) {
        const container = document.getElementById('page-content');
        container.innerHTML = '';
        
        // Show loading skeleton
        container.innerHTML = this.getSkeletonHTML();
        
        // Load page content
        setTimeout(() => {
            if (typeof Pages[template] !== 'undefined') {
                container.innerHTML = Pages[template]();
                PageTransition.in();
                
                // Initialize page-specific logic
                if (typeof Pages.init === 'function') {
                    Pages.init(template);
                }
            } else {
                container.innerHTML = `<div class="empty-state"><div class="empty-state-icon">🔧</div><div class="empty-state-title">页面建设中</div></div>`;
                PageTransition.in();
            }
        }, 300);
    },
    
    getSkeletonHTML() {
        return `
            <div class="skeleton">
                <div class="skeleton-header"></div>
                <div class="skeleton-body">
                    <div class="skeleton-line"></div>
                    <div class="skeleton-line short"></div>
                    <                    div class="skeleton-chart"></div>
                </div>
            </div>
        `;
    }
};

// ========== Sidebar Controller ==========
const Sidebar = {
    init() {
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', () => {
                const page = item.dataset.page;
                Router.navigate(page);
            });
        });
    },
    
    setActive(page) {
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
            if (item.dataset.page === page) {
                item.classList.add('active');
            }
        });
    }
};

// ========== Breadcrumb Controller ==========
const Breadcrumb = {
    update(route) {
        const container = document.getElementById('breadcrumb');
        container.innerHTML = '';
        
        // Home
        const home = document.createElement('span');
        home.className = 'breadcrumb-item';
        home.textContent = '首页';
        home.addEventListener('click', () => Router.navigate('dashboard'));
        container.appendChild(home);
        
        // Parent if exists
        if (route.parent) {
            const parent = Router.routes[route.parent];
            const parentItem = document.createElement('span');
            parentItem.className = 'breadcrumb-item';
            parentItem.textContent = parent.title;
            parentItem.addEventListener('click', () => Router.navigate(route.parent));
            container.appendChild(parentItem);
        }
        
        // Current
        const current = document.createElement('span');
        current.className = 'breadcrumb-item';
        current.textContent = route.title;
        container.appendChild(current);
    }
};

// ========== Page Transition ==========
const PageTransition = {
    out(callback) {
        const content = document.getElementById('page-content');
        content.classList.add('transitioning');
        setTimeout(callback, 250);
    },
    
    in() {
        const content = document.getElementById('page-content');
        content.classList.remove('transitioning');
        content.classList.add('page-enter');
        setTimeout(() => content.classList.remove('page-enter'), 400);
    }
};

// ========== Toast Notifications ==========
const Toast = {
    container: null,
    
    init() {
        this.container = document.getElementById('toast-container');
    },
    
    show(message, type = 'info', title = '') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        
        toast.innerHTML = `
            <span class="toast-icon">${icons[type]}</span>
            <div class="toast-content">
                ${title ? `<div class="toast-title">${title}</div>` : ''}
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close">×</button>
        `;
        
        this.container.appendChild(toast);
        
        toast.querySelector('.toast-close').addEventListener('click', () => this.remove(toast));
        
        setTimeout(() => this.remove(toast), GO2SE.config.toastDuration);
    },
    
    remove(toast) {
        toast.classList.add('removing');
        setTimeout(() => toast.remove(), 300);
    },
    
    success(message, title = '成功') { this.show(message, 'success', title); },
    error(message, title = '错误') { this.show(message, 'error', title); },
    warning(message, title = '警告') { this.show(message, 'warning', title); },
    info(message, title = '提示') { this.show(message, 'info', title); }
};

// ========== API Client ==========
const API = {
    async fetch(endpoint, options = {}) {
        const url = GO2SE.config.apiBase + endpoint;
        
        try {
            const response = await fetch(url, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },
    
    get(endpoint) {
        return this.fetch(endpoint, { method: 'GET' });
    },
    
    post(endpoint, data) {
        return this.fetch(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
};

// ========== Connection Status ==========
const Connection = {
    init() {
        this.check();
        setInterval(() => this.check(), 5000);
    },
    
    async check() {
        try {
            const response = await fetch(GO2SE.config.apiBase + '/stats');
            if (response.ok) {
                this.setStatus('online');
            } else {
                this.setStatus('offline');
            }
        } catch {
            this.setStatus('offline');
        }
    },
    
    setStatus(status) {
        const dot = document.querySelector('.status-dot');
        const text = document.querySelector('.status-text');
        
        dot.classList.remove('online', 'offline');
        dot.classList.add(status);
        text.textContent = status === 'online' ? '已连接' : '未连接';
        
        GO2SE.state.connection = status;
    }
};

// ========== DateTime Display ==========
const DateTime = {
    init() {
        this.update();
        setInterval(() => this.update(), 1000);
    },
    
    update() {
        const el = document.getElementById('datetime');
        const now = new Date();
        el.textContent = now.toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    }
};

// ========== Keyboard Shortcuts ==========
const Keyboard = {
    init() {
        document.addEventListener('keydown', (e) => this.handle(e));
    },
    
    handle(e) {
        // Don't trigger if typing in input
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
        
        // Number keys 1-7 for page navigation
        if (e.key >= '1' && e.key <= '7' && !e.ctrlKey && !e.metaKey) {
            const pages = ['dashboard', 'signals', 'portfolio', 'assets', 'wallet', 'settings', 'help'];
            const index = parseInt(e.key) - 1;
            if (pages[index]) {
                Router.navigate(pages[index]);
            }
        }
        
        // ESC to go back
        if (e.key === 'Escape') {
            const route = Router.routes[GO2SE.state.currentPage];
            if (route.parent) {
                Router.navigate(route.parent);
            }
        }
        
        // Ctrl+R to refresh
        if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
            e.preventDefault();
            location.reload();
        }
    }
};

// ========== Form Validation ==========
const Validation = {
    rules: {
        required: (value) => value.trim() !== '' || '此字段为必填项',
        email: (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) || '请输入有效的邮箱地址',
        number: (value) => !isNaN(parseFloat(value)) || '请输入有效的数字',
        positive: (value) => parseFloat(value) > 0 || '请输入正数',
        url: (value) => {
            try {
                new URL(value);
                return true;
            } catch {
                return '请输入有效的URL';
            }
        }
    },
    
    validate(form) {
        let isValid = true;
        const inputs = form.querySelectorAll('[data-validate]');
        
        inputs.forEach(input => {
            const rules = input.dataset.validate.split(',');
            const error = this.validateInput(input, rules);
            
            if (error) {
                isValid = false;
                this.showError(input, error);
            } else {
                this.clearError(input);
            }
        });
        
        return isValid;
    },
    
    validateInput(input, rules) {
        for (const rule of rules) {
            const trimmedRule = rule.trim();
            if (this.rules[trimmedRule]) {
                const error = this.rules[trimmedRule](input.value);
                if (error !== true) return error;
            }
        }
        return null;
    },
    
    showError(input, message) {
        input.classList.add('error');
        let errorEl = input.parentElement.querySelector('.form-error');
        if (!errorEl) {
            errorEl = document.createElement('div');
            errorEl.className = 'form-error';
            input.parentElement.appendChild(errorEl);
        }
        errorEl.textContent = message;
    },
    
    clearError(input) {
        input.classList.remove('error');
        const errorEl = input.parentElement.querySelector('.form-error');
        if (errorEl) errorEl.remove();
    }
};

// ========== Application Init ==========
document.addEventListener('DOMContentLoaded', () => {
    // Initialize components
    SplashScreen.init();
    Toast.init();
    Sidebar.init();
    Router.init();
    Connection.init();
    DateTime.init();
    Keyboard.init();
    
    // Bind refresh button
    document.getElementById('btn-refresh').addEventListener('click', () => {
        location.reload();
    });
    
    // Bind notifications button
    document.getElementById('btn-notifications').addEventListener('click', () => {
        Toast.info('您有 3 条新通知', '通知中心');
    });
});
