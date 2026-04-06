// ========== 宏观微观模块 ==========
const MacroMicro = {
    state: {
        level: 1,
        activeTool: null,
        viewMode: 'macro', // macro or micro
        signals: {},
        alerts: []
    },

    // 7工具市场配置
    tools: {
        rabbit: {
            name: '打兔子', icon: '🐰',
            markets: ['Binance', 'Coinbase', 'Kraken', 'OKX', 'Bybit'],
            top5: [
                { symbol: 'BTC', price: 75145, change: 3.62, volume: 28.5e9 },
                { symbol: 'ETH', price: 3215, change: 2.85, volume: 15.2e9 },
                { symbol: 'BNB', price: 598, change: 1.23, volume: 1.8e9 },
                { symbol: 'SOL', price: 178, change: 5.42, volume: 4.5e9 },
                { symbol: 'XRP', price: 0.52, change: -1.2, volume: 2.1e9 }
            ],
            anomalies: [
                { symbol: 'DOGE', change: 12.5, reason: '马斯克推文效应' },
                { symbol: 'PEPE', change: 15.2, reason: 'Meme币热潮' },
                { symbol: 'FLOKI', change: 8.7, reason: '社区驱动' }
            ]
        },
        mole: {
            name: '打地鼠', icon: '🐹',
            markets: ['Binance', 'Bybit', 'OKX', 'Huobi', 'Gate.io'],
            top5: [
                { symbol: 'PEPE', price: 0.000012, change: 12.5, volume: 890e6 },
                { symbol: 'SHIB', price: 0.000025, change: 8.3, volume: 1.2e9 },
                { symbol: 'FLOKI', price: 0.00018, change: 15.2, volume: 456e6 },
                { symbol: 'BONK', price: 0.000028, change: 6.8, volume: 320e6 },
                { symbol: 'WIF', price: 2.45, change: 4.2, volume: 580e6 }
            ],
            anomalies: [
                { symbol: 'PEPE', change: 12.5, reason: '成交量异常放大' },
                { symbol: 'FLOKI', change: 15.2, reason: '波动率飙升' },
                { symbol: 'SHIB', change: 8.3, reason: '鲸鱼买入' }
            ]
        },
        oracle: {
            name: '走着瞧', icon: '🔮',
            markets: ['Polymarket', ' Kalshi', 'Betmgm', 'Draftkings', 'Predictit'],
            top5: [
                { symbol: 'BTC-50K', price: 0.82, change: 5.2, volume: '12M' },
                { symbol: 'ETH-POL', price: 0.65, change: 3.8, volume: '8.5M' },
                { symbol: 'SOL-PRICE', price: 0.55, change: -2.1, volume: '5.2M' },
                { symbol: 'AI-EVENT', price: 0.72, change: 4.5, volume: '3.8M' },
                { symbol: 'FED-RATE', price: 0.48, change: 1.2, volume: '15M' }
            ],
            anomalies: [
                { symbol: 'BTC-50K', change: 5.2, reason: '机构押注上涨' },
                { symbol: 'AI-EVENT', change: 4.5, reason: 'AI板块热度' },
                { symbol: 'ETH-POL', change: 3.8, reason: 'Polymarket流量激增' }
            ]
        },
        leader: {
            name: '跟大哥', icon: '👑',
            markets: ['Bybit', 'Binance', 'Bitget', 'Okx', 'Mexc'],
            top5: [
                { symbol: 'CRV', price: 0.58, change: 4.2, volume: 180e6 },
                { symbol: 'FXS', price: 4.82, change: 3.8, volume: 95e6 },
                { symbol: 'SNX', price: 3.25, change: 2.9, volume: 78e6 },
                { symbol: 'MKR', price: 2850, change: 1.5, volume: 120e6 },
                { symbol: 'AAVE', price: 165, change: 2.1, volume: 220e6 }
            ],
            anomalies: [
                { symbol: 'CRV', change: 4.2, reason: '做市商大量买入' },
                { symbol: 'FXS', change: 3.8, reason: 'KOL推荐' },
                { symbol: 'SNX', change: 2.9, reason: 'DeFi复兴' }
            ]
        },
        hitchhiker: {
            name: '搭便车', icon: '🍀',
            markets: ['Binance', 'Bybit', 'Bitget', 'Zebec', 'Humans'],
            top5: [
                { symbol: 'ZBC', price: 0.12, change: 5.8, volume: 45e6 },
                { symbol: 'HUM', price: 1.85, change: 3.2, volume: 28e6 },
                { symbol: 'PENDLE', price: 3.45, change: 4.5, volume: 62e6 },
                { symbol: 'ETHFI', price: 2.85, change: 2.8, volume: 35e6 },
                { symbol: 'EIGEN', price: 4.20, change: 1.9, volume: 52e6 }
            ],
            anomalies: [
                { symbol: 'ZBC', change: 5.8, reason: '跟单社区爆发' },
                { symbol: 'PENDLE', change: 4.5, reason: '收益聚合热点' },
                { symbol: 'ETHFI', change: 2.8, reason: 'LSD赛道' }
            ]
        },
        airdrop: {
            name: '薅羊毛', icon: '💰',
            markets: ['LayerZero', 'ZkSync', 'Starknet', 'Linea', 'Scroll'],
            top5: [
                { symbol: 'ZK', price: 0.45, change: 5.2, volume: 120e6 },
                { symbol: 'STARK', price: 0.62, change: 3.8, volume: 85e6 },
                { symbol: 'LINEA', price: 1.85, change: 2.5, volume: 45e6 },
                { symbol: 'SCROLL', price: 0.78, change: 1.8, volume: 32e6 },
                { symbol: 'METIS', price: 28.5, change: 4.2, volume: 58e6 }
            ],
            anomalies: [
                { symbol: 'ZK', change: 5.2, reason: '空投预期升温' },
                { symbol: 'STARK', change: 3.8, reason: '主网活跃' },
                { symbol: 'LINEA', change: 2.5, reason: '生态爆发' }
            ]
        },
        crowdsource: {
            name: '穷孩子', icon: '👶',
            markets: ['EvoMap', 'Clickworker', 'Toloka', 'Appen', 'Lionbridge'],
            top5: [
                { symbol: 'AI-TASK', price: 0.15, change: 0, tasks: 15420 },
                { symbol: 'DATA-LABEL', price: 0.08, change: 0, tasks: 28350 },
                { symbol: 'SENTIMENT', price: 0.12, change: 0, tasks: 8950 },
                { symbol: 'TRANSCRIBE', price: 0.05, change: 0, tasks: 32100 },
                { symbol: 'TRANSLATE', price: 0.18, change: 0, tasks: 12800 }
            ],
            anomalies: [
                { symbol: 'AI-TASK', tasks: 15420, reason: 'AI训练需求激增' },
                { symbol: 'DATA-LABEL', tasks: 28350, reason: 'ML数据集' },
                { symbol: 'TRANSCRIBE', tasks: 32100, reason: '语音转写' }
            ]
        }
    },

    // 用户持仓状态
    userStatus: {
        invested: [
            { tool: 'rabbit', symbol: 'BTC', amount: 0.5, value: 37572, status: '盈利', pnl: 1250 },
            { tool: 'rabbit', symbol: 'ETH', amount: 2.0, value: 6430, status: '盈利', pnl: 320 },
            { tool: 'mole', symbol: 'PEPE', amount: 50000000, value: 600, status: '盈利', pnl: 120 },
            { tool: 'oracle', symbol: 'BTC-50K', amount: 100, value: 82, status: '持仓', pnl: 12 }
        ],
        investing: [
            { tool: 'rabbit', symbol: 'SOL', amount: 10, value: 1780, status: '建仓中', pnl: -45 },
            { tool: 'mole', symbol: 'SHIB', amount: 10000000, value: 250, status: '观察', pnl: 0 },
            { tool: 'airdrop', symbol: 'ZK', amount: 500, value: 225, status: '交互中', pnl: 0 }
        ],
        watching: [
            { tool: 'leader', symbol: 'CRV', reason: 'KOL推荐', confidence: 85 },
            { tool: 'hitchhiker', symbol: 'PENDLE', reason: '收益聚合', confidence: 78 },
            { tool: 'rabbit', symbol: 'BNB', reason: '低估', confidence: 72 },
            { tool: 'oracle', symbol: 'ETH-POL', reason: '预测胜率高', confidence: 80 },
            { tool: 'crowdsource', symbol: 'AI-TASK', reason: '高收益任务', confidence: 90 }
        ]
    },

    init: function() {
        this.loadState();
        
        console.log('🌐 MacroMicro initialized');
    },

    loadState: function() {
        try {
            var saved = localStorage.getItem('MacroMicroState');
            if (saved) {
                var data = JSON.parse(saved);
                this.state.level = data.level || 1;
                this.state.activeTool = data.activeTool || null;
                this.state.viewMode = data.viewMode || 'macro';
            }
        } catch(e) {}
    },

    saveState: function() {
        try {
            localStorage.setItem('MacroMicroState', JSON.stringify({
                level: this.state.level,
                activeTool: this.state.activeTool,
                viewMode: this.state.viewMode
            }));
        } catch(e) {}
    },

    renderPanel: function() {
        var container = document.getElementById('macroMicroPanelContainer');
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
        html += '<div><span style="font-size:28px;">🌐</span> <span style="font-size:18px; font-weight:700;">宏观微观</span></div>';
        html += '<button onclick="MacroMicro.closePanel()" style="background:none; border:none; color:#888; font-size:24px; cursor:pointer;">✕</button>';
        html += '</div>';

        html += '<div style="padding:20px;">';

        // 视角切换
        html += '<div style="display:flex; gap:10px; margin-bottom:20px;">';
        html += '<button onclick="MacroMicro.setViewMode(\'macro\')" style="flex:1; padding:12px; background:' + (this.state.viewMode === 'macro' ? 'rgba(0,212,170,0.2)' : 'rgba(0,0,0,0.3)') + '; border:1px solid ' + (this.state.viewMode === 'macro' ? '#00d4aa' : 'rgba(255,255,255,0.1)') + '; color:' + (this.state.viewMode === 'macro' ? '#00d4aa' : '#888') + '; border-radius:8px; cursor:pointer; font-weight:600;">🌐 宏观</button>';
        html += '<button onclick="MacroMicro.setViewMode(\'micro\')" style="flex:1; padding:12px; background:' + (this.state.viewMode === 'micro' ? 'rgba(0,212,170,0.2)' : 'rgba(0,0,0,0.3)') + '; border:1px solid ' + (this.state.viewMode === 'micro' ? '#00d4aa' : 'rgba(255,255,255,0.1)') + '; color:' + (this.state.viewMode === 'micro' ? '#00d4aa' : '#888') + '; border-radius:8px; cursor:pointer; font-weight:600;">🔬 微观</button>';
        html += '</div>';

        // 7工具卡片
        html += '<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:10px; margin-bottom:20px;">';
        var self = this;
        Object.keys(this.tools).forEach(function(key) {
            var tool = self.tools[key];
            html += '<div onclick="MacroMicro.selectTool(\'' + key + '\')" style="background:rgba(0,0,0,0.4); border:1px solid rgba(0,212,170,0.2); border-radius:10px; padding:15px; cursor:pointer; transition:all 0.3s;">';
            html += '<div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">';
            html += '<span style="font-size:24px;">' + tool.icon + '</span>';
            html += '<span style="font-weight:600;">' + tool.name + '</span>';
            html += '</div>';
            html += '<div style="font-size:11px; color:#888;">市场: ' + tool.markets.length + '个</div>';
            html += '<div style="font-size:11px; color:#00d4aa;">Top5 + 异动3</div>';
            html += '</div>';
        });
        html += '</div>';

        // 用户状态概览
        html += '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px;">';
        html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px;">📊 我的持仓</div>';
        html += '<div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px;">';

        var invested = this.userStatus.invested.length;
        var investing = this.userStatus.investing.length;
        var watching = this.userStatus.watching.length;
        var totalValue = this.userStatus.invested.reduce(function(a, b) { return a + b.value; }, 0);

        html += '<div style="text-align:center; padding:12px; background:rgba(0,212,170,0.1); border-radius:8px;">';
        html += '<div style="font-size:20px; font-weight:700; color:#00d4aa;">' + invested + '</div>';
        html += '<div style="font-size:11px; color:#888;">已投</div>';
        html += '</div>';

        html += '<div style="text-align:center; padding:12px; background:rgba(245,158,11,0.1); border-radius:8px;">';
        html += '<div style="font-size:20px; font-weight:700; color:#f59e0b;">' + investing + '</div>';
        html += '<div style="font-size:11px; color:#888;">在投</div>';
        html += '</div>';

        html += '<div style="text-align:center; padding:12px; background:rgba(168,85,247,0.1); border-radius:8px;">';
        html += '<div style="font-size:20px; font-weight:700; color:#a78bfa;">' + watching + '</div>';
        html += '<div style="font-size:11px; color:#888;">关注</div>';
        html += '</div>';

        html += '</div>';
        html += '<div style="margin-top:15px; text-align:center;"><span style="color:#888; font-size:12px;">总市值 </span><span style="color:#00d4aa; font-weight:700; font-size:18px;">$' + totalValue.toLocaleString() + '</span></div>';
        html += '</div>';

        html += '<button onclick="MacroMicro.navigateLevel(2)" style="width:100%; padding:12px; margin-top:20px; background:rgba(0,212,170,0.2); border:1px solid #00d4aa; color:#00d4aa; border-radius:8px; cursor:pointer; font-weight:600;">查看详情 →</button>';
        html += '</div></div></div>';

        return html;
    },

    // Level 2: 详情
    renderLevel2: function() {
        var self = this;
        var html = '<div style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(10,14,23,0.98); z-index:10000; overflow:auto;">';
        html += '<div style="max-width:900px; margin:0 auto; background:rgba(20,25,35,0.98); border:1px solid rgba(0,212,170,0.2); border-radius:15px; margin-top:30px; margin-bottom:30px;">';

        html += '<div style="padding:20px; border-bottom:1px solid rgba(255,255,255,0.1); display:flex; justify-content:space-between; align-items:center;">';
        html += '<div><span style="font-size:28px;">🌐</span> <span style="font-size:18px; font-weight:700;">宏观微观 - 详情</span></div>';
        html += '<button onclick="MacroMicro.closePanel()" style="background:none; border:none; color:#888; font-size:24px; cursor:pointer;">✕</button>';
        html += '</div>';

        html += '<div style="padding:20px;">';
        html += '<button onclick="MacroMicro.navigateLevel(1)" style="padding:8px 15px; background:rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.2); color:#fff; border-radius:8px; cursor:pointer; margin-bottom:15px;">← 返回</button>';

        // 工具选择
        html += '<div style="display:flex; gap:8px; margin-bottom:15px; flex-wrap:wrap;">';
        Object.keys(this.tools).forEach(function(key) {
            var tool = self.tools[key];
            var isActive = self.state.activeTool === key;
            html += '<button onclick="MacroMicro.selectTool(\'' + key + '\')" style="padding:8px 12px; background:' + (isActive ? 'rgba(0,212,170,0.2)' : 'rgba(0,0,0,0.3)') + '; border:1px solid ' + (isActive ? '#00d4aa' : 'rgba(255,255,255,0.1)') + '; color:' + (isActive ? '#00d4aa' : '#888') + '; border-radius:20px; cursor:pointer; font-size:12px;">' + tool.icon + ' ' + tool.name + '</button>';
        });
        html += '</div>';

        if (this.state.activeTool) {
            var tool = this.tools[this.state.activeTool];
            html += this.renderToolMarketDetail(tool);
        } else {
            html += this.renderAllToolsSummary();
        }

        html += '</div></div></div>';
        return html;
    },

    // 工具市场详情
    renderToolMarketDetail: function(tool) {
        var html = '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px; margin-bottom:15px;">';
        html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px;">' + tool.icon + ' ' + tool.name + ' - 市场详情</div>';

        // Top 5
        html += '<div style="margin-bottom:20px;">';
        html += '<div style="font-size:12px; color:#888; margin-bottom:10px;">📈 Top 5 市场</div>';
        html += '<table style="width:100%; font-size:12px;">';
        html += '<thead><tr style="color:#888;"><th style="text-align:left; padding:5px;">标的</th><th style="text-align:right; padding:5px;">价格</th><th style="text-align:right; padding:5px;">24h</th><th style="text-align:right; padding:5px;">成交量</th></tr></thead>';
        html += '<tbody>';
        tool.top5.forEach(function(item) {
            html += '<tr style="border-top:1px solid rgba(255,255,255,0.05);">';
            html += '<td style="padding:8px; font-weight:600;">' + item.symbol + '</td>';
            html += '<td style="text-align:right; color:#00d4aa;">$' + (typeof item.price === 'number' && item.price < 1 ? item.price.toFixed(6) : item.price.toLocaleString()) + '</td>';
            html += '<td style="text-align:right; color:' + (item.change >= 0 ? '#00d4aa' : '#ef4444') + ';">' + (item.change >= 0 ? '+' : '') + item.change + '%</td>';
            html += '<td style="text-align:right; color:#888;">' + (item.volume >= 1e9 ? (item.volume/1e9).toFixed(1) + 'B' : item.volume >= 1e6 ? (item.volume/1e6).toFixed(1) + 'M' : (item.volume/1e3).toFixed(1) + 'K') + '</td>';
            html += '</tr>';
        });
        html += '</tbody></table>';
        html += '</div>';

        // 异动前三
        html += '<div>';
        html += '<div style="font-size:12px; color:#ef4444; margin-bottom:10px;">⚠️ 异动前三</div>';
        html += '<div style="display:grid; gap:8px;">';
        tool.anomalies.forEach(function(item) {
            html += '<div style="display:flex; justify-content:space-between; align-items:center; padding:10px; background:rgba(239,68,68,0.1); border:1px solid rgba(239,68,68,0.3); border-radius:8px;">';
            html += '<div><span style="font-weight:600; color:#ef4444;">' + item.symbol + '</span><span style="color:#888; font-size:11px; margin-left:10px;">' + item.reason + '</span></div>';
            html += '<span style="color:#ef4444; font-weight:600;">' + (item.change >= 0 ? '+' : '') + item.change + '%</span>';
            html += '</div>';
        });
        html += '</div>';
        html += '</div>';

        html += '</div>';
        return html;
    },

    // 所有工具汇总
    renderAllToolsSummary: function() {
        var html = '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px;">';
        html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px;">📊 7工具市场总览</div>';

        var self = this;
        Object.keys(this.tools).forEach(function(key) {
            var tool = self.tools[key];
            var topGainer = tool.top5[0];
            var topAnomaly = tool.anomalies[0];

            html += '<div style="padding:12px; background:rgba(0,0,0,0.3); border-radius:8px; margin-bottom:10px;">';
            html += '<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">';
            html += '<div><span style="font-size:18px; margin-right:8px;">' + tool.icon + '</span><span style="font-weight:600;">' + tool.name + '</span></div>';
            html += '<div style="font-size:11px; color:#888;">覆盖: ' + tool.markets.length + '市场</div>';
            html += '</div>';
            html += '<div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; font-size:11px;">';
            html += '<div style="padding:8px; background:rgba(0,212,170,0.1); border-radius:6px;">';
            html += '<div style="color:#888; margin-bottom:3px;">最强</div>';
            html += '<div style="color:#00d4aa; font-weight:600;">' + topGainer.symbol + ' ' + (topGainer.change >= 0 ? '+' : '') + topGainer.change + '%</div>';
            html += '</div>';
            html += '<div style="padding:8px; background:rgba(239,68,68,0.1); border-radius:6px;">';
            html += '<div style="color:#888; margin-bottom:3px;">异动</div>';
            html += '<div style="color:#ef4444; font-weight:600;">' + topAnomaly.symbol + ' ' + (topAnomaly.change >= 0 ? '+' : '') + topAnomaly.change + '%</div>';
            html += '</div>';
            html += '</div>';
            html += '</div>';
        });

        html += '</div>';
        return html;
    },

    // Level 3: 用户持仓详情
    renderLevel3: function() {
        var html = '<div style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(10,14,23,0.98); z-index:10000; overflow:auto;">';
        html += '<div style="max-width:800px; margin:0 auto; background:rgba(20,25,35,0.98); border:1px solid rgba(0,212,170,0.2); border-radius:15px; margin-top:30px; margin-bottom:30px;">';

        html += '<div style="padding:20px; border-bottom:1px solid rgba(255,255,255,0.1); display:flex; justify-content:space-between; align-items:center;">';
        html += '<div><span style="font-size:28px;">📊</span> <span style="font-size:18px; font-weight:700;">我的持仓</span></div>';
        html += '<button onclick="MacroMicro.closePanel()" style="background:none; border:none; color:#888; font-size:24px; cursor:pointer;">✕</button>';
        html += '</div>';

        html += '<div style="padding:20px;">';
        html += '<button onclick="MacroMicro.navigateLevel(2)" style="padding:8px 15px; background:rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.2); color:#fff; border-radius:8px; cursor:pointer; margin-bottom:15px;">← 返回</button>';

        // 已投
        html += '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px; margin-bottom:15px;">';
        html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px; color:#00d4aa;">✓ 已投 (' + this.userStatus.invested.length + ')</div>';
        var self = this;
        this.userStatus.invested.forEach(function(item) {
            var tool = self.tools[item.tool];
            html += '<div style="display:flex; justify-content:space-between; align-items:center; padding:12px; background:rgba(0,0,0,0.3); border-radius:8px; margin-bottom:8px;">';
            html += '<div><div style="font-weight:600;">' + tool.icon + ' ' + item.symbol + '</div><div style="font-size:11px; color:#888;">' + item.tool + ' | ' + item.status + '</div></div>';
            html += '<div style="text-align:right;"><div style="color:#00d4aa; font-weight:600;">+$' + item.pnl + '</div><div style="font-size:11px; color:#888;">$' + item.value.toLocaleString() + '</div></div>';
            html += '</div>';
        });
        html += '</div>';

        // 在投
        html += '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px; margin-bottom:15px;">';
        html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px; color:#f59e0b;">⏳ 在投 (' + this.userStatus.investing.length + ')</div>';
        this.userStatus.investing.forEach(function(item) {
            var tool = self.tools[item.tool];
            html += '<div style="display:flex; justify-content:space-between; align-items:center; padding:12px; background:rgba(0,0,0,0.3); border-radius:8px; margin-bottom:8px;">';
            html += '<div><div style="font-weight:600;">' + tool.icon + ' ' + item.symbol + '</div><div style="font-size:11px; color:#888;">' + item.tool + ' | ' + item.status + '</div></div>';
            html += '<div style="text-align:right;"><div style="color:' + (item.pnl >= 0 ? '#00d4aa' : '#ef4444') + '; font-weight:600;">' + (item.pnl >= 0 ? '+$' : '-$') + Math.abs(item.pnl) + '</div><div style="font-size:11px; color:#888;">$' + item.value.toLocaleString() + '</div></div>';
            html += '</div>';
        });
        html += '</div>';

        // 关注
        html += '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px;">';
        html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px; color:#a78bfa;">⭐ 关注 (' + this.userStatus.watching.length + ')</div>';
        this.userStatus.watching.forEach(function(item) {
            var tool = self.tools[item.tool];
            html += '<div style="display:flex; justify-content:space-between; align-items:center; padding:12px; background:rgba(0,0,0,0.3); border-radius:8px; margin-bottom:8px;">';
            html += '<div><div style="font-weight:600;">' + tool.icon + ' ' + item.symbol + '</div><div style="font-size:11px; color:#888;">' + item.reason + '</div></div>';
            html += '<div style="text-align:right;"><div style="color:#a78bfa; font-weight:600;">' + item.confidence + '%</div><div style="font-size:11px; color:#888;">置信度</div></div>';
            html += '</div>';
        });
        html += '</div>';

        html += '</div></div></div>';
        return html;
    },

    // Level 4: 操作
    renderLevel4: function() {
        var html = '<div style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(10,14,23,0.98); z-index:10000; overflow:auto;">';
        html += '<div style="max-width:500px; margin:0 auto; background:rgba(20,25,35,0.98); border:1px solid rgba(0,212,170,0.2); border-radius:15px; margin-top:30px;">';

        html += '<div style="padding:20px; border-bottom:1px solid rgba(255,255,255,0.1); display:flex; justify-content:space-between; align-items:center;">';
        html += '<div><span style="font-size:28px;">⚙️</span> <span style="font-size:18px; font-weight:700;">配置</span></div>';
        html += '<button onclick="MacroMicro.closePanel()" style="background:none; border:none; color:#888; font-size:24px; cursor:pointer;">✕</button>';
        html += '</div>';

        html += '<div style="padding:20px;">';
        html += '<button onclick="MacroMicro.navigateLevel(3)" style="padding:8px 15px; background:rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.2); color:#fff; border-radius:8px; cursor:pointer; margin-bottom:15px;">← 返回</button>';

        html += '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px;">';
        html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px;">⚙️ 宏观微观配置</div>';

        html += '<div style="margin-bottom:15px;">';
        html += '<label style="font-size:12px; color:#888; display:block; margin-bottom:5px;">市场数据源</label>';
        html += '<select style="width:100%; padding:10px; background:rgba(0,0,0,0.3); border:1px solid rgba(255,255,255,0.2); border-radius:8px; color:#fff;">';
        html += '<option>Binance (推荐)</option><option>Coinbase</option><option>Bybit</option><option>聚合</option>';
        html += '</select>';
        html += '</div>';

        html += '<div style="margin-bottom:15px;">';
        html += '<label style="font-size:12px; color:#888; display:block; margin-bottom:5px;">异动提醒阈值</label>';
        html += '<input type="range" min="1" max="20" value="5" style="width:100%;">';
        html += '<div style="display:flex; justify-content:space-between; font-size:11px; color:#888;"><span>1%</span><span>5%</span><span>20%</span></div>';
        html += '</div>';

        html += '<div style="margin-bottom:15px;">';
        html += '<label style="font-size:12px; color:#888; display:block; margin-bottom:5px;">刷新间隔</label>';
        html += '<select style="width:100%; padding:10px; background:rgba(0,0,0,0.3); border:1px solid rgba(255,255,255,0.2); border-radius:8px; color:#fff;">';
        html += '<option>实时</option><option>30秒</option><option>1分钟</option><option>5分钟</option>';
        html += '</select>';
        html += '</div>';

        html += '</div>';

        html += '<button onclick="MacroMicro.closePanel()" style="width:100%; padding:15px; margin-top:20px; background:linear-gradient(135deg, #00d4aa, #00a884); color:#000; border:none; border-radius:10px; cursor:pointer; font-weight:700; font-size:16px;">保存配置</button>';
        html += '</div></div></div>';

        return html;
    },

    selectTool: function(toolId) {
        this.state.activeTool = toolId;
        this.saveState();
        
    },

    setViewMode: function(mode) {
        this.state.viewMode = mode;
        this.saveState();
        
    },

    navigateLevel: function(level) {
        this.state.level = level;
        this.saveState();
        this.renderPanel();
        
    },

    closePanel: function() {
        var container = document.getElementById('macroMicroPanelContainer');
        if (container) {
            container.style.display = 'none';
            container.innerHTML = '';
        }
        this.state.level = 1;
        this.state.activeTool = null;
    }
};

// Auto-init (panel display disabled on load)
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() { MacroMicro.init(); });
} else {
    MacroMicro.init();
}


// Init - Disabled auto-init, call MacroMicro.init() manually when needed
// // Auto-init restored
if (document.readyState === 'loading') {
//     document.addEventListener('DOMContentLoaded', function() { MacroMicro.init(); });
// } else {
//     MacroMicro.init();
// }


// Auto-init (panel display disabled on load)
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() { MacroMicro.init(); });
} else {
    MacroMicro.init();
}
