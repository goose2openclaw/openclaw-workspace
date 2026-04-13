// ========== 交易仿真模块 (V14) ==========
const TradingSim = {
    state: {
        level: 1,
        simulations: [
            { id: 1, name: 'BTC趋势跟踪', symbol: 'BTCUSDT', type: 'trend', result: 'profit', pnl: 1250.50, winrate: 72 },
            { id: 2, name: 'ETH网格交易', symbol: 'ETHUSDT', type: 'grid', result: 'profit', pnl: 830.00, winrate: 68 },
            { id: 3, name: 'SOL合约对冲', symbol: 'SOLUSDT', type: 'hedge', result: 'loss', pnl: -320.00, winrate: 55 }
        ],
        activeSimulation: null
    },
    
    init: function() { console.log('🔮 TradingSim initialized'); },
    
    renderPanel: function(level) {
        level = level || 1;
        var contents = {
            1: { title: '仿真总览', data: this.getOverview() },
            2: { title: '仿真记录', data: this.getRecords() },
            3: { title: '新建仿真', data: this.getNewSim() },
            4: { title: '仿真设置', data: this.getSettings() }
        };
        var c = contents[level] || contents[1];
        return '<div class="module-detail">' +
            '<h2>' + c.title + '</h2>' +
            c.data +
            '</div>';
    },
    
    getOverview: function() {
        var totalPnL = this.state.simulations.reduce(function(s, m) { return s + m.pnl; }, 0);
        var wins = this.state.simulations.filter(function(m) { return m.result === 'profit'; }).length;
        var winrate = Math.round(wins / this.state.simulations.length * 100);
        
        return '<div class="sim-dashboard">' +
            '<div class="sim-card">' +
            '<div class="value ' + (totalPnL >= 0 ? 'positive' : 'negative') + '">' + (totalPnL >= 0 ? '+' : '') + '$' + totalPnL.toFixed(2) + '</div>' +
            '<div class="label">总收益</div>' +
            '</div>' +
            '<div class="sim-card">' +
            '<div class="value positive">' + winrate + '%</div>' +
            '<div class="label">胜率</div>' +
            '</div>' +
            '<div class="sim-card">' +
            '<div class="value">' + this.state.simulations.length + '</div>' +
            '<div class="label">仿真数</div>' +
            '</div>' +
            '</div>' +
            '<button class="start-sim-btn" onclick="TradingSim.startNewSim()">+ 新建仿真</button>';
    },
    
    getRecords: function() {
        var html = '<div class="sim-records">';
        var self = this;
        this.state.simulations.forEach(function(sim) {
            html += '<div class="record-item">';
            html += '<span class="symbol">' + sim.symbol + '</span>';
            html += '<span class="type">' + sim.type + '</span>';
            html += '<span class="pnl ' + (sim.pnl >= 0 ? 'positive' : 'negative') + '">' + (sim.pnl >= 0 ? '+' : '') + '$' + sim.pnl.toFixed(2) + '</span>';
            html += '</div>';
        });
        html += '</div>';
        return html;
    },
    
    getNewSim: function() {
        return '<div class="new-sim-form">' +
            '<div class="form-group">' +
            '<label>仿真名称</label>' +
            '<input type="text" placeholder="例如: BTC突破策略" class="form-input">' +
            '</div>' +
            '<div class="form-group">' +
            '<label>交易对</label>' +
            '<select class="form-select">' +
            '<option>BTCUSDT</option>' +
            '<option>ETHUSDT</option>' +
            '<option>SOLUSDT</option>' +
            '</select>' +
            '</div>' +
            '<div class="form-group">' +
            '<label>策略类型</label>' +
            '<select class="form-select">' +
            '<option>趋势跟踪</option>' +
            '<option>网格交易</option>' +
            '<option>对冲</option>' +
            '<option>套利</option>' +
            '</select>' +
            '</div>' +
            '<div class="form-group">' +
            '<label>初始资金</label>' +
            '<input type="number" value="10000" class="form-input">' +
            '</div>' +
            '<button class="submit-btn" onclick="TradingSim.submitSim()">开始仿真</button>' +
            '</div>';
    },
    
    getSettings: function() {
        return '<div class="sim-settings">' +
            '<div class="setting-item">' +
            '<span>默认滑点</span>' +
            '<input type="range" min="0.1" max="1" step="0.1" value="0.2" class="setting-range">' +
            '<span class="setting-value">0.2%</span>' +
            '</div>' +
            '<div class="setting-item">' +
            '<span>手续费率</span>' +
            '<input type="range" min="0.01" max="0.5" step="0.01" value="0.1" class="setting-range">' +
            '<span class="setting-value">0.1%</span>' +
            '</div>' +
            '<div class="setting-item">' +
            '<span>杠杆倍数</span>' +
            '<input type="range" min="1" max="10" step="1" value="1" class="setting-range">' +
            '<span class="setting-value">1x</span>' +
            '</div>' +
            '</div>';
    },
    
    startNewSim: function() {
        this.state.level = 3;
        this.renderPanel(3);
    },
    
    submitSim: function() {
        alert('仿真功能开发中，敬请期待！');
    }
};
