/**
 * GO2SE API Client V11
 * 前后端数据流通封装 - 完整版
 * 支持: 错误处理/重试/缓存/实时数据/认证
 */

// ========== API错误类 ==========
class GO2SEApiError extends Error {
  constructor(message, status, code, data) {
    super(message);
    this.name = 'GO2SEApiError';
    this.status = status;
    this.code = code;
    this.data = data;
  }
}

// ========== 缓存策略 ==========
class CacheStrategy {
  constructor() {
    this.cache = new Map();
    this.ttlMap = new Map();
  }

  set(key, data, ttl = 10000) {
    this.cache.set(key, data);
    this.ttlMap.set(key, Date.now() + ttl);
  }

  get(key) {
    const ttl = this.ttlMap.get(key);
    if (!ttl) return null;
    if (Date.now() > ttl) {
      this.cache.delete(key);
      this.ttlMap.delete(key);
      return null;
    }
    return this.cache.get(key);
  }

  invalidate(key) {
    this.cache.delete(key);
    this.ttlMap.delete(key);
  }

  clear() {
    this.cache.clear();
    this.ttlMap.clear();
  }
}

// ========== 主API客户端 ==========
class GO2SEClient {
  constructor(baseUrl = 'http://localhost:8004') {
    this.baseUrl = baseUrl;
    this.wsUrl = baseUrl.replace('http', 'ws') + '/ws';
    this.token = localStorage.getItem('go2se_token');
    this.retryCount = 3;
    this.retryDelay = 1000;
    this.cache = new CacheStrategy();
    this.ws = null;
    this.wsReconnectDelay = 3000;
    this.wsReconnectMax = 5;
    this._wsReconnectCount = 0;
  }

