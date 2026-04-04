/**
 * GO2SE Data Flow
 * 实时数据流和状态管理
 */

class DataFlow {
  constructor() {
    this.cache = new Map();
    this.cacheTimeout = 5000; // 5秒缓存
    this.subscribers = new Map();
    this.isConnected = false;
  }

  // ========== 缓存管理 ==========
  setCache(key, data) {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
    });
  }

  getCache(key) {
    const cached = this.cache.get(key);
    if (!cached) return null;
    
    if (Date.now() - cached.timestamp > this.cacheTimeout) {
      this.cache.delete(key);
      return null;
    }
    
    return cached.data;
  }

  clearCache() {
    this.cache.clear();
  }

  // ========== 订阅发布 ==========
  subscribe(event, callback) {
    if (!this.subscribers.has(event)) {
      this.subscribers.set(event, new Set());
    }
    this.subscribers.get(event).add(callback);
    
    // 返回取消订阅函数
    return () => {
      this.subscribers.get(event)?.delete(callback);
    };
  }

  publish(event, data) {
    const callbacks = this.subscribers.get(event);
    if (callbacks) {
      callbacks.forEach(cb => {
        try {
          cb(data);
        } catch (e) {
          console.error(`Error in subscriber for ${event}:`, e);
        }
      });
    }
  }

  // ========== 实时数据处理 ==========
  handleMessage(data) {
    const { type, payload } = data;
    
    switch (type) {
      case 'price_update':
        this.setCache(`price_${payload.symbol}`, payload);
        this.publish('priceUpdate', payload);
        break;
        
      case 'signal_update':
        this.setCache(`signal_${payload.id}`, payload);
        this.publish('signalUpdate', payload);
        break;
        
      case 'asset_update':
        this.setCache('assets', payload);
        this.publish('assetUpdate', payload);
        break;
        
      case 'trade_executed':
        this.publish('tradeExecuted', payload);
        break;
        
      case 'alert':
        this.publish('alert', payload);
        this.handleAlert(payload);
        break;
        
      default:
        console.log('Unknown message type:', type);
    }
  }

  // ========== 告警处理 ==========
  handleAlert(alert) {
    const level = alert.level || 'info';
    
    switch (level) {
      case 'critical':
        this.showNotification(alert.title, alert.message, 'error');
        this.publish('criticalAlert', alert);
        break;
      case 'warning':
        this.showNotification(alert.title, alert.message, 'warning');
        this.publish('warningAlert', alert);
        break;
      default:
        this.showNotification(alert.title, alert.message, 'info');
    }
  }

  // ========== Toast通知 ==========
  showNotification(title, message, type = 'info') {
    const icons = {
      info: 'ℹ️',
      warning: '⚠️',
      error: '❌',
      success: '✅',
    };
    
    // 创建toast元素
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
      <span class="toast-icon">${icons[type]}</span>
      <div class="toast-content">
        <strong>${title}</strong>
        <p>${message}</p>
      </div>
      <button class="toast-close">×</button>
    `;
    
    // 添加到body
    document.body.appendChild(toast);
    
    // 动画显示
    requestAnimationFrame(() => {
      toast.classList.add('show');
    });
    
    // 自动关闭
    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => toast.remove(), 300);
    }, 5000);
    
    // 点击关闭
    toast.querySelector('.toast-close').onclick = () => {
      toast.classList.remove('show');
      setTimeout(() => toast.remove(), 300);
    };
  }

  // ========== 连接状态 ==========
  setConnected(connected) {
    this.isConnected = connected;
    this.publish('connectionChange', { connected });
  }
}

// 导出单例
window.DataFlow = new DataFlow();

// ========== 状态管理 ==========
class Store {
  constructor() {
    this.state = {
      // 用户状态
      user: null,
      membership: 'guest',
      
      // 资产状态
      assets: {
        total: 0,
        change24h: 0,
        byTool: {},
      },
      
      // 信号状态
      signals: [],
      activeSignalCount: 0,
      
      // 钱包状态
      wallets: [],
      
      // 系统状态
      systemStatus: 'unknown',
      lastUpdate: null,
    };
    
    this.listeners = new Map();
  }

  // 获取状态
  get(key) {
    if (key) {
      return this.state[key];
    }
    return { ...this.state };
  }

  // 更新状态
  set(key, value) {
    const oldValue = this.state[key];
    this.state[key] = value;
    
    // 通知监听器
    this.notify(key, value, oldValue);
  }

  // 合并状态
  merge(updates) {
    Object.entries(updates).forEach(([key, value]) => {
      this.set(key, value);
    });
  }

  // 监听状态变化
  subscribe(key, callback) {
    if (!this.listeners.has(key)) {
      this.listeners.set(key, new Set());
    }
    this.listeners.get(key).add(callback);
    
    return () => {
      this.listeners.get(key)?.delete(callback);
    };
  }

  // 通知监听器
  notify(key, newValue, oldValue) {
    const callbacks = this.listeners.get(key);
    if (callbacks) {
      callbacks.forEach(cb => {
        try {
          cb(newValue, oldValue);
        } catch (e) {
          console.error(`Error in state listener for ${key}:`, e);
        }
      });
    }
  }
}

// 导出单例
window.GO2SEStore = new Store();
