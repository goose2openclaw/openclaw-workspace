// ========== 宏观微观模块 (V14兼容版) ==========
const MacroMicro = {
    state: {
        level: 1,
        activeTab: 'macro',
        lastUpdate: null
    },
    
    init: function() {
        this.loadState();
        console.log('🌐 MacroMicro v14 initialized');
    },
    
    loadState: function() {
        try {
            var saved = localStorage.getItem('MacroMicroState');
            if (saved) {
                var data = JSON.parse(saved);
                this.state.level = data.level || 1;
            }
        } catch(e) {}
    },
    
    saveState: function() {
        try {
            localStorage.setItem('MacroMicroState', JSON.stringify({
                level: this.state.level
            }));
        } catch(e) {}
    },
    
    navigateLevel: function(level) {
        this.state.level = level;
        this.saveState();
        this.renderPanel();
    },
    
    renderPanel: function() {
        var container = document.getElementById('macroMicroPanel');
        if (!container) {
            container = document.createElement('div');
            container.id = 'macroMicroPanel';
            container.className = 'panel-overlay';
            document.body.appendChild(container);
        }
        
        var html = '<div class="panel-container">';
        html += '<div class="panel-header">';
        html += '<h3>🌐 宏观微观 - 7工具市场分析</h3>';
        html += '<button class="panel-close" onclick="MacroMicro.closePanel()">✕</button>';
        html += '</div>';
        html += '<div class="panel-body">';
        
        // Level Nav
        html += '<div class="level-nav">';
        html += '<button class="level-btn ' + (this.state.level === 1 ? 'active' : '') + '" onclick="MacroMicro.navigateLevel(1)">L1 总览</button>';
        html += '<button class="level-btn ' + (this.state.level === 2 ? 'active' : '') + '" onclick="MacroMicro.navigateLevel(2)">L2 市场</button>';
        html += '<button class="level-btn ' + (this.state.level === 3 ? 'active' : '') + '" onclick="MacroMicro.navigateLevel(3)">L3 持仓</button>';
        html += '<button class="level-btn ' + (this.state.level === 4 ? 'active' : '') + '" onclick="MacroMicro.navigateLevel(4)">L4 配置</button>';
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
    },
    
    renderLevel1: function() {
        return '<div class="level-content">' +
            '<h4>🌐 宏观微观总览</h4>' +
            '<p>7工具市场分析 - Top5 + 异动3</p>' +
            '<div class="module-grid" style="margin-top:15px;">' +
            '<div class="module-card" onclick="MacroMicro.navigateLevel(2)"><div class="module-icon">🐰</div><div class="module-name">打兔子</div></div>' +
            '<div class="module-card" onclick="MacroMicro.navigateLevel(2)"><div class="module-icon">🐹</div><div class="module-name">打地鼠</div></div>' +
            '<div class="module-card" onclick="MacroMicro.navigateLevel(2)"><div class="module-icon">🔮</div><div class="module-name">走着瞧</div></div>' +
            '<div class="module-card" onclick="MacroMicro.navigateLevel(2)"><div class="module-icon">👑</div><div class="module-name">跟大哥</div></div>' +
            '<div class="module-card" onclick="MacroMicro.navigateLevel(2)"><div class="module-icon">🍀</div><div class="module-name">搭便车</div></div>' +
            '<div class="module-card" onclick="MacroMicro.navigateLevel(2)"><div class="module-icon">💰</div><div class="module-name">薅羊毛</div></div>' +
            '<div class="module-card" onclick="MacroMicro.navigateLevel(2)"><div class="module-icon">👶</div><div class="module-name">穷孩子</div></div>' +
            '</div></div>';
    },
    
    renderLevel2: function() {
        return '<div class="level-content">' +
            '<h4>📊 7工具市场详情</h4>' +
            '<div style="background:var(--bg-tertiary);padding:15px;border-radius:8px;margin-top:15px;">' +
            '<p style="margin-bottom:10px;">🐰 <strong>打兔子</strong> - 前20主流加密货币</p>' +
            '<p style="color:var(--accent-green);">BTC +3.62% | ETH +2.85% | SOL +5.42%</p>' +
            '<p style="margin-top:10px;color:var(--text-muted);">异动: PEPE +12.5% | SHIB +8.3%</p>' +
            '</div></div>';
    },
    
    renderLevel3: function() {
        return '<div class="level-content">' +
            '<h4>💼 用户持仓状态</h4>' +
            '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-top:15px;">' +
            '<div style="padding:15px;background:var(--bg-tertiary);border-radius:8px;text-align:center;">' +
            '<div style="color:var(--accent-green);font-size:20px;">✓</div>' +
            '<div style="font-size:12px;color:var(--text-muted);">已投</div>' +
            '<div style="font-size:11px;margin-top:5px;">BTC, ETH, PEPE</div>' +
            '</div>' +
            '<div style="padding:15px;background:var(--bg-tertiary);border-radius:8px;text-align:center;">' +
            '<div style="color:var(--accent-gold);font-size:20px;">⏳</div>' +
            '<div style="font-size:12px;color:var(--text-muted);">在投</div>' +
            '<div style="font-size:11px;margin-top:5px;">SOL, SHIB, ZK</div>' +
            '</div>' +
            '<div style="padding:15px;background:var(--bg-tertiary);border-radius:8px;text-align:center;">' +
            '<div style="color:var(--accent-purple);font-size:20px;">⭐</div>' +
            '<div style="font-size:12px;color:var(--text-muted);">关注</div>' +
            '<div style="font-size:11px;margin-top:5px;">CRV, PENDLE, BNB</div>' +
            '</div>' +
            '</div></div>';
    },
    
    renderLevel4: function() {
        return '<div class="level-content">' +
            '<h4>⚙️ 配置设置</h4>' +
            '<div style="margin-top:15px;">' +
            '<div class="form-group"><label>市场数据源</label><select><option>Binance</option><option>Coinbase</option><option>OKX</option></select></div>' +
            '<div class="form-group"><label>更新频率</label><select><option>实时</option><option>5秒</option><option>30秒</option></select></div>' +
            '<button style="width:100%;padding:12px;background:var(--accent-green);border:none;border-radius:8px;color:#000;font-weight:600;margin-top:15px;cursor:pointer;">保存配置</button>' +
            '</div></div>';
    },
    
    closePanel: function() {
        var container = document.getElementById('macroMicroPanel');
        if (container) container.style.display = 'none';
    }
};

// Auto-init for v14
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() { MacroMicro.init(); });
} else {
    MacroMicro.init();
}
