// ==========================================================================
// V14 模块完整4级页面 - 基于v13深度内容
// ==========================================================================

(function() {
    'use strict';
    
    // ========== 通用模块4级内容生成器 ==========
    function createModuleContent(name, icon, levels) {
        return {
            name: name,
            icon: icon,
            levels: levels
        };
    }
    
    // ========== PlatformIntro - 平台介绍 ==========
    window.PlatformIntro = {
        state: { level: 1 },
        init: function() { console.log('🚀 PlatformIntro initialized'); },
        renderPanel: function(level) {
            level = level || 1;
            this.state.level = level;
            var contents = {
                1: {
                    title: '平台总览',
                    data: '<div class="detail-grid">' +
                        '<div class="detail-card"><div class="detail-icon">🪿</div><div class="detail-title">GO2SE</div><div class="detail-desc">AI量化投资平台</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">📊</div><div class="detail-title">7大工具</div><div class="detail-desc">北斗七鑫投资体系</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">🧠</div><div class="detail-title">MiroFish</div><div class="detail-desc">100智能体预测</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">🔮</div><div class="detail-title">25维度</div><div class="detail-desc">全向仿真评测</div></div>' +
                        '</div>' +
                        '<div class="detail-section"><h4>平台优势</h4><ul>' +
                        '<li>✅ 全自动化投资决策</li><li>✅ 多策略并行执行</li>' +
                        '<li>✅ 实时风险控制</li><li>✅ 跨市场套利</li></ul></div>'
                },
                2: {
                    title: '核心功能',
                    data: '<div class="detail-section"><h4>7大投资工具</h4>' +
                        '<div class="detail-grid"><div class="detail-card"><div class="detail-icon">🐰</div><div class="detail-title">打兔子</div><div class="detail-desc">前20主流加密货币</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">🐹</div><div class="detail-title">打地鼠</div><div class="detail-desc">其他加密货币</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">🔮</div><div class="detail-title">走着瞧</div><div class="detail-desc">预测市场</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">👑</div><div class="detail-title">跟大哥</div><div class="detail-desc">做市商跟单</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">🍀</div><div class="detail-title">搭便车</div><div class="detail-desc">跟单分成</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">💰</div><div class="detail-title">薅羊毛</div><div class="detail-desc">空投猎手</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">👶</div><div class="detail-title">穷孩子</div><div class="detail-desc">众包赚钱</div></div></div></div>'
                },
                3: {
                    title: '技术架构',
                    data: '<div class="detail-section"><h4>技术架构</h4>' +
                        '<div class="detail-section"><p>🌐 表现层 - React/Vue</p></div>' +
                        '<div class="detail-section"><p>⚙️ 逻辑层 - Python/AI</p></div>' +
                        '<div class="detail-section"><p>💾 数据层 - MongoDB/Redis</p></div>' +
                        '<div class="detail-section"><p>📡 交易所API - Binance/ByBit</p></div></div>'
                },
                4: {
                    title: '版本信息',
                    data: '<div class="detail-section"><h4>版本信息</h4>' +
                        '<div class="detail-section"><p>当前版本: <strong>v14.8-dev</strong></p></div>' +
                        '<div class="detail-section"><p>发布日期: 2026-04-06</p></div>' +
                        '<div class="detail-section"><p>构建时间: ' + new Date().toLocaleString() + '</p></div></div>'
                }
            };
            var c = contents[level] || contents[1];
            return '<div class="module-detail"><h2>' + c.title + '</h2>' + c.data + '</div>';
        }
    };
    
    // ========== AttentionDIY - DIY注意力 ==========
    window.AttentionDIY = {
        state: { level: 1, focus: 75, energy: 80, mood: 'productive' },
        init: function() { console.log('🎯 AttentionDIY initialized'); },
        renderPanel: function(level) {
            level = level || 1;
            this.state.level = level;
            var contents = {
                1: {
                    title: '注意力总览',
                    data: '<div class="detail-grid">' +
                        '<div class="detail-card"><div class="detail-icon">🎯</div><div class="detail-title">专注度</div><div class="detail-desc">' + this.state.focus + '%</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">⚡</div><div class="detail-title">精力值</div><div class="detail-desc">' + this.state.energy + '%</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">😊</div><div class="detail-title">状态</div><div class="detail-desc">' + this.state.mood + '</div></div></div>'
                },
                2: {
                    title: '专注模式',
                    data: '<div class="detail-section"><h4>可用专注模式</h4>' +
                        '<div class="detail-section"><p>🎯 深度工作 - 25分钟</p></div>' +
                        '<div class="detail-section"><p>🧘 冥想 - 15分钟</p></div>' +
                        '<div class="detail-section"><p>📚 阅读 - 45分钟</p></div>' +
                        '<div class="detail-section"><p>💻 编码 - 90分钟</p></div></div>'
                },
                3: {
                    title: '习惯养成',
                    data: '<div class="detail-section"><h4>今日习惯</h4>' +
                        '<div class="detail-section"><p>✅ 早起冥想 6:00</p></div>' +
                        '<div class="detail-section"><p>✅ 晨间阅读 7:00</p></div>' +
                        '<div class="detail-section"><p>⟳ 专注工作 9:00-12:00</p></div>' +
                        '<div class="detail-section"><p>○ 晚间复盘 22:00</p></div></div>'
                },
                4: {
                    title: '数据报告',
                    data: '<div class="detail-section"><h4>本周报告</h4>' +
                        '<div class="detail-grid"><div class="detail-card"><div class="detail-title">总专注</div><div class="detail-desc">18.5h</div></div>' +
                        '<div class="detail-card"><div class="detail-title">完成率</div><div class="detail-desc">72%</div></div>' +
                        '<div class="detail-card"><div class="detail-title">提升</div><div class="detail-desc">+15%</div></div></div></div>'
                }
            };
            var c = contents[level] || contents[1];
            return '<div class="module-detail"><h2>' + c.title + '</h2>' + c.data + '</div>';
        }
    };
    
    // ========== MacroMicro - 宏观微观 ==========
    window.MacroMicro = {
        state: { level: 1 },
        init: function() { console.log('🌐 MacroMicro initialized'); },
        renderPanel: function(level) {
            level = level || 1;
            this.state.level = level;
            var contents = {
                1: {
                    title: '宏观微观总览',
                    data: '<div class="detail-grid">' +
                        '<div class="detail-card"><div class="detail-icon">🌐</div><div class="detail-title">BTC</div><div class="detail-desc">$75,000</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">📊</div><div class="detail-title">ETH</div><div class="detail-desc">$3,200</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">📈</div><div class="detail-title">RSI</div><div class="detail-desc">68</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">🔥</div><div class="detail-title">热度</div><div class="detail-desc">中高</div></div></div>'
                },
                2: {
                    title: '技术指标',
                    data: '<div class="detail-section"><h4>MA交叉</h4><p>MA50 < MA200: 看涨</p></div>' +
                        '<div class="detail-section"><h4>RSI</h4><p>当前值: 68 (超买区域)</p></div>' +
                        '<div class="detail-section"><h4>MACD</h4><p>信号线金叉</p></div>'
                },
                3: {
                    title: '分析配置',
                    data: '<div class="detail-section"><h4>时间范围</h4>' +
                        '<select class="form-control"><option>1H</option><option selected>4H</option><option>1D</option><option>1W</option></select></div>' +
                        '<div class="detail-section"><h4>指标选择</h4>' +
                        '<label><input type="checkbox" checked> MA</label>' +
                        '<label><input type="checkbox" checked> RSI</label>' +
                        '<label><input type="checkbox" checked> MACD</label></div>'
                },
                4: {
                    title: '确认分析',
                    data: '<div class="detail-section"><p>确认执行技术分析？</p></div>' +
                        '<div class="detail-section"><p>时间范围: 4H</p></div>' +
                        '<div class="detail-section"><p>指标: MA + RSI + MACD</p></div>'
                }
            };
            var c = contents[level] || contents[1];
            return '<div class="module-detail"><h2>' + c.title + '</h2>' + c.data + '</div>';
        }
    };
    
    // ========== SevenTools - 北斗七鑫 ==========
    window.SevenTools = {
        state: { level: 1 },
        init: function() { console.log('⭐ SevenTools initialized'); },
        renderPanel: function(level) {
            level = level || 1;
            this.state.level = level;
            var tools = [
                { icon: '🐰', name: '打兔子', pos: '25%', win: '72%', desc: '前20主流加密货币' },
                { icon: '🐹', name: '打地鼠', pos: '20%', win: '62%', desc: '其他加密货币' },
                { icon: '🔮', name: '走着瞧', pos: '15%', win: '70%', desc: '预测市场' },
                { icon: '👑', name: '跟大哥', pos: '15%', win: '78%', desc: '做市商跟单' },
                { icon: '🍀', name: '搭便车', pos: '10%', win: '65%', desc: '跟单分成' },
                { icon: '💰', name: '薅羊毛', pos: '3%', win: '55%', desc: '空投猎手' },
                { icon: '👶', name: '穷孩子', pos: '2%', win: '50%', desc: '众包赚钱' }
            ];
            var contents = {
                1: {
                    title: '北斗七鑫总览',
                    data: '<div class="detail-grid">' +
                        tools.map(function(t) {
                            return '<div class="detail-card"><div class="detail-icon">' + t.icon + '</div><div class="detail-title">' + t.name + '</div><div class="detail-desc">' + t.pos + '</div></div>';
                        }).join('') + '</div>'
                },
                2: {
                    title: '工具详情',
                    data: '<div class="detail-section"><h4>仓位分配详情</h4>' +
                        '<div class="detail-section"><p>🐰 打兔子: 25% - 稳定收益</p></div>' +
                        '<div class="detail-section"><p>🐹 打地鼠: 20% - 高波动</p></div>' +
                        '<div class="detail-section"><p>🔮 走着瞧: 15% - 预测驱动</p></div>' +
                        '<div class="detail-section"><p>👑 跟大哥: 15% - 跟单模式</p></div>' +
                        '<div class="detail-section"><p>🍀 搭便车: 10% - 被动收益</p></div>' +
                        '<div class="detail-section"><p>💰 薅羊毛: 3% - 空投猎手</p></div>' +
                        '<div class="detail-section"><p>👶 穷孩子: 2% - 众包赚钱</p></div></div>'
                },
                3: {
                    title: '参数配置',
                    data: '<div class="detail-section"><h4>总仓位上限</h4>' +
                        '<input type="range" min="50" max="100" value="80" class="full-width"><span>80%</span></div>' +
                        '<div class="detail-section"><h4>风控等级</h4>' +
                        '<select class="form-control"><option>保守</option><option selected>标准</option><option>激进</option></select></div>'
                },
                4: {
                    title: '确认执行',
                    data: '<div class="detail-section"><p>确认执行北斗七鑫策略配置？</p></div>' +
                        '<div class="detail-section"><p>总仓位: 80%</p></div>' +
                        '<div class="detail-section"><p>风控等级: 标准</p></div>'
                }
            };
            var c = contents[level] || contents[1];
            return '<div class="module-detail"><h2>' + c.title + '</h2>' + c.data + '</div>';
        }
    };
    
    // ========== TradingPanel - 交易面板 ==========
    window.TradingPanel = {
        state: { level: 1, activeTab: 'live' },
        init: function() { console.log('⚡ TradingPanel initialized'); },
        renderPanel: function(level) {
            level = level || 1;
            this.state.level = level;
            var contents = {
                1: {
                    title: '交易面板总览',
                    data: '<div class="detail-grid">' +
                        '<div class="detail-card"><div class="detail-icon">⚡</div><div class="detail-title">实时流</div><div class="detail-desc">监控中</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">📊</div><div class="detail-title">今日交易</div><div class="detail-desc">12笔</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">💰</div><div class="detail-title">总盈亏</div><div class="detail-desc">+$1,234</div></div></div>'
                },
                2: {
                    title: '交易详情',
                    data: '<div class="detail-section"><h4>当前持仓</h4>' +
                        '<div class="detail-section"><p>BTC/USDT: +0.5 @ $75,000 = $37,500</p></div>' +
                        '<div class="detail-section"><p>ETH/USDT: +5 @ $3,200 = $16,000</p></div>' +
                        '<div class="detail-section"><p>SOL/USDT: +100 @ $178 = $17,800</p></div></div>'
                },
                3: {
                    title: '交易配置',
                    data: '<div class="detail-section"><h4>交易对</h4>' +
                        '<select class="form-control"><option>BTC/USDT</option><option>ETH/USDT</option><option>SOL/USDT</option></select></div>' +
                        '<div class="detail-section"><h4>仓位</h4>' +
                        '<input type="range" min="1" max="100" value="10" class="full-width"><span>10%</span></div>' +
                        '<div class="detail-section"><h4>止损</h4><input type="number" value="5" class="form-control">%</div>' +
                        '<div class="detail-section"><h4>止盈</h4><input type="number" value="15" class="form-control">%</div>'
                },
                4: {
                    title: '确认下单',
                    data: '<div class="detail-section"><p>确认执行交易？</p></div>' +
                        '<div class="detail-section"><p>交易对: BTC/USDT</p></div>' +
                        '<div class="detail-section"><p>仓位: 10%</p></div>' +
                        '<div class="detail-section"><p>止损: 5% | 止盈: 15%</p></div>'
                }
            };
            var c = contents[level] || contents[1];
            return '<div class="module-detail"><h2>' + c.title + '</h2>' + c.data + '</div>';
        }
    };
    
    // ========== TradingSim - 交易仿真 ==========
    window.TradingSim = {
        state: { level: 1 },
        init: function() { console.log('🔮 TradingSim initialized'); },
        renderPanel: function(level) {
            level = level || 1;
            this.state.level = level;
            var contents = {
                1: {
                    title: '仿真中心总览',
                    data: '<div class="detail-grid">' +
                        '<div class="detail-card"><div class="detail-icon">🎮</div><div class="detail-title">仿真模式</div><div class="detail-desc">Paper Trading</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">📊</div><div class="detail-title">模拟资金</div><div class="detail-desc">$100,000</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">📈</div><div class="detail-title">模拟收益</div><div class="detail-desc">+12.5%</div></div></div>'
                },
                2: {
                    title: '仿真详情',
                    data: '<div class="detail-section"><h4>仿真记录</h4>' +
                        '<div class="detail-section"><p>BTC模拟单: +5.2%</p></div>' +
                        '<div class="detail-section"><p>ETH模拟单: +3.8%</p></div>' +
                        '<div class="detail-section"><p>SOL模拟单: -1.2%</p></div></div>'
                },
                3: {
                    title: '仿真配置',
                    data: '<div class="detail-section"><h4>初始资金</h4><input type="number" value="100000" class="form-control"></div>' +
                        '<div class="detail-section"><h4>手续费率</h4><input type="number" value="0.1" step="0.01" class="form-control">%</div>'
                },
                4: {
                    title: '开始仿真',
                    data: '<div class="detail-section"><p>确认开始新的仿真？</p></div>' +
                        '<div class="detail-section"><p>初始资金: $100,000</p></div>' +
                        '<div class="detail-section"><p>手续费率: 0.1%</p></div>'
                }
            };
            var c = contents[level] || contents[1];
            return '<div class="module-detail"><h2>' + c.title + '</h2>' + c.data + '</div>';
        }
    };
    
    // ========== Competitor - 竞品对比 ==========
    window.Competitor = {
        state: { level: 1 },
        init: function() { console.log('📊 Competitor initialized'); },
        renderPanel: function(level) {
            level = level || 1;
            this.state.level = level;
            var contents = {
                1: {
                    title: '竞品对比总览',
                    data: '<div class="detail-grid">' +
                        '<div class="detail-card"><div class="detail-icon">🆚</div><div class="detail-title">GO2SE</div><div class="detail-desc">97.2分</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">3C</div><div class="detail-title">3Commas</div><div class="detail-desc">85分</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">H</div><div class="detail-title">HaasOnline</div><div class="detail-desc">82分</div></div></div>'
                },
                2: {
                    title: '功能对比',
                    data: '<div class="detail-section"><h4>功能矩阵</h4>' +
                        '<div class="detail-section"><p>✅ 自动交易: GO2SE | 3Commas | Haas</p></div>' +
                        '<div class="detail-section"><p>✅ 社交跟单: GO2SE | 3Commas | -</p></div>' +
                        '<div class="detail-section"><p>✅ 仿真测试: GO2SE | - | Haas</p></div>' +
                        '<div class="detail-section"><p>✅ MiroFish预测: GO2SE独有</p></div></div>'
                },
                3: {
                    title: '价格对比',
                    data: '<div class="detail-section"><h4>定价</h4>' +
                        '<div class="detail-section"><p>GO2SE: 订阅制 - 起价$29/月</p></div>' +
                        '<div class="detail-section"><p>3Commas: $49/月 起</p></div>' +
                        '<div class="detail-section"><p>HaasOnline: $99/月 起</p></div></div>'
                },
                4: {
                    title: '选择确认',
                    data: '<div class="detail-section"><p>选择GO2SE的优势：</p></div>' +
                        '<div class="detail-section"><p>1. MiroFish 100智能体预测</p></div>' +
                        '<div class="detail-section"><p>2. 北斗七鑫完整投资体系</p></div>' +
                        '<div class="detail-section"><p>3. 25维度全向仿真评测</p></div>'
                }
            };
            var c = contents[level] || contents[1];
            return '<div class="module-detail"><h2>' + c.title + '</h2>' + c.data + '</div>';
        }
    };
    
    // ========== AssetDashboard - 资产看板 ==========
    window.AssetDashboard = {
        state: { level: 1 },
        init: function() { console.log('💰 AssetDashboard initialized'); },
        renderPanel: function(level) {
            level = level || 1;
            this.state.level = level;
            var contents = {
                1: {
                    title: '资产总览',
                    data: '<div class="detail-grid">' +
                        '<div class="detail-card"><div class="detail-icon">💵</div><div class="detail-title">总资产</div><div class="detail-desc">$85,000</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">📈</div><div class="detail-title">总收益</div><div class="detail-desc">+$12,350</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">📊</div><div class="detail-title">日收益</div><div class="detail-desc">+2.3%</div></div></div>'
                },
                2: {
                    title: '资产详情',
                    data: '<div class="detail-section"><h4>资产明细</h4>' +
                        '<div class="detail-section"><p>USDT: $15,000 (15%)</p></div>' +
                        '<div class="detail-section"><p>BTC: $37,500 (45%)</p></div>' +
                        '<div class="detail-section"><p>ETH: $16,000 (19%)</p></div>' +
                        '<div class="detail-section"><p>SOL: $17,800 (21%)</p></div></div>'
                },
                3: {
                    title: '资产配置',
                    data: '<div class="detail-section"><h4>目标配置</h4>' +
                        '<input type="text" value="40/30/20/10" class="form-control" placeholder="BTC/ETH/SOL/USDT"></div>' +
                        '<div class="detail-section"><h4>再平衡频率</h4>' +
                        '<select class="form-control"><option>每日</option><option selected>每周</option><option>每月</option></select></div>'
                },
                4: {
                    title: '确认执行',
                    data: '<div class="detail-section"><p>确认执行资产再平衡？</p></div>' +
                        '<div class="detail-section"><p>目标配置: 40/30/20/10</p></div>' +
                        '<div class="detail-section"><p>频率: 每周</p></div>'
                }
            };
            var c = contents[level] || contents[1];
            return '<div class="module-detail"><h2>' + c.title + '</h2>' + c.data + '</div>';
        }
    };
    
    // ========== InvestIncome - 投资收益 ==========
    window.InvestIncome = {
        state: { level: 1, totalReturn: 12350, totalInvest: 100000 },
        init: function() { console.log('📈 InvestIncome initialized'); },
        renderPanel: function(level) {
            level = level || 1;
            this.state.level = level;
            var roi = ((this.state.totalReturn / this.state.totalInvest) * 100).toFixed(2);
            var contents = {
                1: {
                    title: '收益总览',
                    data: '<div class="detail-grid">' +
                        '<div class="detail-card"><div class="detail-icon">💰</div><div class="detail-title">总资产</div><div class="detail-desc">$112,350</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">📈</div><div class="detail-title">总收益</div><div class="detail-desc">+$' + this.state.totalReturn.toLocaleString() + '</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">%</div><div class="detail-title">收益率</div><div class="detail-desc">+' + roi + '%</div></div></div>'
                },
                2: {
                    title: '持仓明细',
                    data: '<div class="detail-section"><h4>持仓列表</h4>' +
                        '<div class="detail-section"><p>BTC: +$2,340 (+6.6%)</p></div>' +
                        '<div class="detail-section"><p>ETH: +$1,120 (+7.5%)</p></div>' +
                        '<div class="detail-section"><p>SOL: +$2,150 (+13.7%)</p></div>' +
                        '<div class="detail-section"><p>PEPE: -$1,200 (-11.9%) ⚠️</p></div></div>'
                },
                3: {
                    title: '历史收益',
                    data: '<div class="detail-section"><h4>最近交易</h4>' +
                        '<div class="detail-section"><p>2026-04-05: 卖BTC +$2,340</p></div>' +
                        '<div class="detail-section"><p>2026-04-04: 买ETH +$1,120</p></div>' +
                        '<div class="detail-section"><p>2026-04-03: 买SOL +$2,150</p></div></div>'
                },
                4: {
                    title: '收益分析',
                    data: '<div class="detail-section"><h4>风险指标</h4>' +
                        '<div class="detail-grid"><div class="detail-card"><div class="detail-title">夏普比率</div><div class="detail-desc">1.85</div></div>' +
                        '<div class="detail-card"><div class="detail-title">最大回撤</div><div class="detail-desc">8.5%</div></div></div></div>'
                }
            };
            var c = contents[level] || contents[1];
            return '<div class="module-detail"><h2>' + c.title + '</h2>' + c.data + '</div>';
        }
    };
    
    // ========== WorkIncome - 打工收益 ==========
    window.WorkIncome = {
        state: { level: 1, totalEarned: 1580.50, pending: 95.00 },
        init: function() { console.log('💼 WorkIncome initialized'); },
        renderPanel: function(level) {
            level = level || 1;
            this.state.level = level;
            var contents = {
                1: {
                    title: '打工收益总览',
                    data: '<div class="detail-grid">' +
                        '<div class="detail-card"><div class="detail-icon">💰</div><div class="detail-title">总收入</div><div class="detail-desc">$1,580.50</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">⏳</div><div class="detail-title">待结算</div><div class="detail-desc">$95.00</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">📊</div><div class="detail-title">完成任务</div><div class="detail-desc">23个</div></div></div>'
                },
                2: {
                    title: '任务列表',
                    data: '<div class="detail-section"><h4>最近任务</h4>' +
                        '<div class="detail-section"><p>✅ AI数据标注 - $45.50</p></div>' +
                        '<div class="detail-section"><p>✅ 翻译任务 - $120.00</p></div>' +
                        '<div class="detail-section"><p>⟳ App测试 - $80.00</p></div>' +
                        '<div class="detail-section"><p>○ 问卷调查 - $15.00</p></div></div>'
                },
                3: {
                    title: '平台绑定',
                    data: '<div class="detail-section"><h4>已绑定平台</h4>' +
                        '<div class="detail-section"><p>✅ Amazon MTurk</p></div>' +
                        '<div class="detail-section"><p>✅ ProZ</p></div>' +
                        '<div class="detail-section"><p>+ 添加新平台</p></div></div>'
                },
                4: {
                    title: '提现设置',
                    data: '<div class="detail-section"><h4>提现方式</h4>' +
                        '<select class="form-control"><option selected>PayPal</option><option>银行转账</option><option>加密货币</option></select></div>' +
                        '<div class="detail-section"><p>提现金额: $' + this.state.pending.toFixed(2) + '</p></div>'
                }
            };
            var c = contents[level] || contents[1];
            return '<div class="module-detail"><h2>' + c.title + '</h2>' + c.data + '</div>';
        }
    };
    
    // ========== WalletArch - 钱包架构 ==========
    window.WalletArch = {
        state: { level: 1 },
        init: function() { console.log('🏦 WalletArch initialized'); },
        renderPanel: function(level) {
            level = level || 1;
            this.state.level = level;
            var contents = {
                1: {
                    title: '钱包架构总览',
                    data: '<div class="detail-grid">' +
                        '<div class="detail-card"><div class="detail-icon">🏦</div><div class="detail-title">主钱包</div><div class="detail-desc">$85,000</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">👛</div><div class="detail-title">子钱包</div><div class="detail-desc">7个</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">🔐</div><div class="detail-title">安全等级</div><div class="detail-desc">92分</div></div></div>'
                },
                2: {
                    title: '钱包详情',
                    data: '<div class="detail-section"><h4>子钱包分配</h4>' +
                        '<div class="detail-section"><p>🐰 打兔子: $2,500</p></div>' +
                        '<div class="detail-section"><p>🐹 打地鼠: $3,000</p></div>' +
                        '<div class="detail-section"><p>🔮 走着瞧: $3,000</p></div>' +
                        '<div class="detail-section"><p>👑 跟大哥: $1,500</p></div>' +
                        '<div class="detail-section"><p>🍀 搭便车: $1,000</p></div>' +
                        '<div class="detail-section"><p>💰 薅羊毛: $1,500</p></div>' +
                        '<div class="detail-section"><p>👶 穷孩子: $500</p></div></div>'
                },
                3: {
                    title: '钱包配置',
                    data: '<div class="detail-section"><h4>主钱包地址</h4>' +
                        '<input type="text" value="0x1234...5678" class="form-control" readonly></div>' +
                        '<div class="detail-section"><h4>Gas设置</h4>' +
                        '<select class="form-control"><option>低 (慢)</option><option selected>中 (标准)</option><option>高 (快)</option></select></div>'
                },
                4: {
                    title: '确认保存',
                    data: '<div class="detail-section"><p>确认保存钱包配置？</p></div>' +
                        '<div class="detail-section"><p>主钱包: $85,000</p></div>' +
                        '<div class="detail-section"><p>子钱包: 7个</p></div>'
                }
            };
            var c = contents[level] || contents[1];
            return '<div class="module-detail"><h2>' + c.title + '</h2>' + c.data + '</div>';
        }
    };
    
    // ========== WalletDeconstruct - 资产分布 ==========
    window.WalletDeconstruct = {
        state: { level: 1 },
        init: function() { console.log('📊 WalletDeconstruct initialized'); },
        renderPanel: function(level) {
            level = level || 1;
            this.state.level = level;
            var contents = {
                1: {
                    title: '资产分布总览',
                    data: '<div class="detail-grid">' +
                        '<div class="detail-card"><div class="detail-icon">₿</div><div class="detail-title">BTC</div><div class="detail-desc">45%</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">Ξ</div><div class="detail-title">ETH</div><div class="detail-desc">25%</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">◎</div><div class="detail-title">SOL</div><div class="detail-desc">15%</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">$</div><div class="detail-title">USDT</div><div class="detail-desc">15%</div></div></div>'
                },
                2: {
                    title: '分布详情',
                    data: '<div class="detail-section"><h4>资产明细</h4>' +
                        '<div class="detail-section"><p>BTC: $37,500 (45%)</p></div>' +
                        '<div class="detail-section"><p>ETH: $20,800 (25%)</p></div>' +
                        '<div class="detail-section"><p>SOL: $12,500 (15%)</p></div>' +
                        '<div class="detail-section"><p>USDT: $12,500 (15%)</p></div></div>'
                },
                3: {
                    title: '调整配置',
                    data: '<div class="detail-section"><h4>目标配置</h4>' +
                        '<input type="text" value="40/25/20/15" class="form-control" placeholder="BTC/ETH/SOL/USDT"></div>' +
                        '<div class="detail-section"><p>当前偏差: BTC +5%, ETH 0%, SOL -5%</p></div>'
                },
                4: {
                    title: '确认调整',
                    data: '<div class="detail-section"><p>确认执行资产再平衡？</p></div>' +
                        '<div class="detail-section"><p>目标: 40/25/20/15</p></div>' +
                        '<div class="detail-section"><p>预计交易次数: 3笔</p></div>'
                }
            };
            var c = contents[level] || contents[1];
            return '<div class="module-detail"><h2>' + c.title + '</h2>' + c.data + '</div>';
        }
    };
    
    // ========== AssetRisk - 风险状态 ==========
    window.AssetRisk = {
        state: { level: 1, riskScore: 35 },
        init: function() { console.log('⚠️ AssetRisk initialized'); },
        renderPanel: function(level) {
            level = level || 1;
            this.state.level = level;
            var contents = {
                1: {
                    title: '风险总览',
                    data: '<div class="detail-grid">' +
                        '<div class="detail-card"><div class="detail-icon">⚠️</div><div class="detail-title">风险指数</div><div class="detail-desc">' + this.state.riskScore + '/100</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">📉</div><div class="detail-title">最大回撤</div><div class="detail-desc">8.5%</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">📊</div><div class="detail-title">VaR(95%)</div><div class="detail-desc">2.5%</div></div></div>' +
                        '<div class="detail-section"><h4>状态: 🟢 低风险</h4></div>'
                },
                2: {
                    title: '风险指标',
                    data: '<div class="detail-section"><h4>详细指标</h4>' +
                        '<div class="detail-section"><p>VaR (95%): 2.5%</p></div>' +
                        '<div class="detail-section"><p>最大回撤: 8.5%</p></div>' +
                        '<div class="detail-section"><p>夏普比率: 1.85</p></div>' +
                        '<div class="detail-section"><p>杠杆率: 1.0x</p></div></div>'
                },
                3: {
                    title: '告警记录',
                    data: '<div class="detail-section"><h4>最近告警</h4>' +
                        '<div class="detail-section"><p>⚠️ PEPE仓位亏损11.9%，接近止损线</p></div>' +
                        '<div class="detail-section"><p>ℹ️ BTC RSI指标70，处于超买区域</p></div></div>'
                },
                4: {
                    title: '风控设置',
                    data: '<div class="detail-section"><h4>风控规则</h4>' +
                        '<div class="detail-section"><p>单笔最大损失: 5%</p></div>' +
                        '<div class="detail-section"><p>日最大损失: 15%</p></div>' +
                        '<div class="detail-section"><p>杠杆限制: 3x</p></div></div>'
                }
            };
            var c = contents[level] || contents[1];
            return '<div class="module-detail"><h2>' + c.title + '</h2>' + c.data + '</div>';
        }
    };
    
    // ========== BrainDual - 虾驭双脑 ==========
    window.BrainDual = {
        state: { level: 1, mode: 'dual' },
        init: function() { console.log('🧠 BrainDual initialized'); },
        renderPanel: function(level) {
            level = level || 1;
            this.state.level = level;
            var contents = {
                1: {
                    title: '双脑总览',
                    data: '<div class="detail-grid">' +
                        '<div class="detail-card"><div class="detail-icon">🧮</div><div class="detail-title">左脑</div><div class="detail-desc">逻辑分析</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">🎨</div><div class="detail-title">右脑</div><div class="detail-desc">创意洞察</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">🔄</div><div class="detail-title">模式</div><div class="detail-desc">' + (this.state.mode === 'dual' ? '双脑协同' : this.state.mode) + '</div></div></div>'
                },
                2: {
                    title: '深度分析',
                    data: '<div class="detail-section"><h4>左脑分析</h4>' +
                        '<div class="detail-section"><p>📊 数据驱动决策</p></div>' +
                        '<div class="detail-section"><p>📈 技术指标分析</p></div>' +
                        '<div class="detail-section"><h4>右脑洞察</h4></div>' +
                        '<div class="detail-section"><p>🎯 直觉判断</p></div>' +
                        '<div class="detail-section"><p>💡 创意策略</p></div></div>'
                },
                3: {
                    title: '模式配置',
                    data: '<div class="detail-section"><h4>双脑模式</h4>' +
                        '<select class="form-control"><option value="left">左脑优先</option><option value="dual" selected>双脑协同</option><option value="right">右脑优先</option></select></div>' +
                        '<div class="detail-section"><h4>权重分配</h4>' +
                        '<div class="detail-section"><p>左脑权重: 50%</p></div>' +
                        '<div class="detail-section"><p>右脑权重: 50%</p></div></div>'
                },
                4: {
                    title: '确认执行',
                    data: '<div class="detail-section"><p>确认更新双脑配置？</p></div>' +
                        '<div class="detail-section"><p>模式: 双脑协同</p></div>' +
                        '<div class="detail-section"><p>权重: 50/50</p></div>'
                }
            };
            var c = contents[level] || contents[1];
            return '<div class="module-detail"><h2>' + c.title + '</h2>' + c.data + '</div>';
        }
    };
    
    // ========== WalletSecurity - 钱包安全 ==========
    window.WalletSecurity = {
        state: { level: 1, securityScore: 92 },
        init: function() { console.log('🔐 WalletSecurity initialized'); },
        renderPanel: function(level) {
            level = level || 1;
            this.state.level = level;
            var contents = {
                1: {
                    title: '钱包安全总览',
                    data: '<div class="detail-grid">' +
                        '<div class="detail-card"><div class="detail-icon">🔐</div><div class="detail-title">安全评分</div><div class="detail-desc">' + this.state.securityScore + '/100</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">🏦</div><div class="detail-title">钱包数量</div><div class="detail-desc">8个</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">🔑</div><div class="detail-title">授权次数</div><div class="detail-desc">12次</div></div></div>'
                },
                2: {
                    title: '安全详情',
                    data: '<div class="detail-section"><h4>安全规则</h4>' +
                        '<div class="detail-section"><p>✅ 双重验证已启用</p></div>' +
                        '<div class="detail-section"><p>✅ 延迟交易已启用</p></div>' +
                        '<div class="detail-section"><p>✅ IP白名单已启用</p></div>' +
                        '<div class="detail-section"><p>✅ 自动登出已启用</p></div></div>'
                },
                3: {
                    title: '安全配置',
                    data: '<div class="detail-section"><h4>自动锁定时间</h4>' +
                        '<select class="form-control"><option>5分钟</option><option selected>15分钟</option><option>30分钟</option><option>1小时</option></select></div>' +
                        '<div class="detail-section"><h4>交易密码</h4>' +
                        '<input type="password" placeholder="设置交易密码" class="form-control"></div>'
                },
                4: {
                    title: '确认保存',
                    data: '<div class="detail-section"><p>确认保存安全设置？</p></div>' +
                        '<div class="detail-section"><p>自动锁定: 15分钟</p></div>' +
                        '<div class="detail-section"><p>双重验证: 启用</p></div>'
                }
            };
            var c = contents[level] || contents[1];
            return '<div class="module-detail"><h2>' + c.title + '</h2>' + c.data + '</div>';
        }
    };
    
    // ========== SecurityMechanism - 安全机制 ==========
    window.SecurityMechanism = {
        state: { level: 1, securityScore: 92 },
        init: function() { console.log('🛡️ SecurityMechanism initialized'); },
        renderPanel: function(level) {
            level = level || 1;
            this.state.level = level;
            var contents = {
                1: {
                    title: '安全机制总览',
                    data: '<div class="detail-grid">' +
                        '<div class="detail-card"><div class="detail-icon">🛡️</div><div class="detail-title">威胁检测</div><div class="detail-desc">无威胁</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">🔍</div><div class="detail-title">监控状态</div><div class="detail-desc">运行中</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">📊</div><div class="detail-title">安全评分</div><div class="detail-desc">' + this.state.securityScore + '/100</div></div></div>'
                },
                2: {
                    title: '安全规则',
                    data: '<div class="detail-section"><h4>安全规则</h4>' +
                        '<div class="detail-section"><p>🔑 API密钥轮换: 90天</p></div>' +
                        '<div class="detail-section"><p>⏱️ 交易延迟: 5秒</p></div>' +
                        '<div class="detail-section"><p>📋 IP白名单: 启用</p></div>' +
                        '<div class="detail-section"><p>🔔 异常告警: 启用</p></div></div>'
                },
                3: {
                    title: '操作日志',
                    data: '<div class="detail-section"><h4>最近日志</h4>' +
                        '<div class="detail-section"><p>14:32:15 登录成功 - 192.168.1.100</p></div>' +
                        '<div class="detail-section"><p>14:25:03 API调用 - 192.168.1.100</p></div>' +
                        '<div class="detail-section"><p>13:45:22 交易执行 - 192.168.1.100</p></div></div>'
                },
                4: {
                    title: '安全设置',
                    data: '<div class="detail-section"><h4>紧急联系人</h4>' +
                        '<input type="text" placeholder="输入邮箱或手机" class="form-control"></div>' +
                        '<div class="detail-section"><h4>审计日志</h4>' +
                        '<p>保留期限: 90天</p></div>'
                }
            };
            var c = contents[level] || contents[1];
            return '<div class="module-detail"><h2>' + c.title + '</h2>' + c.data + '</div>';
        }
    };
    
    // ========== EngineerModule - 工善其事 ==========
    window.EngineerModule = {
        state: { level: 1 },
        init: function() { console.log('🔧 EngineerModule initialized'); },
        renderPanel: function(level) {
            level = level || 1;
            this.state.level = level;
            var contents = {
                1: {
                    title: '工善其事总览',
                    data: '<div class="detail-grid">' +
                        '<div class="detail-card"><div class="detail-icon">🔧</div><div class="detail-title">模块数</div><div class="detail-desc">20个</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">⚙️</div><div class="detail-title">引擎</div><div class="detail-desc">运行中</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">📊</div><div class="detail-title">性能</div><div class="detail-desc">正常</div></div></div>'
                },
                2: {
                    title: '模块详情',
                    data: '<div class="detail-section"><h4>核心模块</h4>' +
                        '<div class="detail-section"><p>✅ v14-core.js</p></div>' +
                        '<div class="detail-section"><p>✅ trading-modules.js</p></div>' +
                        '<div class="detail-section"><p>✅ brain-dual.js</p></div>' +
                        '<div class="detail-section"><p>✅ security-module.js</p></div></div>'
                },
                3: {
                    title: '工程配置',
                    data: '<div class="detail-section"><h4>并发数</h4>' +
                        '<input type="number" value="5" class="form-control"></div>' +
                        '<div class="detail-section"><h4>缓存策略</h4>' +
                        '<select class="form-control"><option selected>内存缓存</option><option>Redis缓存</option><option>无缓存</option></select></div>'
                },
                4: {
                    title: '确认执行',
                    data: '<div class="detail-section"><p>确认更新工程配置？</p></div>' +
                        '<div class="detail-section"><p>并发数: 5</p></div>' +
                        '<div class="detail-section"><p>缓存: 内存缓存</p></div>'
                }
            };
            var c = contents[level] || contents[1];
            return '<div class="module-detail"><h2>' + c.title + '</h2>' + c.data + '</div>';
        }
    };
    
    // ========== CustomizeModule - 可迭代定制 ==========
    window.CustomizeModule = {
        state: { level: 1 },
        init: function() { console.log('🎨 CustomizeModule initialized'); },
        renderPanel: function(level) {
            level = level || 1;
            this.state.level = level;
            var contents = {
                1: {
                    title: '可迭代定制总览',
                    data: '<div class="detail-grid">' +
                        '<div class="detail-card"><div class="detail-icon">🎨</div><div class="detail-title">主题</div><div class="detail-desc">夜空蓝</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">📝</div><div class="detail-title">布局</div><div class="detail-desc">默认</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">🔤</div><div class="detail-title">字体</div><div class="detail-desc">Inter</div></div></div>'
                },
                2: {
                    title: '定制详情',
                    data: '<div class="detail-section"><h4>颜色配置</h4>' +
                        '<div class="detail-section"><p>主色: #0A0E17 (夜空蓝)</p></div>' +
                        '<div class="detail-section"><p>强调色: #00D4AA (翡翠绿)</p></div>' +
                        '<div class="detail-section"><p>辅助色: #7C3AED (紫罗兰)</p></div></div>'
                },
                3: {
                    title: '定制配置',
                    data: '<div class="detail-section"><h4>主题</h4>' +
                        '<select class="form-control"><option selected>暗色</option><option>亮色</option><option>自动</option></select></div>' +
                        '<div class="detail-section"><h4>主色调</h4>' +
                        '<input type="color" value="#0A0E17" class="form-control"></div>'
                },
                4: {
                    title: '确认应用',
                    data: '<div class="detail-section"><p>确认应用定制设置？</p></div>' +
                        '<div class="detail-section"><p>主题: 暗色</p></div>' +
                        '<div class="detail-section"><p>主色调: #0A0E17</p></div>'
                }
            };
            var c = contents[level] || contents[1];
            return '<div class="module-detail"><h2>' + c.title + '</h2>' + c.data + '</div>';
        }
    };
    
    // ========== SettingsModule - 设置系统 ==========
    window.SettingsModule = {
        state: { level: 1 },
        init: function() { console.log('⚙️ SettingsModule initialized'); },
        renderPanel: function(level) {
            level = level || 1;
            this.state.level = level;
            var contents = {
                1: {
                    title: '设置总览',
                    data: '<div class="detail-grid">' +
                        '<div class="detail-card"><div class="detail-icon">👤</div><div class="detail-title">账户</div><div class="detail-desc">已登录</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">🔔</div><div class="detail-title">通知</div><div class="detail-desc">已开启</div></div>' +
                        '<div class="detail-card"><div class="detail-icon">🌐</div><div class="detail-title">语言</div><div class="detail-desc">中文</div></div></div>'
                },
                2: {
                    title: '设置详情',
                    data: '<div class="detail-section"><h4>账户信息</h4>' +
                        '<div class="detail-section"><p>用户名: Admin</p></div>' +
                        '<div class="detail-section"><p>用户模式: 专家</p></div>' +
                        '<div class="detail-section"><p>注册时间: 2026-03-14</p></div></div>'
                },
                3: {
                    title: '设置配置',
                    data: '<div class="detail-section"><h4>通知设置</h4>' +
                        '<label><input type="checkbox" checked> 邮件通知</label><br>' +
                        '<label><input type="checkbox" checked> 推送通知</label><br>' +
                        '<label><input type="checkbox"> 短信通知</label></div>' +
                        '<div class="detail-section"><h4>隐私设置</h4>' +
                        '<label><input type="checkbox"> 公开我的交易</label></div>'
                },
                4: {
                    title: '确认保存',
                    data: '<div class="detail-section"><p>确认保存设置？</p></div>' +
                        '<div class="detail-section"><p>通知: 邮件+推送</p></div>' +
                        '<div class="detail-section"><p>隐私: 私有</p></div>'
                }
            };
            var c = contents[level] || contents[1];
            return '<div class="module-detail"><h2>' + c.title + '</h2>' + c.data + '</div>';
        }
    };
    
    console.log('✅ V14 modules (v13-based) loaded - 20 modules with 4-level pages');
})();
