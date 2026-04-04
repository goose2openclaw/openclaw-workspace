/**
 * GO2SE WebSocket Service
 * 实时数据WebSocket - 自动重连/消息路由/心跳
 */

class WebSocketService {
  constructor() {
    this.ws = null;
    this.url = null;
    this.reconnectDelay = 3000;
    this.reconnectMax = 10;
    this.reconnectCount = 0;
    this.heartbeatInterval = null;
    this.heartbeatIntervalMs = 30000;
    this.listeners = new Map();
    this.subscriptions = new Set();
    this.autoReconnect = true;
    this._isConnecting = false;
  }

  connect(url) {
    if (this._isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
      return;
    }

    this.url = url || this._getDefaultUrl();
    this._isConnecting = true;

    try {
      this.ws = new WebSocket(this.url);
      this._setupEventHandlers();
    } catch (e) {
      console.error('WebSocket connection error:', e);
      this._isConnecting = false;
      this._scheduleReconnect();
    }
  }

  _getDefaultUrl() {
    const baseUrl = window.GO2SE?.baseUrl || 'http://localhost:8004';
    return baseUrl.replace('http', 'ws') + '/ws';
  }

  _setupEventHandlers() {
    this.ws.onopen = () => {
      console.log('🟢 WebSocket connected');
      this._isConnecting = false;
      this.reconnectCount = 0;
      this._startHeartbeat();
      this._resubscribe();
      this._emit('open', {});
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this._handleMessage(data);
      } catch (e) {
        console.error('WebSocket parse error:', e);
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      this._emit('error', error);
    };

    this.ws.onclose = (event) => {
      console.log('🔴 WebSocket disconnected:', event.code, event.reason);
      this._isConnecting = false;
      this._stopHeartbeat();
      this._emit('close', event);
      this._scheduleReconnect();
    };
  }

  _handleMessage(data) {
    // 广播给所有监听器
    this._emit('message', data);

    // 按类型路由
    const type = data.type || data.event;
    if (type) {
      this._emit(type, data);
    }

    // 特定类型处理
    switch (type) {
      case 'market':
        this._emit('market:update', data.data);
        break;
      case 'signal':
        this._emit('signal:update', data.data);
        break;
      case 'portfolio':
        this._emit('portfolio:update', data.data);
        break;
      case 'trade':
        this._emit('trade:new', data.data);
        break;
      case 'mirofish_prediction':
        this._emit('mirofish:prediction', data.data);
        break;
      case 'simulation_update':
        this._emit('simulation:update', data.data);
        break;
      case 'pong':
        // 心跳响应，忽略
        break;
      default:
        if (data.data) {
          this._emit('data', data.data);
        }
    }
  }

  _scheduleReconnect() {
    if (!this.autoReconnect) return;
    if (this.reconnectCount >= this.reconnectMax) {
      console.error('WebSocket max reconnection attempts reached');
      return;
    }

    this.reconnectCount++;
    const delay = this.reconnectDelay * Math.pow(1.5, this.reconnectCount - 1);
    console.log(`🔄 WebSocket reconnecting in ${delay}ms (attempt ${this.reconnectCount}/${this.reconnectMax})`);

    setTimeout(() => {
      this.connect(this.url);
    }, delay);
  }

  _startHeartbeat() {
    this._stopHeartbeat();
    this.heartbeatInterval = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: 'ping', timestamp: Date.now() }));
      }
    }, this.heartbeatIntervalMs);
  }

  _stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  _resubscribe() {
    this.subscriptions.forEach(channel => {
      this.send({ type: 'subscribe', channel });
    });
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
      return true;
    }
    console.warn('WebSocket not connected, message not sent');
    return false;
  }

  subscribe(channel) {
    this.subscriptions.add(channel);
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.send({ type: 'subscribe', channel });
    }
  }

  unsubscribe(channel) {
    this.subscriptions.delete(channel);
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.send({ type: 'unsubscribe', channel });
    }
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event).add(callback);
    return () => this.off(event, callback);
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).delete(callback);
    }
  }

  _emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data);
        } catch (e) {
          console.error(`WebSocket listener error (${event}):`, e);
        }
      });
    }
  }

  disconnect() {
    this.autoReconnect = false;
    this._stopHeartbeat();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  get isConnected() {
    return this.ws && this.ws.readyState === WebSocket.OPEN;
  }

  get isConnecting() {
    return this._isConnecting;
  }
}

// 导出单例
window.GO2SE_WS = new WebSocketService();
