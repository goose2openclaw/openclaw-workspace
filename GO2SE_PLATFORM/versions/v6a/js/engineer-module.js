// ========== 工善其事模块 - Engineer Module ==========
window.EngineerModule = {
    state: {
        level: 1,
        activeSubmodule: 'signal', // signal, strategy, simulation, sonar
        signals: {},
        strategies: [],
        simulations: [],
        sonarModels: [],
        history: []
    },

    // 子系统配置
    submodules: {
        signal: {
            name: '市场信号',
            icon: '📡',
            description: '多源信号聚合与综合判断'
        },
        strategy: {
            name: '策略中心',
            icon: '🏆',
            description: '123趋势模型策略库'
        },
        simulation: {
            name: '仿真引擎',
            icon: '🔄',
            description: 'MiroFish全向仿真'
        },
        sonar: {
            name: '声纳库',
            icon: '📉',
            description: '123个趋势监测指标'
        }
    },

    // 信号源
    signalSources: [
        { id: 'binance', name: 'Binance', status: 'online', latency: 45, signal: 'bull' },
        { id: 'bybit', name: 'Bybit', status: 'online', latency: 52, signal: 'bull' },
        { id: 'okx', name: 'OKX', status: 'standby', latency: 68, signal: 'neutral' },
        { id: 'mirofish', name: 'MiroFish', status: 'online', latency: 120, signal: 'bull' },
        { id: 'twitter', name: 'Twitter/KOL', status: 'online', latency: 0, signal: 'neutral' }
    ],

    // 策略列表
    strategyList: [
        { id: 'ema', name: 'EMA交叉', type: '原创', winrate: 74.5, signals: 1234 },
        { id: 'rsi', name: 'RSI超卖', type: '知名', winrate: 68.2, signals: 856 },
        { id: 'macd', name: 'MACD背离', type: '原创', winrate: 71.8, signals: 967 },
        { id: 'bollinger', name: '布林带', type: '知名', winrate: 65.5, signals: 543 },
        { id: 'volume', name: '成交量异动', type: '原创', winrate: 72.1, signals: 789 }
    ],

    // 仿真状态
    simulationStatus: {
        lastRun: '2026-04-06 12:00',
        status: 'idle', // idle, running, completed
        score: 87.6,
        details: {
            A1: { name: '投资组合', score: 82 },
            A2: { name: '风控规则', score: 85 },
            A3: { name: '多样化', score: 79 },
            B1: { name: '打兔子', score: 92 },
            B2: { name: '打地鼠', score: 88 },
            B3: { name: '走着瞧', score: 91 }
        }
    },

    // 声纳库123模型
    sonarModels: {
        trend: { name: '趋势类', count: 30, examples: ['EMA20>EMA50', 'MA金叉'] },
        momentum: { name: '动量类', count: 25, examples: ['RSI>70', 'MACD金叉'] },
        volatility: { name: '波动类', count: 20, examples: ['Bollinger突破', 'ATR收缩'] },
        volume: { name: '成交量类', count: 15, examples: ['OBV上升', 'VWAP偏离'] },
        reversal: { name: '反转类', count: 15, examples: ['CCI超买', 'Williams%R'] },
        channel: { name: '通道类', count: 10, examples: ['通道突破'] },
        other: { name: '其他类', count: 8, examples: ['自定义指标'] }
    },

    init: function() {
        this.loadState();
        
        this.startAutoUpdate();
        console.log('⚙️ EngineerModule initialized');
    },

    loadState: function() {
        try {
            var saved = localStorage.getItem('EngineerModuleState');
            if (saved) {
                var data = JSON.parse(saved);
                this.state.level = data.level || 1;
                this.state.activeSubmodule = data.activeSubmodule || 'signal';
            }
        } catch(e) {}
    },

    saveState: function() {
        try {
            localStorage.setItem('EngineerModuleState', JSON.stringify({
                level: this.state.level,
                activeSubmodule: this.state.activeSubmodule
            }));
        } catch(e) {}
    },

    // 渲染主面板
    renderPanel: function() {
        var container = document.getElementById('engineerPanelContainer');
        if (!container) return;

        var html = '';
        if (this.state.level === 1) {
            html = this.renderLevel1();
        } else if (this.state.level === 2) {
            html = this.renderLevel2();
        } else if (this.state.level === 3) {
            html = this.renderLevel3();
        } else if (this.state.level === 4) {
            html = this.renderLevel4();
        }

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
        html += '<div><span style="font-size:28px;">⚙️</span> <span style="font-size:18px; font-weight:700;">工善其事</span></div>';
        html += '<button onclick="EngineerModule.closePanel()" style="background:none; border:none; color:#888; font-size:24px; cursor:pointer;">✕</button>';
        html += '</div>';

        // 子系统选择
        html += '<div style="padding:20px;">';
        html += '<div style="font-size:12px; color:#888; margin-bottom:10px;">选择子系统</div>';
        html += '<div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">';
        Object.keys(this.submodules).forEach(function(key) {
            var sub = self.submodules[key];
            var isActive = self.state.activeSubmodule === key;
            html += '<div onclick="EngineerModule.selectSubmodule(\'' + key + '\')" style="background:' + (isActive ? 'rgba(0,212,170,0.2)' : 'rgba(0,0,0,0.3)') + '; border:1px solid ' + (isActive ? '#00d4aa' : 'rgba(255,255,255,0.1)') + '; border-radius:10px; padding:15px; cursor:pointer;">';
            html += '<div style="font-size:20px; margin-bottom:5px;">' + sub.icon + '</div>';
            html += '<div style="font-weight:600; font-size:14px;">' + sub.name + '</div>';
            html += '<div style="font-size:11px; color:#888; margin-top:3px;">' + sub.description + '</div>';
            html += '</div>';
        });
        html += '</div>';

        // 当前子系统总览
        html += '<div style="margin-top:20px;">';
        html += this.renderSubmoduleOverview();
        html += '</div>';

        // 操作按钮
        html += '<div style="display:flex; gap:10px; margin-top:20px;">';
        html += '<button onclick="EngineerModule.navigateLevel(2)" style="flex:1; padding:12px; background:rgba(0,212,170,0.2); border:1px solid #00d4aa; color:#00d4aa; border-radius:8px; cursor:pointer; font-weight:600;">查看详情 →</button>';
        html += '</div>';
        html += '</div></div></div>';

        return html;
    },

    // 子系统总览
    renderSubmoduleOverview: function() {
        var sub = this.state.activeSubmodule;
        var html = '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px;">';

        if (sub === 'signal') {
            html += '<div style="font-size:14px; font-weight:600; margin-bottom:10px;">📡 市场信号总览</div>';
            html += '<div style="display:grid; grid-template-columns:repeat(5,1fr); gap:8px;">';
            this.signalSources.forEach(function(src) {
                html += '<div style="text-align:center; padding:8px; background:rgba(0,0,0,0.3); border-radius:8px;">';
                html += '<div style="font-size:12px; font-weight:600;">' + src.name + '</div>';
                html += '<div style="font-size:10px; color:' + (src.status === 'online' ? '#00d4aa' : '#f59e0b') + ';">' + (src.status === 'online' ? '● 在线' : '○ 待机') + '</div>';
                html += '<div style="font-size:9px; color:#888;">' + src.latency + 'ms</div>';
                html += '</div>';
            });
            html += '</div>';
        } else if (sub === 'strategy') {
            var avgWinrate = Math.round(this.strategyList.reduce(function(a, b) { return a + b.winrate; }, 0) / this.strategyList.length);
            html += '<div style="font-size:14px; font-weight:600; margin-bottom:10px;">🏆 策略中心总览</div>';
            html += '<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">';
            html += '<span style="font-size:12px; color:#888;">组合胜率</span>';
            html += '<span style="font-size:24px; font-weight:700; color:#00d4aa;">' + avgWinrate + '%</span>';
            html += '</div>';
            html += '<div style="font-size:11px; color:#888;">策略数量: ' + this.strategyList.length + ' | 123趋势模型</div>';
        } else if (sub === 'simulation') {
            html += '<div style="font-size:14px; font-weight:600; margin-bottom:10px;">🔄 仿真引擎状态</div>';
            html += '<div style="display:flex; justify-content:space-between; align-items:center;">';
            html += '<div><div style="font-size:11px; color:#888;">上次仿真</div><div style="font-size:12px;">' + this.simulationStatus.lastRun + '</div></div>';
            html += '<div style="text-align:right;"><div style="font-size:11px; color:#888;">仿真评分</div><div style="font-size:24px; font-weight:700; color:#00d4aa;">' + this.simulationStatus.score + '</div></div>';
            html += '</div>';
        } else if (sub === 'sonar') {
            var total = Object.values(this.sonarModels).reduce(function(a, b) { return a + b.count; }, 0);
            html += '<div style="font-size:14px; font-weight:600; margin-bottom:10px;">📉 声纳库总览</div>';
            html += '<div style="display:flex; justify-content:space-between; align-items:center;">';
            html += '<div><div style="font-size:11px; color:#888;">趋势模型总数</div><div style="font-size:24px; font-weight:700; color:#00d4aa;">' + total + '</div></div>';
            html += '<div style="text-align:right;"><div style="font-size:11px; color:#888;">模型类别</div><div style="font-size:14px;">' + Object.keys(this.sonarModels).length + ' 类</div></div>';
            html += '</div>';
        }

        html += '</div>';
        return html;
    },

    // Level 2: 详情
    renderLevel2: function() {
        var self = this;
        var sub = this.state.activeSubmodule;
        var subInfo = this.submodules[sub];

        var html = '<div style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(10,14,23,0.98); z-index:10000; overflow:auto;">';
        html += '<div style="max-width:800px; margin:0 auto; background:rgba(20,25,35,0.98); border:1px solid rgba(0,212,170,0.2); border-radius:15px; margin-top:30px; margin-bottom:30px;">';

        // Header
        html += '<div style="padding:20px; border-bottom:1px solid rgba(255,255,255,0.1); display:flex; justify-content:space-between; align-items:center;">';
        html += '<div><span style="font-size:28px;">' + subInfo.icon + '</span> <span style="font-size:18px; font-weight:700;">' + subInfo.name + ' - 详情</span></div>';
        html += '<button onclick="EngineerModule.closePanel()" style="background:none; border:none; color:#888; font-size:24px; cursor:pointer;">✕</button>';
        html += '</div>';

        html += '<div style="padding:20px;">';

        // 返回和导航
        html += '<button onclick="EngineerModule.navigateLevel(1)" style="padding:8px 15px; background:rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.2); color:#fff; border-radius:8px; cursor:pointer; margin-bottom:15px;">← 返回总览</button>';

        // 子系统切换
        html += '<div style="display:flex; gap:8px; margin-bottom:15px; flex-wrap:wrap;">';
        Object.keys(this.submodules).forEach(function(key) {
            var s = self.submodules[key];
            var isActive = self.state.activeSubmodule === key;
            html += '<button onclick="EngineerModule.selectSubmodule(\'' + key + '\'); EngineerModule.navigateLevel(2)" style="padding:8px 12px; background:' + (isActive ? 'rgba(0,212,170,0.2)' : 'rgba(0,0,0,0.3)') + '; border:1px solid ' + (isActive ? '#00d4aa' : 'rgba(255,255,255,0.1)') + '; color:' + (isActive ? '#00d4aa' : '#888') + '; border-radius:20px; cursor:pointer; font-size:12px;">' + s.icon + ' ' + s.name + '</button>';
        });
        html += '</div>';

        // 详情内容
        if (sub === 'signal') {
            html += this.renderSignalDetail();
        } else if (sub === 'strategy') {
            html += this.renderStrategyDetail();
        } else if (sub === 'simulation') {
            html += this.renderSimulationDetail();
        } else if (sub === 'sonar') {
            html += this.renderSonarDetail();
        }

        // 操作按钮
        html += '<div style="display:flex; gap:10px; margin-top:20px;">';
        html += '<button onclick="EngineerModule.navigateLevel(3)" style="flex:1; padding:12px; background:rgba(0,212,170,0.2); border:1px solid #00d4aa; color:#00d4aa; border-radius:8px; cursor:pointer; font-weight:600;">配置设置 →</button>';
        html += '</div>';
        html += '</div></div></div>';

        return html;
    },

    // 信号详情
    renderSignalDetail: function() {
        var html = '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px;">';
        html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px;">📡 信号源详情</div>';

        var self = this;
        this.signalSources.forEach(function(src) {
            html += '<div style="display:flex; justify-content:space-between; align-items:center; padding:12px; background:rgba(0,0,0,0.3); border-radius:8px; margin-bottom:8px;">';
            html += '<div><div style="font-weight:600;">' + src.name + '</div><div style="font-size:11px; color:#888;">延迟: ' + src.latency + 'ms</div></div>';
            html += '<div style="text-align:right;"><div style="color:' + (src.signal === 'bull' ? '#00d4aa' : src.signal === 'bear' ? '#ef4444' : '#888') + '; font-weight:600;">' + (src.signal === 'bull' ? '看涨' : src.signal === 'bear' ? '看跌' : '中性') + '</div>';
            html += '<div style="font-size:10px; color:' + (src.status === 'online' ? '#00d4aa' : '#f59e0b') + ';">' + (src.status === 'online' ? '● 在线' : '○ 待机') + '</div></div>';
            html += '</div>';
        });

        html += '</div>';
        return html;
    },

    // 策略详情
    renderStrategyDetail: function() {
        var html = '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px;">';
        html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px;">🏆 策略详情</div>';

        var self = this;
        this.strategyList.forEach(function(strat) {
            html += '<div style="padding:12px; background:rgba(0,0,0,0.3); border-radius:8px; margin-bottom:8px;">';
            html += '<div style="display:flex; justify-content:space-between; margin-bottom:5px;">';
            html += '<div style="font-weight:600;">' + strat.name + '</div>';
            html += '<div style="color:#00d4aa; font-weight:600;">' + strat.winrate + '%</div>';
            html += '</div>';
            html += '<div style="display:flex; gap:8px; font-size:11px;">';
            html += '<span style="padding:2px 6px; background:rgba(0,212,170,0.2); color:#00d4aa; border-radius:4px;">' + strat.type + '</span>';
            html += '<span style="color:#888;">信号数: ' + strat.signals + '</span>';
            html += '</div>';
            html += '</div>';
        });

        html += '</div>';
        return html;
    },

    // 仿真详情
    renderSimulationDetail: function() {
        var html = '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px;">';
        html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px;">🔄 MiroFish仿真详情</div>';

        html += '<div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:15px;">';
        Object.keys(this.simulationStatus.details).forEach(function(key) {
            var detail = self.simulationStatus.details[key];
            html += '<div style="padding:12px; background:rgba(0,0,0,0.3); border-radius:8px;">';
            html += '<div style="font-size:11px; color:#888;">' + detail.name + '</div>';
            html += '<div style="font-size:20px; font-weight:700; color:' + (detail.score >= 80 ? '#00d4aa' : detail.score >= 60 ? '#f59e0b' : '#ef4444') + ';">' + detail.score + '</div>';
            html += '</div>';
        });
        html += '</div>';

        html += '<div style="display:flex; justify-content:space-between; padding:12px; background:rgba(0,0,0,0.3); border-radius:8px;">';
        html += '<span style="color:#888;">上次仿真</span>';
        html += '<span>' + this.simulationStatus.lastRun + '</span>';
        html += '</div>';
        html += '</div>';
        return html;
    },

    // 声纳详情
    renderSonarDetail: function() {
        var html = '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px;">';
        html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px;">📉 声纳库123模型</div>';

        var self = this;
        Object.keys(this.sonarModels).forEach(function(key) {
            var model = self.sonarModels[key];
            html += '<div style="padding:12px; background:rgba(0,0,0,0.3); border-radius:8px; margin-bottom:8px;">';
            html += '<div style="display:flex; justify-content:space-between; margin-bottom:5px;">';
            html += '<div style="font-weight:600;">' + model.name + '</div>';
            html += '<div style="color:#00d4aa; font-weight:600;">' + model.count + '个</div>';
            html += '</div>';
            html += '<div style="font-size:11px; color:#888;">' + model.examples.join(' | ') + '</div>';
            html += '</div>';
        });

        html += '</div>';
        return html;
    },

    // Level 3: 配置
    renderLevel3: function() {
        var subInfo = this.submodules[this.state.activeSubmodule];

        var html = '<div style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(10,14,23,0.98); z-index:10000; overflow:auto;">';
        html += '<div style="max-width:600px; margin:0 auto; background:rgba(20,25,35,0.98); border:1px solid rgba(0,212,170,0.2); border-radius:15px; margin-top:30px;">';

        html += '<div style="padding:20px; border-bottom:1px solid rgba(255,255,255,0.1); display:flex; justify-content:space-between; align-items:center;">';
        html += '<div><span style="font-size:28px;">' + subInfo.icon + '</span> <span style="font-size:18px; font-weight:700;">' + subInfo.name + ' - 配置</span></div>';
        html += '<button onclick="EngineerModule.closePanel()" style="background:none; border:none; color:#888; font-size:24px; cursor:pointer;">✕</button>';
        html += '</div>';

        html += '<div style="padding:20px;">';
        html += '<button onclick="EngineerModule.navigateLevel(2)" style="padding:8px 15px; background:rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.2); color:#fff; border-radius:8px; cursor:pointer; margin-bottom:15px;">← 返回详情</button>';

        html += '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px;">';
        html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px;">⚙️ 参数配置</div>';

        html += '<div style="margin-bottom:15px;">';
        html += '<label style="font-size:12px; color:#888; display:block; margin-bottom:5px;">启用自动更新</label>';
        html += '<select style="width:100%; padding:10px; background:rgba(0,0,0,0.3); border:1px solid rgba(255,255,255,0.2); border-radius:8px; color:#fff;">';
        html += '<option>每5分钟</option><option>每15分钟</option><option>每30分钟</option><option>每小时</option>';
        html += '</select>';
        html += '</div>';

        html += '<div style="margin-bottom:15px;">';
        html += '<label style="font-size:12px; color:#888; display:block; margin-bottom:5px;">告警阈值</label>';
        html += '<input type="range" min="0" max="100" value="75" style="width:100%;">';
        html += '<div style="display:flex; justify-content:space-between; font-size:11px; color:#888;"><span>0%</span><span>75%</span><span>100%</span></div>';
        html += '</div>';

        html += '<div style="margin-bottom:15px;">';
        html += '<label style="font-size:12px; color:#888; display:block; margin-bottom:5px;">通知方式</label>';
        html += '<div style="display:flex; gap:10px;">';
        html += '<label style="flex:1; display:flex; align-items:center; gap:5px; padding:10px; background:rgba(0,212,170,0.2); border:1px solid #00d4aa; border-radius:8px; cursor:pointer;"><input type="checkbox" checked> 邮件</label>';
        html += '<label style="flex:1; display:flex; align-items:center; gap:5px; padding:10px; background:rgba(0,0,0,0.3); border:1px solid rgba(255,255,255,0.2); border-radius:8px; cursor:pointer;"><input type="checkbox"> 短信</label>';
        html += '</div>';
        html += '</div>';

        html += '</div>';

        html += '<div style="display:flex; gap:10px; margin-top:20px;">';
        html += '<button onclick="EngineerModule.navigateLevel(2)" style="flex:1; padding:12px; background:rgba(255,255,255,0.1); color:#fff; border:1px solid rgba(255,255,255,0.2); border-radius:8px; cursor:pointer;">取消</button>';
        html += '<button onclick="EngineerModule.navigateLevel(4)" style="flex:1; padding:12px; background:linear-gradient(135deg, #00d4aa, #00a884); color:#000; border:none; border-radius:8px; cursor:pointer; font-weight:600;">保存配置</button>';
        html += '</div>';
        html += '</div></div></div>';

        return html;
    },

    // Level 4: 结果
    renderLevel4: function() {
        var html = '<div style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(10,14,23,0.98); z-index:10000; overflow:auto;">';
        html += '<div style="max-width:600px; margin:0 auto; background:rgba(20,25,35,0.98); border:1px solid rgba(0,212,170,0.2); border-radius:15px; margin-top:30px;">';

        html += '<div style="padding:20px; border-bottom:1px solid rgba(255,255,255,0.1); display:flex; justify-content:space-between; align-items:center;">';
        html += '<div><span style="font-size:28px;">✅</span> <span style="font-size:18px; font-weight:700;">执行结果</span></div>';
        html += '<button onclick="EngineerModule.closePanel()" style="background:none; border:none; color:#888; font-size:24px; cursor:pointer;">✕</button>';
        html += '</div>';

        html += '<div style="padding:20px; text-align:center;">';
        html += '<div style="font-size:64px; margin-bottom:20px;">✅</div>';
        html += '<div style="font-size:24px; font-weight:700; color:#00d4aa; margin-bottom:10px;">配置已保存</div>';
        html += '<div style="color:#888; margin-bottom:20px;">订单号: EN' + Date.now().toString().slice(-8) + '</div>';
        html += '</div>';

        html += '<div style="padding:0 20px 20px;">';
        html += '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px; margin-bottom:15px;">';
        html += '<div style="font-size:12px; color:#888; margin-bottom:8px;">配置状态</div>';
        html += '<div style="display:flex; justify-content:space-between;"><span>自动更新</span><span style="color:#00d4aa;">已启用</span></div>';
        html += '<div style="display:flex; justify-content:space-between; margin-top:5px;"><span>告警阈值</span><span style="color:#00d4aa;">75%</span></div>';
        html += '</div>';

        html += '<button onclick="EngineerModule.closePanel()" style="width:100%; padding:15px; background:linear-gradient(135deg, #00d4aa, #00a884); color:#000; border:none; border-radius:10px; cursor:pointer; font-weight:700; font-size:16px;">完成</button>';
        html += '</div></div></div>';

        return html;
    },

    // 选择子系统
    selectSubmodule: function(sub) {
        this.state.activeSubmodule = sub;
        this.saveState();
        
    },

    // 导航到某一级
    navigateLevel: function(level) {
        this.state.level = level;
        this.saveState();
        this.renderPanel();
        
    },

    // 关闭面板
    closePanel: function() {
        var container = document.getElementById('engineerPanelContainer');
        if (container) {
            container.style.display = 'none';
            container.innerHTML = '';
        }
        this.state.level = 1;
    },

    // 自动更新
    startAutoUpdate: function() {
        var self = this;
        setInterval(function() {
            // 模拟更新信号状态
            self.signalSources.forEach(function(src) {
                if (Math.random() > 0.9) {
                    src.signal = src.signal === 'bull' ? 'neutral' : 'bull';
                }
            });
            if (self.state.level === 1 || self.state.level === 2) {
                self.renderPanel();
            }
        }, 30000);
    }
};

// Auto-init (panel display disabled on load)
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() { EngineerModule.init(); });
} else {
    EngineerModule.init();
}


// 初始化 - Disabled auto-init
// // Auto-init restored
//     document.addEventListener('DOMContentLoaded', function() { EngineerModule.init(); });
// } else {
//     EngineerModule.init();
// }

// Auto-init (panel display disabled on load)
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() { EngineerModule.init(); });
} else {
    EngineerModule.init();
}
