// ==========================================================================
// GO2SE V12 - 交易面板模块 (实时流式)
// ==========================================================================
window.TradingPanel = {
    state: {
        level: 1,
        activeTab: 'live', // live, backtest, paper, simulation
        streams: {},
        history: [],
        isStreaming: false,
        // L5/L6 Analytics
        stats: { today: 5, week: 23, total: 156, successRate: 78 },
        analytics: { totalProfit: 24680, returnRate: 24.7, maxDrawdown: 8.3, sharpeRatio: 1.85, tradeCount: 156, winRate: 67, avgProfit: 158, profitFactor: 1.72 }
    },

    // 7工具配置
    tools: {
        rabbit: { name: '打兔子', icon: '🐰', type: 'invest', status: 'scanning' },
        mole: { name: '打地鼠', icon: '🐹', type: 'invest', status: 'scanning' },
        oracle: { name: '走着瞧', icon: '🔮', type: 'invest', status: 'analyzing' },
        leader: { name: '跟大哥', icon: '👑', type: 'invest', status: 'watching' },
        hitchhiker: { name: '搭便车', icon: '🍀', type: 'invest', status: 'scanning' },
        airdrop: { name: '薅羊毛', icon: '💰', type: 'work', status: 'hunting' },
        crowdsource: { name: '穷孩子', icon: '👶', type: 'work', status: 'working' }
    },

    // 实时数据流
    streams: {
        rabbit: [
            { symbol: 'BTC', price: 75145, change: 3.62, signal: 'EMA金叉', confidence: 92 },
            { symbol: 'ETH', price: 3215, change: 2.85, signal: 'MACD多头', confidence: 88 },
            { symbol: 'SOL', price: 178, change: 5.42, signal: 'RSI超买', confidence: 85 },
            { symbol: 'BNB', price: 598, change: 1.23, signal: '趋势确认', confidence: 82 }
        ],
        mole: [
            { symbol: 'PEPE', price: 0.000012, change: 12.5, signal: '成交量异常', confidence: 75 },
            { symbol: 'SHIB', price: 0.000025, change: 8.3, signal: '布林带突破', confidence: 72 },
            { symbol: 'FLOKI', price: 0.00018, change: 15.2, signal: 'Meme热潮', confidence: 68 }
        ],
        oracle: [
            { symbol: 'BTC-50K', price: 0.82, change: 5.2, signal: 'MiroFish预测', confidence: 78 },
            { symbol: 'ETH-POL', price: 0.65, change: 3.8, signal: '市场共识', confidence: 72 }
        ],
        leader: [
            { symbol: 'CRV', price: 0.58, change: 4.2, signal: 'KOL建仓', confidence: 80 },
            { symbol: 'FXS', price: 4.82, change: 3.8, signal: '做市商买入', confidence: 75 }
        ],
        hitchhiker: [
            { symbol: 'ZBC', price: 0.12, change: 5.8, signal: '跟单社区', confidence: 73 },
            { symbol: 'PENDLE', price: 3.45, change: 4.5, signal: '收益聚合', confidence: 70 }
        ],
        airdrop: [
            { symbol: 'ZK', price: 0.45, change: 5.2, signal: '空投预热', confidence: 82 },
            { symbol: 'STARK', price: 0.62, change: 3.8, signal: '主网活跃', confidence: 78 }
        ],
        crowdsource: [
            { symbol: 'AI-TASK', tasks: 15420, reward: 0.15, signal: 'AI训练', confidence: 90 },
            { symbol: 'DATA-LABEL', tasks: 28350, reward: 0.08, signal: '数据标注', confidence: 85 }
        ]
    },

    // 决策流程
    decisions: [
        { step: '信号检测', status: 'completed', tool: 'rabbit', detail: 'BTC EMA金叉确认' },
        { step: '趋势判断', status: 'completed', tool: 'oracle', detail: 'MiroFish看涨78%' },
        { step: '风控验证', status: 'running', tool: 'brain', detail: '仓位计算中...' },
        { step: '策略匹配', status: 'pending', tool: 'strategy', detail: '等待策略库响应' },
        { step: '执行确认', status: 'pending', tool: 'execute', detail: '待用户确认' }
    ],

    API_BASE: 'http://localhost:8004/api',

    init: function() {
        this.loadState();
        this.fetchSignals();
        console.log('⚡ TradingPanel initialized');
    },

    fetchSignals: function() {
        var self = this;
        // 获取统计信息
        fetch(this.API_BASE + '/stats')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data.data) {
                    self.state.stats = data.data;
                    self.state.lastUpdate = new Date().toLocaleTimeString();
                    console.log('📊 Stats loaded:', data.data);
                }
            })
            .catch(function(e) { console.error('Stats fetch error:', e); });
        
        // 获取信号列表
        fetch(this.API_BASE + '/signals')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data.data) {
                    self.state.signals = data.data;
                    console.log('📡 Signals loaded:', data.data.length);
                    self.renderPanel();
                }
            })
            .catch(function(e) { console.error('Signal fetch error:', e); });
    },

    loadState: function() {
        try {
            var saved = localStorage.getItem('TradingPanelState');
            if (saved) {
                var data = JSON.parse(saved);
                this.state.level = data.level || 1;
                this.state.activeTab = data.activeTab || 'live';
            }
        } catch(e) {}
    },

    saveState: function() {
        try {
            localStorage.setItem('TradingPanelState', JSON.stringify({
                level: this.state.level,
                activeTab: this.state.activeTab
            }));
        } catch(e) {}
    },

    renderPanel: function() {
        var container = document.getElementById('tradingPanelContainer');
        if (!container) return;

        var html = '';
        if (this.state.level === 1) html = this.renderLevel1();
        else if (this.state.level === 2) html = this.renderLevel2();
        else if (this.state.level === 3) html = this.renderLevel3();
        else if (this.state.level === 4) html = this.renderLevel4();
        else if (this.state.level === 5) html = this.renderLevel5();
        else if (this.state.level === 6) html = this.renderLevel6();

        container.innerHTML = html;
        container.style.display = 'block';
    },

    // Level 1: 总览 (根据activeTab显示不同内容)
    renderLevel1: function() {
        var self = this;
        var html = '<div style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(10,14,23,0.98); z-index:10000; overflow:auto;">';
        html += '<div style="max-width:1000px; margin:0 auto; background:rgba(20,25,35,0.98); border:1px solid rgba(124,58,237,0.2); border-radius:15px; margin-top:30px; margin-bottom:30px;">';

        // Header
        var tabNames = { live: '实时流', backtest: '回测交易', paper: '模拟交易', simulation: '回测仿真' };
        html += '<div style="padding:20px; border-bottom:1px solid rgba(255,255,255,0.1); display:flex; justify-content:space-between; align-items:center;">';
        html += '<div><span style="font-size:28px;">⚡</span> <span style="font-size:18px; font-weight:700;">交易面板</span> <span style="font-size:12px; color:#a78bfa; margin-left:10px;">' + (tabNames[this.state.activeTab] || '实时流') + '</span></div>';
        html += '<button onclick="TradingPanel.closePanel()" style="background:none; border:none; color:#888; font-size:24px; cursor:pointer;">✕</button>';
        html += '</div>';

        html += '<div style="padding:20px;">';

        // Tab切换
        html += '<div style="display:flex; gap:8px; margin-bottom:20px;">';
        var tabs = [
            { id: 'live', name: '实时流', icon: '⚡' },
            { id: 'backtest', name: '回测', icon: '📊' },
            { id: 'paper', name: '模拟', icon: '🎮' },
            { id: 'simulation', name: '仿真', icon: '🔮' }
        ];
        tabs.forEach(function(tab) {
            var isActive = self.state.activeTab === tab.id;
            html += '<button onclick="TradingPanel.selectTab(\'' + tab.id + '\')" style="flex:1; padding:10px; background:' + (isActive ? 'rgba(124,58,237,0.2)' : 'rgba(0,0,0,0.3)') + '; border:1px solid ' + (isActive ? '#7c3aed' : 'rgba(255,255,255,0.1)') + '; color:' + (isActive ? '#a78bfa' : '#888') + '; border-radius:8px; cursor:pointer; font-size:12px;">' + tab.icon + ' ' + tab.name + '</button>';
        });
        html += '</div>';

        // 根据activeTab显示不同内容
        if (this.state.activeTab === 'live') {
            html += this.renderLiveContent();
        } else if (this.state.activeTab === 'backtest') {
            html += this.renderBacktestContent();
        } else if (this.state.activeTab === 'paper') {
            html += this.renderPaperContent();
        } else if (this.state.activeTab === 'simulation') {
            html += this.renderSimulationContent();
        }

        html += '</div></div></div>';
        return html;
    },

    // 实时流内容
    renderLiveContent: function() {
        var self = this;
        var html = '';
        
        // 系统状态卡片
        var stats = this.state.stats || {};
        html += '<div style="display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin-bottom:20px;">';
        html += '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:12px; text-align:center;">';
        html += '<div style="font-size:18px; font-weight:700; color:#00d4aa;">' + (stats.total_signals || 0) + '</div>';
        html += '<div style="font-size:11px; color:#888;">总信号</div></div>';
        html += '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:12px; text-align:center;">';
        html += '<div style="font-size:18px; font-weight:700; color:#f59e0b;">' + (stats.executed_signals || 0) + '</div>';
        html += '<div style="font-size:11px; color:#888;">已执行</div></div>';
        html += '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:12px; text-align:center;">';
        html += '<div style="font-size:18px; font-weight:700;">' + (stats.trading_mode || 'dry_run') + '</div>';
        html += '<div style="font-size:11px; color:#888;">交易模式</div></div>';
        html += '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:12px; text-align:center;">';
        html += '<div style="font-size:18px; font-weight:700; color:#a78bfa;">' + (stats.version || 'v7.1') + '</div>';
        html += '<div style="font-size:11px; color:#888;">版本</div></div>';
        html += '</div>';
        
        html += '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px; margin-bottom:20px;">';
        html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px;">📋 决策流程</div>';
        html += '<div style="display:flex; gap:5px; overflow-x:auto; padding-bottom:10px;">';
        this.decisions.forEach(function(d, i) {
            var color = d.status === 'completed' ? '#00d4aa' : d.status === 'running' ? '#f59e0b' : '#666';
            html += '<div style="flex:1; min-width:100px; text-align:center;">';
            html += '<div style="width:30px; height:30px; border-radius:50%; background:' + color + '; color:#000; display:inline-flex; align-items:center; justify-content:center; font-size:14px; margin-bottom:5px;">' + (d.status === 'completed' ? '✓' : d.status === 'running' ? '⟳' : (i+1)) + '</div>';
            html += '<div style="font-size:11px; color:' + color + ';">' + d.step + '</div>';
            html += '</div>';
            if (i < self.decisions.length - 1) html += '<div style="flex:0; color:#666; align-self:center;">→</div>';
        });
        html += '</div></div>';

        html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px;">⚡ 7工具实时流</div>';
        html += '<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:10px; margin-bottom:20px;">';
        
        // 真实信号数据
        var signals = this.state.signals || [];
        var toolSignals = {};
        signals.forEach(function(s) {
            if (!toolSignals[s.strategy]) {
                toolSignals[s.strategy] = [];
            }
            toolSignals[s.strategy].push(s);
        });
        
        Object.keys(this.tools).forEach(function(key) {
            var tool = self.tools[key];
            var toolSignalList = toolSignals[key] || [];
            var topSignal = toolSignalList[0] || {};
            var statusColor = topSignal.signal === 'buy' ? '#00d4aa' : topSignal.signal === 'sell' ? '#ef4444' : topSignal.signal === 'hold' ? '#f59e0b' : '#666';
            html += '<div onclick="TradingPanel.selectTool(\'' + key + '\')" style="background:rgba(0,0,0,0.4); border:1px solid rgba(124,58,237,0.2); border-radius:10px; padding:12px; cursor:pointer; transition:all 0.2s;" onmouseover="this.style.borderColor=\'#7c3aed\'" onmouseout="this.style.borderColor=\'rgba(124,58,237,0.2)\'">';
            html += '<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">';
            html += '<div style="display:flex; align-items:center; gap:8px;"><span style="font-size:20px;">' + tool.icon + '</span><span style="font-weight:600;">' + tool.name + '</span></div>';
            html += '<span style="font-size:10px; padding:2px 6px; background:rgba(0,0,0,0.5); border-radius:10px; color:' + statusColor + ';">' + (topSignal.signal || 'N/A') + '</span>';
            html += '</div>';
            if (topSignal.symbol) {
                html += '<div style="padding:8px; background:rgba(0,0,0,0.3); border-radius:6px;">';
                html += '<div style="display:flex; justify-content:space-between; margin-bottom:5px;"><span style="font-weight:600;">' + topSignal.symbol + '</span><span style="color:' + statusColor + ';">' + topSignal.confidence + '%</span></div>';
                html += '<div style="font-size:11px; color:#888; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">' + (topSignal.reason || '') + '</div>';
                html += '</div>';
            }
            html += '<div style="margin-top:8px; display:flex; align-items:center; gap:4px;">';
            html += '<span style="font-size:10px; color:#666;">' + toolSignalList.length + ' 信号</span>';
            html += '<div style="flex:1; height:4px; background:rgba(0,0,0,0.3); border-radius:2px; margin-left:8px;">';
            var barWidth = Math.min(100, topSignal.confidence || 0);
            html += '<div style="width:' + barWidth + '%; height:100%; background:' + statusColor + '; border-radius:2px;"></div>';
            html += '</div></div>';
        });
        html += '</div>';
        html += '<button onclick="TradingPanel.navigateLevel(2)" style="width:100%; padding:12px; background:rgba(124,58,237,0.2); border:1px solid #7c3aed; color:#a78bfa; border-radius:8px; cursor:pointer; font-weight:600;">查看详情 →</button>';
        return html;
    },

    // 回测交易内容
    renderBacktestContent: function() {
        var html = '';
        html += '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px; margin-bottom:20px;">';
        html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px;">📊 回测交易</div>';
        html += '<div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:15px;">';
        html += '<div style="padding:12px; background:rgba(0,212,170,0.1); border-radius:8px; text-align:center;"><div style="font-size:20px; font-weight:700; color:#00d4aa;">72.3%</div><div style="font-size:11px; color:#888;">组合胜率</div></div>';
        html += '<div style="padding:12px; background:rgba(0,0,0,0.3); border-radius:8px; text-align:center;"><div style="font-size:20px; font-weight:700;">1.85</div><div style="font-size:11px; color:#888;">夏普比率</div></div>';
        html += '</div>';
        html += '<div style="font-size:12px; color:#888; margin-bottom:15px;">策略: EMA交叉 | RSI超卖 | MACD背离 | 布林带</div>';
        html += '<div style="padding:12px; background:rgba(0,0,0,0.3); border-radius:8px; margin-bottom:15px;">';
        html += '<div style="display:flex; justify-content:space-between; margin-bottom:8px;"><span style="color:#888;">回测周期</span><span>2024-01-01 ~ 2026-04-01</span></div>';
        html += '<div style="display:flex; justify-content:space-between; margin-bottom:8px;"><span style="color:#888;">总交易次数</span><span>1,234</span></div>';
        html += '<div style="display:flex; justify-content:space-between;"><span style="color:#888;">盈利交易</span><span style="color:#00d4aa;">892 (72.3%)</span></div>';
        html += '</div>';
        html += '<button onclick="TradingPanel.navigateLevel(2)" style="width:100%; padding:12px; background:rgba(0,212,170,0.2); border:1px solid #00d4aa; color:#00d4aa; border-radius:8px; cursor:pointer; font-weight:600;">开始回测 →</button>';
        return html;
    },

    // 模拟交易内容
    renderPaperContent: function() {
        var html = '';
        html += '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px; margin-bottom:20px;">';
        html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px;">🎮 模拟交易</div>';
        html += '<div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:15px;">';
        html += '<div style="padding:12px; background:rgba(245,158,11,0.1); border-radius:8px; text-align:center;"><div style="font-size:20px; font-weight:700; color:#f59e0b;">+$1,234</div><div style="font-size:11px; color:#888;">模拟收益</div></div>';
        html += '<div style="padding:12px; background:rgba(0,0,0,0.3); border-radius:8px; text-align:center;"><div style="font-size:20px; font-weight:700;">23</div><div style="font-size:11px; color:#888;">持仓数</div></div>';
        html += '</div>';
        html += '<div style="font-size:12px; color:#888; margin-bottom:15px;">状态: <span style="color:#f59e0b;">● 模拟运行中</span></div>';
        html += '<div style="padding:12px; background:rgba(0,0,0,0.3); border-radius:8px; margin-bottom:15px;">';
        html += '<div style="display:flex; justify-content:space-between; margin-bottom:8px;"><span style="color:#888;">模拟资金</span><span>$100,000</span></div>';
        html += '<div style="display:flex; justify-content:space-between;"><span style="color:#888;">可用资金</span><span style="color:#00d4aa;">$45,678</span></div>';
        html += '</div>';
        html += '<button onclick="TradingPanel.navigateLevel(2)" style="width:100%; padding:12px; background:rgba(0,212,170,0.2); border:1px solid #00d4aa; color:#00d4aa; border-radius:8px; cursor:pointer; font-weight:600;">管理持仓 →</button>';
        return html;
    },

    // 回测仿真内容
    renderSimulationContent: function() {
        var html = '';
        html += '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px; margin-bottom:20px;">';
        html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px;">🔮 MiroFish 回测仿真</div>';
        html += '<div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:15px;">';
        html += '<div style="padding:12px; background:rgba(124,58,237,0.1); border-radius:8px; text-align:center;"><div style="font-size:20px; font-weight:700; color:#a78bfa;">87.6%</div><div style="font-size:11px; color:#888;">仿真评分</div></div>';
        html += '<div style="padding:12px; background:rgba(0,0,0,0.3); border-radius:8px; text-align:center;"><div style="font-size:20px; font-weight:700;">1000</div><div style="font-size:11px; color:#888;">智能体</div></div>';
        html += '</div>';
        html += '<div style="font-size:12px; color:#888; margin-bottom:15px;">仿真维度: 投资组合 | 风控规则 | 多样化 | 7工具 | 25维度</div>';
        html += '<div style="padding:12px; background:rgba(0,0,0,0.3); border-radius:8px; margin-bottom:15px;">';
        html += '<div style="font-size:12px; color:#00d4aa; margin-bottom:8px;">✓ 投资组合 (82分)</div>';
        html += '<div style="font-size:12px; color:#00d4aa; margin-bottom:8px;">✓ 风控规则 (85分)</div>';
        html += '<div style="font-size:12px; color:#00d4aa; margin-bottom:8px;">✓ 打兔子 (92分)</div>';
        html += '<div style="font-size:12px; color:#f59e0b;">⟳ 走着瞧 (78分)</div>';
        html += '</div>';
        html += '<button onclick="TradingPanel.navigateLevel(2)" style="width:100%; padding:12px; background:rgba(124,58,237,0.2); border:1px solid #7c3aed; color:#a78bfa; border-radius:8px; cursor:pointer; font-weight:600;">运行新仿真 →</button>';
        return html;
    },

    // Level 2: 工具详情
    renderLevel2: function() {
        var self = this;
        var html = '<div style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(10,14,23,0.98); z-index:10000; overflow:auto;">';
        html += '<div style="max-width:900px; margin:0 auto; background:rgba(20,25,35,0.98); border:1px solid rgba(124,58,237,0.2); border-radius:15px; margin-top:30px; margin-bottom:30px;">';

        html += '<div style="padding:20px; border-bottom:1px solid rgba(255,255,255,0.1); display:flex; justify-content:space-between; align-items:center;">';
        html += '<div><span style="font-size:28px;">⚡</span> <span style="font-size:18px; font-weight:700;">工具详情</span></div>';
        html += '<button onclick="TradingPanel.closePanel()" style="background:none; border:none; color:#888; font-size:24px; cursor:pointer;">✕</button>';
        html += '</div>';

        html += '<div style="padding:20px;">';
        html += '<button onclick="TradingPanel.navigateLevel(1)" style="padding:8px 15px; background:rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.2); color:#fff; border-radius:8px; cursor:pointer; margin-bottom:15px;">← 返回</button>';

        // 工具选择
        html += '<div style="display:flex; gap:8px; margin-bottom:15px; flex-wrap:wrap;">';
        Object.keys(this.tools).forEach(function(key) {
            var tool = self.tools[key];
            var isActive = self.state.activeTool === key;
            html += '<button onclick="TradingPanel.selectTool(\'' + key + '\')" style="padding:8px 12px; background:' + (isActive ? 'rgba(124,58,237,0.2)' : 'rgba(0,0,0,0.3)') + '; border:1px solid ' + (isActive ? '#7c3aed' : 'rgba(255,255,255,0.1)') + '; color:' + (isActive ? '#a78bfa' : '#888') + '; border-radius:20px; cursor:pointer; font-size:12px;">' + tool.icon + ' ' + tool.name + '</button>';
        });
        html += '</div>';

        // 选中工具的详细流
        if (this.state.activeTool) {
            var stream = this.streams[this.state.activeTool] || [];
            html += '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px;">';
            html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px;">📊 ' + this.tools[this.state.activeTool].name + ' 实时流</div>';

            stream.forEach(function(item, i) {
                html += '<div style="padding:12px; background:rgba(0,0,0,0.3); border-radius:8px; margin-bottom:8px; border-left:3px solid ' + (item.confidence >= 80 ? '#00d4aa' : item.confidence >= 60 ? '#f59e0b' : '#ef4444') + ';">';
                html += '<div style="display:flex; justify-content:space-between; margin-bottom:5px;">';
                html += '<div><span style="font-weight:600; font-size:16px;">' + item.symbol + '</span>';
                if (item.price) html += '<span style="color:#888; font-size:12px; margin-left:10px;">$' + (typeof item.price === 'number' && item.price < 1 ? item.price.toFixed(6) : item.price.toLocaleString()) + '</span>';
                html += '</div>';
                html += '<div style="text-align:right;">';
                html += '<span style="color:' + (item.change >= 0 ? '#00d4aa' : '#ef4444') + '; font-weight:600;">' + (item.change >= 0 ? '+' : '') + (item.change || 0) + '%</span>';
                html += '<span style="font-size:10px; color:#888; margin-left:5px;">' + item.confidence + '%</span>';
                html += '</div>';
                html += '</div>';
                html += '<div style="font-size:12px; color:#888;">' + item.signal + '</div>';
                html += '<div style="margin-top:8px; display:flex; align-items:center; gap:5px;">';
                html += '<div style="flex:1; height:4px; background:rgba(255,255,255,0.1); border-radius:2px;"><div style="width:' + item.confidence + '%; height:100%; background:#00d4aa; border-radius:2px;"></div></div>';
                html += '<span style="font-size:10px; color:#00d4aa;">' + item.confidence + '%</span>';
                html += '</div>';
                html += '</div>';
            });

            html += '</div>';
        } else {
            html += '<div style="text-align:center; padding:40px; color:#888;">选择工具查看详情</div>';
        }

        html += '<button onclick="TradingPanel.navigateLevel(3)" style="width:100%; padding:12px; margin-top:20px; background:rgba(124,58,237,0.2); border:1px solid #7c3aed; color:#a78bfa; border-radius:8px; cursor:pointer; font-weight:600;">交易设置 →</button>';
        html += '</div></div></div>';

        return html;
    },

    // Level 3: 交易设置
    renderLevel3: function() {
        var tool = this.state.activeTool ? this.tools[this.state.activeTool] : this.tools.rabbit;
        var stream = this.state.activeTool ? (this.streams[this.state.activeTool] || []) : this.streams.rabbit;
        var topItem = stream[0] || {};

        var html = '<div style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(10,14,23,0.98); z-index:10000; overflow:auto;">';
        html += '<div style="max-width:500px; margin:0 auto; background:rgba(20,25,35,0.98); border:1px solid rgba(124,58,237,0.2); border-radius:15px; margin-top:30px;">';

        html += '<div style="padding:20px; border-bottom:1px solid rgba(255,255,255,0.1); display:flex; justify-content:space-between; align-items:center;">';
        html += '<div><span style="font-size:28px;">⚡</span> <span style="font-size:18px; font-weight:700;">交易确认</span></div>';
        html += '<button onclick="TradingPanel.closePanel()" style="background:none; border:none; color:#888; font-size:24px; cursor:pointer;">✕</button>';
        html += '</div>';

        html += '<div style="padding:20px;">';
        html += '<button onclick="TradingPanel.navigateLevel(2)" style="padding:8px 15px; background:rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.2); color:#fff; border-radius:8px; cursor:pointer; margin-bottom:15px;">← 返回</button>';

        // 确认信息
        html += '<div style="background:rgba(239,68,68,0.1); border:2px solid rgba(239,68,68,0.3); border-radius:10px; padding:15px; margin-bottom:20px;">';
        html += '<div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;"><span style="font-size:24px;">⚠️</span><div style="font-weight:600; color:#ef4444;">请确认交易</div></div>';
        html += '<div style="font-size:12px; color:#888;">交易对: <span style="color:#fff;">' + (topItem.symbol || 'BTC') + '</span></div>';
        html += '</div>';

        // 参数
        html += '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px; margin-bottom:15px;">';
        html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px;">⚙️ 交易参数</div>';

        html += '<div style="margin-bottom:12px;">';
        html += '<label style="font-size:12px; color:#888; display:block; margin-bottom:5px;">仓位 (%)</label>';
        html += '<input type="number" value="' + tool.position + '" style="width:100%; padding:10px; background:rgba(0,0,0,0.3); border:1px solid rgba(255,255,255,0.2); border-radius:6px; color:#fff; font-size:16px;">';
        html += '</div>';

        html += '<div style="margin-bottom:12px;">';
        html += '<label style="font-size:12px; color:#888; display:block; margin-bottom:5px;">止损 (%)</label>';
        html += '<input type="number" value="' + tool.stopLoss + '" style="width:100%; padding:10px; background:rgba(0,0,0,0.3); border:1px solid rgba(255,255,255,0.2); border-radius:6px; color:#fff; font-size:16px;">';
        html += '</div>';

        html += '<div style="margin-bottom:12px;">';
        html += '<label style="font-size:12px; color:#888; display:block; margin-bottom:5px;">止盈 (%)</label>';
        html += '<input type="number" value="' + tool.takeProfit + '" style="width:100%; padding:10px; background:rgba(0,0,0,0.3); border:1px solid rgba(255,255,255,0.2); border-radius:6px; color:#fff; font-size:16px;">';
        html += '</div>';

        html += '</div>';

        html += '<div style="display:flex; gap:10px;">';
        html += '<button onclick="TradingPanel.navigateLevel(2)" style="flex:1; padding:12px; background:rgba(255,255,255,0.1); color:#fff; border:1px solid rgba(255,255,255,0.2); border-radius:8px; cursor:pointer;">取消</button>';
        html += '<button onclick="TradingPanel.navigateLevel(4)" style="flex:1; padding:12px; background:linear-gradient(135deg, #ef4444, #dc2626); color:#fff; border:none; border-radius:8px; cursor:pointer; font-weight:700;">⚡ 执行</button>';
        html += '</div>';
        html += '</div></div></div>';

        return html;
    },

    // Level 4: 执行结果
    renderLevel4: function() {
        var stream = this.state.activeTool ? (this.streams[this.state.activeTool] || []) : this.streams.rabbit;
        var topItem = stream[0] || {};

        var html = '<div style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(10,14,23,0.98); z-index:10000; overflow:auto;">';
        html += '<div style="max-width:500px; margin:0 auto; background:rgba(20,25,35,0.98); border:1px solid rgba(0,212,170,0.2); border-radius:15px; margin-top:30px;">';

        html += '<div style="padding:20px; border-bottom:1px solid rgba(255,255,255,0.1); display:flex; justify-content:space-between; align-items:center;">';
        html += '<div><span style="font-size:28px;">✅</span> <span style="font-size:18px; font-weight:700;">执行成功</span></div>';
        html += '<button onclick="TradingPanel.closePanel()" style="background:none; border:none; color:#888; font-size:24px; cursor:pointer;">✕</button>';
        html += '</div>';

        html += '<div style="padding:20px; text-align:center;">';
        html += '<div style="font-size:64px; margin-bottom:20px;">✅</div>';
        html += '<div style="font-size:24px; font-weight:700; color:#00d4aa; margin-bottom:10px;">交易执行成功</div>';
        html += '<div style="color:#888; margin-bottom:20px;">订单号: TX' + Date.now().toString().slice(-8) + '</div>';
        html += '</div>';

        html += '<div style="padding:0 20px 20px;">';
        html += '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px; margin-bottom:15px;">';
        html += '<div style="display:flex; justify-content:space-between; margin-bottom:8px;"><span style="color:#888;">交易对</span><span style="font-weight:600;">' + (topItem.symbol || 'BTC') + '</span></div>';
        html += '<div style="display:flex; justify-content:space-between; margin-bottom:8px;"><span style="color:#888;">执行价格</span><span>$' + (topItem.price ? (typeof topItem.price === 'number' && topItem.price < 1 ? topItem.price.toFixed(6) : topItem.price.toLocaleString()) : '-') + '</span></div>';
        html += '<div style="display:flex; justify-content:space-between; margin-bottom:8px;"><span style="color:#888;">状态</span><span style="color:#00d4aa;">已完成</span></div>';
        html += '</div>';

        html += '<button onclick="TradingPanel.closePanel()" style="width:100%; padding:15px; background:linear-gradient(135deg, #00d4aa, #00a884); color:#000; border:none; border-radius:10px; cursor:pointer; font-weight:700; font-size:16px;">完成</button>';
        html += '</div></div></div>';

        return html;
    },

    selectTab: function(tab) {
        this.state.activeTab = tab;
        this.saveState();
        
    },

    selectTool: function(toolId) {
        this.state.activeTool = toolId;
        this.saveState();
        
    },

    navigateLevel: function(level) {
        this.state.level = level;
        this.saveState();
        this.renderPanel();
    },

    startStreaming: function() {
        var self = this;
        setInterval(function() {
            // 模拟实时数据更新
            Object.keys(self.streams).forEach(function(key) {
                self.streams[key].forEach(function(item) {
                    if (Math.random() > 0.7) {
                        item.change = parseFloat((item.change + (Math.random() - 0.5) * 0.5).toFixed(2));
                        item.confidence = Math.min(100, Math.max(50, item.confidence + Math.floor(Math.random() * 5 - 2)));
                    }
                });
            });
            if (self.state.level === 1 || self.state.level === 2) {
                self.renderPanel();
            }
        }, 3000);
    },

    navigateToLevel: function(level) {
        this.state.level = level || 1;
        this.renderPanel();
    },

    closePanel: function() {
        var container = document.getElementById('tradingPanelContainer');
        if (container) {
            container.style.display = 'none';
            container.innerHTML = '';
        }
        this.state.level = 1;
        this.state.activeTool = null;
    },

    // Level 5: 历史记录
    renderLevel5: function() {
        var stats = this.state.stats || { today: 0, week: 0, total: 0, successRate: 0 };
        var history = this.state.history || [];
        
        var html = '<div style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(10,14,23,0.98); z-index:10000; overflow:auto;">';
        html += '<div style="max-width:800px; margin:0 auto; background:rgba(20,25,35,0.98); border:1px solid rgba(59,130,246,0.3); border-radius:15px; margin-top:30px; margin-bottom:30px;">';
        
        html += '<div style="padding:20px; border-bottom:1px solid rgba(255,255,255,0.1);">';
        html += '<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">';
        html += '<div><span style="font-size:28px;">📜</span> <span style="font-size:18px; font-weight:700;">交易历史</span> <span style="font-size:12px; color:#3b82f6; margin-left:10px;">● L5</span></div>';
        html += '<button onclick="TradingPanel.closePanel()" style="background:none; border:none; color:#888; font-size:24px; cursor:pointer;">✕</button>';
        html += '</div>';
        html += '<div style="display:flex; gap:8px;">';
        [1,2,3,4,5,6].forEach(function(lv) {
            var labels = {1:'总览',2:'详情',3:'设置',4:'执行',5:'历史',6:'分析'};
            var colors = {1:'#00d4aa',2:'#7c3aed',3:'#f59e0b',4:'#ef4444',5:'#3b82f6',6:'#ec4899'};
            var icons = {1:'📊',2:'🔍',3:'⚙️',4:'▶️',5:'📜',6:'📈'};
            var isActive = TradingPanel.state.level === lv;
            html += '<button onclick="TradingPanel.navigateLevel(' + lv + ')" style="padding:6px 12px; background:' + (isActive ? colors[lv] : 'rgba(255,255,255,0.1)') + '; color:' + (isActive ? '#000' : '#fff') + '; border:none; border-radius:6px; cursor:pointer; font-size:12px;">' + icons[lv] + ' ' + labels[lv] + '</button>';
        });
        html += '</div></div>';
        
        html += '<div style="padding:20px;">';
        html += '<div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:12px; margin-bottom:20px;">';
        html += '<div style="background:rgba(0,0,0,0.3); border-radius:8px; padding:15px; text-align:center;"><div style="font-size:11px; color:#888; margin-bottom:5px;">今日</div><div style="font-size:24px; font-weight:700; color:#3b82f6;">' + stats.today + '</div></div>';
        html += '<div style="background:rgba(0,0,0,0.3); border-radius:8px; padding:15px; text-align:center;"><div style="font-size:11px; color:#888; margin-bottom:5px;">本周</div><div style="font-size:24px; font-weight:700; color:#3b82f6;">' + stats.week + '</div></div>';
        html += '<div style="background:rgba(0,0,0,0.3); border-radius:8px; padding:15px; text-align:center;"><div style="font-size:11px; color:#888; margin-bottom:5px;">总交易</div><div style="font-size:24px; font-weight:700; color:#3b82f6;">' + stats.total + '</div></div>';
        html += '<div style="background:rgba(0,0,0,0.3); border-radius:8px; padding:15px; text-align:center;"><div style="font-size:11px; color:#888; margin-bottom:5px;">成功率</div><div style="font-size:24px; font-weight:700; color:#00d4aa;">' + stats.successRate + '%</div></div>';
        html += '</div>';
        
        html += '<div style="background:rgba(0,0,0,0.3); border-radius:10px; padding:15px;">';
        html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px;">📜 最近交易</div>';
        if (history.length === 0) {
            html += '<div style="text-align:center; padding:40px; color:#888;">暂无交易记录</div>';
        } else {
            history.slice(0, 15).forEach(function(h) {
                html += '<div style="display:flex; justify-content:space-between; padding:12px; border-bottom:1px solid rgba(255,255,255,0.1);">';
                html += '<div><span style="color:' + (h.profit > 0 ? '#00d4aa' : '#ef4444') + '; margin-right:8px;">' + (h.profit > 0 ? '📈' : '📉') + '</span>' + h.symbol + '</div>';
                html += '<div style="color:' + (h.profit > 0 ? '#00d4aa' : '#ef4444') + ';">' + (h.profit > 0 ? '+' : '') + h.profit + '%</div>';
                html += '</div>';
            });
        }
        html += '</div></div></div></div>';
        return html;
    },

    // Level 6: 数据分析
    renderLevel6: function() {
        var a = this.state.analytics || { totalProfit: 0, returnRate: 0, maxDrawdown: 0, sharpeRatio: 0, tradeCount: 0, winRate: 0, avgProfit: 0, profitFactor: 0 };
        
        var html = '<div style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(10,14,23,0.98); z-index:10000; overflow:auto;">';
        html += '<div style="max-width:800px; margin:0 auto; background:rgba(20,25,35,0.98); border:1px solid rgba(236,72,153,0.3); border-radius:15px; margin-top:30px; margin-bottom:30px;">';
        
        html += '<div style="padding:20px; border-bottom:1px solid rgba(255,255,255,0.1);">';
        html += '<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">';
        html += '<div><span style="font-size:28px;">📈</span> <span style="font-size:18px; font-weight:700;">交易分析</span> <span style="font-size:12px; color:#ec4899; margin-left:10px;">● L6</span></div>';
        html += '<button onclick="TradingPanel.closePanel()" style="background:none; border:none; color:#888; font-size:24px; cursor:pointer;">✕</button>';
        html += '</div>';
        html += '<div style="display:flex; gap:8px;">';
        [1,2,3,4,5,6].forEach(function(lv) {
            var labels = {1:'总览',2:'详情',3:'设置',4:'执行',5:'历史',6:'分析'};
            var colors = {1:'#00d4aa',2:'#7c3aed',3:'#f59e0b',4:'#ef4444',5:'#3b82f6',6:'#ec4899'};
            var icons = {1:'📊',2:'🔍',3:'⚙️',4:'▶️',5:'📜',6:'📈'};
            var isActive = TradingPanel.state.level === lv;
            html += '<button onclick="TradingPanel.navigateLevel(' + lv + ')" style="padding:6px 12px; background:' + (isActive ? colors[lv] : 'rgba(255,255,255,0.1)') + '; color:' + (isActive ? '#000' : '#fff') + '; border:none; border-radius:6px; cursor:pointer; font-size:12px;">' + icons[lv] + ' ' + labels[lv] + '</button>';
        });
        html += '</div></div>';
        
        html += '<div style="padding:20px;">';
        html += '<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(140px, 1fr)); gap:12px; margin-bottom:20px;">';
        html += '<div style="background:linear-gradient(135deg, rgba(0,212,170,0.2), rgba(0,0,0,0.3)); border-radius:10px; padding:16px;"><div style="font-size:11px; color:#888; margin-bottom:5px;">总收益</div><div style="font-size:22px; font-weight:700; color:#00d4aa;">+$' + a.totalProfit.toLocaleString() + '</div></div>';
        html += '<div style="background:linear-gradient(135deg, rgba(124,58,237,0.2), rgba(0,0,0,0.3)); border-radius:10px; padding:16px;"><div style="font-size:11px; color:#888; margin-bottom:5px;">收益率</div><div style="font-size:22px; font-weight:700; color:#7c3aed;">' + a.returnRate + '%</div></div>';
        html += '<div style="background:linear-gradient(135deg, rgba(239,68,68,0.2), rgba(0,0,0,0.3)); border-radius:10px; padding:16px;"><div style="font-size:11px; color:#888; margin-bottom:5px;">最大回撤</div><div style="font-size:22px; font-weight:700; color:#ef4444;">-' + a.maxDrawdown + '%</div></div>';
        html += '<div style="background:linear-gradient(135deg, rgba(245,158,11,0.2), rgba(0,0,0,0.3)); border-radius:10px; padding:16px;"><div style="font-size:11px; color:#888; margin-bottom:5px;">夏普比率</div><div style="font-size:22px; font-weight:700; color:#f59e0b;">' + a.sharpeRatio + '</div></div>';
        html += '</div>';
        
        html += '<div style="background:rgba(0,0,0,0.3); border-radius:10px; padding:20px; margin-bottom:15px;">';
        html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px;">📊 收益曲线</div>';
        html += '<div style="height:150px; display:flex; align-items:center; justify-content:center; color:#888; background:rgba(0,0,0,0.2); border-radius:8px;"><div style="text-align:center;"><div style="font-size:40px; margin-bottom:10px;">📈</div><div>Chart.js / ECharts</div></div></div>';
        html += '</div>';
        
        html += '<div style="background:rgba(0,0,0,0.3); border-radius:10px; padding:20px;">';
        html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px;">📈 交易统计</div>';
        html += '<div style="display:grid; grid-template-columns:1fr 1fr; gap:15px;">';
        html += '<div style="display:flex; justify-content:space-between; padding:10px; background:rgba(0,0,0,0.2); border-radius:6px;"><span style="color:#888;">交易次数</span><span style="font-weight:600;">' + a.tradeCount + '</span></div>';
        html += '<div style="display:flex; justify-content:space-between; padding:10px; background:rgba(0,0,0,0.2); border-radius:6px;"><span style="color:#888;">胜率</span><span style="font-weight:600; color:#00d4aa;">' + a.winRate + '%</span></div>';
        html += '<div style="display:flex; justify-content:space-between; padding:10px; background:rgba(0,0,0,0.2); border-radius:6px;"><span style="color:#888;">平均收益</span><span style="font-weight:600;">$' + a.avgProfit.toLocaleString() + '</span></div>';
        html += '<div style="display:flex; justify-content:space-between; padding:10px; background:rgba(0,0,0,0.2); border-radius:6px;"><span style="color:#888;">盈亏比</span><span style="font-weight:600;">' + a.profitFactor + '</span></div>';
        html += '</div></div>';
        
        html += '</div></div></div>';
        return html;
    }
};

// Auto-init (panel display disabled on load)
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() { TradingPanel.init(); });
} else {
    TradingPanel.init();
}


// Init - Disabled auto-init
// // Auto-init restored
//     document.addEventListener('DOMContentLoaded', function() { TradingPanel.init(); });
// } else {
//     TradingPanel.init();
// }


// Auto-init (panel display disabled on load)
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() { TradingPanel.init(); });
} else {
    TradingPanel.init();
}

// TradingModules wrapper for compatibility with HTML
window.TradingModules = window.TradingPanel;
