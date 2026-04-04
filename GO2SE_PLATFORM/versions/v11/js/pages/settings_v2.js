/**
 * 系统设置 v2 - L2-L3结构
 * P3优先级: 资产/设置L2-L3
 */

window.SettingsV2 = {
    currentSection: 'general',
    
    settings: {
        general: {
            language: 'zh-CN',
            timezone: 'Asia/Shanghai',
            theme: 'dark',
            notifications: true,
            sound: false
        },
        api: {
            binance: { key: '****', secret: '****', status: 'connected' },
            okx: { key: '****', secret: '****', status: 'connected' },
            polymarket: { key: '****', secret: '****', status: 'connected' }
        },
        risk: {
            maxPosition: 80,
            dailyLossLimit: 15,
            singleTradeRisk: 5,
            stopLoss: 8,
            takeProfit: 15,
            circuitBreaker: true,
            autoHedge: false
        },
        strategies: {
            rabbit: { enabled: true, allocation: 25, maxConcurrent: 5 },
            mole: { enabled: true, allocation: 20, maxConcurrent: 10 },
            oracle: { enabled: true, allocation: 15, maxConcurrent: 3 },
            leader: { enabled: true, allocation: 15, maxConcurrent: 3 },
            hitchhiker: { enabled: false, allocation: 10, maxConcurrent: 5 },
            airdrop: { enabled: true, allocation: 3, maxConcurrent: 20 },
            crowdsource: { enabled: true, allocation: 2, maxConcurrent: 10 }
        }
    },
    
    init() {
        this.render();
        console.log('⚙️ 系统设置v2已初始化');
    },
    
    render() {
        const content = `
            <div class="settings-page">
                <div class="page-header">
                    <div class="page-title">
                        <h1>⚙️ 系统设置</h1>
                        <p class="page-desc">配置API连接、风控规则、策略参数</p>
                    </div>
                </div>
                
                <!-- 设置Tab -->
                <div class="settings-tabs">
                    <button class="settings-tab active" data-section="general" onclick="SettingsV2.showSection('general')">
                        🎛️ 通用
                    </button>
                    <button class="settings-tab" data-section="api" onclick="SettingsV2.showSection('api')">
                        🔑 API配置
                    </button>
                    <button class="settings-tab" data-section="risk" onclick="SettingsV2.showSection('risk')">
                        🛡️ 风控规则
                    </button>
                    <button class="settings-tab" data-section="strategies" onclick="SettingsV2.showSection('strategies')">
                        🎯 策略配置
                    </button>
                    <button class="settings-tab" data-section="notifications" onclick="SettingsV2.showSection('notifications')">
                        🔔 通知
                    </button>
                </div>
                
                <!-- 通用设置 -->
                <div class="settings-content active" id="section-general">
                    ${this.renderGeneral()}
                </div>
                
                <!-- API配置 -->
                <div class="settings-content" id="section-api" style="display:none;">
                    ${this.renderAPI()}
                </div>
                
                <!-- 风控规则 -->
                <div class="settings-content" id="section-risk" style="display:none;">
                    ${this.renderRisk()}
                </div>
                
                <!-- 策略配置 -->
                <div class="settings-content" id="section-strategies" style="display:none;">
                    ${this.renderStrategies()}
                </div>
                
                <!-- 通知设置 -->
                <div class="settings-content" id="section-notifications" style="display:none;">
                    ${this.renderNotifications()}
                </div>
            </div>
        `;
        
        document.getElementById('page-content').innerHTML = content;
    },
    
    showSection(sectionName) {
        document.querySelectorAll('.settings-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.section === sectionName);
        });
        
        document.querySelectorAll('.settings-content').forEach(content => {
            content.style.display = content.id === `section-${sectionName}` ? 'block' : 'none';
        });
        
        this.currentSection = sectionName;
    },
    
    renderGeneral() {
        const s = this.settings.general;
        return `
            <div class="settings-section">
                <h2>通用设置</h2>
                
                <div class="setting-item">
                    <div class="setting-label">
                        <div class="setting-name">语言</div>
                        <div class="setting-desc">选择界面显示语言</div>
                    </div>
                    <select class="setting-input" onchange="SettingsV2.updateSetting('general', 'language', this.value)">
                        <option value="zh-CN" ${s.language === 'zh-CN' ? 'selected' : ''}>中文</option>
                        <option value="en-US" ${s.language === 'en-US' ? 'selected' : ''}>English</option>
                    </select>
                </div>
                
                <div class="setting-item">
                    <div class="setting-label">
                        <div class="setting-name">时区</div>
                        <div class="setting-desc">交易和日志的时间基准</div>
                    </div>
                    <select class="setting-input">
                        <option value="Asia/Shanghai" selected>Asia/Shanghai (UTC+8)</option>
                        <option value="UTC">UTC</option>
                    </select>
                </div>
                
                <div class="setting-item">
                    <div class="setting-label">
                        <div class="setting-name">主题</div>
                        <div class="setting-desc">界面颜色方案</div>
                    </div>
                    <select class="setting-input">
                        <option value="dark" selected>🌙 暗色</option>
                        <option value="light">☀️ 亮色</option>
                    </select>
                </div>
                
                <div class="setting-item">
                    <div class="setting-label">
                        <div class="setting-name">通知</div>
                        <div class="setting-desc">交易和风控通知推送</div>
                    </div>
                    <label class="toggle">
                        <input type="checkbox" ${s.notifications ? 'checked' : ''} onchange="SettingsV2.updateSetting('general', 'notifications', this.checked)">
                        <span class="toggle-slider"></span>
                    </label>
                </div>
                
                <div class="setting-item">
                    <div class="setting-label">
                        <div class="setting-name">声音提示</div>
                        <div class="setting-desc">信号和交易的声音提醒</div>
                    </div>
                    <label class="toggle">
                        <input type="checkbox" ${s.sound ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                    </label>
                </div>
            </div>
        `;
    },
    
    renderAPI() {
        const apis = this.settings.api;
        return `
            <div class="settings-section">
                <h2>交易所API配置</h2>
                <p class="section-desc">配置各交易所API密钥，用于交易和获取市场数据</p>
                
                ${Object.entries(apis).map(([name, api]) => `
                    <div class="api-card">
                        <div class="api-header">
                            <div class="api-exchange">${this.getExchangeName(name)}</div>
                            <div class="api-status ${api.status}">
                                <span class="status-dot"></span>
                                ${api.status === 'connected' ? '已连接' : '未连接'}
                            </div>
                        </div>
                        <div class="api-keys">
                            <div class="api-key-item">
                                <span class="key-label">API Key</span>
                                <span class="key-value">${api.key}</span>
                            </div>
                            <div class="api-key-item">
                                <span class="key-label">Secret</span>
                                <span class="key-value">${api.secret}</span>
                            </div>
                        </div>
                        <div class="api-actions">
                            <button class="btn btn-secondary btn-sm" onclick="SettingsV2.testAPI('${name}')">🧪 测试</button>
                            <button class="btn btn-secondary btn-sm" onclick="SettingsV2.editAPI('${name}')">✏️ 编辑</button>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    },
    
    renderRisk() {
        const r = this.settings.risk;
        return `
            <div class="settings-section">
                <h2>风控规则配置</h2>
                <p class="section-desc">设置交易风控参数，保护资金安全</p>
                
                <div class="risk-rules">
                    <div class="risk-card">
                        <div class="risk-header">
                            <span class="risk-icon">📊</span>
                            <span class="risk-name">仓位限制</span>
                        </div>
                        <div class="risk-value">
                            <input type="number" class="risk-input" value="${r.maxPosition}" min="0" max="100">
                            <span class="risk-unit">%</span>
                        </div>
                        <div class="risk-desc">总仓位不超过资产</div>
                    </div>
                    
                    <div class="risk-card">
                        <div class="risk-header">
                            <span class="risk-icon">📉</span>
                            <span class="risk-name">日内熔断</span>
                        </div>
                        <div class="risk-value">
                            <input type="number" class="risk-input" value="${r.dailyLossLimit}" min="0" max="100">
                            <span class="risk-unit">%</span>
                        </div>
                        <div class="risk-desc">日亏损超过停止交易</div>
                    </div>
                    
                    <div class="risk-card">
                        <div class="risk-header">
                            <span class="risk-icon">⚡</span>
                            <span class="risk-name">单笔风险</span>
                        </div>
                        <div class="risk-value">
                            <input type="number" class="risk-input" value="${r.singleTradeRisk}" min="0" max="100">
                            <span class="risk-unit">%</span>
                        </div>
                        <div class="risk-desc">单笔交易最大风险</div>
                    </div>
                    
                    <div class="risk-card">
                        <div class="risk-header">
                            <span class="risk-icon">🛑</span>
                            <span class="risk-name">止损</span>
                        </div>
                        <div class="risk-value">
                            <input type="number" class="risk-input" value="${r.stopLoss}" min="0" max="100">
                            <span class="risk-unit">%</span>
                        </div>
                        <div class="risk-desc">自动止损阈值</div>
                    </div>
                    
                    <div class="risk-card">
                        <div class="risk-header">
                            <span class="risk-icon">🎯</span>
                            <span class="risk-name">止盈</span>
                        </div>
                        <div class="risk-value">
                            <input type="number" class="risk-input" value="${r.takeProfit}" min="0" max="100">
                            <span class="risk-unit">%</span>
                        </div>
                        <div class="risk-desc">自动止盈阈值</div>
                    </div>
                    
                    <div class="risk-card">
                        <div class="risk-header">
                            <span class="risk-icon">🔒</span>
                            <span class="risk-name">熔断机制</span>
                        </div>
                        <label class="toggle">
                            <input type="checkbox" ${r.circuitBreaker ? 'checked' : ''}>
                            <span class="toggle-slider"></span>
                        </label>
                        <div class="risk-desc">异常时自动熔断</div>
                    </div>
                </div>
                
                <button class="btn btn-primary" onclick="SettingsV2.saveRiskRules()">
                    💾 保存风控规则
                </button>
            </div>
        `;
    },
    
    renderStrategies() {
        const strategies = this.settings.strategies;
        return `
            <div class="settings-section">
                <h2>策略配置</h2>
                <p class="section-desc">启用/禁用各工具，调整仓位分配</p>
                
                <div class="strategies-grid">
                    ${Object.entries(strategies).map(([id, strategy]) => `
                        <div class="strategy-config-card">
                            <div class="strategy-header">
                                <span class="strategy-icon">${this.getToolIcon(id)}</span>
                                <span class="strategy-name">${this.getToolName(id)}</span>
                                <label class="toggle">
                                    <input type="checkbox" ${strategy.enabled ? 'checked' : ''} onchange="SettingsV2.toggleStrategy('${id}', this.checked)">
                                    <span class="toggle-slider"></span>
                                </label>
                            </div>
                            
                            <div class="strategy-params">
                                <div class="param-item">
                                    <span class="param-label">仓位</span>
                                    <div class="param-value">
                                        <input type="number" class="param-input" value="${strategy.allocation}" min="0" max="100" ${!strategy.enabled ? 'disabled' : ''}>
                                        <span>%</span>
                                    </div>
                                </div>
                                <div class="param-item">
                                    <span class="param-label">最大并发</span>
                                    <div class="param-value">
                                        <input type="number" class="param-input" value="${strategy.maxConcurrent}" min="1" max="50" ${!strategy.enabled ? 'disabled' : ''}>
                                        <span>个</span>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="strategy-status">
                                <span class="status-badge ${strategy.enabled ? 'active' : 'inactive'}">
                                    ${strategy.enabled ? '已启用' : '已禁用'}
                                </span>
                            </div>
                        </div>
                    `).join('')}
                </div>
                
                <button class="btn btn-primary" onclick="SettingsV2.saveStrategies()">
                    💾 保存策略配置
                </button>
            </div>
        `;
    },
    
    renderNotifications() {
        return `
            <div class="settings-section">
                <h2>通知设置</h2>
                <p class="section-desc">配置各类通知的接收方式和阈值</p>
                
                <div class="notification-rules">
                    <div class="notification-item">
                        <div class="notification-info">
                            <span class="notification-icon">📈</span>
                            <div>
                                <div class="notification-name">交易执行</div>
                                <div class="notification-desc">买卖单成交时通知</div>
                            </div>
                        </div>
                        <label class="toggle">
                            <input type="checkbox" checked>
                            <span class="toggle-slider"></span>
                        </label>
                    </div>
                    
                    <div class="notification-item">
                        <div class="notification-info">
                            <span class="notification-icon">⚠️</span>
                            <div>
                                <div class="notification-name">风险预警</div>
                                <div class="notification-desc">仓位/波动超阈值时通知</div>
                            </div>
                        </div>
                        <label class="toggle">
                            <input type="checkbox" checked>
                            <span class="toggle-slider"></span>
                        </label>
                    </div>
                    
                    <div class="notification-item">
                        <div class="notification-info">
                            <span class="notification-icon">🔔</span>
                            <div>
                                <div class="notification-name">信号提示</div>
                                <div class="notification-desc">新交易信号时通知</div>
                            </div>
                        </div>
                        <label class="toggle">
                            <input type="checkbox" checked>
                            <span class="toggle-slider"></span>
                        </label>
                    </div>
                    
                    <div class="notification-item">
                        <div class="notification-info">
                            <span class="notification-icon">💰</span>
                            <div>
                                <div class="notification-name">盈亏报告</div>
                                <div class="notification-desc">每日收益总结</div>
                            </div>
                        </div>
                        <label class="toggle">
                            <input type="checkbox">
                            <span class="toggle-slider"></span>
                        </label>
                    </div>
                </div>
            </div>
        `;
    },
    
    getExchangeName(name) {
        const names = { binance: 'Binance', okx: 'OKX', polymarket: 'Polymarket' };
        return names[name] || name;
    },
    
    getToolIcon(tool) {
        const icons = { rabbit: '🐰', mole: '🐹', oracle: '🔮', leader: '👑', hitchhiker: '🍀', airdrop: '💰', crowdsource: '👶' };
        return icons[tool] || '🎯';
    },
    
    getToolName(tool) {
        const names = { rabbit: '打兔子', mole: '打地鼠', oracle: '走着瞧', leader: '跟大哥', hitchhiker: '搭便车', airdrop: '薅羊毛', crowdsource: '穷孩子' };
        return names[tool] || tool;
    },
    
    updateSetting(category, key, value) {
        this.settings[category][key] = value;
        console.log(`更新设置: ${category}.${key} = ${value}`);
    },
    
    toggleStrategy(id, enabled) {
        this.settings.strategies[id].enabled = enabled;
        console.log(`策略 ${id}: ${enabled ? '启用' : '禁用'}`);
        this.render();
    },
    
    saveRiskRules() {
        console.log('保存风控规则');
        alert('风控规则已保存');
    },
    
    saveStrategies() {
        console.log('保存策略配置');
        alert('策略配置已保存');
    },
    
    testAPI(exchange) {
        console.log(`测试 ${exchange} API`);
        alert(`${exchange} API连接正常`);
    },
    
    editAPI(exchange) {
        console.log(`编辑 ${exchange} API`);
    }
};
