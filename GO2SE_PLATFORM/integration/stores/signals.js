/**
 * Signals Store - 信号列表状态管理
 */
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useSignalsStore = defineStore('signals', () => {
  const signals = ref([]);
  const total = ref(0);
  const loading = ref(false);
  const error = ref(null);
  const filter = ref({ strategy: null, signal: null });
  const pagination = ref({ limit: 50, offset: 0 });

  const byStrategy = computed(() => {
    const map = {};
    signals.value.forEach(s => {
      if (!map[s.strategy]) map[s.strategy] = [];
      map[s.strategy].push(s);
    });
    return map;
  });

  const activeSignals = computed(() => {
    return signals.value.filter(s => s.status === 'active' || s.active);
  });

  const recentSignals = computed(() => {
    return [...signals.value]
      .sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0))
      .slice(0, 20);
  });

  async function fetchSignals(params = {}) {
    loading.value = true;
    error.value = null;
    try {
      const result = await window.GO2SE.getSignals({
        ...filter.value,
        ...pagination.value,
        ...params,
      });
      signals.value = result.data || result;
      total.value = result.total || signals.value.length;
      return result;
    } catch (e) {
      error.value = e;
      console.error('Signals fetch error:', e);
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function runSignal(strategy) {
    loading.value = true;
    error.value = null;
    try {
      const result = await window.GO2SE.runSignal(strategy);
      await fetchSignals();
      return result;
    } catch (e) {
      error.value = e;
      throw e;
    } finally {
      loading.value = false;
    }
  }

  function setFilter(newFilter) {
    filter.value = { ...filter.value, ...newFilter };
  }

  function setPagination(newPagination) {
    pagination.value = { ...pagination.value, ...newPagination };
  }

  function updateFromWebSocket(message) {
    if (message.type === 'signal' && message.data) {
      const item = message.data;
      const index = signals.value.findIndex(s => s.id === item.id || s.signal === item.signal);
      if (index >= 0) {
        signals.value[index] = item;
      } else {
        signals.value.unshift(item);
      }
    }
  }

  return {
    signals,
    total,
    loading,
    error,
    filter,
    pagination,
    byStrategy,
    activeSignals,
    recentSignals,
    fetchSignals,
    runSignal,
    setFilter,
    setPagination,
    updateFromWebSocket,
  };
});
