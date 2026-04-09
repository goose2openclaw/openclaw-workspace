// ========== 竞品对比模块 (V14) ==========
const Competitor = {
    state: {
        level: 1,
        competitors: [
            { name: '3Commas', url: '3commas.io', winrate: 68, features: ['Smart Trade', 'DCA Bot', 'Grid Bot'], price: '$29.99/月', color: '#00d4aa', rank: 1 },
            { name: 'HaasOnline', url: 'haasonline.com', winrate: 72, features: ['HaasBot', 'Script Editor', 'Backtesting'], price: '$89/月', color: '#7c3aed', rank: 2 },
            { name: 'FreqTrade', url: 'freqtrade.io', winrate: 65, features: ['免费开源', 'REST API', 'Docker'], price: '免费', color: '#f59e0b', rank: 3 },
            { name: 'Cornix', url: 'cornix.io', winrate: 70, features: ['Telegram Bot', 'Auto Trading', 'Signals'], price: '$24.99/月', color: '#ef4444', rank: 4 },
            { name: 'Bitsgap', url: 'bitsgap.com', winrate: 71, features: ['Grid Trading', 'Portfolio', 'Arbitrage'], price: '$39/月', color: '#06b6d4', rank: 5 }
        ]
    },
    
    init: function() { console.log('📊 Competitor initialized'); },
    
    renderPanel: function(level) {
        level = level || 1;
        var contents = {
            1: { title: '竞品总览', data: this.getOverview() },
            2: { title: '功能对比', data: this.getFeatures() },
            3: { title: '价格对比', data: this.getPricing() },
            4: { title: '优劣势', data: this.getAnalysis() }
        };
        var c = contents[level] || contents[1];
        return '<div class="module-detail">' +
            '<h2>' + c.title + '</h2>' +
            c.data +
            '</div>';
    },
    
    getOverview: function() {
        var html = '<div class="competitor-list">';
        var self = this;
        this.state.competitors.forEach(function(c) {
            var isBest = c.rank === 1;
            html += '<div class="competitor-item' + (isBest ? ' best' : '') + '">';
            html += '<div class="competitor-rank" style="color:' + c.color + '">#' + c.rank + '</div>';
            html += '<div class="competitor-info">';
            html += '<div class="name">' + c.name + '</div>';
            html += '<div class="features">' + c.features.join(' • ') + '</div>';
            html += '</div>';
            html += '<div class="competitor-score">' + c.winrate + '%</div>';
            html += '</div>';
        });
        html += '</div>';
        return html;
    },
    
    getFeatures: function() {
        var html = '<div class="feature-compare">';
        html += '<table class="compare-table">';
        html += '<thead><tr><th>功能</th><th>GO2SE</th><th>3Commas</th><th>Haas</th><th>Freq</th></tr></thead>';
        html += '<tbody>';
        var features = [
            ['MiroFish预测', '✓', '✗', '✗', '✗'],
            ['声纳库趋势', '✓', '✗', '✗', '✗'],
            ['七鑫工具', '✓', '✓', '✓', '✗'],
            ['GPU调度', '✓', '✗', '✗', '✗'],
            ['免费开源', '✓', '✗', '✗', '✓'],
            ['Docker支持', '✓', '✓', '✓', '✓']
        ];
        var self = this;
        features.forEach(function(row) {
            html += '<tr>';
            row.forEach(function(cell, i) {
                html += '<td' + (i === 1 ? ' class="go2se"' : '') + '>' + cell + '</td>';
            });
            html += '</tr>';
        });
        html += '</tbody></table></div>';
        return html;
    },
    
    getPricing: function() {
        var html = '<div class="pricing-grid">';
        var self = this;
        this.state.competitors.forEach(function(c) {
            var isBest = c.price === '免费';
            html += '<div class="pricing-card' + (isBest ? ' best' : '') + '">';
            html += '<div class="pricing-name" style="color:' + c.color + '">' + c.name + '</div>';
            html += '<div class="pricing-price">' + c.price + '</div>';
            html += '<div class="pricing-note">胜率 ' + c.winrate + '%</div>';
            html += '</div>';
        });
        html += '</div>';
        return html;
    },
    
    getAnalysis: function() {
        return '<div class="analysis-content">' +
            '<div class="analysis-section">' +
            '<h4>🪿 GO2SE 优势</h4>' +
            '<ul>' +
            '<li><strong>MiroFish预测</strong> - 100智能体共识，超越所有竞品</li>' +
            '<li><strong>声纳库123模型</strong> - 多维度趋势识别</li>' +
            '<li><strong>北斗七鑫体系</strong> - 完整投资+打工工具体系</li>' +
            '<li><strong>GPU算力调度</strong> - 智能化资源分配</li>' +
            '<li><strong>免费开源</strong> - 社区驱动，持续进化</li>' +
            '</ul>' +
            '</div>' +
            '<div class="analysis-section">' +
            '<h4>⚠️ 竞品优势</h4>' +
            '<ul>' +
            '<li><strong>HaasOnline</strong> - 专业的回测系统</li>' +
            '<li><strong>3Commas</strong> - 成熟的DCA机器人</li>' +
            '<li><strong>FreqTrade</strong> - 社区活跃，文档完善</li>' +
            '</ul>' +
            '</div>' +
            '</div>';
    }
};
