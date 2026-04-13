// ========== 平台介绍模块 (V14) ==========
const PlatformIntro = {
    state: { level: 1 },
    
    init: function() { console.log('🚀 PlatformIntro initialized'); },
    
    renderPanel: function(level) {
        level = level || 1;
        var contents = {
            1: { title: '平台总览', data: this.getOverview() },
            2: { title: '核心功能', data: this.getFeatures() },
            3: { title: '技术架构', data: this.getArchitecture() },
            4: { title: '版本信息', data: this.getVersion() }
        };
        var c = contents[level] || contents[1];
        return '<div class="module-detail">' +
            '<h2>' + c.title + '</h2>' +
            c.data +
            '</div>';
    },
    
    getOverview: function() {
        return '<div class="detail-grid">' +
            '<div class="detail-card"><div class="detail-icon">🪿</div><div class="detail-title">GO2SE</div><div class="detail-desc">AI量化投资平台</div></div>' +
            '<div class="detail-card"><div class="detail-icon">📊</div><div class="detail-title">7大工具</div><div class="detail-desc">北斗七鑫投资体系</div></div>' +
            '<div class="detail-card"><div class="detail-icon">🧠</div><div class="detail-title">MiroFish</div><div class="detail-desc">100智能体预测</div></div>' +
            '<div class="detail-card"><div class="detail-icon">🔮</div><div class="detail-title">25维度</div><div class="detail-desc">全向仿真评测</div></div>' +
            '</div>' +
            '<div class="detail-section"><h4>平台优势</h4><ul>' +
            '<li>✅ 全自动化投资决策</li><li>✅ 多策略并行执行</li>' +
            '<li>✅ 实时风险控制</li><li>✅ 跨市场套利</li></ul></div>';
    },
    
    getFeatures: function() {
        return '<div class="detail-section"><h4>核心功能</h4>' +
            '<div class="feature-list">' +
            '<div class="feature-item"><span class="feature-icon">🐰</span><span>打兔子 - 前20主流加密货币</span></div>' +
            '<div class="feature-item"><span class="feature-icon">🐹</span><span>打地鼠 - 其他加密货币</span></div>' +
            '<div class="feature-item"><span class="feature-icon">🔮</span><span>走着瞧 - 预测市场</span></div>' +
            '<div class="feature-item"><span class="feature-icon">👑</span><span>跟大哥 - 做市商跟单</span></div>' +
            '<div class="feature-item"><span class="feature-icon">🍀</span><span>搭便车 - 跟单分成</span></div>' +
            '<div class="feature-item"><span class="feature-icon">💰</span><span>薅羊毛 - 空投猎手</span></div>' +
            '<div class="feature-item"><span class="feature-icon">👶</span><span>穷孩子 - 众包赚钱</span></div>' +
            '</div></div>';
    },
    
    getArchitecture: function() {
        return '<div class="detail-section"><h4>技术架构</h4>' +
            '<div class="arch-diagram">' +
            '<div class="arch-layer">🌐 表现层 - React/Vue</div>' +
            '<div class="arch-arrow">↓</div>' +
            '<div class="arch-layer">⚙️ 逻辑层 - Python/AI</div>' +
            '<div class="arch-arrow">↓</div>' +
            '<div class="arch-layer">💾 数据层 - MongoDB/Redis</div>' +
            '<div class="arch-arrow">↓</div>' +
            '<div class="arch-layer">📡 交易所API - Binance/ByBit</div>' +
            '</div></div>';
    },
    
    getVersion: function() {
        return '<div class="detail-section"><h4>版本信息</h4>' +
            '<div class="version-info">' +
            '<div class="version-row"><span>当前版本</span><span class="mono">v14.3</span></div>' +
            '<div class="version-row"><span>发布日期</span><span>2026-04-06</span></div>' +
            '<div class="version-row"><span>构建时间</span><span>' + new Date().toLocaleString() + '</span></div>' +
            '</div></div>';
    }
};

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() { PlatformIntro.init(); });
} else { PlatformIntro.init(); }
