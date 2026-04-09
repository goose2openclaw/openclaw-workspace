// ========== 钱包架构模块 (V14) ==========
const WalletArch = {
    state: {
        level: 1,
        wallets: {
            main: { name: '主钱包', icon: '🏦', balance: 45000, exposure: 'high', color: '#ef4444', desc: '主要存储' },
            transit: { name: '中转钱包', icon: '🔄', balance: 10000, exposure: 'medium', color: '#f59e0b', desc: '日常交易' },
            backup: { name: '备用钱包', icon: '🔐', balance: 50000, exposure: 'zero', color: '#00d4aa', desc: '风控隔离' }
        }
    },
    
    init: function() { console.log('🏦 WalletArch initialized'); },
    
    renderPanel: function(level) {
        level = level || 1;
        var contents = {
            1: { title: '钱包总览', data: this.getOverview() },
            2: { title: '子钱包分配', data: this.getSubwallets() },
            3: { title: '资金流向', data: this.getFlow() },
            4: { title: '钱包设置', data: this.getSettings() }
        };
        var c = contents[level] || contents[1];
        return '<div class="module-detail">' +
            '<h2>' + c.title + '</h2>' +
            c.data +
            '</div>';
    },
    
    getOverview: function() {
        var total = Object.values(this.state.wallets).reduce(function(s, w) { return s + w.balance; }, 0);
        var html = '<div class="wallet-header">';
        html += '<div class="icon">🏦</div>';
        html += '<div class="info">';
        html += '<div class="balance">$' + total.toLocaleString() + '</div>';
        html += '<div class="label">总资产</div>';
        html += '</div>';
        html += '</div>';
        
        html += '<div class="wallet-list">';
        var self = this;
        Object.entries(this.state.wallets).forEach(function(entry) {
            var key = entry[0];
            var w = entry[1];
            html += '<div class="wallet-item" onclick="WalletArch.showDetail(\'' + key + '\')">';
            html += '<div class="wallet-item-icon" style="background:' + w.color + '20;color:' + w.color + '">' + w.icon + '</div>';
            html += '<div class="wallet-item-info">';
            html += '<div class="wallet-item-name">' + w.name + '</div>';
            html += '<div class="wallet-item-desc">' + w.desc + '</div>';
            html += '</div>';
            html += '<div class="wallet-item-balance">$' + w.balance.toLocaleString() + '</div>';
            html += '</div>';
        });
        html += '</div>';
        return html;
    },
    
    getSubwallets: function() {
        var html = '<div class="allocation-chart">';
        html += '<div class="allocation-legend">';
        var self = this;
        var colors = { main: '#ef4444', transit: '#f59e0b', backup: '#00d4aa' };
        Object.entries(this.state.wallets).forEach(function(entry) {
            var key = entry[0];
            var w = entry[1];
            html += '<div class="legend-item">';
            html += '<div class="legend-color" style="background:' + colors[key] + '"></div>';
            html += '<span>' + w.name + ': $' + w.balance.toLocaleString() + '</span>';
            html += '</div>';
        });
        html += '</div>';
        html += '</div>';
        
        html += '<div class="subwallet-list">';
        var self = this;
        Object.entries(this.state.wallets).forEach(function(entry) {
            var key = entry[0];
            var w = entry[1];
            html += '<div class="subwallet-item">';
            html += '<div class="tool">';
            html += '<span class="tool-icon">' + w.icon + '</span>';
            html += '<span class="tool-name">' + w.name + '</span>';
            html += '</div>';
            html += '<span class="balance-amount">$' + w.balance.toLocaleString() + '</span>';
            html += '</div>';
        });
        html += '</div>';
        return html;
    },
    
    getFlow: function() {
        return '<div class="flow-diagram">' +
            '<div class="flow-step">' +
            '<div class="flow-icon">💰</div>' +
            '<div class="flow-info"><div class="flow-name">主钱包</div><div class="flow-desc">冷存储</div></div>' +
            '</div>' +
            '<div class="flow-arrow">→</div>' +
            '<div class="flow-step">' +
            '<div class="flow-icon">🔄</div>' +
            '<div class="flow-info"><div class="flow-name">中转钱包</div><div class="flow-desc">日常交易</div></div>' +
            '</div>' +
            '<div class="flow-arrow">→</div>' +
            '<div class="flow-step">' +
            '<div class="flow-icon">📈</div>' +
            '<div class="flow-info"><div class="flow-name">交易所</div><div class="flow-desc">开仓/平仓</div></div>' +
            '</div>' +
            '</div>' +
            '<div class="flow-note">' +
            '<p>💡 <strong>安全原则：</strong></p>' +
            '<ul>' +
            '<li>主钱包不直接交易，只做冷存储</li>' +
            '<li>中转钱包控制单笔交易额度</li>' +
            '<li>备用钱包隔离风险，用于极端情况</li>' +
            '</ul>' +
            '</div>';
    },
    
    getSettings: function() {
        return '<div class="wallet-settings">' +
            '<div class="setting-section">' +
            '<h4>安全设置</h4>' +
            '<div class="setting-row">' +
            '<span>多签钱包</span>' +
            '<label class="switch"><input type="checkbox" checked><span class="slider"></span></label>' +
            '</div>' +
            '<div class="setting-row">' +
            '<span>延迟转账</span>' +
            '<label class="switch"><input type="checkbox" checked><span class="slider"></span></label>' +
            '</div>' +
            '<div class="setting-row">' +
            '<span>IP白名单</span>' +
            '<label class="switch"><input type="checkbox"><span class="slider"></span></label>' +
            '</div>' +
            '</div>' +
            '<div class="setting-section">' +
            '<h4>通知设置</h4>' +
            '<div class="setting-row">' +
            '<span>大额转账提醒</span>' +
            '<label class="switch"><input type="checkbox" checked><span class="slider"></span></label>' +
            '</div>' +
            '<div class="setting-row">' +
            '<span>异常登录提醒</span>' +
            '<label class="switch"><input type="checkbox" checked><span class="slider"></span></label>' +
            '</div>' +
            '</div>' +
            '</div>';
    },
    
    showDetail: function(key) {
        this.state.level = 2;
        this.renderPanel(2);
    }
};
