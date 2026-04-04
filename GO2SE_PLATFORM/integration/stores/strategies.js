/**
 * Strategies Store - 策略配置状态管理
 */
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useStrategiesStore = defineStore('strategies', () => {
  const strategies = ref([]);
  const tools = ref([]);
  const activeStrategy = ref(null);
  const loading = ref(false);
  const error = ref(null);

  // 七工具映射
  const toolsMap = computed(() => {
    const map = {};
    tools.value.forEach(t => {
      map[t.id || t.tool_id] = t;
    });
    return map;
  });

  // 投资工具 (5个)
  const investmentTools = computed(() => {
    return tools.value.filter(t => 
      ['rabbit', 'mole', 'oracle', 'leader', 'hitchhiker'].includes(t.id)
    );
  });

  // 打工工具 (2个)
  const workTools = computed(() => {
    return tools.value.filter(t => 
      ['wool', 'poor'].includes(t.id)
    );
  });

  // 工具权重汇总
  const totalWeight = computed(() => {
    return tools.value.reduce((sum, t) => sum + (t.weight || 0), 0);
  });

  async function fetchStrategies() {
    loading.value = true;
    error.value = null;
    try {
      const result = await window.GO2SE.getStrategies();
      strategies.value = result.data || result;
      return result;
    } catch (e) {
      error.value = e;
      console.error('Strategies fetch error:', e);
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function fetchTools() {
    loading.value = true;
    error.value = null;
    try {
      const result = await window.GO2SE.getTools();
      tools.value = result.data || [];
      return result;
    } catch (e) {
      error.value = e;
      console.error('Tools fetch error:', e);
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function fetchActiveStrategy() {
    try {
      const result = await window.GO2SE.getActiveStrategy();
      activeStrategy.value = result.data || result;
      return result;
    } catch (e) {
      console.error('Active strategy fetch error:', e);
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

  async function validateStrategy(params) {
    try {
      return await window.GO2SE.validateStrategy(params);
    } catch (e) {
      error.value = e;
      throw e;
    }
  }

  async function fetchAll() {
    await Promise.all([
      fetchTools(),
      fetchActiveStrategy(),
    ]);
  }

  return {
    strategies,
    tools,
    activeStrategy,
    loading,
    error,
    toolsMap,
    investmentTools,
    workTools,
    totalWeight,
    fetchStrategies,
    fetchTools,
    fetchActiveStrategy,
    updateTool,
    validateStrategy,
    fetchAll,
  };
});
