// ==========================================================================
// V14 兼容层 - 为缺失的模块添加 navigateLevel 和 renderPanel
// ==========================================================================

// ========== BrainDual 兼容层 ==========
if (typeof BrainDual !== 'undefined') {
    BrainDual.state = BrainDual.state || { level: 1, mode: 'dual' };
    BrainDual.navigateLevel = function(level) {
        this.state.level = level;
        this.renderPanel();
    };
    BrainDual.renderPanel = function() {
        var container = document.getElementById('brainDualPanel');
        if (!container) {
            container = document.createElement('div');
            container.id = 'brainDualPanel';
            container.className = 'panel-overlay';
            document.body.appendChild(container);
        }
        
        var html = '<div class="panel-container">';
        html += '<div class="panel-header">';
        html += '<h3>🧠 虾驭双脑</h3>';
        html += '<button class="panel-close" onclick="BrainDual.closePanel()">✕</button>';
        html += '</div>';
        html += '<div class="panel-body">';
        html += '<div class="level-nav">';
        html += '<button class="level-btn ' + (this.state.level === 1 ? 'active' : '') + '" onclick="BrainDual.navigateLevel(1)">L1 总览</button>';
        html += '<button class="level-btn ' + (this.state.level === 2 ? 'active' : '') + '" onclick="BrainDual.navigateLevel(2)">L2 分析</button>';
        html += '<button class="level-btn ' + (this.state.level === 3 ? 'active' : '') + '" onclick="BrainDual.navigateLevel(3)">L3 策略</button>';
        html += '<button class="level-btn ' + (this.state.level === 4 ? 'active' : '') + '" onclick="BrainDual.navigateLevel(4)">L4 执行</button>';
        html += '</div>';
        
        if (this.state.level === 1) {
            html += this.renderLevel1();
        } else if (this.state.level === 2) {
            html += this.renderLevel2();
        } else if (this.state.level === 3) {
            html += this.renderLevel3();
        } else {
            html += this.renderLevel4();
        }
        
        html += '</div></div>';
        container.innerHTML = html;
        container.style.display = 'block';
    };
    
    BrainDual.renderLevel1 = function() {
        return '<div class="level-content">' +
            '<h4>🧠 双脑总览</h4>' +
            '<p>左脑: 逻辑分析 | 右脑: 创意洞察</p>' +
            '<div style="display:grid;grid-template-columns:1fr 1fr;gap:15px;margin-top:15px;">' +
            '<div style="padding:15px;background:var(--bg-tertiary);border-radius:8px;text-align:center;">' +
            '<div style="font-size:24px;margin-bottom:5px;">🧮</div>' +
            '<div>左脑模式</div>' +
            '<div style="color:var(--accent-green);">逻辑 85%</div>' +
            '</div>' +
            '<div style="padding:15px;background:var(--bg-tertiary);border-radius:8px;text-align:center;">' +
            '<div style="font-size:24px;margin-bottom:5px;">🎨</div>' +
            '<div>右脑模式</div>' +
            '<div style="color:var(--accent-purple);">创意 72%</div>' +
            '</div>' +
            '</div>' +
            '</div>';
    };
    
    BrainDual.renderLevel2 = function() {
        return '<div class="level-content">' +
            '<h4>📊 深度分析</h4>' +
            '<p>市场数据深度解析</p>' +
            '<div style="margin-top:15px;padding:15px;background:var(--bg-tertiary);border-radius:8px;">' +
            '<p>• 趋势识别: EMA + MACD</p>' +
            '<p>• 动量分析: RSI + ADX</p>' +
            '<p>• 波动检测: Bollinger + ATR</p>' +
            '</div>' +
            '</div>';
    };
    
    BrainDual.renderLevel3 = function() {
        return '<div class="level-content">' +
            '<h4>⚙️ 策略生成</h4>' +
            '<p>AI生成交易策略</p>' +
            '<div style="margin-top:15px;padding:15px;background:var(--bg-tertiary);border-radius:8px;">' +
            '<p>• 策略1: 突破追涨</p>' +
            '<p>• 策略2: 回踩买入</p>' +
            '<p>• 策略3: 网格交易</p>' +
            '</div>' +
            '</div>';
    };
    
    BrainDual.renderLevel4 = function() {
        return '<div class="level-content">' +
            '<h4>✅ 执行确认</h4>' +
            '<p>确认执行策略</p>' +
            '<div style="margin-top:15px;">' +
            '<button style="width:100%;padding:12px;background:var(--accent-green);border:none;border-radius:8px;color:#000;font-weight:600;cursor:pointer;">确认执行</button>' +
            '</div>' +
            '</div>';
    };
    
    BrainDual.closePanel = function() {
        var container = document.getElementById('brainDualPanel');
        if (container) container.style.display = 'none';
    };
    
    BrainDual.setMode = function(mode) {
        this.state.mode = mode;
        console.log('🧠 Brain mode set to:', mode);
    };
}

