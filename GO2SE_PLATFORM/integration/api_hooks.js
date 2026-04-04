/**
 * GO2SE API Hooks (Vue 3 Composition API)
 * API调用hooks - 错误处理/加载状态/数据缓存
 */

import { ref, computed, onMounted, onUnmounted } from 'vue';

// ========== useApi - 通用API调用hook ==========
export function useApi(apiCall, options = {}) {
  const { immediate = false, cacheKey = null } = options;
  
  const data = ref(null);
  const error = ref(null);
  const loading = ref(false);
  const called = ref(false);

  async function execute(...args) {
    loading.value = true;
    error.value = null;
    
    try {
      const result = await apiCall(...args);
      data.value = result;
      called.value = true;
      return result;
    } catch (e) {
      error.value = e;
      console.error('API Error:', e);
      throw e;
    } finally {
      loading.value = false;
    }
  }

  if (immediate && cacheKey && window.GO2SE?.cache) {
    const cached = window.GO2SE.cache.get(cacheKey);
    if (cached) {
      data.value = cached;
      called.value = true;
    }
  }

  return {
    data,
    error,
    loading,
    called,
    execute,
    isSuccess: computed(() => called.value && !error.value),
    isError: computed(() => !!error.value),
  };
}

// ========== useMarketData - 市场数据 ==========
export function useMarketData(options = {}) {
  const { immediate = true } = options;
  const api = useApi(() => window.GO2SE.getMarketData(), { immediate, cacheKey: '/api/market' });
  
  return {
    ...api,
    marketData: api.data,
  };
}

