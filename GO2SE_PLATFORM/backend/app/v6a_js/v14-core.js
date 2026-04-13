// ==========================================================================
// GO2SE V14 CORE - 全屏滚动，无折叠，点击模块标题展开详情
// ==========================================================================

(function() {
    'use strict';

    const GO2SE = window.GO2SE || {};

    // ========== 状态 ==========
    GO2SE.state = {
        currentSection: 'home',
        userMode: 'expert',  // DEV模式
        adminLevel: 3,
        statusLight: 'green',
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        language: 'zh-CN',
        style: 'dark',
        expandedModules: {}  // {moduleId: true/false}
    };

    GO2SE.version = 'v14.10-dev';

    // ========== 5大板块 ==========
    GO2SE.sections = {
        home: {
            name: '首页',
            icon: '🏠',
            modules: ['platformIntro', 'attentionDIY', 'macroMicro', 'sevenTools', 'tradingPanel', 'assetDashboard', 'brainDual', 'settingsModule']
        },
        tools: {
            name: '引擎',
            icon: '🌟',
            modules: ['sevenTools', 'tradingPanel', 'tradingSim', 'competitorCompare', 'macroMicro', 'assetDashboard', 'brainDual']
        },
        assets: {
            name: '资产',
            icon: '💰',
            modules: ['assetDashboard', 'investIncome', 'workIncome', 'walletArchitecture', 'assetDistribution', 'assetRisk']
        },
        security: {
            name: '安全',
            icon: '🛡️',
            modules: ['brainDual', 'walletSecurity', 'securityMechanism', 'tradingPanel', 'macroMicro']
        },
        settings: {
            name: '设定',
            icon: '⚙️',
            modules: ['engineerModule', 'customizeModule', 'settingsModule', 'walletArchitecture', 'assetDistribution']
        }
    };

    // ========== 所有模块定义 ==========
    GO2SE.modules = {
        platformIntro: { name: '平台介绍', icon: '🚀', component: 'PlatformIntro' },
        attentionDIY: { name: 'DIY注意力', icon: '🎯', component: 'AttentionDIY' },
        macroMicro: { name: '宏观微观', icon: '🌐', component: 'MacroMicro' },
        sevenTools: { name: '北斗七鑫', icon: '⭐', component: 'SevenTools' },
        tradingPanel: { name: '交易面板', icon: '⚡', component: 'TradingPanel' },
        tradingSim: { name: '交易仿真', icon: '🔮', component: 'TradingSim' },
        competitorCompare: { name: '竞品对比', icon: '📊', component: 'Competitor' },
        assetDashboard: { name: '资产看板', icon: '💰', component: 'AssetDashboard' },
        investIncome: { name: '投资收益', icon: '📈', component: 'InvestIncome' },
        workIncome: { name: '打工收益', icon: '💼', component: 'WorkIncome' },
        walletArchitecture: { name: '钱包架构', icon: '🏦', component: 'WalletArch' },
        assetDistribution: { name: '资产分布', icon: '📊', component: 'WalletDeconstruct' },
        assetRisk: { name: '风险状态', icon: '⚠️', component: 'AssetRisk' },
        brainDual: { name: '虾驭双脑', icon: '🧠', component: 'BrainDual' },
        walletSecurity: { name: '钱包安全', icon: '🔐', component: 'WalletSecurity' },
        securityMechanism: { name: '安全机制', icon: '🛡️', component: 'SecurityMechanism' },
        engineerModule: { name: '工善其事', icon: '🔧', component: 'EngineerModule' },
        customizeModule: { name: '可迭代定制', icon: '🎨', component: 'CustomizeModule' },
        settingsModule: { name: '设置系统', icon: '⚙️', component: 'SettingsModule' },
        apiBridge: { name: 'API桥接', icon: '🔗', component: 'ApiBridge' }
    };

    // ========== 权限 (DEV模式全部可访问) ==========
    GO2SE.canAccess = function(modId) {
        return true;  // DEV模式
    };

    GO2SE.getModuleComponent = function(modId) {
        var mod = GO2SE.modules[modId];
        if (!mod || !mod.component) return null;
        return window[mod.component];
    };

    // ========== 初始化 ==========
    GO2SE.init = function() {
        GO2SE.loadState();
        GO2SE.render();
        GO2SE.initModules();
        console.log('🪿 GO2SE ' + GO2SE.version + ' initialized - 全屏滚动模式');
    };

    GO2SE.loadState = function() {
        try {
            var saved = localStorage.getItem('GO2SEState');
            if (saved) Object.assign(GO2SE.state, JSON.parse(saved));
        } catch(e) {}
    };

    GO2SE.saveState = function() {
        try { localStorage.setItem('GO2SEState', JSON.stringify(GO2SE.state)); } catch(e) {}
    };

    GO2SE.initModules = function() {
        // 初始化所有模块
        for (var modId in GO2SE.modules) {
            var comp = GO2SE.getModuleComponent(modId);
            if (comp && comp.init) {
                try { comp.init(); } catch(e) { console.error(modId + ' init error:', e); }
            }
        }
    };

    // ========== 导航 ==========
    GO2SE.navigateSection = function(sectionId) {
        GO2SE.state.currentSection = sectionId;
        GO2SE.saveState();
        GO2SE.renderContent();
        window.scrollTo(0, 0);
    };

    GO2SE.toggleModule = function(modId) {
        GO2SE.state.expandedModules[modId] = !GO2SE.state.expandedModules[modId];
        GO2SE.saveState();
        GO2SE.renderContent();
    };

    GO2SE.scrollToTop = function() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    // ========== 渲染 ==========
    GO2SE.render = function() {
        GO2SE.renderHeader();
        GO2SE.renderContent();
        GO2SE.renderFooter();
    };

    GO2SE.renderHeader = function() {
        var header = document.getElementById('mainHeader');
        if (!header) return;

        var html = '<div class="header-left">';
        html += '<div class="logo" onclick="GO2SE.navigateSection(\'home\')">';
        html += '<span class="logo-icon">🪿</span>';
        html += '<span class="logo-text">GO2SE</span>';
        html += '<span class="logo-version">' + GO2SE.version + '</span>';
        html += '</div></div>';

        // 5板块导航
        html += '<div class="header-center">';
        html += '<nav class="header-nav">';
        for (var id in GO2SE.sections) {
            var sec = GO2SE.sections[id];
            var isActive = GO2SE.state.currentSection === id;
            html += '<a class="nav-item ' + (isActive ? 'active' : '') + '" onclick="GO2SE.navigateSection(\'' + id + '\')">';
            html += '<span>' + sec.icon + '</span>';
            html += '<span>' + sec.name + '</span>';
            html += '</a>';
        }
        html += '</nav></div>';

        // 右侧状态
        html += '<div class="header-right">';
        html += '<button class="header-btn brain-btn-compact" onclick="GO2SE.showBrainMenu()">🧠</button>';
        html += '<div class="status-light" onclick="GO2SE.showStatusMenu()">';
        html += '<span class="status-dot" style="background:#00d4aa;box-shadow:0 0 8px #00d4aa;"></span>';
        html += '</div>';
        html += '<div class="user-info" onclick="GO2SE.showUserMenu()">';
        html += '<span class="user-mode" style="color:#ef4444;">专家</span>';
        html += '</div>';
        html += '</div>';

        header.innerHTML = html;
    };

    GO2SE.renderContent = function() {
        var content = document.getElementById('mainContent');
        if (!content) return;

        var section = GO2SE.sections[GO2SE.state.currentSection];
        if (!section) return;

        var html = '';

        // 板块头部
        html += '<div class="section-hero">';
        html += '<div class="section-hero-icon">' + section.icon + '</div>';
        html += '<h1 class="section-hero-title">' + section.name + '</h1>';
        html += '<p class="section-hero-desc">一滑到底，探索全部功能</p>';
        html += '</div>';

        // 所有模块全展开（一滑到底）
        var self = this;
        section.modules.forEach(function(modId) {
            var mod = GO2SE.modules[modId];
            if (!mod) return;
            var isExpanded = GO2SE.state.expandedModules[modId] !== false; // 默认展开
            var hasAccess = GO2SE.canAccess(modId);

            html += '<div class="module-section ' + (!hasAccess ? 'locked' : '') + '">';

            // 模块标题栏（点击展开/折叠）
            html += '<div class="module-section-header" onclick="GO2SE.toggleModule(\'' + modId + '\')">';
            html += '<div class="module-section-icon">' + mod.icon + '</div>';
            html += '<div class="module-section-name">' + mod.name + '</div>';
            html += '<div class="module-section-arrow">' + (isExpanded ? '▼' : '▶') + '</div>';
            html += '</div>';

            // 模块内容（全展开模式）
            if (isExpanded && hasAccess) {
                html += '<div class="module-section-content" id="content-' + modId + '">';
                html += GO2SE.renderModuleContent(modId);
                html += '</div>';
            }

            html += '</div>';
        });

        // 到底了
        html += '<div class="section-end">';
        html += '<div class="section-end-icon">✓</div>';
        html += '<div class="section-end-text">你已经到达底部</div>';
        html += '<button class="section-end-btn" onclick="GO2SE.scrollToTop()">返回顶部 ↑</button>';
        html += '</div>';

        content.innerHTML = html;
    };

    GO2SE.renderModuleContent = function(modId) {
        var comp = GO2SE.getModuleComponent(modId);
        if (!comp) {
            return '<div class="module-placeholder">模块 ' + modId + ' 加载中...</div>';
        }

        // 检查模块是否有renderPanel方法 (v14格式)
        if (comp.renderPanel && typeof comp.renderPanel === 'function') {
            return comp.renderPanel(1);
        }

        // 检查模块是否有renderFull方法
        if (comp.renderFull && typeof comp.renderFull === 'function') {
            return comp.renderFull();
        }

        // 检查模块是否有renderToolPanel方法 (v13 SevenTools覆盖层)
        if (comp.renderToolPanel && typeof comp.renderToolPanel === 'function') {
            var mod = GO2SE.modules[modId];
            return '<div class="module-own-render">' +
                '<button class="module-open-btn" onclick="GO2SE.openModuleOverlay(\'' + modId + '\')">' +
                mod.icon + ' 打开' + mod.name + '</button>' +
                '<p class="module-hint">该模块使用独立界面</p>' +
                '</div>';
        }

        // 检查模块是否有render方法 (v13格式，需要容器)
        if (comp.render && typeof comp.render === 'function') {
            // v13模块渲染到特定容器，需要创建容器
            var mod = GO2SE.modules[modId];
            var containerId = modId + 'Module';
            // 返回一个容器，render方法会填充它
            return '<div id="' + containerId + '" class="module-v13-container"></div>' +
                   '<script>if(typeof ' + mod.component + ' !== "undefined") { ' +
                   mod.component + '.init(); }<\/script>';
        }

        // 检查是否有 HTML 容器
        var containerId = modId + 'Container';
        var container = document.getElementById(containerId);
        if (container) {
            return container.innerHTML;
        }

        // 默认：显示模块信息
        var mod = GO2SE.modules[modId];
        return '<div class="module-placeholder">' +
            '<p>' + mod.name + ' - ' + mod.icon + '</p>' +
            '<p>模块内容待完善...</p>' +
            '</div>';
    };

    // 打开模块的覆盖层
    GO2SE.openModuleOverlay = function(modId) {
        var comp = GO2SE.getModuleComponent(modId);
        if (!comp) return;

        // 对于SevenTools，调用openToolPanel初始化
        if (comp.openToolPanel && typeof comp.openToolPanel === 'function') {
            // 初始化activeTool为第一个工具
            var tools = comp.tools || {};
            var firstTool = Object.keys(tools)[0] || 'rabbit';
            comp.state.activeTool = firstTool;
            comp.state.level = 1;
        }

        // 调用模块的渲染方法
        if (comp.renderToolPanel && typeof comp.renderToolPanel === 'function') {
            comp.renderToolPanel();
        } else if (comp.render && typeof comp.render === 'function') {
            comp.render();
        }
    };

    GO2SE.renderFooter = function() {
        var footer = document.querySelector('.main-footer');
        if (footer) {
            footer.innerHTML = '<span>🪿 GO2SE ' + GO2SE.version + ' - 北斗七鑫投资体系</span>' +
                '<span id="footerTime"></span>';
        }
    };

    // ========== 菜单 ==========
    GO2SE.showBrainMenu = function() {
        var html = '<div class="modal-overlay" onclick="GO2SE.closeModal()">';
        html += '<div class="modal-content" onclick="event.stopPropagation()">';
        html += '<div class="modal-header"><h3>🧠 双脑模式</h3><button onclick="GO2SE.closeModal()">✕</button></div>';
        html += '<div class="modal-body">';
        html += '<div class="menu-item" onclick="GO2SE.setBrainMode(\'left\')">🧮 左脑优先 - 逻辑分析</div>';
        html += '<div class="menu-item" onclick="GO2SE.setBrainMode(\'dual\')">🔄 双脑协同 - 平衡模式</div>';
        html += '<div class="menu-item" onclick="GO2SE.setBrainMode(\'right\')">🎨 右脑优先 - 创意洞察</div>';
        html += '</div></div></div>';
        GO2SE.showModal(html);
    };

    GO2SE.showStatusMenu = function() {
        var html = '<div class="modal-overlay" onclick="GO2SE.closeModal()">';
        html += '<div class="modal-content" onclick="event.stopPropagation()">';
        html += '<div class="modal-header"><h3>⚡ 平台状态</h3><button onclick="GO2SE.closeModal()">✕</button></div>';
        html += '<div class="modal-body">';
        html += '<div class="menu-item active">🟢 自动运行</div>';
        html += '<div class="menu-item">🟡 需要关注</div>';
        html += '<div class="menu-item">🔴 需要处理</div>';
        html += '</div></div></div>';
        GO2SE.showModal(html);
    };

    GO2SE.showUserMenu = function() {
        var html = '<div class="modal-overlay" onclick="GO2SE.closeModal()">';
        html += '<div class="modal-content" onclick="event.stopPropagation()">';
        html += '<div class="modal-header"><h3>👤 用户中心</h3><button onclick="GO2SE.closeModal()">✕</button></div>';
        html += '<div class="modal-body">';
        html += '<div class="info-row"><span>用户</span><span>Admin</span></div>';
        html += '<div class="info-row"><span>模式</span><span style="color:#ef4444;">专家</span></div>';
        html += '<div class="info-row"><span>权限</span><span>超级管理员</span></div>';
        html += '</div></div></div>';
        GO2SE.showModal(html);
    };

    GO2SE.showModal = function(html) {
        var modal = document.getElementById('modalContainer');
        if (modal) modal.innerHTML = html;
    };

    GO2SE.closeModal = function() {
        var modal = document.getElementById('modalContainer');
        if (modal) modal.innerHTML = '';
    };

    GO2SE.setBrainMode = function(mode) {
        GO2SE.state.brainMode = mode;
        GO2SE.saveState();
        GO2SE.closeModal();
        GO2SE.renderContent();
    };

    // ========== 页面加载完成后初始化 ==========
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() { GO2SE.init(); });
    } else {
        GO2SE.init();
    }

    // ========== 更新时间 ==========
    setInterval(function() {
        var el = document.getElementById('footerTime');
        if (el) el.textContent = new Date().toLocaleString();
    }, 1000);

    window.GO2SE = GO2SE;
})();
