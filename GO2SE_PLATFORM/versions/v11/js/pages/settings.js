// GO2SE v11 - Settings Page Module
const SettingsPage = {
    name: 'settings',
    
    data: {
        apiKeys: {},
        riskRules: {}
    },
    
    async load() {
        const container = document.getElementById('page-content');
        container.innerHTML = this.template();
        this.initEventListeners();
        this.initAllocationSliders();
        this.initWeightSliders();
        this.loadSavedSettings();
    },
    
    template() {
        return `
        <div class="settings-page">
            <div class="page-header">
                <h1>⚙️ 系统设置</h1>
            </div>
            
            <div class="settings-sections">
                <div class="settings-section">
                    <h3>🔐 API配置</h3>
                    <div class="form-group">
                        <label>Binance API Key</label>
                        <input type="password" id="api-binance-key" placeholder="输入API Key">
                    </div>
                    <div class="form-group">
                        <label>Binance Secret</label>
                        <input type="password" id="api-binance-secret" placeholder="输入Secret">
                    </div>
                    <button class="btn-primary" onclick="SettingsPage.saveApiKeys()">保存</button>
                </div>
                
                <div class="settings-section">
                    <h3>💼 投资组合配置 <span class="badge">推荐值</span></h3>
                    <p class="section-desc">以下为推荐值，可根据风险偏好自行调节</p>
                    <div class="allocation-grid">
                        <div class="allocation-item">
                            <label>🐰 打兔子</label>
                            <input type="range" id="alloc-rabbit" min="0" max="40" value="25" step="1">
                            <span class="allocation-value" id="alloc-rabbit-value">25%</span>
                        </div>
                        <div class="allocation-item">
                            <label>🐹 打地鼠</label>
                            <input type="range" id="alloc-mole" min="0" max="30" value="20" step="1">
                            <span class="allocation-value" id="alloc-mole-value">20%</span>
                        </div>
                        <div class="allocation-item">
                            <label>🔮 走着瞧</label>
                            <input type="range" id="alloc-oracle" min="0" max="25" value="15" step="1">
                            <span class="allocation-value" id="alloc-oracle-value">15%</span>
                        </div>
                        <div class="allocation-item">
                            <label>👑 跟大哥</label>
                            <input type="range" id="alloc-leader" min="0" max="25" value="15" step="1">
                            <span class="allocation-value" id="alloc-leader-value">15%</span>
                        </div>
                        <div class="allocation-item">
                            <label>🍀 搭便车</label>
                            <input type="range" id="alloc-hitchhike" min="0" max="20" value="10" step="1">
                            <span class="allocation-value" id="alloc-hitchhike-value">10%</span>
                        </div>
                        <div class="allocation-item">
                            <label>💰 薅羊毛</label>
                            <input type="range" id="alloc-airdrop" min="0" max="10" value="3" step="1">
                            <span class="allocation-value" id="alloc-airdrop-value">3%</span>
                        </div>
                        <div class="allocation-item">
                            <label>👶 穷孩子</label>
                            <input type="range" id="alloc-crowdsource" min="0" max="5" value="2" step="1">
                            <span class="allocation-value" id="alloc-crowdsource-value">2%</span>
                        </div>
                    </div>
                    <div class="total-allocation">
                        <span>总计:</span>
                        <span id="total-allocation">100%</span>
                    </div>
                    <button class="btn-primary" onclick="SettingsPage.saveAllocation()">保存组合配置</button>
                </div>
                
                <div class="settings-section">
                    <h3>⚖️ 策略权重配置 <span class="badge">推荐值</span></h3>
                    <p class="section-desc">MiroFish等外部策略参与权重 (0=不参与, 1=完全依赖)</p>
                    <div class="weight-grid">
                        <div class="weight-item">
                            <label>🐰 打兔子 MiroFish权重</label>
                            <input type="range" id="weight-rabbit" min="0" max="100" value="35" step="5">
                            <span class="weight-value" id="weight-rabbit-value">35%</span>
                        </div>
                        <div class="weight-item">
                            <label>🐹 打地鼠 MiroFish权重</label>
                            <input type="range" id="weight-mole" min="0" max="100" value="40" step="5">
                            <span class="weight-value" id="weight-mole-value">40%</span>
                        </div>
                        <div class="weight-item">
                            <label>🔮 走着瞧 MiroFish权重</label>
                            <input type="range" id="weight-oracle" min="0" max="100" value="50" step="5">
                            <span class="weight-value" id="weight-oracle-value">50%</span>
                        </div>
                        <div class="weight-item">
                            <label>👑 跟大哥 MiroFish权重</label>
                            <input type="range" id="weight-leader" min="0" max="100" value="30" step="5">
                            <span class="weight-value" id="weight-leader-value">30%</span>
                        </div>
                        <div class="weight-item">
                            <label>🍀 搭便车 MiroFish权重</label>
                            <input type="range" id="weight-hitchhike" min="0" max="100" value="25" step="5">
                            <span class="weight-value" id="weight-hitchhike-value">25%</span>
                        </div>
                    </div>
                    <button class="btn-primary" onclick="SettingsPage.saveWeights()">保存权重配置</button>
                </div>
                
                <div class="settings-section">
                    <h3>🛡️ 风控规则</h3>
                    <div class="rule-item">
                        <label>最大仓位</label>
                        <input type="number" id="risk-max-position" value="80" step="1" min="0" max="100"> %
                    </div>
                    <div class="rule-item">
                        <label>单笔风险</label>
                        <input type="number" id="risk-single-risk" value="5" step="0.1" min="0" max="100"> %
                    </div>
                    <div class="rule-item">
                        <label>日熔断</label>
                        <input type="number" id="risk-daily-stop" value="15" step="1" min="0" max="100"> %
                    </div>
                    <div class="rule-item">
                        <label>止损</label>
                        <input type="number" id="risk-stop-loss" value="10" step="0.1" min="0" max="100"> %
                    </div>
                    <button class="btn-primary" onclick="SettingsPage.saveRiskRules()">保存</button>
                </div>
                
                <div class="settings-section">
                    <h3>🎨 界面设置</h3>
                    <div class="form-group">
                        <label>主题</label>
                        <select id="theme-select">
                            <option value="dark">🌙 暗色</option>
                            <option value="light">☀️ 亮色</option>
                            <option value="auto">🔄 自动</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>语言</label>
                        <select id="lang-select">
                            <option value="zh">中文</option>
                            <option value="en">English</option>
                        </select>
                    </div>
                    <button class="btn-primary" onclick="SettingsPage.saveUISettings()">保存</button>
                </div>
                
                <div class="settings-section">
                    <h3>🔄 系统操作</h3>
                    <div class="action-buttons">
                        <button class="btn-secondary" onclick="SettingsPage.exportData()">
                            📤 导出数据
                        </button>
                        <button class="btn-secondary" onclick="SettingsPage.importData()">
                            📥 导入数据
                        </button>
                        <button class="btn-warning" onclick="SettingsPage.clearCache()">
                            🗑️ 清除缓存
                        </button>
                        <button class="btn-danger" onclick="SettingsPage.resetAll()">
                            ⚠️ 重置所有
                        </button>
                    </div>
                </div>
            </div>
        </div>
        `;
    },
    
    initEventListeners() {
        const theme = localStorage.getItem('theme') || 'dark';
        const lang = localStorage.getItem('lang') || 'zh';
        
        const themeSelect = document.getElementById('theme-select');
        const langSelect = document.getElementById('lang-select');
        
        if (themeSelect) themeSelect.value = theme;
        if (langSelect) langSelect.value = lang;
    },
    
    saveApiKeys() {
        const binanceKey = document.getElementById('api-binance-key')?.value;
        const binanceSecret = document.getElementById('api-binance-secret')?.value;
        
        if (binanceKey && binanceSecret) {
            localStorage.setItem('api_binance_key', binanceKey);
            localStorage.setItem('api_binance_secret', binanceSecret);
            Toast.show('API配置已保存', 'success');
        } else {
            Toast.show('请填写完整的API信息', 'error');
        }
    },
    
    saveRiskRules() {
        const rules = {
            maxPosition: parseFloat(document.getElementById('risk-max-position')?.value || 80),
            singleRisk: parseFloat(document.getElementById('risk-single-risk')?.value || 5),
            dailyStop: parseFloat(document.getElementById('risk-daily-stop')?.value || 15),
            stopLoss: parseFloat(document.getElementById('risk-stop-loss')?.value || 10)
        };
        
        localStorage.setItem('risk_rules', JSON.stringify(rules));
        Toast.show('风控规则已保存', 'success');
    },
    
    saveAllocation() {
        const allocation = {
            rabbit: parseFloat(document.getElementById('alloc-rabbit')?.value || 25),
            mole: parseFloat(document.getElementById('alloc-mole')?.value || 20),
            oracle: parseFloat(document.getElementById('alloc-oracle')?.value || 15),
            leader: parseFloat(document.getElementById('alloc-leader')?.value || 15),
            hitchhike: parseFloat(document.getElementById('alloc-hitchhike')?.value || 10),
            airdrop: parseFloat(document.getElementById('alloc-airdrop')?.value || 3),
            crowdsource: parseFloat(document.getElementById('alloc-crowdsource')?.value || 2)
        };
        
        const total = Object.values(allocation).reduce((a, b) => a + b, 0);
        if (total > 100) {
            Toast.show(`总分配超过100% (${total}%), 请调整`, 'error');
            return;
        }
        
        localStorage.setItem('tool_allocation', JSON.stringify(allocation));
        Toast.show(`投资组合已保存 (总计${total}%)`, 'success');
    },
    
    saveWeights() {
        const weights = {
            rabbit: parseFloat(document.getElementById('weight-rabbit')?.value || 35) / 100,
            mole: parseFloat(document.getElementById('weight-mole')?.value || 40) / 100,
            oracle: parseFloat(document.getElementById('weight-oracle')?.value || 50) / 100,
            leader: parseFloat(document.getElementById('weight-leader')?.value || 30) / 100,
            hitchhike: parseFloat(document.getElementById('weight-hitchhike')?.value || 25) / 100
        };
        
        localStorage.setItem('mirofish_weights', JSON.stringify(weights));
        Toast.show('策略权重已保存', 'success');
    },
    
    initAllocationSliders() {
        const tools = ['rabbit', 'mole', 'oracle', 'leader', 'hitchhike', 'airdrop', 'crowdsource'];
        tools.forEach(tool => {
            const slider = document.getElementById(`alloc-${tool}`);
            const value = document.getElementById(`alloc-${tool}-value`);
            if (slider && value) {
                slider.addEventListener('input', () => {
                    value.textContent = `${slider.value}%`;
                    this.updateTotalAllocation();
                });
            }
        });
        this.updateTotalAllocation();
    },
    
    initWeightSliders() {
        const tools = ['rabbit', 'mole', 'oracle', 'leader', 'hitchhike'];
        tools.forEach(tool => {
            const slider = document.getElementById(`weight-${tool}`);
            const value = document.getElementById(`weight-${tool}-value`);
            if (slider && value) {
                slider.addEventListener('input', () => {
                    value.textContent = `${slider.value}%`;
                });
            }
        });
    },
    
    updateTotalAllocation() {
        const tools = ['rabbit', 'mole', 'oracle', 'leader', 'hitchhike', 'airdrop', 'crowdsource'];
        let total = 0;
        tools.forEach(tool => {
            const slider = document.getElementById(`alloc-${tool}`);
            if (slider) total += parseFloat(slider.value || 0);
        });
        const totalEl = document.getElementById('total-allocation');
        if (totalEl) {
            totalEl.textContent = `${total}%`;
            totalEl.className = total > 100 ? 'negative' : '';
        }
    },
    
    loadSavedSettings() {
        // Load allocation
        const savedAlloc = localStorage.getItem('tool_allocation');
        if (savedAlloc) {
            const alloc = JSON.parse(savedAlloc);
            Object.entries(alloc).forEach(([tool, value]) => {
                const slider = document.getElementById(`alloc-${tool}`);
                const valueEl = document.getElementById(`alloc-${tool}-value`);
                if (slider) slider.value = value;
                if (valueEl) valueEl.textContent = `${value}%`;
            });
        }
        
        // Load weights
        const savedWeights = localStorage.getItem('mirofish_weights');
        if (savedWeights) {
            const weights = JSON.parse(savedWeights);
            Object.entries(weights).forEach(([tool, value]) => {
                const slider = document.getElementById(`weight-${tool}`);
                const valueEl = document.getElementById(`weight-${tool}-value`);
                if (slider) slider.value = value * 100;
                if (valueEl) valueEl.textContent = `${(value * 100).toFixed(0)}%`;
            });
        }
        
        this.updateTotalAllocation();
    },
    
    saveUISettings() {
        const theme = document.getElementById('theme-select')?.value || 'dark';
        const lang = document.getElementById('lang-select')?.value || 'zh';
        
        localStorage.setItem('theme', theme);
        localStorage.setItem('lang', lang);
        
        document.documentElement.setAttribute('data-theme', theme);
        Toast.show('界面设置已保存', 'success');
    },
    
    exportData() {
        const data = {
            apiKeys: {
                binance: localStorage.getItem('api_binance_key')
            },
            riskRules: JSON.parse(localStorage.getItem('risk_rules') || '{}'),
            theme: localStorage.getItem('theme'),
            lang: localStorage.getItem('lang')
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `go2se-settings-${Date.now()}.json`;
        a.click();
        
        Toast.show('数据已导出', 'success');
    },
    
    importData() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        input.onchange = e => {
            const file = e.target.files[0];
            if (!file) return;
            
            const reader = new FileReader();
            reader.onload = event => {
                try {
                    const data = JSON.parse(event.target.result);
                    if (data.apiKeys?.binance) {
                        localStorage.setItem('api_binance_key', data.apiKeys.binance);
                    }
                    if (data.riskRules) {
                        localStorage.setItem('risk_rules', JSON.stringify(data.riskRules));
                    }
                    if (data.theme) {
                        localStorage.setItem('theme', data.theme);
                    }
                    Toast.show('数据已导入', 'success');
                    this.load();
                } catch (err) {
                    Toast.show('导入失败: 无效的文件格式', 'error');
                }
            };
            reader.readAsText(file);
        };
        input.click();
    },
    
    clearCache() {
        localStorage.removeItem('cache');
        Toast.show('缓存已清除', 'success');
    },
    
    resetAll() {
        if (confirm('确定要重置所有设置吗？此操作不可撤销。')) {
            localStorage.clear();
            Toast.show('所有设置已重置', 'success');
            setTimeout(() => location.reload(), 1000);
        }
    }
};

window.SettingsPage = SettingsPage;
