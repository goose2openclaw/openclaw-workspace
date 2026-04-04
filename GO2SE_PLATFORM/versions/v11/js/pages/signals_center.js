/**
 * 信号中心 - 声纳库 + MiroFish可视化
 * P2优先级: 信号中心L2-L3
 */

window.SignalsCenter = {
    sonarLibrary: null,
    mirofishCache: {},
    
    init() {
        this.loadSonarLibrary();
        this.render();
        console.log('📡 信号中心已初始化');
    },
    
    loadSonarLibrary() {
        // 123趋势模型数据
        this.sonarLibrary = {
            trend: {
                name: '趋势类',
                count: 30,
                models: ['EMA5', 'EMA10', 'EMA20', 'EMA50', 'EMA200', 'MA10', 'MA20', 'MA50', 'MA200', 'SMA10', 'SMA20', 'MACD Channel', 'TEMA', 'DEMA', 'Ichimoku', 'Parabolic SAR', 'ZigZag', 'ADX', 'Aroon', 'Momentum', 'ROC', 'TriX', 'DM', 'CCI', 'Detrended', 'KST', 'Mass Index', 'QStick', 'RI', 'TRIX'],
                indicators: ['EMA', 'MA', 'MACD', 'Ichimoku', 'Parabolic SAR']
            },
            momentum: {
                name: '动量类',
                count: 25,
                models: ['RSI6', 'RSI14', 'RSI28', 'StochasticK', 'StochasticD', 'StochasticRSI', 'MACD', 'MACD Signal', 'MACD Histogram', 'Williams %R', 'CCI', 'ROC', 'Momentum', 'RSI Momentum', 'Ultimate', 'Stochastic Momentum', 'RSI Stochastic', 'K振', 'DMI', 'ADX', 'R', 'Williams AD', 'Ultimate Osc', 'Vortex', 'KVO'],
                indicators: ['RSI', 'MACD', 'Stochastic', 'Williams %R', 'CCI']
            },
            volatility: {
                name: '波动类',
                count: 20,
                models: ['BB Upper', 'BB Middle', 'BB Lower', 'ATR', 'NATR', 'Keltner Upper', 'Keltner Lower', 'Donchian Upper', 'Donchian Lower', 'STDDEV', 'Ulcer', 'Choppiness', 'Acceleration', 'Deceleration', ' 历史波动率', 'Future Volatility', 'Bandwidth', '%B', 'Bandwidth %B', 'ATR Trailing'],
                indicators: ['Bollinger Bands', 'ATR', 'Keltner', 'Donchian']
            },
            volume: {
                name: '成交量类',
                count: 15,
                models: ['OBV', 'VWAP', 'Volume MA', 'Volume Profile', 'Accumulation/Distribution', 'Chaikin Money Flow', 'EOM', 'Force Index', 'MFI', 'NVI', 'PVI', 'EMV', 'TVI', 'VPT', 'Volume Oscillator'],
                indicators: ['OBV', 'VWAP', 'Volume Profile', 'MFI']
            },
            reversal: {
                name: '反转类',
                count: 15,
                models: ['RSI Extreme', 'Stochastic Extreme', 'Williams Extreme', 'Bollinger Bounce', 'Pivot Reversal', 'Fibonacci Retracement', 'Pattern Recognition', 'Candle Patterns', 'MACD Divergence', 'RSI Divergence', 'Stochastic Divergence', 'Support/Resistance', 'Trendline Break', 'Gap Reversal', 'Opening Range'],
                indicators: ['RSI', 'Stochastic', 'Bollinger Bands', 'Divergence']
            },
            breakout: {
                name: '通道类',
                count: 10,
                models: ['Donchian Breakout', 'Trendline Break', 'Support Break', 'Resistance Break', 'Channel Break', 'Price Channel', 'Regression Channel', 'Volume Breakout', 'Volatility Breakout', 'Time Segmented'],
                indicators: ['Donchian', 'Trendline', 'Channel']
            },
            other: {
                name: '专用类',
                count: 8,
                models: ['Ichimoku Cloud', 'Heikin Ashi', 'Renko', 'Kagi', 'Point & Figure', 'Line Break', 'Range Bars', 'Variable RC'],
                indicators: ['Ichimoku', 'Heikin Ashi', 'Renko', 'Kagi']
            }
        };
    },
    
    render() {
        const content = `
            <div class="signals-center">
                <div class="page-header">
                    <div class="page-title">
                        <h1>📡 信号中心</h1>
                        <p class="page-desc">123趋势模型声纳库 + MiroFish AI预测</p>
                    </div>
                    <div class="page-actions">
                        <button class="btn btn-primary" onclick="SignalsCenter.runSonarScan()">
                            🔍 全网扫描
                        </button>
                        <button class="btn btn-secondary" onclick="SignalsCenter.runMirofish()">
                            🤖 MiroFish预测
                        </button>
                    </div>
                </div>
                
                <!-- 统计概览 -->
                <div class="signals-stats">
                    <div class="stat-card">
                        <div class="stat-icon">📊</div>
                        <div class="stat-info">
                            <div class="stat-value">${this.getTotalModels()}</div>
                            <div class="stat-label">趋势模型</div>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">📈</div>
                        <div class="stat-info">
                            <div class="stat-value">${this.getActiveSignals()}</div>
                            <div class="stat-label">活跃信号</div>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">🎯</div>
                        <div class="stat-info">
                            <div class="stat-value">${this.getConfidence()}%</div>
                            <div class="stat-label">MiroFish置信度</div>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">⏱️</div>
                        <div class="stat-info">
                            <div class="stat-value">${this.getLastUpdate()}</div>
                            <div class="stat-label">最后更新</div>
                        </div>
                    </div>
                </div>
                
                <!-- MiroFish 预测概览 -->
                <div class="section">
                    <h2>🤖 MiroFish AI预测</h2>
                    <div class="mirofish-overview">
                        ${this.renderMirofishCards()}
                    </div>
                </div>
                
                <!-- 声纳库浏览器 -->
                <div class="section">
                    <h2>📊 声纳库浏览器</h2>
                    <div class="sonar-tabs">
                        ${this.renderSonarTabs()}
                    </div>
                    <div class="sonar-content" id="sonar-content">
                        ${this.renderSonarCategory('trend')}
                    </div>
                </div>
                
                <!-- 123模型详情 -->
                <div class="section">
                    <h2>🔢 123趋势模型详情</h2>
                    ${this.render123Models()}
                </div>
            </div>
        `;
        
        document.getElementById('page-content').innerHTML = content;
    },
    
    getTotalModels() {
        return Object.values(this.sonarLibrary).reduce((sum, cat) => sum + cat.count, 0);
    },
    
    getActiveSignals() {
        return Math.floor(Math.random() * 20) + 10;
    },
    
    getConfidence() {
        return Math.floor(Math.random() * 15) + 80;
    },
    
    getLastUpdate() {
        return new Date().toLocaleTimeString('zh-CN', {hour: '2-digit', minute: '2-digit'});
    },
    
    renderMirofishCards() {
        const predictions = [
            {symbol: 'BTC', signal: 'buy', confidence: 85, bullish: 8, bearish: 2, neutral: 3, price: 68500, change: '+2.3%'},
            {symbol: 'ETH', signal: 'buy', confidence: 78, bullish: 6, bearish: 3, neutral: 4, price: 3800, change: '+1.8%'},
            {symbol: 'SOL', signal: 'hold', confidence: 65, bullish: 4, bearish: 4, neutral: 5, price: 145, change: '-0.5%'},
            {symbol: 'BNB', signal: 'sell', confidence: 72, bullish: 2, bearish: 7, neutral: 4, price: 580, change: '-1.2%'},
            {symbol: 'XRP', signal: 'buy', confidence: 75, bullish: 5, bearish: 3, neutral: 5, price: 0.52, change: '+3.1%'}
        ];
        
        return predictions.map(p => `
            <div class="mirofish-card ${p.signal}">
                <div class="mirofish-header">
                    <span class="symbol">${p.symbol}</span>
                    <span class="signal-badge ${p.signal}">${this.getSignalText(p.signal)}</span>
                    <span class="mirofish-score" title="MiroFish AI置信度">🪿${p.confidence}</span>
                </div>
                
                <!-- 置信度进度条 -->
                <div class="mirofish-confidence">
                    <div class="confidence-bar">
                        <div class="confidence-fill ${p.confidence >= 75 ? 'high' : p.confidence >= 60 ? 'medium' : 'low'}" 
                             style="width: ${p.confidence}%"></div>
                    </div>
                    <span class="confidence-value">${p.confidence}%</span>
                </div>
                
                <!-- 决策理由 -->
                <div class="mirofish-reasoning">
                    <div class="reasoning-title">🤔 决策理由</div>
                    <div class="reasoning-bar">
                        <div class="reasoning-segment bullish" style="width: ${p.bullish * 10}%"></div>
                        <div class="reasoning-segment neutral" style="width: ${p.neutral * 10}%"></div>
                        <div class="reasoning-segment bearish" style="width: ${p.bearish * 10}%"></div>
                    </div>
                    <div class="reasoning-stats">
                        <span class="stat bullish">🟢 ${p.bullish} 看涨</span>
                        <span class="stat neutral">🟡 ${p.neutral} 中性</span>
                        <span class="stat bearish">🔴 ${p.bearish} 看跌</span>
                    </div>
                    <div class="reasoning-conclusion">
                        ${this.getReasoningText(p)}
                    </div>
                </div>
                
                <div class="mirofish-price">
                    <span class="price">$${this.formatPrice(p.price)}</span>
                    <span class="change ${p.change.startsWith('+') ? 'up' : 'down'}">${p.change}</span>
                </div>
            </div>
        `).join('');
    },
    
    getReasoningText(p) {
        const total = p.bullish + p.bearish + p.neutral;
        const bullishPct = Math.round(p.bullish / total * 100);
        const bearishPct = Math.round(p.bearish / total * 100);
        
        if (p.signal === 'buy') {
            return `📈 <strong>${p.bullish}个看涨模型</strong> vs <span class="bearish-text">${p.bearish}个看跌模型</span> → <strong>推荐买入</strong>`;
        } else if (p.signal === 'sell') {
            return `📉 <strong>${p.bearish}个看跌模型</strong> vs <span class="bullish-text">${p.bullish}个看涨模型</span> → <strong>推荐卖出</strong>`;
        } else {
            return `⏸️ <strong>多空分歧</strong> (${p.bullish} vs ${p.bearish}) → <strong>建议观望</strong>`;
        }
    },
    
    getSignalText(signal) {
        const map = {buy: '买入', sell: '卖出', hold: '观望'};
        return map[signal] || signal;
    },
    
    formatPrice(price) {
        if (price < 1) return price.toFixed(4);
        if (price < 100) return price.toFixed(2);
        return price.toLocaleString();
    },
    
    renderSonarTabs() {
        const categories = Object.keys(this.sonarLibrary);
        return categories.map((cat, idx) => `
            <button class="sonar-tab ${idx === 0 ? 'active' : ''}" 
                    onclick="SignalsCenter.showSonarCategory('${cat}')"
                    data-category="${cat}">
                ${this.sonarLibrary[cat].name}
                <span class="tab-count">${this.sonarLibrary[cat].count}</span>
            </button>
        `).join('');
    },
    
    showSonarCategory(category) {
        // 更新tab状态
        document.querySelectorAll('.sonar-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.category === category);
        });
        
        // 更新内容
        document.getElementById('sonar-content').innerHTML = this.renderSonarCategory(category);
    },
    
    renderSonarCategory(category) {
        const cat = this.sonarLibrary[category];
        return `
            <div class="sonar-category">
                <div class="category-header">
                    <h3>${cat.name}</h3>
                    <span class="model-count">${cat.count} 个模型</span>
                </div>
                <div class="model-grid">
                    ${cat.models.slice(0, 12).map(model => `
                        <div class="model-card" onclick="SignalsCenter.showModelDetail('${model}')">
                            <div class="model-name">${model}</div>
                            <div class="model-status active">活跃</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    },
    
    render123Models() {
        return `
            <div class="models-123">
                <div class="model-123-card">
                    <div class="model-number">1</div>
                    <div class="model-content">
                        <h4>趋势确认</h4>
                        <p>EMA/MA确认趋势方向</p>
                        <div class="model-indicators">
                            <span class="indicator">EMA20</span>
                            <span class="indicator">EMA50</span>
                            <span class="indicator">MA200</span>
                        </div>
                    </div>
                </div>
                <div class="model-123-card">
                    <div class="model-number">2</div>
                    <div class="model-content">
                        <h4>信号确认</h4>
                        <p>RSI + MACD + Volume验证</p>
                        <div class="model-indicators">
                            <span class="indicator">RSI14</span>
                            <span class="indicator">MACD</span>
                            <span class="indicator">Volume</span>
                        </div>
                    </div>
                </div>
                <div class="model-123-card">
                    <div class="model-number">3</div>
                    <div class="model-content">
                        <h4>执行信号</h4>
                        <p>买入/卖出/观望</p>
                        <div class="model-indicators">
                            <span class="indicator signal-buy">买入</span>
                            <span class="indicator signal-hold">观望</span>
                            <span class="indicator signal-sell">卖出</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },
    
    showModelDetail(modelName) {
        console.log('查看模型详情:', modelName);
        // TODO: 显示模型详细页面
    },
    
    runSonarScan() {
        console.log('🔍 运行全网扫描');
        // TODO: 调用扫描API
    },
    
    runMirofish() {
        console.log('🤖 运行MiroFish预测');
        // TODO: 调用MiroFish API
    }
};
