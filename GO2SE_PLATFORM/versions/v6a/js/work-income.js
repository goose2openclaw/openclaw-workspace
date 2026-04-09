// ========== 打工收益模块 (V14) ==========
const WorkIncome = {
    state: {
        level: 1,
        totalEarned: 1580.50,
        pendingPayment: 95.00,
        thisMonth: 680.00,
        lastMonth: 1240.50,
        tasks: [
            { id: 1, name: 'AI数据标注', platform: 'Amazon MTurk', earn: 45.50, status: 'completed', date: '2026-04-06', category: '标注' },
            { id: 2, name: '翻译任务 - 中英', platform: 'ProZ', earn: 120.00, status: 'completed', date: '2026-04-05', category: '翻译' },
            { id: 3, name: '问卷调查', platform: 'Toluna', earn: 15.00, status: 'pending', date: '2026-04-04', category: '调查' },
            { id: 4, name: 'App测试', platform: 'UserTesting', earn: 80.00, status: 'in_progress', date: '2026-04-03', category: '测试' },
            { id: 5, name: '内容审核', platform: 'Appen', earn: 200.00, status: 'completed', date: '2026-04-02', category: '审核' },
            { id: 6, name: '语音转写', platform: 'Rev', earn: 65.00, status: 'completed', date: '2026-04-01', category: '转写' }
        ],
        platforms: [
            { name: 'Amazon MTurk', icon: '🤖', tasks: 45, earn: 890, rate: 2.5 },
            { name: 'ProZ', icon: '🌐', tasks: 12, earn: 560, rate: 5.2 },
            { name: 'Toluna', icon: '📝', tasks: 28, earn: 85, rate: 0.8 },
            { name: 'UserTesting', icon: '🧪', tasks: 8, earn: 320, rate: 8.5 },
            { name: 'Appen', icon: '🔍', tasks: 15, earn: 450, rate: 4.2 }
        ],
        categories: ['标注', '翻译', '调查', '测试', '审核', '转写', '其他']
    },
    
    init: function() { console.log('💼 WorkIncome initialized'); },
    
    renderPanel: function(level) {
        level = level || 1;
        var contents = {
            1: { title: '收益总览', data: this.getOverview() },
            2: { title: '任务列表', data: this.getTasks() },
            3: { title: '平台统计', data: this.getPlatforms() },
            4: { title: '提现设置', data: this.getWithdraw() }
        };
        var c = contents[level] || contents[1];
        return '<div class="module-detail">' +
            '<h2>' + c.title + '</h2>' +
            c.data +
            '</div>';
    },
    
    getOverview: function() {
        var html = '<div class="work-summary">';
        html += '<div class="work-card">';
        html += '<div class="icon">💰</div>';
        html += '<div class="value">$' + this.state.totalEarned.toFixed(2) + '</div>';
        html += '<div class="label">总收入</div>';
        html += '</div>';
        html += '<div class="work-card">';
        html += '<div class="icon">⏳</div>';
        html += '<div class="value">$' + this.state.pendingPayment.toFixed(2) + '</div>';
        html += '<div class="label">待结算</div>';
        html += '</div>';
        html += '</div>';
        
        html += '<div class="month-comparison">';
        html += '<div class="month-stat">';
        html += '<div class="month-label">本月收入</div>';
        html += '<div class="month-value">$' + this.state.thisMonth.toFixed(2) + '</div>';
        html += '</div>';
        html += '<div class="month-vs">vs</div>';
        html += '<div class="month-stat">';
        html += '<div class="month-label">上月收入</div>';
        html += '<div class="month-value">$' + this.state.lastMonth.toFixed(2) + '</div>';
        html += '</div>';
        var change = ((this.state.thisMonth - this.state.lastMonth) / this.state.lastMonth * 100).toFixed(1);
        html += '<div class="month-change ' + (change >= 0 ? 'positive' : 'negative') + '">' + (change >= 0 ? '+' : '') + change + '%</div>';
        html += '</div>';
        
        html += '<div class="quick-actions">';
        html += '<button class="action-btn" onclick="WorkIncome.showTasks()">📋 查看任务</button>';
        html += '<button class="action-btn" onclick="WorkIncome.showPlatforms()">📊 平台统计</button>';
        html += '<button class="action-btn" onclick="WorkIncome.withdraw()">💸 申请提现</button>';
        html += '</div>';
        
        return html;
    },
    
    getTasks: function() {
        var html = '<div class="task-filters">';
        var self = this;
        this.state.categories.forEach(function(cat) {
            html += '<button class="filter-btn active" onclick="WorkIncome.filterByCategory(\'' + cat + '\')">' + cat + '</button>';
        });
        html += '</div>';
        
        html += '<div class="task-list">';
        var self = this;
        this.state.tasks.forEach(function(t) {
            var statusClass = t.status === 'completed' ? 'done' : (t.status === 'pending' ? 'pending' : 'progress');
            var statusText = t.status === 'completed' ? '已完成' : (t.status === 'pending' ? '待处理' : '进行中');
            
            html += '<div class="task-item">';
            html += '<div class="task-category">' + t.category + '</div>';
            html += '<div class="task-info">';
            html += '<div class="task-name">' + t.name + '</div>';
            html += '<div class="task-platform">' + t.platform + ' • ' + t.date + '</div>';
            html += '</div>';
            html += '<div class="task-amount">+$' + t.earn.toFixed(2) + '</div>';
            html += '<div class="task-status ' + statusClass + '">' + statusText + '</div>';
            html += '</div>';
        });
        html += '</div>';
        
        return html;
    },
    
    getPlatforms: function() {
        var html = '<div class="platform-grid">';
        var self = this;
        this.state.platforms.forEach(function(p) {
            html += '<div class="platform-card">';
            html += '<div class="platform-icon">' + p.icon + '</div>';
            html += '<div class="platform-name">' + p.name + '</div>';
            html += '<div class="platform-stats">';
            html += '<div class="platform-stat">';
            html += '<div class="stat-value">' + p.tasks + '</div>';
            html += '<div class="stat-label">任务数</div>';
            html += '</div>';
            html += '<div class="platform-stat">';
            html += '<div class="stat-value">$' + p.earn.toFixed(0) + '</div>';
            html += '<div class="stat-label">总收入</div>';
            html += '</div>';
            html += '<div class="platform-stat">';
            html += '<div class="stat-value">$' + p.rate.toFixed(1) + '</div>';
            html += '<div class="stat-label">时薪</div>';
            html += '</div>';
            html += '</div>';
            html += '</div>';
        });
        html += '</div>';
        
        html += '<div class="platform-tip">';
        html += '<h4>💡 优化建议</h4>';
        html += '<ul>';
        html += '<li>UserTesting 时薪最高($8.5)，建议多接测试任务</li>';
        html += '<li>Toluna 问卷单价较低，可减少参与</li>';
        html += '<li>ProZ 翻译任务收益稳定，保持专注</li>';
        html += '</ul>';
        html += '</div>';
        
        return html;
    },
    
    getWithdraw: function() {
        var html = '<div class="withdraw-info">';
        html += '<div class="withdraw-available">';
        html += '<div class="withdraw-label">可提现余额</div>';
        html += '<div class="withdraw-value">$' + (this.state.totalEarned - this.state.pendingPayment).toFixed(2) + '</div>';
        html += '</div>';
        
        html += '<div class="withdraw-pending">';
        html += '<div class="pending-label">待结算</div>';
        html += '<div class="pending-value">$' + this.state.pendingPayment.toFixed(2) + '</div>';
        html += '<div class="pending-note">预计 3-5 个工作日到账</div>';
        html += '</div>';
        html += '</div>';
        
        html += '<div class="withdraw-form">';
        html += '<h4>申请提现</h4>';
        html += '<div class="form-group">';
        html += '<label>提现金额</label>';
        html += '<input type="number" value="' + (this.state.totalEarned - this.state.pendingPayment).toFixed(2) + '" class="form-input">';
        html += '</div>';
        html += '<div class="form-group">';
        html += '<label>收款方式</label>';
        html += '<select class="form-select">';
        html += '<option>PayPal</option>';
        html += '<option>银行转账</option>';
        html += '<option>加密货币</option>';
        html += '</select>';
        html += '</div>';
        html += '<button class="submit-btn" onclick="WorkIncome.submitWithdraw()">确认提现</button>';
        html += '</div>';
        
        html += '<div class="withdraw-history">';
        html += '<h4>提现记录</h4>';
        html += '<div class="history-list">';
        html += '<div class="history-item">';
        html += '<div class="history-date">2026-04-01</div>';
        html += '<div class="history-method">PayPal</div>';
        html += '<div class="history-amount">-$450.00</div>';
        html += '<div class="history-status done">已完成</div>';
        html += '</div>';
        html += '<div class="history-item">';
        html += '<div class="history-date">2026-03-15</div>';
        html += '<div class="history-method">银行转账</div>';
        html += '<div class="history-amount">-$780.50</div>';
        html += '<div class="history-status done">已完成</div>';
        html += '</div>';
        html += '</div>';
        html += '</div>';
        
        return html;
    },
    
    filterByCategory: function(category) {
        console.log('Filter by:', category);
    },
    
    showTasks: function() {
        this.state.level = 2;
        this.renderPanel(2);
    },
    
    showPlatforms: function() {
        this.state.level = 3;
        this.renderPanel(3);
    },
    
    withdraw: function() {
        this.state.level = 4;
        this.renderPanel(4);
    },
    
    submitWithdraw: function() {
        alert('提现申请已提交，预计 3-5 个工作日到账');
    }
};
