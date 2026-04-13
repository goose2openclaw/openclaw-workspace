// ========== 安全机制模块 (V14) ==========
const SecurityMechanism = {
    state: { 
        level: 1,
        securityScore: 92,
        lastAudit: '2026-04-06 10:30',
        protections: {
            apiKey: true,
            twoFactor: true,
            whitelist: true,
            delayTrade: true,
            autoLogout: true
        },
        logs: [
            { time: '14:32:15', action: '登录成功', ip: '192.168.1.100', status: 'ok' },
            { time: '14:25:03', action: 'API调用', ip: '192.168.1.100', status: 'ok' },
            { time: '13:45:22', action: '交易执行', ip: '192.168.1.100', status: 'ok' },
            { time: '12:30:00', action: '白名单修改', ip: '192.168.1.100', status: 'warning' }
        ]
    },
    
    init: function() { console.log('🛡️ SecurityMechanism initialized'); },
    
    renderPanel: function(level) {
        level = level || 1;
        var contents = {
            1: { title: '安全总览', data: this.getOverview() },
            2: { title: '安全规则', data: this.getRules() },
            3: { title: '操作日志', data: this.getLogs() },
            4: { title: '安全设置', data: this.getSettings() }
        };
        var c = contents[level] || contents[1];
        return '<div class="module-detail">' +
            '<h2>' + c.title + '</h2>' +
            c.data +
            '</div>';
    },
    
    getOverview: function() {
        return '<div class="security-summary">' +
            '<div class="security-score">' +
            '<div class="score-circle" style="--score: ' + this.state.securityScore + '%; --color: ' + (this.state.securityScore > 80 ? '#00d4aa' : '#f59e0b') + ';">' +
            '<div class="score-value">' + this.state.securityScore + '</div>' +
            '<div class="score-label">安全评分</div>' +
            '</div>' +
            '<div class="score-info">' +
            '<p>上次审计: ' + this.state.lastAudit + '</p>' +
            '<p class="' + (this.state.securityScore > 80 ? 'good' : 'warning') + '">' + (this.state.securityScore > 80 ? '✓ 安全状态良好' : '⚠️ 建议加强安全措施') + '</p>' +
            '</div>' +
            '</div>' +
            '<div class="protection-status">' +
            '<h4>防护状态</h4>' +
            '<div class="protection-items">' +
            '<div class="protection-item ' + (this.state.protections.apiKey ? 'on' : 'off') + '"><span>🔑</span><span>API密钥</span><span class="status">' + (this.state.protections.apiKey ? '启用' : '关闭') + '</span></div>' +
            '<div class="protection-item ' + (this.state.protections.twoFactor ? 'on' : 'off') + '"><span>🔐</span><span>双重验证</span><span class="status">' + (this.state.protections.twoFactor ? '启用' : '关闭') + '</span></div>' +
            '<div class="protection-item ' + (this.state.protections.whitelist ? 'on' : 'off') + '"><span>📋</span><span>IP白名单</span><span class="status">' + (this.state.protections.whitelist ? '启用' : '关闭') + '</span></div>' +
            '<div class="protection-item ' + (this.state.protections.delayTrade ? 'on' : 'off') + '"><span>⏱️</span><span>延迟交易</span><span class="status">' + (this.state.protections.delayTrade ? '启用' : '关闭') + '</span></div>' +
            '<div class="protection-item ' + (this.state.protections.autoLogout ? 'on' : 'off') + '"><span>⏻</span><span>自动登出</span><span class="status">' + (this.state.protections.autoLogout ? '启用' : '关闭') + '</span></div>' +
            '</div></div>';
    },
    
    getRules: function() {
        return '<div class="security-rules">' +
            '<h4>安全规则</h4>' +
            '<div class="rule-item">' +
            '<div class="rule-info"><span class="rule-icon">🔑</span><div><div class="rule-name">API密钥轮换</div><div class="rule-desc">90天自动更换API密钥</div></div></div>' +
            '<div class="rule-toggle on"><span class="toggle-track"><span class="toggle-thumb"></span></span></div>' +
            '</div>' +
            '<div class="rule-item">' +
            '<div class="rule-info"><span class="rule-icon">⏱️</span><div><div class="rule-name">交易延迟</div><div class="rule-desc">大额交易延迟5秒确认</div></div></div>' +
            '<div class="rule-toggle on"><span class="toggle-track"><span class="toggle-thumb"></span></span></div>' +
            '</div>' +
            '<div class="rule-item">' +
            '<div class="rule-info"><span class="rule-icon">📋</span><div><div class="rule-name">IP白名单</div><div class="rule-desc">仅允许注册IP地址访问</div></div></div>' +
            '<div class="rule-toggle on"><span class="toggle-track"><span class="toggle-thumb"></span></span></div>' +
            '</div>' +
            '<div class="rule-item">' +
            '<div class="rule-info"><span class="rule-icon">🔔</span><div><div class="rule-name">异常告警</div><div class="rule-desc">检测到异常操作立即告警</div></div></div>' +
            '<div class="rule-toggle on"><span class="toggle-track"><span class="toggle-thumb"></span></span></div>' +
            '</div>';
    },
    
    getLogs: function() {
        var html = '<div class="logs-list">';
        html += '<table><thead><tr><th>时间</th><th>操作</th><th>IP地址</th><th>状态</th></tr></thead><tbody>';
        this.state.logs.forEach(function(log) {
            var statusClass = log.status === 'ok' ? 'success' : 'warning';
            html += '<tr><td class="mono">' + log.time + '</td><td>' + log.action + '</td><td class="mono">' + log.ip + '</td><td class="' + statusClass + '">' + log.status + '</td></tr>';
        });
        html += '</tbody></table>';
        return html;
    },
    
    getSettings: function() {
        return '<div class="security-settings">' +
            '<h4>安全设置</h4>' +
            '<div class="setting-group">' +
            '<div class="setting-item">' +
            '<label>自动登出时间</label>' +
            '<select><option>5分钟</option><option selected>15分钟</option><option>30分钟</option><option>1小时</option></select>' +
            '</div>' +
            '<div class="setting-item">' +
            '<label>交易密码</label>' +
            '<input type="password" placeholder="设置交易密码">' +
            '</div>' +
            '<div class="setting-item">' +
            '<label>紧急联系人</label>' +
            '<input type="text" placeholder="输入邮箱或手机">' +
            '</div>' +
            '</div>' +
            '<div class="danger-zone">' +
            '<h4>危险区域</h4>' +
            '<button class="danger-btn">导出所有数据</button>' +
            '<button class="danger-btn">重置安全设置</button>' +
            '</div></div>';
    }
};

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() { SecurityMechanism.init(); });
} else { SecurityMechanism.init(); }
