// ==========================================================================
// GO2SE V14 - 核心架构
// 5大UI板块 + 4级页面 + 用户系统 + 状态管理
// ==========================================================================

// 全局命名空间
const GO2SE = {
    version: 'v14',
    state: {
        currentSection: 'home',     // home/tools/assets/security/settings
        currentModule: null,
        currentLevel: 1,            // 1-4 四级页面
        userMode: 'guest',          // guest/subscribe/member/partner+expert
        adminLevel: 0,               // 0/1/2/3
        statusLight: 'green',        // red/yellow/green
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        language: 'zh-CN',
        style: 'dark',
        brainMode: 'dual',          // left/right/dual
        isLoggedIn: false,
        user: null
    },
    
    // 用户权限配置
    userModes: {
        guest: { name: '游客', color: '#666', access: 1 },
        subscribe: { name: '订阅', color: '#00d4aa', access: 2 },
        member: { name: '会员', color: '#7c3aed', access: 3 },
        partner: { name: '鹅伙人', color: '#f59e0b', access: 4 },
        expert: { name: '专家模式', color: '#ef4444', access: 5, stackable: true }
    },
    
    adminLevels: {
        0: { name: '普通用户', color: '#666' },
        1: { name: '一级管理', color: '#00d4aa' },
        2: { name: '二级管理', color: '#f59e0b' },
        3: { name: '超级管理员', color: '#ef4444' }
    },
    
    // 状态灯配置
    statusLight: {
        red: { name: '需要处理', color: '#ef4444', action: 'platform_defensive' },
        yellow: { name: '需要关注', color: '#f59e0b', action: 'attention_required' },
        green: { name: '自动运行', color: '#00d4aa', action: 'auto_running' }
    },
    
    // 模块注册表
    modules: {
        // 首页模块
        home: {
            platformIntro: { name: '平台介绍', icon: '🚀', file: 'platform-intro.js' },
            attentionDIY: { name: 'DIY注意力', icon: '🎯', file: 'attention-diy.js' },
            macroMicro: { name: '宏观微观', icon: '🌐', file: 'macro-micro.js' }
        },
        // 工具模块
        tools: {
            sevenTools: { name: '北斗七鑫', icon: '⭐', file: 'seven-tools.js' },
            tradingPanel: { name: '交易面板', icon: '⚡', file: 'trading-modules.js' },
            tradingSim: { name: '交易仿真', icon: '🔮', file: 'trading-sim.js' },
            competitorCompare: { name: '竞品对比', icon: '📊', file: 'competitor.js' }
        },
        // 资产模块
        assets: {
            assetDashboard: { name: '资产看板', icon: '💰', file: 'asset-dashboard.js' },
            investIncome: { name: '投资收益', icon: '📈', file: 'invest-income.js' },
            workIncome: { name: '打工收益', icon: '💼', file: 'work-income.js' },
            walletArchitecture: { name: '钱包架构', icon: '🏦', file: 'wallet-arch.js' },
            assetDistribution: { name: '资产分布', icon: '📊', file: 'asset-distribution.js' },
            assetRisk: { name: '风险状态', icon: '⚠️', file: 'asset-risk.js' }
        },
        // 安全模块
        security: {
            brainDual: { name: '虾驭双脑', icon: '🧠', file: 'brain-dual.js' },
            walletSecurity: { name: '钱包安全', icon: '🔐', file: 'wallet-security.js' },
            securityMechanism: { name: '安全机制', icon: '🛡️', file: 'security-mechanism.js' }
        },
        // 设置模块
        settings: {
            engineerModule: { name: '工善其事', icon: '🔧', file: 'engineer-module.js' },
            customizeModule: { name: '可迭代定制', icon: '🎨', file: 'customize-module.js' },
            settingsModule: { name: '设置系统', icon: '⚙️', file: 'settings-module.js' }
        }
    },
    
    // 快捷方式注册
    shortcuts: {},
    
    init: function() {
        this.loadState();
        this.renderHeader();
        this.renderSidebar();
        this.renderContent();
        this.startStatusMonitor();
        this.startAutoSave();
        console.log('🪿 GO2SE v14 initialized');
    },
    
    loadState: function() {
        try {
            var saved = localStorage.getItem('GO2SEState');
            if (saved) {
                var data = JSON.parse(saved);
                Object.assign(this.state, data);
            }
        } catch(e) {}
    },
    
    saveState: function() {
        try {
            localStorage.setItem('GO2SEState', JSON.stringify(this.state));
        } catch(e) {}
    },
    
    // 渲染Header
    renderHeader: function() {
        var header = document.getElementById('mainHeader');
        if (!header) return;
        
        var self = this;
        var status = this.statusLight[this.state.statusLight];
        var userMode = this.userModes[this.state.userMode] || this.userModes.guest;
        var adminLevel = this.adminLevels[this.state.adminLevel] || this.adminLevels[0];
        
        header.innerHTML = `
            <div class="header-left">
                <div class="logo" onclick="GO2SE.navigateSection('home')">
                    <span class="logo-icon">🪿</span>
                    <span class="logo-text">GO2SE</span>
                    <span class="logo-version">${this.version}</span>
                </div>
                
                <div class="header-selectors">
                    <select class="header-select" onchange="GO2SE.setTimezone(this.value)" title="时区">
                        <option value="UTC" ${this.state.timezone === 'UTC' ? 'selected' : ''}>UTC</option>
                        <option value="Asia/Shanghai" ${this.state.timezone === 'Asia/Shanghai' ? 'selected' : ''}>北京</option>
                        <option value="Asia/Tokyo" ${this.state.timezone === 'Asia/Tokyo' ? 'selected' : ''}>东京</option>
                        <option value="America/New_York" ${this.state.timezone === 'America/New_York' ? 'selected' : ''}>纽约</option>
                    </select>
                    
                    <select class="header-select" onchange="GO2SE.setStyle(this.value)" title="风格">
                        <option value="dark" ${this.state.style === 'dark' ? 'selected' : ''}>🌙 深色</option>
                        <option value="light" ${this.state.style === 'light' ? 'selected' : ''}>☀️ 浅色</option>
                    </select>
                    
                    <select class="header-select" onchange="GO2SE.setLanguage(this.value)" title="语言">
                        <option value="zh-CN" ${this.state.language === 'zh-CN' ? 'selected' : ''}>中文</option>
                        <option value="en-US" ${this.state.language === 'en-US' ? 'selected' : ''}>English</option>
                    </select>
                </div>
            </div>
            
            <div class="header-center">
                <div class="brain-toggle" title="左右脑切换">
                    <button class="brain-btn ${this.state.brainMode === 'left' ? 'active' : ''}" onclick="GO2SE.setBrainMode('left')" title="左脑逻辑">🧠左</button>
                    <button class="brain-btn ${this.state.brainMode === 'dual' ? 'active' : ''}" onclick="GO2SE.setBrainMode('dual')" title="双脑并行">⚡</button>
                    <button class="brain-btn ${this.state.brainMode === 'right' ? 'active' : ''}" onclick="GO2SE.setBrainMode('right')" title="右脑创意">🎨右</button>
                </div>
            </div>
            
            <div class="header-right">
                <div class="status-light" onclick="GO2SE.showStatusMenu()" title="状态: ${status.name}">
                    <span class="status-dot" style="background: ${status.color}; box-shadow: 0 0 10px ${status.color};"></span>
                    <span class="status-name">${status.name}</span>
                </div>
                
                <div class="user-info" onclick="GO2SE.showUserMenu()">
                    <span class="user-mode" style="color: ${userMode.color};">${userMode.name}</span>
                    <span class="admin-level" style="color: ${adminLevel.color};">${adminLevel.name}</span>
                    <span class="user-time">${new Date().toLocaleTimeString()}</span>
                </div>
                
                <button class="header-btn" onclick="GO2SE.toggleLogin()" title="${this.state.isLoggedIn ? '登出' : '登录'}">
                    ${this.state.isLoggedIn ? '🚪' : '🔑'}
                </button>
            </div>
        `;
    },
    
    // 渲染侧边栏
    renderSidebar: function() {
        var sidebar = document.getElementById('mainSidebar');
        if (!sidebar) return;
        
        var sections = [
            { id: 'home', name: '首页', icon: '🏠', modules: Object.keys(this.modules.home) },
            { id: 'tools', name: '工具', icon: '⚙️', modules: Object.keys(this.modules.tools) },
            { id: 'assets', name: '资产', icon: '💰', modules: Object.keys(this.modules.assets) },
            { id: 'security', name: '安全', icon: '🛡️', modules: Object.keys(this.modules.security) },
            { id: 'settings', name: '设定', icon: '⚙️', modules: Object.keys(this.modules.settings) }
        ];
        
        var html = '<div class="sidebar-header"><span class="sidebar-title">导航</span></div>';
        
        sections.forEach(function(sec) {
            var isActive = GO2SE.state.currentSection === sec.id;
            html += '<div class="sidebar-section">';
            html += '<div class="sidebar-item ' + (isActive ? 'active' : '') + '" onclick="GO2SE.navigateSection(\'' + sec.id + '\')">';
            html += '<span class="sidebar-icon">' + sec.icon + '</span>';
            html += '<span class="sidebar-name">' + sec.name + '</span>';
            html += '<span class="sidebar-arrow">' + (isActive ? '25BC' : '25B6') + '</span>';
            html += '</div>';
            
            if (isActive) {
                html += '<div class="sidebar-subitems">';
                sec.modules.forEach(function(modId) {
                    var mod = GO2SE.modules[sec.id][modId];
                    var isModActive = GO2SE.state.currentModule === modId;
                    html += '<div class="sidebar-subitem ' + (isModActive ? 'active' : '') + '" onclick="GO2SE.navigateModule(\'' + sec.id + '\', \'' + modId + '\', event)">';
                    html += '<span>' + mod.icon + '</span>';
                    html += '<span>' + mod.name + '</span>';
                    html += '</div>';
                });
                html += '</div>';
            }
            html += '</div>';
        });
        
        sidebar.innerHTML = html;
    },
    
    // 渲染内容区
    renderContent: function() {
        var content = document.getElementById('mainContent');
        if (!content) return;
        
        var section = this.state.currentSection;
        var moduleId = this.state.currentModule;
        
        if (!moduleId) {
            // 显示模块列表
            content.innerHTML = this.renderModuleList(section);
        } else {
            // 显示具体模块
            content.innerHTML = this.renderModuleView(section, moduleId);
        }
    },
    
    // 渲染模块列表
    renderModuleList: function(section) {
        var self = this;
        var modules = this.modules[section] || {};
        var sectionNames = { home: '首页', tools: '工具', assets: '资产', security: '安全', settings: '设定' };
        
        var html = '<div class="content-header">';
        html += '<h2>' + sectionNames[section] + '</h2>';
        html += '<div class="content-actions">';
        html += '<button class="action-btn" onclick="GO2SE.scrollToTop()">⬆ 顶部</button>';
        html += '<button class="action-btn" onclick="GO2SE.scrollToBottom()">⬇ 底部</button>';
        html += '</div></div>';
        
        html += '<div class="module-grid">';
        Object.keys(modules).forEach(function(modId) {
            var mod = modules[modId];
            html += '<div class="module-card" onclick="GO2SE.navigateModule(\'' + section + '\', \'' + modId + '\')">';
            html += '<div class="module-icon">' + mod.icon + '</div>';
            html += '<div class="module-name">' + mod.name + '</div>';
            html += '<div class="module-arrow">&rarr;</div>';
            html += '</div>';
        });
        html += '</div>';
        
        return html;
    },
    
    // 渲染模块视图
    renderModuleView: function(section, moduleId) {
        var mod = this.modules[section]?.[moduleId];
        if (!mod) return '<div class="error">模块未找到</div>';
        
        // 调用对应模块的渲染
        var moduleObj = window[mod.file.replace('.js', '').replace(/-/g, '')] || 
                        window[mod.file.replace('.js', '').replace(/-/g, '_')] ||
                        window[Object.keys(window).find(function(k) { 
                            return k.toLowerCase().includes(moduleId.toLowerCase()); 
                        })];
        
        if (moduleObj && moduleObj.renderPanel) {
            return moduleObj.renderPanel();
        }
        
        // Fallback: 显示模块信息
        return '<div class="module-view">' +
               '<div class="module-header">' +
               '<button class="back-btn" onclick="GO2SE.navigateSection(\'' + section + '\')">← 返回</button>' +
               '<h3>' + mod.icon + ' ' + mod.name + '</h3>' +
               '</div>' +
               '<div class="module-body">' +
               '<p>模块: ' + mod.name + '</p>' +
               '<p>文件: ' + mod.file + '</p>' +
               '<p>状态: 加载中...</p>' +
               '</div>' +
               '</div>';
    },
    
    // 导航
    navigateSection: function(section) {
        this.state.currentSection = section;
        this.state.currentModule = null;
        this.state.currentLevel = 1;
        this.saveState();
        this.renderSidebar();
        this.renderContent();
        this.renderHeader();
    },
    
    navigateModule: function(section, moduleId, event) {
        if (event) event.stopPropagation();
        this.state.currentSection = section;
        this.state.currentModule = moduleId;
        this.state.currentLevel = 1;
        this.saveState();
        this.renderSidebar();
        this.renderContent();
    },
    
    navigateLevel: function(level) {
        this.state.currentLevel = level;
        this.saveState();
        this.renderContent();
    },
    
    // 状态设置
    setTimezone: function(tz) {
        this.state.timezone = tz;
        this.saveState();
        this.renderHeader();
    },
    
    setStyle: function(style) {
        this.state.style = style;
        document.body.className = style + '-mode';
        this.saveState();
        this.renderHeader();
    },
    
    setLanguage: function(lang) {
        this.state.language = lang;
        this.saveState();
        this.renderHeader();
    },
    
    setBrainMode: function(mode) {
        this.state.brainMode = mode;
        this.saveState();
        this.renderHeader();
        // 通知brain-dual模块
        if (window.BrainDual) BrainDual.setMode(mode);
    },
    
    setStatusLight: function(status) {
        this.state.statusLight = status;
        this.saveState();
        this.renderHeader();
        
        // 根据状态执行对应操作
        if (status === 'red') {
            this.activateDefensiveMode();
        } else if (status === 'yellow') {
            this.showAttentionItems();
        }
    },
    
    // 用户系统
    toggleLogin: function() {
        if (this.state.isLoggedIn) {
            this.state.isLoggedIn = false;
            this.state.user = null;
            this.state.adminLevel = 0;
        } else {
            this.showLoginDialog();
        }
        this.saveState();
        this.renderHeader();
    },
    
    showLoginDialog: function() {
        var html = '<div class="modal-overlay" onclick="GO2SE.closeModal()">';
        html += '<div class="modal-content" onclick="event.stopPropagation()">';
        html += '<div class="modal-header"><h3>🔑 登录 GO2SE</h3><button onclick="GO2SE.closeModal()">✕</button></div>';
        html += '<div class="modal-body">';
        html += '<div class="form-group"><label>用户名</label><input type="text" id="loginUser" placeholder="请输入用户名"></div>';
        html += '<div class="form-group"><label>密码</label><input type="password" id="loginPass" placeholder="请输入密码"></div>';
        html += '<div class="form-group"><label>用户模式</label>';
        html += '<select id="loginMode"><option value="guest">游客</option><option value="subscribe">订阅</option><option value="member">会员</option><option value="partner">鹅伙人</option></select>';
        html += '</div>';
        html += '<div class="form-group"><label>管理模式</label>';
        html += '<select id="loginAdmin"><option value="0">普通用户</option><option value="1">一级管理</option><option value="2">二级管理</option><option value="3">超级管理员</option></select>';
        html += '</div>';
        html += '</div>';
        html += '<div class="modal-footer"><button onclick="GO2SE.doLogin()">登录</button></div>';
        html += '</div></div>';
        
        this.showModal(html);
    },
    
    doLogin: function() {
        var user = document.getElementById('loginUser').value;
        var mode = document.getElementById('loginMode').value;
        var admin = parseInt(document.getElementById('loginAdmin').value) || 0;
        
        if (!user) {
            alert('请输入用户名');
            return;
        }
        
        this.state.isLoggedIn = true;
        this.state.user = user;
        this.state.userMode = mode;
        this.state.adminLevel = admin;
        this.saveState();
        this.closeModal();
        this.renderHeader();
    },
    
    showUserMenu: function() {
        var html = '<div class="modal-overlay" onclick="GO2SE.closeModal()">';
        html += '<div class="modal-content" onclick="event.stopPropagation()">';
        html += '<div class="modal-header"><h3>👤 用户信息</h3><button onclick="GO2SE.closeModal()">✕</button></div>';
        html += '<div class="modal-body">';
        html += '<div class="info-row"><span>用户:</span><span>' + (this.state.user || '未登录') + '</span></div>';
        html += '<div class="info-row"><span>模式:</span><span style="color:' + this.userModes[this.state.userMode].color + ';">' + this.userModes[this.state.userMode].name + '</span></div>';
        html += '<div class="info-row"><span>权限:</span><span style="color:' + this.adminLevels[this.state.adminLevel].color + ';">' + this.adminLevels[this.state.adminLevel].name + '</span></div>';
        html += '<div class="info-row"><span>时区:</span><span>' + this.state.timezone + '</span></div>';
        html += '<div class="info-row"><span>语言:</span><span>' + this.state.language + '</span></div>';
        html += '</div>';
        html += '<div class="modal-footer"><button onclick="GO2SE.toggleLogin()">' + (this.state.isLoggedIn ? '登出' : '登录') + '</button></div>';
        html += '</div></div>';
        
        this.showModal(html);
    },
    
    showStatusMenu: function() {
        var self = this;
        var html = '<div class="modal-overlay" onclick="GO2SE.closeModal()">';
        html += '<div class="modal-content" onclick="event.stopPropagation()">';
        html += '<div class="modal-header"><h3>⚡ 平台状态</h3><button onclick="GO2SE.closeModal()">✕</button></div>';
        html += '<div class="modal-body">';
        
        Object.keys(this.statusLight).forEach(function(status) {
            var s = self.statusLight[status];
            var isActive = self.state.statusLight === status;
            html += '<div class="status-option ' + (isActive ? 'active' : '') + '" onclick="GO2SE.setStatusLight(\'' + status + '\')">';
            html += '<span class="status-dot" style="background:' + s.color + ';"></span>';
            html += '<span>' + s.name + '</span>';
            html += '</div>';
        });
        
        html += '</div></div>';
        this.showModal(html);
    },
    
    activateDefensiveMode: function() {
        // 红色状态: 平台进入资产保全和保守交易模式
        console.log('🔴 进入防御模式: 资产保全 + 保守交易');
        // 通知所有模块
        if (window.TradingPanel) TradingPanel.setMode('conservative');
        if (window.WalletDeconstruct) WalletDeconstruct.lock();
    },
    
    showAttentionItems: function() {
        // 黄色状态: 显示需要处理的事项
        console.log('🟡 需要关注的事项');
    },
    
    // Modal辅助
    showModal: function(html) {
        var modal = document.getElementById('modalContainer');
        if (modal) {
            modal.innerHTML = html;
            modal.style.display = 'block';
        }
    },
    
    closeModal: function() {
        var modal = document.getElementById('modalContainer');
        if (modal) {
            modal.innerHTML = '';
            modal.style.display = 'none';
        }
    },
    
    // 滚动
    scrollToTop: function() {
        document.getElementById('mainContent')?.scrollTo(0, 0);
    },
    
    scrollToBottom: function() {
        var c = document.getElementById('mainContent');
        if (c) c.scrollTo(0, c.scrollHeight);
    },
    
    // 状态监控
    startStatusMonitor: function() {
        setInterval(function() {
            // 检查系统状态
            GO2SE.checkSystemStatus();
        }, 10000); // 每10秒检查
    },
    
    checkSystemStatus: function() {
        // 检查各项指标,更新状态灯
        var needsAttention = false;
        var critical = false;
        
        // 检查后端
        fetch('/api/stats').then(function(r) { return r.json(); }).then(function(data) {
            if (data.error) critical = true;
        }).catch(function() {
            needsAttention = true;
        });
        
        // 检查钱包
        if (window.WalletDeconstruct && WalletDeconstruct.state.needsAttention) {
            needsAttention = true;
        }
        
        if (critical) {
            this.setStatusLight('red');
        } else if (needsAttention) {
            this.setStatusLight('yellow');
        } else {
            this.setStatusLight('green');
        }
    },
    
    // 自动保存
    startAutoSave: function() {
        setInterval(function() {
            GO2SE.saveState();
        }, 30000); // 每30秒自动保存
    }
};

// 快捷键支持
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        GO2SE.closeModal();
    }
});

// 初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() { GO2SE.init(); });
} else {
    GO2SE.init();
}
