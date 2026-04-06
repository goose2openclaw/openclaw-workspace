// ========== 交易面板模块 (V14兼容版) ==========
const TradingPanel = {
    state: {
        level: 1,
        activeTab: 'live',
        decisions: [
            { step: '信号扫描', status: 'completed' },
            { step: '策略匹配', status: 'completed' },
            { step: '风险评估', status: 'running' },
            { step: '执行确认', status: 'pending' }
        ],
        tools: {
            rabbit: { name: '打兔子', icon: '🐰', status: 'scanning', signals: 12 },
            mole: { name: '打地鼠', icon: '🐹', status: 'analyzing', signals: 8 },
            oracle: { name: '走着瞧', icon: '🔮', status: 'running', signals: 5 },
            leader: { name: '跟大哥', icon: '👑', status: 'scanning', signals: 3 },
            hitchhiker: { name: '搭便车', icon: '🍀', status: 'idle', signals: 0 },
            airdrop: { name: '薅羊毛', icon: '💰', status: 'scanning', signals: 15 },
            crowdsource: { name: '穷孩子', icon: '👶', status: 'idle', signals: 0 }
        },
        streams: {
            rabbit: [
                { symbol: 'BTC', change: 3.62, signal: '看涨', confidence: 85 },
                { symbol: 'ETH', change: 2.85, signal: '强势', confidence: 78 },
                { symbol: 'SOL', change: 5.42, signal: '突破', confidence: 82 }
            ],
            mole: [
                { symbol: 'PEPE', change: 12.5, signal: '异动', confidence: 72 },
                { symbol: 'SHIB', change: 8.3, signal: '反弹', confidence: 65 }
            ],
            oracle: [
                { symbol: 'BTC-50K', change: 5.2, signal: '预测应验', confidence: 88 }
            ],
            leader: [
                { symbol: 'CRV', change: 4.2, signal: '跟单', confidence: 75 }
            ],
            hitchhiker: [
                { symbol: 'PENDLE', change: 5.8, signal: '跟单', confidence: 70 }
            ],
            airdrop: [
                { symbol: 'ZK', change: 5.2, signal: '空投猎取', confidence: 80 },
                { symbol: 'STARK', change: 3.8, signal: '空投猎取', confidence: 75 }
            ],
            crowdsource: [
                { symbol: 'AI-TASK', change: 0, signal: '任务众包', confidence: 60 }
            ]
        }
    },
    
    init: function() {
        this.loadState();
        this.startStreaming();
        console.log('⚡ TradingPanel v14 initialized');
    },
    
    loadState: function() {
        try {
            var saved = localStorage.getItem('TradingPanelState');
            if (saved) {
                var data = JSON.parse(saved);
                this.state.level = data.level || 1;
                this.state.activeTab = data.activeTab || 'live';
            }
        } catch(e) {}
    },
    
    saveState: function() {
        try {
            localStorage.setItem('TradingPanelState', JSON.stringify({
                level: this.state.level,
                activeTab: this.state.activeTab
            }));
        } catch(e) {}
    },
    
    navigateLevel: function(level) {
        this.state.level = level;
        this.saveState();
        this.renderPanel();
    },
    
    selectTab: function(tab) {
        this.state.activeTab = tab;
        this.saveState();
        this.renderPanel();
    },
    
    startStreaming: function() {
        var self = this;
        setInterval(function() {
            // 模拟数据更新
            Object.keys(self.streams).forEach(function(key) {
                self.streams[key].forEach(function(item) {
                    if (Math.random() > 0.7) {
                        item.change = parseFloat((item.change + (Math.random() - 0.5) * 0.5).toFixed(2));
                        item.confidence = Math.min(100, Math.max(50, item.confidence + Math.floor(Math.random() * 5 - 2)));
                    }
                });
            });
            
            // 更新决策状态
            self.decisions.forEach(function(d, i) {
                if (d.status === 'running') {
                    d.status = 'completed';
                } else if (d.status === 'completed' && i < self.decisions.length - 1) {
                    if (self.decisions[i + 1].status === 'pending') {
                        self.decisions[i + 1].status = 'running';
                    }
                }
            });
        }, 5000);
    },
    
    renderPanel: function() {
        var container = document.getElementById('tradingPanelContainer');
        if (!container) {
            container = document.createElement('div');
            container.id = 'tradingPanelContainer';
            container.className = 'panel-overlay';
            document.body.appendChild(container);
        }
        
        var html = '<div class="panel-container" style="max-width:1000px;">';
        html += '<div class="panel-header">';
        html += '<h3>⚡ 交易面板</h3>';
        html += '<button class="panel-close" onclick="TradingPanel.closePanel()">✕</button>';
        html += '</div>';
        html += '<div class="panel-body">';
        
        // Tab切换
        html += '<div style="display:flex;gap:8px;margin-bottom:20px;">';
        var tabs = [
            { id: 'live', name: '实时流', icon: '⚡' },
            { id: 'backtest', name: '回测', icon: '📊' },
            { id: 'paper', name: '模拟', icon: '🎮' },
            { id: 'simulation', name: '仿真', icon: '🔮' }
        ];
        var self = this;
        tabs.forEach(function(tab) {
            var isActive = self.state.activeTab === tab.id;
            html += '<button onclick="TradingPanel.selectTab(\'' + tab.id + '\')" style="flex:1;padding:10px;background:' + (isActive ? 'rgba(124,58,237,0.2)' : 'var(--bg-tertiary)') + ';border:1px solid ' + (isActive ? '#7c3aed' : 'var(--border-color)') + ';color:' + (isActive ? '#a78bfa' : 'var(--text-secondary)') + ';border-radius:8px;cursor:pointer;font-size:12px;">' + tab.icon + ' ' + tab.name + '</button>';
        });
        html += '</div>';
        
        // 根据Tab显示内容
        if (this.state.activeTab === 'live') {
            html += this.renderLiveContent();
        } else if (this.state.activeTab === 'backtest') {
            html += this.renderBacktestContent();
        } else if (this.state.activeTab === 'paper') {
            html += this.renderPaperContent();
        } else {
            html += this.renderSimulationContent();
        }
        
        html += '</div></div>';
        container.innerHTML = html;
        container.style.display = 'block';
    },
    
    renderLiveContent: function() {
        var self = this;
        var html = '<div>';
        
        // 决策流程
        html += '<div style="background:var(--bg-tertiary);border-radius:10px;padding:15px;margin-bottom:20px;">';
        html += '<div style="font-size:14px;font-weight:600;margin-bottom:15px;">📋 决策流程</div>';
        html += '<div style="display:flex;gap:5px;overflow-x:auto;padding-bottom:10px;">';
        this.decisions.forEach(function(d, i) {
            var color = d.status === 'completed' ? '#00d4aa' : d.status === 'running' ? '#f59e0b' : '#666';
            html += '<div style="flex:1;min-width:100px;text-align:center;">';
            html += '<div style="width:30px;height:30px;border-radius:50%;background:' + color + ';color:#000;display:inline-flex;align-items:center;justify-content:center;font-size:14px;margin-bottom:5px;">' + (d.status === 'completed' ? '&#x2713;' : d.status === 'running' ? '&#x27F3;' : (i+1)) + '</div>';
            html += '<div style="font-size:11px;color:' + color + ';">' + d.step + '</div>';
            html += '</div>';
            if (i < self.decisions.length - 1) {
                html += '<div style="flex:0;color:#666;align-self:center;">-&gt;</div>';
            }
        });
        html += '</div></div>';
        
        // 7工具实时流
        html += '<div style="font-size:14px;font-weight:600;margin-bottom:15px;">⚡ 7工具实时流</div>';
        html += '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:10px;margin-bottom:20px;">';
        
        Object.keys(this.tools).forEach(function(key) {
            var tool = self.tools[key];
            var stream = self.streams[key] || [];
            var topItem = stream[0] || {};
            var statusColor = tool.status === 'scanning' ? '#00d4aa' : tool.status === 'analyzing' ? '#f59e0b' : tool.status === 'running' ? '#7c3aed' : '#666';
            
            html += '<div style="background:var(--bg-tertiary);border:1px solid rgba(124,58,237,0.2);border-radius:10px;padding:12px;">';
            html += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">';
            html += '<div style="display:flex;align-items:center;gap:8px;">';
            html += '<span style="font-size:20px;">' + tool.icon + '</span>';
            html += '<span style="font-weight:600;">' + tool.name + '</span>';
            html += '</div>';
            html += '<span style="font-size:10px;padding:2px 6px;background:rgba(0,0,0,0.5);border-radius:10px;color:' + statusColor + ';">&#x25CF; ' + tool.status + '</span>';
            html += '</div>';
            
            if (topItem.symbol) {
                html += '<div style="padding:8px;background:rgba(0,0,0,0.3);border-radius:6px;">';
                html += '<div style="display:flex;justify-content:space-between;margin-bottom:5px;">';
                html += '<span style="font-weight:600;">' + topItem.symbol + '</span>';
                html += '<span style="color:' + (topItem.change >= 0 ? '#00d4aa' : '#ef4444') + ';">' + (topItem.change >= 0 ? '+' : '') + topItem.change + '%</span>';
                html += '</div>';
                html += '<div style="font-size:11px;color:var(--text-muted);">' + topItem.signal + ' | ' + topItem.confidence + '%置信</div>';
                html += '</div>';
            }
            
            html += '</div>';
        });
        
        html += '</div>';
        html += '<button onclick="TradingPanel.navigateLevel(2)" style="width:100%;padding:12px;background:rgba(124,58,237,0.2);border:1px solid #7c3aed;color:#a78bfa;border-radius:8px;cursor:pointer;font-weight:600;">查看详情 &#x2192;</button>';
        html += '</div>';
        
        return html;
    },
    
    renderBacktestContent: function() {
        return '<div>' +
            '<div style="background:var(--bg-tertiary);border-radius:10px;padding:15px;margin-bottom:20px;">' +
            '<div style="font-size:14px;font-weight:600;margin-bottom:15px;">📊 回测交易</div>' +
            '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:15px;">' +
            '<div style="padding:12px;background:rgba(0,212,170,0.1);border-radius:8px;text-align:center;"><div style="font-size:20px;font-weight:700;color:#00d4aa;">72.3%</div><div style="font-size:11px;color:var(--text-muted);">组合胜率</div></div>' +
            '<div style="padding:12px;background:rgba(0,0,0,0.3);border-radius:8px;text-align:center;"><div style="font-size:20px;font-weight:700;">1.85</div><div style="font-size:11px;color:var(--text-muted);">夏普比率</div></div>' +
            '</div>' +
            '<div style="font-size:12px;color:var(--text-muted);margin-bottom:15px;">策略: EMA交叉 | RSI超卖 | MACD背离 | 布林带</div>' +
            '<div style="padding:12px;background:rgba(0,0,0,0.3);border-radius:8px;margin-bottom:15px;">' +
            '<div style="display:flex;justify-content:space-between;margin-bottom:8px;"><span style="color:var(--text-muted);">回测周期</span><span>2024-01-01 ~ 2026-04-01</span></div>' +
            '<div style="display:flex;justify-content:space-between;margin-bottom:8px;"><span style="color:var(--text-muted);">总交易次数</span><span>1,234</span></div>' +
            '<div style="display:flex;justify-content:space-between;"><span style="color:var(--text-muted);">盈利交易</span><span style="color:#00d4aa;">892 (72.3%)</span></div>' +
            '</div>' +
            '<button onclick="TradingPanel.navigateLevel(2)" style="width:100%;padding:12px;background:rgba(0,212,170,0.2);border:1px solid #00d4aa;color:#00d4aa;border-radius:8px;cursor:pointer;font-weight:600;">开始回测 &#x2192;</button>' +
            '</div></div>';
    },
    
    renderPaperContent: function() {
        return '<div>' +
            '<div style="background:var(--bg-tertiary);border-radius:10px;padding:15px;margin-bottom:20px;">' +
            '<div style="font-size:14px;font-weight:600;margin-bottom:15px;">🎮 模拟交易</div>' +
            '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:15px;">' +
            '<div style="padding:12px;background:rgba(245,158,11,0.1);border-radius:8px;text-align:center;"><div style="font-size:20px;font-weight:700;color:#f59e0b;">+$1,234</div><div style="font-size:11px;color:var(--text-muted);">模拟收益</div></div>' +
            '<div style="padding:12px;background:rgba(0,0,0,0.3);border-radius:8px;text-align:center;"><div style="font-size:20px;font-weight:700;">23</div><div style="font-size:11px;color:var(--text-muted);">持仓数</div></div>' +
            '</div>' +
            '<div style="font-size:12px;color:var(--text-muted);margin-bottom:15px;">状态: <span style="color:#f59e0b;">&#x25CF; 模拟运行中</span></div>' +
            '<button onclick="TradingPanel.navigateLevel(2)" style="width:100%;padding:12px;background:rgba(0,212,170,0.2);border:1px solid #00d4aa;color:#00d4aa;border-radius:8px;cursor:pointer;font-weight:600;">管理持仓 &#x2192;</button>' +
            '</div></div>';
    },
    
    renderSimulationContent: function() {
        return '<div>' +
            '<div style="background:var(--bg-tertiary);border-radius:10px;padding:15px;margin-bottom:20px;">' +
            '<div style="font-size:14px;font-weight:600;margin-bottom:15px;">🔮 MiroFish 回测仿真</div>' +
            '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:15px;">' +
            '<div style="padding:12px;background:rgba(124,58,237,0.1);border-radius:8px;text-align:center;"><div style="font-size:20px;font-weight:700;color:#a78bfa;">87.6%</div><div style="font-size:11px;color:var(--text-muted);">仿真评分</div></div>' +
            '<div style="padding:12px;background:rgba(0,0,0,0.3);border-radius:8px;text-align:center;"><div style="font-size:20px;font-weight:700;">1000</div><div style="font-size:11px;color:var(--text-muted);">智能体</div></div>' +
            '</div>' +
            '<div style="font-size:12px;color:var(--text-muted);margin-bottom:15px;">仿真维度: 投资组合 | 风控规则 | 多样化 | 7工具 | 25维度</div>' +
            '<div style="padding:12px;background:rgba(0,0,0,0.3);border-radius:8px;margin-bottom:15px;">' +
            '<div style="font-size:12px;color:#00d4aa;margin-bottom:8px;">&#x2713; 投资组合 (82分)</div>' +
            '<div style="font-size:12px;color:#00d4aa;margin-bottom:8px;">&#x2713; 风控规则 (85分)</div>' +
            '<div style="font-size:12px;color:#00d4aa;margin-bottom:8px;">&#x2713; 打兔子 (92分)</div>' +
            '<div style="font-size:12px;color:#f59e0b;">&#x27F3; 走着瞧 (78分)</div>' +
            '</div>' +
            '<button onclick="TradingPanel.navigateLevel(2)" style="width:100%;padding:12px;background:rgba(124,58,237,0.2);border:1px solid #7c3aed;color:#a78bfa;border-radius:8px;cursor:pointer;font-weight:600;">运行新仿真 &#x2192;</button>' +
            '</div></div>';
    },
    
    closePanel: function() {
        var container = document.getElementById('tradingPanelContainer');
        if (container) container.style.display = 'none';
    }
};

// Auto-init for v14
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() { TradingPanel.init(); });
} else {
    TradingPanel.init();
}
