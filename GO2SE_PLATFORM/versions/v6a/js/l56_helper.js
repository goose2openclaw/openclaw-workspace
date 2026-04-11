/**
 * 🪿 L5/L6 Helper - 历史记录 & 数据分析面板生成器
 * =========================================================
 * 为各模块提供统一的历史记录和分析面板
 */

var L56Helper = (function() {
    'use strict';
    
    var LEVEL_COLORS = {
        1: '#00d4aa',
        2: '#7c3aed',
        3: '#f59e0b',
        4: '#ef4444',
        5: '#3b82f6',
        6: '#ec4899'
    };
    
    var LEVEL_LABELS = {
        1: '总览',
        2: '详情',
        3: '设置',
        4: '执行',
        5: '历史',
        6: '分析'
    };
    
    var LEVEL_ICONS = {
        1: '📊',
        2: '🔍',
        3: '⚙️',
        4: '▶️',
        5: '📜',
        6: '📈'
    };
    
    /**
     * 生成面包屑导航
     */
    function breadcrumb(moduleName, currentLevel, maxLevel) {
        var html = '<div style="display:flex; gap:8px; margin-bottom:15px; flex-wrap:wrap;">';
        for (var i = 1; i <= maxLevel; i++) {
            var isActive = i === currentLevel;
            var color = LEVEL_COLORS[i];
            var label = LEVEL_LABELS[i];
            var icon = LEVEL_ICONS[i];
            
            html += '<button onclick="' + moduleName + '.navigateLevel(' + i + ')" ';
            html += 'style="padding:6px 14px; background:' + (isActive ? color : 'rgba(255,255,255,0.1)') + '; ';
            html += 'color:' + (isActive ? '#000' : '#fff') + '; border:none; border-radius:6px; ';
            html += 'cursor:pointer; font-size:13px; font-weight:' + (isActive ? '700' : '400') + ';">';
            if (i >= 5) {
                html += '<span style="font-size:9px; background:#ec4899; color:#fff; padding:1px 4px; border-radius:3px; margin-right:4px;">NEW</span>';
            }
            html += icon + ' ' + label;
            html += '</button>';
        }
        html += '</div>';
        return html;
    }
    
    /**
     * 生成L5历史记录面板
     */
    function renderLevel5(options) {
        options = options || {};
        var moduleName = options.moduleName || 'Module';
        var title = options.title || '历史记录';
        var icon = options.icon || '📜';
        var historyData = options.history || [];
        var stats = options.stats || { today: 0, week: 0, total: 0, successRate: 0 };
        
        var html = '<div style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(10,14,23,0.98); z-index:10000; overflow:auto;">';
        html += '<div style="max-width:800px; margin:0 auto; background:rgba(20,25,35,0.98); border:1px solid rgba(59,130,246,0.3); border-radius:15px; margin-top:30px; margin-bottom:30px;">';
        
        // Header
        html += '<div style="padding:20px; border-bottom:1px solid rgba(255,255,255,0.1);">';
        html += '<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">';
        html += '<div><span style="font-size:28px;">' + icon + '</span> <span style="font-size:18px; font-weight:700;">' + title + '</span> <span style="font-size:12px; color:#3b82f6; margin-left:10px;">● L5</span></div>';
        html += '<button onclick="' + moduleName + '.closePanel()" style="background:none; border:none; color:#888; font-size:24px; cursor:pointer;">✕</button>';
        html += '</div>';
        html += breadcrumb(moduleName, 5, 6);
        html += '</div>';
        
        html += '<div style="padding:20px;">';
        
        // 统计卡片
        html += '<div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:12px; margin-bottom:20px;">';
        html += '<div style="background:rgba(0,0,0,0.3); border-radius:8px; padding:15px; text-align:center;"><div style="font-size:11px; color:#888; margin-bottom:5px;">今日操作</div><div style="font-size:24px; font-weight:700; color:#3b82f6;">' + stats.today + '</div></div>';
        html += '<div style="background:rgba(0,0,0,0.3); border-radius:8px; padding:15px; text-align:center;"><div style="font-size:11px; color:#888; margin-bottom:5px;">本周操作</div><div style="font-size:24px; font-weight:700; color:#3b82f6;">' + stats.week + '</div></div>';
        html += '<div style="background:rgba(0,0,0,0.3); border-radius:8px; padding:15px; text-align:center;"><div style="font-size:11px; color:#888; margin-bottom:5px;">总操作</div><div style="font-size:24px; font-weight:700; color:#3b82f6;">' + stats.total + '</div></div>';
        html += '<div style="background:rgba(0,0,0,0.3); border-radius:8px; padding:15px; text-align:center;"><div style="font-size:11px; color:#888; margin-bottom:5px;">成功率</div><div style="font-size:24px; font-weight:700; color:#00d4aa;">' + stats.successRate + '%</div></div>';
        html += '</div>';
        
        // 历史列表
        html += '<div style="background:rgba(0,0,0,0.3); border-radius:10px; padding:15px;">';
        html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px;">📜 最近操作记录</div>';
        
        if (historyData.length === 0) {
            html += '<div style="text-align:center; padding:40px; color:#888;">暂无历史记录</div>';
        } else {
            historyData.slice(0, 20).forEach(function(item) {
                html += '<div style="display:flex; justify-content:space-between; align-items:center; padding:12px; border-bottom:1px solid rgba(255,255,255,0.1);">';
                html += '<div><span style="color:' + (item.success ? '#00d4aa' : '#ef4444') + '; margin-right:8px;">' + (item.success ? '✅' : '❌') + '</span>' + (item.action || item.type || '操作') + '</div>';
                html += '<div style="color:#888; font-size:12px;">' + (item.time || item.timestamp || '') + '</div>';
                html += '</div>';
            });
        }
        html += '</div>';
        
        html += '</div></div></div>';
        return html;
    }
    
    /**
     * 生成L6数据分析面板
     */
    function renderLevel6(options) {
        options = options || {};
        var moduleName = options.moduleName || 'Module';
        var title = options.title || '数据分析';
        var icon = options.icon || '📈';
        var analytics = options.analytics || { totalProfit: 0, returnRate: 0, maxDrawdown: 0, sharpeRatio: 0, tradeCount: 0 };
        
        var html = '<div style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(10,14,23,0.98); z-index:10000; overflow:auto;">';
        html += '<div style="max-width:800px; margin:0 auto; background:rgba(20,25,35,0.98); border:1px solid rgba(236,72,153,0.3); border-radius:15px; margin-top:30px; margin-bottom:30px;">';
        
        // Header
        html += '<div style="padding:20px; border-bottom:1px solid rgba(255,255,255,0.1);">';
        html += '<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">';
        html += '<div><span style="font-size:28px;">' + icon + '</span> <span style="font-size:18px; font-weight:700;">' + title + '</span> <span style="font-size:12px; color:#ec4899; margin-left:10px;">● L6</span></div>';
        html += '<button onclick="' + moduleName + '.closePanel()" style="background:none; border:none; color:#888; font-size:24px; cursor:pointer;">✕</button>';
        html += '</div>';
        html += breadcrumb(moduleName, 6, 6);
        html += '</div>';
        
        html += '<div style="padding:20px;">';
        
        // 指标卡片
        html += '<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(140px, 1fr)); gap:12px; margin-bottom:20px;">';
        html += '<div style="background:linear-gradient(135deg, rgba(0,212,170,0.2), rgba(0,0,0,0.3)); border-radius:10px; padding:16px;"><div style="font-size:11px; color:#888; margin-bottom:5px;">总收益</div><div style="font-size:22px; font-weight:700; color:#00d4aa;">+$' + (analytics.totalProfit || 0).toLocaleString() + '</div></div>';
        html += '<div style="background:linear-gradient(135deg, rgba(124,58,237,0.2), rgba(0,0,0,0.3)); border-radius:10px; padding:16px;"><div style="font-size:11px; color:#888; margin-bottom:5px;">收益率</div><div style="font-size:22px; font-weight:700; color:#7c3aed;">' + (analytics.returnRate || 0) + '%</div></div>';
        html += '<div style="background:linear-gradient(135deg, rgba(239,68,68,0.2), rgba(0,0,0,0.3)); border-radius:10px; padding:16px;"><div style="font-size:11px; color:#888; margin-bottom:5px;">最大回撤</div><div style="font-size:22px; font-weight:700; color:#ef4444;">-' + (analytics.maxDrawdown || 0) + '%</div></div>';
        html += '<div style="background:linear-gradient(135deg, rgba(245,158,11,0.2), rgba(0,0,0,0.3)); border-radius:10px; padding:16px;"><div style="font-size:11px; color:#888; margin-bottom:5px;">夏普比率</div><div style="font-size:22px; font-weight:700; color:#f59e0b;">' + (analytics.sharpeRatio || 0) + '</div></div>';
        html += '</div>';
        
        // 图表区域
        html += '<div style="background:rgba(0,0,0,0.3); border-radius:10px; padding:20px; margin-bottom:15px;">';
        html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px;">📊 收益趋势</div>';
        html += '<div style="height:150px; display:flex; align-items:center; justify-content:center; color:#888; background:rgba(0,0,0,0.2); border-radius:8px;">';
        html += '<div style="text-align:center;"><div style="font-size:40px; margin-bottom:10px;">📈</div><div>图表区域 (ECharts/Chart.js)</div></div>';
        html += '</div></div>';
        
        // 交易统计
        html += '<div style="background:rgba(0,0,0,0.3); border-radius:10px; padding:20px;">';
        html += '<div style="font-size:14px; font-weight:600; margin-bottom:15px;">📈 交易统计</div>';
        html += '<div style="display:grid; grid-template-columns:1fr 1fr; gap:15px;">';
        html += '<div style="display:flex; justify-content:space-between; padding:10px; background:rgba(0,0,0,0.2); border-radius:6px;"><span style="color:#888;">交易次数</span><span style="font-weight:600;">' + (analytics.tradeCount || 0) + '</span></div>';
        html += '<div style="display:flex; justify-content:space-between; padding:10px; background:rgba(0,0,0,0.2); border-radius:6px;"><span style="color:#888;">胜率</span><span style="font-weight:600; color:#00d4aa;">' + (analytics.winRate || 0) + '%</span></div>';
        html += '<div style="display:flex; justify-content:space-between; padding:10px; background:rgba(0,0,0,0.2); border-radius:6px;"><span style="color:#888;">平均收益</span><span style="font-weight:600;">$' + (analytics.avgProfit || 0).toLocaleString() + '</span></div>';
        html += '<div style="display:flex; justify-content:space-between; padding:10px; background:rgba(0,0,0,0.2); border-radius:6px;"><span style="color:#888;">盈亏比</span><span style="font-weight:600;">' + (analytics.profitFactor || 0) + '</span></div>';
        html += '</div></div>';
        
        html += '</div></div></div>';
        return html;
    }
    
    /**
     * 获取默认统计数据
     */
    function getDefaultStats() {
        return {
            today: Math.floor(Math.random() * 10) + 1,
            week: Math.floor(Math.random() * 50) + 10,
            total: Math.floor(Math.random() * 500) + 100,
            successRate: Math.floor(Math.random() * 20) + 70
        };
    }
    
    /**
     * 获取默认分析数据
     */
    function getDefaultAnalytics() {
        return {
            totalProfit: Math.floor(Math.random() * 30000) + 5000,
            returnRate: (Math.random() * 30 + 10).toFixed(1),
            maxDrawdown: (Math.random() * 15 + 5).toFixed(1),
            sharpeRatio: (Math.random() * 2 + 1).toFixed(2),
            tradeCount: Math.floor(Math.random() * 200) + 50,
            winRate: Math.floor(Math.random() * 20) + 60,
            avgProfit: Math.floor(Math.random() * 500) + 100,
            profitFactor: (Math.random() * 2 + 0.5).toFixed(2)
        };
    }
    
    return {
        breadcrumb: breadcrumb,
        renderLevel5: renderLevel5,
        renderLevel6: renderLevel6,
        getDefaultStats: getDefaultStats,
        getDefaultAnalytics: getDefaultAnalytics
    };
})();
