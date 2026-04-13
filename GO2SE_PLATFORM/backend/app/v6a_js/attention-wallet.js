// ========== 注意力看板 ==========
var attentionBoard = {
    pinned: [],
    followed: [],
    settings: { maxItems: 10, autoRefresh: true, customReq: '' }
};

function awLoadData() {
    try {
        var saved = localStorage.getItem('attentionBoard');
        if (saved) {
            var data = JSON.parse(saved);
            attentionBoard.pinned = data.pinned || [];
            attentionBoard.followed = data.followed || [];
            attentionBoard.settings = data.settings || attentionBoard.settings;
        }
    } catch(e) {}
}

function awSaveData() {
    try { localStorage.setItem('attentionBoard', JSON.stringify(attentionBoard)); } catch(e) {}
}

function togglePin(sectionId, title) {
    awLoadData();
    var idx = attentionBoard.pinned.findIndex(function(p) { return p.id === sectionId; });
    if (idx >= 0) {
        attentionBoard.pinned.splice(idx, 1);
        awShowToast('已取消置顶');
    } else {
        attentionBoard.pinned.push({ id: sectionId, title: title, time: Date.now() });
        awShowToast('已置顶到注意力看板');
    }
    awSaveData();
    awRenderAttentionBoard();
    awUpdatePinButtons();
}

function awUnpinItem(sourceId) {
    awLoadData();
    attentionBoard.pinned = attentionBoard.pinned.filter(function(p) { return p.id !== sourceId; });
    awSaveData();
    awRenderAttentionBoard();
    awUpdatePinButtons();
    awShowToast('已取消置顶');
}

function awUnfollowItem(sourceId) {
    awLoadData();
    attentionBoard.followed = attentionBoard.followed.filter(function(f) { return f.id !== sourceId; });
    awSaveData();
    awRenderAttentionBoard();
    awShowToast('已取消关注');
}

function toggleFollow(itemId, title, source) {
    awLoadData();
    var idx = attentionBoard.followed.findIndex(function(f) { return f.id === itemId; });
    if (idx >= 0) {
        attentionBoard.followed.splice(idx, 1);
        awShowToast('已取消关注');
    } else {
        attentionBoard.followed.push({ id: itemId, title: title, source: source, time: Date.now() });
        awShowToast('已关注');
    }
    awSaveData();
    awRenderAttentionBoard();
    awUpdateFollowButtons();
}

function awRenderAttentionBoard() {
    var container = document.getElementById('attentionContent');
    if (!container) return;
    awLoadData();
    var html = '';
    if (attentionBoard.pinned.length === 0 && attentionBoard.followed.length === 0) {
        html = '<div style="text-align:center; padding:40px 20px; color:#666;"><div style="font-size:48px; margin-bottom:15px;">📌</div><div style="color:#888;">点击任意板块的 📌 按钮置顶到此处</div><div style="color:#555; font-size:12px; margin-top:10px;">点击 👁 关注按钮将内容加入看板</div></div>';
    } else {
        if (attentionBoard.pinned.length > 0) {
            html += '<div style="margin-bottom:20px;"><h4 style="color:#00d4aa; margin-bottom:10px;">📌 已置顶</h4>';
            attentionBoard.pinned.forEach(function(p) {
                html += '<div class="attention-item pinned" onclick="awNavigateTo(\'' + p.id + '\')">';
                html += '<span>' + p.title + '</span>';
                html += '<button onclick="event.stopPropagation(); awUnpinItem(\'' + p.id + '\')" style="background:none; border:none; color:#ef4444; cursor:pointer; font-size:16px; padding:0 5px;">×</button>';
                html += '</div>';
            });
            html += '</div>';
        }
        if (attentionBoard.followed.length > 0) {
            html += '<div><h4 style="color:#a78bfa; margin-bottom:10px;">👁 已关注</h4>';
            attentionBoard.followed.forEach(function(f) {
                html += '<div class="attention-item followed">';
                html += '<span onclick="awNavigateTo(\'' + f.source + '\')" style="cursor:pointer;">' + f.title + '</span>';
                html += '<button onclick="awUnfollowItem(\'' + f.id + '\')" style="background:none; border:none; color:#888; cursor:pointer; padding:0 5px;">×</button>';
                html += '</div>';
            });
            html += '</div>';
        }
    }
    container.innerHTML = html;
}

function awUpdatePinButtons() {
    awLoadData();
    document.querySelectorAll('.pin-btn').forEach(function(btn) {
        var sectionId = btn.getAttribute('data-section');
        if (!sectionId) return;
        var isPinned = attentionBoard.pinned.some(function(p) { return p.id === sectionId; });
        btn.textContent = isPinned ? '📌 已置顶' : '📌 置顶';
        btn.classList.toggle('active', isPinned);
    });
}

