/**
 * VV6 Auto Handler - 自动处理工善其事等通知
 *除非必须人工干预，否则自动处理
 */

class AutoHandlerVV6 {
  constructor() {
    this.name = 'AutoHandler';
    this.version = '1.0';
    this.autoMode = true;
    this.pendingTasks = [];
    this.processingHistory = [];
    
    this.init();
  }

  init() {
    console.log('🔧 AutoHandler启动...');
    this.startMonitoring();
  }

  // 启动监控
  startMonitoring() {
    // 每10秒检查一次待处理任务
    setInterval(() => {
      this.checkPendingTasks();
    }, 10000);
    
    // 每30秒检查一次alerts
    setInterval(() => {
      this.checkAlerts();
    }, 30000);
    
    // 立即执行一次检查
    setTimeout(() => {
      this.checkAlerts();
      this.checkPendingTasks();
    }, 3000);
  }

  // 检查待处理任务
  async checkPendingTasks() {
    try {
      // 检查autonomous状态
      const status = await fetch('/autonomous/status').then(r => r.json()).catch(() => null);
      if (!status) return;

      // 检查Mirofish状态
      const miro = await fetch('/autonomous/mirofish/status').then(r => r.json()).catch(() => null);
      if (miro && miro.status === 'running') {
        // Mirofish运行中，无需人工干预
        this.log('Mirofish运行中', 'auto');
      }

      // 检查gstack团队任务
      const team = await fetch('/autonomous/gstack/team').then(r => r.json()).catch(() => null);
      if (team && team.members) {
        team.members.forEach(member => {
          if (member.status === 'standby' && member.command) {
            // 待机成员，自动分配轻量任务
            this.autoAssignTask(member);
          }
        });
      }
    } catch (e) {
      console.warn('检查任务失败:', e.message);
    }
  }

  // 自动分配任务
  async autoAssignTask(member) {
    const autoTasks = {
      '工程经理': '/plan-eng-review',
      '代码审查员': '/review',
      '设计师': '/design-consultation',
      '安全官': '/cso'
    };

    const task = autoTasks[member.role];
    if (task) {
      console.log(`🤖 自动为 ${member.role} 分配任务: ${task}`);
      // 自动执行不需要人工确认的任务
      this.processingHistory.push({
        member: member.role,
        task: task,
        time: Date.now(),
        type: 'auto'
      });
    }
  }

  // 检查alerts
  async checkAlerts() {
    try {
      const alerts = await fetch('/autonomous/alerts').then(r => r.json()).catch(() => ({alerts: []}));
      
      if (alerts.alerts && alerts.alerts.length > 0) {
        console.log(`📋 发现 ${alerts.alerts.length} 个待处理alerts`);
        
        alerts.alerts.forEach(alert => {
          // 判断是否需要人工干预
          if (this.needHumanIntervention(alert)) {
            this.requestHumanReview(alert);
          } else {
            this.autoResolve(alert);
          }
        });
      }
    } catch (e) {
      console.warn('检查alerts失败:', e.message);
    }
  }

  // 判断是否需要人工干预
  needHumanIntervention(alert) {
    // 高风险操作需要人工确认
    const highRiskTypes = ['trade', 'withdraw', 'deploy', 'delete'];
    if (highRiskTypes.includes(alert.type)) return true;
    
    // 超过阈值的操作
    if (alert.amount > 10000) return true;
    
    // 未知类型
    if (!alert.type) return true;
    
    return false;
  }

  // 请求人工审核
  requestHumanReview(alert) {
    console.warn(`⚠️ 需要人工审核:`, alert);
    this.showNotification(`需要人工处理: ${alert.message || alert.type}`);
  }

  // 自动解决
  autoResolve(alert) {
    console.log(`✅ 自动处理:`, alert);
    fetch(`/autonomous/alerts/${alert.id}/acknowledge`, {method: 'POST'}).catch(() => {});
    this.processingHistory.push({
      alert: alert,
      time: Date.now(),
      type: 'auto_resolved'
    });
  }

  // 显示通知
  showNotification(message) {
    const notifBadge = document.getElementById('notifBadge');
    if (notifBadge) {
      const current = parseInt(notifBadge.textContent) || 0;
      notifBadge.textContent = current + 1;
    }
    
    // 创建临时通知
    const toast = document.createElement('div');
    toast.style.cssText = `
      position: fixed;
      top: 70px;
      right: 20px;
      background: var(--bg-secondary);
      border: 1px solid var(--primary);
      border-radius: 8px;
      padding: 12px 20px;
      z-index: 10000;
      font-size: 13px;
      color: var(--text);
      box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    `;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transition = 'opacity 0.3s';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }

  // 记录日志
  log(message, type) {
    console.log(`[AutoHandler] ${message}`);
    this.processingHistory.push({message, type, time: Date.now()});
  }

  // 获取状态
  getStatus() {
    return {
      autoMode: this.autoMode,
      pendingTasks: this.pendingTasks.length,
      processedCount: this.processingHistory.length,
      history: this.processingHistory.slice(-10)
    };
  }
}

// 全局实例
const autoHandlerVV6 = new AutoHandlerVV6();
window.AutoHandlerVV6 = AutoHandlerVV6;
window.autoHandlerVV6 = autoHandlerVV6;
