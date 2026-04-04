/**
 * Market Store - 市场数据状态管理
 */
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useMarketStore = defineStore('market', () => {
  const data = ref([]);
  const loading = ref(false);
  const error = ref(null);
  const lastUpdated = ref(null);

  const topGainers = computed(() => {
    return [...data.value]
      .filter(item => item.change_24h > 0)
      .sort((a, b) => b.change_24h - a.change_24h)
      .slice(0, 5);
  });

  const topLosers = computed(() => {
    return [...data.value]
      .filter(item => item.change_24h < 0)
      .sort((a, b) => a.change_24h - b.change_24h)
      .slice(0, 5);
  });

  const bySymbol = computed(() => {
    const map = {};
    data.value.forEach(item => {
      map[item.symbol] = item;
    });
    return map;
  });

  async function fetchMarketData() {
    loading.value = true;
    error.value = null;
    try {
      const result = await window.GO2SE.getMarketData();
      data.value = result.data || [];
      lastUpdated.value = new Date();
    } catch (e) {
      error.value = e;
      console.error('Market fetch error:', e);
    } finally {
      loading.value = false;
    }
  }

  async function fetchSymbol(symbol) {
    try {
      const result = await window.GO2SE.getSymbolData(symbol);
      const item = result.data || result;
      const index = data.value.findIndex(d => d.symbol === symbol);
      if (index >= 0) {
        data.value[index] = item;
      } else {
        data.value.push(item);
      }
      return item;
    } catch (e) {
      console.error(`Symbol fetch error (${symbol}):`, e);
      throw e;
    }
  }

  function updateFromWebSocket(message) {
    if (message.type === 'market' && message.data) {
      const item = message.data;
      const index = data.value.findIndex(d => d.symbol === item.symbol);
      if (index >= 0) {
        data.value[index] = item;
      } else {
        data.value.push(item);
      }
      lastUpdated.value = new Date();
    }
  }

  return {
    data,
    loading,
    error,
    lastUpdated,
    topGainers,
    topLosers,
    bySymbol,
    fetchMarketData,
    fetchSymbol,
    updateFromWebSocket,
  };
});