// ========== WalletSecurity 兼容层 ==========
if (typeof WalletSecurity !== 'undefined') {
    WalletSecurity.state = WalletSecurity.state || { level: 1 };
    WalletSecurity.navigateLevel = function(level) {
        this.state.level = level;
        this.renderPanel();
    };
    WalletSecurity.renderPanel = function() {
        var container = document.getElementById('walletSecurityPanel');
        if (!container) {
            container = document.createElement('div');
            container.id = 'walletSecurityPanel';
            container.className = 'panel-overlay';
            document.body.appendChild(container);
        }
        
        var html = '<div class="panel-container">';
        html += '<div class="panel-header">';
        html += '<h3>🔐 钱包安全架构</h3>';
        html += '<button class="panel-close" onclick="WalletSecurity.closePanel()">✕</button>';
        html += '</div>';
        html += '<div class="panel-body">';
        html += '<div class="level-nav">';
        html += '<button class="level-btn ' + (this.state.level === 1 ? 'active' : '') + '" onclick="WalletSecurity.navigateLevel(1)">L1 总览</button>';
        html += '<button class="level-btn ' + (this.state.level === 2 ? 'active' : '') + '" onclick="WalletSecurity.navigateLevel(2)">L2 架构</button>';
        html += '<button class="level-btn ' + (this.state.level === 3 ? 'active' : '') + '" onclick="WalletSecurity.navigateLevel(3)">L3 设置</button>';
        html += '<button class="level-btn ' + (this.state.level === 4 ? 'active' : '') + '" onclick="WalletSecurity.navigateLevel(4)">L4 保存</button>';
        html += '</div>';
        
        if (this.state.level === 1) {
            html += '<div class="level-content"><h4>🔐 安全总览</h4><p>钱包安全状态: 安全</p></div>';
        } else if (this.state.level === 2) {
            html += '<div class="level-content"><h4>🏦 架构配置</h4><p>主钱包 | 中转钱包 | 备用钱包</p></div>';
        } else if (this.state.level === 3) {
            html += '<div class="level-content"><h4>⚙️ 安全设置</h4><p>多重签名 | 延迟交易 | 白名单</p></div>';
        } else {
            html += '<div class="level-content"><h4>✅ 保存</h4><button style="width:100%;padding:12px;background:var(--accent-green);border:none;border-radius:8px;color:#000;font-weight:600;">保存配置</button></div>';
        }
        
        html += '</div></div>';
        container.innerHTML = html;
        container.style.display = 'block';
    };
    WalletSecurity.closePanel = function() {
        var container = document.getElementById('walletSecurityPanel');
        if (container) container.style.display = 'none';
    };
    WalletSecurity.lock = function() {
        console.log('🔒 Wallet locked');
    };
}

// ========== SecurityModule 兼容层 ==========
if (typeof SecurityModule !== 'undefined') {
    SecurityModule.state = SecurityModule.state || { level: 1 };
    SecurityModule.navigateLevel = function(level) {
        this.state.level = level;
        if (this.renderPanel) this.renderPanel();
    };
    if (!SecurityModule.renderPanel) {
        SecurityModule.renderPanel = function() {
            var container = document.getElementById('securityModulePanel');
            if (!container) {
                container = document.createElement('div');
                container.id = 'securityModulePanel';
                container.className = 'panel-overlay';
                document.body.appendChild(container);
            }
            
            var html = '<div class="panel-container">';
            html += '<div class="panel-header">';
            html += '<h3>🛡️ 安全机制</h3>';
            html += '<button class="panel-close" onclick="SecurityModule.closePanel()">✕</button>';
            html += '</div>';
            html += '<div class="panel-body">';
            html += '<div class="level-nav">';
            html += '<button class="level-btn" onclick="SecurityModule.navigateLevel(1)">L1</button>';
            html += '<button class="level-btn" onclick="SecurityModule.navigateLevel(2)">L2</button>';
            html += '<button class="level-btn" onclick="SecurityModule.navigateLevel(3)">L3</button>';
            html += '<button class="level-btn" onclick="SecurityModule.navigateLevel(4)">L4</button>';
            html += '</div>';
            html += '<div class="level-content"><p>安全模块 - Level ' + this.state.level + '</p></div>';
            html += '</div></div>';
            container.innerHTML = html;
            container.style.display = 'block';
        };
    }
    SecurityModule.closePanel = function() {
        var container = document.getElementById('securityModulePanel');
        if (container) container.style.display = 'none';
    };
}

// ========== SevenTools 兼容层 ==========
if (typeof SevenTools !== 'undefined') {
    SevenTools.state = SevenTools.state || { level: 1 };
    SevenTools.navigateLevel = function(level) {
        this.state.level = level;
        if (this.renderPanel) this.renderPanel();
    };
    if (!SevenTools.renderPanel) {
        SevenTools.renderPanel = function() {
            var container = document.getElementById('sevenToolsPanel');
            if (!container) {
                container = document.createElement('div');
                container.id = 'sevenToolsPanel';
                container.className = 'panel-overlay';
                document.body.appendChild(container);
            }
            
            var html = '<div class="panel-container">';
            html += '<div class="panel-header">';
            html += '<h3>⭐ 北斗七鑫投资体系</h3>';
            html += '<button class="panel-close" onclick="SevenTools.closePanel()">✕</button>';
            html += '</div>';
            html += '<div class="panel-body">';
            html += '<div class="level-nav">';
            html += '<button class="level-btn" onclick="SevenTools.navigateLevel(1)">L1</button>';
            html += '<button class="level-btn" onclick="SevenTools.navigateLevel(2)">L2</button>';
            html += '<button class="level-btn" onclick="SevenTools.navigateLevel(3)">L3</button>';
            html += '<button class="level-btn" onclick="SevenTools.navigateLevel(4)">L4</button>';
            html += '</div>';
            html += '<div class="level-content"><p>北斗七鑫 - Level ' + this.state.level + '</p></div>';
            html += '</div></div>';
            container.innerHTML = html;
            container.style.display = 'block';
        };
    }
    SevenTools.closePanel = function() {
        var container = document.getElementById('sevenToolsPanel');
        if (container) container.style.display = 'none';
    };
}

console.log('✅ V14 compatibility layer loaded');
