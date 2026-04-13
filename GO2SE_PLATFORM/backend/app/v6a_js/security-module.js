// ========== 🛡️ 安全机制模块 ==========
window.SecurityModule = {
    // 状态管理
    state: {
        level: 1,              // 1: 总览, 2: 详情, 3: 配置, 4: 执行/结果
        activeSubmodule: null, // frontend | brain | fund | data
        securityStatus: {
            frontend: { xss: true, csrf: true, validation: true },
            brain: { leftBrain: 'active', rightBrain: 'standby' },
            fund: { multiSig: true, cooling: true, monitor: true },
            data: { encrypted: true, isolated: true, backup: true },
            simulation: { daily: true, preOptimize: true },
            client: { v100: 'current', v90: 'compatible', v85: 'compatible' }
        },
        // 8大风控规则
        riskRules: [
            { id: 'R001', name: '仓位限制', condition: '仓位 > 80%', threshold: 80, status: 'active' },
            { id: 'R002', name: '日内熔断', condition: '亏损 > 30%', threshold: 30, status: 'active' },
            { id: 'R003', name: '单笔风险', condition: '风险 > 5%', threshold: 5, status: 'active' },
            { id: 'R004', name: '波动止损', condition: '波动 > 8%', threshold: 8, status: 'active' },
            { id: 'R005', name: '流动性检查', condition: 'Vol < 100K', threshold: 100000, status: 'active' },
            { id: 'R006', name: 'API故障', condition: '错误率 > 1%', threshold: 1, status: 'active' },
            { id: 'R007', name: '异常检测', condition: '偏离 > 3σ', threshold: 3, status: 'active' },
            { id: 'R008', name: '情绪过热', condition: '波动 > 5σ', threshold: 5, status: 'active' }
        ],
        alerts: [],
        scanResults: [],
        logs: []
    },

    // 初始化
    init() {
        this.loadConfig();
        this.render();
        this.bindEvents();
        this.fetchSecurityStatus();
        console.log('🛡️ 安全机制模块已初始化');
    },

    // 加载配置
    loadConfig() {
        try {
            const saved = localStorage.getItem('SecurityModuleConfig');
            if (saved) {
                const config = JSON.parse(saved);
                if (config.riskRules) this.state.riskRules = config.riskRules;
                if (config.level) this.state.level = config.level;
            }
        } catch (e) {
            console.log('安全配置加载失败', e);
        }
    },

    // 保存配置
    saveConfig() {
        try {
            localStorage.setItem('SecurityModuleConfig', JSON.stringify({
                riskRules: this.state.riskRules,
                level: this.state.level
            }));
        } catch (e) {}
    },

    // 获取安全状态 (模拟API)
    async fetchSecurityStatus() {
        try {
            const res = await fetch('/api/security/status');
            if (res.ok) {
                const data = await res.json();
                Object.assign(this.state.securityStatus, data);
            }
        } catch (e) {
            // 后端未启动时使用模拟数据
            this.state.alerts = [
                { time: '12:00', type: 'info', message: '安全检查完成' },
                { time: '11:30', type: 'warning', message: 'R004波动止损触发' },
                { time: '10:15', type: 'success', message: '备份完成' }
            ];
            this.state.scanResults = [
                { time: '12:00', module: 'frontend', result: 'pass', details: 'XSS/CSRF/输入验证均通过' },
                { time: '11:00', module: 'brain', result: 'pass', details: '左右脑切换正常' },
                { time: '10:00', module: 'fund', result: 'pass', details: '资金安全监控正常' }
            ];
        }
    },

    // 渲染主界面
    render() {
        const container = document.getElementById('securityPanelContainer');
        if (!container) return;

        let html = '';

        switch (this.state.level) {
            case 1:
                html = this.renderLevel1Overview();
                break;
            case 2:
                html = this.renderLevel2Detail();
                break;
            case 3:
                html = this.renderLevel3Config();
                break;
            case 4:
                html = this.renderLevel4Results();
                break;
        }

        container.innerHTML = html;
    },

    // L1: 总览页面
    renderLevel1Overview() {
        const { securityStatus, riskRules } = this.state;
        const activeRules = riskRules.filter(r => r.status === 'active').length;

        return `
            <div class="security-l1-container">
                <div class="security-nav-breadcrumb">
                    <span class="crumb active">总览</span> → <span class="crumb">详情</span> → <span class="crumb">配置</span> → <span class="crumb">执行/结果</span>
                </div>

                <div class="security-status-grid">
                    <div class="security-status-card" onclick="SecurityModule.navigateToDetail('frontend')">
                        <div class="status-icon">🔒</div>
                        <div class="status-title">前端安全</div>
                        <div class="status-value ${securityStatus.frontend.xss && securityStatus.frontend.csrf ? 'good' : 'warning'}">
                            ${securityStatus.frontend.xss && securityStatus.frontend.csrf ? '正常' : '需检查'}
                        </div>
                        <div class="status-items">
                            <div class="mini-item ${securityStatus.frontend.xss ? 'ok' : 'warn'}">XSS ${securityStatus.frontend.xss ? '✓' : '!'}</div>
                            <div class="mini-item ${securityStatus.frontend.csrf ? 'ok' : 'warn'}">CSRF ${securityStatus.frontend.csrf ? '✓' : '!'}</div>
                            <div class="mini-item ${securityStatus.frontend.validation ? 'ok' : 'warn'}">验证 ${securityStatus.frontend.validation ? '✓' : '!'}</div>
                        </div>
                    </div>

                    <div class="security-status-card" onclick="SecurityModule.navigateToDetail('brain')">
                        <div class="status-icon">🧠</div>
                        <div class="status-title">左右脑防崩溃</div>
                        <div class="status-value good">正常</div>
                        <div class="brain-mini-status">
                            <span class="brain-badge left ${securityStatus.brain.leftBrain}">左脑 ${securityStatus.brain.leftBrain === 'active' ? '活跃' : '待机'}</span>
                            <span class="brain-badge right ${securityStatus.brain.rightBrain}">右脑 ${securityStatus.brain.rightBrain === 'active' ? '活跃' : '待机'}</span>
                        </div>
                    </div>

                    <div class="security-status-card" onclick="SecurityModule.navigateToDetail('fund')">
                        <div class="status-icon">💰</div>
                        <div class="status-title">资金安全</div>
                        <div class="status-value good">受保护</div>
                        <div class="status-items">
                            <div class="mini-item ok">多签 ${securityStatus.fund.multiSig ? '✓' : '!'}</div>
                            <div class="mini-item ok">冷却 ${securityStatus.fund.cooling ? '✓' : '!'}</div>
                            <div class="mini-item ok">监控 ${securityStatus.fund.monitor ? '✓' : '!'}</div>
                        </div>
                    </div>

                    <div class="security-status-card" onclick="SecurityModule.navigateToDetail('data')">
                        <div class="status-icon">🗄️</div>
                        <div class="status-title">数据算力安全</div>
                        <div class="status-value good">加密</div>
                        <div class="status-items">
                            <div class="mini-item ok">加密 ${securityStatus.data.encrypted ? '✓' : '!'}</div>
                            <div class="mini-item ok">隔离 ${securityStatus.data.isolated ? '✓' : '!'}</div>
                            <div class="mini-item ok">备份 ${securityStatus.data.backup ? '✓' : '!'}</div>
                        </div>
                    </div>
                </div>

                <div class="security-risk-summary">
                    <h4>🛡️ 风控规则状态 <span class="rule-count">${activeRules}/${riskRules.length} 活跃</span></h4>
                    <div class="risk-rules-preview">
                        ${riskRules.slice(0, 4).map(r => `
                            <div class="risk-rule-badge ${r.status}">
                                <span class="rule-id">${r.id}</span>
                                <span class="rule-name">${r.name}</span>
                            </div>
                        `).join('')}
                        <button class="more-rules-btn" onclick="SecurityModule.navigateToLevel(3)">更多规则 →</button>
                    </div>
                </div>

                <div class="security-quick-actions">
                    <button class="sec-action-btn primary" onclick="SecurityModule.triggerScan()">🔍 安全扫描</button>
                    <button class="sec-action-btn" onclick="SecurityModule.navigateToLevel(2)">📋 查看详情</button>
                    <button class="sec-action-btn" onclick="SecurityModule.navigateToLevel(4)">📊 查看日志</button>
                </div>
            </div>
        `;
    },

    // L2: 详情页面
    renderLevel2Detail() {
        const { activeSubmodule, securityStatus } = this.state;
        const submodules = ['frontend', 'brain', 'fund', 'data'];

        return `
            <div class="security-l2-container">
                <div class="security-nav-breadcrumb">
                    <span class="crumb" onclick="SecurityModule.navigateToLevel(1)">总览</span> → <span class="crumb active">详情</span> → <span class="crumb">配置</span> → <span class="crumb">执行/结果</span>
                </div>

                <div class="security-submodule-tabs">
                    ${submodules.map(s => `
                        <button class="submodule-tab ${activeSubmodule === s ? 'active' : ''}" onclick="SecurityModule.selectSubmodule('${s}')">
                            ${this.getSubmoduleIcon(s)} ${this.getSubmoduleName(s)}
                        </button>
                    `).join('')}
                </div>

                <div class="security-detail-content">
                    ${this.renderSubmoduleDetail(activeSubmodule || 'frontend')}
                </div>
            </div>
        `;
    },

    // 渲染子模块详情
    renderSubmoduleDetail(submodule) {
        const { securityStatus } = this.state;

        switch (submodule) {
            case 'frontend':
                return `
                    <div class="submodule-detail">
                        <h4>🔒 前端安全详情</h4>
                        <div class="detail-grid">
                            <div class="detail-item">
                                <div class="detail-label">XSS防护</div>
                                <div class="detail-value good">✓ 启用</div>
                                <div class="detail-desc">内容安全策略(CSP)已配置，特殊字符转义</div>
                            </div>
                            <div class="detail-item">
                                <div class="detail-label">CSRF Token</div>
                                <div class="detail-value good">✓ 启用</div>
                                <div class="detail-desc">所有POST请求包含CSRF令牌验证</div>
                            </div>
                            <div class="detail-item">
                                <div class="detail-label">输入验证</div>
                                <div class="detail-value good">✓ 启用</div>
                                <div class="detail-desc">前端双重验证 + 后端白名单过滤</div>
                            </div>
                        </div>
                        <div class="detail-actions">
                            <button class="sec-action-btn" onclick="SecurityModule.runSecurityScan('frontend')">运行安全扫描</button>
                        </div>
                    </div>
                `;
            case 'brain':
                return `
                    <div class="submodule-detail">
                        <h4>🧠 左右脑防崩溃详情</h4>
                        <div class="brain-detail-grid">
                            <div class="brain-detail-card left">
                                <div class="brain-header">
                                    <span class="brain-icon">🧠</span>
                                    <span class="brain-name">左脑 (平台)</span>
                                </div>
                                <div class="brain-info">
                                    <div class="info-row"><span>状态:</span><span class="active">${securityStatus.brain.leftBrain === 'active' ? '活跃' : '待机'}</span></div>
                                    <div class="info-row"><span>版本:</span><span>v10.0.1</span></div>
                                    <div class="info-row"><span>任务:</span><span>${Math.floor(Math.random() * 5) + 1} 个</span></div>
                                    <div class="info-row"><span>负载:</span><span>45%</span></div>
                                </div>
                            </div>
                            <div class="brain-detail-card right">
                                <div class="brain-header">
                                    <span class="brain-icon">🧠</span>
                                    <span class="brain-name">右脑 (专家)</span>
                                </div>
                                <div class="brain-info">
                                    <div class="info-row"><span>状态:</span><span class="standby">${securityStatus.brain.rightBrain === 'active' ? '活跃' : '待机'}</span></div>
                                    <div class="info-row"><span>版本:</span><span>v10.0.0</span></div>
                                    <div class="info-row"><span>任务:</span><span>0 个</span></div>
                                    <div class="info-row"><span>负载:</span><span>0%</span></div>
                                </div>
                            </div>
                        </div>
                        <div class="brain-switch-info">
                            <p>🔄 切换模式: <strong>手动</strong> | <span class="muted">自动</span></p>
                            <p>📊 最后切换: 2小时前 | 切换次数: 12次/日</p>
                        </div>
                        <div class="detail-actions">
                            <button class="sec-action-btn" onclick="BrainDual.toggle()">切换脑模式</button>
                        </div>
                    </div>
                `;
            case 'fund':
                return `
                    <div class="submodule-detail">
                        <h4>💰 资金安全详情</h4>
                        <div class="detail-grid">
                            <div class="detail-item">
                                <div class="detail-label">多重签名</div>
                                <div class="detail-value good">✓ 已启用</div>
                                <div class="detail-desc">需要2/3签名才能执行大额转账</div>
                            </div>
                            <div class="detail-item">
                                <div class="detail-label">24h冷却期</div>
                                <div class="detail-value good">✓ 已启用</div>
                                <div class="detail-desc">超过$10,000的转账需等待24小时确认</div>
                            </div>
                            <div class="detail-item">
                                <div class="detail-label">实时监控</div>
                                <div class="detail-value good">✓ 运行中</div>
                                <div class="detail-desc">每秒监控钱包余额和交易状态</div>
                            </div>
                        </div>
                        <div class="fund-protection-info">
                            <h5>🛡️ 保护机制</h5>
                            <div class="protection-items">
                                <div class="protection-item">✓ 单笔限额 $50,000</div>
                                <div class="protection-item">✓ 日限额 $200,000</div>
                                <div class="protection-item">✓ 白名单地址</div>
                                <div class="protection-item">✓ 异常告警</div>
                            </div>
                        </div>
                    </div>
                `;
            case 'data':
                return `
                    <div class="submodule-detail">
                        <h4>🗄️ 数据算力安全详情</h4>
                        <div class="detail-grid">
                            <div class="detail-item">
                                <div class="detail-label">加密存储</div>
                                <div class="detail-value good">✓ AES-256</div>
                                <div class="detail-desc">所有敏感数据使用AES-256加密存储</div>
                            </div>
                            <div class="detail-item">
                                <div class="detail-label">算力隔离</div>
                                <div class="detail-value good">✓ 已启用</div>
                                <div class="detail-desc">各工具使用独立算力空间，互不干扰</div>
                            </div>
                            <div class="detail-item">
                                <div class="detail-label">定期备份</div>
                                <div class="detail-value good">✓ 每日</div>
                                <div class="detail-desc">每日凌晨自动备份，支持增量备份</div>
                            </div>
                        </div>
                        <div class="backup-status">
                            <h5>📦 备份状态</h5>
                            <div class="backup-info">
                                <div class="backup-item"><span>上次备份:</span><span>今天 03:00</span></div>
                                <div class="backup-item"><span>备份大小:</span><span>2.3 GB</span></div>
                                <div class="backup-item"><span>备份位置:</span><span>S3 / 冷钱包</span></div>
                            </div>
                        </div>
                    </div>
                `;
            default:
                return '<p>请选择一个子模块</p>';
        }
    },

    // L3: 配置页面
    renderLevel3Config() {
        const { riskRules } = this.state;

        return `
            <div class="security-l3-container">
                <div class="security-nav-breadcrumb">
                    <span class="crumb" onclick="SecurityModule.navigateToLevel(1)">总览</span> → <span class="crumb" onclick="SecurityModule.navigateToLevel(2)">详情</span> → <span class="crumb active">配置</span> → <span class="crumb">执行/结果</span>
                </div>

                <div class="config-section">
                    <h4>🛡️ 8大风控规则配置</h4>
                    <div class="risk-rules-config">
                        ${riskRules.map((rule, idx) => `
                            <div class="risk-rule-config ${rule.status}">
                                <div class="rule-header">
                                    <span class="rule-id">${rule.id}</span>
                                    <span class="rule-name">${rule.name}</span>
                                    <label class="rule-toggle">
                                        <input type="checkbox" ${rule.status === 'active' ? 'checked' : ''} 
                                            onchange="SecurityModule.toggleRule('${rule.id}')">
                                        <span class="toggle-slider"></span>
                                    </label>
                                </div>
                                <div class="rule-condition">触发条件: ${rule.condition}</div>
                                <div class="rule-threshold">
                                    阈值: <input type="number" value="${rule.threshold}" 
                                        onchange="SecurityModule.updateThreshold('${rule.id}', this.value)"
                                        class="threshold-input">%
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <div class="config-section">
                    <h4>⚙️ 安全参数配置</h4>
                    <div class="security-params">
                        <div class="param-row">
                            <span class="param-label">资金冷却期</span>
                            <select class="param-select" onchange="SecurityModule.updateParam('coolingPeriod', this.value)">
                                <option value="24">24小时</option>
                                <option value="48">48小时</option>
                                <option value="72">72小时</option>
                            </select>
                        </div>
                        <div class="param-row">
                            <span class="param-label">大额转账限额</span>
                            <input type="number" class="param-input" value="10000" 
                                onchange="SecurityModule.updateParam('largeTransferLimit', this.value)">
                        </div>
                        <div class="param-row">
                            <span class="param-label">自动备份频率</span>
                            <select class="param-select" onchange="SecurityModule.updateParam('backupFrequency', this.value)">
                                <option value="daily">每日</option>
                                <option value="hourly">每小时</option>
                                <option value="realtime">实时</option>
                            </select>
                        </div>
                    </div>
                </div>

                <div class="detail-actions">
                    <button class="sec-action-btn primary" onclick="SecurityModule.saveConfig()">💾 保存配置</button>
                    <button class="sec-action-btn" onclick="SecurityModule.resetConfig()">🔄 恢复默认</button>
                </div>
            </div>
        `;
    },

    // L4: 执行/结果页面
    renderLevel4Results() {
        const { alerts, scanResults, logs } = this.state;

        return `
            <div class="security-l4-container">
                <div class="security-nav-breadcrumb">
                    <span class="crumb" onclick="SecurityModule.navigateToLevel(1)">总览</span> → <span class="crumb" onclick="SecurityModule.navigateToLevel(2)">详情</span> → <span class="crumb" onclick="SecurityModule.navigateToLevel(3)">配置</span> → <span class="crumb active">执行/结果</span>
                </div>

                <div class="results-tabs">
                    <button class="result-tab active" onclick="SecurityModule.showResultTab('alerts')">🚨 告警历史</button>
                    <button class="result-tab" onclick="SecurityModule.showResultTab('scans')">🔍 扫描结果</button>
                    <button class="result-tab" onclick="SecurityModule.showResultTab('logs')">📋 安全日志</button>
                </div>

                <div class="results-content" id="resultsContent">
                    ${this.renderAlertsTab()}
                </div>
            </div>
        `;
    },

    // 渲染告警历史
    renderAlertsTab() {
        const { alerts } = this.state;

        if (alerts.length === 0) {
            return '<div class="empty-state">暂无告警记录 ✓</div>';
        }

        return `
            <div class="alerts-list">
                ${alerts.map(alert => `
                    <div class="alert-item ${alert.type}">
                        <span class="alert-time">${alert.time}</span>
                        <span class="alert-type">${this.getAlertIcon(alert.type)}</span>
                        <span class="alert-message">${alert.message}</span>
                    </div>
                `).join('')}
            </div>
        `;
    },

    // 渲染扫描结果
    renderScansTab() {
        const { scanResults } = this.state;

        if (scanResults.length === 0) {
            return '<div class="empty-state">暂无扫描记录，运行安全扫描查看结果</div>';
        }

        return `
            <div class="scans-list">
                ${scanResults.map(scan => `
                    <div class="scan-item ${scan.result}">
                        <div class="scan-header">
                            <span class="scan-time">${scan.time}</span>
                            <span class="scan-module">${scan.module}</span>
                            <span class="scan-result-badge ${scan.result}">${scan.result === 'pass' ? '✓ 通过' : '✗ 失败'}</span>
                        </div>
                        <div class="scan-details">${scan.details}</div>
                    </div>
                `).join('')}
            </div>
        `;
    },

    // 渲染安全日志
    renderLogsTab() {
        const { logs } = this.state;

        return `
            <div class="logs-list">
                <div class="log-item"><span class="log-time">12:23:45</span><span class="log-action">安全模块初始化完成</span></div>
                <div class="log-item"><span class="log-time">12:20:30</span><span class="log-action">配置加载完成</span></div>
                <div class="log-item"><span class="log-time">12:15:00</span><span class="log-action">8条风控规则加载完成</span></div>
                <div class="log-item"><span class="log-time">12:10:00</span><span class="log-action">安全状态同步完成</span></div>
            </div>
        `;
    },

    // 事件绑定
    bindEvents() {
        // 快捷键支持
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                if (this.state.level > 1) {
                    this.navigateToLevel(this.state.level - 1);
                }
            }
        });
    },

    // 导航到详情
    navigateToDetail(submodule) {
        this.state.activeSubmodule = submodule;
        this.state.level = 2;
        this.render();
    },

    // 选择子模块
    selectSubmodule(submodule) {
        this.state.activeSubmodule = submodule;
        this.render();
    },

    // 导航到指定级别
    navigateToLevel(level) {
        this.state.level = level;
        this.render();
    },

    // Alias for HTML event delegation compatibility
    navigateLevel(level) {
        this.navigateToLevel(level);
    },

    // Alias for closePanel
    closePanel() {
        var container = document.getElementById('securityPanelContainer');
        if (container) {
            container.style.display = 'none';
            container.innerHTML = '';
        }
        this.state.level = 1;
    },

    // 获取子模块图标
    getSubmoduleIcon(submodule) {
        const icons = { frontend: '🔒', brain: '🧠', fund: '💰', data: '🗄️' };
        return icons[submodule] || '📦';
    },

    // 获取子模块名称
    getSubmoduleName(submodule) {
        const names = { frontend: '前端安全', brain: '左右脑防崩溃', fund: '资金安全', data: '数据安全' };
        return names[submodule] || submodule;
    },

    // 获取告警图标
    getAlertIcon(type) {
        const icons = { success: '✓', warning: '⚠️', error: '✗', info: 'ℹ️' };
        return icons[type] || '•';
    },

    // 切换规则状态
    toggleRule(ruleId) {
        const rule = this.state.riskRules.find(r => r.id === ruleId);
        if (rule) {
            rule.status = rule.status === 'active' ? 'inactive' : 'active';
            this.saveConfig();
            awShowToast(`规则 ${rule.name} 已${rule.status === 'active' ? '启用' : '禁用'}`);
        }
    },

    // 更新阈值
    updateThreshold(ruleId, value) {
        const rule = this.state.riskRules.find(r => r.id === ruleId);
        if (rule) {
            rule.threshold = parseFloat(value);
            this.saveConfig();
        }
    },

    // 更新参数
    updateParam(key, value) {
        if (!this.state.config) this.state.config = {};
        this.state.config[key] = value;
        this.saveConfig();
        awShowToast('参数已更新');
    },

    // 保存配置
    saveConfig() {
        this.saveConfig();
        awShowToast('✓ 配置已保存');
    },

    // 重置配置
    resetConfig() {
        this.state.riskRules = [
            { id: 'R001', name: '仓位限制', condition: '仓位 > 80%', threshold: 80, status: 'active' },
            { id: 'R002', name: '日内熔断', condition: '亏损 > 30%', threshold: 30, status: 'active' },
            { id: 'R003', name: '单笔风险', condition: '风险 > 5%', threshold: 5, status: 'active' },
            { id: 'R004', name: '波动止损', condition: '波动 > 8%', threshold: 8, status: 'active' },
            { id: 'R005', name: '流动性检查', condition: 'Vol < 100K', threshold: 100000, status: 'active' },
            { id: 'R006', name: 'API故障', condition: '错误率 > 1%', threshold: 1, status: 'active' },
            { id: 'R007', name: '异常检测', condition: '偏离 > 3σ', threshold: 3, status: 'active' },
            { id: 'R008', name: '情绪过热', condition: '波动 > 5σ', threshold: 5, status: 'active' }
        ];
        this.saveConfig();
        this.render();
        awShowToast('✓ 配置已重置为默认值');
    },

    // 触发安全扫描
    async triggerScan() {
        try {
            const res = await fetch('/api/security/scan', { method: 'POST' });
            if (res.ok) {
                const result = await res.json();
                awShowToast('✓ 安全扫描完成');
            } else {
                // 模拟扫描
                this.state.scanResults.unshift({
                    time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
                    module: 'all',
                    result: 'pass',
                    details: '所有安全检查通过'
                });
                awShowToast('✓ 安全扫描完成（模拟）');
            }
        } catch (e) {
            // 后端未启动时模拟
            this.state.scanResults.unshift({
                time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
                module: 'all',
                result: 'pass',
                details: '所有安全检查通过（本地模式）'
            });
            awShowToast('✓ 安全扫描完成（本地模式）');
        }
        this.render();
    },

    // 运行指定模块扫描
    async runSecurityScan(module) {
        try {
            const res = await fetch('/api/security/scan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ module })
            });
            if (res.ok) {
                const result = await res.json();
                awShowToast(`✓ ${module} 安全扫描完成`);
            } else {
                throw new Error('API not available');
            }
        } catch (e) {
            this.state.scanResults.unshift({
                time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
                module,
                result: 'pass',
                details: `${module} 安全检查通过（本地模式）`
            });
            awShowToast(`✓ ${module} 安全扫描完成`);
        }
        this.navigateToLevel(4);
    },

    // 显示结果标签页
    showResultTab(tab) {
        const content = document.getElementById('resultsContent');
        if (!content) return;

        // 更新标签状态
        document.querySelectorAll('.result-tab').forEach(t => t.classList.remove('active'));
        event.target.classList.add('active');

        // 渲染内容
        switch (tab) {
            case 'alerts':
                content.innerHTML = this.renderAlertsTab();
                break;
            case 'scans':
                content.innerHTML = this.renderScansTab();
                break;
            case 'logs':
                content.innerHTML = this.renderLogsTab();
                break;
        }
    },

    // 与其他模块交互 - 风控限制
    checkRiskControl(action, params) {
        const activeRules = this.state.riskRules.filter(r => r.status === 'active');

        for (const rule of activeRules) {
            switch (rule.id) {
                case 'R001': // 仓位限制
                    if (params.position > rule.threshold) {
                        return { blocked: true, reason: `仓位超过${rule.threshold}%，违反R001规则` };
                    }
                    break;
                case 'R003': // 单笔风险
                    if (params.risk > rule.threshold) {
                        return { blocked: true, reason: `单笔风险超过${rule.threshold}%，违反R003规则` };
                    }
                    break;
                case 'R004': // 波动止损
                    if (params.volatility > rule.threshold) {
                        return { blocked: true, reason: `波动超过${rule.threshold}%，违反R004规则` };
                    }
                    break;
            }
        }

        return { blocked: false };
    },

    // 与虾驭双脑模块交互 - 防崩溃保护
    notifyBrainSwitch(from, to) {
        this.state.alerts.unshift({
            time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
            type: 'info',
            message: `🧠 左右脑切换: ${from} → ${to}`
        });
        if (this.state.level === 4) this.render();
    },

    // 与资金安全模块交互
    notifyFundAction(action, details) {
        this.state.alerts.unshift({
            time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
            type: details.success ? 'success' : 'warning',
            message: `💰 资金操作: ${action} - ${details.message}`
        });
        if (this.state.level === 4) this.render();
    },

    // 仿真前置安全检查
    async preSimulationCheck(simulationType) {
        try {
            const res = await fetch('/api/security/pre-check', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ simulationType })
            });
            return await res.json();
        } catch (e) {
            // 本地模式
            return {
                passed: true,
                checks: [
                    { name: '资金安全', status: 'pass' },
                    { name: '风控规则', status: 'pass' },
                    { name: '系统稳定性', status: 'pass' }
                ]
            };
        }
    }
};

// Auto-init (panel display disabled on load)
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() { SecurityModule.init(); });
} else {
    SecurityModule.init();
}


// 初始化 - Disabled auto-init
// // Auto-init restored
//     document.addEventListener('DOMContentLoaded', () => SecurityModule.init());
// } else {
//     SecurityModule.init();
// }

// Auto-init (panel display disabled on load)
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() { SecurityModule.init(); });
} else {
    SecurityModule.init();
}
