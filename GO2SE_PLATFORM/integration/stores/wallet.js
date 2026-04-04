/**
 * Wallet Store - 钱包状态管理
 */
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useWalletStore = defineStore('wallet', () => {
  const balance = ref(null);
  const history = ref([]);
  const loading = ref(false);
  const error = ref(null);

  // 主钱包状态
  const mainWallet = computed(() => balance.value?.investment_tools?.main || {
    balance: 0,
    connected: false,
  });

  // 各工具钱包
  const toolWallets = computed(() => {
    const tools = balance.value?.investment_tools || {};
    return Object.entries(tools).map(([id, tool]) => ({
      id,
      name: tool.name || id,
      balance: tool.allocation || 0,
      weight: tool.weight || 0,
      status: tool.status || 'unknown',
      color: tool.color || '#64748B',
      icon: getIcon(id),
    }));
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
      main: '🏦',
    };
    return icons[toolId] || '📦';
  }

  async function fetchBalance() {
    loading.value = true;
    error.value = null;
    try {
      const result = await window.GO2SE.getWalletBalance();
      balance.value = result.data || result;
      return result;
    } catch (e) {
      error.value = e;
      console.error('Wallet balance fetch error:', e);
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function getPerformance() {
    try {
      const result = await window.GO2SE.getPerformance();
      balance.value = result;
      return result;
    } catch (e) {
      console.error('Performance fetch error:', e);
    }
  }

  async function executeTrade(signal) {
    loading.value = true;
    error.value = null;
    try {
      const result = await window.GO2SE.executeTrade(signal);
      await fetchBalance();
      return result;
    } catch (e) {
      error.value = e;
      throw e;
    } finally {
      loading.value = false;
    }
  }

  return {
    balance,
    history,
    loading,
    error,
    mainWallet,
    toolWallets,
    fetchBalance,
    getPerformance,
    executeTrade,
  };
});
