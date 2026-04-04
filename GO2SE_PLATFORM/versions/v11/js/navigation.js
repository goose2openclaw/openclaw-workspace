/**
 * 4级导航系统
 * - 可展开子菜单 (投资工具, 风控中心)
 * - 实时搜索
 * - 面包屑导航
 */

window.NavigationManager = {
    currentPage: 'dashboard',
    breadcrumbs: [],
    
    init() {
        this.bindEvents();
        this.loadNavigationState();
        console.log('🧭 导航系统已初始化');
    },
    
    bindEvents() {
        // 子菜单展开/收起
        document.querySelectorAll('.nav-group-toggle').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const group = btn.closest('.nav-group');
                group.classList.toggle('expanded');
                this.saveNavigationState();
            });
        });
        
        // 子菜单项点击
        document.querySelectorAll('.nav-subitem').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const page = item.dataset.page;
                this.navigateTo(page);
                this.updateBreadcrumb(page);
            });
        });
        
        // 导航搜索
        const searchInput = document.getElementById('nav-search-input');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.handleSearch(e.target.value);
            });
            
            searchInput.addEventListener('focus', () => {
                if (searchInput.value) {
                    document.getElementById('nav-search-results').classList.add('active');
                }
            });
            
            searchInput.addEventListener('blur', () => {
                setTimeout(() => {
                    document.getElementById('nav-search-results').classList.remove('active');
                }, 200);
            });
        }
    },
    
    navigateTo(page) {
        // 更新活跃状态
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        
        const targetItem = document.querySelector(`[data-page="${page}"]`);
        if (targetItem) {
            targetItem.classList.add('active');
        }
        
        this.currentPage = page;
        this.updateBreadcrumb(page);
        
        // 通知路由系统
        if (window.Router) {
            Router.navigate(page);
        }
        
        this.saveNavigationState();
    },
    
    updateBreadcrumb(page) {
        const breadcrumb = document.getElementById('breadcrumb');
        if (!breadcrumb) return;
        
        // 构建面包屑路径
        const parts = page.split('/');
        let html = '<span class="breadcrumb-item" data-page="dashboard">首页</span>';
        
        if (parts.length > 1) {
            const groupNames = {
                'tools': '投资工具',
                'risk': '风控中心'
            };
            
            const pageNames = {
                'rabbit': '🐰 打兔子',
                'mole': '🐹 打地鼠',
                'oracle': '🔮 走着瞧',
                'leader': '👑 跟大哥',
                'hitchhiker': '🍀 搭便车',
                'airdrop': '💰 薅羊毛',
                'crowdsource': '👶 穷孩子',
                'dashboard': '⚠️ 实时监控',
                'alerts': '🚨 预警列表',
                'circuit': '🔒 熔断记录',
                'history': '📋 历史事故'
            };
            
            const group = parts[0];
            const subpage = parts[1] || 'index';
            
            if (groupNames[group]) {
                html += ` <span class="breadcrumb-sep">›</span> `;
                html += `<span class="breadcrumb-item" data-page="tools">${groupNames[group]}</span>`;
            }
            
            if (pageNames[subpage]) {
                html += ` <span class="breadcrumb-sep">›</span> `;
                html += `<span class="breadcrumb-item active">${pageNames[subpage]}</span>`;
            }
        }
        
        breadcrumb.innerHTML = html;
    },
    
    handleSearch(query) {
        const resultsContainer = document.getElementById('nav-search-results');
        if (!resultsContainer) return;
        
        if (!query || query.length < 2) {
            resultsContainer.classList.remove('active');
            return;
        }
        
        // 搜索数据
        const searchIndex = this.getSearchIndex();
        const results = this.search(query, searchIndex);
        
        if (results.length === 0) {
            resultsContainer.innerHTML = '<div class="search-result-item"><span class="search-result-desc">未找到结果</span></div>';
        } else {
            resultsContainer.innerHTML = results.map(r => `
                <div class="search-result-item" data-page="${r.page}">
                    <div class="search-result-title">${r.title}</div>
                    <div class="search-result-desc">${r.desc}</div>
                    <span class="search-result-type">${r.type}</span>
                </div>
            `).join('');
            
            // 绑定点击事件
            resultsContainer.querySelectorAll('.search-result-item[data-page]').forEach(item => {
                item.addEventListener('click', () => {
                    this.navigateTo(item.dataset.page);
                    resultsContainer.classList.remove('active');
                    document.getElementById('nav-search-input').value = '';
                });
            });
        }
        
        resultsContainer.classList.add('active');
    },
    
    getSearchIndex() {
        return [
            // 投资工具
            { page: 'tools/rabbit', title: '🐰 打兔子', desc: '前20主流加密货币趋势策略', type: '策略' },
            { page: 'tools/rabbit/config', title: '🐰 打兔子配置', desc: 'EMA/MACD/RSI/布林带参数', type: '配置' },
            { page: 'tools/rabbit/backtest', title: '🐰 打兔子回测', desc: '历史表现验证', type: '回测' },
            { page: 'tools/mole', title: '🐹 打地鼠', desc: '其他加密货币异动扫描', type: '策略' },
            { page: 'tools/mole/radar', title: '🐹 火控雷达', desc: '异动币种锁定', type: '工具' },
            { page: 'tools/oracle', title: '🔮 走着瞧', desc: '预测市场策略', type: '策略' },
            { page: 'tools/oracle/mirofish', title: '🔮 MiroFish仿真', desc: 'AI共识预测', type: '仿真' },
            { page: 'tools/leader', title: '👑 跟大哥', desc: '做市协作策略', type: '策略' },
            { page: 'tools/hitchhiker', title: '🍀 搭便车', desc: '跟单分成策略', type: '策略' },
            { page: 'tools/airdrop', title: '💰 薅羊毛', desc: '空投猎手策略', type: '策略' },
            { page: 'tools/crowdsource', title: '👶 穷孩子', desc: '众包赚钱策略', type: '策略' },
            
            // 风控中心
            { page: 'risk/dashboard', title: '⚠️ 实时监控', desc: '风控状态实时监控', type: '风控' },
            { page: 'risk/alerts', title: '🚨 预警列表', desc: '风险预警详情', type: '风控' },
            { page: 'risk/circuit', title: '🔒 熔断记录', desc: '熔断触发历史', type: '风控' },
            { page: 'risk/history', title: '📋 历史事故', desc: '事故复盘报告', type: '风控' },
            
            // Mapping
            { page: 'mapping/symbols', title: '💱 币种Mapping', desc: '币种交易所映射', type: '配置' },
            { page: 'mapping/strategies', title: '🎯 策略Mapping', desc: '策略参数配置', type: '配置' },
            
            // 通用页面
            { page: 'dashboard', title: '📊 仪表盘', desc: '账户总览', type: '页面' },
            { page: 'signals', title: '📡 信号列表', desc: '交易信号', type: '页面' },
            { page: 'portfolio', title: '💼 投资组合', desc: '持仓和盈亏', type: '页面' },
            { page: 'assets', title: '💰 资产看板', desc: '资产分布', type: '页面' },
            { page: 'settings', title: '⚙️ 系统设置', desc: '配置和偏好', type: '页面' }
        ];
    },
    
    search(query, index) {
        const q = query.toLowerCase();
        return index.filter(item => 
            item.title.toLowerCase().includes(q) ||
            item.desc.toLowerCase().includes(q)
        ).slice(0, 8);
    },
    
    saveNavigationState() {
        try {
            const state = {
                expandedGroups: [],
                currentPage: this.currentPage
            };
            
            document.querySelectorAll('.nav-group.expanded').forEach(group => {
                const toggle = group.querySelector('.nav-group-toggle');
                if (toggle) {
                    state.expandedGroups.push(toggle.dataset.group);
                }
            });
            
            localStorage.setItem('go2se_nav_state', JSON.stringify(state));
        } catch (e) {
            console.warn('导航状态保存失败:', e);
        }
    },
    
    loadNavigationState() {
        try {
            const saved = localStorage.getItem('go2se_nav_state');
            if (saved) {
                const state = JSON.parse(saved);
                
                // 恢复展开的分组
                state.expandedGroups?.forEach(groupId => {
                    const group = document.querySelector(`[data-group="${groupId}"]`)?.closest('.nav-group');
                    if (group) {
                        group.classList.add('expanded');
                    }
                });
                
                // 恢复当前页面
                if (state.currentPage) {
                    this.navigateTo(state.currentPage);
                }
            }
        } catch (e) {
            console.warn('导航状态恢复失败:', e);
        }
    },
    
    // 获取页面组件 (用于动态加载)
    getPageComponent(page) {
        const components = {
            // 投资工具
            'tools/rabbit': this.createToolPage('rabbit', '🐰 打兔子', {
                description: '前20主流加密货币趋势策略',
                strategies: ['EMA交叉', 'MACD动量', '布林带均值回归', 'RSI极端值'],
                symbols: ['BTC', 'ETH', 'BNB', 'SOL', 'XRP'],
                allocation: 25,
                winrate: 72
            }),
            'tools/mole': this.createToolPage('mole', '🐹 打地鼠', {
                description: '其他加密货币异动扫描',
                strategies: ['RSI超卖', '成交量突刺', '波动率突破', '大户追踪'],
                symbols: [],
                allocation: 20,
                winrate: 62
            }),
            'tools/oracle': this.createToolPage('oracle', '🔮 走着瞧', {
                description: '预测市场策略',
                strategies: ['MiroFish预测', '情绪分析', '共识预测'],
                symbols: ['POLYMATIC'],
                allocation: 15,
                winrate: 70
            }),
            'tools/leader': this.createToolPage('leader', '👑 跟大哥', {
                description: '做市协作策略',
                strategies: ['跟单策略', 'MiroFish评估'],
                symbols: ['BTC', 'ETH', 'SOL'],
                allocation: 15,
                winrate: 68
            }),
            'tools/hitchhiker': this.createToolPage('hitchhiker', '🍀 搭便车', {
                description: '跟单分成策略',
                strategies: ['信号优化器'],
                symbols: ['BTC', 'ETH', 'BNB', 'SOL'],
                allocation: 10,
                winrate: 75
            }),
            'tools/airdrop': this.createToolPage('airdrop', '💰 薅羊毛', {
                description: '空投猎手策略',
                strategies: ['空投扫描', '授权检查'],
                symbols: [],
                allocation: 3,
                winrate: 65
            }),
            'tools/crowdsource': this.createToolPage('crowdsource', '👶 穷孩子', {
                description: '众包赚钱策略',
                strategies: ['EvoMap任务', '社交变现'],
                symbols: [],
                allocation: 2,
                winrate: 60
            }),
            
            // 风控中心
            'risk/dashboard': this.createRiskPage('实时监控', {
                items: ['仓位监控', '波动监控', '流动性监控', '情绪监控']
            }),
            'risk/alerts': this.createRiskPage('预警列表', {
                items: ['高波动预警', '流动性预警', '异常交易预警', '情绪过热预警']
            }),
            'risk/circuit': this.createRiskPage('熔断记录', {
                items: ['仓位熔断', '波动熔断', '亏损熔断', '流动性熔断']
            }),
            'risk/history': this.createRiskPage('历史事故', {
                items: ['事故复盘', '根因分析', '修复记录', '预防措施']
            })
        };
        
        return components[page] || this.create404(page);
    },
    
    createToolPage(toolId, title, config) {
        return `
            <div class="tool-page" id="tool-${toolId}">
                <div class="page-header">
                    <div class="page-title">
                        <h1>${title}</h1>
                        <p class="page-desc">${config.description}</p>
                    </div>
                    <div class="page-actions">
                        <button class="btn btn-primary" onclick="NavigationManager.runBacktest('${toolId}')">
                            🧪 回测
                        </button>
                        <button class="btn btn-secondary" onclick="NavigationManager.configTool('${toolId}')">
                            ⚙️ 配置
                        </button>
                    </div>
                </div>
                
                <div class="tool-stats">
                    <div class="stat-card">
                        <div class="stat-label">当前胜率</div>
                        <div class="stat-value">${config.winrate}%</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">仓位分配</div>
                        <div class="stat-value">${config.allocation}%</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">子策略数</div>
                        <div class="stat-value">${config.strategies.length}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">交易币种</div>
                        <div class="stat-value">${config.symbols.length || '全部'}</div>
                    </div>
                </div>
                
                <div class="tool-content">
                    <div class="content-section">
                        <h2>📊 子策略</h2>
                        <div class="strategy-list">
                            ${config.strategies.map((s, i) => `
                                <div class="strategy-item">
                                    <div class="strategy-name">${s}</div>
                                    <div class="strategy-actions">
                                        <button class="btn-icon" title="回测">🧪</button>
                                        <button class="btn-icon" title="配置">⚙️</button>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    
                    <div class="content-section">
                        <h2>📈 绩效图表</h2>
                        <div class="chart-placeholder" id="tool-chart-${toolId}">
                            图表加载中...
                        </div>
                    </div>
                </div>
            </div>
        `;
    },
    
    createRiskPage(title, config) {
        return `
            <div class="risk-page" id="risk-${title}">
                <div class="page-header">
                    <div class="page-title">
                        <h1>🛡️ ${title}</h1>
                    </div>
                </div>
                <div class="risk-items">
                    ${config.items.map(item => `
                        <div class="risk-item">
                            <div class="risk-icon">⚠️</div>
                            <div class="risk-content">
                                <div class="risk-title">${item}</div>
                                <div class="risk-status">正常</div>
                            </div>
                            <div class="risk-badge safe">安全</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    },
    
    create404(page) {
        return `
            <div class="page-404">
                <h1>页面未找到</h1>
                <p>页面 "${page}" 不存在</p>
                <button class="btn btn-primary" onclick="NavigationManager.navigateTo('dashboard')">
                    返回首页
                </button>
            </div>
        `;
    },
    
    runBacktest(toolId) {
        console.log(`🧪 运行 ${toolId} 回测`);
        // TODO: 调用回测API
    },
    
    configTool(toolId) {
        console.log(`⚙️ 配置 ${toolId}`);
        // TODO: 打开配置面板
    }
};

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    NavigationManager.init();
});
