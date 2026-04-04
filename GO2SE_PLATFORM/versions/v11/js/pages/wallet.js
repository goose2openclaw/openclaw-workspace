// GO2SE v11 - Wallet Page Module
const WalletPage = {
    name: 'wallet',
    
    data: {
        wallets: [],
        transfers: []
    },
    
    async load() {
        const container = document.getElementById('page-content');
        container.innerHTML = this.template();
        await this.fetchData();
        this.initEventListeners();
    },
    
    template() {
        return `
        <div class="wallet-page">
            <div class="page-header">
                <h1>👛 钱包架构</h1>
                <div class="header-actions">
                    <button class="btn-primary" onclick="WalletPage.showTransfer()">
                        💸 转账
                    </button>
                </div>
            </div>
            
            <div class="wallet-overview">
                <div class="wallet-card main-wallet">
                    <div class="wallet-icon">🏦</div>
                    <div class="wallet-info">
                        <div class="wallet-name">主钱包</div>
                        <div class="wallet-balance" id="main-balance">$0.00</div>
                    </div>
                </div>
            </div>
            
            <div class="sub-wallets">
                <h3>子钱包分配</h3>
                <div class="wallets-grid" id="wallets-grid">
                    <div class="loading">加载中...</div>
                </div>
            </div>
            
            <div class="transfer-form hidden" id="transfer-form">
                <h3>💸 转账</h3>
                <div class="form-group">
                    <label>从</label>
                    <select id="transfer-from"></select>
                </div>
                <div class="form-group">
                    <label>到</label>
                    <select id="transfer-to"></select>
                </div>
                <div class="form-group">
                    <label>金额</label>
                    <input type="number" id="transfer-amount" step="0.01" min="0">
                </div>
                <div class="form-actions">
                    <button class="btn-secondary" onclick="WalletPage.hideTransfer()">取消</button>
                    <button class="btn-primary" onclick="WalletPage.executeTransfer()">确认</button>
                </div>
            </div>
            
            <div class="card history-card">
                <h3>📜 转账历史</h3>
                <div id="transfer-history" class="history-list">
                    <div class="empty">暂无记录</div>
                </div>
            </div>
        </div>
        `;
    },
    
    async fetchData() {
        try {
            const res = await API.get('/api/performance');
            this.data.wallets = this.buildWallets(res.data);
            this.renderWallets();
        } catch (err) {
            console.error('Wallet fetch error:', err);
        }
    },
    
    buildWallets(performance) {
        const tools = performance?.investment_tools || {};
        return [
            { id: 'main', name: '主钱包', icon: '🏦', balance: performance?.total_capital || 100000, color: '#00D4AA' },
            { id: 'rabbit', name: '🐰 打兔子', icon: '🐰', balance: tools.rabbit?.allocation || 0, color: '#64748B' },
            { id: 'mole', name: '🐹 打地鼠', icon: '🐹', balance: tools.mole?.allocation || 0, color: '#00D4AA' },
            { id: 'oracle', name: '🔮 走着瞧', icon: '🔮', balance: tools.oracle?.allocation || 0, color: '#7C3AED' },
            { id: 'leader', name: '👑 跟大哥', icon: '👑', balance: tools.leader?.allocation || 0, color: '#F59E0B' },
            { id: 'hitchhiker', name: '🍀 搭便车', icon: '🍀', balance: tools.hitchhiker?.allocation || 0, color: '#3B82F6' }
        ];
    },
    
    renderWallets() {
        const grid = document.getElementById('wallets-grid');
        if (!grid) return;
        
        const main = this.data.wallets.find(w => w.id === 'main');
        document.getElementById('main-balance').textContent = `$${(main?.balance || 0).toLocaleString()}`;
        
        grid.innerHTML = this.data.wallets.filter(w => w.id !== 'main').map(w => `
            <div class="wallet-card sub-wallet" data-id="${w.id}">
                <div class="wallet-icon">${w.icon}</div>
                <div class="wallet-info">
                    <div class="wallet-name">${w.name}</div>
                    <div class="wallet-balance">$${w.balance.toLocaleString()}</div>
                </div>
                <div class="wallet-actions">
                    <button class="btn-small" onclick="WalletPage.initTransfer('${w.id}')">转账</button>
                </div>
            </div>
        `).join('');
    },
    
    showTransfer() {
        document.getElementById('transfer-form')?.classList.remove('hidden');
    },
    
    hideTransfer() {
        document.getElementById('transfer-form')?.classList.add('hidden');
    },
    
    initTransfer(toolId) {
        const fromSelect = document.getElementById('transfer-from');
        const toSelect = document.getElementById('transfer-to');
        
        const options = this.data.wallets.map(w => 
            `<option value="${w.id}">${w.name}</option>`
        ).join('');
        
        if (fromSelect) fromSelect.innerHTML = options;
        if (toSelect) toSelect.innerHTML = options;
        
        this.showTransfer();
    },
    
    async executeTransfer() {
        const from = document.getElementById('transfer-from')?.value;
        const to = document.getElementById('transfer-to')?.value;
        const amount = parseFloat(document.getElementById('transfer-amount')?.value || 0);
        
        if (!from || !to || !amount) {
            Toast.show('请填写完整信息', 'error');
            return;
        }
        
        Toast.show('转账功能开发中', 'info');
        this.hideTransfer();
    }
};

window.WalletPage = WalletPage;