function awUpdateFollowButtons() {
    awLoadData();
    document.querySelectorAll('.follow-btn').forEach(function(btn) {
        var itemId = btn.getAttribute('data-item');
        if (!itemId) return;
        var isFollowed = attentionBoard.followed.some(function(f) { return f.id === itemId; });
        btn.textContent = isFollowed ? '👁' : '👁🏻';
    });
}

function awShowSettings(panelId) {
    var panel = document.getElementById(panelId);
    if (panel) panel.classList.remove('hidden');
}

function awCloseSettings(panelId) {
    var panel = document.getElementById(panelId);
    if (panel) panel.classList.add('hidden');
}

function updateAttentionCount(val) {
    document.getElementById('attentionCountVal').textContent = val;
    attentionBoard.settings.maxItems = parseInt(val);
    awSaveData();
}

function toggleAutoRefresh(btn) {
    btn.classList.toggle('active');
    attentionBoard.settings.autoRefresh = btn.classList.contains('active');
    btn.textContent = attentionBoard.settings.autoRefresh ? '开' : '关';
    awSaveData();
}

function applyAttentionSettings() {
    var req = document.getElementById('attentionAdvancedSettings').value;
    attentionBoard.settings.customReq = req;
    awSaveData();
    awShowToast('设置已应用');
    awCloseSettings('attentionSettingsPanel');
}

function awNavigateTo(sectionId) {
    navigateTo(sectionId);
}

function awShowToast(msg) {
    var toast = document.getElementById('toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'toast';
        toast.style.cssText = 'position:fixed; bottom:20px; left:50%; transform:translateX(-50%); background:#00d4aa; color:#000; padding:10px 20px; border-radius:20px; font-size:14px; z-index:10001; opacity:0; transition:opacity 0.3s;';
        document.body.appendChild(toast);
    }
    toast.textContent = msg;
    toast.style.opacity = '1';
    setTimeout(function() { toast.style.opacity = '0'; }, 2000);
}

function awClearAll() {
    if (confirm('确定清除所有置顶和关注？')) {
        attentionBoard.pinned = [];
        attentionBoard.followed = [];
        awSaveData();
        awRenderAttentionBoard();
        awUpdatePinButtons();
        awShowToast('已全部清除');
    }
}

// ========== 钱包资产系统 ==========
var walletData = {
    // 外部钱包API数据
    external: { balance: 45000, label: '外部钱包' },
    // 各工具钱包 (从外部钱包分配)
    tools: {
        rabbit: { balance: 25000, pos: '25%', label: '🐰 打兔子', win: '72%' },
        mole: { balance: 20000, pos: '20%', label: '🐹 打地鼠', win: '62%' },
        oracle: { balance: 15000, pos: '15%', label: '🔮 走着瞧', win: '70%' },
        leader: { balance: 15000, pos: '15%', label: '👑 跟大哥', win: '78%' },
        hitchhiker: { balance: 10000, pos: '10%', label: '🍀 搭便车', win: '65%' },
        airdrop: { balance: 3000, pos: '3%', label: '💰 薅羊毛', win: '55%' },
        crowdsource: { balance: 2000, pos: '2%', label: '👶 穷孩子', win: '50%' }
    },
    // 中转钱包
    transfer: { balance: 10000, label: '中转钱包' },
    // 保证金钱包
    guarantee: { balance: 5000, label: '保证金' },
    // 应付款项(含贷款)
    payable: { loans: 50000, fees: 2000, label: '应付款项' }
};

// 计算总资产
function getTotalAssets() {
    var toolsTotal = 0;
    for (var key in walletData.tools) {
        toolsTotal += walletData.tools[key].balance;
    }
    var total = walletData.external.balance + toolsTotal + walletData.transfer.balance + walletData.guarantee.balance;
    var payable = walletData.payable.loans + walletData.payable.fees;
    return { gross: total, net: total - payable, payable: payable };
}

var walletHidden = true;
var walletLevel = 1;
var walletContext = {};

