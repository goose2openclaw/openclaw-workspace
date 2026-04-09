// ========== 风险状态模块 (V14) ==========
const AssetRisk = {
    state: {
        level: 1,
        riskScore: 35,
        riskLevel: 'low',
        var: 2.5,
        maxDrawdown: 8.5,
        sharpeRatio: 1.85,
        leverage: 1.0,
        totalExposure: 45,
        positions: [
            { symbol: 'BTCUSDT', side: 'long', size: 25, pnl: 1250, risk: 'low' },
            { symbol: 'ETHUSDT', side: 'long', size: 15, pnl: 560, risk: 'medium' },
            { symbol: 'SOLUSDT', side: 'long', size: 10, pnl: 340, risk: 'low' },
            { symbol: 'PEPEUSDT', side: 'short', size: 5, pnl: -120, risk: 'high' }
        ],
        alerts: [
            { id: 1, level: 'warning', msg: 'PEPE空头仓位亏损11.9%，接近止损线', time: '14:32:15', read: false },
            { id: 2, level: 'info', msg: 'BTC RSI指标70，处于超买区域', time: '14:25:03', read: true }
        ],
        rules: [
            { name: '仓位限制', desc: '单笔仓位不超过5%总资金', enabled: true, value: '5%' },
            { name: '日亏损熔断', desc: '日亏损超过15%自动停止交易', enabled: true, value: '15%' },
            { name: '止损规则', desc: '每个仓位必须设置止损', enabled: true, value: '2%' }
        ]
    },
    init: function() { console.log('⚠️ AssetRisk initialized'); },
    renderPanel: function(level) {
        level = level || 1;
        var contents = {
            1: { title: '风险总览', data: this.getOverview() },
            2: { title: '风险指标', data: this.getMetrics() },
            3: { title: '告警记录', data: this.getAlerts() },
            4: { title: '风控设置', data: this.getSettings() }
        };
        var c = contents[level] || contents[1];
        return '<div class="module-detail"><h2>' + c.title + '</h2>' + c.data + '</div>';
    },
    getOverview: function() {
        var lc = { low: '#00d4aa', medium: '#f59e0b', high: '#ef4444' };
        var lt = { low: '低风险', medium: '中等风险', high: '高风险' };
        var html = '<div class="risk-overview">';
        html += '<div class="risk-metric"><div class="icon">📊</div><div class="value" style="color:' + lc[this.state.riskLevel] + '">' + this.state.riskScore + '</div><div class="label">风险评分</div></div>';
        html += '<div class="risk-metric"><div class="icon">📉</div><div class="value">' + this.state.var + '%</div><div class="label">VaR</div></div>';
        html += '<div class="risk-metric"><div class="icon">📈</div><div class="value">' + this.state.sharpeRatio + '</div><div class="label">夏普比率</div></div>';
        html += '</div>';
        html += '<div class="risk-status-card" style="border-color:' + lc[this.state.riskLevel] + '">';
        html += '<div class="status-icon">' + (this.state.riskLevel === 'low' ? '✅' : '⚠️') + '</div>';
        html += '<div class="status-info"><div class="status-level" style="color:' + lc[this.state.riskLevel] + '">' + lt[this.state.riskLevel] + '</div></div>';
        html += '</div>';
        return html;
    },
    getMetrics: function() {
        var html = '<div class="metrics-grid">';
        html += '<div class="metric-card"><div class="metric-name">VaR</div><div class="metric-value">' + this.state.var + '%</div></div>';
        html += '<div class="metric-card"><div class="metric-name">最大回撤</div><div class="metric-value negative">' + this.state.maxDrawdown + '%</div></div>';
        html += '<div class="metric-card"><div class="metric-name">夏普比率</div><div class="metric-value">' + this.state.sharpeRatio + '</div></div>';
        html += '<div class="metric-card"><div class="metric-name">杠杆</div><div class="metric-value">' + this.state.leverage + 'x</div></div>';
        html += '</div>';
        html += '<div class="positions-risk"><h4>仓位风险</h4>';
        var self = this;
        this.state.positions.forEach(function(p) {
            var rc = { low: '#00d4aa', medium: '#f59e0b', high: '#ef4444' }[p.risk];
            html += '<div class="position-risk-item">';
            html += '<span class="pos-symbol">' + p.symbol + '</span>';
            html += '<span class="pos-pnl ' + (p.pnl >= 0 ? 'positive' : 'negative') + '">$' + p.pnl.toFixed(2) + '</span>';
            html += '<span class="pos-risk" style="color:' + rc + '">' + p.risk.toUpperCase() + '</span>';
            html += '</div>';
        });
        html += '</div>';
        return html;
    },
    getAlerts: function() {
        var html = '<div class="alerts-list">';
        var self = this;
        this.state.alerts.forEach(function(a) {
            var li = { warning: '⚠️', danger: '🚨', info: 'ℹ️' };
            var lc = { warning: '#f59e0b', danger: '#ef4444', info: '#3b82f6' };
            html += '<div class="alert-item' + (a.read ? ' read' : '') + '">';
            html += '<div class="alert-icon" style="color:' + lc[a.level] + '">' + li[a.level] + '</div>';
            html += '<div class="alert-msg">' + a.msg + '</div>';
            html += '<div class="alert-time">' + a.time + '</div></div>';
        });
        html += '</div>';
        return html;
    },
    getSettings: function() {
        var html = '<div class="rules-list"><h4>风控规则</h4>';
        var self = this;
        this.state.rules.forEach(function(r) {
            html += '<div class="rule-item">';
            html += '<div class="rule-info"><div class="rule-name">' + r.name + '</div><div class="rule-desc">' + r.desc + '</div></div>';
            html += '<div class="rule-value">' + r.value + '</div></div>';
        });
        html += '</div>';
        html += '<div class="emergency-section"><h4>🆘 紧急措施</h4>';
        html += '<button class="emergency-btn danger" onclick="AssetRisk.emergencyClose()">🚨 立即平仓</button>';
        html += '<button class="emergency-btn warning" onclick="AssetRisk.emergencyStop()">⏸️ 暂停交易</button></div>';
        return html;
    },
    emergencyClose: function() { alert('紧急平仓功能开发中...'); },
    emergencyStop: function() { alert('交易暂停功能开发中...'); }
};
