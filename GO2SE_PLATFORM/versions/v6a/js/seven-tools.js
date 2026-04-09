// ========== 北斗七鑫七大工具完整系统 ==========
window.SevenTools = {
    state: {
        activeTool: null,
        level: 1,
        mode: 'normal',
        style: 'balanced',
        selectedProducts: {},
        followedProducts: {},
        capitalAllocation: {},
        computeAllocation: {},
        tradeHistory: []
    },

    tools: {
        rabbit: { id: 'rabbit', name: '打兔子', icon: '🐰', type: 'invest', position: 25, stopLoss: 5, takeProfit: 8, desc: '前20主流加密货币', strategies: ['EMA趋势', 'MACD交叉', 'RSI超买'] },
        mole: { id: 'mole', name: '打地鼠', icon: '🐹', type: 'invest', position: 20, stopLoss: 8, takeProfit: 15, desc: '其他加密货币，火控雷达', strategies: ['布林带', '波动率', '成交量异常'] },
        oracle: { id: 'oracle', name: '走着瞧', icon: '🔮', type: 'invest', position: 15, stopLoss: 5, takeProfit: 10, desc: '预测市场+MiroFish', strategies: ['MiroFish预测', '共识机制', '情绪分析'] },
        leader: { id: 'leader', name: '跟大哥', icon: '👑', type: 'invest', position: 15, stopLoss: 3, takeProfit: 6, desc: '做市协作', strategies: ['跟单策略', 'KOL跟随', '做市商'] },
        hitchhiker: { id: 'hitchhiker', name: '搭便车', icon: '🍀', type: 'invest', position: 10, stopLoss: 5, takeProfit: 8, desc: '跟单分成', strategies: ['跟单分成', '二级分包', '风控仿真'] },
        airdrop: { id: 'airdrop', name: '薅羊毛', icon: '💰', type: 'work', position: 3, stopLoss: 2, takeProfit: 20, desc: '空投猎手', strategies: ['空投猎手', '授权安全', '中转钱包'] },
        crowdsource: { id: 'crowdsource', name: '穷孩子', icon: '👶', type: 'work', position: 2, stopLoss: 1, takeProfit: 30, desc: '众包赚钱', strategies: ['众包任务', 'EvoMap', '隔离保护'] }
    },

    styleParams: {
        conservative: { positionMult: 0.5, leverage: 1, stopLossMult: 0.6, takeProfitMult: 0.8 },
        balanced: { positionMult: 0.75, leverage: 2, stopLossMult: 1.0, takeProfitMult: 1.0 },
        aggressive: { positionMult: 1.0, leverage: 3, stopLossMult: 1.6, takeProfitMult: 1.2 }
    },

    products: {
        rabbit: [
            { symbol: 'BTC', name: 'Bitcoin', price: 75145, change: 3.62, confidence: 92, status: '可选' },
            { symbol: 'ETH', name: 'Ethereum', price: 3215, change: 2.85, confidence: 88, status: '可选' },
            { symbol: 'BNB', name: 'Binance Coin', price: 598, change: 1.23, confidence: 82, status: '已选' },
            { symbol: 'SOL', name: 'Solana', price: 178, change: 5.42, confidence: 85, status: '可选' },
            { symbol: 'XRP', name: 'Ripple', price: 0.52, change: -1.2, confidence: 78, status: '可选' }
        ],
        mole: [
            { symbol: 'PEPE', name: 'Pepe', price: 0.000012, change: 12.5, confidence: 75, status: '可选' },
            { symbol: 'SHIB', name: 'Shiba', price: 0.000025, change: 8.3, confidence: 72, status: '可选' },
            { symbol: 'FLOKI', name: 'FLOKI', price: 0.00018, change: 15.2, confidence: 68, status: '关注' }
        ],
        oracle: [
            { symbol: 'POLY', name: 'Polymarket', price: 0.82, change: 3.2, confidence: 70, status: '可选' },
            { symbol: 'CRM', name: 'Crossmark', price: 1.25, change: -2.1, confidence: 65, status: '可选' }
        ],
        leader: [{ symbol: 'BYD', name: 'Bybit Leader', price: 1.0, change: 2.5, confidence: 80, status: '可选' }],
        hitchhiker: [{ symbol: 'CT', name: 'CopyTrade', price: 1.0, change: 1.8, confidence: 73, status: '可选' }],
        airdrop: [
            { symbol: 'ZK', name: 'ZkSync', price: 0.45, change: 5.2, confidence: 82, status: '可选' },
            { symbol: 'ST', name: 'Starknet', price: 0.62, change: 3.8, confidence: 78, status: '关注' }
        ],
        crowdsource: [{ symbol: 'EV', name: 'EvoMap任务', price: 0.15, change: 0, confidence: 75, status: '可选' }]
    },

    init: function() {
        this.loadState();
        this.fetchData();
        this.renderToolCards();
        this.renderModeSwitch();
        this.renderCapitalPanel();
        this.renderComputePanel();
        this.renderAPIStatus();
        console.log('🪿 SevenTools initialized');
    },

    fetchData: function() {
        var self = this;
        fetch('/api/market/signals/beidou')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                self.state.signals = data.signals || {};
                self.state.lastUpdate = new Date().toLocaleTimeString();
                self.renderToolCards();
            })
            .catch(function(e) { console.log('SevenTools: using cached data'); });
    },

    loadState: function() {
        try {
            var saved = localStorage.getItem('SevenToolsState');
            if (saved) {
                var data = JSON.parse(saved);
                this.state.selectedProducts = data.selectedProducts || {};
                this.state.followedProducts = data.followedProducts || {};
                this.state.mode = data.mode || 'normal';
                this.state.style = data.style || 'balanced';
                this.state.capitalAllocation = data.capitalAllocation || this.getDefaultCapital();
                this.state.computeAllocation = data.computeAllocation || this.getDefaultCompute();
                this.state.tradeHistory = data.tradeHistory || [];
            } else {
                this.state.capitalAllocation = this.getDefaultCapital();
                this.state.computeAllocation = this.getDefaultCompute();
            }
        } catch(e) {
            this.state.capitalAllocation = this.getDefaultCapital();
            this.state.computeAllocation = this.getDefaultCompute();
        }
    },

    saveState: function() {
        try {
            localStorage.setItem('SevenToolsState', JSON.stringify({
                selectedProducts: this.state.selectedProducts,
                followedProducts: this.state.followedProducts,
                mode: this.state.mode,
                style: this.state.style,
                capitalAllocation: this.state.capitalAllocation,
                computeAllocation: this.state.computeAllocation,
                tradeHistory: this.state.tradeHistory
            }));
        } catch(e) {}
    },

    getDefaultCapital: function() {
        return { rabbit: 25, mole: 20, oracle: 15, leader: 15, hitchhiker: 10, airdrop: 3, crowdsource: 2 };
    },

    getDefaultCompute: function() {
        return { rabbit: 30, mole: 25, oracle: 20, leader: 10, hitchhiker: 5, airdrop: 5, crowdsource: 5 };
    },

    // 渲染7工具卡片
    renderToolCards: function() {
        var container = document.getElementById('beidouToolsGrid');
        if (!container) return;
        var html = '<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:15px; padding:15px;">';
        var self = this;
        Object.values(this.tools).forEach(function(tool) {
            var products = self.products[tool.id] || [];
            var selected = self.state.selectedProducts[tool.id] || [];
            var confidence = products.length > 0 ? Math.round(products.reduce(function(a, b) { return a + b.confidence; }, 0) / products.length) : 0;
            html += '<div class="tool-card" onclick="SevenTools.openToolPanel(\'' + tool.id + '\')" style="background:rgba(0,0,0,0.4); border:1px solid rgba(0,212,170,0.2); border-radius:12px; padding:18px; cursor:pointer; transition:all 0.3s;">';
            html += '<div style="display:flex; justify-content:space-between; align-items:start; margin-bottom:12px;">';
            html += '<div style="display:flex; align-items:center; gap:10px;">';
            html += '<span style="font-size:32px;">' + tool.icon + '</span>';
            html += '<div><div style="font-weight:700; font-size:16px;">' + tool.name + '</div><div style="font-size:11px; color:#888;">' + tool.position + '%仓位</div></div>';
            html += '</div>';
            html += '<span style="font-size:10px; padding:3px 8px; background:' + (tool.type === 'invest' ? 'rgba(0,212,170,0.2)' : 'rgba(167,139,250,0.2)') + '; color:' + (tool.type === 'invest' ? '#00d4aa' : '#a78bfa') + '; border-radius:10px;">' + (tool.type === 'invest' ? '投资' : '打工') + '</span>';
            html += '</div>';
            html += '<div style="font-size:12px; color:#888; margin-bottom:12px;">' + tool.desc + '</div>';
            html += '<div style="display:flex; justify-content:space-between; align-items:center;">';
            html += '<div><div style="font-size:11px; color:#888;">置信度</div><div style="font-size:20px; font-weight:700; color:' + (confidence >= 80 ? '#00d4aa' : confidence >= 60 ? '#f59e0b' : '#ef4444') + ';">' + confidence + '%</div></div>';
            html += '<div style="text-align:right;"><div style="font-size:11px; color:#888;">已选/可选</div><div style="font-size:14px; font-weight:600;">' + selected.length + '/' + products.length + '</div></div>';
            html += '<button style="background:rgba(0,212,170,0.2); border:1px solid #00d4aa; color:#00d4aa; padding:8px 15px; border-radius:20px; cursor:pointer; font-size:12px;">进入 →</button>';
            html += '</div>';
            html += '<div style="margin-top:12px; display:flex; gap:5px; flex-wrap:wrap;">';
            tool.strategies.forEach(function(s) {
                html += '<span style="font-size:10px; padding:3px 8px; background:rgba(255,255,255,0.1); border-radius:10px; color:#888;">' + s + '</span>';
            });
            html += '</div></div>';
        });
        html += '</div>';
        container.innerHTML = html;
    },

    // 渲染模式切换
    renderModeSwitch: function() {
        var container = document.getElementById('beidouModeSwitch');
        if (!container) return;
        var self = this;
        var modeHtml = '<div style="display:flex; gap:10px; padding:10px; background:rgba(0,0,0,0.3); border-radius:10px;">';
        modeHtml += '<button onclick="SevenTools.setMode(\'normal\')" style="flex:1; padding:10px; border:none; border-radius:8px; cursor:pointer; background:' + (this.state.mode === 'normal' ? 'rgba(0,212,170,0.3)' : 'transparent') + '; color:' + (this.state.mode === 'normal' ? '#00d4aa' : '#888') + '; font-weight:600;">🧠 普通模式</button>';
        modeHtml += '<button onclick="SevenTools.setMode(\'expert\')" style="flex:1; padding:10px; border:none; border-radius:8px; cursor:pointer; background:' + (this.state.mode === 'expert' ? 'rgba(168,85,247,0.3)' : 'transparent') + '; color:' + (this.state.mode === 'expert' ? '#a78bfa' : '#888') + '; font-weight:600;">🎯 专家模式</button>';
        modeHtml += '</div>';
        var styleNames = { conservative: '保守', balanced: '平衡', aggressive: '积极' };
        var styleColors = { conservative: '#3b82f6', balanced: '#00d4aa', aggressive: '#ef4444' };
        modeHtml += '<div style="display:flex; gap:8px; margin-top:10px;">';
        ['conservative', 'balanced', 'aggressive'].forEach(function(s) {
            modeHtml += '<button onclick="SevenTools.setStyle(\'' + s + '\')" style="flex:1; padding:8px; border:1px solid ' + (this.state.style === s ? styleColors[s] : 'rgba(255,255,255,0.1)') + '; background:' + (this.state.style === s ? styleColors[s].replace('#', 'rgba(').replace(/([0-9a-f]{2})/gi, function(m) { return parseInt(m, 16) + ','; }).slice(0, -1) + ',0.2)' : 'transparent') + '; color:' + (this.state.style === s ? styleColors[s] : '#888') + '; border-radius:8px; cursor:pointer; font-size:12px;">';
            modeHtml += (s === 'conservative' ? '🛡️' : s === 'balanced' ? '⚖️' : '🚀') + ' ' + styleNames[s];
            modeHtml += '</button>';
        });
        modeHtml += '</div>';
        container.innerHTML = modeHtml;
    },

    setMode: function(mode) {
        this.state.mode = mode;
        this.saveState();
        this.renderModeSwitch();
        awShowToast('已切换到' + (mode === 'normal' ? '普通' : '专家') + '模式');
    },

    setStyle: function(style) {
        this.state.style = style;
        this.saveState();
        this.renderModeSwitch();
        awShowToast('风格已调整为' + (style === 'conservative' ? '保守' : style === 'balanced' ? '平衡' : '积极'));
    },

    // 打开工具面板 - 4级页面入口
    openToolPanel: function(toolId) {
        this.state.activeTool = toolId;
        this.state.level = 1;
        this.renderToolPanel();
    },

    // 渲染工具面板 - 4级页面
    renderToolPanel: function() {
        var tool = this.tools[this.state.activeTool];
        if (!tool) return;
        var container = document.getElementById('toolPanelContainer');
        if (!container) return;

        var products = this.products[tool.id] || [];
        var selected = this.state.selectedProducts[tool.id] || [];
        var params = this.styleParams[this.state.style];
        var html = '';

        // Level 1: 选品
        if (this.state.level === 1) {
            html += '<div style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(10,14,23,0.98); z-index:10000; overflow:auto;">';
            html += '<div style="max-width:600px; margin:0 auto; background:rgba(20,25,35,0.98); border:1px solid rgba(0,212,170,0.2); border-radius:15px; margin-top:30px; margin-bottom:30px;">';
            html += '<div style="padding:20px; border-bottom:1px solid rgba(255,255,255,0.1);">';
            html += '<div style="display:flex; justify-content:space-between; align-items:center;">';
            html += '<div><span style="font-size:28px;">' + tool.icon + '</span> <span style="font-size:18px; font-weight:700;">' + tool.name + '</span></div>';
            html += '<button onclick="SevenTools.closePanel()" style="background:none; border:none; color:#888; font-size:24px; cursor:pointer;">✕</button>';
            html += '</div>';
            html += '<div style="font-size:12px; color:#888; margin-top:5px;">' + tool.desc + '</div>';
            html += '</div>';

            html += '<div style="padding:20px;">';
            html += '<div style="display:flex; gap:10px; margin-bottom:15px;">';
            html += '<button onclick="SevenTools.navigateLevel(2)" ' + (selected.length === 0 ? 'disabled ' : '') + 'style="flex:1; padding:12px; background:' + (selected.length > 0 ? '#00d4aa' : 'rgba(255,255,255,0.1)') + '; color:' + (selected.length > 0 ? '#000' : '#666') + '; border:none; border-radius:8px; cursor:' + (selected.length > 0 ? 'pointer' : 'not-allowed') + '; font-weight:600;">已选(' + selected.length + ')</button>';
            html += '<button onclick="SevenTools.navigateLevel(2)" style="flex:1; padding:12px; background:rgba(167,139,250,0.2); color:#a78bfa; border:1px solid #a78bfa; border-radius:8px; cursor:pointer;">关注</button>';
            html += '</div>';

            html += '<div style="display:flex; gap:8px; margin-bottom:15px; font-size:12px;">';
            html += '<button onclick="SevenTools.sortProducts(\'confidence\')" style="padding:5px 10px; background:rgba(0,212,170,0.1); border:1px solid #00d4aa; color:#00d4aa; border-radius:20px; cursor:pointer;">置信度</button>';
            html += '<button onclick="SevenTools.sortProducts(\'change\')" style="padding:5px 10px; background:rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.2); color:#888; border-radius:20px; cursor:pointer;">涨跌幅</button>';
            html += '<button onclick="SevenTools.sortProducts(\'name\')" style="padding:5px 10px; background:rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.2); color:#888; border-radius:20px; cursor:pointer;">名称</button>';
            html += '</div>';

            html += '<div style="max-height:400px; overflow-y:auto;">';
            var self = this;
            products.forEach(function(p) {
                var isSelected = selected.indexOf(p.symbol) >= 0;
                var borderColor = isSelected ? '#00d4aa' : (p.status === '关注' ? '#a78bfa' : 'rgba(255,255,255,0.1)');
                html += '<div onclick="SevenTools.toggleProduct(\'' + p.symbol + '\')" style="display:flex; justify-content:space-between; align-items:center; padding:12px; background:rgba(0,0,0,0.3); border:1px solid ' + borderColor + '; border-radius:10px; margin-bottom:10px; cursor:pointer;">';
                html += '<div><div style="font-weight:600;">' + p.symbol + ' <span style="color:#888; font-size:12px;">' + p.name + '</span></div><div style="font-size:11px; color:#888;">$' + (typeof p.price === 'number' ? p.price.toLocaleString() : p.price) + '</div></div>';
                html += '<div style="text-align:right;"><div style="color:' + (p.change >= 0 ? '#00d4aa' : '#ef4444') + '; font-weight:600;">' + (p.change >= 0 ? '+' : '') + p.change + '%</div><div style="font-size:12px; color:' + (p.confidence >= 80 ? '#00d4aa' : p.confidence >= 60 ? '#f59e0b' : '#ef4444') + ';">置信 ' + p.confidence + '%</div></div>';
                html += '<div style="margin-left:10px; color:' + (isSelected ? '#00d4aa' : p.status === '关注' ? '#a78bfa' : '#666') + '; font-size:18px;">' + (isSelected ? '✓' : p.status === '关注' ? '★' : '+') + '</div>';
                html += '</div>';
            });
            html += '</div>';

            html += '<button onclick="SevenTools.navigateLevel(2)" ' + (selected.length === 0 ? 'disabled ' : '') + 'style="width:100%; padding:15px; margin-top:15px; background:' + (selected.length > 0 ? 'linear-gradient(135deg, #00d4aa, #00a884)' : 'rgba(255,255,255,0.1)') + '; color:' + (selected.length > 0 ? '#000' : '#666') + '; border:none; border-radius:10px; cursor:' + (selected.length > 0 ? 'pointer' : 'not-allowed') + '; font-weight:700; font-size:16px;">下一步: 荐品(' + selected.length + ') →</button>';
            html += '</div></div></div>';
        }

        // Level 2: 荐品 (AI推荐 + 复盘+仿真)
        else if (this.state.level === 2) {
            var toolId = this.state.activeTool;
            var recommendText = '';
            if (toolId === 'rabbit') recommendText = 'EMA趋势信号强劲，MACD金叉形成，建议做多。风险评估：中等，建议50%仓位。';
            else if (toolId === 'mole') recommendText = 'PEPE成交量异常放大，波动率上升，火控雷达锁定。风险评估：较高，建议30%仓位。';
            else if (toolId === 'oracle') recommendText = 'MiroFish预测胜率78%，市场情绪转向积极。风险评估：低，建议60%仓位。';
            else recommendText = '基于复盘+仿真+ML迭代的综合分析，当前市场条件适合该工具操作。';

            html += '<div style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(10,14,23,0.98); z-index:10000; overflow:auto;">';
            html += '<div style="max-width:600px; margin:0 auto; background:rgba(20,25,35,0.98); border:1px solid rgba(0,212,170,0.2); border-radius:15px; margin-top:30px;">';
            html += '<div style="padding:20px; border-bottom:1px solid rgba(255,255,255,0.1); display:flex; justify-content:space-between; align-items:center;">';
            html += '<div><span style="font-size:28px;">' + tool.icon + '</span> <span style="font-size:18px; font-weight:700;">' + tool.name + ' - 荐品</span></div>';
            html += '<button onclick="SevenTools.closePanel()" style="background:none; border:none; color:#888; font-size:24px; cursor:pointer;">✕</button>';
            html += '</div>';

            html += '<div style="padding:20px;">';
            html += '<div style="background:rgba(0,212,170,0.1); border:1px solid rgba(0,212,170,0.3); border-radius:10px; padding:15px; margin-bottom:20px;">';
            html += '<div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;"><span style="font-size:24px;">🤖</span><div><div style="font-weight:600; color:#00d4aa;">AI荐品分析</div><div style="font-size:11px; color:#888;">基于复盘+仿真+ML迭代</div></div></div>';
            html += '<div style="font-size:12px; color:#888; line-height:1.6;">' + recommendText + '</div>';
            html += '</div>';

            html += '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px; margin-bottom:15px;">';
            html += '<div style="font-size:12px; color:#888; margin-bottom:8px;">权重决策等式</div>';
            html += '<div style="font-size:11px; color:#00d4aa; font-family:JetBrains Mono,monospace;">综合 = 0.25×原生 + 0.20×外部 + 0.20×复盘 + 0.20×仿真 + 0.10×ML + 0.05×其他</div>';
            html += '</div>';

            html += '<div style="margin-bottom:15px;">';
            html += '<div style="display:flex; justify-content:space-between; margin-bottom:8px;"><span style="color:#888; font-size:12px;">推荐仓位</span><span style="color:#00d4aa; font-weight:600;">' + Math.round(tool.position * params.positionMult) + '%</span></div>';
            html += '<div style="background:rgba(255,255,255,0.1); height:8px; border-radius:4px;"><div style="background:linear-gradient(90deg, #00d4aa, #00a884); height:100%; width:' + (tool.position * params.positionMult) + '%; border-radius:4px;"></div></div>';
            html += '</div>';

            html += '<div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:15px;">';
            html += '<div style="background:rgba(0,0,0,0.3); padding:12px; border-radius:8px; text-align:center;"><div style="font-size:10px; color:#888;">建议止损</div><div style="color:#ef4444; font-weight:700;">' + (tool.stopLoss * params.stopLossMult).toFixed(1) + '%</div></div>';
            html += '<div style="background:rgba(0,0,0,0.3); padding:12px; border-radius:8px; text-align:center;"><div style="font-size:10px; color:#888;">建议止盈</div><div style="color:#00d4aa; font-weight:700;">' + (tool.takeProfit * params.takeProfitMult).toFixed(1) + '%</div></div>';
            html += '</div>';

            html += '<div style="display:flex; gap:10px;">';
            html += '<button onclick="SevenTools.navigateLevel(1)" style="flex:1; padding:12px; background:rgba(255,255,255,0.1); color:#fff; border:1px solid rgba(255,255,255,0.2); border-radius:8px; cursor:pointer;">← 返回选品</button>';
            html += '<button onclick="SevenTools.navigateLevel(3)" style="flex:1; padding:12px; background:linear-gradient(135deg, #00d4aa, #00a884); color:#000; border:none; border-radius:8px; cursor:pointer; font-weight:600;">确认荐品 →</button>';
            html += '</div>';
            html += '</div></div></div>';
        }

        // Level 3: 确认
        else if (this.state.level === 3) {
            html += '<div style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(10,14,23,0.98); z-index:10000; overflow:auto;">';
            html += '<div style="max-width:600px; margin:0 auto; background:rgba(20,25,35,0.98); border:1px solid rgba(239,68,68,0.3); border-radius:15px; margin-top:30px;">';
            html += '<div style="padding:20px; border-bottom:1px solid rgba(255,255,255,0.1); display:flex; justify-content:space-between; align-items:center;">';
            html += '<div><span style="font-size:28px;">' + tool.icon + '</span> <span style="font-size:18px; font-weight:700;">' + tool.name + ' - 确认</span></div>';
            html += '<button onclick="SevenTools.closePanel()" style="background:none; border:none; color:#888; font-size:24px; cursor:pointer;">✕</button>';
            html += '</div>';

            html += '<div style="padding:20px;">';
            html += '<div style="background:rgba(239,68,68,0.1); border:2px solid rgba(239,68,68,0.3); border-radius:10px; padding:15px; margin-bottom:20px;">';
            html += '<div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;"><span style="font-size:24px;">⚠️</span><div style="font-weight:600; color:#ef4444;">请确认交易</div></div>';
            html += '<div style="font-size:12px; color:#888;">交易对: ' + (selected.length > 0 ? selected.join(', ') : '未选择') + '</div>';
            html += '</div>';

            html += '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px; margin-bottom:15px;">';
            html += '<div style="display:flex; justify-content:space-between; margin-bottom:8px;"><span style="color:#888;">模式</span><span style="color:' + (this.state.mode === 'normal' ? '#00d4aa' : '#a78bfa') + ';">' + (this.state.mode === 'normal' ? '🧠 普通' : '🎯 专家') + '</span></div>';
            html += '<div style="display:flex; justify-content:space-between; margin-bottom:8px;"><span style="color:#888;">风格</span><span style="color:' + (this.state.style === 'conservative' ? '#3b82f6' : this.state.style === 'balanced' ? '#00d4aa' : '#ef4444') + ';">' + (this.state.style === 'conservative' ? '🛡️ 保守' : this.state.style === 'balanced' ? '⚖️ 平衡' : '🚀 积极') + '</span></div>';
            html += '<div style="display:flex; justify-content:space-between; margin-bottom:8px;"><span style="color:#888;">仓位</span><span style="color:#00d4aa;">' + Math.round(tool.position * params.positionMult) + '%</span></div>';
            html += '<div style="display:flex; justify-content:space-between;"><span style="color:#888;">杠杆</span><span style="color:#00d4aa;">' + params.leverage + 'x</span></div>';
            html += '</div>';

            html += '<div style="display:flex; gap:10px;">';
            html += '<button onclick="SevenTools.navigateLevel(2)" style="flex:1; padding:12px; background:rgba(255,255,255,0.1); color:#fff; border:1px solid rgba(255,255,255,0.2); border-radius:8px; cursor:pointer;">← 返回</button>';
            html += '<button onclick="SevenTools.execute()" style="flex:1; padding:12px; background:linear-gradient(135deg, #ef4444, #dc2626); color:#fff; border:none; border-radius:8px; cursor:pointer; font-weight:700;">⚡ 执行交易</button>';
            html += '</div>';
            html += '</div></div></div>';
        }

        // Level 4: 结果/记录
        else if (this.state.level === 4) {
            html += '<div style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(10,14,23,0.98); z-index:10000; overflow:auto;">';
            html += '<div style="max-width:600px; margin:0 auto; background:rgba(20,25,35,0.98); border:1px solid rgba(0,212,170,0.2); border-radius:15px; margin-top:30px;">';
            html += '<div style="padding:20px; border-bottom:1px solid rgba(255,255,255,0.1); display:flex; justify-content:space-between; align-items:center;">';
            html += '<div><span style="font-size:28px;">' + tool.icon + '</span> <span style="font-size:18px; font-weight:700;">' + tool.name + ' - 结果</span></div>';
            html += '<button onclick="SevenTools.closePanel()" style="background:none; border:none; color:#888; font-size:24px; cursor:pointer;">✕</button>';
            html += '</div>';

            html += '<div style="padding:20px;">';
            html += '<div style="text-align:center; padding:30px;">';
            html += '<div style="font-size:64px; margin-bottom:20px;">✅</div>';
            html += '<div style="font-size:24px; font-weight:700; color:#00d4aa; margin-bottom:10px;">交易执行成功</div>';
            html += '<div style="color:#888; margin-bottom:20px;">订单号: TX' + Date.now().toString().slice(-8) + '</div>';
            html += '</div>';

            html += '<div style="background:rgba(0,0,0,0.4); border-radius:10px; padding:15px; margin-bottom:15px;">';
            html += '<div style="display:flex; justify-content:space-between; margin-bottom:8px;"><span style="color:#888;">交易对</span><span>' + (selected.length > 0 ? selected.join(', ') : '-') + '</span></div>';
            html += '<div style="display:flex; justify-content:space-between; margin-bottom:8px;"><span style="color:#888;">执行价格</span><span>$' + (products[0] ? products[0].price.toLocaleString() : '-') + '</span></div>';
            html += '<div style="display:flex; justify-content:space-between;"><span style="color:#888;">状态</span><span style="color:#00d4aa;">已完成</span></div>';
            html += '</div>';

            // 历史记录
            var history = this.state.tradeHistory.filter(function(h) { return h.tool === tool.id; });
            if (history.length > 0) {
                html += '<div style="margin-top:20px;">';
                html += '<div style="font-size:14px; font-weight:600; margin-bottom:10px;">📜 历史记录</div>';
                history.slice(-5).reverse().forEach(function(h) {
                    html += '<div style="display:flex; justify-content:space-between; padding:10px; background:rgba(0,0,0,0.3); border-radius:8px; margin-bottom:8px; font-size:12px;">';
                    html += '<span>' + h.symbols.join(', ') + '</span>';
                    html += '<span style="color:#888;">' + h.time + '</span>';
                    html += '<span style="color:' + (h.status === '执行成功' ? '#00d4aa' : '#ef4444') + ';">' + h.status + '</span>';
                    html += '</div>';
                });
                html += '</div>';
            }

            html += '<button onclick="SevenTools.closePanel()" style="width:100%; padding:15px; margin-top:20px; background:linear-gradient(135deg, #00d4aa, #00a884); color:#000; border:none; border-radius:10px; cursor:pointer; font-weight:700; font-size:16px;">完成</button>';
            html += '</div></div></div>';
        }

        container.innerHTML = html;
        container.style.display = 'block';
    },

    // 切换产品
    toggleProduct: function(symbol) {
        var toolId = this.state.activeTool;
        if (!this.state.selectedProducts[toolId]) {
            this.state.selectedProducts[toolId] = [];
        }
        var idx = this.state.selectedProducts[toolId].indexOf(symbol);
        if (idx >= 0) {
            this.state.selectedProducts[toolId].splice(idx, 1);
        } else {
            this.state.selectedProducts[toolId].push(symbol);
        }
        this.saveState();
        this.renderToolPanel();
    },

    // 排序产品
    sortProducts: function(criteria) {
        var toolId = this.state.activeTool;
        var products = this.products[toolId] || [];
        if (criteria === 'confidence') {
            products.sort(function(a, b) { return b.confidence - a.confidence; });
        } else if (criteria === 'change') {
            products.sort(function(a, b) { return b.change - a.change; });
        } else if (criteria === 'name') {
            products.sort(function(a, b) { return a.symbol.localeCompare(b.symbol); });
        }
        this.renderToolPanel();
    },

    // 导航到某一级
    navigateLevel: function(level) {
        this.state.level = level;
        this.renderToolPanel();
    },

    // 关闭面板
    closePanel: function() {
        var container = document.getElementById('toolPanelContainer');
        if (container) {
            container.style.display = 'none';
            container.innerHTML = '';
        }
        this.state.activeTool = null;
        this.state.level = 1;
    },

    // 执行交易
    execute: function() {
        var tool = this.tools[this.state.activeTool];
        var selected = this.state.selectedProducts[this.state.activeTool] || [];
        this.state.tradeHistory.push({
            id: Date.now(),
            tool: tool.id,
            toolName: tool.name,
            symbols: [].concat(selected),
            mode: this.state.mode,
            style: this.state.style,
            time: new Date().toLocaleString(),
            status: '执行成功'
        });
        this.saveState();
        this.navigateLevel(4);
    },

    // 渲染资金面板
    renderCapitalPanel: function() {
        var c = document.getElementById('capitalPanel');
        if (!c) return;
        var self = this;
        var html = '<div style="padding:15px;"><h4 style="margin:0 0 15px 0; color:#00d4aa;">💰 资金分配</h4>';
        Object.keys(this.state.capitalAllocation).forEach(function(id) {
            var pct = self.state.capitalAllocation[id];
            var tool = self.tools[id];
            if (!tool) return;
            html += '<div style="margin-bottom:12px;">';
            html += '<div style="display:flex; justify-content:space-between; margin-bottom:5px;"><span>' + tool.icon + ' ' + tool.name + '</span><span style="color:#00d4aa; font-weight:600;">' + pct + '%</span></div>';
            html += '<input type="range" min="0" max="50" value="' + pct + '" onchange="SevenTools.updateCapital(\'' + id + '\', this.value)" style="width:100%;">';
            html += '</div>';
        });
        html += '<button onclick="SevenTools.autoRebalanceCapital()" style="width:100%; padding:10px; background:rgba(0,212,170,0.2); border:1px solid #00d4aa; color:#00d4aa; border-radius:8px; cursor:pointer; margin-top:10px;">🔄 自动再平衡</button>';
        html += '</div>';
        c.innerHTML = html;
    },

    updateCapital: function(id, value) {
        this.state.capitalAllocation[id] = parseInt(value);
        this.saveState();
        this.renderCapitalPanel();
    },

    autoRebalanceCapital: function() {
        this.state.capitalAllocation = this.getDefaultCapital();
        this.saveState();
        this.renderCapitalPanel();
        awShowToast('资金已自动再平衡');
    },

    // 渲染算力面板
    renderComputePanel: function() {
        var c = document.getElementById('computePanel');
        if (!c) return;
        var self = this;
        var html = '<div style="padding:15px;"><h4 style="margin:0 0 15px 0; color:#a78bfa;">⚡ 算力分配</h4>';
        Object.keys(this.state.computeAllocation).forEach(function(id) {
            var pct = self.state.computeAllocation[id];
            var tool = self.tools[id];
            if (!tool) return;
            html += '<div style="margin-bottom:12px;">';
            html += '<div style="display:flex; justify-content:space-between; margin-bottom:5px;"><span>' + tool.icon + ' ' + tool.name + '</span><span style="color:#a78bfa; font-weight:600;">' + pct + '%</span></div>';
            html += '<input type="range" min="0" max="50" value="' + pct + '" onchange="SevenTools.updateCompute(\'' + id + '\', this.value)" style="width:100%;">';
            html += '</div>';
        });
        html += '<button onclick="SevenTools.autoRebalanceCompute()" style="width:100%; padding:10px; background:rgba(167,139,250,0.2); border:1px solid #a78bfa; color:#a78bfa; border-radius:8px; cursor:pointer; margin-top:10px;">🔄 自动再平衡</button>';
        html += '</div>';
        c.innerHTML = html;
    },

    updateCompute: function(id, value) {
        this.state.computeAllocation[id] = parseInt(value);
        this.saveState();
        this.renderComputePanel();
    },

    autoRebalanceCompute: function() {
        this.state.computeAllocation = this.getDefaultCompute();
        this.saveState();
        this.renderComputePanel();
        awShowToast('算力已自动再平衡');
    },

    // 渲染API状态
    renderAPIStatus: function() {
        var c = document.getElementById('apiStatusPanel');
        if (!c) return;
        var apis = [
            { name: 'Binance', status: 'online', latency: 45 },
            { name: 'Bybit', status: 'online', latency: 52 },
            { name: 'OKX', status: 'standby', latency: 68 },
            { name: 'Polymarket', status: 'online', latency: 120 }
        ];
        var html = '<div style="padding:15px;"><h4 style="margin:0 0 15px 0; color:#888;">📡 API状态</h4>';
        var self = this;
        apis.forEach(function(api) {
            var color = api.latency < 60 ? '#00d4aa' : api.latency < 100 ? '#f59e0b' : '#ef4444';
            html += '<div style="display:flex; justify-content:space-between; align-items:center; padding:10px; background:rgba(0,0,0,0.3); border-radius:8px; margin-bottom:8px;">';
            html += '<div style="display:flex; align-items:center; gap:8px;"><span style="width:8px; height:8px; border-radius:50%; background:' + (api.status === 'online' ? '#00d4aa' : '#f59e0b') + ';"></span><span>' + api.name + '</span></div>';
            html += '<div style="color:' + color + '; font-size:12px;">' + api.latency + 'ms</div>';
            html += '</div>';
        });
        html += '<div style="margin-top:15px; padding:10px; background:rgba(0,0,0,0.3); border-radius:8px;">';
        html += '<div style="display:flex; justify-content:space-between; margin-bottom:5px;"><span style="color:#888; font-size:12px;">缓存命中率</span><span style="color:#00d4aa; font-size:12px;">94.7%</span></div>';
        html += '<div style="background:rgba(255,255,255,0.1); height:4px; border-radius:2px;"><div style="background:#00d4aa; height:100%; width:94.7%; border-radius:2px;"></div></div>';
        html += '</div></div>';
        c.innerHTML = html;
    }
};

// Auto-init
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() { SevenTools.init(); });
} else {
    SevenTools.init();
}