// ========== useSignals - 信号列表 ==========
export function useSignals(options = {}) {
  const { limit = 50, strategy = null, signal = null } = options;
  
  const signals = ref([]);
  const total = ref(0);
  const loading = ref(false);
  const error = ref(null);

  async function fetchSignals(params = {}) {
    loading.value = true;
    error.value = null;
    try {
      const result = await window.GO2SE.getSignals({ limit, strategy, signal, ...params });
      signals.value = result.data || result;
      total.value = result.total || signals.value.length;
      return result;
    } catch (e) {
      error.value = e;
      console.error('Failed to fetch signals:', e);
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function runSignal(strategyId) {
    loading.value = true;
    try {
      const result = await window.GO2SE.runSignal(strategyId);
      await fetchSignals();
      return result;
    } catch (e) {
      error.value = e;
      throw e;
    } finally {
      loading.value = false;
    }
  }

  if (immediate) {
    fetchSignals();
  }

  return {
    signals,
    total,
    loading,
    error,
    fetchSignals,
    runSignal,
  };
}

// ========== useStrategies - 策略配置 ==========
export function useStrategies(options = {}) {
  const { immediate = true } = options;
  const api = useApi(() => window.GO2SE.getStrategies(), { immediate });
  
  const strategies = computed(() => api.data.value?.data || []);
  const tools = ref([]);
  const loading = ref(false);
  const error = ref(null);

  async function fetchTools() {
    loading.value = true;
    try {
      const result = await window.GO2SE.getTools();
      tools.value = result.data || [];
      return result;
    } catch (e) {
      error.value = e;
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function updateTool(toolId, config) {
    loading.value = true;
    error.value = null;
    try {
      const result = await window.GO2SE.updateTool(toolId, config);
      await fetchTools();
      return result;
    } catch (e) {
      error.value = e;
      throw e;
    } finally {
      loading.value = false;
    }
  }

  if (immediate) {
    fetchTools();
  }

  return {
    ...api,
    strategies,
    tools,
    loading,
    error,
    fetchTools,
    updateTool,
    getActiveStrategy: () => window.GO2SE.getActiveStrategy(),
    validateStrategy: (params) => window.GO2SE.validateStrategy(params),
  };
}

// ========== usePortfolio - 资产看板 ==========
export function usePortfolio(options = {}) {
  const { immediate = true } = options;
  const api = useApi(() => window.GO2SE.getPortfolio(), { immediate });
  
  const portfolio = computed(() => api.data.value?.data || api.data.value || {});
  const positions = ref([]);
  const trades = ref([]);

  async function fetchPositions() {
    try {
      const result = await window.GO2SE.getPositions();
      positions.value = result.data || [];
    } catch (e) {
      console.error('Failed to fetch positions:', e);
    }
  }

  async function fetchTrades(limit = 50) {
    try {
      const result = await window.GO2SE.getTrades(limit);
      trades.value = result.data || [];
    } catch (e) {
      console.error('Failed to fetch trades:', e);
    }
  }

  if (immediate) {
    fetchPositions();
    fetchTrades();
  }

  return {
    ...api,
    portfolio,
    positions,
    trades,
    fetchPositions,
    fetchTrades,
  };
}

// ========== useWallet - 钱包状态 ==========
export function useWallet(options = {}) {
  const { immediate = true } = options;
  const api = useApi(() => window.GO2SE.getWalletBalance(), { immediate });

  const balance = computed(() => {
    const d = api.data.value;
    if (!d) return null;
    return {
      total: d.total_capital || 0,
      investment: d.investment_pool || 0,
      work: d.work_pool || 0,
      tools: d.investment_tools || {},
      workTools: d.work_tools || {},
    };
  });

  return {
    ...api,
    balance,
    getPerformance: () => window.GO2SE.getPerformance(),
  };
}

// ========== useMirofish - MiroFish集成 ==========
export function useMirofish(options = {}) {
  const { immediate = false } = options;
  
  const markets = ref([]);
  const predictions = ref([]);
  const simulationResults = ref(null);
  const dimensions = ref([]);
  const loading = ref(false);
  const error = ref(null);

  async function fetchMarkets() {
    loading.value = true;
    try {
      const result = await window.GO2SE.getMirofishMarkets();
      markets.value = result.data || [];
      return result;
    } catch (e) {
      error.value = e;
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function predict(question, scenario = 'default') {
    loading.value = true;
    error.value = null;
    try {
      const result = await window.GO2SE.mirofishPredict(question, scenario);
      predictions.value.unshift(result);
      return result;
    } catch (e) {
      error.value = e;
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function getDecision(params) {
    loading.value = true;
    error.value = null;
    try {
      const result = await window.GO2SE.getMirofishDecision(params);
      return result;
    } catch (e) {
      error.value = e;
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function runSimulation(simulationParams) {
    loading.value = true;
    error.value = null;
    try {
      const result = await window.GO2SE.runSimulation(simulationParams);
      simulationResults.value = result;
      return result;
    } catch (e) {
      error.value = e;
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function fetchDimensions() {
    try {
      const result = await window.GO2SE.getDimensions();
      dimensions.value = result.data || [];
      return result;
    } catch (e) {
      console.error('Failed to fetch dimensions:', e);
    }
  }

  async function fetchSimulationResults() {
    try {
      const result = await window.GO2SE.getSimulationResults();
      simulationResults.value = result;
      return result;
    } catch (e) {
      console.error('Failed to fetch simulation results:', e);
    }
  }

  return {
    markets,
    predictions,
    simulationResults,
    dimensions,
    loading,
    error,
    fetchMarkets,
    predict,
    getDecision,
    runSimulation,
    fetchDimensions,
    fetchSimulationResults,
  };
}

// ========== useWebSocket - WebSocket实时数据 ==========
export function useWebSocket(options = {}) {
  const {
    onMessage = null,
    onError = null,
    onClose = null,
    autoReconnect = true,
  } = options;

  const connected = ref(false);
  const lastMessage = ref(null);
  const reconnectCount = ref(0);

  function handleOpen() {
    connected.value = true;
    reconnectCount.value = 0;
  }

  function handleMessage(data) {
    lastMessage.value = data;
    onMessage && onMessage(data);
  }

  function handleError(error) {
    onError && onError(error);
  }

  function handleClose(event) {
    connected.value = false;
    onClose && onClose(event);
  }

  onMounted(() => {
    window.GO2SE?.createWebSocket({
      onOpen: handleOpen,
      onMessage: handleMessage,
      onError: handleError,
      onClose: handleClose,
      autoReconnect,
    });
  });

  onUnmounted(() => {
    window.GO2SE?.closeWS();
  });

  function send(data) {
    return window.GO2SE?.sendWS(data) || false;
  }

  return {
    connected,
    lastMessage,
    reconnectCount,
    send,
    reconnect: () => {
      window.GO2SE?.closeWS();
      window.GO2SE?.createWebSocket({
        onOpen: handleOpen,
        onMessage: handleMessage,
        onError: handleError,
        onClose: handleClose,
        autoReconnect,
      });
    },
  };
}

// ========== useHealth - 健康检查 ==========
export function useHealth(options = {}) {
  const { immediate = true, interval = 30000 } = options;
  
  const health = ref(null);
  const healthy = ref(false);
  const loading = ref(false);
  let timer = null;

  async function check() {
    loading.value = true;
    try {
      const result = await window.GO2SE.healthCheck();
      health.value = result.data;
      healthy.value = result.ok && result.data?.status === 'healthy';
      return result;
    } catch (e) {
      health.value = null;
      healthy.value = false;
      throw e;
    } finally {
      loading.value = false;
    }
  }

  if (immediate) {
    check();
    if (interval > 0) {
      timer = setInterval(check, interval);
    }
  }

  onUnmounted(() => {
    if (timer) clearInterval(timer);
  });

  return {
    health,
    healthy,
    loading,
    check,
  };
}
