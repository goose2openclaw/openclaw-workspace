/**
 * Portfolio Store - 资产看板状态管理
 */
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const usePortfolioStore = defineStore('portfolio', () => {
  const data = ref(null);
  const positions = ref([]);
  const trades = ref([]);
  const loading = ref(false);
  const error = ref(null);
  const lastUpdated = ref(null);

  // 总资产
  const totalAsset = computed(() => data.value?.total_capital || 0);
  
  // 投资池
  const investmentPool = computed(() => data.value?.investment_pool || 0);
  
  // 打工池
  const workPool = computed(() => data.value?.work_pool || 0);
  
  // 打工现金流池
  const cashflowPool = computed(() => data.value?.cashflow_pool || 0);
  
  // 投资工具详情
  const investmentTools = computed(() => {
    const tools = data.value?.investment_tools || {};
    return Object.entries(tools).map(([id, tool]) => ({
      id,
      ...tool,
    }));
  });
  
  // 打工工具详情
  const workTools = computed(() => {
    const tools = data.value?.work_tools || {};
    return Object.entries(tools).map(([id, tool]) => ({
      id,
      ...tool,
    }));
  });

  // 工具分配汇总
  const toolAllocations = computed(() => {
    const allocations = [];
    investmentTools.value.forEach(t => {
      allocations.push({
        name: t.name,
        icon: getIcon(t.id),
        percent: t.weight,
        amount: t.allocation || 0,
        color: t.color || '#64748B',
      });
    });
    return allocations;
  });

  function getIcon(toolId) {
    const icons = {
      rabbit: '🐰',
      mole: '🐹',
      oracle: '🔮',
      leader: '👑',
      hitchhiker: '🍀',
      wool: '💰',
      poor: '👶',
    };
    return icons[toolId] || '📦';
  }

  async function fetchPortfolio() {
    loading.value = true;
    error.value = null;
    try {
      const result = await window.GO2SE.getPortfolio();
      data.value = result.data || result;
      lastUpdated.value = new Date();
      return result;
    } catch (e) {
      error.value = e;
      console.error('Portfolio fetch error:', e);
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function fetchPositions() {
    try {
      const result = await window.GO2SE.getPositions();
      positions.value = result.data || [];
      return result;
    } catch (e) {
      console.error('Positions fetch error:', e);
    }
  }

  async function fetchTrades(limit = 50) {
    try {
      const result = await window.GO2SE.getTrades(limit);
      trades.value = result.data || [];
      return result;
    } catch (e) {
      console.error('Trades fetch error:', e);
    }
  }

  async function fetchAll() {
    await Promise.all([
      fetchPortfolio(),
      fetchPositions(),
      fetchTrades(),
    ]);
  }

  function updateFromWebSocket(message) {
    if (message.type === 'portfolio' && message.data) {
      data.value = message.data;
      lastUpdated.value = new Date();
    }
    if (message.type === 'position' && message.data) {
      const item = message.data;
      const index = positions.value.findIndex(p => p.symbol === item.symbol);
      if (index >= 0) {
        positions.value[index] = item;
      } else {
        positions.value.push(item);
      }
    }
    if (message.type === 'trade' && message.data) {
      trades.value.unshift(message.data);
      if (trades.value.length > 100) {
        trades.value.pop();
      }
    }
  }

  return {
    data,
    positions,
    trades,
    loading,
    error,
    lastUpdated,
    totalAsset,
    investmentPool,
    workPool,
    cashflowPool,
    investmentTools,
    workTools,
    toolAllocations,
    fetchPortfolio,
    fetchPositions,
    fetchTrades,
    fetchAll,
    updateFromWebSocket,
  };
});
