// 北斗七鑫 - 金字塔流程动画 v6
(function() {
    // 隐藏splash，显示app
    var splash = document.getElementById('splash');
    var app = document.getElementById('app');
    if (splash) { splash.style.display = 'none'; splash.style.visibility = 'hidden'; }
    if (app) { app.classList.remove('hidden'); app.style.display = 'flex'; app.style.visibility = 'visible'; }

    var tools = [
        { icon: '🐰', name: '打兔子', pos: '25%', win: '72%' },
        { icon: '🐹', name: '打地鼠', pos: '20%', win: '62%' },
        { icon: '🔮', name: '走着瞧', pos: '15%', win: '70%' },
        { icon: '👑', name: '跟大哥', pos: '15%', win: '78%' },
        { icon: '🍀', name: '搭便车', pos: '10%', win: '65%' },
        { icon: '💰', name: '薅羊毛', pos: '3%', win: '55%' },
        { icon: '👶', name: '穷孩子', pos: '2%', win: '50%' }
    ];

    function renderPyramid() {
        var container = document.getElementById('beidouFlowDiagram');
        if (!container) return;
        
        var html = '<div style="display:flex; flex-direction:column; align-items:center; gap:6px; padding:20px; background:rgba(0,0,0,0.4); border-radius:15px; min-height:280px; justify-content:center; border:1px solid rgba(0,212,170,0.15);">';
        
        html += '<div class="pyr" id="pyr-6"><div style="min-width:120px; padding:14px 24px; background:rgba(16,185,129,0.15); border:2px solid rgba(16,185,129,0.4); border-radius:12px; text-align:center;"><span style="font-size:32px; display:block;">🚀</span><span style="font-size:13px; color:#10b981; margin-top:6px; display:block; font-weight:600;">执行</span></div></div>';
        html += '<div class="arr" id="arr-5">▲</div>';
        html += '<div class="pyr" id="pyr-5"><div style="display:flex; gap:10px;"><div style="min-width:95px; padding:12px; background:rgba(6,182,212,0.12); border:2px solid rgba(6,182,212,0.3); border-radius:10px; text-align:center;"><span style="font-size:26px; display:block;">📊</span><span style="font-size:11px; color:#06b6d4; margin-top:4px; display:block;">复盘</span></div><div style="min-width:95px; padding:12px; background:rgba(0,212,170,0.12); border:2px solid rgba(0,212,170,0.3); border-radius:10px; text-align:center;"><span style="font-size:26px; display:block;">🔄</span><span style="font-size:11px; color:#00d4aa; margin-top:4px; display:block;">仿真</span></div></div></div>';
        html += '<div class="arr" id="arr-4">▲</div>';
        html += '<div class="pyr" id="pyr-4"><div style="display:flex; gap:10px;"><div style="min-width:95px; padding:12px; background:rgba(236,72,153,0.12); border:2px solid rgba(236,72,153,0.3); border-radius:10px; text-align:center;"><span style="font-size:26px; display:block;">⚖️</span><span style="font-size:11px; color:#ec4899; margin-top:4px; display:block;">权重</span></div><div style="min-width:95px; padding:12px; background:rgba(245,158,11,0.12); border:2px solid rgba(245,158,11,0.3); border-radius:10px; text-align:center;"><span style="font-size:26px; display:block;">🎯</span><span style="font-size:11px; color:#f59e0b; margin-top:4px; display:block;">策略</span></div></div></div>';
        html += '<div class="arr" id="arr-3">▲</div>';
        html += '<div class="pyr" id="pyr-3"><div style="display:flex; gap:10px;"><div style="min-width:95px; padding:12px; background:rgba(139,92,246,0.12); border:2px solid rgba(139,92,246,0.3); border-radius:10px; text-align:center;"><span style="font-size:26px; display:block;">🔊</span><span style="font-size:11px; color:#8b5cf6; margin-top:4px; display:block;">声纳</span></div><div style="min-width:95px; padding:12px; background:rgba(59,130,246,0.12); border:2px solid rgba(59,130,246,0.3); border-radius:10px; text-align:center;"><span style="font-size:26px; display:block;">📡</span><span style="font-size:11px; color:#3b82f6; margin-top:4px; display:block;">信号</span></div></div></div>';
        
        html += '</div>';
        container.innerHTML = html;
    }

    function renderToolsBar() {
        var container = document.getElementById('beidouToolsPyramid');
        if (!container) return;
        var html = '<div style="display:flex; flex-wrap:wrap; gap:8px; justify-content:center; padding:15px; background:rgba(0,0,0,0.3); border-radius:10px; margin-top:15px; border:1px solid rgba(0,212,170,0.1);">';
        html += '<div style="width:100%; text-align:center; font-size:12px; color:#888; margin-bottom:10px;">🎯 7大投资工具</div>';
        tools.forEach(function(tool) {
            html += '<div style="display:flex; align-items:center; gap:6px; padding:8px 14px; background:rgba(0,212,170,0.1); border:1px solid rgba(0,212,170,0.2); border-radius:8px; font-size:12px;">';
            html += '<span style="font-size:18px;">' + tool.icon + '</span>';
            html += '<span style="color:#fff; font-weight:600;">' + tool.name + '</span>';
            html += '<span style="color:#00d4aa; font-family:JetBrains Mono,monospace; font-weight:700;">' + tool.pos + '</span>';
            html += '<span style="color:#555;">|</span>';
            html += '<span style="color:#00d4aa; font-family:JetBrains Mono,monospace; font-weight:700;">' + tool.win + '</span>';
            html += '</div>';
        });
        html += '</div>';
        container.innerHTML = html;
    }

    function renderStats() {
        var container = document.getElementById('beidouToolStats');
        if (!container) return;
        var html = '<div style="display:flex; gap:25px; align-items:center; justify-content:center; padding:12px 25px; background:rgba(0,0,0,0.4); border-radius:10px; margin-top:15px;">';
        html += '<div style="text-align:center;"><div style="font-size:11px; color:#888; margin-bottom:3px;">总仓位</div><div style="font-size:22px; color:#00d4aa; font-weight:700; font-family:JetBrains Mono,monospace;">90%</div></div>';
        html += '<div style="width:1px; height:35px; background:rgba(255,255,255,0.1);"></div>';
        html += '<div style="text-align:center;"><div style="font-size:11px; color:#888; margin-bottom:3px;">均胜率</div><div style="font-size:22px; color:#00d4aa; font-weight:700; font-family:JetBrains Mono,monospace;">65%</div></div>';
        html += '<div style="width:1px; height:35px; background:rgba(255,255,255,0.1);"></div>';
        html += '<div style="text-align:center;"><div style="font-size:11px; color:#a78bfa; margin-bottom:3px;">MiroFish</div><div style="font-size:22px; color:#a78bfa; font-weight:700; font-family:JetBrains Mono,monospace;">97.2</div></div>';
        html += '</div>';
        container.innerHTML = html;
    }

    function animatePyramid() {
        var sequence = [
            { el: 'pyr-3', arr: 'arr-3' },
            { el: 'pyr-4', arr: 'arr-4' },
            { el: 'pyr-5', arr: 'arr-5' },
            { el: 'pyr-6', arr: null }
        ];
        
        var step = 0;
        var interval = setInterval(function() {
            if (step >= sequence.length) {
                clearInterval(interval);
                showComplete();
                return;
            }
            
            var item = document.getElementById(sequence[step].el);
            if (item) {
                item.style.opacity = '1';
            }
            if (sequence[step].arr) {
                var arrow = document.getElementById(sequence[step].arr);
                if (arrow) arrow.style.opacity = '1';
            }
            
            step++;
        }, 1000);
    }

    function showComplete() {
        var container = document.getElementById('beidouFlowDiagram');
        if (container) {
            container.style.minHeight = '280px';
        }
    }

    // 初始化
    renderPyramid();
    renderToolsBar();
    renderStats();
    setTimeout(animatePyramid, 500);
})();

