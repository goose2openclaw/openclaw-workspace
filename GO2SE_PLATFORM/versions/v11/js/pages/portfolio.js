// GO2SE v11 - Portfolio Page Module
const PortfolioPage = {
    name: 'portfolio',
    
    data: {
        portfolio: null,
        positions: []
    },
    
    async load() {
        const container = document.getElementById('page-content');
        container.innerHTML = this.template();
        await this.fetchData();
        this.initCharts();
    },
    
    template() {
        return `
        <div class="portfolio-page">
            <div class="page-header">
                <h1>💼 投资组合</h1>
                <div class="header-actions">
                    <button class="btn-refresh" onclick="PortfolioPage.refresh()">
                        <span>🔄</span> 刷新
                    </button>
                </div>
            </div>
            
            <div class="portfolio-summary">
                <div class="summary-card total">
                    <div class="summary-label">总资产</div>
                    <div class="summary-value" id="portfolio-total">$0.00</div>
                </div>
                <div class="summary-card invested">
                    <div class="summary-label">已投资</div>
                    <div class="summary-value" id="portfolio-invested">$0.00</div>
                </div>
                <div class="summary-card cash">
                    <div class="summary-label">现金</div>
                    <div class="summary-value" id="portfolio-cash">$0.00</div>
                </div>
                <div class="summary-card pnl">
                    <div class="summary-label">总盈亏</div>
                    <div class="summary-value" id="portfolio-pnl">$0.00</div>
                </div>
            </div>
            
            <div class="portfolio-grid">
                <div class="card allocation-card">
                    <h3>📊 仓位分配</h3>
                    <canvas id="allocation-chart"></canvas>
                </div>
                
                <div class="card positions-card">
                    <h3>📋 当前仓位</h3>
                    <div id="positions-list" class="positions-list">
                        <div class="loading">加载中...</div>
                    </div>
                </div>
            </div>
            
            <div class="card history-card">
                <h3>📈 历史记录</h3>
                <canvas id="history-chart"></canvas>
            </div>
        </div>
        `;
    },
    
    async fetchData() {
        try {
            const res = await API.get('/api/portfolio');
            this.data.portfolio = res.data || {};
            this.updateUI();
        } catch (err) {
            console.error('Portfolio fetch error:', err);
        }
    },
    
    updateUI() {
        const p = this.data.portfolio;
        if (!p) return;
        
        document.getElementById('portfolio-total').textContent = `$${(p.total || 0).toLocaleString()}`;
        document.getElementById('portfolio-invested').textContent = `$${(p.invested || 0).toLocaleString()}`;
        document.getElementById('portfolio-cash').textContent = `$${(p.cash || 0).toLocaleString()}`;
        
        const pnlEl = document.getElementById('portfolio-pnl');
        const pnl = p.pnl || 0;
        pnlEl.textContent = `${pnl >= 0 ? '+' : ''}$${pnl.toFixed(2)}`;
        pnlEl.className = `summary-value ${pnl >= 0 ? 'positive' : 'negative'}`;
    },
    
    initCharts() {
        const allocCtx = document.getElementById('allocation-chart');
        if (allocCtx) {
            new Chart(allocCtx, {
                type: 'doughnut',
                data: {
                    labels: ['🐰 打兔子', '🐹 打地鼠', '🔮 走着瞧', '👑 跟大哥', '🍀 搭便车'],
                    datasets: [{
                        data: [25, 20, 15, 15, 10],
                        backgroundColor: ['#64748B', '#00D4AA', '#7C3AED', '#F59E0B', '#3B82F6']
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { position: 'bottom' } }
                }
            });
        }
    },
    
    async refresh() {
        await this.fetchData();
        Toast.show('投资组合已刷新', 'success');
    }
};

window.PortfolioPage = PortfolioPage;
