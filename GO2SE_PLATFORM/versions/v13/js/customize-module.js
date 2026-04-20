// ========== 可迭代定制化平台模块 ==========
const CustomizeModule = {
    state: {
        level: 1,
        activeTab: 'competitor',
        competitors: [],
        customModes: []
    },

    // 竞品配置
    competitorConfig: [
        { id: '3commas', name: '3Commas DCA Bot', type: 'DCA', winrate: 62, status: 'ready', features: ['DCA', 'Smart Order', 'Trailing'] },
        { id: 'haasonline', name: 'HaasOnline SuperGuppy', type: 'SuperGuppy', winrate: 58, status: 'ready', features: ['SuperGuppy', '剧本', '多交易所'] },
        { id: 'freqtrade', name: 'FreqTrade Grid', type: 'Grid', winrate: 65, status: 'ready', features: ['Grid', 'DCA', '信号'] },
        { id: 'cornix', name: 'Cornix', type: '信号跟单', winrate: 55, status: 'ready', features: ['信号', '自动跟单', '剧本'] },
        { id: 'bitsgap', name: 'Bitsgap', type: '多交易所', winrate: 60, status: 'ready', features: ['多交易所', 'Grid', 'DCA'] }
    ],

    // 自定义模式
    customModes: [
        { id: 'expert-v1', name: '专家模式v1', description: '激进型高频交易', winrate: 75, tools: ['rabbit', 'mole'] },
        { id: 'safe-v1', name: '安全模式v1', description: '保守型低频交易', winrate: 68, tools: ['rabbit', 'oracle'] }
    ],

    init: function() {
        this.loadState();
        
        console.log('🔧 CustomizeModule initialized');
    },

    loadState: function() {
        try {
            var saved = localStorage.getItem('CustomizeModuleState');
            if (saved) {
                var data = JSON.parse(saved);
                this.state.level = data.level || 1;
                this.state.activeTab = data.activeTab || 'competitor';
            }
        } catch(e) {}
    },

    saveState: function() {
        try {
            localStorage.setItem('CustomizeModuleState', JSON.stringify({
                level: this.state.level,
                activeTab: this.state.activeTab
            }));
        } catch(e) {}
    },

    renderPanel: function() {
        var container = document.getElementById('customizePanelContainer');
        if (!container) return;

        var html = '';
        if (this.state.level === 1) html = this.renderLevel1();
        else if (this.state.level === 2) html = this.renderLevel2();
        else if (this.state.level === 3) html = this.renderLevel3();
        else if (this.state.level === 4) html = this.renderLevel4();

        container.innerHTML = html;
        container.style.display = 'block';
    },

    // Level 1: 总览
    renderLevel1: function() {
        var html = '<div style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(10,14,23,0.98); z-index:10000; overflow:auto;">';
        html += '<div style="max-width:700px; margin:0 auto; background:rgba(20,25,35,0.98); border:1px solid rgba(124,58,237,0.2); border-radius:15px; margin-top:30px; margin-bottom:30px;">';

        html += '<div style="padding:20px; border-bottom:1px solid rgba(255,255,255,0.1); display:flex; justify-content:space-between; align-items:center;">';
        html += '<div><span style="font-size:28px;">🔧</span> <span style="font-size:18px; font-weight:700;">可迭代定制化平台</span></div>';
        html += '<button onclick="CustomizeModule.closePanel()" style="background:none; border:none; color:#888; font-size:24px; cursor:pointer;">✕</button>';
        html += '</div>';

        html += '<div style="padding:20px;">';

        // 标签切换
        html += '<div style="display:flex; gap:8px; margin-bottom:15px;">';
        var tabs = [
            { id: 'competitor', name: '竞品集成', icon: '📦' },
            { id: 'custom', name: '自定义模式', icon: '🎨' },
            { id: 'monitor', name: '竞品监控', icon: '📊' }
        ];
        var self = this;
        tabs.forEach(function(tab) {
            var isActive = self.state.activeTab === tab.id;
            html += '<button onclick="CustomizeModule.selectTab(\'' + tab.id + '\')" style="flex:1; padding:10px; background:' + (isActive ? 'rgba(124,58,237,0.2)' : 'rgba(0,0,0,0.3)') + '; border:1px solid ' + (isActive ? '#7c3aed' : 'rgba(255,255,255,0.1)') + '; color:' + (isActive ? '#a78bfa' : '#888') + '; border-radius:8px; cursor:pointer; font-size:12px;">' + tab.icon + ' ' + tab.name + '</button>';
        });
        html += '</div>';

        if (this.state.activeTab === 'competitor') {
            html += this.renderCompetitorOverview();
        } else if (this.state.activeTab === 'custom') {
            html += this.renderCustomModeOverview();
        } else {
            html += this.renderMonitorOverview();
        }

        html += '<button onclick="CustomizeModule.navigateLevel(2)" style="width:100%; padding:12px; margin-top:20px; background:rgba(124,58,237,0.2); border:1px solid #7c3aed; color:#a78bfa; border-radius:8px; cursor:pointer; font-weight:600;">查看详情 →</button>';
        html += '</div></div></div>';

        return html;
    },

    // 竞品总览
    renderCompetitorOverview: function() {
        var html = '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px;">';
        html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px;">📦 竞品集成</div>';

        var self = this;
        this.competitorConfig.forEach(function(comp) {
            html += '<div style="display:flex; justify-content:space-between; align-items:center; padding:12px; background:rgba(0,0,0,0.3); border-radius:8px; margin-bottom:8px;">';
            html += '<div><div style="font-weight:600;">' + comp.name + '</div><div style="font-size:11px; color:#888;">' + comp.type + '</div></div>';
            html += '<div style="text-align:right;"><div style="color:#00d4aa; font-weight:600;">' + comp.winrate + '%</div><div style="font-size:10px; color:#888;">胜率</div></div>';
            html += '</div>';
        });

        html += '</div>';
        return html;
    },

    // 自定义模式总览
    renderCustomModeOverview: function() {
        var html = '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px;">';
        html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px;">🎨 自定义专家模式</div>';

        var self = this;
        this.customModes.forEach(function(mode) {
            html += '<div style="padding:12px; background:rgba(0,0,0,0.3); border-radius:8px; margin-bottom:8px;">';
            html += '<div style="display:flex; justify-content:space-between; margin-bottom:5px;">';
            html += '<div style="font-weight:600;">' + mode.name + '</div>';
            html += '<div style="color:#a78bfa; font-weight:600;">' + mode.winrate + '%</div>';
            html += '</div>';
            html += '<div style="font-size:11px; color:#888;">' + mode.description + '</div>';
            html += '</div>';
        });

        html += '</div>';
        return html;
    },

    // 监控总览
    renderMonitorOverview: function() {
        var html = '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px;">';
        html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px;">📊 竞品监控</div>';

        var monitors = [
            { name: '3Commas胜率', value: '62%', trend: 'up', change: '+2%' },
            { name: 'HaasOnline胜率', value: '58%', trend: 'down', change: '-1%' },
            { name: 'FreqTrade胜率', value: '65%', trend: 'up', change: '+3%' }
        ];

        var self = this;
        monitors.forEach(function(m) {
            html += '<div style="display:flex; justify-content:space-between; align-items:center; padding:10px; background:rgba(0,0,0,0.3); border-radius:8px; margin-bottom:8px;">';
            html += '<span style="color:#888;">' + m.name + '</span>';
            html += '<div><span style="color:#00d4aa; font-weight:600; margin-right:5px;">' + m.value + '</span>';
            html += '<span style="color:' + (m.trend === 'up' ? '#00d4aa' : '#ef4444') + '; font-size:11px;">' + m.change + '</span></div>';
            html += '</div>';
        });

        html += '</div>';
        return html;
    },

    // Level 2: 详情
    renderLevel2: function() {
        var html = '<div style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(10,14,23,0.98); z-index:10000; overflow:auto;">';
        html += '<div style="max-width:700px; margin:0 auto; background:rgba(20,25,35,0.98); border:1px solid rgba(124,58,237,0.2); border-radius:15px; margin-top:30px; margin-bottom:30px;">';

        html += '<div style="padding:20px; border-bottom:1px solid rgba(255,255,255,0.1); display:flex; justify-content:space-between; align-items:center;">';
        html += '<div><span style="font-size:28px;">🔧</span> <span style="font-size:18px; font-weight:700;">详情</span></div>';
        html += '<button onclick="CustomizeModule.closePanel()" style="background:none; border:none; color:#888; font-size:24px; cursor:pointer;">✕</button>';
        html += '</div>';

        html += '<div style="padding:20px;">';
        html += '<button onclick="CustomizeModule.navigateLevel(1)" style="padding:8px 15px; background:rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.2); color:#fff; border-radius:8px; cursor:pointer; margin-bottom:15px;">← 返回</button>';

        if (this.state.activeTab === 'competitor') {
            html += '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px;">';
            html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px;">📦 竞品详情</div>';

            var self = this;
            this.competitorConfig.forEach(function(comp) {
                html += '<div style="padding:15px; background:rgba(0,0,0,0.3); border-radius:8px; margin-bottom:10px;">';
                html += '<div style="display:flex; justify-content:space-between; margin-bottom:10px;">';
                html += '<div><div style="font-weight:600;">' + comp.name + '</div><div style="font-size:11px; color:#888;">' + comp.type + '</div></div>';
                html += '<div style="text-align:right;"><div style="color:#00d4aa; font-weight:700; font-size:18px;">' + comp.winrate + '%</div><div style="font-size:10px; color:#888;">历史胜率</div></div>';
                html += '</div>';
                html += '<div style="display:flex; gap:5px; flex-wrap:wrap;">';
                comp.features.forEach(function(f) {
                    html += '<span style="font-size:10px; padding:3px 8px; background:rgba(124,58,237,0.2); color:#a78bfa; border-radius:10px;">' + f + '</span>';
                });
                html += '</div>';
                html += '<button onclick="CustomizeModule.navigateLevel(3)" style="width:100%; padding:8px; margin-top:10px; background:rgba(124,58,237,0.2); border:1px solid #7c3aed; color:#a78bfa; border-radius:6px; cursor:pointer; font-size:12px;">一键接入</button>';
                html += '</div>';
            });

            html += '</div>';
        } else if (this.state.activeTab === 'custom') {
            html += '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px;">';
            html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px;">🎨 自定义模式</div>';

            var self = this;
            this.customModes.forEach(function(mode) {
                html += '<div style="padding:15px; background:rgba(0,0,0,0.3); border-radius:8px; margin-bottom:10px;">';
                html += '<div style="display:flex; justify-content:space-between; margin-bottom:5px;">';
                html += '<div style="font-weight:600;">' + mode.name + '</div>';
                html += '<div style="color:#a78bfa; font-weight:600;">' + mode.winrate + '%</div>';
                html += '</div>';
                html += '<div style="font-size:12px; color:#888; margin-bottom:10px;">' + mode.description + '</div>';
                html += '<div style="font-size:11px; color:#888; margin-bottom:10px;">适用工具: ' + mode.tools.join(', ') + '</div>';
                html += '<button style="width:100%; padding:8px; background:rgba(124,58,237,0.2); border:1px solid #7c3aed; color:#a78bfa; border-radius:6px; cursor:pointer; font-size:12px;">编辑</button>';
                html += '</div>';
            });

            html += '<button onclick="CustomizeModule.navigateLevel(3)" style="width:100%; padding:12px; margin-top:15px; background:linear-gradient(135deg, #7c3aed, #6d28d9); border:none; color:#fff; border-radius:8px; cursor:pointer; font-weight:600;">+ 创建新模式</button>';
            html += '</div>';
        }

        html += '</div></div></div>';
        return html;
    },

    // Level 3: 配置
    renderLevel3: function() {
        var html = '<div style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(10,14,23,0.98); z-index:10000; overflow:auto;">';
        html += '<div style="max-width:500px; margin:0 auto; background:rgba(20,25,35,0.98); border:1px solid rgba(124,58,237,0.2); border-radius:15px; margin-top:30px;">';

        html += '<div style="padding:20px; border-bottom:1px solid rgba(255,255,255,0.1); display:flex; justify-content:space-between; align-items:center;">';
        html += '<div><span style="font-size:28px;">⚙️</span> <span style="font-size:18px; font-weight:700;">配置</span></div>';
        html += '<button onclick="CustomizeModule.closePanel()" style="background:none; border:none; color:#888; font-size:24px; cursor:pointer;">✕</button>';
        html += '</div>';

        html += '<div style="padding:20px;">';
        html += '<button onclick="CustomizeModule.navigateLevel(2)" style="padding:8px 15px; background:rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.2); color:#fff; border-radius:8px; cursor:pointer; margin-bottom:15px;">← 返回</button>';

        html += '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px;">';
        html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px;">🔧 接入配置</div>';

        html += '<div style="margin-bottom:15px;">';
        html += '<label style="font-size:12px; color:#888; display:block; margin-bottom:5px;">API Key</label>';
        html += '<input type="text" placeholder="Enter API Key" style="width:100%; padding:10px; background:rgba(0,0,0,0.3); border:1px solid rgba(255,255,255,0.2); border-radius:8px; color:#fff;">';
        html += '</div>';

        html += '<div style="margin-bottom:15px;">';
        html += '<label style="font-size:12px; color:#888; display:block; margin-bottom:5px;">API Secret</label>';
        html += '<input type="password" placeholder="Enter API Secret" style="width:100%; padding:10px; background:rgba(0,0,0,0.3); border:1px solid rgba(255,255,255,0.2); border-radius:8px; color:#fff;">';
        html += '</div>';

        html += '<div style="margin-bottom:15px;">';
        html += '<label style="font-size:12px; color:#888; display:block; margin-bottom:5px;">同步策略</label>';
        html += '<select style="width:100%; padding:10px; background:rgba(0,0,0,0.3); border:1px solid rgba(255,255,255,0.2); border-radius:8px; color:#fff;">';
        html += '<option>全部同步</option><option>仅高频</option><option>仅低频</option>';
        html += '</select>';
        html += '</div>';

        html += '</div>';

        html += '<div style="display:flex; gap:10px; margin-top:20px;">';
        html += '<button onclick="CustomizeModule.navigateLevel(4)" style="flex:1; padding:12px; background:linear-gradient(135deg, #7c3aed, #6d28d9); border:none; color:#fff; border-radius:8px; cursor:pointer; font-weight:600;">确认接入</button>';
        html += '</div>';
        html += '</div></div></div>';

        return html;
    },

    // Level 4: 结果
    renderLevel4: function() {
        var html = '<div style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(10,14,23,0.98); z-index:10000; overflow:auto;">';
        html += '<div style="max-width:500px; margin:0 auto; background:rgba(20,25,35,0.98); border:1px solid rgba(124,58,237,0.2); border-radius:15px; margin-top:30px;">';

        html += '<div style="padding:20px; border-bottom:1px solid rgba(255,255,255,0.1); display:flex; justify-content:space-between; align-items:center;">';
        html += '<div><span style="font-size:28px;">✅</span> <span style="font-size:18px; font-weight:700;">接入成功</span></div>';
        html += '<button onclick="CustomizeModule.closePanel()" style="background:none; border:none; color:#888; font-size:24px; cursor:pointer;">✕</button>';
        html += '</div>';

        html += '<div style="padding:20px; text-align:center;">';
        html += '<div style="font-size:64px; margin-bottom:20px;">✅</div>';
        html += '<div style="font-size:24px; font-weight:700; color:#a78bfa; margin-bottom:10px;">竞品接入成功</div>';
        html += '<div style="color:#888; margin-bottom:20px;">ID: CP' + Date.now().toString().slice(-8) + '</div>';
        html += '</div>';

        html += '<div style="padding:0 20px 20px;">';
        html += '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px; margin-bottom:15px;">';
        html += '<div style="display:flex; justify-content:space-between; margin-bottom:8px;"><span style="color:#888;">竞品</span><span>3Commas DCA Bot</span></div>';
        html += '<div style="display:flex; justify-content:space-between; margin-bottom:8px;"><span style="color:#888;">状态</span><span style="color:#00d4aa;">已连接</span></div>';
        html += '<div style="display:flex; justify-content:space-between;"><span style="color:#888;">同步策略</span><span>全部同步</span></div>';
        html += '</div>';

        html += '<button onclick="CustomizeModule.closePanel()" style="width:100%; padding:15px; background:linear-gradient(135deg, #7c3aed, #6d28d9); border:none; color:#fff; border-radius:10px; cursor:pointer; font-weight:700; font-size:16px;">完成</button>';
        html += '</div></div></div>';

        return html;
    },

    selectTab: function(tab) {
        this.state.activeTab = tab;
        this.saveState();
        
    },

    navigateLevel: function(level) {
        this.state.level = level;
        this.saveState();
        this.renderPanel();
        
    },

    closePanel: function() {
        var container = document.getElementById('customizePanelContainer');
        if (container) {
            container.style.display = 'none';
            container.innerHTML = '';
        }
        this.state.level = 1;
    }
};

// Auto-init (panel display disabled on load)
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() { CustomizeModule.init(); });
} else {
    CustomizeModule.init();
}


// Init - Disabled auto-init
// // Auto-init restored
//     document.addEventListener('DOMContentLoaded', function() { CustomizeModule.init(); });
// } else {
//     CustomizeModule.init();
// }

// Auto-init (panel display disabled on load)
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() { CustomizeModule.init(); });
} else {
    CustomizeModule.init();
}
