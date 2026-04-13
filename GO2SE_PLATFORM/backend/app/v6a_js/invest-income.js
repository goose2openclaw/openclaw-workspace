// ========== 投资收益模块 (V14) ==========
const InvestIncome = {
    state: {
        level: 1,
        totalInvest: 100000,
        totalReturn: 12350,
        totalValue: 112350,
        dayChange: 1250,
        dayChangePercent: 1.12,
        positions: [
            { name: 'BTC', symbol: 'BTCUSDT', amount: 0.5, avgPrice: 71000, currentPrice: 75000, value: 37500, pnl: 2340, pnlPercent: 6.6, allocation: 33.4, trend: 'up' },
            { name: 'ETH', symbol: 'ETHUSDT', amount: 5, avgPrice: 3200, currentPrice: 3400, value: 17000, pnl: 1120, pnlPercent: 7.5, allocation: 15.1, trend: 'up' },
            { name: 'SOL', symbol: 'SOLUSDT', amount: 100, avgPrice: 145, currentPrice: 178, value: 17800, pnl: 2150, pnlPercent: 22.8, allocation: 15.8, trend: 'up' },
            { name: 'BNB', symbol: 'BNBUSDT', amount: 10, avgPrice: 580, currentPrice: 610, value: 6100, pnl: 340, pnlPercent: 5.9, allocation: 5.4, trend: 'up' },
            { name: 'PEPE', symbol: 'PEPEUSDT', amount: 100000000, avgPrice: 0.0001, currentPrice: 0.000089, value: 8900, pnl: -1200, pnlPercent: -11.9, allocation: 7.9, trend: 'down' }
        ],
        history: [
            { date: '2026-04-06', action: '买入BTC', amount: 0.1, price: 74500, total: 7450 },
            { date: '2026-04-05', action: '卖出ETH', amount: 0.5, price: 3350, total: 1675 },
            { date: '2026-04-04', action: '买入SOL', amount: 20, price: 165, total: 3300 },
            { date: '2026-04-03', action: '买入PEPE', amount: 50000000, price: 0.000095, total: 4750 },
            { date: '2026-04-01', action: '买入BNB', amount: 5, price: 595, total: 2975 }
        ]
    },
    
    init: function() { console.log('📈 InvestIncome initialized'); },
    
    renderPanel: function(level) {
        level = level || 1;
        var contents = {
            1: { title: '收益总览', data: this.getOverview() },
            2: { title: '持仓明细', data: this.getPositions() },
            3: { title: '历史记录', data: this.getHistory() },
            4: { title: '收益分析', data: this.getAnalysis() }
        };
        var c = contents[level] || contents[1];
        return '<div class="module-detail">' +
            '<h2>' + c.title + '</h2>' +
            c.data +
            '</div>';
    },
    
    getOverview: function() {
        var html = '<div class="income-stats">';
        html += '<div class="income-stat-card">';
        html += '<div class="value ' + (this.state.dayChange >= 0 ? 'positive' : 'negative') + '">' + (this.state.dayChange >= 0 ? '+' : '') + '$' + this.state.dayChange.toFixed(2) + '</div>';
        html += '<div class="label">今日收益</div>';
        html += '</div>';
        html += '<div class="income-stat-card">';
        html += '<div class="value ' + (this.state.dayChangePercent >= 0 ? 'positive' : 'negative') + '">' + (this.state.dayChangePercent >= 0 ? '+' : '') + this.state.dayChangePercent.toFixed(2) + '%</div>';
        html += '<div class="label">收益率</div>';
        html += '</div>';
        html += '</div>';
        
        html += '<div class="portfolio-summary">';
        html += '<div class="portfolio-item">';
        html += '<span class="portfolio-label">总投资</span>';
        html += '<span class="portfolio-value">$' + this.state.totalInvest.toLocaleString() + '</span>';
        html += '</div>';
        html += '<div class="portfolio-item highlight">';
        html += '<span class="portfolio-label">总收益</span>';
        html += '<span class="portfolio-value ' + (this.state.totalReturn >= 0 ? 'positive' : 'negative') + '">' + (this.state.totalReturn >= 0 ? '+' : '') + '$' + this.state.totalReturn.toLocaleString() + '</span>';
        html += '</div>';
        html += '<div class="portfolio-item">';
        html += '<span class="portfolio-label">当前价值</span>';
        html += '<span class="portfolio-value">$' + this.state.totalValue.toLocaleString() + '</span>';
        html += '</div>';
        html += '</div>';
        
        return html;
    },
    
    getPositions: function() {
        var html = '<div class="positions-table">';
        var self = this;
        this.state.positions.forEach(function(p) {
            html += '<div class="position-item">';
            html += '<div class="position-main">';
            html += '<div class="position-icon">' + self.getCoinIcon(p.name) + '</div>';
            html += '<div class="position-info">';
            html += '<div class="position-name">' + p.name + '</div>';
            html += '<div class="position-amount">' + p.amount + ' @ $' + p.currentPrice.toLocaleString() + '</div>';
            html += '</div>';
            html += '</div>';
            html += '<div class="position-value">$' + p.value.toLocaleString() + '</div>';
            html += '<div class="position-pnl ' + (p.pnl >= 0 ? 'positive' : 'negative') + '">';
            html += '<div>' + (p.pnl >= 0 ? '+' : '') + '$' + p.pnl.toFixed(2) + '</div>';
            html += '<div class="pnl-percent">' + (p.pnlPercent >= 0 ? '+' : '') + p.pnlPercent.toFixed(2) + '%</div>';
            html += '</div>';
            html += '<div class="position-alloc">' + p.allocation.toFixed(1) + '%</div>';
            html += '</div>';
        });
        html += '</div>';
        return html;
    },
    
    getHistory: function() {
        var html = '<div class="history-list">';
        var self = this;
        this.state.history.forEach(function(h) {
            var isBuy = h.action.includes('买入');
            html += '<div class="history-item">';
            html += '<div class="history-date">' + h.date + '</div>';
            html += '<div class="history-action ' + (isBuy ? 'buy' : 'sell') + '">' + h.action + '</div>';
            html += '<div class="history-details">' + h.amount + ' @ $' + h.price.toLocaleString() + '</div>';
            html += '<div class="history-total ' + (isBuy ? 'negative' : 'positive') + '">' + (isBuy ? '-' : '+') + '$' + h.total.toLocaleString() + '</div>';
            html += '</div>';
        });
        html += '</div>';
        return html;
    },
    
    getAnalysis: function() {
        var html = '<div class="analysis-container">';
        html += '<div class="analysis-section">';
        html += '<h4>📊 收益分析</h4>';
        html += '<div class="analysis-grid">';
        html += '<div class="analysis-item">';
        html += '<div class="analysis-label">总收益率</div>';
        html += '<div class="analysis-value positive">' + (this.state.totalReturn / this.state.totalInvest * 100).toFixed(2) + '%</div>';
        html += '</div>';
        html += '<div class="analysis-item">';
        html += '<div class="analysis-label">盈利持仓</div>';
        html += '<div class="analysis-value">' + this.state.positions.filter(function(p) { return p.pnl > 0; }).length + '/' + this.state.positions.length + '</div>';
        html += '</div>';
        html += '<div class="analysis-item">';
        html += '<div class="analysis-label">最佳持仓</div>';
        var best = this.state.positions.reduce(function(a, b) { return a.pnlPercent > b.pnlPercent ? a : b; });
        html += '<div class="analysis-value">' + best.name + ' +' + best.pnlPercent.toFixed(1) + '%</div>';
        html += '</div>';
        html += '<div class="analysis-item">';
        html += '<div class="analysis-label">亏损持仓</div>';
        var worst = this.state.positions.reduce(function(a, b) { return a.pnlPercent < b.pnlPercent ? a : b; });
        html += '<div class="analysis-value negative">' + worst.name + ' ' + worst.pnlPercent.toFixed(1) + '%</div>';
        html += '</div>';
        html += '</div>';
        html += '</div>';
        
        html += '<div class="analysis-section">';
        html += '<h4>💡 建议</h4>';
        html += '<ul class="analysis-tips">';
        html += '<li>PEPE处于亏损状态，建议关注止损线</li>';
        html += '<li>SOL表现最佳，可考虑适度加仓</li>';
        html += '<li>整体仓位分散度良好</li>';
        html += '</ul>';
        html += '</div>';
        
        html += '</div>';
        return html;
    },
    
    getCoinIcon: function(name) {
        var icons = { BTC: '₿', ETH: 'Ξ', SOL: '◎', BNB: '🔶', PEPE: '🐸' };
        return icons[name] || '●';
    }
};