  // ========== 通用请求封装 ==========
  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
        ...(this.token && { 'Authorization': `Bearer ${this.token}` }),
      },
    };
    
    const config = { ...defaultOptions, ...options };

    for (let i = 0; i < this.retryCount; i++) {
      try {
        const response = await fetch(url, config);
        
        if (response.status === 429) {
          const retryAfter = response.headers.get('Retry-After') || this.retryDelay;
          throw new GO2SEApiError('Rate limit exceeded', 429, 'RATE_LIMIT', { retryAfter });
        }
        
        if (response.status === 401) {
          this.clearToken();
          throw new GO2SEApiError('Unauthorized', 401, 'UNAUTHORIZED', null);
        }
        
        if (response.status === 404) {
          throw new GO2SEApiError('Not found', 404, 'NOT_FOUND', null);
        }
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new GO2SEApiError(
            errorData.error || response.statusText,
            response.status,
            errorData.code || 'UNKNOWN',
            errorData
          );
        }
        
        return await response.json();
      } catch (error) {
        if (error instanceof GO2SEApiError) throw error;
        if (i === this.retryCount - 1) {
          throw new GO2SEApiError(error.message, 0, 'NETWORK_ERROR', null);
        }
        await this._delay(this.retryDelay * Math.pow(2, i));
      }
    }
  }

  _delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // ========== HTTP方法 ==========
  async get(endpoint, useCache = false, cacheTtl = 10000) {
    if (useCache) {
      const cached = this.cache.get(endpoint);
      if (cached) return cached;
    }
    const data = await this.request(endpoint, { method: 'GET' });
    if (useCache) this.cache.set(endpoint, data, cacheTtl);
    return data;
  }

  async post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }

  // ========== 健康检查 & 统计 ==========
  async ping() {
    return this.get('/api/ping', true, 5000);
  }

  async healthCheck() {
    try {
      const data = await this.get('/api/health', true, 8000);
      return { ok: true, data };
    } catch (error) {
      return { ok: false, error: error.message };
    }
  }

  async getStats() {
    return this.get('/api/stats', true, 8000);
  }

  async getPerformance() {
    return this.get('/api/performance', true, 10000);
  }

  // ========== 市场数据 ==========
  async getMarketData() {
    return this.get('/api/market', true, 15000);
  }

  async getSymbolData(symbol) {
    return this.get(`/api/market/${symbol}`, true, 10000);
  }

  // ========== 资产看板 ==========
  async getPortfolio() {
    return this.get('/api/portfolio', true, 10000);
  }

  async getPositions() {
    return this.get('/api/positions', true, 8000);
  }

  async getTrades(limit = 50) {
    return this.get(`/api/trades?limit=${limit}`, false);
  }

  // ========== 策略配置 ==========
  async getStrategies() {
    return this.get('/api/strategies', true, 10000);
  }

  async getTools() {
    return this.get('/api/tools', true, 10000);
  }

  async getTool(toolId) {
    return this.get(`/api/tools/${toolId}`, true, 10000);
  }

  async updateTool(toolId, config) {
    const data = await this.put(`/api/tools/${toolId}`, config);
    this.cache.invalidate('/api/tools');
    this.cache.invalidate(`/api/tools/${toolId}`);
    return data;
  }

  async getActiveStrategy() {
    return this.get('/api/strategy/active', true, 10000);
  }

  async validateStrategy(params) {
    return this.post('/api/strategy/validate', params);
  }

  // ========== 信号列表 ==========
  async getSignals(params = {}) {
    const { limit = 50, offset = 0, strategy, signal } = params;
    let endpoint = `/api/signals?limit=${limit}&offset=${offset}`;
    if (strategy) endpoint += `&strategy=${strategy}`;
    if (signal) endpoint += `&signal=${signal}`;
    return this.get(endpoint, false);
  }

  async runSignal(strategy) {
    return this.post(`/api/signals/${strategy}/run`, {});
  }

  // ========== 钱包状态 ==========
  async getWalletBalance() {
    return this.get('/api/portfolio', true, 10000);
  }

  async executeTrade(signal) {
    return this.post('/api/trade', signal);
  }

  // ========== MiroFish 集成 ==========
  async getMirofishMarkets() {
    return this.get('/api/mirofish/markets', true, 30000);
  }

  async mirofishPredict(question, scenario = 'default') {
    return this.post('/api/mirofish/predict', { question, scenario });
  }

  async getMirofishDecision(params) {
    return this.post('/api/mirofish/decision', params);
  }

  async runSimulation(simulationParams) {
    return this.post('/api/simulation/run', simulationParams);
  }

  async getSimulationResults() {
    return this.get('/api/simulation', true, 10000);
  }

  async getDimensions() {
    return this.get('/api/dimensions', true, 60000);
  }

  // ========== 回测 & 模拟交易 ==========
  async runBacktest(params) {
    return this.post('/api/backtest', params);
  }

  async getBacktestHistory() {
    return this.get('/api/backtest/history', false);
  }

  async getPaperTrades() {
    return this.get('/api/paper-trades', true, 5000);
  }

  // ========== 声纳库 ==========
  async getSonarSignals() {
    return this.get('/api/sonar/signals', true, 15000);
  }

  async getSonarAnalysis(symbol) {
    return this.get(`/api/sonar/${symbol}`, true, 10000);
  }

  // ========== 专家模式 ==========
  async getExpertMode() {
    return this.get('/api/expert/mode', true, 10000);
  }

  async updateExpertMode(config) {
    return this.put('/api/expert/mode', config);
  }

  // ========== 认证 ==========
  async login(username, password) {
    const data = await this.post('/api/auth/login', { username, password });
    if (data.token) {
      this.setToken(data.token);
    }
    return data;
  }

  async register(username, password) {
    return this.post('/api/auth/register', { username, password });
  }

  async getMe() {
    return this.get('/api/auth/me', false);
  }

  setToken(token) {
    this.token = token;
    localStorage.setItem('go2se_token', token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('go2se_token');
  }

  // ========== WebSocket 实时数据 ==========
  createWebSocket(options = {}) {
    const {
      onOpen,
      onMessage,
      onError,
      onClose,
      autoReconnect = true,
    } = options;

    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.close();
    }

    this.ws = new WebSocket(this.wsUrl);
    this._wsOnOpen = onOpen;
    this._wsOnMessage = onMessage;
    this._wsOnError = onError;
    this._wsOnClose = onClose;
    this._wsAutoReconnect = autoReconnect;

    this.ws.onopen = () => {
      console.log('🟢 WebSocket connected');
      this._wsReconnectCount = 0;
      this._wsOnOpen && this._wsOnOpen();
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this._wsOnMessage && this._wsOnMessage(data);
      } catch (e) {
        console.error('WebSocket parse error:', e);
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      this._wsOnError && this._wsOnError(error);
    };

    this.ws.onclose = (event) => {
      console.log('🔴 WebSocket disconnected', event.code, event.reason);
      this._wsOnClose && this._wsOnClose(event);
      
      if (this._wsAutoReconnect && this._wsReconnectCount < this.wsReconnectMax) {
        this._wsReconnectCount++;
        console.log(`🔄 WebSocket 重连中 (${this._wsReconnectCount}/${this.wsReconnectMax})...`);
        setTimeout(() => this.createWebSocket(options), this.wsReconnectDelay);
      }
    };

    return this.ws;
  }

  sendWS(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
      return true;
    }
    return false;
  }

  closeWS() {
    this._wsAutoReconnect = false;
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  // ========== 缓存管理 ==========
  clearCache() {
    this.cache.clear();
  }

  invalidateCache(pattern) {
    if (!pattern) {
      this.clearCache();
      return;
    }
    for (const key of this.cache.cache.keys()) {
      if (key.includes(pattern)) {
        this.cache.invalidate(key);
      }
    }
  }
}

// 导出单例
window.GO2SE = new GO2SEClient();
window.GO2SEApiError = GO2SEApiError;
