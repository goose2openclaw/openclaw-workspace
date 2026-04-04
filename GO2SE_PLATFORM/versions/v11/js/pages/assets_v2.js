/**
 * 资产看板 v2 - L2-L3结构
 * P3优先级: 资产/设置L2-L3
 */

window.AssetsV2 = {
    assets: {
        total: 85000,
        wallets: {
            main: { name: '主钱包', balance: 85000, address: '0x...Main', allocation: 100 },
            rabbit: { name: '打兔子', balance: 25000, address: '0x...Rabbit', allocation: 25 },
            mole: { name: '打地鼠', balance: 17000, address: '0x...Mole', allocation: 20 },
            oracle: { name: '走着瞧', balance: 12750, address: '0x...Oracle', allocation: 15 },
            leader: { name: '跟大哥', balance: 12750, address: '0x...Leader', allocation: 15 },
            hitchhiker: { name: '搭便车', balance: 8500, address: '0x...Hitch', allocation: 10 },
            airdrop: { name: '薅羊毛', balance: 2550, address: '0x...Airdrop', allocation: 3 },
            crowdsource: { name: '穷孩子', balance: 1700, address: '0x...Crowd', allocation: 2 }
        }
    },
    
    holdings: [
        { symbol: 'BTC', name: 'Bitcoin', amount: 0.5, value: 34250, allocation: 40.3, change: 2.3 },
        { symbol: 'ETH', name: 'Ethereum', amount: 5.0, value: 19000, allocation: 22.4, change: 1.8 },
        { symbol: 'BNB', name: 'BNB', amount: 20, value: 11600, allocation: 13.6, change: -0.5 },
        { symbol: 'SOL', name: 'Solana', amount: 50, value: 7250, allocation: 8.5, change: 5.2 },
        { symbol: 'XRP', name: 'Ripple', amount: 10000, value: 5200, allocation: 6.1, change: 3.1 },
        { symbol: 'USDT', name: 'Tether', amount: 7700, value: 7700, allocation: 9.1, change: 0 }
    ],
    
    transactions: [
        { id: 'TX001', type: 'buy', symbol: 'BTC', amount: 0.1, price: 68000, time: '10:30:25', status: 'completed' },
        { id: 'TX002', type: 'sell', symbol: 'ETH', amount: 0.5, price: 3750, time: '09:15:42', status: 'completed' },
        { id: 'TX003', type: 'buy', symbol: 'SOL', amount: 10, price: 140, time: '08:45:18', status: 'pending' }
    ],
    
    init() {
        this.render();
        console.log('💰 资产看板v2已初始化');
    },
    
    render() {
        const content = `
            <div class="assets-page">
                <div class="page-header">
                    <div class="page-title">
                        <h1>💰 资产看板</h1>
                        <p class="page-desc">钱包架构 + 持仓分布 + 交易历史</p>
                    </div>
                    <div class="page-actions">
                        <button class="btn btn-primary" onclick="AssetsV2.showDeposit()">
                            💵 充值
                        </button>
                        <button class="btn btn-secondary" onclick="AssetsV2.showWithdraw()">
                            💸 提现
                        </button>
                    </div>
                </div>
                
                <!-- 总览统计 -->
                <div class="assets-stats">
                    <div class="stat-card highlight">
                        <div class="stat-label">总资产 (USDT)</div>
                        <div class="stat-value">${this.formatNumber(this.assets.total)}</div>
                        <div class="stat-change up">+2.3% (24h)</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">可用</div>
                        <div class="stat-value">${this.formatNumber(this.assets.total * 0.65)}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">持仓中</div>
                        <div class="stat-value">${this.formatNumber(this.assets.total * 0.35)}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">未实现盈亏</div>
                        <div class="stat-value profit">+${this.formatNumber(this.assets.total * 0.08)}</div>
                    </div>
                </div>
                
                <!-- Tab切换 -->
                <div class="assets-tabs">
                    <button class="asset-tab active" data-tab="wallets" onclick="AssetsV2.showTab('wallets')">
                        👛 钱包架构
                    </button>
                    <button class="asset-tab" data-tab="holdings" onclick="AssetsV2.showTab('holdings')">
                        📊 持仓分布
                    </button>
                    <button class="asset-tab" data-tab="history" onclick="AssetsV2.showTab('history')">
                        📜 交易历史
                    </button>
                </div>
                
                <!-- 钱包架构 -->
                <div class="tab-content active" id="tab-wallets">
                    ${this.renderWallets()}
                </div>
                
                <!-- 持仓分布 -->
                <div class="tab-content" id="tab-holdings" style="display:none;">
                    ${this.renderHoldings()}
                </div>
                
                <!-- 交易历史 -->
                <div class="tab-content" id="tab-history" style="display:none;">
                    ${this.renderHistory()}
                </div>
            </div>
        `;
        
        document.getElementById('page-content').innerHTML = content;
    },
    
    renderWallets() {
        const wallets = Object.values(this.assets.wallets);
        const mainWallet = wallets[0];
        const subWallets = wallets.slice(1);
        
        return `
            <div class="wallets-container">
                <!-- 主钱包 -->
                <div class="main-wallet" onclick="AssetsV2.showWalletDetail('main')">
                    <div class="wallet-icon">🏦</div>
                    <div class="wallet-info">
                        <div class="wallet-name">${mainWallet.name}</div>
                        <div class="wallet-address">${mainWallet.address}</div>
                    </div>
                    <div class="wallet-balance">
                        <div class="balance-value">${this.formatNumber(mainWallet.balance)}</div>
                        <div class="balance-label">USDT</div>
                    </div>
                </div>
                
                <!-- 子钱包网格 -->
                <div class="sub-wallets">
                    <div class="section-title">子钱包分配</div>
                    <div class="wallet-grid">
                        ${subWallets.map(w => `
                            <div class="sub-wallet-card" onclick="AssetsV2.showWalletDetail('${w.name.toLowerCase()}')">
                                <div class="wallet-header">
                                    <span class="wallet-name">${w.name}</span>
                                    <span class="wallet-allocation">${w.allocation}%</span>
                                </div>
                                <div class="wallet-balance-small">
                                    ${this.formatNumber(w.balance)} <span class="usdt">USDT</span>
                                </div>
                                <div class="wallet-address-small">${w.address}</div>
                                <div class="wallet-bar">
                                    <div class="wallet-bar-fill" style="width: ${w.allocation * 3}%"></div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    },
    
    renderHoldings() {
        return `
            <div class="holdings-container">
                <!-- 持仓图表 -->
                <div class="holdings-chart">
                    <div class="chart-placeholder">
                        <div class="pie-chart-visual">
                            ${this.renderPieChart()}
                        </div>
                    </div>
                </div>
                
                <!-- 持仓列表 -->
                <div class="holdings-list">
                    ${this.holdings.map(h => `
                        <div class="holding-item">
                            <div class="holding-symbol">
                                <span class="symbol-icon">${this.getSymbolIcon(h.symbol)}</span>
                                <div>
                                    <div class="symbol-name">${h.symbol}</div>
                                    <div class="symbol-full">${h.name}</div>
                                </div>
                            </div>
                            <div class="holding-amount">
                                <div class="amount-value">${h.amount}</div>
                                <div class="amount-usdt">≈ $${this.formatNumber(h.value)}</div>
                            </div>
                            <div class="holding-change ${h.change >= 0 ? 'up' : 'down'}">
                                ${h.change >= 0 ? '+' : ''}${h.change}%
                            </div>
                            <div class="holding-allocation">
                                <div class="allocation-bar">
                                    <div class="allocation-fill" style="width: ${h.allocation * 3}%"></div>
                                </div>
                                <span>${h.allocation}%</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    },
    
    renderPieChart() {
        const colors = ['#ff9500', '#5856d6', '#007aff', '#34c759', '#ff3b30', '#af52de'];
        let startAngle = 0;
        
        return this.holdings.map((h, i) => {
            const angle = (h.allocation / 100) * 360;
            const color = colors[i % colors.length];
            const item = `
                <div class="pie-segment" style="
                    background: conic-gradient(${color} ${startAngle}deg, ${color} ${startAngle + angle}deg, transparent ${startAngle + angle}deg);
                "></div>
            `;
            startAngle += angle;
            return item;
        }).join('');
    },
    
    renderHistory() {
        return `
            <div class="history-container">
                <table class="history-table">
                    <thead>
                        <tr>
                            <th>时间</th>
                            <th>类型</th>
                            <th>币种</th>
                            <th>数量</th>
                            <th>价格</th>
                            <th>状态</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${this.transactions.map(tx => `
                            <tr>
                                <td>${tx.time}</td>
                                <td>
                                    <span class="tx-type ${tx.type}">${tx.type === 'buy' ? '买入' : '卖出'}</span>
                                </td>
                                <td>${tx.symbol}</td>
                                <td>${tx.amount}</td>
                                <td>$${this.formatNumber(tx.price)}</td>
                                <td>
                                    <span class="tx-status ${tx.status}">${tx.status === 'completed' ? '已完成' : '处理中'}</span>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    },
    
    showTab(tabName) {
        document.querySelectorAll('.asset-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.tab === tabName);
        });
        
        document.querySelectorAll('.tab-content').forEach(content => {
            content.style.display = content.id === `tab-${tabName}` ? 'block' : 'none';
        });
    },
    
    showDeposit() {
        console.log('💵 显示充值');
    },
    
    showWithdraw() {
        console.log('💸 显示提现');
    },
    
    showWalletDetail(walletId) {
        console.log('查看钱包详情:', walletId);
    },
    
    getSymbolIcon(symbol) {
        const icons = {
            'BTC': '₿',
            'ETH': 'Ξ',
            'BNB': '◈',
            'SOL': '◎',
            'XRP': '✕',
            'USDT': '₮'
        };
        return icons[symbol] || '◯';
    },
    
    formatNumber(num) {
        return num.toLocaleString('en-US', { maximumFractionDigits: 2 });
    }
};
