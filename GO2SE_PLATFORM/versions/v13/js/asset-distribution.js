// ========== 钱包解构 + 资产分布模块 (变化触发更新) ==========
const WalletDeconstruct = {
    state: {
        level: 1,
        activeTab: 'overview',
        lastUpdate: null,
        changeTriggers: [],
        isWatching: false
    },

    // 钱包解构配置
    wallets: {
        main: {
            name: '主钱包', icon: '🏦', type: 'external',
            balance: 45000, originalBalance: 45000,
            change: 0, changeRate: 0,
            exposure: 'high', address: '0x****.main',
            transactions: []
        },
        transit: {
            name: '中转钱包', icon: '🔄', type: 'internal',
            balance: 10000, originalBalance: 10000,
            change: 0, changeRate: 0,
            exposure: 'medium', address: '0x****.transit',
            transactions: []
        },
        backup: {
            name: '备用钱包', icon: '🔐', type: 'cold',
            balance: 50000, originalBalance: 50000,
            change: 0, changeRate: 0,
            exposure: 'zero', address: '0x****.backup',
            transactions: []
        }
    },

    // 7工具钱包
    toolWallets: {
        rabbit: { name: '打兔子', icon: '🐰', balance: 2500, position: 25, change: 0, changeRate: 0 },
        mole: { name: '打地鼠', icon: '🐹', balance: 1700, position: 20, change: 0, changeRate: 0 },
        oracle: { name: '走着瞧', icon: '🔮', balance: 1275, position: 15, change: 0, changeRate: 0 },
        leader: { name: '跟大哥', icon: '👑', balance: 1275, position: 15, change: 0, changeRate: 0 },
        hitchhiker: { name: '搭便车', icon: '🍀', balance: 850, position: 10, change: 0, changeRate: 0 },
        airdrop: { name: '薅羊毛', icon: '💰', balance: 255, position: 3, change: 0, changeRate: 0 },
        crowdsource: { name: '穷孩子', icon: '👶', balance: 170, position: 2, change: 0, changeRate: 0 }
    },

    // 计算属性
    get totalAssets() { return 150000; },
    get netAssets() { return 98000; },
    get totalLiability() { return 52000; },
    get toolWalletTotal() {
        return Object.values(this.toolWallets).reduce(function(a, w) { return a + w.balance; }, 0);
    },

    // 变化触发器
    triggers: [
        { id: 'trade_executed', name: '交易执行', threshold: 1 },
        { id: 'balance_change', name: '余额变动', threshold: 0.01 },
        { id: 'position_change', name: '仓位变动', threshold: 5 },
        { id: 'profit_threshold', name: '盈利达标', threshold: 100 }
    ],

    init: function() {
        this.loadState();
        
        this.startChangeWatcher();
        console.log('💰 WalletDeconstruct initialized');
    },

    loadState: function() {
        try {
            var saved = localStorage.getItem('WalletDeconstructState');
            if (saved) {
                var data = JSON.parse(saved);
                this.state.level = data.level || 1;
                this.state.activeTab = data.activeTab || 'overview';
            }
        } catch(e) {}
    },

    saveState: function() {
        try {
            localStorage.setItem('WalletDeconstructState', JSON.stringify({
                level: this.state.level,
                activeTab: this.state.activeTab
            }));
        } catch(e) {}
    },

    renderPanel: function() {
        var container = document.getElementById('walletDeconstructContainer');
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
        html += '<div style="max-width:900px; margin:0 auto; background:rgba(20,25,35,0.98); border:1px solid rgba(0,212,170,0.2); border-radius:15px; margin-top:30px; margin-bottom:30px;">';

        // Header
        html += '<div style="padding:20px; border-bottom:1px solid rgba(255,255,255,0.1); display:flex; justify-content:space-between; align-items:center;">';
        html += '<div><span style="font-size:28px;">💰</span> <span style="font-size:18px; font-weight:700;">钱包解构</span> <span style="font-size:12px; color:#00d4aa; margin-left:10px;">● WATCHING</span></div>';
        html += '<div style="font-size:11px; color:#888;">更新: ' + (this.state.lastUpdate ? new Date(this.state.lastUpdate).toLocaleTimeString() : '--:--:--') + '</div>';
        html += '<button onclick="WalletDeconstruct.closePanel()" style="background:none; border:none; color:#888; font-size:24px; cursor:pointer; margin-left:15px;">✕</button>';
        html += '</div>';

        html += '<div style="padding:20px;">';

        // Tab切换
        html += '<div style="display:flex; gap:8px; margin-bottom:20px;">';
        var tabs = [
            { id: 'overview', name: '总览', icon: '📊' },
            { id: 'wallets', name: '钱包解构', icon: '💼' },
            { id: 'tools', name: '工具钱包', icon: '🐰' },
            { id: 'triggers', name: '触发器', icon: '⚡' }
        ];
        var self = this;
        tabs.forEach(function(tab) {
            var isActive = self.state.activeTab === tab.id;
            html += '<button onclick="WalletDeconstruct.selectTab(\'' + tab.id + '\')" style="flex:1; padding:10px; background:' + (isActive ? 'rgba(0,212,170,0.2)' : 'rgba(0,0,0,0.3)') + '; border:1px solid ' + (isActive ? '#00d4aa' : 'rgba(255,255,255,0.1)') + '; color:' + (isActive ? '#00d4aa' : '#888') + '; border-radius:8px; cursor:pointer; font-size:12px;">' + tab.icon + ' ' + tab.name + '</button>';
        });
        html += '</div>';

        // 财产总额卡片
        html += '<div style="background:linear-gradient(135deg, rgba(0,212,170,0.15), rgba(0,0,0,0.8)); border:2px solid rgba(0,212,170,0.3); border-radius:12px; padding:20px; margin-bottom:20px; text-align:center;">';
        html += '<div style="font-size:12px; color:#888; margin-bottom:5px;">财产总额</div>';
        html += '<div style="font-size:42px; font-weight:700; color:#00d4aa;">$' + this.totalAssets.toLocaleString() + '</div>';
        html += '<div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:15px; margin-top:15px;">';
        html += '<div><div style="font-size:11px; color:#888;">净资产</div><div style="font-size:18px; font-weight:700; color:#00d4aa;">$' + this.netAssets.toLocaleString() + '</div></div>';
        html += '<div><div style="font-size:11px; color:#888;">总负债</div><div style="font-size:18px; font-weight:700; color:#ef4444;">$' + this.totalLiability.toLocaleString() + '</div></div>';
        html += '<div><div style="font-size:11px; color:#888;">工具钱包</div><div style="font-size:18px; font-weight:700; color:#a78bfa;">$' + this.toolWalletTotal.toLocaleString() + '</div></div>';
        html += '</div>';
        html += '</div>';

        // 钱包解构图
        html += '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px; margin-bottom:15px;">';
        html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px;">💼 钱包解构</div>';

        // 主钱包
        html += '<div style="text-align:center; margin-bottom:20px;">';
        html += '<div onclick="WalletDeconstruct.selectTab(\'wallets\')" style="display:inline-block; padding:15px 30px; background:rgba(0,212,170,0.2); border:2px solid #00d4aa; border-radius:12px; cursor:pointer;">';
        html += '<div style="font-size:28px; margin-bottom:5px;">🏦</div>';
        html += '<div style="font-weight:700;">主钱包</div>';
        html += '<div style="font-size:20px; font-weight:700; color:#00d4aa;">$' + this.wallets.main.balance.toLocaleString() + '</div>';
        var mainChange = this.wallets.main.changeRate;
        html += '<div style="font-size:12px; color:' + (mainChange >= 0 ? '#00d4aa' : '#ef4444') + ';">' + (mainChange >= 0 ? '+' : '') + mainChange.toFixed(2) + '%</div>';
        html += '</div>';
        html += '</div>';

        // 中转和备用
        html += '<div style="display:flex; justify-content:center; gap:15px; margin-bottom:20px;">';
        ['transit', 'backup'].forEach(function(key) {
            var w = self.wallets[key];
            html += '<div onclick="WalletDeconstruct.selectTab(\'wallets\')" style="flex:1; max-width:150px; padding:12px; background:rgba(0,0,0,0.3); border:1px solid rgba(255,255,255,0.1); border-radius:10px; cursor:pointer; text-align:center;">';
            html += '<div style="font-size:20px; margin-bottom:5px;">' + w.icon + '</div>';
            html += '<div style="font-size:12px; color:#888;">' + w.name + '</div>';
            html += '<div style="font-size:16px; font-weight:700; color:#00d4aa;">$' + w.balance.toLocaleString() + '</div>';
            html += '</div>';
        });
        html += '</div>';

        // 7工具钱包
        html += '<div style="font-size:12px; color:#888; margin-bottom:10px;">🐰 7工具钱包 (总计 $' + this.toolWalletTotal.toLocaleString() + ')</div>';
        html += '<div style="display:grid; grid-template-columns:repeat(7,1fr); gap:8px;">';
        Object.values(this.toolWallets).forEach(function(tool) {
            var changeRate = tool.changeRate;
            html += '<div onclick="WalletDeconstruct.selectTab(\'tools\')" style="padding:10px 5px; background:rgba(0,0,0,0.3); border-radius:8px; cursor:pointer; text-align:center;">';
            html += '<div style="font-size:16px; margin-bottom:3px;">' + tool.icon + '</div>';
            html += '<div style="font-size:9px; color:#888;">' + tool.name + '</div>';
            html += '<div style="font-size:11px; font-weight:600; color:#00d4aa;">$' + tool.balance.toLocaleString() + '</div>';
            html += '<div style="font-size:9px; color:' + (changeRate >= 0 ? '#00d4aa' : '#ef4444') + ';">' + (changeRate >= 0 ? '+' : '') + changeRate.toFixed(1) + '%</div>';
            html += '</div>';
        });
        html += '</div>';

        html += '</div>';

        // 变化触发器状态
        html += '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px;">';
        html += '<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">';
        html += '<div style="font-size:14px; font-weight:600;">⚡ 变化触发器</div>';
        html += '<span style="font-size:11px; color:#00d4aa;">● ACTIVE</span>';
        html += '</div>';
        html += '<div style="display:flex; gap:8px; flex-wrap:wrap;">';
        this.triggers.forEach(function(t) {
            html += '<span style="font-size:11px; padding:4px 10px; background:rgba(0,212,170,0.1); border:1px solid rgba(0,212,170,0.3); color:#00d4aa; border-radius:20px;">' + t.name + '</span>';
        });
        html += '</div>';
        html += '</div>';

        html += '<button onclick="WalletDeconstruct.navigateLevel(2)" style="width:100%; padding:12px; margin-top:20px; background:rgba(0,212,170,0.2); border:1px solid #00d4aa; color:#00d4aa; border-radius:8px; cursor:pointer; font-weight:600;">查看详情 →</button>';
        html += '</div></div></div>';

        return html;
    },

    // Level 2: 详情
    renderLevel2: function() {
        var self = this;
        var html = '<div style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(10,14,23,0.98); z-index:10000; overflow:auto;">';
        html += '<div style="max-width:800px; margin:0 auto; background:rgba(20,25,35,0.98); border:1px solid rgba(0,212,170,0.2); border-radius:15px; margin-top:30px; margin-bottom:30px;">';

        html += '<div style="padding:20px; border-bottom:1px solid rgba(255,255,255,0.1); display:flex; justify-content:space-between; align-items:center;">';
        html += '<div><span style="font-size:28px;">💰</span> <span style="font-size:18px; font-weight:700;">钱包详情</span></div>';
        html += '<button onclick="WalletDeconstruct.closePanel()" style="background:none; border:none; color:#888; font-size:24px; cursor:pointer;">✕</button>';
        html += '</div>';

        html += '<div style="padding:20px;">';
        html += '<button onclick="WalletDeconstruct.navigateLevel(1)" style="padding:8px 15px; background:rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.2); color:#fff; border-radius:8px; cursor:pointer; margin-bottom:15px;">← 返回</button>';

        // 钱包详情
        var wallets = [this.wallets.main, this.wallets.transit, this.wallets.backup];
        wallets.forEach(function(w) {
            var changeColor = w.changeRate >= 0 ? '#00d4aa' : '#ef4444';
            html += '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px; margin-bottom:15px;">';
            html += '<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">';
            html += '<div style="display:flex; align-items:center; gap:10px;">';
            html += '<span style="font-size:28px;">' + w.icon + '</span>';
            html += '<div><div style="font-weight:700;">' + w.name + '</div><div style="font-size:11px; color:#888;">地址: ' + w.address + ' | 暴露度: ' + w.exposure + '</div></div>';
            html += '</div>';
            html += '<div style="text-align:right;">';
            html += '<div style="font-size:20px; font-weight:700; color:#00d4aa;">$' + w.balance.toLocaleString() + '</div>';
            html += '<div style="font-size:12px; color:' + changeColor + ';">' + (w.changeRate >= 0 ? '+' : '') + w.change.toFixed(2) + ' (' + w.changeRate.toFixed(2) + '%)</div>';
            html += '</div>';
            html += '</div>';

            // 变化进度条
            var changeWidth = Math.min(100, Math.abs(w.changeRate) * 10);
            html += '<div style="height:4px; background:rgba(255,255,255,0.1); border-radius:2px; margin-bottom:10px;">';
            html += '<div style="height:100%; width:' + changeWidth + '%; background:' + changeColor + '; border-radius:2px;"></div>';
            html += '</div>';

            // 交易记录预览
            if (w.transactions && w.transactions.length > 0) {
                html += '<div style="font-size:11px; color:#888;">最近交易: ' + w.transactions.length + '笔</div>';
            }
            html += '</div>';
        });

        // 7工具钱包详情
        html += '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px;">';
        html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px;">🐰 工具钱包详情</div>';

        Object.values(this.toolWallets).forEach(function(tool) {
            var changeColor = tool.changeRate >= 0 ? '#00d4aa' : '#ef4444';
            html += '<div style="display:flex; justify-content:space-between; align-items:center; padding:12px; background:rgba(0,0,0,0.3); border-radius:8px; margin-bottom:8px;">';
            html += '<div style="display:flex; align-items:center; gap:10px;">';
            html += '<span style="font-size:24px;">' + tool.icon + '</span>';
            html += '<div><div style="font-weight:600;">' + tool.name + '</div><div style="font-size:11px; color:#888;">仓位: ' + tool.position + '%</div></div>';
            html += '</div>';
            html += '<div style="text-align:right;">';
            html += '<div style="font-size:16px; font-weight:700; color:#00d4aa;">$' + tool.balance.toLocaleString() + '</div>';
            html += '<div style="font-size:11px; color:' + changeColor + ';">' + (tool.changeRate >= 0 ? '+' : '') + tool.changeRate.toFixed(2) + '%</div>';
            html += '</div>';
            html += '</div>';
        });

        html += '</div>';

        html += '<button onclick="WalletDeconstruct.navigateLevel(3)" style="width:100%; padding:12px; margin-top:20px; background:rgba(0,212,170,0.2); border:1px solid #00d4aa; color:#00d4aa; border-radius:8px; cursor:pointer; font-weight:600;">资金操作 →</button>';
        html += '</div></div></div>';

        return html;
    },

    // Level 3: 操作
    renderLevel3: function() {
        var html = '<div style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(10,14,23,0.98); z-index:10000; overflow:auto;">';
        html += '<div style="max-width:500px; margin:0 auto; background:rgba(20,25,35,0.98); border:1px solid rgba(0,212,170,0.2); border-radius:15px; margin-top:30px;">';

        html += '<div style="padding:20px; border-bottom:1px solid rgba(255,255,255,0.1); display:flex; justify-content:space-between; align-items:center;">';
        html += '<div><span style="font-size:28px;">💰</span> <span style="font-size:18px; font-weight:700;">资金操作</span></div>';
        html += '<button onclick="WalletDeconstruct.closePanel()" style="background:none; border:none; color:#888; font-size:24px; cursor:pointer;">✕</button>';
        html += '</div>';

        html += '<div style="padding:20px;">';
        html += '<button onclick="WalletDeconstruct.navigateLevel(2)" style="padding:8px 15px; background:rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.2); color:#fff; border-radius:8px; cursor:pointer; margin-bottom:15px;">← 返回</button>';

        html += '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px;">';
        html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px;">⚡ 资金转账</div>';

        html += '<div style="margin-bottom:15px;">';
        html += '<label style="font-size:12px; color:#888; display:block; margin-bottom:5px;">从钱包</label>';
        html += '<select id="fromWallet" style="width:100%; padding:10px; background:rgba(0,0,0,0.3); border:1px solid rgba(255,255,255,0.2); border-radius:8px; color:#fff;">';
        html += '<option value="main">🏦 主钱包 ($' + this.wallets.main.balance.toLocaleString() + ')</option>';
        html += '<option value="transit">🔄 中转钱包 ($' + this.wallets.transit.balance.toLocaleString() + ')</option>';
        html += '</select>';
        html += '</div>';

        html += '<div style="margin-bottom:15px;">';
        html += '<label style="font-size:12px; color:#888; display:block; margin-bottom:5px;">到工具</label>';
        html += '<select id="toTool" style="width:100%; padding:10px; background:rgba(0,0,0,0.3); border:1px solid rgba(255,255,255,0.2); border-radius:8px; color:#fff;">';
        Object.values(this.toolWallets).forEach(function(tool) {
            html += '<option value="' + tool.name + '">' + tool.icon + ' ' + tool.name + ' ($' + tool.balance.toLocaleString() + ')</option>';
        });
        html += '</select>';
        html += '</div>';

        html += '<div style="margin-bottom:15px;">';
        html += '<label style="font-size:12px; color:#888; display:block; margin-bottom:5px;">金额 ($)</label>';
        html += '<input type="number" id="transferAmount" placeholder="0.00" style="width:100%; padding:10px; background:rgba(0,0,0,0.3); border:1px solid rgba(255,255,255,0.2); border-radius:8px; color:#fff; font-size:16px;">';
        html += '</div>';

        html += '<div style="font-size:11px; color:#888; margin-bottom:15px; padding:10px; background:rgba(0,0,0,0.3); border-radius:6px;">';
        html += '⛽ Gas费估算: <span style="color:#00d4aa;">~$0.01 (内部转账)</span>';
        html += '</div>';

        html += '</div>';

        html += '<div style="display:flex; gap:10px; margin-top:20px;">';
        html += '<button onclick="WalletDeconstruct.navigateLevel(4)" style="flex:1; padding:12px; background:linear-gradient(135deg, #00d4aa, #00a884); color:#000; border:none; border-radius:8px; cursor:pointer; font-weight:600;">确认转账</button>';
        html += '</div>';
        html += '</div></div></div>';

        return html;
    },

    // Level 4: 结果
    renderLevel4: function() {
        var html = '<div style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(10,14,23,0.98); z-index:10000; overflow:auto;">';
        html += '<div style="max-width:500px; margin:0 auto; background:rgba(20,25,35,0.98); border:1px solid rgba(0,212,170,0.2); border-radius:15px; margin-top:30px;">';

        html += '<div style="padding:20px; border-bottom:1px solid rgba(255,255,255,0.1); display:flex; justify-content:space-between; align-items:center;">';
        html += '<div><span style="font-size:28px;">✅</span> <span style="font-size:18px; font-weight:700;">转账成功</span></div>';
        html += '<button onclick="WalletDeconstruct.closePanel()" style="background:none; border:none; color:#888; font-size:24px; cursor:pointer;">✕</button>';
        html += '</div>';

        html += '<div style="padding:20px; text-align:center;">';
        html += '<div style="font-size:64px; margin-bottom:20px;">✅</div>';
        html += '<div style="font-size:24px; font-weight:700; color:#00d4aa; margin-bottom:10px;">钱包已更新</div>';
        html += '<div style="color:#888; margin-bottom:20px;">交易号: W' + Date.now().toString().slice(-8) + '</div>';
        html += '</div>';

        html += '<div style="padding:0 20px 20px;">';
        html += '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px; margin-bottom:15px;">';
        html += '<div style="display:flex; justify-content:space-between; margin-bottom:8px;"><span style="color:#888;">从</span><span>🏦 主钱包</span></div>';
        html += '<div style="display:flex; justify-content:space-between; margin-bottom:8px;"><span style="color:#888;">到</span><span>🐰 打兔子</span></div>';
        html += '<div style="display:flex; justify-content:space-between;"><span style="color:#888;">金额</span><span style="color:#00d4aa; font-weight:600;">$1,000</span></div>';
        html += '</div>';

        html += '<button onclick="WalletDeconstruct.closePanel()" style="width:100%; padding:15px; background:linear-gradient(135deg, #00d4aa, #00a884); color:#000; border:none; border-radius:10px; cursor:pointer; font-weight:700; font-size:16px;">完成</button>';
        html += '</div></div></div>';

        return html;
    },

    // 变化触发监听
    startChangeWatcher: function() {
        var self = this;
        setInterval(function() {
            // 模拟钱包变化
            var hasChange = false;

            // 主钱包随机变化
            if (Math.random() > 0.8) {
                var change = (Math.random() - 0.5) * 100;
                self.wallets.main.balance += change;
                self.wallets.main.change = change;
                self.wallets.main.changeRate = (change / self.wallets.main.originalBalance) * 100;
                hasChange = true;
            }

            // 工具钱包随机变化
            Object.values(self.toolWallets).forEach(function(tool) {
                if (Math.random() > 0.7) {
                    var tChange = (Math.random() - 0.5) * 50;
                    tool.balance += tChange;
                    tool.change = tChange;
                    tool.changeRate = (tChange / (tool.balance - tChange)) * 100;
                    hasChange = true;
                }
            });

            if (hasChange) {
                self.state.lastUpdate = Date.now();
                self.triggerUpdate();
            }
        }, 5000); // 每5秒检查一次
    },

    // 触发更新
    triggerUpdate: function() {
        // 检查触发器
        var triggered = [];
        this.triggers.forEach(function(t) {
            if (Math.random() > 0.9) {
                triggered.push(t);
            }
        });

        // 如果有变化，更新UI
        if (this.state.level === 1 || this.state.activeTab === 'overview') {
            
        }

        // 显示触发通知
        if (triggered.length > 0 && typeof awShowToast === 'function') {
            triggered.forEach(function(t) {
                awShowToast('⚡ 触发: ' + t.name);
            });
        }
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
        var container = document.getElementById('walletDeconstructContainer');
        if (container) {
            container.style.display = 'none';
            container.innerHTML = '';
        }
        this.state.level = 1;
        this.state.activeTab = 'overview';
    }
};

// Auto-init (panel display disabled on load)
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() { WalletDeconstruct.init(); });
} else {
    WalletDeconstruct.init();
}


// Init - Disabled auto-init
// // Auto-init restored
//     document.addEventListener('DOMContentLoaded', function() { WalletDeconstruct.init(); });
// } else {
//     WalletDeconstruct.init();
// }


// Auto-init (panel display disabled on load)
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() { WalletDeconstruct.init(); });
} else {
    WalletDeconstruct.init();
}