// 渲染资金总额
function renderWalletTotal() {
    var container = document.getElementById('walletTotalAmount');
    if (!container) return;
    var assets = getTotalAssets();
    if (walletHidden) {
        var displayNet = assets.net.toString().replace(/\d(?=.{3})/g, '*');
        container.innerHTML = '<span style="color:#00d4aa; font-size:28px; font-weight:700;">$' + displayNet + '</span> <button onclick="toggleTotalVisibility()" style="background:rgba(0,212,170,0.2); border:1px solid #00d4aa; color:#00d4aa; padding:5px 12px; border-radius:15px; cursor:pointer; font-size:12px; margin-left:10px;">👁 显示</button>';
    } else {
        container.innerHTML = '<div style="display:flex; flex-direction:column; gap:5px;"><span style="color:#00d4aa; font-size:28px; font-weight:700;">$' + assets.net.toLocaleString() + '</span><span style="color:#888; font-size:11px;">总额 $' + assets.gross.toLocaleString() + ' | 负债 $' + assets.payable.toLocaleString() + '</span></div> <button onclick="toggleTotalVisibility()" style="background:rgba(0,212,170,0.2); border:1px solid #00d4aa; color:#00d4aa; padding:5px 12px; border-radius:15px; cursor:pointer; font-size:12px; margin-left:10px; align-self:flex-start;">🔒 隐藏</button>';
    }
}

function toggleTotalVisibility() {
    walletHidden = !walletHidden;
    renderWalletTotal();
}

// 渲染钱包详情
function renderWalletDetails() {
    var container = document.getElementById('walletDetails');
    if (!container) return;
    var assets = getTotalAssets();
    var html = '<div style="display:grid; gap:10px; margin-top:15px;">';
    
    // 外部钱包 + 保证金
    html += '<div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">';
    html += '<div class="wallet-card" onclick="showWalletPage(2, \'external\')"><div style="display:flex; justify-content:space-between; align-items:center;"><span style="font-weight:600;">💼 外部钱包</span><span style="color:#00d4aa; font-weight:700;">$' + walletData.external.balance.toLocaleString() + '</span></div></div>';
    html += '<div class="wallet-card" onclick="showWalletPage(2, \'guarantee\')"><div style="display:flex; justify-content:space-between; align-items:center;"><span style="font-weight:600;">🔐 保证金</span><span style="color:#00d4aa; font-weight:700;">$' + walletData.guarantee.balance.toLocaleString() + '</span></div></div>';
    html += '</div>';
    
    // 中转钱包
    html += '<div class="wallet-card" onclick="showWalletPage(2, \'transfer\')"><div style="display:flex; justify-content:space-between; align-items:center;"><span style="font-weight:600;">🔄 中转钱包</span><span style="color:#00d4aa; font-weight:700;">$' + walletData.transfer.balance.toLocaleString() + '</span></div></div>';
    
    // 工具钱包
    html += '<div style="margin-top:10px;"><div style="color:#888; font-size:11px; margin-bottom:8px;">🎯 工具钱包 (分配自外部钱包)</div>';
    html += '<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(140px, 1fr)); gap:8px;">';
    for (var key in walletData.tools) {
        var tool = walletData.tools[key];
        html += '<div class="wallet-card small" onclick="showWalletPage(2, \'' + key + '\')" style="cursor:pointer;">';
        html += '<div style="display:flex; align-items:center; gap:6px;"><span style="font-size:16px;">' + tool.label.split(' ')[0] + '</span><span style="font-size:12px; color:#fff;">' + tool.label.split(' ')[1] + '</span></div>';
        html += '<div style="display:flex; justify-content:space-between; margin-top:5px;"><span style="color:#00d4aa; font-size:13px;">$' + tool.balance.toLocaleString() + '</span><span style="color:#888; font-size:10px;">' + tool.pos + '</span></div>';
        html += '</div>';
    }
    html += '</div></div>';
    
    // 应付款项
    html += '<div style="margin-top:10px;"><div style="color:#888; font-size:11px; margin-bottom:8px;">⚠️ 应付款项 (含贷款)</div>';
    html += '<div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">';
    html += '<div class="wallet-card" style="border-color:rgba(239,68,68,0.3);"><div style="display:flex; justify-content:space-between;"><span>💳 贷款</span><span style="color:#ef4444;">-$' + walletData.payable.loans.toLocaleString() + '</span></div></div>';
    html += '<div class="wallet-card" style="border-color:rgba(239,68,68,0.3);"><div style="display:flex; justify-content:space-between;"><span>📋 费用</span><span style="color:#ef4444;">-$' + walletData.payable.fees.toLocaleString() + '</span></div></div>';
    html += '</div></div>';
    
    html += '</div>';
    container.innerHTML = html;
}