// 显示全部策略
function showAllStrategies() {
    var moreSection = document.getElementById('allStrategiesPanel');
    if (!moreSection) {
        // 创建全部策略面板
        var panel = document.createElement('div');
        panel.id = 'allStrategiesPanel';
        panel.style.cssText = 'position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.95); z-index:10000; overflow:auto; padding:20px; color:#fff;';
        
        var strategies = [
            { name: 'EMA趋势策略', win: 72, type: '趋势跟踪' },
            { name: 'MACD交叉策略', win: 68, type: '动量策略' },
            { name: 'RSI超买超卖', win: 65, type: '均值回归' },
            { name: '布林带策略', win: 63, type: '波动性策略' },
            { name: '成交量加权', win: 61, type: '趋势确认' },
            { name: 'KDJ随机指标', win: 60, type: '动量策略' },
            { name: '威廉指标', win: 58, type: '均值回归' },
            { name: 'CCI顺势指标', win: 57, type: '趋势跟踪' },
            { name: 'OBV能量潮', win: 56, type: '成交量策略' },
            { name: 'VWAP均价', win: 55, type: '执行策略' },
            { name: '多周期共振', win: 70, type: '组合策略' },
            { name: '123反转策略', win: 69, type: '趋势反转' },
            { name: '双均线策略', win: 67, type: '趋势跟踪' },
            { name: 'ATR止损策略', win: 64, type: '风控策略' },
            { name: '金字塔仓位', win: 66, type: '仓位管理' }
        ];
        
        var html = '<div style="max-width:600px; margin:0 auto;">';
        html += '<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">';
        html += '<h2 style="margin:0;">📋 全部策略及胜率</h2>';
        html += '<button onclick="closeAllStrategies()" style="background:#ef4444; border:none; color:#fff; padding:10px 20px; border-radius:8px; cursor:pointer;">关闭</button>';
        html += '</div>';
        html += '<div style="display:grid; gap:10px;">';
        
        strategies.forEach(function(s) {
            var barWidth = s.win + '%';
            var color = s.win >= 70 ? '#00d4aa' : s.win >= 60 ? '#f59e0b' : '#ef4444';
            html += '<div style="background:rgba(255,255,255,0.05); padding:12px 15px; border-radius:8px; border:1px solid rgba(255,255,255,0.1);">';
            html += '<div style="display:flex; justify-content:space-between; margin-bottom:8px;">';
            html += '<span style="font-weight:600;">' + s.name + '</span>';
            html += '<span style="color:' + color + '; font-weight:700; font-family:JetBrains Mono,monospace;">' + s.win + '%</span>';
            html += '</div>';
            html += '<div style="background:rgba(255,255,255,0.1); height:6px; border-radius:3px; overflow:hidden;">';
            html += '<div style="width:' + barWidth + '; height:100%; background:' + color + '; border-radius:3px;"></div>';
            html += '</div>';
            html += '<div style="font-size:11px; color:#888; margin-top:5px;">' + s.type + '</div>';
            html += '</div>';
        });
        
        html += '</div></div>';
        panel.innerHTML = html;
        document.body.appendChild(panel);
    } else {
        moreSection.style.display = moreSection.style.display === 'none' ? 'block' : 'none';
    }
}

function closeAllStrategies() {
    var panel = document.getElementById('allStrategiesPanel');
    if (panel) panel.style.display = 'none';
}
