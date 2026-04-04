// GO2SE v11 - Dashboard Page Module
const DashboardPage = {
    name: 'dashboard',
    
    data: {
        totalValue: 0,
        dailyPnL: 0,
        signalCount: 0,
        activePositions: 0,
        recentSignals: []
    },
    
    async load() {
        const container = document.getElementById('page-content');
        container.innerHTML = this.template();
        await this.fetchData();
        this.initCharts();
        this.initEventListeners();
    },
    
    template() {
        return `
        <div class="dashboard-page">
            <div class="page-header">
                <h1>📊 仪表盘</h1>
                <div class="header-actions">
                    <button class="btn-refresh" onclick="DashboardPage.refresh()">
                        <span>🔄</span> 刷新
                    </button>
                </div>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card stat-value">
                    <div class="stat-icon">💰</div>
                    <div class="stat-content">
                        <div class="stat-label">总资产</div>
                        <div class="stat-value" id="total-value">$0.00</div>
                    </div>
                </div>
                
                <div class="stat-card stat-pnl">
                    <div class="stat-icon">📈</div>
                    <div class="stat-content">
                        <div class="stat-label">日盈亏</div>
                        <div class="stat-value" id="daily-pnl">+$0.00</div>
                    </div>
                </div>
                
                <div class="stat-card stat-signals">
                    <div class="stat-icon">🎯</div>
                    <div class="stat-content">
                        <div class="stat-label">信号数</div>
                        <div class="stat-value" id="signal-count">0</div>
                    </div>
                </div>
                
                <div class="stat-card stat-positions">
                    <div class="stat-icon">📋</div>
                    <div class="stat-content">
                        <div class="stat-label">活跃仓位</div>
                        <div class="stat-value" id="active-positions">0</div>
                    </div>
                </div>
            </div>
            
            <div class="dashboard-grid">
                <div class="card chart-card">
                    <h3>📈 收益曲线</h3>
                    <canvas id="pnl-chart"></canvas>
                </div>
                
                <div class="card signals-card">
                    <h3>🎯 最新信号</h3>
                    <div id="recent-signals-list" class="signals-list">
                        <div class="loading">加载中...</div>
                    </div>
                </div>
            </div>
            
            <div class="tools-grid">
                <h3>🛠️ 北斗七鑫投资工具</h3>
                <div class="tools-row" id="tools-status">
                    <div class="tool-card" data-tool="rabbit">
                        <div class="tool-icon">🐰</div>
                        <div class="tool-name">打兔子</div>
                        <div class="tool-status active">●</div>
                    </div>
                    <div class="tool-card" data-tool="mole">
                        <div class="tool-icon">🐹</div>
                        <div class="tool-name">打地鼠</div>
                        <div class="tool-status active">●</div>
                    </div>
                    <div class="tool-card" data-tool="oracle">
                        <div class="tool-icon">🔮</div>
                        <div class="tool-name">走着瞧</div>
                        <div class="tool-status active">●</div>
                    </div>
                    <div class="tool-card" data-tool="leader">
                        <div class="tool-icon">👑</div>
                        <div class="tool-name">跟大哥</div>
                        <div class="tool-status active">●</div>
                    </div>
                    <div class="tool-card" data-tool="hitchhiker">
                        <div class="tool-icon">🍀</div>
                        <div class="tool-name">搭便车</div>
                        <div class="tool-status active">●</div>
                    </div>
                    <div class="tool-card" data-tool="airdrop">
                        <div class="tool-icon">💰</div>
                        <div class="tool-name">薅羊毛</div>
                        <div class="tool-status active">●</div>
                    </div>
                    <div class="tool-card" data-tool="crowdsource">
                        <div class="tool-icon">👶</div>
                        <div class="tool-name">穷孩子</div>
                        <div class="tool-status active">●</div>
                    </div>
                </div>
            </div>
        </div>
        `;
    },
    
    async fetchData() {
        try {
            const [stats, signals] = await Promise.all([
                API.get('/api/stats'),
                API.get('/api/signals?limit=5')
            ]);
            
            this.data.totalValue = stats.data?.total_value || 100000;
            this.data.signalCount = stats.data?.total_signals || 0;
            this.data.activePositions = stats.data?.open_trades || 0;
            this.data.dailyPnL = stats.data?.daily_pnl || 0;
            this.data.recentSignals = signals.data?.slice(0, 5) || [];
            
            this.updateUI();
        } catch (err) {
            console.error('Dashboard fetch error:', err);
        }
    },
    
    updateUI() {
        const totalEl = document.getElementById('total-value');
        const pnlEl = document.getElementById('daily-pnl');
        const signalEl = document.getElementById('signal-count');
        const posEl = document.getElementById('active-positions');
        
        if (totalEl) totalEl.textContent = `$${this.data.totalValue.toLocaleString()}`;
        if (pnlEl) {
            pnlEl.textContent = `${this.data.dailyPnL >= 0 ? '+' : ''}$${this.data.dailyPnL.toFixed(2)}`;
            pnlEl.className = `stat-value ${this.data.dailyPnL >= 0 ? 'positive' : 'negative'}`;
        }
        if (signalEl) signalEl.textContent = this.data.signalCount;
        if (posEl) posEl.textContent = this.data.activePositions;
        
        this.updateSignalsList();
    },
    
    updateSignalsList() {
        const container = document.getElementById('recent-signals-list');
        if (!container || !this.data.recentSignals.length) return;
        
        container.innerHTML = this.data.recentSignals.map(s => `
            <div class="signal-item signal-${s.signal}">
                <span class="signal-symbol">${s.symbol}</span>
                <span class="signal-action">${s.signal.toUpperCase()}</span>
                <span class="signal-confidence">${(s.confidence * 100).toFixed(0)}%</span>
            </div>
        `).join('');
    },
    
    initCharts() {
        const ctx = document.getElementById('pnl-chart');
        if (!ctx) return;
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
                datasets: [{
                    label: '收益',
                    data: [0, 0, 0, 0, 0, 0, 0],
                    borderColor: '#00D4AA',
                    backgroundColor: 'rgba(0, 212, 170, 0.1)',
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } }
            }
        });
    },
    
    initEventListeners() {
        document.querySelectorAll('.tool-card').forEach(card => {
            card.addEventListener('click', () => {
                const tool = card.dataset.tool;
                Router.navigate(tool);
            });
        });
    },
    
    async refresh() {
        await this.fetchData();
        Toast.show('数据已刷新', 'success');
    }
};

window.DashboardPage = DashboardPage;
