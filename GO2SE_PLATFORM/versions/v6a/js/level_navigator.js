/**
 * 🪿 GO2SE Level Navigator - 6级导航框架
 * =========================================
 * 将原有4级扩展到6级:
 * L1: 总览 (Overview)
 * L2: 详情 (Detail)
 * L3: 设置 (Settings)
 * L4: 执行 (Execute)
 * L5: 历史 (History)     - NEW
 * L6: 分析 (Analytics)  - NEW
 * 
 * 使用方式:
 *   LevelNavigator.init('WalletDeconstruct', {
 *     levels: 6,
 *     onLevelChange: function(level) { ... },
 *     historyEndpoint: '/api/backtest/history',
 *     analyticsEndpoint: '/api/performance'
 *   });
 */

var LevelNavigator = (function() {
    'use strict';
    
    var instances = {};
    
    // 层级定义
    var LEVEL_NAMES = {
        1: { name: '总览', icon: '📊', color: '#00d4aa' },
        2: { name: '详情', icon: '🔍', color: '#7c3aed' },
        3: { name: '设置', icon: '⚙️', color: '#f59e0b' },
        4: { name: '执行', icon: '▶️', color: '#ef4444' },
        5: { name: '历史', icon: '📜', color: '#3b82f6' },
        6: { name: '分析', icon: '📈', color: '#ec4899' }
    };
    
    // 层级顺序
    var LEVEL_ORDER = [1, 2, 3, 4, 5, 6];
    
    function createBreadcrumb(moduleName, currentLevel, maxLevel) {
        var html = '<div class="ln-breadcrumb">';
        for (var i = 1; i <= maxLevel; i++) {
            var levelInfo = LEVEL_NAMES[i];
            var isActive = i === currentLevel;
            var isPast = i < currentLevel;
            var isNew = i >= 5; // L5, L6 是新增的
            
            html += '<span class="ln-bread-item ' + (isActive ? 'active' : '') + ' ' + (isPast ? 'past' : '') + '" ';
            html += 'onclick="' + moduleName + '.navigateLevel(' + i + ')" ';
            html += 'style="' + (isActive ? 'color:' + levelInfo.color + ';font-weight:700;' : (isPast ? 'opacity:0.6;' : '')) + '">';
            if (isNew) {
                html += '<span class="ln-new-tag">NEW</span>';
            }
            html += levelInfo.icon + ' ' + levelInfo.name;
            html += '</span>';
            
            if (i < maxLevel) {
                html += '<span class="ln-bread-sep">›</span>';
            }
        }
        html += '</div>';
        return html;
    }
    
    function createLevelNav(moduleName, currentLevel, maxLevel) {
        var html = '<div class="ln-level-nav">';
        for (var i = 1; i <= maxLevel; i++) {
            var levelInfo = LEVEL_NAMES[i];
            var isActive = i === currentLevel;
            var isNew = i >= 5;
            
            html += '<button class="ln-level-btn ' + (isActive ? 'active' : '') + '" ';
            html += 'onclick="' + moduleName + '.navigateLevel(' + i + ')" ';
            html += 'style="' + (isActive ? 'background:' + levelInfo.color + ';color:#000;' : 'background:rgba(255,255,255,0.1);') + '">';
            if (isNew) {
                html += '<span class="ln-new-dot"></span>';
            }
            html += levelInfo.icon + ' L' + i;
            html += '</button>';
        }
        html += '</div>';
        return html;
    }
    
    function init(moduleName, config) {
        config = config || {};
        var maxLevel = config.levels || 6;
        
        instances[moduleName] = {
            config: config,
            currentLevel: 1,
            maxLevel: maxLevel,
            history: [],
            analytics: null
        };
        
        // 创建CSS
        injectStyles();
    }
    
    function getInstance(moduleName) {
        return instances[moduleName];
    }
    
    function navigateLevel(moduleName, level) {
        var instance = instances[moduleName];
        if (!instance) return;
        
        var prevLevel = instance.currentLevel;
        instance.currentLevel = level;
        
        // 记录历史
        if (level >= 5) {
            loadHistoryData(moduleName);
        }
        if (level >= 6) {
            loadAnalyticsData(moduleName);
        }
        
        // 回调
        if (instance.config.onLevelChange) {
            instance.config.onLevelChange(level, prevLevel);
        }
    }
    
    function loadHistoryData(moduleName) {
        var instance = instances[moduleName];
        if (!instance || !instance.config.historyEndpoint) return;
        
        // 加载历史数据
        fetch(instance.config.historyEndpoint)
            .then(function(r) { return r.json(); })
            .then(function(data) {
                instance.history = data.history || data.data || [];
                if (instance.config.onHistoryLoaded) {
                    instance.config.onHistoryLoaded(instance.history);
                }
            })
            .catch(function(e) {
                console.warn('History load failed:', e);
            });
    }
    
    function loadAnalyticsData(moduleName) {
        var instance = instances[moduleName];
        if (!instance || !instance.config.analyticsEndpoint) return;
        
        fetch(instance.config.analyticsEndpoint)
            .then(function(r) { return r.json(); })
            .then(function(data) {
                instance.analytics = data;
                if (instance.config.onAnalyticsLoaded) {
                    instance.config.onAnalyticsLoaded(data);
                }
            })
            .catch(function(e) {
                console.warn('Analytics load failed:', e);
            });
    }
    
    function getBreadcrumb(moduleName) {
        var instance = instances[moduleName];
        if (!instance) return '';
        return createBreadcrumb(moduleName, instance.currentLevel, instance.maxLevel);
    }
    
    function getLevelNav(moduleName) {
        var instance = instances[moduleName];
        if (!instance) return '';
        return createLevelNav(moduleName, instance.currentLevel, instance.maxLevel);
    }
    
    function renderHistoryPanel(moduleName, historyData) {
        var instance = instances[moduleName];
        historyData = historyData || instance.history || [];
        
        var html = '<div class="ln-history-panel">';
        html += '<h3>📜 历史记录</h3>';
        
        if (historyData.length === 0) {
            html += '<p class="ln-empty">暂无历史记录</p>';
        } else {
            html += '<div class="ln-history-list">';
            historyData.slice(0, 20).forEach(function(item) {
                html += '<div class="ln-history-item">';
                html += '<span class="ln-history-time">' + (item.time || item.created_at || '') + '</span>';
                html += '<span class="ln-history-action">' + (item.action || item.type || '操作') + '</span>';
                html += '<span class="ln-history-result">' + (item.result || item.status || '') + '</span>';
                html += '</div>';
            });
            html += '</div>';
        }
        
        html += '</div>';
        return html;
    }
    
    function renderAnalyticsPanel(moduleName, analyticsData) {
        var instance = instances[moduleName];
        analyticsData = analyticsData || instance.analytics || {};
        
        var html = '<div class="ln-analytics-panel">';
        html += '<h3>📈 数据分析</h3>';
        html += '<div class="ln-analytics-grid">';
        
        // 核心指标
        html += '<div class="ln-metric-card">';
        html += '<div class="ln-metric-label">总收益</div>';
        html += '<div class="ln-metric-value">' + (analyticsData.total_profit || analyticsData.profit || '0') + '</div>';
        html += '</div>';
        
        html += '<div class="ln-metric-card">';
        html += '<div class="ln-metric-label">收益率</div>';
        html += '<div class="ln-metric-value">' + (analyticsData.return_rate || analyticsData.returnRate || '0') + '%</div>';
        html += '</div>';
        
        html += '<div class="ln-metric-card">';
        html += '<div class="ln-metric-label">最大回撤</div>';
        html += '<div class="ln-metric-value">' + (analyticsData.max_drawdown || '0') + '%</div>';
        html += '</div>';
        
        html += '<div class="ln-metric-card">';
        html += '<div class="ln-metric-label">交易次数</div>';
        html += '<div class="ln-metric-value">' + (analyticsData.trade_count || analyticsData.total_trades || '0') + '</div>';
        html += '</div>';
        
        html += '</div>'; // .ln-analytics-grid
        
        // 图表区域
        html += '<div class="ln-chart-container">';
        html += '<div class="ln-chart-placeholder">📊 图表区域 (可集成Chart.js)</div>';
        html += '</div>';
        
        html += '</div>';
        return html;
    }
    
    function injectStyles() {
        if (document.getElementById('ln-styles')) return;
        
        var css = document.createElement('style');
        css.id = 'ln-styles';
        css.textContent = `
            /* Level Navigator Styles */
            .ln-breadcrumb {
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 12px 16px;
                background: rgba(255,255,255,0.05);
                border-radius: 8px;
                margin-bottom: 16px;
                flex-wrap: wrap;
            }
            .ln-bread-item {
                cursor: pointer;
                padding: 6px 12px;
                border-radius: 6px;
                transition: all 0.2s;
                font-size: 14px;
            }
            .ln-bread-item:hover { background: rgba(255,255,255,0.1); }
            .ln-bread-item.active { font-weight: 700; }
            .ln-bread-item.past { opacity: 0.5; }
            .ln-bread-sep { color: rgba(255,255,255,0.3); }
            .ln-new-tag {
                font-size: 9px;
                background: #ec4899;
                color: #fff;
                padding: 2px 4px;
                border-radius: 3px;
                margin-right: 4px;
                vertical-align: middle;
            }
            
            .ln-level-nav {
                display: flex;
                gap: 8px;
                margin-bottom: 16px;
                flex-wrap: wrap;
            }
            .ln-level-btn {
                position: relative;
                padding: 8px 16px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 13px;
                font-weight: 600;
                transition: all 0.2s;
                color: #fff;
            }
            .ln-level-btn:hover { transform: translateY(-2px); }
            .ln-level-btn.active { transform: scale(1.05); box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
            .ln-new-dot {
                position: absolute;
                top: -4px;
                right: -4px;
                width: 8px;
                height: 8px;
                background: #ec4899;
                border-radius: 50%;
                animation: ln-pulse 1.5s infinite;
            }
            @keyframes ln-pulse {
                0%, 100% { transform: scale(1); opacity: 1; }
                50% { transform: scale(1.5); opacity: 0.5; }
            }
            
            .ln-history-panel, .ln-analytics-panel {
                padding: 16px;
                background: rgba(255,255,255,0.03);
                border-radius: 12px;
                margin-top: 16px;
            }
            .ln-history-panel h3, .ln-analytics-panel h3 {
                margin: 0 0 16px 0;
                font-size: 16px;
            }
            .ln-history-list {
                max-height: 400px;
                overflow-y: auto;
            }
            .ln-history-item {
                display: flex;
                justify-content: space-between;
                padding: 10px;
                border-bottom: 1px solid rgba(255,255,255,0.1);
            }
            .ln-history-item:last-child { border-bottom: none; }
            .ln-history-time { color: rgba(255,255,255,0.5); font-size: 12px; }
            .ln-history-action { font-weight: 500; }
            .ln-history-result { color: #00d4aa; }
            .ln-empty { color: rgba(255,255,255,0.4); text-align: center; padding: 40px; }
            
            .ln-analytics-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                gap: 12px;
                margin-bottom: 16px;
            }
            .ln-metric-card {
                background: rgba(255,255,255,0.05);
                border-radius: 8px;
                padding: 12px;
                text-align: center;
            }
            .ln-metric-label { font-size: 12px; color: rgba(255,255,255,0.6); margin-bottom: 4px; }
            .ln-metric-value { font-size: 20px; font-weight: 700; color: #00d4aa; }
            .ln-chart-container {
                background: rgba(255,255,255,0.03);
                border-radius: 8px;
                padding: 20px;
                text-align: center;
            }
            .ln-chart-placeholder { color: rgba(255,255,255,0.3); }
        `;
        document.head.appendChild(css);
    }
    
    return {
        init: init,
        getInstance: getInstance,
        navigateLevel: navigateLevel,
        getBreadcrumb: getBreadcrumb,
        getLevelNav: getLevelNav,
        renderHistoryPanel: renderHistoryPanel,
        renderAnalyticsPanel: renderAnalyticsPanel,
        LEVEL_NAMES: LEVEL_NAMES
    };
})();
