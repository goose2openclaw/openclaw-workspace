// GO2SE v11 - Signals Page Module
const SignalsPage = {
    name: 'signals',
    
    data: {
        signals: [],
        filters: { strategy: 'all', signal: 'all' },
        sortBy: 'confidence',
        sortOrder: 'desc'
    },
    
    async load() {
        const container = document.getElementById('page-content');
        container.innerHTML = this.template();
        await this.fetchData();
        this.initEventListeners();
    },
    
    template() {
        return `
        <div class="signals-page">
            <div class="page-header">
                <h1>🎯 信号列表</h1>
                <div class="header-actions">
                    <select id="filter-strategy" class="filter-select">
                        <option value="all">全部策略</option>
                        <option value="rabbit">🐰 打兔子</option>
                        <option value="mole">🐹 打地鼠</option>
                        <option value="oracle">🔮 走着瞧</option>
                        <option value="leader">👑 跟大哥</option>
                    </select>
                    <select id="filter-signal" class="filter-select">
                        <option value="all">全部信号</option>
                        <option value="buy">买入</option>
                        <option value="sell">卖出</option>
                        <option value="hold">观望</option>
                    </select>
                    <button class="btn-refresh" onclick="SignalsPage.refresh()">
                        <span>🔄</span> 刷新
                    </button>
                </div>
            </div>
            
            <div class="signals-table-container">
                <table class="signals-table">
                    <thead>
                        <tr>
                            <th>时间</th>
                            <th>交易对</th>
                            <th>策略</th>
                            <th>信号</th>
                            <th>置信度</th>
                            <th>原因</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody id="signals-tbody">
                        <tr><td colspan="7" class="loading">加载中...</td></tr>
                    </tbody>
                </table>
            </div>
            
            <div class="pagination" id="signals-pagination"></div>
        </div>
        `;
    },
    
    async fetchData() {
        try {
            const res = await API.get('/api/signals?limit=50');
            this.data.signals = res.data || [];
            this.renderTable();
        } catch (err) {
            console.error('Signals fetch error:', err);
            document.getElementById('signals-tbody').innerHTML = 
                '<tr><td colspan="7" class="error">加载失败</td></tr>';
        }
    },
    
    renderTable() {
        const tbody = document.getElementById('signals-tbody');
        if (!tbody) return;
        
        let filtered = this.data.signals;
        
        if (this.data.filters.strategy !== 'all') {
            filtered = filtered.filter(s => s.strategy === this.data.filters.strategy);
        }
        if (this.data.filters.signal !== 'all') {
            filtered = filtered.filter(s => s.signal === this.data.filters.signal);
        }
        
        filtered.sort((a, b) => {
            const aVal = a[this.data.sortBy] || 0;
            const bVal = b[this.data.sortBy] || 0;
            return this.data.sortOrder === 'desc' ? bVal - aVal : aVal - bVal;
        });
        
        tbody.innerHTML = filtered.length ? filtered.map(s => `
            <tr class="signal-row signal-${s.signal}">
                <td>${new Date(s.created_at).toLocaleString()}</td>
                <td><strong>${s.symbol}</strong></td>
                <td>${this.getStrategyBadge(s.strategy)}</td>
                <td><span class="signal-badge signal-${s.signal}">${s.signal.toUpperCase()}</span></td>
                <td>
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: ${s.confidence * 10}%"></div>
                        <span class="confidence-text">${(s.confidence * 10).toFixed(1)}%</span>
                    </div>
                </td>
                <td class="reason">${s.reason || '-'}</td>
                <td>
                    <button class="btn-small" onclick="SignalsPage.viewDetail(${s.id})">详情</button>
                </td>
            </tr>
        `).join('') : '<tr><td colspan="7" class="empty">暂无信号</td></tr>';
    },
    
    getStrategyBadge(strategy) {
        const badges = {
            rabbit: '🐰 打兔子',
            mole: '🐹 打地鼠',
            oracle: '🔮 走着瞧',
            leader: '👑 跟大哥',
            hitchhiker: '🍀 搭便车',
            airdrop: '💰 薅羊毛',
            crowdsource: '👶 穷孩子'
        };
        return badges[strategy] || strategy;
    },
    
    viewDetail(id) {
        window.location.hash = `signals-detail-${id}`;
    },
    
    initEventListeners() {
        document.getElementById('filter-strategy')?.addEventListener('change', e => {
            this.data.filters.strategy = e.target.value;
            this.renderTable();
        });
        
        document.getElementById('filter-signal')?.addEventListener('change', e => {
            this.data.filters.signal = e.target.value;
            this.renderTable();
        });
    },
    
    async refresh() {
        await this.fetchData();
        Toast.show('信号已刷新', 'success');
    }
};

window.SignalsPage = SignalsPage;