// 4级页面导航
function showWalletPage(level, context) {
    walletLevel = level;
    walletContext = context || {};
    var container = document.getElementById('walletPageContainer');
    if (!container) return;
    var html = '';
    
    if (level === 1) {
        // Level 1: 资产总览
        var assets = getTotalAssets();
        html = '<div class="page-header"><button onclick="closeWalletPage()" style="background:none; border:none; color:#888; font-size:20px; cursor:pointer;">×</button><h3>💰 资产总览</h3></div>';
        html += '<div class="page-content">';
        html += '<div class="wallet-balance-large">$' + assets.net.toLocaleString() + '</div>';
        html += '<div style="background:rgba(0,0,0,0.3); padding:12px; border-radius:10px; margin:15px 0; display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px; text-align:center;">';
        html += '<div><div style="color:#888; font-size:10px;">总额</div><div style="color:#fff; font-size:14px; font-weight:600;">$' + assets.gross.toLocaleString() + '</div></div>';
        html += '<div><div style="color:#888; font-size:10px;">负债</div><div style="color:#ef4444; font-size:14px; font-weight:600;">-$' + assets.payable.toLocaleString() + '</div></div>';
        html += '<div><div style="color:#888; font-size:10px;">净资</div><div style="color:#00d4aa; font-size:14px; font-weight:600;">$' + assets.net.toLocaleString() + '</div></div>';
        html += '</div>';
        html += '<div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px; margin-bottom:20px;">';
        html += '<div style="text-align:center; padding:12px; background:rgba(0,0,0,0.3); border-radius:10px;"><div style="color:#888; font-size:10px;">总仓位</div><div style="color:#00d4aa; font-size:18px; font-weight:700;">90%</div></div>';
        html += '<div style="text-align:center; padding:12px; background:rgba(0,0,0,0.3); border-radius:10px;"><div style="color:#888; font-size:10px;">均胜率</div><div style="color:#00d4aa; font-size:18px; font-weight:700;">65%</div></div>';
        html += '<div style="text-align:center; padding:12px; background:rgba(0,0,0,0.3); border-radius:10px;"><div style="color:#a78bfa; font-size:10px;">MiroFish</div><div style="color:#a78bfa; font-size:18px; font-weight:700;">97.2</div></div>';
        html += '</div>';
        html += '<div style="margin-top:20px;"><h4 style="color:#888; font-size:12px; margin-bottom:10px;">选择钱包查看详情</h4>';
        html += '<div class="wallet-option" onclick="showWalletPage(2, \'external\')"><span>💼 外部钱包</span><span style="color:#00d4aa;">$' + walletData.external.balance.toLocaleString() + ' →</span></div>';
        html += '<div class="wallet-option" onclick="showWalletPage(2, \'guarantee\')"><span>🔐 保证金</span><span style="color:#00d4aa;">$' + walletData.guarantee.balance.toLocaleString() + ' →</span></div>';
        html += '<div class="wallet-option" onclick="showWalletPage(2, \'transfer\')"><span>🔄 中转钱包</span><span style="color:#00d4aa;">$' + walletData.transfer.balance.toLocaleString() + ' →</span></div>';
        for (var key in walletData.tools) {
            var tool = walletData.tools[key];
            html += '<div class="wallet-option" onclick="showWalletPage(2, \'' + key + '\')"><span>' + tool.label + '</span><span style="color:#00d4aa;">$' + tool.balance.toLocaleString() + ' →</span></div>';
        }
        html += '<div class="wallet-option" style="border-color:rgba(239,68,68,0.3);" onclick="showWalletPage(2, \'payable\')"><span>⚠️ 应付款项</span><span style="color:#ef4444;">-$' + assets.payable.toLocaleString() + ' →</span></div>';
        html += '</div></div>';
        
    } else if (level === 2) {
        // Level 2: 钱包详情
        var wallet = null;
        var walletName = '';
        if (walletContext === 'external') { wallet = walletData.external; walletName = '外部钱包'; }
        else if (walletContext === 'transfer') { wallet = walletData.transfer; walletName = '中转钱包'; }
        else if (walletContext === 'guarantee') { wallet = walletData.guarantee; walletName = '保证金'; }
        else if (walletData.tools[walletContext]) { wallet = walletData.tools[walletContext]; walletName = wallet.label; }
        if (!wallet) { closeWalletPage(); return; }
        html = '<div class="page-header"><button onclick="showWalletPage(1)" style="background:none; border:none; color:#888; font-size:20px; cursor:pointer;">←</button><h3>' + walletName + '</h3></div>';
        html += '<div class="page-content">';
        html += '<div class="wallet-balance-large">$' + wallet.balance.toLocaleString() + '</div>';
        html += '<div style="background:rgba(0,0,0,0.3); padding:15px; border-radius:10px; margin:15px 0;">';
        if (wallet.pos) html += '<div style="display:flex; justify-content:space-between; margin-bottom:8px;"><span style="color:#888;">仓位</span><span style="color:#00d4aa;">' + wallet.pos + '</span></div>';
        if (wallet.win) html += '<div style="display:flex; justify-content:space-between;"><span style="color:#888;">胜率</span><span style="color:#00d4aa;">' + wallet.win + '</span></div>';
        html += '</div>';
        html += '<div style="display:grid; gap:10px;">';
        html += '<button class="page-btn primary" onclick="showWalletPage(3, \'' + walletContext + '\')">🔄 转账</button>';
        html += '<button class="page-btn secondary" onclick="awShowToast(\'功能开发中\')">⚙️ 设置</button>';
        html += '<button class="page-btn secondary" onclick="awShowToast(\'历史记录开发中\')">📜 历史</button>';
        html += '</div></div>';
        
    } else if (level === 3) {
        // Level 3: 操作确认
        var fromName = walletContext === 'external' ? '外部钱包' : walletContext === 'transfer' ? '中转钱包' : walletContext === 'guarantee' ? '保证金' : walletContext === 'payable' ? '应付款项' : (walletData.tools[walletContext] ? walletData.tools[walletContext].label : '钱包');
        html = '<div class="page-header"><button onclick="showWalletPage(2, walletContext)" style="background:none; border:none; color:#888; font-size:20px; cursor:pointer;">←</button><h3>⚠️ 确认转账</h3></div>';
        html += '<div class="page-content">';
        html += '<div class="confirm-box">';
        html += '<div style="text-align:center; padding:30px;">';
        html += '<div style="font-size:48px; margin-bottom:20px;">🔄</div>';
        html += '<div style="font-size:16px; color:#888; margin-bottom:10px;">从</div>';
        html += '<div style="font-size:18px; font-weight:600; margin-bottom:15px;">' + fromName + '</div>';
        html += '<div style="font-size:24px; font-weight:700; color:#00d4aa; margin:20px 0;">$1,000</div>';
        html += '<div style="font-size:16px; color:#888; margin-bottom:10px;">到</div>';
        html += '<div style="font-size:18px; font-weight:600;">中转钱包</div>';
        html += '</div>';
        html += '<div style="display:grid; gap:10px; margin-top:20px;">';
        html += '<button class="page-btn primary" onclick="executeTransfer()">✅ 确认转账</button>';
        html += '<button class="page-btn secondary" onclick="showWalletPage(2, walletContext)">取消</button>';
        html += '</div></div></div>';
        
    } else if (level === 4) {
        // Level 4: 结果返回
        html = '<div class="page-header"><button onclick="closeWalletPage()" style="background:none; border:none; color:#888; font-size:20px; cursor:pointer;">×</button><h3>📋 转账结果</h3></div>';
        html += '<div class="page-content">';
        html += '<div style="text-align:center; padding:50px;">';
        html += '<div style="font-size:64px; margin-bottom:20px;">✅</div>';
        html += '<div style="font-size:20px; color:#00d4aa; margin-bottom:10px;">转账成功</div>';
        html += '<div style="color:#888; margin-bottom:20px;">$1,000 已转入中转钱包</div>';
        html += '<div style="font-size:12px; color:#555; font-family:JetBrains Mono,monospace; word-break:break-all;">TX: 0x7f3e...8a2b</div>';
        html += '</div>';
        html += '<button class="page-btn primary" onclick="closeWalletPage()" style="margin-top:30px;">完成</button>';
        html += '</div>';
    }
    
    container.innerHTML = html;
    container.style.display = 'block';
}

function closeWalletPage() {
    var container = document.getElementById('walletPageContainer');
    if (container) container.style.display = 'none';
    walletLevel = 1;
}

function executeTransfer() {
    // 模拟转账
    awShowToast('转账处理中...');
    setTimeout(function() {
        showWalletPage(4, 'success');
    }, 1000);
}

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    awLoadData();
    awRenderAttentionBoard();
    awUpdatePinButtons();
    awUpdateFollowButtons();
    renderWalletTotal();
    renderWalletDetails();
    
    // 绑定设置按钮事件
    document.querySelectorAll('.settings-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            var panelId = this.getAttribute('data-panel');
            if (panelId) awShowSettings(panelId);
        });
    });
    
    document.querySelectorAll('.panel-close-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            var panelId = this.getAttribute('data-close');
            if (panelId) awCloseSettings(panelId);
        });
    });
    
    document.querySelectorAll('.pin-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            var sectionId = this.getAttribute('data-section');
            var title = this.getAttribute('data-title') || sectionId;
            togglePin(sectionId, title);
        });
    });
});
