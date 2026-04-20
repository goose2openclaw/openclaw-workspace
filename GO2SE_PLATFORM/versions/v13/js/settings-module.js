// ========== 设置系统联系我模块 ==========
const SettingsModule = {
    state: {
        level: 1,
        activeTab: 'settings', // settings, lp, system
        settings: {},
        lpMembers: [],
        systemInfo: {}
    },

    // 设置配置
    settingsConfig: {
        api: {
            binance: { key: '***', status: 'connected', lastSync: '2026-04-06 12:00' },
            bybit: { key: '***', status: 'connected', lastSync: '2026-04-06 12:00' },
            okx: { key: '***', status: 'standby', lastSync: '2026-04-06 11:30' },
            polymarket: { key: '***', status: 'connected', lastSync: '2026-04-06 12:00' }
        },
        notifications: {
            email: true,
            telegram: true,
            sms: false,
            push: true
        },
        trading: {
            autoConfirm: false,
            confirmThreshold: 1000,
            maxPosition: 80,
            dailyLossLimit: 15
        },
        security: {
            twoFactor: true,
            sessionTimeout: 30,
            apiRestrictions: true
        }
    },

    // 鹅伙人配置
    lpConfig: {
        levels: [
            { id: 'basic', name: '普通LP', share: 70, min: 1000, features: ['群组管理', '业绩追踪'] },
            { id: 'advanced', name: '高级LP', share: 75, min: 10000, features: ['群组管理', '业绩追踪', '优先信号'] },
            { id: 'strategic', name: '战略LP', share: 80, min: 50000, features: ['群组管理', '业绩追踪', '优先信号', '专属策略'] }
        ],
        members: [
            { id: 1, name: 'User', level: 'strategic', investment: 85000, pnl: 4250, joined: '2026-01-15' },
            { id: 2, name: '***', level: 'advanced', investment: 15000, pnl: 750, joined: '2026-02-20' },
            { id: 3, name: '***', level: 'basic', investment: 5000, pnl: 200, joined: '2026-03-10' }
        ]
    },

    // 系统版本配置
    systemConfig: {
        currentVersion: 'v10.0.0',
        lastUpdate: '2026-04-01',
        brains: {
            left: { name: '左脑', version: 'v10.0.1', status: 'active', lastSync: '2026-04-06 12:00' },
            right: { name: '右脑', version: 'v10.0.0', status: 'standby', lastSync: '2026-04-06 11:00' }
        },
        bestState: { date: '2026-03-28', value: 9200, pnl: 1200 }
    },

    // 联系信息
    contactInfo: {
        email: 'contact@go2se.ai',
        telegram: '@GO2SEBot',
        discord: 'discord.gg/go2se',
        twitter: '@GO2SE_AI'
    },

    init: function() {
        this.loadState();
        
        console.log('⚙️ SettingsModule initialized');
    },

    loadState: function() {
        try {
            var saved = localStorage.getItem('SettingsModuleState');
            if (saved) {
                var data = JSON.parse(saved);
                this.state.level = data.level || 1;
                this.state.activeTab = data.activeTab || 'settings';
            }
        } catch(e) {}
    },

    saveState: function() {
        try {
            localStorage.setItem('SettingsModuleState', JSON.stringify({
                level: this.state.level,
                activeTab: this.state.activeTab
            }));
        } catch(e) {}
    },

    renderPanel: function() {
        var container = document.getElementById('settingsPanelContainer');
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
        var self = this;
        var html = '<div style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(10,14,23,0.98); z-index:10000; overflow:auto;">';
        html += '<div style="max-width:800px; margin:0 auto; background:rgba(20,25,35,0.98); border:1px solid rgba(0,212,170,0.2); border-radius:15px; margin-top:30px; margin-bottom:30px;">';

        // Header
        html += '<div style="padding:20px; border-bottom:1px solid rgba(255,255,255,0.1); display:flex; justify-content:space-between; align-items:center;">';
        html += '<div><span style="font-size:28px;">⚙️</span> <span style="font-size:18px; font-weight:700;">设置 · 系统 · 联系我</span></div>';
        html += '<button onclick="SettingsModule.closePanel()" style="background:none; border:none; color:#888; font-size:24px; cursor:pointer;">✕</button>';
        html += '</div>';

        html += '<div style="padding:20px;">';

        // 标签切换
        html += '<div style="display:flex; gap:8px; margin-bottom:20px;">';
        var tabs = [
            { id: 'settings', name: '设置', icon: '⚙️' },
            { id: 'lp', name: '鹅伙人', icon: '👥' },
            { id: 'system', name: '系统', icon: '📋' },
            { id: 'contact', name: '联系', icon: '📧' }
        ];
        tabs.forEach(function(tab) {
            var isActive = self.state.activeTab === tab.id;
            html += '<button onclick="SettingsModule.selectTab(\'' + tab.id + '\')" style="flex:1; padding:10px; background:' + (isActive ? 'rgba(0,212,170,0.2)' : 'rgba(0,0,0,0.3)') + '; border:1px solid ' + (isActive ? '#00d4aa' : 'rgba(255,255,255,0.1)') + '; color:' + (isActive ? '#00d4aa' : '#888') + '; border-radius:8px; cursor:pointer; font-size:12px;">' + tab.icon + ' ' + tab.name + '</button>';
        });
        html += '</div>';

        // 内容
        if (this.state.activeTab === 'settings') {
            html += this.renderSettingsOverview();
        } else if (this.state.activeTab === 'lp') {
            html += this.renderLPOverview();
        } else if (this.state.activeTab === 'system') {
            html += this.renderSystemOverview();
        } else {
            html += this.renderContactOverview();
        }

        html += '<button onclick="SettingsModule.navigateLevel(2)" style="width:100%; padding:12px; margin-top:20px; background:rgba(0,212,170,0.2); border:1px solid #00d4aa; color:#00d4aa; border-radius:8px; cursor:pointer; font-weight:600;">管理 →</button>';
        html += '</div></div></div>';

        return html;
    },

    // 设置总览
    renderSettingsOverview: function() {
        var html = '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px;">';
        html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px;">⚙️ 连接设置</div>';

        var apiStatus = Object.values(this.settingsConfig.api);
        var connected = apiStatus.filter(function(a) { return a.status === 'connected'; }).length;

        html += '<div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">';
        html += '<div style="padding:12px; background:rgba(0,212,170,0.1); border-radius:8px; text-align:center;">';
        html += '<div style="font-size:24px; font-weight:700; color:#00d4aa;">' + connected + '/' + apiStatus.length + '</div>';
        html += '<div style="font-size:11px; color:#888;">API已连接</div>';
        html += '</div>';
        html += '<div style="padding:12px; background:rgba(0,0,0,0.3); border-radius:8px; text-align:center;">';
        html += '<div style="font-size:24px; font-weight:700; color:#00d4aa;">4</div>';
        html += '<div style="font-size:11px; color:#888;">通知渠道</div>';
        html += '</div>';
        html += '</div>';

        html += '<div style="margin-top:15px;">';
        Object.keys(this.settingsConfig.api).forEach(function(key) {
            var api = self.settingsConfig.api[key];
            html += '<div style="display:flex; justify-content:space-between; padding:8px; background:rgba(0,0,0,0.3); border-radius:6px; margin-bottom:5px; font-size:12px;">';
            html += '<span>' + key.charAt(0).toUpperCase() + key.slice(1) + '</span>';
            html += '<span style="color:' + (api.status === 'connected' ? '#00d4aa' : '#f59e0b') + ';">' + (api.status === 'connected' ? '● 已连接' : '○ 待机') + '</span>';
            html += '</div>';
        });
        html += '</div>';

        html += '</div>';
        return html;
    },

    // 鹅伙人总览
    renderLPOverview: function() {
        var html = '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px;">';
        html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px;">👥 鹅伙人计划</div>';

        var totalInvestment = this.lpConfig.members.reduce(function(a, m) { return a + m.investment; }, 0);
        var totalPnL = this.lpConfig.members.reduce(function(a, m) { return a + m.pnl; }, 0);

        html += '<div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:15px;">';
        html += '<div style="padding:12px; background:rgba(0,212,170,0.1); border-radius:8px; text-align:center;">';
        html += '<div style="font-size:18px; font-weight:700; color:#00d4aa;">$' + totalInvestment.toLocaleString() + '</div>';
        html += '<div style="font-size:11px; color:#888;">总资产管理</div>';
        html += '</div>';
        html += '<div style="padding:12px; background:rgba(0,212,170,0.1); border-radius:8px; text-align:center;">';
        html += '<div style="font-size:18px; font-weight:700; color:#00d4aa;">+$' + totalPnL.toLocaleString() + '</div>';
        html += '<div style="font-size:11px; color:#888;">总收益</div>';
        html += '</div>';
        html += '</div>';

        html += '<div style="font-size:12px; color:#888; margin-bottom:10px;">LP等级</div>';
        this.lpConfig.levels.forEach(function(level) {
            html += '<div style="display:flex; justify-content:space-between; padding:10px; background:rgba(0,0,0,0.3); border-radius:6px; margin-bottom:5px;">';
            html += '<span>' + level.name + '</span>';
            html += '<span style="color:#00d4aa;">' + level.share + '%分润</span>';
            html += '</div>';
        });

        html += '</div>';
        return html;
    },

    // 系统总览
    renderSystemOverview: function() {
        var html = '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px;">';
        html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px;">📋 系统版本</div>';

        html += '<div style="text-align:center; padding:15px; background:rgba(0,212,170,0.1); border-radius:10px; margin-bottom:15px;">';
        html += '<div style="font-size:11px; color:#888; margin-bottom:5px;">当前版本</div>';
        html += '<div style="font-size:28px; font-weight:700; color:#00d4aa;">' + this.systemConfig.currentVersion + '</div>';
        html += '<div style="font-size:11px; color:#888; margin-top:5px;">更新: ' + this.systemConfig.lastUpdate + '</div>';
        html += '</div>';

        html += '<div style="font-size:12px; color:#888; margin-bottom:10px;">🧠 双脑状态</div>';
        html += '<div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">';
        Object.values(this.systemConfig.brains).forEach(function(brain) {
            html += '<div style="padding:12px; background:rgba(0,0,0,0.3); border-radius:8px; text-align:center;">';
            html += '<div style="font-size:16px; margin-bottom:5px;">' + (brain.name === '左脑' ? '🧠' : '🎯') + '</div>';
            html += '<div style="font-size:12px; font-weight:600;">' + brain.name + '</div>';
            html += '<div style="font-size:10px; color:' + (brain.status === 'active' ? '#00d4aa' : '#f59e0b') + ';">' + brain.version + ' | ' + (brain.status === 'active' ? '活跃' : '待机') + '</div>';
            html += '</div>';
        });
        html += '</div>';

        html += '<div style="margin-top:15px; padding:12px; background:rgba(0,0,0,0.3); border-radius:8px;">';
        html += '<div style="display:flex; justify-content:space-between; margin-bottom:5px;">';
        html += '<span style="color:#888; font-size:12px;">最优收益</span>';
        html += '<span style="color:#00d4aa; font-weight:600;">$' + this.systemConfig.bestState.value.toLocaleString() + '</span>';
        html += '</div>';
        html += '<div style="font-size:10px; color:#888;">' + this.systemConfig.bestState.date + ' | +$' + this.systemConfig.bestState.pnl + '</div>';
        html += '</div>';

        html += '</div>';
        return html;
    },

    // 联系总览
    renderContactOverview: function() {
        var html = '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px;">';
        html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px;">📧 联系方式</div>';

        var contacts = [
            { icon: '📧', name: '邮箱', value: this.contactInfo.email },
            { icon: '✈️', name: 'Telegram', value: this.contactInfo.telegram },
            { icon: '💬', name: 'Discord', value: this.contactInfo.discord },
            { icon: '𝕏', name: 'Twitter', value: this.contactInfo.twitter }
        ];

        contacts.forEach(function(c) {
            html += '<div style="display:flex; justify-content:space-between; align-items:center; padding:12px; background:rgba(0,0,0,0.3); border-radius:8px; margin-bottom:8px;">';
            html += '<div style="display:flex; align-items:center; gap:10px;">';
            html += '<span style="font-size:18px;">' + c.icon + '</span>';
            html += '<div><div style="font-size:11px; color:#888;">' + c.name + '</div><div style="font-size:12px;">' + c.value + '</div></div>';
            html += '</div>';
            html += '<button onclick="SettingsModule.copyContact(\'' + c.value + '\')" style="padding:5px 10px; background:rgba(0,212,170,0.2); border:1px solid #00d4aa; color:#00d4aa; border-radius:6px; cursor:pointer; font-size:11px;">复制</button>';
            html += '</div>';
        });

        html += '<div style="margin-top:15px; padding:12px; background:rgba(0,0,0,0.3); border-radius:8px;">';
        html += '<div style="font-size:12px; color:#888; margin-bottom:8px;">发送消息</div>';
        html += '<textarea placeholder="输入您的消息..." style="width:100%; padding:10px; background:rgba(0,0,0,0.3); border:1px solid rgba(255,255,255,0.1); border-radius:6px; color:#fff; font-size:12px; min-height:80px; resize:none;"></textarea>';
        html += '<button style="width:100%; padding:10px; margin-top:8px; background:rgba(0,212,170,0.2); border:1px solid #00d4aa; color:#00d4aa; border-radius:6px; cursor:pointer; font-size:12px;">发送</button>';
        html += '</div>';

        html += '</div>';
        return html;
    },

    // Level 2: 详情/管理
    renderLevel2: function() {
        var self = this;
        var html = '<div style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(10,14,23,0.98); z-index:10000; overflow:auto;">';
        html += '<div style="max-width:800px; margin:0 auto; background:rgba(20,25,35,0.98); border:1px solid rgba(0,212,170,0.2); border-radius:15px; margin-top:30px; margin-bottom:30px;">';

        html += '<div style="padding:20px; border-bottom:1px solid rgba(255,255,255,0.1); display:flex; justify-content:space-between; align-items:center;">';
        html += '<div><span style="font-size:28px;">⚙️</span> <span style="font-size:18px; font-weight:700;">管理</span></div>';
        html += '<button onclick="SettingsModule.closePanel()" style="background:none; border:none; color:#888; font-size:24px; cursor:pointer;">✕</button>';
        html += '</div>';

        html += '<div style="padding:20px;">';
        html += '<button onclick="SettingsModule.navigateLevel(1)" style="padding:8px 15px; background:rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.2); color:#fff; border-radius:8px; cursor:pointer; margin-bottom:15px;">← 返回</button>';

        if (this.state.activeTab === 'settings') {
            html += this.renderSettingsDetail();
        } else if (this.state.activeTab === 'lp') {
            html += this.renderLPDetail();
        } else if (this.state.activeTab === 'system') {
            html += this.renderSystemDetail();
        } else {
            html += this.renderContactDetail();
        }

        html += '</div></div></div>';
        return html;
    },

    // 设置详情
    renderSettingsDetail: function() {
        var html = '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px;">';
        html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px;">⚙️ API配置</div>';

        Object.keys(this.settingsConfig.api).forEach(function(key) {
            var api = self.settingsConfig.api[key];
            html += '<div style="padding:12px; background:rgba(0,0,0,0.3); border-radius:8px; margin-bottom:10px;">';
            html += '<div style="display:flex; justify-content:space-between; margin-bottom:8px;">';
            html += '<span style="font-weight:600;">' + key.charAt(0).toUpperCase() + key.slice(1) + '</span>';
            html += '<span style="color:' + (api.status === 'connected' ? '#00d4aa' : '#f59e0b') + ';">' + (api.status === 'connected' ? '● 已连接' : '○ 待机') + '</span>';
            html += '</div>';
            html += '<div style="display:flex; gap:8px;">';
            html += '<button style="flex:1; padding:8px; background:rgba(0,212,170,0.2); border:1px solid #00d4aa; color:#00d4aa; border-radius:6px; cursor:pointer; font-size:11px;">编辑</button>';
            html += '<button style="flex:1; padding:8px; background:rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.2); color:#888; border-radius:6px; cursor:pointer; font-size:11px;">测试</button>';
            html += '</div>';
            html += '</div>';
        });

        html += '<div style="margin-top:20px;">';
        html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px;">🔔 通知设置</div>';

        var notif = this.settingsConfig.notifications;
        var notifList = [
            { key: 'email', name: '邮件通知', enabled: notif.email },
            { key: 'telegram', name: 'Telegram', enabled: notif.telegram },
            { key: 'sms', name: '短信', enabled: notif.sms },
            { key: 'push', name: '推送通知', enabled: notif.push }
        ];

        notifList.forEach(function(n) {
            html += '<div style="display:flex; justify-content:space-between; align-items:center; padding:10px; background:rgba(0,0,0,0.3); border-radius:6px; margin-bottom:5px;">';
            html += '<span>' + n.name + '</span>';
            html += '<div style="width:40px; height:20px; background:' + (n.enabled ? '#00d4aa' : 'rgba(255,255,255,0.2)') + '; border-radius:10px; position:relative; cursor:pointer;">';
            html += '<div style="width:16px; height:16px; background:#fff; border-radius:50%; position:absolute; top:2px; ' + (n.enabled ? 'right:2px' : 'left:2px') + ';"></div>';
            html += '</div>';
            html += '</div>';
        });

        html += '</div></div>';
        return html;
    },

    // LP详情
    renderLPDetail: function() {
        var html = '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px;">';
        html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px;">👥 鹅伙人成员</div>';

        this.lpConfig.members.forEach(function(member) {
            var level = self.lpConfig.levels.find(function(l) { return l.id === member.level; });
            html += '<div style="padding:12px; background:rgba(0,0,0,0.3); border-radius:8px; margin-bottom:10px;">';
            html += '<div style="display:flex; justify-content:space-between; margin-bottom:8px;">';
            html += '<div><span style="font-weight:600;">' + member.name + '</span><span style="font-size:11px; color:#888; margin-left:8px;">' + level.name + '</span></div>';
            html += '<span style="color:#00d4aa; font-weight:600;">+$' + member.pnl.toLocaleString() + '</span>';
            html += '</div>';
            html += '<div style="display:flex; justify-content:space-between; font-size:11px; color:#888;">';
            html += '<span>投资: $' + member.investment.toLocaleString() + '</span>';
            html += '<span>加入: ' + member.joined + '</span>';
            html += '</div>';
            html += '</div>';
        });

        html += '<button style="width:100%; padding:12px; margin-top:15px; background:linear-gradient(135deg, #00d4aa, #00a884); border:none; color:#000; border-radius:8px; cursor:pointer; font-weight:600;">成为鹅伙人 →</button>';
        html += '</div>';
        return html;
    },

    // 系统详情
    renderSystemDetail: function() {
        var html = '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px;">';
        html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px;">🧠 双脑管理</div>';

        Object.values(this.systemConfig.brains).forEach(function(brain) {
            html += '<div style="padding:15px; background:rgba(0,0,0,0.3); border-radius:8px; margin-bottom:10px;">';
            html += '<div style="display:flex; justify-content:space-between; margin-bottom:10px;">';
            html += '<div style="display:flex; align-items:center; gap:10px;">';
            html += '<span style="font-size:24px;">' + (brain.name === '左脑' ? '🧠' : '🎯') + '</span>';
            html += '<div><div style="font-weight:600;">' + brain.name + '</div><div style="font-size:11px; color:#888;">' + brain.version + '</div></div>';
            html += '</div>';
            html += '<span style="color:' + (brain.status === 'active' ? '#00d4aa' : '#f59e0b') + '; font-size:12px;">' + (brain.status === 'active' ? '● 活跃' : '○ 待机') + '</span>';
            html += '</div>';
            html += '<div style="display:flex; gap:8px;">';
            html += '<button style="flex:1; padding:8px; background:rgba(0,212,170,0.2); border:1px solid #00d4aa; color:#00d4aa; border-radius:6px; cursor:pointer; font-size:11px;">同步</button>';
            html += '<button style="flex:1; padding:8px; background:rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.2); color:#888; border-radius:6px; cursor:pointer; font-size:11px;">切换</button>';
            html += '<button style="flex:1; padding:8px; background:rgba(239,68,68,0.2); border:1px solid #ef4444; color:#ef4444; border-radius:6px; cursor:pointer; font-size:11px;">备份</button>';
            html += '</div>';
            html += '</div>';
        });

        html += '<div style="margin-top:20px; padding:12px; background:rgba(0,0,0,0.3); border-radius:8px;">';
        html += '<div style="font-size:12px; color:#888; margin-bottom:8px;">系统状态</div>';
        html += '<div style="display:flex; justify-content:space-between; margin-bottom:5px;"><span>CPU使用率</span><span style="color:#00d4aa;">32%</span></div>';
        html += '<div style="display:flex; justify-content:space-between; margin-bottom:5px;"><span>内存使用</span><span style="color:#00d4aa;">48%</span></div>';
        html += '<div style="display:flex; justify-content:space-between;"><span>磁盘使用</span><span style="color:#f59e0b;">78%</span></div>';
        html += '</div>';

        html += '</div>';
        return html;
    },

    // 联系详情
    renderContactDetail: function() {
        var html = '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px;">';
        html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px;">📧 发送消息</div>';

        html += '<div style="margin-bottom:15px;">';
        html += '<label style="font-size:12px; color:#888; display:block; margin-bottom:5px;">主题</label>';
        html += '<input type="text" placeholder="选择主题" style="width:100%; padding:10px; background:rgba(0,0,0,0.3); border:1px solid rgba(255,255,255,0.2); border-radius:6px; color:#fff; font-size:12px;">';
        html += '</div>';

        html += '<div style="margin-bottom:15px;">';
        html += '<label style="font-size:12px; color:#888; display:block; margin-bottom:5px;">消息内容</label>';
        html += '<textarea placeholder="详细描述您的问题或建议..." style="width:100%; padding:10px; background:rgba(0,0,0,0.3); border:1px solid rgba(255,255,255,0.2); border-radius:6px; color:#fff; font-size:12px; min-height:150px; resize:none;"></textarea>';
        html += '</div>';

        html += '<div style="display:flex; gap:10px;">';
        html += '<button onclick="SettingsModule.navigateLevel(3)" style="flex:1; padding:12px; background:rgba(0,212,170,0.2); border:1px solid #00d4aa; color:#00d4aa; border-radius:6px; cursor:pointer; font-weight:600;">发送</button>';
        html += '</div>';

        html += '<div style="margin-top:20px; padding:12px; background:rgba(0,0,0,0.3); border-radius:8px;">';
        html += '<div style="font-size:12px; color:#888; margin-bottom:8px;">常见问题</div>';
        html += '<div style="font-size:12px; color:#00d4aa; cursor:pointer;">如何配置API？ →</div>';
        html += '<div style="font-size:12px; color:#00d4aa; cursor:pointer;">如何成为鹅伙人？ →</div>';
        html += '<div style="font-size:12px; color:#00d4aa; cursor:pointer;">系统更新日志 →</div>';
        html += '</div>';

        html += '</div>';
        return html;
    },

    // Level 3: 配置
    renderLevel3: function() {
        var html = '<div style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(10,14,23,0.98); z-index:10000; overflow:auto;">';
        html += '<div style="max-width:500px; margin:0 auto; background:rgba(20,25,35,0.98); border:1px solid rgba(0,212,170,0.2); border-radius:15px; margin-top:30px;">';

        html += '<div style="padding:20px; border-bottom:1px solid rgba(255,255,255,0.1); display:flex; justify-content:space-between; align-items:center;">';
        html += '<div><span style="font-size:28px;">⚙️</span> <span style="font-size:18px; font-weight:700;">配置</span></div>';
        html += '<button onclick="SettingsModule.closePanel()" style="background:none; border:none; color:#888; font-size:24px; cursor:pointer;">✕</button>';
        html += '</div>';

        html += '<div style="padding:20px;">';
        html += '<button onclick="SettingsModule.navigateLevel(2)" style="padding:8px 15px; background:rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.2); color:#fff; border-radius:8px; cursor:pointer; margin-bottom:15px;">← 返回</button>';

        html += '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px;">';
        html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px;">⚙️ 高级配置</div>';

        html += '<div style="margin-bottom:15px;">';
        html += '<label style="font-size:12px; color:#888; display:block; margin-bottom:5px;">交易确认阈值 ($)</label>';
        html += '<input type="number" value="1000" style="width:100%; padding:10px; background:rgba(0,0,0,0.3); border:1px solid rgba(255,255,255,0.2); border-radius:6px; color:#fff; font-size:12px;">';
        html += '</div>';

        html += '<div style="margin-bottom:15px;">';
        html += '<label style="font-size:12px; color:#888; display:block; margin-bottom:5px;">最大仓位 (%)</label>';
        html += '<input type="range" min="10" max="100" value="80" style="width:100%;">';
        html += '<div style="display:flex; justify-content:space-between; font-size:11px; color:#888;"><span>10%</span><span>80%</span><span>100%</span></div>';
        html += '</div>';

        html += '<div style="margin-bottom:15px;">';
        html += '<label style="font-size:12px; color:#888; display:block; margin-bottom:5px;">会话超时 (分钟)</label>';
        html += '<input type="number" value="30" style="width:100%; padding:10px; background:rgba(0,0,0,0.3); border:1px solid rgba(255,255,255,0.2); border-radius:6px; color:#fff; font-size:12px;">';
        html += '</div>';

        html += '</div>';

        html += '<button onclick="SettingsModule.navigateLevel(4)" style="width:100%; padding:15px; margin-top:20px; background:linear-gradient(135deg, #00d4aa, #00a884); border:none; color:#000; border-radius:10px; cursor:pointer; font-weight:700; font-size:16px;">保存配置</button>';
        html += '</div></div></div>';

        return html;
    },

    // Level 4: 结果
    renderLevel4: function() {
        var html = '<div style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(10,14,23,0.98); z-index:10000; overflow:auto;">';
        html += '<div style="max-width:500px; margin:0 auto; background:rgba(20,25,35,0.98); border:1px solid rgba(0,212,170,0.2); border-radius:15px; margin-top:30px;">';

        html += '<div style="padding:20px; border-bottom:1px solid rgba(255,255,255,0.1); display:flex; justify-content:space-between; align-items:center;">';
        html += '<div><span style="font-size:28px;">✅</span> <span style="font-size:18px; font-weight:700;">保存成功</span></div>';
        html += '<button onclick="SettingsModule.closePanel()" style="background:none; border:none; color:#888; font-size:24px; cursor:pointer;">✕</button>';
        html += '</div>';

        html += '<div style="padding:20px; text-align:center;">';
        html += '<div style="font-size:64px; margin-bottom:20px;">✅</div>';
        html += '<div style="font-size:24px; font-weight:700; color:#00d4aa; margin-bottom:10px;">配置已保存</div>';
        html += '<div style="color:#888; margin-bottom:20px;">ID: CFG' + Date.now().toString().slice(-8) + '</div>';
        html += '</div>';

        html += '<div style="padding:0 20px 20px;">';
        html += '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px; margin-bottom:15px;">';
        html += '<div style="display:flex; justify-content:space-between; margin-bottom:8px;"><span style="color:#888;">交易确认</span><span style="color:#00d4aa;">$1,000</span></div>';
        html += '<div style="display:flex; justify-content:space-between; margin-bottom:8px;"><span style="color:#888;">最大仓位</span><span style="color:#00d4aa;">80%</span></div>';
        html += '<div style="display:flex; justify-content:space-between;"><span style="color:#888;">会话超时</span><span style="color:#00d4aa;">30分钟</span></div>';
        html += '</div>';

        html += '<button onclick="SettingsModule.closePanel()" style="width:100%; padding:15px; background:linear-gradient(135deg, #00d4aa, #00a884); border:none; color:#000; border-radius:10px; cursor:pointer; font-weight:700; font-size:16px;">完成</button>';
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

    copyContact: function(value) {
        // 复制到剪贴板
        if (navigator.clipboard) {
            navigator.clipboard.writeText(value);
            if (typeof awShowToast === 'function') awShowToast('已复制: ' + value);
        }
    },

    closePanel: function() {
        var container = document.getElementById('settingsPanelContainer');
        if (container) {
            container.style.display = 'none';
            container.innerHTML = '';
        }
        this.state.level = 1;
        this.state.activeTab = 'settings';
    }
};

// Auto-init (panel display disabled on load)
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() { SettingsModule.init(); });
} else {
    SettingsModule.init();
}


// Init - Disabled auto-init
// // Auto-init restored
//     document.addEventListener('DOMContentLoaded', function() { SettingsModule.init(); });
// } else {
//     SettingsModule.init();
// }


// Auto-init (panel display disabled on load)
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() { SettingsModule.init(); });
} else {
    SettingsModule.init();
}
