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
