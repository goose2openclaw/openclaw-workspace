/**
 * 🪿 市场介绍模块 v1.8.7
 * 北斗七鑫7+2工具市场机会展示
 */

const MarketModule = {
    API_BASE: '/api/market-module',
    cache: {},
    refreshInterval: null,

    /**
     * 初始化市场模块
     */
    async init() {
        console.log('📊 MarketModule initializing...');
        await this.loadAllTools();
        this.startAutoRefresh();
    },

    /**
     * 加载所有工具市场数据
     */
    async loadAllTools() {
        try {
            const response = await fetch(`${this.API_BASE}/tools`);
            const data = await response.json();
            this.cache.tools = data;
            this.renderTools(data.tools);
            return data;
        } catch (error) {
            console.error('❌ Failed to load tools:', error);
            return null;
        }
    },

    /**
     * 加载策略胜率
     */
    async loadStrategies() {
        try {
            const response = await fetch(`${this.API_BASE}/strategies`);
            const data = await response.json();
            this.cache.strategies = data;
            this.renderStrategies(data.strategies);
            return data;
        } catch (error) {
            console.error('❌ Failed to load strategies:', error);
            return null;
        }
    },

    /**
     * 加载Oracle热点
     */
    async loadOracleHot() {
        try {
            const response = await fetch(`${this.API_BASE}/oracle/hot`);
            const data = await response.json();
            this.cache.oracleHot = data;
            this.renderOracleHot(data);
            return data;
        } catch (error) {
            console.error('❌ Failed to load oracle hot:', error);
            return null;
        }
    },

    /**
     * 加载所有赚钱机会
     */
    async loadOpportunities() {
        try {
            const response = await fetch(`${this.API_BASE}/opportunities`);
            const data = await response.json();
            this.cache.opportunities = data;
            this.renderOpportunities(data.opportunities);
            return data;
        } catch (error) {
            console.error('❌ Failed to load opportunities:', error);
            return null;
        }
    },

    /**
     * 渲染工具卡片
     */
    renderTools(tools) {
        const container = document.getElementById('market-tools-grid');
        if (!container) return;

        container.innerHTML = tools.map(tool => `
            <div class="market-tool-card" data-tool="${tool.tool_id}">
                <div class="tool-header">
                    <span class="tool-emoji">${tool.emoji}</span>
                    <div class="tool-info">
                        <h3>${tool.tool_name}</h3>
                        <span class="tool-position">${tool.position_pct}%仓位</span>
                    </div>
                    <button class="btn-more" onclick="MarketModule.showToolDetail('${tool.tool_id}')">
                        查看更多 →
                    </button>
                </div>
                <p class="tool-description">${tool.description}</p>
                <div class="tool-opportunities">
                    ${tool.opportunities.length > 0 ? tool.opportunities.slice(0, 5).map(opp => `
                        <div class="opportunity-item ${opp.action}" onclick="MarketModule.showOrderDialog('${opp.symbol}', '${opp.action}', '${tool.tool_id}')">
                            <span class="opp-symbol">${opp.symbol}</span>
                            <span class="opp-price">$${this.formatPrice(opp.price)}</span>
                            <span class="opp-change ${opp.change_24h >= 0 ? 'positive' : 'negative'}">
                                ${opp.change_24h >= 0 ? '+' : ''}${opp.change_24h.toFixed(2)}%
                            </span>
                            <span class="opp-signal ${opp.signal.toLowerCase()}">${opp.signal}</span>
                        </div>
                    `).join('') : '<div class="no-opportunities">暂无实时机会</div>'}
                </div>
            </div>
        `).join('');
    },

    /**
     * 渲染策略胜率
     */
    renderStrategies(strategies) {
        const container = document.getElementById('strategies-list');
        if (!container) return;

        container.innerHTML = strategies.map(s => `
            <div class="strategy-item">
                <div class="strategy-name">${s.name}</div>
                <div class="strategy-winrate">
                    <div class="winrate-bar" style="width: ${s.win_rate}%"></div>
                    <span>${s.win_rate}%</span>
                </div>
                <div class="strategy-meta">
                    <span>${s.total_trades}笔交易</span>
                    <span>平均${s.avg_profit}%</span>
                </div>
            </div>
        `).join('');
    },

    /**
     * 渲染Oracle热点
     */
    renderOracleHot(data) {
        const container = document.getElementById('oracle-hot-list');
        if (!container) return;

        container.innerHTML = `
            <div class="sentiment-badge ${data.overall_sentiment.toLowerCase()}">${data.overall_sentiment}</div>
            ${data.hot_info.map(hot => `
                <div class="hot-item">
                    <span class="hot-topic">${hot.topic}</span>
                    <span class="hot-confidence">${hot.confidence.toFixed(1)}%</span>
                    <span class="hot-source">${hot.source}</span>
                </div>
            `).join('')}
        `;
    },

    /**
     * 渲染赚钱机会
     */
    renderOpportunities(opportunities) {
        const container = document.getElementById('opportunities-list');
        if (!container) return;

        container.innerHTML = opportunities.map(opp => `
            <div class="opportunity-row ${opp.action}" onclick="MarketModule.showOrderDialog('${opp.symbol}', '${opp.action}', 'rabbit')">
                <span class="opp-symbol">${opp.symbol}</span>
                <span class="opp-category">${opp.category}</span>
                <span class="opp-price">$${this.formatPrice(opp.price)}</span>
                <span class="opp-change ${opp.change_24h >= 0 ? 'positive' : 'negative'}">
                    ${opp.change_24h >= 0 ? '+' : ''}${opp.change_24h.toFixed(2)}%
                </span>
                <span class="opp-signal ${opp.signal.toLowerCase()}">${opp.signal}</span>
                <span class="opp-confidence">${opp.confidence.toFixed(1)}%</span>
            </div>
        `).join('');
    },

    /**
     * 显示工具详情
     */
    async showToolDetail(toolId) {
        try {
            const response = await fetch(`${this.API_BASE}/tool/${toolId}`);
            const data = await response.json();
            
            // 显示详情弹窗
            this.showModal(`
                <div class="tool-detail-modal">
                    <h2>${data.emoji} ${data.tool_name}</h2>
                    <p>${data.description}</p>
                    <p>仓位配置: ${data.position_pct}%</p>
                    <h3>全部机会 (${data.total_opportunities})</h3>
                    <div class="opportunities-full">
                        ${data.opportunities.map(opp => `
                            <div class="opp-row ${opp.action}" onclick="MarketModule.showOrderDialog('${opp.symbol}', '${opp.action}', '${toolId}')">
                                <span>${opp.symbol}</span>
                                <span>$${this.formatPrice(opp.price)}</span>
                                <span class="${opp.change_24h >= 0 ? 'positive' : 'negative'}">
                                    ${opp.change_24h >= 0 ? '+' : ''}${opp.change_24h.toFixed(2)}%
                                </span>
                                <span>${opp.signal}</span>
                                <button class="btn-trade">交易</button>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `);
        } catch (error) {
            console.error('❌ Failed to load tool detail:', error);
        }
    },

    /**
     * 显示订单对话框
     */
    showOrderDialog(symbol, action, tool) {
        const actionText = action === 'buy' ? '买入' : action === 'sell' ? '卖出' : '观望';
        const actionColor = action === 'buy' ? 'green' : action === 'sell' ? 'red' : 'gray';
        
        this.showModal(`
            <div class="order-dialog">
                <h2>📝 订单确认</h2>
                <div class="order-info">
                    <div class="order-row">
                        <span>币种:</span>
                        <strong>${symbol}</strong>
                    </div>
                    <div class="order-row">
                        <span>操作:</span>
                        <strong class="${actionColor}">${actionText}</strong>
                    </div>
                    <div class="order-row">
                        <span>工具:</span>
                        <strong>${tool}</strong>
                    </div>
                </div>
                <div class="order-form">
                    <label>数量:</label>
                    <input type="number" id="order-amount" value="1" min="0.001" step="0.001">
                </div>
                <div class="order-actions">
                    <button class="btn-confirm" onclick="MarketModule.confirmOrder('${symbol}', '${action}', '${tool}')">
                        ✅ 确认
                    </button>
                    <button class="btn-cancel" onclick="MarketModule.closeModal()">
                        取消
                    </button>
                </div>
            </div>
        `);
    },

    /**
     * 确认订单
     */
    async confirmOrder(symbol, action, tool) {
        const amount = document.getElementById('order-amount').value;
        
        try {
            const response = await fetch(
                `${this.API_BASE}/order/preview?symbol=${symbol}&action=${action}&amount=${amount}&tool=${tool}`
            );
            const data = await response.json();
            
            // 显示预览
            this.showModal(`
                <div class="order-preview">
                    <h2>✅ 订单预览</h2>
                    <div class="preview-info">
                        <p>币种: <strong>${data.symbol}</strong></p>
                        <p>价格: <strong>$${this.formatPrice(data.price)}</strong></p>
                        <p>数量: <strong>${data.amount}</strong></p>
                        <p>总计: <strong>$${this.formatPrice(data.total)}</strong></p>
                        <p>预计手续费: <strong>$${data.fee_estimate.toFixed(2)}</strong></p>
                    </div>
                    <div class="preview-actions">
                        <button class="btn-execute" onclick="MarketModule.executeOrder('${symbol}', '${action}', ${amount}, '${tool}')">
                            🚀 执行交易
                        </button>
                        <button class="btn-back" onclick="MarketModule.showOrderDialog('${symbol}', '${action}', '${tool}')">
                            返回修改
                        </button>
                    </div>
                </div>
            `);
        } catch (error) {
            console.error('❌ Failed to preview order:', error);
            alert('订单预览失败，请重试');
        }
    },

    /**
     * 执行订单
     */
    async executeOrder(symbol, action, amount, tool) {
        // 调用实际交易API
        try {
            const response = await fetch('/api/trading/order', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({symbol, action, amount, tool})
            });
            
            this.showModal(`
                <div class="order-result success">
                    <h2>✅ 订单已提交</h2>
                    <p>${symbol} ${action === 'buy' ? '买入' : '卖出'} ${amount}</p>
                    <button onclick="MarketModule.closeModal()">关闭</button>
                </div>
            `);
        } catch (error) {
            this.showModal(`
                <div class="order-result error">
                    <h2>❌ 订单失败</h2>
                    <p>${error.message}</p>
                    <button onclick="MarketModule.closeModal()">关闭</button>
                </div>
            `);
        }
    },

    /**
     * 显示弹窗
     */
    showModal(content) {
        let modal = document.getElementById('market-modal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'market-modal';
            modal.className = 'market-modal';
            document.body.appendChild(modal);
        }
        
        modal.innerHTML = `
            <div class="modal-content">
                <button class="modal-close" onclick="MarketModule.closeModal()">×</button>
                ${content}
            </div>
        `;
        modal.style.display = 'flex';
    },

    /**
     * 关闭弹窗
     */
    closeModal() {
        const modal = document.getElementById('market-modal');
        if (modal) modal.style.display = 'none';
    },

    /**
     * 格式化价格
     */
    formatPrice(price) {
        if (price >= 1000) return price.toLocaleString('en-US', {maximumFractionDigits: 2});
        if (price >= 1) return price.toFixed(2);
        if (price >= 0.01) return price.toFixed(4);
        return price.toFixed(6);
    },

    /**
     * 启动自动刷新
     */
    startAutoRefresh() {
        // 每30秒刷新一次
        this.refreshInterval = setInterval(() => {
            this.loadAllTools();
        }, 30000);
    },

    /**
     * 停止自动刷新
     */
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
    }
};

// 自动初始化
document.addEventListener('DOMContentLoaded', () => {
    MarketModule.init();
});
