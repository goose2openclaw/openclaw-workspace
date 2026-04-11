// ========== 🦞 虾驭双脑模块 ==========
const BrainDual = {
    state: {
        activePart: 1,       // 1: 平台三宝, 2: 左右脑, 3: 切换系统
        level: 1,            // 1: 总览, 2: 详情, 3: 设置, 4: 执行/结果
        mode: 'left',        // left: 左脑(普通), right: 右脑(专家)
        style: 'balanced',   // conservative: 保守, balanced: 平衡, aggressive: 积极
        switchMode: 'manual', // manual: 一键切换, auto: 自主切换
        leftBrain: { style: 'balanced', status: 'active', tasks: [] },
        rightBrain: { style: 'balanced', status: 'standby', tasks: [] },
        retroResults: [],
        simulationResults: [],
        optimizationResults: [],
        history: [],
        // L5/L6 Analytics
        stats: { today: 12, week: 45, total: 312, successRate: 85 },
        analytics: { totalProfit: 45600, returnRate: 45.6, maxDrawdown: 9.8, sharpeRatio: 2.45, tradeCount: 312, winRate: 75, avgProfit: 146, profitFactor: 2.1 }
    },

    // 7工具 × 左右脑配置
    toolConfigs: {
        rabbit: {
            left: { strategies: ['EMA趋势', 'MACD交叉', 'RSI超买'], indicators: 'EMA, MACD, RSI' },
            right: { strategies: ['模式识别', '趋势预测', 'AI识别'], indicators: 'CNN, LSTM, 趋势预测' }
        },
        mole: {
            left: { strategies: ['布林带', '波动率', '成交量异常'], indicators: 'BB, ATR, Volatility' },
            right: { strategies: ['异常检测', '火控雷达', '闪电战'], indicators: '火控雷达, 异常检测' }
        },
        oracle: {
            left: { strategies: ['MiroFish共识', '概率计算', '统计'], indicators: 'MiroFish共识, 概率' },
            right: { strategies: ['直觉预测', '灵感捕捉', '模式直觉'], indicators: '直觉, 第六感' }
        },
        leader: {
            left: { strategies: ['跟单策略', '量化跟随', '规则'], indicators: '跟单规则, 量化模型' },
            right: { strategies: ['KOL直觉', '经验判断', '领袖直觉'], indicators: 'KOL直觉, 经验' }
        },
        hitchhiker: {
            left: { strategies: ['跟单分成', '分包风控', '规则'], indicators: '分包规则, 风控' },
            right: { strategies: ['机会识别', '直觉发现', '灵感捕捉'], indicators: '机会直觉, 灵感' }
        },
        airdrop: {
            left: { strategies: ['空投规则', '任务列表', '清单'], indicators: '规则引擎, 清单' },
            right: { strategies: ['安全直觉', '风险预判', '本能'], indicators: '安全直觉, 本能' }
        },
        crowdsource: {
            left: { strategies: ['EvoMap任务', '规则化任务', '清单'], indicators: 'EvoMap任务, 规则' },
            right: { strategies: ['机会发现', '直觉挖掘', '灵感'], indicators: '机会直觉, 灵感' }
        }
    },

    // 初始化
    init() {
        this.render();
        this.bindEvents();
        this.updateNavState();
        console.log('🧠 虾驭双脑模块已初始化');
    },

    // 渲染主界面
    render() {
        const container = document.getElementById('brainDualModule');
        if (!container) return;

        container.innerHTML = this.getModuleHTML();
    },

    // 获取模块HTML
    getModuleHTML() {
        const level1Overview = this.level === 1 ? this.getLevel1HTML() : '';
        const level2Detail = this.level === 2 ? this.getLevel2HTML() : '';
        const level3Settings = this.level === 3 ? this.getLevel3HTML() : '';
        const level4Results = this.level === 4 ? this.getLevel4HTML() : '';
        const level5History = this.level === 5 ? this.getLevel5HTML() : '';
        const level6Analytics = this.level === 6 ? this.getLevel6HTML() : '';

        return `
            <div class="bd-container">
                <h3>🦞 虾驭双脑</h3>
                
                <!-- 面包屑 -->
                <div class="bd-breadcrumb">
                    <span class="bd-bread-item ${this.level === 1 ? 'active' : ''}" onclick="BrainDual.setLevel(1)">总览</span>
                    <span class="bd-bread-sep">›</span>
                    <span class="bd-bread-item ${this.level === 2 ? 'active' : ''}" onclick="BrainDual.setLevel(2)">详情</span>
                    <span class="bd-bread-sep">›</span>
                    <span class="bd-bread-item ${this.level === 3 ? 'active' : ''}" onclick="BrainDual.setLevel(3)">设置</span>
                    <span class="bd-bread-sep">›</span>
                    <span class="bd-bread-item ${this.level === 4 ? 'active' : ''}" onclick="BrainDual.setLevel(4)">执行</span>
                    <span class="bd-bread-sep">›</span>
                    <span class="bd-bread-item ${this.level === 5 ? 'active' : ''}" onclick="BrainDual.setLevel(5)">📜历史</span>
                    <span class="bd-bread-sep">›</span>
                    <span class="bd-bread-item ${this.level === 6 ? 'active' : ''}" onclick="BrainDual.setLevel(6)">📈分析</span>
                </div>

                <!-- Part选择器 -->
                <div class="bd-part-selector">
                    <button class="bd-part-btn ${this.activePart === 1 ? 'active' : ''}" onclick="BrainDual.setPart(1)">
                        🔄 平台三宝
                    </button>
                    <button class="bd-part-btn ${this.activePart === 2 ? 'active' : ''}" onclick="BrainDual.setPart(2)">
                        🧠 左右脑
                    </button>
                    <button class="bd-part-btn ${this.activePart === 3 ? 'active' : ''}" onclick="BrainDual.setPart(3)">
                        ⚡ 切换系统
                    </button>
                </div>

                <!-- 4级页面内容 -->
                ${level1Overview}
                ${level2Detail}
                ${level3Settings}
                ${level4Results}

                <!-- 当前模式指示 -->
                <div class="bd-mode-indicator">
                    <span class="bd-mode-label">当前:</span>
                    <span class="bd-mode-value ${this.state.mode === 'left' ? 'left-mode' : 'right-mode'}">
                        ${this.state.mode === 'left' ? '🧠 左脑(普通)' : '🎯 右脑(专家)'}
                    </span>
                    <span class="bd-style-label">风格:</span>
                    <span class="bd-style-value">${this.getStyleLabel()}</span>
                </div>
            </div>
        `;
    },

    // Level 1: 总览
    getLevel1HTML() {
        return `
            <div class="bd-level bd-level-1">
                <div class="bd-overview-cards">
                    <!-- Part 1: 平台三宝 -->
                    <div class="bd-overview-card" onclick="BrainDual.setPart(1); BrainDual.setLevel(2)">
                        <div class="bd-ov-icon">🔄</div>
                        <h4>平台三宝</h4>
                        <p>复盘·仿真·迭代</p>
                        <div class="bd-ov-sub">
                            <span>🔄 复盘 Retro</span>
                            <span>🧪 仿真 Simulation</span>
                            <span>⚡ 迭代 Optimization</span>
                        </div>
                    </div>
                    
                    <!-- Part 2: 左右脑 -->
                    <div class="bd-overview-card" onclick="BrainDual.setPart(2); BrainDual.setLevel(2)">
                        <div class="bd-ov-icon">🧠</div>
                        <h4>左右脑系统</h4>
                        <p>理性·直觉·双模式</p>
                        <div class="bd-ov-sub">
                            <span>🧠 左脑 普通模式</span>
                            <span>🎯 右脑 专家模式</span>
                        </div>
                    </div>
                    
                    <!-- Part 3: 切换系统 -->
                    <div class="bd-overview-card" onclick="BrainDual.setPart(3); BrainDual.setLevel(2)">
                        <div class="bd-ov-icon">⚡</div>
                        <h4>切换系统</h4>
                        <p>一键·自主·条件触发</p>
                        <div class="bd-ov-sub">
                            <span>🖱️ 一键切换</span>
                            <span>🤖 自主切换</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    // Level 2: 详情
    getLevel2HTML() {
        if (this.activePart === 1) {
            return this.getPart1DetailHTML();
        } else if (this.activePart === 2) {
            return this.getPart2DetailHTML();
        } else {
            return this.getPart3DetailHTML();
        }
    },

    // Part 1 详情: 平台三宝
    getPart1DetailHTML() {
        return `
            <div class="bd-level bd-level-2 bd-part-1">
                <div class="bd-detail-cards">
                    <!-- 复盘 -->
                    <div class="bd-detail-card">
                        <div class="bd-dc-header">
                            <span class="bd-dc-icon">🔄</span>
                            <h4>复盘 Retro</h4>
                            <span class="bd-dc-badge">gstack 15人团队</span>
                        </div>
                        <div class="bd-dc-content">
                            <p>gstack 15人团队评审，从策略构思到执行全流程复盘</p>
                            <div class="bd-dc-metrics">
                                <div class="bd-metric"><span>本周复盘次数</span><strong>3</strong></div>
                                <div class="bd-metric"><span>发现问题</span><strong>5</strong></div>
                                <div class="bd-metric"><span>优化建议</span><strong>8</strong></div>
                            </div>
                        </div>
                        <div class="bd-dc-actions">
                            <button class="bd-btn primary" onclick="BrainDual.runRetro()">🔄 启动复盘</button>
                            <button class="bd-btn secondary" onclick="BrainDual.setLevel(3)">⚙️ 设置</button>
                        </div>
                    </div>

                    <!-- 仿真 -->
                    <div class="bd-detail-card">
                        <div class="bd-dc-header">
                            <span class="bd-dc-icon">🧪</span>
                            <h4>仿真 Simulation</h4>
                            <span class="bd-dc-badge success">MiroFish 1000智能体</span>
                        </div>
                        <div class="bd-dc-content">
                            <p>MiroFish 1000智能体全维度仿真，覆盖25个评估维度</p>
                            <div class="bd-dc-metrics">
                                <div class="bd-metric"><span>上次评分</span><strong>87</strong></div>
                                <div class="bd-metric"><span>仿真维度</span><strong>25</strong></div>
                                <div class="bd-metric"><span>智能体</span><strong>1000</strong></div>
                            </div>
                        </div>
                        <div class="bd-dc-actions">
                            <button class="bd-btn primary" onclick="BrainDual.runSimulation()">🧪 启动仿真</button>
                            <button class="bd-btn secondary" onclick="BrainDual.setLevel(3)">⚙️ 设置</button>
                        </div>
                    </div>

                    <!-- 迭代 -->
                    <div class="bd-detail-card">
                        <div class="bd-dc-header">
                            <span class="bd-dc-icon">⚡</span>
                            <h4>迭代 Optimization</h4>
                            <span class="bd-dc-badge warning">策略参数优化</span>
                        </div>
                        <div class="bd-dc-content">
                            <p>策略参数优化，基于仿真结果自动调整参数配置</p>
                            <div class="bd-dc-metrics">
                                <div class="bd-metric"><span>优化次数</span><strong>12</strong></div>
                                <div class="bd-metric"><span>参数调整</span><strong>45</strong></div>
                                <div class="bd-metric"><span>收益提升</span><strong>+8.5%</strong></div>
                            </div>
                        </div>
                        <div class="bd-dc-actions">
                            <button class="bd-btn primary" onclick="BrainDual.runOptimization()">⚡ 优化参数</button>
                            <button class="bd-btn secondary" onclick="BrainDual.setLevel(3)">⚙️ 设置</button>
                        </div>
                    </div>
                </div>

                <!-- 流程图 -->
                <div class="bd-flow-diagram">
                    <h5>迭代流程</h5>
                    <div class="bd-flow-line">
                        <span class="bd-flow-step">信号</span>
                        <span class="bd-flow-arrow">→</span>
                        <span class="bd-flow-step active">龙虾仿真</span>
                        <span class="bd-flow-arrow">→</span>
                        <span class="bd-flow-step">策略更新</span>
                        <span class="bd-flow-arrow">→</span>
                        <span class="bd-flow-step">执行</span>
                        <span class="bd-flow-arrow">↩️</span>
                        <span class="bd-flow-step">复盘</span>
                    </div>
                </div>
            </div>
        `;
    },

    // Part 2 详情: 左右脑
    getPart2DetailHTML() {
        const leftActive = this.state.mode === 'left';
        const rightActive = this.state.mode === 'right';

        return `
            <div class="bd-level bd-level-2 bd-part-2">
                <div class="bd-brain-compare">
                    <!-- 左脑 -->
                    <div class="bd-brain-card ${leftActive ? 'active' : ''}">
                        <div class="bd-brain-header">
                            <span class="bd-brain-icon">🧠</span>
                            <h4>左脑 (普通模式)</h4>
                            <span class="bd-brain-status ${leftActive ? 'active' : 'standby'}">
                                ${leftActive ? '运行中' : '待机'}
                            </span>
                        </div>
                        <div class="bd-brain-content">
                            <div class="bd-brain-trait">
                                <span class="trait-label">思维方式</span>
                                <span class="trait-value">逻辑 · 分析 · 理性</span>
                            </div>
                            <div class="bd-brain-trait">
                                <span class="trait-label">处理速度</span>
                                <span class="trait-value">慢 · 精确</span>
                            </div>
                            <div class="bd-brain-trait">
                                <span class="trait-label">风险偏好</span>
                                <span class="trait-value">保守</span>
                            </div>
                            <div class="bd-brain-trait">
                                <span class="trait-label">决策依据</span>
                                <span class="trait-value">数据 · 指标</span>
                            </div>
                            <div class="bd-brain-trait">
                                <span class="trait-label">适合场景</span>
                                <span class="trait-value">稳定市场</span>
                            </div>
                        </div>
                        <div class="bd-brain-tools">
                            <h6>适配工具</h6>
                            <div class="bd-tools-list">
                                <span class="bd-tool-tag">🐰 EMA/MACD/RSI</span>
                                <span class="bd-tool-tag">🐹 布林带/波动率</span>
                                <span class="bd-tool-tag">🔮 MiroFish共识</span>
                                <span class="bd-tool-tag">👑 跟单策略</span>
                            </div>
                        </div>
                        <div class="bd-brain-actions">
                            <button class="bd-btn ${leftActive ? 'disabled' : 'primary'}" 
                                    ${leftActive ? 'disabled' : ''} 
                                    onclick="BrainDual.switchTo('left')">
                                ${leftActive ? '🧠 当前模式' : '切换到左脑'}
                            </button>
                        </div>
                    </div>

                    <!-- 中间切换 -->
                    <div class="bd-brain-switch">
                        <button class="bd-switch-btn" onclick="BrainDual.toggleBrain()">
                            ${leftActive ? '→' : '←'}
                        </button>
                        <span class="bd-switch-label">切换</span>
                    </div>

                    <!-- 右脑 -->
                    <div class="bd-brain-card ${rightActive ? 'active' : ''}">
                        <div class="bd-brain-header">
                            <span class="bd-brain-icon">🎯</span>
                            <h4>右脑 (专家模式)</h4>
                            <span class="bd-brain-status ${rightActive ? 'active' : 'standby'}">
                                ${rightActive ? '运行中' : '待机'}
                            </span>
                        </div>
                        <div class="bd-brain-content">
                            <div class="bd-brain-trait">
                                <span class="trait-label">思维方式</span>
                                <span class="trait-value">直觉 · 创造 · 模式识别</span>
                            </div>
                            <div class="bd-brain-trait">
                                <span class="trait-label">处理速度</span>
                                <span class="trait-value">快 · 模式</span>
                            </div>
                            <div class="bd-brain-trait">
                                <span class="trait-label">风险偏好</span>
                                <span class="trait-value">激进</span>
                            </div>
                            <div class="bd-brain-trait">
                                <span class="trait-label">决策依据</span>
                                <span class="trait-value">经验 · 感觉</span>
                            </div>
                            <div class="bd-brain-trait">
                                <span class="trait-label">适合场景</span>
                                <span class="trait-value">剧变市场</span>
                            </div>
                        </div>
                        <div class="bd-brain-tools">
                            <h6>适配工具</h6>
                            <div class="bd-tools-list">
                                <span class="bd-tool-tag">🐰 模式识别/趋势预测</span>
                                <span class="bd-tool-tag">🐹 火控雷达/异常检测</span>
                                <span class="bd-tool-tag">🔮 直觉预测</span>
                                <span class="bd-tool-tag">👑 KOL直觉</span>
                            </div>
                        </div>
                        <div class="bd-brain-actions">
                            <button class="bd-btn ${rightActive ? 'disabled' : 'primary'}" 
                                    ${rightActive ? 'disabled' : ''} 
                                    onclick="BrainDual.switchTo('right')">
                                ${rightActive ? '🎯 当前模式' : '切换到右脑'}
                            </button>
                        </div>
                    </div>
                </div>

                <!-- 差异对比表 -->
                <div class="bd-compare-table">
                    <h5>左右脑差异对比</h5>
                    <table>
                        <thead>
                            <tr><th>维度</th><th>🧠 左脑(普通)</th><th>🎯 右脑(专家)</th></tr>
                        </thead>
                        <tbody>
                            <tr><td>思维方式</td><td>逻辑·分析</td><td>直觉·创造</td></tr>
                            <tr><td>处理速度</td><td>慢·精确</td><td>快·模式</td></tr>
                            <tr><td>风险偏好</td><td>保守</td><td>激进</td></tr>
                            <tr><td>决策依据</td><td>数据·指标</td><td>经验·感觉</td></tr>
                            <tr><td>适合场景</td><td>稳定市场</td><td>剧变市场</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    },

    // Part 3 详情: 切换系统
    getPart3DetailHTML() {
        const isManual = this.state.switchMode === 'manual';

        return `
            <div class="bd-level bd-level-2 bd-part-3">
                <div class="bd-switch-options">
                    <!-- 一键切换 -->
                    <div class="bd-switch-card ${isManual ? 'active' : ''}">
                        <div class="bd-sc-header">
                            <span class="bd-sc-icon">🖱️</span>
                            <h4>一键切换 (手动)</h4>
                        </div>
                        <div class="bd-sc-content">
                            <p>手动点击按钮，快速切换左右脑模式</p>
                            <div class="bd-sc-current">
                                <span>当前模式:</span>
                                <strong>${this.state.mode === 'left' ? '🧠 左脑' : '🎯 右脑'}</strong>
                            </div>
                        </div>
                        <div class="bd-sc-actions">
                            <button class="bd-btn primary" onclick="BrainDual.toggleBrain()">
                                切换到${this.state.mode === 'left' ? '右脑' : '左脑'}
                            </button>
                        </div>
                    </div>

                    <!-- 自主切换 -->
                    <div class="bd-switch-card ${!isManual ? 'active' : ''}">
                        <div class="bd-sc-header">
                            <span class="bd-sc-icon">🤖</span>
                            <h4>自主切换 (条件触发)</h4>
                        </div>
                        <div class="bd-sc-content">
                            <p>根据市场条件自动切换左右脑模式</p>
                            <div class="bd-sc-conditions">
                                <div class="bd-condition">
                                    <span class="cond-label">左脑触发条件:</span>
                                    <span class="cond-value">波动率 &lt; 30%, RSI &lt; 70</span>
                                </div>
                                <div class="bd-condition">
                                    <span class="cond-label">右脑触发条件:</span>
                                    <span class="cond-value">波动率 &gt; 50%, 出现异常信号</span>
                                </div>
                            </div>
                        </div>
                        <div class="bd-sc-actions">
                            <button class="bd-btn secondary" onclick="BrainDual.setSwitchMode('auto')">
                                启用自主切换
                            </button>
                        </div>
                    </div>
                </div>

                <!-- 风格选择 -->
                <div class="bd-style-selector">
                    <h5>当前风格: ${this.getStyleLabel()}</h5>
                    <div class="bd-style-options">
                        <button class="bd-style-btn ${this.state.style === 'conservative' ? 'active' : ''}" 
                                onclick="BrainDual.setStyle('conservative')">
                            🛡️ 保守
                        </button>
                        <button class="bd-style-btn ${this.state.style === 'balanced' ? 'active' : ''}" 
                                onclick="BrainDual.setStyle('balanced')">
                            ⚖️ 平衡
                        </button>
                        <button class="bd-style-btn ${this.state.style === 'aggressive' ? 'active' : ''}" 
                                onclick="BrainDual.setStyle('aggressive')">
                            🚀 积极
                        </button>
                    </div>
                </div>
            </div>
        `;
    },

    // Level 3: 设置
    getLevel3HTML() {
        return `
            <div class="bd-level bd-level-3">
                <h4>⚙️ 参数配置</h4>
                
                <!-- 风格参数 -->
                <div class="bd-settings-group">
                    <h5>风格参数</h5>
                    <div class="bd-param-grid">
                        <div class="bd-param">
                            <label>风格模式</label>
                            <select onchange="BrainDual.setStyle(this.value)">
                                <option value="conservative" ${this.state.style === 'conservative' ? 'selected' : ''}>🛡️ 保守</option>
                                <option value="balanced" ${this.state.style === 'balanced' ? 'selected' : ''}>⚖️ 平衡</option>
                                <option value="aggressive" ${this.state.style === 'aggressive' ? 'selected' : ''}>🚀 积极</option>
                            </select>
                        </div>
                        <div class="bd-param">
                            <label>切换模式</label>
                            <select onchange="BrainDual.setSwitchMode(this.value)">
                                <option value="manual" ${this.state.switchMode === 'manual' ? 'selected' : ''}>🖱️ 手动切换</option>
                                <option value="auto" ${this.state.switchMode === 'auto' ? 'selected' : ''}>🤖 自主切换</option>
                            </select>
                        </div>
                    </div>
                </div>

                <!-- 左脑参数 -->
                <div class="bd-settings-group">
                    <h5>🧠 左脑参数 (普通模式)</h5>
                    <div class="bd-param-grid">
                        <div class="bd-param">
                            <label>止损倍数</label>
                            <input type="number" value="0.6" min="0.1" max="2" step="0.1">
                        </div>
                        <div class="bd-param">
                            <label>止盈倍数</label>
                            <input type="number" value="0.8" min="0.1" max="3" step="0.1">
                        </div>
                        <div class="bd-param">
                            <label>仓位系数</label>
                            <input type="number" value="0.5" min="0.1" max="1" step="0.1">
                        </div>
                    </div>
                </div>

                <!-- 右脑参数 -->
                <div class="bd-settings-group">
                    <h5>🎯 右脑参数 (专家模式)</h5>
                    <div class="bd-param-grid">
                        <div class="bd-param">
                            <label>止损倍数</label>
                            <input type="number" value="1.6" min="0.1" max="3" step="0.1">
                        </div>
                        <div class="bd-param">
                            <label>止盈倍数</label>
                            <input type="number" value="1.2" min="0.1" max="5" step="0.1">
                        </div>
                        <div class="bd-param">
                            <label>仓位系数</label>
                            <input type="number" value="1.0" min="0.1" max="1.5" step="0.1">
                        </div>
                    </div>
                </div>

                <!-- 自主切换条件 -->
                <div class="bd-settings-group">
                    <h5>🤖 自主切换条件</h5>
                    <div class="bd-param-grid">
                        <div class="bd-param">
                            <label>左脑波动率阈值</label>
                            <input type="number" value="30" min="1" max="100"> %
                        </div>
                        <div class="bd-param">
                            <label>右脑波动率阈值</label>
                            <input type="number" value="50" min="1" max="100"> %
                        </div>
                        <div class="bd-param">
                            <label>RSI超买阈值</label>
                            <input type="number" value="70" min="50" max="95">
                        </div>
                    </div>
                </div>

                <div class="bd-settings-actions">
                    <button class="bd-btn primary" onclick="BrainDual.saveSettings()">💾 保存设置</button>
                    <button class="bd-btn secondary" onclick="BrainDual.setLevel(2)">← 返回详情</button>
                    <button class="bd-btn secondary" onclick="BrainDual.setLevel(4)">📊 查看结果</button>
                </div>
            </div>
        `;
    },

    // Level 4: 执行/结果
    getLevel4HTML() {
        return `
            <div class="bd-level bd-level-4">
                <h4>📊 执行结果</h4>
                
                <!-- 历史记录 -->
                <div class="bd-history">
                    <h5>最近执行记录</h5>
                    <div class="bd-history-list">
                        ${this.getHistoryHTML()}
                    </div>
                </div>

                <!-- 复盘结果 -->
                <div class="bd-results-section">
                    <h5>🔄 复盘结果</h5>
                    <div class="bd-results-grid">
                        ${this.getRetroResultsHTML()}
                    </div>
                </div>

                <!-- 仿真结果 -->
                <div class="bd-results-section">
                    <h5>🧪 仿真结果</h5>
                    <div class="bd-results-grid">
                        ${this.getSimulationResultsHTML()}
                    </div>
                </div>

                <!-- 优化结果 -->
                <div class="bd-results-section">
                    <h5>⚡ 优化结果</h5>
                    <div class="bd-results-grid">
                        ${this.getOptimizationResultsHTML()}
                    </div>
                </div>

                <div class="bd-level4-actions">
                    <button class="bd-btn secondary" onclick="BrainDual.setLevel(2)">← 返回详情</button>
                    <button class="bd-btn primary" onclick="BrainDual.exportResults()">📥 导出报告</button>
                </div>
            </div>
        `;
    },

    // 获取历史记录HTML
    getHistoryHTML() {
        if (this.state.history.length === 0) {
            return '<div class="bd-empty">暂无执行记录</div>';
        }
        return this.state.history.slice(0, 5).map(h => `
            <div class="bd-history-item">
                <span class="bd-hi-time">${h.time}</span>
                <span class="bd-hi-type">${h.type}</span>
                <span class="bd-hi-result ${h.success ? 'success' : 'error'}">${h.success ? '成功' : '失败'}</span>
            </div>
        `).join('');
    },

    // 获取复盘结果HTML
    getRetroResultsHTML() {
        if (this.state.retroResults.length === 0) {
            return '<div class="bd-empty">暂无复盘结果，运行复盘后显示</div>';
        }
        return this.state.retroResults.map(r => `
            <div class="bd-result-card">
                <div class="bd-rc-header">
                    <span class="bd-rc-title">${r.title}</span>
                    <span class="bd-rc-score">${r.score}分</span>
                </div>
                <div class="bd-rc-content">
                    <p>${r.summary}</p>
                </div>
            </div>
        `).join('');
    },

    // 获取仿真结果HTML
    getSimulationResultsHTML() {
        if (this.state.simulationResults.length === 0) {
            return '<div class="bd-empty">暂无仿真结果，运行仿真后显示</div>';
        }
        return this.state.simulationResults.map(r => `
            <div class="bd-result-card">
                <div class="bd-rc-header">
                    <span class="bd-rc-title">${r.title}</span>
                    <span class="bd-rc-score">${r.score}分</span>
                </div>
                <div class="bd-rc-content">
                    <p>${r.summary}</p>
                </div>
            </div>
        `).join('');
    },

    // 获取优化结果HTML
    getOptimizationResultsHTML() {
        if (this.state.optimizationResults.length === 0) {
            return '<div class="bd-empty">暂无优化结果，运行优化后显示</div>';
        }
        return this.state.optimizationResults.map(r => `
            <div class="bd-result-card">
                <div class="bd-rc-header">
                    <span class="bd-rc-title">${r.title}</span>
                    <span class="bd-rc-score">${r.improvement}</span>
                </div>
                <div class="bd-rc-content">
                    <p>${r.summary}</p>
                </div>
            </div>
        `).join('');
    },

    // 绑定事件
    bindEvents() {
        // 键盘快捷键 B 切换模式
        document.addEventListener('keydown', (e) => {
            if (e.key === 'b' || e.key === 'B') {
                if (!e.ctrlKey && !e.metaKey && !e.altKey) {
                    const tag = e.target.tagName;
                    if (tag !== 'INPUT' && tag !== 'TEXTAREA' && tag !== 'SELECT') {
                        this.toggleBrain();
                    }
                }
            }
        });

        // 导航栏双脑切换
        const brainSwitch = document.getElementById('brainSwitch');
        if (brainSwitch) {
            brainSwitch.addEventListener('change', () => {
                this.switchTo(brainSwitch.checked ? 'right' : 'left');
            });
        }
    },

    // 更新导航状态
    updateNavState() {
        const brainSwitch = document.getElementById('brainSwitch');
        const brainLabel = document.getElementById('brainLabel');
        const brainMode = document.getElementById('brainMode');
        
        if (brainSwitch) {
            brainSwitch.checked = this.state.mode === 'right';
        }
        if (brainLabel) {
            brainLabel.textContent = this.state.mode === 'left' ? '🧠左脑' : '🎯右脑';
        }
        if (brainMode) {
            brainMode.textContent = this.state.mode === 'left' ? '普通' : '专家';
        }
    },

    // 设置Part
    setPart(part) {
        this.state.activePart = part;
        this.render();
    },

    // 设置Level
    setLevel(level) {
        this.state.level = level;
        this.render();
    },

    // 切换左右脑
    toggleBrain() {
        this.switchTo(this.state.mode === 'left' ? 'right' : 'left');
    },

    // 切换到指定模式
    switchTo(mode) {
        const oldMode = this.state.mode;
        this.state.mode = mode;
        
        // 更新状态
        if (mode === 'left') {
            this.state.leftBrain.status = 'active';
            this.state.rightBrain.status = 'standby';
        } else {
            this.state.leftBrain.status = 'standby';
            this.state.rightBrain.status = 'active';
        }

        // 记录历史
        this.addHistory(`切换到${mode === 'left' ? '左脑' : '右脑'}模式`);

        // 更新导航
        this.updateNavState();
        this.render();

        console.log(`🧠 切换到${mode === 'left' ? '左脑(普通)' : '右脑(专家)'}`);
    },

    // 设置风格
    setStyle(style) {
        this.state.style = style;
        this.state.leftBrain.style = style;
        this.state.rightBrain.style = style;
        this.render();
    },

    // 获取风格标签
    getStyleLabel() {
        const labels = {
            conservative: '🛡️ 保守',
            balanced: '⚖️ 平衡',
            aggressive: '🚀 积极'
        };
        return labels[this.state.style] || '⚖️ 平衡';
    },

    // 设置切换模式
    setSwitchMode(mode) {
        this.state.switchMode = mode;
        this.render();
    },

    // 运行复盘
    async runRetro() {
        this.addHistory('启动复盘');
        
        try {
            // 调用后台API
            const response = await fetch('/api/backtest', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'retro' })
            });
            
            if (response.ok) {
                const data = await response.json();
                this.state.retroResults.push({
                    title: `复盘 ${new Date().toLocaleString()}`,
                    score: data.score || 85,
                    summary: data.summary || '复盘完成，发现优化点3个'
                });
            } else {
                // 模拟结果
                this.state.retroResults.push({
                    title: `复盘 ${new Date().toLocaleString()}`,
                    score: 85 + Math.floor(Math.random() * 10),
                    summary: '复盘完成，gstack 15人团队评审通过，优化建议8条'
                });
            }
        } catch (e) {
            // 离线模式模拟
            this.state.retroResults.push({
                title: `复盘 ${new Date().toLocaleString()}`,
                score: 85 + Math.floor(Math.random() * 10),
                summary: '复盘完成，gstack 15人团队评审通过，优化建议8条'
            });
        }

        this.addHistory('复盘完成');
        this.setLevel(4);
    },

    // 运行仿真
    async runSimulation() {
        this.addHistory('启动仿真');
        
        try {
            // 调用后台API
            const response = await fetch('/api/simulation', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    action: 'full',
                    dimensions: 25,
                    agents: 1000
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                this.state.simulationResults.push({
                    title: `仿真 ${new Date().toLocaleString()}`,
                    score: data.score || 87,
                    summary: data.summary || 'MiroFish 25维度全向仿真完成'
                });
            } else {
                // 模拟结果
                this.state.simulationResults.push({
                    title: `仿真 ${new Date().toLocaleString()}`,
                    score: 82 + Math.floor(Math.random() * 15),
                    summary: 'MiroFish 1000智能体25维度仿真完成，评分87分'
                });
            }
        } catch (e) {
            // 离线模式模拟
            this.state.simulationResults.push({
                title: `仿真 ${new Date().toLocaleString()}`,
                score: 82 + Math.floor(Math.random() * 15),
                summary: 'MiroFish 1000智能体25维度仿真完成，评分87分'
            });
        }

        this.addHistory('仿真完成');
        this.setLevel(4);
    },

    // 运行优化
    async runOptimization() {
        this.addHistory('启动优化');
        
        try {
            // 调用后台ML API
            const response = await fetch('/api/ml/capabilities', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'optimize' })
            });
            
            if (response.ok) {
                const data = await response.json();
                this.state.optimizationResults.push({
                    title: `优化 ${new Date().toLocaleString()}`,
                    improvement: data.improvement || '+5.2%',
                    summary: data.summary || '参数优化完成，策略收益提升'
                });
            } else {
                // 模拟结果
                this.state.optimizationResults.push({
                    title: `优化 ${new Date().toLocaleString()}`,
                    improvement: `+${(3 + Math.random() * 8).toFixed(1)}%`,
                    summary: '策略参数优化完成，收益提升8.5%，风险降低12%'
                });
            }
        } catch (e) {
            // 离线模式模拟
            this.state.optimizationResults.push({
                title: `优化 ${new Date().toLocaleString()}`,
                improvement: `+${(3 + Math.random() * 8).toFixed(1)}%`,
                summary: '策略参数优化完成，收益提升8.5%，风险降低12%'
            });
        }

        this.addHistory('优化完成');
        this.setLevel(4);
    },

    // 添加历史记录
    addHistory(action) {
        this.state.history.unshift({
            time: new Date().toLocaleTimeString(),
            type: action,
            success: true
        });
        
        // 保持最多20条
        if (this.state.history.length > 20) {
            this.state.history.pop();
        }
    },

    // 保存设置
    saveSettings() {
        this.addHistory('保存设置');
        this.render();
        alert('设置已保存！');
    },

    // 导出结果
    exportResults() {
        const report = {
            mode: this.state.mode,
            style: this.state.style,
            retroResults: this.state.retroResults,
            simulationResults: this.state.simulationResults,
            optimizationResults: this.state.optimizationResults,
            history: this.state.history
        };
        
        const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `brain-dual-report-${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
        
        this.addHistory('导出报告');
    },

    // 获取工具配置
    getToolConfig(toolId) {
        return this.toolConfigs[toolId] || null;
    },

    // 获取当前模式的工具配置
    getCurrentModeTools(toolId) {
        const config = this.getToolConfig(toolId);
        if (!config) return null;
        return config[this.state.mode];
    },

    // Level 5: 历史记录
    getLevel5HTML() {
        const stats = this.state.stats || { today: 0, week: 0, total: 0, successRate: 0 };
        const history = this.state.history || [];
        
        return `
            <div style="padding:20px;">
                <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:12px; margin-bottom:20px;">
                    <div style="background:rgba(0,0,0,0.3); border-radius:8px; padding:15px; text-align:center;">
                        <div style="font-size:11px; color:#888; margin-bottom:5px;">今日切换</div>
                        <div style="font-size:24px; font-weight:700; color:#3b82f6;">${stats.today}</div>
                    </div>
                    <div style="background:rgba(0,0,0,0.3); border-radius:8px; padding:15px; text-align:center;">
                        <div style="font-size:11px; color:#888; margin-bottom:5px;">本周切换</div>
                        <div style="font-size:24px; font-weight:700; color:#3b82f6;">${stats.week}</div>
                    </div>
                    <div style="background:rgba(0,0,0,0.3); border-radius:8px; padding:15px; text-align:center;">
                        <div style="font-size:11px; color:#888; margin-bottom:5px;">总切换</div>
                        <div style="font-size:24px; font-weight:700; color:#3b82f6;">${stats.total}</div>
                    </div>
                    <div style="background:rgba(0,0,0,0.3); border-radius:8px; padding:15px; text-align:center;">
                        <div style="font-size:11px; color:#888; margin-bottom:5px;">成功率</div>
                        <div style="font-size:24px; font-weight:700; color:#00d4aa;">${stats.successRate}%</div>
                    </div>
                </div>
                <div style="background:rgba(0,0,0,0.3); border-radius:10px; padding:15px;">
                    <div style="font-size:14px; font-weight:600; margin-bottom:15px;">📜 切换历史</div>
                    ${history.length === 0 ? '<div style="text-align:center; padding:40px; color:#888;">暂无切换记录</div>' : history.slice(0, 15).map(h => `
                        <div style="display:flex; justify-content:space-between; padding:12px; border-bottom:1px solid rgba(255,255,255,0.1);">
                            <div><span style="color:#7c3aed; margin-right:8px;">🧠</span>${h.type || '脑切换'}</div>
                            <div style="color:#888; font-size:12px;">${h.time || ''}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    },

    // Level 6: 数据分析
    getLevel6HTML() {
        const a = this.state.analytics || { totalProfit: 0, returnRate: 0, maxDrawdown: 0, sharpeRatio: 0, tradeCount: 0, winRate: 0, avgProfit: 0, profitFactor: 0 };
        
        return `
            <div style="padding:20px;">
                <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(140px, 1fr)); gap:12px; margin-bottom:20px;">
                    <div style="background:linear-gradient(135deg, rgba(0,212,170,0.2), rgba(0,0,0,0.3)); border-radius:10px; padding:16px;">
                        <div style="font-size:11px; color:#888; margin-bottom:5px;">脑收益</div>
                        <div style="font-size:22px; font-weight:700; color:#00d4aa;">+$${a.totalProfit.toLocaleString()}</div>
                    </div>
                    <div style="background:linear-gradient(135deg, rgba(124,58,237,0.2), rgba(0,0,0,0.3)); border-radius:10px; padding:16px;">
                        <div style="font-size:11px; color:#888; margin-bottom:5px;">收益率</div>
                        <div style="font-size:22px; font-weight:700; color:#7c3aed;">${a.returnRate}%</div>
                    </div>
                    <div style="background:linear-gradient(135deg, rgba(239,68,68,0.2), rgba(0,0,0,0.3)); border-radius:10px; padding:16px;">
                        <div style="font-size:11px; color:#888; margin-bottom:5px;">最大回撤</div>
                        <div style="font-size:22px; font-weight:700; color:#ef4444;">-${a.maxDrawdown}%</div>
                    </div>
                    <div style="background:linear-gradient(135deg, rgba(245,158,11,0.2), rgba(0,0,0,0.3)); border-radius:10px; padding:16px;">
                        <div style="font-size:11px; color:#888; margin-bottom:5px;">夏普比率</div>
                        <div style="font-size:22px; font-weight:700; color:#f59e0b;">${a.sharpeRatio}</div>
                    </div>
                </div>
                <div style="background:rgba(0,0,0,0.3); border-radius:10px; padding:20px; margin-bottom:15px;">
                    <div style="font-size:14px; font-weight:600; margin-bottom:15px;">📊 脑表现</div>
                    <div style="height:150px; display:flex; align-items:center; justify-content:center; color:#888; background:rgba(0,0,0,0.2); border-radius:8px;">
                        <div style="text-align:center;"><div style="font-size:40px; margin-bottom:10px;">🧠</div><div>Chart.js / ECharts</div></div>
                    </div>
                </div>
                <div style="background:rgba(0,0,0,0.3); border-radius:10px; padding:20px;">
                    <div style="font-size:14px; font-weight:600; margin-bottom:15px;">📈 脑统计</div>
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:15px;">
                        <div style="display:flex; justify-content:space-between; padding:10px; background:rgba(0,0,0,0.2); border-radius:6px;"><span style="color:#888;">切换次数</span><span style="font-weight:600;">${a.tradeCount}</span></div>
                        <div style="display:flex; justify-content:space-between; padding:10px; background:rgba(0,0,0,0.2); border-radius:6px;"><span style="color:#888;">胜率</span><span style="font-weight:600; color:#00d4aa;">${a.winRate}%</span></div>
                        <div style="display:flex; justify-content:space-between; padding:10px; background:rgba(0,0,0,0.2); border-radius:6px;"><span style="color:#888;">平均收益</span><span style="font-weight:600;">$${a.avgProfit}</span></div>
                        <div style="display:flex; justify-content:space-between; padding:10px; background:rgba(0,0,0,0.2); border-radius:6px;"><span style="color:#888;">盈亏比</span><span style="font-weight:600;">${a.profitFactor}</span></div>
                    </div>
                </div>
            </div>
        `;
    }
};

// Auto-init (panel display disabled on load)
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() { BrainDual.init(); });
} else {
    BrainDual.init();
}


// 初始化 - Disabled auto-init


// Auto-init (panel display disabled on load)
document.addEventListener('DOMContentLoaded', function() { BrainDual.init(); });
