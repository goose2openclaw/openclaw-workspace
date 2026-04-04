/**
 * 公开数据页面 - 解决信任问题
 */

window.PublicDashboard = {
    cache: {},
    
    template() {
        return '<div id="page-content"></div>';
    },
    
    init() {
        this.loadDashboard();
        console.log('📊 公开数据页面已初始化');
    },
    
    async loadDashboard() {
        try {
            const response = await fetch('/api/public/dashboard');
            const data = await response.json();
            
            if (data.status === 'success') {
                this.render(data);
                this.cache = data;
            }
        } catch (error) {
            console.error('加载公开数据失败:', error);
            this.showError();
        }
    },
    
    render(data) {
        const html = `
            <div class="public-dashboard">
                <div class="page-header">
                    <div class="page-title">
                        <h1>📊 公开数据</h1>
                        <p class="page-desc">交易历史和收益表现 - 透明可信</p>
                    </div>
                    <div class="last-updated">
                        最后更新: ${data.last_updated || '未知'}
                    </div>
                </div>
                
                <!-- 核心指标 -->
                <div class="trust-stats">
                    <div class="trust-card main">
                        <div class="trust-icon">💰</div>
                        <div class="trust-value">${data.summary.total_value}</div>
                        <div class="trust-label">总资产</div>
                        <div class="trust-change up">+${data.summary.total_pnl_pct} (${data.summary.total_pnl})</div>
                    </div>
                    <div class="trust-card">
                        <div class="trust-icon">🎯</div>
                        <div class="trust-value">${data.summary.win_rate}</div>
                        <div class="trust-label">胜率</div>
                    </div>
                    <div class="trust-card">
                        <div class="trust-icon">📈</div>
                        <div class="trust-value">${data.summary.sharpe_ratio}</div>
                        <div class="trust-label">夏普比率</div>
                    </div>
                    <div class="trust-card">
                        <div class="trust-icon">📉</div>
                        <div class="trust-value">-${data.summary.max_drawdown}</div>
                        <div class="trust-label">最大回撤</div>
                    </div>
                </div>
                
                <!-- 权益曲线 -->
                <div class="section">
                    <h2>📈 权益曲线 (近30天)</h2>
                    <div class="equity-chart" id="equity-chart">
                        ${this.renderEquityCurve(data.equity_curve)}
                    </div>
                </div>
                
                <!-- 近期交易 -->
                <div class="section">
                    <h2>📋 近期交易</h2>
                    <div class="recent-trades">
                        ${this.renderRecentTrades(data.recent_trades)}
                    </div>
                </div>
                
                <!-- 策略排行榜 -->
                <div class="section">
                    <h2>🏆 策略排行榜</h2>
                    <div class="strategy-leaderboard">
                        ${this.renderLeaderboard(data.top_strategies)}
                    </div>
                </div>
                
                <!-- 免责声明 -->
                <div class="disclaimer">
                    <p>⚠️ ${data.disclaimer}</p>
                </div>
            </div>
        `;
        
        document.getElementById('page-content').innerHTML = html;
    },
    
    renderEquityCurve(curve) {
        if (!curve || curve.length === 0) return '<p>暂无数据</p>';
        
        const max = Math.max(...curve.map(c => c.capital));
        const min = Math.min(...curve.map(c => c.capital));
        const range = max - min || 1;
        
        const bars = curve.map((c, i) => {
            const height = ((c.capital - min) / range * 100).toFixed(1);
            const color = c.pnl >= 0 ? '#34c759' : '#ff3b30';
            return `<div class="bar" style="height: ${Math.max(height, 5)}%; background: ${color};" title="${c.date}: $${c.capital.toFixed(2)}"></div>`;
        }).join('');
        
        return `<div class="chart-container">${bars}</div>`;
    },
    
    renderRecentTrades(trades) {
        if (!trades || trades.length === 0) return '<p>暂无交易</p>';
        
        return `
            <table class="trades-table">
                <thead>
                    <tr>
                        <th>时间</th>
                        <th>币种</th>
                        <th>方向</th>
                        <th>策略</th>
                        <th>置信度</th>
                        <th>收益</th>
                    </tr>
                </thead>
                <tbody>
                    ${trades.map(t => `
                        <tr class="${t.win ? 'win' : 'loss'}">
                            <td>${new Date(t.date).toLocaleString('zh-CN')}</td>
                            <td><strong>${t.symbol}</strong></td>
                            <td><span class="side ${t.side}">${t.side === 'buy' ? '买入' : '卖出'}</span></td>
                            <td>${t.strategy}</td>
                            <td>${t.confidence}%</td>
                            <td class="pnl ${t.win ? 'up' : 'down'}">
                                ${t.pnl >= 0 ? '+' : ''}${t.pnl.toFixed(2)} (${t.pnl_pct.toFixed(1)}%)
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    },
    
    renderLeaderboard(strategies) {
        if (!strategies || strategies.length === 0) return '<p>暂无数据</p>';
        
        return `
            <table class="leaderboard-table">
                <thead>
                    <tr>
                        <th>排名</th>
                        <th>策略</th>
                        <th>交易次数</th>
                        <th>胜率</th>
                        <th>总收益</th>
                    </tr>
                </thead>
                <tbody>
                    ${strategies.map((s, i) => `
                        <tr>
                            <td><span class="rank rank-${i+1}">${i+1}</span></td>
                            <td><strong>${s.name}</strong></td>
                            <td>${s.trades}</td>
                            <td class="${s.win_rate >= 60 ? 'up' : ''}">${s.win_rate}%</td>
                            <td class="pnl ${s.pnl >= 0 ? 'up' : 'down'}">
                                ${s.pnl >= 0 ? '+' : ''}$${s.pnl.toFixed(2)}
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    },
    
    showError() {
        document.getElementById('page-content').innerHTML = `
            <div class="error-state">
                <h2>加载失败</h2>
                <p>无法获取公开数据，请稍后重试。</p>
            </div>
        `;
    }
};
