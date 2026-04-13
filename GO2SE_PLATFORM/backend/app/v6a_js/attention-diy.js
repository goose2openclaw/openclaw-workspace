// ========== DIY注意力模块 (V14) ==========
const AttentionDIY = {
    state: {
        level: 1,
        focus: 85,
        energy: 72,
        mood: 'productive',
        streak: 7,
        todayMinutes: 180,
        weekData: [
            { day: '周一', focus: 75 },
            { day: '周二', focus: 82 },
            { day: '周三', focus: 68 },
            { day: '周四', focus: 90 },
            { day: '周五', focus: 85 },
            { day: '周六', focus: 45 },
            { day: '周日', focus: 85 }
        ],
        habits: [
            { name: '晨间冥想', icon: '🧘', streak: 14, done: true },
            { name: '深度工作', icon: '💻', streak: 7, done: true },
            { name: '阅读30分钟', icon: '📚', streak: 21, done: false },
            { name: '运动', icon: '🏃', streak: 5, done: false }
        ],
        modes: [
            { id: 'deep', icon: '🎯', name: '深度工作', duration: 25, color: '#00d4aa' },
            { id: 'meditate', icon: '🧘', name: '冥想', duration: 15, color: '#8b5cf6' },
            { id: 'read', icon: '📚', name: '阅读', duration: 30, color: '#3b82f6' },
            { id: 'code', icon: '💻', name: '编码', duration: 90, color: '#f59e0b' },
            { id: 'write', icon: '✍️', name: '写作', duration: 45, color: '#ef4444' },
            { id: 'plan', icon: '📋', name: '计划', duration: 20, color: '#06b6d4' }
        ],
        activeMode: null,
        timerInterval: null
    },
    
    init: function() { console.log('🎯 AttentionDIY initialized'); },
    
    renderPanel: function(level) {
        level = level || 1;
        var contents = {
            1: { title: '注意力总览', data: this.getOverview() },
            2: { title: '专注模式', data: this.getFocusMode() },
            3: { title: '习惯养成', data: this.getHabits() },
            4: { title: '数据报告', data: this.getReport() }
        };
        var c = contents[level] || contents[1];
        return '<div class="module-detail">' +
            '<h2>' + c.title + '</h2>' +
            c.data +
            '</div>';
    },
    
    getOverview: function() {
        var html = '<div class="attention-stats">';
        html += '<div class="stat-card green"><div class="stat-value">' + this.state.focus + '%</div><div class="stat-label">专注度</div></div>';
        html += '<div class="stat-card blue"><div class="stat-value">' + this.state.energy + '%</div><div class="stat-label">精力值</div></div>';
        html += '<div class="stat-card purple"><div class="stat-value">' + this.state.mood + '</div><div class="stat-label">状态</div></div>';
        html += '</div>';
        
        html += '<div class="focus-summary">';
        html += '<div class="focus-stat"><span class="focus-num">' + this.state.todayMinutes + '</span><span class="focus-label">今日分钟数</span></div>';
        html += '<div class="focus-stat"><span class="focus-num">' + this.state.streak + '</span><span class="focus-label">连续天数</span></div>';
        html += '</div>';
        
        html += '<div class="attention-chart">';
        html += '<h4>本周专注曲线</h4>';
        html += '<div class="chart-bars">';
        var maxFocus = Math.max.apply(null, this.state.weekData.map(function(d) { return d.focus; }));
        var self = this;
        this.state.weekData.forEach(function(d) {
            var height = (d.focus / maxFocus) * 100;
            var isToday = d.day === '周日';
            html += '<div class="chart-bar' + (isToday ? ' active' : '') + '" style="height:' + height + '%">';
            html += '<span>' + d.day + '</span>';
            html += '<span class="chart-value">' + d.focus + '%</span>';
            html += '</div>';
        });
        html += '</div></div>';
        
        return html;
    },
    
    getFocusMode: function() {
        var html = '<div class="focus-modes">';
        html += '<h4>选择专注模式</h4>';
        html += '<div class="mode-grid">';
        var self = this;
        this.state.modes.forEach(function(m) {
            var isActive = self.state.activeMode === m.id;
            html += '<div class="mode-card' + (isActive ? ' active' : '') + '" onclick="AttentionDIY.startMode(\'' + m.id + '\')">';
            html += '<div class="mode-icon" style="color:' + m.color + '">' + m.icon + '</div>';
            html += '<div class="mode-name">' + m.name + '</div>';
            html += '<div class="mode-duration">' + m.duration + '分钟</div>';
            html += '</div>';
        });
        html += '</div>';
        
        if (this.state.activeMode) {
            var mode = this.state.modes.find(function(m) { return m.id === self.state.activeMode; });
            html += '<div class="timer-display">';
            html += '<div class="timer-icon">' + mode.icon + '</div>';
            html += '<div class="timer-time" id="timerDisplay">25:00</div>';
            html += '<div class="timer-controls">';
            html += '<button class="timer-btn" onclick="AttentionDIY.pauseTimer()">暂停</button>';
            html += '<button class="timer-btn stop" onclick="AttentionDIY.stopTimer()">停止</button>';
            html += '</div></div>';
        }
        
        html += '</div>';
        return html;
    },
    
    getHabits: function() {
        var html = '<div class="habits-container">';
        var self = this;
        this.state.habits.forEach(function(h) {
            html += '<div class="habit-item' + (h.done ? ' completed' : '') + '">';
            html += '<div class="habit-icon">' + h.icon + '</div>';
            html += '<div class="habit-info">';
            html += '<div class="habit-name">' + h.name + '</div>';
            html += '<div class="habit-streak">🔥 ' + h.streak + '天连续</div>';
            html += '</div>';
            html += '<div class="habit-check"' + (h.done ? ' ✓' : '') + ' onclick="AttentionDIY.toggleHabit(\'' + h.name + '\')"></div>';
            html += '</div>';
        });
        html += '</div>';
        
        html += '<div class="add-habit">';
        html += '<input type="text" placeholder="添加新习惯..." class="habit-input" id="habitInput">';
        html += '<button onclick="AttentionDIY.addHabit()">+</button>';
        html += '</div>';
        
        return html;
    },
    
    getReport: function() {
        var html = '<div class="report-container">';
        html += '<div class="report-header">';
        html += '<h4>📊 本周专注报告</h4>';
        html += '</div>';
        
        html += '<div class="report-stats">';
        html += '<div class="report-stat">';
        html += '<div class="report-value">' + this.state.todayMinutes + '</div>';
        html += '<div class="report-label">今日专注</div>';
        html += '</div>';
        html += '<div class="report-stat">';
        var weekTotal = this.state.weekData.reduce(function(s, d) { return s + d.focus; }, 0);
        html += '<div class="report-value">' + Math.round(weekTotal / 7) + '%</div>';
        html += '<div class="report-label">平均专注</div>';
        html += '</div>';
        html += '<div class="report-stat">';
        html += '<div class="report-value">' + this.state.streak + '</div>';
        html += '<div class="report-label">连续天数</div>';
        html += '</div>';
        html += '</div>';
        
        html += '<div class="report-insights">';
        html += '<h4>💡 洞察</h4>';
        html += '<ul>';
        html += '<li>最佳专注日：周四 (90%)</li>';
        html += '<li>需要改进：周六 (仅45%)</li>';
        html += '<li>建议：周六安排轻松任务</li>';
        html += '</ul>';
        html += '</div>';
        
        html += '</div>';
        return html;
    },
    
    startMode: function(modeId) {
        this.state.activeMode = modeId;
        var mode = this.state.modes.find(function(m) { return m.id === modeId; });
        console.log('Starting focus mode:', mode.name);
        this.renderPanel(2);
    },
    
    pauseTimer: function() {
        console.log('Timer paused');
    },
    
    stopTimer: function() {
        this.state.activeMode = null;
        this.renderPanel(2);
    },
    
    toggleHabit: function(name) {
        var habit = this.state.habits.find(function(h) { return h.name === name; });
        if (habit) {
            habit.done = !habit.done;
            this.renderPanel(3);
        }
    },
    
    addHabit: function() {
        var input = document.getElementById('habitInput');
        if (input && input.value.trim()) {
            this.state.habits.push({
                name: input.value.trim(),
                icon: '⭐',
                streak: 0,
                done: false
            });
            this.renderPanel(3);
        }
    }
};
